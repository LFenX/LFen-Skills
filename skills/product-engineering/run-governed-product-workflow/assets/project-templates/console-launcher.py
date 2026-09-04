#!/usr/bin/env python3
"""Governance console for this project.

This is the launcher. It is a real, runnable entry point that belongs to this
project, not a copy of a tool that lives somewhere else: it finds its own project
root from where it sits, so it takes no path arguments.

    python .project-governance/console/console.py start
    python .project-governance/console/console.py status
    python .project-governance/console/console.py stop
    python .project-governance/console/console.py verify

The console code itself is a pinned snapshot under snapshot/, deployed by
run-governed-product-workflow when this project's governance directory was created.
The snapshot is what makes the console outlive the Skill: upgrading, uninstalling
or moving the Skill does not change what this console does, and the console can
still be rebuilt years from now exactly as it ran today.

Every page reads only this project's own files, with one exception. The integrity
page audits the Skill's protected assets, so it needs the Skill to be reachable;
when it is not, that page says the check did not run rather than reporting a clean
result. See README.md in this directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent           # <project>/.project-governance/console/
SNAPSHOT = HERE / "snapshot"
DEPLOYMENT = HERE / "deployment.json"
SKILL_ROOT_ENV = "LG_SKILL_ROOT"


def load_deployment() -> dict:
    try:
        return json.loads(DEPLOYMENT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def is_skill_root(candidate: Path) -> bool:
    return (candidate / "assets" / "runtime" / "embedded-manifest.json").is_file()


def resolve_skill_root(deployment: dict) -> Path | None:
    """Find the Skill this console came from, for the integrity page only.

    An explicit environment variable wins so a moved or reinstalled Skill can be
    pointed at without editing the deployment record.
    """

    for raw in (os.environ.get(SKILL_ROOT_ENV, "").strip(), deployment.get("skill_root", "")):
        if not raw:
            continue
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = (PROJECT_ROOT / candidate)
        candidate = candidate.resolve()
        if is_skill_root(candidate):
            return candidate
    return None


def snapshot_drift(deployment: dict) -> list[str]:
    """Report snapshot files that no longer match what was deployed."""

    problems: list[str] = []
    recorded = deployment.get("snapshot", {})
    if not recorded:
        return ["deployment.json 没有记录快照哈希，无法判断是否被改动"]
    for name, expected in sorted(recorded.items()):
        path = SNAPSHOT / name
        if not path.is_file():
            problems.append(f"缺失：{name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(f"已改动：{name}")
    extra = {p.name for p in SNAPSHOT.glob("*.py")} - set(recorded)
    problems.extend(f"未登记：{name}" for name in sorted(extra))
    return problems


def command_verify(deployment: dict, skill_root: Path | None) -> int:
    print(f"项目根      : {PROJECT_ROOT}")
    print(f"装配于      : {deployment.get('deployed_at', '未知')}")
    print(f"来源 skill  : {deployment.get('skill_name', '未知')} {deployment.get('skill_version', '')}")
    print(f"记录的路径  : {deployment.get('skill_root', '未记录')}")
    print(f"当前可达    : {skill_root or '否 —— 完整性页将显示「无法核对」，其余页面不受影响'}")
    problems = snapshot_drift(deployment)
    if problems:
        print(f"\n快照与装配记录不一致（{len(problems)} 处）：")
        for problem in problems:
            print(f"  - {problem}")
        print("\n重新装配可恢复：在 skill 侧运行 deploy_console.py --project-root <本项目> --force")
        return 1
    print(f"\n快照完整：{len(deployment.get('snapshot', {}))} 个文件与装配记录逐一相符")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    deployment = load_deployment()
    skill_root = resolve_skill_root(deployment)

    if argv and argv[0] == "verify":
        return command_verify(deployment, skill_root)

    if not SNAPSHOT.is_dir():
        print(f"控制台快照缺失：{SNAPSHOT}", file=sys.stderr)
        print("在 skill 侧运行 deploy_console.py --project-root <本项目> 重新装配。", file=sys.stderr)
        return 2

    drift = snapshot_drift(deployment)
    if drift:
        print(f"警告：控制台快照有 {len(drift)} 处与装配记录不符，运行 `console.py verify` 查看。", file=sys.stderr)

    # The Skill is passed through the environment rather than patched in, because
    # `start` detaches a child process that would not inherit an in-process patch.
    if skill_root is not None:
        os.environ[SKILL_ROOT_ENV] = str(skill_root)

    sys.path.insert(0, str(SNAPSHOT))
    sys.dont_write_bytecode = True
    import console  # noqa: PLC0415 - the snapshot is only importable once located

    # This launcher lives inside the project it serves, so the project root is never
    # something the operator should have to supply.
    if argv and not argv[0].startswith("-") and "--project-root" not in argv:
        argv = [argv[0], "--project-root", str(PROJECT_ROOT), *argv[1:]]
    sys.argv = ["console.py", *argv]
    return console.main()


if __name__ == "__main__":
    raise SystemExit(main())
