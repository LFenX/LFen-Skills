#!/usr/bin/env python3
"""Register metadata for a native AuthorityAsset without rewriting its content."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, register_authority_asset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--legacy-kind", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--content-ref", required=True)
    parser.add_argument("--native-format")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--scope", action="append", default=[])
    parser.add_argument("--trace-ref", action="append", default=[])
    parser.add_argument("--access-classification", default="internal")
    parser.add_argument("--retention-rule", default="follow-source-asset")
    parser.add_argument("--history-ref", default="git-history")
    profile_group = parser.add_mutually_exclusive_group(required=True)
    profile_group.add_argument("--profile-fields-json")
    profile_group.add_argument("--profile-fields-json-base64", help="Base64 UTF-8 JSON object")
    profile_group.add_argument("--profile-fields-json-file", type=Path, help="UTF-8 JSON file containing an object")
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--profile-index", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        raw_fields = args.profile_fields_json
        if args.profile_fields_json_base64 is not None:
            raw_fields = base64.b64decode(args.profile_fields_json_base64, validate=True).decode("utf-8")
        elif args.profile_fields_json_file is not None:
            raw_fields = args.profile_fields_json_file.read_text(encoding="utf-8")
        profile_fields = json.loads(raw_fields)
        if not isinstance(profile_fields, dict):
            raise GovernanceError("profile-fields-json must contain a JSON object")
        target = register_authority_asset(
            args.project_root,
            project_id=args.project_id,
            asset_id=args.asset_id,
            legacy_kind=args.legacy_kind,
            title=args.title,
            owner=args.owner,
            state=args.state,
            revision=args.revision,
            content_ref=args.content_ref,
            native_format=args.native_format,
            source=args.source,
            scope=args.scope,
            trace_refs=args.trace_ref,
            access_classification=args.access_classification,
            retention_rule=args.retention_rule,
            history_ref=args.history_ref,
            profile_fields=profile_fields,
            mapping_path=args.mapping,
            profile_index=args.profile_index,
        )
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
