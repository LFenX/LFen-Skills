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

REVIEW_CONTRACT = "report-bound-v2"
TASK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")


def review_schema() -> dict[str, Any]:
    """One schema definition, embedded into both existing outcome schemas."""
    text = {"type": "string", "minLength": 1}
    refs = {"type": "array", "minItems": 1, "uniqueItems": True, "items": text}
    strings = {"type": "array", "uniqueItems": True, "items": text}
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}

    def obj(properties: dict[str, Any], optional: tuple[str, ...] = ()) -> dict[str, Any]:
        return {"type": "object", "additionalProperties": False,
                "required": [key for key in properties if key not in optional], "properties": properties}

    variants = []
    details = {
        "Offer": {"prompt": text, "evidence_ref": text},
        "Decision": {"outcome": {"enum": ["Accepted", "Declined", "Deferred", "Stopped"]},
                     "response": text, "decided_by": text, "evidence_ref": text},
        "Blocked": {"reason": text, "evidence_refs": refs},
        "Round": {"round_id": text, "started_at": {"type": "string", "format": "date-time"},
                  "reviewer": text, "delivery_task_id": text, "subject_sha256": digest,
                  "requirements_sha256": digest, "coverage": {"enum": ["Complete", "Incomplete"]},
                  "review_contract_version": {"const": REVIEW_CONTRACT},
                  "report_ref": text, "report_sha256": digest,
                  "delivery_completed_at": {"type": "string", "format": "date-time"},
                  "delivery_verified_at": {"type": "string", "format": "date-time"},
                  "unreviewed_items": strings, "evidence_refs": refs,
                  "findings": {"type": "array", "items": obj({"id": text, "summary": text,
                                                              "evidence_refs": refs})},
                  "resolutions": {"type": "array", "items": obj({"finding_id": text,
                     "disposition": {"enum": ["Fixed", "NotAnIssue"]}, "reason": text, "evidence_refs": refs})}},
    }
    for kind, properties in details.items():
        variants.append(obj({"event": {"const": kind},
                             "recorded_at": {"type": "string", "format": "date-time"}, **properties},
                            ("review_contract_version", "report_ref", "report_sha256", "delivery_completed_at", "delivery_verified_at") if kind == "Round" else ()))
    return {"type": "array", "items": {"oneOf": variants}}


def requirements_subject(contract: dict[str, Any]) -> str:
    """Bind original words and their question/default context, not survey metadata."""
    raw = {"request": (contract.get("request_snapshot") or {}).get("text"), "clarification": []}
    for round_value in (contract.get("clarification") or {}).get("rounds", []):
        raw["clarification"].append({"ordinal": round_value.get("ordinal"), "exchanges": [
            {key: exchange[key] for key in ("question", "changes", "recommended_default", "answer", "answer_state", "follows_up") if key in exchange}
            for exchange in round_value.get("exchanges", [])]})
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _legacy_requirements_subject(contract: dict[str, Any]) -> str:
    raw = {"request_snapshot": contract.get("request_snapshot"), "clarification": contract.get("clarification")}
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _instant(value: Any) -> datetime:
    from governance_artifacts import GovernanceError
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise GovernanceError("adversarial review requires real timezone-aware timestamps") from exc
    if parsed.tzinfo is None or parsed > datetime.now(timezone.utc):
        raise GovernanceError("adversarial review time must include timezone and must not be in the future")
    return parsed


