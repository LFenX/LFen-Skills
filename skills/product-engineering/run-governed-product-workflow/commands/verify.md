# verify

用于验证和验收前准备。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

验证必须证明原始结果和约束成立，不只证明命令运行成功。记录：

- 验证对象和版本。
- 方法、输入、预期、实际和结果。
- Evidence 引用。
- 未覆盖范围和残留风险。

## 逐条对照，不抽查

**验收基准是需求原文**：`request_snapshot` 里的用户原话，以及澄清各轮里用户逐条的回答。

不是任务卡、完成判据或验收清单——那些是 Agent 起草的派生物，起草时就可能漏掉原文里的要求。**用派生判据验自己写的实现，查多少遍都不会红**：漏掉的那条既不在判据里，也不在实现里，两边一致，全绿。

执行方式：

1. 独立重读完整 `request_snapshot` 和每轮真实澄清回答，再把用户的要求**逐条摘出**，编号成清单。不得只接收其他 Agent 的任务卡、拆条台账或摘要作为复查输入。一句话含多个要求的要拆开——「阻断并提示 X **或者**提交 Y 让管理员审查」是两条，不是一条。交互、呈现、文案类的要求同样入清单，它们最容易在起草判据时被当成细节丢掉。
2. 清单**必须穷举**，包括看起来早就做过的、看起来是小事的。不得以「这条显然没问题」为由跳过。
3. 每条给出三样：**状态**（已实现 / 未实现 / 部分实现）、**证据**（文件与行号、命令输出、或活体验证结果）、部分实现时**差在哪**。
4. 「未实现」与「部分实现」逐条列出，不得省略、不得合并进结论段落。
5. 只给结论、不给逐条清单的复查，视为未完成。
6. 原文含“只有……时”“除非”“或”“已……后”等条件或例外时，保留限定词，并给出条件成立与不成立的对照输入、预期、实际和证据。例如“仅备注且未改值才须补值”，必须同时验证“仅备注未改值应拦截”和“已改值并备注应放行”，不得只测拒绝分支。对照不能实际执行时明确缺口，不得标为已验证。

拆分复句的 reading 和验证用例时，`quote` 仍须保留同来源的完整原句及限定词；多条可引用同一完整原句。不得用短词覆盖整句，也不得用另一轮同字回答抵消本轮原话。`source` 使用 `request_snapshot` 或实际 `clarification:r<轮次>.e<序号>`。

抽查漏得有系统性：Agent 倾向于复查自己记得的、自己实现过的条目，而漏掉的恰恰是自己起草时就没接住的那些。逐条对照是唯一能把这类漏项翻出来的方式。

需求原文与派生判据不一致时，以原文为准，并按 Amendment 修订派生判据；不得反过来用判据裁剪原文。

机器可以检查原文引用、覆盖记录、证据字段和关系是否完整，不能证明自然语言含义已被正确理解，也不能替代独立复核。不得把结构校验通过表述为需求语义正确或验收通过。

## 历史读取与当前执行

当前证明契约为 `implemented-proof-v1`，生效时间为 `2026-10-15T08:22:24Z`。新建 Full / Minimal 记录写入 `proof_contract_version`。仅缺少版本字段不构成历史豁免：旧终态还须满足截止时间及现行证明信号检查；现行版本、现行证明信号或截止时间之后的记录仍按当前证明校验。未知版本和原始结构、身份、Run 关系损坏继续报错。

历史兼容只用于读取已存在的旧终态。保持原状态和权威源文件字节，派生状态中的 `source_tasks[].proof_validation` 及审阅页说明 `HistoricalNotRevalidated`，表示未追溯补验新增证明；这不等于本次通过当前门禁。活动任务尚未完成终态核验，不能标成 `CurrentVerified`。全项目汇总不能因历史缺少后来新增的证明而要求补造批准或改写旧状态。

旧活动 Full 任务继续物质执行前，使用 `amend_record.py --path proof_contract_version --value-json '"implemented-proof-v1"' --allow-add --reason <实际原因> --basis <真实依据>`；Minimal 使用 `record-review --adopt-proof-contract --reason <实际原因> --basis <真实依据>`。采用契约只记录版本修订，不补授权，后续执行和收尾仍检查真实有效的 Proceed、验收和所需 Gate。已存在的版本不得删改。版本采用改变本次批准绑定，不能沿用旧版本 Acceptance。

