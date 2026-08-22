# C10 决策、追踪与资产血缘规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C10 |
| 英文名称 | Decision, Traceability and Asset Lineage Specification |
| 正式文件名 | `C10_Decision_Traceability_and_Lineage_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3、C02 V6.3、C03 V6.3、C04 V6.3、C05 V6.3、C06 V6.3、C07 V6.3、C08 V6.3、C09 V6.3 |
| 生产前调研 | RVR-C10-0001 |
| 下游规范 | C11、C12、E01 至 E05 |
| 横向适用 | C01 至 C09 的 Decision、Trace、Coverage 和 Lineage |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule 保留；正式 Decision、Trace Link、影响查询、孤立项、无来源变更、批准、替代、更正和审计历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式基线、Gate 通过依据或自动状态写入授权。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品、Requirement、UX、技术、架构、Agent 执行和治理决策的记录方式，以及受控资产之间的来源、派生、细化、约束、设计、实现、验证、确认、生成、观察、替代、影响和发布关系。

本规范用于实现以下控制目标：

1. 使重大选择能够回答“为何决定、比较过什么、影响什么、由谁批准”；
2. 使每项正式关系具有唯一 Link ID、明确方向、语义、依据、端点 Revision 和有效边界；
3. 使 Requirement 能向上追到 Need、Intent、PRD 或 Feature，向下追到 Design、Implementation、Verification 和 Release；
4. 使同一权威 Link 集合支持正向和反向查询，避免双份矩阵漂移；
5. 使 Coverage 的集合、分母、排除、Unknown、阈值和时间点透明；
6. 使资产从来源、派生、生成、实现、验证到发布和替代的 Lineage 可重建；
7. 使 Orphan Artifact、Untracked Change、断链、悬空端点和语义冲突可自动发现；
8. 使 Change、Decision、Baseline、Release 和 Retirement 前能够执行有界、可复核的 Impact Query；
9. 使 Agent 或工具提出的 Link 与经验证的正式 Link 分离；
10. 使 C10 与 C01 至 C09、C11、C12 和 E01 至 E05 保持单一事实源边界。

## 3. 适用范围

本规范适用于：

- 产品、Scope、Requirement、UX、技术、架构、Agent 执行、配置和治理领域的重大 Decision；
- Need、Problem、Intent、Goal、Initiative、PRD、Feature、Requirement、Acceptance、Design、Code、Configuration、Test、Evidence、Agent Run、Change、Baseline、Release 和 Record 之间的 Trace；
- 文档、代码、测试、配置、Schema、Migration、脚本、模型、数据资产、基础设施即代码和发布资产的 Lineage；
- 同一仓库、跨仓库、跨工具、跨环境和跨供应商边界的受控关系；
- 正向追踪、反向追踪、覆盖率、孤立项检测、无来源变更检测和影响分析；
- 人工建立、规则生成、工具导入和 Agent 建议的 Link；
- P2 档位下 8 类 C10 正式产物的身份、状态、必填信息、模板和质量检查；
- E01 至 E05 适用性与 C10 的附加接口。

只要某项 Decision、资产关系或查询结果用于批准、变更、验证、发布、审计或风险判断，即使其载体不是 Markdown 文件，也适用本规范。

## 4. 不适用范围

以下对象的内容和最终状态由其事实源管理：

- Need、Problem、Discovery Evidence、Product Definition、Intent 和 Goal，由 C01 管理；
- Initiative、Scope、Risk、Constraint、Dependency 和 Agent Modification Boundary，由 C02 管理；
- PRD、Feature、Scenario、Release Intent 和 Non-goal，由 C03 管理；
- Requirement 身份、语义、Revision、演进和冲突，由 C04 管理；
- Acceptance Criteria、Verification、Validation、Evidence、Coverage Strategy 和 Acceptance Decision，由 C05 管理；
- UX、技术设计、架构元素、接口、数据/状态、Failure Design 和 Design Review，由 C06 管理；
- Agent Role、Accountability、Authorization、Approval、Prohibition、Stop、Escalation 和 Resume，由 C07 管理；
- Agent Context、Source、Priority、Freshness、Trust、Fingerprint 和 Context Delta，由 C08 管理；
- Agent Run、Command、Tool、Actual Change、Validation Report、Failure 和 Human Review，由 C09 管理；
- Asset、Revision、Snapshot、Baseline、Change Request、Configuration Status 和 Release Configuration，由 C11 管理；
- Review、Gate、Exception/Waiver、Risk Acceptance、Release Readiness 和 Product Health，由 C12 管理；
- Architecture、Security/Privacy/Compliance、Data/AI Data、Knowledge/Records 和 Operations 的扩展控制，由适用 E01 至 E05 管理。

C10 记录上述对象之间的正式关系、Decision rationale 和查询结果，但禁止：

- 用 Trace Link 修改端点资产的内容、状态、Owner 或 Revision；
- 用 Decision Record 替代 Acceptance Decision、Gate Decision、Risk Acceptance Record、Exception or Waiver Record 或 Change Request；
- 用 Coverage 百分比替代 C05 的 Verification/Validation 证据；
- 用 Git Commit、文件路径或文本相似度替代业务 Asset ID；
- 用 Lineage Report 替代 C11 的 Snapshot、Baseline 或 Release Configuration；
- 用 Impact Query 自动批准 Change、扩大 Scope、接受 Risk 或通过 Gate。

## 5. 规范性用语与受控判定

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性示例，不作为符合性判定依据。

### 5.2 领域判定值

以下值不是正式产物 State：

| 字段 | 受控值 |
|---|---|
| Decision Type | `Product`、`Requirement`、`UX`、`Technical`、`Architecture`、`Agent Execution`、`Configuration`、`Traceability`、`Governance` |
| Trace Link Member State | `Proposed`、`Active`、`Suspect`、`Invalid`、`Rejected`、`Retired` |
| Coverage Status | `Covered`、`Partially Covered`、`Not Covered`、`Not Applicable`、`Unknown` |
| Orphan Type | `Missing Upstream`、`Missing Downstream`、`Detached Implementation`、`Detached Evidence`、`Detached Decision`、`Dangling Endpoint` |
| Change Source Status | `Tracked`、`Untracked`、`Contested`、`Unknown` |
| Impact Distance | `Direct`、`Indirect`、`Unknown` |
| Query Completeness | `Complete`、`Partial`、`Indeterminate` |
| Link Establishment Method | `Human Authored`、`Deterministic Rule`、`Imported`、`Agent Proposed` |

Decision 的正式状态只能使用 DEC State。TLR、BTM、RCR 和 ALR 的正式状态只能使用 DOC State。UCR 和 OAR 的正式状态只能使用 CASE State。IQR 的正式状态只能使用 REC State。

### 5.3 判定顺序

发生冲突时按以下顺序判定：

1. 确认 Source/Target 是否是可定位的受控资产；
2. 确认关系是否来自公共受控关系集合；
3. 确认关系方向是否符合公共语义；
4. 确认端点 Revision、Snapshot 和有效范围；
5. 确认建立依据、Authority 和 Evidence；
6. 判定 Trace Link Member State；
7. 计算 Coverage、Lineage 或 Impact；
8. 将 Gap、Unknown、Conflict 路由到 UCR、OAR、Change、Risk 或 Gate；
9. 由授权角色决定批准、补救、替代或关闭。

禁止先以“看起来相关”创建 Active Link，再补写端点、语义或依据。

### 5.4 事实、推断和决定

| 类型 | 允许内容 | 禁止内容 |
|---|---|---|
| Fact | 已存在 Asset、Revision、Run、Diff、Evidence、批准和已验证 Link | 未核验的工具摘要 |
| Inference | 明确标记的候选 Link、潜在影响和待确认 Orphan | 直接写为 Active/Covered |
| Decision | 有权主体批准的选择、条件、影响和有效边界 | Agent 私有推理或无 Authority 结论 |
| Metric | 固定集合、查询规则、时间点和公式的 Coverage | 不披露分母或排除项的百分比 |

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Decision | 对一个明确问题在候选方案中形成的受控选择；包含理由、影响、Risk、Authority 和有效边界 |
| Decision Record | 记录一个 Decision 的背景、问题、候选方案、选择、理由、影响、Risk、参与者、状态和替代关系的正式产物 |
| Trace Link | 一个具有方向和受控语义的 Source Asset—Relationship—Target Asset 关系成员 |
| Trace Link Register | 保存正式 Trace Link、成员状态、版本范围和历史的权威受控集合 |
| Bidirectional Traceability | 从任一端点按同一正式 Link 进行正向和反向查询的能力 |
| Bidirectional Traceability Matrix | 在指定 Snapshot、范围和时间点对 TLR 的双向投影，不是第二 Link 事实源 |
| Coverage | 在定义的适用资产集合上，满足指定关系和质量条件的比例及缺口说明 |
| Asset Lineage | 资产从 Source、Derivation、Generation、Implementation、Verification、Observation、Release 到 Supersession 的可重建链 |
| Orphan Artifact | 在当前 State、阶段和适用规则下缺少强制上游或下游 Link 的资产 |
| Untracked Change | 已发生但没有可证明的 Requirement、Decision、Change、Incident 或其他批准来源的受控资产变化 |
| Impact Query | 从指定资产和 Revision 出发，按关系、方向、深度、范围和时间点遍历并记录影响的只读查询 |
| Suspect Link | 因端点 Revision、Scope、Decision、Change、Rule 或有效期变化而必须重新验证的 Link |
| Dangling Endpoint | Source 或 Target 无法解析到有效 Asset ID、Revision 或允许的外部引用 |
| Semantic Duplicate | Source、关系、Target 和有效范围表达相同治理事实的重复 Active Link |
| Effective Version Range | Link、Decision 或规则适用的产品、资产、Baseline、Release、环境或时间边界 |
| Rationale | 可供 Reviewer 复核的选择依据、权衡和约束；不包含私有思维链 |

MADR、ADR、图数据库 Edge、Issue Link、文件引用和 Git Commit 均可以是实现载体或 Evidence，但只有满足本规范的实例才是正式 C10 对象。

## 7. 角色与职责

| 角色 | 主要职责 | 禁止事项 |
|---|---|---|
| Decision Owner | 定义问题、候选方案、影响、Risk，维护 DEC | 自行批准超出授权的 Decision |
| Decision Authority | 批准、条件批准、拒绝、替代或使 Decision 过期 | 批准未披露重大候选方案或影响的 Decision |
| Traceability Owner | 对产品级 Trace Policy、Coverage Profile 和阈值负责 | 用工具默认值替代批准策略 |
| Trace Steward | 建立、验证、修正、退役 Link，维护 TLR | 激活无端点 Revision 或无依据的 Link |
| Artifact Owner | 确认本资产的 Source、Consumer 和 Revision | 删除不利或被替代 Link 历史 |
| Requirement Owner | 确认 Requirement 的来源、设计、实现、验证和发布适用性 | 把 N/A 当作留空 |
| Configuration/Change Owner | 提供 C11 Revision、Snapshot、Baseline、Change 和 Release Configuration | 用 C10 报告替代 C11 记录 |
| Verification/Validation Owner | 提供 C05 Evidence 和 Result，确认 verified-by/validated-by 目标 | 以 Link 存在声称通过 |
| Agent/Automation Operator | 按授权生成候选 Link、报告和检查结果 | 自行把概率推断激活为正式关系 |
| Records Steward | 按 E04 管理元数据、访问、保留、更正和处置 | 无痕删除 Decision、Link 或查询历史 |
| Independent Reviewer | 独立核对语义、端点、Coverage、Lineage、Impact 和缺口 | 仅审阅生成的百分比而不审阅输入集合 |
| Gate/Release Authority | 在 C12 中消费 C10 Evidence 并作 Gate/Release Decision | 在 C10 内绕过 C12 |

### 7.1 最低职责分离

1. Agent 可以起草 DEC、Proposed Link 和报告，不能在无明确授权时批准自身 Decision 或激活自身推断 Link。
2. Decision Owner 与 Decision Authority 在 High/Critical Risk、外部承诺、安全、隐私、架构边界或不可逆选择中必须分离。
3. Trace Steward 可以修正 Link，不得修改端点资产内容或倒签 Approval。
4. Coverage 生成者与 Gate/Release Authority 必须分离。
5. UCR/OAR Owner 可以提出关闭，不得单独接受 Residual Risk 或通过 Gate。

## 8. 治理对象与关系

### 8.0 V6.3 任务链与元类型追踪

V6.3 的最低任务追踪链为 `ProjectID → WorkItemID → TaskID → RunID → AttemptID`。TaskID 表示子任务，必须显式保存 `ordinal`、`depends_on`、`supersedes` 和 `blocked_by`；顺序号只提供建议顺序，不替代依赖关系。

TaskContract 保存执行前来源和计划关系，RunLedger 保存重要事件和 Evidence 引用，TaskOutcome 保存终态事实及后继 TaskID，ProjectState 只物化有效终态与 AuthorityAsset。跨任务 Agent 默认优先消费 ProjectState 和相关 TaskOutcome；只有定位执行细节时才下钻 RunLedger。DerivedView 禁止成为新追踪事实的唯一来源。

### 8.1 正式产物

| 类型代码 | 正式产物名称 | 状态模型 | 核心用途 |
|---|---|---|---|
| DEC | Decision Record | DEC | 记录一个重大选择、候选方案、理由、影响、Risk 和替代 |
| TLR | Trace Link Register | DOC | 维护正式 Link 的权威集合 |
| BTM | Bidirectional Traceability Matrix | DOC | 在固定 Snapshot 上双向展示 Link |
| RCR | Requirement Coverage Report | DOC | 计算来源、设计、实现、验证和发布覆盖 |
| ALR | Asset Lineage Report | DOC | 展示目标资产的端到端来源与演进链 |
| UCR | Untracked Change Report | CASE | 处理没有受控来源的代码或资产变化 |
| OAR | Orphan Artifact Report | CASE | 处理缺少强制上游或下游关系的资产 |
| IQR | Impact Query Result | REC | 固化一次影响查询的参数、结果和完整性 |

八类正式产物不得合并。TLR 中的 Link 是 Register Member，Link ID 不创建新的正式产物类型。

### 8.2 受控关系

| 关系 | Source → Target | C10 使用规则 |
|---|---|---|
| derives-from | 派生资产 → 上游来源资产 | 不表示替代；必须可解释派生路径 |
| addresses | 解决资产 → Need/Problem/Risk/Concern | 必须说明处理范围 |
| contains | 集合/包 → 成员资产 | 成员保持独立身份；禁止 contains Cycle |
| refines | 细化资产 → 上游资产 | 不得改变原意；改变原意走 Revision/Change |
| extends | 新能力资产 → 被扩展资产 | 新独立义务必须有独立身份 |
| depends-on | 依赖资产 → 被依赖资产 | 必须记录依赖条件和失效影响 |
| constrains | 约束资产 → 被约束资产 | 必须引用约束来源 |
| designed-by | Requirement → Design Asset | Target 必须是受控设计资产 |
| implemented-by | Requirement/Design → Implementation Asset | Target 必须可定位到代码、配置、Schema、模型或部署资产 |
| verified-by | Requirement/Criterion → Verification Evidence | 不表示 Validation 或 Acceptance |
| validated-by | Need/Intent/Goal → Validation Result | 不替代 Verification |
| released-in | Asset → Release Configuration | Target 必须由 C11 可重建 |
| affected-by | Asset → Event/Risk/Change | 必须说明影响类型、范围和时间 |
| supersedes | 新资产 → 旧资产 | 旧资产退出当前有效集但永久保留 |
| replaces | 新资产 → 被直接接替资产 | 必须记录职责和生效边界 |
| generated-by | 生成资产 → Agent Run/Tool/Process | 不表示已批准或已验证 |
| observed-from | Evidence/Learning/Finding → Run/Observation | 必须保留观察来源 |

蓝图最低集合包含除 extends 外的 16 种关系；extends 来自公共关系基线，同样属于允许的正式关系。禁止使用无受控语义的 related-to 或中文“相关”建立正式 Link。

### 8.3 关系身份与方向

一个 Link 的逻辑身份由以下内容共同界定：

```text
Source Asset ID + Controlled Relationship + Target Asset ID + Applicable Scope
```

规则如下：

1. Link ID 采用 TLR 成员标识，例如 `TLR-0001-L0042`。
2. Source、关系或 Target 任一发生语义变化时必须建立新 Link ID。
3. 同一逻辑 Link 的端点 Revision、Evidence、状态或有效范围修正可以形成 Link Revision。
4. 反向查询不得创建一个方向相反、语义相同的第二 Link。
5. 关系方向以第 8.2 节为准；显示层可以使用“被……实现”等反向标签，但底层 Link 不翻转。
6. 跨产品或外部资产必须使用可解析 External Asset Reference、Authority、Version 和访问边界。

### 8.4 唯一事实源边界

| 信息 | 唯一事实源 | C10 处理 |
|---|---|---|
| Asset 内容与 Current Revision | 所属 C01–C09/C11/E01–E05 规范 | 引用固定 Revision |
| Decision rationale 与替代 | C10 DEC 或专属 Decision 事实源 | C10 DEC 只管理自身类型；专属 Decision 只建立 Link |
| 正式 Trace Link | C10 TLR | 建立、验证、查询、修正和退役 |
| Matrix/Coverage/Lineage | C10 派生报告 | 固定输入 Snapshot 和规则 |
| Actual Change/Run | C09 | 建立 generated-by/observed-from 候选关系 |
| Snapshot/Baseline/Change/Release | C11 | C10 消费配置身份和输出 Impact |
| Verification/Validation | C05 | 建立 Link；不修改 Result |
| Gate/Risk Acceptance/Waiver | C12 | 提供 Evidence；不作决定 |
| Record metadata/lifecycle | E04 | C10 提供领域字段和关联 |

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
资产/问题出现
  → Decision 或 Trace 触发判定
  → 建立 DEC / Proposed Link
  → 固定端点 Revision、依据和范围
  → Review / Validate
  → Approved DEC / Active Link
  → BTM、RCR、ALR、IQR 消费
  → Revision/Change/Context 变化
  → Suspect / Impact Query / UCR / OAR
  → Revalidate、Correct、Supersede、Replace 或 Retire
  → 保留 History
```

