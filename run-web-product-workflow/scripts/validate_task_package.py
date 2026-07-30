#!/usr/bin/env python3
"""Validate a task profile and its compact artifact manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
MODES = {"Normal", "Emergency"}
CONFIDENCE_LEVELS = {"Low", "Medium", "High"}
ARTIFACT_ACTIONS = {"Create/Revise", "Reference", "Generate", "On Event", "N/A"}
EXTENSION_STATES = {
    "Not Evaluated",
    "Pending",
    "Inactive",
    "Conditionally Active",
    "Active",
    "Retiring",
    "Retired",
}
EXTENSIONS = {"E01", "E02", "E03", "E04", "E05"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a run-web-product-workflow task package."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="JSON file path, or - to read JSON from stdin.",
    )
    parser.add_argument(
        "--spec-root",
        help="Override the canonical specification repository root.",
    )
    return parser.parse_args()


def load_json(source: str) -> dict[str, Any]:
    if source == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(source).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def default_spec_root() -> Path:
    markers = (
        Path("01_治理基线") / "Vibe_Coding_受控产物目录与状态模型_V6.2.md",
        Path("05_记录与登记册") / "V6.2_跨规范产物归属索引.md",
    )
    starts = (Path(__file__).resolve().parent, Path.cwd().resolve())
    candidates: list[Path] = []
    for start in starts:
        for candidate in (start, *start.parents):
            if all((candidate / marker).is_file() for marker in markers):
                if candidate not in candidates:
                    candidates.append(candidate)
                break
    if len(candidates) != 1:
        rendered = ", ".join(str(item) for item in candidates) or "none"
        raise ValueError(
            "could not resolve exactly one canonical specification root; "
            f"candidates: {rendered}. Pass --spec-root explicitly."
        )
    return candidates[0]


def load_artifact_ids(spec_root: Path) -> set[str]:
    index = spec_root / "05_记录与登记册" / "V6.2_跨规范产物归属索引.md"
    text = index.read_text(encoding="utf-8")
    section_match = re.search(
        r"^## 4\.\s+全量产物归属索引\s*$"
        r"(?P<section>.*?)"
        r"^## 5\.\s+",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError(f"full artifact ownership section is missing from {index}")
    ids = set(
        re.findall(
            r"^\|\s*([A-Z][A-Z0-9]{2})\s*\|",
            section_match.group("section"),
            flags=re.MULTILINE,
        )
    )
    if len(ids) != 137:
        raise ValueError(
            f"canonical artifact index must contain 137 type IDs; found {len(ids)} in {index}"
        )
    return ids


def require_nonempty_list(
    owner: dict[str, Any], field: str, errors: list[str]
) -> list[Any]:
    value = owner.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"task_profile.{field} must be a non-empty array")
        return []
    return value


def validate_package(package: dict[str, Any], artifact_ids: set[str]) -> list[str]:
    errors: list[str] = []
    profile = package.get("task_profile")
    manifest = package.get("artifact_manifest")

    if not isinstance(profile, dict):
        return ["task_profile must be an object"]
    if not isinstance(manifest, list):
        return ["artifact_manifest must be an array"]

    scenario = profile.get("delivery_scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        errors.append("task_profile.delivery_scenario must be a non-empty string")

    require_nonempty_list(profile, "development_types", errors)
    require_nonempty_list(profile, "change_surfaces", errors)
    require_nonempty_list(profile, "basis", errors)
    if not isinstance(profile.get("baseline_inheritance"), list):
        errors.append("task_profile.baseline_inheritance must be an array")

    if profile.get("risk_level") not in RISK_LEVELS:
        errors.append(f"task_profile.risk_level must be one of {sorted(RISK_LEVELS)}")
    if profile.get("mode") not in MODES:
        errors.append(f"task_profile.mode must be one of {sorted(MODES)}")
    if profile.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append(
            f"task_profile.confidence must be one of {sorted(CONFIDENCE_LEVELS)}"
        )
    if not isinstance(profile.get("open_questions"), list):
        errors.append("task_profile.open_questions must be an array")

    extension_triggers = profile.get("extension_triggers")
    if not isinstance(extension_triggers, dict):
        errors.append("task_profile.extension_triggers must be an object")
    else:
        if set(extension_triggers) != EXTENSIONS:
            errors.append("task_profile.extension_triggers must contain exactly E01-E05")
        for extension, state in extension_triggers.items():
            if state not in EXTENSION_STATES:
                errors.append(
                    f"task_profile.extension_triggers.{extension} has invalid state {state!r}"
                )

    seen: set[str] = set()
    for position, item in enumerate(manifest):
        prefix = f"artifact_manifest[{position}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        artifact_id = item.get("artifact_type_id")
        if artifact_id not in artifact_ids:
            errors.append(f"{prefix}.artifact_type_id is not in the canonical index")
        elif artifact_id in seen:
            errors.append(f"{prefix}.artifact_type_id duplicates {artifact_id}")
        else:
            seen.add(artifact_id)
        if item.get("action") not in ARTIFACT_ACTIONS:
            errors.append(f"{prefix}.action must be one of {sorted(ARTIFACT_ACTIONS)}")
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{prefix}.reason must be a non-empty string")
        if item.get("action") == "N/A" and not item.get("rule_reference"):
            errors.append(f"{prefix}.rule_reference is required when action is N/A")

    return errors


def main() -> int:
    args = parse_args()
    try:
        package = load_json(args.input)
        spec_root = Path(args.spec_root) if args.spec_root else default_spec_root()
        artifact_ids = load_artifact_ids(spec_root)
        errors = validate_package(package, artifact_ids)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"VALID: {len(package['artifact_manifest'])} manifest entries; "
        f"{len(artifact_ids)} canonical artifact type IDs loaded."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
