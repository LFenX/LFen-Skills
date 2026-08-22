# C05 验收、验证与确认规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C05 |
| 英文名称 | Acceptance, Verification and Validation Specification |
| 正式文件名 | `C05_Acceptance_Verification_and_Validation_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3、C02 V6.3、C03 V6.3、C04 V6.3 |
| 生产前调研 | RVR-C05-0001 |
| 下游规范 | C06、C07、C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式策略、Criteria、Evidence、评审、接受、失效、豁免、风险接受和基线记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定如何把 Need、Intent、Goal、Requirement 和 Quality Attribute 转化为可观察、可重复或可客观判断的 Acceptance Criteria，并分别管理 Verification、Validation、Evidence、Coverage 和 Acceptance Decision。

本规范用于实现以下控制目标：

1. 明确区分“产物是否符合已规定 Requirement”与“产品是否满足 intended use 和真实用户需要”；
2. 使每项当前 Approved Requirement 具有受控 Verification Method、Acceptance Criterion、Test/Check 和 Evidence 链；
3. 使 Validation 在明确用户、任务、资源和环境的 Context of Use 中评价 Need、Intent 和 Goal；
4. 使功能、业务规则、权限、接口、质量、安全、审计和 Agent 行为约束均有风险匹配的验证方法；
5. 使实际结果、Evidence 可信度、Evidence State、覆盖结论和 Acceptance Outcome 分别记录；
6. 防止自动化测试通过、Agent 自检或单一 UI 检查被误作最终接受；
7. 使失败、阻塞、失效、Waiver、Risk Acceptance 和带条件接受能够被追踪且不掩盖未满足 Requirement。

## 3. 适用范围

本规范适用于：

- 从 C04 Requirement Record 和 Requirement Set 建立 Acceptance Criteria；
- 建立 Verification Strategy、Validation Strategy 和方法选择；
- 功能、业务规则、数据、权限、接口、UI、质量、安全、审计和 Agent 行为 Requirement 的验证；
- 正常、异常、边界、权限、幂等、并发、重试、恢复和适用风险场景；
- Test Case、脚本、人工检查、分析模型、演示、评审和外部工具结果的受控引用；
- Verification Evidence 和 Validation Evidence 的捕获、复核、接受、拒绝和失效；
- Web 核心流程的 WCAG 2.2 Level AA 目标验证；
- Requirement、Criterion、Method、Test/Check、Evidence、Result 和 Gap 的覆盖管理；
- 发布、阶段、交付或范围接受的授权决定；
- 人类主导、Agent 辅助和多 Agent 参与的验收、验证与确认活动。

本规范适用于交互式产品、服务、API、数据产品、内部工具、Agent 能力和包含软硬件的 ICT 产品。适用专业扩展是否激活由第 18 章规定。

## 4. 不适用范围

以下内容不由本规范定义：

- Need、Evidence、Problem、Product Definition、Intent 和 Goal 的发现规则，由 C01 管理；
- Initiative、Scope、Assumption、Risk 和 Success Metric 的建立规则，由 C02 管理；
- PRD、Feature、User Scenario、Non-goal、Dependency 和 Quality Attribute Summary 的组织规则，由 C03 管理；
- Requirement Statement、Requirement Set、类型、Revision 和演进分类，由 C04 管理；
- UX Design、Technical Design、接口、数据和权限设计，由 C06 管理；
- 人机职责、工具授权、批准权限和独立性角色的完整模型，由 C07 管理；
- Agent Context 的组装、新鲜度和隔离，由 C08 管理；
- Agent Run、命令、Tool Call、代码变更和 C09 Validation Report，由 C09 管理；
- Decision、Traceability Matrix 和 Provenance 的统一机制，由 C10 管理；
- Configuration Item、Snapshot、Baseline、Change Request 和 Release Configuration，由 C11 管理；
- Gate Decision、Exception or Waiver、Risk Acceptance 和产品健康评价，由 C12 管理；
- 测试框架、测试代码结构、CI/CD 产品选型、物理数据 Schema、法律意见或外部认证。

C05 可以引用上述对象，但禁止建立同名平行资产、复制正文形成第二事实源或以 Acceptance Decision 替代 C12 Gate Decision。

## 5. 规范性用语

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性实践，不作为符合性判定依据。

### 5.2 结果关键词

`Pass`、`Fail` 和 `Blocked` 是 Verification Result，不是资产 State。`Supports`、`Does Not Support` 和 `Inconclusive` 是 Validation Conclusion，不是资产 State。`Accept`、`Accept with Conditions`、`Reject` 和 `Defer` 是 Acceptance Outcome，不是资产 State。

Evidence 的 `Accepted` State 只表示该 Evidence 的来源、完整性、相关性和复核质量已被接受，不表示 Requirement 已通过，也不表示产品已被接受。

### 5.3 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 已批准 Exception、Waiver 或 Risk Acceptance 的明确范围；
3. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
4. 本规范已批准或已基线版本；
5. 当前 Product、Initiative、Scope、PRD 和 Requirement 的有效 Baseline；
6. C06、C07、C10、C11、C12 等专业资产的当前有效 Baseline；
7. R2 无障碍参考、R3 表达实践、模板和示例。

冲突无法判定时必须停止 Evidence 接受、Acceptance Outcome 和下游发布授权，并提交人类决策。

### 5.4 可判定表达

Acceptance Criterion、Strategy、Evidence 和 Coverage 的强制内容必须能够通过 Asset ID、Revision、字段、数值、单位、时间、环境、输入、预期、实际、原始材料、受控枚举、Trace Link 或批准记录直接判定。

禁止使用没有判定条件的“基本通过”“大致符合”“体验良好”“性能正常”“没有明显问题”“看起来正确”“测试充分”“风险可接受”和“必要时”。概率、抽样和统计结论必须记录方法、样本、置信范围或适用限制。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| Acceptance Criterion | 针对 Requirement 定义可观察通过条件的受控成员对象 | 不是 Test Case、Requirement 或 Verification Evidence |
| Acceptance Criteria Set | 在同一受控范围内组织 Criterion 的正式产物 | 使用 ACS 身份和 DOC 状态模型 |
| Verification | 通过客观 Evidence 确认实现、产物或活动结果满足已规定 Requirement | 回答是否按规格构建，不回答真实需要是否满足 |
| Validation | 通过客观 Evidence 确认产品在预期 Context of Use 中满足 Need、Intent、Goal 和 intended use | 不得以 Requirement Pass 自动推导 |
| Acceptance | 授权主体基于适用 Verification、Validation、Risk 和条件作出的范围接受行为 | 不是测试执行或 Evidence State |
| Verification Strategy | 规定验证范围、方法、环境、独立性、覆盖、进入/退出和 Evidence 要求的正式策略 | 不是 Test Plan 的同义词 |
| Validation Strategy | 规定 Need/Intent/Goal、用户、Context、方法、参与者、成功和护栏条件的正式策略 | 不是 Verification Strategy 的章节 |
| Verification Method | 获得 Requirement 符合性 Evidence 的受控方法类别 | C05 内部类型见第 8.2 章 |
| Test Case or Check Reference | 指向外部 Test、Check、脚本、模型或检查资产的受控索引产物 | 不复制外部资产形成第二事实源 |
| Verification Evidence Record | 记录一次 Verification 的对象、版本、执行、环境、输入、预期、实际、结果和原始材料的 Evidence | 不与 C09 Validation Report 混同 |
| Validation Evidence Record | 记录 Need、Intent、Goal、参与者、Context、观察、指标、局限和确认结论的 Evidence | 不等同用户反馈原文或会议纪要 |
| Acceptance Decision | 对特定对象、Revision、范围和期限作出的受控接受决定 | 使用 ACD 身份和 DEC 状态模型 |
| C05 Coverage Matrix | 连接 Requirement、Criterion、Method、Test/Check、Evidence、Result 和 Gap 的正式矩阵 | 不替代 C10 Requirement Coverage Report 或 Bidirectional Traceability Matrix |
| Verification Result | Pass、Fail 或 Blocked 的执行判定 | 与 Evidence State 分开记录 |
| Validation Conclusion | Supports、Does Not Support 或 Inconclusive | 与 Evidence State、Acceptance Outcome 分开记录 |
| Acceptance Outcome | Accept、Accept with Conditions、Reject 或 Defer | 与 ACD State、Gate Decision 分开记录 |
| Expected Result | 从当前 Requirement 和 Criterion 推导的预期可观察结果 | 禁止从当前实现反推 |
| Actual Result | 在指定输入、环境、实现和时间下实际观察到的结果 | 必须保留原始材料 |
| Test Oracle | 决定 Expected Result 及 Pass/Fail 的权威依据 | 必须可定位到 Requirement、Criterion、标准、模型或批准 Decision |
| Verification Independence | 验证、确认或复核主体与被评价内容的作者、实现者或执行者之间的职责分离约束 | 专业化自 C07 Independence；具体授权由 C07 管理 |
| Repeatability | 同一方法、操作者、环境和输入下获得一致结果的能力 | 不等同跨环境 Reproducibility |
| Reproducibility | 在受控变化的操作者、工具或环境下获得可比较结果的能力 | 必须声明允许变化范围 |
| Core Flow | 当前 PRD Acceptance Boundary 中对主要用户结果或关键业务结果不可缺失的完整过程 | 必须覆盖完整页面和完整过程 |

`Context of Use` 的唯一语义直接适用 C01；`Verification Independence` 是 C07 `Independence` 在验证、确认和复核活动中的专业化，授权与职责分离仍由 C07 管理。

未在本章定义的公共术语以 VC-PPG-COM-001 为准。

## 7. 角色与职责

| 角色 | 强制职责 | 禁止事项 |
|---|---|---|
| Acceptance Criteria Owner | 维护 ACS 边界、Criterion、Requirement Trace 和版本 | 不得改变 Requirement 含义 |
| Verification Lead | 建立 VFS、方法、环境、覆盖和独立性要求 | 不得用可用工具反向决定验证目标 |
| Validation Lead | 建立 VLS、Context、参与者、成功和护栏条件 | 不得以实验方便替代目标用户 |
| Test or Check Custodian | 维护 TCR 与外部 Test/Check 的版本、入口和有效性 | 不得复制过期脚本引用 |
| Evidence Producer | 按授权方法执行活动并捕获原始材料 | 不得修改 Actual Result 或删除失败日志 |
| Evidence Reviewer | 复核 Evidence 来源、完整性、相关性、方法和限制 | 不得把 Evidence Accepted 等同 Requirement Pass |
| Requirement Owner | 确认 Criterion 未改变 Requirement 义务并处理 Requirement Gap | 不得因测试困难降低 Requirement |
| Quality Representative | 核验产品质量 Measure、环境、阈值、样本和不确定性 | 不得以一次运行证明持续质量 |
| UX and Accessibility Reviewer | 核验用户流程、Context、可用性和 WCAG 适用覆盖 | 不得以自动扫描替代人工和辅助技术验证 |
| Stakeholder or Participant Representative | 确认目标用户、参与者、情境和 Validation 观察解释 | 不得隐瞒样本偏差或利益冲突 |
| Risk Owner | 评价 Fail、Blocked、Inconclusive 和剩余 Risk | 不得把 Risk Acceptance 写成 Requirement Pass |
| Acceptance Authority | 基于当前 Evidence、Coverage、Risk 和条件作 Acceptance Decision | 不得批准自己生成且未经独立复核的高风险 Evidence |
| Independent Reviewer | 按 Criticality 复核 Strategy、Criterion、Evidence、Coverage 和 Decision | 不得同时是唯一作者、唯一执行者和唯一接受者 |
| Coding Agent | 生成 Draft、候选 Criterion/Test、执行获批检查、整理 Evidence 和运行覆盖检查 | 不得接受自身 Evidence、关闭高风险 Failure、作 Risk Acceptance 或 Acceptance Decision |

同一人可以承担多个非冲突角色，但高 Criticality 对象的 Acceptance Authority 禁止与唯一 Author、唯一 Evidence Producer 和唯一 Reviewer 为同一人。具体职责分离、工具授权和替代路径由 C07 管理。

## 8. 管理对象与关系

### 8.1 正式产物

本规范管理八类正式产物：

1. Acceptance Criteria Set（ACS）；
2. Verification Strategy（VFS）；
3. Validation Strategy（VLS）；
4. Test Case or Check Reference（TCR）；
5. Verification Evidence Record（VER）；
6. Validation Evidence Record（VAE）；
7. Acceptance Decision（ACD）；
8. Coverage Matrix（VCM）。

八类产物可以在同一工具或页面展示，但必须分别保留 Asset ID、Artifact Type、Owner、State、Current Revision、Trace Links、Access Classification、Retention Rule 和 History Reference。

### 8.2 Verification Method 分类

| Method | 用途边界 | 最低 Evidence |
|---|---|---|
| Test | 在受控输入和环境下执行对象并比较 Expected 与 Actual | 执行版本、环境、输入、Expected、Actual、日志和 Result |
| Analysis | 使用计算、模型、静态分析、数据分析或推理评价符合性 | 分析方法、输入、假设、工具/模型版本、结果和复核 |
| Inspection | 对代码、配置、文档、界面或物理对象作结构化检查 | 检查对象与版本、准则、观察、Finding 和 Reviewer |
| Demonstration | 在代表性场景中展示可观察能力或行为 | 场景、环境、步骤、观察、限制和见证者 |
| Review | 由具备资格的人员按准则评价产物 | Reviewer、独立性、准则、Finding、结论和时间 |
| Assessment | 综合多种 Evidence 对质量、风险或适用性作系统评价 | 范围、准则、Evidence 集、权重/方法、限制和结论 |

每项 Requirement 可以使用一种或多种 Method。方法名称不自动证明充分性；VFS 必须记录选择理由、Criticality、覆盖范围和剩余缺口。

### 8.3 Scenario Class

| Class | 目的 | 适用判定 |
|---|---|---|
| Positive | 证明有效输入和允许路径产生预期结果 | 所有行为 Requirement |
| Negative or Error | 证明无效输入、失败依赖或错误状态被正确处理 | 所有存在拒绝或失败路径的对象 |
| Boundary | 证明最小、最大、空、零、阈值两侧和时间边界 | 存在范围、阈值、容量或期限时 |
| Permission and Access | 证明允许、拒绝、隔离、撤销和最小权限 | 涉及角色、身份、资源或敏感数据时 |
| Idempotency | 证明重复请求或重试不会产生未授权重复效果 | API、命令、支付、事件或可重试操作 |
| Concurrency and Ordering | 证明并发、乱序、竞争和一致性行为 | 共享状态、异步事件或多主体操作 |
| Retry and Recovery | 证明超时、重试、降级、恢复和回滚行为 | 外部依赖、长事务或关键服务 |
| Quality and Load | 证明性能、可靠性、容量、安全或其他质量阈值 | 适用 Quality Requirement |
| Accessibility and Interaction | 证明完整流程的可感知、可操作、可理解和兼容 | Web 核心流程及适用交互产品 |
| Agent Behavior | 证明上下文、工具、权限、停止、升级和输出约束 | Agent Behavior Constraint |

Scenario Class 是 Criterion 分类字段，不是正式产物类型或 State。

### 8.4 最低关系链

```text
Acceptance Criterion
  └─ derives-from → Requirement

