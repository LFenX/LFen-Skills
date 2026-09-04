# C12 评审、质量门禁与产品健康规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C12 |
| 英文名称 | Review, Quality Gate and Product Health Specification |
| 正式文件名 | `C12_Review_Quality_Gate_and_Product_Health_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3 至 C11 V6.3 |
| 生产前调研 | RVR-C12-0001 |
| 横向治理 | C01 至 C11、E01 至 E05 |
| 后续规范 | E01 至 E05 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule 保留；评审、Gate、Waiver、Risk Acceptance、健康指标、复盘、改进行动、状态转换和更正历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式 Gate、Waiver、Risk Acceptance、Release Decision 或自动状态写入授权。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品资产和活动的评审方法、进入下一状态或阶段的最低条件、例外与豁免、风险接受、产品健康评价、复盘和持续改进。

本规范实现以下目标：

1. 使评审对象、输入、准则、发现、结论、整改和复核可追溯；
2. 使 Quality Gate 成为状态或阶段转换前的强制控制，而不是普通检查清单；
3. 使 Checklist、Review Result 和 Gate Decision 保持独立事实源；
4. 使 Pass、Conditional Pass、Reject 和 Waive 具有明确条件、Authority 和有效边界；
5. 使 Exception/Waiver 有范围、理由、Risk、补偿控制、责任人、失效和撤销；
6. 使 Risk Acceptance 只接受受控剩余风险，不改写 Requirement、Evidence 或实际 Risk；
7. 使 Product Health 由定义明确、来源可查、周期受控、阈值可解释的指标评价；
8. 使缺失数据、异常趋势、阈值突破和指标局限得到公开披露；
9. 使 Retrospective 将结果、偏差、Incident 和 Feedback 转化为 Learning 与 Improvement Action；
10. 使 Agent 和自动化工具可以计算、检查和起草，但不能自批高风险输出或风险接受；
11. 使 C01 至 C11 的 Readiness Assertion 由 C12 统一作受控 Gate Decision；
12. 防止通过拆分、隐藏、降级、删除记录或改变分母优化指标。

## 3. 适用范围

本规范适用于：

- C01 至 C11 管理的全部正式产品、工程、Agent、Evidence、Decision、Trace、Configuration 和 Release 资产；
- E01 至 E05 当前激活或经适用性判定需要评价的领域资产；
- 人工评审、同行评审、技术评审、管理评审、独立评审、审核、检查、发布评审和事后评审；
- Discovery Ready、Specification Ready、Agent Execution Ready、Release Ready、Learning Closed 五个强制生命周期 Gate；
- Initiative Ready、PRD Ready、Requirement Ready、Design Ready、Context Ready、Trace Ready、Configuration Ready 等受控领域 Gate；
- Exception、Waiver、Residual Risk Acceptance、Gate Condition、纠正措施和改进行动；
- Requirement、Agent、Engineering、Process 和适用产品质量维度的健康评价；
- 人工、规则、CI/CD、分析平台、Agent 或其他工具生成的检查、测量和报告；
- P2 档位下 8 类 C12 正式产物的身份、状态、必填信息、模板和质量检查；
- E04 已激活的记录、元数据、访问、保留、审计和历史恢复要求。

只要某项结论用于状态转换、Baseline、执行授权、发布、风险接受、合规声明、对外承诺或持续改进，即使载体不是 Markdown，也适用本规范。

### 3.1 横向生效

C12 对 C01 至 C11 横向生效：

1. C01 至 C11 定义业务和工程对象的内容、Evidence、Readiness Assertion 与领域状态；
2. C12 定义 Review、Gate、Waiver、Risk Acceptance、Health 和 Improvement；
3. C12 可以阻断下游消费，但不得直接改写上游资产内容；
4. Gate Decision 必须固定上游资产的 Revision、Snapshot、Baseline 和适用 Scope；
5. 上游输入发生实质变化时，原 Gate 必须重新评价、过期或被后继 Gate 替代。

### 3.2 蓝图必备主题映射

| 蓝图必备主题 | 本规范位置 |
|---|---|
| 评审类型 | 10.1 |
| 评审角色 | 第 7 章 |
| 评审输入和输出 | 10.2 至 10.4、13.1 |
| 质量门禁 | 10.5 至 10.12 |
| 例外和豁免 | 10.13、13.4 |
| 风险接受 | 10.14、13.5 |
| 健康指标 | 10.15 至 10.19 |
| 阈值和趋势 | 10.20 |
| 复盘 | 10.22、13.7 |
| 改进行动 | 10.23、13.8 |
| 审计 | 10.24、16 |
| 模板与检查清单 | 第 20 章 |

## 4. 不适用范围

本规范不负责：

- 定义 C01 Need、Evidence、Problem、Intent 和 Goal 的业务内容；
- 定义 C02 Scope、Risk、Constraint、Dependency 和 Success Metric 的业务目标；
- 定义 C03 PRD、Feature、Scenario 和 Release Intent；
- 定义 C04 Requirement 身份、语义和演进；
- 执行 C05 Verification/Validation 或判断原始 Evidence 的技术真实性；
- 定义 C06 UX、Architecture、Interface、Data 和 Failure Design；
- 创建 C07 Authorization、Approval Matrix、Stop 和 Escalation 权限；
- 组装 C08 Context 或判断 Source Priority；
- 执行 C09 Agent Run、Command、Tool 和 Actual Change；
- 建立 C10 Trace Link、Coverage 或 Impact Query；
- 管理 C11 Asset ID、Revision、Snapshot、Baseline、Change 和 RLC；
- 替代 E01 至 E05 的领域专属质量、安全、数据、记录或运营控制；
- 规定组织认证、法规合格性或第三方审核结论；
- 为所有产品设定统一数值 Threshold。

C12 可以消费上述事实，但禁止：

- 用 Review Record 代替被评审对象的 Approval；
- 用 QGC 代替实际检查或 Gate Decision；
- 用 GTE 代替 C05 Acceptance Decision、C11 Change Decision 或 Baseline Approval；
- 用 EWR 声明被偏离要求已经满足；
- 用 RAR 声明 Risk 不存在或已经解决；
- 用 PHR 单一总分替代质量特性、Evidence 和 Threshold 明细；
- 用 Retrospective 会议摘要替代 Learning 与 Action；
- 用指标改善倒推删除、拆分或降级历史事实。

## 5. 规范性用语与受控判定

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“必须”和“禁止”规则不得通过普通 EWR 绕过。法律、监管、合同、Safety、Security、Privacy、不可逆数据和明确 Non-waivable Gate 项不得豁免。

### 5.2 领域判定值

以下值不是正式产物 State：

| 字段 | 受控值 |
|---|---|
| Gate Outcome | `Pass`、`Conditional Pass`、`Reject`、`Waive` |
| Review Conclusion | `Conformant`、`Conformant with Findings`、`Nonconformant`、`Inconclusive` |
| Check Result | `Pass`、`Fail`、`Blocked`、`Not Applicable`、`Not Evaluated` |
| Finding Severity | `Blocker`、`Critical`、`Major`、`Minor`、`Observation` |
| Gate Item Blocking Level | `Blocking`、`Condition-Eligible`、`Advisory` |
| Waivability | `Waivable`、`Non-waivable` |
| Threshold Result | `Within`、`Near`、`Breached`、`Not Evaluated` |
| Trend | `Improving`、`Stable`、`Degrading`、`Insufficient Data` |
| Data Status | `Complete`、`Partial`、`Unavailable`、`Unreliable` |
| Health Conclusion | `Healthy`、`At Risk`、`Unhealthy`、`Indeterminate` |
| Action Member Status | `Open`、`In Progress`、`Blocked`、`Resolved`、`Closed`、`Reopened`、`Cancelled` |

RVR、RTR 只使用 EXEC State；QGC、PHR、IAP 只使用 DOC State；GTE、EWR、RAR 只使用 DEC State。

### 5.3 Gate Outcome 与 DEC State 映射

| Gate Outcome | GTE State | 语义 |
|---|---|---|
| Pass | Approved | 全部 Blocking 项满足，未满足项不影响进入下一阶段 |
| Conditional Pass | Conditionally Approved | 无 Non-waivable Blocking Fail；条件、Owner、期限和验证明确 |
| Reject | Rejected | 存在未处置 Blocking Fail、证据不足或 Authority 不允许进入 |
| Waive | Waived | Gate 或可豁免项在 EWR/RAR 支持下有界跳过；不表示要求满足 |

禁止使用 `Passed`、`Conditional Passed`、`Failed` 或 `Approved with Risk` 作为 GTE Formal State。

### 5.4 事实、推断、评价与决定

| 类型 | 允许内容 | 禁止内容 |
|---|---|---|
| Fact | Asset、Revision、Evidence、Metric Value、Finding、Run、Approval 和实际状态 | 未核验工具摘要 |
| Inference | 明确标记的原因候选、影响候选、Trend Interpretation 和待验证假设 | 直接写成已证实原因 |
| Evaluation | 按固定 Scope、Criteria、Measure 和 Threshold 形成的结论 | 不公开输入、规则或未知项的评分 |
| Gate Decision | Authority 基于评价和 Risk 作出的 C10 Decision，范围限于 Gate、Waiver 或 Risk Acceptance | Agent 私有推理或无权结论 |
| Learning | 经 Evidence 支持、可回流上游或形成 Action 的结论 | 聊天感想或对个人的归责 |

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Review | 对固定对象和 Revision，按明确准则、角色和 Evidence 执行的系统性检查 |
| Review Record | 记录一次 Review 的计划、输入、执行、发现、结论、整改和复核的 EXEC 产物 |
| Quality Gate | 资产或活动进入下一状态或阶段前必须满足的受控条件集合 |
| Gate Profile | 一类 Gate 的 Scope、QGC、角色、Evidence、阻断、例外和有效规则 |
| Gate Instance | 对特定对象、Revision、Scope 和时间点执行的一次 Gate 评价 |
| Quality Gate Checklist | 定义 Gate 检查项、判定规则、Evidence、阻断级别和例外规则的 DOC 产物 |
| Gate Decision | Authority 对特定 Gate Instance 作出的 Pass、Conditional Pass、Reject 或 Waive 决定 |
| Readiness Assertion | 上游规范基于领域规则形成的可检查就绪陈述；不是 Gate Decision |
| Finding | Review 或检查识别的符合、偏差、缺口、风险或观察成员 |
| Blocker | 未处置时禁止进入下一状态、阶段或发布的 Finding 或 Gate Item |
| Condition | Conditional Pass 必须在指定 Owner、期限和验证方式下满足的义务 |
| Exception | 对受控规则在具体 Scope 内偏离的请求或决定 |
| Waiver | 在明确 Scope、期限和补偿控制下不执行某项可豁免要求的决定 |
| Risk Acceptance | 有权角色明确接受剩余 Risk 及其范围、期限和监控条件的决定 |
| Product Health | 通过定义、来源、周期、Threshold 和趋势受控的指标评价产品与过程状态 |
| Metric | 对明确对象集合、属性和时间窗口执行的受控测量定义及结果 |
| Threshold | 将 Metric Value 映射为评价结果的受控边界 |
| Trend | 在可比定义、范围和周期上对 Metric 方向的评价 |
| Retrospective | 对实际结果、偏差、Incident 和 Feedback 执行的结构化回顾 |
| Learning | 可由 Evidence 复核并影响产品、过程、Decision 或 Action 的受控认识 |
| Corrective Action | 消除已发生不符合原因并防止再发生的行动 |
| Improvement Action | 提升结果、能力、质量或过程的受控行动 |
| Metric Gaming | 通过改变记录、Scope、分类、分母、时间点或可见性改善指标而不改善真实结果 |

`Risk` 和 `Residual Risk` 的唯一语义直接适用 C02；C12 只管理其 Review、Gate、Waiver 和 Risk Acceptance 处置。无限定 `Threshold` 的定义 Authority 为 C12，专业域阈值必须使用限定名称并声明专业化关系。

### 6.1 必须区分的对象

| 对象 | 回答的问题 | 不得替代 |
|---|---|---|
| QGC | 应检查什么 | 实际检查结果 |
| RVR | 实际检查了什么、发现什么 | Gate Decision |
| GTE | 是否获准进入下一阶段 | 资产 Approval、Baseline |
| EWR | 哪项规则被有界偏离 | Requirement Pass |
| RAR | 哪项剩余 Risk 被接受 | Risk Resolution |
| PHR | 当前周期健康如何 | Gate Decision、原始 Metric Source |
| RTR | 从实际结果学到什么 | Incident、Defect 或原始 Evidence |
| IAP | 后续如何改进 | 已完成改进的证据 |

## 7. 角色、职责与独立性

| 角色 | 主要职责 | 禁止事项 |
|---|---|---|
| Review Owner | 定义 Review Scope、对象、输入、准则、Reviewer 和输出 | 操纵对象 Revision 或隐藏 Finding |
| Reviewer | 执行检查、记录 Evidence、Finding 和结论 | 评审未提供的假定输入 |
| Independent Reviewer | 对高风险对象提供组织、职责或技术独立复核 | 接受自身生成或实施的高风险输出 |
| Gate Owner | 维护 Gate Profile、QGC 和运行日程 | 将 QGC 当作 GTE |
| Gate Approver | 基于 RVR、QGC、Evidence 和 Risk 作 GTE 决定 | 绕过 Non-waivable Blocker |
| Exception/Waiver Owner | 提交偏离范围、理由、Risk 和补偿控制 | 申请无期限或无边界豁免 |
| Waiver Authority | 审批、拒绝、撤销、替代或使 EWR 过期 | 把 Waiver 写成 Requirement Pass |
| Risk Owner | 维护 Risk、控制、剩余 Risk 和监控 | 将接受决定等同风险消除 |
| Risk Acceptance Authority | 在授权范围内审批 RAR | 接受未定义、不可监控或超权 Risk |
| Product Health Owner | 管理 Metric Catalog、PHR、Threshold 和行动 | 改分母或删除历史改善指标 |
| Metric Steward | 维护公式、Source、Query、Data Quality 和可比性 | 无版本修改定义 |
| Retrospective Facilitator | 组织事实回顾、原因分析、Learning 和 Action | 以个人归责代替系统分析 |
| Improvement Owner | 维护 IAP 和 Action Member | 无关闭 Evidence 标记完成 |
| Records Steward | 按 E04 管理元数据、访问、保留、更正和审计 | 无痕删除 Rejected、Waived 或 Expired 历史 |
| Agent/Automation Operator | 计算、检查、起草、提示缺口和生成候选报告 | 自批、自验、自行接受 Risk 或关闭高风险 Action |

### 7.1 最低独立性

1. Agent 禁止担任 Accountable、Gate Approver、Waiver Authority 或 Risk Acceptance Authority；
2. High/Critical Risk、Release、Security、Privacy、Compliance、Safety、不可逆数据和外部承诺场景中，Author/Implementer、Reviewer 与 Approver 必须按 C07 分离；
3. RVR 的执行者可以与被评审对象 Owner 相同仅限已批准的 Low Risk Self-review 场景；最终 GTE 仍由有权人类作出；
4. Metric Steward 不得单独批准有利于自身绩效评价的定义变化；
5. Retrospective Facilitator 不得隐去管理、流程、工具或系统性贡献因素；
6. RAR Approver 必须拥有被接受影响范围的责任与授权。

## 8. 管理对象、关系与唯一事实源

### 8.0 V6.3 最小派生审核视图

V6.3 首版固定生成三类审核视图：单任务审核摘要、项目当前状态与遗留问题、137→6 Profile 迁移映射与完整性报告。其他矩阵、报告和清单仅在 Gate、审计、查询或专业触发成立时生成。

所有 DerivedView 必须记录生成器、Source Snapshot、来源对象、生成时间和完整性状态；可以删除后重建，禁止直接写入新的批准、事实或风险接受结论。Reviewer 发现视图与 TaskOutcome、AuthorityAsset 或 Evidence 冲突时，必须修正权威来源或生成规则，再重新生成视图。

### 8.1 正式产物

| 代码 | 正式产物 | 状态模型 | 唯一事实源 |
|---|---|---|---|
| RVR | Review Record | EXEC | 一次评审执行和结论 |
| QGC | Quality Gate Checklist | DOC | Gate 检查标准 |
| GTE | Gate Decision | DEC | 特定 Gate 实例决定 |
| EWR | Exception or Waiver Record | DEC | 规则/门禁偏离决定 |
| RAR | Risk Acceptance Record | DEC | 剩余 Risk 接受决定 |
| PHR | Product Health Report | DOC | 周期健康评价 |
| RTR | Retrospective Record | EXEC | 回顾执行、Learning 和行动结论 |
| IAP | Improvement Action Plan | DOC | 改进行动集合 |

八类产物不得因使用同一审批单、仪表盘、工单或文档而失去独立身份。

### 8.2 受控关系

至少建立：

- RVR `addresses` 被评审对象和适用 Concern；
- RVR `depends-on` 固定 QGC/Review Criteria 和输入 Evidence；
- GTE `depends-on` QGC、RVR、Evidence、EWR、RAR 和当前 Baseline；
- EWR `addresses` 被偏离规则或 Gate Item；
- RAR `addresses` C02/E02/E03/E05 或其他权威 Risk；
- PHR `generated-by` 固定 Query/Run，并 `depends-on` Metric Definition；
- RTR `observed-from` Release、Run、Incident、Feedback 和 PHR；
- IAP `derives-from` Finding、Learning、Risk 或 PHR；
- 后继 QGC、GTE、EWR、RAR、PHR、RTR、IAP 使用 `supersedes`；
- Action 完成 Evidence 使用 `verified-by`；
- 发布资产使用 `released-in` C11 RLC。

禁止以 `related-to` 或未定义“关联”建立正式 Link。

### 8.3 唯一事实源边界

| 信息 | 唯一事实源 | C12 处理 |
|---|---|---|
| Need/Scope/PRD/Requirement/Design | C01 至 C06 | 固定 Revision 并评审 |
| Authorization/Context/Run | C07 至 C09 | 消费 Authority、Snapshot 和 Evidence |
| Trace/Coverage/Impact | C10 | 消费固定查询结果 |
| Configuration/Change/Release | C11 | 消费 Baseline、CHG、RLC 和 Drift |
| Verification/Validation | C05 | 评审 Evidence，不复制结果 |
| Risk | C02 或适用扩展 | RAR 引用，不建立平行 Risk |
| Review 执行 | C12 RVR | 记录对象、准则、发现和结论 |
| Gate 决定 | C12 GTE | 批准状态/阶段进入 |
| Waiver | C12 EWR | 管理可豁免偏离 |
| Risk Acceptance | C12 RAR | 管理剩余 Risk 接受 |
| Health | C12 PHR | 固定指标评价快照 |
| Learning/Improvement | C12 RTR/IAP | 回流上游和关闭行动 |
| Record 生命周期 | E04 | C12 提供领域元数据和历史 |

## 9. 生命周期与工作机制

### 9.1 评审与 Gate 总流程

```text
建立 Approved QGC / Gate Profile
  → 固定 Gate Instance 对象、Revision、Scope 和输入
  → 创建 RVR Planned
  → 核验 Reviewer、独立性、Evidence 和准则
  → RVR Ready → Running
  → 记录 Check Result、Finding 和整改
  → RVR Completed
  → 独立复核 RVR Accepted/Rejected
  → 汇总未满足项、EWR、RAR 和 Condition
  → GTE Proposed → Under Review
  → Approved / Conditionally Approved / Rejected / Waived
  → 进入下一状态/阶段或返回整改
  → 输入变化、条件到期、风险变化
  → Re-evaluate / Supersede / Expire
