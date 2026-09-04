# 任务类型裁剪与统一执行流程规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | VC-PPG-PRO-001 |
| 英文名称 | Task-Type Tailoring and Unified Execution Process Standard |
| 正式文件名 | `Vibe_Coding_任务类型裁剪与统一执行流程规范_V6.3.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-08-14 |
| 责任人 | 项目负责人；正式身份待登记 |
| 编制者 | Coding Agent |
| 批准人 | 待具有权限的人类批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-COM-001、VC-PPG-COM-002、VC-PPG-DEC-001、VC-PPG-IDX-001、VC-PPG-MAP-001 |
| 专业控制依赖 | C01 至 C12、按触发条件适用的 E01 至 E05 |
| 变更来源 | CHG-0006、IMA-0003、CHD-0004 Proposed；保留 CHG-0004/CHG-0005 历史 |
| 符合性检查 | RVR-V63-0001 Candidate |
| 访问级别 | Internal |
| 保留要求 | 正式修订、评审、批准、替代、流程运行和基线记录永久保留 |

本文件在具有权限的人类批准、Gate Decision 和新 Baseline 建立前，只是 V6.3 Candidate，不得被声明为 Approved、正式 Baseline 或发布依据。

## 2. 目的

本规范建立跨任务类型的唯一流程路由，使所有任务共用一个八阶段主流程，并以 TaskContract、RunLedger 和 TaskOutcome 分别承载任务执行前、执行中和任务终态事实；Task Profile 作为 TaskContract 字段驱动阶段深度、专业规范、Profile 实例、Evidence、Gate 和人类确认裁剪。

本规范实现以下控制目标：

1. 消除 C01 至 C12、E01 至 E05 第 17 章之间的流程路由重复解释；
2. 为 DS-01 至 DS-04、DT-01 至 DT-09 提供统一、可执行和可检查的流程；
3. 保持专业规则由原主规范负责，本规范只负责流程顺序、触发和交接；
4. 保证小任务减少实例和载体，但不删除适用控制目标；
5. 防止缺陷、工程变更、配置变更和紧急处置被错误升级为完整产品需求流程；
6. 防止新产品、新功能、需求修订、迁移和生产处置绕过必要的产品、风险、变更、验证或发布控制；
7. 为 Agent 提供可解析的流程入口，同时保留人类批准、验收、发布和风险接受边界。

## 3. 适用范围

本规范适用于采用 V6.3 Candidate 规范体系的 Web App、SaaS、AI Native Web 产品和内部业务系统，覆盖：

- DS-01 新产品；
- DS-02 产品族或模板派生；
- DS-03 现有产品演进；
- DS-04 运行中产品处置；
- DT-01 新产品；
- DT-02 产品族实例化；
- DT-03 新功能；
- DT-04 需求澄清；
- DT-05 需求修订；
- DT-06 缺陷修复；
- DT-07 工程变更；
- DT-08 配置或内容变更；
- DT-09 迁移、替代或退役；
- Normal 与 Emergency 执行模式；
- UI/UX、API/Integration、Data/Schema、Identity/Security/Privacy、AI/Data Governance、Architecture/Multi-repo、Deploy/Operations、Agent/Collaboration 变更面。

本规范适用于形成正式产品交付、受控资产、Evidence、Review、Decision 或实际变更的需求澄清、计划、Agent 执行、人工执行、验证、验收、发布、观察和收尾任务。

普通信息查询、知识问答以及不形成正式 Review、Evidence、Decision 或其他受控记录的只读检索不适用本规范。只读活动一旦形成正式影响分析、评审、审计、Evidence、Decision 或受控报告，必须按对应 Development Type 进入本规范，并完成适用阶段。

## 4. 不适用范围

本规范不负责：

1. 重新定义六类正式元类型、137 个兼容领域 Profile、状态模型或最低信息；
2. 重新定义 C02 风险等级、E01 至 E05 触发条件或 C07 Authority；
3. 替代 C01 至 C12、E01 至 E05 的专业控制、模板和检查清单；
4. 规定数据库、API、平台界面或工作流工具的物理实现；
5. 把团队聊天、工单状态、Git 历史或 Skill 内部步骤单独提升为完整权威事实源；
6. 代替人类作出 Acceptance、Gate Approval、Risk Acceptance、Release Decision 或 Baseline Decision；
7. 要求每个任务创建全部 Profile 实例或每个 AuthorityAsset 占用独立物理文件。

若本规范与正式产物目录、状态模型或单项专业规范冲突，必须停止受影响路由并提交变更决议；不得静默选择。

## 5. 规范性用语

“必须”“禁止”“应”“不应”“可以”和“可选”按 VC-PPG-COM-001 使用。本规范不使用“尽量”“适当”“酌情”等不可验证表述。

规范优先级如下：

1. 已批准且适用于当前范围的 Baseline；
2. 已批准的 Change Decision、Gate Decision 和授权边界；
3. VC-PPG-COM-001、VC-PPG-COM-002、VC-PPG-DEC-001；
4. C01 至 C12、已激活的 E01 至 E05；
5. 本规范的统一流程路由；
6. 团队工作流、Skill、模板和工具实现。

候选或 In Review 文件不得覆盖已批准 Baseline。低层级实现不得重定义高层级规范语义。

## 6. 术语与定义

| 术语 | 定义 | 边界 |
|---|---|---|
| 统一八阶段主流程 | 初次澄清、二次确认、条件深化、计划、执行、验证与验收、发布与观察、收尾的固定顺序 | 是流程结构，不是新的元类型 |
| 流程路由 | 根据 Task Profile 决定阶段深度、适用规范、产物动作、Gate 和交接 | 必须引用规则和事实依据 |
| 主开发类型 | 当前交付目标的首要 Development Type | 不得覆盖同时成立的次级类型 |
| 次级开发类型 | 同一交付范围内同时成立、但不改变首要交付目标的 Development Type | 具有独立批准或发布边界时必须拆分任务 |
| 阶段深度 | 某阶段执行到何种信息、证据和评审粒度 | 不得用于删除适用控制目标 |
| TaskContract | 执行前目标、范围、权限、验收、计划、Task Profile 和 Artifact Manifest 的结构化契约 | Run 开始时冻结，后续变化通过 Amendment 留痕 |
| RunLedger | 只追加记录变更、失败、验证、外部副作用、门禁和回滚的重要事件 | 不记录普通读取、搜索和可由 Git 低成本重建的信息 |
| TaskOutcome | 记录已成立事实、实际变化、验证、未完成项、遗留问题和后续任务的终态对象 | 不保存执行前指令，不替代项目级 ProjectState |
| ProjectState | 由有效 TaskOutcome 与当前 AuthorityAsset 生成的项目当前状态 | 禁止直接编辑 |
| 重新分类 | 新证据导致 Development Type、Change Surface、Risk 或 Extension Trigger 变化 | 必须保留原分类、依据和影响 |
| 阶段缩短 | 某阶段的适用控制目标已由有效 Baseline 覆盖，或该阶段在当前 Scope 内无适用控制活动 | 阶段仍保留进入、活动与退出记录；必须记录覆盖或不适用依据、适用范围和关联 Artifact Manifest 项，不得对阶段使用产物实例动作 |

TaskContract、Task Profile、Artifact Manifest、RunLedger、TaskOutcome、ProjectState、Delivery Scenario、Development Type、Change Surface、Risk Level、Extension Trigger、Baseline Inheritance、Execution Mode 和五类实例动作的唯一术语来源是 VC-PPG-COM-001 与 VC-PPG-COM-002。

## 7. 角色与职责

| 角色 | 必须履行的职责 | 禁止事项 |
|---|---|---|
| Requestor | 说明期望结果和不可发现的关键约束；确认目标是否正确 | 不得把模糊愿望直接声明为已批准 Requirement |
| Task Owner | 对目标、Scope、依赖、时序和结果负责 | 不得隐瞒已知影响或未决问题 |
| Classification Owner | 确认 Development Type 和需要时的重新分类 | 不得用低控制类型规避 Change、Risk 或 Gate |
| Agent | 检查环境和 Baseline；起草 TaskContract、Task Profile、Artifact Manifest、Evidence 汇总和检查结果 | 不得自批、虚构 Evidence 或扩大 Scope |
| Implementer | 按 C07 Authority、C11 CHD 和批准计划实施人工或自动化变化，并维护等价 RunLedger 的重要事件、变化、失败和 Evidence | 不得以人工操作、控制台操作或非 Agent 执行为由绕过 Scope、Change、Run、Verification 或 Trace |
| Professional Owner | 对产品、设计、安全、数据、架构、运营等专业规则作判断 | 不得由通用 Gate Approver 替代法定或专业 Authority |
| Verification Owner | 执行可复核验证并固定 Evidence | 不得把工具成功写成 Acceptance |
| Acceptance Authority | 作出验收决定 | 不得在验收输入不完整时声称通过 |
| Release Authority | 作出发布、回滚或继续观察决定 | 不得由实现者默认为自己具有该权限 |
| Gate Approver | 根据 Gate 输入作出进入下一阶段的决定 | 不得用 Gate Decision 替代资产批准或风险接受 |
| Records Steward | 保持版本、状态、追踪、保留和替代关系可解析 | 不得无痕覆盖历史或失败记录 |

同一人可以承担多个无冲突角色，但 High/Critical、生产发布、风险接受及专业授权必须满足 C07、C11 和 C12 的职责分离要求。

## 8. 管理对象与关系

### 8.1 执行前输入：TaskContract

每个任务必须在执行前形成 `before.json`，其 TaskContract 至少包含：

- ProjectID、WorkItemID、TaskID、ordinal、depends_on、supersedes、blocked_by；
- 期望结果、In Scope、Out of Scope、允许路径和禁止动作；
- 执行权限、Authority 引用、Stop Condition 和所需 Gate；
- Acceptance、唯一计划、验证和回退；
- Source Snapshot；
- Task Profile，其中至少包含：
- Delivery Scenario；
- 一个或多个 Development Type，并标识主类型；
- `development_type_scopes`，为每个已选类型绑定一个或多个 `scope.in_scope` 精确值；
- Change Surfaces；
- C02 Risk Level；
- E01 至 E05 Extension Triggers；
- E01 至 E05 `extension_evidence_refs`；Retiring/Retired 必须引用退役计划或证据；
- Baseline Inheritance；
- Normal 或 Emergency；
- VC-PPG-TAIL-001 规定的全部适用性事实，值为 Yes、No 或 Unknown；
- 判定依据、置信度、Source Snapshot 和未决问题；
- 当前 Stage 的 `tailoring_resolution`，包含规则表版本/哈希、22 个规范源聚合哈希、解析器与 TaskContract Schema 哈希、输入摘要、适用/待判定规范、控制强度、阻断原因、规则 ID、源章节定位和 137 Profile 覆盖摘要；
- 需要人类决定的 Gate；
- Artifact Manifest。

Run 首次开始时 TaskContract 进入 `Frozen`。后续 Scope、Acceptance、Authority 或计划变化必须增加 Revision 和 Amendment，记录旧值、新值、原因、依据和时间；禁止静默覆盖。

### 8.2 执行中记录：RunLedger

每个实际执行任务必须维护 `run.jsonl`。它只记录 Git 无法低成本、完整复原且对 Agent 复查有价值的事件：

- Run/Attempt 开始和结束；
- 改变仓库或外部系统状态的操作摘要；
- 失败、重试、阻断和回滚；
- 测试、构建、验证和发布检查；
- 外部副作用；
- 人工门禁和权威决定引用。

RunLedger 保存结构化摘要、时间、状态、结果码、Evidence 引用、副作用和脱敏说明；禁止默认保存完整命令输出、文件内容、凭据、Token 或其他敏感值。普通读取、目录查看和搜索不记录。Git Commit/Diff 作为变化证据引用，不要求在账本复制 Diff。

一个 Task 只使用一个 RunID。验证失败后必须先在当前 AttemptID 追加显式 `failure` 事件，再以未使用的 AttemptID 追加 `retry`；`retry` 一旦切换 AttemptID，禁止回填旧 Attempt。`run_finished` 后禁止追加事件。

### 8.3 任务终态：TaskOutcome

每个结束任务必须形成 `after.json`，至少包含：

- `Implemented / Deferred / Cancelled / Blocked / Superseded`；
- 已成立事实和实际变化；
- Verification 结果和 Evidence；
- 未完成或未验证事项；
- 遗留问题、原因、影响、Owner 和重新进入条件；
- 人类决定引用和下一任务；
- 终态 Artifact Manifest。

终态纠错禁止静默覆盖；必须增加 `revision` 和 `amendments[]`。TaskOutcome 不重复 TaskContract 中未变化的指令。

### 8.4 项目状态与唯一事实源

| 内容 | 唯一事实源 |
|---|---|
| 六类元类型、Task Profile 与 Artifact Manifest 术语 | VC-PPG-COM-001 |
| Profile 代码、状态、字段和实例动作 | VC-PPG-COM-002 |
| 137→6 映射 | VC-PPG-MAP-001 |
| 完整裁剪代数与优先级 | VC-PPG-DEC-001 |
| 受控值、22 源、17 标准、阶段和 Profile 覆盖机器表 | VC-PPG-TAIL-001 |
| 风险、Scope 和 Initiative | C02 |
| 专业触发和控制活动 | C01 至 C12、E01 至 E05 |
| 跨任务阶段顺序和路由 | VC-PPG-PRO-001 |
| Profile 主规范和消费方 | VC-PPG-IDX-001 |
| TaskContract/RunLedger/TaskOutcome Schema 与生成器 | `run-web-product-workflow`；不得重定义上述语义 |
| ProjectState | 仅由有效 TaskOutcome 和当前 AuthorityAsset 物化，禁止直接编辑 |

### 8.5 最低追踪关系

流程必须能够追踪：

```text
ProjectID / WorkItemID / TaskID
  → TaskContract / Task Profile
  → Scope / Requirement / Change 来源
  → Artifact Manifest
  → RunLedger / Git Change
  → Changed Asset
  → Verification / Validation Evidence
  → Acceptance / Gate / Release Decision
  → TaskOutcome / Follow-up
  → ProjectState
