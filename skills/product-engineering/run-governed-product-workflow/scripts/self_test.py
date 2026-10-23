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
    validate_survey_refs,
    reconcile_required_gates,
    current_tailoring,
    validate_tailoring_resolution,
    require_decision,
    approval_subject_sha256,
    validate_implemented_contract,
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
    amend_record_batch,
    append_run_event,
    capture_source_snapshot,
    close_task,
    default_profile_index_path,
    embedded_manifest_path,
    generate_views,
    initialize_task,
    load_tailoring_map,
    read_json,
    now_utc,
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
from audit_norm_retrieval import canonical_help, claim_mandatory_target_identity, validate_contracts
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
    record_minimal_review,
    minimal_approval_contract,
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


def fixture_discharge_items(contract: dict) -> list[dict]:
    """Synthetic data for lifecycle plumbing tests, not evidence of a product review."""
    from governance_artifacts import _requirement_source_texts
    sources = dict(_requirement_source_texts(contract))
    items = copy.deepcopy(contract["requirement_items"])
    for item in items:
        if item["state"] == "Covered":
            item["review"] = {"source_sha256": hashlib.sha256(sources[item["source"]].encode("utf-8")).hexdigest(),
                              "conditions": [], "cases": [{"condition": None, "branch": "Unconditional",
                              "input": "synthetic lifecycle fixture", "expected": "fixture check passes",
                              "actual": "fixture check passes", "result": "Passed", "evidence_refs": ["self-test://simulated-review"]}]}
    return items


def record_fixture_acceptance(task_dir: Path) -> None:
    """Simulate a human answer only after a lifecycle fixture has verified delivery."""
    from governance_artifacts import read_jsonl
    full = (task_dir / "before.json").is_file()
    record = read_json(task_dir / ("before.json" if full else "task-record.json"))
    contract = record if full else minimal_approval_contract(record)
    events = read_jsonl(task_dir / "run.jsonl") if full else record["run_ledger"]
    decision = {"id": "D-FIXTURE-ACCEPT", "kind": "Acceptance", "presented": "verified synthetic fixture delivery",
                "response": "accepted", "outcome": "Approved", "decided_by": "self-test",
                "decided_at": now_utc(), "evidence_ref": "self-test://simulated-human-answer",
                "subject_sha256": approval_subject_sha256(contract, events)}
    items = fixture_discharge_items(contract)
    if full:
        amend_record_batch(task_dir / "before.json", changes=[{"path": "decisions", "value": contract["decisions"] + [decision]},
            {"path": "requirement_items", "value": items}], reason="simulate post-verification acceptance", basis="self-test fixture only")
    else:
        record_minimal_review(task_dir, decisions=[decision], requirement_items=items,
                              reason="simulate post-verification acceptance", basis="self-test fixture only")


def run_historical_proof_compatibility_fixture() -> dict[str, object]:
    """Exercise read compatibility and strict future actions in isolated carriers."""
    from governance_artifacts import (PROOF_CONTRACT_VERSION, PROOF_CONTRACT_EFFECTIVE_AT,
                                     proof_validation_for_read, read_jsonl, _set_dotted_path)
    import console_render
    checks = 0

    def check(condition, message):
        nonlocal checks
        require_test(condition, message)
        checks += 1

    old = "2026-09-01T00:00:00Z"
    with tempfile.TemporaryDirectory(prefix="v63-proof-history-") as temp:
        root = Path(temp).resolve()
        task = new_task(root, "T-HISTORICAL-FULL", 1)
        before = read_json(task / "before.json")
        check(before["proof_contract_version"] == PROOF_CONTRACT_VERSION, "new Full factories must stamp the current proof contract")
        before.pop("proof_contract_version")
        before.update(created_at=old, frozen_at=old, lifecycle_state="Frozen", decisions=[], amendments=[])
        events = [{"schema_version": "6.3-candidate", "meta_type": "RunLedger", "event_id": f"RUN-HIST-E{i}",
                   "project_id": "P-TEST", "task_id": before["task_id"], "run_id": "RUN-HIST", "attempt_id": "A01",
                   "sequence": i, "timestamp": old, "event_type": kind, "summary": "synthetic pre-cutover fact",
                   "status": status, "exit_code": None, "evidence_refs": [], "side_effects": [], "redactions": []}
                  for i, (kind, status) in enumerate([("run_started", "started"), ("run_finished", "succeeded")], 1)]
        terminal_manifest = copy.deepcopy(before["artifact_manifest"])
        for item in terminal_manifest:
            item["outcome"] = "Created" if item["meta_type"] == "TaskOutcome" else "Revised"
        after = {"schema_version": "6.3-candidate", "meta_type": "TaskOutcome", "project_id": "P-TEST",
                 "work_item_id": before["work_item_id"], "task_id": before["task_id"], "revision": 1,
                 "status": "Implemented", "completed_at": old, "source_snapshot": {"kind": "synthetic historical fixture"},
                 "established_facts": ["Historical completion was recorded before the new proof contract"],
                 "actual_changes": [], "verification": [], "incomplete_items": [], "legacy_issues": [],
                 "decisions": [], "evidence_refs": [], "next_tasks": [], "artifact_manifest": terminal_manifest, "amendments": []}

        def save_full(contract, ledger, outcome):
            atomic_write_json(task / "before.json", contract)
            (task / "run.jsonl").write_text("".join(json.dumps(item) + "\n" for item in ledger), encoding="utf-8")
            atomic_write_json(task / "after.json", outcome)

        save_full(before, events, after)
        check(not validate_task_directory(task), "historical Full completion must remain readable without fabricated new proof")
        check(proof_validation_for_read(before, events, after)[0]["status"] == "HistoricalNotRevalidated", "historical read must be explicitly distinct from current proof passing")
        for field in ("created_at", "frozen_at"):
            changed = copy.deepcopy(before)
            changed[field] = PROOF_CONTRACT_EFFECTIVE_AT
            projection, errors = proof_validation_for_read(changed, events, after)
            check(projection["status"] != "HistoricalNotRevalidated" and errors, f"deleting a marker cannot downgrade a new {field}")
        changed_after = copy.deepcopy(after)
        changed_after["completed_at"] = PROOF_CONTRACT_EFFECTIVE_AT
        check(proof_validation_for_read(before, events, changed_after)[1], "new close time cannot inherit historical read exemption")
        changed_events = copy.deepcopy(events)
        changed_events[0]["timestamp"] = PROOF_CONTRACT_EFFECTIVE_AT
        check(proof_validation_for_read(before, changed_events, after)[1], "new Run timestamp cannot inherit historical read exemption")
        for marker in ("implemented-proof-v0", None):
            changed = copy.deepcopy(before)
            changed["proof_contract_version"] = marker
            check(proof_validation_for_read(changed, events, after)[1], "unknown and null policy markers must fail closed")
        for owner, field, value in [("before", "proof_contract_version", PROOF_CONTRACT_VERSION),
                                    ("after", "scope_reconciliation", {})]:
            b, a = copy.deepcopy(before), copy.deepcopy(after)
            (b if owner == "before" else a)[field] = value
            save_full(b, events, a)
            check(validate_task_directory(task), "current proof signals must run full current validation even on old dates")
        save_full(before, events, after)

        mini_path = create_minimal_record(root, project_id="P-TEST", work_item_id="W-HIST-MIN", task_id="T-HISTORICAL-MIN",
            ordinal=2, depends_on=[], supersedes=[], objective="Synthetic historical Minimal fixture",
            request_snapshot={"language": "en", "text": "Synthetic historical Minimal fixture", "captured_at": old},
            clarification=copy.deepcopy(before["clarification"]), requirement_items=[{
                "id": "R-01", "source": "request_snapshot", "quote": "Synthetic historical Minimal fixture",
                "reading": "synthetic fixture", "state": "Covered", "evidence_refs": ["self-test://historical"], "acceptance_refs": [0]}],
            decisions=[], scope="one local fixture", acceptance="the local fixture reads", delivery_scenario="DS-03",
            development_type="DT-08", change_surface="UI/UX", selected_approach="read the local fact",
            alternative_rejected="rewrite historical approvals", plan_steps=["read the local fact"], verification="read the local fact",
            rollback="discard the isolated directory", allowed_paths=["label.txt"], out_of_scope=[], forbidden_actions=[],
            selection_source="automatic", basis=["synthetic compatibility fixture"], authority_refs=["self-test://authority"],
            eligibility_evidence_refs=[f"self-test://eligibility-{i}" for i in range(7)], facts=[], constraints=[], assumptions=[],
            fundamentals=[], causal_chain=[], decision_criteria=[])
        mini = read_json(mini_path)
        check(mini["proof_contract_version"] == PROOF_CONTRACT_VERSION, "new Minimal factories must stamp the current proof contract")
        mini.pop("proof_contract_version")
        mini.update(created_at=old, completed_at=old, lifecycle_state="Completed", amendments=[])
        mini["run_ledger"] = [{"sequence": i, "timestamp": old, "event_type": kind, "summary": "synthetic pre-cutover fact",
                               "status": status, "evidence_refs": []}
                              for i, (kind, status) in enumerate([("run_started", "started"), ("run_finished", "succeeded")], 1)]
        mini["task_outcome"] = {"status": "Implemented", "established_facts": ["historical Minimal fact"], "actual_changes": [],
                                "verification": [{"result": "Passed", "summary": "historical check", "evidence_refs": []}],
                                "incomplete_items": [], "completed_at": old}
        for item in mini["artifact_manifest"]:
            item["outcome"] = "Created"
        atomic_write_json(mini_path, mini)
        check(not validate_minimal_record(mini, task_dir=mini_path.parent), "historical Minimal must preserve its pre-cutover controls")
        changed = copy.deepcopy(mini)
        changed["completed_at"] = changed["task_outcome"]["completed_at"] = PROOF_CONTRACT_EFFECTIVE_AT
        check(validate_minimal_record(changed, task_dir=mini_path.parent), "new Minimal completion cannot downgrade by omitting its marker")

        files = [task / "before.json", task / "run.jsonl", task / "after.json", mini_path]
        original_bytes = {str(path): path.read_bytes() for path in files}
        state = read_json(rebuild_project_state(root, "P-TEST"))
        check(len(state["source_tasks"]) == 2 and all(item["status"] == "Implemented" for item in state["source_tasks"]),
              "mixed historical carriers must retain their original statuses in a real aggregate")
        check(all(item["proof_validation"]["status"] == "HistoricalNotRevalidated" for item in state["source_tasks"]),
              "ProjectState must expose historical proof classification for both carriers")
        outputs = generate_views(root, project_id="P-TEST", profile_index=default_profile_index_path())
        status_page = root / ".project-governance/generated/reviews/project-status.md"
        check(outputs and "未追溯验证新增证明" in status_page.read_text(encoding="utf-8"), "generated status must explain historical proof limits")
        model = console_model.scan(root)
        check("未追溯验证新增证明" in console_render.page_task(model, before["task_id"]), "console task details must explain historical proof limits")
        check(all(path.read_bytes() == original_bytes[str(path)] for path in files), "read validation and aggregation must not rewrite historical carrier bytes")

        (task / "after.json").unlink()
        (task / "run.jsonl").write_text(json.dumps(events[0]) + "\n", encoding="utf-8")
        expect_governance_error("historical Full new action needs explicit policy adoption", lambda: append_run_event(task,
            run_id="RUN-HIST", attempt_id="A01", event_type="mutation", summary="new action", status="succeeded"))
        checks += 1
        adopted = amend_record(task / "before.json", dotted_path="proof_contract_version", new_value=PROOF_CONTRACT_VERSION,
                               reason="explicit isolated policy adoption", basis="self-test only", allow_add=True)
        check(adopted["amendments"][-2 if adopted["amendments"][-1]["path"] == "tailoring_resolution" else -1]["path"] == "proof_contract_version",
              "Full policy adoption must carry an amendment trail")
        expect_governance_error("adoption does not fabricate Full Proceed", lambda: append_run_event(task,
            run_id="RUN-HIST", attempt_id="A01", event_type="mutation", summary="new action", status="succeeded"))
        checks += 1
        for value in (None, "implemented-proof-v0", PROOF_CONTRACT_VERSION):
            expect_governance_error("existing policy marker is immutable", lambda v=value: _set_dotted_path(adopted, "proof_contract_version", v, allow_add=True))
            checks += 1

        mini.update(completed_at=None, lifecycle_state="Frozen", task_outcome=None)
        mini["run_ledger"] = mini["run_ledger"][:1]
        for item in mini["artifact_manifest"]:
            item["outcome"] = "Planned"
        atomic_write_json(mini_path, mini)
        expect_governance_error("historical Minimal new action needs policy adoption", lambda: append_minimal_event(mini_path.parent,
            event_type="mutation", summary="new action", status="succeeded"))
        checks += 1
        record_minimal_review(mini_path.parent, adopt_proof_contract=True, reason="explicit isolated adoption", basis="self-test only")
        check(read_json(mini_path)["proof_contract_version"] == PROOF_CONTRACT_VERSION, "Minimal official review must support explicit recorded adoption")
        expect_governance_error("adoption does not fabricate Minimal Proceed", lambda: append_minimal_event(mini_path.parent,
            event_type="mutation", summary="new action", status="succeeded"))
        checks += 1

        # A real cutover can interrupt an active run: the record lacks a marker
        # while its already-recorded events are newer than the policy boundary.
        pending = copy.deepcopy(mini)
        pending["run_ledger"][0]["timestamp"] = PROOF_CONTRACT_EFFECTIVE_AT
        atomic_write_json(mini_path, pending)
        check(bool(validate_minimal_record(pending, task_dir=mini_path.parent)),
              "unadopted post-cutover records must still fail ordinary validation")
        record_minimal_review(mini_path.parent, adopt_proof_contract=True,
                              reason="recover interrupted cutover", basis="isolated real-boundary regression")
        migrated = read_json(mini_path)
        check(not validate_minimal_record(migrated, task_dir=mini_path.parent),
              "explicit migration must fully validate its current-policy candidate")
        check(migrated["task_contract"] == pending["task_contract"] and migrated["run_ledger"] == pending["run_ledger"],
              "migration must preserve original requests, human decisions and every historical event")
        check(migrated["amendments"][:-1] == pending["amendments"] and
              migrated["amendments"][-1]["changes"] == [{"path": "proof_contract_version",
              "old_value": {"$missing": True}, "new_value": PROOF_CONTRACT_VERSION}],
              "migration must append exactly its explicit policy adoption amendment")
        expect_governance_error("migration never supplies Acceptance", lambda: close_minimal_record(mini_path.parent,
            status="Implemented", established_facts=["fixture"], actual_changes=[], verification=["Passed::fixture::self-test://fixture"]))
        checks += 1

        malformed = []
        broken = copy.deepcopy(pending)
        broken["run_ledger"][0]["sequence"] = 2
        malformed.append(broken)
        broken = copy.deepcopy(pending)
        broken["task_id"] = "T-OTHER-ID"
        malformed.append(broken)
        broken = copy.deepcopy(pending)
        del broken["task_contract"]
        malformed.append(broken)
        malformed.append(json.loads(original_bytes[str(mini_path)]))  # Valid, closed legacy history.
        for marker in (None, "implemented-proof-v0", PROOF_CONTRACT_VERSION):
            broken = copy.deepcopy(pending)
            broken["proof_contract_version"] = marker
            malformed.append(broken)
        for invalid in malformed:
            atomic_write_json(mini_path, invalid)
            unchanged = mini_path.read_bytes()
            expect_governance_error("adoption cannot repair unrelated corruption, reopen history or replace a marker",
                lambda: record_minimal_review(mini_path.parent, adopt_proof_contract=True, reason="fixture", basis="fixture"))
            check(mini_path.read_bytes() == unchanged, "rejected adoption must not rewrite its input bytes")
        atomic_write_json(mini_path, migrated)
    return {"status": "passed", "checks": checks}