### 9.2 初始化

每个产品在 Discovery Ready 前必须建立：

- Traceability Owner；
- TLR；
- 适用资产类型与关系 Profile；
- Critical Requirement 的强制链路；
- Coverage 维度、集合、阈值和 N/A 规则；
- Link 建立、验证、失效和修正规则；
- 外部资产解析规则；
- Access、Retention 和审计规则；
- 自动化规则和人工复核边界。

### 9.3 Decision 生命周期

1. 识别重大选择并创建 DEC `Proposed`；
2. 固定背景、问题、候选方案、评价、选择建议、影响和 Risk；
3. 关联受影响资产、Requirement、Design、Run、Change 或 Gate；
4. 进入 `Under Review`；
5. 由 Decision Authority 进入 `Approved`、`Conditionally Approved` 或 `Rejected`；
6. 条件满足并不自动改变 State，必须记录复核；
7. 新 Decision 使旧 Decision 失效时使用 supersedes/replaces；
8. 有效期届满时进入 `Expired`，不得删除。

### 9.4 Trace 生命周期

1. 从上游资产、C09 Run、C11 Change 或规则生成候选 Link；
2. 分配 Link ID，记录端点、关系、依据、Method 和范围；
3. Trace Steward 验证方向、Revision、权限和语义；
4. 通过后进入 `Active`；
5. 端点、范围、Decision、Change、Rule 或有效期变化时进入 `Suspect`；
6. 重新验证后恢复 `Active`，错误 Link 进入 `Invalid`，不再适用进入 `Retired`；
7. 被拒绝候选进入 `Rejected` 并保留最小历史。

### 9.5 报告与查询生命周期

- BTM、RCR 和 ALR 在每次重大 Revision、Gate、Baseline 或 Release 前重新生成并评审；
- IQR 每次查询产生一个 REC，固定查询参数、图 Snapshot 和结果；
- 报告失效时进入 DOC `Superseded`，不得覆盖旧报告；
- 查询规则或输入不完整时必须标记 Partial/Indeterminate，不得声称 Complete；
- UCR/OAR 在发现时创建 CASE，完成补救和复核后才能 Resolved/Closed。

### 9.6 失效传播

以下事件必须触发相关 Link 重新判定：

- Source 或 Target Current Revision 变化；
- Requirement 状态、Scope、关键度或适用版本变化；
- Decision 被拒绝、替代或过期；
- Design、Implementation、Test、Evidence 或 Release Configuration 变化；
- C09 发现未跟踪资产变化；
- C11 Change、Baseline 或 Retirement；
- C08 Context Source 失效影响已建立关系；
- 自动化规则、外部系统或 ID 解析器变化；
- Access 或 Retention 规则使端点不可用。

