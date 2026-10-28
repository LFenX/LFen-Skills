"""Isolated tests: no real keys, network calls, configuration writes, or heartbeats."""

import json
import contextlib
import io
from pathlib import Path
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

    def test_corrupt_queue_and_vault_config_never_start_process_or_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config, queue, cli = root / "wakatime.cfg", root / "queue.db", root / "fake-cli"
            config.write_text("[settings]\napi_key_vault_cmd = must-not-execute\n", encoding="utf-8")
            queue.write_bytes(b"corrupt synthetic queue, never repair or rename")
            cli.write_text("must never execute", encoding="utf-8")
            before = {path.name: path.read_bytes() for path in root.iterdir()}
            output = io.StringIO()
            argv = ["inspect_wakatime.py", "--config", str(config), "--cli", str(cli), "--sample-limit", "5", "--timeout", "2"]
            with contextlib.ExitStack() as stack:
                calls = [stack.enter_context(mock.patch(name, side_effect=AssertionError(name)))
                         for name in ("subprocess.run", "subprocess.Popen", "os.system", "socket.socket", "socket.create_connection")]
                stack.enter_context(mock.patch("sys.argv", argv))
                stack.enter_context(contextlib.redirect_stdout(output))
                self.assertEqual(inspect.main(), 0)
                for call in calls:
                    call.assert_not_called()
            result = json.loads(output.getvalue())
            self.assertEqual({path.name: path.read_bytes() for path in root.iterdir()}, before)
        self.assertTrue(result["cli_found"])
        self.assertFalse(result["cli_executed"])
        self.assertEqual(result["offline_queue"], {"status": "not_checked", "reason": "live_cli_probes_disabled"})
        self.assertNotIn("offline_count", result)
        self.assertNotIn("queue_sample", result)
        self.assertEqual(result["errors"], [])

    def test_quoted_and_project_credentials_are_normalized_and_filtered(self):
        secret = "12345-synthetic-credential-for-isolated-test"
        cases = (
            f"[settings]\napi_key = {secret}\n",
            f'[settings]\napi_key = "{secret}"\n',
            f"[settings]\napi_key = '{secret}'\n",
            f"[settings]\n[project_api_key]\n^/Projects/example = {secret}\n",
            f'[settings]\n[project_api_key]\n^/Projects/example = "{secret}"\n',
            f'[settings]\n[api_urls]\n^/Projects/example = "https://example.invalid/api/v1|{secret}"\n',
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.cfg"
            for index, text in enumerate(cases):
                with self.subTest(case=index):
                    path.write_text(text, encoding="utf-8")
                    summary, secrets = inspect.config_summary(path)
                    self.assertIn(secret, secrets)
                    result = inspect.queue_summary([{"type": "app", "language": secret, "user_agent": "gpt/" + secret}], secrets)
                    self.assertNotIn(secret, json.dumps([summary, result]))
                    self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_legacy_uuid_credentials_are_filtered_without_config_values(self):
        credential = "12345678-1234-4abc-8def-123456789abc"
        for value in (credential, credential.upper()):
            with self.subTest(value=value):
                result = inspect.queue_summary([{"type": "app", "language": value, "user_agent": "gpt/" + value}], set())
                self.assertNotIn(value, json.dumps(result))
                self.assertEqual(result["redacted_model_tokens"], 1)

    def test_empty_quoted_key_is_not_reported_as_configured(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.cfg"
            path.write_text('[settings]\napi_key = ""\n', encoding="utf-8")
            summary, _ = inspect.config_summary(path)
            self.assertFalse(summary["api_key_in_selected_config"])


if __name__ == "__main__":
    unittest.main()