```

### 9.2 健康与改进总流程

```text
批准 Metric Definition 和 Threshold
  → 固定 Period、Scope、Population、Source 和 Query
  → 收集 Metric Value 与 Data Quality
  → 评价 Threshold 和 Trend
  → 形成 PHR
  → 识别异常、Risk、Finding 和系统性偏差
  → 执行 RTR
  → 形成 Learning / Decision / No-action Rationale
  → 创建或更新 IAP
  → 执行 Action
  → 验证 Success Condition
  → 关闭 Action
  → 下一周期验证真实结果是否改善
```

### 9.3 初始化

产品在 Discovery Ready 前必须建立：

- 五个强制 Gate 的 Owner 和 Authority；
- 五个强制 Gate 的 QGC Draft/Approved 计划；
- Review Type、独立性和 Finding 规则；
- EWR 和 RAR Authority；
- Metric Catalog、21 项最低指标的适用性和 Owner；
- Threshold、Trend、Data Quality 和 Unknown 规则；
- PHR 周期；
- RTR 触发器；
- IAP Member 状态、优先级、期限和关闭 Evidence 规则；
- C11 版本、Baseline 和 Change 接口；
- E04 记录、访问、保留和审计接口；
- E01 至 E05 激活复评规则。

## 10. 强制规则

### 10.1 评审类型

受控 Review Type 至少包括：

- Content Review；
- Peer Review；
- Technical Review；
- Design Review；
- Verification/Validation Review；
- Agent Output Review；
- Change Review；
- Baseline/Configuration Review；
- Traceability Review；
- Gate Review；
- Release Review；
- Management Review；
- Internal Audit；
- Post-implementation Review；
- Retrospective Review。

每个 Review Type 必须定义 Purpose、Scope、Object、Input、Criteria、Reviewer、Independence、Output、Blocking Rule 和复核方式。

### 10.2 评审策划与输入

RVR 从 `Planned` 进入 `Ready` 前必须固定：

- Review ID、Type、Purpose 和 Scope；
- 被评审 Asset ID、Revision、Snapshot/Baseline；
- 适用 Requirement、Policy、QGC 和 Criteria Revision；
- 必须 Evidence、实际 Evidence 和缺失项；
- Reviewer、Role、Competence 和 Independence；
- Review Method、Sample、Tool 和环境；
- Finding 分类、Blocking 和 Escalation；
- Start/End、时限和沟通方；
- 访问、敏感、保留和利益冲突；
- 接受 Reviewer 结果的 Authority。

输入发生变化时，RVR 必须返回 `Planned/Blocked` 或建立新 Attempt，不得继续使用旧 Scope 形成结论。

### 10.3 评审执行与 Finding

1. 每个检查项必须记录 Check Result、Evidence 和 Reviewer；
2. `Pass` 必须有可复核 Evidence；
3. `Fail` 必须形成 Finding ID、Severity、受影响对象、准则、实际事实、预期条件和 Owner；
4. `Blocked` 必须记录阻断来源、解除责任人和继续条件；
5. `Not Applicable` 必须记录理由、适用性 Authority 和范围；
6. `Not Evaluated` 必须保持缺口，不得计入通过率；
7. Sampling 必须记录 Population、Sample Method、Size、Coverage 和局限；
8. 工具结果必须固定 Tool/Rule/Query Version；
9. 推断的原因或影响必须标记为候选并等待验证；
10. 修改被评审对象时必须走其所属规范和 C11 Change，不得在 RVR 中直接覆盖。

### 10.4 评审结论与接受

1. `Review Conclusion = Conformant` 要求适用检查项无未处置 Fail；
2. `Conformant with Findings` 只允许无 Blocking Finding，且行动已分配；
3. `Nonconformant` 必须列出 Blocking/Critical/Major Finding 和返回路径；
4. `Inconclusive` 必须列出缺失 Evidence、Unknown 和重新评审条件；
5. RVR `Completed` 只表示评审动作结束；
6. RVR `Accepted` 必须由授权人类复核评审完整性；
7. RVR `Accepted` 不改变被评审对象 State；
8. RVR `Rejected` 表示评审结果不可接受，必须重做或纠正评审；
9. Finding 整改后必须记录新 Evidence 和复核结果；
10. 禁止删除已经修复的 Finding。

### 10.5 QGC 设计与版本

每个 QGC 必须定义：

- Gate Type/Profile；
- Applicable Scope 和对象类型；
- Check ID、Statement 和 Rationale；
- Required Input 和 Evidence；
- Evaluation Method；
- Pass/Fail/Blocked/N/A 判定规则；
- Blocking Level；
- Waivability；
- Condition Eligibility；
- Responsible Role 和 Approver；
- Required Reviewer Independence；
- Risk Escalation；
- Applicable Version、Effective、Review 和 Supersession；
- 自动检查与人工检查边界。

规则：

1. QGC 是检查标准，不记录特定 Gate 实例结果；
2. GTE 必须固定 QGC Revision；
3. Approved/Baselined QGC 变化必须走 C11；
4. 新 QGC 不得回写旧 Gate 的判定；
5. 规则冲突时执行更严格且有权的上位规则；
6. Non-waivable 项不得在实例中改为 Waivable；
7. 自动检查规则变化必须创建新 Revision 和回归验证。

### 10.6 Gate Instance 与决定

GTE 必须固定：

- Gate ID、Type/Profile 和 Parent Mandatory Gate；
- Object、Revision、Snapshot、Baseline 和 Scope；
- QGC Revision；
- RVR、Evidence 和 Metric Snapshot；
- Check Summary、Fail/Blocked/N/A/Unknown；
- EWR、RAR 和 Open Finding；
- Gate Outcome、DEC State、Rationale；
- Conditions、Owner、Due、Verification 和 Expiry；
- Approver、Authority、Decision Time；
- Effective Scope、Next State/Stage；
- Re-evaluation Trigger、Successor 和 History。

Gate 规则：

1. 未完成 RVR 或缺失 Required Evidence 时禁止 Pass；
2. Non-waivable Blocking Fail 存在时必须 Reject；
3. Conditional Pass 禁止承载未定义 Owner、期限或验证的条件；
4. Waive 必须引用有效 EWR，并披露未满足项；
5. RAR 不自动产生 Pass；
6. GTE 只批准特定对象 Revision 和 Scope；
7. GTE 不批准资产内容、不创建 Baseline、不执行 Release；
8. 输入 Revision、Scope、Risk、Evidence、Waiver 或 Condition 变化时必须重新评价；
9. 到期 GTE 进入 `Expired`，不得作为当前授权；
10. 后继 GTE 使用 `supersedes`，保留原决定。

### 10.7 Discovery Ready

最低输入：

- C01 Stakeholder Need、Evidence、Problem、Product Definition、Intent/Goal；
- Assumption Register；
- C10 Trace；
- C11 当前 Revision/Snapshot；
- 适用 Risk、Context 和相关方要求。

必须通过：

1. Need 具有来源、Stakeholder/用户群和情境；
2. Evidence 方法、范围、局限和可靠性明确；
3. Problem 与 Evidence、Need 的关系成立；
4. Product Definition、Intent 和 Goal 可区分；
5. 关键 Assumption 已登记并有验证计划；
6. 无来源、冲突和 Critical Unknown 已处置或阻断；
7. 气候变化及相关方气候要求已执行适用性判定。

强制阻断：

- 无来源 Need；
- 证据不可复核；
- Problem 与目标无成立关系；
- 高影响 Assumption 被隐藏；
- Agent 自行批准 Discovery Ready。

### 10.8 Specification Ready

最低输入：

- C02 Initiative、Scope、Risk、Constraint、Dependency、Metric Plan；
- C03 PRD、Feature、Scenario、Non-goal、Quality Attribute；
- C04 Requirement、Revision、Conflict；
- C05 Acceptance、Verification/Validation Plan；
- C06 UX/Technical Design、Coverage；
- C10 Trace/Coverage；
- C11 Baseline/Change。

必须通过：

1. Scope 与 Non-scope 明确且无未决冲突；
2. PRD/Feature 不扩大 Initiative Scope；
3. Requirement 原子、可理解、可验证且有来源；
4. 关键 Requirement 具有 Acceptance；
5. Quality Attribute 已完成九类 ISO/IEC 25010 适用性；
6. Design 覆盖 Requirement 和 Failure/State/Interface；
7. Critical Dependency、Risk、Unknown 和 Open Question 已处置；
8. Trace、Revision 和 Baseline 可解析。

Specification Ready 可以包含 Initiative Ready、PRD Ready、Requirement Ready 和 Design Ready 子 Gate，但禁止取消父 Gate 的完整性检查。

### 10.9 Agent Execution Ready

最低输入：

- C07 Collaboration Contract、Role、Approval Matrix、Authorization、Stop/Escalation；
- C08 Context Manifest、ECP、Freshness、Conflict、Fingerprint；
- C09 Execution Plan、Command/Tool Plan、Validation Plan；
- C05 Verification Plan；
- C06 Design；
- C11 Input Snapshot/Baseline。

必须通过：

1. 执行目标、Scope、Non-scope 和最大变化边界明确；
2. Agent Role、Accountability、Authority 和禁止动作明确；
3. Context Source、Priority、Freshness、Trust、Conflict 和 Fingerprint 合格；
4. 命令、工具、权限、环境和网络边界明确；
5. Validation、Rollback、Stop、Escalation 和人工复核可执行；
6. 无未处置 High/Critical Context Conflict 或权限冲突；
7. Agent 不承担自身高风险输出的 Approver。

### 10.10 Release Ready

最低输入：

- C05 Accepted Evidence、Coverage、Acceptance Decision；
- C09 Run、Actual Change、Validation、Failure、Human Review；
- C10 BTM/RCR/ALR/IQR、UCR/OAR；
- C11 BSL、CHG/CHD、RLC、Drift、Rollback/Recovery；
- 适用 E01 至 E05 Evidence；
- PHR 最新有效快照。

必须通过：

1. Critical Requirement Verification/Validation 完成；
2. Traceability 和 Coverage 达到 Approved Threshold；
3. 无未处置 Untracked Change、Critical Orphan 或 Release Blocking Finding；
4. 实际 Release Configuration 可重建且 Integrity Pass；
5. Migration、Rollback、Recovery、Monitoring 和 Notification 可执行；
6. 未解决 Risk 已处置或存在有效 RAR；
7. Waiver 有明确 Scope、补偿控制和到期；
8. Product Health 无未接受的 Critical Threshold Breach；
9. Release Authority 与 Implementer、Agent 满足职责分离。

构建成功、测试数量、Branch、Tag、BSL 或 RLC 任一单项均不足以形成 Release Ready。

### 10.11 Learning Closed

最低输入：

- C01/C02 Success Metric Observation；
- Release/Run/PHR；
- Feedback、Defect、Incident、Drift 和异常；
- RTR；
- IAP 或 No-action Rationale；
- 上游回流和 Trace。

必须通过：

1. 结果指标和护栏已在规定观察窗口内评价；
2. 计划与实际差异已记录；
3. Incident、Defect、Feedback 和失败已归档并关联；
4. 原因陈述有 Evidence 或明确标记为假设；
5. Learning 已回流 C01、C02、C04、C06、C11、C12 或适用扩展；
6. 需要 Action 时已创建 IAP Member；
7. 无需 Action 时有依据、Approver 和复评触发；
8. 未完成长期 Action 不必全部 Closed，但必须有 Owner、期限、Risk 和跟踪 Gate。

### 10.12 Conditional Pass

Conditional Pass 只在以下条件同时满足时允许：

1. 无 Non-waivable Blocking Fail；
2. 未满足项不会立即破坏目标阶段的最低安全与合法性；
3. Condition 可验证且具有明确 Owner；
4. Due/Expiry 在风险暴露窗口之前；
5. 临时补偿控制已实施；
6. 失败时 Stop、Rollback 或撤销路径明确；
7. GTE 记录受影响 Scope 和下游限制。

条件完成后必须形成复核 Evidence 和后继 GTE，禁止直接删除 Condition。到期未满足时，GTE 进入 `Expired`，相关下游活动必须停止、隔离或升级。

### 10.13 Exception 与 Waiver

EWR 必须记录：

- 被偏离的 Rule/Gate Item 和 Revision；
- Scope、Object、Environment 和时间；
- Reason、Alternative 和不批准后果；
- Risk、影响、受影响方；
- Compensating Controls；
- Owner、Approver/Authority；
- Effective、Expiry；
- Monitoring、Review Frequency；
- Revocation、Re-evaluation 和 Exit Conditions；
- 关联 GTE、RAR、CHG 和 Evidence。

规则：

1. EWR 禁止无期限；
2. Expiry 必须是时间点或确定可判定事件；
3. `Waived` 不表示要求满足；
4. Non-waivable 规则禁止普通 EWR；
5. 多项偏离必须逐项记录或提供可独立审计成员；
6. Scope 扩大必须建立新 EWR；
7. 控制失效、Risk 增加、法律变化或条件消失时立即复评或撤销；
8. 到期 EWR 禁止作为当前 Gate 输入；
9. 重复 Waiver 必须触发规则、资源、设计或流程根因评审；
10. Agent 可以起草，禁止批准。

### 10.14 Risk Acceptance

RAR 必须记录：

- Risk ID 和权威 Risk Source；
- Affected Scope、Asset、Environment、Stakeholder 和期限；
- Inherent/Current Risk；
- Current Controls 和 Evidence；
- Residual Risk 与评价准则；
- Acceptance Reason 和 Alternatives；
- Risk Owner；
- Acceptance Authority；
- Monitoring Metric、Threshold 和 Frequency；
- Review、Expiry、Revocation 和 Escalation；
- 关联 GTE、EWR、CHG、PHR 和 Incident。

规则：

1. 接受前必须完成适用 Risk Assessment 和 Treatment；
2. RAR 不改变 Risk Register 的事实值；
3. RAR 不把 Fail 改为 Pass；
4. RAR 不豁免法律、监管或合同禁止项；
5. Acceptance Authority 必须对影响范围负责；
6. 无监控能力的 High/Critical Residual Risk 禁止接受；
7. Threshold Breach、控制失效、Scope 变化、Incident 或到期必须复评；
8. RAR 到期后 Gate 必须重新决定；
9. 一个 RAR 禁止被无界复用于多个产品、环境或 Release；
10. Agent 禁止作 Risk Acceptance。

### 10.15 Metric Definition

每项 Metric 必须定义：

- Metric ID、Name、Purpose、Owner；
- Domain 和 Health Question；
- Scope、Population、Unit；
- Numerator、Denominator、Formula；
- Inclusion、Exclusion、Missing Data；
- Source、Authority、Query/Method、Revision；
- Collection Time、Period、Timezone；
- Baseline、Target、Threshold、Direction；
- Segmentation 和 Aggregation；
- Data Quality Check；
- Threshold Result 和 Trend Rule；
- Limitation、Interpretation 和 Misuse Warning；
- Definition Revision、Effective 和 Supersession。

Metric Definition 必须在报告周期前 Approved/Baselined。临时分析可以作为 Draft，但不得进入正式 PHR 或 Gate。

### 10.16 Product Health Report

PHR 必须：

1. 固定报告范围、周期、Metric Definition Revision 和 Data Snapshot；
2. 展示每项 Metric Current Value、Threshold Result、Trend 和 Data Status；
3. 展示分子、分母、Exclusion、Unknown 和异常；
4. 展示 Requirement、Agent、Engineering、Process 四个最低域；
5. 对九个 ISO/IEC 25010 产品质量特性执行适用性判定；
6. 对 AI 产品/Agent 展示适用 AI Risk、Impact 和性能评价；
7. 展示 Threshold Breach、Risk、Waiver、RAR、Incident 和 Finding；
8. 给出 Health Conclusion、依据和局限；
9. 为异常分配 Action、Owner 和 Due；
10. 与上一可比周期解释 Trend；
11. 定义不同比较口径时禁止直接合并趋势；
12. `Approved` 只表示报告正确，不表示 Health Conclusion 为 Healthy。

### 10.17 需求健康指标

| Metric ID | 指标 | 最低计算规则 |
|---|---|---|
| RH-001 | 无来源需求数 | 在固定 Requirement Population 中，缺少有效上游 Source Link 的 Requirement 数 |
| RH-002 | 无验收需求数 | 适用且要求 Acceptance 的 Requirement 中，缺少有效 Acceptance Reference 的数量 |
| RH-003 | 重复或冲突需求数 | 当前 Open/In Progress/Blocked 的 Confirmed Duplicate 或 Conflict Case 去重数量 |
| RH-004 | 长期未维护需求数 | 超过 Approved Review Age Threshold 且仍在有效 Scope、未完成复核的 Requirement 数 |
| RH-005 | 需求到发布追踪覆盖率 | 具有有效 Source→Requirement→Design/Implementation→Verification→Release 链的适用 Requirement 数 ÷ 适用 Requirement 总数 × 100% |

RH-005 必须单独展示 `Unknown`、`Not Applicable` 和 Critical Requirement Coverage，禁止只报总体百分比。

### 10.18 Agent 健康指标

| Metric ID | 指标 | 最低计算规则 |
|---|---|---|
| AH-001 | 无来源修改数 | 周期内 C10 UCR 确认的无有效 Requirement/Decision/Change/Incident 来源的实际修改数量 |
| AH-002 | 范围违规数 | Actual Change 超出 C07/C09 授权 Scope 的已确认 Run 数 |
| AH-003 | 上下文冲突数 | 周期内新发现或仍未解决的 C08 Context Conflict 数，按 Conflict ID 去重 |
| AH-004 | 执行失败率 | `Failed` Eligible Run 数 ÷ 具有 Completed/Failed 技术结果的 Eligible Run 总数 × 100% |
| AH-005 | 返工率 | 在 Approved Rework Window 内因前次不合格输出产生后继修正 Run/CHG 的 Accepted Change Unit 数 ÷ Accepted Change Unit 总数 × 100% |
| AH-006 | 未经复核的高风险 Agent 输出数 | 被消费、合并、基线化或发布前缺少 Accepted Human/Independent Review 的 High/Critical Agent Output 数 |

Cancelled、Blocked 和重复 Attempt 的纳入规则必须在 Metric Definition 中明确，禁止为降低失败率静默排除。

### 10.19 工程与过程健康指标

#### 工程健康

| Metric ID | 指标 | 最低计算规则 |
|---|---|---|
| EH-001 | 重复模块数 | 经批准检测规则识别并经 Review 确认的活跃重复模块/资产组数 |
| EH-002 | 孤立代码数 | 缺少有效 Requirement、Design、Change、Incident 或其他授权来源的生产代码资产数 |
| EH-003 | 未解决架构决策数 | 适用范围内仍为 Proposed/Under Review 或被 Blocked Finding 约束的必需架构 Decision 数 |
| EH-004 | 技术债趋势 | 使用固定权重和 Population 的 Open Technical Debt Exposure 相对前一可比周期的方向与老化分布 |
| EH-005 | 发布与回滚缺陷 | 分别展示 Release Defect Count、Rollback Failure Count 和受影响 Release；禁止只合并成单一数值 |

#### 过程健康

| Metric ID | 指标 | 最低计算规则 |
|---|---|---|
| PH-001 | 门禁豁免率 | 周期内 `Waived` GTE 数 ÷ 已作最终 Outcome 的 GTE 总数 × 100% |
| PH-002 | 变更周期 | 每个 Closed CHG 的 `Closed Time - Open Time`；报告中位数、分位数、异常值和 Blocked Time |
| PH-003 | 基线后返工率 | Approved Baseline 后被确认属于 Rework 的 CHG 数 ÷ 同范围 Baseline 后 CHG 总数 × 100% |
| PH-004 | 验证失败率 | Failed Verification Execution 数 ÷ 具有 Passed/Failed 技术结果的 Eligible Verification 总数 × 100% |
| PH-005 | 改进行动关闭率 | 周期内到期且具有关闭 Evidence 的 Closed Action 数 ÷ 周期内应到期 Action 总数 × 100% |

PH-005 必须同时报告 Overdue、Reopened 和无 Evidence 关闭数。

### 10.20 Threshold、Trend 与数据质量

1. 每项 Metric 必须有 Direction：Higher is Better、Lower is Better、Range 或 Informational；
2. Threshold 必须记录依据、Authority、有效范围和 Revision；
3. `Near` 区间必须由 Metric Definition 明确定义，禁止临时报喜；
4. Trend 只在 Definition、Scope、Population、Period 和 Source 可比时计算；
5. 不可比时使用 `Insufficient Data`，禁止拼接；
6. Data Status 为 `Partial/Unavailable/Unreliable` 时，Health Conclusion 不得默认为 Healthy；
7. Critical Segment Breach 禁止被总体平均抵消；
8. Threshold 调整必须走 C11 Change 并解释对历史可比性的影响；
9. 预测值与实际值必须分开；
10. Agent 生成 Trend Interpretation 必须经人工复核。

### 10.21 指标防操纵

禁止：

- 删除失败、Finding、Waiver、Defect、Run 或 Action 改善指标；
- 将一个对象拆分或合并以改变分母而不披露；
- 将 High Risk 降级以减少复核项；
- 延迟登记跨过报告周期；
- 只选有利时间窗、环境、团队或 Segment；
- 将 Unknown、Not Evaluated、Unavailable 计为 Pass 或零；
- 修改历史 Metric Definition 后回写旧周期；
- 以平均值隐藏尾部、Critical 或少数群体影响；
- 以 Action Created 代替 Action Effective；
- 以输出数量、代码行数、测试数量或 Agent 运行次数替代结果健康。

PHR 必须包含 Anti-gaming Check。发现操纵时必须建立 Finding、纠正 Action，并按严重度触发 Gate Re-evaluation。

### 10.22 Retrospective

RTR 必须固定：

- 回顾 Scope、Period、Release/Run/Incident；
- 目标、Success Metric 和预期结果；
- 实际结果、Timeline 和 Evidence；
- 成功、偏差、失败、Incident 和 Feedback；
- 直接原因、贡献因素、系统条件和 Unknown；
- 已验证 Learning 与待验证假设；
- 受影响 Requirement、Design、Process、Tool、Context 和 Decision；
- 保留、修正、停止、替代或实验 Decision；
- Improvement Action 或 No-action Rationale；
- Participant、Facilitator、时间和独立复核。

规则：

1. RTR 必须基于事实，不以个人归责代替原因分析；
2. 时间线必须区分已知事实、推断和决定；
3. 没有改进行动时必须记录依据、Approver 和复评触发；
4. 重复 Finding、Waiver、Incident 或失败必须执行更深层原因分析；
5. RTR `Completed` 不等于 Learning 已接受；
6. RTR `Accepted` 后 Learning 才可作为正式改进输入；
7. Learning 必须回流相关上游资产或明确不影响理由。

### 10.23 Improvement Action

IAP 每个 Action Member 必须：

- 有永久 Action ID；
- 引用 Finding、Learning、Risk、Incident 或 PHR；
- 定义 Problem/Opportunity、Target Outcome 和 Action；
- 有 Priority、Owner、Due、Dependency；
- 有 Success Condition、Measure、Baseline 和 Verification；
- 使用 Action Member Status；
- 有 Blocked Reason、Escalation 和变更历史；
- 关闭时有 Evidence、Reviewer 和 Effective Result；
- 未达到效果时 Reopened 或建立后继 Action。

规则：

1. IAP DOC State 与 Action Member Status 分离；
2. `Resolved` 表示行动完成等待效果复核；
3. `Closed` 必须有 Success Condition Evidence；
4. 仅完成任务不证明结果改善；
5. 到期未完成必须进入 PHR 和适用 Gate；
6. 取消必须记录理由、Risk 和 Authority；
7. Agent 可以更新执行事实，不得关闭自身高风险 Action；
8. Action 改变 Approved/Baselined 资产时必须进入 C11 CHG。

### 10.24 审核、管理评审与纠正

1. Internal Audit 使用 RVR，Review Type=`Internal Audit`；
2. Management Review 使用 RVR，必须消费 PHR、Gate、Waiver、RAR、Finding、Incident 和 IAP；
3. Audit Scope、Criteria、Sample、Independence 和 Finding 必须可复核；
4. Nonconformity 必须控制当前影响、分析原因、识别类似问题、执行纠正并验证有效性；
5. Corrective Action 可以进入 IAP，但必须标记其来源和强制性；
6. 重复 Nonconformity 禁止只延长 Due；
7. 审核结果禁止由被审核 Agent 自动接受；
8. Audit/Management Review 不建立新的 C12 正式产物类型。

### 10.25 Coding Agent 与自动化边界

Agent 可以：

- 组装固定 Gate 输入；
- 执行确定性检查和 Metric Query；
- 起草 RVR、GTE、EWR、RAR、PHR、RTR 和 IAP；
- 识别缺失 Evidence、Finding、Threshold Breach、Trend 和 Anti-gaming 信号；
- 在授权下更新 Action 执行事实；
- 提出 Gate Outcome、Waiver、Risk 和 Improvement 候选。

Agent 禁止：

- 将自身输出直接标为 RVR/RTR `Accepted`；
- 作 GTE、EWR、RAR 的最终决定；
- 自行降低 Finding Severity、Risk 或 Blocking Level；
- 将 Unknown/Not Evaluated 转成 Pass；
- 修改 Metric Definition、Threshold 或 Population 以优化结果；
- 删除或隐藏失败、Waiver、Condition、Reopened 和 Expired 历史；
- 在无 Evidence 时宣称 Root Cause、Health 或 Improvement Effective；
- 作为自身高风险输出的 Independent Reviewer；
- 因自动检查通过而修改上游资产 State、Baseline 或 Release 状态。

## 11. 受控状态

### 11.1 EXEC State：RVR、RTR

```text
Planned → Ready → Running → Completed → Accepted/Rejected
                    ↕ Blocked
                    → Failed/Cancelled
