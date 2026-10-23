本次任务使用的 skills：run-governed-product-workflow（verify）。

# AR-02 独立只读对抗性审查

结论：发现 2 项已确认问题（P1 × 1、P2 × 1）。本轮不计为干净轮次；需要返修并从新交付版本重新累计。

- 执行者：/root/adversarial_round_02。
- 开始 UTC：2026-10-23T10:47:42.7498397Z；结束 UTC：2026-10-23T11:10:17.596439Z。
- 固定提交：62aeb847cfb6fe75679a3b0ae66fdababd995bcf。
- 固定 skill：D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow；96 文件冻结摘要：5376dee45f101d8374a229aae34ce9dae2801a34c9d5b09d3ee8767bea4fac19。
- 实际已验证交付：T-ADVERSARIAL-20261023-002；completed_at=2026-10-23T10:41:43.098330Z。
- 原任务的真实问题发生于 2026-10-23T09:34:53.863146Z；明确回答“开始审查”发生于 2026-10-23T09:58:06.866514Z。本轮使用该已授权会话。
- 146 个最终有效用例：132 个满足断言，14 个断言失败均归入以下两项问题。初始错误和重试单独留存，不冒充通过。

## 原始权威输入与逐条结论

以下完整原话从 T-ADVERSARIAL-20261023-001/before.json 的 request_snapshot 独立读取；没有以派生任务卡或上一轮报告替代。

> 在工作流中加一个点就是 针对此任务进行多轮对抗性审查，直到连续2次对抗性审查没有发现任何问题，请优化该表述 以及 流程，然后嵌入该skill，确保其能够发挥作用，另外，对抗性审查不能直接开始，而是要在任务完成后主动询问用户是否需要进行对抗性审查

澄清：mode=Skipped、state=Settled、rounds=[]，没有需要另行展开的真实回答。每条结构化记录均保留同一完整原句、来源及限定词，见 requirements-audit.json。

| ID | 独立摘取的要求 | 状态 | 差异与证据 |
|---|---|---|---|
| R01 | 将审查绑定到本任务，支持多轮查错、返修、复验 | 已实现 | FULL-12；MIN-12；CROSS-MIN-FULL-ROUND；FULL-WRONG-DELIVERY；MIN-WRONG-DELIVERY |
| R02 | 只有当前同一交付版本连续两轮完整审查未发现问题才结束 | 部分实现 | AR02-F002：新登记且内容不同的返修交付未使旧计数失效，旧交付可继续获得 Passed。 |
| R03 | 优化原要求的表述，使启动、轮次、完成判据明确 | 已实现 | STATIC-SCHEMA；STATUS-OFFER |
| R04 | 优化流程并嵌入 skill，形成可执行、可核对的调用机制 | 部分实现 | AR02-F001 拒绝文档支持的有效报告路径；AR02-F002 可把过期交付记为通过。 |
| R05 | 对抗性审查不能直接开始；必须取得本次审查明确同意 | 已实现 | FULL-03；FULL-04；FULL-06；FULL-08；FULL-10；FULL-11；MIN-03；MIN-04；MIN-06；MIN-08；MIN-10；MIN-11；EDGE-13；FULL-27；MIN-27 |
| R06 | 任务工程完成后主动询问是否需要审查，保留开始/拒绝/稍后分支 | 已实现 | FULL-01；FULL-05；FULL-07；FULL-09；FULL-34；MIN-01；MIN-05；MIN-07；MIN-09；MIN-34；STATUS-OFFER |

未实现项：无独立的完全未实现项。部分实现项：R02、R04，分别由 AR02-F002、AR02-F001/002 证明；不得作为已全部实现交付。

## 已确认发现

### AR02-F001 [P2] 合法绝对 report_ref 被原始路径与归一化路径比较拒绝

