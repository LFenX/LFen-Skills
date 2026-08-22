#!/usr/bin/env python3
"""Reseal the embedded runtime manifest and publish the Skill without runtime lookup."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = SKILL_ROOT / "assets" / "runtime"
MANIFEST_PATH = RUNTIME_ROOT / "embedded-manifest.json"
REFERENCE_FILES = [
    "01_治理基线/Vibe_Coding_公共术语与规范性用语基线_V6.3.md",
    "01_治理基线/Vibe_Coding_受控产物目录与状态模型_V6.3.md",
    "01_治理基线/Vibe_Coding_P2裁剪与扩展规范适用性决议_V6.3.md",
    "01_治理基线/Vibe_Coding_任务类型裁剪与统一执行流程规范_V6.3.md",
    "02_核心规范/C01_Product_Discovery_Evidence_and_Intent_Standard.md",
    "02_核心规范/C02_Initiative_and_Scope_Standard.md",
    "02_核心规范/C03_PRD_and_Feature_Standard.md",
    "02_核心规范/C04_Atomic_Requirement_and_Evolution_Standard.md",
    "02_核心规范/C05_Acceptance_Verification_and_Validation_Standard.md",
    "02_核心规范/C06_UX_and_Technical_Design_Standard.md",
    "02_核心规范/C07_Human_Agent_Collaboration_Standard.md",
    "02_核心规范/C08_Agent_Context_Governance_Standard.md",
    "02_核心规范/C09_Agent_Execution_and_Evidence_Standard.md",
    "02_核心规范/C10_Decision_Traceability_and_Lineage_Standard.md",
    "02_核心规范/C11_Configuration_Version_Baseline_and_Change_Standard.md",
    "02_核心规范/C12_Review_Quality_Gate_and_Product_Health_Standard.md",
    "03_扩展规范/E01_Architecture_Governance_Extension_Standard.md",
    "03_扩展规范/E02_Security_Privacy_and_Compliance_Extension_Standard.md",
    "03_扩展规范/E03_Data_and_AI_Data_Governance_Extension_Standard.md",
    "03_扩展规范/E04_Knowledge_and_Records_Governance_Extension_Standard.md",
    "03_扩展规范/E05_Product_Operations_and_Service_Management_Extension_Standard.md",
    "05_记录与登记册/V6.3_跨规范产物归属索引.md",
]
MAPPING_FILES = [
    (
        "01_治理基线/Vibe_Coding_领域Profile到元类型映射_V6.3.json",
        "mappings/profile-meta-map.json",
        "assets/runtime/mappings/profile-meta-map.json",
    ),
    (
        "01_治理基线/Vibe_Coding_裁剪适用性规则_V6.3.json",
        "mappings/tailoring-applicability-map.json",
        "assets/runtime/mappings/tailoring-applicability-map.json",
    ),
]
LOCAL_MAPPING_FILES = [
    "norm-action-taxonomy.json",
]

SKILL_REFERENCE_FILES = [
    "references/first-principles-method.md",
    "references/project-document-layout.md",
    "references/spec-source-map.md",
]
SCHEMA_FILES = [
    "authority-asset.schema.json",
    "derived-view.schema.json",
    "minimal-task-record.schema.json",
    "norm-consistency-report.schema.json",
    "norm-index-metadata.schema.json",
    "norm-query-result.schema.json",
    "norm-query.schema.json",
    "project-state.schema.json",
    "run-event.schema.json",
    "task-after.schema.json",
    "task-before.schema.json",
]
EVALUATION_FILES = [
    "norm-retrieval-budgets.json",
    "norm-retrieval-gold.json",
]
ASSET_TEMPLATE_FILES = [
    "project-docs.README.md",
    "project-governance.README.md",
    "requirement.README.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh_embedded() -> list[dict[str, str]]:
    previous_manifest = (
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if MANIFEST_PATH.is_file()
        else {"files": []}
    )
    manifest: list[dict[str, str]] = []
    for relative in REFERENCE_FILES:
        logical_path = f"references/{relative}"
        embedded_path = f"assets/runtime/norms/{relative}"
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"embedded norm is missing: {target}")
        manifest.append(
            {
                "role": "norm",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    for _legacy_relative, logical_path, embedded_path in MAPPING_FILES:
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"embedded mapping is missing: {target}")
        manifest.append(
            {
                "role": "mapping",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    for name in LOCAL_MAPPING_FILES:
        logical_path = f"mappings/{name}"
        embedded_path = f"assets/runtime/mappings/{name}"
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"local runtime mapping is missing: {target}")
        manifest.append(
            {
                "role": "mapping",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    for relative in SKILL_REFERENCE_FILES:
        target = SKILL_ROOT / relative
        if not target.is_file():
            raise FileNotFoundError(f"local runtime fact is missing: {target}")
        manifest.append(
            {
                "role": "skill-reference",
                "source": f"skill-local:{relative}",
                "logical_path": relative,
                "embedded": relative,
                "sha256": sha256(target),
            }
        )
    for name in SCHEMA_FILES:
        logical_path = f"schemas/{name}"
        embedded_path = f"assets/runtime/schemas/{name}"
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"local runtime schema is missing: {target}")
        manifest.append(
            {
                "role": "schema",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    for name in EVALUATION_FILES:
        logical_path = f"evaluations/{name}"
        embedded_path = f"assets/runtime/evaluations/{name}"
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"local runtime evaluation is missing: {target}")
        manifest.append(
            {
                "role": "evaluation",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    for name in ASSET_TEMPLATE_FILES:
        logical_path = f"project-templates/{name}"
        embedded_path = f"assets/project-templates/{name}"
        target = SKILL_ROOT / embedded_path
        if not target.is_file():
            raise FileNotFoundError(f"local asset template is missing: {target}")
        manifest.append(
            {
                "role": "asset-template",
                "source": f"skill-local:{logical_path}",
                "logical_path": logical_path,
                "embedded": embedded_path,
                "sha256": sha256(target),
            }
        )
    active_embedded = {item["embedded"] for item in manifest}
    for item in previous_manifest.get("files", []):
        stale_relative = item.get("embedded")
        if not isinstance(stale_relative, str) or stale_relative in active_embedded:
            continue
        stale = (SKILL_ROOT / stale_relative).resolve()
        try:
            stale.relative_to(SKILL_ROOT.resolve())
        except ValueError as exc:
            raise ValueError(f"stale manifest entry escapes Skill root: {stale_relative}") from exc
        if stale.is_file():
            stale.unlink()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "schema_version": "6.3-candidate",
                "layout_version": "skill-runtime-v2",
                "source_of_truth": "LFen-Skills/run-web-product-workflow; the embedded runtime assets are the sole editing source of truth for the norms, mappings, schemas and evaluations they contain",
                "files": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def publish(destination: Path) -> int:
    resolved = destination.resolve()
    if resolved == SKILL_ROOT.resolve():
        return 0
    if SKILL_ROOT.resolve() in resolved.parents or resolved in SKILL_ROOT.resolve().parents:
        raise ValueError("publish source and destination must not contain one another")
    source_files = {
        source.relative_to(SKILL_ROOT)
        for source in SKILL_ROOT.rglob("*")
        if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc"
    }
    if resolved.exists():
        stale_files = [
            target for target in resolved.rglob("*")
            if target.is_file()
            and target.relative_to(resolved) not in source_files
        ]
        for target in stale_files:
            target.resolve().relative_to(resolved)
            target.unlink()
        for directory in sorted(
            (path for path in resolved.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            if not any(directory.iterdir()):
                directory.rmdir()
    copied = 0
    for relative in sorted(source_files, key=lambda path: path.as_posix()):
        source = SKILL_ROOT / relative
        target = resolved / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute the SHA-256 of every protected runtime asset from the Skill's "
            "own files and rewrite embedded-manifest.json. The Skill is the sole "
            "editing source of truth; no external specification repository is read."
        )
    )
    parser.add_argument(
        "--publish-to",
        type=Path,
        help="Optional installed Skill directory to update after refreshing embedded norms.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = refresh_embedded()
        print(f"RESEALED: {len(manifest)} embedded runtime fact files")
        if args.publish_to:
            count = publish(args.publish_to)
            if count == 0 and args.publish_to.resolve() == SKILL_ROOT.resolve():
                print(f"LINKED: {args.publish_to} resolves to the source Skill; no copy required")
            else:
                print(f"PUBLISHED: {count} files to {args.publish_to.resolve()}")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
