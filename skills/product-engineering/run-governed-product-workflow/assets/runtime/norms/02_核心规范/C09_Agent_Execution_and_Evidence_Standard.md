# C09 Agent 执行与证据规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C09 |
| 英文名称 | Agent Execution and Evidence Specification |
| 正式文件名 | `C09_Agent_Execution_and_Evidence_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3、C02 V6.3、C03 V6.3、C04 V6.3、C05 V6.3、C06 V6.3、C07 V6.3、C08 V6.3 |
| 生产前调研 | RVR-C09-0001 |
| 下游规范 | C10、C11、C12 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule 保留；正式 Run、批准、变更、验证、失败、复核和风险记录禁止无痕删除；敏感原始日志到期后按规则处置并保留最小审计记录 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的执行授权。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定 Coding Agent 从需求理解、执行计划、工具调用、命令运行、资产修改、验证、失败、重试、回滚、人类复核到交付的可审计记录。

本规范用于实现以下控制目标：

1. 使每次 Agent Run 具有唯一身份、准确输入、明确边界、时间、动作、变更和结果；
2. 使执行前的理解摘要、计划、权限、Context、Snapshot、验证和 Stop 可判定；
3. 使会改变状态、失败、验证、产生外部副作用或影响门禁的 Tool Invocation 可追踪，同时避免记录低价值读取和敏感原文；
4. 使每项资产或代码变化关联 Requirement、Design、Decision 或经批准 Engineering Change；
5. 使命令成功、Tool Result、Verification Result、Human Acceptance 和 Gate 保持分离；
6. 使失败、Retry、Stop、Rollback、未验证项和 Residual Risk 不被后续成功覆盖；
7. 使人类能够基于固定 Run、Diff、Evidence 和风险独立复核；
8. 使敏感数据、凭据、个人信息、私有推理和受限日志不被不当记录；
9. 使执行事实可以重建，但不把重建能力解释为再次执行授权或确定性复现；
10. 使 C09 与 C02、C05、C07、C08、C10、C11、C12 和 E04 保持单一事实源边界。

## 3. 适用范围

本规范适用于：

- Coding Agent、自动化 Agent、Agent Orchestrator 和被授权子 Agent 的执行；
- 文档、代码、测试、配置、Schema、Migration、脚本、基础设施即代码和其他受控资产修改；
- Read、Create、Modify、Delete、Execute、Network、External Mutation 和 Deploy 八类操作；
- Shell、CLI、API、IDE、版本控制、构建、测试、数据库、浏览器和外部服务 Tool Invocation；
- Agent Run 前检查、需求理解、计划、批准、运行、验证、失败、重试、回滚、复核和交付；
- 本地、CI、隔离环境、测试环境、预生产和生产环境中的受控执行；
- 单 Agent、多 Agent、并行 Agent 和跨 Run 交接；
- Run 产生的重要事件、受控 Evidence 引用、Diff、Commit、验证结果、失败和 Residual Risk；
- P2 档位下九类 C09 正式产物的身份、状态、必填信息、模板和质量检查；
- E01 至 E05 适用性与 C09 的附加接口。

本规范管理可观察执行事实。无论 Agent 是否修改资产，只要形成受控 Run、执行工具、产生验证主张或影响后续决策，均适用本规范。

## 4. 不适用范围

以下内容由其事实源管理：

- Product、Need、Problem、Intent、Goal 和 Discovery Evidence，由 C01 管理；
- Initiative、Scope、Agent Modification Boundary、Risk、Constraint 和 Dependency，由 C02 管理；
- PRD、Feature、Scenario 和 Non-goal，由 C03 管理；
- Requirement 语义、Revision、演进、Conflict 和缺陷转需求，由 C04 管理；
- Acceptance Criteria、Verification/Validation Strategy、Test/Check、VER/VAE、Coverage 和 Acceptance Decision，由 C05 管理；
- UX、技术设计、数据/状态、接口、Permission、Failure Design 和 Design Review，由 C06 管理；
- Agent Role、Accountability、Authorization、Approval、Prohibition、Stop、Escalation 和 Resume，由 C07 管理；
- Stable/Execution Context、Source、Priority、Freshness、Trust、Fingerprint 和 Context Delta Policy，由 C08 管理；
- Decision、Trace、Coverage、Lineage、Untracked Change 和 Orphan Artifact，由 C10 管理；
- Asset Identity、Revision、Snapshot、Baseline、Change Request、Release Configuration 和 Retirement，由 C11 管理；
- Gate、Exception/Waiver、Risk Acceptance、Release Readiness 和 Product Health，由 C12 管理；
- Security/Privacy/Compliance、Data、Knowledge/Records 或 Operations 的扩展控制，由适用 E01 至 E05 管理。

C09 可以引用上述对象并记录实际操作，但禁止用 Run 成功、日志、Agent 摘要或 VDR 修改其语义、状态、批准或基线。

## 5. 规范性用语与受控判定

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性示例，不作为符合性判定依据。

### 5.2 执行分类与判定值

以下均不是资产 State：

| 字段 | 受控值 |
|---|---|
| Operation Type | `Read`、`Create`、`Modify`、`Delete`、`Execute`、`Network`、`External Mutation`、`Deploy` |
| Execution Permission Class | `Autonomous`、`Approval Required`、`Prohibited`、`Not Assessed` |
| Step Outcome | `Succeeded`、`Failed`、`Blocked`、`Skipped`、`Cancelled` |
| Verification Result | `Pass`、`Fail`、`Blocked` |
| Review Outcome | `Pass`、`Fail`、`Blocked` |
| Approval Outcome | `Approve`、`Approve with Conditions`、`Reject`、`Defer` |

Step Outcome 表示 Run 内一个步骤的实际结果，不代替 RUN 的 EXEC State。Verification Result 复用 C05，Review Outcome 和 Approval Outcome 复用 C07。最终执行状态只能写入 RUN/HRR 的 EXEC State。

### 5.3 判定顺序

执行前按以下顺序判定：

1. 适用法律、监管、合同和有权人类 Stop；
2. C02 Scope、Agent Modification Boundary 和 Risk；
3. C07 Agent Role、Authorization、Execution Permission Class、Approval 和 Stop；
4. C08 SCM/ECP Revision、Context Fingerprint、Freshness 和 Conflict；
5. C04 Requirement、C05 Acceptance/Verification、C06 Design 和 C11 Snapshot；
6. 当前已批准 AEP；
7. 计划 Step、Action、Tool、Command、目标和验证；
8. Agent 或工具默认行为。

低层计划或命令不得扩大高层 Scope、Authority、Context、Requirement 或 Risk Acceptance。

### 5.4 状态与结果分离

RUN `Completed` 只表示执行动作结束；不表示 Verification Result = Pass、HRR = Accepted、Requirement 满足、Risk 被接受、Gate 通过或 Release 获准。

TIL/CAS/CCS 的 REC State 只表示事实已记录、更正、替代或归档，不表示工具成功、变化正确或代码可接受。RRS 的 DEC State 只表示剩余风险陈述的决策进度，不表示风险不存在。

### 5.5 规则标识与可例外性

本规范规则按 `C09-<章节号>-<条目序号>` 引用。只有使用“应”或“不应”的规则可以通过适用 C07 EXA 或 C12 EWR 申请偏离；“必须”或“禁止”规则不可由普通例外覆盖。

### 5.6 可判定表达

执行规则必须通过 Run ID、Step/Action/Attempt ID、Agent Role/Instance、Requirement/Scope/Context Revision、Operation Type、Permission Class、Approval、Tool/Version、Command/Arguments、Target、Environment/Snapshot、时间、Exit Status、Raw Log、Diff、Evidence、Result、State 和 History 直接判定。

禁止使用“按需执行”“相关命令”“适当修改”“测试通过”“已处理”“必要时重试”“应该没问题”“恢复正常”或“Agent 自行判断”代替上述字段。

## 6. 术语与定义

| 术语 | 定义 | 边界 |
|---|---|---|
| Agent Run | 具有唯一 Run ID、明确输入、开始与结束时间、动作、变更和验证结果的一次 Agent 执行 | 不等同 Agent Role、会话或模型产品 |
| Run Step | AEP 中可顺序判定、具有进入/退出条件和验证的执行阶段 | 使用 Run 内成员 ID，不是正式产物 |
| Action | Step 内一次受授权 Operation，具有精确目标、输入、预期副作用和结果 | 一次 Action 可以产生一个 Tool Invocation；不可审计复合动作必须拆分 |
| Attempt | 对同一 Action 的一次实际尝试 | Retry 创建新 Attempt，不覆盖原 Attempt |
| Tool Invocation | Agent 对 Shell、CLI、API、服务、浏览器、数据库或其他工具的一次调用 | 仅在符合第 8.0 节的重要事件条件时进入 RunLedger |
| Command | 实际交给解释器、运行时、CLI 或 Tool 的指令及参数 | 计划命令、显示文本和实际调用分开 |
| Raw Log | 工具或运行环境产生的原始 stdout、stderr、事件、响应或审计材料 | 可存外部受控位置；C09 保留稳定引用和完整性 |
| Execution Evidence | 支持某次操作、变化或验证事实的可观察材料 | 不包含模型私有思维链 |
| Understanding Summary | Agent 对当前 Requirement、Scope、Context、约束、Assumption、未知项和计划意图的可审计摘要 | 不是私有推理过程或 Requirement 重写 |
| Replayability | 在固定依赖下能够重建主要调用、输入和验证步骤的记录属性 | 不等于授权再次执行或逐字确定性复现 |
| Changed Artifact | Run 实际创建、修改、删除、移动或替代的受控资产 | Git/Diff 是低成本变化证据；任务级事实进入 TaskOutcome |
| Code Change | 影响可执行行为、构建、测试、配置、Schema、Migration、脚本或基础设施的变化 | TaskOutcome 记录 CCS 兼容语义并引用 Git；不复制完整 Diff |
| Validation Report | C09 对 Run 实际执行验证的报告 | 不与 C05 VER/VAE 混同，不作 Acceptance Decision |
| Failure | Action、Tool、Command、Validation、Environment 或控制未达到规定条件 | 后续成功不得删除或覆盖 |
| Retry | 在受控条件下再次执行 Action 的新 Attempt | 不是忽略失败或扩大 Scope |
| Execution Rollback | 为恢复到指定受控 Snapshot 而执行的新 Action 集合 | 专业化自 C11 Rollback；必须单独授权、记录和验证 |
| Run Completion | Run 已结束计划动作并记录全部结果 | 对应 RUN Completed/Failed/Cancelled，不表示接受 |
| Human Review | 有权人类基于固定 Run、Diff、Evidence 和 Risk 的独立复核 | 使用 HRR 管理 |
| Private Chain of Thought | 模型不可观察的内部推理状态 | 禁止声称捕获、恢复或强制记录 |

`Risk` 和 `Residual Risk` 的唯一语义直接适用 C02，接受权限直接适用 C12；C09 只记录 Run 产生的风险事实和处置证据，不建立平行风险定义。

## 7. 角色与职责

| 角色 | 职责 | 禁止 |
|---|---|---|
| Human Accountable / Run Owner | 确认 Run 目标、边界、完成条件、复核和交付责任 | 不得把最终责任转给 Agent |
| Requirement/Change Owner | 确认 Requirement、Engineering Change 和范围外发现的处置 | 不得用聊天口头扩展 Scope |
| Plan Author / Assembler | 编制 AEP、理解摘要、步骤、工具、验证、回滚和 Stop | 不得隐藏 Assumption 或批准缺口 |
| Coding Agent / Agent Instance | 按已批准 AEP、C07 Authorization 和 C08 Context 执行并记录事实 | 不得扩权、自批、伪造命令/结果或覆盖失败 |
| Run Controller / Orchestrator | 分配 Run/子 Run、维护顺序、共享写入和停止协调 | 不得向子 Agent 授予自身没有的权限 |
| Tool/Environment Owner | 维护工具身份、版本、技术 Permission、隔离、日志和撤销能力 | 技术能力不得被解释为正式 Authorization |
| Evidence Custodian | 保存 Raw Log、Diff、Artifact、Digest、Access 和 Retention | 不得原位修改 REC 或删除反对 Evidence |
| Validation Executor | 按 VDR 计划执行检查并记录 Expected/Actual/Result | 不得只写“已测试” |
| Independent Reviewer | 核对 Run、变更、验证、失败、敏感处理和剩余风险 | 不得评审自己未经独立复核的高风险输出 |
| Human Review Authority | 对 HRR 作 Accepted/Rejected 决定 | 不得在 Evidence 缺失时无条件接受 |
| Risk Owner / Acceptance Authority | 核对 RRS、监控、条件和适用 Risk Acceptance | Agent 不得担任 |
| Security/Privacy/Compliance Reviewer | 处理敏感命令、日志、外部传输和监管 Evidence | 不得用日志便利覆盖义务 |
| Records Owner | 按 E04 管理分类、访问、保留、更正和处置 | 不得默认永久保存敏感原文 |

高风险 Run 的 Agent、Validation Executor、Independent Reviewer、Human Review Authority 和 Risk Acceptance Authority 必须执行 C07/C12 规定的职责分离。

## 8. 治理对象与关系

### 8.0 V6.3 最小执行记录覆盖规则

本节覆盖本规范中“每次 Tool Invocation 均创建独立 TIL”“每个变化均创建独立 CAS/CCS”及“必须保存完整命令/输出”的 V6.2/V6.2.1 物理实例要求，但不删除其专业语义：

1. AEP 与 ECP 语义进入 TaskContract（`before.json`）。
2. RUN 与 TIL 语义进入只追加 RunLedger（`run.jsonl`）。普通读取、目录查看、搜索和未产生重要结果的无副作用调用不记录。
3. RunLedger 只记录 `run_started`、`mutation`、`failure`、`retry`、`verification`、`external_effect`、`human_gate`、`authority_decision_reference`、`rollback`、`run_finished`。
4. CAS、CCS、FER 的任务级事实进入 TaskOutcome（`after.json`）；需要独立长期治理时仍可建立 AuthorityAsset Profile。
5. VDR 是 DerivedView，从 RunLedger、Git Diff/Commit、VER/VAE 和原始 Evidence 按需生成。
6. HRR、RRS 仍作为 AuthorityAsset Profile 保存人类复核和剩余风险事实。
7. Git 负责低成本保存代码和文档 Diff；RunLedger 只引用 Base/Result Commit、Diff 或 Evidence Locator，不复制完整 Diff。
8. 默认只保存结构化摘要、时间、状态、Exit Code、Evidence 引用、外部副作用和脱敏说明。只有复核无法通过其他证据完成时，才把完整命令或原始输出作为受控 Evidence 保存。
9. 明文密钥、Token、密码、私钥、Session Cookie 和可复用认证材料在所有情况下均禁止写入任务记录。

V6.2/V6.2.1 的 AEP/RUN/TIL/CAS/CCS/VDR/FER 对象继续通过 `legacy_kind`兼容读取。V6.3 新任务禁止为了满足旧 Profile 数量而生成重复物理文件。

### 8.1 九类正式产物

| 类型代码 | 正式名称 | 治理职责 |
|---|---|---|
| AEP | Agent Execution Plan | 固定 Requirement/Scope/Context、理解摘要、步骤、工具、修改、验证、回滚、批准、Stop 和 Assumption |
| RUN | Agent Run Record | 记录一次 Run 的身份、时间、计划、实际动作、变更、命令、结果、失败、风险、复核和最终 State |
| TIL | Tool Invocation Log | 不可变记录一次 Tool Invocation 的输入、权限、输出、退出、日志和敏感处理 |
| CAS | Changed Artifact Summary | 不可变记录一个受控资产的原/新 Revision、变化、来源、影响和 Diff |
| CCS | Code Change Summary | 不可变记录一个代码变更集合的仓库、Commit/Diff、行为、测试、迁移和回滚影响 |
| VDR | Validation Report | 报告 Run 的验证范围、方法、环境、命令、Expected/Actual、Result、Evidence 和未验证项 |
| FER | Failure or Exception Report | 处理失败、异常、Stop、Retry、Rollback、根因状态、升级和后续行动 |
| HRR | Human Review Record | 记录固定 Run/Change 的人类评审、独立性、Evidence、Finding、结论和接受/拒绝 |
| RRS | Residual Risk Statement | 陈述 Run/Release 范围内剩余 Risk、控制、条件、Owner、批准、监控和失效 |

兼容 TIL Profile 只记录一次重要 Tool Invocation；V6.3 默认以 RunLedger Event ID 保持独立身份。CAS/CCS/FER 语义进入 TaskOutcome 时必须保留来源、范围和 History，聚合视图不得消除可追踪性。

### 8.2 受控关系

| 来源 | 关系 | 目标 | 规则 |
|---|---|---|---|
| AEP | `depends-on` | Requirement、Scope、C07 Authorization、C08 ECP、C11 Snapshot | 必须固定 Revision |
| RUN | `depends-on` | AEP、C07 Authorization、C08 ECP/SCM/CPP | 实际 Revision 必须记录 |
| RUN | `contains` | Step、Action、Attempt 和 TIL 引用 | 成员保留独立身份 |
| TIL | `observed-from` | Tool Invocation/Command | 必须保留时间、输入输出和 Raw Log |
| CAS/CCS | `generated-by` | RUN | 不表示变化已批准 |
| CAS/CCS | `derives-from` | 原资产 Revision、Diff 或 Commit | 原/新状态和来源可定位 |
| VDR | `observed-from` | TIL、Raw Evidence 和 Environment | Result 绑定实际 Snapshot |
| VDR | `depends-on` | C05 Strategy/Criterion/Test/Check | 不替代 VER/VAE |
| FER | `observed-from` | 失败 Action/TIL/VDR | 原失败不可覆盖 |
| HRR | `observed-from` | RUN、CAS/CCS、VDR、FER、RRS | 评审对象 Revision 固定 |
| RRS | `addresses` | Risk/Concern | 不等于风险已接受 |
| C09 产物 | `affected-by` | C08 Context Delta/C11 Change | 必须说明影响和失效 |

正式 Trace 由 C10 管理。C09 只能使用公共受控关系，禁止创建名为 related-to、“执行了”或“测试了”的模糊关系。

### 8.3 唯一事实源边界

| 信息 | 唯一事实源 | C09 处理 |
|---|---|---|
| Requirement/Engineering Change | C04/C11 | 引用 ID/Revision；记录实现来源 |
| Acceptance/Verification/Validation | C05 | 执行既定检查并形成 VDR；引用 VER/VAE/ACD |
| Agent Role/Authorization/Approval/Stop | C07 | 每个 Action 记录实际引用 |
| Context/Source/Fingerprint/Delta | C08 | 每个 Step 记录有效 ECP Revision |
| Run/Command/Tool/Actual Change | C09 | 建立与维护 |
| Decision/Trace/Lineage | C10 | 输出候选链接和执行事实 |
| Snapshot/Baseline/Change/Release Configuration | C11 | 记录实际使用和产生的 Revision |
| Gate/Risk Acceptance/Exception | C12 | 输出 Evidence；不得自行决定 |
| Knowledge/Record lifecycle | E04 | 提供 Provenance、Access、Retention、更正和处置规则 |

### 8.4 C05 与 C09 Evidence 分工

C09 VDR 证明“某个 Run 在某环境实际执行了哪些验证并得到什么结果”。C05 VER/VAE 判断这些材料是否构成当前 Requirement/Need 的正式 Evidence，C05 ACD 决定 Acceptance。三者禁止合并。

## 9. 生命周期与工作机制

### 9.1 生命周期

`Run Intake → Preflight → Understanding Summary → AEP → Authorization/Approval Check → RUN Ready → Step/Action Execution → TIL/CAS/CCS Capture → VDR → Failure/Retry/Rollback Control → Human Review → Status Writeback → Completion/Acceptance → Retention`

### 9.2 Run Intake

必须取得：

- Product、Initiative、Requirement、Scope、Risk 和 Agent Modification Boundary；
- C05 Acceptance/Verification 输入；
- C06 Design、Failure、Permission 和 Rollback 输入；
- C07 Agent Role、Authorization、Execution Permission Class、Approval、Stop 和有效期；
- C08 SCM/ECP/CPP/CFR Revision、Fingerprint、Context Delta Policy 和开放 CCF；
- C11 仓库、Commit、工作区、配置、环境和数据 Snapshot；
- 目标 Run、Human Accountable、Reviewer、交付形式和期限；
- E01 至 E05 适用性及 Access/Retention 义务。

必需输入缺失、冲突或过期时，只能创建 Planned RUN/AEP Draft，禁止进入 Ready。

### 9.3 Preflight

Run Controller 必须依次检查 Scope、Context、Authorization、Permission、Approval、Stop、Risk、Snapshot、Tool、Sensitive、Validation、Rollback、Logging 和 Retention。检查结果、检查者、时间和 Evidence 写入 RUN；任一 Blocking 失败使 RUN State = Blocked。

### 9.4 Understanding Summary

Agent 在计划前输出：

- 当前 Requirement/Goal 和 Revision；
- In Scope、Out of Scope、允许/禁止 Operation；
- 当前 ECP/SCM Revision 和关键约束；
- Acceptance/Verification 目标；
- Design/Snapshot/Environment；
- 已知事实、Assumption、未知项和冲突；
- 拟修改对象、预期行为和完成定义。

摘要必须可供人类复核，但禁止包含或声称包含私有思维链。

### 9.5 AEP 与 RUN Ready

AEP 将理解摘要转换为有序 Step、Action、Tool、Command/Invocation、预期副作用、验证、回滚、批准点和 Stop。AEP 达到 Approved/Baselined 且全部 Preflight 通过后，RUN 可以从 Planned 转为 Ready。

### 9.6 Step 执行循环

每个 Step 按以下顺序执行：

1. 固定 Step/Action/Attempt ID；
2. 读取当时有效 ECP Revision；
3. 复核 Operation、Permission、Approval、Target 和 Snapshot；
4. 记录计划调用、Expected Effect 和验证；
5. 执行 Tool/Command；
6. 捕获 TIL、Raw Log 和 Actual Effect；
7. 捕获 CAS/CCS；
8. 执行局部验证；
9. 判定 Step Outcome；
10. 检查 Context Delta、Risk、Stop 和下一个 Step。

### 9.7 Failure、Retry 与 Rollback

任一 Failed/Blocked、非预期副作用、Stop、验证失败或证据缺失必须建立 FER。Retry 或 Rollback 只能在副作用、权限、Plan、风险和新鲜 Context 可判定时执行。

### 9.8 Validation 与 Human Review

Run 动作结束后形成 VDR。涉及受控资产变化、正式交付或高风险结果时，Independent Reviewer/人类 Reviewer 必须基于固定 RUN、CAS/CCS、VDR、FER、RRS 和 Diff 形成 HRR。

### 9.9 Completion、Acceptance 与 Writeback

RUN Completed 表示动作已结束且记录完整；RUN Accepted 必须有 HRR Accepted、阻断 Finding 为零、Residual Risk 已按 Authority 处置且写回接口完成。写回只能更新原事实源允许的字段或创建受控 Change/Issue/Trace，不得用 C09 覆盖上游状态。

## 10. 强制规则

### 10.1 Run 身份与边界

1. 每次 Agent Run 必须创建唯一 RUN ID，格式为 `RUN-<NNNN>`。
2. RUN ID 禁止复用；终止、失败、重启、恢复或不同 Agent Instance 不得覆盖原 RUN。
3. Step ID 使用 `<RUN ID>-S<NNN>`，Action ID 使用 `<RUN ID>-A<NNN>`，Attempt ID 使用 `<Action ID>-T<NN>`。
4. 成员 ID 不是新增正式产物类型；正式产物仍为 AEP/RUN/TIL/CAS/CCS/VDR/FER/HRR/RRS。
5. RUN 必须绑定一个主要 Task/交付目标；无关工作建立新 Run。
6. Parent/Child Run 必须分别具有 RUN ID、Scope、Agent Instance、Authorization、ECP Revision 和交接。
7. 开始、结束、阻塞、恢复和终止时间必须使用可排序时间及 Time Zone。
8. Session、Thread、聊天标题、进程 ID 或模型响应 ID 不得单独作为 Run 身份。

### 10.2 执行前检查

RUN 进入 Ready 前必须全部满足：

- Requirement/Engineering Change 来源可定位；
- Scope、Risk 和八类 Operation Boundary 明确；
- C07 Agent Role、Authorization、Permission、Approval、Stop、ESP 和有效期当前有效；
- C08 ECP/SCM/CPP/CFR 为适用 Approved/Baselined Revision，无阻断 CCF；
- ECP Fingerprint 可重算，Context Budget 和 Delta Policy 可用；
- 仓库、Commit、Dirty State、未跟踪变化、环境、配置和数据 Snapshot 固定；
- Tool/Version/Identity/Permission 与 AEP 一致；
- Sensitive/Secret/External Service 边界明确；
- Verification Method、Expected、Environment 和 Raw Evidence 位置明确；
- Failure、Retry、Rollback、Cleanup 和 Retention 有规则；
- Human Accountable、Reviewer、Approver、Risk Owner 和交付目标明确。

“技术上可以执行”禁止替代上述检查。

### 10.3 需求理解摘要

1. 每个 AEP/RUN 必须保存 Understanding Summary。
2. 摘要必须逐项引用 Requirement、Scope、Context、Design、Acceptance 和 Snapshot Revision。
3. 摘要必须分开记录 Fact、Assumption、Unknown、Conflict、Non-goal 和 Proposed Action。
4. Agent 不得把自己的解释写回为 Requirement，也不得用摘要消除上游冲突。
5. 高影响 Unknown、歧义或 Conflict 未解决时必须 Blocked。
6. 摘要变化必须形成 AEP/RUN 新 Revision 或 Delta，不得无痕改写。
7. 摘要只说明“理解结果与执行依据”，禁止要求或声称记录完整内部推理。

### 10.4 Agent Execution Plan

AEP 必须包含：

1. Task、Requirement、Scope、Context、Agent Role、Environment 和 Snapshot；
2. 理解摘要、完成条件、Non-goal 和剩余 Assumption；
3. 有序 Step、每个 Step 的目标、输入、输出、依赖和退出条件；
4. 每个 Action 的 Operation Type、Target、Permission、Approval 和 Expected Effect；
5. Tool/Version、Command/Invocation、工作目录、参数边界、超时和资源限制；
6. 修改对象、最大数量/范围和禁止对象；
7. Verification Method、Expected Result、Evidence 和未验证风险；
8. Failure、Retry、Rollback、Cleanup 和停止策略；
9. Sensitive/Secret/External Data 处理；
10. Reviewer、Approval Point、交付和状态回写。

AEP 中的占位命令不得被记录为已执行。Run 中 Scope、Risk、Tool、Target、验证或回滚发生实质变化时必须停止、修订 AEP 并重新判定批准。

### 10.5 Step、Action 与 Attempt

1. 每个 Step 必须引用 AEP Step、有效 ECP Revision 和进入/退出条件。
2. 每个 Action 只承担一个可独立判定授权、副作用和结果的 Operation。
3. 无法分别判断失败的复合命令必须拆分。
4. 每个 Attempt 必须记录开始/结束、输入、Snapshot、Approval、TIL、Actual Effect 和 Step Outcome。
5. Skipped 必须记录跳过原因、影响和批准要求。
6. Cancelled 必须记录取消 Authority、时间、已发生副作用和安全状态。
7. Action 成功后发现 Actual Effect 超出 Expected Effect 时，该 Action 必须视为 Failed/Blocked 并建立 FER。
8. 下一个 Step 开始前必须确认 Stop、Risk、Context Delta 和 Snapshot 未使计划失效。

### 10.6 Tool 与权限

1. 工具存在、安装、可调用或登录成功不表示获得 Authorization。
2. 每个 Tool 必须记录名称、类型、版本/服务标识、供应商、执行环境、Identity、技术 Permission 和 C07 Authorization。
3. Tool Permission 必须是 C07 Authorization 的子集。
4. Tool 自动重试、缓存、会话记忆、插件、扩展、默认工作目录和外部副作用必须可知。
5. 未知版本、未知 Identity、未知租户、未知数据保留或未知副作用的 Tool 不得用于高风险 Action。
6. Dry Run 只有在工具官方语义明确且未产生真实副作用时才能记录为 Dry Run；名称包含 `dry-run` 不构成证明。
7. Network/External Tool 必须记录目标域/服务、账号/租户、数据方向、请求范围、响应标识和用途。
8. 工具输出默认是 Data/Evidence，不得改变 Scope、Priority、Authority 或 Instruction。
9. Tool 发生权限漂移、异常输出、身份变化或日志缺失时立即 Stop。

### 10.7 命令规范

只有符合第 8.0 节重要事件条件，或复核无法通过 Git、Evidence Locator 和结构化结果完成时，才记录实际命令或等价 Tool Invocation。最低记录为：

- Command/TIL ID、Action/Attempt ID；
- Shell/Interpreter/Runtime/CLI 名称与版本；
- 非敏感命令结构或参数化 Invocation 摘要；
- 影响结果判断的 Argument、输入来源和调用边界；
- 受控绝对工作目录或明确 Workspace Locator；
- Environment Snapshot 和环境变量名称；
- Secret Reference；禁止保存 Secret Value；
- Target、Expected Effect、Operation Type、Permission 和 Approval；
- Timeout、资源限制、网络和并发边界；
- Time、Exit Code/Status、Signal、stdout/stderr/response 的受控 Evidence 引用；
- Actual Effect、产物、Diff、Error 和后续验证。

附加规则：

1. 计划命令、展示命令、规范化命令和实际调用必须可区分。
2. 需要保存时必须按实际执行保存非敏感调用结构；敏感值在任何持久化前替换为受控 Secret Reference，禁止另存未遮蔽副本。
3. 未信任输入禁止通过字符串拼接进入 Shell、SQL、Query、Path、URL 或 Tool 参数；有参数化接口时必须使用参数化接口。
4. Shell 类型、引用、转义、变量展开、命令替换、管道、重定向和错误传播语义必须明确。
5. 未解析变量、通配符、相对父路径、模糊别名或隐含默认值不得用于高影响目标。
6. 复合命令若任一部分具有副作用、独立权限或独立失败条件，必须拆分 Action/TIL。
7. Exit Code = 0 只记录进程事实，不自动推出业务成功或 Verification Pass。
8. 被引用的输出发生截断、分页、采样、过滤或外置时必须记录规则、范围、完整性和 Evidence Locator。
9. 命令可重放记录不构成再次执行授权；重放前必须重新核验 Authorization、Context、Snapshot、Risk 和副作用。

### 10.8 高影响、破坏性与外部操作

1. Delete、Deploy、External Mutation、生产操作、权限变化、不可逆操作和 High/Critical Risk Action 至少为 Approval Required；Prohibited 仍禁止。
2. 目标必须解析为精确仓库、路径、资源、记录、租户、账户、环境和版本。
3. 工作区根、用户主目录、系统根、整个账户/租户、未解析变量、宽泛通配符或计算后未复核目标禁止作为破坏性 Target。
4. 执行前必须记录 Before Snapshot、影响范围、可恢复性、备份/回滚、幂等策略、观察窗口和验证。
5. External Mutation 必须使用服务支持的 Idempotency Key 或记录不可幂等及补偿措施。
6. Deploy 必须引用 C11 Release Configuration、C12 Gate/Approval、窗口、监测、回滚和 Owner。
7. “清理”“修复”“格式化”“回滚”“恢复”不得扩大批准目标。
8. Retry 高影响 Action 前必须先确认上次 Attempt 的外部副作用和幂等状态。
9. 删除或覆盖前必须识别用户已有、未提交、未跟踪和并行 Agent 变化；未知时 Stop。
10. 操作后必须验证 Actual Effect；只有命令成功但目标状态未知时为 Blocked。

### 10.9 Tool Invocation Log

1. 只有 mutation、failure、retry、verification、external_effect、human_gate、authority_decision_reference 或 rollback 调用进入 RunLedger；普通读取和搜索不创建事件。
2. RunLedger Event 必须按 Run 内 Sequence 单调编号。
3. Event 的必需字段以 VC-PPG-PRO-001 §13.3 和 `run-event.schema.json` 为准：Run/Attempt、Sequence、Time、Event Type、Summary、Status、Exit Code、Evidence References、Side Effects 和 Redactions。Tool/操作类别、Permission、Input/Output Summary 与 Actual Effect 只在解释重要事件、权限边界或副作用所必需时进入 Summary、Evidence 或外置 Raw Log，不为普通调用强制扩展账本字段。
4. 输入/输出摘要必须保留事实语义和限制，禁止为显示成功而删除错误。
5. Raw Log 只有在复核需要时外置，并记录 URI/Locator、Digest、Access、Retention、获取方式和不可用原因。
6. Tool 超时、取消、断连、部分返回、非零退出、异常格式或未知状态必须明确记录。
7. RunLedger 只追加；更正通过新 Event 引用原 Event，不允许原位修改。
8. 未实际发生的重要事件禁止创建伪造记录。
9. 验证失败后必须先在当前 AttemptID 追加显式 `failure` 事件，再以新 AttemptID 追加 `retry`；切换后不得回填旧 Attempt。

### 10.10 变更捕获

1. Action 前后必须比较受控目标的 Snapshot。
2. 创建、修改、删除、移动、重命名、权限变化、生成物和外部资源变化都必须捕获。
3. Git 工作区必须记录 Base Commit、Branch、Dirty State、Staged/Unstaged/Untracked、Submodule/LFS 和检查时间。
4. Diff 必须能定位到文件/资产和 Revision；二进制、生成物或外部对象使用 Manifest/Digest/对象版本。
5. Agent 发现非本 Run 产生的变化时必须隔离并登记，不得归因给当前 Run。
6. 自动格式化、依赖更新、Lockfile、Schema、Migration、测试快照和配置变化不能以“附带变化”省略。
7. 变化超出 AEP 最大范围时必须 Stop，并保留已发生变化的 Evidence。
8. 无变化时 RUN 必须记录比较方法和 No Change Evidence，禁止仅写“未修改”。

### 10.11 CAS 与 CCS

1. 每个实际变化必须在 TaskOutcome 的 `actual_changes` 或独立 AuthorityAsset Profile 中可解析；不要求每个文件建立单独 CAS。
2. 变化记录必须固定目标 Asset/Path、Old Revision、New Revision、Change Summary、Reason、Requirement/Engineering Change、Impact 和 Git/Evidence 引用。
3. 同一 Asset 多个结果 Revision 必须分别记录，禁止只保留最终状态而丢失已使用中间状态。
4. 涉及代码、测试、配置、Schema、Migration、构建脚本或基础设施即代码时，TaskOutcome 必须包含 CCS 兼容语义。
5. 代码变化摘要必须记录 Repo、Base/Result Commit 或 Diff、File/Component、行为影响、Requirement/Design/Decision、Test、Migration、Compatibility 和 Rollback Impact。
6. Git Commit/PR/Diff 可以作为变化范围和内容的权威证据；TaskOutcome 仍必须解释行为影响、来源、验证和未解决项。
7. 变化摘要不表示变更被 Review、Accepted、Baselined 或 Released。

### 10.12 验证与 Evidence

1. 每个产生变化、运行结果或质量主张的 Run 必须在 RunLedger/TaskOutcome 记录验证事实；Gate、审计或人类审核需要汇总时按需生成 VDR DerivedView。
2. VDR 必须引用 C05 Strategy/Criterion/Test/Check；无正式 C05 对象时必须说明适用边界和建立要求。
3. 每项验证必须记录 Subject/Snapshot、Method、Environment、Input、Command/TIL、Expected、Actual、Verification Result、Raw Evidence、Executor 和 Time。
4. 只有实际执行且 Expected/Actual 可比较时才能给出 Pass/Fail；必需验证未执行时为 Blocked。
5. Exit Code = 0、编译成功、测试数量、Agent 自述或无错误输出不得单独构成 Pass。
6. Fail/Blocked、Flaky、Warning、Skipped、Not Applicable、未覆盖和环境差异必须显式记录。
7. 重跑必须创建新 verification Event/Evidence 引用，并保留全部旧结果。
8. VDR 必须列出未验证项、局限、过期风险、Coverage Gap 和复核要求。
9. C05 VER/VAE 是否 Accepted、Coverage 是否满足、Acceptance Outcome 如何，由 C05 决定。
10. Snapshot、Context、Environment、Tool 或 Criterion 变化时必须重评 VDR 新鲜度。
11. “全部通过”“已测试”“符合标准”没有逐项 Evidence 时禁止使用。
12. 验证 Action 按计划完成时 Step Outcome 可以为 Succeeded，而 Verification Result 仍可为 Fail；两个字段禁止互相覆盖。

### 10.13 Failure、Stop 与 Retry

1. 以下任一情况必须创建 FER：Failed/Blocked Step、Tool/Command Error、Validation Fail/Blocked、Stop Trigger、非预期副作用、证据丢失、Retry、Rollback 或敏感暴露。
2. FER 必须记录失败时间/步骤、症状、Error Evidence、影响、已发生副作用、即时处置、根因状态、升级和关闭条件。
3. 失败类别必须能区分 Input、Permission、Context、Tool、Command、Environment、External、Validation、Resource、Conflict 和 Sensitive。
4. 后续成功禁止覆盖、删除或把失败改写为成功。
5. Retry 必须创建新 Attempt，记录原因、变化参数、修正、授权、幂等/副作用检查和结果。
6. Retry 上限、退避和终止条件由 AEP、工具、Risk 和授权定义，禁止使用虚构全局次数。
7. 非幂等或副作用未知的 Action 禁止自动 Retry。
8. Retry 需要扩大 Scope、权限、参数、目标、环境或风险时必须停止并重新批准。
9. Stop 后只允许 C07 预授权的安全保存、只读诊断和 Evidence 封存。
10. FER 只能在根因/处置、影响、剩余风险和复核条件满足后由有权人类关闭高风险事项。

### 10.14 Rollback 与恢复

1. Rollback 是新受控 Action，不是失败记录的删除。
2. Rollback 前必须固定目标 Snapshot、Current State、影响、权限、批准、命令、验证和无法恢复项。
3. 禁止把强制重置、覆盖未提交变化、删除工作区或回滚并行 Agent/用户变化作为默认恢复手段。
4. Rollback 必须记录 TIL、CAS/CCS、Actual Effect 和 VDR。
5. “Rollback Succeeded” 必须由目标资产/环境恢复到指定 Snapshot 且验证 Pass 证明。
6. 部分回滚、补偿动作失败、外部不可逆影响和数据丢失必须保留 FER/RRS。
7. Resume 必须取得 C07 Resume Approval、重新生成/确认 C08 Context Fingerprint，并核对新 Snapshot。
8. 恢复后继续原 Run 还是创建新 Run，必须根据 AEP、Authorization、Context 和已终止 State 判定；终端 RUN 禁止重新打开为 Running。

### 10.15 Human Review

1. 受控资产变化、正式交付、高风险 Action、生产/外部影响或 Residual Risk 必须形成 HRR。
2. HRR 必须固定 RUN、AEP、Context、Snapshot、CAS/CCS、VDR、FER、RRS 和 Diff Revision。
3. Reviewer 必须记录身份、角色、独立性、范围、方法、Evidence、Finding、Review Outcome、整改和时间。
4. Reviewer 必须检查来源、范围、Actual Change、命令、验证、失败、未解决项、敏感处理和风险。
5. Agent 自检可以写入 RUN，但不能把自身高风险输出的 HRR State 设为 Accepted。
6. HRR Accepted/Rejected 必须由授权人类决定。
7. 有 Open/Blocked 高风险 FER、缺失 Evidence、范围外变化或未经处置 Residual Risk 时禁止 Accepted。
8. 复核后变化必须产生新 Run/Revision 和新 HRR，旧评审不得自动沿用。
9. 人类评论、表情、聊天或沉默未形成 HRR/Approval Evidence 时不得解释为接受。

### 10.16 状态回写与范围外发现

1. C09 只能按上游规范定义的接口写回执行事实、Evidence 引用、Finding、Change Request 候选或状态转换请求。
2. RUN/VDR Pass 禁止直接把 Requirement、Acceptance、Risk、Baseline、Gate 或 Release 状态改为已批准。
3. 范围外发现必须记录在 RUN 的 Observation/Unresolved Item，并路由到 C02 Risk/Dependency、C04 Requirement/Defect、C10 UCR/OAR 或 C11 Change。
4. Agent 禁止以“顺手修复”“同类问题”“必要重构”实施范围外发现。
5. Writeback 必须记录 Target Asset/Field、Old/New Value、Authority、Source Run、Time 和 Result。
6. 写回失败、部分成功、冲突或外部状态未知必须建立 FER。
7. 状态转换必须遵循公共状态模型并记录原/新状态、执行者、依据和时间。
8. C10/C11/C12 未完成时，C09 只能形成约束输入和引用，不得伪造正式下游产物。

### 10.17 敏感信息与日志

1. Access Classification 使用公开、内部、机密、受限。
2. 明文密钥、Token、密码、私钥、Session Cookie 和可复用认证材料禁止进入 AEP/RUN/TIL/VDR/FER/HRR 或 Raw Log。
3. 使用 Secret Reference 时必须记录提供方、用途、Scope、有效期和撤销，不记录值。
4. 个人信息、客户数据、商业秘密、漏洞、受监管数据和受限代码必须最小化、遮蔽、隔离和授权。
5. Redaction 必须保留字段位置、方法、执行者、时间、验证和不可逆影响。
6. stdout/stderr、Stack Trace、Diff、截图、Core Dump、Environment、URL、Header 和 Tool Response 必须检查敏感回显。
7. 日志采集、传输、索引、缓存、训练使用、外部供应商和跨租户边界必须可知。
8. 为避免泄漏而遮蔽内容时，仍必须保留不含敏感值的命令结构、Exit Status、Evidence Locator 和审计可用性。
9. 敏感日志保留期限按 E04/E02、合同和合规确定；禁止因“可审计”默认永久保存全部原文。
10. 发现泄漏或越权时立即 Stop、封存 Evidence、通知并按触发条件激活 E02。
11. 可预知的敏感字段必须在持久化前遮蔽；不可预知回显必须先进入授权隔离区，完成清理验证后才能进入普通日志系统。

### 10.18 模型与执行引擎标识

1. 可获得时记录 Provider、Service、Model/Engine Name、Exact Version/Revision、Deployment、Runtime、Region 和 Invocation Time。
2. 无法获得 Exact Version 时记录可获得的 Provider/Service、Model Alias、Endpoint/Deployment、Runtime 和时间，并标记限制。
3. 禁止根据营销名称、UI 标签、输出风格、模型自述或猜测编造版本。
4. Agent Instance、Orchestrator、Model/Engine、Tool 和 Human Actor 必须分别记录。
5. 模型参数、随机性、系统约束或私有配置不可获得时必须声明 Unavailable，不得伪造。
6. 模型标识变化必须进入影响分析，并明确 Comparison、Replayability 和 VDR 是否失效。
7. C09 不要求记录私有思维链、隐藏系统 Prompt 或供应商不可见内部状态。

### 10.19 多 Agent、并发与交接

1. 每个 Agent Instance 使用独立 RUN ID 或明确 Parent/Child Run。
2. Parent 给 Child 的权限为 Parent Authorization、Child ARD、Task Scope、Tool Permission 和 ECP 的交集。
3. 交接必须传递 Requirement/Scope、AEP Step、ECP Revision/Fingerprint、Snapshot、允许输出、禁止项、Stop、Evidence 和返回格式。
4. 共享工作区必须记录 Owner、锁/租约、Base Commit、写入顺序、并发冲突和合并 Authority。
5. 两个 Agent 对同一资产并发 Modify 时，未有批准协调策略必须冻结写入。
6. 子 Agent TIL、CAS/CCS、VDR、FER 和 RRS 必须回链 Parent Run；只传最终摘要禁止作为完整 Evidence。
7. Agent 禁止相互授权、批准、接受风险或消除 Stop。
8. 合并结果必须记录来源 Run、Diff、Conflict Resolution、Reviewer 和新 Snapshot。

### 10.20 Coding Agent 行为边界

Coding Agent 可以：

- 生成 AEP/RUN/TIL/CAS/CCS/VDR/FER/HRR/RRS Draft；
- 执行已授权、已计划且未触发 Stop 的 Action；
- 捕获命令、Tool Result、Diff、日志、验证和 Failure；
- 计算已定义 Digest、统计和机械检查；
- 提出 Finding、范围外 Observation、Change 和 Risk 候选；
- 执行已授权的安全保存、验证和证据封存。

Coding Agent 禁止：

- 扩大 Scope、Authorization、Permission、Approval、Context 或最大修改范围；
- 把计划命令、模拟结果、缓存结果或未执行检查记录为实际执行；
- 伪造模型版本、命令、时间、退出状态、Diff、测试或 Evidence；
- 删除、隐藏、重写 Failure、Retry、Rollback、Finding、反对意见或原 REC；
- 把 Exit Code = 0、测试通过或 Tool Success 声明为 Acceptance、Gate、Release 或完整标准符合；
- 自行接受 High/Critical Residual Risk、自批 Run 或关闭高风险 FER；
- 将私有思维链写入正式记录或声称已捕获；
- 为完成任务访问、复制、输出或持久化未授权敏感信息；
- 用回滚、清理、格式化、自动修复或重试执行未授权变化；
- 把范围外发现直接实现。

## 11. 受控状态

### 11.1 DOC：AEP 与 VDR

`Draft`、`In Review`、`Changes Required`、`Approved`、`Baselined`、`Rejected`、`Superseded`、`Retired`。

AEP Draft/In Review/Changes Required 禁止授权 RUN Ready。VDR Approved/Baselined 只表示报告内容被批准/基线，不表示其 Verification Result 必然 Pass。

### 11.2 EXEC：RUN 与 HRR

`Planned`、`Ready`、`Running`、`Blocked`、`Completed`、`Failed`、`Accepted`、`Rejected`、`Cancelled`。

RUN 遵循：

`Planned → Ready → Running → Completed → Accepted/Rejected`；
`Running ↔ Blocked`；
`Running → Failed/Cancelled`。

RUN Failed/Cancelled/Accepted/Rejected 为终端结果；继续工作必须建立新 Run。HRR 使用同一 EXEC 模型，Accepted/Rejected 必须由授权人类决定。

### 11.3 REC：TIL、CAS 与 CCS

`Recorded`、`Corrected`、`Superseded`、`Archived`。

REC 捕获已发生事实，禁止原位修改。更正必须创建 Corrected 记录，保留原值、原因、执行者和时间。

### 11.4 CASE：FER

`Open`、`In Progress`、`Blocked`、`Resolved`、`Closed`、`Reopened`、`Cancelled`。

FER Closed 表示失败/异常处置已复核，不表示原失败未发生。

### 11.5 DEC：RRS

`Proposed`、`Under Review`、`Approved`、`Conditionally Approved`、`Rejected`、`Waived`、`Superseded`、`Expired`。

RRS Approved/Conditionally Approved/Waived 必须由有权人类决定，并记录范围、条件、Owner、监控、复核和失效时间。RRS 不替代 C02/C12 的正式 Risk Acceptance。

### 11.6 状态转换

1. 状态转换遵循 VC-PPG-COM-002。
2. Approved、Conditionally Approved、Waived、Accepted 和 Baselined 必须由授权人类决定。
3. Agent 可以建议 State，但不得批准自身产生的高风险输出。
4. RUN Completed 禁止自动转为 Accepted。
5. Step Outcome、Verification Result、Review Outcome、Approval Outcome、Exit Status 和 Failure Category 禁止写入 State。
6. Failed/Rejected/Cancelled/Blocked/Ferr Finding 不得通过修改 State 历史消失。
7. 已用于 Decision/Gate/Release 的 Revision 和 State 历史必须保留。

## 12. V6.3 必需载体与条件 Profile

| 元类型/载体 | 最低创建条件 | 承载的 C09 兼容语义 |
|---|---|---|
| TaskContract / `before.json` | 每个拟执行任务在 Run 前创建并冻结 | AEP、ECP、Scope、Authorization、计划、验证、回退和 Stop |
| RunLedger / `run.jsonl` | 每个实际 Run；无事件时允许空文件 | RUN、重要 TIL、失败、重试、验证、外部副作用和回滚事件 |
| TaskOutcome / `after.json` | 每个结束任务 | CAS、CCS、FER、实际变化、验证、未完成项和遗留问题 |
| DerivedView / VDR | Gate、审计、复核或查询需要时 | 从 RunLedger、Git 和 VER/VAE 生成验证汇总 |
| AuthorityAsset / HRR、RRS | 实际发生人类复核或剩余风险陈述时 | 权威复核和风险事实 |

P2 禁止丢失九个旧 Profile 的专业语义，但允许按上表合并物理载体。没有 Change、Failure、Human Review 或 Residual Risk 时不创建空 Profile 实例。

## 13. 必填信息

### 13.1 通用必填信息

TaskContract、RunLedger 和 TaskOutcome 必须满足对应 JSON Schema；独立 AuthorityAsset/DerivedView Profile 必须引用 VC-PPG-COM-002 第 3 章通用信息和第 3.1 节公共字段组。以下旧 Profile 字段作为兼容信息按需嵌入，不要求拆成九份文件。

### 13.2 Agent Execution Plan

AEP 必须包含：

- AEP ID、Run ID、Task、Owner、Human Accountable；
- Requirement、Scope、Risk、Context、Design、Acceptance、Snapshot；
- Understanding Summary、Fact/Assumption/Unknown/Conflict/Non-goal；
- Step/Action、依赖、输入、输出、进入/退出和顺序；
- Operation、Tool、Command/Invocation、Target、Environment、资源和超时；
- Permission、Approval Point、Prohibited Action、Stop 和 ESP；
- 修改对象和最大范围；
- Validation、Expected、Evidence 和 Coverage；
- Failure、Retry、Rollback、Cleanup；
- Sensitive、Secret、Network、External Data；
- Reviewer、交付、状态回写；
- State、Revision、Approval 和 History。

### 13.3 Agent Run Record

RUN 必须包含：

- Run ID、Parent/Child、Task、Agent Role/Instance、Human Accountable；
- Model/Engine/Orchestrator/Tool 标识与可用性限制；
- Start/End、State、Blocked/Resume/Cancel/Failure Time；
- Requirement、Scope、Risk、Design、Acceptance、AEP；
- SCM/ECP/CPP/CFR Revision、Fingerprint 和 Delta；
- Environment/Workspace/Commit/Dirty State/Config/Data Snapshot；
- Understanding Summary 和实际偏差；
- Step/Action/Attempt、Operation、Permission、Approval、Stop；
- Tool/TIL、Command、Input/Output、Exit 和 Actual Effect；
- CAS/CCS、Diff、Commit、External Change；
- VDR、FER、Retry、Rollback；
- Unresolved/Observation/Out-of-Scope；
- Residual Risk/RRS、HRR、Writeback、Final State；
- History 和 Retention。

### 13.4 Tool Invocation Log

TIL 必须包含：

- TIL ID、Run/Step/Action/Attempt、Invocation Sequence；
- Tool/Version/Provider/Service/Identity/Environment；
- Operation Type、Permission、Approval、Target；
- Command/Invocation、Argument、Working Directory、Input Summary；
- Environment/Secret Reference、Timeout/Resource/Network；
- Start/End、Exit Code/Status/Signal；
- Output/Error Summary、Raw Log Locator/Digest；
- Actual Effect、Produced Artifact、Follow-up Validation；
- Sensitive/Redaction、Retention；
- State、Correction/Supersession 和 History。

### 13.5 Changed Artifact Summary

CAS 必须包含：

- CAS ID、Run/Action/TIL；
- Asset ID/Type/Owner/Locator；
- Old Revision/Snapshot/State、New Revision/Snapshot/State；
- Change Type、Summary、Reason、Producer；
- Requirement/Engineering Change/Design/Decision Source；
- Diff/Manifest/Digest/Commit；
- Behavior/Data/Interface/Access/Retention Impact；
- Downstream Impact、Validation、Rollback；
- State、Correction/Supersession 和 History。

### 13.6 Code Change Summary

CCS 必须包含：

- CCS ID、Run、Repo、Base/Result Commit、Branch/Dirty State；
- File/Component/Module、Change Type 和代码摘要；
- Behavior、Interface、Data、Security、Performance 和 Compatibility Impact；
- Requirement、Design、Decision、Engineering Change；
- Test/Static/Build/Scan Result 和 VDR/VER；
- Dependency/Lockfile/Generated/Migration/Config 变化；
- Deployment、Migration、Rollback 和 Operational Impact；
- Reviewer、Diff/PR/Commit；
- State、Correction/Supersession 和 History。

### 13.7 Validation Report

VDR 必须包含：

- VDR ID、Run、Validation Scope、Owner/Reviewer；
- Requirement/Criterion/Strategy/Test/Check；
- Subject、Revision/Snapshot、Environment、Tool；
- Method、Command/TIL、Input、Oracle；
- Expected、Actual、Verification Result；
- Raw Evidence、Digest、Producer、Time；
- Fail/Blocked/Warning/Flaky/Skipped/Not Applicable；
- 未执行、未覆盖、局限、Freshness 和 Impact；
- C05 VER/VAE/VCM/ACD 引用；
- Conclusion、Required Action、Recheck；
- State、Revision、Approval 和 History。

### 13.8 Failure or Exception Report

FER 必须包含：

- FER ID、Run/Step/Action/Attempt、Failure Category；
- Detection Time、Detector、Symptom、Error Evidence；
- Expected/Actual、Exit/Tool State；
- Affected Asset/Environment/User/External System；
- 已发生副作用、Risk ID/Current Risk Level/Impact、Stop/STC/ESP；
- Immediate Containment、Preserved Evidence；
- Retry Attempts、参数变化和结果；
- Rollback/Compensation 和验证；
- Root Cause Status、Owner、Due、Escalation；
- Resolution、Residual Risk、Close/Reopen Condition；
- State 和 History。

### 13.9 Human Review Record

HRR 必须包含：

- HRR ID、Reviewed RUN/AEP/Context/Snapshot；
- CAS/CCS/VDR/FER/RRS/Diff/Commit；
- Reviewer Identity/Role/Authority/Independence；
- Review Scope、Method、Time；
- Requirement/Scope/Change/Command/Validation/Failure/Risk 检查；
- Evidence 和 Finding；
- Review Outcome、整改、Owner、Due；
- Acceptance/Rejection Authority 和理由；
- Follow-up Run/Review、失效条件；
- State 和 History。

### 13.10 Residual Risk Statement

RRS 必须包含：

- RRS ID、Run/Release/Asset/Environment Scope；
- Risk ID/Description/Category/Current Level；
- Cause、Impact、Likelihood 来源和 Evidence；
- 已执行控制、验证和控制局限；
- Residual Risk、未验证项和 Failure；
- Treatment、Acceptance Condition 和 Alternative；
- Risk Owner、Approval Authority、Decision；
- Monitoring Metric/Trigger、Review Due、Expiry；
- C02/C12 Risk Acceptance 引用；
- State、Supersession 和 History。

## 14. 质量要求

九类产物必须同时满足：

1. 完整：适用实例和必填信息无缺口；
2. 真实：只记录实际观察、调用、变更和结果；
3. 可重建：Run、Step、Action、Attempt、ECP Revision、Snapshot、命令和 Evidence 可恢复；
4. 可授权：每个 Action 可关联 Scope、Permission、Approval 和 Stop；
5. 可追踪：每项变更关联 Requirement/Change、Asset Revision、Diff 和 Validation；
6. 原子：副作用、权限和失败不可分时拆分 Action/TIL；
7. 失败保真：Fail、Blocked、Retry、Rollback 和反对 Evidence 不被覆盖；
8. 验证充分：Expected、Actual、Result、Environment 和 Raw Evidence 可复核；
9. 人机分离：Agent 生成、验证、Human Review、Acceptance 和 Risk Acceptance 分开；
10. 状态准确：DOC/EXEC/REC/CASE/DEC 与非 State 判定不混用；
11. 敏感最小：Secret、PII、受限数据和日志按最小披露处理；
12. 范围受控：Out-of-Scope Observation 只登记不实施；
13. 可恢复：Rollback 有 Target、Authorization、Actual Effect 和验证；
14. 可保留：记录按 E04/义务分类、访问、更正和处置；
15. 无虚假符合：不声明私有推理捕获、未执行测试或完整标准认证。

## 15. 评审、批准与 Run 接受

### 15.1 评审顺序

1. Plan Author/Agent 自检 AEP；
2. Requirement/Scope Owner 核对来源和边界；
3. C07 Authorization Owner 核对 Operation、Permission、Approval 和 Stop；
4. C08 Context Owner 核对 ECP/SCM/Fingerprint；
5. Tool/Environment Owner 核对 Tool、Identity、Permission、Snapshot 和日志；
6. Validation Reviewer 核对 Method、Expected/Actual、Result 和 Evidence；
7. Security/Privacy/Compliance Reviewer 核对敏感与外部影响；
8. Independent Reviewer 核对 RUN、CAS/CCS、VDR、FER 和 RRS；
9. Human Review Authority 决定 HRR Accepted/Rejected；
10. C10/C11/C12 处理 Trace、Baseline、Change、Gate 和 Risk Acceptance。

### 15.2 RUN Ready 条件

只有全部满足时 RUN 可以进入 Ready：

- AEP 为 Approved/Baselined 且绑定当前 RUN；
- C02 Scope/Risk/Operation Boundary 当前有效；
- C07 Agent Role、Authorization、Permission、Approval、Stop 和 ESP 当前有效；
- C08 Context Ready、ECP/SCM/CPP/CFR 和 Fingerprint 当前有效；
- Requirement、Design、Acceptance 和 Snapshot Revision 准确；
- Tool/Environment/Identity/Technical Permission 匹配；
- Verification、Raw Evidence、Failure、Retry、Rollback 和 Retention 可执行；
- Human Accountable、Reviewer 和升级目标明确；
- 无 Blocking Conflict/Finding/Stop。

### 15.3 RUN Completed 条件

只有全部满足时 RUN 可以进入 Completed：

- 所有计划 Step 为 Succeeded/Skipped/Cancelled 且理由完整；
- 所有符合第 8.0 节的重要 Tool Invocation 有连续 RunLedger Event；
- 所有变化在 Git/Evidence 和 TaskOutcome 中可解析；
- 需要审核或 Gate 时 VDR DerivedView 已形成；
- Fail/Blocked/Retry/Rollback 在 RunLedger 和 TaskOutcome 中可解析；
- 未解决项、范围外发现、Residual Risk 和 Writeback 已记录；
- End Snapshot、实际范围、时间和日志完整；
- 未发生未记录副作用或 Evidence 缺口。

验证 Action 已按计划执行但 Verification Result = Fail 时，Run 动作可以 Completed，但不能伪装为成功交付；RUN State 必须依据实际完成条件记录为 Completed、Failed 或 Blocked。

### 15.4 RUN Accepted 条件

RUN 从 Completed 转为 Accepted 必须同时满足：

- HRR State = Accepted，决定者为授权人类；
- HRR 固定当前 RUN/AEP/Context/Snapshot/CAS/CCS/VDR/FER/RRS；
- 必需 Verification Result 满足 C05 要求；
- Blocking Finding、失败、范围外变化和安全事件为零；
- Residual Risk 已由适用 Authority 处置；
- C10 Trace、C11 Change/Baseline 和 C12 Gate 输入已提供；
- 接受范围、条件、失效和后续责任明确。

### 15.5 阻断条件

以下任一情况必须 Blocked/Failed/Rejected：

- Run/Step/Action/Attempt 身份缺失或复用；
- AEP 未批准、Scope/Context/Authorization/Snapshot 过期或冲突；
- Permission 为 Prohibited/Not Assessed，或 Approval 缺失；
- 实际 Command、Working Directory、Target、Tool/Identity 或参数不明；
- 破坏性/外部操作使用宽泛目标、未解析变量或未知副作用；
- 重要 Tool Invocation、Failure、Retry、Rollback、Diff 或必需 Evidence 未记录；
- 变化无 Requirement/Engineering Change 来源；
- 必需验证未执行、Expected/Actual 缺失或虚构 Pass；
- 敏感信息进入命令、日志、Diff 或外部供应商；
- Agent 自批、接受 Risk 或把 Completed 当 Accepted；
- 多 Agent 共享写入冲突未解决；
- 无法重建主要副作用、TaskContract Revision 或 End Snapshot。

## 16. 变更、审计与保留

### 16.1 Plan 与 Run 变更

AEP Approved 但未 Baselined 的变化必须建立新 Revision、差异、原因、影响和重新批准。Baselined AEP 或正式 Scope/Requirement/Design/Context/Snapshot 变化必须转 C11 Change Request。

Run 中变化至少影响：Step、Action、Tool、Command、Target、Permission、Approval、Context、Snapshot、Validation、Failure、Retry、Rollback、Sensitive、Risk、CAS/CCS、HRR 和 Gate。实质变化发生前必须 Stop。

### 16.2 审计历史

以下记录必须按适用 Retention Rule 保留；正式 Run、批准、变更、验证、失败、复核和风险记录禁止无痕删除：

- AEP 每个 Revision、理解摘要、批准和差异；
- RUN 每个 State、Step/Action/Attempt、时间和 Context/Snapshot；
- 每个 TIL 的调用、权限、输入输出、Exit 和 Raw Log 引用；
- CAS/CCS 的 Old/New、Diff、Commit、Impact 和 Validation；
- VDR 的 Expected/Actual/Result、Raw Evidence 和局限；
- FER 的失败、Retry、Rollback、根因、升级和关闭；
- HRR 的 Reviewer、Finding、接受/拒绝和独立性；
- RRS 的 Risk、控制、Decision、监控、失效和替代；
- Redaction、Access、Retention、Correction、Supersession 和 Disposal。

### 16.3 Evidence 完整性

1. Raw Log、Diff、Artifact、Manifest、Screenshot 或外部响应必须记录 Locator、Digest/版本、Producer、时间和 Access。
2. Timestamp 必须说明 Time Zone 和来源；时钟不同步时记录偏差。
3. 摘要、转码、压缩、过滤、采样和脱敏必须保留转换链及遗漏。
4. REC 更正不得修改原记录；使用 Corrected 并保留 Before/After。
5. Evidence 不可获得时必须记录原因、影响和 Blocked/限制，禁止补写推测内容。

### 16.4 保留与处置

1. Retention Rule 必须引用 E04、合同、合规、Risk、事故调查、供应商和存储限制。
2. 全部日志永久保存禁止作为默认规则。
3. 敏感原文到期后必须按批准规则删除、匿名化或隔离，并保留最小审计记录。
4. Legal Hold、调查、争议、Incident 或 Gate 需要时禁止处置。
5. 外部 Tool/供应商日志不能满足保留义务时，必须在执行前建立允许的替代 Evidence。
6. 处置必须记录对象、范围、Authority、时间、方法、验证和不可恢复影响。

## 17. P2 裁剪与扩展适用性

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C09 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

实际 Agent 变更任务必须具有 TaskContract 和 RunLedger；计划深化通过 TaskContract Amendment 更新，不创建第二份“执行方案”。重要运行事件进入 RunLedger，CAS/CCS/FER 语义进入 TaskOutcome；HRR/RRS 只在实际人类复核或剩余风险事件发生时 `On Event` 创建。

TaskOutcome 是任务级实际变化和遗留问题的事实源；存在代码变化时记录 CCS 兼容语义并引用 Git Diff。VDR 按 Run 汇总 VER/VAE、RunLedger 和 Git，仅作为 `Derived View / On Demand`，不得替代原始 Evidence。

### 17.1 当前 P2 档位

1. AEP、RUN、TIL、CAS、CCS、VDR、FER、HRR、RRS 九个旧 Profile 代码全部保留用于兼容，不再作为九类顶层产物。
2. 旧 Profile 的 State、Owner、Revision/记录身份、Trace 和 History 在元类型载体中必须可区分。
3. 无 Tool/Change/Failure/Risk 时可不创建相应实例，但不得删除类型、触发规则和模板。
4. Run ID、重要 Event、实际变更、验证、失败、Human Review、Residual Risk、Sensitive 和 Retention 不得裁剪；普通读取、搜索、完整命令和完整输出默认不记录。
5. 聚合页面、数据库表或流水线视图可以联合展示，但必须导出独立逻辑产物。

### 17.2 未来档位

P1/P2 可以通过 TaskContract、RunLedger、TaskOutcome 和 DerivedView 联合展示旧 Profile 语义，但必须保留 Run/Event/Asset ID、关键动作、Evidence、Failure、Risk、State 和逻辑身份。HRR、RRS 在触发时仍需独立权威记录。

P3 可以增加策略即代码、隔离 Runner、签名日志、不可变存储、自动 Provenance、连续验证、异常检测和实时 Trace，但不得取消人类接受、Risk Authority、失败保留或敏感最小化。

### 17.3 扩展适用性

| 扩展 | 触发条件 | C09 附加接口 |
|---|---|---|
| E01 Architecture Governance | 多系统、关键架构、迁移、质量属性或架构一致性 | Architecture Decision/View/Fitness/Conformance 执行 Evidence |
| E02 Security/Privacy/Compliance | 身份、敏感、个人、密钥、外部威胁、监管或安全验证 | Security Plan、Threat/Privacy、Scan、Vulnerability、Incident、专业 Stop |
| E03 Data/AI Data Governance | Dataset、Corpus、RAG、训练/评估、数据质量或模型 | Data Contract、Lineage、Dataset/Model Version、Quality/Bias Evidence |
| E04 Knowledge/Records | Provenance、长期记录、审计、保留、新鲜度和历史恢复 | RCS、RTS、SPR、记录捕获、更正、访问和处置；当前规范仓库已激活 |
| E05 Operations/Service | 生产、SLO、发布、灰度、监控、Incident 或恢复 | Runbook、Change Window、Deploy/Observe/Rollback、Incident Evidence |

当前规范仓库 E04 已激活；E01、E02、E03、E05 未激活。具体目标产品必须重新判定，不能继承本仓库结论。

## 18. 上下游交接

| 规范 | C09 接收 | C09 输出 |
|---|---|---|
| C01 | Product/Need/Goal/Evidence Revision | 实际执行和发现的观察 |
| C02 | Scope、Risk、Constraint、八类 Operation Boundary | Actual Operation、Stop、Failure、Residual Risk |
| C03 | PRD、Feature、Scenario、Non-goal | Feature/Scenario 实现与验证事实 |
| C04 | Requirement、Revision、Engineering Change、Conflict | CAS/CCS、实现来源和范围外发现 |
| C05 | Criterion、Strategy、Test/Check、VER/VAE/Acceptance | VDR、TIL、Raw Evidence 和未验证项 |
| C06 | Design、Interface、Data/State、Failure、Permission、Rollback | Actual Change、行为影响和设计偏差 |
| C07 | Agent Role、Authorization、Permission、Approval、Stop、ESP、Resume | 实际 Action、Approval Use、Stop/Resume Evidence |
| C08 | SCM/ECP/CPP/CFR、Fingerprint、Delta Policy | 每 Step ECP Revision、Tool Result 和 Context Delta 原始事实 |
| C10 | Decision/Trace/Lineage 规则 | RUN/CAS/CCS/VDR/FER/HRR/RRS 候选链接 |
| C11 | Asset/Revision/Snapshot/Baseline/Change/Release Configuration | Actual Diff/Commit/Artifact、Untracked Change 和 End Snapshot |
| C12 | Gate、Risk Acceptance、Exception、Release 条件 | Human Review、Validation、Failure、Residual Risk 和 Readiness Evidence |
| E04 | Classification、Provenance、Access、Retention、Correction/Disposal | Run 记录、Raw Log、Evidence 和 History |

C10/C11/C12 必须消费准确 Revision 和 State。C09 变化使既有 Trace、Baseline、Gate 或 Review 失效时必须通知并阻断沿用。

## 19. 符合性检查

### 19.1 检查方法

使用一个固定 Requirement/Scope、C07 Authorization、C08 ECP、AEP、Workspace Snapshot 和代表性 Run，检查身份、命令、工具、权限、变更、验证、失败、复核、风险、敏感和重建。检查结果使用 Review Record，不直接提升正式产物 State。

### 19.2 强制检查项

1. 九类正式产物是否保留独立身份；
2. 通用必填信息是否完整；
3. Run ID 是否唯一且未复用；
4. Step/Action/Attempt 是否具有成员 ID；
5. Parent/Child Run 是否独立授权和记录；
6. Requirement/Scope/Risk/Operation Boundary 是否固定；
7. C07 Agent Role/Authorization/Permission/Approval/Stop 是否有效；
8. C08 ECP/SCM/CPP/CFR/Fingerprint 是否固定；
9. Workspace/Commit/Dirty/Untracked/Environment Snapshot 是否固定；
10. Understanding Summary 是否覆盖 Fact/Assumption/Unknown/Conflict/Non-goal；
11. 是否未记录或声称记录私有思维链；
12. AEP 是否在执行前 Approved/Baselined；
13. AEP Step/Action/Tool/Target/Validation/Rollback 是否完整；
14. Operation Type 是否复用 C02 八类；
15. Permission Class 是否复用 C07 四类；
16. High/Critical/Delete/External Mutation/Deploy 是否具有批准；
17. Tool/Version/Identity/Technical Permission 是否可定位；
18. Tool 默认行为、缓存、重试和副作用是否可知；
19. 每个重要 Tool Invocation 是否有独立 RunLedger Event；
20. Event Sequence、Time、摘要、Exit、Evidence 和脱敏说明是否完整；
21. 需要保存的实际命令是否与计划/显示命令分离；
22. Shell/Runtime、Argument、Working Directory、Environment、Timeout 是否完整；
23. Secret Value 是否未进入命令和日志；
24. 未信任输入是否未通过字符串拼接进入命令；
25. 不可判定复合命令是否已拆分；
26. 破坏性 Target 是否精确且无宽泛根/未解析变量；
27. External Mutation 是否有幂等/补偿控制；
28. Command Replay 是否未被解释为再次执行授权；
29. Action 前后 Snapshot 和 Actual Effect 是否比较；
30. 非本 Run 变化是否未被错误归因；
31. 每个变化是否在 TaskOutcome 和 Git/Evidence 中可解析；
32. 适用代码/配置变化是否具有 CCS 兼容语义；
33. 变化摘要是否关联 Requirement/Engineering Change；
34. Commit/PR/Diff 与行为影响、验证和遗留问题是否同时可解析；
35. VDR 是否记录 Method/Environment/Command/Expected/Actual/Result；
36. VDR 是否保留 Raw Evidence、未验证项和局限；
37. Exit Code/Tool Success 是否未自动等同 Pass；
38. C09 VDR 是否未替代 C05 VER/VAE/Acceptance；
39. Fail/Blocked/Stop/Retry/Rollback 是否有 FER；
40. 后续成功是否未覆盖原失败；
41. Retry 是否创建新 Attempt 并检查副作用/幂等；
42. Retry 上限是否来自 AEP/Risk/Authorization；
43. Rollback 是否单独授权、记录和验证；
44. 用户/并行 Agent 变化是否未被默认回滚；
45. HRR 是否固定 Run/Change/Evidence Revision；
46. HRR Accepted/Rejected 是否由授权人类决定；
47. Agent 是否未自批或接受 Residual Risk；
48. RRS 是否具有控制、Owner、监控和失效；
49. High/Critical Risk 是否路由 C02/C12；
50. 状态回写是否未越过事实源；
51. 范围外发现是否只登记未实施；
52. 多 Agent 是否独立 Run、Context、Authorization 和 Evidence；
53. Access、Redaction、Retention、Correction 和 Disposal 是否完整；
54. 是否能重建主要副作用、TaskContract Revision、Diff 和验证；
55. 是否不存在虚构模型版本、测试结果或完整标准符合声明。

### 19.3 不符合处理

1. 越权、破坏性目标不明、实际命令缺失、Evidence 伪造、敏感泄漏、Failure 覆盖和不可重建属于 Blocking Finding。
2. 正在运行时发现上述问题必须立即执行 C07 Stop。
3. Finding 必须记录 Owner、期限、受影响 Run/Asset/Requirement/Risk/Gate 和复核结果。
4. 高风险 Finding 不能由生成该 Run 或变更的 Agent 自行关闭。
5. 修复必须形成新 Attempt/Run/Revision、实际 Evidence 和新 HRR，不得修改历史制造通过。

## 20. 附录

### 20.1 通用资产头模板

```markdown
| 信息项 | 内容 |
|---|---|
| Asset ID | <TYPE>-<NNNN> |
| Artifact Type | <正式产物名称>（<TYPE>） |
| Name or Summary | |
| Purpose | |
| Source | |
| Owner | <明确人类> |
| State | <对应公共状态模型值> |
| Current Revision | |
| Created and Updated | |
| Applicable Scope | |
| Trace Links | |
| Access Classification | 公开 / 内部 / 机密 / 受限 |
| Retention Rule | |
| History Reference | |
```

### 20.2 Agent Execution Plan 模板

```markdown
# AEP-<NNNN> <Task / Run>

