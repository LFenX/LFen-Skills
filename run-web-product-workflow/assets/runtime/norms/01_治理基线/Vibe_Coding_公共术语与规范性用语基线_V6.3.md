# Vibe Coding 公共术语与规范性用语基线 V6.3 Candidate

| 文档属性 | 内容 |
|---|---|
| 文档编号 | VC-PPG-COM-001 |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 生效日期 | 待评审；V6.2/V6.2.1 历史由 Git 保留 |
| 变更来源 | CHG-0006、IMA-0003、CHD-0004 Proposed |
| 责任人 | 项目负责人 |
| 上位基线 | 尚未建立；V6.3 Candidate 不替代现有 Baseline |
| 适用范围 | C01 至 C12、E01 至 E05 及其模板、记录、检查清单和报告 |

## 1. 目的

本文件建立跨规范唯一术语、规范性用语、产物命名和关系语义，防止同义对象并行、术语漂移和跨规范引用冲突。

本文件中的中文名称用于解释，英文正式名称用于六类元类型、领域 Profile、模板标题和跨规范引用。禁止在正式规范中另建语义相同但名称不同的对象。

## 2. 规范性用语

| 用语 | 含义 | 使用规则 |
|---|---|---|
| 必须 | 满足规范的强制条件 | 必须能够通过文档、规则、证据或检查直接判定 |
| 禁止 | 不得发生的行为 | 必须同时明确违规对象或行为 |
| 应 | 默认强制执行，可经批准偏离 | 偏离时必须有理由、风险、责任人、批准人和失效时间 |
| 不应 | 默认不得执行，可经批准采用 | 采用时必须建立例外记录 |
| 可以 | 允许采用的方式 | 不构成强制要求 |
| 可选 | 由适用性和风险决定 | 必须先执行适用性判定 |

禁止使用“尽量”“最好”“酌情”“快速”“合理”“适当”“充分”等不可验证词语，除非同一句或同一规则中给出可复核的判定条件。

## 3. 信息类型

| 信息类型 | 定义 | 强制标识规则 |
|---|---|---|
| Fact | 已被直接观察或由可复核来源支持的事实 | 必须引用来源和观察时间 |
| Evidence | 支持或反驳需要、问题、假设、要求或结论的可复核材料 | 必须说明收集方法、范围、局限性和可靠性 |
| Source | 受控信息直接取自、观察自、生成自或接收自的资产、主体、系统、事件或记录 | 必须具有可定位身份、Owner 和适用时间 |
| Provenance | Source 经获取、生成、处理、转换和使用形成的可追踪历史事实 | 必须记录责任主体、时间、方法、版本和使用限制 |
| Inference | 从事实或证据推导出的解释 | 必须与事实分开，并说明推导依据 |
| Recommendation | 非强制建议 | 禁止使用“必须”或“禁止”表达 |
| Example | 用于解释规则的非规范性实例 | 必须标记为示例，不得作为唯一要求来源 |

### 3.1 跨规范术语 Authority 路由

下列术语的唯一正式定义由指定 Source ID 维护。本文件只提供路由，不复制专业定义；非 Authority 规范必须引用，专业含义不同必须使用限定名称。

| 不带限定词的术语 | 唯一 Authority | 非 Authority 使用规则 |
|---|---|---|
| 必须、禁止、应、不应、可以、可选 | VC-PPG-COM-001 §2 | 直接适用，不得重定义 |
| Evidence、Source、Provenance | VC-PPG-COM-001 §3 | 专业域使用限定名称并声明父概念 |
| Success Metric、Guardrail Metric、Context of Use | C01 | Initiative 指标使用限定名称；C05/C06 引用 C01 |
| Agent Modification Boundary、Assumption、Constraint、Risk、Residual Risk、Dependency | C02 | 产品或专业依赖使用限定名称 |
| Requirement | C04 | 公共基线和其他规范只引用 |
| Verification Method | C05 | C04 等规范只保存方法引用 |
| Concern、Viewpoint、View | C06 | 架构专业域使用 Architecture 限定名称 |
| Independence | C07 | 验证专业域使用 Verification Independence |
| Architecture、Architecture Description | E01 | C06 在 Architecture Surface 下引用 E01 |
| Decision、Rationale | C10 | 专业域使用限定名称 |
| Rollback | C11 | 执行和服务域使用限定名称 |
| Recovery | C11/E05 | 不保留无限定通用定义；分别使用 Configuration Recovery、Service Recovery |
| Threshold | C12 | 数据与 AI 域使用 Data/AI Evaluation Threshold |
| Record | E04 | 配置域使用 Configuration Record |

