# AR-01 对抗性审查

- 交付提交：`2c3496bb8701474d0ec3313d2143684e6d8fb2f6`。
- 独立执行者：`/root/adversarial_round_01`，新上下文，只读。
- 独立检查：2026-10-23 09:58:40—10:10:17 UTC；主代理随后复核、合并证据并登记。
- 原文：在工作流中加一个点就是 针对此任务进行多轮对抗性审查，直到连续2次对抗性审查没有发现任何问题，请优化该表述 以及 流程，然后嵌入该skill，确保其能够发挥作用，另外，对抗性审查不能直接开始，而是要在任务完成后主动询问用户是否需要进行对抗性审查
- 澄清：Skipped / Settled，rounds 为空，没有其他澄清回答。启动授权另见 review-consent.json 中真实用户回答“开始审查”。
- 方法：逐条原文、源码及关联调用方对照，102 条隔离实验；主代理补充暂缓后恢复与返修推荐反例。没有修改受审源码或安装副本。

## 原文覆盖

| 原文要求 | 实际检查 | 结论 |
|---|---|---|
| 针对此任务多轮对抗性审查 | Full/Minimal 多轮、返修引用、无关交付拒绝 | 存在恢复及返修归属缺陷 |
| 连续两次没有任何问题 | 两轮、清零、版本、时间、并发、报告身份、未解决项 | 存在错误通过路径 |
| 优化表述和流程 | 入口、方法、反例、修复、复验、退出与停止 | 文本已接入，部分运行约束失效 |
| 嵌入 skill 且发挥作用 | 命令卡、脚本、Schema、状态、审阅、CLI、部署与安装 | 接入存在，需修复以下问题 |
| 不得直接开始 | 无 Offer/答复、拒绝、暂缓、停止、未留档 | 拒绝写轮次，原文件不变 |
| 完工后主动询问 | NotOffered、询问推荐、时间、返修分支 | 主流程成立，返修会重复询问 |

## 已确认问题

| ID | 级别 | 可复现条件、预期与实际 | 位置 | 原始证据 |
|---|---|---|---|---|
| ADR-01 | P1 | 两轮通过后，公开 amendment 更换 outcome.verification 引用，当前交付摘要变化；CLI 仍将新摘要与旧 Passed/2 一起返回。应使旧轮次失效。 | adversarial_review.py 的重放与 CLI 查询 | round-01-raw/results.json：counterexample-stale-Passed-after-delivery-change |
| ADR-02 | P1 | Full 用户决定 amendment 读取旧文档后暂停；审查入口成功写入 F-LOST；前一 writer 再覆盖文件，问题及修订丢失。两 writer 均成功，随后两空轮可通过。应使用同一锁序列化。 | governance_artifacts.py amend_record/amend_record_batch 与审查写入 | round-01-raw/concurrency-results.json、concurrency-midpoint.json、audit_concurrency.py |
| ADR-03 | P2 | Round.started_at 早于所引用返修交付的 verification 和 completed_at，正确摘要仍被接受并通过。应先完成复验留档再启动新轮。Full/Minimal 均复现。 | adversarial_review.py append_review 与时间校验 | round-01-raw/results.json：counterexample-repair-round-before-verified |
| ADR-04 | P2 | 合法更正 clarification.basis，原话未改，但整个 clarification 摘要变化；查询及追加 Blocked 都 exit 2，历史无法恢复。应只绑定原文，真实变更应清零且保留可继续路径。 | requirements_subject、重放与 _load_delivery | round-01-raw/results.json：counterexample-clarification-* |
| ADR-05 | P2 | 同一物理报告以不同路径别名可凑两轮；不同报告共享需求/测试证据却被拒绝。应区分报告与支持证据，核对报告身份。 | adversarial_review.py 报告去重 | round-01-raw/results.json：counterexample-same-physical-report-aliases；boundary-results.json：distinct-reports-share-legitimate-support |
| ADR-06 | P2 | 原审查已授权且有问题，返修任务留档后是 NotOffered，signals 优先推荐再次询问。应将该返修关联到原审查，继续原会话。 | signals.py recommendations 与 close 初始化 | round-01-raw/boundary-results.json：counterexample-repair-repeats-optin-recommendation |
| ADR-07 | P3 | 输入 []、null 或字符串 JSON，Schema 校验前 entry.get 引发 AttributeError/Traceback/exit 1。应受控 ERROR/exit 2，不改文件。 | adversarial_review.py append_review/main | round-01-raw/extra-results.json：CLI-invalid-* |
| ADR-08 | P2 | 用户已选 Deferred/Declined，之后主动明确 Accepted，仍被要求新的 Offer。无需重复询问即可依据真实新决定开始；既有授权及问题历史应保留。 | adversarial_review.py Decision 分支 | round-01-supplement.json |

## 证据与边界

- `round-01-raw/receipt.json` 记录 10 份原始脚本、输出的字节摘要及重放方法；四份结果共 102 条实验记录。关键并发中点和最终输出均已保存。
- 公开代码只读、权限边界、历史无字段兼容、两 Schema 同源、CLI 帮助、只读查询无写、控制台部署闭包及当前 Windows 安装副本均检查。
- 观察 O-01：实时控制台没有新增审查详情，但生成审阅 Markdown 与 signals 已显示。原文未要求扩展实时控制台 UI，本观察不认定为需求缺陷，不扩大到新界面开发。
- 未执行非 Windows 实机安装、真实浏览器操作；当前任务环境为 Windows，已检查模型/渲染、文件闭包及安装字节。未把这些操作表述为已执行。原文所要求的工作流范围逐条检查完成。
- 合成夹具不作为真实人的决定或本任务实际审查轮次；本报告记录的是实际独立审查及其反例。
- 本轮有 8 项已确认问题，连续无问题计数为 0，须返修复验后开启下一轮。
