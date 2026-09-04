# C03 PRD 与 Feature 规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C03 |
| 英文名称 | PRD and Feature Specification |
| 正式文件名 | `C03_PRD_and_Feature_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-27 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3、C02 V6.3 |
| 生产前调研 | RVR-C03-0001 |
| 下游规范 | C04、C05、C06、C07、C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式修订、评审、批准、替代和基线记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定 PRD Package、Feature、User Scenario、Non-goal、Dependency、Constraint、Requirement Index 和 Quality Attribute 的创建、组织、评审、追踪、批准、基线和演进规则。

本规范用于实现以下控制目标：

1. 使一个 PRD Package 对应一个可独立评审、实现、验证和发布的交付范围；
2. 使 Feature 表示用户或业务可感知能力，而不是技术任务、组件、页面或代码改动；
3. 使 PRD 组织背景、目标、用户、场景、范围、质量和交付边界，但不复制 C04 Requirement；
4. 使 User Scenario、Feature、Requirement、Acceptance、Design、Release 和 Observation 形成可查询追踪链；
5. 使 Non-goal、Dependency、Constraint、Risk、Open Question 和质量属性在进入下游前被明确处理；
6. 使 Coding Agent 只能在已批准 Scope 和受控事实源内生成 Draft、候选和检查结果。

## 3. 适用范围

本规范适用于：

- 从已批准或已基线的 Initiative 和 Scope 建立 PRD Package；
- 新功能、重大改进、迁移、替换、退役、实验或运营改进的产品需求组织；
- PRD 背景、目标、用户、角色、场景、范围、Non-goal、Feature、业务规则候选和开放问题；
- 权限、数据、安全、质量属性、UX、技术约束、Risk、Dependency 和验收边界的产品级组织；
- Feature 与 C04 Requirement 的建立、索引和追踪；
- 目标发布、观察要求、评审、批准、基线、变更和替代；
- 人类主导、Agent 辅助和多 Agent 参与的 PRD 编制与评审。

本规范适用于交互式产品、服务、API、数据产品、内部工具、Agent 能力和包含软硬件的 ICT 产品。适用专业扩展是否激活由第 18 章规定。

## 4. 不适用范围

以下内容不由本规范定义：

- Stakeholder Need、Evidence、Problem、Product Definition 和 Product Intent 的发现规则，由 C01 管理；
- Initiative、Scope Boundary、Agent Modification Boundary、Assumption、Risk、Success Metric 和 Initiative Dependency 的建立规则，由 C02 管理；
- 原子 Requirement、Requirement Set、Requirement 属性和需求语句质量，由 C04 管理；
- Acceptance Criterion、Verification、Validation、测试设计和测试结果，由 C05 管理；
- Technical Design、Architecture、接口设计、数据设计和实现决策，由 C06 管理；
- 角色授权、工具权限、批准权限和升级路径的完整模型，由 C07 管理；
- Agent Context 的组装、新鲜度和隔离，由 C08 管理；
- 命令、Tool Call、重试、执行证据和 Agent Run，由 C09 管理；
- Decision、Traceability Matrix 和 Provenance 的统一机制，由 C10 管理；
- Change Request、Configuration、Baseline 和 Release 变更，由 C11 管理；
- Gate Decision、质量门禁和产品健康评价，由 C12 管理；
- 组织级项目组合、预算审批、供应商合同、法律意见或完整质量管理体系。

C03 可以引用上述对象，但禁止建立同名平行资产或复制其正文形成第二事实源。

## 5. 规范性用语

### 5.1 关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。“建议”只表示非强制实践，不作为符合性判定依据。

### 5.2 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 已批准 Exception、Waiver 或 Risk Acceptance 的明确范围；
3. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
4. 本规范已批准或已基线版本；
5. 当前 Product、Initiative 和 Scope 的已批准资产；
6. C04、C05、C06 等专业资产的当前有效 Baseline；
7. 模板、示例和 R3 实践参考。

冲突无法判定时必须停止进入 PRD Ready，并提交人类决策。

### 5.3 可判定表达

所有强制语句必须能够通过 Asset ID、字段、Trace Link、受控状态、数值、枚举、批准记录或检查结果直接判定。禁止使用没有判定条件的“尽量”“最好”“酌情”“快速”“合理”“适当”“用户友好”或“高性能”。

PRD 实例中的产品义务必须由 C04 Requirement ID 承载。PRD 背景、摘要、说明和示例不得以“必须”“不得”“应当”“shall”“must”等未编号强制表达替代 Requirement。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| PRD Package | 对一个可独立评审、实现、验证和发布的交付范围进行组织的正式产品需求包 | 不是永久整产品文档，不复制 Requirement Set |
| Feature | 用户或业务可感知且可独立组织的能力 | 不是 Requirement、技术任务、组件、页面或 Agent Run |
| Feature Record | 描述一个 Feature 的用户、场景、价值、范围、优先级、依赖和 Requirement 引用的正式产物 | 不承载未编号强制义务 |
| User Scenario | 特定用户在使用情境中由触发事件开始、经过活动流程并获得预期结果的结构化描述 | 不是 Acceptance Criterion 或测试用例 |
| User Scenario Set | 管理一个 PRD 范围内主流程、替代流程和异常流程的正式产物 | 场景成员必须具有稳定 Scenario ID |
| Non-goal | 当前 PRD 明确不承诺实现、验证或发布的内容 | 不是 Future Scope，也不是未分析内容 |
| Non-goal Register | 记录排除内容、理由、适用范围和重评条件的正式产物 | 不得缩小或重解释已批准 C02 Out of Scope |
| Product Dependency | PRD、Feature 或 Requirement 成立、实现、验证或发布所依赖的外部对象或条件 | 专业化自 C02 Dependency；冲突时以 C02 上游事实为准 |
| Product Constraint | 限制产品选择、行为、实现或验证空间的强制边界 | 专业化自 C02 Constraint；必须有来源、影响范围和解除条件 |
| Dependency & Constraint Register | 管理 C03 范围内 Dependency 和 Constraint 的正式产物 | 不复制 C02、C06 或 E02 的事实源 |
| Requirement Index | 对 C04 Requirement 的标识、归属、修订、状态、优先级和验证引用建立的受控索引 | 不是 Requirement Set，不复制 Requirement 正文 |
| Quality Attribute | 可用于规定、测量和评价产品质量的特性或子特性 | 强制目标必须进入 C04 Requirement |
| Quality Attribute Summary | 汇总质量业务理由、场景、指标、阈值、环境、优先级、验证策略和 Requirement 引用的正式产物 | 不是 C05 Verification Plan |
| Acceptance Boundary | 规定 PRD 进入验收时必须覆盖的 Feature、Scenario、Requirement、质量目标、证据和排除项 | 不直接定义 Acceptance Criterion |
| Open Question | 当前缺少授权答案且会影响 PRD、Feature、Requirement、质量、依赖或发布的受控问题 | 必须有 Owner、期限、关闭条件和 Blocking 结论 |
| PRD Ready | 七类 C03 产物满足本规范并获得授权 Gate Decision 后的门禁结论 | 不是 DOC State，不得替代 Approved 或 Baselined |
| Applicability Conclusion | 对质量特性是否适用于当前 PRD 的非状态结论 | 只允许 Applicable、Not Applicable、Not Assessed |
| Requirement Gap | Feature 或 Scenario 尚未建立所需 C04 Requirement 的阻断缺口 | 只允许存在于 Draft；PRD Ready 前必须为零 |

未在本章定义的公共术语以 VC-PPG-COM-001 为准。

## 7. 角色与职责

| 角色 | 强制职责 | 禁止事项 |
|---|---|---|
| PRD Owner | 维护 PRD Package；协调七类产物；提交评审；处理范围、质量和开放问题冲突 | 不得自行批准自己的 PRD 或扩大 C02 Scope |
| Feature Owner | 维护 Feature Record；确认用户价值、业务价值、Scenario、Requirement 和 Dependency | 不得以技术任务或页面名称冒充 Feature |
| Scenario Owner | 维护 User Scenario Set；确认用户、任务、环境、流程和结果 | 不得将预期结果写成无证据偏好 |
| Requirement Index Custodian | 同步 C04 Requirement 的 ID、Revision、State、Priority、Verification 和 Acceptance 引用 | 不得复制、改写或批准 Requirement |
| Quality Owner | 组织九类质量特性适用性检查；维护指标、阈值、环境和验证策略 | 不得单独批准 Not Applicable 或将未测量目标写成通过 |
| UX Representative | 核验用户、使用情境、用户参与、整体体验和评价引用 | 不得以单一界面稿替代 Scenario Set |
| Engineering Representative | 核验技术可行性、Dependency、Constraint、Requirement 和设计承接 | 不得在 PRD 内固化未经 C06 决策的设计方案 |
| Quality Representative | 核验验收边界、可验证性、环境和 C05 承接 | 不得把 PRD 评审等同于测试通过 |
| Independent Reviewer | 检查 Scope、Feature、Scenario、Non-goal、Requirement、质量、Risk、Dependency 和 Open Question | 不得是全部内容的唯一作者和唯一责任人 |
| Gate Approver | 按 C12 对 PRD Ready、条件通过、拒绝或退回作授权决定 | 不得绕过阻断项作口头批准 |
| Coding Agent | 整理输入、生成 Draft、提出候选、同步索引、运行检查和报告缺口 | 不得批准 PRD、改变 Scope、最终判定 Not Applicable、关闭 Blocking Question 或作 Gate Decision |

同一人可以承担多个非冲突角色，但 Gate Approver 禁止与该 PRD 的唯一编制者和唯一 Reviewer 为同一人。具体授权、替代和升级安排由 C07 管理。

## 8. 管理对象与关系

### 8.1 管理对象

本规范管理七类正式产物：

1. PRD Package；
2. Feature Record；
3. User Scenario Set；
4. Non-goal Register；
5. Dependency & Constraint Register；
6. Requirement Index；
7. Quality Attribute Summary。

Feature、Scenario、Non-goal、Dependency、Constraint、Index Row、Quality Attribute Entry 和 Open Question 是所属正式产物中的受控成员。成员必须有稳定 ID 和变更历史，但不得建立同名平行事实源。

### 8.2 最低关系链

```text
PRD Package
  ├─ derives-from → Initiative Brief / Product Intent & Goal Record
  ├─ affected-by → Risk Register
  ├─ contains → Feature Record / User Scenario Set / Non-goal Register
  ├─ contains → Dependency & Constraint Register / Requirement Index / Quality Attribute Summary
  └─ released-in → Release

