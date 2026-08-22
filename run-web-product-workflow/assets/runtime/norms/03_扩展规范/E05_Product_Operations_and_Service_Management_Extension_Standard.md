# E05 产品运营与服务管理扩展规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | E05 |
| 英文名称 | Product Operations and Service Management Extension Specification |
| 正式文件名 | `E05_Product_Operations_and_Service_Management_Extension_Standard.md` |
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
| 扩展规范依赖 | E01 至 E04 V6.3 |
| 生产前调研 | RVR-E05-0001 |
| 后续任务 | 跨规范产物归属索引、引用与依赖检查、V6.2 完整符合性检查 |
| 访问级别 | 内部 |
| 保留要求 | Release、Deployment、Rollback、Incident、Problem、Observation、Feedback、Review、Decision、Approval、Command、Evidence 和 Audit 历史必须按 E04 RCS/RTS 及适用法律、监管、合同、安全、隐私和业务连续性要求保留，禁止无痕覆盖 |

本文件在项目负责人批准前不得作为已批准的 E05 正文。当前规范仓库没有生产服务、SLA/SLO、灰度、告警、值守或事故运行对象，因此 `当前激活状态 = 未激活`；这不影响 E05 在 P2 交付集合中的 `编制适用性 = 必须编制`。目标产品满足任一强制触发条件时必须重新判定并激活。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品发布后持续运营、服务目标、运行观测、发布与回滚、监控与告警、事故与问题、用户反馈、维护、退役、评审和改进的最低治理要求。

本规范实现以下目标：

1. 使 Service 的用户、价值、Scope、Owner、依赖、环境、支持时间、质量目标和退出条件明确；
2. 使 SLI 可计算、SLO 可测量、观察窗口与错误预算可追踪，并关联业务结果；
3. 使每次 Release 固定内容、环境、批准、观察指标、停止条件和 Rollback 条件；
4. 使 Deployment 与 Release 分离，并能追踪至精确版本、配置、数据、环境和变更；
5. 使 Monitoring Signal、Alert、Incident、Problem、Defect、Risk、Change 和 Request 分类明确；
6. 使 Incident 响应优先恢复服务，同时保留时间线、用户影响、动作、证据和后续事项；
7. 使 Problem 管理根因、趋势、已知错误、临时措施和永久处理，不与单次 Incident 混合；
8. 使 Operational Observation 可追溯到 Service、Release、环境和受影响 Requirement；
9. 使 User Feedback 保留原始陈述、情境、影响、证据、分类和处置状态；
10. 使 Post-release Review 将目标、实际结果、Incident、Feedback、Risk、Decision 和行动形成闭环；
11. 使运行学习进入 C01、C02、C04 或 C12 受控产物，不停留在聊天、告警或仪表盘；
12. 使运行命令固定工具、目标、版本、环境、授权、模式、限制、停止、回滚和 Evidence；
13. 使 Operation、Maintenance、Continuity、Recovery 和 Disposal 边界明确；
14. 使服务管理、软件生命周期、维护、质量和风险控制具有国际标准映射；
15. 防止用工具成功、零告警、恢复完成、SLO 达标或单次用户反馈自动推导产品正确、风险可接受或发布获批；
16. 防止 Agent 自批 Release、Rollback、Incident Closure、Risk Acceptance、Waiver 或 Gate。

## 3. 适用范围

E05 在任一触发条件成立时必须激活：

- 产品进入持续运营；
- 存在生产环境、SLA、SLO、值守或 On-call；
- 灰度、回滚、事故和用户反馈需要受控；
- 发布后指标决定下一轮产品演进。

激活后的 E05 适用于：

- Web App、SaaS、API、Worker、Batch、Mobile Backend、AI Service、Data Service 和支撑组件；
- Production、Canary、Staging、Disaster Recovery 和其他影响真实用户或业务结果的环境；
- Service、Release、Deployment、Rollback、Monitoring、Alert、Incident、Problem、Maintenance、Recovery 和 Disposal；
- 可用性、延迟、吞吐、错误率、正确性、数据质量、安全、隐私、成本、容量和用户结果；
- SLA、SLO、SLI、错误预算、支持时间、值守、升级和沟通；
- 用户反馈、支持工单、运行观察、实验结果、投诉和运营报告；
- Human、Agent、Automation、Tool、Operator、Service Owner、Incident Commander 和 Reviewer；
- P2 档位下 SDF、SLO、RBP、MAP、INR、PBR、OPO、UFR、PRR 和 IBL；
- 设计、开发、验证、发布、运行、维护、退役和持续改进阶段。

### 3.1 当前仓库状态

当前仓库仅生产规范文档，没有可识别的生产 Service、SLA/SLO、Deployment、Monitoring、Alert、On-call 或 Incident 运行对象，因此：

1. `编制适用性 = 必须编制`；
2. `当前激活状态 = 未激活`；
3. 本文件必须完整定义全部 E05 控制、模板和检查清单；
4. 当前仓库不实例化虚构的 Service Definition、SLI/SLO Register 或 Incident Record；
5. 规范文件自身继续受 C01 至 C12 和已激活 E04 约束；
6. 未来出现生产服务、真实用户流量、服务目标或值守时，必须重新执行 Applicability Decision；
7. 激活前已经识别的运营 Risk 仍必须进入 C02、C05、C06、C11 或 C12；
8. 修改当前结论必须引用适用 C11 Change Request 和 C12 Decision。

### 3.2 横向生效边界

1. C01 管理 Need、Problem、Evidence、Product Intent 和 Goal；
2. C02 管理 Initiative、Scope、Risk、Success Metric 和 Dependency；
3. C03 管理 PRD、Feature、Scenario、Requirement Index 和目标 Release；
4. C04 管理原子 Requirement、Revision 和 Supersession；
5. C05 管理 Acceptance、Verification、Validation 和 Evidence；
6. C06 管理 UX、Technical Design、Failure Mode 和 Design Decision；
7. C07 至 C09 管理 Authority、Collaboration、Context、Agent Run 和 Command；
8. C10 管理 Decision、Trace、Lineage、Impact Query 和 Orphan；
9. C11 管理 Change、Revision、Snapshot、Baseline、Release Configuration 和 Recovery Point；
10. C12 管理 Review、Gate、Waiver、Risk Acceptance 和 Product Health；
11. E01 管理 Architecture、Capacity、Resilience 和 Conformance；
12. E02 管理 Security、Privacy、Compliance、Vulnerability 和事件通知约束；
13. E03 管理 Data/AI Data Contract、Quality、Lineage、Retention 和 Dataset；
14. E04 管理运行 Knowledge、Record、Source、Access、Retention、Freshness 和历史恢复；
15. E05 管理 Service、SLO、Release Observation、Incident、Problem、Feedback 和 Improvement。

## 4. 不适用范围

本规范不负责：

- 代替 C01 的 Need、Problem、Intent、Goal 或 Evidence；
- 代替 C02 的 Risk Register、Success Metric Plan 或 Dependency Register；
- 代替 C03 PRD、Feature、Scenario 或 Requirement Index；
- 代替 C04 Requirement Record 或需求变更；
- 代替 C05 Verification、Validation、Acceptance Decision 或 Evidence 充分性判断；
- 代替 C06 Technical Design、Failure Mode 或 Architecture Design；
- 代替 C07 Authority 或 C09 Agent Run Record；
- 代替 C10 Decision Record、Traceability Matrix 或 Impact Query；
- 代替 C11 Change Request、Baseline、Release Configuration 或 Snapshot；
- 代替 C12 Gate Decision、Exception/Waiver 或 Risk Acceptance；
- 代替 E01 Capacity、Resilience、Architecture Fitness 或 Conformance；
- 代替 E02 Security Incident、Privacy Breach、Legal Notification 或 Compliance 决定；
- 代替 E03 Data Quality Incident、Data Contract 或 Data Retention；
- 代替 E04 Record Classification、Retention、Access、Knowledge Freshness 或 Supersession；
- 指定唯一 Cloud、CI/CD、Observability、ITSM、Incident、Ticket、On-call 或 Feature Flag 产品；
- 声明组织、Service、过程或工具获得 ISO 认证；
- 提供 SLA、合同、监管通知、安全披露、隐私事件或法律责任的法律结论。

E05 可以消费上述事实，但禁止：

- 用 SDF 替代 Product Definition、PRD 或 Architecture；
- 用 SLO 替代 SLA、Acceptance Criteria 或业务 Goal；
- 用 RBP 替代 C11 Release Configuration 或 Change Approval；
- 用 MAP 替代安全、隐私或数据专项检测要求；
- 用 INR 替代 Defect、Risk、Change、Requirement 或有权法律通知；
- 用 PBR 覆盖原 Incident 时间线；
- 用 OPO 自动判定 Requirement 通过或失败；
- 用 UFR 的单条反馈自动确定产品优先级；
- 用 PRR 自动批准后续发布或接受剩余 Risk；
- 用 IBL 代替 C02 Initiative、C04 Requirement、C11 Change 或 C12 Corrective Action；
- 用 Rollback 成功证明数据完整、用户影响消除或事故可关闭；
- 用 SLO 达标证明用户满意、业务成功或零事故；
- 用 Tool Exit Code、Dashboard Green 或 Agent Confidence 判定治理 Pass。

## 5. 规范性用语与受控判定

### 5.1 规范性用语

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

法律、监管、合同、安全、隐私、支付、生命安全、数据不可逆损失、Non-waivable Gate 和 Authority Boundary 不得通过普通 EWR 绕过。

### 5.2 扩展适用性判定值

以下值是 E05 Activation Status，不是资产 State：

| 值 | 语义 |
|---|---|
| Not Evaluated | 尚未评价；禁止进入 Discovery Ready |
| Pending | 存在 Unknown 或等待 Evidence/Authority |
| Inactive | 全部触发条件明确为 No |
| Conditionally Active | 在明确 Scope、条件和期限内激活 |
| Active | 任一触发条件成立，E05 完整适用 |
| Retiring | 服务正在退出，但仍需运行、迁移、沟通和处置 |
| Retired | 服务已退出活动运营；历史记录继续保留 |

### 5.3 触发条件判定值

| 值 | 语义 |
|---|---|
| Yes | 条件已由 Evidence 证实 |
| No | 条件已由 Evidence 排除 |
| Unknown | 证据不足、Scope 不明确或等待有权判断 |
| Not Applicable | 条件不属于被评 Scope；必须记录理由和批准者 |

任一 Yes 使 E05 进入 Active 或 Conditionally Active。任一 Unknown 使 E05 进入 Pending。

### 5.4 领域判定值

| 判定域 | 允许值 |
|---|---|
| SLO Evaluation | Met、Not Met、No Data、Invalid Data、Not Evaluated |
| Release Readiness | Ready、Conditionally Ready、Not Ready、Not Evaluated |
| Deployment Result | Completed、Partially Completed、Failed、Rolled Back、Cancelled、Not Evaluated |
| Rollback Result | Completed、Partially Completed、Failed、Not Required、Not Evaluated |
| Incident Severity | SEV-1、SEV-2、SEV-3、SEV-4、Unclassified |
| Incident Impact | Ongoing、Contained、Recovered、Unknown |
| Root Cause Status | Not Started、Hypothesis、Under Analysis、Confirmed、Unknown |
| Observation Assessment | Within Expected、Degraded、Improved、Anomalous、Inconclusive、Not Evaluated |
| Feedback Disposition | New、Triaged、Accepted for Action、Duplicate、Declined、Deferred、Closed |
| Review Conclusion | Proceed、Proceed with Conditions、Rollback、Remediate、Escalate、Inconclusive |

领域 Result 不得注册为 DOC、CASE、EXEC 或 EVID State。每个 Result 必须固定对象 Revision、时间窗口、Criteria、Evidence、Evaluator 和限制。

### 5.5 Unknown、Not Applicable 与 Fail Closed