<通用头部；State 使用 DOC>

| Run / Task / Human Accountable | |
|---|---|
| Requirement / Scope / Risk / Operation Boundary | |
| C07 Role / Authorization / Permission / Approval / Stop / ESP | |
| C08 SCM / ECP / CPP / CFR / Fingerprint | |
| Design / Acceptance / Verification | |
| Workspace / Environment / Commit / Dirty State / Config / Data Snapshot | |
| Understanding Summary | |
| Fact / Assumption / Unknown / Conflict / Non-goal | |
| Maximum Change Scope | |
| Sensitive / Secret / Network / External Boundary | |
| Failure / Retry / Rollback / Cleanup | |
| Reviewer / Approval / Handoff / Writeback | |

| Step ID | Objective | Input / Dependency | Operation / Target | Tool / Command | Permission / Approval | Expected Effect | Validation / Evidence | Rollback | Stop / Exit |
|---|---|---|---|---|---|---|---|---|---|
| RUN-<NNNN>-S001 | | | | | | | | | |
```

### 20.3 Agent Run Record 模板

```markdown
# RUN-<NNNN> <Task>

<通用头部；State 使用 EXEC>

| Parent / Child / Agent Role / Instance / Human Accountable | |
|---|---|
| Model / Engine / Orchestrator / Tool Identity | |
| Start / End / Blocked / Resume / Cancel / Failure Time | |
| Requirement / Scope / Risk / Design / Acceptance / AEP | |
| SCM / ECP / CPP / CFR / Fingerprint / Delta | |
| Workspace / Environment / Snapshot Before / After | |
| Understanding Summary / Actual Deviation | |
| CAS / CCS / VDR / FER / HRR / RRS | |
| Unresolved / Observation / Out-of-Scope | |
| Writeback / Handoff / Final State | |

