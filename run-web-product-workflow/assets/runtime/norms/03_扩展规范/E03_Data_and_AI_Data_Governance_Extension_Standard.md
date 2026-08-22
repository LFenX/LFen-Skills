# E03 数据与 AI 数据治理扩展规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | E03 |
| 英文名称 | Data and AI Data Governance Extension Specification |
| 正式文件名 | `E03_Data_and_AI_Data_Governance_Extension_Standard.md` |
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
| 已编制扩展依赖 | E01、E02 V6.3 |
| 生产前调研 | RVR-E03-0001 |
| 后续规范 | E04 至 E05 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 RDR、E04 Retention Rule、法律、监管、合同、许可、Legal Hold 和 Evidence 要求保留；批准、来源、许可、Dataset Revision、Data Contract、Lineage、质量结果、Issue、处置和更正历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式数据或 AI 数据治理约束。E03 当前未激活，不对本规范文档仓库强加目标产品数据治理控制；未激活不影响本文件必须编制、评审和建立 Git 基线。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品、软件、服务、分析、报表、指标、跨系统交换、机器学习、RAG、训练、验证、测试和评估数据的 Requirement、Contract、Dictionary、Quality Specification、Lineage、Dataset/Corpus、AI Data Quality、Retention/Disposal 和 Issue Remediation 治理。

本规范实现以下目标：

1. 使数据用途、业务决策、受影响方、错误后果、来源、语义、Owner、时效、访问、保留和 Privacy 要求明确；
2. 使 Data Contract 的提供方、使用方、Schema、Semantics、Quality SLO、Compatibility、Change 和 Verification 受控；
3. 使 Data Dictionary 成为数据项业务语义事实源，而不是数据库注释集合；
4. 使质量维度、业务 Risk、指标、测量函数、单位、阈值、周期、结果和失败处置可追踪；
5. 使数据来源、转换、版本、使用方和质量影响形成可查询 Lineage；
6. 使 Dataset/Corpus 的用途、来源、许可、时间、覆盖、代表性、标签、敏感性、版本、质量和限制明确；
7. 使 AI 数据的 Balance、Diversity、Relevance、Representativeness、Similarity、Timeliness、污染和泄漏得到评价；
8. 使训练、验证、测试、RAG 和评估数据的 Split、近重复、回流和污染边界可验证；
9. 使数据从 Requirement、Planning、Acquisition、Preparation、Provisioning、Operation 到 Decommissioning 全生命周期受控；
10. 使数据问题具有发现来源、影响、根因、临时控制、修复、复测和关闭条件；
11. 使数据访问、Profile、转换、标注、回填、匿名化和删除命令具有授权、范围、Stop、恢复和 Evidence；
12. 防止用 Tool Success、Dashboard 绿色、Model Metric、单次抽样或零告警自动推导 Data Quality Pass；
13. 防止 Agent 自批 Data Quality、Risk Acceptance、Waiver、Retention、Deletion 或 Gate；
14. 在 E03 未激活、已激活、待判定、条件激活和退役期间保持治理状态可追溯。

## 3. 适用范围

E03 在任一触发条件成立时必须激活：

- 存在数据分析；
- 存在报表；
- 存在业务指标或护栏指标；
- 存在数据产品；
- 存在跨系统数据交换；
- 存在 Data API、Event、File Exchange、Stream 或 Batch Feed；
- 存在机器学习；
- 存在 RAG 或 Corpus；
- 存在训练、验证、测试或评估 Dataset；
- 数据正确性直接影响业务、财务、运营、安全、合规或用户决策。

激活后的 E03 适用于：

- Product、Initiative、PRD、Requirement、Design、Code、Configuration、Release 和 Operation；
- Structured、Semi-structured、Unstructured、Tabular、Text、Image、Audio、Video、Event 和 Derived Data；
- Source Data、Reference Data、Master Data、Feature Data、Label、Annotation、Synthetic Data 和 Feedback Data；
- Analytical Dataset、Training Dataset、Validation Dataset、Test Dataset、Benchmark、Evaluation Set 和 RAG Corpus；
- Provider、Consumer、Owner、Steward、Engineer、Analyst、Annotator、Reviewer、Agent、Tool 和 Supplier；
- Development、Test、Staging、Production、Offline、Online、Backup、Archive 和 Retirement Environment；
- P2 档位下 DRS、DCO、DDY、DQS、DLG、DSR、ADQ、RDR 和 DIR；
- 人类、规则工具、数据质量工具、Pipeline、Query Engine、ML Tool 和 Agent 参与的数据活动；
- E04 已激活时的记录、元数据、访问、保留、审计、更正和历史恢复控制。

### 3.1 当前仓库状态

当前仓库只生产规范文档，不生产分析数据、Data Contract、模型训练数据、RAG Corpus 或评估 Dataset，因此：

1. `编制适用性 = 必须编制`；
2. `当前激活状态 = 未激活`；
3. E03 文件、模板骨架和检查规则必须完成；
4. 当前仓库不创建目标产品 DRS 至 DIR 实例；
5. 后续目标产品在 Discovery Ready 前必须重新执行全部触发条件判定；
6. 任一触发条件为 Unknown 时，禁止判为未激活；
7. 本规范文件中的示例不得包含真实受限数据、PII、Secret、许可受限 Corpus 或生产数据摘录。

### 3.2 横向生效边界

E03 激活后：

1. C01 至 C03 继续管理 Evidence、Product、Scope、PRD、Feature 和指标意图；
2. C04 继续管理原子 Requirement 和 Requirement Set；
3. C05 继续管理 Acceptance、Verification、Validation 和 Evidence；
4. C06 继续管理 UX 和 Technical Design；
5. C07 至 C09 继续管理 Authority、Context、Agent Run、Command 和 Evidence；
6. C10 继续管理 Decision、Trace 和 Lineage 总体治理；
7. C11 继续管理 Revision、Snapshot、Baseline、Change 和 Release Configuration；
8. C12 继续管理 Review、Gate、Waiver、Risk Acceptance 和 Product Health；
9. E01 继续管理 Data/AI Architecture Concern、View、Decision、Fitness 和 Conformance；
10. E02 继续管理 Security、Privacy、Compliance、PII 和 AI Impact；
11. E03 管理数据与 AI 数据的领域要求、契约、语义、质量、血缘、Dataset 和问题；
12. E04 管理 Knowledge、Record、Metadata、Access、Retention 和 Audit；
13. E05 管理 Service、SLO、Incident、Continuity、Monitoring 和 Operation。

## 4. 不适用范围

本规范不负责：

- 代替 C02 Risk Register、Success Metric Plan 或 Dependency Register；
- 代替 C04 Requirement Record；
- 代替 C05 Acceptance Criteria、Verification Plan、Evidence 或 Acceptance Decision；
- 代替 C06 Technical Design Specification；
- 代替 C07 Human Authority 或 C09 Agent Run Record；
- 代替 C10 Decision Record、Traceability Matrix 或通用 Lineage 治理；
- 代替 C11 Baseline、Change Request 或 Release Configuration；
- 代替 C12 Gate Decision、Exception or Waiver Record 或 Risk Acceptance Record；
- 代替 E01 Data Architecture、AI Architecture 或 Architecture Conformance；
- 代替 E02 Security、Privacy、PII、Compliance、License 或 AI Impact 判断；
- 代替 E04 Record、Access、Retention、Legal Hold、Audit 或 Disposition；
- 代替 E05 Monitoring、Incident、SLO 或 Service Review；
- 规定唯一数据库、Data Warehouse、Lakehouse、Feature Store、Vector Store、Catalog、Lineage Tool、Quality Tool 或 ML Platform；
- 规定唯一数据质量公式、统计分布、采样方式、标注方法、匿名化方法或模型；
- 声明产品、组织、Dataset、供应商或流程获得 ISO/IEC 认证；
- 提供许可、著作权、数据库权、个人信息、跨境、行业监管或其他法律结论；
- 保存真实受限数据、PII、Secret、Credential、完整 Production Row 或 Agent 私有思维链。

E03 可以消费上述事实，但禁止：

- 用 DRS 复制并替代 C04 REQ 正文；
- 用 DCO 替代法律合同；
- 用 DDY 替代 Physical Schema 或 TDS；
- 用 DQS 替代 C05 Acceptance；
- 用 DLG 图形替代可验证 Lineage；
- 用 DSR 证明取得合法使用权；
- 用 ADQ 证明模型质量、公平性、安全性或业务有效性；
- 用 RDR 自动作出法律保留或删除结论；
- 用 DIR 替代 C02 Risk、C11 Change 或 E05 Incident；
- 用 Model Accuracy 自动推导 Data Quality；
- 用数据可访问自动推导数据可使用；
- 用单次 Profile 自动推导持续符合；
- 用普通 EWR 绕过 Privacy、Security、Legal Hold、不可逆删除或 Non-waivable Gate。

## 5. 规范性用语与受控判定

### 5.1 规范性用语

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

法律、监管、合同、Security、Privacy、Safety、PII、许可、Legal Hold、不可逆数据、Non-waivable Gate 和 Authority Boundary 不得通过普通 EWR 绕过。

### 5.2 扩展适用性判定值

以下值是 E03 Activation Status，不是 DOC、CASE 或 DEC State：

| 值 | 语义 |
|---|---|
| Not Evaluated | 尚未评价；禁止进入 Discovery Ready |
| Pending | 存在未知项或等待 Evidence/Authority；禁止判为未激活 |
| Inactive | 全部触发条件明确为 No |
| Conditionally Active | 在明确 Scope、条件和期限内激活 |
| Active | 任一触发条件成立，E03 完整适用 |
| Retiring | 正在退出但仍需维持迁移、保留、删除、依赖和历史控制 |
| Retired | 当前 Scope 不再适用；历史资产继续保留 |

### 5.3 触发条件判定值

| 值 | 语义 |
|---|---|
| Yes | 条件已由 Evidence 证实 |
| No | 条件已由 Evidence 排除 |
| Unknown | 证据不足、Scope 不明确或等待有权判断 |
| Not Applicable | 仅在条件本身不属于被评 Scope 时使用，必须有理由和批准者 |

任一 Yes 使 E03 进入 Active 或 Conditionally Active。任一 Unknown 使 E03 进入 Pending。

### 5.4 领域判定值

以下是字段级 Result，不是资产 State：

| 判定域 | 允许值 |
|---|---|
| Requirement Result | Met、Partially Met、Not Met、Not Evaluated |
| Contract Compatibility | Compatible、Conditionally Compatible、Breaking、Unknown |
| Quality Result | Pass、Conditional Pass、Fail、Not Evaluated |
| Data Fitness | Fit for Intended Use、Conditionally Fit、Not Fit、Unknown |
| Lineage Status | Complete、Partial、Broken、Unknown |
| License/Use Result | Authorized、Conditionally Authorized、Prohibited、Pending Authority |
| Issue Validity | Confirmed、Duplicate、False Positive、Unable to Determine |
| Remediation Result | Effective、Partially Effective、Ineffective、Not Verified |
| Disposal Result | Completed、Partially Completed、Failed、Blocked、Not Due |

每个 Result 必须记录 Scope、Revision、Criteria、Evidence、Reviewer 和时间。禁止把 Result 注册为 DOC 或 CASE State。

### 5.5 不适用和未知规则

1. 字段不适用时必须记录理由、Scope、依据和批准人；
2. 未知来源、许可、数据主体、Schema、Owner、阈值、Consumer、Lineage 或 Retention 必须显式标为 Pending/Unknown；
3. 空值禁止代替 Unknown、Not Applicable 或 Not Evaluated；
4. 未知的许可、Privacy、Security 或 Legal Hold 禁止由 Agent 推断；
5. 未知阈值禁止由 Tool Default、行业惯例或任意百分比填充；
6. 未知 Consumer 禁止批准 Breaking Change；
7. 未知 Dataset Revision 禁止作为训练、测试、RAG 或 Gate 输入。

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Data Asset | 在明确用途、Owner、Scope 和生命周期下受治理的数据集合或数据服务 |
| Data Requirement | 对数据用途、对象、语义、来源、质量、时效、访问、保留、Privacy 或验证的可追踪要求 |
| Data Contract | Provider 与 Consumer 对数据集或事件的语义、Schema、质量、兼容、Change、通知和验证承诺 |
| Data Dictionary | 数据项业务定义、概念类型、允许值、单位、来源、Owner、分类和质量规则的受控目录 |
| Data Quality | 数据特性满足明示或隐含使用需要的程度；必须限定 Intended Use、Context 和 Revision |
| Data Quality Characteristic | 评价数据质量的特性维度 |
| Quality Measure | 将一个或多个可观察元素通过明确函数转化为质量结果的方法 |
| Data/AI Evaluation Threshold | 对 Data/AI Measure Result 作 Pass、Conditional Pass 或 Fail 判断的受控边界；专业化自 C12 Threshold |
| Data Lineage | 数据从来源经过获取、转换、组合、存储、供给到使用方的可追踪链 |
| Data Provenance | 数据来源、获取、生成、处理主体、时间、方法、版本和限制的历史事实 |
| Dataset | 为明确用途按一致边界组织的数据集合 |
| Corpus | 为检索、训练、分析或评估组织的文档、文本、媒体或知识材料集合 |
| AI Data | 用于开发、训练、验证、测试、评估、部署、运行或改进 AI 系统的数据 |
| Intended Use | 被批准的数据使用目的、任务、对象、环境、使用方和决策边界 |
| Representativeness | Dataset 对目标总体、场景或分布的覆盖程度 |
| Balance | 目标类别、群体、场景或其他分层之间与任务要求相符的分布程度 |
| Diversity | Dataset 对不同取值、模式、场景、来源或群体的覆盖广度 |
| Data Contamination | 不应进入某 Dataset、Split、评估或运行边界的数据发生混入 |
| Data Leakage | 训练或决策过程中获得按设计不应可用的信息，造成虚高结果或错误判断 |
| Label | 为样本指定的类别、数值或目标值 |
| Annotation | 对样本增加的结构化解释、边界、关系、属性或元数据 |
| Split | 按可重建规则将 Dataset 分配为训练、验证、测试、评估或其他 Partition |
| Data Drift | 数据分布、来源、语义、质量或使用环境相对批准基线发生变化 |
| Data Owner | 对数据资产内容、用途、质量和治理负责的人类角色；不自动表示法律所有权 |
| Data Steward | 负责执行数据政策、语义、质量、血缘和问题管理的角色 |
| Provider | 按 DCO 提供数据的角色或系统 |
| Consumer | 按 DCO 使用数据的角色、系统、模型、报表或流程 |
| Data Issue | 数据要求、契约、语义、质量、血缘、许可、保留或使用边界的已识别偏差 |
| Decommissioning | 数据停止活动使用并完成迁移、依赖检查、保留、归档、删除或替代的阶段 |