Scope Boundary Record
  └─ constrains → PRD Package / Feature Record

Feature Record
  ├─ addresses → User Scenario
  ├─ depends-on → Dependency Target
  └─ contains → Requirement Reference

C04 Requirement
  ├─ refines → Feature
  ├─ derives-from → User Scenario / Quality Attribute Entry / Constraint
  └─ verified-by → Acceptance Criterion / Verification Result

Constraint
  └─ constrains → PRD Package / Feature / Requirement

Feature
  └─ validated-by → Validation Result
```

每条关系必须可反向查询。禁止使用 `related-to` 或中文“相关”作为正式关系。

### 8.3 产物一致性

七类产物可以在同一界面、目录或物理文件中展示，但必须分别保留 Asset ID、Artifact Type、Owner、State、Revision、Trace Links、Access Classification、Retention Rule 和 History Reference。任一产物更新时必须记录其他 C03 产物是否受影响。

### 8.4 事实源边界

| 信息 | 唯一事实源 | C03 允许动作 |
|---|---|---|
| Product、Problem、Intent、Goal | C01 | 引用当前 Revision，保留摘要和链接 |
| Initiative、Scope、Risk、Success Metric、Initiative Dependency | C02 | 引用，不重写边界 |
| 原子 Requirement | C04 | 在 RQI 中索引，不复制正文 |
| Acceptance、Verification、Validation | C05 | 记录引用和覆盖结论 |
| Technical Design、Architecture | C06 | 记录引用和适用约束 |
| Decision、Trace、Provenance | C10 | 提交关系和决定候选 |
| Change、Baseline、Release | C11 | 记录引用和影响 |
| Gate Decision | C12 | 接收结论，不建立平行状态 |

摘要与事实源不一致时，摘要必须标记 Stale 并停止评审；禁止用摘要覆盖事实源。

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
C02 Handoff
  → Eligibility Check
  → Draft PRD Package
  → Structure Features and User Scenarios
  → Register Non-goals, Dependencies and Constraints
  → Establish C04 Requirements and Requirement Index
  → Define Quality Attributes and C05 Verification Handoff
  → Cross-functional and Independent Review
  → PRD Ready Decision
  → Handoff to C04/C05/C06/C08/C09
  → Controlled Change and Release Tracking
  → Supersede or Retire
```

### 9.2 Eligibility Check

PRD Owner 必须核验 C02 输入是否包含 Initiative Brief、Scope Boundary Record、Assumption & Constraint Register、Risk Register、Success Metric Plan、Dependency Register、Gate Decision 和 Open Questions。输入缺失或未达到 Approved/Baselined 时可以创建 Draft，但禁止进入 In Review、Approved、Baselined 或 PRD Ready。

### 9.3 Draft and Structure

PRD Owner 必须先建立 PRD Package，再建立 FTR、USC、NGR、DCR、RQI 和 QAS。禁止从功能名称清单直接生成 Requirement、Design、代码任务或 Agent Run。

### 9.4 Requirement and Quality Elaboration

Feature、Scenario、业务规则候选、权限、数据、安全和质量目标必须转化为 C04 Requirement 候选，并由 C04 完成正式化。C03 只维护引用、覆盖和缺口。质量指标、阈值、环境和验证策略必须同步到 C05 输入。

### 9.5 Review and Gate

PRD Ready 前必须完成 Product、UX、Engineering、Quality 和适用专业方的交叉评审及 Independent Review。Gate Approver 只能在第 15.3 章阻断项为零时作无条件通过决定。

### 9.6 Handoff and Control

进入 C04、C05、C06 或 C08 时必须提供七类 C03 产物的当前 Revision、上游 Baseline、开放问题、Risk、Dependency、Constraint 和 Gate Decision。仅提供 PRD 标题、聊天摘要或 Feature 名称不得授权下游执行。

### 9.7 Change, Supersede and Retire

Approved 或 Baselined PRD 的 Scope、Feature、Requirement coverage、质量阈值、Acceptance Boundary 或 Target Release 变化必须进入 C11。被替代或退役的 PRD、Feature 和 Scenario 必须保留 Trace、发布范围、观测结果和未关闭责任。

## 10. 强制规则

### 10.1 PRD 创建与粒度

1. 每个 PRD Package 必须具有唯一 PRD ID，并且只属于一个 Primary Initiative。
2. 一个 PRD 可以服务多个 Goal，但必须标记 Primary Goal 并证明其他 Goal 不冲突。
3. 一个 PRD 必须能够被独立评审、实现、验证和发布；不能独立完成上述四项时必须拆分或记录经批准的耦合理由。
4. PRD 必须引用当前 Product Definition、Initiative、Goal、Problem 和 Scope Boundary Revision。
5. PRD 必须定义 Target Release、Acceptance Boundary、观察要求和发布后判定输入。
6. 整个产品的永久说明书、Roadmap、技术设计、测试计划或任务列表禁止作为 PRD Package。
7. 上游输入未达到 Approved 或 Baselined 时，PRD 只能保持 Draft。

### 10.2 背景、目标和用户

1. Background 必须引用已核验 Problem、Evidence、Intent、Goal、Assumption 和当前业务情境。
2. Goal 必须引用 C01/C02 的当前事实源；禁止在 C03 新建未受控 Goal。
3. 必须列明直接用户、间接用户、业务角色、受影响方和明确排除的用户群。
4. 用户与角色必须连接到 User Scenario；只列 Persona 名称不构成场景覆盖。
5. 用户研究、反馈或可用性 Evidence 必须记录来源、日期、样本或覆盖范围和局限。

### 10.3 Scope、Non-goal 和 Future Scope

1. PRD In Scope 必须是 C02 In Scope 的子集或等集。
2. C02 Out of Scope 必须进入 Non-goal Register 或通过 Trace Link 明确继承。
3. 每个 Non-goal 必须记录排除内容、理由、适用范围、Owner 和未来重新评估条件。
4. Future Scope 只能引用 C02 Future Scope，不构成当前 Feature、Requirement、Agent Context 或发布承诺。
5. Scope、Non-goal 和 Feature 存在重叠或冲突时必须阻断评审。
6. Coding Agent 发现 Scope 不足时必须提出 Scope Change 候选，禁止自行扩大。

