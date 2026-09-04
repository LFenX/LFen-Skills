#!/usr/bin/env python3
"""Standard-library helpers for the V6.3 Candidate governance artifacts."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "6.3-candidate"
DERIVED_VIEW_CANONICAL_FIELDS_LEGACY = (
    "schema_version",
    "meta_type",
    "project_id",
    "view_id",
    "view_kind",
    "legacy_kind",
    "generated_at",
    "generator",
    "source_snapshot",
    "sources",
    "content_ref",
    "integrity_status",
)
DERIVED_VIEW_CANONICAL_FIELDS = (
    *DERIVED_VIEW_CANONICAL_FIELDS_LEGACY[:9],
    "source_snapshot_method",
    *DERIVED_VIEW_CANONICAL_FIELDS_LEGACY[9:],
)
LEGACY_RUN_POLICY_CUTOFF = "2026-08-15T00:00:00Z"
META_TYPES = {
    "ProjectState",
    "TaskContract",
    "RunLedger",
    "TaskOutcome",
    "AuthorityAsset",
    "DerivedView",
}
OUTCOME_STATES = {
    "Implemented",
    "Deferred",
    "Cancelled",
    "Blocked",
    "Superseded",
}
RUN_EVENT_TYPES = {
    "run_started",
    "mutation",
    "failure",
    "retry",
    "verification",
    "external_effect",
    "human_gate",
    "authority_decision_reference",
    "rollback",
    "run_finished",
}
RUN_STATUSES = {"started", "succeeded", "failed", "blocked", "skipped", "recorded"}
VERIFICATION_RESULTS = {"Passed", "Failed", "Blocked", "Skipped", "Not Applicable"}
EXTENSION_STATES = {
    "Not Evaluated", "Pending", "Inactive", "Conditionally Active",
    "Active", "Retiring", "Retired",
}
DELIVERY_SCENARIOS = {"DS-01", "DS-02", "DS-03", "DS-04"}
DEVELOPMENT_TYPES = {
    "DT-01", "DT-02", "DT-03", "DT-04", "DT-05",
    "DT-06", "DT-07", "DT-08", "DT-09",
}
CHANGE_SURFACES = {
    "UI/UX",
    "API/Integration",
    "Data/Schema",
    "Identity/Security/Privacy",
    "AI/Data Governance",
    "Architecture/Multi-repo",
    "Deploy/Operations",
    "Agent/Collaboration",
}
BASELINE_INHERITANCE_STATES = {"New", "Reference", "Revise", "Supersede"}
TAILORING_STAGES = {f"S{value}" for value in range(1, 9)}
APPLICABILITY_FACT_VALUES = {"Yes", "No", "Unknown"}
EXECUTION_PERMISSIONS = {"read", "edit-in-scope", "validate", "external-effect", "rollback"}
APPLICABILITY_FACTS = {
    "product_intent_change",
    "initiative_scope_change",
    "requirement_change",
    "external_behavior_change",
    "design_change",
    "architecture_impact",
    "security_privacy_impact",
    "data_ai_impact",
    "formal_knowledge_records",
    "operations_impact",
    "production_release",
    "irreversible_change",
    "actual_execution",
    "authority_available",
    "migration_retirement",
    "external_system_effect",
    "formal_review_or_gate",
}
STATE_MODELS = {
    "DOC": {"Draft", "In Review", "Changes Required", "Approved", "Baselined", "Rejected", "Superseded", "Retired"},
    "CASE": {"Open", "In Progress", "Blocked", "Resolved", "Closed", "Reopened", "Cancelled"},
    "EXEC": {"Planned", "Ready", "Running", "Blocked", "Completed", "Failed", "Accepted", "Rejected", "Cancelled"},
    "EVID": {"Planned", "Collected", "Under Review", "Accepted", "Rejected", "Invalidated"},
    "DEC": {"Proposed", "Under Review", "Approved", "Conditionally Approved", "Rejected", "Waived", "Superseded", "Expired"},
    "REC": {"Recorded", "Corrected", "Superseded", "Archived"},
}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
PROFILE_RE = re.compile(r"^[A-Z][A-Z0-9]{2}$")
IMMUTABLE_FIELDS = {
    "schema_version",
    "meta_type",
    "project_id",
    "work_item_id",
    "task_id",
    "revision",
    "lifecycle_state",
    "created_at",
    "frozen_at",
    "completed_at",
    "amendments",
}


class GovernanceError(ValueError):
    """Raised for invalid governance data or an unsafe state transition."""


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file without changing filesystem state."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_id(value: str, label: str) -> str:
    if not ID_RE.fullmatch(value):
        raise GovernanceError(
            f"{label} must match {ID_RE.pattern}; received {value!r}"
        )
    return value


def read_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise GovernanceError(f"{path} must contain a JSON object")
    if (
        value.get("meta_type") == "DerivedView"
        and "view_id" in value
        and "view_kind" in value
        and "content_ref" in value
    ):
        if tuple(value) not in {
            DERIVED_VIEW_CANONICAL_FIELDS_LEGACY,
            DERIVED_VIEW_CANONICAL_FIELDS,
        }:
            raise GovernanceError(f"{path} DerivedView fields are not in canonical order")
        expected = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if raw != expected:
            raise GovernanceError(f"{path} DerivedView bytes are not canonical")
    return value


SKILL_ROOT_ENV = "LG_SKILL_ROOT"

# The sealed runtime set, by role. Adding a protected asset means updating this and
# resealing; the total is derived so the two can never disagree.
EXPECTED_MANIFEST_ROLES = {
    "norm": 22,
    "mapping": 3,
    "schema": 11,
    "skill-reference": 3,
    "evaluation": 2,
    "asset-template": 5,
}


def _is_skill_root(candidate: Path) -> bool:
    return (candidate / "assets" / "runtime" / "embedded-manifest.json").is_file()


def skill_root_path() -> Path:
    """Locate the Skill root, normally from this file's own position.

    A console deployed into a project carries a verbatim snapshot of these modules,
    so __file__ then points into the project rather than at any Skill. Only in that
    case is LG_SKILL_ROOT consulted, and only if it really is a Skill root. Keeping
    the override subordinate to the local answer means a stale environment variable
    can never silently redirect the Skill's own scripts at a different version.
    """

    local = Path(__file__).resolve().parent.parent
    if _is_skill_root(local):
        return local
    override = os.environ.get(SKILL_ROOT_ENV, "").strip()
    if override:
        candidate = Path(override).expanduser().resolve()
        if _is_skill_root(candidate):
            return candidate
    return local


def embedded_manifest_path(skill_root: Path | None = None) -> Path:
    root = (skill_root or skill_root_path()).resolve()
    return root / "assets" / "runtime" / "embedded-manifest.json"


def runtime_asset_path(
    logical_path: str,
    *,
    skill_root: Path | None = None,
    verify_hash: bool = True,
) -> Path:
    """Resolve a stable logical Skill path through the integrity manifest."""

    root = (skill_root or skill_root_path()).resolve()
    manifest_path = embedded_manifest_path(root)
    manifest = read_json(manifest_path)
    files = manifest.get("files")
    if not isinstance(files, list):
        raise GovernanceError(f"{manifest_path}: files must be an array")
    matches = [
        item for item in files
        if isinstance(item, dict) and item.get("logical_path") == logical_path
    ]
    if len(matches) != 1:
        raise GovernanceError(
            f"{manifest_path}: logical path {logical_path!r} must resolve exactly once"
        )
    item = matches[0]
    embedded = item.get("embedded")
    expected = item.get("sha256")
    if not isinstance(embedded, str) or not isinstance(expected, str):
        raise GovernanceError(f"{manifest_path}: invalid entry for {logical_path}")
    target = (root / embedded).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise GovernanceError(f"manifest path escapes Skill root: {embedded}") from exc
    if not target.is_file():
        raise GovernanceError(f"runtime asset is missing: {embedded}")
    if verify_hash and hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise GovernanceError(f"runtime asset hash mismatch: {embedded}")
    return target


def schema_path(schema_name: str) -> Path:
    return runtime_asset_path(f"schemas/{schema_name}")


def _matches_json_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _validate_schema_node(value: Any, schema: dict[str, Any], location: str) -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not isinstance(expected_types, list) or not all(isinstance(item, str) for item in expected_types):
            return [f"{location}: schema type declaration is invalid"]
        if not any(_matches_json_type(value, item) for item in expected_types):
            return [f"{location}: expected type {' or '.join(expected_types)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value {value!r} is not in the allowed set")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{location}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"{location}: does not match pattern {pattern}")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{location}: is not a valid date-time")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{location}: must be at least {minimum}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: has fewer than minItems entries")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{location}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_validate_schema_node(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{location}.{key}: required property is missing")
        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{location}: has fewer than minProperties entries")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, child in value.items():
                child_schema = properties.get(key)
                if isinstance(child_schema, dict):
                    errors.extend(_validate_schema_node(child, child_schema, f"{location}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{location}.{key}: additional property is not allowed")
    return errors


def validate_json_document(value: dict[str, Any], schema_name: str, location: str = "$") -> list[str]:
    """Validate against the JSON-Schema subset used by this Skill, using stdlib only."""

    schema = read_json(schema_path(schema_name))
    return _validate_schema_node(value, schema, location)


def require_valid_json_document(value: dict[str, Any], schema_name: str, location: str = "$") -> None:
    errors = validate_json_document(value, schema_name, location)
    if errors:
        raise GovernanceError("; ".join(errors))


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GovernanceError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise GovernanceError(f"{path}:{line_number}: event must be an object")
        events.append(value)
    return events


def validate_query_history(project_root: Path, task_id: str) -> dict[str, Any]:
    """Validate immutable query archives, redirects, and the complete active set."""

    project_root = project_root.resolve()
    history_root = (
        project_root / ".project-governance" / "generated" / "query-history" / task_id
    ).resolve()
    index = read_json(history_root / "archive-index.json")
    if index.get("task_id") != task_id or not isinstance(index.get("publications"), list):
        raise GovernanceError("query history archive index has an invalid task identity")

    def parse_time(value: Any, label: str) -> datetime:
        if not isinstance(value, str):
            raise GovernanceError(f"{label} is missing")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise GovernanceError(f"{label} is invalid") from exc
        if parsed.tzinfo is None:
            raise GovernanceError(f"{label} must include a timezone")
        return parsed

    def checked_files(directory: Path, expected: dict[str, Any], label: str) -> int:
        if not directory.is_dir():
            raise GovernanceError(f"{label} directory is missing: {directory}")
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        if actual != set(expected):
            raise GovernanceError(f"{label} file set differs: {directory}")
        for name, expected_sha256 in expected.items():
            actual_sha256 = hashlib.sha256((directory / name).read_bytes()).hexdigest()
            if actual_sha256 != expected_sha256:
                raise GovernanceError(f"{label} hash differs: {directory / name}")
        return len(expected)

    archive_files = 0
    archived_paths: set[str] = set()
    for publication in index["publications"]:
        if not isinstance(publication, dict) or not isinstance(publication.get("files"), dict):
            raise GovernanceError("query history publication entry is invalid")
        archived = (project_root / str(publication.get("archived_path"))).resolve()
        try:
            archived.relative_to(history_root)
        except ValueError as exc:
            raise GovernanceError("query history publication escapes its task history root") from exc
        archived_ref = archived.relative_to(project_root).as_posix()
        if archived_ref in archived_paths:
            raise GovernanceError("query history contains a duplicate archived path")
        archived_paths.add(archived_ref)
        archive_files += checked_files(archived, publication["files"], "query archive")
        original = (project_root / str(publication.get("original_path"))).resolve()
        if original.exists():
            raise GovernanceError(f"archived query publication remains active: {original}")
        archived_at = parse_time(publication.get("archived_at"), "publication archived_at")
        envelope = read_json(archived / "query-result.json.view.json")
        generated_at = parse_time(envelope.get("generated_at"), "publication generated_at")
        if generated_at > archived_at:
            raise GovernanceError("query publication was generated after its archive time")
        if publication.get("generated_at") != envelope.get("generated_at"):
            raise GovernanceError("query archive generated_at does not match its envelope")

    redirects = index.get("evidence_redirects")
    if not isinstance(redirects, list):
        raise GovernanceError("query history evidence_redirects must be an array")
    redirect_originals: set[str] = set()
    for redirect in redirects:
        if not isinstance(redirect, dict):
            raise GovernanceError("query history evidence redirect is invalid")
        original_ref = redirect.get("original_ref")
        archived_ref = redirect.get("archived_ref")
        if not isinstance(original_ref, str) or not isinstance(archived_ref, str):
            raise GovernanceError("query history evidence redirect path is invalid")
        if original_ref in redirect_originals:
            raise GovernanceError("query history has a duplicate evidence redirect")
        redirect_originals.add(original_ref)
        original = (project_root / original_ref).resolve()
        archived = (project_root / archived_ref).resolve()
        try:
            archived.relative_to(history_root)
        except ValueError as exc:
            raise GovernanceError("query history evidence redirect escapes its history root") from exc
        if original.exists() or not archived.is_file():
            raise GovernanceError("query history evidence redirect is not closed")
        if hashlib.sha256(archived.read_bytes()).hexdigest() != redirect.get("sha256"):
            raise GovernanceError("query history evidence redirect hash differs")

    archived_request_sets = index.get("archived_request_sets")
    if not isinstance(archived_request_sets, list):
        raise GovernanceError("query history archived_request_sets must be an array")
    request_set_paths: set[str] = set()
    archived_request_files = 0
    for request_set in archived_request_sets:
        if not isinstance(request_set, dict) or not isinstance(request_set.get("files"), dict):
            raise GovernanceError("query history archived request set is invalid")
        directory = (project_root / str(request_set.get("path"))).resolve()
        try:
            directory.relative_to(history_root)
        except ValueError as exc:
            raise GovernanceError("query history archived request set escapes its history root") from exc
        directory_ref = directory.relative_to(project_root).as_posix()
        if directory_ref in request_set_paths:
            raise GovernanceError("query history archived request set is duplicated")
        request_set_paths.add(directory_ref)
        expected = request_set["files"]
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        if actual != set(expected):
            raise GovernanceError("query history archived request file set differs")
        for name, expected_sha256 in expected.items():
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected_sha256:
                raise GovernanceError("query history archived request hash differs")
            archived_request_files += 1

    active_entries = index.get("active_publications")
    if not isinstance(active_entries, list) or not active_entries:
        raise GovernanceError("query history active_publications must be a non-empty array")
    active_root = (
        project_root / ".project-governance" / "generated" / "queries" / task_id
    ).resolve()
    active_refs: set[str] = set()
    active_actions: set[tuple[str, str]] = set()
    active_files = 0
    for publication in active_entries:
        if not isinstance(publication, dict) or not isinstance(publication.get("files"), dict):
            raise GovernanceError("query history active publication entry is invalid")
        result = (project_root / str(publication.get("result_path"))).resolve()
        try:
            result.relative_to(active_root)
        except ValueError as exc:
            raise GovernanceError("active query publication escapes its task root") from exc
        result_ref = result.relative_to(project_root).as_posix()
        if result_ref in active_refs:
            raise GovernanceError("query history contains a duplicate active publication")
        active_refs.add(result_ref)
        active_files += checked_files(result.parent, publication["files"], "active query")
        result_document = read_json(result)
        if result_document.get("query_digest") != publication.get("query_digest"):
            raise GovernanceError("active query digest does not match the result")
        envelope = read_json(result.with_suffix(result.suffix + ".view.json"))
        if envelope.get("generated_at") != publication.get("generated_at"):
            raise GovernanceError("active query generated_at does not match its envelope")
        request_ref = publication.get("request_path")
        if not isinstance(request_ref, str):
            raise GovernanceError("active query request path is missing")
        request = (project_root / request_ref).resolve()
        if not request.is_file():
            raise GovernanceError("active query request is missing")
        if hashlib.sha256(request.read_bytes()).hexdigest() != publication.get("request_sha256"):
            raise GovernanceError("active query request hash differs")
        sources = envelope.get("sources")
        expected_request_ref = request.relative_to(project_root).as_posix()
        if not isinstance(sources, list) or not sources or sources[0] != expected_request_ref:
            raise GovernanceError("active query envelope is not bound to its request")
        request_document = read_json(request)
        if request_document.get("task_id") != task_id:
            raise GovernanceError("active query request task identity differs")
        action = request_document.get("action")
        identity = (str(action), result_document["query_digest"])
        if identity in active_actions:
            raise GovernanceError("active query action/digest identity is duplicated")
        active_actions.add(identity)

    actual_active = {
        path.resolve().relative_to(project_root).as_posix()
        for path in active_root.rglob("query-result.json")
        if "requests" not in path.parts
    }
    if actual_active != active_refs:
        raise GovernanceError("query history does not enumerate the complete active publication set")
    current_ref = index.get("current_active_query_result")
    if not isinstance(current_ref, str) or current_ref not in active_refs:
        raise GovernanceError("query history current_active_query_result is not in the active set")
    return {
        "status": "Passed",
        "publications": len(index["publications"]),
        "archive_files": archive_files,
        "redirects": len(redirects),
        "archived_request_sets": len(archived_request_sets),
        "archived_request_files": archived_request_files,
        "active_publications": len(active_entries),
        "active_files": active_files,
        "current_active_query_result": current_ref,
    }


def governance_root(project_root: Path) -> Path:
    return project_root.resolve() / ".project-governance"


def task_directory(project_root: Path, task_id: str) -> Path:
    require_id(task_id, "task_id")
    return governance_root(project_root) / "tasks" / task_id


def capture_source_snapshot(project_root: Path) -> dict[str, Any]:
    """Capture an honest Git snapshot; fall back to a non-Git filesystem snapshot."""

    root = project_root.resolve()
    captured = now_utc()
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], cwd=root, check=True,
            text=True, encoding="utf-8", errors="replace", capture_output=True,
        )
        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=root, check=True,
            text=True, encoding="utf-8", errors="replace", capture_output=True,
        ).stdout.strip()
        head_result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=root, check=False,
            text=True, encoding="utf-8", errors="replace", capture_output=True,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=root,
            check=True, text=True, encoding="utf-8", errors="replace", capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {
            "repository": root.name,
            "root": str(root),
            "vcs": "unavailable",
            "captured_at": captured,
        }
    entries = [line for line in status.splitlines() if line]
    head = head_result.stdout.strip() if head_result.returncode == 0 else "UNBORN"
    return {
        "repository": root.name,
        "root": str(root),
        "vcs": "git",
        "branch": branch or "DETACHED",
        "head": head,
        "head_exists": head != "UNBORN",
        "dirty": bool(entries),
        "dirty_entries": len(entries),
        "status_digest": hashlib.sha256(status.encode("utf-8")).hexdigest(),
        "captured_at": captured,
    }


def default_mapping_path() -> Path:
    return runtime_asset_path("mappings/profile-meta-map.json")


def default_tailoring_map_path() -> Path:
    return runtime_asset_path("mappings/tailoring-applicability-map.json")


def default_profile_index_path() -> Path:
    return runtime_asset_path("references/05_记录与登记册/V6.3_跨规范产物归属索引.md")


def validate_embedded_manifest(skill_root: Path | None = None) -> list[str]:
    root = (skill_root or skill_root_path()).resolve()
    manifest_path = embedded_manifest_path(root)
    errors: list[str] = []
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return [str(exc)]
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{manifest_path}: schema_version must be {SCHEMA_VERSION}")
    if manifest.get("layout_version") != "skill-runtime-v2":
        errors.append(f"{manifest_path}: layout_version must be skill-runtime-v2")
    files = manifest.get("files")
    if not isinstance(files, list):
        return [f"{manifest_path}: files must be an array"]
    required_runtime = {
        path.relative_to(root).as_posix()
        for path in (root / "references").rglob("*.md")
    } | {
        path.relative_to(root).as_posix()
        for path in (root / "assets" / "runtime" / "norms").rglob("*.md")
    } | {
        path.relative_to(root).as_posix()
        for path in (root / "assets" / "runtime" / "mappings").glob("*.json")
    } | {
        path.relative_to(root).as_posix()
        for path in (root / "assets" / "runtime" / "schemas").glob("*.json")
    } | {
        path.relative_to(root).as_posix()
        for path in (root / "assets" / "runtime" / "evaluations").glob("*.json")
    } | {
        path.relative_to(root).as_posix()
        for path in (root / "assets" / "project-templates").glob("*")
        if path.is_file()
    }
    listed: set[str] = set()
    logical_paths: set[str] = set()
    role_counts = {
        "norm": 0,
        "mapping": 0,
        "schema": 0,
        "skill-reference": 0,
        "evaluation": 0,
        "asset-template": 0,
    }
    for position, item in enumerate(files):
        if not isinstance(item, dict):
            errors.append(f"manifest.files[{position}] must be an object")
            continue
        relative = item.get("embedded")
        logical = item.get("logical_path")
        role = item.get("role")
        expected = item.get("sha256")
        source = item.get("source")
        if (
            not isinstance(relative, str)
            or not isinstance(logical, str)
            or not isinstance(source, str)
            or not isinstance(expected, str)
            or role not in role_counts
        ):
            errors.append(
                f"manifest.files[{position}] requires role, source, logical_path, embedded, and sha256"
            )
            continue
        role_counts[role] += 1
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            errors.append(f"manifest.files[{position}].sha256 is invalid")
            continue
        if relative in listed:
            errors.append(f"manifest contains duplicate embedded path: {relative}")
        listed.add(relative)
        if logical in logical_paths:
            errors.append(f"manifest contains duplicate logical path: {logical}")
        logical_paths.add(logical)
        expected_prefixes = {
            "norm": ("references/", "assets/runtime/norms/"),
            "mapping": ("mappings/", "assets/runtime/mappings/"),
            "schema": ("schemas/", "assets/runtime/schemas/"),
            "skill-reference": ("references/", "references/"),
            "evaluation": ("evaluations/", "assets/runtime/evaluations/"),
            "asset-template": ("project-templates/", "assets/project-templates/"),
        }
        logical_prefix, embedded_prefix = expected_prefixes[role]
        if not logical.startswith(logical_prefix) or not relative.startswith(embedded_prefix):
            errors.append(
                f"manifest.files[{position}] has invalid {role} logical/embedded path"
            )
        target = (root / Path(relative)).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            errors.append(f"manifest path escapes Skill root: {relative}")
            continue
        if not target.is_file():
            errors.append(f"embedded file is missing: {relative}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"embedded file hash mismatch: {relative}")
    for relative in sorted(required_runtime - listed):
        errors.append(f"runtime fact is absent from embedded manifest: {relative}")
    for relative in sorted(listed - required_runtime):
        errors.append(f"embedded manifest contains an undeclared runtime fact: {relative}")
    if role_counts != EXPECTED_MANIFEST_ROLES or len(files) != sum(EXPECTED_MANIFEST_ROLES.values()):
        expected = ", ".join(f"{role}={count}" for role, count in EXPECTED_MANIFEST_ROLES.items())
        errors.append(
            f"embedded manifest must contain {sum(EXPECTED_MANIFEST_ROLES.values())} files "
            f"with roles {expected}"
        )
    return errors


def ensure_skill_integrity() -> None:
    errors = validate_embedded_manifest()
    if errors:
        raise GovernanceError("Skill integrity check failed: " + "; ".join(errors))


def load_mapping(path: Path | None = None) -> dict[str, Any]:
    target = path or default_mapping_path()
    mapping = read_json(target)
    if set(mapping.get("meta_types", [])) != META_TYPES:
        raise GovernanceError(f"{target}: meta_types must contain the six V6.3 types")
    if mapping.get("default_meta_type") != "AuthorityAsset":
        raise GovernanceError(f"{target}: default_meta_type must be AuthorityAsset")
    overrides = mapping.get("overrides")
    if not isinstance(overrides, dict):
        raise GovernanceError(f"{target}: overrides must be an object")
    seen: set[str] = set()
    for meta_type, codes in overrides.items():
        if meta_type not in META_TYPES:
            raise GovernanceError(f"{target}: unknown meta type {meta_type}")
        if not isinstance(codes, list):
            raise GovernanceError(f"{target}: overrides.{meta_type} must be an array")
        for code in codes:
            if not isinstance(code, str) or not PROFILE_RE.fullmatch(code):
                raise GovernanceError(f"{target}: invalid legacy profile code {code!r}")
            if code in seen:
                raise GovernanceError(f"{target}: duplicate override for {code}")
            seen.add(code)
    return mapping


def validate_tailoring_map(
    mapping: dict[str, Any],
    *,
    skill_root: Path | None = None,
    profile_index: Path | None = None,
    meta_mapping: Path | None = None,
) -> list[str]:
    """Prove that the executable tailoring table closes every controlled dimension."""

    root = (skill_root or Path(__file__).resolve().parent.parent).resolve()
    errors: list[str] = []
    if mapping.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"tailoring map schema_version must be {SCHEMA_VERSION}")
    if mapping.get("document_id") != "VC-PPG-TAIL-001":
        errors.append("tailoring map document_id must be VC-PPG-TAIL-001")
    semantics = mapping.get("semantics")
    clause_policy = semantics.get("normative_clause_policy") if isinstance(semantics, dict) else None
    if (
        not isinstance(clause_policy, dict)
        or set(clause_policy.get("navigation_only", [])) != {"non_trimmable_controls", "source_sections"}
        or not clause_policy.get("applicable_standard")
        or not clause_policy.get("pending_standard")
        or not clause_policy.get("complete_pack")
    ):
        errors.append("semantics.normative_clause_policy is incomplete")
    resolution_contract = mapping.get("resolution_contract")
    expected_resolution_outputs = {
        "rule_set_sha256", "normative_sources_sha256", "resolver_sha256", "task_contract_schema_sha256",
        "input_digest", "applicable_standards", "pending_standards", "stage_context_standards",
        "control_strength", "independent_review", "blocking_reasons", "rule_ids", "source_sections",
        "complete_source_files", "profile_coverage_digest",
    }
    if (
        not isinstance(resolution_contract, dict)
        or set(resolution_contract.get("required_outputs", [])) != expected_resolution_outputs
    ):
        errors.append("resolution_contract.required_outputs is incomplete")
    controlled = mapping.get("controlled_values")
    expected_dimensions = {
        "delivery_scenarios": DELIVERY_SCENARIOS,
        "development_types": DEVELOPMENT_TYPES,
        "change_surfaces": CHANGE_SURFACES,
        "risk_levels": {"Low", "Medium", "High", "Critical"},
        "extension_states": EXTENSION_STATES,
        "baseline_inheritance": BASELINE_INHERITANCE_STATES,
        "execution_modes": {"Normal", "Emergency"},
        "confidence_levels": {"Low", "Medium", "High"},
        "stages": TAILORING_STAGES,
        "fact_values": APPLICABILITY_FACT_VALUES,
        "profile_actions": {"Create/Revise", "Reference", "Generate", "On Event", "N/A"},
        "execution_permissions": EXECUTION_PERMISSIONS,
    }
    if not isinstance(controlled, dict):
        errors.append("tailoring map controlled_values must be an object")
        controlled = {}
    for key, expected in expected_dimensions.items():
        actual = controlled.get(key)
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            errors.append(f"controlled_values.{key} must cover exactly {sorted(expected)}")
    standards = mapping.get("standards")
    expected_standards = {f"C{value:02d}" for value in range(1, 13)} | {
        f"E{value:02d}" for value in range(1, 6)
    }
    if not isinstance(standards, dict) or set(standards) != expected_standards:
        errors.append("tailoring map standards must contain exactly C01-C12 and E01-E05")
        standards = {}
    routes = mapping.get("routes")
    if not isinstance(routes, dict):
        errors.append("tailoring map routes must be an object")
        routes = {}
    route_dimensions = {
        "delivery_scenarios": DELIVERY_SCENARIOS,
        "development_types": DEVELOPMENT_TYPES,
        "change_surfaces": CHANGE_SURFACES,
        "risk_levels": {"Low", "Medium", "High", "Critical"},
        "baseline_inheritance": BASELINE_INHERITANCE_STATES,
        "execution_modes": {"Normal", "Emergency"},
    }
    for dimension, expected_keys in route_dimensions.items():
        table = routes.get(dimension)
        if not isinstance(table, dict) or set(table) != expected_keys:
            errors.append(f"routes.{dimension} must cover every controlled value exactly once")
            continue
        for key, rule in table.items():
            values = rule if isinstance(rule, list) else rule.get("minimum", rule.get("adds", [])) if isinstance(rule, dict) else []
            unknown = sorted(set(values) - expected_standards)
            if unknown:
                errors.append(f"routes.{dimension}.{key} contains unknown standards {unknown}")
    stage_context = mapping.get("stage_context")
    if not isinstance(stage_context, dict) or set(stage_context) != TAILORING_STAGES:
        errors.append("stage_context must contain exactly S1-S8")
    else:
        for stage, rule in stage_context.items():
            if not isinstance(rule, dict):
                errors.append(f"stage_context.{stage} must be an object")
                continue
            routed = set(rule.get("minimum_standards", [])) | set(rule.get("conditional_standards", []))
            if routed - expected_standards:
                errors.append(f"stage_context.{stage} contains unknown standards")
            if not rule.get("global_sections") or not rule.get("unknown_policy"):
                errors.append(f"stage_context.{stage} requires global_sections and unknown_policy")
    facts = mapping.get("applicability_facts")
    if not isinstance(facts, dict) or set(facts) != APPLICABILITY_FACTS:
        errors.append("applicability_facts must contain exactly the 17 controlled fact keys")
        facts = {}
    for key, rule in facts.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or not isinstance(rule, dict):
            errors.append(f"invalid applicability fact rule {key!r}")
            continue
        if set(rule.get("activates", [])) - expected_standards:
            errors.append(f"applicability fact {key} activates unknown standards")
        if rule.get("blocking_from_stage") not in TAILORING_STAGES:
            errors.append(f"applicability fact {key} has invalid blocking_from_stage")
    sources = mapping.get("source_catalog")
    expected_source_ids = {
        "VC-PPG-COM-001", "VC-PPG-COM-002", "VC-PPG-DEC-001", "VC-PPG-PRO-001",
        "VC-PPG-IDX-001", *expected_standards,
    }
    source_ids: set[str] = set()
    source_paths_by_id: dict[str, Path] = {}
    if not isinstance(sources, list):
        errors.append("source_catalog must be an array")
        sources = []
    for position, source in enumerate(sources):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not isinstance(source.get("path"), str):
            errors.append(f"source_catalog[{position}] requires id and path")
            continue
        source_ids.add(source["id"])
        try:
            target = runtime_asset_path(source["path"], skill_root=root)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            errors.append(f"tailoring source cannot be resolved: {source['path']}: {exc}")
        else:
            source_paths_by_id[source["id"]] = target
    if source_ids != expected_source_ids or len(sources) != len(expected_source_ids):
        errors.append("source_catalog must cover the four governance norms, C01-C12, E01-E05, and the profile index exactly once")
    reachable = set(routes.get("always_applicable", []))
    for dimension in ("delivery_scenarios", "development_types", "change_surfaces"):
        table = routes.get(dimension, {})
        if isinstance(table, dict):
            for rule in table.values():
                reachable.update(_standards_from_route(rule))
    for fact_rule in facts.values():
        if isinstance(fact_rule, dict):
            reachable.update(fact_rule.get("activates", []))
    unreachable = sorted(expected_standards - reachable)
    if unreachable:
        errors.append(f"standards are unreachable from all tailoring routes: {unreachable}")
    for standard, rule in standards.items():
        if not isinstance(rule, dict):
            errors.append(f"standards.{standard} must be an object")
            continue
        controls = rule.get("non_trimmable_controls")
        sections = rule.get("source_sections")
        if not isinstance(controls, list) or not controls or not all(isinstance(item, str) and item for item in controls):
            errors.append(f"standards.{standard}.non_trimmable_controls must be non-empty")
        if not isinstance(sections, list) or not sections:
            errors.append(f"standards.{standard}.source_sections must be non-empty")
            continue
        source_path = source_paths_by_id.get(standard)
        if source_path:
            headings = set(re.findall(r"^##\s+(\d+)\.\s+", source_path.read_text(encoding="utf-8"), flags=re.MULTILINE))
            missing_sections = sorted(set(sections) - headings, key=int)
            if missing_sections:
                errors.append(f"{standard} declares missing source sections {missing_sections}")
        if standard.startswith("E"):
            if rule.get("extension") is not True:
                errors.append(f"standards.{standard}.extension must be true")
            if not rule.get("trigger_facts"):
                errors.append(f"standards.{standard}.trigger_facts must be non-empty")
    profile_rule = mapping.get("profile_resolution")
    if not isinstance(profile_rule, dict) or profile_rule.get("expected_profile_count") != 137:
        errors.append("profile_resolution.expected_profile_count must be 137")
    gate_requirements = mapping.get("gate_requirements")
    if not isinstance(gate_requirements, dict):
        errors.append("gate_requirements must be an object")
    else:
        risk_gates = gate_requirements.get("risk_levels")
        fact_gates = gate_requirements.get("applicability_facts")
        if not isinstance(risk_gates, dict) or set(risk_gates) - {"High", "Critical"}:
            errors.append("gate_requirements.risk_levels may contain only High and Critical")
        if not isinstance(fact_gates, dict) or set(fact_gates) - set(facts):
            errors.append("gate_requirements.applicability_facts contains unknown fact keys")
    confidence_policy = mapping.get("confidence_policy")
    if not isinstance(confidence_policy, dict) or set(confidence_policy) != {"Low", "Medium", "High"}:
        errors.append("confidence_policy must contain exactly Low, Medium, and High")
    authority_policy = mapping.get("authority_policy")
    if not isinstance(authority_policy, dict):
        errors.append("authority_policy must be an object")
    else:
        if authority_policy.get("enforcement_from_stage") != "S4":
            errors.append("authority_policy.enforcement_from_stage must be S4")
        if set(authority_policy.get("source_kinds", [])) != {"UserDirective", "AuthorityAsset", "PlatformDecision", "Policy"}:
            errors.append("authority_policy.source_kinds is incomplete")
        if set(authority_policy.get("assessment_states", [])) != {"Valid", "Pending", "Invalid", "Expired"}:
            errors.append("authority_policy.assessment_states is incomplete")
        for flag in (
            "requires_reference_binding",
            "requires_evidence_refs",
            "requires_unexpired_assessment",
            "requires_verified_at_not_future",
            "requires_expiry_after_verification",
            "requires_complete_scope_coverage",
        ):
            if authority_policy.get(flag) is not True:
                errors.append(f"authority_policy.{flag} must be true")
        if authority_policy.get("scope_reference_target") != "scope.in_scope":
            errors.append("authority_policy.scope_reference_target must be scope.in_scope")
        fact_permissions = authority_policy.get("fact_permission_requirements")
        event_permissions = authority_policy.get("run_event_permission_requirements")
        if not isinstance(fact_permissions, dict) or set(fact_permissions) != {"external_system_effect", "production_release"} or any(
            set(values) - EXECUTION_PERMISSIONS for values in fact_permissions.values()
        ):
            errors.append("authority_policy.fact_permission_requirements is invalid")
        if not isinstance(event_permissions, dict) or set(event_permissions) != {"run_started", "mutation", "verification", "external_effect", "rollback"} or any(
            set(values) - EXECUTION_PERMISSIONS for values in event_permissions.values()
        ):
            errors.append("authority_policy.run_event_permission_requirements is invalid")
        if authority_policy.get("executable_state") != "Valid" or not authority_policy.get("gate_token_semantics"):
            errors.append("authority_policy executable state and gate token semantics are incomplete")
    multi_type_policy = mapping.get("multi_type_policy")
    if not isinstance(multi_type_policy, dict) or multi_type_policy.get("requires_scope_partition_when_multiple") is not True:
        errors.append("multi_type_policy must require scope partitioning")
    else:
        pairs = multi_type_policy.get("semantic_conflict_pairs")
        if not isinstance(pairs, list) or any(
            not isinstance(pair, list) or len(pair) != 2 or set(pair) - DEVELOPMENT_TYPES
            for pair in pairs
        ):
            errors.append("multi_type_policy.semantic_conflict_pairs is invalid")
    consistency = mapping.get("classification_consistency")
    if not isinstance(consistency, dict):
        errors.append("classification_consistency must be an object")
    else:
        surface_rules = consistency.get("fact_requires_any_surface")
        type_rules = consistency.get("fact_requires_any_development_type")
        if not isinstance(surface_rules, dict) or set(surface_rules) - set(facts) or any(set(values) - CHANGE_SURFACES for values in surface_rules.values()):
            errors.append("classification_consistency.fact_requires_any_surface is invalid")
        if not isinstance(type_rules, dict) or set(type_rules) - set(facts) or any(set(values) - DEVELOPMENT_TYPES for values in type_rules.values()):
            errors.append("classification_consistency.fact_requires_any_development_type is invalid")
    try:
        profiles = resolve_all_profiles(profile_index or default_profile_index_path(), meta_mapping)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        errors.append(f"cannot validate profile closure: {exc}")
        profiles = []
    owner_counts: dict[str, int] = {key: 0 for key in expected_standards}
    for profile in profiles:
        owner = profile.get("owner_standard")
        if owner not in owner_counts:
            errors.append(f"profile {profile.get('legacy_kind')} has unknown owner {owner}")
        else:
            owner_counts[owner] += 1
    for standard, expected_count in owner_counts.items():
        declared = standards.get(standard, {}).get("profile_count") if isinstance(standards.get(standard), dict) else None
        if declared != expected_count:
            errors.append(f"{standard} profile_count is {declared}, index contains {expected_count}")
    if len(profiles) != 137 or sum(owner_counts.values()) != 137:
        errors.append(f"tailoring profile closure must equal 137, found {len(profiles)}")
    return errors


def load_tailoring_map(path: Path | None = None, *, validate_sources: bool = True) -> dict[str, Any]:
    target = path or default_tailoring_map_path()
    mapping = read_json(target)
    if validate_sources:
        errors = validate_tailoring_map(mapping)
        if errors:
            raise GovernanceError(f"{target}: " + "; ".join(errors))
    return mapping


def _standards_from_route(rule: Any) -> set[str]:
    if isinstance(rule, list):
        return set(rule)
    if isinstance(rule, dict):
        return set(rule.get("minimum", rule.get("adds", [])))
    return set()


def _parse_rfc3339(value: str) -> datetime:
    """Parse a schema-compatible RFC 3339 timestamp for runtime expiry checks."""

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone is required")
    return parsed.astimezone(timezone.utc)


def build_default_first_principles_analysis(
    *,
    objective: str,
    in_scope: Iterable[str],
    out_of_scope: Iterable[str],
    allowed_paths: Iterable[str],
    forbidden_actions: Iterable[str],
    acceptance: Iterable[str],
    plan_steps: Iterable[str],
    plan_verification: Iterable[str],
    open_questions: Iterable[dict[str, Any]],
    authority_references: Iterable[str],
    basis: Iterable[str],
    risk_level: str,
) -> dict[str, Any]:
    """Build an honest minimum analysis when the caller supplies no richer analysis."""

    source_refs = list(dict.fromkeys(
        value for value in [*authority_references, *basis] if isinstance(value, str) and value
    )) or ["task-initiator-input"]
    scope_values = [value for value in in_scope if value]
    exclusions = [value for value in out_of_scope if value]
    paths = [value for value in allowed_paths if value]
    prohibitions = [value for value in forbidden_actions if value]
    criteria = [value for value in acceptance if value]
    steps = [value for value in plan_steps if value]
    verifications = [value for value in plan_verification if value] or criteria
    constraints = [
        {
            "id": "C1",
            "statement": "执行范围仅限：" + "；".join(scope_values),
            "source_refs": source_refs,
        },
        {
            "id": "C2",
            "statement": (
                "执行必须遵守允许路径、排除范围和禁止动作；"
                f"allowed={paths or ['未声明额外路径']}；"
                f"out={exclusions or ['无额外排除']}；"
                f"forbidden={prohibitions or ['无额外禁止动作']}"
            ),
            "source_refs": source_refs,
        },
    ]
    fundamentals = [
        {
            "id": "P1",
            "statement": "任何方案必须直接改变已确认的目标状态，而不是只完成活动清单。",
            "derived_from": ["F1"],
        },
        {
            "id": "P2",
            "statement": "任何方案必须保持已确认的范围、权限和禁止边界。",
            "derived_from": ["C1", "C2"],
        },
    ]
    alternatives = [
        {
            "id": "O0",
            "description": "保持现状，不实施本任务变更",
            "status": "Rejected",
            "derived_from": ["F1"],
            "tradeoffs": ["无新增实施成本", "不能达到已确认目标"],
        },
        {
            "id": "O1",
            "description": "按已确认计划在授权范围内实施并验证",
            "status": "Selected",
            "derived_from": ["P1", "P2"],
            "tradeoffs": ["直接覆盖验收标准", "需要实施与回归验证成本"],
        },
    ]
    if risk_level != "Low":
        alternatives.append(
            {
                "id": "O2",
                "description": "仅实施局部修补并推迟体系性变更",
                "status": "Rejected",
                "derived_from": ["P1", "P2"],
                "tradeoffs": ["短期改动较少", "不能闭合全部目标与长期一致性"],
            }
        )
    decision_criteria = [
        {"id": f"K{position}", "statement": value, "source_refs": source_refs}
        for position, value in enumerate(criteria, 1)
    ]
    criterion_refs = [item["id"] for item in decision_criteria]
    return {
        "method_version": "first-principles-v1",
        "depth": {"Low": "Concise", "Medium": "Standard"}.get(risk_level, "Deep"),
        "outcome": objective.strip(),
        "facts": [
            {
                "id": "F1",
                "statement": "任务发起人已确认目标：" + objective.strip(),
                "evidence_refs": source_refs,
            }
        ],
        "constraints": constraints,
        "assumptions": [],
        "unknowns": [
            {
                "id": f"U{position}",
                "statement": str(item.get("summary")),
                "owner": str(item.get("owner")),
                "resolution_condition": "获得可验证答案并更新 TaskContract",
                "blocking": bool(item.get("blocking")),
            }
            for position, item in enumerate(open_questions, 1)
            if isinstance(item, dict) and item.get("summary") and item.get("owner")
        ],
        "fundamentals": fundamentals,
        "causal_links": [
            {
                "from_ref": "P1",
                "to_ref": "O1",
                "rationale": "选定方案必须产生目标状态变化。",
                "evidence_refs": source_refs,
            },
            {
                "from_ref": "P2",
                "to_ref": "O1",
                "rationale": "选定方案必须在授权边界内可执行。",
                "evidence_refs": source_refs,
            },
        ],
        "alternatives": alternatives,
        "decision_criteria": decision_criteria,
        "selected_approach": "O1",
        "derivation": [
            {
                "plan_step": step,
                "derived_from": ["P1", "P2"],
                "supports": criterion_refs,
            }
            for step in steps
        ],
        "validation_refs": verifications,
        "source_refs": source_refs,
    }


def validate_clarification(clarification: Any) -> list[str]:
    """Report why S1 is not settled yet.

    The clarification loop used to exist only as prose in a command card, so nothing
    could tell a task that skipped it from one that ran it — every record looked the
    same. These rules give the carrier teeth: a skipped round has to say so out loud
    and show the survey it rests on, and an answer the requester left ambiguous keeps
    the task open instead of being quietly resolved by the Agent.
    """

    if not isinstance(clarification, dict):
        return ["clarification is required"]
    errors: list[str] = []
    state = clarification.get("state")
    mode = clarification.get("mode")
    rounds = clarification.get("rounds")
    if not isinstance(rounds, list):
        return ["clarification.rounds must be an array"]
    if mode == "Skipped" and rounds:
        errors.append("clarification.mode=Skipped must not carry rounds")
    if mode == "Asked" and not rounds:
        errors.append("clarification.mode=Asked must carry at least one round")
    if not str(clarification.get("notice", "")).strip():
        errors.append("clarification.notice must record the sentence shown to the requester")
    if not clarification.get("survey_refs"):
        errors.append("clarification.survey_refs must cite the survey the decision rests on")
    ordinals = [item.get("ordinal") for item in rounds if isinstance(item, dict)]
    if ordinals != list(range(1, len(ordinals) + 1)):
        errors.append("clarification.rounds must be numbered from 1 without gaps")
    unresolved = [
        exchange.get("question", "?")
        for item in rounds
        if isinstance(item, dict)
        for exchange in item.get("exchanges", [])
        if isinstance(exchange, dict)
        and exchange.get("answer_state") in {"Ambiguous", "Deferred"}
    ]
    if state == "Settled" and unresolved:
        errors.append(
            "clarification cannot be Settled while answers stay ambiguous or deferred: "
            + "; ".join(unresolved[:3])
        )
    if state != "Settled":
        errors.append("clarification.state must be Settled before the task leaves S1")
    return errors


def validate_first_principles_analysis(
    analysis: Any,
    *,
    risk_level: str,
    plan_steps: Iterable[str],
) -> list[str]:
    """Validate cross-reference and decision invariants not expressible in JSON Schema."""

    if not isinstance(analysis, dict):
        return ["first_principles_analysis is required"]
    errors: list[str] = []
    collections = {
        key: analysis.get(key, [])
        for key in (
            "facts", "constraints", "assumptions", "unknowns", "fundamentals",
            "alternatives", "decision_criteria",
        )
    }
    identifiers: dict[str, str] = {}
    for collection, items in collections.items():
        if not isinstance(items, list):
            errors.append(f"first_principles_analysis.{collection} must be an array")
            continue
        for item in items:
            identifier = item.get("id") if isinstance(item, dict) else None
            if not isinstance(identifier, str) or not identifier:
                errors.append(f"first_principles_analysis.{collection} contains an invalid id")
            elif identifier in identifiers:
                errors.append(f"first_principles_analysis id is duplicated: {identifier}")
            else:
                identifiers[identifier] = collection
    allowed_refs = set(identifiers)
    for item in collections.get("fundamentals", []):
        if isinstance(item, dict):
            unknown = sorted(set(item.get("derived_from", [])) - allowed_refs)
            if unknown:
                errors.append(f"fundamental {item.get('id')} has unknown derived_from: {', '.join(unknown)}")
    for item in analysis.get("causal_links", []):
        if not isinstance(item, dict):
            continue
        for key in ("from_ref", "to_ref"):
            if item.get(key) not in allowed_refs:
                errors.append(f"causal link has unknown {key}: {item.get(key)}")
    for item in collections.get("alternatives", []):
        if isinstance(item, dict):
            unknown = sorted(set(item.get("derived_from", [])) - allowed_refs)
            if unknown:
                errors.append(f"alternative {item.get('id')} has unknown derived_from: {', '.join(unknown)}")
    alternatives = [item for item in collections.get("alternatives", []) if isinstance(item, dict)]
    selected = [item for item in alternatives if item.get("status") == "Selected"]
    if len(selected) != 1 or analysis.get("selected_approach") != selected[0].get("id"):
        errors.append("first_principles_analysis must select exactly one matching alternative")
    status_quo = next((item for item in alternatives if item.get("id") == "O0"), None)
    if status_quo is None or status_quo.get("status") != "Rejected":
        errors.append("first_principles_analysis must compare and explicitly reject O0 status quo")
    if risk_level in {"Medium", "High", "Critical"} and len(alternatives) < 3:
        errors.append(f"{risk_level} analysis requires status quo, selected, and one viable alternative")
    expected_steps = [value for value in plan_steps if value]
    derivation = analysis.get("derivation", [])
    actual_steps = [item.get("plan_step") for item in derivation if isinstance(item, dict)]
    if actual_steps != expected_steps:
        errors.append("first_principles_analysis.derivation must trace every plan step in order")
    fundamental_ids = {item.get("id") for item in collections.get("fundamentals", []) if isinstance(item, dict)}
    criterion_ids = {item.get("id") for item in collections.get("decision_criteria", []) if isinstance(item, dict)}
    for item in derivation if isinstance(derivation, list) else []:
        if not isinstance(item, dict):
            continue
        if not set(item.get("derived_from", [])).issubset(fundamental_ids):
            errors.append(f"plan step has non-fundamental derivation: {item.get('plan_step')}")
        if not set(item.get("supports", [])).issubset(criterion_ids):
            errors.append(f"plan step has unknown decision criterion: {item.get('plan_step')}")
    for item in collections.get("unknowns", []):
        if isinstance(item, dict) and item.get("blocking") is True:
            errors.append(f"blocking first-principles unknown remains open: {item.get('id')}")
    return sorted(set(errors))


def resolve_tailoring(
    task_profile: dict[str, Any],
    *,
    stage: str,
    contract_context: dict[str, Any] | None = None,
    mapping_path: Path | None = None,
    profile_index: Path | None = None,
    meta_mapping: Path | None = None,
) -> dict[str, Any]:
    """Resolve an auditable, deterministic, fail-closed tailoring snapshot."""

    if stage not in TAILORING_STAGES:
        raise GovernanceError(f"unsupported tailoring stage: {stage}")
    mapping = load_tailoring_map(mapping_path)
    routes = mapping["routes"]
    standards: set[str] = set(routes["always_applicable"])
    rule_ids = ["VC-PPG-TAIL-001:always_applicable"]
    scenario = task_profile.get("delivery_scenario")
    if scenario not in DELIVERY_SCENARIOS:
        raise GovernanceError(f"invalid task_profile.delivery_scenario: {scenario!r}")
    standards.update(routes["delivery_scenarios"][scenario])
    rule_ids.append(f"VC-PPG-TAIL-001:delivery_scenarios:{scenario}")
    development_types = task_profile.get("development_types", [])
    if not isinstance(development_types, list) or not development_types or set(development_types) - DEVELOPMENT_TYPES:
        raise GovernanceError("task_profile.development_types is incomplete or invalid")
    for development_type in development_types:
        standards.update(routes["development_types"][development_type])
        rule_ids.append(f"VC-PPG-TAIL-001:development_types:{development_type}")
    type_scopes = task_profile.get("development_type_scopes")
    if not isinstance(type_scopes, dict) or set(type_scopes) != set(development_types):
        raise GovernanceError("task_profile.development_type_scopes must contain exactly the selected development types")
    for development_type, scoped_values in type_scopes.items():
        if not isinstance(scoped_values, list) or not scoped_values or not all(isinstance(value, str) and value for value in scoped_values):
            raise GovernanceError(f"task_profile.development_type_scopes.{development_type} must be a non-empty string array")
    surfaces = task_profile.get("change_surfaces", [])
    if not isinstance(surfaces, list) or not surfaces or set(surfaces) - CHANGE_SURFACES:
        raise GovernanceError("task_profile.change_surfaces is incomplete or invalid")
    extension_route_triggers: dict[str, list[str]] = {f"E{value:02d}": [] for value in range(1, 6)}
    for surface in surfaces:
        routed = set(routes["change_surfaces"][surface])
        standards.update(item for item in routed if not item.startswith("E"))
        for extension in sorted(item for item in routed if item.startswith("E")):
            extension_route_triggers[extension].append(f"surface:{surface}")
        rule_ids.append(f"VC-PPG-TAIL-001:change_surfaces:{surface}")
    risk_level = task_profile.get("risk_level")
    if risk_level not in routes["risk_levels"]:
        raise GovernanceError(f"invalid task_profile.risk_level: {risk_level!r}")
    risk_rule = routes["risk_levels"][risk_level]
    standards.update(risk_rule["minimum"])
    rule_ids.append(f"VC-PPG-TAIL-001:risk_levels:{risk_level}")
    for inheritance in task_profile.get("baseline_inheritance", []):
        if inheritance not in BASELINE_INHERITANCE_STATES:
            raise GovernanceError(f"invalid baseline inheritance: {inheritance!r}")
        standards.update(routes["baseline_inheritance"][inheritance]["adds"])
        rule_ids.append(f"VC-PPG-TAIL-001:baseline_inheritance:{inheritance}")
    if not task_profile.get("baseline_inheritance"):
        raise GovernanceError("task_profile.baseline_inheritance requires at least one controlled value")
    mode = task_profile.get("mode")
    if mode not in routes["execution_modes"]:
        raise GovernanceError(f"invalid task_profile.mode: {mode!r}")
    standards.update(routes["execution_modes"][mode]["adds"])
    rule_ids.append(f"VC-PPG-TAIL-001:execution_modes:{mode}")
    if scenario == "DS-04":
        extension_route_triggers["E05"].append("scenario:DS-04")
        standards.discard("E05")

    facts = task_profile.get("applicability_facts")
    expected_facts = set(mapping["applicability_facts"])
    if not isinstance(facts, dict) or set(facts) != expected_facts:
        raise GovernanceError("task_profile.applicability_facts must contain every VC-PPG-TAIL-001 fact exactly once")
    invalid_fact_values = {key: value for key, value in facts.items() if value not in APPLICABILITY_FACT_VALUES}
    if invalid_fact_values:
        raise GovernanceError(f"invalid applicability fact values: {invalid_fact_values}")
    blocking: list[str] = []
    pending_standards: set[str] = set()
    current_stage = int(stage[1:])
    selected_types = set(development_types)
    for first, second in mapping["multi_type_policy"]["semantic_conflict_pairs"]:
        if {first, second} <= selected_types:
            first_scopes = {value.strip().casefold() for value in type_scopes[first]}
            second_scopes = {value.strip().casefold() for value in type_scopes[second]}
            overlap = sorted(first_scopes & second_scopes)
            if overlap:
                blocking.append(
                    f"semantic-conflict development types {first}/{second} share sub-scope: {', '.join(overlap)}"
                )
    confidence = task_profile.get("confidence")
    if confidence not in mapping["confidence_policy"]:
        raise GovernanceError(f"invalid task_profile.confidence: {confidence!r}")
    confidence_boundary = mapping["confidence_policy"][confidence].get("blocks_from_stage")
    if confidence_boundary and current_stage >= int(confidence_boundary[1:]):
        blocking.append(f"confidence={confidence} blocks {stage}")
    if current_stage >= 2 and contract_context is not None:
        blocking.extend(validate_clarification(contract_context.get("clarification")))
    open_questions = task_profile.get("open_questions", [])
    if not isinstance(open_questions, list):
        raise GovernanceError("task_profile.open_questions must be an array")
    if current_stage >= 4:
        for position, question in enumerate(open_questions):
            if isinstance(question, dict) and question.get("blocking") is True:
                blocking.append(f"open_questions[{position}] is blocking at {stage}")
        if contract_context is not None:
            blocking.extend(
                validate_first_principles_analysis(
                    contract_context.get("first_principles_analysis"),
                    risk_level=str(risk_level),
                    plan_steps=contract_context.get("plan", {}).get("steps", []),
                )
            )
    for fact, value in facts.items():
        fact_rule = mapping["applicability_facts"][fact]
        activates = set(fact_rule["activates"])
        if value == "Yes":
            standards.update(item for item in activates if not item.startswith("E"))
            for extension in sorted(item for item in activates if item.startswith("E")):
                extension_route_triggers[extension].append(f"fact:{fact}=Yes")
            rule_ids.append(f"VC-PPG-TAIL-001:applicability_facts:{fact}=Yes")
        elif value == "Unknown":
            pending_standards.update(activates)
            if current_stage >= int(fact_rule["blocking_from_stage"][1:]):
                blocking.append(f"{fact}=Unknown blocks {stage}")
        required_value = fact_rule.get("required_value_from_stage")
        if required_value and current_stage >= int(fact_rule["blocking_from_stage"][1:]) and value != required_value:
            blocking.append(f"{fact} must be {required_value} at {stage}, found {value}")
    if current_stage >= 4:
        for fact, required_surfaces in mapping["classification_consistency"]["fact_requires_any_surface"].items():
            if facts.get(fact) == "Yes" and not (set(required_surfaces) & set(surfaces)):
                blocking.append(f"{fact}=Yes requires one of change_surfaces: {', '.join(required_surfaces)}")
        for fact, required_types in mapping["classification_consistency"]["fact_requires_any_development_type"].items():
            if facts.get(fact) == "Yes" and not (set(required_types) & set(development_types)):
                blocking.append(f"{fact}=Yes requires one of development_types: {', '.join(required_types)}")

    trigger_states = task_profile.get("extension_triggers")
    expected_extensions = {f"E{value:02d}" for value in range(1, 6)}
    if not isinstance(trigger_states, dict) or set(trigger_states) != expected_extensions:
        raise GovernanceError("task_profile.extension_triggers must contain exactly E01-E05")
    extension_evidence = task_profile.get("extension_evidence_refs")
    if not isinstance(extension_evidence, dict) or set(extension_evidence) != expected_extensions:
        raise GovernanceError("task_profile.extension_evidence_refs must contain exactly E01-E05")
    for extension, refs in extension_evidence.items():
        if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
            raise GovernanceError(f"task_profile.extension_evidence_refs.{extension} must be an array of non-empty strings")
    applicable_extensions: set[str] = set()
    for extension in sorted(expected_extensions):
        state = trigger_states[extension]
        if state not in EXTENSION_STATES:
            raise GovernanceError(f"invalid extension state {extension}={state!r}")
        standard_rule = mapping["standards"][extension]
        fact_values = [facts[key] for key in standard_rule.get("trigger_facts", [])]
        triggers = extension_route_triggers[extension]
        if state in {"Active", "Conditionally Active", "Retiring"}:
            applicable_extensions.add(extension)
            if state == "Retiring" and current_stage >= 4 and not extension_evidence[extension]:
                blocking.append(f"{extension}=Retiring requires extension_evidence_refs")
        elif state in {"Pending", "Not Evaluated"}:
            pending_standards.add(extension)
            if current_stage >= 4:
                blocking.append(f"{extension}={state} blocks {stage}")
        elif state == "Inactive":
            if triggers or any(value != "No" for value in fact_values):
                basis = triggers or [f"fact={value}" for value in fact_values]
                blocking.append(f"{extension}=Inactive conflicts with {', '.join(basis)}")
        elif state == "Retired":
            if current_stage >= 4 and not extension_evidence[extension]:
                blocking.append(f"{extension}=Retired requires extension_evidence_refs")
            if triggers or any(value == "Yes" for value in fact_values):
                blocking.append(f"{extension}=Retired conflicts with a current trigger and requires reactivation or a superseding rule")
        rule_ids.append(f"VC-PPG-TAIL-001:extension_resolution:{extension}:{state}")
    standards.update(applicable_extensions)
    standards.difference_update({f"E{value:02d}" for value in range(1, 6)} - applicable_extensions)

    authority_boundary = int(mapping["authority_policy"]["enforcement_from_stage"][1:])
    if current_stage >= authority_boundary and contract_context is not None:
        authority = contract_context.get("authority", {})
        authority_refs = authority.get("authority_references", []) if isinstance(authority, dict) else []
        authority_assessments = authority.get("authority_assessments", []) if isinstance(authority, dict) else []
        required_gates = set(authority.get("required_gates", [])) if isinstance(authority, dict) else set()
        raw_permissions = authority.get("execution_permissions", []) if isinstance(authority, dict) else []
        execution_permissions = set(raw_permissions) if isinstance(raw_permissions, list) else set()
        if not isinstance(raw_permissions, list) or not execution_permissions or execution_permissions - EXECUTION_PERMISSIONS:
            blocking.append("authority.execution_permissions is incomplete or contains uncontrolled values")
        required_permissions: set[str] = set()
        required_permissions.update(
            mapping["authority_policy"]["run_event_permission_requirements"].get("run_started", [])
        )
        for fact, permissions in mapping["authority_policy"]["fact_permission_requirements"].items():
            if facts.get(fact) == "Yes":
                required_permissions.update(permissions)
        missing_permissions = sorted(required_permissions - execution_permissions)
        if missing_permissions:
            blocking.append(f"required execution permissions are missing: {', '.join(missing_permissions)}")
        if facts.get("authority_available") == "Yes" and not authority_refs:
            blocking.append("authority_available=Yes requires at least one authority reference")
        required_gate_tokens = set(mapping["gate_requirements"]["risk_levels"].get(risk_level, []))
        for fact, tokens in mapping["gate_requirements"]["applicability_facts"].items():
            if facts.get(fact) == "Yes":
                required_gate_tokens.update(tokens)
        missing_gates = sorted(required_gate_tokens - required_gates)
        if missing_gates:
            blocking.append(f"required gates are missing: {', '.join(missing_gates)}")
        blocked_by = contract_context.get("blocked_by", [])
        if blocked_by:
            blocking.append("task is blocked_by: " + ", ".join(str(item) for item in blocked_by))
        scope = contract_context.get("scope", {})
        raw_in_scope = scope.get("in_scope", []) if isinstance(scope, dict) else []
        in_scope_values = {str(item).strip().casefold() for item in raw_in_scope}
        unresolved_type_scopes = sorted(
            value
            for values in type_scopes.values()
            for value in values
            if value.strip().casefold() not in in_scope_values
        )
        if unresolved_type_scopes:
            blocking.append(
                "development_type_scopes must reference exact scope.in_scope values: "
                + ", ".join(unresolved_type_scopes)
            )
        if not isinstance(authority_assessments, list):
            blocking.append("authority.authority_assessments must be an array")
            authority_assessments = []
        assessment_by_ref: dict[str, dict[str, Any]] = {}
        duplicate_assessment_refs: set[str] = set()
        for assessment in authority_assessments:
            if not isinstance(assessment, dict) or not isinstance(assessment.get("reference"), str):
                blocking.append("each authority assessment requires a string reference")
                continue
            reference = assessment["reference"]
            if reference in assessment_by_ref:
                duplicate_assessment_refs.add(reference)
            assessment_by_ref[reference] = assessment
        if duplicate_assessment_refs:
            blocking.append("duplicate authority assessments: " + ", ".join(sorted(duplicate_assessment_refs)))
        unbound_assessments = sorted(set(assessment_by_ref) - set(authority_refs))
        if unbound_assessments:
            blocking.append("authority assessments are not bound to authority_references: " + ", ".join(unbound_assessments))
        if facts.get("authority_available") == "Yes":
            missing_assessments = sorted(set(authority_refs) - set(assessment_by_ref))
            if missing_assessments:
                blocking.append("authority references lack structured assessments: " + ", ".join(missing_assessments))
            valid_scope_refs: set[str] = set()
            valid_references: set[str] = set()
            verification_now = datetime.now(timezone.utc)
            for reference in authority_refs:
                assessment = assessment_by_ref.get(reference)
                if assessment is None:
                    continue
                if assessment.get("status") != mapping["authority_policy"]["executable_state"]:
                    blocking.append(
                        f"authority assessment is not {mapping['authority_policy']['executable_state']}: "
                        f"{reference}={assessment.get('status')}"
                    )
                    continue
                verified_at = assessment.get("verified_at")
                try:
                    verified_time = _parse_rfc3339(str(verified_at))
                except ValueError:
                    blocking.append(f"authority assessment has invalid verified_at: {reference}")
                    continue
                if verified_time > verification_now:
                    blocking.append(f"authority assessment verified_at is in the future: {reference}")
                    continue
                expires_at = assessment.get("expires_at")
                if expires_at is not None:
                    try:
                        expiry_time = _parse_rfc3339(str(expires_at))
                        if expiry_time <= verified_time:
                            blocking.append(f"authority assessment expires_at is not after verified_at: {reference}")
                            continue
                        if expiry_time <= verification_now:
                            blocking.append(f"authority assessment expired: {reference}")
                            continue
                    except ValueError:
                        blocking.append(f"authority assessment has invalid expires_at: {reference}")
                        continue
                evidence_refs = assessment.get("evidence_refs")
                scope_refs = assessment.get("scope_refs")
                if not isinstance(evidence_refs, list) or not evidence_refs:
                    blocking.append(f"authority assessment lacks evidence_refs: {reference}")
                    continue
                if not isinstance(scope_refs, list) or not scope_refs:
                    blocking.append(f"authority assessment lacks scope_refs: {reference}")
                    continue
                valid_references.add(reference)
                valid_scope_refs.update(str(item).strip().casefold() for item in scope_refs)
            if authority_refs and not valid_references:
                blocking.append("no valid authority assessment covers execution")
            unresolved_authority_scope = sorted(value for value in valid_scope_refs if value not in in_scope_values)
            if unresolved_authority_scope:
                blocking.append(
                    "authority assessment scope_refs must reference exact scope.in_scope values: "
                    + ", ".join(unresolved_authority_scope)
                )
            uncovered_scope = sorted(value for value in in_scope_values if value not in valid_scope_refs)
            if uncovered_scope:
                blocking.append("valid authority assessments do not cover scope.in_scope: " + ", ".join(uncovered_scope))

    stage_rule = mapping["stage_context"][stage]
    stage_standards = (standards & set(stage_rule["minimum_standards"])) | applicable_extensions
    stage_standards.update(standards & set(stage_rule["conditional_standards"]))
    source_by_id = {item["id"]: item for item in mapping["source_catalog"]}
    source_sections = [
        {"source_id": source_id, "path": source_by_id[source_id]["path"], "sections": sections}
        for source_id, sections in (
            ("VC-PPG-COM-001", ["2", "10", "12"]),
            ("VC-PPG-COM-002", ["2", "3", "4", "22", "23"]),
            ("VC-PPG-DEC-001", ["9", "10", "11", "12", "13", "14", "15", "16", "17"]),
            ("VC-PPG-PRO-001", stage_rule["global_sections"]),
            ("VC-PPG-IDX-001", ["2", "3", "4", "9"]),
        )
    ]
    source_sections.extend(
        {
            "source_id": standard,
            "path": source_by_id[standard]["path"],
            "sections": mapping["standards"][standard]["source_sections"],
        }
        for standard in sorted(standards | pending_standards)
    )
    complete_source_ids = {
        "VC-PPG-COM-001",
        "VC-PPG-COM-002",
        "VC-PPG-DEC-001",
        "VC-PPG-PRO-001",
        "VC-PPG-IDX-001",
        *standards,
        *pending_standards,
    }
    complete_source_files = [
        {
            "source_id": source["id"],
            "path": source["path"],
            "sha256": hashlib.sha256(runtime_asset_path(source["path"]).read_bytes()).hexdigest(),
        }
        for source in mapping["source_catalog"]
        if source["id"] in complete_source_ids
    ]
    profiles = resolve_all_profiles(profile_index or default_profile_index_path(), meta_mapping)
    applicable_profiles = sorted(
        item["legacy_kind"] for item in profiles if item["owner_standard"] in standards
    )
    profile_digest = hashlib.sha256("\n".join(applicable_profiles).encode("utf-8")).hexdigest()
    digest_input: dict[str, Any] = {"task_profile": task_profile}
    if contract_context is not None:
        digest_input.update(
            {
                key: contract_context.get(key)
                for key in (
                    "objective", "scope", "authority", "acceptance", "plan",
                    "first_principles_analysis", "source_snapshot", "depends_on",
                    "supersedes", "blocked_by",
                )
            }
        )
    input_digest = hashlib.sha256(
        json.dumps(digest_input, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    rule_set_path = mapping_path or default_tailoring_map_path()
    normative_digest = hashlib.sha256()
    for source in sorted(mapping["source_catalog"], key=lambda item: item["id"]):
        source_path = runtime_asset_path(source["path"])
        normative_digest.update(source["id"].encode("utf-8"))
        normative_digest.update(hashlib.sha256(source_path.read_bytes()).digest())
    normative_digest.update(hashlib.sha256((meta_mapping or default_mapping_path()).read_bytes()).digest())
    return {
        "rule_set_id": mapping["document_id"],
        "rule_set_version": mapping["version"],
        "rule_set_status": mapping["status"],
        "rule_set_sha256": hashlib.sha256(rule_set_path.read_bytes()).hexdigest(),
        "normative_sources_sha256": normative_digest.hexdigest(),
        "resolver_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest(),
        "task_contract_schema_sha256": hashlib.sha256(schema_path("task-before.schema.json").read_bytes()).hexdigest(),
        "input_digest": input_digest,
        "stage": stage,
        "applicable_standards": sorted(standards),
        "pending_standards": sorted(pending_standards - standards),
        "stage_context_standards": sorted(stage_standards),
        "control_strength": risk_rule["control_strength"],
        "independent_review": bool(risk_rule.get("independent_review")),
        "explicit_human_gate": bool(risk_rule.get("explicit_human_gate")),
        "blocking_reasons": sorted(set(blocking)),
        "rule_ids": sorted(set(rule_ids)),
        "source_sections": source_sections,
        "complete_source_files": complete_source_files,
        "profile_coverage_digest": {
            "applicable": len(applicable_profiles),
            "total": len(profiles),
            "sha256": profile_digest,
        },
    }


def validate_tailoring_resolution(before: dict[str, Any]) -> list[str]:
    profile = before.get("task_profile")
    stored = before.get("tailoring_resolution")
    if not isinstance(profile, dict):
        return ["before.task_profile must be an object"]
    if not isinstance(stored, dict):
        return ["before.tailoring_resolution must be an object"]
    stage = stored.get("stage")
    try:
        expected = resolve_tailoring(profile, stage=stage, contract_context=before)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return [f"cannot resolve tailoring: {exc}"]
    return [] if stored == expected else ["before.tailoring_resolution is stale or differs from VC-PPG-TAIL-001"]


def validate_historical_tailoring_sources(before: dict[str, Any]) -> list[str]:
    """Validate frozen identities without coupling terminal history to the current release."""

    stored = before.get("tailoring_resolution")
    if not isinstance(stored, dict):
        return ["before.tailoring_resolution must be an object"]
    sources = stored.get("complete_source_files")
    if not isinstance(sources, list) or not sources:
        return ["before.tailoring_resolution.complete_source_files must be a non-empty array"]
    errors: list[str] = []
    seen: set[str] = set()
    for position, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"before.tailoring_resolution.complete_source_files[{position}] must be an object")
            continue
        source_id = source.get("source_id")
        logical_path = source.get("path")
        expected_hash = source.get("sha256")
        if not all(isinstance(value, str) and value for value in (source_id, logical_path, expected_hash)):
            errors.append(
                f"before.tailoring_resolution.complete_source_files[{position}] requires source_id, path, and sha256"
            )
            continue
        if source_id in seen:
            errors.append(f"historical tailoring sources contain duplicate source_id: {source_id}")
        seen.add(source_id)
        if not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
            errors.append(f"historical tailoring source sha256 is invalid: {source_id}")
            continue
        parts = logical_path.split("/")
        if (
            "\\" in logical_path
            or not parts
            or parts[0] != "references"
            or any(part in {"", ".", ".."} for part in parts)
        ):
            errors.append(
                f"historical tailoring source path must be a safe canonical references/ path: {source_id}"
            )
    return errors


def resolve_meta_type(legacy_kind: str, mapping: dict[str, Any]) -> str:
    for meta_type, codes in mapping["overrides"].items():
        if legacy_kind in codes:
            return meta_type
    return mapping["default_meta_type"]


def parse_profile_index(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    section = re.search(
        r"^## 4\.\s+全量(?:产物|领域\s+Profile)\s*归属索引\s*$"
        r"(?P<body>.*?)"
        r"^## 5\.\s+",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section:
        raise GovernanceError(f"{path}: cannot locate the full profile ownership section")
    rows = re.findall(
        r"^\|\s*([A-Z][A-Z0-9]{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([A-Z]+)\s*\|",
        section.group("body"),
        flags=re.MULTILINE,
    )
    profiles = [
        {
            "legacy_kind": code,
            "name": name.strip(),
            "owner_standard": owner.strip(),
            "legacy_state_model": state,
        }
        for code, name, owner, state in rows
    ]
    codes = [item["legacy_kind"] for item in profiles]
    if len(codes) != len(set(codes)):
        raise GovernanceError(f"{path}: duplicate legacy profile codes")
    return profiles


def resolve_all_profiles(
    index_path: Path, mapping_path: Path | None = None
) -> list[dict[str, str]]:
    mapping = load_mapping(mapping_path)
    profiles = parse_profile_index(index_path)
    expected = mapping.get("expected_legacy_profile_count")
    if len(profiles) != expected:
        raise GovernanceError(
            f"{index_path}: expected {expected} legacy profiles, found {len(profiles)}"
        )
    known = {item["legacy_kind"] for item in profiles}
    overrides = {
        code
        for codes in mapping["overrides"].values()
        for code in codes
    }
    unknown = sorted(overrides - known)
    if unknown:
        raise GovernanceError(f"mapping contains unknown legacy profiles: {unknown}")
    for item in profiles:
        item["meta_type"] = resolve_meta_type(item["legacy_kind"], mapping)
    return profiles


def validate_artifact_manifest(
    manifest: Any, *, terminal: bool, before_manifest: list[dict[str, Any]] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, list):
        return ["artifact_manifest must be an array"]
    asset_ids: list[str] = [
        item["asset_id"] for item in manifest
        if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
    ]
    if len(asset_ids) != len(set(asset_ids)):
        errors.append("artifact_manifest.asset_id values must be unique")
    try:
        mapping = load_mapping()
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        errors.append(f"artifact_manifest mapping is unavailable: {exc}")
        mapping = None
    for position, item in enumerate(manifest):
        if not isinstance(item, dict):
            continue
        legacy_kind = item.get("legacy_kind")
        if legacy_kind is not None:
            if not isinstance(legacy_kind, str) or not PROFILE_RE.fullmatch(legacy_kind):
                errors.append(f"artifact_manifest[{position}].legacy_kind is invalid")
            elif mapping is not None and resolve_meta_type(legacy_kind, mapping) != item.get("meta_type"):
                errors.append(
                    f"artifact_manifest[{position}] meta_type does not match legacy_kind {legacy_kind}"
                )
    mandatory = {"TaskContract", "RunLedger", "TaskOutcome"}
    present = {
        item["meta_type"] for item in manifest
        if isinstance(item, dict) and isinstance(item.get("meta_type"), str)
    }
    missing = sorted(mandatory - present)
    if missing:
        errors.append(f"artifact_manifest is missing mandatory task meta types: {missing}")
    if terminal:
        if before_manifest is not None:
            planned_by_id = {
                item["asset_id"]: item for item in before_manifest
                if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
            }
            planned_ids = set(planned_by_id)
            terminal_ids = set(asset_ids)
            missing_planned = sorted(planned_ids - terminal_ids)
            if missing_planned:
                errors.append(
                    "terminal artifact_manifest cannot remove frozen planned assets: "
                    f"{missing_planned}"
                )
            terminal_by_id = {
                item["asset_id"]: item for item in manifest
                if isinstance(item, dict) and isinstance(item.get("asset_id"), str)
            }
            for asset_id in sorted(planned_ids & terminal_ids):
                planned = planned_by_id[asset_id]
                actual = terminal_by_id[asset_id]
                comparable = {key: value for key, value in actual.items() if key != "outcome"}
                if comparable != planned:
                    errors.append(
                        f"terminal artifact_manifest asset {asset_id} changed frozen planning fields"
                    )
            actual_outcomes = {"Created", "Revised", "Referenced", "Generated"}
            for asset_id in sorted(terminal_ids - planned_ids):
                if terminal_by_id[asset_id].get("outcome") not in actual_outcomes:
                    errors.append(
                        f"unplanned terminal asset {asset_id} requires an actual outcome"
                    )
        for position, item in enumerate(manifest):
            if isinstance(item, dict) and "outcome" not in item:
                errors.append(f"artifact_manifest[{position}].outcome is required at task close")
    return errors


def require_record_semantics(path: Path, document: dict[str, Any]) -> None:
    """Reject amendments that satisfy JSON shape but violate task semantics."""

    errors: list[str] = []
    if document.get("meta_type") == "TaskContract":
        errors.extend(validate_artifact_manifest(document.get("artifact_manifest"), terminal=False))
        profile = document.get("task_profile", {})
        if isinstance(profile, dict):
            if profile.get("primary_development_type") not in profile.get("development_types", []):
                errors.append("primary_development_type must be included in development_types")
        errors.extend(validate_tailoring_resolution(document))
    elif document.get("meta_type") == "TaskOutcome":
        before_path = path.parent / "before.json"
        if not before_path.is_file():
            errors.append(f"TaskOutcome amendment requires sibling {before_path.name}")
        else:
            before = read_json(before_path)
            errors.extend(
                validate_artifact_manifest(
                    document.get("artifact_manifest"),
                    terminal=True,
                    before_manifest=before.get("artifact_manifest"),
                )
            )
    if errors:
        raise GovernanceError("; ".join(errors))


def initialize_task(
    project_root: Path,
    *,
    project_id: str,
    work_item_id: str,
    task_id: str,
    ordinal: int,
    objective: str,
    request_snapshot: dict[str, str] | None = None,
    clarification: dict[str, Any] | None = None,
    acceptance: Iterable[str],
    development_types: Iterable[str],
    change_surfaces: Iterable[str],
    in_scope: Iterable[str] = (),
    out_of_scope: Iterable[str] = (),
    allowed_paths: Iterable[str] = (),
    forbidden_actions: Iterable[str] = (),
    depends_on: Iterable[str] = (),
    supersedes: Iterable[str] = (),
    risk_level: str = "Medium",
    mode: str = "Normal",
    delivery_scenario: str = "DS-03",
    primary_development_type: str | None = None,
    development_type_scopes: dict[str, list[str]] | None = None,
    extension_triggers: dict[str, str] | None = None,
    extension_evidence_refs: dict[str, list[str]] | None = None,
    applicability_facts: dict[str, str] | None = None,
    tailoring_stage: str = "S1",
    baseline_inheritance: Iterable[str] = (),
    confidence: str = "Medium",
    basis: Iterable[str] = ("task-initiator-input",),
    open_questions: Iterable[dict[str, Any]] = (),
    execution_permissions: Iterable[str] = ("read", "edit-in-scope", "validate"),
    required_gates: Iterable[str] = (),
    stop_conditions: Iterable[str] = ("scope-expansion", "authority-conflict", "critical-evidence-missing"),
    authority_references: Iterable[str] = (),
    authority_assessments: Iterable[dict[str, Any]] = (),
    plan_steps: Iterable[str] = ("inspect", "change", "validate", "close"),
    plan_verification: Iterable[str] = (),
    rollback: Iterable[str] = ("revert only changes owned by this task",),
    artifact_manifest: Iterable[dict[str, Any]] = (),
    source_snapshot: dict[str, Any] | None = None,
    first_principles_analysis: dict[str, Any] | None = None,
    upgrade_minimal_reason: str | None = None,
    upgrade_minimal_basis: str | None = None,
) -> Path:
    ensure_skill_integrity()
    require_id(project_id, "project_id")
    require_id(work_item_id, "work_item_id")
    require_id(task_id, "task_id")
    if ordinal < 1:
        raise GovernanceError("ordinal must be at least 1")
    criteria = [value for value in acceptance if value]
    scope_in = [value for value in in_scope if value]
    scope_out = [value for value in out_of_scope if value]
    allowed = [value for value in allowed_paths if value]
    forbidden = [value for value in forbidden_actions if value]
    basis_values = [value for value in basis if value]
    question_values = list(open_questions)
    authority_ref_values = [value for value in authority_references if value]
    authority_assessment_values = list(authority_assessments)
    plan_step_values = [value for value in plan_steps if value]
    verification_values = [value for value in plan_verification if value]
    rollback_values = [value for value in rollback if value]
    dev_types = list(dict.fromkeys(value for value in development_types if value))
    surfaces = list(dict.fromkeys(value for value in change_surfaces if value))
    inheritance = list(dict.fromkeys(value for value in baseline_inheritance if value))
    permissions = list(dict.fromkeys(value for value in execution_permissions if value))
    if not objective.strip() or not criteria:
        raise GovernanceError("objective and at least one acceptance criterion are required")
    if not dev_types or not surfaces:
        raise GovernanceError("at least one development type and one change surface are required")
    if delivery_scenario not in DELIVERY_SCENARIOS:
        raise GovernanceError(f"unsupported delivery scenario: {delivery_scenario}")
    invalid_development_types = sorted(set(dev_types) - DEVELOPMENT_TYPES)
    if invalid_development_types:
        raise GovernanceError(f"unsupported development types: {invalid_development_types}")
    invalid_surfaces = sorted(set(surfaces) - CHANGE_SURFACES)
    if invalid_surfaces:
        raise GovernanceError(f"unsupported change surfaces: {invalid_surfaces}")
    invalid_inheritance = sorted(set(inheritance) - BASELINE_INHERITANCE_STATES)
    if invalid_inheritance:
        raise GovernanceError(f"unsupported baseline inheritance values: {invalid_inheritance}")
    if not inheritance:
        raise GovernanceError("at least one baseline inheritance value is required")
    invalid_permissions = sorted(set(permissions) - EXECUTION_PERMISSIONS)
    if invalid_permissions or not permissions:
        raise GovernanceError(f"execution_permissions must use controlled values: {sorted(EXECUTION_PERMISSIONS)}")
    primary = primary_development_type or dev_types[0]
    if primary not in dev_types:
        raise GovernanceError("primary_development_type must be included in development_types")
    if development_type_scopes is None:
        if len(dev_types) > 1:
            raise GovernanceError("multiple development types require development_type_scopes for every selected type")
        type_scopes = {dev_types[0]: list(scope_in)}
    else:
        type_scopes = {
            key: list(dict.fromkeys(value for value in values if value))
            for key, values in development_type_scopes.items()
        }
    if set(type_scopes) != set(dev_types) or any(not values for values in type_scopes.values()):
        raise GovernanceError("development_type_scopes must contain every selected development type exactly once with a non-empty scope array")
    normalized_scope = {value.strip().casefold() for value in scope_in}
    if any(
        value.strip().casefold() not in normalized_scope
        for values in type_scopes.values()
        for value in values
    ):
        raise GovernanceError("development_type_scopes values must exactly reference scope.in_scope values")
    triggers = {key: "Not Evaluated" for key in ("E01", "E02", "E03", "E04", "E05")}
    if extension_triggers:
        unknown = sorted(set(extension_triggers) - set(triggers))
        if unknown:
            raise GovernanceError(f"unknown extension triggers: {unknown}")
        triggers.update(extension_triggers)
    invalid_triggers = {key: value for key, value in triggers.items() if value not in EXTENSION_STATES}
    if invalid_triggers:
        raise GovernanceError(f"invalid extension trigger states: {invalid_triggers}")
    extension_evidence = {key: [] for key in triggers}
    if extension_evidence_refs:
        unknown_evidence_keys = sorted(set(extension_evidence_refs) - set(extension_evidence))
        if unknown_evidence_keys:
            raise GovernanceError(f"unknown extension evidence keys: {unknown_evidence_keys}")
        for key, refs in extension_evidence_refs.items():
            if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
                raise GovernanceError(f"extension evidence {key} must be an array of non-empty strings")
            extension_evidence[key] = list(dict.fromkeys(refs))
    tailoring_map = load_tailoring_map()
    facts = {key: "Unknown" for key in tailoring_map["applicability_facts"]}
    if applicability_facts:
        unknown_facts = sorted(set(applicability_facts) - set(facts))
        if unknown_facts:
            raise GovernanceError(f"unknown applicability facts: {unknown_facts}")
        facts.update(applicability_facts)
    invalid_facts = {key: value for key, value in facts.items() if value not in APPLICABILITY_FACT_VALUES}
    if invalid_facts:
        raise GovernanceError(f"invalid applicability fact values: {invalid_facts}")
    task_dir = task_directory(project_root, task_id)
    before_path = task_dir / "before.json"
    if before_path.exists():
        raise GovernanceError(f"task already exists: {before_path}")
    minimal_path = task_dir / "task-record.json"
    upgraded_minimal: dict[str, Any] | None = None
    minimal_history_path = task_dir / "history" / "task-record.minimal-v1.json"
    if minimal_path.exists():
        if not upgrade_minimal_reason or not upgrade_minimal_basis:
            raise GovernanceError(
                "task already uses the Minimal carrier; pass both "
                "--upgrade-minimal-reason and --upgrade-minimal-basis for a one-way upgrade"
            )
        if minimal_history_path.exists():
            raise GovernanceError(f"Minimal history target already exists: {minimal_history_path}")
        from minimal_task import (
            mark_minimal_upgrade,
            minimal_record_sha256,
            require_valid_minimal_record,
        )

        current_minimal = read_json(minimal_path)
        require_valid_minimal_record(current_minimal, task_dir=task_dir)
        for key, expected in (
            ("project_id", project_id),
            ("work_item_id", work_item_id),
            ("task_id", task_id),
            ("ordinal", ordinal),
        ):
            if current_minimal.get(key) != expected:
                raise GovernanceError(f"Minimal upgrade {key} does not match the full TaskContract")
        upgraded_minimal = mark_minimal_upgrade(
            task_dir,
            reason=upgrade_minimal_reason,
            basis=upgrade_minimal_basis,
            full_carrier_ref=f".project-governance/tasks/{task_id}/before.json",
        )
    elif upgrade_minimal_reason or upgrade_minimal_basis:
        raise GovernanceError("Minimal upgrade arguments require an existing task-record.json")
    snapshot = dict(source_snapshot or capture_source_snapshot(project_root))
    if upgraded_minimal is not None:
        snapshot["minimal_upgrade"] = {
            "history_ref": f".project-governance/tasks/{task_id}/history/task-record.minimal-v1.json",
            "reason": upgrade_minimal_reason,
            "basis": upgrade_minimal_basis,
            "record_sha256": minimal_record_sha256(upgraded_minimal),
        }
    manifest = list(artifact_manifest)
    snapshot_ref = str(snapshot.get("head") or snapshot.get("status_digest") or snapshot.get("captured_at"))
    if not manifest:
        manifest = [
            {
                "meta_type": meta_type,
                "legacy_kind": None,
                "action": "Create/Revise",
                "asset_id": f"{task_id}-{suffix}",
                "content_ref": f".project-governance/tasks/{task_id}/{filename}",
                "reason": reason,
                "rule_reference": rule,
                "owner": "task-initiator" if meta_type != "RunLedger" else "execution-agent",
                "source_snapshot": snapshot_ref,
                "human_confirmation_refs": [],
            }
            for meta_type, suffix, filename, reason, rule in (
                ("TaskContract", "before", "before.json", "freeze execution input", "VC-PPG-PRO-001 §8.1"),
                ("RunLedger", "run", "run.jsonl", "record material execution events", "VC-PPG-PRO-001 §8.2"),
                ("TaskOutcome", "after", "after.json", "record terminal facts and residue", "VC-PPG-PRO-001 §8.3"),
            )
        ]
    verification_plan = verification_values or criteria
    if not request_snapshot:
        raise GovernanceError(
            "request_snapshot is required: the requester's own words are the acceptance baseline"
        )
    # Omitting the record must fail closed rather than look like a clean skip, so the
    # default is a well-formed but unsettled carrier that blocks from S2 onward.
    clarification_value = clarification or {
        "state": "Open",
        "mode": "Asked",
        "notice": "clarification was not recorded by the caller",
        "survey_refs": ["none-recorded"],
        "rounds": [],
        "basis": "init_task was called without a clarification record; S1 is unsettled",
    }
    analysis = first_principles_analysis or build_default_first_principles_analysis(
        objective=objective,
        in_scope=scope_in,
        out_of_scope=scope_out,
        allowed_paths=allowed,
        forbidden_actions=forbidden,
        acceptance=criteria,
        plan_steps=plan_step_values,
        plan_verification=verification_plan,
        open_questions=question_values,
        authority_references=authority_ref_values,
        basis=basis_values,
        risk_level=risk_level,
    )
    before = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "TaskContract",
        "project_id": project_id,
        "work_item_id": work_item_id,
        "task_id": task_id,
        "ordinal": ordinal,
        "revision": 1,
        "lifecycle_state": "Ready",
        "created_at": now_utc(),
        "frozen_at": None,
        "objective": objective.strip(),
        "request_snapshot": request_snapshot,
        "clarification": clarification_value,
        "depends_on": sorted(set(depends_on)),
        "supersedes": sorted(set(supersedes)),
        "blocked_by": [],
        "source_snapshot": snapshot,
        "scope": {
            "in_scope": scope_in,
            "out_of_scope": scope_out,
            "allowed_paths": allowed,
            "forbidden_actions": forbidden,
        },
        "authority": {
            "execution_permissions": permissions,
            "required_gates": [value for value in required_gates if value],
            "stop_conditions": [value for value in stop_conditions if value],
            "authority_references": authority_ref_values,
            "authority_assessments": authority_assessment_values,
        },
        "acceptance": {"criteria": criteria, "decision_owner": "task-initiator"},
        "plan": {
            "steps": plan_step_values,
            "verification": verification_plan,
            "rollback": rollback_values,
        },
        "first_principles_analysis": analysis,
        "task_profile": {
            "delivery_scenario": delivery_scenario,
            "development_types": dev_types,
            "primary_development_type": primary,
            "development_type_scopes": type_scopes,
            "change_surfaces": surfaces,
            "risk_level": risk_level,
            "extension_triggers": triggers,
            "extension_evidence_refs": extension_evidence,
            "baseline_inheritance": inheritance,
            "mode": mode,
            "confidence": confidence,
            "basis": basis_values,
            "open_questions": question_values,
            "applicability_facts": facts,
        },
        "artifact_manifest": manifest,
        "amendments": [],
    }
    before["tailoring_resolution"] = resolve_tailoring(
        before["task_profile"], stage=tailoring_stage, contract_context=before
    )
    require_valid_json_document(before, "task-before.schema.json", "before")
    manifest_errors = validate_artifact_manifest(before["artifact_manifest"], terminal=False)
    if manifest_errors:
        raise GovernanceError("; ".join(manifest_errors))
    from manage_project_docs import initialize_project_document_layout

    initialize_project_document_layout(project_root)
    task_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = task_dir / "run.jsonl"
    if upgraded_minimal is None:
        atomic_write_json(before_path, before)
        ledger_path.touch(exist_ok=False)
    else:
        minimal_history_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(minimal_path, upgraded_minimal)
        os.replace(minimal_path, minimal_history_path)
        try:
            atomic_write_json(before_path, before)
            ledger_path.touch(exist_ok=False)
        except BaseException:
            before_path.unlink(missing_ok=True)
            ledger_path.unlink(missing_ok=True)
            os.replace(minimal_history_path, minimal_path)
            raise
    from manage_project_docs import refresh_project_readmes

    refresh_project_readmes(project_root)
    return task_dir


def register_authority_asset(
    project_root: Path,
    *,
    project_id: str,
    asset_id: str,
    legacy_kind: str,
    title: str,
    owner: str,
    state: str,
    revision: str,
    content_ref: str,
    native_format: str | None = None,
    source: Iterable[str] = (),
    scope: Iterable[str] = (),
    trace_refs: Iterable[str] = (),
    access_classification: str = "internal",
    retention_rule: str = "follow-source-asset",
    history_ref: str = "git-history",
    profile_fields: dict[str, Any] | None = None,
    mapping_path: Path | None = None,
    profile_index: Path | None = None,
) -> Path:
    """Register a native long-lived asset without copying or rewriting its content."""

    ensure_skill_integrity()
    require_id(project_id, "project_id")
    require_id(asset_id, "asset_id")
    if not PROFILE_RE.fullmatch(legacy_kind):
        raise GovernanceError(f"invalid legacy profile code: {legacy_kind!r}")
    mapping = load_mapping(mapping_path)
    resolved_type = resolve_meta_type(legacy_kind, mapping)
    if resolved_type != "AuthorityAsset":
        raise GovernanceError(
            f"{legacy_kind} resolves to {resolved_type}, not AuthorityAsset"
        )
    profiles = {item["legacy_kind"]: item for item in resolve_all_profiles(profile_index or default_profile_index_path(), mapping_path)}
    if legacy_kind not in profiles:
        raise GovernanceError(f"legacy profile is not present in the ownership index: {legacy_kind}")
    state_model = profiles[legacy_kind]["legacy_state_model"]
    if state not in STATE_MODELS[state_model]:
        raise GovernanceError(
            f"state {state!r} is invalid for {legacy_kind} ({state_model}); "
            f"allowed: {sorted(STATE_MODELS[state_model])}"
        )
    required_text = {
        "title": title,
        "owner": owner,
        "state": state,
        "revision": revision,
        "content_ref": content_ref,
    }
    for label, value in required_text.items():
        if not value.strip():
            raise GovernanceError(f"{label} is required")
    fields = profile_fields or {}
    if not fields:
        raise GovernanceError("profile_fields must contain profile-specific validation facts")
    sources = [value for value in source if value]
    scopes = [value for value in scope if value]
    if not sources or not scopes:
        raise GovernanceError("source and scope must each contain at least one entry")
    ref = content_ref.strip()
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", ref) and not ref.startswith("external:"):
        local_ref = Path(ref)
        local_target = local_ref if local_ref.is_absolute() else project_root.resolve() / local_ref
        if not local_target.is_file():
            raise GovernanceError(f"local content_ref does not exist: {local_target}")
    inferred_format = native_format
    if not inferred_format:
        suffix = Path(content_ref).suffix.lstrip(".").lower()
        inferred_format = suffix or "external"
    target = governance_root(project_root) / "authority" / f"{asset_id}.json"
    if target.exists():
        raise GovernanceError(f"authority asset already exists: {target}")
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "AuthorityAsset",
        "project_id": project_id,
        "asset_id": asset_id,
        "legacy_kind": legacy_kind,
        "profile_state_model": state_model,
        "title": title.strip(),
        "owner": owner.strip(),
        "state": state.strip(),
        "revision": revision.strip(),
        "source": sources,
        "scope": scopes,
        "trace_links": [
            {"relation": "references", "target": value}
            for value in trace_refs
            if value
        ],
        "native_format": inferred_format,
        "content_ref": content_ref.strip(),
        "access_classification": access_classification,
        "retention_rule": retention_rule,
        "history_ref": history_ref,
        "profile_fields": fields,
    }
    require_valid_json_document(envelope, "authority-asset.schema.json", "authority")
    atomic_write_json(target, envelope)
    return target


def _set_dotted_path(
    document: dict[str, Any], dotted_path: str, new_value: Any, *, allow_add: bool = False
) -> Any:
    parts = [part for part in dotted_path.split(".") if part]
    if not parts or parts[0] in IMMUTABLE_FIELDS:
        raise GovernanceError(f"field cannot be amended: {dotted_path}")
    owner: dict[str, Any] = document
    for part in parts[:-1]:
        child = owner.get(part)
        if not isinstance(child, dict):
            raise GovernanceError(f"path does not resolve to an object: {dotted_path}")
        owner = child
    final = parts[-1]
    if final not in owner and not allow_add:
        raise GovernanceError(f"field does not exist: {dotted_path}")
    old_value = owner[final] if final in owner else {"$missing": True}
    owner[final] = new_value
    return old_value


def _refresh_tailoring_after_amendment(
    document: dict[str, Any],
    amendments: list[dict[str, Any]],
    *,
    reason: str,
    basis: str,
) -> None:
    if document.get("meta_type") != "TaskContract":
        return
    profile = document.get("task_profile")
    stored = document.get("tailoring_resolution")
    if not isinstance(profile, dict) or not isinstance(stored, dict):
        return
    stage = stored.get("stage")
    expected = resolve_tailoring(profile, stage=stage, contract_context=document)
    if stored == expected:
        return
    from_revision = document["revision"]
    document["tailoring_resolution"] = expected
    document["revision"] = from_revision + 1
    amendments.append(
        {
            "from_revision": from_revision,
            "to_revision": from_revision + 1,
            "path": "tailoring_resolution",
            "old_value": stored,
            "new_value": expected,
            "reason": f"automatically refresh deterministic tailoring after: {reason}",
            "basis": basis,
            "changed_at": now_utc(),
        }
    )


def amend_record(
    path: Path,
    *,
    dotted_path: str,
    new_value: Any,
    reason: str,
    basis: str,
    allow_add: bool = False,
) -> dict[str, Any]:
    ensure_skill_integrity()
    if not reason.strip() or not basis.strip():
        raise GovernanceError("amendment reason and basis are required")
    document = read_json(path)
    if document.get("meta_type") not in {"TaskContract", "TaskOutcome"}:
        raise GovernanceError("only TaskContract and TaskOutcome can use this amendment flow")
    old_value = _set_dotted_path(document, dotted_path, new_value, allow_add=allow_add)
    from_revision = document.get("revision")
    if not isinstance(from_revision, int):
        raise GovernanceError(f"{path}: revision must be an integer")
    document["revision"] = from_revision + 1
    amendments = document.setdefault("amendments", [])
    if not isinstance(amendments, list):
        raise GovernanceError(f"{path}: amendments must be an array")
    amendments.append(
        {
            "from_revision": from_revision,
            "to_revision": from_revision + 1,
            "path": dotted_path,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "basis": basis,
            "changed_at": now_utc(),
        }
    )
    _refresh_tailoring_after_amendment(document, amendments, reason=reason, basis=basis)
    schema_name = "task-before.schema.json" if document["meta_type"] == "TaskContract" else "task-after.schema.json"
    require_valid_json_document(document, schema_name, path.name)
    require_record_semantics(path, document)
    atomic_write_json(path, document)
    return document


def amend_record_batch(
    path: Path,
    *,
    changes: Iterable[dict[str, Any]],
    reason: str,
    basis: str,
) -> dict[str, Any]:
    """Apply a validated historical correction set without invalid intermediate writes."""

    ensure_skill_integrity()
    if not reason.strip() or not basis.strip():
        raise GovernanceError("batch amendment reason and basis are required")
    document = read_json(path)
    if document.get("meta_type") not in {"TaskContract", "TaskOutcome"}:
        raise GovernanceError("only TaskContract and TaskOutcome can use this amendment flow")
    amendments = document.setdefault("amendments", [])
    if not isinstance(amendments, list):
        raise GovernanceError(f"{path}: amendments must be an array")
    applied = 0
    for change in changes:
        dotted_path = change.get("path")
        if not isinstance(dotted_path, str):
            raise GovernanceError("each batch change requires a string path")
        if "value" not in change:
            raise GovernanceError(f"batch change {dotted_path} requires value")
        from_revision = document.get("revision")
        if not isinstance(from_revision, int):
            raise GovernanceError(f"{path}: revision must be an integer")
        old_value = _set_dotted_path(
            document, dotted_path, change["value"], allow_add=bool(change.get("allow_add"))
        )
        document["revision"] = from_revision + 1
        amendments.append(
            {
                "from_revision": from_revision,
                "to_revision": from_revision + 1,
                "path": dotted_path,
                "old_value": old_value,
                "new_value": change["value"],
                "reason": change.get("reason") or reason,
                "basis": change.get("basis") or basis,
                "changed_at": now_utc(),
            }
        )
        applied += 1
    if not applied:
        raise GovernanceError("batch amendment requires at least one change")
    _refresh_tailoring_after_amendment(document, amendments, reason=reason, basis=basis)
    schema_name = "task-before.schema.json" if document["meta_type"] == "TaskContract" else "task-after.schema.json"
    require_valid_json_document(document, schema_name, path.name)
    require_record_semantics(path, document)
    atomic_write_json(path, document)
    return document


def append_run_event(
    task_dir: Path,
    *,
    run_id: str,
    attempt_id: str,
    event_type: str,
    summary: str,
    status: str,
    evidence_refs: Iterable[str] = (),
    side_effects: Iterable[str] = (),
    redactions: Iterable[str] = (),
    exit_code: int | None = None,
) -> dict[str, Any]:
    ensure_skill_integrity()
    require_id(run_id, "run_id")
    require_id(attempt_id, "attempt_id")
    if event_type not in RUN_EVENT_TYPES:
        raise GovernanceError(f"unsupported event_type: {event_type}")
    if status not in RUN_STATUSES:
        raise GovernanceError(f"unsupported run event status: {status}")
    if not summary.strip():
        raise GovernanceError("summary is required")
    before_path = task_dir / "before.json"
    ledger_path = task_dir / "run.jsonl"
    before = read_json(before_path)
    require_valid_json_document(before, "task-before.schema.json", "before")
    tailoring_errors = validate_tailoring_resolution(before)
    if tailoring_errors:
        raise GovernanceError("invalid tailoring resolution: " + "; ".join(tailoring_errors))
    if before.get("legacy_run_policy") and before.get("created_at", "") >= LEGACY_RUN_POLICY_CUTOFF:
        raise GovernanceError("legacy_run_policy is restricted to tasks created before enforcement")
    events = read_jsonl(ledger_path)
    if (task_dir / "after.json").exists():
        raise GovernanceError("cannot append run events after a terminal TaskOutcome exists")
    if not events and event_type != "run_started":
        raise GovernanceError("the first run ledger event must be run_started")
    if events and event_type == "run_started":
        raise GovernanceError("run_started already exists for this task ledger")
    if events:
        lifecycle_errors = validate_run_lifecycle(before, events, terminal_required=False)
        if lifecycle_errors:
            raise GovernanceError("existing run ledger is invalid: " + "; ".join(lifecycle_errors))
        if events[-1]["event_type"] == "run_finished":
            raise GovernanceError("cannot append after run_finished")
        if run_id != events[0]["run_id"]:
            raise GovernanceError("all events in a task ledger must use the same run_id")
        seen_attempts = {event["attempt_id"] for event in events}
        current_attempt = events[-1]["attempt_id"]
        if event_type == "retry":
            if attempt_id in seen_attempts:
                raise GovernanceError("retry must introduce a new attempt_id")
            if not any(
                event.get("attempt_id") == current_attempt
                and event.get("event_type") == "failure"
                and event.get("status") in {"failed", "blocked"}
                for event in events
            ):
                raise GovernanceError(
                    "retry requires an explicit failed or blocked failure event on the current attempt"
                )
        elif attempt_id != current_attempt:
            raise GovernanceError("attempt_id can change only on a retry event")
    if event_type == "run_started" and status != "started":
        raise GovernanceError("run_started status must be started")
    if event_type == "run_started":
        resolution = before["tailoring_resolution"]
        if int(resolution["stage"][1:]) < 4:
            raise GovernanceError("run_started requires a current S4-or-later tailoring resolution")
        if resolution["blocking_reasons"]:
            raise GovernanceError("run_started is blocked by tailoring: " + "; ".join(resolution["blocking_reasons"]))
    if event_type in {"mutation", "external_effect"} and before["tailoring_resolution"]["blocking_reasons"]:
        raise GovernanceError(
            f"{event_type} is blocked by tailoring; record failure, human gate, rollback, or reclassify first: "
            + "; ".join(before["tailoring_resolution"]["blocking_reasons"])
        )
    event_required_permissions = set(
        load_tailoring_map()["authority_policy"]["run_event_permission_requirements"].get(event_type, [])
    )
    granted_permissions = set(before.get("authority", {}).get("execution_permissions", []))
    missing_event_permissions = sorted(event_required_permissions - granted_permissions)
    if missing_event_permissions:
        raise GovernanceError(
            f"{event_type} requires execution permissions: {', '.join(missing_event_permissions)}"
        )
    if event_type == "retry" and status != "started":
        raise GovernanceError("retry status must be started")
    if event_type == "failure" and status not in {"failed", "blocked"}:
        raise GovernanceError("failure status must be failed or blocked")
    if event_type == "run_finished" and status not in {"succeeded", "failed", "blocked"}:
        raise GovernanceError("run_finished status must be succeeded, failed, or blocked")
    sequence = len(events) + 1
    event = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "RunLedger",
        "event_id": f"{run_id}-E{sequence:04d}",
        "project_id": before["project_id"],
        "task_id": before["task_id"],
        "run_id": run_id,
        "attempt_id": attempt_id,
        "sequence": sequence,
        "timestamp": now_utc(),
        "event_type": event_type,
        "summary": summary.strip(),
        "status": status,
        "exit_code": exit_code,
        "evidence_refs": list(evidence_refs),
        "side_effects": list(side_effects),
        "redactions": list(redactions),
    }
    require_valid_json_document(event, "run-event.schema.json", f"run[{sequence}]")
    if not events:
        before["lifecycle_state"] = "Frozen"
        before["frozen_at"] = event["timestamp"]
        require_valid_json_document(before, "task-before.schema.json", "before")
        atomic_write_json(before_path, before)
    append_jsonl(ledger_path, event)
    return event


def validate_run_lifecycle(
    before: dict[str, Any], events: list[dict[str, Any]], *, terminal_required: bool
) -> list[str]:
    errors: list[str] = []
    if not events:
        return ["run ledger is empty"] if terminal_required else []
    run_id = events[0].get("run_id")
    current_attempt = events[0].get("attempt_id")
    seen_attempts: set[Any] = {current_attempt}
    finished = False
    previous_timestamp = ""
    legacy_policy = before.get("legacy_run_policy", {})
    legacy_sequences: set[Any] = set()
    if isinstance(legacy_policy, dict) and legacy_policy:
        if before.get("created_at", "") >= LEGACY_RUN_POLICY_CUTOFF:
            errors.append("legacy_run_policy is restricted to tasks created before enforcement")
        else:
            legacy_sequences = set(legacy_policy.get("affected_sequences", []))
            for sequence in sorted(legacy_sequences):
                if not isinstance(sequence, int) or sequence < 1 or sequence > len(events):
                    errors.append(f"legacy_run_policy references missing sequence {sequence}")
                elif events[sequence - 1].get("event_type") != "retry":
                    errors.append(f"legacy_run_policy sequence {sequence} is not a retry event")
    for position, event in enumerate(events, 1):
        errors.extend(validate_json_document(event, "run-event.schema.json", f"run[{position}]"))
        if event.get("sequence") != position:
            errors.append(f"run[{position}].sequence must be {position}")
        if event.get("project_id") != before.get("project_id"):
            errors.append(f"run[{position}].project_id does not match TaskContract")
        if event.get("task_id") != before.get("task_id"):
            errors.append(f"run[{position}].task_id does not match TaskContract")
        if event.get("run_id") != run_id:
            errors.append(f"run[{position}].run_id differs from the first event")
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str) and previous_timestamp and timestamp < previous_timestamp:
            errors.append(f"run[{position}].timestamp is earlier than the prior event")
        if isinstance(timestamp, str):
            previous_timestamp = timestamp
        event_type = event.get("event_type")
        attempt = event.get("attempt_id")
        if position == 1:
            if event_type != "run_started":
                errors.append("first run event must be run_started")
            if event.get("status") != "started":
                errors.append("run_started status must be started")
        elif finished:
            errors.append(f"run[{position}] occurs after run_finished")
        if event_type == "retry":
            if attempt in seen_attempts and position not in legacy_sequences:
                errors.append(f"run[{position}]: retry must use a new attempt_id")
            if not any(
                prior.get("attempt_id") == current_attempt
                and prior.get("event_type") == "failure"
                and prior.get("status") in {"failed", "blocked"}
                for prior in events[: position - 1]
            ) and position not in legacy_sequences:
                errors.append(
                    f"run[{position}]: retry requires an explicit failed or blocked failure "
                    "event on the current attempt"
                )
            if event.get("status") != "started" and position not in legacy_sequences:
                errors.append(f"run[{position}]: retry status must be started")
            if attempt not in seen_attempts:
                current_attempt = attempt
                seen_attempts.add(attempt)
        elif position > 1 and attempt != current_attempt:
            errors.append(f"run[{position}]: attempt_id changed without retry")
        if event_type == "failure" and event.get("status") not in {"failed", "blocked"}:
            errors.append(f"run[{position}]: failure has invalid status")
        if event_type == "run_finished":
            if event.get("status") not in {"succeeded", "failed", "blocked"}:
                errors.append(f"run[{position}]: run_finished has invalid status")
            finished = True
    if terminal_required and events[-1].get("event_type") != "run_finished":
        errors.append("terminal TaskOutcome requires run_finished as the final event")
    return errors


# Paths this tooling writes on its own behalf, not as part of the task's work. They
# are always in scope: making every task declare them would fail the check for reasons
# that have nothing to do with the change under review. Kept deliberately narrow --
# the docs scaffold README is exempt, the product documentation around it is not.
IMPLICIT_SCOPE = (".project-governance", "LG_project_docs/README.md")


def _scope_pattern_matches(relative: str, pattern: str) -> bool:
    """Match one changed path against one declared scope entry.

    allowed_paths is written by hand and comes in three shapes: a bare file, a
    directory that stands for everything under it, and an explicit `**` glob. Treat
    all three the same way rather than making the author remember which is which.
    """

    pattern = pattern.replace("\\", "/").strip().rstrip("/")
    if not pattern:
        return False
    base = pattern
    for suffix in ("/**", "/*"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    base = base.rstrip("/")
    if relative == base or relative.startswith(base + "/"):
        return True
    return fnmatch.fnmatch(relative, pattern)


def _is_external_declaration(pattern: str) -> bool:
    """A declaration git cannot speak about: absolute, drive-qualified or escaping."""

    value = pattern.replace("\\", "/").strip()
    return value.startswith("/") or value.startswith("..") or re.match(r"^[A-Za-z]:/", value) is not None


def _git_changed_paths(root: Path, head: str) -> tuple[list[str], str | None]:
    """Every path Git says changed since the snapshot: committed plus working tree.

    Returns the paths and, when a query did not answer, the reason. A failed query is
    never reported as "nothing changed": the whole point of this check is that it cannot
    pass without Git actually speaking, so an unreachable baseline has to surface rather
    than quietly shrink the set of changes being reconciled.

    `-z` throughout: this repository has non-ASCII paths and Git quotes those in its
    default output, which would silently turn a real path into a non-matching literal.
    """

    def run(args: list[str]) -> tuple[list[str] | None, str | None]:
        try:
            result = subprocess.run(["git", *args], cwd=root, check=False, capture_output=True)
        except OSError as exc:
            return None, f"git {args[0]} could not be run: {exc}"
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
            first = detail[0] if detail else f"exit {result.returncode}"
            return None, f"git {args[0]} failed: {first}"
        return [item for item in result.stdout.decode("utf-8", "replace").split("\x00") if item], None

    committed, failure = run(["diff", "--name-only", "-z", f"{head}..HEAD"])
    if failure is not None:
        return [], failure
    entries, failure = run(["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    if failure is not None:
        return [], failure
    changed: set[str] = set(committed or [])
    entries = entries or []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) < 4:
            continue
        code, path = entry[:2], entry[3:]
        changed.add(path)
        if code[0] in {"R", "C"} and index < len(entries):
            changed.add(entries[index])
            index += 1
    return sorted(changed), None


def reconcile_scope(project_root: Path, before: dict[str, Any]) -> dict[str, Any]:
    """Compare the scope a task declared against what git says it actually touched.

    Every other blocker in this system checks a field the Agent filled in itself, so it
    can be satisfied by typing a value. This one cannot: one side is the declaration,
    the other is git. A change outside the declared paths is reported by name and the
    task cannot close until either the change is reverted or the scope is amended.
    """

    snapshot = before.get("source_snapshot") or {}
    if snapshot.get("vcs") != "git" or not snapshot.get("head_exists") or not snapshot.get("head"):
        return {
            "status": "Skipped",
            "reason": "no Git baseline in source_snapshot; nothing independent to reconcile against",
            "out_of_scope": [], "undeclared_untouched": [], "changed_count": 0,
        }
    declared = [str(item) for item in (before.get("scope", {}).get("allowed_paths") or [])]
    reconcilable = [item for item in declared if not _is_external_declaration(item)]
    external = [item for item in declared if _is_external_declaration(item)]
    patterns = list(reconcilable) + list(IMPLICIT_SCOPE)

    changed, failure = _git_changed_paths(project_root.resolve(), str(snapshot["head"]))
    if failure is not None:
        return {
            "status": "Unverifiable",
            "reason": failure,
            "out_of_scope": [], "undeclared_untouched": [], "changed_count": 0,
        }
    out_of_scope = [
        path for path in changed
        if not any(_scope_pattern_matches(path, pattern) for pattern in patterns)
    ]
    untouched = [
        pattern for pattern in reconcilable
        if not any(_scope_pattern_matches(path, pattern) for path in changed)
    ]
    return {
        "status": "Failed" if out_of_scope else "Passed",
        "changed_count": len(changed),
        "out_of_scope": out_of_scope,
        "undeclared_untouched": untouched,
        "external_declarations": external,
    }


def _write_scope_reconciliation_view(
    project_root: Path, before: dict[str, Any], report: dict[str, Any]
) -> None:
    """Leave the reconciliation as evidence, not just as a close that happened to pass."""

    root = governance_root(project_root)
    lines = [
        f"# Scope Reconciliation: {before['task_id']}",
        "",
        f"- Status: {report['status']}",
        f"- Changed paths seen by Git: {report['changed_count']}",
        "",
        "## Declared but untouched",
        "",
    ]
    untouched = report["undeclared_untouched"]
    lines.extend(f"- {item}" for item in untouched)
    if not untouched:
        lines.append("- none")
    if report.get("external_declarations"):
        lines.extend(["", "## Outside this repository (not reconcilable)", ""])
        lines.extend(f"- {item}" for item in report["external_declarations"])
    _write_derived_view(
        root=root,
        content_path=root / "generated" / "scope-reconciliation" / f"{before['task_id']}.md",
        content="".join(line + chr(10) for line in lines),
        project_id=before["project_id"],
        view_id=f"DV-{before['project_id']}-{before['task_id']}-SCOPE-RECON",
        view_kind="scope-reconciliation",
        sources=[Path(project_root) / ".project-governance" / "tasks" / before["task_id"] / "before.json"],
    )


def close_task(
    task_dir: Path,
    *,
    status: str,
    established_facts: Iterable[str],
    actual_changes: Iterable[str],
    verification: Iterable[dict[str, Any]],
    incomplete_items: Iterable[dict[str, Any]] = (),
    legacy_issues: Iterable[dict[str, Any]] = (),
    decisions: Iterable[str] = (),
    evidence_refs: Iterable[str] = (),
    next_tasks: Iterable[str] = (),
    artifact_manifest: Iterable[dict[str, Any]] | None = None,
    source_snapshot: dict[str, Any] | None = None,
) -> Path:
    ensure_skill_integrity()
    if status not in OUTCOME_STATES:
        raise GovernanceError(f"unsupported outcome status: {status}")
    before = read_json(task_dir / "before.json")
    require_valid_json_document(before, "task-before.schema.json", "before")
    after_path = task_dir / "after.json"
    if after_path.exists():
        raise GovernanceError(f"task outcome already exists: {after_path}; use amend_record.py")
    project_root = task_dir.resolve().parents[2]
    scope_report = reconcile_scope(project_root, before)
    if scope_report["status"] == "Unverifiable":
        raise GovernanceError(
            "scope reconciliation could not run: " + str(scope_report["reason"])
            + "; the declared scope cannot be checked against Git, and a close is not "
            "allowed to pass on an unchecked scope -- restore the baseline commit, or "
            "amend source_snapshot with a reachable one and say why"
        )
    if scope_report["status"] == "Failed":
        listed = scope_report["out_of_scope"]
        shown = ", ".join(listed[:12])
        extra = f" (+{len(listed) - 12} more)" if len(listed) > 12 else ""
        raise GovernanceError(
            "scope reconciliation failed: changed outside scope.allowed_paths: "
            + shown + extra
            + "; revert them, or amend scope.allowed_paths with amend_record.py"
        )
    events = read_jsonl(task_dir / "run.jsonl")
    changes = [value for value in actual_changes if value]
    execution_required = status == "Implemented" or bool(changes)
    lifecycle_errors = validate_run_lifecycle(before, events, terminal_required=execution_required or bool(events))
    if lifecycle_errors:
        raise GovernanceError("; ".join(lifecycle_errors))
    if events and before.get("lifecycle_state") != "Frozen":
        raise GovernanceError("a task with run events must have a Frozen TaskContract")
    checks = [dict(value) for value in verification]
    incomplete = [dict(value) for value in incomplete_items]
    legacy = [dict(value) for value in legacy_issues]
    for position, item in enumerate(checks):
        if item.get("result") not in VERIFICATION_RESULTS:
            raise GovernanceError(f"verification[{position}].result is invalid")
        item.setdefault("evidence_refs", [])
    if status == "Implemented":
        if not events or events[-1].get("status") != "succeeded":
            raise GovernanceError("Implemented requires a succeeded run_finished event")
        if not any(
            event.get("event_type") == "verification" and event.get("status") == "succeeded"
            for event in events
        ):
            raise GovernanceError("Implemented requires at least one succeeded verification RunLedger event")
        if not any(item.get("result") == "Passed" for item in checks):
            raise GovernanceError("Implemented requires at least one Passed verification result")
        blocking = [
            item for item in checks
            if item.get("required", True) and item.get("result") in {"Failed", "Blocked"}
        ]
        if blocking:
            raise GovernanceError("Implemented cannot contain a required Failed or Blocked verification")
        if any(
            item.get("result") == "Passed" and not item.get("evidence_refs")
            for item in checks
        ):
            raise GovernanceError("Passed verification in an Implemented outcome requires evidence_refs")
    if artifact_manifest is None:
        planned_types = {item.get("meta_type") for item in before["artifact_manifest"]}
        if len(before["artifact_manifest"]) != 3 or planned_types != {"TaskContract", "RunLedger", "TaskOutcome"}:
            raise GovernanceError(
                "an explicit terminal artifact_manifest is required when the frozen manifest contains conditional, authority, or derived assets"
            )
    terminal_manifest = [dict(item) for item in (artifact_manifest if artifact_manifest is not None else before["artifact_manifest"])]
    for item in terminal_manifest:
        if "outcome" not in item:
            action = item.get("action")
            item["outcome"] = {
                "Create/Revise": "Created" if item.get("meta_type") == "TaskOutcome" else "Revised",
                "Reference": "Referenced",
                "Generate": "Generated",
                "On Event": "Not Triggered",
                "N/A": "Not Applicable",
            }.get(action, "Deferred")
    manifest_errors = validate_artifact_manifest(
        terminal_manifest, terminal=True, before_manifest=before["artifact_manifest"]
    )
    if manifest_errors:
        raise GovernanceError("; ".join(manifest_errors))
    after = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "TaskOutcome",
        "project_id": before["project_id"],
        "work_item_id": before["work_item_id"],
        "task_id": before["task_id"],
        "revision": 1,
        "status": status,
        "completed_at": now_utc(),
        "source_snapshot": source_snapshot or capture_source_snapshot(task_dir.resolve().parents[2]),
        "established_facts": [value for value in established_facts if value],
        "actual_changes": changes,
        "verification": checks,
        "incomplete_items": incomplete,
        "legacy_issues": legacy,
        "decisions": [value for value in decisions if value],
        "evidence_refs": [value for value in evidence_refs if value],
        "next_tasks": [value for value in next_tasks if value],
        "artifact_manifest": terminal_manifest,
        "amendments": [],
    }
    require_valid_json_document(after, "task-after.schema.json", "after")
    atomic_write_json(after_path, after)
    _write_scope_reconciliation_view(project_root, before, scope_report)
    # Closing a task is the point where its DerivedViews stop being rebuilt, so it is
    # also the point where a Source Pack nothing links to any more can be reclaimed.
    collect_orphan_content_blobs(
        governance_root(task_dir.resolve().parents[2]) / "generated" / "source-packs"
    )
    return after_path


def _authority_assets(root: Path, project_id: str) -> list[dict[str, Any]]:
    authority_root = root / "authority"
    if not authority_root.exists():
        return []
    assets: list[dict[str, Any]] = []
    profiles = {
        item["legacy_kind"]: item
        for item in resolve_all_profiles(default_profile_index_path())
    }
    for path in sorted(authority_root.rglob("*.json")):
        try:
            value = read_json(path)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            raise GovernanceError(f"invalid authority envelope {path}: {exc}") from exc
        require_valid_json_document(value, "authority-asset.schema.json", str(path))
        profile = profiles.get(value["legacy_kind"])
        if profile is None or profile["meta_type"] != "AuthorityAsset":
            raise GovernanceError(f"{path}: legacy_kind does not resolve to AuthorityAsset")
        state_model = profile["legacy_state_model"]
        if value["profile_state_model"] != state_model:
            raise GovernanceError(f"{path}: profile_state_model must be {state_model}")
        if value["state"] not in STATE_MODELS[state_model]:
            raise GovernanceError(f"{path}: state is invalid for {state_model}")
        ref = value["content_ref"]
        if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", ref) and not ref.startswith("external:"):
            local_ref = Path(ref)
            local_target = local_ref if local_ref.is_absolute() else root.parent / local_ref
            if not local_target.is_file():
                raise GovernanceError(f"{path}: local content_ref does not exist: {local_target}")
        if value["project_id"] != project_id:
            continue
        assets.append(
            {
                "asset_id": value["asset_id"],
                "legacy_kind": value["legacy_kind"],
                "state": value["state"],
                "revision": value["revision"],
                "content_ref": value["content_ref"],
                "envelope_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return assets


def _link_task_graph(task_graph: list[dict[str, Any]], derived: dict[str, list[dict[str, str]]]) -> None:
    """Fill forward succession edges and derive the reverse ones.

    next_tasks may name a task that does not exist yet -- recording "this run spawned
    a regression" before the follow-up is created is the normal order -- so unlike
    depends_on a dangling target is not an error. Reverse edges are built only for
    targets present in the project; the forward edge keeps the dangling ones visible.
    """

    by_id = {node["task_id"]: node for node in task_graph}
    for task_id, links in derived.items():
        node = by_id.get(task_id)
        if node is None:
            continue
        node["next_tasks"] = [dict(link) for link in links]
        for link in links:
            target = by_id.get(link["task_id"])
            if target is None:
                continue
            target["derived_from"].append(
                {"task_id": task_id, "relation": link["relation"], "reason": link["reason"]}
            )
    for node in task_graph:
        for dependency in node.get("depends_on", []):
            upstream = by_id.get(dependency)
            if upstream is not None and node["task_id"] not in upstream["required_by"]:
                upstream["required_by"].append(node["task_id"])
    for node in task_graph:
        node["derived_from"].sort(key=lambda item: (item["task_id"], item["relation"]))
        node["required_by"].sort()


def _validate_task_graph(task_graph: list[dict[str, Any]]) -> None:
    by_id: dict[str, dict[str, Any]] = {}
    ordinals: dict[int, str] = {}
    for node in task_graph:
        task_id = node["task_id"]
        ordinal = node["ordinal"]
        if task_id in by_id:
            raise GovernanceError(f"duplicate task_id in project: {task_id}")
        if ordinal in ordinals:
            raise GovernanceError(
                f"duplicate task ordinal {ordinal}: {ordinals[ordinal]} and {task_id}"
            )
        by_id[task_id] = node
        ordinals[ordinal] = task_id
    for node in task_graph:
        for dependency in node.get("depends_on", []):
            if dependency not in by_id:
                raise GovernanceError(f"{node['task_id']} depends on missing task {dependency}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise GovernanceError(f"task dependency cycle detected at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id)
    for node in task_graph:
        for dependency in node.get("depends_on", []):
            if by_id[dependency]["ordinal"] >= node["ordinal"]:
                raise GovernanceError(
                    f"{node['task_id']} depends on non-prior task {dependency}"
                )


def rebuild_project_state(project_root: Path, project_id: str) -> Path:
    ensure_skill_integrity()
    require_id(project_id, "project_id")
    root = governance_root(project_root)
    source_tasks: list[dict[str, Any]] = []
    current_facts: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    task_graph: list[dict[str, Any]] = []
    derived_links: dict[str, list[dict[str, str]]] = {}
    digest_parts: list[bytes] = []
    tasks_root = root / "tasks"
    if tasks_root.exists():
        for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
            before_path = task_dir / "before.json"
            after_path = task_dir / "after.json"
            minimal_path = task_dir / "task-record.json"
            if minimal_path.exists():
                if before_path.exists() or (task_dir / "run.jsonl").exists() or after_path.exists():
                    raise GovernanceError(
                        f"{task_dir}: active Minimal and default carriers must not coexist"
                    )
                from minimal_task import require_valid_minimal_record

                record = read_json(minimal_path)
                require_valid_minimal_record(record, task_dir=task_dir)
                if record["project_id"] != project_id:
                    continue
                digest_parts.append(minimal_path.read_bytes())
                task_graph.append(
                    {
                        "task_id": record["task_id"],
                        "ordinal": record["ordinal"],
                        "depends_on": record.get("depends_on", []),
                        "supersedes": record.get("supersedes", []),
                        "blocked_by": record.get("blocked_by", []),
                        "next_tasks": [],
                        "derived_from": [],
                        "required_by": [],
                    }
                )
                outcome = record.get("task_outcome")
                if not isinstance(outcome, dict):
                    source_tasks.append(
                        {
                            "task_id": record["task_id"],
                            "ordinal": record["ordinal"],
                            "status": "Active",
                            "carrier_mode": "Minimal",
                        }
                    )
                    continue
                source_tasks.append(
                    {
                        "task_id": record["task_id"],
                        "ordinal": record["ordinal"],
                        "status": outcome["status"],
                        "revision": record["revision"],
                        "completed_at": outcome["completed_at"],
                        "carrier_mode": "Minimal",
                    }
                )
                for fact in outcome.get("established_facts", []):
                    current_facts.append(
                        {
                            "task_id": record["task_id"],
                            "ordinal": record["ordinal"],
                            "fact": fact,
                        }
                    )
                for item in outcome.get("incomplete_items", []):
                    unresolved.append(
                        {
                            "task_id": record["task_id"],
                            "ordinal": record["ordinal"],
                            "category": "incomplete_items",
                            **item,
                        }
                    )
                if outcome.get("next_tasks"):
                    derived_links[record["task_id"]] = list(outcome["next_tasks"])
                continue
            if not before_path.exists():
                continue
            before = read_json(before_path)
            require_valid_json_document(before, "task-before.schema.json", str(before_path))
            if before["task_id"] != task_dir.name:
                raise GovernanceError(f"{before_path}: task_id must match directory name")
            semantic_errors = validate_artifact_manifest(before["artifact_manifest"], terminal=False)
            if before["task_profile"]["primary_development_type"] not in before["task_profile"]["development_types"]:
                semantic_errors.append("primary_development_type must be included in development_types")
            if before["task_id"] in set(before.get("depends_on", [])):
                semantic_errors.append("task cannot depend on itself")
            if semantic_errors:
                raise GovernanceError(f"{before_path}: " + "; ".join(semantic_errors))
            if before["project_id"] != project_id:
                continue
            task_errors = validate_task_directory(task_dir)
            if task_errors:
                raise GovernanceError(f"{task_dir}: " + "; ".join(task_errors))
            digest_parts.append(before_path.read_bytes())
            task_graph.append(
                {
                    "task_id": before["task_id"],
                    "ordinal": before["ordinal"],
                    "depends_on": before.get("depends_on", []),
                    "supersedes": before.get("supersedes", []),
                    "blocked_by": before.get("blocked_by", []),
                    "next_tasks": [],
                    "derived_from": [],
                    "required_by": [],
                }
            )
            if not after_path.exists():
                source_tasks.append({"task_id": before["task_id"], "ordinal": before["ordinal"], "status": "Active"})
                continue
            after = read_json(after_path)
            require_valid_json_document(after, "task-after.schema.json", str(after_path))
            for key in ("project_id", "work_item_id", "task_id"):
                if after[key] != before[key]:
                    raise GovernanceError(f"{after_path}: {key} does not match TaskContract")
            digest_parts.append(after_path.read_bytes())
            source_tasks.append(
                {
                    "task_id": after["task_id"],
                    "ordinal": before["ordinal"],
                    "status": after["status"],
                    "revision": after["revision"],
                    "completed_at": after["completed_at"],
                }
            )
            for fact in after.get("established_facts", []):
                current_facts.append({"task_id": after["task_id"], "ordinal": before["ordinal"], "fact": fact})
            for category in ("incomplete_items", "legacy_issues"):
                for item in after.get(category, []):
                    unresolved.append(
                        {"task_id": after["task_id"], "ordinal": before["ordinal"], "category": category, **item}
                    )
            if after.get("next_tasks"):
                derived_links[after["task_id"]] = list(after["next_tasks"])
    _link_task_graph(task_graph, derived_links)
    _validate_task_graph(task_graph)
    source_tasks.sort(key=lambda item: (item["ordinal"], item["task_id"]))
    current_facts.sort(key=lambda item: (item["ordinal"], item["task_id"]))
    unresolved.sort(key=lambda item: (item["ordinal"], item["task_id"], item["category"]))
    authority_assets = _authority_assets(root, project_id)
    digest_parts.extend(
        asset["envelope_sha256"].encode("ascii") for asset in authority_assets
    )
    digest = hashlib.sha256(b"\n".join(digest_parts)).hexdigest()
    state = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "ProjectState",
        "project_id": project_id,
        "generated": True,
        "generated_at": now_utc(),
        "source_digest": digest,
        "source_tasks": source_tasks,
        "current_facts": current_facts,
        "unresolved_items": unresolved,
        "task_graph": sorted(task_graph, key=lambda item: (item["ordinal"], item["task_id"])),
        "authority_assets": authority_assets,
    }
    require_valid_json_document(state, "project-state.schema.json", "project-state")
    target = root / "project-state.json"
    atomic_write_json(target, state)
    return target


def render_project_status(state: dict[str, Any]) -> str:
    lines = [
        f"# Project Status: {state['project_id']}",
        "",
        f"Generated: {state['generated_at']}",
        "",
        "## Tasks",
        "",
        "| Task | Status | Revision |",
        "|---|---|---:|",
    ]
    for item in state["source_tasks"]:
        lines.append(
            f"| {item['task_id']} | {item['status']} | {item.get('revision', '')} |"
        )
    lines.extend(["", "## Established facts", ""])
    lines.extend(
        f"- `{item['task_id']}`: {item['fact']}" for item in state["current_facts"]
    )
    lines.extend(["", "## Unresolved items", ""])
    lines.extend(
        f"- `{item['task_id']}` / {item['category']}: {item.get('summary', '')}; "
        f"reason={item.get('reason', '')}; impact={item.get('impact', '')}; "
        f"owner={item.get('owner', '')}; reentry={item.get('reentry_condition', '')}"
        for item in state["unresolved_items"]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_task_review(before: dict[str, Any], after: dict[str, Any] | None) -> str:
    lines = [
        f"# Task Review: {before['task_id']}",
        "",
        f"- Objective: {before['objective']}",
        f"- Contract revision: {before['revision']}",
        f"- Contract state: {before['lifecycle_state']}",
        f"- Depends on: {', '.join(before.get('depends_on', [])) or 'None'}",
        "",
        "## Acceptance criteria",
        "",
    ]
    lines.extend(f"- {item}" for item in before["acceptance"]["criteria"])
    if after is None:
        lines.extend(["", "## Outcome", "", "No terminal outcome recorded."])
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "",
            "## Outcome",
            "",
            f"- Status: {after['status']}",
            f"- Revision: {after['revision']}",
            "",
            "## Established facts",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in after["established_facts"])
    lines.extend(["", "## Actual changes", ""])
    lines.extend(f"- {item}" for item in after["actual_changes"])
    lines.extend(["", "## Verification", ""])
    lines.extend(
        f"- {item.get('result')}: {item.get('summary')}" for item in after["verification"]
    )
    lines.extend(["", "## Evidence", ""])
    lines.extend(f"- {item}" for item in after.get("evidence_refs", []))
    lines.extend(["", "## Incomplete items", ""])
    lines.extend(
        f"- {item.get('summary')}; reason={item.get('reason')}; impact={item.get('impact')}; "
        f"owner={item.get('owner')}; reentry={item.get('reentry_condition')}"
        for item in after.get("incomplete_items", [])
    )
    lines.extend(["", "## Legacy issues", ""])
    lines.extend(
        f"- {item.get('summary')}; reason={item.get('reason')}; impact={item.get('impact')}; "
        f"owner={item.get('owner')}; reentry={item.get('reentry_condition')}"
        for item in after.get("legacy_issues", [])
    )
    lines.extend(["", "## Decisions", ""])
    lines.extend(f"- {item}" for item in after.get("decisions", []))
    lines.extend(["", "## Next tasks", ""])
    lines.extend(f"- {item}" for item in after.get("next_tasks", []))
    lines.extend(["", "## Terminal artifact manifest", ""])
    lines.extend(
        f"- {item.get('asset_id')} / {item.get('meta_type')} / {item.get('action')} / {item.get('outcome')}"
        for item in after.get("artifact_manifest", [])
    )
    lines.extend(["", "## Amendments", ""])
    lines.extend(
        f"- r{item.get('from_revision')}→r{item.get('to_revision')} {item.get('path')}: "
        f"{item.get('reason')} (basis: {item.get('basis')})"
        for item in [*before.get("amendments", []), *after.get("amendments", [])]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_legacy_mapping(profiles: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {meta_type: 0 for meta_type in sorted(META_TYPES)}
    for item in profiles:
        counts[item["meta_type"]] += 1
    lines = [
        "# V6.3 Legacy Profile Migration Map",
        "",
        "| Meta type | Profile count |",
        "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in counts.items())
    lines.extend(
        [
            "",
            "| Legacy kind | Name | Owner | Legacy state | Meta type |",
            "|---|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {item['legacy_kind']} | {item['name']} | {item['owner_standard']} | "
        f"{item['legacy_state_model']} | {item['meta_type']} |"
        for item in profiles
    )
    return "\n".join(lines) + "\n"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_content_addressed(content_path: Path, value: str, store: Path) -> Path:
    """Keep one copy of `value` under its digest and hard-link `content_path` to it.

    A Source Pack is byte-identical across the stages of a task, and across tasks that
    resolve the same sources, so writing it per stage stored the same 1.2 MB three times
    over. The store holds one copy per digest while every caller still gets a real file
    at the contracted path, so ripgrep, the DerivedView hash checks and every existing
    reader are unaffected. Filesystems that refuse hard links fall back to a full copy.
    """

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    blob = store / f"{digest}{content_path.suffix}"
    if not blob.is_file() or sha256_file(blob) != digest:
        write_text(blob, value)
    content_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if content_path.exists() or content_path.is_symlink():
            content_path.unlink()
        os.link(blob, content_path)
    except OSError:
        write_text(content_path, value)
    return blob


# A compile writes the blob before it links to it. Collecting only blobs older than
# this leaves that window alone instead of deleting a pack out from under a run.
ORPHAN_BLOB_GRACE_SECONDS = 300


def collect_orphan_content_blobs(store: Path) -> list[Path]:
    """Drop content-addressed blobs that no DerivedView links to any more.

    `write_content_addressed` hard-links every consumer to one blob, so a blob back down
    to a single link is referenced by nothing but the store. Where the filesystem refused
    a hard link the consumer holds an independent copy, so dropping the blob is still
    safe. Returns what was removed so a caller can report it.
    """

    if not store.is_dir():
        return []
    cutoff = time.time() - ORPHAN_BLOB_GRACE_SECONDS
    removed: list[Path] = []
    for blob in sorted(store.iterdir()):
        if not blob.is_file():
            continue
        info = blob.stat()
        if info.st_nlink > 1 or info.st_mtime > cutoff:
            continue
        try:
            blob.unlink()
        except OSError:
            continue
        removed.append(blob)
    return removed


def _write_derived_view(
    *,
    root: Path,
    content_path: Path,
    content: str,
    project_id: str,
    view_id: str,
    view_kind: str,
    sources: Iterable[Path],
    legacy_kind: str | None = None,
    source_content_overrides: dict[Path, bytes] | None = None,
    dedupe_store: Path | None = None,
) -> list[Path]:
    source_paths = [path.resolve() for path in sources]
    overrides = {
        path.resolve(): value for path, value in (source_content_overrides or {}).items()
    }
    digest = hashlib.sha256()
    source_refs: list[str] = []
    for path in source_paths:
        if not path.is_file():
            raise GovernanceError(f"DerivedView source is missing: {path}")
        digest.update(overrides.get(path, path.read_bytes()))
        try:
            source_refs.append(path.relative_to(root.parent).as_posix())
        except ValueError:
            source_refs.append(str(path))
    if dedupe_store is None:
        write_text(content_path, content)
    else:
        write_content_addressed(content_path, content, dedupe_store)
    try:
        content_ref = content_path.resolve().relative_to(root.parent).as_posix()
    except ValueError:
        content_ref = str(content_path.resolve())
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "meta_type": "DerivedView",
        "project_id": project_id,
        "view_id": view_id,
        "view_kind": view_kind,
        "legacy_kind": legacy_kind,
        "generated_at": now_utc(),
        "generator": "run-governed-product-workflow/scripts/governance_artifacts.py",
        "source_snapshot": digest.hexdigest(),
    }
    if overrides:
        envelope["source_snapshot_method"] = "retrieval-contract-projection-v1"
    envelope.update({
        "sources": source_refs,
        "content_ref": content_ref,
        "integrity_status": "Complete",
    })
    require_valid_json_document(envelope, "derived-view.schema.json", view_id)
    envelope_path = content_path.with_suffix(content_path.suffix + ".view.json")
    atomic_write_json(envelope_path, envelope)
    return [content_path, envelope_path]


def generate_views(
    project_root: Path,
    *,
    project_id: str,
    profile_index: Path,
    mapping_path: Path | None = None,
) -> list[Path]:
    state_path = rebuild_project_state(project_root, project_id)
    state = read_json(state_path)
    root = governance_root(project_root)
    generated = root / "generated"
    outputs: list[Path] = []
    status_path = generated / "reviews" / "project-status.md"
    outputs.extend(_write_derived_view(
        root=root,
        content_path=status_path,
        content=render_project_status(state),
        project_id=project_id,
        view_id=f"DV-{project_id}-STATUS",
        view_kind="project-status-review",
        sources=[state_path],
    ))
    tasks_root = root / "tasks"
    if tasks_root.exists():
        for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
            before_path = task_dir / "before.json"
            minimal_path = task_dir / "task-record.json"
            if minimal_path.is_file():
                from minimal_task import render_minimal_review, require_valid_minimal_record

                record = read_json(minimal_path)
                require_valid_minimal_record(record, task_dir=task_dir)
                if record.get("project_id") != project_id:
                    continue
                review_path = generated / "reviews" / f"{record['task_id']}.md"
                outputs.extend(_write_derived_view(
                    root=root,
                    content_path=review_path,
                    content=render_minimal_review(record),
                    project_id=project_id,
                    view_id=f"DV-{record['task_id']}-REVIEW",
                    view_kind="task-review",
                    sources=[minimal_path],
                ))
                continue
            if not before_path.exists():
                continue
            before = read_json(before_path)
            if before.get("project_id") != project_id:
                continue
            after_path = task_dir / "after.json"
            after = read_json(after_path) if after_path.exists() else None
            review_path = generated / "reviews" / f"{before['task_id']}.md"
            sources = [before_path, task_dir / "run.jsonl"]
            if after is not None:
                sources.append(after_path)
            outputs.extend(_write_derived_view(
                root=root,
                content_path=review_path,
                content=render_task_review(before, after),
                project_id=project_id,
                view_id=f"DV-{project_id}-{before['task_id']}",
                view_kind="task-review",
                sources=sources,
            ))
    profiles = resolve_all_profiles(profile_index, mapping_path)
    mapping_report = generated / "matrices" / "legacy-137-to-meta-types.md"
    outputs.extend(_write_derived_view(
        root=root,
        content_path=mapping_report,
        content=render_legacy_mapping(profiles),
        project_id=project_id,
        view_id=f"DV-{project_id}-LEGACY-MAP",
        view_kind="legacy-profile-mapping",
        sources=[profile_index, mapping_path or default_mapping_path()],
    ))
    return outputs


def _canonical_digest(value: Any) -> str:
    def normalize(item: Any) -> Any:
        if isinstance(item, str):
            return unicodedata.normalize("NFC", item)
        if isinstance(item, list):
            return [normalize(child) for child in item]
        if isinstance(item, dict):
            return {str(key): normalize(child) for key, child in item.items()}
        return item

    payload = json.dumps(
        normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def retrieval_contract_projection_bytes(before: dict[str, Any]) -> bytes:
    """Bind retrieval to material TaskContract content, excluding run-start freeze fields."""

    projected = {
        key: value
        for key, value in before.items()
        if key not in {"lifecycle_state", "frozen_at"}
    }
    payload = {
        "projection_version": "retrieval-contract-projection-v1",
        "excluded_fields": ["frozen_at", "lifecycle_state"],
        "task_contract": projected,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def retrieval_contract_reference(before_path: Path, before: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "task-contract",
        "path": str(before_path.resolve()),
        "sha256": hashlib.sha256(retrieval_contract_projection_bytes(before)).hexdigest(),
        "digest_kind": "retrieval-contract-projection-v1",
        "excluded_fields": ["frozen_at", "lifecycle_state"],
    }


def validate_retrieval_plan(task_dir: Path, plan_path: Path | None = None) -> list[str]:
    """Validate the active-task hand-off from a frozen Norm Packet to bounded queries."""

    errors: list[str] = []
    task_dir = task_dir.resolve()
    before_path = task_dir / "before.json"
    try:
        before = read_json(before_path)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return [f"cannot validate retrieval plan: {exc}"]
    resolution = before.get("tailoring_resolution")
    if not isinstance(resolution, dict):
        return ["retrieval plan requires before.tailoring_resolution"]
    stage = resolution.get("stage")
    project_root = task_dir.parents[2]
    expected_dir = governance_root(project_root) / "generated" / "contexts" / task_dir.name / str(stage)
    expected_path = expected_dir / "retrieval-plan.json"
    candidate = (plan_path or expected_path).resolve()
    if candidate != expected_path.resolve():
        return [f"retrieval plan must use the canonical path: {expected_path}"]
    if not candidate.is_file():
        return [f"missing retrieval plan: {candidate}"]
    envelope_path = candidate.with_suffix(candidate.suffix + ".view.json")
    if not envelope_path.is_file():
        return [f"missing retrieval plan envelope: {envelope_path}"]
    try:
        plan = read_json(candidate)
        envelope = read_json(envelope_path)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return [str(exc)]

    expected_scalars = {
        "schema_version": SCHEMA_VERSION,
        "plan_version": "1.0",
        "plan_type": "bounded-norm-retrieval",
        "project_id": before.get("project_id"),
        "task_id": before.get("task_id"),
        "stage": stage,
        "status": "ShadowReady",
    }
    for field, expected in expected_scalars.items():
        if plan.get(field) != expected:
            errors.append(f"retrieval plan field is stale or invalid: {field}")
    if plan.get("activation") != {
        "mode": "Shadow", "release_authorized": False, "remote_semantic_enabled": False
    }:
        errors.append("retrieval plan activation must remain unreleased local Shadow mode")
    expected_source_ids = [
        item.get("source_id")
        for item in resolution.get("complete_source_files", [])
        if isinstance(item, dict)
    ]
    expected_boundary = {
        "tailoring_resolution_sha256": _canonical_digest(resolution),
        "normative_sources_sha256": resolution.get("normative_sources_sha256"),
        "source_ids": expected_source_ids,
    }
    if plan.get("source_boundary") != expected_boundary:
        errors.append("retrieval plan source boundary is stale")

    taxonomy_path = runtime_asset_path("mappings/norm-action-taxonomy.json")
    query_schema_path = schema_path("norm-query.schema.json")
    result_schema_path = schema_path("norm-query-result.schema.json")
    skill_root = skill_root_path().resolve()
    expected_inputs = [
        ("task-contract", before_path),
        ("norm-packet-json", expected_dir / "norm-packet.json"),
        ("norm-packet-markdown", expected_dir / "norm-packet.md"),
        ("complete-source-pack", expected_dir / "norm-source-pack.md"),
        ("action-taxonomy", taxonomy_path),
        ("query-schema", query_schema_path),
        ("query-result-schema", result_schema_path),
        ("query-runtime", skill_root / "scripts" / "query_norm_context.py"),
        ("compiler", skill_root / "scripts" / "compile_norm_context.py"),
        ("governance-runtime", skill_root / "scripts" / "governance_artifacts.py"),
    ]
    actual_inputs = plan.get("inputs")
    if not isinstance(actual_inputs, list) or len(actual_inputs) != len(expected_inputs):
        errors.append("retrieval plan inputs are incomplete")
    else:
        for item, (role, expected_path_item) in zip(actual_inputs, expected_inputs):
            expected_path_item = expected_path_item.resolve()
            if not expected_path_item.is_file():
                errors.append(f"retrieval plan input is missing: {role}")
                continue
            expected = (
                retrieval_contract_reference(before_path, before)
                if role == "task-contract"
                else {
                    "role": role,
                    "path": str(expected_path_item),
                    "sha256": hashlib.sha256(expected_path_item.read_bytes()).hexdigest(),
                }
            )
            if item != expected:
                errors.append(f"retrieval plan input is stale or invalid: {role}")

    try:
        taxonomy = read_json(taxonomy_path)
        expected_actions = [
            {
                "action": action_id,
                "required_control_types": definition["required_control_types"],
                "pinned_control_types": definition["pinned_control_types"],
            }
            for action_id, definition in sorted(taxonomy["actions"].items())
            if stage in definition["stages"]
        ]
    except (OSError, json.JSONDecodeError, GovernanceError, KeyError, TypeError) as exc:
        errors.append(f"cannot validate retrieval action taxonomy: {exc}")
        expected_actions = []
    if plan.get("allowed_actions") != expected_actions:
        errors.append("retrieval plan allowed_actions are stale")
    expected_template = {
        "schema_version": SCHEMA_VERSION,
        "task_id": before.get("task_id"),
        "stage": stage,
        "action": None,
        "query_text": None,
        "tailoring_resolution_sha256": expected_boundary["tailoring_resolution_sha256"],
        "normative_sources_sha256": resolution.get("normative_sources_sha256"),
        "budget_profile": "standard",
        "modes": ["exact", "fts"],
        "requested_additional_control_types": [],
    }
    if plan.get("request_template") != expected_template:
        errors.append("retrieval plan request_template is stale or unsafe")
    if plan.get("required_agent_inputs") != ["action", "query_text"]:
        errors.append("retrieval plan must require only action and query_text")
    if plan.get("fallback_chain") != [
        "clause", "parent-section", "complete-source", "ordered-source-pages", "blocked"
    ]:
        errors.append("retrieval plan fallback chain is invalid")
    if plan.get("source_pack_retained") is not True:
        errors.append("retrieval plan must retain the complete Source Pack")
    diagnostic = plan.get("diagnostic_fallback")
    if not isinstance(diagnostic, dict) or diagnostic.get("tool") != "rg" or "Blocked" not in diagnostic.get("cannot_bypass", []):
        errors.append("retrieval plan diagnostic fallback can bypass a blocker")

    envelope_errors = validate_json_document(envelope, "derived-view.schema.json", "retrieval-plan envelope")
    errors.extend(envelope_errors)
    source_paths = [path.resolve() for _, path in expected_inputs]
    digest = hashlib.sha256()
    expected_refs: list[str] = []
    for role_and_path in expected_inputs:
        role, source_path = role_and_path
        source_path = source_path.resolve()
        if source_path.is_file():
            digest.update(
                retrieval_contract_projection_bytes(before)
                if role == "task-contract"
                else source_path.read_bytes()
            )
        try:
            expected_refs.append(source_path.relative_to(project_root).as_posix())
        except ValueError:
            expected_refs.append(str(source_path))
    try:
        content_ref = candidate.relative_to(project_root).as_posix()
    except ValueError:
        content_ref = str(candidate)
    expected_envelope = {
        "project_id": before.get("project_id"),
        "view_id": f"DV-{before.get('project_id')}-{before.get('task_id')}-{stage}-RETRIEVAL-PLAN",
        "view_kind": "compiled-norm-retrieval-plan",
        "legacy_kind": None,
        "generator": "run-governed-product-workflow/scripts/governance_artifacts.py",
        "source_snapshot": digest.hexdigest(),
        "source_snapshot_method": "retrieval-contract-projection-v1",
        "sources": expected_refs,
        "content_ref": content_ref,
        "integrity_status": "Complete",
    }
    mismatches = [key for key, value in expected_envelope.items() if envelope.get(key) != value]
    if mismatches:
        errors.append("retrieval plan envelope is stale: " + ", ".join(mismatches))
    return errors


def validate_task_directory(task_dir: Path) -> list[str]:
    errors: list[str] = []
    before_path = task_dir / "before.json"
    ledger_path = task_dir / "run.jsonl"
    after_path = task_dir / "after.json"
    minimal_path = task_dir / "task-record.json"
    if minimal_path.is_file():
        conflicting = [
            path.name
            for path in (before_path, ledger_path, after_path)
            if path.exists()
        ]
        if conflicting:
            return [
                "active Minimal and default carriers must not coexist: "
                + ", ".join(conflicting)
            ]
        try:
            from minimal_task import validate_minimal_record

            return validate_minimal_record(read_json(minimal_path), task_dir=task_dir)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            return [str(exc)]
    if not before_path.is_file():
        return [f"missing {before_path}"]
    try:
        before = read_json(before_path)
    except (OSError, json.JSONDecodeError, GovernanceError) as exc:
        return [str(exc)]
    errors.extend(validate_json_document(before, "task-before.schema.json", "before"))
    if before.get("task_id") != task_dir.name:
        errors.append("before.task_id must match the task directory name")
    errors.extend(validate_artifact_manifest(before.get("artifact_manifest"), terminal=False))
    profile = before.get("task_profile", {})
    if isinstance(profile, dict):
        development_types = profile.get("development_types")
        if isinstance(development_types, list) and profile.get("primary_development_type") not in development_types:
            errors.append("before.task_profile.primary_development_type must be included in development_types")
    if after_path.exists():
        errors.extend(validate_historical_tailoring_sources(before))
    else:
        errors.extend(validate_tailoring_resolution(before))
        if isinstance(before.get("first_principles_analysis"), dict):
            try:
                from manage_project_docs import validate_project_document_layout

                errors.extend(
                    "project document layout: " + item
                    for item in validate_project_document_layout(task_dir.parents[2])
                )
            except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
                errors.append(f"project document layout validation failed: {exc}")
    dependencies = before.get("depends_on")
    if isinstance(dependencies, list) and before.get("task_id") in dependencies:
        errors.append("before task cannot depend on itself")
    try:
        events = read_jsonl(ledger_path)
    except GovernanceError as exc:
        errors.append(str(exc))
        events = []
    errors.extend(validate_run_lifecycle(before, events, terminal_required=False))
    if events and (before.get("lifecycle_state") != "Frozen" or not before.get("frozen_at")):
        errors.append("a task with run events must have lifecycle_state Frozen and frozen_at")
    if after_path.exists():
        try:
            after = read_json(after_path)
        except (OSError, json.JSONDecodeError, GovernanceError) as exc:
            errors.append(str(exc))
        else:
            errors.extend(validate_json_document(after, "task-after.schema.json", "after"))
            errors.extend(
                validate_artifact_manifest(
                    after.get("artifact_manifest"),
                    terminal=True,
                    before_manifest=before.get("artifact_manifest") if isinstance(before.get("artifact_manifest"), list) else None,
                )
            )
            for key in ("project_id", "work_item_id", "task_id"):
                if after.get(key) != before.get(key):
                    errors.append(f"before and after {key} must match")
            execution_required = after.get("status") == "Implemented" or bool(after.get("actual_changes"))
            errors.extend(
                validate_run_lifecycle(before, events, terminal_required=execution_required or bool(events))
            )
            if after.get("status") == "Implemented":
                checks = after.get("verification", [])
                if not events or events[-1].get("status") != "succeeded":
                    errors.append("Implemented outcome requires a succeeded run_finished event")
                if not any(
                    event.get("event_type") == "verification" and event.get("status") == "succeeded"
                    for event in events
                ):
                    errors.append("Implemented outcome requires a succeeded verification RunLedger event")
                if not any(item.get("result") == "Passed" for item in checks if isinstance(item, dict)):
                    errors.append("Implemented outcome requires at least one Passed verification")
                if any(
                    item.get("result") == "Passed" and not item.get("evidence_refs")
                    for item in checks if isinstance(item, dict)
                ):
                    errors.append("Passed verification in an Implemented outcome requires evidence_refs")
                if any(
                    item.get("required", True) and item.get("result") in {"Failed", "Blocked"}
                    for item in checks if isinstance(item, dict)
                ):
                    errors.append("Implemented outcome contains a required Failed or Blocked verification")
    return errors