```

规则：

1. `Ready` 表示对象、输入、准则、角色和授权完整；
2. `Completed` 表示评审/回顾动作结束，等待结果接受；
3. `Accepted` 必须由授权人类决定；
4. `Rejected` 表示执行结果不可作为正式输入；
5. `Failed` 表示执行本身未达到完成条件；
6. `Blocked` 必须记录解除条件；
7. `Cancelled` 保留原因和已产生事实。

### 11.2 DOC State：QGC、PHR、IAP

```text
Draft → In Review → Approved → Baselined
                 ↘ Changes Required → Draft
                 ↘ Rejected
Approved/Baselined → Superseded → Retired
```

规则：

1. Approved QGC 才可用于正式 Gate；
2. Approved PHR 表示报告内容接受，不表示健康为绿；
3. Approved IAP 表示计划获批，不表示 Action 已完成；
4. Baselined 内容变化必须走 C11；
5. Superseded/Retired 历史永久保留。

### 11.3 DEC State：GTE、EWR、RAR

```text
Proposed → Under Review → Approved
                       ↘ Conditionally Approved
                       ↘ Rejected
                       ↘ Waived
Approved/Conditionally Approved/Waived → Superseded/Expired
```

规则：

1. GTE 使用第 5.3 节 Outcome 映射；
2. EWR/RAR 通常使用 Approved、Conditionally Approved、Rejected、Superseded、Expired；
3. EWR `Waived` 表示偏离请求获准；仍必须有 Scope 和 Expiry；
4. RAR 禁止使用 `Waived` 表示风险接受；
5. `Conditionally Approved/Waived` 必须有 Owner、条件、期限和复核；
6. `Expired` 禁止作为当前输入；
7. Agent 禁止写入最终 DEC State。

## 12. 必需产物

| 产物 | 创建触发 | 进入正式使用条件 | 退出当前有效集合 |
|---|---|---|---|
| RVR | 任一正式 Review/Audit/Gate Review | Accepted；对象、准则、Evidence、Finding 和复核完整 | 被后继评审替代或对象变化 |
| QGC | 新 Gate Type/Profile 或规则变化 | Approved；检查、判定、Evidence、阻断和例外明确 | Superseded/Retired |
| GTE | 特定对象请求进入下一状态/阶段 | Approved/Conditionally Approved/Waived；Authority 和边界完整 | Superseded/Expired |
| EWR | 请求偏离可豁免规则/Gate Item | Approved/Conditionally Approved/Waived；补偿控制和到期完整 | Superseded/Expired/撤销 |
| RAR | 请求接受 Residual Risk | Approved/Conditionally Approved；监控和到期完整 | Superseded/Expired/撤销 |
| PHR | 到达报告周期或重大健康事件 | Approved；Metric、Source、Threshold、Trend 和行动完整 | 下一周期 Superseded |
| RTR | Release、Incident、重大失败、周期回顾或 Learning Closed | Accepted；事实、Learning、Decision/Action 完整 | 后继回顾或范围变化 |
| IAP | Finding/Learning/Risk 需要改进 | Approved；Action、Owner、Due、Success 条件完整 | 全部 Action 关闭后 Superseded/Retired |

八类产物不得合并为一个正式实例。P2 工具可以统一展示，但必须保留类型代码和状态边界。

## 13. 产物必填信息

八类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C12 类型专属要求。

### 13.1 RVR — Review Record

必须包含：

- Review ID、Type、Purpose；
- Object ID、Revision、Snapshot/Baseline；
- Review Scope 和 Period；
- Review Input、Evidence 和缺失项；
- Reviewer、Role、Competence、Independence；
- Criteria/QGC Revision；
- Method、Sample、Tool/Rule Version；
- Check Result；
- Finding ID、Severity、Blocking、Evidence；
- Review Conclusion；
- Remediation Action、Owner、Due；
- Re-review Result；
- Start/End/Accepted Time；
- Acceptance Authority；
- Related GTE/CHG/IAP。

### 13.2 QGC — Quality Gate Checklist

必须包含：

- QGC ID、Gate Type/Profile、Parent Mandatory Gate；
- Purpose、Scope、Applicable Object/Version；
- Check ID、Statement、Rationale；
- Required Input/Evidence；
- Evaluation Method；
- Pass/Fail/Blocked/N/A Rule；
- Blocking Level、Waivability、Condition Eligibility；
- Responsible Role、Reviewer Independence；
- Escalation 和 Risk Rule；
- Automatic/Human Boundary；
- Owner、Approver、Revision、Effective；
- Review Frequency、Supersession。

### 13.3 GTE — Gate Decision

必须包含：

- Gate Decision ID；
- Gate Type/Profile、Parent Mandatory Gate；
- Object、Revision、Snapshot/Baseline、Scope；
- QGC Revision；
- RVR 和 Evidence；
- Check Summary、Unmet Items、Finding；
- Risk、Unknown；
- EWR、RAR；
- Gate Outcome、DEC State、Rationale；
- Conditions、Owner、Due、Verification；
- Approver/Authority；
- Decision/Effective/Expiry；
- Next State/Stage；
- Re-evaluation Trigger；
- Supersedes/History。

### 13.4 EWR — Exception or Waiver Record

必须包含：

- EWR ID；
- Deviated Rule/Gate Item 和 Revision；
- Waivability；
- Scope、Object、Environment；
- Reason、Alternative、Impact；
- Risk；
- Compensating Controls 和 Evidence；
- Owner；
- Approver/Authority；
- DEC State；
- Effective、Expiry；
- Monitoring、Review；
- Revocation/Re-evaluation/Exit；
- Related GTE/RAR/CHG；
- Supersession/History。

### 13.5 RAR — Risk Acceptance Record

必须包含：

- RAR ID；
- Risk ID 和 Source；
- Affected Scope/Asset/Environment/Stakeholder；
- Inherent/Current Risk；
- Current Controls 和 Evidence；
- Residual Risk 和 Criteria；
- Acceptance Reason、Alternative；
- Risk Owner；
- Acceptance Authority；
- DEC State；
- Monitoring Metric/Threshold/Frequency；
- Review/Effective/Expiry；
- Revocation/Escalation；
- Related GTE/EWR/PHR/Incident；
- Supersession/History。

### 13.6 PHR — Product Health Report

必须包含：

- PHR ID、Scope、Period；
- Metric Definition Revision；
- Data Source/Snapshot/Query；
- Metric ID、Formula、Numerator/Denominator；
- Threshold/Target/Direction；
- Current Value、Threshold Result、Trend；
- Data Status、Unknown、Limitation；
- Segment 和异常；
- Requirement/Agent/Engineering/Process Health；
- ISO/IEC 25010 九类适用性；
- AI Health/Risk/Impact 适用性；
- Health Conclusion 和 Rationale；
- Risk、Finding、Waiver、RAR；
- Action、Owner、Due；
- Report Owner、Reviewer、Approver；
- Previous PHR、Comparability、History。

### 13.7 RTR — Retrospective Record

必须包含：

- RTR ID、Type、Scope、Period；
- Participants、Facilitator、Independence；
- Goal/Expected Result/Metric；
- Actual Result、Timeline、Evidence；
- Success、Deviation、Failure、Incident、Feedback；
- Direct Cause、Contributing Factor、System Condition；
- Unknown、Assumption；
- Learning；
- Affected Asset/Decision/Process；
- Decision；
- Improvement Action 或 No-action Rationale；
- Owner、Due；
- Start/End/Accepted Time；
- Acceptance Authority；
- Trace 和 History。

### 13.8 IAP — Improvement Action Plan

必须包含：

- IAP ID、Purpose、Scope、Revision、DOC State；
- Source Finding/Learning/Risk/Incident/PHR；
- Action ID；
- Problem/Opportunity；
- Target Outcome；
- Action Content；
- Priority；
- Owner；
- Start/Due；
- Success Condition/Measure/Baseline/Target；
- Dependency；
- Action Member Status；
- Blocked/Escalation；
- Closure Evidence；
- Effectiveness Reviewer/Result；
- Reopened/Successor；
- Related CHG/GTE/RTR；
- History。

## 14. 质量准则

### 14.1 Review 质量

- 100% 正式 Review 固定对象 Revision 和 Criteria Revision；
- 100% Fail 有 Finding ID 和 Evidence；
- 100% N/A 有理由和 Authority；
- 0 个高风险输出由生成 Agent 自我接受；
- Finding、整改和复核历史完整；
- RVR Accepted 不改写对象 State。

### 14.2 Gate 质量

- 五个强制 Gate 均有 Approved QGC；
- 每个 GTE 固定对象、Scope、QGC、RVR 和 Evidence；
- Pass 时 Non-waivable Blocking Fail 为 0；
- Conditional Pass 的条件 100% 有 Owner、Due、Verification 和 Expiry；
- Waive 的未满足项 100% 有有效 EWR；
- 到期/输入变化 Gate 不被继续使用。

### 14.3 Waiver 与 Risk Acceptance 质量

- 无永久 EWR；
- Non-waivable 项豁免数为 0；
- EWR 的 Scope、Risk、补偿控制和撤销完整；
- RAR 的 Residual Risk、Authority、监控和到期完整；
- EWR/RAR 不改变 Requirement、Evidence、Risk 或 Check Result；
- 重复 Waiver 进入原因分析和改进。

### 14.4 Health 质量

- 21 项最低指标全部定义或有批准的 N/A；
- 每项 Metric 可重放 Source/Query/Formula；
- Numerator、Denominator、Exclusion、Unknown 可见；
- Threshold、Trend 和 Data Status 可解释；
- Critical Segment 不被总体值掩盖；
- Definition 变化不回写历史；
- PHR Approval 与 Health Conclusion 分离。

### 14.5 Learning 与 Improvement 质量

- 每次强制 RTR 形成 Learning 或 No-action Rationale；
- 每项 Action 有 Owner、Due、Success Condition；
- Action Closed 有 Effectiveness Evidence；
- Reopened、Cancelled 和 Overdue 不被隐藏；
- Learning 回流相关上游资产；
- 改进以结果变化验证，不以任务完成数量验证。

## 15. 验证与符合性检查

### 15.1 Discovery Ready 检查

- [ ] C01 必需资产 Revision 固定；
- [ ] Need、Evidence、Problem、Intent Trace 成立；
- [ ] Evidence 方法、局限、可靠性完整；
- [ ] Assumption、Unknown、Risk 披露；
- [ ] Climate relevance 与相关方要求已判定；
- [ ] Blocking Finding 为 0 或 Gate Reject。

### 15.2 Specification Ready 检查

- [ ] Scope/Non-scope 无冲突；
- [ ] PRD/Feature/Requirement 完整；
- [ ] Critical Requirement 有 Acceptance；
- [ ] Verification/Validation Plan 完整；
- [ ] UX/Design/Interface/Failure 覆盖；
- [ ] 九类产品质量适用性完成；
- [ ] Risk/Dependency/Unknown 受控；
- [ ] Trace/Baseline 可解析。

### 15.3 Agent Execution Ready 检查

- [ ] C07 Authority 和禁止边界完整；
- [ ] C08 Context/Freshness/Conflict/Fingerprint 合格；
- [ ] C09 Plan/Command/Tool/Scope 完整；
- [ ] Input Snapshot Integrity Pass；
- [ ] Verification、Stop、Escalation、Rollback 完整；
- [ ] 高风险 Agent 输出有独立 Review 计划；
- [ ] Agent 未被列为最终 Approver。

### 15.4 Release Ready 检查

- [ ] Verification/Validation Evidence Accepted；
- [ ] Trace/Coverage 达标；
- [ ] UCR/OAR/Drift 处置；
- [ ] RLC 可重建且 Integrity Pass；
- [ ] Migration/Rollback/Monitoring 就绪；
- [ ] Open Risk 有有效 RAR；
- [ ] Waiver 未过期；
- [ ] Critical Health Breach 已阻断或有权处置；
- [ ] Release Authority 独立。

### 15.5 Learning Closed 检查

- [ ] 结果指标和护栏已观察；
- [ ] 偏差、Incident、Defect、Feedback 已归档；
- [ ] RTR Accepted；
- [ ] Learning 已回流；
- [ ] IAP 已创建或 No-action Rationale 获批；
- [ ] Action Owner/Due/Success 完整；
- [ ] 未关闭长期 Action 有跟踪和 Risk。

### 15.6 强制阻断

出现以下任一情形必须 Reject 或 Block Gate：

1. 对象、Revision、Scope 或 QGC 无法解析；
2. Required Evidence 缺失或失效；
3. Non-waivable Blocking Fail；
4. Agent 自批、自验或越权；
5. High/Critical Risk 无有权处置；
6. EWR 无 Scope、Risk、补偿控制或 Expiry；
7. RAR 无 Residual Risk、监控或 Authority；
8. Conditional Pass 无 Owner、Due、Verification 或 Expiry；
9. Input Baseline/Snapshot Integrity Fail；
10. Critical Requirement 无 Acceptance/Verification；
11. Release 存在 UCR、不可重建配置或关键 Drift；
12. Metric Source/Formula/Population 不可复核；
13. Unknown 被计为 Pass/零；
14. 发现指标操纵；
15. Learning Closed 无观察、Learning 或行动依据；
16. 法律、监管、合同、Safety、Security、Privacy 禁止项被豁免。

### 15.7 P2 强制检查

| 检查编号 | 检查项 | 通过条件 |
|---|---|---|
| C12-P2-001 | 八类产物独立 | 类型、身份、状态可区分 |
| C12-P2-002 | 公共状态合规 | 无平行 State |
| C12-P2-003 | Outcome/State 分离 | 映射正确 |
| C12-P2-004 | RVR 对象固定 | ID/Revision/Snapshot 完整 |
| C12-P2-005 | Review Criteria 固定 | QGC/规则 Revision 完整 |
| C12-P2-006 | Reviewer 明确 | Role/Competence/Independence 完整 |
| C12-P2-007 | Finding 有 Evidence | 无空结论 |
| C12-P2-008 | N/A 受控 | 理由和 Authority 完整 |
| C12-P2-009 | RVR Accepted 有人类授权 | Agent 未自批 |
| C12-P2-010 | QGC Approved | 正式 Gate 使用有效版本 |
| C12-P2-011 | Check 判定完整 | Pass/Fail/Blocked/N/A 明确 |
| C12-P2-012 | Blocking Level 完整 | 每项均定义 |
| C12-P2-013 | Waivability 完整 | Non-waivable 未降级 |
| C12-P2-014 | GTE 输入固定 | Object/QGC/RVR/Evidence 完整 |
| C12-P2-015 | Gate Outcome 合规 | 四种受控值 |
| C12-P2-016 | GTE State 合规 | DEC 映射正确 |
| C12-P2-017 | Pass 无 Blocker | Non-waivable Fail 为 0 |
| C12-P2-018 | Conditional Pass 有边界 | 条件/Owner/Due/验证/到期完整 |
| C12-P2-019 | Waive 有 EWR | 所有偏离可追 |
| C12-P2-020 | Reject 保留理由 | 未删除失败 |
| C12-P2-021 | Discovery Ready | 最低输入与条件完整 |
| C12-P2-022 | Specification Ready | 最低输入与条件完整 |
| C12-P2-023 | Agent Execution Ready | 最低输入与条件完整 |
| C12-P2-024 | Release Ready | 最低输入与条件完整 |
| C12-P2-025 | Learning Closed | 最低输入与条件完整 |
| C12-P2-026 | 领域 Gate 映射 | Parent Mandatory Gate 明确 |
| C12-P2-027 | Gate 输入变化复评 | 无旧决定沿用 |
| C12-P2-028 | EWR 无永久项 | 100% 有 Expiry |
| C12-P2-029 | EWR Scope 明确 | 无跨产品/环境复用 |
| C12-P2-030 | 补偿控制有效 | 有 Evidence |
| C12-P2-031 | Non-waivable 未豁免 | 数量为 0 |
| C12-P2-032 | 重复 Waiver 复盘 | 有 RTR/IAP |
| C12-P2-033 | RAR 引用权威 Risk | 无平行 Risk |
| C12-P2-034 | Residual Risk 明确 | Criteria/Evidence 完整 |
| C12-P2-035 | RAR Authority 有效 | Agent 不担任 |
| C12-P2-036 | RAR 监控完整 | Metric/Threshold/Frequency |
| C12-P2-037 | RAR 未改写事实 | Risk/Evidence/Gate 保持 |
| C12-P2-038 | 21 项最低指标 | 全部定义或批准 N/A |
| C12-P2-039 | Metric Formula 完整 | 分子/分母/单位 |
| C12-P2-040 | Source 可重放 | Query/Revision/Snapshot |
| C12-P2-041 | Threshold 受控 | Authority/Revision 完整 |
| C12-P2-042 | Trend 可比 | 不可比时 Insufficient Data |
| C12-P2-043 | Unknown 显式 | 未计为绿色 |
| C12-P2-044 | Critical Segment 可见 | 未被平均掩盖 |
| C12-P2-045 | PHR Approval 分离 | 不等于 Healthy |
| C12-P2-046 | 九类产品质量适用性 | 全部判定 |
| C12-P2-047 | Agent Health 完整 | 六项最低指标 |
| C12-P2-048 | Anti-gaming 检查 | 无删除/拆分/分母操纵 |
| C12-P2-049 | 历史定义不回写 | Definition Revision 可追 |
| C12-P2-050 | RTR 事实完整 | 目标/实际/Timeline/Evidence |
| C12-P2-051 | 原因与假设分离 | 无虚构根因 |
| C12-P2-052 | Learning 可追 | 回流上游 |
| C12-P2-053 | No-action 有依据 | Approver/复评触发完整 |
| C12-P2-054 | IAP Action 完整 | Owner/Due/Success/依赖 |
| C12-P2-055 | Action State 分离 | Member Status 不冒充 DOC |
| C12-P2-056 | Action 关闭有 Evidence | 效果已验证 |
| C12-P2-057 | Overdue/Reopened 可见 | 未隐藏 |
| C12-P2-058 | E04 元数据完整 | Access/Retention/History |
| C12-P2-059 | 扩展适用性复评 | E01/E02/E03/E05 触发已检查 |
| C12-P2-060 | 标准映射完整 | 六项 R1 均映射 |

任何 `Fail` 必须形成 Finding、Owner、Due 和阻断结论，禁止只给总分。

## 16. 追踪、记录与变更要求

### 16.1 追踪

每个 C12 产物必须至少追到：

- Source Asset/Rule/Risk/Learning；
- Object Revision/Snapshot/Baseline；
- QGC/Metric Definition Revision；
- Review/Query/Run/Evidence；
- Decision/Authority；
- Change/Release/Incident；
- Downstream State/Stage/Action；
- Supersession/Expiry/Correction。

GTE 必须支持从 Gate 反查所有检查和 Evidence，也必须支持从任一 Blocking Finding 反查受影响 Gate。

### 16.2 状态转换记录

每次状态转换必须记录：

- Asset ID；
- Original State；
- New State；
- Actor；
- Authority；
- Timestamp；
- Revision；
- Rationale；
- Evidence；
- Condition/Expiry；
- Supersession/Correction。

### 16.3 更正与历史

1. EXEC/DOC/DEC 对象的事实错误必须通过新 Revision、更正事件或后继记录处理；
2. 禁止删除 Rejected、Waived、Expired、Cancelled、Failed 和 Reopened 历史；
3. 指标数据更正必须保留原值、错误原因、更正值、影响周期和 Reviewer；
4. Gate 输入错误时必须使原 GTE Superseded/Expired 并建立新 GTE；
5. EWR/RAR 更正不得扩大原授权；
6. RTR 原因假设被反证时必须更新 Learning 并影响 IAP。

### 16.4 保留与访问

E04 当前激活。C12 必须记录：

- Access Classification；
- Retention Rule；
- Legal/Contract Hold；
- Sensitive/Personal/Secret Boundary；
- Authoritative Location；
- Format/Tool/Query Version；
- Integrity；
- Archive/Recovery；
- Disposition Authority。

正式 Gate、Waiver、Risk Acceptance、Release Review、Metric Source 和 Audit Record 禁止无痕删除。

### 16.5 重新评价触发

以下变化必须重新评审适用 GTE、EWR、RAR 或 PHR：

- Object Revision、Scope、Baseline、Release 或环境变化；
- Requirement、Evidence、Risk、Dependency 或 Context 变化；
- QGC、Metric Definition、Threshold 或 Source 变化；
- Condition、Waiver、Risk Acceptance 到期或控制失效；
- Incident、Defect、Drift、UCR、Threshold Breach；
- 标准、法律、合同或相关方要求变化；
- E01 至 E05 激活状态变化；
- ISO 9001 新版正式替代当前引用。

## 17. P2 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C12 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

每个任务只执行其生命周期位置、Risk、Change Surfaces 和 Release Scope 实际触发的 Gate。QGC 可以从稳定 Baseline `Reference`；RVR、GTE、RTR 按实际评审/Gate/回顾事件创建；PHR 只在产品健康周期或发布观察需要时 `Generate`。

EXA、EWR、RRS、RAR 边界固定：EXA 是 Agent 权限例外，EWR 是规范/Gate 豁免，RRS 是剩余风险陈述，RAR 是具有人类 Authority 的风险接受。Agent 不得把自动检查通过写成 Human Acceptance 或 Gate Approval。

### 17.1 P2 必须保留

P2 必须：

- 保留 8 类正式产物；
- 保留 5 个强制生命周期 Gate；
- 保留 QGC、RVR、GTE 的事实源分离；
- 保留 EWR 和 RAR；
- 保留 21 项最低健康指标；
- 保留 RTR 与 IAP；
- 保留公共状态、Authority、独立性和 Agent 自批禁止；
- 保留第 15.7 节 60 项检查；
- 保留 E04 记录接口和五个扩展适用性接口。

P2 可以：

- 在一个工具中承载多类产物；
- 自动生成检查、Metric、PHR 和候选 Decision；
- 将领域 Ready 作为强制 Gate 的子 Gate；
- 对 Low Risk 重复 Review 使用批准的 Sampling 和自动化；
- 对多个产品共享 QGC/Metric Definition，但实例必须固定适用 Scope 和 Revision。

P2 禁止：

- 使用 P1 `Review & Health Log` 代替正式产物；
- 取消任一强制 Gate；
- 取消业务 ID、Evidence、Decision、Expiry、History；
- 将 Agent 自动检查直接写为 Gate Pass；
- 取消 Core Health Metric 或以无数据声明 N/A；
- 用永久 Waiver 替代规则修正。

### 17.2 P1 兼容边界

P1 可以使用统一 `Review & Health Log` 作为物理载体，但：

- 八类逻辑对象仍需可识别；
- 五个 Gate 不得取消；
- EWR、RAR 和核心健康指标不得取消；
- Gate Decision、Authority、Expiry 和历史不得合并丢失。

本项目采用 P2，禁止实施 P1 合并。

## 18. 扩展接口与上下游交接

### 18.1 C01 至 C11

| 来源 | C12 接收 | C12 输出 |
|---|---|---|
| C01 | Need/Evidence/Problem/Intent/Assumption | Discovery Ready、Finding、Learning |
| C02 | Initiative/Scope/Risk/Dependency/Metric Plan | Specification 子 Gate、RAR、PHR |
| C03 | PRD/Feature/Requirement Index/Quality Summary | PRD Ready、Specification Ready |
| C04 | Requirement/Revision/Conflict/Readiness | Requirement Ready、Finding、Health |
| C05 | Acceptance/Verification/Validation/Evidence | Gate Evidence、Release Ready |
| C06 | UX/Design/Coverage/Failure/Readiness | Design Ready、Quality Finding |
| C07 | Role/Authority/Approval/Stop/Escalation | Gate RACI、独立性、Agent 阻断 |
| C08 | Context/Freshness/Conflict/Fingerprint | Context/Execution Readiness |
| C09 | Run/Actual Change/Validation/HRR/Failure | Execution/Release Evidence、Agent Health |
| C10 | Trace/Coverage/Lineage/IQR/UCR/OAR | Trace Ready、Gate Gap、Health |
| C11 | Asset/Revision/Baseline/CHG/RLC/Drift | Configuration/Release Ready、复评触发 |

### 18.2 E01 架构治理

当前未激活。目标产品出现多服务、多仓库、关键容量、重大迁移或长期架构演进时必须复评。激活后向 C12 提供 Architecture Decision、Fitness、Debt、Drift 和 Review Evidence。

### 18.3 E02 安全、隐私与合规

当前未激活。目标产品处理账号、外部 API、Secret、个人信息、支付或监管数据时必须复评。激活后向 C12 提供 Security/Privacy/Compliance Gate、Risk、Waiver 和 Verification Evidence。Non-waivable 法规项禁止 EWR。

### 18.4 E03 数据与 AI 数据

当前未激活。目标产品涉及分析数据、数据契约、模型训练、RAG、评估数据集或高数据质量时必须复评。激活后向 C12 提供 Data Quality、Model/Data Evaluation、Bias、Drift 和 Lineage Evidence。

### 18.5 E04 知识与正式记录

当前激活。C12 必须立即执行 E04 的元数据、访问、保留、更正、归档、恢复和审计目标。RVR、GTE、EWR、RAR、PHR、RTR 和 IAP 历史禁止只保留在聊天或临时仪表盘。

### 18.6 E05 产品运营与服务管理

当前未激活。目标产品存在生产服务、SLA/SLO、灰度、告警、值守、Incident 或多环境运行时必须复评。激活后向 C12 提供 SLO、Monitoring、Incident、Problem、Post-release Observation、Rollback 和 Service Review。

### 18.7 交接不变量

1. C12 只消费上游权威事实，不复制正文；
2. Gate Decision 不修改对象 State，状态转换由对象 Owner 按决定执行并记录；
3. EWR/RAR 不改变 Check Result、Requirement Result 或 Risk 值；
4. PHR 不改变原始 Metric Source；
5. RTR 不改写 Incident/Defect/Run；
6. IAP 行动变更正式资产时必须进入 C11；
7. 未激活扩展的已识别 Risk 仍进入 C12。

## 19. 参考标准

| 级别 | 标准 | 版本状态 | C12 适用主题 |
|---|---|---|---|
| R1 | ISO 9001:2015/Amd 1:2024 | Published；新版处于出版流程 | 角色、目标、绩效评价、审核、管理评审、纠正、改进、气候相关性 |
| R1 | IEEE 1012-2024 | Active Standard | V&V、评审、完整性级别、独立性和全生命周期评价 |
| R1 | ISO/IEC 25010:2023 | Published | 九类产品质量模型 |
| R1 | ISO/IEC 25040:2024 | Published | 质量评价定义、设计、计划、执行和结束 |
| R1 | ISO 31000:2018 | Published；待修订 | Risk Assessment、Treatment、Acceptance、Monitoring、Review |
| R1 | ISO/IEC 42001:2023 | Published | AI 目标、Risk、Impact、绩效评价、审核和持续改进 |

### 19.1 引用控制

1. 标准年份和状态按 2026-07-28 官方信息记录；
2. ISO 9001 新版正式发布后必须触发 C11 Change 和 C12 适用性复评；
3. IEEE 1012-2024 只映射官方公开范围和过程组；
4. ISO/IEC 25010 不提供项目固定 Threshold；
5. ISO/IEC 25040 不提供具体测试方法；
6. ISO 31000 是指南，不得声称 C12 因引用该标准获得认证；
7. ISO/IEC 42001 的组织认证范围不得由单份 C12 文档推断；
8. 标准全文冲突时，以合法取得的正式版本为准并执行 Change Control。

## 20. 附录：模板、清单、指标与条款映射

### 20.1 通用产物头

```yaml
artifact_id: ""
artifact_type: ""
name_or_summary: ""
purpose: ""
source: []
owner: ""
formal_state: ""
current_revision: ""
snapshot_or_baseline: ""
applicable_scope: ""
trace_links: []
access_classification: "Internal"
retention_rule: ""
created_by: ""
created_at: ""
updated_by: ""
updated_at: ""
history_reference: []
```

### 20.2 RVR 模板

```yaml
review_record:
  review_id: "RVR-0001"
  formal_state: "Planned"
  review_type: ""
  purpose: ""
  object:
    asset_id: ""
    revision: ""
    snapshot_or_baseline: ""
  scope: ""
  inputs: []
  missing_inputs: []
  criteria_revision: ""
  reviewers:
    - identity: ""
      role: ""
      competence: ""
      independence: ""
  method: ""
  sample:
    population: ""
    method: ""
    size: ""
    limitation: ""
  tool_and_rule_versions: []
  checks:
    - check_id: ""
      result: "Not Evaluated"
      evidence: []
      finding_id: ""
  findings:
    - finding_id: ""
      severity: ""
      blocking_level: ""
      criterion: ""
      fact: ""
      evidence: []
      owner: ""
      due_at: ""
  review_conclusion: ""
  remediation_actions: []
  rereview_result: ""
  acceptance_authority: ""
  started_at: ""
  completed_at: ""
  accepted_at: ""
