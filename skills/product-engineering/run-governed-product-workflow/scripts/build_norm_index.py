#!/usr/bin/env python3
"""Build the deterministic, content-addressed local norm index.

This module implements TDS-0001 section 7 only.  It deliberately exposes no
agent-facing query gateway, budget packing, coverage decision, or fallback
state machine; those belong to T-015.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from governance_artifacts import (  # noqa: E402
    GovernanceError,
    _write_derived_view,
    atomic_write_json,
    default_profile_index_path,
    embedded_manifest_path,
    governance_root,
    now_utc,
    read_json,
    parse_profile_index,
    require_valid_json_document,
    runtime_asset_path,
    sha256_file,
    validate_embedded_manifest,
)


INDEX_SCHEMA_VERSION = "1.1"
LOCATOR_KIND = "derived-retrieval-locator"
DEFAULT_MAX_BLOCK_CHARS = 4000
DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0
DEFAULT_LOCK_LEASE_SECONDS = 120.0
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
LIST_RE = re.compile(r"^(\s*)(?:[-+*]|\d+[.)])\s+\S")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
TABLE_DELIMITER_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
IDENTIFIER_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?![A-Za-z0-9])")
BACKTICK_RE = re.compile(r"`([^`\n]{1,80})`")
QUOTE_RE = re.compile(r"[“\"]([^“”\"\n]{2,40})[”\"]")

CONTROL_PATTERNS: dict[str, tuple[str, ...]] = {
    "applicability": ("适用", "不适用", "pending", "tailoring", "裁剪", "trigger"),
    "scope": ("范围", "scope", "边界", "in_scope", "out_of_scope", "allowed_paths"),
    "authority": ("authority", "有权", "批准", "权威", "owner", "decision"),
    "permission": ("权限", "授权", "permission", "execution_permissions", "未授权"),
    "prohibition": ("不得", "禁止", "严禁", "失败关闭", "blocked", "prohibited", "must not"),
    "gate": ("gate", "门禁", "进入条件", "退出条件", "review", "验收"),
    "evidence": ("evidence", "证据", "来源", "sha-256", "sha256", "digest", "证明"),
    "integrity": ("完整性", "integrity", "manifest", "哈希", "摘要", "越界", "原子"),
    "freshness": ("陈旧", "过期", "fresh", "stale", "snapshot", "revision", "版本"),
    "change": ("change", "变更", "修订", "影响分析", "回退", "rollback"),
    "execution": ("run", "执行", "attempt", "retry", "stop", "mutation"),
    "validation": ("validation", "verification", "acceptance", "验证", "校验", "验收"),
    "release": ("release", "发布", "上线", "生产", "观察", "rollback"),
    "records": ("record", "记录", "保留", "ledger", "derivedview", "归档"),
    "data": ("data", "数据", "schema", "dataset", "lineage", "retention"),
    "definition": ("定义", "术语", "definition", "是指", "称为"),
    "example": ("示例", "例如", "example"),
    "background": ("目的", "背景", "说明", "context", "概述"),
}


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    logical_path: str
    physical_path: Path
    source_sha256: str
    title: str
    version: str
    status: str
    normalized_text: str
    lines: tuple[str, ...]


class BuildLock:
    """A fail-closed cross-process lease lock with process identity checks."""

    def __init__(self, path: Path, *, timeout_seconds: float, lease_seconds: float) -> None:
        if timeout_seconds < 0 or lease_seconds <= 0:
            raise GovernanceError("lock timeout must be non-negative and lease must be positive")
        self.path = path
        self.timeout_seconds = timeout_seconds
        self.lease_seconds = lease_seconds
        self.nonce = uuid.uuid4().hex
        self.acquired = False
        self.recovered_stale_lock = False

    def _payload(self, *, nonce: str | None = None, lease_seconds: float | None = None) -> dict[str, Any]:
        created = datetime.now(timezone.utc)
        start_token = process_start_token(os.getpid())
        if start_token is None:
            raise GovernanceError("cannot determine current process start identity")
        effective_lease = self.lease_seconds if lease_seconds is None else lease_seconds
        return {
            "schema_version": "1.0",
            "pid": os.getpid(),
            "process_start_token": start_token,
            "created_at": created.isoformat().replace("+00:00", "Z"),
            "lease_expires_at": (created + timedelta(seconds=effective_lease)).isoformat().replace("+00:00", "Z"),
            "nonce": nonce or self.nonce,
        }

    @staticmethod
    def _read_record(path: Path) -> tuple[bytes, dict[str, Any]]:
        try:
            original = path.read_bytes()
            record = json.loads(original.decode("utf-8"))
            int(record["pid"])
            str(record["process_start_token"])
            parse_rfc3339(record["lease_expires_at"])
            if not isinstance(record.get("nonce"), str) or not record["nonce"]:
                raise ValueError("lock nonce is missing")
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise GovernanceError(f"index build lock is invalid and cannot be recovered safely: {path}") from exc
        return original, record

    @staticmethod
    def _is_active_or_leased(record: dict[str, Any]) -> bool:
        pid = int(record["pid"])
        token = str(record["process_start_token"])
        lease = parse_rfc3339(record["lease_expires_at"])
        current_token = process_start_token(pid)
        same_process = current_token is not None and current_token == token
        return same_process or datetime.now(timezone.utc) <= lease

    def _acquire_recovery_guard(self, recovery: Path) -> str | None:
        guard_nonce = uuid.uuid4().hex
        payload = canonical_json_bytes(self._payload(
            nonce=guard_nonce,
            lease_seconds=min(self.lease_seconds, 5.0),
        )) + b"\n"
        while True:
            try:
                descriptor = os.open(recovery, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                return guard_nonce
            except FileExistsError:
                try:
                    original, record = self._read_record(recovery)
                except GovernanceError:
                    try:
                        original = recovery.read_bytes()
                        age_seconds = max(0.0, time.time() - recovery.stat().st_mtime)
                    except FileNotFoundError:
                        continue
                    malformed_grace = min(max(self.lease_seconds, 0.1), 5.0)
                    if age_seconds <= malformed_grace:
                        return None
                    try:
                        if recovery.read_bytes() == original:
                            recovery.unlink()
                    except FileNotFoundError:
                        pass
                    continue
                if self._is_active_or_leased(record):
                    return None
                try:
                    if recovery.read_bytes() == original:
                        recovery.unlink()
                except FileNotFoundError:
                    pass

    @staticmethod
    def _release_recovery_guard(recovery: Path, guard_nonce: str) -> None:
        try:
            _, record = BuildLock._read_record(recovery)
            if record.get("nonce") != guard_nonce:
                raise GovernanceError(f"recovery guard ownership changed unexpectedly: {recovery}")
            recovery.unlink()
        except FileNotFoundError:
            raise GovernanceError(f"recovery guard disappeared before release: {recovery}")

    def _try_recover(self) -> bool:
        try:
            original, record = self._read_record(self.path)
        except GovernanceError:
            try:
                age_seconds = max(0.0, time.time() - self.path.stat().st_mtime)
            except FileNotFoundError:
                return True
            main_record_grace = min(max(self.lease_seconds, 0.1), 1.0)
            if age_seconds <= main_record_grace:
                return False
            raise
        if self._is_active_or_leased(record):
            return False
        recovery = self.path.with_name(f"{self.path.name}.recover")
        guard_nonce = self._acquire_recovery_guard(recovery)
        if guard_nonce is None:
            return False
        try:
            if not self.path.is_file() or self.path.read_bytes() != original:
                return False
            self.path.unlink()
            self.recovered_stale_lock = True
            return True
        finally:
            self._release_recovery_guard(recovery, guard_nonce)

    def __enter__(self) -> "BuildLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_seconds
        payload = canonical_json_bytes(self._payload()) + b"\n"
        while True:
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                self.acquired = True
                return self
            except FileExistsError:
                if self._try_recover():
                    continue
                if time.monotonic() >= deadline:
                    raise GovernanceError(f"index build lock timeout: {self.path}")
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))

    def __exit__(self, exc_type, exc, traceback) -> None:  # type: ignore[no-untyped-def]
        if not self.acquired:
            return
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
            if record.get("nonce") != self.nonce:
                raise GovernanceError(f"index build lock ownership changed unexpectedly: {self.path}")
            self.path.unlink()
        except FileNotFoundError as error:
            raise GovernanceError(f"index build lock disappeared before release: {self.path}") from error
        finally:
            self.acquired = False


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def normalize_term(value: str) -> str:
    return normalize_text(value).strip().casefold()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def ordered_rows_digest(rows: Iterable[Iterable[Any]]) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    for row in rows:
        encoded = canonical_json_bytes(list(row))
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        count += 1
    return count, digest.hexdigest()


def parse_rfc3339(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def process_start_token(pid: int) -> str | None:
    """Return an OS process creation token, not merely a liveness answer."""

    if pid <= 0:
        return None
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        creation = ctypes.c_ulonglong()
        exit_time = ctypes.c_ulonglong()
        kernel = ctypes.c_ulonglong()
        user = ctypes.c_ulonglong()
        exit_code = ctypes.c_ulong()
        try:
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
                return None
            ok = kernel32.GetProcessTimes(
                handle,
                ctypes.byref(creation),
                ctypes.byref(exit_time),
                ctypes.byref(kernel),
                ctypes.byref(user),
            )
            return str(creation.value) if ok else None
        finally:
            kernel32.CloseHandle(handle)
    stat_path = Path("/proc") / str(pid) / "stat"
    try:
        fields = stat_path.read_text(encoding="ascii").split()
        return fields[21]
    except (OSError, IndexError, UnicodeError):
        try:
            os.kill(pid, 0)
        except OSError:
            return None
        return f"alive-without-start:{pid}"


def atomic_replace_durable(source: Path, target: Path) -> None:
    """Atomically replace target and request durable directory metadata."""

    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        move_file_ex = kernel32.MoveFileExW
        move_file_ex.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint)
        move_file_ex.restype = ctypes.c_int
        movefile_replace_existing = 0x1
        movefile_write_through = 0x8
        if not move_file_ex(
            str(source),
            str(target),
            movefile_replace_existing | movefile_write_through,
        ):
            raise ctypes.WinError()
        return
    os.replace(source, target)
    directory_descriptor = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def source_metadata(lines: tuple[str, ...], fallback_id: str) -> tuple[str, str, str]:
    title = fallback_id
    version = "Unspecified"
    status = "Unspecified"
    for line in lines:
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1:
            title = match.group(2).strip()
            break
    for line in lines[:80]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key, value = cells[0], cells[1]
        if key in {"版本", "文档版本", "Revision"} and value:
            version = value
        elif key in {"状态", "文档状态", "State"} and value:
            status = value
    return title, version, status


def load_sources() -> tuple[list[SourceDocument], str]:
    mapping_path = runtime_asset_path("mappings/tailoring-applicability-map.json")
    profile_path = runtime_asset_path("mappings/profile-meta-map.json")
    mapping = read_json(mapping_path)
    catalog = mapping.get("source_catalog")
    if not isinstance(catalog, list) or len(catalog) != 22:
        raise GovernanceError("tailoring source_catalog must contain exactly 22 sources")
    documents: list[SourceDocument] = []
    for position, item in enumerate(catalog, 1):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("path"), str):
            raise GovernanceError(f"source_catalog[{position}] is invalid")
        physical = runtime_asset_path(item["path"])
        raw = physical.read_bytes()
        decoded = raw.decode("utf-8-sig")
        normalized = decoded.replace("\r\n", "\n").replace("\r", "\n")
        lines = tuple(normalized.splitlines())
        title, version, status = source_metadata(lines, item["id"])
        documents.append(SourceDocument(
            source_id=item["id"],
            logical_path=item["path"],
            physical_path=physical,
            source_sha256=sha256_bytes(raw),
            title=title,
            version=version,
            status=status,
            normalized_text=normalized,
            lines=lines,
        ))
    aggregate = hashlib.sha256()
    for source in sorted(documents, key=lambda item: item.source_id):
        aggregate.update(source.source_id.encode("utf-8"))
        aggregate.update(bytes.fromhex(source.source_sha256))
    aggregate.update(hashlib.sha256(profile_path.read_bytes()).digest())
    return documents, aggregate.hexdigest()


def consistency_audit_digest(document: dict[str, Any]) -> str:
    keys = (
        "report_version", "project_id", "task_id", "scope", "inputs", "findings",
        "manual_review_inventory", "norm_index_ready", "protected_assets_unchanged",
    )
    try:
        body = {key: document[key] for key in keys}
    except KeyError as exc:
        raise GovernanceError(f"consistency report is missing {exc.args[0]}") from exc
    return sha256_bytes(canonical_json_bytes(body))


def validate_consistency_report(
    report: dict[str, Any], *, normative_sources_sha256: str, manifest_sha256: str
) -> None:
    require_valid_json_document(report, "norm-consistency-report.schema.json", "consistency_report")
    blockers: list[str] = []
    if report.get("audit_status") != "Complete":
        blockers.append("audit_status is not Complete")
    if report.get("norm_index_ready") is not True:
        blockers.append("norm_index_ready is not true")
    if report.get("protected_assets_unchanged") is not True:
        blockers.append("protected_assets_unchanged is not true")
    severity = report.get("summary", {}).get("by_severity", {})
    if severity.get("Blocker") != 0 or severity.get("Major") != 0:
        blockers.append("consistency report contains unresolved Blocker or Major findings")
    inputs = report.get("inputs", {})
    if inputs.get("normative_sources_sha256") != normative_sources_sha256:
        blockers.append("consistency report normative_sources_sha256 is stale")
    if inputs.get("manifest_sha256") != manifest_sha256:
        blockers.append("consistency report manifest_sha256 is stale")
    if report.get("audit_digest") != consistency_audit_digest(report):
        blockers.append("consistency report audit_digest is invalid")
    if blockers:
        raise GovernanceError("norm index build blocked: " + "; ".join(blockers))


def heading_hash(heading_path: Iterable[str]) -> str:
    return sha256_bytes(normalize_text("\n".join(heading_path)).encode("utf-8"))


def deterministic_spans(text: str, maximum: int) -> list[tuple[int, int]]:
    if maximum < 64:
        raise GovernanceError("max block chars must be at least 64")
    if len(text) <= maximum:
        return [(0, len(text))]
    boundaries = [match.end() for match in re.finditer(r"(?:[。！？.!?；;]\s*|\n+)", text)]
    spans: list[tuple[int, int]] = []
    start = 0
    while start < len(text):
        hard_end = min(len(text), start + maximum)
        candidates = [item for item in boundaries if start + maximum // 2 <= item <= hard_end]
        end = candidates[-1] if candidates else hard_end
        if end <= start:
            end = hard_end
        spans.append((start, end))
        start = end
    if "".join(text[start:end] for start, end in spans) != text:
        raise GovernanceError("deterministic long-block split lost source text")
    return spans


def is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def raw_blocks(lines: tuple[str, ...]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    headings: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            headings = headings[:level - 1]
            headings.append(title)
            blocks.append({
                "structure_kind": "heading",
                "line_start": index + 1,
                "line_end": index + 1,
                "text": line,
                "heading_path": list(headings),
                "table_header": None,
            })
            index += 1
            continue
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)[0]
            width = len(fence.group(1))
            end = index + 1
            while end < len(lines):
                closing = lines[end].lstrip()
                if closing.startswith(marker * width):
                    end += 1
                    break
                end += 1
            if end > len(lines) or not lines[end - 1].lstrip().startswith(marker * width):
                raise GovernanceError(f"unterminated fenced code block at line {index + 1}")
            if blocks:
                previous = blocks[-1]
                previous["line_end"] = end
                previous["text"] = "\n".join(lines[previous["line_start"] - 1:end])
                previous["structure_kind"] = f"{previous['structure_kind']}+code"
            else:
                blocks.append({
                    "structure_kind": "code",
                    "line_start": index + 1,
                    "line_end": end,
                    "text": "\n".join(lines[index:end]),
                    "heading_path": list(headings),
                    "table_header": None,
                })
            index = end
            continue
        if is_table_row(line) and index + 1 < len(lines) and TABLE_DELIMITER_RE.match(lines[index + 1]):
            header = line
            blocks.append({
                "structure_kind": "table-header",
                "line_start": index + 1,
                "line_end": index + 2,
                "text": "\n".join(lines[index:index + 2]),
                "heading_path": list(headings),
                "table_header": header,
            })
            index += 2
            while index < len(lines) and is_table_row(lines[index]) and lines[index].strip():
                blocks.append({
                    "structure_kind": "table-row",
                    "line_start": index + 1,
                    "line_end": index + 1,
                    "text": lines[index],
                    "heading_path": list(headings),
                    "table_header": header,
                })
                index += 1
            continue
        if LIST_RE.match(line):
            start = index
            index += 1
            while index < len(lines) and lines[index].strip():
                if HEADING_RE.match(lines[index]) or FENCE_RE.match(lines[index]):
                    break
                next_list = LIST_RE.match(lines[index])
                if next_list:
                    break
                if is_table_row(lines[index]):
                    break
                index += 1
            blocks.append({
                "structure_kind": "list-item",
                "line_start": start + 1,
                "line_end": index,
                "text": "\n".join(lines[start:index]),
                "heading_path": list(headings),
                "table_header": None,
            })
            continue
        start = index
        index += 1
        while index < len(lines) and lines[index].strip():
            if HEADING_RE.match(lines[index]) or FENCE_RE.match(lines[index]) or LIST_RE.match(lines[index]):
                break
            if is_table_row(lines[index]) and index + 1 < len(lines) and TABLE_DELIMITER_RE.match(lines[index + 1]):
                break
            index += 1
        blocks.append({
            "structure_kind": "paragraph",
            "line_start": start + 1,
            "line_end": index,
            "text": "\n".join(lines[start:index]),
            "heading_path": list(headings),
            "table_header": None,
        })
    return blocks


def modality_for(text: str, taxonomy: dict[str, Any]) -> str:
    folded = normalize_term(text)
    modalities = taxonomy.get("normative_modalities", {})
    for key in ("must_not", "must", "should", "may"):
        for term in modalities.get(key, []):
            if normalize_term(term) in folded:
                return key
    return "informative"


def tags_for(text: str, heading_path: list[str], taxonomy: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    context = normalize_term("\n".join(heading_path + [text]))
    actions: list[str] = []
    stages: set[str] = set()
    controls: set[str] = set()
    for action_id, action in taxonomy.get("actions", {}).items():
        terms = list(action.get("keywords", [])) + list(action.get("identifiers", []))
        if any(normalize_term(term) in context for term in terms):
            actions.append(action_id)
            stages.update(action.get("stages", []))
            controls.update(action.get("required_control_types", []))
            controls.update(action.get("pinned_control_types", []))
    for control, patterns in CONTROL_PATTERNS.items():
        if any(normalize_term(pattern) in context for pattern in patterns):
            controls.add(control)
    return sorted(actions), sorted(stages), sorted(controls)


def parse_source(
    source: SourceDocument, taxonomy: dict[str, Any], *, max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for block in raw_blocks(source.lines):
        parent_hash = sha256_bytes(block["text"].encode("utf-8"))
        for span_start, span_end in deterministic_spans(block["text"], max_block_chars):
            text = block["text"][span_start:span_end]
            if not text:
                continue
            ordinal = len(records) + 1
            heading = list(block["heading_path"])
            chunk_hash = sha256_bytes(text.encode("utf-8"))
            actions, stages, controls = tags_for(text, heading, taxonomy)
            context_parts = [
                f"[{source.source_id}]",
                f"[{source.title}]",
                f"[{' > '.join(heading)}]",
                f"[stages={','.join(stages)};controls={','.join(controls)};actions={','.join(actions)}]",
            ]
            if block["table_header"] and block["structure_kind"] == "table-row":
                context_parts.append(f"[table-header={block['table_header']}]")
            context_parts.append(text)
            context_text = "\n".join(context_parts)
            line_start = block["line_start"] + block["text"][:span_start].count("\n")
            line_end = block["line_start"] + block["text"][:span_end].count("\n")
            range_char_start = len(block["text"][:span_start].rsplit("\n", 1)[-1])
            range_char_end = range_char_start + len(text)
            retrieval_locator = ":".join((
                source.source_id,
                source.source_sha256[:8],
                heading_hash(heading)[:8],
                str(ordinal),
                chunk_hash[:8],
            ))
            records.append({
                "retrieval_locator": retrieval_locator,
                "locator_kind": LOCATOR_KIND,
                "source_id": source.source_id,
                "source_version": source.version,
                "logical_path": source.logical_path,
                "source_sha256": source.source_sha256,
                "source_status": source.status,
                "source_title": source.title,
                "heading_path": heading,
                "line_start": line_start,
                "line_end": line_end,
                "span_start": span_start,
                "span_end": span_end,
                "range_char_start": range_char_start,
                "range_char_end": range_char_end,
                "text": text,
                "chunk_sha256": chunk_hash,
                "normative_modality": modality_for(text, taxonomy),
                "control_types": controls,
                "stage_tags": stages,
                "action_tags": actions,
                "ordinal": ordinal,
                "structure_kind": block["structure_kind"],
                "parent_block_sha256": parent_hash,
                "table_header": block["table_header"],
                "context_text": context_text,
                "context_sha256": sha256_bytes(context_text.encode("utf-8")),
            })
    locators = [item["retrieval_locator"] for item in records]
    if len(locators) != len(set(locators)):
        raise GovernanceError(f"duplicate retrieval locator in source {source.source_id}")
    return records


def profile_terms() -> set[str]:
    mapping = read_json(runtime_asset_path("mappings/profile-meta-map.json"))
    terms: set[str] = set()
    overrides = mapping.get("overrides", {})
    if isinstance(overrides, dict):
        for meta_type, profiles in overrides.items():
            terms.add(meta_type)
            if isinstance(profiles, str):
                terms.update(profiles.split())
            elif isinstance(profiles, list):
                terms.update(item for item in profiles if isinstance(item, str))
    terms.update(item["legacy_kind"] for item in parse_profile_index(default_profile_index_path()))
    return {term for term in terms if term}


def known_terms(taxonomy: dict[str, Any], source_ids: Iterable[str]) -> dict[str, str]:
    terms: dict[str, str] = {item: "source-id" for item in source_ids}
    terms.update({item: "profile-id" for item in profile_terms()})
    for action_id, action in taxonomy.get("actions", {}).items():
        terms[action_id] = "action-id"
        for value in list(action.get("keywords", [])) + list(action.get("identifiers", [])):
            terms[value] = "action-term"
    for control in taxonomy.get("control_types", {}):
        terms[control] = "control-type"
    for values in taxonomy.get("normative_modalities", {}).values():
        for value in values:
            terms[value] = "modality"
    for value in taxonomy.get("negation_terms", []):
        terms[value] = "negation-term"
    return terms


def effective_index_schema_version(max_block_chars: int) -> str:
    if max_block_chars < 64:
        raise GovernanceError("max block chars must be at least 64")
    return f"{INDEX_SCHEMA_VERSION};max_block_chars={max_block_chars}"


def contains_controlled_term(context: str, term: str) -> bool:
    folded = normalize_term(context)
    needle = normalize_term(term)
    if not needle:
        return False
    if re.fullmatch(r"[a-z0-9_-]+", needle):
        return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", folded) is not None
    return needle in folded


def clause_exact_terms(record: dict[str, Any], controlled_terms: dict[str, str]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = {(record["source_id"], "source-id")}
    context = record["context_text"]
    for term, kind in controlled_terms.items():
        if contains_controlled_term(context, term):
            result.add((term, kind))
    for match in IDENTIFIER_RE.finditer(context):
        result.add((match.group(0), "identifier"))
    for pattern, kind in ((BACKTICK_RE, "quoted-term"), (QUOTE_RE, "quoted-term")):
        for match in pattern.finditer(context):
            value = match.group(1).strip()
            if value:
                result.add((value, kind))
    return result


def compute_index_digest(
    normative_sources_sha256: str,
    consistency_report_sha256: str,
    parser_sha256: str,
    action_taxonomy_sha256: str,
    *,
    index_schema_version: str = INDEX_SCHEMA_VERSION,
) -> str:
    material = "".join((
        normative_sources_sha256,
        consistency_report_sha256,
        parser_sha256,
        index_schema_version,
        action_taxonomy_sha256,
    ))
    return sha256_bytes(material.encode("ascii"))


def create_sqlite_index(
    path: Path,
    *,
    records: list[dict[str, Any]],
    sources: list[SourceDocument],
    controlled_terms: dict[str, str],
    metadata: dict[str, Any],
) -> str:
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.executescript("""
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
            CREATE TABLE sources (
                source_id TEXT PRIMARY KEY,
                logical_path TEXT NOT NULL UNIQUE,
                source_sha256 TEXT NOT NULL,
                source_title TEXT NOT NULL,
                source_version TEXT NOT NULL,
                source_status TEXT NOT NULL,
                line_count INTEGER NOT NULL CHECK(line_count >= 0)
            ) WITHOUT ROWID;
            CREATE TABLE clauses (
                retrieval_locator TEXT PRIMARY KEY,
                locator_kind TEXT NOT NULL CHECK(locator_kind = 'derived-retrieval-locator'),
                source_id TEXT NOT NULL REFERENCES sources(source_id),
                source_version TEXT NOT NULL,
                logical_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                source_status TEXT NOT NULL,
                source_title TEXT NOT NULL,
                heading_path_json TEXT NOT NULL,
                line_start INTEGER NOT NULL CHECK(line_start >= 1),
                line_end INTEGER NOT NULL CHECK(line_end >= line_start),
                span_start INTEGER NOT NULL CHECK(span_start >= 0),
                span_end INTEGER NOT NULL CHECK(span_end > span_start),
                range_char_start INTEGER NOT NULL CHECK(range_char_start >= 0),
                range_char_end INTEGER NOT NULL CHECK(range_char_end > range_char_start),
                text TEXT NOT NULL,
                chunk_sha256 TEXT NOT NULL,
                normative_modality TEXT NOT NULL,
                control_types_json TEXT NOT NULL,
                stage_tags_json TEXT NOT NULL,
                action_tags_json TEXT NOT NULL,
                ordinal INTEGER NOT NULL CHECK(ordinal >= 1),
                structure_kind TEXT NOT NULL,
                parent_block_sha256 TEXT NOT NULL,
                table_header TEXT,
                context_text TEXT NOT NULL,
                context_sha256 TEXT NOT NULL,
                UNIQUE(source_id, ordinal)
            );
            CREATE INDEX clauses_source_line ON clauses(source_id, line_start, line_end);
            CREATE TABLE exact_terms (
                normalized_term TEXT NOT NULL,
                term TEXT NOT NULL,
                term_kind TEXT NOT NULL,
                retrieval_locator TEXT NOT NULL REFERENCES clauses(retrieval_locator),
                PRIMARY KEY(normalized_term, retrieval_locator, term_kind)
            ) WITHOUT ROWID;
            CREATE VIRTUAL TABLE clauses_unicode USING fts5(
                retrieval_locator UNINDEXED,
                context_text,
                tokenize='unicode61 remove_diacritics 2'
            );
            CREATE VIRTUAL TABLE clauses_trigram USING fts5(
                retrieval_locator UNINDEXED,
                context_text,
                tokenize='trigram'
            );
        """)
        for source in sources:
            connection.execute(
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?)",
                (source.source_id, source.logical_path, source.source_sha256, source.title,
                 source.version, source.status, len(source.lines)),
            )
        for record in records:
            connection.execute(
                """INSERT INTO clauses VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )""",
                (
                    record["retrieval_locator"], record["locator_kind"], record["source_id"],
                    record["source_version"], record["logical_path"], record["source_sha256"],
                    record["source_status"], record["source_title"],
                    json.dumps(record["heading_path"], ensure_ascii=False, separators=(",", ":")),
                    record["line_start"], record["line_end"], record["span_start"], record["span_end"],
                    record["range_char_start"], record["range_char_end"],
                    record["text"], record["chunk_sha256"], record["normative_modality"],
                    json.dumps(record["control_types"], ensure_ascii=False, separators=(",", ":")),
                    json.dumps(record["stage_tags"], ensure_ascii=False, separators=(",", ":")),
                    json.dumps(record["action_tags"], ensure_ascii=False, separators=(",", ":")),
                    record["ordinal"], record["structure_kind"], record["parent_block_sha256"],
                    record["table_header"], record["context_text"], record["context_sha256"],
                ),
            )
            connection.execute(
                "INSERT INTO clauses_unicode(retrieval_locator, context_text) VALUES (?, ?)",
                (record["retrieval_locator"], record["context_text"]),
            )
            connection.execute(
                "INSERT INTO clauses_trigram(retrieval_locator, context_text) VALUES (?, ?)",
                (record["retrieval_locator"], record["context_text"]),
            )
            for term, kind in sorted(clause_exact_terms(record, controlled_terms), key=lambda item: (normalize_term(item[0]), item[1], item[0])):
                connection.execute(
                    "INSERT OR IGNORE INTO exact_terms VALUES (?, ?, ?, ?)",
                    (normalize_term(term), term, kind, record["retrieval_locator"]),
                )
        exact_term_count, exact_terms_digest = ordered_rows_digest(connection.execute(
            """SELECT normalized_term, term, term_kind, retrieval_locator
               FROM exact_terms
               ORDER BY normalized_term, term, term_kind, retrieval_locator"""
        ))
        stored_metadata = {
            **metadata,
            "exact_term_count": exact_term_count,
            "exact_terms_digest": exact_terms_digest,
        }
        for key, value in sorted(stored_metadata.items()):
            connection.execute(
                "INSERT INTO metadata VALUES (?, ?)",
                (key, json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
            )
        content_digest = sha256_bytes(canonical_json_bytes([
            {key: record[key] for key in (
                "retrieval_locator", "source_id", "logical_path", "source_sha256", "heading_path",
                "line_start", "line_end", "span_start", "span_end", "range_char_start", "range_char_end",
                "chunk_sha256", "context_sha256",
                "normative_modality", "control_types", "stage_tags", "action_tags", "ordinal",
            )}
            for record in records
        ]))
        connection.execute("INSERT INTO metadata VALUES (?, ?)", ("content_digest", json.dumps(content_digest)))
        connection.execute("INSERT INTO metadata VALUES (?, ?)", ("completion_marker", "true"))
        connection.commit()
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if result != ("ok",):
            raise GovernanceError(f"SQLite integrity_check failed: {result}")
        return content_digest
    finally:
        connection.close()


def read_sqlite_metadata(connection: sqlite3.Connection) -> dict[str, Any]:
    try:
        return {key: json.loads(value) for key, value in connection.execute("SELECT key, value FROM metadata")}
    except (sqlite3.Error, json.JSONDecodeError) as exc:
        raise GovernanceError("index metadata table is invalid") from exc


def verify_index_content(connection: sqlite3.Connection, stored: dict[str, Any]) -> str:
    source_ids = stored.get("source_ids")
    if not isinstance(source_ids, list) or not all(isinstance(item, str) for item in source_ids):
        raise GovernanceError("index source_ids metadata is invalid")
    source_order = {source_id: position for position, source_id in enumerate(source_ids)}
    connection.row_factory = sqlite3.Row
    source_rows = {row["source_id"]: dict(row) for row in connection.execute("SELECT * FROM sources")}
    if set(source_rows) != set(source_ids):
        raise GovernanceError("index sources table does not match source_ids metadata")
    for source_id in source_ids:
        source_row = source_rows[source_id]
        current = runtime_asset_path(source_row["logical_path"])
        if sha256_file(current) != source_row["source_sha256"]:
            raise GovernanceError(f"index source row is stale: {source_id}")
    mismatch = connection.execute("""
        SELECT COUNT(*)
        FROM clauses AS c JOIN sources AS s ON s.source_id = c.source_id
        WHERE c.logical_path <> s.logical_path OR c.source_sha256 <> s.source_sha256
    """).fetchone()[0]
    if mismatch:
        raise GovernanceError("index clause/source provenance rows are inconsistent")
    rows = [dict(row) for row in connection.execute("SELECT * FROM clauses")]
    try:
        rows.sort(key=lambda row: (source_order[row["source_id"]], row["ordinal"]))
    except KeyError as exc:
        raise GovernanceError(f"index clause references an unknown source: {exc.args[0]}") from exc
    canonical: list[dict[str, Any]] = []
    for row in rows:
        try:
            heading = json.loads(row["heading_path_json"])
            controls = json.loads(row["control_types_json"])
            stages = json.loads(row["stage_tags_json"])
            actions = json.loads(row["action_tags_json"])
        except json.JSONDecodeError as exc:
            raise GovernanceError("index clause contains invalid JSON metadata") from exc
        if sha256_bytes(row["text"].encode("utf-8")) != row["chunk_sha256"]:
            raise GovernanceError(f"index clause text hash mismatch: {row['retrieval_locator']}")
        if sha256_bytes(row["context_text"].encode("utf-8")) != row["context_sha256"]:
            raise GovernanceError(f"index clause context hash mismatch: {row['retrieval_locator']}")
        expected_locator = ":".join((
            row["source_id"], row["source_sha256"][:8], heading_hash(heading)[:8],
            str(row["ordinal"]), row["chunk_sha256"][:8],
        ))
        if row["locator_kind"] != LOCATOR_KIND or row["retrieval_locator"] != expected_locator:
            raise GovernanceError(f"index clause locator is invalid: {row['retrieval_locator']}")
        canonical.append({
            "retrieval_locator": row["retrieval_locator"],
            "source_id": row["source_id"],
            "logical_path": row["logical_path"],
            "source_sha256": row["source_sha256"],
            "heading_path": heading,
            "line_start": row["line_start"],
            "line_end": row["line_end"],
            "span_start": row["span_start"],
            "span_end": row["span_end"],
            "range_char_start": row["range_char_start"],
            "range_char_end": row["range_char_end"],
            "chunk_sha256": row["chunk_sha256"],
            "context_sha256": row["context_sha256"],
            "normative_modality": row["normative_modality"],
            "control_types": controls,
            "stage_tags": stages,
            "action_tags": actions,
            "ordinal": row["ordinal"],
        })
    content_digest = sha256_bytes(canonical_json_bytes(canonical))
    if content_digest != stored.get("content_digest"):
        raise GovernanceError("index content_digest does not match canonical clause rows")
    exact_term_count, exact_terms_digest = ordered_rows_digest(connection.execute(
        """SELECT normalized_term, term, term_kind, retrieval_locator
           FROM exact_terms
           ORDER BY normalized_term, term, term_kind, retrieval_locator"""
    ))
    if (
        exact_term_count != stored.get("exact_term_count")
        or exact_terms_digest != stored.get("exact_terms_digest")
    ):
        raise GovernanceError("index exact_terms closure does not match metadata")
    clause_count = len(rows)
    for table in ("clauses_unicode", "clauses_trigram"):
        if connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] != clause_count:
            raise GovernanceError(f"index {table} row count does not match clauses")
        expected_fts = ordered_rows_digest(
            (row["retrieval_locator"], row["context_text"])
            for row in sorted(rows, key=lambda item: item["retrieval_locator"])
        )
        actual_fts = ordered_rows_digest(connection.execute(
            f"SELECT retrieval_locator, context_text FROM {table} ORDER BY retrieval_locator"
        ))
        if actual_fts != expected_fts:
            raise GovernanceError(f"index {table} contents do not match clauses")
    return content_digest


def validate_index(
    path: Path, expected: dict[str, Any], *, require_formal_name: bool = True
) -> dict[str, Any]:
    if not path.is_file() or (
        require_formal_name and path.name != f"{expected['index_digest']}.sqlite3"
    ):
        raise GovernanceError(f"formal norm index is missing or misnamed: {path}")
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if result != ("ok",):
            raise GovernanceError(f"formal index integrity_check failed: {result}")
        stored = read_sqlite_metadata(connection)
        if stored.get("completion_marker") is not True:
            raise GovernanceError("formal index has no completion marker")
        verify_index_content(connection, stored)
        for key, value in expected.items():
            if stored.get(key) != value:
                raise GovernanceError(f"formal index metadata mismatch: {key}")
        clause_count = connection.execute("SELECT COUNT(*) FROM clauses").fetchone()[0]
        source_count = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        if clause_count != expected["clause_count"] or source_count != expected["source_count"]:
            raise GovernanceError("formal index row counts do not match metadata")
        return stored
    except sqlite3.Error as exc:
        raise GovernanceError(f"cannot open formal norm index read-only: {path}: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()


def metadata_document(base: dict[str, Any], *, cache_relative: str, created_at: str) -> dict[str, Any]:
    document = {
        "schema_version": "6.3-candidate",
        "index_schema_version": base["index_schema_version"],
        "index_digest": base["index_digest"],
        "status": "Ready",
        "created_at": created_at,
        "normative_sources_sha256": base["normative_sources_sha256"],
        "consistency_report_sha256": base["consistency_report_sha256"],
        "parser_sha256": base["parser_sha256"],
        "action_taxonomy_sha256": base["action_taxonomy_sha256"],
        "source_ids": base["source_ids"],
        "source_count": base["source_count"],
        "clause_count": base["clause_count"],
        "storage": {
            "engine": "sqlite3-fts5",
            "sqlite_version": sqlite3.sqlite_version,
            "fts_modes": ["unicode61", "trigram"],
            "relative_cache_path": cache_relative,
        },
        "integrity": {
            "sqlite_integrity_check": "ok",
            "source_hashes_verified": True,
            "completion_marker": True,
        },
        "blocker_reasons": [],
    }
    require_valid_json_document(document, "norm-index-metadata.schema.json", "index_metadata")
    return document


def build_index(
    project_root: Path,
    consistency_report_path: Path,
    *,
    force_rebuild: bool = False,
    max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    lock_timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    lock_lease_seconds: float = DEFAULT_LOCK_LEASE_SECONDS,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    manifest_errors = validate_embedded_manifest()
    if manifest_errors:
        raise GovernanceError("embedded runtime integrity failed: " + "; ".join(manifest_errors))
    if not consistency_report_path.is_file():
        raise GovernanceError(f"consistency report is missing: {consistency_report_path}")
    sources, normative_digest = load_sources()
    manifest_sha = sha256_file(embedded_manifest_path())
    report = read_json(consistency_report_path)
    validate_consistency_report(report, normative_sources_sha256=normative_digest, manifest_sha256=manifest_sha)
    taxonomy_path = runtime_asset_path("mappings/norm-action-taxonomy.json")
    taxonomy = read_json(taxonomy_path)
    parser_sha = sha256_file(Path(__file__).resolve())
    report_sha = sha256_file(consistency_report_path)
    taxonomy_sha = sha256_file(taxonomy_path)
    schema_identity = effective_index_schema_version(max_block_chars)
    index_digest = compute_index_digest(
        normative_digest,
        report_sha,
        parser_sha,
        taxonomy_sha,
        index_schema_version=schema_identity,
    )
    identity = {
        "index_digest": index_digest,
        "index_schema_version": schema_identity,
        "normative_sources_sha256": normative_digest,
        "consistency_report_sha256": report_sha,
        "parser_sha256": parser_sha,
        "action_taxonomy_sha256": taxonomy_sha,
        "source_ids": [source.source_id for source in sources],
        "source_count": len(sources),
    }
    cache_dir = governance_root(project_root) / "runtime-cache" / "norm-index"
    cache_dir.mkdir(parents=True, exist_ok=True)
    formal = cache_dir / f"{index_digest}.sqlite3"
    relative = f".project-governance/runtime-cache/norm-index/{index_digest}.sqlite3"
    lock_path = cache_dir / f"{index_digest}.lock"
    build_status = "Reused"
    recovered = False
    with BuildLock(lock_path, timeout_seconds=lock_timeout_seconds, lease_seconds=lock_lease_seconds) as lock:
        recovered = lock.recovered_stale_lock
        if formal.is_file() and not force_rebuild:
            stored = read_existing_metadata(formal, identity)
            clause_count = stored.get("clause_count")
            created_at = stored.get("created_at")
            if not isinstance(clause_count, int) or clause_count < 0 or not isinstance(created_at, str):
                raise GovernanceError("existing index has invalid clause_count or created_at metadata")
            base = {**identity, "clause_count": clause_count}
            expected = {**base, "created_at": created_at}
            stored = validate_index(formal, expected)
            content_digest, structure_counts, modality_counts = index_statistics(formal)
        else:
            records = [
                record
                for source in sources
                for record in parse_source(source, taxonomy, max_block_chars=max_block_chars)
            ]
            base = {**identity, "clause_count": len(records)}
            controlled = known_terms(taxonomy, base["source_ids"])
            created_at = now_utc()
            expected = dict(base)
            expected["created_at"] = created_at
            temp_path = cache_dir / f".{index_digest}.{os.getpid()}.{uuid.uuid4().hex}.tmp.sqlite3"
            try:
                content_digest = create_sqlite_index(
                    temp_path,
                    records=records,
                    sources=sources,
                    controlled_terms=controlled,
                    metadata=expected,
                )
                validate_index(temp_path, expected, require_formal_name=False)
                with temp_path.open("r+b") as stream:
                    os.fsync(stream.fileno())
                atomic_replace_durable(temp_path, formal)
                validate_index(formal, expected)
                build_status = "Built"
                structure_counts = count_values(record["structure_kind"] for record in records)
                modality_counts = count_values(record["normative_modality"] for record in records)
            finally:
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass
    prune_warnings = prune_runtime_index_cache(cache_dir, index_digest)
    document = metadata_document(base, cache_relative=relative, created_at=created_at)
    stats = {
        "build_status": build_status,
        "recovered_stale_lock": recovered,
        "cache_prune_warnings": prune_warnings,
        "content_digest": content_digest,
        "structure_counts": structure_counts,
        "modality_counts": modality_counts,
    }
    return formal, document, stats


def prune_runtime_index_cache(cache_dir: Path, active_digest: str) -> list[str]:
    """Keep only the active runtime index digest; stale cleanup never blocks use."""

    warnings: list[str] = []
    keep = {
        f"{active_digest}.sqlite3",
        f"{active_digest}.lock",
    }
    for path in sorted(cache_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name in keep:
            continue
        if path.name.startswith(f".{active_digest}."):
            continue
        if path.suffix not in {".sqlite3", ".lock"}:
            continue
        try:
            path.unlink()
        except OSError as exc:
            warnings.append(f"{path.name}: {exc}")
    return warnings


def read_existing_metadata(path: Path, identity: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise GovernanceError(f"formal index is missing: {path}")
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        stored = read_sqlite_metadata(connection)
    except sqlite3.Error as exc:
        raise GovernanceError(f"existing index cannot be opened: {path}: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()
    for key, value in identity.items():
        if stored.get(key) != value:
            raise GovernanceError(f"existing index metadata mismatch: {key}")
    if stored.get("completion_marker") is not True:
        raise GovernanceError("existing index has no completion marker")
    return stored


def index_statistics(path: Path) -> tuple[str, dict[str, int], dict[str, int]]:
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        stored = read_sqlite_metadata(connection)
        content_digest = stored.get("content_digest")
        if not isinstance(content_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", content_digest):
            raise GovernanceError("existing index content_digest is invalid")
        structure = dict(connection.execute(
            "SELECT structure_kind, COUNT(*) FROM clauses GROUP BY structure_kind ORDER BY structure_kind"
        ).fetchall())
        modality = dict(connection.execute(
            "SELECT normative_modality, COUNT(*) FROM clauses GROUP BY normative_modality ORDER BY normative_modality"
        ).fetchall())
        return content_digest, structure, modality
    except sqlite3.Error as exc:
        raise GovernanceError(f"cannot read index statistics: {path}: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()


def count_values(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def fts_phrase(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def diagnostic_lookup(index_path: Path, term: str, lane: str, limit: int = 10) -> list[str]:
    uri = f"{index_path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        if read_sqlite_metadata(connection).get("completion_marker") is not True:
            raise GovernanceError("diagnostic lookup rejected an incomplete index")
        if lane == "exact":
            rows = connection.execute(
                "SELECT retrieval_locator FROM exact_terms WHERE normalized_term = ? ORDER BY retrieval_locator LIMIT ?",
                (normalize_term(term), limit),
            ).fetchall()
        elif lane in {"unicode61", "trigram"}:
            table = "clauses_unicode" if lane == "unicode61" else "clauses_trigram"
            rows = connection.execute(
                f"SELECT retrieval_locator FROM {table} WHERE {table} MATCH ? ORDER BY bm25({table}), retrieval_locator LIMIT ?",
                (fts_phrase(term), limit),
            ).fetchall()
        else:
            raise GovernanceError(f"unknown diagnostic lane: {lane}")
        return [row[0] for row in rows]
    except sqlite3.Error as exc:
        raise GovernanceError(f"diagnostic lookup failed in {lane}: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()


def retrieval_lane_evaluation(
    index_path: Path,
    rows: list[dict[str, Any]],
    taxonomy: dict[str, Any],
    source_ids: list[str],
) -> dict[str, Any]:
    controlled = known_terms(taxonomy, source_ids)
    required_negations = [value for value in taxonomy.get("negation_terms", []) if isinstance(value, str)]
    missing_negations = [term for term in required_negations if controlled.get(term) != "negation-term"]
    if missing_negations:
        raise GovernanceError(f"negation terms are missing from exact retrieval control: {missing_negations}")
    grouped_terms: dict[str, set[str]] = {
        "source_ids": set(source_ids),
        "profile_codes": profile_terms(),
        "negations": set(required_negations),
        "actions": set(),
    }
    for action_id, action in taxonomy.get("actions", {}).items():
        grouped_terms["actions"].add(action_id)
        grouped_terms["actions"].update(action.get("keywords", []))
        grouped_terms["actions"].update(action.get("identifiers", []))
    exact_groups: dict[str, dict[str, Any]] = {}
    for group, terms in grouped_terms.items():
        checked = 0
        skipped_absent = 0
        expected_total = 0
        returned_total = 0
        for term in sorted(term for term in terms if isinstance(term, str) and term):
            expected = {
                record["retrieval_locator"]
                for record in rows
                if contains_controlled_term(record["context_text"], term)
            }
            if not expected:
                skipped_absent += 1
                continue
            actual = set(diagnostic_lookup(index_path, term, "exact", len(rows) + 1))
            if actual != expected:
                missing = sorted(expected - actual)[:3]
                unexpected = sorted(actual - expected)[:3]
                raise GovernanceError(
                    f"exact retrieval target mismatch for {group}:{term}: "
                    f"missing={missing}; unexpected={unexpected}"
                )
            checked += 1
            expected_total += len(expected)
            returned_total += len(actual)
        if checked == 0:
            raise GovernanceError(f"exact retrieval group has no applicable terms: {group}")
        exact_groups[group] = {
            "passed": True,
            "terms_checked": checked,
            "terms_absent_from_corpus": skipped_absent,
            "expected_targets": expected_total,
            "returned_targets": returned_total,
            "recall_at_corpus_bound": 1.0,
        }

    fts_cases = (
        ("unicode_english_authority", "Authority", "unicode61"),
        ("trigram_chinese_unauthorized", "未授权", "trigram"),
    )
    fts_results: dict[str, dict[str, Any]] = {}
    for case_id, term, lane in fts_cases:
        expected = {
            record["retrieval_locator"]
            for record in rows
            if normalize_term(term) in normalize_term(record["context_text"])
        }
        actual = set(diagnostic_lookup(index_path, term, lane, len(rows) + 1))
        if not expected or not expected.issubset(actual):
            raise GovernanceError(
                f"{lane} retrieval recall failed for {term}: "
                f"expected={len(expected)}; returned={len(actual)}; missing={sorted(expected - actual)[:3]}"
            )
        fts_results[case_id] = {
            "passed": True,
            "lane": lane,
            "term": term,
            "expected_targets": len(expected),
            "returned_targets": len(actual),
            "recall_at_corpus_bound": 1.0,
        }
    return {
        "status": "Passed",
        "fixed_k": len(rows) + 1,
        "exact_groups": exact_groups,
        "fts_cases": fts_results,
    }


def partial_index_mutation_evaluation(index_path: Path) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for table, expected_error in (
        ("exact_terms", "exact_terms closure"),
        ("clauses_unicode", "row count does not match clauses"),
        ("clauses_trigram", "row count does not match clauses"),
    ):
        source = sqlite3.connect(f"{index_path.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
        candidate = sqlite3.connect(":memory:")
        try:
            source.backup(candidate)
            stored = read_sqlite_metadata(candidate)
            if table == "exact_terms":
                key = candidate.execute(
                    """SELECT normalized_term, retrieval_locator, term_kind
                       FROM exact_terms
                       ORDER BY normalized_term, retrieval_locator, term_kind LIMIT 1"""
                ).fetchone()
                if key is None:
                    raise GovernanceError("partial-index fixture exact_terms table is empty")
                candidate.execute(
                    """DELETE FROM exact_terms
                       WHERE normalized_term = ? AND retrieval_locator = ? AND term_kind = ?""",
                    key,
                )
            else:
                rowid = candidate.execute(f"SELECT rowid FROM {table} ORDER BY rowid LIMIT 1").fetchone()
                if rowid is None:
                    raise GovernanceError(f"partial-index fixture table is empty: {table}")
                candidate.execute(f"DELETE FROM {table} WHERE rowid = ?", (rowid[0],))
            candidate.commit()
            try:
                verify_index_content(candidate, stored)
            except GovernanceError as exc:
                if expected_error not in str(exc):
                    raise GovernanceError(
                        f"partial-index fixture {table} failed for the wrong reason: {exc}"
                    ) from exc
                results[f"{table}_partial_blocked"] = True
            else:
                raise GovernanceError(f"partial-index fixture was accepted: {table}")
        finally:
            candidate.close()
            source.close()
    return results


def reconstruct_clause(record: dict[str, Any], source: SourceDocument) -> str:
    if record["source_sha256"] != source.source_sha256:
        raise GovernanceError("clause source hash is stale")
    ranged = "\n".join(source.lines[record["line_start"] - 1:record["line_end"]])
    range_start = record.get("range_char_start")
    range_end = record.get("range_char_end")
    if (
        not isinstance(range_start, int)
        or isinstance(range_start, bool)
        or not isinstance(range_end, int)
        or isinstance(range_end, bool)
        or range_start < 0
        or range_end <= range_start
        or range_end > len(ranged)
    ):
        raise GovernanceError(f"clause range offsets are invalid: {record['retrieval_locator']}")
    reconstructed = ranged[range_start:range_end]
    if reconstructed != record["text"]:
        raise GovernanceError(f"clause range offsets do not reproduce text: {record['retrieval_locator']}")
    if sha256_bytes(reconstructed.encode("utf-8")) != record["chunk_sha256"]:
        raise GovernanceError("reconstructed clause hash mismatch")
    return reconstructed


def synthetic_source(text: str, source_sha: str | None = None) -> SourceDocument:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = tuple(normalized.splitlines())
    title, version, status = source_metadata(lines, "FIXTURE")
    return SourceDocument(
        source_id="FIXTURE",
        logical_path="references/fixtures/parser.md",
        physical_path=Path("fixtures/parser.md"),
        source_sha256=source_sha or sha256_bytes(normalized.encode("utf-8")),
        title=title,
        version=version,
        status=status,
        normalized_text=normalized,
        lines=lines,
    )


def run_parser_fixtures() -> dict[str, Any]:
    taxonomy = read_json(runtime_asset_path("mappings/norm-action-taxonomy.json"))
    fixture = """# Fixture 标准

