# Vibe Coding 受控产物元模型、领域 Profile 与状态模型 V6.3 Candidate

| 文档属性 | 内容 |
|---|---|
| 文档编号 | VC-PPG-COM-002 |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 生效日期 | 待评审；V6.2/V6.2.1 历史由 Git 保留 |
| 变更来源 | CHG-0006、IMA-0003、CHD-0004 Proposed |
| 责任人 | 项目负责人 |
| 上位基线 | 尚未建立；V6.3 Candidate 不替代现有 Baseline |
| 关联决议 | VC-PPG-DEC-001 |
| 关联术语基线 | VC-PPG-COM-001 |
| 适用范围 | 六类正式元类型、C01 至 C12/E01 至 E05 的 137 个兼容领域 Profile 及被触发实例 |

## 1. 目的

本文件建立六类正式产物元类型、领域 Profile 兼容目录、通用信息、Profile 专属信息、状态模型、转换规则和实例动作。V6.2/V6.2.1 的 137 个类型代码自 V6.3 起作为 `legacy_kind/profile` 保留，不再构成顶层产物类型。

本文件定义概念信息和治理规则；六类机器载体的 JSON Schema 由 `run-governed-product-workflow/assets/runtime/schemas/` 实现，Schema 不得改变本文件语义。

## 2. 适用规则

1. 每个治理对象必须先确定六类正式元类型之一；`AuthorityAsset` 和兼容 `DerivedView` 再按第 5 至 21 章确定 `legacy_kind/profile`。
2. 被创建或修订的领域 Profile 实例必须同时满足第 3 章通用信息和第 5 至 21 章对应行的专属信息。
3. “登记册”“集合”“目录”“矩阵”自身是受控资产；其每个成员必须具有成员标识、成员状态、来源和历史。
4. 字段标记“不适用”时，必须记录规则级理由和当前产物批准或 Artifact Manifest 人类确认的引用；同一次确认覆盖的字段不得重复要求人逐字段批准。禁止留空代替不适用判定。
5. 模板可以增加领域字段，但不得删除、改名或改变本文件规定字段的语义。
6. 六类元类型名称是正式顶层分类；原三位代码是稳定 `legacy_kind/profile`，创建后不得复用。
7. 元类型或 Profile 不等于独立物理文件；共享载体必须保持每个逻辑对象身份可独立解析。
8. 未触发的 Profile 不创建空文件；完整载体模式由 `before.json` 中的 Task Profile、VC-PPG-TAIL-001 `tailoring_resolution` 和 Artifact Manifest 解析；Minimal 载体模式由同一 TaskContract、RunLedger、TaskOutcome 字段子集和资格事实解析。
9. 默认物理载体分别使用 `before.json`、`run.jsonl` 和 `after.json`。仅当 VC-PPG-DEC-001 的 Minimal 全部资格条件成立时，三类逻辑对象可以聚合进 `task-record.json`；该文件不是新元类型、任务等级或平行框架。两种载体都必须进入 `project-state.json`。
10. `generated/` 下的审核报告、矩阵和索引是可重建视图，禁止反向成为权威事实源。

### 2.1 六类正式元类型

| 元类型 | 生命周期位置 | 权威性 | 默认物理载体 |
|---|---|---|---|
| ProjectState | 跨任务当前状态 | 从终态和权威资产物化，不直接编辑 | `.project-governance/project-state.json` |
| TaskContract | 任务执行前 | 保存 Task Profile、适用性事实、确定性裁剪快照、权限、验收和计划；Run 开始时冻结，修订必须留痕 | `tasks/<TaskID>/before.json` |
| RunLedger | 任务执行中 | 只追加重要事件 | `tasks/<TaskID>/run.jsonl` |
| TaskOutcome | 任务终态 | 已成立事实和遗留问题的任务级事实源 | `tasks/<TaskID>/after.json` |
| AuthorityAsset | 项目长期事实 | 需求、设计、决定、证据、基线等权威对象 | 保留原生格式并使用统一元数据 |
| DerivedView | 按需审核与查询 | 可重建，禁止直接承载新权威事实 | `generated/reviews/`、`generated/matrices/` |

正式顶层类型数量为 6，相比 V6.2/V6.2.1 的 137 个逻辑类型减少 131 个，缩减 95.62%。137 个原代码全部保留为兼容 Profile；映射唯一来源为 VC-PPG-MAP-001。

`tasks/<TaskID>/task-record.json` 是 TaskContract、RunLedger、TaskOutcome 的 Minimal 聚合载体。它必须保持三类逻辑身份和生命周期段可独立解析，不得使用 `TaskRecord` 作为第七个 `meta_type`。命中升级条件后，原 Minimal 载体进入只读历史，活动记录单向转换为默认三文件载体；禁止重转为 Minimal。

### 2.2 身份与顺序

统一身份链为 `ProjectID → WorkItemID → TaskID → RunID → AttemptID`。`TaskID` 表示可排序、可依赖的子任务，必须同时记录 `ordinal`、`depends_on`、`supersedes` 和 `blocked_by`；禁止只用编号顺序推断真实依赖。

### 2.3 固定目录与原生格式

普通项目默认使用项目根目录 `.project-governance/`，允许通过工具参数修改治理根目录。任务记录固定为 JSON/JSONL；AuthorityAsset 保留 Markdown、JSON、图、表格或外部权威系统记录等原生格式，通过统一元数据和索引定位。

### 2.4 兼容与迁移