1. Service Owner、Release、Environment、Authority、Rollback、数据影响或用户影响 Unknown 时，禁止高风险 Deployment；
2. SLI 数据为 No Data/Invalid Data 时不得判 SLO Met；
3. Incident Severity 为 Unclassified 时按组织预定义的最高适用临时响应级别处理，直至有权分级；
4. Root Cause Unknown 不阻止先恢复服务，但禁止把 Incident 关闭为已完成根因改进；
5. Not Applicable 必须记录 Scope、理由、依据、批准者和复核触发器；
6. 空值不得替代 Unknown、Not Applicable 或 Not Evaluated；
7. Agent 不得推断权限、严重度、法律通知义务、剩余风险接受或事故关闭。

## 6. 术语、定义与边界

| 术语 | 定义 |
|---|---|
| Service | 为明确用户或消费方持续提供价值、具有 Owner、Scope、接口、依赖、质量目标和生命周期的能力 |
| Service Definition | 固定 Service 身份、价值、Scope、用户、Owner、依赖、环境、支持和退出条件的受控产物 |
| Service Level Indicator（SLI） | 对 Service 某项可观察行为或结果的定量度量 |
| Service Level Objective（SLO） | 在明确窗口、范围和计算方式下对 SLI 的目标值 |
| Service Level Agreement（SLA） | 与外部或内部消费方形成的服务水平协议；是否构成合同由有权角色判断 |
| Error Budget | 在给定窗口内相对 SLO 可容许的不符合额度及其治理用途 |
| Release | 作为受控集合准备交付或已批准交付的产品、代码、配置、数据和文档版本 |
| Deployment | 将特定 Release Configuration 应用于特定 Environment 的执行活动 |
| Service Rollback | 将受影响服务范围恢复到预先固定的可接受配置或运行状态的受控动作；专业化自 C11 Rollback |
| Service Recovery | 在中断或损害后恢复所需业务能力、数据和服务状态的过程；不得与 C11 Configuration Recovery 混同 |
| Monitoring | 持续或周期获取 Service 状态、行为、资源、事件和业务结果的活动 |
| Alert | Monitoring Signal 满足预定义条件后生成、要求明确响应的受控通知 |
| Incident | 已经或正在造成非计划服务中断、质量下降或用户影响的运行事件 |
| Problem | 一个或多个 Incident、趋势或缺陷背后的原因或潜在原因，需独立分析与治理 |
| Known Error | 已确认根因或已知触发方式，且存在已记录临时措施或永久处理计划的 Problem 状态信息 |
| Operational Observation | 在固定 Service、Release、Environment 和时间范围内捕获的运行事实及其初步评价 |
| User Feedback | 用户或群体对体验、结果、问题或期望的原始陈述及其情境 |
| Post-release Review | 对 Release 目标、实际结果、Incident、Feedback、Risk 和行动的受控评审执行 |
| Improvement | 基于运行 Evidence 改善产品、过程、服务或控制的候选事项 |
| Maintenance | 在交付后对软件进行修改、分析和支持以纠错、适应、完善、预防或退役的生命周期活动 |
| Disposal | 在终止使用时受控移除软件、数据、资源和责任，并保留必要记录的活动 |

### 6.1 Service、Product、Feature 与 Component

1. Product 表达面向用户和业务的整体价值边界；Service 表达持续交付和运营责任边界；
2. Feature 是用户可感知能力，不自动具有独立 Service Owner、SLO 或 On-call；
3. Component 是实现构件，不因存在监控而自动成为 Service；
4. 一个 Product 可以包含多个 Service；一个 Service 可以支撑多个 Product；
5. SDF 必须引用而不是复制 Product Definition、PRD、Architecture 和 Requirement 正文。

### 6.2 SLI、SLO、SLA 与业务指标

1. SLI 是度量，SLO 是目标，SLA 是协议，三者不得互换；
2. SLO 必须引用 SLI 计算和窗口，不得只写“高可用”“快速”；
3. SLA 可以引用 SLO，但 SLA 违约、补偿或法律含义由有权角色判断；
4. 业务指标衡量结果价值，技术 SLI 衡量服务行为；二者必须建立关联但不得相互替代；
5. Error Budget 是治理输入，不是自动批准发布的额度。

### 6.3 Release、Deployment、Change 与 Rollback

1. Release 固定“交付什么”，Deployment 固定“何时、向何环境、以何动作应用”；
2. Change Request 授权受控变化，RBP 规定具体发布和回滚执行；
3. 同一 Release 可以有多次 Deployment；每次必须有独立执行记录；
4. Rollback 必须固定目标配置、数据兼容、验证和停止条件；
5. 无法回滚时必须在发布前记录替代恢复策略和有权批准。

### 6.4 Alert、Incident、Problem、Defect、Risk 与 Request

1. Alert 是信号，不自动等于 Incident；
2. Incident 是已经发生的服务影响；Risk 是未来不确定性；
3. Problem 管理根因或趋势；Defect 管理实现不符合；两者可以相互引用但保持独立身份；
4. 用户请求或支持工单不自动是 Incident；有服务影响时必须建立 INR；
5. 单个 Incident 可以关联多个 Problem/Defect；一个 Problem 可以关联多个 Incident；
6. 恢复服务不等于根因已确认、Problem 已关闭或 Risk 已接受。

### 6.5 Monitoring Signal、Observation、Evidence 与 Decision

1. Signal 是原始或加工后的测量结果；
2. OPO 固定 Signal、范围、版本、时间和可靠性，使其可作为候选 Evidence；
3. Evidence 是否充分由 C05/C12 在明确 Criteria 下判断；
4. Dashboard 是展示，不替代原始数据、查询、时间窗口和完整性引用；
5. Observation 不自动改变 Requirement、Release 或 Gate 状态。

### 6.6 Operation、Maintenance、Continuity、Recovery 与 Disposal

1. Operation 维持服务日常交付、监控、支持和响应；
2. Maintenance 修改交付后的软件或相关资产；
3. Continuity 维持或恢复可接受业务能力；Recovery 是实现 Continuity 的具体恢复过程；
4. Rollback 恢复配置，不必然恢复全部业务或数据；
5. Disposal 终止使用并处理资产、数据、依赖和责任；
6. ISO/IEC/IEEE 14764:2022 不覆盖备份、恢复和系统管理等软件运行职能；本规范以 ISO/IEC 20000-1 和 ISO/IEC/IEEE 12207 管理这些 Operation 职能，以 ISO/IEC/IEEE 14764 管理 Maintenance 和 Disposal。

### 6.7 Feedback、Learning 与 Improvement

1. UFR 保留原始反馈及情境，不直接等于 Need、Problem 或 Requirement；
2. Learning 是由多个 Observation、Incident、Feedback 或 Review 形成的可复核认识；
3. Improvement Backlog 是候选改进集合，不替代 Initiative、Requirement、Change 或 Corrective Action；
4. 被接受的学习必须进入 C01 Need/Evidence、C02 Risk/Metric/Initiative、C04 Requirement 或 C12 Improvement/Health；
5. Chat、即时消息、告警评论或会议口头结论不得作为唯一正式闭环。

## 7. 角色、职责与职责分离

### 7.1 角色

| 角色 | 必须职责 | 禁止事项 |
|---|---|---|
| 项目负责人 | 批准 E05、重大适用性变化、关键发布策略和重大例外 | 不得代替无权的法律或监管决定 |
| Service Owner | 服务价值、Scope、SLO、依赖、支持、风险和退出责任 | 不得以 SLO 达标忽略用户或合规影响 |
| Product Owner | 将运行学习转化为产品目标、优先级和需求候选 | 不得用单条反馈直接改动 Baseline |
| Release Manager | Release Scope、窗口、依赖、批准、观察和回滚协调 | 不得扩大已批准 Release Configuration |
| Operator | 按批准 RBP/Runbook 执行部署、回滚和恢复 | 不得使用未固定目标、Latest 或隐式默认值 |
| Incident Commander | 事故分级、响应协调、沟通、恢复和交接 | 不得同时独立批准自身重大事故关闭 |
| Problem Owner | 趋势、根因、已知错误、临时与永久处理 | 不得覆盖 Incident 原始时间线 |
| SRE/Operations Engineer | SLI、Monitoring、Alert、Runbook、容量和可靠性工程 | 不得把技术指标代替业务结果 |
| Support/Feedback Steward | 捕获反馈原文、情境、影响、分类和处置 | 不得伪造用户结论或删除不利反馈 |
| Security/Privacy/Data Owner | 处理专项事件、通知、取证、数据和访问要求 | 不得由普通 Incident 流程覆盖专项义务 |
| Reviewer | 独立检查发布、回滚、Incident、Problem 和 Review Evidence | 不得接受自己生成的高风险输出 |
| Configuration Manager | Release Configuration、Baseline、Change、Snapshot 和恢复点 | 不得把 Git/Artifact 存在推导为已批准 |
| Auditor | 检查日志、状态、授权、证据、闭环和保留 | 不得修改被审计原始记录 |
| Agent | 在授权范围内分析信号、生成候选记录、执行检查和建议 | 不得批准发布、回滚、事故关闭、风险接受或 Gate |

### 7.2 最低职责分离

以下事项必须至少由两个不同责任主体承担：

1. 高风险 Release 执行与批准；
2. Rollback 目标确认与执行；
3. SEV-1/SEV-2 Incident 指挥与关闭批准；
4. Problem 根因提出与确认；
5. SLO 定义与业务接受；
6. Monitoring/Alert 规则修改与验证；
7. 高风险生产命令生成与执行；
8. 数据恢复执行与完整性验证；
9. Post-release Review 编制与接受；
10. Agent 生成运行结论与人类批准；
11. Risk Acceptance 提出与批准；
12. 服务退役执行与最终确认。

### 7.3 Authority 规则

1. Authority 必须引用 C07 Human Authority 或等价已批准来源；
2. Authority 必须限定 Operation、Service、Release、Revision、Environment、Tenant、窗口、资源和期限；
3. 生产写操作、Deployment、Rollback、Traffic Shift、数据迁移和 Disposal 必须显式授权；
4. 紧急授权必须最小化 Scope、设置到期、记录原因并事后复核；
5. Authority 缺失、过期、冲突或撤销时必须 Fail Closed；
6. On-call 身份不自动具有所有生产权限；
7. Agent Token、Service Account 或自动化身份只能执行明确委托的动作。

## 8. 受控产物与关系

### 8.1 正式产物

| 代码 | 正式产物 | 状态模型 | 治理目的 |
|---|---|---|---|
| SDF | Service Definition | DOC | 固定服务价值、Scope、Owner、用户、依赖、环境、目标和退出条件 |
| SLO | SLI/SLO Register | DOC | 管理指标定义、计算、数据源、目标、窗口、错误预算、告警和处置 |
| RBP | Release and Rollback Plan | DOC | 固定 Release、环境、步骤、检查、观察、停止、回滚、责任和批准 |
| MAP | Monitoring and Alert Plan | DOC | 固定监控对象、信号、阈值、严重度、通知、响应、Runbook 和测试 |
| INR | Incident Record | CASE | 保留服务影响、时间线、响应、恢复、Evidence、根因状态和行动 |
| PBR | Problem Record | CASE | 管理趋势、业务影响、根因、已知错误、临时和永久处理 |
| OPO | Operational Observation | EVID | 固定运行事实、原始数据、预期差异、影响、可靠性和 Requirement |
| UFR | User Feedback Record | CASE | 保留反馈原文、用户情境、影响、Evidence、分类、追踪和处置 |
| PRR | Post-release Review | EXEC | 评审 Release 目标、实际结果、Incident、Feedback、Risk、Decision 和行动 |
| IBL | Improvement Backlog | DOC | 管理改进来源、问题或机会、预期结果、优先级、责任和关闭 Evidence |

十类产物必须保持独立身份、Revision、状态模型和模板。禁止合并为无类型的“运营台账”。

### 8.2 通用必填字段

十类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。E05 不拆分或改名公共字段。

### 8.3 容器与成员

