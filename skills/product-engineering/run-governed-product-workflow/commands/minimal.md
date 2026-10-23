# minimal

Minimal 是同一六元模型的物理载体裁剪，不是第二套流程。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

## 资格

唯一事实源是 `VC-PPG-DEC-001 §16.4`。下表是它的人类可读投影，每行绑定 `schemas/minimal-task-record.schema.json` 中 `eligibility` 的受控字段；`self_test.py` 校验本表覆盖全部字段，投影与 schema 漂移时失败。

| 条件 | schema 字段 | 记录值 |
|---|---|---|
| C02 Risk 为 Low | `risk_level` | `Low` |
| 变化可逆且回退路径已记录 | `reversible` | `true` |
| 只有一个可独立验收的 Scope | `single_scope` | `true` |
| 无外部系统副作用 | `external_system_effect` | `false` |
| 无生产发布 | `production_release` | `false` |
| 无安全/隐私影响 | `security_privacy_impact` | `false` |
| E01–E05 全部 Inactive | `extension_triggers` | 五项均 `Inactive` |
| 无阻断 Unknown、权限扩大、独立复核 | `blocking_unknowns` | `[]` |
| 无专用 Gate | `special_gates` | `[]` |

九条**全部**成立才可用。任意一条不成立或为 Unknown，走完整载体——Unknown 不得当作 No。


若裁剪图显示 Change Surface 或 Delivery Scenario 会触发 E01-E05，初始化必须拒绝 Minimal 并改走完整载体；当前允许的 Minimal Change Surface 为 `UI/UX`、`API/Integration`、`Agent/Collaboration`。

`--selection-source explicit-user` 用于用户明确说“采用最轻框架”；`--selection-source automatic` 用于 agent 判定资格全部成立并告知默认采用 Minimal。

`--objective` 用用户提问所用的语言；`--request-snapshot` 传用户原话，两者都必填。

先筛查再决定载体。Minimal 记录不承载 `applicability_facts`，资格只取决于取值为 `Yes` 就会否决某条条件的那 9 条事实，所以不必先完成完整 Task Profile：

```console
python <skill-root>/scripts/manage_minimal_task.py screen --risk <Low|Medium|High|Critical> --single-scope <yes|no> --fact <key>=<Yes|No|Unknown>
```

不带 `--fact` 直接运行会列出需要哪 9 条。输出 `ELIGIBLE` 才走下面的 init；`NOT-ELIGIBLE` 会点名是哪条否决的，改走 [init](init.md)。任一事实为 `Unknown` 即否决——§10.2 明令 Unknown 不得当作 No。

初始化。只需 §16.4 在 init 期要求的字段加基础 ID、Task Profile 三元和资格证据：

```console
python <skill-root>/scripts/manage_minimal_task.py init --project-root <project-root> --project-id <ProjectID> --work-item-id <WorkItemID> --task-id <TaskID> --ordinal <N> --objective <text> --scope <single-scope> --allowed-path <path> --acceptance <criterion> --delivery-scenario DS-03 --development-type DT-08 --change-surface UI/UX --selected-approach <approach> --alternative-rejected <rejected-alternative> --selection-source automatic --authority-ref <authority-ref> --eligibility-evidence-ref <risk-low-ref> --eligibility-evidence-ref <reversible-ref> --eligibility-evidence-ref <single-scope-ref> --eligibility-evidence-ref <no-external-effect-ref> --eligibility-evidence-ref <no-production-ref>
```

资格证据至少 5 条且互不相同，不设默认值：它是 Minimal 被允许的证明，编造默认等于伪造证据。

其余字段省略时由脚本写入带 `script default:` 前缀的可追溯值，并在 `selection.basis` 记录默认来源；需要时照常显式传入即可覆盖：`--plan-step`、`--verification`、`--basis`、`--fact`、`--fundamental`、`--causal-link`、`--decision-criterion`、`--out-of-scope`、`--forbidden-action`、`--assumption`、`--rollback`、`--constraint`

追加事件：

```console
python <skill-root>/scripts/manage_minimal_task.py append <project-root>/.project-governance/tasks/<TaskID> --event-type run_started --summary <summary> --status started
python <skill-root>/scripts/manage_minimal_task.py append <project-root>/.project-governance/tasks/<TaskID> --event-type mutation --summary <summary> --status recorded --evidence-ref <evidence-ref>
```

收尾：

先按 [verify](verify.md) 独立对照原话，核对工程验证并交付版本、证据和未验项。close 先生成 `task_outcome` 并结束工程 Run，`user_decision` 默认 `Pending`；不等待用户即时回复，不要求回到原对话，也不把 `Implemented` 当成人已验收。

