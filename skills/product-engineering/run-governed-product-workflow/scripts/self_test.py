#!/usr/bin/env python3
"""Positive and negative conformance tests for V6.3 Candidate."""

from __future__ import annotations

import copy
import argparse
import hashlib
import contextlib
import io
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
    validate_clarification,
    current_tailoring,
    validate_tailoring_resolution,
    require_decision,
    validate_requirement_items,
    reconcile_scope,
    _scope_pattern_matches,
    _is_external_declaration,
    skill_root_path,
    EXPECTED_MANIFEST_ROLES,
    GovernanceError,
    _write_derived_view,
    atomic_write_json,
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
    prune_runtime_index_cache,
    run_lock_lifecycle_fixtures,
    run_parser_fixtures,
)
from check_write_guard import evaluate as evaluate_write_guard
from manage_project_docs import (
    apply_migration_plan,
    create_migration_plan,
    initialize_project_document_layout,
    sha256_file,
    validate_project_document_layout,
)
import console_model
from minimal_task import (
    append_minimal_event,
    close_minimal_record,
    create_minimal_record,
    mark_minimal_upgrade,
    validate_minimal_record,
)
from get_context import should_skip_for_minimal
from query_norm_context import run_query_planner_fixtures
from signals import active_task_signal, recommendations
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


