#!/usr/bin/env python3
"""Create the minimal V6.3 task contract and empty run ledger."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import (
    APPLICABILITY_FACT_VALUES,
    BASELINE_INHERITANCE_STATES,
    CHANGE_SURFACES,
    DELIVERY_SCENARIOS,
    DEVELOPMENT_TYPES,
    EXECUTION_PERMISSIONS,
    GovernanceError,
    initialize_task,
    load_tailoring_map,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--ordinal", type=int, required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--acceptance", action="append", required=True)
    parser.add_argument("--development-type", action="append", choices=sorted(DEVELOPMENT_TYPES), required=True)
    parser.add_argument("--primary-development-type", choices=sorted(DEVELOPMENT_TYPES))
    parser.add_argument("--development-type-scope", action="append", default=[], help="DT-05=sub-scope; required for every type when multiple types are selected")
    parser.add_argument("--change-surface", action="append", choices=sorted(CHANGE_SURFACES), required=True)
    parser.add_argument("--delivery-scenario", choices=sorted(DELIVERY_SCENARIOS), default="DS-03")
    parser.add_argument("--in-scope", action="append", required=True)
    parser.add_argument("--out-of-scope", action="append", default=[])
    parser.add_argument("--allowed-path", action="append", default=[])
    parser.add_argument("--forbidden-action", action="append", default=[])
    parser.add_argument("--depends-on", action="append", default=[])
    parser.add_argument("--supersedes", action="append", default=[])
    parser.add_argument("--risk-level", choices=("Low", "Medium", "High", "Critical"), default="Medium")
    parser.add_argument("--mode", choices=("Normal", "Emergency"), default="Normal")
    parser.add_argument("--confidence", choices=("Low", "Medium", "High"), default="Medium")
    parser.add_argument("--extension-trigger", action="append", default=[], help="E01=Active, Inactive, or Not Evaluated")
    parser.add_argument("--extension-evidence-ref", action="append", default=[], help="E01=evidence-ref; repeat for multiple refs")
    parser.add_argument("--applicability-fact", action="append", default=[], help="KEY=Yes, No, or Unknown; unspecified facts default to Unknown")
    parser.add_argument("--tailoring-stage", choices=tuple(f"S{value}" for value in range(1, 9)), default="S1")
    parser.add_argument("--baseline-inheritance", action="append", choices=sorted(BASELINE_INHERITANCE_STATES), required=True)
    parser.add_argument("--basis", action="append", default=[])
    parser.add_argument("--authority-reference", action="append", default=[])
    parser.add_argument("--execution-permission", action="append", choices=sorted(EXECUTION_PERMISSIONS), default=[], help="Controlled permission; defaults to read, edit-in-scope, validate")
    authority_assessments = parser.add_mutually_exclusive_group()
    authority_assessments.add_argument("--authority-assessments-json-base64", help="Base64 UTF-8 JSON array of structured authority assessments")
    authority_assessments.add_argument("--authority-assessments-json-file", type=Path, help="UTF-8 JSON array of structured authority assessments")
    parser.add_argument("--required-gate", action="append", default=[])
    parser.add_argument("--plan-step", action="append", default=[])
    parser.add_argument("--verification-plan", action="append", default=[])
    parser.add_argument("--rollback", action="append", default=[])
    parser.add_argument(
        "--upgrade-minimal-reason",
        help="One-way upgrade reason when the same TaskID currently uses task-record.json.",
    )
    parser.add_argument(
        "--upgrade-minimal-basis",
        help="Evidence reference proving the Minimal hard boundary was crossed.",
    )
    questions = parser.add_mutually_exclusive_group()
    questions.add_argument("--open-questions-json-base64", help="Base64 UTF-8 JSON array of question objects")
    questions.add_argument("--open-questions-json-file", type=Path, help="UTF-8 JSON file containing an array of question objects")
    manifest = parser.add_mutually_exclusive_group()
    manifest.add_argument("--artifact-manifest-json-base64", help="Base64 UTF-8 JSON array")
    manifest.add_argument("--artifact-manifest-json-file", type=Path, help="UTF-8 JSON file containing the planned Artifact Manifest")
    snapshot = parser.add_mutually_exclusive_group()
    snapshot.add_argument("--source-snapshot-json-base64", help="Base64 UTF-8 JSON object; omitted captures Git automatically")
    snapshot.add_argument("--source-snapshot-json-file", type=Path, help="UTF-8 JSON file; omitted captures Git automatically")
    first_principles = parser.add_mutually_exclusive_group()
    first_principles.add_argument(
        "--first-principles-json-base64",
        help="Base64 UTF-8 first_principles_analysis object; omitted builds the honest minimum analysis",
    )
    first_principles.add_argument(
        "--first-principles-json-file",
        type=Path,
        help="UTF-8 first_principles_analysis object",
    )
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


def main() -> int:
    args = parse_args()
    try:
        snapshot = decode_json_input(args.source_snapshot_json_base64, args.source_snapshot_json_file, dict, "source snapshot")
        manifest = decode_json_input(args.artifact_manifest_json_base64, args.artifact_manifest_json_file, list, "artifact manifest")
        questions = decode_json_input(args.open_questions_json_base64, args.open_questions_json_file, list, "open questions")
        authority_assessments = decode_json_input(
            args.authority_assessments_json_base64,
            args.authority_assessments_json_file,
            list,
            "authority assessments",
        )
        first_principles_analysis = decode_json_input(
            args.first_principles_json_base64,
            args.first_principles_json_file,
            dict,
            "first-principles analysis",
        )
        triggers = {}
        type_scopes = {}
        for raw in args.development_type_scope:
            key, separator, value = raw.partition("=")
            if not separator or key not in DEVELOPMENT_TYPES or not value:
                raise GovernanceError(f"invalid --development-type-scope {raw!r}; expected DT-05=sub-scope")
            type_scopes.setdefault(key, []).append(value)
        extension_evidence = {key: [] for key in ("E01", "E02", "E03", "E04", "E05")}
        for raw in args.extension_trigger:
            key, separator, value = raw.partition("=")
            if not separator:
                raise GovernanceError(f"invalid --extension-trigger {raw!r}; expected E01=Active")
            triggers[key] = value
        for raw in args.extension_evidence_ref:
            key, separator, value = raw.partition("=")
            if not separator or key not in extension_evidence or not value:
                raise GovernanceError(f"invalid --extension-evidence-ref {raw!r}; expected E01=reference")
            extension_evidence[key].append(value)
        facts = {key: "Unknown" for key in load_tailoring_map()["applicability_facts"]}
        for raw in args.applicability_fact:
            key, separator, value = raw.partition("=")
            if not separator or key not in facts or value not in APPLICABILITY_FACT_VALUES:
                raise GovernanceError(f"invalid --applicability-fact {raw!r}; expected a controlled KEY=Yes|No|Unknown")
            facts[key] = value
        task_dir = initialize_task(
            Path(args.project_root),
            project_id=args.project_id,
            work_item_id=args.work_item_id,
            task_id=args.task_id,
            ordinal=args.ordinal,
            objective=args.objective,
            acceptance=args.acceptance,
            development_types=args.development_type,
            primary_development_type=args.primary_development_type,
            development_type_scopes=type_scopes or None,
            change_surfaces=args.change_surface,
            delivery_scenario=args.delivery_scenario,
            in_scope=args.in_scope,
            out_of_scope=args.out_of_scope,
            allowed_paths=args.allowed_path,
            forbidden_actions=args.forbidden_action,
            depends_on=args.depends_on,
            supersedes=args.supersedes,
            risk_level=args.risk_level,
            mode=args.mode,
            confidence=args.confidence,
            extension_triggers=triggers,
            extension_evidence_refs=extension_evidence,
            applicability_facts=facts,
            tailoring_stage=args.tailoring_stage,
            baseline_inheritance=args.baseline_inheritance,
            basis=args.basis or ["task-initiator-input"],
            open_questions=questions or [],
            required_gates=args.required_gate,
            authority_references=args.authority_reference,
            authority_assessments=authority_assessments or [],
            execution_permissions=args.execution_permission or ["read", "edit-in-scope", "validate"],
            plan_steps=args.plan_step or ["inspect", "change", "validate", "close"],
            plan_verification=args.verification_plan,
            rollback=args.rollback or ["revert only changes owned by this task"],
            artifact_manifest=manifest or [],
            source_snapshot=snapshot,
            first_principles_analysis=first_principles_analysis,
            upgrade_minimal_reason=args.upgrade_minimal_reason,
            upgrade_minimal_basis=args.upgrade_minimal_basis,
        )
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(task_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