### 6.1 Data Quality、Model Quality 与 Product Quality 边界

1. Data Quality 评价数据是否适合明确用途；
2. Model Quality 评价模型行为或性能，归属适用 AI/工程规范；
3. Product Quality 评价产品能力和质量属性，归属 C03 至 C06、C12；
4. 高 Model Metric 不证明 Dataset 无污染、代表性充分或许可有效；
5. 高 Data Quality 不证明模型安全、公平、合规或达到业务结果；
6. E03 只对数据质量结论负责，不越权声明其他质量结论。

### 6.2 Source、Provenance、Lineage 与 Trace 边界

| 概念 | 回答的问题 | 权威位置 |
|---|---|---|
| Data Source | 数据直接来自何处；专业化自 VC-PPG-COM-001 Source | DRS、DDY、DSR |
| Data Provenance | 数据如何获得、由谁处理、何时形成；专业化自 VC-PPG-COM-001 Provenance | DSR、DLG |
| Lineage | 数据经过哪些转换并被谁消费 | DLG |
| Trace | 数据治理产物与 Need、Requirement、Evidence、Decision、Change、Gate 的关系 | C10 |

四者必须互相引用，禁止合并为一个无类型链接字段。

## 7. 角色、职责与职责分离

### 7.1 角色

| 角色 | 最低职责 |
|---|---|
| Governing Authority | 指导和监督数据质量治理，批准策略、重大 Risk、例外和不可逆处置边界 |
| Project Owner | 对 E03 激活、资源、Scope、Gate 输入和最终责任负责 |
| Data Owner | 对数据用途、语义、质量、访问、保留、Consumer 和变更负责 |
| Data Steward | 维护 Dictionary、Quality、Lineage、Issue 和数据政策执行 |
| Data Provider | 按 DCO 提供可识别 Revision、通知 Change 并提交 Evidence |
| Data Consumer | 声明 Intended Use、质量需要、兼容要求和使用限制 |
| Data Engineer | 实现 Acquisition、Transformation、Validation、Provisioning 和 Lineage |
| Data Quality Owner | 维护 DQS、测量方法、阈值、质量报告和改进计划 |
| Dataset Curator | 维护 DSR、来源、许可、Composition、Label、Split、Version 和限制 |
| Annotator | 按批准规范和任务边界执行 Label/Annotation |
| Privacy/Security/Compliance Authority | 处理 PII、Security、许可、义务、跨境和 Legal Hold 相关判断 |
| Independent Reviewer | 独立复核 DCO Change、DQS、ADQ、DIR Closure 和 Gate Evidence |
| Record Custodian | 按 E04 管理记录访问、保留、归档、处置和历史 |
| Agent | 在授权 Scope 内起草、检查、测量和报告；无批准权 |

组织可以合并低风险角色，但不得消除职责。

### 7.2 最低职责分离

以下决定必须由有权人类作出：

- E03 激活、停用和退役；
- Data Owner 和 Governing Authority 指派；
- Intended Use、Prohibited Use 和受影响方确认；
- Data Contract Breaking Change；
- 许可、Privacy、Security、Compliance 和 Legal Hold 判断；
- Data Quality Model、Threshold 和 Risk Acceptance 批准；
- Dataset 对训练、验证、测试、RAG 或评估的放行；
- ADQ 结论和 Conditional Pass 条件；
- DIR 的 Unable to Determine、Risk Acceptance 和 Closed；
- 不可逆删除、匿名化、外部共享和生产数据导出；
- Waiver、Gate 和 Release Decision。

执行者不得独立批准自己的测量、修复或删除结果。高风险 Dataset 的 Curator、Quality Reviewer 和 Gate Approver 必须分离。

### 7.3 Agent 使用规则

Agent 可以：

- 起草九类 E03 产物；
- 检查字段、状态、关系、版本和 Template；
- 在已批准 Scope 内生成 Query、Rule、Profile、Diff 和 Lineage 候选；
- 汇总公开或已授权 Evidence；
- 标记缺失、冲突、异常、漂移和 Pending；
- 生成不包含真实受限数据的报告。

Agent 禁止：

- 访问未授权 Source、Tenant、Environment 或 Partition；
- 将真实数据复制到 Prompt、公共日志或未批准 Tool；
- 擅自运行全表扫描、生产写入、回填、重标注、匿名化或删除；
- 推断未知许可、法律权属、PII 合法性或跨境允许性；
- 修改 Source Data 以使质量结果通过；
- 删除失败结果、异常样本或反例；
- 自行调整阈值以改变 Pass/Fail；
- 批准自身 DQS、ADQ、DIR、Waiver 或 Gate；
- 输出 Agent 私有思维链。

## 8. 受控产物与关系

### 8.1 正式产物

| 代码 | 正式名称 | 状态模型 | 核心目的 |
|---|---|---|---|
| DRS | Data Requirement Set | DOC | 规定数据业务用途、对象、语义、来源、质量、时效、访问、保留、Privacy、Acceptance 和 Verification |
| DCO | Data Contract | DOC | 规定 Provider/Consumer 的数据或事件承诺 |
| DDY | Data Dictionary | DOC | 管理数据项的正式业务语义和质量规则 |
| DQS | Data Quality Specification | DOC | 规定质量维度、Risk、指标、函数、阈值、周期和失败处置 |
| DLG | Data Lineage | DOC | 管理 Source、Transformation、Consumer、Version 和质量影响链 |
| DSR | Dataset or Corpus Record | DOC | 管理 Dataset/Corpus 身份、用途、来源、许可、代表性、标签、版本、质量和限制 |
| ADQ | AI Data Quality Report | DOC | 报告 AI/ML/RAG 数据的质量结果、代表性、偏差、污染、限制、Risk、结论和行动 |
| RDR | Data Retention and Disposal Rule | DOC | 规定数据保留、归档、删除、匿名化、Legal Hold 和 Evidence |
| DIR | Data Issue and Remediation Record | CASE | 管理数据问题、影响、根因、控制、修复、验证和关闭 |

九类产物身份必须保留。ADQ 不替代一般 DQS；非 AI 数据不强制创建 ADQ，但必须按 DQS 形成 C05 Verification/Evidence。

### 8.2 单一事实源

| 事实 | 权威产物 |
|---|---|
| 业务用途、数据对象和数据要求 | DRS |
| Provider/Consumer 交换承诺 | DCO |
| 数据项业务定义 | DDY |
| 质量模型、指标、函数和阈值 | DQS |
| 来源、转换和消费链 | DLG |
| Dataset/Corpus 身份和限制 | DSR |
| AI 数据质量结果和结论 | ADQ |
| 数据保留和处置规则 | RDR |
| 数据问题和整改 | DIR |

其他文档只能引用，不得复制后独立演化。

### 8.3 最低关系链

```text
SNR/PIG → INI/SCP/RSK → PRD/FTR → REQ/ACP
       → DRS → DCO/DDY → DQS → DLG/DSR
       → ADQ/VER/EVD → DIR/CHG → GDR/PHR
```

最低约束：

1. DRS 必须 `derives-from` C01/C03/C04 输入；
2. DCO、DDY 和 DQS 必须 `derives-from` DRS；
3. DLG 和 DSR 的实现含义必须通过公共关系 `implemented-by` 的反向查询表达，不新增关系值；
4. DQS 必须 `addresses` C02 RSK 和 C04 REQ；
5. ADQ 必须 `generated-by` 可重建的 Verification/Run，并 `verified-by` C05 Evidence；
6. DIR 必须 `addresses` 失败 Requirement、DCO、DQS、DSR 或 ADQ；
7. RDR 必须 `constrains` DSR、DLG、DIR 和数据执行；
8. Change 必须 `affected-by` 或 `supersedes` 受影响 Revision；
9. Gate 必须查询 C10 Trace，而不是依赖人工摘要。

### 8.4 受控关系

E03 只允许使用公共术语基线规定的关系：

| 关系 | E03 用法 |
|---|---|
| derives-from | 从 Need、Requirement、DRS、Source 或上一 Revision 派生 |
| addresses | DQS/DIR 处理 Requirement、Risk 或 Finding |
| contains | Set、Dictionary、Report 包含受控成员 |
| refines | DRS、DCO、DQS 细化上游要求 |
| extends | AI 数据控制扩展通用数据质量控制 |
| depends-on | Dataset、Consumer 或 Process 依赖 Source、Tool、Contract |
| constrains | RDR、DCO、DQS 限制使用、变更、保留或执行 |
| designed-by | Data Solution 由 Design 规定 |
| implemented-by | Requirement 或 Rule 由 Pipeline、Query、Code、Configuration 实现 |
| verified-by | Contract、Quality、Issue 或 Disposal 由 Evidence 验证 |
| validated-by | Intended Use 或 Dataset Fitness 由 Stakeholder/Validation 确认 |
| released-in | Data Revision 或 Contract Revision 进入 Release |
| affected-by | Asset 受 Change、Issue、Incident 或 Standard Change 影响 |
| supersedes | 新 Revision 或 Rule 替代旧 Revision |
| replaces | 新 Data Asset 替换不同身份的旧 Data Asset |
| generated-by | ADQ、Profile、Manifest 或 Evidence 由 Run/Tool 生成 |
| observed-from | Issue、Drift 或 Metric 从运行观察获得 |

无法表达的关系必须进入 C10 关系治理，不得在 E03 私增关系。

## 9. E03 治理生命周期

### 9.1 生命周期

E03 采用以下项目级生命周期：

```text
Intent and Requirement
  → Data Planning
  → Acquisition
  → Preparation
  → Provisioning
  → Use and Monitoring
  → Change and Improvement
  → Decommissioning
```

该生命周期与 ISO/IEC 5259-1、5259-3、5259-4 和 8183 建立映射，不强行合并各标准不同粒度的阶段名称。

### 9.2 启动输入

进入 Data Planning 前必须存在：

- Product/Initiative/PRD Scope；
- Stakeholder Need、Intended Use 和 Prohibited Use；
- 数据主体或业务对象；
- 业务决策和错误后果；
- C02 Risk、Assumption、Constraint 和 Dependency；
- C04 Requirement；
- C05 Acceptance/Verification Strategy；
- E03 Applicability Decision；
- 适用 E01/E02/E04/E05 结论；
- 未知项和 Authority Owner。

任一关键输入 Unknown 时必须进入 Pending 或建立有条件计划，不得伪造默认事实。

### 9.3 迭代规则

以下事件必须重新评价 DRS、DCO、DDY、DQS、DLG、DSR、ADQ、RDR 和 DIR：

- Intended Use、User、Decision 或 Risk 变化；
- Source、Provider、Consumer、Schema 或 Semantics 变化；
- 数据覆盖时间、地区、群体、设备、语言或场景变化；
- Transformation、Filter、Join、Normalization、Imputation、Augmentation 或 Label 变化；
- Split、Sampling、Seed 或 Evaluation Set 变化；
- License、Privacy、Security、Compliance 或 Retention 变化；
- Tool、Rule、Query、Model、Embedding 或 Index Version 变化；
- Data Drift、Quality Fail、Leakage、Contamination 或 Incident；
- 标准版本、组织政策或合同变化；
- Decommissioning、Migration 或 Replacement。

每次变化必须进入 C11 Change；禁止直接覆盖 Baselined Revision。

### 9.4 阶段完成条件

