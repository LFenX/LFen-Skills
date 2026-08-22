#!/usr/bin/env python3
"""Positive and negative conformance tests for V6.3 Candidate."""

from __future__ import annotations

import copy
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from governance_artifacts import (
    GovernanceError,
    _write_derived_view,
    amend_record,
    append_run_event,
    capture_source_snapshot,
    close_task,
    default_profile_index_path,
    embedded_manifest_path,
    generate_views,
    initialize_task,
    load_tailoring_map,
    read_json,
    register_authority_asset,
    rebuild_project_state,
    resolve_all_profiles,
    resolve_tailoring,
    runtime_asset_path,
    validate_embedded_manifest,
    validate_json_document,
    validate_retrieval_plan,
    validate_tailoring_map,
    validate_task_directory,
)
from sync_embedded_references import publish
from audit_norm_retrieval import claim_mandatory_target_identity, validate_contracts
from build_norm_index import (
    bootstrap_project_runtime,
    run_lock_lifecycle_fixtures,
    run_parser_fixtures,
)
from manage_project_docs import (
    apply_migration_plan,
    create_migration_plan,
    sha256_file,
    validate_project_document_layout,
)
from minimal_task import (
    append_minimal_event,
    close_minimal_record,
    create_minimal_record,
    validate_minimal_record,
)
from query_norm_context import run_query_planner_fixtures
from validate_task_package import QUERY_PUBLICATION_FILES, inspect_active_query_tree


class SelfTestFailure(RuntimeError):
    """Raised when a conformance invariant fails with an actionable message."""


def require_test(condition: bool, message: object) -> None:
    if not condition:
        raise SelfTestFailure(str(message))


TEST_FACTS = {
    "product_intent_change": "No",
    "initiative_scope_change": "No",
    "requirement_change": "No",
    "external_behavior_change": "No",
    "design_change": "No",
    "architecture_impact": "No",
    "security_privacy_impact": "No",
    "data_ai_impact": "Yes",
    "formal_knowledge_records": "No",
    "operations_impact": "No",
    "production_release": "No",
    "irreversible_change": "No",
    "actual_execution": "Yes",
    "authority_available": "Yes",
    "migration_retirement": "No",
    "external_system_effect": "No",
    "formal_review_or_gate": "Yes",
}


def expect_governance_error(label: str, operation) -> None:
    try:
        operation()
    except GovernanceError:
        return
    raise SelfTestFailure(f"negative test did not fail: {label}")


def run_active_query_tree_fixtures() -> dict[str, object]:
    """Exercise discovery without depending on query-result.json as the root sentinel."""

    checks = 0
    link_checks = 0
    with tempfile.TemporaryDirectory(prefix="v63-active-query-tree-") as temp:
        query_root = Path(temp) / "T-QUERY"
        requests_root = query_root / "requests"
        publication = query_root / ("a" * 64)
        requests_root.mkdir(parents=True)
        (requests_root / "run-started.json").write_text("{}\n", encoding="utf-8")
        publication.mkdir()

        def restore(directory: Path) -> None:
            directory.mkdir(parents=True, exist_ok=True)
            for name in QUERY_PUBLICATION_FILES:
                (directory / name).write_text("fixture\n", encoding="utf-8")

        restore(publication)
        requests, results = inspect_active_query_tree(query_root)
        require_test((len(requests) == 1 and results == [(publication / "query-result.json").resolve()]), "self-test invariant failed at original line 118: len(requests) == 1 and results == [(publication / 'query-result.json').resolve()]")
        checks += 1

        for name in sorted(QUERY_PUBLICATION_FILES):
            target = publication / name
            target.unlink()
            expect_governance_error(
                f"active publication missing {name}",
                lambda: inspect_active_query_tree(query_root),
            )
            target.write_text("fixture\n", encoding="utf-8")
            checks += 1

        shutil.rmtree(publication)
        expect_governance_error(
            "active request lost its complete publication directory",
            lambda: inspect_active_query_tree(query_root),
        )
        checks += 1

        paged = query_root / ("b" * 64) / "page-0001"
        restore(paged)
        requests, results = inspect_active_query_tree(query_root)
        require_test((len(requests) == 1 and results == [(paged / "query-result.json").resolve()]), "self-test invariant failed at original line 141: len(requests) == 1 and results == [(paged / 'query-result.json').resolve()]")
        checks += 1
        (paged / "clause-context.md.view.json").unlink()
        expect_governance_error(
            "partial paged publication",
            lambda: inspect_active_query_tree(query_root),
        )
        checks += 1

        restore(paged)
        empty_page = query_root / ("c" * 64) / "page-0002"
        empty_page.mkdir(parents=True)
        expect_governance_error(
            "empty paged publication",
            lambda: inspect_active_query_tree(query_root),
        )
        checks += 1
        shutil.rmtree(empty_page.parent)

        missing_root = Path(temp) / "missing-query-root"
        expect_governance_error(
            "required active query root is missing",
            lambda: inspect_active_query_tree(missing_root, required=True),
        )
        checks += 1

        request_path = requests_root / "run-started.json"
        outside_request = Path(temp) / "outside-request.json"
        try:
            shutil.move(request_path, outside_request)
            os.symlink(outside_request, request_path)
            expect_governance_error(
                "request file link",
                lambda: inspect_active_query_tree(query_root, required=True),
            )
            link_checks += 1
        except OSError:
            pass
        finally:
            if request_path.is_symlink():
                request_path.unlink()
            if outside_request.exists():
                shutil.move(outside_request, request_path)

        outside_requests = Path(temp) / "outside-requests"
        try:
            shutil.move(requests_root, outside_requests)
            os.symlink(outside_requests, requests_root, target_is_directory=True)
            expect_governance_error(
                "request registry directory link",
                lambda: inspect_active_query_tree(query_root, required=True),
            )
            link_checks += 1
        except OSError:
            pass
        finally:
            if requests_root.is_symlink():
                requests_root.unlink()
            if outside_requests.exists():
                shutil.move(outside_requests, requests_root)

    return {"status": "Passed", "checks": checks, "link_checks": link_checks}


def run_derived_view_byte_fixture() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="v63-derived-view-bytes-") as temp:
        project_root = Path(temp)
        governance = project_root / ".project-governance"
        source = project_root / "source.txt"
        source.write_text("source\n", encoding="utf-8")
        content = governance / "generated" / "fixture.md"
        _, envelope = _write_derived_view(
            root=governance,
            content_path=content,
            content="fixture\n",
            project_id="P-TEST",
            view_id="DV-P-TEST-BYTE-FIXTURE",
            view_kind="byte-fixture",
            sources=[source],
        )
        read_json(envelope)
        envelope.write_bytes(envelope.read_bytes() + b"\n")
        expect_governance_error(
            "DerivedView trailing byte change",
            lambda: read_json(envelope),
        )
    return {"status": "Passed", "checks": 2}