def minimal_fixture_record(project_root: Path, task_id: str, *, change_surface: str = "UI/UX", delivery_scenario: str = "DS-03") -> Path:
    evidence = [
        "evidence://risk-low",
        "evidence://reversible",
        "evidence://single-scope",
        "evidence://no-external-effect",
        "evidence://no-production",
        "evidence://no-security",
        "evidence://extensions-inactive",
    ]
    return create_minimal_record(
        project_root,
        project_id="P-MIN",
        work_item_id=f"W-{task_id}",
        task_id=task_id,
        ordinal=1,
        depends_on=[],
        supersedes=[],
        objective="Update one local label.",
        request_snapshot={
            "language": "en",
            "text": "Update one local label.",
            "captured_at": "2026-08-15T00:00:00Z",
        },
        requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "Update one local label.", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
        decisions=[
            {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
        ],
        clarification={
            "state": "Settled",
            "mode": "Skipped",
            "notice": "Requirement is unambiguous and matches the repository; skipping the question round.",
            "survey_refs": ["self-test://survey"],
            "rounds": [],
            "basis": "self-test fixture: single label change, fully declared",
        },
        scope="Change one label.",
        acceptance="The focused test passes.",
        delivery_scenario=delivery_scenario,
        development_type="DT-08",
        change_surface=change_surface,
        selected_approach="Edit one label.",
        alternative_rejected="Keep current text.",
        plan_steps=["Edit."],
        verification="Run focused test.",
        rollback="Restore line.",
        allowed_paths=["src/label.txt"],
        out_of_scope=[],
        forbidden_actions=[],
        selection_source="automatic",
        basis=["All Minimal eligibility facts were inspected."],
        authority_refs=["conversation://fixture"],
        eligibility_evidence_refs=evidence,
        facts=["The current label is observable."],
        constraints=["Only src/label.txt is authorized."],
        assumptions=[],
        fundamentals=["One value changes.", "The change is reversible."],
        causal_chain=["A focused edit satisfies acceptance."],
        decision_criteria=["The test passes."],
    )


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
        # tailoring_resolution is a derived view now. A stale snapshot is not an error,
        # and nothing gates on it: what blocks an action is the tailoring resolved at the
        # moment of that action. Requiring the two to match is what made restating a
        # recalculation cost an Amendment, 24 times in this project alone.
        stale_contract = read_json(task_dir / "before.json")
        stale_contract["tailoring_resolution"] = {
            **stale_contract["tailoring_resolution"],
            "blocking_reasons": ["stale placeholder"],
        }
        require_test(
            (validate_tailoring_resolution(stale_contract) == []),
            "a stale tailoring snapshot must not be an error; it is a derived view",
        )
        require_test(
            (current_tailoring(stale_contract)["blocking_reasons"] != ["stale placeholder"]),
            "gating must use the tailoring resolved now, not the stored snapshot",
        )
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
            request_snapshot={"language": "en", "text": "self-test minimal fixture", "captured_at": "2026-08-15T00:00:00Z"},
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["self-test://survey"], "rounds": [], "basis": "self-test fixture"},
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
        signal = active_task_signal(task_dir)
        require_test(
            signal and signal["pending_acceptance"] and not signal.get("upgrade_pending"),
            "active Minimal carrier must remain pending until close or upgrade",
        )
        active_commands = {item["command"] for item in recommendations([signal])}
        require_test(
            {"run", "verify", "close"} <= active_commands,
            "active Minimal carrier should retain run/verify/close recommendations",
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

    for blocked_surface in (
        "Identity/Security/Privacy",
        "Deploy/Operations",
        "Data/Schema",
        "AI/Data Governance",
        "Architecture/Multi-repo",
    ):
        with tempfile.TemporaryDirectory(prefix="v63-minimal-surface-block-") as temp:
            project_root = Path(temp)
            expect_governance_error(
                f"Minimal rejects {blocked_surface}",
                lambda blocked_surface=blocked_surface, project_root=project_root: minimal_fixture_record(
                    project_root,
                    "T-MIN-BLOCK",
                    change_surface=blocked_surface,
                ),
            )
            require_test(
                not (project_root / ".project-governance" / "tasks" / "T-MIN-BLOCK" / "task-record.json").exists(),
                "rejected Minimal surface must not write task-record.json",
            )

    with tempfile.TemporaryDirectory(prefix="v63-minimal-ds04-block-") as temp:
        project_root = Path(temp)
        expect_governance_error(
            "Minimal rejects DS-04",
            lambda: minimal_fixture_record(
                project_root,
                "T-MIN-DS04",
                delivery_scenario="DS-04",
            ),
        )
        require_test(
            not (project_root / ".project-governance" / "tasks" / "T-MIN-DS04" / "task-record.json").exists(),
            "rejected Minimal scenario must not write task-record.json",
        )

    with tempfile.TemporaryDirectory(prefix="v63-minimal-validate-block-") as temp:
        project_root = Path(temp)
        record_path = minimal_fixture_record(project_root, "T-MIN-TAMPER")
        record = read_json(record_path)
        record["task_contract"]["task_profile"]["change_surface"] = "Data/Schema"
        errors = validate_minimal_record(record, task_dir=record_path.parent)
        require_test(
            any("Minimal rejects change_surface Data/Schema" in error for error in errors),
            "validate_minimal_record must reject extension-triggering surfaces",
        )

    with tempfile.TemporaryDirectory(prefix="v63-get-context-stray-") as temp:
        task_dir = Path(temp) / ".project-governance" / "tasks" / "T-FULL-STRAY"
        task_dir.mkdir(parents=True)
        (task_dir / "before.json").write_text("{}\n", encoding="utf-8")
        (task_dir / "task-record.json").write_text("not-even-json", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            require_test(
                should_skip_for_minimal(task_dir) is False,
                "Full carrier must not skip norm query because a stray task-record.json exists",
            )

    with tempfile.TemporaryDirectory(prefix="v63-get-context-invalid-min-") as temp:
        task_dir = Path(temp) / ".project-governance" / "tasks" / "T-BAD-MIN"
        task_dir.mkdir(parents=True)
        (task_dir / "task-record.json").write_text("not-even-json", encoding="utf-8")
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve().with_name("get_context.py")),
                "--task-dir",
                str(task_dir),
                "--action",
                "run_started",
                "--query-text",
                "fixture",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        require_test(process.returncode == 2, "invalid Minimal task-record must fail get_context")
        require_test(
            "Minimal skips bounded norm query" not in process.stdout,
            "invalid Minimal task-record must not print skip notice",
        )

    with tempfile.TemporaryDirectory(prefix="v63-get-context-active-min-") as temp:
        project_root = Path(temp)
        record_path = minimal_fixture_record(project_root, "T-MIN-GET")
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve().with_name("get_context.py")),
                "--task-dir",
                str(record_path.parent),
                "--action",
                "run_started",
                "--query-text",
                "fixture",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        require_test(process.returncode == 0, "active Minimal task-record should skip bounded query")
        require_test(
            "Minimal skips bounded norm query" in process.stdout,
            "active Minimal task-record should print skip notice",
        )

    with tempfile.TemporaryDirectory(prefix="v63-minimal-upgraded-signal-") as temp:
        project_root = Path(temp)
        record_path = minimal_fixture_record(project_root, "T-MIN-UPG")
        upgraded = mark_minimal_upgrade(
            record_path.parent,
            reason="Scope expanded beyond Minimal.",
            basis="evidence://scope-expanded",
            full_carrier_ref=".project-governance/tasks/T-MIN-UPG/before.json",
        )
        atomic_write_json(record_path, upgraded)
        signal = active_task_signal(record_path.parent)
        require_test(
            signal and signal["lifecycle_state"] == "Upgraded" and signal.get("upgrade_pending"),
            "Upgraded Minimal carrier must be marked as upgrade_pending",
        )
        require_test(
            not signal["pending_acceptance"],
            "Upgraded Minimal carrier must not remain pending acceptance",
        )
        commands = {item["command"] for item in recommendations([signal])}
        require_test("init" in commands, "Upgraded Minimal carrier must recommend init upgrade")
        require_test(
            not ({"run", "verify", "close"} & commands),
            "Upgraded Minimal carrier must not recommend run/verify/close",
        )
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve().with_name("get_context.py")),
                "--task-dir",
                str(record_path.parent),
                "--action",
                "run_started",
                "--query-text",
                "fixture",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        require_test(process.returncode == 2, "Upgraded Minimal task-record must fail get_context")
        require_test(
            "Minimal skips bounded norm query" not in process.stdout,
            "Upgraded Minimal task-record must not print skip notice",
        )

    with tempfile.TemporaryDirectory(prefix="v63-mixed-carrier-signal-") as temp:
        project_root = Path(temp)
        record_path = minimal_fixture_record(project_root, "T-MIX")
        (record_path.parent / "before.json").write_text(
            json.dumps(
                {
                    "task_id": "T-MIX",
                    "lifecycle_state": "Ready",
                    "task_profile": {
                        "applicability_facts": {
                            "security_privacy_impact": "Unknown",
                            "production_release": "Unknown",
                        }
                    },
                    "tailoring_resolution": {"blocking_reasons": ["unknown facts"]},
                    "scope": {"allowed_paths": ["src/only-full.txt"]},
                }
            ),
            encoding="utf-8",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            mixed_signal = active_task_signal(record_path.parent)
        require_test(
            mixed_signal
            and mixed_signal["carrier"] == "Full"
            and mixed_signal["pending_acceptance"]
            and mixed_signal["unknown_blockers"],
            "before.json must win over a stray Minimal record",
        )
        mixed_commands = {item["command"] for item in recommendations([mixed_signal])}
        require_test(
            mixed_commands == {"clarify", "plan"},
            "mixed carrier must surface full-carrier Unknown blockers",
        )

    with tempfile.TemporaryDirectory(prefix="v63-upgrade-sibling-signal-") as temp:
        project_root = Path(temp)
        record_path = minimal_fixture_record(project_root, "T-MIN-UPG-SIB")
        upgraded = mark_minimal_upgrade(
            record_path.parent,
            reason="Scope expanded beyond Minimal.",
            basis="evidence://scope-expanded",
            full_carrier_ref=".project-governance/tasks/T-MIN-UPG-SIB/before.json",
        )
        atomic_write_json(record_path, upgraded)
        sibling = {
            "task_id": "T-FULL-ACTIVE",
            "carrier": "Full",
            "lifecycle_state": "Frozen",
            "unknown_blockers": [],
            "pending_acceptance": True,
            "minimal_eligibility": None,
            "upgrade_pending": False,
        }
        sibling_commands = {
            item["command"]
            for item in recommendations([active_task_signal(record_path.parent), sibling])
        }
        require_test(
            {"run", "verify", "close"} <= sibling_commands,
            "Upgraded leftover must not suppress sibling run/verify/close",
        )

    with tempfile.TemporaryDirectory(prefix="v63-minimal-defaults-") as temp:
        project_root = Path(temp)
        record_path = create_minimal_record(
            project_root,
            project_id="P-DEF",
            work_item_id="W-DEF",
            task_id="T-DEF-001",
            ordinal=1,
            depends_on=[],
            supersedes=[],
            objective="Update one local label.",
            request_snapshot={"language": "en", "text": "self-test minimal fixture", "captured_at": "2026-08-15T00:00:00Z"},
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["self-test://survey"], "rounds": [], "basis": "self-test fixture"},
            scope="Change one label.",
            acceptance="The focused test passes.",
            delivery_scenario="DS-03",
            development_type="DT-08",
            change_surface="UI/UX",
            selected_approach="Edit one label.",
            alternative_rejected="Keep current text.",
            plan_steps=["Edit."],
            verification="Run focused test.",
            rollback="",
            allowed_paths=["src/label.txt"],
            out_of_scope=[],
            forbidden_actions=[],
            selection_source="automatic",
            basis=["Eligibility facts were inspected."],
            authority_refs=["conversation://fixture"],
            eligibility_evidence_refs=evidence,
            facts=["The current label is observable."],
            constraints=[],
            assumptions=[],
            fundamentals=["One value changes.", "The change is reversible."],
            causal_chain=["A focused edit satisfies acceptance."],
            decision_criteria=["The test passes."],
        )
        record = read_json(record_path)
        require_test(
            any("script default" in item for item in record["selection"]["basis"]),
            "Minimal defaults must leave a basis trace",
        )
        require_test(
            record["task_contract"]["plan"]["rollback"].startswith("script default:"),
            "Minimal rollback default must be recorded",
        )
        require_test(
            record["task_contract"]["first_principles_analysis"]["constraints"][0].startswith("script default:"),
            "Minimal constraint default must be recorded",
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
            request_snapshot={"language": "en", "text": "self-test minimal fixture", "captured_at": "2026-08-15T00:00:00Z"},
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["self-test://survey"], "rounds": [], "basis": "self-test fixture"},
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
            request_snapshot={"language": "en", "text": "self-test fixture request", "captured_at": "2026-08-15T00:00:00Z"},
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test fixture request", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Scope is fully declared by the fixture; skipping the question round.", "survey_refs": ["self-test://survey"], "rounds": [], "basis": "self-test fixture"},
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
    return {"status": "Passed", "lifecycle": "single-file", "upgrade": "one-way", "defaults": "traceable"}