```

## 9. 生命周期或工作机制

### 9.1 统一八阶段主流程

| 阶段 | 进入条件 | 强制活动 | 最低退出条件 |
|---|---|---|---|
| S1 初次澄清 | 收到期望结果 | 检查仓库、文档、环境和 Baseline；只对会改变目标、Scope、Acceptance、风险或授权的未知执行 Grill Me；建立初步 TaskContract/Task Profile | 目标用户、问题、期望行为和完成判定可表达；安全、隐私、数据、不可逆性、生产影响、Authority 和其他阻断 Unknown 已逐项列出 |
| S2 二次确认 | 初步 Task Profile 可用 | 展示目标、范围、非目标、验收示例、风险、默认项；仅在仍存在推进选择时等待 `Proceed / Revise / Stop` | 人类已明确要求执行同一范围，或作出 `Proceed / Revise / Stop`；流程确认不替代正式 Gate |
| S3 条件深化 | `Proceed` 且专业触发成立 | 按任务类型深化产品、需求、验收、设计、扩展规范或影响分析 | 被触发规范的输入达到计划就绪；稳定资产已在 Artifact Manifest 中记录 `Reference`，不适用的正式类型已记录带规则依据的 `N/A` |
| S4 计划 | Scope 已固定到受控 Revision/Snapshot；Blocking Risk/Unknown 已处置；被触发设计输入达到所属规范的计划就绪条件 | 形成唯一执行计划；按 VC-PPG-TAIL-001 重新计算裁剪快照和阶段上下文；列步骤、目标、工具、路径、验证、回退、Stop 和 Gate；生产发布适用时固定 RBP、MAP Revision | `tailoring_resolution` 为 S4 或更晚、与 Task Profile/规则表哈希一致且无 blocker；计划可执行、可验证、可回退；所需事前批准可解析 |
| S5 执行 | TaskContract 已冻结；计划与权限有效；当前裁剪快照无 blocker | Agent 或人工实施按最小 RunLedger 执行；Git 保存代码/文档 Diff，RunLedger 保存变化摘要、失败、重试、验证、外部副作用和 Evidence 引用 | 计划动作完成或触发 Stop；Actual 与 Planned Change 已比较；账本顺序连续 |
| S6 验证与验收 | 实际变化和验证输入已固定 | 执行 Verification/Validation；生成 Evidence；由人类作 Acceptance | 验证结论可复核；验收结果已决定或明确 Pending/Blocked |
| S7 发布与观察 | Release/Deploy/Operations 适用，RBP/MAP 固定 Revision 已就绪，且所需 Gate 已满足 | 按批准 RBP 执行发布、观察、Stop、回滚或恢复，并处理指标和事件 | 发布决定、观察窗口、结果和回滚状态可解析；不适用时记录规则依据 |
| S8 收尾 | 当前交付不再继续执行 | 形成 TaskOutcome，更新终态 Artifact Manifest、Trace、Change、遗留问题和后继项；重建 ProjectState 和派生审核视图 | 结果为 Implemented、Deferred、Cancelled、Blocked 或 Superseded；事实、Owner、理由和 Evidence 完整 |

### 9.2 转换规则

1. S1 至 S8 顺序固定；阶段执行深度可以按 Task Profile 缩短，但阶段必须保留进入、活动、退出和缩短依据，不得倒置，也不得把产物实例动作写成阶段状态。
2. `Revise` 返回 S1 或 S3，取决于被修改的是目标/Scope 还是专业方案。
3. `Stop` 进入 S8，结果必须为 Cancelled、Blocked 或 Superseded，不得伪装为 Implemented。
4. S5 发现 Scope 扩大、权限不足、输入漂移或新 High/Critical Risk 时，必须停止受影响动作并返回 S3 或 S4。
5. S6 验证失败时不得进入已通过验收或已批准发布状态；必须修正、回滚、延期或取消。
6. S7 观察发现回归、Incident 或阈值失败时，必须执行回滚/恢复决策并创建相应事件记录。
7. 重新分类必须通过 TaskContract Amendment 更新 Task Profile、Artifact Manifest、影响分析和计划，不得只修改标签。

### 9.3 最小流程与完整流程

- 默认最小流程仍必须经过 S1、S2、S4、S6 和 S8。专业规范未触发时可以缩短 S3；没有执行动作时可以缩短 S5；没有发布或运行观察范围时可以缩短 S7。每个被缩短阶段仍必须在 TaskContract 或 TaskOutcome 记录适用性依据、活动事实和退出结论，相关 Profile 在 Artifact Manifest 中使用受控实例动作。
- 任何实际变更，无论由 Agent、自动化或人类实施，都必须经过 S4、S5、S6 和 S8，并保持同等的身份、权限、实际变化、失败、验证、Trace 和历史边界。Git 可承担 Diff 历史，RunLedger 不复制可低成本重建的信息。
- 任何生产发布必须经过 S4、S5、S6、S7 和 S8，并满足 E05、C11、C12。
- Emergency 可以先执行恢复服务或控制损害所必需的 S5 动作，但必须在恢复后补齐 S1 至 S4、S6 至 S8 的事实、决定和记录。
- 符合 VC-PPG-DEC-001 §16.4 全部资格条件的任务可以选择 Minimal 物理载体模式。S1/S2 摘要可与首次回复合并，三阶段逻辑对象聚合进 `task-record.json`，S4 计划、S5 重要变化、S6 验证和 S8 结果仍各自可解析。任何硬边界变化立即触发单向升级。

## 10. 强制规则

### 10.1 分类顺序

Agent 必须按以下顺序建立流程路由：

1. 判定 Delivery Scenario；
2. 判定一个或多个 Development Type，并标识主类型；
3. 判定 Change Surfaces；
4. 使用 C02 判定 Risk Level；
5. 逐项判定 E01 至 E05；
6. 逐项判定 VC-PPG-TAIL-001 的适用性事实；
7. 判定 Baseline Inheritance；
8. 判定 Normal/Emergency；
9. 按并集和最强控制规则生成 `tailoring_resolution`；
10. 生成 TaskContract，其中包含 Artifact Manifest；
11. 计算阶段深度和所需 Gate；
12. 分配 ProjectID、WorkItemID、TaskID、ordinal 和显式任务关系。

安全、隐私、数据、发布、不可逆性或 Authority 为 Unknown 时，不得默认为 Low、Inactive 或 N/A。

### 10.2 Delivery Scenario 路由

| 场景 | 强制关注点 | 默认流程影响 |
|---|---|---|
| DS-01 新产品 | Need、Evidence、Problem、Product Definition、Intent、Scope、PRD、Requirement、Acceptance、Design | S1 至 S4 必须完整深化；首次 Baseline 和发布按 C11/C12 控制 |
| DS-02 产品族/模板派生 | 来源 Baseline、继承边界、允许偏差、身份隔离、升级路径 | 先 Reference 模板，再只对偏差 Create/Revise；禁止复制后失去来源 |
| DS-03 现有产品演进 | 当前 Requirement/Baseline、影响范围、兼容、回归、变更记录 | 根据 DT-03 至 DT-09 裁剪；稳定内容 Reference |
| DS-04 运行中产品处置 | 生产影响、SLO、发布/回滚、Incident、观察和运营反馈 | 激活 E05；S7 适用性必须形成明确判定，相关 Profile 使用 `N/A` 时必须记录规则和 Scope；Emergency 适用时补齐事后控制 |

### 10.3 Development Type 总路由矩阵

| 类型 | 进入判定 | 必须深化的阶段 | 核心规范路由 | 默认产物策略 | 关键 Gate |
|---|---|---|---|---|---|
| DT-01 新产品 | 建立新的产品身份和产品边界 | S1、S3、S4、S6；发布时 S7 | C01–C06、C07–C12；按触发 E01–E05 | 新建产品意图、Scope、PRD、REQ、ACS、设计和验证策略 | 产品意图、Scope、需求/设计、验收、发布 |
| DT-02 产品族实例化 | 从批准模板或产品族派生独立实例 | S1、S3、S4、S6；发布时 S7 | C01–C12；按偏差和风险触发扩展 | Reference 来源 Baseline；只对实例差异 Create/Revise | 继承与偏差、实例验收、发布 |
| DT-03 新功能 | 新增用户或业务可感知能力 | S1、S3、S4、S6；发布时 S7 | C03–C06、C07–C12；产品服务对象、核心价值、系统边界或 Product Intent 变化时激活 C01；Initiative、Scope、Risk、Metric 或 Dependency 变化时激活 C02 | Create/Revise PRD/FTR/REQ/ACS 和受影响设计；稳定产品意图 Reference | Scope、Requirement、Design、Acceptance、Release |
| DT-04 需求澄清 | 不改变已批准义务，仅消除歧义或补充可理解性 | S1、S2、S4、S6、S8；发现需求质量、来源、冲突或下游理解缺口时执行 S3 | C02、C04、C05、C07–C12 | 保持 Requirement ID；按规则修订同一 Revision 链；无产品实施时 S5 记录 No Execution 事实 | Classification、Requirement Review；若行为变化必须重新分类 |
| DT-05 需求修订 | 改变已批准义务、范围、验收或产品行为 | S1、S3、S4、S6；发布时 S7 | C02–C12；Need、Problem、Product Definition 或 Intent 变化时激活 C01 | Revise 原资产；建立影响、Change、Decision、Trace 和新验证 | Change、Requirement、Acceptance、Release |
| DT-06 缺陷修复 | 实现或产物不符合现有批准 Requirement | S1、S4、S5、S6；发布时 S7 | C04、C05、C07–C12；按变更面触发 C06/E01–E05 | Reference 现有 PRD/REQ/ACS；记录缺陷来源、修复、CAS/CCS 和回归 Evidence | 缺陷分类、修复计划、Verification、Release |
| DT-07 工程变更 | 外部行为和验收不变的内部改进、重构或技术债处理 | S1、S4、S5、S6；发布时 S7 | C05–C12；按变更面触发 E01–E05 | 不创建产品 REQ；记录 Engineering Change 来源、影响、变化和回归 Evidence | 行为不变证明、Change、Verification、Release |
| DT-08 配置/内容变更 | 不改变 Requirement 的配置、策略参数或内容变化 | S1、S4、S5、S6；生产时 S7 | C05、C07–C12；按变更面触发 C06/E02–E05 | Reference 产品/需求 Baseline；记录受控配置、Diff、生效范围、验证和回退 | 配置边界、Change、Verification、Release |
| DT-09 迁移/替代/退役 | 资产、接口、数据、服务或能力迁移、被替代或停止使用 | S1、S3、S4、S5、S6、适用时 S7 | C04–C12；通常检查 E01、E03、E04、E05 | 建立 IMA、迁移/兼容/回滚计划、VRR/SRR、验证、通知和保留记录 | 影响、不可逆性、迁移、退役、发布/观察 |

### 10.4 DT-01 新产品流程

1. S1 必须确认目标用户、Need、Evidence、Problem、期望结果、护栏和非目标。
2. S3 必须建立或修订 C01、C02、C03、C04、C05、C06 所需资产，不得以一份摘要替代逻辑身份。
3. S4 必须覆盖架构、安全、数据、运营等触发判定及首次 Baseline 策略。
4. S6 必须同时验证 Requirement 符合性和 Need/Intent 有效性；Verification 不替代 Validation。
5. 涉及生产时，S7 必须建立发布、回滚、监控和观察范围。

### 10.5 DT-02 产品族实例化流程

1. S1 必须固定来源模板或产品族 Baseline、Revision/Snapshot 和允许继承范围。
2. S3 必须形成继承、覆盖、偏差和新实例身份的可追踪关系。
3. 稳定且未变化的产品、需求、设计和控制必须 `Reference`，不得复制成无来源新定义。
4. 偏差改变产品行为、Requirement 或风险时，必须按 DT-03、DT-05 或相应扩展规范处理。
5. 上游模板后续变化不得自动覆盖已发布实例；必须通过影响分析和 Change Decision。

### 10.6 DT-03 新功能流程

1. S1 必须确认用户可感知能力、使用场景、范围、非目标和验收示例。
2. S3 必须创建或修订 PRD Package、Feature、Requirement、Acceptance 和受影响设计。
3. 已批准产品意图完整覆盖该功能时 C01 使用 `Reference`；产品定位变化时重新激活 C01。
4. S6 必须覆盖主流程、替代流程、异常、权限、数据和回归。
5. 功能发布必须连接 Requirement、Design、Code/Config、Evidence 和 Release Configuration。

### 10.7 DT-04 需求澄清流程

1. S1 必须判定澄清是否改变规范性义务、范围、验收或外部承诺。
2. 不改变时保持原 Requirement ID，记录澄清依据和 Revision；不得创建平行 PRD。
3. 改变时必须重新分类为 DT-05；形成新能力时分类为 DT-03。
4. 纯澄清没有实际产品变化时，TaskOutcome 记录未执行产品变更的事实、检查方法和范围，S7 记录无发布或运行观察范围的规则依据；相关 Profile 按 Artifact Manifest 规则使用 `N/A`，S6 执行需求质量复核而非产品验收。

### 10.8 DT-05 需求修订流程

1. S1 必须识别原 Requirement、原 Revision/Baseline、变化原因和期望新义务。
2. S3 必须完成影响分析，并同步更新 PRD/Feature、Acceptance、Design、Trace 和受影响下游。
3. 已批准或基线化资产变化必须建立 CHG、IMA 和 CHD；Candidate 修订也必须保留来源和评审状态。
4. 旧 Revision 不得无痕覆盖；替代时保留有效边界和下游处理。
5. S6 必须验证新义务并执行回归；S7 必须处理兼容、通知、迁移和回滚。

### 10.9 DT-06 缺陷修复流程

1. S1 必须能够引用被违反的现有 Requirement Revision 和可复现的实际偏差。
2. 无有效 Requirement 时不得继续伪装为 Defect；必须转为 DT-03 或 DT-05。
3. S4 必须列复现、根因范围、修复边界、回归范围、回退和停止条件。
4. S5 必须记录实际修复、CAS；存在代码变化时生成 CCS。
5. S6 必须先证明缺陷不再复现，再证明相关 Requirement 未回归。
6. 生产缺陷发布和观察必须适用 E05；Incident 实际发生时按事件记录。

### 10.10 DT-07 工程变更流程

1. S1 必须明确外部行为、Requirement 和 Acceptance 保持不变的依据。
2. 无法证明行为不变时，必须转为 DT-03 或 DT-05。
3. S3 可以引用现有 PRD/REQ/Design；只对技术设计或架构变化 Create/Revise。
4. S4 必须列技术目标、受影响组件、兼容、性能、迁移、回退和回归策略。
5. S6 必须验证行为不变和技术目标达成；仅通过单元测试不足以证明外部行为未变。

### 10.11 DT-08 配置或内容变更流程

1. S1 必须固定配置项、原值/内容、目标值/内容、环境、生效范围和 Owner。
2. 配置或内容改变产品义务、权限、隐私、安全、数据处理或用户可感知行为时，必须叠加或转为 DT-03/DT-05 并激活相应扩展规范。
3. S4 必须包含验证、预览或 Dry Run、回退值、传播延迟和缓存/副本一致性检查。
4. S5 必须记录实际 Diff、操作者、环境和生效时间；控制台和 Feature Flag 变化同样受控。
5. S6/S7 必须验证目标环境实际生效、无越权传播且可回退。

### 10.12 DT-09 迁移、替代或退役流程

1. S1 必须识别当前资产、消费方、接口、数据、外部承诺、保留和恢复需求。
2. S3 必须建立影响分析、目标状态、兼容窗口、迁移步骤、通知、回滚或补偿策略。
3. 不可逆删除、Schema/Data 迁移、密钥轮换和服务退役必须单独确认 Authority 和剩余风险。
4. S5 必须按批次、检查点和停止条件执行；失败不得删除旧身份、Snapshot 或 Evidence。
5. S6 必须验证完整性、兼容性、消费方切换、数据一致性和恢复可行性。
6. S7/S8 必须记录 SRR、有效时间、保留位置、未迁移消费方和后继支持窗口。

### 10.13 多类型组合规则

1. 一个 Task Profile 可以包含多个 Development Type，但必须标识主类型，并在 `development_type_scopes` 中为每个类型绑定非空子范围和事实依据。
2. 同一 Scope、同一 Authority、同一发布边界且步骤强耦合时可以共用一个流程载体。
3. 目标、Owner、Authority、风险接受、发布窗口或回滚边界独立时必须拆分任务并建立依赖。
4. 组合任务执行所有被触发规则的并集；不得选择控制更少的类型覆盖另一类型。
5. 发现 Requirement Gap 的 DT-06 必须拆出或重新分类 DT-03/DT-05；缺陷事实与需求修订保持独立身份。
6. DT-09 与其他类型组合时，迁移、替代、退役控制不得被新功能或工程变更流程吸收。
7. DT-03/DT-07、DT-03/DT-08、DT-04/DT-05、DT-05/DT-07、DT-05/DT-08 同时出现时必须使用不同子范围；共享同一子范围表示分类自相矛盾，S4 不得就绪。子范围必须精确引用 `scope.in_scope` 的完整值；文本不同但业务含义重叠时，独立 Review 或人类 Gate 必须要求拆分或重分类。

### 10.14 Change Surface 与扩展规范

| Change Surface 或事实 | 必须检查的规范 |
|---|---|
| UI/UX | C06；需要视觉决策时才生成 HTML/PNG |
| API/Integration | C06 IFC；涉及多系统、多仓库、架构迁移、关键质量属性或架构一致性时按 E01 触发条件检查并判定 |
| Data/Schema、AI/Data Governance | C06、E03；不可逆影响进入 C11/C12 |
| Identity/Security/Privacy | C06、E02；Unknown 不得判为未激活 |
| Architecture/Multi-repo | E01；检查架构 Decision、迁移和一致性 |
| Deploy/Operations | E05；检查发布、回滚、监控和观察 |
| Agent/Collaboration | C07、C08、C09；权限扩大必须人类确认 |
| 正式知识、记录、保留或处置 | E04 |

### 10.15 Baseline 继承规则

1. `New`：不存在可覆盖当前 Scope 的有效 Baseline，创建新资产和首次 Revision。
2. `Reference`：有效 Baseline 完整覆盖且内容未变化，固定 Asset ID、Revision/Snapshot 和范围。
3. `Revise`：保持资产身份并建立新 Revision、影响和历史。
4. `Supersede`：旧身份保留，记录替代对象、有效边界、迁移和通知。
5. Approved Baseline 禁止原位编辑；Candidate 也必须保留修订来源和评审状态。

### 10.16 Artifact Manifest 规则

1. `Create/Revise` 只用于本任务实际创建或修订的权威实例。
2. `Reference` 必须解析到固定 Revision/Snapshot 和有效范围。
3. `Generate` 只用于可从权威事实重建的矩阵、报告或查询视图。
4. `On Event` 只在 Failure、Incident、Waiver、Risk Acceptance、Release 等事实发生后创建。
5. `N/A` 必须记录规则和范围；Risk 为 High/Critical，或安全、隐私、数据、不可逆性、生产影响、Extension Trigger、Authority 任一项为 Unknown 时禁止使用。
6. Artifact Manifest 不复制全量 137 项 Profile；未列项必须能通过 VC-PPG-IDX-001 和 VC-PPG-MAP-001 解析。
7. 执行前 Manifest 位于 `before.json`；执行结束后实际动作和结果写入 `after.json`，禁止单独维护第三份 Manifest 文件。
8. 终态 Manifest 不得删除执行前计划项，也不得改写其计划字段；只在原项上增加 Outcome。
9. 终态 Manifest 可追加收尾时实际发生的资产，追加项的 Outcome 只能是 `Created / Revised / Referenced / Generated`；TaskOutcome 建立后的追加必须通过 Amendment 记录。

### 10.17 Emergency 叠加规则

1. Emergency 不改变 Development Type。
2. 只有延迟会扩大现实损害且存在 Emergency Authority 时，才允许先执行恢复或控制损害动作。
3. 必须保留原状态、重要操作摘要、时间线、Evidence、权限、变更、验证和回滚边界；原始命令仅在复核无法通过其他证据完成时受控保存。
4. 恢复后必须补齐 TaskContract、Emergency CHG ID、最低 Impact/Risk、RunLedger、TaskOutcome、Verification、Trace，以及 C11 在适用 Policy 时限内要求补齐的 IMA、CHD、VRR、SNP、CIR、BSL 或 RLC Profile。

### 10.18 确定性裁剪解析

1. VC-PPG-TAIL-001 是受控值和完整路由的唯一机器表；流程实现不得复制第二张手工路由表。
2. Always、DS、全部 DT、全部 Surface、Risk、Extension、Fact、Baseline 和 Mode 取并集，执行最强控制；Stage 只决定当前加载范围。
3. TaskContract 必须保存规则表 ID、Version、Status、SHA-256、Task Profile 输入摘要、适用/待判定规范、阶段规范、控制强度、阻断原因、规则 ID、优先源章节、完整命中源及逐文件 SHA-256 和 Profile 覆盖摘要。
4. 规则表、Task Profile、Source Snapshot 或本规范变化后，旧裁剪快照失效；必须通过 Amendment 重新计算。
5. S4 起存在 Unknown、Blocking Open Question、`blocked_by`、Low Confidence、扩展冲突、权限不足、规则缺失或过期快照时，`run_started` 必须被拒绝。
6. 编译后的小型 Norm Packet 是非穷尽导航 DerivedView；同步生成的 Complete Norm Source Pack 必须包含治理源、索引、已适用和待判定标准的完整原文。Agent 在物质动作前用导航和搜索只读取相关段落；无法可靠缩小时必须读取完整命中源，不得将未出现在控制卡中解释为 N/A。
7. `authority_available=Yes` 必须具有 Authority 引用，且每个引用必须绑定结构化 `authority_assessments`。只有所有评估状态均为 `Valid`、验证时间不在未来、未过期、Evidence 非空且作用域精确覆盖全部 `scope.in_scope` 才允许 S4 就绪。`execution_permissions` 只使用 `read / edit-in-scope / validate / external-effect / rollback`；Fact 触发所需权限必须在 S4 齐备，每个 Run Event 还必须在写入时再校验对应权限。High/Critical 必须计划 `independent-review`，Critical 还必须计划 `human-acceptance`；安全/隐私、生产发布和不可逆变化分别要求 `security-privacy-review`、`release-approval` 和 `irreversible-change-approval`。
8. Applicability Fact 与 Development Type/Change Surface 必须通过 VC-PPG-TAIL-001 一致性检查；不一致时不得凭 Primary Type 或较弱标签继续。
9. `required_gates` 表示计划的转换控制，不表示 Gate 已通过。执行受保护转换前，必须从对应 Authority 事实源读取并验证 Gate Outcome。
5. 所有 Emergency 实施后必须执行 C12 `Post-implementation Review` 类型的正式 Review 并形成 RVR；只有 E05 已激活且实际发生生产发布或部署时，才同时触发 E05 PRR。
6. Agent 不得以 Emergency 自批发布、风险接受、Waiver 或 Baseline。

## 11. 受控状态

### 11.1 流程阶段状态

流程阶段值固定为：

- `S1 Clarifying`
- `S2 Awaiting Confirmation`
- `S3 Deepening`
- `S4 Planning`
- `S5 Executing`
- `S6 Verifying/Accepting`
- `S7 Releasing/Observing`
- `S8 Closing`

这些值只表示流程位置，不是 DOC、CASE、EXEC、EVID、DEC 或 REC State。

### 11.2 流程结果

流程结果只使用：

| 结果 | 判定条件 |
|---|---|
| `Implemented` | 当前声明交付已完成并形成要求的受控输出；可以是产品变化，也可以是正式评审、分析或报告，不表示资产已批准或发布 |
| `Deferred` | 已决定推迟当前交付，且后继条件、Owner 和恢复入口已记录 |
| `Cancelled` | 已决定终止且不再继续当前交付，原因、影响和已产生事实已记录 |
| `Blocked` | 阻断条件尚未解除，Owner、解除条件和受影响范围已记录 |
| `Superseded` | 当前任务被明确的后继任务或决定替代，替代对象和有效边界已记录 |

流程结果不得替代 CHG、REQ、RVR、GTE、BSL 或其他领域 Profile 状态，也不得替代 AuthorityAsset 的批准状态。

### 11.3 人类确认结果

存在未决推进选择时，二次确认只使用 `Proceed / Revise / Stop`。用户已明确要求执行且目标、Scope、Acceptance、风险和授权无歧义时，不重复询问 `Proceed`，直接记录原指令引用。两种方式都只控制当前声明范围的流程推进，不自动构成资产 Approval、Gate Approval、Risk Acceptance、Release Decision 或 Baseline Decision。

## 12. 最小物理产物与条件 Profile

### 12.1 所有任务的最低集合

所有任务必须按生命周期解析以下内容：

| 阶段 | 必需元类型/载体 | 最低内容 |
|---|---|---|
| 执行前 | TaskContract / `before.json` | 身份链、任务关系、目标、Scope、权限、Task Profile、Artifact Manifest、Acceptance、计划、验证、回退、Gate、Source Snapshot |
| 执行中 | RunLedger / `run.jsonl` | RunID、AttemptID、顺序、重要事件、失败/重试、验证、外部副作用、Evidence 和 Git 引用；无执行动作时允许空账本 |
| 任务终态 | TaskOutcome / `after.json` | 结果、已成立事实、实际变化、验证、未完成项、遗留问题、决定、Evidence、后继任务、终态 Manifest |
| 跨任务消费 | ProjectState / `project-state.json` | 从有效 TaskOutcome 与 AuthorityAsset 自动物化的当前事实、遗留项和任务图 |

Task Profile 和 Artifact Manifest 是 TaskContract/TaskOutcome 字段，不再是独立物理产物。长期需求、设计、决定、证据和基线按触发条件保存为 AuthorityAsset；审核报告、矩阵和索引保存为 DerivedView。

满足 VC-PPG-DEC-001 §16.4 时，前三行逻辑对象可以聚合到单一 `task-record.json`；字段子集必须与 TaskContract、RunLedger、TaskOutcome 语义兼容。该聚合载体不是新元类型，也不改变 ProjectState 的消费规则。

### 12.2 条件产物

下表只汇总跨任务高频触发，不是 137 个领域 Profile 的第二套目录。未列 Profile 必须通过 VC-PPG-IDX-001、VC-PPG-MAP-001 和所属专业规范解析；专业触发一旦成立，即使本表未单列也必须进入 Artifact Manifest。

| 触发条件 | 条件产物或记录 |
|---|---|
| 新产品、新功能、行为性需求修订 | C01/C03/C04/C05/C06 对应资产 |
| 计划 Agent Run | TaskContract 引用 SCM、CPP、CSR 等稳定 AuthorityAsset；ECP/AEP 语义写入 `before.json`；发现 Context Conflict 时建立 CCF Profile |
| 实际 Tool Invocation | 普通读取和搜索不记录；变更、失败、重试、验证、外部副作用、人工门禁和回滚追加到 RunLedger；超时、取消、非零退出、未知状态和部分返回不得省略 |
| Agent Run 产生变化、运行结果或质量主张 | Git 保存 Diff；RunLedger 保存必要事件；TaskOutcome 保存 CAS/CCS/FER 语义；需要审核时从 RunLedger、VER/VAE 和 Git 引用生成 VDR |
| 实际人工或自动化实施 | C11 CHG/IMA/CHD 和同结构 RunLedger；记录 Implementer、Authority、Actual Change、失败、验证和 Trace；禁止要求复制全部终端输出 |
| 已批准/基线资产变化 | CHG、IMA、CHD、VRR/SNP |
| 实际 Verification/Validation | 创建 VER/VAE；Gate、审计或覆盖查询需要时从权威 Evidence 生成 VCM 等派生视图 |
| 实际 Failure/Exception | FER |
| 受控资产变化、正式交付、高风险或外部影响需要复核 | HRR；存在未消除 Risk、限制、未验证项或临时控制时创建 RRS |
| 实际评审或 Gate | RVR/GTE |
| 计划生产发布或 Deploy/Operations 触发 | 在 Release Ready 前创建、修订或引用固定 Revision 的 RBP、MAP |
| 实际发布或部署 | RLC；实际运行观察建立 OPO；发布后评审事件触发时建立 PRR |
| 实际 Incident/Problem | INR/PBR 和相关 Evidence |
| 实际替代或退役 | RSP/SRR、迁移与通知记录 |
| 实际剩余风险需要接受决定 | RAR；只能由具有 Authority 的人类决定，不得用 RAR 改写 RRS 或 Risk Register 的事实 |

事件未发生时禁止预建空 Profile 实例。空 `run.jsonl`只表示尚无执行事件，不表示已经执行。`On Event` 只表示事件实际发生后创建，不表示可以省略专业规范规定的事件触发。

## 13. 三阶段记录必填信息

### 13.1 TaskContract / before.json

TaskContract 至少包含：

- ProjectID、WorkItemID、TaskID、ordinal；
- depends_on、supersedes、blocked_by；
- 期望结果、In Scope、Out of Scope；
- Delivery Scenario；
- Development Types、主类型和组合依据；
- Change Surfaces；
- Risk Level 和来源；
- E01 至 E05 状态；
- Baseline Inheritance；
- Execution Mode；
- Artifact Manifest；
- 唯一执行计划、验证、回退、Stop Condition；
- 人类确认、Authority 和 Pending Gate；
- Source Snapshot、置信度和未决问题；
- Revision、lifecycle_state、frozen_at 和 amendments。

### 13.2 单项路由决定

每项 `Create/Revise`、`Reference`、`Generate`、`On Event` 或 `N/A` 必须记录：

- Meta Type；
- Legacy Kind/Profile（适用时）；
- 动作；
- 规则引用；
- 事实依据；
- Owner；
- Source Asset/Revision/Snapshot；
- 目标载体或生成规则；
- 未决问题；
- 需要的人类决定。

### 13.3 RunLedger / run.jsonl

每个被记录事件必须包含：

- EventID、RunID、AttemptID、连续 Sequence 和时间；
- event_type、结构化摘要和结果状态；
- 适用的 exit_code、Evidence/Git 引用和外部副作用；
- 已执行的敏感信息脱敏说明。

RunLedger 禁止默认保存完整命令、完整输出、文件正文、Token、凭据或其他敏感值。需要保留原始日志时只保存受控 Evidence 引用。

### 13.4 TaskOutcome / after.json

TaskOutcome 至少包含：

- TaskID、Revision、终态和完成时间；
- 已成立事实、实际变化和 Verification；
- 未完成或未验证事项；
- 遗留问题的原因、影响、Owner 和重新进入条件；
- 决定、Evidence、后继 TaskID；
- 终态 Artifact Manifest 和 amendments。

### 13.5 ProjectState / project-state.json

ProjectState 必须包含 Source Digest、来源 TaskOutcome、当前事实、遗留项、任务图和 AuthorityAsset 索引；必须由生成器重建，禁止直接编辑。

## 14. 质量准则

一个流程路由只有同时满足以下条件才可接受：

1. **分类正确**：Task Profile 维度完整且有事实依据；
2. **覆盖完整**：所有触发的专业规范、风险和扩展均进入路线；
3. **裁剪有据**：每个缩短、Reference 或 N/A 都有规则和范围；
4. **单一事实源**：本规范不复制专业字段、状态或类型定义；
5. **可执行**：计划具有动作、目标、工具、顺序、验证、回退和停止条件；
6. **可验证**：Acceptance 与 Evidence 可观察、可复核并固定环境/版本；
7. **权限明确**：Agent、人类、专业 Owner、Gate、发布和风险接受边界可解析；
8. **可追踪**：目标、来源、变化、Evidence、决定和结果形成闭环；
9. **可恢复**：变更、迁移和发布满足 C02 Risk Level 及所属专业规范规定的最低回退、恢复或补偿要求；
10. **历史完整**：失败、拒绝、替代、旧 Revision 和重新分类不被无痕覆盖；
11. **无重复流程**：团队工作流和 Skill 引用本规范，不维护冲突矩阵；
12. **可审计**：独立 Reviewer 能根据文件和 Evidence 重建路由结论。

## 15. 验证与符合性检查

### 15.1 流程就绪检查

进入 S4 前必须确认：

- TaskContract 与其中的 Task Profile 完整；
- `Proceed` 已记录；
- Scope、非目标和 Acceptance 可解析；
- Blocking Risk、Unknown、Dependency 和 Extension Trigger 已处置，或已记录 Owner、处置条件和期限；
- 必需专业深化已完成；
- TaskContract 中的 Artifact Manifest 无无据 N/A；
- 人类 Gate 和 Authority 可解析。

### 15.2 执行就绪检查

进入 S5 前必须确认：

- 唯一执行计划已固定；
- 输入 Snapshot 和目标路径可解析；
- 允许动作、工具、命令、环境和权限明确；
- 验证、回退、监视和 Stop 可执行；
- TaskContract、C11 或所属专业规范触发的 CHG/IMA/CHD 和专业批准当前有效；
- Blocking Risk、Unknown 和依赖已处置。

### 15.3 验收就绪检查

作出 Acceptance 前必须确认：

- Actual Change 与 Planned Change 已比较；
- 验证输入、环境和版本固定；
- Acceptance、Non-regression、兼容、迁移和回退验证完整；
- Failure、Exception 和剩余风险已披露；
- Evidence 可访问且来源可核验；
- Acceptance Authority 明确。

### 15.4 强制阻断

出现以下任一情形必须停止受影响动作：

1. 无法确定目标、Scope 或 Development Type；
2. 安全、隐私、数据、不可逆性、生产影响或 Authority 中任一阻断项为 Unknown；
3. Agent 试图自批或扩大授权范围；
4. Approved/Baselined 资产变化无适用 Change Control；
5. 输入 Snapshot 失效、冲突或完整性失败；
6. 实际变化超出计划、Scope 或权限；
7. 验证失败但流程试图进入通过、发布或关闭；
8. DT-06 无法引用被违反的 Requirement；
9. DT-07/DT-08 实际改变外部行为但未重新分类；
10. DT-09 不可逆变化无迁移、补偿、保留或有权决定；
11. DS-04 发布、回滚或风险接受无人类 Authority；
12. 本规范与专业规范发生未解决冲突。

### 15.5 自动检查

自动检查至少覆盖：

- 4 个 Delivery Scenario 和 9 个 Development Type 均有唯一入口；
- 八阶段名称、顺序和转换规则完整；
- 五类实例动作值合法；
- Risk 只使用 C02 的四级值；
- E01 至 E05 均有触发判定；
- 正式元类型严格为 6 类；137 个兼容 Profile 全部唯一映射，覆盖 137/137；
- C01 至 C12、E01 至 E05 编号未变化；
- 无第七个元类型、第二套 Profile 目录或平行状态模型；
- 注册表、蓝图、来源映射和 Skill 引用一致；
- Candidate/In Review/Proposed 未被写成 Approved。

## 16. 追踪与记录要求

1. 本规范所有修订必须通过 CHG、IMA、CHD、VRR/SNP 和适用 RVR 管理。
2. 流程路由变更必须记录受影响任务类型、阶段、产物、Gate、Skill 和消费方。
3. 单项规范第 17 章继续拥有专业触发和不可裁剪控制，本规范只引用并编排。
4. 当专业规范增加、删除或修改触发条件时，必须检查本规范路由矩阵是否需要修订。
5. 当本规范变化时，必须检查 BP-001、BP-002、VC-PPG-DEC-001、Skill 和注册表。
6. 派生流程图、检查表和团队工作流必须记录本规范 Revision/Snapshot。
7. 失败检查、Rejected Decision 和旧流程 Revision 必须保留。

## 17. 裁剪规则

### 17.1 不可裁剪项

任何任务均不得裁剪：

- TaskContract、Task Profile 与事实依据；
- VC-PPG-TAIL-001 的全部适用性事实和当前裁剪快照；
- 最小 Scope 和 Agent Modification Boundary；
- 可验证的期望结果；
- C02 Risk 判定；
- E01 至 E05 逐项判定；
- TaskContract/TaskOutcome 中的 Artifact Manifest；
- 人类 Authority 和 Gate 边界；
- 实际变化、重要运行事件、失败和 Evidence；
- 最小 Trace、Revision 和历史；
- 最终结果、Owner 和未决问题。

不可裁剪的是控制目标、判定和证据，不是全文上下文、独立文件或重复说明。

### 17.2 可以缩放项

可以按 Task Profile 缩放：

- 物理文件或页面数量；
- 说明深度；
- 示例数量；
- 派生矩阵和报告的生成时机；
- 评审范围和参与者数量，但不得违反独立性和 Authority；
- 稳定 Baseline 的重复说明；
- 未触发专业模板的实例数量。
- 满足 VC-PPG-DEC-001 §16.4 时，TaskContract、RunLedger 和 TaskOutcome 的物理文件数量可缩为一个聚合载体，并跳过不产生 Authority 结论的 Shadow 检索派生物；控制目标、事实、验证、历史和升级检查不得删除。

### 17.3 禁止裁剪方式

禁止：

- 用“小任务”删除风险、验证、追踪或人类决定；
- 用一页 PRD 替代独立逻辑资产身份；
- 用聊天、工单或工具成功替代正式 Evidence 和 Decision；Git 可以作为代码/文档 Diff 证据，但不能替代外部副作用、失败、验证环境、Approval 或 Decision 记录；
- 为完整性预建空 Failure、Incident、Waiver 或 Risk Acceptance；
- 把 `Reference` 写成已重新批准；
- 把未判定扩展触发写成 Inactive；
- 用 Stage、Primary Development Type、Reference、Emergency 或物理载体选择删除已适用控制；
- 在规则缺项、哈希变化、Unknown 或同级冲突时凭经验继续执行；
- 为流程便利新建第二套任务等级、风险等级、状态或产物动作。

## 18. 扩展接口

| 规范 | 本规范的调用方式 | 本规范不得替代的内容 |
|---|---|---|
| C01 | 新产品或产品意图变化时深化 S1/S3 | Need、Evidence、Problem、Intent 规则 |
| C02 | 所有任务建立最小 Scope/Risk | 风险等级、Initiative 和 Scope 规则 |
| C03 | DT-01/02/03 和行为性 DT-05 激活 PRD/Feature | PRD 与 Feature 定义 |
| C04 | Requirement 新增、澄清、修订、缺陷分类和替代 | Requirement 身份、分类和演进 |
| C05 | 任何可观察变化或缺陷状态变化建立验证/验收 | Acceptance、Verification、Validation |
| C06 | 按 Change Surface 激活设计 | UX、技术、接口、数据和权限设计 |
| C07 | 所有任务解析角色、权限、Stop 和 Escalation | Authority 和 Approval Protocol |
| C08 | TaskContract 引用稳定上下文并承载 ECP 兼容语义 | Context 优先级、新鲜度和冲突 |
| C09 | 实际执行使用 RunLedger、TaskOutcome 和 Evidence | 重要运行事件、变化和失败记录 |
| C10 | 建立最小 Trace；Gate、审计、影响查询或覆盖查询触发时生成覆盖和血缘视图 | 关系语义、Decision 和 Lineage |
| C11 | 管理身份、Revision、Baseline、Change、人工等价受控 Run 和 Release Configuration | 配置与变更状态、批准和记录 |
| C12 | 按生命周期、风险和发布范围触发 Gate | Gate、Waiver、Risk Acceptance 和健康 |
| E01–E05 | 按 Task Profile 与 VC-PPG-TAIL-001 逐项激活或保持待判定 | 专业扩展触发、控制和 Evidence |

团队工作流和 Skill 必须以本规范为跨任务阶段顺序和路由的唯一来源；交互文案、页面、自动化和物理载体可以变化。

## 19. 参考标准

本规范继承上位蓝图已登记的标准版本和引用等级，只映射公开生命周期与治理主题，不声称未核验的逐条符合性：

| 标准 | 映射主题 | 本规范位置 |
|---|---|---|
| ISO/IEC/IEEE 12207:2026 | 软件生命周期过程、实施、验证、运行与维护 | 第 9、10、15、18 章 |
| ISO/IEC/IEEE 29148:2018 | 需求定义、分析、验证、确认和变更 | 第 10.6 至 10.12、15 章 |
| ISO 10007:2017 | 配置标识、变更控制、状态记账和审核 | 第 10.15、16、18 章 |
| IEEE 1012-2024 | Verification and Validation 的独立判定与 Evidence | 第 9.1、10、15 章 |
| ISO 31000:2018 | 风险识别、处置、监视和决策边界 | 第 8、10.1、15 章 |
| ISO/IEC/IEEE 42010:2022 | 架构 Concern、View、Decision 和演进 | 第 10.14、18 章 |
| ISO/IEC 20000-1:2018 | 服务变更、发布、事件、问题和持续改进 | 第 9.3、10.2、10.17、18 章 |
| ISO 15489-1:2016 | 记录真实性、完整性、保留和可访问性 | 第 11、13、16 章 |
| ISO/IEC 42001:2023 | AI 管理、风险、运行控制和持续改进 | 第 7、10.14、15 章 |
| RFC 2119 / RFC 8174 | 规范性关键词 | 第 5 章 |

正式条款符合性必须使用合法取得的完整标准文本和独立评审；本表不替代逐条符合性证据。

## 20. 附录：模板骨架、检查清单与示例

### 20.1 TaskContract 最小结构

```json
{
  "schema_version": "6.3-candidate",
  "meta_type": "TaskContract",
  "project_id": "P-001",
  "work_item_id": "W-001",
  "task_id": "T-001",
  "ordinal": 1,
  "revision": 1,
  "lifecycle_state": "Ready",
  "created_at": "2026-08-15T00:00:00Z",
  "frozen_at": null,
  "depends_on": [],
  "supersedes": [],
  "blocked_by": [],
  "source_snapshot": {"snapshot": "<source-snapshot>"},
  "objective": "<期望结果>",
  "scope": {"in_scope": ["<scope>"], "out_of_scope": [], "allowed_paths": [], "forbidden_actions": []},
  "authority": {
    "execution_permissions": ["read", "edit-in-scope", "validate"], "required_gates": [], "stop_conditions": ["scope-expansion"],
    "authority_references": ["user:task-directive"],
    "authority_assessments": [{"reference": "user:task-directive", "source_kind": "UserDirective", "status": "Valid", "scope_refs": ["<scope>"], "evidence_refs": ["conversation:<task-id>:user-directive"], "verified_at": "2026-08-15T00:00:00Z", "expires_at": null}]
  },
  "acceptance": {"criteria": ["<criterion>"], "decision_owner": "task-initiator"},
  "plan": {"steps": ["inspect", "execute", "verify", "close"], "verification": ["<check>"], "rollback": ["<rollback>" ]},
  "task_profile": {
    "delivery_scenario": "DS-03",
    "development_types": ["DT-06"],
    "primary_development_type": "DT-06",
    "development_type_scopes": {"DT-06": ["defect correction scope"]},
    "change_surfaces": ["Agent/Collaboration"],
    "risk_level": "Medium",
    "extension_triggers": {"E01": "Inactive", "E02": "Inactive", "E03": "Inactive", "E04": "Inactive", "E05": "Inactive"},
    "extension_evidence_refs": {"E01": [], "E02": [], "E03": [], "E04": [], "E05": []},
    "baseline_inheritance": ["Revise"],
    "mode": "Normal",
    "confidence": "Medium",
    "basis": ["<basis>"],
    "open_questions": [],
    "applicability_facts": {
      "product_intent_change": "No", "initiative_scope_change": "No", "requirement_change": "No", "external_behavior_change": "No", "design_change": "No",
      "architecture_impact": "No", "security_privacy_impact": "No", "data_ai_impact": "No", "formal_knowledge_records": "No", "operations_impact": "No",
      "production_release": "No", "irreversible_change": "No", "actual_execution": "Yes", "authority_available": "Yes", "migration_retirement": "No",
      "external_system_effect": "No", "formal_review_or_gate": "Yes"
    }
  },
  "tailoring_resolution": {
    "rule_set_id": "VC-PPG-TAIL-001", "rule_set_version": "6.3 Candidate", "rule_set_status": "In Review",
    "rule_set_sha256": "<64-char-sha256>", "normative_sources_sha256": "<64-char-sha256>", "resolver_sha256": "<64-char-sha256>", "task_contract_schema_sha256": "<64-char-sha256>", "input_digest": "<64-char-sha256>", "stage": "S4",
    "applicable_standards": ["C02", "C04", "C05", "C07", "C08", "C09", "C10", "C11", "C12"],
    "pending_standards": [], "stage_context_standards": ["C02", "C05", "C07", "C08", "C09", "C10", "C11", "C12"],
    "control_strength": "standard", "independent_review": false, "explicit_human_gate": false, "blocking_reasons": [],
    "rule_ids": ["VC-PPG-TAIL-001:always_applicable"], "source_sections": [{"source_id": "VC-PPG-DEC-001", "path": "references/01_治理基线/Vibe_Coding_P2裁剪与扩展规范适用性决议_V6.3.md", "sections": ["9", "10", "11", "12", "13", "14", "15", "16", "17"]}],
    "complete_source_files": [
      {"source_id": "VC-PPG-COM-001", "path": "references/01_治理基线/Vibe_Coding_公共术语与规范性用语基线_V6.3.md", "sha256": "<64-char-sha256>"},
      {"source_id": "VC-PPG-COM-002", "path": "references/01_治理基线/Vibe_Coding_受控产物目录与状态模型_V6.3.md", "sha256": "<64-char-sha256>"},
      {"source_id": "VC-PPG-DEC-001", "path": "references/01_治理基线/Vibe_Coding_P2裁剪与扩展规范适用性决议_V6.3.md", "sha256": "<64-char-sha256>"},
      {"source_id": "VC-PPG-PRO-001", "path": "references/01_治理基线/Vibe_Coding_任务类型裁剪与统一执行流程规范_V6.3.md", "sha256": "<64-char-sha256>"},
      {"source_id": "VC-PPG-IDX-001", "path": "references/05_记录与登记册/V6.3_跨规范产物归属索引.md", "sha256": "<64-char-sha256>"}
    ],
    "profile_coverage_digest": {"applicable": 0, "total": 137, "sha256": "<64-char-sha256>"}
  },
  "artifact_manifest": [
    {"meta_type": "TaskContract", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-before", "content_ref": ".project-governance/tasks/T-001/before.json", "reason": "freeze execution input", "rule_reference": "VC-PPG-PRO-001 §8.1", "owner": "task-initiator", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": []},
    {"meta_type": "RunLedger", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-run", "content_ref": ".project-governance/tasks/T-001/run.jsonl", "reason": "record material execution events", "rule_reference": "VC-PPG-PRO-001 §8.2", "owner": "execution-agent", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": []},
    {"meta_type": "TaskOutcome", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-after", "content_ref": ".project-governance/tasks/T-001/after.json", "reason": "record terminal facts and residue", "rule_reference": "VC-PPG-PRO-001 §8.3", "owner": "task-initiator", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": []}
  ],
  "amendments": []
}
```

### 20.2 RunLedger 事件结构

```json
{
  "schema_version": "6.3-candidate",
  "meta_type": "RunLedger",
  "event_id": "RUN-001-E0001",
  "project_id": "P-001",
  "task_id": "T-001",
  "run_id": "RUN-001",
  "attempt_id": "A-001",
  "sequence": 1,
  "timestamp": "2026-08-15T00:00:00Z",
  "event_type": "run_started",
  "summary": "<脱敏摘要>",
  "status": "started",
  "exit_code": null,
  "evidence_refs": [],
  "side_effects": [],
  "redactions": []
}
```

### 20.3 TaskOutcome 最小结构

```json
{
  "schema_version": "6.3-candidate",
  "meta_type": "TaskOutcome",
  "project_id": "P-001",
  "work_item_id": "W-001",
  "task_id": "T-001",
  "revision": 1,
  "status": "Implemented",
  "completed_at": "2026-08-15T00:00:00Z",
  "source_snapshot": {"snapshot": "<result-snapshot>"},
  "established_facts": ["<established-fact>"],
  "actual_changes": ["<actual-change>"],
  "verification": [{"summary": "<check>", "result": "Passed", "evidence_refs": ["<evidence-ref>"], "required": true}],
  "incomplete_items": [],
  "legacy_issues": [],
  "decisions": [],
  "evidence_refs": [],
  "next_tasks": [],
  "artifact_manifest": [
    {"meta_type": "TaskContract", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-before", "content_ref": ".project-governance/tasks/T-001/before.json", "reason": "freeze execution input", "rule_reference": "VC-PPG-PRO-001 §8.1", "owner": "task-initiator", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": [], "outcome": "Revised"},
    {"meta_type": "RunLedger", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-run", "content_ref": ".project-governance/tasks/T-001/run.jsonl", "reason": "record material execution events", "rule_reference": "VC-PPG-PRO-001 §8.2", "owner": "execution-agent", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": [], "outcome": "Revised"},
    {"meta_type": "TaskOutcome", "legacy_kind": null, "action": "Create/Revise", "asset_id": "T-001-after", "content_ref": ".project-governance/tasks/T-001/after.json", "reason": "record terminal facts and residue", "rule_reference": "VC-PPG-PRO-001 §8.3", "owner": "task-initiator", "source_snapshot": "<source-snapshot>", "human_confirmation_refs": [], "outcome": "Created"}
  ],
  "amendments": []
}
```

完整字段以 `run-web-product-workflow/schemas/` 为准；模板不得替代 Schema。

### 20.4 阶段检查模板

```text
Stage:
Entry Criteria:
Inputs and Revisions:
Activities:
Outputs and Evidence:
Exceptions / Retries:
Exit Criteria:
Human Decision:
Next Stage:
```

### 20.5 九类任务快速检查

| 类型 | 不得遗漏 | 禁止误用 |
|---|---|---|
| DT-01 | Need→Intent→Scope→PRD→REQ→ACS→Design→Evidence | 直接从想法进入代码 |
| DT-02 | 来源 Baseline、继承、偏差、独立身份 | 复制模板后失去来源 |
| DT-03 | Feature、REQ、ACS、受影响设计和回归 | 用工程任务替代产品能力定义 |
| DT-04 | 是否改变义务的分类证据 | 改变行为仍标为澄清 |
| DT-05 | 原 Revision、影响、Change、下游同步 | 原位覆盖批准需求 |
| DT-06 | 被违反 REQ、复现、修复、回归 Evidence | 无 REQ 仍关闭为缺陷 |
| DT-07 | 外部行为不变依据、技术目标、回归 | 创建无业务来源产品 REQ |
| DT-08 | 配置项、环境、Diff、生效、回退 | 控制台变更不留记录 |
| DT-09 | 消费方、迁移、兼容、保留、SRR | 删除旧身份和历史 |

### 20.6 审核清单

- [ ] 文档为二十章结构。
- [ ] 4 个 Delivery Scenario 全覆盖。
- [ ] 9 个 Development Type 全覆盖。
- [ ] 八阶段主流程顺序唯一。
- [ ] 每类任务具有进入、深化、产物、Gate、验证和退出规则。
- [ ] 多类型组合和重新分类规则明确。
- [ ] Normal/Emergency 边界明确。
- [ ] 五类实例动作未被扩展。
- [ ] C02 风险等级未被重定义。
- [ ] 正式元类型为6类；137个兼容 Profile 映射覆盖137/137；C01–C12/E01–E05 编号未变化。
- [ ] 人类 Approval、Acceptance、Risk Acceptance、Release 和 Baseline 边界明确。
- [ ] Candidate/In Review 状态未被写成 Approved。