Acceptance Criteria Set
  └─ contains → Acceptance Criterion

Requirement
  └─ verified-by → Verification Evidence Record

Need / Intent / Goal
  └─ validated-by → Validation Evidence Record

Test Case or Check Reference
  └─ depends-on → Requirement / Acceptance Criterion / Tool or Repository Asset

Acceptance Decision
  └─ depends-on → Verification Evidence / Validation Evidence / Coverage Matrix / Risk Decision

Release
  └─ depends-on → Acceptance Decision
```

实际 Trace Link 必须使用 VC-PPG-COM-001 规定的方向和语义。禁止使用 `related-to` 或中文“相关”作为正式关系。

### 8.5 事实源边界

| 信息 | 唯一事实源 | C05 允许动作 |
|---|---|---|
| Need、Intent、Goal、Evidence | C01 | 作为 Validation 来源和目标 |
| Scope、Risk、Metric | C02 | 作为边界、Criticality 和成功/护栏输入 |
| PRD、Feature、Scenario、QAS、Acceptance Boundary | C03 | 作为范围和场景来源 |
| Requirement、Revision、Applicability、Priority、Criticality | C04 | 只引用，不复制或改写 |
| Acceptance Criterion、V&V Strategy、Evidence、Coverage、Acceptance | C05 | 维护唯一权威内容 |
| Design、接口、数据、权限和实现约束 | C06 | 作为 Test/Check 和环境输入 |
| Agent Run、命令、日志和代码验证报告 | C09 | 引用原始执行事实 |
| Decision、Trace 和 Lineage | C10 | 提交关系和决定候选 |
| Configuration、Snapshot、Baseline、Change、Release | C11 | 固定被测对象与环境版本 |
| Gate、Waiver、Risk Acceptance | C12 | 引用授权决定，不建立平行对象 |

缓存、报告或矩阵与事实源不一致时必须标记 Stale，并禁止进入 Evidence Accepted、Acceptance Outcome 或 Gate。

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
C04 Handoff
  → Eligibility Check
  → Verification and Validation Planning
  → Acceptance Criteria Definition
  → Method and Test/Check Selection
  → Readiness Review
  → Verification Execution and Evidence Collection
  → Validation Execution and Evidence Collection
  → Evidence Review
  → Coverage Reconciliation
  → Acceptance Decision
  → Gate / Release Handoff
  → Observation, Change or Evidence Invalidation
  → Re-verification / Re-validation / New Decision
```

### 9.2 Eligibility Check

C05 Owner 必须核验上游 PRD、Requirement Set、REQ ID、Current Revision、Statement、Applicability、Criticality、Verification Method Candidate、Acceptance Boundary、Risk 和 Baseline。上游未达到 Approved 或 Baselined 时可以创建 Draft 产物，但禁止将 ACS/VFS/VLS/VCM 置为 Approved/Baselined，禁止将 Evidence 作为当前接受依据。

### 9.3 策略与 Criteria

必须先建立 VFS/VLS 的范围、方法、环境、独立性和 Evidence 规则，再批准 ACS 和执行引用。禁止先编写自动化脚本，再从脚本反推 Acceptance Criterion。

### 9.4 执行与 Evidence

执行前必须固定 Requirement、Criterion、Test/Check、实现、配置、环境、数据和工具 Revision。执行后必须先捕获原始材料，再形成 VER/VAE。缺少原始材料时只能记录 Blocked 或限制，不得补写推测结果。

### 9.5 复核、覆盖与接受

Evidence Reviewer 必须先判断 Evidence 是否可信可用，再由 VCM 计算当前覆盖。Acceptance Authority 必须基于 Accepted Evidence、实际 Result、Validation Conclusion、Coverage、Failure、Risk 和条件形成 ACD。

### 9.6 变化与失效

Requirement、Criterion、Test Oracle、Design、Code、Configuration、Environment、Data、Tool、Context of Use 或原始材料变化时必须执行 Evidence 新鲜度检查。失效 Evidence 必须进入 Invalidated，禁止继续计入当前覆盖。

## 10. 强制规则

### 10.1 身份、Revision 与范围

1. ACS、VFS、VLS、TCR、VER、VAE、ACD 和 VCM 必须使用目录规定的永久类型代码和唯一 ID。
2. Criterion 是 ACS 的受控成员，必须使用稳定 Criterion ID、成员 Revision、来源和历史；不得创建蓝图外平行正式产物。
3. Criterion ID 应采用 `<ACS ID>-C<顺序号>`，该格式表示成员身份，不是新产物类型代码。
4. ACS 边界必须指向 PRD、Requirement Set、Feature、Release、环境和适用版本。
5. TCR 必须指向外部 Test/Check 的稳定 ID 与版本；文件路径、测试名称或 CI URL 不能单独充当永久身份。
6. VER/VAE 每次受控执行或观察必须创建独立 Evidence ID；重跑禁止覆盖原 Evidence。
7. ACD 必须固定被接受对象、Revision、Evidence 集、范围、环境、Release 和有效期。
8. VCM 必须固定成员 Revision；引用“latest”禁止作为 Baseline 或 Acceptance 依据。

### 10.2 Verification、Validation 与 Acceptance 分离

1. Verification 必须追踪 Requirement，Validation 必须追踪 Need、Intent、Goal 和 Context of Use。
2. Requirement 全部 Pass 不自动推出 Need、Intent 或 Goal 得到支持。
3. Validation Conclusion 为 Supports 不自动推出全部 Requirement Pass。
4. Test、Inspection、Analysis 或 Review 完成不等于 Acceptance。
5. Evidence Accepted 不等于 Verification Result Pass、Validation Conclusion Supports 或 Acceptance Outcome Accept。
6. Acceptance Decision 必须由授权人作出，并分别列明 Verification、Validation、Coverage、Risk 和未完成项。
7. C05 Acceptance Decision 禁止替代 C12 Gate Decision 或发布批准。

