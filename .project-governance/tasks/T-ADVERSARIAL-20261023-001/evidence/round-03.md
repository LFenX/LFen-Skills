# AR-03 独立只读对抗性审查

本次任务使用的 skills：run-governed-product-workflow。

**结论：发现 1 个确认问题 AR03-001（P2）。本轮不能计为无问题轮次，连续计数归零。**

| 固定信息 | 实际值 |
|---|---|
| UTC 开始 | 2026-10-23T11:47:54.835315Z（审查子会话启动标记）；首次本机核时 11:48:43.0194577Z |
| UTC 结束 | 2026-10-23T12:04:06.773242Z |
| 提交 | `11ecd2a3d05f51268ff51ed15cb0ab3cd7990648` |
| skill 源码冻结 | 96 文件，`3ef1adf1ff23fb1fb48dfb4fe9b4e16ef2b815fa084fb2d70d31eed1d01244a8`；结束时逐文件核对全部一致 |
| 交付对象 | T-ADVERSARIAL-20261023-003，工程结果已保存 Implemented |
| 实际检查 | 188 项；184 项符合预期，4 个断言共同暴露同一缺陷 |
| 审查执行者 | 新只读子 Agent `/root/adversarial_round_03`；未读取先前轮次报告 |

## 原文逐条核对

权威源：`.project-governance/tasks/T-ADVERSARIAL-20261023-001/before.json` 的 `request_snapshot` 与 `clarification`。原话：

> 在工作流中加一个点就是 针对此任务进行多轮对抗性审查，直到连续2次对抗性审查没有发现任何问题，请优化该表述 以及 流程，然后嵌入该skill，确保其能够发挥作用，另外，对抗性审查不能直接开始，而是要在任务完成后主动询问用户是否需要进行对抗性审查

澄清为 `mode=Skipped`、`state=Settled`、`rounds=[]`，没有额外真实澄清回答。下表各项均引用上述完整原句，完整 quote 与证据记录保存在 `requirement-review.json`。

| 项 | 独立提取的要求 | 状态 | 证据与缺口 |
|---|---|---|---|
| R01 | 针对本任务进行多轮对抗性审查 | 已实现 | Full/Minimal 多轮、问题处置、返修归属及独立执行流程均已实现。 `commands/verify.md:127` |
| R02 | 直到连续两次对抗性审查均没有发现任何问题 | 部分实现 | 普通同版两轮及清零分支成立；AR03-001 允许重复历史报告被重新计为一轮并错误 Passed。 `commands/verify.md:135` |
| R03 | 优化表述与流程 | 已实现 | 表述明确开始条件、拒绝/推迟、每轮完整覆盖、返修复验、计数和停止条件。 `SKILL.md:26` |
| R04 | 嵌入该 skill 并确保能够发挥作用 | 部分实现 | Full/Minimal、状态、Schema、分发及安装入口均已接入；AR03-001 使关键两轮通过判定在报告更正边界失效。 `scripts/governance_artifacts.py:3975` |
| R05 | 不能直接开始；任务完成后主动询问用户是否需要审查 | 已实现 | 已保存 Implemented 后才可 Offer，明确 Accepted 才可 Round；无答复、拒绝、推迟、停止均不启动。 `SKILL.md:190` |

R02 的部分实现缺口：报告去重丢失历史身份，重复报告可重新贡献无问题计数。

R04 的部分实现缺口：相关入口已接入，但该错误计数可从公开入口持久化并显示 Passed。两项均由 AR03-001 的实际反例证明。

## 条件与反例覆盖

逐例 input / expected / actual / result 与完整 CLI 参数、stdout、stderr 见 `results.json`；下表只列对照及索引，避免复制全部输出。Full/Minimal 均实际运行。

| 条件/边界 | 正例实际结果 | 反例实际结果 | 证据 ID |
|---|---|---|---|
| 工程已完成并保存 | Implemented 初始化 NotOffered | 无结果拒绝写入且源记录不变；Blocked 为 NotApplicable 且拒绝 Offer | `*-initial`、`*-no-saved-engineering-result`、`*-nonimplemented-offer-refused` |
| 实际询问后明确同意 | Offer→AwaitingUser，Accepted→InProgress | 无 Offer、无回答、Declined、Deferred、Stopped 均拒绝轮次 | `*-offer`、`*-accept`、`*-no-offer-decision`、`*-awaiting-round`、`*-declined-round`、`*-stopped-round` |
| 连续两轮完整无问题 | 第一轮 1，第二轮 Passed/2 | Incomplete、未检项、问题未处置、Blocked 清零；Passed 后拒绝继续轮次 | `*-clean-1/2`、`*-unchecked`、`*-finding`、`*-unresolved`、`*-blocked`、`*-after-pass` |
| 真实时序与绑定 | 当前已验证交付及原文摘要通过 | 早于留档/验证、未来时间、无时区、错误交付/原文摘要、伪填派生时间均拒绝 | `*-precompletion-round`、`*-future-event`、`*-naive-time`、`*-wrong-delivery-hash`、`*-wrong-requirements-hash` |
| 报告完整性与独立性 | 不同报告可共用支持证据 | 空/缺失/越界报告、同内容副本和路径别名原本拒绝；但旧报告变更后的原内容副本错误放行 | `*-empty-report`、`*-copied-report`、`*-report-alias`、`*-identity-reuse-recorded-content` |
| 问题处置 | NotAnIssue 需指向已有问题；新验证返修可 Fixed | 未知问题、重复问题 ID、同一交付声称 Fixed 均拒绝 | `*-notissue`、`*-repair-clean-1`、`*-unknown-resolution`、`*-duplicate-findings`、`*-same-version-fix` |
| 返修接续 | Full 和 Minimal 返修均 ManagedByParent；留档即使旧版计数失效；新版本从 1 重算 | 旧版、无关交付、未复验时序、递归父任务与已 Passed 父会话均拒绝 | `*-repair-stale-before-round`、`*-minimal-repair-managed`、`*-old-delivery`、`*-unrelated-delivery`、`*-recursive-repair-parent` |
| 历史兼容 | 缺协议字段为 LegacyUntracked；旧两轮为 LegacyNotRevalidated | 不自动补录、不自动重启、未知协议版本拒绝 | `*-legacy-untracked`、`*-legacy-pair-not-current-pass`、`*-legacy-no-auto-restart`、`*-unknown-review-contract` |
| 说明更正与独立用户决定 | prose / survey basis / user_decision 更正保持同版计数 | 普通 amendment 改删审查历史、改写返修归属拒绝 | `*-metadata-after`、`Full-survey-metadata-keeps-streak`、`Full-history-rewrite`、`Full-parent-rewrite` |
| 并发与真实调用方 | Full/Minimal 审查追加与普通修订同时成功，两个变更保留且 revision+2；signals 与生成 Markdown 显示状态 | 未观察到丢写；受控锁均释放 | `*-concurrent-append-and-amend`、`*-concurrency-final-valid`、`*-review-markdown-visible` |
| Schema、源码与安装分发 | Full/Minimal/runtime Schema 相同，import closure 完整；安装实际入口可读写并两轮收敛 | 96 文件冻结无漂移；安装仅保留已说明的一文件环境差异 | `schema-parity`、`distribution-import-closure`、`source-freeze-96-files`、`installation-known-difference`、`*-installed-round-2` |