| 阶段 | 最低完成条件 |
|---|---|
| Intent and Requirement | E03 判定完成；DRS Scope、Use、Risk、Requirement 和 Owner 完整 |
| Data Planning | Source、Contract、Dictionary、Quality、Lineage、Retention 和 Verification 计划批准 |
| Acquisition | Source、Authority、Method、Time、Revision、Integrity 和 Restrictions 有 Evidence |
| Preparation | 所有转换、清洗、标注、增强、去标识和 Split 可重建 |
| Provisioning | Dataset Revision、DCO、DQS、DLG、Access 和 Consumer Acceptance 固定 |
| Use and Monitoring | Quality、Drift、Issue、Usage 和 Consumer Feedback 受监控 |
| Change and Improvement | 影响分析、修复、重测、迁移和历史完成 |
| Decommissioning | Consumer/Dependency 清零或迁移；Retention、Legal Hold、Deletion 和 Evidence 完成 |

## 10. 适用性与数据治理过程

### 10.1 Extension Applicability Decision

目标产品必须在 Discovery Ready 前逐项记录：

- Trigger ID；
- Condition；
- Result；
- Evidence；
- Evaluator；
- Evaluated At；
- Scope；
- Unknown/Not Applicable Reason；
- Decision；
- Approver；
- Review Trigger。

判定对象必须覆盖分析、报表、指标、数据产品、跨系统交换、ML、RAG、训练、评估和决策影响，不得只问“是否有数据库”。

### 10.2 强制激活规则

1. 任一触发条件为 Yes，E03 必须 Active；
2. 有限 Scope 内触发时可以 Conditionally Active，但必须记录边界、条件、期限和重评事件；
3. 任一触发条件 Unknown，E03 必须 Pending；
4. 全部条件为 No 且 Evidence 充分，才可以 Inactive；
5. Scope、Data、Integration、AI 或 Decision 变化时必须重评；
6. 决定不激活已触发的 E03 时，必须建立 EWR，并由有权人类批准；
7. 未激活不允许忽略 C02、C05、C06、C11 和 C12 已识别的数据 Risk。

### 10.3 Data Requirement Process

1. 从 SNR、PIG、PRD、REQ、RSK 和 ACP 提取数据需要；
2. 识别 Intended Use、Prohibited Use、Data Subject/Object 和 Decision；
3. 记录 Semantics、Source、Quality、Timeliness、Access、Retention、Privacy 和 Verification；
4. 将复合要求拆分为可验证 REQ，并由 DRS 引用；
5. 将 Unknown、Assumption、Constraint 和 Dependency 显式登记；
6. 由 Data Owner、Consumer、Quality Owner 和适用 Authority 评审；
7. 批准后纳入 Baseline，变更走 C11。

### 10.4 Data Contract Process

1. 固定 Provider、Consumer、Dataset/Event、Environment 和 Revision；
2. 固定 Schema Concept、Semantics、Ordering、Cardinality、Null、Time 和 Identifier 规则；
3. 固定 Quality SLO、Measurement、Threshold 和 Breach 处理；
4. 固定 Version、Compatibility、Deprecation、Notice 和 Migration；
5. 固定 Access、Security、Privacy、Retention 和 Prohibited Use；
6. 固定 Verification、Evidence、Owner、Escalation 和 Support；
7. Change 前查询 DLG 和 Consumer Register；
8. Breaking Change 必须经 C11/C12 处理，禁止静默发布。

### 10.5 Data Dictionary Process

1. 每个数据项使用稳定 ID；
2. 记录正式业务名称、定义、概念类型、允许值、单位、时间语义和 Null 语义；
3. 记录 Source、Owner、Classification、Quality Rule 和关联资产；
4. 禁止同一业务概念存在冲突定义；
5. Physical Column、API Field 或 Event Attribute 必须映射到业务项；
6. 定义变更必须分析 DCO、DQS、DLG、DSR、报表、模型和历史数据；
7. Deprecated 项必须有替代项、迁移期和 Consumer。

### 10.6 Data Quality Process

```text
Intended Use and Risk
  → Select Quality Characteristics
  → Define Measures and Thresholds
  → Plan Measurement
  → Execute and Capture Evidence
  → Review and Report
  → Remediate and Re-measure
  → Monitor and Improve
```

强制规则：

1. 质量模型必须与 Intended Use、Stakeholder 和 Risk 关联；
2. Measure 必须有定义、输入、函数、单位、方向、样本、周期和限制；
3. Threshold 必须有业务依据和批准者；
4. Tool Output 只能产生 Candidate Result；
5. Pass/Fail 必须针对固定 Dataset/Asset Revision；
6. Fail 必须进入 DIR、C02 Risk、C11 Change 或 C12 Gate；
7. Conditional Pass 必须有条件、Owner、期限和复核计划；
8. 数据变化后必须判断 Evidence 是否 Invalidated。

### 10.7 Dataset and Corpus Process

1. 创建 DSR 并固定 Intended Use；
2. 登记 Source、Acquisition、Authority、License/Use Restriction 和时间范围；
3. 记录 Composition、Coverage、Representativeness、Balance、Diversity 和 Known Gaps；
4. 记录 Sensitive Data、PII、Security Classification 和访问；
5. 记录 Transformation、Filter、Cleaning、Imputation、Augmentation 和 Synthetic Ratio；
6. 记录 Label/Annotation Specification、Participant、Tool 和 Quality Check；
7. 固定 Split、Seed、Entity/Time Isolation 和 Contamination Check；
8. 固定 Dataset Revision、Manifest、Hash、Schema/DDY、DQS 和 DLG；
9. 执行 ADQ 或适用 C05 Verification；
10. Provisioning 前由 Consumer 和 Independent Reviewer 接受；
11. 使用期间监控 Drift、Issue、Feedback 和 Unauthorized Use；
12. 退役时执行 RDR 和 Consumer/Dependency 检查。

### 10.8 Data Issue Process

1. 发现异常时创建 DIR，禁止只留在聊天、日志或 Dashboard；
2. 固定受影响 Data Asset、Dataset Revision、Consumer、Time 和 Quality Dimension；
3. 判断 Issue Validity，记录 Evidence 和 Reviewer；
4. 评估业务、用户、模型、报表、合规和下游影响；
5. 建立临时控制、Owner、Due Date 和 Escalation；
6. 进行 Root Cause Analysis，区分 Source、Contract、Semantic、Transformation、Tool、Process 和 Use Error；
7. 通过 C11 执行修复并保留前后 Revision；
8. 按原 DQS 或批准的新 DQS 重测；
9. 关闭前确认 Consumer 恢复、残余 Risk、Evidence 和独立复核；
10. 复发时 Reopened，不得创建重复 Closed Record 隐藏复发。

### 10.9 Retention and Disposal Process

1. 按数据类别、用途、来源、合同、许可、Privacy、Security、法规和 Evidence 确定 RDR；
2. 固定起算事件、期限、归档、删除/匿名化方法、Legal Hold、Owner 和例外；
3. RDR 与 E04 Retention Schedule 不一致时必须升级给有权角色；
4. 处置前查询 DLG、Consumer、Backup、Derived Data、Model、Index、Cache 和 Evidence；
5. 删除或匿名化必须有授权、Dry Run、Scope、Stop、验证和记录；
6. Legal Hold 未解除时禁止处置；
7. 处置失败必须创建 DIR；
8. 历史审批、Evidence 和不可变记录按 E04 保留，禁止随业务数据无痕删除。

### 10.10 Data Governance Review

Data Governance Review 至少检查：

- Activation 和 Scope；
- Intended Use、Prohibited Use 和受影响方；
- Owner、Steward、Provider、Consumer 和 Authority；
- DRS/DCO/DDY/DQS/DLG/DSR/ADQ/RDR/DIR 完整性；
- Source、License、Privacy、Security 和 Compliance；
- Quality Model、Measure、Threshold、Result 和 Risk；
- Dataset Revision、Label、Split、Contamination 和 Drift；
- Contract Change、Lineage Impact 和 Consumer Readiness；
- Retention、Legal Hold、Deletion 和 Evidence；
- Open DIR、Waiver、Conditional Pass 和 Expiry；
- Agent/Tool Authority、Command、Output 和 Audit；
- C12 Gate 和 Product Health 输入。

## 11. 数据与 AI 数据控制

### 11.1 Intended Use、Purpose 与 Risk

每个 Data Asset 和 Dataset 必须记录：

- 直接业务用途；
- 使用方和受影响方；
- 支持的 Decision、Feature、Model、Report、Metric 或 RAG Task；
- Prohibited Use；
- 输入和输出边界；
- Environment、Region、Language、Population 和 Time Scope；
- 错误、缺失、延迟、偏差或不可用的后果；
- C02 Risk、C04 Requirement 和 C05 Acceptance；
- 目的变化的重评触发条件。

禁止：

- 先获得数据再虚构目的；
- 用“分析”“AI”“优化”“改善体验”等宽泛词代替明确用途；
- 将为 A 用途批准的数据默认复用于 B 用途；
- 将 Sandbox、Test 或 Research 数据未经评价转为 Production；
- 将受限 Dataset 用于未批准训练、评估、RAG 或 Prompt。

### 11.2 Source、Acquisition 与 Authority

Source 控制必须覆盖：

| 控制项 | 最低要求 |
|---|---|
| Source Identity | Source ID、Provider、System/Repository、Environment 和 Owner |
| Acquisition | 方法、接口、Query/Export、时间、频率、完整性和传输 |
| Revision | Source Revision、Schema Revision、Time Window 和 Snapshot |
| Authority | 授权主体、Purpose、Scope、期限、许可和限制 |
| Integrity | Hash、Count、Signature 或其他完整性 Evidence |
| Classification | Access Classification、PII、Secret、商业敏感和受限级别 |
| Reliability | 已知缺陷、缺失、延迟、偏差、变更历史和可信级别 |
| Trace | DRS、DCO、DDY、DQS、DLG、DSR、COR 和 Evidence |

Web Scraping、Public Download、Open License 或公开可见不自动构成可训练、可转售、可跨境、可长期保留或可删除个人权利请求的数据授权。许可和法律结论必须由适用 Authority 处理。

### 11.3 Schema、Semantics 与 Dictionary

1. Schema 说明结构；DDY 说明业务语义；二者必须关联但不得混同；
2. 每个字段必须有稳定 Data Item ID；
3. Identifier 必须说明唯一性范围、生成规则和可复用性；
4. Time 字段必须说明事件时间、处理时间、时区、精度和区间边界；
5. Unit、Currency、Locale、Encoding、Language 和 Coordinate System 必须明确；
6. Null、Missing、Unknown、Not Applicable、Zero 和 Empty String 必须区分；
7. Enum 必须有受控值、未知值策略和废弃规则；
8. Derived Field 必须记录计算定义、输入、版本和 Owner；
9. Label 和 Target 必须说明定义、来源、标注规则和争议处理；
10. 语义变更即使 Physical Schema 不变，也必须执行 DCO Change 和影响分析。

### 11.4 Data Contract 与 Compatibility

Compatibility 至少从以下维度评价：

- Schema；
- Semantics；
- Required/Optional；
- Cardinality；
- Ordering；
- Identifier；
- Time；
- Unit；
- Null/Default；
- Quality SLO；
- Access/Classification；
- Retention；
- Consumer Behavior；
- Historical Reprocessing；
- Rollback。

Breaking Change 包括但不限于：

- 删除或重命名 Consumer 使用的数据项；
- 改变同一字段语义、单位、时区、精度或允许值；
- 缩短可用历史、Retention 或通知期；
- 降低 Quality SLO；
- 改变 Identifier 稳定性；
- 改变 Event Ordering、Deduplication 或 Delivery Semantics；
- 将未知值静默映射为默认值；
- 改变许可、Privacy、Security 或 Prohibited Use；
- 改变 Dataset Split、Label Definition 或 Evaluation Set。

禁止仅凭 Schema Validator Pass 判定 Compatible。

### 11.5 通用数据质量模型

通用数据质量候选维度来自 ISO/IEC 25012：

| 视角 | 候选维度 |
|---|---|
| Inherent | Accuracy、Completeness、Consistency、Credibility、Currentness |
| Inherent and System-dependent | Accessibility、Compliance、Confidentiality、Efficiency、Precision、Traceability、Understandability |
| System-dependent | Availability、Portability、Recoverability |

选择规则：

1. DQS 必须逐项评价候选维度的适用性；
2. 选择的维度必须关联 Intended Use 和 Risk；
3. 未选择的维度必须记录理由；
4. Confidentiality 接口 E02，不由质量工具单独判定；
5. Availability、Recoverability 和运行期 Timeliness 接口 E05；
6. Compliance 必须引用 COR 或有权来源；
7. 不得使用一个综合分数掩盖关键维度 Fail。

### 11.6 AI/ML 扩展数据质量模型

AI/ML、RAG 和评估数据除通用维度外，必须评价 ISO/IEC 5259-2 的附加候选维度：

| 维度 | E03 最低评价问题 |
|---|---|
| Auditability | 来源、处理、版本、测量和决定能否由独立角色复核 |
| Balance | 类别、群体、场景或分层分布是否满足任务要求 |
| Diversity | 来源、取值、模式、语言、地区、设备或场景覆盖是否充分 |
| Effectiveness | 数据是否支持预期分析或 ML 任务结果 |
| Identifiability | 数据记录、实体或样本能否在需要时被正确识别；涉及个人时接口 E02 |
| Relevance | 数据与 Intended Use、任务、时间和场景是否相关 |
| Representativeness | Dataset 是否代表目标总体、环境或分布 |
| Similarity | 数据之间或与目标分布之间的相似性是否符合用途并避免重复/污染 |
| Timeliness | 数据到达、更新、可用和决策时点是否满足要求 |

