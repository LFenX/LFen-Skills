#!/usr/bin/env python3
"""Finite, append-only accounting for an opted-in review session."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

DEFAULT_BUDGET = {"review_rounds": 3, "repair_batches": 2, "elapsed_minutes": 60}


def budget_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False,
            "required": list(DEFAULT_BUDGET),
            "properties": {key: {"type": "integer", "minimum": 1} for key in DEFAULT_BUDGET}}


def budget_state(records: list[dict], *, at: datetime | None = None) -> dict[str, Any]:
    """Replay grants and charged work. Failed/interrupted starts are not refunded."""
    from governance_artifacts import GovernanceError

    def instant(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    limits = None
    granted_at = None
    active = False
    used = {"review_rounds": 0, "repair_batches": 0}
    starts: dict[tuple[str, str], str] = {}
    finished: set[str] = set()
    seen: set[tuple[str, str]] = set()

    def exhausted(stamp: datetime) -> list[str]:
        if limits is None:
            return []
        reasons = [key for key, value in used.items() if value >= limits[key]]
        if stamp >= granted_at + timedelta(minutes=limits["elapsed_minutes"]):
            reasons.append("elapsed_minutes")
        return reasons

    for item in records:
        kind = item["event"]
        stamp = instant(item["recorded_at"])
        if kind == "Decision":
            active = item["outcome"] == "Accepted"
            if active:
                limits = item.get("budget")
                granted_at = stamp
                used = {"review_rounds": 0, "repair_batches": 0}
                starts, finished = {}, set()
        elif kind == "Offer":
            active = False
        elif kind == "WorkStarted":
            if not active or limits is None:
                raise GovernanceError("work requires an explicit user decision with a finite budget")
            if exhausted(stamp):
                raise GovernanceError("review budget exhausted; summarize and wait for a real new user decision")
            key = (item["work_type"], item["work_id"])
            if key in seen:
                raise GovernanceError("each charged work start requires a fresh id; interrupted work is not refunded")
            seen.add(key)
            starts[key] = item["recorded_at"]
            used["review_rounds" if key[0] == "Review" else "repair_batches"] += 1
        elif kind == "Round" and active and limits is not None:
            key = ("Review", item["round_id"])
            if key in starts:
                if instant(item["started_at"]) < instant(starts[key]):
                    raise GovernanceError("round cannot predate its charged start")
            else:
                # Older callers may submit completed reports without a start
                # receipt. Charge them too; omission cannot buy extra rounds.
                if exhausted(instant(item["started_at"])):
                    raise GovernanceError("review budget exhausted; no additional round may be recorded")
                used["review_rounds"] += 1
            finished.add(item["round_id"])

    if not active:
        return {"status": "Inactive"}
    if limits is None:
        return {"status": "BudgetRequired"}
    clock = at or datetime.now(timezone.utc)
    reasons = exhausted(clock)
    return {"status": "BudgetExhausted" if reasons else "Available",
            "limits": dict(limits), "used": dict(used),
            "remaining": {key: max(0, limits[key] - value) for key, value in used.items()},
            "deadline": (granted_at + timedelta(minutes=limits["elapsed_minutes"])).isoformat().replace("+00:00", "Z"),
            "exhausted_by": reasons,
            "pending_reviews": sorted(key[1] for key in starts if key[0] == "Review" and key[1] not in finished),
            "repair_tasks": sorted(key[1] for key in starts if key[0] == "Repair")}