| Step / Action / Attempt | ECP Revision | Operation / Target | Permission / Approval | TIL / Command | Actual Effect | CAS / CCS | Validation | Failure / Retry / Rollback | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
```

### 20.4 Tool Invocation Log 模板

```markdown
# TIL-<NNNN> <Tool Invocation>

<通用头部；State 使用 REC>

| Run / Step / Action / Attempt / Sequence | |
|---|---|
| Tool / Version / Provider / Service / Identity | |
| Operation / Permission / Approval / Target | |
| Shell / Runtime / CLI | |
| Actual Invocation Structure / Redacted Arguments | |
| Arguments / Input / stdin / Redirection / Pipeline | |
| Working Directory / Environment Snapshot | |
| Environment Variable Names / Secret Reference | |
| Timeout / Resource / Network / Concurrency | |
| Start / End / Exit Code / Status / Signal | |
| Output Summary / Error Summary | |
| Raw Log Locator / Digest / Access / Retention | |
| Actual Effect / Produced Artifact / Follow-up Validation | |
| Sensitive / Redaction / Correction / History | |
```

### 20.5 Changed Artifact Summary 模板

```markdown
# CAS-<NNNN> <Asset Change>

<通用头部；State 使用 REC>

| Run / Action / TIL | |
|---|---|
| Asset ID / Type / Owner / Locator | |
| Old Revision / Snapshot / State | |
| New Revision / Snapshot / State | |
| Change Type / Summary / Reason / Producer | |
| Requirement / Engineering Change / Design / Decision | |
| Diff / Manifest / Digest / Commit | |
| Behavior / Data / Interface / Access / Retention Impact | |
| Downstream Impact / Validation / Rollback | |
| Correction / Supersession / History | |
```

### 20.6 Code Change Summary 模板

```markdown
# CCS-<NNNN> <Code Change>

