#!/usr/bin/env python3
"""Tests for check_install_links.py: every finding kind, the clean case, clone freshness and the move reminder."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_install_links as checker  # noqa: E402


def make_link(link: Path, target: Path) -> None:
    """A junction on Windows (what install.ps1 creates), a symlink elsewhere."""

    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def make_dangling(link: Path, target: Path) -> None:
    target.mkdir(parents=True)
    make_link(link, target)
    shutil.rmtree(target)


def add_skill(root: Path, category: str, name: str) -> Path:
    directory = root / "skills" / category / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    return directory


class InstallLinksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.clone = self.home / ".lfenskills"
        self.alpha = add_skill(self.clone, "data", "alpha")
        self.beta = add_skill(self.clone, "tools", "beta")
        (self.clone / "skills" / "tools" / "notes").mkdir()  # no SKILL.md: not a skill

    def tearDown(self) -> None:
        # rmtree removes links without following them, junctions included (3.8+); git leaves
        # its object files read-only, which Windows refuses to delete until the bit is cleared.
        def force(function, path, _info) -> None:
            os.chmod(path, stat.S_IWRITE)
            function(path)

        if sys.version_info >= (3, 12):
            shutil.rmtree(self.tmp, onexc=force)
        else:
            shutil.rmtree(self.tmp, onerror=force)

    def platform_dir(self, key: str) -> Path:
        directory = self.home / checker.PLATFORMS[key]
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def kinds(self, key: str, require_all: bool = False) -> dict[str, str]:
        report = checker.inspect_platform(
            key, self.home / checker.PLATFORMS[key], checker.discover_catalog(self.clone),
            self.clone / "skills", require_all,
        )
        return {item.name: item.kind for item in report.findings}

    def test_catalog_is_directories_with_skill_md(self) -> None:
        self.assertEqual(set(checker.discover_catalog(self.clone)), {"alpha", "beta"})

    def test_clean_install_and_foreign_entries_report_nothing(self) -> None:
        claude = self.platform_dir("claude")
        make_link(claude / "alpha", self.alpha)
        make_link(claude / "beta", self.beta)
        codex = self.platform_dir("codex")
        make_link(codex / "alpha", self.alpha)
        make_link(codex / "beta", self.beta)
        (codex / "hatch-pet").mkdir()
        elsewhere = self.tmp / "elsewhere" / "tool"
        elsewhere.mkdir(parents=True)
        make_link(codex / "tool", elsewhere)
        lines, code = checker.check(self.home, self.clone, None, fetch=False)
        self.assertEqual(code, 0, "\n".join(lines))
        self.assertIn("没有发现问题。", lines)

    def test_each_defect_kind_is_reported(self) -> None:
        dev_repo = self.tmp / "dev" / "LFen-Skills"
        dev_alpha = add_skill(dev_repo, "data", "alpha")
        claude = self.platform_dir("claude")
        make_link(claude / "alpha", dev_alpha)  # points at the dev repo instead of the clone
        make_dangling(claude / "old-name", self.clone / "skills" / "tools" / "old-name")
        make_link(claude / "notes", self.clone / "skills" / "tools" / "notes")
        codex = self.platform_dir("codex")
        shutil.copytree(self.alpha, codex / "alpha")
        make_link(codex / "beta", self.beta)
        make_dangling(codex / "foreign", self.tmp / "gone" / "foreign")
        self.assertEqual(
            self.kinds("claude"),
            {"alpha": "wrong_target", "old-name": "dangling", "notes": "wrong_target", "beta": "missing"},
        )
        self.assertEqual(self.kinds("codex"), {"alpha": "copy", "foreign": "dangling"})
        lines, code = checker.check(self.home, self.clone, None, fetch=False)
        self.assertEqual(code, 1)
        self.assertIn("共 6 项问题。", lines)

    def test_platform_without_lfen_entries_is_required_only_when_named(self) -> None:
        gemini = self.platform_dir("gemini")
        (gemini / "someone-else").mkdir()
        self.assertEqual(self.kinds("gemini"), {})
        self.assertEqual(self.kinds("gemini", require_all=True), {"alpha": "missing", "beta": "missing"})
        _, code = checker.check(self.home, self.clone, ["gemini"], fetch=False)
        self.assertEqual(code, 1)
        lines, code = checker.check(self.home, self.clone, ["cursor"], fetch=False)
        self.assertEqual(code, 1, "a named platform without its directory is missing every skill")

    def test_missing_clone_is_a_usage_error(self) -> None:
        lines, code = checker.check(self.home, self.tmp / "nowhere", None, fetch=False)
        self.assertEqual(code, 2)

    def test_unknown_platform_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            checker.parse_platforms(["claude,nope"])
        self.assertEqual(checker.parse_platforms(["claude,codex", "claude"]), ["claude", "codex"])

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_clone_status_reports_commits_behind_the_remote(self) -> None:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")

        def git(*args: str) -> None:
            subprocess.run(["git", *args], check=True, capture_output=True, env=env)

        source = self.tmp / "source"
        add_skill(source, "data", "alpha")
        git("init", "-q", str(source))
        git("-C", str(source), "add", ".")
        git("-C", str(source), "commit", "-q", "-m", "first")
        remote = self.tmp / "remote.git"
        git("clone", "-q", "--bare", str(source), str(remote))
        clone = self.tmp / "clone"
        git("clone", "-q", str(remote), str(clone))
        self.assertIn("与远端一致", checker.clone_status(clone, fetch=True))
        (source / "README.md").write_text("more\n", encoding="utf-8")
        git("-C", str(source), "add", ".")
        git("-C", str(source), "commit", "-q", "-m", "second")
        git("-C", str(source), "push", "-q", str(remote), "HEAD")
        self.assertIn("落后远端 1 个提交", checker.clone_status(clone, fetch=True))

    def test_move_reminder_names_moves_and_stale_entries(self) -> None:
        dev_repo = self.tmp / "dev" / "LFen-Skills"
        old_location = add_skill(dev_repo, "data", "alpha")
        claude = self.platform_dir("claude")
        make_link(claude / "alpha", old_location)
        make_link(claude / "beta", self.beta)
        old = {"alpha": "skills/data/alpha", "beta": "skills/tools/beta", "gone": "skills/tools/gone"}
        new = {"alpha": "skills/analysis/alpha", "beta": "skills/tools/beta", "fresh": "skills/tools/fresh"}
        text = "\n".join(checker.move_reminder(old, new, self.home, self.clone))
        self.assertIn("移动  alpha：skills/data/alpha -> skills/analysis/alpha", text)
        self.assertIn("移除或改名  gone：skills/tools/gone", text)
        self.assertIn("新增  fresh：skills/tools/fresh", text)
        self.assertIn(str(claude / "alpha"), text)
        self.assertIn("当前安装入口检查：", text)
        self.assertEqual(checker.move_reminder(old, dict(old), self.home, self.clone), [])

    def test_update_catalog_reminds_only_when_a_skill_moved(self) -> None:
        import update_catalog

        index = self.tmp / "index.json"
        index.write_text('{"skills": [{"name": "alpha", "path": "skills/data/alpha/SKILL.md"}]}', encoding="utf-8")
        self.assertEqual(update_catalog.indexed_skill_paths(index), {"alpha": "skills/data/alpha"})
        index.write_text("not json", encoding="utf-8")
        self.assertEqual(update_catalog.indexed_skill_paths(index), {})
        old = {"alpha": "skills/data/alpha", "beta": "skills/tools/beta"}
        self.assertEqual(update_catalog.install_entry_reminder(old, dict(old, fresh="skills/tools/fresh")), [])
        with mock.patch.object(Path, "home", return_value=self.home):
            lines = update_catalog.install_entry_reminder(old, {"alpha": "skills/analysis/alpha"})
        text = "\n".join(lines)
        self.assertIn("移动  alpha：skills/data/alpha -> skills/analysis/alpha", text)
        self.assertIn("移除或改名  beta：skills/tools/beta", text)


class InstallerSourceTest(unittest.TestCase):
    def test_single_skill_selection_is_kept_as_an_array(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "install.ps1").read_text(encoding="ascii")
        self.assertIn(
            "$selectedSkills = @($selectedSkillIdx | ForEach-Object { $skillMenu[$_] })",
            text,
        )

    def test_install_ps1_stays_ascii_without_a_bom(self) -> None:
        # Windows PowerShell 5.1 reads a script without a BOM in the system code page (GBK on
        # Chinese Windows), where UTF-8 bytes swallow quotes and the script no longer parses;
        # a BOM would fix that but breaks `iwr ... | iex`.
        data = (Path(__file__).resolve().parents[1] / "install.ps1").read_bytes()
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
        offenders = [number for number, line in enumerate(data.splitlines(), 1) if any(byte > 127 for byte in line)]
        self.assertEqual(offenders, [], "install.ps1 lines with non-ASCII bytes")


if __name__ == "__main__":
    unittest.main()
