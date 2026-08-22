# E01 架构治理扩展规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | E01 |
| 英文名称 | Architecture Governance Extension Specification |
| 正式文件名 | `E01_Architecture_Governance_Extension_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 编制适用性 | 必须编制 |
| 当前激活状态 | 未激活 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 核心规范依赖 | C01 至 C12 V6.3 |
| 生产前调研 | RVR-E01-0001 |
| 后续规范 | E02 至 E05 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule 保留；Architecture Baseline、ADR、Conformance Review、批准、偏差、迁移和替代历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式架构约束。E01 当前未激活，不对本规范文档仓库强加目标产品架构控制；未激活不影响本文件必须编制、评审和建立基线。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定复杂产品、软件、系统和服务的架构描述、Stakeholder 与 Concern、Viewpoint、Model、Fitness Criteria、Architecture Decision、演进路线和符合性评审。

本规范实现以下目标：

1. 区分 Architecture 与表达 Architecture 的 Architecture Description；
2. 使每个 Architecture View 都有明确 Stakeholder、Concern、Viewpoint、Model Kind 和适用版本；
3. 使 Architecture Principle、Constraint 和 Fitness Criteria 可检查、可测量或可评审；
4. 使 Architecture Decision 记录候选方案、取舍、理由、质量影响、Risk 和替代关系；
5. 使架构从当前状态到目标状态的兼容、迁移、回滚和退出可执行；
6. 使 Architecture Baseline 与被评审实现之间的偏差可定位、可处置、可复核；
7. 使架构治理接入 Requirement、Design、Trace、Configuration、Gate 和 Release；
8. 防止用单张“架构图”、工具模型、代码结构或口头共识代替受控架构描述；
9. 防止 Agent 自批架构、隐藏不确定项或将建议写成已批准 Decision；
10. 在 E01 未激活、已激活、待判定、条件激活和退役期间保持治理状态可追溯。

## 3. 适用范围

E01 在任一触发条件成立时必须激活：

- 多服务并行；
- 多仓库并行；
- 多团队并行；
- 存在关键性能要求；
- 存在关键可靠性要求；
- 存在关键扩展性要求；
- 存在复杂外部集成；
- 存在长期架构迁移；
- 架构决策频繁影响多个 PRD。

激活后的 E01 适用于：

- 软件、系统、服务、平台、企业能力、产品线和系统族的 Architecture Description；
- 当前、候选、目标、过渡、参考和退役架构；
- 业务、应用、数据、集成、部署、运行、Security、Privacy、AI、可靠性和迁移等适用 View；
- Architecture Principle、Constraint、Decision、Fitness Criteria 和 Correspondence；
- 多服务、多仓库、多团队及复杂外部依赖的边界和责任分配；
- 从 Concept、Development、Transition、Operation、Maintenance 到 Retirement 的架构演进；
- P2 档位下 ARC、SCR、VPC、AMS、AFC、ADR、AER、ACV 八类正式产物；
- 人类、规则工具、建模工具、代码分析工具、CI/CD 和 Agent 参与的架构活动；
- E04 已激活时的记录、元数据、访问、保留、审计和历史恢复控制。

### 3.1 当前仓库状态

当前仓库只生产规范文档，不存在目标产品运行系统、多服务、多仓库运行架构、关键容量目标或长期架构迁移，因此：

1. `编制适用性 = 必须编制`；
2. `当前激活状态 = 未激活`；
3. E01 文件、模板骨架和检查规则必须完成；
4. 当前仓库不需要创建目标产品 ARC 至 ACV 实例；
5. 后续目标产品在 Discovery Ready 前必须重新执行全部触发条件判定；
6. 任一触发条件为未知时，禁止判为未激活。

### 3.2 横向生效边界

E01 激活后：

1. C01 至 C04 继续管理 Need、Problem、Scope、PRD 和 Requirement；
2. C05 继续管理 Acceptance、Verification、Validation 和 Evidence；
3. C06 继续管理 UX 与 Technical Design；
4. E01 管理跨 PRD、跨组件、跨服务、跨仓库、跨团队和长期演进的 Architecture；
5. C07 至 C09 继续管理 Authority、Context 和 Agent Execution；
6. C10 继续管理正式 Decision、Trace 和 Lineage；
7. C11 继续管理 Configuration Item、Revision、Snapshot、Baseline 和 Change；
8. C12 继续管理 Review、Gate、Waiver、Risk Acceptance 和 Product Health。

## 4. 不适用范围

本规范不负责：

- 代替 C03 PRD Package；
- 代替 C04 Requirement Record；
- 代替 C05 Acceptance Criteria、Verification Plan 或 Evidence；
- 代替 C06 Technical Design Specification、System Context & Component View、Interface & Integration Specification、Data & State Design 或 Failure & Recovery Design；
- 代替 E02 Security、Privacy 或 Compliance 控制；
- 代替 E03 Data 与 AI Data Governance；
- 代替 E05 Service Management、SLO、Incident 或运行值守；
- 规定唯一建模语言、框架、图形符号、工具、云平台、编程语言或部署技术；
- 为所有产品设定统一数值 Threshold；
- 声明 ISO、IEC 或 IEEE 认证；
- 保存 Agent 私有思维链；
- 允许 Architecture Board 覆盖产品、Security、Privacy、Safety 或合同 Authority。

E01 可以消费上述事实，但禁止：

- 用 ARC 替代 Requirement；
- 用 AMS 图形替代 ARC、SCR、VPC 或 ADR；
- 用 ADR 修改已批准 Requirement；
- 用 AFC 代替 C05 Verification Evidence；
- 用 AER 代替 C11 Change Request；
- 用 ACV 代替 C12 Gate Decision；
- 用 Architecture Principle 绕过法律、合同、Security、Privacy 或 Safety 义务；
- 用“行业最佳实践”作为无来源的强制规则；
- 用架构评分总分隐藏 Critical Finding；
- 将未建模对象解释为不存在。

## 5. 规范性用语与受控判定

### 5.1 规范性用语

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

法律、监管、合同、Security、Privacy、Safety、不可逆数据、Non-waivable Gate 和 Authority Boundary 不得通过普通 EWR 绕过。

### 5.2 扩展适用性判定值

以下值是 E01 Activation Status，不是 DOC、DEC 或 EXEC State：

| 值 | 语义 |
|---|---|
| Not Evaluated | 尚未评价；禁止进入 Discovery Ready |
| Pending | 存在未知项或等待证据；禁止判为未激活 |
| Inactive | 全部触发条件明确为否 |
| Conditionally Active | 在明确 Scope、条件和期限内激活 |
| Active | 任一触发条件成立，E01 完整适用 |
| Retiring | 正在退出但仍需维持迁移、审计和历史控制 |
| Retired | 当前 Scope 不再适用；历史资产继续保留 |

### 5.3 触发条件判定值

| 值 | 语义 |
|---|---|
| Yes | 条件已由 Evidence 证实 |
| No | 条件已由 Evidence 证实不成立 |
| Unknown | 缺少充分 Evidence |
| Not Applicable | 条件定义对 Scope 不适用，必须记录理由和批准人 |

`Unknown` 必须映射为 E01 `Pending`，禁止映射为 `Inactive`。

### 5.4 架构符合性判定值

| 字段 | 受控值 |
|---|---|
| Criterion Result | Pass、Fail、Blocked、Not Applicable、Not Evaluated |
| Deviation Type | Intended、Unintended、Unknown |
| Conformance Conclusion | Conformant、Conformant with Findings、Nonconformant、Inconclusive |
| Architecture Significance | Local、Cross-component、Cross-service、Cross-product、Enterprise |
| Model Confidence | Confirmed、Partially Confirmed、Assumed、Unknown |
| Roadmap Stage Status | Planned、Ready、In Progress、Blocked、Completed、Cancelled |

上述字段不得替代正式产物 State。

## 6. 术语与定义

| 术语 | 定义 | 禁止混同 |
|---|---|---|
| Entity of Interest | 被描述其 Architecture 的目标实体 | ARC 文件 |
| Architecture | Entity 在其 Environment 中体现的基本概念或属性，以及元素、关系和演进原则 | Architecture Description |
| Architecture Description | 表达某 Entity Architecture 的受控工作产品集合 | Architecture 本身 |
| Stakeholder | 对 Entity 或 Architecture 持有 Interest、责任、影响或受影响关系的主体 | 普通联系人列表 |
| Architecture Concern | 对 Stakeholder 重要且需要 Architecture 回答的问题、利益或风险 | 专业化自 C06 Concern；不得混同 Requirement、Risk 本身 |
| Architecture Viewpoint | 为处理特定 Architecture Concern 而规定 Architecture View 构造约定的工作产品 | 专业化自 C06 Viewpoint；不得混同 Architecture View |
| Architecture View | 按某 Architecture Viewpoint 表达 Architecture 的工作产品 | 专业化自 C06 View；不得混同 Architecture Viewpoint |
| Model Kind | 规定某类 Architecture Model 的约定 | 某个 Model 实例 |
| Architecture Model | 使用一个 Model Kind 表达 Entity 的部分 Architecture | 整个 Architecture |
| Correspondence | Architecture Description 内元素之间受控的一致性或关系声明 | 无语义 related-to |
| Correspondence Rule | 对 Correspondence 必须满足的约束 | 自动修复脚本 |
| Architecture Principle | 约束架构形成和演进的长期规则 | 口号 |
| Architecture Decision | 对 Architecture Significant 问题的受控选择 | Agent 推理全文 |
| Architecture Rationale | 支持 Architecture Decision 的事实、权衡和理由 | 专业化自 C10 Rationale；不得记录不可审计意见 |
| Architecture Baseline | 经 C11 批准并固定的 ARC、SCR、VPC、AMS、AFC、ADR 和适用 AER 版本集合 | Git 分支当前状态 |
| Fitness Criterion | 对架构特性、场景、指标、阈值、环境、方法和失败处置的可执行判定 | 产品总分 |
| Architecture Drift | 实现、配置或运行事实偏离 Architecture Baseline 的状态 | 所有 Change |
| Architecture Debt | 已知架构缺口产生的受控长期负担 | 未记录缺陷 |
| Architecture Conformance Review | 按固定 Baseline、Criteria 和 Evidence 评价实现符合性的执行实例 | Gate Decision |
| Evolution Roadmap | 从当前 Architecture 到目标 Architecture 的阶段、兼容、迁移、回滚和退出计划 | 普通里程碑列表 |

### 6.1 Architecture 与 Architecture Description 边界

1. ARC、AMS 和图形只描述 Entity；
2. 任何图形都必须标识 Viewpoint、Scope、Revision 和来源；
3. 图形缺少元素不证明 Entity 中不存在该元素；
4. 工具模型是 Architecture Description 的载体，不自动成为事实源；
5. 运行发现与描述不一致时，必须记录 Drift，不得静默改图；
6. ARC 的 Approved 或 Baselined 表示描述获批，不表示实现自动符合。

### 6.2 Viewpoint 与 View 边界

1. VPC 管理可复用 Viewpoint 定义；
2. AMS 管理按 Viewpoint 生成的 Model 和 View；
3. 每个 View 必须引用且只声明其实际遵循的 Viewpoint；
4. 同一 Viewpoint 可以产生多个适用 Scope 或版本的 View；
5. 同一 View 可以组合多个 Model，但必须保留 Model Kind 和 Correspondence；
6. Viewpoint 变化必须分析现有 View 是否失效。

## 7. 角色、职责与职责分离

### 7.1 角色

| 角色 | 必须职责 | 禁止事项 |
|---|---|---|
| Architecture Sponsor | 确认 Architecture Objective、Scope、资源和升级路径 | 代替领域 Owner 证明技术事实 |
| Architecture Owner | 对 ARC 完整性、Architecture Baseline 和演进负责 | 自批自身高风险例外 |
| Architect | 维护 SCR、VPC、AMS、AFC、ADR 候选和 AER | 修改 Requirement 或 Risk 原事实 |
| Product Owner | 确认业务目标、PRD 和价值取舍 | 单方批准 Security/Privacy/Safety 偏离 |
| Technical Owner | 确认实现边界、可行性、运行约束和迁移 | 将代码现状直接宣布为 Baseline |
| Quality Owner | 维护 AFC 评价方法、Evidence 要求和 ACV 独立性 | 代替 Risk Owner 接受风险 |
| Security/Privacy/Data/Operations Owner | 提供对应领域 Concern、Constraint、Criteria 和 Decision 输入 | 被 Architecture Board 无权覆盖 |
| Architecture Reviewer | 按固定 Criteria 独立评审 | 评审自己唯一编制的 Critical Decision |
| Configuration Manager | 管理 Architecture Configuration Item、Snapshot 和 Baseline | 改写架构内容 |
| Gate Authority | 基于 ACV、Risk 和 Evidence 作 Gate Decision | 用 Gate 代替 Architecture Baseline |
| Coding Agent | 分析、建模、检查、生成候选内容和报告 | 批准 ARC、ADR、AER、ACV、Waiver 或 Baseline |

### 7.2 最低职责分离

以下活动不得由同一 Agent 或同一无复核主体独立完成：

1. 提出 Critical ADR 与最终批准该 ADR；
2. 实现 Architecture Change 与接受 ACV；
3. 发现 Drift 与删除 Drift 记录；
4. 制定 Non-waivable Criterion 与批准其豁免；
5. 编制 AER 与接受不可逆退出 Risk；
6. 计算关键 Fitness Result 与修改原始测量 Evidence；
7. 建立 Architecture Baseline 与无记录覆盖其成员版本。

### 7.3 Agent 使用规则

Agent 可以：

- 从受控资产提取 Stakeholder 和 Concern 候选；
- 生成 Viewpoint、Model、ADR 和 Roadmap 草案；
- 计算可复现 Fitness Result；
- 执行一致性、追踪和 Drift 检查；
- 汇总 ACV Evidence 和 Finding；
- 标记冲突、未知项和缺失关系。

Agent 禁止：

- 生成虚构 Stakeholder、Requirement、Evidence 或测量结果；
- 把概率推断写成事实；
- 自动批准 Architecture Decision；
- 自动接受剩余 Risk；
- 自动 Waive 失败 Criterion；
- 删除失败、Unknown、Not Evaluated 或 Superseded 历史；
- 以私有思维链作为 Rationale；
- 在未授权 Scope 修改模型、代码或配置。

## 8. 受控产物与关系

### 8.1 正式产物

| 代码 | 正式名称 | 状态模型 | 事实源职责 |
|---|---|---|---|
| ARC | Architecture Description | DOC | Entity、Scope、Stakeholder、Concern、View、Model、Principle、Boundary、Decision 和限制 |
| SCR | Stakeholder and Concern Register | DOC | Stakeholder、Concern、重要度、Owner、处置和上下游关系 |
| VPC | Viewpoint Catalog | DOC | Viewpoint 目的、Stakeholder、Concern、Model Kind、约定和检查规则 |
| AMS | Architecture Model Set | DOC | Model、View、元素、关系、假设、版本和一致性 |
| AFC | Architecture Fitness Criteria | DOC | 场景、指标、阈值、环境、方法、频率和失败处置 |
| ADR | Architecture Decision Record | DEC | Architecture Significant Decision、候选方案、选择、理由、影响和替代 |
| AER | Architecture Evolution Roadmap | DOC | 当前、目标、过渡、依赖、兼容、迁移、回滚和退出 |
| ACV | Architecture Conformance Review | EXEC | Baseline、实现、Criteria、Evidence、Deviation、Risk、结论和复核 |

P2 禁止合并、删除或用其他名称替代上述八类资产。工具可以统一承载，但必须保留独立 Asset ID、State、Owner、Revision、权限和导出能力。

### 8.2 单一事实源

| 事实 | 唯一事实源 | E01 只允许 |
|---|---|---|
| Need、Problem、Goal | C01 | 引用 |
| Scope、Risk、Constraint、Dependency | C02 | 引用并解释架构影响 |
| PRD、Feature、Quality Attribute | C03 | 引用并建立 Concern |
| Requirement | C04 | 引用，不改写 |
| Acceptance、Verification、Evidence | C05 | 引用和消费 |
| Technical Design | C06 | 建立一致性和实现映射 |
| Authority | C07 | 引用 Approval Matrix |
| Agent Context | C08 | 引用适用 Architecture Baseline |
| Agent Run 和实际 Change | C09 | 引用执行记录 |
| Decision、Trace、Lineage | C10 | 建立和查询正式关系 |
| Revision、Snapshot、Baseline、Change | C11 | 引用配置事实 |
| Gate、Waiver、Risk Acceptance | C12 | 引用，不替代 |
| Architecture Description | E01 ARC | 管理 |
| Architecture View/Model | E01 AMS | 管理 |
| Architecture Fitness Definition | E01 AFC | 管理 |

### 8.3 最低关系链

```text
Need → Problem → Goal → PRD → Requirement
Requirement → Concern → Viewpoint → View/Model
Concern → ADR → Architecture Element
Architecture Element → Technical Design → Implementation
AFC → Verification Evidence → ACV → Gate Decision
ADR → AER Stage → Change Request → Architecture Baseline
Architecture Baseline → Release Configuration → Observed Runtime
Observed Runtime → Drift/Finding → Change or Waiver → Re-review
```

所有关系必须使用公共术语基线的受控关系类型。禁止创建无方向、无语义的 related-to 关系。

### 8.4 ARC 聚合关系

必须按公共受控关系的方向建立：

- ARC `contains` SCR、VPC、AMS、AFC 和适用 AER；
- ARC `addresses` Need、Problem、Risk 和 Concern；
- Requirement `designed-by` ARC 中受控 Architecture Element；
- Constraint、Policy、Contract 或外部义务 `constrains` ARC；
- ADR `addresses` Architecture Concern，并 `constrains` 适用 Architecture Element；
- Criterion `verified-by` ACV 引用的适用 Evidence；
- C11 BSL `contains` ARC、SCR、VPC、AMS、AFC、ADR 和适用 AER 的固定 Revision；
- 后继 ARC Revision `supersedes` 旧 ARC Revision。

## 9. 架构治理生命周期

### 9.1 生命周期

```text
适用性评价
  → Architecture Scope 与 Objective
  → Stakeholder/Concern 识别
  → Viewpoint 选择或定义
  → 候选 Architecture 概念化
  → 候选评价与 Decision
  → View/Model 细化
  → Fitness Criteria 与 Roadmap
  → Architecture Review
  → Architecture Baseline
  → 实现与持续检查
  → Architecture Conformance Review
  → Gate/Release
  → 运行反馈、演进、替代或退役