## 10. 强制规则

### 10.1 永久身份与端点解析

1. 每个正式产物必须使用受控产物目录规定的 Asset ID。
2. 每个 Trace Link 必须有唯一 Link ID，且创建后不得复用。
3. Source 和 Target 必须至少记录 Asset ID、Artifact Type、Revision/Snapshot Reference 和 Resolver。
4. 文件路径、URL、Issue Number、数据库主键、对象存储 Key 和 Commit Hash 只能作为 Locator，不得替代 Asset ID。
5. 外部端点必须记录 External Authority、External ID、Version、Access 和 Last Verified Time。
6. 端点无法解析时 Link 只能为 Proposed/Suspect/Invalid，禁止 Active。
7. 已删除、Retired 或 Superseded 端点仍保留历史身份和解析结果。

### 10.2 Decision 触发

出现以下任一情况必须建立 Decision Record 或引用已有专属 Decision：

- 改变 Product Intent、Scope、Requirement 语义或公开行为；
- 在两个及以上可行方案中选择并产生显著长期影响；
- 改变架构边界、接口、数据模型、状态模型、依赖或部署拓扑；
- 引入、替换或退出关键技术、外部服务、模型或供应商；
- 影响 Security、Privacy、Compliance、Data、Availability 或重大成本；
- 需要不可逆、难回滚、跨仓库、跨团队或跨版本行动；
- Agent 在授权范围内作出影响多个受控资产的非例行选择；
- Trace/Coverage Policy、关系语义或自动化规则发生变化。

Acceptance、Gate、Risk Acceptance、Exception/Waiver 和 Change 的专属决定必须由其事实源产物管理；C10 只建立 Link，不复制为通用 DEC。

### 10.3 单一问题与 Decision 内容

1. 一个 DEC 只处理一个可判定的 Decision Question。
2. 多个独立选择必须拆分为多个 DEC，并使用 depends-on 或 constrains。
3. DEC 必须记录至少两个真实候选方案；只有一个可行方案时必须解释约束来源。
4. “保持现状”和“延期决定”在适用时必须作为候选方案评估。
5. 每个候选方案必须记录 Benefits、Costs、Risks、Constraints、Reversibility 和受影响资产。
6. Chosen Option、Rationale、Conditions、Effective Boundary 和 Review Date 必须明确。
7. 私有思维链禁止进入 DEC；只记录可复核的事实、评价准则、权衡和结论。

### 10.4 Decision Authority 与生效

1. DEC Author、Owner、Participants 和 Decision Authority 必须分别记录。
2. Agent 起草的 DEC 默认 `Proposed`；只有 C07 明确授权且不违反职责分离时才能推进指定 State。
3. `Approved` 表示无附加前置条件的批准；`Conditionally Approved` 必须列出条件、Owner、期限和失效规则。
4. Decision Effective Time 不得早于实际批准时间。
5. 口头、聊天或 Tool Result 只有被捕获为受控 Evidence 并由 Authority 确认后才能支持 Decision。
6. `Waived` 只在上游专属 Waiver 事实已存在且 C10 DEC 的义务被正式豁免时使用；不得替代 C12 EWR。
7. DEC State 改变必须记录 Actor、Authority、Old/New State、Time、Basis 和 History。

### 10.5 Rationale、Impact 与 Risk

1. Rationale 必须能说明为何选择当前方案而非其他候选方案。
2. 每个 DEC 必须引用受影响 Need、Requirement、Design、Implementation、Test、Change、Release 或 Record。
3. Impact 必须区分直接、间接和未知影响。
4. Risk 使用 C02/C12 的 Risk ID 和 Current Risk Level，禁止建立平行风险量表。
5. 未知影响、未验证假设和受限 Evidence 必须显式记录。
6. Decision Reviewer 必须能从引用 Revision 独立复核事实，不得只接受摘要。
7.重大不利意见必须保留在 DEC 或 Review History 中。

### 10.6 Decision 替代、接替与过期

1. Chosen Option 实质改变时必须建立新 DEC；禁止重写旧 DEC 的选择。
2. 新 DEC 使旧 DEC 退出当前有效集合时使用 supersedes。
3. 新 DEC 直接接替旧 DEC 的职责或义务时使用 replaces，并记录 Effective Boundary。
4. 旧 DEC State 必须相应进入 `Superseded` 或 `Expired`。
5. 被拒绝、替代、过期或撤销的 DEC 不得删除。
6. 仅修正拼写、Locator 或不改变语义的元数据时可以修订原 DEC，但必须保留 History。
7. 被替代 Decision 的下游 Link 必须进入 Suspect 并执行 Impact Query。

### 10.7 Trace Link 语义

1. 正式 Link 只允许使用第 8.2 节关系。
2. 每个 Link 必须记录 Direction、Scope Note 和 Establishment Basis。
3. 同一 Link 禁止同时表达来源、实现、验证和发布等多种语义。
4. “同一 PR”“同一 Commit”“同一文件”“同一 Run”或“文本相似”不足以单独证明正式关系。
5. Link Basis 必须引用资产内容、批准 Decision、执行事实、配置记录、验证 Evidence 或批准规则。
6. 显示层别名不得改变底层受控关系。
7. 无法判断语义时建立 Trace Gap/OAR，不得创建模糊 Link。

### 10.8 Link Revision 与有效范围

1. Source/Target 必须记录建立 Link 时的 Revision。
2. Effective Version Range 必须指明 Product、Baseline、Release、Environment、Time 或其组合。
3. 同一逻辑 Link 的有效范围不得无解释重叠或冲突。
4. 端点 Revision 变化不自动表示 Link 仍有效。
5. Editorial Revision 只有在端点 Owner 确认语义未变时才允许沿用 Link。
6. Semantic Revision 必须使所有相关 Active Link 进入 Suspect。
7. Link Revision 必须保留 Previous Revision、Change Reason、Actor、Time 和 Review Result。

### 10.9 Link 建立与激活

1. Human Authored Link 由 Trace Steward 验证端点、关系、依据和范围。
2. Deterministic Rule 必须有 Rule ID、Version、Owner、测试、误报处理和批准。
3. Imported Link 必须记录 Source System、Export Version、Mapping Rule、Import Time 和完整性。
4. Agent Proposed Link 必须记录 Model/Agent、Run、输入范围和建议理由，只能进入 `Proposed`。
5. 只有确定性、已批准且当前有效的规则可以按策略自动激活 Link。
6. 概率模型、Embedding、LLM 或模糊匹配的结果禁止自动进入 `Active`。
7. Link 激活必须记录 Reviewer、Time、Basis 和端点可解析 Evidence。

### 10.10 Suspect、修正与退役

1. 失效事件发生时系统必须在下一次 Gate/Release 前将相关 Link 标为 `Suspect`。
2. `Suspect` Link 不得计入 Covered；临时例外只能影响 Gate 处置，不得改写 Coverage 事实。
3. 错误建立的 Link 进入 `Invalid`，保留错误原因和更正引用。
4. 候选被拒绝进入 `Rejected`。
5. 业务上不再适用但历史正确的 Link 进入 `Retired`。
6. 物理删除只允许依法处置且必须保留最小审计记录；Legal Hold 时禁止处置。
7. 修正不得倒签创建时间、批准或有效期。

### 10.11 双向追踪与 BTM

1. 正向和反向查询必须读取同一 TLR Snapshot。
2. BTM 每一行必须显示 Upstream Asset、Relation、Downstream Asset、双向查询键、适用版本和 Coverage Status。
3. BTM 不得维护独立于 TLR 的手工 Link 事实。
4. 查询必须接受 Asset ID、Revision、方向、关系集合、范围和时间点。
5. 正向结果与反向结果对同一 Link 必须一致。
6. Duplicate、Dangling、Direction Error 和 Missing Reverse Query 必须自动检查。
7. BTM 生成规则、Tool Version、Input Snapshot 和 Digest 必须记录。

### 10.12 关系约束与图完整性

1. contains、derives-from、refines、supersedes 和 replaces 图禁止 Cycle。
2. depends-on Cycle 必须报告并由 Architecture/Change Reviewer 判断；禁止静默忽略。
3. supersedes/replaces 必须指向更早生效的资产，禁止时间反转。
4. designed-by、implemented-by、verified-by、validated-by 和 released-in 的 Target Type 必须符合第 8.2 节。
5. generated-by/observed-from 不得用于声称 Approval、Verification 或 Acceptance。
6. Active Link 的端点必须在有效范围内同时可用。
7. 同一 Source—Relation—Target—Scope 只允许一个当前 Active 语义事实。
8. 图检查必须输出 Cycle Path、Conflicting Link IDs 和受影响资产。

### 10.13 Coverage

1. RCR 必须分别计算 Source、Design、Implementation、Verification 和 Release Coverage。
2. 每一维的 Eligible Set 由 Artifact Type、State、Criticality、Scope、Release 和批准的 Applicability Rule 决定。
3. 公式为：

```text
Applicable = Eligible Total - Approved Not Applicable
Coverage % = Covered / Applicable × 100
```

4. Applicable 为 0 时结果必须为 `N/A`，禁止报告 100%。
5. `Partially Covered`、`Not Covered`、`Unknown` 和 `Suspect` 不计入 Covered。
6. `Not Applicable` 必须记录理由、Authority、日期和有效范围。
7. RCR 必须同时披露 Total、Applicable、Covered、Partial、Not Covered、Unknown、N/A 和 Orphan。
8. Critical/High Requirement 必须逐项展示，不得只给聚合百分比。
9. Threshold 必须引用批准的 Gate、Plan 或 Standard；报告生成者不得临时设定。
10. End-to-End Covered 只有在全部适用维度存在当前 Active、Revision 有效的完整链时成立。

### 10.14 Asset Lineage

1. ALR 必须以 Target Asset ID 和 Revision 为查询根。
2. Lineage 至少覆盖适用的 Source、Derivation、Generation、Implementation、Verification、Observation、Release、Supersession 和 Replacement。
3. 每个 Node 必须记录 Asset ID、Type、Revision、State、Owner 和 Locator。
4. 每个 Edge 必须记录 Link ID、Relation、Member State、Effective Range 和 Basis。
5. 分支、合并、外部来源、生成 Tool/Run、人工修正和断链必须可见。
6. Lineage 必须区分“由某 Run 生成”和“由某 Requirement 授权”。
7. 无法访问受限端点时必须保留最小元数据并标记 Access Gap。
8. ALR 必须固定 TLR/C11 Snapshot、Query Rule、Time 和 Digest。

