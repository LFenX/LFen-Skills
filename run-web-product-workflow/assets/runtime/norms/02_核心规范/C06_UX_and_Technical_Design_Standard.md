# C06 UX 与技术设计规格规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C06 |
| 英文名称 | UX and Technical Design Specification |
| 正式文件名 | `C06_UX_and_Technical_Design_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3、C02 V6.3、C03 V6.3、C04 V6.3、C05 V6.3 |
| 生产前调研 | RVR-C06-0001 |
| 下游规范 | C07、C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式设计、Constraint、评审、Decision 引用、覆盖、变更、替代和基线记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定如何把已批准的 Product、Scope、PRD、Feature、Requirement、Acceptance Criterion 和 Quality Attribute 转化为可实现、可验证且与既有系统一致的 UX Design 与 Technical Design。

本规范用于实现以下控制目标：

1. 使用户、使用情境、任务、概念、流程、页面、组件和交互状态形成可追踪的 UX 设计；
2. 使系统边界、组件职责、数据与状态、接口、权限、质量属性、迁移、回滚和可观测性形成可追踪的技术设计；
3. 使 UX Design Specification 与 Technical Design Specification 分别成为唯一事实源，不互相复制；
4. 使每项关键 Requirement 映射到 Design Element 或经授权接受的 No Design Required 理由；
5. 使正常、异常、空、加载、无权限、重试和恢复行为在实现前被显式设计；
6. 使重大架构、接口、数据、权限和迁移选择引用 C10 Decision Record；
7. 防止 Coding Agent 以“技术优化”“顺手重构”或“实现需要”为由扩大 C02 Scope；
8. 使设计变化能够触发验证、上下文、执行、追踪、配置和门禁影响分析。

## 3. 适用范围

本规范适用于：

- Web App、SaaS、交互式内部工具、API、事件接口、数据产品和 Agent 能力的 UX 与技术设计；
- 新建、修改、替代或退役用户流程、页面、组件、接口、状态、权限和技术组件；
- 从 C03 PRD/Feature 与 C04 Requirement 建立设计；
- 从 C05 Acceptance Criterion 和 Verification Strategy 反查设计可验证性；
- 信息架构、用户流程、交互场景、内容提示、响应式、键盘和无障碍设计；
- 系统上下文、组件视图、数据流、控制流、接口契约、概念数据与状态模型；
- 权限、安全、可靠性、性能、容量、兼容性、可维护性和 Safety 的设计考虑；
- 异常、超时、重试、幂等、并发、顺序、一致性、降级、恢复和回滚设计；
- 人类主导、Agent 辅助和多 Agent 参与的设计生成、检查、评审和演进；
- P2 档位下十类 C06 正式产物的身份、状态、必填信息、模板和质量检查。

具体目标产品是否启用 E01 至 E05，由正式扩展适用性记录决定。扩展未激活不免除 C06 对已识别 Architecture、Security、Privacy、Compliance、Data、AI、Knowledge 或 Operations Risk 的记录义务。

## 4. 不适用范围

以下内容不由本规范定义：

- Need、Evidence、Problem、Product Definition、Intent 和 Goal 的发现规则，由 C01 管理；
- Initiative、Scope、Assumption、Constraint 和 Risk 的建立规则，由 C02 管理；
- PRD、Feature、User Scenario、Non-goal、Dependency 和 Quality Attribute Summary 的组织规则，由 C03 管理；
- Requirement Statement、Requirement Set、类型、Revision 和演进分类，由 C04 管理；
- Acceptance Criterion、Verification、Validation、Evidence、Coverage 与 Acceptance Decision，由 C05 管理；
- 人机职责、授权、审批矩阵、停止条件和升级协议的完整模型，由 C07 管理；
- Agent Context 的组装、新鲜度、最小化、隔离和泄漏控制，由 C08 管理；
- Agent Run、命令、Tool Call、代码修改、执行 Evidence 和 Validation Report，由 C09 管理；
- Decision、统一 Traceability Matrix 和 Asset Lineage，由 C10 管理；
- Configuration Item、Snapshot、Baseline、Change Request 和 Release Configuration，由 C11 管理；
- Gate Decision、Exception or Waiver、Risk Acceptance 和 Product Health，由 C12 管理；
- E01 激活后的完整 Architecture Description、Architecture Viewpoint Catalog 和 Architecture Conformance Review；
- E02 激活后的威胁模型、隐私影响评估和安全验证计划；
- 物理数据库 Schema、DDL、迁移脚本、源代码结构、CI/CD 配置、云资源配置或工具产品选型；
- 法律意见、监管解释、外部认证或国际标准符合性声明。

C06 可以引用上述对象，但禁止建立同名平行资产、复制正文形成第二事实源，或以 Design Review 替代 Acceptance、Gate、Risk Acceptance、Change Approval 或 Architecture Approval。

## 5. 规范性用语

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性示例，不作为符合性判定依据。

### 5.2 设计判定关键词

`Design Ready`、`Not Ready` 和 `Blocked` 是 Design Readiness Conclusion，不是资产 State。

`Pass`、`Fail` 和 `Blocked` 是 Review Outcome，不是资产 State。

`Not Covered`、`UX Covered`、`Technical Covered`、`Both Covered`、`No Design Required`、`Stale` 和 `Blocked` 是 Design Coverage Status，不是资产 State。

`Initial`、`Empty`、`Loading`、`Success`、`Partial`、`Error`、`No Permission`、`Retrying` 和 `Recovering` 是交互或系统状态类型，不是 DOC 或 CASE State。

### 5.3 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 已批准 Exception、Waiver 或 Risk Acceptance 的明确范围；
3. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
4. 本规范已批准或已基线版本；
5. 当前 Product、Initiative、Scope、PRD、Feature 和 Requirement 的有效 Baseline；
6. C05、C07、C10、C11、C12 及已激活扩展的当前有效 Baseline；
7. R2 无障碍参考与 R3 表达实践。

无法判定冲突时，必须停止 Design Ready、实现授权和 Agent 下游执行，并提交人类决策。

### 5.4 可判定表达

设计规则必须通过 Asset ID、Revision、Design Element ID、字段、受控枚举、图例、边界、方向、输入、输出、状态、阈值、时间、容量、Trace Link、Decision 或批准记录直接判定。

禁止使用没有判定条件的“用户友好”“现代化”“性能良好”“安全可靠”“兼容现有系统”“必要时重试”“响应式适配”“符合最佳实践”“架构合理”“可扩展”和“易维护”。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| Design | 针对已批准问题与 Requirement，规定可实现结构、行为、交互和约束的受控结果 | 不等同实现、原型或 Decision |
| UX Design Specification | 规定用户、Context、任务、流程、页面、组件、交互状态、内容、权限差异、响应式和无障碍行为的正式产物 | 使用 UXD 身份和 DOC 状态 |
| Technical Design Specification | 规定系统边界、组件、数据、状态、接口、权限、质量属性、迁移、回滚、可观测性和测试策略的正式产物 | 使用 TDS 身份和 DOC 状态 |
| Design Element | UXD、UFS、PCI、TDS、SCV、IFC、DSM 或 PEM 内可独立追踪的设计成员 | 是容器内稳定成员，不是新增正式产物类型 |
| UX Element | 描述用户可感知或可操作行为的 Design Element | 必须位于 UXD/UFS/PCI 中 |
| Technical Design Element | 描述系统结构、行为或约束的 Design Element | 必须位于 TDS/SCV/IFC/DSM/PEM 中 |
| Design ID | UXD 或 TDS 的永久 Asset ID，或其受控 Design Element ID | 禁止包含版本、状态、日期或 Owner |
| User Flow | 用户为达成目标经过的入口、步骤、分支、系统响应和退出路径 | 不是页面跳转图的同义词 |
| Interaction State | 用户可感知的系统当前状况、可用动作和反馈 | 与资产 State、业务状态分开 |
| System State | 影响业务或技术行为的受控状态及其转换 | 必须记录进入、退出、守卫和失败行为 |
| Information Architecture | 内容、功能、对象和导航的组织及命名体系 | 不等同组件树或数据库结构 |
| Page | 具有独立路由、视图边界或任务上下文的用户界面单元 | 单页应用也可以有多个 Page 身份 |
| Component | 在明确职责、输入、输出、状态和复用边界内工作的可组合设计单元 | UX Component 与技术组件必须标明类型 |
| System Boundary | 明确系统内外责任、信任、数据和控制交界的设计边界 | 禁止使用无范围的“后端”“平台” |
| Affected Boundary | 当前设计允许改变的组件、接口、数据、状态、配置和行为集合 | 必须受 C02 Scope 约束 |
| Unaffected Boundary | 当前设计明确承诺不改变的对象、接口、行为和质量边界 | 不得因实现便利隐式突破 |
| External Entity | 位于 System Boundary 外并与系统交换信息、控制或服务的主体 | 必须记录责任方和交互方向 |
| Concern | Stakeholder 对系统的特定兴趣、风险、目标或问题 | SCV 必须指向明确 Concern |
| Viewpoint | 规定构造、解释和评审某类 View 的约定 | 不是图名或工具名 |
| View | 按 Viewpoint 表达系统某组 Concern 的工作产品 | 不存在覆盖所有 Concern 的通用 View |
| Model | 在明确语义和抽象层级下表达系统部分特征的结构化表示 | 必须记录图例或语义 |
| API or Interface Contract | 提供方与使用方之间对操作/事件、输入、输出、错误、权限、兼容、性能和变更的受控约定 | 使用 IFC 身份；不等同实现代码 |
| Data and State Model | 业务实体、概念数据、状态、关系、约束、转换和一致性的受控模型 | 本蓝图阶段禁止物理 Schema |
| Permission Model | 主体在条件下对资源执行动作的授权、拒绝、审计和撤销模型 | 必须默认拒绝 |
| Design Constraint | 限制可行设计空间且有明确来源、影响和解除条件的事实 | 使用 DCT；不等同 Requirement 或 Decision |
| Design Coverage Matrix | 连接 Requirement、UX Element、Technical Design Element、No Design Required 理由、Revision 和 Gap 的正式矩阵 | 跨规范引用时写作 C06 Design Coverage Matrix |
| No Design Required | 经分析确认特定 Requirement 不需要新增或修改 UX/技术设计的覆盖结论 | 必须有理由、影响、Reviewer 和批准 |
| Design Ready | 当前范围、Revision 和适用扩展的设计前置条件全部满足的门禁建议 | 不是 State，不授权实现，不替代 C12 Gate Decision |
| Prototype | 用于探索、沟通或评价设计假设的可交互或静态表现 | 不是 UXD/TDS 的唯一事实源 |

`Context of Use` 的唯一语义直接适用 C01；当 Architecture Surface 适用时，`Architecture` 和 `Architecture Description` 的唯一语义直接适用 E01，C06 只管理其设计消费关系，不建立平行定义。

未在本章定义的公共术语以 VC-PPG-COM-001 为准。

## 7. 角色与职责

| 角色 | 强制职责 | 禁止事项 |
|---|---|---|
| Design Owner | 维护 C06 设计范围、十类产物一致性、Revision 和 Readiness | 不得批准自己生成且未独立复核的高风险设计 |
| UX Design Owner | 维护用户、Context、概念、流程、页面、组件、状态、内容和无障碍设计 | 不得改变 Requirement 或以视觉稿替代 UXD |
| Technical Design Owner | 维护系统边界、组件、数据、接口、权限、质量属性、迁移和回滚设计 | 不得把范围外重构写成实现细节 |
| Requirement Owner | 确认设计没有改变 Requirement 含义并处理 Requirement Gap | 不得因设计困难降低 Requirement |
| Product Owner | 确认用户结果、Feature、Non-goal 和 Scope 一致性 | 不得用口头意见无痕改 Scope |
| Accessibility Reviewer | 评审适用 WCAG A/AA 的设计支持、键盘、焦点、语义和完整过程 | 不得以自动扫描替代人工设计评审 |
| Interface Owner | 确认提供方/使用方、契约、兼容、错误、幂等、性能和变更规则 | 不得单方修改共享接口 |
| Data or State Owner | 确认实体、语义、状态、关系、一致性、保留与所有权 | 不得在 DSM 中引入未批准物理 Schema |
| Permission or Security Reviewer | 确认默认拒绝、授权来源、职责分离、审计、撤销和安全边界 | 不得把 UI 隐藏视为授权控制 |
| Operations or Reliability Reviewer | 评审容量、故障、恢复、可观测性、迁移和回滚 | 不得以“上线后观察”替代设计 |
| Verification Lead | 确认 Design Element 可被 C05 Criterion、Method 和 Evidence 验证 | 不得把 Design Review 写成最终 Acceptance |
| Architecture Authority | 识别 Architecturally Significant Decision 和 E01 触发条件 | 不得在无 C10 Decision 时口头批准重大变化 |
| Decision Owner | 在 C10 中维护候选、选择、理由、后果和替代关系 | 不得用 TDS 段落替代 Decision Record |
| Independent Reviewer | 按 Scope、Requirement、质量、风险和标准映射复核设计 | 不得同时是唯一作者和唯一批准人 |
| Coding Agent | 生成 Draft、候选 Design Element、矩阵、检查结果和影响分析 | 不得扩大 Scope、决定架构、批准设计、创建物理 Schema 或隐式重构 |

同一人可以承担多个非冲突角色，但关键或高风险设计的 Author、唯一 Reviewer 和 Approval Authority 禁止为同一主体。具体职责分离、工具授权、停止和升级规则由 C07 管理。

## 8. 管理对象与关系

### 8.1 正式产物

本规范管理十类正式产物：

1. UX Design Specification（UXD）；
2. User Flow and State Model（UFS）；
3. Page and Component Inventory（PCI）；
4. Technical Design Specification（TDS）；
5. System Context or Component View（SCV）；
6. API or Interface Contract（IFC）；
7. Data and State Model（DSM）；
8. Permission Model（PEM）；
9. Design Coverage Matrix（DCM）；
10. Design Constraint Record（DCT）。

十类产物可以在同一工具或页面展示，但必须分别保留 Asset ID、Artifact Type、Owner、State、Current Revision、Trace Links、Access Classification、Retention Rule 和 History Reference。

### 8.2 Design Element 身份

Design Element 使用以下概念格式：

```text
<容器 Asset ID>#<成员类型>-<顺序号>
```

示例：

```text
UXD-0042#UXE-007
UFS-0018#FLOW-003
PCI-0021#PAGE-004
TDS-0031#TDE-012
IFC-0015#OP-006
DSM-0009#STATE-003
```

规则：

1. 成员 ID 在容器 Asset 内永久唯一且不得复用。
2. 内容修订保持成员 ID；独立义务变化时创建新成员并记录 `replaces` 或 `supersedes`。
3. 删除成员必须保留历史、原因、影响和替代关系。
4. 成员 ID 不得包含 Revision、State、Owner 或日期。
5. DCM 必须引用精确成员 ID，不得只写“见 UXD”或“见技术方案”。

### 8.3 View 与 Model 最低元数据

每个 SCV 或嵌入式 View 必须记录：

| 元数据 | 最低要求 |
|---|---|
| View ID and Name | 永久成员 ID 与可识别名称 |
| Purpose | View 要支持的设计或评审用途 |
| Stakeholders | 使用或评审该 View 的角色 |
| Concerns | View 明确回答的问题或风险 |
| Viewpoint | 构造规则、元素类型、关系类型和解释方式 |
| System of Interest | 目标系统及适用边界 |
| Elements and Relations | 组件、外部实体、数据/控制流和方向 |
| Legend | 符号、线型、颜色和缩写语义 |
| Applicable Revision | Product/Design/Configuration 版本 |
| Correspondence | 与其他 View、Model、Requirement 或 Decision 的一致性关系 |
| Known Limitations | 未表达的 Concern、层级和假设 |

### 8.4 最低关系链

```text
UX Design Specification
  ├─ contains → UX Element
  ├─ depends-on → PRD / Feature / Requirement
  └─ depends-on → User Flow and State Model / Page and Component Inventory

