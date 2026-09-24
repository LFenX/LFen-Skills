#!/usr/bin/env python3
"""Extract interaction metrics from a public Xiaohongshu note URL.

The default run is intentionally headless and unauthenticated. It reports when an
authorized browser session is required instead of silently escalating to one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


try:
    from playwright.sync_api import BrowserContext, Page, Response, sync_playwright
except ImportError:  # Kept importable so self tests can cover deterministic helpers.
    BrowserContext = Any  # type: ignore[assignment,misc]
    Page = Any  # type: ignore[assignment,misc]
    Response = Any  # type: ignore[assignment,misc]
    sync_playwright = None


SCHEMA_VERSION = "1.0"
DEFAULT_REQUIRED = ("liked", "collected", "commented")
ALLOWED_REQUIRED = frozenset((*DEFAULT_REQUIRED, "shared"))
SENSITIVE_QUERY_KEYS = frozenset(
    {"access_token", "authorization", "session", "token", "xsec_token"}
)
NOTE_PATH_PATTERNS = (
    re.compile(r"^/explore/([0-9a-fA-F]+)(?:/)?$"),
    re.compile(r"^/discovery/item/([0-9a-fA-F]+)(?:/)?$"),
)
BLOCKER_PHRASES = {
    "app_only": (
        "仅支持在小红书 app 内查看",
        "当前内容仅支持在小红书 app 内查看",
        "app内打开",
        "打开小红书app",
    ),
    "login_wall": (
        "登录后查看",
        "扫码登录",
        "手机号登录",
        "登录后推荐更懂你的笔记",
    ),
    "risk_control": ("安全验证", "访问过于频繁", "验证后继续", "异常访问"),
    "unavailable": ("笔记不存在", "内容已删除", "该内容无法查看"),
}
ALIASES = {
    "liked": (
        "likedCount",
        "likeCount",
        "liked_count",
        "like_count",
        "likes",
    ),
    "collected": (
        "collectedCount",
        "collectCount",
        "collected_count",
        "collect_count",
        "收藏数",
    ),
    "commented": (
        "commentCount",
        "commentsCount",
        "comment_count",
        "comments_count",
        "评论数",
    ),
    "shared": (
        "shareCount",
        "sharedCount",
        "share_count",
        "shared_count",
        "分享数",
    ),
}
NOTE_ID_KEYS = ("noteId", "note_id", "itemId", "item_id")


@dataclass(frozen=True)
class Candidate:
    source: str
    path: str
    note_id: str | None
    metrics: dict[str, dict[str, Any]]


def validate_xhs_note_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise ValueError("URL 必须使用 HTTPS")
    if host != "xiaohongshu.com" and not host.endswith(".xiaohongshu.com"):
        raise ValueError("URL 必须属于 xiaohongshu.com")
    for pattern in NOTE_PATH_PATTERNS:
        match = pattern.fullmatch(parsed.path)
        if match:
            return match.group(1).lower()
    raise ValueError("仅支持 /explore/<note-id> 或 /discovery/item/<note-id> 笔记链接")


def redact_url(url: str) -> str:
    parsed = urlparse(url)
    redacted = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if value.startswith(("http://", "https://")):
            value = redact_url(value)
        else:
            value = re.sub(
                r"(?i)(xsec_token|access_token|authorization|session|token)=([^&\s]+)",
                r"\1=[REDACTED]",
                value,
            )
        redacted.append(
            (key, "[REDACTED]" if key.lower() in SENSITIVE_QUERY_KEYS else value)
        )
    return urlunparse(parsed._replace(query=urlencode(redacted)))


def redact_sensitive_text(text: str) -> str:
    url_pattern = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
    redacted = url_pattern.sub(lambda match: redact_url(match.group(0)), text)
    return re.sub(
        r"(?i)(xsec_token|access_token|authorization|session|token)=([^&\s]+)",
        r"\1=[REDACTED]",
        redacted,
    )


def alternate_note_url(url: str) -> str | None:
    parsed = urlparse(url)
    match = NOTE_PATH_PATTERNS[0].fullmatch(parsed.path)
    if not match:
        return None
    return urlunparse(parsed._replace(path=f"/discovery/item/{match.group(1)}"))


def normalize_metric(value: Any) -> dict[str, Any] | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return {"display": str(value), "normalized_value": value, "exact": True}
    if isinstance(value, float):
        if value.is_integer():
            integer = int(value)
            return {"display": str(integer), "normalized_value": integer, "exact": True}
        return None

    display = str(value).strip()
    if not display:
        return None
    compact = re.sub(r"[\s,，]", "", display)
    if re.fullmatch(r"\d+", compact):
        return {"display": display, "normalized_value": int(compact), "exact": True}

    abbreviated = re.fullmatch(r"(\d+(?:\.\d+)?)(万|亿)(\+)?", compact)
    if not abbreviated:
        return None
    multiplier = Decimal(10_000 if abbreviated.group(2) == "万" else 100_000_000)
    try:
        normalized = int(Decimal(abbreviated.group(1)) * multiplier)
    except InvalidOperation:
        return None
    return {"display": display, "normalized_value": normalized, "exact": False}


def _first_metric(mapping: dict[str, Any], aliases: Iterable[str]) -> dict[str, Any] | None:
    lowered = {str(key).lower(): value for key, value in mapping.items()}
    for alias in aliases:
        if alias in mapping:
            metric = normalize_metric(mapping[alias])
            if metric:
                return metric
        if alias.lower() in lowered:
            metric = normalize_metric(lowered[alias.lower()])
            if metric:
                return metric
    return None


def extract_candidates(
    value: Any,
    *,
    source: str,
    path: str = "$",
    max_depth: int = 12,
    max_nodes: int = 100_000,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[int] = set()
    visited = 0

    def walk(
        current: Any,
        current_path: str,
        depth: int,
        inherited_note_id: str | None = None,
    ) -> None:
        nonlocal visited
        if depth > max_depth or visited >= max_nodes:
            return
        if isinstance(current, (dict, list)):
            identity = id(current)
            if identity in seen:
                return
            seen.add(identity)
        visited += 1

        if isinstance(current, dict):
            current_note_id = next(
                (
                    str(current[key]).lower()
                    for key in NOTE_ID_KEYS
                    if key in current and current[key] is not None
                ),
                inherited_note_id,
            )
            generic_id = current.get("id")
            if (
                current_note_id is None
                and "note" in current_path.lower()
                and generic_id is not None
                and re.fullmatch(r"[0-9a-fA-F]{24}", str(generic_id))
            ):
                current_note_id = str(generic_id).lower()
            metrics = {
                name: metric
                for name, aliases in ALIASES.items()
                if (metric := _first_metric(current, aliases)) is not None
            }
            if metrics and (
                len(metrics) >= 2
                or current_note_id is not None
                or "interact" in current_path.lower()
            ):
                candidates.append(
                    Candidate(
                        source=source,
                        path=current_path,
                        note_id=current_note_id,
                        metrics=metrics,
                    )
                )
            for key, child in current.items():
                walk(child, f"{current_path}.{key}", depth + 1, current_note_id)
        elif isinstance(current, list):
            for index, child in enumerate(current):
                walk(child, f"{current_path}[{index}]", depth + 1, inherited_note_id)

    walk(value, path, 0)
    return candidates


def candidate_score(candidate: Candidate, note_id: str) -> tuple[int, int, int]:
    id_score = 100 if candidate.note_id == note_id else 0
    path_score = 10 if "interact" in candidate.path.lower() else 0
    source_score = {"initial_state": 3, "network": 2, "dom": 1}.get(
        candidate.source, 0
    )
    return id_score + len(candidate.metrics) * 20 + path_score + source_score, len(
        candidate.metrics
    ), source_score


def detect_blockers(text: str) -> list[str]:
    lowered = text.lower()
    return [
        name
        for name, phrases in BLOCKER_PHRASES.items()
        if any(phrase in lowered for phrase in phrases)
    ]


def _dom_candidates(dom_metrics: dict[str, list[dict[str, str]]]) -> list[Candidate]:
    metrics: dict[str, dict[str, Any]] = {}
    paths: list[str] = []
    for name in ALIASES:
        for item in dom_metrics.get(name, []):
            metric = normalize_metric(item.get("text"))
            if metric:
                metrics[name] = metric
                paths.append(item.get("selector", "dom"))
                break
    if not metrics:
        return []
    return [Candidate(source="dom", path="; ".join(paths), note_id=None, metrics=metrics)]


def compose_result(
    *,
    source_url: str,
    note_id: str,
    attempts: list[dict[str, Any]],
    required: tuple[str, ...],
) -> dict[str, Any]:
    all_candidates: list[Candidate] = []
    blocker_names: set[str] = set()
    errors: list[str] = []
    page_title = ""
    resolved_url = source_url

    for attempt in attempts:
        page_title = attempt.get("title") or page_title
        resolved_url = attempt.get("resolved_url") or resolved_url
        blocker_names.update(detect_blockers(attempt.get("body_head", "")))
        if attempt.get("error"):
            errors.append(str(attempt["error"]))
        all_candidates.extend(attempt.get("candidates", []))
        all_candidates.extend(_dom_candidates(attempt.get("dom_metrics", {})))

    eligible_candidates = [
        candidate
        for candidate in all_candidates
        if candidate.note_id in (None, note_id)
    ]
    ordered = sorted(
        eligible_candidates,
        key=lambda candidate: candidate_score(candidate, note_id),
        reverse=True,
    )
    metrics: dict[str, dict[str, Any]] = {}
    evidence: list[dict[str, Any]] = []
    for candidate in ordered:
        used: list[str] = []
        for name, metric in candidate.metrics.items():
            if name not in metrics:
                metrics[name] = metric
                used.append(name)
        if used:
            evidence.append(
                {
                    "source": candidate.source,
                    "path": candidate.path,
                    "note_id": candidate.note_id,
                    "fields": used,
                }
            )

    missing = [name for name in required if name not in metrics]
    fallback_required = bool(missing)
    blockers = sorted(blocker_names)
    if not missing:
        status = "ok"
    elif metrics:
        status = "partial"
    elif any(name in blocker_names for name in ("app_only", "login_wall")):
        status = "browser_session_required"
    elif "risk_control" in blocker_names:
        status = "blocked"
    else:
        status = "unavailable"

    return {
        "schema_version": SCHEMA_VERSION,
        "platform": "xiaohongshu",
        "status": status,
        "source_url": redact_url(source_url),
        "resolved_url": redact_url(resolved_url),
        "note_id": note_id,
        "title": page_title,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "required": list(required),
        "missing_required": missing,
        "evidence": evidence,
        "blockers": blockers,
        "errors": errors,
        "fallback": {
            "required": fallback_required,
            "recommended": (
                "existing_browser_session_dom"
                if fallback_required
                and any(name in blocker_names for name in ("app_only", "login_wall"))
                else None
            ),
        },
    }


PAGE_PROBE = r"""
() => {
  const aliases = {
    liked: ['likedCount', 'likeCount', 'liked_count', 'like_count', 'likes'],
    collected: ['collectedCount', 'collectCount', 'collected_count', 'collect_count', '收藏数'],
    commented: ['commentCount', 'commentsCount', 'comment_count', 'comments_count', '评论数'],
    shared: ['shareCount', 'sharedCount', 'share_count', 'shared_count', '分享数'],
  };
  const noteIdKeys = ['noteId', 'note_id', 'itemId', 'item_id'];
  const stateCandidates = [];
  const seen = new WeakSet();
  let visited = 0;

  function walk(value, path, depth, inheritedNoteId = null) {
    if (!value || typeof value !== 'object' || depth > 12 || visited >= 100000 || seen.has(value)) return;
    seen.add(value);
    visited += 1;
    let currentNoteId = inheritedNoteId;
    if (!Array.isArray(value)) {
      const data = {};
      for (const names of Object.values(aliases)) {
        for (const name of names) {
          if (Object.prototype.hasOwnProperty.call(value, name)) data[name] = value[name];
        }
      }
      for (const name of noteIdKeys) {
        if (Object.prototype.hasOwnProperty.call(value, name)) {
          data[name] = value[name];
          currentNoteId = String(value[name]).toLowerCase();
        }
      }
      if (!currentNoteId && /note/i.test(path) && /^[0-9a-f]{24}$/i.test(String(value.id || ''))) {
        currentNoteId = String(value.id).toLowerCase();
      }
      if (Object.keys(data).some(key => !noteIdKeys.includes(key))) {
        if (currentNoteId && !noteIdKeys.some(key => Object.prototype.hasOwnProperty.call(data, key))) {
          data.noteId = currentNoteId;
        }
        stateCandidates.push({path, data});
      }
    }
    if (Array.isArray(value)) {
      value.slice(0, 2000).forEach((child, index) => walk(child, `${path}[${index}]`, depth + 1, currentNoteId));
    } else {
      Object.entries(value).slice(0, 2000).forEach(([key, child]) => walk(child, `${path}.${key}`, depth + 1, currentNoteId));
    }
  }
  for (const name of ['__INITIAL_STATE__', '__INITIAL_SSR_STATE__', '__NEXT_DATA__']) {
    try { walk(window[name], name, 0); } catch (_) {}
  }

  const selectors = {
    liked: [
      '.engage-bar-container .like-wrapper .count',
      '.engage-bar .like-wrapper .count',
      '[class*="engage"] [class*="like"] [class*="count"]'
    ],
    collected: [
      '.engage-bar-container .collect-wrapper .count',
      '.engage-bar .collect-wrapper .count',
      '[class*="engage"] [class*="collect"] [class*="count"]'
    ],
    commented: [
      '.engage-bar-container .chat-wrapper .count',
      '.engage-bar .chat-wrapper .count',
      '[class*="engage"] [class*="chat"] [class*="count"]',
      '[class*="engage"] [class*="comment"] [class*="count"]'
    ],
    shared: [
      '.engage-bar-container .share-wrapper .count',
      '.engage-bar .share-wrapper .count',
      '[class*="engage"] [class*="share"] [class*="count"]'
    ]
  };
  const domMetrics = {};
  for (const [metric, metricSelectors] of Object.entries(selectors)) {
    domMetrics[metric] = [];
    for (const selector of metricSelectors) {
      for (const element of document.querySelectorAll(selector)) {
        const text = (element.innerText || element.textContent || '').trim();
        if (text) domMetrics[metric].push({selector, text});
      }
    }
  }
  return {
    title: document.title || '',
    resolvedUrl: location.href,
    bodyHead: (document.body?.innerText || '').slice(0, 5000),
    stateCandidates,
    domMetrics,
  };
}
"""


def _response_handler(candidates: list[Candidate]):
    def handle(response: Response) -> None:
        if len(candidates) >= 200:
            return
        parsed = urlparse(response.url)
        content_type = response.headers.get("content-type", "").lower()
        if not parsed.hostname or not parsed.hostname.endswith("xiaohongshu.com"):
            return
        if "json" not in content_type:
            return
        if not any(part in parsed.path.lower() for part in ("feed", "note", "item")):
            return
        try:
            payload = response.json()
        except Exception:
            return
        candidates.extend(
            extract_candidates(payload, source="network", path=f"response:{parsed.path}")
        )

    return handle


def probe_page(context: BrowserContext, url: str, note_id: str, timeout_ms: int) -> dict[str, Any]:
    page: Page = context.new_page()
    network_candidates: list[Candidate] = []
    page.on("response", _response_handler(network_candidates))
    attempt: dict[str, Any] = {
        "url": url,
        "resolved_url": url,
        "title": "",
        "body_head": "",
        "candidates": network_candidates,
        "dom_metrics": {},
        "error": None,
    }
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(1800)
        probed = page.evaluate(PAGE_PROBE)
        attempt.update(
            {
                "resolved_url": probed.get("resolvedUrl", url),
                "title": probed.get("title", ""),
                "body_head": probed.get("bodyHead", ""),
                "dom_metrics": probed.get("domMetrics", {}),
            }
        )
        for item in probed.get("stateCandidates", []):
            attempt["candidates"].extend(
                extract_candidates(
                    item.get("data", {}),
                    source="initial_state",
                    path=item.get("path", "initial_state"),
                    max_depth=2,
                )
            )
    except Exception as exc:  # Playwright error types vary by version.
        attempt["error"] = redact_sensitive_text(f"{type(exc).__name__}: {exc}")
        try:
            attempt["resolved_url"] = page.url
            attempt["title"] = page.title()
            attempt["body_head"] = page.locator("body").inner_text(timeout=1000)[:5000]
        except Exception:
            pass
    finally:
        page.close()
    return attempt


def collect(
    url: str,
    *,
    required: tuple[str, ...] = DEFAULT_REQUIRED,
    timeout_ms: int = 45_000,
    storage_state: str | None = None,
) -> tuple[dict[str, Any], int]:
    note_id = validate_xhs_note_url(url)
    if sync_playwright is None:
        result = {
            "schema_version": SCHEMA_VERSION,
            "platform": "xiaohongshu",
            "status": "dependency_missing",
            "source_url": redact_url(url),
            "note_id": note_id,
            "metrics": {},
            "required": list(required),
            "missing_required": list(required),
            "errors": ["缺少 Python Playwright；安装 requirements.txt 并安装 Chromium"],
            "fallback": {"required": True, "recommended": None},
        }
        return result, 1

    attempts: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context_options: dict[str, Any] = {
            "viewport": {"width": 1280, "height": 900},
            "locale": "zh-CN",
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        if storage_state:
            context_options["storage_state"] = storage_state
        context = browser.new_context(**context_options)
        try:
            attempts.append(probe_page(context, url, note_id, timeout_ms))
            interim = compose_result(
                source_url=url,
                note_id=note_id,
                attempts=attempts,
                required=required,
            )
            alternate = alternate_note_url(url)
            if (
                interim["missing_required"]
                and "app_only" in interim["blockers"]
                and alternate
            ):
                attempts.append(probe_page(context, alternate, note_id, timeout_ms))
        finally:
            context.close()
            browser.close()

    result = compose_result(
        source_url=url,
        note_id=note_id,
        attempts=attempts,
        required=required,
    )
    return result, 0 if not result["missing_required"] else 2


def parse_required(value: str) -> tuple[str, ...]:
    requested = tuple(dict.fromkeys(part.strip() for part in value.split(",") if part.strip()))
    invalid = sorted(set(requested) - ALLOWED_REQUIRED)
    if not requested:
        raise argparse.ArgumentTypeError("--required 不能为空")
    if invalid:
        raise argparse.ArgumentTypeError(
            f"未知字段：{', '.join(invalid)}；允许值：{', '.join(sorted(ALLOWED_REQUIRED))}"
        )
    return requested


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="抓取公开小红书笔记的互动数据")
    parser.add_argument("url", help="完整的 /explore/ 或 /discovery/item/ HTTPS 链接")
    parser.add_argument(
        "--required",
        type=parse_required,
        default=DEFAULT_REQUIRED,
        help="逗号分隔的必需字段；默认 liked,collected,commented",
    )
    parser.add_argument("--timeout-ms", type=int, default=45_000)
    parser.add_argument("--storage-state", help="用户明确提供的 Playwright storage_state 文件")
    parser.add_argument("--output", type=Path, help="可选 JSON 输出路径")
    args = parser.parse_args(argv)

    try:
        if args.timeout_ms < 1_000:
            raise ValueError("--timeout-ms 不得小于 1000")
        result, exit_code = collect(
            args.url,
            required=args.required,
            timeout_ms=args.timeout_ms,
            storage_state=args.storage_state,
        )
    except (OSError, ValueError) as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "platform": "xiaohongshu",
            "status": "error",
            "metrics": {},
            "errors": [str(exc)],
            "fallback": {"required": False, "recommended": None},
        }
        exit_code = 1
    except Exception as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "platform": "xiaohongshu",
            "status": "error",
            "metrics": {},
            "errors": [redact_sensitive_text(f"{type(exc).__name__}: {exc}")],
            "fallback": {"required": False, "recommended": None},
        }
        exit_code = 1

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
