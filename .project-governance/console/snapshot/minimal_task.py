#!/usr/bin/env python3
"""Shared logic for the Minimal aggregate carrier.

The carrier preserves TaskContract, RunLedger, and TaskOutcome as logical
sections. It is not a seventh meta type or a second risk model.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

from governance_artifacts import (
    GovernanceError,
    atomic_write_json,
    capture_source_snapshot,
    now_utc,
    read_json,
    require_id,
    runtime_asset_path,
    validate_json_document,
    validate_clarification,
)


MINIMAL_SCHEMA = "minimal-task-record.schema.json"
MINIMAL_META_TYPES = ["TaskContract", "RunLedger", "TaskOutcome"]
MINIMAL_EVENT_TYPES = {
    "run_started",
    "mutation",
    "verification",
    "failure",
    "run_finished",
    "upgrade_triggered",
}
MINIMAL_STATUSES = {"started", "recorded", "succeeded", "failed", "blocked"}
OUTCOME_STATES = {"Implemented", "Deferred", "Cancelled", "Blocked", "Superseded"}
EXTENSIONS = ("E01", "E02", "E03", "E04", "E05")
DEFAULT_OUT_OF_SCOPE = "script default: no additional exclusions beyond the stated Minimal scope."
DEFAULT_FORBIDDEN_ACTION = "script default: files outside allowed_paths are forbidden."
DEFAULT_ASSUMPTION = "script default: Minimal eligibility facts remain valid; upgrade if a hard boundary is crossed."
DEFAULT_ROLLBACK = "script default: reversible through git revert on the current branch."
DEFAULT_CONSTRAINT = "script default: only allowed_paths may be modified."
DEFAULT_BASIS = "script default: omitted non-blocking Minimal fields were populated by manage_minimal_task.py."
# VC-PPG-DEC-001 16.4 lists what a Minimal record must carry at init -- objective,
# single scope, allowed paths, Authority, one verifiable acceptance, the selected
# approach and why the alternative was rejected -- and authorises the script to
# populate omitted non-blocking fields with traceable defaults. Minimal is Risk=Low
# by eligibility, so first-principles depth is Concise, whose floor per
# references/first-principles-method.md 4 is the selected approach against the status
# quo with traceable steps; both are already mandatory arguments. These defaults keep
# every control objective present in the record without charging the caller for
# content the norm does not require up front. They restate facts the record already
# proves elsewhere -- never invented evidence.
DEFAULT_FACT = (
    "script default: no separate first-principles fact was supplied; the recorded "
    "Minimal eligibility evidence refs are the established fact base."
)
DEFAULT_FUNDAMENTALS = (
    "script default: the change is confined to the recorded allowed_paths.",
    "script default: the change is reversible, which is the eligibility fact that "
    "permits the Minimal carrier.",
)
DEFAULT_CAUSAL_LINK = (
    "script default: the recorded eligibility facts -- Low risk, reversible, single "
    "scope, no external effect, no production release, no security or privacy impact, "
    "all extensions Inactive -- are why the aggregate carrier is sufficient here."
)
DEFAULT_DECISION_CRITERION = (
    "script default: satisfy the recorded acceptance statement without crossing any "
    "Minimal hard boundary."
)
DEFAULT_VERIFICATION = (
    "script default: verification evidence is recorded at close via "
    "manage_minimal_task.py close --verification."
)
MINIMAL_ALLOWED_CHANGE_SURFACES = ("UI/UX", "API/Integration", "Agent/Collaboration")
MINIMAL_BLOCKING_FACT_SURFACE_KEYS = (
    "architecture_impact",
    "security_privacy_impact",
    "data_ai_impact",
    "operations_impact",
    "production_release",
)


def minimal_record_path(task_dir: Path) -> Path:
    return task_dir.resolve() / "task-record.json"


def load_tailoring_applicability_map() -> dict[str, Any]:
    return read_json(runtime_asset_path("mappings/tailoring-applicability-map.json"))


def minimal_applicability_errors(
    *,
    delivery_scenario: str,
    change_surface: str,
    tailoring_map: dict[str, Any] | None = None,
) -> list[str]:
    mapping = tailoring_map or load_tailoring_applicability_map()
    errors: list[str] = []
    extensions = set(EXTENSIONS)
    controlled = mapping.get("controlled_values", {})
    surfaces = controlled.get("change_surfaces", [])
    scenarios = controlled.get("delivery_scenarios", [])
    if change_surface not in surfaces:
        errors.append(f"Minimal change_surface is not controlled: {change_surface}")
        return errors
    if delivery_scenario not in scenarios:
        errors.append(f"Minimal delivery_scenario is not controlled: {delivery_scenario}")
        return errors
    routes = mapping.get("routes", {})
    surface_standards = set(routes.get("change_surfaces", {}).get(change_surface, []))
    routed_extensions = sorted(surface_standards & extensions)
    if routed_extensions:
        errors.append(
            f"Minimal rejects change_surface {change_surface}: routes extension standards {', '.join(routed_extensions)}"
        )
    scenario_standards = set(routes.get("delivery_scenarios", {}).get(delivery_scenario, []))
    scenario_extensions = sorted(scenario_standards & extensions)
    if scenario_extensions:
        errors.append(
            f"Minimal rejects delivery_scenario {delivery_scenario}: routes extension standards {', '.join(scenario_extensions)}"
        )
    standards = mapping.get("standards", {})
    trigger_extensions = sorted(
        source_id
        for source_id, spec in standards.items()
        if source_id in extensions and change_surface in spec.get("trigger_surfaces", [])
    )
    if trigger_extensions:
        errors.append(
            f"Minimal rejects change_surface {change_surface}: triggers {', '.join(trigger_extensions)}"
        )
    consistency = mapping.get("classification_consistency", {})
    fact_surfaces = consistency.get("fact_requires_any_surface", {})
    boundary_facts = sorted(
        fact
        for fact in MINIMAL_BLOCKING_FACT_SURFACE_KEYS
        if change_surface in fact_surfaces.get(fact, [])
    )
    if boundary_facts:
        errors.append(
            f"Minimal rejects change_surface {change_surface}: implies {', '.join(boundary_facts)}"
        )
    return errors


def require_minimal_applicability(*, delivery_scenario: str, change_surface: str) -> None:
    errors = minimal_applicability_errors(
        delivery_scenario=delivery_scenario,
        change_surface=change_surface,
    )
    if errors:
        raise GovernanceError("; ".join(errors))


def allowed_minimal_change_surfaces() -> list[str]:
    mapping = load_tailoring_applicability_map()
    return [
        surface
        for surface in mapping.get("controlled_values", {}).get("change_surfaces", [])
        if not minimal_applicability_errors(
            delivery_scenario="DS-03",
            change_surface=surface,
            tailoring_map=mapping,
        )
    ]


def validate_minimal_record(
    record: dict[str, Any],
    *,
    task_dir: Path | None = None,
) -> list[str]:
    errors = validate_json_document(record, MINIMAL_SCHEMA, "task-record")
    if errors:
        return errors
    if task_dir is not None and record["task_id"] != task_dir.name:
        errors.append("task-record.task_id must match the task directory name")
    if record["meta_types"] != MINIMAL_META_TYPES:
        errors.append("Minimal carrier must preserve exactly TaskContract, RunLedger, TaskOutcome")
    if record["task_id"] in set(record.get("depends_on", [])):
        errors.append("Minimal task cannot depend on itself")
    triggers = record["eligibility"]["extension_triggers"]
    if set(triggers) != set(EXTENSIONS) or any(value != "Inactive" for value in triggers.values()):
        errors.append("Minimal carrier requires E01-E05 to be Inactive")
    if record["task_contract"]["task_profile"]["extension_triggers"] != triggers:
        errors.append("Minimal task profile and eligibility extension triggers must match")
    # Minimal trims instances and carriers, never the clarification control itself.
    errors.extend(
        f"task_contract.{item}"
        for item in validate_clarification(record["task_contract"].get("clarification"))
    )
    task_profile = record["task_contract"]["task_profile"]
    errors.extend(
        minimal_applicability_errors(
            delivery_scenario=task_profile["delivery_scenario"],
            change_surface=task_profile["change_surface"],
        )
    )
    manifest_types = [item.get("meta_type") for item in record["artifact_manifest"]]
    if manifest_types != MINIMAL_META_TYPES:
        errors.append("Minimal Artifact Manifest must preserve the three logical meta types in order")
    expected_ref = f".project-governance/tasks/{record['task_id']}/task-record.json"
    if any(item.get("content_ref") != expected_ref for item in record["artifact_manifest"]):
        errors.append("Minimal Artifact Manifest content_ref must point to task-record.json")
    events = record["run_ledger"]
    for index, event in enumerate(events, start=1):
        if event.get("sequence") != index:
            errors.append("Minimal RunLedger sequence must be contiguous and start at 1")
            break
    if events and events[0].get("event_type") != "run_started":
        errors.append("Minimal RunLedger must begin with run_started")
    if sum(event.get("event_type") == "run_started" for event in events) > 1:
        errors.append("Minimal RunLedger may contain only one run_started")
    outcome = record["task_outcome"]
    lifecycle = record["lifecycle_state"]
    if outcome is None:
        if lifecycle == "Completed":
            errors.append("Completed Minimal carrier requires task_outcome")
    else:
        if lifecycle != "Completed":
            errors.append("Minimal task_outcome requires lifecycle_state Completed")
        if not events or events[-1].get("event_type") != "run_finished":
            errors.append("Completed Minimal carrier requires run_finished as final event")
        if record["completed_at"] != outcome.get("completed_at"):
            errors.append("Minimal carrier completion timestamps must match")
        if any(item.get("outcome") != "Created" for item in record["artifact_manifest"]):
            errors.append("Completed Minimal carrier requires Created manifest outcomes")
    upgrade = record["upgrade"]
    if lifecycle == "Upgraded" and not upgrade.get("required"):
        errors.append("Upgraded Minimal carrier requires an upgrade reason")
    if upgrade.get("required") and (
        not upgrade.get("reason") or not upgrade.get("basis") or not upgrade.get("triggered_at")
    ):
        errors.append("Minimal upgrade requires triggered_at, reason, and basis")
    return errors


def require_valid_minimal_record(record: dict[str, Any], *, task_dir: Path | None = None) -> None:
    errors = validate_minimal_record(record, task_dir=task_dir)
    if errors:
        raise GovernanceError("; ".join(errors))


def create_minimal_record(
    project_root: Path,
    *,
    project_id: str,
    work_item_id: str,
    task_id: str,
    ordinal: int,
    depends_on: Iterable[str],
    supersedes: Iterable[str],
    objective: str,
    clarification: dict[str, Any] | None = None,
    scope: str,
    acceptance: str,
    delivery_scenario: str,
    development_type: str,
    change_surface: str,
    selected_approach: str,
    alternative_rejected: str,
    plan_steps: Iterable[str],
    verification: str,
    rollback: str,
    allowed_paths: Iterable[str],
    out_of_scope: Iterable[str],
    forbidden_actions: Iterable[str],
    selection_source: str,
    basis: Iterable[str],
    authority_refs: Iterable[str],
    eligibility_evidence_refs: Iterable[str],
    facts: Iterable[str],
    constraints: Iterable[str],
    assumptions: Iterable[str],
    fundamentals: Iterable[str],
    causal_chain: Iterable[str],
    decision_criteria: Iterable[str],
    request_snapshot: dict[str, str] | None = None,
) -> Path:
    require_id(project_id, "project_id")
    require_id(work_item_id, "work_item_id")
    require_id(task_id, "task_id")
    if ordinal < 1:
        raise GovernanceError("ordinal must be at least 1")
    default_used = False
    rollback_value = rollback.strip()
    if not rollback_value:
        rollback_value = DEFAULT_ROLLBACK
        default_used = True
    out_values = [value.strip() for value in out_of_scope if value.strip()]
    if not out_values:
        out_values = [DEFAULT_OUT_OF_SCOPE]
        default_used = True
    forbidden_values = [value.strip() for value in forbidden_actions if value.strip()]
    if not forbidden_values:
        forbidden_values = [DEFAULT_FORBIDDEN_ACTION]
        default_used = True
    assumption_values = [value.strip() for value in assumptions if value.strip()]
    if not assumption_values:
        assumption_values = [DEFAULT_ASSUMPTION]
        default_used = True
    constraint_values = [value.strip() for value in constraints if value.strip()]
    if not constraint_values:
        constraint_values = [DEFAULT_CONSTRAINT]
        default_used = True
    verification_value = verification.strip()
    if not verification_value:
        verification_value = DEFAULT_VERIFICATION
        default_used = True

    values = {
        "objective": objective.strip(),
        "scope": scope.strip(),
        "acceptance": acceptance.strip(),
        "selected_approach": selected_approach.strip(),
        "alternative_rejected": alternative_rejected.strip(),
        "verification": verification_value,
        "rollback": rollback_value,
    }
    if any(not value for value in values.values()):
        raise GovernanceError("Minimal objective, scope, acceptance, plan, verification, and rollback are required")
    steps = [value.strip() for value in plan_steps if value.strip()]
    if not steps:
        steps = [
            "script default: execute the selected approach within allowed_paths -- "
            f"{values['selected_approach']}"
        ]
        default_used = True
    allowed = [value.strip() for value in allowed_paths if value.strip()]
    bases = [value.strip() for value in basis if value.strip()]
    if default_used and DEFAULT_BASIS not in bases:
        bases.append(DEFAULT_BASIS)
    authorities = list(dict.fromkeys(value.strip() for value in authority_refs if value.strip()))
    evidence = list(
        dict.fromkeys(value.strip() for value in eligibility_evidence_refs if value.strip())
    )
    fact_values = [value.strip() for value in facts if value.strip()]
    if not fact_values:
        fact_values = [DEFAULT_FACT]
        default_used = True
    fundamental_values = [value.strip() for value in fundamentals if value.strip()]
    if len(fundamental_values) < 2:
        fundamental_values = list(
            dict.fromkeys([*fundamental_values, *DEFAULT_FUNDAMENTALS])
        )
        default_used = True
    causal_values = [value.strip() for value in causal_chain if value.strip()]
    if not causal_values:
        causal_values = [DEFAULT_CAUSAL_LINK]
        default_used = True
    criterion_values = [value.strip() for value in decision_criteria if value.strip()]
    if not criterion_values:
        criterion_values = [DEFAULT_DECISION_CRITERION]
        default_used = True
    if not bases:
        bases = [DEFAULT_BASIS]
    elif default_used and DEFAULT_BASIS not in bases:
        bases.append(DEFAULT_BASIS)
    if not allowed or not authorities:
        raise GovernanceError("Minimal allowed paths and authority refs are required")
    # Eligibility evidence stays mandatory and uncounted-down: it is the proof that the
    # Minimal carrier is permitted at all, the schema requires five refs, and inventing
    # a default here would fabricate evidence, which first-principles-method.md 5 forbids.
    if len(evidence) < 5:
        raise GovernanceError("Minimal eligibility requires at least five distinct evidence refs")
    if selection_source not in {"explicit-user", "automatic"}:
        raise GovernanceError("selection_source must be explicit-user or automatic")
    require_minimal_applicability(
        delivery_scenario=delivery_scenario,
        change_surface=change_surface,
    )

    task_dir = (
        project_root.resolve()
        / ".project-governance"
        / "tasks"
        / task_id
    )
    record_path = minimal_record_path(task_dir)
    if record_path.exists() or (task_dir / "before.json").exists():
        raise GovernanceError(f"task already exists: {task_dir}")
    timestamp = now_utc()
    triggers = {extension: "Inactive" for extension in EXTENSIONS}
    content_ref = f".project-governance/tasks/{task_id}/task-record.json"
    record = {
        "schema_version": "6.3-candidate",
        "carrier_version": "minimal-task-record-v1",
        "carrier_mode": "Minimal",
        "meta_types": MINIMAL_META_TYPES,
        "project_id": project_id,
        "work_item_id": work_item_id,
        "task_id": task_id,
        "ordinal": ordinal,
        "depends_on": list(dict.fromkeys(value for value in depends_on if value)),
        "supersedes": list(dict.fromkeys(value for value in supersedes if value)),
        "blocked_by": [],
        "revision": 1,
        "lifecycle_state": "Ready",
        "created_at": timestamp,
        "completed_at": None,
        "selection": {
            "source": selection_source,
            "basis": bases,
            "authority_refs": authorities,
        },
        "eligibility": {
            "risk_level": "Low",
            "reversible": True,
            "single_scope": True,
            "external_system_effect": False,
            "production_release": False,
            "security_privacy_impact": False,
            "extension_triggers": triggers,
            "blocking_unknowns": [],
            "special_gates": [],
            "evidence_refs": evidence,
        },
        "task_contract": {
            "objective": values["objective"],
            "request_snapshot": request_snapshot,  # 必填：用户原话是验收基准
            "clarification": clarification or {
                "state": "Open",
                "mode": "Asked",
                "notice": "clarification was not recorded by the caller",
                "survey_refs": ["none-recorded"],
                "rounds": [],
                "basis": "create_minimal_record was called without a clarification record",
            },
            "scope": values["scope"],
                "out_of_scope": out_values,
                "allowed_paths": allowed,
                "forbidden_actions": forbidden_values,
            "acceptance": values["acceptance"],
            "task_profile": {
                "delivery_scenario": delivery_scenario,
                "development_type": development_type,
                "change_surface": change_surface,
                "risk_level": "Low",
                "extension_triggers": triggers,
            },
            "plan": {
                "selected_approach": values["selected_approach"],
                "alternative_rejected": values["alternative_rejected"],
                "steps": steps,
                "verification": values["verification"],
                "rollback": values["rollback"],
            },
            "first_principles_analysis": {
                "outcome": values["objective"],
                "facts": fact_values,
                "constraints": constraint_values,
                "assumptions": assumption_values,
                "unknowns": [],
                "fundamentals": fundamental_values,
                "causal_chain": causal_values,
                "alternatives": [
                    values["selected_approach"],
                    values["alternative_rejected"],
                ],
                "decision_criteria": criterion_values,
                "selected_approach": values["selected_approach"],
                "validation": values["verification"],
            },
            "source_snapshot": capture_source_snapshot(project_root.resolve()),
        },
        "run_ledger": [],
        "task_outcome": None,
        "artifact_manifest": [
            {
                "meta_type": meta_type,
                "action": "Create/Revise",
                "content_ref": content_ref,
                "outcome": "Planned",
            }
            for meta_type in MINIMAL_META_TYPES
        ],
        "upgrade": {
            "required": False,
            "triggered_at": None,
            "reason": None,
            "basis": None,
            "full_carrier_ref": None,
        },
        "amendments": [],
    }
    require_valid_minimal_record(record, task_dir=task_dir)
    from manage_project_docs import (
        initialize_project_document_layout,
        refresh_project_readmes,
    )

    initialize_project_document_layout(project_root.resolve())
    task_dir.mkdir(parents=True, exist_ok=False)
    atomic_write_json(record_path, record)
    refresh_project_readmes(project_root.resolve())
    return record_path


def append_minimal_event(
    task_dir: Path,
    *,
    event_type: str,
    summary: str,
    status: str,
    evidence_refs: Iterable[str] = (),
) -> dict[str, Any]:
    if event_type not in MINIMAL_EVENT_TYPES:
        raise GovernanceError(f"unsupported Minimal event_type: {event_type}")
    if status not in MINIMAL_STATUSES:
        raise GovernanceError(f"unsupported Minimal event status: {status}")
    record_path = minimal_record_path(task_dir)
    record = read_json(record_path)
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    if record["lifecycle_state"] in {"Completed", "Upgraded"}:
        raise GovernanceError("cannot append to a completed or upgraded Minimal carrier")
    events = record["run_ledger"]
    if not events and event_type != "run_started":
        raise GovernanceError("the first Minimal event must be run_started")
    if events and event_type == "run_started":
        raise GovernanceError("run_started already exists")
    if event_type == "run_finished":
        raise GovernanceError("run_finished is written by close, not append")
    event = {
        "sequence": len(events) + 1,
        "timestamp": now_utc(),
        "event_type": event_type,
        "summary": summary.strip(),
        "status": status,
        "evidence_refs": [value for value in evidence_refs if value],
    }
    if not event["summary"]:
        raise GovernanceError("Minimal event summary is required")
    events.append(event)
    record["lifecycle_state"] = "Frozen"
    record["revision"] += 1
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    atomic_write_json(record_path, record)
    return event


# C10 8.2 owns the controlled relation vocabulary and forbids establishing a formal
# link with uncontrolled semantics. Task succession uses the five that apply between
# tasks; supersedes and replaces already have dedicated fields. The reason is where
# C10's per-relation obligation lands -- affected-by must state impact type, scope and
# time; addresses must state the handled scope.
NEXT_TASK_RELATIONS = ("observed-from", "affected-by", "addresses", "extends", "refines")


def parse_request_snapshot(value: str | None, *, language: str | None) -> dict[str, str] | None:
    """Capture the requester's own words verbatim.

    An objective is the agent's summary; a summary in a language the requester does
    not use, or paraphrased past the point of recognition, cannot be checked by them.
    Storing the original alongside it keeps the summary auditable.
    """

    if not value:
        return None
    text = value.strip()
    if not text:
        raise GovernanceError("--request-snapshot must not be empty")
    detected = (language or "").strip() or ("zh" if re.search(r"[一-鿿]", text) else "en")
    return {"language": detected, "text": text, "captured_at": now_utc()}


def parse_next_tasks(values: Iterable[str], *, task_id: str) -> list[dict[str, str]]:
    """Parse TASK_ID::relation::reason, matching the existing :: argument style."""

    parsed: list[dict[str, str]] = []
    for raw in values:
        parts = [part.strip() for part in str(raw).split("::")]
        if len(parts) != 3 or not all(parts):
            raise GovernanceError(
                f"--next-task must use TASK_ID::relation::reason, got {raw!r}"
            )
        target, relation, reason = parts
        if relation not in NEXT_TASK_RELATIONS:
            raise GovernanceError(
                f"--next-task relation must be one of {', '.join(NEXT_TASK_RELATIONS)}, got {relation!r}"
            )
        if target == task_id:
            raise GovernanceError(f"--next-task cannot point at the task itself: {target}")
        parsed.append({"task_id": target, "relation": relation, "reason": reason})
    seen = [item["task_id"] for item in parsed]
    duplicates = sorted({value for value in seen if seen.count(value) > 1})
    if duplicates:
        raise GovernanceError(f"--next-task repeats a target task: {', '.join(duplicates)}")
    return parsed


def parse_verification(values: Iterable[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for raw in values:
        parts = raw.split("::", 2)
        if len(parts) < 2 or parts[0] not in {
            "Passed",
            "Failed",
            "Blocked",
            "Skipped",
            "Not Applicable",
        }:
            raise GovernanceError("verification must use RESULT::summary[::evidence-ref]")
        checks.append(
            {
                "result": parts[0],
                "summary": parts[1],
                "evidence_refs": [parts[2]] if len(parts) == 3 and parts[2] else [],
            }
        )
    if not checks:
        raise GovernanceError("at least one Minimal verification is required")
    return checks


def close_minimal_record(
    task_dir: Path,
    *,
    status: str,
    established_facts: Iterable[str],
    actual_changes: Iterable[str],
    verification: Iterable[str],
    incomplete_items: Iterable[str] = (),
    next_tasks: Iterable[dict[str, str]] = (),
) -> Path:
    if status not in OUTCOME_STATES:
        raise GovernanceError(f"unsupported Minimal outcome: {status}")
    record_path = minimal_record_path(task_dir)
    record = read_json(record_path)
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    if record["lifecycle_state"] in {"Completed", "Upgraded"}:
        raise GovernanceError("Minimal carrier is already terminal")
    events = record["run_ledger"]
    changes = [value for value in actual_changes if value]
    if (status == "Implemented" or changes) and not events:
        raise GovernanceError("Implemented Minimal work requires run_started")
    checks = parse_verification(verification)
    incomplete: list[dict[str, str]] = []
    for raw in incomplete_items:
        parts = raw.split("::", 4)
        if len(parts) != 5 or any(not part for part in parts):
            raise GovernanceError(
                "incomplete item must use summary::reason::impact::owner::reentry_condition"
            )
        incomplete.append(
            {
                "summary": parts[0],
                "reason": parts[1],
                "impact": parts[2],
                "owner": parts[3],
                "reentry_condition": parts[4],
            }
        )
    if status == "Implemented" and any(item["result"] != "Passed" for item in checks):
        raise GovernanceError("Implemented Minimal work requires all verification results to pass")
    completed_at = now_utc()
    if events:
        events.append(
            {
                "sequence": len(events) + 1,
                "timestamp": completed_at,
                "event_type": "run_finished",
                "summary": f"Minimal task closed as {status}.",
                "status": "succeeded" if status == "Implemented" else "recorded",
                "evidence_refs": [
                    ref
                    for item in checks
                    for ref in item["evidence_refs"]
                ],
            }
        )
    record["task_outcome"] = {
        "status": status,
        "established_facts": [value for value in established_facts if value],
        "actual_changes": changes,
        "verification": checks,
        "incomplete_items": incomplete,
        "completed_at": completed_at,
    }
    derived = [dict(item) for item in next_tasks]
    if derived:
        record["task_outcome"]["next_tasks"] = derived
    record["completed_at"] = completed_at
    record["lifecycle_state"] = "Completed"
    record["revision"] += 1
    for item in record["artifact_manifest"]:
        item["outcome"] = "Created"
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    atomic_write_json(record_path, record)
    return record_path


def mark_minimal_upgrade(
    task_dir: Path,
    *,
    reason: str,
    basis: str,
    full_carrier_ref: str,
) -> dict[str, Any]:
    record_path = minimal_record_path(task_dir)
    record = read_json(record_path)
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    if record["lifecycle_state"] in {"Completed", "Upgraded"}:
        raise GovernanceError("only active Minimal work can upgrade")
    timestamp = now_utc()
    events = record["run_ledger"]
    if not events:
        events.append(
            {
                "sequence": 1,
                "timestamp": timestamp,
                "event_type": "run_started",
                "summary": "Minimal task opened for mandatory upgrade.",
                "status": "started",
                "evidence_refs": [basis],
            }
        )
    events.append(
        {
            "sequence": len(events) + 1,
            "timestamp": timestamp,
            "event_type": "upgrade_triggered",
            "summary": reason,
            "status": "blocked",
            "evidence_refs": [basis],
        }
    )
    record["upgrade"] = {
        "required": True,
        "triggered_at": timestamp,
        "reason": reason,
        "basis": basis,
        "full_carrier_ref": full_carrier_ref,
    }
    record["lifecycle_state"] = "Upgraded"
    record["revision"] += 1
    require_valid_minimal_record(record, task_dir=task_dir.resolve())
    return record


def minimal_record_sha256(record: dict[str, Any]) -> str:
    import json

    payload = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def render_minimal_review(record: dict[str, Any]) -> str:
    outcome = record.get("task_outcome")
    status = outcome.get("status") if isinstance(outcome, dict) else "Active"
    lines = [
        f"# Task {record['task_id']}",
        "",
        "- Carrier: Minimal aggregate (TaskContract + RunLedger + TaskOutcome)",
        f"- Status: {status}",
        f"- Objective: {record['task_contract']['objective']}",
        f"- Scope: {record['task_contract']['scope']}",
        f"- Acceptance: {record['task_contract']['acceptance']}",
        "",
        "## Events",
        "",
    ]
    lines.extend(
        f"- {event['sequence']}: {event['event_type']} — {event['summary']}"
        for event in record["run_ledger"]
    )
    if outcome:
        lines.extend(["", "## Verification", ""])
        lines.extend(
            f"- {item['result']}: {item['summary']}"
            for item in outcome["verification"]
        )
    return "\n".join(lines) + "\n"


# --- Minimal eligibility screening -------------------------------------------
# VC-PPG-DEC-001 16.4 lists nine conditions; minimal-task-record.schema.json pins
# them as const fields. Deciding whether a task may use the Minimal carrier needs
# only the applicability facts whose Yes value would veto one of those conditions
# -- not the full 17-fact Task Profile, which the Minimal record does not even
# carry. Screening on that subset is what lets the carrier be chosen before the
# heavy classification work, instead of after it.
#
# Facts that gate an extension are read from the map so E01-E05 coverage cannot
# drift. The rest are named here because the fact vocabulary and the schema field
# names genuinely differ for two of them.
SCREEN_FACT_TO_CONDITION = {
    "irreversible_change": "reversible",
    "external_system_effect": "external_system_effect",
    "production_release": "production_release",
    "security_privacy_impact": "security_privacy_impact",
    "formal_review_or_gate": "special_gates",
}


def screening_facts() -> dict[str, str]:
    """Fact key -> the eligibility condition its Yes value would veto."""

    mapping = load_tailoring_applicability_map()
    facts = dict(SCREEN_FACT_TO_CONDITION)
    for key, rule in mapping["applicability_facts"].items():
        extension = rule.get("extension")
        if extension:
            facts.setdefault(key, f"extension_triggers.{extension}")
    return facts


def screen_minimal_eligibility(
    *,
    risk_level: str,
    single_scope: bool,
    facts: dict[str, str],
) -> tuple[bool, list[str]]:
    """Return (eligible, reasons). Reasons name the condition that vetoed."""

    mapping = load_tailoring_applicability_map()
    fact_values = set(mapping["controlled_values"]["fact_values"])
    required = screening_facts()
    reasons: list[str] = []
    missing = sorted(set(required) - set(facts))
    if missing:
        reasons.append(
            "not screened: supply --fact for each of " + ", ".join(missing)
        )
    if risk_level != "Low":
        reasons.append(f"risk_level={risk_level} vetoes eligibility; Minimal requires Low")
    if not single_scope:
        reasons.append("single_scope=false vetoes eligibility")
    for key in sorted(set(required) & set(facts)):
        value = facts[key]
        if value not in fact_values:
            reasons.append(f"{key}={value} is not Yes, No or Unknown")
        elif value == "Yes":
            reasons.append(f"{key}=Yes vetoes eligibility condition {required[key]}")
        elif value == "Unknown":
            # VC-PPG-DEC-001 10.2: Unknown may never be read as No, and 16.4 requires
            # blocking_unknowns to be empty.
            reasons.append(
                f"{key}=Unknown vetoes eligibility condition blocking_unknowns; "
                "resolve it or use the full carrier"
            )
    return (not reasons), reasons
