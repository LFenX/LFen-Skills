#!/usr/bin/env python3
"""Print the current verified-delivery digest for an Acceptance or Gate record."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from governance_artifacts import GovernanceError, approval_subject_sha256, user_decision_subject_sha256, read_json, read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    args = parser.parse_args()
    try:
        if (args.task_dir / "before.json").is_file():
            before = read_json(args.task_dir / "before.json")
            events = read_jsonl(args.task_dir / "run.jsonl")
            outcome = read_json(args.task_dir / "after.json") if (args.task_dir / "after.json").is_file() else None
        else:
            from minimal_task import minimal_approval_contract
            record = read_json(args.task_dir / "task-record.json")
            before, events = minimal_approval_contract(record), record["run_ledger"]
            outcome = record.get("task_outcome")
        subject = (user_decision_subject_sha256(before, events, outcome)
                   if isinstance(outcome, dict) and "user_decision" in outcome else approval_subject_sha256(before, events))
        if not subject:
            raise GovernanceError("no current succeeded verification with evidence; verify the actual delivery first")
    except (OSError, KeyError, ValueError, GovernanceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(subject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
