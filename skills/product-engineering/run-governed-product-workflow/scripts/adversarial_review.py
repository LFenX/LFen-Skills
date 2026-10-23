#!/usr/bin/env python3
"""Record opt-in adversarial reviews on saved Full or Minimal outcomes."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def review_schema() -> dict[str, Any]:
    """One schema definition, embedded into both existing outcome schemas."""
    text = {"type": "string", "minLength": 1}
    refs = {"type": "array", "minItems": 1, "uniqueItems": True, "items": text}
    strings = {"type": "array", "uniqueItems": True, "items": text}
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}

    def obj(properties: dict[str, Any]) -> dict[str, Any]:
        return {"type": "object", "additionalProperties": False,
                "required": list(properties), "properties": properties}

    variants = []
    details = {
        "Offer": {"prompt": text, "evidence_ref": text},
        "Decision": {"outcome": {"enum": ["Accepted", "Declined", "Deferred", "Stopped"]},
                     "response": text, "decided_by": text, "evidence_ref": text},
        "Blocked": {"reason": text, "evidence_refs": refs},
        "Round": {"round_id": text, "started_at": {"type": "string", "format": "date-time"},
                  "reviewer": text, "delivery_task_id": text, "subject_sha256": digest,
                  "requirements_sha256": digest, "coverage": {"enum": ["Complete", "Incomplete"]},
                  "unreviewed_items": strings, "evidence_refs": refs,
                  "findings": {"type": "array", "items": obj({"id": text, "summary": text,
                                                              "evidence_refs": refs})},
                  "resolutions": {"type": "array", "items": obj({"finding_id": text,
                     "disposition": {"enum": ["Fixed", "NotAnIssue"]}, "reason": text, "evidence_refs": refs})}},
    }
    for kind, properties in details.items():
        variants.append(obj({"event": {"const": kind},
                             "recorded_at": {"type": "string", "format": "date-time"}, **properties}))
    return {"type": "array", "items": {"oneOf": variants}}


def requirements_subject(contract: dict[str, Any]) -> str:
    raw = {"request_snapshot": contract.get("request_snapshot"),
           "clarification": contract.get("clarification")}
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def review_state(outcome: dict[str, Any], contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Replay actual records; a stored claim cannot override the clean streak."""
    from governance_artifacts import GovernanceError, validate_json_document

    records = outcome.get("adversarial_review")
    if records is None:
        return {"status": "LegacyUntracked", "clean_streak": 0, "rounds": 0, "open_findings": []}
    errors = validate_json_document(records, review_schema(), "adversarial_review")
    if errors:
        raise GovernanceError("; ".join(errors))
    status = "NotOffered" if outcome.get("status") == "Implemented" else "NotApplicable"
    streak = rounds = 0
    offered = accepted = False
    last_subject = None
    ids: set[str] = set()
    reports: set[str] = set()
    findings: dict[str, str] = {}
    all_findings: set[str] = set()

    def instant(value: Any) -> datetime:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise GovernanceError("adversarial review requires real timezone-aware timestamps") from exc
        if parsed.tzinfo is None or parsed > datetime.now(timezone.utc):
            raise GovernanceError("adversarial review time must include timezone and must not be in the future")
        return parsed

    previous = instant(outcome["completed_at"]) if records else None
    for item in records:
        if outcome.get("status") != "Implemented":
            raise GovernanceError("offer adversarial review only after an Implemented engineering result is saved")
        stamp = instant(item["recorded_at"])
        if previous is not None and stamp < previous:
            raise GovernanceError("adversarial review records must follow engineering completion and prior records")
        kind = item["event"]
        if kind == "Offer":
            if accepted:
                raise GovernanceError("an active review must be completed or stopped before offering it again")
            offered, accepted, streak, status = True, False, 0, "AwaitingUser"
        elif kind == "Decision":
            if not offered:
                raise GovernanceError("record the actual post-completion question before a user decision")
            if item["outcome"] == "Stopped" and not accepted:
                raise GovernanceError("only an opted-in review can be stopped")
            if accepted and item["outcome"] != "Stopped":
                raise GovernanceError("an active review only accepts an explicit stop decision")
            if not offered or (status != "AwaitingUser" and item["outcome"] != "Stopped"):
                raise GovernanceError("a new review decision requires a new actual offer")
            accepted = item["outcome"] == "Accepted"
            status = "InProgress" if accepted else item["outcome"]
            streak = 0
        else:
            if not accepted or status == "Passed":
                raise GovernanceError("do not start review without explicit opt-in, or continue after two clean rounds")
            if kind == "Blocked":
                streak, status = 0, "Blocked"
            else:
                start = instant(item["started_at"])
                if start < previous or start > stamp:
                    raise GovernanceError("each round must start after opt-in and after the previous round finished")
                if item["round_id"] in ids or reports.intersection(item["evidence_refs"]):
                    raise GovernanceError("each round requires a fresh review id and distinct report evidence")
                if contract is not None and item["requirements_sha256"] != requirements_subject(contract):
                    raise GovernanceError("review must cover the unchanged original request and clarification")
                ids.add(item["round_id"])
                reports.update(item["evidence_refs"])
                for fix in item["resolutions"]:
                    key = fix["finding_id"]
                    if key not in findings:
                        raise GovernanceError("resolution must reference an unresolved finding")
                    if fix["disposition"] == "Fixed" and findings[key] == item["subject_sha256"]:
                        raise GovernanceError("a fix requires a newly verified delivery; use evidenced NotAnIssue for a false positive")
                    del findings[key]
                for finding in item["findings"]:
                    if finding["id"] in all_findings:
                        raise GovernanceError("finding ids must be unique; retain original issues and resolutions")
                    all_findings.add(finding["id"])
                    findings[finding["id"]] = item["subject_sha256"]
                subject = (item["delivery_task_id"], item["subject_sha256"], item["requirements_sha256"])
                if subject != last_subject:
                    streak = 0
                clean = item["coverage"] == "Complete" and not item["unreviewed_items"] and not item["findings"] and not findings
                streak = streak + 1 if clean else 0
                rounds += 1
                last_subject = subject
                status = "Passed" if streak == 2 else "InProgress"
                if status == "Passed":
                    accepted = False
        previous = stamp
    return {"status": status, "clean_streak": streak, "rounds": rounds,
            "open_findings": sorted(findings)}