1. SLO 和 IBL 是 DOC 容器，其成员必须有稳定 Member ID、Member Status、Source 和 History；
2. SDF、RBP 和 MAP 可以包含表格成员，但容器 DOC State 不等于成员结果；
3. OPO 每个实例固定一次观察范围和 Evidence，不以 Register Member Status 代替 EVID State；
4. UFR/INR/PBR 的 CASE State 与领域分类、严重度、影响或处置分离；
5. PRR 的 EXEC State 与 Review Conclusion 分离；
6. 删除成员必须通过新 Revision 和历史表示，禁止无痕移除。

### 8.4 受控关系

| 关系 | E05 使用 |
|---|---|
| derives-from | Service、SLO、Improvement 从 Need、Goal、Observation 或 Review 派生 |
| contains | Register、Plan 或 Backlog 包含独立成员 |
| refines | Service/Plan/Requirement 在不改变上位义务时细化 |
| extends | Service、Release 或 Improvement 增加独立能力 |
| depends-on | Service、Release、SLO 或 Recovery 依赖资产、数据或服务 |
| constrains | SLO、SLA、Policy、Risk、Capacity 或 Window 限制运行活动 |
| verified-by | Requirement/Criterion 由运行 Evidence 证明 |
| validated-by | Need/Intent/Goal 由用户和业务结果支持 |
| affected-by | Service、Release、Requirement 或 SLO 受 Incident/Problem/Change 影响 |
| supersedes | 新 Plan、Runbook 或 Service Definition 使旧资产退出当前集合 |
| replaces | 新 Service 或实现直接接替旧职责 |
| generated-by | Observation、Record、Report 由 Run、Tool 或 Process 生成 |
| observed-from | Learning、Issue、Risk 或 Requirement 候选来自运行 Observation/Feedback |
| released-in | Requirement、Design、Code、Configuration 或 Data 进入 Release |
| implemented-by | Requirement/Design 由可定位代码、配置或部署资产实现 |

禁止使用 `related-to`、“相关”或无方向链接作为正式关系。

### 8.5 最低关系链

```text
Service -depends-on-> Service/Component/Data
SLI/SLO -derives-from-> Goal/Quality Requirement
Release -contains-> Configuration Revision
Deployment -generated-by-> Approved Run
Observation -observed-from-> Service/Release
Incident -affected-by-> Release/Change
Problem -derives-from-> Incident/Trend
Requirement -verified-by-> Operational Evidence
Learning -observed-from-> Observation/Feedback/Incident
Improvement -derives-from-> Review/Learning
```

## 9. E05 治理生命周期

### 9.1 生命周期

```text
Applicability and Service Identification
  -> Service Definition
  -> SLI/SLO and Support Design
  -> Monitoring, Alert and Runbook Readiness
  -> Release and Rollback Planning
  -> Readiness Review and Approval
  -> Deployment and Traffic Control
  -> Observation and Service Operation
  -> Incident and Request Response
  -> Problem and Maintenance
  -> Post-release Review
  -> Learning and Improvement
  -> Change, Supersession or Retirement
```

### 9.2 Service Identification

1. 固定 Product、用户、消费方、价值、Service Boundary 和 Owner；
2. 识别依赖、环境、数据、安全、隐私、合规和支持边界；
3. 识别关键用户旅程和业务结果；
4. 建立 SDF 并关联上位 Product、Goal、PRD、Requirement 和 Architecture；
5. 无 Owner、Scope 或用户价值的技术组件不得被包装为正式 Service。

### 9.3 Service Objective 与支持设计

1. 为关键 Service 行为定义 SLI 及计算；
2. 为适用 SLI 定义 SLO、窗口、目标、错误预算和业务关联；
3. 明确 SLA/合同是否适用及有权 Owner；
4. 明确支持时间、On-call、升级、供应方和沟通；
5. 识别 Capacity、Continuity、Security、Privacy 和 Data Quality 目标；
6. 建立 SLO 和 MAP 固定 Revision。

### 9.4 Release Readiness

1. 固定 Release Configuration 和变更集合；
2. 验证 Acceptance、Security、Data、Architecture、Migration 和操作前置条件；
3. 建立 RBP，明确观察指标、停止、回滚和不可回滚边界；
4. 验证 Monitoring、Alert、Runbook、On-call 和沟通就绪；
5. 取得 C11/C12 和适用专项 Authority；
6. 未达 Ready 时禁止 Production Deployment。

### 9.5 Deployment 与观察

1. 执行前再次解析 Service、Release、Revision、Environment 和 Authority；
2. 按阶段控制流量、批次或目标；
3. 每阶段观察预定指标和用户影响；
4. 触发 Stop/Rollback 时停止扩大范围；
5. 记录命令、执行者、时间、结果、配置、日志和 Observation；
6. Tool Success 不得直接写入 Release Accepted。

### 9.6 Incident Response

1. 发现服务影响后创建或关联 INR；
2. 临时分级并指派 Incident Commander；
3. 优先保护人员、用户、数据和业务并恢复服务；
4. 固定事件时间线、决策、命令、沟通和 Evidence；
5. 涉及 Security、Privacy、Data 或 Legal 时立即启动专项流程；
6. 恢复后更新 Impact、Root Cause Status 和后续行动；
7. 关闭前执行独立复核。

### 9.7 Problem 与 Maintenance

1. 从重复 Incident、趋势、Defect 或异常创建 PBR；
2. 分离事实、假设、根因和未知项；
3. 记录临时措施、Known Error 和永久处理；
4. 软件修改必须进入 C04/C06/C11 并重新验证；
5. Maintenance 计划必须考虑资源、环境、工具、记录、测量和退役；
6. Problem 关闭不得仅依赖“未再发生”。

### 9.8 Review 与 Improvement

1. 每次适用 Release 在观察窗口后执行 PRR；
2. 对比目标与实际，纳入 Incident、Problem、Defect、Feedback、Cost 和 Risk；
3. 形成明确 Review Conclusion 和 Decision 引用；
4. 将行动登记 IBL，并映射 C01/C02/C04/C12；
5. 改进实施后重新验证效果；
6. 未进入受控产物的聊天结论不得视为改进闭环。

### 9.9 Retirement 与 Disposal

1. 形成退役 Scope、替代方案、用户沟通和时间表；
2. 识别调用方、数据、合同、密钥、证书、域名、供应方和运行依赖；
3. 验证迁移、归档、保留、Legal Hold 和恢复；
4. 分阶段停止流量、作业和资源；
5. 保留最小运行、批准、迁移和处置记录；
6. 验证旧 Service 不再被默认调用；
7. 退役完成后保持历史 Trace 和重新激活条件。

## 10. 适用性与治理过程

### 10.1 Applicability Decision

每个目标产品必须在 Discovery Ready 前：

1. 固定 Product、Scope、Revision、Decision Owner 和评价时间；
2. 逐项判断四个 E05 触发条件；
3. 每项记录 Yes/No/Unknown/Not Applicable 和 Evidence；
4. 任一 Unknown 映射 Pending；
5. 决定 Activation Status、Effective Time 和 Review Trigger；
6. 识别需实例化的十类产物；
7. 通过 C12 Review；
8. 纳入 C11 Baseline。

### 10.2 Service Onboarding

1. 创建 SDF；
2. 建立 Owner、支持和升级责任；
3. 识别用户、价值、业务结果、Scope 和 Non-scope；
4. 建立依赖、环境、数据和安全分类；
5. 建立 SLI/SLO 与业务结果映射；
6. 建立 MAP、Runbook 和 On-call；
7. 验证 Release/Rollback 能力；
8. 执行 Operational Readiness Review；
9. 进入 Production 前形成 C12 Gate Decision。

### 10.3 SLI/SLO 管理

1. 明确 SLI Event/Population、Good/Valid Event 和排除规则；
2. 固定计算公式、数据源、采样、聚合、时区和延迟；
3. 定义 SLO Target、Window 和业务理由；
4. 定义 Error Budget 计算、消费政策和行动；
5. 定义告警条件、响应和升级；
6. 验证数据完整性和查询可重复性；
7. 周期评审目标的可用性和业务关联；
8. 变更 SLI/SLO 必须创建新 Revision，禁止重写历史窗口。

### 10.4 Release and Rollback Planning

1. 固定 Release ID 和 Configuration Revision；
2. 列出代码、配置、数据、模型、Prompt、Feature Flag 和文档版本；
3. 明确 Environment、Tenant、Region、Window 和流量阶段；
4. 完成前置检查和 Authority；
5. 定义每阶段命令、观察、成功、停止和超时；
6. 定义 Rollback Target、数据兼容、触发者和步骤；
7. 定义不能回滚的范围和替代恢复；
8. 完成独立 Review 和演练；
9. 绑定 C09 Run、C11 Change/Baseline 和 C12 Gate。

### 10.5 Monitoring and Alert Management

1. 以用户旅程、服务目标、依赖和关键风险确定监控对象；
2. 每个 Signal 固定定义、来源、窗口、延迟、完整性和 Owner；
3. 每个 Alert 固定阈值、严重度、去重、抑制、通知和响应时限；
4. Alert 必须引用 Runbook 和升级路径；
5. 周期测试 Alert 能否生成、送达、确认和升级；
6. 控制误报、漏报和告警疲劳；
7. 监控失效必须进入 Incident/Risk，不得以零告警替代健康判断；
8. Dashboard 变更必须固定 Revision。

### 10.6 Incident Management

1. 创建 INR 并固定 Service、Release、Environment 和开始时间；
2. 记录发现来源、临时 Severity 和用户影响；
3. 建立 Incident Commander、响应角色和沟通渠道；
4. 按时间顺序记录事实、假设、Decision、Command 和结果；
5. 执行 Containment、Recovery 和 Verification；
6. 识别 Security/Privacy/Data/Legal 分支；
7. 更新 Impact、恢复时间、Evidence 和后续行动；
8. 重复或系统性原因创建 PBR；
9. 关闭必须满足恢复、沟通、记录、行动分派和独立复核条件；
10. 重大事故执行单独 Review。

### 10.7 Problem Management

1. 从 Incident 集合、趋势或主动分析识别 Problem；
2. 固定 Problem Statement 和业务影响；
3. 分离 Root Cause Hypothesis、Evidence 和 Confirmed Cause；
4. 记录 Known Error、Workaround 和限制；
5. 永久处理进入 Requirement/Design/Change；
6. 验证处理前后指标和复发情况；
7. 关闭条件包含根因确认或有权接受 Unknown、永久处理验证、文档更新和残余 Risk；
8. Root Cause 未知时不得伪造“人为失误”结论。

### 10.8 Feedback and Observation

1. OPO 固定 Service、Release、环境、时间、Signal 和原始数据；
2. UFR 保留原始反馈、用户/群体、渠道、时间和使用情境；
3. 记录可靠性、样本限制、选择偏差和重复项；
4. 分类为 Incident、Problem、Defect、Need、Requirement、Support Request、Risk 或信息；
5. 分类不能改变原始记录；
6. 对高影响反馈执行 Evidence 补充和反向查询；
7. 处置结果和拒绝理由必须可审计；
8. PII、敏感和合同信息按 E02/E04 处理。

### 10.9 Post-release Review and Improvement

1. 固定 Release、观察窗口、目标和比较基线；
2. 汇总 SLO、业务指标、护栏、Incident、Defect、Feedback、Cost 和 Capacity；
3. 识别预期与实际差异及 Evidence 限制；
4. 评价剩余 Risk 和未完成问题；
5. 形成 Proceed、Proceed with Conditions、Rollback、Remediate、Escalate 或 Inconclusive；
6. 每项行动有 Owner、Due、Priority 和 Trace；
7. 运行学习映射到 C01/C02/C04/C12；
8. 改进行动关闭必须有 Evidence；
9. Review Conclusion 不自动构成 C12 Gate 或 Risk Acceptance。

### 10.10 Maintenance and Disposal

