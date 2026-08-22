# C02 建设事项与范围规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C02 |
| 英文名称 | Initiative and Scope Specification |
| 正式文件名 | `C02_Initiative_and_Scope_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-27 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3 |
| 生产前调研 | RVR-C02-0001 |
| 下游规范 | C03、C05、C06、C07、C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式修订、评审、批准、替代和基线记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定 Initiative 的创建、目标、价值假设、范围边界、Agent 修改边界、假设、约束、风险、成功指标、依赖、评审、暂停、终止、合并和演进规则。

本规范用于实现以下控制目标：

1. 使每个 Initiative 追踪到经过评审的 Product Intent、Product Goal 和 Problem；
2. 同时明确本次建设做什么、不做什么、以后再做什么以及 Agent 可以修改什么；
3. 在进入 PRD、Requirement 或 Agent 执行前识别假设、约束、风险和依赖；
4. 用成功指标、护栏、启动条件和终止条件控制建设投入；
5. 使范围变化、暂停、终止和合并保留责任、理由、影响、批准和历史。

## 3. 适用范围

本规范适用于：

- 从 C01 已评审的 Problem、Product Intent 和 Product Goal 建立新的 Initiative；
- 新能力、重大改进、迁移、替换、退役、实验或运营改进的建设边界；
- Initiative 的优先级、预期结果、计划时间范围和价值假设；
- In Scope、Out of Scope、Future Scope 和交付边界；
- Coding Agent 可以访问和修改的仓库、目录、服务、数据和操作类别；
- Initiative 级 Assumption、Constraint、Risk、Success Metric 和 Dependency；
- Initiative Ready 决策输入；
- Initiative 的暂停、恢复、终止、合并、完成和受控变更。

本规范同时适用于人类主导、Agent 辅助和多 Agent 参与的建设事项。

## 4. 不适用范围

以下内容不由本规范定义：

- Stakeholder Need、Evidence、Problem 和 Product Intent 的发现规则，由 C01 管理；
- PRD Package 和 Feature 的内容结构，由 C03 管理；
- 原子 Requirement 及其演进，由 C04 管理；
- Acceptance Criteria、Verification 和 Validation 方法，由 C05 管理；
- Technical Design 和 Architecture，由 C06 管理；
- 角色授权、工具权限和升级路径的完整模型，由 C07 管理；
- Agent Context 的组装和隔离，由 C08 管理；
- 具体命令、工具调用、重试、执行证据和 Agent Run，由 C09 管理；
- Decision、Traceability Matrix 和 Provenance 的统一机制，由 C10 管理；
- Change Request、配置、Baseline 和 Release 变更，由 C11 管理；
- Gate Decision、质量门禁和产品健康评价，由 C12 管理；
- 组织级项目组合、预算审批、供应商合同、法律意见或完整风险管理体系。

C02 可以引用上述对象，但禁止建立同名平行资产。

## 5. 规范性用语

### 5.1 关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。“建议”只表示非强制实践，不作为符合性判定依据。

### 5.2 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 已批准 Exception、Waiver 或 Risk Acceptance 的明确范围；
3. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
4. 本规范已批准或已基线版本；
5. 当前 Initiative 的已批准资产；
6. 模板、示例和非规范性实践。

冲突无法判定时必须停止进入 Initiative Ready，并提交人类决策。

### 5.3 可判定表达

所有强制语句必须能够通过受控资产、Trace Link、状态、数值、枚举条件、批准记录或检查结果直接判定。禁止使用没有判定条件的“尽量”“最好”“酌情”“快速”“合理”“适当”或“充分”。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| Initiative | 为实现一个或多个 Product Goal 而设立的可独立治理建设单元 | 不是 PRD、Feature、Project Task 或 Agent Run |
| Initiative Brief | 定义 Initiative 身份、目标、预期结果、价值假设、优先级、时间和启停条件的正式产物 | 不替代其他五类 C02 产物 |
| Scope Boundary | 对 In Scope、Out of Scope、Future Scope、交付边界和 Agent 修改边界的正式约束 | 不等同于 Product Definition |
| In Scope | 当前 Initiative 已批准承诺分析或交付的对象集合 | 每项必须可定位和判定完成 |
| Out of Scope | 当前 Initiative 明确禁止纳入的对象集合 | 空值不表示没有排除项 |
| Future Scope | 已识别但未对当前 Initiative 作出承诺的候选对象集合 | 禁止作为当前默认执行输入 |
| Agent Modification Boundary | 对 Agent 可访问、创建、修改、删除、执行、联网、外部变更和部署范围的操作约束 | 不能替代 C07 权限和 C09 Run 控制 |
| Deliverable Boundary | 对当前 Initiative 必须形成的交付物类别、完成条件和不包含内容的说明 | 不建立具体 Feature 或 Requirement |
| Value Hypothesis | 对预期结果如何产生用户价值或业务价值的可验证陈述 | 必须有证据来源或 Assumption 标记 |
| Start Condition | Initiative 可以进入下游建设的必要条件 | 不满足时禁止进入 Ready 或 Active |
| Pause Condition | 触发暂时停止下游工作的客观条件 | 必须同时定义恢复条件和复核日期 |
| Termination Condition | 触发停止 Initiative 且不再按原计划继续的客观条件 | 必须覆盖失败、失效和战略撤回情形 |
| Merge | 将两个或多个 Initiative 的未完成职责受控转移到新建或指定 Initiative | 原 Asset ID 和历史必须保留 |
| Initiative Disposition | 表示 Initiative 运行处境的业务字段 | 不是 DOC State，不得替代资产状态 |
| Assumption | 当前未达到既定证据门槛但作为计划输入的陈述 | 必须有验证方式、责任人和失效条件 |
| Constraint | 限制可选方案或执行范围的强制边界 | 必须说明来源、适用范围和解除条件 |
| Risk | 不确定性对 Initiative 目标、范围、指标、依赖或执行产生的影响 | 可以表示不利影响或机会 |
| Residual Risk | 实施当前控制和处置后仍然存在的 Risk | 必须重新评分并明确接受权限 |
| Risk Exposure | C02 内部使用的 Likelihood 与 Impact 乘积 | 不是 ISO 31000 规定的统一量表 |
| Initiative Success Metric | 判断 Initiative 是否达到预期结果的指标 | 专业化自 C01 Success Metric；不等同于 Acceptance Criterion |
| Initiative Guardrail Metric | 防止 Initiative 目标优化造成不可接受损害的指标 | 专业化自 C01 Guardrail Metric；必须定义阈值和触发动作 |
| Dependency | Initiative 成立、启动、执行或成功所依赖的外部对象、输入、人员、决定、系统或时间条件 | 必须记录提供方、需要日期和失败影响 |
| Dependency Readiness | Dependency 是否满足当前需要的结论字段 | 不是资产 State |

未在本章定义的公共术语以 VC-PPG-COM-001 为准。

## 7. 角色与职责

| 角色 | 强制职责 | 禁止事项 |
|---|---|---|
| Initiative Owner | 维护 Initiative Brief；协调六类产物；提交评审；处理范围、风险和依赖冲突 | 不得自行批准重大范围例外或自己的 Risk Acceptance |
| Scope Owner | 维护 Scope Boundary；确认受影响用户、模块、仓库、服务和操作边界 | 不得以空白或通配表达授予无限范围 |
| Risk Owner | 分析指定 Risk；提出处置；维护剩余风险和监控条件 | 不得删除反对意见、失败证据或未关闭 Risk |
| Dependency Owner | 确认 Dependency 提供方、满足条件、日期、失败影响和替代方案 | 不得把未确认依赖标记为 Confirmed |
| Metric Owner | 定义指标、数据源、计算方式、基线、目标、护栏和观察周期 | 不得用无法复核的数据声明成功 |
| Independent Reviewer | 检查目标、范围、Agent 边界、风险、指标、依赖和启停条件 | 不得评审自己是唯一作者且唯一责任人的全部内容 |
| Gate Approver | 按 C12 对 Initiative Ready、条件通过、拒绝、暂停或终止输入作出授权决定 | 不得绕过未关闭阻断项而口头批准 |
| Coding Agent | 整理输入、生成 Draft、运行检查、维护 Trace Link 候选和报告缺口 | 不得扩大 Scope、最终定优先级、接受 Risk、批准例外或作 Gate Decision |

同一人可以承担多个非冲突角色，但 Gate Approver 禁止与该 Initiative 的唯一编制者和唯一 Reviewer 为同一人。权限来源和替代安排由 C07 管理。

## 8. 管理对象与关系

### 8.1 管理对象

本规范管理六类正式产物：

1. Initiative Brief；
2. Scope Boundary Record；
3. Assumption & Constraint Register；
4. Risk Register；
5. Success Metric Plan；
6. Dependency Register。

Scope Item、Assumption Entry、Constraint Entry、Risk Entry、Metric Entry 和 Dependency Entry 是所属正式产物内的受控成员，不建立同义平行产物。

### 8.2 最低关系链

```text
Initiative Brief
  ├─ derives-from → Product Intent & Goal Record / Problem Definition
  ├─ depends-on → Scope Boundary Record / Assumption & Constraint Register
  ├─ depends-on → Risk Register / Success Metric Plan / Dependency Register
  └─ affected-by → Assumption Entry / Constraint Entry / Risk Entry

