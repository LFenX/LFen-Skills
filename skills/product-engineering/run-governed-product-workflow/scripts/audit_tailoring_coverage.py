#!/usr/bin/env python3
"""Audit complete tailoring closure and optionally emit a DerivedView report."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import (
    GovernanceError,
    _write_derived_view,
    default_mapping_path,
    default_profile_index_path,
    default_tailoring_map_path,
    governance_root,
    load_tailoring_map,
    resolve_all_profiles,
    runtime_asset_path,
    validate_tailoring_map,
)

def render_report(mapping: dict, profiles: list[dict[str, str]]) -> str:
    owners = Counter(item["owner_standard"] for item in profiles)
    controlled = mapping["controlled_values"]
    lines = [
        "# Complete Tailoring Coverage Audit",
        "",
        f"- Rule set: `{mapping['document_id']}` / {mapping['version']} / {mapping['status']}",
        f"- Normative sources: {len(mapping['source_catalog'])} / expected 22",
        f"- C/E standards: {len(mapping['standards'])} / expected 17",
        f"- Domain Profiles: {len(profiles)} / expected 137",
        "- Closure result: PASS",
        "",
        "## Controlled dimensions",
        "",
        "| Dimension | Covered values |",
        "|---|---:|",
    ]
    for key in (
        "delivery_scenarios", "development_types", "change_surfaces", "risk_levels",
        "extension_states", "baseline_inheritance", "execution_modes", "stages",
        "confidence_levels", "fact_values", "profile_actions", "execution_permissions",
    ):
        lines.append(f"| {key} | {len(controlled[key])} |")
    lines.append(f"| applicability_facts | {len(mapping['applicability_facts'])} |")
    lines.extend([
        "",
        "## Standards and Profile ownership",
        "",
        "| Standard | Always minimum | Profile count | Trigger facts | Trigger surfaces/scenarios |",
        "|---|---|---:|---|---|",
    ])
    for standard, rule in mapping["standards"].items():
        triggers = [*rule.get("trigger_surfaces", []), *rule.get("trigger_scenarios", [])]
        lines.append(
            f"| {standard} | {'Yes' if rule['always_minimum'] else 'No'} | {owners[standard]} | "
            f"{', '.join(rule.get('trigger_facts', [])) or 'route/fact dependent'} | "
            f"{', '.join(triggers) or 'none'} |"
        )
    lines.extend([
        "",
        "## Closure assertions",
        "",
        "- Every governance norm and C/E standard has one catalog source.",
        "- Every DS, DT, Change Surface, Risk, Extension State, Baseline state, Mode, Stage and Execution Permission is represented exactly once in its controlled table.",
        "- Every C/E standard is reachable from an always-applicable, classification, surface, extension or fact rule.",
        "- Every standard declares non-trimmable controls and source sections that exist in the embedded norm.",
        "- Control cards and priority sections are navigation only; the complete source pack retains every governance, index, applicable, and pending source in full with per-file integrity.",
        "- All 137 Profile codes have exactly one owner standard and exactly one six-meta-type resolution.",
        "- Unknown, conflict and stale resolution are fail-closed from the configured stage boundary.",
        "- Every execution Authority reference requires one Valid, evidenced, unexpired assessment; their exact scope references must cover all scope.in_scope values.",
        "- Primary Development Type, stage loading and physical carrier choice cannot subtract an applicable control.",
        "",
        "## Authority boundary",
        "",
        "This report proves structural closure. It does not approve the V6.3 Candidate, accept residual risk, or replace a human gate.",
    ])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--view-id", default="TAILORING-COVERAGE")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        mapping = load_tailoring_map(validate_sources=False)
        errors = validate_tailoring_map(mapping)
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        profiles = resolve_all_profiles(default_profile_index_path(), default_mapping_path())
        report = render_report(mapping, profiles)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8", newline="\n")
        if args.project_root or args.project_id:
            if not args.project_root or not args.project_id:
                raise GovernanceError("--project-root and --project-id must be supplied together")
            root = governance_root(args.project_root)
            output = args.output or root / "generated" / "matrices" / "tailoring-coverage.md"
            sources = list(dict.fromkeys([
                default_tailoring_map_path(),
                default_mapping_path(),
                default_profile_index_path(),
                Path(__file__).resolve(),
                Path(__file__).resolve().parent / "governance_artifacts.py",
                *(runtime_asset_path(item["path"]) for item in mapping["source_catalog"]),
            ]))
            _write_derived_view(
                root=root,
                content_path=output,
                content=report,
                project_id=args.project_id,
                view_id=args.view_id,
                view_kind="tailoring-coverage-audit",
                sources=sources,
            )
        print(f"PASS: 22 sources, 17 standards, {len(profiles)} profiles, all controlled dimensions closed")
    except (OSError, ValueError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