### 10.3 Acceptance Criterion 表达

每个 Criterion 必须包含一个可独立判断的 Expected Result，并采用结构化字段或以下表达骨架：

```text
Given <前置状态、角色、数据和环境>
When <触发事件或行为>
Then <可观察结果、量值、阈值、时限或状态>
```

强制要求：

1. Given 必须可建立和核验，不得包含待验证结果；
2. When 必须只有一个主要触发；多个独立触发必须拆分；
3. Then 必须基于用户、外部系统、接口、日志、状态、指标或其他受控输出客观判断；
4. 每个独立 Expected Result 必须具有独立 Criterion ID；
5. 数据、时间、单位、容差、顺序、环境、角色和权限必须在适用时明确；
6. Expected Result 必须来自当前 Requirement/Test Oracle，禁止从现有实现反推；
7. Criterion 不得降低、扩大或重新解释 Requirement；
8. Requirement 存在歧义时必须返回 C04，禁止用 Criterion 私自解决；
9. Gherkin 是可选表达载体；Criterion 的受控字段和 ID 才是治理事实源。

### 10.4 Scenario Coverage

1. 每项行为 Requirement 必须至少覆盖 Positive 场景。
2. 存在拒绝、错误、失效或异常路径时必须覆盖 Negative or Error 场景。
3. 存在数值、长度、容量、时限、日期或枚举边界时必须覆盖阈值本身及阈值两侧。
4. 涉及身份、角色、权限、敏感数据或职责分离时必须同时覆盖允许、拒绝、撤销和跨主体隔离。
5. 可重试操作必须评价 Idempotency；不适用时必须记录原因。
6. 共享状态、异步消息或多主体修改必须评价 Concurrency and Ordering。
7. 外部依赖、超时或关键状态变化必须评价 Retry and Recovery。
8. 关键业务规则禁止只验证 UI 表现；必须验证承载规则的服务、接口、数据或策略层。
9. Scenario Class 不适用时必须记录 Requirement、Risk、Reviewer 和批准依据，禁止留空。

### 10.5 Method 选择与独立性

1. VFS 必须按 Requirement Type、Criticality、Failure Impact、可观察性和环境选择一种或多种 Method。
2. 单一 Method 无法覆盖全部义务时必须组合使用，不得以工具可用性限制目标。
3. Functional、Interface、Permission、Agent Behavior 通常至少需要 Test 或 Demonstration；只用文档 Review 必须有批准依据。
4. 数值、算法、容量或静态属性可以使用 Analysis，但输入、模型、假设和工具必须可复核。
5. Security、Safety、合规、财务权限和高 Criticality Requirement 必须定义独立 Reviewer、负向场景和原始 Evidence。
6. 同一 Agent 生成 Criterion、实现和 Test 时，不得成为唯一 Evidence Reviewer。
7. Independence 要求必须与 C04 Criticality 和 C02 Risk 追踪；禁止由执行者自行降低。
8. 需要专门资格、校准设备、受控实验室或真实用户参与时，Strategy 必须记录资格与环境前置条件。

### 10.6 Verification Strategy

VFS 必须：

1. 定义 Product、PRD、Requirement Set、Release、环境和排除项；
2. 按 Requirement Type 与 Criticality建立方法矩阵；
3. 固定目标 Requirement Revision 和适用 Baseline；
4. 定义环境、数据、工具、权限、隔离、时间和资源；
5. 定义独立性、Reviewer、Witness 和批准责任；
6. 定义 Requirement-to-Method、Requirement-to-Criterion 和 Critical Requirement-to-Accepted-Evidence 的覆盖目标；
7. 定义执行进入条件、退出条件、停止条件和恢复条件；
8. 定义 Fail、Blocked、Flaky、Inconclusive 和环境偏差处理；
9. 定义原始材料、完整性、Retention、敏感信息和复核要求；
10. 定义 Evidence 失效触发条件和重新验证范围。

### 10.7 Validation Strategy

VLS 必须：

1. 固定 Need、Intent、Goal、PRD、目标用户和 Stakeholder；
2. 描述真实或代表性 Context of Use，包括用户、目标、任务、资源和环境；
3. 说明参与者选择、样本、代表性、排除条件和利益冲突；
4. 规定访谈、观察、可用性评价、现场试用、实验、模拟、运营指标或其他确认方法；
5. 规定 beneficialness、freedom from risk、acceptability 的适用范围；
6. 定义 Success Metric、护栏、阈值、观察周期和 Test Oracle；
7. 记录伦理、隐私、知情、数据最小化和敏感材料访问约束；
8. 定义偏差、局限、缺失、早停和 Inconclusive 处理；
9. 指定 Validation Lead、Participant Representative、Reviewer 和 Acceptance Authority；
10. 说明 Validation Evidence 如何进入 ACD、C12 Gate 和后续 Observation。

### 10.8 Test Case or Check Reference

1. 每个 TCR 必须记录外部 ID、来源系统、版本、执行入口、维护责任人、当前有效性和 Trace。
2. 外部 Test/Check 必须能够定位到代码、配置、文档、工具、模型或受控仓库 Revision。
3. TCR 只保存必要元数据和引用，禁止复制外部 Test 正文形成第二事实源。
4. 外部 Test/Check 变更后必须更新 TCR Revision 并执行影响分析。
5. 被删除、禁用、跳过、Flaky、失效或无法执行的 Test/Check 禁止标记为当前有效。
6. 自动化状态必须使用第 11.4 章的受控值，并与实际执行能力一致。

### 10.9 Execution 与 Verification Evidence

1. 执行前必须检查 VFS State、Criterion Revision、TCR Validity、Environment Readiness、权限和数据。
2. VER 必须记录 Requirement、Criterion、执行方式、实现/配置版本、环境、输入、Expected、Actual、Result、执行者、时间和原始材料。
3. Result 只允许 Pass、Fail 或 Blocked。
4. Expected 与 Actual 不一致时必须为 Fail；禁止以“已知问题”“非关键”或“后续修复”改写为 Pass。
5. 执行未开始、环境无效、输入缺失、权限不足或 Oracle 不可用时必须为 Blocked。
6. 随机、概率或统计测试必须记录种子、样本、重复次数、分布、置信范围和失败规则。
7. 日志、截图、报告、转储、指标、Trace、录屏或签名材料必须能够定位到原始存储和完整性引用。
8. 任何清洗、脱敏、汇总或转换必须保留处理规则和原始材料指针。
9. Evidence Producer 禁止修改 Actual Result；记录错误通过新 Revision 或更正记录处理。
10. Evidence Accepted 只表示证据可信可用；VCM 必须另读 Result 判断 Requirement 是否验证通过。

### 10.10 Validation Execution 与 Evidence

1. Validation 必须按 VLS 在已定义 Context of Use 或经批准的代表性情境中执行。
2. VAE 必须记录 Need/Intent/Goal、参与者、Context、方法、观察、指标、偏差、局限、原始材料和 Validation Conclusion。
3. 参与者与目标用户不一致时必须记录差异、影响和授权理由。
4. 样本不足、情境失真、指标不可用或偏差无法控制时必须为 Inconclusive。
5. 用户偏好、单次反馈或内部 Stakeholder 意见禁止单独作为 Supports 结论。
6. Does Not Support 或 Inconclusive 禁止改写为 Requirement Fail；必须分别触发 Need、Product、Requirement、Design 或 Strategy 分析。
7. 隐私、伦理和敏感材料处理必须遵守适用 E02 和访问规则。
8. VAE Accepted 只表示 Evidence 可信可用，不表示产品已被接受。

### 10.11 Evidence 可信度与失效

Evidence Reviewer 必须检查：

1. Identity：对象、Requirement、Criterion、实现、配置、环境和时间唯一；
2. Provenance：执行者、工具、数据、Agent Run 和原始材料可追溯；
3. Integrity：原始材料未被无痕修改，校验或受控存储可用；
4. Relevance：方法、输入和环境实际覆盖目标义务或使用情境；
5. Sufficiency：样本、场景、重复、边界和持续时间足以支持结论；
6. Objectivity：Expected、Actual、Oracle 和判断规则在执行前可识别；
7. Repeatability or Reproducibility：按 Strategy 能复现或解释不可复现原因；
8. Independence：满足 Criticality 和 C07 规定的职责分离；
9. Limitations：未知项、偏差、抽样和工具局限明确；
10. Freshness：所有来源 Revision 与当前事实源一致。

出现以下任一情况时 Evidence 必须进入 Invalidated 或重新评审：

- Requirement、Criterion、Oracle 或 Acceptance Boundary 变化；
- Design、Code、Configuration、Data、Dependency 或 Release 变化影响结论；
- 环境、工具、浏览器、辅助技术、模型或校准状态变化；
- 原始材料丢失、完整性失败或 Provenance 无法验证；
- Test/Check 被证明错误、Flaky 或覆盖不足；
- 新 Defect、Incident、Observation 或 Risk 反驳原结论；
- Context of Use、目标用户或 Success Metric 发生实质变化。

### 10.12 非功能与产品质量验证

1. C03 QAS 中适用的 ISO/IEC 25010 九类产品质量必须逐类关联 C04 REQ、Criterion、Method 和 Evidence。
2. 质量 Criterion 必须记录 Measure、计算公式、单位、数据源、阈值、比较符、时间窗口和适用对象。
3. 性能与容量验证必须记录硬件、软件、网络、数据量、并发、负载模型、预热、持续时间、采样和重复次数。
4. 可靠性验证必须记录观察窗口、故障注入或失效条件、恢复标准和中断处理。
5. Security 和 Safety 验证必须记录威胁/危险来源、负向场景、独立性和剩余 Risk。
6. Maintainability、Flexibility 或其他静态/演进质量可以组合 Analysis、Inspection、Test 和历史数据，但必须固定版本和评价规则。
7. 测量误差、工具误差、环境波动和统计不确定性必须被记录并纳入阈值判断。
8. 一次非受控运行、平均值掩盖尾部结果或缺少原始样本禁止作为 Pass 依据。

### 10.13 UX、使用质量与无障碍

