#!/usr/bin/env python3
"""Classify legacy artifact references without rewriting their source content."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, load_mapping, resolve_all_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-index", type=Path, required=True)
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--legacy-kind", action="append", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        mapping = load_mapping(args.mapping)
        profiles = {
            item["legacy_kind"]: item
            for item in resolve_all_profiles(args.profile_index, args.mapping)
        }
        selected = []
        for code in args.legacy_kind:
            if code not in profiles:
                raise GovernanceError(f"unknown legacy profile: {code}")
            selected.append(profiles[code])
        plan = {
            "schema_version": "6.3-candidate",
            "status": "MigrationPlan",
            "source_policy": "forward-only; preserve source; create envelope or reference on demand",
            "default_meta_type": mapping["default_meta_type"],
            "items": selected,
        }
        rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
            print(args.output)
        else:
            print(rendered, end="")
    except (OSError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
