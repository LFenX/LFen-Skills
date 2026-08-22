# C07 人机协作与责任规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C07 |
| 英文名称 | Human-Agent Collaboration and Responsibility Specification |
| 正式文件名 | `C07_Human_Agent_Collaboration_Standard.md` |
| 版本 | V0.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V0.3、C02 V0.3、C03 V0.3、C04 V0.3、C05 V0.3、C06 V0.3 |
| 生产前调研 | RVR-C07-0001 |
| 下游规范 | C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式角色、责任、授权、批准、停止、升级、恢复、撤销、例外、评审和历史记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定人类参与者、Coding Agent、Review Agent、Orchestrator Agent、工具、运行环境和外部服务之间的职责、问责、授权、批准、停止、升级、恢复和审计规则。

本规范用于实现以下控制目标：

1. 确保 Requirement、Architecture、Risk、Acceptance、Baseline、Gate、Release 和外部承诺的最终责任始终属于明确人类；
2. 区分 Agent 的 Capability、正式 Authorization、技术 Permission、特定 Approval 和人类 Accountability；
3. 使 Agent 只能在最小、明确、可撤销、可追踪且有时限的边界内行动；
4. 使 Autonomous、Approval Required、Prohibited 和 Not Assessed 操作可以确定性判定；
5. 使高影响、不可逆、破坏性、跨 Scope、安全、隐私、合规、生产和外部副作用操作获得有权人类批准；
6. 使需求、Context、Scope、授权、目标版本、风险或工具结果发生冲突时立即停止并升级；
7. 使多 Agent 分工不扩大权限、不形成自我批准、不发生未受控共享写入；
8. 使授权、批准、停止、升级、恢复、撤销和例外形成完整审计链。

## 3. 适用范围

本规范适用于：

- 人类与一个或多个 Agent 共同进行发现、规格、设计、实现、评审、验证、配置、发布准备和维护；
- Agent 对文件、仓库、代码、配置、数据、工具、命令、网络、外部系统和部署环境的读取或变更；
- Agent 生成 Draft、建议、分析、差异、代码、测试、报告或执行结果；
- Agent 之间的委派、编排、评审、验证、交接、共享 Context 和共享工作区；
- 人类提出任务、授予权限、批准动作、审查结果、接受风险、处理冲突或恢复执行；
- P2 档位下七类 C07 正式产物的身份、状态、必填信息、模板和质量检查；
- 目标产品对 E01 至 E05 扩展的适用性判定及扩展激活后的附加职责约束。

每个目标产品、Initiative、Agent Role、运行环境和生命周期阶段必须分别确定适用范围。开发环境授权不得自动延伸到测试、预发布、生产或外部服务。

## 4. 不适用范围

以下内容不由本规范定义：

- Need、Evidence、Problem、Product Definition、Intent 和 Goal 的发现规则，由 C01 管理；
- Initiative、Scope Boundary、Agent Modification Boundary、Assumption、Constraint、Risk 和 Metric，由 C02 管理；
- PRD、Feature、User Scenario、Non-goal、Dependency 和 Quality Attribute Summary，由 C03 管理；
- Requirement、Requirement Set、原子性、属性、Revision 和演进分类，由 C04 管理；
- Acceptance Criterion、Verification、Validation、Test/Check、Evidence 和 Acceptance Decision，由 C05 管理；
- UX Design、Technical Design、接口、数据、权限设计和 Design Ready，由 C06 管理；
- Agent Context 的选择、最小化、组装、新鲜度、隔离和失效，由 C08 管理；
- Agent Run、命令、Tool Call、代码修改、执行 Evidence、Validation Report 和运行日志，由 C09 管理；
- Decision、Traceability Matrix、Asset Lineage 和关系治理，由 C10 管理；
- Configuration Item、Snapshot、Baseline、Change Request 和 Release Configuration，由 C11 管理；
- Gate Decision、Exception or Waiver、Risk Acceptance 和 Product Health，由 C12 管理；
- 组织法定治理结构、劳动关系、采购合同、法律意见、监管解释或外部认证；
- 具体 Agent 框架、模型、身份系统、密钥系统、CI/CD、云平台或审计产品选型。

C07 的 Exception Authorization 只处理对 C07 协作与授权规则的有界例外，不替代 C02 Risk Acceptance、C10 Decision、C11 Change Approval 或 C12 Exception or Waiver。

## 5. 规范性用语

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性示例，不作为符合性判定依据。

### 5.2 C07 判定关键词

`Autonomous`、`Approval Required`、`Prohibited` 和 `Not Assessed` 是 Execution Permission Class，不是资产 State。

`Approve`、`Approve with Conditions`、`Reject` 和 `Defer` 是 Approval Outcome，不是资产 State。

`Collaboration Ready`、`Not Ready` 和 `Blocked` 是 Collaboration Readiness Conclusion，不是资产 State。

`Pass`、`Fail` 和 `Blocked` 是 Review Outcome，不是资产 State。

`Not Triggered`、`Triggered` 和 `Cleared` 是 Stop Trigger Status，不是 STC 或其成员 State。

### 5.3 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 有权人类发布的即时 Stop 指令；
3. 当前有效的 C02 Scope、Agent Modification Boundary 和不可覆盖 Constraint；
4. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
5. 本规范已批准或已基线版本中的“必须”“禁止”及第 10.17 节例外边界；
6. 对本规范指定“应”“不应”规则生效的已批准且未过期 EXA；
7. 当前任务的有效 Requirement、Design、Context、Snapshot 和 Run Plan；
8. 已批准且未过期的 COL、RMA、ARD、APM、ESP 和 STC；
9. Agent 生成的建议、推断或默认行为。

同一优先级冲突、来源有效性不明或无法判断适用范围时，必须停止受影响操作并按 ESP 升级。Agent 禁止自行选择更宽权限的解释。

### 5.4 可判定表达

授权与协作规则必须通过 Asset ID、Revision、Agent Role ID、Participant ID、对象路径或资源 ID、操作类别、环境、目标 Snapshot、最大修改范围、风险引用、批准事件、有效期、停止条件、升级目标和撤销条件直接判定。

禁止使用没有边界的“按需访问”“相关文件”“必要修改”“合理操作”“全权处理”“自行判断”“需要时上线”“长期有效”“默认批准”和通配范围。

### 5.5 规则标识与可例外性

本规范的编号规则按 `C07-<章节号>-<条目序号>` 引用，例如第 10.11 节第 3 项为 `C07-10.11-03`。表格规则使用章节号加表中唯一键引用。

只有使用“应”或“不应”的规则可以通过 EXA 申请偏离。使用“必须”或“禁止”的规则不可由 EXA 覆盖；需要改变时必须修订本规范或更高优先级治理输入。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| Human Participant | 以可验证身份参与任务、评审、授权、批准、决定或问责的人类 | 机器人账号、共享账号或未知操作者不属于明确人类 |
| Agent | 在给定 Context、工具和约束下生成内容或执行动作的软件主体 | 不是法律主体，也不承担本项目最终 Accountability |
| Agent Role | 对一类 Agent 的目的、输入、能力、工具、范围、限制、批准点和责任接口的受控定义 | 使用 ARD 管理；不是一次 Agent Run |
| Agent Instance | 在具体模型、版本、配置、会话和运行身份下工作的 Agent 实例 | 实际实例与 Run 由 C09 记录 |
| Coding Agent | 生成或修改规格、设计、代码、测试、配置或其他工作产品的 Agent Role | 不因名称获得写入或批准权 |
| Review Agent | 检查规则、差异、质量、风险或证据的 Agent Role | 不能替代必须由人类完成的独立评审或批准 |
| Orchestrator Agent | 分解任务、分派 Agent、汇总结果和协调交接的 Agent Role | 不能扩大自身或子 Agent 的授权 |
| Capability | Agent、模型或工具技术上能够执行的动作集合 | Capability 不构成 Authority、Authorization 或 Permission |
| Authority | 由治理、职位、合同或正式决定赋予人类角色的决定或授权权力 | 必须可定位来源、范围和有效期 |
| Authorization | 有权人类对指定 Agent Role 在指定条件内执行指定动作的正式授予 | 必须有 COL/ARD/APM 等受控依据 |
| Permission | 工具、身份、仓库、平台或环境实际强制执行的技术能力 | 必须是 Authorization 的子集 |
| Approval | 有权人类对一个准确动作、产物或决定在明确条件下作出的特定授权结果 | 不得通过沉默、默认值或 Agent 摘要推定 |
| Approval Evidence | 证明特定人类 Approval 的不可变记录或受控记录引用 | 是 APM/COL 字段，可指向适用 C09/C10/C11/C12 记录或权威系统事件；不是新增 C07 正式产物类型 |
| Accountability | 对结果、风险和决定承担最终解释与接受责任 | 每项高影响工作必须属于明确人类，禁止分配给 Agent |
| Responsibility | 执行、准备、检查、沟通或维护某项工作的职责 | Agent 可以在授权范围内承担 Responsible |
| Delegation | 人类或编排主体将有界任务及相应授权交给另一个参与者 | 不转移人类最终 Accountability |
| Least Privilege | 仅授予完成已批准任务所需的最小对象、动作、工具、环境、时长和变更规模 | 便利性不是扩大权限的理由 |
| Execution Permission Class | 对一个具体操作能否自主执行、需批准、禁止或尚未评估的判定 | 不表示 Risk Level 或 Approval Outcome |
| Approval Event | APM 规定必须在执行前由有权人类作出特定批准的事件 | 实际批准证据必须绑定目标 Revision/Snapshot |
| High-Impact Action | 对 Scope、Requirement、数据、权限、安全、隐私、合规、生产、外部主体、成本或不可逆结果产生显著影响的动作 | 具体风险等级引用 C02 Risk |
| External Side Effect | 对工作区外系统、数据、人员、客户、账户、资源、资金或公开渠道产生改变的动作 | 归入 External Mutation 或 Deploy 等 C02 操作类别 |
| Stop Condition | 一旦满足即禁止继续受影响操作并要求保存证据、通知和升级的可判定条件 | 使用 STC 登记 |
| Fail-Closed | 在授权、范围、目标、风险或控制无法确认时默认禁止继续 | 不能以时间压力改为默认允许 |
| Escalation | 将阻断信息提交给具有明确决定权的人类角色并等待受控决定 | Agent-to-Agent 转发不等于完成升级 |
| Resume Approval | Stop Condition 触发后，有权人类基于新鲜输入批准恢复的特定决定 | 禁止沿用已失效的旧批准 |
| Exception Authorization | 对 C07 某项规则在明确范围、期限和补偿控制下的受控偏离决定 | 使用 EXA 和 DEC State；不等于风险接受或 Gate Waiver |
| Independence | 评审者或批准者不受被评对象执行角色、自我利益和未声明冲突控制的条件 | 模型不同、会话不同不自动证明独立性 |
| Human-in-the-loop | 有权人类获得充分信息，并能在规定时限内批准、拒绝、停止或改变执行的控制安排 | 仅抄送人类或提供事后通知不满足本定义 |