## 4. 核心对象术语

| 正式英文名称 | 中文名称 | 唯一定义 | 不得混同对象 |
|---|---|---|---|
| Product Asset | 产品资产 | 在产品生命周期中受控的意图、规格、执行、证据或学习对象 | 文件、数据库记录或聊天消息只是载体，不自动等同于资产 |
| Meta Type | 元类型 | V6.3 对治理对象的六类正式顶层分类：ProjectState、TaskContract、RunLedger、TaskOutcome、AuthorityAsset、DerivedView | `legacy_kind`、领域 Profile、文件格式 |
| Domain Profile | 领域 Profile | C01 至 C12、E01 至 E05 对专业语义、字段和领域状态的兼容约束；V6.2/V6.2.1 的137个代码均转为 Profile | 顶层元类型、独立物理文件 |
| Project State | 项目状态 | 从有效 TaskOutcome 与当前 AuthorityAsset 自动物化的跨任务当前事实、遗留问题和依赖视图 | 人工维护的第三份事实源 |
| Task Contract | 任务执行契约 | Run 开始前提供目标、范围、权限、验收、计划、前置事实和任务关系的受控输入 | 任务终态、项目长期需求 |
| Run Ledger | 最小运行账本 | 只追加记录 Git 无法完整表达且对复核有价值的变更、失败、验证、外部副作用和门禁事件 | 全量终端历史、所有读取和搜索 |
| Task Outcome | 任务终态 | 记录本任务已成立事实、实际变化、验证、未完成项、遗留问题和后续任务的终态对象 | 执行前指令或项目总状态 |
| Authority Asset | 权威资产 | 需求、设计、决策、证据、策略和基线等长期事实的唯一权威对象，可保留原生格式 | 自动生成的审核视图 |
| Derived View | 派生视图 | 从权威对象按固定规则生成、可重建的报告、矩阵、清单或索引 | 新权威事实或批准决定 |
| Stakeholder Need | 利益相关方需要 | 利益相关方在特定情境下期望获得的结果或避免的损失 | Requirement、Feature、Solution |
| Problem Definition | 问题定义 | 基于证据描述当前情境、期望情境、影响和边界的受控对象 | 解决方案、Feature |
| Product Definition | 产品定义 | 对产品服务对象、核心价值、系统边界、主要能力和非目标的稳定说明 | 单次 Initiative 或 PRD |
| Product Intent | 产品意图 | 产品期望造成的方向性变化及其原因 | Product Goal、Feature |
| Product Goal | 产品目标 | 在规定时间范围内可观察或可验证的目标结果 | Task、输出数量 |
| Initiative | 建设事项 | 为实现一个或多个产品目标而设立的可独立治理建设单元 | PRD、Feature、Project Task |
| Scope Boundary | 范围边界 | 对 In Scope、Out of Scope、Future Scope 和修改边界的正式约束 | Non-goal、Requirement |
| PRD Package | PRD 包 | 对一个可独立评审、实现、验证和发布范围的规格集合及索引 | 整个产品永久总文档、Requirement 集合的复制品 |
| Feature | 功能能力 | 用户或业务可感知且可独立组织交付的能力 | Requirement、技术任务、页面 |
| User Scenario | 用户场景 | 特定用户在特定情境下为获得结果而执行的活动序列 | Acceptance Criterion、测试用例 |
| Requirement Set | 需求集合 | 处于同一受控范围并接受整体质量检查的 Requirement 集合 | PRD 正文 |
| Acceptance Criterion | 验收标准 | 针对 Requirement 定义可观察通过条件的受控对象 | Test Case、Validation Evidence |
| Verification | 验证 | 确认实现或产物是否满足已规定要求 | Validation |
| Validation | 确认 | 确认产品在预期使用情境中是否满足实际需要和意图 | Verification |
| UX Design Specification | UX 设计规格 | 将用户、场景、流程、页面、组件、内容和交互状态形成的可实现规格 | 原型文件本身、Requirement |
| Technical Design Specification | 技术设计规格 | 将 Requirement 转化为系统边界、组件、数据、接口、权限和质量实现约束的规格 | 代码、架构决策本身 |
| Collaboration Contract | 人机协作契约 | 对人类与 Agent 的职责、权限、审批、停止和升级规则的正式约定 | 单次 Agent 任务提示词 |
| Coding Agent | 编码 Agent | 在受控上下文和授权范围内执行规格分析、代码修改、验证或记录任务的 AI 执行主体 | 人类责任人、最终批准人 |
| Agent Context | Agent 上下文 | Agent 某次执行可读取且影响执行的受控信息集合 | Agent Run、聊天历史全集 |
| Stable Context | 稳定上下文 | 跨多次执行持续有效的已批准规范、基线、约束、术语和长期决策 | 当前任务和工具输出 |
| Execution Context | 执行上下文 | 仅对当前任务或 Agent Run 有效的 Requirement、Scope、工作区快照、工具结果和临时假设 | 稳定基线 |
| Agent Run | Agent 执行实例 | 具有唯一 Run ID、明确输入、开始与结束时间、动作、变更和验证结果的一次执行 | Agent 角色、模型产品 |
| Decision Record | 决策记录 | 记录背景、问题、候选方案、选择、理由、影响和替代关系的受控资产 | 私有思维链、聊天讨论全文 |
| Trace Link | 追踪关系 | 由明确关系类型连接两个受控资产的可查询关系 | 无语义的“相关”链接 |
| Asset Lineage | 资产血缘 | 资产的来源、派生、实现、验证、替代、生成、观察和发布关系集合 | 单一时间线 |
| Configuration Item | 配置项 | 需要被唯一标识、版本化、基线化和受控变更的资产 | 所有临时草稿 |
| Version | 版本 | 用于识别资产内容状态或发布状态的标记 | 永久资产身份 |
| Revision | 修订 | 同一资产身份下经记录的内容变化 | 新资产、新 Requirement |
| Snapshot | 快照 | 某一时间点资产完整状态的不可变表示 | 当前可编辑文件 |
| Baseline | 基线 | 经批准并固定、后续只能通过受控变更修改的资产版本集合 | 普通 Git 工作区状态 |
| Change Request | 变更申请 | 对已批准或已基线资产提出受控改变的控制记录 | 新 Requirement、Defect、Task |
| Defect | 缺陷 | 实现或产物未符合已批准 Requirement 的偏差 | 新 Requirement、需求澄清 |
| Engineering Change | 工程变更 | 不改变外部已批准义务的技术改进、重构或技术债处理 | Product Requirement |
| Quality Gate | 质量门禁 | 资产或活动进入下一状态前必须满足的受控条件集合 | 普通检查清单 |
| Gate Decision | 门禁决议 | 对特定门禁实例作出的通过、条件通过、拒绝或豁免决定 | Review Record |
| Risk Acceptance | 风险接受 | 由授权人明确接受剩余风险及其范围、期限和监控条件的决定 | 风险不存在或风险已解决 |
| Product Health | 产品健康 | 通过定义明确、来源可查、周期和阈值受控的指标评价产品与过程状态 | 单一 KPI 或主观评价 |
| Learning Record | 学习记录 | 将运行结果、反馈、事故或验证偏差转化为可追踪结论和后续行动的记录 | 聊天总结 |