1. Validation 必须按 ISO/IEC 25019 的 beneficialness、freedom from risk、acceptability 逐项确定适用性。
2. Usability 评价必须明确用户、任务、Context、有效性、效率和满意相关 Measure，禁止只记录主观印象。
3. Web App 核心流程默认以 WCAG 2.2 Level AA 为目标；适用法律、合同或组织 Baseline 要求更高时从其规定。
4. WCAG AA 目标必须覆盖适用 A 和 AA Success Criteria、完整页面、完整流程、Accessibility-supported 技术和 Non-interference。
5. 无障碍验证必须组合自动化检查、键盘操作、人工评审和适用辅助技术；自动扫描禁止单独证明符合。
6. 必须记录浏览器、操作系统、辅助技术、视口、缩放、语言、输入方式、页面和流程版本。
7. 颜色、焦点、名称/角色/值、状态消息、错误处理、认证、拖动、目标尺寸和完整流程必须按适用 Success Criteria 评价。
8. `Not Applicable` 必须逐项记录 Success Criterion、范围、理由、Reviewer 和 Approver。
9. 外部 WCAG Conformance Claim 只有满足 W3C 第 5 章范围和声明要求时才能形成；C05 默认只记录内部目标与 Evidence。
10. 非 Web 产品必须选择适用无障碍或人因标准，并记录 Applicability Decision，禁止机械声明 WCAG 全量适用。

### 10.14 Agent 生成 Test 与人类复核

1. Agent 生成的 Criterion、Test、Check、数据或 Oracle 必须标记 Generated Candidate 并追踪 Agent Run、输入 Context、模型/执行引擎标识和生成时间。
2. Agent 禁止把 Requirement 未规定的实现细节写入 Expected Result。
3. Agent 生成内容进入执行前必须由 Requirement Owner 或授权 Reviewer 核验语义和范围。
4. 同一 Agent 生成实现与 Test 时，必须由独立主体复核高 Criticality Result。
5. Agent 可以执行已批准的确定性检查，但原始 Tool Call、命令、退出状态和日志必须由 C09 保留。
6. Agent 自报成功、自然语言总结或内部推理禁止作为原始 Evidence。
7. Agent 禁止接受自身 Evidence、豁免 Failure、接受剩余 Risk 或作 ACD。
8. 自动修复后必须创建新 Evidence；原 Fail Evidence 禁止覆盖或删除。

### 10.15 Failure、Waiver、Risk Acceptance 与 Acceptance

1. Fail 必须记录偏差、影响对象、Defect/Change 候选、Owner 和处置期限。
2. Blocked 必须记录阻塞原因、解除条件、责任人和重新执行计划。
3. Validation Does Not Support 或 Inconclusive 必须记录对 Need、Intent、Goal、PRD 和 Product 的影响。
4. Waiver 只豁免明确门禁或规则，不表示 Requirement 已满足，也不得把 Fail 改为 Pass。
5. Risk Acceptance 只表示授权人接受剩余 Risk，不改变 Evidence、Result 或 Validation Conclusion。
6. Accept with Conditions 必须记录条件、Owner、期限、监控、失效时间和违反条件后的动作。
7. 存在高 Criticality Fail、无授权 Blocked、Invalidated Evidence 或未关闭安全/合规问题时禁止 Accept。
8. ACD 必须引用 C12 Exception or Waiver Record 和 Risk Acceptance Record；禁止在 C05 建立同名平行产物。
9. Requirement 本身需要变化时必须返回 C04/C11，禁止通过修改 Criterion 或 Acceptance Outcome 规避。

### 10.16 Coverage 与 Acceptance Gate

1. 所有当前 In Scope、Approved/Baselined Requirement 的 Method Coverage 必须为 100%，除非存在已批准 Not Applicable。
2. 所有当前 In Scope、Approved/Baselined Requirement 的 Criterion Coverage 必须为 100%，除非存在已批准 Not Applicable。
3. 所有高 Criticality Requirement 在 Accept 前必须具有当前、Accepted 且 Result 为 Pass 的 VER，覆盖率为 100%。
4. 每个 In Scope Need、Intent 和 Goal 必须具有 VLS 覆盖；进入最终接受时必须具有当前 VAE 或经批准的分阶段 Validation 计划。
5. Failed、Blocked、Rejected、Invalidated、过期或 Revision 不匹配的 Evidence 禁止计入 Satisfied。
6. VCM 必须分别报告 Requirement Coverage、Evidence Coverage、Pass Coverage、Validation Coverage 和 Gap，不得用一个总百分比掩盖关键缺口。
7. 只验证 UI 而未验证关键后端业务规则、权限、数据约束或审计义务时必须判定 Coverage Gap。
8. Coverage 阈值满足不自动产生 Acceptance Outcome；ACD 仍需评价 Risk、Validation、条件和授权。

### 10.17 Change、Re-execution 与版本控制

1. ACS/VFS/VLS/TCR/VCM Approved 后变化必须重新评审；Baselined 后变化必须进入 C11 Change Request。
2. Requirement Revision 必须触发 Criterion、Method、TCR、Evidence、VCM 和 ACD 影响分析。
3. 实现或配置变化必须按影响范围重新 Verification；“无功能变化”必须有 C04/C11 分类和回归依据。
4. Context of Use、目标用户、Goal 或 Success Metric 变化必须重新 Validation。
5. Evidence 重跑必须创建新 VER/VAE，并通过 Trace 保留新旧结果。
6. 新 ACD 生效时必须保留旧 ACD 的范围、Evidence、条件和有效期，不得无痕覆盖。

## 11. 受控状态

### 11.1 DOC 状态：ACS、VFS、VLS、TCR、VCM

| State | 进入条件 | 允许后续 |
|---|---|---|
| Draft | 已建立 ID、Owner、Source 和边界 | In Review、Rejected |
| In Review | 必填信息完整且 Reviewer 已指定 | Changes Required、Approved、Rejected |
| Changes Required | 存在需整改 Finding | Draft、In Review、Rejected |
| Approved | 授权人批准当前 Revision | Baselined、In Review、Superseded、Retired |
| Baselined | 已纳入 C11 Baseline 并固定 Revision/Snapshot | 通过 Change Request 产生新修订、Superseded、Retired |
| Rejected | 当前候选不获接受 | 保留历史 |
| Superseded | 已由新资产或新修订替代 | 仅历史查询 |
| Retired | 无替代且不再适用 | 仅历史查询 |

### 11.2 EVID 状态：VER 与 VAE

| State | 含义 | 强制规则 |
|---|---|---|
| Planned | 已定义 Evidence 目标但尚未捕获 | 不计覆盖 |
| Collected | 原始材料和 Evidence Record 已捕获 | 等待复核 |
| Under Review | Reviewer 正在复核可信度与适用性 | 不计最终接受依据 |
| Accepted | Evidence 可信可用且局限已记录 | 必须另读 Result/Conclusion |
| Rejected | Evidence 不可信、不充分或不适用 | 禁止计入覆盖 |
| Invalidated | 先前 Evidence 因版本、环境、方法、Context 或新事实失效 | 禁止作为当前依据 |

### 11.3 DEC 状态：ACD

| State | 使用条件 |
|---|---|
| Proposed | 已形成 Acceptance Outcome 候选 |
| Under Review | 授权主体正在评审 |
| Approved | ACD 内容与 Outcome 已批准 |
| Conditionally Approved | ACD 在明确条件、期限和责任下批准 |
| Rejected | ACD 候选被拒绝 |
| Waived | 仅在明确范围内豁免决定流程或门禁，不表示 Requirement 满足 |
| Superseded | 后续 ACD 替代当前决定 |
| Expired | 有效期或条件已失效 |

### 11.4 非 State 受控值

| 字段 | 允许值 |
|---|---|
| Verification Result | Pass、Fail、Blocked |
| Validation Conclusion | Supports、Does Not Support、Inconclusive |
| Acceptance Outcome | Accept、Accept with Conditions、Reject、Defer |
| Automation Status | Manual、Automation Candidate、Automated、Hybrid、Not Applicable |
| Coverage Status | Not Covered、Criteria Defined、Execution Pending、Evidence Under Review、Satisfied、Not Satisfied、Blocked、Invalidated、Not Applicable |
| Applicability | Applicable、Not Applicable、Not Assessed |
| Test/Check Validity | Current、Stale、Disabled、Missing、Unknown |

`Generated Candidate` 是生成来源标记，`Flaky` 是 Test/Check 健康标记，均不是 State。每次 State 变化必须记录原状态、新状态、对象 Revision、执行者、时间、依据和批准。人类批准是 Approved、Conditionally Approved、Waived、Accepted 和 Baselined 的必要条件。

## 12. 必需产物

| 类型代码 | 正式产物 | 状态模型 | 最低用途 |
|---|---|---|---|
| ACS | Acceptance Criteria Set | DOC | 管理 Requirement 的可观察通过条件和 Scenario Coverage |
| VFS | Verification Strategy | DOC | 管理验证范围、Method、环境、独立性、覆盖、进入/退出和 Evidence |
| VLS | Validation Strategy | DOC | 管理 Need/Intent/Goal、目标用户、Context、方法、成功和护栏 |
| TCR | Test Case or Check Reference | DOC | 引用外部 Test/Check ID、版本、入口、责任和有效性 |
| VER | Verification Evidence Record | EVID | 记录 Requirement/Criterion 的执行、Expected、Actual、Result 和原始材料 |
| VAE | Validation Evidence Record | EVID | 记录 Need/Intent/Goal 的参与者、Context、观察、指标、局限和结论 |
| ACD | Acceptance Decision | DEC | 对明确范围、Revision、Evidence、Risk 和条件作接受决定 |
| VCM | Coverage Matrix | DOC | 连接 Requirement、Criterion、Method、Test/Check、Evidence、Result 和 Gap |

八类产物禁止合并身份。P2 下禁止以一个“测试报告”或“验收表”替代八类产物。

## 13. 产物必填信息

### 13.1 通用必填信息

八类产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C05 类型专属要求。

### 13.2 Acceptance Criteria Set

| 字段 | 强制要求 |
|---|---|
| Boundary | PRD、Requirement Set、Feature、Release、环境和适用版本 |
| Requirement Reference | REQ ID、Current Revision、Statement Snapshot、Type、Priority、Criticality |
| Criterion ID | ACS 内稳定成员 ID |
| Preconditions | 可建立的前置状态 |
| Trigger or Action | 单一主要触发 |
| Expected Result | 单一可独立判断结果 |
| Observable Output | UI、API、事件、日志、状态、指标或其他受控输出 |
| Data and Environment | 输入数据、时间、配置、依赖和环境 |
| Applicable Role | 用户、系统、外部主体或 Agent |
| Scenario Class | 第 8.3 章受控值 |
| Priority | Criterion 执行排序及来源 |
| Verification Method | 第 8.2 章一种或多种 Method |
| Test Oracle | Requirement、模型、标准或 Decision 引用 |
| Automation Status | 第 11.4 章受控值 |
| Test/Check Reference | TCR ID；Draft 可为 Candidate 并设期限 |
| Member Revision and History | Criterion Revision、变化和影响 |
| Open Findings | Finding、Owner、期限和阻断结论 |