def run_new_query_history_fixture() -> dict[str, object]:
    """A first query publication is a legal state even when no history root exists."""

    with tempfile.TemporaryDirectory(prefix="v63-new-query-history-") as temp:
        root = Path(temp)
        task_id = "T-NEW"
        digest = "d" * 64
        query_root = root / ".project-governance" / "generated" / "queries" / task_id
        request_path = query_root / "requests" / "first.json"
        publication = query_root / digest
        request_path.parent.mkdir(parents=True)
        publication.mkdir(parents=True)
        request_path.write_text(
            json.dumps({"task_id": task_id, "action": "run_started"}) + "\n",
            encoding="utf-8",
        )
        request_ref = request_path.relative_to(root).as_posix()
        generated_at = "2026-08-21T00:00:00+00:00"
        (publication / "query-result.json").write_text(
            json.dumps({"query_digest": digest}) + "\n", encoding="utf-8"
        )
        (publication / "query-result.json.view.json").write_text(
            json.dumps({"generated_at": generated_at, "sources": [request_ref]}) + "\n",
            encoding="utf-8",
        )
        (publication / "clause-context.md").write_text("fixture\n", encoding="utf-8")
        (publication / "clause-context.md.view.json").write_text("{}\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-X",
                "utf8",
                str(Path(__file__).resolve().parent / "rebuild_query_history_index.py"),
                "--project-root",
                str(root),
                "--task-id",
                task_id,
                "--reason",
                "first-publication fixture",
                "--reconciled-at",
                "2026-08-21T00:01:00+00:00",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        require_test((result.returncode == 0), (result.stdout + result.stderr))
        index = read_json(
            root
            / ".project-governance"
            / "generated"
            / "query-history"
            / task_id
            / "archive-index.json"
        )
        require_test((index["publications"] == []), "self-test invariant failed at original line 287: index['publications'] == []")
        require_test((len(index["active_publications"]) == 1), "self-test invariant failed at original line 288: len(index['active_publications']) == 1")
    return {"status": "Passed", "checks": 2}


def run_document_governance_fixture() -> dict[str, object]:
    """Prove README initialization and reversible, hash-bound legacy migration."""

    with tempfile.TemporaryDirectory(prefix="v63-doc-governance-") as temp:
        root = Path(temp)
        root.mkdir(exist_ok=True)
        legacy = root / "docs"
        legacy.mkdir()
        source = legacy / "REQ-42_产品需求文档.md"
        source.write_text("# Legacy requirement\n", encoding="utf-8")
        plan_path = create_migration_plan(root, migration_id="M-001")
        plan_sha256 = sha256_file(plan_path)
        expect_governance_error(
            "migration requires exact plan confirmation",
            lambda: apply_migration_plan(
                plan_path,
                confirmed_plan_sha256="0" * 64,
                authorized_by="self-test",
            ),
        )
        manifest_path, report_path = apply_migration_plan(
            plan_path,
            confirmed_plan_sha256=plan_sha256,
            authorized_by="self-test",
        )
        manifest = read_json(manifest_path)
        migrated = manifest["files"][0]
        require_test((not source.exists()), 'self-test invariant failed at original line 319: not source.exists()')
        require_test((sha256_file(root / migrated["backup"]) == migrated["sha256"]), "self-test invariant failed at original line 320: sha256_file(root / migrated['backup']) == migrated['sha256']")
        require_test((sha256_file(root / migrated["target"]) == migrated["sha256"]), "self-test invariant failed at original line 321: sha256_file(root / migrated['target']) == migrated['sha256']")
        require_test((report_path.is_file()), 'self-test invariant failed at original line 322: report_path.is_file()')
        require_test(((root / ".project-governance" / "README.md").is_file()), "self-test invariant failed at original line 323: (root / '.project-governance' / 'README.md').is_file()")
        require_test(((root / "LG_project_docs" / "README.md").is_file()), "self-test invariant failed at original line 324: (root / 'LG_project_docs' / 'README.md').is_file()")
        require_test(((
            root / "LG_project_docs" / "requirements" / "REQ-42" / "README.md"
        ).is_file()), "self-test invariant failed at original line 325: (root / 'LG_project_docs' / 'requirements' / 'REQ-42' / 'README.md').is_file()")
        require_test((not validate_project_document_layout(root)), 'self-test invariant failed at original line 328: not validate_project_document_layout(root)')
    return {"status": "Passed", "checks": 9}


def run_consumer_bootstrap_fixture() -> dict[str, object]:
    """A governed consumer bootstraps from the protected Skill publication only."""

    with tempfile.TemporaryDirectory(prefix="v63-consumer-bootstrap-") as temp:
        root = Path(temp)
        task_dir = new_task(root, "T-CONSUMER", 1)
        metadata_path, report_path, index_path = bootstrap_project_runtime(task_dir)
        require_test((read_json(metadata_path)["status"] == "Ready"), "self-test invariant failed at original line 339: read_json(metadata_path)['status'] == 'Ready'")
        require_test((report_path.is_file()), 'self-test invariant failed at original line 340: report_path.is_file()')
        require_test((index_path.is_file()), 'self-test invariant failed at original line 341: index_path.is_file()')
        require_test((not (
            root / ".project-governance" / "tasks" / "T-015"
        ).exists()), "self-test invariant failed at original line 342: not (root / '.project-governance' / 'tasks' / 'T-015').exists()")
    return {"status": "Passed", "checks": 4}


def run_minimal_carrier_fixture() -> dict[str, object]:
    evidence = [
        "evidence://risk-low",
        "evidence://reversible",
        "evidence://single-scope",
        "evidence://no-external-effect",
        "evidence://no-production",
        "evidence://no-security",
        "evidence://extensions-inactive",
    ]
    with tempfile.TemporaryDirectory(prefix="v63-minimal-carrier-") as temp:
        project_root = Path(temp)
        record_path = create_minimal_record(
            project_root,
            project_id="P-MIN",
            work_item_id="W-MIN",
            task_id="T-MIN-001",
            ordinal=1,
            depends_on=[],
            supersedes=[],
            objective="Update one local label.",
            scope="Change one label in src/label.txt.",
            acceptance="The focused test passes.",
            delivery_scenario="DS-03",
            development_type="DT-08",
            change_surface="UI/UX",
            selected_approach="Edit the existing label and run the focused test.",
            alternative_rejected="Keep the incorrect label unchanged.",
            plan_steps=["Edit one file.", "Run one focused test."],
            verification="Compare the label and run the focused test.",
            rollback="Restore the prior line.",
            allowed_paths=["src/label.txt"],
            out_of_scope=[],
            forbidden_actions=[],
            selection_source="automatic",
            basis=["All Minimal eligibility facts were inspected."],
            authority_refs=["conversation://fixture"],
            eligibility_evidence_refs=evidence,
            facts=["The current label is directly observable."],
            constraints=["Only src/label.txt is authorized."],
            assumptions=[],
            fundamentals=[
                "One observable value must change.",
                "The change is locally reversible.",
            ],
            causal_chain=[
                "Changing the sole value and testing it satisfies acceptance."
            ],
            decision_criteria=["The focused test passes."],
        )
        task_dir = record_path.parent
        require_test(
            not validate_minimal_record(read_json(record_path), task_dir=task_dir),
            "fresh Minimal carrier must validate",
        )
        append_minimal_event(
            task_dir,
            event_type="run_started",
            summary="Started the single reversible edit.",
            status="started",
            evidence_refs=["conversation://fixture"],
        )
        append_minimal_event(
            task_dir,
            event_type="mutation",
            summary="Changed the local label.",
            status="recorded",
            evidence_refs=["git://fixture"],
        )
        append_minimal_event(
            task_dir,
            event_type="verification",
            summary="Focused test passed.",
            status="succeeded",
            evidence_refs=["test://fixture"],
        )
        close_minimal_record(
            task_dir,
            status="Implemented",
            established_facts=["The label now matches expected text."],
            actual_changes=["Changed src/label.txt."],
            verification=["Passed::Focused test passed.::test://fixture"],
        )
        state = read_json(rebuild_project_state(project_root, "P-MIN"))
        require_test(
            state["source_tasks"][0].get("carrier_mode") == "Minimal",
            "ProjectState must index the Minimal carrier",
        )

    with tempfile.TemporaryDirectory(prefix="v63-minimal-upgrade-") as temp:
        project_root = Path(temp)
        record_path = create_minimal_record(
            project_root,
            project_id="P-UP",
            work_item_id="W-UP",
            task_id="T-UP-001",
            ordinal=1,
            depends_on=[],
            supersedes=[],
            objective="Update one local label.",
            scope="Change one label.",
            acceptance="The focused test passes.",
            delivery_scenario="DS-03",
            development_type="DT-08",
            change_surface="UI/UX",
            selected_approach="Edit one label.",
            alternative_rejected="Keep current text.",
            plan_steps=["Edit."],
            verification="Run focused test.",
            rollback="Restore line.",
            allowed_paths=["src/label.txt"],
            out_of_scope=[],
            forbidden_actions=[],
            selection_source="explicit-user",
            basis=["User requested Minimal and eligibility was verified."],
            authority_refs=["conversation://fixture"],
            eligibility_evidence_refs=evidence,
            facts=["The current label is observable."],
            constraints=["Only one file is initially authorized."],
            assumptions=[],
            fundamentals=["One value changes.", "The initial change is reversible."],
            causal_chain=["A focused edit satisfies the initial result."],
            decision_criteria=["The test passes."],
        )
        initialize_task(
            project_root,
            project_id="P-UP",
            work_item_id="W-UP",
            task_id="T-UP-001",
            ordinal=1,
            objective="Handle the expanded multi-file scope.",
            acceptance=["All expanded-scope tests pass."],
            development_types=["DT-07"],
            change_surfaces=["Architecture/Multi-repo"],
            in_scope=["Change multiple components after scope expansion."],
            allowed_paths=["src/**"],
            baseline_inheritance=["Revise"],
            upgrade_minimal_reason=(
                "Scope expanded beyond one independently acceptable scope."
            ),
            upgrade_minimal_basis="evidence://scope-expanded",
        )
        history = record_path.parent / "history" / "task-record.minimal-v1.json"
        require_test(
            history.is_file(),
            "Minimal upgrade must retain a read-only history carrier",
        )
        require_test(
            not record_path.exists(),
            "Minimal upgrade must remove the active Minimal carrier",
        )
        require_test(
            not validate_task_directory(record_path.parent),
            "upgraded default task package must validate",
        )
    return {"status": "Passed", "lifecycle": "single-file", "upgrade": "one-way"}


def new_task(root: Path, task_id: str, ordinal: int, *, project_id: str = "P-TEST", depends_on=()) -> Path:
    return initialize_task(
        root,
        project_id=project_id,
        work_item_id=f"W-{task_id}",
        task_id=task_id,
        ordinal=ordinal,
        objective=f"Conformance task {task_id}",
        acceptance=["All declared checks pass"],
        delivery_scenario="DS-03",
        development_types=["DT-06"],
        primary_development_type="DT-06",
        change_surfaces=["Agent/Collaboration", "Data/Schema"],
        baseline_inheritance=["New"],
        in_scope=["temporary test project"],
        out_of_scope=["external systems"],
        allowed_paths=[str(root)],
        forbidden_actions=["external mutation"],
        depends_on=depends_on,
        extension_triggers={"E01": "Inactive", "E02": "Inactive", "E03": "Active", "E04": "Inactive", "E05": "Inactive"},
        extension_evidence_refs={key: [] for key in ("E01", "E02", "E03", "E04", "E05")},
        applicability_facts=TEST_FACTS,
        tailoring_stage="S4",
        required_gates=["independent-review"],
        authority_references=["self-test://authority"],
        authority_assessments=[{
            "reference": "self-test://authority",
            "source_kind": "Policy",
            "status": "Valid",
            "scope_refs": ["temporary test project"],
            "evidence_refs": ["self-test://authority-evidence"],
            "verified_at": "2026-08-15T00:00:00Z",
            "expires_at": None,
        }],
        basis=["self-test"],
        source_snapshot={"kind": "self-test", "task": task_id},
    )


def resolve_project_root(skill_root: Path, explicit_root: str | None) -> Path:
    if explicit_root:
        project_root = Path(explicit_root).resolve()
        if not (project_root / ".project-governance").is_dir():
            raise GovernanceError(
                f"project root does not contain .project-governance: {project_root}"
            )
        return project_root

    working_root = Path.cwd().resolve()
    if (working_root / ".project-governance").is_dir():
        return working_root

    raise GovernanceError(
        "project root is not discoverable; run from a governed project root "
        "or pass --project-root <directory-containing-.project-governance>"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run positive and negative conformance tests for the Skill."
    )
    parser.add_argument(
        "--project-root",
        help="Governed project root that contains .project-governance.",
    )
    args = parser.parse_args(argv)
    skill_root = Path(__file__).resolve().parent.parent
    project_root = resolve_project_root(skill_root, args.project_root)
    require_test(({
        "SKILL.md", "agents", "scripts", "references", "assets"
    }.issubset({item.name for item in skill_root.iterdir()})), "self-test invariant failed at original line 421: {'SKILL.md', 'agents', 'scripts', 'references', 'assets'}.issubset({item.name for item in skill_root.iterdir()})")
    require_test((skill_root.name == "run-web-product-workflow"), "self-test invariant failed at original line 424: skill_root.name == 'run-web-product-workflow'")
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    skill_lines = skill_text.splitlines()
    require_test((len(skill_lines) < 500), 'self-test invariant failed at original line 427: len(skill_lines) < 500')
    require_test((skill_lines[0] == "---" and "---" in skill_lines[1:]), "self-test invariant failed at original line 428: skill_lines[0] == '---' and '---' in skill_lines[1:]")
    frontmatter_end = skill_lines[1:].index("---") + 1
    frontmatter_keys = {
        line.split(":", 1)[0].strip()
        for line in skill_lines[1:frontmatter_end]
        if ":" in line
    }
    require_test(({"name", "description"}.issubset(frontmatter_keys)), "self-test invariant failed at original line 435: {'name', 'description'}.issubset(frontmatter_keys)")
    reference_files = sorted(
        path.relative_to(skill_root).as_posix()
        for path in (skill_root / "references").rglob("*")
        if path.is_file()
    )
    required_reference_files = {
        "references/first-principles-method.md",
        "references/platform-bootstrap.md",
        "references/project-document-layout.md",
        "references/spec-source-map.md",
    }
    require_test((required_reference_files.issubset(reference_files)), 'self-test invariant failed at original line 447: required_reference_files.issubset(reference_files)')
    require_test((all(f"({relative})" in skill_text for relative in reference_files)), "self-test invariant failed at original line 448: all((f'({relative})' in skill_text for relative in reference_files))")
    require_test(("retrieval-plan.json" in skill_text), "self-test invariant failed at original line 449: 'retrieval-plan.json' in skill_text")
    require_test(("scripts/query_norm_context.py" in skill_text), "self-test invariant failed at original line 450: 'scripts/query_norm_context.py' in skill_text")
    require_test(("`Shadow`" in skill_text), "self-test invariant failed at original line 451: '`Shadow`' in skill_text")
    require_test(("`rg` 不是正常查询入口" in skill_text), "self-test invariant failed at original line 452: '`rg` 不是正常查询入口' in skill_text")
    source_map_text = (skill_root / "references" / "spec-source-map.md").read_text(encoding="utf-8")
    require_test(("Manifest 的45个受保护文件" in source_map_text), "self-test invariant failed at original line 454: 'Manifest 的45个受保护文件' in source_map_text")
    require_test(("retrieval-plan.json" in source_map_text), "self-test invariant failed at original line 455: 'retrieval-plan.json' in source_map_text")
    require_test((not (skill_root / "mappings").exists()), "self-test invariant failed at original line 456: not (skill_root / 'mappings').exists()")
    require_test((not (skill_root / "schemas").exists()), "self-test invariant failed at original line 457: not (skill_root / 'schemas').exists()")
    openai_yaml = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    short_match = re.search(r'^\s*short_description: "([^"]+)"$', openai_yaml, re.MULTILINE)
    prompt_match = re.search(r'^\s*default_prompt: "([^"]+)"$', openai_yaml, re.MULTILINE)
    require_test((short_match and 25 <= len(short_match.group(1)) <= 64), 'self-test invariant failed at original line 461: short_match and 25 <= len(short_match.group(1)) <= 64')
    require_test((prompt_match and "$run-web-product-workflow" in prompt_match.group(1)), "self-test invariant failed at original line 462: prompt_match and '$run-web-product-workflow' in prompt_match.group(1)")
    require_test((len(re.findall(r"[.!?。！？]", prompt_match.group(1))) == 1), "self-test invariant failed at original line 463: len(re.findall('[.!?。！？]', prompt_match.group(1))) == 1")
    require_test((not validate_embedded_manifest(skill_root)), 'self-test invariant failed at original line 464: not validate_embedded_manifest(skill_root)')
    manifest = read_json(embedded_manifest_path(skill_root))
    require_test((manifest["layout_version"] == "skill-runtime-v2"), "self-test invariant failed at original line 466: manifest['layout_version'] == 'skill-runtime-v2'")
    require_test((len(manifest["files"]) == 45), "self-test invariant failed at original line 467: len(manifest['files']) == 45")
    require_test(({item["role"] for item in manifest["files"]} == {
        "norm", "mapping", "schema", "skill-reference", "evaluation", "asset-template"
    }), "self-test invariant failed at original line 468: {item['role'] for item in manifest['files']} == {'norm', 'mapping', 'schema', 'skill-reference', 'evaluation', 'asset-template'}")
    retrieval_validation = validate_contracts(
        project_root,
        verify_project_snapshots=False,
    )
    mandatory_locations: set[tuple[str, int, int]] = set()
    mandatory_texts: set[str] = set()
    claim_mandatory_target_identity(
        target_id="TARGET-ORIGINAL",
        logical_path="references/C09.md",
        line_start=10,
        line_end=10,
        text_sha256="a" * 64,
        locations=mandatory_locations,
        text_identities=mandatory_texts,
    )
    expect_governance_error(
        "duplicate mandatory target location",
        lambda: claim_mandatory_target_identity(
            target_id="TARGET-DUPLICATE-LOCATION",
            logical_path="references/C09.md",
            line_start=10,
            line_end=10,
            text_sha256="b" * 64,
            locations=mandatory_locations,
            text_identities=mandatory_texts,
        ),
    )
    expect_governance_error(
        "duplicate mandatory target text identity",
        lambda: claim_mandatory_target_identity(
            target_id="TARGET-DUPLICATE-TEXT",
            logical_path="references/C12.md",
            line_start=20,
            line_end=20,
            text_sha256="a" * 64,
            locations=mandatory_locations,
            text_identities=mandatory_texts,
        ),
    )
    parser_validation = run_parser_fixtures()
    lifecycle_validation = run_lock_lifecycle_fixtures()
    query_planner_validation = run_query_planner_fixtures()
    active_query_tree_validation = run_active_query_tree_fixtures()
    derived_view_byte_validation = run_derived_view_byte_fixture()
    new_query_history_validation = run_new_query_history_fixture()
    document_governance_validation = run_document_governance_fixture()
    consumer_bootstrap_validation = run_consumer_bootstrap_fixture()
    minimal_carrier_validation = run_minimal_carrier_fixture()
    require_test((retrieval_validation["manifest_files"] == 45), "self-test invariant failed at original line 518: retrieval_validation['manifest_files'] == 45")
    require_test((retrieval_validation["fixture_counts"] == {
        "positive": 8,
        "schema_negative": 21,
        "semantic_negative": 13,
    }), "self-test invariant failed at original line 519: retrieval_validation['fixture_counts'] == {'positive': 8, 'schema_negative': 21, 'semantic_negative': 13}")
    require_test((retrieval_validation["gold_case_count"] == 28), "self-test invariant failed at original line 524: retrieval_validation['gold_case_count'] == 28")
    require_test((retrieval_validation["mandatory_target_count"] == 12), "self-test invariant failed at original line 525: retrieval_validation['mandatory_target_count'] == 12")
    require_test((retrieval_validation["hard_gate_negative_count"] == 8), "self-test invariant failed at original line 526: retrieval_validation['hard_gate_negative_count'] == 8")
    require_test((retrieval_validation["compatibility"]["cli_contract_count"] == 15), "CLI compatibility closure must contain 15 public scripts")
    require_test((retrieval_validation["requirement_coverage"] == 41), "self-test invariant failed at original line 528: retrieval_validation['requirement_coverage'] == 41")
    require_test((retrieval_validation["acceptance_coverage"] == 25), "self-test invariant failed at original line 529: retrieval_validation['acceptance_coverage'] == 25")
    require_test((retrieval_validation["verification_mode"] == "protected-runtime"), "self-test invariant failed at original line 530: retrieval_validation['verification_mode'] == 'protected-runtime'")
    require_test((retrieval_validation["skipped_structural_checks"] == [
        "legacy-source-pack-regression"
    ]), "self-test invariant failed at original line 531: retrieval_validation['skipped_structural_checks'] == ['legacy-source-pack-regression']")
    require_test((parser_validation["status"] == "Passed"), "self-test invariant failed at original line 534: parser_validation['status'] == 'Passed'")
    require_test((lifecycle_validation["status"] == "Passed"), "self-test invariant failed at original line 535: lifecycle_validation['status'] == 'Passed'")
    require_test((query_planner_validation["status"] == "Passed"), "self-test invariant failed at original line 536: query_planner_validation['status'] == 'Passed'")
    require_test((query_planner_validation["lexical_boundary_cases"] == 6), "self-test invariant failed at original line 537: query_planner_validation['lexical_boundary_cases'] == 6")
    require_test((query_planner_validation["semantic_default"] == "disabled"), "self-test invariant failed at original line 538: query_planner_validation['semantic_default'] == 'disabled'")
    require_test((active_query_tree_validation["status"] == "Passed"), "self-test invariant failed at original line 539: active_query_tree_validation['status'] == 'Passed'")
    require_test((active_query_tree_validation["checks"] == 10), "self-test invariant failed at original line 540: active_query_tree_validation['checks'] == 10")
    require_test((active_query_tree_validation["link_checks"] in {0, 2}), "self-test invariant failed at original line 541: active_query_tree_validation['link_checks'] in {0, 2}")
    require_test((derived_view_byte_validation == {"status": "Passed", "checks": 2}), "self-test invariant failed at original line 542: derived_view_byte_validation == {'status': 'Passed', 'checks': 2}")
    require_test((new_query_history_validation == {"status": "Passed", "checks": 2}), "self-test invariant failed at original line 543: new_query_history_validation == {'status': 'Passed', 'checks': 2}")
    require_test((document_governance_validation == {"status": "Passed", "checks": 9}), "self-test invariant failed at original line 544: document_governance_validation == {'status': 'Passed', 'checks': 9}")
    require_test((consumer_bootstrap_validation == {"status": "Passed", "checks": 4}), "self-test invariant failed at original line 545: consumer_bootstrap_validation == {'status': 'Passed', 'checks': 4}")
    require_test(
        minimal_carrier_validation
        == {"status": "Passed", "lifecycle": "single-file", "upgrade": "one-way"},
        "Minimal aggregate lifecycle and one-way upgrade must pass",
    )
    expect_governance_error(
        "unknown logical runtime path",
        lambda: runtime_asset_path("references/unknown-source.md"),
    )
    index = default_profile_index_path()
    profiles = resolve_all_profiles(index)
    require_test((len(profiles) == 137), 'self-test invariant failed at original line 552: len(profiles) == 137')
    require_test(({item["meta_type"] for item in profiles} == {
        "AuthorityAsset", "DerivedView", "TaskContract", "RunLedger", "TaskOutcome"
    }), "self-test invariant failed at original line 553: {item['meta_type'] for item in profiles} == {'AuthorityAsset', 'DerivedView', 'TaskContract', 'RunLedger', 'TaskOutcome'}")
    tailoring_map = load_tailoring_map()
    require_test((len(tailoring_map["source_catalog"]) == 22), "self-test invariant failed at original line 557: len(tailoring_map['source_catalog']) == 22")
    require_test((len(tailoring_map["standards"]) == 17), "self-test invariant failed at original line 558: len(tailoring_map['standards']) == 17")
    require_test((len(tailoring_map["applicability_facts"]) == 17), "self-test invariant failed at original line 559: len(tailoring_map['applicability_facts']) == 17")
    require_test((sum(item["profile_count"] for item in tailoring_map["standards"].values()) == 137), "self-test invariant failed at original line 560: sum((item['profile_count'] for item in tailoring_map['standards'].values())) == 137")
    union_profile = {
        "delivery_scenario": "DS-03",
        "development_types": ["DT-04", "DT-05"],
        "primary_development_type": "DT-04",
        "development_type_scopes": {"DT-04": ["clarification-only text"], "DT-05": ["normative behavior revision"]},
        "change_surfaces": ["Data/Schema", "Agent/Collaboration"],
        "risk_level": "High",
        "extension_triggers": {"E01": "Inactive", "E02": "Inactive", "E03": "Active", "E04": "Inactive", "E05": "Inactive"},
        "extension_evidence_refs": {key: [] for key in ("E01", "E02", "E03", "E04", "E05")},
        "baseline_inheritance": ["Revise"],
        "mode": "Normal",
        "confidence": "High",
        "basis": ["self-test"],
        "open_questions": [],
        "applicability_facts": TEST_FACTS,
    }
    union_resolution = resolve_tailoring(union_profile, stage="S4")
    require_test(({"C07", "C08", "C09", "E03"} <= set(union_resolution["applicable_standards"])), "self-test invariant failed at original line 578: {'C07', 'C08', 'C09', 'E03'} <= set(union_resolution['applicable_standards'])")
    require_test((not union_resolution["blocking_reasons"]), "self-test invariant failed at original line 579: not union_resolution['blocking_reasons']")
    overlap_profile = copy.deepcopy(union_profile)
    overlap_profile["development_type_scopes"] = {"DT-04": ["same scope"], "DT-05": ["same scope"]}
    overlap_resolution = resolve_tailoring(overlap_profile, stage="S4")
    require_test((any("semantic-conflict development types" in item for item in overlap_resolution["blocking_reasons"])), "self-test invariant failed at original line 583: any(('semantic-conflict development types' in item for item in overlap_resolution['blocking_reasons']))")
    inconsistent_profile = copy.deepcopy(union_profile)
    inconsistent_profile["applicability_facts"]["architecture_impact"] = "Yes"
    inconsistent_profile["extension_triggers"]["E01"] = "Active"
    inconsistent_resolution = resolve_tailoring(inconsistent_profile, stage="S4")
    require_test((any("architecture_impact=Yes requires" in item for item in inconsistent_resolution["blocking_reasons"])), "self-test invariant failed at original line 588: any(('architecture_impact=Yes requires' in item for item in inconsistent_resolution['blocking_reasons']))")
    conflict_profile = copy.deepcopy(union_profile)
    conflict_profile["extension_triggers"]["E03"] = "Inactive"
    conflict_profile["applicability_facts"]["data_ai_impact"] = "Unknown"
    conflict_resolution = resolve_tailoring(conflict_profile, stage="S4")
    require_test((conflict_resolution["blocking_reasons"]), "self-test invariant failed at original line 593: conflict_resolution['blocking_reasons']")
    pending_profile = copy.deepcopy(union_profile)
    pending_profile["extension_triggers"]["E01"] = "Pending"
    pending_resolution = resolve_tailoring(pending_profile, stage="S1")
    require_test(("E01" in pending_resolution["pending_standards"]), "self-test invariant failed at original line 597: 'E01' in pending_resolution['pending_standards']")
    require_test(("E01" in {item["source_id"] for item in pending_resolution["complete_source_files"]}), "self-test invariant failed at original line 598: 'E01' in {item['source_id'] for item in pending_resolution['complete_source_files']}")
    retired_profile = copy.deepcopy(union_profile)
    retired_profile["extension_triggers"]["E01"] = "Retired"
    retired_resolution = resolve_tailoring(retired_profile, stage="S4")
    require_test((any("E01=Retired requires extension_evidence_refs" in item for item in retired_resolution["blocking_reasons"])), "self-test invariant failed at original line 602: any(('E01=Retired requires extension_evidence_refs' in item for item in retired_resolution['blocking_reasons']))")
    gate_resolution = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative gate test",
            "scope": {},
            "authority": {"authority_references": [], "authority_assessments": [], "required_gates": []},
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("authority_available=Yes" in item for item in gate_resolution["blocking_reasons"])), "self-test invariant failed at original line 614: any(('authority_available=Yes' in item for item in gate_resolution['blocking_reasons']))")
    require_test((any("independent-review" in item for item in gate_resolution["blocking_reasons"])), "self-test invariant failed at original line 615: any(('independent-review' in item for item in gate_resolution['blocking_reasons']))")
    placeholder_authority = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative placeholder authority test",
            "scope": {"in_scope": ["normative behavior revision"]},
            "authority": {
                "authority_references": ["placeholder://unverified"],
                "authority_assessments": [],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("lack structured assessments" in item for item in placeholder_authority["blocking_reasons"])), "self-test invariant failed at original line 631: any(('lack structured assessments' in item for item in placeholder_authority['blocking_reasons']))")
    expired_authority = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative expired authority test",
            "scope": {"in_scope": ["normative behavior revision"]},
            "authority": {
                "authority_references": ["self-test://expired"],
                "authority_assessments": [{
                    "reference": "self-test://expired", "source_kind": "Policy", "status": "Valid",
                    "scope_refs": ["normative behavior revision"], "evidence_refs": ["self-test://expired-evidence"],
                    "verified_at": "2020-01-01T00:00:00Z", "expires_at": "2020-01-02T00:00:00Z",
                }],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("authority assessment expired" in item for item in expired_authority["blocking_reasons"])), "self-test invariant failed at original line 651: any(('authority assessment expired' in item for item in expired_authority['blocking_reasons']))")
    incomplete_authority_scope = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative authority scope test",
            "scope": {"in_scope": ["clarification-only text", "normative behavior revision"]},
            "authority": {
                "authority_references": ["self-test://partial"],
                "authority_assessments": [{
                    "reference": "self-test://partial", "source_kind": "Policy", "status": "Valid",
                    "scope_refs": ["clarification-only text", "invented scope"],
                    "evidence_refs": ["self-test://partial-evidence"],
                    "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
                }],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("scope_refs must reference exact" in item for item in incomplete_authority_scope["blocking_reasons"])), "self-test invariant failed at original line 672: any(('scope_refs must reference exact' in item for item in incomplete_authority_scope['blocking_reasons']))")
    require_test((any("do not cover scope.in_scope" in item for item in incomplete_authority_scope["blocking_reasons"])), "self-test invariant failed at original line 673: any(('do not cover scope.in_scope' in item for item in incomplete_authority_scope['blocking_reasons']))")
    mixed_authority_states = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative mixed authority state test",
            "scope": {"in_scope": ["normative behavior revision"]},
            "authority": {
                "authority_references": ["self-test://valid", "self-test://pending"],
                "authority_assessments": [
                    {
                        "reference": "self-test://valid", "source_kind": "Policy", "status": "Valid",
                        "scope_refs": ["normative behavior revision"], "evidence_refs": ["self-test://valid-evidence"],
                        "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
                    },
                    {
                        "reference": "self-test://pending", "source_kind": "Policy", "status": "Pending",
                        "scope_refs": ["normative behavior revision"], "evidence_refs": ["self-test://pending-evidence"],
                        "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
                    },
                ],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("authority assessment is not Valid" in item for item in mixed_authority_states["blocking_reasons"])), "self-test invariant failed at original line 700: any(('authority assessment is not Valid' in item for item in mixed_authority_states['blocking_reasons']))")
    external_effect_profile = copy.deepcopy(union_profile)
    external_effect_profile["applicability_facts"]["external_system_effect"] = "Yes"
    missing_external_permission = resolve_tailoring(
        external_effect_profile,
        stage="S4",
        contract_context={
            "objective": "negative execution permission test",
            "scope": {"in_scope": ["normative behavior revision"]},
            "authority": {
                "execution_permissions": ["read", "edit-in-scope", "validate"],
                "authority_references": ["self-test://valid"],
                "authority_assessments": [{
                    "reference": "self-test://valid", "source_kind": "Policy", "status": "Valid",
                    "scope_refs": ["normative behavior revision"], "evidence_refs": ["self-test://valid-evidence"],
                    "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
                }],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("external-effect" in item for item in missing_external_permission["blocking_reasons"])), "self-test invariant failed at original line 723: any(('external-effect' in item for item in missing_external_permission['blocking_reasons']))")
    future_authority = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative future authority assessment test",
            "scope": {"in_scope": ["normative behavior revision"]},
            "authority": {
                "execution_permissions": ["read", "edit-in-scope", "validate"],
                "authority_references": ["self-test://future"],
                "authority_assessments": [{
                    "reference": "self-test://future", "source_kind": "Policy", "status": "Valid",
                    "scope_refs": ["normative behavior revision"], "evidence_refs": ["self-test://future-evidence"],
                    "verified_at": "2999-01-01T00:00:00Z", "expires_at": None,
                }],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
        },
    )
    require_test((any("verified_at is in the future" in item for item in future_authority["blocking_reasons"])), "self-test invariant failed at original line 744: any(('verified_at is in the future' in item for item in future_authority['blocking_reasons']))")
    low_confidence_profile = copy.deepcopy(union_profile)
    low_confidence_profile["confidence"] = "Low"
    low_confidence_resolution = resolve_tailoring(low_confidence_profile, stage="S4")
    require_test((any("confidence=Low" in item for item in low_confidence_resolution["blocking_reasons"])), "self-test invariant failed at original line 748: any(('confidence=Low' in item for item in low_confidence_resolution['blocking_reasons']))")
    dependency_resolution = resolve_tailoring(
        union_profile,
        stage="S4",
        contract_context={
            "objective": "negative dependency test",
            "scope": {"in_scope": ["dependency scope"]},
            "authority": {
                "authority_references": ["self-test://authority"],
                "authority_assessments": [{
                    "reference": "self-test://authority", "source_kind": "Policy", "status": "Valid",
                    "scope_refs": ["dependency scope"], "evidence_refs": ["self-test://authority-evidence"],
                    "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
                }],
                "required_gates": ["independent-review"],
            },
            "acceptance": {},
            "source_snapshot": {},
            "blocked_by": ["T-BLOCKER"],
        },
    )
    require_test((any("task is blocked_by" in item for item in dependency_resolution["blocking_reasons"])), "self-test invariant failed at original line 769: any(('task is blocked_by' in item for item in dependency_resolution['blocking_reasons']))")

    with tempfile.TemporaryDirectory(prefix="v63-governance-") as temp:
        root = Path(temp)
        task_dir = new_task(root, "T-001", 1)
        arbitrary_cwd = root / "nested" / "working-directory"
        arbitrary_cwd.mkdir(parents=True)
        compile_result = subprocess.run(
            [
                sys.executable, "-B", "-X", "utf8",
                str(Path(__file__).resolve().parent / "compile_norm_context.py"),
                "--task-dir", str(task_dir), "--stage", "S4", "--enforce",
            ],
            cwd=arbitrary_cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        require_test((compile_result.returncode == 0), (compile_result.stdout + compile_result.stderr))
        compiled_before = read_json(task_dir / "before.json")
        context_dir = task_dir.parents[1] / "generated" / "contexts" / "T-001" / "S4"
        source_pack = context_dir / "norm-source-pack.md"
        retrieval_plan = context_dir / "retrieval-plan.json"
        require_test((retrieval_plan.is_file() and retrieval_plan.with_suffix(".json.view.json").is_file()), "self-test invariant failed at original line 793: retrieval_plan.is_file() and retrieval_plan.with_suffix('.json.view.json').is_file()")
        require_test((not validate_retrieval_plan(task_dir)), 'self-test invariant failed at original line 794: not validate_retrieval_plan(task_dir)')
        plan = read_json(retrieval_plan)
        require_test((plan["activation"] == {
            "mode": "Shadow", "release_authorized": False, "remote_semantic_enabled": False
        }), "self-test invariant failed at original line 796: plan['activation'] == {'mode': 'Shadow', 'release_authorized': False, 'remote_semantic_enabled': False}")
        require_test((plan["required_agent_inputs"] == ["action", "query_text"]), "self-test invariant failed at original line 799: plan['required_agent_inputs'] == ['action', 'query_text']")
        require_test((plan["request_template"]["modes"] == ["exact", "fts"]), "self-test invariant failed at original line 800: plan['request_template']['modes'] == ['exact', 'fts']")
        require_test((plan["source_pack_retained"] is True), "self-test invariant failed at original line 801: plan['source_pack_retained'] is True")
        packet_markdown = context_dir / "norm-packet.md"
        original_packet_markdown = packet_markdown.read_text(encoding="utf-8")
        packet_markdown.write_text(
            original_packet_markdown + "tamper\n", encoding="utf-8", newline="\n"
        )
        require_test((any("norm-packet-markdown" in item or "envelope is stale" in item for item in validate_retrieval_plan(task_dir))), "self-test invariant failed at original line 807: any(('norm-packet-markdown' in item or 'envelope is stale' in item for item in validate_retrieval_plan(task_dir)))")
        packet_markdown.write_text(original_packet_markdown, encoding="utf-8", newline="\n")
        original_plan_text = retrieval_plan.read_text(encoding="utf-8")
        tampered_plan = read_json(retrieval_plan)
        tampered_plan["activation"]["release_authorized"] = True
        retrieval_plan.write_text(
            json.dumps(tampered_plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        require_test((any("activation" in item for item in validate_retrieval_plan(task_dir))), "self-test invariant failed at original line 817: any(('activation' in item for item in validate_retrieval_plan(task_dir)))")
        retrieval_plan.write_text(original_plan_text, encoding="utf-8", newline="\n")
        require_test((not validate_retrieval_plan(task_dir)), 'self-test invariant failed at original line 819: not validate_retrieval_plan(task_dir)')
        source_pack_text = source_pack.read_text(encoding="utf-8")
        for source in compiled_before["tailoring_resolution"]["complete_source_files"]:
            require_test((f"SOURCE-BEGIN {source['source_id']} sha256={source['sha256']}" in source_pack_text), "self-test invariant failed at original line 822: f'SOURCE-BEGIN {source['source_id']} sha256={source['sha256']}' in source_pack_text")
            require_test((runtime_asset_path(source["path"]).read_text(encoding="utf-8").rstrip() in source_pack_text), "self-test invariant failed at original line 823: runtime_asset_path(source['path']).read_text(encoding='utf-8').rstrip() in source_pack_text")
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-001", event_type="run_started", summary="Started isolated self-test run", status="started")
        require_test((not validate_retrieval_plan(task_dir)), 'self-test invariant failed at original line 825: not validate_retrieval_plan(task_dir)')
        amend_record(
            task_dir / "before.json",
            dotted_path="scope.in_scope",
            new_value=["temporary test project", "generated views"],
            reason="exercise amendment history",
            basis="self-test",
        )
        amend_record(
            task_dir / "before.json",
            dotted_path="authority.authority_assessments",
            new_value=[{
                "reference": "self-test://authority", "source_kind": "Policy", "status": "Valid",
                "scope_refs": ["temporary test project", "generated views"],
                "evidence_refs": ["self-test://authority-evidence"],
                "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
            }],
            reason="extend authority assessment to amended scope",
            basis="self-test",
        )
        require_test((validate_retrieval_plan(task_dir)), ("material TaskContract amendment must stale the plan"))
        compile_result = subprocess.run(
            [
                sys.executable, "-B", "-X", "utf8",
                str(Path(__file__).resolve().parent / "compile_norm_context.py"),
                "--task-dir", str(task_dir), "--stage", "S4", "--enforce",
            ],
            cwd=arbitrary_cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        require_test((compile_result.returncode == 0), (compile_result.stdout + compile_result.stderr))
        require_test((not validate_retrieval_plan(task_dir)), 'self-test invariant failed at original line 859: not validate_retrieval_plan(task_dir)')
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-001", event_type="failure", summary="Recorded a synthetic recoverable failure", status="failed", exit_code=1, evidence_refs=["self-test://failure"])
        expect_governance_error(
            "retry must use a new attempt",
            lambda: append_run_event(task_dir, run_id="RUN-001", attempt_id="A-001", event_type="retry", summary="Invalid retry", status="started"),
        )
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="retry", summary="Retried with a new attempt", status="started")
        expect_governance_error(
            "run id cannot change",
            lambda: append_run_event(task_dir, run_id="RUN-OTHER", attempt_id="A-002", event_type="mutation", summary="Invalid run", status="succeeded"),
        )
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="verification", summary="Validated generated JSON and task relationships", status="succeeded", exit_code=0, evidence_refs=["self-test://validation"])
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="run_finished", summary="Finished isolated self-test run", status="succeeded")
        expect_governance_error(
            "late event after run_finished",
            lambda: append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="mutation", summary="Too late", status="succeeded"),
        )
        close_task(
            task_dir,
            status="Implemented",
            established_facts=["V6.3 task lifecycle completed"],
            actual_changes=["Created isolated governance artifacts"],
            verification=[{"summary": "Task directory validation passed", "result": "Passed", "evidence_refs": ["self-test://validation"], "required": True}],
            legacy_issues=[{"summary": "Synthetic failure remains visible", "reason": "audit fixture", "impact": "none outside temporary data", "owner": "self-test", "reentry_condition": "not applicable"}],
            evidence_refs=["self-test://validation"],
            source_snapshot={"kind": "self-test-result"},
        )
        expect_governance_error(
            "event after TaskOutcome",
            lambda: append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="mutation", summary="Too late", status="succeeded"),
        )
        amend_record(
            task_dir / "after.json",
            dotted_path="actual_changes",
            new_value=["Created isolated governance artifacts", "Recorded terminal amendment history"],
            reason="exercise terminal correction",
            basis="self-test",
        )
        expect_governance_error(
            "amendment history cannot be rewritten",
            lambda: amend_record(task_dir / "after.json", dotted_path="amendments", new_value=[], reason="invalid", basis="self-test"),
        )
        (root / "requirements.md").write_text("# Requirement\n", encoding="utf-8")
        register_authority_asset(
            root,
            project_id="P-TEST",
            asset_id="PRD-TEST-001",
            legacy_kind="PRD",
            title="Self-test product requirement",
            owner="self-test",
            state="Draft",
            revision="0.1",
            content_ref="requirements.md",
            source=["T-001"],
            scope=["temporary test project"],
            trace_refs=["T-001"],
            profile_fields={"purpose": "exercise native asset registration"},
        )
        expect_governance_error(
            "invalid profile state",
            lambda: register_authority_asset(root, project_id="P-TEST", asset_id="PRD-BAD-STATE", legacy_kind="PRD", title="Bad", owner="self-test", state="Completed", revision="0.1", content_ref="requirements.md", source=["T-001"], scope=["test"], profile_fields={"purpose": "negative"}),
        )
        expect_governance_error(
            "missing local authority source",
            lambda: register_authority_asset(root, project_id="P-TEST", asset_id="PRD-BAD-REF", legacy_kind="PRD", title="Bad", owner="self-test", state="Draft", revision="0.1", content_ref="missing.md", source=["T-001"], scope=["test"], profile_fields={"purpose": "negative"}),
        )
        state = read_json(rebuild_project_state(root, "P-TEST"))
        require_test((len(state["source_tasks"]) == 1 and len(state["authority_assets"]) == 1), "self-test invariant failed at original line 926: len(state['source_tasks']) == 1 and len(state['authority_assets']) == 1")
        outputs = generate_views(root, project_id="P-TEST", profile_index=index)
        require_test((len(outputs) == 6 and all(path.is_file() for path in outputs)), 'self-test invariant failed at original line 928: len(outputs) == 6 and all((path.is_file() for path in outputs))')
        terminal_manifest = read_json(task_dir / "after.json")["artifact_manifest"] + [
            {
                "meta_type": "ProjectState",
                "legacy_kind": None,
                "action": "Generate",
                "asset_id": "P-TEST-state",
                "content_ref": ".project-governance/project-state.json",
                "reason": "rebuild cross-task current state",
                "rule_reference": "VC-PPG-PRO-001 §8.4",
                "owner": "execution-agent",
                "source_snapshot": "self-test-result",
                "human_confirmation_refs": [],
                "outcome": "Generated",
            },
            {
                "meta_type": "DerivedView",
                "legacy_kind": None,
                "action": "Generate",
                "asset_id": "P-TEST-review-views",
                "content_ref": ".project-governance/generated/reviews/project-status.md",
                "reason": "generate human review views",
                "rule_reference": "VC-PPG-PRO-001 §8.6",
                "owner": "execution-agent",
                "source_snapshot": "self-test-result",
                "human_confirmation_refs": [],
                "outcome": "Generated",
            },
        ]
        amend_record(
            task_dir / "after.json",
            dotted_path="artifact_manifest",
            new_value=terminal_manifest,
            reason="register actual close-out outputs",
            basis="self-test",
        )
        expect_governance_error(
            "terminal manifest cannot remove a frozen planned asset",
            lambda: amend_record(
                task_dir / "after.json",
                dotted_path="artifact_manifest",
                new_value=terminal_manifest[1:],
                reason="invalid removal",
                basis="self-test",
            ),
        )
        state = read_json(rebuild_project_state(root, "P-TEST"))
        require_test((state["source_tasks"][0]["revision"] == 3), "self-test invariant failed at original line 975: state['source_tasks'][0]['revision'] == 3")
        outputs = generate_views(root, project_id="P-TEST", profile_index=index)
        for envelope in [path for path in outputs if path.name.endswith(".view.json")]:
            require_test((not validate_json_document(read_json(envelope), "derived-view.schema.json", str(envelope))), "self-test invariant failed at original line 978: not validate_json_document(read_json(envelope), 'derived-view.schema.json', str(envelope))")
        require_test((not validate_task_directory(task_dir)), 'self-test invariant failed at original line 979: not validate_task_directory(task_dir)')

        historical_before_path = task_dir / "before.json"
        historical_before = read_json(historical_before_path)
        historical_before["tailoring_resolution"]["complete_source_files"][0]["sha256"] = "0" * 64
        historical_before_path.write_text(
            json.dumps(historical_before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        require_test((not validate_task_directory(task_dir)), 'self-test invariant failed at original line 987: not validate_task_directory(task_dir)')
        rebuild_project_state(root, "P-TEST")
        historical_before["tailoring_resolution"]["complete_source_files"][0]["path"] = "references/legacy/V6.2-source.md"
        historical_before_path.write_text(
            json.dumps(historical_before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        require_test(
            not validate_task_directory(task_dir),
            "a terminal task must preserve a safe historical source identity even when the current Manifest no longer publishes that path",
        )
        rebuild_project_state(root, "P-TEST")
        historical_before["tailoring_resolution"]["complete_source_files"][0]["path"] = "../unsafe-source.md"
        historical_before_path.write_text(
            json.dumps(historical_before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        require_test(
            any("safe canonical references/ path" in item for item in validate_task_directory(task_dir)),
            "a terminal historical source identity must reject traversal or non-canonical paths",
        )
        historical_before["tailoring_resolution"]["complete_source_files"][0]["path"] = compiled_before["tailoring_resolution"]["complete_source_files"][0]["path"]
        historical_before_path.write_text(
            json.dumps(historical_before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        require_test((not validate_task_directory(task_dir)), 'self-test invariant failed at original line 998: not validate_task_directory(task_dir)')

        broken = read_json(task_dir / "before.json")
        del broken["objective"]
        require_test((any("objective" in error for error in validate_json_document(broken, "task-before.schema.json", "negative"))), "self-test invariant failed at original line 1002: any(('objective' in error for error in validate_json_document(broken, 'task-before.schema.json', 'negative')))")
        original_before = (task_dir / "before.json").read_text(encoding="utf-8")
        (task_dir / "before.json").write_text(json.dumps(broken, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require_test((any("objective" in error for error in validate_task_directory(task_dir))), "self-test invariant failed at original line 1005: any(('objective' in error for error in validate_task_directory(task_dir)))")
        (task_dir / "before.json").write_text(original_before, encoding="utf-8")
        broken_after = read_json(task_dir / "after.json")
        del broken_after["artifact_manifest"]
        require_test((any("artifact_manifest" in error for error in validate_json_document(broken_after, "task-after.schema.json", "negative"))), "self-test invariant failed at original line 1009: any(('artifact_manifest' in error for error in validate_json_document(broken_after, 'task-after.schema.json', 'negative')))")

    with tempfile.TemporaryDirectory(prefix="v63-no-run-") as temp:
        no_run = new_task(Path(temp), "T-001", 1)
        expect_governance_error(
            "Implemented cannot close without a run",
            lambda: close_task(no_run, status="Implemented", established_facts=[], actual_changes=["changed"], verification=[{"summary": "claimed", "result": "Passed", "evidence_refs": []}], source_snapshot={"kind": "negative"}),
        )
        amend_record(
            no_run / "before.json",
            dotted_path="legacy_run_policy",
            new_value={"policy_version": "pre-v6.3-enforcement", "rationale": "negative test", "affected_sequences": [1], "evidence_refs": ["self-test://negative"]},
            reason="exercise anti-bypass rule",
            basis="self-test",
            allow_add=True,
        )
        expect_governance_error(
            "new tasks cannot claim legacy run policy",
            lambda: append_run_event(no_run, run_id="RUN-001", attempt_id="A-001", event_type="run_started", summary="Invalid legacy bypass", status="started"),
        )

    with tempfile.TemporaryDirectory(prefix="v63-retrieval-plan-required-") as temp:
        uncompiled_task = new_task(Path(temp), "T-001", 1)
        readiness = subprocess.run(
            [
                sys.executable, "-B", "-X", "utf8",
                str(Path(__file__).resolve().parent / "validate_task_package.py"),
                str(uncompiled_task), "--execution-ready",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        require_test((readiness.returncode == 1), 'self-test invariant failed at original line 1043: readiness.returncode == 1')
        require_test(("missing retrieval plan" in readiness.stderr), "self-test invariant failed at original line 1044: 'missing retrieval plan' in readiness.stderr")

    with tempfile.TemporaryDirectory(prefix="v63-stale-context-compiler-") as temp:
        stale_task = new_task(Path(temp), "T-001", 1)
        stale_before_path = stale_task / "before.json"
        stale_before = read_json(stale_before_path)
        stale_before["objective"] = "Unamended input drift"
        stale_before_path.write_text(json.dumps(stale_before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        stale_compile = subprocess.run(
            [
                sys.executable, "-B", "-X", "utf8",
                str(Path(__file__).resolve().parent / "compile_norm_context.py"),
                "--task-dir", str(stale_task), "--stage", "S4", "--enforce",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        require_test((stale_compile.returncode == 3), 'self-test invariant failed at original line 1063: stale_compile.returncode == 3')
        require_test(("stored tailoring_resolution is stale" in stale_compile.stdout), "self-test invariant failed at original line 1064: 'stored tailoring_resolution is stale' in stale_compile.stdout")

    with tempfile.TemporaryDirectory(prefix="v63-profile-values-") as temp:
        expect_governance_error(
            "uncontrolled change surface",
            lambda: initialize_task(
                Path(temp),
                project_id="P-TEST",
                work_item_id="W-T-001",
                task_id="T-001",
                ordinal=1,
                objective="Reject aliases outside the controlled vocabulary",
                acceptance=["Alias is rejected"],
                delivery_scenario="DS-03",
                development_types=["DT-07"],
                change_surfaces=["automation"],
            ),
        )

    with tempfile.TemporaryDirectory(prefix="v63-retry-order-") as temp:
        retry_task = new_task(Path(temp), "T-001", 1)
        append_run_event(retry_task, run_id="RUN-001", attempt_id="A-001", event_type="run_started", summary="Start retry ordering test", status="started")
        append_run_event(retry_task, run_id="RUN-001", attempt_id="A-001", event_type="verification", summary="Verification exposed a defect", status="failed")
        expect_governance_error(
            "retry requires an explicit failure event",
            lambda: append_run_event(retry_task, run_id="RUN-001", attempt_id="A-002", event_type="retry", summary="Invalid retry before failure event", status="started"),
        )
        append_run_event(retry_task, run_id="RUN-001", attempt_id="A-001", event_type="failure", summary="Record the defect on the current attempt", status="failed")
        append_run_event(retry_task, run_id="RUN-001", attempt_id="A-002", event_type="retry", summary="Valid retry after explicit failure", status="started")

    with tempfile.TemporaryDirectory(prefix="v63-permission-enforcement-") as temp:
        read_only_task = new_task(Path(temp), "T-001", 1)
        amend_record(
            read_only_task / "before.json",
            dotted_path="authority.execution_permissions",
            new_value=["read"],
            reason="exercise event permission enforcement",
            basis="negative self-test",
        )
        append_run_event(read_only_task, run_id="RUN-001", attempt_id="A-001", event_type="run_started", summary="Start read-only run", status="started")
        expect_governance_error(
            "mutation requires edit-in-scope permission",
            lambda: append_run_event(read_only_task, run_id="RUN-001", attempt_id="A-001", event_type="mutation", summary="Must reject unauthorized mutation", status="succeeded"),
        )

    with tempfile.TemporaryDirectory(prefix="v63-midrun-tailoring-") as temp:
        blocked_task = new_task(Path(temp), "T-001", 1)
        append_run_event(blocked_task, run_id="RUN-001", attempt_id="A-001", event_type="run_started", summary="Start fail-closed test", status="started")
        amend_record(
            blocked_task / "before.json",
            dotted_path="task_profile.applicability_facts.data_ai_impact",
            new_value="Unknown",
            reason="introduce a newly discovered unknown",
            basis="negative self-test",
        )
        expect_governance_error(
            "mid-run blocker prevents mutation",
            lambda: append_run_event(blocked_task, run_id="RUN-001", attempt_id="A-001", event_type="mutation", summary="Must be rejected", status="succeeded"),
        )
        append_run_event(blocked_task, run_id="RUN-001", attempt_id="A-001", event_type="failure", summary="Record tailoring blocker", status="blocked")
        append_run_event(blocked_task, run_id="RUN-001", attempt_id="A-001", event_type="run_finished", summary="Stop affected execution", status="blocked")

    with tempfile.TemporaryDirectory(prefix="v63-unborn-git-") as temp:
        if shutil.which("git"):
            unborn_root = Path(temp)
            subprocess.run(["git", "init"], cwd=unborn_root, check=True, capture_output=True)
            (unborn_root / "tracked.txt").write_text("unborn\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=unborn_root, check=True, capture_output=True)
            snapshot = capture_source_snapshot(unborn_root)
            require_test((snapshot["vcs"] == "git"), "self-test invariant failed at original line 1133: snapshot['vcs'] == 'git'")
            require_test((snapshot["head"] == "UNBORN" and snapshot["head_exists"] is False), "self-test invariant failed at original line 1134: snapshot['head'] == 'UNBORN' and snapshot['head_exists'] is False")
            require_test((snapshot["dirty"] is True and snapshot["dirty_entries"] == 1), "self-test invariant failed at original line 1135: snapshot['dirty'] is True and snapshot['dirty_entries'] == 1")

    with tempfile.TemporaryDirectory(prefix="v63-cli-json-files-") as temp:
        cli_root = Path(temp)
        scripts = Path(__file__).resolve().parent

        def write_fixture(name: str, value) -> Path:
            path = cli_root / name
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return path

        def run_cli(script_name: str, *arguments: str) -> None:
            result = subprocess.run(
                [sys.executable, "-B", "-X", "utf8", str(scripts / script_name), *arguments],
                cwd=cli_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            if result.returncode != 0:
                raise SelfTestFailure(
                    f"{script_name} failed with {result.returncode}: {result.stdout}{result.stderr}"
                )

        snapshot_file = write_fixture("source-snapshot.json", {"kind": "cli-file-test", "head": "UNBORN"})
        questions_file = write_fixture(
            "open-questions.json",
            [{"summary": "Non-blocking CLI fixture", "owner": "self-test", "blocking": False}],
        )
        authority_assessments_file = write_fixture(
            "authority-assessments.json",
            [{
                "reference": "self-test://authority", "source_kind": "Policy", "status": "Valid",
                "scope_refs": ["temporary CLI fixture"], "evidence_refs": ["self-test://authority-evidence"],
                "verified_at": "2026-08-15T00:00:00Z", "expires_at": None,
            }],
        )
        run_cli(
            "init_task.py",
            "--project-root", str(cli_root),
            "--project-id", "P-CLI",
            "--work-item-id", "W-CLI-001",
            "--task-id", "T-001",
            "--ordinal", "1",
            "--objective", "Exercise UTF-8 JSON file inputs",
            "--acceptance", "CLI file inputs are consumed without Base64",
            "--in-scope", "temporary CLI fixture",
            "--delivery-scenario", "DS-03",
            "--development-type", "DT-07",
            "--change-surface", "Agent/Collaboration",
            "--baseline-inheritance", "New",
            "--authority-reference", "self-test://authority",
            "--authority-assessments-json-file", str(authority_assessments_file),
            "--open-questions-json-file", str(questions_file),
            "--source-snapshot-json-file", str(snapshot_file),
        )
        cli_task = cli_root / ".project-governance" / "tasks" / "T-001"
        value_file = write_fixture("objective.json", "Exercise all UTF-8 JSON file input modes")
        run_cli(
            "amend_record.py",
            str(cli_task / "before.json"),
            "--path", "objective",
            "--value-json-file", str(value_file),
            "--reason", "exercise single-value JSON file input",
            "--basis", "self-test",
        )
        changes_file = write_fixture(
            "changes.json",
            [{"path": "scope.in_scope", "value": ["temporary CLI fixture"]}],
        )
        run_cli(
            "amend_record.py",
            str(cli_task / "before.json"),
            "--changes-json-file", str(changes_file),
            "--reason", "exercise batch JSON file input",
            "--basis", "self-test",
        )
        tailoring_arguments = [
            str(cli_task / "before.json"),
            "--stage", "S4",
            "--reason", "close all execution-blocking applicability facts",
            "--basis", "self-test",
            "--extension-trigger", "E01=Inactive",
            "--extension-trigger", "E02=Inactive",
            "--extension-trigger", "E03=Inactive",
            "--extension-trigger", "E04=Inactive",
            "--extension-trigger", "E05=Inactive",
        ]
        cli_facts = dict(TEST_FACTS)
        cli_facts["data_ai_impact"] = "No"
        for key, value in cli_facts.items():
            tailoring_arguments.extend(["--applicability-fact", f"{key}={value}"])
        run_cli("refresh_tailoring_resolution.py", *tailoring_arguments)
        append_run_event(cli_task, run_id="RUN-CLI", attempt_id="A-001", event_type="run_started", summary="Start CLI input test", status="started")
        append_run_event(cli_task, run_id="RUN-CLI", attempt_id="A-001", event_type="verification", summary="Validate CLI JSON file inputs", status="succeeded", evidence_refs=["self-test://cli-json-files"])
        append_run_event(cli_task, run_id="RUN-CLI", attempt_id="A-001", event_type="run_finished", summary="Finish CLI input test", status="succeeded")
        before_manifest = read_json(cli_task / "before.json")["artifact_manifest"]
        terminal_manifest = []
        for item in before_manifest:
            terminal = dict(item)
            terminal["outcome"] = "Created" if item["meta_type"] == "TaskOutcome" else "Revised"
            terminal_manifest.append(terminal)
        manifest_file = write_fixture("terminal-manifest.json", terminal_manifest)
        verification_file = write_fixture(
            "verification.json",
            [{"summary": "CLI file inputs passed", "result": "Passed", "evidence_refs": ["self-test://cli-json-files"], "required": True}],
        )
        empty_array_file = write_fixture("empty-array.json", [])
        run_cli(
            "close_task.py",
            str(cli_task),
            "--status", "Implemented",
            "--fact", "All declared JSON file inputs were parsed",
            "--change", "Created isolated CLI governance artifacts",
            "--verification-json-file", str(verification_file),
            "--incomplete-json-file", str(empty_array_file),
            "--legacy-issues-json-file", str(empty_array_file),
            "--artifact-manifest-json-file", str(manifest_file),
            "--source-snapshot-json-file", str(snapshot_file),
        )
        requirement = cli_root / "requirements.md"
        requirement.write_text("# CLI authority fixture\n", encoding="utf-8")
        profile_fields_file = write_fixture("profile-fields.json", {"purpose": "exercise JSON file input"})
        run_cli(
            "register_authority_asset.py",
            "--project-root", str(cli_root),
            "--project-id", "P-CLI",
            "--asset-id", "PRD-CLI-001",
            "--legacy-kind", "PRD",
            "--title", "CLI file input fixture",
            "--owner", "self-test",
            "--state", "Draft",
            "--revision", "0.1",
            "--content-ref", "requirements.md",
            "--source", "T-001",
            "--scope", "temporary CLI fixture",
            "--profile-fields-json-file", str(profile_fields_file),
        )
        run_cli(
            "rebuild_project_state.py",
            "--project-root", str(cli_root),
            "--project-id", "P-CLI",
        )
        run_cli(
            "generate_review_views.py",
            "--project-root", str(cli_root),
            "--project-id", "P-CLI",
        )
        require_test(((cli_root / ".project-governance" / "generated" / "matrices" / "legacy-137-to-meta-types.md").is_file()), "self-test invariant failed at original line 1284: (cli_root / '.project-governance' / 'generated' / 'matrices' / 'legacy-137-to-meta-types.md').is_file()")

    with tempfile.TemporaryDirectory(prefix="v63-graph-") as temp:
        graph_root = Path(temp)
        new_task(graph_root, "T-001", 1)
        new_task(graph_root, "T-OTHER", 1, project_id="P-OTHER")
        require_test((len(read_json(rebuild_project_state(graph_root, "P-TEST"))["source_tasks"]) == 1), "self-test invariant failed at original line 1290: len(read_json(rebuild_project_state(graph_root, 'P-TEST'))['source_tasks']) == 1")
        new_task(graph_root, "T-002", 1)
        expect_governance_error("duplicate project ordinal", lambda: rebuild_project_state(graph_root, "P-TEST"))

    with tempfile.TemporaryDirectory(prefix="v63-dependency-") as temp:
        dependency_root = Path(temp)
        new_task(dependency_root, "T-002", 2, depends_on=["T-001"])
        expect_governance_error("missing dependency", lambda: rebuild_project_state(dependency_root, "P-TEST"))

    with tempfile.TemporaryDirectory(prefix="v63-cycle-") as temp:
        cycle_root = Path(temp)
        new_task(cycle_root, "T-001", 1, depends_on=["T-002"])
        new_task(cycle_root, "T-002", 2, depends_on=["T-001"])
        expect_governance_error("dependency cycle", lambda: rebuild_project_state(cycle_root, "P-TEST"))

    with tempfile.TemporaryDirectory(prefix="v63-publish-") as temp:
        destination = Path(temp) / "installed-skill"
        destination.mkdir()
        stale = destination / "stale-runtime-fact.txt"
        stale.write_text("stale", encoding="utf-8")
        require_test((publish(destination) > 0), 'self-test invariant failed at original line 1310: publish(destination) > 0')
        require_test((not stale.exists()), 'self-test invariant failed at original line 1311: not stale.exists()')
        require_test((not validate_embedded_manifest(destination)), 'self-test invariant failed at original line 1312: not validate_embedded_manifest(destination)')
        require_test((publish(skill_root) == 0), 'self-test invariant failed at original line 1313: publish(skill_root) == 0')

        manifest_path = embedded_manifest_path(destination)
        original_manifest = read_json(manifest_path)

        wrong_hash = copy.deepcopy(original_manifest)
        wrong_hash["files"][0]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(wrong_hash, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require_test((any("hash mismatch" in item for item in validate_embedded_manifest(destination))), "self-test invariant failed at original line 1321: any(('hash mismatch' in item for item in validate_embedded_manifest(destination)))")

        duplicate_logical = copy.deepcopy(original_manifest)
        duplicate_logical["files"][1]["logical_path"] = duplicate_logical["files"][0]["logical_path"]
        manifest_path.write_text(json.dumps(duplicate_logical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require_test((any("duplicate logical path" in item for item in validate_embedded_manifest(destination))), "self-test invariant failed at original line 1326: any(('duplicate logical path' in item for item in validate_embedded_manifest(destination)))")

        escaped = copy.deepcopy(original_manifest)
        escaped["files"][0]["embedded"] = "../../outside.md"
        manifest_path.write_text(json.dumps(escaped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require_test((any("escapes Skill root" in item for item in validate_embedded_manifest(destination))), "self-test invariant failed at original line 1331: any(('escapes Skill root' in item for item in validate_embedded_manifest(destination)))")

        manifest_path.write_text(json.dumps(original_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        missing_target = destination / original_manifest["files"][0]["embedded"]
        missing_target.unlink()
        require_test((any("embedded file is missing" in item for item in validate_embedded_manifest(destination))), "self-test invariant failed at original line 1336: any(('embedded file is missing' in item for item in validate_embedded_manifest(destination)))")

        publish(destination)
        orphan = destination / "assets" / "runtime" / "norms" / "orphan.md"
        orphan.write_text("orphan\n", encoding="utf-8")
        require_test((any("absent from embedded manifest" in item for item in validate_embedded_manifest(destination))), "self-test invariant failed at original line 1341: any(('absent from embedded manifest' in item for item in validate_embedded_manifest(destination)))")

    unknown_source = copy.deepcopy(tailoring_map)
    unknown_source["source_catalog"][0]["id"] = "UNKNOWN-SOURCE"
    require_test((any("source_catalog must cover" in item for item in validate_tailoring_map(unknown_source))), "self-test invariant failed at original line 1345: any(('source_catalog must cover' in item for item in validate_tailoring_map(unknown_source)))")

    print(json.dumps({
        "profiles": len(profiles),
        "meta_types": 6,
        "runtime_assets": retrieval_validation["manifest_files"],
        "retrieval_gold_cases": retrieval_validation["gold_case_count"],
        "parser_fixture_records": parser_validation["record_count"],
        "index_lifecycle": lifecycle_validation["status"],
        "query_planner": query_planner_validation["status"],
        "active_query_tree_adversarial": active_query_tree_validation,
        "derived_view_byte_adversarial": derived_view_byte_validation,
        "new_query_history": new_query_history_validation,
        "document_governance": document_governance_validation,
        "consumer_bootstrap": consumer_bootstrap_validation,
        "minimal_carrier": minimal_carrier_validation,
        "positive": "passed",
        "negative": "passed",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