Technical Design Specification
  ├─ contains → Technical Design Element
  ├─ depends-on → Requirement
  └─ depends-on → SCV / IFC / DSM / PEM / Decision Record

Requirement
  └─ designed-by → UX Element / Technical Design Element

Design Constraint Record
  └─ constrains → UXD / TDS / Design Element

Design Coverage Matrix
  ├─ depends-on → Requirement Set
  └─ generated-by → Review Record

Design Element
  ├─ verified-by → Verification Evidence Record
  └─ affected-by → Change Request / Risk / Constraint
```

只能使用 VC-PPG-COM-001 规定的受控关系。禁止使用 `related-to`、`see-also` 或无方向“关联”作为正式 Trace Link。

### 8.5 事实源边界

| 事实 | 唯一规范责任方 | C06 处理方式 |
|---|---|---|
| Need、Problem、Intent、Goal | C01 | 引用，不改写 |
| Initiative、Scope、Constraint、Risk | C02 | 引用并校验设计边界 |
| PRD、Feature、Scenario、Non-goal、Quality Attribute Summary | C03 | 作为设计组织与优先级输入 |
| Requirement、Revision、演进类型 | C04 | 作为设计义务输入 |
| Criterion、Verification/Validation、Evidence、Acceptance | C05 | 作为可验证性输入和下游消费方 |
| UX 与技术设计 | C06 | 建立并维护十类产物 |
| Role、Approval、Stop、Escalation | C07 | 引用授权边界 |
| Agent Context | C08 | 提供受控设计 Revision |
| Agent Run、代码与执行记录 | C09 | 提供实现约束和变更影响 |
| Decision、Traceability、Lineage | C10 | 引用，不在 TDS 建立平行 Decision |
| Version、Baseline、Change | C11 | 引用，不把 Design Revision 当 Baseline |
| Gate、Waiver、Risk Acceptance、Health | C12 | 提供 Readiness Evidence，不自行批准 |

原型、白板、截图、图表、OpenAPI 文件或代码可以作为外部 Reference，但必须有 Source System、Object ID、Version、Owner、访问路径和当前有效性；禁止只使用易失链接。

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
Design Intake
  → Eligibility Check
  → Input Revision Freeze
  → UX and Technical Design
  → Cross-Design Reconciliation
  → Coverage and Quality Review
  → Design Readiness Assessment
  → Human Approval
  → C11 Baseline
  → Implementation Consumption
  → Change Impact / Supersession / Retirement
```

### 9.2 Eligibility Check

开始正式设计前必须记录：

1. Product、Initiative、Scope、PRD、Feature、Requirement Set 和 Acceptance Criteria 的 ID 与 Revision；
2. 当前 P 档位和 E01 至 E05 适用性记录；
3. 目标系统、环境、用户、业务边界和已有 Configuration/Baseline；
4. 输入资产的 State、新鲜度、冲突、缺失和未批准项；
5. Design Owner、UX Owner、Technical Design Owner、Reviewer 和 Approval Authority；
6. 已知 Constraint、Risk、Dependency、Decision 和 Non-goal；
7. 本次允许改变与禁止改变的边界。

Draft 设计可以使用已明确 Revision 的 Draft 上游输入，但 Design Ready 必须以当前有效且按治理要求 Approved 或 Baselined 的上游资产为依据。使用未批准输入时必须标记 `Provisional Input` 和失效触发条件。

### 9.3 Input Revision Freeze

1. 每次设计周期必须固定输入 Asset ID、Revision、Snapshot 和时间。
2. 设计期间上游变化不得无痕并入；必须先执行 Impact Analysis。
3. 未接受的新输入必须保持隔离，禁止污染当前评审 Revision。
4. 输入冲突必须记录冲突对象、权威顺序、阻断范围和责任人。
5. C02 Scope 不明确时禁止通过设计假设扩大范围。

### 9.4 UX 与技术设计并行

UXD 与 TDS 可以并行编制，但必须在以下接口点同步：

