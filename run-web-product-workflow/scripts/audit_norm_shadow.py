#!/usr/bin/env python3
"""Evaluate T-017 Shadow retrieval quality without authorizing release."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from audit_norm_integration import compare_trees, junction_status
from audit_norm_retrieval import query_gateway_evaluation, validate_contracts
from governance_artifacts import (
    GovernanceError,
    _write_derived_view,
    atomic_write_json,
    governance_root,
    now_utc,
    read_json,
    runtime_asset_path,
    sha256_file,
    validate_query_history,
    validate_task_directory,
)
from query_norm_context import validate_query_output_directory


EVALUATION_ALGORITHM_VERSION = "shadow-context-reduction-v2"
PUBLICATION_FILES = (
    "shadow-evaluation.json",
    "shadow-evaluation.json.view.json",
    "shadow-evaluation.md",
    "shadow-evaluation.md.view.json",
    "publication-manifest.json",
)


REPRESENTATIVE_CASES = (
    {
        "sample_id": "T017-SHADOW-001",
        "task_id": "T-016",
        "action": "run_started",
        "category": "execution-authority-gate",
        "legacy_case_id": "NRG-G-009",
    },
    {
        "sample_id": "T017-SHADOW-002",
        "task_id": "T-016",
        "action": "plan_execution",
        "category": "gate-transition-and-closure",
        "legacy_case_id": "NRG-G-005",
    },
    {
        "sample_id": "T017-SHADOW-003",
        "task_id": "T-017",
        "action": "run_started",
        "category": "shadow-start-and-release-boundary",
        "legacy_case_id": "NRG-G-009",
    },
    {
        "sample_id": "T017-SHADOW-004",
        "task_id": "T-017",
        "action": "plan_execution",
        "category": "high-risk-implementation-plan",
        "legacy_case_id": "NRG-G-005",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--approval-ref", required=True)
    parser.add_argument("--median-reduction-threshold", type=float, required=True)
    parser.add_argument("--minimum-case-reduction-threshold", type=float, required=True)
    parser.add_argument("--mandatory-coverage-threshold", type=float, required=True)
    parser.add_argument("--false-allow-threshold", type=int, required=True)
    parser.add_argument(
        "--publication-state",
        choices=("pre-review", "post-review"),
        default="pre-review",
    )
    return parser.parse_args()


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        detail = (result.stdout + result.stderr)[-4000:]
        raise GovernanceError(f"{label} failed: {detail}")


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def citation_integrity(result: dict[str, Any]) -> tuple[bool, int]:
    checked = 0
    for citation in result.get("citations", []):
        source_path = runtime_asset_path(citation["logical_path"])
        if sha256_file(source_path) != citation["source_sha256"]:
            return False, checked
        expected_chunk = hashlib.sha256(citation["text"].encode("utf-8")).hexdigest()
        if expected_chunk != citation["chunk_sha256"]:
            return False, checked
        lines = source_path.read_text(encoding="utf-8").splitlines()
        start, end = citation["line_start"], citation["line_end"]
        if start < 1 or end < start or end > len(lines):
            return False, checked
        if "\n".join(lines[start - 1 : end]) != citation["text"]:
            return False, checked
        checked += 1
    return checked > 0, checked


def legacy_case_by_id(baseline: dict[str, Any], case_id: str) -> dict[str, Any]:
    matches = [
        item for item in baseline["benchmark"]["legacy_rg"]["cases"]
        if item.get("case_id") == case_id
    ]
    if len(matches) != 1:
        raise GovernanceError(f"legacy baseline case must resolve exactly once: {case_id}")
    return matches[0]


def load_shadow_contract(
    project_root: Path,
    before: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    authority_path = project_root / ".project-governance" / "authority" / "CHG-0015.json"
    authority = read_json(authority_path)
    if (
        authority.get("asset_id") != "CHG-0015"
        or authority.get("legacy_kind") != "CHG"
        or authority.get("state") not in {"In Progress", "In Review"}
    ):
        raise GovernanceError("CHG-0015 is not a valid active Shadow AuthorityAsset")
    contract = authority.get("profile_fields", {}).get("shadow_evaluation_contract")
    if not isinstance(contract, dict):
        raise GovernanceError("CHG-0015 shadow_evaluation_contract is missing")
    contract_body = {key: value for key, value in contract.items() if key != "contract_sha256"}
    if contract.get("contract_sha256") != canonical_sha256(contract_body):
        raise GovernanceError("Shadow evaluation contract digest differs")
    if contract.get("contract_version") != "1.0":
        raise GovernanceError("unsupported Shadow evaluation contract version")
    if contract.get("algorithm_version") != EVALUATION_ALGORITHM_VERSION:
        raise GovernanceError("Shadow evaluation algorithm version differs")
    if contract.get("threshold_approval_ref") != args.approval_ref:
        raise GovernanceError("Shadow threshold Authority reference differs")
    if args.approval_ref not in before["authority"]["authority_references"]:
        raise GovernanceError("threshold approval reference is not bound to TaskContract")

    thresholds = contract.get("thresholds")
    if not isinstance(thresholds, dict):
        raise GovernanceError("Shadow evaluation thresholds are missing")
    expected_thresholds = {
        "median_reduction_percent": args.median_reduction_threshold,
        "minimum_case_reduction_percent": args.minimum_case_reduction_threshold,
        "mandatory_coverage_percent": args.mandatory_coverage_threshold,
        "false_allow_count": args.false_allow_threshold,
    }
    for key, cli_value in expected_thresholds.items():
        authority_value = thresholds.get(key)
        if isinstance(authority_value, bool) or not isinstance(authority_value, (int, float)):
            raise GovernanceError(f"Shadow Authority threshold is invalid: {key}")
        if not math.isfinite(float(authority_value)):
            raise GovernanceError(f"Shadow Authority threshold is not finite: {key}")
        if float(authority_value) != float(cli_value):
            raise GovernanceError(f"CLI threshold differs from Shadow Authority: {key}")
    if not (
        0.0 <= float(thresholds["median_reduction_percent"]) <= 100.0
        and 0.0 <= float(thresholds["minimum_case_reduction_percent"]) <= 100.0
        and float(thresholds["mandatory_coverage_percent"]) == 100.0
        and int(thresholds["false_allow_count"]) == 0
    ):
        raise GovernanceError("Shadow Authority thresholds violate the fail-closed range")

    baseline = contract.get("legacy_baseline")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("path"), str):
        raise GovernanceError("Shadow legacy baseline binding is missing")
    baseline_path = (project_root / baseline["path"]).resolve()
    try:
        baseline_path.relative_to(project_root)
    except ValueError as exc:
        raise GovernanceError("Shadow legacy baseline escapes the project root") from exc
    if not baseline_path.is_file() or sha256_file(baseline_path) != baseline.get("sha256"):
        raise GovernanceError("Shadow legacy baseline binding differs")

    bindings = contract.get("representative_samples")
    if not isinstance(bindings, list) or len(bindings) != len(REPRESENTATIVE_CASES):
        raise GovernanceError("Shadow representative sample binding count differs")
    by_id: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, dict) or not isinstance(binding.get("sample_id"), str):
            raise GovernanceError("Shadow representative sample binding is invalid")
        if binding["sample_id"] in by_id:
            raise GovernanceError("Shadow representative sample binding is duplicated")
        by_id[binding["sample_id"]] = binding
    expected_ids = {str(item["sample_id"]) for item in REPRESENTATIVE_CASES}
    if set(by_id) != expected_ids:
        raise GovernanceError("Shadow representative sample identities differ")
    for specification in REPRESENTATIVE_CASES:
        binding = by_id[str(specification["sample_id"])]
        for key in ("task_id", "action", "category", "legacy_case_id"):
            if binding.get(key) != specification[key]:
                raise GovernanceError(
                    f"Shadow representative sample contract differs: {specification['sample_id']}/{key}"
                )
    return {
        "authority_path": authority_path,
        "authority_sha256": sha256_file(authority_path),
        "contract": contract,
        "contract_sha256": contract["contract_sha256"],
        "baseline_path": baseline_path,
        "bindings": by_id,
        "thresholds": thresholds,
    }


def representative_evaluation(
    project_root: Path,
    baseline: dict[str, Any],
    *,
    shadow_contract: dict[str, Any],
    median_threshold: float,
    minimum_threshold: float,
) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for specification in REPRESENTATIVE_CASES:
        binding = shadow_contract["bindings"][str(specification["sample_id"])]
        result_ref = binding.get("result_ref")
        request_ref = binding.get("request_ref")
        if not isinstance(result_ref, str) or not isinstance(request_ref, str):
            raise GovernanceError("representative query binding path is missing")
        result_path = (project_root / result_ref).resolve()
        request_path = (project_root / request_ref).resolve()
        if not result_path.is_file():
            raise GovernanceError(f"representative query result is missing: {result_path}")
        task_dir = (
            project_root / ".project-governance" / "tasks" / str(specification["task_id"])
        )
        validate_query_output_directory(task_dir, result_path)
        expected_files = binding.get("files")
        if not isinstance(expected_files, dict) or set(expected_files) != {
            "query-result.json",
            "query-result.json.view.json",
            "clause-context.md",
            "clause-context.md.view.json",
        }:
            raise GovernanceError("representative query package binding is incomplete")
        actual_names = {path.name for path in result_path.parent.iterdir() if path.is_file()}
        if actual_names != set(expected_files):
            raise GovernanceError("representative query package file set differs")
        for name, expected_sha256 in expected_files.items():
            if sha256_file(result_path.parent / name) != expected_sha256:
                raise GovernanceError(
                    f"representative query package hash differs: {result_path.parent / name}"
                )
        if not request_path.is_file() or sha256_file(request_path) != binding.get("request_sha256"):
            raise GovernanceError("representative query request binding differs")
        request = read_json(request_path)
        if (
            request.get("task_id") != specification["task_id"]
            or request.get("action") != specification["action"]
        ):
            raise GovernanceError("representative query request identity differs")
        result = read_json(result_path)
        if (
            result.get("query_digest") != binding.get("query_digest")
            or result_path.parent.name != result.get("query_digest")
        ):
            raise GovernanceError("representative query digest binding differs")
        envelope = read_json(result_path.with_suffix(result_path.suffix + ".view.json"))
        sources = envelope.get("sources")
        if (
            not isinstance(sources, list)
            or not sources
            or sources[0] != request_path.relative_to(project_root).as_posix()
        ):
            raise GovernanceError("representative query envelope request binding differs")
        context_path = result_path.with_name("clause-context.md")
        if len(context_path.read_text(encoding="utf-8")) != result["budget"]["used_chars"]:
            raise GovernanceError("representative query used_chars differs from Clause Context")
        required = set(result["coverage"]["required"])
        present = set(result["coverage"]["present"])
        missing = set(result["coverage"]["missing"])
        coverage_complete = bool(required) and present == required and not missing
        citations_valid, citation_count = citation_integrity(result)
        legacy = legacy_case_by_id(baseline, str(specification["legacy_case_id"]))
        if canonical_sha256(legacy) != binding.get("legacy_case_sha256"):
            raise GovernanceError("representative legacy case binding differs")
        old_chars = int(legacy["matched_chars"])
        new_chars = int(result["budget"]["used_chars"])
        reduction = round((old_chars - new_chars) * 100.0 / old_chars, 4)
        sample_passed = (
            result["status"] in {"Complete", "Expanded"}
            and coverage_complete
            and citations_valid
            and reduction >= minimum_threshold
        )
        samples.append(
            {
                **specification,
                "result_ref": result_path.relative_to(project_root).as_posix(),
                "result_sha256": sha256_file(result_path),
                "binding_sha256": canonical_sha256(binding),
                "query_digest": result["query_digest"],
                "query_status": result["status"],
                "legacy_matched_chars": old_chars,
                "new_context_chars": new_chars,
                "unrelated_context_reduction_proxy_percent": reduction,
                "required_control_count": len(required),
                "missing_control_count": len(missing),
                "citation_count": citation_count,
                "citation_integrity": citations_valid,
                "passed": sample_passed,
            }
        )
    reductions = [item["unrelated_context_reduction_proxy_percent"] for item in samples]
    median_reduction = round(float(statistics.median(reductions)), 4)
    minimum_reduction = round(min(reductions), 4)
    return {
        "method": (
            "When mandatory-clause coverage remains 100% and false-allow count remains zero, "
            "the reduction in delivered context characters is used as a conservative proxy for "
            "unrelated-context reduction. It is not a relevance-label substitute."
        ),
        "sample_policy": "four fixed real-query samples declared by CHG-0015; no auto-selection",
        "sample_count": len(samples),
        "samples": samples,
        "median_reduction_percent": median_reduction,
        "minimum_case_reduction_percent": minimum_reduction,
        "thresholds": {
            "median_reduction_percent": median_threshold,
            "minimum_case_reduction_percent": minimum_threshold,
        },
        "passed": (
            len(samples) == len(REPRESENTATIVE_CASES)
            and all(item["passed"] for item in samples)
            and median_reduction >= median_threshold
            and minimum_reduction >= minimum_threshold
        ),
    }


def query_history_integrity(project_root: Path, task_id: str) -> dict[str, Any]:
    return validate_query_history(project_root, task_id)


def bootstrap_adversarial(
    project_root: Path,
    task_id: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    skill_relative = Path("04_模板与检查清单") / "run-web-product-workflow"
    with tempfile.TemporaryDirectory(prefix="t017-bootstrap-") as temp:
        isolated = Path(temp) / project_root.name
        isolated.mkdir()
        shutil.copytree(project_root / ".project-governance", isolated / ".project-governance")
        shutil.copytree(project_root / skill_relative, isolated / skill_relative)
        isolated_skill = isolated / skill_relative
        task_dir = isolated / ".project-governance" / "tasks" / task_id
        before_path = task_dir / "before.json"
        before = read_json(before_path)
        isolated_args = argparse.Namespace(**vars(args))
        isolated_args.project_root = isolated
        isolated_args.task_dir = task_dir
        isolated_contract = load_shadow_contract(isolated, before, isolated_args)
        downgrade_args = argparse.Namespace(**vars(isolated_args))
        downgrade_args.median_reduction_threshold = -200.0
        downgrade_args.minimum_case_reduction_threshold = -200.0
        try:
            load_shadow_contract(isolated, before, downgrade_args)
            threshold_downgrade_blocked = False
        except GovernanceError:
            threshold_downgrade_blocked = True
        isolated_baseline = read_json(isolated_contract["baseline_path"])
        first_binding = isolated_contract["bindings"]["T017-SHADOW-001"]
        tampered_result_path = isolated / first_binding["result_ref"]
        original_result = tampered_result_path.read_bytes()
        tampered_result = read_json(tampered_result_path)
        tampered_result["budget"]["used_chars"] *= 2
        tampered_result_path.write_text(
            json.dumps(tampered_result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            representative_evaluation(
                isolated,
                isolated_baseline,
                shadow_contract=isolated_contract,
                median_threshold=args.median_reduction_threshold,
                minimum_threshold=args.minimum_case_reduction_threshold,
            )
            sample_tamper_blocked = False
        except GovernanceError:
            sample_tamper_blocked = True
        finally:
            tampered_result_path.write_bytes(original_result)
        before["lifecycle_state"] = "Ready"
        before["frozen_at"] = None
        before_path.write_text(
            json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (task_dir / "run.jsonl").write_text("", encoding="utf-8")
        after_path = task_dir / "after.json"
        if after_path.exists():
            after_path.unlink()
        for relative in (
            Path(".project-governance/generated/queries") / task_id,
            Path(".project-governance/generated/query-history") / task_id,
        ):
            target = isolated / relative
            if target.exists():
                shutil.rmtree(target)

        scripts = isolated_skill / "scripts"
        refresh = scripts / "refresh_tailoring_resolution.py"
        compile_script = scripts / "compile_norm_context.py"
        query_script = scripts / "query_norm_context.py"
        append_script = scripts / "append_run_event.py"
        validate_script = scripts / "validate_task_package.py"

        def refresh_stage(stage: str) -> None:
            require_success(
                run_command(
                    [
                        sys.executable, "-B", "-X", "utf8", str(refresh), str(before_path),
                        "--stage", stage, "--reason", "T-017 isolated bootstrap fixture",
                        "--basis", "CHG-0015 bootstrap adversarial",
                    ],
                    cwd=isolated,
                ),
                f"refresh {stage}",
            )

        def compile_stage(stage: str) -> Path:
            require_success(
                run_command(
                    [
                        sys.executable, "-B", "-X", "utf8", str(compile_script),
                        "--task-dir", str(task_dir), "--stage", stage, "--enforce",
                    ],
                    cwd=isolated,
                ),
                f"compile {stage}",
            )
            return isolated / ".project-governance" / "generated" / "contexts" / task_id / stage

        refresh_stage("S2")
        s2_context = compile_stage("S2")
        s2_packet = read_json(s2_context / "norm-packet.json")
        card_sources = set(
            re.findall(
                r"^###\s+((?:C|E)\d{2})\s+—",
                (s2_context / "norm-packet.md").read_text(encoding="utf-8"),
                flags=re.MULTILINE,
            )
        )
        s2_plan = read_json(s2_context / "retrieval-plan.json")
        s2_request = dict(s2_plan["request_template"])
        s2_request["action"] = "clarify_requirement"
        s2_request["query_text"] = "确认范围、验收与阻断问题"
        request_root = (
            isolated / ".project-governance" / "generated" / "queries" / task_id / "requests"
        )
        request_root.mkdir(parents=True)
        s2_request_path = request_root / "s2.json"
        s2_request_path.write_text(
            json.dumps(s2_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        s2_query = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(query_script),
                "--task-dir", str(task_dir), "--request-json-file", str(s2_request_path),
            ],
            cwd=isolated,
        )
        require_success(s2_query, "S2 stage-context query")
        stage_card_passed = (
            card_sources == set(s2_packet["stage_context_standards"])
            and card_sources != set(s2_packet["applicable_standards"])
        )

        markdown_path = s2_context / "norm-packet.md"
        original_markdown = markdown_path.read_text(encoding="utf-8")
        markdown_path.write_text(
            re.sub(r"^###\s+((?:C|E)\d{2})\s+—", "### C99 —", original_markdown, count=1, flags=re.MULTILINE),
            encoding="utf-8",
        )
        tampered_cards = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(query_script),
                "--task-dir", str(task_dir), "--request-json-file", str(s2_request_path),
                "--validate-only",
            ],
            cwd=isolated,
        )
        markdown_path.write_text(original_markdown, encoding="utf-8")
        card_tamper_blocked = tampered_cards.returncode != 0

        shutil.rmtree(isolated / ".project-governance" / "generated" / "queries" / task_id)
        refresh_stage("S4")
        s4_context = compile_stage("S4")
        s4_plan = read_json(s4_context / "retrieval-plan.json")
        s4_request = dict(s4_plan["request_template"])
        s4_request["action"] = "run_started"
        s4_request["query_text"] = "开始执行前需要哪些权限、Gate和失败关闭条件"
        request_root.mkdir(parents=True)
        s4_request_path = request_root / "run-started.json"
        s4_request_path.write_text(
            json.dumps(s4_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        prefreeze_query = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(query_script),
                "--task-dir", str(task_dir), "--request-json-file", str(s4_request_path),
            ],
            cwd=isolated,
        )
        require_success(prefreeze_query, "pre-freeze run_started query")
        prefreeze_before = read_json(before_path)
        prefreeze_passed = (
            prefreeze_before["lifecycle_state"] == "Ready"
            and prefreeze_before["frozen_at"] is None
        )
        require_success(
            run_command(
                [
                    sys.executable, "-B", "-X", "utf8", str(append_script), str(task_dir),
                    "--run-id", "RUN-T017-BOOTSTRAP", "--attempt-id", "A-001",
                    "--event-type", "run_started", "--summary", "isolated bootstrap",
                    "--status", "started",
                ],
                cwd=isolated,
            ),
            "freeze isolated TaskContract",
        )
        postfreeze_context = compile_stage("S4")
        postfreeze_validation = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(validate_script), str(task_dir),
                "--execution-ready",
            ],
            cwd=isolated,
        )
        postfreeze_passed = postfreeze_validation.returncode == 0

        result_path = next(
            path for path in (
                isolated / ".project-governance" / "generated" / "queries" / task_id
            ).glob("*/query-result.json")
        )
        view_path = result_path.with_suffix(result_path.suffix + ".view.json")
        original_view = view_path.read_bytes()
        view = read_json(view_path)
        view["generated_at"] = "2999-01-01T00:00:00Z"
        view_path.write_text(json.dumps(view, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        future_timestamp = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(validate_script), str(task_dir),
                "--execution-ready",
            ],
            cwd=isolated,
        )
        view_path.write_bytes(original_view)
        future_timestamp_blocked = future_timestamp.returncode != 0

        postfreeze_plan = read_json(postfreeze_context / "retrieval-plan.json")
        plan_request = dict(postfreeze_plan["request_template"])
        plan_request["action"] = "plan_execution"
        plan_request["query_text"] = "冻结后计划查询必须使用 frozen_at 时间下界"
        plan_request_path = request_root / "postfreeze-plan.json"
        plan_request_path.write_text(
            json.dumps(plan_request, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        plan_query = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(query_script),
                "--task-dir", str(task_dir), "--request-json-file", str(plan_request_path),
            ],
            cwd=isolated,
        )
        require_success(plan_query, "post-freeze plan query")
        plan_digest = json.loads(plan_query.stdout)["query_digest"]
        plan_result = (
            isolated / ".project-governance" / "generated" / "queries" /
            task_id / plan_digest / "query-result.json"
        )

        def rewrite_envelope_time(envelope_path: Path, generated_at: str) -> bytes:
            original = envelope_path.read_bytes()
            envelope = read_json(envelope_path)
            source_paths = []
            for source_ref in envelope["sources"]:
                source_path = Path(source_ref)
                if not source_path.is_absolute():
                    source_path = isolated / source_path
                source_paths.append(source_path.resolve())
            digest = hashlib.sha256()
            digest.update(b"LFEN-QUERY-DERIVED-VIEW-SNAPSHOT-V1\x00")
            digest.update(generated_at.encode("utf-8"))
            digest.update(b"\x00")
            for source_path in source_paths:
                digest.update(source_path.read_bytes())
            envelope["generated_at"] = generated_at
            envelope["source_snapshot"] = digest.hexdigest()
            envelope_path.write_text(
                json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            return original

        backdated_at = read_json(before_path)["created_at"]
        plan_result_view = plan_result.with_suffix(plan_result.suffix + ".view.json")
        plan_context_view = plan_result.with_name("clause-context.md.view.json")
        original_plan_result_view = rewrite_envelope_time(plan_result_view, backdated_at)
        original_plan_context_view = rewrite_envelope_time(plan_context_view, backdated_at)
        backdated_plan = run_command(
            [
                sys.executable, "-B", "-X", "utf8", str(validate_script), str(task_dir),
                "--execution-ready",
            ],
            cwd=isolated,
        )
        plan_result_view.write_bytes(original_plan_result_view)
        plan_context_view.write_bytes(original_plan_context_view)
        backdated_postfreeze_blocked = backdated_plan.returncode != 0

        checks = {
            "authority-threshold-downgrade-blocked": threshold_downgrade_blocked,
            "bound-sample-tamper-blocked": sample_tamper_blocked,
            "s2-stage-context-card-set": stage_card_passed,
            "s2-query-published": s2_query.returncode == 0,
            "s2-card-tamper-blocked": card_tamper_blocked,
            "prefreeze-query-published": prefreeze_passed,
            "postfreeze-publication-valid": postfreeze_passed,
            "future-generated-at-blocked": future_timestamp_blocked,
            "backdated-postfreeze-plan-blocked": backdated_postfreeze_blocked,
        }
        return {
            "status": "Passed" if all(checks.values()) else "Failed",
            "passed": sum(checks.values()),
            "total": len(checks),
            "checks": checks,
        }


def render_report(report: dict[str, Any]) -> str:
    comparison = report["representative_comparison"]
    lines = [
        "# T-017 Shadow 对照评测",
        "",
        f"- 状态：`{report['status']}`",
        f"- 发布阶段：`{report['publication_state']}`",
        f"- 代表性样本：`{comparison['sample_count']}`",
        f"- 无关上下文降幅代理中位数：`{comparison['median_reduction_percent']}%`",
        f"- 最低单例降幅：`{comparison['minimum_case_reduction_percent']}%`",
        f"- 强制条款覆盖：`{report['quality_gates']['mandatory_coverage_percent']}%`",
        f"- 错误放行：`{report['quality_gates']['false_allow_count']}`",
        "",
        "## 代表性样本",
        "",
        "| Sample | Task/Action | 旧路径字符 | 新路径字符 | 降幅 | 结果 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for sample in comparison["samples"]:
        lines.append(
            f"| {sample['sample_id']} | {sample['task_id']}/{sample['action']} | "
            f"{sample['legacy_matched_chars']} | {sample['new_context_chars']} | "
            f"{sample['unrelated_context_reduction_proxy_percent']}% | "
            f"{'Passed' if sample['passed'] else 'Failed'} |"
        )
    lines.extend(["", "## 发布边界", "", report["publication_gate"]["decision"], ""])
    return "\n".join(lines)


def publish_immutable_report(
    *,
    project_root: Path,
    project_id: str,
    task_id: str,
    output_dir: Path,
    report: dict[str, Any],
    sources: list[Path],
) -> dict[str, Any]:
    """Publish one content-addressed evaluation and update only a mutable pointer."""

    json_content = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    markdown_content = render_report(report)
    digest = hashlib.sha256(
        json_content.encode("utf-8") + b"\x00" + markdown_content.encode("utf-8")
    ).hexdigest()
    publication_dir = output_dir / "publications" / digest
    json_path = publication_dir / "shadow-evaluation.json"
    markdown_path = publication_dir / "shadow-evaluation.md"
    publication_dir.parent.mkdir(parents=True, exist_ok=True)
    if publication_dir.exists():
        actual_names = {path.name for path in publication_dir.iterdir() if path.is_file()}
        if actual_names != set(PUBLICATION_FILES):
            raise GovernanceError("immutable Shadow publication is partial")
        if (
            json_path.read_text(encoding="utf-8") != json_content
            or markdown_path.read_text(encoding="utf-8") != markdown_content
        ):
            raise GovernanceError("immutable Shadow publication digest collision")
        manifest = read_json(publication_dir / "publication-manifest.json")
        if manifest.get("publication_digest") != digest:
            raise GovernanceError("immutable Shadow publication manifest digest differs")
        expected_hashes = manifest.get("files")
        if not isinstance(expected_hashes, dict) or set(expected_hashes) != set(
            PUBLICATION_FILES
        ) - {"publication-manifest.json"}:
            raise GovernanceError("immutable Shadow publication manifest is incomplete")
        for name, expected_sha256 in expected_hashes.items():
            if sha256_file(publication_dir / name) != expected_sha256:
                raise GovernanceError("immutable Shadow publication file hash differs")
    else:
        publication_dir.mkdir()
        try:
            root = governance_root(project_root)
            _write_derived_view(
                root=root,
                content_path=json_path,
                content=json_content,
                project_id=project_id,
                view_id=f"DV-{task_id}-SHADOW-EVALUATION-{digest[:16]}-JSON",
                view_kind="norm-query-shadow-evaluation-json",
                sources=sources,
            )
            _write_derived_view(
                root=root,
                content_path=markdown_path,
                content=markdown_content,
                project_id=project_id,
                view_id=f"DV-{task_id}-SHADOW-EVALUATION-{digest[:16]}-MD",
                view_kind="norm-query-shadow-evaluation-review",
                sources=[json_path],
            )
            atomic_write_json(
                publication_dir / "publication-manifest.json",
                {
                    "schema_version": "6.3-candidate",
                    "publication_type": "norm-query-shadow-evaluation",
                    "publication_digest": digest,
                    "files": {
                        name: sha256_file(publication_dir / name)
                        for name in PUBLICATION_FILES
                        if name != "publication-manifest.json"
                    },
                },
            )
            if {path.name for path in publication_dir.iterdir() if path.is_file()} != set(
                PUBLICATION_FILES
            ):
                raise GovernanceError("immutable Shadow publication did not close four files")
        except BaseException:
            shutil.rmtree(publication_dir, ignore_errors=True)
            raise

    legacy_names = (
        "shadow-evaluation.json",
        "shadow-evaluation.json.view.json",
        "shadow-evaluation.md",
        "shadow-evaluation.md.view.json",
    )
    legacy_files = {
        name: sha256_file(output_dir / name)
        for name in legacy_names
        if (output_dir / name).is_file()
    }
    legacy_manifest_path = output_dir / "legacy-fixed-publication-manifest.json"
    if legacy_files:
        if set(legacy_files) != set(legacy_names):
            raise GovernanceError("legacy fixed Shadow publication is partial")
        legacy_manifest = {
            "schema_version": "6.3-candidate",
            "publication_type": "legacy-fixed-shadow-evaluation",
            "status": "ImmutableLegacyNotActive",
            "files": legacy_files,
        }
        if legacy_manifest_path.exists():
            if read_json(legacy_manifest_path) != legacy_manifest:
                raise GovernanceError("legacy fixed Shadow publication hash differs")
        else:
            atomic_write_json(legacy_manifest_path, legacy_manifest)

    pointer = {
        "schema_version": "6.3-candidate",
        "pointer_type": "norm-query-shadow-active-publication",
        "project_id": project_id,
        "task_id": task_id,
        "updated_at": now_utc(),
        "publication_digest": digest,
        "publication_state": report["publication_state"],
        "status": report["status"],
        "algorithm_version": report["algorithm_version"],
        "shadow_contract_sha256": report["shadow_contract_sha256"],
        "json_ref": json_path.relative_to(project_root).as_posix()
        if json_path.is_relative_to(project_root)
        else str(json_path),
        "json_sha256": sha256_file(json_path),
        "markdown_ref": markdown_path.relative_to(project_root).as_posix()
        if markdown_path.is_relative_to(project_root)
        else str(markdown_path),
        "markdown_sha256": sha256_file(markdown_path),
        "legacy_fixed_publication_status": "ImmutableLegacyNotActive"
        if legacy_files
        else "Absent",
        "legacy_fixed_publication_manifest_ref": str(legacy_manifest_path)
        if legacy_files
        else None,
        "legacy_fixed_publication_manifest_sha256": sha256_file(legacy_manifest_path)
        if legacy_files
        else None,
    }
    pointer_path = output_dir / "active-publication.json"
    _write_derived_view(
        root=governance_root(project_root),
        content_path=pointer_path,
        content=json.dumps(pointer, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        project_id=project_id,
        view_id=f"DV-{task_id}-SHADOW-ACTIVE-POINTER",
        view_kind="norm-query-shadow-active-pointer",
        sources=[json_path, markdown_path],
    )
    return {
        "digest": digest,
        "json_path": json_path,
        "markdown_path": markdown_path,
        "pointer_path": pointer_path,
    }


def write_failure_snapshot(args: argparse.Namespace, exc: BaseException) -> Path | None:
    """Best-effort immutable failure evidence for future evaluator failures."""

    try:
        output_dir = args.output_dir.resolve()
        task_before = args.task_dir.resolve() / "before.json"
        script_path = Path(__file__).resolve()
        query_runtime = script_path.parent / "query_norm_context.py"
        payload = {
            "schema_version": "6.3-candidate",
            "evidence_type": "norm-query-shadow-failure",
            "generated_at": now_utc(),
            "project_id": args.project_id,
            "task_id": args.task_id,
            "algorithm_version": EVALUATION_ALGORITHM_VERSION,
            "command": [sys.executable, *sys.argv],
            "exit_code": 2,
            "exception_type": type(exc).__name__,
            "error": str(exc),
            "approval_ref": args.approval_ref,
            "thresholds": {
                "median_reduction_percent": args.median_reduction_threshold,
                "minimum_case_reduction_percent": args.minimum_case_reduction_threshold,
                "mandatory_coverage_percent": args.mandatory_coverage_threshold,
                "false_allow_count": args.false_allow_threshold,
            },
            "inputs": {
                "task_contract_sha256": sha256_file(task_before) if task_before.is_file() else None,
                "evaluator_sha256": sha256_file(script_path),
                "query_runtime_sha256": sha256_file(query_runtime)
                if query_runtime.is_file()
                else None,
            },
            "stdout": "",
            "stderr": str(exc),
            "side_effects": [],
        }
        digest = canonical_sha256(payload)
        failure_dir = output_dir / "failures" / digest
        failure_path = failure_dir / "shadow-failure.json"
        failure_dir.mkdir(parents=True, exist_ok=False)
        atomic_write_json(failure_path, payload)
        atomic_write_json(
            output_dir / "latest-failure.json",
            {
                "schema_version": "6.3-candidate",
                "pointer_type": "norm-query-shadow-latest-failure",
                "status": "HistoricalFailureEvidence",
                "task_id": args.task_id,
                "updated_at": now_utc(),
                "failure_digest": digest,
                "failure_ref": str(failure_path),
                "failure_sha256": sha256_file(failure_path),
            },
        )
        return failure_path
    except (OSError, UnicodeError, GovernanceError, FileExistsError):
        return None


def main() -> int:
    args = parse_args()
    try:
        project_root = args.project_root.resolve()
        task_dir = args.task_dir.resolve()
        skill_root = Path(__file__).resolve().parent.parent
        before = read_json(task_dir / "before.json")
        if before.get("project_id") != args.project_id or before.get("task_id") != args.task_id:
            raise GovernanceError("project/task identity does not match TaskContract")
        shadow_contract = load_shadow_contract(project_root, before, args)

        validation = validate_contracts(project_root)
        gold_task_dir = project_root / ".project-governance" / "tasks" / "T-015"
        gateway, _ = query_gateway_evaluation(
            project_root=project_root,
            project_id=args.project_id,
            task_id="T-015",
            task_dir=gold_task_dir,
            index_metadata=None,
            consistency_report=None,
            budget_baseline=None,
            validation=validation,
            expected_default_path_integration=True,
        )
        hard_gates = {item["gate_id"]: item for item in gateway["hard_gates"]}
        mandatory_observation = gateway["observations"]["mandatory_clause_recall"]
        mandatory_percent = round(
            mandatory_observation["numerator"] * 100.0 / mandatory_observation["denominator"], 4
        )
        false_allow_count = int(gateway["observations"]["false_allow_count"]["value"])
        baseline_path = shadow_contract["baseline_path"]
        baseline = read_json(baseline_path)
        representative = representative_evaluation(
            project_root,
            baseline,
            shadow_contract=shadow_contract,
            median_threshold=args.median_reduction_threshold,
            minimum_threshold=args.minimum_case_reduction_threshold,
        )
        history = query_history_integrity(project_root, args.task_id)
        bootstrap = bootstrap_adversarial(project_root, args.task_id, args)
        historical = {
            f"T-{ordinal:03d}": validate_task_directory(
                project_root / ".project-governance" / "tasks" / f"T-{ordinal:03d}"
            )
            for ordinal in range(6, 10)
        }

        with tempfile.TemporaryDirectory(prefix="t017-regression-") as temp:
            temp_root = Path(temp)
            arbitrary_cwd = temp_root / "nested" / "cwd"
            arbitrary_cwd.mkdir(parents=True)
            compiled = temp_root / "t017-s4"
            compile_result = run_command(
                [
                    sys.executable, "-B", "-X", "utf8",
                    str(skill_root / "scripts" / "compile_norm_context.py"),
                    "--task-dir", str(task_dir), "--stage", "S4",
                    "--output-dir", str(compiled), "--enforce",
                ],
                cwd=arbitrary_cwd,
            )
            arbitrary_cwd_passed = compile_result.returncode == 0
            t008_output = temp_root / "t008-s5"
            t008_result = run_command(
                [
                    sys.executable, "-B", "-X", "utf8",
                    str(skill_root / "scripts" / "compile_norm_context.py"),
                    "--task-dir", str(project_root / ".project-governance" / "tasks" / "T-008"),
                    "--stage", "S5", "--output-dir", str(t008_output),
                ],
                cwd=arbitrary_cwd,
            )
            t008_baseline = (
                project_root / ".project-governance" / "generated" / "contexts" / "T-008" / "S5"
            )
            t008_passed = False
            if t008_result.returncode == 0:
                current_packet = read_json(t008_output / "norm-packet.json")
                baseline_packet = read_json(t008_baseline / "norm-packet.json")
                current_sources = current_packet["complete_source_files"]
                current_source_ids = [item["source_id"] for item in current_sources]
                baseline_source_ids = [
                    item["source_id"] for item in baseline_packet["complete_source_files"]
                ]
                current_pack = (t008_output / "norm-source-pack.md").read_text(encoding="utf-8")
                current_pack_complete = all(
                    f"SOURCE-BEGIN {item['source_id']} sha256={item['sha256']}" in current_pack
                    and runtime_asset_path(item["path"]).read_text(encoding="utf-8").rstrip()
                    in current_pack
                    for item in current_sources
                )
                frozen_pack_unchanged = (
                    sha256_file(t008_baseline / "norm-source-pack.md")
                    == validation["compatibility"]["t008_s5"]["source_pack"]["sha256"]
                )
                t008_passed = (
                    current_packet["applicable_standards"]
                    == baseline_packet["applicable_standards"]
                    and current_packet["pending_standards"]
                    == baseline_packet["pending_standards"]
                    and current_source_ids == baseline_source_ids
                    and len(current_sources) == 18
                    and current_pack_complete
                    and frozen_pack_unchanged
                    and (t008_output / "norm-packet.md").stat().st_size
                    <= int((t008_baseline / "norm-packet.md").stat().st_size * 1.10)
                )

        self_test = run_command(
            [sys.executable, "-B", "-X", "utf8", str(skill_root / "scripts" / "self_test.py")],
            cwd=project_root,
        )
        tailoring = run_command(
            [
                sys.executable, "-B", "-X", "utf8",
                str(skill_root / "scripts" / "audit_tailoring_coverage.py"),
            ],
            cwd=project_root,
        )
        task_validation = run_command(
            [
                sys.executable, "-B", "-X", "utf8",
                str(skill_root / "scripts" / "validate_task_package.py"), str(task_dir),
                "--check-mapping", "--execution-ready",
            ],
            cwd=project_root,
        )

        mirror = project_root.parent / "LFen-Skills" / skill_root.name
        mirror_comparison = compare_trees(skill_root, mirror)
        home = Path.home()
        junctions = {
            "codex": junction_status(home / ".codex" / "skills" / skill_root.name, skill_root),
            "agents": junction_status(home / ".agents" / "skills" / skill_root.name, skill_root),
        }
        quality_passed = (
            gateway["status"] == "Passed"
            and all(item["passed"] for item in hard_gates.values())
            and mandatory_percent >= args.mandatory_coverage_threshold
            and false_allow_count <= args.false_allow_threshold
            and representative["passed"]
        )
        core_checks = {
            "rqs-hard-gates": quality_passed,
            "bootstrap-adversarial": bootstrap["status"] == "Passed",
            "query-history": history["status"] == "Passed",
            "historical-t006-t009": all(not errors for errors in historical.values()),
            "arbitrary-cwd": arbitrary_cwd_passed,
            "t008-s5": t008_passed,
            "self-test": self_test.returncode == 0,
            "tailoring-22-17-137": tailoring.returncode == 0,
            "task-execution-ready": task_validation.returncode == 0,
            "junctions-target-source": all(item["targets_source"] for item in junctions.values()),
        }
        core_passed = all(core_checks.values())
        publication_ready = (
            mirror_comparison["diff_count"] == 0
            and all(item["targets_source"] for item in junctions.values())
        )
        if args.publication_state == "post-review":
            status = "Passed" if core_passed and publication_ready else "Failed"
            decision = (
                "复核后技术与入口一致性通过；正式启用仍需人工验收和release-approval。"
                if status == "Passed"
                else "复核后检查未闭合，保持Shadow并禁止发布。"
            )
        else:
            status = "ReadyForIndependentReview" if core_passed else "Failed"
            decision = (
                "技术证据已就绪，等待独立技术复核；复核前镜像差异是受控的未发布状态。"
                if status == "ReadyForIndependentReview"
                else "技术证据存在失败项，保持Shadow并禁止进入独立复核通过结论。"
            )

        report = {
            "schema_version": "6.3-candidate",
            "report_type": "norm-query-shadow-evaluation",
            "project_id": args.project_id,
            "task_id": args.task_id,
            "generated_at": now_utc(),
            "status": status,
            "publication_state": args.publication_state,
            "algorithm_version": EVALUATION_ALGORITHM_VERSION,
            "threshold_approval_ref": args.approval_ref,
            "shadow_contract_sha256": shadow_contract["contract_sha256"],
            "shadow_authority_sha256": shadow_contract["authority_sha256"],
            "representative_comparison": representative,
            "quality_gates": {
                "status": gateway["status"],
                "hard_gates": gateway["hard_gates"],
                "mandatory_coverage_percent": mandatory_percent,
                "false_allow_count": false_allow_count,
            },
            "bootstrap_adversarial": bootstrap,
            "query_history": history,
            "compatibility": {
                "historical_tasks": historical,
                "arbitrary_cwd": arbitrary_cwd_passed,
                "t008_s5": t008_passed,
                "existing_cli_contract_count": validation["compatibility"]["cli_contract_count"],
                "manifest_files": validation["manifest_files"],
                "mirror": mirror_comparison,
                "junctions": junctions,
            },
            "checks": core_checks,
            "publication_gate": {
                "independent_review_required": True,
                "human_acceptance_required": True,
                "release_approval_required": True,
                "publication_ready": publication_ready,
                "release_authorized": False,
                "decision": decision,
            },
            "remote_semantic_enabled": False,
            "v63_approved": False,
            "t018_authorized": False,
        }
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        sources = [
            task_dir / "before.json",
            shadow_contract["authority_path"],
            project_root / "05_记录与登记册" / "CHG-0015_T-017_Shadow对照与正式启用.md",
            project_root / "05_记录与登记册" / "IMA-0012_T-017_Shadow对照与发布影响分析.md",
            project_root / "05_记录与登记册" / "RQS-0001_规范条款检索网关需求规格.md",
            project_root / "05_记录与登记册" / "TDS-0001_规范条款检索网关技术设计.md",
            baseline_path,
            project_root / history["current_active_query_result"],
            skill_root / "scripts" / "query_norm_context.py",
            Path(__file__).resolve(),
        ]
        for sample in representative["samples"]:
            source_path = project_root / sample["result_ref"]
            if source_path not in sources:
                sources.append(source_path)
        publication = publish_immutable_report(
            project_root=project_root,
            project_id=args.project_id,
            task_id=args.task_id,
            output_dir=output_dir,
            report=report,
            sources=sources,
        )
        print(
            json.dumps(
                {
                    "status": status,
                    "median_reduction_percent": representative["median_reduction_percent"],
                    "minimum_case_reduction_percent": representative["minimum_case_reduction_percent"],
                    "mandatory_coverage_percent": mandatory_percent,
                    "false_allow_count": false_allow_count,
                    "mirror_diff": mirror_comparison["diff_count"],
                    "publication_digest": publication["digest"],
                    "outputs": [
                        str(publication["json_path"]),
                        str(publication["markdown_path"]),
                        str(publication["pointer_path"]),
                    ],
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
        )
        return 0 if status != "Failed" else 1
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        GovernanceError,
        KeyError,
        TypeError,
        ValueError,
        StopIteration,
    ) as exc:
        failure_path = write_failure_snapshot(args, exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        if failure_path is not None:
            print(f"FAILURE_EVIDENCE: {failure_path}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
