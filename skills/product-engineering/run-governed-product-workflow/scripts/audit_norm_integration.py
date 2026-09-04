#!/usr/bin/env python3
"""Audit T-016 bounded-query integration without authorizing publication."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from audit_norm_retrieval import query_gateway_evaluation, validate_contracts
from governance_artifacts import (
    EXPECTED_MANIFEST_ROLES,
    GovernanceError,
    _write_derived_view,
    embedded_manifest_path,
    governance_root,
    now_utc,
    read_json,
    runtime_asset_path,
    sha256_file,
    validate_query_history,
    validate_retrieval_plan,
    validate_task_directory,
)
from query_norm_context import execute_query, load_environment, validate_query_request
from validate_task_package import QUERY_PUBLICATION_FILES, inspect_active_query_tree


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--publication-state",
        choices=("pre-review", "post-review"),
        default="pre-review",
    )
    return parser.parse_args()


def inventory(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "__pycache__" and path.suffix != ".pyc"
    }


def compare_trees(source: Path, mirror: Path) -> dict[str, Any]:
    source_files = inventory(source)
    mirror_files = inventory(mirror)
    source_names = set(source_files)
    mirror_names = set(mirror_files)
    changed = sorted(
        name for name in source_names & mirror_names if source_files[name] != mirror_files[name]
    )
    missing = sorted(source_names - mirror_names)
    extra = sorted(mirror_names - source_names)
    return {
        "source_files": len(source_files),
        "mirror_files": len(mirror_files),
        "changed": changed,
        "missing_in_mirror": missing,
        "extra_in_mirror": extra,
        "diff_count": len(changed) + len(missing) + len(extra),
    }


def junction_status(path: Path, source: Path) -> dict[str, Any]:
    exists = path.exists()
    resolved = path.resolve() if exists else None
    return {
        "path": str(path),
        "exists": exists,
        "resolved_target": str(resolved) if resolved else None,
        "targets_source": bool(resolved == source.resolve()) if resolved else False,
    }


def resolve_mirror_root(project_root: Path, skill_root: Path) -> Path:
    """Use the in-repository nested skill as its own baseline when applicable."""

    resolved_project = project_root.resolve()
    resolved_skill = skill_root.resolve()
    if resolved_skill == resolved_project or resolved_skill.is_relative_to(resolved_project):
        return resolved_skill
    repository = project_root.parent / "LFen-Skills"
    nested = sorted((repository / "skills").glob(f"*/{skill_root.name}"))
    if len(nested) == 1:
        return nested[0]
    return repository / skill_root.name


def query_history_integrity(project_root: Path, task_id: str) -> dict[str, Any]:
    return validate_query_history(project_root, task_id)


def active_query_publication_adversarial(
    project_root: Path,
    task_id: str,
    stage: str,
) -> dict[str, Any]:
    """Prove that active-task readiness rejects missing and partial publications."""

    query_root = project_root / ".project-governance" / "generated" / "queries" / task_id
    _, source_results = inspect_active_query_tree(query_root)
    if len(source_results) != 1:
        raise GovernanceError(
            f"T-016 adversarial fixture requires exactly one active publication; found {len(source_results)}"
        )
    publication_relative = source_results[0].parent.relative_to(project_root)
    with tempfile.TemporaryDirectory(prefix="t016-query-publication-") as temp:
        temp_root = Path(temp)
        isolated = temp_root / project_root.name
        shutil.copytree(
            project_root,
            isolated,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        isolated_skill = isolated / "04_模板与检查清单" / "run-governed-product-workflow"
        isolated_task = isolated / ".project-governance" / "tasks" / task_id
        compile_result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-X",
                "utf8",
                str(isolated_skill / "scripts" / "compile_norm_context.py"),
                "--task-dir",
                str(isolated_task),
                "--stage",
                stage,
                "--output-dir",
                str(
                    isolated
                    / ".project-governance"
                    / "generated"
                    / "contexts"
                    / task_id
                    / stage
                ),
                "--enforce",
            ],
            cwd=isolated,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        if compile_result.returncode != 0:
            raise GovernanceError(
                "cannot prepare isolated active-query adversarial fixture: "
                + (compile_result.stdout + compile_result.stderr)[-2000:]
            )

        validator = isolated_skill / "scripts" / "validate_task_package.py"

        def readiness() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-X",
                    "utf8",
                    str(validator),
                    str(isolated_task),
                    "--execution-ready",
                ],
                cwd=isolated,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

        publication = isolated / publication_relative
        backup = temp_root / "backup"
        backup.mkdir()
        checks: dict[str, bool] = {"baseline": readiness().returncode == 0}
        for name in sorted(QUERY_PUBLICATION_FILES):
            source = publication / name
            saved = backup / name
            shutil.move(source, saved)
            checks[f"missing:{name}"] = readiness().returncode != 0
            shutil.move(saved, source)

        for name in sorted(QUERY_PUBLICATION_FILES):
            source = publication / name
            original = source.read_bytes()
            source.write_bytes(original + b"\n")
            checks[f"changed-bytes:{name}"] = readiness().returncode != 0
            source.write_bytes(original)

        saved_publication = backup / "complete-publication"
        shutil.move(publication, saved_publication)
        checks["missing:complete-publication"] = readiness().returncode != 0
        publication.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(saved_publication, publication)

        partial_page = (
            isolated
            / ".project-governance"
            / "generated"
            / "queries"
            / task_id
            / ("f" * 64)
            / "page-0001"
        )
        partial_page.mkdir(parents=True)
        for name in sorted(QUERY_PUBLICATION_FILES)[:-1]:
            (partial_page / name).write_text("adversarial\n", encoding="utf-8")
        checks["partial:paged-publication"] = readiness().returncode != 0
        shutil.rmtree(partial_page.parent)

        isolated_query_root = (
            isolated / ".project-governance" / "generated" / "queries" / task_id
        )
        saved_query_root = backup / "complete-query-root"
        shutil.move(isolated_query_root, saved_query_root)
        checks["missing:complete-query-root"] = readiness().returncode != 0
        isolated_query_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(saved_query_root, isolated_query_root)

        request_path = next((isolated_query_root / "requests").glob("*.json"))
        original_request = request_path.read_bytes()
        stale_request = json.loads(original_request.decode("utf-8"))
        stale_request["tailoring_resolution_sha256"] = "0" * 64
        request_path.write_text(
            json.dumps(stale_request, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        validate_only = subprocess.run(
            [
                sys.executable,
                "-B",
                "-X",
                "utf8",
                str(isolated_skill / "scripts" / "query_norm_context.py"),
                "--task-dir",
                str(isolated_task),
                "--request-json-file",
                str(request_path),
                "--validate-only",
            ],
            cwd=isolated,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        checks["stale-request:validate-only"] = validate_only.returncode != 0
        request_path.write_bytes(original_request)

        outside_request = isolated / ".project-governance" / "generated" / "outside-request.json"
        shutil.move(request_path, outside_request)
        try:
            request_path.symlink_to(outside_request)
            checks["link:request-file"] = readiness().returncode != 0
        finally:
            if request_path.is_symlink():
                request_path.unlink()
            shutil.move(outside_request, request_path)

        requests_root = isolated_query_root / "requests"
        outside_requests = isolated / ".project-governance" / "generated" / "outside-requests"
        shutil.move(requests_root, outside_requests)
        try:
            requests_root.symlink_to(outside_requests, target_is_directory=True)
            checks["link:request-registry"] = readiness().returncode != 0
        finally:
            if requests_root.is_symlink():
                requests_root.unlink()
            shutil.move(outside_requests, requests_root)

        checks["restored"] = readiness().returncode == 0
        return {
            "status": "Passed" if all(checks.values()) else "Failed",
            "passed": sum(checks.values()),
            "total": len(checks),
            "checks": checks,
            "active_result_ref": source_results[0].relative_to(project_root).as_posix(),
        }


def render_report(report: dict[str, Any]) -> str:
    gateway = report["query_gateway"]
    compatibility = report["compatibility"]
    lines = [
        f"# T-016 规范条款查询集成评估",
        "",
        f"- 状态：`{report['status']}`",
        f"- 发布阶段：`{report['publication_state']}`",
        f"- 查询门户：`{gateway['status']}`",
        f"- Gold cases：`{gateway['case_summary']['passed']}/{gateway['case_summary']['total']}`",
        f"- 对抗检查：`{gateway['adversarial_tests']['passed']}/{gateway['adversarial_tests']['total']}`",
        f"- 历史 T-006..T-009：`{compatibility['historical_tasks_passed']}/4`",
        f"- 规范源/镜像 DIFF：`{compatibility['mirror']['diff_count']}`",
        "",
        "## 发布边界",
        "",
        report["publication_gate"]["decision"],
        "",
        "## 核心检查",
        "",
    ]
    for name, check in report["checks"].items():
        lines.append(f"- {name}: `{'Passed' if check['passed'] else 'Failed'}` — {check['detail']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        project_root = args.project_root.resolve()
        task_dir = args.task_dir.resolve()
        skill_root = Path(__file__).resolve().parent.parent
        output_dir = args.output_dir.resolve()
        before = read_json(task_dir / "before.json")
        if before.get("project_id") != args.project_id or before.get("task_id") != args.task_id:
            raise GovernanceError("project/task identity does not match the frozen TaskContract")
        validation = validate_contracts(project_root)
        plan_errors = validate_retrieval_plan(task_dir)
        environment = load_environment(task_dir)
        plan_path = (
            governance_root(project_root)
            / "generated"
            / "contexts"
            / args.task_id
            / before["tailoring_resolution"]["stage"]
            / "retrieval-plan.json"
        )
        plan = read_json(plan_path)
        smoke_request = dict(plan["request_template"])
        smoke_request["action"] = "run_started"
        smoke_request["query_text"] = "开始执行前的权限、Authority、Gate、完整性和失败关闭条款"
        smoke_request = validate_query_request(smoke_request, environment)
        smoke_result = execute_query(smoke_request, environment)
        smoke_source_ids = {item["source_id"] for item in smoke_result["citations"]}
        smoke_passed = (
            smoke_result["status"] in {"Complete", "Expanded"}
            and bool(smoke_result["citations"])
            and smoke_source_ids.issubset(set(environment.source_ids))
        )
        active_query_adversarial = active_query_publication_adversarial(
            project_root,
            args.task_id,
            str(before["tailoring_resolution"]["stage"]),
        )
        query_history = query_history_integrity(project_root, args.task_id)
        gold_task_dir = project_root / ".project-governance" / "tasks" / "T-015"
        gold_before = read_json(gold_task_dir / "before.json")
        gateway, _ = query_gateway_evaluation(
            project_root=project_root,
            project_id=args.project_id,
            task_id=gold_before["task_id"],
            task_dir=gold_task_dir,
            index_metadata=None,
            consistency_report=None,
            budget_baseline=None,
            validation=validation,
            expected_default_path_integration=True,
        )
        gateway["integration_task_id"] = args.task_id
        gateway["gold_fixture_task_id"] = gold_before["task_id"]
        historical: dict[str, list[str]] = {}
        for ordinal in range(6, 10):
            historical_id = f"T-{ordinal:03d}"
            historical[historical_id] = validate_task_directory(
                project_root / ".project-governance" / "tasks" / historical_id
            )
        with tempfile.TemporaryDirectory(prefix="t016-arbitrary-cwd-") as temp:
            temp_root = Path(temp)
            cwd = temp_root / "nested" / "working-directory"
            output = temp_root / "compiled"
            cwd.mkdir(parents=True)
            compile_result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-X",
                    "utf8",
                    str(skill_root / "scripts" / "compile_norm_context.py"),
                    "--task-dir",
                    str(task_dir),
                    "--stage",
                    str(before["tailoring_resolution"]["stage"]),
                    "--output-dir",
                    str(output),
                    "--enforce",
                ],
                cwd=cwd,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            arbitrary_cwd_ok = compile_result.returncode == 0 and all(
                (output / name).is_file()
                for name in (
                    "norm-packet.json",
                    "norm-packet.md",
                    "norm-source-pack.md",
                    "retrieval-plan.json",
                    "retrieval-plan.json.view.json",
                )
            )
            t008_task_dir = project_root / ".project-governance" / "tasks" / "T-008"
            t008_output = temp_root / "t008-s5"
            t008_compile = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-X",
                    "utf8",
                    str(skill_root / "scripts" / "compile_norm_context.py"),
                    "--task-dir",
                    str(t008_task_dir),
                    "--stage",
                    "S5",
                    "--output-dir",
                    str(t008_output),
                ],
                cwd=cwd,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            t008_baseline = (
                project_root / ".project-governance" / "generated" / "contexts" / "T-008" / "S5"
            )
            t008_files_ok = all(
                (directory / name).is_file()
                for directory in (t008_output, t008_baseline)
                for name in ("norm-packet.json", "norm-packet.md", "norm-source-pack.md")
            )
            t008_context_ok = False
            t008_navigation_bytes: int | None = None
            t008_baseline_navigation_bytes = (t008_baseline / "norm-packet.md").stat().st_size
            if t008_compile.returncode == 0 and t008_files_ok:
                t008_current_packet = read_json(t008_output / "norm-packet.json")
                t008_baseline_packet = read_json(t008_baseline / "norm-packet.json")
                current_sources = t008_current_packet["complete_source_files"]
                baseline_source_ids = [
                    item["source_id"] for item in t008_baseline_packet["complete_source_files"]
                ]
                current_source_ids = [item["source_id"] for item in current_sources]
                current_source_pack = (t008_output / "norm-source-pack.md").read_text(
                    encoding="utf-8"
                )
                current_pack_complete = all(
                    f"SOURCE-BEGIN {item['source_id']} sha256={item['sha256']}" in current_source_pack
                    and runtime_asset_path(item["path"]).read_text(encoding="utf-8").rstrip()
                    in current_source_pack
                    for item in current_sources
                )
                frozen_source_pack_unchanged = sha256_file(
                    t008_baseline / "norm-source-pack.md"
                ) == validation["compatibility"]["t008_s5"]["source_pack"]["sha256"]
                t008_context_ok = (
                    all(
                        t008_current_packet[field] == t008_baseline_packet[field]
                        for field in (
                            "applicable_standards",
                            "pending_standards",
                        )
                    )
                    and current_source_ids == baseline_source_ids
                    and len(current_sources) == 18
                    and current_pack_complete
                    and frozen_source_pack_unchanged
                    and (t008_output / "norm-packet.md").stat().st_size
                    <= int(t008_baseline_navigation_bytes * 1.10)
                )
                t008_navigation_bytes = (t008_output / "norm-packet.md").stat().st_size

        mirror = resolve_mirror_root(project_root, skill_root)
        mirror_comparison = compare_trees(skill_root, mirror)
        home = Path.home()
        junctions = {
            "codex": junction_status(home / ".codex" / "skills" / skill_root.name, skill_root),
            "agents": junction_status(home / ".agents" / "skills" / skill_root.name, skill_root),
        }
        checks = {
            "retrieval-plan": {
                "passed": not plan_errors,
                "detail": "valid" if not plan_errors else "; ".join(plan_errors),
            },
            "runtime-contracts": {
                "passed": validation["manifest_files"] == sum(EXPECTED_MANIFEST_ROLES.values())
                and validation["compatibility"]["cli_contract_count"] == 14,
                "detail": f"manifest={validation['manifest_files']}, cli={validation['compatibility']['cli_contract_count']}",
            },
            "query-gold-and-adversarial": {
                "passed": gateway["status"] == "Passed",
                "detail": f"gateway={gateway['status']}",
            },
            "t016-end-to-end-query": {
                "passed": smoke_passed,
                "detail": (
                    f"status={smoke_result['status']}, citations={len(smoke_result['citations'])}, "
                    f"sources={','.join(sorted(smoke_source_ids))}"
                ),
            },
            "active-query-publication-adversarial": {
                "passed": active_query_adversarial["status"] == "Passed",
                "detail": (
                    f"{active_query_adversarial['passed']}/"
                    f"{active_query_adversarial['total']} active-publication integrity checks"
                ),
            },
            "query-history-integrity": {
                "passed": query_history["status"] == "Passed",
                "detail": (
                    f"{query_history['publications']} archived publications / "
                    f"{query_history['files']} immutable files"
                ),
            },
            "historical-logical-paths": {
                "passed": all(not errors for errors in historical.values()),
                "detail": json.dumps(historical, ensure_ascii=False, sort_keys=True),
            },
            "arbitrary-cwd-compile": {
                "passed": arbitrary_cwd_ok,
                "detail": f"returncode={compile_result.returncode}",
            },
            "t008-context-regression": {
                "passed": t008_context_ok,
                "detail": (
                    f"returncode={t008_compile.returncode}, navigation_bytes="
                    f"{t008_navigation_bytes if t008_navigation_bytes is not None else 'missing'}/"
                    f"{t008_baseline_navigation_bytes}"
                ),
            },
            "shadow-boundary": {
                "passed": gateway.get("default_path_integration") is True
                and gateway.get("remote_semantic_enabled") is False
                and read_json(
                    project_root
                    / ".project-governance"
                    / "generated"
                    / "contexts"
                    / args.task_id
                    / before["tailoring_resolution"]["stage"]
                    / "retrieval-plan.json"
                )["activation"]
                == {"mode": "Shadow", "release_authorized": False, "remote_semantic_enabled": False},
                "detail": "local Shadow; no release authority",
            },
        }
        core_passed = all(check["passed"] for check in checks.values())
        publication_ready = (
            mirror_comparison["diff_count"] == 0
            and all(item["targets_source"] for item in junctions.values())
        )
        if args.publication_state == "post-review":
            status = "Passed" if core_passed and publication_ready else "Failed"
            decision = (
                "独立复核后发布一致性检查已通过。"
                if publication_ready
                else "后复核发布检查未闭合：镜像或 Junction 不一致。"
            )
        else:
            status = "ReadyForIndependentReview" if core_passed else "Failed"
            decision = (
                "当前是复核前证据包；镜像差异为预期的未发布状态。"
                "未通过独立技术复核前，禁止发布到镜像或声称默认启用。"
            )
        report = {
            "schema_version": "6.3-candidate",
            "report_type": "norm-query-integration-evaluation",
            "project_id": args.project_id,
            "task_id": args.task_id,
            "generated_at": now_utc(),
            "status": status,
            "publication_state": args.publication_state,
            "checks": checks,
            "query_gateway": gateway,
            "active_query_publication_adversarial": active_query_adversarial,
            "query_history": query_history,
            "compatibility": {
                "historical_tasks": historical,
                "historical_tasks_passed": sum(not errors for errors in historical.values()),
                "mirror": mirror_comparison,
                "junctions": junctions,
            },
            "publication_gate": {
                "independent_review_required": True,
                "human_acceptance_required": True,
                "publication_ready": publication_ready,
                "decision": decision,
            },
            "evidence_gaps": [
                {
                    "event_id": "RUN-T016-001-E0010",
                    "original_ref": (
                        ".project-governance/generated/queries/T-016/"
                        "4c830baa885889c933f81ca6f46b8734cdbc3c5f6c83b2958f716e8c8b84bf92/"
                        "query-result.json"
                    ),
                    "status": "Documented-Unavailable",
                    "reason": (
                        "the failed-attempt query publication was removed during deterministic "
                        "cleanup after its validator defect was found; its original bytes are unavailable"
                    ),
                    "impact": (
                        "the RunLedger failure fact remains authoritative; this unavailable output is "
                        "not used by any passing check or gate conclusion"
                    ),
                    "superseding_verification_ref": (
                        active_query_adversarial["active_result_ref"]
                    ),
                }
            ],
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        root = governance_root(project_root)
        json_path = output_dir / "integration-evaluation.json"
        markdown_path = output_dir / "integration-evaluation.md"
        sources = [
            task_dir / "before.json",
            gold_task_dir / "before.json",
            plan_path,
            embedded_manifest_path(),
            runtime_asset_path("mappings/norm-action-taxonomy.json"),
            runtime_asset_path("evaluations/norm-retrieval-gold.json"),
            environment.index_metadata_path,
            environment.consistency_report_path,
            environment.budget_baseline_path,
            skill_root / "SKILL.md",
            skill_root / "scripts" / "compile_norm_context.py",
            skill_root / "scripts" / "query_norm_context.py",
            skill_root / "scripts" / "validate_task_package.py",
            skill_root / "scripts" / "self_test.py",
            project_root / ".project-governance" / "generated" / "query-history" / args.task_id / "archive-index.json",
            Path(__file__).resolve(),
        ]
        _write_derived_view(
            root=root,
            content_path=json_path,
            content=json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            project_id=args.project_id,
            view_id=f"DV-{args.task_id}-NORM-INTEGRATION-JSON",
            view_kind="norm-query-integration-evaluation-json",
            sources=sources,
        )
        _write_derived_view(
            root=root,
            content_path=markdown_path,
            content=render_report(report),
            project_id=args.project_id,
            view_id=f"DV-{args.task_id}-NORM-INTEGRATION-MD",
            view_kind="norm-query-integration-evaluation-review",
            sources=[json_path],
        )
        print(json.dumps({
            "status": status,
            "outputs": [str(json_path), str(markdown_path)],
            "mirror_diff": mirror_comparison["diff_count"],
        }, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if status != "Failed" else 1
    except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