def review_state(outcome: dict[str, Any], contract: dict[str, Any] | None = None, *,
                 delivery_subjects: dict[str, str | None] | None = None,
                 report_hashes: dict[str, str | None] | None = None,
                 current_delivery_ids: set[str] | None = None) -> dict[str, Any]:
    """Replay actual records; a stored claim cannot override the clean streak."""
    from governance_artifacts import GovernanceError, validate_json_document

    records = outcome.get("adversarial_review")
    if records is None:
        return {"status": "LegacyUntracked", "clean_streak": 0, "rounds": 0, "open_findings": []}
    errors = validate_json_document(records, review_schema(), "adversarial_review")
    if errors:
        raise GovernanceError("; ".join(errors))
    status = "NotOffered" if outcome.get("status") == "Implemented" else "NotApplicable"
    parent = outcome.get("adversarial_review_parent")
    if parent:
        if records or not isinstance(parent, str) or not TASK_ID.fullmatch(parent) or (contract is not None and (
                parent == contract.get("task_id") or parent not in contract.get("depends_on", []))):
            raise GovernanceError("a review repair must retain its direct parent and must not open a recursive review")
        return {"status": "ManagedByParent" if outcome.get("status") == "Implemented" else "NotApplicable",
                "parent_task_id": parent, "clean_streak": 0, "rounds": 0, "open_findings": []}
    streak = rounds = 0
    legacy_streak = 0
    recorded_streak = 0
    offered = accepted = False
    last_subject = None
    ids: set[str] = set()
    reports: set[str] = set()
    recorded_reports: set[str] = set()
    findings: dict[str, str] = {}
    all_findings: set[str] = set()

    previous = _instant(outcome["completed_at"]) if records else None
    for item in records:
        if outcome.get("status") != "Implemented":
            raise GovernanceError("offer adversarial review only after an Implemented engineering result is saved")
        stamp = _instant(item["recorded_at"])
        if previous is not None and stamp < previous:
            raise GovernanceError("adversarial review records must follow engineering completion and prior records")
        kind = item["event"]
        if kind == "Offer":
            if accepted and status != "Passed" and recorded_streak != 2:
                raise GovernanceError("an active review must be completed or stopped before offering it again")
            offered, accepted, streak, status = True, False, 0, "AwaitingUser"
            legacy_streak = recorded_streak = 0
        elif kind == "Decision":
            if not offered:
                raise GovernanceError("record the actual post-completion question before a user decision")
            if item["outcome"] == "Stopped" and not accepted:
                raise GovernanceError("only an opted-in review can be stopped")
            if accepted and status not in {"Passed", "LegacyNotRevalidated"} and recorded_streak != 2 and item["outcome"] != "Stopped":
                raise GovernanceError("an active review only accepts an explicit stop decision")
            accepted = item["outcome"] == "Accepted"
            status = "InProgress" if accepted else item["outcome"]
            streak = legacy_streak = recorded_streak = 0
        else:
            if not accepted or status == "Passed":
                raise GovernanceError("do not start review without explicit opt-in, or continue after two clean rounds")
            if kind == "Blocked":
                streak, legacy_streak, recorded_streak, status = 0, 0, 0, "Blocked"
            else:
                start = _instant(item["started_at"])
                if start < previous or start > stamp:
                    raise GovernanceError("each round must start after opt-in and after the previous round finished")
                if item["round_id"] in ids:
                    raise GovernanceError("each round requires a fresh review id")
                bound = item.get("review_contract_version") == REVIEW_CONTRACT
                if bound and any(not item.get(key) for key in ("report_ref", "report_sha256", "delivery_completed_at", "delivery_verified_at")):
                    raise GovernanceError("report-bound rounds require their actual report and delivery times")
                if bound and start < max(_instant(item["delivery_completed_at"]), _instant(item["delivery_verified_at"])):
                    raise GovernanceError("a round must start after its repaired delivery was verified and saved")
                expected_requirements = (requirements_subject(contract) if bound else _legacy_requirements_subject(contract)) if contract is not None else item["requirements_sha256"]
                current = item["requirements_sha256"] == expected_requirements
                if delivery_subjects is not None:
                    current = current and delivery_subjects.get(item["delivery_task_id"]) == item["subject_sha256"]
                if current_delivery_ids is not None:
                    current = current and len(current_delivery_ids) == 1 and item["delivery_task_id"] in current_delivery_ids
                identity = (report_hashes or {}).get(item["round_id"]) if report_hashes is not None else item.get("report_sha256")
                recorded_report = item.get("report_sha256")
                recorded_report_valid = not bound or bool(recorded_report) and recorded_report not in recorded_reports
                report_valid = bound and bool(identity) and identity == recorded_report and identity not in reports and recorded_report_valid
                if identity:
                    reports.add(identity)
                if recorded_report:
                    recorded_reports.add(recorded_report)
                ids.add(item["round_id"])
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
                subject = (item["delivery_task_id"], item["subject_sha256"], item["requirements_sha256"], bound)
                if subject != last_subject:
                    streak = legacy_streak = recorded_streak = 0
                clean = item["coverage"] == "Complete" and not item["unreviewed_items"] and not item["findings"] and not findings
                # Replay later Offer/Decision records even if an older version
                # accepted duplicate evidence. Historical claims never validate
                # current counts; only current, distinct reports can do that.
                recorded_streak = min(2, recorded_streak + 1) if clean and (not bound or recorded_report) else 0
                streak = streak + 1 if clean and current and report_valid else 0
                legacy_streak = legacy_streak + 1 if clean and current and not bound else 0
                rounds += 1
                last_subject = subject
                status = "Stale" if not current or bound and not report_valid else "Passed" if streak == 2 else "InProgress"
                if legacy_streak == 2:
                    status = "LegacyNotRevalidated"
                    accepted = False
        previous = stamp
    result = {"status": status, "clean_streak": streak, "rounds": rounds, "open_findings": sorted(findings)}
    if last_subject is not None:
        result["reviewed_delivery"] = {"task_id": last_subject[0], "subject_sha256": last_subject[1],
                                       "requirements_sha256": last_subject[2]}
    return result


