#!/usr/bin/env python3
"""检查各 agent 的 skill 安装入口是否指向安装克隆里当前的 skill。

安装器把 skill 以 junction（Windows）或 symlink 链接到 ~/.lfenskills 克隆。这些入口在仓库之外，
CI 看不到；skill 目录一改名或移动，入口就可能悬空，agent 读到的仍是旧版本或什么也读不到。
本脚本直接读磁盘逐项核对，规则与 install.ps1、install.sh 的状态模式相同：

- catalog：安装克隆 skills/ 下所有含 SKILL.md 的目录（与 update_catalog.py 的发现规则一致）；
- 缺失：已装有 LFen skill（或用 --platform 点名）的平台上没有某个 catalog skill 的入口；
- 悬空：链接的目标不存在，不论这个链接是谁建的；
- 拷贝：与 catalog skill 同名的真实目录，不会随 git pull 更新；
- 指错：与 catalog skill 同名的链接没有指向安装克隆里的该 skill，
  或指进安装克隆的链接指向的不是 catalog skill。

有任何一项即以 1 退出。安装克隆是否落后远端只报告，不算缺陷。
"""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PLATFORMS = {
    "opencode": ".agents/skills",
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "copilot": ".copilot/skills",
    "windsurf": ".codeium/windsurf/skills",
}
LABELS = {"missing": "缺失", "dangling": "悬空", "copy": "拷贝", "wrong_target": "指错"}


@dataclass(frozen=True)
class Finding:
    platform: str
    kind: str
    name: str
    detail: str


@dataclass(frozen=True)
class PlatformReport:
    platform: str
    directory: Path
    exists: bool
    installed: bool
    ok: int
    findings: tuple[Finding, ...]


def is_link(path: Path) -> bool:
    """A symlink, or on Windows a junction -- which os.path.islink does not report."""

    if path.is_symlink():
        return True
    try:
        return os.lstat(path).st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT
    except (OSError, AttributeError):
        return False


def link_target(path: Path) -> Path:
    raw = os.readlink(path)
    if raw.startswith("\\\\?\\"):
        raw = raw[4:]
    target = Path(raw)
    return target if target.is_absolute() else path.parent / target


def _key(path: Path | str) -> str:
    return os.path.normcase(os.path.abspath(path))


def same_path(first: Path, second: Path) -> bool:
    return os.path.normcase(os.path.realpath(first)) == os.path.normcase(os.path.realpath(second))


def is_inside(path: Path, root: Path) -> bool:
    candidate = _key(path)
    return any(
        candidate.startswith(prefix.rstrip(os.sep) + os.sep)
        for prefix in {_key(root), os.path.normcase(os.path.realpath(root))}
    )


def discover_catalog(clone: Path) -> dict[str, Path]:
    """Every directory under <clone>/skills that holds a SKILL.md, by directory name."""

    catalog: dict[str, Path] = {}
    for skill_file in sorted((clone / "skills").rglob("SKILL.md"), key=lambda path: path.as_posix()):
        catalog.setdefault(skill_file.parent.name, skill_file.parent)
    return catalog


def inspect_platform(
    platform: str, directory: Path, catalog: dict[str, Path], skills_root: Path, require_all: bool = False
) -> PlatformReport:
    findings: list[Finding] = []
    present: set[str] = set()
    installed = False
    ok = 0
    exists = directory.is_dir()
    entries = sorted(directory.iterdir(), key=lambda path: path.name.lower()) if exists else []
    for entry in entries:
        name = entry.name
        if is_link(entry):
            target = link_target(entry)
            into_clone = is_inside(target, skills_root)
            if name in catalog:
                present.add(name)
            installed = installed or name in catalog or into_clone
            if not os.path.exists(target):
                findings.append(Finding(platform, "dangling", name, f"-> {target}"))
            elif name in catalog:
                if same_path(target, catalog[name]):
                    ok += 1
                else:
                    findings.append(Finding(platform, "wrong_target", name, f"-> {target}，应为 {catalog[name]}"))
            elif into_clone:
                findings.append(Finding(platform, "wrong_target", name, f"-> {target}，不是 catalog 里的 skill"))
        elif entry.is_dir() and name in catalog:
            present.add(name)
            installed = True
            findings.append(Finding(platform, "copy", name, "真实目录，不会随 git pull 更新"))
    if installed or require_all:
        findings.extend(
            Finding(platform, "missing", name, f"应链接到 {catalog[name]}")
            for name in sorted(set(catalog) - present)
        )
    return PlatformReport(platform, directory, exists, installed, ok, tuple(findings))


