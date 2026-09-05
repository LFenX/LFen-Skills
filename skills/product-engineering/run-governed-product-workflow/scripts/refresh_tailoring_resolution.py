#!/usr/bin/env python3
"""Amend Task Profile fields in one atomic write batch with one Amendment/Revision per changed field."""

from __future__ import annotations

import argparse
import base64
import copy
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import (
    APPLICABILITY_FACT_VALUES,
    EXTENSION_STATES,
    GovernanceError,
    amend_record_batch,
    refresh_derived_tailoring,
    read_json,
    resolve_tailoring,
)


def parse_assignment(raw: str, allowed: set[str], label: str) -> tuple[str, str]:
    key, separator, value = raw.partition("=")
    if not separator or value not in allowed:
        raise GovernanceError(f"invalid {label} {raw!r}")
    return key, value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_contract", type=Path)
    parser.add_argument("--stage", required=True, choices=tuple(f"S{value}" for value in range(1, 9)))
    profile_input = parser.add_mutually_exclusive_group()
    profile_input.add_argument(
        "--task-profile-json-file",
        type=Path,
        help="Optional UTF-8 complete replacement Task Profile",
    )
    profile_input.add_argument(
        "--task-profile-json-base64",
        help="Optional Base64-encoded UTF-8 complete replacement Task Profile",
    )
    parser.add_argument("--applicability-fact", action="append", default=[], help="KEY=Yes|No|Unknown")
    parser.add_argument("--extension-trigger", action="append", default=[], help="E01=Active, Inactive, etc.")
    parser.add_argument("--extension-evidence-ref", action="append", default=[], help="E01=evidence-ref; repeat for multiple refs")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--basis", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        before = read_json(args.task_contract)
        if before.get("meta_type") != "TaskContract":
            raise GovernanceError("target must be a TaskContract")
        profile = copy.deepcopy(before["task_profile"])
        if args.task_profile_json_file or args.task_profile_json_base64:
            payload = (
                args.task_profile_json_file.read_text(encoding="utf-8")
                if args.task_profile_json_file
                else base64.b64decode(
                    args.task_profile_json_base64,
                    validate=True,
                ).decode("utf-8")
            )
            profile = json.loads(payload)
            if not isinstance(profile, dict):
                raise GovernanceError("task profile file must contain a JSON object")
        facts = profile.get("applicability_facts")
        if not isinstance(facts, dict):
            raise GovernanceError("Task Profile is missing applicability_facts")
        for raw in args.applicability_fact:
            key, value = parse_assignment(raw, APPLICABILITY_FACT_VALUES, "applicability fact")
            if key not in facts:
                raise GovernanceError(f"unknown applicability fact {key!r}")
            facts[key] = value
        triggers = profile.get("extension_triggers")
        if not isinstance(triggers, dict):
            raise GovernanceError("Task Profile is missing extension_triggers")
        for raw in args.extension_trigger:
            key, value = parse_assignment(raw, EXTENSION_STATES, "extension trigger")
            if key not in triggers:
                raise GovernanceError(f"unknown extension {key!r}")
            triggers[key] = value
        extension_evidence = profile.setdefault(
            "extension_evidence_refs",
            {key: [] for key in ("E01", "E02", "E03", "E04", "E05")},
        )
        if not isinstance(extension_evidence, dict):
            raise GovernanceError("Task Profile extension_evidence_refs must be an object")
        for raw in args.extension_evidence_ref:
            key, separator, value = raw.partition("=")
            if not separator or key not in extension_evidence or not value:
                raise GovernanceError(f"invalid extension evidence reference {raw!r}")
            extension_evidence[key] = list(dict.fromkeys([*extension_evidence[key], value]))
        prospective = copy.deepcopy(before)
        prospective["task_profile"] = profile
        resolution = resolve_tailoring(profile, stage=args.stage, contract_context=prospective)
        changes = []
        if profile != before["task_profile"]:
            changes.append({"path": "task_profile", "value": profile})
        if changes:
            updated = amend_record_batch(
                args.task_contract,
                changes=changes,
                reason=args.reason,
                basis=args.basis,
            )
            print(f"AMENDED: {args.task_contract} revision {updated['revision']}")
        # The resolution itself is a derived view, so it is refreshed rather than
        # amended -- restating a recalculation was never a change to the contract.
        resolution = refresh_derived_tailoring(args.task_contract, stage=args.stage)
        if not changes:
            print(f"REFRESHED: {args.task_contract} tailoring now reflects {args.stage}")
        for blocker in resolution["blocking_reasons"]:
            print(f"BLOCKED: {blocker}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