### 13.3 Verification Strategy

| 字段 | 强制要求 |
|---|---|
| Verification Scope | Product、PRD、Requirement Set、Release、环境和排除项 |
| Requirement Classification | Type、Priority、Criticality、Risk 和数量 |
| Method Selection | 每类 Requirement 的 Method、理由和组合 |
| Environment | 硬件、软件、网络、数据、配置、权限和隔离 |
| Tools | 工具、版本、校准或可信来源 |
| Independence | Author、Implementer、Producer、Reviewer 和 Authority 分离要求 |
| Coverage Targets | Method、Criterion、Evidence、Pass 和 Criticality 目标 |
| Entry and Exit Criteria | 进入、退出、停止和恢复条件 |
| Failure Handling | Fail、Blocked、Flaky、Inconclusive、Defect 和重跑规则 |
| Evidence Requirements | 原始材料、完整性、Provenance、Retention、复核和失效 |

### 13.4 Validation Strategy

| 字段 | 强制要求 |
|---|---|
| Need, Intent and Goal Scope | 当前 ID、Revision、Owner 和目标结果 |
| Target Users and Stakeholders | 直接、间接和受影响群体 |
| Context of Use | 用户、目标、任务、资源和环境 |
| Validation Method | 观察、访谈、试用、实验、模拟、运营指标或组合 |
| Participants or Sample | 选择、数量、代表性、排除和利益冲突 |
| Quality-in-use Coverage | beneficialness、freedom from risk、acceptability 的适用性 |
| Success and Guardrail Conditions | Metric、阈值、观察周期和 Oracle |
| Ethics and Privacy | 知情、最小化、访问、保留和退出规则 |
| Limitations and Bias | 样本、情境、测量、偏差和未知项 |
| Acceptance Responsibility | Validation Lead、Reviewer、Stakeholder 和 Authority |

### 13.5 Test Case or Check Reference

| 字段 | 强制要求 |
|---|---|
| External Test or Check ID | 外部系统中的稳定身份 |
| Source System | 仓库、测试管理、工具、模型或文档事实源 |
| Requirement and Criterion | REQ ID/Revision、ACS ID、Criterion ID/Revision |
| External Version | 提交、版本、配置或快照 |
| Execution Entry | 可定位命令、作业、页面、程序或人工程序 |
| Method and Scenario Class | 受控 Method 与场景分类 |
| Maintenance Owner | 对有效性和更新负责的人类角色 |
| Automation Status | 第 11.4 章受控值 |
| Current Validity | Current、Stale、Disabled、Missing 或 Unknown |
| Last Verified | 最近核验时间、环境和 Evidence |

### 13.6 Verification Evidence Record

| 字段 | 强制要求 |
|---|---|
| Requirement and Criterion | REQ ID/Revision、ACS/Criterion ID/Revision |
| Test or Check | TCR ID/Revision 或经批准的直接 Method |
| Execution Method | Method、步骤或命令引用 |
| Subject Version | Code、Build、Configuration、Data、Model 和 Release Revision |
| Environment | 硬件、软件、网络、依赖、权限、时间和隔离 |
| Input | 数据、事件、种子、负载、用户或前置状态 |
| Expected Result | Criterion/Test Oracle 的不可变引用 |
| Actual Result | 实际观察及量值 |
| Verification Result | Pass、Fail 或 Blocked |
| Executor | 人类、Agent、工具、Run ID 和权限上下文 |
| Execution Time | 开始、结束、时区和持续时间 |
| Raw Evidence | 日志、报告、截图、指标、转储、录屏或其他原始材料 |
| Integrity and Provenance | 存储、校验、生成链、脱敏和转换规则 |
| Limitations | 偏差、抽样、环境差异、未知项和适用边界 |
| Evidence Review State | 使用 EVID State；Reviewer、独立性和时间 |

### 13.7 Validation Evidence Record

| 字段 | 强制要求 |
|---|---|
| Need, Intent and Goal | 当前 ID 与 Revision |
| Product and Release | 被确认产品、Build、Configuration、环境和版本 |
| Participants and Stakeholders | 群体、选择、数量、代表性和权限 |
| Context of Use | 用户、任务、资源和环境 |
| Method | VLS、程序、时间和执行主体 |
| Observations | 可观察行为、结果、反馈和事件 |
| Success Metric Results | 指标、算法、基线、目标、实际和护栏 |
| Quality-in-use Results | 三类特性及适用子特性结果 |
| Deviations and Limitations | 样本、偏差、情境差异、缺失和未知项 |
| Raw Materials | 数据、记录、日志、录像、问卷或其他原始材料 |
| Ethics and Privacy Controls | 知情、最小化、访问、脱敏和保留 |
| Validation Conclusion | Supports、Does Not Support 或 Inconclusive |
| Evidence Review State | 使用 EVID State；Reviewer、独立性和时间 |

### 13.8 Acceptance Decision

| 字段 | 强制要求 |
|---|---|
| Acceptance Scope | Product、PRD、Requirement Set、Feature、Release、环境和版本 |
| Verification Evidence | 当前 Accepted VER 及 Result |
| Validation Evidence | 当前 Accepted VAE 及 Conclusion |
| Coverage Matrix | VCM ID、Revision、统计时间和 Gap |
| Failed, Blocked and Invalidated Items | 对象、Criticality、影响和处置 |
| Residual Risk | Risk、控制、Owner、监控和 C12 决定 |
| Acceptance Outcome | Accept、Accept with Conditions、Reject 或 Defer |
| Conditions | 条件、Owner、期限、Evidence、失效和违反动作 |
| Approver | 授权人、独立性和批准依据 |
| Effective and Expiry Time | 生效、失效、Release 和环境边界 |
| Gate and Change References | C12 Gate、C11 Release/Change 和适用 Waiver/Risk Acceptance |

### 13.9 Coverage Matrix

| 字段 | 强制要求 |
|---|---|
| Requirement | REQ ID、Revision、Type、Priority、Criticality 和 State |
| Acceptance Criterion | ACS/Criterion ID、Revision 和 Scenario Class |
| Verification Method | Method 和 Strategy Revision |
| Test or Check | TCR ID、External ID、Version 和 Validity |
| Verification Evidence | VER ID、State、Result 和 Freshness |
| Validation Link | Need/Intent/Goal、VLS 和 VAE 引用 |
| Coverage Status | 第 11.4 章受控值 |
| Gap | 缺失、失败、阻塞、失效或只覆盖 UI 的说明 |
| Gap Owner and Due Date | 人类责任人、期限和关闭 Evidence |
| Query Boundary | Product、PRD、Requirement Set、Release、Baseline 和统计时间 |

## 14. 质量准则

### 14.1 单项产物质量

| 产物 | 通过条件 |
|---|---|
| ACS | Criterion 原子、可观察、客观、覆盖适用场景且不改变 Requirement |
| VFS | 范围、Method、环境、独立性、覆盖、进入/退出、失败和 Evidence 规则完整 |
| VLS | Need/Intent/Goal、用户、Context、样本、方法、成功、护栏、伦理和局限完整 |
| TCR | 外部 ID、来源、版本、入口、Owner、Validity 和 Trace 可解析 |
| VER | Expected、Actual、Result、版本、环境、输入、原始材料、Provenance 和限制可复核 |
| VAE | Context、参与者、观察、指标、偏差、原始材料和 Conclusion 可复核 |
| ACD | Scope、Evidence、Coverage、Failure、Risk、Outcome、条件、授权和期限完整 |
| VCM | 当前 Revision 的 REQ 至 Criterion、Method、Test、Evidence、Result 和 Gap 链完整 |

### 14.2 Criterion 质量

每个 Criterion 必须满足：

- Relevant：直接验证一项当前 Requirement；
- Atomic：只有一个独立 Expected Result；
- Observable：输出可由授权主体或工具观察；
- Objective：Oracle、阈值和 Pass/Fail 规则明确；
- Repeatable：前置、输入、环境和步骤可重建；
- Complete：角色、数据、异常、边界和适用场景充分；
- Traceable：Requirement、Strategy、TCR、Evidence 和 Revision 可查询；
- Maintainable：Requirement 或实现变化时影响可定位；
- Risk-proportionate：Method、独立性和 Evidence 与 Criticality 匹配。

### 14.3 Evidence 质量

Evidence 必须满足 Identity、Provenance、Integrity、Relevance、Sufficiency、Objectivity、Repeatability/Reproducibility、Independence、Limitations 和 Freshness。任一项 Fail 或 Blocked 时禁止 Evidence Accepted。

### 14.4 Coverage 质量

VCM 必须：

1. 使用当前 Scope、Baseline 和 Revision；
2. 分别统计 Method、Criterion、Evidence、Pass 和 Validation Coverage；
3. 按 Type、Priority、Criticality 和 Scenario Class 分层；
4. 将 Failed、Blocked、Invalidated、Stale、Not Applicable 和 Gap 分开；
5. 提供可反向查询的明细，而不是只给总百分比；
6. 对每个 Gap 指定 Owner、期限和关闭 Evidence。

## 15. 验证与符合性检查

### 15.1 自动检查

工具必须或应执行以下检查：

1. 八类产物 ID 唯一、格式正确且未复用；
2. ACS/VFS/VLS/TCR/VCM、VER/VAE、ACD 使用正确状态模型；
3. 所有必填字段无空白，Not Applicable 有依据和批准；
4. Criterion ID 在 ACS 内唯一且 Revision 可定位；
5. 每个 Criterion 只含一个 When 和一个独立 Expected Result；
6. Expected Result 含模糊词、缺单位、缺阈值或不可观察输出时产生 Finding；
7. 每个当前 Approved/Baselined REQ 有 Method 与 Criterion；
8. Positive、Negative、Boundary、Permission、Idempotency 等适用场景无缺口；
9. 关键业务规则只关联 UI Test 时产生阻断 Finding；
10. TCR 外部 ID、版本、入口、Owner 和 Validity 可解析；
11. VER 的 Requirement/Criterion/Subject/Environment/Input/Expected/Actual/Result/Raw Evidence 完整；
12. VAE 的 Need/Intent/Goal/Participant/Context/Method/Observation/Metric/Limitation/Conclusion 完整；
13. Evidence State Accepted 时 Reviewer、独立性和完整性检查存在；
14. Accepted Evidence 的 Result 或 Conclusion 被误作 State 时阻断；
15. Failed、Blocked、Rejected 或 Invalidated Evidence 被计入 Satisfied 时阻断；
16. Requirement、Criterion、TCR、Subject、Environment 或 Context Revision 不匹配时标记 Stale；
17. 高 Criticality REQ 缺少当前 Accepted Pass VER 时阻断；
18. Web 核心流程缺少 WCAG A/AA 适用性、人工或辅助技术 Evidence 时阻断；
19. Agent 同时是生成者、执行者和唯一 Reviewer 时阻断高风险接受；
20. ACD Outcome、DEC State、C12 Gate Decision 和 Risk Acceptance 混用时阻断；
21. VCM 使用 `latest`、无统计边界或无 Gap Owner 时阻断；
22. IEEE 1012、ISO/IEC/IEEE 29148 或 ISO/IEC 40500 出现替代版本时阻断 C05 Baseline。

