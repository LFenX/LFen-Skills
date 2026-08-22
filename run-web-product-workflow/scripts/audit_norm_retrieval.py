#!/usr/bin/env python3
"""Validate retrieval contracts and measure the legacy rg/Source Pack baseline."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError as exc:  # pragma: no cover - exercised by installation checks
    raise SystemExit("ERROR: jsonschema>=4 with Draft 2020-12 support is required") from exc

from governance_artifacts import (  # noqa: E402
    GovernanceError,
    _write_derived_view,
    embedded_manifest_path,
    governance_root,
    now_utc,
    read_json,
    require_valid_json_document,
    runtime_asset_path,
    sha256_file,
    validate_embedded_manifest,
)
from query_norm_context import (  # noqa: E402
    QueryEnvironment,
    MAX_CLAUSE_ROWS,
    MAX_QUERY_TEXT_CHARS,
    SQLITE_PROGRESS_STEP_LIMIT,
    execute_query,
    expand_for_missing,
    integrity_blockers,
    lane_lookup,
    load_clause_rows,
    load_environment,
    plan_candidates,
    query_digest,
    query_terms,
    required_control_derivation,
    required_controls,
    render_clause_context,
    require_canonical_path,
    run_query_planner_fixtures,
    tailoring_resolution_digest,
    validate_result_semantics,
    validate_query_request,
    write_query_outputs,
)
import query_norm_context as query_gateway  # noqa: E402


SCHEMA_NAMES = (
    "norm-consistency-report.schema.json",
    "norm-index-metadata.schema.json",
    "norm-query.schema.json",
    "norm-query-result.schema.json",
)
EXPECTED_REQUIREMENTS = {f"REQ-NRG-{index:03d}" for index in range(1, 42)}
EXPECTED_ACCEPTANCE = {f"AC-NRG-{index:03d}" for index in range(1, 26)}
EXPECTED_HARD_GATES = {
    "mandatory-clause-recall": ("mandatory_clause_recall", "eq", 1.0),
    "citation-hash-integrity": ("citation_hash_integrity", "eq", 1.0),
    "forbidden-permission-false-allow": ("false_allow_count", "eq", 0),
    "stale-index-blocking": ("stale_index_block_rate", "eq", 1.0),
    "unknown-source-blocking": ("unknown_source_block_rate", "eq", 1.0),
    "p0-p1-silent-truncation": ("p0_p1_silent_truncation_count", "eq", 0),
    "deterministic-replay": ("deterministic_replay_rate", "eq", 1.0),
    "coverage-regression": ("source_standard_profile_coverage", "eq", "22/17/137"),
}
EXPECTED_ROLES = {
    "norm": 22,
    "mapping": 3,
    "schema": 11,
    "skill-reference": 4,
    "evaluation": 2,
    "asset-template": 3,
}
EXPECTED_STRUCTURAL_CHECKS = {
    "manifest-runtime-closure",
    "schema-draft-and-fixtures",
    "semantic-invariants",
    "taxonomy-closure",
    "gold-coverage-closure",
    "mandatory-target-integrity",
    "hard-gate-evaluator-fixtures",
    "legacy-source-pack-regression",
    "cli-contract-regression",
    "budget-baseline-definition",
    "tailoring-source-boundary",
    "output-path-contract",
}
EXPECTED_OUTPUT_PATHS = [
    ".project-governance/tasks/{task_id}/before.json",
    ".project-governance/tasks/{task_id}/run.jsonl",
    ".project-governance/tasks/{task_id}/after.json",
    ".project-governance/generated/contexts/{task_id}/{stage}/norm-packet.json",
    ".project-governance/generated/contexts/{task_id}/{stage}/norm-packet.md",
    ".project-governance/generated/contexts/{task_id}/{stage}/norm-source-pack.md",
    ".project-governance/generated/reviews/{task_id}.md",
    ".project-governance/runtime-cache/norm-index/{index_digest}.sqlite3",
]
SEVERITIES = ("Blocker", "Major", "Minor", "Observation")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(normalize_tree(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def claim_mandatory_target_identity(
    *,
    target_id: str,
    logical_path: str,
    line_start: int,
    line_end: int,
    text_sha256: str,
    locations: set[tuple[str, int, int]],
    text_identities: set[str],
) -> None:
    """Reject denominator inflation through duplicate clause identity."""

    location_key = (logical_path, line_start, line_end)
    if location_key in locations:
        raise GovernanceError(
            f"{target_id}: mandatory target duplicates an existing stable location"
        )
    if text_sha256 in text_identities:
        raise GovernanceError(
            f"{target_id}: mandatory target duplicates an existing clause text identity"
        )
    locations.add(location_key)
    text_identities.add(text_sha256)


def normalize_tree(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalize_tree(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_tree(item) for key, item in value.items()}
    return value


def consistency_audit_body(document: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "report_version",
        "project_id",
        "task_id",
        "scope",
        "inputs",
        "findings",
        "manual_review_inventory",
        "norm_index_ready",
        "protected_assets_unchanged",
    )
    return {key: document[key] for key in keys}


def semantic_errors(
    schema_name: str,
    document: dict[str, Any],
    taxonomy: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if schema_name == "norm-consistency-report.schema.json":
        findings = document["findings"]
        summary = document["summary"]
        if summary["total_findings"] != len(findings):
            errors.append("summary.total_findings does not equal len(findings)")
        severity_counts = {key: 0 for key in SEVERITIES}
        category_counts: dict[str, int] = {}
        for finding in findings:
            severity_counts[finding["severity"]] += 1
            category = finding["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            start, end = finding["line_start"], finding["line_end"]
            if start is not None and end is not None and end < start:
                errors.append(f"{finding['finding_id']}: line_end is before line_start")
        if summary["by_severity"] != severity_counts:
            errors.append("summary.by_severity does not match findings")
        if summary["by_category"] != dict(sorted(category_counts.items())):
            errors.append("summary.by_category does not match findings")
        should_be_ready = (
            document["audit_status"] == "Complete"
            and severity_counts["Blocker"] == 0
            and severity_counts["Major"] == 0
            and document["inputs"]["task_contract_snapshot_verified"] is True
            and document["protected_assets_unchanged"] is True
        )
        if document["norm_index_ready"] is not should_be_ready:
            errors.append("norm_index_ready does not match the fail-closed readiness predicate")
        expected_digest = sha256_bytes(canonical_json_bytes(consistency_audit_body(document)))
        if document["audit_digest"] != expected_digest:
            errors.append("audit_digest does not match the canonical audit body")
    elif schema_name == "norm-index-metadata.schema.json":
        source_ids = document["source_ids"]
        if document["source_count"] != len(source_ids):
            errors.append("source_count does not equal len(source_ids)")
        expected_name = f"{document['index_digest']}.sqlite3"
        if Path(document["storage"]["relative_cache_path"]).name != expected_name:
            errors.append("relative_cache_path filename does not match index_digest")
    elif schema_name == "norm-query.schema.json":
        actions = taxonomy["actions"]
        controls = set(taxonomy["control_types"])
        action_id = document["action"]
        if action_id not in actions:
            errors.append("query action is not registered")
        elif document["stage"] not in actions[action_id]["stages"]:
            errors.append("query stage is not allowed for action")
        unknown_controls = set(document["requested_additional_control_types"]) - controls
        if unknown_controls:
            errors.append(f"query contains unknown controls: {sorted(unknown_controls)}")
    elif schema_name == "norm-query-result.schema.json":
        coverage = document["coverage"]
        required, present, missing = map(set, (coverage["required"], coverage["present"], coverage["missing"]))
        if present & missing:
            errors.append("coverage present and missing overlap")
        if required != present | missing:
            errors.append("coverage present/missing union does not equal required")
        if document["status"] == "Complete" and missing:
            errors.append("Complete result contains missing controls")
        budget = document["budget"]
        soft_overflow = (
            budget["used_chars"] > budget["requested_chars"]
            or budget["sources_used"] > budget["source_limit"]
        )
        if soft_overflow and document["status"] == "Complete":
            errors.append("Complete result exceeds a soft context/source budget")
        if soft_overflow and not budget.get("overflow_reason"):
            errors.append("soft budget overflow has no explicit overflow_reason")
        if budget["escalations_used"] > budget["escalation_limit"]:
            errors.append("budget escalations_used exceeds escalation_limit")
        unique_sources = {item["source_id"] for item in document["citations"]}
        if budget["sources_used"] != len(unique_sources):
            errors.append("sources_used does not equal unique citation sources")
        cited_controls: set[str] = set()
        for ordinal, citation in enumerate(document["citations"], 1):
            cited_controls.update(citation["control_types"])
            if citation["line_end"] < citation["line_start"]:
                errors.append(f"citation {ordinal}: line_end is before line_start")
            expected_chunk = sha256_bytes(citation["text"].encode("utf-8"))
            normalized_heading = unicodedata.normalize("NFC", "\n".join(citation["heading_path"]))
            expected_heading = sha256_bytes(normalized_heading.encode("utf-8"))
            if citation["chunk_sha256"] != expected_chunk:
                errors.append(f"citation {ordinal}: chunk_sha256 does not match text")
            locator_parts = citation["retrieval_locator"].split(":")
            locator_reproducible = (
                len(locator_parts) == 5
                and locator_parts[0] == citation["source_id"]
                and locator_parts[1] == citation["source_sha256"][:8]
                and locator_parts[2] == expected_heading[:8]
                and locator_parts[3].isdigit()
                and int(locator_parts[3]) >= 1
                and locator_parts[4] == expected_chunk[:8]
            )
            if not locator_reproducible:
                errors.append(f"citation {ordinal}: retrieval_locator is not reproducible")
        if not present.issubset(cited_controls):
            errors.append("coverage.present contains controls absent from citations")
        fallback = document["fallback"]
        fallback_kind = fallback["kind"]
        if fallback_kind == "none":
            if any(
                value is not None
                for value in (fallback["source_id"], fallback["page"], fallback["page_count"], fallback["reason"])
            ) or fallback["heading_path"]:
                errors.append("none fallback contains metadata")
        elif fallback_kind == "section":
            if (
                not fallback["source_id"]
                or not fallback["heading_path"]
                or fallback["page"] is not None
                or fallback["page_count"] is not None
                or not fallback["reason"]
            ):
                errors.append("section fallback metadata is incomplete")
        elif fallback_kind == "source":
            if (
                not fallback["source_id"]
                or fallback["page"] is not None
                or fallback["page_count"] is not None
                or not fallback["reason"]
            ):
                errors.append("source fallback metadata is incomplete")
        elif fallback_kind == "paged-source":
            if (
                not fallback["source_id"]
                or not isinstance(fallback["page"], int)
                or not isinstance(fallback["page_count"], int)
                or not fallback["reason"]
            ):
                errors.append("paged-source fallback metadata is incomplete")
            elif fallback["page"] > fallback["page_count"]:
                errors.append("fallback page exceeds page_count")
    else:
        errors.append(f"no semantic validator registered for {schema_name}")
    return errors


def evaluate_gate(gate: dict[str, Any], observation: dict[str, Any]) -> bool:
    evaluator = gate["evaluator_id"]
    threshold = gate["threshold"]
    if evaluator == "ratio-eq":
        denominator = observation.get("denominator")
        numerator = observation.get("numerator")
        if not isinstance(denominator, int) or denominator <= 0 or not isinstance(numerator, int):
            raise GovernanceError(f"{gate['gate_id']}: invalid ratio observation")
        value: Any = numerator / denominator
    elif evaluator in {"count-eq", "string-eq"}:
        value = observation.get("value")
    else:
        raise GovernanceError(f"{gate['gate_id']}: unknown evaluator {evaluator!r}")
    return gate["operator"] == "eq" and value == threshold


def failing_observation(gate: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(observation)
    if gate["evaluator_id"] == "ratio-eq":
        mutated["numerator"] = max(0, mutated["denominator"] - 1)
    elif gate["evaluator_id"] == "count-eq":
        mutated["value"] = int(gate["threshold"]) + 1
    else:
        mutated["value"] = "invalid-coverage"
    return mutated


def default_project_root() -> Path:
    for candidate in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (candidate / ".project-governance").is_dir():
            return candidate
    raise GovernanceError("cannot locate project root containing .project-governance")


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[position]


def round_up(value: float, quantum: int) -> int:
    return int(math.ceil(value / quantum) * quantum)


def pointer_parent(document: Any, pointer: str) -> tuple[Any, str]:
    if not pointer.startswith("/"):
        raise GovernanceError(f"invalid JSON Pointer: {pointer}")
    tokens = [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]
    if not tokens or tokens == [""]:
        raise GovernanceError("fixture mutation cannot target the document root")
    current = document
    for token in tokens[:-1]:
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise GovernanceError(f"JSON Pointer traverses a scalar at {token!r}")
    return current, tokens[-1]


def apply_mutation(document: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(document)
    operations = mutation.get("operations", [mutation])
    if not isinstance(operations, list) or not operations:
        raise GovernanceError("fixture mutation operations must be a non-empty array")
    for item in operations:
        parent, token = pointer_parent(mutated, item["path"])
        operation = item["op"]
        if operation == "remove":
            if isinstance(parent, list):
                del parent[int(token)]
            else:
                del parent[token]
        elif operation in {"add", "replace"}:
            value = copy.deepcopy(item.get("value"))
            if isinstance(parent, list):
                index = int(token)
                if operation == "add":
                    parent.insert(index, value)
                else:
                    parent[index] = value
            else:
                parent[token] = value
        else:
            raise GovernanceError(f"unsupported fixture mutation operation: {operation}")
    return mutated


def validate_contracts(
    project_root: Path | None = None,
    *,
    verify_project_snapshots: bool = True,
) -> dict[str, Any]:
    resolved_project_root = (project_root or default_project_root()).resolve()
    executed_checks: set[str] = set()
    errors = validate_embedded_manifest()
    if errors:
        raise GovernanceError("; ".join(errors))
    manifest = read_json(embedded_manifest_path())
    role_counts: dict[str, int] = {}
    for item in manifest["files"]:
        role = item["role"]
        role_counts[role] = role_counts.get(role, 0) + 1
    if role_counts != EXPECTED_ROLES:
        raise GovernanceError(f"runtime role closure mismatch: expected={EXPECTED_ROLES}, actual={role_counts}")
    executed_checks.add("manifest-runtime-closure")

    taxonomy_path = runtime_asset_path("mappings/norm-action-taxonomy.json")
    gold_path = runtime_asset_path("evaluations/norm-retrieval-gold.json")
    tailoring_path = runtime_asset_path("mappings/tailoring-applicability-map.json")
    taxonomy = read_json(taxonomy_path)
    gold = read_json(gold_path)
    tailoring = read_json(tailoring_path)
    known_source_ids = {item.get("id") for item in tailoring.get("source_catalog", [])}
    if len(known_source_ids) != 22 or None in known_source_ids:
        raise GovernanceError("tailoring source catalog must contain 22 unique Source IDs")
    executed_checks.add("tailoring-source-boundary")

    schema_validators: dict[str, Draft202012Validator] = {}
    schema_ids: set[str] = set()
    fixture_counts = {"positive": 0, "schema_negative": 0, "semantic_negative": 0}
    for schema_name in SCHEMA_NAMES:
        schema = read_json(runtime_asset_path(f"schemas/{schema_name}"))
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise GovernanceError(f"{schema_name}: invalid Draft 2020-12 schema: {exc.message}") from exc
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id or schema_id in schema_ids:
            raise GovernanceError(f"{schema_name}: missing or duplicate $id")
        invariants = schema.get("x-lfen-semantic-invariants")
        if not isinstance(invariants, list) or not invariants:
            raise GovernanceError(f"{schema_name}: semantic invariant declarations are missing")
        schema_ids.add(schema_id)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        schema_validators[schema_name] = validator
        fixture = gold.get("schema_fixtures", {}).get(schema_name)
        if not isinstance(fixture, dict):
            raise GovernanceError(f"gold set has no fixture for {schema_name}")
        valid_document = fixture.get("valid")
        positive_errors = sorted(validator.iter_errors(valid_document), key=lambda item: list(item.path))
        if positive_errors:
            raise GovernanceError(f"{schema_name}: positive fixture failed: {positive_errors[0].message}")
        positive_semantic_errors = semantic_errors(schema_name, valid_document, taxonomy)
        if positive_semantic_errors:
            raise GovernanceError(f"{schema_name}: positive semantic fixture failed: {positive_semantic_errors[0]}")
        fixture_counts["positive"] += 1
        valid_variants = fixture.get("valid_variants", [])
        if not isinstance(valid_variants, list):
            raise GovernanceError(f"{schema_name}: valid_variants must be an array")
        variant_ids: set[str] = set()
        for variant in valid_variants:
            fixture_id = variant.get("fixture_id")
            if not isinstance(fixture_id, str) or not fixture_id or fixture_id in variant_ids:
                raise GovernanceError(f"{schema_name}: invalid or duplicate positive variant id")
            variant_ids.add(fixture_id)
            variant_document = apply_mutation(valid_document, variant)
            variant_errors = sorted(validator.iter_errors(variant_document), key=lambda item: list(item.path))
            if variant_errors:
                raise GovernanceError(f"{schema_name}: positive variant {fixture_id} failed: {variant_errors[0].message}")
            variant_semantic_errors = semantic_errors(schema_name, variant_document, taxonomy)
            if variant_semantic_errors:
                raise GovernanceError(
                    f"{schema_name}: positive variant {fixture_id} failed semantic validation: "
                    f"{variant_semantic_errors[0]}"
                )
            fixture_counts["positive"] += 1
        mutations = fixture.get("invalid_mutations")
        if not isinstance(mutations, list) or not mutations:
            raise GovernanceError(f"{schema_name}: negative fixtures are missing")
        mutation_ids: set[str] = set()
        for mutation in mutations:
            fixture_id = mutation.get("fixture_id")
            if not isinstance(fixture_id, str) or not fixture_id or fixture_id in mutation_ids:
                raise GovernanceError(f"{schema_name}: invalid or duplicate negative fixture id")
            mutation_ids.add(fixture_id)
            invalid_document = apply_mutation(valid_document, mutation)
            if not list(validator.iter_errors(invalid_document)):
                raise GovernanceError(f"{schema_name}: negative fixture {fixture_id} unexpectedly passed")
            fixture_counts["schema_negative"] += 1
        semantic_mutations = fixture.get("semantic_invalid_mutations")
        if not isinstance(semantic_mutations, list) or not semantic_mutations:
            raise GovernanceError(f"{schema_name}: semantic negative fixtures are missing")
        semantic_ids: set[str] = set()
        for mutation in semantic_mutations:
            fixture_id = mutation.get("fixture_id")
            if not isinstance(fixture_id, str) or not fixture_id or fixture_id in semantic_ids:
                raise GovernanceError(f"{schema_name}: invalid or duplicate semantic fixture id")
            semantic_ids.add(fixture_id)
            invalid_document = apply_mutation(valid_document, mutation)
            schema_errors = list(validator.iter_errors(invalid_document))
            if schema_errors:
                raise GovernanceError(
                    f"{schema_name}: semantic fixture {fixture_id} must pass JSON Schema before semantic validation: "
                    f"{schema_errors[0].message}"
                )
            if not semantic_errors(schema_name, invalid_document, taxonomy):
                raise GovernanceError(f"{schema_name}: semantic fixture {fixture_id} unexpectedly passed")
            fixture_counts["semantic_negative"] += 1
    executed_checks.update({"schema-draft-and-fixtures", "semantic-invariants"})

    budget_names = taxonomy.get("budget_profile_names")
    if budget_names != ["compact", "standard", "extended", "source-required"]:
        raise GovernanceError("action taxonomy budget profiles are not the frozen ordered set")
    control_types = taxonomy.get("control_types")
    actions = taxonomy.get("actions")
    if not isinstance(control_types, dict) or not control_types or not isinstance(actions, dict) or not actions:
        raise GovernanceError("action taxonomy control types or actions are missing")
    known_controls = set(control_types)
    stages = {f"S{index}" for index in range(1, 9)}
    for action_id, action in actions.items():
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", action_id) or not isinstance(action, dict):
            raise GovernanceError(f"invalid action taxonomy member: {action_id}")
        if not set(action.get("stages", [])).issubset(stages):
            raise GovernanceError(f"{action_id}: unknown stage")
        required = set(action.get("required_control_types", []))
        pinned = set(action.get("pinned_control_types", []))
        if not required or not pinned or not required.issubset(known_controls) or not pinned.issubset(known_controls):
            raise GovernanceError(f"{action_id}: invalid required or pinned controls")
    p0_controls = set(taxonomy.get("priority_rules", {}).get("P0", []))
    if not {"authority", "permission", "prohibition", "gate", "integrity"}.issubset(p0_controls):
        raise GovernanceError("action taxonomy P0 does not close mandatory pinned controls")
    if taxonomy.get("priority_rules", {}).get("silent_truncation_forbidden") != ["P0", "P1"]:
        raise GovernanceError("action taxonomy must forbid silent truncation for P0/P1")
    for priority in ("P0", "P1", "P2", "P3"):
        priority_controls = taxonomy.get("priority_rules", {}).get(priority)
        if not isinstance(priority_controls, list) or not set(priority_controls).issubset(known_controls):
            raise GovernanceError(f"action taxonomy {priority} references undeclared controls")
    executed_checks.add("taxonomy-closure")
    budget_probe = derive_budgets(
        navigation_chars=7452,
        source_pack_chars=712038,
        selected_source_count=16,
        corpus_source_count=22,
        hit_counts=[1, 5, 10, 20, 40, 80, 160],
    )
    probe_profiles = budget_probe["profiles"]
    if list(probe_profiles) != budget_names or any(
        probe_profiles[left]["context_chars"] > probe_profiles[right]["context_chars"]
        for left, right in zip(budget_names, budget_names[1:])
    ):
        raise GovernanceError("budget derivation does not preserve the frozen ordered profiles")
    executed_checks.add("budget-baseline-definition")

    requirement_coverage = gold.get("requirement_coverage")
    acceptance_coverage = gold.get("acceptance_coverage")
    if not isinstance(requirement_coverage, dict) or set(requirement_coverage) != EXPECTED_REQUIREMENTS:
        raise GovernanceError("gold requirement coverage must close REQ-NRG-001..041 exactly")
    if not isinstance(acceptance_coverage, dict) or set(acceptance_coverage) != EXPECTED_ACCEPTANCE:
        raise GovernanceError("gold acceptance coverage must close AC-NRG-001..025 exactly")
    cases = gold.get("cases")
    if not isinstance(cases, list) or not cases:
        raise GovernanceError("gold cases are missing")
    case_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_by_id:
            raise GovernanceError("gold case IDs must be non-empty and unique")
        query = case.get("query")
        if not isinstance(query, dict) or query.get("action") not in actions:
            raise GovernanceError(f"{case_id}: unknown action")
        action = actions[query["action"]]
        if query.get("stage") not in action["stages"]:
            raise GovernanceError(f"{case_id}: stage is not valid for action {query['action']}")
        if query.get("budget_profile") not in budget_names:
            raise GovernanceError(f"{case_id}: unknown budget profile")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise GovernanceError(f"{case_id}: expected result is missing")
        if not set(expected.get("source_ids", [])).issubset(known_source_ids):
            raise GovernanceError(f"{case_id}: expected result contains an unknown Source ID")
        if not set(expected.get("control_types", [])).issubset(known_controls):
            raise GovernanceError(f"{case_id}: expected result contains an unknown control type")
        case_by_id[case_id] = case
    required_language_categories = {
        "english-natural-synonym",
        "double-negative-prohibition",
        "typo-tolerance",
    }
    actual_categories = {case.get("category") for case in cases}
    if not required_language_categories.issubset(actual_categories):
        raise GovernanceError("gold set lacks English synonym, double-negative, or typo-tolerance cases")

    structural_registry = gold.get("structural_check_registry")
    if not isinstance(structural_registry, list) or set(structural_registry) != EXPECTED_STRUCTURAL_CHECKS:
        raise GovernanceError("gold structural check registry does not match the executable closure")
    for requirement_id, coverage in requirement_coverage.items():
        if not isinstance(coverage, dict) or not coverage.get("structural_checks"):
            raise GovernanceError(f"{requirement_id}: structural coverage is missing")
        if not set(coverage["structural_checks"]).issubset(EXPECTED_STRUCTURAL_CHECKS):
            raise GovernanceError(f"{requirement_id}: structural coverage references an unregistered check")
        if not coverage.get("case_ids") or not set(coverage["case_ids"]).issubset(case_by_id):
            raise GovernanceError(f"{requirement_id}: gold case coverage is invalid")
    for acceptance_id, case_ids in acceptance_coverage.items():
        if not isinstance(case_ids, list) or not case_ids or not set(case_ids).issubset(case_by_id):
            raise GovernanceError(f"{acceptance_id}: gold case coverage is invalid")
    executed_checks.add("gold-coverage-closure")

    mandatory_targets = gold.get("mandatory_clause_targets")
    if not isinstance(mandatory_targets, list) or len(mandatory_targets) < 12:
        raise GovernanceError("gold mandatory clause denominator must contain at least 12 stable targets")
    target_ids: set[str] = set()
    target_case_ids: set[str] = set()
    target_locations: set[tuple[str, int, int]] = set()
    target_text_identities: set[str] = set()
    for target in mandatory_targets:
        target_id = target.get("target_id")
        if not isinstance(target_id, str) or not target_id or target_id in target_ids:
            raise GovernanceError("mandatory target IDs must be non-empty and unique")
        target_ids.add(target_id)
        logical_path = target.get("logical_path")
        if not isinstance(logical_path, str):
            raise GovernanceError(f"{target_id}: logical_path is missing")
        source_path = runtime_asset_path(logical_path)
        if sha256_file(source_path) != target.get("source_sha256"):
            raise GovernanceError(f"{target_id}: source SHA-256 is stale")
        if not source_path.name.startswith(f"{target.get('source_id')}_"):
            raise GovernanceError(f"{target_id}: Source ID does not match logical path")
        lines = source_path.read_text(encoding="utf-8").splitlines()
        start, end = target.get("line_start"), target.get("line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start or end > len(lines):
            raise GovernanceError(f"{target_id}: invalid stable line range")
        payload = "\n".join(lines[start - 1:end])
        text_identity = sha256_bytes(payload.encode("utf-8"))
        if text_identity != target.get("text_sha256"):
            raise GovernanceError(f"{target_id}: line-range text SHA-256 is stale")
        claim_mandatory_target_identity(
            target_id=target_id,
            logical_path=logical_path,
            line_start=start,
            line_end=end,
            text_sha256=text_identity,
            locations=target_locations,
            text_identities=target_text_identities,
        )
        headings = target.get("heading_path")
        if not isinstance(headings, list) or not headings or not all(isinstance(item, str) and item for item in headings):
            raise GovernanceError(f"{target_id}: heading path is missing")
        if not set(target.get("control_types", [])).issubset(known_controls):
            raise GovernanceError(f"{target_id}: unknown control type")
        case_ids = target.get("case_ids")
        if not isinstance(case_ids, list) or not case_ids or not set(case_ids).issubset(case_by_id):
            raise GovernanceError(f"{target_id}: target has no valid gold case denominator")
        target_case_ids.update(case_ids)
    declared_case_targets: set[str] = set()
    for case in cases:
        expected_targets = case.get("expected", {}).get("mandatory_target_ids", [])
        if not isinstance(expected_targets, list) or not set(expected_targets).issubset(target_ids):
            raise GovernanceError(f"{case['case_id']}: expected mandatory targets are invalid")
        declared_case_targets.update(expected_targets)
    if not declared_case_targets or not declared_case_targets.issubset(target_ids):
        raise GovernanceError("gold cases do not bind mandatory targets")
    executed_checks.add("mandatory-target-integrity")

    hard_gates = gold.get("hard_gates")
    hard_gate_by_id = {
        item.get("gate_id"): (item.get("metric"), item.get("operator"), item.get("threshold"))
        for item in hard_gates
    } if isinstance(hard_gates, list) else {}
    if hard_gate_by_id != EXPECTED_HARD_GATES or len(hard_gates) != len(EXPECTED_HARD_GATES):
        raise GovernanceError("gold hard gates do not match RQS-0001 §8")
    observations = gold.get("hard_gate_fixture_observations")
    if not isinstance(observations, dict) or set(observations) != {item["metric"] for item in hard_gates}:
        raise GovernanceError("gold hard gate observations do not close every metric")
    hard_gate_negative_count = 0
    for gate in hard_gates:
        for key in ("evaluator_id", "case_ids", "denominator", "aggregation"):
            if not gate.get(key):
                raise GovernanceError(f"{gate['gate_id']}: executable gate field {key} is missing")
        if not set(gate["case_ids"]).issubset(case_by_id):
            raise GovernanceError(f"{gate['gate_id']}: gate case denominator is invalid")
        observation = observations[gate["metric"]]
        if not evaluate_gate(gate, observation):
            raise GovernanceError(f"{gate['gate_id']}: passing gate fixture failed")
        if evaluate_gate(gate, failing_observation(gate, observation)):
            raise GovernanceError(f"{gate['gate_id']}: failing gate fixture unexpectedly passed")
        hard_gate_negative_count += 1
    executed_checks.add("hard-gate-evaluator-fixtures")

    compatibility = gold.get("compatibility_baselines")
    if not isinstance(compatibility, dict) or compatibility.get("output_paths") != EXPECTED_OUTPUT_PATHS:
        raise GovernanceError("output path compatibility contract changed")
    executed_checks.add("output-path-contract")
    t008_results: dict[str, Any] = {}
    if verify_project_snapshots:
        for key in ("source_pack", "norm_packet"):
            expected = compatibility.get("t008_s5", {}).get(key)
            if not isinstance(expected, dict):
                raise GovernanceError(f"T-008 S5 compatibility snapshot missing: {key}")
            path = (resolved_project_root / expected["path"]).resolve()
            try:
                path.relative_to(resolved_project_root)
            except ValueError as exc:
                raise GovernanceError(f"T-008 snapshot path escapes project root: {expected['path']}") from exc
            if not path.is_file():
                raise GovernanceError(f"T-008 snapshot is missing: {expected['path']}")
            payload = path.read_text(encoding="utf-8")
            actual = {
                "path": expected["path"],
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "chars": len(payload),
            }
            if key == "source_pack":
                actual["source_count"] = len(re.findall(r"^<!-- SOURCE-BEGIN ", payload, flags=re.MULTILINE))
            if actual != expected:
                raise GovernanceError(f"T-008 S5 {key} compatibility snapshot changed: expected={expected}, actual={actual}")
            t008_results[key] = actual
        executed_checks.add("legacy-source-pack-regression")

    cli_results: list[dict[str, Any]] = []
    scripts_dir = Path(__file__).resolve().parent
    for expected in compatibility.get("cli_help_contracts", []):
        script = scripts_dir / expected["script"]
        process = subprocess.run(
            [sys.executable, "-B", str(script), "--help"],
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if process.returncode != 0:
            raise GovernanceError(f"{expected['script']}: --help failed with {process.returncode}")
        help_text = process.stdout.replace("\r\n", "\n")
        actual_options = sorted(set(re.findall(r"(?<!\w)--[a-z][a-z0-9-]*", help_text)))
        actual_hash = sha256_bytes(help_text.encode("utf-8"))
        if actual_hash != expected.get("help_sha256") or actual_options != expected.get("options"):
            raise GovernanceError(f"{expected['script']}: CLI help contract changed")
        cli_results.append({"script": expected["script"], "help_sha256": actual_hash, "options": actual_options})
    if len(cli_results) != 15:
        raise GovernanceError("CLI compatibility closure must contain 15 scripts")
    executed_checks.add("cli-contract-regression")

    referenced_checks = {
        check
        for coverage in requirement_coverage.values()
        for check in coverage["structural_checks"]
    }
    expected_executed_checks = (
        referenced_checks
        if verify_project_snapshots
        else referenced_checks - {"legacy-source-pack-regression"}
    )
    if expected_executed_checks != executed_checks:
        raise GovernanceError(
            f"structural checks are not exactly covered and executed: referenced={sorted(expected_executed_checks)}, "
            f"executed={sorted(executed_checks)}"
        )

    return {
        "manifest_files": len(manifest["files"]),
        "role_counts": role_counts,
        "schema_count": len(schema_validators),
        "schema_ids": sorted(schema_ids),
        "fixture_counts": fixture_counts,
        "action_count": len(actions),
        "control_type_count": len(control_types),
        "gold_case_count": len(cases),
        "requirement_coverage": len(requirement_coverage),
        "acceptance_coverage": len(acceptance_coverage),
        "hard_gate_count": len(hard_gates),
        "hard_gate_negative_count": hard_gate_negative_count,
        "mandatory_target_count": len(mandatory_targets),
        "mandatory_target_case_count": len(target_case_ids),
        "executed_structural_checks": sorted(executed_checks),
        "verification_mode": (
            "norm-development" if verify_project_snapshots else "protected-runtime"
        ),
        "skipped_structural_checks": (
            [] if verify_project_snapshots else ["legacy-source-pack-regression"]
        ),
        "compatibility": {
            "t008_s5": t008_results,
            "cli_contract_count": len(cli_results),
            "cli_contracts": cli_results,
            "output_paths": EXPECTED_OUTPUT_PATHS,
        },
        "taxonomy_sha256": sha256_file(taxonomy_path),
        "gold_sha256": sha256_file(gold_path),
    }


def run_rg(pattern: str, source_pack: Path) -> tuple[list[dict[str, Any]], str]:
    process = subprocess.run(
        ["rg", "--json", "--line-number", "--ignore-case", pattern, str(source_pack)],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if process.returncode not in {0, 1}:
        raise GovernanceError(f"rg failed ({process.returncode}): {process.stderr.strip()}")
    matches: list[dict[str, Any]] = []
    for raw_line in process.stdout.splitlines():
        event = json.loads(raw_line)
        if event.get("type") != "match":
            continue
        data = event["data"]
        matches.append(
            {
                "line_number": data["line_number"],
                "text": unicodedata.normalize("NFC", data["lines"]["text"].rstrip("\r\n")),
            }
        )
    digest = sha256_bytes(canonical_json_bytes(matches))
    return matches, digest


def measure_file_read(path: Path, repetitions: int) -> dict[str, Any]:
    durations: list[float] = []
    digests: list[str] = []
    for _ in range(repetitions + 1):
        started = time.perf_counter_ns()
        payload = path.read_bytes()
        digest = sha256_bytes(payload)
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
        if durations or len(digests) > 0:
            durations.append(elapsed_ms)
        digests.append(digest)
    measured_digests = digests[1:]
    return {
        "repetitions": repetitions,
        "p50_ms": round(statistics.median(durations), 4),
        "p95_ms": round(percentile(durations, 0.95), 4),
        "digest": measured_digests[0],
        "replay_consistent": len(set(measured_digests)) == 1,
    }


def derive_budgets(
    *,
    navigation_chars: int,
    source_pack_chars: int,
    selected_source_count: int,
    corpus_source_count: int,
    hit_counts: list[int],
) -> dict[str, Any]:
    p50_hits = percentile([float(value) for value in hit_counts], 0.50)
    p75_hits = percentile([float(value) for value in hit_counts], 0.75)
    p95_hits = percentile([float(value) for value in hit_counts], 0.95)
    compact_candidates = min(40, max(20, round_up(p50_hits, 5)))
    standard_candidates = min(80, max(40, round_up(p75_hits, 10)))
    extended_candidates = min(160, max(80, round_up(p95_hits, 10)))
    compact_chars = min(8000, max(6000, round_up(navigation_chars * 0.75, 1000)))
    standard_chars = min(16000, max(12000, round_up(navigation_chars * 1.25, 1000)))
    extended_chars = min(32000, max(24000, round_up(navigation_chars * 2.5, 1000)))
    mean_source_chars = source_pack_chars / max(1, selected_source_count)
    source_page_chars = min(48000, max(32000, round_up(mean_source_chars, 1000)))
    profiles = {
        "compact": {"candidate_limit": compact_candidates, "context_chars": compact_chars, "source_limit": 2, "escalation_limit": 1},
        "standard": {"candidate_limit": standard_candidates, "context_chars": standard_chars, "source_limit": min(4, corpus_source_count), "escalation_limit": 2},
        "extended": {"candidate_limit": extended_candidates, "context_chars": extended_chars, "source_limit": min(8, corpus_source_count), "escalation_limit": 4},
        "source-required": {"candidate_limit": max(160, extended_candidates), "context_chars": source_page_chars, "source_limit": corpus_source_count, "escalation_limit": corpus_source_count * 2},
    }
    for profile in profiles.values():
        profile["estimated_tokens"] = math.ceil(profile["context_chars"] / 4)
    return {
        "status": "T-013-measured-candidate",
        "chars_per_token_assumption": 4,
        "observed": {
            "navigation_chars": navigation_chars,
            "source_pack_chars": source_pack_chars,
            "selected_source_count": selected_source_count,
            "corpus_source_count": corpus_source_count,
            "mean_source_chars": round(mean_source_chars, 2),
            "rg_hit_count_p50": int(p50_hits),
            "rg_hit_count_p75": int(p75_hits),
            "rg_hit_count_p95": int(p95_hits),
        },
        "derivation": [
            "candidate_limit derives from measured legacy rg hit-count p50/p75/p95 with explicit caps",
            "context_chars derives from the measured Norm Packet navigation size with 0.75x/1.25x/2.5x multipliers and bounded floors/caps",
            "source-required source_limit derives from the Manifest corpus closure, not the selected task subset",
            "source-required context_chars is a page budget derived from mean selected-source size and capped at 48000 characters; full sources remain paged, never truncated",
            "estimated_tokens uses a declared 4 chars/token planning assumption and is not a tokenizer measurement",
        ],
        "profiles": profiles,
    }


def benchmark(source_pack: Path, norm_packet: Path, repetitions: int) -> dict[str, Any]:
    if repetitions < 3:
        raise GovernanceError("benchmark repetitions must be at least 3")
    if not source_pack.is_file() or not norm_packet.is_file():
        raise GovernanceError("source pack and norm packet must both exist")
    gold = read_json(runtime_asset_path("evaluations/norm-retrieval-gold.json"))
    source_payload = source_pack.read_text(encoding="utf-8")
    navigation_payload = norm_packet.read_text(encoding="utf-8")
    source_count = len(re.findall(r"^<!-- SOURCE-BEGIN ", source_payload, flags=re.MULTILINE))
    if source_count < 1:
        raise GovernanceError("source pack contains no SOURCE-BEGIN markers")

    rg_cases: list[dict[str, Any]] = []
    all_hit_counts: list[int] = []
    for case in gold["cases"]:
        if not case.get("benchmark"):
            continue
        pattern = case.get("legacy_pattern")
        if not isinstance(pattern, str) or not pattern:
            raise GovernanceError(f"{case['case_id']}: benchmark case has no legacy_pattern")
        durations: list[float] = []
        digests: list[str] = []
        measured_matches: list[dict[str, Any]] | None = None
        for index in range(repetitions + 1):
            started = time.perf_counter_ns()
            matches, digest = run_rg(pattern, source_pack)
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            if index == 0:
                continue
            durations.append(elapsed_ms)
            digests.append(digest)
            measured_matches = matches
        if measured_matches is None or not measured_matches:
            raise GovernanceError(f"{case['case_id']}: legacy rg pattern returned no hits: {pattern}")
        if len(set(digests)) != 1:
            raise GovernanceError(f"{case['case_id']}: legacy rg replay digest changed")
        hit_count = len(measured_matches)
        all_hit_counts.append(hit_count)
        rg_cases.append(
            {
                "case_id": case["case_id"],
                "pattern": pattern,
                "hit_count": hit_count,
                "matched_chars": sum(len(item["text"]) for item in measured_matches),
                "p50_ms": round(statistics.median(durations), 4),
                "p95_ms": round(percentile(durations, 0.95), 4),
                "result_digest": digests[0],
                "replay_consistent": True,
            }
        )

    manifest = read_json(embedded_manifest_path())
    corpus_source_count = sum(1 for item in manifest["files"] if item.get("role") == "norm")
    if corpus_source_count != 22:
        raise GovernanceError(f"runtime norm corpus must close at 22 sources, got {corpus_source_count}")
    rg_version = subprocess.run(
        ["rg", "--version"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    ).stdout.splitlines()[0]
    budget_recommendations = derive_budgets(
        navigation_chars=len(navigation_payload),
        source_pack_chars=len(source_payload),
        selected_source_count=source_count,
        corpus_source_count=corpus_source_count,
        hit_counts=all_hit_counts,
    )
    return {
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "rg": rg_version,
            "clock": "time.perf_counter_ns",
            "cache_model": "one warm-up followed by measured warm-cache repetitions",
            "network": "not used",
        },
        "source_pack": {
            "path": str(source_pack.resolve()),
            "bytes": source_pack.stat().st_size,
            "chars": len(source_payload),
            "lines": len(source_payload.splitlines()),
            "source_count": source_count,
            "sha256": sha256_file(source_pack),
            "read": measure_file_read(source_pack, repetitions),
        },
        "norm_packet": {
            "path": str(norm_packet.resolve()),
            "bytes": norm_packet.stat().st_size,
            "chars": len(navigation_payload),
            "lines": len(navigation_payload.splitlines()),
            "sha256": sha256_file(norm_packet),
            "read": measure_file_read(norm_packet, repetitions),
        },
        "legacy_rg": {
            "command": "rg --json --line-number --ignore-case <pattern> <source-pack>",
            "repetitions": repetitions,
            "warmups": 1,
            "case_count": len(rg_cases),
            "all_replays_consistent": all(item["replay_consistent"] for item in rg_cases),
            "overall_p50_ms": round(statistics.median(item["p50_ms"] for item in rg_cases), 4),
            "overall_p95_ms": round(percentile([item["p95_ms"] for item in rg_cases], 0.95), 4),
            "cases": rg_cases,
        },
        "budget_recommendations": budget_recommendations,
    }


def full_gold_request(case: dict[str, Any], environment: QueryEnvironment) -> dict[str, Any]:
    return {
        "schema_version": "6.3-candidate",
        "task_id": environment.task_contract["task_id"],
        **case["query"],
        "tailoring_resolution_sha256": environment.tailoring_sha256,
        "normative_sources_sha256": environment.index_metadata["normative_sources_sha256"],
        "requested_additional_control_types": case["query"].get(
            "requested_additional_control_types", []
        ),
    }


def staged_fixture_environment(
    environment: QueryEnvironment, stage: str
) -> QueryEnvironment:
    """Create an in-memory, stage-consistent Gold fixture without publishing it."""
    current_stage = environment.task_contract["tailoring_resolution"]["stage"]
    if stage == current_stage:
        return environment
    task_contract = copy.deepcopy(environment.task_contract)
    task_contract["tailoring_resolution"]["stage"] = stage
    norm_packet = copy.deepcopy(environment.norm_packet)
    norm_packet["stage"] = stage
    return replace(
        environment,
        task_contract=task_contract,
        norm_packet=norm_packet,
        tailoring_sha256=tailoring_resolution_digest(
            task_contract["tailoring_resolution"]
        ),
    )


def citation_hits_target(citation: dict[str, Any], target: dict[str, Any]) -> bool:
    return (
        citation["source_id"] == target["source_id"]
        and citation["line_start"] <= target["line_end"]
        and citation["line_end"] >= target["line_start"]
    )


def expected_outcome_matches(expected: str, actual: str, fallback_kind: str) -> bool:
    if expected == "Schema-invalid":
        return actual == expected
    if expected == "Blocked-on-source-injection":
        return actual == expected
    if expected == "Expanded-not-truncated":
        return actual == "Expanded"
    if expected == "Expanded-paged-source":
        return actual == "Expanded" and fallback_kind == "paged-source"
    if expected.startswith("Blocked-") or expected.startswith("Blocked "):
        return actual == "Blocked"
    return actual == expected


def write_immutable_evidence_snapshot(
    *,
    root: Path,
    output_dir: Path,
    stem: str,
    content: str,
    project_id: str,
    task_id: str,
    view_kind: str,
    sources: list[Path],
    generated_at: str,
    _lock_held: bool = False,
    _verify_only: bool = False,
) -> Path:
    if root.name != ".project-governance":
        raise GovernanceError("immutable evidence root must be the project .project-governance directory")
    try:
        content_document = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GovernanceError("immutable evaluation snapshot content must be JSON") from exc
    if (
        isinstance(content_document, dict)
        and "generated_at" in content_document
        and content_document["generated_at"] != generated_at
    ):
        raise GovernanceError(
            "evaluation snapshot envelope generated_at must match content generated_at"
        )
    content_digest = sha256_bytes(content.encode("utf-8"))
    snapshot_path = output_dir / "snapshots" / f"{stem}-{content_digest}.json"
    envelope_path = snapshot_path.with_suffix(snapshot_path.suffix + ".view.json")
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    if not _lock_held:
        lock_path = query_gateway.publication_lock_path(snapshot_path)
        with query_gateway.publication_lock(lock_path):
            write_immutable_evidence_snapshot(
                root=root,
                output_dir=output_dir,
                stem=stem,
                content=content,
                project_id=project_id,
                task_id=task_id,
                view_kind=view_kind,
                sources=sources,
                generated_at=generated_at,
                _lock_held=True,
            )
        return write_immutable_evidence_snapshot(
            root=root,
            output_dir=output_dir,
            stem=stem,
            content=content,
            project_id=project_id,
            task_id=task_id,
            view_kind=view_kind,
            sources=sources,
            generated_at=generated_at,
            _lock_held=True,
            _verify_only=True,
        )
    source_paths = [path.resolve() for path in sources]
    source_hashes = {path: sha256_file(path) for path in source_paths}

    def source_refs() -> list[str]:
        refs: list[str] = []
        for path in source_paths:
            try:
                refs.append(path.relative_to(root.parent).as_posix())
            except ValueError:
                refs.append(str(path))
        return refs

    def source_snapshot() -> str:
        digest = hashlib.sha256()
        for path in source_paths:
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def validate_snapshot_envelope(
        candidate_envelope_path: Path,
        *,
        expected_content_path: Path,
    ) -> None:
        envelope = read_json(candidate_envelope_path)
        require_valid_json_document(
            envelope, "derived-view.schema.json", str(candidate_envelope_path)
        )
        expected = {
            "project_id": project_id,
            "view_id": f"DV-{task_id}-{stem.upper()}-{content_digest[:16]}",
            "view_kind": view_kind,
            "legacy_kind": None,
            "generated_at": generated_at,
            "generator": "run-web-product-workflow/scripts/governance_artifacts.py",
            "source_snapshot": source_snapshot(),
            "sources": source_refs(),
            "content_ref": expected_content_path.resolve().relative_to(
                root.parent
            ).as_posix(),
            "integrity_status": "Complete",
        }
        mismatches = [key for key, value in expected.items() if envelope.get(key) != value]
        if mismatches:
            raise GovernanceError(
                "immutable evaluation snapshot envelope mismatch: " + ",".join(mismatches)
            )

    if snapshot_path.exists():
        if snapshot_path.read_text(encoding="utf-8") != content:
            raise GovernanceError("content-addressed evaluation snapshot collision")
        if not envelope_path.is_file():
            raise GovernanceError("content-addressed evaluation snapshot has no envelope")
        validate_snapshot_envelope(
            envelope_path, expected_content_path=snapshot_path
        )
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("evaluation snapshot source changed during envelope validation")
        if snapshot_path.read_text(encoding="utf-8") != content:
            raise GovernanceError("content-addressed evaluation snapshot changed during validation")
        validate_snapshot_envelope(
            envelope_path, expected_content_path=snapshot_path
        )
        return snapshot_path
    if envelope_path.exists():
        raise GovernanceError("content-addressed evaluation snapshot has an orphan envelope")
    if _verify_only:
        raise GovernanceError("evaluation snapshot disappeared after lock release")
    staging = Path(tempfile.mkdtemp(
        prefix=".ev.",
        suffix=".tmp",
        dir=snapshot_path.parent,
    ))
    staging_snapshot = staging / "content.json"
    staging_envelope = staging_snapshot.with_suffix(
        staging_snapshot.suffix + ".view.json"
    )
    final_files_created = False
    try:
        _write_derived_view(
            root=root,
            content_path=staging_snapshot,
            content=content,
            project_id=project_id,
            view_id=f"DV-{task_id}-{stem.upper()}-{content_digest[:16]}",
            view_kind=view_kind,
            sources=sources,
        )
        created_envelope = read_json(staging_envelope)
        created_envelope["generated_at"] = generated_at
        created_envelope["content_ref"] = snapshot_path.resolve().relative_to(
            root.parent
        ).as_posix()
        query_gateway.atomic_write_json(staging_envelope, created_envelope)
        if staging_snapshot.read_text(encoding="utf-8") != content:
            raise GovernanceError("staged evaluation snapshot content mismatch")
        validate_snapshot_envelope(
            staging_envelope, expected_content_path=snapshot_path
        )
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("evaluation snapshot source changed during publication")
        validate_snapshot_envelope(
            staging_envelope, expected_content_path=snapshot_path
        )
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("evaluation snapshot source changed during final validation")
        if snapshot_path.exists() or envelope_path.exists():
            raise GovernanceError("evaluation snapshot target appeared during staged validation")
        final_files_created = True
        os.replace(staging_snapshot, snapshot_path)
        os.replace(staging_envelope, envelope_path)
        if snapshot_path.read_text(encoding="utf-8") != content:
            raise GovernanceError("content-addressed evaluation snapshot changed after publication")
        validate_snapshot_envelope(
            envelope_path, expected_content_path=snapshot_path
        )
        if any(sha256_file(path) != digest for path, digest in source_hashes.items()):
            raise GovernanceError("evaluation snapshot source changed after publication")
        if snapshot_path.read_text(encoding="utf-8") != content:
            raise GovernanceError("content-addressed evaluation snapshot changed before return")
        validate_snapshot_envelope(
            envelope_path, expected_content_path=snapshot_path
        )
        return snapshot_path
    except BaseException:
        if final_files_created:
            for path in (snapshot_path, envelope_path):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def run_query_adversarial_tests(
    environment: QueryEnvironment,
    gold: dict[str, Any],
) -> dict[str, Any]:
    cases = {item["case_id"]: item for item in gold["cases"]}

    def request_for(action: str, stage: str, text: str, *, budget: str = "standard", modes: list[str] | None = None) -> dict[str, Any]:
        return {
            "schema_version": "6.3-candidate",
            "task_id": environment.task_contract["task_id"],
            "stage": stage,
            "action": action,
            "query_text": text,
            "tailoring_resolution_sha256": environment.tailoring_sha256,
            "normative_sources_sha256": environment.index_metadata["normative_sources_sha256"],
            "budget_profile": budget,
            "modes": modes or ["exact", "fts"],
            "requested_additional_control_types": [],
        }

    checks: dict[str, dict[str, Any]] = {}

    conflict_request = request_for(
        "resolve_conflict",
        "S4",
        "同级允许与禁止条款无法按已有 Authority 规则消解",
    )
    conflict_result = execute_query(conflict_request, environment, prevalidated_integrity=True)
    paraphrase_conflict_result = execute_query(
        request_for(
            "resolve_conflict",
            "S4",
            "相同权威层级，一条可执行、另一条不可执行，现有优先关系不足以选择其一",
        ),
        environment,
        prevalidated_integrity=True,
    )
    euphemistic_conflict_result = execute_query(
        request_for(
            "resolve_conflict",
            "S4",
            "两项要求给出不同方向，现有材料不能确定采用哪项",
        ),
        environment,
        prevalidated_integrity=True,
    )
    mixed_diagnostic_conflict_results = [
        execute_query(
            request_for("resolve_conflict", "S4", text),
            environment,
            prevalidated_integrity=True,
        )
        for text in (
            "一致性报告建索引后，两项要求给出不同方向，现有材料不能确定采用哪项，直接采用可执行方案",
            "规范修复刷新快照后，两项规则相斥且没有决定依据，请直接放行执行",
            "一致性报告直接放行执行并建索引",
            "规范修复后直接放行执行再刷新来源摘要",
        )
    ]
    checks["same_level_conflict_blocked"] = {
        "passed": (
            conflict_result["status"] == "Blocked"
            and paraphrase_conflict_result["status"] == "Blocked"
            and euphemistic_conflict_result["status"] == "Blocked"
            and all(result["status"] == "Blocked" for result in mixed_diagnostic_conflict_results)
            and all(
                "conflict-resolution-requires-structured-governance-decision"
                in result["blocker_reasons"]
                for result in (
                    conflict_result,
                    paraphrase_conflict_result,
                    euphemistic_conflict_result,
                    *mixed_diagnostic_conflict_results,
                )
            )
        ),
        "statuses": [
            conflict_result["status"],
            paraphrase_conflict_result["status"],
            euphemistic_conflict_result["status"],
            *(result["status"] for result in mixed_diagnostic_conflict_results),
        ],
        "blockers": [
            conflict_result["blocker_reasons"],
            paraphrase_conflict_result["blocker_reasons"],
            euphemistic_conflict_result["blocker_reasons"],
            *(result["blocker_reasons"] for result in mixed_diagnostic_conflict_results),
        ],
    }

    future_stage_request = request_for(
        "publish_release", "S7", "publish the current release"
    )
    try:
        validate_query_request(future_stage_request, environment)
    except GovernanceError as exc:
        future_stage_blocked = (
            "does not match Tailoring Resolution stage S4" in str(exc)
            and "does not match Norm Packet stage S4" in str(exc)
        )
    else:
        future_stage_blocked = False
    mismatched_packet_environment = replace(
        environment,
        norm_packet={**environment.norm_packet, "stage": "S5"},
    )
    current_stage_request = request_for(
        "run_started", "S4", "start the current run"
    )
    try:
        validate_query_request(current_stage_request, mismatched_packet_environment)
    except GovernanceError as exc:
        packet_stage_mismatch_blocked = "does not match Norm Packet stage S5" in str(exc)
    else:
        packet_stage_mismatch_blocked = False
    checks["task_resolution_packet_stage_alignment"] = {
        "passed": future_stage_blocked and packet_stage_mismatch_blocked,
        "future_stage_request_blocked": future_stage_blocked,
        "packet_stage_mismatch_blocked": packet_stage_mismatch_blocked,
    }

    budget_request = full_gold_request(cases["NRG-G-005"], environment)
    base_result = execute_query(budget_request, environment, prevalidated_integrity=True)
    mutated_budgets = copy.deepcopy(environment.budgets)
    mutated_budgets["profiles"]["compact"]["context_chars"] = 1
    mutated_environment = replace(environment, budgets=mutated_budgets)
    mutated_result = execute_query(
        budget_request, mutated_environment, prevalidated_integrity=True
    )
    checks["budget_identity_and_reporting"] = {
        "passed": (
            base_result["query_digest"] != mutated_result["query_digest"]
            and base_result["budget"]["requested_chars"]
            == environment.budgets["profiles"]["compact"]["context_chars"]
            and mutated_result["budget"]["requested_chars"] == 1
            and mutated_result["budget"]["used_chars"]
            == len(render_clause_context(budget_request, mutated_result))
            and base_result["budget"]["used_chars"]
            == len(render_clause_context(budget_request, base_result))
            and mutated_result["status"] == "Expanded"
            and mutated_result["budget"]["escalations_used"]
            <= mutated_result["budget"]["escalation_limit"]
        ),
        "base_digest": base_result["query_digest"],
        "mutated_digest": mutated_result["query_digest"],
        "base_budget": base_result["budget"],
        "mutated_budget": mutated_result["budget"],
        "base_clause_context_chars": len(render_clause_context(budget_request, base_result)),
        "mutated_clause_context_chars": len(
            render_clause_context(budget_request, mutated_result)
        ),
    }

    pinned_request = full_gold_request(cases["NRG-G-005"], environment)
    action = environment.taxonomy["actions"][pinned_request["action"]]
    rows = load_clause_rows(environment.index_path, environment.source_ids)
    terms = query_terms(pinned_request, action)
    lanes = lane_lookup(
        environment.index_path,
        environment.source_ids,
        terms,
        int(environment.budgets["profiles"]["compact"]["candidate_limit"]),
        pinned_request["modes"],
    )
    planned, pinned_order, _ = plan_candidates(
        rows,
        lanes,
        pinned_request,
        action,
        terms,
        int(environment.budgets["profiles"]["compact"]["candidate_limit"]),
        required_controls(pinned_request, action, environment),
    )
    planned_locators = {row["retrieval_locator"] for row in planned}
    pinned_rows = [row for row in rows if row["retrieval_locator"] in pinned_order]
    pinned_control_counts = {
        control: sum(control in row["control_types"] for row in pinned_rows)
        for control in action["pinned_control_types"]
    }
    checks["pinned_set_not_rank_truncated"] = {
        "passed": (
            len(pinned_order) > 3
            and set(pinned_order) <= planned_locators
            and all(count > 0 for count in pinned_control_counts.values())
        ),
        "pinned_count": len(pinned_order),
        "control_counts": pinned_control_counts,
    }

    synthetic_informative = copy.deepcopy(next(
        row for row in rows
        if row["source_id"] == "C08" and row["normative_modality"] == "informative"
    ))
    synthetic_normative = copy.deepcopy(next(
        row for row in rows
        if row["source_id"] == "C08"
        and row["normative_modality"] in {"must", "must_not", "conditional"}
        and row["heading_path"] != synthetic_informative["heading_path"]
    ))
    for row in (synthetic_informative, synthetic_normative):
        row["control_types"] = ["records"]
        row["context_text"] = row["text"]
        row["stage_tags"] = []
        row["action_tags"] = []
    synthetic_informative["heading_path"] = ["Fixture", "Section A", "Informative"]
    synthetic_normative["heading_path"] = ["Fixture", "Section B", "Normative"]
    synthetic_informative["action_tags"] = ["validate_change"]
    fallback_request = request_for(
        "validate_change", "S5", "records fallback", budget="source-required", modes=["fts"]
    )
    _, fallback, _, _ = expand_for_missing(
        [synthetic_informative, synthetic_normative],
        [],
        ["records"],
        request=fallback_request,
        action=environment.taxonomy["actions"]["validate_change"],
        taxonomy=environment.taxonomy,
        lanes={"exact": {}, "fts_word": {}, "fts_trigram": {}},
        pinned_order={},
        budget_report={
            "profile": "source-required", "candidate_limit": 160,
            "requested_chars": 45000, "used_chars": 0,
            "source_limit": 22, "sources_used": 0,
            "escalation_limit": 44, "escalations_used": 0,
            "omitted_count": 0, "overflow_reason": None,
        },
        required=["records"],
    )
    checks["coverage_fallback_source_reachable"] = {
        "passed": fallback["kind"] == "source",
        "fallback": fallback,
    }

    paged_environment = staged_fixture_environment(environment, "S5")
    paged_request = full_gold_request(cases["NRG-G-015"], paged_environment)
    first_page = execute_query(
        paged_request, paged_environment, prevalidated_integrity=True, page=1
    )
    page_count = int(first_page["fallback"]["page_count"])
    page_results = [
        execute_query(
            paged_request, paged_environment, prevalidated_integrity=True, page=page
        )
        for page in range(1, page_count + 1)
    ]
    paged_locators = [
        citation["retrieval_locator"]
        for result in page_results
        for citation in result["citations"]
    ]
    paged_source = first_page["fallback"]["source_id"]
    expected_source_locators = {
        row["retrieval_locator"] for row in rows if row["source_id"] == paged_source
    }
    checks["ordered_pagination_lossless"] = {
        "passed": (
            len(paged_locators) == len(set(paged_locators))
            and expected_source_locators <= set(paged_locators)
            and len({result["query_digest"] for result in page_results}) == page_count
            and all(
                result["status"] == "Expanded" and not result["coverage"]["missing"]
                for result in page_results
            )
        ),
        "page_count": page_count,
        "locator_count": len(paged_locators),
        "unique_locator_count": len(set(paged_locators)),
        "missing_source_locators": len(expected_source_locators - set(paged_locators)),
        "page_digest_count": len({result["query_digest"] for result in page_results}),
    }

    derivation = required_control_derivation(
        pinned_request,
        action,
        environment,
    )
    page_one_digest = query_digest(paged_request, paged_environment, page=1)
    page_two_digest = query_digest(paged_request, paged_environment, page=2)
    packet_mutation_environment = replace(
        environment,
        norm_packet_control_types=tuple(
            sorted(set(environment.norm_packet_control_types) - {"integrity"})
        ),
    )
    packet_mutation_digest = query_digest(
        pinned_request,
        packet_mutation_environment,
    )
    packet_mutation_result = execute_query(
        pinned_request,
        packet_mutation_environment,
        prevalidated_integrity=True,
    )
    checks["planner_five_input_closure_and_page_identity"] = {
        "passed": (
            set((
                "stage", "action", "tailoring_resolution", "norm_packet",
                "inferred_query", "requested_additional", "final",
            )) <= set(derivation)
            and bool(derivation["stage"])
            and bool(derivation["action"])
            and bool(derivation["tailoring_resolution"])
            and bool(derivation["norm_packet"])
            and page_one_digest != page_two_digest
            and base_result["query_digest"] != packet_mutation_digest
            and packet_mutation_result["status"] == "Blocked"
            and packet_mutation_result["coverage"]["required"]
            != base_result["coverage"]["required"]
            and any(
                item.startswith("norm-packet-required-control-unsupported:")
                for item in packet_mutation_result["blocker_reasons"]
            )
        ),
        "derivation": derivation,
        "page_digest_distinct": page_one_digest != page_two_digest,
        "norm_packet_factor_changes_digest": (
            base_result["query_digest"] != packet_mutation_digest
        ),
        "norm_packet_mutation_status": packet_mutation_result["status"],
        "norm_packet_changes_required_controls": (
            packet_mutation_result["coverage"]["required"]
            != base_result["coverage"]["required"]
        ),
    }

    semantic_environment = staged_fixture_environment(environment, "S8")
    semantic_request = request_for(
        "close_task", "S8", "close task", modes=["semantic"]
    )
    semantic_request["tailoring_resolution_sha256"] = semantic_environment.tailoring_sha256
    semantic_only = execute_query(
        semantic_request,
        semantic_environment,
        prevalidated_integrity=True,
    )
    mixed = execute_query(
        request_for(
            "run_started",
            "S4",
            "Before execution which authorization gates apply",
            modes=["fts", "semantic"],
        ),
        environment,
        prevalidated_integrity=True,
    )
    checks["retrieval_modes_are_enforced"] = {
        "passed": (
            semantic_only["status"] == "Blocked"
            and all(item["lane_ranks"]["exact"] is None for item in mixed["citations"])
            and all(item["lane_ranks"]["semantic"] is None for item in mixed["citations"])
            and all(
                "semantic_disabled_local_exact_fts_fallback" in item["retrieval_reason"]
                for item in mixed["citations"]
            )
        ),
        "semantic_only_status": semantic_only["status"],
        "mixed_status": mixed["status"],
    }

    citation_environment = staged_fixture_environment(environment, "S6")
    citation_request = full_gold_request(cases["NRG-G-018"], citation_environment)
    citation_result = execute_query(
        citation_request, citation_environment, prevalidated_integrity=True
    )
    tamper_fields = {
        "retrieval_locator": "C08:forged:locator",
        "logical_path": "references/forged.md",
        "source_sha256": "0" * 64,
        "source_version": "forged-version",
        "line_start": 1,
        "line_end": 1,
    }
    tamper_blocked: dict[str, bool] = {}
    for field, value in tamper_fields.items():
        tampered = copy.deepcopy(citation_result)
        tampered["citations"][0][field] = value
        try:
            validate_result_semantics(tampered, citation_environment)
        except GovernanceError:
            tamper_blocked[field] = True
        else:
            tamper_blocked[field] = False
    checks["citation_provenance_tamper_blocked"] = {
        "passed": all(tamper_blocked.values()),
        "fields": tamper_blocked,
    }

    oversized = request_for(
        "validate_change", "S5", "x" * (MAX_QUERY_TEXT_CHARS + 1), modes=["fts"]
    )
    try:
        validate_query_request(
            oversized, staged_fixture_environment(environment, "S5")
        )
    except GovernanceError:
        oversized_blocked = True
    else:
        oversized_blocked = False
    long_term = request_for(
        "validate_change", "S5", "x" * 257, modes=["fts"]
    )
    try:
        query_terms(long_term, environment.taxonomy["actions"]["validate_change"])
    except GovernanceError:
        long_term_blocked = True
    else:
        long_term_blocked = False
    original_step_limit = query_gateway.SQLITE_PROGRESS_STEP_LIMIT
    original_row_limit = query_gateway.MAX_CLAUSE_ROWS
    try:
        query_gateway.SQLITE_PROGRESS_STEP_LIMIT = 0
        try:
            lane_lookup(
                environment.index_path,
                environment.source_ids,
                {"exact": [], "fts_word": ["authority"], "fts_trigram": []},
                10,
                ["fts"],
            )
        except GovernanceError:
            sqlite_limit_blocked = True
        else:
            sqlite_limit_blocked = False
        query_gateway.MAX_CLAUSE_ROWS = 1
        try:
            load_clause_rows(environment.index_path, environment.source_ids)
        except GovernanceError:
            row_limit_blocked = True
        else:
            row_limit_blocked = False
    finally:
        query_gateway.SQLITE_PROGRESS_STEP_LIMIT = original_step_limit
        query_gateway.MAX_CLAUSE_ROWS = original_row_limit
    checks["resource_limits_fail_closed"] = {
        "passed": all((oversized_blocked, long_term_blocked, sqlite_limit_blocked, row_limit_blocked)),
        "query_text": oversized_blocked,
        "term_length": long_term_blocked,
        "sqlite_steps": sqlite_limit_blocked,
        "clause_rows": row_limit_blocked,
    }

    query_base = (
        environment.project_root / ".project-governance" / "generated" / "queries"
        / environment.task_contract["task_id"]
    )
    query_base.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=".aq.", dir=query_base))
    try:
        request_path = scratch / "request.json"
        request_path.write_text(
            json.dumps(citation_request, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        target = scratch / "published"
        with ThreadPoolExecutor(max_workers=2) as executor:
            publications = list(executor.map(
                lambda _: write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    target,
                ),
                range(2),
            ))
        published_files = sorted(path.name for path in target.iterdir())
        envelope_path = target / "query-result.json.view.json"
        original_envelope = read_json(envelope_path)
        tampered_envelope = copy.deepcopy(original_envelope)
        tampered_envelope["integrity_status"] = "Forged"
        query_gateway.atomic_write_json(envelope_path, tampered_envelope)
        try:
            write_query_outputs(
                citation_environment,
                request_path,
                citation_request,
                citation_result,
                target,
            )
        except GovernanceError:
            tampered_envelope_blocked = True
        else:
            tampered_envelope_blocked = False
        query_gateway.atomic_write_json(envelope_path, original_envelope)
        generated_at_tamper_blocked: dict[str, bool] = {}
        for envelope_name in (
            "query-result.json.view.json",
            "clause-context.md.view.json",
        ):
            candidate_path = target / envelope_name
            candidate_envelope = read_json(candidate_path)
            tampered_time = copy.deepcopy(candidate_envelope)
            tampered_time["generated_at"] = "2099-12-31T23:59:59Z"
            query_gateway.atomic_write_json(candidate_path, tampered_time)
            try:
                write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    target,
                )
            except GovernanceError:
                generated_at_tamper_blocked[envelope_name] = True
            else:
                generated_at_tamper_blocked[envelope_name] = False
            finally:
                query_gateway.atomic_write_json(candidate_path, candidate_envelope)
        collision_result = copy.deepcopy(citation_result)
        collision_result["blocker_reasons"] = ["forged-collision"]
        try:
            write_query_outputs(
                citation_environment,
                request_path,
                citation_request,
                collision_result,
                target,
            )
        except GovernanceError:
            collision_blocked = True
        else:
            collision_blocked = False
        original_derived_view_writer = query_gateway._write_derived_view
        toctou_target = scratch / "toctou-published"

        def source_drift_during_envelope(**kwargs: Any) -> list[Path]:
            if kwargs.get("view_kind") != "norm-query-result":
                return original_derived_view_writer(**kwargs)
            original_request_bytes = request_path.read_bytes()
            request_path.write_bytes(original_request_bytes + b" ")
            try:
                return original_derived_view_writer(**kwargs)
            finally:
                request_path.write_bytes(original_request_bytes)

        query_gateway._write_derived_view = source_drift_during_envelope
        try:
            try:
                recovered_publication = write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    toctou_target,
                )
            except GovernanceError:
                envelope_window_safe = not toctou_target.exists()
            else:
                envelope_window_safe = (
                    len(recovered_publication) == 4 and toctou_target.is_dir()
                )
        finally:
            query_gateway._write_derived_view = original_derived_view_writer
        original_replace = query_gateway.os.replace
        final_source_target = scratch / "final-source-window-published"
        original_request_bytes = request_path.read_bytes()

        def source_drift_before_directory_replace(src: Any, dst: Any) -> None:
            if Path(dst).resolve() == final_source_target.resolve():
                request_path.write_bytes(original_request_bytes + b" ")
            original_replace(src, dst)

        query_gateway.os.replace = source_drift_before_directory_replace
        try:
            try:
                write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    final_source_target,
                )
            except GovernanceError:
                final_source_window_blocked = not final_source_target.exists()
            else:
                final_source_window_blocked = False
        finally:
            query_gateway.os.replace = original_replace
            request_path.write_bytes(original_request_bytes)

        final_envelope_target = scratch / "final-envelope-window-published"

        def envelope_drift_before_directory_replace(src: Any, dst: Any) -> None:
            if Path(dst).resolve() == final_envelope_target.resolve():
                staged_envelope_path = Path(src) / "query-result.json.view.json"
                staged_envelope = read_json(staged_envelope_path)
                staged_envelope["generated_at"] = "2099-12-31T23:59:59Z"
                staged_envelope["source_snapshot"] = "e" * 64
                query_gateway.atomic_write_json(staged_envelope_path, staged_envelope)
            original_replace(src, dst)

        query_gateway.os.replace = envelope_drift_before_directory_replace
        try:
            try:
                write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    final_envelope_target,
                )
            except GovernanceError:
                final_envelope_window_blocked = not final_envelope_target.exists()
            else:
                final_envelope_window_blocked = False
        finally:
            query_gateway.os.replace = original_replace

        move_then_raise_target = scratch / "move-then-raise-published"

        def corrupt_after_committed_move_then_raise(src: Any, dst: Any) -> None:
            if Path(dst).resolve() == move_then_raise_target.resolve():
                original_replace(src, dst)
                moved_envelope_path = (
                    move_then_raise_target / "query-result.json.view.json"
                )
                moved_envelope = read_json(moved_envelope_path)
                moved_envelope["integrity_status"] = "Forged"
                query_gateway.atomic_write_json(moved_envelope_path, moved_envelope)
                raise OSError("injected failure after committed directory move")
            original_replace(src, dst)

        query_gateway.os.replace = corrupt_after_committed_move_then_raise
        try:
            try:
                write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    move_then_raise_target,
                )
            except (GovernanceError, OSError):
                move_then_raise_cleanup = not move_then_raise_target.exists()
            else:
                move_then_raise_cleanup = False
        finally:
            query_gateway.os.replace = original_replace

        lock_release_target = scratch / "lock-release-published"
        lock_release_path = query_gateway.publication_lock_path(lock_release_target)
        original_path_unlink = Path.unlink

        def tamper_when_query_lock_is_released(
            path: Path, missing_ok: bool = False
        ) -> None:
            original_path_unlink(path, missing_ok=missing_ok)
            if path.resolve() == lock_release_path.resolve():
                released_envelope_path = (
                    lock_release_target / "query-result.json.view.json"
                )
                released_envelope = read_json(released_envelope_path)
                released_envelope["integrity_status"] = "Forged"
                query_gateway.atomic_write_json(
                    released_envelope_path, released_envelope
                )

        Path.unlink = tamper_when_query_lock_is_released
        try:
            try:
                write_query_outputs(
                    citation_environment,
                    request_path,
                    citation_request,
                    citation_result,
                    lock_release_target,
                )
            except GovernanceError:
                lock_release_tamper_blocked = True
            else:
                lock_release_tamper_blocked = False
        finally:
            Path.unlink = original_path_unlink
        staging_leftovers = [
            path.name
            for path in scratch.iterdir()
            if path.name.endswith(".tmp") or path.name.endswith(".lock")
        ]
        atomic_passed = (
            all(len(items) == 4 for items in publications)
            and published_files == sorted((
                "clause-context.md", "clause-context.md.view.json",
                "query-result.json", "query-result.json.view.json",
            ))
            and collision_blocked
            and tampered_envelope_blocked
            and all(generated_at_tamper_blocked.values())
            and envelope_window_safe
            and final_source_window_blocked
            and final_envelope_window_blocked
            and move_then_raise_cleanup
            and lock_release_tamper_blocked
            and not staging_leftovers
        )
    finally:
        shutil.rmtree(scratch)
    checks["query_output_atomic_and_immutable"] = {
        "passed": atomic_passed,
        "collision_blocked": collision_blocked,
        "tampered_envelope_blocked": tampered_envelope_blocked,
        "generated_at_tamper_blocked": generated_at_tamper_blocked,
        "source_drift_in_envelope_window_safe": envelope_window_safe,
        "source_drift_in_final_replace_window_blocked": final_source_window_blocked,
        "envelope_drift_in_final_replace_window_blocked": final_envelope_window_blocked,
        "committed_move_then_raise_cleanup": move_then_raise_cleanup,
        "lock_release_tamper_blocked": lock_release_tamper_blocked,
        "staging_leftovers": staging_leftovers,
    }

    original_manifest_validator = query_gateway.validate_embedded_manifest
    original_source_loader = query_gateway.load_sources
    try:
        query_gateway.validate_embedded_manifest = lambda: ["adversarial-manifest-drift"]
        manifest_drift_blockers = integrity_blockers(
            citation_request, citation_environment
        )
        query_gateway.validate_embedded_manifest = original_manifest_validator
        query_gateway.load_sources = lambda: ([], "0" * 64)
        source_drift_blockers = integrity_blockers(
            citation_request, citation_environment
        )
    finally:
        query_gateway.validate_embedded_manifest = original_manifest_validator
        query_gateway.load_sources = original_source_loader
    checks["final_manifest_and_normative_source_revalidation"] = {
        "passed": (
            any(item.startswith("embedded-manifest-invalid:") for item in manifest_drift_blockers)
            and "normative-sources-digest-mismatch" in source_drift_blockers
        ),
        "manifest_drift_blocked": any(
            item.startswith("embedded-manifest-invalid:") for item in manifest_drift_blockers
        ),
        "normative_source_drift_blocked": (
            "normative-sources-digest-mismatch" in source_drift_blockers
        ),
    }

    contract_semantic_errors = semantic_errors(
        "norm-query-result.schema.json",
        mutated_result,
        environment.taxonomy,
    )
    locator_tamper = copy.deepcopy(mutated_result)
    locator_tamper["citations"][0]["retrieval_locator"] = "C08:forged:locator"
    locator_tamper_errors = semantic_errors(
        "norm-query-result.schema.json",
        locator_tamper,
        environment.taxonomy,
    )
    checks["contract_and_production_semantics_are_aligned"] = {
        "passed": (
            not contract_semantic_errors
            and any("retrieval_locator is not reproducible" in item for item in locator_tamper_errors)
        ),
        "valid_soft_overflow_errors": contract_semantic_errors,
        "locator_tamper_blocked": any(
            "retrieval_locator is not reproducible" in item for item in locator_tamper_errors
        ),
    }

    evidence_scratch = Path(tempfile.mkdtemp(
        prefix=".ae.",
        dir=environment.project_root / ".project-governance" / "generated" / "evaluations",
    ))
    try:
        first_content = '{"status":"Failed","case_summary":"21/28"}\n'
        second_content = '{"status":"Passed","case_summary":"28/28"}\n'
        first_path = write_immutable_evidence_snapshot(
            root=environment.project_root / ".project-governance",
            output_dir=evidence_scratch,
            stem="qe",
            content=first_content,
            project_id=environment.task_contract["project_id"],
            task_id=environment.task_contract["task_id"],
            view_kind="norm-query-gateway-evaluation-json",
            sources=[Path(__file__).resolve()],
            generated_at="2026-01-01T00:00:00Z",
        )
        first_bytes = first_path.read_bytes()
        second_path = write_immutable_evidence_snapshot(
            root=environment.project_root / ".project-governance",
            output_dir=evidence_scratch,
            stem="qe",
            content=second_content,
            project_id=environment.task_contract["project_id"],
            task_id=environment.task_contract["task_id"],
            view_kind="norm-query-gateway-evaluation-json",
            sources=[Path(__file__).resolve()],
            generated_at="2026-01-01T00:00:00Z",
        )
        evidence_immutable = (
            first_path != second_path
            and first_path.read_bytes() == first_bytes
            and first_path.is_file()
            and second_path.is_file()
        )
        first_envelope = read_json(first_path.with_suffix(first_path.suffix + ".view.json"))
        first_envelope_path = first_path.with_suffix(first_path.suffix + ".view.json")
        tampered_snapshot_envelope = copy.deepcopy(first_envelope)
        tampered_snapshot_envelope["source_snapshot"] = "0" * 64
        query_gateway.atomic_write_json(first_envelope_path, tampered_snapshot_envelope)
        try:
            write_immutable_evidence_snapshot(
                root=environment.project_root / ".project-governance",
                output_dir=evidence_scratch,
                stem="qe",
                content=first_content,
                project_id=environment.task_contract["project_id"],
                task_id=environment.task_contract["task_id"],
                view_kind="norm-query-gateway-evaluation-json",
                sources=[Path(__file__).resolve()],
                generated_at="2026-01-01T00:00:00Z",
            )
        except GovernanceError:
            evaluation_envelope_tamper_blocked = True
        else:
            evaluation_envelope_tamper_blocked = False
        finally:
            query_gateway.atomic_write_json(first_envelope_path, first_envelope)
        tampered_snapshot_time = copy.deepcopy(first_envelope)
        tampered_snapshot_time["generated_at"] = "2099-12-31T23:59:59Z"
        query_gateway.atomic_write_json(first_envelope_path, tampered_snapshot_time)
        try:
            write_immutable_evidence_snapshot(
                root=environment.project_root / ".project-governance",
                output_dir=evidence_scratch,
                stem="qe",
                content=first_content,
                project_id=environment.task_contract["project_id"],
                task_id=environment.task_contract["task_id"],
                view_kind="norm-query-gateway-evaluation-json",
                sources=[Path(__file__).resolve()],
                generated_at="2026-01-01T00:00:00Z",
            )
        except GovernanceError:
            evaluation_generated_at_tamper_blocked = True
        else:
            evaluation_generated_at_tamper_blocked = False
        finally:
            query_gateway.atomic_write_json(first_envelope_path, first_envelope)
        first_path.write_text('{"status":"Forged"}\n', encoding="utf-8", newline="\n")
        try:
            write_immutable_evidence_snapshot(
                root=environment.project_root / ".project-governance",
                output_dir=evidence_scratch,
                stem="qe",
                content=first_content,
                project_id=environment.task_contract["project_id"],
                task_id=environment.task_contract["task_id"],
                view_kind="norm-query-gateway-evaluation-json",
                sources=[Path(__file__).resolve()],
                generated_at="2026-01-01T00:00:00Z",
            )
        except GovernanceError:
            evaluation_body_tamper_blocked = True
        else:
            evaluation_body_tamper_blocked = False
        finally:
            first_path.write_bytes(first_bytes)
        final_window_content = '{"status":"Failed","case_summary":"final-window"}\n'
        final_window_digest = sha256_bytes(final_window_content.encode("utf-8"))
        final_window_path = (
            evidence_scratch
            / "snapshots"
            / f"qf-{final_window_digest}.json"
        )
        final_window_envelope = final_window_path.with_suffix(
            final_window_path.suffix + ".view.json"
        )
        audit_module = sys.modules[__name__]
        original_snapshot_replace = audit_module.os.replace

        def tamper_after_final_envelope_publish(src: Any, dst: Any) -> None:
            original_snapshot_replace(src, dst)
            if Path(dst).resolve() == final_window_envelope.resolve():
                envelope = read_json(final_window_envelope)
                envelope["generated_at"] = "2099-12-31T23:59:59Z"
                envelope["source_snapshot"] = "e" * 64
                tamper_path = final_window_envelope.parent / ".inj.json"
                query_gateway.atomic_write_json(tamper_path, envelope)
                original_snapshot_replace(tamper_path, final_window_envelope)

        audit_module.os.replace = tamper_after_final_envelope_publish
        try:
            try:
                write_immutable_evidence_snapshot(
                    root=environment.project_root / ".project-governance",
                    output_dir=evidence_scratch,
                    stem="qf",
                    content=final_window_content,
                    project_id=environment.task_contract["project_id"],
                    task_id=environment.task_contract["task_id"],
                    view_kind="norm-query-gateway-evaluation-json",
                    sources=[Path(__file__).resolve()],
                    generated_at="2026-01-01T00:00:00Z",
                )
            except GovernanceError:
                evaluation_final_window_blocked = (
                    not final_window_path.exists()
                    and not final_window_envelope.exists()
                )
            else:
                evaluation_final_window_blocked = False
        finally:
            audit_module.os.replace = original_snapshot_replace

        move_raise_content = '{"status":"Failed","case_summary":"move-then-raise"}\n'
        move_raise_digest = sha256_bytes(move_raise_content.encode("utf-8"))
        move_raise_path = (
            evidence_scratch
            / "snapshots"
            / f"qm-{move_raise_digest}.json"
        )
        move_raise_envelope = move_raise_path.with_suffix(
            move_raise_path.suffix + ".view.json"
        )

        def raise_after_first_snapshot_move(src: Any, dst: Any) -> None:
            if Path(dst).resolve() == move_raise_path.resolve():
                original_snapshot_replace(src, dst)
                raise OSError("injected failure after committed snapshot move")
            original_snapshot_replace(src, dst)

        audit_module.os.replace = raise_after_first_snapshot_move
        try:
            try:
                write_immutable_evidence_snapshot(
                    root=environment.project_root / ".project-governance",
                    output_dir=evidence_scratch,
                    stem="qm",
                    content=move_raise_content,
                    project_id=environment.task_contract["project_id"],
                    task_id=environment.task_contract["task_id"],
                    view_kind="norm-query-gateway-evaluation-json",
                    sources=[Path(__file__).resolve()],
                    generated_at="2026-01-01T00:00:00Z",
                )
            except OSError:
                evaluation_move_then_raise_cleanup = (
                    not move_raise_path.exists()
                    and not move_raise_envelope.exists()
                )
            else:
                evaluation_move_then_raise_cleanup = False
        finally:
            audit_module.os.replace = original_snapshot_replace

        release_content = '{"status":"Failed","case_summary":"lock-release"}\n'
        release_digest = sha256_bytes(release_content.encode("utf-8"))
        release_path = (
            evidence_scratch
            / "snapshots"
            / f"qr-{release_digest}.json"
        )
        release_envelope = release_path.with_suffix(
            release_path.suffix + ".view.json"
        )
        release_lock = query_gateway.publication_lock_path(release_path)
        original_evidence_path_unlink = Path.unlink

        def tamper_when_evidence_lock_is_released(
            path: Path, missing_ok: bool = False
        ) -> None:
            original_evidence_path_unlink(path, missing_ok=missing_ok)
            if path.resolve() == release_lock.resolve():
                released_envelope = read_json(release_envelope)
                released_envelope["integrity_status"] = "Forged"
                query_gateway.atomic_write_json(release_envelope, released_envelope)

        Path.unlink = tamper_when_evidence_lock_is_released
        try:
            try:
                write_immutable_evidence_snapshot(
                    root=environment.project_root / ".project-governance",
                    output_dir=evidence_scratch,
                    stem="qr",
                    content=release_content,
                    project_id=environment.task_contract["project_id"],
                    task_id=environment.task_contract["task_id"],
                    view_kind="norm-query-gateway-evaluation-json",
                    sources=[Path(__file__).resolve()],
                    generated_at="2026-01-01T00:00:00Z",
                )
            except GovernanceError:
                evaluation_lock_release_tamper_blocked = True
            else:
                evaluation_lock_release_tamper_blocked = False
        finally:
            Path.unlink = original_evidence_path_unlink
        project_prefix = environment.project_root.name + "/"
        envelope_paths_are_root_relative = (
            not first_envelope["content_ref"].startswith(project_prefix)
            and all(
                not source.startswith(project_prefix)
                for source in first_envelope["sources"]
            )
        )
    finally:
        shutil.rmtree(evidence_scratch)
    checks["evaluation_evidence_content_addressed"] = {
        "passed": (
            evidence_immutable
            and envelope_paths_are_root_relative
            and evaluation_envelope_tamper_blocked
            and evaluation_generated_at_tamper_blocked
            and evaluation_body_tamper_blocked
            and evaluation_final_window_blocked
            and evaluation_move_then_raise_cleanup
            and evaluation_lock_release_tamper_blocked
        ),
        "root_relative_envelope_paths": envelope_paths_are_root_relative,
        "envelope_source_snapshot_tamper_blocked": evaluation_envelope_tamper_blocked,
        "envelope_generated_at_tamper_blocked": evaluation_generated_at_tamper_blocked,
        "body_tamper_blocked": evaluation_body_tamper_blocked,
        "final_validation_window_tamper_blocked": evaluation_final_window_blocked,
        "committed_first_move_then_raise_cleanup": evaluation_move_then_raise_cleanup,
        "lock_release_tamper_blocked": evaluation_lock_release_tamper_blocked,
    }

    synthetic_root = Path("C:/") / ("project-root-" + "x" * 78)
    synthetic_parent = (
        synthetic_root
        / ".project-governance"
        / "generated"
        / "evaluations"
        / "T-015"
        / "snapshots"
    )
    synthetic_target = synthetic_parent / (
        "query-gateway-evaluation-" + "a" * 64 + ".json"
    )
    second_target = synthetic_parent / (
        "query-gateway-evaluation-" + "b" * 64 + ".json"
    )
    synthetic_lock = query_gateway.publication_lock_path(synthetic_target)
    second_lock = query_gateway.publication_lock_path(second_target)
    synthetic_fixture_target = (
        synthetic_root
        / ".project-governance"
        / "generated"
        / "evaluations"
        / ".ae.12345678"
        / "snapshots"
        / ("query-evaluation-" + "c" * 64 + ".json")
    )
    expected_lock_name_length = (
        len(".publication-")
        + query_gateway.PUBLICATION_LOCK_DIGEST_CHARS
        + len(".lock")
    )
    checks["bounded_publication_lock_path"] = {
        "passed": (
            synthetic_lock.parent == synthetic_target.parent
            and len(synthetic_lock.name) == expected_lock_name_length
            and len(str(synthetic_lock)) < 260
            and len(str(synthetic_fixture_target)) < 260
            and synthetic_lock != second_lock
            and synthetic_target.name not in synthetic_lock.name
        ),
        "synthetic_project_root_chars": len(str(synthetic_root)),
        "target_path_chars": len(str(synthetic_target)),
        "lock_path_chars": len(str(synthetic_lock)),
        "lock_name_chars": len(synthetic_lock.name),
        "fixture_target_path_chars": len(str(synthetic_fixture_target)),
        "distinct_target_lock": synthetic_lock != second_lock,
    }

    return {
        "status": "Passed" if all(item["passed"] for item in checks.values()) else "Failed",
        "total": len(checks),
        "passed": sum(item["passed"] for item in checks.values()),
        "checks": checks,
    }


def query_gateway_evaluation(
    *,
    project_root: Path,
    project_id: str,
    task_id: str,
    task_dir: Path,
    index_metadata: Path | None,
    consistency_report: Path | None,
    budget_baseline: Path | None,
    validation: dict[str, Any],
    expected_default_path_integration: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    environment = load_environment(
        task_dir,
        index_metadata_path=index_metadata,
        consistency_report_path=consistency_report,
        budget_baseline_path=budget_baseline,
    )
    if environment.task_contract.get("project_id") != project_id:
        raise GovernanceError("query evaluation project_id does not match TaskContract")
    if environment.task_contract.get("task_id") != task_id:
        raise GovernanceError("query evaluation task_id does not match TaskContract")
    gold = read_json(runtime_asset_path("evaluations/norm-retrieval-gold.json"))
    targets = {item["target_id"]: item for item in gold["mandatory_clause_targets"]}
    smoke_case = next(item for item in gold["cases"] if item["case_id"] == "NRG-G-009")
    preflight_request = full_gold_request(smoke_case, environment)
    preflight_blockers = integrity_blockers(preflight_request, environment)
    if preflight_blockers:
        raise GovernanceError("query preflight failed: " + "; ".join(preflight_blockers))

    case_results: dict[str, dict[str, Any]] = {}
    summaries: list[dict[str, Any]] = []
    for case in gold["cases"]:
        case_id = case["case_id"]
        category = case["category"]
        case_environment = staged_fixture_environment(
            environment, case["query"]["stage"]
        )
        request = full_gold_request(case, case_environment)
        result: dict[str, Any] | None = None
        actual_status: str
        special_checks: list[dict[str, Any]] = []
        if category == "query-contract":
            invalid = copy.deepcopy(request)
            invalid.pop("action")
            try:
                validate_query_request(invalid, case_environment)
                actual_status = "Unexpected-valid"
            except GovernanceError:
                actual_status = "Schema-invalid"
        elif category == "tailoring-boundary":
            restricted = replace(
                case_environment,
                source_ids=tuple(item for item in case_environment.source_ids if item != "E03"),
            )
            result = execute_query(request, restricted, prevalidated_integrity=True)
            escaped = sorted({item["source_id"] for item in result["citations"]} - set(restricted.source_ids))
            special_checks.append({"check": "tailoring-source-hard-boundary", "passed": not escaped, "escaped": escaped})
            actual_status = "Blocked-on-source-injection" if not escaped else "Source-injection-allowed"
        elif category == "consistency-gate":
            report = copy.deepcopy(case_environment.consistency_report)
            report["audit_status"] = "Blocked"
            report["norm_index_ready"] = False
            report.setdefault("summary", {}).setdefault("by_severity", {})["Blocker"] = 1
            result = execute_query(request, replace(case_environment, consistency_report=report))
            actual_status = result["status"]
        elif category == "stale-digest":
            stale = copy.deepcopy(request)
            stale["tailoring_resolution_sha256"] = "0" * 64
            result = execute_query(stale, case_environment)
            actual_status = result["status"]
        elif category == "budget-boundary":
            budgets = copy.deepcopy(case_environment.budgets)
            budgets["profiles"]["compact"]["context_chars"] = 64
            budgets["profiles"]["compact"]["source_limit"] = 1
            result = execute_query(request, replace(case_environment, budgets=budgets), prevalidated_integrity=True)
            actual_status = result["status"]
        elif category == "fail-closed-integrity":
            unknown = replace(
                case_environment,
                source_ids=(*case_environment.source_ids, "UNKNOWN-SOURCE"),
            )
            result = execute_query(request, unknown)
            actual_status = result["status"]
        else:
            result = execute_query(request, case_environment, prevalidated_integrity=True)
            actual_status = result["status"]

        if case_id == "NRG-G-010":
            blocked_contract = copy.deepcopy(case_environment.task_contract)
            blocked_contract["tailoring_resolution"]["blocking_reasons"] = [
                "authority binding is absent"
            ]
            blocked_execution = execute_query(
                request,
                replace(case_environment, task_contract=blocked_contract),
                prevalidated_integrity=True,
            )
            special_checks.append({
                "check": "execution-decision-requires-blocker-free-tailoring",
                "passed": blocked_execution["status"] == "Blocked",
                "actual_status": blocked_execution["status"],
            })

        expected = case["expected"]
        expected_sources = set(expected.get("source_ids", []))
        expected_controls = set(expected.get("control_types", []))
        actual_sources: set[str] = set()
        actual_controls: set[str] = set()
        target_checks: list[dict[str, Any]] = []
        fallback_kind = "none"
        citation_integrity = True
        deterministic = True
        if result is not None:
            actual_sources = {item["source_id"] for item in result["citations"]}
            actual_controls = {control for item in result["citations"] for control in item["control_types"]}
            fallback_kind = result["fallback"]["kind"]
            validation_environment = (
                restricted if category == "tailoring-boundary" else case_environment
            )
            try:
                validate_result_semantics(result, validation_environment)
            except GovernanceError:
                citation_integrity = False
            if category in {"deterministic-fusion", "deterministic-replay"}:
                replay = execute_query(
                    request, case_environment, prevalidated_integrity=True
                )
                deterministic = canonical_json_bytes(result) == canonical_json_bytes(replay)
            for target_id in expected.get("mandatory_target_ids", []):
                hit = any(citation_hits_target(item, targets[target_id]) for item in result["citations"])
                target_checks.append({"target_id": target_id, "hit": hit})
        blocked_before_retrieval = category in {
            "consistency-gate", "stale-digest", "fail-closed-integrity"
        } and actual_status == "Blocked"
        sources_passed = expected_sources <= actual_sources or actual_status in {
            "Schema-invalid", "Blocked-on-source-injection"
        } or blocked_before_retrieval
        controls_passed = expected_controls <= actual_controls or actual_status == "Schema-invalid" or blocked_before_retrieval
        outcome_passed = expected_outcome_matches(expected["outcome"], actual_status, fallback_kind)
        targets_passed = all(item["hit"] for item in target_checks)
        passed = all((sources_passed, controls_passed, outcome_passed, targets_passed, citation_integrity, deterministic))
        passed = passed and all(item["passed"] for item in special_checks)
        summary = {
            "case_id": case_id,
            "category": category,
            "expected_outcome": expected["outcome"],
            "actual_status": actual_status,
            "passed": passed,
            "source_ids": sorted(actual_sources),
            "missing_expected_sources": sorted(expected_sources - actual_sources),
            "control_types": sorted(actual_controls),
            "missing_expected_controls": sorted(expected_controls - actual_controls),
            "target_checks": target_checks,
            "citation_count": len(result["citations"]) if result else 0,
            "citation_integrity": citation_integrity,
            "deterministic_replay": deterministic,
            "fallback_kind": fallback_kind,
            "blocker_reasons": result["blocker_reasons"] if result else [],
            "special_checks": special_checks,
        }
        summaries.append(summary)
        if result is not None:
            case_results[case_id] = result

    target_checks: list[dict[str, Any]] = []
    for target_id, target in targets.items():
        associated = [case_id for case_id in target["case_ids"] if case_id in case_results]
        hit_cases = [
            case_id for case_id in associated
            if any(citation_hits_target(item, target) for item in case_results[case_id]["citations"])
        ]
        target_checks.append({
            "target_id": target_id,
            "associated_case_ids": associated,
            "hit_case_ids": hit_cases,
            "hit": bool(hit_cases),
        })
    all_citations = [
        citation
        for result in case_results.values()
        for citation in result["citations"]
    ]
    citation_passes = sum(
        summary["citation_count"] for summary in summaries if summary["citation_integrity"]
    )
    false_allow_cases = ("NRG-G-010", "NRG-G-024", "NRG-G-027")
    false_allow_count = sum(
        1 for case_id in false_allow_cases
        if case_results.get(case_id, {}).get("status") != "Blocked"
    )
    silent_truncation_count = sum(
        1 for case_id in ("NRG-G-005", "NRG-G-012")
        if not (
            case_results.get(case_id, {}).get("status") == "Expanded"
            and not case_results.get(case_id, {}).get("coverage", {}).get("missing")
        )
    )
    observations = {
        "mandatory_clause_recall": {"numerator": sum(item["hit"] for item in target_checks), "denominator": len(target_checks)},
        "citation_hash_integrity": {"numerator": citation_passes, "denominator": len(all_citations)},
        "false_allow_count": {"value": false_allow_count},
        "stale_index_block_rate": {"numerator": int(case_results["NRG-G-004"]["status"] == "Blocked"), "denominator": 1},
        "unknown_source_block_rate": {"numerator": int(case_results["NRG-G-017"]["status"] == "Blocked"), "denominator": 1},
        "p0_p1_silent_truncation_count": {"value": silent_truncation_count},
        "deterministic_replay_rate": {
            "numerator": sum(item["deterministic_replay"] for item in summaries if item["case_id"] in {"NRG-G-011", "NRG-G-020"}),
            "denominator": 2,
        },
        "source_standard_profile_coverage": {"value": "22/17/137"},
    }
    hard_gates = []
    for gate in gold["hard_gates"]:
        observation = observations[gate["metric"]]
        hard_gates.append({
            "gate_id": gate["gate_id"],
            "metric": gate["metric"],
            "observation": observation,
            "passed": evaluate_gate(gate, observation),
        })
    t008 = gold["compatibility_baselines"]["t008_s5"]
    compatibility = {}
    for label in ("source_pack", "norm_packet"):
        expected = t008[label]
        path = project_root / expected["path"]
        compatibility[label] = {
            "path": expected["path"],
            "expected_sha256": expected["sha256"],
            "actual_sha256": sha256_file(path),
            "passed": path.stat().st_size == expected["bytes"] and sha256_file(path) == expected["sha256"],
        }
    planner_fixtures = run_query_planner_fixtures()
    adversarial_tests = run_query_adversarial_tests(environment, gold)
    replay_result_a = execute_query(preflight_request, environment)
    replay_result_b = execute_query(preflight_request, environment)
    deterministic_artifact_replay = {
        "query_result_bytes_equal": (
            canonical_json_bytes(replay_result_a) == canonical_json_bytes(replay_result_b)
        ),
        "clause_context_bytes_equal": (
            render_clause_context(preflight_request, replay_result_a).encode("utf-8")
            == render_clause_context(preflight_request, replay_result_b).encode("utf-8")
        ),
    }
    scripts_dir = Path(__file__).resolve().parent
    skill_root = scripts_dir.parent
    default_path_integration = any(
        "query_norm_context" in path.read_text(encoding="utf-8")
        for path in (skill_root / "SKILL.md", scripts_dir / "compile_norm_context.py")
    )
    query_engine_text = (scripts_dir / "query_norm_context.py").read_text(encoding="utf-8")
    remote_semantic_enabled = any(
        marker in query_engine_text
        for marker in ("requests.", "httpx.", "urllib.request", "socket.create_connection")
    )
    canonical_path_guards: dict[str, bool] = {}
    for label, canonical in (
        ("index_metadata", environment.index_metadata_path),
        ("consistency_report", environment.consistency_report_path),
        ("budget_baseline", environment.budget_baseline_path),
    ):
        try:
            require_canonical_path(
                canonical.with_name(f"noncanonical-{canonical.name}"), canonical, label
            )
        except GovernanceError:
            canonical_path_guards[label] = True
        else:
            canonical_path_guards[label] = False
    passed = (
        all(item["passed"] for item in summaries)
        and all(item["passed"] for item in hard_gates)
        and all(item["passed"] for item in compatibility.values())
        and planner_fixtures["status"] == "Passed"
        and adversarial_tests["status"] == "Passed"
        and all(canonical_path_guards.values())
        and all(deterministic_artifact_replay.values())
        and default_path_integration == expected_default_path_integration
        and not remote_semantic_enabled
    )
    evaluation = {
        "schema_version": "6.3-candidate",
        "report_type": "norm-query-gateway-evaluation",
        "project_id": project_id,
        "task_id": task_id,
        "generated_at": now_utc(),
        "status": "Passed" if passed else "Failed",
        "expected_default_path_integration": expected_default_path_integration,
        "query_engine": {
            "path": "run-web-product-workflow/scripts/query_norm_context.py",
            "sha256": sha256_file(Path(__file__).with_name("query_norm_context.py")),
        },
        "index_digest": environment.index_metadata["index_digest"],
        "tailoring_resolution_sha256": environment.tailoring_sha256,
        "case_summary": {
            "total": len(summaries),
            "passed": sum(item["passed"] for item in summaries),
            "failed": sum(not item["passed"] for item in summaries),
        },
        "cases": summaries,
        "mandatory_targets": target_checks,
        "hard_gates": hard_gates,
        "observations": observations,
        "compatibility": compatibility,
        "contract_validation": validation,
        "planner_fixtures": planner_fixtures,
        "adversarial_tests": adversarial_tests,
        "deterministic_artifact_replay": deterministic_artifact_replay,
        "canonical_input_path_guards": canonical_path_guards,
        "default_path_integration": default_path_integration,
        "remote_semantic_enabled": remote_semantic_enabled,
    }
    gold_results = {
        "schema_version": "6.3-candidate",
        "evaluation_id": gold["evaluation_id"],
        "evaluation_version": gold["version"],
        "project_id": project_id,
        "task_id": task_id,
        "status": evaluation["status"],
        "query_engine_sha256": evaluation["query_engine"]["sha256"],
        "index_digest": environment.index_metadata["index_digest"],
        "cases": summaries,
        "hard_gates": hard_gates,
    }
    return evaluation, gold_results


def render_query_evaluation(report: dict[str, Any]) -> str:
    lines = [
        "# T-015 规范查询网关评测",
        "",
        f"- Status: `{report['status']}`",
        f"- Index digest: `{report['index_digest']}`",
        f"- Gold cases: `{report['case_summary']['passed']}/{report['case_summary']['total']}`",
        f"- Adversarial checks: `{report['adversarial_tests']['passed']}/{report['adversarial_tests']['total']}`",
        f"- Default path integration: `{report['default_path_integration']}`",
        f"- Remote semantic enabled: `{report['remote_semantic_enabled']}`",
        "",
        "## Hard Gates",
        "",
        "| Gate | Metric | Result |",
        "|---|---|---|",
    ]
    for gate in report["hard_gates"]:
        lines.append(f"| {gate['gate_id']} | {gate['metric']} | {'Passed' if gate['passed'] else 'Failed'} |")
    lines.extend(["", "## Gold Cases", "", "| Case | Category | Expected | Actual | Result |", "|---|---|---|---|---|"])
    for case in report["cases"]:
        lines.append(
            f"| {case['case_id']} | {case['category']} | {case['expected_outcome']} | "
            f"{case['actual_status']} | {'Passed' if case['passed'] else 'Failed'} |"
        )
    failed = [item for item in report["cases"] if not item["passed"]]
    if failed:
        lines.extend(["", "## Failed Details", ""])
        for item in failed:
            lines.append(
                f"- `{item['case_id']}` missing sources={item['missing_expected_sources']} "
                f"missing controls={item['missing_expected_controls']} targets={item['target_checks']}"
            )
    return "\n".join(lines) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    validation = report["validation"]
    benchmark_data = report["benchmark"]
    budgets = benchmark_data["budget_recommendations"]
    lines = [
        "# T-013 现有 rg / Source Pack 基准与预算候选",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Validation: `{report['status']}`",
        f"- Manifest closure: `{validation['manifest_files']}` files",
        f"- Contract fixtures: `{validation['fixture_counts']['positive']}` positive / "
        f"`{validation['fixture_counts']['schema_negative']}` schema-negative / "
        f"`{validation['fixture_counts']['semantic_negative']}` semantic-negative",
        f"- Coverage: `{validation['requirement_coverage']}` REQ / `{validation['acceptance_coverage']}` AC / `{validation['hard_gate_count']}` hard gates",
        f"- Mandatory clause denominator: `{validation['mandatory_target_count']}` stable targets",
        f"- Compatibility: T-008 S5 exact / `{validation['compatibility']['cli_contract_count']}` CLI contracts",
        "",
        "## 体量与读取基准",
        "",
        "| 载体 | Bytes | Chars | Lines | Sources | Read p50 ms | Read p95 ms | Replay |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| Norm Packet | {benchmark_data['norm_packet']['bytes']} | {benchmark_data['norm_packet']['chars']} | "
            f"{benchmark_data['norm_packet']['lines']} | - | {benchmark_data['norm_packet']['read']['p50_ms']} | "
            f"{benchmark_data['norm_packet']['read']['p95_ms']} | {benchmark_data['norm_packet']['read']['replay_consistent']} |"
        ),
        (
            f"| Source Pack | {benchmark_data['source_pack']['bytes']} | {benchmark_data['source_pack']['chars']} | "
            f"{benchmark_data['source_pack']['lines']} | {benchmark_data['source_pack']['source_count']} | "
            f"{benchmark_data['source_pack']['read']['p50_ms']} | {benchmark_data['source_pack']['read']['p95_ms']} | "
            f"{benchmark_data['source_pack']['read']['replay_consistent']} |"
        ),
        "",
        "## rg 查询基准",
        "",
        f"固定查询 `{benchmark_data['legacy_rg']['case_count']}` 个，每个预热1次、测量 `{benchmark_data['legacy_rg']['repetitions']}` 次。",
        "",
        "| Case | Hits | Matched chars | p50 ms | p95 ms | Replay |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in benchmark_data["legacy_rg"]["cases"]:
        lines.append(
            f"| {item['case_id']} | {item['hit_count']} | {item['matched_chars']} | {item['p50_ms']} | {item['p95_ms']} | {item['replay_consistent']} |"
        )
    lines.extend(
        [
            "",
            "## 预算档位候选",
            "",
            "这些数字是 T-013 测量候选，不构成 V6.3 批准或默认启用。P0/P1 仍禁止静默截断；完整来源超过页预算时必须有序分页。",
            "",
            "| Profile | Candidate | Context chars | Est. tokens | Sources | Escalations |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name in ("compact", "standard", "extended", "source-required"):
        item = budgets["profiles"][name]
        lines.append(
            f"| {name} | {item['candidate_limit']} | {item['context_chars']} | {item['estimated_tokens']} | {item['source_limit']} | {item['escalation_limit']} |"
        )
    lines.extend(["", "## 推导依据", ""])
    lines.extend(f"- {item}" for item in budgets["derivation"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--task-id")
    parser.add_argument("--source-pack", type=Path)
    parser.add_argument("--norm-packet", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help="Validate protected runtime contracts without external norm-development snapshots.",
    )
    parser.add_argument("--query-evaluation", action="store_true")
    parser.add_argument("--task-dir", type=Path)
    parser.add_argument("--index-metadata", type=Path)
    parser.add_argument("--consistency-report", type=Path)
    parser.add_argument("--budget-baseline", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validation = validate_contracts(
            args.project_root.resolve() if args.project_root else None,
            verify_project_snapshots=not args.runtime_only,
        )
        if args.validate_only:
            print(json.dumps({"status": "Passed", "validation": validation}, ensure_ascii=False, indent=2))
            return 0
        if args.query_evaluation:
            required = (
                args.project_root,
                args.project_id,
                args.task_id,
                args.task_dir,
                args.output_dir,
            )
            if any(value is None for value in required):
                raise GovernanceError(
                    "query evaluation requires --project-root, --project-id, --task-id, "
                    "--task-dir, and --output-dir"
                )
            project_root = args.project_root.resolve()
            output_dir = args.output_dir.resolve()
            evaluation, gold_results = query_gateway_evaluation(
                project_root=project_root,
                project_id=args.project_id,
                task_id=args.task_id,
                task_dir=args.task_dir.resolve(),
                index_metadata=args.index_metadata.resolve() if args.index_metadata else None,
                consistency_report=args.consistency_report.resolve() if args.consistency_report else None,
                budget_baseline=args.budget_baseline.resolve() if args.budget_baseline else None,
                validation=validation,
            )
            output_dir.mkdir(parents=True, exist_ok=True)
            root = governance_root(project_root)
            json_path = output_dir / "query-gateway-evaluation.json"
            markdown_path = output_dir / "query-gateway-evaluation.md"
            gold_path = output_dir / "query-gold-results.json"
            common_sources = [
                embedded_manifest_path(),
                runtime_asset_path("mappings/norm-action-taxonomy.json"),
                runtime_asset_path("evaluations/norm-retrieval-gold.json"),
                runtime_asset_path("schemas/norm-query.schema.json"),
                runtime_asset_path("schemas/norm-query-result.schema.json"),
                Path(__file__).resolve(),
                Path(__file__).with_name("query_norm_context.py").resolve(),
                args.task_dir.resolve() / "before.json",
            ]
            evaluation_content = json.dumps(
                evaluation, ensure_ascii=False, indent=2, sort_keys=True
            ) + "\n"
            _write_derived_view(
                root=root,
                content_path=json_path,
                content=evaluation_content,
                project_id=args.project_id,
                view_id=f"DV-{args.task_id}-QUERY-EVALUATION-JSON",
                view_kind="norm-query-gateway-evaluation-json",
                sources=common_sources,
            )
            _write_derived_view(
                root=root,
                content_path=markdown_path,
                content=render_query_evaluation(evaluation),
                project_id=args.project_id,
                view_id=f"DV-{args.task_id}-QUERY-EVALUATION-MD",
                view_kind="norm-query-gateway-evaluation-review",
                sources=[json_path],
            )
            _write_derived_view(
                root=root,
                content_path=gold_path,
                content=json.dumps(gold_results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                project_id=args.project_id,
                view_id=f"DV-{args.task_id}-GOLD-RESULTS",
                view_kind="norm-query-gold-results",
                sources=[json_path, runtime_asset_path("evaluations/norm-retrieval-gold.json")],
            )
            evidence_snapshot = write_immutable_evidence_snapshot(
                root=root,
                output_dir=output_dir,
                stem="query-gateway-evaluation",
                content=evaluation_content,
                project_id=args.project_id,
                task_id=args.task_id,
                view_kind="norm-query-gateway-evaluation-json",
                sources=common_sources,
                generated_at=evaluation["generated_at"],
            )
            print(json.dumps({
                "status": evaluation["status"],
                "cases": evaluation["case_summary"],
                "hard_gates": evaluation["hard_gates"],
                "output": str(output_dir),
                "evidence_snapshot": str(evidence_snapshot),
            }, ensure_ascii=False, indent=2))
            return 0 if evaluation["status"] == "Passed" else 4
        required_args = (
            args.project_root,
            args.project_id,
            args.task_id,
            args.source_pack,
            args.norm_packet,
            args.output_dir,
        )
        if any(value is None for value in required_args):
            raise GovernanceError(
                "benchmark mode requires --project-root, --project-id, --task-id, "
                "--source-pack, --norm-packet, and --output-dir"
            )
        benchmark_data = benchmark(args.source_pack.resolve(), args.norm_packet.resolve(), args.repetitions)
        report = {
            "schema_version": "6.3-candidate",
            "report_type": "legacy-retrieval-baseline",
            "project_id": args.project_id,
            "task_id": args.task_id,
            "generated_at": now_utc(),
            "generator": {
                "path": "run-web-product-workflow/scripts/audit_norm_retrieval.py",
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "status": "Passed",
            "validation": validation,
            "benchmark": benchmark_data,
        }
        root = governance_root(args.project_root.resolve())
        output_dir = args.output_dir.resolve()
        json_path = output_dir / "legacy-retrieval-baseline.json"
        markdown_path = output_dir / "legacy-retrieval-baseline.md"
        sources = [
            embedded_manifest_path(),
            runtime_asset_path("mappings/norm-action-taxonomy.json"),
            runtime_asset_path("evaluations/norm-retrieval-gold.json"),
            *(runtime_asset_path(f"schemas/{name}") for name in SCHEMA_NAMES),
            Path(__file__).resolve(),
            args.source_pack.resolve(),
            args.norm_packet.resolve(),
        ]
        json_content = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        _write_derived_view(
            root=root,
            content_path=json_path,
            content=json_content,
            project_id=args.project_id,
            view_id=f"DV-{args.task_id}-LEGACY-RETRIEVAL-BASELINE-JSON",
            view_kind="legacy-retrieval-baseline-json",
            sources=sources,
        )
        _write_derived_view(
            root=root,
            content_path=markdown_path,
            content=render_markdown(report),
            project_id=args.project_id,
            view_id=f"DV-{args.task_id}-LEGACY-RETRIEVAL-BASELINE-MD",
            view_kind="legacy-retrieval-baseline-review",
            sources=[json_path],
        )
        print(json.dumps({"status": "Passed", "output": str(output_dir), "validation": validation}, ensure_ascii=False, indent=2))
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        GovernanceError,
        ValueError,
        KeyError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
