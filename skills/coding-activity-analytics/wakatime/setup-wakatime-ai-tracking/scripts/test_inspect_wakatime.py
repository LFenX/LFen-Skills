"""Isolated tests: no real keys, network calls, configuration writes, or heartbeats."""

import json
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import inspect_wakatime as inspect


class ReadOnlyDiagnosticsTest(unittest.TestCase):
    def test_invalid_arguments_do_not_echo_sensitive_values(self):
        secret = "private-value-pasted-into-wrong-argument"
        output = io.StringIO()
        with mock.patch("sys.argv", ["inspect_wakatime.py", "--unexpected", secret]), contextlib.redirect_stderr(output):
            with self.assertRaises(SystemExit) as error:
                inspect.main()
        self.assertEqual(error.exception.code, 2)
        self.assertNotIn(secret, output.getvalue())
        self.assertIn("argument_error", output.getvalue())

    def test_empty_legacy_file_has_priority_over_xdg(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            legacy = home / ".wakatime.cfg"
            legacy.touch()
            self.assertEqual(inspect.select_config(home, {"XDG_CONFIG_HOME": str(home / "xdg")}), legacy)

    def test_explicit_and_wakatime_home_config_priority(self):
        home = Path("home")
        env = {"WAKATIME_HOME": "custom"}
        self.assertEqual(inspect.select_config(home, env), Path("custom/.wakatime.cfg"))
        self.assertEqual(inspect.select_config(home, env, Path("chosen")), Path("chosen"))

    def test_secret_and_private_fields_do_not_escape_summary(self):
        secret = "synthetic-secret-for-isolated-test"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.ini"
            original = "[settings]\napi_key = " + secret + "\nhostname = private-host\n[projectmap]\nprivate-project-path = private-project-name\n"
            path.write_text(original, encoding="utf-8")
            summary, secrets = inspect.config_summary(path)
            rows = [{"type": "file", "language": "Python", "user_agent": "gpt/6.1-sol-max opencode/1.0", "entity": "private-file", "project": "private-project-name"}]
            report = json.dumps([summary, inspect.queue_summary(rows, secrets)])
            for forbidden in [secret, "private-host", "private-project-path", "private-project-name", "private-file"]:
                self.assertNotIn(forbidden, report)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertTrue(summary["api_key_in_selected_config"])

    def test_queue_formats_and_invalid_input(self):
        row = {"type": "app", "language": None, "user_agent": "deepseek/4-pro grok-bot/1.0"}
        for raw in [json.dumps([row]), json.dumps(row), json.dumps({"heartbeats": [row]}), json.dumps(row) + "\n" + json.dumps(row)]:
            self.assertGreaterEqual(len(inspect.parse_queue(raw)), 1)
        for raw in ["private invalid content", '[{"type":"file"}', '42', '{"unexpected":"value"}']:
            with self.assertRaisesRegex(inspect.ProbeError, "queue_format_invalid"):
                inspect.parse_queue(raw)

    def test_app_without_language_and_model_version_remain_distinct(self):
        rows = [{"type": "app", "language": None, "user_agent": "gpt/6.1-sol-max codex-vscode/0.154.0"}, {"type": "file", "language": "Go", "user_agent": "deepseek/4-flash opencode/1.18"}]
        result = inspect.queue_summary(rows, set())
        self.assertEqual(result["languages"], {"Go": 1, "unspecified": 1})
        self.assertEqual(result["known_model_tokens"], {"deepseek/4-flash": 1, "gpt/6.1-sol-max": 1})
        self.assertTrue(result["sample_only"])

    def test_credentials_in_metadata_are_filtered(self):
        secret = "12345678-1234-1234-1234-123456789abc"
        result = inspect.queue_summary([{"type": "app", "language": secret, "user_agent": "gpt/" + secret}], {secret})
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(result["redacted_model_tokens"], 1)

    @mock.patch.object(inspect.subprocess, "run")
    def test_subprocess_failures_never_echo_output(self, run):
        run.return_value = subprocess.CompletedProcess([], 9, "private stdout", "private stderr")
        with self.assertRaisesRegex(inspect.ProbeError, "^cli_nonzero_exit$"):
            inspect.probe(Path("cli"), ["--offline-count"], Path("config"), 2)
        run.side_effect = subprocess.TimeoutExpired("private command", 2, output="private output")
        with self.assertRaisesRegex(inspect.ProbeError, "^cli_timeout$"):
            inspect.probe(Path("cli"), ["--offline-count"], Path("config"), 2)

    @mock.patch.object(inspect, "probe")
    def test_collect_uses_only_local_read_commands(self, probe):
        probe.side_effect = ["v2.28.0\n", "0\n", "[]"]
        with tempfile.TemporaryDirectory() as directory:
            result = inspect.collect(Path("trusted-cli"), Path(directory) / "missing", 5, 2)
        self.assertEqual(result["offline_count"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual([call.args[1] for call in probe.call_args_list], [["--version"], ["--offline-count"], ["--print-offline-heartbeats", "5"]])


if __name__ == "__main__":
    unittest.main()
