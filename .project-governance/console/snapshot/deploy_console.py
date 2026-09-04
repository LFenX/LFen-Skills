#!/usr/bin/env python3
"""Deploy the governance console into a project as a pinned snapshot.

The console in this Skill is a template. The runnable console belongs to the
project it audits: it is deployed under `.project-governance/console/` when the
project's governance directory is created, and from then on it is the project's
own tool. Upgrading, moving or uninstalling this Skill does not change what a
deployed console does.

The snapshot is copied byte for byte and its SHA-256 recorded, for the same reason
this Skill snapshots the norms it works from: a tool that audits records has to be
able to say exactly which version produced a given view, and has to make later
tampering visible rather than silent.

    deploy_console.py --project-root <project-root>
    deploy_console.py --project-root <project-root> --force
    deploy_console.py --project-root <project-root> --check
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, skill_root_path

CONSOLE_DIR = "console"
LAUNCHER_TEMPLATE = "console-launcher.py"
README_TEMPLATE = "console.README.md"

# The console's full import closure, declared rather than computed so the deployed
# set is auditable and stable. self_test holds this list against the real closure,
# so it cannot drift silently as the console gains or drops an import.
SNAPSHOT_MODULES = (
    "audit_console.py",
    "console.py",
    "console_assets.py",
    "console_model.py",
    "console_render.py",
    "deploy_console.py",
    "governance_artifacts.py",
    "manage_project_docs.py",
    "minimal_task.py",
)

# Roots of the closure: what a console deployment must be able to run.
CONSOLE_ENTRY_MODULES = ("console", "console_model", "console_render", "console_assets")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def computed_closure(scripts_dir: Path) -> tuple[str, ...]:
    """Resolve the console's real import closure from the source itself."""

    local = {path.stem for path in scripts_dir.glob("*.py")}

    def local_imports(module: str) -> set[str]:
        tree = ast.parse((scripts_dir / f"{module}.py").read_text(encoding="utf-8"))
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                found.add(node.module.split(".")[0])
        return {name for name in found if name in local}

    closure = set(CONSOLE_ENTRY_MODULES)
    frontier = list(CONSOLE_ENTRY_MODULES)
    while frontier:
        for dependency in local_imports(frontier.pop()):
            if dependency not in closure:
                closure.add(dependency)
                frontier.append(dependency)
    return tuple(sorted(f"{name}.py" for name in closure))


def skill_version(skill_root: Path) -> str:
    """Read the version out of SKILL.md front matter."""

    try:
        for line in (skill_root / "SKILL.md").read_text(encoding="utf-8").splitlines()[:20]:
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return "unknown"


def console_dir(project_root: Path) -> Path:
    from manage_project_docs import GOVERNANCE_DIR

    return project_root.resolve() / GOVERNANCE_DIR / CONSOLE_DIR


def read_deployment(project_root: Path) -> dict:
    path = console_dir(project_root) / "deployment.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def current_sources(skill_root: Path) -> dict[str, bytes]:
    scripts = skill_root / "scripts"
    sources: dict[str, bytes] = {}
    for name in SNAPSHOT_MODULES:
        path = scripts / name
        if not path.is_file():
            raise GovernanceError(f"console snapshot source is missing: {path}")
        sources[name] = path.read_bytes()
    return sources


def deployment_status(project_root: Path, skill_root: Path) -> dict:
    """Compare what the project has against what this Skill would deploy now."""

    deployment = read_deployment(project_root)
    recorded = deployment.get("snapshot", {})
    target = console_dir(project_root)
    sources = current_sources(skill_root)
    latest = {name: sha256_bytes(payload) for name, payload in sources.items()}

    on_disk: dict[str, str] = {}
    for name in SNAPSHOT_MODULES:
        path = target / "snapshot" / name
        if path.is_file():
            on_disk[name] = sha256_bytes(path.read_bytes())

    return {
        "deployed": bool(deployment) and target.is_dir(),
        "deployed_version": deployment.get("skill_version", ""),
        "skill_version": skill_version(skill_root),
        "missing": [name for name in SNAPSHOT_MODULES if name not in on_disk],
        # Changed since it was deployed here: local tampering.
        "modified": sorted(name for name, digest in on_disk.items()
                           if name in recorded and digest != recorded[name]),
        # Differs from what this Skill holds now: the Skill moved on.
        "outdated": sorted(name for name, digest in on_disk.items() if latest.get(name) != digest),
    }