```

### 20.3 QGC 模板

```yaml
quality_gate_checklist:
  qgc_id: "QGC-0001"
  formal_state: "Draft"
  gate_type: ""
  gate_profile: ""
  parent_mandatory_gate: ""
  purpose: ""
  scope: ""
  applicable_objects: []
  applicable_version: ""
  checks:
    - check_id: ""
      statement: ""
      rationale: ""
      required_inputs: []
      required_evidence: []
      evaluation_method: ""
      pass_rule: ""
      fail_rule: ""
      blocked_rule: ""
      not_applicable_rule: ""
      blocking_level: "Blocking"
      waivability: "Non-waivable"
      condition_eligibility: false
      responsible_role: ""
      reviewer_independence: ""
      automation_boundary: ""
  risk_escalation: ""
  owner: ""
  approver: ""
  effective_at: ""
  review_frequency: ""
  supersedes: ""
```

### 20.4 GTE 模板

```yaml
gate_decision:
  gate_decision_id: "GTE-0001"
  formal_state: "Proposed"
  gate_outcome: ""
  gate_type: ""
  gate_profile: ""
  parent_mandatory_gate: ""
  object:
    asset_id: ""
    revision: ""
    snapshot_or_baseline: ""
  scope: ""
  qgc_revision: ""
  review_records: []
  evidence: []
  metric_snapshot: ""
  check_summary:
    pass: 0
    fail: 0
    blocked: 0
    not_applicable: 0
    not_evaluated: 0
  unmet_items: []
  findings: []
  risks: []
  unknowns: []
  waivers: []
  risk_acceptances: []
  rationale: ""
  conditions:
    - condition: ""
      owner: ""
      due_at: ""
      verification: ""
  approver: ""
  authority: ""
  decided_at: ""
  effective_at: ""
  expires_at: ""
  next_state_or_stage: ""
  reevaluation_triggers: []
  supersedes: ""