### 10.15 Orphan Artifact

1. Orphan 判定必须基于 Artifact Type、State、阶段和 Expected Relationship Profile。
2. Draft Requirement 在尚未到 Design 阶段时不得因缺少 designed-by 自动判为 Orphan。
3. Approved/Baselined Requirement 在适用 Gate 到期仍缺少强制下游 Link 时必须创建 OAR。
4. 已实现资产缺少 Requirement、Decision、Change 或 Incident 来源时优先创建 UCR，并可同时建立 OAR 引用。
5. Evidence 缺少被验证对象时属于 Detached Evidence。
6. Link 端点无法解析时属于 Dangling Endpoint。
7. OAR 必须记录 Missing Relation、Expected By、Impact、Owner、Disposition 和 Closure Criteria。
8. OAR 关闭必须基于补链、退役、回退、批准 N/A 或资产修正的可验证 Evidence。

### 10.16 Untracked Change

1. C09 CAS/CCS 或 C11 Diff 发现变化但无批准来源时必须创建 UCR。
2. UCR 必须固定 Repository、Revision/Snapshot、Changed Asset、Diff、Discovery Method 和发现时间。
3. 允许的处置为：回退、建立当前有效的 Requirement/Decision/Change、认定为已批准 Emergency/Incident Change、隔离或退役。
4. 后续补充批准不得倒签为变化发生时已授权。
5. UCR 必须保留原始 Untracked 事实、未授权期间影响和补救时间线。
6. 在 UCR Resolved 前，相关 Change、Baseline 或 Release 必须按 C11/C12 规则阻断或形成正式例外。
7. `Tracked` 只表示当前已存在有效来源，不消除历史 UCR。
8. 关闭必须有 Trace、Impact、Verification、配置处置和授权复核 Evidence。

### 10.17 Impact Query

1. 下列操作前必须执行 IQR：重大 Decision、Change Approval、Baseline、Release、Supersession、Replacement、Retirement 和高影响 UCR/OAR 处置。
2. 查询参数必须包含 Root Asset/Revision、Direction、Relation Set、Max Depth、Scope、As-of Time、State Filter 和 Stop Rules。
3. 结果必须区分 Direct、Indirect 和 Unknown。
4. Cycle 必须去重并报告 Cycle Path，不得无限遍历。
5. 权限不足、端点不可解析、外部系统不可用或 Snapshot 不一致时 Query Completeness 不得为 Complete。
6. IQR 必须记录 Query Engine/Version、Rule Version、Input Digest、Start/End Time 和执行者。
7. IQR 是只读 REC，不得在查询过程中修改 Link 或端点。
8. 任何自动处置建议必须作为 Proposed Action，不得作为批准。

### 10.18 自动化与 AI 边界

1. 自动检查必须可重复执行并记录 Rule/Tool Version。
2. 确定性规则应覆盖 ID 解析、Duplicate、Cycle、Dangling、Revision Drift、Missing Link、Coverage 和有效期。
3. LLM/Embedding 可以发现候选 Decision、Link、Impact 或 Orphan，但输出必须标记为 Suggestion。
4. 自动化不得编造 Asset ID、Revision、Approval、Evidence 或 Link Basis。
5. 工具无法访问完整 Source 时必须标记 Partial/Indeterminate。
6. Tool 更新、Mapping Rule 更新或模型变化必须触发抽样回归和影响分析。
7. 自动生成的 RCR/ALR/BTM 必须允许 Reviewer 下钻到 Link 和端点 Evidence。
8. 生成摘要不得替代 TLR、IQR 或原始查询日志。

### 10.19 访问、敏感与跨边界关系

1. Link 的 Access Classification 取 Source、Target 和 Basis 中最严格的适用级别。
2. 导出 Matrix/Report 时必须执行最小披露和字段级遮蔽。
3. Secret、Token、个人敏感数据、受限漏洞细节和商业秘密不得写入 Link Label 或公开 Locator。
4. 跨租户、跨组织、跨供应商 Link 必须记录 Authority、Purpose、Agreement 和有效期。
5. 外部端点不可访问时不得将历史缓存视为当前有效。
6. 访问撤销不得删除历史 Link；必须调整可见性和保留最小审计元数据。
7. Security/Privacy/Compliance Trace 在 E02 激活时必须执行其附加控制。

### 10.20 Coding Agent 行为边界

Coding Agent：

1. 必须先读取蓝图、公共关系、产物目录、当前 Revision 和适用 Authority；
2. 必须把推断关系作为 Proposed，禁止伪造 Active Link；
3. 必须保留 Source/Target、Revision、Basis、Rule/Tool 和查询限制；
4. 禁止使用文件邻近、同一 Commit 或词语相似直接判定正式关系；
5. 禁止改变 Requirement、Decision、Risk、Acceptance、Baseline 或 Gate 的事实源状态；
6. 禁止删除被拒绝、Invalid、Suspect、Superseded、Expired 或不利的历史；
7. 必须对 Untracked Change、Orphan、Dangling、Cycle 和 Unknown 建立明确 Finding/CASE；
8. 必须在 Impact Query 不完整时报告 Partial/Indeterminate；
9. 必须避免覆盖用户或并行 Agent 产生的未知变化；
10. 必须将超出授权的 Decision、Link 激活、补链、关闭和例外升级给人类。

## 11. 受控状态

### 11.1 Decision Record

DEC 使用 DEC State：

```text
Proposed → Under Review → Approved / Conditionally Approved / Rejected
Approved / Conditionally Approved → Superseded / Expired
Under Review → Proposed
```

`Waived` 仅按第 10.4 节受限使用。Rejected、Superseded 和 Expired 均为保留状态。

### 11.2 TLR、BTM、RCR、ALR

四类产物使用 DOC State：

```text
Draft → In Review → Approved → Baselined
In Review → Changes Required → Draft
In Review → Rejected
Approved / Baselined → Superseded
Superseded → Retired
```

TLR 的 DOC State 与 Link Member State 分离。TLR Baselined 不表示其中每个成员永远有效。

### 11.3 UCR、OAR

两类产物使用 CASE State：

```text
Open → In Progress → Resolved → Closed
In Progress → Blocked
Closed → Reopened
Open / In Progress / Blocked → Cancelled
```

Resolved 必须有补救 Evidence；Closed 必须有独立复核。Cancelled 只表示无需继续处理，不删除发现事实。

### 11.4 Impact Query Result

IQR 使用 REC State：

```text
Recorded → Corrected / Superseded → Archived
```

IQR 创建即为 `Recorded`。查询错误通过新 Revision/新 IQR 更正，原结果保留。

### 11.5 Link Member State

```text
Proposed → Active / Rejected
Active → Suspect / Retired
Suspect → Active / Invalid / Retired
Invalid / Rejected / Retired → 终端
```

确需恢复 Invalid/Rejected/Retired 关系时必须建立新 Link ID，禁止复活旧成员。

### 11.6 状态禁止混用

- Coverage Status 不得写入 DOC/DEC/CASE/REC State；
- Link Member State 不得替代 TLR DOC State；
- Query Completeness 不得替代 IQR REC State；
- UCR 的 Change Source Status 不得替代 CASE State；
- Decision 的 Approved 不等于 Requirement、Change、Gate 或 Release 已批准；
- Active Link 不等于端点已验证、已接受或已发布。

## 12. 必需产物

| 产物 | 最低创建条件 | 主要下游 |
|---|---|---|
| Decision Record | 第 10.2 节任一触发条件成立，且没有专属 Decision 事实源可引用 | C06、C09、C11、C12、E01–E05 |
| Trace Link Register | 每个采用本体系的产品必须存在且持续维护 | 全部规范 |
| Bidirectional Traceability Matrix | Gate、Baseline、Release、审计或重大影响分析前 | C04、C05、C11、C12 |
| Requirement Coverage Report | Requirement 集合进入评审、Baseline、Release 或 Coverage 阈值检查时 | C05、C11、C12 |
| Asset Lineage Report | 关键资产、生成资产、受限资产、发布资产或审计对象需要重建来源时 | C09、C11、C12、E04 |
| Untracked Change Report | 发现代码或受控资产变化缺少有效来源时 | C09、C11、C12 |
| Orphan Artifact Report | 资产在当前阶段缺少强制上游或下游 Link 时 | C04、C05、C11、C12 |
| Impact Query Result | Decision、Change、Baseline、Release、替代、退役或高影响处置前 | C02、C11、C12 |

P2 禁止合并八类身份。没有重大 Decision、Untracked Change 或 Orphan 时无需创建空 DEC/UCR/OAR 实例，但类型、触发规则和模板必须保留。

## 13. 必填信息

### 13.1 通用必填信息

八类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C10 类型专属要求。

### 13.2 Decision Record

- Decision ID；
- Decision Type；
- Context；
- Decision Question；
- Evaluation Criteria；
- Considered Options；
- Chosen Option；
- Rationale；
- Benefits、Costs 和 Trade-offs；
- Impact（Direct/Indirect/Unknown）；
- Risk IDs 和 Current Risk；
- Assumptions/Unknowns；
- Owner；
- Author、Participants 和 Decision Authority；
- DEC State；
- Proposed/Review/Decision/Effective Date；
- Conditions、Review Date 和 Expiry；
- Related Assets 及 Revision；
- supersedes/replaces 关系；
- Dissent/Review Findings；
- Confirmation/Verification Plan。

### 13.3 Trace Link Register

TLR 本体必须记录 Register Scope、Schema/Rule Version、Custodian、Current Snapshot 和成员统计。每个成员必须包含：

- Link ID；
- Source Asset ID、Type、Revision 和 Locator；
- Controlled Relationship；
- Target Asset ID、Type、Revision 和 Locator；
- Direction/Scope Note；
- Establishment Basis 和 Evidence；
- Establishment Method；
- Rule/Tool/Import Source；
- Creator、Reviewer 和 Authority；
- Created/Reviewed/Last Verified Time；
- Trace Link Member State；
- Effective Version Range；
- Access Classification；
- Previous Link Revision；
- Suspect/Invalid/Retired Reason；
- History Reference。

### 13.4 Bidirectional Traceability Matrix

- Matrix Scope；
- TLR Snapshot/Digest；
- As-of Time；
- Query Rule/Version；
- Upstream Asset/Revision；
- Relationship；
- Downstream Asset/Revision；
- Forward Query Key；
- Reverse Query Key；
- Applicable Version；
- Link Member State；
- Coverage Status；
- Gap、Conflict、Duplicate 或 Dangling；
- Gap Owner 和 Due Date；
- Generated By 和 Review Result。