Product Definition
  └─ constrains → Initiative Brief

Scope Boundary Record
  ├─ derives-from → Initiative Brief
  └─ constrains → C03 PRD Package / C08 Context Manifest / C09 Agent Run

Success Metric Plan
  └─ derives-from → Product Intent & Goal Record / Initiative Brief

Initiative Brief
  └─ depends-on → Dependency Target

C03 PRD Package
  └─ derives-from → Initiative Brief
```

每条关系必须可反向查询。禁止使用 `related-to` 或中文“相关”作为正式关系。

### 8.3 产物一致性

六类产物可以在同一界面或物理文件中展示，但必须分别保留 Asset ID、Artifact Type、Owner、State、Revision、Trace Links、Access Classification、Retention Rule 和 History Reference。任一产物更新时必须记录其余五类产物是否受影响。

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
C01 Handoff
  → Intake and Eligibility
  → Draft Initiative Brief
  → Define Scope and Agent Boundary
  → Register Assumptions and Constraints
  → Assess Risks and Dependencies
  → Plan Success Metrics
  → Independent Review
  → Initiative Ready Decision
  → Handoff to C03/C05/C06/C08
  → Monitor and Control
  → Complete / Pause / Terminate / Merge
  → Preserve Learning and History
```

### 9.2 Intake and Eligibility

Initiative Owner 必须核验 C01 输入是否包含 Product Definition、Problem Definition、Product Intent & Goal Record、开放 Assumption、Evidence 局限和 Gate Decision。缺少输入时可以创建 Draft，但禁止进入 Initiative Ready。

### 9.3 Draft and Analysis

Initiative Owner 必须先建立 Initiative Brief，再建立其他五类产物。不得从功能清单直接生成 PRD 或 Agent Run。范围、Risk、Dependency 或 Metric 的分析发现上游 Problem 或 Goal 无效时，必须退回 C01 处理。

### 9.4 Review and Gate

Independent Reviewer 必须检查第 15 章全部阻断条件。Gate Approver 只能在阻断项为零时作出 Initiative Ready 通过决定；条件通过、Waiver 或 Risk Acceptance 必须由 C10、C12 及相应受控记录承接。

### 9.5 Handoff and Control

进入 C03 时必须提供当前有效的六类 C02 产物、Gate Decision 和开放问题。进入 Agent Context 时必须同时提供 Scope Boundary 的有效 Revision；仅有 Initiative 名称或自然语言摘要不得授权执行。

### 9.6 Completion and Learning

完成、暂停、终止或合并时必须记录实际结果、未完成 Scope、剩余 Risk、Dependency 结果、Metric 观察、下游影响和后续责任。新的学习必须回流 C01、C02、C11 或 C12，不得只保留在聊天或 Run 输出中。

## 10. 强制规则

### 10.1 Initiative 创建条件

1. 每个 Initiative 必须具有唯一 INI ID 和一个 Primary Product Goal。
2. 一个 Initiative 可以服务多个 Goal，但必须标识 Primary Goal 并说明目标间无冲突。
3. 必须引用至少一个 Problem Definition 和一个 Product Intent & Goal Record。
4. 必须记录 Product Definition 及其当前 Revision 对 Initiative 的约束。
5. 必须定义预期结果、Value Hypothesis、Owner、计划时间范围、Priority、Start Condition 和 Termination Condition。
6. 仅包含功能名称、技术方案、任务列表或截止日期的输入禁止成为 Initiative Ready。
7. 上游输入未达到 Approved 或 Baselined 时，Initiative 只能保持 Draft 或 In Review。

### 10.2 目标、结果和优先级

预期结果必须描述目标用户、业务或系统状态的可观察变化，不得只描述交付动作。Value Hypothesis 必须采用“如果完成当前 Scope，则在观察周期内产生某项可观察变化，因为某项 Evidence 或 Assumption”的结构。

Initiative Priority 使用以下受控值：

| 值 | 判定条件 |
|---|---|
| Critical | 存在有期限的法律、监管、合同、安全或重大事故义务，并有授权依据 |
| High | 已批准 Primary Goal 的时间窗口会在延期后关闭，或当前 Initiative 明确用于降低 High/Critical Risk，或依赖具有不可恢复的到期日 |
| Normal | 服务已批准 Goal，允许按常规顺序规划 |
| Low | 延期不违反已批准义务、Primary Goal 时间窗口或风险处置期限 |

Priority 必须记录判定依据、决定人和日期。Coding Agent 可以提出候选值，但禁止作最终 Priority 决定。

### 10.3 Scope Boundary

1. Scope Boundary Record 必须同时包含 In Scope、Out of Scope 和 Future Scope；没有条目时必须写明“None”及判定依据。
2. 每个 In Scope Item 必须包含对象、预期边界、受影响用户或模块、完成判定和 Owner。
3. 每个 Out of Scope Item 必须说明被排除对象、原因和重新进入条件。
4. Future Scope 只表示候选，不构成当前承诺、Requirement 或 Agent 授权。
5. Product Definition 的稳定边界禁止复制为 Initiative Scope；必须通过 Trace Link 引用。
6. In Scope 与 Out of Scope 存在重叠或冲突时必须阻断评审。
7. 未明确列入 In Scope 或 Agent Modification Boundary 的对象默认禁止修改。
8. “其他相关内容”“必要修改”“视情况调整”或“不要改无关代码”不得作为可执行范围表达。

### 10.4 Agent Modification Boundary

Scope Boundary Record 必须对以下每项给出 Allow、Deny 或 Approval Required：