1. 建立 Maintenance Strategy、Scope、资源、工具、环境和记录；
2. 评估 Problem/Modification、可行性、影响和回归范围；
3. 修改前固定 Baseline，修改后执行 Verification/Validation；
4. 维护类型、协议、测量和记录必须明确；
5. Disposal 前通知用户和依赖方；
6. Archive、Retention、Data Handling、Access Revocation 和资源终止受控；
7. Disposal 后验证残留调用、数据、密钥、计费和依赖；
8. 不可逆处置必须有 Authority、Dry-run、Stop 和 Evidence。

## 11. 产品运营与服务管理控制

### 11.1 Service Definition

1. Service 必须有稳定 Service ID；
2. Service Value 必须关联用户或消费方结果；
3. Scope 必须列 In Scope、Out of Scope、Interface 和 Dependency；
4. Owner、Support Time、On-call 和 Escalation 必须明确；
5. Environment、Tenant、Region、Data 和 Security Classification 必须明确；
6. 质量目标必须可测量；
7. Exit Criteria 和 Retirement Trigger 必须明确；
8. SDF 变化必须执行影响分析。

### 11.2 SLI/SLO

1. SLI 名称必须唯一并能复算；
2. 分子、分母、排除、时区、窗口和数据延迟必须明确；
3. SLO 目标必须有业务理由和 Owner；
4. 无数据和无有效数据必须显式区分；
5. Error Budget 政策必须定义允许和禁止动作；
6. SLO 变更不得重写历史结果；
7. 未满足 SLO 必须触发 Review、Risk 或 Improvement；
8. SLO 达标不得自动关闭 Incident 或接受剩余 Risk。

### 11.3 Release、Deployment 与 Traffic

1. Release Configuration 必须精确到不可变 Revision；
2. Deployment Target 禁止使用未解析的 `latest`、`head`、`all`、通配环境或隐式租户；
3. 灰度必须定义批次、流量、持续时间和每阶段 Criteria；
4. Feature Flag 必须有 Owner、默认值、到期和回滚；
5. 配置和数据迁移必须纳入 RBP；
6. 每次写操作必须有幂等、重复执行或失败恢复说明；
7. 生产执行不得依赖交互式默认值；
8. 执行失败不得自动扩大权限或跳过阶段。

### 11.4 Rollback、Recovery 与 Continuity

1. Rollback Target 必须是已知可接受配置；
2. 回滚前必须评估数据向前/向后兼容；
3. 回滚后验证服务、数据、队列、缓存、外部依赖和用户状态；
4. 无法回滚时必须有 Forward Fix、Failover 或隔离方案；
5. Recovery Point、Recovery Time 和业务可接受能力必须可验证；
6. 恢复测试不得直接在未授权生产范围执行；
7. 备份存在不证明可恢复；恢复成功不证明数据 Current/Complete；
8. Continuity 决定需由有权业务和技术角色共同处理。

### 11.5 Monitoring 与 Alert

1. 监控覆盖用户旅程、服务边界、关键依赖和业务结果；
2. Signal 必须有来源、Revision、查询和可靠性；
3. Alert 必须可行动，具有 Owner、Severity、Response Time 和 Runbook；
4. 告警规则必须测试；
5. 抑制、静默和维护窗口必须有 Scope、时间、批准和审计；
6. 监控管道本身必须被监控；
7. 日志、指标、Trace 和事件的时间源与 Correlation 必须一致；
8. 监控不得记录不必要的 Secret、Credential 或 PII。

### 11.6 Incident

1. 事故响应以用户、人员、数据和业务保护优先；
2. 时间线只记录事实、标记假设并保留更正；
3. 所有高风险命令必须关联执行者、Authority 和 Run；
4. 用户影响必须包含对象、范围、时间和表现；
5. 恢复时间与事故关闭时间必须分离；
6. 沟通内容必须区分已知事实、未知项和下一更新时间；
7. 重大事故不得由同一 Agent 或同一执行者独立关闭；
8. Incident Record 禁止覆盖 Security/Privacy/Legal 专项记录。

### 11.7 Problem 与 Known Error

1. Problem 必须引用 Incident、Trend 或主动分析来源；
2. 根因分析必须保留候选假设和排除 Evidence；
3. Known Error 必须记录触发条件、影响、Workaround 和限制；
4. 临时措施必须有到期和永久处理 Owner；
5. 永久处理必须通过 Requirement、Design、Change 和 Verification；
6. Problem 关闭必须有 Criteria 和 Evidence；
7. 复发必须触发 Reopened 或新 Problem 关系；
8. 无 Incident 也可以基于趋势创建 Problem。

### 11.8 Operational Observation

1. 每个 OPO 固定 Service、Release、环境、时间和数据；
2. 原始数据位置、查询、采样、聚合和完整性必须可复核；
3. 预期值必须引用 SLO、Metric、Requirement 或 Review Criteria；
4. Observation Assessment 必须记录不确定性；
5. Anomalous 不自动等于 Incident，必须执行影响判断；
6. 运行 Evidence 用于 `verified-by` 时必须满足 C05；
7. 观察结果必须反向关联受影响 Requirement；
8. Evidence 失效必须触发受影响 Decision/Gate 复评。

### 11.9 User Feedback

1. 保留原始反馈，不用摘要覆盖原文；
2. 记录用户/群体、渠道、时间、产品版本和使用情境；
3. 匿名化、Consent、Access 和 Retention 受 E02/E04 约束；
4. 情绪、频率和严重度必须分别评价；
5. 重复反馈必须保留来源并建立 Duplicate 指向；
6. Declined/Deferred 必须记录理由和复核条件；
7. Feedback 不得由 Agent 自动转为已批准 Requirement；
8. 反馈处理状态必须可追踪。

### 11.10 Post-release Review

1. PRR 必须在预定义观察窗口后执行；
2. 窗口未结束或数据无效时不得判定最终成功；
3. 目标、实际、差异和统计限制必须并列；
4. Incident、Defect、Feedback、Risk 和 EWR 必须完整列出；
5. 结论必须有 Criteria、Evidence、Reviewer 和 Decision 引用；
6. 条件结论必须有 Owner、Due 和 Expiry；
7. 行动必须进入 IBL 或上游受控产物；
8. PRR Accepted 只能由授权人决定。

### 11.11 Improvement Backlog

1. 每个 Improvement 有稳定 ID、Source 和预期结果；
2. Priority 必须说明价值、风险、紧迫性和成本依据；
3. 成员状态与容器 DOC State 分离；
4. 进入实施时必须映射 Initiative/Requirement/Change；
5. 关闭必须引用结果 Evidence；
6. Deferred 必须有复核触发器；
7. 重复项不得无痕删除；
8. Backlog 数量下降不证明质量改善。

### 11.12 命令与工具控制

运行命令必须包含：

| 控制项 | 最低要求 |
|---|---|
| Operation | observe、query、deploy、traffic-shift、rollback、recover、restart、scale、migrate、retire 等明确动作 |
| Tool | Tool Name、Version、Digest、Plugin/Connector Revision |
| Target | Service、Release、Resource、Revision、Environment、Tenant、Region、Partition |
| Input | RBP、MAP、Runbook、Manifest、Query、Policy 的受控引用 |
| Authority | Requester、Operator、Approval、Scope、有效期 |
| Mode | read-only、dry-run、write；默认 read-only/dry-run |
| Limits | Traffic、Batch、Record、Byte、Concurrency、Timeout、Rate、Cost |
| Output | Location、Classification、Redaction、Retention、Integrity |
| Safety | Preconditions、Stop Conditions、Snapshot、Transaction、Rollback |
| Evidence | Run ID、Command Hash、Log、Result、Observation、Reviewer |

强制规则：

1. Secret 只能使用 Secret Reference；
2. Write 前必须 Dry-run；不能 Dry-run 时记录理由、替代验证和批准；
3. 生产 Target 必须解析为精确对象；
4. 部署、回滚、恢复、迁移和退役必须有显式 Authority；
5. 每阶段执行后先验证再扩大 Scope；
6. Stop Condition 成立时禁止继续；
7. Exit Code 只表示进程结果，不表示 Deployment、Rollback 或 Governance Pass；
8. 重试不得扩大 Scope、权限或资源上限；
9. 命令必须绑定 C09 Run、RBP/Runbook 和 OPO/Evidence；
10. 高风险输出必须由独立 Reviewer 复核。

### 11.13 Audit、Time 与 Communication

1. 所有运行记录使用统一时间源并保留时区；
2. Correlation ID 贯穿 Alert、Incident、Command、Log、Observation 和 Review；
3. 审计记录包含 Actor、Authority、Action、Target、Before/After、Time、Result 和 Evidence；
4. 外部沟通必须有 Audience、Approver、事实边界和更新时间；
5. 更正沟通不得覆盖原消息；
6. 日志访问和写入权限应分离；
7. Audit Query 必须只读；
8. 记录保留按 E04 RCS/RTS，不默认永久；
9. 事件日志不得保存不必要 Secret/PII；
10. 审计缺口进入 Risk/Incident。

### 11.14 Fail Closed

以下情形必须 Fail Closed：

- Service、Release、Revision、Environment 或 Tenant 未解析；
- Authority 缺失、过期、冲突或撤销；
- RBP/Runbook Revision 不匹配；
- Rollback Target 或数据兼容 Unknown；
- Observation Signal 无数据且发布需要该信号判定；
- 监控管道失效且无替代观察；
- 高风险 Command 超出批准 Scope；
- Security/Privacy/Data 影响未知且动作会扩大损害；
- Audit Log 无法记录高风险动作；
- Output Redaction 或 Secret 保护失败；
- Stop Condition 成立；
- Agent 尝试自批。

Fail Closed 后必须记录原因、影响、临时控制、Owner 和恢复条件。

## 12. 状态模型与转换

### 12.1 DOC State

SDF、SLO、RBP、MAP 和 IBL 使用公共 DOC State：

```text
Draft -> In Review -> Approved -> Baselined -> Superseded/Retired
             -> Changes Required -> Draft
             -> Rejected
```

### 12.2 CASE State

INR、PBR 和 UFR 使用公共 CASE State：

```text
Open -> In Progress -> Resolved -> Closed
          <-> Blocked          Closed -> Reopened -> In Progress
          -> Cancelled
```

Incident 恢复可以使处置进入 Resolved，但关闭必须完成复核、沟通、记录和行动分派。UFR 的 Feedback Disposition 不替代 CASE State。

### 12.3 EVID State

OPO 使用公共 EVID State：

```text
Planned -> Collected -> Under Review -> Accepted/Rejected
                                  Accepted -> Invalidated
```

Accepted 只表示在固定 Criteria 下可作为 Evidence 使用，不表示 Service 健康、Requirement 满足或 Release 成功。

### 12.4 EXEC State

PRR 使用公共 EXEC State：

```text
Planned -> Ready -> Running -> Completed -> Accepted/Rejected
                Running <-> Blocked
                Running -> Failed/Cancelled
```

Completed 表示评审执行结束，不能替代授权人的 Accepted。

### 12.5 Activation Status

```text
Not Evaluated -> Pending -> Inactive/Conditionally Active/Active
Inactive -> Pending/Active
Conditionally Active -> Active/Inactive/Retiring
Active -> Retiring
Retiring -> Retired
Retired -> Pending/Active
```

Activation Status 与资产状态分离。当前仓库为 Inactive，E05 文档为 Draft。

### 12.6 SLO、Severity 与领域 Result

1. SLO Evaluation、Release Readiness、Deployment Result、Rollback Result、Incident Severity、Incident Impact、Root Cause Status、Observation Assessment、Feedback Disposition 和 Review Conclusion 是字段值；
2. Severity 变化必须保留原值、时间、依据和决定者；
3. SLO Evaluation 必须固定窗口和数据 Revision；
4. Deployment/Rollback Result 不改变 RBP DOC State；
5. Review Conclusion 不改变 PRR EXEC State；
6. Tool Success 禁止自动写入 Met、Ready、Completed、Recovered 或 Confirmed。