`Agent Modification Boundary` 的唯一语义直接适用 C02；C07 只规定该边界内的 Authority、Permission、Approval、Stop 和职责分离控制。

## 7. 参与者与职责

### 7.1 人类角色

| 角色 | 强制职责 | 禁止缺口 |
|---|---|---|
| Human Accountable Owner | 对指定协作目标、产物、风险或动作承担最终 Accountability | 禁止填 Agent、团队名或未知共享账号 |
| Task Requester | 提供任务目的、期望结果、期限和已知限制 | 不得用任务描述隐式授予权限 |
| Product/Requirement/Design Owner | 对相应上游事实源、歧义和变更作出有权解释或发起正式决定 | 不得通过聊天覆盖当前 Baseline |
| Authorization Owner | 根据 Authority Source 建立、收缩、撤销 Agent Authorization | 不得授予自身不具备的 Authority |
| Approver | 对 APM 指定 Approval Event 作出具体 Approval Outcome | 必须核对对象、参数、风险、证据和有效期 |
| Independent Reviewer | 独立检查高风险输出、职责冲突、证据和控制有效性 | 不得是高风险变更的唯一执行者或唯一作者 |
| Agent Owner | 维护 Agent Role、模型/工具依赖、已知限制和复核周期 | 不得把供应商能力声明写成项目授权 |
| Context Owner | 确认 C08 Context 来源、最小化、新鲜度和敏感性边界 | 不得批准超出自身数据 Authority 的访问 |
| Tool/Environment Owner | 维护技术 Permission、环境隔离、撤销和审计能力 | 技术权限不得大于正式 Authorization |
| Risk Owner | 维护 C02 Risk、Treatment、Residual Risk 和触发条件 | 不得用 C07 EXA 代替 RAR |
| Security/Privacy/Compliance Authority | 对适用安全、隐私、合规和专业问题提供有权判断 | 未激活扩展时仍须处理已识别义务 |
| Escalation Coordinator | 接收升级、核对信息完整性、召集决策并记录响应 | 不得自行代替未拥有 Authority 的决定者 |
| Recovery Authority | 对停止后的恢复、回滚、降级或终止作出授权 | 恢复授权必须引用新鲜 Snapshot 和证据 |

同一人可以承担多个角色，但必须显式记录。高风险或 Critical 工作的职责分离必须满足 C05、C06、C11、C12 和已激活扩展中的更严格要求。

### 7.2 Agent 角色

| 角色 | 允许职责 | 固有限制 |
|---|---|---|
| Coding Agent | 在授权边界内生成 Draft、差异、实现、测试、报告和修复候选 | 不能批准自身输出、接受风险、批准例外或扩大 Scope |
| Review Agent | 按明确准则检查字段、追踪、差异、规则、风险信号和证据 | 不能充当高风险工作所要求的最终人类 Reviewer/Approver |
| Orchestrator Agent | 在授权范围内分解任务、分派子任务、收集结果和报告冲突 | 子 Agent 授权不得超过自身授权与子任务 Scope 的交集 |
| Observer Agent | 读取获准信息、监测信号、形成报告和升级候选 | 无写入、执行或外部变更权，除非 ARD/APM 单独授予 |

每个 Agent Role 必须有独立 ARD。角色名称不能授予权限；相同 Agent Instance 同时承担多个角色时按全部限制的交集执行。

### 7.3 RACI 规则

1. RMA 对每项活动和正式产物记录 Responsible、Accountable、Consulted、Informed、Reviewer 和 Approver。
2. Accountable 必须是一个可识别人类；每项活动或产物只能有一个最终 Accountable。
3. Responsible 可以有多个，人类或 Agent 均可承担；Agent 仅在有效 Authorization 内承担。
4. Consulted 和 Informed 不获得决定、批准或执行 Authority。
5. Reviewer 和 Approver 的独立性要求必须在 RMA/APM 中明确。
6. RMA 发现两个 Accountable、没有 Accountable、Agent 被列为 Accountable 或角色 Authority 冲突时，必须阻断 Collaboration Ready。

## 8. 治理对象与关系

### 8.0 V6.3 TaskContract 权限边界

“我被允许做什么”属于任务执行前输入，必须进入 TaskContract 的 `authority`、`scope`、`required_gates` 和 `stop_conditions`，不得等待任务结束后补写。Run 开始时这些字段冻结；后续权限扩大、范围变化或新 Gate 必须先停止受影响动作，并通过带 Authority 依据的 Amendment 修订。

TaskOutcome 只引用实际使用的权限、发生的人类决定和未决 Gate，不复制完整协作策略。COL、RMA、ARD、APM、ESP、STC、EXA 继续作为 AuthorityAsset Profile 保存长期规则。

### 8.1 七类正式产物

| 类型代码 | 正式产物 | 唯一责任 |
|---|---|---|
| COL | Collaboration Contract | 定义一次受控协作的参与者、目标、边界、权限、批准点、禁止项、停止、升级和有效期 |
| RMA | Responsibility Matrix | 定义活动与产物的 RACI、Reviewer、Approver、职责分离和冲突检查 |
| ARD | Agent Role Definition | 定义 Agent Role 的目的、Context、工具、读写范围、环境、最大修改、批准点和限制 |
| APM | Approval Matrix | 定义操作或产物的风险、提交人、批准角色、独立性、证据、时限和替代路线 |
| ESP | Escalation Protocol | 定义升级触发、严重度、停止动作、通知、响应时限、决定权和恢复条件 |
| STC | Stop Condition Register | 登记可判定 Stop Condition、信号、范围、即时动作、升级和恢复批准 |
| EXA | Exception Authorization | 决定 C07 规则的有界例外、理由、风险、补偿控制、期限、复核和撤销 |

七类产物不得相互替代。一个物理系统或文件可以联合展示，但每类产物必须保留独立 Asset ID、Artifact Type、State、Revision、Owner、Approval 和 History。

### 8.2 核心关系

| 来源 | 关系 | 目标 | 规则 |
|---|---|---|---|
| COL | `constrains` | Initiative、Feature、Requirement、Design、Run Scope | 必须绑定准确 Revision/Snapshot |
| COL | `depends-on` | RMA、ARD、APM、ESP、STC | 所有引用必须为当前有效 Revision |
| RMA | `contains` | Responsibility Assignment 成员 | 成员字段指向 Participant/Agent Role；Accountable 必须为人类 |
| ARD | `depends-on` | C02 Scope、C08 Context、Tool/Environment | 权限取各项边界的交集，不取并集 |
| APM | `constrains` | Operation/Artifact/Decision | 通过类型专属字段记录 Approval Event，不得用通配对象 |
| ESP | `depends-on` | Human Authority 与沟通路线 | 必须有主路线与替代路线 |
| STC | `constrains` | Agent Role/Operation/Scope | Triggered 后禁止继续受影响动作 |
| EXA | `depends-on` | C07 Standard Revision、Authority Source | 被例外 Rule ID 使用类型专属字段，不新增关系类型 |
| EXA | `depends-on` | Compensating Control 及其 Evidence | 控制必须可验证 |
| C09 Run | `depends-on` | COL/ARD/APM/Approval Evidence | 实际执行必须记录所用 Revision |

### 8.3 事实源边界

| 信息 | 唯一事实源 |
|---|---|
| Product、Goal、Problem | C01 |
| Initiative、Scope、Agent Modification Boundary、Risk | C02 |
| PRD、Feature、Scenario、Quality Attribute | C03 |
| Requirement | C04 |
| Acceptance、Verification、Validation、Evidence | C05 |
| UX/Technical Design、Permission Model Design | C06 |
| 角色、责任、Authorization、Approval、Stop、Escalation | C07 |
| Agent Context | C08 |
| Run、Command、Tool Call、实际变更和执行证据 | C09 |
| Decision、Trace 和 Lineage | C10 |
| Configuration、Snapshot、Baseline 和 Change | C11 |
| Gate、Risk Acceptance、质量例外和 Product Health | C12 |

## 9. 生命周期与工作机制

### 9.1 生命周期

`Collaboration Intake → Boundary and Risk Review → Role and Responsibility Design → Authorization and Approval Design → Stop and Escalation Design → Independent Review → Human Approval → Baselining → Context/Run Handoff → Monitoring → Change/Revocation/Retirement`

### 9.2 Collaboration Intake

进入 C07 前必须取得：

- 当前 Product、Initiative、Scope Boundary 和 Agent Modification Boundary；
- 当前 Feature、Requirement、Acceptance 和 Design Revision；
- 目标仓库、资源、环境和 Snapshot；
- 任务目标、预期输出、截止条件和禁止项；
- 当前 Risk、Constraint、Dependency 和扩展适用性；
- 拟使用 Agent、模型、工具、外部服务和人类角色；
- 需要的 Read、Create、Modify、Delete、Execute、Network、External Mutation 和 Deploy 操作；
- 已知敏感数据、凭据、合规、成本、外部承诺和不可逆影响。