### 10.4 Feature 定义与拆分

1. 每个 Feature 必须描述目标用户能够感知的能力或业务能够判定的结果。
2. Feature 必须包含用户价值、业务价值、适用 Scope、Scenario、Priority、Dependency 和 Requirement 引用。
3. Feature 名称必须采用“能力或结果”表达，禁止仅使用页面名、组件名、服务名、数据库名、接口名、技术方案或任务动作。
4. 一个 Feature 可以跨多个模块，但必须保持同一用户结果和可追踪 Requirement 集。
5. 一个 Feature 包含互不相关的用户结果、独立发布路径或冲突 Priority 时必须拆分。
6. 一个 Feature 无法关联至少一个 C04 Requirement 时可以在 Draft 中记录 Requirement Gap，但禁止进入 PRD Ready。
7. 删除、合并或拆分 Feature 必须记录原 Feature、目标 Feature、Requirement、Scenario、Release 和 Observation 影响。

### 10.5 User Scenario

1. 每个 Scenario 必须具有稳定 USC Member ID。
2. Scenario 必须包含目标用户、使用情境、触发事件、前置条件、主流程、替代流程、异常流程和预期结果。
3. Context of Use 必须覆盖用户、目标、任务、资源以及适用的技术、物理、社会、文化或组织环境。
4. 主流程必须描述用户与产品之间的活动顺序，禁止写成代码流程、接口调用序列或测试步骤。
5. 替代流程和异常流程为空时必须写明核验范围和 `None` 依据。
6. 每个 In Scope Feature 必须关联至少一个 Scenario；每个 Scenario 必须关联至少一个 Feature。
7. Scenario 中出现的强制产品行为必须转化为 C04 Requirement。

### 10.6 Requirement 边界与索引

1. PRD 正文禁止承载未编号强制产品需求。
2. 每项业务规则、权限规则、数据规则、安全义务、质量阈值和外部约束必须由 C04 Requirement ID 承载。
3. Requirement Index 必须从 C04 当前事实源同步 Requirement ID、Title、Type、Feature、Revision、State、Priority、Verification Method 和 Acceptance Reference。
4. RQI 可以展示 Title，但禁止复制 Requirement Statement、Rationale、完整 Acceptance Criteria 或设计内容。
5. Requirement 变化后，RQI 必须标记同步时间、Source Revision 和受影响 Feature/Scenario/QAS。
6. RQI Source Revision 落后于 C04 当前 Revision 时必须标记 Stale，并阻断 PRD Ready 或 Baseline 使用。
7. 未经 C04 批准的候选只能标记为 Candidate Reference，禁止计入 Requirement Coverage 的 `Covered` 结论。

### 10.7 业务规则、权限、数据和安全

| 主题 | C03 必须记录 | 正式事实源 |
|---|---|---|
| Business Rule | 规则来源、适用角色/场景、触发、结果、例外和 Requirement 引用 | C04 Requirement |
| Permission | 主体、对象、操作、条件、拒绝行为、审计需要和 Requirement 引用 | C04；授权模型由 C07/E02 |
| Data | 数据对象、来源、用途、读写方向、生命周期、质量或敏感性约束和 Requirement 引用 | C04；数据治理由 E03 |
| Security | 资产、威胁或义务来源、保护目标、适用场景、Risk 和 Requirement 引用 | C04；安全治理由 E02 |

PRD 可以保留非规范性摘要，但必须标注 `Informative Summary` 并指向事实源。摘要不一致时以事实源为准。

### 10.8 Quality Attribute

1. QAS 必须对 ISO/IEC 25010:2023 九类特性逐类作 Applicability Conclusion。
2. 九类特性为 functional suitability、performance efficiency、compatibility、interaction capability、reliability、security、maintainability、flexibility、safety。
3. `Not Assessed` 必须阻断 PRD Ready。
4. `Not Applicable` 必须记录判定依据、Quality Owner、Independent Reviewer、Gate Approver 和日期；Coding Agent 禁止作最终判定。
5. 每个 `Applicable` 项必须记录业务理由、适用 Feature/Scenario、指标、阈值、环境、Priority、验证策略和 C04 Requirement 引用。
6. 只写“高性能”“安全”“稳定”“易用”或“可扩展”不构成质量目标。
7. 指标没有单位、计算方式、数据来源或环境时禁止进入 PRD Ready。
8. 阈值必须可由 C05 的 Verification 或 Validation 判定；无法验证时必须建立 Open Question 或 Requirement Gap。
9. 质量属性权衡必须记录受影响 Goal、Feature、Requirement、Risk、Decision Owner 和 C10 Decision 引用。
10. safety 与 security 必须分别判定；禁止用一个“安全”字段合并二者。

九类特性的项目内部工作译名如下：

| 英文权威标识 | 内部工作译名 |
|---|---|
| functional suitability | 功能适合性 |
| performance efficiency | 性能效率 |
| compatibility | 兼容性 |
| interaction capability | 交互能力 |
| reliability | 可靠性 |
| security | 信息安全性 |
| maintainability | 可维护性 |
| flexibility | 灵活性 |
| safety | 人身、财产与环境安全性 |

### 10.9 UX 与人本设计

1. PRD 必须说明用户参与方式、时间、样本或覆盖范围和 Evidence 引用；无用户参与时必须记录批准的限制和 Risk。
2. Scenario 必须体现已知用户、任务和环境，不得从界面布局反推用户需要。
3. Feature 必须说明整体用户体验影响，包括开始、主要交互、异常、恢复和结束结果。
4. 设计方案、原型和研究报告只能通过链接引用；正式设计由 C06 管理。
5. 用户中心评价结论必须连接受影响 Scenario、Feature、Requirement 和下一步行动。
6. 用户反馈导致 Scope 或 Baseline 变化时必须进入 C11。

### 10.10 Dependency、Constraint 和 Risk

1. DCR 的每个成员必须标识 `Dependency` 或 `Constraint`。
2. Dependency 必须记录对象、提供方、来源、影响范围、需要日期、满足条件、失败影响、替代方案、Owner 和 Readiness。
3. Constraint 必须记录陈述、强制来源、适用范围、影响、解除条件、Owner 和期限。
4. C02 已存在的 Dependency、Constraint 或 Risk 必须通过 Trace Link 引用，禁止复制后独立维护。
5. Blocking Dependency 未满足、强制 Constraint 无承接 Requirement 或 High/Critical Risk 无处置时必须阻断 PRD Ready。
6. 技术 Constraint 必须由 Engineering Representative 核验；安全、隐私、合规或数据 Constraint 必须触发适用扩展评审。
7. Dependency 或 Constraint 变化必须执行 Feature、Requirement、Quality、Acceptance、Release 和 Agent Context 影响分析。

### 10.11 Open Question

1. 每个 Open Question 必须包含 Question ID、Statement、Affected Assets、Owner、Due Date、Closure Condition、Blocking、Escalation Path 和 CASE State。
2. 只允许使用 CASE 状态：Open、In Progress、Blocked、Resolved、Closed、Reopened、Cancelled。
3. `Blocking = Yes` 且 State 不是 Closed 或 Cancelled 时禁止 PRD Ready；Cancelled 必须有授权决定。
4. 答案形成产品义务时必须建立或更新 C04 Requirement；形成设计决定时必须进入 C06/C10。
5. 禁止在聊天、评论或会议中口头关闭 Open Question 而不更新受控记录。

### 10.12 Acceptance Boundary

Acceptance Boundary 必须列明：

- Included Feature、Scenario 和 Requirement；
- Applicable Quality Attribute 和阈值；
- 必需的 C05 Acceptance、Verification 和 Validation 引用；
- 测试或评价环境边界；
- 明确排除项；
- 必须解决的 Risk、Dependency、Constraint 和 Open Question；
- 证据新鲜度和接受角色；
- 失败、条件通过和重新评审路径。

Acceptance Boundary 只定义覆盖和输入，禁止复制 Acceptance Criterion 或测试步骤。

### 10.13 Release 与 Observation

1. PRD 必须记录 Target Release、发布范围、前置条件、分阶段或回滚约束和 C11 Release 引用。
2. Target Release 是计划引用，不等同于 Release 资产或发布批准。
3. 必须列明发布后 Success Metric、Guardrail、产品行为或质量属性的观察对象、数据来源、观察周期、Owner 和判定引用。
4. 观察义务必须追踪到 C02 Success Metric、C05 Validation、C11 Release 或 E05 Observation。
5. 发布结果与 PRD 假设、Feature 价值或质量目标冲突时必须回流 C01/C02/C11/C12。