def deploy(project_root: Path, *, skill_root: Path | None = None, force: bool = False) -> bool:
    """Materialize the launcher, the snapshot and the docs. Returns True if written."""

    from manage_project_docs import copy_template_if_absent, replace_managed_section

    root = project_root.resolve()
    skill = (skill_root or skill_root_path()).resolve()
    target = console_dir(root)
    status = deployment_status(root, skill)

    # Already deployed and byte-identical to this Skill: nothing to do. Staying quiet
    # here is what lets the deploy hook run on every project init without churn.
    if status["deployed"] and not status["missing"] and not status["outdated"] and not force:
        refresh_console_readme(root)
        return False

    sources = current_sources(skill)
    snapshot = target / "snapshot"
    snapshot.mkdir(parents=True, exist_ok=True)
    for name, payload in sources.items():
        # Byte-wise: these files legitimately contain CRLF, and a text-mode round
        # trip would rewrite line endings and break every recorded hash.
        (snapshot / name).write_bytes(payload)

    launcher_bytes = (skill / "assets" / "project-templates" / LAUNCHER_TEMPLATE).read_bytes()
    (target / "console.py").write_bytes(launcher_bytes)
    copy_template_if_absent(target / "README.md", README_TEMPLATE)

    deployment = {
        "deployed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill_name": skill.name,
        "skill_version": skill_version(skill),
        "skill_root": str(skill),
        "launcher_sha256": sha256_bytes(launcher_bytes),
        "snapshot": {name: sha256_bytes(payload) for name, payload in sorted(sources.items())},
        "note": "snapshot 为逐字节固定的控制台代码；skill_root 仅用于完整性页，可被 LG_SKILL_ROOT 覆盖。",
    }
    (target / "deployment.json").write_text(
        json.dumps(deployment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    replace_managed_section(target / "README.md", _readme_lines(deployment))
    return True


def refresh_console_readme(project_root: Path) -> None:
    from manage_project_docs import replace_managed_section

    target = console_dir(project_root)
    if (target / "README.md").is_file():
        replace_managed_section(target / "README.md", _readme_lines(read_deployment(project_root)))


def _readme_lines(deployment: dict) -> list[str]:
    if not deployment:
        return ["尚未装配。"]
    return [
        f"- 装配时间：`{deployment.get('deployed_at', '未知')}`",
        f"- 来源 skill：`{deployment.get('skill_name', '未知')}` 版本 `{deployment.get('skill_version', '未知')}`",
        f"- 装配时的 skill 路径：`{deployment.get('skill_root', '未记录')}`",
        f"- 快照文件：{len(deployment.get('snapshot', {}))} 个，哈希记录于 `deployment.json`",
        "- 核对快照是否被改动：`python .project-governance/console/console.py verify`",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="把治理控制台装配进项目")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--force", action="store_true", help="即使已是最新也重新写入")
    parser.add_argument("--check", action="store_true", help="只报告状态，不写入")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    skill = skill_root_path()
    if not (root / ".project-governance").is_dir():
        print(f"项目尚未建立治理目录：{root}", file=sys.stderr)
        return 2

    status = deployment_status(root, skill)
    if args.check:
        print(f"已装配      : {'是' if status['deployed'] else '否'}")
        print(f"装配版本    : {status['deployed_version'] or '—'}")
        print(f"当前 skill  : {status['skill_version']}")
        for key, label in (("missing", "缺失"), ("modified", "被改动"), ("outdated", "已过期")):
            if status[key]:
                print(f"{label:<12}: {', '.join(status[key])}")
        if not status["deployed"]:
            return 1
        return 1 if (status["missing"] or status["modified"] or status["outdated"]) else 0

    written = deploy(root, skill_root=skill, force=args.force)
    target = console_dir(root)
    if written:
        print(f"控制台已装配：{target}")
        print(f"启动： python {(target / 'console.py').relative_to(root)} start")
    else:
        print(f"控制台已是最新，无需改动：{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