| 操作类别 | 最低边界信息 |
|---|---|
| Read | 允许读取的仓库、目录、服务、数据集和敏感级别 |
| Create | 允许新建的路径、资源类型和命名边界 |
| Modify | 允许修改的路径、模块、配置项和接口 |
| Delete | 精确目标、可恢复方式、审批角色和验证条件 |
| Execute | 允许的命令类别、工作目录、参数边界和资源限制 |
| Network | 允许访问的域、服务、协议、数据方向和凭据来源 |
| External Mutation | 允许变更的外部系统、对象、幂等或回滚条件 |
| Deploy | 允许环境、发布对象、审批门禁和回滚条件 |

附加规则如下：

1. 空白、通配路径、仓库根目录或“全部”禁止解释为授权。
2. Delete、External Mutation 和 Deploy 禁止仅凭 C02 授权；必须同时满足 C07 权限和 C09 执行控制。
3. 真实命令、Tool Call、参数、重试和输出必须由 C09 记录；C02 只定义操作边界。
4. 访问个人信息、敏感数据、密钥或生产环境时必须触发 E02 适用性检查。
5. Agent 发现边界不足时必须停止并提交 Scope Change，不得自行扩大。

### 10.5 Assumption 与 Constraint

1. Assumption & Constraint Register 的每个成员必须标记 Member Type 为 Assumption 或 Constraint。
2. Assumption 必须包含陈述、来源、影响、置信依据、验证方法、验证期限、责任人和失效条件。
3. Constraint 必须包含陈述、来源、强制依据、适用 Scope、影响、解除条件、责任人和期限。
4. C01 Assumption 进入 C02 时必须保留来源 Trace Link；禁止复制后失去上游身份。
5. Assumption 被反证或 Constraint 变化时必须重新检查 Scope、Risk、Dependency、Metric 和 Gate Decision。
6. 高影响 Assumption 未有验证计划或 Constraint 来源无法定位时必须阻断 Initiative Ready。
7. Coding Agent 禁止把推断改写为 Constraint，禁止自行宣布 Assumption 已验证。

### 10.6 Risk 分类、评价与处置

每个 Risk Entry 必须使用“原因—不确定事件—对目标或范围的影响”结构，并选择一个 Primary Category：

| Primary Category | 覆盖对象 |
|---|---|
| Product | 用户价值、业务结果、采用、体验和产品方向 |
| Engineering | 架构、实现、质量、性能、安全技术、维护和交付可行性 |
| Agent | Agent 越权、幻觉、错误上下文、工具误用、不可审计操作和自动化失控 |
| Operational | 发布、运行、支持、恢复、容量、供应和持续服务 |

Security、Privacy、Compliance、Data、Financial 或 Reputational 可以作为 Risk Tag，但禁止替代四个 Primary Category。触发扩展规范时必须建立相应 Trace Link。

Likelihood 在当前计划时间范围内使用以下内部量表：

| 等级 | 概率区间 |
|---|---|
| L1 | 0% 至 5% |
| L2 | 大于 5% 至 20% |
| L3 | 大于 20% 至 50% |
| L4 | 大于 50% 至 80% |
| L5 | 大于 80% 至 100% |

无法给出概率时必须定义可观察频率或触发条件，并说明映射依据；禁止无依据打分。

Impact 使用以下内部量表：

| 等级 | 最低判定条件 |
|---|---|
| I1 | 不影响 Goal、Guardrail、关键路径或外部义务，可在当前 Scope 内吸收 |
| I2 | 影响一个或多个 In Scope Item，但不改变任何已批准 Goal、Guardrail、Blocking Dependency 或适用外部义务 |
| I3 | 使一项非 Primary Goal 无法实现，或触发已定义的 Pause Condition |
| I4 | 使 Primary Goal 无法实现，或突破 Guardrail Threshold，或使 Blocking Dependency、适用法律、监管或合同义务无法满足 |
| I5 | 造成 Initiative 不可行、不可逆损失，或触发严重安全、隐私、合规、运营后果 |

Risk Exposure 计算为 `Likelihood × Impact`：

| 分值 | 等级 | 强制处理 |
|---|---|---|
| 1–4 | Low | 记录并按计划复核 |
| 5–9 | Medium | 指定 Owner、监控条件和复核日期 |
| 10–15 | High | 制定处置行动、期限、剩余风险和升级路径 |
| 16–25 | Critical | 阻断 Initiative Ready，直到降低等级或形成授权的 Risk Acceptance Record |

Risk Treatment 使用 Avoid、Reduce、Share、Accept 或 Pursue。选择 Accept 时必须说明当前控制、Residual Risk、接受理由、监控指标、复核时间和失效条件；High 或 Critical 的接受必须形成 RAR。涉及法律、安全、隐私或监管义务时，通用 Gate Approver 无权替代相应专业授权。

### 10.7 Success Metric Plan

1. 每个 Initiative 必须至少有一个 Success Metric 和一个 Guardrail Metric，或具有已批准的不适用理由。
2. 每个 Metric Entry 必须包含 Goal、定义、公式或判定方法、数据源、基线值、目标值或阈值、观察周期、Owner 和决策规则。
3. Success Metric 必须面向预期结果；完成任务数、代码行数、发布日期或 Agent 调用次数禁止作为唯一成功指标。
4. Guardrail 超阈值时必须定义暂停、回滚、复核或终止动作。
5. 数据源不可用、未经授权或质量不满足判定要求时，必须建立 Dependency 或 Risk；关键指标不可计算时阻断 Initiative Ready。
6. Metric 的验证与确认方法由 C05 管理；C02 禁止把 Metric 直接改写为 Acceptance Criterion。

### 10.8 Dependency

Dependency Type 使用以下受控值：Internal Asset、Team or Approval、External System or Service、Vendor、Data、Legal or Compliance、Environment or Infrastructure。

每个 Dependency Entry 必须记录依赖对象、类型、提供方、需要日期、满足条件、失败影响、替代方案、Owner、Blocking 标记和 Dependency Readiness。

Dependency Readiness 使用：Not Assessed、Planned、Confirmed、Failed、Waived。该字段不是资产 State。

1. Blocking Dependency 在 Initiative Ready 前必须为 Confirmed 或具有批准的 Waiver。
2. Confirmed 必须具有提供方确认、可复核证据和有效期限。
3. Failed 必须触发 Risk、Scope 或 Termination 影响检查。
4. Waived 必须引用 EWR，并记录补偿控制和失效时间。
5. Dependency Target 必须通过 `depends-on` 从 Initiative 可查询。

### 10.9 启动、暂停、终止、合并与完成

Initiative Disposition 使用 Planned、Ready、Active、Paused、Terminated、Merged 或 Completed；它不得替代 DOC State。

| 动作 | 强制条件 |
|---|---|
| 启动 | Start Condition 全部满足；Initiative Ready Gate 通过；当前 Scope 和 Agent Boundary 可定位 |
| 暂停 | Pause Condition 触发或授权人决定；记录原因、影响、保护动作、恢复条件、Owner 和复核日期 |
| 恢复 | 恢复条件满足；暂停期间变化已完成影响检查；授权人确认 |
| 终止 | Termination Condition 触发或授权人决定；记录实际结果、停止动作、剩余义务、资产处理和通知 |
| 合并 | 建立目标 Initiative；完成 Scope、Risk、Metric、Dependency 和历史迁移；保留原 ID；目标 Initiative `supersedes` 或 `replaces` 来源 Initiative |
| 完成 | 已交付 Scope、剩余项、Metric 观察安排、Residual Risk、Dependency 结果和学习记录全部可定位 |