def clone_status(clone: Path, fetch: bool) -> str:
    def git(*args: str) -> subprocess.CompletedProcess[str] | None:
        try:
            return subprocess.run(
                ["git", "-C", str(clone), *args], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None

    head = git("rev-parse", "--short", "HEAD")
    if head is None or head.returncode != 0:
        return "不是 git 克隆，无法判断是否落后远端"
    notes = []
    if fetch:
        fetched = git("fetch", "--quiet")
        if fetched is None or fetched.returncode != 0:
            notes.append("fetch 失败，按上次获取的远端状态判断")
    else:
        notes.append("未 fetch，按上次获取的远端状态判断")
    dirty = git("status", "--porcelain")
    if dirty is not None and dirty.returncode == 0 and dirty.stdout.strip():
        notes.append("有本地改动，agent 读到的不是远端版本")
    counts = git("rev-list", "--left-right", "--count", "HEAD...@{upstream}")
    suffix = "".join(f"；{note}" for note in notes)
    if counts is None or counts.returncode != 0:
        return f"HEAD {head.stdout.strip()}，没有上游分支，无法判断是否落后远端{suffix}"
    ahead, behind = (int(value) for value in counts.stdout.split())
    if behind:
        state = f"落后远端 {behind} 个提交；运行 git -C {clone} pull 更新"
    else:
        state = "与远端一致"
    if ahead:
        state += f"，另有 {ahead} 个未推送的本地提交"
    return f"HEAD {head.stdout.strip()}，{state}{suffix}"


def check(home: Path, clone: Path, platforms: list[str] | None, fetch: bool) -> tuple[list[str], int]:
    """Return the report lines and the exit code (0 clean, 1 defects, 2 unusable clone)."""

    catalog = discover_catalog(clone)
    if not catalog:
        return [f"安装克隆 {clone} 不存在或没有任何 SKILL.md；先运行 install.ps1 或 install.sh 安装"], 2
    lines = [f"安装克隆：{clone}（{len(catalog)} 个 skill，{clone_status(clone, fetch)}）"]
    total = 0
    for key in platforms or list(PLATFORMS):
        report = inspect_platform(key, home / PLATFORMS[key], catalog, clone / "skills", require_all=platforms is not None)
        if not report.exists and not report.findings:
            lines.append(f"[{key}] {report.directory}：目录不存在")
            continue
        if not report.installed and not report.findings:
            lines.append(f"[{key}] {report.directory}：未安装 LFen skill")
            continue
        summary = f"{report.ok} 个正常" + (f"，{len(report.findings)} 项问题" if report.findings else "")
        lines.append(f"[{key}] {report.directory}：{summary}")
        lines.extend(f"  {LABELS[item.kind]}  {item.name} {item.detail}" for item in report.findings)
        total += len(report.findings)
    lines.append(f"共 {total} 项问题。" if total else "没有发现问题。")
    return lines, 1 if total else 0


def entries_pointing_at(home: Path, relative_dirs: list[str]) -> list[str]:
    """Entries on any platform whose link target ends with one of the given skills/... paths."""

    suffixes = [os.path.normcase(os.path.normpath(value)) for value in relative_dirs]
    found = []
    for key, relative in PLATFORMS.items():
        directory = home / relative
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir(), key=lambda path: path.name.lower()):
            if not is_link(entry):
                continue
            target = link_target(entry)
            normalized = os.path.normcase(os.path.normpath(str(target)))
            if any(normalized.endswith(os.sep + suffix) for suffix in suffixes):
                found.append(f"[{key}] {entry} -> {target}")
    return found


def move_reminder(old_paths: dict[str, str], new_paths: dict[str, str], home: Path, clone: Path) -> list[str]:
    """What update_catalog.py prints when a skill directory moved or disappeared; empty otherwise."""

    moved = {name: (old_paths[name], new_paths[name]) for name in old_paths
             if name in new_paths and old_paths[name] != new_paths[name]}
    removed = {name: path for name, path in old_paths.items() if name not in new_paths}
    if not moved and not removed:
        return []
    lines = ["提醒：skill 目录有移动或改名，各 agent 的安装入口可能因此悬空或指错。"]
    lines.extend(f"  移动  {name}：{old} -> {new}" for name, (old, new) in sorted(moved.items()))
    lines.extend(f"  移除或改名  {name}：{old}" for name, old in sorted(removed.items()))
    lines.extend(f"  新增  {name}：{path}" for name, path in sorted(new_paths.items()) if name not in old_paths)
    lines.append(
        "  推送后在每台机器上运行 git -C ~/.lfenskills pull，再运行 install.ps1 -Update 或 bash install.sh --update"
        "（会重新链接并清掉悬空入口），最后运行 python scripts/check_install_links.py 确认。"
    )
    stale = entries_pointing_at(home, [old for old, _ in moved.values()] + list(removed.values()))
    if stale:
        lines.append("  以下入口仍指向旧位置：")
        lines.extend(f"    {item}" for item in stale)
    if (clone / "skills").is_dir():
        report, _ = check(home, clone, None, fetch=False)
        lines.append("  当前安装入口检查：")
        lines.extend(f"    {item}" for item in report)
    else:
        lines.append(f"  未找到安装克隆 {clone}，跳过安装入口检查。")
    return lines


def parse_platforms(values: list[str]) -> list[str] | None:
    if not values:
        return None
    keys = [item.strip() for value in values for item in value.split(",") if item.strip()]
    unknown = sorted(set(keys) - set(PLATFORMS))
    if unknown:
        raise SystemExit(f"未知平台：{', '.join(unknown)}；可选 {', '.join(PLATFORMS)}")
    return list(dict.fromkeys(keys))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查各 agent 的 skill 安装入口是否指向安装克隆里当前的 skill")
    parser.add_argument("--clone", type=Path, default=Path.home() / ".lfenskills", help="安装克隆，默认 ~/.lfenskills")
    parser.add_argument("--home", type=Path, default=Path.home(), help="各平台 skill 目录所在的家目录，默认当前用户")
    parser.add_argument(
        "--platform", action="append", default=[],
        help=f"只检查这些平台并要求每个 catalog skill 都有入口，可重复或用逗号分隔：{', '.join(PLATFORMS)}",
    )
    parser.add_argument("--no-fetch", action="store_true", help="不访问远端，按上次获取的远端状态报告是否落后")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    lines, code = check(args.home, args.clone, parse_platforms(args.platform), fetch=not args.no_fetch)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
