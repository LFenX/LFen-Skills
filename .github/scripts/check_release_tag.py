#!/usr/bin/env python3
"""Fail unless a release tag names the version the Skill declares."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[2] / "run-web-product-workflow" / "SKILL.md"
PREFIX = "rwpw-v"


def declared_version() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"ERROR: {SKILL_MD.name} has no YAML frontmatter")
    match = re.search(r"^\s+version:\s*(\S+)\s*$", parts[1], re.MULTILINE)
    if not match:
        raise SystemExit(f"ERROR: {SKILL_MD.name} frontmatter declares no metadata.version")
    return match.group(1)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: check_release_tag.py <tag>")
    tag = argv[1]
    expected = PREFIX + declared_version()
    print(f"tag={tag} expected={expected}")
    if tag != expected:
        print(f"::error::tag {tag} does not match SKILL.md metadata.version; expected {expected}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