def run_verification_recovery_fixture() -> dict[str, object]:
    """Recovery preserves actual chronology and refuses stale or unsupported evidence."""
    from datetime import datetime, timezone
    checks = 0
    with tempfile.TemporaryDirectory(prefix="v63-verification-recovery-") as temp:
        root = Path(temp)
        record_path = minimal_fixture_record(root, "T-RECOVERY")
        task_dir = record_path.parent
        append_minimal_event(task_dir, event_type="run_started", summary="fixture run", status="started")
        source = root / "label.txt"
        proof = root / "test.log"
        source.write_text("verified fixture source", encoding="utf-8")
        proof.write_text("synthetic test passed", encoding="utf-8")
        receipt = {"verified_at": datetime.now(timezone.utc).isoformat(), "summary": "recover synthetic check",
                   "result": "Passed", "source_files": [{"path": "label.txt", "sha256": sha256_file(source)}],
                   "evidence_files": [{"path": "test.log", "sha256": sha256_file(proof)}]}
        original = read_json(record_path)
        before_bytes = record_path.read_bytes()
        bad_receipts = []
        for field, value in [("result", "Failed"), ("verified_at", "2099-01-01T00:00:00Z"),
                             ("verified_at", "2000-01-01T00:00:00Z"), ("verified_at", "2026-01-01T00:00:00"),
                             ("source_files", []), ("evidence_files", [])]:
            changed = copy.deepcopy(receipt)
            changed[field] = value
            bad_receipts.append(changed)
        for field, value in [("path", "../outside.log"), ("sha256", "0" * 64)]:
            changed = copy.deepcopy(receipt)
            changed["source_files"][0][field] = value
            bad_receipts.append(changed)
        changed = copy.deepcopy(receipt)
        changed["source_files"].append(changed["source_files"][0])
        bad_receipts.append(changed)
        for invalid in bad_receipts:
            expect_governance_error("recovery rejects unsupported evidence without writing",
                lambda: record_minimal_review(task_dir, verification_receipt=invalid, reason="fixture", basis="fixture"))
            require_test(record_path.read_bytes() == before_bytes, "failed recovery changed the record")
            checks += 1
        source_time = source.stat().st_mtime_ns
        os.utime(source, ns=(source_time + 10_000_000_000, source_time + 10_000_000_000))
        expect_governance_error("source modified after verification invalidates recovery",
            lambda: record_minimal_review(task_dir, verification_receipt=receipt, reason="fixture", basis="fixture"))
        os.utime(source, ns=(source_time, source_time))
        checks += 1
        record_minimal_review(task_dir, verification_receipt=receipt, reason="restore actual verification", basis="self-test only")
        recovered = read_json(record_path)
        require_test(recovered["run_ledger"][:-1] == original["run_ledger"], "recovery rewrote historical events")
        require_test(recovered["run_ledger"][-1]["timestamp"] == receipt["verified_at"], "recovery redated the check")
        require_test(datetime.fromisoformat(recovered["amendments"][-1]["changed_at"].replace("Z", "+00:00"))
                     >= datetime.fromisoformat(receipt["verified_at"]),
                     "recovery did not retain its later recording time")
        checks += 3
        expect_governance_error("recovery cannot replace an existing verification",
            lambda: record_minimal_review(task_dir, verification_receipt=receipt, reason="fixture", basis="fixture"))
        checks += 1
        subject = approval_subject_sha256(minimal_approval_contract(recovered), recovered["run_ledger"])
        old_answer = copy.deepcopy(recovered["task_contract"]["decisions"][-1])
        old_answer.update(id="D-EARLY", subject_sha256=subject)
        record_minimal_review(task_dir, decisions=[old_answer],
            requirement_items=fixture_discharge_items(recovered["task_contract"]), reason="fixture", basis="fixture")
        close_minimal_record(task_dir, status="Implemented", established_facts=["fixture"],
                             actual_changes=[], verification=["Passed::fixture::test.log"])
        saved = read_json(record_path)
        require_test(saved["task_outcome"]["user_decision"] == {"outcome": "Pending"},
                     "recovered engineering result must be saved without treating an early answer as valid acceptance")
        checks += 1
        old_answer.update(id="D-VALID", decided_at=datetime.now(timezone.utc).isoformat())
        from governance_artifacts import user_decision_subject_sha256
        later = {key: old_answer[key] for key in ("outcome", "presented", "response", "decided_by", "decided_at", "evidence_ref")}
        later["subject_sha256"] = user_decision_subject_sha256(minimal_approval_contract(saved), saved["run_ledger"], saved["task_outcome"])
        record_minimal_review(task_dir, user_decision=later, reason="synthetic later answer", basis="self-test only")
        require_test(not validate_minimal_record(read_json(record_path), task_dir=task_dir), "recovered task did not close validly")
        checks += 1
    return {"status": "Passed", "checks": checks}