```

### 20.5 EWR 模板

```yaml
exception_or_waiver_record:
  ewr_id: "EWR-0001"
  formal_state: "Proposed"
  deviated_rule_or_gate_item: ""
  rule_revision: ""
  waivability: "Waivable"
  scope:
    objects: []
    environment: ""
    time_boundary: ""
  reason: ""
  alternatives: []
  impact: ""
  risks: []
  compensating_controls:
    - control: ""
      evidence: []
  owner: ""
  approver: ""
  authority: ""
  effective_at: ""
  expires_at: ""
  monitoring: []
  review_frequency: ""
  revocation_conditions: []
  reevaluation_triggers: []
  exit_conditions: []
  related_gate_risk_change: []
  supersedes: ""
```

### 20.6 RAR 模板

```yaml
risk_acceptance_record:
  rar_id: "RAR-0001"
  formal_state: "Proposed"
  risk_id: ""
  risk_source: ""
  affected_scope:
    assets: []
    environment: ""
    stakeholders: []
    time_boundary: ""
  inherent_or_current_risk: ""
  current_controls:
    - control: ""
      evidence: []
  residual_risk: ""
  evaluation_criteria: ""
  acceptance_reason: ""
  alternatives: []
  risk_owner: ""
  acceptance_authority: ""
  monitoring:
    - metric_id: ""
      threshold: ""
      frequency: ""
  effective_at: ""
  review_at: ""
  expires_at: ""
  revocation_conditions: []
  escalation: ""
  related_gate_waiver_health_incident: []
  supersedes: ""