1. 新任务只写六类元模型。
2. 旧对象通过 `legacy_kind` 和 VC-PPG-MAP-001 读取；不要求本次批量改写历史资产。
3. 迁移不得修改原始内容；先生成迁移计划，再建立新信封或受控引用。
4. V6.2/V6.2.1 的历史报告和决议保持历史语义，不因 V6.3 Candidate 反向改写。

## 3. AuthorityAsset 与领域 Profile 的通用必填信息

| 信息项 | 最低要求 |
|---|---|
| Asset ID | 永久、唯一、不可复用，不包含版本、日期、状态或负责人 |
| Meta Type | 固定为 AuthorityAsset；派生查询结果固定为 DerivedView |
| Legacy Kind / Profile | 使用第 5 至 21 章规定的英文名称和三位兼容代码 |
| Name or Summary | 能唯一表达业务、工程或治理含义 |
| Purpose | 说明产物存在的治理目的或预期用途 |
| Source | 上游资产、事件、授权指令、事实证据或外部义务的引用 |
| Owner | 对内容正确性和状态负责的人类角色 |
| State | 使用第 4 章中该产物对应状态模型的受控值 |
| Current Revision | 当前修订号及对应快照引用 |
| Created and Updated | 创建者、创建时间、最后修改者和修改时间 |
| Applicable Scope | 适用产品、Initiative、PRD、模块、环境、版本或时间范围 |
| Trace Links | 至少包含上游来源和适用的下游消费方；使用受控关系类型 |
| Access Classification | 公开、内部、机密、受限之一；涉及个人信息、密钥或商业秘密时必须说明访问规则 |
| Retention Rule | 保留期限、归档条件和删除限制；正式基线、批准、执行证据和发布记录禁止无痕删除 |
| History Reference | 修订、状态变化、决策、批准、替代和更正记录的引用 |

### 3.1 公共责任与人工决定引用组

下列字段组只定义跨对象复用的最低引用信息，不新增元类型、领域 Profile、状态模型或物理 Schema。各规范和模板必须引用本节，只补充 Profile 专属字段。

| 字段组 | 最低信息 |
|---|---|
| Responsibility Reference | Owner；适用时的 Human Accountable、Responsible/Executor、Reviewer、Approver/Decision Maker；各角色身份或角色代码；Authority Source；Applicable Scope；Effective/Expiry；Independence/Conflict |
| Approval or Decision Reference | Decision Type；Object ID 与 Revision；Applicable Scope；Decision；Decision Maker 及角色；Authority Reference；Evidence Reference；Decision Time；Condition；Expiry/Review；Trace 与 History |

使用规则：

1. 角色语义和职责分离由 C07 定义；决定类型、状态和受控值由对应 DEC Profile 及本文件第 4 章定义。本字段组不表示每个对象都需要独立批准。
2. 类型专属模板可以展示本字段组，但不得再次定义 Owner、Reviewer、Approver、Authority、Scope、Decision、Evidence、Trace 或 History 的公共语义。
3. 某角色或决定不适用时，必须记录规则级理由，并引用当前产物批准或 Artifact Manifest 的人类确认；禁止新增逐字段人工确认。

## 4. 领域 Profile 与元类型状态模型

### 4.1 状态模型定义

| 模型代码 | 适用对象 | 允许状态 |
|---|---|---|
| DOC | AuthorityAsset 中的规范、规格、计划、策略、目录、登记册和清单 | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| CASE | 问题、风险、假设、依赖、异常、事故、改进行动和其他工作项 | Open、In Progress、Blocked、Resolved、Closed、Reopened、Cancelled |
| EXEC | Agent Run、验证、发布、评审和其他执行实例 | Planned、Ready、Running、Blocked、Completed、Failed、Accepted、Rejected、Cancelled |
| EVID | 证据及证据集合 | Planned、Collected、Under Review、Accepted、Rejected、Invalidated |
| DEC | 决策、批准、门禁、例外、豁免和风险接受 | Proposed、Under Review、Approved、Conditionally Approved、Rejected、Waived、Superseded、Expired |
| REC | 已发生事实的不可变记录、日志、快照和版本记录 | Recorded、Corrected、Superseded、Archived |

### 4.2 状态语义

| 状态 | 统一语义 |
|---|---|
| Draft | 内容正在编制，禁止作为正式执行约束 |
| In Review / Under Review | 已提交评审，内容尚未批准 |
| Changes Required | 评审发现必须修正的问题，返回 Owner 处理 |
| Approved | 内容已由授权人批准，但尚未纳入基线 |
| Baselined | 已纳入明确 Baseline，后续修改必须执行变更控制 |
| Rejected | 当前候选内容、证据、执行结果或决议未被接受 |
| Superseded | 已由新资产或新修订替代，禁止作为当前默认输入 |
| Retired | 不再适用且没有直接替代对象，保留历史与血缘 |
| Open | 已登记且需要处理 |
| In Progress | 责任人正在处理 |
| Blocked | 因明确阻塞条件无法继续，必须记录阻塞原因和解除责任人 |
| Resolved | 已形成解决结果，等待复核或关闭 |
| Closed | 已复核完成且无需继续处理 |
| Reopened | 关闭后发现新证据或解决结果无效，重新进入处理 |
| Cancelled | 经授权停止处理，必须保留原因 |
| Planned | 执行范围、输入或方式正在计划 |
| Ready | 执行前置条件和授权已经满足 |
| Running | 执行已经开始但尚未产生最终结果 |
| Completed | 执行动作结束，等待接受判断 |
| Failed | 执行未达到规定完成条件 |
| Accepted | 证据或执行结果已经通过独立复核 |
| Collected | 证据已经捕获但尚未复核 |
| Invalidated | 曾有效的证据因环境、输入、版本或方法变化而失效 |
| Proposed | 决策候选已提出但未评审 |
| Conditionally Approved | 在规定条件、责任人和期限内临时批准 |
| Waived | 在明确范围和期限内豁免门禁或规则，不表示要求已满足 |
| Expired | 决策、授权或豁免超过有效期 |
| Recorded | 已发生事实已按要求捕获，禁止直接覆盖 |
| Corrected | 原记录存在错误，已通过新记录更正并保留原值 |
| Archived | 已移出活动集合并按保留规则保存 |