def validate_review(outcome: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    from governance_artifacts import GovernanceError
    try:
        review_state(outcome, contract)
    except (GovernanceError, KeyError, TypeError, ValueError) as exc:
        return [f"adversarial_review: {exc}"]
    return []


def _load_delivery(task_dir: Path) -> tuple[Path, dict, dict, dict, list]:
    from governance_artifacts import GovernanceError, read_json, read_jsonl, validate_task_directory
    from minimal_task import minimal_approval_contract
    errors = validate_task_directory(task_dir)
    if errors:
        raise GovernanceError("; ".join(errors))
    if (task_dir / "before.json").is_file():
        path = task_dir / "after.json"
        if not path.is_file():
            raise GovernanceError("save the engineering result before offering adversarial review")
        document = read_json(path)
        return path, document, document, read_json(task_dir / "before.json"), read_jsonl(task_dir / "run.jsonl")
    path = task_dir / "task-record.json"
    document = read_json(path)
    outcome = document.get("task_outcome")
    if not outcome:
        raise GovernanceError("save the engineering result before offering adversarial review")
    return path, document, outcome, minimal_approval_contract(document), document["run_ledger"]


def append_review(task_dir: Path, entry: dict[str, Any], *, reason: str, basis: str) -> Path:
    """Append only the new record to amendment history, never copy the whole series."""
    from governance_artifacts import (GovernanceError, atomic_write_json, ensure_skill_integrity,
        ledger_lock, require_record_semantics, require_valid_json_document, user_decision_subject_sha256)
    from minimal_task import require_valid_minimal_record
    from check_write_guard import evaluate

    ensure_skill_integrity()
    task_dir = task_dir.resolve()
    if not reason.strip() or not basis.strip():
        raise GovernanceError("review update requires its actual reason and source")
    path = task_dir / ("after.json" if (task_dir / "before.json").is_file() else "task-record.json")
    if not evaluate(path, task_dir)[0]:
        raise GovernanceError("review result write refused by task scope")
    with ledger_lock(path):
        path, document, outcome, contract, _ = _load_delivery(task_dir)
        if "adversarial_review" not in outcome:
            raise GovernanceError("legacy results are not automatically enrolled in the new review protocol")
        if entry.get("event") == "Round":
            delivery_id = entry.get("delivery_task_id", "")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", delivery_id):
                raise GovernanceError("delivery_task_id must identify a task in this project")
            delivery_dir = task_dir.parent / delivery_id
            _, _, delivery, delivery_contract, events = _load_delivery(delivery_dir)
            if delivery.get("status") != "Implemented":
                raise GovernanceError("rounds require a verified Implemented delivery")
            if delivery_id != task_dir.name and task_dir.name not in delivery_contract.get("depends_on", []):
                raise GovernanceError("a repaired delivery must directly depend on the original task")
            if entry.get("subject_sha256") != user_decision_subject_sha256(delivery_contract, events, delivery):
                raise GovernanceError("round subject does not match the referenced verified engineering result")
        records = outcome["adversarial_review"]
        records.append(copy.deepcopy(entry))
        review_state(outcome, contract)
        revision = document["revision"]
        document["revision"] += 1
        field = "adversarial_review" if path.name == "after.json" else "task_outcome.adversarial_review"
        delta = {"path": f"{field}.{len(records)-1}", "old_value": {"$missing": True}, "new_value": entry}
        amendment = {"from_revision": revision, "to_revision": revision + 1, "reason": reason,
                     "basis": basis, "changed_at": entry["recorded_at"]}
        amendment.update(delta if path.name == "after.json" else {"changes": [delta]})
        document["amendments"].append(amendment)
        if path.name == "after.json":
            require_valid_json_document(document, "task-after.schema.json", "after")
            require_record_semantics(path, document)
        else:
            require_valid_minimal_record(document, task_dir=task_dir)
        atomic_write_json(path, document)
    return path


def main() -> int:
    from governance_artifacts import GovernanceError, user_decision_subject_sha256
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--entry-json-file", type=Path, help="Append an actual Offer, Decision, Round or Blocked record; omitted means read-only status")
    parser.add_argument("--reason")
    parser.add_argument("--basis")
    args = parser.parse_args()
    try:
        if args.entry_json_file:
            append_review(args.task_dir, json.loads(args.entry_json_file.read_text(encoding="utf-8")),
                          reason=args.reason or "", basis=args.basis or "")
        _, _, outcome, contract, events = _load_delivery(args.task_dir.resolve())
        status = {**review_state(outcome, contract), "requirements_sha256": requirements_subject(contract),
                  "delivery_task_id": args.task_dir.resolve().name,
                  "subject_sha256": user_decision_subject_sha256(contract, events, outcome)}
        print(json.dumps(status, ensure_ascii=False, indent=2))
    except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
