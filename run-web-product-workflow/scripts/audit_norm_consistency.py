#!/usr/bin/env python3
"""Run a deterministic, read-only consistency audit over embedded norms and contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from governance_artifacts import (  # noqa: E402
    GovernanceError,
    _write_derived_view,
    default_mapping_path,
    default_profile_index_path,
    default_tailoring_map_path,
    governance_root,
    load_mapping,
    load_tailoring_map,
    now_utc,
    read_json,
    resolve_all_profiles,
    runtime_asset_path,
    sha256_file,
    validate_embedded_manifest,
    validate_json_document,
    validate_tailoring_map,
)


REPORT_VERSION = "1.0"
SEVERITY_ORDER = {"Blocker": 0, "Major": 1, "Minor": 2, "Observation": 3}
BLOCKING_SEVERITIES = {"Blocker", "Major"}
VERSION_RE = re.compile(r"\bV\d+(?:\.\d+)+\b", flags=re.IGNORECASE)
NEGATIVE_MODAL_RE = re.compile(r"MUST\s+NOT|SHALL\s+NOT|禁止|不得|不应", flags=re.IGNORECASE)
POSITIVE_MODAL_RE = re.compile(r"MUST|SHALL|必须|应当|应", flags=re.IGNORECASE)
MODAL_REMOVE_RE = re.compile(
    r"MUST\s+NOT|SHALL\s+NOT|MUST|SHALL|禁止|不得|不应|必须|应当|应",
    flags=re.IGNORECASE,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return unicodedata.normalize("NFC", text).encode("utf-8")


def strip_markdown(value: str) -> str:
    value = re.sub(r"[`*]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [strip_markdown(cell) for cell in stripped[1:-1].split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_control_table(text: str) -> dict[str, tuple[str, int]]:
    """Parse only the first document-control section, never later status tables."""

    result: dict[str, tuple[str, int]] = {}
    control_active = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^##\s+", line):
            if control_active and result:
                break
            if "文档控制" in line:
                control_active = True
            continue
        if line_no > 120:
            continue
        cells = split_table_row(line)
        if len(cells) < 2 or is_separator_row(cells):
            continue
        key, value = cells[0], cells[1]
        if key in {"文档属性", "属性", "Field", "字段"}:
            control_active = True
            continue
        if not control_active or not key or not value:
            continue
        result.setdefault(key, (value, line_no))
    return result


def control_value(
    controls: dict[str, tuple[str, int]],
    names: Iterable[str],
) -> tuple[str | None, int | None]:
    for name in names:
        if name in controls:
            return controls[name]
    return None, None


def base_version(value: str | None) -> str | None:
    if not value:
        return None
    match = VERSION_RE.search(value)
    return match.group(0).upper() if match else None


def normalized_term(value: str) -> str:
    value = strip_markdown(value).casefold()
    return re.sub(r"[\s\-_/：:（）()\[\]]+", "", value)


def normalized_statement(value: str) -> str:
    value = MODAL_REMOVE_RE.sub("", strip_markdown(value))
    value = re.sub(r"^\s*(?:[-+*]|\d+[.)、])\s*", "", value)
    value = re.sub(r"[\s，,。；;：:、|（）()\[\]{}<>《》\"'`]+", "", value)
    return unicodedata.normalize("NFC", value).casefold()


def extract_definitions(source_id: str, logical_path: str, text: str) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    term_index: int | None = None
    definition_index: int | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        cells = split_table_row(line)
        if not cells:
            term_index = None
            definition_index = None
            continue
        if is_separator_row(cells):
            continue
        if term_index is None:
            term_candidates = [
                index for index, cell in enumerate(cells)
                if cell in {"术语", "概念", "信息类型", "用语", "关系"}
            ]
            definition_candidates = [index for index, cell in enumerate(cells) if cell in {"定义", "含义"}]
            if term_candidates and definition_candidates:
                term_index = term_candidates[0]
                definition_index = definition_candidates[0]
            continue
        if definition_index is None:
            continue
        if max(term_index, definition_index) >= len(cells):
            continue
        term = cells[term_index]
        definition = cells[definition_index]
        if term and definition:
            definitions.append(
                {
                    "source_id": source_id,
                    "logical_path": logical_path,
                    "line": line_no,
                    "term": term,
                    "term_key": normalized_term(term),
                    "definition": definition,
                    "definition_key": normalized_statement(definition),
                }
            )
    return definitions


def extract_unique_source_claims(source_id: str, logical_path: str, text: str) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    subject_index: int | None = None
    source_index: int | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        cells = split_table_row(line)
        if not cells:
            subject_index = None
            source_index = None
            continue
        if is_separator_row(cells):
            continue
        if source_index is None:
            candidates = [index for index, cell in enumerate(cells) if cell == "唯一事实源"]
            if candidates and len(cells) >= 2:
                source_index = candidates[0]
                subject_index = 0 if source_index != 0 else 1
            continue
        if subject_index is None:
            continue
        if max(subject_index, source_index) >= len(cells):
            continue
        subject = cells[subject_index]
        owner = cells[source_index]
        if subject and owner:
            claims.append(
                {
                    "source_id": source_id,
                    "logical_path": logical_path,
                    "line": line_no,
                    "subject": subject,
                    "subject_key": normalized_term(subject),
                    "owner": owner,
                    "owner_key": normalized_statement(owner),
                }
            )
    return claims


def extract_precedence_claims(source_id: str, logical_path: str, text: str) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    pattern = re.compile(r"优先于|冲突时.{0,40}(?:为准|采用|适用)|发生冲突.{0,40}(?:为准|采用|适用)|唯一事实源")
    in_code_block = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not pattern.search(line):
            continue
        claims.append(
            {
                "source_id": source_id,
                "logical_path": logical_path,
                "line": line_no,
                "text": strip_markdown(line),
            }
        )
    return claims


def precedence_cycle_findings(
    claims: list[dict[str, Any]],
    known_ids: set[str],
) -> list[dict[str, Any]]:
    graph: dict[str, set[str]] = defaultdict(set)
    edge_claim: dict[tuple[str, str], dict[str, Any]] = {}
    id_pattern = "|".join(re.escape(item) for item in sorted(known_ids, key=len, reverse=True))
    direct = re.compile(rf"(?P<higher>{id_pattern}).{{0,80}}?优先于.{{0,80}}?(?P<lower>{id_pattern})", re.IGNORECASE)
    defer = re.compile(rf"以\s*(?P<higher>{id_pattern})\s*为准", re.IGNORECASE)
    for claim in claims:
        text = claim["text"]
        for match in direct.finditer(text):
            higher, lower = match.group("higher").upper(), match.group("lower").upper()
            if higher != lower:
                graph[higher].add(lower)
                edge_claim[(higher, lower)] = claim
        for match in defer.finditer(text):
            higher, lower = match.group("higher").upper(), claim["source_id"].upper()
            if higher != lower and lower in known_ids:
                graph[higher].add(lower)
                edge_claim[(higher, lower)] = claim

    findings: list[dict[str, Any]] = []
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for child in sorted(graph.get(node, set())):
            if state.get(child, 0) == 0:
                visit(child)
            elif state.get(child) == 1:
                start = stack.index(child)
                cycle = stack[start:] + [child]
                claim = edge_claim.get((node, child), claims[0] if claims else {})
                findings.append(
                    make_finding(
                        severity="Blocker",
                        category="precedence_cycle",
                        source_id=str(claim.get("source_id", node)),
                        logical_path=str(claim.get("logical_path", "")),
                        line_start=claim.get("line"),
                        message="规范优先级形成循环: " + " -> ".join(cycle),
                        impact="循环 Authority/优先级无法确定冲突条款的有效控制",
                        evidence=str(claim.get("text", "")),
                        related_sources=cycle,
                        requires_human_decision=True,
                        remediation_class="governance-decision",
                    )
                )
        stack.pop()
        state[node] = 2

    for node in sorted(known_ids):
        if state.get(node, 0) == 0:
            visit(node)
    return findings


def extract_normative_statements(source_id: str, logical_path: str, text: str) -> list[dict[str, Any]]:
    statements: list[dict[str, Any]] = []
    in_code_block = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for sentence in re.split(r"(?<=[。；;])", line):
            if not sentence.strip():
                continue
            polarity: str | None = None
            if NEGATIVE_MODAL_RE.search(sentence):
                polarity = "negative"
            elif POSITIVE_MODAL_RE.search(sentence):
                polarity = "positive"
            if polarity is None:
                continue
            key = normalized_statement(sentence)
            if len(key) < 8:
                continue
            statements.append(
                {
                    "source_id": source_id,
                    "logical_path": logical_path,
                    "line": line_no,
                    "polarity": polarity,
                    "statement": strip_markdown(sentence),
                    "key": key,
                }
            )
    return statements


def make_finding(
    *,
    severity: str,
    category: str,
    message: str,
    impact: str | None = None,
    source_id: str,
    logical_path: str,
    line_start: int | None = None,
    line_end: int | None = None,
    evidence: str = "",
    related_sources: Iterable[str] = (),
    requires_human_decision: bool = False,
    remediation_class: str = "implementation-fix",
) -> dict[str, Any]:
    if severity not in SEVERITY_ORDER:
        raise ValueError(f"unknown severity: {severity}")
    return {
        "severity": severity,
        "category": category,
        "source_id": source_id,
        "logical_path": logical_path,
        "line_start": line_start,
        "line_end": line_end if line_end is not None else line_start,
        "message": message,
        "impact": impact or {
            "Blocker": "阻断一致性结论、执行放行和 Norm Index Ready",
            "Major": "在关闭或裁决前阻断 Norm Index Ready",
            "Minor": "不单独阻断 Gate，但降低规范一致性或可审计性",
            "Observation": "不改变当前 Gate，仅作为后续治理输入保留",
        }[severity],
        "evidence": evidence[:1000],
        "related_sources": sorted(set(related_sources)),
        "requires_human_decision": requires_human_decision,
        "remediation_class": remediation_class,
    }


def finalize_findings(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for item in findings:
        key = (
            item["severity"],
            item["category"],
            item["source_id"],
            item["logical_path"],
            item["line_start"],
            item["message"],
        )
        unique[key] = item
    ordered = sorted(
        unique.values(),
        key=lambda item: (
            SEVERITY_ORDER[item["severity"]],
            item["category"],
            item["source_id"],
            item["logical_path"],
            item["line_start"] or 0,
            item["message"],
        ),
    )
    for position, item in enumerate(ordered, start=1):
        item["finding_id"] = f"NCF-{position:04d}"
    return ordered


def dependency_version_findings(
    *,
    source_id: str,
    logical_path: str,
    controls: dict[str, tuple[str, int]],
    versions: dict[str, str],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    identifiers = sorted(versions, key=len, reverse=True)
    if not identifiers:
        return findings
    id_pattern = "|".join(re.escape(item) for item in identifiers)
    pattern = re.compile(
        rf"(?P<id>{id_pattern})\s*(?:[（(]\s*)?(?P<version>V\d+(?:\.\d+)+)",
        flags=re.IGNORECASE,
    )
    range_pattern = re.compile(
        r"(?P<prefix>[CE])(?P<start>\d{2})(?:\s*V\d+(?:\.\d+)+)?"
        r"\s*至\s*(?P=prefix)(?P<end>\d{2})\s*(?P<version>V\d+(?:\.\d+)+)",
        flags=re.IGNORECASE,
    )
    trailing_list_pattern = re.compile(
        r"(?P<ids>(?:(?:C\d{2}|E\d{2})\s*[、,，]\s*)+(?:C\d{2}|E\d{2}))"
        r"\s*(?P<version>V\d+(?:\.\d+)+)",
        flags=re.IGNORECASE,
    )
    for key, (value, line_no) in controls.items():
        if not re.search(r"依赖|上游|下游|Source", key, flags=re.IGNORECASE):
            continue
        declared_versions: dict[str, str] = {}
        for match in range_pattern.finditer(value):
            prefix = match.group("prefix").upper()
            start = int(match.group("start"))
            end = int(match.group("end"))
            declared = match.group("version").upper()
            if start <= end:
                for ordinal in range(start, end + 1):
                    declared_versions[f"{prefix}{ordinal:02d}"] = declared
        for match in trailing_list_pattern.finditer(value):
            declared = match.group("version").upper()
            for referenced_id in re.findall(r"C\d{2}|E\d{2}", match.group("ids"), flags=re.IGNORECASE):
                declared_versions[referenced_id.upper()] = declared
        for match in pattern.finditer(value):
            referenced_id = match.group("id").upper()
            declared = match.group("version").upper()
            declared_versions[referenced_id] = declared
        mismatches = [
            (referenced_id, declared, versions[referenced_id])
            for referenced_id, declared in sorted(declared_versions.items())
            if referenced_id in versions and declared != versions[referenced_id]
        ]
        if mismatches:
            detail = ", ".join(
                f"{referenced_id} {declared}→{current}"
                for referenced_id, declared, current in mismatches
            )
            findings.append(
                make_finding(
                    severity="Major",
                    category="stale_dependency_version",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=line_no,
                    message=f"依赖元数据包含 {len(mismatches)} 个陈旧版本引用: {detail}",
                    impact="依赖版本元数据与当前来源不一致，会污染来源定位、版本过滤和索引溯源",
                    evidence=f"{key}: {value}",
                    related_sources=[item[0] for item in mismatches],
                    remediation_class="norm-change",
                )
            )
    return findings


def normative_sources_digest(source_catalog: list[dict[str, Any]], meta_mapping: Path) -> str:
    digest = hashlib.sha256()
    for source in sorted(source_catalog, key=lambda item: item["id"]):
        path = runtime_asset_path(source["path"])
        digest.update(source["id"].encode("utf-8"))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    digest.update(hashlib.sha256(meta_mapping.read_bytes()).digest())
    return digest.hexdigest()


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# T-011 规范一致性只读审计报告",
        "",
        "## 1. 结论",
        "",
        f"- Audit status: `{report['audit_status']}`",
        f"- Norm Index Ready: `{str(report['norm_index_ready']).lower()}`",
        f"- Next gate: `{report['next_gate']}`",
        f"- Audit digest: `{report['audit_digest']}`",
        f"- Frozen TaskContract snapshot verified: `{str(report['inputs']['task_contract_snapshot_verified']).lower()}`",
        f"- Protected assets unchanged during audit: `{str(report['protected_assets_unchanged']).lower()}`",
        "",
        "本报告是 DerivedView，只记录机器审计事实与冲突候选，不批准 V6.3，不自动裁决同级语义冲突，也不修改规范正文。",
        "",
        "## 2. 覆盖",
        "",
        "| 对象 | 数量 |",
        "|---|---:|",
        f"| 规范源 | {report['scope']['norm_sources']} |",
        f"| 映射 | {report['scope']['mappings']} |",
        f"| Schema | {report['scope']['schemas']} |",
        f"| Evaluation | {report['scope']['evaluations']} |",
        f"| Manifest | {report['scope']['manifest']} |",
        f"| Standards | {report['scope']['standards']} |",
        f"| Profiles | {report['scope']['profiles']} |",
        "",
        "## 3. Finding 摘要",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {summary['by_severity'].get(severity, 0)} |")
    lines.extend(
        [
            "",
            "## 4. Findings",
            "",
            "| ID | Severity | Category | Source | Line | Human decision | Impact | Message |",
            "|---|---|---|---|---:|---|---|---|",
        ]
    )
    if not report["findings"]:
        lines.append("| — | — | — | — | — | — | — | 未发现一致性问题 |")
    for item in report["findings"]:
        message = item["message"].replace("|", "\\|").replace("\n", " ")
        impact = item["impact"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['finding_id']} | {item['severity']} | {item['category']} | "
            f"{item['source_id']} | {item['line_start'] or '—'} | "
            f"{str(item['requires_human_decision']).lower()} | {impact} | {message} |"
        )
    inventory = report["manual_review_inventory"]
    lines.extend(
        [
            "",
            "## 5. 人工复核清单与检测边界",
            "",
            f"- 显式优先级/Authority 声明：{len(inventory['precedence_and_authority_claims'])} 条。",
            f"- 唯一事实源声明：{len(inventory['unique_fact_source_claims'])} 条。",
            "- 上述声明已进入结构化 JSON 清单，供独立复核逐条回源。",
            "",
            *[f"- {item}" for item in report["detector_limits"]],
            "",
            "## 6. Gate 规则",
            "",
            "- 任一 Blocker 或 Major 未关闭时，`Norm Index Ready=false`。",
            "- `governance-decision` Finding 必须由有权人裁决，Agent 不得自行选择同级规范。",
            "- `norm-change` Finding 必须进入 T-012 修正规范并重建运行快照与哈希。",
            "- Minor/Observation 仍需保留，但不单独授权修改规范或构建索引。",
            "",
        ]
    )
    return "\n".join(lines)


def audit(
    project_root: Path,
    project_id: str,
    task_id: str,
    *,
    verify_authority_sources: bool = True,
) -> tuple[dict[str, Any], list[Path]]:
    project_root = project_root.resolve()
    skill_root = Path(__file__).resolve().parent.parent
    manifest_path = skill_root / "assets" / "runtime" / "embedded-manifest.json"
    manifest = read_json(manifest_path)
    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise GovernanceError("embedded manifest files must be an array")

    protected_entries = [
        item for item in files
        if isinstance(item, dict) and item.get("role") in {"norm", "mapping", "schema", "evaluation"}
    ]
    protected_paths = [skill_root / item["embedded"] for item in protected_entries]
    before_hashes = {item["embedded"]: sha256_file(skill_root / item["embedded"]) for item in protected_entries}

    findings: list[dict[str, Any]] = []
    for error in validate_embedded_manifest(skill_root):
        findings.append(
            make_finding(
                severity="Blocker",
                category="manifest_integrity",
                source_id="embedded-manifest",
                logical_path="assets/runtime/embedded-manifest.json",
                message=error,
                evidence=error,
                remediation_class="runtime-sync",
            )
        )

    role_counts = Counter(item.get("role") for item in files if isinstance(item, dict))
    expected_protected_roles = {"norm": 22, "mapping": 3, "schema": 11, "evaluation": 2}
    actual_protected_roles = {
        role: role_counts.get(role, 0) for role in expected_protected_roles
    }
    if actual_protected_roles != expected_protected_roles:
        findings.append(
            make_finding(
                severity="Blocker",
                category="audit_scope_closure",
                source_id="embedded-manifest",
                logical_path="assets/runtime/embedded-manifest.json",
                message=(
                    "受保护审计集合必须按角色闭合为 22 norm + 3 mapping + 11 schema + 2 evaluation，"
                    f"当前为 {json.dumps(actual_protected_roles, ensure_ascii=False, sort_keys=True)}"
                ),
                evidence=json.dumps(role_counts, ensure_ascii=False, sort_keys=True),
                remediation_class="runtime-sync",
            )
        )

    valid_runtime_paths: dict[str, Path] = {}
    for item in protected_entries:
        logical_path = item["logical_path"]
        try:
            runtime_path = runtime_asset_path(logical_path, skill_root=skill_root)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="runtime_asset_integrity",
                    source_id=logical_path,
                    logical_path=logical_path,
                    message=str(exc),
                    evidence=item.get("embedded", ""),
                    remediation_class="runtime-sync",
                )
            )
            continue
        valid_runtime_paths[logical_path] = runtime_path
        source_ref = item.get("source", "")
        if (
            verify_authority_sources
            and item.get("role") in {"norm", "mapping"}
            and not source_ref.startswith("skill-local:")
        ):
            canonical = (project_root / source_ref).resolve()
            try:
                canonical.relative_to(project_root)
            except ValueError:
                canonical = Path()
            if not canonical.is_file():
                findings.append(
                    make_finding(
                        severity="Blocker",
                        category="authority_source_missing",
                        source_id=logical_path,
                        logical_path=logical_path,
                        message=f"权威来源不存在或越出项目根目录: {source_ref}",
                        evidence=source_ref,
                        remediation_class="runtime-sync",
                    )
                )
            elif sha256_file(canonical) != item["sha256"]:
                findings.append(
                    make_finding(
                        severity="Blocker",
                        category="runtime_authority_drift",
                        source_id=logical_path,
                        logical_path=logical_path,
                        message="权威来源与受保护运行快照 SHA-256 不一致",
                        evidence=f"source={source_ref}; embedded={item['embedded']}",
                        remediation_class="runtime-sync",
                    )
                )

    try:
        tailoring = load_tailoring_map(default_tailoring_map_path(), validate_sources=False)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        raise GovernanceError(f"cannot load tailoring map: {exc}") from exc
    for error in validate_tailoring_map(tailoring, skill_root=skill_root):
        findings.append(
            make_finding(
                severity="Blocker",
                category="tailoring_mapping_integrity",
                source_id="VC-PPG-TAIL-001",
                logical_path="mappings/tailoring-applicability-map.json",
                message=error,
                evidence=error,
                remediation_class="mapping-fix",
            )
        )

    try:
        meta_mapping = load_mapping(default_mapping_path())
        profiles = resolve_all_profiles(default_profile_index_path(), default_mapping_path())
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        findings.append(
            make_finding(
                severity="Blocker",
                category="profile_mapping_integrity",
                source_id="VC-PPG-MAP-001",
                logical_path="mappings/profile-meta-map.json",
                message=str(exc),
                evidence=str(exc),
                remediation_class="mapping-fix",
            )
        )
        meta_mapping = {}
        profiles = []
    profile_ids = [item.get("legacy_kind") for item in profiles]
    if len(profiles) != 137 or len(set(profile_ids)) != 137:
        findings.append(
            make_finding(
                severity="Blocker",
                category="profile_closure",
                source_id="VC-PPG-IDX-001",
                logical_path="references/05_记录与登记册/V6.3_跨规范产物归属索引.md",
                message=f"Profile 必须唯一闭合 137 项，当前总数 {len(profiles)}、唯一数 {len(set(profile_ids))}",
                remediation_class="mapping-fix",
            )
        )

    source_catalog = tailoring.get("source_catalog", [])
    catalog_ids = [source.get("id") for source in source_catalog if isinstance(source, dict)]
    catalog_paths = [source.get("path") for source in source_catalog if isinstance(source, dict)]
    norm_logical_paths = [item["logical_path"] for item in protected_entries if item["role"] == "norm"]
    if len(catalog_ids) != 22 or len(set(catalog_ids)) != 22 or set(catalog_paths) != set(norm_logical_paths):
        findings.append(
            make_finding(
                severity="Blocker",
                category="source_catalog_closure",
                source_id="VC-PPG-TAIL-001",
                logical_path="mappings/tailoring-applicability-map.json",
                message="source_catalog 必须以唯一 Source ID 精确覆盖 Manifest 的 22 个 norm 逻辑路径",
                evidence=f"ids={len(catalog_ids)}/{len(set(catalog_ids))}; paths={len(set(catalog_paths))}/{len(set(norm_logical_paths))}",
                remediation_class="mapping-fix",
            )
        )

    source_records: dict[str, dict[str, Any]] = {}
    versions: dict[str, str] = {}
    definitions: list[dict[str, Any]] = []
    statements: list[dict[str, Any]] = []
    unique_source_claims: list[dict[str, Any]] = []
    precedence_claims: list[dict[str, Any]] = []
    for source in source_catalog:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not isinstance(source.get("path"), str):
            continue
        source_id = source["id"]
        logical_path = source["path"]
        path = valid_runtime_paths.get(logical_path)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8")
        controls = parse_control_table(text)
        document_id, id_line = control_value(controls, ["文档编号", "Document ID", "文档ID"])
        version, version_line = control_value(controls, ["版本", "Version"])
        status, status_line = control_value(controls, ["状态", "Status"])
        formal_name, name_line = control_value(controls, ["正式文件名", "Filename"])
        source_records[source_id] = {
            "source_id": source_id,
            "logical_path": logical_path,
            "sha256": sha256_file(path),
            "document_id": document_id,
            "version": version,
            "status": status,
            "controls": controls,
        }
        if document_id != source_id:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="document_identity",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=id_line,
                    message=f"文档控制编号必须为 {source_id}，当前为 {document_id!r}",
                    evidence=document_id or "missing",
                    remediation_class="norm-change",
                )
            )
        current_version = base_version(version)
        if current_version is None:
            findings.append(
                make_finding(
                    severity="Major",
                    category="document_version_missing",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=version_line,
                    message="文档控制信息缺少可解析版本",
                    evidence=version or "missing",
                    remediation_class="norm-change",
                )
            )
        else:
            versions[source_id.upper()] = current_version
        if not status:
            findings.append(
                make_finding(
                    severity="Major",
                    category="document_status_missing",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=status_line,
                    message="文档控制信息缺少状态",
                    remediation_class="norm-change",
                )
            )
        if version and "candidate" in version.casefold() and status and status.casefold() in {"approved", "baselined"}:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="candidate_status_conflict",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=status_line,
                    message=f"Candidate 版本不得同时声明为 {status}",
                    evidence=f"version={version}; status={status}",
                    requires_human_decision=True,
                    remediation_class="governance-decision",
                )
            )
        if formal_name and strip_markdown(formal_name) != path.name:
            findings.append(
                make_finding(
                    severity="Major",
                    category="formal_filename_drift",
                    source_id=source_id,
                    logical_path=logical_path,
                    line_start=name_line,
                    message=f"正式文件名 {strip_markdown(formal_name)!r} 与运行来源文件名 {path.name!r} 不一致",
                    evidence=formal_name,
                    remediation_class="norm-change",
                )
            )
        definitions.extend(extract_definitions(source_id, logical_path, text))
        statements.extend(extract_normative_statements(source_id, logical_path, text))
        unique_source_claims.extend(extract_unique_source_claims(source_id, logical_path, text))
        precedence_claims.extend(extract_precedence_claims(source_id, logical_path, text))

    for source_id, record in source_records.items():
        findings.extend(
            dependency_version_findings(
                source_id=source_id,
                logical_path=record["logical_path"],
                controls=record["controls"],
                versions=versions,
            )
        )

    definition_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for definition in definitions:
        definition_groups[definition["term_key"]].append(definition)
    for group in definition_groups.values():
        source_ids = {item["source_id"] for item in group}
        definition_keys = {item["definition_key"] for item in group}
        if len(source_ids) < 2 or len(definition_keys) < 2:
            continue
        first = sorted(group, key=lambda item: (item["source_id"], item["line"]))[0]
        findings.append(
            make_finding(
                severity="Major",
                category="definition_conflict_candidate",
                source_id=first["source_id"],
                logical_path=first["logical_path"],
                line_start=first["line"],
                message=f"术语 {first['term']!r} 在多个规范源存在不同定义，必须人工判定是否为同一语义域",
                impact="同名术语的语义边界未裁决，可能导致条款召回、Authority选择和冲突消解歧义",
                evidence="; ".join(
                    f"{item['source_id']}:{item['line']}={item['definition']}" for item in group
                ),
                related_sources=source_ids,
                requires_human_decision=True,
                remediation_class="governance-decision",
            )
        )

    unique_source_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in unique_source_claims:
        unique_source_groups[claim["subject_key"]].append(claim)
    for group in unique_source_groups.values():
        source_ids = {item["source_id"] for item in group}
        owner_keys = {item["owner_key"] for item in group}
        if len(source_ids) < 2 or len(owner_keys) < 2:
            continue
        first = sorted(group, key=lambda item: (item["source_id"], item["line"]))[0]
        findings.append(
            make_finding(
                severity="Major",
                category="unique_fact_source_conflict_candidate",
                source_id=first["source_id"],
                logical_path=first["logical_path"],
                line_start=first["line"],
                message=f"信息 {first['subject']!r} 在多个规范源声明了不同的唯一事实源",
                impact="同一事实存在多个权威归属候选，查询层无法安全选择 Authority",
                evidence="; ".join(
                    f"{item['source_id']}:{item['line']}={item['owner']}" for item in group
                ),
                related_sources=source_ids,
                requires_human_decision=True,
                remediation_class="governance-decision",
            )
        )

    findings.extend(precedence_cycle_findings(precedence_claims, {item.upper() for item in catalog_ids if isinstance(item, str)}))

    statement_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for statement in statements:
        statement_groups[statement["key"]].append(statement)
    for group in statement_groups.values():
        polarities = {item["polarity"] for item in group}
        if polarities != {"positive", "negative"}:
            continue
        first = sorted(group, key=lambda item: (item["source_id"], item["line"]))[0]
        findings.append(
            make_finding(
                severity="Blocker",
                category="opposing_normative_clause_candidate",
                source_id=first["source_id"],
                logical_path=first["logical_path"],
                line_start=first["line"],
                message="相同规范对象同时出现允许/要求与禁止模态，必须人工确认适用条件和Authority优先级",
                impact="同一规范对象存在相反模态候选，无法安全形成执行结论",
                evidence="; ".join(
                    f"{item['source_id']}:{item['line']}[{item['polarity']}]={item['statement']}" for item in group
                ),
                related_sources={item["source_id"] for item in group},
                requires_human_decision=True,
                remediation_class="governance-decision",
            )
        )

    schema_ids: dict[str, str] = {}
    for item in protected_entries:
        if item["role"] != "schema":
            continue
        logical_path = item["logical_path"]
        path = valid_runtime_paths.get(logical_path)
        if path is None:
            continue
        try:
            schema = read_json(path)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="schema_parse",
                    source_id=logical_path,
                    logical_path=logical_path,
                    message=str(exc),
                    evidence=str(exc),
                    remediation_class="schema-fix",
                )
            )
            continue
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="schema_identity",
                    source_id=logical_path,
                    logical_path=logical_path,
                    message="Schema 缺少非空 $id",
                    remediation_class="schema-fix",
                )
            )
        elif schema_id in schema_ids:
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="schema_identity",
                    source_id=logical_path,
                    logical_path=logical_path,
                    message=f"Schema $id 与 {schema_ids[schema_id]} 重复: {schema_id}",
                    related_sources=[schema_ids[schema_id]],
                    remediation_class="schema-fix",
                )
            )
        else:
            schema_ids[schema_id] = logical_path

    current_normative_digest = normative_sources_digest(source_catalog, default_mapping_path())
    current_rule_set_sha256 = sha256_file(default_tailoring_map_path())
    task_contract_snapshot_verified = True
    task_before_path = governance_root(project_root) / "tasks" / task_id / "before.json"
    try:
        task_before = read_json(task_before_path)
        task_resolution = task_before.get("tailoring_resolution", {})
        expected_normative_digest = task_resolution.get("normative_sources_sha256")
        expected_rule_set_sha256 = task_resolution.get("rule_set_sha256")
        if expected_normative_digest != current_normative_digest:
            task_contract_snapshot_verified = False
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="task_contract_snapshot_drift",
                    source_id=task_id,
                    logical_path=f".project-governance/tasks/{task_id}/before.json",
                    message="当前规范来源集合摘要与冻结 TaskContract 不一致",
                    impact="无法证明审计输入属于任务冻结时接受的规范来源集合",
                    evidence=f"expected={expected_normative_digest}; actual={current_normative_digest}",
                    remediation_class="refresh-or-stop",
                )
            )
        if expected_rule_set_sha256 != current_rule_set_sha256:
            task_contract_snapshot_verified = False
            findings.append(
                make_finding(
                    severity="Blocker",
                    category="task_contract_snapshot_drift",
                    source_id=task_id,
                    logical_path=f".project-governance/tasks/{task_id}/before.json",
                    message="当前裁剪规则摘要与冻结 TaskContract 不一致",
                    impact="无法证明审计使用任务冻结时的适用性和来源路由规则",
                    evidence=f"expected={expected_rule_set_sha256}; actual={current_rule_set_sha256}",
                    remediation_class="refresh-or-stop",
                )
            )
        for source in task_resolution.get("complete_source_files", []):
            if not isinstance(source, dict):
                continue
            logical_path = source.get("path")
            expected_sha256 = source.get("sha256")
            path = valid_runtime_paths.get(logical_path)
            if path is None or expected_sha256 != sha256_file(path):
                task_contract_snapshot_verified = False
                findings.append(
                    make_finding(
                        severity="Blocker",
                        category="task_contract_snapshot_drift",
                        source_id=str(source.get("source_id", task_id)),
                        logical_path=str(logical_path),
                        message="TaskContract 中的命中来源哈希与当前运行资产不一致",
                        impact="当前审计输入无法回到任务冻结的完整来源文件",
                        evidence=f"expected={expected_sha256}",
                        remediation_class="refresh-or-stop",
                    )
                )
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        task_contract_snapshot_verified = False
        findings.append(
            make_finding(
                severity="Blocker",
                category="task_contract_snapshot_missing",
                source_id=task_id,
                logical_path=f".project-governance/tasks/{task_id}/before.json",
                message=f"无法读取冻结 TaskContract: {exc}",
                impact="审计输入没有任务执行前的来源与规则摘要基线",
                evidence=str(exc),
                remediation_class="task-contract-fix",
            )
        )

    after_hashes = {item["embedded"]: sha256_file(skill_root / item["embedded"]) for item in protected_entries}
    protected_unchanged = before_hashes == after_hashes
    if not protected_unchanged:
        changed = sorted(path for path, digest in before_hashes.items() if after_hashes.get(path) != digest)
        findings.append(
            make_finding(
                severity="Blocker",
                category="audit_mutated_protected_asset",
                source_id="T-011",
                logical_path="04_模板与检查清单/run-web-product-workflow",
                message="审计运行期间受保护资产发生变化",
                evidence=", ".join(changed),
                remediation_class="implementation-fix",
            )
        )

    ordered_findings = finalize_findings(findings)
    severity_counts = Counter(item["severity"] for item in ordered_findings)
    category_counts = Counter(item["category"] for item in ordered_findings)
    norm_index_ready = not any(item["severity"] in BLOCKING_SEVERITIES for item in ordered_findings)
    input_facts = {
        "manifest_sha256": sha256_file(manifest_path),
        "tailoring_map_sha256": current_rule_set_sha256,
        "profile_meta_map_sha256": sha256_file(default_mapping_path()),
        "normative_sources_sha256": current_normative_digest,
        "task_contract_snapshot_verified": task_contract_snapshot_verified,
        "protected_asset_sha256": dict(sorted(before_hashes.items())),
        "auditor_sha256": sha256_file(Path(__file__).resolve()),
    }
    deterministic_body = {
        "report_version": REPORT_VERSION,
        "project_id": project_id,
        "task_id": task_id,
        "scope": {
            "norm_sources": role_counts.get("norm", 0),
            "mappings": role_counts.get("mapping", 0),
            "schemas": role_counts.get("schema", 0),
            "evaluations": role_counts.get("evaluation", 0),
            "manifest": 1,
            "standards": len(tailoring.get("standards", {})),
            "profiles": len(profiles),
        },
        "inputs": input_facts,
        "findings": ordered_findings,
        "manual_review_inventory": {
            "precedence_and_authority_claims": sorted(
                precedence_claims,
                key=lambda item: (item["source_id"], item["logical_path"], item["line"], item["text"]),
            ),
            "unique_fact_source_claims": sorted(
                unique_source_claims,
                key=lambda item: (item["source_id"], item["logical_path"], item["line"], item["subject"]),
            ),
        },
        "norm_index_ready": norm_index_ready,
        "protected_assets_unchanged": protected_unchanged,
    }
    audit_digest = sha256_bytes(canonical_json_bytes(deterministic_body))
    report = {
        "schema_version": "6.3-candidate",
        "report_version": REPORT_VERSION,
        "report_type": "norm-consistency-audit",
        "project_id": project_id,
        "task_id": task_id,
        "generated_at": now_utc(),
        "generator": {
            "path": "run-web-product-workflow/scripts/audit_norm_consistency.py",
            "sha256": input_facts["auditor_sha256"],
        },
        "audit_status": "Complete",
        "scope": deterministic_body["scope"],
        "inputs": input_facts,
        "summary": {
            "total_findings": len(ordered_findings),
            "by_severity": {key: severity_counts.get(key, 0) for key in SEVERITY_ORDER},
            "by_category": dict(sorted(category_counts.items())),
        },
        "manual_review_inventory": deterministic_body["manual_review_inventory"],
        "detector_limits": [
            "模态冲突机检只确认规范化命题完全一致的相反模态；同义改写由独立人工复核补充",
            "Authority机检覆盖唯一事实源重复声明与显式优先级循环；隐式Scope/时效/主体冲突由独立人工复核补充",
            "定义差异先作为候选，不由机器自行判断兼容扩展或语义冲突",
            (
                "消费项目 runtime-only 模式验证 Manifest、内嵌快照和任务来源边界；"
                "规范编辑仓 Authority 对账只在发布审计执行"
                if not verify_authority_sources
                else "发布审计已对账规范编辑仓 Authority 与内嵌运行快照"
            ),
        ],
        "norm_index_ready": norm_index_ready,
        "next_gate": "T-013-eligible" if norm_index_ready else "T-012-required",
        "protected_assets_unchanged": protected_unchanged,
        "audit_digest": audit_digest,
        "findings": ordered_findings,
    }
    schema_errors = validate_json_document(
        report,
        "norm-consistency-report.schema.json",
        "norm-consistency-report",
    )
    if schema_errors:
        raise GovernanceError("; ".join(schema_errors))
    return report, [manifest_path, *sorted(protected_paths, key=lambda path: path.as_posix())]


def write_report(
    report: dict[str, Any],
    *,
    project_root: Path,
    project_id: str,
    output_dir: Path,
    sources: list[Path],
) -> list[Path]:
    root = governance_root(project_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "norm-consistency-audit.json"
    markdown_path = output_dir / "norm-consistency-audit.md"
    json_content = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    outputs = _write_derived_view(
        root=root,
        content_path=json_path,
        content=json_content,
        project_id=project_id,
        view_id=f"DV-{report['task_id']}-NORM-AUDIT-JSON",
        view_kind="norm-consistency-audit-json",
        sources=sources,
    )
    outputs.extend(
        _write_derived_view(
            root=root,
            content_path=markdown_path,
            content=render_markdown(report),
            project_id=project_id,
            view_id=f"DV-{report['task_id']}-NORM-AUDIT-MD",
            view_kind="norm-consistency-audit-review",
            sources=[json_path],
        )
    )
    return outputs


def run_self_test() -> None:
    def check(condition: bool, message: str) -> None:
        if not condition:
            raise GovernanceError(f"audit_norm_consistency self-test failed: {message}")

    fixture = """# C01 fixture

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C01 |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 上游依赖 | C02 V0.1 |