任一必需输入缺失、冲突或失效时，COL 保持 Draft 或 Blocked 结论，不得进入执行。

### 9.3 Boundary and Risk Review

1. 对每项拟执行操作定位 C02 Agent Modification Boundary 判定。
2. 对相关 C02 Risk 记录当前 Risk Level、Treatment、Residual Risk 和 Trigger。
3. 未有 Risk 记录但操作引入新不确定性时，先在 C02 建立或更新 Risk，不得在 C07 临时评分代替。
4. 确认目标对象、环境、版本、最大修改范围和外部副作用。
5. 确认 E01 至 E05 适用性；需要而未激活的扩展按 C01 扩展规则升级。

### 9.4 Role and Responsibility Design

1. 建立 RMA 并为每项活动、产物和决定分配 RACI。
2. 为每个 Agent Role 建立 ARD。
3. 为每项高影响工作指定唯一 Human Accountable Owner。
4. 检查 Author/Executor、Reviewer、Approver、Risk Owner 和 Recovery Authority 的职责冲突。
5. 无法满足上游独立性要求时停止，不得用 Agent 数量补偿人类 Authority 缺口。

### 9.5 Authorization and Approval Design

1. 对八类 C02 操作逐项确定 Execution Permission Class。
2. Autonomous 只允许已明确授权、目标和环境确定、在最大修改范围内、无 Approval Event、无 Stop Trigger 且技术 Permission 匹配的操作。
3. Approval Required 必须在执行前取得绑定目标的有效 Approval Evidence。
4. Prohibited 不得通过普通 Approval 改为允许；需要偏离时必须先确认规则是否允许 EXA。
5. Not Assessed 按禁止执行处理并触发升级。
6. Tool/Environment Owner 将技术 Permission 收敛为 Authorization 的子集。

### 9.6 Stop and Escalation Design

建立 ESP 和 STC，至少覆盖输入冲突、授权缺失或过期、目标变化、风险上升、环境不符、工具异常、证据失败、敏感信息暴露、多 Agent 冲突、重试耗尽和人类 Stop 指令。

### 9.7 Review, Approval and Baselining

1. 独立 Reviewer 核对七类产物、边界、风险、独立性和可执行性。
2. Human Accountable Owner 与适用 Approver 核对责任和批准路线。
3. 只有有权人类可以把 DOC 产物置为 Approved，把 EXA 置为 Approved 或 Conditionally Approved。
4. 只有有权人类可以把 DOC 产物置为 Baselined。
5. 七类产物未满足适用条件时不得形成 Collaboration Ready。

### 9.8 Context and Run Handoff

交给 C08/C09 的协作包必须包含：

- COL、RMA、ARD、APM、ESP、STC 当前 Revision；
- 有效 EXA 和 Approval Evidence 引用；
- Agent Role、Human Accountable、Reviewer、Approver 和升级目标；
- Scope、Agent Modification Boundary、Risk、Requirement、Design 和 Snapshot 引用；
- Execution Permission Class、最大修改范围、有效期和撤销条件；
- 运行前检查、Stop Condition 和恢复规则。

### 9.9 Monitoring, Change and Retirement

运行期间必须监测授权有效期、目标 Snapshot、技术 Permission、风险触发、停止信号、审批消费、角色冲突和异常。任务完成、终止、有效期届满、角色撤销、目标变化或 EXA 过期后，相关授权必须撤销或失效。

## 10. 强制规则

### 10.1 协作身份与边界

1. 每个 COL 必须绑定一个可判定 Collaboration Scope。
2. Collaboration Scope 至少包括目标 Product/Initiative、Feature/Requirement、仓库或资源、环境、生命周期阶段、起止时间和预期输出。
3. 未列入 Scope 的对象默认禁止访问或修改。
4. 跨 Initiative、跨租户、跨仓库、跨账户、跨环境或跨组织边界不得通过近似名称解释为同一 Scope。
5. 目标 Snapshot、Revision 或环境无法确认时必须停止。

### 10.2 人类最终责任

1. Requirement 含义、Architecture 选择、Risk Acceptance、Acceptance Decision、Exception/Waiver、Baseline、Gate、Release、法律合规结论和外部承诺必须由有权人类负责。
2. Agent 可以准备建议、证据和草案，但禁止被列为 Accountable、Approval Authority、Risk Acceptance Authority 或最终 Gate Approver。
3. Delegation 只转移受限执行责任，不转移人类最终 Accountability。
4. “由系统决定”“由模型负责”“Agent 已验证”不能作为责任人字段。
5. Human Accountable 无法履职、身份不可验证或超过响应时限时，必须按 ESP 使用替代路线或停止。

### 10.3 Authority、Authorization、Permission 与 Approval

必须按以下关系执行：

`Capability ⊇ Technical Permission ⊆ Formal Authorization ⊆ Human Authority`

特定 Approval 只能在 Formal Authorization 和 Human Authority 内放行准确动作，不能扩大其边界。

1. Authority 必须有来源、适用对象、决定类型、环境和有效期。
2. Authorization 必须记录授予人、Agent Role、操作、对象、工具、环境、最大修改范围、条件、有效期和撤销方式。
3. Permission 必须由 Tool/Environment Owner 核对，禁止仅因技术上可用而执行。
4. Approval 必须由 APM 指定角色作出，并绑定具体目标和证据。
5. Authorization 或 Permission 任一缺失、过期、冲突或更宽时，按更窄边界执行；无法判定时停止。

### 10.4 八类操作与最低授权信息

沿用 C02 的操作类别：

| 操作类别 | 最低授权信息 |
|---|---|
| Read | 对象、路径或资源 ID、版本、敏感级别、允许用途、禁止导出范围 |
| Create | 允许目录或目标系统、对象类型、命名规则、最大数量/大小、所有者 |
| Modify | 允许对象、基线或 Commit、字段/路径边界、最大修改规模、不受影响边界 |
| Delete | 精确对象、可恢复性、备份或 Snapshot、影响、批准与恢复责任 |
| Execute | 命令或工具类别、参数边界、工作目录、超时、资源限制、预期输出 |
| Network | 目标域名或服务、方向、协议、数据类别、凭据边界、速率和日志 |
| External Mutation | 外部系统、账户/租户、操作、对象、幂等/撤销、外部影响和批准 |
| Deploy | 目标环境、版本、配置、变更窗口、验证、回滚、批准和观察责任 |

禁止把八类操作合并为“读写权限”或“完全访问”。每类未评估项均为 Not Assessed。

### 10.5 Execution Permission Class

| 类别 | 判定 | 执行规则 |
|---|---|---|
| Autonomous | 已在 COL/ARD/APM 明确允许，操作不触发批准事件，所有前置条件满足 | Agent 可在有效期与最大修改范围内执行并由 C09 记录 |
| Approval Required | APM、上游规范、Risk、操作性质或人类指令要求执行前批准 | 未取得有效 Approval Evidence 前禁止执行 |
| Prohibited | 法律、合同、Scope、C07 规则、ARD/APM 或人类决定明确禁止 | 普通 Approval 无法放行 |
| Not Assessed | 未完成对象、操作、环境、风险或责任判定 | 按 Prohibited 处理并升级 |

Autonomous 不表示低风险、无监督或无需记录。High/Critical Risk 操作禁止列为 Autonomous。

Medium Risk 操作应判为 Approval Required。申请将其列为 Autonomous 时，必须通过 EXA 记录可逆性、隔离、监测、最大修改范围、验证、Human Accountable 和到期时间；上游规范要求批准时禁止例外。

### 10.6 Autonomous 操作

Agent 仅在全部条件同时满足时可以自主执行：

1. COL、ARD 和 APM 为 Approved 或 Baselined 且 Revision 一致；
2. C02 对该操作明确为 Allow，且 C07 APM 明确为 Autonomous；
3. 关联风险不是 High 或 Critical；
4. 目标、环境、Snapshot、Context 和工具与授权完全一致；
5. 技术 Permission 不超过 Authorization；
6. 未触发任何 Approval Event 或 Stop Condition；
7. 操作可审计，且不会产生未声明的外部副作用；
8. 当前修改规模未达到最大修改范围；
9. C09 能记录命令、Tool Call、输入、输出、变更和结果；
10. 人类未发出 Stop 或更窄限制。

任一条件不满足即停止自主执行。

### 10.7 必须批准的事件

以下任一事件至少为 Approval Required；适用规则为 Prohibited 时仍不得执行：

- High 或 Critical Risk 相关动作；
- Delete、Deploy 或不可逆操作；
- External Mutation、对外消息、公开发布、外部工单、账户或资源变更；
- 生产、客户、真实用户、真实资金、付费资源或外部承诺；
- 凭据、密钥、令牌、权限、身份、角色、访问控制或安全策略变化；
- 敏感、个人、机密、受监管或合同受限数据的新增访问、导出、移动或用途变化；
- 跨 Scope、跨仓库、跨租户、跨账户、跨组织或跨环境；
- Agent Modification Boundary、Authorization、技术 Permission 或最大修改范围扩大；
- Requirement、Architecture、Risk Acceptance、Acceptance、Baseline、Gate、Release 或正式 Decision；
- 绕过、关闭或削弱测试、审计、监控、安全、隐私、合规或职责分离控制；
- 失败后回滚、恢复、重试范围扩大或以不同参数再次执行高影响操作；
- APM、上游规范、适用扩展或有权人类指定的其他事件。

### 10.8 Agent 禁止行为

Agent 禁止：