Paused、Terminated、Merged 的 Initiative 禁止作为新的 Agent Run 默认执行上下文。已 Baselined 产物的上述变化必须执行 C11。

### 10.10 范围变化

以下任一变化必须建立 Change Request 或受控修订，不得直接覆盖：

- Primary Goal、预期结果或 Value Hypothesis 改变；
- In Scope、Out of Scope 或 Future Scope 之间移动对象；
- Agent Modification Boundary 扩大；
- 新增 High 或 Critical Risk；
- Blocking Dependency 新增、失败或失效；
- Success Metric、Guardrail、目标值或观察周期实质改变；
- Start、Pause 或 Termination Condition 改变；
- Initiative 暂停、终止或合并；
- 影响已批准 C03 至 C12 资产。

影响分析必须覆盖目标、范围、成本或资源、时间、Risk、Dependency、Metric、Agent Context、下游资产和 Gate Decision。

### 10.11 评审与批准

1. 六类产物必须由 Independent Reviewer 评审。
2. Reviewer 必须记录输入版本、准则、发现项、结论和整改结果。
3. Initiative Ready 只能由 Gate Approver 决定。
4. Scope Exception、Waiver、Risk Acceptance、Pause、Termination 和 Merge 必须由授权人批准并形成受控记录。
5. 口头同意、聊天表态或 Agent 总结不得作为批准证据。
6. 任何批准必须指向确切 Revision 和 Snapshot；后续内容变化使原批准失效时必须重新评审。

### 10.12 Coding Agent 行为边界

Coding Agent 可以：

- 从 C01 当前有效输入生成 C02 Draft；
- 检查字段、关系、状态、范围冲突、Risk 分值和 Dependency 缺口；
- 提出 Priority、Risk、Metric、Scope 和变更候选；
- 生成差异、影响分析和评审材料；
- 在明确 Agent Modification Boundary 内准备下游草案。

Coding Agent 禁止：

- 编造 C01 Goal、Evidence、资源、预算、Dependency 确认或 Metric 数据；
- 将 Future Scope 自动移入 In Scope；
- 把空白或通配表达解释为无限授权；
- 自行扩大仓库、目录、服务、数据、外部系统或部署范围；
- 最终决定 Priority、Risk Acceptance、Waiver、Gate、Pause、Termination 或 Merge；
- 从未批准 Initiative 直接生成执行命令、PRD 基线或代码任务；
- 声称 C02、项目或组织已符合或通过国际标准认证。

## 11. 受控状态

### 11.1 正式产物状态

| 产物 | 类型代码 | 状态模型 | 允许状态 |
|---|---|---|---|
| Initiative Brief | INI | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Scope Boundary Record | SCP | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Assumption & Constraint Register | ACR | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Risk Register | RSK | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Success Metric Plan | SMP | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| Dependency Register | DEP | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |

Assumption Entry、Constraint Entry、Risk Entry 和 Dependency Entry 需要独立成员状态时使用 CASE：Open、In Progress、Blocked、Resolved、Closed、Reopened、Cancelled。成员结论、风险等级、Dependency Readiness 和 Initiative Disposition 必须使用各自字段，禁止冒充 State。Metric Entry 的治理状态由所属 Success Metric Plan 的 DOC State 表示，不设置独立 State。

### 11.2 状态转换规则

1. 状态转换必须遵循 VC-PPG-COM-002。
2. 六类产物未全部达到 Approved 或 Baselined 时禁止作出无条件 Initiative Ready。
3. Changes Required 必须记录 Finding、Owner、整改期限和复核结果。
4. Baselined 内容变化必须建立 Change Request 和新 Revision，禁止退回 Draft 原位覆盖。
5. Rejected、Superseded 或 Retired 资产禁止作为当前默认输入，但必须保留历史。
6. Initiative Disposition 变化不得自动改变 DOC State；两者必须分别记录并执行适用的变更控制。

## 12. 必需产物

| 产物 | 目的 | 最低创建条件 | 主要下游 |
|---|---|---|---|
| Initiative Brief | 定义建设事项身份、目标、结果、价值、优先级和启停条件 | C01 Goal 被提出进入建设规划 | C03、C10、C12 |
| Scope Boundary Record | 约束交付范围和 Agent 修改范围 | Initiative Brief 创建后立即建立 | C03、C08、C09、C11 |
| Assumption & Constraint Register | 管理计划不确定性和强制边界 | 存在任一 Assumption 或 Constraint；无成员时仍需空登记册及理由 | C03、C06、C11、C12 |
| Risk Register | 识别和处理 Initiative Risk | 每个 Initiative 必须创建 | C05、C06、C09、C12、E02–E05 |
| Success Metric Plan | 定义结果、护栏、观察和判定 | Initiative 具有预期结果时必须创建 | C05、C12、E03、E05 |
| Dependency Register | 管理成立、启动和执行依赖 | 每个 Initiative 必须创建；无依赖时记录核验范围和结论 | C03、C06、C09、C12 |

P2 档位禁止合并 Initiative Brief、Scope Boundary Record、Risk Register 或其他 C02 产物的独立身份。

## 13. 产物必填信息

### 13.1 通用必填信息

每项正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C02 类型专属要求。

### 13.2 Initiative Brief

必须包含：

- INI ID 和 Name；
- Product Definition Revision；
- Primary Goal 和其他 Goal 引用；
- Product Intent 和 Problem 引用；
- Problem Summary；
- Expected Outcome；
- Value Hypothesis 及 Evidence 或 Assumption；
- Initiative Priority、依据、决定人和日期；
- Initiative Owner；
- Planned Time Range；
- Start Condition；
- Pause Condition 和 Resume Condition；
- Termination Condition；
- Initiative Disposition；
- 六类 C02 产物当前 Revision；
- State、Revision、评审和批准记录。

### 13.3 Scope Boundary Record

必须包含：

- SCP ID 和 INI ID；
- In Scope Item 集合及完成判定；
- Out of Scope Item 集合及重新进入条件；
- Future Scope Item 集合；
- Deliverable Boundary；
- 受影响用户、模块、接口和数据；
- 允许 Agent 修改的仓库、Commit 或 Baseline、目录、服务和资源；
- Read、Create、Modify、Delete、Execute、Network、External Mutation、Deploy 的权限判定；
- 明确禁止的路径、资源、操作和环境；
- Scope Exception 审批方式；
- Scope Owner；
- State、Revision、评审和批准记录。

### 13.4 Assumption & Constraint Register

登记册必须包含：

- ACR ID、INI ID、Register Owner；
- Current Revision、State 和批准记录；
- Assumption Entry 与 Constraint Entry 集合。

每个成员必须包含：

- Entry ID 和 Member Type；
- 陈述和来源；
- 适用 Scope 和影响资产；
- 影响说明；
- Assumption 的置信依据、验证方法、期限、责任人和失效条件；
- Constraint 的强制依据、解除条件、期限和责任人；
- 关联 Risk、Dependency 和 Scope Item；
- Evidence 或 Decision 引用；
- 成员 State、结论和历史。

### 13.5 Risk Register

登记册必须包含：

- RSK ID、INI ID、Risk Context、Risk Criteria 和 Register Owner；
- Current Revision、State 和批准记录；
- Risk Entry 集合。

每个 Risk Entry 必须包含：