### 4.3 状态转换规则

```text
DOC:  Draft → In Review → Approved → Baselined → Superseded/Retired
                    ↘ Changes Required → Draft
                    ↘ Rejected

CASE: Open → In Progress → Resolved → Closed
              ↕ Blocked          Closed → Reopened → In Progress
              ↘ Cancelled

EXEC: Planned → Ready → Running → Completed → Accepted/Rejected
                    Running ↔ Blocked
                    Running → Failed/Cancelled

EVID: Planned → Collected → Under Review → Accepted/Rejected
                                      Accepted → Invalidated

DEC:  Proposed → Under Review → Approved/Conditionally Approved/Rejected/Waived
                              Approved/Conditionally Approved/Waived → Superseded/Expired

REC:  Recorded → Corrected/Superseded → Archived
```

强制转换控制：

1. 每次状态转换必须记录原状态、新状态、时间、执行者、依据和适用修订。
2. Approved、Conditionally Approved、Waived、Accepted 和 Baselined 必须由授权的人类角色决定。
3. Agent 禁止批准自身产生的高风险输出。
4. Baselined 内容禁止退回 Draft；必须创建 Change Request 和新修订。
5. REC 对象禁止原位修改；更正时必须创建更正记录并保留原记录。
6. Superseded、Retired、Rejected、Cancelled、Invalidated 和 Expired 状态的资产禁止作为当前默认上下文。
7. Conditionally Approved 和 Waived 必须记录条件、责任人、失效时间和复核计划。
8. 状态字段未知时必须报错，禁止使用“其他”“处理中”“已完成”等未受控值。

### 4.4 元类型专属状态

| 元类型 | 受控状态或结果 |
|---|---|
| TaskContract | Draft、Ready、Frozen、Superseded |
| RunLedger | 事件状态 `started/succeeded/failed/blocked/skipped/recorded`；账本自身只追加，不设置终态 |
| TaskOutcome | Implemented、Deferred、Cancelled、Blocked、Superseded |
| ProjectState | `generated=true`；完整性由 Source Digest 验证 |
| AuthorityAsset | 使用其 Profile 对应 DOC/CASE/EVID/DEC/REC/EXEC 状态 |
| DerivedView | Complete、Incomplete、Stale、Failed |

## 5. C01 产品发现、证据与意图领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| SNR | Stakeholder Need Record | CASE | 利益相关方或用户群、原始陈述、使用情境、期望结果、来源日期、Evidence 引用、假设、置信度 |
| EVD | Evidence Record | EVID | 证据类型、来源、收集日期与方法、可观察事实、样本或覆盖范围、局限性、可靠性等级、关联 Need 与 Problem |
| PRB | Problem Definition | DOC | 受影响对象、当前情境、期望情境、可量化影响、已知原因、待验证原因、Evidence 引用、排除项 |
| PDF | Product Definition | DOC | 目标用户、核心需要、价值主张、产品边界、主要能力、非目标、使用情境、外部约束、长期责任人 |
| PIG | Product Intent & Goal Record | DOC | Problem 引用、期望变化、目标用户、可观察成功指标、护栏指标、时间范围、约束、目标负责人 |
| ASM | Assumption Register | DOC | Assumption ID、陈述、来源、影响、置信度、验证方法、验证期限、验证责任人、失效条件、结果状态 |

## 6. C02 建设事项与范围领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| INI | Initiative Brief | DOC | 关联 Intent 与 Goal、Problem 摘要、预期结果、价值假设、优先级、计划时间范围、启动与终止条件 |
| SCP | Scope Boundary Record | DOC | In Scope、Out of Scope、Future Scope、受影响用户与模块、允许 Agent 修改边界、禁止修改项、例外审批方式 |
| ACR | Assumption & Constraint Register | DOC | 成员类型、陈述、来源、影响、验证或解除条件、责任人、期限、关联 Risk 与 Scope |
| RSK | Risk Register | DOC | Risk ID、类别、描述、原因、影响、可能性、严重度、处理方式、触发条件、风险责任人、剩余风险、成员状态 |
| SMP | Success Metric Plan | DOC | 关联 Goal、指标定义、计算方式、数据来源、基线值、目标值、护栏值、观察周期、责任人、判定规则 |
| DEP | Dependency Register | DOC | Dependency ID、依赖对象、依赖类型、提供方、需要日期、满足条件、失败影响、替代方案、责任人、成员状态 |