### 12.7 IBL Member Status

IBL 成员使用：

```text
Proposed -> Active -> Deprecated -> Retired
Proposed -> Rejected
```

成员进入实际执行后必须映射适用 CASE/DOC/Change，不得以 Active 表示工作已完成。

### 12.8 状态转换最低字段

每次转换必须记录：

- Object ID/Revision；
- Previous State/Value；
- New State/Value；
- Trigger；
- Criteria；
- Evidence；
- Requested By；
- Approved By；
- Effective Time；
- Expiry/Review Time；
- Affected Service/Release/User；
- History Reference。

Approved、Accepted、Baselined、Risk Acceptance、Waiver 和重大 Incident Closure 只能由授权的人类角色决定。

## 13. 正式产物最低内容

### 13.1 通用结构

除 VC-PPG-COM-002 第 3 章和第 3.1 节外，每类正式产物还必须包含适用的运营边界、状态转换记录、类型专属字段、Risk/Exception/Change 引用、Verification/Evidence 引用和标准映射。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义。

### 13.2 SDF Service Definition

至少包含 Service ID、服务对象、价值、Scope、Owner、用户、依赖、接口、环境、区域/租户、支持时间、On-call、升级、质量目标、业务结果、数据与安全分类、Continuity、供应方、退出条件、Retirement Trigger 和 Trace。

### 13.3 SLO SLI/SLO Register

每个成员至少包含 SLI ID、名称、定义、Event/Population、分子、分母、排除、计算、数据源、查询 Revision、聚合、时区、数据延迟、SLO 目标、窗口、业务依据、Error Budget、Owner、Alert、处置、Last/Next Review、Member Status 和 History。

### 13.4 RBP Release and Rollback Plan

至少包含 Release ID、Scope、Configuration Revision、包含版本、Environment/Tenant/Region、窗口、流量阶段、前置检查、Authority、命令引用、每阶段观察指标、成功 Criteria、停止与回滚条件、Rollback Target、数据兼容、回滚步骤、替代恢复、沟通、责任人、批准、演练和 Evidence。

### 13.5 MAP Monitoring and Alert Plan

至少包含监控对象、用户旅程、指标或事件、定义、数据源、查询 Revision、窗口、阈值、严重度、去重/抑制、通知、响应时限、升级、Runbook、Owner、监控管道健康、测试周期、Last Test、数据分类、保留和 Evidence。

### 13.6 INR Incident Record

至少包含 Incident ID、事件时间线、Service、Release/Version、Environment、Severity、用户影响、发现来源、Incident Commander、响应角色、响应动作、Command/Decision、沟通、Containment、恢复时间、Impact Status、Evidence、责任人、Root Cause Status、Security/Privacy/Data 分支、后续行动、关闭 Criteria、Reviewer 和 History。

### 13.7 PBR Problem Record

至少包含 Problem ID、关联 Incident/Trend/Defect、Problem 描述、业务影响、候选假设、根因分析、Confirmed Cause、Known Error、Workaround、临时措施到期、永久处理、Requirement/Change、责任人、剩余 Risk、验证、复发检查、关闭条件和 History。

### 13.8 OPO Operational Observation

至少包含 Observation ID、Service、Release、观察时间、Environment、窗口、指标或行为、原始数据位置、查询/工具 Revision、采样/聚合、预期、实际、差异、影响、可靠性、限制、Observation Assessment、关联 Requirement/SLO、Evidence Integrity、Reviewer 和失效条件。

### 13.9 UFR User Feedback Record

至少包含 Feedback ID、用户或群体、渠道、时间、Service/Release、原始反馈、语言、使用情境、影响、Evidence、分类、重复指向、情绪/频率/严重度、关联 Need/Problem/Requirement、隐私与访问、Feedback Disposition、理由、责任人、复核触发和 History。

### 13.10 PRR Post-release Review

至少包含 Review ID、Release、观察周期、目标指标、实际结果、统计限制、SLO、业务结果、护栏、Defect、Incident、Problem、用户反馈、成本/容量、剩余 Risk、EWR、结论、Criteria、Decision、行动、Owner/Due、Reviewer、Evidence 和接受记录。

### 13.11 IBL Improvement Backlog

每个成员至少包含 Improvement ID、来源、问题或机会、预期结果、业务/风险价值、Priority、估算、责任人、目标时间、关联 Initiative/Need/Requirement/Change、依赖、Member Status、延期/拒绝理由、复核触发、关闭 Criteria、关闭 Evidence 和 History。

## 14. 质量要求

### 14.1 总体质量

E05 实例必须满足：

- Complete：身份、字段、Owner、Scope、状态、关系和 Evidence 完整；
- Correct：结果与原始数据、时间窗口、Criteria 和 Source 一致；
- Consistent：Service、Release、Version、Environment、Time 和术语一致；
- Current：Plan、Runbook、SLO、Contact 和 Dependency 已复核；
- Traceable：可查询 Need 至 Release 至 Observation 至 Improvement；
- Controlled：Authority、Change、Command、Access、Retention 和 History 受控；
- Resilient：失败、回滚、恢复、连续性和退役边界明确；
- Actionable：Alert、Incident、Problem、Feedback 和 Improvement 有责任与时限。

### 14.2 发布质量

1. 100% Production Release 有固定 Configuration Revision；
2. 100% 适用 Release 有观察指标、停止和回滚条件；
3. 高风险 Deployment 100% 有独立批准；
4. 未解析 Target、Authority 或 Rollback 的生产写操作为 0；
5. 每阶段扩大流量前 100% 完成 Criteria 检查；
6. Tool Success 自动判定 Release Accepted 的次数为 0。

### 14.3 服务目标质量

1. 100% 关键 SLI 可复算；
2. 100% SLO 有窗口、目标、Owner 和业务关联；
3. No Data/Invalid Data 被判 Met 的次数为 0；
4. SLO 变更重写历史窗口的次数为 0；
5. Error Budget 无政策或无 Owner 的关键 Service 为 0；
6. SLO 达标自动推导业务成功的次数为 0。

### 14.4 Incident 与 Problem 质量

1. SEV-1/SEV-2 100% 有 Incident Commander、时间线、影响、沟通和独立关闭复核；
2. 事故恢复时间和关闭时间 100% 分离；
3. 重大运行命令 100% 有 Authority 和 Run；
4. 重复 Incident 100% 完成 Problem 适用性判断；
5. Root Cause 无 Evidence 却标 Confirmed 的数量为 0；
6. Problem 永久处理 100% 关联 Requirement/Change/Verification。

### 14.5 Observation、Feedback 与 Improvement 质量

1. OPO 100% 关联 Service、Release、Environment 和时间；
2. 运行 Observation 至受影响 Requirement 的可追踪覆盖率为 100%；
3. UFR 原始反馈保留率为 100%；
4. 被接受学习进入 C01/C02/C04/C12 的覆盖率为 100%；
5. IBL 关闭项 100% 有结果 Evidence；
6. 单条反馈自动转为已批准 Requirement 的次数为 0。

### 14.6 质量判定规则

1. 任一关键控制 Fail 时总体不得判 Pass；
2. Unknown、No Data、Invalid Data 或 Not Evaluated 不得计为 Pass；
3. 采样必须记录 Population、Sample、Method、Seed 和 Limitation；
4. Dashboard Green、零告警或零事故不证明服务健康；
5. 指标目标必须有业务依据和 Owner；
6. 指标改善不得忽略护栏或用户群差异；
7. 结论必须固定时间窗口、Service 和 Release Revision；
8. Agent 或 Tool 只能提出候选结论。

## 15. 验证、评审与 Gate

### 15.1 Verification 层级

| 层级 | 验证对象 | 最低验证 |
|---|---|---|
| V1 | Schema/Format | 必填字段、枚举、引用、语法和 State |
| V2 | Content | Service、SLO、Criteria、数据和业务依据 |
| V3 | Relationship | Need、Requirement、Release、Observation、Incident 和 Improvement |
| V4 | Control | Authority、Change、Access、Retention、Audit 和职责分离 |
| V5 | Operation | Deploy、Traffic、Rollback、Recover、Alert 和 Runbook |
| V6 | Outcome | 用户、业务、可靠性、风险和学习闭环 |

### 15.2 最低评审

1. SDF：Service Owner + Product Owner + Architecture/Operations；
2. SLO：Service Owner + SRE/Operations + Business Owner；
3. RBP：Release Manager + Operator + Configuration Manager + 适用专项 Reviewer；
4. MAP：SRE/Operations + Service Owner + On-call Representative；
5. INR：Incident Commander 之外的 Reviewer；重大事故增加业务与专项 Reviewer；
6. PBR：Problem Owner + Domain/Engineering Reviewer；
7. OPO：数据来源 Owner + 独立 Reviewer；
8. UFR：Feedback Steward + Product Owner，涉及 PII 时增加 Privacy Reviewer；
9. PRR：Release Manager 之外的授权 Reviewer；
10. IBL：Product/Service Owner + 受影响治理域 Owner。

### 15.3 Operational Readiness Gate 输入

至少包含：

- Applicability Decision；
- SDF、SLO、RBP、MAP 固定 Revision；
- On-call、Escalation 和 Runbook；
- C05 Verification/Validation/Acceptance；
- C10 Trace/Impact Query；
- C11 Change/Baseline/Release Configuration；
- E01 Capacity/Resilience；
- E02 Security/Privacy/Compliance；
- E03 Data Quality/Migration；
- E04 Access/Retention/Knowledge Freshness；
- Open Risk、EWR 和 RAR；
- Rollback/Recovery Test Evidence。

### 15.4 阻断条件

以下任一成立必须阻断 Production Deployment 或扩大流量：

- Service/Release/Environment/Authority 未解析；
- SDF、SLO、RBP 或 MAP 缺失或非适用批准 Revision；
- 关键 Verification/Validation 未完成；
- Rollback/Recovery Unknown 且无批准替代；
- Monitoring/Alert/On-call 未就绪；
- Stop Condition 已满足；
- Critical Risk 未处理且无有权 RAR；
- Security/Privacy/Data Gate 未通过；
- 关键 Evidence 已失效；
- Agent 尝试自批。

### 15.5 Incident Closure Gate

至少满足：

1. 用户影响已 Recovered 或有批准的明确剩余影响；
2. 时间线、命令、Decision、沟通和 Evidence 完整；
3. Security/Privacy/Data/Legal 分支已交接；
4. Root Cause Status 和 Unknown 明确；
5. Problem/Defect/Risk/Improvement 已建立；
6. Owner 和 Due 明确；
7. 独立 Reviewer 完成；
8. 关闭不构成自动 Risk Acceptance。

### 15.6 Acceptance 边界

1. E05 Verification Pass 不表示产品满足全部用户需求；
2. SLO Met 不表示 SLA 无违约或业务成功；
3. Release Accepted 不表示零缺陷或零风险；
4. Incident Closed 不表示 Problem 已解决；
5. Rollback Completed 不表示数据完整或所有用户已恢复；
6. PRR Completed 不表示结论被接受；
7. Gate Decision 只能由 C12 有权角色作出。

## 16. 追踪、审计与指标

### 16.1 必须追踪

至少必须追踪：

- Service -> Product/Goal/User；
- Service -> Dependency/Environment/Owner；
- SLI/SLO -> Goal/Requirement/Data Source；
- Release -> Change/Baseline/Configuration；
- Deployment -> Release/Environment/Run；
- Observation -> Service/Release/Requirement；
- Alert -> Signal/Runbook/Incident；
- Incident -> Release/Change/User Impact/Evidence；
- Problem -> Incident/Defect/Requirement；
- Feedback -> User Context/Need/Problem/Requirement；
- PRR -> Release/Metric/Incident/Feedback/Risk；
- Improvement -> Source/Initiative/Requirement/Change/Evidence。

### 16.2 审计事件

必须记录：