- Risk ID；
- Primary Category 和 Risk Tag；
- 原因、不确定事件和影响；
- 受影响 Goal、Scope、Metric、Dependency 或资产；
- Evidence 和 Assumption；
- Likelihood、Impact、评分依据、Risk Exposure 和等级；
- 当前控制；
- Treatment、行动、责任人和期限；
- Trigger Condition 和 Monitoring Metric；
- Residual Likelihood、Residual Impact、Residual Risk 和复核日期；
- Risk Acceptance 或 Waiver 引用；
- 成员 State 和历史。

### 13.6 Success Metric Plan

计划必须包含：

- SMP ID、INI ID、Primary Goal 和 Metric Owner；
- 测量边界、总体观察周期、数据授权和质量限制；
- Current Revision、State 和批准记录；
- Metric Entry 集合。

每个 Metric Entry 必须包含：

- Metric ID 和类型：Success 或 Guardrail；
- 关联 Goal 和 Expected Outcome；
- 指标定义、单位、计算公式或客观判定方法；
- 数据来源、数据 Owner 和采集频率；
- Baseline Value、Target Value 或 Guardrail Threshold；
- Observation Period；
- Metric Owner；
- Decision Rule、Trigger Action 和失效条件；
- 数据质量、隐私和 Dependency 限制；
- 成员变更历史。

### 13.7 Dependency Register

登记册必须包含：

- DEP ID、INI ID、Register Owner；
- Current Revision、State 和批准记录；
- Dependency Entry 集合。

每个 Dependency Entry 必须包含：

- Dependency ID 和 Type；
- Dependency Target 和提供方；
- 需要日期和满足条件；
- 证据、确认人、确认日期和有效期限；
- Blocking 标记；
- 失败影响和替代方案；
- Dependency Owner；
- Dependency Readiness；
- 关联 Risk、Scope、Metric 和 Decision；
- 成员 State 和历史。

## 14. 质量准则

### 14.1 单项产物质量

| 产物 | 必须满足的质量条件 |
|---|---|
| Initiative Brief | Goal 和 Problem 可追踪；结果不是任务；价值假设可验证；优先级有依据；启停条件可判定 |
| Scope Boundary Record | In、Out、Future 同时存在；Agent 边界可操作；默认拒绝空白范围；例外审批明确 |
| Assumption & Constraint Register | 成员类型分离；来源可定位；Assumption 可验证；Constraint 可解除或复核；影响可查询 |
| Risk Register | 四类 Risk 已检查；评分有依据；处置、剩余风险和监控完整；高风险有授权路径 |
| Success Metric Plan | 指标面向结果；公式和数据源可复核；基线、目标、护栏、周期和规则完整 |
| Dependency Register | 对象和提供方明确；Blocking 可判定；确认有证据和期限；失败有替代或终止处理 |

### 14.2 资产集合质量

C02 资产集合必须：

- 只服务于已批准或已基线的 Product Goal；
- 不存在没有 Problem 或 Intent 的 Initiative；
- 不存在未归类的 Scope Item；
- 不存在空白或通配 Agent Modification Boundary；
- 不存在无验证计划的高影响 Assumption；
- 不存在来源不明的 Constraint；
- 不存在没有 Owner、Treatment 或 Residual Risk 的 High/Critical Risk；
- 不存在没有基线、目标、周期或 Owner 的关键 Metric；
- 不存在未确认且无 Waiver 的 Blocking Dependency；
- 能执行 Goal → Initiative → Scope/Risk/Metric/Dependency → C03/C05/C09 的正向和反向查询。

### 14.3 可验证表达

每项强制结论必须至少满足以下一种方式：

- 具有数值、公式、阈值和观察窗口；
- 具有枚举条件和客观通过规则；
- 具有可复核 Evidence、Decision 或确认记录；
- 具有批准的不适用理由、责任人、补偿控制和失效时间。

## 15. 验证与符合性检查

### 15.1 自动检查

自动检查至少包括：

1. 六类正式产物是否存在且类型代码唯一；
2. 通用和专属必填信息是否为空；
3. Asset ID、Member ID 和 Revision 是否唯一；
4. State 是否属于允许状态；
5. Initiative 是否断开 Product Goal、Intent 或 Problem；
6. In Scope、Out of Scope 和 Future Scope 是否缺失或冲突；
7. Agent Modification Boundary 是否含空白、通配或未判定操作类别；
8. Assumption 是否缺少方法、期限、责任人或失效条件；
9. Constraint 是否缺少来源、适用范围或解除条件；
10. Risk Exposure 计算与等级是否一致；
11. High/Critical Risk 是否缺少处置、Owner、Residual Risk 或授权记录；
12. Metric 是否缺少公式、数据源、基线、目标、周期、Owner 或规则；
13. Blocking Dependency 是否未确认且无 Waiver；
14. Start、Pause、Resume 和 Termination Condition 是否缺失；
15. 是否存在 Future Scope 被下游当作当前授权；
16. 是否存在未经 Change Request 扩大的 Scope；
17. 是否存在无语义 Trace Link 或禁止的模糊词。

### 15.2 人工评审

人工评审必须检查：

- Initiative 是否真实服务 Product Goal，而不是为预定 Solution 寻找理由；
- Expected Outcome 和 Value Hypothesis 是否可观察和可反证；
- Scope 是否覆盖用户、模块、接口、数据和交付边界；
- Agent 权限矩阵是否与真实仓库、服务和环境一致；
- Assumption、Constraint、Risk 和 Dependency 是否被错误合并；
- Risk Category、Likelihood、Impact、Treatment 和 Residual Risk 是否有依据；
- Success Metric 和 Guardrail 是否能支持继续、暂停或终止决定；
- Blocking Dependency 的确认是否来自真实提供方；
- 资源、时间、外部义务和气候相关输入是否完成影响分析；
- Pause、Termination 和 Merge 是否具有可执行保护与交接动作；
- Agent 是否执行了超出授权的判断、批准或范围扩展。

### 15.3 Initiative Ready 阻断条件

存在任一条件时必须拒绝 Initiative Ready：

- C01 必需输入缺失、失效或未达到 Approved/Baselined；
- Primary Goal、Problem、Expected Outcome 或 Value Hypothesis 缺失；
- 六类 C02 产物缺失或未完成评审；
- In Scope、Out of Scope 或 Future Scope 缺失；
- Agent Modification Boundary 为空、使用通配或存在未判定操作类别；
- 高影响 Assumption 没有验证计划；
- Constraint 来源或适用范围无法定位；
- Critical Risk 未降低且无授权 RAR；
- High Risk 没有处置、Owner、期限或 Residual Risk；
- Blocking Dependency 不是 Confirmed 且无批准 Waiver；
- 关键 Success Metric 或 Guardrail 不可计算；
- Start Condition 或 Termination Condition 缺失；
- 存在未解决的重大 Scope 冲突；
- 隐私、安全、数据、架构或运营扩展适用性为待判定；
- 资产由 Coding Agent 自行批准；
- 国际标准版本状态已变化但尚未完成影响分析。

### 15.4 符合性声明限制

通过本章检查只能声明“符合 C02 V0.1 的内部规则”。禁止据此声明符合、认证或通过 ISO/IEC/IEEE 29148、ISO/IEC/IEEE 12207、ISO 31000 或 ISO 9001。

## 16. 追踪与记录要求

### 16.1 最低追踪覆盖