### 13.5 Requirement Coverage Report

- Requirement Set/Revision；
- Scope、Release/Baseline 和 As-of Time；
- Requirement Total；
- 按 Type、Criticality 和 State 的数量；
- Source/Design/Implementation/Verification/Release Eligible、Applicable 和 Covered；
- Partial、Not Covered、Unknown、Not Applicable 和 Orphan 数量；
- 各维 Coverage Formula 和 Result；
- End-to-End Coverage；
- N/A Reasons/Approvers；
- Threshold Source 和阈值；
- Threshold Result；
- Gap List、Owner 和 Due Date；
- TLR/BTM Snapshot；
- Conclusion、Limitations 和 Reviewer；
- Statistics Time。

### 13.6 Asset Lineage Report

- Target Asset ID/Type/Revision；
- Query Scope、As-of Time 和 Version Boundary；
- Source/Derivation Chain；
- Generation Run/Tool/Process；
- Implementation Chain；
- Verification/Validation Chain；
- Observation/Evidence Chain；
- Release Configuration；
- Supersession/Replacement Chain；
- External Sources；
- Node/Edge Count；
- Branch/Merge/Cycle；
- Broken Link、Dangling Endpoint 和 Access Gap；
- TLR/C11 Snapshot 和 Digest；
- Query Rule/Tool Version；
- Generated Time、Generator 和 Reviewer；
- Completeness/Limitations。

### 13.7 Untracked Change Report

- Changed Code/Asset ID、Type 和 Revision；
- Repository/Workspace/Environment；
- Base/Result Snapshot、Commit 和 Diff；
- Discovery Method、Run 和 Time；
- Missing Source Type；
- Change Source Status；
- Potential Direct/Indirect/Unknown Impact；
- Affected Requirement/Design/Test/Release；
- Risk ID 和 Current Risk；
- Owner；
- Containment；
- Disposition Decision；
- Required Requirement/Decision/Change/Incident Link；
- Backfill or Revert Deadline；
- Verification、Configuration 和 Gate Evidence；
- Resolution/Closure Criteria；
- CASE State 和 History。

### 13.8 Orphan Artifact Report

- Orphan Asset ID、Type、Revision 和 State；
- Orphan Type；
- Expected Relationship Profile；
- Missing Upstream/Downstream Relation；
- Lifecycle Stage/Gate；
- Expected By；
- Detection Rule/Tool/Time；
- Current Links；
- Impact 和 Risk；
- Owner；
- Disposition；
- N/A Decision（如适用）；
- Remediation Due Date；
- Closure Criteria 和 Evidence；
- CASE State 和 History。

### 13.9 Impact Query Result

- Query ID；
- Root Asset ID/Type/Revision；
- Query Purpose；
- Query Time/As-of Time；
- Direction；
- Relation Set；
- Max Depth 和 Stop Rules；
- Scope、State Filter 和 Version Filter；
- TLR/C11 Snapshot 和 Input Digest；
- Query Engine/Version 和 Rule Version；
- Direct Impact Assets；
- Indirect Impact Assets；
- Unknown/Unresolved Assets；
- Cycle、Duplicate、Dangling 和 Access Gap；
- Query Completeness；
- Result Count 和 Truncation；
- Executor、Start/End Time；
- Proposed Actions；
- Correction/Supersession Reference。

## 14. 质量要求

### 14.1 Decision 质量

合格 DEC 必须：

- 一项记录只处理一个问题；
- 候选方案真实且可比较；
- 选择、理由、影响、Risk、Authority 和日期完整；
- Rationale 可由引用 Evidence 复核；
- 适用边界和失效条件明确；
- 替代、接替和过期关系完整；
- 不复制专属 Decision 事实源；
- 不保存私有思维链。

### 14.2 Link 质量

Active Link 必须同时满足：

- Source/Target 可解析；
- Asset ID、Type 和 Revision 有效；
- Relation 来自受控集合且方向正确；
- Basis、Method、Creator、Reviewer 和时间完整；
- Effective Range 当前适用；
- 无 Semantic Duplicate；
- 无禁止 Cycle；
- Access 和 Retention 有效；
- 未受失效事件影响，或已完成重新验证。

### 14.3 报告质量

BTM、RCR、ALR 和 IQR 必须：

- 固定 TLR/C11 Snapshot 和 As-of Time；
- 记录 Query/Rule/Tool Version；
- 披露 Scope、Filter、Exclusion 和 Limitation；
- 可从聚合结果下钻到 Link 和端点；
- 生成结果可重复或说明不可重复原因；
- 不把 Unknown、Suspect、Partial 或 N/A 计为 Covered；
- 不把权限不足解释为无影响；
- 由指定 Reviewer 完成复核。

### 14.4 时效

| 事件 | 最大允许滞后 |
|---|---|
| 新 Approved/Baselined 资产 | 在进入下一 Gate 前建立必需 Link |
| 端点 Semantic Revision | 在下一次消费前标记 Suspect |
| Untracked Change 发现 | 当日创建 UCR |
| Orphan 到期 | 在检测批次内创建 OAR |
| Gate/Baseline/Release | 使用同一候选 Snapshot 重新生成 BTM/RCR/IQR |
| Critical Link 失效 | 立即通知 Owner、C11 和 C12 |

项目可以设置更短时限，不得设置使已知失效 Link 跨 Gate 静默沿用的更长期限。

## 15. 评审、批准与接受

### 15.1 评审顺序

1. Artifact Owner 核对资产身份和 Revision；
2. Trace Steward 核对 Link 语义、方向、范围和 Evidence；
3. Requirement/Design/Verification Owner 核对领域关系；
4. Configuration/Change Owner 核对 Snapshot、Baseline、Change 和 Release；
5. Records Steward 核对元数据、访问、保留和历史；
6. Independent Reviewer 核对 Coverage、Lineage、Impact、UCR/OAR 和自动化限制；
7. Decision Authority、Gate/Release Authority 在各自事实源中作决定。

### 15.2 DEC Review Ready

DEC 进入 `Under Review` 前必须：

- Decision Question 单一明确；
- 候选方案、评价准则和 Chosen Option 建议完整；
- 影响、Risk、Unknown 和受影响资产已记录；
- Owner、Participants 和 Authority 已确认；
- 引用 Revision 可访问；
- Conditions、Review/Expiry 和替代关系适用性已判定。

### 15.3 Link Active Ready

Link 进入 `Active` 前必须：

- Link ID 唯一；
- Source/Target ID、Type、Revision 可解析；
- Relation 和方向正确；
- Basis/Evidence 充分；
- Effective Range 无冲突；
- Reviewer 和 Authority 有效；
- Duplicate、Cycle 和 Access 检查通过；
- 失效监测规则已建立。

### 15.4 Trace Ready

产品可以声明 Trace Ready 只有在：

- TLR 已 Approved/Baselined；
- Critical/High Requirement 的适用链路完整；
- BTM 双向查询一致；
- RCR 达到批准阈值；
- Blocking UCR/OAR、Dangling、Cycle 和 Unknown 为零；
- 最新 IQR 使用候选 Baseline/Release Snapshot；
- C11 配置身份和 C12 Gate 输入已提供；
- 限制、N/A、例外和剩余 Risk 已由有权流程处理。

Trace Ready 是 C10 的可验证就绪断言，不是正式产物 State，也不是 Gate Decision；只有 C12 可以消费该断言并作 Gate 决定。

### 15.5 阻断条件

以下任一情况阻断 Trace Ready 或相应 Gate：

- 使用模糊关系；
- Active Link 端点无法解析；
- Critical Requirement 缺少强制来源、设计、实现、验证或发布链；
- Coverage 分母、排除项或 Snapshot 不明；
- 存在未处置 UCR；
- 存在到期 OAR 或禁止 Cycle；
- Impact Query 为 Indeterminate 且涉及高影响变化；
- 被替代 Decision 仍被当作当前依据；
- Agent/LLM 推断未经复核即激活；
- Access/Retention 违反 E04 或适用扩展。

## 16. 变更、审计与保留

### 16.1 变更控制

1. C10 文档、Schema、关系 Profile、Coverage Rule、Query Rule 和自动化策略变化必须进入 C11 Change。
2. 关系语义、端点类型约束或 Coverage 公式变化必须执行全量 Impact Query。
3. 只改变显示标签不得改变底层关系语义。
4. 迁移必须保存 Old/New Link ID、映射规则、异常和回滚。
5. 批量导入或重算必须先在隔离 Snapshot 验证。
6. 变更失败不得覆盖原 TLR 或报告。

### 16.2 审计事件

至少记录：

- DEC 创建、提交、批准、拒绝、条件、替代和过期；
- Link 创建、导入、激活、Suspect、修正、Invalid、Rejected 和 Retired；
- Rule/Tool/Schema 版本变化；
- BTM/RCR/ALR/IQR 生成、复核、导出和更正；
- UCR/OAR 创建、状态变化、处置、Reopen 和关闭；
- Access、导出、遮蔽、保留、Legal Hold 和处置；
- 自动化批次、失败、误报和人工覆盖。

### 16.3 更正

1. DEC 语义选择改变时创建新 DEC，不做原地更正。
2. Link 端点或关系错误时旧 Link 进入 Invalid，新建正确 Link。
3. IQR 错误时建立 Corrected Revision/新 IQR，原记录保留。
4. 报告统计错误时生成新 Revision，旧报告 Superseded。
5. 更正必须记录原因、Actor、Authority、Time、Old/New 和受影响消费者。

### 16.4 保留与处置

1. Retention Rule 由 E04、合同、法规、Risk、Baseline 和审计需要决定。
2. Approved/Superseded/Rejected Decision、Invalid/Retired Link、UCR/OAR 和 IQR 禁止无痕删除。
3. 敏感 Link 可以到期遮蔽详细 Locator，但必须保留最小身份、关系、Authority、时间和处置记录。
4. Legal Hold、Incident、争议、审计、Gate 或调查期间禁止处置。
5. 处置必须记录对象、范围、依据、批准、方法、时间、验证和不可恢复影响。

## 17. P2 裁剪与扩展适用性

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C10 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

每次实际变更必须保留最小上游来源、变更资产、验证和结果 Trace。已有 TLR 关系继续有效时只追加必要 Link，不重建全量矩阵。DEC、UCR、OAR 仅在决定、未追踪变化或孤立资产实际出现时 `On Event` 创建。

