#!/usr/bin/env python3
"""Amend a frozen TaskContract or terminal TaskOutcome without hiding history."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, amend_record, amend_record_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--path", help="Dotted field path, for example scope.in_scope")
    value_group = parser.add_mutually_exclusive_group()
    value_group.add_argument("--value-json")
    value_group.add_argument(
        "--value-json-base64",
        help="UTF-8 JSON encoded as Base64; avoids native-shell quoting loss",
    )
    value_group.add_argument("--value-json-file", type=Path, help="UTF-8 JSON file containing one value")
    changes_group = parser.add_mutually_exclusive_group()
    changes_group.add_argument(
        "--changes-json-base64",
        help="Base64 UTF-8 JSON array of {path,value,allow_add?} changes; validates once after the batch",
    )
    changes_group.add_argument(
        "--changes-json-file",
        type=Path,
        help="UTF-8 JSON file containing an array of {path,value,allow_add?} changes",
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--basis", required=True)
    parser.add_argument("--allow-add", action="store_true", help="Allow adding a missing non-immutable field")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.changes_json_base64 is not None or args.changes_json_file is not None:
            if args.path or args.value_json is not None or args.value_json_base64 is not None or args.value_json_file is not None or args.allow_add:
                raise GovernanceError("batch changes cannot be combined with single-field options")
            raw_changes = (
                args.changes_json_file.read_text(encoding="utf-8")
                if args.changes_json_file is not None
                else base64.b64decode(args.changes_json_base64, validate=True).decode("utf-8")
            )
            changes = json.loads(raw_changes)
            if not isinstance(changes, list):
                raise GovernanceError("batch changes must contain an array")
            document = amend_record_batch(
                args.record,
                changes=changes,
                reason=args.reason,
                basis=args.basis,
            )
            print(f"AMENDED: {args.record} revision {document['revision']}")
            return 0
        if not args.path or (args.value_json is None and args.value_json_base64 is None and args.value_json_file is None):
            raise GovernanceError("single-field mode requires --path and one value option")
        raw_value = args.value_json
        if args.value_json_base64 is not None:
            raw_value = base64.b64decode(args.value_json_base64, validate=True).decode(
                "utf-8"
            )
        elif args.value_json_file is not None:
            raw_value = args.value_json_file.read_text(encoding="utf-8")
        value = json.loads(raw_value)
        document = amend_record(
            args.record,
            dotted_path=args.path,
            new_value=value,
            reason=args.reason,
            basis=args.basis,
            allow_add=args.allow_add,
        )
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"AMENDED: {args.record} revision {document['revision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