自动检查只产生 Evidence 和 Finding，禁止自动接受 Evidence、关闭高风险 Failure、作 Risk Acceptance 或 Acceptance Decision。

### 15.2 人工评审

人工评审必须覆盖：

- Verification、Validation 和 Acceptance 是否分离；
- Criterion 是否保持 Requirement 原意、原子、可观察和客观；
- Scenario Class 是否覆盖真实风险和后端约束；
- Method、环境、独立性和原始 Evidence 是否与 Criticality 匹配；
- Expected Result 是否来自权威 Oracle，而非现有实现；
- 非功能 Measure、阈值、工作负载、样本和不确定性；
- Validation 的用户、Context、样本、偏差、伦理和使用质量覆盖；
- WCAG 完整页面、完整流程、人工和辅助技术验证；
- Agent 生成内容的来源、幻觉、自我验证和权限风险；
- Failure、Waiver、Risk Acceptance、条件和 Acceptance Outcome 是否如实分离；
- Evidence 是否当前、完整、可信、充分并可重建；
- VCM 是否存在只看总百分比、漏掉 Criticality 或隐藏 Gap。

### 15.3 Acceptance Ready 阻断条件

存在以下任一情况时禁止形成 Accept 或 Accept with Conditions：

1. 上游 PRD、Requirement Set 或 REQ 未 Approved/Baselined；
2. Requirement、Criterion、Strategy、TCR、Subject 或 Environment Revision 不可定位；
3. Method Coverage 或 Criterion Coverage 未达到第 10.16 章要求；
4. 高 Criticality REQ 缺少当前 Accepted Pass VER；
5. 存在未授权 Fail、Blocked、Rejected 或 Invalidated Evidence；
6. Evidence 缺少 Expected、Actual、Raw Evidence、Provenance 或 Reviewer；
7. Evidence Accepted 与 Result Pass 被混同；
8. Validation 与 Verification 被合并，或 In Scope Need/Intent/Goal 无 VLS；
9. 真实用户、Context、样本或 Success/Guardrail 条件不完整；
10. 关键业务规则只验证 UI，未验证后端约束；
11. 适用 Negative、Boundary、Permission、Idempotency、Concurrency 或 Recovery 场景缺失；
12. 非功能 Requirement 缺少 Measure、环境、阈值或不确定性；
13. Web 核心流程未达到适用 WCAG 2.2 A/AA 目标且无授权处置；
14. 自动化扫描或 Agent 自检是唯一高风险 Evidence；
15. Agent 是唯一 Author、Producer、Reviewer 和实际 Authority；
16. Waiver 或 Risk Acceptance 被表述为 Requirement Pass；
17. VCM 存在 Stale、孤立、无 Owner Gap 或统计边界不明；
18. IEEE 1012、ISO/IEC/IEEE 29148 或 ISO/IEC 40500 已有替代版但未完成影响复核。

### 15.4 符合性声明限制

通过本章检查只证明符合 C05 当前内部草案规则，不构成 IEEE、ISO、IEC、W3C、WCAG 或其他认证和完整标准符合性声明。

## 16. 追踪与记录要求

### 16.1 最低 Verification Trace

```text
Requirement ID + Revision
  → Acceptance Criteria Set + Criterion ID + Revision
  → Verification Strategy + Method
  → Test Case or Check Reference + Version
  → Verification Evidence Record + State + Result
  → C05 Coverage Matrix + Coverage Status
  → Acceptance Decision
```

### 16.2 最低 Validation Trace

```text
Need / Intent / Goal + Revision
  → PRD / Feature / User Scenario
  → Validation Strategy + Context of Use
  → Validation Evidence Record + State + Conclusion
  → Acceptance Decision
  → Gate / Release / Operational Observation
```

每条关系必须记录源 ID 与 Revision、受控关系、目标 ID 与 Revision、建立依据、建立者、时间、有效版本范围和成员状态，并支持正向与反向查询。

### 16.3 Evidence 与变更追踪

每次执行必须能够查询到 Strategy、Criterion、TCR、Subject、Environment、Input、Oracle、Raw Evidence、Producer、Reviewer、Result/Conclusion 和时间。每次变化必须查询到 Impact Analysis、失效 Evidence、新 Evidence、VCM、ACD、Gate 和 Release 影响。

### 16.4 记录保留

1. Fail、Blocked、Rejected、Invalidated 和被替代 Evidence 禁止删除或覆盖。
2. 原始日志、报告、指标、录屏、截图、模型输出和用户研究材料必须按 Retention Rule 保留。
3. ACD、Waiver、Risk Acceptance、条件、过期和替代历史永久关联保留。
4. 敏感测试数据、个人信息和安全 Evidence 必须执行最小访问、脱敏和保留控制，但不得破坏授权审计。
5. Git 提交、CI URL、聊天和报告摘要不能单独替代业务 Asset ID 和原始 Evidence。

## 17. 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C05 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

任何改变用户可观察行为、质量属性、接口、数据、权限、部署结果或缺陷状态的任务都必须具有可验证 Acceptance/Expected Result。已有 ACS、VFS、VLS 或 TCR 完整覆盖当前 Revision 时 `Reference`；实际执行后按事件创建 VER/VAE，Acceptance Decision 必须由具备 Authority 的人类作出。

VCM 是从 REQ、ACS、VER/VAE 和 TLR 生成的验证覆盖视图，只在 Gate、审计或覆盖查询需要时 `Generate`，禁止另行维护重复事实。

### 17.1 当前 P2 决议

当前项目采用 P2，以下内容禁止裁剪：

- 八类正式产物的独立身份；
- Criterion ID、Requirement Revision、Method、Oracle、Scenario Class、Automation Status 和历史；
- VFS/VLS 的范围、环境、独立性、进入/退出、失败和 Evidence 要求；
- VER/VAE 的 Expected/Actual 或 Observation、原始材料、Producer、Reviewer、Result/Conclusion 和 State；
- Verification、Validation、Acceptance、Evidence State 和 Result 的分离；
- C05 Coverage Matrix 的固定 Revision、Gap Owner 和反向查询；
- 高 Criticality 独立复核、Web 无障碍适用性和 Evidence 失效控制；
- 人类 Acceptance Decision、Waiver 和 Risk Acceptance 引用。

同页展示、自动生成视图、索引或工具内关联不构成身份合并。

### 17.2 允许的呈现裁剪

可以将 Given、When、Then 展示为表格、YAML 或 Gherkin，但必须保留 Criterion ID 和全部受控字段。可以把执行步骤保存在外部测试系统，但 TCR 必须保留稳定引用。可以隐藏不适用字段，但必须记录 Not Applicable、依据和批准。

### 17.3 未来裁剪

未来改为 P1 或其他档位必须通过正式决议和 Change Request。即使把 Criterion、步骤和结果合并展示，也必须保持 Requirement 关联、Evidence 原始引用、身份、版本、责任、状态和接受决定。

## 18. 扩展接口

| 扩展 | 激活条件 | C05 追加要求 | 不替代对象 |
|---|---|---|---|
| E01 架构治理 | 多系统、关键质量权衡、复杂集成或架构演进 | 验证 Architecture Fitness Criteria、Viewpoint Concern 和 Architecture Conformance | C05 REQ/Criteria/Evidence |
| E02 安全、隐私与合规 | 身份、敏感数据、外部暴露、支付、监管或高风险 AI | 使用 Security Verification Plan、威胁/隐私/合规来源、独立测试、敏感 Evidence 和 Risk 决定 | VFS、VER、ACD |
| E03 数据与 AI 数据治理 | 数据质量、数据合同、训练/评估数据或模型质量 | 验证 Data Contract、DQS、Dataset、Lineage、偏差和数据保留 | C04 Data REQ、C05 Evidence |
| E04 知识与正式记录 | 多 Agent、长周期、审计或 Evidence 长期复用 | 增加 Provenance、新鲜度、分类、访问、保留和可检索性验证 | C10 Trace、C11 Configuration |
| E05 产品运营与服务管理 | SLO、监控、事故、灰度、回滚或持续运营 | 验证 SLI/SLO、Monitoring、Rollback、Incident、Observation 和 Post-release Validation | ACD、C11 Release、C12 Gate |

扩展激活只增加控制，不得删除 C05 基础产物、状态、Evidence、Coverage 或独立性要求。

## 19. 参考标准

### 19.1 R1 国际标准