```

### 20.7 PHR 模板

```yaml
product_health_report:
  phr_id: "PHR-0001"
  formal_state: "Draft"
  scope: ""
  period:
    start: ""
    end: ""
    timezone: ""
  metric_definition_revision: ""
  data_snapshot: ""
  metrics:
    - metric_id: ""
      formula: ""
      numerator: ""
      denominator: ""
      value: ""
      unit: ""
      threshold: ""
      threshold_result: "Not Evaluated"
      trend: "Insufficient Data"
      data_status: "Unavailable"
      segments: []
      exclusions: []
      unknowns: []
      limitations: []
  domains:
    requirement_health: ""
    agent_health: ""
    engineering_health: ""
    process_health: ""
  product_quality_applicability:
    functional_suitability: ""
    performance_efficiency: ""
    compatibility: ""
    interaction_capability: ""
    reliability: ""
    security: ""
    maintainability: ""
    flexibility: ""
    safety: ""
  ai_health_applicability: ""
  health_conclusion: "Indeterminate"
  rationale: ""
  findings: []
  risks: []
  waivers: []
  risk_acceptances: []
  actions: []
  report_owner: ""
  reviewer: ""
  approver: ""
  previous_phr: ""
  comparability: ""
```

### 20.8 RTR 模板

```yaml
retrospective_record:
  rtr_id: "RTR-0001"
  formal_state: "Planned"
  retrospective_type: ""
  scope: ""
  period: ""
  related_release_run_incident: []
  participants: []
  facilitator: ""
  independence: ""
  goals_and_expected_results: []
  actual_results: []
  timeline:
    - time: ""
      fact: ""
      evidence: []
  successes: []
  deviations: []
  failures: []
  incidents: []
  feedback: []
  direct_causes: []
  contributing_factors: []
  system_conditions: []
  unknowns: []
  assumptions: []
  learnings:
    - learning: ""
      evidence: []
      affected_assets: []
  decisions: []
  improvement_actions: []
  no_action_rationale: ""
  acceptance_authority: ""
  started_at: ""
  completed_at: ""
  accepted_at: ""
