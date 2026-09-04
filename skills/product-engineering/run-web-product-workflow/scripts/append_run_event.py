#!/usr/bin/env python3
"""Append one material event to a V6.3 minimal run ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, RUN_EVENT_TYPES, RUN_STATUSES, append_run_event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--event-type", choices=sorted(RUN_EVENT_TYPES), required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--status", choices=sorted(RUN_STATUSES), required=True)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--side-effect", action="append", default=[])
    parser.add_argument("--redaction", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        event = append_run_event(
            args.task_dir,
            run_id=args.run_id,
            attempt_id=args.attempt_id,
            event_type=args.event_type,
            summary=args.summary,
            status=args.status,
            exit_code=args.exit_code,
            evidence_refs=args.evidence_ref,
            side_effects=args.side_effect,
            redactions=args.redaction,
        )
    except (OSError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"APPENDED: {event['event_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