- 位置：D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\adversarial_review.py:348；D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\commands\verify.md:162。
- 预期：验证文件边界和内容后接受文档支持的绝对路径，并保存规范化后的报告引用。
- 实际：facts 中的 report_ref 已规范化为项目相对路径；348-350 行把输入必填 report_ref 作为派生值逐字比较，绝对路径必然不同。
- 影响：用户按文档提供合法绝对路径时无法追加审查轮次；同一记录改为规范相对路径才能继续。

复现步骤：

1. 使用绝对路径填写 report_ref，其他字段使用真实临时夹具当前绑定；执行 adversarial_review.py --entry-json-file。
2. 观察 exit 2 和 ERROR: report_ref must match the actual report or delivery；结果文件与封闭 RunLedger 未改写。
3. 仅将同一报告的 report_ref 换为规范项目相对路径，再执行同一 Round；exit 0、clean_streak=1。
4. Full 与 Minimal 均复现；等价 ./ 项目相对路径也被拒绝。

误报排除：

- 同一个实际非空文件、同一 Round、同一交付摘要的规范相对路径对照成功，排除授权、摘要、时间、报告内容及 fixture 失效。
- 绝对路径属于 commands/verify.md:162 的明确承诺，不是额外路径功能建议。

证据：

- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\supplement-results.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\results-initial-absolute.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\audit-initial-absolute.log
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\reproduce-findings.log

### AR02-F002 [P1] 新登记并复验的返修版本不使旧交付计数失效，旧版可继续获得 Passed

- 位置：D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\adversarial_review.py:205；D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\adversarial_review.py:326；D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\adversarial_review.py:174；D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\commands\verify.md:138。
- 预期：当前交付改变时旧计数归零并显式失效；旧 delivery 不能作为当前版本的后续干净轮次，新 Beta 必须独立完成两轮。
- 实际：_current_bindings 仅读取历史 Round 已经引用的任务；新登记返修没有进入当前绑定集合。append_review 核对旧任务自身摘要仍一致后接受，review_state 的 subject 未变而累计为 2。
- 影响：当前 Beta 未经历两轮审查，却可把父审查标记 Passed 并停止；违反本需求的核心完成条件。

复现步骤：

1. 初始 src/label.txt 为 baseline；通过合法任务将其交付为 Alpha\n，记录 mutation、成功 verification 与 close。
2. 原审查 Offer/Accepted 后记录 Alpha 的第 1 个完整干净轮次，得到 clean_streak=1。
3. 通过新返修任务将同一文件改为 Beta\n，保留实际内容与 SHA256 证据；记录 mutation、成功 verification，close 时关联原审查。子任务正确显示 ManagedByParent。
4. 只读查询原审查；实际仍 InProgress/1，而非 Stale/0。
5. 追加独立新报告，但 delivery_task_id 仍指向旧 Alpha；CLI exit 0 并得到 Passed/2。signals 与生成的审阅 Markdown 同步显示该旧版 Passed。
6. Full 与 Minimal 均复现。

误报排除：

- Alpha 与 Beta 的实际文件内容、SHA256 不同；两个交付均有成功 verification 和已保存结果。
- 返修通过公开 close 参数合法登记，项目、直接依赖、父审查同意均通过校验；未离线伪造或覆盖已保存治理记录。
- 报告内容与 round_id 均独立，时间在复验和保存之后；不是报告复制、提前开始或授权缺失。
- 使用正确新 delivery 时重算为第一轮的对照 EDGE-01/EDGE-06 通过；问题是旧 delivery 没有被判为当前已过期。

证据：

- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\version-proof-FULL.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\version-proof-MIN.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\stale-round-FULL.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\stale-round-MIN.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\signals-after-FULL.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\supplement-run-3\signals-after-MIN.json
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\boundary-run\generated-FULL.md
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\boundary-run\generated-MIN.md
- C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\reproduce-findings.log

## 条件与例外的正反对照