```

### 20.9 IAP 模板

```yaml
improvement_action_plan:
  iap_id: "IAP-0001"
  formal_state: "Draft"
  purpose: ""
  scope: ""
  actions:
    - action_id: ""
      sources: []
      problem_or_opportunity: ""
      target_outcome: ""
      action_content: ""
      priority: ""
      owner: ""
      start_at: ""
      due_at: ""
      success_condition: ""
      measure: ""
      baseline: ""
      target: ""
      dependencies: []
      member_status: "Open"
      blocked_reason: ""
      escalation: ""
      closure_evidence: []
      effectiveness_reviewer: ""
      effectiveness_result: ""
      reopened_or_successor: ""
  owner: ""
  approver: ""
  supersedes: ""
```

### 20.10 五个强制 Gate 映射

| Mandatory Gate | 主要规范输入 | 允许的领域子 Gate |
|---|---|---|
| Discovery Ready | C01、C10、C11、C12 | Evidence Ready、Problem Ready |
| Specification Ready | C02 至 C06、C10、C11、C12 | Initiative Ready、PRD Ready、Requirement Ready、Design Ready |
| Agent Execution Ready | C05 至 C09、C11、C12 | Context Ready、Execution Plan Ready |
| Release Ready | C05、C09 至 C12、适用 E01 至 E05 | Trace Ready、Configuration Ready、Deployment Ready |
| Learning Closed | C01/C02 Metric、C09/C11 实际结果、C12 PHR/RTR/IAP、适用 E05 | Observation Complete、Retrospective Accepted |

### 20.11 Gate Decision 清单

- [ ] Gate Type/Profile 和 Parent Mandatory Gate 明确；
- [ ] Object ID、Revision、Snapshot/Baseline 固定；
- [ ] QGC Revision Approved；
- [ ] RVR Accepted；
- [ ] Required Evidence 完整；
- [ ] Check Result 与 Finding 可追；
- [ ] Non-waivable Blocking Fail 为 0；
- [ ] N/A 有理由和 Authority；
- [ ] EWR 有 Scope、Risk、补偿控制和 Expiry；
- [ ] RAR 有 Residual Risk、监控和 Expiry；
- [ ] Condition 有 Owner、Due、Verification 和 Expiry；
- [ ] Gate Outcome 与 DEC State 映射正确；
- [ ] Approver 有 Authority 且满足独立性；
- [ ] Next State/Stage 和下游限制明确；
- [ ] Re-evaluation Trigger 明确；
- [ ] History/Supersession 保留。

### 20.12 Metric Definition 模板

```yaml
metric_definition:
  metric_id: ""
  name: ""
  purpose: ""
  owner: ""
  domain: ""
  health_question: ""
  scope: ""
  population: ""
  unit: ""
  numerator: ""
  denominator: ""
  formula: ""
  inclusions: []
  exclusions: []
  missing_data_rule: ""
  source: ""
  source_authority: ""
  query_or_method: ""
  source_revision: ""
  period: ""
  timezone: ""
  baseline: ""
  target: ""
  threshold: ""
  direction: ""
  segmentation: []
  aggregation: ""
  data_quality_checks: []
  threshold_result_rule: ""
  trend_rule: ""
  limitations: []
  misuse_warnings: []
  definition_revision: ""
  effective_at: ""
  supersedes: ""