## 5. 需求演进术语

| 正式名称 | 判定条件 | 身份与版本处理 |
|---|---|---|
| Clarification or Patch Event | 消除歧义、补充遗漏或明确边界，不改变原业务意图和独立义务 | 保持 Requirement ID；建立事件和新快照 |
| Requirement Revision | 在同一业务意图下改变行为、约束或验收含义 | 保持 Requirement ID；产生新修订；已基线时执行 Change Request |
| New Requirement | 引入新的、可独立验证的业务义务或利益相关方结果 | 创建新 Requirement ID；建立 `derives-from`、`extends` 或 `replaces` 关系 |
| Defect Fix | 修复实现对已批准 Requirement 的不符合 | 建立 Defect 和修复记录；禁止创建新 Requirement 代替 |
| Technical Refactoring | 外部行为和验收保持不变的内部改进 | 建立 Engineering Change 或技术债记录；禁止创建产品 Requirement 代替 |
| Requirement Supersession | 原 Requirement 不再有效且由另一 Requirement 接替 | 保留原 ID 和历史；建立 `supersedes` 或 `replaces` 关系 |

## 6. Profile 命名消歧

下表对两份蓝图中存在的简称、集合名和领域 Profile 名进行统一。左列名称不得再作为独立 Profile 创建。