每项评价必须限定 Target Population、Task、Time、Environment 和 Dataset Revision。禁止将 Demographic Parity、Fairness、Bias 或 Model Performance 简化为单一 Data Quality 维度；相关结论必须接口 E02 AIA 和适用模型评价。

### 11.7 Measure、Function、Threshold 与 Result

每项 Quality Measure 必须记录：

| 字段 | 最低要求 |
|---|---|
| Measure ID | 稳定、唯一、版本外标识 |
| Characteristic | 对应质量维度 |
| Business Rationale | Intended Use、Risk 和 Requirement |
| Target Entity | Field、Record、Dataset、Partition、Event、Corpus 或 Service |
| Base Measures | 原始可观察量及获取方式 |
| Function | 明确公式、规则或算法 |
| Unit/Scale | 单位、量纲、值域和方向 |
| Population/Sample | 总体、样本、抽样框、大小、分层和随机种子 |
| Time Window | 事件时间、处理时间和观察窗口 |
| Environment | Source、Engine、Locale、Timezone 和配置 |
| Threshold | Pass、Conditional Pass、Fail 边界 |
| Threshold Basis | Stakeholder、Risk、Baseline、Contract 或 Regulation |
| Frequency | 测量时点和周期 |
| Limitations | 盲区、误差、统计限制和不可比较条件 |
| Owner/Reviewer | 责任和独立复核 |
| Failure Action | DIR、Stop、Rollback、Quarantine、Recompute 或 Gate |

Result 必须同时记录 Numerator、Denominator 或等价原始量，禁止只保存百分比。除非 DQS 明确允许，空分母、零样本、采样失败、Query Error 或 Timeout 必须判为 Not Evaluated，不得判 Pass。

### 11.8 Dataset Composition、Split 与 Leakage

Dataset Composition 必须记录：

- 样本/记录数量；
- 时间范围；
- Source 分布；
- 类别/群体/场景分布；
- 语言、地区、设备、渠道和环境分布；
- 缺失、异常、重复和近重复；
- Synthetic、Augmented、Human-generated 和 Machine-generated 比例；
- Label/Annotation 覆盖和争议；
- Exclusion、Filter 和 Sampling；
- Known Gaps 和 Out-of-scope。

Split 控制必须：

1. 固定 Split Purpose、Rule、Ratio、Seed 和 Revision；
2. 评价同一实体、会话、时间序列、文档族或近重复跨 Split 泄漏；
3. 固定训练、验证、测试、评估和 Benchmark 的访问角色；
4. 将评估数据进入训练、提示优化、Embedding 调整或人工调参视为 Contamination Event；
5. 变更 Split 后重新执行 ADQ 和适用模型评价；
6. 禁止为提高结果而删除困难样本且不记录；
7. 禁止在看过 Test/Evaluation Result 后静默重定义 Dataset。

### 11.9 Label、Annotation 与 Human Data Work

Label/Annotation 必须具有：

- Specification ID 和 Revision；
- Task、Unit、Class/Schema 和边界；
- Included/Excluded 示例；
- Ambiguity 和 Escalation 规则；
- Annotator Qualification 和 Training；
- Tool/Platform、Version 和 Configuration；
- Assignment、Blind/Non-blind 和 Conflict 规则；
- Gold/Reference Set 来源和限制；
- Inter-annotator、Expert Review 或其他 Quality Check；
- Revision、Appeal、Correction 和 History；
- Privacy、Security、劳动与访问约束；
- Output Manifest 和 Evidence。

Label Agreement 高不自动证明 Ground Truth 正确。专家结论、用户反馈、弱监督、模型生成标签和 Synthetic Label 必须分别标识。

### 11.10 Transformation、Cleaning 与 Augmentation

所有 Data Transformation 必须记录：

- Input Revision；
- Code/Query/Rule/Model Revision；
- Tool、Runtime、Library 和 Configuration；
- Parameter、Locale、Timezone 和 Seed；
- Filter、Join、Dedup、Aggregation 和 Window；
- Normalization、Standardization、Encoding 和 Imputation；
- Cleaning、Outlier 和 Missing Handling；
- Augmentation、Synthetic Generation 和 De-identification；
- Output Revision、Manifest、Count 和 Hash；
- Reject/Quarantine Data；
- Validation Result 和 Evidence；
- Operator、Run ID 和 Time。

禁止原位覆盖 Source Snapshot。Manual Fix 必须通过受控 Patch、Reason、Reviewer 和 New Revision 实施。

### 11.11 RAG 与 Corpus 控制

RAG/Corpus 除 DSR 通用字段外必须记录：

- 文档/知识 Source、Title、Owner、Version 和有效日期；
- Acquisition、License、Access、PII 和 Prohibited Use；
- Parsing、OCR、Normalization 和 Dedup Revision；
- Chunking Strategy、Size、Overlap、Boundary 和 Metadata；
- Embedding Model、Version、Configuration 和 Dimension；
- Index、Vector Store、Namespace、Revision 和 Build Run；
- Retrieval Filter、Access Enforcement 和 Ranking Configuration；
- Freshness、Supersession、Deletion 和 Re-index Trigger；
- Evaluation Query、Expected Evidence、Corpus Coverage 和 Retrieval Metric；
- Prompt/Response 中 Source Citation 和 Unsupported Output 处理；
- Poisoning、Prompt Injection、Sensitive Content 和 Unauthorized Retrieval 接口 E02；
- Consumer、Model/Application Revision 和 Rollback。

Corpus 中 Source 被替代、撤销授权、到期或要求删除时，必须查询 Chunk、Embedding、Index、Cache、Evaluation Set 和 Generated Artifact 的派生链。

### 11.12 Synthetic、Feedback 与 Online Data

Synthetic Data 必须记录：

- 生成目的；
- Source/Input Boundary；
- Generator/Model/Tool Version；
- Prompt/Rule/Parameter/Seed；
- Synthetic Ratio；
- 与真实数据的相似性、重复和泄漏检查；
- Known Artifact 和 Limitations；
- License、Privacy、Security 和 Retention；
- 质量评价和适用范围。

Feedback/Online Data 必须记录：

- Collection Purpose、Notice 和 Authority；
- User/System/Agent Source；
- Event、Time、Environment 和 Version；
- Selection Bias 和 Missing Feedback；
- Abuse、Poisoning 和 Manipulation Risk；
- 回流到 Training、RAG、Evaluation 或 Rule 的批准路径；
- Holdout、Rollback 和 Monitoring；
- Prohibited Automated Learning 条件。

禁止把 Production Feedback 自动写入训练集或长期知识库。

### 11.13 Lineage 与 Provenance

DLG 必须支持：

```text
Source Revision
  → Acquisition Run
  → Raw Snapshot
  → Transformation Run(s)
  → Curated Dataset Revision
  → Split/Corpus/Index Revision
  → Consumer/Model/Report/Decision
```

每个 Node 至少有 Asset ID、Revision、Owner、Time、Classification 和 Location Reference；每个 Edge 至少有 Transformation/Transfer、Run ID、Input/Output Revision 和 Evidence。

Lineage 断链时：

1. Status = Broken 或 Partial；
2. 禁止把受影响 Dataset 判为完全可审计；
3. 创建 DIR；
4. 识别受影响 Consumer、Model、Report、Decision 和 Gate；
5. 在恢复前执行 Quarantine、Conditional Use 或 Stop；
6. 修复后由独立 Reviewer 验证。

### 11.14 Access、Security、Privacy 与 Compliance

E03 必须消费 E02 的：

- Data Classification；
- Identity 和 Authorization；
- PII Register；
- Privacy Impact；
- Compliance Obligation；
- Security Requirement 和 Architecture；
- AI Impact；
- Vulnerability 和 Incident。

数据治理记录中只保存 Secret Reference，不保存 Credential 明文。敏感样本、PII、商业秘密和受限文本禁止进入普通 ADQ、DIR、Log、Screenshot 或 Prompt；应使用聚合、Hash、Tokenized ID、受控 Evidence Locator 或批准的 Redaction。

### 11.15 Retention、Deletion 与 Legal Hold

RDR 必须区分：

- 活动数据；
- Raw Snapshot；
- Intermediate/Derived Data；
- Training/Validation/Test/Evaluation Dataset；
- Corpus、Chunk、Embedding 和 Index；
- Backup、Cache 和 Replica；
- Quality Evidence；
- Audit、Approval 和 History。

删除范围必须可证明覆盖派生资产；无法删除的技术、法律或依赖限制必须记录。匿名化结论必须经适用 E02 Authority 确认，禁止把 Masking、Encryption、Pseudonymization 或 Access Revocation 自动称为匿名化。

### 11.16 数据命令和工具控制

所有 E03 执行必须使用参数化、可审计的命令结构。以下是规范结构，不规定具体 CLI：

```text
data-control run
  --run-id <ARR-or-EXEC-id>
  --tool <name@version+digest>
  --operation <profile|validate|compare|transform|label|export|delete>
  --target <asset-id@revision>
  --partition <approved-partition>
  --environment <approved-environment>
  --rule-set <dqs-id@revision>
  --parameters <controlled-parameter-reference>
  --authority <approval-reference>
  --mode <read-only|dry-run|write>
  --limit <record-or-byte-budget>
  --timeout <approved-timeout>
  --output <controlled-evidence-location>
  --redaction <redaction-policy>
  --stop-on <approved-stop-conditions>
```

强制命令规则：

1. Tool、Rule、Query、Code、Configuration 和 Dependency 必须固定 Revision；
2. Target 必须包含 Asset ID、Revision、Environment、Tenant 和 Partition；
3. 参数来自受控引用，禁止未审查字符串拼接；
4. 默认使用 Read-only 和 Dry-run；
5. Write、Export、Delete、Re-label、Backfill、Anonymize 和 Production 操作必须单独授权；
6. 查询必须限制扫描量、输出量、并发、超时和成本；
7. 输出必须按分类 Redact，并进入受控位置；
8. Stop Condition 必须覆盖 Scope 超出、异常量、权限错误、成本超限、质量恶化和不可逆风险；
9. Mutation 前必须有 Snapshot、Transaction 或等价恢复策略；
10. Command Exit Code 只表示执行状态，不表示 Data Quality Result；
11. 所有真实执行进入 C09 ARR 和 C05 Evidence；
12. 禁止在文档、聊天或命令行参数中暴露 Secret 或真实受限样本。

### 11.17 Fail Closed、Quarantine 与恢复

以下情况必须 Fail Closed 或 Quarantine：

- Source、Authority、License 或 Intended Use Unknown；
- Dataset Revision、Manifest 或 DQS Revision Unknown；
- Critical Quality Dimension Fail；
- Evaluation/Training Contamination；
- Lineage Broken 且影响不可界定；
- Breaking DCO Change 未批准；
- PII、Security、Compliance 或 Legal Hold 阻断；
- Tool/Rule/Query Version 不可重建；
- 输出发生未授权泄露；
- 删除或写入范围超出批准边界；
- Gate Evidence Invalidated。

恢复必须记录 Root Cause、修复 Revision、重测 Evidence、Consumer Confirmation、Residual Risk 和 Approver。

## 12. 状态模型与转换

### 12.1 状态模型

| 产物 | 状态模型 |
|---|---|
| DRS、DCO、DDY、DQS、DLG、DSR、ADQ、RDR | DOC |
| DIR | CASE |

E03 禁止建立私有 State。Activation Status、Quality Result、Fitness、Compatibility、Lineage Status、License Result 和 Remediation Result 只能作为领域字段。

### 12.2 DOC 转换规则

```text
Draft → In Review → Approved → Baselined → Superseded/Retired
                  ↘ Changes Required → Draft
                  ↘ Rejected
```

强制规则：

1. Draft 禁止作为生产 Gate 的唯一正式输入；
2. In Review 必须固定 Revision；
3. Approved 必须由有权人类决定；
4. Baselined 必须引用 C11 Baseline；
5. Baselined 后变更必须创建 C11 Change 和新 Revision；
6. Superseded 必须引用替代资产；
7. Retired 必须完成 Consumer、Retention、Disposal 和 History 检查。

### 12.3 DIR 转换规则

```text
Open → In Progress → Resolved → Closed
            ↕ Blocked        Closed → Reopened → In Progress
            ↘ Cancelled
```

DIR Closed 必须同时满足：

- Validity 已判断；
- 影响范围已固定；
- Root Cause 已记录；
- 临时控制已解除或转为正式控制；
- 修复 Revision 可定位；
- 原 DQS 或批准的新 DQS 重测完成；
- Consumer 影响已处理；
- Residual Risk 已接受或消除；
- Independent Reviewer 已复核；
- Evidence 和 History 已保存。

### 12.4 状态边界

禁止以下混用：