1. 将自己或其他 Agent 指定为最终 Accountable 或有权人类；
2. 批准自身或其他 Agent 的高风险输出；
3. 作出 Risk Acceptance、Exception/Waiver、Gate、Release、Baseline 或法律合规结论；
4. 创建、扩大、延长或恢复自身 Authorization；
5. 获取、复制、共享或使用未明确授权的凭据和身份；
6. 绕过技术 Permission、分支保护、评审、测试、审计、监控或 Stop；
7. 修改、删除、隐藏或伪造批准、运行、证据、日志、发现项或反对意见；
8. 把聊天、沉默、表情、口头同意或 Agent 摘要解释为 Approval；
9. 用相似名称、符号链接、间接依赖、生成目录或外部服务扩大 Scope；
10. 在目标不明确时执行 Delete、External Mutation 或 Deploy；
11. 在冲突、异常或未知状态下采用更宽权限解释；
12. 为完成任务而自行修改 Requirement、Design、Risk、Acceptance 或 Gate；
13. 把模型输出、单元测试通过或命令成功声明为业务接受或国际标准符合；
14. 以回滚、清理、重试、格式化或自动修复名义执行未授权变更；
15. 指示子 Agent 执行自身无权执行的动作。

### 10.9 Approval Protocol

每项 Approval Evidence 必须包含：

- Approval Evidence ID 或受控记录引用；
- Approval Event 和适用 APM ID/Revision；
- 提交人、执行 Agent Role/Instance 和 Human Accountable；
- 批准人身份、角色及 Authority Source；
- 精确动作、参数、目标对象、环境和目标 Snapshot；
- 关联 Scope、Requirement、Design、Risk 和 Evidence；
- 允许的最大修改范围、使用次数和执行窗口；
- 条件、补偿控制、验证和失败处理；
- Approval Outcome、理由、决定时间和到期时间；
- 撤销方式、替代路线和历史引用。

以下情况使 Approval 立即失效：

- 动作、参数、目标、环境、Snapshot 或 Context 变化；
- Risk Level 上升、新 Risk 出现或控制失效；
- Approval 超期、已消费、被撤销或批准人 Authority 失效；
- 修改范围超过批准值；
- 发生 Stop Condition；
- 上游 Requirement、Design、Scope、Baseline 或授权 Revision 变化。

禁止批准者未查看证据即批量批准；禁止以一次批准覆盖未列明的未来动作。

### 10.10 最小权限与最大修改范围

1. ARD 必须对对象、操作、工具、环境和时间分别收敛。
2. Read 与 Write 必须分开；Create、Modify 与 Delete 必须分开。
3. Network、External Mutation 与 Deploy 默认不是本地 Write 的附带权限。
4. 最大修改范围必须使用可测边界，例如对象清单、文件数量、路径、字段、资源数量、数据行数、字节、执行次数或变更窗口；不得使用空值或通配。
5. 目标产品必须选择与任务相符的量纲和数值，本规范不虚构统一默认值。
6. 达到最大修改范围时必须停止并提交差异，不得自动分批规避上限。
7. Context、凭据和工具权限在任务结束、超期、撤销或角色变化后必须失效。

### 10.11 风险与职责分离

1. C07 必须引用 C02 Risk ID、Risk Level、Treatment、Residual Risk 和 Risk Owner。
2. Execution Permission Class 不能替代 Risk Level。
3. High/Critical 变更的 Author/Executor 不得成为唯一 Reviewer 或最终 Approver。
4. 同一 Agent Instance 不得同时被计为高风险实现者和独立 Review Agent。
5. Agent 数量、模型名称差异、会话差异或提示词差异不能替代人类独立性。
6. C05、C06、C11、C12 或适用扩展规定更严格分离时，执行更严格规则。
7. 无法满足独立性时必须 Blocked；不得由 Agent 批准 EXA 绕过。
8. Critical Risk 的 Reviewer 与 Approver 应由两个不同且无未声明冲突的人类承担；上游规范规定为强制分离时，EXA 不得覆盖。

### 10.12 Stop Conditions 与 Fail-Closed

至少登记以下 Stop Condition：

| Stop 类别 | 可判定信号 | 即时动作 |
|---|---|---|
| 输入冲突 | Requirement、Design、Scope、Context 或指令互相矛盾 | 停止受影响操作，保留冲突引用 |
| 授权失效 | Authorization 缺失、过期、撤销、范围不符或 Authority 不明 | 禁止继续，通知 Authorization Owner |
| 权限漂移 | 技术 Permission 大于或小于预期，或身份变化 | 停止 Tool Call，隔离凭据 |
| 目标变化 | 文件、分支、Snapshot、环境或外部对象与批准不一致 | 禁止使用旧批准 |
| 风险变化 | 新增 High/Critical Risk、Risk Trigger 或控制失败 | 通知 Risk Owner 和 Approver |
| 环境不符 | 实际环境、账户、租户、区域或工作目录不符 | 禁止写入或执行 |
| 结果异常 | 工具输出、变更数量、影响范围或副作用超出预期 | 停止后续步骤，保存证据 |
| 证据失败 | 日志、哈希、差异、验证或审计记录不可用 | 禁止继续高影响动作 |
| 敏感暴露 | 凭据、个人数据、机密或受限内容出现在未授权位置 | 停止传播，按安全/隐私路线升级 |
| 多 Agent 冲突 | 对 Scope、Requirement、Decision、写入所有权或目标版本存在冲突 | 停止冲突范围，禁止覆盖 |
| 依赖失败 | Blocking Dependency、服务、工具或审批路线不可用 | 停止依赖步骤 |
| 重试耗尽 | 达到 APM/ARD 规定次数、时间或资源上限 | 禁止继续重试 |
| 人类 Stop | 任一有权人类发出明确 Stop | 立即停止并确认已停止范围 |

Stop 后 Agent 只能执行预先授权的安全保存、只读诊断和证据封存动作。任何修改、删除、外部变更、回滚或恢复均需重新判定权限。

### 10.13 Escalation、Resume 与 Rollback

1. ESP 必须对每个 Stop Condition 指定通知目标、响应时限、决定 Authority、必需信息和替代路线。
2. 升级信息至少包含任务、Agent、目标、环境、Snapshot、最后成功步骤、异常、已执行动作、潜在影响、Risk、证据和请求决定。
3. 未在时限内获得决定时按 Fail-Closed 保持停止，不得默认为批准。
4. Resume Approval 必须引用新鲜 Context、目标 Snapshot、剩余 Risk、恢复步骤、验证和新的有效期。
5. 旧 Approval、旧 Authorization 或同一 Run 的缓存决定不得自动恢复。
6. Rollback 是独立操作；必须核对目标、可逆性、数据影响、权限、批准、验证和恢复责任。
7. 无法安全回滚时必须保持隔离并交由 Recovery Authority 决定降级、前滚、终止或人工修复。

### 10.14 多 Agent 协作

1. 每个 Agent Role 必须有独立 ARD，每次 Agent Instance 由 C09 标识。
2. Orchestrator 对子 Agent 的有效授权是 `Orchestrator Authorization ∩ Child ARD ∩ Task Scope ∩ Tool Permission`。
3. Agent 禁止相互授予更高 Authority、延长有效期或改变 Approval Outcome。
4. 子任务必须传递目标、输入 Revision、允许输出、禁止项、最大修改范围、Stop Condition 和交接格式。
5. 共享写入必须指定对象 Owner、写入分区、锁或串行顺序、合并责任和冲突处理。
6. 同一对象存在未合并变更、未知工作区状态或版本漂移时，后续写入 Agent 必须停止。
7. Review Agent 必须获得被评对象的准确 Revision、评审准则和独立性声明。
8. 汇总 Agent 禁止删除异议、失败、未解决 Finding 或不确定性。
9. 多 Agent 冲突必须生成可定位记录并交由有权人类决定；不得按多数 Agent 输出投票。
10. Agent 交接不替代人类 Approval，也不改变事实源。

### 10.15 冲突解决

冲突按以下顺序处理：

1. 确定受影响对象并冻结相关写入；
2. 保存各方输入、Revision、输出、理由和证据；
3. 识别冲突类型：事实、Requirement、Scope、Design、Risk、权限、Decision、版本或写入所有权；
4. 路由到相应事实源 Owner 或 C10 Decision Authority；
5. 记录受控决定、适用范围、后果和被替代输入；
6. 更新受影响 COL/RMA/ARD/APM/ESP/STC/EXA Revision；
7. 重新评估 Context、Approval 和 Resume 条件后再执行。

禁止通过覆盖文件、删除分支、丢弃异议或选择最新时间戳自动解决语义冲突。

### 10.16 审计与可追责

C07 必须使 C09 能记录：

- COL、RMA、ARD、APM、ESP、STC、EXA ID 与 Revision；
- Human Accountable、执行 Agent Role/Instance、Reviewer 和 Approver；
- Authorization、Approval Evidence、Scope、Risk、Context 和 Snapshot 引用；
- 实际操作类别、工具、环境、对象、参数、时间和结果；
- 最大修改范围与实际使用量；
- Stop Trigger、升级、响应、Resume Approval 和撤销；
- 多 Agent 委派链、交接、冲突和合并；
- Finding、反对意见、失败、补偿控制和剩余 Risk；
- 产物 Revision、变更原因、批准和 History。

审计信息不得由被审计 Agent 单独控制删除或覆盖。无法形成必要记录时禁止执行高影响操作。

### 10.17 Exception Authorization

1. EXA 必须指向一个或多个准确 C07 Rule ID。
2. EXA 只能申请偏离“应”或“不应”规则，禁止覆盖“必须”或“禁止”规则。
3. EXA 必须有业务或技术理由、Scope、Risk、补偿控制、请求人、有权人类批准人、起止时间、复核计划和撤销条件。
4. EXA 的补偿控制必须在生效前可验证；无法验证时不得 Approved。
5. Conditionally Approved 必须列明前置条件、验证人和到期处理。
6. EXA 过期后 State 置为 Expired，相关授权立即失效。
7. EXA 禁止覆盖适用法律、合同义务、人类最终 Accountability、审计完整性、Agent 自我批准禁令、未知目标的破坏性操作或有权人类 Stop。
8. EXA 不得作为 C02 Risk Acceptance、C10 Decision、C11 Change Approval 或 C12 Exception/Waiver 使用。
9. Agent 可以起草 EXA，但不能批准、延长、撤销或把 EXA 解释为未列明权限。

### 10.18 变化、到期与撤销

