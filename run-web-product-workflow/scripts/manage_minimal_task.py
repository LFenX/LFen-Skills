#!/usr/bin/env python3
"""Initialize, update, close, or validate one Minimal aggregate task carrier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, read_json
from minimal_task import (
    append_minimal_event,
    screen_minimal_eligibility,
    screening_facts,
    allowed_minimal_change_surfaces,
    close_minimal_record,
    create_minimal_record,
    minimal_record_path,
    validate_minimal_record,
)


def add_common_init(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--ordinal", type=int, required=True)
    parser.add_argument("--depends-on", action="append", default=[])
    parser.add_argument("--supersedes", action="append", default=[])
    parser.add_argument("--objective", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--out-of-scope", action="append", default=[])
    parser.add_argument("--allowed-path", action="append", required=True)
    parser.add_argument("--forbidden-action", action="append", default=[])
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--delivery-scenario", required=True, choices=[f"DS-{value:02d}" for value in range(1, 5)])
    parser.add_argument("--development-type", required=True, choices=[f"DT-{value:02d}" for value in range(1, 10)])
    parser.add_argument(
        "--change-surface",
        required=True,
        choices=allowed_minimal_change_surfaces(),
        help="Minimal-eligible controlled surface; extension-triggering surfaces are rejected and must use the full carrier.",
    )
    parser.add_argument("--selected-approach", required=True)
    parser.add_argument("--alternative-rejected", required=True)
    # Optional by VC-PPG-DEC-001 16.4, which lists what Minimal must carry at init
    # and authorises the script to populate omitted non-blocking fields with
    # traceable defaults. Minimal is Risk=Low, so first-principles depth is Concise,
    # whose floor is the selected approach against the status quo -- both already
    # mandatory above. Supplying any of these still overrides the default.
    parser.add_argument("--plan-step", action="append", default=[])
    parser.add_argument("--verification", default="")
    parser.add_argument("--rollback", default="")
    parser.add_argument("--selection-source", required=True, choices=["explicit-user", "automatic"])
    parser.add_argument("--basis", action="append", default=[])
    parser.add_argument("--authority-ref", action="append", required=True)
    parser.add_argument(
        "--eligibility-evidence-ref",
        action="append",
        required=True,
        help="Repeat with distinct evidence for reversibility, scope, effects, release, security, and extensions.",
    )
    parser.add_argument("--fact", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--assumption", action="append", default=[])
    parser.add_argument("--fundamental", action="append", default=[])
    parser.add_argument("--causal-link", action="append", default=[])
    parser.add_argument("--decision-criterion", action="append", default=[])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    add_common_init(init)
    append = commands.add_parser("append")
    append.add_argument("task_dir", type=Path)
    append.add_argument(
        "--event-type",
        required=True,
        choices=["run_started", "mutation", "verification", "failure"],
    )
    append.add_argument("--summary", required=True)
    append.add_argument(
        "--status",
        required=True,
        choices=["started", "recorded", "succeeded", "failed", "blocked"],
    )
    append.add_argument("--evidence-ref", action="append", default=[])
    close = commands.add_parser("close")
    close.add_argument("task_dir", type=Path)
    close.add_argument(
        "--status",
        required=True,
        choices=["Implemented", "Deferred", "Cancelled", "Blocked", "Superseded"],
    )
    close.add_argument("--fact", action="append", default=[])
    close.add_argument("--change", action="append", default=[])
    close.add_argument("--verification", action="append", required=True)
    close.add_argument(
        "--incomplete-item",
        action="append",
        default=[],
        help="summary::reason::impact::owner::reentry_condition",
    )
    # Answers "Minimal or full carrier?" before any record exists. The Minimal
    # record does not carry applicability_facts at all, and eligibility depends on
    # only the facts whose Yes value vetoes one of VC-PPG-DEC-001 16.4's conditions,
    # so the carrier can be chosen without first completing the full Task Profile.
    screen = commands.add_parser("screen")
    screen.add_argument("--risk", required=True, choices=["Low", "Medium", "High", "Critical"])
    screen.add_argument(
        "--single-scope",
        required=True,
        choices=["yes", "no"],
        help="Whether scope.in_scope would hold exactly one independently acceptable Scope.",
    )
    screen.add_argument(
        "--fact",
        action="append",
        default=[],
        metavar="KEY=Yes|No|Unknown",
        help="Repeat for each screening fact; run without any to be told which are needed.",
    )
    validate = commands.add_parser("validate")
    validate.add_argument("--project-root", default=".")
    validate.add_argument("task_dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "init":
            path = create_minimal_record(
                Path(args.project_root),
                project_id=args.project_id,
                work_item_id=args.work_item_id,
                task_id=args.task_id,
                ordinal=args.ordinal,
                depends_on=args.depends_on,
                supersedes=args.supersedes,
                objective=args.objective,
                scope=args.scope,
                acceptance=args.acceptance,
                delivery_scenario=args.delivery_scenario,
                development_type=args.development_type,
                change_surface=args.change_surface,
                selected_approach=args.selected_approach,
                alternative_rejected=args.alternative_rejected,
                plan_steps=args.plan_step,
                verification=args.verification,
                rollback=args.rollback,
                allowed_paths=args.allowed_path,
                out_of_scope=args.out_of_scope,
                forbidden_actions=args.forbidden_action,
                selection_source=args.selection_source,
                basis=args.basis,
                authority_refs=args.authority_ref,
                eligibility_evidence_refs=args.eligibility_evidence_ref,
                facts=args.fact,
                constraints=args.constraint,
                assumptions=args.assumption,
                fundamentals=args.fundamental,
                causal_chain=args.causal_link,
                decision_criteria=args.decision_criterion,
            )
            print(path)
        elif args.command == "append":
            event = append_minimal_event(
                args.task_dir,
                event_type=args.event_type,
                summary=args.summary,
                status=args.status,
                evidence_refs=args.evidence_ref,
            )
            print(json.dumps(event, ensure_ascii=False, indent=2))
        elif args.command == "close":
            print(
                close_minimal_record(
                    args.task_dir,
                    status=args.status,
                    established_facts=args.fact,
                    actual_changes=args.change,
                    verification=args.verification,
                    incomplete_items=args.incomplete_item,
                )
            )
        elif args.command == "screen":
            facts: dict[str, str] = {}
            for item in args.fact:
                key, _, value = item.partition("=")
                if not value:
                    raise GovernanceError(f"--fact must be KEY=VALUE, got {item!r}")
                facts[key.strip()] = value.strip()
            unknown_keys = sorted(set(facts) - set(screening_facts()))
            if unknown_keys:
                raise GovernanceError(
                    "not screening facts: " + ", ".join(unknown_keys)
                )
            eligible, reasons = screen_minimal_eligibility(
                risk_level=args.risk,
                single_scope=args.single_scope == "yes",
                facts=facts,
            )
            if eligible:
                print("ELIGIBLE: every VC-PPG-DEC-001 16.4 condition holds; use the Minimal carrier.")
                print("Next: manage_minimal_task.py init  (see reference/minimal.md)")
                return 0
            print("NOT-ELIGIBLE: use the full carrier via init_task.py (see reference/init.md).")
            for reason in reasons:
                print(f"  - {reason}")
            return 0
        else:
            project_root = Path(args.project_root).resolve()
            task_dir = args.task_dir if args.task_dir.is_absolute() else project_root / args.task_dir
            task_dir = task_dir.resolve()
            errors = validate_minimal_record(
                read_json(minimal_record_path(task_dir)),
                task_dir=task_dir,
            )
            if errors:
                for error in errors:
                    print(f"INVALID: {error}", file=sys.stderr)
                return 1
            print(f"VALID: {minimal_record_path(task_dir)}")
    except (OSError, UnicodeError, ValueError, KeyError, GovernanceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
