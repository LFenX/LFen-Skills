#!/usr/bin/env python3
"""Compile and query the bounded norm context through one command."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from build_norm_index import load_sources
from governance_artifacts import GovernanceError, read_json
from minimal_task import require_valid_minimal_record
from query_norm_context import (
    atomic_write_json,
    execute_query,
    integrity_blockers,
    load_environment,
    query_digest,
    validate_query_request,
    write_query_outputs,
)


def project_root_from_task_dir(task_dir: Path) -> Path:
    resolved = task_dir.resolve()
    if resolved.parent.name != "tasks" or resolved.parent.parent.name != ".project-governance":
        raise GovernanceError("task directory must be .project-governance/tasks/<TaskID>")
    return resolved.parent.parent.parent


def compile_context(task_dir: Path) -> None:
    before = read_json(task_dir / "before.json")
    resolution = before.get("tailoring_resolution", {})
    stage = resolution.get("stage")
    if not isinstance(stage, str):
        raise GovernanceError("TaskContract has no tailoring_resolution.stage")
    command = [
        sys.executable,
        str(Path(__file__).resolve().with_name("compile_norm_context.py")),
        "--task-dir",
        str(task_dir),
        "--stage",
        stage,
        "--enforce",
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        detail = (completed.stdout + completed.stderr).strip()
        raise GovernanceError(f"context compilation failed: {detail}")


def load_environment_with_compile(task_dir: Path):
    try:
        return load_environment(task_dir)
    except GovernanceError as exc:
        message = str(exc)
        stale_markers = (
            "retrieval plan is invalid",
            "canonical Norm Packet",
            "Norm Packet",
            "retrieval plan",
        )
        if not any(marker in message for marker in stale_markers):
            raise
    compile_context(task_dir)
    return load_environment(task_dir)


def request_from_plan(task_dir: Path, environment: Any, *, action: str, query_text: str) -> dict[str, Any]:
    stage = environment.task_contract["tailoring_resolution"]["stage"]
    plan_path = (
        project_root_from_task_dir(task_dir)
        / ".project-governance"
        / "generated"
        / "contexts"
        / str(environment.task_contract["task_id"])
        / stage
        / "retrieval-plan.json"
    )
    plan = read_json(plan_path)
    request = dict(plan.get("request_template", {}))
    request["action"] = action
    request["query_text"] = query_text
    return validate_query_request(request, environment)


def maybe_print_update_available(environment: Any) -> None:
    try:
        _, current_digest = load_sources()
    except Exception:
        return
    index_digest = environment.index_metadata.get("normative_sources_sha256")
    if isinstance(index_digest, str) and index_digest != current_digest:
        print(
            f"UPDATE_AVAILABLE current_normative_sources_sha256={current_digest} index_normative_sources_sha256={index_digest}",
            file=sys.stderr,
        )


def write_request(task_dir: Path, environment: Any, request: dict[str, Any]) -> Path:
    digest = query_digest(request, environment)
    root = project_root_from_task_dir(task_dir)
    request_path = (
        root
        / ".project-governance"
        / "generated"
        / "requests"
        / str(environment.task_contract["task_id"])
        / f"{digest}.json"
    )
    atomic_write_json(request_path, request)
    return request_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--query-text", required=True)
    return parser


def should_skip_for_minimal(task_dir: Path) -> bool:
    before_path = task_dir / "before.json"
    minimal_path = task_dir / "task-record.json"
    if before_path.is_file():
        if minimal_path.is_file():
            print(
                "WARNING: task-record.json exists beside before.json; using the full carrier and ignoring the stray Minimal record.",
                file=sys.stderr,
            )
        return False
    if not minimal_path.is_file():
        raise GovernanceError("task directory has neither task-record.json nor before.json")
    record = read_json(minimal_path)
    require_valid_minimal_record(record, task_dir=task_dir)
    lifecycle = record.get("lifecycle_state")
    if lifecycle in {"Ready", "Frozen"}:
        print("Minimal skips bounded norm query; eligibility facts are recorded in task-record.json.")
        return True
    if lifecycle == "Upgraded":
        raise GovernanceError(
            "Minimal carrier is Upgraded; complete the full carrier with init_task.py "
            "--upgrade-minimal-reason and --upgrade-minimal-basis before executing."
        )
    if lifecycle == "Completed":
        raise GovernanceError("Minimal carrier is Completed; no active Minimal execution remains")
    raise GovernanceError(f"Minimal carrier lifecycle_state is not executable: {lifecycle}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        task_dir = args.task_dir.resolve()
        if should_skip_for_minimal(task_dir):
            return 0
        environment = load_environment_with_compile(task_dir)
        maybe_print_update_available(environment)
        request = request_from_plan(
            task_dir,
            environment,
            action=args.action,
            query_text=args.query_text,
        )
        blockers = integrity_blockers(request, environment)
        if blockers:
            print("Blocked: " + "; ".join(sorted(set(blockers))))
            return 3
        request_path = write_request(task_dir, environment, request)
        result = execute_query(request, environment)
        outputs = write_query_outputs(environment, request_path, request, result, None)
        context_path = next(path for path in outputs if path.name == "clause-context.md")
        if result["status"] == "Blocked":
            print("Blocked: " + "; ".join(result["blocker_reasons"]))
            return 3
        print(context_path.read_text(encoding="utf-8"), end="")
        return 0
    except (GovernanceError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
