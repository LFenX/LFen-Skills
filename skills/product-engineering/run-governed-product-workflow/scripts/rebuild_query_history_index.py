#!/usr/bin/env python3
"""Reconcile immutable query archives and the complete active publication set."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from governance_artifacts import (
    GovernanceError,
    atomic_write_json,
    now_utc,
    read_json,
    sha256_file,
    validate_query_history,
)


PUBLICATION_FILES = (
    "query-result.json",
    "query-result.json.view.json",
    "clause-context.md",
    "clause-context.md.view.json",
)
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--reconciled-at")
    return parser.parse_args()


def parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise GovernanceError("query publication time is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GovernanceError("query publication time is invalid") from exc
    if parsed.tzinfo is None:
        raise GovernanceError("query publication time must include a timezone")
    return parsed


def file_manifest(directory: Path) -> dict[str, str]:
    actual = {path.name for path in directory.iterdir() if path.is_file()}
    if actual != set(PUBLICATION_FILES):
        raise GovernanceError(f"query publication file set differs: {directory}")
    return {name: sha256_file(directory / name) for name in sorted(PUBLICATION_FILES)}


def main() -> int:
    args = parse_args()
    try:
        project_root = args.project_root.resolve()
        history_root = (
            project_root / ".project-governance" / "generated" /
            "query-history" / args.task_id
        ).resolve()
        active_root = (
            project_root / ".project-governance" / "generated" /
            "queries" / args.task_id
        ).resolve()
        if not active_root.is_dir():
            raise GovernanceError("active query root must exist")
        if history_root.exists() and not history_root.is_dir():
            raise GovernanceError("query history root must be a directory")
        history_root.mkdir(parents=True, exist_ok=True)
        index_path = history_root / "archive-index.json"
        previous = read_json(index_path) if index_path.is_file() else {}
        previous_by_digest = {
            item.get("query_digest"): item
            for item in previous.get("publications", [])
            if isinstance(item, dict)
        }
        reconciled_at = args.reconciled_at or now_utc()
        reconciled_time = parse_time(reconciled_at)

        publications: list[dict[str, Any]] = []
        redirects: list[dict[str, str]] = []
        for directory in sorted(history_root.iterdir(), key=lambda path: path.name):
            if not directory.is_dir() or not DIGEST_PATTERN.fullmatch(directory.name):
                continue
            files = file_manifest(directory)
            envelope = read_json(directory / "query-result.json.view.json")
            generated_at = envelope.get("generated_at")
            generated_time = parse_time(generated_at)
            previous_entry = previous_by_digest.get(directory.name, {})
            candidate_archived_at = previous_entry.get("archived_at")
            try:
                archived_time = parse_time(candidate_archived_at)
            except GovernanceError:
                archived_time = reconciled_time
                candidate_archived_at = reconciled_at
            if generated_time > archived_time:
                archived_time = reconciled_time
                candidate_archived_at = reconciled_at
            if generated_time > archived_time:
                raise GovernanceError("reconciled archive time predates publication generation")
            original_root = (
                project_root / ".project-governance" / "generated" /
                "queries" / args.task_id / directory.name
            )
            archived_ref = directory.relative_to(project_root).as_posix()
            original_ref = original_root.relative_to(project_root).as_posix()
            publications.append(
                {
                    "query_digest": directory.name,
                    "generated_at": generated_at,
                    "archived_at": candidate_archived_at,
                    "original_path": original_ref,
                    "archived_path": archived_ref,
                    "files": files,
                }
            )
            for name, file_sha256 in files.items():
                redirects.append(
                    {
                        "original_ref": f"{original_ref}/{name}",
                        "archived_ref": f"{archived_ref}/{name}",
                        "sha256": file_sha256,
                    }
                )

        archived_request_sets: list[dict[str, Any]] = []
        for directory in sorted(history_root.glob("requests-*"), key=lambda path: path.name):
            if not directory.is_dir():
                continue
            request_files = {
                path.name: sha256_file(path)
                for path in sorted(directory.iterdir(), key=lambda path: path.name)
                if path.is_file() and path.suffix.lower() == ".json"
            }
            if not request_files:
                raise GovernanceError(f"archived request set is empty: {directory}")
            archived_request_sets.append(
                {
                    "path": directory.relative_to(project_root).as_posix(),
                    "files": request_files,
                }
            )

        active_publications: list[dict[str, Any]] = []
        for directory in sorted(active_root.iterdir(), key=lambda path: path.name):
            if not directory.is_dir() or not DIGEST_PATTERN.fullmatch(directory.name):
                continue
            files = file_manifest(directory)
            result = read_json(directory / "query-result.json")
            envelope = read_json(directory / "query-result.json.view.json")
            if result.get("query_digest") != directory.name:
                raise GovernanceError("active query digest differs from its directory")
            sources = envelope.get("sources")
            if not isinstance(sources, list) or not sources or not isinstance(sources[0], str):
                raise GovernanceError("active query envelope has no request source")
            request_ref = sources[0]
            request_path = Path(request_ref)
            if not request_path.is_absolute():
                request_path = project_root / request_path
            request_path = request_path.resolve()
            if not request_path.is_file():
                raise GovernanceError("active query request is missing")
            request = read_json(request_path)
            active_publications.append(
                {
                    "query_digest": directory.name,
                    "task_id": args.task_id,
                    "action": request.get("action"),
                    "generated_at": envelope.get("generated_at"),
                    "result_path": (directory / "query-result.json").relative_to(
                        project_root
                    ).as_posix(),
                    "files": files,
                    "request_path": request_path.relative_to(project_root).as_posix(),
                    "request_sha256": sha256_file(request_path),
                }
            )
        if not active_publications:
            raise GovernanceError("active query publication set is empty")
        current = max(
            active_publications,
            key=lambda item: (parse_time(item["generated_at"]), item["result_path"]),
        )["result_path"]
        index = {
            "schema_version": "6.3-candidate",
            "task_id": args.task_id,
            "reconciled_at": reconciled_at,
            "reason": args.reason,
            "legacy_index_archived_at": previous.get("archived_at"),
            "publications": publications,
            "archived_request_sets": archived_request_sets,
            "evidence_redirects": sorted(redirects, key=lambda item: item["original_ref"]),
            "active_publications": active_publications,
            "current_active_query_result": current,
        }
        atomic_write_json(index_path, index)
        result = validate_query_history(project_root, args.task_id)
        print(index_path)
        print(result)
        return 0
    except (OSError, UnicodeError, GovernanceError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
