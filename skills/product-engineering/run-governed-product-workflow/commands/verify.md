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

## 工程验证后的真实验收交接

实现和工程验证完成后，必须主动向人提交一次可验收的交付：交付对象、版本和范围，原文逐条覆盖结果，实际执行的验证与证据，失败、未验项、未通过 Gate 和残留限制。不得只说“测试已绿，请确认”。必要验证或 Gate 尚未满足时，明确说明尚不能正式收尾，不将其藏在“完成”结论中。

没有覆盖同一交付版本与范围的有效明确验收通过决定时，交付后请求人选择“验收通过 / 需要返修 / 暂不验收”，并等待真实回答。已有该决定且交付未发生使其失效的变化时，核对决定及证据后直接进入 close，不重复询问。

- 明确验收通过：保留实际展示内容、回答原话、决定人、时间与对应证据，按正式工具记录 Acceptance；其他 required Gate 分别核验，不能由 Acceptance 一并替代。
- 要求返修：保留原验证和回答，依实际问题修正并重新验证；不得沿用已失效版本的验收。
- 推迟、未答或含糊：明确报告“待人验收”及待答内容，保留实际证据，不虚构肯定决定。

Proceed、验证通过、沉默、消息已读、普通确认收到和工具成功均不构成 Acceptance。不得为了补齐 `after.json` 或 `task_outcome` 把待人验收写成 `Implemented`、`Deferred` 或 `Blocked`。

实际验证成功后，用当前工具取得已验证交付的绑定摘要：

```console
python <skill-root>/scripts/get_approval_subject.py <project-root>/.project-governance/tasks/<TaskID>
```

该摘要绑定原文、范围、验收判据及带证据的已验证交付；证据引用必须定位不可变的实际源或产物版本。没有中间材料动作且引用完全相同的重复成功验证，复用该交付首次验证的批准锚点，不重复索取同一验收。不同版本证据，或之后发生 mutation、external_effect、rollback、failure、retry、失败验证，会使原绑定失效；必须重新验证，不能把旧验收摘要抄到新交付。摘要不证明证据为真，也不证明人已经批准。仅记录决定或需求交代不构成交付变更。

真实决定须保留 `presented`、`response` 原话、`decided_by`、含时区的真实 `decided_at`、`evidence_ref`，并显式记录 `outcome=Approved|Rejected|Deferred`。`Implemented` 要求本次 Acceptance 为 `Approved` 且 `subject_sha256` 等于上述当前摘要；否定、推迟和缺少明确结果不能当成通过。新决定使用新 ID、保留旧历史；按实际决定时间判断先后，补录较早批准不能掩盖较晚拒绝，同时间冲突按未决处理。决定必须在对应交付验证后作出。完整载体用官方 Amendment 记录，Minimal 用 `record-review`。这些字段由 Agent 整理，不因此证明答复或审批真实发生，必须引用真实人侧来源。旧记录已有真实明确授权及来源时，可据原证据补结构字段，不要求人对同一授权重新回答；缺证据时不得猜补。

拟以 `Implemented` 收尾时，完整载体先记录验证与实际人侧决定、所需 Gate，再写成功的 `run_finished`，然后 close；Minimal 先完成真实验收交接，再调用 close，由 close 追加 `run_finished`。真实失败、取消或其他未完成结果按各自事实记录，不要求先取得肯定验收。已封账的历史记录不得倒改或补造决定；按官方修订路径如实处理。