- Service Create/Change/Retire；
- SLI/SLO Create/Change/Evaluate；
- Monitoring/Alert Rule Create/Test/Suppress；
- Release Approve/Deploy/Traffic Shift/Stop/Rollback；
- Incident Declare/Reclassify/Respond/Recover/Close/Reopen；
- Problem Create/Analyze/Known Error/Resolve/Close；
- Observation Collect/Review/Invalidate；
- Feedback Capture/Classify/Dispose；
- Post-release Review/Accept/Reject；
- Improvement Create/Prioritize/Map/Close；
- Authority Grant/Revoke/Emergency Use；
- Audit/Corrective Action。

### 16.3 审计记录字段

每个事件至少包含 Event ID、Actor/Identity、Role/Authority、Operation、Target ID/Revision、Service/Release、Environment/Tenant/Region、Timestamp/Timezone、Run/Correlation ID、Before/After、Result、Error/Stop、Evidence、Access Classification 和 Retention Rule。

### 16.4 指标

| 指标 | 计算边界 | 禁止推论 |
|---|---|---|
| SLO Attainment | 符合 SLO 的有效窗口 / 已评价窗口 | 不证明业务成功 |
| Error Budget Consumption | 不符合事件量 / 允许额度 | 不自动批准或阻止发布 |
| Change Failure Rate | 造成回滚、Incident 或修复的发布 / 已部署发布 | 不单独定位根因 |
| Deployment Success | 达到执行 Criteria 的 Deployment / 已执行 | 不证明用户结果 |
| Mean Time to Detect | 影响开始至可靠发现的时间 | 不证明监控完整 |
| Mean Time to Recover | 影响开始至恢复 Criteria 的时间 | 不等于 Incident Closure |
| Incident Recurrence | 相同已确认原因的重复事故 / 已关闭事故 | 零不证明根因正确 |
| Alert Actionability | 经复核需行动的 Alert / 抽样 Alert | 不证明无漏报 |
| Observation Trace Coverage | 关联 Requirement 的 OPO / 应关联 OPO | 不证明 Requirement 满足 |
| Feedback Closure | 有受控处置的 UFR / 到期 UFR | 不证明用户满意 |
| Improvement Effectiveness | 达到预期结果的已验证改进 / 已验证改进 | 不证明无副作用 |

### 16.5 Evidence 失效

1. 数据源、查询、Release、Environment、Criteria 或工具变化可以使 OPO 失效；
2. 失效必须标记 Invalidated 并反向查询 SLO、PRR、Decision 和 Gate；
3. 禁止删除原 Evidence 隐藏失效；
4. 失效范围未知时相关结论回到 Not Evaluated/Inconclusive；
5. 新 Evidence 不得无痕覆盖旧时间窗口。

## 17. 裁剪、激活、停用与退役

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。E05 的 Active、Conditionally Active、Retiring、Retired、Inactive、Pending、Not Evaluated 必须按统一状态语义解析；Trigger、Unknown 或冲突不得被局部规则降级。

### 17.0 Task Profile 驱动的激活

E05 在 DS-04 运行中产品处置、生产发布、Deploy/Operations Change Surface、SLO/监控变化、Incident/Problem、发布后观察或运营反馈闭环成立时激活。无生产或服务运营范围的原型/离线任务可以保持未激活。

稳定 SDF、SLO、RBP、MAP 可以 `Reference`；INR、PBR、OPO、UFR、PRR 按实际事件生成；IBL 只接收具有来源、Owner 和关闭 Evidence 的改进项。Emergency 处置后必须补齐时间线、实际动作、恢复验证、剩余风险和 Post-release Review。

### 17.1 P2 不可裁剪项

P2 不允许删除：

- E05 Applicability Decision；
- 十类正式产物定义和模板；
- 每次发布的观察指标、停止和回滚条件；
- Incident、Problem、Defect、Risk、Change、Request 分类；
- Observation 至 Release 和 Requirement 的追踪；
- 学习进入 C01/C02/C04/C12 的闭环；
- 可测量 SLI/SLO 与业务结果关联；
- Authority 和职责分离；
- 命令 Tool、Target、Revision、Dry-run、Limit、Stop、Rollback 和 Evidence；
- 状态轴和领域 Result 分离；
- 国际标准映射。

### 17.2 可裁剪实现

满足风险和 Evidence 要求时可以：

- 用 Markdown/Git 实现十类产物；
- 用同一 ITSM/Issue 系统承载 INR、PBR、UFR，但保持类型身份；
- 用人工 On-call 和升级；
- 以日志和指标平台组合实现 Monitoring；
- 对低流量 Service 使用较长 SLO 窗口；
- 对低风险发布采用单批次但仍保留 Stop/Rollback；
- 不建立独立 NOC 或专用 SRE 团队。

裁剪不得改变最低字段、状态、Authority、关系、阻断条件和 Evidence。

### 17.3 激活

1. 当前仓库为 Inactive；
2. 新目标产品任一触发条件 Yes 即激活；
3. 激活必须确定 Scope、Owner、Effective Time、产物实例和 Gate；
4. Pending 转 Active 必须关闭关键 Unknown；
5. Activation Decision 纳入 C11 Baseline；
6. 激活不等于 E05 文档 Approved。

### 17.4 条件激活

Conditionally Active 必须记录 Scope、未完成项、临时控制、禁止动作、Owner、Due、Expiry、Review Trigger 和 Exit Criteria。到期未完成不得自动延长。

### 17.5 停用与退役

1. Retiring 期间继续维持服务、告警、Incident、数据、访问、保留和沟通；
2. 活跃 Consumer 必须迁移或批准关闭；
3. SLO/SLA 和支持承诺必须有终止处理；
4. 数据、密钥、证书、域名、供应方和计费必须受控处置；
5. Historical Incident、Problem、Release 和 Evidence 按 E04 保留；
6. Retired 不表示允许删除历史；
7. 重新激活必须重做 Applicability、Readiness、Security、Data 和 Recovery 检查。

## 18. 与其他规范接口

### 18.1 C01 至 C03

1. SDF 引用 C01 Product、Need、Intent 和 Goal；
2. SLO 关联 C02 Success Metric，但不替代业务指标计划；
3. Incident/Feedback/Learning 可以产生 C01 Evidence 或 Need 候选；
4. Improvement 映射 C02 Initiative/Risk/Dependency；
5. Release Scope 引用 C03 PRD、Feature 和 Target Release；
6. 运行发现的 Non-goal 冲突进入 C03/C11 变更。

### 18.2 C04 至 C06

1. OPO 必须关联受影响 C04 Requirement；
2. 运行 Evidence 作为 Verification 时适用 C05；
3. 用户和业务结果作为 Validation 时适用 C05；
4. Incident/Problem 永久处理进入 C04 Requirement 和 C06 Design；
5. Rollback/Failure Mode/Recovery 由 C06 设计并由 E05 执行；
6. 运行结果不能原位修改 Requirement。

### 18.3 C07 至 C09

1. C07 决定 Human/Agent Authority；
2. Release、Rollback、Incident Command 和 Closure 必须有授权角色；
3. C08 Context 固定运行输入、Runbook、Plan 和 Policy Revision；
4. C09 记录 Agent Run、Command、Tool、Target、Output 和 Evidence；
5. E05 命令禁止使用未解析 Target 和隐式默认；
6. Agent 不得自批运行决定。

### 18.4 C10 至 C12

1. C10 提供关系、追踪、影响查询和 Orphan 检查；
2. E05 使用 `affected-by`、`generated-by`、`observed-from`、`released-in` 和其他公共关系；
3. C11 管理 Change、Baseline、Release Configuration、Snapshot 和 Recovery Point；
4. RBP 不替代 C11；
5. C12 管理 Readiness Gate、Release Gate、Risk Acceptance、Waiver 和 Product Health；
6. Incident Closure 和 PRR Conclusion 不替代 C12 Gate；
7. 运行 Evidence 失效必须反向查询既有 Decision/Gate。

### 18.5 E01 至 E04

1. E01 提供 Architecture、Capacity、Resilience、Dependency 和 Conformance；
2. E02 提供 Security、Privacy、Compliance、Vulnerability 和事件通知控制；
3. E03 提供 Data Contract、Quality、Lineage、Migration、Retention 和 AI Data 运行控制；
4. E04 管理 E05 Record/Knowledge 的 Source、Access、Retention、Freshness、Supersession 和检索；
5. Security/Privacy/Data Incident 必须同时进入适用专项流程；
6. E05 恢复运行，E04 验证恢复 Record 和 Knowledge 的完整性与可用性；
7. 多个扩展冲突时采用更严格适用控制并建立 Decision。

## 19. 参考标准治理

### 19.1 参考层级

| 层级 | 标准 | E05 用途 |
|---|---|---|
| R1 | ISO/IEC 20000-1:2018 + Amd 1:2024 | 服务管理体系、服务组合、服务级别、发布、Incident、Problem、可用性、连续性、监测和改进 |
| R1 | ISO/IEC/IEEE 12207:2026 | 软件生命周期、技术管理、Transition、Operation、Maintenance 和 Disposal |
| R1 | ISO/IEC/IEEE 14764:2022 | 软件 Maintenance、Problem/Modification Analysis、维护计划和 Disposal |
| R1 | ISO 9001:2015 + Amd 1:2024 | 质量管理、运行、绩效评价、不符合和持续改进 |
| R1 | ISO 31000:2018 | Risk 原则、框架、识别、分析、评价、处置、监测和记录 |

### 19.2 版本固定

1. ISO/IEC 20000-1 固定 2018 Edition 3，并记录 Amd 1:2024；
2. ISO/IEC/IEEE 12207 固定 2026 Edition 2；该版已于 2026-04 发布并替代 2017 版；
3. ISO/IEC/IEEE 14764 固定 2022 Edition 3；
4. ISO 9001 固定 2015 Edition 5，并记录 Amd 1:2024；
5. ISO 9001 Edition 6 当前处于发布阶段，ISO 官方预计 2026-09 替代 2015 版；未正式发布前不得作为本规范依据；
6. ISO 31000 固定 2018 Edition 2；
7. ISO/CD 31000 Edition 3 处于 Committee Draft，不作为本规范依据；
8. 标准引用必须写编号和年份，禁止使用“最新版”。

### 19.3 标准变化

以下变化必须进入 C11：

- 新 Edition 正式发布；
- Amendment/Correction 发布或撤销；
- 标准变为 Withdrawn/Replaced；
- 条款结构变化影响现有映射；
- 法律、监管、合同要求不同版本；
- 认证或符合性范围发生变化。

标准变化必须分析术语、产物、字段、状态、流程、命令、模板、Gate、Evidence、培训和历史 Baseline。ISO 9001 Edition 6 和 ISO/CD 31000 是当前明确监测项。

### 19.4 版权与符合性边界

1. 本规范仅引用 ISO 官方产品页和公开目录可确认的条款主题；
2. 不复制受版权保护的标准全文；
3. 项目代码、状态、阈值、命令、模板和 Gate 是工程化控制；
4. 未取得标准全文和正式评估时，禁止声明完整符合或认证；
5. 官方产品页用于身份和生命周期核验，不替代授权标准文本；
6. 国际标准不替代法律、监管、合同、SLA 或有权意见。

## 20. 模板、检查清单与国际标准条例映射

### 20.1 Extension Applicability Decision 骨架

```yaml
decision_id:
product_scope_revision:
decision_owner:
evaluation_time:
triggers:
  continuous_operation:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  production_sla_slo_oncall:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  canary_rollback_incident_feedback_control:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  post_release_metrics_drive_evolution:
    result: Yes|No|Unknown|Not Applicable
    evidence:
activation_status: Not Evaluated|Pending|Inactive|Conditionally Active|Active|Retiring|Retired
scope_conditions:
effective_time:
required_artifacts:
open_unknowns:
review_trigger:
change_request:
approver:
evidence:
```

### 20.2 SDF 骨架