```

### 9.2 启动输入

启动 Architecture Governance 前必须具备：

- Extension Applicability Decision；
- Entity of Interest 和 Scope；
- Product Definition、Initiative、PRD 或授权的 Problem；
- 适用 Requirement、Risk、Constraint 和 Dependency；
- Architecture Sponsor 和 Architecture Owner；
- 初始 Stakeholder；
- 适用 Security、Privacy、Data、AI、Operations Concern；
- 计划生命周期阶段和目标版本；
- 访问、保留和工具约束。

### 9.3 迭代规则

1. Architecture Process 可以并发、迭代和递归执行；
2. 每轮必须固定 Input Revision、Output Revision 和未解决 Concern；
3. 上游 Requirement 实质变化必须触发 Impact Analysis；
4. Viewpoint 或 Model Kind 变化必须检查既有 View 和 Correspondence；
5. ADR 被 Superseded 时必须检查 ARC、AMS、AFC、AER、Design、Code、Test 和 Release；
6. ACV 只对固定 Architecture Baseline 和实现版本有效；
7. 运行事实可以触发新 Decision，但不得反向改写旧 Decision。

### 9.4 完成条件

Architecture Governance 不以“所有图已画完”为完成。进入 Baseline 前必须：

- 适用 Stakeholder 和 Concern 完整；
- 所有 Critical Concern 有 Viewpoint、Decision 或受控未解决处置；
- ARC、VPC、AMS、AFC、ADR 和适用 AER 一致；
- Architecture Principle 可评审或可检查；
- 关键 Quality Attribute 有 Fitness Criteria；
- 已知 Risk、Assumption、Constraint 和 Limitation 公开；
- 兼容、迁移、回滚和退出具备可执行路径；
- Architecture Review 完成；
- C11 Baseline Decision 和 C12 Gate Decision 的输入就绪。

## 10. 适用性、激活与治理过程

### 10.1 扩展适用性记录

“Extension Applicability Record”不是 E01 第九类正式产物。必须使用 C10 `Decision Record` 承载，并满足：

| 字段 | 最低要求 |
|---|---|
| Decision Type | Extension Applicability |
| Scope | Product、Initiative、PRD、Module、Environment、Version |
| Trigger Set | E01 五组蓝图触发条件及细分项 |
| Per-trigger Result | Yes、No、Unknown、Not Applicable |
| Evidence | 每项判定的 Source |
| Decision | Inactive、Conditionally Active、Active、Retiring、Retired |
| Conditions | 条件激活的 Scope、期限、补充 Evidence |
| Owner | 人类 Architecture Owner |
| Approver | C07 授权角色 |
| Review Time | 最迟复评时间和事件触发器 |

### 10.2 强制激活规则

满足任一项时 `Activation Status` 必须为 `Active` 或有界的 `Conditionally Active`：

1. 存在两个及以上独立部署服务且架构边界影响 Release；
2. 存在两个及以上受控代码仓库且 Change 需要跨仓库协调；
3. 存在两个及以上团队并行且架构责任或接口跨团队；
4. 性能、可靠性或扩展性失败会导致关键 Goal、SLO、合同或安全影响；
5. 外部集成包含多个协议、信任边界、不可控依赖或长期兼容义务；
6. 迁移跨越多个 Release、数据格式、协议、平台或不可逆阶段；
7. Architecture Decision 在一个评价周期内影响多个 PRD；
8. 架构 Drift 已造成重复 Defect、Incident、回退或无法解释的实现差异。

### 10.3 Pending 规则

出现以下任一情况必须 `Pending`：

- 服务、仓库或团队边界未知；
- 容量、可靠性或扩展目标未定义；
- 外部集成清单不完整；
- 迁移范围或持续时间未知；
- 多 PRD 影响尚未完成查询；
- Evidence 过期、冲突或不可访问；
- Authority 或 Scope 不明确。

Pending 必须阻断 Discovery Ready，除非 C12 形成合法且可豁免的 EWR；Non-waivable 条件不得豁免。

### 10.4 Architecture Governance Process

架构治理必须：

1. 建立 Architecture Objective、Policy、Principle 和决策权限；
2. 定义 Architecture Collection 和 Entity 关系；
3. 维护组织、产品和项目目标对齐；
4. 监测 Architecture Baseline 与治理指令符合性；
5. 记录治理 Decision、Finding、Escalation 和 Action；
6. 评价治理有效性和重复偏差；
7. 规定跨团队、跨仓库和跨服务的仲裁路径；
8. 防止 Architecture Board 越权修改领域事实。

### 10.5 Architecture Management Process

架构管理必须：

1. 将治理指令转化为 Scope、Plan、Owner、Milestone 和 Evidence；
2. 维护 ARC 至 ACV 的工作队列和状态；
3. 监测进度、Dependency、Risk、资源和质量；
4. 协调 Architecture Collection 内的冲突；
5. 维护 Architecture Review、Baseline 和 Change 日程；
6. 评价架构活动有效性；
7. 完成后移交、归档和回顾。

### 10.6 Architecture Conceptualization Process

概念化必须：

1. 描述 Problem Space、Environment、Boundary 和 External Entity；
2. 识别 Stakeholder、Concern、Objective、Constraint 和 Assumption；
3. 识别现有、参考和相关 Architecture；
4. 形成两个及以上可行候选方案，除非唯一性有 Evidence；
5. 明确候选方案元素、关系、关键 Mechanism 和 Trade-off；
6. 评价候选方案对 Requirement、Quality Attribute、Risk 和 Migration 的影响；
7. 形成首选 Architecture 候选和待决问题；
8. 禁止在候选分析前将现有实现默认设为首选。

### 10.7 Architecture Evaluation Process

架构评价必须：

1. 固定评价对象、版本、Scope 和目的；
2. 固定 Stakeholder、Concern、Scenario、Measure 和 Decision Criteria；
3. 公开评价方法、输入、假设和局限；
4. 区分事实、推断、评价和 Decision；
5. 记录候选方案价值、成本、Risk、质量影响和未知项；
6. 保留否决方案及其理由；
7. 不得将未评价项计为通过；
8. 输出 ADR 候选、Finding、Action 或重新概念化要求。

### 10.8 Architecture Elaboration Process

架构细化必须：

1. 选择或定义适用 Viewpoint；
2. 建立 Architecture Model 和 View；
3. 记录 Model Kind、Notation、Tool、Version 和 Convention；
4. 建立元素、关系、Interface、Boundary 和 Correspondence；
5. 检查 View 间完整性与一致性；
6. 关联 Requirement、Decision、Risk、Design 和 Verification；
7. 记录已知 Limitation、Assumption 和 Open Concern；
8. 使目标使用者可以解释和消费 Architecture Description。

### 10.9 Architecture Enablement Process

架构使能必须管理：

- 方法、模板和建模约定；
- 工具、格式和交换能力；
- 角色能力和培训；
- Reference Architecture 和复用资产；
- Repository、访问、版本和保留；
- 自动检查和 CI 反馈；
- 指标、回顾和过程改进；
- 标准版本复评和影响分析。

## 11. Architecture Description 控制

### 11.1 Entity、Scope 与 Environment

ARC 必须唯一标识：

- Entity of Interest；
- Entity 类型和 Owner；
- System Boundary；
- External Entity；
- Environment 和运行假设；
- 适用 Product、PRD、Version、Release 和 Lifecycle Stage；
- In Scope、Out of Scope 和 Future Scope；
- 与其他 Architecture 的包含、依赖、继承或 Correspondence；
- 描述目的和 Intended User。

### 11.2 Stakeholder 与 Concern

1. 每个 Stakeholder 必须有角色、责任、影响和联系路径；
2. 每个 Concern 必须有来源、重要度、Owner 和处置状态；
3. Concern 必须关联至少一个 Stakeholder；
4. Critical Concern 必须关联 Viewpoint、ADR、AFC 或 Risk；
5. Requirement、Risk 和 Concern 必须保持独立 Asset ID；
6. 未处置 Concern 必须进入 Gate 输入；
7. Stakeholder 缺席不得删除其 Concern；
8. 同名 Concern 必须判断是复用、细化还是独立对象。

### 11.3 Viewpoint

每个 VPC 成员必须规定：

- Viewpoint ID 和名称；
- 目的和适用范围；
- 目标 Stakeholder；
- 被处理 Concern；
- Model Kind；
- 元素、关系和 Notation；
- 建模步骤；
- Correspondence Rule；
- 完整性、一致性和质量检查；
- 适用 Tool/Version 或 Tool-neutral 约定；
- Known Limitation；
- 维护 Owner。

### 11.4 Architecture View 与 Model

每个 View/Model 必须：

- 有永久 Model ID；
- 引用一个 Viewpoint；
- 标识 Entity、Scope、Revision 和时间；
- 声明 Model Kind 和 Notation；
- 标识每个受控元素和关系；
- 记录来源、Assumption 和 Confidence；
- 关联适用 Requirement、ADR、Risk 和 Design；
- 通过适用 Correspondence Rule；
- 对无法表示的信息声明 Limitation；
- 禁止通过颜色、位置或图标承载未定义语义。

### 11.5 Correspondence

1. Cross-view 同一元素必须使用相同 Asset ID 或明确映射；
2. 名称相同但身份不同的元素必须显式区分；
3. Interface 两端、Direction、Protocol、Data、Failure 和 Owner 必须一致；
4. Deployment View 与 Logical View 的映射必须可查询；
5. Data View 与 Interface View 的 Schema/Contract 必须一致；
6. Security/Privacy Concern 必须映射至适用 Trust Boundary 和 Control；
7. Correspondence Rule 失败必须形成 Finding，不得静默修复；
8. 自动修复必须作为 C09 Agent Run 或工具执行记录保留。

### 11.6 Architecture Principle

每个 Principle 必须包含：

- Principle ID；
- 规范性陈述；
- Business/Engineering Rationale；
- 适用 Scope；
- 具体 Implication；
- 可检查条件或 Review Question；
- Owner 和 Approver；
- Exception 规则；
- 生效和复评时间；
- 关联 ADR、AFC、Risk 和 Requirement。

“松耦合”“高可用”“云原生”“简单”“可扩展”单独出现时不构成可接受 Principle。

### 11.7 Architecture Decision

ADR 必须记录：

1. 单一 Architecture Concern；
2. Context 和 Problem Statement；
3. Decision Driver；
4. 两个及以上候选，或唯一候选的 Evidence；
5. 每个候选的优点、缺点、Risk、Cost 和 Reversibility；
6. Chosen Option；
7. Rationale；
8. 对九类适用 Product Quality 的影响；
9. 对 Security、Privacy、Data、AI、Operations 的影响；
10. Migration 和 Compatibility 影响；
11. 适用 Scope、Version 和 Effective Time；
12. Decision Maker、Consulted、Informed；
13. Confirmation Method；
14. Supersedes/Superseded-by 关系；
15. Revisit Trigger。

ADR 禁止：

- 保存私有思维链；
- 用“团队一致同意”替代参与者和批准；
- 删除 rejected option；
- 原位反转已批准 Decision；
- 用 `Accepted` 作为未登记的 DEC State；
- 以 ADR 修改 Requirement 或授权。

### 11.8 Architecture Fitness Criteria

每个 Criterion 必须包含：

- Architecture Characteristic；
- Scenario；
- Applicable Scope；
- Measure；
- Unit；
- Threshold；
- Environment；
- Workload/Data Set；
- Measurement Method；
- Tool 和 Version；
- Frequency；
- Owner；
- Evidence Type；
- Failure Handling；
- Waivability；
- Review/Expiry Time。

Criterion 必须满足：

1. Threshold 有业务、Requirement、Risk、历史或实验依据；
2. 环境和负载可复现；
3. 数据缺失映射为 Not Evaluated；
4. 工具失败映射为 Blocked 或 Not Evaluated；
5. 单次 Pass 不替代趋势评价；
6. Threshold 变化必须经 Change；
7. 失败不得被平均分抵消；
8. Critical Criterion 失败必须进入 C12 Gate。

### 11.9 Architecture Evolution

AER 必须区分：

- Current State；
- Target State；
- Transition State；
- Invariant；
- Compatibility Window；
- Migration Wave；
- Data/Protocol/Schema Conversion；
- Dual-run 或 Coexistence；
- Cutover；
- Rollback；
- Exit；
- Decommission；
- Residual Risk；
- Success Criterion。

禁止只有 Target Diagram 而没有阶段、兼容、迁移、回滚和退出。

### 11.10 Architecture Conformance

ACV 必须：

1. 固定 Architecture Baseline ID；
2. 固定 Implementation/Configuration/Release Revision；
3. 固定 Criteria 和 Review Method；
4. 记录 Evidence 和其有效性；
5. 按 Criterion 记录 Result；
6. 标识 Intended、Unintended 或 Unknown Deviation；
7. 关联 Risk、Defect、Change 或 EWR；
8. 形成 Conformance Conclusion；
9. 记录整改、Owner、期限和复核；
10. 将结论交给 C12 Gate Authority。

ACV `Completed` 只表示评审执行结束；ACV `Accepted` 只表示评审执行结果被接受；两者都不表示 Gate 已 Pass。

## 12. 状态模型与转换

### 12.1 状态模型

| 产物 | 模型 | 允许状态 |
|---|---|---|
| ARC、SCR、VPC、AMS、AFC、AER | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| ADR | DEC | Proposed、Under Review、Approved、Conditionally Approved、Rejected、Waived、Superseded、Expired |
| ACV | EXEC | Planned、Ready、Running、Blocked、Completed、Failed、Accepted、Rejected、Cancelled |

### 12.2 状态边界

1. `Architecture Active/Inactive` 不是 DOC State；
2. `Conformant/Nonconformant` 不是 ACV State；
3. `Accepted` 不是 ADR State；
4. `Implemented` 不是 ADR State；
5. ARC Approved 不等于 ARC Baselined；
6. ADR Approved 不等于 Implementation 已完成；
7. AER Completed 是 Stage Member Status，不是 AER DOC State；
8. Superseded 资产继续保留并禁止作为默认输入。

### 12.3 转换规则

```text
DOC:  Draft → In Review → Approved → Baselined → Superseded/Retired
                    ↘ Changes Required → Draft
                    ↘ Rejected

