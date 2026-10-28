#!/usr/bin/env python3
"""Read-only, redacted local WakaTime diagnostics. Python standard library only."""

from __future__ import annotations

import argparse
import configparser
from collections import Counter
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess


MODEL_TOKEN = re.compile(
    r"(?<!\S)((?:gpt|claude|sonnet|opus|haiku|gemini|grok|deepseek|qwen|kimi)"
    r"/[0-9][A-Za-z0-9_.+-]{0,95})(?=\s|$)", re.IGNORECASE
)
SENSITIVE_TOKEN = re.compile(r"waka_|sk-|gh[pousr]_|github_pat_", re.IGNORECASE)
LANGUAGE_LABEL = re.compile(r"[\w .+#()-]{1,64}\Z")


class ProbeError(Exception):
    """Contains a fixed public error code, never subprocess or config contents."""


class RedactedParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, "argument_error: use --help for supported arguments.\n")


def select_config(home: Path, environ: dict[str, str], explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser()
    waka_home = environ.get("WAKATIME_HOME", "").strip()
    if waka_home:
        return Path(waka_home).expanduser() / ".wakatime.cfg"
    legacy = home / ".wakatime.cfg"
    if legacy.exists():
        return legacy
    xdg = Path(environ.get("XDG_CONFIG_HOME", ""))
    return (xdg if xdg.is_absolute() else home / ".config") / "wakatime" / "wakatime.cfg"


def config_summary(path: Path) -> tuple[dict, set[str]]:
    summary = {"exists": path.is_file(), "parsed": False}
    secrets: set[str] = set()
    if not summary["exists"]:
        return summary, secrets
    parser = configparser.ConfigParser(interpolation=None, strict=False, delimiters=("=",))
    try:
        parser.read_string(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, configparser.Error):
        summary["error"] = "config_unreadable_or_invalid"
        return summary, secrets
    settings = dict(parser.items("settings", raw=True)) if parser.has_section("settings") else {}
    for section in parser.sections():
        for key, value in parser.items(section, raw=True):
            if re.search(r"key|token|password", key, re.IGNORECASE) and value.strip():
                secrets.add(value.strip())
            if section == "api_urls" and "|" in value:
                secrets.add(value.rsplit("|", 1)[-1].strip())
    summary.update(
        parsed=True,
        api_key_in_selected_config=bool(settings.get("api_key", "").strip()),
        vault_command_present=bool(settings.get("api_key_vault_cmd", "").strip()),
        custom_hostname_present=bool(settings.get("hostname", "").strip()),
        import_config_present=bool(settings.get("import_cfg", "").strip()),
        project_mapping_count=len(parser.items("projectmap", raw=True)) if parser.has_section("projectmap") else 0,
    )
    return summary, secrets


def find_cli(explicit: Path | None, home: Path) -> Path | None:
    if explicit is not None:
        return explicit.expanduser() if explicit.expanduser().is_file() else None
    found = shutil.which("wakatime-cli")
    if found:
        return Path(found)
    system = {"Windows": "windows", "Darwin": "darwin", "Linux": "linux"}.get(platform.system())
    arch = {"amd64": "amd64", "x86_64": "amd64", "arm64": "arm64", "aarch64": "arm64"}.get(platform.machine().lower())
    if not system or not arch:
        return None
    suffix = ".exe" if system == "windows" else ""
    for name in (f"wakatime-cli-{system}-{arch}{suffix}", f"wakatime-cli{suffix}"):
        candidate = home / ".wakatime" / name
        if candidate.is_file():
            return candidate
    return None


def probe(cli: Path, args: list[str], config: Path, timeout: int) -> str:
    options = {"capture_output": True, "text": True, "encoding": "utf-8", "timeout": timeout}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        result = subprocess.run([str(cli), "--config", str(config), *args], **options)
    except subprocess.TimeoutExpired:
        raise ProbeError("cli_timeout") from None
    except (OSError, UnicodeError):
        raise ProbeError("cli_execution_failed") from None
    if result.returncode != 0:
        raise ProbeError("cli_nonzero_exit")
    return result.stdout


def parse_queue(raw: str) -> list[dict]:
    if not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        try:
            parsed = [json.loads(line) for line in raw.splitlines() if line.strip()]
        except json.JSONDecodeError:
            raise ProbeError("queue_format_invalid") from None
    if isinstance(parsed, dict):
        if isinstance(parsed.get("data"), list):
            parsed = parsed["data"]
        elif isinstance(parsed.get("heartbeats"), list):
            parsed = parsed["heartbeats"]
        elif "user_agent" in parsed and "type" in parsed:
            parsed = [parsed]
    if not isinstance(parsed, list) or not all(isinstance(row, dict) for row in parsed):
        raise ProbeError("queue_format_invalid")
    return parsed


def safe_label(value: object, secrets: set[str]) -> str | None:
    if not isinstance(value, str) or not LANGUAGE_LABEL.fullmatch(value):
        return None
    if SENSITIVE_TOKEN.search(value) or any(secret and secret in value for secret in secrets):
        return None
    return value


def queue_summary(rows: list[dict], secrets: set[str]) -> dict:
    types: Counter = Counter()
    languages: Counter = Counter()
    models: Counter = Counter()
    without_known_model = 0
    redacted = 0
    for row in rows:
        entity_type = row.get("type")
        types[entity_type if entity_type in ("file", "app", "domain") else "unclassified"] += 1
        language = row.get("language")
        label = safe_label(language, secrets)
        languages[label or ("unspecified" if not language else "redacted_or_unclassified")] += 1
        ua = row.get("user_agent")
        tokens = MODEL_TOKEN.findall(ua) if isinstance(ua, str) else []
        visible = []
        for token in tokens:
            if SENSITIVE_TOKEN.search(token) or any(secret and secret in token for secret in secrets):
                redacted += 1
            else:
                visible.append(token)
        models.update(set(visible))
        without_known_model += not bool(visible)
    return {
        "sample_only": True,
        "sampled_records": len(rows),
        "entity_types": dict(sorted(types.items())),
        "languages": dict(sorted(languages.items())),
        "known_model_tokens": dict(sorted(models.items())),
        "rows_without_known_model_token": without_known_model,
        "redacted_model_tokens": redacted,
    }


def collect(cli: Path | None, config: Path, sample_limit: int, timeout: int) -> dict:
    selected, secrets = config_summary(config)
    report = {"read_only": True, "config": selected, "cli_found": cli is not None, "errors": []}
    if cli is None:
        report["errors"].append("cli_not_found")
        return report
    for name, args in (
        ("version", ["--version"]),
        ("offline_count", ["--offline-count"]),
        ("queue_sample", ["--print-offline-heartbeats", str(sample_limit)]),
    ):
        try:
            raw = probe(cli, args, config, timeout)
            if name == "version":
                match = re.fullmatch(r"v?(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)\s*", raw.strip())
                if not match:
                    raise ProbeError("version_format_invalid")
                report[name] = match.group(1)
            elif name == "offline_count":
                if not re.fullmatch(r"\d+", raw.strip()):
                    raise ProbeError("count_format_invalid")
                report[name] = int(raw.strip())
            else:
                report[name] = queue_summary(parse_queue(raw), secrets)
                report[name]["requested_limit"] = sample_limit
        except ProbeError as error:
            report["errors"].append(str(error))
    if selected.get("error"):
        report["errors"].append(selected["error"])
    return report


def bounded_integer(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 1000:
        raise argparse.ArgumentTypeError("value must be between 1 and 1000")
    return number


def main() -> int:
    parser = RedactedParser(description=__doc__)
    parser.add_argument("--cli", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--sample-limit", type=bounded_integer, default=100)
    parser.add_argument("--timeout", type=bounded_integer, default=10, help="per local probe timeout in seconds")
    args = parser.parse_args()
    config = select_config(Path.home(), dict(os.environ), args.config)
    report = collect(find_cli(args.cli, Path.home()), config, args.sample_limit, args.timeout)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