```yaml
asset_id:
artifact_type: Service Definition
name_summary:
purpose:
source:
owner:
state: Draft|In Review|Changes Required|Approved|Baselined|Rejected|Superseded|Retired
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
service_id:
service_object:
value:
scope:
users_consumers:
dependencies_interfaces:
environments_regions_tenants:
support_time_oncall_escalation:
quality_objectives:
business_outcomes:
data_security_privacy_classification:
continuity_recovery:
suppliers:
exit_conditions:
retirement_triggers:
reviewer_approver:
```

### 20.3 SLO 骨架

```yaml
asset_id:
artifact_type: SLI/SLO Register
name_summary:
purpose:
source:
owner:
state: Draft|In Review|Changes Required|Approved|Baselined|Rejected|Superseded|Retired
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
members:
  - sli_id:
    sli_name:
    definition:
    event_population:
    numerator_denominator_exclusions:
    calculation_aggregation_timezone:
    data_source_query_revision:
    data_latency_integrity:
    slo_target:
    evaluation_window:
    business_basis:
    error_budget_policy:
    member_owner:
    alert_response:
    last_next_review:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.4 RBP 骨架

```yaml
asset_id:
artifact_type: Release and Rollback Plan
name_summary:
purpose:
source:
owner:
state: Draft|In Review|Changes Required|Approved|Baselined|Rejected|Superseded|Retired
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
release_id:
release_scope:
configuration_revision:
included_versions:
environment_tenant_region:
window:
traffic_stages:
prechecks:
authority:
command_references:
observation_metrics:
success_criteria:
stop_conditions:
rollback_conditions:
rollback_target:
data_compatibility:
rollback_steps:
alternative_recovery:
communication:
responsible_roles:
approvals:
rehearsal_evidence:
```

### 20.5 MAP 骨架

```yaml
asset_id:
artifact_type: Monitoring and Alert Plan
name_summary:
purpose:
source:
owner:
state: Draft|In Review|Changes Required|Approved|Baselined|Rejected|Superseded|Retired
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
monitoring_objects:
user_journeys:
signals:
  - signal_id:
    metric_event_definition:
    data_source_query_revision:
    window_latency_integrity:
    threshold:
    severity:
    dedup_suppression:
    notification:
    response_time:
    escalation:
    runbook:
    signal_owner:
monitoring_pipeline_health:
test_cycle:
last_test_evidence:
data_classification_retention:
```

### 20.6 INR 骨架

```yaml
asset_id:
artifact_type: Incident Record
name_summary:
purpose:
source:
owner:
state: Open|In Progress|Blocked|Resolved|Closed|Reopened|Cancelled
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
incident_id:
service_release_environment:
severity: SEV-1|SEV-2|SEV-3|SEV-4|Unclassified
user_impact:
detection_source:
incident_commander_roles:
timeline:
response_actions:
commands_decisions:
communications:
containment:
recovery_time:
impact_status: Ongoing|Contained|Recovered|Unknown
evidence:
root_cause_status: Not Started|Hypothesis|Under Analysis|Confirmed|Unknown
security_privacy_data_branches:
follow_up_actions:
closure_criteria:
closure_reviewer:
```

### 20.7 PBR 骨架

```yaml
asset_id:
artifact_type: Problem Record
name_summary:
purpose:
source:
owner:
state: Open|In Progress|Blocked|Resolved|Closed|Reopened|Cancelled
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
problem_id:
related_incidents_trends_defects:
problem_description:
business_impact:
cause_hypotheses_evidence:
root_cause_analysis:
confirmed_cause:
known_error:
workaround:
temporary_measure_expiry:
permanent_treatment:
requirement_change:
residual_risk:
verification:
recurrence_check:
closure_conditions:
```

### 20.8 OPO 骨架

```yaml
asset_id:
artifact_type: Operational Observation
name_summary:
purpose:
source:
owner:
state: Planned|Collected|Under Review|Accepted|Rejected|Invalidated
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
observation_id:
service_release:
observation_time_window:
environment_tenant_region:
metric_behavior:
raw_data_location:
query_tool_revision:
sampling_aggregation:
expected:
actual:
difference:
impact:
reliability_limitations:
assessment: Within Expected|Degraded|Improved|Anomalous|Inconclusive|Not Evaluated
related_requirements_slos:
evidence_integrity:
reviewer:
invalidation_conditions:
```

### 20.9 UFR 骨架

```yaml
asset_id:
artifact_type: User Feedback Record
name_summary:
purpose:
source:
owner:
state: Open|In Progress|Blocked|Resolved|Closed|Reopened|Cancelled
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
feedback_id:
user_group:
channel_time:
service_release:
original_feedback_language:
usage_context:
impact:
evidence:
classification:
duplicate_reference:
sentiment_frequency_severity:
related_need_problem_requirement:
privacy_access:
disposition: New|Triaged|Accepted for Action|Duplicate|Declined|Deferred|Closed
disposition_reason:
responsible_owner:
review_trigger:
```

### 20.10 PRR 骨架

```yaml
asset_id:
artifact_type: Post-release Review
name_summary:
purpose:
source:
owner:
state: Planned|Ready|Running|Blocked|Completed|Failed|Accepted|Rejected|Cancelled
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
review_id:
release:
observation_period:
target_metrics:
actual_results:
statistical_limitations:
slo_results:
business_guardrail_results:
defects_incidents_problems:
user_feedback:
cost_capacity:
residual_risks:
exceptions_waivers:
conclusion: Proceed|Proceed with Conditions|Rollback|Remediate|Escalate|Inconclusive
criteria:
decision_reference:
actions_owner_due:
reviewer:
evidence:
acceptance_record:
```

### 20.11 IBL 骨架

```yaml
asset_id:
artifact_type: Improvement Backlog
name_summary:
purpose:
source:
owner:
state: Draft|In Review|Changes Required|Approved|Baselined|Rejected|Superseded|Retired
current_revision:
created_updated:
applicable_scope:
trace_links:
access_classification:
retention_rule:
history_reference:
members:
  - improvement_id:
    improvement_source:
    problem_opportunity:
    expected_result:
    business_risk_value:
    priority_basis:
    estimate:
    member_owner:
    target_time:
    related_initiative_need_requirement_change:
    dependencies:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    defer_reject_reason:
    review_trigger:
    closure_criteria:
    closure_evidence:
    member_history_reference:
```

### 20.12 Operations Command Control 骨架

```yaml
command_id:
operation:
tool_name_version_digest:
plugin_connector_revision:
target:
  service_resource:
  release_revision:
  environment:
  tenant_region_partition:
input_references:
requester_operator:
authority_approval:
mode: read-only|dry-run|write
limits:
  traffic_batch_records_bytes:
  concurrency:
  timeout:
  rate_cost:
secret_references:
output:
  location:
  classification:
  redaction:
  retention:
  integrity:
preconditions:
stop_conditions:
snapshot_transaction_rollback:
run_correlation_id:
result:
observations:
evidence:
reviewer:
```

### 20.13 P2 生产检查清单

- [ ] E05 Applicability 在 Discovery Ready 前完成；
- [ ] 四项触发条件逐项有 Result 和 Evidence；
- [ ] 当前仓库为 Inactive；
- [ ] 必须编制与当前激活状态分离；
- [ ] 任一 Yes 强制 Active/Conditionally Active；
- [ ] 任一 Unknown 强制 Pending；
- [ ] 十类正式产物身份未合并；
- [ ] SDF/SLO/RBP/MAP/IBL 使用 DOC；
- [ ] INR/PBR/UFR 使用 CASE；
- [ ] OPO 使用 EVID；
- [ ] PRR 使用 EXEC；
- [ ] 通用必填字段完整；
- [ ] 容器 State 与成员/领域 Result 分离；
- [ ] Service、Product、Feature、Component 边界明确；
- [ ] SLI、SLO、SLA、业务指标边界明确；
- [ ] Release、Deployment、Change、Rollback 边界明确；
- [ ] Incident、Problem、Defect、Risk、Request 分类明确；
- [ ] Operation 与 Maintenance 边界明确；
- [ ] Service 有用户、价值、Scope 和 Owner；
- [ ] Service 依赖、环境、支持和退出条件完整；
- [ ] 关键 SLI 可复算；
- [ ] SLI 分子、分母、排除、窗口和数据源完整；
- [ ] SLO 有目标、业务依据和 Owner；
- [ ] No Data/Invalid Data 未判 Met；
- [ ] Error Budget 有治理政策；
- [ ] Release Configuration 固定 Revision；
- [ ] Release 包含代码、配置、数据、模型和文档版本；
- [ ] Environment/Tenant/Region 明确；
- [ ] 灰度阶段和流量明确；
- [ ] 每阶段成功 Criteria 完整；
- [ ] 每次发布有观察指标；
- [ ] 每次发布有停止条件；
- [ ] 每次发布有回滚条件；
- [ ] Rollback Target 已固定；
- [ ] 数据兼容和恢复边界完整；
- [ ] 不可回滚范围有替代恢复和批准；
- [ ] Monitoring 覆盖用户旅程和关键依赖；
- [ ] Signal 数据源、查询和可靠性完整；
- [ ] Alert 阈值、Severity、Owner 和响应完整；
- [ ] Runbook 和升级路径完整；
- [ ] Alert 测试周期和 Evidence 完整；
- [ ] 监控管道自身被监控；
- [ ] 零告警未推导为健康；
- [ ] Incident 有 Service/Release/Environment；
- [ ] Incident 时间线区分事实与假设；
- [ ] 用户影响有范围、时间和表现；
- [ ] Incident Commander 和响应角色完整；
- [ ] 高风险命令有 Authority/Run；
- [ ] 恢复时间与关闭时间分离；
- [ ] Security/Privacy/Data 分支已判断；
- [ ] 重大 Incident 有独立关闭复核；
- [ ] 重复 Incident 完成 Problem 判定；
- [ ] Problem 关联 Incident/Trend/Defect；
- [ ] 根因候选和 Evidence 保留；
- [ ] Root Cause 无 Evidence 未判 Confirmed；
- [ ] Known Error 有触发、影响和 Workaround；
- [ ] 临时措施有到期；
- [ ] 永久处理映射 Requirement/Change；
- [ ] Problem 关闭有验证和复发检查；
- [ ] OPO 固定 Service/Release/Environment/Time；
- [ ] 原始数据、Query/Tool Revision 可定位；
- [ ] 预期值引用 SLO/Metric/Requirement；
- [ ] 可靠性和限制完整；
- [ ] OPO 追踪到受影响 Requirement；
- [ ] OPO Accepted 未推导产品正确；
- [ ] UFR 保留原始反馈和语言；
- [ ] 用户群、渠道、版本和情境完整；
- [ ] PII/Access/Retention 已处理；
- [ ] Duplicate 保留原记录；
- [ ] Declined/Deferred 有理由和复核触发；
- [ ] 单条反馈未自动变为批准 Requirement；
- [ ] PRR 固定 Release 和观察窗口；
- [ ] 目标、实际、差异和统计限制并列；
- [ ] Incident/Problem/Defect/Feedback/Risk 完整；
- [ ] Review Conclusion 与 EXEC State 分离；
- [ ] 条件结论有 Owner/Due/Expiry；
- [ ] PRR Completed 未推导 Accepted；
- [ ] IBL 每项有 Source 和预期结果；
- [ ] Priority 有业务/风险依据；
- [ ] Improvement 映射 C01/C02/C04/C12；
- [ ] IBL 关闭有 Evidence；
- [ ] 运行学习未停留在聊天；
- [ ] Authority 固定 Operation/Scope/Time；
- [ ] 高风险职责已分离；
- [ ] Agent 未自批 Release/Rollback/Closure/Risk/Gate；
- [ ] Command 固定 Tool/Version/Digest；
- [ ] Target 固定 Service/Release/Environment/Tenant/Region；
- [ ] 生产 Target 未使用 Latest/Head/All/通配；
- [ ] Secret 仅使用 Reference；
- [ ] 默认 Read-only/Dry-run；
- [ ] Write/Deploy/Rollback/Recover/Dispose 单独授权；
- [ ] Resource/Traffic/Timeout/Cost Limit 完整；
- [ ] Stop/Snapshot/Transaction/Rollback 完整；
- [ ] Exit Code 未自动写 Governance Pass；
- [ ] 命令绑定 C09 Run 和 Evidence；
- [ ] 审计时间源、时区和 Correlation ID 一致；
- [ ] 日志不保存不必要 Secret/PII；
- [ ] Evidence 失效已反向查询；
- [ ] Operational Readiness Gate 输入完整；
- [ ] 阻断条件执行 Fail Closed；
- [ ] C01 至 C12 接口完整；
- [ ] E01 至 E04 接口完整；
- [ ] ISO/IEC 20000-1 Amd 1:2024 已记录；
- [ ] ISO/IEC/IEEE 12207 固定 2026 发布版；
- [ ] ISO 9001 Edition 6 发布状态受监测；
- [ ] ISO/CD 31000 未作为正式依据；
- [ ] 文末国际标准条例映射完整。

### 20.14 反例与标准复评清单

反例 1：

> Dashboard 全绿且没有告警，因此发布已经成功。

不符合：Dashboard 只展示信号；必须固定观察窗口、数据有效性、用户结果、护栏和 Review Criteria。

反例 2：

> 镜像使用 latest，回滚时再查上一个版本。

不符合：Release 和 Rollback Target 未固定，无法重现、授权和验证。

反例 3：

> 服务已经恢复，所以事故、Problem 和 Risk 都可以关闭。

不符合：恢复、事故关闭、根因确认、Problem 处理和 Risk Acceptance 是不同判断。

反例 4：

> 这条用户反馈很强烈，Agent 已自动将其升级为 P0 Requirement。

不符合：情绪不等于频率或业务影响；UFR 必须经 Evidence、分类、产品判断和需求流程。

反例 5：

> 工具返回 0，说明回滚完成且数据没有损失。

不符合：Exit Code 不证明目标配置、数据完整性、用户恢复或治理接受。

反例 6：

> SLO 本月达标，所以服务没有风险。

不符合：SLO 只覆盖定义的 SLI 和窗口，不能替代安全、隐私、数据、业务或未来 Risk。

标准复评：

- [ ] ISO/IEC 20000-1:2018 产品页状态未变化；
- [ ] ISO/IEC 20000-1:2018/Amd 1:2024 已纳入；
- [ ] ISO/IEC 20000-1 新 Edition/Correction 已检查；
- [ ] ISO/IEC/IEEE 12207:2026 仍是发布版；
- [ ] 12207:2017 已替代关系未被误用；
- [ ] ISO/IEC/IEEE 14764:2022 状态未变化；
- [ ] Operation 与 Maintenance 范围边界仍一致；
- [ ] ISO 9001:2015 及 Amd 1:2024 状态已核验；
- [ ] ISO 9001 Edition 6 是否已正式发布已检查；
- [ ] ISO 9001 新版未在批准前自动替换；
- [ ] ISO 31000:2018 状态已核验；
- [ ] ISO/CD 31000 未作为发布版依据；
- [ ] 服务、软件生命周期、维护、质量和风险映射无冲突；
- [ ] 标准变化已进入 C11；
- [ ] 历史 Baseline、Mapping 和 Evidence 未重写。

### 20.15 国际标准条例映射

以下映射依据 ISO 官方产品页和公开预览目录。项目产物代码、状态值、阈值、严重度、命令字段、模板和 Gate 是本项目工程化控制，不表示国际标准逐字规定。未取得标准全文授权时，不据此声明完整符合性。

| 国际标准及条款 | 条款或公开主题 | 本规范落实位置 |
|---|---|---|
| ISO/IEC 20000-1:2018 第 4 章 | Organization Context | 3、10.1、17、18 |
| ISO/IEC 20000-1:2018 第 5 章 | Leadership | 7、11.1、15 |
| ISO/IEC 20000-1:2018 第 6 章 | Planning | 9、10、14、17 |
| ISO/IEC 20000-1:2018 第 7 章 | Support | 7、10.2、11.5、15.2 |
| ISO/IEC 20000-1:2018 8.1 | Operational Planning and Control | 9、10、11、15 |
| ISO/IEC 20000-1:2018 8.2.1–8.2.4 | Service Delivery、Planning、Lifecycle Parties、Service Catalogue | 8、9.2–9.3、10.2、11.1 |
| ISO/IEC 20000-1:2018 8.2.5–8.2.6 | Asset and Configuration Management | 6.3、10.4、11.3、18.4 |
| ISO/IEC 20000-1:2018 8.3.2–8.3.4 | Business Relationship、Service Level、Supplier | 6.2、7、10.3、11.2 |
| ISO/IEC 20000-1:2018 8.4.1–8.4.3 | Budgeting、Demand、Capacity | 10.9、14、16.4、18.5 |
| ISO/IEC 20000-1:2018 8.5.1–8.5.3 | Change、Design/Transition、Release/Deployment | 6.3、9.4–9.5、10.4、11.3 |
| ISO/IEC 20000-1:2018 8.6.1–8.6.3 | Incident、Service Request、Problem | 6.4、9.6–9.7、10.6–10.7、11.6–11.7 |
| ISO/IEC 20000-1:2018 8.7.1–8.7.3 | Availability、Continuity、Information Security | 10.2、11.4、15.3、18.5 |
| ISO/IEC 20000-1:2018 9.1 | Monitoring、Measurement、Analysis and Evaluation | 10.3、10.5、14、16 |
| ISO/IEC 20000-1:2018 9.2–9.4 | Internal Audit、Management Review、Service Reporting | 15、16、20.13 |
| ISO/IEC 20000-1:2018 10.1–10.2 | Nonconformity、Corrective Action、Continual Improvement | 9.8、10.9、11.11、16.4 |
| ISO/IEC 20000-1:2018/Amd 1:2024 4.1–4.2 | Climate Action Changes | 3、19.2–19.3、20.14 |
| ISO/IEC/IEEE 12207:2026 第 4 章 | Conformance | 15、19.4 |
| ISO/IEC/IEEE 12207:2026 第 5 章 | Key Concepts and Application | 2–6、17 |
| ISO/IEC/IEEE 12207:2026 6.1 | Agreement Processes | 6.2、7、18 |
| ISO/IEC/IEEE 12207:2026 6.2 | Organizational Project-enabling Processes | 7、9、10、14–16 |
| ISO/IEC/IEEE 12207:2026 6.3.1–6.3.3 | Planning、Assessment/Control、Decision | 9–10、15–16 |
| ISO/IEC/IEEE 12207:2026 6.3.4 | Risk Management | 5、10、14、18 |
| ISO/IEC/IEEE 12207:2026 6.3.5–6.3.6 | Configuration and Information Management | 8、10.4、11.3、18.4 |
| ISO/IEC/IEEE 12207:2026 6.3.7–6.3.8 | Measurement and Quality Assurance | 10.3、14–16 |
| ISO/IEC/IEEE 12207:2026 6.4.9–6.4.11 | Verification、Transition、Validation | 9.4–9.5、15、18.2 |
| ISO/IEC/IEEE 12207:2026 6.4.12 | Operation Process | 9.5–9.8、10.5–10.9、11 |
| ISO/IEC/IEEE 12207:2026 6.4.13 | Maintenance Process | 9.7、10.10、11.7 |
| ISO/IEC/IEEE 12207:2026 6.4.14 | Disposal Process | 9.9、10.10、17.5 |
| ISO/IEC/IEEE 12207:2026 Annex A | Tailoring | 17 |
| ISO/IEC/IEEE 14764:2022 5 | Application of the Document | 3–6、17 |
| ISO/IEC/IEEE 14764:2022 6.1.1–6.1.4 | Maintenance Strategy、Planning、Plan、Requirements Review | 9.7、10.10、11.7 |
| ISO/IEC/IEEE 14764:2022 6.1.5–6.1.9 | Change Impact、Measurement、Replacement、Availability、Results | 10.7、10.10、14、16 |
| ISO/IEC/IEEE 14764:2022 6.2.1–6.2.3 | Problem/Modification Analysis、Feasibility、Replication/Verification | 9.7、10.7、11.7 |
| ISO/IEC/IEEE 14764:2022 6.2.4–6.2.7 | Implementation、Review/Recording、Approval、Technical Processes | 10.7、10.10、15 |
| ISO/IEC/IEEE 14764:2022 6.2.8 | Modified System Review | 10.10、15.1–15.2 |
| ISO/IEC/IEEE 14764:2022 第 7 章 | Software Disposal | 9.9、10.10、17.5 |
| ISO/IEC/IEEE 14764:2022 第 8 章 | Maintenance Implementation | 7、9.7、10.10、13.7 |
| ISO/IEC/IEEE 14764:2022 第 9 章 | Maintenance Plan | 10.10、13.7、20.7 |
| ISO 9001:2015 第 4 章 | Context of the Organization | 3、9.2、10.1 |
| ISO 9001:2015 第 5 章 | Leadership | 7、11.1、15 |
| ISO 9001:2015 第 6 章 | Planning | 9、10、14、17 |
| ISO 9001:2015 第 7 章 | Support | 7、11.5、15.2、16 |
| ISO 9001:2015 第 8 章 | Operation | 9–11、15 |
| ISO 9001:2015 9.1 | Monitoring、Measurement、Analysis and Evaluation | 10.3、10.5、14、16 |
| ISO 9001:2015 9.2–9.3 | Internal Audit and Management Review | 15、16 |
| ISO 9001:2015 10.2 | Nonconformity and Corrective Action | 9.6–9.8、10.6–10.9 |
| ISO 9001:2015 10.3 | Continual Improvement | 9.8、10.9、11.11 |
| ISO 9001:2015/Amd 1:2024 4.1–4.2 | Climate Action Changes | 3、19.2–19.3、20.14 |
| ISO 31000:2018 第 4 章 | Principles | 2、5、7、14 |
| ISO 31000:2018 5.2–5.6 | Leadership、Integration、Design、Implementation、Evaluation | 7、9–11、15–17 |
| ISO 31000:2018 6.2 | Communication and Consultation | 7、9.6、11.13 |
| ISO 31000:2018 6.3 | Scope、Context and Criteria | 3、5、10.1、15 |
| ISO 31000:2018 6.4.2–6.4.4 | Risk Identification、Analysis and Evaluation | 10、14、15 |
| ISO 31000:2018 6.5 | Risk Treatment | 10.4–10.10、11、15 |
| ISO 31000:2018 6.6 | Monitoring and Review | 10.5、14–16 |
| ISO 31000:2018 6.7 | Recording and Reporting | 8、11.13、16 |

规范性国际标准来源：

1. ISO, [ISO/IEC 20000-1:2018 — Service management system requirements](https://www.iso.org/standard/70636.html)。
2. ISO, [ISO/IEC 20000-1:2018/Amd 1:2024 — Climate action changes](https://www.iso.org/standard/88434.html)。
3. ISO, [ISO/IEC/IEEE 12207:2026 — Software life cycle processes](https://www.iso.org/standard/90219.html)。
4. ISO, [ISO/IEC/IEEE 14764:2022 — Software life cycle processes — Maintenance](https://www.iso.org/standard/80710.html)。
5. ISO, [ISO 9001:2015 — Quality management systems — Requirements](https://www.iso.org/standard/62085.html)。
6. ISO, [ISO 9001:2015/Amd 1:2024 — Climate action changes](https://www.iso.org/standard/88431.html)。
7. ISO, [ISO 9001 Edition 6（制定中）](https://www.iso.org/standard/88464.html)。
8. ISO, [ISO 31000:2018 — Risk management — Guidelines](https://www.iso.org/standard/65694.html)。
9. ISO, [ISO/CD 31000 Edition 3（制定中）](https://www.iso.org/standard/88574.html)。