## 2. 术语

| 术语 | 定义 |
|---|---|
| Gate | 必须满足的进入条件 |

1. Agent 必须记录事实。
"""
    controls = parse_control_table(fixture)
    check(control_value(controls, ["文档编号"])[0] == "C01", "control table parsing")
    stale = dependency_version_findings(
        source_id="C01",
        logical_path="references/C01.md",
        controls=controls,
        versions={"C01": "V0.3", "C02": "V0.3"},
    )
    check(len(stale) == 1 and stale[0]["category"] == "stale_dependency_version", "stale dependency detection")
    check(bool(stale[0]["impact"]), "stale dependency impact")
    list_fixture = fixture.replace("C02 V0.1", "E01、E02 V0.1")
    list_stale = dependency_version_findings(
        source_id="C01",
        logical_path="references/C01.md",
        controls=parse_control_table(list_fixture),
        versions={"C01": "V0.3", "E01": "V0.3", "E02": "V0.3"},
    )
    check(len(list_stale) == 1 and list_stale[0]["related_sources"] == ["E01", "E02"], "list dependency parsing")
    check(len(extract_definitions("C01", "references/C01.md", fixture)) == 1, "definition extraction")
    positive = extract_normative_statements("C01", "references/C01.md", "Agent 必须记录事实。")
    negative = extract_normative_statements("C02", "references/C02.md", "Agent 禁止记录事实。")
    check(positive[0]["key"] == negative[0]["key"], "normative statement normalization")
    check({positive[0]["polarity"], negative[0]["polarity"]} == {"positive", "negative"}, "normative polarity")
    authority_fixture = """| 主题 | 唯一事实源 |