| 蓝图简称或集合名 | 唯一处理方式 | 正式产物名称 |
|---|---|---|
| Product Intent Brief | 仅为 P1 合并载体；P2 禁止作为替代产物 | Stakeholder Need Record、Evidence Record、Problem Definition、Product Definition、Product Intent & Goal Record、Assumption Register |
| Assumption & Risk Register | 产物域集合名，不是独立产物 | Assumption Register、Assumption & Constraint Register、Risk Register |
| Context Manifest | C08 产物类别简称，不是独立产物 | Stable Context Manifest、Execution Context Package |
| Execution Plan | C09 简称 | Agent Execution Plan |
| Change Summary | C09 产物类别简称 | Changed Artifact Summary、Code Change Summary |
| Validation Report | C09 的执行验证报告 | Validation Report；不得与 Validation Evidence Record 混同 |
| Coverage Matrix | C05 的正式产物；跨规范引用时写作 `C05 Coverage Matrix` 以消除歧义 | Coverage Matrix |
| Traceability Matrix | C10 简称 | Bidirectional Traceability Matrix |
| Requirement Coverage Report | C10 报告 | 不得替代 C05 Coverage Matrix |
| Version Record | C11 允许名称 | Version or Revision Record |
| Review & Health Log | 仅为 P1 合并载体；P2 禁止作为替代产物 | Review Record、Gate Decision、Product Health Report 及关联产物 |
| Security Verification | 跨规范矩阵简称 | Security Verification Plan 和相应 Verification Evidence Record |
| Data Quality Report | 跨规范矩阵简称 | AI Data Quality Report；非 AI 数据使用 Data Quality Specification 的评价结果记录 |

正式规范引用集合名时，必须明确其包含的正式产物；禁止为集合名分配新的永久资产身份。

## 7. 标识规则

AuthorityAsset 和兼容 Profile 的永久标识采用以下概念格式：

```text
<legacy_kind/profile代码>-<顺序号>
```

规则如下：

1. Profile 代码由《受控产物元模型、领域 Profile 与状态模型》唯一规定。
2. 顺序号在所属产品或明确命名空间内唯一，创建后不得修改或复用。
3. 版本、日期、状态、负责人和标题禁止写入永久标识。
4. 文件名、数据库主键、URL 和 Git 提交哈希不得替代业务资产永久标识。
5. 同一资产修订时保持永久标识；新独立义务或新独立治理对象必须创建新标识。
6. 被替代、拒绝、废弃或删除的标识永久保留。

任务执行身份使用独立链：`ProjectID → WorkItemID → TaskID → RunID → AttemptID`。`TaskID`表示项目内可排序、可依赖的子任务；必须显式记录 `ordinal`、`depends_on`、`supersedes` 和 `blocked_by`，禁止用文件名或自然顺序替代依赖关系。

## 8. 受控关系语义

| 关系 | 方向语义 | 使用限制 |
|---|---|---|
| derives-from | 当前资产派生自上游资产 | 不表示替代 |
| addresses | 当前资产处理某 Need、Problem、Risk 或 Concern | 必须说明处理范围 |
| contains | 集合或包包含成员资产 | 不得替代成员的独立身份 |
| refines | 当前资产细化上游资产且不改变其原意 | 改变原意时必须使用修订或变更 |
| extends | 当前资产增加独立义务或能力 | 新对象必须有独立身份 |
| depends-on | 当前资产的有效性或执行依赖另一资产 | 必须说明依赖条件 |
| constrains | 当前资产限制另一资产的可选范围 | 必须引用约束来源 |
| designed-by | Requirement 由设计元素覆盖 | 目标必须是受控设计资产 |
| implemented-by | Requirement 或设计由实现资产实现 | 目标必须可定位到代码、配置或部署资产 |
| verified-by | Requirement 或 Criterion 由验证证据证明 | 不表示满足真实用户需要 |
| validated-by | Need、Intent 或 Goal 由确认结果支持 | 不得替代 Verification |
| released-in | 资产包含于某发布配置 | 必须指向可重建发布 |
| affected-by | 资产受事件、风险或变更影响 | 必须说明影响类型 |
| supersedes | 当前资产使旧资产退出当前有效集合 | 旧资产必须保留 |
| replaces | 当前资产直接接替旧资产的职责或义务 | 必须记录生效边界 |
| generated-by | 资产由 Agent Run、工具或过程生成 | 不代表已批准 |
| observed-from | 学习、问题或证据来自运行观察 | 必须保留观察来源 |