## 1. 控制

普通段落必须保留来源。

1. 第一条必须验证。
   延续内容保持在同一列表项。
   - 嵌套条款必须单独解析。
2. 第二条不得丢失。

| 字段 | 规则 |
|---|---|
| Authority | 必须 |
| Gate | 不得跳过 |

代码前置条款：

```python
print("Gate")
```

超长段落。第一句必须保留。第二句不得丢失。第三句用于确定性拆分。第四句用于验证重放。第五句继续增加长度。第六句继续增加长度。第七句继续增加长度。第八句确认所有文字都被保留。
"""
    source = synthetic_source(fixture)
    first = parse_source(source, taxonomy, max_block_chars=64)
    second = parse_source(source, taxonomy, max_block_chars=64)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise GovernanceError("parser fixture replay is not byte deterministic")
    kinds = {record["structure_kind"] for record in first}
    required_kinds = {"heading", "paragraph", "list-item", "table-header", "table-row", "paragraph+code"}
    if not required_kinds.issubset(kinds):
        raise GovernanceError(f"parser fixture is missing structure kinds: {sorted(required_kinds - kinds)}")
    if not any(record["text"].startswith("   - 嵌套条款") for record in first):
        raise GovernanceError("parser fixture did not emit a nested list item independently")
    if not any(record["parent_block_sha256"] != record["chunk_sha256"] for record in first):
        raise GovernanceError("parser fixture did not exercise deterministic long-block splitting")
    for record in first:
        reconstruct_clause(record, source)
        if record["locator_kind"] != LOCATOR_KIND:
            raise GovernanceError("parser fixture emitted a non-derived locator kind")
    changed = parse_source(synthetic_source(fixture + "\n新增位置变化。"), taxonomy, max_block_chars=64)
    if {item["retrieval_locator"] for item in first} & {item["retrieval_locator"] for item in changed}:
        raise GovernanceError("source mutation did not invalidate all derived locators")
    nfd = synthetic_source("# Cafe\u0301\n\n必须验证。")
    nfc = synthetic_source("# Café\n\n必须验证。", source_sha=nfd.source_sha256)
    nfd_heading = parse_source(nfd, taxonomy)[0]["retrieval_locator"].split(":")[2]
    nfc_heading = parse_source(nfc, taxonomy)[0]["retrieval_locator"].split(":")[2]
    if nfd_heading != nfc_heading:
        raise GovernanceError("heading hash is not NFC deterministic")
    repeated = synthetic_source("# Repeated\n\n" + "A" * 128)
    repeated_records = parse_source(repeated, taxonomy, max_block_chars=64)
    for record in repeated_records:
        reconstruct_clause(record, repeated)
    newline_boundary = synthetic_source("A" * 63 + "\n" + "B" * 65)
    newline_records = parse_source(newline_boundary, taxonomy, max_block_chars=64)
    if not any(record["text"].endswith("\n") for record in newline_records):
        raise GovernanceError("parser fixture did not split a long block at a newline boundary")
    for record in newline_records:
        reconstruct_clause(record, newline_boundary)
    identity_material = ("1" * 64, "2" * 64, "3" * 64, "4" * 64)
    identity_64 = compute_index_digest(
        *identity_material,
        index_schema_version=effective_index_schema_version(64),
    )
    identity_128 = compute_index_digest(
        *identity_material,
        index_schema_version=effective_index_schema_version(128),
    )
    if identity_64 == identity_128:
        raise GovernanceError("max block chars did not invalidate index identity")
    return {
        "status": "Passed",
        "record_count": len(first),
        "structure_kinds": sorted(kinds),
        "replay_sha256": sha256_bytes(canonical_json_bytes(first)),
        "long_block_split": True,
        "locator_kind": LOCATOR_KIND,
        "nfc_heading_hash_stable": True,
        "nested_list_item_independent": True,
        "repeated_chunks_reconstructed": True,
        "newline_boundary_chunks_reconstructed": True,
        "max_block_chars_identity_bound": True,
    }


def run_lock_lifecycle_fixtures() -> dict[str, Any]:
    """Exercise real multi-process contention, interruption, and partial-index rejection."""

    with tempfile.TemporaryDirectory(prefix="norm-index-lock-") as temp:
        root = Path(temp)
        lock_path = root / "fixture.lock"
        first_result = root / "first.json"
        second_result = root / "second.json"
        command_base = [
            sys.executable, "-B", str(Path(__file__).resolve()),
            "--internal-lock-probe", str(lock_path),
            "--lock-timeout-seconds", "2",
            "--lock-lease-seconds", "2",
        ]
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        first = subprocess.Popen(
            command_base + ["--internal-result", str(first_result), "--internal-hold-seconds", "0.25"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=environment,
        )
        deadline = time.monotonic() + 2.0
        while not lock_path.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        if not lock_path.exists():
            first.terminate()
            raise GovernanceError("multi-process lock fixture did not acquire the first lock")
        second = subprocess.Popen(
            command_base + ["--internal-result", str(second_result), "--internal-hold-seconds", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=environment,
        )
        first_output, first_error = first.communicate(timeout=5)
        second_output, second_error = second.communicate(timeout=5)
        if first.returncode != 0 or second.returncode != 0:
            raise GovernanceError(
                "multi-process lock fixture failed: "
                f"first={first.returncode}:{first_output}:{first_error}; "
                f"second={second.returncode}:{second_output}:{second_error}"
            )
        first_times = read_json(first_result)
        second_times = read_json(second_result)
        if second_times["acquired_monotonic"] < first_times["released_monotonic"]:
            raise GovernanceError("multi-process builders overlapped their exclusive lock windows")

        interrupted_lock = root / "interrupted.lock"
        interrupted_result = root / "interrupted.json"
        interrupted = subprocess.Popen(
            [
                sys.executable, "-B", str(Path(__file__).resolve()),
                "--internal-lock-probe", str(interrupted_lock),
                "--internal-result", str(interrupted_result),
                "--internal-hold-seconds", "5",
                "--lock-timeout-seconds", "1",
                "--lock-lease-seconds", "0.15",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=environment,
        )
        deadline = time.monotonic() + 2.0
        while not interrupted_lock.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        if not interrupted_lock.exists():
            interrupted.terminate()
            raise GovernanceError("interrupted builder fixture did not acquire its lock")
        interrupted.terminate()
        interrupted.communicate(timeout=5)
        recorded_lease = parse_rfc3339(read_json(interrupted_lock)["lease_expires_at"])
        lease_wait_deadline = time.monotonic() + 2.0
        while datetime.now(timezone.utc) <= recorded_lease and time.monotonic() < lease_wait_deadline:
            time.sleep(0.01)
        if datetime.now(timezone.utc) <= recorded_lease:
            raise GovernanceError("interrupted builder fixture lease did not expire within its bound")
        with BuildLock(interrupted_lock, timeout_seconds=1.0, lease_seconds=1.0) as recovered:
            if not recovered.recovered_stale_lock:
                raise GovernanceError("dead builder lock was not recovered through identity and lease checks")

        stale_guard_lock = root / "stale-guard.lock"
        stale_guard_path = stale_guard_lock.with_name(f"{stale_guard_lock.name}.recover")
        stale_record = {
            "schema_version": "1.0",
            "pid": 2147483647,
            "process_start_token": "dead-fixture-process",
            "created_at": "2000-01-01T00:00:00Z",
            "lease_expires_at": "2000-01-01T00:00:01Z",
            "nonce": "stale-fixture-nonce",
        }
        stale_guard_lock.write_bytes(canonical_json_bytes(stale_record) + b"\n")
        stale_guard_path.write_bytes(canonical_json_bytes({**stale_record, "nonce": "stale-guard-nonce"}) + b"\n")
        with BuildLock(stale_guard_lock, timeout_seconds=1.0, lease_seconds=1.0) as recovered_guard:
            if not recovered_guard.recovered_stale_lock:
                raise GovernanceError("dead recovery guard did not permit bounded stale-lock takeover")
        if stale_guard_path.exists():
            raise GovernanceError("stale recovery guard remained after successful takeover")

        malformed_guard_lock = root / "malformed-guard.lock"
        malformed_guard_path = malformed_guard_lock.with_name(f"{malformed_guard_lock.name}.recover")
        malformed_guard_lock.write_bytes(canonical_json_bytes(stale_record) + b"\n")
        malformed_guard_path.write_bytes(b'{"schema_version":')
        old_time = time.time() - 10.0
        os.utime(malformed_guard_path, (old_time, old_time))
        with BuildLock(malformed_guard_lock, timeout_seconds=1.0, lease_seconds=0.1) as recovered_malformed:
            if not recovered_malformed.recovered_stale_lock:
                raise GovernanceError("interrupted malformed recovery guard was not recovered")
        if malformed_guard_path.exists():
            raise GovernanceError("malformed recovery guard remained after bounded takeover")

        active_lock = root / "active.lock"
        active_blocked = False
        with BuildLock(active_lock, timeout_seconds=0.1, lease_seconds=1.0):
            try:
                with BuildLock(active_lock, timeout_seconds=0.05, lease_seconds=1.0):
                    pass
            except GovernanceError:
                active_blocked = True
        if not active_blocked:
            raise GovernanceError("active process lock was incorrectly taken over")

        partial_main_lock = root / "partial-main.lock"
        partial_main_lock.write_bytes(b"")
        partial_owner = BuildLock(partial_main_lock, timeout_seconds=1.0, lease_seconds=1.0)

        def finish_partial_main_record() -> None:
            time.sleep(0.05)
            partial_main_lock.write_bytes(canonical_json_bytes(partial_owner._payload()) + b"\n")

        partial_writer = threading.Thread(target=finish_partial_main_record, daemon=True)
        partial_writer.start()
        partial_wait_started = time.monotonic()
        partial_wait_blocked = False
        try:
            with BuildLock(partial_main_lock, timeout_seconds=0.2, lease_seconds=1.0):
                pass
        except GovernanceError as exc:
            partial_wait_elapsed = time.monotonic() - partial_wait_started
            partial_wait_blocked = "timeout" in str(exc) and partial_wait_elapsed >= 0.15
        finally:
            partial_writer.join(timeout=1.0)
            try:
                _, completed_partial_record = BuildLock._read_record(partial_main_lock)
                partial_record_valid = BuildLock._is_active_or_leased(completed_partial_record)
            except GovernanceError:
                partial_record_valid = False
            partial_main_lock.unlink(missing_ok=True)
        if not partial_wait_blocked or not partial_record_valid:
            raise GovernanceError(
                "partial main lock record did not become valid and wait to the configured timeout"
            )

        invalid_lock = root / "invalid.lock"
        invalid_lock.write_text("not-json\n", encoding="utf-8")
        invalid_blocked = False
        try:
            with BuildLock(invalid_lock, timeout_seconds=0.0, lease_seconds=1.0):
                pass
        except GovernanceError:
            invalid_blocked = True
        if not invalid_blocked:
            raise GovernanceError("invalid lock record did not fail closed")

        partial = root / f"{'0' * 64}.sqlite3"
        sqlite3.connect(partial).close()
        partial_blocked = False
        try:
            validate_index(partial, {
                "index_digest": "0" * 64,
                "source_count": 1,
                "clause_count": 1,
            })
        except GovernanceError:
            partial_blocked = True
        if not partial_blocked:
            raise GovernanceError("partial SQLite index did not fail closed")

        leftovers = [path.name for path in root.iterdir() if path.suffix in {".recover", ".lock"}]
        if invalid_lock.exists():
            invalid_lock.unlink()
            leftovers = [item for item in leftovers if item != invalid_lock.name]
        if leftovers:
            raise GovernanceError(f"lock lifecycle fixtures left control files: {leftovers}")
        return {
            "status": "Passed",
            "multi_process_single_holder": True,
            "interrupted_builder_recovered": True,
            "interrupted_recovery_guard_recovered": True,
            "malformed_recovery_guard_recovered": True,
            "active_owner_not_preempted": True,
            "partial_main_record_waited_to_timeout": True,
            "invalid_lock_blocked": True,
            "partial_index_blocked": True,
            "control_file_leftovers": 0,
        }


def load_clause_rows(index_path: Path) -> list[dict[str, Any]]:
    uri = f"{index_path.resolve().as_uri()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = []
        for row in connection.execute("SELECT * FROM clauses ORDER BY source_id, ordinal"):
            item = dict(row)
            for key in ("heading_path_json", "control_types_json", "stage_tags_json", "action_tags_json"):
                item[key.removesuffix("_json")] = json.loads(item.pop(key))
            rows.append(item)
        return rows
    finally:
        connection.close()


def prohibited_boundary_evaluation(
    project_root: Path,
    evaluation_task_id: str,
) -> dict[str, Any]:
    skill_root = Path(__file__).resolve().parent.parent
    resolved_project = project_root.resolve()
    resolved_skill = skill_root.resolve()
    if resolved_skill == resolved_project or resolved_skill.is_relative_to(resolved_project):
        mirror_root = resolved_skill
    else:
        repository = project_root.parent / "LFen-Skills"
        nested = sorted((repository / "skills").glob(f"*/{skill_root.name}"))
        mirror_root = nested[0] if len(nested) == 1 else repository / skill_root.name
    protected_entries = (
        "SKILL.md",
        "agents/openai.yaml",
        "references/spec-source-map.md",
    )
    hash_comparisons: dict[str, dict[str, Any]] = {}
    for relative in protected_entries:
        source = skill_root / relative
        baseline = mirror_root / relative
        if not source.is_file() or not baseline.is_file():
            raise GovernanceError(f"default-path boundary baseline is missing: {relative}")
        source_hash = sha256_file(source)
        baseline_hash = sha256_file(baseline)
        hash_comparisons[relative] = {
            "source_sha256": source_hash,
            "published_baseline_sha256": baseline_hash,
            "matched": source_hash == baseline_hash,
        }
    changed_entries = [
        relative for relative, result in hash_comparisons.items() if not result["matched"]
    ]
    integration_references = [
        relative
        for relative in protected_entries
        if "build_norm_index" in (skill_root / relative).read_text(encoding="utf-8")
    ]
    parser = build_parser()
    exposed_options = sorted({
        option
        for action in parser._actions
        for option in action.option_strings
    })
    prohibited_options = {
        "--query", "--query-text", "--budget", "--budget-profile",
        "--pinned-set", "--coverage", "--fallback", "--clause-context",
    }
    exposed_prohibited_options = sorted(prohibited_options.intersection(exposed_options))
    t015_entry = skill_root / "scripts" / "query_norm_context.py"
    default_changed = bool(changed_entries or integration_references)
    t015_present = bool(t015_entry.exists() or exposed_prohibited_options)
    t015_outcome_path = (
        project_root / ".project-governance" / "tasks" / "T-015" / "after.json"
    )
    t015_implemented = False
    if t015_outcome_path.is_file():
        t015_outcome = read_json(t015_outcome_path)
        t015_implemented = (
            t015_outcome.get("task_id") == "T-015"
            and t015_outcome.get("status") == "Implemented"
        )
    if default_changed:
        raise GovernanceError(
            f"T-014 default Agent path boundary changed: "
            f"hash_changes={changed_entries}; integration_refs={integration_references}"
        )
    if t015_present and evaluation_task_id == "T-014":
        raise GovernanceError(
            f"T-015 surface was exposed during T-014: "
            f"entry_exists={t015_entry.exists()}; options={exposed_prohibited_options}"
        )
    if t015_present and evaluation_task_id == "T-015" and not t015_implemented:
        raise GovernanceError(
            "T-015 surface exists without a valid Implemented T-015 TaskOutcome"
        )
    return {
        "status": "Passed",
        "baseline_root": str(mirror_root),
        "protected_entry_hashes": hash_comparisons,
        "build_norm_index_entry_references": integration_references,
        "exposed_cli_options": exposed_options,
        "exposed_prohibited_options": exposed_prohibited_options,
        "query_norm_context_entry_exists": t015_entry.exists(),
        "default_agent_path_changed": default_changed,
        "t015_features_present": t015_present,
        "t015_features_authorized": (
            (not t015_present)
            or t015_implemented
            or evaluation_task_id not in {"T-014", "T-015"}
        ),
        "t015_authorization_mode": (
            "development-task-outcome"
            if evaluation_task_id in {"T-014", "T-015"}
            else "embedded-skill-publication"
        ),
        "t015_outcome_ref": (
            ".project-governance/tasks/T-015/after.json" if t015_implemented else None
        ),
    }


def evaluate_index(
    project_root: Path,
    index_path: Path,
    metadata: dict[str, Any],
    build_stats: dict[str, Any],
    consistency_report_path: Path,
    evaluation_task_id: str,
) -> dict[str, Any]:
    sources, normative_digest = load_sources()
    by_id = {source.source_id: source for source in sources}
    rows = load_clause_rows(index_path)
    for record in rows:
        reconstruct_clause(record, by_id[record["source_id"]])
        expected_locator = ":".join((
            record["source_id"], record["source_sha256"][:8],
            heading_hash(record["heading_path"])[:8], str(record["ordinal"]), record["chunk_sha256"][:8],
        ))
        if record["retrieval_locator"] != expected_locator:
            raise GovernanceError("stored retrieval locator is not reproducible")
    diagnostics = {
        "exact_source_id_C07": diagnostic_lookup(index_path, "C07", "exact"),
        "exact_profile_CHG": diagnostic_lookup(index_path, "CHG", "exact"),
        "exact_chinese_permission": diagnostic_lookup(index_path, "权限", "exact"),
        "exact_short_negation": diagnostic_lookup(index_path, "不", "exact"),
        "exact_normative_negation": diagnostic_lookup(index_path, "不得", "exact"),
        "exact_action_run_started": diagnostic_lookup(index_path, "run_started", "exact"),
        "unicode_english_authority": diagnostic_lookup(index_path, "Authority", "unicode61"),
        "trigram_chinese_unauthorized": diagnostic_lookup(index_path, "未授权", "trigram"),
    }
    if any(not values for values in diagnostics.values()):
        missing = [key for key, values in diagnostics.items() if not values]
        raise GovernanceError(f"diagnostic retrieval lanes produced no results: {missing}")
    gold = read_json(runtime_asset_path("evaluations/norm-retrieval-gold.json"))
    mandatory: list[dict[str, Any]] = []
    for target in gold["mandatory_clause_targets"]:
        source = by_id[target["source_id"]]
        raw = "\n".join(source.lines[target["line_start"] - 1:target["line_end"]])
        raw_hash = sha256_bytes(raw.encode("utf-8"))
        covered_lines = {
            line
            for record in rows
            if record["source_id"] == target["source_id"]
            for line in range(record["line_start"], record["line_end"] + 1)
        }
        required_lines = {
            line
            for line in range(target["line_start"], target["line_end"] + 1)
            if source.lines[line - 1].strip()
        }
        passed = (
            source.source_sha256 == target["source_sha256"]
            and raw_hash == target["text_sha256"]
            and required_lines.issubset(covered_lines)
        )
        mandatory.append({"target_id": target["target_id"], "passed": passed})
    if not all(item["passed"] for item in mandatory):
        raise GovernanceError("mandatory target source restoration or parser coverage failed")
    report = read_json(consistency_report_path)
    negative_gates: dict[str, bool] = {}
    missing_report_path = governance_root(project_root) / "generated" / "evaluations" / "T-014" / ".missing-consistency-report.json"
    cache_before = sorted(path.name for path in index_path.parent.iterdir())
    try:
        build_index(project_root, missing_report_path)
    except GovernanceError:
        negative_gates["missing_report"] = cache_before == sorted(path.name for path in index_path.parent.iterdir())
    else:
        raise GovernanceError("missing consistency report unexpectedly produced an index")
    mutations = {
        "not_ready": (
            lambda item: item.update({"norm_index_ready": False}),
            "norm_index_ready is not true",
        ),
        "blocker_present": (
            lambda item: item["summary"]["by_severity"].update({"Blocker": 1}),
            "contains unresolved Blocker or Major",
        ),
        "stale_normative_digest": (
            lambda item: item["inputs"].update({"normative_sources_sha256": "0" * 64}),
            "normative_sources_sha256 is stale",
        ),
        "stale_manifest_digest": (
            lambda item: item["inputs"].update({"manifest_sha256": "0" * 64}),
            "manifest_sha256 is stale",
        ),
    }
    for name, (mutation, expected_error) in mutations.items():
        candidate = json.loads(json.dumps(report))
        mutation(candidate)
        candidate["audit_digest"] = consistency_audit_digest(candidate)
        try:
            validate_consistency_report(
                candidate,
                normative_sources_sha256=normative_digest,
                manifest_sha256=sha256_file(embedded_manifest_path()),
            )
        except GovernanceError as exc:
            if expected_error not in str(exc):
                raise GovernanceError(
                    f"consistency negative gate {name} failed for the wrong reason: {exc}"
                ) from exc
            negative_gates[name] = True
        else:
            raise GovernanceError(f"consistency negative gate unexpectedly passed: {name}")
    factors = {
        "normative_sources_sha256": metadata["normative_sources_sha256"],
        "consistency_report_sha256": metadata["consistency_report_sha256"],
        "parser_sha256": metadata["parser_sha256"],
        "action_taxonomy_sha256": metadata["action_taxonomy_sha256"],
    }
    base_digest = metadata["index_digest"]
    variants: dict[str, str] = {}
    for factor in factors:
        changed = dict(factors)
        changed[factor] = sha256_bytes((changed[factor] + ":changed").encode("ascii"))
        variants[factor] = compute_index_digest(
            changed["normative_sources_sha256"], changed["consistency_report_sha256"],
            changed["parser_sha256"], changed["action_taxonomy_sha256"],
            index_schema_version=metadata["index_schema_version"],
        )
    variants["index_schema_version"] = compute_index_digest(
        factors["normative_sources_sha256"], factors["consistency_report_sha256"],
        factors["parser_sha256"], factors["action_taxonomy_sha256"],
        index_schema_version=metadata["index_schema_version"] + ";mutated",
    )
    if any(value == base_digest for value in variants.values()) or len(set(variants.values())) != len(variants):
        raise GovernanceError("single-factor index invalidation is incomplete")
    parser_fixtures = run_parser_fixtures()
    lifecycle_fixtures = run_lock_lifecycle_fixtures()
    taxonomy = read_json(runtime_asset_path("mappings/norm-action-taxonomy.json"))
    retrieval_lanes = retrieval_lane_evaluation(
        index_path,
        rows,
        taxonomy,
        metadata["source_ids"],
    )
    partial_mutations = partial_index_mutation_evaluation(index_path)
    prohibited_boundaries = prohibited_boundary_evaluation(
        project_root,
        evaluation_task_id,
    )
    normalized_result = {
        "index_digest": base_digest,
        "index_schema_version": metadata["index_schema_version"],
        "content_digest": build_stats["content_digest"],
        "diagnostic_locators": diagnostics,
        "retrieval_lane_evaluation": retrieval_lanes,
        "partial_index_mutations": partial_mutations,
        "mandatory": mandatory,
        "structure_counts": build_stats["structure_counts"],
    }
    return {
        "schema_version": "6.3-candidate",
        "evaluation_id": f"{evaluation_task_id}-PARSER-INDEX-EVALUATION",
        "task_id": evaluation_task_id,
        "status": "Passed",
        "index_digest": base_digest,
        "index_content_digest": build_stats["content_digest"],
        "deterministic_result_sha256": sha256_bytes(canonical_json_bytes(normalized_result)),
        "source_count": metadata["source_count"],
        "clause_count": metadata["clause_count"],
        "structure_counts": build_stats["structure_counts"],
        "modality_counts": build_stats["modality_counts"],
        "parser_fixtures": parser_fixtures,
        "lifecycle_fixtures": lifecycle_fixtures,
        "retrieval_lane_evaluation": retrieval_lanes,
        "partial_index_mutations": partial_mutations,
        "prohibited_boundary_evaluation": prohibited_boundaries,
        "diagnostic_retrieval": {key: {"passed": bool(value), "result_count": len(value)} for key, value in diagnostics.items()},
        "mandatory_target_coverage": mandatory,
        "consistency_negative_gates": negative_gates,
        "single_factor_digest_variants": variants,
        "build_status": build_stats["build_status"],
        "recovered_stale_lock": build_stats["recovered_stale_lock"],
        "default_agent_path_changed": prohibited_boundaries["default_agent_path_changed"],
        "t015_features_present": prohibited_boundaries["t015_features_present"],
    }


def render_evaluation(document: dict[str, Any]) -> str:
    diagnostics = document["diagnostic_retrieval"]
    return "\n".join([
        f"# {document['task_id']} 条款解析与本地索引评测",
        "",
        f"- Status: `{document['status']}`",
        f"- Index digest: `{document['index_digest']}`",
        f"- Content digest: `{document['index_content_digest']}`",
        f"- Sources / clauses: `{document['source_count']} / {document['clause_count']}`",
        f"- Parser fixture records: `{document['parser_fixtures']['record_count']}`",
        f"- Lifecycle fixtures: `{document['lifecycle_fixtures']['status']}`",
        f"- Mandatory target coverage: `{sum(item['passed'] for item in document['mandatory_target_coverage'])}/{len(document['mandatory_target_coverage'])}`",
        f"- Diagnostic lanes passed: `{sum(item['passed'] for item in diagnostics.values())}/{len(diagnostics)}`",
        f"- Consistency negative gates: `{sum(document['consistency_negative_gates'].values())}/{len(document['consistency_negative_gates'])}`",
        f"- Single-factor invalidation: `{len(document['single_factor_digest_variants'])}/5`",
        f"- Retrieval target groups: `{len(document['retrieval_lane_evaluation']['exact_groups'])}` exact / `{len(document['retrieval_lane_evaluation']['fts_cases'])}` FTS",
        f"- Partial-index mutations blocked: `{sum(document['partial_index_mutations'].values())}/{len(document['partial_index_mutations'])}`",
        f"- Default Agent path changed: `{str(document['default_agent_path_changed']).lower()}` (machine-checked)",
        f"- T-015 features present: `{str(document['t015_features_present']).lower()}` (machine-checked)",
        "",
        f"该报告只验证 {document['task_id']} 的本地索引，不构成 V6.3 批准、Baseline、Release 或风险接受。",
        "",
    ])


def write_outputs(
    project_root: Path,
    index_path: Path,
    metadata: dict[str, Any],
    evaluation: dict[str, Any],
    consistency_report_path: Path,
    metadata_output: Path,
    evaluation_output: Path,
) -> None:
    root = governance_root(project_root)
    project_id = read_json(consistency_report_path).get("project_id")
    if not isinstance(project_id, str) or not project_id:
        raise GovernanceError("consistency report has no valid project_id for DerivedView output")
    sources = [
        consistency_report_path,
        Path(__file__).resolve(),
        embedded_manifest_path(),
        runtime_asset_path("schemas/norm-index-metadata.schema.json"),
        runtime_asset_path("mappings/norm-action-taxonomy.json"),
        index_path,
    ]
    _write_derived_view(
        root=root,
        content_path=metadata_output,
        content=json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        project_id=project_id,
        view_id=f"DV-{evaluation['task_id']}-INDEX-METADATA",
        view_kind="norm-index-metadata",
        sources=sources,
    )
    _write_derived_view(
        root=root,
        content_path=evaluation_output,
        content=json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n",
        project_id=project_id,
        view_id=f"DV-{evaluation['task_id']}-EVALUATION-JSON",
        view_kind="norm-index-evaluation",
        sources=sources + [metadata_output],
    )
    _write_derived_view(
        root=root,
        content_path=evaluation_output.with_suffix(".md"),
        content=render_evaluation(evaluation),
        project_id=project_id,
        view_id=f"DV-{evaluation['task_id']}-EVALUATION-MD",
        view_kind="norm-index-evaluation-review",
        sources=sources + [metadata_output, evaluation_output],
    )


def bootstrap_project_runtime(
    task_dir: Path,
    *,
    force_refresh: bool = False,
) -> tuple[Path, Path, Path]:
    """Create a trusted project-local Ready index from the protected Skill publication."""

    resolved_task = task_dir.resolve()
    if resolved_task.parent.name != "tasks" or resolved_task.parent.parent.name != ".project-governance":
        raise GovernanceError("bootstrap task directory must be .project-governance/tasks/<TaskID>")
    project_root = resolved_task.parent.parent.parent
    before = read_json(resolved_task / "before.json")
    task_id = before.get("task_id")
    project_id = before.get("project_id")
    if task_id != resolved_task.name or not isinstance(project_id, str) or not project_id:
        raise GovernanceError("bootstrap TaskContract identity is invalid")
    output_dir = (
        governance_root(project_root)
        / "generated"
        / "evaluations"
        / "runtime-bootstrap"
        / str(task_id)
    )
    metadata_path = output_dir / "norm-index-metadata.json"
    report_path = output_dir / "norm-consistency-audit.json"
    if not force_refresh and metadata_path.is_file() and report_path.is_file():
        metadata = read_json(metadata_path)
        report = read_json(report_path)
        runtime_is_current = (
            metadata.get("parser_sha256") == sha256_file(Path(__file__).resolve())
            and metadata.get("action_taxonomy_sha256")
            == sha256_file(runtime_asset_path("mappings/norm-action-taxonomy.json"))
            and report.get("inputs", {}).get("manifest_sha256")
            == sha256_file(embedded_manifest_path())
        )
        if metadata.get("status") == "Ready" and runtime_is_current:
            cache_relative = metadata.get("storage", {}).get("relative_cache_path")
            if isinstance(cache_relative, str):
                index_path = (project_root / cache_relative).resolve()
                expected = {
                    key: metadata[key]
                    for key in (
                        "index_digest", "index_schema_version", "normative_sources_sha256",
                        "consistency_report_sha256", "parser_sha256", "action_taxonomy_sha256",
                        "source_ids", "source_count", "clause_count", "created_at",
                    )
                }
                validate_index(index_path, expected)
                if sha256_file(report_path) == metadata.get("consistency_report_sha256"):
                    return metadata_path, report_path, index_path

    from audit_norm_consistency import audit, write_report

    report, sources = audit(
        project_root,
        project_id,
        str(task_id),
        verify_authority_sources=False,
    )
    if not report.get("norm_index_ready"):
        blockers = [
            item.get("message")
            for item in report.get("findings", [])
            if item.get("severity") in {"Blocker", "Major"}
        ]
        raise GovernanceError(
            "runtime bootstrap consistency audit is not Ready: " + "; ".join(map(str, blockers))
        )
    write_report(
        report,
        project_root=project_root,
        project_id=project_id,
        output_dir=output_dir,
        sources=sources,
    )
    index_path, metadata, _ = build_index(project_root, report_path)
    _write_derived_view(
        root=governance_root(project_root),
        content_path=metadata_path,
        content=json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        project_id=project_id,
        view_id=f"DV-{task_id}-RUNTIME-BOOTSTRAP-INDEX-METADATA",
        view_kind="norm-index-metadata",
        sources=[
            report_path,
            Path(__file__).resolve(),
            embedded_manifest_path(),
            runtime_asset_path("schemas/norm-index-metadata.schema.json"),
            runtime_asset_path("mappings/norm-action-taxonomy.json"),
            index_path,
        ],
    )
    return metadata_path, report_path, index_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the deterministic content-addressed SQLite FTS5 norm index."
    )
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--task-id", help="Owning task ID for a formal index evaluation.")
    parser.add_argument("--consistency-report", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--evaluation-output", type=Path)
    parser.add_argument("--force-rebuild", action="store_true")
    parser.add_argument("--max-block-chars", type=int, default=DEFAULT_MAX_BLOCK_CHARS)
    parser.add_argument("--lock-timeout-seconds", type=float, default=DEFAULT_LOCK_TIMEOUT_SECONDS)
    parser.add_argument("--lock-lease-seconds", type=float, default=DEFAULT_LOCK_LEASE_SECONDS)
    parser.add_argument("--self-test", action="store_true", help="Run isolated parser and SQLite capability fixtures.")
    parser.add_argument(
        "--bootstrap-task-dir",
        type=Path,
        help="Initialize a consumer project's trusted local index from the protected Skill publication",
    )
    parser.add_argument("--internal-lock-probe", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--internal-result", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--internal-hold-seconds", type=float, default=0.0, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.internal_lock_probe is not None:
            if args.internal_result is None or args.internal_hold_seconds < 0:
                raise GovernanceError("internal lock probe requires a result path and non-negative hold")
            with BuildLock(
                args.internal_lock_probe,
                timeout_seconds=args.lock_timeout_seconds,
                lease_seconds=args.lock_lease_seconds,
            ):
                acquired = time.monotonic()
                time.sleep(args.internal_hold_seconds)
            atomic_write_json(args.internal_result, {
                "acquired_monotonic": acquired,
                "released_monotonic": time.monotonic(),
            })
            return 0
        if args.self_test:
            fixture = run_parser_fixtures()
            lifecycle = run_lock_lifecycle_fixtures()
            connection = sqlite3.connect(":memory:")
            try:
                connection.execute("CREATE VIRTUAL TABLE u USING fts5(text, tokenize='unicode61')")
                connection.execute("CREATE VIRTUAL TABLE t USING fts5(text, tokenize='trigram')")
            finally:
                connection.close()
            print(json.dumps({
                **fixture,
                "lifecycle": lifecycle,
                "sqlite_version": sqlite3.sqlite_version,
                "fts5": True,
            }, ensure_ascii=False, indent=2))
            return 0
        if args.bootstrap_task_dir is not None:
            metadata_path, report_path, index_path = bootstrap_project_runtime(
                args.bootstrap_task_dir,
                force_refresh=args.force_rebuild,
            )
            print(json.dumps({
                "status": "Ready",
                "metadata": str(metadata_path),
                "consistency_report": str(report_path),
                "index": str(index_path),
            }, ensure_ascii=False, indent=2))
            return 0
        if args.consistency_report is None:
            raise GovernanceError("--consistency-report is required unless --self-test is used")
        if not args.task_id:
            raise GovernanceError("--task-id is required for a formal index evaluation")
        project_root = args.project_root.resolve()
        report_path = args.consistency_report
        if not report_path.is_absolute():
            report_path = (project_root / report_path).resolve()
        formal, metadata, stats = build_index(
            project_root,
            report_path,
            force_rebuild=args.force_rebuild,
            max_block_chars=args.max_block_chars,
            lock_timeout_seconds=args.lock_timeout_seconds,
            lock_lease_seconds=args.lock_lease_seconds,
        )
        evaluation = evaluate_index(
            project_root,
            formal,
            metadata,
            stats,
            report_path,
            args.task_id,
        )
        if args.metadata_output or args.evaluation_output:
            if not args.metadata_output or not args.evaluation_output:
                raise GovernanceError("--metadata-output and --evaluation-output must be supplied together")
            metadata_output = args.metadata_output
            evaluation_output = args.evaluation_output
            if not metadata_output.is_absolute():
                metadata_output = (project_root / metadata_output).resolve()
            if not evaluation_output.is_absolute():
                evaluation_output = (project_root / evaluation_output).resolve()
            write_outputs(project_root, formal, metadata, evaluation, report_path, metadata_output, evaluation_output)
        print(json.dumps({
            "status": "Ready",
            "index": str(formal),
            "index_digest": metadata["index_digest"],
            "source_count": metadata["source_count"],
            "clause_count": metadata["clause_count"],
            "build_status": stats["build_status"],
            "cache_prune_warnings": stats["cache_prune_warnings"],
            "evaluation_status": evaluation["status"],
        }, ensure_ascii=False, indent=2))
        return 0
    except (GovernanceError, OSError, sqlite3.Error, UnicodeError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