def run_closed_scope_history_fixture() -> dict[str, object]:
    """Closed scope binds its original delivery, not later unrelated Git changes."""
    from governance_artifacts import read_jsonl

    checks = 0

    def check(condition, message: str) -> None:
        nonlocal checks
        require_test(condition, message)
        checks += 1

    with tempfile.TemporaryDirectory(prefix="v63-closed-scope-history-") as temp:
        root = Path(temp).resolve()

        def git(*args: str) -> str:
            result = subprocess.run(
                ["git", "-c", "user.name=Workflow Self Test", "-c", "user.email=workflow-self-test@example.invalid",
                 "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={root / '.git' / 'fixture-hooks'}", *args],
                cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            require_test(result.returncode == 0, f"isolated git {args}: {result.stdout}{result.stderr}")
            return result.stdout.strip()

        (root / "a.txt").write_text("a baseline\n", encoding="utf-8")
        (root / "b.txt").write_text("b baseline\n", encoding="utf-8")
        (root / "surveyed.md").write_text("surveyed by the conformance fixture\n", encoding="utf-8")
        git("init")
        git("add", "--", "a.txt", "b.txt", "surveyed.md")
        git("commit", "-m", "isolated closed-scope baseline")
        baseline = capture_source_snapshot(root)
        check(baseline.get("vcs") == "git" and baseline.get("head_exists")
              and baseline.get("head") == git("rev-parse", "HEAD"), "scope fixture requires a reachable real Git baseline")

        task = new_task(root, "T-CLOSED-SCOPE-HISTORY", 1)
        amend_record_batch(task / "before.json", changes=[
            {"path": "scope.allowed_paths", "value": ["a.txt"]},
            {"path": "source_snapshot", "value": baseline},
        ], reason="bind the isolated task to its actual Git baseline and sole edited file", basis="self-test fixture")
        append_run_event(task, run_id="RUN-CLOSED-SCOPE", attempt_id="A01", event_type="run_started",
                         summary="Start isolated a.txt task", status="started")
        (root / "a.txt").write_text("a verified delivery\n", encoding="utf-8")
        append_run_event(task, run_id="RUN-CLOSED-SCOPE", attempt_id="A01", event_type="mutation",
                         summary="Edit only a.txt", status="succeeded", evidence_refs=["self-test://a-change"])
        append_run_event(task, run_id="RUN-CLOSED-SCOPE", attempt_id="A01", event_type="verification",
                         summary="Verify a.txt delivery", status="succeeded", evidence_refs=["self-test://a-verified"])
        record_fixture_acceptance(task)
        contract = read_json(task / "before.json")
        subject = approval_subject_sha256(contract, read_jsonl(task / "run.jsonl"))
        append_run_event(task, run_id="RUN-CLOSED-SCOPE", attempt_id="A01", event_type="human_gate",
                         summary="Independent synthetic review passed", status="succeeded",
                         evidence_refs=["self-test://closed-scope-independent-review"], gate={
                             "id": "independent-review", "outcome": "Passed", "subject_sha256": subject,
                             "decided_by": "synthetic-independent-reviewer", "decided_at": now_utc(),
                             "authority_ref": "self-test://authority"})
        append_run_event(task, run_id="RUN-CLOSED-SCOPE", attempt_id="A01", event_type="run_finished",
                         summary="Complete isolated a.txt task", status="succeeded")
        after_path = close_task(task, status="Implemented", established_facts=["a.txt matches its verified delivery"],
                                actual_changes=["Changed only a.txt"], verification=[{
                                    "summary": "a.txt verified", "result": "Passed", "required": True,
                                    "evidence_refs": ["self-test://a-verified"]}])
        check(read_json(after_path)["scope_reconciliation"]["status"] == "Passed",
              "close must generate Passed frozen scope evidence from the real Git baseline")
        check(not validate_task_directory(task), "the legitimately closed isolated task must validate")
        before_bytes = (task / "before.json").read_bytes()
        ledger_bytes = (task / "run.jsonl").read_bytes()
        after_bytes = after_path.read_bytes()

        (root / "b.txt").write_text("unrelated later task delivery\n", encoding="utf-8")
        live = reconcile_scope(root, contract)
        check(live["status"] == "Failed" and "b.txt" in live["out_of_scope"],
              "the later b.txt change must really be outside the old task's a.txt-only scope")
        check(not validate_task_directory(task), "future b.txt work cannot retroactively invalidate a closed a.txt task")
        state = read_json(rebuild_project_state(root, "P-TEST"))
        check(any(item["task_id"] == "T-CLOSED-SCOPE-HISTORY" and item["status"] == "Implemented"
                  for item in state["source_tasks"]), "rebuilding the project must retain the valid closed task after future work")

        for label, mutate in (
            ("missing", lambda item: item.pop("scope_reconciliation")),
            ("baseline", lambda item: item["scope_reconciliation"].update(baseline_sha256="0" * 64)),
            ("delivery", lambda item: item["scope_reconciliation"].update(delivery_sha256="0" * 64)),
            ("failed", lambda item: item["scope_reconciliation"].update(status="Failed")),
            ("out-of-scope", lambda item: item["scope_reconciliation"].update(out_of_scope=["outside.txt"])),
            ("changed-count", lambda item: item["scope_reconciliation"].update(changed_count=0)),
        ):
            invalid = json.loads(after_bytes)
            mutate(invalid)
            atomic_write_json(after_path, invalid)
            try:
                check(any("scope_reconciliation" in error for error in validate_task_directory(task)),
                      f"hand-written {label} scope evidence must be rejected")
            finally:
                after_path.write_bytes(after_bytes)
        invalid_before = json.loads(before_bytes)
        invalid_before["scope"]["allowed_paths"].append("b.txt")
        atomic_write_json(task / "before.json", invalid_before)
        try:
            check(any("scope_reconciliation" in error for error in validate_task_directory(task)),
                  "changing the old contract's scope must invalidate the frozen close-time evidence")
        finally:
            (task / "before.json").write_bytes(before_bytes)
        check(not validate_task_directory(task), "restoring the original closed bytes must restore validity")
        check((task / "before.json").read_bytes() == before_bytes and (task / "run.jsonl").read_bytes() == ledger_bytes
              and after_path.read_bytes() == after_bytes, "historical validation must preserve the original contract, ledger and outcome")
    return {"status": "Passed", "checks": checks}


def run_approval_time_fixture() -> dict[str, object]:
    """Synthetic in-memory approval contracts; no real human approval is asserted."""
    quote = "Confirm this exact verified delivery."
    before = {
        "schema_version": "6.3-candidate", "meta_type": "TaskContract", "task_id": "T-APPROVAL-TIME",
        "project_id": "P-APPROVAL-TIME", "objective": quote,
        "request_snapshot": {"language": "en", "text": quote, "captured_at": "2026-01-01T00:00:00Z"},
        "clarification": {"state": "Settled", "mode": "Skipped", "notice": "Synthetic approval-time fixture is unambiguous.",
                          "survey_refs": ["self-test://approval-time-survey"], "rounds": [], "reopened_by": []},
        "requirement_items": [{"id": "R-01", "source": "request_snapshot", "quote": quote, "reading": quote,
                               "state": "Covered", "acceptance_refs": [0], "evidence_refs": ["self-test://verified-delivery"]}],
        "scope": {"in_scope": ["approved fixture scope"], "out_of_scope": ["production"],
                  "allowed_paths": ["fixture.py"], "forbidden_actions": ["deploy"]},
        "acceptance": {"criteria": ["The verified synthetic fixture has the expected output."]},
        "source_snapshot": {"root": "self-test://approval-time-source", "head": "verified-fixture-revision"},
        "authority": {"required_gates": ["security-review"], "authority_references": ["self-test://reviewer-authority"],
                      "authority_assessments": [{"reference": "self-test://reviewer-authority", "status": "Valid",
                          "scope_refs": ["approved fixture scope"], "evidence_refs": ["self-test://authority-evidence"],
                          "verified_at": "2026-01-01T00:00:00Z", "expires_at": None}]},
        "decisions": [{"id": "D-PROCEED", "kind": "Proceed", "presented": "Synthetic fixture scope and acceptance",
                       "response": "Proceed", "outcome": "Approved", "decided_by": "synthetic-user",
                       "decided_at": "2026-01-01T01:00:00Z", "evidence_ref": "self-test://simulated-proceed"}],
    }
    before["requirement_items"] = fixture_discharge_items(before)

    def event(sequence: int, kind: str, timestamp: str, status: str, evidence: str) -> dict:
        return {"schema_version": "6.3-candidate", "meta_type": "RunLedger", "project_id": before["project_id"],
                "task_id": before["task_id"], "run_id": "RUN-APPROVAL-TIME", "attempt_id": "A01",
                "event_id": f"APPROVAL-TIME-E{sequence}", "sequence": sequence, "timestamp": timestamp,
                "event_type": kind, "summary": f"Synthetic {kind}", "status": status,
                "evidence_refs": [evidence], "side_effects": [], "redactions": []}

    events = [event(1, "run_started", "2026-01-02T06:00:00Z", "started", "self-test://simulated-proceed"),
              event(2, "verification", "2026-01-02T07:00:00Z", "succeeded", "self-test://verified-delivery")]

    def gate(contract: dict, decided_at: str, recorded_at: str) -> dict:
        value = event(3, "human_gate", recorded_at, "succeeded", "self-test://simulated-gate")
        value["gate"] = {"id": "security-review", "outcome": "Passed",
                         "subject_sha256": approval_subject_sha256(contract, events),
                         "decided_by": "synthetic-reviewer", "decided_at": decided_at,
                         "authority_ref": "self-test://reviewer-authority"}
        return value

    require_test(reconcile_required_gates(before, events + [gate(before, "2026-01-01T01:00:00Z", "2026-01-02T07:30:00Z")]),
                 "a gate decided before the verified delivery cannot approve its new subject")
    valid = copy.deepcopy(before)
    valid["authority"]["authority_assessments"][0]["expires_at"] = "2026-01-02T08:00:00Z"
    require_test(not reconcile_required_gates(valid, events + [gate(valid, "2026-01-02T15:00:00+08:00", "2026-01-02T15:30:00+08:00")]),
                 "UTC+08:00 gate recorded at 07:30 UTC must precede 08:00 UTC expiry")
    expired = copy.deepcopy(before)
    expired["authority"]["authority_assessments"][0]["expires_at"] = "2026-01-02T15:00:00+08:00"
    require_test(reconcile_required_gates(expired, events + [gate(expired, "2026-01-02T07:15:00Z", "2026-01-02T07:30:00Z")]),
                 "UTC gate recorded at 07:30 must not use authority expired at 15:00 UTC+08:00")

    minimal = {"task_id": "T-APPROVAL-MINIMAL", "project_id": before["project_id"], "task_contract": {
        "objective": quote, "request_snapshot": before["request_snapshot"], "scope": "one local label",
        "allowed_paths": ["ui/label.txt"], "out_of_scope": ["permissions"], "forbidden_actions": ["deploy"],
        "acceptance": "The label matches the expected value.", "source_snapshot": before["source_snapshot"]}}
    subject = approval_subject_sha256(minimal_approval_contract(minimal), events)
    for field, replacement in (("allowed_paths", ["server/auth.py"]), ("out_of_scope", []), ("forbidden_actions", [])):
        changed = copy.deepcopy(minimal)
        changed["task_contract"][field] = replacement
        require_test(approval_subject_sha256(minimal_approval_contract(changed), events) != subject,
                     f"changing Minimal {field} must invalidate the prior approval subject")

    good = copy.deepcopy(before)
    good["decisions"].append({"id": "D-ACCEPT", "kind": "Acceptance", "presented": "Verified synthetic delivery",
        "response": "Accepted", "outcome": "Approved", "decided_by": "synthetic-user",
        "decided_at": "2026-01-02T07:45:00Z", "evidence_ref": "self-test://simulated-acceptance",
        "subject_sha256": approval_subject_sha256(good, events)})
    finished = events + [gate(good, "2026-01-02T07:15:00Z", "2026-01-02T07:30:00Z"),
                        event(4, "run_finished", "2026-01-02T08:00:00Z", "succeeded", "self-test://verified-delivery")]
    checks = [{"summary": "Verified synthetic delivery", "result": "Passed", "required": True,
               "evidence_refs": ["self-test://verified-delivery"]}]
    require_test(not validate_implemented_contract(good, finished, checks),
                 "complete current acceptance, authority, gate, discharge and verification must pass the terminal invariant")
    old = copy.deepcopy(good)
    old["decisions"][-1]["decided_at"] = "2026-01-01T01:00:00Z"
    errors = validate_implemented_contract(old, finished, checks)
    require_test(len(errors) == 1 and "Acceptance" in errors[0],
                 f"only the stale Acceptance time must reject an otherwise valid terminal contract: {errors}")
    return {"status": "Passed", "checks": 8}


def run_review_boundary_regressions_fixture() -> dict[str, object]:
    checks = 0
    verification = {"event_type": "verification", "status": "succeeded", "timestamp": "2026-01-01T00:00:00Z",
                    "summary": "verified immutable delivery", "evidence_refs": ["sha256://verified-delivery-v1"]}
    before = {"task_id": "T-REVIEW-BOUNDARIES", "objective": "fixture", "request_snapshot": {"text": "fixture"},
              "scope": {"in_scope": ["fixture"], "allowed_paths": ["a.txt"]},
              "authority": {"required_gates": ["review"], "authority_assessments": [{"reference": "fixture://authority",
                 "status": "Valid", "scope_refs": ["fixture"], "evidence_refs": ["fixture://source"],
                 "verified_at": "2025-12-01T00:00:00Z", "expires_at": None}]}}
    subject = approval_subject_sha256(before, [verification])
    repeated = {**verification, "timestamp": "2026-01-01T00:03:00Z", "summary": "same delivery checked again"}
    require_test(approval_subject_sha256(before, [verification, repeated]) == subject,
                 "same immutable delivery without an intervening material event reuses its approval anchor")
    require_test(approval_subject_sha256(before, [verification, {**repeated, "evidence_refs": ["sha256://v2"]}]) != subject,
                 "a different evidenced delivery invalidates prior approval")
    checks += 2
    for kind in ("mutation", "failure", "retry", "rollback", "external_effect"):
        require_test(approval_subject_sha256(before, [verification, {"event_type": kind}, repeated]) != subject,
                     f"{kind} invalidates the old verified-delivery anchor")
        checks += 1
    require_test(approval_subject_sha256(before, [verification, {**repeated, "status": "failed"}, repeated]) != subject,
                 "a failed verification invalidates the old approval even if later evidence refs are reused")
    checks += 1

    def decision(outcome, time):
        return {"id": outcome + time, "kind": "Acceptance", "outcome": outcome, "response": outcome,
                "presented": "fixture delivery", "decided_by": "fixture-user", "decided_at": time,
                "evidence_ref": "fixture://real-simulated-answer", "subject_sha256": subject}
    approved = decision("Approved", "2026-01-01T00:01:00Z")
    rejected = decision("Rejected", "2026-01-01T00:02:00Z")
    for denial in (rejected, {**rejected, "outcome": "Deferred"}):
        require_test(require_decision({**before, "decisions": [denial, approved]}, "Acceptance", "close", subject_sha256=subject),
                     "late recording of an older approval cannot hide a later refusal or deferral")
        checks += 1
    require_test(require_decision({**before, "decisions": [approved, {**rejected, "decided_at": approved["decided_at"]}]},
                                 "Acceptance", "close", subject_sha256=subject), "equal-time contradictory answers fail closed")
    newest = {**approved, "id": "D-NEWEST", "decided_at": "2026-01-01T08:03:00+08:00"}
    require_test(not require_decision({**before, "decisions": [rejected, approved, newest]}, "Acceptance", "close", subject_sha256=subject),
                 "an actual newer affirmative answer resolves the refusal using UTC decision time")
    require_test(not require_decision({**before, "decisions": [approved]}, "Acceptance", "close",
                                     subject_sha256=approval_subject_sha256(before, [verification, repeated])),
                 "same-delivery re-verification does not demand repeated acceptance")
    checks += 3

    def gate(outcome, time):
        return {"event_type": "human_gate", "status": "succeeded", "timestamp": "2026-01-01T00:05:00Z",
                "summary": "fixture gate", "evidence_refs": ["fixture://gate-source"],
                "gate": {"id": "review", "outcome": outcome, "subject_sha256": subject,
                         "decided_by": "fixture-reviewer", "decided_at": time, "authority_ref": "fixture://authority"}}
    passed = gate("Passed", "2026-01-01T00:01:00Z")
    failed = gate("Failed", "2026-01-01T00:02:00Z")
    for denial in (failed, gate("Pending", "2026-01-01T00:02:00Z")):
        require_test(reconcile_required_gates(before, [verification, denial, passed]), "older Passed gate cannot hide later failure/pending")
        checks += 1
    conflict = gate("Failed", "2026-01-01T00:01:00Z")
    require_test(reconcile_required_gates(before, [verification, passed, conflict]), "equal-time contradictory gates fail closed")
    require_test(not reconcile_required_gates(before, [verification, passed, conflict, gate("Passed", "2026-01-01T00:04:00Z")]),
                 "a genuinely newer Passed gate resolves the historical conflict")
    require_test(not reconcile_required_gates(before, [verification, passed, repeated]), "same-delivery re-verification preserves its current gate")
    checks += 3

    with tempfile.TemporaryDirectory(prefix="v63-review-boundaries-") as temp:
        root = Path(temp); path = minimal_fixture_record(root, "T-REVIEW-MIN")
        original = read_json(path)
        for old_state in ("OutOfScope", "Deferred", "NotARequirement"):
            saved = copy.deepcopy(original); saved["task_contract"]["requirement_items"][0]["state"] = old_state
            atomic_write_json(path, saved)
            for new_state in ("Open", "Covered"):
                replacement = copy.deepcopy(saved["task_contract"]["requirement_items"]); replacement[0]["state"] = new_state
                expect_governance_error("review cannot reverse a scope trade-off", lambda: record_minimal_review(path.parent,
                    requirement_items=replacement, reason="fixture", basis="fixture"))
                checks += 1
        atomic_write_json(path, original)
        for new_state in ("OutOfScope", "Deferred"):
            addition = {**original["task_contract"]["requirement_items"][0], "id": "R-02", "state": new_state}
            expect_governance_error("review cannot introduce scope trade-offs", lambda: record_minimal_review(path.parent,
                requirement_items=original["task_contract"]["requirement_items"] + [addition], reason="fixture", basis="fixture"))
            checks += 1
        append_minimal_event(path.parent, event_type="run_started", summary="fixture", status="started")
        append_minimal_event(path.parent, event_type="failure", summary="recoverable fixture failure", status="failed")
        script = Path(__file__).with_name("manage_minimal_task.py")
        def cli(kind, status):
            return subprocess.run([sys.executable, "-B", "-X", "utf8", str(script), "append", str(path.parent),
                                   "--event-type", kind, "--status", status, "--summary", "fixture", "--evidence-ref", "sha256://fixture"],
                                  capture_output=True, text=True, encoding="utf-8")
        retried = cli("retry", "started"); require_test(retried.returncode == 0, retried.stdout + retried.stderr)
        attempt = read_json(path)["run_ledger"][-1]["attempt_id"]
        verified = cli("verification", "succeeded"); require_test(verified.returncode == 0, verified.stdout + verified.stderr)
        require_test(read_json(path)["run_ledger"][-1]["attempt_id"] == attempt != "attempt-001", "Minimal CLI retains its new retry attempt")
        require_test(cli("retry", "started").returncode != 0, "an earlier attempt's failure cannot justify another retry")
        require_test(len([e for e in read_json(path)["run_ledger"] if e["event_type"] == "failure"]) == 1, "retry preserves original failure history")
        checks += 4
    with tempfile.TemporaryDirectory(prefix="v63-legacy-decision-") as temp:
        path = minimal_fixture_record(Path(temp), "T-LEGACY-PROCEED")
        record = read_json(path)
        original_answer = record["task_contract"]["decisions"][0]
        original_answer.pop("outcome")
        atomic_write_json(path, record)
        enriched = {**original_answer, "id": "D-ENRICHED", "enriches": original_answer["id"], "outcome": "Approved"}
        record_minimal_review(path.parent, decisions=[enriched], reason="structure the existing authentic fixture answer", basis=original_answer["evidence_ref"])
        updated = read_json(path)
        require_test(updated["task_contract"]["decisions"][0] == original_answer, "legacy enrichment preserves original answer bytes as data")
        append_minimal_event(path.parent, event_type="run_started", summary="reuse original authorization", status="started")
        require_test(len(updated["task_contract"]["decisions"]) == len(record["task_contract"]["decisions"]) + 1,
                     "enrichment appends a unique record instead of manufacturing a fresh user answer")
        for field, replacement in (("response", "a different answer"), ("decided_at", "2026-01-01T00:00:00Z"),
                                   ("decided_by", "a different user"), ("evidence_ref", "other://source")):
            forbidden = {**enriched, "id": "BAD-" + field, field: replacement}
            expect_governance_error("enrichment cannot alter human facts", lambda: record_minimal_review(path.parent,
                decisions=[forbidden], reason="invalid enrichment", basis="fixture"))
            checks += 1
        forbidden = {**enriched, "id": "BAD-OUTCOME", "enriches": "D-ENRICHED", "outcome": "Rejected"}
        expect_governance_error("enrichment cannot overwrite an established outcome", lambda: record_minimal_review(path.parent,
            decisions=[forbidden], reason="invalid enrichment", basis="fixture"))
        checks += 3
    return {"status": "Passed", "checks": checks}


def run_failure_and_terminal_fixture() -> dict[str, object]:
    from governance_artifacts import read_jsonl
    checks = 0
    with tempfile.TemporaryDirectory(prefix="v63-failure-terminal-") as temp:
        root = Path(temp)
        task = new_task(root, "T-RETRY-TERMINAL", 1)
        initial = read_json(task / "before.json")["clarification"]
        append_run_event(task, run_id="RUN-RETRY", attempt_id="A1", event_type="run_started", summary="fixture", status="started")
        for index, cause in enumerate(("tool syntax", "old fixture", "implementation defect"), start=1):
            append_run_event(task, run_id="RUN-RETRY", attempt_id=f"A{index}", event_type="failure", summary=cause, status="failed", evidence_refs=[f"self-test://failure/{index}"])
            append_run_event(task, run_id="RUN-RETRY", attempt_id=f"A{index+1}", event_type="retry", summary="same scope, inspected side effects and authorization", status="started")
        require_test(read_json(task / "before.json")["clarification"] == initial, "technical/implementation failure counts cannot mutate clarification")
        require_test(len([e for e in read_jsonl(task / "run.jsonl") if e["event_type"] == "failure"]) == 3, "all failures remain in history")
        checks += 2
        amend_record(task / "before.json", dotted_path="scope.allowed_paths", new_value=[str(root), "src/helper.py"], reason="include helper implementing the same authorized task", basis="self-test fixture")
        require_test(read_json(task / "before.json")["clarification"] == initial, "implementation path amendment cannot invent human questions")
        append_run_event(task, run_id="RUN-RETRY", attempt_id="A4", event_type="verification", summary="verified source v1", status="succeeded", evidence_refs=["self-test://verified-source/v1"])
        before = read_json(task / "before.json"); events = read_jsonl(task / "run.jsonl")
        subject = approval_subject_sha256(before, events)
        proof = {"id": "independent-review", "outcome": "Passed", "subject_sha256": subject,
                 "decided_by": "independent-fixture-reviewer", "decided_at": now_utc(), "authority_ref": "self-test://authority"}
        gate_event = {"event_type": "human_gate", "status": "succeeded", "timestamp": now_utc(), "summary": "independent review", "evidence_refs": ["self-test://independent-review"], "gate": proof}
        require_test(not reconcile_required_gates(before, events + [gate_event]), "explicit current gate passes")
        for field, value in (("outcome", "Pending"), ("outcome", "Failed"), ("subject_sha256", "0" * 64), ("decided_at", "2020-01-01T00:00:00Z"), ("authority_ref", "unregistered://authority")):
            bad = copy.deepcopy(gate_event); bad["gate"][field] = value
            require_test(reconcile_required_gates(before, events + [bad]), f"invalid gate {field}={value} must fail")
            checks += 1
        bad = copy.deepcopy(gate_event); bad["status"] = "recorded"
        require_test(reconcile_required_gates(before, events + [bad]), "recorded cannot mean Passed")
        require_test(reconcile_required_gates(before, events + [gate_event, bad]), "later pending decision supersedes an old Passed gate")
        changed = copy.deepcopy(before); changed["scope"]["allowed_paths"].append("other.py")
        require_test(approval_subject_sha256(changed, events) != subject, "scope changes invalidate the approval subject")
        require_test(not approval_subject_sha256(before, events + [{"event_type": "mutation", "status": "succeeded"}]), "post-verification mutation invalidates approval subject")
        checks += 7
        record_fixture_acceptance(task)
        before = read_json(task / "before.json")
        for outcome, response in (("Rejected", "验收不通过，需要返修"), ("Deferred", "暂不验收")):
            bad_before = copy.deepcopy(before); bad_before["decisions"][-1].update(outcome=outcome, response=response)
            require_test(require_decision(bad_before, "Acceptance", "close", subject_sha256=subject), "a refusal or deferral is not acceptance")
            checks += 1
        append_run_event(task, run_id="RUN-RETRY", attempt_id="A4", event_type="human_gate", summary="explicit gate", status="succeeded", evidence_refs=gate_event["evidence_refs"], gate=proof)
        append_run_event(task, run_id="RUN-RETRY", attempt_id="A4", event_type="run_finished", summary="fixture complete", status="succeeded")
        close_task(task, status="Implemented", established_facts=["synthetic flow verified"], actual_changes=["temporary fixture"], verification=[{"summary":"fixture verified", "result":"Passed", "evidence_refs":["self-test://verified-source/v1"]}])
        require_test(not validate_task_directory(task), "legitimate complete carrier must validate")
        good = read_json(task / "before.json")
        for mutate in (lambda b:b.update(decisions=[d for d in b["decisions"] if d["kind"] != "Proceed"]),
                       lambda b:b["requirement_items"][0].update(state="Open"),
                       lambda b:b["authority"].update(required_gates=["unpassed-gate"])):
            invalid = copy.deepcopy(good); mutate(invalid); atomic_write_json(task / "before.json", invalid)
            require_test(validate_task_directory(task), "hand-written Implemented cannot bypass terminal invariant")
            checks += 1
        atomic_write_json(task / "before.json", good)
        # A genuine acceptance change still reopens S1 and blocks material mutation.
        other = new_task(root, "T-SEMANTIC-CHANGE", 2)
        amend_record(other / "before.json", dotted_path="acceptance.criteria", new_value=["a new human-visible outcome"], reason="synthetic real expectation change", basis="self-test")
        require_test(read_json(other / "before.json")["clarification"]["state"] == "Open", "genuine expectation changes remain blocked")
        checks += 2
    return {"status": "Passed", "checks": checks}


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
    (project_root / "surveyed.md").write_text("surveyed by the minimal fixture\n", encoding="utf-8")
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
        requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "Update one local label.", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
        decisions=[
            {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
        ],
        clarification={
            "state": "Settled",
            "mode": "Skipped",
            "notice": "Requirement is unambiguous and matches the repository; skipping the question round.",
            "survey_refs": ["surveyed.md"],
            "rounds": [],
            "basis": "self-test fixture: single label change, fully declared", "reopened_by": [],
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


def run_requirement_review_fixture() -> dict[str, object]:
    """Source-bound review controls; the fixture does not infer prose semantics."""

    from governance_artifacts import _validate_schema_node

    text = "只有备注没有实际修改时必须提示供应商改值。"
    quote = text[:-1]
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    checks = 0

    def case(branch: str, input_value: object, expected: str, actual: str) -> dict[str, object]:
        return {
            "condition": 0, "branch": branch, "input": input_value,
            "expected": expected, "actual": actual, "result": "Passed",
            "evidence_refs": [f"self-test://requirement-review/{branch}"],
        }

    base = {
        "request_snapshot": {"text": text},
        "clarification": {"rounds": []},
        "acceptance": {"criteria": ["仅备注时阻止确认，已修改金额时允许确认"]},
        "requirement_items": [{
            "id": "R-01", "source": "request_snapshot", "quote": quote,
            "reading": "条件是只有备注且值未改变，不是出现备注即阻止确认",
            "state": "Covered", "evidence_refs": ["self-test://requirement-review/executed"],
            "acceptance_refs": [0],
            "review": {
                "source_sha256": digest,
                "conditions": ["管理员仅填写备注，金额仍与修改前相同"],
                "cases": [
                    case("Met", {"before": 100, "after": 100, "note": "请改金额"},
                         "阻止确认并提示修改金额", "已阻止确认并显示修改金额提示"),
                    case("NotMet", {"before": 100, "after": 120, "note": "金额已改"},
                         "允许确认已改金额", "确认成功，保存金额120"),
                ],
            },
        }],
    }

    def check(record: dict[str, object], *, valid: bool, label: str, discharge: bool = True) -> None:
        nonlocal checks
        errors = validate_requirement_items(record, require_discharge=discharge)
        require_test((not errors) == valid, f"requirement-review {label}: {errors}")
        checks += 1

    check(base, valid=True, label="paired-condition-and-execution")
    unconditional = copy.deepcopy(base)
    review = unconditional["requirement_items"][0]["review"]
    review["conditions"] = []
    review["cases"] = [dict(review["cases"][0], condition=None, branch="Unconditional", input="真实输入")]
    check(unconditional, valid=True, label="unconditional-string-input")
    two_conditions = copy.deepcopy(base)
    review = two_conditions["requirement_items"][0]["review"]
    review["conditions"].append("当前记录允许编辑")
    review["cases"].extend([dict(copy.deepcopy(value), condition=1) for value in review["cases"][:2]])
    review["cases"].append(dict(copy.deepcopy(review["cases"][0]), branch="Exception"))
    check(two_conditions, valid=True, label="each-condition-and-explicit-exception")

    mutations = [
        ("short-fragment-cannot-cover-clause", lambda row: row.update(quote="备注")),
        ("blank-quote", lambda row: row.update(quote="")),
        ("missing-review", lambda row: row.pop("review")),
        ("missing-item-evidence", lambda row: row.update(evidence_refs=[])),
        ("review-not-an-object", lambda row: row.update(review=[])),
        ("quote-hash-not-source-hash", lambda row: row["review"].update(source_sha256=hashlib.sha256(quote.encode("utf-8")).hexdigest())),
        ("invalid-source-hash", lambda row: row["review"].update(source_sha256="f" * 63)),
        ("review-extra-field", lambda row: row["review"].update(invented=True)),
        ("empty-condition", lambda row: row["review"].update(conditions=[" "])),
        ("duplicate-condition", lambda row: row["review"].update(conditions=["同条件", "同条件"])),
        ("no-cases", lambda row: row["review"].update(cases=[])),
        ("case-not-an-object", lambda row: row["review"].update(cases=[None])),
        ("missing-opposite-branch", lambda row: row["review"].update(cases=row["review"]["cases"][:1])),
        ("exception-does-not-replace-notmet", lambda row: row["review"]["cases"][1].update(branch="Exception")),
        ("conditional-null-index", lambda row: row["review"]["cases"][0].update(condition=None)),
        ("conditional-bool-index", lambda row: row["review"]["cases"][0].update(condition=True)),
        ("conditional-negative-index", lambda row: row["review"]["cases"][0].update(condition=-1)),
        ("conditional-out-of-range", lambda row: row["review"]["cases"][0].update(condition=1)),
        ("conditional-unconditional-branch", lambda row: row["review"]["cases"][0].update(branch="Unconditional")),
        ("blank-input", lambda row: row["review"]["cases"][0].update(input=" ")),
        ("empty-object-input", lambda row: row["review"]["cases"][0].update(input={})),
        ("invalid-input-type", lambda row: row["review"]["cases"][0].update(input=[])),
        ("blank-expected", lambda row: row["review"]["cases"][0].update(expected=" ")),
        ("passed-without-actual", lambda row: row["review"]["cases"][0].update(actual="")),
        ("passed-without-evidence", lambda row: row["review"]["cases"][0].update(evidence_refs=[])),
        ("blank-evidence", lambda row: row["review"]["cases"][0].update(evidence_refs=[" "])),
        ("invalid-result", lambda row: row["review"]["cases"][0].update(result="Declared")),
        ("failed-is-not-discharged", lambda row: row["review"]["cases"][0].update(result="Failed")),
        ("notrun-is-not-discharged", lambda row: row["review"]["cases"][0].update(result="NotRun", actual="", evidence_refs=[])),
        ("case-extra-field", lambda row: row["review"]["cases"][0].update(invented=True)),
        ("boolean-acceptance-index", lambda row: row.update(acceptance_refs=[True])),
    ]
    for label, mutate in mutations:
        record = copy.deepcopy(base)
        mutate(record["requirement_items"][0])
        check(record, valid=False, label=label)

    unfinished = copy.deepcopy(base)
    unfinished["requirement_items"][0]["review"]["cases"][0].update(result="NotRun", actual="", evidence_refs=[])
    check(unfinished, valid=True, label="notrun-readable-before-discharge", discharge=False)
    historical = copy.deepcopy(base)
    historical["requirement_items"][0].pop("review")
    check(historical, valid=True, label="historical-optional-review", discharge=False)
    failed = copy.deepcopy(base)
    failed["requirement_items"][0]["review"]["cases"][0]["result"] = "Failed"
    check(failed, valid=True, label="failed-execution-readable-before-discharge", discharge=False)
    changed_source = copy.deepcopy(base)
    changed_source["request_snapshot"]["text"] = "\n" + text
    check(changed_source, valid=False, label="complete-raw-source-hash-includes-whitespace")
    bad_unconditional = copy.deepcopy(unconditional)
    bad_unconditional["requirement_items"][0]["review"]["cases"][0]["condition"] = 0
    check(bad_unconditional, valid=False, label="unconditional-null-required")

    clarified = copy.deepcopy(base)
    clarified["clarification"] = {"rounds": [{"ordinal": 1, "exchanges": [{"answer": "是"}]}]}
    check(clarified, valid=False, label="one-character-answer-not-silently-dropped")
    clarified["requirement_items"].append({
        "id": "R-02", "source": "clarification:r1.e1", "quote": "是",
        "reading": "确认性短答，原要求未增加", "state": "NotARequirement",
        "evidence_refs": [], "acceptance_refs": [],
    })
    check(clarified, valid=True, label="explicit-short-answer-disposition")
    same_words = copy.deepcopy(base)
    same_words["clarification"] = {"rounds": [{"ordinal": 1, "exchanges": [{"answer": text}]}]}
    same_words["requirement_items"][0]["source"] = "clarification:r1.e1"
    check(same_words, valid=False, label="other-source-identical-quote-cannot-cover-request")
    bound_answer = copy.deepcopy(clarified)
    bound_answer["requirement_items"][1].update(state="Covered", acceptance_refs=[0], evidence_refs=["self-test://answer"])
    bound_answer["requirement_items"][1]["review"] = copy.deepcopy(unconditional["requirement_items"][0]["review"])
    check(bound_answer, valid=False, label="answer-must-bind-own-source-hash")
    bound_answer["requirement_items"][1]["review"]["source_sha256"] = hashlib.sha256("是".encode("utf-8")).hexdigest()
    check(bound_answer, valid=True, label="answer-own-source-bound-review")

    schemas = skill_root_path() / "assets" / "runtime" / "schemas"
    full_item_schema = read_json(schemas / "task-before.schema.json")["properties"]["requirement_items"]["items"]
    minimal_item_schema = read_json(schemas / "minimal-task-record.schema.json")["properties"]["task_contract"]["properties"]["requirement_items"]["items"]
    require_test(full_item_schema == minimal_item_schema, "full/minimal requirement item schemas must agree")
    checks += 1
    for schema in (full_item_schema, minimal_item_schema):
        require_test(not _validate_schema_node(base["requirement_items"][0], schema, "$"), "paired review must match schema")
        require_test(not _validate_schema_node(unconditional["requirement_items"][0], schema, "$"), "unconditional review must match schema")
        require_test(not _validate_schema_node(historical["requirement_items"][0], schema, "$"), "review remains optional for historical reading")
        checks += 3
        for label, field, value in (
            ("unknown-field", "unknown", True),
            ("bad-input", "input", []),
            ("boolean-index", "condition", True),
        ):
            row = copy.deepcopy(base["requirement_items"][0])
            row["review"]["cases"][0][field] = value
            require_test(bool(_validate_schema_node(row, schema, "$")), f"schema rejects {label}")
            checks += 1
    return {"status": "Passed", "checks": checks, "semantic_inference": "not_performed"}


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
        dependencies = root / "requirements.txt"
        dependencies.write_text("psycopg[binary]>=3.2\n", encoding="utf-8")
        dependency_digest = sha256_file(dependencies)
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
        require_test(sha256_file(dependencies) == dependency_digest, "documentation migration changed the Python dependency manifest")

        declaration = root / ".project-governance" / "tasks" / "T-DOCUMENT-DECLARATION" / "before.json"
        atomic_write_json(declaration, {"artifact_manifest": [{"content_ref": "requirements.txt"}]})
        require_test(not validate_project_document_layout(root), "declared Python dependency manifest was misclassified as a native document")

        product_text = root / "product-requirements.txt"
        product_text.write_text("The product must preserve the selected account.\n", encoding="utf-8")
        require_test(
            "product document is outside LG_project_docs: product-requirements.txt" in validate_project_document_layout(root),
            "the dependency manifest exception exempted a real product requirement document",
        )
        product_text.unlink()
        product_markdown = root / "requirements.md"
        product_markdown.write_text("# Product requirements\n", encoding="utf-8")
        atomic_write_json(declaration, {"artifact_manifest": [
            {"content_ref": "requirements.txt"}, {"content_ref": "requirements.md"},
        ]})
        errors = validate_project_document_layout(root)
        require_test("product document is outside LG_project_docs: requirements.md" in errors,
                     "real Markdown requirements outside the document directory were accepted")
        require_test("declared native document is outside LG_project_docs: requirements.md (before.json)" in errors,
                     "declaring a real native document bypassed its layout rule")
        require_test("product document is outside LG_project_docs: requirements.txt" not in errors,
                     "the root Python dependency manifest remains misclassified")
        require_test("declared native document is outside LG_project_docs: requirements.txt (before.json)" not in errors,
                     "the declared Python dependency manifest remains misclassified")
        product_markdown.unlink()
        atomic_write_json(declaration, {"artifact_manifest": [{"content_ref": "requirements.txt"}]})
        require_test(not validate_project_document_layout(root), "removing real layout violations did not restore a valid document layout")
    return {"status": "Passed", "checks": 17}


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
        (project_root / "surveyed.md").write_text("surveyed\n", encoding="utf-8")
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
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "self-test fixture", "reopened_by": []},
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
        record_fixture_acceptance(task_dir)
        close_minimal_record(
            task_dir,
            status="Implemented",
            established_facts=["The label now matches expected text."],
            actual_changes=["Changed src/label.txt."],
            verification=["Passed::Focused test passed.::test://fixture"],
        )
        completed = read_json(record_path)
        for field, replacement in (("decisions", []), ("requirement_items", [{**completed["task_contract"]["requirement_items"][0], "state": "Open"}])):
            tampered = copy.deepcopy(completed); tampered["task_contract"][field] = replacement
            require_test(validate_minimal_record(tampered, task_dir=task_dir), "hand-written Minimal outcome cannot bypass decision/discharge")
        tampered = copy.deepcopy(completed); tampered["task_outcome"]["verification"][0]["result"] = "Failed"
        require_test(validate_minimal_record(tampered, task_dir=task_dir), "hand-written Minimal outcome cannot bypass verification")
        original_subject = approval_subject_sha256(minimal_approval_contract(completed), completed["run_ledger"])
        for field in ("allowed_paths", "out_of_scope", "forbidden_actions"):
            tampered = copy.deepcopy(completed); tampered["task_contract"][field].append("changed boundary")
            require_test(approval_subject_sha256(minimal_approval_contract(tampered), tampered["run_ledger"]) != original_subject,
                         f"Minimal {field} must bind the approval subject")
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
        (project_root / "surveyed.md").write_text("surveyed\n", encoding="utf-8")
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
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "self-test fixture", "reopened_by": []},
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
        (project_root / "surveyed.md").write_text("surveyed\n", encoding="utf-8")
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
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test minimal fixture", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Requirement is unambiguous and matches the repository; skipping the question round.", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "self-test fixture", "reopened_by": []},
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
        (project_root / "surveyed.md").write_text("surveyed\n", encoding="utf-8")
        initialize_task(
            project_root,
            project_id="P-UP",
            work_item_id="W-UP",
            task_id="T-UP-001",
            ordinal=1,
            objective="Handle the expanded multi-file scope.",
            request_snapshot={"language": "en", "text": "self-test fixture request", "captured_at": "2026-08-15T00:00:00Z"},
            requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test fixture request", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
            decisions=[
                {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            ],
            clarification={"state": "Settled", "mode": "Skipped", "notice": "Scope is fully declared by the fixture; skipping the question round.", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "self-test fixture", "reopened_by": []},
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
    (root / "surveyed.md").write_text("surveyed by the conformance fixture\n", encoding="utf-8")
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
        requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": f"Conformance fixture request for {task_id}", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
        decisions=[
            {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
        ],
        clarification={
            "state": "Settled",
            "mode": "Skipped",
            "notice": "Requirement is unambiguous and matches the repository; skipping the question round.",
            "survey_refs": ["surveyed.md"],
            "rounds": [],
            "basis": "self-test fixture: the caller declares the full scope", "reopened_by": [],
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


def run_amendment_growth_fixture() -> dict[str, object]:
    """Only actual contract changes add revisions; derived snapshots never do."""

    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        require_test(condition, message)
        checks += 1

    with tempfile.TemporaryDirectory(prefix="v63-amendment-growth-") as temp:
        root = Path(temp)
        task = new_task(root, "T-AMENDMENT-GROWTH", 1)
        path = task / "before.json"
        initial = read_json(path)
        initial_bytes = path.read_bytes()
        options = {"reason": "synthetic growth regression", "basis": "self-test://amendment-growth"}
        unchanged = amend_record(
            path, dotted_path="scope.allowed_paths",
            new_value=copy.deepcopy(initial["scope"]["allowed_paths"]), **options,
        )
        check(path.read_bytes() == initial_bytes, "an unchanged amendment rewrote the contract")
        check(unchanged["revision"] == initial["revision"], "an unchanged amendment advanced the revision")
        check(unchanged["amendments"] == initial["amendments"], "an unchanged amendment added history")

        allowed = [*initial["scope"]["allowed_paths"], "src/helper.py"]
        changed = amend_record(path, dotted_path="scope.allowed_paths", new_value=allowed, **options)
        check(changed["revision"] == initial["revision"] + 1, "one contract edit must add exactly one revision")
        check(len(changed["amendments"]) == len(initial["amendments"]) + 1, "derived refresh added an amendment")
        edit = changed["amendments"][-1]
        check(edit["path"] == "scope.allowed_paths", "the amendment does not identify the actual edit")
        check(edit["old_value"] == initial["scope"]["allowed_paths"] and edit["new_value"] == allowed,
              "a real edit lost its old or new value")
        check(changed["tailoring_resolution"] == current_tailoring(changed), "derived snapshot was not refreshed")

        risk = "High" if changed["task_profile"]["risk_level"] != "High" else "Low"
        mixed = amend_record_batch(path, changes=[
            {"path": "scope.allowed_paths", "value": allowed},
            {"path": "task_profile.risk_level", "value": risk},
            {"path": "scope.allowed_paths", "value": allowed},
        ], **options)
        check(mixed["revision"] == changed["revision"] + 1, "a mixed batch counted unchanged fields")
        check(len(mixed["amendments"]) == len(changed["amendments"]) + 1, "a mixed batch copied derived history")
        check(mixed["amendments"][:-1] == changed["amendments"], "a batch rewrote existing audit history")
        check(mixed["tailoring_resolution"] == current_tailoring(mixed), "batch refresh left a stale derived snapshot")

        stable_bytes = path.read_bytes()
        for _ in range(12):
            amend_record(path, dotted_path="scope.allowed_paths", new_value=allowed, **options)
            amend_record_batch(path, changes=[
                {"path": "task_profile.risk_level", "value": risk},
                {"path": "scope.allowed_paths", "value": allowed},
            ], **options)
        check(path.read_bytes() == stable_bytes, "repeated unchanged operations grew the contract")

        for changes in ([], [
            {"path": "scope.allowed_paths", "value": ["src/other.py"]},
            {"path": "revision", "value": mixed["revision"]},
        ]):
            expect_governance_error("invalid batch must remain atomic",
                                    lambda: amend_record_batch(path, changes=changes, **options))
            check(path.read_bytes() == stable_bytes, "a rejected batch changed the contract")

        expect_governance_error("an unchanged immutable field is still immutable",
                                lambda: amend_record(path, dotted_path="task_id", new_value=mixed["task_id"], **options))
        check(path.read_bytes() == stable_bytes, "an immutable-field rejection changed the contract")
        expect_governance_error("JSON booleans must not compare equal to integer fields",
                                lambda: amend_record(path, dotted_path="ordinal", new_value=True, **options))
        check(path.read_bytes() == stable_bytes, "an invalid JSON-type edit changed the contract")

        broken_path = task / "invalid-before.json"
        broken = copy.deepcopy(mixed)
        broken["revision"] = "invalid"
        atomic_write_json(broken_path, broken)
        broken_bytes = broken_path.read_bytes()
        expect_governance_error("unchanged edits still validate the record",
                                lambda: amend_record(broken_path, dotted_path="scope.allowed_paths", new_value=allowed, **options))
        check(broken_path.read_bytes() == broken_bytes, "validation rewrote an invalid record")
        for dotted_path, value in (
            ("tailoring_resolution", mixed["tailoring_resolution"]),
            ("tailoring_resolution.stage", "S5"),
        ):
            expect_governance_error("derived snapshots use the refresh entrypoint",
                                    lambda: amend_record(path, dotted_path=dotted_path, new_value=value, **options))
            check(path.read_bytes() == stable_bytes, "a rejected derived amendment changed the contract")

        command = subprocess.run([
            sys.executable, str(skill_root_path() / "scripts" / "amend_record.py"), str(path),
            "--path", "scope.allowed_paths", "--value-json", json.dumps(allowed),
            "--reason", options["reason"], "--basis", options["basis"],
        ], capture_output=True, text=True, encoding="utf-8")
        check(command.returncode == 0 and command.stdout.startswith("UNCHANGED:"),
              f"CLI must identify an unchanged operation: {command.stdout} {command.stderr}")
        check(path.read_bytes() == stable_bytes, "an unchanged CLI operation rewrote the contract")
    return {"status": "Passed", "checks": checks}


def run_adversarial_review_fixture() -> dict[str, object]:
    """Synthetic opt-in/round records, not an actual adversarial review of this task."""
    from adversarial_review import append_review, review_state, requirements_subject, REVIEW_CONTRACT
    from governance_artifacts import now_utc, read_jsonl, user_decision_subject_sha256
    from minimal_task import minimal_approval_contract
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        require_test(condition, message)
        checks += 1

    with tempfile.TemporaryDirectory(prefix="v63-adversarial-") as temp:
        root = Path(temp)
        for minimal in (False, True):
            tid = "T-REVIEW-MIN" if minimal else "T-REVIEW-FULL"
            task = root / ".project-governance/tasks" / tid
            if minimal:
                path = minimal_fixture_record(root, tid)
                expect_governance_error("cannot offer before Minimal completion", lambda: append_review(task,
                    {"event": "Offer", "recorded_at": now_utc(), "prompt": "Synthetic opt-in?", "evidence_ref": "self-test://question"}, reason="fixture", basis="self-test"))
                append_minimal_event(task, event_type="run_started", summary="Synthetic work", status="started")
                append_minimal_event(task, event_type="verification", summary="Synthetic verification", status="succeeded", evidence_refs=["self-test://verification"])
                record_fixture_acceptance(task)
                close_minimal_record(task, status="Implemented", established_facts=["Synthetic work complete"], actual_changes=["Synthetic change"], verification=["Passed::Synthetic check::self-test://verification"])
            else:
                new_task(root, tid, 1)
                before = read_json(task / "before.json")
                before["authority"]["required_gates"] = []
                atomic_write_json(task / "before.json", before)
                append_run_event(task, run_id="RUN-REVIEW", attempt_id="A01", event_type="run_started", summary="Synthetic work", status="started")
                append_run_event(task, run_id="RUN-REVIEW", attempt_id="A01", event_type="verification", summary="Synthetic verification", status="succeeded", evidence_refs=["self-test://verification"])
                record_fixture_acceptance(task)
                append_run_event(task, run_id="RUN-REVIEW", attempt_id="A01", event_type="run_finished", summary="Synthetic finished", status="succeeded")
                path = close_task(task, status="Implemented", established_facts=["Synthetic work complete"], actual_changes=["Synthetic change"], verification=[{"result": "Passed", "summary": "Synthetic check", "evidence_refs": ["self-test://verification"]}])

            def load():
                document = read_json(path)
                outcome = document["task_outcome"] if minimal else document
                contract = minimal_approval_contract(document) if minimal else read_json(task / "before.json")
                events = document["run_ledger"] if minimal else read_jsonl(task / "run.jsonl")
                return document, outcome, contract, events

            def write(entry):
                return append_review(task, entry, reason="Synthetic protocol check", basis="self-test://adversarial")

            def offer():
                write({"event": "Offer", "recorded_at": now_utc(), "prompt": "Synthetic opt-in question after engineering completion?", "evidence_ref": "self-test://question", "budget": {"review_rounds": 50, "repair_batches": 50, "elapsed_minutes": 60}})

            def decision(choice):
                return {"event": "Decision", "recorded_at": now_utc(), "outcome": choice,
                        "response": f"Synthetic explicit {choice}", "decided_by": "synthetic-user", "evidence_ref": "self-test://answer"}

            def round_record(number):
                _, outcome, contract, events = load()
                report = task / "evidence" / f"synthetic-round-{number}.md"
                report.parent.mkdir(parents=True, exist_ok=True)
                if not report.exists():
                    report.write_text(f"Synthetic complete report for {tid} round {number}\n", encoding="utf-8")
                return {"event": "Round", "recorded_at": now_utc(), "started_at": now_utc(),
                        "round_id": f"R{number}", "reviewer": "synthetic-reviewer", "delivery_task_id": tid,
                        "report_ref": report.relative_to(root).as_posix(),
                        "subject_sha256": user_decision_subject_sha256(contract, events, outcome),
                        "requirements_sha256": requirements_subject(contract), "coverage": "Complete",
                        "unreviewed_items": [], "evidence_refs": [f"self-test://round-{number}"], "findings": [], "resolutions": []}

            def ready_round(number, **changes):
                record = round_record(number)
                record.update(changes)
                record["recorded_at"] = now_utc()
                return record

            original, initial, contract, events = load()
            ledger = copy.deepcopy(events)
            user_decision = copy.deepcopy(initial["user_decision"])
            check(review_state(initial)["status"] == "NotOffered", "new results must prompt after completion")
            expect_governance_error("answer without actual question", lambda: write(decision("Accepted")))
            offer()
            snapshot = path.read_bytes()
            expect_governance_error("silence is not opt-in", lambda: write(ready_round(1)))
            check(path.read_bytes() == snapshot, "denied review must not write the result")
            check(review_state(load()[1])["status"] == "AwaitingUser", "unanswered offer must remain waiting")
            for choice in ("Declined", "Deferred"):
                write(decision(choice))
                expect_governance_error(f"{choice} is not opt-in", lambda: write(ready_round(1)))
                check(review_state(load()[1])["status"] == choice, "user choice must remain separate from engineering")
                offer()
            write(decision("Accepted"))
            check(review_state(load()[1])["status"] == "InProgress", "explicit opt-in starts review")
            expect_governance_error("wrong delivery version", lambda: write(ready_round(1, subject_sha256="f" * 64)))
            expect_governance_error("wrong original request", lambda: write(ready_round(1, requirements_sha256="f" * 64)))
            expect_governance_error("review started before opt-in", lambda: write(ready_round(1, started_at="2026-08-15T00:00:00Z")))
            write(ready_round(1))
            check(review_state(load()[1])["clean_streak"] == 1, "one clean round cannot pass")
            expect_governance_error("same report is not a second round", lambda: write(ready_round(2, report_ref=(task / "evidence/synthetic-round-1.md").relative_to(root).as_posix())))
            expect_governance_error("same id is not a second round", lambda: write(ready_round(1, evidence_refs=["self-test://fresh-report"])))
            write(ready_round(2, findings=[{"id": "F1", "summary": "Synthetic edge case", "evidence_refs": ["self-test://reproduction"]}]))
            check(review_state(load()[1])["clean_streak"] == 0, "any finding must reset the streak")
            write(ready_round(3))
            check(review_state(load()[1])["clean_streak"] == 0 and review_state(load()[1])["open_findings"] == ["F1"], "unresolved findings block a clean round")
            expect_governance_error("fixed without new verified delivery", lambda: write(ready_round(4, resolutions=[{"finding_id": "F1", "disposition": "Fixed", "reason": "Synthetic fix claim", "evidence_refs": ["self-test://fix"]}])))
            write(ready_round(4, resolutions=[{"finding_id": "F1", "disposition": "NotAnIssue", "reason": "Synthetic counterevidence disproves issue", "evidence_refs": ["self-test://counterevidence"]}]))
            check(review_state(load()[1])["clean_streak"] == 1, "evidenced false-positive resolution permits first clean round")
            write(ready_round(5, coverage="Incomplete"))
            check(review_state(load()[1])["clean_streak"] == 0, "incomplete coverage must reset")
            write(ready_round(6, unreviewed_items=["Synthetic unavailable environment"]))
            check(review_state(load()[1])["clean_streak"] == 0, "unreviewed items must reset")
            write({"event": "Blocked", "recorded_at": now_utc(), "reason": "Synthetic tool unavailable", "evidence_refs": ["self-test://blocked"]})
            check(review_state(load()[1])["status"] == "Blocked", "blockers cannot be reported as pass")
            write(ready_round(7))
            changed = copy.deepcopy(load()[1])
            candidate = ready_round(8, subject_sha256="a" * 64)
            previous_round = changed["adversarial_review"][-1]
            candidate.update(review_contract_version=REVIEW_CONTRACT,
                             report_sha256=hashlib.sha256((root / candidate["report_ref"]).read_bytes()).hexdigest(),
                             delivery_completed_at=previous_round["delivery_completed_at"],
                             delivery_verified_at=previous_round["delivery_verified_at"])
            changed["adversarial_review"].append(candidate)
            check(review_state(changed)["clean_streak"] == 1, "changing delivery resets the previous clean streak")
            write(ready_round(8))
            state = review_state(load()[1])
            check(state["status"] == "Passed" and state["clean_streak"] == 2 and not state["open_findings"], "only two consecutive complete clean rounds pass")
            expect_governance_error("no unsolicited extra rounds after pass", lambda: write(ready_round(9)))
            document, outcome, contract, events = load()
            check(events == ledger and outcome["user_decision"] == user_decision, "review must preserve finished ledger and user acceptance")
            check(not validate_task_directory(task), "review-enriched carrier must remain valid")
            last_amendment = document["amendments"][-1]
            delta = last_amendment["changes"][0] if minimal else last_amendment
            check(isinstance(delta["new_value"], dict) and delta["old_value"] == {"$missing": True}, "review history must store only one new record, not old and new series")
            check(active_task_signal(task)["adversarial_review"]["status"] == "Passed", "public status must expose review progress")
            if not minimal:
                expect_governance_error("generic amendments cannot erase review", lambda: amend_record(path, dotted_path="adversarial_review", new_value=[], reason="Synthetic erase", basis="self-test"))
            offer()
            write(decision("Accepted"))
            write(ready_round(9, findings=[{"id": "F2", "summary": "Synthetic fix required", "evidence_refs": ["self-test://fix-repro"]}]))
            repair_id = tid + "-FIX"
            write({"event": "WorkStarted", "recorded_at": now_utc(), "work_type": "Repair", "work_id": repair_id, "evidence_refs": ["self-test://repair-start"]})
            repair = new_task(root, repair_id, 3 if minimal else 2, project_id=contract["project_id"], depends_on=[tid])
            repaired_before = read_json(repair / "before.json")
            repaired_before["authority"]["required_gates"] = []
            atomic_write_json(repair / "before.json", repaired_before)
            append_run_event(repair, run_id="RUN-FIX", attempt_id="A01", event_type="run_started", summary="Synthetic repair", status="started")
            append_run_event(repair, run_id="RUN-FIX", attempt_id="A01", event_type="verification", summary="Synthetic repair verified", status="succeeded", evidence_refs=["self-test://repair-check"])
            record_fixture_acceptance(repair)
            append_run_event(repair, run_id="RUN-FIX", attempt_id="A01", event_type="run_finished", summary="Synthetic repair finished", status="succeeded")
            repaired_path = close_task(repair, status="Implemented", established_facts=["Synthetic repair verified"], actual_changes=["Synthetic fix"], verification=[{"result": "Passed", "summary": "Synthetic repair check", "evidence_refs": ["self-test://repair-check"]}], review_parent_task_id=tid)
            repaired_before = read_json(repair / "before.json")
            repaired_subject = user_decision_subject_sha256(repaired_before, read_jsonl(repair / "run.jsonl"), read_json(repaired_path))
            write(ready_round(10, delivery_task_id=repair_id, subject_sha256=repaired_subject, resolutions=[{"finding_id": "F2", "disposition": "Fixed", "reason": "Synthetic verified repair", "evidence_refs": ["self-test://repair-check"]}]))
            check(review_state(load()[1])["clean_streak"] == 1, "repaired delivery must begin a new clean streak")
            write(ready_round(11, delivery_task_id=repair_id, subject_sha256=repaired_subject))
            check(review_state(load()[1])["status"] == "Passed", "a linked verified repair can converge with two new clean rounds")
            public = subprocess.run([sys.executable, "-X", "utf8", str(skill_root_path() / "scripts/adversarial_review.py"), str(task)], capture_output=True, text=True, encoding="utf-8")
            check(public.returncode == 0 and json.loads(public.stdout)["status"] == "Passed", "public review CLI must read both carriers")
            offer()
            write(decision("Accepted"))
            write(decision("Stopped"))
            expect_governance_error("stopped review cannot continue", lambda: write(ready_round(9)))
            check(review_state(load()[1])["status"] == "Stopped", "explicit stop must be preserved")
            legacy = copy.deepcopy(initial)
            legacy.pop("adversarial_review")
            check(review_state(legacy)["status"] == "LegacyUntracked", "historical absence must not invent reviews")
            check(review_state({"status": "Blocked", "adversarial_review": []})["status"] == "NotApplicable", "unfinished engineering cannot trigger a review offer")
    return {"status": "Passed", "checks": checks}


def run_adversarial_boundary_fixture() -> dict[str, object]:
    """Reproduce the eight independently observed review failures through public APIs."""
    import threading
    import time
    import governance_artifacts as ga
    from adversarial_review import append_review, review_status, requirements_subject, review_state
    from minimal_task import minimal_approval_contract
    checks = 0

    def check(condition, message):
        nonlocal checks
        require_test(condition, message)
        checks += 1

    with tempfile.TemporaryDirectory(prefix="v63-adversarial-boundary-") as temp:
        root = Path(temp).resolve()

        def finish(tid, ordinal, minimal=False, parent=None, source_ref="self-test://source"):
            if parent:
                write(root / ".project-governance/tasks" / parent, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Repair", "work_id": tid, "evidence_refs": ["self-test://repair-start"]})
            if minimal:
                path = minimal_fixture_record(root, tid)
                record = read_json(path)
                record["depends_on"] = [parent] if parent else []
                atomic_write_json(path, record)
                task = path.parent
                append_minimal_event(task, event_type="run_started", summary="Synthetic work", status="started")
                append_minimal_event(task, event_type="verification", summary="Synthetic verification", status="succeeded", evidence_refs=[source_ref])
                record_fixture_acceptance(task)
                pending = read_json(path)
                pending["task_contract"]["decisions"] = [item for item in pending["task_contract"]["decisions"] if item["kind"] != "Acceptance"]
                atomic_write_json(path, pending)
                close_minimal_record(task, status="Implemented", established_facts=["Synthetic complete"], actual_changes=["Synthetic change"], verification=[f"Passed::Synthetic verification::{source_ref}"], review_parent_task_id=parent)
            else:
                task = new_task(root, tid, ordinal, depends_on=[parent] if parent else [])
                before = read_json(task / "before.json")
                before["authority"]["required_gates"] = []
                atomic_write_json(task / "before.json", before)
                append_run_event(task, run_id=tid, attempt_id="A01", event_type="run_started", summary="Synthetic work", status="started")
                append_run_event(task, run_id=tid, attempt_id="A01", event_type="verification", summary="Synthetic verification", status="succeeded", evidence_refs=[source_ref])
                record_fixture_acceptance(task)
                pending = read_json(task / "before.json")
                pending["decisions"] = [item for item in pending["decisions"] if item["kind"] != "Acceptance"]
                atomic_write_json(task / "before.json", pending)
                append_run_event(task, run_id=tid, attempt_id="A01", event_type="run_finished", summary="Synthetic complete", status="succeeded")
                close_task(task, status="Implemented", established_facts=["Synthetic complete"], actual_changes=["Synthetic change"], verification=[{"result": "Passed", "summary": "Synthetic verification", "evidence_refs": [source_ref]}], review_parent_task_id=parent)
            return task

        def load(task):
            if (task / "before.json").is_file():
                return task / "after.json", read_json(task / "after.json"), read_json(task / "before.json"), ga.read_jsonl(task / "run.jsonl")
            record = read_json(task / "task-record.json")
            return task / "task-record.json", record["task_outcome"], minimal_approval_contract(record), record["run_ledger"]

        def write(task, entry):
            return append_review(task, entry, reason="Synthetic boundary regression", basis="self-test://independent-counterexamples")

        def choose(task, state):
            write(task, {"event": "Decision", "recorded_at": ga.now_utc(), "outcome": state, "response": f"Synthetic {state}", "decided_by": "synthetic-user", "evidence_ref": "self-test://explicit-user"})

        def start(task, first="Accepted"):
            write(task, {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic actual post-completion question", "evidence_ref": "self-test://offer", "budget": {"review_rounds": 50, "repair_batches": 50, "elapsed_minutes": 60}})
            choose(task, first)

        def entry(task, number, delivery=None, **changes):
            delivery = delivery or task
            _, out, before, events = load(delivery)
            _, _, original, _ = load(task)
            report = task / "evidence" / f"round-{number}.md"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(f"Synthetic independently written report {number} for {task.name}\n", encoding="utf-8")
            result = {"event": "Round", "recorded_at": ga.now_utc(), "started_at": ga.now_utc(), "round_id": f"B-{number}", "reviewer": "synthetic-reviewer", "delivery_task_id": delivery.name,
                      "subject_sha256": ga.user_decision_subject_sha256(before, events, out), "requirements_sha256": requirements_subject(original), "report_ref": report.relative_to(root).as_posix(), "coverage": "Complete", "unreviewed_items": [],
                      "evidence_refs": ["self-test://shared-original-and-test-log"], "findings": [], "resolutions": []}
            result.update(changes)
            result["recorded_at"] = ga.now_utc()
            return result

        for minimal in (False, True):
            auth_task = finish("T-BLANK-MIN" if minimal else "T-BLANK-FULL", 80, minimal)
            auth_path = load(auth_task)[0]
            blank_values = (" ", "\t\r\n", "\u3000\u00a0\u2003")
            for field in ("prompt", "evidence_ref"):
                for blank in blank_values:
                    offer = {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic actual question", "evidence_ref": "self-test://actual-offer"}
                    offer[field] = blank
                    unchanged = auth_path.read_bytes()
                    expect_governance_error("whitespace-only offer text", lambda value=offer: write(auth_task, value))
                    check(auth_path.read_bytes() == unchanged, "blank offer fields must not write either carrier")
            write(auth_task, {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic actual question", "evidence_ref": "self-test://actual-offer"})
            for field in ("response", "decided_by", "evidence_ref"):
                for blank in blank_values:
                    decision = {"event": "Decision", "recorded_at": ga.now_utc(), "outcome": "Accepted", "response": "Synthetic explicit consent", "decided_by": "synthetic-user", "evidence_ref": "self-test://actual-consent"}
                    decision[field] = blank
                    unchanged = auth_path.read_bytes()
                    expect_governance_error("whitespace-only authorization", lambda value=decision: write(auth_task, value))
                    check(auth_path.read_bytes() == unchanged and review_status(auth_task)["status"] == "AwaitingUser", "blank consent fields must not enroll or write either carrier")
            padded = {"event": "Decision", "recorded_at": ga.now_utc(), "outcome": "Accepted", "response": " \t Synthetic explicit consent \u3000", "decided_by": " synthetic-user ", "evidence_ref": " self-test://actual-consent "}
            write(auth_task, padded)
            check(all(load(auth_task)[1]["adversarial_review"][-1][field] == padded[field] for field in ("response", "decided_by", "evidence_ref")), "real consent text and surrounding whitespace must remain unchanged")
            for field, value in (("reviewer", " \t "), ("evidence_refs", ["\u3000"])):
                candidate = entry(auth_task, "blank-" + field, **{field: value})
                unchanged = auth_path.read_bytes()
                expect_governance_error("whitespace-only round evidence", lambda value=candidate: write(auth_task, value))
                check(auth_path.read_bytes() == unchanged, "round text and evidence items must contain actual text")
            for field, value in (("reason", " \t "), ("evidence_refs", ["\u3000"])):
                candidate = {"event": "Blocked", "recorded_at": ga.now_utc(), "reason": "Synthetic actual blocker", "evidence_refs": ["self-test://actual-blocker"], field: value}
                unchanged = auth_path.read_bytes()
                expect_governance_error("whitespace-only blocked evidence", lambda value=candidate: write(auth_task, value))
                check(auth_path.read_bytes() == unchanged, "blocked reasons and evidence items must contain actual text")
            task = finish("T-BOUND-MIN" if minimal else "T-BOUND-FULL", 1, minimal)
            start(task, "Deferred")
            choose(task, "Accepted")
            check(review_status(task)["status"] == "InProgress", "later actual opt-in must not require another question")
            choose(task, "Stopped")
            choose(task, "Declined")
            choose(task, "Accepted")
            check(review_status(task)["status"] == "InProgress", "an actual changed decision may resume an earlier offer")
            first = entry(task, 1)
            first["report_ref"] = str((root / first["report_ref"]).resolve())
            write(task, first)
            path, out, before, events = load(task)
            check(out["adversarial_review"][-1]["report_ref"] == (task / "evidence/round-1.md").relative_to(root).as_posix(), "a valid absolute report must be accepted and saved canonically")
            original_digest = requirements_subject(before)
            corrected = copy.deepcopy(before)
            corrected["clarification"]["basis"] += " Synthetic metadata correction"
            check(requirements_subject(corrected) == original_digest, "basis edits must not change original-word binding")
            changed_words = copy.deepcopy(before)
            changed_words["request_snapshot"]["text"] += " Synthetic new condition"
            check(review_state(out, changed_words)["status"] == "Stale", "real word changes must stale history without making it unreadable")
            if not minimal:
                amend_record(task / "before.json", dotted_path="clarification.basis", new_value=corrected["clarification"]["basis"], reason="Synthetic metadata correction", basis="self-test://metadata")
                check(review_status(task)["clean_streak"] == 1, "a public basis correction must retain the valid clean round")
            first_report = task / "evidence/round-1.md"
            alias = str(first_report.parent) + "/./" + first_report.name
            expect_governance_error("same physical report aliases", lambda: write(task, entry(task, 2, report_ref=alias)))
            copied = task / "evidence/copied.md"
            copied.write_bytes(first_report.read_bytes())
            expect_governance_error("copied report content", lambda: write(task, entry(task, 2, report_ref=str(copied))))
            second = entry(task, 2)
            canonical_report = second["report_ref"]
            second["report_ref"] = "./" + canonical_report
            write(task, second)
            check(load(task)[1]["adversarial_review"][-1]["report_ref"] == canonical_report, "a distinct valid report with a relative alias must be accepted canonically")
            check(review_status(task)["status"] == "Passed", "distinct reports may share original requirements and test evidence")
            second_report = task / "evidence/round-2.md"
            report_bytes = second_report.read_bytes()
            second_report.write_text("Synthetic changed report after its recorded review\n", encoding="utf-8")
            check(review_status(task)["status"] == "RestartRequired" and review_status(task)["clean_streak"] == 0, "changing a completed review's report must require a new decision")
            second_report.write_bytes(report_bytes)
            check(review_status(task)["status"] == "Passed", "restoring the exact bound report must restore its verifiable state")
            snapshot = path.read_bytes()
            for index, invalid in enumerate(([], None, "wrong")):
                expect_governance_error("non-object input", lambda value=invalid: write(task, value))
                bad = root / f"invalid-{minimal}-{index}.json"
                bad.write_text(json.dumps(invalid), encoding="utf-8")
                result = subprocess.run([sys.executable, "-X", "utf8", str(skill_root_path() / "scripts/adversarial_review.py"), str(task), "--entry-json-file", str(bad), "--reason", "synthetic", "--basis", "self-test"], capture_output=True, text=True, encoding="utf-8")
                check(result.returncode == 2 and "ERROR:" in result.stderr and "Traceback" not in result.stderr and path.read_bytes() == snapshot, "invalid JSON types must fail uniformly without writes")
            if not minimal:
                _, out, _, _ = load(task)
                amended = copy.deepcopy(out["verification"])
                amended[0]["evidence_refs"] = ["self-test://new-verified-reference"]
                amend_record(path, dotted_path="verification", new_value=amended, reason="Synthetic evidence correction changes bound delivery", basis="self-test://version")
                check(review_status(task)["status"] == "RestartRequired" and review_status(task)["clean_streak"] == 0, "current delivery changes must not restore a completed review's authorization")
                expect_governance_error("completed stale review cannot continue without new decision", lambda: write(task, entry(task, 3)))
                choose(task, "Accepted")
                write(task, {"event": "Blocked", "recorded_at": ga.now_utc(), "reason": "Synthetic recovery check", "evidence_refs": ["self-test://blocked"]})
                check(review_status(task)["status"] == "Blocked", "stale history must permit a truthful blocked record")
            else:
                choose(task, "Accepted")
            started_before_repair = ga.now_utc()
            repair = finish(task.name + "-REPAIR", 2, minimal, parent=task.name)
            check(review_status(repair)["status"] == "ManagedByParent", "a repair must not recursively offer another review")
            recs = recommendations([active_task_signal(task), active_task_signal(repair)])
            check(not any("主动询问" in item["reason"] for item in recs), "signals must continue the already opted-in parent review")
            expect_governance_error("round before repaired delivery completion", lambda: write(task, entry(task, 3, repair, started_at=started_before_repair)))
            expect_governance_error("recursive repair offer", lambda: start(repair))
            write(task, entry(task, 3, repair))
            check(review_status(task)["clean_streak"] == 1, "verified repair must start a new clean streak")
            write(task, entry(task, 4, repair))
            check(review_status(task)["status"] == "Passed" and review_status(task)["reviewed_delivery"]["task_id"] == repair.name, "pass must identify the reviewed repair, not its original result")
            check(not validate_task_directory(task) and not validate_task_directory(repair), "both carriers must retain valid engineering records")

            current_id = "T-CURRENT-MIN" if minimal else "T-CURRENT-FULL"
            artifact = root / f"{current_id}-output.txt"

            def version_ref(tid, value):
                artifact.write_bytes(value.encode("utf-8"))
                proof = root / f"{tid}-delivery.json"
                proof.write_text(json.dumps({"path": str(artifact), "text": artifact.read_text(encoding="utf-8"),
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}, ensure_ascii=False), encoding="utf-8")
                return str(proof)

            original = finish(current_id, 20, minimal, source_ref=version_ref(current_id, "Alpha\n"))
            start(original)
            write(original, entry(original, 1))
            finish(current_id + "-UNRELATED", 21, minimal)
            check(review_status(original)["clean_streak"] == 1, "an unrelated completed task must not replace the review delivery")
            beta_id = current_id + "-BETA"
            beta = finish(beta_id, 22, minimal, parent=current_id, source_ref=version_ref(beta_id, "Beta\n"))
            state = review_status(original)
            check(artifact.read_text(encoding="utf-8") == "Beta\n" and state["status"] == "Stale" and state["clean_streak"] == 0
                  and state["current_delivery"]["task_id"] == beta_id, "a saved new repair must immediately replace the old clean delivery before any new round")
            original_path = load(original)[0]
            before_rejection = original_path.read_bytes()
            expect_governance_error("old original delivery after repair", lambda: write(original, entry(original, 2)))
            check(original_path.read_bytes() == before_rejection, "rejecting an old delivery must preserve the review history")
            write(original, entry(original, 2, beta))
            check(review_status(original)["clean_streak"] == 1, "the current Beta delivery must start from one clean round")
            gamma_id = current_id + "-GAMMA"
            gamma = finish(gamma_id, 23, minimal, parent=current_id, source_ref=version_ref(gamma_id, "Gamma\n"))
            check(review_status(original)["status"] == "Stale" and review_status(original)["clean_streak"] == 0, "a later repair must invalidate a previous repair's first clean round")
            before_rejection = original_path.read_bytes()
            expect_governance_error("old repaired delivery after a newer repair", lambda: write(original, entry(original, 3, beta)))
            check(original_path.read_bytes() == before_rejection, "rejecting an old repair must preserve the review history")
            write(original, entry(original, 3, gamma))
            check(review_status(original)["clean_streak"] == 1, "the current Gamma delivery must restart the clean streak")
            write(original, entry(original, 4, gamma))
            state = review_status(original)
            check(state["status"] == "Passed" and state["clean_streak"] == 2 and state["current_delivery"]["task_id"] == gamma_id,
                  "only two complete reviews of the current saved delivery may pass")
            check(not validate_task_directory(original), "version succession must preserve valid engineering and review records")

            identity_task = finish("T-IDENTITY-MIN" if minimal else "T-IDENTITY-FULL", 30, minimal)
            start(identity_task)
            captured = entry(identity_task, 1)
            write(identity_task, captured)
            captured_report = root / captured["report_ref"]
            captured_bytes = captured_report.read_bytes()
            captured_report.write_bytes(captured_bytes + b"Synthetic correction after review\n")
            check(review_status(identity_task)["status"] == "Stale" and review_status(identity_task)["clean_streak"] == 0,
                  "a changed report must invalidate its original clean round")
            reused = entry(identity_task, 2)
            (root / reused["report_ref"]).write_bytes(captured_bytes)
            identity_path, old_out, original_before, _ = load(identity_task)
            unchanged = identity_path.read_bytes()
            expect_governance_error("reuse recorded report content after its file changed", lambda: write(identity_task, reused))
            check(identity_path.read_bytes() == unchanged, "rejecting reused historical content must not change either carrier")
            captured_report.unlink()
            expect_governance_error("reuse recorded report content after its file disappeared", lambda: write(identity_task, reused))
            check(identity_path.read_bytes() == unchanged, "a missing original report must not release its recorded identity")
            # Read a synthetic saved history produced by the prior public-CLI bug.
            # Its copied report must not regain a clean count when the old file changes.
            faulty = copy.deepcopy(old_out)
            for old_round in faulty["adversarial_review"]:
                old_round.pop("session_completed", None)
            duplicate = {**copy.deepcopy(faulty["adversarial_review"][-1]), **reused}
            duplicate["report_sha256"] = faulty["adversarial_review"][-1]["report_sha256"]
            faulty["adversarial_review"].append(duplicate)
            hashes = {captured["round_id"]: None, reused["round_id"]: duplicate["report_sha256"]}
            recovered = review_state(faulty, original_before, report_hashes=hashes)
            check(recovered["status"] == "RestartRequired" and recovered["clean_streak"] == 0,
                  "a persisted old claimed pair cannot count or restore authorization")
            third = entry(identity_task, 3)
            third_sha = hashlib.sha256((root / third["report_ref"]).read_bytes()).hexdigest()
            faulty["adversarial_review"].append({**copy.deepcopy(duplicate), **third, "report_sha256": third_sha})
            hashes[third["round_id"]] = third_sha
            recovered = review_state(faulty, original_before, report_hashes=hashes)
            check(recovered["status"] == "RestartRequired" and recovered["clean_streak"] == 0,
                  "a prior ended or ambiguous old session needs a new decision before further reports count")
            faulty["adversarial_review"].append({"event": "Offer", "recorded_at": ga.now_utc(),
                "prompt": "Synthetic question accepted after the prior erroneous pass", "evidence_ref": "self-test://historical-offer"})
            check(review_state(faulty, original_before, report_hashes=hashes)["status"] == "AwaitingUser",
                  "invalid old counting must not make a historical post-pass Offer unreadable")
            faulty["adversarial_review"].append({"event": "Decision", "recorded_at": ga.now_utc(), "outcome": "Accepted",
                "response": "Synthetic later explicit opt-in", "decided_by": "synthetic-user", "evidence_ref": "self-test://historical-decision"})
            recovered = review_state(faulty, original_before, report_hashes=hashes)
            check(recovered["status"] == "BudgetRequired" and recovered["clean_streak"] == 0,
                  "a readable historical restart without limits requires a real bounded decision")
            write(identity_task, entry(identity_task, 3))
            check(review_status(identity_task)["clean_streak"] == 1, "one genuinely new report must restart the clean streak")
            write(identity_task, entry(identity_task, 4))
            check(review_status(identity_task)["status"] == "Passed" and not validate_task_directory(identity_task),
                  "two distinct new reports must still converge without rewriting stale history")

            ended_task = finish("T-ENDED-MIN" if minimal else "T-ENDED-FULL", 40, minimal)
            start(ended_task)
            ended_path = load(ended_task)[0]
            unchanged = ended_path.read_bytes()
            expect_governance_error("false completion claim on first round", lambda: write(ended_task, entry(ended_task, 1, session_completed=True)))
            check(ended_path.read_bytes() == unchanged, "a fabricated completion claim must not be written")
            write(ended_task, entry(ended_task, 1))
            check(load(ended_task)[1]["adversarial_review"][-1]["session_completed"] is False, "one round must not end its authorization session")
            unchanged = ended_path.read_bytes()
            expect_governance_error("false incomplete claim on clean pair", lambda: write(ended_task, entry(ended_task, 2, session_completed=False)))
            check(ended_path.read_bytes() == unchanged, "a caller cannot suppress a real session completion")
            write(ended_task, entry(ended_task, 2))
            _, ended_out, ended_before, _ = load(ended_task)
            check(ended_out["adversarial_review"][-1]["session_completed"] is True, "the machine must record when its clean pair ended the session")
            import adversarial_review as ar
            legacy = copy.deepcopy(ended_out)
            for old_round in legacy["adversarial_review"]:
                if old_round["event"] == "Round":
                    for field in ("session_completed", "review_contract_version", "report_ref", "report_sha256", "delivery_verified_at", "delivery_completed_at"):
                        old_round.pop(field, None)
                    old_round["requirements_sha256"] = ar._legacy_requirements_subject(ended_before)
            check(review_state(legacy, ended_before)["status"] == "LegacyNotRevalidated", "old completed pairs remain readable without claiming current passage")
            corrected_before = copy.deepcopy(ended_before)
            corrected_before["clarification"]["basis"] += " Synthetic later explanation correction"
            check(review_state(legacy, corrected_before)["status"] == "RestartRequired", "metadata changes must not reactivate an ended legacy authorization")
            ended_report = ended_task / "evidence/round-2.md"
            ended_report.write_bytes(ended_report.read_bytes() + b"Synthetic post-completion evidence correction\n")
            state = review_status(ended_task)
            check(state["status"] == "RestartRequired" and state["clean_streak"] == 0, "proof invalidation must preserve the ended session boundary")
            unchanged = ended_path.read_bytes()
            expect_governance_error("ended review cannot restart with old opt-in", lambda: write(ended_task, entry(ended_task, 3)))
            expect_governance_error("ended review cannot continue as blocked", lambda: write(ended_task, {"event": "Blocked", "recorded_at": ga.now_utc(), "reason": "Synthetic blocked after end", "evidence_refs": ["self-test://ended"]}))
            check(ended_path.read_bytes() == unchanged, "rejected restarts must preserve outcome bytes and revisions")
            recs = recommendations([active_task_signal(ended_task)])
            check(any("新决定" in item["reason"] for item in recs), "recommendations must request a new decision for an ended stale session")
            choose(ended_task, "Accepted")
            check(review_status(ended_task)["status"] == "InProgress" and review_status(ended_task)["clean_streak"] == 0, "a real new decision may restart without fabricating another Offer")
            write(ended_task, entry(ended_task, 3))
            check(review_status(ended_task)["clean_streak"] == 1, "a restarted session must earn its first clean round again")
            write(ended_task, entry(ended_task, 4))
            check(review_status(ended_task)["status"] == "Passed" and not validate_task_directory(ended_task), "only a second new clean report may complete the restarted session")

            # Bounded work, renewal and accounting use the same public API on
            # both carriers. These are synthetic checks, not real review rounds.
            from adversarial_review import require_review_parent
            from review_budget import DEFAULT_BUDGET, budget_state
            from datetime import datetime, timedelta
            task = finish("T-BUDGET-MIN" if minimal else "T-BUDGET-FULL", 90, minimal)
            path = load(task)[0]
            write(task, {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic finite review offer", "evidence_ref": "self-test://budget-offer"})
            check(load(task)[1]["adversarial_review"][-1]["budget"] == DEFAULT_BUDGET, "new offers must persist finite defaults")
            unchanged = path.read_bytes()
            expect_governance_error("cannot increase offered limits at acceptance", lambda: write(task, {"event": "Decision", "recorded_at": ga.now_utc(), "outcome": "Accepted", "response": "Synthetic yes", "decided_by": "synthetic-user", "evidence_ref": "self-test://budget-answer", "budget": {"review_rounds": 30, "repair_batches": 20, "elapsed_minutes": 600}}))
            check(path.read_bytes() == unchanged, "a denied budget change must not mutate either carrier")
            choose(task, "Accepted")
            write(task, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Review", "work_id": "B-1", "evidence_refs": ["self-test://review-start"]})
            check(review_status(task)["budget"]["used"]["review_rounds"] == 1, "charge at start, before a completed report exists")
            unchanged = path.read_bytes()
            expect_governance_error("interrupted start cannot be refunded by reusing id", lambda: write(task, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Review", "work_id": "B-1", "evidence_refs": ["self-test://repeat-start"]}))
            check(path.read_bytes() == unchanged, "a rejected duplicate start preserves the charged receipt")
            write(task, entry(task, 1, findings=[{"id": "F-BUDGET", "summary": "Synthetic unresolved issue", "evidence_refs": ["self-test://budget-repro"]}]))
            check(review_status(task)["budget"]["used"]["review_rounds"] == 1, "finishing an already charged review must not charge twice")
            _, _, parent_contract, _ = load(task)
            repair_contract = {"depends_on": [task.name], "project_id": parent_contract["project_id"]}
            repair_id = task.name + "-FIX"
            expect_governance_error("repair without a prior charged reservation", lambda: require_review_parent(task.parent / repair_id, repair_contract, task.name))
            for repair in (repair_id, repair_id + "-2"):
                write(task, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Repair", "work_id": repair, "evidence_refs": ["self-test://repair-budget"]})
            state = review_status(task)
            check(state["status"] == "BudgetExhausted" and state["budget"]["exhausted_by"] == ["repair_batches"], "the last permitted repair start must stop all further work")
            check(require_review_parent(task.parent / repair_id, repair_contract, task.name) == task.name, "a charged last repair may save its engineering outcome at the cap")
            unchanged = path.read_bytes()
            expect_governance_error("no new review after repair cap", lambda: write(task, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Review", "work_id": "B-2", "evidence_refs": ["self-test://over-budget"]}))
            expect_governance_error("report-only callers cannot bypass the cap", lambda: write(task, entry(task, 2)))
            check(path.read_bytes() == unchanged and review_status(task)["open_findings"] == ["F-BUDGET"], "exhaustion preserves both outcome bytes and unresolved issues")
            check(any("预算" in item["reason"] and "等待用户" in item["reason"] for item in recommendations([active_task_signal(task)])), "status must hand control to the user instead of recommending repair")
            grant = next(item for item in load(task)[1]["adversarial_review"] if item["event"] == "Decision")
            instant = datetime.fromisoformat(grant["recorded_at"].replace("Z", "+00:00"))
            check(budget_state([grant], at=instant + timedelta(minutes=59, seconds=59))["status"] == "Available", "time is available just before the deadline")
            check(budget_state([grant], at=instant + timedelta(minutes=60))["exhausted_by"] == ["elapsed_minutes"], "time stops exactly at the deadline without waiting for another report")
            write(task, {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic issue summary and two-round continuation offer", "evidence_ref": "self-test://budget-renewal", "budget": {"review_rounds": 2, "repair_batches": 2, "elapsed_minutes": 60}})
            check(review_status(task)["status"] == "AwaitingUser", "presenting a renewal is not authorization")
            choose(task, "Deferred")
            expect_governance_error("deferred renewal cannot start work", lambda: write(task, entry(task, 2)))
            choose(task, "Accepted")
            check(review_status(task)["budget"]["used"] == {"review_rounds": 0, "repair_batches": 0} and review_status(task)["open_findings"] == ["F-BUDGET"], "a real new bounded decision renews counters and retains original issues")
            write(task, entry(task, 2, resolutions=[{"finding_id": "F-BUDGET", "disposition": "NotAnIssue", "reason": "Synthetic counterevidence", "evidence_refs": ["self-test://disproof"]}]))
            check(review_status(task)["clean_streak"] == 1 and review_status(task)["status"] != "Passed", "one clean round cannot pass after renewal")
            write(task, {"event": "WorkStarted", "recorded_at": ga.now_utc(), "work_type": "Review", "work_id": "B-3", "evidence_refs": ["self-test://last-permitted-review"]})
            check(review_status(task)["status"] == "BudgetExhausted", "a charged last round consumes the review cap before completion")
            write(task, entry(task, 3))
            check(review_status(task)["status"] == "Passed" and review_status(task)["clean_streak"] == 2, "a real second clean report may pass exactly at the cap")
            unchanged = path.read_bytes()
            expect_governance_error("no unsolicited round after a bounded pass", lambda: write(task, entry(task, 4)))
            check(path.read_bytes() == unchanged and not validate_task_directory(task), "bounded pass remains valid and cannot launch extra work")

            one = finish("T-ONE-MIN" if minimal else "T-ONE-FULL", 91, minimal)
            write(one, {"event": "Offer", "recorded_at": ga.now_utc(), "prompt": "Synthetic single-round budget", "evidence_ref": "self-test://one-offer", "budget": {"review_rounds": 1, "repair_batches": 2, "elapsed_minutes": 60}})
            choose(one, "Accepted")
            write(one, entry(one, 1))
            check(review_status(one)["status"] == "BudgetExhausted" and review_status(one)["clean_streak"] == 1, "exhausting a single-round budget must never imply a pass")
            expect_governance_error("the next report cannot exceed a completed-round cap", lambda: write(one, entry(one, 2)))

        for batch in (False, True):
            task = finish("T-CONCURRENT-BATCH" if batch else "T-CONCURRENT-SINGLE", 10 if batch else 9)
            start(task)
            path, out, before, events = load(task)
            answer = {"outcome": "Rejected", "presented": "Synthetic saved delivery", "response": "Synthetic rejection", "decided_by": "synthetic-user", "decided_at": ga.now_utc(), "evidence_ref": "self-test://user-rejection", "subject_sha256": ga.user_decision_subject_sha256(before, events, out)}
            round_value = entry(task, 1, findings=[{"id": "F-KEEP", "summary": "Synthetic confirmed issue", "evidence_refs": ["self-test://repro"]}])
            paused = threading.Event()
            release = threading.Event()
            errors = []
            original_write = ga.atomic_write_json

            def delayed_write(target, document):
                if Path(target).resolve() == path.resolve() and threading.current_thread().name == "human-update":
                    paused.set()
                    if not release.wait(5):
                        raise RuntimeError("synthetic schedule timed out")
                return original_write(target, document)

            def human_update():
                try:
                    if batch:
                        ga.amend_record_batch(path, changes=[{"path": "user_decision", "value": answer}], reason="Synthetic actual user answer", basis="self-test://concurrent")
                    else:
                        ga.amend_record(path, dotted_path="user_decision", new_value=answer, reason="Synthetic actual user answer", basis="self-test://concurrent")
                except Exception as exc:
                    errors.append(str(exc))

            def review_update():
                try:
                    write(task, round_value)
                except Exception as exc:
                    errors.append(str(exc))

            ga.atomic_write_json = delayed_write
            first = threading.Thread(target=human_update, name="human-update")
            second = threading.Thread(target=review_update, name="review-update")
            try:
                first.start()
                require_test(paused.wait(5), "human update never reached the deterministic pause")
                second.start()
                time.sleep(0.05)
                check(second.is_alive(), "the review writer must wait for the same record lock")
                release.set()
                first.join(5)
                second.join(5)
            finally:
                release.set()
                first.join(5)
                if second.ident is not None:
                    second.join(5)
                ga.atomic_write_json = original_write
            final = read_json(path)
            check(not first.is_alive() and not second.is_alive() and not errors, "both public writers must finish without lost-update errors")
            check(final["user_decision"]["outcome"] == "Rejected" and review_status(task)["open_findings"] == ["F-KEEP"], "concurrent updates must preserve both user decision and confirmed issue")
            check(final["revision"] == out["revision"] + 2 and not validate_task_directory(task), "concurrent successful writers need distinct revisions and a valid result")
    return {"status": "Passed", "checks": checks}


def run_saved_result_user_decision_fixture() -> dict[str, object]:
    """Engineering results survive delayed acceptance; actual decisions remain source-bound."""
    from governance_artifacts import now_utc, read_jsonl, user_decision_subject_sha256, user_decision_label, initial_user_decision
    from minimal_task import record_minimal_review, minimal_approval_contract

    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        require_test(condition, message)
        checks += 1

    def answer(before: dict, events: list, outcome: dict, state: str = "Approved") -> dict:
        return {"outcome": state, "presented": "Synthetic saved engineering result",
                "response": f"Synthetic external answer: {state}", "decided_by": "synthetic-user",
                "decided_at": now_utc(), "evidence_ref": "self-test://external-review-source",
                "subject_sha256": user_decision_subject_sha256(before, events, outcome)}

    with tempfile.TemporaryDirectory(prefix="v63-saved-result-") as temp:
        root = Path(temp)
        task = new_task(root, "T-SAVED-RESULT", 1)
        append_run_event(task, run_id="RUN-SAVED", attempt_id="A01", event_type="run_started", summary="Start synthetic work", status="started")
        append_run_event(task, run_id="RUN-SAVED", attempt_id="A01", event_type="verification", summary="Verify synthetic delivery", status="succeeded", evidence_refs=["self-test://saved-result-check"])
        record_fixture_acceptance(task)
        before = read_json(task / "before.json")
        before["decisions"] = [item for item in before["decisions"] if item["kind"] != "Acceptance"]
        atomic_write_json(task / "before.json", before)
        append_run_event(task, run_id="RUN-SAVED", attempt_id="A01", event_type="human_gate", summary="Synthetic independent engineering gate", status="succeeded", evidence_refs=["self-test://independent-check"], gate={
            "id": "independent-review", "outcome": "Passed", "subject_sha256": approval_subject_sha256(before, read_jsonl(task / "run.jsonl")),
            "decided_by": "synthetic-reviewer", "decided_at": now_utc(), "authority_ref": "self-test://authority"})
        append_run_event(task, run_id="RUN-SAVED", attempt_id="A01", event_type="run_finished", summary="Engineering work finished", status="succeeded")
        after_path = close_task(task, status="Implemented", established_facts=["Synthetic delivery verified"], actual_changes=["Synthetic authorized change"], verification=[{
            "summary": "Synthetic delivery check", "result": "Passed", "evidence_refs": ["self-test://saved-result-check"]}])
        outcome = read_json(after_path)
        events = read_jsonl(task / "run.jsonl")
        check(outcome["user_decision"] == {"outcome": "Pending"}, "Full result must exist before a human answer")
        check(not validate_task_directory(task), "Full pending result must satisfy engineering invariants")
        check(outcome["verification"][0]["result"] == "Passed" and outcome["actual_changes"], "pending result lost the delivery facts")
        pending_signal = active_task_signal(task)
        check(pending_signal["pending_acceptance"] and pending_signal["engineering_recorded"], "saved results must still show pending acceptance")
        check(all(item["command"] != "run" for item in recommendations([pending_signal])), "waiting for a human must not recommend repeating engineering work")
        state = read_json(rebuild_project_state(root, "P-TEST"))
        check(state["source_tasks"][0]["user_decision"] == "Pending", "project state must distinguish engineering result and user decision")
        entry = console_model._task_entry(task, {"task_id": task.name}, "Implemented", root)
        check(user_decision_label(entry["user_decision"]) == "待用户验收", "console must not label a pending result as accepted")
        public_status = subprocess.run([sys.executable, "-X", "utf8", str(skill_root_path() / "scripts/signals.py"), "--project-root", str(root)], capture_output=True, text=True, encoding="utf-8")
        check(public_status.returncode == 0 and json.loads(public_status.stdout)["task_progress"][0]["engineering_recorded"]
              and json.loads(public_status.stdout)["task_progress"][0]["user_decision"] == "Pending", "public status must expose the independent saved result and pending decision")
        before_bytes, ledger_bytes, pending_bytes = (task / "before.json").read_bytes(), (task / "run.jsonl").read_bytes(), after_path.read_bytes()
        real_answer = answer(before, events, outcome)
        known = copy.deepcopy(before)
        known_answer = {**real_answer, "id": "D-KNOWN", "kind": "Acceptance", "subject_sha256": approval_subject_sha256(before, events)}
        known["decisions"].append(known_answer)
        carried = initial_user_decision(known, events, outcome)
        check(carried["outcome"] == "Approved" and carried["response"] == real_answer["response"]
              and carried["evidence_ref"] == real_answer["evidence_ref"], "an existing real answer for this delivery must be retained without another question")
        legacy_answer = {key: value for key, value in known_answer.items() if key not in {"outcome", "subject_sha256", "evidence_ref"}}
        enriched_answer = {**known_answer, "id": "D-ENRICHED", "enriches": "D-KNOWN"}
        known["decisions"] = [*before["decisions"], legacy_answer, enriched_answer]
        check(initial_user_decision(known, events, outcome)["outcome"] == "Approved", "evidence-backed enrichment must not turn an existing answer into Pending")
        known["decisions"] = [*before["decisions"], {**known_answer, "subject_sha256": "0" * 64}]
        check(initial_user_decision(known, events, outcome) == {"outcome": "Pending"}, "an answer for a different delivery must not be silently carried forward")
        invalid = []
        for key in ("presented", "response", "decided_by", "evidence_ref"):
            bad = dict(real_answer); bad[key] = ""; invalid.append(bad)
        for key, value in (("subject_sha256", "0" * 64), ("decided_at", "2099-01-01T00:00:00Z"), ("decided_at", "2000-01-01T00:00:00Z")):
            bad = dict(real_answer); bad[key] = value; invalid.append(bad)
        invalid.append({"outcome": "Pending", "decided_by": "invented"})
        for bad in invalid:
            expect_governance_error("invalid actual decision must be rejected", lambda: amend_record(after_path, dotted_path="user_decision", new_value=bad, reason="synthetic invalid answer", basis="self-test://negative"))
            check(after_path.read_bytes() == pending_bytes, "a rejected decision changed the saved engineering result")
        amend_record(after_path, dotted_path="user_decision", new_value=real_answer, reason="record a later external review", basis="self-test://external-review-source")
        accepted = read_json(after_path)
        check(accepted["user_decision"] == real_answer and not validate_task_directory(task), "a later evidence-backed decision must validate")
        check((task / "before.json").read_bytes() == before_bytes and (task / "run.jsonl").read_bytes() == ledger_bytes, "a later answer must not rewrite the contract or append to a finished run")
        check({k:v for k,v in accepted.items() if k not in {"user_decision", "revision", "amendments"}} == {k:v for k,v in outcome.items() if k not in {"user_decision", "revision", "amendments"}}, "a later user decision changed engineering facts")
        check(not active_task_signal(task)["pending_acceptance"], "approved results must stop showing pending acceptance")
        accepted_bytes = after_path.read_bytes()
        expect_governance_error("a verdict cannot be flipped independently of its actual source", lambda: amend_record(after_path, dotted_path="user_decision.outcome", new_value="Rejected", reason="synthetic unsupported flip", basis="self-test://negative"))
        check(after_path.read_bytes() == accepted_bytes, "a partial verdict update changed the saved decision")
        expect_governance_error("old approval cannot authorise a different verification version", lambda: amend_record(after_path, dotted_path="verification", new_value=[{"summary": "different unreviewed delivery", "result": "Passed", "evidence_refs": ["self-test://different-source/v2"]}], reason="synthetic stale answer", basis="self-test://negative"))
        check(after_path.read_bytes() == accepted_bytes, "stale approval allowed a delivery change")
        amend_record(after_path, dotted_path="actual_changes", new_value=["Corrected description of the same verified delivery"], reason="correct result prose without changing delivery", basis="self-test://report-correction")
        accepted = read_json(after_path)
        check(accepted["user_decision"] == real_answer, "correcting result prose must not erase a real answer or require the user to repeat it")
        rejection = answer(before, events, accepted, "Rejected")
        amend_record(after_path, dotted_path="user_decision", new_value=rejection, reason="later actual external rejection", basis="self-test://external-review-source")
        rejected_bytes = after_path.read_bytes()
        expect_governance_error("an older approval cannot overwrite a later rejection", lambda: amend_record(after_path, dotted_path="user_decision", new_value=real_answer, reason="synthetic old approval", basis="self-test://negative"))
        check(after_path.read_bytes() == rejected_bytes and read_json(after_path)["status"] == "Implemented", "rejection must remain separate from engineering status")
        legacy = dict(outcome); legacy.pop("user_decision")
        atomic_write_json(after_path, legacy)
        check(any("Acceptance" in item for item in validate_task_directory(task)), "old current-format records must not silently bypass their original acceptance proof")
        after_path.write_bytes(rejected_bytes)

        mini = minimal_fixture_record(root, "T-SAVED-MINIMAL")
        append_minimal_event(mini.parent, event_type="run_started", summary="Start synthetic Minimal work", status="started")
        append_minimal_event(mini.parent, event_type="verification", summary="Verify Minimal delivery", status="succeeded", evidence_refs=["self-test://minimal-check"])
        record_fixture_acceptance(mini.parent)
        record = read_json(mini)
        record["task_contract"]["decisions"] = [item for item in record["task_contract"]["decisions"] if item["kind"] != "Acceptance"]
        atomic_write_json(mini, record)
        close_minimal_record(mini.parent, status="Implemented", established_facts=["Synthetic Minimal verified"], actual_changes=["Synthetic Minimal edit"], verification=["Passed::Synthetic Minimal check::self-test://minimal-check"])
        completed = read_json(mini)
        check(completed["task_outcome"]["user_decision"] == {"outcome": "Pending"}, "Minimal must save its result before a human answer")
        check(not validate_minimal_record(completed, task_dir=mini.parent), "Minimal pending result must validate")
        check(active_task_signal(mini.parent)["pending_acceptance"], "Completed Minimal engineering work can still await the user")
        mini_answer = answer(minimal_approval_contract(completed), completed["run_ledger"], completed["task_outcome"])
        payload = root / "external-decision.json"
        atomic_write_json(payload, mini_answer)
        command = subprocess.run([sys.executable, "-X", "utf8", str(skill_root_path() / "scripts/manage_minimal_task.py"), "record-review", str(mini.parent), "--user-decision-json-file", str(payload), "--reason", "later external review", "--basis", "self-test://external-review-source"], capture_output=True, text=True, encoding="utf-8")
        check(command.returncode == 0, f"Minimal later-decision CLI failed: {command.stdout}{command.stderr}")
        updated = read_json(mini)
        check(updated["task_contract"] == completed["task_contract"] and updated["run_ledger"] == completed["run_ledger"], "Minimal later decision rewrote execution history")
        check(updated["task_outcome"]["user_decision"] == mini_answer and not active_task_signal(mini.parent)["pending_acceptance"], "Minimal later approval was not saved independently")
        check(not validate_minimal_record(updated, task_dir=mini.parent), "Minimal later answer invalidated the saved result")
        command = subprocess.run([sys.executable, "-X", "utf8", str(skill_root_path() / "scripts/get_approval_subject.py"), str(mini.parent)], capture_output=True, text=True, encoding="utf-8")
        check(command.returncode == 0 and command.stdout.strip() == mini_answer["subject_sha256"], "approval subject must bind the saved result after close")
    return {"status": "Passed", "checks": checks}


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
        {"state": "Open", "mode": "Asked", "notice": "n", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "b", "reopened_by": []}
    )
    require_test(bool(unsettled), "an unsettled clarification must block")
    ambiguous = validate_clarification({
        "state": "Settled", "mode": "Asked", "notice": "n", "survey_refs": ["surveyed.md"], "basis": "b", "reopened_by": [],
        "rounds": [{"ordinal": 1, "asked_at": "2026-08-15T00:00:00Z", "exchanges": [
            {"question": "q", "changes": "Scope", "recommended_default": "d",
             "answer": "maybe", "answer_state": "Ambiguous"}]}],
    })
    require_test(bool(ambiguous), "an ambiguous answer must keep the task open")
    settled = validate_clarification({
        "state": "Settled", "mode": "Skipped", "notice": skip_notice,
        "survey_refs": ["surveyed.md"], "rounds": [], "basis": "surveyed", "reopened_by": [],
    })
    require_test((not settled), f"a surveyed zero-round record must pass, got {settled}")

    # An open answer is closed by a later answer that follows it up, and by nothing
    # else. Before follows_up existed a record that asked again honestly could never
    # settle, so the only way through was to relabel the first answer -- and a real
    # task did exactly that. Both halves are held here: the honest path settles, and
    # the shortcut is refused at the amendment boundary.
    def _asked(*rounds):
        return {"state": "Settled", "mode": "Asked", "notice": "n", "survey_refs": ["surveyed.md"],
                "basis": "b", "reopened_by": [],
                "rounds": [{"ordinal": index, "asked_at": "2026-09-14T00:00:00Z", "exchanges": list(exchanges)}
                           for index, exchanges in enumerate(rounds, start=1)]}

    def _answer(state, follows_up=None):
        exchange = {"question": "q", "changes": "Scope", "recommended_default": "d",
                    "answer": "a", "answer_state": state}
        if follows_up is not None:
            exchange["follows_up"] = follows_up
        return exchange

    require_test(
        (not validate_clarification(_asked([_answer("Ambiguous")], [_answer("Answered", "r1.e1")]))),
        "an ambiguous answer followed up and answered in a later round must settle",
    )
    require_test(
        (not validate_clarification(_asked([_answer("Deferred")], [_answer("DefaultAccepted", "r1.e1")]))),
        "a deferred answer followed up and accepted by default must settle",
    )
    require_test(
        (not validate_clarification(_asked([_answer("Ambiguous")], [_answer("Ambiguous", "r1.e1")],
                                           [_answer("Answered", "r2.e1")]))),
        "a chain of follow-ups that ends in a clear answer must resolve every open link",
    )
    require_test(
        (bool(validate_clarification(_asked([_answer("Ambiguous")], [_answer("Answered")])))),
        "a later answer that does not name the open one must not resolve it",
    )
    require_test(
        (bool(validate_clarification(_asked([_answer("Ambiguous")], [_answer("Ambiguous", "r1.e1")])))),
        "a follow-up that is itself still ambiguous must not resolve what it follows",
    )
    require_test(
        (not validate_clarification(_asked([_answer("Answered")]))),
        "a record without follows_up and without open answers must keep settling",
    )
    for label, record, expected in (
        ("a follow-up naming no recorded answer",
         _asked([_answer("Ambiguous")], [_answer("Answered", "r9.e1")]), "not a recorded answer"),
        ("a follow-up naming an answer in its own round",
         _asked([_answer("Ambiguous"), _answer("Answered", "r1.e1")]), "earlier round"),
        ("a follow-up naming an answer from a later round",
         _asked([_answer("Answered", "r2.e1")], [_answer("Ambiguous")]), "earlier round"),
        ("a follow-up naming an answer that was already answered",
         _asked([_answer("Answered")], [_answer("Answered", "r1.e1")]), "already answered"),
    ):
        problems = validate_clarification(record)
        require_test((any(expected in item for item in problems)), f"{label} must be refused, got {problems}")
    for schema_name, container in (
        ("task-before.schema.json", lambda doc: doc),
        ("minimal-task-record.schema.json", lambda doc: doc["properties"]["task_contract"]),
    ):
        exchange = container(read_json(skill_root / "assets" / "runtime" / "schemas" / schema_name))[
            "properties"]["clarification"]["properties"]["rounds"]["items"]["properties"]["exchanges"]["items"]
        require_test(
            ("follows_up" in exchange["properties"] and "follows_up" not in exchange["required"]),
            f"{schema_name} must accept an optional follows_up on every answer",
        )
    with tempfile.TemporaryDirectory(prefix="v63-clarification-history-") as temp:
        history_before = new_task(Path(temp), "T-HISTORY", 1) / "before.json"
        followed = _asked([_answer("Ambiguous")], [_answer("Answered", "r1.e1")])
        amend_record(history_before, dotted_path="clarification", new_value=followed,
                     reason="record a follow-up round", basis="self-test")
        relabelled = copy.deepcopy(followed)
        relabelled["rounds"][0]["exchanges"][0]["answer_state"] = "Answered"
        expect_governance_error(
            "an amendment relabelling an open answer as answered",
            lambda: amend_record(history_before, dotted_path="clarification", new_value=relabelled,
                                 reason="relabel", basis="self-test"),
        )
        expect_governance_error(
            "a batch amendment relabelling an open answer as answered",
            lambda: amend_record_batch(history_before, changes=[{"path": "clarification", "value": relabelled}],
                                       reason="relabel", basis="self-test"),
        )
        erased = copy.deepcopy(followed)
        erased["rounds"] = [dict(erased["rounds"][1], ordinal=1)]
        expect_governance_error(
            "an amendment erasing a recorded answer",
            lambda: amend_record(history_before, dotted_path="clarification", new_value=erased,
                                 reason="erase", basis="self-test"),
        )
        reopened_answer = copy.deepcopy(followed)
        reopened_answer["state"] = "Open"
        reopened_answer["rounds"][1]["exchanges"][0]["answer_state"] = "Ambiguous"
        amend_record(history_before, dotted_path="clarification", new_value=reopened_answer,
                     reason="the follow-up answer turned out ambiguous", basis="self-test")
        pursued = copy.deepcopy(reopened_answer)
        pursued["state"] = "Settled"
        pursued["rounds"].append({"ordinal": 3, "asked_at": "2026-09-14T00:00:00Z",
                                  "exchanges": [_answer("Answered", "r2.e1")]})
        amend_record(history_before, dotted_path="clarification", new_value=pursued,
                     reason="pursue the reopened answer", basis="self-test")
        require_test(
            (not validate_clarification(read_json(history_before)["clarification"])),
            "moving an answer back to open and pursuing it in a new round must stay possible",
        )

    # Skipping the question round is the cheap path, so it has to cost evidence: a
    # survey reference that resolves to a file someone could have read. "looked at it"
    # is not a survey, and neither is a directory that happens to exist.
    require_test(
        (validate_survey_refs(skill_root, {"survey_refs": ["看过了"]})),
        "an invented survey reference must not justify skipping the question round",
    )
    require_test(
        (validate_survey_refs(skill_root, {"survey_refs": ["scripts"]})),
        "a directory is not evidence that anything was read",
    )
    require_test(
        (not validate_survey_refs(skill_root, {"survey_refs": ["SKILL.md"]})),
        "a real file is a survey reference",
    )
    require_test(
        (not validate_survey_refs(skill_root, {"survey_refs": ["x://note", "SKILL.md:3"]})),
        "path:line resolves, and one real reference among others is enough",
    )

    # A clause with no acceptance criterion is a clause nobody can say is done. The
    # answer to that is a question, not an invented criterion.
    def _tie_contract(items):
        return {"request_snapshot": {"language": "zh", "text": "先改登录页；再加导出按钮",
                                     "captured_at": "2026-08-15T00:00:00Z"},
                "acceptance": {"criteria": ["登录页与导出按钮均可用"]},
                "clarification": {"state": "Settled", "mode": "Skipped", "notice": "n",
                                  "survey_refs": ["SKILL.md"], "rounds": [], "basis": "b",
                                  "reopened_by": []},
                "requirement_items": items}

    def _tie_item(quote, **over):
        base = {"id": "R-01", "source": "request_snapshot", "quote": quote, "reading": "r",
                "state": "Covered", "evidence_refs": ["e://1"], "acceptance_refs": [0]}
        base.update(over)
        return base

    untied = validate_requirement_items(_tie_contract([_tie_item("先改登录页", acceptance_refs=[]),
                                                       _tie_item("再加导出按钮", id="R-02")]))
    require_test(
        (any("no acceptance criterion" in item for item in untied)),
        f"a requirement with no acceptance criterion must be refused; got {untied}",
    )
    require_test(
        (any("out of range" in item for item in
             validate_requirement_items(_tie_contract([_tie_item("先改登录页", acceptance_refs=[7]),
                                                       _tie_item("再加导出按钮", id="R-02")])))),
        "an acceptance_ref pointing at no criterion must be refused",
    )
    require_test(
        (not validate_requirement_items(_tie_contract(
            [_tie_item("先改登录页", state="NotARequirement", acceptance_refs=[]),
             _tie_item("再加导出按钮", id="R-02")]))),
        "a clause marked as not a requirement needs no criterion",
    )

    # Technical history is preserved without manufacturing one question per marker.
    base_clarification = {"state": "Settled", "mode": "Skipped", "notice": "n",
        "survey_refs": ["SKILL.md"], "rounds": [], "basis": "b",
        "reopened_by": ["failures:2", "failures:3", "amendment:scope.allowed_paths"]}
    require_test(not validate_clarification(base_clarification), "technical markers cannot require synthetic question rounds")
    require_test(validate_clarification({**base_clarification, "state": "Open"}), "old Open state is not silently cleared")
    require_test(validate_clarification({**base_clarification, "reopened_by": ["amendment:acceptance"]}),
                 "substantive uncertainty still requires real clarification")
    require_test(reconcile_required_gates({"authority": {"required_gates": ["independent-review"]}},
        [{"event_type": "human_gate", "status": "recorded", "summary": "independent-review not executed"}]),
        "a pending gate name is not a Passed gate")

    # Both carriers are exercised through their real entrypoints by the lifecycle
    # fixtures; implementation-text inspection is not evidence of a working gate.

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
                "decided_by": "someone", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"}
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
                         "survey_refs": ["surveyed.md"], "rounds": [], "basis": "b", "reopened_by": []}
        if answer is not None:
            clarification = {**clarification, "mode": "Asked", "rounds": [{
                "ordinal": 1, "asked_at": "2026-08-15T00:00:00Z",
                "exchanges": [{"question": "q", "changes": "Scope", "recommended_default": "d",
                               "answer": answer, "answer_state": "Answered"}]}]}
        return {"request_snapshot": {"language": "zh", "text": "先改登录页；再加导出按钮",
                                     "captured_at": "2026-08-15T00:00:00Z"},
                "acceptance": {"criteria": ["登录页与导出按钮均可用"]},
                "clarification": clarification, "requirement_items": items}

    def _item(quote, **over):
        base = {"id": "R-01", "source": "request_snapshot", "quote": quote,
                "reading": "r", "state": "Covered", "evidence_refs": ["e://1"],
                "acceptance_refs": [0]}
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
    requirement_review_validation = run_requirement_review_fixture()
    new_query_history_validation = run_new_query_history_fixture()
    document_governance_validation = run_document_governance_fixture()
    amendment_growth_validation = run_amendment_growth_fixture()
    saved_result_validation = run_saved_result_user_decision_fixture()
    adversarial_review_validation = run_adversarial_review_fixture()
    adversarial_boundary_validation = run_adversarial_boundary_fixture()
    approval_time_validation = run_approval_time_fixture()
    closed_scope_history_validation = run_closed_scope_history_fixture()
    historical_proof_compatibility_validation = run_historical_proof_compatibility_fixture()
    verification_recovery_validation = run_verification_recovery_fixture()
    failure_terminal_validation = run_failure_and_terminal_fixture()
    review_boundary_validation = run_review_boundary_regressions_fixture()
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
    # The same parser as rendered by Python 3.12 and 3.13: up to 3.12, adjacent mutually
    # exclusive groups created out of argument order print as one bracket pair.
    help_312 = (
        "usage: tool.py [-h] --task-id TASK_ID\n"
        "               [--items-base64 ITEMS_BASE64 | --items-file ITEMS_FILE  --questions-base64 QUESTIONS_BASE64 | --questions-file QUESTIONS_FILE]\n"
        "               [--stage STAGE]\n"
        "\n"
        "options:\n"
        "  --stage STAGE  stage (default: S1)\n"
    )
    help_313 = (
        "usage: tool.py [-h] --task-id TASK_ID\n"
        "               [--items-base64 ITEMS_BASE64 |\n"
        "               --items-file ITEMS_FILE]\n"
        "               [--questions-base64 QUESTIONS_BASE64 |\n"
        "               --questions-file QUESTIONS_FILE]\n"
        "               [--stage STAGE]\n"
        "\n"
        "options:\n"
        "  --stage STAGE  stage (default: S1)\n"
    )
    require_test(
        canonical_help(help_312) == canonical_help(help_313),
        "a CLI help contract must not depend on how the interpreter brackets exclusive groups",
    )
    require_test(
        canonical_help(help_313.replace("--stage", "--phase")) != canonical_help(help_313),
        "a renamed flag must still change a CLI help contract",
    )
    require_test(
        canonical_help(help_313.replace("(default: S1)", "(default: S2)")) != canonical_help(help_313),
        "changed help text must still change a CLI help contract",
    )
    require_test(
        "(default: S1)" in canonical_help(help_313),
        "grouping punctuation may only be dropped from the usage paragraph",
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
    require_test((document_governance_validation == {"status": "Passed", "checks": 17}), "document governance must execute all 17 positive and negative controls")
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
        # Amending the scope reopened S1, which is the whole point: the plan changed
        # because the reading of the request changed. Settling it again costs a real
        # round -- flipping the state back is not answering anything.
        amend_record(
            task_dir / "before.json",
            dotted_path="clarification",
            new_value={
                "state": "Settled", "mode": "Asked",
                "notice": "针对你的需求和项目现状，有几个问题需要你先回答，以保证本需求完成的质量",
                "survey_refs": ["surveyed.md"],
                "rounds": [{
                    "ordinal": 1, "asked_at": "2026-08-15T00:00:00Z",
                    "exchanges": [{
                        "question": "扩大后的范围是否包含生成视图？", "changes": "Scope",
                        "recommended_default": "包含", "answer": "包含",
                        "answer_state": "Answered",
                    }],
                }],
                "basis": "the scope amendment raised a question that was asked",
                "reopened_by": ["amendment:scope.in_scope"],
            },
            reason="answer the question the scope change raised",
            basis="self-test",
        )
        amended_items = read_json(task_dir / "before.json")["requirement_items"] + [{
            "id": "R-02", "source": "clarification:r1.e1", "quote": "包含",
            "reading": "generated views are included in the fixture scope", "state": "Covered",
            "evidence_refs": ["self-test://generated-views"], "acceptance_refs": [0]}]
        amend_record(task_dir / "before.json", dotted_path="requirement_items", new_value=amended_items,
                     reason="account for the short but substantive scope answer", basis="self-test")
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
        # The contract declares independent-review, so the ledger has to show it was
        # passed. Declaring a gate and going through one are different facts.
        record_fixture_acceptance(task_dir)
        gate_subject = approval_subject_sha256(read_json(task_dir / "before.json"), __import__("governance_artifacts").read_jsonl(task_dir / "run.jsonl"))
        append_run_event(task_dir, run_id="RUN-001", attempt_id="A-002", event_type="human_gate", summary="independent-review passed", status="succeeded", evidence_refs=["self-test://independent-review"], gate={"id":"independent-review", "outcome":"Passed", "subject_sha256":gate_subject, "decided_by":"self-test-reviewer", "decided_at":now_utc(), "authority_ref":"self-test://authority"})
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
                requirement_items=[{"id": "R-01", "source": "request_snapshot", "quote": "self-test fixture request", "reading": "self-test fixture", "state": "Covered", "evidence_refs": ["self-test://evidence"], "acceptance_refs": [0]}],
                decisions=[
                    {"id": "D-01", "kind": "Proceed", "presented": "range and acceptance", "response": "Proceed", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                    {"id": "D-02", "kind": "Acceptance", "presented": "verification result", "response": "accepted", "decided_by": "self-test", "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                ],
                clarification={"state": "Settled", "mode": "Skipped", "notice": "Scope is fully declared by the fixture; skipping the question round.", "survey_refs": ["surveyed.md"], "rounds": [], "basis": "self-test fixture", "reopened_by": []},
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
        (cli_root / "surveyed.md").write_text("surveyed by the CLI fixture\n", encoding="utf-8")
        decisions_file = write_fixture(
            "decisions.json",
            [
                {"id": "D-01", "kind": "Proceed", "presented": "范围与验收",
                 "response": "Proceed", "decided_by": "self-test",
                 "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
                {"id": "D-02", "kind": "Acceptance", "presented": "验证结果",
                 "response": "接受", "decided_by": "self-test",
                 "decided_at": "2026-08-15T00:00:00Z", "outcome": "Approved", "evidence_ref": "self-test://simulated-human-answer"},
            ],
        )
        requirement_items_file = write_fixture(
            "requirement-items.json",
            [
                {"id": "R-01", "source": "request_snapshot",
                 "quote": "用 UTF-8 JSON 文件输入跑一遍自检",
                 "reading": "跑一遍 CLI 文件输入自检", "state": "Covered",
                 "evidence_refs": ["self-test://cli"], "acceptance_refs": [0]},
                {"id": "R-02", "source": "clarification:r1.e1",
                 "quote": "是，只覆盖文件输入",
                 "reading": "范围限定在文件输入路径", "state": "Covered",
                 "evidence_refs": ["self-test://cli"], "acceptance_refs": [0]},
            ],
        )
        clarification_file = write_fixture(
            "clarification.json",
            {
                "state": "Settled",
                "mode": "Asked",
                "notice": "针对你的需求和项目现状，有几个问题需要你先回答，以保证本需求完成的质量",
                "survey_refs": ["surveyed.md"],
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
                "basis": "勘察确认 CLI 固件仅走文件输入路径", "reopened_by": [],
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
        # Two amendments touched objective and scope, so S1 reopened twice. Execution
        # stays blocked until each reopening has been answered by its own round.
        def _round(ordinal, question, answer):
            return {"ordinal": ordinal, "asked_at": "2026-08-15T00:00:00Z", "exchanges": [{
                "question": question, "changes": "Scope", "recommended_default": answer,
                "answer": answer, "answer_state": "Answered"}]}

        amend_record(
            cli_task / "before.json",
            dotted_path="clarification",
            new_value={
                "state": "Settled", "mode": "Asked",
                "notice": "针对你的需求和项目现状，有几个问题需要你先回答，以保证本需求完成的质量",
                "survey_refs": ["surveyed.md"],
                "rounds": read_json(cli_task / "before.json")["clarification"]["rounds"] + [_round(2, "改后的目标仍限于文件输入吗？", "是"),
                           _round(3, "扩大后的范围包含哪些路径？", "只有临时 CLI 固件")],
                "basis": "objective 与 scope 各自的修订都问过了",
                "reopened_by": ["amendment:objective", "amendment:scope.in_scope"],
            },
            reason="answer both questions the amendments raised",
            basis="self-test",
        )
        # New answers are new requirement sources, so the ledger has to grow with them.
        amend_record(
            cli_task / "before.json",
            dotted_path="requirement_items",
            new_value=[
                {"id": "R-01", "source": "request_snapshot",
                 "quote": "用 UTF-8 JSON 文件输入跑一遍自检", "reading": "跑一遍 CLI 文件输入自检",
                 "state": "Covered", "evidence_refs": ["self-test://cli"], "acceptance_refs": [0]},
                {"id": "R-03", "source": "clarification:r1.e1", "quote": "是，只覆盖文件输入", "reading": "只覆盖文件输入", "state": "Covered", "evidence_refs": ["self-test://cli"], "acceptance_refs": [0]},
                {"id": "R-04", "source": "clarification:r2.e1", "quote": "是", "reading": "确认原有范围", "state": "NotARequirement", "evidence_refs": ["self-test://cli"], "acceptance_refs": []},
                {"id": "R-02", "source": "clarification:r3.e1",
                 "quote": "只有临时 CLI 固件", "reading": "范围限定在临时固件目录",
                 "state": "Covered", "evidence_refs": ["self-test://cli"], "acceptance_refs": [0]},
            ],
            reason="cover the clauses the new answers introduced",
            basis="self-test",
        )
        append_run_event(cli_task, run_id="RUN-CLI", attempt_id="A-001", event_type="run_started", summary="Start CLI input test", status="started")
        append_run_event(cli_task, run_id="RUN-CLI", attempt_id="A-001", event_type="verification", summary="Validate CLI JSON file inputs", status="succeeded", evidence_refs=["self-test://cli-json-files"])
        record_fixture_acceptance(cli_task)
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
        "requirement_review": requirement_review_validation,
        "new_query_history": new_query_history_validation,
        "document_governance": document_governance_validation,
        "amendment_growth": amendment_growth_validation,
        "saved_result_user_decision": saved_result_validation,
        "adversarial_review": adversarial_review_validation,
        "adversarial_review_boundaries": adversarial_boundary_validation,
        "approval_time": approval_time_validation,
        "closed_scope_history": closed_scope_history_validation,
        "historical_proof_compatibility": historical_proof_compatibility_validation,
        "verification_recovery": verification_recovery_validation,
        "failure_and_terminal": failure_terminal_validation,
        "review_boundaries": review_boundary_validation,
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