禁止使用无受控语义的 `related-to` 或中文“相关”。现有资料只能确定存在关联但无法判断语义时，必须建立待处理的 Trace Link 问题，不得创建模糊正式关系。

## 9. 名称与语言规则

1. 六类元类型使用本文件规定的英文名称；领域 Profile 使用《受控产物元模型、领域 Profile 与状态模型》规定的英文名称和兼容代码。
2. 中文翻译用于说明，不建立第二元类型或第二 Profile。
3. Requirement、Feature、PRD、Change Request、Defect、Task 和 Decision 必须保持独立语义。
4. Verification 与 Validation 必须分别记录。
5. Agent Context、Agent Run、Agent Role 和 Agent Decision 不得互换。
6. Patch、Revision、Change Request、New Requirement、Defect Fix 和 Technical Refactoring 必须按第 5 章分类。
7. 标准、规范、策略、计划、记录、报告、登记册、矩阵和清单的后缀必须与产物用途一致。
8. 模板不是正式实例；检查清单不是 Gate Decision；报告不是原始证据。

## 10. 冲突处理与优先级

正式规范生成期间的术语与命名优先级如下：

```text
VC-PPG-BP-001 与 VC-PPG-BP-002 的明确对象定义
  > 已批准的前置治理决议
  > 本公共术语与规范性用语基线
  > 受控产物目录与状态模型
  > 单项正式规范中的局部说明
  > 模板、示例和非规范性实践参考
```

两个上位蓝图相互冲突时，不得使用上述优先级擅自选择其一；必须停止相关扩写并建立冲突报告。局部规范不得重定义本文件中的公共术语，只能引用或增加不冲突的领域限定。

## 11. 符合性检查

正式规范或模板只有在满足以下条件时才通过术语检查：

- 每个正式产物名能在受控产物目录中唯一定位；
- 未把第 6 章集合名创建为独立产物；
- 需求演进类型与身份处理一致；
- 关系类型来自第 8 章且方向正确；
- 规范性语句可以客观判断；
- 未用模板、示例、聊天、工具输出或 Agent 私有推理替代正式记录；
- 未创建同义但不同名的平行对象。

## 12. 任务裁剪与产物实例化术语

### 12.1 Task Profile

`Task Profile` 是 Agent 基于人类最小输入、当前环境和稳定 Baseline 形成的任务适用性判定，不是新的元类型或 Profile。它作为 TaskContract（`before.json`）中的受控字段存在；旧 ECP/AEP/SCP 只通过 `legacy_kind` 兼容读取。

| 维度 | 受控值或判定范围 |
|---|---|
| Delivery Scenario | DS-01 新产品；DS-02 产品族/模板派生；DS-03 现有产品演进；DS-04 运行中产品处置 |
| Development Type | DT-01 新产品；DT-02 产品族实例化；DT-03 新功能；DT-04 需求澄清；DT-05 需求修订；DT-06 缺陷修复；DT-07 工程变更；DT-08 配置/内容变更；DT-09 迁移/替代/退役 |
| Change Surfaces | UI/UX、API/Integration、Data/Schema、Identity/Security/Privacy、AI/Data Governance、Architecture/Multi-repo、Deploy/Operations、Agent/Collaboration |
| Risk Level | 只使用 C02 的 Low、Medium、High、Critical |
| Extension Triggers | 逐项判定 E01、E02、E03、E04、E05；Unknown 必须保持待判定 |
| Extension Evidence Refs | E01-E05 各自的证据引用数组；Retiring/Retired 必须非空 |
| Baseline Inheritance | New、Reference、Revise、Supersede |
| Execution Mode | Normal、Emergency；Emergency 不改变 Development Type |
| Applicability Facts | VC-PPG-TAIL-001 定义的事实键；值只使用 Yes、No、Unknown |
| Authority Assessment | Authority 引用的结构化有效性评估；包含来源类型、状态、精确作用域、Evidence、验证时间和过期时间 |