已经按现行证明完成且无版本字段的旧终态，保持其原有真实验收绑定并严格核验证明，不为读取强制添加新字段。任何新的追加执行或收尾都要求当前版本。JSON 时间、字段和摘要不是不可伪造的签名；兼容判定不能证明任意离线改写的历史事实真实发生。

需要将 Covered 条目正式交代时，在该 `requirement_items[]` 上记录 `review`：

| 字段 | 记录内容 |
|---|---|
| `source_sha256` | 对该条 `source` 指向的完整原话文本按 UTF-8 计算 SHA-256；不是只对 `quote`、reading 或派生清单求摘要 |
| `conditions` | 独立重读原文后列出的条件与例外；无条件时为 `[]`，不得为省略对照而清空真实条件 |
| `cases` | 每例包含 `condition`、`branch`、`input`、`expected`、`actual`、`result`、`evidence_refs` |

有条件时，`condition` 是 `conditions` 的从 0 开始索引，`branch` 为 `Met`、`NotMet` 或 `Exception`；每个条件都需要 `Met` 和 `NotMet` 对照，例外不能替代它们。无条件时，`condition` 为 `null`，`branch` 为 `Unconditional`。`result` 仅为 `Passed`、`Failed` 或 `NotRun`；已执行结果要有实际输出与证据，未执行不得冒填 Passed。Covered 收口需要所列案例均 Passed。字段齐全只证明记录结构成立，不能证明条件提取穷尽或 expected 符合原意。

完整载体使用 `amend_record.py` 保留修订历史；Minimal 使用 `manage_minimal_task.py record-review`，详见 [minimal](minimal.md)。两者都不能用新的 reading 或 review 篡改原话及其来源。

完整载体常用命令：

```console
python <skill-root>/scripts/validate_task_package.py <project-root>/.project-governance/tasks/<TaskID> --check-mapping
python <skill-root>/scripts/audit_tailoring_coverage.py
python <skill-root>/scripts/audit_norm_consistency.py --project-root <project-root> --project-id <ProjectID> --task-id <TaskID> --runtime-only
```

`<skill-root>/scripts/audit_norm_retrieval.py --validate-only --runtime-only` 可不传规范开发仓 TaskID。

验收决定、发布批准和风险接受不能由验证脚本代替。

## 工程结果留档与独立用户决定

实现和工程验证结束后，先保存可核对的工程结果：对象与版本、原文逐条覆盖、成立事实、实际变化、验证与证据、未完成项、未通过的工程 Gate 和残留限制。`Implemented` 表示工程实现及必要验证完成；其他真实结果使用对应状态。人的决定不控制 `after.json` / `task_outcome` 是否生成，工程结果存在也不等于 Acceptance 或发布批准。

Full 的 `after.json` 与 Minimal 的 `task_outcome` 使用同一个 `user_decision` 字段。无有效决定时为：

```json
{"outcome": "Pending"}
```

`Pending` 不编造答复、决定人、决定时间或证据。已有绑定同一验证版本且可核对的真实决定时，生成器保留实际决定；不存在时仍须先留档并交付结果，无需等待即时回复、反复询问或要求用户回到原对话。用户稍后在其他可访问来源中的明确答复同样可以作为证据，必须核对实际对象、版本与原话，不能从沉默、测试成功、普通收到或文件存在推断通过。

实际决定的 `outcome` 为 `Approved`、`Rejected` 或 `Deferred`，并完整保留：

| 字段 | 内容 |
|---|---|
| `presented` | 用户当时看到的交付对象、版本和验收信息 |
| `response` | 用户实际回答原文 |
| `decided_by` / `decided_at` | 实际决定人及含时区的真实决定时间 |
| `evidence_ref` | 可核对的实际来源；可以来自原对话以外 |
| `subject_sha256` | 已保存工程结果的绑定摘要 |

结果生成后，用现有工具读取该结果的绑定摘要：

```console
python <skill-root>/scripts/get_approval_subject.py <project-root>/.project-governance/tasks/<TaskID>
```

该摘要绑定实际交付快照、验证结果和契约；更正工程结果的说明文字不要求用户重复验收。用户决定本身、修订号和修订历史不参与绑定。结果尚未生成时，同一工具仍返回工程 Gate 使用的验证交付摘要。摘要检查不证明人实际作过决定，真实来源和回答仍须核对。

将真实决定整理成完整 JSON 文件后，Full 更新现有 after 字段：

