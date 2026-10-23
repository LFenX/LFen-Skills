# close

用于收尾并生成 TaskOutcome。

工程验证完成不等于验收通过。拟以 `Implemented` 收尾前，先按 [verify](verify.md) 向人交付本次版本的原文覆盖、实际验证证据和未验项，并主动发起一次真实 Acceptance 确认；已有同版本、同范围且仍有效的明确通过决定时不重复问。未答、拒绝、推迟或含糊答复均不得写成肯定验收，也不得为了生成 outcome 伪标 `Deferred` / `Blocked`。未答时明确说明“待人验收”，不声称正式关闭。真实失败、取消或其他未完成结果按相应事实收尾，不要求伪造肯定验收。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

先分流：

- 存在 `before.json` 且不存在活动 `task-record.json`：按完整载体收尾。
- 存在合法 `task-record.json` 且 `lifecycle_state` 为 `Ready` 或 `Frozen`：按 Minimal 收尾。
- 两者同时存在：停止；先确认是否已升级，禁止混用载体。
- `task-record.json` 为 `Upgraded`：停止；先用 `init_task.py --upgrade-minimal-reason --upgrade-minimal-basis` 完成完整载体升级。
- `task-record.json` 为 `Completed`：停止；该 Minimal 任务已收尾。

完整载体：

以 `Implemented` 收尾时，先记录真实 Acceptance 和每一项 required Gate，再追加成功的 `run_finished`，最后执行下列 close。验证事件本身不替代人的决定；不得提前封账后再补门。

```console
python <skill-root>/scripts/close_task.py <project-root>/.project-governance/tasks/<TaskID> --status <Implemented|Deferred|Cancelled|Blocked|Superseded> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python <skill-root>/scripts/rebuild_project_state.py --project-root <project-root> --project-id <ProjectID>
python <skill-root>/scripts/generate_review_views.py --project-root <project-root> --project-id <ProjectID>
```

收尾为 `Implemented` 时，`authority.required_gates` 里的每一道门都必须有真实通过的决定和账本证据。**声明了门、记录待审和走过了门是三件事**；只有在 summary 或引用里出现门名不证明它已经通过。`Pending`、拒绝、失败或仅记录收到不能当作通过，具体结构按当前 Schema 和 CLI。账本是追加式的，`run_finished` 之后不能再补记——门要在它通过的当时就写进去。

先按 [verify](verify.md) 的 `get_approval_subject.py` 取得当前已验证交付摘要。Acceptance 决定须有真实肯定回答及证据、`outcome: "Approved"` 和匹配的 `subject_sha256`。Gate 事件通过 `--gate-json-file` 传入以下完整结构：

| `gate` 字段 | 内容 |
|---|---|
| `id` | 具体 required Gate 的精确 ID |
| `outcome` | `Passed`、`Failed` 或 `Pending`，如实记录；只有 Passed 能满足通过条件 |
| `subject_sha256` | 当前已验证交付摘要 |
| `decided_by` / `decided_at` | 实际决定人与含时区的真实决定时间 |
| `authority_ref` | 有效 Authority assessment 的引用，须有证据且覆盖本次实际范围 |

通过 Gate 的账本事件必须为 `succeeded`、带非空证据引用，且对应 Authority 在决定时有效。仅 `recorded`、门名字符串、Pending、过期或范围不符的授权不能满足 Gate。正式 CLI 写法：

```console
python <skill-root>/scripts/append_run_event.py <project-root>/.project-governance/tasks/<TaskID> --run-id <RunID> --attempt-id <AttemptID> --event-type human_gate --summary <actual-gate-result> --status succeeded --evidence-ref <actual-gate-evidence> --gate-json-file <gate-proof.json>
```

引用已有权威决定时可按当前契约使用 `authority_decision_reference`，同样要求结构化 proof 和真实证据。Agent 填入 Passed 或 Approved 不构成人的审批，也不豁免其他 Gate。历史终态可按 [verify](verify.md) 的兼容规则保留原状态并汇总，明确标记未追溯补验；不得补造批准，也不得把兼容读取表述为当前证明合规。新的 close 必须使用当前证明契约，不能以历史日期或删字段豁免。

TaskOutcome 写明成立事实、实际变化、验证、遗留项、责任人和后续 TaskID。

完整 close 在当时实际核对 Git 范围，并冻结 `scope_reconciliation`，绑定起始快照、范围、交付快照及报告摘要。后续读取校验这份关闭时证据，不把未来任务的工作树变化追记到已关闭任务。摘要校验只证明内容绑定，不能证明伪造的观察为真；缺证据不得手填 Passed。

TaskOutcome 建立后修订必须使用：

```console
python <skill-root>/scripts/amend_record.py <project-root>/.project-governance/tasks/<TaskID>/after.json --path <field> --value-json <json> --reason <reason> --basis <basis>
```

旧 V6.2/V6.2.1 已收尾任务只做安全身份兼容读取，不要求当前 manifest 仍发布同一路径。

Minimal 载体：

```console
python <skill-root>/scripts/manage_minimal_task.py close <project-root>/.project-governance/tasks/<TaskID> --status <Implemented|Deferred|Cancelled|Blocked|Superseded> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python <skill-root>/scripts/manage_minimal_task.py validate --project-root <project-root> <project-root>/.project-governance/tasks/<TaskID>
python <skill-root>/scripts/rebuild_project_state.py --project-root <project-root> --project-id <ProjectID>
python <skill-root>/scripts/generate_review_views.py --project-root <project-root> --project-id <ProjectID>
```

Minimal 收尾只适用于未升级的合法 `task-record.json`；升级后必须走完整载体收尾。

Minimal 不能因零轮澄清或省略重复 Proceed 而省略 Acceptance。先取得并记录本次交付的真实肯定验收，再 close；该命令负责追加最终 `run_finished`。完整与 Minimal 载体都不得靠手写 outcome、只过 JSON Schema 或编辑派生状态绕过相同的 `Implemented` 收口校验。