### 10.14 Review、批准与基线

1. PRD In Review 前七类产物必须存在且 Source Revision 可识别。
2. Review 必须覆盖 Product、UX、Engineering、Quality 和适用的安全、数据、架构或运营角色。
3. Reviewer Finding 必须有 Finding ID、Severity、Affected Asset、Owner、Due Date、State 和 Recheck Result。
4. Coding Agent 可以生成检查结果和 Finding 候选，禁止关闭需要人类判断的 Finding。
5. 七类产物未全部 Approved 或 Baselined 时禁止作出无条件 PRD Ready。
6. PRD Ready 必须由 C12 Gate Decision 承载，禁止在 PRD 的 DOC State 中自造 `Ready`。
7. Baselined 内容变化必须建立 Change Request 和新 Revision，禁止退回 Draft 原位覆盖。

### 10.15 Coding Agent 行为边界

Coding Agent 可以：

- 读取已授权的上游资产并生成七类 C03 产物 Draft；
- 从已批准文本提取 Feature、Scenario、Non-goal、Dependency、Constraint、Requirement 和质量属性候选；
- 同步 Requirement Index、检查 Trace Link、字段完整性、状态和 Revision；
- 提出 Requirement Gap、Open Question、Risk、Scope Change 和扩展适用性候选；
- 运行结构、术语、表格、链接和一致性检查。

Coding Agent 禁止：

- 扩大或重解释 Product、Initiative、Scope、Non-goal 或 Agent Modification Boundary；
- 把自然语言摘要、聊天内容、代码、原型或测试结果提升为 Approved Requirement；
- 最终决定 Feature Priority、Quality Not Applicable、Risk Acceptance、Waiver、Gate 或 Baseline；
- 关闭 Blocking Question、删除反对意见或覆盖人类决定；
- 从 Draft PRD 直接生成可执行命令、生产变更、部署或发布批准；
- 声称 C03、项目或组织完整符合或通过国际标准认证。

## 11. 受控状态

### 11.1 正式产物状态

| 产物 | 类型代码 | 状态模型 | 允许状态 |
|---|---|---|---|
| PRD Package | PRD | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Feature Record | FTR | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| User Scenario Set | USC | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Non-goal Register | NGR | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Dependency & Constraint Register | DCR | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Requirement Index | RQI | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Quality Attribute Summary | QAS | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |

Open Question 以及需要独立处理的 Dependency 或 Constraint 成员使用 CASE。Scenario、Non-goal、Index Row 和 Quality Attribute Entry 的治理状态由所属 DOC 产物表示，不设置独立 State。RQI 中的 Requirement State 是对 C04 状态的只读镜像，不是 RQI 成员状态。

### 11.2 非状态字段

以下字段禁止冒充 State：

| 字段 | 允许值 |
|---|---|
| PRD Ready Conclusion | Pass、Conditional Pass、Fail、Not Assessed |
| Applicability Conclusion | Applicable、Not Applicable、Not Assessed |
| Requirement Coverage | Covered、Gap、Not Applicable |
| Dependency Readiness | Confirmed、At Risk、Unavailable、Not Assessed |
| Blocking | Yes、No |
| Sync Status | Current、Stale、Failed |

`Conditional Pass` 必须由 C12 Gate Decision 记录条件、Owner、期限和失效规则。

### 11.3 状态转换规则

1. 状态转换必须遵循 VC-PPG-COM-002。
2. 七类产物未全部达到 Approved 或 Baselined 时禁止作出无条件 PRD Ready。
3. Changes Required 必须记录 Finding、Owner、整改期限和复核结果。
4. Baselined 内容变化必须建立 Change Request 和新 Revision，禁止退回 Draft 原位覆盖。
5. Rejected、Superseded 或 Retired 资产禁止作为当前默认输入，但必须保留历史。
6. Gate、Applicability、Coverage、Readiness 和 Sync 结论不得自动改变 DOC State。

## 12. 必需产物

| 产物 | 目的 | 最低创建条件 | 主要下游 |
|---|---|---|---|
| PRD Package | 组织一个独立交付范围的产品需求上下文、边界和追踪 | C02 Initiative 被提出进入 PRD 编制 | C04–C12 |
| Feature Record | 定义用户或业务可感知能力及其价值、场景和需求覆盖 | PRD Package 创建后识别到能力 | C04、C05、C06、C10 |
| User Scenario Set | 记录用户、情境、触发、流程和预期结果 | PRD Package 创建后立即建立 | C04、C05、C06 |
| Non-goal Register | 明确当前 PRD 排除项和重评条件 | 每个 PRD 必须创建；无成员时记录核验范围和结论 | C04、C08、C11、C12 |
| Dependency & Constraint Register | 管理 PRD 级依赖和强制边界 | 每个 PRD 必须创建；无成员时记录核验范围和结论 | C04–C06、C09、C12 |
| Requirement Index | 建立 Feature 与 C04 Requirement 的当前索引 | 首个 Requirement 候选产生时；无候选时仍需空索引和 Gap | C04、C05、C10–C12 |
| Quality Attribute Summary | 管理九类质量特性的适用性、目标和验证承接 | 每个 PRD 必须创建 | C04、C05、C06、C12、E02、E03 |

P2 档位禁止合并 PRD、FTR、USC、NGR、DCR、RQI 或 QAS 的独立身份。

## 13. 产物必填信息

### 13.1 通用必填信息

每项正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C03 类型专属要求。

### 13.2 PRD Package

必须包含：

- PRD ID、Name 和 Summary；
- Product Definition ID 与 Revision；
- Initiative ID、Primary Goal 和其他 Goal；
- Product Intent、Problem 和 Evidence 引用；
- Background 和 Problem Summary；
- Target User、Indirect User、Role 和 Affected Stakeholder；
- In Scope、Out of Scope、Future Scope 与 Scope Boundary Revision；
- Feature Record 列表；
- User Scenario Set、Non-goal Register 和 DCR 引用；
- Requirement Index 和 QAS 引用；
- Business Rule、Permission、Data、Security 和 UX 摘要及事实源链接；
- Risk 和 Dependency 引用；
- Acceptance Boundary；
- Target Release 和发布约束；
- Observation Requirement；
- Open Question；
- Review、Approval、Gate Decision 和 Baseline 引用。

### 13.3 Feature Record

必须包含：

- FTR ID、Name 和所属 PRD；
- User-perceptible Capability；
- Target User 和 Scenario 引用；
- User Value 和 Business Value；
- In Scope 与 Non-goal 冲突检查；
- Requirement 引用和 Requirement Coverage；
- Priority、Basis、Decider 和 Date；
- Dependency、Constraint 和 Risk；
- Acceptance Boundary 引用；
- Target Release；
- Owner、Review 和 History。

Priority 只允许使用 Critical、High、Normal、Low，并继承 C02 的判定语义。

### 13.4 User Scenario Set

每个 Scenario 成员必须包含：

- Scenario ID 和 Name；
- Target User、Role 和 Goal；
- Context of Use；
- Trigger Event；
- Preconditions；
- Main Flow；
- Alternate Flow；
- Exception Flow；
- Expected Outcome；
- User Involvement 或 Evidence 引用；
- Feature 和 Requirement 引用；
- Applicable Quality Attribute；
- Assumption、Risk、Open Question；
- Scenario Owner 和 Revision History。

### 13.5 Non-goal Register

每个 Non-goal 成员必须包含：

- Non-goal ID；
- Excluded Content；
- Exclusion Reason；
- Applicable Scope；
- Source Scope Item；
- Future Reconsideration Condition；
- Owner；
- Conflicting Feature or Requirement Check；
- Decision、Revision 和 History 引用。

### 13.6 Dependency & Constraint Register

每个成员必须包含：

- Entry ID 和 Member Type；
- Statement 或 Dependency Target；
- Source；
- Provider 或 Authority；
- Impact Scope；
- Need Date 或 Effective Period；
- Fulfilment 或 Release Condition；
- Failure Impact；
- Alternative 或 Exception Path；
- Owner；
- PRD、Feature、Requirement、Risk 引用；
- Dependency Readiness 或 CASE State；
- Evidence、Review 和 History。

### 13.7 Requirement Index

