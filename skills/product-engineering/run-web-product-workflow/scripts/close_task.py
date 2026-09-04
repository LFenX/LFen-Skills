#!/usr/bin/env python3
"""Write the terminal V6.3 TaskOutcome for a task."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from minimal_task import parse_next_tasks
from governance_artifacts import GovernanceError, OUTCOME_STATES, close_task


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--status", choices=sorted(OUTCOME_STATES), required=True)
    parser.add_argument("--fact", action="append", default=[])
    parser.add_argument("--change", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[], help="RESULT::summary[::evidence-ref]")
    verification = parser.add_mutually_exclusive_group()
    verification.add_argument("--verification-json-base64", help="Base64 UTF-8 JSON array of structured verification results")
    verification.add_argument("--verification-json-file", type=Path, help="UTF-8 JSON file containing structured verification results")
    incomplete = parser.add_mutually_exclusive_group()
    incomplete.add_argument("--incomplete-json-base64", help="Base64 UTF-8 JSON array with reason, impact, owner, and reentry_condition")
    incomplete.add_argument("--incomplete-json-file", type=Path, help="UTF-8 JSON file containing incomplete items")
    legacy = parser.add_mutually_exclusive_group()
    legacy.add_argument("--legacy-issues-json-base64", help="Base64 UTF-8 JSON array with reason, impact, owner, and reentry_condition")
    legacy.add_argument("--legacy-issues-json-file", type=Path, help="UTF-8 JSON file containing legacy issues")
    parser.add_argument("--decision", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument(
        "--next-task",
        action="append",
        default=[],
        metavar="TASK_ID::relation::reason",
        help="Derived task and its C10 8.2 relation: observed-from, affected-by, addresses, extends or refines",
    )
    manifest = parser.add_mutually_exclusive_group()
    manifest.add_argument("--artifact-manifest-json-base64", help="Base64 UTF-8 terminal Artifact Manifest array")
    manifest.add_argument("--artifact-manifest-json-file", type=Path, help="UTF-8 JSON file containing the terminal Artifact Manifest")
    snapshot = parser.add_mutually_exclusive_group()
    snapshot.add_argument("--source-snapshot-json-base64", help="Base64 UTF-8 JSON object; omitted captures Git automatically")
    snapshot.add_argument("--source-snapshot-json-file", type=Path, help="UTF-8 JSON file; omitted captures Git automatically")
    return parser.parse_args()


def decode_json_input(raw: str | None, file_path: Path | None, expected: type, label: str):
    if raw is None and file_path is None:
        return None
    payload = (
        file_path.read_text(encoding="utf-8")
        if file_path is not None
        else base64.b64decode(raw, validate=True).decode("utf-8")
    )
    value = json.loads(payload)
    if not isinstance(value, expected):
        raise GovernanceError(f"{label} must decode to {expected.__name__}")
    return value


def main() -> int:
    args = parse_args()
    try:
        snapshot = decode_json_input(args.source_snapshot_json_base64, args.source_snapshot_json_file, dict, "source snapshot")
        checks = decode_json_input(args.verification_json_base64, args.verification_json_file, list, "verification") or []
        for raw in args.verification:
            parts = raw.split("::")
            if len(parts) not in {2, 3}:
                raise GovernanceError("--verification must use RESULT::summary[::evidence-ref]")
            checks.append({"result": parts[0], "summary": parts[1], "evidence_refs": parts[2:]})
        incomplete = decode_json_input(args.incomplete_json_base64, args.incomplete_json_file, list, "incomplete items") or []
        legacy = decode_json_input(args.legacy_issues_json_base64, args.legacy_issues_json_file, list, "legacy issues") or []
        manifest = decode_json_input(args.artifact_manifest_json_base64, args.artifact_manifest_json_file, list, "artifact manifest")
        path = close_task(
            args.task_dir,
            status=args.status,
            established_facts=args.fact,
            actual_changes=args.change,
            verification=checks,
            incomplete_items=incomplete,
            legacy_issues=legacy,
            decisions=args.decision,
            evidence_refs=args.evidence_ref,
            next_tasks=parse_next_tasks(args.next_task, task_id=Path(args.task_dir).resolve().name),
            artifact_manifest=manifest,
            source_snapshot=snapshot,
        )
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