## 7. C03 PRD 与 Feature 领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| PRD | PRD Package | DOC | 所属 Product、Initiative 与 Goal、背景与 Problem 摘要、用户和角色、Scope 与 Non-goal、Feature 列表、Requirement Index、质量属性、Risk 与 Dependency、验收边界、目标发布、开放问题、评审与 Baseline 引用 |
| FTR | Feature Record | DOC | 所属 PRD、用户可感知能力、目标用户和场景、用户价值、业务价值、Scope、Requirement 引用、优先级、Dependency |
| USC | User Scenario Set | DOC | 目标用户、使用情境、触发事件、前置条件、主流程、替代流程、异常流程、期望结果、关联 Feature 与 Requirement |
| NGR | Non-goal Register | DOC | Non-goal ID、排除内容、排除理由、适用范围、未来重新评估条件、责任人、关联 Scope |
| DCR | Dependency & Constraint Register | DOC | 成员类型、陈述或依赖对象、来源、影响范围、满足或解除条件、责任人、期限、关联 PRD 与 Requirement |
| RQI | Requirement Index | DOC | Requirement ID、标题、类型、所属 Feature、当前修订、状态、优先级、验证方法、Acceptance 引用 |
| QAS | Quality Attribute Summary | DOC | 质量属性、业务理由、适用场景、测量指标、阈值、环境条件、优先级、验证策略、关联 Requirement |

## 8. C04 原子需求与需求演进领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| REQ | Requirement Record | DOC | 规范性陈述、类型、业务理由、所属 PRD 与 Feature、目标用户或责任主体、前置与适用条件、优先级或关键程度、验证方法、Acceptance 引用、Risk 或 Assumption、上下游追踪 |
| RQS | Requirement Set | DOC | 集合边界、成员 Requirement、完整性依据、一致性检查、覆盖结论、整体可行性、确认结果、适用 Baseline |
| CPE | Clarification or Patch Event | REC | 关联 Requirement、触发问题、原文本、澄清或修补内容、不改变独立义务的判定依据、影响分析、新快照、记录者 |
| RRV | Requirement Revision | REC | Requirement ID、原修订、新修订、变更内容、同一业务意图判定、原因、影响、Change Request 引用、批准与生效时间 |
| RSP | Requirement Supersession Record | REC | 原 Requirement、新 Requirement、替代类型、生效边界、理由、迁移影响、未完成下游处理、批准人、生效时间 |
| RQR | Requirement Quality Review | EXEC | 被评审 Requirement 或 Set、质量准则、逐项结果、问题列表、评审者、结论、整改要求、复核结果 |
| RCL | Requirement Classification Record | DEC | 被分类对象、候选类型、最终分类、判定依据、身份处理、所需控制流程、决定者、决定时间 |

## 9. C05 验收、验证与确认领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| ACS | Acceptance Criteria Set | DOC | 集合边界、关联 Requirement、Criterion ID、前置条件、触发行为、预期与可观察结果、数据和环境条件、适用角色、优先级、验证方法、自动化状态 |
| VFS | Verification Strategy | DOC | 验证范围、Requirement 分类、方法选择、环境、工具、独立性、覆盖目标、进入与退出条件、失败处理、证据要求 |
| VLS | Validation Strategy | DOC | Need、Intent 与 Goal 范围、目标用户、真实使用情境、确认方法、样本或参与者、成功与护栏条件、伦理与隐私约束、接受责任人 |
| TCR | Test Case or Check Reference | DOC | 外部 Test/Check ID、来源系统、关联 Requirement 与 Criterion、版本、执行入口、维护责任人、当前有效性 |
| VER | Verification Evidence Record | EVID | 关联 Requirement 与 Criterion、执行方式、环境、输入、实际与预期结果、通过/失败/阻塞、执行者、时间、原始日志或产物、复核状态 |
| VAE | Validation Evidence Record | EVID | 关联 Need、Intent 与 Goal、参与者和情境、方法、观察结果、成功指标结果、偏差与局限、原始材料、复核和确认结论 |
| ACD | Acceptance Decision | DEC | 接受范围、关联 Verification 与 Validation Evidence、未通过项、剩余风险、决定、条件、批准人、生效与失效时间 |
| VCM | Coverage Matrix | DOC | Requirement、Acceptance Criterion、验证方法、Test/Check、Evidence、结果、覆盖状态、缺口责任人和关闭期限 |

## 10. C06 UX 与技术设计规格领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| UXD | UX Design Specification | DOC | 关联 PRD、Feature 与 Requirement、用户与情境、主流程和异常流程、页面与组件、交互状态、内容规则、权限差异、响应式与无障碍规则、原型引用、评审状态 |
| UFS | User Flow and State Model | DOC | 用户角色、入口、步骤、决策分支、系统状态、空/加载/错误/无权限/恢复状态、退出条件、关联 Requirement |
| PCI | Page and Component Inventory | DOC | 页面或组件 ID、名称、职责、所属流程、输入与输出、状态、权限、复用边界、关联 Requirement 与设计版本 |
| TDS | Technical Design Specification | DOC | 关联 Requirement、系统边界、受影响组件、数据流与状态、接口、数据模型概念、权限与安全、异常/重试/幂等/一致性、性能与容量、迁移与回滚、可观测性、测试策略、Decision 与 Risk 引用 |
| SCV | System Context or Component View | DOC | 视图目的、利益相关方关注点、系统边界、组件与外部实体、关系、数据或控制流、图例、适用版本、对应 Decision |
| IFC | API or Interface Contract | DOC | 提供方与使用方、操作或事件、输入、输出、错误、权限、幂等性、版本兼容、性能约束、变更规则、验证方法 |
| DSM | Data and State Model | DOC | 业务实体或状态、语义、关系、约束、状态转换、一致性要求、数据所有者、保留规则、关联 Requirement；禁止在本蓝图阶段规定物理 Schema |
| PEM | Permission Model | DOC | 主体、资源、动作、条件、默认拒绝规则、授权来源、职责分离、审计要求、异常与撤销、验证方法 |
| DCM | Design Coverage Matrix | DOC | Requirement、UX 元素、Technical Design 元素、无需设计理由、设计版本、评审状态、缺口责任人 |
| DCT | Design Constraint Record | CASE | 约束陈述、来源、适用设计范围、影响、替代方案限制、解除条件、责任人、关联 Decision 与 Risk |