<通用头部；State 使用 REC>

| Run / Repo / Base Commit / Result Commit / Branch / Dirty State | |
|---|---|
| File / Component / Module / Change Type | |
| Code Change / Behavior Impact | |
| Requirement / Design / Decision / Engineering Change | |
| Interface / Data / Security / Performance / Compatibility | |
| Dependency / Lockfile / Generated / Migration / Config | |
| Test / Static / Build / Scan / VDR / VER | |
| Deployment / Migration / Rollback / Operational Impact | |
| Reviewer / Diff / PR / Commit / History | |
```

### 20.7 Validation Report 模板

```markdown
# VDR-<NNNN> <Validation Scope>

<通用头部；State 使用 DOC>

| Run / Owner / Reviewer | |
|---|---|
| Requirement / Criterion / Strategy / Test / Check | |
| Subject / Revision / Snapshot / Environment / Tool | |
| Coverage / Freshness / Recheck | |

| Check ID | Method | Command / TIL | Input / Oracle | Expected | Actual | Result | Raw Evidence | Limitation / Unverified | Reviewer |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | Pass / Fail / Blocked | | | |

| C05 VER / VAE / VCM / ACD | |
|---|---|
| Conclusion / Required Action | |
```

### 20.8 Failure or Exception Report 模板

```markdown
# FER-<NNNN> <Failure / Exception>

