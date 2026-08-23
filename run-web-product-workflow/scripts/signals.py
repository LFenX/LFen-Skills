#!/usr/bin/env python3
"""Emit lightweight workflow signals without executing recommended commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from build_norm_index import load_sources
from governance_artifacts import GovernanceError, capture_source_snapshot, read_json


FACT_KEYS = (
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
    "migration_retirement",
    "external_system_effect",
    "formal_review_or_gate",
)


def governance_root(project_root: Path) -> Path:
    return project_root.resolve() / ".project-governance"


def task_dirs(project_root: Path) -> list[Path]:
    root = governance_root(project_root) / "tasks"
    if not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir())


def unknown_blockers(before: dict[str, Any]) -> list[str]:
    facts = before.get("task_profile", {}).get("applicability_facts", {})
    values = [
        f"{key}=Unknown"
        for key in FACT_KEYS
        if facts.get(key) == "Unknown"
    ]
    values.extend(before.get("tailoring_resolution", {}).get("blocking_reasons", []))
    return sorted(set(str(value) for value in values))


def full_carrier_signal(task_dir: Path, before: dict[str, Any], after_path: Path) -> dict[str, Any]:
    return {
        "task_id": before.get("task_id", task_dir.name),
        "carrier": "Full",
        "lifecycle_state": before.get("lifecycle_state"),
        "unknown_blockers": unknown_blockers(before) if not after_path.is_file() else [],
        "pending_acceptance": not after_path.is_file(),
        "minimal_eligibility": None,
        "upgrade_pending": False,
        "upgrade_reason": None,
    }


def active_task_signal(task_dir: Path) -> dict[str, Any] | None:
    before_path = task_dir / "before.json"
    minimal_path = task_dir / "task-record.json"
    after_path = task_dir / "after.json"
    if before_path.is_file():
        if minimal_path.is_file():
            print(
                "WARNING: task-record.json exists beside before.json; using the full carrier and ignoring the stray Minimal record.",
                file=sys.stderr,
            )
        return full_carrier_signal(task_dir, read_json(before_path), after_path)
    if not minimal_path.is_file():
        return None
    record = read_json(minimal_path)
    lifecycle = record.get("lifecycle_state")
    upgrade = record.get("upgrade") if isinstance(record.get("upgrade"), dict) else {}
    upgrade_pending = lifecycle == "Upgraded"
    terminal = lifecycle in {"Completed", "Upgraded"}
    blockers = []
    if upgrade_pending:
        reason = upgrade.get("reason") or "Minimal carrier requires one-way upgrade to the full carrier."
        blockers.append(f"minimal-upgrade-required:{reason}")
    return {
        "task_id": record.get("task_id", task_dir.name),
        "carrier": "Minimal",
        "lifecycle_state": lifecycle,
        "unknown_blockers": blockers,
        "pending_acceptance": False if terminal else record.get("task_outcome") is None,
        "minimal_eligibility": record.get("eligibility", {}),
        "upgrade_pending": upgrade_pending,
        "upgrade_reason": upgrade.get("reason") if upgrade_pending else None,
    }


def snapshot_stale(project_root: Path, task_dir: Path) -> dict[str, Any] | None:
    before_path = task_dir / "before.json"
    if not before_path.is_file():
        return None
    before = read_json(before_path)
    recorded = before.get("source_snapshot", {})
    try:
        current = capture_source_snapshot(project_root.resolve())
    except Exception as exc:
        return {"task_id": task_dir.name, "status": "unknown", "reason": str(exc)}
    mismatches = [
        key for key in ("head", "status_digest")
        if recorded.get(key) != current.get(key)
    ]
    if not mismatches:
        return None
    return {
        "task_id": before.get("task_id", task_dir.name),
        "status": "stale",
        "fields": mismatches,
        "recorded_head": recorded.get("head"),
        "current_head": current.get("head"),
    }


def update_available(project_root: Path) -> dict[str, Any] | None:
    cache_root = governance_root(project_root) / "runtime-cache"
    metadata_files = list(governance_root(project_root).rglob("norm-index-metadata.json"))
    metadata_files.extend(cache_root.rglob("norm-index-metadata.json") if cache_root.is_dir() else [])
    if not metadata_files:
        return None
    try:
        _, current_digest = load_sources()
    except Exception:
        return None
    stale = []
    for path in sorted(set(metadata_files)):
        try:
            metadata = read_json(path)
        except Exception:
            continue
        digest = metadata.get("normative_sources_sha256")
        if isinstance(digest, str) and digest != current_digest:
            stale.append({"path": str(path), "normative_sources_sha256": digest})
    if not stale:
        return None
    return {"current_normative_sources_sha256": current_digest, "stale_indexes": stale}


def recommendations(signals: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not signals:
        return [
            {"command": "init", "reason": "No governed task package exists."},
            {"command": "status", "reason": "Create or inspect project governance state first."},
        ]
    active = [item for item in signals if item.get("pending_acceptance")]
    if any(item.get("unknown_blockers") for item in active):
        return [
            {"command": "clarify", "reason": "Blocking Unknown facts remain open."},
            {"command": "plan", "reason": "Refresh TaskContract after facts are resolved."},
        ]
    if active:
        return [
            {"command": "run", "reason": "An active task is ready for execution or validation."},
            {"command": "verify", "reason": "Close evidence before acceptance."},
            {"command": "close", "reason": "Write TaskOutcome after verification."},
        ]
    if any(item.get("upgrade_pending") for item in signals):
        return [
            {"command": "init", "reason": "Complete the one-way Minimal to full-carrier upgrade with upgrade parameters."},
            {"command": "status", "reason": "Do not continue Minimal run, verify, or close while upgrade is pending."},
        ]
    return [
        {"command": "status", "reason": "No active task requires execution."},
        {"command": "init", "reason": "Start a new governed change if work remains."},
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser


# C10 8.2 relations carry opposite meanings for a review. A task whose successors
# are observed-from surfaced hidden problems -- that is the run doing its job. A task
# whose successors are affected-by created the work itself. Counting them together
# yields a number that cannot be reflected on, so the audit reports them apart and
# only follows affected-by when measuring how far a repair kept propagating.
NEGATIVE_RELATIONS = ("affected-by",)
POSITIVE_RELATIONS = ("observed-from",)


def derivation_audit(project_root: Path) -> dict[str, Any]:
    state_path = project_root / ".project-governance" / "project-state.json"
    if not state_path.is_file():
        return {"available": False, "reason": "project-state.json not built yet"}
    graph = read_json(state_path).get("task_graph", [])
    by_id = {node["task_id"]: node for node in graph}
    known = set(by_id)

    def chain_depth(task_id: str, relations: tuple[str, ...], seen: frozenset[str]) -> int:
        node = by_id.get(task_id)
        if node is None or task_id in seen:
            return 0
        deeper = [
            1 + chain_depth(link["task_id"], relations, seen | {task_id})
            for link in node.get("next_tasks", [])
            if link["relation"] in relations
        ]
        return max(deeper, default=0)

    counts: dict[str, int] = {}
    per_task = []
    dangling = []
    for node in graph:
        links = node.get("next_tasks", [])
        for link in links:
            counts[link["relation"]] = counts.get(link["relation"], 0) + 1
            if link["task_id"] not in known:
                dangling.append(
                    {"task_id": node["task_id"], "target": link["task_id"], "relation": link["relation"]}
                )
        if not links and not node.get("derived_from"):
            continue
        per_task.append(
            {
                "task_id": node["task_id"],
                "caused": sum(1 for link in links if link["relation"] in NEGATIVE_RELATIONS),
                "surfaced": sum(1 for link in links if link["relation"] in POSITIVE_RELATIONS),
                "derived_from": len(node.get("derived_from", [])),
                "caused_chain_depth": chain_depth(node["task_id"], NEGATIVE_RELATIONS, frozenset()),
            }
        )
    per_task.sort(key=lambda item: (-item["caused_chain_depth"], -item["caused"], item["task_id"]))
    return {
        "available": True,
        "relation_counts": dict(sorted(counts.items())),
        "by_task": per_task,
        "recorded_but_not_created": sorted(
            dangling, key=lambda item: (item["task_id"], item["target"])
        ),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        project_root = args.project_root.resolve()
        tasks = [item for item in (active_task_signal(path) for path in task_dirs(project_root)) if item]
        document = {
            "status": "Ready",
            "project_root": str(project_root),
            "blocking_unknowns": [
                {"task_id": item["task_id"], "unknowns": item["unknown_blockers"]}
                for item in tasks
                if item.get("unknown_blockers")
            ],
            "pending_acceptance_tasks": [
                item["task_id"] for item in tasks if item.get("pending_acceptance")
            ],
            "snapshot_stale": [
                item for item in (snapshot_stale(project_root, path) for path in task_dirs(project_root)) if item
            ],
            "minimal_eligibility_facts": [
                {"task_id": item["task_id"], "eligibility": item["minimal_eligibility"]}
                for item in tasks
                if item.get("minimal_eligibility") is not None
            ],
            "derivation_audit": derivation_audit(project_root),
            "update_available": update_available(project_root),
            "recommended_commands": recommendations(tasks),
        }
        print(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (GovernanceError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
