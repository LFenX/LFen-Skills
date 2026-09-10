"""Canonical event conversion for governed product workflow records.

This module is deliberately dependency-free.  It reads immutable task records and
creates an outbox-ready batch; it never edits the source task or uploads source code.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "skill-practice-event.v1"
_SAFE_NAME = re.compile(r"[^a-zA-Z0-9_.-]+")
_SOURCE_DIRS = {".git", ".env", "node_modules", "credentials", "secrets"}
_SOURCE_FIELDS = {"source", "source_code", "file_content", "content", "diff", "patch", "stdout", "stderr"}
_IDENTITY_FIELDS = {"producer_id", "hostname", "host", "ip", "source_ip", "cwd", "workspace", "workspace_root", "root", "project_id", "task_id", "run_id", "attempt_id", "event_id"}


def _json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return default


def _utc(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_local_secret(path: Path | None = None) -> bytes:
    """Get/create a machine-local key. Its bytes never enter an event payload."""
    candidate = path or Path(os.environ.get("SKILL_COLLECTOR_SECRET_FILE", "~/.skill-practice-collector/key")).expanduser()
    candidate.parent.mkdir(parents=True, exist_ok=True)
    try:
        return candidate.read_bytes()
    except FileNotFoundError:
        value = secrets.token_bytes(32)
        with open(candidate, "xb") as fh:
            fh.write(value)
        try:
            os.chmod(candidate, 0o600)
        except OSError:
            pass
        return value


def pseudonym(value: Any, secret: bytes) -> str | None:
    if value is None or value == "":
        return None
    return "h1_" + hmac.new(secret, str(value).encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def _event_id(task_id: str, suffix: str, payload: Any) -> str:
    # Event identifiers are stable but must not embed the raw task identifier.
    return f"e_{_digest({'task_id': task_id, 'suffix': suffix, 'payload': payload})[:32]}"


def _stage(raw: dict[str, Any], event_type: str) -> str | None:
    candidate = raw.get("stage") or raw.get("phase")
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    known = {"run_started": "start", "clarification": "clarification", "plan": "planning",
             "step_started": "execution", "step_completed": "execution", "verification": "verification",
             "run_finished": "close", "task_closed": "close", "retry": "execution"}
    return known.get(event_type)


def _metric(raw: dict[str, Any], key: str) -> tuple[int | float | None, str]:
    value = raw.get(key)
    if isinstance(value, (int, float)) and value >= 0:
        return value, "reported"
    return None, "unavailable"


def _artifact_metadata(task_root: Path, manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, list):
        return []
    output: list[dict[str, Any]] = []
    for item in manifest:
        if not isinstance(item, dict):
            continue
        ref = item.get("content_ref")
        safe_ref = ref
        if isinstance(ref, str):
            ref_path = Path(ref)
            if ref_path.is_absolute():
                try:
                    safe_ref = ref_path.resolve().relative_to(task_root.resolve()).as_posix()
                except ValueError:
                    safe_ref = None
        entry: dict[str, Any] = {"asset_id": item.get("asset_id"), "content_ref": safe_ref,
                                 "action": item.get("action"), "size_bytes": None,
                                 "sha256": None, "size_provenance": "unavailable"}
        if isinstance(ref, str):
            candidate = (task_root / ref).resolve()
            try:
                inside = os.path.commonpath([str(task_root.resolve()), str(candidate)]) == str(task_root.resolve())
            except ValueError:
                inside = False
            if inside and candidate.is_file() and not any(part.lower() in _SOURCE_DIRS for part in candidate.parts):
                entry["size_bytes"] = candidate.stat().st_size
                entry["size_provenance"] = "observed_current"
                digest = hashlib.sha256()
                with candidate.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                        digest.update(chunk)
                entry["sha256"] = digest.hexdigest()
        output.append(entry)
    return output


def _without_source(value: Any, key: str | None = None) -> Any:
    """Remove fields that can carry source bytes while retaining process evidence."""
    if key and key.lower() in _SOURCE_FIELDS:
        return None
    if key and key.lower() in _IDENTITY_FIELDS:
        return None
    if isinstance(value, dict):
        return {k: cleaned for k, v in value.items()
                if (cleaned := _without_source(v, str(k))) is not None}
    if isinstance(value, list):
        return [_without_source(item) for item in value]
    return value


def _safe_refs(value: Any, task_root: Path) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            continue
        path = Path(item)
        if path.is_absolute():
            try:
                item = path.resolve().relative_to(task_root.resolve()).as_posix()
            except ValueError:
                continue
        result.append(item.replace("\\", "/"))
    return result


def _base_event(task: dict[str, Any], raw: dict[str, Any], secret: bytes, task_root: Path,
                sequence: int, event_type: str, payload: Any, suffix: str) -> dict[str, Any]:
    task_id = str(task.get("task_id") or task_root.name)
    run_id = raw.get("run_id") or task.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        run_id = "run-unknown"
    attempt_id = raw.get("attempt_id") or "attempt-unknown"
    duration, duration_source = _metric(raw, "duration_ms")
    wait, wait_source = _metric(raw, "wait_ms")
    occurred = _utc(raw.get("occurred_at") or raw.get("timestamp") or raw.get("at"))
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": _event_id(task_id, str(raw.get("event_id") or suffix), payload),
        "task_id": pseudonym(task_id, secret) or "h1_unknown",
        "run_id": pseudonym(run_id, secret) or "h1_unknown",
        "attempt_id": pseudonym(attempt_id, secret) or "h1_unknown",
        "sequence": sequence,
        "skill_name": task.get("skill_name") or "run-governed-product-workflow",
        "skill_version": task.get("skill_version") or task.get("schema_version"),
        "producer_id_hash": pseudonym(task.get("producer_id") or "local", secret),
        "project_id_hash": pseudonym(task.get("project_id"), secret),
        "stage": _stage(raw, event_type), "event_type": event_type,
        "status": raw.get("status") if isinstance(raw.get("status"), str) else None,
        "occurred_at": occurred,
        "duration_ms": duration, "duration_provenance": duration_source,
        "wait_ms": wait, "wait_provenance": wait_source,
        "failure_class": raw.get("failure_class"), "error_code": raw.get("error_code"),
        "blocker_code": raw.get("blocker_code"), "retry_reason": raw.get("retry_reason"),
        "request_snapshot_ref": "payload.request_snapshot" if "request_snapshot" in payload else None,
        "requirement_ref": raw.get("requirement_ref"), "plan_step_ref": raw.get("plan_step_ref"),
        "execution_step_ref": raw.get("execution_step_ref"),
        "artifact_refs": _safe_refs(raw.get("artifact_refs"), task_root),
        "metrics": {"duration_provenance": duration_source, "wait_provenance": wait_source},
        "payload": payload,
    }


def canonicalize_task(task_dir: str | Path, *, secret: bytes | None = None) -> list[dict[str, Any]]:
    """Read a task directory and return deterministic canonical events."""
    root = Path(task_dir).resolve()
    task = _json(root / "before.json", {})
    if not isinstance(task, dict):
        raise ValueError("before.json must be a JSON object")
    secret = secret or load_local_secret()
    task_id = str(task.get("task_id") or root.name)
    events: list[dict[str, Any]] = []
    request_raw = task.get("request_snapshot") if isinstance(task.get("request_snapshot"), dict) else {}
    # Keep the exact user text and capture metadata; ignore optional attachment/source blobs.
    request = {key: request_raw[key] for key in ("language", "text", "captured_at") if key in request_raw}
    summary_payload = {
        "request_snapshot": request,
        "clarification": task.get("clarification"),
        "requirement_items": task.get("requirement_items", []),
        "plan": task.get("plan", {}),
        "acceptance": task.get("acceptance", {}),
        "decisions": task.get("decisions", []),
    }
    events.append(_base_event(task, {}, secret, root, 1, "task_snapshot", summary_payload, "snapshot"))
    ledger = []
    for line in (root / "run.jsonl").read_text(encoding="utf-8").splitlines() if (root / "run.jsonl").exists() else []:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            ledger.append(value)
    measurement_path = root / "collector-measurements.jsonl"
    for line in measurement_path.read_text(encoding="utf-8").splitlines() if measurement_path.exists() else []:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            ledger.append(value)
    ledger.sort(key=lambda x: (_utc(x.get("occurred_at") or x.get("timestamp") or x.get("at")) or "", str(x.get("event_id", ""))))
    for index, raw in enumerate(ledger, start=2):
        event_type = str(raw.get("event_type") or raw.get("type") or "ledger_event")
        events.append(_base_event(task, raw, secret, root, index, event_type,
                                  {"raw": _without_source(raw)}, f"ledger-{index}"))
    outcome = _json(root / "after.json", {})
    if isinstance(outcome, dict) and outcome:
        # source_snapshot and artifact_manifest can contain absolute workspace paths;
        # artifact metadata is reduced to relative references, size and hash below.
        outcome_evidence = {k: v for k, v in outcome.items()
                            if k not in {"source_snapshot", "artifact_manifest"}}
        payload = {"outcome": _without_source(outcome_evidence),
                   "artifact_metadata": _artifact_metadata(root.parent.parent.parent, outcome.get("artifact_manifest"))}
        events.append(_base_event(task, outcome, secret, root, len(events) + 1, "task_outcome", payload, "outcome"))
    return events


def collect_task(task_dir: str | Path, *, secret: bytes | None = None) -> dict[str, Any]:
    events = canonicalize_task(task_dir, secret=secret)
    batch_id = "b1_" + _digest([e["event_id"] for e in events])[:32]
    return {"schema_version": "skill-practice-batch.v1", "batch_id": batch_id,
            "events": events, "event_count": len(events)}
