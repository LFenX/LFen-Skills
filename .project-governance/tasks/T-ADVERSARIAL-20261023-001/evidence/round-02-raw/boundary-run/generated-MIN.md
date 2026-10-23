# Task T-OLD-MIN

- Carrier: Minimal aggregate (TaskContract + RunLedger + TaskOutcome)
- Status: Implemented
- User decision: 待用户验收
- Adversarial review: {'status': 'Passed', 'clean_streak': 2, 'rounds': 2, 'open_findings': [], 'reviewed_delivery': {'task_id': 'T-OLD-MIN', 'subject_sha256': 'e950703c67647b8502b7ed5b400592b1df73d5cfc35197696f9e09fdac1c98b3', 'requirements_sha256': '6357a4ebd3f432f0b91140b68250a99136bf47a79f70e6bce41b5d1faca5861a'}}
- Proof validation: 当前契约记录校验通过（不替代人的验收）
- Objective: Update one local label.
- Scope: Change one label.
- Acceptance: The focused test passes.

## Events

- 1: run_started — Independent version-changing work
- 2: mutation — Set actual local source label
- 3: verification — Read and hash actual delivered local label
- 4: run_finished — Minimal task closed as Implemented.

## Verification

- Passed: Actual source label hash checked