<通用头部；State 使用 CASE>

| Run / Step / Action / Attempt / Category | |
|---|---|
| Detection Time / Detector / Symptom | |
| Expected / Actual / Exit / Tool State | |
| Error Evidence / Raw Log | |
| Affected Asset / Environment / User / External System | |
| Side Effect / Risk ID / Current Risk Level / Impact / Stop / ESP | |
| Immediate Containment / Preserved Evidence | |
| Retry Attempts / Parameter Change / Result | |
| Rollback / Compensation / Validation | |
| Root Cause Status / Owner / Due / Escalation | |
| Resolution / Residual Risk / Close / Reopen | |
```

### 20.9 Human Review Record 模板

```markdown
# HRR-<NNNN> <Run Review>

<通用头部；State 使用 EXEC>

| Reviewed RUN / AEP / Context / Snapshot | |
|---|---|
| CAS / CCS / VDR / FER / RRS / Diff / Commit | |
| Reviewer Identity / Role / Authority / Independence | |
| Review Scope / Method / Time | |
| Requirement / Scope / Actual Change / Command Review | |
| Validation / Failure / Sensitive / Risk Review | |
| Evidence / Finding / Review Outcome | |
| Remediation / Owner / Due | |
| Acceptance / Rejection Authority / Reason | |
| Follow-up Run / Review / Invalidation | |
```

### 20.10 Residual Risk Statement 模板

```markdown
# RRS-<NNNN> <Residual Risk>