| 错误 | 正确 |
|---|---|
| `State = Pass` | `State = Approved/Baselined`，`Quality Result = Pass` |
| `State = Active` | `Activation Status = Active` |
| `State = Compatible` | `Contract Compatibility = Compatible` |
| `State = Fit` | `Data Fitness = Fit for Intended Use` |
| `State = Fixed` | `DIR State = Resolved/Closed`，`Remediation Result = Effective` |
| `State = Deleted` | `Disposal Result = Completed`，适用记录 State 保持 REC/DOC 模型 |

Unknown State 必须报错，禁止映射到 Draft、Open 或其他近似值。

### 12.5 Member Status

DRS Set、DDY、DLG 和其他集合成员如需成员状态，必须：

1. 明确标为 Member Status；
2. 使用该集合批准的受控值；
3. 不覆盖集合资产自身 DOC State；
4. 每次成员变化保留 Source、Revision、Time 和 History；
5. 成员状态值进入 DQS/DDY 定义或 C10 治理。

### 12.6 Evidence Invalidated

当 Source、Dataset、Rule、Query、Tool、Environment、Threshold、Intended Use 或 Standard Revision 变化时，Owner 必须判断旧 Evidence 是否 Invalidated。失效 Evidence 禁止继续支持 Pass、Fit、Closure 或 Gate；必须保留失效原因和替代 Evidence。

## 13. 正式产物最低内容

### 13.1 通用必填信息

九类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。数据资产 Scope、Legal Hold、Unknown、Pending 和 Not Applicable 的领域限制按本规范第 5.5 节处理。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 E03 类型专属要求。

### 13.2 DRS Data Requirement Set

除通用字段外必须包含：

- Business Purpose；
- Intended Use 和 Prohibited Use；
- Data Subject/Object；
- Decision/Feature/Model/Report/Metric；
- Stakeholder 和 Consumer；
- Semantics；
- Source 和 Authority；
- Quality；
- Timeliness；
- Access 和 Classification；
- Retention；
- Privacy/Security/Compliance；
- Acceptance；
- Verification；
- Risk、Assumption、Constraint 和 Dependency；
- REQ/ACP Trace；
- Scope、Owner、Review 和 Baseline。

### 13.3 DCO Data Contract

除通用字段外必须包含：

- Provider；
- Consumer；
- Dataset/Event/Interface；
- Environment 和 Scope；
- Schema Concept；
- Semantics；
- Identifier、Time、Order、Cardinality 和 Null；
- Quality SLO；
- Measure、Threshold 和 Breach；
- Version 和 Compatibility；
- Deprecation、Change Notice 和 Migration；
- Access、Classification、Privacy 和 Security；
- Retention 和 Prohibited Use；
- Owner、Support、Escalation；
- Verification 和 Evidence；
- DRS/DDY/DQS/DLG Trace。

### 13.4 DDY Data Dictionary

除通用字段外，每个成员必须包含：

- Data Item ID；
- Formal Business Name；
- Business Definition；
- Conceptual Data Type；
- Allowed Values/Range；
- Unit、Currency、Locale、Timezone 或 Encoding；
- Null/Unknown/Not Applicable Semantics；
- Source；
- Owner/Steward；
- Classification；
- PII/Sensitive Indicator；
- Quality Rule；
- Derived Logic；
- Physical Mapping；
- Related Asset；
- Effective/Deprecated Revision；
- Replacement 和 History。

### 13.5 DQS Data Quality Specification

除通用字段外，每项质量要求必须包含：

- Quality Characteristic；
- Intended Use；
- Business Risk；
- Requirement；
- Target Entity；
- Measure ID；
- Base Measure；
- Function；
- Data Source；
- Population/Sample；
- Unit/Scale/Direction；
- Threshold 和 Basis；
- Measurement Frequency；
- Environment 和 Tool Independence；
- Owner；
- Reviewer；
- Failure Action；
- Limitation；
- Evidence；
- Version 和 Change Trigger。

### 13.6 DLG Data Lineage

除通用字段外必须包含：

- Data Asset/Node ID；
- Source；
- Input Revision；
- Acquisition/Transformation；
- Run ID；
- Code/Query/Rule/Tool Revision；
- Output Revision；
- Consumer；
- Environment；
- Processing Owner；
- Time Range；
- Classification；
- Quality Impact；
- Contract/Dictionary/Quality Links；
- Broken/Partial Link；
- Verification 和 Freshness；
- History。

### 13.7 DSR Dataset or Corpus Record

除通用字段外必须包含：

- Intended Use 和 Prohibited Use；
- Source 和 Provider；
- Acquisition Method 和 Authority；
- License/Use Restriction；
- Time、Region、Language、Population 和 Coverage；
- Composition；
- Representativeness、Balance、Diversity 和 Known Gap；
- Transformation、Cleaning、Augmentation 和 Synthetic Ratio；
- Label/Annotation；
- Sensitive Information、PII 和 Classification；
- Split/Partition；
- Contamination/Leakage Check；
- Dataset Revision、Manifest 和 Hash；
- DDY/DQS/DLG；
- Quality Result；
- Consumer；
- Retention/Deletion；
- Limitation 和 Review Trigger。

### 13.8 ADQ AI Data Quality Report

除通用字段外必须包含：

- Dataset/Corpus ID 和 Revision；
- Intended Use、Task、Population 和 Environment；
- DQS Revision；
- Measurement Run、Tool、Rule 和 Evidence；
- Quality Characteristic；
- Measure、Raw Value、Unit、Threshold 和 Result；
- Accuracy、Completeness、Consistency 等适用通用维度；
- Representativeness、Balance、Diversity、Relevance 等适用 AI 维度；
- Bias/Skew Observation；
- Missing、Outlier、Duplicate 和 Near-duplicate；
- Label/Annotation Quality；
- Split、Leakage 和 Contamination；
- Drift 和 Time Limitation；
- License/Privacy/Security Limitation；
- Affected Consumer/Model/Report；
- Risk；
- Conclusion；
- Action、Owner 和 Due；
- Independent Reviewer；
- Conditional Pass 条件；
- Next Review 和 Invalidation Trigger。

### 13.9 RDR Data Retention and Disposal Rule

除通用字段外必须包含：

- Data Category；
- Purpose 和 Scope；
- Retention Basis；
- Start Event；
- Retention Period；
- Active/Archive Boundary；
- Archive Method 和 Location Reference；
- Delete/Anonymize Method；
- Backup、Replica、Cache、Derived Data 和 Index；
- Legal Hold；
- Authority；
- Owner/Executor/Reviewer；
- Verification Evidence；
- Exception 和 Expiry；
- Conflict 和 Escalation；
- Review Cycle；
- Supersession 和 History。

### 13.10 DIR Data Issue and Remediation Record

除通用字段外必须包含：

- Issue Description；
- Discovery Source；
- Detection Time；
- Affected Data Asset/Dataset Revision；
- Affected Consumer、Decision、Model、Report 和 Time；
- Quality Dimension；
- Issue Validity；
- Evidence；
- Impact 和 Severity Context；
- C02 Risk；
- Root Cause；
- Temporary Control；
- Owner 和 Due；
- Remediation；
- Change/Fix Revision；
- Verification 和 Evidence；
- Remediation Result；
- Residual Risk；
- Closure Criteria；
- Independent Reviewer；
- Reopen Trigger；
- Communication 和 History。

## 14. 质量要求

### 14.1 DRS

- 100% Data Requirement 可追踪到 Need/PRD/REQ/Risk；
- 每项 Data Requirement 有 Intended Use、Owner 和 Verification；
- 不得存在无 Consumer 或无业务用途的数据采集要求；
- Unknown 和 Assumption 必须显式；
- Prohibited Use 必须在高风险或复用场景明确；
- 与 C04 REQ 不得发生身份复制。

### 14.2 DCO

- Provider、Consumer、Dataset/Event 和 Revision 唯一；
- Schema 和 Semantics 均完整；
- Quality SLO 可测量；
- Compatibility 和 Breaking Change 判定可复核；
- Change Notice、Migration 和 Rollback 可执行；
- Consumer 清单与 DLG 一致；
- Security、Privacy、Retention 和 Prohibited Use 无冲突。

### 14.3 DDY

- 每个成员有稳定 ID 和正式业务定义；
- 同一业务概念没有未解决冲突定义；
- Unit、Time、Null 和 Allowed Value 语义明确；
- Derived Field 可重建；
- Physical Mapping 与业务定义分离；
- Deprecated 项有替代、Consumer 和迁移期；
- Classification 与 E02 一致。

### 14.4 DQS

- 每个维度关联 Intended Use 和 Risk；
- Measure 可重复、可解释、可验证；
- Threshold 具有业务依据；
- Sample 和 Time Window 可重建；
- Tool Default 不作为唯一依据；
- Critical Fail 具有 Stop/Quarantine/Gate 规则；
- Limitation 和 Not Evaluated 不被隐藏；
- 版本变化触发 Evidence Invalidation 评价。

### 14.5 DLG

- Source 至 Consumer 的关键链完整；
- Node 和 Edge 均有 Revision；
- Transformation 可定位 Run、Code/Query/Rule；
- 关键 Consumer 覆盖率为 100%；
- Broken/Partial Link 有 DIR；
- Freshness 可测量；
- 删除和 Change 可执行影响查询；
- 图形视图与机器可查询事实一致。

### 14.6 DSR

- Dataset/Corpus 身份和 Revision 唯一；
- Source、Authority、License 和 Restriction 完整；
- Composition、Coverage 和 Known Gap 明确；
- AI 数据的 Representativeness/Balance/Diversity 已评价；
- Transformation、Label、Split 和 Contamination 可重建；
- PII/Sensitive 分类一致；
- Consumer 和 Prohibited Use 明确；
- Retention/Deletion 可执行；
- Limitation 随数据交付。

### 14.7 ADQ

- 固定 Dataset 和 DQS Revision；
- 每项 Result 保留原始量、函数、阈值和 Evidence；
- 通用维度与 AI 扩展维度按适用性覆盖；
- Missing、Duplicate、Label、Split、Contamination 和 Drift 结果明确；
- Fail 和 Conditional Pass 均有行动；
- Conclusion 不越权声明模型或产品质量；
- Independent Reviewer 明确；
- 报告具有失效触发条件。

### 14.8 RDR

- 每个 Data Category 有 Retention Basis；
- Period、Start Event、Archive 和 Disposal 明确；
- Backup、Replica、Derived Data、Embedding、Index 和 Cache 均已处理；
- Legal Hold 优先级明确；
- 删除/匿名化方法有 Authority 和 Verification；
- 与 E04 Schedule 冲突已升级；
- 处置 Evidence 可审计；
- 历史记录无痕删除被禁止。

### 14.9 DIR

- Issue、Asset、Revision 和 Consumer 精确；
- Validity 和 Root Cause 由 Evidence 支持；
- 临时控制可验证；
- 修复进入 C11 Change；
- 原 Criteria 或批准的新 Criteria 已重测；
- Residual Risk 由有权角色处理；
- Closure 有独立复核；
- Reopen 和复发规则明确。

## 15. 验证、评审与 Gate

### 15.1 验证层次

| 层次 | 目标 | 最低输出 |
|---|---|---|
| Static Completeness | 字段、状态、关系、版本和模板完整 | Check Result |
| Contract Verification | Schema、Semantics、Quality SLO、Compatibility | DCO Evidence |
| Data Quality Measurement | 按 DQS 执行质量测量 | Measurement Evidence |
| Lineage Verification | Source、Transformation、Consumer 和 Revision 可追踪 | DLG Evidence |
| Dataset Verification | Composition、Label、Split、Contamination、Restriction | DSR/ADQ Evidence |
| Intended-use Validation | 数据对 Stakeholder 和任务是否适用 | Validation Record |
| Operational Monitoring | Drift、SLO、Issue、Usage 和 Consumer Feedback | Observation/E05 Record |
| Governance Review | Authority、Risk、Waiver、Retention 和 Gate | C12 Decision |

自动化只负责可自动判断部分。License、Privacy、Representativeness、Fitness、Residual Risk 和 Gate 必须由有权人类复核。

### 15.2 五个 Data Gate

| Gate | 强制输入 | Blocker |
|---|---|---|
| Data Discovery Ready | E03 Applicability、DRS、Owner、Use、Risk | Unknown Trigger、无 Use/Owner |
| Data Acquisition Ready | Source、Authority、DCO、DDY、DQS、RDR | Source/Authority/License Pending |
| Data Provision Ready | DSR、DLG、DQS Result、Access、Consumer | Critical Fail、Lineage Broken、Unknown Revision |
| AI Data Use Ready | DSR、ADQ、Split、Contamination、AIA Link | Not Fit、Contamination、无 Independent Review |
| Data Retirement Ready | Consumer/Dependency、RDR、Legal Hold、Disposal Plan | Active Consumer、Legal Hold、无恢复/验证 |

Gate 名称是 E03 领域检查点，正式决策仍由 C12 GDR 管理。

### 15.3 Release Blocker

以下情形阻断受影响 Data/Feature/Model/Report Release：

