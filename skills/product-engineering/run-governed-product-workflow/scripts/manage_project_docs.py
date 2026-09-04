#!/usr/bin/env python3
"""Initialize, validate, inventory, and safely migrate project documentation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from governance_artifacts import (
    GovernanceError,
    atomic_write_json,
    now_utc,
    read_json,
    sha256_file,
    skill_root_path,
    validate_embedded_manifest,
    write_text,
)


GOVERNANCE_DIR = ".project-governance"
DOCS_DIR = "LG_project_docs"
STANDARD_TYPES = (
    "discovery",
    "prd",
    "requirements",
    "design",
    "ui-previews",
    "decisions",
    "verification",
    "release",
    "references",
)
LEGACY_ROOT_NAMES = {
    "docs", "doc", "documentation", "documents", "project-docs", "product-docs",
    "requirements", "requirement", "design", "designs", "prd", "specs",
    "文档", "项目文档", "产品文档", "需求", "设计",
}
EXCLUDED_ROOTS = {
    ".git", ".svn", ".hg", ".idea", ".vscode", ".openai", ".codex", ".agents",
    GOVERNANCE_DIR, DOCS_DIR, "node_modules", "vendor", "dist", "build", "coverage",
    ".venv", "venv", "__pycache__",
}
DOCUMENT_EXTENSIONS = {
    ".md", ".mdx", ".txt", ".rtf", ".doc", ".docx", ".pdf", ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".webp", ".svg",
}
PACKAGE_DOC_RE = re.compile(
    r"^(?:readme|license|contributing|changelog|security|code_of_conduct)(?:\..+)?$",
    flags=re.IGNORECASE,
)
PRODUCT_DOC_RE = re.compile(
    r"(?:prd|需求|requirement|设计|design|架构|architecture|执行计划|需求澄清|验收|verification|release)",
    flags=re.IGNORECASE,
)
REQUIREMENT_ID_RE = re.compile(
    r"(?<![A-Za-z0-9])((?:REQ|FR|FEAT|TASK|T)-[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99}[A-Za-z0-9])?)(?![A-Za-z0-9])",
    flags=re.IGNORECASE,
)
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
MANAGED_START = "<!-- LG-MANAGED:START -->"
MANAGED_END = "<!-- LG-MANAGED:END -->"


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def ensure_within(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise GovernanceError(f"{label} escapes project root: {path}") from exc
    return resolved


def template_path(name: str) -> Path:
    return skill_root_path() / "assets" / "project-templates" / name


def copy_template_if_absent(target: Path, template_name: str, replacements: dict[str, str] | None = None) -> bool:
    if target.exists():
        if not target.is_file():
            raise GovernanceError(f"README target is not a file: {target}")
        return False
    content = template_path(template_name).read_text(encoding="utf-8")
    for key, value in (replacements or {}).items():
        content = content.replace("{{" + key + "}}", value)
    write_text(target, content)
    return True


def replace_managed_section(path: Path, lines: Iterable[str]) -> None:
    content = path.read_text(encoding="utf-8") if path.is_file() else ""
    managed = MANAGED_START + "\n" + "\n".join(lines).rstrip() + "\n" + MANAGED_END
    if MANAGED_START in content and MANAGED_END in content:
        start = content.index(MANAGED_START)
        end = content.index(MANAGED_END, start) + len(MANAGED_END)
        updated = content[:start] + managed + content[end:]
    else:
        updated = content.rstrip() + ("\n\n" if content.strip() else "") + managed + "\n"
    if updated != content:
        write_text(path, updated)


def ensure_requirement_directory(project_root: Path, requirement_id: str) -> Path:
    if not SAFE_ID_RE.fullmatch(requirement_id):
        raise GovernanceError(f"invalid RequirementID for a Windows-safe directory: {requirement_id!r}")
    root = project_root.resolve() / DOCS_DIR / "requirements" / requirement_id
    root.mkdir(parents=True, exist_ok=True)
    for category in STANDARD_TYPES:
        (root / category).mkdir(parents=True, exist_ok=True)
    copy_template_if_absent(
        root / "README.md",
        "requirement.README.md",
        {"REQUIREMENT_ID": requirement_id},
    )
    refresh_requirement_readme(root)
    return root


def refresh_requirement_readme(requirement_root: Path) -> None:
    entries: list[str] = []
    for directory in sorted((path for path in requirement_root.iterdir() if path.is_dir()), key=lambda p: p.name.casefold()):
        files = sorted(
            path.relative_to(requirement_root).as_posix()
            for path in directory.rglob("*")
            if path.is_file()
        )
        kind = "标准类型" if directory.name in STANDARD_TYPES else "自定义类型"
        entries.append(f"- `{directory.name}/`（{kind}）：{len(files)} 个文件")
        entries.extend(f"  - `{value}`" for value in files)
    replace_managed_section(requirement_root / "README.md", entries or ["当前没有文档文件。"])


def refresh_project_readmes(project_root: Path) -> None:
    root = project_root.resolve()
    governance = root / GOVERNANCE_DIR
    docs = root / DOCS_DIR
    governance_entries = []
    for path in sorted(governance.iterdir(), key=lambda item: item.name.casefold()):
        if path.name == "README.md":
            continue
        kind = "目录" if path.is_dir() else "文件"
        governance_entries.append(f"- `{path.name}{'/' if path.is_dir() else ''}`：{kind}")
    replace_managed_section(
        governance / "README.md",
        governance_entries or ["当前没有治理记录。"],
    )
    requirement_root = docs / "requirements"
    requirement_entries: list[str] = []
    if requirement_root.is_dir():
        for path in sorted((item for item in requirement_root.iterdir() if item.is_dir()), key=lambda p: p.name.casefold()):
            refresh_requirement_readme(path)
            custom = sorted(item.name for item in path.iterdir() if item.is_dir() and item.name not in STANDARD_TYPES)
            suffix = f"；自定义类型：{', '.join(custom)}" if custom else ""
            requirement_entries.append(f"- `{path.name}/`{suffix}")
    intake_files = sum(1 for path in (docs / "_intake").rglob("*") if path.is_file())
    archive_count = sum(1 for path in (docs / "_archive" / "legacy-migrations").iterdir() if path.is_dir())
    requirement_entries.extend([
        f"- `_intake/`：{intake_files} 个待分类文件",
        f"- `_archive/legacy-migrations/`：{archive_count} 次迁移归档",
    ])
    replace_managed_section(docs / "README.md", requirement_entries)


def initialize_project_document_layout(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    if not root.is_dir():
        raise GovernanceError(f"project root is missing: {root}")
    governance = root / GOVERNANCE_DIR
    docs = root / DOCS_DIR
    for directory in (
        governance,
        governance / "tasks",
        governance / "authority",
        governance / "generated",
        docs,
        docs / "requirements",
        docs / "_intake" / "unclassified",
        docs / "_archive" / "legacy-migrations",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    copy_template_if_absent(governance / "README.md", "project-governance.README.md")
    copy_template_if_absent(docs / "README.md", "project-docs.README.md")
    # The console is the project's own tool, so it is deployed with the directory it
    # audits rather than left to be run out of the Skill. Idempotent: a deployment
    # that already matches this Skill is left untouched.
    from deploy_console import deploy as deploy_governance_console

    deploy_governance_console(root)
    refresh_project_readmes(root)
    return [governance / "README.md", docs / "README.md"]


def document_type(path: Path) -> str:
    folded = path.as_posix().casefold()
    suffix = path.suffix.casefold()
    routes = (
        ("prd", ("prd", "产品需求文档")),
        ("discovery", ("discovery", "research", "调研", "用户研究", "机会")),
        ("decisions", ("decision", "adr", "决策", "决定")),
        ("verification", ("verification", "validation", "acceptance", "test", "验收", "验证", "测试")),
        ("release", ("release", "deploy", "rollback", "发布", "上线", "回滚", "迁移手册")),
        ("design", ("design", "architecture", "ux", "设计", "架构")),
        ("requirements", ("requirement", "需求", "澄清", "执行计划")),
    )
    for category, terms in routes:
        if any(term in folded for term in terms):
            return category
    if suffix in {".html", ".htm", ".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        return "ui-previews"
    return "references"


def inferred_requirement_id(path: Path) -> str | None:
    match = REQUIREMENT_ID_RE.search(path.as_posix())
    return match.group(1).upper() if match else None


def legacy_roots(project_root: Path, explicit: Iterable[Path] = ()) -> list[Path]:
    root = project_root.resolve()
    requested = list(explicit)
    if requested:
        resolved = [ensure_within(path if path.is_absolute() else root / path, root, "legacy root") for path in requested]
    else:
        resolved = [
            path.resolve()
            for path in root.iterdir()
            if path.is_dir() and path.name.casefold() in LEGACY_ROOT_NAMES and path.name not in EXCLUDED_ROOTS
        ]
    invalid = [path for path in resolved if not path.is_dir()]
    if invalid:
        raise GovernanceError("legacy root is not a directory: " + ", ".join(map(str, invalid)))
    return sorted(set(resolved), key=str)


def migration_entries(project_root: Path, roots: Iterable[Path], default_requirement_id: str | None) -> list[dict[str, Any]]:
    project = project_root.resolve()
    entries: list[dict[str, Any]] = []
    targets: set[str] = set()
    for legacy_root in roots:
        for source in sorted((path for path in legacy_root.rglob("*") if path.is_file()), key=str):
            if source.suffix.casefold() not in DOCUMENT_EXTENSIONS:
                continue
            source_ref = source.relative_to(project).as_posix()
            category = document_type(source)
            requirement_id = inferred_requirement_id(source) or default_requirement_id
            relative_inside = source.relative_to(legacy_root).as_posix()
            if requirement_id:
                if not SAFE_ID_RE.fullmatch(requirement_id):
                    raise GovernanceError(f"invalid default RequirementID: {requirement_id!r}")
                target_ref = (
                    Path(DOCS_DIR) / "requirements" / requirement_id / category /
                    legacy_root.name / relative_inside
                ).as_posix()
            else:
                target_ref = (
                    Path(DOCS_DIR) / "_intake" / "unclassified" / category /
                    legacy_root.name / relative_inside
                ).as_posix()
            if target_ref in targets:
                raise GovernanceError(f"migration target collision: {target_ref}")
            targets.add(target_ref)
            entries.append({
                "source": source_ref,
                "sha256": sha256_file(source),
                "size": source.stat().st_size,
                "requirement_id": requirement_id,
                "document_type": category,
                "classification_basis": (
                    "path RequirementID or caller default plus deterministic filename/type routing"
                    if requirement_id
                    else "RequirementID unknown; routed fail-closed to intake"
                ),
                "target": target_ref,
            })
    return entries


def create_migration_plan(
    project_root: Path,
    *,
    migration_id: str,
    explicit_roots: Iterable[Path] = (),
    default_requirement_id: str | None = None,
) -> Path:
    if not SAFE_ID_RE.fullmatch(migration_id):
        raise GovernanceError(f"invalid MigrationID: {migration_id!r}")
    root = project_root.resolve()
    initialize_project_document_layout(root)
    roots = legacy_roots(root, explicit_roots)
    entries = migration_entries(root, roots, default_requirement_id)
    archive_root = root / DOCS_DIR / "_archive" / "legacy-migrations" / migration_id
    plan_path = archive_root / "migration-plan.json"
    if plan_path.exists():
        raise GovernanceError(f"migration plan already exists: {plan_path}")
    for entry in entries:
        entry["backup"] = (
            Path(DOCS_DIR) / "_archive" / "legacy-migrations" / migration_id /
            "original" / entry["source"]
        ).as_posix()
    body = {
        "schema_version": "1.0",
        "migration_id": migration_id,
        "project_root": str(root),
        "created_at": now_utc(),
        "legacy_roots": [path.relative_to(root).as_posix() for path in roots],
        "default_requirement_id": default_requirement_id,
        "entries": entries,
    }
    plan = {**body, "plan_digest": canonical_digest(body)}
    atomic_write_json(plan_path, plan)
    return plan_path


def validate_plan_document(plan: dict[str, Any]) -> None:
    digest = plan.get("plan_digest")
    body = {key: value for key, value in plan.items() if key != "plan_digest"}
    if not isinstance(digest, str) or digest != canonical_digest(body):
        raise GovernanceError("migration plan_digest is invalid")
    if not isinstance(plan.get("entries"), list):
        raise GovernanceError("migration entries must be an array")


def copy_verified(source: Path, target: Path, expected_sha256: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".lg-migration-tmp")
    if temporary.exists():
        raise GovernanceError(f"migration temporary target already exists: {temporary}")
    shutil.copy2(source, temporary)
    if sha256_file(temporary) != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise GovernanceError(f"migration copy hash mismatch: {target}")
    temporary.replace(target)


def apply_migration_plan(
    plan_path: Path,
    *,
    confirmed_plan_sha256: str,
    authorized_by: str,
) -> tuple[Path, Path]:
    resolved_plan = plan_path.resolve()
    if not re.fullmatch(r"[a-f0-9]{64}", confirmed_plan_sha256):
        raise GovernanceError("confirmed plan SHA-256 must be 64 lowercase hex characters")
    if sha256_file(resolved_plan) != confirmed_plan_sha256:
        raise GovernanceError("confirmed plan SHA-256 differs from the current migration plan")
    if not authorized_by.strip():
        raise GovernanceError("authorized_by is required")
    plan = read_json(resolved_plan)
    validate_plan_document(plan)
    root = Path(str(plan.get("project_root"))).resolve()
    ensure_within(resolved_plan, root, "migration plan")
    entries = plan["entries"]
    preflight: list[tuple[dict[str, Any], Path, Path, Path]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise GovernanceError("migration entry must be an object")
        source = ensure_within(root / str(entry.get("source")), root, "migration source")
        backup = ensure_within(root / str(entry.get("backup")), root, "migration backup")
        target = ensure_within(root / str(entry.get("target")), root, "migration target")
        expected = entry.get("sha256")
        if not source.is_file() or not isinstance(expected, str) or sha256_file(source) != expected:
            raise GovernanceError(f"migration source is missing or changed: {source}")
        if backup.exists() or target.exists():
            raise GovernanceError(f"migration destination already exists: {backup if backup.exists() else target}")
        preflight.append((entry, source, backup, target))
    for entry, source, backup, _ in preflight:
        copy_verified(source, backup, entry["sha256"])
    for entry, source, _, target in preflight:
        requirement_id = entry.get("requirement_id")
        if isinstance(requirement_id, str) and requirement_id:
            ensure_requirement_directory(root, requirement_id)
        copy_verified(source, target, entry["sha256"])
    for entry, source, backup, target in preflight:
        if sha256_file(backup) != entry["sha256"] or sha256_file(target) != entry["sha256"]:
            raise GovernanceError("verified migration copies changed before source removal")
        source.unlink()
    archive_root = resolved_plan.parent
    manifest_path = archive_root / "manifest.json"
    report_path = archive_root / "migration-report.md"
    manifest = {
        "schema_version": "1.0",
        "migration_id": plan["migration_id"],
        "applied_at": now_utc(),
        "authorized_by": authorized_by,
        "plan_ref": resolved_plan.relative_to(root).as_posix(),
        "plan_sha256": confirmed_plan_sha256,
        "files": [
            {
                "source": entry["source"],
                "backup": entry["backup"],
                "target": entry["target"],
                "sha256": entry["sha256"],
                "status": "BackedUpAndMoved",
            }
            for entry in entries
        ],
    }
    atomic_write_json(manifest_path, manifest)
    intake = [entry for entry in entries if not entry.get("requirement_id")]
    report_lines = [
        f"# 旧文档迁移报告：{plan['migration_id']}",
        "",
        f"- 应用时间：`{manifest['applied_at']}`",
        f"- 授权引用：`{authorized_by}`",
        f"- 计划 SHA-256：`{confirmed_plan_sha256}`",
        f"- 已备份并移动：{len(entries)} 个文件",
        f"- 待人工分类：{len(intake)} 个文件",
        "- 旧目录未递归删除；空目录可由项目维护者另行确认处理。",
        "",
        "## 文件",
        "",
        "| 原路径 | 备份 | 活动位置 | SHA-256 |",
        "|---|---|---|---|",
        *[
            f"| `{entry['source']}` | `{entry['backup']}` | `{entry['target']}` | `{entry['sha256']}` |"
            for entry in entries
        ],
        "",
    ]
    write_text(report_path, "\n".join(report_lines))
    refresh_project_readmes(root)
    return manifest_path, report_path


def is_package_root_document(relative: Path) -> bool:
    return len(relative.parts) == 1 and PACKAGE_DOC_RE.fullmatch(relative.name) is not None


def validate_docs_tree(project_root: Path) -> list[str]:
    root = project_root.resolve()
    docs = root / DOCS_DIR
    errors: list[str] = []
    if not (docs / "README.md").is_file():
        errors.append(f"missing {DOCS_DIR}/README.md")
        return errors
    requirements = docs / "requirements"
    if requirements.is_dir():
        project_readme = (docs / "README.md").read_text(encoding="utf-8")
        for requirement in sorted((path for path in requirements.iterdir() if path.is_dir()), key=str):
            readme = requirement / "README.md"
            if not readme.is_file():
                errors.append(f"missing requirement README: {readme.relative_to(root).as_posix()}")
                continue
            requirement_readme = readme.read_text(encoding="utf-8")
            for file_path in requirement.iterdir():
                if file_path.is_file() and file_path.name != "README.md":
                    errors.append(f"document is loose in requirement root: {file_path.relative_to(root).as_posix()}")
            for category in (path for path in requirement.iterdir() if path.is_dir()):
                if category.name not in STANDARD_TYPES and (
                    category.name not in requirement_readme or category.name not in project_readme
                ):
                    errors.append(
                        "custom document type is not recorded in both READMEs: "
                        + category.relative_to(root).as_posix()
                    )
    for file_path in docs.iterdir():
        if file_path.is_file() and file_path.name != "README.md":
            errors.append(f"document is loose in {DOCS_DIR} root: {file_path.relative_to(root).as_posix()}")
    return errors


def declared_document_errors(project_root: Path) -> list[str]:
    root = project_root.resolve()
    errors: list[str] = []
    tasks = root / GOVERNANCE_DIR / "tasks"
    if not tasks.is_dir():
        return errors
    for record_path in sorted(tasks.glob("*/*.json"), key=str):
        if record_path.name not in {"before.json", "after.json"}:
            continue
        try:
            record = read_json(record_path)
        except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError):
            continue
        for item in record.get("artifact_manifest", []):
            if not isinstance(item, dict):
                continue
            content_ref = item.get("content_ref")
            if not isinstance(content_ref, str) or "://" in content_ref:
                continue
            relative = Path(content_ref)
            if relative.suffix.casefold() not in DOCUMENT_EXTENSIONS:
                continue
            if relative.parts and relative.parts[0] in {GOVERNANCE_DIR, DOCS_DIR}:
                continue
            if is_package_root_document(relative):
                continue
            errors.append(
                f"declared native document is outside {DOCS_DIR}: {content_ref} ({record_path.name})"
            )
    return sorted(set(errors))


def validate_project_document_layout(project_root: Path) -> list[str]:
    root = project_root.resolve()
    errors: list[str] = []
    if not (root / GOVERNANCE_DIR / "README.md").is_file():
        errors.append(f"missing {GOVERNANCE_DIR}/README.md")
    errors.extend(validate_docs_tree(root))
    for child in root.iterdir():
        if child.is_dir() and child.name.casefold() in LEGACY_ROOT_NAMES and child.name not in EXCLUDED_ROOTS:
            if any(path.is_file() and path.suffix.casefold() in DOCUMENT_EXTENSIONS for path in child.rglob("*")):
                errors.append(f"legacy document directory requires migration: {child.relative_to(root).as_posix()}")
        elif child.is_file() and not is_package_root_document(child.relative_to(root)):
            if child.suffix.casefold() in DOCUMENT_EXTENSIONS and PRODUCT_DOC_RE.search(child.name):
                errors.append(f"product document is outside {DOCS_DIR}: {child.name}")
    errors.extend(declared_document_errors(root))
    return sorted(set(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "validate", "refresh-readme"):
        command = sub.add_parser(name)
        command.add_argument("--project-root", type=Path, default=Path.cwd())
    requirement = sub.add_parser("ensure-requirement")
    requirement.add_argument("--project-root", type=Path, default=Path.cwd())
    requirement.add_argument("--requirement-id", required=True)
    plan = sub.add_parser("plan-migration")
    plan.add_argument("--project-root", type=Path, default=Path.cwd())
    plan.add_argument("--migration-id", required=True)
    plan.add_argument("--legacy-root", type=Path, action="append", default=[])
    plan.add_argument("--default-requirement-id")
    apply = sub.add_parser("apply-migration")
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--confirm-plan-sha256", required=True)
    apply.add_argument("--authorized-by", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest_errors = validate_embedded_manifest()
        if manifest_errors:
            raise GovernanceError("Skill integrity check failed: " + "; ".join(manifest_errors))
        if args.command == "init":
            paths = initialize_project_document_layout(args.project_root)
            print(json.dumps({"status": "Initialized", "readmes": [str(path) for path in paths]}, ensure_ascii=False, indent=2))
        elif args.command == "ensure-requirement":
            print(ensure_requirement_directory(args.project_root, args.requirement_id))
        elif args.command == "refresh-readme":
            initialize_project_document_layout(args.project_root)
            refresh_project_readmes(args.project_root)
            print("README inventory refreshed")
        elif args.command == "validate":
            errors = validate_project_document_layout(args.project_root)
            if errors:
                print(json.dumps({"status": "Blocked", "errors": errors}, ensure_ascii=False, indent=2))
                return 3
            print(json.dumps({"status": "Valid", "errors": []}, ensure_ascii=False, indent=2))
        elif args.command == "plan-migration":
            path = create_migration_plan(
                args.project_root,
                migration_id=args.migration_id,
                explicit_roots=args.legacy_root,
                default_requirement_id=args.default_requirement_id,
            )
            print(json.dumps({
                "status": "Planned",
                "plan": str(path),
                "plan_sha256": sha256_file(path),
            }, ensure_ascii=False, indent=2))
        elif args.command == "apply-migration":
            manifest, report = apply_migration_plan(
                args.plan,
                confirmed_plan_sha256=args.confirm_plan_sha256,
                authorized_by=args.authorized_by,
            )
            print(json.dumps({
                "status": "Applied",
                "manifest": str(manifest),
                "report": str(report),
            }, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