<通用头部；State 使用 DEC>

| Run / Release / Asset / Environment Scope | |
|---|---|
| Risk ID / Description / Category / Current Level | |
| Cause / Impact / Likelihood Source / Evidence | |
| Implemented Control / Validation / Limitation | |
| Residual Risk / Unverified / Failure | |
| Treatment / Acceptance Condition / Alternative | |
| Risk Owner / Approval Authority / Decision | |
| Monitoring Metric / Trigger / Review Due / Expiry | |
| C02 / C12 Risk Acceptance / Supersession | |
```

### 20.11 Preflight 判定表

| 检查 | 通过 | 不通过 |
|---|---|---|
| Requirement/Scope/Risk/Operation Boundary 当前有效？ | 继续 | Blocked |
| C07 Role/Authorization/Permission/Approval 当前有效？ | 继续 | Stop/Blocked |
| C08 ECP/SCM/Fingerprint 当前有效？ | 继续 | Stop/Blocked |
| Snapshot/Dirty/Untracked/Environment 可重建？ | 继续 | Blocked |
| Tool/Identity/Permission 与 AEP 一致？ | 继续 | Stop |
| Validation/Raw Evidence 可执行？ | 继续 | Blocked |
| Failure/Retry/Rollback/Stop 完整？ | 继续 | Blocked |
| Sensitive/Secret/External 边界清楚？ | 继续 | Stop |
| 无 Blocking CCF/Finding/Stop？ | RUN Ready | Blocked |

### 20.12 命令记录速查表

| 命令面 | 最低记录 | 禁止 |
|---|---|---|
| Identity | TIL/Action/Attempt、Tool/Runtime/Version | 只写“运行脚本” |
| Invocation | 原始命令或参数化调用、Argument 顺序 | 用计划命令冒充实际调用 |
| Location | 受控工作目录、Target、Snapshot | 模糊目录、未知租户 |
| Permission | Operation、Permission、Approval、Stop | 技术可用等于授权 |
| Environment | 环境、配置、变量名、Secret Reference | 明文 Secret |
| Control | Timeout、资源、网络、并发、幂等 | 未知自动重试 |
| Result | Start/End、Exit/Signal、stdout/stderr、Actual Effect | Exit 0 等于验证通过 |
| Evidence | Raw Log、Digest、CAS/CCS、VDR | 仅保留摘要 |

### 20.13 Retry 与 Rollback 判定表

| 情况 | Retry | Rollback | 强制动作 |
|---|---|---|---|
| 幂等、无副作用、参数不变、授权有效 | 按 AEP 新 Attempt | 不需要 | 保留原失败 |
| 副作用未知或外部状态未知 | 禁止自动 Retry | 先诊断 | FER、Stop |
| 需要扩大 Scope/参数/权限 | 禁止 | 禁止 | 修订 AEP/重新批准 |
| 验证失败但变化可定位 | 按 AEP | 按批准策略 | 新 Attempt/TIL/VDR |
| 用户/并行 Agent 变化存在 | 禁止覆盖 | 禁止默认回滚 | 隔离、协调 |
| Rollback 部分失败 | 不得声称恢复 | 记录实际结果 | FER/RRS/升级 |
| RUN 已终端 | 建立新 RUN | 新 RUN 中授权 | 回链原 RUN |

### 20.14 质量检查清单模板

```markdown
| Check ID | 检查对象 | 通过条件 | 结果 | Evidence / Finding |
|---|---|---|---|---|
| C09-CHK-001 | 九类产物 | ID、State、Owner、History 独立 | 待检查 | |
| C09-CHK-002 | Preflight | Scope/Authorization/Context/Snapshot/Tool 全部有效 | 待检查 | |
| C09-CHK-003 | Understanding | Fact/Assumption/Unknown/Conflict/Non-goal 完整 | 待检查 | |
| C09-CHK-004 | AEP | Step/Action/Tool/Validation/Rollback 可执行 | 待检查 | |
| C09-CHK-005 | Command | 实际调用、参数、目录、环境、退出和日志完整 | 待检查 | |
| C09-CHK-006 | Permission | 八类操作和四类 Permission 正确 | 待检查 | |
| C09-CHK-007 | High Impact | Target、Approval、Snapshot、Rollback、Validation 完整 | 待检查 | |
| C09-CHK-008 | TIL | 每次 Invocation 独立且 REC 不可变 | 待检查 | |
| C09-CHK-009 | Change | CAS/CCS、来源、Diff、Impact 完整 | 待检查 | |
| C09-CHK-010 | Validation | Expected/Actual/Result/Raw Evidence 完整 | 待检查 | |
| C09-CHK-011 | Failure | Fail/Retry/Rollback 未覆盖 | 待检查 | |
| C09-CHK-012 | Human Review | 固定 Revision、独立性、接受 Authority 完整 | 待检查 | |
| C09-CHK-013 | Sensitive | 无明文 Secret，Redaction/Access/Retention 完整 | 待检查 | |
| C09-CHK-014 | Reconstruction | Run/Step/ECP/Snapshot/Command/Diff 可重建 | 待检查 | |
| C09-CHK-015 | P2/E04 | 未裁剪；记录接口和目标产品重评完整 | 待检查 | |
```

### 20.15 正反例

正例：

> RUN-0043 绑定 AEP-0043 Revision 2、REQ-031 Revision 4、ECP-0043 Revision 3、Commit `abc123` 和 ARD/APM 当前授权。Action RUN-0043-A003 使用 TIL-0187 记录参数化测试调用、工作目录、超时、Exit Code、stdout/stderr Digest 和实际结果。第一次 Attempt 因依赖超时失败，FER-0012 保留；确认无外部副作用后按 AEP 执行第二次 Attempt。CAS/CCS 固定 Diff 和 Result Commit；VDR 逐项记录 Expected/Actual，HRR 由独立人类基于当前 Revision 接受，未解决低 Risk 进入 RRS。

反例：

> Agent 理解需求后直接改完代码，跑了测试都通过；中间报错已重试解决，日志太长没保存，模型版本应该是最新版，人类看过就算批准。

反例没有 Run/AEP/Context/Authorization/Snapshot、实际命令、TIL、Diff、Expected/Actual、原始 Evidence、Failure/Retry、Human Authority 或 Residual Risk，并包含虚构模型版本和口头批准，禁止进入 RUN Accepted。

### 20.16 参考的国际标准条款映射总表

| 国际标准 | 条款或官方公开项目 | 本规范落地位置 | 采用方式 | 复核限制 |
|---|---|---|---|---|
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | 4.3–4.4 AIMS 范围和体系 | 第 3、8.3、9.2、10.1 章 | 固定 Product/Run/Scope/Environment 边界 | 不构成组织完整 AIMS |
| ISO/IEC 42001:2023 | 5.3 角色、责任与权限 | 第 7、9.3、15.1 章 | 明确 Run/Tool/Evidence/Review/Risk 角色 | 权限模型由 C07 管理 |
| ISO/IEC 42001:2023 | 6.1 风险与机会 | 第 9.7、10.8、10.13–10.14、13.10 章 | 识别越权、失败、泄漏、伪造和未验证风险 | C09 不建立第二 Risk Register |
| ISO/IEC 42001:2023 | 6.3 变更策划 | 第 10.4、10.10–10.11、16.1 章 | Plan/Scope/Context/Tool/Command 变化执行影响分析 | 正式 Change 由 C11 管理 |
| ISO/IEC 42001:2023 | 7.5 文件化信息 | 第 10.9–10.12、13、16 章 | 九类产物控制标识、访问、完整性、保留和历史 | 不保存私有思维链 |
| ISO/IEC 42001:2023 | 8.1 运行策划与控制 | 第 9、10.2–10.9、15 章 | Preflight、AEP、Permission、Action、Evidence 和 Review | 技术 Permission 不等于 Authorization |
| ISO/IEC 42001:2023 | 8.2 AI 风险评估 | 第 10.13、10.18–10.20、13.10 章 | Agent/模型/工具执行风险进入 C02/C12 | 模型置信度不替代风险决定 |
| [ISO/IEC 5338:2023](https://www.iso.org/standard/81118.html) | 5.2–5.4 AI 系统、生命周期和过程概念 | 第 3、6、9、10.1 章 | Run/Step/Input/Output/Evidence 绑定生命周期 | 不建立第二生命周期模型 |
| ISO/IEC 5338:2023 | 6.1 协议过程 | 第 10.6–10.9、13.4 章 | 外部 Tool/Service 记录接受、用途和限制 | 不替代合同或采购 |
| ISO/IEC 5338:2023 | 6.2 组织项目使能过程 | 第 8.3、9.2、16、17.3 章 | 接入质量、知识、配置、风险和资源控制 | 事实源保持独立 |
| ISO/IEC 5338:2023 | 6.3 技术管理过程 | 第 9、10.2–10.5、10.10、16 章 | Plan、Risk、Configuration、Information、Quality 接口 | 公开目录未展开子过程 |
| ISO/IEC 5338:2023 | 6.4 技术过程 | 第 9.4–9.9、10.10–10.16 章 | 按适用生命周期活动记录输入、Action、输出和验证 | 公开目录未展开子过程 |
| ISO/IEC 5338:2023 | Annex A.2–A.3 过程流与控制流数据 | 第 9.6、10.5、10.9、10.19 章 | 记录 Step 顺序、Context Delta 和 Tool Result | Annex A 为观察性内容 |
| [ISO/IEC 23894:2023](https://www.iso.org/standard/77304.html) | 4 AI 风险管理原则 | 第 7、9.3、10.2、14 章 | 执行基于当前 Evidence、透明边界和人类责任 | 不建立平行原则集 |
| ISO/IEC 23894:2023 | 5.3–5.7 整合、设计、实施、评价、改进 | 第 9、10、15、16 章 | 风险控制嵌入计划、执行、验证、复核和整改 | 不复制组织风险框架 |
| ISO/IEC 23894:2023 | 6.2 沟通与协商 | 第 10.13–10.16、13.8–13.10 章 | Stop、Failure、Risk、Finding 和结果升级 | 报告不等于批准 |
| ISO/IEC 23894:2023 | 6.3 范围、情境和准则 | 第 9.2、10.1–10.4、15.2 章 | 固定 Scope、Context、Risk、Permission 和完成准则 | 禁止模糊执行边界 |
| ISO/IEC 23894:2023 | 6.4–6.5 风险评估与处置 | 第 10.2、10.8、10.13–10.14、13.10 章 | 检查风险变化、控制失败、Retry 和 Rollback | C09 不计算第二 Risk 分值 |
| ISO/IEC 23894:2023 | 6.6–6.7 监测/评审、记录/报告 | 第 10.9–10.15、16 章 | TIL/RUN/VDR/FER/HRR 保存实际观察和评审 | 失败不得被成功覆盖 |
| [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html) | 1 Scope | 第 3–4、8.3、18 章 | 覆盖软件生命周期中的 Agent Run | 不规定具体方法 |
| ISO/IEC/IEEE 12207:2026 | 4.3 Tailored conformance | 第 17 章 | P1/P2/P3 裁剪保留必要过程结果 | 不声明 12207 符合 |
| ISO/IEC/IEEE 12207:2026 | 5.4–5.8 生命周期、过程和应用概念 | 第 6、8、9、10.1–10.5 章 | Run 映射阶段、过程、输入、活动和输出 | 不复制付费正文 |
| ISO/IEC/IEEE 12207:2026 | 6.2 组织项目使能过程 | 第 8.3、9.2、16、17.3 章 | 接入质量、知识、基础设施和资源约束 | 原规范保持事实源 |
| ISO/IEC/IEEE 12207:2026 | 6.3 技术管理过程 | 第 9、10.2–10.5、10.10–10.12、16 章 | AEP/RUN 接入计划、风险、配置、信息和质量 | 公开目录未展开子过程 |
| ISO/IEC/IEEE 12207:2026 | 6.4 技术过程 | 第 9.4–9.9、10.10–10.16 章 | 按 AEP 记录适用技术活动的实际输入、动作、输出和验证 | 公开目录未展开子过程；详细对应需合法全文 |
| ISO/IEC/IEEE 12207:2026 | Annex A Tailoring process | 第 17.1–17.2 章 | 裁剪记录选择、理由、影响和批准 | P2 九类身份不裁剪 |
| [IEEE 1012-2024](https://standards.ieee.org/ieee/1012/7324/) | Active Standard；Superseding 1012-2016 | 第 1、16、20.16 章 | 使用当前标准标识与官方状态 | 编号年份和发布日期分别记录 |
| IEEE 1012-2024 | 官方 Scope：符合活动要求与满足预期用途 | 第 8.4、10.12、15.3–15.4 章 | 区分 Verification、Validation、Completion 和 Acceptance | C05 管理 VER/VAE/ACD |
| IEEE 1012-2024 | 官方 Scope：分析、评价、评审、检查、评估和测试 | 第 10.12、10.15、13.7、13.9 章 | VDR/HRR 记录方法、Evidence、Finding 和 Result | 不以“已测试”替代 Evidence |
| IEEE 1012-2024 | 官方公开过程组概述 | 第 3、9、17.3、18 章 | Run 按生命周期与过程组分类 | 官方页未公开完整目录，不推断条款号 |
| [ISO 15489-1:2016](https://www.iso.org/standard/62542.html) | 4 记录管理原则 | 第 8、10.9–10.15、16 章 | Run、调用、变化、失败和复核记录可重建 | 不覆盖组织全部记录 |
| ISO 15489-1:2016 | 5.2–5.3 记录与记录系统 | 第 6、8.1、10.9、16.2–16.3 章 | 区分 Event、REC、Raw Log、Summary 和系统 | 摘要不替代原日志 |
| ISO 15489-1:2016 | 6.2–6.5 政策、责任、监测、能力 | 第 7、9、15、16 章 | 定义 Owner、Custodian、Reviewer 和监测 | 不建立组织培训体系 |
| ISO 15489-1:2016 | 7.2–7.5 记录鉴定 | 第 9.2、10.17、16.2–16.4 章 | 按 Risk、义务、用途和重建需要保留 | 禁止默认全部日志永久保存 |
| ISO 15489-1:2016 | 8.2 记录元数据 Schema | 第 10.9–10.11、13、20.1–20.10 章 | 记录 ID、Actor、Time、Source、Version、Access 和 History | 不规定物理 Schema |
| ISO 15489-1:2016 | 8.3–8.4 分类、访问与权限 | 第 5.2、10.17、16.4、17.3 章 | 类型、敏感、访问、保留和处置受控 | 公开预览止于 8.4 |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) | 4.1–4.4 情境、相关方、范围和 ISMS | 第 3、9.2、10.6–10.8、10.17 章 | 固定系统、租户、环境、供应商和义务边界 | 不构成完整 ISMS |
| ISO/IEC 27001:2022 | 5.3 角色、责任与权限 | 第 7、10.6、10.15、15.1 章 | Agent、Run、Tool、Evidence、Review 责任明确 | Authorization 由 C07 管理 |
| ISO/IEC 27001:2022 | 6.1 信息安全风险与机会 | 第 10.8、10.13、10.17、13.10 章 | 未授权命令、泄漏、篡改、越权重试进入 C02 Risk | C09 不建立安全风险量表 |
| ISO/IEC 27001:2022 | 7.5 文件化信息 | 第 10.7、10.9、10.17、13、16 章 | 控制访问、版本、完整性、分发、保留和更正 | 明文凭据禁止记录 |
| ISO/IEC 27001:2022 | 8.1 运行策划与控制 | 第 9.3–9.7、10.2、10.6–10.9、15 章 | 命令按 Scope、Environment、Approval 和 Stop 执行 | 不推断未公开 Annex A 编号 |
| [ISO/IEC 27001:2022/Amd 1:2024](https://www.iso.org/standard/88435.html) | 4.1、4.2 气候变化相关性和相关方要求 | 第 9.2、17.3、18 章 | 上游已判定适用时进入 Run Context/Constraint | C09 不重复识别气候风险 |