1. [IEEE 1012-2024, IEEE Standard for System, Software, and Hardware Verification and Validation](https://standards.ieee.org/ieee/1012/7324/)。
2. [ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering](https://www.iso.org/standard/72089.html)。
3. [ISO/IEC 25010:2023, Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model](https://www.iso.org/standard/78176.html)。
4. [ISO/IEC 25019:2023, Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Quality-in-use model](https://www.iso.org/standard/78177.html)。
5. [ISO/IEC 25030:2019, Systems and software engineering — Systems and software quality requirements and evaluation (SQuaRE) — Quality requirements framework](https://www.iso.org/standard/72116.html)。

### 19.2 R2 无障碍参考

1. [W3C Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)。
2. [ISO/IEC 40500:2025, Information technology — W3C Web Content Accessibility Guidelines (WCAG) 2.2](https://www.iso.org/standard/91029.html)，仅用于记录当前国际标准化状态；蓝图层级仍按 R2 执行。

### 19.3 R3 表达实践

1. [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)，用于 Given-When-Then 的非规范性表达参考。

### 19.4 来源与复核边界

本规范依据 RVR-C05-0001 核验的官方元数据、公开目录和公开范围形成原创治理规则。IEEE 1012-2024 未公开完整目录，禁止推测条款号。C05 批准或基线前必须复核 IEEE 1012、ISO/IEC/IEEE 29148 和 ISO/IEC 40500 的替代状态。

## 20. 附录

### 20.1 通用资产头模板

```yaml
asset_id: "<受控永久 ID>"
artifact_type: "<正式英文名称与类型代码>"
name_or_summary: "<名称或摘要>"
purpose: "<受控用途>"
source:
  - asset_id: "<来源 ID>"
    revision: "<来源 Revision>"
owner: "<人类责任人>"
state: "<本产物状态模型中的 State>"
current_revision: "<当前 Revision>"
created_at: "<ISO 8601 时间>"
updated_at: "<ISO 8601 时间>"
applicable_scope: "<产品、PRD、Requirement Set、Release 或环境>"
trace_links:
  - relation: "<受控关系>"
    target_id: "<目标 ID>"
    target_revision: "<目标 Revision>"
access_classification: "<Public | Internal | Confidential | Restricted>"
retention_rule: "<保留规则>"
history_reference: "<Revision、Snapshot、Git 或记录引用>"
```

### 20.2 Acceptance Criteria Set 模板骨架

```yaml
acceptance_criteria_set_id: "ACS-0001"
boundary:
  prd: "<PRD ID + Revision>"
  requirement_set: "<RQS ID + Revision>"
  feature: "<FTR ID + Revision>"
  release: "<目标 Release>"
  environment: "<适用环境>"
criteria:
  - criterion_id: "ACS-0001-C001"
    member_revision: "<Revision>"
    requirement: {id: "REQ-0001", revision: "<Revision>"}
    preconditions: "<Given>"
    trigger_or_action: "<When>"
    expected_result: "<Then>"
    observable_output: "<受控输出>"
    data_and_environment: "<数据与环境>"
    applicable_role: "<角色或主体>"
    scenario_class: "<第 8.3 章受控值>"
    priority: "<值与来源>"
    verification_method: ["<Method>"]
    test_oracle: "<权威引用>"
    automation_status: "<第 11.4 章受控值>"
    test_or_check_reference: "<TCR ID 或 Candidate + 期限>"
    open_findings: []
```

### 20.3 Verification Strategy 模板骨架

```yaml
verification_strategy_id: "VFS-0001"
verification_scope: "<Product/PRD/RQS/Release/环境/排除项>"
requirement_classification:
  by_type: {}
  by_criticality: {}
method_selection:
  - requirement_group: "<分组>"
    methods: ["Test", "Analysis"]
    rationale: "<选择理由>"
environment: "<硬件/软件/网络/数据/配置/权限/隔离>"
tools: [{name: "<工具>", version: "<版本>", trust_or_calibration: "<依据>"}]
independence: "<角色分离要求>"
coverage_targets:
  method: "100% in-scope Approved/Baselined REQ"
  criterion: "100% in-scope Approved/Baselined REQ"
  high_criticality_pass_evidence: "100%"
entry_criteria: []
exit_criteria: []
stop_and_resume_conditions: []
failure_handling: "<Fail/Blocked/Flaky/Inconclusive/Defect/重跑>"
evidence_requirements: "<原始材料/完整性/Provenance/Retention/复核/失效>"
```

### 20.4 Validation Strategy 模板骨架

```yaml
validation_strategy_id: "VLS-0001"
need_intent_goal_scope: []
target_users_and_stakeholders: []
context_of_use:
  users: []
  goals: []
  tasks: []
  resources: []
  environment: []
validation_methods: []
participants_or_sample:
  selection: "<规则>"
  size: "<数量与依据>"
  representativeness: "<覆盖与限制>"
quality_in_use:
  beneficialness: "<Applicable | Not Applicable | Not Assessed>"
  freedom_from_risk: "<Applicable | Not Applicable | Not Assessed>"
  acceptability: "<Applicable | Not Applicable | Not Assessed>"
success_and_guardrail_conditions: []
ethics_and_privacy: "<知情/最小化/访问/保留/退出>"
limitations_and_bias: []
acceptance_responsibility: "<Lead/Reviewer/Stakeholder/Authority>"
```

### 20.5 Test Case or Check Reference 模板骨架

```yaml
test_check_reference_id: "TCR-0001"
external_test_or_check_id: "<外部稳定 ID>"
source_system: "<仓库/测试管理/工具/模型/文档>"
requirement: {id: "REQ-0001", revision: "<Revision>"}
criterion: {acs_id: "ACS-0001", criterion_id: "ACS-0001-C001", revision: "<Revision>"}
external_version: "<提交/版本/配置/快照>"
execution_entry: "<命令/作业/页面/程序>"
method: "<第 8.2 章 Method>"
scenario_class: "<第 8.3 章 Class>"
maintenance_owner: "<人类责任人>"
automation_status: "<第 11.4 章受控值>"
current_validity: "<Current | Stale | Disabled | Missing | Unknown>"
last_verified: {time: "<时间>", environment: "<环境>", evidence: "<VER ID>"}
```

### 20.6 Verification Evidence Record 模板骨架

```yaml
verification_evidence_id: "VER-0001"
requirement: {id: "REQ-0001", revision: "<Revision>"}
criterion: {acs_id: "ACS-0001", criterion_id: "ACS-0001-C001", revision: "<Revision>"}
test_or_check: {tcr_id: "TCR-0001", revision: "<Revision>"}
execution_method: "<Method + 步骤/命令引用>"
subject_version:
  code_or_build: "<提交/构建>"
  configuration: "<配置 Revision>"
  data_or_model: "<数据/模型 Revision>"
  release: "<Release>"
environment: "<硬件/软件/网络/依赖/权限/隔离>"
input: "<数据/事件/种子/负载/前置状态>"
expected_result: "<Criterion/Oracle 引用>"
actual_result: "<实际观察与量值>"
verification_result: "<Pass | Fail | Blocked>"
executor: {actor: "<人类/Agent/工具>", run_id: "<RUN ID>", authority: "<权限上下文>"}
execution_time: {start: "<时间>", end: "<时间>", timezone: "<时区>"}
raw_evidence: []
integrity_and_provenance: "<存储/校验/生成链/脱敏/转换>"
limitations: []
state: "Collected"
review: {reviewer: "<Reviewer>", independence: "<独立性>", time: "<时间>"}
```

### 20.7 Validation Evidence Record 模板骨架

```yaml
validation_evidence_id: "VAE-0001"
need_intent_goal: []
product_and_release: "<产品/Build/配置/环境/版本>"
participants_and_stakeholders:
  groups: []
  selection: "<规则>"
  size: "<数量>"
  representativeness: "<覆盖与限制>"
context_of_use: "<用户/任务/资源/环境>"
method: {strategy: "VLS-0001", procedure: "<程序>", executor: "<主体>", time: "<时间>"}
observations: []
success_metric_results: []
quality_in_use_results:
  beneficialness: "<结果>"
  freedom_from_risk: "<结果>"
  acceptability: "<结果>"
deviations_and_limitations: []
raw_materials: []
ethics_and_privacy_controls: "<知情/最小化/访问/脱敏/保留>"
validation_conclusion: "<Supports | Does Not Support | Inconclusive>"
state: "Collected"
review: {reviewer: "<Reviewer>", independence: "<独立性>", time: "<时间>"}
```

### 20.8 Acceptance Decision 模板骨架

```yaml
acceptance_decision_id: "ACD-0001"
acceptance_scope:
  product: "<Product + Revision>"
  prd: "<PRD + Revision>"
  requirement_set: "<RQS + Revision>"
  release: "<Release>"
  environment: "<环境>"
verification_evidence: []
validation_evidence: []
coverage_matrix: {id: "VCM-0001", revision: "<Revision>", measured_at: "<时间>"}
failed_blocked_invalidated_items: []
residual_risk: []
acceptance_outcome: "<Accept | Accept with Conditions | Reject | Defer>"
conditions: []
approver: {actor: "<授权人>", independence: "<独立性>", basis: "<批准依据>"}
effective_time: "<时间>"
expiry_time: "<时间或 None>"
gate_and_change_references: []
state: "Proposed"
```

### 20.9 Coverage Matrix 模板骨架

```yaml
coverage_matrix_id: "VCM-0001"
query_boundary:
  product: "<Product>"
  prd: "<PRD + Revision>"
  requirement_set: "<RQS + Revision>"
  release: "<Release>"
  baseline: "<BSL ID>"
  measured_at: "<时间>"
rows:
  - requirement: {id: "REQ-0001", revision: "<Revision>", type: "<Type>", criticality: "<值>", state: "<DOC State>"}
    criterion: {acs_id: "ACS-0001", id: "ACS-0001-C001", revision: "<Revision>", scenario_class: "<Class>"}
    verification_method: "<Method + VFS Revision>"
    test_or_check: {tcr_id: "TCR-0001", external_id: "<ID>", version: "<Version>", validity: "Current"}
    verification_evidence: {id: "VER-0001", state: "Accepted", result: "Pass", freshness: "Current"}
    validation_link: "<Need/Intent/Goal/VLS/VAE>"
    coverage_status: "Satisfied"
    gap: "None"
    gap_owner_and_due_date: "Not Applicable"
```

### 20.10 Method 选择速查表

| Requirement 类型 | 首选候选 Method | 必须追加考虑 |
|---|---|---|
| Functional | Test、Demonstration | Positive、Negative、Boundary、完整流程 |
| Business Rule | Test、Analysis | 后端规则、组合、优先级、时间和例外 |
| Data | Test、Analysis、Inspection | 语义、完整性、质量、保留和迁移 |
| Permission and Access | Test、Inspection | 允许、拒绝、撤销、隔离和审计 |
| Interface | Test、Analysis、Inspection | 输入输出、错误、兼容、幂等和顺序 |
| UI and Interaction Behavior | Test、Demonstration、Inspection | 状态、权限、响应、完整流程和无障碍 |
| Quality | Test、Analysis、Assessment | Measure、环境、负载、阈值、样本和不确定性 |
| Security | Test、Analysis、Inspection、Assessment | 威胁、负向场景、独立性和剩余 Risk |
| Audit and Recording | Test、Inspection | 主体、事件、时间、完整性、查询和保留 |
| Agent Behavior Constraint | Test、Demonstration、Review、Assessment | Context、工具、权限、停止、升级和不可预测输入 |

本表只用于提出候选，VFS 必须按实际 Requirement 和 Risk 作授权选择。

### 20.11 C05 质量检查清单

- [ ] 八类正式产物具有独立 ID、状态、Owner、Revision 和历史。
- [ ] ACS 边界固定 PRD、RQS、Feature、Release、环境和版本。
- [ ] 每个 Criterion 具有稳定成员 ID、Requirement ID 与 Revision。
- [ ] Given、When、Then 或等价字段完整且可建立、可触发、可观察。
- [ ] 每个 Criterion 只有一个独立 Expected Result。
- [ ] Expected Result 来自 Requirement/Test Oracle，不是从实现反推。
- [ ] Data、Environment、Role、Priority、Method 和 Automation Status 完整。
- [ ] Positive、Negative、Boundary、Permission 和 Idempotency 已逐项判定。
- [ ] Concurrency、Retry、Recovery、Quality、Accessibility 和 Agent 场景已按风险判定。
- [ ] 关键业务规则未只验证 UI。
- [ ] VFS 的范围、Method、环境、工具、独立性、覆盖、进入/退出和 Evidence 完整。
- [ ] VLS 的 Need/Intent/Goal、用户、Context、样本、方法、成功、护栏、伦理和局限完整。
- [ ] TCR 外部 ID、系统、版本、入口、Owner、Automation 和 Validity 可解析。
- [ ] VER 的 Subject、Environment、Input、Expected、Actual、Result 和 Raw Evidence 完整。
- [ ] VAE 的 Participant、Context、Observation、Metric、Limitation、Raw Material 和 Conclusion 完整。
- [ ] Evidence State 与 Result/Conclusion 分离。
- [ ] Evidence Accepted 未被当作 Requirement Pass 或 Product Accept。
- [ ] Failed、Blocked、Rejected、Invalidated 和 Stale Evidence 未计入 Satisfied。
- [ ] Evidence Provenance、Integrity、Relevance、Sufficiency、Independence 和 Freshness 通过。
- [ ] 非功能验证具有 Measure、公式、单位、环境、阈值、样本和不确定性。
- [ ] Web 核心流程具有 WCAG 2.2 A/AA 完整页面和完整过程覆盖。
- [ ] 无障碍验证组合自动化、键盘、人工和适用辅助技术。
- [ ] Agent 生成 Test 保留 Run/Context/模型标识并经人类复核。
- [ ] 高 Criticality Requirement 具有 100% 当前 Accepted Pass VER。
- [ ] Method Coverage 和 Criterion Coverage 达到 100% 或具有批准 Not Applicable。
- [ ] VCM 固定 Revision、统计边界、Coverage Status、Gap Owner 和期限。
- [ ] Waiver/Risk Acceptance 未改变 Result 或 Requirement 满足结论。
- [ ] ACD 的 Scope、Evidence、Coverage、Failure、Risk、Outcome、条件和有效期完整。
- [ ] C05 Acceptance Decision 未替代 C12 Gate Decision。
- [ ] 三组需复核标准的版本新鲜度已在基线前检查。

### 20.12 正反例

正例：

```text
Criterion ID: ACS-0001-C004
Requirement: REQ-0042 R3
Given: 账户状态为 Active，连续失败次数为 4，当前时间为 2026-07-28T10:00:00+08:00
When: 该账户提交第 5 次错误密码
Then: 身份认证服务在 1 秒内将账户状态置为 Locked，并将解锁时间设为 15 分钟后
Method: Test
Scenario Class: Boundary, Permission and Access
```

该 Criterion 固定角色、状态、次数、时间、输出和阈值。审计事件是另一项独立 Expected Result，必须使用另一 Criterion ID。

反例：

```text
用户登录应正常、快速、安全，失败时给出友好提示，并记录必要日志。
```

不符合原因：包含登录、性能、安全、提示和日志多个独立结果；“正常”“快速”“安全”“友好”“必要”无判定条件；缺少角色、数据、环境、阈值和 Oracle。

Evidence 误判反例：

```text
Evidence State: Accepted
Verification Result: Fail
Acceptance 说明: Evidence 已接受，所以 Requirement 通过。
```

Evidence Accepted 只说明失败证据可信。Requirement 仍为 Not Satisfied，必须处理 Defect、Change、Waiver 或 Risk，但禁止改写为 Pass。

### 20.13 参考的国际标准条款与公开范围映射总表

| 参考 | 条款或公开范围 | 公开主题 | C05 落地位置 | 采用方式与限制 |
|---|---|---|---|---|
| IEEE 1012-2024 | IEEE 官方公开范围 | Verification 判断活动产物符合 Requirement | 第 6、8.2、10.2、10.5–10.6 章 | 分离 Verification；未获得合法全文时不引用具体条款号 |
| IEEE 1012-2024 | IEEE 官方公开范围 | Validation 判断产品满足 intended use 和 user needs | 第 6、9、10.2、10.7、10.10 章 | 分离 Validation；不以 Requirement Pass 自动推导 |
| IEEE 1012-2024 | IEEE 官方公开范围 | V&V 覆盖系统、软件、硬件、接口及不同 integrity level | 第 3、7、10.5、14–15 章 | 以 C04 Criticality/C02 Risk 决定强度；不自建 IEEE Integrity Level |
| IEEE 1012-2024 | IEEE 官方公开范围 | Analysis、evaluation、review、inspection、assessment、testing | 第 8.2、10.5、20.10 章 | 建立内部 Method 分类；方法名不自动证明充分 |
| ISO/IEC/IEEE 29148:2018 | 5.2.5 | 单项 Requirement 特性 | 第 9.2、10.3、14.2、15.3 章 | 不可验证 Requirement 阻断 C05 并返回 C04 |
| ISO/IEC/IEEE 29148:2018 | 5.2.6 | Requirement Set 特性 | 第 10.16、13.9、14.4 章 | 建立集合覆盖；不替代 C04 RQS |
| ISO/IEC/IEEE 29148:2018 | 5.2.8 | Requirement 属性 | 第 8.5、9.2、13.2、13.9 章 | 接收 Method、Priority、Criticality 和 Trace |
| ISO/IEC/IEEE 29148:2018 | 6.3.1–6.3.3 | Stakeholder needs and requirements definition | 第 9、10.7、10.10、16.2 章 | Validation 追踪 Need/Intent/Goal 和 Context |
| ISO/IEC/IEEE 29148:2018 | 6.4.1–6.4.3 | System/Software requirements definition | 第 9、10.3–10.6、16.1 章 | Verification 追踪 REQ、Criterion、Method 和 Evidence |
| ISO/IEC/IEEE 29148:2018 | 6.6.1–6.6.3 | Requirements management、Change、Measurement | 第 9.6、10.11、10.16–10.17、16.3 章 | 管理 Revision、Coverage、失效和重验证 |
| ISO/IEC 25010:2023 | 3.1–3.9 | 九类产品质量特性 | 第 10.12、13.3、20.10 章 | 对适用质量逐类定义 Method、Measure 和 Evidence |
| ISO/IEC 25010:2023 | 4.1 | 产品质量模型结构 | 第 10.12、14.4 章 | 按特性/子特性组织覆盖 |
| ISO/IEC 25010:2023 | 4.2 | 产品质量模型目标 | 第 10.12、13.3、13.6 章 | 固定目标产品、组件、数据、环境和版本 |
| ISO/IEC 25010:2023 | 5 | 与使用质量模型关系 | 第 10.2、10.12–10.13 章 | 产品属性 Verification 与实际使用 Validation 分离 |
| ISO/IEC 25010:2023 | Annex C | 使用模型进行测量 | 第 10.12、13.2、13.6 章 | 记录 Measure、算法、阈值和环境；不复制附录 |
| ISO/IEC 25019:2023 | 3.2.1 | beneficialness | 第 10.7、10.10、10.13、13.7 章 | 评价适用 usability、accessibility、suitability 等效益 |
| ISO/IEC 25019:2023 | 3.2.2 | freedom from risk | 第 10.7、10.10、10.13、10.15 章 | 覆盖经济、环境/社会、健康和生命 Risk |
| ISO/IEC 25019:2023 | 3.2.3 | acceptability | 第 10.7、10.10、10.13、13.7 章 | 记录参与者反应、经验、信任和局限 |
| ISO/IEC 25019:2023 | 4.2–4.5 | Stakeholder、Context、模型结构和目标 | 第 6、10.7、10.10、13.4、13.7 章 | 固定用户、任务、资源、环境和目标 |
| ISO/IEC 25019:2023 | 4.6 | 使用质量模型 | 第 10.7、10.13、14.1 章 | 用于 Validation、Acceptance 和改进 |
| ISO/IEC 25019:2023 | Annex B–D | Need 关系、影响和应用示例 | 第 10.7、10.10、18 章 | 仅作场景设计参考，不复制示例正文 |
| ISO/IEC 25030:2019 | 6.1–6.4 | 质量需求概念、类型、目标、模型和测量 | 第 10.12、13.2–13.3、20.10 章 | 质量 Criterion 固定 Measure、阈值、环境和方法 |
| ISO/IEC 25030:2019 | 6.5.1–6.5.5 | 来源、产品类别、关系、派生和权衡 | 第 8.5、10.12、16 章 | 保留来源、关系、Decision 和 Risk |
| ISO/IEC 25030:2019 | 7.1–7.4 | 质量需求过程、获取和定义 | 第 9.2–9.3、10.6、10.12 章 | 从 C03/C04 接收，不在 C05 新建质量 REQ |
| ISO/IEC 25030:2019 | 8.1 | 实施质量需求关键因素 | 第 7、10.6、15 章 | 明确责任、资源、环境、工具和进入/退出 |
| ISO/IEC 25030:2019 | 8.2 | 质量需求追踪 | 第 10.16、13.9、16.1 章 | VCM 连接 REQ、Criterion、Method、Test 和 Evidence |
| ISO/IEC 25030:2019 | 8.3 | 测试质量需求关键因素 | 第 10.9、10.12、13.6 章 | 记录负载、数据、重复、窗口、不确定性和结果 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 1 | Perceivable | 第 10.13、15、20.11 章 | Web 核心流程按适用 A/AA 检查 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 2 | Operable | 第 10.13、15、20.11 章 | 覆盖键盘、焦点、输入和操作 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 3 | Understandable | 第 10.13、15、20.11 章 | 覆盖可预测、帮助、错误和认证 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 4 | Robust | 第 10.13、15、20.11 章 | 覆盖名称/角色/值、状态消息和兼容 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 5.2.1 | Conformance Level | 第 10.13、15.3 章 | 默认 Level AA，含适用 A 与 AA |
| WCAG 2.2 / ISO/IEC 40500:2025 | 5.2.2–5.2.3 | Full pages、Complete processes | 第 6、10.13、15.3 章 | 核心流程覆盖完整页面和完整过程 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 5.2.4–5.2.5 | Accessibility-supported use、Non-interference | 第 10.13、13.6、15 章 | 记录技术与辅助技术；自动扫描不充分 |
| WCAG 2.2 / ISO/IEC 40500:2025 | 5.3 | Conformance Claims | 第 10.13、15.4、19.2 章 | C05 默认只记录目标和 Evidence，不自动生成外部声明 |