- 条件：工程完成并保存后才询问/审查。成立输入：FULL-01, MIN-01, STATUS-OFFER；不成立输入：FULL-34, MIN-34；结论：Passed。
- 条件：仅明确同意才开始；未答/拒绝/推迟不得开始。成立输入：FULL-11, MIN-11, FULL-12, MIN-12；不成立输入：FULL-04, FULL-06, FULL-08, FULL-10, MIN-04, MIN-06, MIN-08, MIN-10；结论：Passed。
- 条件：只有连续两轮完整无问题且无未解决/未检查项才通过。成立输入：FULL-16, MIN-16；不成立输入：FULL-19, FULL-21, FULL-23, MIN-19, MIN-21, MIN-23, FULL-COVERAGE-INCOMPLETE, FULL-UNREVIEWED, MIN-COVERAGE-INCOMPLETE, MIN-UNREVIEWED；结论：Passed for fixed registered subject; current-version switch fails AR02-F002。
- 条件：版本或原文变化使旧计数失效；说明更正不改变绑定。成立输入：EDGE-05, FULL-REQUEST-CHANGED, MIN-REQUEST-CHANGED, FULL-ANSWER-CHANGED, MIN-ANSWER-CHANGED, VERSION-FULL-QUERY, VERSION-MIN-QUERY；不成立输入：EDGE-03, EDGE-04；结论：Partial: same-task modification invalidates; newly registered repaired task does not。
- 条件：返修沿用已同意原审查，禁止无父会话或递归开始。成立输入：FULL-35, MIN-35, CROSS-MIN-FULL；不成立输入：FULL-36, MIN-36, FULL-NO-CONSENT-PARENT, MIN-NO-CONSENT-PARENT, FULL-STOPPED-PARENT, MIN-STOPPED-PARENT；结论：Passed。
- 条件：独立报告可以共享支持证据；同一报告/内容不得复用。成立输入：FULL-16, MIN-16；不成立输入：FULL-14, FULL-15, MIN-14, MIN-15；结论：Passed。
- 条件：合法绝对/相对报告路径应可使用；文件越界/空报告不得使用。成立输入：PATH-FULL-ABS, PATH-MIN-ABS, PATH-FULL-CANONICAL, PATH-MIN-CANONICAL；不成立输入：EDGE-09, EDGE-10；结论：Partial: AR02-F001。
- 条件：停止后禁止继续；真实后续同意可恢复。成立输入：FULL-28, MIN-28；不成立输入：FULL-27, MIN-27；结论：Passed。
- 条件：人工验收与审查授权互不替代；旧记录不补造协议。成立输入：EDGE-14, FULL-30, MIN-30, CONCURRENCY-FULL, CONCURRENCY-MIN；不成立输入：EDGE-13, COMPAT-01, COMPAT-02；结论：Passed。

## 覆盖范围、兼容与边界

已完整检查入口 SKILL、verify/close/status/minimal 命令说明、adversarial_review 主实现、Full/Minimal 结果生成与归属、修订守卫/锁、Schema、signals、生成审阅 Markdown、get_approval_subject、既有部署闭包及安装分发。其余不相关规范正文没有递归读取。

- 需求原文及澄清绑定、工程完成/同意/停止时间、轮次/问题 ID、独立报告及内容、未检查项、阻塞、问题处置、返修关联与复验均有正反对照。
- 既有结果、user_decision 和封闭 RunLedger 保持兼容：Pending 不被替换成批准，普通 Acceptance 不启动审查；实际并发线程保存拒绝决定与新发现，Full/Minimal 均无丢失。
- 缺少协议的旧结果只读显示 LegacyUntracked；旧轮次显示 LegacyNotRevalidated，不被计为新 v2 两轮通过。旧记录用纯读取模型测试，不离线改写权威文件。
- 初始 FZ-01 对源、安装克隆及 Codex Junction 的 96 文件逐项 SHA256 核对一致；结束时固定源 96 文件仍无漂移，但安装目录出现下述环境变化。
- 只有一个独立执行者完成本轮；146 个用例没有拆成多个审查轮次。没有读取先前任何轮次报告，没有执行 self_test，没有启动子 Agent。
- 未向共享仓库、真实安装目录或真实用户决定写入。本轮测试、夹具、Git 项目及报告全部位于 OS Temp。