- 用户动作与系统能力；
- Interaction State 与 System State；
- Page/Component 输入输出与 Interface Contract；
- Permission Difference 与 PEM；
- 错误/恢复文案与技术错误/恢复机制；
- 响应式/无障碍行为与技术实现约束；
- 性能体验目标与性能/容量设计；
- 可取消、重试、撤销、回滚与一致性机制；
- Prototype Revision 与 Design Revision。

同步采用精确 Design Element Trace，不得复制另一产物的事实正文。

### 9.5 Review 与 Design Readiness

1. 单项产物先执行 Owner 自检，再执行跨产物一致性评审。
2. UX、技术、Requirement、Verification、Accessibility、Security/Permission 和 Operations Reviewer 按适用性参与。
3. Finding 必须有 ID、严重性来源、对象、Revision、证据、责任人、期限和关闭条件。
4. Design Ready 只能作为 Readiness Assessment 结论提交有权人类。
5. Approved 后由 C11 决定是否进入 Baseline；Approved 不等于 Baselined。

### 9.6 变化与失效

以下变化必须触发 C06 Impact Analysis：

- Scope、PRD、Feature、Requirement、Criterion 或 Quality Attribute Revision；
- 用户、Context of Use、目标任务、支持设备或输入方式变化；
- 组件、接口、数据、状态、权限、依赖或信任边界变化；
- 容量、性能、安全、可靠性、兼容或运营约束变化；
- Decision 被 Approved、Rejected、Superseded 或 Expired；
- Prototype、实现、配置或外部依赖与 Design 不一致；
- E01 至 E05 适用性状态变化。

Impact Analysis 必须确定受影响 Design Element、DCM 行、C05 Evidence、C08 Context、C09 Run、C10 Trace、C11 Baseline 和 C12 Gate/Health。先前 Evidence 是否失效由 C05 判定。

## 10. 强制规则

### 10.1 身份、Revision 与范围

1. UXD 与 TDS 必须使用不同 Asset ID、Owner、State 和 Revision。
2. 同一设计对象的内容变化使用 Revision；独立设计义务或独立生命周期使用新 Asset ID。
3. 每个设计必须记录 Applicable Scope、Affected Boundary 和 Unaffected Boundary。
4. Design ID 禁止因重命名、迁移工具或 Owner 变化而改变。
5. P2 禁止使用 Design Brief 替代十类产物。
6. 共享页面、组件、接口或模型必须记录复用边界和使用方，不得以复制建立分叉事实。

### 10.2 设计输入与追踪

1. 每个 Design Element 必须至少追踪一个 PRD、Feature、Requirement、Constraint、Decision 或 Risk 来源。
2. 每个当前有效关键 Requirement 必须在 DCM 中出现且有覆盖结论。
3. Design 禁止改变 Requirement 的主体、触发、行为、对象、条件、量值、时限或例外。
4. 发现 Requirement 模糊、冲突、不可实现或不可验证时，必须创建 Gap 并返回 C04/C05，不得在设计中静默解释。
5. Non-goal 与 Unaffected Boundary 必须转化为明确设计禁止项。
6. Provisional Input 必须记录 Owner、到期条件和替换规则。

### 10.3 用户、Context、任务与概念设计

UXD 必须记录：

1. 目标用户角色、能力、经验、限制和授权差异；
2. 用户目标、任务、频率、重要性和失败后果；
3. 技术、物理、社会、文化与组织 Context；
4. 用户可理解的业务对象、动作、关系、术语和反馈；
5. 当前方式、目标方式和不改变方式；
6. 用户参与、研究、评价或已批准证据的引用；
7. 已知排除用户、未覆盖 Context 和剩余 Risk。

禁止直接将内部服务名、数据库字段、队列、异常码或技术状态作为用户概念，除非 Requirement 明确要求且 UX Review 接受。

### 10.4 信息架构与 User Flow

1. 信息架构必须记录内容/功能分组、命名、层级、导航入口、返回路径和跨区域一致性。
2. 每个核心任务必须有端到端 User Flow，不得只列页面。
3. UFS 必须包含用户角色、入口、前置条件、步骤、决策分支、系统响应、退出和 Requirement Trace。
4. Flow 分支必须显示允许、拒绝、错误、取消、超时、重试和恢复中的适用项。
5. 多设备、多角色或多权限产生不同行为时，必须建立差异规则。
6. 跨系统跳转必须记录责任边界、上下文传递、返回和失败行为。
7. 无出口、无返回、循环依赖或无法恢复的 Flow 必须作为 Finding。

### 10.5 Page 与 Component

PCI 中每个 Page/Component 必须记录：

- ID、名称、类型和责任；
- 所属 Flow 与调用/包含关系；
- 输入、输出、事件和依赖；
- Interaction State 与 System State 映射；
- 可执行动作、前置条件和后果；
- Permission、可见性与可操作性；
- 内容和反馈来源；
- 响应式与无障碍规则；
- 复用、扩展和禁止复用边界；
- Requirement、UXD/TDS Revision 和验证引用。

组件复用只有在语义、行为、状态、权限和无障碍要求一致时成立。仅外观相同不得作为复用依据。

### 10.6 状态、异常与恢复

1. 每个远程、异步、长耗时或可失败动作必须判定 `Initial`、`Empty`、`Loading`、`Success`、`Partial`、`Error`、`No Permission`、`Retrying` 和 `Recovering` 的适用性。
2. 每个适用状态必须记录触发、用户可见反馈、允许动作、禁止动作、退出、超时和遥测。
3. Error State 必须区分用户可修复、系统可重试、需要升级和不可恢复情形。
4. Retry 必须记录触发、最大范围、退避或等待语义、幂等前提、重复副作用和停止条件。
5. Recovery 必须记录恢复点、数据状态、用户确认、后续动作和 Evidence。
6. No Permission 必须区分未认证、已认证但未授权、授权失效和资源不可见；不得泄露资源存在性。
7. Empty 必须区分无数据、筛选无结果、尚未创建、加载失败和权限过滤。
8. 状态转换必须有源、目标、事件、守卫、动作、失败和不可达状态检查。

### 10.7 内容、响应式、键盘与无障碍

1. 内容规则必须规定术语来源、语气、标签、帮助、确认、警告、错误和恢复提示。
2. 错误提示必须说明发生了什么、用户能做什么和如何恢复；禁止暴露密钥、内部堆栈、敏感标识或未授权资源。
3. 响应式设计必须记录目标视口/设备类别、输入方式、布局重排、内容优先级、隐藏/替代规则和组件状态保持。
4. 禁止在无产品输入时虚构统一像素断点；断点必须引用 Design Token、目标设备数据或 Approved Decision。
5. 所有核心流程必须具有完整键盘路径、可见焦点、可预测焦点顺序和模态焦点管理。
6. 不得以颜色、位置、动画、声音或形状作为唯一状态表达。
7. 自定义组件必须记录 Name、Role、Value、State、键盘交互和 Status Message 设计。
8. Web 核心流程默认目标为 WCAG 2.2 Level AA，并覆盖完整页面、完整过程和响应式变体。
9. C06 只能声明设计支持目标；WCAG 符合性必须由 C05 Evidence 和授权声明流程证明。

### 10.8 System Boundary、Component 与 View

1. SCV 必须固定 System of Interest、Affected Boundary、Unaffected Boundary、外部实体和信任边界。
2. 每个 Component 必须记录责任、Owner、输入、输出、依赖、状态和失败边界。
3. 数据流与控制流必须使用不同关系或明确图例，且记录方向、同步/异步和敏感等级引用。
4. View 必须由 Stakeholder Concern 和 Viewpoint 驱动，不得以“架构总图”作为无边界替代。
5. View 之间的冲突必须通过 Correspondence、Finding 或 Decision 处理。
6. C06 SCV 不自动构成 ISO/IEC/IEEE 42010 Architecture Description。
7. 出现多服务、多仓库、关键容量、复杂部署、架构迁移或其他 E01 触发条件时，必须重新判定 E01。

### 10.9 Technical Design Specification

TDS 必须对每项适用内容给出设计或明确 Not Applicable 理由：

1. Design ID 与 Requirement Trace；
2. 系统边界和受影响/不受影响组件；
3. 数据流、控制流、状态与一致性；
4. Interface 与外部 Dependency；
5. 业务/概念数据模型；
6. Permission、Security 和 Trust Boundary；
7. 异常、超时、重试、幂等、并发、顺序和补偿；
8. Performance、Capacity 和资源边界；
9. Reliability、Availability、Recovery 和降级；
10. Compatibility、Versioning、Migration 和 Rollback；
11. Observability：日志、指标、Trace、事件、告警和关联 ID；
12. Maintainability、Flexibility 和 Safety；
13. Test Strategy 与验证接口；
14. Alternative、Decision、Constraint 和 Risk；
15. Known Limitation、开放 Finding 和剩余 Risk。

TDS 禁止规定超出 Scope 的重构、替换技术栈、共享接口破坏性变化、数据迁移或权限提升。

### 10.10 API or Interface Contract

每个 IFC 必须记录：

- Provider、Consumer、Owner 和适用环境；
- Operation、Command、Query、Callback 或 Event 类型；
- 输入、输出、字段语义、必填/可选、单位和边界；
- Error 类别、错误语义、可重试性和用户影响；
- Authentication、Authorization、最小权限和审计；
- Idempotency Key、去重范围、副作用和有效期；
- 顺序、并发、交付语义、超时和重试；
- Compatibility、Version、Deprecation 和 Breaking Change 规则；
- Performance、Capacity、Rate/Quota 和资源限制；
- 变更通知、迁移、回滚和双写/双读适用性；
- Verification Method、Test/Check Reference 和 Observability；
- Requirement、TDS、Decision、Risk 和 Dependency Trace。

接口的自然语言摘要、机器可读定义和实现必须指向同一 Contract Revision。冲突时禁止自行选择，必须提交 Interface Owner。

### 10.11 Data and State Model

