#!/usr/bin/env python3
"""Scan the two governed asset roots and build the console's domain model.

Read-only. Every request re-scans, so the console never shows a stale snapshot --
that was the defect of the generated single page it replaces.

Document classification is not reimplemented here: manage_project_docs already owns
the layout rules from references/project-document-layout.md, including the section 3
exceptions that decide whether a file is a product document at all. Reusing it is
what lets the console audit assets this Skill did not create.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import audit_console
from governance_artifacts import (
    GovernanceError,
    embedded_manifest_path,
    read_json,
    read_jsonl,
    validate_embedded_manifest,
)
from manage_project_docs import (
    DOCS_DIR,
    GOVERNANCE_DIR,
    MANAGED_END,
    MANAGED_START,
    STANDARD_TYPES,
    document_type,
    is_package_root_document,
    legacy_roots,
)

# Authoritative one-line purposes, quoted from VC-PPG-COM-002 (受控产物目录与状态模型).
# The console must explain what each governance object is FOR, and that explanation
# has to come from the norm rather than from the console's author.
META_TYPES = (
    ("TaskContract", "任务执行前", "保存 Task Profile、适用性事实、确定性裁剪快照、权限、验收和计划；Run 开始时冻结，修订必须留痕", "tasks/<TaskID>/before.json"),
    ("RunLedger", "任务执行中", "只追加重要事件", "tasks/<TaskID>/run.jsonl"),
    ("TaskOutcome", "任务终态", "已成立事实和遗留问题的任务级事实源", "tasks/<TaskID>/after.json"),
    ("ProjectState", "跨任务当前状态", "从终态和权威资产物化，不直接编辑", "project-state.json"),
    ("AuthorityAsset", "项目长期事实", "需求、设计、决定、证据、基线等权威对象", "authority/"),
    ("DerivedView", "按需审核与查询", "可重建，禁止直接承载新权威事实", "generated/"),
)


PREVIEWABLE_TEXT = {".md", ".mdx", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv", ".log"}
PREVIEWABLE_IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
PREVIEWABLE_HTML = {".html", ".htm"}

ARTIFACT_FAMILIES = (
    ("contexts", "检索上下文", "每个任务每阶段的 Norm Packet、Source Pack 与 Retrieval Plan"),
    ("audits", "审计报告", "规范一致性与检索契约审计输出"),
    ("reviews", "评审视图", "ProjectState 与任务的人类评审 DerivedView"),
    ("requests", "查询请求", "已固化的有界条款查询请求"),
)


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _stat(path: Path, root: Path) -> dict[str, Any]:
    info = path.stat()
    return {
        "path": _relative(path, root),
        "name": path.name,
        "size": info.st_size,
        "modified": datetime.fromtimestamp(info.st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "suffix": path.suffix.lower(),
        "kind": preview_kind(path),
    }


def preview_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in PREVIEWABLE_IMAGE:
        return "image"
    if suffix in PREVIEWABLE_HTML:
        return "html"
    if suffix in {".json", ".jsonl"}:
        return "json"
    if suffix in PREVIEWABLE_TEXT:
        return "text"
    return "binary"


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return []
    return (path for path in sorted(root.rglob("*")) if path.is_file())


# --- governance domain ------------------------------------------------------


def _project_state(project_root: Path) -> dict[str, Any]:
    path = project_root / GOVERNANCE_DIR / "project-state.json"
    if not path.is_file():
        return {}
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, GovernanceError):
        return {}


def _task_entry(task_dir: Path, node: dict[str, Any], status: str, project_root: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "task_id": node["task_id"],
        "ordinal": node.get("ordinal", 0),
        "status": status,
        "carrier": "未知",
        "objective": "",
        "risk_level": "",
        "delivery_scenario": "",
        "development_types": [],
        "change_surfaces": [],
        "allowed_paths": [],
        "acceptance": [],
        "events": [],
        "established_facts": [],
        "actual_changes": [],
        "incomplete_items": [],
        "next_tasks": node.get("next_tasks", []),
        "derived_from": node.get("derived_from", []),
        "required_by": node.get("required_by", []),
        "depends_on": node.get("depends_on", []),
        "supersedes": node.get("supersedes", []),
        "files": [],
        "manifest": [],
        "tailoring": None,
        "eligibility": None,
        "selection": None,
        "scope": {},
        "authority": [],
    }
    minimal_path = task_dir / "task-record.json"
    before_path = task_dir / "before.json"
    try:
        if minimal_path.is_file():
            record = read_json(minimal_path)
            contract = record.get("task_contract", {})
            profile = contract.get("task_profile", {})
            outcome = record.get("task_outcome") or {}
            entry.update(
                carrier="Minimal",
                objective=contract.get("objective", ""),
                risk_level=profile.get("risk_level", ""),
                delivery_scenario=profile.get("delivery_scenario", ""),
                development_types=[profile["development_type"]] if profile.get("development_type") else [],
                change_surfaces=[profile["change_surface"]] if profile.get("change_surface") else [],
                allowed_paths=contract.get("allowed_paths", []),
                acceptance=[contract["acceptance"]] if contract.get("acceptance") else [],
                events=[
                    {
                        "event_type": event.get("event_type", ""),
                        "summary": event.get("summary", ""),
                        "timestamp": event.get("timestamp", ""),
                        "status": event.get("status", ""),
                    }
                    for event in record.get("run_ledger", [])
                ],
                established_facts=outcome.get("established_facts", []),
                actual_changes=outcome.get("actual_changes", []),
                incomplete_items=outcome.get("incomplete_items", []),
                lifecycle=record.get("lifecycle_state", ""),
                # Minimal has no tailoring_resolution by design (16.4); its analogue is
                # the eligibility that permitted the carrier plus how it was selected.
                eligibility=record.get("eligibility"),
                selection=record.get("selection"),
                manifest=record.get("artifact_manifest", []),
                scope={"in_scope": [contract.get("scope", "")], "out_of_scope": contract.get("out_of_scope", []),
                       "allowed_paths": contract.get("allowed_paths", []),
                       "forbidden_actions": contract.get("forbidden_actions", [])},
                authority=contract.get("authority_refs", []),
            )
        elif before_path.is_file():
            before = read_json(before_path)
            profile = before.get("task_profile", {})
            entry.update(
                carrier="完整载体",
                objective=before.get("objective", ""),
                risk_level=profile.get("risk_level", ""),
                delivery_scenario=profile.get("delivery_scenario", ""),
                development_types=profile.get("development_types", []),
                change_surfaces=profile.get("change_surfaces", []),
                allowed_paths=before.get("scope", {}).get("allowed_paths", []),
                acceptance=[
                    item.get("statement", "") if isinstance(item, dict) else str(item)
                    for item in before.get("acceptance", [])
                ],
                lifecycle=before.get("lifecycle_state", ""),
                manifest=before.get("artifact_manifest", []),
                tailoring=before.get("tailoring_resolution"),
                scope=before.get("scope", {}),
                authority=before.get("authority", []),
            )
            run_path = task_dir / "run.jsonl"
            if run_path.is_file():
                entry["events"] = [
                    {
                        "event_type": event.get("event_type", ""),
                        "summary": event.get("summary", ""),
                        "timestamp": event.get("timestamp", ""),
                        "status": event.get("status", ""),
                    }
                    for event in read_jsonl(run_path)
                ]
            after_path = task_dir / "after.json"
            if after_path.is_file():
                after = read_json(after_path)
                entry["established_facts"] = after.get("established_facts", [])
                entry["actual_changes"] = after.get("actual_changes", [])
                entry["incomplete_items"] = after.get("incomplete_items", [])
                # The terminal manifest supersedes the contract's declaration.
                if after.get("artifact_manifest"):
                    entry["manifest"] = after["artifact_manifest"]
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        entry["error"] = str(exc)
    entry["files"] = [_stat(path, project_root) for path in _iter_files(task_dir)]
    entry["updated_at"] = max((item["modified"] for item in entry["files"]), default="")
    return entry


def state_provenance(project_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    """Where the task data came from and whether it can still be trusted.

    Documents, artifacts and integrity are scanned live on every request. Tasks and
    lineage are not: they are read from project-state.json, a generated snapshot. If a
    task record changed after that snapshot was built, every task view is quietly out
    of date -- an auditor has to be told, not left to assume.
    """

    state_path = project_root / GOVERNANCE_DIR / "project-state.json"
    info: dict[str, Any] = {
        "present": state_path.is_file(),
        "generated_at": state.get("generated_at", ""),
        "stale": False,
        "newer": [],
    }
    if not info["present"]:
        return info
    built = state_path.stat().st_mtime
    tasks_root = project_root / GOVERNANCE_DIR / "tasks"
    info["newer"] = sorted(
        _relative(path, project_root.resolve())
        for path in _iter_files(tasks_root)
        if path.stat().st_mtime > built + 1
    )
    info["stale"] = bool(info["newer"])
    return info


def scan_tasks(project_root: Path, state: dict[str, Any]) -> list[dict[str, Any]]:
    tasks_root = project_root / GOVERNANCE_DIR / "tasks"
    status_by_id = {item["task_id"]: item.get("status", "Active") for item in state.get("source_tasks", [])}
    entries = []
    for node in sorted(state.get("task_graph", []), key=lambda item: item.get("ordinal", 0)):
        entries.append(
            _task_entry(tasks_root / node["task_id"], node, status_by_id.get(node["task_id"], "Active"), project_root)
        )
    return entries


def scan_artifacts(project_root: Path) -> list[dict[str, Any]]:
    """Group generated artifacts by family, pairing each with its DerivedView envelope."""

    generated = project_root / GOVERNANCE_DIR / "generated"
    families = []
    for name, label, hint in ARTIFACT_FAMILIES:
        root = generated / name
        files = [path for path in _iter_files(root) if not path.name.endswith(".view.json")]
        items = []
        for path in files:
            envelope_path = path.with_name(path.name + ".view.json")
            envelope = None
            if envelope_path.is_file():
                try:
                    raw = read_json(envelope_path)
                    envelope = {
                        "view_id": raw.get("view_id", ""),
                        "view_kind": raw.get("view_kind", ""),
                        "integrity_status": raw.get("integrity_status", ""),
                        "generated_at": raw.get("generated_at", ""),
                        "sources": raw.get("sources", []),
                    }
                except (OSError, json.JSONDecodeError, GovernanceError):
                    envelope = {"integrity_status": "Failed"}
            entry = _stat(path, project_root)
            entry["envelope"] = envelope
            entry["group"] = _relative(path.parent, generated / name)
            parts = path.relative_to(root).parts
            entry["task_id"] = parts[0] if len(parts) > 1 else ""
            entry["stage"] = parts[1] if len(parts) > 2 else ""
            items.append(entry)
        families.append({"name": name, "label": label, "hint": hint, "items": items})
    return families


def scan_authority(project_root: Path) -> list[dict[str, Any]]:
    root = project_root / GOVERNANCE_DIR / "authority"
    assets = []
    for path in _iter_files(root):
        if path.suffix != ".json":
            continue
        try:
            raw = read_json(path)
        except (OSError, json.JSONDecodeError, GovernanceError):
            continue
        assets.append(
            {
                "asset_id": raw.get("asset_id", path.stem),
                "state": raw.get("state", ""),
                "legacy_kind": raw.get("legacy_kind", ""),
                "revision": raw.get("revision", ""),
                "path": _relative(path, project_root),
            }
        )
    return assets


# --- document domain --------------------------------------------------------


def _managed_entries(readme: Path) -> list[str]:
    """Names listed between the LG-MANAGED markers, which is where custom types register."""

    if not readme.is_file():
        return []
    try:
        text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    if MANAGED_START not in text or MANAGED_END not in text:
        return []
    block = text.split(MANAGED_START, 1)[1].split(MANAGED_END, 1)[0]
    names = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- `"):
            names.append(line.split("`")[1].rstrip("/"))
    return names


def scan_documents(project_root: Path) -> dict[str, Any]:
    docs_root = project_root / DOCS_DIR
    requirements: list[dict[str, Any]] = []
    intake: list[dict[str, Any]] = []
    archives: list[dict[str, Any]] = []
    stray: list[dict[str, Any]] = []

    if not docs_root.is_dir():
        return {"present": False, "requirements": [], "intake": [], "archives": [], "stray": [], "root": DOCS_DIR}

    requirements_root = docs_root / "requirements"
    if requirements_root.is_dir():
        for req_dir in sorted(path for path in requirements_root.iterdir() if path.is_dir()):
            readme = req_dir / "README.md"
            registered = set(_managed_entries(readme))
            groups: dict[str, list[dict[str, Any]]] = {}
            for path in _iter_files(req_dir):
                relative = path.relative_to(req_dir)
                bucket = relative.parts[0] if len(relative.parts) > 1 else "_root"
                groups.setdefault(bucket, []).append(_stat(path, project_root))
            custom = sorted(
                name
                for name in groups
                if name not in STANDARD_TYPES and name != "_root"
            )
            requirements.append(
                {
                    "requirement_id": req_dir.name,
                    "path": _relative(req_dir, project_root),
                    "has_readme": readme.is_file(),
                    "groups": dict(sorted(groups.items())),
                    "file_count": sum(len(items) for items in groups.values()),
                    "custom_types": custom,
                    # refresh_project_readmes rewrites the managed block on every task
                    # creation and lists whatever directories exist, so "unregistered"
                    # is not a state that can persist. What is worth surfacing is that
                    # a type outside the nine standard ones is in use at all.
                    "registered_types": sorted(registered),
                }
            )

    intake_root = docs_root / "_intake"
    for path in _iter_files(intake_root):
        entry = _stat(path, project_root)
        relative = path.relative_to(intake_root)
        entry["document_type"] = relative.parts[1] if len(relative.parts) > 2 else document_type(path)
        intake.append(entry)

    archive_root = docs_root / "_archive" / "legacy-migrations"
    if archive_root.is_dir():
        for migration in sorted(path for path in archive_root.iterdir() if path.is_dir()):
            report = migration / "migration-report.md"
            archives.append(
                {
                    "migration_id": migration.name,
                    "path": _relative(migration, project_root),
                    "file_count": sum(1 for _ in _iter_files(migration)),
                    "has_report": report.is_file(),
                    "has_plan": (migration / "migration-plan.json").is_file(),
                    "has_manifest": (migration / "manifest.json").is_file(),
                }
            )

    known_roots = {"requirements", "_intake", "_archive"}
    for path in _iter_files(docs_root):
        relative = path.relative_to(docs_root)
        if relative.parts[0] in known_roots:
            continue
        if len(relative.parts) == 1 and relative.name.casefold() == "readme.md":
            continue
        stray.append(_stat(path, project_root))

    return {
        "present": True,
        "root": DOCS_DIR,
        "has_readme": (docs_root / "README.md").is_file(),
        "requirements": requirements,
        "intake": intake,
        "archives": archives,
        "stray": stray,
    }


def unmanaged_documents(project_root: Path) -> list[dict[str, Any]]:
    """Product documents still living outside LG_project_docs.

    manage_project_docs.legacy_roots applies the section 3 exceptions -- repository
    READMEs, component docs, runtime assets, dependencies -- so what survives is the
    set a person actually has to decide about.
    """

    findings: list[dict[str, Any]] = []
    try:
        roots = legacy_roots(project_root)
    except (GovernanceError, OSError, ValueError):
        return findings
    for root in roots:
        for path in _iter_files(root):
            relative = path.relative_to(project_root.resolve())
            if is_package_root_document(relative):
                continue
            entry = _stat(path, project_root)
            entry["document_type"] = document_type(path)
            findings.append(entry)
    return findings


def document_findings(project_root: Path, docs: dict[str, Any], tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Layout and registration problems a person should act on."""

    findings: list[dict[str, Any]] = []

    def mark_previewable(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Preview serves files; a finding pointing at a directory must not link to it."""

        for item in items:
            if "previewable" in item or not item.get("path"):
                continue
            item["previewable"] = (project_root / item["path"]).is_file()
        return items
    if not docs.get("present"):
        findings.append(
            {
                "severity": "info",
                "category": "docs-root-missing",
                "summary": f"{DOCS_DIR}/ 尚未建立",
                "detail": "运行 manage_project_docs.py init 建立项目文档目录。",
            }
        )
        return findings
    if not docs.get("has_readme"):
        findings.append(
            {
                "severity": "warn",
                "category": "readme-contract",
                "summary": f"{DOCS_DIR}/README.md 缺失",
                "detail": "项目文档目录与迁移规范 §4 要求该 README 解释分类规则与受管清单。",
            }
        )
    for requirement in docs["requirements"]:
        if not requirement["has_readme"]:
            findings.append(
                {
                    "severity": "warn",
                    "category": "readme-contract",
                    "summary": f"{requirement['requirement_id']} 缺少 README.md",
                    "detail": "§4 要求每个需求目录的 README 解释其下每个文件和目录的作用；"
                              "下次建立任务时 refresh_project_readmes 会补齐受管块。",
                    "path": requirement["path"],
                }
            )
        if requirement["custom_types"]:
            findings.append(
                {
                    "severity": "info",
                    "category": "custom-type",
                    "summary": f"{requirement['requirement_id']} 使用了标准九类之外的类型："
                               + "、".join(requirement["custom_types"]),
                    "detail": "§2 允许自定义类型，README 受管清单由工具自动维护；此处仅告知，供你确认这些类型确有必要。",
                    "path": requirement["path"],
                }
            )
    for item in docs["stray"]:
        findings.append(
            {
                "severity": "warn",
                "category": "layout-violation",
                "summary": f"布局外资产：{item['path']}",
                "detail": "§1 规定文档应落在 requirements/<RequirementID>/<类型>/、_intake 或 _archive。",
                "path": item["path"],
            }
        )
    referenced = {task["task_id"] for task in tasks}
    for requirement in docs["requirements"]:
        if requirement["requirement_id"] not in referenced:
            findings.append(
                {
                    "severity": "info",
                    "category": "orphan-requirement",
                    "summary": f"{requirement['requirement_id']} 没有对应的受控任务",
                    "detail": "文档目录存在但没有任务引用该身份；可能是外部资料或尚未建立任务。",
                    "path": requirement["path"],
                }
            )
    for item in unmanaged_documents(project_root):
        findings.append(
            {
                "severity": "warn",
                "category": "unmanaged-document",
                "summary": f"未纳管文档：{item['path']}",
                "detail": "符合产品文档特征但仍在 LG_project_docs 之外；用 manage_project_docs.py plan-migration 处理。"
                          "该路径不在控制台可读范围内，只显示不提供预览。",
                "path": item["path"],
                "previewable": False,
            }
        )
    return mark_previewable(findings)


# --- integrity --------------------------------------------------------------


def scan_integrity() -> dict[str, Any]:
    manifest_path = embedded_manifest_path()
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return {"total": 0, "errors": [str(exc)]}
    return {
        "total": len(manifest.get("files", [])),
        "errors": sorted(validate_embedded_manifest()),
        "source_of_truth": manifest.get("source_of_truth", ""),
        "roles": _role_counts(manifest),
    }


def _role_counts(manifest: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in manifest.get("files", []):
        counts[item.get("role", "?")] = counts.get(item.get("role", "?"), 0) + 1
    return dict(sorted(counts.items()))


# --- entry point ------------------------------------------------------------


def scan(project_root: Path) -> dict[str, Any]:
    """Build the whole model. Called per request, so it must stay cheap and total."""

    project_root = project_root.resolve()
    state = _project_state(project_root)
    tasks = scan_tasks(project_root, state)
    docs = scan_documents(project_root)
    return {
        "project_root": str(project_root),
        "project_id": state.get("project_id", project_root.name),
        "state_generated_at": state.get("generated_at", ""),
        "state_present": bool(state),
        "provenance": state_provenance(project_root, state),
        # Distinguishing "measured and zero" from "never recorded" matters more to a
        # reviewer than the number itself.
        "lineage_recorded": any(task["next_tasks"] or task["derived_from"] for task in tasks),
        "tasks": tasks,
        "derivation": audit_console.derivation_audit(state),
        "unresolved": state.get("unresolved_items", []),
        "current_facts": state.get("current_facts", []),
        "authority": scan_authority(project_root),
        "artifacts": scan_artifacts(project_root),
        "docs": docs,
        "doc_findings": document_findings(project_root, docs, tasks),
        "integrity": scan_integrity(),
    }


def search(model: dict[str, Any], query: str, limit: int = 120) -> list[dict[str, Any]]:
    """Substring search across the entities the console can link to."""

    needle = query.strip().casefold()
    if not needle:
        return []
    hits: list[dict[str, Any]] = []

    def add(kind: str, label: str, href: str, context: str) -> None:
        if len(hits) < limit:
            hits.append({"kind": kind, "label": label, "href": href, "context": context})

    for task in model["tasks"]:
        haystack = " ".join(
            [task["task_id"], task["objective"], task["status"], task["carrier"]]
            + task["acceptance"]
            + task["established_facts"]
            + task["actual_changes"]
            + [event["summary"] for event in task["events"]]
        )
        if needle in haystack.casefold():
            add("任务", task["task_id"], f"/tasks/{task['task_id']}", task["objective"])
    for requirement in model["docs"].get("requirements", []):
        if needle in requirement["requirement_id"].casefold():
            add("需求", requirement["requirement_id"], f"/docs/{requirement['requirement_id']}",
                f"{requirement['file_count']} 个文档")
        for items in requirement["groups"].values():
            for item in items:
                if needle in item["path"].casefold():
                    add("文档", item["name"], f"/preview?path={item['path']}", item["path"])
    for bucket in ("intake", "stray"):
        for item in model["docs"].get(bucket, []):
            if needle in item["path"].casefold():
                add("文档", item["name"], f"/preview?path={item['path']}", item["path"])
    for family in model["artifacts"]:
        for item in family["items"]:
            if needle in item["path"].casefold():
                add("生成物", item["name"], f"/preview?path={item['path']}", item["path"])
    return hits