以下变化必须建立受控修订，并重新检查 Approval：

- Agent Role、模型、版本、工具或系统提示变化；
- Human Accountable、Authorization Owner、Reviewer、Approver 或 Authority Source 变化；
- Scope、Requirement、Design、Context、Snapshot、环境或最大修改范围变化；
- Risk Level、Treatment、Residual Risk 或 Stop Condition 变化；
- 技术 Permission、凭据、网络或外部服务变化；
- 多 Agent 拓扑、写入所有权、交接或合并方式变化；
- Approval Event、替代路线、响应时限或恢复方式变化；
- EXA 新增、扩大、延期、撤销或过期。

授权收缩和紧急撤销必须立即生效；扩大、恢复或延期必须先评审和人类批准。

## 11. 受控状态

### 11.1 DOC 产物

COL、RMA、ARD、APM、ESP 和 STC 使用 DOC 状态：

`Draft → In Review → Changes Required → Approved → Baselined`

并允许 `Rejected`、`Superseded`、`Retired`。

| 状态 | 使用规则 |
|---|---|
| Draft | 正在编制，不得作为 Agent 执行授权 |
| In Review | 输入冻结供评审，不得作为新授权 |
| Changes Required | 存在待整改 Finding |
| Approved | 有权人类批准，可在批准 Scope 和有效期内使用 |
| Baselined | 已纳入受控基线，变化必须走 C11 |
| Rejected | 不获接受，禁止作为当前输入 |
| Superseded | 已被新 Revision 或新资产替代 |
| Retired | 不再适用，但保留历史 |

### 11.2 EXA 状态

EXA 使用 DEC 状态：

`Proposed → Under Review → Approved / Conditionally Approved / Rejected / Waived → Superseded / Expired`

`Waived` 表示原例外请求被授权人判定无需例外，不表示放弃控制。Approved、Conditionally Approved 和 Waived 只能由有权人类决定。

### 11.3 STC 成员状态

Stop Condition Entry 需要独立治理时使用 CASE：

`Open`、`In Progress`、`Blocked`、`Resolved`、`Closed`、`Reopened`、`Cancelled`。

成员 State 表示条件定义的治理进度，不表示运行时是否已触发。运行时使用 Stop Trigger Status，并由 C09 记录实际触发和清除。

### 11.4 状态转换规则

1. 状态转换必须遵循 VC-PPG-COM-002。
2. Agent 可以建议状态或准备证据，但不能把 DOC 置为 Approved/Baselined，也不能把 EXA 置为 Approved/Conditionally Approved/Waived。
3. Baselined 资产变化必须建立新 Revision 和适用 C11 Change Request。
4. Superseded、Retired、Rejected 或 Expired 资产禁止作为当前授权。
5. Collaboration Readiness、Approval Outcome、Execution Permission Class、Stop Trigger Status 和 Review Outcome 禁止写入 State 字段。

## 12. 必需产物

| 产物 | 最低创建条件 | 主要下游 |
|---|---|---|
| Collaboration Contract | 任何人机或多 Agent 受控协作开始前 | C08、C09、C12 |
| Responsibility Matrix | COL 创建后立即建立 | C08、C09、C10、C12 |
| Agent Role Definition | 每个拟使用 Agent Role 必须建立 | C08、C09 |
| Approval Matrix | 存在任一 Agent 操作或产物批准事件 | C09、C11、C12 |
| Escalation Protocol | 任何 Agent 执行前必须建立 | C08、C09、C12 |
| Stop Condition Register | 任何 Agent 执行前必须建立；无项目特有条件时仍记录最低条件集 | C08、C09 |
| Exception Authorization | 请求偏离 C07 规则时按需建立 | C09、C10、C11、C12 |

P2 禁止合并、删除或用空章节替代七类产物的独立身份。无 EXA 时无需建立空 EXA 实例，但 EXA 类型、模板和触发规则必须保留。

## 13. 必填信息

### 13.1 通用必填信息

每项正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的公共责任与人工决定引用组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C07 类型专属要求。

### 13.2 Collaboration Contract

COL 必须包含：

- COL ID、协作目标、预期输出和完成条件；
- Product、Initiative、Feature、Requirement、Design 和 Snapshot 引用；
- 参与者及 Participant Type；
- Human Accountable Owner；
- Agent Role、Agent Owner 和适用 ARD；
- 输入、输出、Context、仓库、资源和环境边界；
- 八类操作的 Execution Permission Class；
- 最大修改范围和不受影响边界；
- Approval Event、Approver 和 Approval Evidence 规则；
- Prohibited Action；
- Stop Condition、ESP 和恢复规则；
- Risk、Constraint、Dependency 和扩展适用性；
- 生效时间、到期时间、撤销条件和终止处理；
- RMA、APM、ESP、STC 和有效 EXA 引用；
- Review、Approval、State、Revision 和 History。

### 13.3 Responsibility Matrix

RMA 必须包含：

- RMA ID、COL ID 和适用 Scope；
- Activity 或 Artifact；
- Responsible、Accountable、Consulted、Informed；
- Reviewer、Approver 和 Authority Source；
- Participant Type 与身份引用；
- Risk Level 和独立性要求；
- 职责冲突检查及结论；
- 无人响应时的替代角色；
- State、Revision、评审、批准和 History。

### 13.4 Agent Role Definition

ARD 必须包含：

- ARD ID、Agent 角色和用途（Agent Role Name、Purpose）及 Agent Owner；
- 适用 Product、Initiative、生命周期阶段和任务类型；
- 可访问 Context、敏感级别和 C08 规则；
- 模型、可用工具、身份和外部服务边界；
- Read、Create、Modify、Delete、Execute、Network、External Mutation、Deploy 的对象和判定；
- 允许环境、账户、租户、仓库、分支和工作目录；
- 最大修改范围及量纲；
- 允许自主动作；
- Approval Event 与 APM 引用；
- Prohibited Action；
- Stop Condition 与 ESP 引用；
- 关联 Risk Level、Human Accountable 和 Reviewer；
- 已知能力、限制、失败模式和验证方法；
- 生效、到期、复核、撤销和终止处理；
- State、Revision、批准和 History。

### 13.5 Approval Matrix

APM 必须包含：

- APM ID、COL ID、Owner 和适用 Scope；
- Operation 或 Artifact；
- C02 操作类别和 Execution Permission Class；
- 关联 Risk ID/Level；
- Approval Event 和触发条件；
- Submitter、Executor、Human Accountable、Approving Role；
- Authority Source 和独立性要求；
- Required Evidence；
- 允许条件、最大修改范围和验证；
- Approval 响应时限、执行窗口、使用次数和到期；
- 替代批准路线；
- Approval Evidence 记录位置；
- State、Revision、评审、批准和 History。

### 13.6 Escalation Protocol

ESP 必须包含：

- ESP ID、COL ID、Owner 和适用 Scope；
- Trigger、Severity 和关联 STC/Risk；
- Immediate Stop Action；
- Notify Target、Decision Authority 和替代路线；
- Response Time；
- Required Information Package；
- 允许的只读诊断或证据封存；
- Decision Options；
- Resume Condition 和 Resume Approver；
- 无响应、拒绝、延期和终止处理；
- 沟通渠道、确认方式和记录位置；
- State、Revision、评审、批准和 History。

### 13.7 Stop Condition Register

STC 必须包含：

- STC ID、COL ID、Register Owner；
- Stop Condition ID 和 Member State；
- 可判定 Signal；
- 适用 Agent Role、Operation 和 Scope；
- Immediate Action；
- Prohibited Continuation；
- Escalation Target 和 ESP 引用；
- Required Evidence；
- Resume Approval 和恢复前置条件；
- Trigger Status 记录位置；
- Source、History 和复核周期；
- STC 的 State、Revision、评审和批准。

### 13.8 Exception Authorization

EXA 必须包含：

- EXA ID、被例外 C07 Rule ID 和请求摘要；
- Applicable Scope、对象、操作、环境和最大修改范围；
- Rationale、不可采用常规规则的证据和替代方案；
- Risk ID/Level、Residual Risk 和 Risk Owner；
- Compensating Control、验证方法、Owner 和证据；
- Requester、Human Accountable、Reviewer、Approver 和 Authority Source；
- Start、Expiry、使用次数和复核计划；
- Revocation Condition、终止处理和通知对象；
- 与 C02 RAR、C10 Decision、C11 Change、C12 Exception/Waiver 的边界声明；
- State、Revision、Decision Rationale、反对意见和 History。

## 14. 质量要求

七类 C07 产物必须同时满足：

1. 完整：七类身份、适用实例和必填信息无缺口；
2. 明确：参与者、目标、Scope、对象、操作、环境、版本和有效期可判定；
3. 责任唯一：每项高影响工作有且仅有一个明确 Human Accountable；
4. 最小权限：技术 Permission 不大于 Formal Authorization；
5. 不自批：Agent 不得承担最终批准，高风险实现与最终评审不由同一 Agent 实例完成；
6. 风险一致：只引用 C02 风险量表和正式 Risk；
7. 可停止：每个冲突、失效、异常和人类 Stop 都有即时动作；
8. 可升级：每个 Stop 有通知目标、时限、决定 Authority 和替代路线；
9. 可恢复：恢复基于新鲜 Context、Snapshot、Risk 和人类批准；
10. 可撤销：Authorization、Approval 和 EXA 均有到期或撤销；
11. 可审计：每项动作能追踪到 Agent、人员、规则、目标、版本、时间和证据；
12. 多 Agent 受控：委派不扩权、共享写入有所有权、冲突不自动覆盖；
13. 事实源唯一：不复制 C02 Risk、C08 Context、C09 Run、C10 Decision 或 C12 Gate；
14. 无空白授权：不存在通配、隐含、永久或无法测量的修改范围；
15. 无虚假符合：不把本规范、模型输出或工具结果声明为完整国际标准符合或认证。

## 15. 评审、批准与就绪

### 15.1 评审顺序

