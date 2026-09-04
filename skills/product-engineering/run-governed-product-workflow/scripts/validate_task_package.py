#!/usr/bin/env python3
"""Validate V6.3 task artifacts and legacy V6.2 task-package input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from governance_artifacts import (
    default_profile_index_path,
    GovernanceError,
    META_TYPES,
    resolve_all_profiles,
    validate_embedded_manifest,
    validate_retrieval_plan,
    validate_task_directory,
)


RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
MODES = {"Normal", "Emergency"}
CONFIDENCE_LEVELS = {"Low", "Medium", "High"}
ARTIFACT_ACTIONS = {"Create/Revise", "Reference", "Generate", "On Event", "N/A"}
EXTENSION_STATES = {
    "Not Evaluated",
    "Pending",
    "Inactive",
    "Conditionally Active",
    "Active",
    "Retiring",
    "Retired",
}
EXTENSIONS = {"E01", "E02", "E03", "E04", "E05"}
QUERY_PUBLICATION_FILES = frozenset({
    "query-result.json",
    "query-result.json.view.json",
    "clause-context.md",
    "clause-context.md.view.json",
})


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def inspect_active_query_tree(
    query_root: Path,
    *,
    required: bool = False,
) -> tuple[list[Path], list[Path]]:
    """Inventory one active query tree without using a publication file as its entry point."""

    declared_root = query_root.absolute()
    if not declared_root.exists():
        if required:
            raise GovernanceError(f"active query root is missing: {declared_root}")
        return [], []
    if _is_link_or_junction(declared_root):
        raise GovernanceError(f"active query root must not be a link or junction: {declared_root}")
    for ancestor in declared_root.parents:
        if _is_link_or_junction(ancestor):
            raise GovernanceError(
                f"active query root resolves through a linked ancestor: {ancestor}"
            )
    query_root = declared_root.resolve()
    if not query_root.is_dir():
        raise GovernanceError(f"active query root is not a directory: {query_root}")
    root_entries = sorted(query_root.iterdir(), key=lambda path: path.name)
    if not root_entries:
        raise GovernanceError(f"active query root is empty: {query_root}")

    requests_root = query_root / "requests"
    request_files: list[Path] = []
    if requests_root.exists():
        if _is_link_or_junction(requests_root):
            raise GovernanceError(
                f"active query request registry must not be a link or junction: {requests_root}"
            )
        if not requests_root.is_dir():
            raise GovernanceError(f"active query request registry is not a directory: {requests_root}")
        request_entries = sorted(requests_root.iterdir(), key=lambda path: path.name)
        if not request_entries:
            raise GovernanceError(f"active query request registry is empty: {requests_root}")
        for entry in request_entries:
            if _is_link_or_junction(entry):
                raise GovernanceError(f"active query request must not be a link: {entry}")
            if not entry.is_file() or entry.suffix.lower() != ".json":
                raise GovernanceError(f"active query request registry has an invalid entry: {entry}")
            request_files.append(entry.resolve())

    publication_results: list[Path] = []

    def inspect_publication_node(directory: Path) -> None:
        if _is_link_or_junction(directory):
            raise GovernanceError(
                f"active query publication directory must not be a link or junction: {directory}"
            )
        try:
            directory.resolve().relative_to(query_root)
        except ValueError as exc:
            raise GovernanceError(f"active query publication escapes its task root: {directory}") from exc
        entries = sorted(directory.iterdir(), key=lambda path: path.name)
        if not entries:
            raise GovernanceError(f"active query publication directory is empty: {directory}")
        linked = [entry for entry in entries if _is_link_or_junction(entry)]
        if linked:
            raise GovernanceError(f"active query publication must not contain links: {linked[0]}")
        files = [entry for entry in entries if entry.is_file()]
        directories = [entry for entry in entries if entry.is_dir()]
        invalid = [entry for entry in entries if not entry.is_file() and not entry.is_dir()]
        if invalid:
            raise GovernanceError(f"active query publication has an invalid entry: {invalid[0]}")
        if files:
            actual_names = {entry.name for entry in files}
            if directories or actual_names != QUERY_PUBLICATION_FILES:
                raise GovernanceError(f"active query publication is partial or has unexpected entries: {directory}")
            publication_results.append((directory / "query-result.json").resolve())
            return
        for child in directories:
            inspect_publication_node(child)

    for entry in root_entries:
        if entry.name == "requests":
            continue
        if not entry.is_dir():
            raise GovernanceError(f"active query root has an unexpected entry: {entry}")
        inspect_publication_node(entry)

    if request_files and not publication_results:
        raise GovernanceError("active query requests have no published query output")
    if publication_results and not request_files:
        raise GovernanceError("active query publications have no request registry")
    return request_files, publication_results


def validate_active_query_publications(
    task_dir: Path,
    *,
    required: bool = False,
) -> list[str]:
    """Validate structure, replayability, and request coverage for an active task."""

    errors: list[str] = []
    task_dir = task_dir.resolve()
    query_root = (
        task_dir.parents[2]
        / ".project-governance"
        / "generated"
        / "queries"
        / task_dir.name
    )
    try:
        request_files, result_paths = inspect_active_query_tree(query_root, required=required)
        if not request_files and not result_paths:
            return []
        from query_norm_context import validate_query_output_directory

        registered = {path.resolve() for path in request_files}
        covered: set[Path] = set()
        project_root = task_dir.parents[2].resolve()
        for result_path in result_paths:
            validate_query_output_directory(task_dir, result_path)
            envelope = load_json(result_path.with_suffix(result_path.suffix + ".view.json"))
            sources = envelope.get("sources")
            if not isinstance(sources, list) or not sources or not isinstance(sources[0], str):
                raise GovernanceError(f"active query result envelope has no request source: {result_path}")
            request_path = Path(sources[0])
            if not request_path.is_absolute():
                request_path = project_root / request_path
            request_path = request_path.resolve()
            if request_path not in registered:
                raise GovernanceError(
                    f"active query publication references an unregistered request: {request_path}"
                )
            covered.add(request_path)
        uncovered = sorted(registered - covered, key=lambda path: str(path))
        if uncovered:
            raise GovernanceError(f"active query request has no publication: {uncovered[0]}")
    except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        errors.append(str(exc))
    return errors

def default_profile_index() -> Path:
    return default_profile_index_path()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        help="Task directory, before/after JSON path, or legacy task-package JSON path.",
    )
    parser.add_argument(
        "--check-mapping",
        action="store_true",
        help="Validate six meta types and complete 137-profile compatibility mapping.",
    )
    parser.add_argument(
        "--execution-ready",
        action="store_true",
        help="Additionally require an S4-or-later blocker-free tailoring resolution.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GovernanceError(f"{path}: top-level JSON value must be an object")
    return value


def require_nonempty_list(owner: dict[str, Any], field: str, errors: list[str]) -> list[Any]:
    value = owner.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"task_profile.{field} must be a non-empty array")
        return []
    return value


def validate_legacy_package(
    package: dict[str, Any], legacy_profiles: set[str]
) -> list[str]:
    errors: list[str] = []
    profile = package.get("task_profile")
    manifest = package.get("artifact_manifest")
    if not isinstance(profile, dict):
        return ["task_profile must be an object"]
    if not isinstance(manifest, list):
        return ["artifact_manifest must be an array"]
    scenario = profile.get("delivery_scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        errors.append("task_profile.delivery_scenario must be a non-empty string")
    require_nonempty_list(profile, "development_types", errors)
    require_nonempty_list(profile, "change_surfaces", errors)
    require_nonempty_list(profile, "basis", errors)
    if not isinstance(profile.get("baseline_inheritance"), list):
        errors.append("task_profile.baseline_inheritance must be an array")
    if profile.get("risk_level") not in RISK_LEVELS:
        errors.append(f"task_profile.risk_level must be one of {sorted(RISK_LEVELS)}")
    if profile.get("mode") not in MODES:
        errors.append(f"task_profile.mode must be one of {sorted(MODES)}")
    if profile.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append(
            f"task_profile.confidence must be one of {sorted(CONFIDENCE_LEVELS)}"
        )
    if not isinstance(profile.get("open_questions"), list):
        errors.append("task_profile.open_questions must be an array")
    triggers = profile.get("extension_triggers")
    if not isinstance(triggers, dict):
        errors.append("task_profile.extension_triggers must be an object")
    else:
        if set(triggers) != EXTENSIONS:
            errors.append("task_profile.extension_triggers must contain exactly E01-E05")
        for extension, state in triggers.items():
            if state not in EXTENSION_STATES:
                errors.append(
                    f"task_profile.extension_triggers.{extension} has invalid state {state!r}"
                )
    seen: set[str] = set()
    for position, item in enumerate(manifest):
        prefix = f"artifact_manifest[{position}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        legacy_kind = item.get("legacy_kind", item.get("artifact_type_id"))
        if legacy_kind not in legacy_profiles:
            errors.append(f"{prefix}.legacy_kind is not in the compatibility profile catalog")
        elif legacy_kind in seen:
            errors.append(f"{prefix}.legacy_kind duplicates {legacy_kind}")
        else:
            seen.add(legacy_kind)
        if item.get("action") not in ARTIFACT_ACTIONS:
            errors.append(f"{prefix}.action must be one of {sorted(ARTIFACT_ACTIONS)}")
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{prefix}.reason must be a non-empty string")
        if item.get("action") == "N/A" and not item.get("rule_reference"):
            errors.append(f"{prefix}.rule_reference is required when action is N/A")
    return errors


def main() -> int:
    args = parse_args()
    before_for_readiness: dict[str, Any] | None = None
    minimal_for_readiness: dict[str, Any] | None = None
    task_dir_for_validation: Path | None = None
    try:
        manifest_errors = validate_embedded_manifest()
        if manifest_errors:
            raise GovernanceError("; ".join(manifest_errors))
        profiles = resolve_all_profiles(default_profile_index())
        if args.check_mapping:
            counts: dict[str, int] = {meta_type: 0 for meta_type in sorted(META_TYPES)}
            for profile in profiles:
                counts[profile["meta_type"]] = counts.get(profile["meta_type"], 0) + 1
            print(
                "VALID MAPPING: 6 meta types; "
                f"{len(profiles)}/137 legacy profiles resolved; counts={counts}"
            )
            if not args.input:
                return 0
        if not args.input:
            raise GovernanceError("input is required unless --check-mapping is used")
        target = Path(args.input)
        if target.is_dir():
            errors = validate_task_directory(target)
            minimal_path = target / "task-record.json"
            if minimal_path.is_file():
                mode = "V6.3 Minimal aggregate task directory"
                minimal_for_readiness = load_json(minimal_path)
            else:
                mode = "V6.3 default task directory"
                before_for_readiness = load_json(target / "before.json")
            task_dir_for_validation = target.resolve()
        else:
            package = load_json(target)
            if package.get("carrier_mode") == "Minimal":
                from minimal_task import validate_minimal_record

                errors = validate_minimal_record(package, task_dir=target.parent)
                mode = "V6.3 Minimal aggregate task directory"
                minimal_for_readiness = package
                task_dir_for_validation = target.parent.resolve()
            elif package.get("meta_type") in {"TaskContract", "TaskOutcome"}:
                errors = validate_task_directory(target.parent)
                mode = "V6.3 default task directory"
                before_for_readiness = load_json(target.parent / "before.json")
                task_dir_for_validation = target.parent.resolve()
            elif "task_profile" in package and "artifact_manifest" in package:
                if args.execution_ready:
                    raise GovernanceError("--execution-ready is available only for V6.3 TaskContract directories")
                errors = validate_legacy_package(
                    package, {item["legacy_kind"] for item in profiles}
                )
                mode = "legacy task package"
            else:
                raise GovernanceError(
                    f"{target}: unsupported input; expected a V6.3 task artifact or legacy task package"
                )
        if args.execution_ready and minimal_for_readiness is not None:
            if minimal_for_readiness.get("lifecycle_state") not in {"Ready", "Frozen"}:
                errors.append("Minimal execution readiness requires an active carrier")
            if minimal_for_readiness.get("upgrade", {}).get("required"):
                errors.append("Minimal execution readiness is blocked by a mandatory full-carrier upgrade")
        elif args.execution_ready and before_for_readiness is not None:
            resolution = before_for_readiness.get("tailoring_resolution", {})
            stage = resolution.get("stage") if isinstance(resolution, dict) else None
            if not isinstance(stage, str) or not stage.startswith("S") or int(stage[1:]) < 4:
                errors.append("execution readiness requires an S4-or-later tailoring resolution")
            blockers = resolution.get("blocking_reasons", []) if isinstance(resolution, dict) else []
            for blocker in blockers if isinstance(blockers, list) else ["tailoring blockers are invalid"]:
                errors.append(f"execution readiness blocker: {blocker}")
            if task_dir_for_validation is not None and not (task_dir_for_validation / "after.json").is_file():
                errors.extend(validate_retrieval_plan(task_dir_for_validation))
        if (
            minimal_for_readiness is None
            and task_dir_for_validation is not None
            and not (task_dir_for_validation / "after.json").is_file()
        ):
            errors.extend(
                f"active query output is invalid: {error}"
                for error in validate_active_query_publications(
                    task_dir_for_validation,
                    required=args.execution_ready,
                )
            )
    except (OSError, UnicodeError, json.JSONDecodeError, GovernanceError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    readiness = "EXECUTION READY" if args.execution_ready else "STRUCTURE VALID"
    print(f"{readiness}: {mode}; 6 meta types; 137 compatibility profiles available.")
    if not args.execution_ready and before_for_readiness is not None:
        blockers = before_for_readiness.get("tailoring_resolution", {}).get("blocking_reasons", [])
        if blockers:
            print(f"EXECUTION BLOCKED: {len(blockers)} tailoring blocker(s); rerun with --execution-ready for details.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