每个索引行必须包含：

- Requirement ID；
- Title；
- Type；
- Feature ID；
- Scenario ID；
- Current Revision；
- C04 State；
- Priority；
- Verification Method；
- Acceptance Reference；
- Quality Attribute Reference；
- Source Snapshot；
- Sync Time 和 Sync Status。

### 13.8 Quality Attribute Summary

每个九类特性条目必须包含：

- 英文权威标识和适用子特性；
- Applicability Conclusion；
- Business Reason；
- Applicable Product、Feature 和 Scenario；
- Metric、Unit、Formula 和 Data Source；
- Threshold 或 Target；
- Environment Condition；
- Priority；
- Verification Strategy；
- Requirement Reference；
- Trade-off、Risk 和 Decision Reference；
- Quality Owner、Reviewer、Approver 和 Date。

## 14. 质量准则

### 14.1 单项产物质量

| 产物 | 通过条件 |
|---|---|
| PRD Package | 独立交付范围可判定；上游、七类产物、Acceptance、Release 和 Observation 完整 |
| Feature Record | 能力对用户或业务可感知；价值、Scenario、Requirement、Priority 和 Dependency 完整 |
| User Scenario Set | 用户、情境、触发、前置、主/替代/异常流程和结果完整 |
| Non-goal Register | 每项排除内容、理由、范围和重评条件可判定 |
| DCR | 来源、影响、满足/解除条件、Owner、期限和下游引用完整 |
| Requirement Index | 与 C04 当前 Revision 一致，无复制正文和 Stale 行 |
| QAS | 九类特性全部评估；适用项可测量、可验证、可追踪 |

### 14.2 资产集合质量

七类产物集合必须同时满足：

1. PRD Scope 不超出 C02 Scope；
2. 每个 In Scope Feature 至少关联一个 Scenario 和一个当前有效 Requirement；
3. 每个 Scenario 至少关联一个 Feature，强制行为均有 Requirement；
4. Non-goal 不与 In Scope Feature 或 Requirement 冲突；
5. RQI 与 C04 当前事实源一致；
6. QAS 适用项均连接 Requirement 和 C05 验证策略；
7. Blocking Dependency、High/Critical Risk、Requirement Gap 和 Blocking Question 为零；
8. 七类产物 Revision 和 Trace Link 相互一致；
9. Acceptance Boundary 能覆盖全部 In Scope Feature、Scenario、Requirement 和 Applicable Quality Attribute；
10. Target Release 和 Observation 要求有下游承接。

### 14.3 独立可用性

独立 Reviewer 在只读取当前有效上游引用和七类 C03 产物时，必须能够回答：

- 为什么做、为谁做、解决什么问题；
- 本次做什么、不做什么、以后重新评估什么；
- 包含哪些 Feature 和 Scenario；
- 每个 Feature 由哪些 Requirement 规定；
- 有哪些 Dependency、Constraint、Risk 和 Open Question；
- 适用哪些质量属性、如何测量和验证；
- 验收边界、目标发布和观察要求是什么。

任一问题无法从受控资产直接回答时，资产集合不符合本规范。

## 15. 验证与符合性检查

### 15.1 自动检查

自动检查至少包括：

- 文件名、Asset ID、Artifact Type 和 Revision 格式；
- 七类产物存在性和独立身份；
- DOC、CASE 和只读镜像状态值合法性；
- 必填字段非空和受控枚举合法性；
- Trace Link 关系类型和目标可解析性；
- C02 Scope 与 PRD/Feature Scope 的包含关系；
- Feature—Scenario—Requirement 覆盖；
- RQI Source Revision、Sync Time 和 Sync Status；
- QAS 九类特性完整性；
- 指标、单位、阈值、环境、验证策略和 Requirement 引用；
- Non-goal 与 Feature/Requirement 冲突；
- Blocking Dependency、Requirement Gap 和 Blocking Question；
- Markdown 表格列数、围栏和链接完整性。

自动检查结果必须记录工具、版本、时间、输入 Revision、结果和未覆盖范围。

### 15.2 人工评审

人工评审至少检查：

- Feature 是否真正对用户或业务可感知；
- Scenario 是否反映真实用户、任务和环境；
- Value、Goal、Scope 和 Non-goal 是否一致；
- 未编号强制需求是否被隐藏在 PRD 摘要中；
- Business Rule、Permission、Data、Security 和质量义务是否进入 C04；
- 九类质量特性的 Applicable/Not Applicable 依据；
- 质量指标、阈值和环境是否支持真实验证；
- UX、技术、风险、依赖、验收和发布边界是否可执行；
- R3 模板实践是否越权替代 R1 或内部治理基线。

### 15.3 PRD Ready 阻断条件

存在以下任一情况时必须拒绝无条件 PRD Ready：

1. C02 输入不是 Approved 或 Baselined，或缺少有效 Gate Decision；
2. 七类 C03 产物任一缺失或不是 Approved/Baselined；
3. PRD Scope 超出 C02 Scope；
4. Feature 不是用户/业务可感知能力；
5. 任一 In Scope Feature 没有 Scenario 或当前有效 Requirement；
6. PRD 正文存在未编号强制产品需求；
7. RQI 为 Stale、Failed 或复制 Requirement 正文；
8. QAS 任一九类特性为 Not Assessed；
9. Applicable Quality Attribute 缺少指标、阈值、环境、验证策略或 Requirement；
10. Blocking Dependency 未满足；
11. High/Critical Risk 无处置或授权接受；
12. Blocking Open Question 未关闭；
13. Non-goal 与 Feature、Requirement 或 Scope 冲突；
14. Acceptance Boundary 无法覆盖全部 In Scope 内容；
15. Target Release、Observation 或下游责任未明确；
16. Independent Review 或必要专业评审未完成；
17. ISO/IEC/IEEE 29148 替代版本状态未在基线前复核。

### 15.4 符合性声明限制

只有在全部适用检查完成、证据可追溯且获得授权决定后，才可以声明“符合 C03 V0.1 的内部 PRD Ready 条件”。禁止据此声明符合、通过或获得 ISO、IEC、IEEE 认证。

## 16. 追踪与记录要求

### 16.1 最低追踪覆盖

| 源资产 | 正式关系 | 目标资产 | 最低要求 |
|---|---|---|---|
| PRD Package | `derives-from` | Initiative Brief、Product Intent & Goal Record | 必须 |
| Scope Boundary Record | `constrains` | PRD Package、Feature Record | 必须 |
| PRD Package | `contains` | FTR、USC、NGR、DCR、RQI、QAS | 必须 |
| Feature Record | `addresses` | User Scenario | 每个 Feature 至少一条 |
| Requirement | `refines` | Feature | 每个 In Scope Feature 至少一条 |
| Requirement | `derives-from` | User Scenario、Quality Attribute Entry 或 Constraint | 按来源建立 |
| Feature | `depends-on` | Dependency Target | 存在依赖时必须 |
| Constraint | `constrains` | PRD、Feature 或 Requirement | 存在约束时必须 |
| Requirement | `verified-by` | Acceptance Criterion 或 Verification Result | PRD Ready 前必须有策略引用，执行后补结果 |
| Feature | `validated-by` | Validation Result | 适用时必须 |
| PRD Package | `released-in` | Release | 发布时必须 |

### 16.2 记录保留

必须永久关联保留：

- 七类产物的全部正式 Revision 和 Snapshot；
- Reviewer、Finding、反对意见、整改和复核结果；
- Requirement Index 同步记录和 Stale/Failed 历史；
- Applicability、Priority、Trade-off、Waiver、Risk Acceptance 和 Gate Decision；
- 用户参与、质量判定、发布和观察引用；
- Superseded、Retired、Rejected 和 Cancelled 的原因与替代关系。

聊天、会议记录或 Agent 输出只有被登记为受控资产后才能作为正式依据。

### 16.3 影响与变更追踪

以下变化必须执行七类产物及 C04–C12 影响分析：

- Product、Problem、Intent、Goal 或 Scope Revision 变化；
- Feature 新增、拆分、合并、删除或 Priority 变化；
- Scenario、Non-goal、Dependency、Constraint 或 Risk 变化；
- Requirement Revision、State、Verification 或 Acceptance 变化；
- 质量属性适用性、指标、阈值、环境或 Trade-off 变化；
- Acceptance Boundary、Target Release 或 Observation 变化；
- Open Question 的答案推翻现有内容；
- 国际标准发布替代版本。