| 受控方向 | 必须追踪到 | 正式关系 |
|---|---|---|
| Initiative Brief → Product Intent、Goal、Problem | 上游 C01 资产 | `derives-from` |
| Product Definition → Initiative Brief | 稳定产品边界 | `constrains` |
| Initiative Brief → 其他五类 C02 产物 | 当前有效计划、范围、登记册和指标版本 | `depends-on` |
| Scope Boundary Record → Initiative Brief | 建设事项来源 | `derives-from` |
| Scope Boundary Record → C03 PRD、C08 Context、C09 Run | 下游范围和操作边界 | `constrains` |
| ACR、RSK、SMP 或 DEP → 成员 Entry | 登记册或计划成员 | `contains` |
| Initiative、Scope、Metric 或 Dependency → Assumption、Constraint 或 Risk Entry | 受不确定性、强制边界或风险影响的资产 | `affected-by` |
| Entry → 来源资产 | 成员陈述、风险或依赖的来源 | `derives-from` |
| Evidence 或 Treatment Decision → Assumption、Constraint 或 Risk Entry | 验证、处理或决策范围 | `addresses` |
| Success Metric Plan → Product Goal、Initiative | 指标计划来源 | `derives-from` |
| Product Goal → C05 Validation Result | 真实结果确认 | `validated-by` |
| Initiative Brief → Dependency Target | 实际依赖对象 | `depends-on` |

### 16.2 记录保留

必须保留：

- C01 输入的 Asset ID、Revision 和 Snapshot；
- 六类 C02 产物的全部 Revision；
- Scope Item 的增加、删除、移动和冲突解决历史；
- Agent Modification Boundary 的每次批准和收缩或扩大记录；
- Assumption 验证和 Constraint 解除依据；
- Risk 评分依据、反对意见、处置、Residual Risk 和 RAR；
- Metric 定义、数据版本、基线、观察和判定结果；
- Dependency 确认、失败、延期、替代和 Waiver；
- Review Record、Gate Decision、Change Request、Exception、Waiver、Pause、Termination 和 Merge Decision；
- Agent 生成草案与人类批准结果的区分记录。

涉及个人信息或敏感数据时，保留要求必须同时服从 E02；禁止以追踪为理由无限期保留不必要的敏感原始数据。

### 16.3 影响与变更追踪

C01 Goal、Problem、Evidence 或 Product Definition 变化时，Initiative Owner 必须检查全部 C02 产物和下游资产。C02 任一 Approved 或 Baselined 资产变化时必须按 C11 处理，并更新 Traceability Matrix、Context Manifest 和受影响 Gate Decision。

## 17. 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C02 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

每个交付任务都必须具有最小 Scope、Agent Modification Boundary、验收角色和 C02 Risk Level；这些信息可以作为 ECP 或任务定义载体中的结构化章节存在。INI、ACR、RSK、SMP、DEP 只有在对应事项、假设/约束、风险、指标或依赖实际存在时才 `Create/Revise`，已有有效 Baseline 时 `Reference`。

Task Profile 使用 DS/DT/Change Surfaces/Risk/Extension/Baseline/Mode 多维判定，禁止再建立单一任务挡位。Unknown 风险、安全、数据、发布或不可逆影响不得默认为 Low 或 N/A。

### 17.1 当前 P2 决议

本项目采用 P2，必须遵守：

1. 被触发的六类 C02 产物保持独立身份；
2. 可以在同一物理文件、系统或仪表盘中展示，但禁止合并 Asset ID、State、Revision 和 Trace Link；
3. 禁止合并 Initiative Brief、Scope Boundary Record 和 Risk Register 代替独立产物；
4. 模板可以作为本规范附录；
5. Agent Modification Boundary、Risk、Metric、Dependency、变更记录和 Gate 输入不得裁剪。

### 17.2 未来裁剪

目标产品申请 P1 或 P3 时必须通过 Change Request 或项目级适用性决议。裁剪只能改变载体和评审深度，不得删除 Initiative、Scope、Assumption、Constraint、Risk、Metric、Dependency、永久标识、责任人、历史、Agent 边界、启停条件和追踪控制。

## 18. 扩展接口

| 规范 | 触发接口 | C02 必须输出或接收的信息 |
|---|---|---|
| C01 | Problem、Intent、Goal 或 Evidence 变化 | 接收当前 Revision；输出建设反馈、失效 Assumption 和新 Problem 候选 |
| C03 | Initiative Ready 后建立 PRD | 输出六类 C02 产物、Gate Decision 和开放问题；PRD 禁止扩大 Scope |
| C04 | 下游建立 Requirement | 输出 Goal、Scope、Constraint、Risk 和 Trace 边界，不直接创建 Requirement |
| C05 | 建立验收、验证与确认 | 输出 Success Metric、Guardrail、Risk、Assumption 和观察周期 |
| C06 | 技术设计需要边界 | 输出 Scope、Constraint、Risk、Dependency 和禁止修改项 |
| C07 | 需要权限与批准 | 输出 Owner、Approver、操作类别、Scope Exception 和升级条件 |
| C08 | 组装 Agent Context | 输出允许资产、Revision、仓库边界、敏感级别和失效条件 |
| C09 | Agent 执行 | 输出 Agent Modification Boundary、操作判定、Start/Pause/Termination Condition；接收 Run 证据 |
| C10 | 决策和追踪 | 输出关系候选、Priority、Risk、Scope、Pause、Termination 和 Merge Decision 输入 |
| C11 | 范围或 Baseline 变化 | 输出 Change Request、影响范围和当前 Snapshot |
| C12 | Initiative Ready 和产品健康 | 输出检查结果、Residual Risk、Blocking Dependency 和 Metric Plan |
| E01 | 系统、服务或复杂架构成为关键 Dependency | 输出架构范围、边界和技术 Risk |
| E02 | 安全、隐私、合规、敏感数据或显著 AI 风险 | 输出 Risk、数据范围、授权、外部义务和阻断项 |
| E03 | Metric、数据产品、RAG 或训练数据参与 | 输出数据语义、质量、来源、授权和 Dependency |
| E04 | 多 Agent、长期维护或正式记录激活 | 输出 Source、Revision、Freshness、Access 和 Replacement 关系 |
| E05 | 运行反馈、事故、SLO 或发布结果回流 | 接收 Observation、Incident、Metric 和 Dependency 结果 |

## 19. 参考标准

### 19.1 R1 国际标准

| 标准 | 完整名称 | 适用主题 | 适用性限制 |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | Systems and software engineering — Life cycle processes — Requirements engineering | Goal、Constraint、业务分析、信息项和追踪 | 已进入修订流程；替代版发布后必须影响分析 |
| ISO/IEC/IEEE 12207:2026 | Systems and software engineering — Software life cycle processes | 生命周期规划、评估控制、决策、风险、配置和测量 | C02 不声明覆盖完整软件生命周期过程 |
| ISO 31000:2018 | Risk management — Guidelines | 风险原则、情境、准则、识别、分析、评价、处置、监测和记录 | 指南不可用于认证；已进入修订流程 |
| ISO 9001:2015/Amd 1:2024 | Quality management systems — Requirements — Amendment 1: Climate action changes | 过程、角色、目标、风险、变更、运行策划、外部依赖和监测 | 不构成 QMS 认证；2026 新版状态必须复核 |

### 19.2 来源与复核边界

版本和条款目录依据 ISO 官方页面、ISO Online Browsing Platform、ISO 技术委员会材料和 RVR-C02-0001 核验。未取得合法完整标准文本时，本规范只声明参考和条款主题对齐，不声明完整条款符合性。