Task Profile 必须包含判定依据、置信度、未决问题和生成时使用的 Source Snapshot。影响执行边界、不可逆变更、High/Critical Risk、批准或发布的未知项不得使用静默默认值。

`Applicability Fact` 是对规范触发事实的显式三值判定，用于补足 DS、DT 和 Surface 无法表达的业务或治理条件。Unknown 表示尚未证明 Yes 或 No，不表示 Inactive 或 N/A。

`Tailoring Resolution` 是 VC-PPG-TAIL-001 根据完整 Task Profile 和当前 Stage 计算的确定性快照，作为 TaskContract 的 `tailoring_resolution` 字段存在，不是第七类元类型或新的 AuthorityAsset。它至少包含规则表版本/哈希、输入摘要、适用/待判定规范、控制强度、阻断原因、规则 ID、源章节定位和 Profile 覆盖摘要。Task Profile、规则表或 Source Snapshot 变化后旧快照失效。

`Authority Assessment` 是 TaskContract 中对 Authority Reference 的执行前评估，不是新的批准决定。机器可检查引用绑定、状态、证据非空、有效期和作用域覆盖；Evidence 的真实性、授权主体的组织权限和文本作用域的业务语义仍必须由 Authority 事实源、独立 Review 或人类 Gate 验证。

`Execution Permission` 是 TaskContract 执行前 Authority 的受控动作边界，值固定为 `read`、`edit-in-scope`、`validate`、`external-effect`、`rollback`。它只证明计划和记录层权限；工具调用仍必须遵守 `allowed_paths`、`forbidden_actions`、平台权限和 Stop Condition。

### 12.2 Artifact Manifest

`Artifact Manifest` 是 Task Profile 对元类型/Profile 实例的动作清单，不是第二套目录，也不是独立物理产物。执行前计划保存在 `before.json`；实际结果保存在 `after.json`，必须保留全部执行前项并允许追加收尾时实际创建、修订、引用或生成的资产。未在执行前预见的追加项必须记录实际 Outcome；若在 TaskOutcome 建立后追加，必须通过 Amendment 留痕。未列项通过适用性规则解析。

### 12.3 治理角色与实例策略

本节不重定义 `Evidence` 和 `Decision`：`Evidence` 的唯一语义直接适用第 3 章，`Decision` 的唯一语义直接适用 C10。以下仅定义六类元模型中的治理角色和实例策略。

| 术语 | 唯一语义 |
|---|---|
| Authority Record | AuthorityAsset 中某类事实、定义、策略、范围或要求的唯一权威记录 |
| Derived View | 从权威记录和 Evidence 按固定查询规则生成的可重建矩阵、报告或查询结果 |
| Applicable | Task Profile 触发控制目标时必须建立或更新 |
| Conditional | 只有指定 Change Surface、Risk、Extension 或生命周期条件成立时建立 |
| Inherited | 当前任务不复制内容，只引用不可变 Baseline |
| On Event | 事件、执行、失败、评审或决定实际发生后建立 |
| On Demand | Gate、审计、查询或报告需要时从权威来源生成 |

### 12.4 物理载体

`Physical Carrier` 是文件、页面、数据库、工单或流水线视图，不是元类型或领域 Profile。AuthorityAsset 可保留原生格式并共享载体，但必须能独立解析 Asset ID、Meta Type、Legacy Kind/Profile、Owner、State、Revision、Scope、Trace 和 History。TaskContract、RunLedger、TaskOutcome 对每个 TaskID 固定使用三份载体。

### 12.5 人类最小输入

人类输入只包含无法从当前环境可靠发现且会改变交付结果的内容：期望结果与验收示例、目标产品/仓库/环境、不可突破约束与明确排除项、验收决策角色；涉及发布时增加发布决策角色。其他分类、影响、依赖、建议产物和验证方法由 Agent 生成后供人确认。