BTM、RCR、ALR 和 IQR 均从 TLR、固定 Revision/Snapshot 和查询规则生成；它们是不同查询范围的派生视图，不得独立维护重复 Link 或 Coverage 事实。

### 17.1 当前 P2 档位

1. DEC、TLR、BTM、RCR、ALR、UCR、OAR、IQR 八类身份全部保留。
2. 四类 DOC、一类 DEC、两类 CASE 和一类 REC 的 State、Owner、Revision、Trace 和 History 不得合并。
3. 八类模板和检查清单全部保留。
4. TLR、Link ID、双向查询、Coverage 分母、UCR/OAR 和 Impact Query 不得裁剪。
5. 无实例时可以不创建空 DEC/UCR/OAR，但不得删除触发规则。

### 17.2 P1/P3 边界

- P1 可以把 BTM、RCR 和 ALR 展示在同一轻量页面，但底层身份、输入 Snapshot 和结果字段必须可分离；
- P1 不得合并 Decision 与 Trace Link，也不得取消 UCR/OAR；
- P3 可以增加关系 Profile、独立审批、形式化图约束、签名、跨组织联邦查询和连续监测；
- 从 P2 调整档位必须形成治理决议和影响分析。

### 17.3 扩展适用性

| 扩展 | 当前仓库状态 | C10 接口 |
|---|---|---|
| E01 架构治理 | 未激活，必须编制 | Architecture Decision、Concern、View、Model、Conformance 和 Evolution Trace |
| E02 安全、隐私与合规 | 未激活，必须编制 | Security Requirement、Threat、Control、Verification、Exception 和 Release Trace |
| E03 数据与 AI 数据治理 | 未激活，必须编制 | Dataset、Schema、Transformation、Model、Evaluation、Deployment 和 Data Lineage |
| E04 知识与正式记录治理 | 已激活，必须编制 | Provenance、Metadata、Access、Retention、Correction、Disposition 和 History |
| E05 产品运营与服务管理 | 未激活，必须编制 | Incident、Problem、Change、Release、Observation 和 Improvement Trace |

未激活只表示相应运行控制当前不约束本规范仓库，不表示允许删除接口或后续规范。目标产品在 Discovery Ready 前必须重新判定 E01 至 E05。

## 18. 上下游交接

| 规范 | C10 接收 | C10 输出 |
|---|---|---|
| C01 | Need、Problem、Evidence、Intent、Goal Revision | Source/Validation Trace、相关 Decision |
| C02 | Initiative、Scope、Risk、Constraint、Dependency | Impact、affected-by、Decision 和 Coverage Gap |
| C03 | PRD、Feature、Scenario、Release Intent | Requirement Source Trace、Feature Coverage |
| C04 | Requirement ID、Revision、Type、State、Criticality、Evolution | BTM、RCR、Orphan、Impact |
| C05 | Criterion、Strategy、VER、VAE、Acceptance | verified-by/validated-by、Verification Coverage |
| C06 | UX/Technical Design、Interface、Data/State、Architecture Element | designed-by、Decision、Design/Implementation Trace |
| C07 | Role、Authorization、Approval、Stop/Escalation | Decision/Link Actor、Authority 和 Review History |
| C08 | Context Source、Fingerprint、Freshness、Trust、Delta | Context-affected Link、Source Lineage 和失效通知 |
| C09 | RUN、CAS、CCS、VDR、FER、HRR、RRS 候选链接 | 正式 generated-by/observed-from、UCR/OAR、Lineage |
| C11 | Asset、Revision、Snapshot、Baseline、Change、Release Configuration | Impact Query、Trace Gap、UCR、Release Trace |
| C12 | Gate、Exception、Risk Acceptance、Release Criteria | BTM/RCR/ALR/IQR、Blocking Gap 和 Readiness Evidence |
| E04 | Metadata、Access、Retention、Correction、Disposition | Decision、Link、Query、Report 和 History 记录 |

C10 对 C01 至 C09 横向生效，但不回写其内容或状态。C11/C12 必须消费准确 Revision 和 Snapshot；C10 输入失效时必须通知并阻断旧报告沿用。

## 19. 符合性检查

### 19.1 检查方法

- Schema Check：检查必填字段、类型、受控值和状态；
- Resolver Check：检查 Asset ID、Revision、外部端点和 Locator；
- Semantic Check：检查关系名称、方向、端点类型和 Basis；
- Graph Check：检查 Duplicate、Cycle、Dangling、Conflict 和 Effective Range；
- Bidirectional Check：比较同一 TLR Snapshot 的正向和反向结果；
- Coverage Check：复算 Eligible、Applicable、Covered、N/A 和阈值；
- Lineage Check：重建 Node/Edge、Branch/Merge 和断链；
- Impact Check：复算方向、深度、关系集、Cycle 和完整性；
- Record Check：检查 Actor、Time、Authority、Access、Retention、Correction 和 History；
- Independent Review：抽样端点内容和 Evidence，不只审阅生成报告。

### 19.2 强制检查清单

| Check ID | 检查对象 | 通过条件 |
|---|---|---|
| C10-CHK-001 | 八类产物 | ID、Type、State、Owner、Revision、History 独立 |
| C10-CHK-002 | 通用字段 | 十四项通用必填信息完整 |
| C10-CHK-003 | DEC 单一性 | 一项记录只处理一个 Decision Question |
| C10-CHK-004 | DEC 候选 | Options、Criteria、Chosen、Rationale 完整 |
| C10-CHK-005 | DEC 影响 | Direct/Indirect/Unknown、Risk 和资产 Revision 完整 |
| C10-CHK-006 | DEC Authority | Author、Owner、Participants、Authority 和日期完整 |
| C10-CHK-007 | DEC 替代 | supersedes/replaces、Effective Boundary 和旧状态一致 |
| C10-CHK-008 | TLR | Register Scope、Rule Version、Snapshot 和成员统计完整 |
| C10-CHK-009 | Link ID | 唯一、不可复用且不是新产物类型 |
| C10-CHK-010 | Link 端点 | Source/Target ID、Type、Revision、Resolver 可用 |
| C10-CHK-011 | Link 关系 | 名称来自公共集合、方向正确 |
| C10-CHK-012 | Link Basis | Evidence、Method、Creator、Reviewer、Time 完整 |
| C10-CHK-013 | Link Range | Effective Version Range 当前有效且无冲突 |
| C10-CHK-014 | Link State | Proposed/Active/Suspect/Invalid/Rejected/Retired 正确 |
| C10-CHK-015 | 自动 Link | LLM/概率建议未自动 Active |
| C10-CHK-016 | Duplicate | 无 Semantic Duplicate Active Link |
| C10-CHK-017 | Cycle | 禁止关系无 Cycle；depends-on Cycle 已评审 |
| C10-CHK-018 | Dangling | Active Link 无无法解析端点 |
| C10-CHK-019 | Revision Drift | 端点变化已触发 Suspect/Revalidation |
| C10-CHK-020 | BTM Source | 只从同一 TLR Snapshot 投影 |
| C10-CHK-021 | 双向一致 | Forward/Reverse 返回同一 Link |
| C10-CHK-022 | BTM 字段 | Upstream、Relation、Downstream、Version、Status、Gap 完整 |
| C10-CHK-023 | Coverage 集合 | Eligible Set、Scope、State、Criticality、Release 明确 |
| C10-CHK-024 | Coverage 分母 | Total、N/A、Applicable 可复算 |
| C10-CHK-025 | Coverage 公式 | Covered/Applicable 正确，0 分母为 N/A |
| C10-CHK-026 | Coverage 排除 | Partial/Unknown/Suspect 未计 Covered |
| C10-CHK-027 | N/A | 理由、Authority、日期和范围完整 |
| C10-CHK-028 | Threshold | 来自批准 Gate/Plan/Standard |
| C10-CHK-029 | Critical Requirement | 逐项展示端到端链 |
| C10-CHK-030 | ALR Root | Target Asset/Revision、As-of、Scope 明确 |
| C10-CHK-031 | ALR Node/Edge | 身份、Revision、State、Link、Basis 完整 |
| C10-CHK-032 | ALR Chain | Source/Generate/Implement/Verify/Release/Supersede 可重建 |
| C10-CHK-033 | ALR Gap | Branch/Merge/Cycle/Dangling/Access Gap 披露 |
| C10-CHK-034 | UCR Trigger | 无来源变化当日创建 |
| C10-CHK-035 | UCR Evidence | Snapshot、Diff、Discovery、Impact 和 History 完整 |
| C10-CHK-036 | UCR 处置 | 未倒签；Trace、Impact、Verification、Configuration 完整 |
| C10-CHK-037 | OAR Profile | 按 Type/State/Stage 判断，避免过早误报 |
| C10-CHK-038 | OAR Gap | Missing Relation、Expected By、Owner 和 Evidence 完整 |
| C10-CHK-039 | IQR 参数 | Root、Direction、Relations、Depth、Scope、Time、Filter 完整 |
| C10-CHK-040 | IQR 结果 | Direct/Indirect/Unknown、Cycle、Gap 和 Count 完整 |
| C10-CHK-041 | IQR 完整性 | Complete/Partial/Indeterminate 有依据 |
| C10-CHK-042 | IQR 不可变 | 查询结果未原地覆盖，Correction 保留原记录 |
| C10-CHK-043 | 事实源 | C04/C05/C09/C11/C12/E04 边界未重定义 |
| C10-CHK-044 | Agent 边界 | 未伪造 ID、Revision、Approval、Basis 或 Active Link |
| C10-CHK-045 | Access | 最严格分类、最小披露和遮蔽正确 |
| C10-CHK-046 | Retention | Decision、Link、CASE、Query 和更正历史保留 |
| C10-CHK-047 | P2 | 八类身份、模板和检查未裁剪 |
| C10-CHK-048 | 扩展 | E04 当前激活；E01/E02/E03/E05 接口和重评完整 |
| C10-CHK-049 | 国际标准 | 四项 R1 官方来源和公开条款映射完整 |
| C10-CHK-050 | 文档末尾 | 最后内容为国际标准条款映射总表 |

### 19.3 不符合处置

- Schema/字段缺失：返回 Owner 修正；
- 关系语义或方向错误：Link 进入 Invalid，建立正确 Link；
- Revision Drift：Link 进入 Suspect，报告失效；
- Duplicate/Cycle/Dangling：建立 Finding/OAR，阻断适用 Gate；
- Untracked Change：创建 UCR，路由 C09/C11/C12；
- Coverage 未达阈值：列出 Gap、Owner、Due Date 和 Gate 影响；
- 查询不完整：IQR 标记 Partial/Indeterminate；
- 自动化误报：保留批次、Rule Version、修正和回归 Evidence；
- 重大或重复不符合：进入 C12 Review/Gate 和改进行动。