- E03 应激活但未完成判定；
- Critical Data Requirement 未满足；
- Data Contract Breaking Change 未批准；
- Source、Authority、License 或 Prohibited Use Unknown；
- Dataset/Corpus Revision 不可识别；
- Critical DQS Result = Fail 或 Not Evaluated；
- ADQ Conclusion = Not Fit；
- Training/Test/Evaluation Contamination；
- Critical Lineage Broken；
- 未处置 PII、Security、Compliance 或 Legal Hold Finding；
- DIR 超期且影响 Gate；
- Conditional Pass 条件过期；
- Tool/Run/Evidence 不可重建；
- Agent 自批或 Reviewer 不独立；
- 不可逆命令无授权、Stop 或恢复。

### 15.4 Conditional Pass

Conditional Pass 必须记录：

- 明确 Scope；
- 未满足项；
- 业务影响；
- 临时控制；
- Owner；
- 完成期限；
- 允许使用边界；
- 禁止使用边界；
- Monitoring；
- Expiry；
- Re-evaluation；
- Approver。

条件到期未完成时自动失效，禁止无期限滚动。

### 15.5 符合性声明

E03 符合性声明必须固定：

- E03 Version；
- Applicable Scope；
- Activation Status；
- Data Asset/Dataset Revision；
- DRS/DCO/DDY/DQS/DLG/DSR/ADQ/RDR/DIR Revision；
- R1 Standard Version；
- Verification Period；
- Open Finding、Waiver 和 Condition；
- Evidence Reference；
- Reviewer 和 Approver。

禁止声明“ISO 数据质量认证”“完全符合 ISO/IEC 5259”或其他未由有权认证过程支持的结论。

## 16. 追踪、审计与记录

### 16.1 必须审计事件

- E03 Activation 决定和重评；
- Data Owner/Steward/Provider/Consumer/Authority 变化；
- Intended Use 和 Prohibited Use 变化；
- Source、Authority、License 和 Classification 变化；
- DCO、DDY、DQS、DLG、DSR、ADQ 和 RDR Revision；
- Dataset Acquisition、Transformation、Label、Split、Provision 和 Decommission；
- Quality Measurement、Result、Review 和 Invalidation；
- Breaking Change、Waiver、Conditional Pass 和 Gate；
- DIR Create、Assign、Block、Resolve、Close、Reopen 和 Cancel；
- Data Export、Write、Backfill、Re-label、Anonymize 和 Delete；
- Unauthorized Access、Leakage、Contamination、Drift 和 Incident；
- Agent/Tool Run、Stop、Failure 和 Output Redaction；
- Baseline、Supersession、Retirement、Correction 和 Disposition。

### 16.2 最小审计字段

| 字段 | 要求 |
|---|---|
| Event ID | 唯一、不可复用 |
| Event Type | 受控值 |
| Actor | 人类、Agent、Service 或 Tool 身份 |
| Authority | Approval/Instruction/Contract Reference |
| Asset | Asset ID、Artifact Type 和 Revision |
| Data Target | Dataset/Partition/Environment/Tenant/Time |
| Action | Read、Measure、Transform、Export、Write、Delete、Decide 等 |
| Before/After | Revision、State、Result 或 Hash |
| Time | 统一时区和精度 |
| Tool/Command | Tool、Version、Digest、Command/Run Reference |
| Evidence | 受控位置、Hash、Classification |
| Outcome | Completed、Failed、Blocked、Stopped 等执行结果 |
| Reason | Change、Finding、Requirement、Risk 或 Authority |
| Reviewer | 适用时的独立复核者 |

审计记录按 E04 管理，不得把真实受限数据正文作为普通审计字段。

### 16.3 敏感记录

1. ADQ 和 DIR 使用聚合、Tokenized ID 或受控 Evidence Locator；
2. DSR 不复制许可全文，只引用受控来源和适用结论；
3. DLG 不暴露 Secret、Credential、完整 Query 参数或未授权 Location；
4. Screenshot 和 Sample 必须 Redact；
5. Prompt、Agent Context 和 Chat 不得保存真实受限 Row；
6. Evidence Access 按最小权限和 Need-to-know；
7. 导出和下载必须记录 Authority、范围、目的、期限和处置；
8. 记录更正使用新记录，不原位擦除历史。

### 16.4 Coverage 和健康指标

| 指标 | 计算规则 |
|---|---|
| Data Requirement Trace Coverage | 有完整上游/下游 Trace 的 DRS 成员数 / 适用成员总数 |
| Contract Consumer Coverage | 已登记 Consumer 数 / 已识别 Consumer 总数 |
| Dictionary Coverage | 有 DDY 映射的数据项数 / 适用数据项总数 |
| Quality Specification Coverage | 有 DQS 的 Critical Data Requirement 数 / 适用 Critical 数 |
| Measurement Freshness | 在规定周期内有有效结果的 Measure 数 / 适用 Measure 总数 |
| Lineage Coverage | 有 Source-to-Consumer Lineage 的 Critical Asset 数 / 适用 Critical Asset 总数 |
| Dataset Documentation Coverage | DSR 必填字段完整数 / 适用字段总数 |
| AI Quality Review Coverage | 有有效 ADQ 的 AI Dataset Revision 数 / 适用 Revision 总数 |
| Open Critical Issue | Open/In Progress/Blocked 的 Critical DIR 数 |
| Overdue Remediation | 超过 Due 的未关闭 DIR 数 |
| Conditional Pass Expiry | 已过期未关闭的 Conditional Pass 数 |
| Retention Coverage | 有有效 RDR 的 Data Category 数 / 适用 Category 总数 |
| Evidence Invalidation Debt | 已失效但尚未替代的 Evidence 数 |

分母为零时报告 Not Applicable 并说明 Scope，禁止报告 100%。指标不得替代逐项 Gate。

## 17. 裁剪、激活、停用与退役

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。E03 的 Active、Conditionally Active、Retiring、Retired、Inactive、Pending、Not Evaluated 必须按统一状态语义解析；Trigger、Unknown 或冲突不得被局部规则降级。

### 17.0 Task Profile 驱动的激活

E03 在 Data/Schema 或 AI/Data Governance Change Surface、数据合同/质量/血缘/保留变化、训练或检索数据集变化、AI 数据风险，或 E03 蓝图触发条件成立时激活。Unknown 数据来源、许可、质量或保留条件必须保持待判定。

稳定 Data Contract、Dictionary、Lineage 或 Retention Rule 可以 `Reference`；实际变化只修订受影响实例。ADQ 是从 DQS、DSR、DIR 和测量 Evidence 生成的派生报告；DIR 只在数据问题实际发生时创建。

### 17.1 P2 保留边界

P2 下禁止裁剪：

- E03 正式文件；
- 双层适用性判定；
- 四类蓝图触发条件；
- 9 类正式产物身份；
- 通用必填字段；
- DOC/CASE 状态模型；
- 公共受控关系；
- Intended Use、Source、Owner、Quality 和 Restriction；
- Data Contract Change 影响分析；
- Quality Measure、Threshold 和 Risk 关联；
- Dataset Revision、Lineage 和 Consumer；
- AI 数据的代表性、标签、Split、污染和限制；
- Retention、Legal Hold 和 Disposal；
- Agent 权限边界；
- Human Approval、Independent Review 和 Gate；
- Template、Checklist 和国际标准条款映射。

未激活只表示目标产品控制暂不执行，不表示允许删除上述规范内容。

### 17.2 允许裁剪

目标产品可以在保留控制目标和记录理由的前提下裁剪：

- 不适用的数据类型；
- 不适用的质量维度；
- 非 AI 产品的 ADQ 实例；
- 不适用的 ML 类型、Label 或 Split；
- 不适用的 RAG/Corpus 字段；
- 低风险产品的角色合并；
- 具体 Tool、Storage、Catalog、Pipeline 和 Platform；
- Measurement Method 和 Sampling Method；
- Template 的物理格式；
- Gate 在迭代中的执行频率。

每项裁剪必须记录：

- Tailoring ID；
- Scope；
- 被裁剪项；
- 不适用理由；
- Risk；
- 替代控制；
- Evidence；
- Owner；
- Approver；
- Expiry；
- Review Trigger。

禁止以“数据量小”“内部使用”“只是原型”“公开数据”“只做 RAG”“模型效果好”作为无 Evidence 的裁剪理由。

### 17.3 激活

E03 激活时必须：

1. 建立 Applicability Decision；
2. 固定 Scope、Product、Environment 和生效时间；
3. 指派 Project Owner、Data Owner、Steward、Quality Owner 和 Reviewer；
4. 识别 Data Asset、Provider、Consumer 和 Source；
5. 创建适用 DRS 至 DIR；
6. 建立 C02 Risk、C04 Requirement、C05 Verification、C10 Trace、C11 Baseline 和 C12 Gate 接口；
7. 完成 E01/E02/E04/E05 适用性接口；
8. 对存量数据执行 Gap Review；
9. 将未知项设为 Pending；
10. 由有权人类批准激活。

### 17.4 停用

从 Active/Conditionally Active 转为 Inactive 前必须：

- 重新执行全部触发条件；
- 证明不存在仍在活动的分析、交换、ML、RAG、Dataset 或决策影响；
- 查询 DLG、Consumer、Model、Report、Metric、Index 和 Dependency；
- 关闭或迁移 Open DIR；
- 处理 DCO、Access、License、Retention、Legal Hold 和 Disposal；
- 保留 DRS 至 DIR 的历史；
- 使工具、账号、Pipeline、Export 和 Schedule 停止或移交；
- 记录 Residual Risk、Approver 和生效时间。

有一个 Consumer、Legal Hold、未完成 Disposal 或 Unknown Trigger 时，禁止进入 Inactive。

### 17.5 退役

E03 Asset 退役必须：

1. 固定 Retiring Scope 和 Revision；
2. 通知 Provider、Consumer、Owner 和 Authority；
3. 完成 Replacement/Migration 或记录无替代；
4. 更新 DCO、DDY、DLG、DSR 和 RDR；
5. 处理 Derived Data、Backup、Cache、Embedding、Index 和 Evidence；
6. 验证 Disposal 或 Archive；
7. 关闭/迁移 DIR、Waiver 和 Conditional Pass；
8. 使旧 Revision 进入 Superseded/Retired，不删除历史；
9. 更新 C10 Trace、C11 Baseline 和 C12 Decision；
10. 由 Independent Reviewer 确认完成条件。

## 18. 与其他规范接口

### 18.1 C01 至 C03

| 规范 | E03 消费 | E03 提供 |
|---|---|---|
| C01 | Need、Evidence、Problem、Product、Intent、Goal | 数据可行性、Source/Quality Limitation、受影响方和验证需要 |
| C02 | Scope、Risk、Assumption、Constraint、Metric、Dependency | Data Risk、Quality Threshold Basis、Provider/Consumer Dependency |
| C03 | PRD、Feature、Scenario、Non-goal、Quality Attribute | DRS、Data Scope、Prohibited Use、Data Feature/Metric 约束 |

E03 不得把数据可获得性当作产品需求成立的 Evidence。

### 18.2 C04 至 C06

| 规范 | E03 消费 | E03 提供 |
|---|---|---|
| C04 | REQ、RQS、Revision、Supersession、Quality Review | DRS、DCO、DQS 对 Requirement 的细化和验证约束 |
| C05 | ACP、Verification Plan、Validation Plan、Evidence、Decision | Measure、Dataset Revision、ADQ、Contract/Lineage Verification 输入 |
| C06 | UX/TDS、Interface、State、Error、Accessibility 和 Architecture Detail | Data Semantics、Contract、Quality、Lineage、Access、Retention 设计约束 |

DQS 不是 Acceptance Criteria；ADQ 不是 Acceptance Decision。

### 18.3 C07 至 C09

| 规范 | E03 消费 | E03 提供 |
|---|---|---|
| C07 | Collaboration Contract、Authority、Handoff、Escalation | Data Role、Access Boundary、Write/Delete Prohibition、Reviewer 分离 |
| C08 | Context Manifest、Source Manifest、Task Packet、Context Validation | DRS/DCO/DDY/DQS/DLG/DSR 的最小上下文和禁止数据 |
| C09 | Agent Plan、ARR、Command、Tool Invocation、Evidence Package | Data Command Structure、Target Revision、Stop、Redaction 和 Output |

Agent Context 必须引用受控数据元数据，禁止嵌入真实受限 Dataset。

### 18.4 C10 至 C12

| 规范 | E03 消费 | E03 提供 |
|---|---|---|
| C10 | Decision、Traceability Matrix、Lineage、Finding、Action | 九类 E03 资产关系、Data Lineage、Quality/Issue Finding |
| C11 | Revision、Snapshot、Baseline、Change、Release Configuration | DCO/DQS/DSR/ADQ Revision、Change Impact、Evidence Invalidation |
| C12 | Review Plan、Gate、Waiver、Risk Acceptance、Health | Data Gate 输入、Blocker、Coverage、Open DIR、Conditional Pass |

所有 E03 Gate 结论必须由 C12 GDR 承载。

### 18.5 E01、E02、E04 与 E05

| 扩展 | 边界接口 |
|---|---|
| E01 | 管理 Data/AI Architecture、Data Flow、Storage、Integration、Fitness 和 Conformance；E03 提供 Contract、Quality、Lineage 和 Dataset 约束 |
| E02 | 管理 Security、Privacy、PII、Compliance、License/Legal Authority 和 AI Impact；E03 不自行作法律结论 |
| E04 | 管理 DRS 至 DIR 文档及 Evidence 的 Metadata、Access、Retention、Legal Hold、Audit、Correction 和 Disposition |
| E05 | 管理 Data Service、Pipeline、Quality SLO 运行、Monitoring、Drift、Incident、Continuity 和 Service Review |