## 11. C07 人机协作与职责领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| COL | Collaboration Contract | DOC | 参与者、协作目标、Agent 角色、输入输出边界、权限、审批点、禁止项、停止条件、升级路径、有效期、人类责任人 |
| RMA | Responsibility Matrix | DOC | 活动或产物、Responsible、Accountable、Consulted、Informed、审批人、职责冲突检查、适用范围 |
| ARD | Agent Role Definition | DOC | Agent 角色与用途、可访问 Context、可用工具、读写范围、允许环境、最大修改范围、必须批准事件、禁止操作、风险等级、人类责任人与审核人、授权有效期 |
| APM | Approval Matrix | DOC | 操作或产物、风险等级、提交者、批准角色、独立性要求、所需证据、时限、替代批准路径 |
| ESP | Escalation Protocol | DOC | 触发条件、严重度、停止动作、通知对象、响应时限、所需信息、决策权限、恢复条件 |
| STC | Stop Condition Register | DOC | Stop Condition ID、触发信号、适用 Agent 与 Scope、立即动作、禁止继续事项、升级对象、恢复批准条件、成员状态 |
| EXA | Exception Authorization | DEC | 例外规则、适用 Scope、理由、风险、补偿控制、申请人、批准人、生效与失效时间、复核计划、撤销条件 |

## 12. C08 Agent 上下文治理领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| SCM | Stable Context Manifest | DOC | Context ID、来源资产与版本、责任人、生成与有效时间、优先级、可信与敏感级别、内容摘要或指针、完整性校验、替代或失效关系 |
| ECP | Execution Context Package | DOC | 当前 Requirement、Scope、Task、工作区快照、工具输入、临时 Assumption、允许操作、有效 Run、生成时间、敏感级别、失效条件 |
| CSR | Context Source Register | DOC | Source ID、来源类型、所有者、权威级别、获取方式、版本方式、新鲜度规则、信任边界、访问分类、成员状态 |
| CPP | Context Precedence Policy | DOC | 上下文类别、优先级、冲突规则、不得覆盖对象、例外审批、外部内容处理、适用范围、策略责任人 |
| CCR | Context Change Record | REC | Context ID、原版本、新版本、变化内容、原因、影响 Run 与 Requirement、批准人、生效时间、失效旧版本 |
| CFR | Context Freshness Report | DOC | 检查时间、Context 清单、来源版本、有效期、新鲜度结论、过期项、影响范围、处置责任人和期限 |
| CCF | Context Conflict Report | CASE | 冲突 Context、冲突陈述、各自优先级与版本、受影响任务、风险、暂停动作、解决决定、责任人、关闭条件 |

## 13. C09 Agent 执行与证据领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| AEP | Agent Execution Plan | DOC | 关联 Requirement、Scope 与 Context、理解摘要、计划步骤、工具、修改范围、验证方式、回滚方式、审批点、停止条件、剩余假设 |
| RUN | Agent Run Record | EXEC | Agent 角色、模型或执行引擎标识、开始与结束时间、关联 Requirement/Scope/Context、理解摘要、计划引用、工具与动作、修改资产、提交或差异、命令、验证结果、失败与重试、未解决问题、剩余风险、人类复核、最终状态 |
| TIL | Tool Invocation Log | REC | Run ID、调用顺序、工具、时间、输入摘要、权限上下文、输出摘要、退出状态、原始日志引用、敏感信息处理、关联动作 |
| CAS | Changed Artifact Summary | REC | Run ID、资产 ID、原修订、新修订、变化摘要、变化原因、Requirement 或 Engineering Change 来源、影响、差异引用 |
| CCS | Code Change Summary | REC | Run ID、仓库与提交、文件或组件、代码变化、行为影响、关联 Requirement/Design/Decision、测试结果、迁移与回滚影响 |
| VDR | Validation Report | DOC | Run ID、验证范围、方法、环境、命令、预期与实际结果、通过/失败/阻塞、原始 Evidence、未验证项、结论、复核人 |
| FER | Failure or Exception Report | CASE | Run ID、失败时间与步骤、症状、错误证据、影响、已执行重试、回滚结果、临时处置、根因状态、升级与后续行动 |
| HRR | Human Review Record | EXEC | 被评审 Run 与变更、评审者、独立性、评审范围、Evidence、发现项、结论、整改要求、接受或拒绝结果、时间 |
| RRS | Residual Risk Statement | DEC | Run 或发布范围、剩余 Risk、影响与可能性、已有控制、接受条件、责任人、批准人、监控与失效时间 |

