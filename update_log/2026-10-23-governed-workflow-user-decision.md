# 工程结果留档与用户验收决定解耦

- 变更时间：2026-10-23 16:52（Asia/Shanghai，UTC+8）。
- 用户原话：这是一个问题，等于说很多时候其实用户来不及立刻做验收，而后续验收后也不愿回到对话再说一遍，所以我的建议是，将用户决定作为after文件中的一个字段，而不是影响after文件是否存在的因素
- 任务记录：`.project-governance/tasks/T-AFTER-20261023-001/`。
- 涉及目录：`skills/product-engineering/run-governed-product-workflow/`、现有 `.project-governance/console/` 派生部署、`.project-governance/project-state.json`、本任务记录及本日志。

## 变更与原因

- Full 的 `after.json` 和 Minimal 的 `task_outcome` 在工程收尾时生成；缺少即时人工验收不再阻止结果留档。
- 新结果增加 `user_decision`。没有有效决定时仅写 `{"outcome":"Pending"}`；真实决定使用 `Approved`、`Rejected`、`Deferred`，保留展示内容、回答原话、决定人、时间、实际来源及交付版本摘要。
- 用户可稍后从原对话以外的可核对来源作决定。Full 使用现有 `amend_record.py` 更新完整字段；Minimal 使用 `record-review --user-decision-json-file`，保留工程事实和已结束的账本。
- 已有绑定同一验证版本的真实决定及其合法结构补录会保留，不重复索取答复。错误版本、无来源、未来时间、早于验证的答复、较早批准覆盖较晚拒绝、单独翻转结论均拒绝。
- 决定绑定实际交付快照、工程状态、验证及契约。更正结果说明文字不使同一交付的真实验收失效；修改交付或验证版本仍会使旧绑定失效。
- 状态汇总、控制台和审阅页区分工程状态与用户决定。`signals.py` 公开 `task_progress`；已有工程结果而待验收时不建议重复执行。
- 沿用既有目录、文件名及六元模型。旧文件未单列 `user_decision` 时继续按原证明和历史兼容规则读取；未批量回填或改写既有任务。
- 同步更新收尾、验证、状态和 Minimal 指引、Schema、受保护 CLI 契约、Manifest 与现有控制台快照。人的发布批准、Proceed 和 required Gate 保持独立。

## 实际验证

- 完整自检：`self_test.py --project-root <当前仓库>`，最终退出码 0，证据为任务目录的 `evidence/self-test-final.log`。
- 新增结果与用户决定用例 36 项通过，覆盖 Full/Minimal 无即时验收先留档、延后外部来源更新、已有决定保留、版本与时序、状态公开输出及历史规则。
- 40 项历史证明兼容、22 项修订膨胀回归、16 项验证补录、21 项失败与终态、37 项决定边界等原有控制通过。
- 受保护运行资产审计：46 个资产、28 个 gold case、23 项 CLI 契约通过；全部 11 份 Schema 的 Draft 2020-12 结构检查通过。
- runtime 一致性审计 Complete，Blocker/Major/Minor 均为 0；1 项 Observation 为未指定 TaskContract 的快照检查不适用。
- 官方 `quick_validate.py`、目录生成检查和 `git diff --check` 通过。

## 失败与修正记录

- 初始化两次被现有 Schema 与原话覆盖检查拒绝；修正实际字段名并补入真实澄清回答的独立覆盖，保留 `setup-failures.json`。
- 第一轮完整自检命中旧版“等待验收才允许结果生成”的断言，改为工程结果先保存、早于验证的答复仍不算有效验收，并验证稍后独立更新。
- 实现更新后上下文因旧 resolver/资产摘要明确阻断；停止相关验证，使用官方派生快照刷新入口恢复，保留 RunLedger 的 failure/retry。
- 后续完整回归发现结果说明更正会误使真实验收失效，修正为实际交付版本绑定后再验。
- 新状态 CLI 用例在 Windows 默认编码下读取失败，夹具改为显式 UTF-8 后通过。
- 收尾生成审阅视图时一次 Python 调用参数形式错误；after 和项目状态已成功生成，随后改用公开 CLI 生成视图并再次校验通过，记录在 `evidence/finalization-attempts.json`。
- 未将上述失败或未作出的用户决定标为通过；本任务的工程结果按新规则保存，用户决定保持 `Pending`。
