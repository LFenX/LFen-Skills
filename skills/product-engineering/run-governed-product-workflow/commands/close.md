# close

用于收尾并生成 TaskOutcome。

工程验证完成后先保存结果，用户决定独立保存在 `user_decision`。`Implemented` 表示工程实现和必要验证完成，不表示用户验收通过；无人答复时仍生成结果并写 `{"outcome":"Pending"}`，不编造答复或伪标工程阻断。交付本次版本、原文覆盖、实际验证和未验项；用户可稍后从可核对的外部来源作决定，无需回到原对话重复回答。真实失败、取消或其他未完成结果同样按事实留档。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

先分流：

- 存在 `before.json` 且不存在活动 `task-record.json`：按完整载体收尾。
- 存在合法 `task-record.json` 且 `lifecycle_state` 为 `Ready` 或 `Frozen`：按 Minimal 收尾。
- 两者同时存在：停止；先确认是否已升级，禁止混用载体。
- `task-record.json` 为 `Upgraded`：停止；先用 `init_task.py --upgrade-minimal-reason --upgrade-minimal-basis` 完成完整载体升级。
- `task-record.json` 为 `Completed`：停止；该 Minimal 任务已收尾。

完整载体：

以 `Implemented` 留档时，核对需求覆盖、工程验证与每一项 required Gate，再追加成功的 `run_finished`，最后执行下列 close。用户 Acceptance 不再是结果生成的前置条件；已存在且绑定同一验证版本的真实决定会保留到新字段中，缺少有效决定时为 `Pending`。用户决定可在结果生成后单独修订，不能补写已结束 Run 的事件。

```console
python <skill-root>/scripts/close_task.py <project-root>/.project-governance/tasks/<TaskID> --status <Implemented|Deferred|Cancelled|Blocked|Superseded> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python <skill-root>/scripts/rebuild_project_state.py --project-root <project-root> --project-id <ProjectID>
python <skill-root>/scripts/generate_review_views.py --project-root <project-root> --project-id <ProjectID>
```

收尾为 `Implemented` 时，`authority.required_gates` 里的每一道门都必须有真实通过的决定和账本证据。**声明了门、记录待审和走过了门是三件事**；只有在 summary 或引用里出现门名不证明它已经通过。`Pending`、拒绝、失败或仅记录收到不能当作通过，具体结构按当前 Schema 和 CLI。账本是追加式的，`run_finished` 之后不能再补记——门要在它通过的当时就写进去。

工程 Gate 在 close 前使用 [verify](verify.md) 的 `get_approval_subject.py` 取得当前已验证交付摘要。结果生成后，同一工具返回已保存工程结果的用户决定绑定摘要；稍后更新 `user_decision` 时使用该摘要及真实来源。`Approved`、`Rejected`、`Deferred` 均须真实回答、决定人与时间及证据，`Pending` 不携带虚构人的信息。Gate 事件通过 `--gate-json-file` 传入以下完整结构：

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

TaskOutcome 写明成立事实、实际变化、验证、遗留项、责任人、后续 TaskID 和独立 `user_decision`。后续决定的字段格式及补记命令见 [verify](verify.md)。

新结果同时初始化 `adversarial_review: []`；工程状态为 `Implemented` 时其含义为“尚未询问”。保存并交付后必须主动询问是否启动对抗性审查，再记录实际 Offer；不得先审查后补问。未回答、拒绝和推迟均不撤回结果，也不代表审查通过。获明确同意后按 [verify 的对抗性审查流程](verify.md#完工后可选对抗性审查) 追加记录；不要向已结束的 Run 补事件。该选择与 `user_decision` 中的人工验收决定分开，不能相互代替。

同一已授权审查的返修任务在 Full / Minimal close 时传 `--review-parent-task-id <原审查任务ID>`，并直接依赖该原任务。脚本核验同项目、明确同意与未结束会话后写入归属，状态为 `ManagedByParent`，不递归询问或新开审查。无有效父会话不得凭此参数跳过询问；归属不能事后用普通 amendment 改写。

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

Minimal 的 close 在工程验证完成后追加最终 `run_finished` 并生成 `task_outcome`，其中 `user_decision` 默认 `Pending`。稍后用 `record-review --user-decision-json-file` 补记真实决定，对抗性审查记录使用 `adversarial_review.py` 追加；均不重写工程事实或执行账本。完整与 Minimal 均保留工程证明校验，不以文件存在或 `Implemented` 宣称用户已通过验收。