## 14. C10 决策、追踪与资产血缘领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| DEC | Decision Record | DEC | 类型、背景、决策问题、候选方案、选择、理由、影响、Risk、参与者、决定日期、关联资产、替代或被替代关系 |
| TLR | Trace Link Register | DOC | Link ID、源资产、受控关系类型、目标资产、建立依据、建立者、时间、成员状态、有效版本范围 |
| BTM | Bidirectional Traceability Matrix | DOC | 上游资产、关系、下游资产、正向查询、反向查询、适用版本、覆盖状态、缺口与责任人 |
| RCR | Requirement Coverage Report | DOC | Requirement 总数、按类型和关键度的覆盖数、来源/设计/实现/验证/发布覆盖率、孤立项、阈值、结论、统计时间 |
| ALR | Asset Lineage Report | DOC | 目标资产、来源、派生、生成、实现、验证、替代、观察与发布链路、版本边界、断链、生成时间 |
| UCR | Untracked Change Report | CASE | 代码或资产变化、发现方式、仓库与版本、缺失来源、潜在影响、责任人、处置决定、补链或回退期限 |
| OAR | Orphan Artifact Report | CASE | 孤立资产、资产类型、缺失上游或下游关系、当前状态、影响、责任人、处置方式、关闭条件 |
| IQR | Impact Query Result | REC | 查询对象与版本、查询时间、关系范围、受影响资产、直接与间接影响、未知项、查询规则、执行者、结果完整性 |

## 15. C11 配置、版本、基线与变更控制领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| IDP | Identifier Policy | DOC | 命名空间、产物类型代码、编号分配、唯一性、禁止复用、废弃处理、迁移规则、责任角色 |
| CIR | Configuration Item Register | DOC | Configuration Item ID、类型、名称、位置、Owner、当前修订与状态、Baseline、访问与保留分类、成员状态 |
| VRR | Version or Revision Record | REC | 资产 ID、原版本或修订、新版本或修订、变化摘要、原因、作者、时间、批准、快照或提交引用 |
| SNP | Snapshot Record | REC | 资产 ID、快照标识、捕获时间、内容位置、完整性校验、创建者、对应修订、不可变性控制 |
| BSL | Baseline Record | DEC | Baseline ID、目的、范围、包含资产与版本、批准人、生效时间、状态、完整性校验、后续替代 Baseline |
| CHG | Change Request | CASE | 提出者、原因、触发事件、受影响资产、原状态、建议状态、Impact Analysis、Risk、计划版本、审批人、Decision、实施与验证状态 |
| IMA | Impact Analysis | DOC | Change 引用、分析范围、受影响 Need/Requirement/Design/Code/Test/Release/Context、兼容和迁移影响、Risk、成本与时序、未知项、建议 |
| CHD | Change Decision | DEC | Change Request、Impact Analysis、候选处置、决定、理由、条件、批准人、计划 Baseline 与版本、生效或失效时间 |
| RLC | Release Configuration Record | REC | Release ID、环境、包含 Requirement/Design/Code/Config/Evidence 版本、构建与提交、部署时间、批准、回滚版本、完整性校验 |
| SRR | Supersession and Retirement Record | REC | 原资产、替代资产或无替代说明、原因、生效范围与时间、迁移处理、保留位置、批准人、下游通知 |

## 16. C12 评审、质量门禁与产品健康领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| RVR | Review Record | EXEC | 评审类型、对象与版本、评审输入、评审者与角色、准则、发现项、结论、整改行动、复核结果、时间 |
| QGC | Quality Gate Checklist | DOC | Gate 类型、检查项、判定规则、必须 Evidence、阻断级别、例外规则、责任角色、适用版本 |
| GTE | Gate Decision | DEC | Gate 类型、对象与版本、检查结果、未满足项、Risk、通过/条件通过/拒绝/豁免决定、条件、批准人、失效时间 |
| EWR | Exception or Waiver Record | DEC | 被偏离规则或门禁、Scope、理由、Risk、补偿控制、责任人、批准人、生效与失效时间、复核和撤销条件 |
| RAR | Risk Acceptance Record | DEC | Risk、影响范围、当前控制、剩余 Risk、接受理由、责任人、批准人、监控指标、复核与失效时间 |
| PHR | Product Health Report | DOC | 报告范围与周期、指标定义、数据来源、阈值、当前值、趋势、异常、Risk、结论、行动、报告责任人 |
| RTR | Retrospective Record | EXEC | 回顾范围、参与者、目标与实际结果、成功、偏差、事故和反馈、原因、学习、Decision 与行动、时间 |
| IAP | Improvement Action Plan | DOC | Action ID、来源学习或问题、目标、行动内容、优先级、责任人、期限、成功条件、依赖、成员状态、关闭证据 |

## 17. E01 架构治理扩展领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| ARC | Architecture Description | DOC | 系统标识、利益相关方、关注点、架构视点、模型、原则、边界、关键 Decision、适用版本、已知限制 |
| SCR | Stakeholder and Concern Register | DOC | Stakeholder、角色、Concern、重要度、相关视点、责任人、处置状态、关联 Requirement 与 Risk |
| VPC | Viewpoint Catalog | DOC | Viewpoint ID、名称、目标 Stakeholder、Concern、模型类型、建模约定、检查规则、适用范围 |
| AMS | Architecture Model Set | DOC | 模型 ID、Viewpoint、系统范围、元素、关系、假设、版本、来源、完整性和一致性检查 |
| AFC | Architecture Fitness Criteria | DOC | 架构特性、场景、指标、阈值、环境、测量方法、频率、Owner、失败处置 |
| ADR | Architecture Decision Record | DEC | 架构 Concern、背景、候选方案、选择、理由、质量属性影响、Risk、迁移影响、批准人、替代关系 |
| AER | Architecture Evolution Roadmap | DOC | 当前状态、目标状态、阶段、依赖、兼容策略、迁移步骤、退出与回滚策略、里程碑、Risk、Owner |
| ACV | Architecture Conformance Review | EXEC | Architecture Baseline、被评审实现、Criteria、Evidence、偏差、Risk、结论、豁免、整改和复核 |