1. DSM 必须记录业务实体/状态、语义、关系、约束、转换、一致性、Owner、保留和 Requirement。
2. 必须区分 Business State、Interaction State、Technical State 和 Asset State。
3. 状态转换必须记录触发者、事件、守卫、动作、幂等、失败、补偿和审计。
4. 一致性必须记录范围、强度、时间窗口、冲突处理和用户可见行为。
5. 数据生命周期必须记录创建、读取、修改、归档、保留和删除的责任引用。
6. 本蓝图阶段禁止在 DSM 规定表名、列名、索引、分区、存储引擎或物理 DDL。
7. 实现阶段的物理 Schema 必须作为受控实现/配置资产引用 DSM 与 Decision，不得反向覆盖概念语义。

### 10.12 Permission Model

PEM 必须使用：

```text
Subject + Resource + Action + Condition → Permit or Deny
Default → Deny
```

并记录：

1. Subject 类型、身份来源和生命周期；
2. Resource 类型、Owner 和敏感等级引用；
3. Action、条件、范围和环境；
4. 授权来源、决策点、执行点和缓存；
5. 明确 Deny、默认 Deny 和冲突优先级；
6. 职责分离和自审批禁止；
7. 审计事件、关联 ID、保留和访问；
8. 临时授权、例外、到期、撤销和传播时间；
9. UI 可见/可操作差异与服务端授权的一致性；
10. 正向、反向、越权、撤销和多租户隔离验证。

UI 隐藏、前端路由或客户端校验禁止作为唯一 Authorization Control。

### 10.13 产品质量与非功能设计

TDS 必须对 ISO/IEC 25010:2023 九类产品质量逐类记录 `Applicable`、`Not Applicable` 或 `Not Assessed`：

| 特性 | 最低设计问题 |
|---|---|
| functional suitability | 功能完整性、正确性和任务适合性如何由 Design 支持 |
| performance efficiency | 响应、吞吐、资源、并发和容量边界是什么 |
| compatibility | 共存、互操作、版本和依赖兼容如何保持 |
| interaction capability | 可识别、可学习、可操作、错误防护、参与和无障碍如何支持 |
| reliability | 可用、容错、恢复和数据完整性如何设计 |
| security | Confidentiality、Integrity、Authenticity、Accountability 和访问控制如何支持 |
| maintainability | 模块边界、分析、修改、测试和复用如何受控 |
| flexibility | 适配、可伸缩、可安装和可替换边界是什么 |
| safety | 危害、失效安全、警告、保护和安全恢复如何处理 |

适用项必须追踪 Quality Requirement、Measure、Criterion 和 Verification Strategy。`Not Assessed` 阻断 Design Ready；`Not Applicable` 必须有 Reviewer 和理由。

### 10.14 Compatibility、Migration 与 Rollback

1. 兼容性必须覆盖适用的 API、Event、Data、UI、配置、客户端、浏览器、辅助技术和外部 Dependency。
2. Breaking Change 必须有 C10 Decision、C11 Change Request、Consumer 影响和迁移计划。
3. Migration 必须记录来源/目标 Revision、前置检查、步骤、批次、数据验证、停机/共存、Owner 和完成条件。
4. Rollback 必须记录触发、决策人、可回滚窗口、步骤、数据处理、接口兼容、观察和成功条件。
5. 不可回滚变化必须在实施前有明确 Decision、Risk、补偿与人工批准。
6. “数据库可恢复”“重新部署即可”“保留旧版本”不是充分 Rollback 设计。

### 10.15 Alternative、Constraint 与 Decision

以下任一条件成立时必须建立或引用 C10 Decision Record：

- 跨 System Boundary、共享组件或多 Consumer；
- 改变 Architecture、技术栈、接口、数据语义、权限模型或信任边界；
- 具有不可逆迁移、重大兼容影响或高恢复成本；
- 对多个 Requirement 或质量属性形成长期权衡；
- 方案之间存在真实选择且后续需要解释理由；
- E01 或其他扩展规定需要正式 Decision。

DCT 必须记录 Constraint 的原文、来源、适用范围、影响、方案限制、解除条件、Owner、Decision 和 Risk。设计作者禁止把个人偏好、当前工具习惯或未验证假设登记为既定 Constraint。

### 10.16 Design Coverage

1. DCM 的分母是当前 Scope 内、当前 Revision 的所有有效 Requirement。
2. 每行必须记录 Requirement ID/Revision、Criticality 引用、UX Element、Technical Design Element、No Design Required 理由、Design Revision、Review Status、Coverage Status、Gap Owner 和期限。
3. 关键 Requirement 必须达到 `UX Covered`、`Technical Covered`、`Both Covered` 或已批准 `No Design Required`。
4. 非关键 Requirement 也禁止从矩阵省略。
5. 设计变化、Requirement Revision、Decision 变化或 Element 被替代时，相关行必须标记 `Stale` 直至复核。
6. `No Design Required` 必须说明现有 Design 如何已覆盖或为何确实没有设计影响，并记录批准人。
7. Coverage 百分比不得掩盖 Blocked、Stale 或关键 Gap；报告必须同时列绝对数量。

### 10.17 Coding Agent 规则

Coding Agent 可以：

- 解析受控输入并生成 Draft；
- 生成候选 User Flow、Design Element、View、Contract、Model 和 Matrix；
- 对状态覆盖、字段完整性、Trace、范围和术语执行检查；
- 提出 Alternative、Finding、Gap 和 Impact Analysis；
- 在授权范围内更新已指定 Design Revision。

Coding Agent 禁止：

- 将未批准聊天、推断或代码现状升级为 Requirement；
- 创建 Scope 外页面、能力、接口、数据、权限或重构；
- 以实现方便为由改变用户行为或 Acceptance；
- 选择重大 Architecture/Technology/Data/Permission 方案；
- 批准 Design、Decision、Waiver、Risk Acceptance 或 Gate；
- 以自身生成的模拟结果声明用户 Validation 或 WCAG 符合；
- 无痕覆盖旧 Revision、Finding、Rejected 方案或失败记录。

输入冲突、授权不足、需要新 Decision、涉及不可逆变化或将突破 Unaffected Boundary 时，Agent 必须停止并升级。

### 10.18 设计演进

1. Approved Design 的内容变化必须产生新 Revision；Baselined Design 必须通过 C11 Change Request。
2. Design Element 的修订、替代、拆分、合并和退役必须保留血缘。
3. 新 Revision 必须重算 DCM，复核 C05 Evidence 新鲜度并更新 C08 Context。
4. 实现偏离 Design 时必须登记 Defect、Engineering Change 或 Requirement/Design Change，不得反向无痕修改 Design。
5. 旧 Design 只能进入 Superseded 或 Retired，禁止删除历史。

## 11. 受控状态

### 11.1 DOC 状态：UXD、UFS、PCI、TDS、SCV、IFC、DSM、PEM、DCM

| State | 进入条件 | 允许后续 |
|---|---|---|
| Draft | 已建立 ID、Owner、Source、Scope 和输入 Revision | In Review、Rejected |
| In Review | 必填信息完整、DCM 已建立且 Reviewer 已指定 | Changes Required、Approved、Rejected |
| Changes Required | 存在需整改 Finding | Draft、In Review、Rejected |
| Approved | 授权人批准当前 Revision | Baselined、In Review、Superseded、Retired |
| Baselined | 已纳入 C11 Baseline 并固定 Revision/Snapshot | 通过 Change Request 产生新修订、Superseded、Retired |
| Rejected | 当前候选不获接受 | 保留历史 |
| Superseded | 已由新资产或新修订替代 | 仅历史查询 |
| Retired | 无替代且不再适用 | 仅历史查询 |

### 11.2 CASE 状态：DCT

| State | 进入条件 | 允许后续 |
|---|---|---|
| Open | Constraint 已登记且需要处理或持续监控 | In Progress、Blocked、Cancelled |
| In Progress | Owner 正在分析影响、方案限制或解除条件 | Resolved、Blocked、Cancelled |
| Blocked | 因明确依赖、Decision 或外部条件无法继续 | In Progress、Cancelled |
| Resolved | 已形成约束处理、接受或解除结果，等待复核 | Closed、Reopened |
| Closed | 结果已复核且无需继续处理 | Reopened |
| Reopened | 新事实证明 Constraint 仍有效或处理失效 | In Progress、Blocked |
| Cancelled | 经授权确认记录无效或停止处理 | 保留原因和历史 |

### 11.3 非 State 受控值

| 字段 | 允许值 |
|---|---|
| Design Readiness Conclusion | Design Ready、Not Ready、Blocked |
| Design Review Status | Not Started、Scheduled、In Review、Findings Open、Review Complete |
| Review Outcome | Pass、Fail、Blocked |
| Design Coverage Status | Not Covered、UX Covered、Technical Covered、Both Covered、No Design Required、Stale、Blocked |
| Applicability | Applicable、Not Applicable、Not Assessed |
| Interaction State Type | Initial、Empty、Loading、Success、Partial、Error、No Permission、Retrying、Recovering |
| Change Compatibility | Backward Compatible、Forward Compatible、Breaking、Not Applicable、Not Assessed |

每次 State 变化必须记录原状态、新状态、对象 Revision、执行者、时间、依据和批准。Approved 与 Baselined 必须由授权人类决定。Design Ready、Pass、Coverage Status 或 `Review Complete` 禁止写入 State 字段。

## 12. 必需产物

| 类型代码 | 正式产物 | 状态模型 | 最低用途 |
|---|---|---|---|
| UXD | UX Design Specification | DOC | 管理用户、Context、任务、流程、页面、状态、内容、响应式和无障碍设计 |
| UFS | User Flow and State Model | DOC | 管理角色、入口、步骤、分支、系统响应、异常和恢复 |
| PCI | Page and Component Inventory | DOC | 管理页面/组件责任、输入输出、状态、权限和复用边界 |
| TDS | Technical Design Specification | DOC | 管理边界、组件、数据、接口、权限、质量、迁移、可观测和测试策略 |
| SCV | System Context or Component View | DOC | 按 Concern/Viewpoint 表达系统边界、组件、外部实体和关系 |
| IFC | API or Interface Contract | DOC | 管理 Provider/Consumer 的操作/事件、输入输出、错误、兼容和验证 |
| DSM | Data and State Model | DOC | 管理业务实体、概念数据、状态、转换和一致性 |
| PEM | Permission Model | DOC | 管理 Subject、Resource、Action、Condition、Deny、Audit 和 Revocation |
| DCM | Design Coverage Matrix | DOC | 管理 Requirement 至 UX/技术 Design Element 的覆盖与 Gap |
| DCT | Design Constraint Record | CASE | 管理设计 Constraint 的来源、影响、限制、解除、Decision 和 Risk |

