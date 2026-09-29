#!/usr/bin/env python3
"""Isolated end-to-end regression tests for the Bash and PowerShell installers."""

from __future__ import annotations

import os
import shutil
import select
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/LFenX/LFen-Skills.git"


def bash_executable() -> str | None:
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
        return str(git_bash) if git_bash.is_file() else None
    return shutil.which("bash")


def powershell_executable() -> str | None:
    if os.name != "nt":
        return None  # install.ps1 uses Windows junctions and USERPROFILE paths.
    return shutil.which("powershell.exe")


class InstallerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="lfenskills-installer-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.clone = self.home / ".lfenskills"
        self.source = self.tmp / "source"
        self.remote = self.tmp / "remote.git"
        self.git_config = self.tmp / "gitconfig"
        self.env = dict(
            os.environ,
            HOME=str(self.home),
            USERPROFILE=str(self.home),
            GIT_CONFIG_GLOBAL=str(self.git_config),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_ALLOW_PROTOCOL="file",
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="Installer Test",
            GIT_AUTHOR_EMAIL="installer@example.test",
            GIT_COMMITTER_NAME="Installer Test",
            GIT_COMMITTER_EMAIL="installer@example.test",
        )
        # Git's URL rewrite lets the installer use its production URL while every Git
        # operation stays local. GIT_ALLOW_PROTOCOL is a second network guard.
        self.git_config.write_text(
            f'[url "{self.remote.as_uri()}"]\n\tinsteadOf = {REPO_URL}\n',
            encoding="utf-8",
        )
        for name in ("demo", "other"):
            skill = self.source / "skills" / "examples" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
        self.git("init", "-q", str(self.source))
        self.git("-C", str(self.source), "add", ".")
        self.git("-C", str(self.source), "commit", "-q", "-m", "initial")
        self.git("clone", "-q", "--bare", str(self.source), str(self.remote))

    def tearDown(self) -> None:
        temp_root = Path(tempfile.gettempdir()).resolve()
        target = self.tmp.resolve()
        if target.parent != temp_root or not target.name.startswith("lfenskills-installer-"):
            raise RuntimeError(f"Refusing to delete unexpected test directory: {target}")
        # Git object files can be read-only on Windows.
        def force(function, path, _info) -> None:
            os.chmod(path, stat.S_IWRITE)
            function(path)

        if sys.version_info >= (3, 12):
            shutil.rmtree(self.tmp, onexc=force)
        else:
            shutil.rmtree(self.tmp, onerror=force)

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], env=self.env, check=True, capture_output=True, timeout=15)

    def clone_repo(self) -> None:
        self.git("clone", "-q", str(self.remote), str(self.clone))

    def run_bash(self, *args: str, pipeline: bool = False) -> subprocess.CompletedProcess[str]:
        executable = bash_executable()
        if executable is None:
            self.skipTest("Git Bash on Windows, or Bash on POSIX, is required")
        if pipeline:
            command = [executable, "-s", "--", *args]
            script = (ROOT / "install.sh").read_text(encoding="utf-8")
        else:
            command = [executable, str(ROOT / "install.sh"), *args]
            script = None
        return subprocess.run(
            command, input=script, text=True, encoding="utf-8", errors="replace",
            env=self.env, capture_output=True, timeout=20,
            start_new_session=(os.name != "nt" and pipeline),
        )

    def run_powershell(self, *args: str) -> subprocess.CompletedProcess[str]:
        executable = powershell_executable()
        if executable is None:
            self.skipTest("Windows PowerShell is required")
        return subprocess.run(
            [executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(ROOT / "install.ps1"), *args],
            text=True, encoding="utf-8", errors="replace", env=self.env,
            capture_output=True, timeout=25,
        )

    def run_powershell_scriptblock(self) -> subprocess.CompletedProcess[str]:
        executable = powershell_executable()
        if executable is None:
            self.skipTest("Windows PowerShell is required")
        env = dict(self.env, LFEN_INSTALLER_PATH=str(ROOT / "install.ps1"))
        command = (
            "& ([scriptblock]::Create((Get-Content -LiteralPath "
            "$env:LFEN_INSTALLER_PATH -Raw))) -Codex -Skill demo"
        )
        return subprocess.run(
            [executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-Command", command],
            text=True, encoding="utf-8", errors="replace", env=env,
            capture_output=True, timeout=25,
        )

    def seed_stale_other_link(self, platform: str = "codex") -> Path:
        stale = self.clone / "skills" / "old-location" / "other"
        stale.mkdir(parents=True)
        target_dir = self.home / f".{platform}" / "skills"
        target_dir.mkdir(parents=True)
        link = target_dir / "other"
        if os.name == "nt":
            import _winapi

            _winapi.CreateJunction(str(stale), str(link))
        else:
            os.symlink(stale, link, target_is_directory=True)
        self.assertTrue(os.path.samefile(link, stale))
        return stale

    def seed_blocking_real_directory(self) -> Path:
        directory = self.home / ".codex" / "skills" / "demo"
        directory.mkdir(parents=True)
        marker = directory / "keep.txt"
        marker.write_text("keep this directory\n", encoding="utf-8")
        return marker

    def assert_demo_installed(self) -> None:
        codex = self.home / ".codex" / "skills"
        self.assertTrue((codex / "demo" / "SKILL.md").is_file())
        self.assertFalse((self.home / ".claude" / "skills" / "demo").exists())

    def assert_demo_only(self) -> None:
        self.assert_demo_installed()
        self.assertFalse((self.home / ".codex" / "skills" / "other").exists())

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_non_git_install_directory_is_not_deleted(self) -> None:
        self.clone.mkdir()
        marker = self.clone / "user-data.txt"
        marker.write_text("keep me\n", encoding="utf-8")
        result = self.run_bash("--codex", "--skills", "demo")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep me\n")
        self.assertFalse((self.clone / ".git").exists())

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_pipeline_with_explicit_platform_and_skill_has_no_menu(self) -> None:
        self.clone_repo()
        stale = self.seed_stale_other_link()
        result = self.run_bash("--codex", "--skill", "demo", pipeline=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Enter choice", result.stdout)
        self.assert_demo_installed()
        self.assertTrue(os.path.samefile(self.home / ".codex" / "skills" / "other", stale))

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_pipeline_with_skills_filter_has_no_menu(self) -> None:
        self.clone_repo()
        result = self.run_bash("--codex", "--skills", "demo", pipeline=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Enter choice", result.stdout)
        self.assert_demo_only()

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_skills_filter_skips_unknown_name(self) -> None:
        self.clone_repo()
        result = self.run_bash("--codex", "--skills", "demo,absent", pipeline=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skipped", result.stdout)
        self.assertIn("absent", result.stdout)
        self.assert_demo_only()

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_skills_filter_with_no_valid_names_fails(self) -> None:
        self.clone_repo()
        result = self.run_bash("--codex", "--skills", "absent", pipeline=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        codex = self.home / ".codex" / "skills"
        self.assertEqual(list(codex.iterdir()) if codex.exists() else [], [])

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_real_directory_blocks_single_skill_install(self) -> None:
        self.clone_repo()
        marker = self.seed_blocking_real_directory()
        result = self.run_bash("--codex", "--skill", "demo", pipeline=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep this directory\n")
        self.assertNotIn("Done", result.stdout)

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_pipeline_without_choices_reports_terminal_requirement(self) -> None:
        result = self.run_bash(pipeline=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("requires a terminal", result.stderr)
        self.assertFalse(self.clone.exists())

    @unittest.skipUnless(os.name == "posix" and shutil.which("git") and bash_executable(),
                         "POSIX PTY, Git and Bash are required")
    def test_bash_pipeline_reads_menu_choices_from_controlling_terminal(self) -> None:
        import fcntl
        import pty
        import termios

        self.clone_repo()
        master_fd, slave_fd = pty.openpty()
        process = None

        def set_controlling_terminal() -> None:
            fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)

        try:
            process = subprocess.Popen(
                [bash_executable(), "-s"], stdin=subprocess.PIPE,
                stdout=slave_fd, stderr=slave_fd, env=self.env,
                start_new_session=True, preexec_fn=set_controlling_terminal,
            )
            os.close(slave_fd)
            slave_fd = -1
            assert process.stdin is not None
            process.stdin.write((ROOT / "install.sh").read_bytes())
            process.stdin.close()

            output = bytearray()
            platform_sent = False
            skill_sent = False
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                readable, _, _ = select.select([master_fd], [], [], 0.1)
                if readable:
                    try:
                        chunk = os.read(master_fd, 4096)
                    except OSError:  # PTY master reports EIO after the child closes its slave.
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
                    shown = output.decode("utf-8", errors="replace")
                    if not platform_sent and "Enter choice (1-8):" in shown:
                        os.write(master_fd, b"4\n")  # Codex
                        platform_sent = True
                    if not skill_sent and "Enter choice (number, comma-separated, or 'a'):" in shown:
                        os.write(master_fd, b"1\n")  # demo sorts before other
                        skill_sent = True
                if process.poll() is not None and not readable:
                    break
            else:
                self.fail("Interactive pipeline did not finish before timeout")

            process.wait(timeout=5)
            shown = output.decode("utf-8", errors="replace")
            self.assertTrue(platform_sent, shown)
            self.assertTrue(skill_sent, shown)
            self.assertEqual(process.returncode, 0, shown)
            self.assert_demo_only()
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            if slave_fd >= 0:
                os.close(slave_fd)
            os.close(master_fd)

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_unknown_single_skill_fails(self) -> None:
        self.clone_repo()
        result = self.run_bash("--codex", "--skill", "absent", pipeline=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.home / ".codex" / "skills" / "absent").exists())

    @unittest.skipUnless(shutil.which("git") and bash_executable(), "Git and Bash are required")
    def test_bash_update_with_single_skill_is_rejected_before_sync_or_repair(self) -> None:
        self.clone_repo()
        stale = self.seed_stale_other_link("claude")
        (self.source / "new-version.txt").write_text("remote change\n", encoding="utf-8")
        self.git("-C", str(self.source), "add", ".")
        self.git("-C", str(self.source), "commit", "-q", "-m", "remote change")
        self.git("-C", str(self.source), "push", "-q", str(self.remote), "HEAD")

        result = self.run_bash("--update", "--codex", "--skill", "demo", pipeline=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--skill is available in install mode only", result.stderr)
        self.assertFalse((self.clone / "new-version.txt").exists())
        self.assertTrue(os.path.samefile(self.home / ".claude" / "skills" / "other", stale))
        self.assertFalse((self.home / ".codex" / "skills" / "demo").exists())

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_pull_failure_is_fatal(self) -> None:
        self.clone_repo()
        self.git("-C", str(self.clone), "remote", "set-url", "origin", str(self.tmp / "missing.git"))
        result = self.run_powershell("-Codex", "-Skills", "demo")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Done. Restart", result.stdout)
        self.assertFalse((self.home / ".codex" / "skills" / "demo").exists())

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_single_skill_installs_only_requested_skill(self) -> None:
        self.clone_repo()
        stale = self.seed_stale_other_link()
        result = self.run_powershell("-Codex", "-Skill", "demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_demo_installed()
        self.assertTrue(os.path.samefile(self.home / ".codex" / "skills" / "other", stale))

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_scriptblock_entry_passes_single_skill_parameters(self) -> None:
        self.clone_repo()
        result = self.run_powershell_scriptblock()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_demo_only()

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_unknown_single_skill_fails(self) -> None:
        self.clone_repo()
        result = self.run_powershell("-Codex", "-Skill", "absent")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.home / ".codex" / "skills" / "absent").exists())

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_skills_filter_skips_unknown_name(self) -> None:
        self.clone_repo()
        result = self.run_powershell("-Codex", "-Skills", "demo,absent")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skipped", result.stdout)
        self.assertIn("absent", result.stdout)
        self.assert_demo_only()

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_skills_filter_with_no_valid_names_fails(self) -> None:
        self.clone_repo()
        result = self.run_powershell("-Codex", "-Skills", "absent")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        codex = self.home / ".codex" / "skills"
        self.assertEqual(list(codex.iterdir()) if codex.exists() else [], [])

    @unittest.skipUnless(shutil.which("git") and powershell_executable(), "Git and PowerShell are required")
    def test_powershell_real_directory_blocks_single_skill_install(self) -> None:
        self.clone_repo()
        marker = self.seed_blocking_real_directory()
        result = self.run_powershell("-Codex", "-Skill", "demo")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep this directory\n")
        self.assertNotIn("Done", result.stdout)


if __name__ == "__main__":
    unittest.main()