## 18. E02 安全、隐私与合规扩展领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| SRS | Security Requirement Set | DOC | 资产与威胁来源、Requirement、控制目标、适用组件、风险等级、Acceptance、验证方法、例外 |
| THM | Threat Model | DOC | Scope、资产、信任边界、威胁主体、威胁场景、攻击路径、已有控制、Risk 评级、处理和剩余 Risk |
| SAR | Security Architecture | DOC | 安全边界、身份与访问、密钥与秘密、数据保护、网络与组件控制、日志监控、Decision、验证和更新规则 |
| PII | Privacy and PII Register | DOC | 数据类别、个人信息类型、数据主体、来源、目的、合法依据责任、存储位置、访问、共享、保留、删除、Owner |
| PIA | Privacy Impact Assessment | DOC | 处理活动、目的与必要性、数据主体、数据流、隐私 Risk、影响、控制、咨询与批准、剩余 Risk、复核触发条件 |
| COR | Compliance Obligation Register | DOC | 义务来源、司法辖区或组织范围、要求摘要、适用资产、责任人、Evidence、状态、复核日期；禁止由本记录代替法律结论 |
| SVP | Security Verification Plan | DOC | ASVS 或其他控制基线与版本、验证范围、级别、方法、环境、工具、独立性、证据、阈值、失败处置 |
| VUR | Vulnerability and Remediation Record | CASE | 漏洞来源、受影响资产与版本、严重度、利用条件、Evidence、处置、责任人、期限、修复版本、复测和披露状态 |
| AIA | AI Impact Assessment | DOC | AI 用途、受影响个人或群体、预期收益、潜在伤害、数据与模型限制、人类监督、控制、监控、批准和复核触发条件 |

## 19. E03 数据与 AI 数据治理扩展领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| DRS | Data Requirement Set | DOC | 业务用途、数据主体或对象、语义、来源、质量、时效、访问、保留、隐私、Acceptance 与验证 |
| DCO | Data Contract | DOC | 提供方、使用方、数据集或事件、Schema 概念、语义、质量 SLO、版本兼容、变更通知、责任人、验证 |
| DDY | Data Dictionary | DOC | 数据项、业务定义、数据类型概念、允许值、单位、来源、Owner、敏感级别、质量规则、关联资产 |
| DQS | Data Quality Specification | DOC | 质量维度、业务 Risk、指标、计算方式、数据源、阈值、测量周期、Owner、失败处置 |
| DLG | Data Lineage | DOC | 数据资产、来源、转换、使用方、版本、处理责任人、时间范围、质量影响、断链和验证 |
| DSR | Dataset or Corpus Record | DOC | 用途、来源、获取方式、许可或使用限制、时间与覆盖范围、代表性、标签、敏感信息、版本、质量、保留与删除 |
| ADQ | AI Data Quality Report | DOC | Dataset 版本、用途、质量指标与结果、代表性、偏差、缺失、污染、限制、Risk、结论和行动 |
| RDR | Data Retention and Disposal Rule | DOC | 数据类别、保留依据、保留期限、归档、删除或匿名化方式、Legal Hold、责任人、Evidence、例外 |
| DIR | Data Issue and Remediation Record | CASE | 数据问题、发现来源、受影响数据与使用方、质量维度、影响、根因、临时控制、修复、责任人、验证和关闭条件 |

## 20. E04 知识与正式记录治理扩展领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| KAC | Knowledge Asset Catalog | DOC | Knowledge ID、类型、名称、来源、Owner、版本、有效状态、访问、保留、新鲜度、替代关系 |
| VOC | Controlled Vocabulary | DOC | 术语、正式名称、定义、禁止同义词、适用范围、Owner、批准版本、替代术语 |
| SPR | Source and Provenance Register | DOC | Source ID、来源主体、获取方式、时间、版本、可信级别、许可或使用限制、关联知识、完整性、成员状态 |
| RCS | Record Classification Scheme | DOC | 记录类别、业务用途、敏感级别、完整性要求、Owner、保留规则、访问角色、处置方式 |
| RTS | Retention Schedule | DOC | 记录类别、起算事件、保留期限、依据、归档位置、Legal Hold、处置方式、批准人、复核周期 |
| KFR | Knowledge Freshness Report | DOC | 检查范围与时间、Knowledge 版本、最后复核时间、新鲜度规则、过期或冲突项、影响、责任人与期限 |
| SKR | Superseded Knowledge Register | DOC | 旧 Knowledge、新 Knowledge、替代原因、生效时间、受影响 Context、迁移处理、保留位置、成员状态 |
| RAP | Retrieval and Access Policy | DOC | 知识分类、允许角色、检索范围、最小披露、来源与新鲜度显示、敏感过滤、日志、拒绝和例外规则 |

## 21. E05 产品运营与服务管理扩展领域 Profile