禁止新增“Design Brief”“Architecture Diagram”“Flow Document”“API Spec”“Data Model”或“Permission Table”作为平行正式产物。上述呈现必须归入十类产物之一。

## 13. 产物必填信息

### 13.1 通用必填信息

十类产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。模板出现同名公共字段时只表示必须显示或引用该值，不得删除、改名、改变语义或形成第二定义。

### 13.2 UX Design Specification

| 信息 | 最低要求 |
|---|---|
| Design ID | UXD Asset ID 与当前 Revision |
| PRD/Feature/Requirement | 精确 ID、Revision 和 Trace |
| Users and Context | 用户、目标、任务、资源、环境和限制 |
| Primary and Exception Flows | 主流程、异常、取消、超时、无权限和恢复引用 |
| Pages and Components | PCI Page/Component ID |
| Interaction States | 状态、触发、反馈、动作、退出和恢复 |
| Content Rules | 术语、标签、帮助、确认、警告、错误和敏感信息规则 |
| Permission Differences | 角色/权限导致的可见、可操作和反馈差异 |
| Responsive Rules | 目标设备/视口、输入、重排、优先级和状态保持 |
| Accessibility | WCAG 目标、键盘、焦点、语义、替代和完整过程 |
| Design Revision | 版本、输入 Snapshot 和 History |
| Design Review Status | 受控值、Reviewer、Finding 和 Outcome |
| Prototype or Design Reference | Source、Object ID、Version、Owner、URL/路径和有效性 |

### 13.3 User Flow and State Model

| 信息 | 最低要求 |
|---|---|
| User Role | 角色、授权和 Context |
| Entry | 入口、前置条件和来源 |
| Steps | 用户动作、系统响应和顺序 |
| Decision Branches | 条件、允许/拒绝路径和默认路径 |
| System States | State ID、触发、守卫、动作和转换 |
| Interaction States | Empty、Loading、Error、No Permission、Retry、Recovery 等适用结论 |
| Exit Conditions | 成功、取消、失败、超时和安全退出 |
| Requirement Trace | Requirement 与 UXD/PCI Design Element |

### 13.4 Page and Component Inventory

| 信息 | 最低要求 |
|---|---|
| Page or Component ID | 容器内永久成员 ID |
| Name and Type | 名称、Page/UX Component/Technical Component |
| Responsibility | 单一可判定职责 |
| Flow | UFS Flow/Step 引用 |
| Input and Output | 数据、事件、动作和副作用 |
| States | Interaction/System State 映射 |
| Permission | Subject、Action、可见、可操作和拒绝行为 |
| Reuse Boundary | 允许、禁止和扩展条件 |
| Trace | Requirement、UXD/TDS Revision、IFC/DSM/PEM 和验证 |

### 13.5 Technical Design Specification

| 信息 | 最低要求 |
|---|---|
| Design ID | TDS Asset ID 与当前 Revision |
| Requirement | 当前 ID、Revision、Criterion 和 Quality Attribute |
| System Boundary | System of Interest、Affected/Unaffected、Trust Boundary |
| Affected Components | Component ID、责任、变化和 Owner |
| Data Flow and State | 来源、目标、方向、状态、一致性和失败 |
| Interface | IFC ID/Revision |
| Data Model Concept | DSM ID/Revision；禁止物理 Schema |
| Permission and Security | PEM、信任、授权、审计和敏感等级引用 |
| Exception/Retry/Idempotency/Consistency | 条件、策略、限制、停止和恢复 |
| Performance and Capacity | Measure、目标、负载、资源和边界 |
| Migration and Rollback | 步骤、触发、数据、窗口、Owner 和验证 |
| Observability | Log、Metric、Trace、Event、Alert 和关联 ID |
| Test Strategy | C05 Criterion、Method、TCR 和所需接口 |
| Alternatives and Decisions | 候选、权衡、C10 Decision ID/State |
| Risk | C02 Risk ID、影响、控制和剩余 Risk |

### 13.6 System Context or Component View

| 信息 | 最低要求 |
|---|---|
| Purpose | View 的使用与评审目的 |
| Stakeholder Concerns | Stakeholder、Concern 和优先级来源 |
| Viewpoint | 元素、关系、规则和解释 |
| System Boundary | System of Interest、内部/外部和信任边界 |
| Components and External Entities | ID、名称、责任和 Owner |
| Relations | 数据/控制流、方向、同步/异步和协议引用 |
| Legend | 符号、线型、颜色和缩写 |
| Applicable Version | Product、Design 和 Configuration Revision |
| Correspondence | 其他 View/Model/Requirement 的一致性 |
| Decision | C10 Decision 与 Rationale 引用 |
| Limitations | 未覆盖 Concern 和抽象层级 |

### 13.7 API or Interface Contract

| 信息 | 最低要求 |
|---|---|
| Provider and Consumer | ID、Owner、责任和环境 |
| Operation or Event | 名称、类型、触发和语义 |
| Input and Output | 字段、类型语义、单位、边界、必填性和敏感等级引用 |
| Error | 类别、可重试性、外部语义和用户影响 |
| Permission | Authentication、Authorization、Audit |
| Idempotency | Key、范围、有效期、重复副作用 |
| Compatibility | Version、兼容方向、Breaking、Deprecation |
| Performance | Timeout、Latency、Throughput、Quota/Rate |
| Change | 通知、迁移、回滚和生效 |
| Verification | Method、TCR、Mock/Stub/Contract Test 和 Evidence 要求 |

### 13.8 Data and State Model

| 信息 | 最低要求 |
|---|---|
| Business Entity or State | ID、名称、类型和定义 |
| Semantics | 业务含义、来源和术语 |
| Relations | 基数/关联语义和所有权 |
| Constraints | 不变量、边界和禁止组合 |
| State Transitions | 源、目标、事件、守卫、动作、失败和补偿 |
| Consistency | 范围、强度、时间窗口和冲突处理 |
| Data Owner | 人类责任角色 |
| Retention | 分类、期限、归档/删除责任引用 |
| Requirement | 当前 Requirement 与 TDS/IFC Trace |
| Physical Schema Exclusion | 明确未规定物理表、列、索引和 DDL |

### 13.9 Permission Model

| 信息 | 最低要求 |
|---|---|
| Subject | 类型、身份源、租户/组织和生命周期 |
| Resource | 类型、Owner、范围和敏感等级引用 |
| Action | 读取、创建、修改、删除、执行、批准等明确动作 |
| Condition | Context、时间、关系、属性和环境 |
| Default Deny | 冲突、缺省和未知时的 Deny |
| Authorization Source | Policy/Role/Attribute/Relationship 的权威来源 |
| Segregation of Duties | 冲突职责、自审批和双人控制 |
| Audit | 事件、字段、关联、保留和访问 |
| Exception and Revocation | 临时授权、到期、撤销、传播和失败 |
| Verification | 正向、反向、越权、隔离、撤销和审计方法 |

### 13.10 Design Coverage Matrix

| 信息 | 最低要求 |
|---|---|
| Requirement | ID、Revision、Criticality 和 Scope |
| UX Element | 精确成员 ID 或 Not Applicable |
| Technical Design Element | 精确成员 ID 或 Not Applicable |
| No Design Required | 理由、现有覆盖、Reviewer、批准人和日期 |
| Design Revision | UXD/TDS 及相关产物 Revision |
| Review Status | Design Review Status、Outcome 和 Finding |
| Coverage Status | 受控值 |
| Gap Owner | 人类责任人、期限和关闭条件 |

### 13.11 Design Constraint Record

| 信息 | 最低要求 |
|---|---|
| Constraint Statement | 单一、明确且可判定的限制 |
| Source | 法律、合同、Scope、Requirement、Decision、Dependency 或 Evidence |
| Applicable Design Scope | 受约束资产、Element、版本和环境 |
| Impact | 用户、技术、质量、验证、迁移和运营影响 |
| Alternative Limitation | 排除或限制的方案及理由 |
| Release Condition | 解除、到期或重新评估条件 |
| Owner | 负责监控与处理的人类角色 |
| Decision and Risk | C10 Decision、C02 Risk 和适用 Waiver |

## 14. 质量准则

### 14.1 单项产物质量

每类产物必须同时满足：

- Complete：通用与类型专属必填信息完整；
- Correct：不改变上游义务且与权威输入一致；
- Consistent：UX、技术、接口、数据、权限、状态和 View 无冲突；
- Traceable：来源、Design Element、Decision、Risk、验证与下游可定位；
- Feasible：责任、约束和依赖支持实现；
- Verifiable：有可观察行为、边界、Measure、接口或检查点；
- Current：Revision、Prototype、Dependency 和 Decision 状态当前有效；
- Bounded：Affected 与 Unaffected Boundary 清晰；
- Reviewable：结构、图例、术语、差异和开放问题可直接评审。

### 14.2 UX 质量

1. 关键 Requirement 必须落到可识别用户任务、Flow、Page/Component 和 State。
2. 正常、异常、无权限和恢复路径必须完整。
3. 交互原则必须结合 Context 判定，不得用通用启发式替代用户证据。
4. 内容、响应式、键盘、焦点、语义和辅助技术反馈必须有设计规则。
5. 原型与 UXD Revision 必须一致，差异必须显式记录。

### 14.3 技术设计质量

1. System Boundary、Affected/Unaffected、Component Responsibility 和 External Dependency 清晰。
2. Data、State、Interface、Permission 和 Failure Behavior 相互一致。
3. Performance、Reliability、Security、Maintainability、Compatibility、Migration、Rollback 和 Observability 有适用结论。
4. Architecture/Technology 选择具有 Decision 引用。
5. 实现团队无需通过未记录假设补全关键行为。

### 14.4 跨产物一致性

以下对应必须无冲突：