```console
python <skill-root>/scripts/amend_record.py <project-root>/.project-governance/tasks/<TaskID>/after.json --path user_decision --value-json-file <actual-decision.json> --reason <实际补记原因> --basis <真实来源>
```

Minimal 更新聚合载体中的结果字段：

```console
python <skill-root>/scripts/manage_minimal_task.py record-review <project-root>/.project-governance/tasks/<TaskID> --user-decision-json-file <actual-decision.json> --reason <实际补记原因> --basis <真实来源>
```

两者保留修订历史和原工程事实，不向已结束 Run 补事件。无来源、错误版本、未来时间、早于交付验证的决定，以及用较早批准覆盖较晚拒绝，均不得记入。`Rejected` / `Deferred` 仍保留已保存工程结果；返修按实际范围启动后续任务，不把人的选择改写成工程事实。

缺少 `user_decision` 的旧文件继续按原有证明和历史兼容规则读取，不能把“没有字段”当成新的 `Pending` 或 `Approved`，也不批量补造人的决定。新的生成器始终写该字段。`Proceed`、工程 required Gate 和发布权限保持各自的校验，不能用工程结果留档替代。

## 完工后可选对抗性审查

**规则表述：**工程实现、必要验证及结果留档完成后，主动询问是否在明确的有限预算内启动对抗性审查，仅在用户明确同意后开展。每轮按原始需求、澄清原话和当前已验证交付寻找遗漏、反例及失效路径，在剩余预算内修复和复验。只有同一交付版本连续两轮完整无问题，且没有未解决或未检查项，才标为审查通过；任一预算到限即停止新增工作，汇总并等待用户决定，不能用预算耗尽代替通过。

### 启动与授权

1. 先完成普通工程验证并按 [close](close.md) 保存 Full `after.json` 或 Minimal `task_outcome`，再交付并发出开始 / 不需要 / 稍后决定的真实询问。此规则不把普通测试或已要求的工程 Gate 改成可选项。
2. 将实际问题记为 `Offer`。无答复为 `AwaitingUser`；拒绝、推迟分别为 `Declined`、`Deferred`，均不得开始。只有 `Decision.outcome=Accepted` 且保留回答原话、实际决定人、时间和来源，才可进入审查。用户稍后主动明确开始时，直接追加真实新决定，不要求重新提问；已停止或已结束后再开始也须真实新决定。编写此机制、普通验收同意和沉默都不构成启动授权。
3. 同意只覆盖本任务及明确预算内的审查、返修和复验，不扩展生产操作、发布或权限。越界、缺少环境/证据或无法安全修复时记 `Blocked`；用户要求停止时记真实 `Stopped`。未达到两轮不得报告通过，到限仍未收敛则保留未通过状态并交还用户决定。

### 预算与停止出口

- 默认每次授权最多 **3 轮审查、2 批返修、60 分钟**，用户可在启动前指定其他有限正整数；禁止无限预算。`Offer.budget` 展示实际额度，`Accepted` 绑定同一额度。时间从本次同意起按墙钟计，含等待、重试及验证，不因换会话或重启工具暂停计时。
- 每次启动审查或返修前，先在**原审查任务**追加 `WorkStarted` 扣减相应额度，再启动执行者或修改文件。`work_type=Review` 的 `work_id` 为本轮 ID；`Repair` 的 `work_id` 为直接依赖原任务的返修 TaskID。一批返修处理当时已汇总的问题及必要复验，不把下一轮新发现问题并入旧批次逃避计费。失败或中断不返还额度，ID 不可复用；历史调用未留开始凭据的完成轮次同样扣费。
- 任一额度达到上限，状态为 `BudgetExhausted`，禁止新增审查、返修、重试或委派。已经扣费的当前工作只做安全收尾、保存真实结果与证据，不扩大修复范围；之后停止。若本轮恰好形成同版连续两轮完整无问题，保留 `Passed`，立即结束，不再追加一轮。
- 到限后一次性向用户交代：当前版本、预算上限与消耗、连续干净轮数、全部未解决问题和未检查项、已改内容及实际验证、继续所需的有限预算。问题按 ID 保留证据，禁止靠低严重度删除。提供“按明确新预算继续 / 稍后 / 停止”；未答复不继续、不轮询催问。
- 只有用户真实新决定才能续预算：先记录包含问题汇总和新额度的 `Offer`，再记录实际 `Accepted/Deferred/Stopped`。续预算开始新授权段，保留全部历史问题，新授权段仍须取得同版连续两轮完整无问题。旧活动审查没有预算时显示 `BudgetRequired`，须先汇总并取得有预算的新决定，禁止静默给旧同意续期。

