#!/usr/bin/env python3
"""Succession relation vocabulary and the derivation audit computed from ProjectState.

Imports nothing local, so signals.py, console_model.py and console_render.py can all
share one implementation. The single-page HTML report that used to live here was
replaced by the multi-page console in console.py.
"""

from __future__ import annotations

import json
from typing import Any


# C10 8.2 relation identities stay in the data; 8.3 rule 5 allows a display layer to
# label them for humans as long as the underlying link is not flipped.
RELATION_LABELS = {
    "affected-by": ["本次引入", "negative"],
    "observed-from": ["顺带发现", "positive"],
    "addresses": ["承接处理", "neutral"],
    "extends": ["后续增强", "neutral"],
    "refines": ["细化", "neutral"],
}

# C10 8.2 relations mean opposite things in review. Successors related by
# observed-from mean the run surfaced hidden problems; successors related by
# affected-by mean the run created the work. Chain depth follows only affected-by, so
# a repair that kept propagating is attributable to the task that started it while a
# task that merely found things is not penalised for it.
NEGATIVE_RELATIONS = ("affected-by",)
POSITIVE_RELATIONS = ("observed-from",)


def derivation_audit(state: dict[str, Any]) -> dict[str, Any]:
    """Compute the succession audit from a ProjectState document."""

    graph = state.get("task_graph", [])
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
    per_task: list[dict[str, Any]] = []
    dangling: list[dict[str, str]] = []
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
        "recorded_but_not_created": sorted(dangling, key=lambda item: (item["task_id"], item["target"])),
    }