def run_console_deployment_fixture() -> dict[str, object]:
    """The console is a template here and a real, pinned launcher inside a project."""

    import deploy_console

    scripts_dir = skill_root_path() / "scripts"

    # The deployed set is declared, not computed at deploy time, so that what lands in
    # a project is auditable. That only holds while the declaration matches reality.
    require_test(
        deploy_console.SNAPSHOT_MODULES == deploy_console.computed_closure(scripts_dir),
        "console snapshot list must equal the console's real import closure: "
        f"declared={deploy_console.SNAPSHOT_MODULES} "
        f"computed={deploy_console.computed_closure(scripts_dir)}",
    )
    for template in (deploy_console.LAUNCHER_TEMPLATE, deploy_console.README_TEMPLATE):
        require_test(
            (skill_root_path() / "assets" / "project-templates" / template).is_file(),
            f"console template must exist: {template}",
        )

    with tempfile.TemporaryDirectory(prefix="v63-console-deploy-") as temp:
        root = Path(temp)
        # Establishing the governance directory is what deploys the console.
        initialize_project_document_layout(root)
        console_root = root / ".project-governance" / "console"
        require_test((console_root / "console.py").is_file(), "project must get its own launcher")
        require_test((console_root / "README.md").is_file(), "project must get the console docs")
        deployment = read_json(console_root / "deployment.json")

        # A snapshot whose bytes drifted from the Skill would silently be a different
        # tool wearing the same version number.
        require_test(
            set(deployment["snapshot"]) == set(deploy_console.SNAPSHOT_MODULES),
            "deployment record must cover every snapshot module",
        )
        for name in deploy_console.SNAPSHOT_MODULES:
            deployed = (console_root / "snapshot" / name).read_bytes()
            require_test(
                deployed == (scripts_dir / name).read_bytes(),
                f"deployed snapshot must be byte-identical to the Skill: {name}",
            )
            require_test(
                hashlib.sha256(deployed).hexdigest() == deployment["snapshot"][name],
                f"deployment record must match the deployed bytes: {name}",
            )

        # Redeploying an up-to-date console must not churn the project.
        require_test(
            deploy_console.deploy(root) is False,
            "deploying an already-current console must be a no-op",
        )

        # Negative: local tampering has to be visible, not silent.
        target = console_root / "snapshot" / "console_render.py"
        target.write_bytes(target.read_bytes() + b"\n# tampered\n")
        status = deploy_console.deployment_status(root, skill_root_path())
        require_test(
            status["modified"] == ["console_render.py"],
            f"tampering must be reported, got {status}",
        )
        deploy_console.deploy(root, force=True)
        require_test(
            not deploy_console.deployment_status(root, skill_root_path())["modified"],
            "a forced redeploy must restore the snapshot",
        )

    # The integrity page audits the Skill, so a console whose Skill is out of reach
    # must report that the check did not run. Reporting zero problems there would be
    # a clean bill of health for a check that never happened.
    with tempfile.TemporaryDirectory(prefix="v63-console-unreachable-") as temp:
        missing = Path(temp) / "no-skill-here"
        missing.mkdir()
        saved = console_model.embedded_manifest_path
        try:
            console_model.embedded_manifest_path = lambda *a, **k: missing / "embedded-manifest.json"
            integrity = console_model.scan_integrity()
        finally:
            console_model.embedded_manifest_path = saved
        require_test(integrity["reachable"] is False, "an unreachable Skill must be reported as such")
        require_test(integrity["errors"] == [], "an unreachable Skill is not a hash mismatch")
        require_test(integrity["total"] == 0, "an unreachable Skill checks nothing")

    return {"status": "Passed", "checks": 12}


def run_cache_prune_fixture() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="v63-cache-prune-") as temp:
        root = Path(temp)
        for name in (
            "a" * 64 + ".sqlite3",
            "a" * 64 + ".lock",
            "b" * 64 + ".sqlite3",
            "b" * 64 + ".lock",
            "notes.txt",
        ):
            (root / name).write_text("fixture\n", encoding="utf-8")
        warnings = prune_runtime_index_cache(root, "a" * 64)
        require_test(warnings == [], "cache prune fixture should not warn")
        require_test((root / ("a" * 64 + ".sqlite3")).is_file(), "active sqlite must remain")
        require_test((root / ("a" * 64 + ".lock")).is_file(), "active lock must remain")
        require_test(not (root / ("b" * 64 + ".sqlite3")).exists(), "old sqlite must be removed")
        require_test(not (root / ("b" * 64 + ".lock")).exists(), "old lock must be removed")
        require_test((root / "notes.txt").is_file(), "non-cache file must remain")
    return {"status": "Passed", "checks": 5}