## 20. 附录

### 20.1 通用资产头模板

```markdown
| 信息项 | 内容 |
|---|---|
| Asset ID | <永久 ID> |
| Artifact Type | <正式名称（类型代码）> |
| Name or Summary | <名称或摘要> |
| Purpose | <治理目的> |
| Source | <上游资产/事件/授权/Evidence> |
| Owner | <人类责任角色> |
| State | <对应状态模型受控值> |
| Current Revision | <Revision + Snapshot> |
| Created and Updated | <创建者/时间；修改者/时间> |
| Applicable Scope | <产品/Initiative/模块/环境/版本/时间> |
| Trace Links | <受控关系 + Asset ID/Revision> |
| Access Classification | <公开/内部/机密/受限 + 访问规则> |
| Retention Rule | <期限/归档/删除限制> |
| History Reference | <修订/状态/批准/替代/更正历史> |
```

### 20.2 Decision Record 模板

```markdown
# DEC-<序号> <Decision Question>

## Control
- Decision Type:
- Owner:
- Author:
- Participants:
- Decision Authority:
- DEC State:
- Proposed / Review / Decision / Effective Date:
- Applicable Scope:
- Related Assets and Revisions:

## Context and Decision Question
- Context:
- Problem / Concern:
- Decision Question:
- Constraints:
- Assumptions / Unknowns:

## Evaluation
| Option | Benefits | Costs | Risks | Constraints | Reversibility | Impact |
|---|---|---|---|---|---|---|

## Decision
- Chosen Option:
- Rationale:
- Conditions:
- Direct / Indirect / Unknown Impact:
- Risk IDs / Current Risk:
- Dissent / Findings:
- Confirmation / Verification Plan:
- Review Date / Expiry:
- supersedes / replaces:
```

### 20.3 Trace Link Register 模板

```markdown
# TLR-<序号> <Register Name>

- Register Scope:
- Schema / Rule Version:
- Owner / Trace Steward:
- Current Snapshot / Digest:
- Member Counts by State:

| Link ID | Source ID@Rev | Relation | Target ID@Rev | Basis | Method | Creator / Reviewer | Member State | Effective Range | Last Verified | History |
|---|---|---|---|---|---|---|---|---|---|---|
```

每个 Link 的扩展字段必须保存 Locator、Access、Rule/Tool/Import Source、Previous Revision 和状态原因。

### 20.4 Bidirectional Traceability Matrix 模板

```markdown
# BTM-<序号> <Scope>

- TLR Snapshot / Digest:
- As-of Time:
- Query Rule / Version:
- Generator / Reviewer:

| Upstream ID@Rev | Relation | Downstream ID@Rev | Forward Query Key | Reverse Query Key | Applicable Version | Link State | Coverage Status | Gap / Owner |
|---|---|---|---|---|---|---|---|---|
```

### 20.5 Requirement Coverage Report 模板

```markdown
# RCR-<序号> <Requirement Set>

- Requirement Set / Revision:
- Scope / Baseline / Release:
- As-of Time:
- TLR / BTM Snapshot:
- Threshold Source:

| Dimension | Eligible | Approved N/A | Applicable | Covered | Partial | Not Covered | Unknown | Coverage % | Threshold | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Source | | | | | | | | | | |
| Design | | | | | | | | | | |
| Implementation | | | | | | | | | | |
| Verification | | | | | | | | | | |
| Release | | | | | | | | | | |

## Critical / High Requirement Detail
| Requirement ID@Rev | Source | Design | Implementation | Verification | Release | End-to-End | Gap / Owner / Due |
|---|---|---|---|---|---|---|---|

- Conclusion:
- Limitations:
- Reviewer:
```

### 20.6 Asset Lineage Report 模板

```markdown
# ALR-<序号> <Target Asset>

- Target Asset ID / Type / Revision:
- Query Scope / As-of / Version Boundary:
- TLR / C11 Snapshot and Digest:
- Query Rule / Tool Version:
- Query Completeness / Limitations:

| Node ID@Rev | Type | State | Owner | Locator | Access |
|---|---|---|---|---|---|

| Link ID | Source Node | Relation | Target Node | Member State | Effective Range | Basis |
|---|---|---|---|---|---|---|

- Source / Derivation:
- Generation Run / Tool:
- Implementation:
- Verification / Validation:
- Observation:
- Release:
- Supersession / Replacement:
- Branch / Merge / Cycle / Broken Link / Access Gap:
```

### 20.7 Untracked Change Report 模板

```markdown
# UCR-<序号> <Changed Asset>

- Changed Asset ID / Type / Revision:
- Repository / Workspace / Environment:
- Base / Result Snapshot / Commit / Diff:
- Discovery Method / Run / Time:
- Missing Source Type:
- Change Source Status:
- Potential Direct / Indirect / Unknown Impact:
- Affected Assets:
- Risk ID / Current Risk:
- Owner:
- Containment:
- Disposition Decision:
- Required Trace / Requirement / Decision / Change / Incident:
- Backfill or Revert Deadline:
- Verification / Configuration / Gate Evidence:
- Resolution / Closure Criteria:
- CASE State / History:
```

### 20.8 Orphan Artifact Report 模板

```markdown
# OAR-<序号> <Orphan Asset>

- Orphan Asset ID / Type / Revision / State:
- Orphan Type:
- Expected Relationship Profile:
- Missing Relation:
- Lifecycle Stage / Gate / Expected By:
- Detection Rule / Tool / Time:
- Current Links:
- Impact / Risk:
- Owner:
- Disposition:
- N/A Decision / Approver:
- Due Date:
- Closure Criteria / Evidence:
- CASE State / History:
```

### 20.9 Impact Query Result 模板

```markdown
# IQR-<序号> <Query Purpose>

- Root Asset ID / Type / Revision:
- Query Time / As-of Time:
- Direction / Relation Set:
- Max Depth / Stop Rules:
- Scope / State Filter / Version Filter:
- TLR / C11 Snapshot / Input Digest:
- Query Engine / Rule Version:
- Executor / Start / End:
- Query Completeness:

## Results
| Impact Distance | Asset ID@Rev | Type | Link Path | Impact | Unknown / Gap |
|---|---|---|---|---|---|

- Cycle / Duplicate / Dangling / Access Gap:
- Result Count / Truncation:
- Proposed Actions:
- Correction / Supersession Reference:
```

### 20.10 关系方向速查表

| 问题 | 应使用关系 | 方向示例 |
|---|---|---|
| 本资产来源是什么 | derives-from | REQ → Need/Feature |
| 本资产处理什么问题 | addresses | Design/Decision → Problem/Risk |
| Requirement 由什么设计覆盖 | designed-by | REQ → Design |
| Requirement/Design 由什么实现 | implemented-by | REQ/Design → Code/Config |
| Requirement 如何验证 | verified-by | REQ/Criterion → VER |
| Need/Intent 如何确认 | validated-by | Need/Intent → VAE |
| 资产在哪个发布中 | released-in | Asset → Release Configuration |
| 资产由什么 Run 生成 | generated-by | Asset → RUN |
| Finding 来自什么观察 | observed-from | Finding/Evidence → RUN/Observation |
| 新对象替代旧对象 | supersedes / replaces | New → Old |

### 20.11 Link 变化判定表

| 变化 | 旧 Link | 新动作 |
|---|---|---|
| 端点 Editorial Revision，语义不变 | Suspect | Owner 确认后新 Link Revision 恢复 Active |
| 端点 Semantic Revision | Suspect | 重新验证；必要时新 Link ID |
| Source/Target/Relation 改变 | Retired/Invalid | 建立新 Link ID |
| Effective Range 扩大 | Suspect | 影响分析、批准、新 Link Revision |
| Decision Superseded | Suspect | IQR，重建或 Retire 下游 Link |
| 候选被否定 | Rejected | 保留最小历史 |
| 历史正确但不再适用 | Retired | 保留有效期和退役原因 |
| 原 Link 错误 | Invalid | 新建正确 Link，互相引用 |

### 20.12 Coverage 计算工作表

```markdown
| Requirement ID@Rev | Eligible? | Source | Design | Implementation | Verification | Release | N/A Basis / Approver | End-to-End | Gap Owner |
|---|---|---|---|---|---|---|---|---|---|

Applicable = Eligible Total - Approved N/A
Coverage % = Covered / Applicable × 100
Applicable = 0 → N/A
Partial / Unknown / Suspect → not Covered
```

### 20.13 Impact Query 参数与算法

```text
INPUT:
  root_asset_id, root_revision
  direction
  allowed_relations
  max_depth
  scope
  as_of_time
  state_filter
  version_filter
  stop_rules

PROCESS:
  resolve root against fixed snapshots
  traverse links permitted by state_filter
  default state_filter = Active + Suspect
  record direct and indirect paths
  deduplicate visited link + asset revision
  detect cycles, dangling endpoints and access gaps
  stop at max depth, scope boundary or stop rule
  mark unknown and truncation

OUTPUT:
  immutable IQR with parameters, snapshots, paths,
  direct/indirect/unknown impacts and completeness
```

### 20.14 质量检查清单模板

```markdown
| Check ID | 检查对象 | 通过条件 | 结果 | Evidence / Finding |
|---|---|---|---|---|
| C10-QC-001 | 八类产物 | 身份、State、Revision、History 独立 | 待检查 | |
| C10-QC-002 | DEC | Question/Options/Choice/Rationale/Impact/Authority 完整 | 待检查 | |
| C10-QC-003 | TLR | Link ID、端点、关系、Basis、范围和状态完整 | 待检查 | |
| C10-QC-004 | Relation | 名称受控、方向和端点类型正确 | 待检查 | |
| C10-QC-005 | Revision | Drift 触发 Suspect 和复核 | 待检查 | |
| C10-QC-006 | Graph | 无 Duplicate、禁止 Cycle、Dangling | 待检查 | |
| C10-QC-007 | BTM | 同一 Snapshot 双向一致 | 待检查 | |
| C10-QC-008 | Coverage | 分母、N/A、Unknown、阈值可复算 | 待检查 | |
| C10-QC-009 | Lineage | 来源到发布/替代可重建 | 待检查 | |
| C10-QC-010 | UCR | 未倒签，处置和 Evidence 完整 | 待检查 | |
| C10-QC-011 | OAR | 生命周期 Profile 正确，关闭有 Evidence | 待检查 | |
| C10-QC-012 | IQR | 参数、路径、Unknown、完整性和 REC 身份完整 | 待检查 | |
| C10-QC-013 | Automation | LLM/概率建议未自动激活 | 待检查 | |
| C10-QC-014 | Boundary | C04/C05/C09/C11/C12/E04 事实源未重定义 | 待检查 | |
| C10-QC-015 | P2/E04 | 未裁剪；访问、保留、更正和历史完整 | 待检查 | |
```

