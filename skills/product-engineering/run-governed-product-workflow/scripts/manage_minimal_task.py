#!/usr/bin/env python3
"""Initialize, update, close, or validate one Minimal aggregate task carrier."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import GovernanceError, read_json
from minimal_task import (
    append_minimal_event,
    parse_next_tasks,
    parse_request_snapshot,
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
    # Required here even though the schema keeps it optional: existing records stay
    # valid, and every new task carries the requester's own words from now on.
    parser.add_argument(
        "--request-snapshot",
        required=True,
        metavar="TEXT",
        help="用户原始提问原文；任务介绍必须使用同一语言",
    )
    parser.add_argument("--request-language", default="", help="留空则从原文自动判定")
    clarification = parser.add_mutually_exclusive_group()
    clarification.add_argument("--clarification-json-base64", help="Base64 UTF-8 JSON object recording the S1 clarification loop")
    clarification.add_argument("--clarification-json-file", type=Path, help="UTF-8 JSON file recording the S1 clarification loop")
    parser.add_argument(
        "--clarification-skipped",
        action="store_true",
        help="需求已清晰且与项目现状一致时零轮；必须同时给出 --clarification-notice 与至少一个 --survey-ref",
    )
    parser.add_argument("--clarification-notice", default="", help="实际展示给需求提出者的那句话，原文存档")
    parser.add_argument("--clarification-basis", default="", help="零轮或结束澄清所依据的勘察结论")
    parser.add_argument("--survey-ref", action="append", default=[], help="勘察证据引用；可重复")
    decisions = parser.add_mutually_exclusive_group()
    decisions.add_argument("--decisions-json-base64", help="Base64 UTF-8 JSON array of human decisions")
    decisions.add_argument("--decisions-json-file", type=Path, help="UTF-8 JSON file: Proceed/Acceptance 等人的决定")
    items = parser.add_mutually_exclusive_group()
    items.add_argument("--requirement-items-json-base64", help="Base64 UTF-8 JSON array of requirement items")
    items.add_argument("--requirement-items-json-file", type=Path, help="UTF-8 JSON file: 需求原文逐条拆解")
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
        "--next-task",
        action="append",
        default=[],
        metavar="TASK_ID::relation::reason",
        help="Derived task and its C10 8.2 relation: observed-from, affected-by, addresses, extends or refines",
    )
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


def resolve_clarification(args: argparse.Namespace) -> dict | None:
    """Build the S1 record from either a full JSON document or the zero-round flags."""

    value = decode_json_input(
        args.clarification_json_base64, args.clarification_json_file, dict, "clarification"
    )
    if value is None and args.clarification_skipped:
        value = {
            "state": "Settled",
            "mode": "Skipped",
            "notice": args.clarification_notice,
            "survey_refs": args.survey_ref,
            "rounds": [],
            "basis": args.clarification_basis,
            "reopened_by": [],
        }
    return value


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
                request_snapshot=parse_request_snapshot(args.request_snapshot, language=args.request_language),
                clarification=resolve_clarification(args),
                requirement_items=decode_json_input(
                    args.requirement_items_json_base64, args.requirement_items_json_file,
                    list, "requirement items",
                ),
                decisions=decode_json_input(
                    args.decisions_json_base64, args.decisions_json_file, list, "decisions",
                ),
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
                    next_tasks=parse_next_tasks(args.next_task, task_id=Path(args.task_dir).resolve().name),
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
                print("Next: manage_minimal_task.py init  (see commands/minimal.md)")
                return 0
            print("NOT-ELIGIBLE: use the full carrier via init_task.py (see commands/init.md).")
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