def _report_path(task_dir: Path, reference: str) -> Path:
    from governance_artifacts import GovernanceError
    if not isinstance(reference, str) or not reference.strip() or "://" in reference:
        raise GovernanceError("report_ref must identify a local report in the original review task")
    path = Path(reference)
    path = path.resolve() if path.is_absolute() else (task_dir.resolve().parents[2] / path).resolve()
    if not path.is_relative_to(task_dir.resolve()) or not path.is_file():
        raise GovernanceError("report_ref must be an existing file inside the original review task")
    return path


def _current_bindings(task_dir: Path, outcome: dict, contract: dict, events: list) -> tuple[dict, dict, set[str]]:
    from governance_artifacts import user_decision_subject_sha256
    subjects = {task_dir.name: user_decision_subject_sha256(contract, events, outcome)}
    completions = {task_dir.name: _instant(outcome["completed_at"])}
    if not outcome.get("adversarial_review_parent"):
        for candidate in task_dir.parent.iterdir():
            if candidate == task_dir or not candidate.is_dir() or not TASK_ID.fullmatch(candidate.name):
                continue
            try:
                _, _, saved, before, ledger = _read_saved(candidate)
                if (saved.get("adversarial_review_parent") != task_dir.name
                        or before.get("task_id") != candidate.name
                        or before.get("project_id") != contract.get("project_id")
                        or task_dir.name not in before.get("depends_on", [])):
                    continue
                completions[candidate.name] = _instant(saved["completed_at"])
                subjects[candidate.name] = user_decision_subject_sha256(before, ledger, saved)
            except (OSError, ValueError, TypeError, KeyError):
                continue
    latest = max(completions.values())
    current_ids = {key for key, value in completions.items() if value == latest}
    hashes = {}
    for entry in outcome.get("adversarial_review", []):
        if not isinstance(entry, dict) or entry.get("event") != "Round":
            continue
        delivery_id = entry.get("delivery_task_id", "")
        if delivery_id not in subjects:
            try:
                if not TASK_ID.fullmatch(delivery_id):
                    raise ValueError("invalid delivery id")
                _, _, saved, before, ledger = _read_saved(task_dir.parent / delivery_id)
                subjects[delivery_id] = user_decision_subject_sha256(before, ledger, saved)
            except (OSError, ValueError, TypeError, KeyError):
                subjects[delivery_id] = None
        reference = entry.get("report_ref") or next(iter(entry.get("evidence_refs", [])), "")
        try:
            hashes[entry.get("round_id")] = hashlib.sha256(_report_path(task_dir, reference).read_bytes()).hexdigest()
        except (OSError, ValueError, TypeError):
            hashes[entry.get("round_id")] = None
    return subjects, hashes, current_ids