## 17. 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C03 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

C03 在 DT-01 新产品、DT-02 产品族实例化、DT-03 新功能和改变产品行为或范围的 DT-05 需求修订时适用。纯 DT-04 澄清、DT-06 缺陷修复、外部行为不变的 DT-07 工程变更、以及不改变需求的 DT-08 配置/内容变更应引用现有 PRD/Feature，不创建平行 PRD。

PRD Package 是条件产物。被触发时必须保持产品目标、范围、Non-goal、Feature、Scenario、Requirement Index 和适用质量属性完整；未触发时 Artifact Manifest 记录规则引用，不创建空 PRD。

### 17.1 当前 P2 决议

当前项目采用 P2：

1. 必须使用统一二十章结构；
2. 必须保持七类 C03 产物的独立身份；
3. 必须为七类产物分别提供模板；
4. 必须执行九类质量特性适用性检查；
5. 禁止使用 Mini-PRD 替代 PRD Package；
6. 禁止省略 Non-goal、DCR、RQI 或 QAS；
7. 可以同页展示或自动生成视图，但不得合并 Asset ID、State、Revision 或事实源。

### 17.2 未来裁剪

只有 VC-PPG-DEC-001 被正式变更后才可以启用其他裁剪档位。裁剪决定必须记录目的、适用范围、保留信息、替代控制、Risk、批准人、期限和复核计划；禁止由 Coding Agent 自行裁剪。

## 18. 扩展接口

| 规范 | 触发接口 | C03 必须输出或接收的信息 |
|---|---|---|
| C01 | Problem、Intent、Goal、Evidence 或用户认识变化 | 接收当前 Revision；输出新 Evidence、Need、Problem 或 Assumption 候选 |
| C02 | Initiative、Scope、Risk、Metric 或 Dependency 变化 | 接收六类 C02 产物和 Gate；输出 Scope Change、Risk 和 Dependency 反馈 |
| C04 | 建立或更新 Requirement | 输出 Feature、Scenario、规则候选、Constraint、QAS 和 RQI；接收 Requirement ID/Revision/State |
| C05 | 建立 Acceptance、Verification 和 Validation | 输出 Acceptance Boundary、Scenario、QAS、Risk 和 Observation；接收覆盖与结果 |
| C06 | 建立 Technical Design 和 Architecture | 输出 Feature、Requirement、Constraint、Quality 和 Dependency；接收设计引用和 Trade-off |
| C07 | 需要角色、权限、批准或升级 | 输出 Owner、Reviewer、Approver、Permission 需求和冲突 |
| C08 | 组装 Agent Context | 输出七类产物当前 Revision、Scope、Non-goal、Requirement 和失效条件 |
| C09 | Agent 执行 | 输出已批准 Requirement、Acceptance、Scope 和 Dependency；禁止以 PRD 摘要直接授权命令 |
| C10 | 决策、追踪和 Provenance | 输出关系候选、Priority、Applicability、Trade-off、Finding 和 Open Question 决定输入 |
| C11 | Scope、Baseline、Feature、Requirement、Quality 或 Release 变化 | 输出 Change Request、影响范围和当前 Snapshot |
| C12 | PRD Ready 和产品健康 | 输出检查结果、Blocking 项、Residual Risk、Coverage、Release 和 Observation 输入 |
| E01 | 复杂系统、关键服务、架构权衡或跨边界 Dependency | 输出 Feature、Quality、Constraint、Risk 和 Requirement |
| E02 | 安全、隐私、合规、敏感数据、显著 AI 风险或 safety | 输出资产、数据、威胁/危害、义务、Risk 和 Requirement |
| E03 | 数据产品、Metric、RAG、训练数据或关键数据质量 | 输出数据语义、来源、用途、质量阈值、授权和 Dependency |
| E04 | 多 Agent、长期维护或正式记录激活 | 输出 Source、Revision、Freshness、Access 和 Replacement 关系 |
| E05 | 发布观察、事故、SLO 或运行反馈回流 | 接收 Observation、Incident、Metric 和 Feature/Quality 结果 |

## 19. 参考标准

### 19.1 R1 国际标准

| 标准 | 完整名称 | 适用主题 | 适用性限制 |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | Systems and software engineering — Life cycle processes — Requirements engineering | 信息项、Requirement 构造、需求集合、属性、业务/Stakeholder 分析、需求管理和追踪 | 已进入修订流程；替代版发布后必须影响分析 |
| ISO/IEC 25030:2019 | Systems and software engineering — Systems and software quality requirements and evaluation (SQuaRE) — Quality requirements framework | 质量需要、质量需求定义、使用、治理、追踪和验证因素 | 不规定本项目具体指标、阈值或测量方法 |
| ISO/IEC 25010:2023 | Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model | 九类产品质量特性、目标对象和测量使用 | C03 不重制完整质量模型 |
| ISO 9241-210:2019 | Ergonomics of human-system interaction — Part 210: Human-centred design for interactive systems | 用户、任务、环境、用户参与、迭代评价和整体用户体验 | C03 不规定完整 UX 研究方法 |

### 19.2 R3 实践参考

| 来源 | 参考主题 | 适用限制 |
|---|---|---|
| Aha! PRD template | Objective、Background、Assumptions、Features、UX 链接、Constraints、Dependencies 和 Open Questions 的组织 | 仅影响呈现和协作，不是规范性依据 |
| Atlassian Product requirements 与 Confluence template | Goals、Assumptions、User stories、Design links、Questions 和 What we are not doing | 禁止替代七类产物、C02 Scope 或 C04 Requirement |

### 19.3 来源与复核边界

版本和条款目录依据 ISO 官方页面、ISO Online Browsing Platform 和 RVR-C03-0001 核验。未取得合法完整标准文本时，本规范只声明参考和条款主题对齐，不声明完整条款符合性。R3 来源不能覆盖 R1、上位蓝图或公共治理基线。

## 20. 附录

### 20.1 通用资产头模板

所有 C03 模板必须先包含：

```markdown
| 信息项 | 内容 |
|---|---|
| Asset ID | <类型代码-顺序号> |
| Artifact Type | <正式英文名称> |
| Name or Summary | <名称或摘要> |
| Purpose | <治理目的> |
| Source | <上游来源> |
| Owner | <人类责任人> |
| State | <DOC 受控状态> |
| Current Revision | <修订号与快照> |
| Created and Updated | <创建与更新信息> |
| Applicable Scope | <Product、Initiative、PRD 和时间> |
| Trace Links | <受控关系> |
| Access Classification | <访问级别> |
| Retention Rule | <保留规则> |
| History Reference | <历史和变更引用> |
```

### 20.2 PRD Package 模板骨架

```markdown
| 字段 | 内容 |
|---|---|
| PRD ID / Name / Summary | |
| Product Definition / Revision | |
| Initiative / Primary Goal / Other Goals | |
| Product Intent / Problem / Evidence | |
| Background / Problem Summary | |
| Target Users / Roles / Affected Stakeholders | |
| Scope Boundary Revision | |
| In Scope / Out of Scope / Future Scope | |
| Feature Record List | |
| USC / NGR / DCR / RQI / QAS Revision | |
| Business Rule / Permission / Data / Security Summary | |
| UX / Design / Research References | |
| Risk / Dependency References | |
| Acceptance Boundary | |
| Target Release / Release Constraints | |
| Observation Requirements | |
| Open Questions | |
| Review / Approval / Gate / Baseline | |
```

### 20.3 Feature Record 模板骨架

```markdown
| 字段 | 内容 |
|---|---|
| FTR ID / Name | |
| PRD ID | |
| User-perceptible Capability | |
| Target User / Scenario | |
| User Value / Business Value | |
| In Scope / Non-goal Conflict Check | |
| Requirement References / Coverage | |
| Priority / Basis / Decider / Date | |
| Dependency / Constraint / Risk | |
| Acceptance Boundary Reference | |
| Target Release | |
| Feature Owner / Review / History | |
```

### 20.4 User Scenario Set 模板骨架

```markdown
| Scenario ID | Name | Target User / Role / Goal | Context of Use | Trigger | Preconditions | Main Flow | Alternate Flow | Exception Flow | Expected Outcome | Feature / Requirement | Quality Attribute | Evidence / Assumption / Risk | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| USC-<NNNN>-S01 | | | | | | | | | | | | | |
```

### 20.5 Non-goal Register 模板骨架

