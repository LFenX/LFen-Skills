#!/usr/bin/env python3
"""Rebuild project-state.json from task outcomes and authority envelopes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, rebuild_project_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        path = rebuild_project_state(Path(args.project_root), args.project_id)
    except (OSError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