1. Owner 自检；
2. 事实源 Owner 核对 Scope、Requirement、Design、Risk、Context 和 Snapshot；
3. Tool/Environment Owner 核对技术 Permission；
4. Independent Reviewer 核对职责分离、批准、停止、升级、恢复和审计；
5. Security/Privacy/Compliance Authority 处理适用专业事项；
6. Human Accountable 与 Approver 作最终项目级批准；
7. C11 在需要时建立 Baseline。

### 15.2 Collaboration Ready 条件

只有全部满足时可以给出 Collaboration Ready：

- COL、RMA、适用 ARD、APM、ESP 和 STC 为 Approved 或 Baselined；
- 有效 EXA 已批准且前置条件完成，或确认无 EXA；
- Human Accountable、Reviewer、Approver 和升级路线明确；
- 八类操作均已判定，无 Not Assessed；
- C02 Scope、Risk 和 Agent Modification Boundary 当前有效；
- C08 Context 可组装且数据 Authority 明确；
- 目标环境和 Snapshot 可定位；
- 技术 Permission 已验证为 Authorization 子集；
- 高风险职责分离满足上游规则；
- Stop、Resume、Rollback 和审计能力可用。

Collaboration Ready 只表示协作控制就绪，不表示 Requirement、Design、Acceptance、Release 或 Gate 已批准。

### 15.3 阻断条件

以下任一情况必须 Not Ready 或 Blocked：

- Human Accountable 缺失、重复、为 Agent 或 Authority 不明；
- 七类必需产物缺失、状态无效或 Revision 冲突；
- Agent Role、Context、工具、环境、最大修改范围或有效期不明确；
- 八类操作存在 Not Assessed、空白或通配；
- High/Critical 操作被列为 Autonomous；
- Agent 可批准自身输出、接受风险或扩大权限；
- 审批不绑定对象、Snapshot、证据或有效期；
- Stop Condition、升级目标、替代路线或恢复批准缺失；
- 多 Agent 共享写入无 Owner/分区/顺序；
- 技术 Permission 大于 Authorization；
- EXA 试图覆盖禁止例外的规则；
- C02/C04/C06/C08/C11 输入缺失、冲突或过期；
- C09 无法形成要求的审计记录。

## 16. 变更、审计与保留

### 16.1 变更控制

Approved 但未 Baselined 的产物变化必须建立新 Revision、差异、影响分析和重新批准。Baselined 产物变化必须按 C11 建立 Change Request。

影响分析至少覆盖：

- Human Accountable、角色、Authority 和职责分离；
- Scope、操作类别、权限、最大修改范围和环境；
- Risk、Approval Event、Stop Condition 和升级路线；
- Context、工具、模型、外部服务和 Snapshot；
- 进行中 Run、未消费 Approval、有效 EXA 和下游 Gate；
- 凭据撤销、缓存、工作区、未合并变更和审计连续性。

### 16.2 审计历史

必须永久保留：

- 每个 Revision 的作者、时间、差异、评审、批准和替代关系；
- 每次 Authorization 创建、收缩、扩大、暂停、恢复、撤销和到期；
- 每次 Approval 的对象、证据、结果、条件、消费和失效；
- 每次 Stop、升级、响应、恢复、回滚、终止和未响应；
- 每次多 Agent 委派、交接、冲突、覆盖拒绝和合并决定；
- 每个 EXA 的请求、反对、批准、控制、复核、撤销和到期；
- 对应 C09 Run/Evidence、C10 Decision/Trace、C11 Change/Baseline 和 C12 Gate/Risk Acceptance 引用。

### 16.3 访问与保留

1. C07 产物默认 Internal；含凭据、个人数据、漏洞或受限配置时按更高 Access Classification 管理。
2. 正式产物禁止包含可直接使用的明文凭据。
3. Retention Rule 必须覆盖审计、合同、合规、事故调查和模型供应商限制。
4. Retired、Superseded、Rejected 和 Expired 记录必须保留历史，不得物理覆盖。

## 17. P2 裁剪与扩展适用性

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C07 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

每个 Agent 任务必须能解析人类 Accountable、允许修改边界、停止条件和升级路径。已有 COL、RMA、ARD、APM、ESP、STC Baseline 完整覆盖任务时统一 `Reference`，只有角色、权限、批准矩阵、停止或升级规则变化时才 `Create/Revise`。

EXA 只在 Agent 需要超出正常权限时由具备 Authority 的人类 `On Event` 创建；不得用 EXA 替代 C12 EWR 或 RAR。COL、RMA、ARD、APM 共享字段引用 VC-PPG-COM-002 第 3.1 节，不重复定义 Owner、Approval、Scope 和 Trace 语义。

### 17.1 当前 P2 档位

当前项目执行 P2：

1. COL、RMA、ARD、APM、ESP、STC、EXA 七类正式产物身份全部保留；
2. 六类 DOC 与一类 DEC 的 State、Revision、Owner、Trace 和 History 不得合并；
3. 无 EXA 时可不创建实例，但不得删除 EXA 类型、规则和模板；
4. 模板可以作为本规范附录，也可以在工具中实现；
5. 人类最终责任、Agent 权限、禁止项、批准、停止、升级、恢复、有效期和审计不得裁剪。

### 17.2 未来档位

P1 可以用一页 Collaboration Contract 联合展示，但权限、禁止项、批准点、Human Accountable、Stop、Escalation 和有效期不得省略，各逻辑产物仍须有独立身份。

P3 可以增加平台级策略、自动授权验证、细粒度身份、持续监控、强制隔离和自动撤销，但不得取消人类最终 Accountability 或 Agent 自我批准禁令。

任何档位变化必须通过项目级适用性决议和 C11 Change Control。

### 17.3 扩展适用性

| 扩展 | 触发条件 | C07 附加控制 |
|---|---|---|
| E01 Architecture Governance | 多系统、复杂服务、关键架构或独立部署边界 | 增加 Architecture Authority、架构批准与一致性评审职责 |
| E02 Security/Privacy/Compliance | 敏感数据、身份、权限、外部威胁、监管或合同要求 | 增加专业 Authority、职责分离、敏感 Context 和安全 Stop |
| E03 Data/AI Governance | 训练/评估数据、模型、自动决策、知识或数据质量治理 | 增加 Data/Model Owner、数据用途、模型风险和人工监督 |
| E04 Knowledge/Records Governance | 正式知识、记录分类、保留、处置、Legal Hold 或检索进入治理范围 | 增加 Records Steward、Disposition Authority、保留与检索责任 |
| E05 Product Operations/Service Management | 版本发布、部署、生产运行、SLO、事件、值守、容量或恢复进入治理范围 | 增加 Release/Environment/Operations Authority、Deploy Approval、运行 Stop 和恢复责任 |

本规范仓库当前 E03、E04 已激活；E01、E02、E05 未针对规范仓库激活。具体目标产品必须重新执行适用性评估，不能继承本仓库结论。

## 18. 上下游交接

| 规范 | C07 接收 | C07 输出 |
|---|---|---|
| C01 | Stakeholder、Goal、Evidence、扩展适用性 | Discovery 协作角色、权限和批准边界 |
| C02 | Scope、Agent Modification Boundary、Risk、Constraint、Dependency | Owner、Approver、操作许可、Scope Exception 和升级路径 |
| C03 | PRD、Feature、Scenario、Non-goal、Quality Attribute | 产品规格活动的 RACI、评审和批准规则 |
| C04 | Requirement、Revision、Evolution Event、冲突 | Requirement 解释 Authority、Agent 禁止提升和冲突停止 |
| C05 | Verification、Validation、Evidence、独立性要求 | 验证角色、证据权限、评审与 Acceptance 分离 |
| C06 | Design Role、Affected/Unaffected Boundary、Design Risk | 设计职责、Agent 修改授权、批准和停止 |
| C08 | Context 结构与最小化需求 | 允许 Context、访问角色、有效期、敏感边界和撤销 |
| C09 | Run 计划、工具和执行需求 | Agent Role、Authorization、Approval、Stop、Escalation 和审计字段 |
| C10 | Decision/Trace 需求 | Decision Authority、冲突路由和职责引用 |
| C11 | Snapshot、Baseline、Change、Release Configuration | 变更批准角色、配置权限、Deploy 边界和撤销 |
| C12 | Gate、Risk Acceptance、Exception/Waiver、Health | Gate RACI、独立性、批准 Authority 和阻断升级 |

C08/C09 必须使用 C07 的准确 Revision。C07 变化使现有 Context 或 Run Authorization 失效时，必须通知并阻断继续执行。

## 19. 符合性检查

### 19.1 检查方法

符合性检查必须使用目标 COL 及关联七类产物的固定 Revision，检查字段、关系、状态、批准、风险、权限、停止、升级、证据和历史。检查结果使用 Review Record，不修改正式产物 State。

### 19.2 强制检查项