### 20.15 正反例

正例：

> DEC-0031 记录“采用事件驱动还是同步调用”的单一问题，比较三项候选方案，引用 REQ-042 Revision 3、TDS-009 Revision 2 和 RSK-0017。Decision Authority 批准后，REQ-042 `designed-by` TDS-009，TDS-009 `implemented-by` CCS-018，REQ-042 `verified-by` VER-024，相关资产 `released-in` RCF-006。所有 Link 来自 TLR-0001 Snapshot 17，BTM 可双向查询；RCR 披露 Applicable=46、Covered=44、Unknown=2；Change 前 IQR-0081 固定关系集、深度、Snapshot 和 Unknown。旧 DEC-0012 被 supersedes 并保留。

反例：

> AI 根据文件名相似度自动把所有文档和代码关联，显示追踪率 100%；某段代码没有需求，后来补了一个链接，所以不算未跟踪；架构决定已更新到原 ADR 文件，旧内容没有保留。

反例没有端点 Revision、受控关系、Basis、Reviewer、分母、Unknown、UCR、Impact Query 或替代历史，并把概率推断和事后补链当作授权事实，禁止进入 Trace Ready。

### 20.16 参考的国际标准条款映射总表

| 国际标准 | 条款或官方公开项目 | 本规范落地位置 | 采用方式 | 复核限制 |
|---|---|---|---|---|
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | 1 Scope | 第 2–4、8.4、18 章 | 将需求过程和信息项的追踪要求覆盖到全生命周期 | 不声明完整 29148 符合 |
| ISO/IEC/IEEE 29148:2018 | 3.1.22 Requirements management | 第 6、9.4–9.6、10.8–10.10 章 | Link 随 Requirement 全生命周期维护、追踪和失效 | Requirement 内容由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 3.1.23 Requirements traceability | 第 2、6、8.2、10.7、10.11 章 | 同时建立向上来源路径与向下分配/实现路径 | 只使用项目受控关系 |
| ISO/IEC/IEEE 29148:2018 | 3.1.24 Requirements traceability matrix | 第 8.1、10.11、13.4、20.4 章 | BTM 从同一 TLR Snapshot 双向投影 | BTM 不成为第二事实源 |
| ISO/IEC/IEEE 29148:2018 | 4.1–4.5 Conformance and tailoring | 第 17、19 章 | P2 裁剪保留身份、关系、Coverage 和检查 | 未取得全文，不作标准符合性声明 |
| ISO/IEC/IEEE 29148:2018 | 5.2 Requirements fundamentals | 第 8.2、10.7、10.13、14 章 | Requirement 使用永久身份、明确来源和质量 Link | Requirement 质量仍由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 5.4 Requirement information items | 第 8.1、12–13、20.1–20.5 章 | 追踪信息项具备身份、版本、责任和内容模板 | 不复制标准信息项结构 |
| ISO/IEC/IEEE 29148:2018 | 6.3–6.4 Needs/System/Software requirements definition | 第 8.2、10.13、18 章 | 建立 Need、Requirement、Design 和实现的分层链 | 不替代 C01/C04 |
| ISO/IEC/IEEE 29148:2018 | 6.5 Requirements activities in other technical processes | 第 10.13–10.17、18 章 | 接入 Design、Implementation、Verification、Change 和 Release | 过程事实源保持独立 |
| ISO/IEC/IEEE 29148:2018 | 6.6 Requirements management | 第 9.4–9.6、10.8–10.13、16 章 | 管理 Link Revision、Suspect、Coverage、Change 和审计 | 公开目录未展开子条款 |
| ISO/IEC/IEEE 29148:2018 | 7–8 Information items and guidelines | 第 12–14、20.1–20.9 章 | 八类产物具备必填信息、模板和质量要求 | 模板是项目实现，不是标准原文 |
| [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) | 1 Scope | 第 3–4、8.4、17.3 章 | Decision/Correspondence 支持架构描述接口 | C10 不建立完整 Architecture Description |
| ISO/IEC/IEEE 42010:2022 | 3.11 Correspondence | 第 6、8.2–8.3、10.7、20.10 章 | 关系可识别、命名、定向并有语义 | 项目关系名称由公共基线固定 |
| ISO/IEC/IEEE 42010:2022 | 5.2 Conceptual models of an architecture description | 第 8、10.12、10.14 章 | Node/Edge、View 和对应关系保持一致 | 不复制标准概念模型 |
| ISO/IEC/IEEE 42010:2022 | 5.3 Architecture description in the life cycle | 第 9、10.6、10.17、18 章 | Decision 和架构关系随生命周期、Change 和替代维护 | 架构过程由 C06/E01 管理 |
| ISO/IEC/IEEE 42010:2022 | 6.1–6.8 Architecture description elements | 第 10.2–10.5、13.2、17.3 章 | Decision 引用 Stakeholder、Concern、View 和受影响元素 | 只管理关系与 rationale |
| ISO/IEC/IEEE 42010:2022 | 6.9 Recording of architecture correspondences | 第 8.2、10.7–10.12、13.3–13.4 章 | 架构对应关系进入 TLR 并支持双向查询 | 公开预览未提供完整要求正文 |
| ISO/IEC/IEEE 42010:2022 | 6.10 Recording of architecture decisions and rationale | 第 9.3、10.2–10.6、13.2、20.2 章 | DEC 记录 Context、Options、Choice、Rationale、Impact 和替代 | MADR 仅作表达参考 |
| ISO/IEC/IEEE 42010:2022 | 7.1–7.2 ADF/ADL specification | 第 10.12、16.1、17.3 章 | 关系 Profile、规则和工具版本受控 | C10 不规定具体建模语言 |
| [ISO 10007:2017](https://www.iso.org/standard/70400.html) | 1 Scope | 第 3–4、8.4、18 章 | Trace/Lineage 覆盖产品从概念到处置 | 配置事实源由 C11 管理 |
| ISO 10007:2017 | 4.1 Responsibilities and authorities | 第 7、10.4、15 章 | Decision、Trace、Configuration、Review 职责明确 | 不复制组织职责体系 |
| ISO 10007:2017 | 4.2 Dispositioning authority | 第 10.6、10.10、16.3–16.4 章 | 替代、退役、更正和处置由有权角色决定 | 处置同时受 E04 约束 |
| ISO 10007:2017 | 5.2 Configuration management planning | 第 9.2、10.8、16.1、17 章 | 预先定义关系 Profile、Coverage、Rule 和审计 | 不替代 C11 计划 |
| ISO 10007:2017 | 5.3 Configuration identification | 第 8.3–8.4、10.1、10.8、13 章 | 固定 Asset ID、Revision、Snapshot 和有效范围 | Git Commit 不替代业务身份 |
| ISO 10007:2017 | 5.4 Change control | 第 9.6、10.6、10.16–10.17、16.1 章 | Change 前 Impact Query，变化后 Link 重新判定 | Change Approval 由 C11/C12 管理 |
| ISO 10007:2017 | 5.5 Configuration status accounting | 第 9.4–9.5、11、13.3、16.2 章 | 记录 Link/Decision/Report 状态、时间和历史 | 不建立平行配置状态记录 |
| ISO 10007:2017 | 5.6 Configuration audit | 第 14–16、19 章 | 审计身份、关系、Coverage、Lineage、Impact 和更正 | 不构成完整配置审计 |
| ISO 10007:2017 | Annex A Configuration management plan structure | 第 9.2、20.10–20.14 章 | 关系 Profile、检查和模板作为策划输入 | Annex A 为附录；项目模板非标准原文 |
| [ISO 15489-1:2016](https://www.iso.org/standard/62542.html) | 1 Scope | 第 3、8.4、16、17.3 章 | Decision、Link、Query 和报告作为跨环境记录管理 | E04 管理组织级记录体系 |
| ISO 15489-1:2016 | 4 Principles for managing records | 第 8、10.10、16.2–16.4 章 | 保留真实性、完整性、可用性、历史和处置证据 | 不覆盖组织全部记录 |
| ISO 15489-1:2016 | 5.2 Records | 第 6、8.1、11.4、16.3 章 | 区分正式产物、成员、派生报告和不可变查询记录 | 摘要不替代原始记录 |
| ISO 15489-1:2016 | 5.3 Records systems | 第 8.4、9.2、10.18、16.1 章 | TLR/报告系统具备规则、版本、访问和审计 | 不规定物理技术 |
| ISO 15489-1:2016 | 6.2 Policies | 第 9.2、10.19、16.4、17 章 | 建立 Trace、Access、Retention 和自动化策略 | 策略批准由组织治理执行 |
| ISO 15489-1:2016 | 6.3 Responsibilities | 第 7、10.4、15、16 章 | Owner、Steward、Authority、Reviewer 和 Records 责任明确 | Agent 不能替代人类问责 |
| ISO 15489-1:2016 | 6.4 Monitoring and evaluation | 第 9.6、10.10–10.18、14、19 章 | 监测失效、Coverage、Orphan、UCR 和工具质量 | 指标不自动决定 Gate |
| ISO 15489-1:2016 | 6.5 Competence and training | 第 7、15.1、17.3 章 | 评审者具备领域、配置和记录能力 | 不建立组织培训方案 |
| ISO 15489-1:2016 | 7.2–7.5 Appraisal and records requirements | 第 9.2、10.19、16.4、17.3 章 | 按用途、Risk、义务和生命周期确定记录要求 | 具体 Retention 由 E04 决定 |
| ISO 15489-1:2016 | 8.2 Metadata schemas for records | 第 10.1、13、16.2、20.1–20.9 章 | 保存 ID、Actor、Time、Source、Revision、Access 和 History | 不定义物理 Schema |
| ISO 15489-1:2016 | 8.3 Business classification schemes | 第 5.2、8.1、11、13 章 | 使用正式产物类型、领域值和状态模型分类 | 禁止创建平行产物类型 |
| ISO 15489-1:2016 | 8.4 Access and permissions rules | 第 10.19、13、16.4、17.3 章 | 最严格分类、最小披露、遮蔽和跨边界授权 | 公开 OBP 预览止于 8.4 |
