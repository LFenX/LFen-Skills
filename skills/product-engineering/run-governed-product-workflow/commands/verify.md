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