1. 七类正式产物是否保留独立身份；
2. 通用必填信息是否完整；
3. COL 是否绑定准确 Product/Initiative、Scope、环境和 Snapshot；
4. 是否有唯一明确 Human Accountable；
5. Agent 是否被错误列为 Accountable、Approver 或 Risk Acceptance Authority；
6. RMA 是否覆盖 RACI、Reviewer、Approver 和冲突检查；
7. 每个 Agent Role 是否有 ARD；
8. Agent 目的、Context、工具、读写范围和环境是否明确；
9. 最大修改范围是否可测且无通配；
10. 八类 C02 操作是否逐项判定；
11. Execution Permission Class 是否使用受控值；
12. High/Critical 操作是否未被列为 Autonomous；
13. 技术 Permission 是否为 Authorization 子集；
14. Authority Source、授权人和有效期是否可定位；
15. Approval Event 是否覆盖破坏性、外部、生产、敏感和高风险事件；
16. Approval Evidence 是否绑定动作、参数、对象、环境和 Snapshot；
17. 是否禁止沉默、聊天或 Agent 摘要作为批准；
18. Agent 是否能批准自身输出或扩大自身权限；
19. 高风险 Author/Executor、Reviewer、Approver 是否满足独立性；
20. Stop Condition 是否覆盖输入冲突和授权失效；
21. Stop Condition 是否覆盖目标变化、环境不符和结果异常；
22. Stop Condition 是否覆盖敏感暴露、多 Agent 冲突和重试耗尽；
23. Triggered 后是否 Fail-Closed；
24. ESP 是否有通知目标、时限、决定 Authority 和替代路线；
25. Resume 是否需要新鲜 Context、Snapshot、Risk 和人类批准；
26. Rollback 是否作为独立操作重新授权；
27. 多 Agent 子任务授权是否取交集；
28. 共享写入是否有 Owner、分区/锁/顺序和合并责任；
29. Review Agent 是否未被误作人类独立评审；
30. 冲突是否冻结受影响范围并路由事实源 Owner；
31. EXA 是否只指向准确 C07 Rule；
32. EXA 是否有 Risk、补偿控制、期限、复核和撤销；
33. EXA 是否未替代 RAR、Decision、Change Approval 或 Gate Waiver；
34. 无法例外的规则是否得到保护；
35. 授权、批准、停止、升级、恢复和撤销是否可审计；
36. C09 是否能记录 Agent Instance、Tool Call、实际修改和 Evidence；
37. DOC、DEC、CASE State 是否符合公共状态模型；
38. 非 State 判定是否未写入 State；
39. P2 是否未裁剪权限、禁止项、批准、Human Accountable 和停止升级；
40. E01 至 E05 是否完成目标产品级适用性复核；
41. 版本变化是否触发影响分析和重新批准；
42. 是否不存在完整 ISO 符合或认证的虚假声明。

### 19.3 不符合处理

1. 责任、权限、批准、停止或升级缺口属于 Blocking Finding。
2. 技术 Permission 大于 Authorization 时必须立即收缩权限或停止。
3. 已执行的越权、高风险、自我批准或审计缺失操作必须升级 C12，并按需要进入安全、事故或变更流程。
4. Finding 修复后必须由原 Reviewer 或独立替代 Reviewer 复核。
5. Agent 不能关闭涉及自身越权、证据缺失或高风险输出的 Finding。

## 20. 附录

### 20.1 通用头部模板

```markdown
| 信息项 | 内容 |
|---|---|
| Asset ID | <TYPE>-<NNNN> |
| Artifact Type | <正式产物名称>（<TYPE>） |
| Name or Summary | |
| Purpose | |
| Source | |
| Owner | <明确人类或受控角色> |
| State | <公共状态模型允许值> |
| Current Revision | |
| Created and Updated | |
| Applicable Scope | |
| Trace Links | |
| Access Classification | |
| Retention Rule | |
| History Reference | |
```

### 20.2 Collaboration Contract 模板

```markdown
# COL-<NNNN> <协作名称>

<通用头部>

| 字段 | 内容 |
|---|---|
| Collaboration Goal / Expected Output | |
| Completion Condition | |
| Product / Initiative / Feature / Requirement | |
| Target Repository / Resource / Environment / Snapshot | |
| Human Accountable Owner | |
| Participants / Participant Type | |
| Agent Roles / ARD | |
| Input / Output / Context Boundary | |
| Unaffected Boundary | |
| Maximum Modification Scope | |
| Risk / Constraint / Dependency | |
| Effective / Expiry / Revocation | |

| Operation | Object / Environment | Execution Permission Class | Conditions | Approval Event | Prohibition |
|---|---|---|---|---|---|
| Read | | Not Assessed | | | |
| Create | | Not Assessed | | | |
| Modify | | Not Assessed | | | |
| Delete | | Not Assessed | | | |
| Execute | | Not Assessed | | | |
| Network | | Not Assessed | | | |
| External Mutation | | Not Assessed | | | |
| Deploy | | Not Assessed | | | |

| RMA | APM | ESP | STC | Active EXA | Approval Evidence Location |
|---|---|---|---|---|---|
| | | | | | |
```

### 20.3 Responsibility Matrix 模板

```markdown
# RMA-<NNNN> <责任矩阵名称>

<通用头部>

| Activity / Artifact | Responsible | Accountable | Consulted | Informed | Reviewer | Approver | Risk Level | Independence Rule | Conflict Check |
|---|---|---|---|---|---|---|---|---|---|
| | | <一个明确人类> | | | | | | | |

| Participant | Type | Identity Reference | Authority Source | Alternate | Validity |
|---|---|---|---|---|---|
| | Human / Agent | | | | |
```

### 20.4 Agent Role Definition 模板

```markdown
# ARD-<NNNN> <Agent Role Name>

<通用头部>

| 字段 | 内容 |
|---|---|
| Purpose / Task Type / Lifecycle Stage | |
| Agent Owner | |
| Human Accountable / Reviewer | |
| Accessible Context / Classification | |
| Model / Tool / Identity / External Service | |
| Allowed Environment / Account / Tenant / Repository / Branch | |
| Maximum Modification Scope / Unit | |
| Known Capability / Limitation / Failure Mode | |
| Validation Method | |
| Approval Events / APM | |
| Prohibited Actions | |
| Stop Conditions / ESP | |
| Risk ID / Level | |
| Effective / Expiry / Review / Revocation | |

| Operation | Object Boundary | Environment | Execution Permission Class | Conditions |
|---|---|---|---|---|
| Read | | | Not Assessed | |
| Create | | | Not Assessed | |
| Modify | | | Not Assessed | |
| Delete | | | Not Assessed | |
| Execute | | | Not Assessed | |
| Network | | | Not Assessed | |
| External Mutation | | | Not Assessed | |
| Deploy | | | Not Assessed | |
```

### 20.5 Approval Matrix 模板

```markdown
# APM-<NNNN> <批准矩阵名称>

<通用头部>

| Operation / Artifact | C02 Operation | Risk ID / Level | Permission Class | Trigger | Submitter / Executor | Human Accountable | Approver / Authority Source | Independence | Required Evidence | Response / Execution Window | Alternate Route |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | Approval Required | | | | | | | | |

Approval Evidence 必填：

- 动作、参数、对象、环境、Snapshot；
- 批准人、Authority Source、Outcome、理由；
- Risk、Evidence、条件、最大修改范围；
- 决定时间、到期、使用次数、撤销和记录位置。
```

### 20.6 Escalation Protocol 模板

```markdown
# ESP-<NNNN> <升级协议名称>

<通用头部>

| Trigger / STC | Severity | Immediate Stop | Notify Target | Decision Authority | Response Time | Required Information | Allowed Diagnostic | Decision Options | Resume Condition / Approver | Alternate Route |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

无响应处理：
- 保持 Fail-Closed；
- 禁止默认为批准；
- 到时限后转替代路线；
- 替代路线仍不可用时终止或保持隔离。
```

### 20.7 Stop Condition Register 模板

```markdown
# STC-<NNNN> <停止条件登记册名称>

<通用头部>

| Stop Condition ID | Member State | Signal | Agent / Operation / Scope | Immediate Action | Prohibited Continuation | Escalation Target / ESP | Required Evidence | Resume Approval | Trigger Status Location | Source / Review |
|---|---|---|---|---|---|---|---|---|---|---|
| STC-<NNNN>-S01 | Open | | | | | | | | C09 Run | |
```

### 20.8 Exception Authorization 模板

```markdown
# EXA-<NNNN> <例外授权摘要>

<通用头部；Artifact Type = Exception Authorization（EXA）；State 使用 DEC>

| 字段 | 内容 |
|---|---|
| C07 Rule ID | |
| Applicable Scope / Object / Operation / Environment | |
| Maximum Modification Scope | |
| Rationale / Evidence / Alternatives | |
| Risk ID / Level / Residual Risk / Risk Owner | |
| Compensating Control / Owner / Verification / Evidence | |
| Requester / Human Accountable / Reviewer | |
| Approver / Authority Source | |
| Start / Expiry / Usage Limit | |
| Review Plan | |
| Revocation Condition / Termination Handling | |
| RAR / Decision / Change / Gate Boundary | 本 EXA 不替代上述资产 |
| Decision Rationale / Objection | |
```

### 20.9 执行许可判定表

| 问题 | 是 | 否/未知 |
|---|---|---|
| 操作是否明确位于 C02 Agent Modification Boundary？ | 继续 | Not Assessed，停止 |
| COL/ARD/APM 是否 Approved/Baselined 且 Revision 一致？ | 继续 | 停止 |
| 是否为 Prohibited Action？ | 禁止 | 继续 |
| 是否触发第 10.7 节 Approval Event？ | Approval Required | 继续 |
| Risk 是否 High/Critical？ | Approval Required | 继续 |
| 目标、环境、Snapshot、Context、Permission 是否一致？ | 继续 | 停止 |
| 是否存在 Triggered Stop Condition？ | 停止并升级 | 继续 |
| APM 是否明确列为 Autonomous？ | 可在边界内执行 | Not Assessed，停止 |

### 20.10 停止与恢复速查表

| 阶段 | Agent 必须做 | Agent 禁止做 | 人类决定 |
|---|---|---|---|
| Stop 触发 | 立即停止、保存状态、封存证据、通知 | 继续、清理、覆盖、扩大重试 | 确认影响和 Authority |
| 诊断 | 仅执行预授权只读诊断 | 未批准修改、删除或外部变更 | 决定所需调查 |
| 处置 | 等待受控决定 | 自行风险接受或回滚 | 前滚、回滚、降级、终止 |
| Resume | 核对新 Context、Snapshot、授权和条件 | 使用旧批准恢复 | 有权人类签发 Resume Approval |
| 关闭 | 提交证据和剩余问题 | 隐藏失败或自行关闭高风险 Finding | Reviewer/Owner 复核关闭 |

### 20.11 质量检查清单模板

