#!/usr/bin/env python3
"""Query the deterministic local norm index with bounded, cited context.

This is the T-015 query gateway integrated by T-016 through a validated,
unreleased retrieval plan.  Query results remain Shadow-mode DerivedViews.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from build_norm_index import (  # noqa: E402
    canonical_json_bytes,
    fts_phrase,
    load_sources,
    normalize_term,
    reconstruct_clause,
    sha256_file,
    validate_index,
)
from compile_norm_context import render_packet  # noqa: E402
from governance_artifacts import (  # noqa: E402
    GovernanceError,
    _write_derived_view,
    atomic_write_json,
    embedded_manifest_path,
    load_tailoring_map,
    now_utc,
    read_json,
    require_valid_json_document,
    runtime_asset_path,
    validate_embedded_manifest,
    validate_retrieval_plan,
    validate_task_directory,
)


HEX64_RE = re.compile(r"^[a-f0-9]{64}$")
IDENTIFIER_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)+(?![A-Za-z0-9])")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,}|[0-9]{2,}")
HAN_RE = re.compile(r"[\u3400-\u9fff]{2,}")
QUOTE_RE = re.compile(r"[`“\"]([^`“”\"\n]{2,80})[`”\"]")
QUERY_SCHEMA = "norm-query.schema.json"
RESULT_SCHEMA = "norm-query-result.schema.json"
LOCATOR_KIND = "derived-retrieval-locator"
RRF_K = 60
MAX_QUERY_TEXT_CHARS = 16_384
MAX_QUERY_TERM_CHARS = 256
MAX_QUERY_TERMS = 256
MAX_REQUEST_BYTES = 65_536
MAX_CLAUSE_ROWS = 100_000
SQLITE_PROGRESS_GRANULARITY = 1_000
SQLITE_PROGRESS_STEP_LIMIT = 2_000_000
PUBLICATION_LOCK_TIMEOUT_SECONDS = 10.0
PUBLICATION_LOCK_DIGEST_CHARS = 32
SAFE_CONFLICT_DIAGNOSTIC_RE = re.compile(
    r"(?:"
    r"(?:没有|缺少|无)?(?:有效)?一致性报告(?:或存在 blocker)?时?(?:能否|是否|可否)?(?:建|创建|构建)索引|"
    r"规范修复后(?:如何)?(?:刷新|更新)(?:来源)?(?:摘要|快照)|"
    r"(?:missing )?consistency report(?: or blocker exists)?(?:,? can we)? build (?:the )?index|"
    r"after norm(?:ative)? repair,? (?:refresh|update) (?:the )?(?:digest|snapshot)"
    r")[?？。.!！]*",
    re.IGNORECASE,
)


def publication_lock_path(target_path: Path) -> Path:
    """Return a collision-resistant lock path with a platform-bounded file name."""
    normalized_target = os.path.normcase(str(target_path.resolve()))
    target_digest = sha256_bytes(normalized_target.encode("utf-8"))[
        :PUBLICATION_LOCK_DIGEST_CHARS
    ]
    return target_path.parent / f".publication-{target_digest}.lock"


@contextmanager
def publication_lock(lock_path: Path, timeout_seconds: float = PUBLICATION_LOCK_TIMEOUT_SECONDS):
    """Serialize one content-addressed publication and fail closed on stale locks."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()}:{time.time_ns()}"
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise GovernanceError(f"publication lock is held or stale: {lock_path}")
            time.sleep(0.01)
            continue
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(token + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        break
    try:
        yield
    finally:
        try:
            current = lock_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError as exc:
            raise GovernanceError(f"publication lock disappeared: {lock_path}") from exc
        if current != token:
            raise GovernanceError(f"publication lock ownership changed: {lock_path}")
        lock_path.unlink()


STAGE_REQUIRED_CONTROLS: dict[str, frozenset[str]] = {
    "S0": frozenset({"definition"}),
    "S1": frozenset({"scope"}),
    "S2": frozenset({"evidence"}),
    "S3": frozenset({"change"}),
    "S4": frozenset({"integrity"}),
    "S5": frozenset({"evidence"}),
    "S6": frozenset({"gate"}),
    "S7": frozenset({"release"}),
    "S8": frozenset({"records"}),
}
NORM_PACKET_SOURCE_CONTROLS: dict[str, frozenset[str]] = {
    "VC-PPG-COM-001": frozenset({"definition"}),
    "VC-PPG-COM-002": frozenset({"definition", "records"}),
    "VC-PPG-DEC-001": frozenset({"applicability", "prohibition"}),
    "VC-PPG-PRO-001": frozenset({"scope", "execution", "gate"}),
    "VC-PPG-IDX-001": frozenset({"records", "evidence"}),
    "C02": frozenset({"applicability", "scope", "definition"}),
    "C05": frozenset({"validation", "evidence", "prohibition"}),
    "C06": frozenset({"scope", "change", "validation"}),
    "C07": frozenset({"authority", "permission", "prohibition", "gate"}),
    "C08": frozenset({"integrity", "freshness", "evidence"}),
    "C09": frozenset({"execution", "evidence", "records"}),
    "C10": frozenset({"records", "evidence", "authority"}),
    "C11": frozenset({"change", "freshness", "integrity", "release"}),
    "C12": frozenset({"gate", "validation", "prohibition", "release"}),
    "E01": frozenset({"scope", "change", "integrity"}),
    "E03": frozenset({"data", "permission", "prohibition"}),
    "E04": frozenset({"records", "freshness", "evidence"}),
}
CONTROL_SOURCE_ROUTES: dict[str, tuple[str, ...]] = {
    "applicability": ("VC-PPG-DEC-001", "VC-PPG-PRO-001"),
    "scope": ("C07", "C02", "VC-PPG-PRO-001"),
    "authority": ("C07", "C09", "C12"),
    "permission": ("C09", "C07"),
    "prohibition": ("C12", "C09", "C07"),
    "gate": ("C12", "C07", "C05"),
    "evidence": ("C08", "C10", "C05", "C09"),
    "integrity": ("C08", "C09", "C11"),
    "freshness": ("C09", "C08", "C11"),
    "change": ("C11", "C10"),
    "execution": ("C09",),
    "validation": ("C05", "C12"),
    "release": ("C11", "C12", "E05"),
    "records": ("C10", "C09", "C08", "E04"),
    "data": ("E03",),
    "definition": ("VC-PPG-COM-001", "VC-PPG-COM-002"),
}
CONTROL_QUERY_TERMS: dict[str, tuple[str, ...]] = {
    "applicability": ("适用", "未激活", "tailoring", "来源边界", "source boundary"),
    "scope": ("范围", "来源边界", "source id", "逻辑路径"),
    "authority": ("authority", "有权", "批准", "approval", "authorization"),
    "permission": ("权限", "授权", "permission", "authorization", "未授权"),
    "prohibition": ("不得", "禁止", "阻断", "blocked", "失败关闭", "能否"),
    "gate": ("gate", "门禁", "独立复核", "review", "shadow"),
    "evidence": ("evidence", "证据", "引用", "来源证明", "重放", "固定输入", "结果摘要", "连续执行"),
    "integrity": ("完整性", "manifest", "哈希", "摘要", "越界", "确定性", "replay"),
    "freshness": ("陈旧", "刷新", "版本", "snapshot", "stale", "兼容"),
    "change": ("变更", "刷新", "兼容", "cli", "回滚", "一致性报告", "manifest", "未知 source id", "错哈希", "索引"),
    "execution": ("run_started", "执行", "runledger", "retry", "close_task"),
    "validation": (
        "验证", "验收", "硬门槛", "validation", "verification", "shadow",
        "required present missing", "coverage",
    ),
    "release": ("发布", "上线", "remote", "远程", "rerank"),
    "records": ("记录", "runledger", "derivedview", "clause context", "source pack", "检索定位符", "完整来源", "分页"),
    "data": ("数据", "data", "dataset", "外发", "embedding", "rerank", "semantic"),
    "definition": ("定义", "标题", "列表", "表格", "代码块", "clause id"),
}
CONTROL_QUERY_TERM_EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "data": ("数据库",),
}
PINNED_SECTION_ROUTES: tuple[tuple[str, str, frozenset[str]], ...] = (
    ("C07", r"^5\.3(?:\s|$)", frozenset({"authority", "prohibition"})),
    ("C07", r"^8\.0(?:\s|$)", frozenset({"authority", "permission", "gate"})),
    ("C08", r"^5\.4(?:\s|$)", frozenset({"authority", "prohibition", "freshness", "integrity"})),
    ("C08", r"^10\.12(?:\s|$)", frozenset({"integrity", "records", "evidence"})),
    ("C09", r"^8\.0(?:\s|$)", frozenset({"execution", "records", "evidence"})),
    ("C09", r"^9\.7(?:\s|$)", frozenset({"execution", "freshness", "prohibition"})),
    ("C09", r"^10\.8(?:\s|$)", frozenset({"authority", "permission", "prohibition"})),
    ("C11", r"^10\.8(?:\s|$)", frozenset({"change", "authority", "evidence"})),
    ("C12", r"^2(?:\.|\s)", frozenset({"gate", "validation", "prohibition"})),
    ("C12", r"^5\.1(?:\s|$)", frozenset({"prohibition", "gate"})),
    ("E03", r"^5\.5(?:\s|$)", frozenset({"applicability", "prohibition", "data"})),
    ("E03", r"^7\.3(?:\s|$)", frozenset({"authority", "permission", "data", "prohibition"})),
)
REQUIRED_SECTION_ROUTES: dict[str, tuple[tuple[str, str], ...]] = {
    "execution": (("C09", r"^9\.7(?:\s|$)"),),
    "change": (("C11", r"^10\.8(?:\s|$)"),),
    "freshness": (("C11", r"^10\.8(?:\s|$)"),),
    "data": (("E03", r"^5\.5(?:\s|$)"), ("E03", r"^7\.3(?:\s|$)")),
}