```markdown
| Non-goal ID | Excluded Content | Exclusion Reason | Applicable Scope | Source Scope Item | Reconsideration Condition | Owner | Feature / Requirement Conflict | Decision / History |
|---|---|---|---|---|---|---|---|---|
| NGR-<NNNN>-N01 | | | | | | | | |
```

### 20.6 Dependency & Constraint Register 模板骨架

```markdown
| Entry ID | Member Type | Statement or Target | Source / Provider / Authority | Impact Scope | Need Date / Period | Fulfilment or Release Condition | Failure Impact | Alternative / Exception | Owner | PRD / Feature / Requirement / Risk | Readiness or CASE State | Evidence / History |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DCR-<NNNN>-D01 | Dependency | | | | | | | | | | Not Assessed | |
| DCR-<NNNN>-C01 | Constraint | | | | | | | | | | Open | |
```

### 20.7 Requirement Index 模板骨架

```markdown
| Requirement ID | Title | Type | Feature ID | Scenario ID | Current Revision | C04 State | Priority | Verification Method | Acceptance Reference | Quality Attribute | Source Snapshot | Sync Time / Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REQ-<NNNN> | | | | | | | | | | | | Current |
```

### 20.8 Quality Attribute Summary 模板骨架

```markdown
| Quality Characteristic | Applicable Subcharacteristic | Applicability | Business Reason | Product / Feature / Scenario | Metric / Unit / Formula / Data Source | Threshold | Environment | Priority | Verification Strategy | Requirement | Trade-off / Risk / Decision | Owner / Reviewer / Approver / Date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| functional suitability | | Not Assessed | | | | | | | | | | |
| performance efficiency | | Not Assessed | | | | | | | | | | |
| compatibility | | Not Assessed | | | | | | | | | | |
| interaction capability | | Not Assessed | | | | | | | | | | |
| reliability | | Not Assessed | | | | | | | | | | |
| security | | Not Assessed | | | | | | | | | | |
| maintainability | | Not Assessed | | | | | | | | | | |
| flexibility | | Not Assessed | | | | | | | | | | |
| safety | | Not Assessed | | | | | | | | | | |
```

### 20.9 Open Question 模板

```markdown
| Question ID | Statement | Affected Assets | Owner | Due Date | Closure Condition | Blocking | Escalation Path | CASE State | Answer / Decision / Requirement |
|---|---|---|---|---|---|---|---|---|---|
| OQ-<NNNN>-Q01 | | | | | | Yes / No | | Open | |
```

### 20.10 C03 质量检查清单

| 检查 ID | 检查项 | 通过条件 | 结果 |
|---|---|---|---|
| C03-CHK-001 | 上游状态 | C02 六类产物为 Approved/Baselined 且 Gate 有效 | 待检查 |
| C03-CHK-002 | PRD 粒度 | 可独立评审、实现、验证和发布 | 待检查 |
| C03-CHK-003 | 上游追踪 | Product、Initiative、Goal、Problem 和 Scope Revision 完整 | 待检查 |
| C03-CHK-004 | 七类产物 | PRD、FTR、USC、NGR、DCR、RQI、QAS 身份独立 | 待检查 |
| C03-CHK-005 | Scope 一致性 | PRD/Feature 不超出 C02 In Scope | 待检查 |
| C03-CHK-006 | Non-goal | 排除、理由、范围、重评条件和 Owner 完整 | 待检查 |
| C03-CHK-007 | Feature 语义 | 每项为用户或业务可感知能力 | 待检查 |
| C03-CHK-008 | Feature 覆盖 | 每个 In Scope Feature 有 Scenario 和当前 Requirement | 待检查 |
| C03-CHK-009 | Scenario 结构 | 用户、情境、触发、前置、主/替代/异常流程和结果完整 | 待检查 |
| C03-CHK-010 | 未编号需求 | PRD 正文不存在未编号强制产品需求 | 待检查 |
| C03-CHK-011 | 规则承接 | Business、Permission、Data、Security 义务均有 C04 Requirement | 待检查 |
| C03-CHK-012 | RQI 新鲜度 | Source Revision 当前且 Sync Status 为 Current | 待检查 |
| C03-CHK-013 | RQI 边界 | 未复制 Requirement Statement 或 Acceptance 正文 | 待检查 |
| C03-CHK-014 | 九类质量特性 | 全部为 Applicable 或经授权 Not Applicable | 待检查 |
| C03-CHK-015 | 质量可测量性 | Applicable 项有指标、单位、阈值、环境和数据源 | 待检查 |
| C03-CHK-016 | 质量追踪 | Applicable 项有 Requirement 和 C05 Verification Strategy | 待检查 |
| C03-CHK-017 | UX 人本输入 | 用户、任务、环境、参与和评价引用完整 | 待检查 |
| C03-CHK-018 | Dependency/Constraint | 来源、影响、条件、Owner、期限和承接完整 | 待检查 |
| C03-CHK-019 | Risk | High/Critical Risk 已处置或授权接受 | 待检查 |
| C03-CHK-020 | Open Question | Blocking 问题全部 Closed 或经授权 Cancelled | 待检查 |
| C03-CHK-021 | Acceptance Boundary | 覆盖全部 In Scope Feature、Scenario、Requirement 和质量属性 | 待检查 |
| C03-CHK-022 | Release/Observation | Target Release、约束、指标、周期和 Owner 完整 | 待检查 |
| C03-CHK-023 | 评审独立性 | Product、UX、Engineering、Quality 和 Independent Review 完成 | 待检查 |
| C03-CHK-024 | 变更控制 | Approved/Baselined 变化均进入 C11 | 待检查 |
| C03-CHK-025 | Agent 权限 | Agent 未扩大 Scope、批准 PRD、判定 N/A 或关闭 Blocking 项 | 待检查 |
| C03-CHK-026 | 标准新鲜度 | 29148 替代状态已在基线前复核 | 待检查 |

### 20.11 正反例

正例：

> Feature `FTR-0042`：目标用户可在已批准场景中保存并恢复未完成申请。该能力追踪 `USC-0042-S01`、`REQ-0181` 至 `REQ-0186`，用户价值和业务价值分别可判定。performance efficiency 的适用指标、阈值、环境和 `REQ-0186` 已登记；计费变更列入 `NGR-0042-N01`；外部身份服务依赖具有满足条件、Owner 和替代路径。

该表达具有可感知能力、Scenario、Requirement、质量属性、Non-goal 和 Dependency 追踪，可以进入评审。

反例：

> 新增草稿页，接口要快，权限要安全，必要时修改其他服务，测试通过后上线。

该表达把页面和技术动作当作 Feature，包含未编号强制需求，没有用户情境、Scope、Requirement、质量指标、阈值、环境、Dependency、Acceptance Boundary 或 Release 控制，禁止进入 PRD Ready。

### 20.12 参考的国际标准条款映射总表