```markdown
| Check ID | 检查对象 | 通过条件 | 结果 | Evidence / Finding |
|---|---|---|---|---|
| C07-CHK-001 | 七类产物 | 身份、State、Revision、Owner 独立 | 待检查 | |
| C07-CHK-002 | Human Accountability | 每项高影响工作一个明确人类 Accountable | 待检查 | |
| C07-CHK-003 | Agent Role | 目的、Context、工具、边界、限制完整 | 待检查 | |
| C07-CHK-004 | 八类操作 | 全部判定且无 Not Assessed | 待检查 | |
| C07-CHK-005 | Least Privilege | Permission 不大于 Authorization | 待检查 | |
| C07-CHK-006 | Approval | 事件、Authority、证据、时限完整 | 待检查 | |
| C07-CHK-007 | Prohibition | 自批、扩权、越界、审计篡改被禁止 | 待检查 | |
| C07-CHK-008 | Independence | 高风险职责分离满足上游规则 | 待检查 | |
| C07-CHK-009 | Stop | 冲突、失效、异常、敏感、多 Agent 信号完整 | 待检查 | |
| C07-CHK-010 | Escalation | 目标、时限、Authority、替代路线完整 | 待检查 | |
| C07-CHK-011 | Resume/Rollback | 新鲜输入、人类批准、独立授权完整 | 待检查 | |
| C07-CHK-012 | Multi-Agent | 授权取交集、写入所有权和冲突处理明确 | 待检查 | |
| C07-CHK-013 | EXA | Rule、Risk、控制、期限、撤销和边界完整 | 待检查 | |
| C07-CHK-014 | Audit | 授权、批准、停止、恢复和历史可追踪 | 待检查 | |
| C07-CHK-015 | P2/Extension | 未裁剪；扩展适用性已复核 | 待检查 | |
```

### 20.12 正反例

正例：

> ARD-0007 仅允许 Coding Agent 在 `repo-A` 的指定工作分支读取全仓并修改 `docs/specs/` 下列明文件，最大 8 个文件；Execute 限于已列明的 Markdown 检查命令；Network、Delete、External Mutation 和 Deploy 为 Prohibited。Human Accountable 为产品负责人。目标 Commit、Context Revision 或文件数量变化即停止。扩大范围必须由 Authorization Owner 修改 COL/ARD/APM 并重新批准。

反例：

> Agent 可以访问项目需要的内容，自己修改相关文件并运行必要命令，遇到问题自行处理，完成后通知负责人。

反例没有准确 Scope、对象、操作类别、最大修改范围、风险、技术权限、批准事件、禁止项、停止条件、升级目标、有效期或 Human Accountable，禁止进入 Collaboration Ready。

### 20.13 参考的国际标准条款映射总表

| 国际标准 | 条款 | 本规范落地位置 | 采用方式 | 复核限制 |
|---|---|---|---|---|
| [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) | 4.1–4.4 情境、相关方、范围和 AIMS | 第 3、8、9.2、13.2 章 | 限定协作情境、相关方、范围和管理对象 | 不构成组织完整 AIMS |
| ISO/IEC 42001:2023 | 5.1–5.3 领导、方针、角色、责任与权限 | 第 7、10.2、13.3 章 | 明确人类 Accountable、Authority、角色和责任 | 不从公开目录推断具体权限 |
| ISO/IEC 42001:2023 | 6.1–6.3 风险、目标和变更策划 | 第 9.3、10.11、10.18、16.1 章 | 引用 C02 Risk，角色或授权变化重新评估 | C07 不建立第二 Risk Register |
| ISO/IEC 42001:2023 | 7.1–7.5 资源、能力、意识、沟通、文件化信息 | 第 6、7、10.16、13、16 章 | 记录 Agent 能力边界、沟通、版本和审计 | 模型自述不是能力证明 |
| ISO/IEC 42001:2023 | 8.1–8.2 运行策划与控制、AI 风险评估 | 第 9.5–9.9、10.5–10.13 章 | 运行前核对权限、批准、风险和停止 | 实际 Run 由 C09 管理 |
| [ISO/IEC 23894:2023](https://www.iso.org/standard/77304.html) | 4 风险管理原则 | 第 9.3、10.11、14 章 | 使授权随价值、信息和变化受控 | 不新增项目风险原则 |
| ISO/IEC 23894:2023 | 5.2–5.7 领导、整合、设计、实施、评价、改进 | 第 7、9、15、16 章 | 将人机协作控制嵌入生命周期和评审 | 不复制组织风险框架 |
| ISO/IEC 23894:2023 | 6.2 沟通与协商 | 第 10.13、13.6、20.6 章 | 规定升级信息、对象、时限和反馈 | 通知不等于批准 |
| ISO/IEC 23894:2023 | 6.3–6.5 范围/情境/准则、评估和处置 | 第 9.2–9.5、10.1、10.11 章 | 复用 C02 Scope、Risk Criteria、Level 和 Treatment | 禁止建立不兼容量表 |
| ISO/IEC 23894:2023 | 6.6–6.7 监测/评审、记录/报告 | 第 9.9、10.16、16 章 | 监测授权漂移并记录停止、恢复和撤销 | C09 保存运行证据 |
| ISO/IEC 23894:2023 | Annex A.2–A.4 问责、AI 专业能力、数据可用性与质量 | 第 6、7、10.2、13.4 章 | 明确人类问责、Agent 限制和 Context 边界 | 仅使用公开主题 |
| [ISO/IEC 38507:2022](https://www.iso.org/standard/56641.html) | 4.2–4.3 维持治理与问责 | 第 7、10.2、10.16 章 | Agent 可负责执行，人类承担最终问责 | 不定义组织法定治理结构 |
| ISO/IEC 38507:2022 | 5.2–5.5 AI 差异、生态、收益和约束 | 第 3、6、13.4 章 | 记录模型、工具、服务、依赖和限制 | 供应商声明不等于风险接受 |
| ISO/IEC 38507:2022 | 6.2 监督 | 第 9.6–9.9、10.7、10.12–10.13 章 | 建立批准、停止、升级和恢复控制 | 人类必须有权且获得充分信息 |
| ISO/IEC 38507:2022 | 6.3 决策 | 第 6、7、10.3、10.9 章 | 分离建议、执行、评审和批准 | Agent 建议不是决定 |
| ISO/IEC 38507:2022 | 6.4–6.7 数据、文化与价值、合规、风险 | 第 10.7–10.12、17.3 章 | 最小化数据访问并升级专业事项 | 专业结论由有权人类负责 |
| [ISO/IEC 5338:2023](https://www.iso.org/standard/81118.html) | 5.2–5.4 AI 系统、生命周期和过程概念 | 第 3、8、9.2、13.4 章 | 授权绑定系统、阶段、过程、输入和输出 | 不建立第二生命周期模型 |
| ISO/IEC 5338:2023 | 6.1 协议过程 | 第 3、7、18 章 | 明确外部方和 Agent 服务的责任与交接 | 不替代合同或采购记录 |
| ISO/IEC 5338:2023 | 6.2 组织项目使能过程 | 第 7、9、16、18 章 | 连接角色、资源、质量、知识和配置责任 | Configuration 由 C11 管理 |
| ISO/IEC 5338:2023 | 6.3 技术管理过程 | 第 8.3、10.11、10.16、18 章 | 分配决定、风险、配置、信息和质量责任 | 不复制 C10/C11/C12 |
| ISO/IEC 5338:2023 | 6.4 技术过程 | 第 7.2、9、10.14 章 | 不同生命周期活动使用受控 Agent Role | 不推断未公开子条款 |
| [ISO 31000:2018](https://www.iso.org/standard/65694.html) | 4 风险管理原则 | 第 10.11、14、16 章 | 使控制基于信息并随变化改进 | 官方状态待修订 |
| ISO 31000:2018 | 5.2–5.7 领导、整合、设计、实施、评价、改进 | 第 7、9、15、16 章 | 将 Agent 风险治理嵌入职责与评审 | 不建立组织风险框架 |
| ISO 31000:2018 | 6.2 沟通与协商 | 第 10.13、13.6 章 | 建立升级、咨询和反馈闭环 | 自动通知不替代决定 |
| ISO 31000:2018 | 6.3 范围、情境和准则 | 第 3、9.2–9.3、10.1、10.10 章 | 授权绑定精确 Scope、环境、准则和有效期 | 禁止空白和通配授权 |
| ISO 31000:2018 | 6.4–6.5 风险评估与处置 | 第 9.3、10.7、10.11、13.5 章 | 复用 C02 Risk、Treatment 和 Residual Risk | C07 不改变 L×I |
| ISO 31000:2018 | 6.6–6.7 监测/评审、记录/报告 | 第 9.9、10.16、16 章 | 监测权限漂移、停止、例外和撤销 | 运行遥测由 C09/E05 管理 |
| [ISO 9001:2015](https://www.iso.org/standard/62085.html) | 4.1–4.4 情境、相关方、范围和过程 | 第 3、8、9、13.2 章 | 记录协作目标、输入、输出、控制和相互作用 | 不构成组织完整 QMS |
| ISO 9001:2015 | 5.1–5.3 领导、方针、角色、责任与权限 | 第 7、10.2–10.3、13.3–13.5 章 | 明确人类 Owner、Accountable、Reviewer、Approver | 基线前复核替代状态 |
| ISO 9001:2015 | 6.1–6.3 风险、目标和变更策划 | 第 9.3、10.18、16.1 章 | 授权变化执行影响分析和重新批准 | 不复制 C11 Change Request |
| ISO 9001:2015 | 7.1–7.4 资源、能力、意识和沟通 | 第 7、10.13、13.4、13.6 章 | 记录 Agent/人员能力、工具限制和升级沟通 | 模型自述不证明能力 |
| ISO 9001:2015 | 7.5 文件化信息 | 第 11、13、16、20 章 | 保留标识、版本、批准、访问和历史 | 聊天不能提升为正式批准 |
| [ISO 9001:2015/Amd 1:2024](https://www.iso.org/standard/88431.html) | 4.1、4.2 气候变化相关性和相关方要求 | 第 9.2、9.3、17.3 章 | 适用时引用 C01/C02 的 Constraint、Risk 或 Need | C07 不重复识别气候风险 |