DEC:  Proposed → Under Review → Approved/Conditionally Approved/Rejected/Waived
                              Approved/Conditionally Approved/Waived → Superseded/Expired

EXEC: Planned → Ready → Running → Completed → Accepted/Rejected
                    Running ↔ Blocked
                    Running → Failed/Cancelled
```

每次转换必须记录原状态、新状态、时间、执行者、依据、适用 Revision 和 Authority。

### 12.4 Baseline 规则

1. ARC、SCR、VPC、AMS、AFC 和适用 AER 必须形成一致 Baseline；
2. ADR 可作为 Baseline 成员，但保持 DEC State；
3. Baselined DOC 禁止退回 Draft；
4. 修改 Baseline 必须执行 C11 CHG、IMA、CHD 和新 Revision；
5. Architecture Baseline 必须引用完整性校验和 Git Commit/Snapshot；
6. Baseline 不得包含 Rejected、Expired 或未知 Revision 资产；
7. Baseline 替代必须保留 Supersedes 关系；
8. Agent 禁止批准 Baseline。

## 13. 正式产物最低内容

### 13.1 通用必填信息

八类产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 E01 类型专属要求。

### 13.2 ARC Architecture Description

ARC 类型专属必填：

- System/Entity Identifier；
- Stakeholder；
- Concern；
- Architecture Viewpoint；
- View/Model Index；
- Architecture Principle；
- Boundary；
- Key Decision；
- Applicable Version；
- Known Limitation；
- Environment；
- Architecture Objective；
- Baseline Reference；
- Open Concern；
- Conformance Status。

### 13.3 SCR Stakeholder and Concern Register

SCR 类型专属必填：

- Stakeholder；
- Role；
- Concern；
- Importance；
- Related Viewpoint；
- Owner；
- Disposition Status；
- Requirement Link；
- Risk Link；
- Evidence；
- Consultation Method；
- Last Review；
- Unresolved Impact。

SCR Member Status 必须使用 CASE 成员状态：Open、In Progress、Blocked、Resolved、Closed、Reopened、Cancelled；SCR 本体仍使用 DOC State。

### 13.4 VPC Viewpoint Catalog

VPC 类型专属必填：

- Viewpoint ID；
- Name；
- Target Stakeholder；
- Concern；
- Model Kind；
- Modelling Convention；
- Check Rule；
- Applicable Scope；
- Correspondence Rule；
- Notation；
- Tool Compatibility；
- Limitation；
- Owner。

### 13.5 AMS Architecture Model Set

AMS 类型专属必填：

- Model ID；
- Viewpoint；
- Entity Scope；
- Element；
- Relationship；
- Assumption；
- Version；
- Source；
- Completeness Check；
- Consistency Check；
- Model Kind；
- Confidence；
- Tool/Format；
- Correspondence；
- Related Decision。

### 13.6 AFC Architecture Fitness Criteria

AFC 类型专属必填：

- Architecture Characteristic；
- Scenario；
- Metric；
- Threshold；
- Environment；
- Measurement Method；
- Frequency；
- Owner；
- Failure Handling；
- Unit；
- Workload/Data Set；
- Evidence Requirement；
- Waivability；
- Review Time。

### 13.7 ADR Architecture Decision Record

ADR 类型专属必填：

- Architecture Concern；
- Context；
- Candidate Option；
- Choice；
- Rationale；
- Quality Attribute Impact；
- Risk；
- Migration Impact；
- Approver；
- Supersession Relationship；
- Decision Driver；
- Consequence；
- Scope/Version；
- Confirmation Method；
- Revisit Trigger。

### 13.8 AER Architecture Evolution Roadmap

AER 类型专属必填：

- Current State；
- Target State；
- Stage；
- Dependency；
- Compatibility Strategy；
- Migration Step；
- Exit Strategy；
- Rollback Strategy；
- Milestone；
- Risk；
- Owner；
- Transition State；
- Entry/Exit Criteria；
- Data/Protocol Handling；
- Decommission Evidence。

### 13.9 ACV Architecture Conformance Review

ACV 类型专属必填：

- Architecture Baseline；
- Reviewed Implementation；
- Criteria；
- Evidence；
- Deviation；
- Risk；
- Conclusion；
- Waiver；
- Remediation；
- Re-review；
- Reviewer；
- Review Method；
- Per-criterion Result；
- Evidence Validity；
- Gate Link。

## 14. 质量要求

### 14.1 ARC

ARC 合格必须：

- 明确区分 Entity 与 Description；
- 能定位全部成员资产；
- Stakeholder、Concern、Viewpoint、View 和 Decision 可追溯；
- Boundary、Environment 和 Applicable Version 清晰；
- Known Limitation 与 Open Concern 公开；
- 不依赖单一工具才能解释；
- 不存在未定义缩写或图例；
- 具有 Baseline 与 Change 接口。

### 14.2 SCR

SCR 合格必须：

- 覆盖直接、间接、运行、治理和受影响 Stakeholder；
- 每个 Concern 有来源和 Owner；
- Importance 有定义；
- Critical Concern 无孤立项；
- Resolved 有处置 Evidence；
- Unknown 与冲突项显式；
- 不用角色名称掩盖真实责任边界。

### 14.3 VPC/AMS

VPC/AMS 合格必须：

- Viewpoint 对应明确 Concern；
- View 严格声明 Viewpoint；
- Model Kind 和 Notation 可识别；
- Element/Relationship 有身份；
- Cross-view Correspondence 可验证；
- Assumption 和 Confidence 可见；
- 模型范围和时间有效性明确；
- 工具导出保持语义和版本。

### 14.4 AFC

AFC 合格必须：

- Criterion 可执行或有明确人工评审步骤；
- Metric、Unit、Threshold 和 Environment 无歧义；
- 阈值有来源；
- Failure Handling 可操作；
- Not Evaluated 不计 Pass；
- 工具和数据局限公开；
- 变更有 C11 记录；
- 结果可复现。

### 14.5 ADR

ADR 合格必须：

- 只处理一个主要 Decision；
- Context 和候选完整；
- Rationale 基于可引用事实；
- Consequence 同时含正向和负向影响；
- Quality、Risk、Migration 和 Reversibility 已分析；
- Approval 与参与者可追溯；
- Supersession 不覆盖历史；
- Confirmation Method 可执行。

### 14.6 AER

AER 合格必须：

- 当前、目标和过渡状态可区分；
- 阶段有 Entry/Exit Criteria；
- 依赖、兼容、迁移、回滚和退出完整；
- 不可逆步骤有 Authority 和 Evidence；
- 每阶段关联 ADR、Change、Risk 和 Baseline；
- 失败时有停止和升级路径；
- 退役有数据、流量、契约和资源处置；
- Roadmap 变更保留历史。

### 14.7 ACV

ACV 合格必须：

- Baseline 与实现 Revision 固定；
- Reviewer 独立性可证明；
- Criteria 和 Evidence 完整；
- Unknown 与 Not Evaluated 不被隐藏；
- Deviation 有类型、影响和 Owner；
- Risk 来自正式 Risk Register；
- Conclusion 与逐项结果一致；
- Gate、Waiver、整改和复核关系完整。

## 15. 验证、评审与符合性

### 15.1 验证层次

| 层次 | 对象 | 最低方法 |
|---|---|---|
| Schema | 八类产物字段和 State | 自动字段、枚举和唯一性检查 |
| Semantic | Concern、Viewpoint、View、Decision | 人工评审加受控规则 |
| Trace | 上下游与 Cross-view 关系 | 双向查询和断链检查 |
| Model | Element、Relationship、Correspondence | 模型一致性检查 |
| Fitness | AFC | 自动测量或受控人工评价 |
| Conformance | Architecture Baseline 与实现 | ACV |
| Governance | Authority、Exception、Change、History | C07/C10/C11/C12 审计 |

### 15.2 强制检查

每次 Architecture Baseline 前至少检查：

1. 八类产物适用性；
2. 通用字段完整性；
3. State 合法性；
4. Stakeholder—Concern 覆盖；
5. Concern—Viewpoint 覆盖；
6. Viewpoint—View/Model 覆盖；
7. ADR—Requirement/Risk/Element 追踪；
8. AFC—Quality Attribute/Evidence 追踪；
9. AER—ADR/Change/Baseline 追踪；
10. Cross-view Correspondence；
11. 未解决 Critical Concern；
12. Known Limitation；
13. Security/Privacy/Data/Operations 接口；
14. 权限与职责分离；
15. 工具、格式和版本；
16. 标准版本状态；
17. E01 Activation Status；
18. Baseline 完整性校验。

### 15.3 Architecture Review

Architecture Review 必须使用 C12 `Review Record`，至少记录：

- Review Type；
- ARC/Revision；
- Architecture Baseline Candidate；
- Reviewer 和角色；
- Review Criteria；
- Input；
- Finding；
- Severity；
- Conclusion；
- Remediation；
- Re-review；
- 时间；
- 人类接受状态。

### 15.4 Conformance 声明

允许的项目声明：

- “按 E01 V0.1 执行内部 Architecture Review”；
- “按列出的公开国际标准主题建立工程化映射”；
- “ACV 对指定 Architecture Baseline 和实现版本的结论为 Conformant”。

禁止的声明：

- “已通过 ISO/IEC/IEEE 42010 认证”；
- “全面符合 ISO/IEC/IEEE 42020”；
- “采用 ADR 即符合国际标准”；
- “所有架构都符合”；
- “工具检查通过即实现符合”。

需要完整国际标准符合性声明时，必须取得合法标准全文、确定 Conformance Case、逐条建立 Evidence，并由有权独立评审者批准。

## 16. 追踪、审计与记录

### 16.1 必须审计事件

以下事件必须记录：

- E01 适用性判定和复评；
- ARC、VPC、AMS、AFC、AER Revision；
- ADR 提出、评审、批准、拒绝、替代和过期；
- Architecture Baseline 建立和替代；
- Architecture Review 和 ACV；
- Correspondence Rule 失败；
- Fitness Failure；
- Architecture Drift；
- Waiver 和 Risk Acceptance；
- Roadmap Stage 进入、阻断、完成和取消；
- Migration、Rollback、Exit 和 Decommission；
- Tool/Format/Standard Version 变化；
- Agent 对 Architecture Asset 的实际修改。

### 16.2 历史规则

1. Approved、Rejected、Superseded 和 Expired ADR 禁止删除；
2. Failed Criterion 禁止被后续 Pass 覆盖；
3. ACV 原始 Evidence 禁止原位修改；
4. 图形导出必须关联 Source Model Revision；
5. Baseline 成员必须可恢复；
6. 错误记录使用更正链，不做无痕覆盖；
7. 访问受限不允许丢失 Metadata 和存在性；
8. Retired Architecture 必须保留替代、退出和未迁移对象。

### 16.3 Architecture Drift

Drift 发现后必须：

1. 固定 Architecture Baseline 和实际实现版本；
2. 描述差异；
3. 标识 Intended、Unintended 或 Unknown；
4. 分析 Requirement、Quality、Security、Data、Operations 和 Migration 影响；
5. 建立 Defect、Change Request 或 EWR；
6. 指定 Owner、期限和复核；
7. 更新 ACV 和 Gate 输入；
8. 禁止先改 Baseline 以消除 Drift。

## 17. 裁剪、激活、停用与退役

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。E01 的 Active、Conditionally Active、Retiring、Retired、Inactive、Pending、Not Evaluated 必须按统一状态语义解析；Trigger、Unknown 或冲突不得被局部规则降级。

### 17.0 Task Profile 驱动的激活

E01 在 Architecture/Multi-repo Change Surface、系统边界或关键依赖变化、跨服务/跨仓库演进、重大技术路线决定，或 C02 High/Critical 架构风险成立时激活。已有架构 Baseline 完整覆盖当前任务时 `Reference`；只生成受影响 View、Decision、Fitness 和 Conformance 实例。

未触发 E01 时不得删除类型或模板，只在 Artifact Manifest 中引用未激活规则。Emergency 架构变更必须补齐 ADR、兼容/迁移/回滚影响和 Conformance Review。

### 17.1 P2 保留边界

P2 禁止：

- 删除 ARC 至 ACV 任一类型；
- 合并为 Architecture Pack 后丢失独立身份；
- 删除 Stakeholder、Concern、Viewpoint 或 Model Kind；
- 删除 ADR 候选和 Rationale；
- 删除 AFC Environment、Threshold 或 Failure Handling；
- 删除 AER Compatibility、Migration、Rollback 或 Exit；
- 删除 ACV Deviation、Risk 或 Evidence；
- 取消 Architecture Baseline 和 Change Control；
- 允许 Agent 自批。

### 17.2 允许裁剪

在单一 Scope 内可以：

- 将 VPC 复用为组织级 Catalog；
- 用文本、表格或图形表达 AMS；
- 合并载体但保留独立对象；
- 将不适用 Viewpoint 标记 Not Applicable；
- 按 Risk 调整 Review 深度和频率；
- 对低影响 Decision 使用精简 ADR 字段视图，但后台字段不可删除；
- 使用自动化 Fitness Check 或人工 Review Criterion。

每项裁剪必须记录 Scope、理由、影响、Risk、Owner、Approver、期限和复评。

### 17.3 停用

Active E01 只有在以下条件全部满足时可以转为 Retiring：

- 全部触发条件有当前 Evidence 且为 No 或合法 Not Applicable；
- 不存在未完成 Architecture Migration；
- 不存在关键 Drift、ACV Finding 或未过期 Waiver；
- 运行和 Release 不再依赖当前 Architecture Baseline；
- 历史、访问和保留方案已确认；
- C10 DEC 已获授权批准。

Retiring 期间仍必须执行 AER、ACV、Change、Audit 和 Retention。

### 17.4 退役

转为 Retired 前必须：

- 关闭或转移全部 Open Concern；
- 完成 Migration、Exit 和 Decommission；
- 确认替代 Architecture 或无替代理由；
- 固定最终 Baseline 和 ACV；
- 归档 ARC 至 ACV；
- 更新 Trace 和 Lineage；
- 撤销不再适用 Authority、Context 和 Tool Access；
- 记录 Residual Risk 和保留期限。

## 18. 与其他规范接口

### 18.1 C01 至 C04

E01 必须：

- 从 Need、Problem、Goal 建立 Architecture Objective；
- 从 Scope、Risk、Constraint、Dependency 建立 Concern；
- 从 PRD、Feature、Quality Attribute 建立 Architecture Scope；
- 从 Requirement 建立 View、ADR、AFC 和 Conformance Criteria；
- 将架构不可行性回流上游，不得私自改变 Requirement。

### 18.2 C05 至 C06

E01 必须：

- 将 AFC 交给 C05 形成 Verification 方法和 Evidence；
- 将 ARC/AMS/ADR 约束交给 C06 Technical Design；
- 将 Design/Implementation 差异交给 ACV；
- 保持 AFC 与 Acceptance Criteria 独立；
- 保持 Architecture 与 Technical Design 独立。

### 18.3 C07 至 C09

E01 必须：

- 由 C07 定义 Architecture Approval、Tool 和 Change Authority；
- 将 Baseline、Scope、ADR 和 AFC 装入 C08 Context；
- 由 C09 记录 Agent 对 Architecture Asset 的实际动作；
- 禁止 Context 使用 Superseded ARC 或 ADR；
- 对高风险架构生成和修改要求 Human Review。

### 18.4 C10 至 C12

E01 必须：

- 用 C10 DEC 承载 Extension Applicability Decision；
- 用 C10 TLR/BTM/ALR 管理关系、覆盖和血缘；
- 用 C11 CIR/SNP/BSL/CHG/IMA/CHD 管理配置和变化；
- 用 C12 RVR 承载 Architecture Review；
- 用 C12 EWR/RAR 管理偏离和剩余 Risk；
- 用 C12 GTE 形成阶段或 Release Decision；
- 禁止 ACV 直接写 Gate Outcome。

### 18.5 E02 至 E05

E01 Active 时必须评价：

- E02 Security、Privacy、Compliance Architecture Concern；
- E03 Data、AI Data、Model、RAG 和 Evaluation Data Concern；
- E04 Knowledge、Record、Metadata、Access、Retention 和 Audit Concern；
- E05 Service、SLO、Monitoring、Incident、Capacity 和 Continuity Concern。

对应扩展未激活时，必须引用其适用性 Decision，不得默认为无 Concern。

## 19. 参考标准治理

### 19.1 参考层级

| 层级 | 来源 | 用途 |
|---|---|---|
| R1 | ISO/IEC/IEEE 42010:2022 | Architecture Description、Viewpoint、Model Kind、Correspondence、Decision |
| R1 | ISO/IEC/IEEE 42020:2019 | Architecture Governance、Management、Conceptualization、Evaluation、Elaboration、Enablement |
| R1 | ISO/IEC/IEEE 12207:2026 | 生命周期、过程应用、技术管理、技术过程和裁剪 |
| R1 | ISO/IEC 25010:2023 | 九类 Product Quality Characteristic |
| R3 | ADR/MADR 4.0.0 | 轻量 Decision 表达模板 |

R3 不得覆盖 R1、上位蓝图、公共治理或本规范。

### 19.2 版本状态

| 标准 | 2026-07-28 核验状态 | E01 控制 |
|---|---|---|
| ISO/IEC/IEEE 42010:2022 | Edition 2，Published | 使用 2022 版 |
| ISO/IEC/IEEE 42020:2019 | Edition 1，Published；2025 确认；Stage 90.92 To be revised | 当前使用；监测第二版 |
| ISO/IEC/IEEE AWI 42020 | Edition 2，2026-05-22 批准新项目，Under development | 禁止当作现行要求；发布后执行 Impact Analysis |
| ISO/IEC/IEEE 12207:2026 | Edition 2，2026-04 Published，替代 2017 版 | 使用 2026 版；禁止回退旧条款 |
| ISO/IEC 25010:2023 | Edition 2，Published | 使用九类 Product Quality |
| MADR | 4.0.0，R3 社区实践 | 只用于 ADR 表达参考 |

### 19.3 标准变化

任一参考标准发布 Amendment、Corrigendum、Replacement 或新 Edition 时必须：

1. 建立 C11 Change Request；
2. 固定旧标准状态和 Source；
3. 执行 Impact Analysis；
4. 检查术语、过程、产物、字段、模板和条款映射；
5. 更新 E01 Revision；
6. 重新评审受影响 Architecture Baseline；
7. 禁止静默替换年份或条款号。

## 20. 模板、检查清单与国际标准条例映射

### 20.1 Extension Applicability Decision 骨架

```text
Asset ID:
Artifact Type: Decision Record
Decision Type: Extension Applicability
Scope:
Current Revision:
Owner:
State:

Trigger Results:
- Multi-service:
- Multi-repository:
- Multi-team:
- Critical performance/reliability/scalability:
- Complex external integration:
- Long-term architecture migration:
- Cross-PRD architecture decisions:

Evidence:
Unknown Items:
Decision:
Conditions:
Approver:
Review Trigger:
Review Time:
Trace Links:
History Reference:
```

### 20.2 ARC 骨架

```text
Asset ID:
Artifact Type: Architecture Description
Name:
Purpose:
Entity of Interest:
Environment:
Boundary:
Applicable Scope/Version:
Architecture Objective:
Stakeholder and Concern Register:
Viewpoint Catalog:
Architecture Model Set:
Architecture Fitness Criteria:
Architecture Principles:
Key Decisions:
Evolution Roadmap:
Known Limitations:
Open Concerns:
Baseline Reference:
Conformance Status:
Trace Links:
Access Classification:
Retention Rule:
History Reference:
```

### 20.3 SCR 成员骨架

```text
Stakeholder ID:
Stakeholder/Role:
Concern ID:
Concern:
Source:
Importance:
Related Viewpoint:
Requirement:
Risk:
Owner:
Member Status:
Evidence:
Disposition:
Unresolved Impact:
Last Review:
```

### 20.4 VPC 成员骨架

```text
Viewpoint ID:
Name:
Purpose:
Applicable Scope:
Target Stakeholder:
Concern:
Model Kind:
Elements and Relationships:
Notation:
Modelling Convention:
Correspondence Rules:
Check Rules:
Tool/Format:
Known Limitations:
Owner:
```

### 20.5 AMS 成员骨架

```text
Model ID:
Name:
Entity Scope:
Viewpoint:
Model Kind:
Notation:
Elements:
Relationships:
Correspondences:
Assumptions:
Confidence:
Source:
Version:
Tool/Format:
Completeness Result:
Consistency Result:
Related Decisions:
```

### 20.6 AFC 成员骨架

```text
Criterion ID:
Architecture Characteristic:
Scenario:
Applicable Scope:
Metric:
Unit:
Threshold:
Threshold Source:
Environment:
Workload/Data Set:
Measurement Method:
Tool/Version:
Frequency:
Owner:
Evidence Requirement:
Waivability:
Failure Handling:
Review Time:
```

### 20.7 ADR 骨架

```text
Asset ID:
Artifact Type: Architecture Decision Record
State:
Title:
Architecture Concern:
Context and Problem:
Decision Drivers:
Considered Options:
Decision:
Rationale:
Positive Consequences:
Negative Consequences:
Quality Attribute Impact:
Risk:
Security/Privacy/Data/Operations Impact:
Migration and Compatibility Impact:
Reversibility:
Applicable Scope/Version:
Decision Maker:
Consulted:
Informed:
Approval:
Confirmation Method:
Revisit Trigger:
Supersedes/Superseded-by:
Trace Links:
```

### 20.8 AER 阶段骨架

```text
Roadmap ID:
Current State:
Target State:

Stage ID:
Stage Name:
Transition State:
Entry Criteria:
Actions:
Dependencies:
Compatibility Strategy:
Migration Steps:
Data/Protocol Handling:
Rollback Strategy:
Exit Strategy:
Milestone:
Success Criteria:
Risk:
Owner:
Member Status:
Evidence:
Next Baseline:
```

### 20.9 ACV 骨架

```text
Asset ID:
Artifact Type: Architecture Conformance Review
State:
Architecture Baseline:
Reviewed Implementation/Configuration/Release:
Review Scope:
Reviewer:
Criteria:
Evidence:

Per-criterion Results:
- Criterion:
  Result:
  Evidence:
  Deviation:
  Risk:

Conclusion:
Waiver:
Remediation:
Owner:
Due Time:
Re-review:
Gate Link:
```

### 20.10 生产检查清单

- [ ] E01 Activation Status 已评价；
- [ ] 任一 Unknown 均映射为 Pending；
- [ ] 八类产物适用性已记录；
- [ ] ARC 与 Entity 已区分；
- [ ] Stakeholder—Concern 覆盖完整；
- [ ] Critical Concern 有 Viewpoint、ADR、AFC 或 Risk；
- [ ] Viewpoint 与 View 未混同；
- [ ] Model Kind、Notation 和 Tool/Version 明确；
- [ ] Cross-view Correspondence 已检查；
- [ ] Architecture Principle 可检查；
- [ ] ADR 候选、理由、影响和替代关系完整；
- [ ] AFC Metric、Threshold、Environment 和 Failure Handling 完整；
- [ ] AER 兼容、迁移、回滚和退出完整；
- [ ] ACV 固定 Baseline 与实现 Revision；
- [ ] Unknown/Not Evaluated 未计为 Pass；
- [ ] Architecture Baseline 由 C11 管理；
- [ ] Gate、Waiver 和 Risk Acceptance 由 C12 管理；
- [ ] Agent 未执行批准；
- [ ] 标准版本状态已复核；
- [ ] 记录、访问、保留和历史满足 E04。

### 20.11 九类 Product Quality 适用性清单

- [ ] Functional suitability；
- [ ] Performance efficiency；
- [ ] Compatibility；
- [ ] Interaction capability；
- [ ] Reliability；
- [ ] Security；
- [ ] Maintainability；
- [ ] Flexibility；
- [ ] Safety。

每类必须选择 Applicable 或 Not Applicable。Not Applicable 必须记录 Scope、理由、Reviewer 和 Approver。

### 20.12 Architecture View 最低建议集合

以下是选择清单，不是强制固定 View：

- Context and Environment；
- Stakeholder and Concern；
- Functional/Capability；
- Component/Service；
- Interface/Integration；
- Data/Information；
- Deployment/Infrastructure；
- Runtime/Interaction；
- Security/Privacy；
- Reliability/Failure/Recovery；
- Development/Repository/Ownership；
- Migration/Evolution；
- Operations/Observability。

每个 View 的采用或不采用必须由 Concern 和 Viewpoint 驱动，禁止机械生成全部 View。

### 20.13 反例

#### 反例 A：单张图代替 Architecture Description

```text
architecture.png
```

缺少 Entity、Scope、Stakeholder、Concern、Viewpoint、Model Kind、Decision、Version 和 Limitation，不合格。

#### 反例 B：未评价即未激活

```text
Multi-service: Unknown
Activation Status: Inactive
```

必须改为 `Pending`。

#### 反例 C：ADR 原位反转

```text
ADR State: Approved
Decision: A
直接编辑为 Decision: B
```

必须创建后继 ADR，并将原 ADR 设为 Superseded。

#### 反例 D：无数据即通过

```text
Metric Value: null
Criterion Result: Pass
```

必须为 `Not Evaluated` 或 `Blocked`。

#### 反例 E：ACV 代替 Gate

```text
ACV Conclusion: Conformant
Release Authorized: true
```

必须由 C12 GTE 作 Release Gate Decision。

### 20.14 标准复评清单

- [ ] ISO/IEEE 官方产品页仍可访问；
- [ ] 标准编号、年份、Edition 和 Status 未变化；
- [ ] Amendment、Corrigendum 和 Replacement 已检查；
- [ ] ISO/IEC/IEEE 42020 第二版进展已检查；
- [ ] ISO/IEC/IEEE 12207 后继版本已检查；
- [ ] ISO/IEC 25010 质量模型变化已检查；
- [ ] MADR 版本只作为 R3 记录；
- [ ] 变化已建立 C11 CHG/IMA/CHD；
- [ ] 文末条例映射已更新；
- [ ] 历史 Mapping 已保留。

### 20.15 国际标准条例映射

以下映射依据 ISO 和 IEEE 官方产品页及 ISO OBP 公开目录。项目产物代码、状态值、触发阈值、模板和工具规则是本项目的工程化控制，不表示国际标准逐字规定。未取得标准全文授权时，不据此声明完整符合性。

| 国际标准及条款/公开主题 | 条款或公开主题 | 本规范落实位置 |
|---|---|---|
| ISO/IEC/IEEE 42010:2022 第 1 章 | Architecture Description 适用范围；区分 Architecture 与 Description | 2、3、4、6.1、11.1 |
| ISO/IEC/IEEE 42010:2022 第 4 章 | Conformance | 15.4、17、19 |
| ISO/IEC/IEEE 42010:2022 5.1–5.4 | 概念基础、生命周期、Framework 与 Language | 6、9、11.3 至 11.5、19 |
| ISO/IEC/IEEE 42010:2022 6.1 | Architecture Description Identification | 11.1、13.2、20.2 |
| ISO/IEC/IEEE 42010:2022 6.2 | Entity of Interest and Environment | 3、6.1、11.1 |
| ISO/IEC/IEEE 42010:2022 6.3–6.4 | Stakeholder 与 Concern | 6、8、11.2、13.3 |
| ISO/IEC/IEEE 42010:2022 6.5–6.6 | Architecture Viewpoint 与 View | 6.2、11.3、11.4、13.4、13.5 |
| ISO/IEC/IEEE 42010:2022 6.7–6.8 | Architecture Model 与 Model Kind | 6、11.3、11.4、13.5 |
| ISO/IEC/IEEE 42010:2022 6.9 | Architecture Correspondence | 8.3、11.5、14.3、15.2 |
| ISO/IEC/IEEE 42010:2022 6.10 | Architecture Decision and Rationale | 6、11.7、13.7、14.5 |
| ISO/IEC/IEEE 42010:2022 7.1–7.2 | Architecture Description Framework/Language | 11.3、11.4、19 |
| ISO/IEC/IEEE 42020:2019 第 1 章 | Architecture Governance、Management、Architecting 和 Enablement 范围 | 2、3、9、10 |
| ISO/IEC/IEEE 42020:2019 第 4 章 | Conformance 与 Tailoring | 5、15.4、17 |
| ISO/IEC/IEEE 42020:2019 第 5 章 | Process Overview、Interaction、Application 和 Adaptation | 8、9、10、17、18 |
| ISO/IEC/IEEE 42020:2019 第 6 章 | Architecture Governance Process | 7、10.4、16 |
| ISO/IEC/IEEE 42020:2019 第 7 章 | Architecture Management Process | 7、9、10.5、16 |
| ISO/IEC/IEEE 42020:2019 第 8 章 | Architecture Conceptualization Process | 10.6、11.1、11.2、11.7 |
| ISO/IEC/IEEE 42020:2019 第 9 章 | Architecture Evaluation Process | 10.7、11.7、14、15 |
| ISO/IEC/IEEE 42020:2019 第 10 章 | Architecture Elaboration Process | 10.8、11.3 至 11.6、13 |
| ISO/IEC/IEEE 42020:2019 第 11 章 | Architecture Enablement Process | 10.9、16、19、20 |
| ISO/IEC/IEEE 12207:2026 第 1 章 | 软件生命周期过程范围、并发/迭代/递归应用 | 3、9、18 |
| ISO/IEC/IEEE 12207:2026 4.1–4.3 | Conformance 与 Tailoring | 5、15.4、17 |
| ISO/IEC/IEEE 12207:2026 5.2–5.7 | 软件系统、组织、项目、生命周期、过程与应用概念 | 6、7、8、9 |
| ISO/IEC/IEEE 12207:2026 第 6.2 章 | 组织项目使能过程 | 7、10.9、16、19 |
| ISO/IEC/IEEE 12207:2026 第 6.3 章 | 技术管理过程 | 9、10、16、18 |
| ISO/IEC/IEEE 12207:2026 第 6.4 章 | 技术过程 | 9、10.6 至 10.8、11、18 |
| ISO/IEC/IEEE 12207:2026 Annex A | Tailoring Process | 17 |
| ISO/IEC 25010:2023 第 1 章 | ICT Product Quality Model 范围 | 3、11.8、20.11 |
| ISO/IEC 25010:2023 第 4 章 | Product Quality Model | 11.7、11.8、14.4、20.11 |
| ISO/IEC 25010:2023 4.1 | Product Quality Model Structure | 11.8、13.6、20.11 |
| ISO/IEC 25010:2023 4.2 | Product Quality Model Target | 3、11.8、18 |
| ISO/IEC 25010:2023 第 5 章 | 与 Quality-in-use Model 的关系 | 11.2、11.8、18.1 |
| ISO/IEC 25010:2023 Annex C | 使用 Quality Model 进行测量 | 11.8、14.4、15.1、20.6 |

规范性国际标准来源：

1. ISO, [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html)；IEEE Standards Association, [IEEE/ISO/IEC 42010-2022](https://standards.ieee.org/ieee/42010/6846/)。
2. ISO, [ISO/IEC/IEEE 42020:2019](https://www.iso.org/standard/68982.html)；IEEE Standards Association, [IEEE 42020-2019](https://standards.ieee.org/ieee/42020/7601/)。
3. ISO, [ISO/IEC/IEEE AWI 42020](https://www.iso.org/standard/93813.html)，仅用于监测修订状态。
4. ISO, [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html)；IEEE Standards Association, [IEEE/ISO/IEC 12207-2026](https://standards.ieee.org/ieee/12207/11416/)。
5. ISO, [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)。

信息性工程实践来源：

1. MADR, [Markdown Architectural Decision Records 4.0.0](https://adr.github.io/madr/)。