```

### 20.13 Anti-gaming 清单

- [ ] Metric Definition 在周期前冻结；
- [ ] Population 与 Scope 未选择性变化；
- [ ] Numerator/Denominator 可重算；
- [ ] Exclusion 和 Missing Data 公开；
- [ ] 分类和 Severity 未无据降低；
- [ ] 失败、Waiver、Defect、Run、Action 未删除；
- [ ] 登记时间未人为跨期；
- [ ] Critical Segment 单独展示；
- [ ] Unknown/Unavailable 未计为零或 Pass；
- [ ] Definition 变化未回写历史；
- [ ] Output Metric 与 Outcome/Guardrail 同时展示；
- [ ] Action 完成与效果验证分离。

### 20.14 Retrospective 清单

- [ ] Scope、Period、对象固定；
- [ ] 目标和实际结果可比较；
- [ ] Timeline 基于 Evidence；
- [ ] Fact、Inference、Decision 分离；
- [ ] Success、Deviation、Incident、Feedback 完整；
- [ ] 原因、贡献因素、系统条件和 Unknown 分离；
- [ ] Learning 有 Evidence；
- [ ] Learning 回流上游；
- [ ] IAP Action 或 No-action Rationale 完整；
- [ ] Action 有 Owner、Due、Success；
- [ ] Facilitator/Reviewer 独立性满足；
- [ ] RTR Accepted 由人类 Authority 决定。

### 20.15 示例

#### 示例 A：Review 通过但 Gate 拒绝

```text
RVR State: Accepted
Review Conclusion: Conformant with Findings
Finding: Release rollback evidence missing
GTE Outcome: Reject
GTE State: Rejected
```

RVR Accepted 只证明评审记录可信。Release Ready 仍因 Blocking Evidence 缺失而拒绝。

#### 示例 B：Waiver 不等于 Pass

```text
Check Result: Fail
EWR State: Approved
GTE Outcome: Waive
GTE State: Waived
```

Fail 保持为 Fail。EWR 只允许在范围和期限内偏离。

#### 示例 C：Risk Acceptance 不消除 Risk

```text
Residual Risk: High
RAR State: Approved
Monitoring Threshold: defined
GTE Outcome: Conditional Pass
```

Risk Register 仍显示 High，PHR 和 Gate 必须持续展示并监控。

#### 示例 D：无数据不是健康

```text
Metric Value: null
Data Status: Unavailable
Threshold Result: Not Evaluated
Trend: Insufficient Data
Health Conclusion: Indeterminate
```

禁止将 `null` 转为 0 或 Healthy。

### 20.16 ISO/IEC 25010 九类质量适用性清单

- [ ] Functional suitability；
- [ ] Performance efficiency；
- [ ] Compatibility；
- [ ] Interaction capability；
- [ ] Reliability；
- [ ] Security；
- [ ] Maintainability；
- [ ] Flexibility；
- [ ] Safety。

每项必须选择 Applicable 或 Not Applicable。Not Applicable 必须记录 Scope、理由、Reviewer 和 Approver。

### 20.17 标准状态复评清单

- [ ] ISO/IEC/IEEE/IEEE 官方产品页仍可访问；
- [ ] 标准编号、年份、Edition、Status 未变化；
- [ ] 新 Amendment、Corrigendum 或 Replacement 已检查；
- [ ] ISO 9001 第 6 版是否已正式发布；
- [ ] 标准变化是否影响 QGC、Metric、Gate、Waiver、RAR 或 PHR；
- [ ] 影响是否已建立 C11 CHG/IMA/CHD；
- [ ] 文末条款映射是否更新；
- [ ] 旧标准映射和历史是否保留。

### 20.18 国际标准条款映射

以下映射基于 ISO 和 IEEE 官方产品页及公开目录。项目控制要求是对标准主题的工程化落实，不表示标准逐字规定了本项目产物代码、状态值、Gate 名称、指标公式或模板字段。

| 国际标准及条款/公开主题 | 公开主题 | 本规范落实位置 |
|---|---|---|
| ISO 9001:2015 第 4.1 章 | 组织及其环境 | 3.1、10.7、16.5 |
| ISO 9001:2015/Amd 1:2024 对 4.1 的修订 | 气候变化相关性 | 10.7、15.1 |
| ISO 9001:2015 第 4.2 章及 Amd 1:2024 | 相关方需要和气候相关要求 | 10.7、18.2 至 18.6 |
| ISO 9001:2015 第 5.3 章 | 角色、职责和权限 | 第 7 章 |
| ISO 9001:2015 第 6.1 章 | 风险和机会 | 10.13、10.14 |
| ISO 9001:2015 第 6.2 章 | 质量目标及实现策划 | 10.15、10.16 |
| ISO 9001:2015 第 6.3 章 | 变更策划 | 10.5、16.5 |
| ISO 9001:2015 第 7.5 章 | 成文信息 | 第 13、16 章 |
| ISO 9001:2015 第 8.1 章 | 运行策划和控制 | 9.1、10.5 至 10.12 |
| ISO 9001:2015 第 9.1 章 | 监视、测量、分析和评价 | 10.15 至 10.21、13.6 |
| ISO 9001:2015 第 9.2 章 | 内部审核 | 10.24 |
| ISO 9001:2015 第 9.3 章 | 管理评审 | 10.24、14.5 |
| ISO 9001:2015 第 10.1 章 | 改进总则 | 9.2、10.22、10.23 |
| ISO 9001:2015 第 10.2 章 | 不符合与纠正措施 | 10.3、10.23、10.24 |
| ISO 9001:2015 第 10.3 章 | 持续改进 | 10.22、10.23、14.5 |
| IEEE 1012-2024 官方公开 Scope | V&V 判断符合活动要求和满足预期用途/用户需要 | 10.1 至 10.4、18.1 |
| IEEE 1012-2024 官方公开 Scope | 系统、软件、硬件和接口 | 第 3、10.1 章 |
| IEEE 1012-2024 官方公开 Scope | 开发、维护、复用、遗留和 COTS 对象 | 3、10.1、18 |
| IEEE 1012-2024 官方公开 Scope | 不同完整性级别的 V&V | 7.1、10.1、10.2 |
| IEEE 1012-2024 官方公开 Scope | 分析、评价、评审、检查、评估和测试 | 10.1 至 10.4 |
| IEEE 1012-2024 官方公开过程组 | 协议、组织项目使能、项目、技术、实现、支持和复用 | 3.1、18.1 |
| ISO/IEC 25010:2023 第 1 章 | 产品质量模型范围 | 10.16、20.16 |
| ISO/IEC 25010:2023 第 4 章 | 产品质量模型 | 10.8、10.16、20.16 |
| ISO/IEC 25010:2023 第 4.1 章 | 质量模型结构 | 10.16、13.6 |
| ISO/IEC 25010:2023 第 4.2 章 | 质量模型目标对象 | 3、10.16 |
| ISO/IEC 25010:2023 第 5 章 | 与使用质量模型关系 | 10.7、10.11、18 |
| ISO/IEC 25010:2023 Annex C | 使用质量模型进行测量 | 10.15 至 10.20 |
| ISO/IEC 25040:2024 第 1 章 | ICT 产品、数据和 IT 服务质量评价范围 | 第 3、18 章 |
| ISO/IEC 25040:2024 第 4 章 | 质量评价概念 | 6、10.15、10.16 |
| ISO/IEC 25040:2024 第 4.1 章 | 质量评价定义 | 5.4、6、10.16 |
| ISO/IEC 25040:2024 第 4.2 章 | 质量模型与测量 | 10.15、10.16、20.12 |
| ISO/IEC 25040:2024 第 4.3 章 | 测量来源 | 10.15、10.20 |
| ISO/IEC 25040:2024 第 4.4 章 | 质量评价任务 | 9.2、10.15 至 10.20 |
| ISO/IEC 25040:2024 第 4.5 章 | 质量评级模块 | 5.2、10.20 |
| ISO/IEC 25040:2024 第 4.6 章 | 使用评价进行评估 | 10.16、14.4 |
| ISO/IEC 25040:2024 第 5.1 章 | 评价过程总览 | 9.2 |
| ISO/IEC 25040:2024 第 5.2 章 | 定义评价 | 10.15 |
| ISO/IEC 25040:2024 第 5.3 章 | 设计评价 | 10.15、20.12 |
| ISO/IEC 25040:2024 第 5.4 章 | 策划评价 | 9.2、10.16 |
| ISO/IEC 25040:2024 第 5.5 章 | 执行评价 | 10.16 至 10.21 |
| ISO/IEC 25040:2024 第 5.6 章 | 结束评价 | 10.16、13.6、14.4 |
| ISO 31000:2018 第 4 章 | 风险管理原则 | 10.13、10.14 |
| ISO 31000:2018 第 5.2 章 | 领导与承诺 | 7、10.14 |
| ISO 31000:2018 第 5.3 章 | 整合 | 8.3、18 |
| ISO 31000:2018 第 5.4 章 | 设计 | 10.13、10.14 |
| ISO 31000:2018 第 5.5 章 | 实施 | 10.12 至 10.14 |
| ISO 31000:2018 第 5.6 章 | 评价 | 10.14、10.16 |
| ISO 31000:2018 第 5.7 章 | 改进 | 10.22、10.23 |
| ISO 31000:2018 第 6.2 章 | 沟通和协商 | 10.13、10.14、10.22 |
| ISO 31000:2018 第 6.3 章 | 范围、环境和准则 | 10.13、10.14、13.4、13.5 |
| ISO 31000:2018 第 6.4 章 | 风险评估 | 10.14 |
| ISO 31000:2018 第 6.5 章 | 风险处置 | 10.12 至 10.14 |
| ISO 31000:2018 第 6.6 章 | 监视和评审 | 10.14、10.16、16.5 |
| ISO 31000:2018 第 6.7 章 | 记录和报告 | 13.5、16 |
| ISO/IEC 42001:2023 第 1 章 | AI 管理体系范围 | 3、10.25、18.3 至 18.5 |
| ISO/IEC 42001:2023 第 4.1 章 | 组织及其环境 | 3.1、10.16 |
| ISO/IEC 42001:2023 第 4.2 章 | 相关方需要和期望 | 10.7、10.16 |
| ISO/IEC 42001:2023 第 5.3 章 | 角色、职责和权限 | 7、10.25 |
| ISO/IEC 42001:2023 第 6.1 章 | AI 风险和机会 | 10.14、10.16 |
| ISO/IEC 42001:2023 第 6.2 章 | AI 目标及实现策划 | 10.15、10.16 |
| ISO/IEC 42001:2023 第 6.3 章 | 变更策划 | 16.5 |
| ISO/IEC 42001:2023 第 8.1 章 | 运行策划和控制 | 10.9、10.25 |
| ISO/IEC 42001:2023 第 8.2 章 | AI 风险评估 | 10.14、10.16 |
| ISO/IEC 42001:2023 第 8.3 章 | AI 风险处置 | 10.13、10.14 |
| ISO/IEC 42001:2023 第 8.4 章 | AI 系统影响评估 | 10.16、18.4 |
| ISO/IEC 42001:2023 第 9 章 | 绩效评价 | 10.15 至 10.21、10.24 |
| ISO/IEC 42001:2023 第 10 章 | 改进 | 10.22 至 10.24 |

规范性国际标准来源：

1. ISO, [ISO 9001:2015](https://www.iso.org/standard/62085.html) 与 [ISO 9001:2015/Amd 1:2024](https://www.iso.org/standard/88431.html)。
2. IEEE Standards Association, [IEEE 1012-2024](https://standards.ieee.org/ieee/1012/7324/)。
3. ISO, [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)。
4. ISO, [ISO/IEC 25040:2024](https://www.iso.org/standard/83467.html)。
5. ISO, [ISO 31000:2018](https://www.iso.org/standard/65694.html)。
6. ISO, [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)。