def bound_review_state(task_dir: Path, outcome: dict, contract: dict, events: list) -> dict[str, Any]:
    subjects, hashes, current_ids = _current_bindings(task_dir.resolve(), outcome, contract, events)
    state = review_state(outcome, contract, delivery_subjects=subjects, report_hashes=hashes,
                         current_delivery_ids=current_ids)
    if not outcome.get("adversarial_review_parent"):
        if len(current_ids) == 1:
            current_id = next(iter(current_ids))
            state["current_delivery"] = {"task_id": current_id, "subject_sha256": subjects[current_id]}
        else:
            state["current_delivery"] = {"task_ids": sorted(current_ids), "status": "Ambiguous"}
    return state


def validate_review(outcome: dict[str, Any], contract: dict[str, Any], *,
                    task_dir: Path | None = None, events: list | None = None) -> list[str]:
    from governance_artifacts import GovernanceError
    try:
        if task_dir is not None:
            bound_review_state(task_dir, outcome, contract, events or [])
        else:
            review_state(outcome, contract)
    except (GovernanceError, KeyError, TypeError, ValueError) as exc:
        return [f"adversarial_review: {exc}"]
    return []


def _read_saved(task_dir: Path) -> tuple[Path, dict, dict, dict, list]:
    from governance_artifacts import GovernanceError, read_json, read_jsonl
    from minimal_task import minimal_approval_contract
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


def _load_delivery(task_dir: Path) -> tuple[Path, dict, dict, dict, list]:
    from governance_artifacts import GovernanceError, validate_task_directory
    errors = validate_task_directory(task_dir)
    if errors:
        raise GovernanceError("; ".join(errors))
    return _read_saved(task_dir)


def review_status(task_dir: Path) -> dict[str, Any]:
    _, _, outcome, contract, events = _load_delivery(task_dir.resolve())
    return bound_review_state(task_dir, outcome, contract, events)


def require_review_parent(task_dir: Path, contract: dict, parent_id: str) -> str:
    from governance_artifacts import GovernanceError
    if not isinstance(parent_id, str) or not TASK_ID.fullmatch(parent_id) or parent_id == task_dir.name or parent_id not in contract.get("depends_on", []):
        raise GovernanceError("a review repair must directly depend on its original review task")
    parent_dir = task_dir.resolve().parent / parent_id
    _, _, parent, parent_contract, events = _load_delivery(parent_dir)
    if parent_contract.get("project_id") != contract.get("project_id") or parent.get("status") != "Implemented":
        raise GovernanceError("review parent must be a completed engineering task in the same project")
    if bound_review_state(parent_dir, parent, parent_contract, events)["status"] not in {"InProgress", "Blocked", "Stale"}:
        raise GovernanceError("a repair must belong to an explicitly opted-in, unfinished parent review")
    return parent_id