## AR03-001 · P2 · 报告更正后可复用历史内容凑满两轮

位置：`scripts/adversarial_review.py:382` 仅按当前报告文件摘要拒绝重复；`:253` 读取的是现存文件摘要。回放中 `:165` 虽计算历史摘要重复，`:190` 的实际连续计数未使用该条件。

可复现步骤：

1. 合法工程结果经 Offer / Accepted 后，公开入口记录完整无问题的报告 A，计数为 1。
2. 更正 A 的文件内容；状态正确变为 Stale、计数 0。
3. 将 A 记录时的原始字节另存成 B，使用新的轮次 ID、当前时间、同一有效交付与原文摘要提交 Round。
4. 预期拒绝该历史内容副本或不计数；实际 exit 0，InProgress、计数 1。
5. 再提交一份新报告 C；预期不能凭 B+C 通过，实际 Passed、计数 2。

以上询问、决定、轮次全部通过公开 CLI 追加；复现未离线改写 after.json / task-record.json。只更正旧报告文件并另存其原内容。原始命令参数、完整 entry JSON、实际 stdout/stderr 和前后状态在 `finding-AR03-001.json`，现场文件保持完整。

| 载体 | A 与 B 持久化的相同 report_sha256 | 最终实际状态 |
|---|---|---|
| Full | `403ed028dcc74a8e3d02fee3b01f626f7063786a197e1313f8703ff87a7c64d1` | Passed / clean_streak=2 / rounds=3 |
| Minimal | `adf360e3573ebbbb42cd565af52a50a1fddebc2ac5a1f1e9d91c067f2cfdab1b` | Passed / clean_streak=2 / rounds=3 |

影响：旧证据变更使历史原摘要从当前文件摘要集合消失；副本遂被当作新审查，破坏“两次完整审查”的机器计数。涉及 Full 与 Minimal 共用实现，不涉及未授权启动或伪造人类来源。

修复边界：追加和回放均应保留并核对已记录的 report_sha256 唯一性，不能只依赖可变文件的当前摘要。正常独立报告、历史兼容与版本失效继续按原规则处理。

## 范围与限制

- 已完成约定的文案、Full/Minimal 实现、Schema、授权/状态/时序/版本/报告/返修/兼容/并发、真实调用方及安装分发检查；未检查项为 []。
- 执行环境为 Windows、Python 3.13。未在其他操作系统或 Python 版本重跑；未用上游 CI、自验或前轮报告替代本轮判断。
- 夹具为 Temp 内明确标注的合成工程任务；用户决定与普通 Gate 仅用于协议测试，不声称这些合成答复来自真实人类。
- 机器不能证明真实人类来源或自然语言审查质量。没有把纯离线伪造所有治理字段当作程序反例。
- 安装 Junction 指向 `C:/Users/Administrator/.lfenskills/skills/product-engineering/run-governed-product-workflow`；仅 governance_artifacts.py 为已说明并行任务差异，SHA256 为 `ff8124ccd76fcc76527ac2ea1ee2c848aff0604f2a15319e6bf193066bee4bd3`。95 文件相同，安装实际入口的正向调用已验证。
- 仓库、安装目录、真实任务和用户决定均未修改；所有脚本、报告与原始结果只写 OS Temp。

## 原始证据索引

- `results.json`：188 项逐例输入、预期、实际、结果。
- `finding-AR03-001.json`：唯一确认问题，含公开 CLI 全输入/输出、重复摘要及两个载体的最终状态。
- `ar03_audit.py`、`ar03_extended.py`、`ar03_boundaries.py`：独立主测试脚本。
- `ar03_report_identity.py`：确认问题复现脚本，依赖同目录前两个脚本；原始现场已存在，复跑应使用新的 Temp 输出目录保留当前证据。
- `report-identity-repro-Full.json`、`report-identity-repro-Minimal.json`：问题现场摘要。
- `report-identity-Full/`、`report-identity-Minimal/`：完整合法夹具、原报告/副本及持久治理文件。
- `source-verification.json`：结束时逐文件实际 SHA256、固定版本及工作树状态。
- `requirement-review.json`、`review-summary.json`：完整原话逐条核对与本轮元数据。