## 20. 附录

### 20.1 通用资产头模板

所有 C02 模板必须先包含：

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
| Applicable Scope | <Product、Initiative 和时间> |
| Trace Links | <受控关系> |
| Access Classification | <访问级别> |
| Retention Rule | <保留规则> |
| History Reference | <历史和变更引用> |
```

### 20.2 Initiative Brief 模板骨架

```markdown
| 字段 | 内容 |
|---|---|
| INI ID / Name | |
| Product Definition Revision | |
| Primary Goal / Other Goals | |
| Product Intent / Problem | |
| Problem Summary | |
| Expected Outcome | |
| Value Hypothesis / Basis | |
| Priority / Basis / Decider / Date | |
| Initiative Owner | |
| Planned Time Range | |
| Start Condition | |
| Pause / Resume Condition | |
| Termination Condition | |
| Initiative Disposition | Planned |
| SCP / ACR / RSK / SMP / DEP Revision | |
| Review / Approval | |
```

### 20.3 Scope Boundary Record 模板骨架

```markdown
| Scope Item ID | Category | Object | Boundary or Exclusion | Affected User or Module | Completion or Re-entry Condition | Owner |
|---|---|---|---|---|---|---|
| SCP-<NNNN>-S01 | In Scope | | | | | |
| SCP-<NNNN>-S02 | Out of Scope | | | | | |
| SCP-<NNNN>-S03 | Future Scope | | | | | |

| Operation | Decision | Exact Boundary | Approval Role | Validation |
|---|---|---|---|---|
| Read | | | | |
| Create | | | | |
| Modify | | | | |
| Delete | | | | |
| Execute | | | | |
| Network | | | | |
| External Mutation | | | | |
| Deploy | | | | |

| Additional Field | Content |
|---|---|
| Deliverable Boundary | |
| Prohibited Path / Resource / Action | |
| Scope Exception Method | |
| Scope Owner | |
| Review / Approval | |
```

### 20.4 Assumption & Constraint Register 模板骨架

```markdown
| Entry ID | Member Type | Statement | Source | Scope and Impact | Validation or Release Condition | Owner | Due Date | Risk / Dependency | State / Conclusion |
|---|---|---|---|---|---|---|---|---|---|
| ACR-<NNNN>-A01 | Assumption | | | | | | | | Open |
| ACR-<NNNN>-C01 | Constraint | | | | | | | | Open |
```

Assumption 另填 Confidence Basis、Validation Method 和 Invalidation Condition；Constraint 另填 Mandatory Basis 和 Evidence or Decision。

### 20.5 Risk Register 模板骨架

```markdown
| Risk Criteria Field | Content |
|---|---|
| Initiative Time Horizon | |
| Likelihood Evidence Rule | |
| Impact Threshold Rule | |
| Risk Acceptance Authority | |
| Review Frequency | |