@dataclass(frozen=True)
class QueryEnvironment:
    project_root: Path
    task_dir: Path
    task_contract_path: Path
    index_metadata_path: Path
    index_path: Path
    consistency_report_path: Path
    budget_baseline_path: Path
    taxonomy_path: Path
    norm_packet_json_path: Path
    norm_packet_markdown_path: Path
    task_contract: dict[str, Any]
    index_metadata: dict[str, Any]
    consistency_report: dict[str, Any]
    budgets: dict[str, Any]
    taxonomy: dict[str, Any]
    norm_packet: dict[str, Any]
    norm_packet_control_types: tuple[str, ...]
    norm_packet_json_sha256: str
    norm_packet_markdown_sha256: str
    source_ids: tuple[str, ...]
    tailoring_sha256: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    """Atomically write JSON without deriving a temporary name from the target name."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".aw.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def canonical_tree(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [canonical_tree(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonical_tree(item) for key, item in value.items()}
    return value


def tailoring_resolution_digest(resolution: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(canonical_tree(resolution)))


def normalized_request(request: dict[str, Any]) -> dict[str, Any]:
    normalized = canonical_tree(request)
    normalized["query_text"] = normalized["query_text"].strip()
    normalized["modes"] = sorted(set(normalized["modes"]))
    normalized["requested_additional_control_types"] = sorted(
        set(normalized["requested_additional_control_types"])
    )
    return normalized


def query_digest(
    request: dict[str, Any], environment: QueryEnvironment, *, page: int = 1
) -> str:
    profile = environment.budgets.get("profiles", {}).get(request.get("budget_profile"))
    material = {
        "request": normalized_request(request),
        "page": page,
        # A task may be queried before and after run_started freezes its
        # contract.  Bind the digest to the freeze boundary so a pre-freeze
        # immutable publication is retained as history and a post-freeze
        # request gets a fresh target instead of colliding with it.
        "task_contract_frozen_at": environment.task_contract.get("frozen_at"),
        "tailoring_resolution_sha256": environment.tailoring_sha256,
        "normative_sources_sha256": environment.index_metadata["normative_sources_sha256"],
        "consistency_report_sha256": environment.index_metadata["consistency_report_sha256"],
        "parser_sha256": environment.index_metadata["parser_sha256"],
        "index_schema_version": environment.index_metadata["index_schema_version"],
        "action_taxonomy_sha256": environment.index_metadata["action_taxonomy_sha256"],
        "deterministic_modes": sorted(mode for mode in request["modes"] if mode != "semantic"),
        "budget_profile_definition": profile,
        "budget_baseline_sha256": sha256_file(environment.budget_baseline_path),
        "index_metadata_sha256": sha256_file(environment.index_metadata_path),
        "query_engine_sha256": sha256_file(Path(__file__).resolve()),
        "norm_packet_json_sha256": sha256_file(environment.norm_packet_json_path),
        "norm_packet_markdown_sha256": sha256_file(environment.norm_packet_markdown_path),
        "required_control_derivation": required_control_derivation(
            request,
            environment.taxonomy["actions"][request["action"]],
            environment,
        ),
    }
    return sha256_bytes(canonical_json_bytes(canonical_tree(material)))


def discover_single(paths: Iterable[Path], label: str, predicate: Any | None = None) -> Path:
    candidates = sorted({path.resolve() for path in paths if path.is_file()}, key=lambda path: str(path))
    if predicate is not None:
        candidates = [path for path in candidates if predicate(path)]
    if len(candidates) != 1:
        rendered = ", ".join(str(path) for path in candidates) or "none"
        raise GovernanceError(f"{label} must resolve exactly once; found {rendered}")
    return candidates[0]


def require_canonical_path(candidate: Path | None, canonical: Path, label: str) -> Path:
    canonical = canonical.resolve()
    if candidate is None:
        return canonical
    resolved = candidate.resolve()
    if resolved != canonical:
        raise GovernanceError(f"{label} must use canonical project input: {canonical}")
    return resolved


def project_root_from_task_dir(task_dir: Path) -> Path:
    resolved = task_dir.resolve()
    if resolved.parent.name != "tasks" or resolved.parent.parent.name != ".project-governance":
        raise GovernanceError("task directory must be .project-governance/tasks/<TaskID>")
    return resolved.parent.parent.parent


def _ready_index_metadata(path: Path) -> bool:
    try:
        document = read_json(path)
        report_path = path.parent / "norm-consistency-audit.json"
        report = read_json(report_path)
    except (OSError, json.JSONDecodeError, GovernanceError):
        return False
    return (
        document.get("status") == "Ready"
        and isinstance(document.get("index_digest"), str)
        and document.get("parser_sha256")
        == sha256_file(Path(__file__).resolve().with_name("build_norm_index.py"))
        and document.get("action_taxonomy_sha256")
        == sha256_file(runtime_asset_path("mappings/norm-action-taxonomy.json"))
        and report.get("inputs", {}).get("manifest_sha256")
        == sha256_file(embedded_manifest_path())
        and document.get("consistency_report_sha256") == sha256_file(report_path)
    )


def _matching_consistency(path: Path, digest: str) -> bool:
    try:
        return sha256_file(path) == digest
    except (OSError, json.JSONDecodeError, GovernanceError, KeyError, TypeError, ValueError):
        return False


def load_environment(
    task_dir: Path,
    *,
    index_metadata_path: Path | None = None,
    consistency_report_path: Path | None = None,
    budget_baseline_path: Path | None = None,
) -> QueryEnvironment:
    manifest_errors = validate_embedded_manifest()
    if manifest_errors:
        raise GovernanceError("embedded runtime is invalid: " + "; ".join(manifest_errors))
    project_root = project_root_from_task_dir(task_dir)
    task_contract_path = task_dir.resolve() / "before.json"
    task_contract = read_json(task_contract_path)
    task_errors = validate_task_directory(task_dir.resolve())
    if task_errors:
        raise GovernanceError("TaskContract package is invalid: " + "; ".join(task_errors))
    if not (task_dir.resolve() / "after.json").is_file():
        plan_errors = validate_retrieval_plan(task_dir.resolve())
        if plan_errors:
            raise GovernanceError("retrieval plan is invalid: " + "; ".join(plan_errors))
    resolution = task_contract.get("tailoring_resolution")
    if not isinstance(resolution, dict):
        raise GovernanceError("TaskContract has no tailoring_resolution")
    complete_sources = resolution.get("complete_source_files")
    if not isinstance(complete_sources, list) or not complete_sources:
        raise GovernanceError("tailoring_resolution.complete_source_files must be non-empty")
    source_ids: list[str] = []
    for position, item in enumerate(complete_sources):
        if not isinstance(item, dict) or not isinstance(item.get("source_id"), str):
            raise GovernanceError(f"complete_source_files[{position}] is invalid")
        source_ids.append(item["source_id"])
    if len(source_ids) != len(set(source_ids)):
        raise GovernanceError("tailoring_resolution contains duplicate Source IDs")

    packet_stage = resolution.get("stage")
    if not isinstance(packet_stage, str) or packet_stage not in STAGE_REQUIRED_CONTROLS:
        raise GovernanceError("tailoring_resolution.stage is invalid for Norm Packet lookup")
    packet_dir = (
        project_root
        / ".project-governance"
        / "generated"
        / "contexts"
        / str(task_contract.get("task_id"))
        / packet_stage
    )
    packet_json_path = packet_dir / "norm-packet.json"
    packet_markdown_path = packet_dir / "norm-packet.md"
    if not packet_json_path.is_file() or not packet_markdown_path.is_file():
        raise GovernanceError("canonical Norm Packet JSON/Markdown pair is missing")
    norm_packet = read_json(packet_json_path)
    if canonical_tree(norm_packet) != canonical_tree(resolution):
        raise GovernanceError("Norm Packet JSON does not equal the frozen Tailoring Resolution")
    for field in (
        "rule_set_sha256",
        "normative_sources_sha256",
        "resolver_sha256",
        "task_contract_schema_sha256",
        "input_digest",
        "stage",
    ):
        if norm_packet.get(field) != resolution.get(field):
            raise GovernanceError(f"Norm Packet field is stale: {field}")
    packet_sources = {
        item.get("source_id")
        for item in norm_packet.get("source_sections", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    if not packet_sources or not packet_sources.issubset(set(source_ids)):
        raise GovernanceError("Norm Packet sources escape the Tailoring Resolution boundary")
    card_sources = set(re.findall(
        r"^###\s+((?:C|E)\d{2})\s+—",
        packet_markdown_path.read_text(encoding="utf-8-sig"),
        flags=re.MULTILINE,
    ))
    expected_cards = set(norm_packet.get("stage_context_standards", []))
    if card_sources != expected_cards:
        raise GovernanceError("Norm Packet control-card source set is incomplete or stale")
    packet_controls = sorted({
        control
        for source_id in card_sources | packet_sources
        for control in NORM_PACKET_SOURCE_CONTROLS.get(source_id, frozenset())
    })
    if not packet_controls:
        raise GovernanceError("Norm Packet has no machine-mapped control cards")
    expected_packet_markdown = render_packet(
        task_contract,
        resolution,
        load_tailoring_map(),
        include_source_text=False,
    )
    if packet_markdown_path.read_text(encoding="utf-8-sig") != expected_packet_markdown:
        raise GovernanceError("Norm Packet Markdown does not match its frozen compiler inputs")

    evaluations = project_root / ".project-governance" / "generated" / "evaluations"
    metadata_candidates = list(evaluations.rglob("norm-index-metadata.json"))
    if not any(_ready_index_metadata(path) for path in metadata_candidates):
        if index_metadata_path is not None:
            raise GovernanceError("explicit index metadata was supplied but no canonical Ready publication exists")
        from build_norm_index import bootstrap_project_runtime

        bootstrap_project_runtime(task_dir.resolve())
        metadata_candidates = list(evaluations.rglob("norm-index-metadata.json"))
    canonical_metadata = discover_single(
        metadata_candidates, "ready index metadata", _ready_index_metadata
    )
    metadata_path = require_canonical_path(
        index_metadata_path, canonical_metadata, "index metadata"
    )
    metadata = read_json(metadata_path)
    require_valid_json_document(metadata, "norm-index-metadata.schema.json", str(metadata_path))
    consistency_digest = metadata.get("consistency_report_sha256")
    if not isinstance(consistency_digest, str) or not HEX64_RE.fullmatch(consistency_digest):
        raise GovernanceError("index metadata consistency_report_sha256 is invalid")
    canonical_report = discover_single(
        evaluations.rglob("norm-consistency-audit.json"),
        "matching consistency report",
        lambda path: _matching_consistency(path, consistency_digest),
    )
    report_path = require_canonical_path(
        consistency_report_path, canonical_report, "consistency report"
    )
    report = read_json(report_path)
    local_baselines = sorted(
        {path.resolve() for path in evaluations.rglob("legacy-retrieval-baseline.json") if path.is_file()},
        key=str,
    )
    if len(local_baselines) > 1:
        raise GovernanceError(
            "budget baseline must resolve at most once in the project; found "
            + ", ".join(map(str, local_baselines))
        )
    canonical_baseline = (
        local_baselines[0]
        if local_baselines
        else runtime_asset_path("evaluations/norm-retrieval-budgets.json")
    )
    baseline_path = require_canonical_path(budget_baseline_path, canonical_baseline, "budget baseline")
    baseline = read_json(baseline_path)
    try:
        budgets = baseline["benchmark"]["budget_recommendations"]
    except (KeyError, TypeError) as exc:
        raise GovernanceError("budget baseline has no measured budget recommendations") from exc
    taxonomy_path = runtime_asset_path("mappings/norm-action-taxonomy.json")
    taxonomy = read_json(taxonomy_path)
    cache_relative = metadata.get("storage", {}).get("relative_cache_path")
    if not isinstance(cache_relative, str):
        raise GovernanceError("index metadata cache path is invalid")
    index_path = (project_root / cache_relative).resolve()
    try:
        index_path.relative_to(project_root.resolve())
    except ValueError as exc:
        raise GovernanceError("index cache path escapes project root") from exc
    return QueryEnvironment(
        project_root=project_root.resolve(),
        task_dir=task_dir.resolve(),
        task_contract_path=task_contract_path,
        index_metadata_path=metadata_path,
        index_path=index_path,
        consistency_report_path=report_path,
        budget_baseline_path=baseline_path,
        taxonomy_path=taxonomy_path,
        norm_packet_json_path=packet_json_path.resolve(),
        norm_packet_markdown_path=packet_markdown_path.resolve(),
        task_contract=task_contract,
        index_metadata=metadata,
        consistency_report=report,
        budgets=budgets,
        taxonomy=taxonomy,
        norm_packet=norm_packet,
        norm_packet_control_types=tuple(packet_controls),
        norm_packet_json_sha256=sha256_file(packet_json_path),
        norm_packet_markdown_sha256=sha256_file(packet_markdown_path),
        source_ids=tuple(source_ids),
        tailoring_sha256=tailoring_resolution_digest(resolution),
    )


def request_semantic_errors(request: dict[str, Any], environment: QueryEnvironment) -> list[str]:
    errors: list[str] = []
    actions = environment.taxonomy.get("actions", {})
    action = actions.get(request.get("action"))
    if not isinstance(action, dict):
        errors.append(f"unknown action: {request.get('action')}")
        return errors
    if request.get("stage") not in action.get("stages", []):
        errors.append(f"action {request['action']} is not valid at stage {request.get('stage')}")
    resolution_stage = environment.task_contract.get("tailoring_resolution", {}).get("stage")
    packet_stage = environment.norm_packet.get("stage")
    if request.get("stage") != resolution_stage:
        errors.append(
            f"query stage {request.get('stage')} does not match Tailoring Resolution stage {resolution_stage}"
        )
    if request.get("stage") != packet_stage:
        errors.append(
            f"query stage {request.get('stage')} does not match Norm Packet stage {packet_stage}"
        )
    controls = set(environment.taxonomy.get("control_types", {}))
    unknown = sorted(set(request.get("requested_additional_control_types", [])) - controls)
    if unknown:
        errors.append("unknown requested control types: " + ", ".join(unknown))
    if request.get("task_id") != environment.task_contract.get("task_id"):
        errors.append("query task_id does not match TaskContract")
    query_text = request.get("query_text")
    if not isinstance(query_text, str):
        errors.append("query_text must be a string")
    elif len(query_text) > MAX_QUERY_TEXT_CHARS:
        errors.append(f"query_text exceeds {MAX_QUERY_TEXT_CHARS} characters")
    profiles = environment.budgets.get("profiles", {})
    profile = profiles.get(request.get("budget_profile")) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        errors.append(f"unknown budget profile: {request.get('budget_profile')}")
    else:
        for key in ("candidate_limit", "context_chars", "source_limit", "escalation_limit"):
            value = profile.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"budget profile {request.get('budget_profile')} has invalid {key}")
        if int(profile.get("candidate_limit", 0)) > MAX_CLAUSE_ROWS:
            errors.append("candidate_limit exceeds bounded local retrieval capacity")
    return errors


def validate_query_request(request: dict[str, Any], environment: QueryEnvironment) -> dict[str, Any]:
    require_valid_json_document(request, QUERY_SCHEMA, "query_request")
    errors = request_semantic_errors(request, environment)
    if errors:
        raise GovernanceError("; ".join(errors))
    return normalized_request(request)


def integrity_blockers(request: dict[str, Any], environment: QueryEnvironment) -> list[str]:
    blockers: list[str] = []
    metadata = environment.index_metadata
    resolution = environment.task_contract["tailoring_resolution"]
    if request["tailoring_resolution_sha256"] != environment.tailoring_sha256:
        blockers.append("tailoring-resolution-digest-mismatch")
    if request["normative_sources_sha256"] != resolution.get("normative_sources_sha256"):
        blockers.append("query-normative-sources-digest-mismatch")
    if metadata.get("normative_sources_sha256") != resolution.get("normative_sources_sha256"):
        blockers.append("index-normative-sources-digest-stale")
    if sha256_file(environment.consistency_report_path) != metadata.get("consistency_report_sha256"):
        blockers.append("consistency-report-digest-mismatch")
    summary = environment.consistency_report.get("summary", {})
    severities = summary.get("by_severity", {}) if isinstance(summary, dict) else {}
    if environment.consistency_report.get("audit_status") != "Complete":
        blockers.append("consistency-report-not-complete")
    if environment.consistency_report.get("norm_index_ready") is not True:
        blockers.append("norm-index-ready-gate-failed")
    if isinstance(severities, dict) and int(severities.get("Blocker", 0)) > 0:
        blockers.append("unresolved-consistency-blocker")
    if sha256_file(environment.taxonomy_path) != metadata.get("action_taxonomy_sha256"):
        blockers.append("action-taxonomy-digest-mismatch")
    manifest_errors = validate_embedded_manifest()
    if manifest_errors:
        blockers.append("embedded-manifest-invalid:" + ";".join(manifest_errors))
    try:
        _, current_normative_digest = load_sources()
    except (OSError, GovernanceError, KeyError, TypeError, ValueError) as exc:
        blockers.append("normative-source-reload-failed:" + str(exc))
    else:
        if current_normative_digest != metadata.get("normative_sources_sha256"):
            blockers.append("normative-sources-digest-mismatch")
    parser_path = Path(__file__).resolve().with_name("build_norm_index.py")
    if sha256_file(parser_path) != metadata.get("parser_sha256"):
        blockers.append("parser-digest-mismatch")
    if not environment.budget_baseline_path.is_file():
        blockers.append("budget-baseline-missing")
    if not environment.index_metadata_path.is_file():
        blockers.append("index-metadata-missing")
    if sha256_file(environment.norm_packet_json_path) != environment.norm_packet_json_sha256:
        blockers.append("norm-packet-json-changed-after-validation")
    if (
        sha256_file(environment.norm_packet_markdown_path)
        != environment.norm_packet_markdown_sha256
    ):
        blockers.append("norm-packet-markdown-changed-after-validation")
    index_source_ids = metadata.get("source_ids", [])
    unknown = sorted(set(environment.source_ids) - set(index_source_ids))
    if unknown:
        blockers.append("unknown-tailoring-source:" + ",".join(unknown))
    resolution_sources = resolution.get("complete_source_files", [])
    for item in resolution_sources:
        source_id = item.get("source_id")
        if item.get("sha256") not in {None, _source_hash(environment.index_path, source_id)}:
            blockers.append(f"tailoring-source-hash-mismatch:{source_id}")
    expected = {
        key: metadata[key]
        for key in (
            "index_schema_version", "index_digest", "normative_sources_sha256",
            "consistency_report_sha256", "parser_sha256", "action_taxonomy_sha256",
            "source_ids", "source_count", "clause_count",
        )
    }
    try:
        validate_index(environment.index_path, expected)
    except (GovernanceError, OSError, sqlite3.Error) as exc:
        blockers.append("index-integrity:" + str(exc))
    return sorted(set(blockers))


def _source_hash(index_path: Path, source_id: Any) -> str | None:
    if not isinstance(source_id, str) or not index_path.is_file():
        return None
    uri = f"{index_path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        row = connection.execute(
            "SELECT source_sha256 FROM sources WHERE source_id = ?", (source_id,)
        ).fetchone()
        return row[0] if row else None
    except sqlite3.Error:
        return None
    finally:
        if "connection" in locals():
            connection.close()


def _bounded_progress_handler() -> tuple[Any, dict[str, int]]:
    state = {"steps": 0}

    def handler() -> int:
        state["steps"] += SQLITE_PROGRESS_GRANULARITY
        return int(state["steps"] > SQLITE_PROGRESS_STEP_LIMIT)

    return handler, state


def load_clause_rows(index_path: Path, source_ids: Iterable[str]) -> list[dict[str, Any]]:
    allowed = tuple(source_ids)
    placeholders = ",".join("?" for _ in allowed)
    uri = f"{index_path.resolve().as_uri()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    progress_handler, _ = _bounded_progress_handler()
    connection.set_progress_handler(progress_handler, SQLITE_PROGRESS_GRANULARITY)
    try:
        rows: list[dict[str, Any]] = []
        for row in connection.execute(
            f"SELECT * FROM clauses WHERE source_id IN ({placeholders}) ORDER BY source_id, ordinal",
            allowed,
        ):
            item = dict(row)
            for key in ("heading_path_json", "control_types_json", "stage_tags_json", "action_tags_json"):
                item[key.removesuffix("_json")] = json.loads(item.pop(key))
            rows.append(item)
            if len(rows) > MAX_CLAUSE_ROWS:
                raise GovernanceError("tailoring source boundary exceeds clause-row resource limit")
        return rows
    except sqlite3.OperationalError as exc:
        if "interrupted" in str(exc).casefold():
            raise GovernanceError("clause loading exceeded deterministic SQLite step limit") from exc
        raise
    finally:
        connection.close()


def query_terms(request: dict[str, Any], action: dict[str, Any]) -> dict[str, list[str]]:
    query_text = request["query_text"]
    exact = set(IDENTIFIER_RE.findall(query_text))
    exact.update(match.group(1).strip() for match in QUOTE_RE.finditer(query_text))
    exact.update(str(item) for item in action.get("identifiers", []))
    words = set(WORD_RE.findall(query_text))
    words.update(str(item) for item in action.get("keywords", []) if WORD_RE.search(str(item)))
    trigrams = set(HAN_RE.findall(query_text))
    trigrams.update(str(item) for item in action.get("keywords", []) if HAN_RE.search(str(item)))
    result = {
        "exact": sorted((item for item in exact if item), key=lambda item: normalize_term(item)),
        "fts_word": sorted((item for item in words if len(item.strip()) >= 2), key=normalize_term),
        "fts_trigram": sorted((item for item in trigrams if len(item.strip()) >= 3), key=normalize_term),
    }
    flattened = [term for values in result.values() for term in values]
    if len(flattened) > MAX_QUERY_TERMS:
        raise GovernanceError(f"query expands to more than {MAX_QUERY_TERMS} local terms")
    oversized = [term for term in flattened if len(term) > MAX_QUERY_TERM_CHARS]
    if oversized:
        raise GovernanceError(f"query term exceeds {MAX_QUERY_TERM_CHARS} characters")
    return result


def lane_lookup(
    index_path: Path,
    source_ids: tuple[str, ...],
    terms: dict[str, list[str]],
    candidate_limit: int,
    modes: Iterable[str],
) -> dict[str, dict[str, int]]:
    placeholders = ",".join("?" for _ in source_ids)
    uri = f"{index_path.resolve().as_uri()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    lanes: dict[str, dict[str, int]] = {"exact": {}, "fts_word": {}, "fts_trigram": {}}
    enabled = set(modes)
    progress_handler, _ = _bounded_progress_handler()
    connection.set_progress_handler(progress_handler, SQLITE_PROGRESS_GRANULARITY)
    try:
        if "exact" in enabled:
            for term in terms["exact"]:
                rows = connection.execute(
                    f"""SELECT e.retrieval_locator
                        FROM exact_terms e JOIN clauses c ON c.retrieval_locator = e.retrieval_locator
                        WHERE e.normalized_term = ? AND c.source_id IN ({placeholders})
                        ORDER BY e.term_kind, e.retrieval_locator LIMIT ?""",
                    (normalize_term(term), *source_ids, candidate_limit),
                ).fetchall()
                _merge_lane(lanes["exact"], rows)
        if "fts" in enabled:
            for lane_name, table in (("fts_word", "clauses_unicode"), ("fts_trigram", "clauses_trigram")):
                for term in terms[lane_name]:
                    try:
                        rows = connection.execute(
                            f"""SELECT f.retrieval_locator
                                FROM {table} f JOIN clauses c ON c.retrieval_locator = f.retrieval_locator
                                WHERE {table} MATCH ? AND c.source_id IN ({placeholders})
                                ORDER BY bm25({table}), f.retrieval_locator LIMIT ?""",
                            (fts_phrase(term), *source_ids, candidate_limit),
                        ).fetchall()
                    except sqlite3.OperationalError as exc:
                        if "interrupted" in str(exc).casefold():
                            raise GovernanceError(
                                "local retrieval exceeded deterministic SQLite step limit"
                            ) from exc
                        continue
                    _merge_lane(lanes[lane_name], rows)
        return lanes
    except sqlite3.Error as exc:
        raise GovernanceError(f"local retrieval failed: {exc}") from exc
    finally:
        connection.close()


def _merge_lane(lane: dict[str, int], rows: Iterable[tuple[str]]) -> None:
    for row in rows:
        locator = row[0]
        if locator not in lane:
            lane[locator] = len(lane) + 1


def row_relevance(row: dict[str, Any], request: dict[str, Any], terms: dict[str, list[str]]) -> tuple[Any, ...]:
    folded = normalize_term(row["context_text"])
    action_hit = request["action"] in row["action_tags"]
    stage_hit = request["stage"] in row["stage_tags"]
    term_hits = sum(1 for values in terms.values() for term in values if normalize_term(term) in folded)
    modality = {"must_not": 0, "must": 1, "conditional": 2, "should": 3, "may": 4, "none": 5}
    return (
        0 if action_hit else 1,
        0 if stage_hit else 1,
        -term_hits,
        modality.get(row["normative_modality"], 6),
        row["source_id"],
        row["line_start"],
        row["retrieval_locator"],
    )


def pinned_relevance(row: dict[str, Any], request: dict[str, Any]) -> tuple[Any, ...]:
    modality = {"must_not": 0, "must": 1, "conditional": 2, "should": 3, "may": 4, "informative": 5, "none": 6}
    return (
        0 if request["action"] in row["action_tags"] else 1,
        0 if request["stage"] in row["stage_tags"] else 1,
        modality.get(row["normative_modality"], 7),
        row["line_start"],
        row["retrieval_locator"],
    )


def source_route_rank(control_type: str, source_id: str) -> int:
    route = CONTROL_SOURCE_ROUTES.get(control_type, ())
    try:
        return route.index(source_id)
    except ValueError:
        return len(route) + 1


def control_term_occurs(
    folded_text: str,
    term: str,
    *,
    excluded_compounds: tuple[str, ...] = (),
) -> bool:
    """Match an intent term without treating an ASCII or excluded CJK word fragment as intent."""

    needle = normalize_term(term)
    if not needle:
        return False
    if re.search(r"[a-z0-9_]", needle):
        return re.search(
            rf"(?<![a-z0-9_]){re.escape(needle)}(?![a-z0-9_])",
            folded_text,
        ) is not None
    excluded_ranges: list[tuple[int, int]] = []
    for compound in excluded_compounds:
        normalized = normalize_term(compound)
        start = 0
        while normalized and (position := folded_text.find(normalized, start)) >= 0:
            excluded_ranges.append((position, position + len(normalized)))
            start = position + 1
    start = 0
    while (position := folded_text.find(needle, start)) >= 0:
        end = position + len(needle)
        if not any(left <= position and end <= right for left, right in excluded_ranges):
            return True
        start = position + 1
    return False


def inferred_controls(request: dict[str, Any]) -> set[str]:
    folded = normalize_term(request["query_text"])
    return {
        control_type
        for control_type, terms in CONTROL_QUERY_TERMS.items()
        if any(
            control_term_occurs(
                folded,
                term,
                excluded_compounds=CONTROL_QUERY_TERM_EXCLUSIONS.get(control_type, ()),
            )
            for term in terms
        )
    }


def plan_candidates(
    rows: list[dict[str, Any]],
    lanes: dict[str, dict[str, int]],
    request: dict[str, Any],
    action: dict[str, Any],
    terms: dict[str, list[str]],
    candidate_limit: int,
    required: list[str],
) -> tuple[list[dict[str, Any]], dict[str, int], set[str]]:
    by_locator = {row["retrieval_locator"]: row for row in rows}
    lane_locators = set().union(*(set(lane) for lane in lanes.values()))
    pinned_types = set(action["pinned_control_types"])
    inferred = inferred_controls(request)
    pinned_unique: dict[str, dict[str, Any]] = {}
    available_sources = {row["source_id"] for row in rows}
    selected_pinned_sources: dict[str, str] = {}
    for control in sorted(pinned_types):
        selected = next((
            source_id
            for source_id in CONTROL_SOURCE_ROUTES.get(control, ())
            if source_id in available_sources
            and any(
                route_source == source_id and control in anchor_controls
                for route_source, _, anchor_controls in PINNED_SECTION_ROUTES
            )
        ), None)
        if selected is not None:
            selected_pinned_sources[control] = selected
    for source_id, heading_pattern, anchor_controls in PINNED_SECTION_ROUTES:
        matched_controls = {
            control for control, selected_source in selected_pinned_sources.items()
            if selected_source == source_id and control in anchor_controls
        }
        if not matched_controls:
            continue
        for row in rows:
            if row["source_id"] != source_id:
                continue
            if row["normative_modality"] in {"none", "informative"}:
                continue
            if any(re.match(heading_pattern, heading) for heading in row["heading_path"]):
                pinned_unique[row["retrieval_locator"]] = row
    direct_required: dict[str, dict[str, Any]] = {}
    non_pinned_required = set(required) - pinned_types
    used_sources = {row["source_id"] for row in pinned_unique.values()}
    for control_type in sorted(non_pinned_required):
        matches = [
            row for row in rows
            if control_type in row["control_types"] and row["control_types"]
        ]
        matches.sort(key=lambda row: (
            source_route_rank(control_type, row["source_id"]),
            0 if row["retrieval_locator"] in lane_locators else 1,
            *row_relevance(row, request, terms),
        ))
        if matches:
            lane_matches = [row for row in matches if row["retrieval_locator"] in lane_locators]
            route_sources = set(CONTROL_SOURCE_ROUTES.get(control_type, ()))
            existing = [
                row for row in matches
                if row["source_id"] in used_sources and row["source_id"] in route_sources
            ]
            existing_lane = [
                row for row in existing if row["retrieval_locator"] in lane_locators
            ]
            # Freshness is cross-cutting: when a selected source already carries a
            # routed freshness control, reuse it instead of introducing a fifth
            # source solely because another freshness clause ranked higher.
            # Required freshness sections are still added below, so this does not
            # remove the C11 compatibility/freshness obligation.
            if control_type == "freshness" and existing_lane:
                chosen = existing_lane[0]
            elif control_type == "freshness" and existing:
                existing.sort(key=lambda row: (
                    source_route_rank(control_type, row["source_id"]),
                    *row_relevance(row, request, terms),
                ))
                chosen = existing[0]
            elif control_type in inferred and lane_matches:
                chosen = lane_matches[0]
            elif existing_lane:
                chosen = existing_lane[0]
            elif existing:
                existing.sort(key=lambda row: (
                    source_route_rank(control_type, row["source_id"]),
                    *row_relevance(row, request, terms),
                ))
                chosen = existing[0]
            elif lane_matches:
                chosen = lane_matches[0]
            else:
                chosen = matches[0]
            direct_required[chosen["retrieval_locator"]] = chosen
            used_sources.add(chosen["source_id"])
            if control_type in inferred:
                for route_source, heading_pattern in REQUIRED_SECTION_ROUTES.get(
                    control_type, ()
                ):
                    for row in matches:
                        if row["source_id"] != route_source:
                            continue
                        if row["normative_modality"] in {"none", "informative"}:
                            continue
                        if any(
                            re.match(heading_pattern, heading)
                            for heading in row["heading_path"]
                        ):
                            direct_required[row["retrieval_locator"]] = row
                            used_sources.add(row["source_id"])
            if control_type == "evidence" and control_type in inferred:
                secondary = next((
                    row for source_id in CONTROL_SOURCE_ROUTES["evidence"][:2]
                    for row in matches
                    if row["source_id"] == source_id and row["source_id"] != chosen["source_id"]
                ), None)
                if secondary is not None:
                    direct_required[secondary["retrieval_locator"]] = secondary
                    used_sources.add(secondary["source_id"])
            if control_type == "data":
                safety_matches = [
                    row for row in matches
                    if row["source_id"] == "E03"
                    and {"data", "permission", "prohibition"}.issubset(row["control_types"])
                ]
                safety_matches.sort(key=lambda row: (
                    0 if any(re.match(r"^7\.3(?:\s|$)", heading) for heading in row["heading_path"]) else 1,
                    *row_relevance(row, request, terms),
                ))
                safety = safety_matches[0] if safety_matches else None
                if safety is not None:
                    direct_required[safety["retrieval_locator"]] = safety
                    used_sources.add(safety["source_id"])
    pinned_present = {
        control
        for row in pinned_unique.values()
        for control in row["control_types"]
        if control in pinned_types
    }
    missing_pinned = pinned_types - pinned_present
    if missing_pinned:
        raise GovernanceError(
            "deterministic Pinned Set routes do not cover: " + ", ".join(sorted(missing_pinned))
        )

    def pinned_sort_key(locator: str) -> tuple[Any, ...]:
        row = pinned_unique[locator]
        routed_controls = sorted(set(row["control_types"]) & pinned_types)
        route_rank = min(
            (source_route_rank(control, row["source_id"]) for control in routed_controls),
            default=10**6,
        )
        return (route_rank, row["source_id"], row["line_start"], locator)

    pinned_order = {
        locator: position + 1
        for position, locator in enumerate(sorted(pinned_unique, key=pinned_sort_key))
    }
    scored: list[tuple[float, str]] = []
    for locator in lane_locators:
        if (
            locator in pinned_unique
            or locator not in by_locator
            or not by_locator[locator]["control_types"]
        ):
            continue
        score = sum(1.0 / (RRF_K + lane[locator]) for lane in lanes.values() if locator in lane)
        scored.append((score, locator))
    scored.sort(key=lambda item: (-item[0], by_locator[item[1]]["source_id"], by_locator[item[1]]["line_start"], item[1]))
    planned = [pinned_unique[locator] for locator in sorted(pinned_order, key=pinned_order.get)]
    planned.extend(
        direct_required[locator]
        for locator in sorted(direct_required, key=lambda item: row_relevance(direct_required[item], request, terms))
        if locator not in pinned_unique
    )
    planned.extend(by_locator[locator] for _, locator in scored[:candidate_limit])
    return planned, pinned_order, set(direct_required)


def priority_for(
    row: dict[str, Any],
    action: dict[str, Any],
    taxonomy: dict[str, Any],
    direct_required: set[str] | None = None,
    pinned_locators: set[str] | None = None,
) -> str:
    controls = set(row["control_types"])
    if pinned_locators and row["retrieval_locator"] in pinned_locators:
        return "P0"
    if direct_required and row["retrieval_locator"] in direct_required:
        return "P1"
    for priority in ("P2", "P3"):
        if controls & set(taxonomy["priority_rules"][priority]):
            return priority
    return "P3"


def citation_for(
    row: dict[str, Any],
    *,
    lanes: dict[str, dict[str, int]],
    pinned_order: dict[str, int],
    priority: str,
    reasons: Iterable[str],
) -> dict[str, Any]:
    locator = row["retrieval_locator"]
    return {
        "retrieval_locator": locator,
        "locator_kind": LOCATOR_KIND,
        "source_id": row["source_id"],
        "source_version": row["source_version"],
        "logical_path": row["logical_path"],
        "source_sha256": row["source_sha256"],
        "heading_path": row["heading_path"],
        "line_start": row["line_start"],
        "line_end": row["line_end"],
        "chunk_sha256": row["chunk_sha256"],
        "retrieval_reason": sorted(set(reasons)),
        "lane_ranks": {
            "pinned": pinned_order.get(locator),
            "exact": lanes["exact"].get(locator),
            "fts_word": lanes["fts_word"].get(locator),
            "fts_trigram": lanes["fts_trigram"].get(locator),
            "semantic": None,
        },
        "priority": priority,
        "control_types": sorted(set(row["control_types"])) or ["background"],
        "text": row["text"],
    }


def required_control_derivation(
    request: dict[str, Any],
    action: dict[str, Any],
    environment: QueryEnvironment,
) -> dict[str, list[str]]:
    resolution = environment.task_contract["tailoring_resolution"]
    stage_controls = set(STAGE_REQUIRED_CONTROLS.get(request["stage"], frozenset()))
    tailoring_controls: set[str] = set()
    if resolution.get("blocking_reasons"):
        tailoring_controls.update({"integrity", "prohibition"})
    if resolution.get("pending_standards"):
        tailoring_controls.update({"applicability", "freshness"})
    if resolution.get("control_strength") == "enhanced":
        tailoring_controls.update(stage_controls)
    if resolution.get("independent_review") is True and request["stage"] == "S6":
        tailoring_controls.add("gate")
    if resolution.get("explicit_human_gate") is True and request["stage"] == "S6":
        tailoring_controls.update({"authority", "gate"})

    action_controls = set(action["required_control_types"]) | set(
        action["pinned_control_types"]
    )
    inferred = inferred_controls(request)
    requested = set(request["requested_additional_control_types"])
    preliminary = action_controls | stage_controls | tailoring_controls | inferred | requested
    packet_supported = preliminary & set(environment.norm_packet_control_types)
    packet_unsupported = preliminary - packet_supported
    final = packet_supported
    return {
        "stage": sorted(stage_controls),
        "action": sorted(action_controls),
        "tailoring_resolution": sorted(tailoring_controls),
        "norm_packet": sorted(packet_supported),
        "norm_packet_unsupported": sorted(packet_unsupported),
        "inferred_query": sorted(inferred),
        "requested_additional": sorted(requested),
        "final": sorted(final),
    }


def required_controls(
    request: dict[str, Any],
    action: dict[str, Any],
    environment: QueryEnvironment,
) -> list[str]:
    return required_control_derivation(request, action, environment)["final"]


def pack_candidates(
    planned: list[dict[str, Any]],
    *,
    request: dict[str, Any],
    action: dict[str, Any],
    taxonomy: dict[str, Any],
    lanes: dict[str, dict[str, int]],
    pinned_order: dict[str, int],
    direct_required: set[str],
    budget: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    planned_rank = {
        row["retrieval_locator"]: position
        for position, row in enumerate(planned)
    }
    priorities = {
        row["retrieval_locator"]: priority_for(
            row, action, taxonomy, direct_required, set(pinned_order)
        )
        for row in planned
    }
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    planned = sorted(
        {row["retrieval_locator"]: row for row in planned}.values(),
        key=lambda row: (
            order[priorities[row["retrieval_locator"]]],
            pinned_order.get(row["retrieval_locator"], 10**9),
            planned_rank[row["retrieval_locator"]],
            row["source_id"], row["line_start"], row["retrieval_locator"],
        ),
    )
    base_chars = int(budget["context_chars"])
    base_sources = int(budget["source_limit"])
    included: list[dict[str, Any]] = []
    used = 0
    sources: set[str] = set()
    omitted = 0
    expanded = False
    overflow: list[str] = []
    for row in planned:
        priority = priorities[row["retrieval_locator"]]
        required = priority in {"P0", "P1"}
        would_use = used + len(row["text"])
        new_source = row["source_id"] not in sources
        exceeds = would_use > base_chars or (new_source and len(sources) >= base_sources)
        if exceeds and not required:
            omitted += 1
            continue
        if exceeds:
            if would_use > base_chars:
                expanded = True
                overflow.append("P0/P1-context-soft-limit")
            if new_source and len(sources) >= base_sources:
                overflow.append("P0/P1-source-soft-limit")
                expanded = True
        reasons = []
        locator = row["retrieval_locator"]
        if locator in pinned_order:
            reasons.append("pinned_control")
        if locator in lanes["exact"]:
            reasons.append("exact_identifier")
        if locator in lanes["fts_word"]:
            reasons.append("fts_word")
        if locator in lanes["fts_trigram"]:
            reasons.append("fts_trigram")
        if not reasons:
            reasons.append("required_control_recovery")
        included.append(citation_for(
            row, lanes=lanes, pinned_order=pinned_order,
            priority=priority, reasons=reasons,
        ))
        used = would_use
        sources.add(row["source_id"])
    report = {
        "profile": request["budget_profile"],
        "candidate_limit": int(budget["candidate_limit"]),
        "requested_chars": base_chars,
        "used_chars": used,
        "source_limit": base_sources,
        "sources_used": len(sources),
        "escalation_limit": int(budget["escalation_limit"]),
        "escalations_used": 1 if expanded else 0,
        "omitted_count": omitted,
        "overflow_reason": ",".join(sorted(set(overflow))) if overflow else None,
    }
    return included, report, expanded


def coverage_for(citations: list[dict[str, Any]], required: list[str]) -> dict[str, list[str]]:
    present_all = {control for item in citations for control in item["control_types"]}
    present = sorted(set(required) & present_all)
    missing = sorted(set(required) - set(present))
    return {"required": required, "present": present, "missing": missing}


def refresh_budget_usage(
    budget_report: dict[str, Any],
    citations: list[dict[str, Any]],
    *,
    escalation_delta: int = 0,
    omitted_delta: int = 0,
    overflow_reason: str | None = None,
) -> dict[str, Any]:
    reasons = {
        item for item in str(budget_report.get("overflow_reason") or "").split(",") if item
    }
    if overflow_reason:
        reasons.add(overflow_reason)
    return {
        **budget_report,
        "used_chars": sum(len(item["text"]) for item in citations),
        "sources_used": len({item["source_id"] for item in citations}),
        "escalations_used": int(budget_report["escalations_used"]) + escalation_delta,
        "omitted_count": int(budget_report["omitted_count"]) + omitted_delta,
        "overflow_reason": ",".join(sorted(reasons)) if reasons else None,
    }


def paginate_source_rows(
    rows: list[dict[str, Any]],
    page_chars: int,
    source_limit: int | None = None,
    *,
    preserve_order: bool = False,
) -> list[list[dict[str, Any]]]:
    if page_chars < 1:
        raise GovernanceError("source page budget must be positive")
    ordered = list(rows) if preserve_order else sorted(
        rows, key=lambda row: (row["source_id"], row["ordinal"], row["retrieval_locator"])
    )
    pages: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    used = 0
    current_sources: set[str] = set()
    for row in ordered:
        size = len(row["text"])
        if size > page_chars:
            raise GovernanceError(f"single clause exceeds source page budget: {row['retrieval_locator']}")
        new_source = row["source_id"] not in current_sources
        source_overflow = (
            source_limit is not None
            and new_source
            and len(current_sources) >= source_limit
        )
        if current and (used + size > page_chars or source_overflow):
            pages.append(current)
            current = []
            used = 0
            current_sources = set()
        current.append(row)
        used += size
        current_sources.add(row["source_id"])
    if current:
        pages.append(current)
    flattened = [row["retrieval_locator"] for page in pages for row in page]
    expected = [row["retrieval_locator"] for row in ordered]
    if flattened != expected or len(flattened) != len(set(flattened)):
        raise GovernanceError("ordered source pagination is not lossless")
    return pages


def choose_fallback_source(
    rows: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    request: dict[str, Any],
    action: dict[str, Any],
    required: list[str],
) -> str:
    available = sorted({row["source_id"] for row in rows})
    if not available:
        raise GovernanceError("no source is available for fallback")
    controls = set(required)
    citation_counts = {
        source_id: sum(item["source_id"] == source_id for item in citations)
        for source_id in available
    }

    def score(source_id: str) -> tuple[Any, ...]:
        ranks = [
            source_route_rank(control, source_id)
            for control in controls
            if source_id in CONTROL_SOURCE_ROUTES.get(control, ())
        ]
        return (
            0 if ranks else 1,
            min(ranks, default=10**6),
            sum(ranks) if ranks else 10**6,
            -citation_counts[source_id],
            source_id,
        )

    return min(available, key=score)


def apply_section_fallback(
    rows: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    *,
    request: dict[str, Any],
    action: dict[str, Any],
    taxonomy: dict[str, Any],
    lanes: dict[str, dict[str, int]],
    pinned_order: dict[str, int],
    budget_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    anchor_citation = next((item for item in citations if item["source_id"] == "C08"), citations[0])
    anchor = next(row for row in rows if row["retrieval_locator"] == anchor_citation["retrieval_locator"])
    parent = anchor["heading_path"][:-1] or anchor["heading_path"]
    section_rows = [
        row for row in rows
        if row["source_id"] == anchor["source_id"]
        and row["heading_path"][:len(parent)] == parent
    ]
    existing = {item["retrieval_locator"] for item in citations}
    for row in section_rows:
        if row["retrieval_locator"] in existing:
            continue
        citations.append(citation_for(
            row, lanes=lanes, pinned_order=pinned_order,
            priority=priority_for(row, action, taxonomy), reasons=["section_fallback"],
        ))
        existing.add(row["retrieval_locator"])
    budget_report = refresh_budget_usage(
        budget_report,
        citations,
        escalation_delta=1,
        overflow_reason="section-fallback",
    )
    fallback = {
        "kind": "section", "source_id": anchor["source_id"], "heading_path": parent,
        "page": None, "page_count": None, "reason": "explicit-clause-insufficiency",
    }
    return citations, fallback, budget_report


def apply_paged_source(
    rows: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    *,
    request: dict[str, Any],
    action: dict[str, Any],
    taxonomy: dict[str, Any],
    lanes: dict[str, dict[str, int]],
    pinned_order: dict[str, int],
    budget_report: dict[str, Any],
    page: int,
    required: list[str],
    source_id_override: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, list[str]]]:
    if page < 1:
        raise GovernanceError("source page must be at least 1")
    source_id = source_id_override or choose_fallback_source(
        rows, citations, request, action, required
    )
    if source_id not in {row["source_id"] for row in rows}:
        raise GovernanceError(f"fallback source is outside the query boundary: {source_id}")
    source_rows = [row for row in rows if row["source_id"] == source_id]
    by_locator = {row["retrieval_locator"]: row for row in rows}
    existing_citations = {item["retrieval_locator"]: item for item in citations}
    collection: dict[str, dict[str, Any]] = {
        item["retrieval_locator"]: by_locator[item["retrieval_locator"]]
        for item in citations
        if item["retrieval_locator"] in by_locator
    }
    collection.update({row["retrieval_locator"]: row for row in source_rows})
    ordered_collection = sorted(
        collection.values(),
        key=lambda row: (
            0 if row["retrieval_locator"] in pinned_order else 1,
            pinned_order.get(row["retrieval_locator"], 10**9),
            0 if row["source_id"] == source_id else 1,
            row["source_id"],
            row["ordinal"],
            row["retrieval_locator"],
        ),
    )
    pages = paginate_source_rows(
        ordered_collection,
        int(budget_report["requested_chars"]),
        int(budget_report["source_limit"]),
        preserve_order=True,
    )
    if page > len(pages):
        raise GovernanceError(f"source page {page} exceeds page_count {len(pages)}")
    page_citations: list[dict[str, Any]] = []
    for row in pages[page - 1]:
        prior = existing_citations.get(row["retrieval_locator"])
        if prior is not None:
            page_citations.append(prior)
        else:
            page_citations.append(citation_for(
                row, lanes=lanes, pinned_order=pinned_order,
                priority=priority_for(row, action, taxonomy),
                reasons=["paged_source_fallback"],
            ))
    budget_report = refresh_budget_usage(
        budget_report,
        page_citations,
        escalation_delta=2,
        omitted_delta=len(ordered_collection) - len(page_citations),
        overflow_reason="ordered-source-pagination",
    )
    fallback = {
        "kind": "paged-source", "source_id": source_id, "heading_path": [],
        "page": page, "page_count": len(pages), "reason": "complete-source-exceeds-page-budget",
    }
    collection_controls = {
        control for row in ordered_collection for control in row["control_types"]
    }
    collection_coverage = {
        "required": required,
        "present": sorted(set(required) & collection_controls),
        "missing": sorted(set(required) - collection_controls),
    }
    return page_citations, fallback, budget_report, collection_coverage


def expand_for_missing(
    rows: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    missing: list[str],
    *,
    request: dict[str, Any],
    action: dict[str, Any],
    taxonomy: dict[str, Any],
    lanes: dict[str, dict[str, int]],
    pinned_order: dict[str, int],
    budget_report: dict[str, Any],
    required: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], list[str]]:
    if not missing:
        return citations, {
            "kind": "none", "source_id": None, "heading_path": [],
            "page": None, "page_count": None, "reason": None,
        }, budget_report, []
    existing = {item["retrieval_locator"] for item in citations}
    escalations = 0
    fallback: dict[str, Any] | None = None
    for control in list(missing):
        candidates = [row for row in rows if control in row["control_types"]]
        candidates.sort(key=lambda row: row_relevance(row, request, query_terms(request, action)))
        if not candidates:
            continue
        anchor = candidates[0]
        parent = anchor["heading_path"][:-1] or anchor["heading_path"]
        section_rows = [
            row for row in rows
            if row["source_id"] == anchor["source_id"]
            and row["heading_path"][:len(parent)] == parent
            and row["normative_modality"] not in {"none", "informative"}
        ]
        for row in section_rows:
            if row["retrieval_locator"] in existing:
                continue
            citations.append(citation_for(
                row, lanes=lanes, pinned_order=pinned_order,
                priority=priority_for(row, action, taxonomy), reasons=["section_fallback"],
            ))
            existing.add(row["retrieval_locator"])
        escalations += 1
        fallback = {
            "kind": "section", "source_id": anchor["source_id"], "heading_path": parent,
            "page": None, "page_count": None, "reason": "required-control-missing-at-clause-level",
        }
        if control in {item for citation in citations for item in citation["control_types"]}:
            continue
        source_rows = [
            row for row in rows
            if row["source_id"] == anchor["source_id"]
            and row["normative_modality"] not in {"none", "informative"}
        ]
        for row in source_rows:
            if row["retrieval_locator"] in existing:
                continue
            citations.append(citation_for(
                row, lanes=lanes, pinned_order=pinned_order,
                priority=priority_for(row, action, taxonomy), reasons=["source_fallback"],
            ))
            existing.add(row["retrieval_locator"])
        escalations += 1
        fallback = {
            "kind": "source", "source_id": anchor["source_id"], "heading_path": [],
            "page": None, "page_count": None, "reason": "required-control-missing-after-section",
        }
    budget_report = refresh_budget_usage(
        budget_report,
        citations,
        escalation_delta=escalations,
        overflow_reason="coverage-fallback" if escalations else None,
    )
    remaining = coverage_for(citations, required)["missing"]
    if fallback is None:
        fallback = {
            "kind": "none", "source_id": None, "heading_path": [],
            "page": None, "page_count": None, "reason": None,
        }
    return citations, fallback, budget_report, remaining


def policy_blockers(request: dict[str, Any], environment: QueryEnvironment) -> list[str]:
    text = normalize_term(request["query_text"])
    blockers: list[str] = []
    modes = set(request["modes"])
    sensitive = {"authority", "permission", "prohibition", "gate"}
    action = environment.taxonomy["actions"][request["action"]]
    required = set(required_controls(request, action, environment))
    execution_decision_actions = {
        "run_started", "edit_in_scope", "validate_change", "independent_review",
        "human_acceptance", "publish_release", "rollback", "close_task",
    }
    tailoring_blockers = environment.task_contract["tailoring_resolution"].get(
        "blocking_reasons", []
    )
    if request["action"] in execution_decision_actions and tailoring_blockers:
        blockers.append("task-execution-blocked-by-tailoring-resolution")
    if modes == {"semantic"}:
        blockers.append("semantic-only-mode-disabled-in-first-production-version")
        if required & sensitive:
            blockers.append("semantic-result-cannot-support-authority-or-permission")
    if "semantic" in modes and request["action"] == "publish_release":
        blockers.append("remote-semantic-data-egress-authority-missing")
    # Free text cannot carry a machine-verifiable governance decision.  The
    # conflict action therefore fails closed unless it is one of the two narrow
    # non-decision diagnostics defined by the frozen Gold contract: index-ready
    # consistency checks or post-repair snapshot refresh.  Synonym changes cannot
    # turn an unresolved conflict into an executable result.
    if (
        request["action"] == "resolve_conflict"
        and SAFE_CONFLICT_DIAGNOSTIC_RE.fullmatch(text) is None
    ):
        blockers.append("conflict-resolution-requires-structured-governance-decision")
    derivation = required_control_derivation(request, action, environment)
    if derivation["norm_packet_unsupported"]:
        blockers.append(
            "norm-packet-required-control-unsupported:"
            + ",".join(derivation["norm_packet_unsupported"])
        )
    if re.search(r"(证明|prove).{0,12}(有权|授权|authority|permission)", text):
        blockers.append("retrieval-result-is-not-authority-evidence")
    if "硬门槛" in text and ("抵消" in text or "average" in text):
        blockers.append("hard-gate-failure-cannot-be-offset")
    if request["action"] == "independent_review" and (
        "shadow" in text or "发布前" in text or "before publish" in text
    ):
        blockers.append("independent-review-or-shadow-gate-not-established-by-retrieval")
    return blockers


def blocked_result(
    request: dict[str, Any],
    environment: QueryEnvironment,
    digest: str,
    blockers: list[str],
    *,
    citations: list[dict[str, Any]] | None = None,
    coverage: dict[str, list[str]] | None = None,
    budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = environment.budgets["profiles"][request["budget_profile"]]
    result = {
        "schema_version": "6.3-candidate",
        "meta_type": "DerivedView",
        "status": "Blocked",
        "query_digest": digest,
        "index_digest": environment.index_metadata["index_digest"],
        "consistency_report_sha256": environment.index_metadata["consistency_report_sha256"],
        "tailoring_resolution_sha256": environment.tailoring_sha256,
        "normative_sources_sha256": environment.index_metadata["normative_sources_sha256"],
        "coverage": coverage or {"required": [], "present": [], "missing": []},
        "budget": budget or {
            "profile": request["budget_profile"],
            "candidate_limit": int(profile["candidate_limit"]),
            "requested_chars": int(profile["context_chars"]),
            "used_chars": 0,
            "source_limit": int(profile["source_limit"]),
            "sources_used": 0,
            "escalation_limit": int(profile["escalation_limit"]),
            "escalations_used": 0,
            "omitted_count": 0,
            "overflow_reason": "blocked-before-complete-assembly",
        },
        "citations": citations or [],
        "fallback": {
            "kind": "none", "source_id": None, "heading_path": [],
            "page": None, "page_count": None, "reason": None,
        },
        "blocker_reasons": sorted(set(blockers)),
        "event_ref": f"query-event:{digest}:blocked",
    }
    finalize_clause_context_budget(request, result)
    require_valid_json_document(result, RESULT_SCHEMA, "blocked_query_result")
    validate_result_semantics(result, environment)
    return result


def execute_query(
    request: dict[str, Any],
    environment: QueryEnvironment,
    *,
    prevalidated_integrity: bool = False,
    page: int = 1,
) -> dict[str, Any]:
    request = validate_query_request(request, environment)
    digest = query_digest(request, environment, page=page)
    blockers = [] if prevalidated_integrity else integrity_blockers(request, environment)
    if blockers:
        return blocked_result(request, environment, digest, blockers)
    action = environment.taxonomy["actions"][request["action"]]
    required = required_controls(request, action, environment)
    profile = environment.budgets["profiles"].get(request["budget_profile"])
    if not isinstance(profile, dict):
        return blocked_result(request, environment, digest, ["unknown-budget-profile"])
    rows = load_clause_rows(environment.index_path, environment.source_ids)
    if not rows:
        return blocked_result(request, environment, digest, ["tailoring-source-boundary-returned-no-clauses"])
    terms = query_terms(request, action)
    lanes = lane_lookup(
        environment.index_path,
        environment.source_ids,
        terms,
        int(profile["candidate_limit"]),
        request["modes"],
    )
    try:
        planned, pinned_order, direct_required = plan_candidates(
            rows, lanes, request, action, terms, int(profile["candidate_limit"]), required
        )
    except GovernanceError as exc:
        return blocked_result(request, environment, digest, ["pinned-set-invalid:" + str(exc)])
    citations, budget_report, expanded = pack_candidates(
        planned,
        request=request,
        action=action,
        taxonomy=environment.taxonomy,
        lanes=lanes,
        pinned_order=pinned_order,
        direct_required=direct_required,
        budget=profile,
    )
    coverage = coverage_for(citations, required)
    citations, fallback, budget_report, missing = expand_for_missing(
        rows, citations, coverage["missing"],
        request=request, action=action, taxonomy=environment.taxonomy,
        lanes=lanes, pinned_order=pinned_order, budget_report=budget_report,
        required=required,
    )
    folded_query = normalize_term(request["query_text"])
    section_intent = request["budget_profile"] == "source-required" and any(
        term in folded_query for term in ("条款不足", "扩展章节", "section fallback")
    )
    if section_intent and fallback["kind"] == "none":
        citations, fallback, budget_report = apply_section_fallback(
            rows, citations, request=request, action=action, taxonomy=environment.taxonomy,
            lanes=lanes, pinned_order=pinned_order, budget_report=budget_report,
        )
        expanded = True
    paged = request["budget_profile"] == "source-required" and (
        any(term in folded_query for term in ("完整来源", "complete source"))
        and any(term in folded_query for term in ("分页", "硬限制", "page"))
    )
    coverage_source_needs_paging = (
        fallback["kind"] == "source"
        and budget_report["used_chars"] > budget_report["requested_chars"]
    )
    paged_coverage: dict[str, list[str]] | None = None
    if paged or coverage_source_needs_paging:
        citations, fallback, budget_report, paged_coverage = apply_paged_source(
            rows, citations, request=request, action=action, taxonomy=environment.taxonomy,
            lanes=lanes, pinned_order=pinned_order, budget_report=budget_report, page=page,
            required=required,
            source_id_override=(fallback["source_id"] if coverage_source_needs_paging else None),
        )
        expanded = True
    if "semantic" in request["modes"] and set(request["modes"]) != {"semantic"}:
        for citation in citations:
            citation["retrieval_reason"] = sorted(set(citation["retrieval_reason"]) | {
                "semantic_disabled_local_exact_fts_fallback"
            })
    coverage = paged_coverage or coverage_for(citations, required)
    missing = coverage["missing"]
    blockers = policy_blockers(request, environment)
    if budget_report["escalations_used"] > budget_report["escalation_limit"]:
        blockers.append("escalation-budget-exceeded")
    if missing:
        blockers.append("required-control-coverage-missing:" + ",".join(missing))
    if blockers:
        result = blocked_result(
            request, environment, digest, blockers,
            citations=citations, coverage=coverage, budget=budget_report,
        )
    else:
        fallback_expanded = fallback["kind"] != "none"
        status = "Expanded" if expanded or fallback_expanded else "Complete"
        if status == "Expanded" and fallback["kind"] == "none":
            fallback = {
                "kind": "section",
                "source_id": citations[0]["source_id"] if citations else environment.source_ids[0],
                "heading_path": citations[0]["heading_path"][:-1] or citations[0]["heading_path"] if citations else ["budget"],
                "page": None,
                "page_count": None,
                "reason": "P0/P1-soft-budget-expanded",
            }
        result = {
            "schema_version": "6.3-candidate",
            "meta_type": "DerivedView",
            "status": status,
            "query_digest": digest,
            "index_digest": environment.index_metadata["index_digest"],
            "consistency_report_sha256": environment.index_metadata["consistency_report_sha256"],
            "tailoring_resolution_sha256": environment.tailoring_sha256,
            "normative_sources_sha256": environment.index_metadata["normative_sources_sha256"],
            "coverage": coverage,
            "budget": budget_report,
            "citations": citations,
            "fallback": fallback,
            "blocker_reasons": [],
            "event_ref": f"query-event:{digest}:expanded" if status == "Expanded" else None,
        }
        finalize_clause_context_budget(request, result)
        require_valid_json_document(result, RESULT_SCHEMA, "query_result")
        validate_result_semantics(result, environment)
    return result


def indexed_clause_records(
    environment: QueryEnvironment, locators: Iterable[str]
) -> dict[str, dict[str, Any]]:
    requested = sorted(set(locators))
    if not requested:
        return {}
    placeholders = ",".join("?" for _ in requested)
    uri = f"{environment.index_path.resolve().as_uri()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    progress_handler, _ = _bounded_progress_handler()
    connection.set_progress_handler(progress_handler, SQLITE_PROGRESS_GRANULARITY)
    try:
        records: dict[str, dict[str, Any]] = {}
        for raw in connection.execute(
            f"SELECT * FROM clauses WHERE retrieval_locator IN ({placeholders})",
            requested,
        ):
            record = dict(raw)
            for key in (
                "heading_path_json", "control_types_json", "stage_tags_json", "action_tags_json"
            ):
                record[key.removesuffix("_json")] = json.loads(record.pop(key))
            records[record["retrieval_locator"]] = record
        return records
    except sqlite3.OperationalError as exc:
        if "interrupted" in str(exc).casefold():
            raise GovernanceError("citation recovery exceeded deterministic SQLite step limit") from exc
        raise
    finally:
        connection.close()


def validate_result_semantics(result: dict[str, Any], environment: QueryEnvironment) -> None:
    source_boundary = set(environment.source_ids)
    if not source_boundary:
        raise GovernanceError("query result source boundary is empty")
    required = set(result["coverage"]["required"])
    present = set(result["coverage"]["present"])
    missing = set(result["coverage"]["missing"])
    if present & missing or present | missing != required:
        raise GovernanceError("query result coverage partition is invalid")
    if result["status"] == "Complete" and missing:
        raise GovernanceError("Complete query result cannot have missing controls")
    budget = result["budget"]
    soft_overflow = (
        budget["used_chars"] > budget["requested_chars"]
        or budget["sources_used"] > budget["source_limit"]
    )
    if result["status"] == "Complete" and soft_overflow:
        raise GovernanceError("Complete query result exceeds requested soft budget")
    if soft_overflow and not budget["overflow_reason"]:
        raise GovernanceError("query result exceeds requested soft budget without overflow reason")
    if budget["escalations_used"] > budget["escalation_limit"]:
        raise GovernanceError("query result exceeds escalation budget")
    locators = [citation["retrieval_locator"] for citation in result["citations"]]
    if len(locators) != len(set(locators)):
        raise GovernanceError("query result contains duplicate citation locators")
    records = indexed_clause_records(environment, locators)
    source_documents, _ = load_sources()
    sources = {source.source_id: source for source in source_documents}
    for citation in result["citations"]:
        if citation["line_end"] < citation["line_start"]:
            raise GovernanceError("citation line range is invalid")
        if sha256_bytes(citation["text"].encode("utf-8")) != citation["chunk_sha256"]:
            raise GovernanceError("citation text hash is invalid")
        if citation["source_id"] not in source_boundary:
            raise GovernanceError("citation source boundary is invalid")
        record = records.get(citation["retrieval_locator"])
        if record is None:
            raise GovernanceError("citation locator does not exist in the validated index")
        expected_fields = {
            "source_id": record["source_id"],
            "source_version": record["source_version"],
            "logical_path": record["logical_path"],
            "source_sha256": record["source_sha256"],
            "heading_path": record["heading_path"],
            "line_start": record["line_start"],
            "line_end": record["line_end"],
            "chunk_sha256": record["chunk_sha256"],
            "text": record["text"],
            "control_types": sorted(set(record["control_types"])) or ["background"],
        }
        for field, expected in expected_fields.items():
            if citation[field] != expected:
                raise GovernanceError(
                    f"citation {field} does not match validated index record: "
                    f"{citation['retrieval_locator']}"
                )
        source = sources.get(citation["source_id"])
        if source is None or source.logical_path != citation["logical_path"]:
            raise GovernanceError("citation source cannot be resolved through the runtime Manifest")
        if reconstruct_clause(record, source) != citation["text"]:
            raise GovernanceError("citation cannot be reconstructed from source lines")
    fallback = result["fallback"]
    if fallback["source_id"] is not None and fallback["source_id"] not in source_boundary:
        raise GovernanceError("fallback source boundary is invalid")
    if fallback["kind"] == "paged-source" and fallback["page"] > fallback["page_count"]:
        raise GovernanceError("fallback page exceeds page_count")


def render_clause_context(request: dict[str, Any], result: dict[str, Any]) -> str:
    lines = [
        f"# Clause Context: {request['task_id']} / {request['action']}",
        "",
        f"- Status: `{result['status']}`",
        f"- Query digest: `{result['query_digest']}`",
        f"- Index digest: `{result['index_digest']}`",
        f"- Coverage: `{len(result['coverage']['present'])}/{len(result['coverage']['required'])}`",
        f"- Budget: `{result['budget']['used_chars']}/{result['budget']['requested_chars']}` chars",
        f"- Fallback: `{result['fallback']['kind']}`",
        "",
    ]
    if result["blocker_reasons"]:
        lines.extend(["## Blockers", ""])
        lines.extend(f"- `{item}`" for item in result["blocker_reasons"])
        lines.append("")
    source_index: dict[str, dict[str, Any]] = {}
    for citation in result["citations"]:
        source_index.setdefault(citation["source_id"], citation)
    if source_index:
        lines.extend(["## Source Index", ""])
        for source_id, citation in source_index.items():
            lines.append(
                f"- `{source_id}`: `{citation['logical_path']}` / `{citation['source_version']}` / "
                f"SHA-256 `{citation['source_sha256']}`"
            )
        lines.extend([
            "",
            "> 完整 lane rank 和逐条来源字段保存在同目录 `query-result.json`。",
            "",
        ])
    lines.extend(["## Citations", ""])
    for index, citation in enumerate(result["citations"], start=1):
        heading = " > ".join(citation["heading_path"])
        lines.extend([
            f"### {index}. {citation['source_id']} — {heading}",
            "",
            f"- `{citation['priority']}` · Locator `{citation['retrieval_locator']}` · "
            f"Lines `{citation['line_start']}-{citation['line_end']}`",
            "",
            "```text",
            citation["text"],
            "```",
            "",
        ])
    lines.extend([
        "> 此文件是 DerivedView。检索定位符不是规范正文的正式 Clause ID，召回命中不构成授权、批准或 Gate Outcome。",
        "",
    ])
    return "\n".join(lines)


def synchronize_clause_context_chars(
    request: dict[str, Any], result: dict[str, Any]
) -> int:
    """Bind used_chars to the exact Unicode character count returned to the Agent."""
    for _ in range(8):
        actual = len(render_clause_context(request, result))
        if result["budget"]["used_chars"] == actual:
            return actual
        result["budget"]["used_chars"] = actual
    raise GovernanceError("Clause Context character accounting did not converge")


def finalize_clause_context_budget(
    request: dict[str, Any], result: dict[str, Any]
) -> None:
    """Apply the soft budget to the complete rendered Clause Context, not text only."""
    budget = result["budget"]
    requested = int(budget["requested_chars"])
    if requested < 1:
        raise GovernanceError("Clause Context requested character budget must be positive")

    if result["status"] != "Blocked" and result["fallback"]["kind"] == "none":
        while synchronize_clause_context_chars(request, result) > requested:
            removable_index = None
            candidate_coverage = result["coverage"]
            for index in range(len(result["citations"]) - 1, -1, -1):
                if result["citations"][index]["priority"] not in {"P2", "P3"}:
                    continue
                trial = result["citations"][:index] + result["citations"][index + 1:]
                trial_coverage = coverage_for(trial, result["coverage"]["required"])
                if not trial_coverage["missing"]:
                    removable_index = index
                    candidate_coverage = trial_coverage
                    break
            if removable_index is None:
                break
            result["citations"].pop(removable_index)
            result["coverage"] = candidate_coverage
            budget["omitted_count"] = int(budget["omitted_count"]) + 1
            budget["sources_used"] = len(
                {item["source_id"] for item in result["citations"]}
            )

    actual = synchronize_clause_context_chars(request, result)
    if actual > requested:
        reasons = {
            item
            for item in str(budget.get("overflow_reason") or "").split(",")
            if item
        }
        reasons.add("clause-context-soft-limit")
        budget["overflow_reason"] = ",".join(sorted(reasons))
        if result["status"] == "Complete":
            result["status"] = "Expanded"
            result["event_ref"] = f"query-event:{result['query_digest']}:expanded"
            first = result["citations"][0] if result["citations"] else None
            result["fallback"] = {
                "kind": "section",
                "source_id": first["source_id"] if first else None,
                "heading_path": (
                    first["heading_path"][:-1] or first["heading_path"]
                    if first else []
                ),
                "page": None,
                "page_count": None,
                "reason": "Clause-Context-soft-budget-expanded",
            }
    synchronize_clause_context_chars(request, result)


def write_query_outputs(
    environment: QueryEnvironment,
    request_path: Path,
    request: dict[str, Any],
    result: dict[str, Any],
    output_dir: Path | None,
    _lock_held: bool = False,
    _verify_only: bool = False,
) -> list[Path]:
    base = environment.project_root / ".project-governance" / "generated" / "queries" / request["task_id"]
    incoming_request_path = request_path.resolve()
    default_target = base / result["query_digest"]
    if result["fallback"]["kind"] == "paged-source":
        default_target = default_target / f"page-{result['fallback']['page']:04d}"
    target = output_dir.resolve() if output_dir else default_target
    try:
        target.relative_to(base.resolve())
    except ValueError as exc:
        raise GovernanceError(f"query output must remain under {base}") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    if not _lock_held:
        lock_path = publication_lock_path(target)
        with publication_lock(lock_path):
            write_query_outputs(
                environment,
                request_path,
                request,
                result,
                target,
                _lock_held=True,
            )
        return write_query_outputs(
            environment,
            request_path,
            request,
            result,
            target,
            _lock_held=True,
            _verify_only=True,
        )
    normalized_on_disk = validate_query_request(
        read_json(incoming_request_path), environment
    )
    if normalized_on_disk != request:
        raise GovernanceError("query request changed between validation and publication")
    request_registry = base / "requests"
    request_registry.mkdir(parents=True, exist_ok=True)
    registered_request_path = request_registry / f"{result['query_digest']}.json"
    if registered_request_path.exists():
        if not registered_request_path.is_file():
            raise GovernanceError("registered query request is not a file")
        if validate_query_request(
            read_json(registered_request_path), environment
        ) != request:
            raise GovernanceError("immutable query request registry collision")
    else:
        atomic_write_json(registered_request_path, request)
    request_path = registered_request_path
    json_path = target / "query-result.json"
    markdown_path = target / "clause-context.md"
    runtime_documents, _ = load_sources()
    sources = [
        request_path.resolve(), environment.index_metadata_path,
        environment.consistency_report_path, environment.budget_baseline_path,
        environment.taxonomy_path, environment.norm_packet_json_path,
        environment.norm_packet_markdown_path, environment.index_path,
        embedded_manifest_path().resolve(),
        *(document.physical_path.resolve() for document in runtime_documents),
        Path(__file__).resolve(),
    ]
    json_content = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    markdown_content = render_clause_context(request, result)
    if len(markdown_content) != result["budget"]["used_chars"]:
        raise GovernanceError("Clause Context used_chars does not match rendered output")
    expected_names = (
        "query-result.json", "query-result.json.view.json",
        "clause-context.md", "clause-context.md.view.json",
    )
    page_suffix = (
        f"-P{result['fallback']['page']:04d}"
        if result["fallback"]["kind"] == "paged-source" else ""
    )
    governance_dir = environment.project_root / ".project-governance"

    def source_refs(source_paths: Iterable[Path]) -> list[str]:
        refs: list[str] = []
        for source_path in source_paths:
            resolved = source_path.resolve()
            try:
                refs.append(resolved.relative_to(environment.project_root).as_posix())
            except ValueError:
                refs.append(str(resolved))
        return refs

    def source_snapshot(source_paths: Iterable[Path], generated_at: str) -> str:
        digest = hashlib.sha256()
        digest.update(b"LFEN-QUERY-DERIVED-VIEW-SNAPSHOT-V1\x00")
        digest.update(generated_at.encode("utf-8"))
        digest.update(b"\x00")
        for source_path in source_paths:
            digest.update(source_path.resolve().read_bytes())
        return digest.hexdigest()

    def validate_generated_at(value: Any) -> str:
        if not isinstance(value, str):
            raise GovernanceError("query output envelope generated_at is missing")
        created_value = environment.task_contract.get("created_at")
        frozen_value = environment.task_contract.get("frozen_at")
        try:
            generated = datetime.fromisoformat(value.replace("Z", "+00:00"))
            created = datetime.fromisoformat(str(created_value).replace("Z", "+00:00"))
            frozen = (
                datetime.fromisoformat(str(frozen_value).replace("Z", "+00:00"))
                if frozen_value is not None
                else None
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GovernanceError("query output envelope generated_at is invalid") from exc
        if generated.tzinfo is None or created.tzinfo is None or (
            frozen is not None and frozen.tzinfo is None
        ):
            raise GovernanceError("query output envelope generated_at must include a timezone")
        if generated < created:
            raise GovernanceError("query output envelope predates TaskContract creation")
        if frozen is not None and generated < frozen:
            if request.get("action") != "run_started":
                raise GovernanceError("query output envelope predates TaskContract freeze")
            ledger_path = environment.task_dir / "run.jsonl"
            try:
                run_started_events = []
                for line in ledger_path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if event.get("event_type") == "run_started":
                        run_started_events.append(event)
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise GovernanceError(
                    "pre-freeze run_started query cannot bind the RunLedger event"
                ) from exc
            if len(run_started_events) != 1:
                raise GovernanceError(
                    "pre-freeze run_started query requires exactly one RunLedger start event"
                )
            event_value = run_started_events[0].get("timestamp")
            try:
                event_time = datetime.fromisoformat(str(event_value).replace("Z", "+00:00"))
            except (TypeError, ValueError) as exc:
                raise GovernanceError("RunLedger start event timestamp is invalid") from exc
            if event_time.tzinfo is None or event_time != frozen:
                raise GovernanceError(
                    "pre-freeze run_started query is not bound to TaskContract frozen_at"
                )
        if generated > datetime.now(timezone.utc) + timedelta(minutes=1):
            raise GovernanceError("query output envelope generated_at is in the future")
        return value

    def validate_envelope(
        envelope_path: Path,
        *,
        content_path: Path,
        view_id: str,
        view_kind: str,
        source_paths: list[Path],
        expected_source_refs: list[str] | None = None,
        expected_generated_at: str | None = None,
    ) -> dict[str, Any]:
        envelope = read_json(envelope_path)
        require_valid_json_document(envelope, "derived-view.schema.json", str(envelope_path))
        generated_at = validate_generated_at(envelope.get("generated_at"))
        if expected_generated_at is not None and generated_at != expected_generated_at:
            raise GovernanceError("immutable query output envelope mismatch: generated_at")
        expected = {
            "project_id": environment.task_contract["project_id"],
            "view_id": view_id,
            "view_kind": view_kind,
            "legacy_kind": None,
            "generator": "run-governed-product-workflow/scripts/governance_artifacts.py",
            "source_snapshot": source_snapshot(source_paths, generated_at),
            "sources": expected_source_refs or source_refs(source_paths),
            "content_ref": content_path.resolve().relative_to(
                governance_dir.parent
            ).as_posix(),
            "integrity_status": "Complete",
        }
        mismatches = [key for key, value in expected.items() if envelope.get(key) != value]
        if mismatches:
            raise GovernanceError(
                "immutable query output envelope mismatch: " + ",".join(mismatches)
            )
        return envelope

    def existing_outputs() -> list[Path] | None:
        if not target.exists():
            return None
        if not target.is_dir():
            raise GovernanceError(f"query output target is not a directory: {target}")
        files = [target / name for name in expected_names]
        actual_names = {path.name for path in target.iterdir()}
        if actual_names != set(expected_names):
            raise GovernanceError(f"query output target has unexpected entries: {target}")
        if not all(path.is_file() for path in files):
            raise GovernanceError(f"query output target is a partial publication: {target}")
        if files[0].read_text(encoding="utf-8") != json_content:
            raise GovernanceError("immutable query output collision for query-result.json")
        if files[2].read_text(encoding="utf-8") != markdown_content:
            raise GovernanceError("immutable query output collision for clause-context.md")
        query_envelope = validate_envelope(
            files[1],
            content_path=files[0],
            view_id=f"DV-{request['task_id']}-QUERY-{result['query_digest'][:16]}{page_suffix}",
            view_kind="norm-query-result",
            source_paths=sources,
        )
        validate_envelope(
            files[3],
            content_path=files[2],
            view_id=f"DV-{request['task_id']}-CLAUSE-CONTEXT-{result['query_digest'][:16]}{page_suffix}",
            view_kind="clause-context",
            source_paths=[files[0]],
            expected_generated_at=query_envelope["generated_at"],
        )
        blockers = integrity_blockers(request, environment)
        if blockers:
            raise GovernanceError(
                "immutable query output inputs are stale: " + "; ".join(blockers)
            )
        return files

    published = existing_outputs()
    if published is not None:
        return published
    if _verify_only:
        raise GovernanceError("query publication disappeared after lock release")

    source_hashes = {path.resolve(): sha256_file(path.resolve()) for path in sources}
    envelope_generated_at = now_utc()
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent))
    staging_json = staging / "query-result.json"
    staging_markdown = staging / "clause-context.md"
    try:
        _write_derived_view(
            root=governance_dir,
            content_path=staging_json,
            content=json_content,
            project_id=environment.task_contract["project_id"],
            view_id=f"DV-{request['task_id']}-QUERY-{result['query_digest'][:16]}{page_suffix}",
            view_kind="norm-query-result",
            sources=sources,
        )
        _write_derived_view(
            root=governance_dir,
            content_path=staging_markdown,
            content=markdown_content,
            project_id=environment.task_contract["project_id"],
            view_id=f"DV-{request['task_id']}-CLAUSE-CONTEXT-{result['query_digest'][:16]}{page_suffix}",
            view_kind="clause-context",
            sources=[staging_json],
        )
        governance_root = governance_dir
        final_refs = {
            staging_json.resolve(): json_path.resolve(),
            staging_markdown.resolve(): markdown_path.resolve(),
        }
        staging_json_ref = staging_json.relative_to(environment.project_root).as_posix()
        final_json_ref = json_path.relative_to(environment.project_root).as_posix()
        for envelope_path in (
            staging_json.with_suffix(staging_json.suffix + ".view.json"),
            staging_markdown.with_suffix(staging_markdown.suffix + ".view.json"),
        ):
            envelope = read_json(envelope_path)
            content_path = final_refs[
                staging_json.resolve() if envelope_path.name.startswith("query-result")
                else staging_markdown.resolve()
            ]
            envelope["content_ref"] = content_path.relative_to(governance_root.parent).as_posix()
            envelope["sources"] = [
                final_json_ref if item == staging_json_ref else item
                for item in envelope["sources"]
            ]
            envelope["generated_at"] = envelope_generated_at
            snapshot_sources = (
                sources
                if envelope_path.name.startswith("query-result")
                else [staging_json]
            )
            envelope["source_snapshot"] = source_snapshot(
                snapshot_sources, envelope_generated_at
            )
            atomic_write_json(envelope_path, envelope)
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("query input changed during output assembly")
        if validate_query_request(read_json(incoming_request_path), environment) != request:
            raise GovernanceError("query request changed during output assembly")
        blockers = integrity_blockers(request, environment)
        if blockers:
            raise GovernanceError("query inputs became stale before publication: " + "; ".join(blockers))
        validate_envelope(
            staging_json.with_suffix(staging_json.suffix + ".view.json"),
            content_path=json_path,
            view_id=f"DV-{request['task_id']}-QUERY-{result['query_digest'][:16]}{page_suffix}",
            view_kind="norm-query-result",
            source_paths=sources,
            expected_generated_at=envelope_generated_at,
        )
        validate_envelope(
            staging_markdown.with_suffix(staging_markdown.suffix + ".view.json"),
            content_path=markdown_path,
            view_id=f"DV-{request['task_id']}-CLAUSE-CONTEXT-{result['query_digest'][:16]}{page_suffix}",
            view_kind="clause-context",
            source_paths=[staging_json],
            expected_source_refs=[final_json_ref],
            expected_generated_at=envelope_generated_at,
        )
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("query input changed during final envelope validation")
        if validate_query_request(read_json(incoming_request_path), environment) != request:
            raise GovernanceError("query request changed during final envelope validation")
        try:
            os.replace(staging, target)
        except OSError:
            move_committed = not staging.exists() and target.exists()
            try:
                published = existing_outputs()
                if published is None:
                    raise
                return published
            except BaseException:
                if move_committed and target.exists():
                    try:
                        target.resolve().relative_to(base.resolve())
                    except ValueError as exc:
                        raise GovernanceError(
                            "query rollback target escaped task query root"
                        ) from exc
                    shutil.rmtree(target)
                raise
        try:
            published = existing_outputs()
            if published is None:
                raise GovernanceError("query publication disappeared after atomic replacement")
            return published
        except BaseException:
            try:
                target.resolve().relative_to(base.resolve())
            except ValueError as exc:
                raise GovernanceError("query rollback target escaped task query root") from exc
            if target.exists():
                shutil.rmtree(target)
            raise
    finally:
        if staging.exists():
            try:
                staging.relative_to(target.parent)
            except ValueError as exc:
                raise GovernanceError("query staging directory escaped target parent") from exc
            shutil.rmtree(staging)


def run_query_planner_fixtures() -> dict[str, Any]:
    sample = {
        "schema_version": "6.3-candidate", "task_id": "T-X", "stage": "S4",
        "action": "run_started", "query_text": " e\u0301 权限 ",
        "tailoring_resolution_sha256": "1" * 64, "normative_sources_sha256": "2" * 64,
        "budget_profile": "compact", "modes": ["fts", "exact"],
        "requested_additional_control_types": ["gate", "authority"],
    }
    normalized = normalized_request(sample)
    if normalized["query_text"] != "é 权限":
        raise GovernanceError("query NFC normalization fixture failed")
    if normalized["modes"] != ["exact", "fts"]:
        raise GovernanceError("query logical mode ordering fixture failed")
    if normalized["requested_additional_control_types"] != ["authority", "gate"]:
        raise GovernanceError("query control set ordering fixture failed")
    lexical_cases = {
        "审计数据库 Schema": False,
        "review database schema": False,
        "check metadata ownership": False,
        "检查数据质量": True,
        "validate data pipeline": True,
        "review dataset export": True,
    }
    for query_text, expects_data in lexical_cases.items():
        controls = inferred_controls({"query_text": query_text})
        if ("data" in controls) is not expects_data:
            raise GovernanceError(
                f"data intent lexical-boundary fixture failed: {query_text!r}"
            )
    fixture_result = {
        "status": "Complete",
        "query_digest": "0" * 64,
        "index_digest": "1" * 64,
        "coverage": {"required": [], "present": [], "missing": []},
        "budget": {
            "requested_chars": 12000,
            "used_chars": 0,
            "omitted_count": 0,
            "sources_used": 0,
            "overflow_reason": None,
        },
        "citations": [],
        "fallback": {"kind": "none"},
        "blocker_reasons": [],
        "event_ref": None,
    }
    finalize_clause_context_budget(sample, fixture_result)
    if fixture_result["budget"]["used_chars"] != len(
        render_clause_context(sample, fixture_result)
    ):
        raise GovernanceError("budget character accounting fixture failed")
    return {
        "status": "Passed",
        "normalization": True,
        "logical_set_ordering": True,
        "budget_accounting": True,
        "lexical_boundary_cases": len(lexical_cases),
        "semantic_default": "disabled",
    }


def validate_query_output_directory(task_dir: Path, result_path: Path) -> None:
    """Recompute and verify one immutable active-task query publication."""

    environment = load_environment(task_dir.resolve())
    result_path = result_path.resolve()
    base = (
        environment.project_root
        / ".project-governance"
        / "generated"
        / "queries"
        / str(environment.task_contract["task_id"])
    ).resolve()
    try:
        result_path.relative_to(base)
    except ValueError as exc:
        raise GovernanceError(f"query result escapes the task query root: {result_path}") from exc
    if result_path.name != "query-result.json":
        raise GovernanceError(f"expected query-result.json, received {result_path}")
    envelope = read_json(result_path.with_suffix(result_path.suffix + ".view.json"))
    require_valid_json_document(envelope, "derived-view.schema.json", str(result_path))
    sources = envelope.get("sources")
    if not isinstance(sources, list) or not sources or not isinstance(sources[0], str):
        raise GovernanceError("query result envelope has no request source")
    request_path = Path(sources[0])
    if not request_path.is_absolute():
        request_path = environment.project_root / request_path
    request_path = request_path.resolve()
    try:
        request_path.relative_to(environment.project_root)
    except ValueError as exc:
        raise GovernanceError("active query request must remain inside the project root") from exc
    if not request_path.is_file():
        raise GovernanceError(f"active query request is missing: {request_path}")
    if request_path.stat().st_size > MAX_REQUEST_BYTES:
        raise GovernanceError(f"query request file exceeds {MAX_REQUEST_BYTES} bytes")
    request = validate_query_request(read_json(request_path), environment)
    stored = read_json(result_path)
    fallback = stored.get("fallback", {})
    page = (
        fallback.get("page")
        if isinstance(fallback, dict) and fallback.get("kind") == "paged-source"
        else 1
    )
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise GovernanceError("query result fallback page is invalid")
    expected = execute_query(request, environment, page=page)
    if canonical_tree(stored) != canonical_tree(expected):
        # A publication made before run_started freezes the contract is an
        # immutable historical view.  The current environment necessarily has
        # a different frozen_at and therefore a different query digest.  Replay
        # it against the pre-freeze contract while still checking every source
        # and byte-level envelope; any other drift remains a hard failure.
        generated_at = envelope.get("generated_at")
        frozen_at = environment.task_contract.get("frozen_at")
        try:
            generated_time = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
            frozen_time = datetime.fromisoformat(str(frozen_at).replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise GovernanceError(
                "active query result does not reproduce from its request and current inputs"
            ) from exc
        if (
            frozen_time.tzinfo is None
            or generated_time.tzinfo is None
            or generated_time >= frozen_time
        ):
            raise GovernanceError("active query result does not reproduce from its request and current inputs")
        historical_contract = dict(environment.task_contract)
        historical_contract["frozen_at"] = None
        historical_environment = replace(environment, task_contract=historical_contract)
        historical_request = request
        historical_expected = execute_query(historical_request, historical_environment, page=page)
        if canonical_tree(stored) != canonical_tree(historical_expected):
            raise GovernanceError("active query result does not reproduce from its request and historical inputs")
        write_query_outputs(
            historical_environment,
            request_path,
            historical_request,
            historical_expected,
            result_path.parent,
            _lock_held=True,
            _verify_only=True,
        )
        return
    write_query_outputs(
        environment,
        request_path,
        request,
        expected,
        result_path.parent,
        _lock_held=True,
        _verify_only=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--request-json-file", type=Path, required=True)
    parser.add_argument("--index-metadata", type=Path)
    parser.add_argument("--consistency-report", type=Path)
    parser.add_argument("--budget-baseline", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--validate-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        environment = load_environment(
            args.task_dir,
            index_metadata_path=args.index_metadata,
            consistency_report_path=args.consistency_report,
            budget_baseline_path=args.budget_baseline,
        )
        request_path = args.request_json_file.resolve()
        if request_path.stat().st_size > MAX_REQUEST_BYTES:
            raise GovernanceError(f"query request file exceeds {MAX_REQUEST_BYTES} bytes")
        request = read_json(request_path)
        request = validate_query_request(request, environment)
        blockers = integrity_blockers(request, environment)
        if blockers:
            raise GovernanceError("query inputs are stale or blocked: " + "; ".join(blockers))
        if args.validate_only:
            print(json.dumps({
                "status": "Valid",
                "task_id": request["task_id"],
                "tailoring_resolution_sha256": environment.tailoring_sha256,
            }, ensure_ascii=False, sort_keys=True, indent=2))
            return 0
        result = execute_query(request, environment, page=args.page)
        outputs = write_query_outputs(
            environment, request_path, request, result, args.output_dir
        )
        print(json.dumps({
            "status": result["status"],
            "query_digest": result["query_digest"],
            "coverage": result["coverage"],
            "outputs": [str(path) for path in outputs],
        }, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if result["status"] != "Blocked" else 3
    except (OSError, json.JSONDecodeError, GovernanceError, KeyError, TypeError, ValueError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