| Profile 代码 | 领域 Profile 名称 | 状态模型 | Profile 专属必填信息 |
|---|---|---|---|
| SDF | Service Definition | DOC | 服务对象、价值、Scope、Owner、用户、依赖、环境、支持时间、质量目标、数据与安全分类、退出条件 |
| SLO | SLI/SLO Register | DOC | SLI 名称、定义、计算、数据源、SLO 目标、窗口、错误预算、Owner、告警与处置、成员状态 |
| RBP | Release and Rollback Plan | DOC | Release Scope、包含版本、环境、步骤、前置检查、观察指标、停止与回滚条件、回滚步骤、责任人与批准 |
| MAP | Monitoring and Alert Plan | DOC | 监控对象、指标或事件、数据源、阈值、严重度、通知、响应时限、Runbook、Owner、测试周期 |
| INR | Incident Record | CASE | 事件时间线、服务与版本、严重度、用户影响、发现来源、响应动作、恢复时间、Evidence、责任人、根因状态、后续行动 |
| PBR | Problem Record | CASE | 关联 Incident 或趋势、Problem 描述、业务影响、根因分析、已知错误、临时措施、永久处理、责任人、关闭条件 |
| OPO | Operational Observation | EVID | 服务与 Release、观察时间、环境、指标或行为、原始数据、预期差异、影响、可靠性、关联 Requirement |
| UFR | User Feedback Record | CASE | 用户或群体、渠道、时间、原始反馈、使用情境、影响、Evidence、分类、关联 Need/Problem/Requirement、处置状态 |
| PRR | Post-release Review | EXEC | Release、观察周期、目标指标、实际结果、缺陷与 Incident、用户反馈、剩余 Risk、结论、Decision 与行动 |
| IBL | Improvement Backlog | DOC | Improvement ID、来源、问题或机会、预期结果、优先级、责任人、目标时间、关联 Initiative、成员状态、关闭 Evidence |

## 22. 元类型与 Profile 完整性检查

正式规范生成前和 V6.3 Candidate 评审前必须自动检查：

1. 正式元类型严格等于六类，禁止建立第七类。
2. VC-PPG-BP-002 每个“必须治理的对象”均能在 137 个 Profile 中唯一定位。
3. 每个 Profile 代码唯一、未复用且通过 VC-PPG-MAP-001 唯一映射到一个元类型。
4. 137 个 Profile 同时具有通用信息和专属信息，映射覆盖率必须为 137/137。
5. 每个 Profile 只使用一个领域状态模型；元类型状态、成员状态与 Profile 状态分开记录。
6. P1 合并载体和蓝图集合简称未被创建为平行 Profile 或新元类型。
7. 每个批准或基线状态存在人类批准记录。
8. 每个被替代或失效资产保留历史、来源和替代关系。
9. 不存在空白但未说明“不适用”的必填信息。
10. `project-state.json`能够从 TaskOutcome 和 AuthorityAsset 重建，生成内容未被直接维护。
11. 不存在未经 Change、Impact 和评审登记的新 Profile 或元类型。

## 23. 产物实例动作

| 动作 | 使用条件 | 最低记录 |
|---|---|---|
| Create/Revise | Task Profile 触发控制目标，且没有可直接继承的有效实例或现有实例必须变更 | Meta Type、Legacy Kind/Profile、原因、Owner、Scope、计划 Revision、上游来源 |
| Reference | 已批准且未变化的 Baseline 资产完整覆盖当前任务 | Asset ID、Revision/Snapshot、Baseline、适用范围、有效性检查 |
| Generate | Gate、审计、查询或评审需要派生视图 | 查询规则、来源资产、Source Snapshot、生成时间、结果完整性 |
| On Event | 事件、执行、失败、评审、决定或观察实际发生 | 事件来源、时间、主体、范围、事实 Evidence；未发生时不创建空记录 |
| N/A | Task Profile 与 VC-PPG-TAIL-001 明确判定不适用 | 规则引用、事实依据、Scope、Owner 和重新评估触发点；Unknown、High/Critical 无独立依据或扩展触发冲突时禁止使用 |

### 23.1 动作与 State 分离

实例动作只回答当前任务如何处理某个元类型/Profile，不替代其受控状态。`Reference` 不改变被引用资产状态，`Generate` 不允许覆盖权威来源，`On Event` 不允许预先生成虚构事实。

### 23.2 Artifact Manifest 最低信息

Artifact Manifest 是 `before.json` 和 `after.json` 中的受控字段，不再要求单独物理文件。它必须记录 TaskID、Source Snapshot、Meta Type、Legacy Kind/Profile、实际动作、规则引用、Owner、未决问题和人类确认引用。Manifest 不复制全部 137 行 Profile；未列项必须能通过 VC-PPG-IDX-001 和 VC-PPG-MAP-001 得到唯一结论。

### 23.3 逻辑身份与物理载体

多个 AuthorityAsset 可以共用一个原生物理载体。载体必须为每个逻辑对象保留独立标题或结构边界、Asset ID、Meta Type、Legacy Kind/Profile、State、Revision、Owner、Scope、Trace 和 History。拆分或合并载体不自动产生新业务身份。TaskContract、RunLedger 和 TaskOutcome 必须保持每个 TaskID 的固定三文件边界。

### 23.4 相似类型边界

1. VCM、DCM、BTM、RCR、ALR 是 DerivedView Profile，是同一 Trace Link Register/关系图在验证覆盖、设计覆盖、双向追踪、需求覆盖和资产血缘范围下的派生视图。
2. VER、VAE 是 AuthorityAsset 中的权威验证/确认证据；VDR 是按 Run 生成的 DerivedView。
3. CAS、CCS、FER 的任务级事实进入 TaskOutcome；旧代码作为 `legacy_kind` 保留。CCS 只在存在代码变化时生成。
4. ECP、AEP 的执行前信息进入 TaskContract；RUN、TIL 的必要事件进入 RunLedger。迁移时不得恢复逐工具调用的全量日志要求。
5. EXA 只授权超出正常 Agent 权限的动作；EWR 只批准对规范或 Gate 的偏离；RRS 陈述剩余风险；RAR 才表示具有人类 Authority 的风险接受。
6. COL 定义协作契约；RMA 分配 Accountability；ARD 定义 Agent 角色权限；APM 定义批准规则。共同字段引用第 3 章，不得在四个 Profile 中建立含义不同的平行字段。
