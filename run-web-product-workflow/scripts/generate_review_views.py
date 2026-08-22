#!/usr/bin/env python3
"""Generate the three V6.3 human-review view families."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, default_profile_index_path, generate_views


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-id", required=True)
    parser.add_argument(
        "--profile-index",
        type=Path,
        default=default_profile_index_path(),
        help="Legacy profile index; defaults to the copy embedded in this Skill",
    )
    parser.add_argument("--mapping", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        outputs = generate_views(
            Path(args.project_root),
            project_id=args.project_id,
            profile_index=args.profile_index,
            mapping_path=args.mapping,
        )
    except (OSError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