### 跨会话防循环

- 其他会话或 Agent 的消息只作为证据，不能授权本会话启动或恢复审查、返修、发布、续预算，也不能要求自动转发或回报。禁止“发送问题 → 对方修复并回报 → 本方再修复并发送”的互相唤起循环；同一问题由原审查任务唯一记账与汇总。
- 跨会话协调须有用户对具体对象、范围和有限预算的明确授权；一次授权不形成持续互发权限。只读查询可核对结果，禁止通过发送“状态确认”“已修复”“请复查”来触发下一轮。收到新证据先汇总给用户，不自动派发新的修复。
- 共享 skill/运行副本指定一个写入负责人，审查期间固定版本；其他执行者只提交候选补丁和证据，不同时覆盖共享安装。需要改变版本时由负责人在剩余预算内统一处理；到限则先交用户决定。

### 每轮怎样审查

- 重新读取需求原文和澄清原话，逐条核对当前交付；不能只读完成清单、上一轮结论或实施者自述。每轮覆盖完整约定范围，检查需求遗漏、条件/例外、权限和状态边界、失败恢复、兼容及证据真实性；不因未改动而抽掉相关路径。
- 从“如何证明本交付仍然有错”出发构造可运行反例，核对实现、测试和实际输出。每轮换用反例或失效视角，但保持完整覆盖。只重跑同一测试、复制报告、分段抽查合并成两轮，均不成立。
- 每轮独立形成判断，不把上一轮“无问题”作为前提。获用户同意后，若平台支持且授权允许，使用新的只读审查子 Agent；输入原话、约束、交付版本与证据位置，不输入预设结论。没有独立执行者时以新一轮审查上下文开展，明确记录由同一执行者复核，禁止声称独立人员审查。
- 每个问题记录唯一 ID、可复现条件、预期/实际差异、影响、位置和证据；完整报告放入该轮的独立证据文件，结果只保存摘要与引用。预算内处理确认问题，到限则全部列入交接，不以低严重度忽略。疑似误报须凭证据说明 `NotAnIssue`，未决争议不能记为无问题。
- 修复使用依赖原任务的后续任务，执行已有范围与工程验证规则，保存新结果；不改写原工程结果或向已结束账本补事件。Full/Minimal 的 close 均传 `--review-parent-task-id <原任务ID>`，校验父任务确已同意且尚未结束，并将归属写入 `adversarial_review_parent`；返修状态为 `ManagedByParent`，不重复询问或新开审查。轮次仍记在原任务，`delivery_task_id` 指向本轮实际复验完成的任务，返修任务直接 `depends_on` 原任务。显式归属的已保存返修按 `completed_at` 接续为该会话当前交付；即使新返修尚无审查轮次，也使旧交付的连续计数失效并拒绝继续引用旧版。当前交付尚未复验完成或无法唯一确定时，不计数，记录阻塞并核对实际交付。

### 计数与结束

- 发现任何问题、覆盖不完整、有未检查项、存在未解决问题或阻塞：本轮不计为干净轮次，连续计数归零。
- 交付版本或原始需求/澄清变化使旧计数失效；尚未结束的会话显示 `Stale`，仅在预算有效且有余额时沿用授权继续，否则显示预算停止状态。已结束会话的证明失效显示 `RestartRequired`，须有真实新 `Accepted` 才可重新开始，不能恢复旧同意。basis、survey_refs、捕获时间等说明更正不改变新版原文绑定。修复后从新版本第一轮重新计数，开始时间必须晚于该交付的验证和留档时间。已发现问题须在后续轮以证据登记 `Fixed` 或 `NotAnIssue`；`Fixed` 必须绑定重新验证的新交付。
- 第一轮完整无问题记为 1；保持同版再完整审查一轮仍无问题记为 2，自动得到 `Passed`，随后结束。独立报告、轮次 ID、时间与版本必须分别可核对，不能复用一份报告凑数。
- 交付轮次、版本、问题及处置、实际验证和限制；这只证明规定范围内两轮未发现问题，不宣称绝对无缺陷，不替代用户 Acceptance 或发布批准。

### 记录与机器校验

Full 与 Minimal 均在工程结果的 `adversarial_review` 数组中追加 `Offer`、`Decision`、`WorkStarted`、`Round` 或 `Blocked`，不另建任务档位或独立治理载体。使用唯一入口：