def append_review(task_dir: Path, entry: dict[str, Any], *, reason: str, basis: str) -> Path:
    """Append only the new record to amendment history, never copy the whole series."""
    from governance_artifacts import (GovernanceError, atomic_write_json, ensure_skill_integrity,
        ledger_lock, require_record_semantics, require_valid_json_document, user_decision_subject_sha256, validate_json_document)
    from minimal_task import require_valid_minimal_record
    from check_write_guard import evaluate

    ensure_skill_integrity()
    task_dir = task_dir.resolve()
    if not isinstance(entry, dict):
        raise GovernanceError("review entry must be a JSON object")
    entry = copy.deepcopy(entry)
    errors = validate_json_document(entry, review_schema()["items"], "review entry")
    if errors:
        raise GovernanceError("; ".join(errors))
    if not reason.strip() or not basis.strip():
        raise GovernanceError("review update requires its actual reason and source")
    path = task_dir / ("after.json" if (task_dir / "before.json").is_file() else "task-record.json")
    if not evaluate(path, task_dir)[0]:
        raise GovernanceError("review result write refused by task scope")
    with ledger_lock(path):
        path, document, outcome, contract, original_events = _load_delivery(task_dir)
        if "adversarial_review" not in outcome:
            raise GovernanceError("legacy results are not automatically enrolled in the new review protocol")
        if outcome.get("adversarial_review_parent"):
            raise GovernanceError("record rounds on the original review task; this repair is managed by its parent")
        if entry.get("event") == "Round":
            delivery_id = entry.get("delivery_task_id", "")
            if not TASK_ID.fullmatch(delivery_id):
                raise GovernanceError("delivery_task_id must identify a task in this project")
            _, report_hashes, current_ids = _current_bindings(task_dir, outcome, contract, original_events)
            if len(current_ids) != 1 or delivery_id not in current_ids:
                raise GovernanceError("rounds must reference the current saved delivery; an older or ambiguous delivery cannot count")
            delivery_dir = task_dir.parent / delivery_id
            _, _, delivery, delivery_contract, events = _load_delivery(delivery_dir)
            if delivery.get("status") != "Implemented":
                raise GovernanceError("rounds require a verified Implemented delivery")
            if delivery_contract.get("project_id") != contract.get("project_id"):
                raise GovernanceError("delivery and original review must belong to the same project")
            if delivery_id != task_dir.name and (task_dir.name not in delivery_contract.get("depends_on", [])
                    or delivery.get("adversarial_review_parent") != task_dir.name):
                raise GovernanceError("a repaired delivery must directly depend on and explicitly belong to the original review")
            if entry.get("subject_sha256") != user_decision_subject_sha256(delivery_contract, events, delivery):
                raise GovernanceError("round subject does not match the referenced verified engineering result")
            if entry["requirements_sha256"] != requirements_subject(contract):
                raise GovernanceError("new rounds must bind the current original request and clarification words")
            verified_at = max((_instant(event["timestamp"]) for event in events if event.get("event_type") == "verification" and event.get("status") == "succeeded" and event.get("evidence_refs")), default=_instant(delivery["completed_at"]))
            if _instant(entry["started_at"]) < max(verified_at, _instant(delivery["completed_at"])):
                raise GovernanceError("start a new round only after the referenced delivery was verified and saved")
            report = _report_path(task_dir, entry.get("report_ref", ""))
            contents = report.read_bytes()
            if not contents.strip():
                raise GovernanceError("the actual round report must not be empty")
            report_sha = hashlib.sha256(contents).hexdigest()
            recorded_hashes = {item.get("report_sha256") for item in outcome["adversarial_review"] if item.get("event") == "Round"}
            if report_sha in report_hashes.values() or report_sha in recorded_hashes:
                raise GovernanceError("each round needs a distinct report; aliases and copied content cannot count twice")
            facts = {"review_contract_version": REVIEW_CONTRACT,
                     "report_ref": report.relative_to(task_dir.parents[2]).as_posix(), "report_sha256": report_sha,
                     "delivery_completed_at": delivery["completed_at"],
                     "delivery_verified_at": verified_at.isoformat().replace("+00:00", "Z")}
            for key, value in facts.items():
                if key != "report_ref" and key in entry and entry[key] != value:
                    raise GovernanceError(f"{key} must match the actual report or delivery")
            entry.update(facts)
        records = outcome["adversarial_review"]
        records.append(copy.deepcopy(entry))
        bound_review_state(task_dir, outcome, contract, original_events)
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
        status = {**bound_review_state(args.task_dir, outcome, contract, events), "requirements_sha256": requirements_subject(contract),
                  "delivery_task_id": args.task_dir.resolve().name,
                  "subject_sha256": user_decision_subject_sha256(contract, events, outcome)}
        print(json.dumps(status, ensure_ascii=False, indent=2))
    except (GovernanceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