def run_write_guard_fixture() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="v63-write-guard-") as temp:
        root = Path(temp)
        task_dir = new_task(root, "T-GUARD", 1)
        allowed, message = evaluate_write_guard(root / "src" / "file.txt", task_dir)
        require_test(allowed and "allowed_path" in message, "allowed path must pass")
        allowed, message = evaluate_write_guard(
            root / ".project-governance" / "project-state.json",
            task_dir,
        )
        require_test(not allowed and "project-state.json" in message, "project-state direct edit must be refused")
        allowed, message = evaluate_write_guard(
            Path(__file__).resolve().parent.parent
            / "assets"
            / "runtime"
            / "embedded-manifest.json",
            task_dir,
        )
        require_test(not allowed and "embedded-manifest.json" in message, "manifest direct edit must be refused")
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve().with_name("check_write_guard.py")),
                "--task-dir",
                str(root / ".project-governance" / "tasks" / "MISSING"),
                str(root / "src" / "file.txt"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        require_test(process.returncode == 0 and "WARNING" in process.stderr, "guard failure must fail open with warning")

    with tempfile.TemporaryDirectory(prefix="v63-write-guard-stray-garbage-") as temp:
        root = Path(temp)
        task_dir = root / ".project-governance" / "tasks" / "T-FULL-STRAY"
        task_dir.mkdir(parents=True)
        (task_dir / "before.json").write_text(
            json.dumps({"scope": {"allowed_paths": ["src/label.txt"]}}),
            encoding="utf-8",
        )
        (task_dir / "task-record.json").write_text("not-even-json", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            allowed, message = evaluate_write_guard(root / "secrets.env", task_dir)
        require_test(
            not allowed and "allowed_paths" in message,
            "stray garbage task-record must not fail-open when before.json exists",
        )
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).resolve().with_name("check_write_guard.py")),
                "--task-dir",
                str(task_dir),
                str(root / "secrets.env"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        require_test(
            process.returncode == 1 and "REFUSED" in process.stderr,
            "stray garbage task-record CLI must refuse using full carrier paths",
        )

    with tempfile.TemporaryDirectory(prefix="v63-write-guard-mixed-") as temp:
        root = Path(temp)
        record_path = minimal_fixture_record(root, "T-GUARD-MIX")
        (record_path.parent / "before.json").write_text(
            json.dumps({"scope": {"allowed_paths": ["src/only-full.txt"]}}),
            encoding="utf-8",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            allowed_full, _ = evaluate_write_guard(root / "src" / "only-full.txt", record_path.parent)
            allowed_min, _ = evaluate_write_guard(root / "src" / "label.txt", record_path.parent)
        require_test(allowed_full, "mixed carrier write guard must use full allowed_paths")
        require_test(not allowed_min, "mixed carrier write guard must ignore Minimal allowed_paths")
    return {"status": "Passed", "checks": 8}


def new_task(root: Path, task_id: str, ordinal: int, *, project_id: str = "P-TEST", depends_on=()) -> Path:
    return initialize_task(
        root,
        project_id=project_id,
        work_item_id=f"W-{task_id}",
        task_id=task_id,
        ordinal=ordinal,
        objective=f"Conformance task {task_id}",
        request_snapshot={
            "language": "en",
            "text": f"Conformance fixture request for {task_id}",
            "captured_at": "2026-08-15T00:00:00Z",
        },
        requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": f"Conformance fixture request for {task_id}", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
        decisions=[
            {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
            {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
        ],
        clarification={
            "state": "Settled",
            "mode": "Skipped",
            "notice": "Requirement is unambiguous and matches the repository; skipping the question round.",
            "survey_refs": ["self-test://survey"],
            "rounds": [],
            "basis": "self-test fixture: the caller declares the full scope",
        },
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
        "SKILL.md", "agents", "scripts", "references", "commands", "assets"
    }.issubset({item.name for item in skill_root.iterdir()})), "Skill root must contain the required entrypoint, command references, runtime assets, and UI metadata")
    require_test((skill_root.name == "run-governed-product-workflow"), "self-test invariant failed at original line 424: skill_root.name == 'run-governed-product-workflow'")
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    skill_lines = skill_text.splitlines()
    require_test((len(skill_lines) < 200), "SKILL.md must remain below 200 lines after command reference split")
    require_test((skill_lines[0] == "---" and "---" in skill_lines[1:]), "self-test invariant failed at original line 428: skill_lines[0] == '---' and '---' in skill_lines[1:]")
    frontmatter_end = skill_lines[1:].index("---") + 1
    frontmatter_keys = {
        line.split(":", 1)[0].strip()
        for line in skill_lines[1:frontmatter_end]
        if ":" in line
    }
    require_test(({"name", "description", "metadata"}.issubset(frontmatter_keys)), "frontmatter must include name, description, and metadata")
    # SKILL.md frontmatter is the single declaration of the version. Deriving it
    # here instead of hardcoding it keeps a release from needing an edit to this
    # file, where forgetting would fail with a message that names the wrong cause.
    declared_version_match = re.search(
        r"^\s+version:\s*(\S+)\s*$",
        "\n".join(skill_lines[1:frontmatter_end]),
        re.MULTILINE,
    )
    require_test(bool(declared_version_match), "frontmatter metadata must declare a version")
    declared_version = declared_version_match.group(1)
    require_test(
        bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9a-z.]+)?", declared_version)),
        f"frontmatter metadata.version must be a semantic version, got {declared_version!r}",
    )
    release_tag = f"rgpw-v{declared_version}"
    reference_files = sorted(
        path.relative_to(skill_root).as_posix()
        for path in (skill_root / "references").rglob("*")
        if path.is_file()
    )
    required_reference_files = {
        "references/first-principles-method.md",
        "references/project-document-layout.md",
        "references/spec-source-map.md",
    }
    require_test((required_reference_files.issubset(reference_files)), 'self-test invariant failed at original line 447: required_reference_files.issubset(reference_files)')
    require_test((all(f"({relative})" in skill_text for relative in reference_files)), "self-test invariant failed at original line 448: all((f'({relative})' in skill_text for relative in reference_files))")
    command_reference_files = sorted(
        path.relative_to(skill_root).as_posix()
        for path in (skill_root / "commands").glob("*.md")
    )
    require_test((set(command_reference_files) == {
        "commands/init.md",
        "commands/clarify.md",
        "commands/plan.md",
        "commands/run.md",
        "commands/verify.md",
        "commands/close.md",
        "commands/status.md",
        "commands/migrate.md",
        "commands/minimal.md",
    }), "all command reference files must exist")
    require_test((all(f"({relative})" in skill_text for relative in command_reference_files)), "SKILL.md must link every command reference")

    # The command cards used to live in reference/, one character away from
    # references/, which is both a bundled-resource directory and the manifest's
    # logical namespace for the norms. Keep the singular name from coming back.
    require_test(
        (not (skill_root / "reference").exists()),
        "command cards live in commands/; the singular reference/ directory must not return",
    )
    singular = sorted(
        path.relative_to(skill_root).as_posix()
        for path in list(skill_root.glob("*.md")) + list((skill_root / "commands").glob("*.md"))
        if re.search(r"(?<![a-z])reference/(?!s)", path.read_text(encoding="utf-8"))
    )
    require_test(
        (not singular),
        f"these files still point at the retired reference/ directory: {singular}",
    )

    # VC-PPG-DEC-001 16.4 owns the Minimal eligibility conditions, and
    # minimal-task-record.schema.json pins them as const-constrained fields. The table
    # in commands/minimal.md is the one human-readable projection of that pair. Hold it
    # to the schema in both directions so the projection cannot silently drift, and keep
    # SKILL.md from growing a third copy -- SKILL.md 7 allows exactly one authoritative
    # definition per fact.
    minimal_card = (skill_root / "commands" / "minimal.md").read_text(encoding="utf-8")
    eligibility_schema = read_json(
        skill_root / "assets" / "runtime" / "schemas" / "minimal-task-record.schema.json"
    )["properties"]["eligibility"]
    # evidence_refs proves the conditions; it is not itself one of them.
    controlled_keys = {
        key for key in eligibility_schema["required"] if key != "evidence_refs"
    }
    projected_keys = set(re.findall(r"\| `([a-z_]+)` \|", minimal_card))
    missing_keys = sorted(controlled_keys - projected_keys)
    require_test(
        (not missing_keys),
        f"commands/minimal.md eligibility table must project every schema field; missing: {missing_keys}",
    )
    stray_keys = sorted(projected_keys - controlled_keys)
    require_test(
        (not stray_keys),
        f"commands/minimal.md eligibility table names fields the schema does not control: {stray_keys}",
    )
    # VC-PPG-PRO-001 S1 filters Grill Me on materiality alone. "不可发现" appears once
    # in the whole corpus, at PRO-001:116, as the Requestor's duty to volunteer such
    # constraints -- never as a limit on what the Agent may ask. SKILL.md previously
    # carried it as a gate, which let almost any question be argued away as something
    # the Agent could look up, and biased the agent toward not asking.
    discoverability_gate = [
        phrase for phrase in ("无法发现", "不可发现") if phrase in skill_text
    ]
    require_test(
        (not discoverability_gate),
        f"SKILL.md must filter questions on materiality, not discoverability; found: {discoverability_gate}",
    )
    # An objective is the agent's summary. Recording it in a language the requester
    # does not use, with no verbatim original kept beside it, leaves them unable to
    # check the summary at all.
    require_test(
        ("用户提问所用的语言" in skill_text and "request_snapshot" in skill_text),
        "SKILL.md must require human-facing records in the requester's language and a verbatim request_snapshot",
    )
    for schema_name, container in (
        ("task-before.schema.json", lambda doc: doc["properties"]),
        ("minimal-task-record.schema.json",
         lambda doc: doc["properties"]["task_contract"]["properties"]),
    ):
        schema = read_json(skill_root / "assets" / "runtime" / "schemas" / schema_name)
        require_test(
            ("request_snapshot" in container(schema)),
            f"{schema_name} must carry request_snapshot so the original wording survives",
        )

    clarify_card = (skill_root / "commands" / "clarify.md").read_text(encoding="utf-8")
    # The S1 exit conditions are the norm's, and a zero-round claim is only legitimate
    # when they demonstrably hold. Keep both in the card that owns the rule.
    missing_exit = [
        phrase for phrase in ("可表达", "已逐项列出") if phrase not in clarify_card
    ]
    require_test(
        (not missing_exit),
        f"commands/clarify.md must carry the VC-PPG-PRO-001 S1 exit conditions; missing: {missing_exit}",
    )

    # The clarification loop failed for years because it lived only as prose in a card
    # the routing rules forbade reading. These checks hold the repair in place: the
    # decision is stated where the judgement layer can see it, both outcomes are spoken
    # aloud, and the carrier that records them is required by both schemas.
    skip_notice = "你的需求已经描述的非常清楚了，并且和项目现状一致，本次跳过向你提问的阶段"
    ask_notice = "针对你的需求和项目现状，有几个问题需要你先回答，以保证本需求完成的质量"
    for label, text in (("SKILL.md", skill_text), ("commands/clarify.md", clarify_card)):
        missing = [n for n in (skip_notice, ask_notice) if n not in text]
        require_test(
            (not missing),
            f"{label} must carry both clarification notices so a skipped round is never silent",
        )
    require_test(
        ("commands/clarify.md" in skill_text and "建立任务前无条件执行" in skill_text),
        "SKILL.md must make the clarification decision unconditional at the judgement layer",
    )
    require_test(
        ("Ambiguous" in clarify_card and "必须追问" in clarify_card),
        "commands/clarify.md must send an ambiguous answer back into another round",
    )
    for schema_name, container in (
        ("task-before.schema.json", lambda doc: doc),
        ("minimal-task-record.schema.json",
         lambda doc: doc["properties"]["task_contract"]),
    ):
        schema = read_json(skill_root / "assets" / "runtime" / "schemas" / schema_name)
        node = container(schema)
        missing = [
            field for field in ("request_snapshot", "clarification")
            if field not in node["required"]
        ]
        require_test(
            (not missing),
            f"{schema_name} must require {missing} so a task cannot be created without archiving them",
        )
    unsettled = validate_clarification(
        {"state": "Open", "mode": "Asked", "notice": "n", "survey_refs": ["s"], "rounds": [], "basis": "b"}
    )
    require_test(bool(unsettled), "an unsettled clarification must block")
    ambiguous = validate_clarification({
        "state": "Settled", "mode": "Asked", "notice": "n", "survey_refs": ["s"], "basis": "b",
        "rounds": [{"ordinal": 1, "asked_at": "2026-08-15T00:00:00Z", "exchanges": [
            {"question": "q", "changes": "Scope", "recommended_default": "d",
             "answer": "maybe", "answer_state": "Ambiguous"}]}],
    })
    require_test(bool(ambiguous), "an ambiguous answer must keep the task open")
    settled = validate_clarification({
        "state": "Settled", "mode": "Skipped", "notice": skip_notice,
        "survey_refs": ["survey://x"], "rounds": [], "basis": "surveyed",
    })
    require_test((not settled), f"a surveyed zero-round record must pass, got {settled}")

    # Minimal is the common path, so a gate wired only into the full carrier is not a
    # gate at all. Both entry points have to consume the same decision check.
    import inspect as _inspect
    from minimal_task import append_minimal_event as _append_min, close_minimal_record as _close_min
    for fn, why in (
        (_append_min, "Minimal execution must require a Proceed decision"),
        (_close_min, "Minimal close must require an Acceptance decision"),
    ):
        require_test(
            ("require_decision" in _inspect.getsource(fn)),
            f"{why}; {fn.__name__} does not consult the decision gate",
        )

    # The three gates are the whole ordering model. If the surface stops naming them the
    # next author will reinvent a state machine, which is what made tailoring_resolution
    # the most-amended field in the system.
    for phrase in ("三道门", "clarification.state", "Proceed", "Acceptance", "run_started"):
        require_test(
            (phrase in skill_text),
            f"SKILL.md must name the gate that actually blocks: missing {phrase!r}",
        )

    # Only a person can give Proceed or Acceptance. This cannot prove one was given --
    # the response is typed by whoever runs the Agent -- but an absent decision now
    # stops the run instead of looking exactly like a decision that was made.
    def _dec(**over):
        base = {"id": "D-01", "kind": "Proceed", "presented": "p", "response": "Proceed",
                "decided_by": "someone", "decided_at": "2026-08-15T00:00:00Z"}
        base.update(over)
        return base

    require_test((require_decision({"decisions": [_dec()]}, "Proceed", "execution") == []),
                 "a recorded Proceed must let execution through")
    require_test((require_decision({"decisions": []}, "Proceed", "execution")),
                 "an absent Proceed must block execution")
    require_test((require_decision({"decisions": [_dec(response="   ")]}, "Proceed", "execution")),
                 "a Proceed with a blank response is not a decision")
    require_test((require_decision({"decisions": [_dec()]}, "Acceptance", "close")),
                 "a Proceed does not stand in for Acceptance")

    # The requirement ledger is checked against a text the Agent did not write, so both
    # halves have to hold: a quote cannot be invented, and no clause of the request may
    # go unaccounted for. The second is the one that finds what was silently dropped.
    def _req_contract(items, answer=None):
        clarification = {"state": "Settled", "mode": "Skipped", "notice": "n",
                         "survey_refs": ["s"], "rounds": [], "basis": "b"}
        if answer is not None:
            clarification = {**clarification, "mode": "Asked", "rounds": [{
                "ordinal": 1, "asked_at": "2026-08-15T00:00:00Z",
                "exchanges": [{"question": "q", "changes": "Scope", "recommended_default": "d",
                               "answer": answer, "answer_state": "Answered"}]}]}
        return {"request_snapshot": {"language": "zh", "text": "先改登录页；再加导出按钮",
                                     "captured_at": "2026-08-15T00:00:00Z"},
                "clarification": clarification, "requirement_items": items}

    def _item(quote, **over):
        base = {"id": "R-01", "source": "request_snapshot", "quote": quote,
                "reading": "r", "state": "Covered", "evidence_refs": ["e://1"]}
        base.update(over)
        return base

    complete = [_item("先改登录页"), _item("再加导出按钮", id="R-02")]
    require_test(
        (not validate_requirement_items(_req_contract(complete))),
        "a decomposition covering every clause verbatim must pass",
    )
    require_test(
        (any("not verbatim" in item for item in
             validate_requirement_items(_req_contract([_item("加一个我没说过的功能")])))),
        "a quote absent from the requester's words must be rejected",
    )
    dropped = validate_requirement_items(_req_contract([_item("先改登录页")]))
    require_test(
        (any("再加导出按钮" in item for item in dropped)),
        f"an unaccounted clause must be named; got {dropped}",
    )
    from_answer = validate_requirement_items(_req_contract(complete, answer="顺便把弹窗文案也换掉"))
    require_test(
        (any("顺便把弹窗文案也换掉" in item and "clarification:r1.e1" in item for item in from_answer)),
        f"a clarification answer is a requirement source too and must be covered; got {from_answer}",
    )
    still_open = validate_requirement_items(
        _req_contract([_item("先改登录页", state="Open"), _item("再加导出按钮", id="R-02")]),
        require_discharge=True,
    )
    require_test((any("still Open" in item for item in still_open)),
                 "an Open item must block the close")
    no_evidence = validate_requirement_items(
        _req_contract([_item("先改登录页", evidence_refs=[]), _item("再加导出按钮", id="R-02")]),
        require_discharge=True,
    )
    require_test((any("cites no evidence" in item for item in no_evidence)),
                 "Covered without evidence must block the close")

    # Scope reconciliation is the first blocker whose two sides are not both written by
    # the Agent: one is the declaration, the other is Git. The matcher is where its bugs
    # would hide, so hold each shape allowed_paths actually takes in this repo.
    for relative, pattern, expected in (
        ("src/app.py", "src", True),
        ("src/deep/nested/app.py", "src", True),
        ("other/lib.py", "src", False),
        ("srcnot/app.py", "src", False),
        ("a/b/c.py", "a/**", True),
        ("scripts/update_catalog.py", "scripts/update_catalog.py", True),
        (".project-governance/tasks/T/before.json", ".project-governance", True),
    ):
        require_test(
            (_scope_pattern_matches(relative, pattern) is expected),
            f"scope matcher: {relative!r} vs {pattern!r} should be {expected}",
        )
    require_test(
        (_is_external_declaration("D:/elsewhere/**") and _is_external_declaration("/abs/x")
         and not _is_external_declaration("src/**")),
        "declarations outside the repository must be excluded from reconciliation",
    )
    skipped = reconcile_scope(Path("."), {"source_snapshot": {"vcs": "filesystem"}, "scope": {"allowed_paths": []}})
    require_test(
        (skipped["status"] == "Skipped" and not skipped["out_of_scope"]),
        "without a Git baseline the reconciliation must skip, not fail open on a guess",
    )
    # A baseline Git cannot resolve is the one way this check could quietly report
    # "nothing changed" and let a close through unchecked. It has to block instead.
    unverifiable = reconcile_scope(skill_root, {
        "source_snapshot": {"vcs": "git", "head_exists": True, "head": "0" * 40},
        "scope": {"allowed_paths": []},
    })
    require_test(
        (unverifiable["status"] == "Unverifiable" and unverifiable.get("reason")),
        f"an unresolvable Git baseline must block, not pass quietly; got {unverifiable.get('status')}",
    )

    condition_phrases = [
        row.split("|")[1].strip()
        for row in minimal_card.splitlines()
        if re.search(r"\| `[a-z_]+` \|", row)
    ]
    restated = [phrase for phrase in condition_phrases if phrase and phrase in skill_text]
    require_test(
        (len(restated) <= 1),
        f"SKILL.md must point at the eligibility projection, not restate it; restated: {restated}",
    )
    require_test(("scripts/get_context.py" in skill_text), "SKILL.md must route full-carrier context through get_context.py")
    require_test(("scripts/signals.py" in skill_text), "SKILL.md must route no-argument status through signals.py")
    require_test(("scripts/check_write_guard.py" in skill_text), "SKILL.md must document the write guard")
    source_map_text = (skill_root / "references" / "spec-source-map.md").read_text(encoding="utf-8")
    require_test(("Manifest 的44个受保护文件" in source_map_text), "self-test invariant failed at original line 454: 'Manifest 的44个受保护文件' in source_map_text")
    require_test(("retrieval-plan.json" in source_map_text), "self-test invariant failed at original line 455: 'retrieval-plan.json' in source_map_text")
    require_test(("发布信任根" in source_map_text), "spec-source-map must document the Git commit/tag publication trust root")
    # The tag name is written out in the trust-root section; hold it to the version
    # SKILL.md declares so the two cannot drift apart silently.
    require_test(
        (release_tag in source_map_text),
        f"spec-source-map must cite the release tag for the declared version ({release_tag})",
    )
    stale_tags = {
        tag for tag in re.findall(r"rgpw-v[0-9a-z.\-]+", source_map_text) if tag != release_tag
    }
    require_test(
        (not stale_tags),
        f"spec-source-map cites release tags that do not match metadata.version: {sorted(stale_tags)}",
    )
    require_test((not (skill_root / "references" / "platform-bootstrap.md").exists()), "platform bootstrap reference must be removed")
    require_test(("platform-bootstrap" not in skill_text), "SKILL.md must not route to platform bootstrap")
    require_test(("<skill-root>" in skill_text), "SKILL.md must distinguish skill-root from project-root")
    require_test(("<project-root>/.project-governance" in skill_text), "SKILL.md must place governance files under project-root")
    require_test(("assets/runtime/norms/" in source_map_text), "spec-source-map must map logical references/ paths to disk norms")
    require_test(((skill_root / "agents" / "openai.yaml").is_file()), "Codex skill metadata must remain")
    require_test((not (skill_root / "mappings").exists()), "self-test invariant failed at original line 456: not (skill_root / 'mappings').exists()")
    require_test((not (skill_root / "schemas").exists()), "self-test invariant failed at original line 457: not (skill_root / 'schemas').exists()")
    openai_yaml = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    short_match = re.search(r'^\s*short_description: "([^"]+)"$', openai_yaml, re.MULTILINE)
    prompt_match = re.search(r'^\s*default_prompt: "([^"]+)"$', openai_yaml, re.MULTILINE)
    require_test((short_match and 25 <= len(short_match.group(1)) <= 64), 'self-test invariant failed at original line 461: short_match and 25 <= len(short_match.group(1)) <= 64')
    require_test((prompt_match and "$run-governed-product-workflow" in prompt_match.group(1)), "self-test invariant failed at original line 462: prompt_match and '$run-governed-product-workflow' in prompt_match.group(1)")
    require_test((len(re.findall(r"[.!?。！？]", prompt_match.group(1))) == 1), "self-test invariant failed at original line 463: len(re.findall('[.!?。！？]', prompt_match.group(1))) == 1")
    require_test((not validate_embedded_manifest(skill_root)), 'self-test invariant failed at original line 464: not validate_embedded_manifest(skill_root)')
    manifest = read_json(embedded_manifest_path(skill_root))
    require_test((manifest["layout_version"] == "skill-runtime-v2"), "self-test invariant failed at original line 466: manifest['layout_version'] == 'skill-runtime-v2'")
    require_test((len(manifest["files"]) == sum(EXPECTED_MANIFEST_ROLES.values())), f"embedded manifest must hold {sum(EXPECTED_MANIFEST_ROLES.values())} files, found {len(manifest['files'])}")
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
    cache_prune_validation = run_cache_prune_fixture()
    write_guard_validation = run_write_guard_fixture()
    console_deployment_validation = run_console_deployment_fixture()
    require_test((retrieval_validation["manifest_files"] == 46), "self-test invariant failed at original line 518: retrieval_validation['manifest_files'] == 46")
    require_test((retrieval_validation["fixture_counts"] == {
        "positive": 8,
        "schema_negative": 21,
        "semantic_negative": 13,
    }), "self-test invariant failed at original line 519: retrieval_validation['fixture_counts'] == {'positive': 8, 'schema_negative': 21, 'semantic_negative': 13}")
    require_test((retrieval_validation["gold_case_count"] == 28), "self-test invariant failed at original line 524: retrieval_validation['gold_case_count'] == 28")
    require_test((retrieval_validation["mandatory_target_count"] == 12), "self-test invariant failed at original line 525: retrieval_validation['mandatory_target_count'] == 12")
    require_test((retrieval_validation["hard_gate_negative_count"] == 8), "self-test invariant failed at original line 526: retrieval_validation['hard_gate_negative_count'] == 8")
    gold_contracts = read_json(runtime_asset_path("evaluations/norm-retrieval-gold.json"))["compatibility_baselines"]["cli_help_contracts"]
    gold_contract_keys = {
        (item["script"], tuple(item.get("help_args", ["--help"])))
        for item in gold_contracts
    }
    require_test(
        ("query_norm_context.py", ("--help",)) in gold_contract_keys,
        "CLI compatibility closure must include query_norm_context.py",
    )
    require_test(
        ("manage_minimal_task.py", ("init", "--help")) in gold_contract_keys,
        "CLI compatibility closure must include manage_minimal_task.py init --help",
    )
    require_test(
        retrieval_validation["compatibility"]["cli_contract_count"] == len(gold_contracts),
        "CLI compatibility closure must execute every gold help contract",
    )
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
        == {"status": "Passed", "lifecycle": "single-file", "upgrade": "one-way", "defaults": "traceable"},
        "Minimal aggregate lifecycle and one-way upgrade must pass",
    )
    require_test((cache_prune_validation == {"status": "Passed", "checks": 5}), "runtime cache pruning fixture must pass")
    require_test((write_guard_validation == {"status": "Passed", "checks": 8}), "write guard fixture must pass")
    require_test((console_deployment_validation == {"status": "Passed", "checks": 12}), "console deployment fixture must pass")
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
    # S7 was the one stage with no test at all. A production release carries three
    # controls that would each fail open in silence if the mapping drifted: it must be
    # classified onto Deploy/Operations, it must declare the release-approval gate, and
    # an external effect needs the permission for it before the run can even start.
    release_profile = copy.deepcopy(union_profile)
    release_profile["applicability_facts"]["production_release"] = "Yes"
    release_profile["applicability_facts"]["external_system_effect"] = "Yes"
    release_profile["extension_triggers"]["E05"] = "Active"
    release_profile["extension_evidence_refs"]["E05"] = ["self-test://ops"]
    misclassified = resolve_tailoring(release_profile, stage="S7")
    require_test(
        (any("production_release=Yes requires one of change_surfaces: Deploy/Operations" in item
             for item in misclassified["blocking_reasons"])),
        f"a production release must be classified onto Deploy/Operations; got {misclassified['blocking_reasons']}",
    )
    release_profile["change_surfaces"] = ["Deploy/Operations"]
    release_contract = {
        "authority": {"required_gates": [], "execution_permissions": ["read", "edit-in-scope", "validate"]},
    }
    ungated = resolve_tailoring(release_profile, stage="S7", contract_context=release_contract)
    require_test(
        (any("release-approval" in item for item in ungated["blocking_reasons"])),
        f"a production release must declare the release-approval gate; got {ungated['blocking_reasons']}",
    )
    require_test(
        (any("external-effect" in item for item in ungated["blocking_reasons"])),
        f"an external effect needs its permission before the run starts; got {ungated['blocking_reasons']}",
    )
    released = resolve_tailoring(release_profile, stage="S7", contract_context={
        "authority": {"required_gates": ["release-approval"],
                      "execution_permissions": ["read", "edit-in-scope", "validate", "external-effect", "rollback"]},
    })
    require_test(
        ({"C11", "C12", "E05"} <= set(released["applicable_standards"])),
        f"a production release must activate C11, C12 and E05; got {released['applicable_standards']}",
    )

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
                request_snapshot={"language": "en", "text": "self-test fixture request", "captured_at": "2026-08-15T00:00:00Z"},
                requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test fixture request", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"]}],
                decisions=[
                    {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                    {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z"},
                ],
                clarification={"state": "Settled", "mode": "Skipped", "notice": "Scope is fully declared by the fixture; skipping the question round.", "survey_refs": ["self-test://survey"], "rounds": [], "basis": "self-test fixture"},
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
        decisions_file = write_fixture(
            "decisions.json",
            [
                {"id": "D-01", "kind": "Proceed", "presented": "范围与验收",
                 "response": "Proceed", "decided_by": "self-test",
                 "decided_at": "2026-08-15T00:00:00Z"},
                {"id": "D-02", "kind": "Acceptance", "presented": "验证结果",
                 "response": "接受", "decided_by": "self-test",
                 "decided_at": "2026-08-15T00:00:00Z"},
            ],
        )
        requirement_items_file = write_fixture(
            "requirement-items.json",
            [
                {"id": "R-01", "source": "request_snapshot",
                 "quote": "用 UTF-8 JSON 文件输入跑一遍自检",
                 "reading": "跑一遍 CLI 文件输入自检", "state": "Covered",
                 "evidence_refs": ["self-test://cli"]},
                {"id": "R-02", "source": "clarification:r1.e1",
                 "quote": "是，只覆盖文件输入",
                 "reading": "范围限定在文件输入路径", "state": "Covered",
                 "evidence_refs": ["self-test://cli"]},
            ],
        )
        clarification_file = write_fixture(
            "clarification.json",
            {
                "state": "Settled",
                "mode": "Asked",
                "notice": "针对你的需求和项目现状，有几个问题需要你先回答，以保证本需求完成的质量",
                "survey_refs": ["self-test://survey"],
                "rounds": [{
                    "ordinal": 1,
                    "asked_at": "2026-08-15T00:00:00Z",
                    "exchanges": [{
                        "question": "CLI 固件是否只覆盖 UTF-8 文件输入？",
                        "changes": "Scope",
                        "recommended_default": "只覆盖文件输入",
                        "answer": "是，只覆盖文件输入",
                        "answer_state": "Answered",
                    }],
                }],
                "basis": "勘察确认 CLI 固件仅走文件输入路径",
            },
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
            "--request-snapshot", "用 UTF-8 JSON 文件输入跑一遍自检",
            "--clarification-json-file", str(clarification_file),
            "--requirement-items-json-file", str(requirement_items_file),
            "--decisions-json-file", str(decisions_file),
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
        "cache_prune": cache_prune_validation,
        "write_guard": write_guard_validation,
        "console_deployment": console_deployment_validation,
        "positive": "passed",
        "negative": "passed",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