```console
python <skill-root>/scripts/adversarial_review.py <project-root>/.project-governance/tasks/<TaskID>
python <skill-root>/scripts/adversarial_review.py <project-root>/.project-governance/tasks/<TaskID> --entry-json-file <actual-record.json> --reason <实际原因> --basis <真实来源>
```

无 `--entry-json-file` 为只读状态查询。输入字段如下，均为真实观察，不得填占位审批或虚构审查；每条都有 `event` 和 `recorded_at`（含时区的实际发生时间）：

| event | 其他必填字段 |
|---|---|
| `Offer` | `prompt`、`evidence_ref`：实际问题及来源；`budget={review_rounds,repair_batches,elapsed_minutes}`，省略由工具写默认值，实际询问仍须展示额度 |
| `Decision` | `outcome=Accepted/Declined/Deferred/Stopped`、`response`、`decided_by`、`evidence_ref`；`Accepted.budget` 由工具绑定实际 Offer，不能擅改额度 |
| `WorkStarted` | `work_type=Review/Repair`、`work_id`、`evidence_refs`；启动工作前追加，立即计费 |
| `Blocked` | `reason`、`evidence_refs` |
| `Round` | `round_id`、`started_at`、`reviewer`、`delivery_task_id`、`subject_sha256`、`requirements_sha256`、`report_ref`、`coverage=Complete/Incomplete`、`unreviewed_items`、`evidence_refs`、`findings`、`resolutions` |

所有文字字段必须至少包含一个非空白字符；纯空白的询问、答复、决定人或证据来源会被拒绝且不写入。合法原话及其前后空白保留原样。

只读命令同时输出摘要：`subject_sha256` 取**本轮交付任务**的状态输出，与 `get_approval_subject.py` 一致；`requirements_sha256` 取**原审查任务**的状态输出，绑定 request_snapshot.text 与澄清各轮的原问题、推荐默认和真实回答上下文。顶层摘要表示所查询任务的工程结果，`reviewed_delivery` 点名审查末轮实际绑定的交付，`current_delivery` 点名当前应审查的已保存交付；返修后这些对象不能混淆。`findings` 每项为 `{id, summary, evidence_refs}`；`resolutions` 每项为 `{finding_id, disposition: Fixed|NotAnIssue, reason, evidence_refs}`，详情在引用报告中。没有对应条目时写空数组；未检查项必须列明，不能填空以伪造完整覆盖。

`report_ref` 为原审查任务目录内的实际非空报告，推荐 `evidence/round-<n>.md`，路径相对项目根或使用绝对路径。脚本规范化路径并从实际文件写入 `report_sha256`、`review_contract_version=report-bound-v2` 和所引用交付的 `delivery_verified_at` / `delivery_completed_at`；提供这些派生值时须与实际相符。报告路径别名或相同内容副本不能计为两轮；去重同时核对当前文件与已登记的历史摘要，原文件修改或删除不解除旧内容的复用限制。独立报告可以共享 `evidence_refs` 中的需求、测试等支持证据。旧轮次原件可读，不补造绑定证明；缺少新版报告绑定的旧干净轮次不计入新版连续两轮，原协议曾收敛时标 `LegacyNotRevalidated`，不会自动重启。已有未解决问题继续保留。

新轮次由脚本写入 `session_completed`：只有追加时实际算出同版两轮完整无问题才为 true。这是该次会话当时已结束的记录，不随当前证明失效而撤销，禁止手填不符值。旧记录缺少此字段时不补造凭据；其中声称已收敛的记录在证明失效后同样须有真实新启动决定。历史仍可读取；未结束的会话仍受预算停止规则约束。

脚本核对已保存工程结果、时间顺序、明确同意、有限预算与工作扣费、原文绑定、当前交付摘要、返修关系、问题处置和不同报告，自动计算状态及连续轮数；禁止手填 Passed/clean_streak 或用普通 amendment 改删审查历史及返修归属。Full amendment 与审查追加持有同一记录锁，避免并发丢失问题或用户决定。修订历史每次只留新增项，避免复制此前所有轮次。字段完整与摘要匹配不证明自然语言审查质量或来源真实，执行者仍须读取原件并保留实际证据。`signals.py` 和生成的审阅 Markdown 显示审查状态；`NotOffered` 提示先询问，只有获同意、未结束且预算有效有余额的审查才提示继续；预算缺失或耗尽时只提示汇总并等待用户决定。旧工程结果不自动补录、不因缺少审查字段追溯判失败。