未检查需求项：[]。执行环境与范围限制：

- 独立反例在 Windows / Python 3.13.0 执行；未在 Python 3.11、3.12、macOS、Linux 重跑本轮反例。未把其他人的工程测试结果作为本轮结论。
- 本轮不操作生产、不安装/更新真实分发、不启动 Web 服务；安装分发用文件逐项摘要与入口解析检查。
- 机器结构和摘要校验不证明自然语言审查质量；本轮发现项均有自主构造、实际执行的反例。
- 没有新增 live console UI 的原始要求，因此没有将新 UI 呈现作为缺陷或未实现项。

## 重试与原始文件

- 初始合法绝对 report_ref 使 Full/Minimal/返修组在首个 Round 失败；该结果归入 AR02-F001，未计作干净轮次。改用规范项目相对路径完成后续覆盖。 文件：audit-initial-absolute.py, audit-initial-absolute.log, results-initial-absolute.json。
- 真实 Git 夹具沿用了仅绝对根路径声明，scope reconciliation 拒绝 src/label.txt；在新的临时项目预先声明 src/label.txt 后重试。该夹具错误不作为产品发现。 文件：supplement-initial.py, supplement-initial.log, supplement-run/supplement-results.json。
- 测试进程读取 signals 中文输出时 UTF-8 与系统管道编码不一致；在新临时项目以 Python -X utf8 运行 CLI 后完成。该读取错误不作为产品发现。 文件：supplement-run-2.py, supplement-run-2.log, supplement-run-2/supplement-results.json。
- 独立重放第一次遇到 Windows Temp 短路径与 resolve 后长路径不一致；把新建临时根 resolve 后完成两种载体重放。有效重放目录 ar02-replay-p28x3bu3。 文件：reproduce_findings.py, reproduce-findings.log。

独立重放命令：

```powershell
python -X utf8 -B "C:\Users\Administrator\AppData\Local\Temp\ar02-independent-20261023\reproduce_findings.py"
```

已成功的最新重放结果：C:\Users\Administrator\AppData\Local\Temp\ar02-replay-p28x3bu3\reproduction.json

原始脚本：audit.py、audit-initial-absolute.py、supplement.py、supplement-initial.py、supplement-run-2.py、boundaries.py、reproduce_findings.py。原始结果：canonical-run/results.json、supplement-run-3/supplement-results.json、boundary-run/boundary-results.json。

逐例 input / expected / actual / result 完整记录见 cases.json（146 例），并保留原始分组 JSON。

## 安装环境末尾观察（不列为第三项代码发现）

- 观察 UTC：2026-10-23T11:10:17.596439Z。
- 固定源码：D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\governance_artifacts.py；SHA256=7737ed94dfe35f785e783d6385aed0db0bbe284e5c73f938f1d839d52ef1d574，242084 字节。
- 安装克隆及其 Codex Junction：C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow\scripts\governance_artifacts.py；SHA256=a4309d3d994a0700ee0066aa94d36f2ce860c80f14c92238cc8f71bb7d0663a9，245535 字节。
- 最小差异：安装版 capture_source_snapshot 新增 worktree_baseline；新增 _git_path_states；reconcile_scope 新增 dirty-path-bytes-v1 对照与 preexisting_unchanged。不是仅换行变化。
- 初始检查相符、末尾偏离，变更来源未确认。审查执行者未写入安装路径；固定源码的两项反例结论不受影响。
- 原始摘要和逐行差异：installation-observation.json、installation-observation.diff。主会话独立核对该外部变化。