工程完成并留档后主动询问是否启动对抗性审查，明确同意前不得开始。使用 [verify 的统一入口](verify.md#完工后可选对抗性审查) 向 `task_outcome.adversarial_review` 追加问题、真实选择和逐轮结果；同版连续两轮完整无问题才通过。未回答、拒绝或推迟保留工程结果，不改写 `user_decision`。

用户稍后从可核对的来源作出决定时，可在已完成的载体上单独更新：

```console
python <skill-root>/scripts/manage_minimal_task.py record-review <project-root>/.project-governance/tasks/<TaskID> --user-decision-json-file <actual-decision.json> --reason <实际补记原因> --basis <真实来源>
```

该更新只改结果中的用户决定并保留修订历史，不重写契约、工程事实或已结束账本。字段与版本绑定见 [verify](verify.md)。

完工后的原文复核与真实人侧决定通过专用接口补录，不重新 init、不直接手写 outcome：

```console
python <skill-root>/scripts/manage_minimal_task.py record-review <project-root>/.project-governance/tasks/<TaskID> --decisions-json-file <new-decisions.json> --requirement-items-json-file <complete-requirement-items.json> --reason <reason> --basis <evidence-ref>
```

活动任务的两个 JSON 参数至少提供一个，可只传决定或只传需求复核；已完成任务在 `record-review` 接口中只允许前述独立 user_decision 补记，对抗性审查使用独立的 `adversarial_review.py` 入口。决定文件是新增决定的数组，使用新唯一 ID；禁止改旧回答或覆盖已有决定。完整需求台账保留原 `id`、`source`、`quote` 和 `acceptance_refs`，只修订实际 reading、Open/Covered 状态、证据与 `review`；本接口不能改 Scope。工具保留 amendments。

旧活动记录可单独使用 `record-review --adopt-proof-contract --reason <实际原因> --basis <真实依据>` 正式采用当前证明契约；原有决定保留，不据此补造批准。采用后新追加执行和 close 仍按当前门禁核验。旧终态仅兼容读取，状态原样保留并标明未追溯补验，不能借此再次执行或收尾；完整规则见 [verify](verify.md)。

切换中断导致真实验证未能入账时，可使用`record-review --verification-json-file <receipt.json> --reason <实际原因> --basis <真实依据>`补录。receipt仅含`verified_at`（实际验证时间）、`summary`、`result: "Passed"`、`source_files`与`evidence_files`；两组非空文件清单每项为`{path,sha256}`，路径相对于项目根。工具核对文件仍存在、未越界、内容摘要相符且未在验证后修改；拒绝未来时间、早于现有账本或执行授权的时间，以及替换已有验证。原验证时间进入新追加事件，本次补录时间与完整receipt进入Amendment。补录不修改历史事件或人的决定，正式收尾继续校验先验证、后验收及当前交付绑定。仅有本次重跑的测试不能冒充此前的验证；没有原始证据时不得使用补录。

旧决定已有真实授权原话但缺少新结构时，可新增唯一 ID 并写 `enriches: "<旧决定ID>"`：原 kind、presented、response、decided_by、decided_at 逐字保持，既有 evidence_ref、outcome 和 subject 不得改，只补缺失结构及真实来源。旧项保留，此受控补录不构成同时间相反决定，也不要求人重答。不能借补录把拒绝改成批准或改造决定时间。

失败后先记 failure，再用 `append --event-type retry --status started` 开新 Attempt；后续事件沿用新 Attempt，旧 Attempt 的失败不能反复给新 Attempt 充当重试依据。连续失败不按次数重开需求澄清。已有 OutOfScope、Deferred 或 NotARequirement 不得借 record-review 改成 Covered/Open；范围取舍走完整载体。

先记录带证据的成功 verification，再用 [verify](verify.md) 的 `get_approval_subject.py` 取得绑定；Acceptance 必须来自真实回答，显式 `outcome=Approved`、有 `evidence_ref`，且 `subject_sha256` 匹配该交付。复核字段与条件对照也遵循 verify。不要复制旧摘要为新版本制造批准，不要把没有回答写成 Approved。

```console
python <skill-root>/scripts/manage_minimal_task.py close <project-root>/.project-governance/tasks/<TaskID> --status Implemented --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
```

校验：

```console
python <skill-root>/scripts/manage_minimal_task.py validate --project-root <project-root> <project-root>/.project-governance/tasks/<TaskID>
```

升级：

```console
python <skill-root>/scripts/init_task.py --project-root <project-root> --project-id <ProjectID> --work-item-id <WorkItemID> --task-id <TaskID> --ordinal <N> --objective <text> --acceptance <criterion> --development-type <DT> --change-surface <surface> --in-scope <scope> --baseline-inheritance Revise --upgrade-minimal-reason <reason> --upgrade-minimal-basis <evidence-ref>
```

其余参数同普通 `init_task.py`；只允许 Minimal 到完整载体，禁止反向降级。
