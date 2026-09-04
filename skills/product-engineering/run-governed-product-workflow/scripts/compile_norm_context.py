#!/usr/bin/env python3
"""Compile a stage-specific, auditable norm packet from a TaskContract."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
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
    read_json,
    retrieval_contract_projection_bytes,
    retrieval_contract_reference,
    resolve_all_profiles,
    resolve_tailoring,
    runtime_asset_path,
    schema_path,
    sha256_file,
)


def canonical_tree(value: object) -> object:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [canonical_tree(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonical_tree(item) for key, item in value.items()}
    return value


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        canonical_tree(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def render_retrieval_plan(
    before: dict,
    resolution: dict,
    *,
    before_path: Path,
    packet_json_path: Path,
    packet_markdown_path: Path,
    source_pack_path: Path,
) -> tuple[dict, list[Path]]:
    """Create the deterministic hand-off from the Norm Packet to bounded queries."""

    taxonomy_path = runtime_asset_path("mappings/norm-action-taxonomy.json")
    query_schema_path = schema_path("norm-query.schema.json")
    result_schema_path = schema_path("norm-query-result.schema.json")
    query_script_path = Path(__file__).resolve().parent / "query_norm_context.py"
    compiler_path = Path(__file__).resolve()
    governance_path = compiler_path.parent / "governance_artifacts.py"
    taxonomy = read_json(taxonomy_path)
    stage = resolution["stage"]
    actions = []
    for action_id, definition in sorted(taxonomy["actions"].items()):
        if stage not in definition["stages"]:
            continue
        actions.append({
            "action": action_id,
            "required_control_types": definition["required_control_types"],
            "pinned_control_types": definition["pinned_control_types"],
        })
    if not actions:
        raise GovernanceError(f"action taxonomy has no action for stage {stage}")
    source_ids = [item["source_id"] for item in resolution["complete_source_files"]]
    plan_sources = [
        before_path,
        packet_json_path,
        packet_markdown_path,
        source_pack_path,
        taxonomy_path,
        query_schema_path,
        result_schema_path,
        query_script_path,
        compiler_path,
        governance_path,
    ]

    def reference(path: Path, role: str) -> dict[str, str]:
        return {
            "role": role,
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
        }

    tailoring_sha256 = canonical_digest(resolution)
    plan = {
        "schema_version": "6.3-candidate",
        "plan_version": "1.0",
        "plan_type": "bounded-norm-retrieval",
        "project_id": before["project_id"],
        "task_id": before["task_id"],
        "stage": stage,
        "status": "ShadowReady",
        "activation": {
            "mode": "Shadow",
            "release_authorized": False,
            "remote_semantic_enabled": False,
        },
        "source_boundary": {
            "tailoring_resolution_sha256": tailoring_sha256,
            "normative_sources_sha256": resolution["normative_sources_sha256"],
            "source_ids": source_ids,
        },
        "inputs": [
            retrieval_contract_reference(before_path, before),
            reference(packet_json_path, "norm-packet-json"),
            reference(packet_markdown_path, "norm-packet-markdown"),
            reference(source_pack_path, "complete-source-pack"),
            reference(taxonomy_path, "action-taxonomy"),
            reference(query_schema_path, "query-schema"),
            reference(result_schema_path, "query-result-schema"),
            reference(query_script_path, "query-runtime"),
            reference(compiler_path, "compiler"),
            reference(governance_path, "governance-runtime"),
        ],
        "allowed_actions": actions,
        "request_template": {
            "schema_version": "6.3-candidate",
            "task_id": before["task_id"],
            "stage": stage,
            "action": None,
            "query_text": None,
            "tailoring_resolution_sha256": tailoring_sha256,
            "normative_sources_sha256": resolution["normative_sources_sha256"],
            "budget_profile": "standard",
            "modes": ["exact", "fts"],
            "requested_additional_control_types": [],
        },
        "required_agent_inputs": ["action", "query_text"],
        "invocation": {
            "executable": "python",
            "script": "${SKILL_ROOT}/scripts/query_norm_context.py",
            "arguments": [
                "--task-dir", str(before_path.parent.resolve()),
                "--request-json-file", "${QUERY_REQUEST_JSON}",
            ],
        },
        "outcome_policy": {
            "Complete": "consume clause-context.md and its cited controls",
            "Expanded": "follow fallback.event_ref and read the indicated parent section, complete source, or ordered source page",
            "Blocked": "stop the material action; do not bypass the blocker with rg or uncited memory",
        },
        "fallback_chain": [
            "clause", "parent-section", "complete-source", "ordered-source-pages", "blocked"
        ],
        "source_pack_retained": True,
        "diagnostic_fallback": {
            "tool": "rg",
            "scope": str(source_pack_path.resolve()),
            "condition": "query runtime diagnosis or an explicit Expanded fallback only",
            "cannot_bypass": ["Blocked", "Tailoring Resolution", "Authority", "Gate"],
        },
    }
    return plan, plan_sources

def section_text(path: Path, section: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"## {section}. ")), None)
    if start is None:
        raise GovernanceError(f"{path}: missing section {section}")
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip()


def render_source_pack(resolution: dict) -> str:
    """Materialize every selected source completely while preserving per-file integrity.

    The pack body is a pure function of the resolved source set. Naming the task and
    stage in the heading made three byte-different copies of the same 1.2 MB within one
    task and defeated any deduplication; that identity already lives in the DerivedView
    envelope (`view_id`, `sources`, `content_ref`), which is where it belongs.
    """

    lines = [
        "# Complete Norm Source Pack",
        "",
        "This DerivedView contains the complete UTF-8 contents of every governance, index, applicable, and pending source selected by the resolution.",
        "Use the navigation packet and search to read targeted passages; omission from a control card never means N/A.",
        "",
    ]
    for source in resolution["complete_source_files"]:
        source_path = runtime_asset_path(source["path"])
        actual_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_sha != source["sha256"]:
            raise GovernanceError(f"source changed during compilation: {source['source_id']}")
        lines.extend([
            f"<!-- SOURCE-BEGIN {source['source_id']} sha256={actual_sha} path={source['path']} -->",
            "",
            source_path.read_text(encoding="utf-8").rstrip(),
            "",
            f"<!-- SOURCE-END {source['source_id']} -->",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def render_packet(before: dict, resolution: dict, mapping: dict, *, include_source_text: bool) -> str:
    rules = mapping["standards"]
    profile_counts: dict[str, int] = {}
    for profile in resolve_all_profiles(default_profile_index_path(), default_mapping_path()):
        owner = profile["owner_standard"]
        profile_counts[owner] = profile_counts.get(owner, 0) + 1
    lines = [
        f"# Norm Packet: {before['task_id']} / {resolution['stage']}",
        "",
        f"- Objective: {before['objective']}",
        f"- Rule set: `{resolution['rule_set_id']}` / `{resolution['rule_set_sha256']}`",
        f"- Normative sources digest: `{resolution['normative_sources_sha256']}`",
        f"- Resolver digest: `{resolution['resolver_sha256']}`",
        f"- TaskContract Schema digest: `{resolution['task_contract_schema_sha256']}`",
        f"- Task Profile digest: `{resolution['input_digest']}`",
        f"- Control strength: {resolution['control_strength']}",
        f"- Independent review: {resolution['independent_review']}",
        f"- Explicit human gate: {resolution['explicit_human_gate']}",
        f"- Applicable standards: {', '.join(resolution['applicable_standards'])}",
        f"- Stage context: {', '.join(resolution['stage_context_standards'])}",
        f"- Pending standards: {', '.join(resolution['pending_standards']) or 'None'}",
        "",
        "## Blocking reasons",
        "",
    ]
    lines.extend(f"- STOP: {item}" for item in resolution["blocking_reasons"])
    if not resolution["blocking_reasons"]:
        lines.append("- None")
    lines.extend([
        "",
        "## Complete normative coverage",
        "",
        "- `norm-source-pack.md` contains the complete contents and SHA-256 of every selected governance, index, applicable, and pending source.",
        "- The control cards and section locators below are non-exhaustive navigation aids; they are never the complete normative obligation set.",
        "- Before a material action, search the Source Pack and read the passages governing that action. If relevance cannot be narrowed safely, read the complete selected source.",
        "",
        "## Non-trimmable control cards (navigation summary)",
        "",
    ])
    for standard in resolution["stage_context_standards"]:
        rule = rules[standard]
        lines.extend([
            f"### {standard} — {rule['name']}",
            "",
            f"- Owned Profiles in full index: {profile_counts.get(standard, 0)}",
            f"- Source sections: {', '.join('§' + item for item in rule['source_sections'])}",
        ])
        lines.extend(f"- MUST: {control}" for control in rule["non_trimmable_controls"])
        lines.append("")
    lines.extend([
        "## Profile instantiation rules",
        "",
        *(f"- {item}" for item in mapping["profile_resolution"]["rules"]),
        "",
        "## Resolution rules",
        "",
        *(f"- {item['order']}. {item['rule']}" for item in mapping["precedence"]),
        "",
        "## Source locators",
        "",
        "| Source | Sections | Embedded path |",
        "|---|---|---|",
    ])
    for source in resolution["source_sections"]:
        lines.append(f"| {source['source_id']} | {', '.join('§' + item for item in source['sections'])} | `{source['path']}` |")
    if include_source_text:
        lines.extend(["", "## Selected normative text", ""])
        for source in resolution["source_sections"]:
            source_path = runtime_asset_path(source["path"])
            for section in source["sections"]:
                lines.extend([
                    f"### {source['source_id']} §{section}",
                    "",
                    section_text(source_path, section),
                    "",
                ])
    lines.extend([
        "",
        "## Compiler boundary",
        "",
        "This packet is a DerivedView. Normative authority remains in the cited sources and VC-PPG-TAIL-001. A hash or source change makes this packet stale.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--stage", choices=tuple(f"S{value}" for value in range(1, 9)))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--include-source-text", action="store_true", help="Also inline priority sections in the navigation packet; the complete Source Pack is always generated")
    parser.add_argument("--enforce", action="store_true", help="Exit 3 when the resolved packet contains blockers")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        task_dir = args.task_dir.resolve()
        before_path = task_dir / "before.json"
        before = read_json(before_path)
        stored = before.get("tailoring_resolution", {})
        stage = args.stage or stored.get("stage")
        resolution = resolve_tailoring(before["task_profile"], stage=stage, contract_context=before)
        stored_is_current = stored == resolution
        mapping = load_tailoring_map()
        project_root = task_dir.parents[2]
        root = governance_root(project_root)
        output_dir = args.output_dir or root / "generated" / "contexts" / before["task_id"] / stage
        json_path = output_dir / "norm-packet.json"
        markdown_path = output_dir / "norm-packet.md"
        source_pack_path = output_dir / "norm-source-pack.md"
        retrieval_plan_path = output_dir / "retrieval-plan.json"
        sources = list(dict.fromkeys([
            before_path,
            default_tailoring_map_path(),
            default_mapping_path(),
            default_profile_index_path(),
            Path(__file__).resolve(),
            Path(__file__).resolve().parent / "governance_artifacts.py",
            schema_path("task-before.schema.json"),
            *(runtime_asset_path(item["path"]) for item in mapping["source_catalog"]),
        ]))
        _write_derived_view(
            root=root,
            content_path=json_path,
            content=json.dumps(resolution, ensure_ascii=False, indent=2) + "\n",
            project_id=before["project_id"],
            view_id=f"DV-{before['project_id']}-{before['task_id']}-{stage}-NORM-JSON",
            view_kind="compiled-norm-packet-machine",
            sources=sources,
        )
        _write_derived_view(
            root=root,
            content_path=markdown_path,
            content=render_packet(before, resolution, mapping, include_source_text=args.include_source_text),
            project_id=before["project_id"],
            view_id=f"DV-{before['project_id']}-{before['task_id']}-{stage}-NORM-MD",
            view_kind="compiled-norm-packet-human",
            sources=sources,
        )
        _write_derived_view(
            root=root,
            content_path=source_pack_path,
            content=render_source_pack(resolution),
            project_id=before["project_id"],
            view_id=f"DV-{before['project_id']}-{before['task_id']}-{stage}-NORM-SOURCES",
            view_kind="compiled-complete-norm-source-pack",
            sources=sources,
            dedupe_store=root / "generated" / "source-packs",
        )
        retrieval_plan, retrieval_plan_sources = render_retrieval_plan(
            before,
            resolution,
            before_path=before_path,
            packet_json_path=json_path,
            packet_markdown_path=markdown_path,
            source_pack_path=source_pack_path,
        )
        _write_derived_view(
            root=root,
            content_path=retrieval_plan_path,
            content=json.dumps(retrieval_plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            project_id=before["project_id"],
            view_id=f"DV-{before['project_id']}-{before['task_id']}-{stage}-RETRIEVAL-PLAN",
            view_kind="compiled-norm-retrieval-plan",
            sources=retrieval_plan_sources,
            source_content_overrides={
                before_path: retrieval_contract_projection_bytes(before),
            },
        )
        print(markdown_path)
        print(source_pack_path)
        if args.enforce and not stored_is_current:
            print("BLOCKED: stored tailoring_resolution is stale or targets a different stage; amend TaskContract before execution")
            return 3
        if args.enforce and resolution["blocking_reasons"]:
            for reason in resolution["blocking_reasons"]:
                print(f"BLOCKED: {reason}")
            return 3
    except (OSError, ValueError, KeyError, GovernanceError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