|---|---|
| Task State | TaskContract |

C01 优先于 C02。
"""
    unique_claims = extract_unique_source_claims(
        "C01", "references/C01.md", authority_fixture
    )
    check(len(unique_claims) == 1, "unique source claim extraction")
    check(unique_claims[0]["subject"] == "Task State", "unique source subject")
    precedence_claims = extract_precedence_claims(
        "C01", "references/C01.md", authority_fixture
    )
    reverse_claims = extract_precedence_claims(
        "C02", "references/C02.md", "C02 优先于 C01。"
    )
    cycles = precedence_cycle_findings(
        precedence_claims + reverse_claims, {"C01", "C02"}
    )
    check(len(cycles) == 1 and cycles[0]["category"] == "precedence_cycle", "precedence cycle detection")
    payload = {"b": "值", "a": [2, 1]}
    check(canonical_json_bytes(payload) == canonical_json_bytes(payload), "canonical JSON stability")
    first = finalize_findings([stale[0]])
    second = finalize_findings([stale[0]])
    check(canonical_json_bytes(first) == canonical_json_bytes(second), "finding order determinism")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-id", default="P-AINATIVE-SPEC")
    parser.add_argument("--task-id")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--fail-on", choices=("blocker", "major", "none"), default="major")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help="For consumer projects: validate the protected embedded publication without requiring the normative editing repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            print(
                "SELF-TEST PASSED: control metadata, stale dependency, definition, "
                "modal, authority, precedence, deterministic digest"
            )
            return 0
        if not args.task_id and not args.runtime_only:
            raise GovernanceError("--task-id is required unless --runtime-only is used")
        task_id = args.task_id or "RUNTIME-ONLY"
        report, sources = audit(
            args.project_root,
            args.project_id,
            task_id,
            verify_authority_sources=not args.runtime_only,
        )
        output_dir = args.output_dir or (
            governance_root(args.project_root) / "generated" / "audits" / task_id
        )
        outputs = write_report(
            report,
            project_root=args.project_root,
            project_id=args.project_id,
            output_dir=output_dir,
            sources=sources,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        json.dumps(
            {
                "audit_status": report["audit_status"],
                "audit_digest": report["audit_digest"],
                "norm_index_ready": report["norm_index_ready"],
                "next_gate": report["next_gate"],
                "summary": report["summary"],
                "outputs": [str(path) for path in outputs],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if args.fail_on == "blocker" and report["summary"]["by_severity"]["Blocker"]:
        return 3
    if args.fail_on == "major" and any(
        report["summary"]["by_severity"][severity] for severity in ("Blocker", "Major")
    ):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
