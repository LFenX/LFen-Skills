# 对抗性审查停止预算与跨会话防循环

- 日期：2026-10-23（Asia/Shanghai）。
- 范围：`skills/product-engineering/run-governed-product-workflow/`；沿用现有目录与 Full/Minimal 结果载体。
- 原因：原规则只有连续两轮无问题的通过出口，没有有限预算和到限后的用户决定出口。

## 实现

- 默认每次真实授权为 3 轮审查、2 批返修、60 分钟，可在实际询问中指定其他有限额度；同意绑定已展示预算。
- 增加 `WorkStarted`，开始工作即扣费，中断不退费；结果回填不重复扣费。返修保存须核对原任务已扣费的 TaskID。
- 任一预算到限显示 `BudgetExhausted`；旧活动审查无预算显示 `BudgetRequired`，均停止新增工作并汇总，等待用户真实新决定，不自动续期。
- 仍须同一交付连续两轮完整无问题才 `Passed`；最后一轮恰好形成两轮时可通过，到限本身不等于通过。
- SKILL、verify、run、close、minimal、status 同步一次性汇总、用户决定、唯一负责人和禁止跨会话互相触发修复/复查/回报循环的规则。
- 同步两份嵌入 schema、CLI 帮助合同、受保护资产摘要及控制台依赖清单。

## 实际验证

- 针对性回归：协议 50 项、边界 181 项通过（含新增 36 项预算边界断言）。
- 完整 self_test A04：2026-10-23 15:15:09–15:16:37 UTC，exit 0；含控制台分发 12 项通过。
- runtime 检索合同通过；一致性审计 Complete，0 Blocker/Major/Minor，1 项 task_snapshot_not_applicable 观察。
- skill-creator quick_validate、目录检查、git diff --check 通过。
- 原真实审查任务只读查询得到 BudgetRequired；after.json 摘要前后一致，未篡改旧历史。
- 先前失败如实保留：A01 旧历史夹具预期；A02 CLI help 合同摘要未同步；A03 控制台新依赖未列入快照；A04 修正后完整通过。

## 交付边界

- 已保存真实工程结果不代表用户已验收，user_decision 保持 Pending。
- 本任务没有启动真实对抗性审查，没有向其他会话发消息，没有覆盖正在冻结的共享安装副本。
- 跨会话规则约束执行者；不声称 CLI 能全局拦截平台上所有聊天的工具调用。
- GitHub 源码提交：`89565de8a25c60640f1655570e8070d5a50fb90b`，已核对远端 main 一致；Skill gates 39977441636 的 Python 3.11/3.12/3.13 与目录 CI 39977441486 均成功。
- 源码完整摘要：`a8b0df25ca7617b2ef29407741392e1ff19fce5f4462576ffe37f4176326608a`，97 文件。CI 及发布回执位于本任务 evidence/。
- A05 仅纠正外部效果记录事件名并补记真实已推送结果，未再次修改或重推源码。

## 结果留档

- 本任务 after.json 已保存为 Implemented，范围对账 Passed，工程用户决定 Pending。
- 收尾通过正式 Amendment 登记任务前既有脏日志；误加的禁止动作已正式撤回，原用户需求、授权边界和回答均未改变。阻断与更正回执保留。既有暂停日志未编辑、未纳入本次提交。
- 用户在完工询问中明确选择“不启动，结束本任务（推荐）”；审查状态 Declined，轮次 0，不再启动审查或跨会话协调。