| Risk ID | Category / Tags | Cause — Event — Impact | Affected Asset | L | I | Exposure / Level | Current Control | Treatment / Owner / Due | Residual Risk | Trigger / Monitor | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RSK-<NNNN>-R01 | | | | | | | | | | | Open |
```

### 20.6 Success Metric Plan 模板骨架

```markdown
| Metric ID | Type | Goal / Outcome | Definition / Formula | Data Source / Owner | Baseline | Target or Guardrail | Observation Period | Metric Owner | Decision Rule / Action |
|---|---|---|---|---|---|---|---|---|---|
| SMP-<NNNN>-M01 | Success | | | | | | | | |
| SMP-<NNNN>-M02 | Guardrail | | | | | | | | |
```

### 20.7 Dependency Register 模板骨架

```markdown
| Dependency ID | Type | Target / Provider | Need Date | Fulfilment Condition | Confirmation Evidence / Expiry | Blocking | Failure Impact | Alternative | Owner | Readiness | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEP-<NNNN>-D01 | | | | | | Yes / No | | | | Not Assessed | Open |
```

### 20.8 C02 质量检查清单

| 检查 ID | 检查项 | 通过条件 | 结果 |
|---|---|---|---|
| C02-CHK-001 | 上游追踪 | Initiative 指向有效 Product Definition、Intent、Goal 和 Problem | 待检查 |
| C02-CHK-002 | Primary Goal | 唯一且无目标冲突 | 待检查 |
| C02-CHK-003 | Expected Outcome | 描述可观察变化而非任务 | 待检查 |
| C02-CHK-004 | Value Hypothesis | 有 Evidence 或 Assumption 和反证条件 | 待检查 |
| C02-CHK-005 | Priority | 值、依据、决定人和日期完整 | 待检查 |
| C02-CHK-006 | Scope 三分 | In、Out、Future 均有明确记录 | 待检查 |
| C02-CHK-007 | Scope 冲突 | 无重叠、冲突和模糊兜底词 | 待检查 |
| C02-CHK-008 | Agent 边界 | 八类操作均为 Allow、Deny 或 Approval Required | 待检查 |
| C02-CHK-009 | 危险操作 | Delete、External Mutation、Deploy 有额外授权 | 待检查 |
| C02-CHK-010 | Assumption | 方法、期限、Owner 和失效条件完整 | 待检查 |
| C02-CHK-011 | Constraint | 来源、Scope、解除条件和 Owner 完整 | 待检查 |
| C02-CHK-012 | Risk 分类 | Product、Engineering、Agent、Operational 均已检查 | 待检查 |
| C02-CHK-013 | Risk 评价 | L、I、依据、Exposure 和等级一致 | 待检查 |
| C02-CHK-014 | Risk 处置 | High/Critical 有处置、Residual Risk 和授权路径 | 待检查 |
| C02-CHK-015 | Metric | Success、Guardrail、数据、基线、目标、周期和规则完整 | 待检查 |
| C02-CHK-016 | Dependency | Blocking 项均 Confirmed 或有批准 Waiver | 待检查 |
| C02-CHK-017 | 启停条件 | Start、Pause、Resume、Termination 可判定 | 待检查 |
| C02-CHK-018 | 六类产物 | 独立 ID、State、Revision 和 Trace Link 完整 | 待检查 |
| C02-CHK-019 | 变更控制 | Approved/Baselined 变化均进入 C11 | 待检查 |
| C02-CHK-020 | Agent 权限 | Agent 未扩大 Scope、未接受 Risk、未自行批准 | 待检查 |
| C02-CHK-021 | 标准新鲜度 | 29148、31000、9001 替代状态已在基线前复核 | 待检查 |

### 20.9 正反例

正例：

> Primary Goal：在 2026-Q4 将目标用户完成关键任务的成功率从已核验基线提高到批准目标，同时 Guardrail 保持严重支持事件不超过阈值。In Scope 明确任务流程和两个服务；Out of Scope 明确计费系统；Agent 仅可修改指定仓库的两个目录，Delete 和 Deploy 为 Approval Required。关键 Dependency 已由提供方确认，Critical Risk 为零。

该表达具有 Goal、结果、Metric、Scope、Agent Boundary、Dependency 和 Risk 判定，可以进入评审。

反例：

> 做一个新的智能平台，Agent 可以修改必要代码，效果好就上线，风险后续再看。

该表达没有上游 Goal、可观察结果、In/Out/Future Scope、精确修改边界、Risk、Metric、Dependency、启动或终止条件，禁止进入 Initiative Ready。

### 20.10 参考的国际标准条款映射总表

| 国际标准 | 条款 | 本规范落地位置 | 采用方式 | 复核限制 |
|---|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | 4.4 信息项内容符合性 | 第 12、13、15、20 章 | 为六类 C02 产物规定内容和检查条件 | 完整符合性需合法全文逐条复核 |
| ISO/IEC/IEEE 29148:2018 | 4.5 裁剪符合性 | 第 17 章 | 明确 P2 和未来裁剪边界 | 不声明满足标准全部裁剪要求 |
| ISO/IEC/IEEE 29148:2018 | 5.2 需求基础 | 第 6、10.1、10.5 章 | 区分 Goal、Constraint、Assumption、Scope 和 Requirement | Requirement 由 C04 管理 |
| ISO/IEC/IEEE 29148:2018 | 5.4 Requirement 信息项 | 第 8、12、13 章 | 将 Goal、Constraint 和范围输入作为受控资产 | 不建立原子 Requirement 信息项 |
| ISO/IEC/IEEE 29148:2018 | 6.2 业务或任务分析过程 | 第 9、10.1、10.2 章 | 连接 Problem、Intent、Goal、价值假设和预期结果 | 不替代完整业务分析过程 |
| ISO/IEC/IEEE 29148:2018 | 6.6 需求管理 | 第 10.10、16、18 章 | 管理范围和约束变化及追踪 | 配置与 Baseline 由 C11 管理 |
| ISO/IEC/IEEE 29148:2018 | 7、8 信息项及编写指南 | 第 12、13、20 章 | 定义产物、模板和检查清单 | 不复制标准模板或正文 |
| ISO/IEC/IEEE 12207:2026 | 4.3 裁剪符合性 | 第 17 章 | 固定 P2 过程和产物边界 | 不声明完整过程符合性 |
| ISO/IEC/IEEE 12207:2026 | 5.4 生命周期概念 | 第 9、10.9、11 章 | 定义启动、暂停、恢复、终止、合并和完成 | 不选择组织级生命周期模型 |
| ISO/IEC/IEEE 12207:2026 | 5.7 过程应用 | 第 9、10.10、16.3 章 | 支持并发、迭代和增量并要求变化受控 | 不规定具体研发方法 |
| ISO/IEC/IEEE 12207:2026 | 6.3.1 项目规划过程 | 第 10.1–10.9、12、13 章 | 规划目标、范围、风险、指标、依赖和时间 | 不替代完整项目计划 |
| ISO/IEC/IEEE 12207:2026 | 6.3.2 项目评估与控制过程 | 第 9.5、10.9、10.10、15 章 | 设置检查、偏差、暂停和终止条件 | 执行监测由 C09/C12 管理 |
| ISO/IEC/IEEE 12207:2026 | 6.3.3 决策管理过程 | 第 7、10.2、10.9、10.11 章 | 管理优先级、例外、风险接受、暂停、终止和合并 | Decision 由 C10 管理 |
| ISO/IEC/IEEE 12207:2026 | 6.3.4 风险管理过程 | 第 10.6、13.5、15 章 | 识别、评价、处置、剩余风险和监控 | 结合 ISO 31000 细化 |
| ISO/IEC/IEEE 12207:2026 | 6.3.5 配置管理过程 | 第 10.10、11、16.3 章 | Approved/Baselined 变化进入配置控制 | 具体机制由 C11 管理 |
| ISO/IEC/IEEE 12207:2026 | 6.3.7 测量过程 | 第 10.7、13.6、15 章 | 定义基线、目标、护栏、周期和判定规则 | 验证与确认由 C05 管理 |
| ISO 31000:2018 | 4 风险原则 | 第 6、10.6、14 章 | 风险服务于目标、决策和价值保护 | ISO 31000 不用于认证 |
| ISO 31000:2018 | 5.3 风险整合 | 第 8、10.6、18 章 | Risk 进入 Initiative、Scope、Dependency、Metric 和 Gate | 不建立组织级风险体系 |
| ISO 31000:2018 | 5.4 风险框架设计 | 第 7、10.6、13.5 章 | 定义情境、准则、角色和资源输入 | 只适用于 Initiative 级 |
| ISO 31000:2018 | 6.1 风险过程总则 | 第 9、10.6、16 章 | 风险贯穿规划、评审、变化和记录 | 不复制标准流程图 |
| ISO 31000:2018 | 6.2 沟通与协商 | 第 7、10.6、10.11 章 | Risk Owner、受影响方和授权人参与 | 沟通机制由 C07 管理 |
| ISO 31000:2018 | 6.3 Scope、Context 和 Criteria | 第 10.6、13.5、20.5 章 | 先定义风险范围、情境和内部量表 | 分值不是 ISO 统一规定 |
| ISO 31000:2018 | 6.4.1–6.4.4 风险评估、识别、分析和评价 | 第 10.6、13.5、15 章 | 记录原因、事件、影响、L、I、Exposure 和等级 | 需保留评分依据 |
| ISO 31000:2018 | 6.5 风险处置 | 第 10.6、13.5、15.3 章 | 记录处置、行动、Owner、期限和 Residual Risk | High/Critical 接受需 RAR |
| ISO 31000:2018 | 6.6 监测与评审 | 第 9.5、10.6、16.2 章 | 定义触发、指标、复核和重新评估 | 运行监测由 C09/E05 管理 |
| ISO 31000:2018 | 6.7 记录与报告 | 第 13.5、16、20.5 章 | 保留 Risk 历史、决定、处置和报告输入 | 汇总报告由 C12 管理 |
| ISO 9001:2015/Amd 1:2024 | 4.1、4.2 情境、相关方和气候相关性 | 第 3、10.5、10.6、15.2 章 | C01 输入传入 Constraint、Risk 和 Dependency | 不构成完整 QMS 情境分析 |
| ISO 9001:2015 | 4.4 质量管理体系及其过程 | 第 2、7、9、10、14 章 | Initiative 明确输入、输出、责任、准则、Risk 和监测 | Initiative 不等同于 QMS 过程 |
| ISO 9001:2015 | 5.3 角色、责任和权限 | 第 7、10.11、10.12 章 | 明确 Owner、Reviewer、Approver 和 Agent 边界 | 组织岗位体系由 C07 管理 |
| ISO 9001:2015 | 6.1 风险和机会应对 | 第 10.5、10.6、15 章 | 风险进入计划、处置和有效性检查 | 使用 ISO 31000 细化过程 |
| ISO 9001:2015 | 6.2 目标及实现计划 | 第 10.2、10.7、13.6 章 | Goal 绑定指标、目标值、责任、时间和评价 | 只管理 Initiative 成功计划 |
| ISO 9001:2015 | 6.3 变更策划 | 第 10.10、16.3、18 章 | 变化检查目的、后果、资源、责任和完整性 | 审批和 Baseline 由 C11 管理 |
| ISO 9001:2015 | 8.1 运行策划和控制 | 第 9、10.3、10.4、15 章 | 控制 Scope、准入条件、操作边界和变化 | 具体 Run 与命令由 C09 管理 |
| ISO 9001:2015 | 8.4 外部提供的过程、产品和服务 | 第 10.8、13.7、15.3 章 | 外部 Dependency 具有条件、Owner、证据和替代方案 | 不替代供应商治理 |
| ISO 9001:2015 | 9.1 监视、测量、分析和评价 | 第 10.7、13.6、14、15 章 | 定义数据、公式、周期、目标、护栏和决策规则 | 数据质量由 E03 管理 |