冲突优先处理原则：

1. 法律、监管、Privacy、Security、Safety 和 Legal Hold 阻断优先；
2. 正式 Requirement、Approved Decision 和 Baseline 优先于 Tool Default；
3. 数据规则与记录规则冲突时升级有权 Authority；
4. 未决冲突进入 Pending/Blocked，禁止静默选边；
5. 冲突解决必须进入 C10 Decision 和 C11 Change。

## 19. 参考标准治理

### 19.1 参考层级

| 层级 | 来源 | E03 用法 |
|---|---|---|
| R1 | ISO/IEC 25012:2008 | 通用数据质量模型 |
| R1 | ISO/IEC 25024:2015 | 通用数据质量测量 |
| R1 | ISO/IEC 5259-1:2024 | AI/ML 数据质量概念和生命周期 |
| R1 | ISO/IEC 5259-2:2024 | AI/ML 数据质量特性、度量和报告 |
| R1 | ISO/IEC 5259-3:2024 | 数据质量管理要求与指南 |
| R1 | ISO/IEC 5259-4:2024 | 数据质量过程、ML/分析和标注 |
| R1 | ISO/IEC 5259-5:2025 | 数据质量治理框架 |
| R1 | ISO/IEC 8183:2023 | AI 数据生命周期框架 |
| R2 | 适用法律、监管、合同、许可和组织政策 | 经 E02 COR/Authority 确认后补充 |
| R3 | Tool、Vendor、Paper、Blog、Practice | 实现参考；不得自动成为 Gate |

R1 之间不是替代关系。25012/25024 提供通用层，5259 系列提供 Analytics/ML 扩展，8183 提供 AI 系统生命周期视角。

### 19.2 版本固定

每次引用必须记录：

- 标准编号；
- 正式标题；
- Edition/Year；
- Amendment/Correction；
- Language；
- Source URL 或受控获取位置；
- Access Date；
- 采用条款/主题；
- Applicable Scope；
- Mapping Revision；
- Owner。

禁止使用 `latest`、搜索摘要、产品包占位年份或无版本二手材料作为唯一规范性来源。ISO/IEC 5259-5 必须固定为 2025。

### 19.3 标准变化

标准状态、版本、修正或替代变化时必须：

1. 创建 C11 Change Request；
2. 固定旧版和新版；
3. 比较 Scope、Term、Quality Model、Measure、Process、Role 和 Lifecycle；
4. 识别受影响 DRS、DCO、DDY、DQS、DLG、DSR、ADQ、RDR、DIR；
5. 评价已批准 Threshold 和 Evidence 是否失效；
6. 识别 Tool、Rule、Template、Training 和 Contract 变化；
7. 制定迁移、重测、Consumer 通知和 Gate；
8. 由有权人类批准；
9. 保留旧 Baseline 和 Mapping；
10. 禁止自动覆盖历史结果。

### 19.4 版权与符合性边界

1. 本规范使用 ISO 官方公开产品页和公开目录进行主题映射；
2. 本规范不复制受版权保护的标准全文、表格或全部度量公式；
3. 获取标准全文时必须遵守许可和访问控制；
4. 项目工程字段、代码、状态、模板、阈值和 Gate 不表示 ISO 原文要求；
5. 未取得完整标准、授权审计和适用 Evidence 时，不得声明完整符合；
6. 国际标准为自愿标准，不替代适用法律、监管、合同或专业判断；
7. 标准来源变化必须按第 19.3 节处理。

## 20. 模板、检查清单与国际标准条例映射

### 20.1 Extension Applicability Decision 骨架

```yaml
asset_id:
artifact_type: Extension Applicability Decision
extension: E03
scope:
evaluated_at:
evaluator:
triggers:
  - trigger_id:
    condition:
    result: Yes|No|Unknown|Not Applicable
    evidence:
    reason:
activation_status:
conditions:
owner:
approver:
effective_at:
expires_at:
review_triggers:
trace_links:
history_reference:
```

### 20.2 DRS 骨架

```yaml
asset_id:
artifact_type: DRS Data Requirement Set
state: Draft
current_revision:
business_purpose:
intended_use:
prohibited_use:
data_subject_or_object:
decision_feature_model_report_metric:
stakeholders:
consumers:
semantics:
sources:
quality:
timeliness:
access_classification:
retention:
privacy_security_compliance:
acceptance:
verification:
risks_assumptions_constraints_dependencies:
owner:
trace_links:
history_reference:
```

### 20.3 DCO 骨架

```yaml
asset_id:
artifact_type: DCO Data Contract
state: Draft
provider:
consumers:
dataset_event_interface:
scope_environment:
schema_concept:
semantics:
identifier_time_order_cardinality_null:
quality_slo:
measures_thresholds:
version:
compatibility:
deprecation:
change_notice:
migration_rollback:
access_classification:
privacy_security:
retention_prohibited_use:
owner_support_escalation:
verification_evidence:
trace_links:
```

### 20.4 DDY 成员骨架

```yaml
data_item_id:
formal_business_name:
business_definition:
conceptual_data_type:
allowed_values_or_range:
unit_currency_locale_timezone_encoding:
null_unknown_na_semantics:
source:
owner_steward:
classification:
pii_sensitive_indicator:
quality_rules:
derived_logic:
physical_mappings:
related_assets:
effective_revision:
deprecated_revision:
replacement:
history:
```

### 20.5 DQS Measure 骨架

```yaml
asset_id:
artifact_type: DQS Data Quality Specification
state: Draft
measure_id:
quality_characteristic:
intended_use:
business_risk:
requirement:
target_entity:
base_measures:
function:
data_source:
population_sample_seed:
time_window:
unit_scale_direction:
thresholds:
threshold_basis:
frequency:
environment:
tool_rule_independence:
owner:
reviewer:
failure_action:
limitations:
evidence:
version_change_triggers:
```

### 20.6 DLG Edge 骨架

```yaml
lineage_id:
source_asset_revision:
acquisition_or_transformation:
run_id:
code_query_rule_tool_revision:
input_revision:
output_asset_revision:
consumer:
environment:
processing_owner:
time_range:
classification:
quality_impact:
contract_dictionary_quality_links:
lineage_status:
verification:
freshness:
history:
```

### 20.7 DSR 骨架

```yaml
asset_id:
artifact_type: DSR Dataset or Corpus Record
state: Draft
intended_use:
prohibited_use:
sources_providers:
acquisition_method_authority:
license_use_restrictions:
time_region_language_population:
composition_coverage:
representativeness_balance_diversity:
known_gaps:
transformations_cleaning_augmentation:
synthetic_ratio:
label_annotation:
sensitive_pii_classification:
split_partition_seed:
contamination_leakage_checks:
dataset_revision:
manifest_hash:
ddy_dqs_dlg_links:
quality_result:
consumers:
retention_deletion:
limitations:
review_triggers:
```

### 20.8 ADQ 骨架

```yaml
asset_id:
artifact_type: ADQ AI Data Quality Report
state: Draft
dataset_corpus_revision:
intended_use_task_population_environment:
dqs_revision:
measurement_run_tool_rule_evidence:
results:
  - quality_characteristic:
    measure:
    raw_values:
    unit:
    threshold:
    result:
representativeness_balance_diversity_relevance:
bias_skew:
missing_outlier_duplicate_near_duplicate:
label_annotation_quality:
split_leakage_contamination:
drift_time_limitations:
license_privacy_security_limitations:
affected_consumers:
risks:
conclusion:
actions_owners_due:
independent_reviewer:
conditional_pass_conditions:
next_review:
invalidation_triggers:
```

### 20.9 RDR 骨架

```yaml
asset_id:
artifact_type: RDR Data Retention and Disposal Rule
state: Draft
data_category:
purpose_scope:
retention_basis:
start_event:
retention_period:
active_archive_boundary:
archive_method_location:
delete_anonymize_method:
backup_replica_cache_derived_index:
legal_hold:
authority:
owner_executor_reviewer:
verification_evidence:
exceptions_expiry:
conflicts_escalation:
review_cycle:
supersession_history:
```

### 20.10 DIR 骨架

```yaml
asset_id:
artifact_type: DIR Data Issue and Remediation Record
state: Open
issue_description:
discovery_source_time:
affected_data_assets_revisions:
affected_consumers_decisions_models_reports_time:
quality_dimension:
issue_validity:
evidence:
impact_severity_context:
risk_links:
root_cause:
temporary_control:
owner_due:
remediation:
change_fix_revision:
verification_evidence:
remediation_result:
residual_risk:
closure_criteria:
independent_reviewer:
reopen_triggers:
communication_history:
```

### 20.11 Data Command Control 骨架

```yaml
run_id:
authority_reference:
tool:
  name:
  version:
  digest:
  configuration_revision:
operation:
target:
  asset_id:
  revision:
  partition:
  environment:
  tenant:
  time_range:
rule_query_code_revision:
parameter_reference:
mode: read-only|dry-run|write
resource_limits:
access_secret_references:
output_location_classification:
redaction_policy:
stop_conditions:
snapshot_transaction_rollback:
evidence:
reviewer:
```

### 20.12 P2 生产检查清单

- [ ] E03 Applicability 在 Discovery Ready 前完成；
- [ ] 所有触发条件有 Result 和 Evidence；
- [ ] Unknown 映射 Pending；
- [ ] 编制适用性与 Activation Status 分离；
- [ ] 9 类产物身份未合并；
- [ ] 通用必填字段完整；
- [ ] DOC/CASE State 使用正确；
- [ ] 领域 Result 未注册为 State；
- [ ] DRS 有明确 Business Purpose；
- [ ] Intended Use 和 Prohibited Use 完整；
- [ ] Data Subject/Object 和 Consumer 完整；
- [ ] DRS 100% 引用 C04 REQ；
- [ ] 每项 Data Requirement 有 Acceptance 和 Verification；
- [ ] Source Identity 和 Authority 完整；
- [ ] License/Use Restriction 有有权结论；
- [ ] DCO Provider/Consumer 完整；
- [ ] DCO Schema 和 Semantics 均完整；
- [ ] DCO Quality SLO 可测量；
- [ ] Compatibility 不只检查 Physical Schema；
- [ ] Breaking Change 有 C11 Change；
- [ ] Consumer Impact 通过 DLG 查询；
- [ ] DDY Data Item ID 稳定；
- [ ] DDY Business Definition 无冲突；
- [ ] Unit/Time/Null/Unknown 语义明确；
- [ ] Derived Logic 可重建；
- [ ] DQS 维度关联 Intended Use 和 Risk；
- [ ] DQS Measure 有 Base Measure 和 Function；
- [ ] DQS 有 Target Entity、Unit、Direction 和 Window；
- [ ] Threshold 有业务依据和批准者；
- [ ] Sampling、Seed 和 Limitations 完整；
- [ ] 空分母或执行失败不判 Pass；
- [ ] 关键维度 Fail 不被综合分掩盖；
- [ ] DLG Source-to-Consumer 链完整；
- [ ] DLG Node/Edge 有 Revision；
- [ ] Transformation 有 Run/Code/Query/Rule；
- [ ] Broken/Partial Lineage 有 DIR；
- [ ] DSR Dataset/Corpus Revision 唯一；
- [ ] DSR Manifest/Hash 可定位；
- [ ] Composition 和 Coverage 完整；
- [ ] Representativeness/Balance/Diversity 已评价；
- [ ] Known Gap 和 Limitation 完整；
- [ ] Label/Annotation Specification 固定；
- [ ] Annotator/Tool/Quality Check 完整；
- [ ] Split Rule、Seed 和 Isolation 可重建；
- [ ] Duplicate/Near-duplicate 检查完成；
- [ ] Leakage/Contamination 检查完成；
- [ ] Evaluation Data 无未记录回流；
- [ ] Synthetic Data 比例和生成方法完整；
- [ ] Feedback Data 回流有批准；
- [ ] RAG Source/Chunk/Embedding/Index 可追踪；
- [ ] RAG Access 与 Source 权限一致；
- [ ] Corpus Supersession/Delete 触发 Re-index；
- [ ] ADQ 固定 Dataset 和 DQS Revision；
- [ ] ADQ 保留 Raw Value、Threshold 和 Evidence；
- [ ] ADQ 评价适用通用维度；
- [ ] ADQ 评价适用 AI 扩展维度；
- [ ] ADQ 记录 Bias/Skew/Missing/Pollution；
- [ ] ADQ Conclusion 不越权声明 Model Quality；
- [ ] Fail/Conditional Pass 有 Action、Owner 和 Due；
- [ ] ADQ 有 Independent Reviewer；
- [ ] RDR Basis、Start、Period 和 Disposal 完整；
- [ ] Backup/Replica/Cache/Derived/Embedding/Index 已覆盖；
- [ ] Legal Hold 已检查；
- [ ] 匿名化结论由有权角色确认；
- [ ] Disposal 有 Dry-run、Stop、验证和 Evidence；
- [ ] DIR Asset/Revision/Consumer 精确；
- [ ] DIR Validity、Impact 和 Root Cause 完整；
- [ ] DIR 修复进入 C11 Change；
- [ ] DIR 按批准 Criteria 重测；
- [ ] DIR Closure 有独立复核；
- [ ] Data Command 固定 Tool/Version/Digest；
- [ ] Target 固定 Asset/Revision/Environment/Tenant/Partition；
- [ ] 参数来自受控引用；
- [ ] 默认 Read-only/Dry-run；
- [ ] Write/Export/Delete 有单独授权；
- [ ] 扫描量、输出量、并发、超时和成本受控；
- [ ] Stop、Snapshot、Rollback 完整；
- [ ] Output Redaction 和 Retention 完整；
- [ ] Command Exit Code 未自动写 Pass；
- [ ] Agent 无真实受限数据 Prompt；
- [ ] Agent 无自批；
- [ ] Evidence 由 C05/E04 管理；
- [ ] Invalidated Evidence 未继续支持 Gate；
- [ ] Gate 输入固定 Revision；
- [ ] Critical Fail 阻断；
- [ ] E01/E02/E04/E05 接口完整；
- [ ] 标准版本变化进入 C11；
- [ ] 文末国际标准条款映射完整。

