#!/usr/bin/env python3
"""Deterministic regression tests for fetch_xhs_interactions.py."""

from __future__ import annotations

import unittest

import fetch_xhs_interactions as target


class FetchXhsInteractionsTests(unittest.TestCase):
    def test_accepts_supported_note_urls(self) -> None:
        note_id = "0123456789abcdef01234567"
        self.assertEqual(
            target.validate_xhs_note_url(
                f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token=secret"
            ),
            note_id,
        )
        self.assertEqual(
            target.validate_xhs_note_url(
                f"https://www.xiaohongshu.com/discovery/item/{note_id}"
            ),
            note_id,
        )

    def test_rejects_non_note_or_foreign_urls(self) -> None:
        with self.assertRaises(ValueError):
            target.validate_xhs_note_url("https://example.com/explore/1234")
        with self.assertRaises(ValueError):
            target.validate_xhs_note_url(
                "https://www.xiaohongshu.com/livestream/570467089097367877"
            )

    def test_redacts_tokens_without_changing_navigation_input(self) -> None:
        url = (
            "https://www.xiaohongshu.com/explore/0123456789abcdef01234567"
            "?xsec_token=secret&xsec_source=pc_feed"
        )
        redacted = target.redact_url(url)
        self.assertNotIn("secret", redacted)
        self.assertIn("xsec_source=pc_feed", redacted)
        redirected = target.redact_url(
            "https://www.xiaohongshu.com/login?redirectPath="
            "https%3A%2F%2Fwww.xiaohongshu.com%2Fexplore%2Fabc%3Fxsec_token%3Dnested-secret"
        )
        self.assertNotIn("nested-secret", redirected)
        error = target.redact_sensitive_text(
            "navigation failed at https://www.xiaohongshu.com/explore/abc?xsec_token=error-secret"
        )
        self.assertNotIn("error-secret", error)

    def test_ignores_unrelated_single_metric_counters(self) -> None:
        candidates = target.extract_candidates(
            {"notification": {"notificationCount": {"likeCount": 0}}},
            source="initial_state",
            path="__INITIAL_STATE__",
        )
        self.assertEqual(candidates, [])

    def test_normalizes_abbreviated_counts_without_claiming_exactness(self) -> None:
        self.assertEqual(
            target.normalize_metric("2.5万"),
            {"display": "2.5万", "normalized_value": 25_000, "exact": False},
        )
        self.assertEqual(
            target.normalize_metric("366"),
            {"display": "366", "normalized_value": 366, "exact": True},
        )

    def test_prefers_matching_note_candidate(self) -> None:
        note_id = "0123456789abcdef01234567"
        payload = {
            "unrelated": {
                "noteId": "ffffffffffffffffffffffff",
                "likedCount": "9999",
                "collectedCount": "999",
                "commentCount": "99",
                "shareCount": "9",
            },
            "note": {
                "noteId": note_id,
                "interactInfo": {
                    "likedCount": "2.5万",
                    "collectedCount": "366",
                    "commentCount": "1709",
                },
            },
        }
        attempts = [
            {
                "title": "测试笔记",
                "resolved_url": f"https://www.xiaohongshu.com/explore/{note_id}",
                "body_head": "",
                "candidates": target.extract_candidates(payload, source="initial_state"),
                "dom_metrics": {},
                "error": None,
            }
        ]
        result = target.compose_result(
            source_url=attempts[0]["resolved_url"],
            note_id=note_id,
            attempts=attempts,
            required=target.DEFAULT_REQUIRED,
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["metrics"]["liked"]["display"], "2.5万")
        self.assertEqual(result["metrics"]["commented"]["normalized_value"], 1709)

    def test_login_wall_requests_browser_only_when_required_fields_are_missing(self) -> None:
        note_id = "0123456789abcdef01234567"
        result = target.compose_result(
            source_url=f"https://www.xiaohongshu.com/explore/{note_id}",
            note_id=note_id,
            attempts=[
                {
                    "title": "小红书",
                    "resolved_url": f"https://www.xiaohongshu.com/explore/{note_id}",
                    "body_head": "扫码登录 登录后查看完整内容",
                    "candidates": [],
                    "dom_metrics": {},
                    "error": None,
                }
            ],
            required=target.DEFAULT_REQUIRED,
        )
        self.assertEqual(result["status"], "browser_session_required")
        self.assertTrue(result["fallback"]["required"])
        self.assertEqual(result["fallback"]["recommended"], "existing_browser_session_dom")


if __name__ == "__main__":
    unittest.main(verbosity=2)