| 国际标准 | 条款 | 本规范落地位置 | 采用方式 | 复核限制 |
|---|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | 4.4 信息项内容符合性 | 第 12、13、15、20 章 | 为七类 C03 产物规定内容和检查条件 | 完整符合性需合法全文逐条复核 |
| ISO/IEC/IEEE 29148:2018 | 4.5 裁剪符合性 | 第 17 章 | 固定 P2 七类产物身份和未来裁剪边界 | 不声明满足标准全部裁剪要求 |
| ISO/IEC/IEEE 29148:2018 | 5.2.3 Need 向 Requirement 转换 | 第 8、9.4、10.5、10.6 章 | Scenario、Feature 和 Goal 作为 C04 输入 | C03 不建立原子 Requirement |
| ISO/IEC/IEEE 29148:2018 | 5.2.4 Requirement 构造 | 第 5.3、10.6、14、15 章 | 禁止 PRD 未编号强制义务，要求进入 C04 | 具体语句规则由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 5.2.5 单项 Requirement 特性 | 第 10.6、13.7、14 章 | RQI 检查标识、归属、Revision 和 State | 不复制 Requirement 正文 |
| ISO/IEC/IEEE 29148:2018 | 5.2.6 Requirement Set 特性 | 第 10.4–10.6、14.2、15 章 | 检查 Feature、Scenario 和 Requirement 覆盖一致性 | 完整集合质量由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 5.2.7 Requirement 语言准则 | 第 5.3、10.6、15.2 章 | 识别模糊表达和隐藏强制义务 | 只执行 C03 边界检查 |
| ISO/IEC/IEEE 29148:2018 | 5.2.8 Requirement 属性 | 第 10.6、13.7、20.7 章 | 索引 ID、Type、Revision、State、Priority 和 Verification | 正式属性由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 5.4 Requirement 信息项 | 第 8.4、10.6、12、13 章 | PRD 引用 Requirement Set 和 RQI | 不建立平行信息项 |
| ISO/IEC/IEEE 29148:2018 | 6.2 业务或任务分析过程 | 第 9、10.1–10.3、13.2 章 | 连接 Problem、Intent、Goal、用户、价值和 Scope | 不替代 C01/C02 |
| ISO/IEC/IEEE 29148:2018 | 6.3 Stakeholder Need 和 Requirement 定义过程 | 第 10.2、10.5、10.9、13.4 章 | 记录用户、Context of Use、流程和期望结果 | Scenario 不是 Requirement |
| ISO/IEC/IEEE 29148:2018 | 6.4 System/Software Requirement 定义过程 | 第 10.4、10.6–10.8、18 章 | Feature、规则、质量和 Constraint 进入 C04 | Design 由 C06 管理 |
| ISO/IEC/IEEE 29148:2018 | 6.6 Requirements management | 第 9.7、10.6、10.14、16 章 | 管理索引、Revision、变更和 Trace | Baseline 由 C11 管理 |
| ISO/IEC/IEEE 29148:2018 | 7 信息项 | 第 8、12、13 章 | 定义七类内部正式产物 | 不复制标准信息项正文 |
| ISO/IEC/IEEE 29148:2018 | 8.1–8.5 信息项纲要 | 第 12、13、20.1–20.8 章 | 建立 PRD、Feature、Scenario、Index 和质量模板 | 不复制 BRS/StRS/SyRS/SRS 模板 |
| ISO/IEC/IEEE 29148:2018 | 9 信息项内容 | 第 13、14、15 章 | 设置内容、质量和检查条件 | 仅声明条款主题对齐 |
| ISO/IEC 25030:2019 | 5 Conformance | 第 15.4、19.3 章 | 限制符合性声明 | 不声明完整标准符合 |
| ISO/IEC 25030:2019 | 6.1–6.4 质量需求概念、类型、目标、模型和度量 | 第 6、10.8、13.8、20.8 章 | QAS 记录类别、对象、指标、阈值和环境 | 具体度量由 C05/E03 核验 |
| ISO/IEC 25030:2019 | 6.5.1 质量需求来源 | 第 10.2、10.5、10.8、13.8 章 | 来源连接 Goal、Scenario、Risk、Constraint 和 Need | 不把来源直接视为 Requirement |
| ISO/IEC 25030:2019 | 6.5.2 ICT 产品类别 | 第 3、10.8、13.8 章 | 记录质量目标适用产品和对象 | 不建立组织级产品分类 |
| ISO/IEC 25030:2019 | 6.5.3 与功能/数据需求关系 | 第 10.6–10.8、18 章 | 质量、功能和数据义务共同进入 C04 | 数据治理由 E03 管理 |
| ISO/IEC 25030:2019 | 6.5.4 质量需求派生 | 第 10.8、13.8、16.1 章 | 从业务理由和 Scenario 派生并追踪 Requirement | 正式派生由 C04 管理 |
| ISO/IEC 25030:2019 | 6.5.5 质量需求权衡 | 第 7、10.8、16.3、18 章 | 记录 Goal、Feature、Risk 和 C10 Decision | Agent 禁止最终决定权衡 |
| ISO/IEC 25030:2019 | 7.1–7.2 质量需求过程 | 第 9.4、10.8、15 章 | 规定提取、定义、评审和承接步骤 | 不替代完整工程过程 |
| ISO/IEC 25030:2019 | 7.3.1–7.3.2 Stakeholder 识别和需要定义 | 第 10.2、10.5、10.9 章 | 用户、角色、Context 和 Need 进入质量分析 | 不规定具体研究方法 |
| ISO/IEC 25030:2019 | 7.4.1–7.4.2 质量需求定义步骤 | 第 10.8、13.8、20.8 章 | 使用理由—场景—指标—阈值—环境—验证—Requirement 结构 | Requirement 由 C04 管理 |
| ISO/IEC 25030:2019 | 8.1 实施质量需求的关键成功因素 | 第 7、9.5、14、15 章 | 检查责任、可测量性、资源和承接 | 不替代实施计划 |
| ISO/IEC 25030:2019 | 8.2 质量需求追踪 | 第 8.2、10.8、16.1 章 | QAS 追踪 Feature、Scenario、Requirement 和 Verification | 统一机制由 C10 管理 |
| ISO/IEC 25030:2019 | 8.3 测试质量需求的关键因素 | 第 10.8、10.12、13.8、18 章 | 输出指标、阈值、环境和 Verification Strategy | 测试设计和执行由 C05 管理 |
| ISO/IEC 25010:2023 | 3.1–3.9 九类产品质量特性 | 第 10.8、13.8、15.3、20.8 章 | 对九类特性逐项作适用性判定 | 中文名称为内部工作译名 |
| ISO/IEC 25010:2023 | 4.1 产品质量模型结构 | 第 10.8、13.8、20.8 章 | 按特性和适用子特性组织 QAS | 不重制完整模型 |
| ISO/IEC 25010:2023 | 4.2 产品质量模型目标 | 第 10.8、13.8、14 章 | 明确 Product、Feature、Scenario 和环境 | 禁止无法验证的泛化对象 |
| ISO/IEC 25010:2023 | 5 与 Quality-in-use 模型的关系 | 第 10.2、10.8、10.9、10.13 章 | 区分产品质量、用户结果和观察 | Quality-in-use 详细模型不在 C03 |
| ISO/IEC 25010:2023 | Annex C 使用质量模型进行测量 | 第 10.8、13.8、15、20.8 章 | 记录指标、阈值、环境和验证策略 | 测量方法由 C05/E03 核验 |
| ISO 9241-210:2019 | 5.2 明确理解用户、任务和环境 | 第 10.2、10.5、10.9、13.4 章 | Scenario 记录用户、任务、资源和 Context of Use | 不以 Persona 名称替代情境 |
| ISO 9241-210:2019 | 5.3 用户贯穿设计和开发参与 | 第 7、10.2、10.9、13.4 章 | 记录参与方式、样本和反馈引用 | 不规定具体研究方法 |
| ISO 9241-210:2019 | 5.4 用户中心评价驱动和细化设计 | 第 9.4、10.9、10.12、18 章 | 评价结果追踪 Feature、Scenario 和 Requirement | 评价计划由 C05 管理 |
| ISO 9241-210:2019 | 5.5 迭代过程 | 第 9.7、10.9、16.3 章 | 允许受控迭代并保留 Revision | Baseline 变化由 C11 管理 |
| ISO 9241-210:2019 | 5.6 整体用户体验 | 第 10.5、10.9、14 章 | 覆盖主、替代、异常、恢复和结果 | 不把单一页面等同于整体体验 |
| ISO 9241-210:2019 | 5.7 多学科技能和视角 | 第 7、9.5、10.14、15.2 章 | Product、UX、Engineering、Quality 联合评审 | 组织岗位由 C07 管理 |
| ISO 9241-210:2019 | 6.2–6.5 责任、计划、整合、时间和资源 | 第 7、9、10.13、13.2 章 | 记录 Owner、评审、Target Release 和 Dependency | 不替代项目计划 |
| ISO 9241-210:2019 | 7.2 规定 Context of Use | 第 10.5、10.9、13.4、20.4 章 | User Scenario Set 管理使用情境 | UX 研究资产由适用扩展承接 |
| ISO 9241-210:2019 | 7.3 规定用户需求 | 第 10.5、10.6、18 章 | Scenario 和 Feature 形成 C04 输入 | 原子 Requirement 由 C04 管理 |
| ISO 9241-210:2019 | 7.4 产生设计方案 | 第 8.4、10.9、18 章 | PRD 引用 C06 设计，不复制正文 | C03 不批准设计 |
| ISO 9241-210:2019 | 7.5 评价设计 | 第 10.9、10.12、18 章 | 引用 C05 评价并回写追踪 | C03 不执行完整评价 |
| ISO 9241-210:2019 | 9 Conformance | 第 15.4、19.3 章 | 限制符合性声明 | 不声明完整标准符合 |