### 20.13 反例

反例 1：

> 数据准确完整，可用于 AI。

不符合：

- 未限定 Intended Use、Dataset Revision、Population 和 Environment；
- “准确”“完整”无 Measure、Function 和 Threshold；
- 无代表性、标签、Split、污染和限制；
- 无 DQS、ADQ 和 Evidence。

反例 2：

> Profile 工具全部绿色，所以数据质量通过。

不符合：

- Tool Result 不等于 Quality Result；
- 未固定 Tool、Rule、Dataset、Sample 和 Time Window；
- 未说明绿色阈值的业务依据；
- 无 Independent Review。

反例 3：

> Schema 没变，因此 Data Contract 向后兼容。

不符合：

- Semantics、Unit、Time、Null、Quality SLO 或 Retention 仍可变化；
- 未查询 Consumer 和 DLG；
- 无 Compatibility Criteria 和 C11 Change。

反例 4：

> 数据来自公开网页，可以自由训练和永久保存。

不符合：

- 可访问不等于取得许可；
- 未确认 Intended Use、License、PII、Prohibited Use 和 Retention；
- 必须由适用 E02 Authority 处理法律与 Privacy 结论。

反例 5：

> 测试集效果不好，删除困难样本后重新测试。

不符合：

- 改变 Evaluation Set 会使原结果失效；
- 删除依据、Change、New Revision 和 Bias Impact 未记录；
- 存在对 Test Set 调参和 Contamination 风险。

反例 6：

> Agent 已自动清洗生产数据并关闭 Issue。

不符合：

- 生产写入需要明确授权、Dry-run、Snapshot、Stop 和 Rollback；
- Agent 不能自批修复和 Closure；
- 必须保留 Source、Fix Revision、重测 Evidence 和 Independent Reviewer。

### 20.14 标准复评清单

- [ ] ISO 产品页 Status/Edition 未变化；
- [ ] ISO Amendment/Correction 已检查；
- [ ] ISO/IEC 25012 仍为现行确认版；
- [ ] ISO/IEC 25024 仍为现行确认版；
- [ ] ISO/IEC 5259-1 至 5259-4 版本未变化；
- [ ] ISO/IEC 5259-5 使用 2025 正式年份；
- [ ] ISO/IEC 8183 版本未变化；
- [ ] 质量特性和生命周期映射未发生冲突；
- [ ] DQS/ADQ Mapping Revision 当前；
- [ ] Tool Rule Set 与采用标准一致；
- [ ] 标准变化已进入 C11 Change；
- [ ] 历史 Baseline 和 Evidence 未被重写。

### 20.15 国际标准条例映射

以下映射依据 ISO 官方产品页和公开预览目录。项目产物代码、状态值、触发阈值、命令字段、模板和 Gate 是本项目工程化控制，不表示国际标准逐字规定。未取得标准全文授权时，不据此声明完整符合性。

| 国际标准及条款 | 条款或公开主题 | 本规范落实位置 |
|---|---|---|
| ISO/IEC 25012:2008 第 2 章 | Conformance | 15.5、19.4 |
| ISO/IEC 25012:2008 5.1 | Inherent and System-dependent Data Quality | 6.1、11.5 |
| ISO/IEC 25012:2008 5.2 | Data Quality Model | 10.6、11.5、13.5 |
| ISO/IEC 25012:2008 5.3.1 | Accuracy、Completeness、Consistency、Credibility、Currentness | 11.5、11.7、14.4 |
| ISO/IEC 25012:2008 5.3.2 | Accessibility、Compliance、Confidentiality、Efficiency、Precision、Traceability、Understandability | 11.5、11.13–11.15 |
| ISO/IEC 25012:2008 5.3.3 | Availability、Portability、Recoverability | 11.5、18.5 |
| ISO/IEC 25024:2015 第 2 章 | Conformance | 15.1、15.5 |
| ISO/IEC 25024:2015 6.1–6.2 | Data Quality Measurement Concepts and Approach | 10.6、11.7、13.5 |
| ISO/IEC 25024:2015 第 7 章 | Format for Documenting Quality Measures | 11.7、20.5 |
| ISO/IEC 25024:2015 8.2–8.6 | QMs for Inherent Characteristics | 11.5、11.7、14.4 |
| ISO/IEC 25024:2015 8.7–8.13 | QMs for Inherent/System-dependent Characteristics | 11.5、11.7、14.4 |
| ISO/IEC 25024:2015 8.14–8.16 | QMs for System-dependent Characteristics | 11.5、18.5 |
| ISO/IEC 25024:2015 Annex A–E | Measure Elements、Target Entities and Measure Indexes | 11.7、13.5、19.4 |
| ISO/IEC 5259-1:2024 5.1.2–5.1.4 | ML、Data Quality Challenges、Sharing and Re-use | 3、10.7、11.1–11.2 |
| ISO/IEC 5259-1:2024 5.2.2 | Model、Measures、Assessment、Improvement、Reporting | 10.6、11.5–11.7、13.8 |
| ISO/IEC 5259-1:2024 5.2.3 | Data Quality Governance | 7、10.10、17 |
| ISO/IEC 5259-1:2024 5.2.4 | Data Provenance | 6.2、11.2、11.13 |
| ISO/IEC 5259-1:2024 5.3.2.2–5.3.2.7 | Requirement、Planning、Acquisition、Preparation、Provisioning、Decommissioning | 9、10.3–10.9、17.5 |
| ISO/IEC 5259-1:2024 5.3.3 | Data Security and Privacy | 11.14、18.5 |
| ISO/IEC 5259-2:2024 5.1–5.2 | DQ Components and Model | 10.6、11.5–11.7 |
| ISO/IEC 5259-2:2024 6.2 | Inherent Data Quality Characteristics | 11.5–11.7 |
| ISO/IEC 5259-2:2024 6.3 | Inherent/System-dependent Characteristics | 11.5–11.7、11.13 |
| ISO/IEC 5259-2:2024 6.4 | System-dependent Characteristics | 11.5、18.5 |
| ISO/IEC 5259-2:2024 6.5.1–6.5.9 | Auditability、Balance、Diversity、Effectiveness、Identifiability、Relevance、Representativeness、Similarity、Timeliness | 11.6–11.8、13.7–13.8 |
| ISO/IEC 5259-2:2024 第 7 章 | Implementing DQ Model and Measures | 10.6、11.7、14.4 |
| ISO/IEC 5259-2:2024 8.1–8.3 | Data Quality Reporting | 13.8、14.7、20.8 |
| ISO/IEC 5259-3:2024 6.3.1–6.3.10 | Overall DQ Management Requirements | 7、10.6、10.8、15、16 |
| ISO/IEC 5259-3:2024 6.4 | Work Products | 8、13、20 |
| ISO/IEC 5259-3:2024 7.2.2.1–7.2.2.8 | Motivation、Specification、Planning、Acquisition、Preprocessing、Augmentation、Provisioning、Decommissioning | 9、10、11、17 |
| ISO/IEC 5259-3:2024 7.2.4 | Verification/Validation、Change、Configuration、Risk | 9.3、12.6、15、18 |
| ISO/IEC 5259-3:2024 7.3.1–7.3.8 | Lifecycle Requirements and Recommendations | 10.3–10.9、11.1–11.15 |
| ISO/IEC 5259-3:2024 8.3.1 | Verification、Validation、Lifecycle Quality Gates and Improvement | 10.6、15 |
| ISO/IEC 5259-3:2024 8.3.2–8.3.4 | Configuration、Change and Risk Management | 9.3、12、15、18.4 |
| ISO/IEC 5259-3:2024 第 9 章 | Data Quality in Supply Chains | 10.4、11.2、13.3 |
| ISO/IEC 5259-3:2024 第 10 章 | Management of Data Processing Tools | 11.10、11.16、16 |
| ISO/IEC 5259-3:2024 第 11 章 | Management of Data Quality Dependencies | 8.3、10.4、11.13 |
| ISO/IEC 5259-3:2024 第 12 章 | Project-specific DQ Management | 3、7、10、13、17 |
| ISO/IEC 5259-4:2024 第 5 章 | Data Quality Process Principles | 9、10.6、15.1 |
| ISO/IEC 5259-4:2024 6.2–6.5 | Planning、Evaluation、Improvement、Validation | 10.6、10.8、14、15 |
| ISO/IEC 5259-4:2024 7.2–7.7 | ML Data Requirement、Planning、Acquisition、Preparation、Provisioning、Decommissioning | 9、10.7、11.8–11.12 |
| ISO/IEC 5259-4:2024 7.5.5–7.5.11 | Composition、Labelling、Annotation、Assessment、Improvement、De-identification、Encoding | 11.8–11.12、13.7–13.8 |
| ISO/IEC 5259-4:2024 8.1–8.4 | Data Labelling Principles、Methods and Process | 11.9、14.6 |
| ISO/IEC 5259-4:2024 第 9 章 | Roles of Participants | 7、11.9 |
| ISO/IEC 5259-4:2024 第 10 章 | Semi-supervised ML Data Process | 10.7、11.8–11.12 |
| ISO/IEC 5259-4:2024 第 11 章 | Reinforcement Learning Data Process | 10.7、11.8–11.12 |
| ISO/IEC 5259-4:2024 第 12 章 | Analytics Data Process | 3、10.6–10.7、11.5–11.10 |
| ISO/IEC 5259-5:2025 5.1–5.3 | Foundation、Ambiguous Responsibilities、Purpose | 2、6、7、10.10 |
| ISO/IEC 5259-5:2025 6.1–6.7 | Governance Framework、Principles、Strategy、Planning、Accountability、Risk、Processes | 7、9、10、15–17 |
| ISO/IEC 5259-5:2025 7.1–7.7 | Responsibilities of Governing Body | 7.1–7.2、10.10、15、17 |
| ISO/IEC 5259-5:2025 8.1–8.4 | Responsibilities of Management | 7、10、14–16 |
| ISO/IEC 8183:2023 第 5 章 | Data Life Cycle Overview | 9.1、19.1 |
| ISO/IEC 8183:2023 6.2 | Idea Conception | 9.2、10.3、11.1 |
| ISO/IEC 8183:2023 6.3 | Business Requirements | 10.3、13.2、18.1 |
| ISO/IEC 8183:2023 6.4 | Data Planning | 9.4、10.3–10.7 |
| ISO/IEC 8183:2023 6.5 | Data Acquisition | 10.7、11.2、13.7 |
| ISO/IEC 8183:2023 6.6 | Data Preparation | 11.8–11.12、13.6–13.8 |
| ISO/IEC 8183:2023 6.7 | Building a Model | 11.8、13.7–13.8、18.5 |
| ISO/IEC 8183:2023 6.8–6.9 | Deployment and Operation | 9.3、11.12、16.4、18.5 |
| ISO/IEC 8183:2023 6.10–6.11 | Data and System Decommissioning | 10.9、11.15、17.4–17.5 |

规范性国际标准来源：

1. ISO, [ISO/IEC 25012:2008 — Data quality model](https://www.iso.org/standard/35736.html)。
2. ISO, [ISO/IEC 25024:2015 — Measurement of data quality](https://www.iso.org/standard/35749.html)。
3. ISO, [ISO/IEC 5259-1:2024 — Overview, terminology, and examples](https://www.iso.org/standard/81088.html)。
4. ISO, [ISO/IEC 5259-2:2024 — Data quality measures](https://www.iso.org/standard/81860.html)。
5. ISO, [ISO/IEC 5259-3:2024 — Data quality management requirements and guidelines](https://www.iso.org/standard/81092.html)。
6. ISO, [ISO/IEC 5259-4:2024 — Data quality process framework](https://www.iso.org/standard/81093.html)。
7. ISO, [ISO/IEC 5259-5:2025 — Data quality governance framework](https://www.iso.org/standard/84150.html)。
8. ISO, [ISO/IEC 8183:2023 — Data life cycle framework](https://www.iso.org/standard/83002.html)。