| UX 事实 | 技术事实 |
|---|---|
| User Action | Operation/Event/Command |
| Interaction State | System State |
| Page/Component Input | IFC Input |
| User-visible Result | IFC Output / State Change |
| Error and Recovery Message | Error Category / Retry / Recovery |
| Permission Difference | PEM Policy |
| Cancel/Undo | Compensation/Rollback |
| Responsive/Accessibility Rule | Component/Platform Constraint |
| Performance Expectation | Capacity/Latency Design |

## 15. 验证与符合性检查

### 15.1 自动检查

自动检查至少验证：

1. 十类正式产物是否存在独立身份；
2. 通用和类型专属字段是否齐全；
3. Artifact Type、State 和非 State 值是否来自受控集合；
4. Asset ID 与 Design Element ID 是否唯一且格式正确；
5. 每个关键 Requirement 是否存在 DCM 行；
6. DCM 引用的 Requirement、Element 和 Revision 是否可解析；
7. `No Design Required` 是否有理由、Reviewer 和批准；
8. UXD/TDS 是否分别存在且未复制为同一正文；
9. UFS 是否含适用的 Empty、Loading、Error、No Permission 和 Recovery；
10. TDS 是否含 Affected 与 Unaffected Boundary；
11. IFC/DSM/PEM 引用是否当前有效；
12. 重大选择是否有 C10 Decision 引用；
13. Migration、Rollback 和 Observability 是否有适用结论；
14. DCT Open/Blocked 项是否进入 Readiness；
15. 外部 Prototype/View/Contract 引用是否含版本和 Owner；
16. Baselined 资产是否只通过 Change Request 更新。

自动检查只能发现结构化缺口，不能证明用户适合性、架构正确性、安全充分性、可用性、无障碍或 Design Ready。

### 15.2 人工评审

人工评审必须回答：

1. 用户、Context、任务和用户概念是否有真实上游依据；
2. Flow 是否覆盖正常、异常、权限、取消、超时和恢复；
3. 页面/组件是否具有明确责任、状态和复用边界；
4. 内容是否可理解、可操作且不泄露敏感信息；
5. 键盘、焦点、语义、响应式与完整过程是否支持 WCAG 目标；
6. System Boundary 与 Scope 是否一致；
7. 组件、数据、状态、接口和权限是否相互一致；
8. 质量属性是否有设计机制、Measure 和验证接口；
9. 兼容、迁移、回滚和可观测是否可执行；
10. Alternative、Constraint、Decision 和 Risk 是否真实完整；
11. 是否存在 Agent 自行扩大 Scope 或隐式架构选择；
12. DCM 是否准确反映 Gap，而非追求表面百分比。

### 15.3 Design Ready 阻断条件

存在任一条件时，Readiness Conclusion 必须为 `Not Ready` 或 `Blocked`：

- 当前 Scope 内存在关键 Requirement 未覆盖、Stale 或 Blocked；
- Requirement、Criterion、Design 或 Decision 存在未解决冲突；
- UXD/TDS 缺失、合并或复制为第二事实源；
- 核心 Flow 遗漏 Empty、Loading、Error、No Permission 或 Recovery 的适用设计；
- System Boundary、Affected 或 Unaffected Boundary 不明确；
- 共享 Interface、Data、State 或 Permission 无 Owner/Contract；
- 重大架构变化无 C10 Decision；
- 适用 Migration、Rollback 或 Observability 未设计；
- ISO/IEC 25010 适用性存在 `Not Assessed`；
- Web 核心流程未记录 WCAG 2.2 AA 设计目标与验证引用；
- Gate-blocking DCT、Risk 或 Finding 未关闭；
- 输入 Revision 非当前、无 Snapshot 或上游未达到要求状态；
- 需要激活的 E01 至 E05 尚未判定或未激活；
- Agent 超出授权范围或无法识别批准主体。

### 15.4 符合性声明限制

通过本规范检查仅表示 C06 内部结构与规则满足，不表示产品符合 ISO 9241、ISO/IEC/IEEE 42010、ISO/IEC/IEEE 12207、ISO/IEC 25010、ISO/IEC 40500、WCAG、法律或外部认证要求。

## 16. 追踪与记录要求

### 16.1 最低 UX Trace

```text
Need / Intent / Goal
  → PRD / Feature / User Scenario
  → Requirement
  → UXD UX Element
  → UFS Flow / State
  → PCI Page / Component
  → Acceptance Criterion
  → Verification / Validation Evidence
```

### 16.2 最低技术 Trace

```text
Scope / Requirement / Quality Attribute
  → TDS Technical Design Element
  → SCV / IFC / DSM / PEM
  → Decision / Constraint / Risk
  → Implementation Artifact
  → Test/Check
  → Verification Evidence
```

### 16.3 Design Coverage Trace

DCM 每行必须能够从 Requirement 正向定位 Design Element 和验证，并能从任一 Design Element 反向定位 Requirement、Decision、Risk 和当前 Revision。C10 统一 Traceability Matrix 负责跨域汇总，但不得替代 DCM。

### 16.4 记录保留

1. Approved/Baselined Design、Rejected Alternative、Finding、Constraint、Decision 引用和变更影响永久保留。
2. Prototype 或外部设计资产必须保存可恢复版本或不可变 Snapshot 引用。
3. 图形 View 必须同时保留可读导出和源格式/生成来源。
4. 记录更正必须创建新 Revision，不得覆盖原历史。
5. 敏感 View、Interface、Data 或 Permission 信息按 Access Classification 限制访问。

## 17. 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C06 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

C06 按 Change Surfaces 激活：UI/UX 触发 UXD/UFS/PCI；API/Integration 触发 IFC；Data/Schema 触发 DSM；Identity/Security/Privacy 触发 PEM；Architecture/Multi-repo 或复杂技术边界触发 TDS/SCV；设计约束事件触发 DCT。未变化的设计通过固定 Revision/Snapshot `Reference`。

DCM 只作为 REQ 与 UXD/TDS 的派生覆盖视图按需 `Generate`。HTML/PNG UI 效果只在 UI 变化且需要视觉决策时生成，不是所有任务的固定步骤。

### 17.1 当前 P2 决议

当前项目采用 P2 标准档位：

1. 十类正式产物类型和控制能力均保留，实例按 Task Profile 触发；
2. UXD 与 TDS 禁止合并；
3. UFS、PCI、SCV、IFC、DSM、PEM、DCM、DCT 禁止删除；
4. 模板可以嵌入本规范附录，但每次实例必须保留独立身份；
5. 永久 ID、Source、Owner、Revision、Trace、Review、Change 和 History 禁止裁剪；
6. 物理上同页展示不改变逻辑独立性。

### 17.2 允许的呈现裁剪

在不删除字段、不改变语义且保持独立身份的前提下，可以：

- 使用表格、模型仓库、需求工具或图形工具承载产物；
- 将多个 View 存入同一 SCV；
- 将多个小型接口作为同一 IFC 的成员；
- 在同一评审包内展示十类产物；
- 对 `Not Applicable` 内容使用结构化理由代替空章节。

### 17.3 未来裁剪

改为 P1 时，可以按蓝图将 UX 与技术设计呈现在一份 Design Brief 中，但仍须保留用户流程、状态、技术边界、数据/权限、验证和回滚信息。当前 P2 变更为 P1/P3、合并规范或取消产物必须通过正式 Change Request 和人类批准。

## 18. 扩展接口

| 扩展 | 触发时 C06 必须提供 | C06 不得替代 |
|---|---|---|
| E01 Architecture Governance | Concern、Viewpoint、SCV、架构 Decision、边界、质量属性和演进影响 | Architecture Description、Viewpoint Catalog、Architecture Conformance Review |
| E02 Security/Privacy/Compliance | Trust Boundary、PEM、敏感 Data Flow、Security Requirement、Threat/Privacy 输入和控制接口 | Threat Model、PIA/DPIA、Security Verification Plan |
| E03 Data and AI Data Governance | DSM、Data Flow、Owner、质量、保留、模型/数据使用边界 | Data Contract、Dataset、Model Card、AI Impact/Data Quality 资产 |
| E04 Knowledge and Records | Source、Revision、Trace、Freshness、Access、Retention、Supersession | Knowledge Catalog、Freshness Report、Retrieval Policy |
| E05 Operations and Service | SLO/Capacity 输入、Observability、Failure、Recovery、Migration、Rollback 和运行责任 | Service Definition、Runbook、Incident、SLA/SLO、Release Plan |

目标产品必须在 Discovery Ready 前建立扩展适用性记录，并在 Scope、Data、Architecture、外部暴露或运营方式变化时重新判定。

## 19. 参考标准

### 19.1 R1 国际标准

