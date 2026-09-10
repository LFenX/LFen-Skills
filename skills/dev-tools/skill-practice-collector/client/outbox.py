"""Low overhead local outbox and batch HTTP transport for the skill collector.

The module deliberately has no third party dependency.  Events are written to a
SQLite WAL before a network request is attempted, and sent batches are retained
forever.  A batch id is used as the HTTP Idempotency-Key, so a timeout followed
by a retry cannot create a second server-side batch.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import random
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler


_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS batches (
  batch_id TEXT PRIMARY KEY,
  payload BLOB NOT NULL,
  event_count INTEGER NOT NULL CHECK (event_count > 0),
  status TEXT NOT NULL CHECK (status IN ('pending','sent','failed','partial','rejected')),
  attempts INTEGER NOT NULL DEFAULT 0,
  next_attempt_at REAL NOT NULL,
  last_error TEXT,
  created_at TEXT NOT NULL,
  sent_at TEXT
);
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL REFERENCES batches(batch_id),
  event_json TEXT NOT NULL,
  content_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS batches_due_idx ON batches(status, next_attempt_at);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _event_id(event: Mapping[str, Any]) -> str:
    value = event.get("event_id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("event.event_id must be a non-empty string")
    return value


def _compressed_payload(events: list[Mapping[str, Any]], batch_id: str = "preview") -> bytes:
    body = _json_bytes({"data": {"schema_version": "skill-practice-batch.v1", "batch_id": batch_id,
                                  "event_count": len(events), "events": events}})
    # mtime=0 makes equal payloads byte-for-byte reproducible for audit/debugging.
    return gzip.compress(body, compresslevel=6, mtime=0)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise URLError("redirects are disabled for collector ingestion")


@dataclass(frozen=True)
class BatchResult:
    batch_id: str
    status: str
    attempts: int
    error: str | None = None
    request_id: str | None = None


class AckValidationError(ValueError):
    """The server answered, but the ACK cannot be trusted as a success."""

    def __init__(self, message: str, *, rejected: bool = False, partial: bool = False):
        super().__init__(message)
        self.rejected = rejected
        self.partial = partial


class Outbox:
    """SQLite backed immutable event outbox.

    ``path`` is normally a file local to the producing machine.  It must not be
    placed in the repository: the outbox can contain exact user supplied text.
    """

    def __init__(self, path: str | Path, *, busy_timeout_ms: int = 10_000):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=busy_timeout_ms / 1000, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute(f"PRAGMA busy_timeout={int(busy_timeout_ms)}")
        self.db.executescript(_SCHEMA)

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "Outbox":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def enqueue(self, events: Iterable[Mapping[str, Any]], *, batch_id: str | None = None) -> str | None:
        """Persist one immutable batch.  Existing identical event IDs are skipped.

        A conflicting event ID (same id, different content) is rejected loudly;
        silently replacing evidence would break the collector's audit trail.
        """
        normalized = [dict(event) for event in events]
        if not normalized:
            return None
        ids: set[str] = set()
        for event in normalized:
            eid = _event_id(event)
            if eid in ids:
                raise ValueError(f"duplicate event_id in batch: {eid}")
            ids.add(eid)
        fresh: list[dict[str, Any]] = []
        for event in normalized:
            eid = _event_id(event)
            digest = hashlib.sha256(_json_bytes(event)).hexdigest()
            row = self.db.execute("SELECT content_sha256 FROM events WHERE event_id=?", (eid,)).fetchone()
            if row is None:
                fresh.append(event)
            elif row["content_sha256"] != digest:
                raise ValueError(f"event_id already exists with different content: {eid}")
        if not fresh:
            return None
        bid = batch_id or f"b_{uuid.uuid4().hex}"
        if not isinstance(bid, str) or not bid:
            raise ValueError("batch_id must be a non-empty string")
        payload = _compressed_payload(fresh, bid)
        now = _utc_now()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                "INSERT INTO batches(batch_id,payload,event_count,status,attempts,next_attempt_at,created_at) VALUES(?,?,?,?,?,?,?)",
                (bid, payload, len(fresh), "pending", 0, time.time(), now),
            )
            self.db.executemany(
                "INSERT INTO events(event_id,batch_id,event_json,content_sha256) VALUES(?,?,?,?)",
                [(_event_id(event), bid, _json_bytes(event).decode("utf-8"), hashlib.sha256(_json_bytes(event)).hexdigest()) for event in fresh],
            )
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        return bid

    def enqueue_many(
        self,
        events: Iterable[Mapping[str, Any]],
        *,
        max_events: int = 100,
        max_compressed_bytes: int = 1_000_000,
        batch_id: str | None = None,
    ) -> list[str]:
        """Split a stream into bounded immutable batches and persist them.

        Limits are checked before writing.  An individual event larger than the
        limit raises an error so evidence is never silently truncated or dropped.
        """
        if max_events < 1 or max_compressed_bytes < 1:
            raise ValueError("batch limits must be positive")
        ids: list[str] = []
        current: list[Mapping[str, Any]] = []
        chunk_index = 0

        def persist(chunk: list[Mapping[str, Any]]) -> None:
            nonlocal chunk_index
            chosen_id = None if batch_id is None else (batch_id if chunk_index == 0 else f"{batch_id}_{chunk_index}")
            bid = self.enqueue(chunk, batch_id=chosen_id)
            if bid:
                ids.append(bid)
            chunk_index += 1

        for event in events:
            candidate = current + [event]
            if current and (len(candidate) > max_events or len(_compressed_payload([dict(x) for x in candidate])) > max_compressed_bytes):
                persist(current)
                current = [event]
                if len(_compressed_payload([dict(event)])) > max_compressed_bytes:
                    raise ValueError("single event exceeds max_compressed_bytes")
            else:
                current = candidate
                if len(current) == 1 and len(_compressed_payload([dict(event)])) > max_compressed_bytes:
                    raise ValueError("single event exceeds max_compressed_bytes")
        if current:
            persist(current)
        return ids

    def pending(self, *, now: float | None = None, limit: int = 20) -> list[sqlite3.Row]:
        now = time.time() if now is None else now
        return list(self.db.execute(
            "SELECT * FROM batches WHERE status='pending' AND next_attempt_at<=? ORDER BY created_at LIMIT ?",
            (now, int(limit)),
        ))

    def status(self) -> dict[str, int]:
        rows = self.db.execute("SELECT status, COUNT(*) AS n FROM batches GROUP BY status").fetchall()
        result = {key: 0 for key in ("pending", "sent", "failed", "partial", "rejected")}
        result.update({str(row["status"]): int(row["n"]) for row in rows})
        result["events"] = int(self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        return result

    def requeue(self, batch_id: str) -> None:
        changed = self.db.execute(
            "UPDATE batches SET status='pending', next_attempt_at=?, last_error=NULL WHERE batch_id=? AND status IN ('failed','partial','rejected')",
            (time.time(), batch_id),
        ).rowcount
        if changed != 1:
            raise KeyError(f"batch not requeued: {batch_id}")

    def _record_failure(self, row: sqlite3.Row, message: str, *, retryable: bool) -> BatchResult:
        attempts = int(row["attempts"]) + 1
        if retryable:
            # Small jitter prevents a fleet of producers retrying on one edge.
            delay = min(3600.0, 2.0 ** min(attempts - 1, 10)) + random.uniform(0, 0.25)
            status, next_at = "pending", time.time() + delay
        else:
            status, next_at = "failed", time.time()
        self.db.execute(
            "UPDATE batches SET status=?, attempts=?, next_attempt_at=?, last_error=? WHERE batch_id=?",
            (status, attempts, next_at, message[:2000], row["batch_id"]),
        )
        return BatchResult(row["batch_id"], status, attempts, message)

    def flush(self, endpoint: str, *, token: str | None = None, limit: int = 20, timeout: float = 15.0) -> list[BatchResult]:
        """Send due batches.  Network failures are retained and scheduled for retry."""
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("endpoint must use http:// or https://")
        opener = build_opener(_NoRedirect())
        results: list[BatchResult] = []
        for row in self.pending(limit=limit):
            headers = {
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
                "Accept": "application/json",
                "Idempotency-Key": row["batch_id"],
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            req = Request(endpoint, data=bytes(row["payload"]), headers=headers, method="POST")
            try:
                with opener.open(req, timeout=timeout) as response:
                    status_code = int(response.status)
                    response_body = response.read(2_000_000)
                if status_code < 200 or status_code >= 300:
                    raise HTTPError(endpoint, status_code, "non-success response", {}, None)
                ack = json.loads(response_body.decode("utf-8"))
                request_id = validate_ack(ack, int(row["event_count"]))
                self.db.execute(
                    "UPDATE batches SET status='sent', attempts=attempts+1, next_attempt_at=?, sent_at=?, last_error=NULL WHERE batch_id=?",
                    (time.time(), _utc_now(), row["batch_id"]),
                )
                results.append(BatchResult(row["batch_id"], "sent", int(row["attempts"]) + 1, request_id=request_id))
            except HTTPError as exc:
                retryable = exc.code == 429 or exc.code >= 500
                results.append(self._record_failure(row, f"HTTP {exc.code}", retryable=retryable))
            except AckValidationError as exc:
                attempts = int(row["attempts"]) + 1
                status = "partial" if exc.partial else ("rejected" if exc.rejected else "pending")
                delay = time.time() if exc.rejected else time.time() + min(3600.0, 2.0 ** min(attempts - 1, 10))
                self.db.execute(
                    "UPDATE batches SET status=?, attempts=?, next_attempt_at=?, last_error=? WHERE batch_id=?",
                    (status, attempts, delay, str(exc)[:2000], row["batch_id"]),
                )
                results.append(BatchResult(row["batch_id"], status, attempts, str(exc)))
            except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
                results.append(self._record_failure(row, str(exc), retryable=True))
        return results


def validate_ack(ack: Any, event_count: int) -> str | None:
    """Validate the ingestion ACK; reject ambiguous success responses."""
    if not isinstance(ack, dict) or not isinstance(ack.get("data"), dict) or not isinstance(ack.get("meta"), dict):
        raise AckValidationError("ACK must contain data and meta objects")
    data, meta = ack["data"], ack["meta"]
    counts = {key: data.get(key) for key in ("accepted", "duplicate", "rejected")}
    if any(not isinstance(value, int) or value < 0 for value in counts.values()):
        raise AckValidationError("ACK counts must be non-negative integers")
    if sum(counts.values()) != event_count:
        raise AckValidationError("ACK count does not equal batch event_count")
    request_id = meta.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        raise AckValidationError("ACK meta.request_id is required")
    results = data.get("results")
    if results is None and sum(value > 0 for value in counts.values()) > 1:
        raise AckValidationError("ACK results are required when statuses are mixed")
    if results is not None:
        if not isinstance(results, list) or len(results) != event_count:
            raise AckValidationError("ACK results must contain one item per event")
        ids = []
        tally = {"accepted": 0, "duplicate": 0, "rejected": 0}
        for item in results:
            if not isinstance(item, dict) or not isinstance(item.get("event_id"), str) or item.get("status") not in tally:
                raise AckValidationError("invalid ACK result item")
            ids.append(item["event_id"])
            tally[item["status"]] += 1
        if len(set(ids)) != len(ids) or tally != counts:
            raise AckValidationError("ACK result ids or counts are inconsistent")
    if counts["rejected"]:
        raise AckValidationError(
            "ACK contains rejected events",
            rejected=True,
            partial=(counts["accepted"] + counts["duplicate"] > 0),
        )
    return request_id


__all__ = ["BatchResult", "Outbox", "validate_ack"]