1. [ISO 9241-210:2019](https://www.iso.org/standard/77520.html)：人本设计原则、计划与活动；
2. [ISO 9241-110:2020](https://www.iso.org/standard/75258.html)：交互原则；
3. [ISO 9241-115:2024](https://www.iso.org/standard/80773.html)：概念、用户—系统交互、界面与导航设计；
4. [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html)：架构描述、Concern、Viewpoint、View 和 Decision；
5. [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html)：软件生命周期过程、裁剪、技术管理和技术过程；
6. [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)：九类产品质量模型。

### 19.2 R2 无障碍参考

1. [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/)；
2. [ISO/IEC 40500:2025](https://www.iso.org/standard/91029.html)，仅作为 WCAG 2.2 国际标准化版本状态补充。

### 19.3 R3 表达实践

1. [MADR 官方项目](https://adr.github.io/madr/)；
2. [MADR 官方模板](https://adr.github.io/madr/decisions/adr-template.html)。

### 19.4 来源与复核边界

本规范依据 2026-07-28 可访问的官方公开摘要和目录编制。ISO、IEC、IEEE 付费正文未被复制；未公开子条款未被推断。C06 基线前必须复核版本状态，完整符合性声明前必须取得合法全文并逐项验证。生产前调研详见 RVR-C06-0001。

## 20. 附录

### 20.1 通用资产头模板

```markdown
| 信息项 | 内容 |
|---|---|
| Asset ID | <类型代码>-<顺序号> |
| Artifact Type | <正式英文名称>（<类型代码>） |
| Name or Summary |  |
| Purpose |  |
| Source |  |
| Owner |  |
| State | Draft |
| Current Revision | 0.1 / Snapshot |
| Created and Updated |  |
| Applicable Scope |  |
| Trace Links |  |
| Access Classification | Internal |
| Retention Rule |  |
| History Reference |  |
```

### 20.2 UX Design Specification 模板骨架

```markdown
# UXD-____ <名称>

## Design Control
- Design ID and Revision:
- Input Snapshot:
- Owner / Reviewers / Approval Authority:
- Design Review Status:
- Prototype or Design References:

## Users, Context and Tasks
| User | Goal | Task | Context | Limitation | Source |
|---|---|---|---|---|---|

## Conceptual Design and Information Architecture
| UX Element | Object/Action/Term | User Meaning | Rule | Requirement |
|---|---|---|---|---|

## Primary and Exception Flows
| Flow | Entry | Primary | Exception | Exit | UFS |
|---|---|---|---|---|---|

## Pages, Components and Interaction States
| Element | Page/Component | State | Feedback | Action/Recovery | Permission | PCI |
|---|---|---|---|---|---|---|

## Content, Responsive and Accessibility
| Element | Content Rule | Device/Input | Reflow | Keyboard/Focus | WCAG Target | Verification |
|---|---|---|---|---|---|---|

## Constraints, Risks and Open Findings
```

### 20.3 User Flow and State Model 模板骨架

```markdown
# UFS-____ <名称>

| Flow/State ID | User Role | Entry/Source | User Action | System Response | Branch/Guard | Interaction State | System State | Exit/Recovery | Requirement |
|---|---|---|---|---|---|---|---|---|---|

## State Transition
| State ID | Source | Event | Guard | Target | Action | Failure | Retry/Recovery | Observability |
|---|---|---|---|---|---|---|---|---|

## Coverage
- Empty:
- Loading:
- Error:
- No Permission:
- Retry:
- Recovery:
- Cancel/Timeout:
```

### 20.4 Page and Component Inventory 模板骨架

```markdown
# PCI-____ <名称>

| Page/Component ID | Name | Type | Responsibility | Flow | Input | Output/Event | States | Permission | Reuse Boundary | Requirement | Design Revision |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Component Contract
- Semantics:
- Actions and consequences:
- Content source:
- Responsive rules:
- Keyboard/focus/assistive technology:
- Error/recovery:
- IFC/DSM/PEM:
```

### 20.5 Technical Design Specification 模板骨架

```markdown
# TDS-____ <名称>

## Design Control
- Design ID and Revision:
- Input Snapshot:
- Requirement / Criterion / Quality Attribute:
- Owner / Reviewers / Approval Authority:

## Boundary and Components
| Technical Element | Affected Component | Change | Unaffected Boundary | Owner | SCV |
|---|---|---|---|---|---|

## Data, State and Interface
| Element | Data Flow | State/Consistency | IFC | DSM | Failure |
|---|---|---|---|---|---|

## Permission and Security
| Element | Trust Boundary | PEM | Authentication/Authorization | Audit | Verification |
|---|---|---|---|---|---|

## Exception and Reliability
| Failure | Timeout | Retry | Idempotency | Concurrency/Ordering | Recovery/Degradation |
|---|---|---|---|---|---|

## Performance and Capacity
| Measure | Target | Load/Volume | Resource Boundary | Observation | Criterion |
|---|---|---|---|---|---|

## Compatibility, Migration and Rollback
| Object | Compatibility | Migration | Rollback Trigger/Window | Data Handling | Verification |
|---|---|---|---|---|---|

## Observability and Test Strategy
| Requirement | Log/Metric/Trace/Event/Alert | Method | TCR | Evidence Need |
|---|---|---|---|---|

## Alternatives, Decisions, Constraints and Risks
```

### 20.6 System Context or Component View 模板骨架

```markdown
# SCV-____ <名称>

- View ID and Purpose:
- Stakeholders and Concerns:
- Viewpoint:
- System of Interest:
- Applicable Product/Design/Configuration Revision:

## Elements
| Element ID | Type | Name | Responsibility | Owner | Boundary |
|---|---|---|---|---|---|

## Relations
| Source | Relation Type | Target | Direction | Sync/Async | Interface/Data | Trust | Requirement |
|---|---|---|---|---|---|---|---|

## Legend

## Correspondence, Decisions and Limitations
```

### 20.7 API or Interface Contract 模板骨架

```markdown
# IFC-____ <名称>

| Field | Value |
|---|---|
| Provider / Consumer / Owner |  |
| Operation or Event / Version |  |
| Environment and Scope |  |

## Input and Output
| Field | Direction | Semantics | Required | Constraint/Unit | Sensitive Classification |
|---|---|---|---|---|---|

## Error, Permission and Delivery
| Error/Event | External Meaning | Retry | Idempotency | Permission | Ordering/Delivery | Audit |
|---|---|---|---|---|---|---|

## Compatibility, Performance and Change
- Compatibility and deprecation:
- Timeout/latency/throughput/quota:
- Migration and rollback:
- Verification method and TCR:
```

### 20.8 Data and State Model 模板骨架

```markdown
# DSM-____ <名称>

## Entities and Relations
| Entity/State ID | Name | Type | Semantics | Relation/Constraint | Owner | Retention | Requirement |
|---|---|---|---|---|---|---|---|

## State Transitions
| Source | Event | Guard | Target | Action | Idempotency | Failure/Compensation | Audit |
|---|---|---|---|---|---|---|---|

## Consistency
| Scope | Consistency Requirement | Time Window | Conflict Handling | User-visible Behavior | Verification |
|---|---|---|---|---|---|

本模型不规定物理表、列、索引、分区、存储引擎或 DDL。
```

### 20.9 Permission Model 模板骨架

```markdown
# PEM-____ <名称>

| Rule ID | Subject | Resource | Action | Condition | Permit/Deny | Authorization Source | Audit | Expiry/Revocation | Requirement |
|---|---|---|---|---|---|---|---|---|---|

## Global Rules
- Default: Deny
- Conflict precedence:
- Segregation of duties:
- UI/service enforcement consistency:
- Temporary access and revocation propagation:

## Verification
| Scenario | Positive/Negative | Expected | Method | TCR | Evidence |
|---|---|---|---|---|---|
```

### 20.10 Design Coverage Matrix 模板骨架

```markdown
# DCM-____ <名称>

| Requirement ID/Revision | Criticality | UX Element | Technical Design Element | No Design Required Reason/Approval | Design Revision | Review Status/Outcome | Coverage Status | Gap Owner | Due/Close Condition |
|---|---|---|---|---|---|---|---|---|---|

## Summary
- Total current in-scope Requirements:
- Key Requirements covered / stale / blocked:
- All Requirements by Coverage Status:
- Open Gap IDs:
```

### 20.11 Design Constraint Record 模板骨架

```markdown
# DCT-____ <Constraint 摘要>

| Field | Value |
|---|---|
| Constraint Statement |  |
| Source |  |
| Applicable Design Scope/Revision |  |
| Impact |  |
| Alternative Limitation |  |
| Release/Recheck Condition |  |
| Owner |  |
| Decision / Risk / Waiver |  |
| State | Open |

## Handling History
| Time | Old State | New State | Action/Evidence | Actor | Approval |
|---|---|---|---|---|---|
```

### 20.12 设计评审速查表

| 评审面 | 必须读取 | 最低输出 |
|---|---|---|
| Scope | C02 Scope、Non-goal、Affected/Unaffected | 范围一致性 Finding |
| Requirement | C04 Requirement Set、Revision | DCM 覆盖与 Gap |
| Verification | C05 Criteria/Strategy | 可验证性和 Evidence 接口 |
| UX | UXD、UFS、PCI、Prototype | Flow/State/Content/Accessibility Finding |
| Technical | TDS、SCV、IFC、DSM、PEM | Boundary/Data/Interface/Permission Finding |
| Quality | C03 QAS、C04 Quality Requirement、C05 Criterion | 九类特性适用性 |
| Decision | C10 Decision | 重大选择、状态和后果 |
| Change | C11 Baseline/Change | Revision 与 Impact |
| Gate | C12 Criteria | Design Readiness 建议 |

### 20.13 C06 质量检查清单

| Check ID | 检查项 | 通过条件 |
|---|---|---|
| C06-CHK-001 | 正式文件名 | 与 VC-PPG-DEC-001 一致 |
| C06-CHK-002 | 二十章结构 | 第 1 至 20 章存在且编号唯一 |
| C06-CHK-003 | P2 产物 | 十类产物均有定义、必填信息和模板 |
| C06-CHK-004 | 逻辑独立 | 十类产物具有独立 Asset ID/Type/State/Revision |
| C06-CHK-005 | UX/TDS 分离 | UXD 与 TDS 不合并、不复制 |
| C06-CHK-006 | 输入冻结 | 输入 ID、Revision、Snapshot 和 State 可定位 |
| C06-CHK-007 | Scope | Affected 与 Unaffected Boundary 明确 |
| C06-CHK-008 | 关键 Requirement | 每项存在 DCM 行和有效覆盖 |
| C06-CHK-009 | No Design Required | 理由、现有覆盖、Reviewer 和批准完整 |
| C06-CHK-010 | 用户与 Context | 用户、目标、任务、环境和限制有来源 |
| C06-CHK-011 | 概念设计 | 用户对象、动作、术语和反馈明确 |
| C06-CHK-012 | User Flow | 入口、步骤、分支、响应和退出完整 |
| C06-CHK-013 | 状态覆盖 | Empty/Loading/Error/No Permission/Recovery 已判定 |
| C06-CHK-014 | Page/Component | 职责、输入输出、状态、权限和复用边界完整 |
| C06-CHK-015 | 内容 | 标签、帮助、错误、恢复和敏感信息规则明确 |
| C06-CHK-016 | 响应式 | 目标、输入、重排、优先级和状态保持明确 |
| C06-CHK-017 | 键盘与焦点 | 核心流程有键盘路径和焦点规则 |
| C06-CHK-018 | WCAG | Web 核心流程记录 2.2 AA 设计目标和验证引用 |
| C06-CHK-019 | View | Purpose、Concern、Viewpoint、Legend、Version 完整 |
| C06-CHK-020 | Component Boundary | 责任、Owner、依赖和失败边界明确 |
| C06-CHK-021 | Interface | Provider/Consumer、I/O、Error、Permission、Compatibility 完整 |
| C06-CHK-022 | Data/State | 语义、约束、转换、一致性和 Owner 完整 |
| C06-CHK-023 | Physical Schema | DSM 未规定物理 Schema |
| C06-CHK-024 | Permission | 默认拒绝、SoD、Audit、Exception、Revocation 完整 |
| C06-CHK-025 | Failure | Timeout/Retry/Idempotency/Concurrency/Recovery 明确 |
| C06-CHK-026 | 九类质量 | 每类为 Applicable/Not Applicable 且无 Not Assessed |
| C06-CHK-027 | Performance/Capacity | Measure、负载、资源和边界明确 |
| C06-CHK-028 | Migration/Rollback | 步骤、触发、窗口、数据和验证明确 |
| C06-CHK-029 | Observability | Log/Metric/Trace/Event/Alert 适用结论明确 |
| C06-CHK-030 | Decision | 重大选择引用当前 C10 Decision |
| C06-CHK-031 | Constraint/Risk | DCT 与 C02 Risk/Decision 关系完整 |
| C06-CHK-032 | Agent Boundary | 无 Scope 扩张、自批或隐式架构选择 |
| C06-CHK-033 | Change | Revision、Impact、Evidence Freshness 和 Context 已处理 |
| C06-CHK-034 | 状态模型 | DOC/CASE State 与非 State 值分离 |
| C06-CHK-035 | 国际标准 | 第 19 章与 20.15 使用官方来源和公开条款 |
| C06-CHK-036 | 符合性限制 | 未宣称完整 ISO/IEC/IEEE/WCAG 符合性 |

### 20.14 正反例

正例：

```text
Requirement REQ-0217 r3
  designed-by UXD-0042#UXE-007
  designed-by TDS-0031#TDE-012

UXE-007:
  用户提交后进入 Loading；
  超过 10 秒显示仍在处理和取消入口；
  权限失效时进入 No Permission，不显示目标资源详情；
  可重试失败给出原操作与重复提交风险说明。

TDE-012:
  IFC-0015#OP-006 使用幂等键；
  超时不等同失败，状态通过查询接口收敛；
  重试上限与停止条件引用 DEC-0088；
  Log/Metric/Trace 使用同一 Correlation ID；
  Rollback 保留旧 Consumer 兼容窗口。
```

反例：

```text
设计：做一个现代化页面，接口失败时适当重试。
技术：后端优化一下，必要时重构数据库。
覆盖：REQ-0217 → 见设计稿。
状态：设计已完成。
```

反例不合格原因：无 Asset/Revision/Element、无用户与 Context、无状态触发和恢复、无幂等/边界/Decision、扩大 Scope、无精确 Trace，并把非受控“已完成”写成 State。

### 20.15 参考的国际标准条款与公开范围映射总表

| 标准或实践 | 参考条款/公开范围 | 官方主题 | C06 对应章节 | 本规范落地 |
|---|---|---|---|---|
| ISO 9241-210:2019 | 1 | Scope | 第 2–4、9 章 | 将交互系统的人本设计纳入受控生命周期 |
| ISO 9241-210:2019 | 5.1–5.7 | 人本设计原则 | 第 10.3、14.2 章 | 用户/任务/环境、参与、评价、迭代、整体体验和多学科视角 |
| ISO 9241-210:2019 | 6.1–6.5 | 人本设计计划 | 第 7、9.2–9.5 章 | 责任、活动、时间、资源和计划接口 |
| ISO 9241-210:2019 | 7.1–7.3 | 人本设计活动、Context 与用户要求 | 第 9、10.2–10.4、13.2 章 | 固定 Context/用户要求输入并追踪 UXD |
| ISO 9241-110:2020 | 4.1–4.6 | 交互原则框架与应用 | 第 10.3–10.7、14.2 章 | 按 Context 选择和评审交互原则 |
| ISO 9241-110:2020 | 5.1 | Suitability for the user’s tasks | 第 10.3–10.5 章 | 以任务、目标与结果组织 Flow |
| ISO 9241-110:2020 | 5.2 | Self-descriptiveness | 第 10.5–10.7 章 | 状态、能力、反馈和动作自说明 |
| ISO 9241-110:2020 | 5.3 | Conformity with user expectations | 第 10.4–10.7 章 | 一致命名、导航和可预测行为 |
| ISO 9241-110:2020 | 5.4 | Learnability | 第 10.3、10.7 章 | 发现、指导与学习支持 |
| ISO 9241-110:2020 | 5.5 | Controllability | 第 10.4、10.6 章 | 取消、撤销、确认、退出和恢复 |
| ISO 9241-110:2020 | 5.6 | Use error robustness | 第 10.6–10.7 章 | 错误预防、反馈、重试和恢复 |
| ISO 9241-110:2020 | 5.7 | User engagement | 第 10.3、14.2 章 | 在任务与风险边界内支持参与 |
| ISO 9241-115:2024 | 1、4.1–4.2 | 适用范围、人本活动和通用指导 | 第 3、9、10.3 章 | UXD 嵌入迭代设计与评价 |
| ISO 9241-115:2024 | 5.1–5.2 | Conceptual design | 第 10.3、13.2 章 | 用户对象、动作、关系和术语 |
| ISO 9241-115:2024 | 6.1–6.6 | 用户—系统交互与场景设计 | 第 10.4、13.3 章 | Flow、场景、用户动作和系统响应 |
| ISO 9241-115:2024 | 7（公开目录） | User interface design | 第 10.5–10.7、13.4 章 | Page、Component、Content、State 与 Navigation |
| ISO/IEC/IEEE 42010:2022 | 1 | Architecture 与 Architecture Description 边界 | 第 4、6、10.8 章 | SCV 不自动构成完整 Architecture Description |
| ISO/IEC/IEEE 42010:2022 | 4 | Conformance | 第 15.4、19.4 章 | 禁止无合法全文的完整符合性声明 |
| ISO/IEC/IEEE 42010:2022 | 5.1–5.4 | 概念基础、生命周期、框架与语言 | 第 6、8.3、10.8 章 | 统一 Concern/Viewpoint/View/Model 术语 |
| ISO/IEC/IEEE 42010:2022 | 6.1–6.10 | AD 标识、Stakeholder、Concern、Viewpoint、View、Correspondence、Decision | 第 8.3、10.8、13.6 章 | SCV 元数据、关系一致性和 Decision 引用 |
| ISO/IEC/IEEE 42010:2022 | 7.1–7.2 | Architecture Description Framework/Language | 第 8.3、10.8 章 | 采用框架/语言时记录名称、版本与语义 |
| ISO/IEC/IEEE 12207:2026 | 1 | 生命周期范围与迭代/递归/增量应用 | 第 3、9、10.18 章 | 增量设计、受控输入和演进 |
| ISO/IEC/IEEE 12207:2026 | 4.1–4.3 | Conformance 与 Tailoring | 第 15.4、17 章 | P2 裁剪、Not Applicable 理由和声明限制 |
| ISO/IEC/IEEE 12207:2026 | 5.1–5.8 | 系统、组织、生命周期、过程与应用概念 | 第 8–11、16 章 | 设计作为受控生命周期工作产品 |
| ISO/IEC/IEEE 12207:2026 | 6.3（公开目录） | Technical management processes | 第 9.5–9.6、10.15、16–18 章 | Decision、Risk、Configuration、Quality 接口 |
| ISO/IEC/IEEE 12207:2026 | 6.4（公开目录） | Technical processes | 第 10.8–10.14、13.5–13.9 章 | 边界、设计、接口、数据、权限、集成与验证输入 |
| ISO/IEC 25010:2023 | 3.1–3.9 | 九类产品质量特性 | 第 10.13、14.3、20.13 章 | 九类适用性、设计策略和验证追踪 |
| ISO/IEC 25010:2023 | 4.1 | Product quality model structure | 第 10.13、14.3 章 | 按特性/子特性组织设计考虑 |
| ISO/IEC 25010:2023 | 4.2 | Targets of the product quality model | 第 10.1、10.8–10.13 章 | 固定产品、组件、接口、数据、环境和版本 |
| ISO/IEC 25010:2023 | 5 | 与 Quality-in-use model 的关系 | 第 4、8.5、14.2 章 | Design 与 C05 Validation 分离 |
| ISO/IEC 25010:2023 | Annex C（公开目录） | 使用模型进行测量 | 第 10.13、13.5、15 章 | 记录 Measure、数据源和验证接口 |
| WCAG 2.2 | 1–4 | Perceivable、Operable、Understandable、Robust | 第 10.7、13.2、14.2 章 | 适用 A/AA 的设计机制与 Element Trace |
| WCAG 2.2 | 2.1、2.4 | Keyboard Accessible 与 Navigable | 第 10.4–10.7 章 | 键盘、焦点、导航、标题和响应式变体 |
| WCAG 2.2 | 3.2–3.3 | Predictable 与 Input Assistance | 第 10.6–10.7 章 | 一致行为、标签、错误、帮助和认证支持 |
| WCAG 2.2 | 4.1.2–4.1.3 | Name/Role/Value 与 Status Messages | 第 10.5–10.7、13.4 章 | 组件语义、状态和辅助技术反馈 |
| WCAG 2.2 | 5.2.1–5.2.5 | Level、Full pages、Complete processes、Accessibility-supported、Non-interference | 第 10.7、15.2–15.4 章 | 默认 AA 设计目标、完整页面/流程和声明限制 |
| ISO/IEC 40500:2025 | 官方公开范围 | 采用 WCAG 2.2 | 第 19.2–19.4 章 | 版本状态补充，不改变 R2 层级 |
| MADR 4.0.0 | Context、Drivers、Options、Outcome、Consequences、Confirmation | 决策记录表达结构 | 第 8.5、10.15、13.5、19.3 章 | 作为 C10 Decision Record 的可选表达，不建立平行身份 |
