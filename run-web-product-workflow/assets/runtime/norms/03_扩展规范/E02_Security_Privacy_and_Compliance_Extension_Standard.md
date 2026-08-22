# E02 安全、隐私与合规扩展规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | E02 |
| 英文名称 | Security, Privacy and Compliance Extension Specification |
| 正式文件名 | `E02_Security_Privacy_and_Compliance_Extension_Standard.md` |
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
| 已编制扩展依赖 | E01 V6.3 |
| 生产前调研 | RVR-E02-0001 |
| 后续规范 | E03 至 E05 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule、法律、监管、合同、事故调查和 Evidence 要求保留；批准、义务来源、Risk、PIA、AIA、VUR、验证、Waiver、Disclosure 和更正历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式 Security、Privacy 或 Compliance 约束。E02 当前未激活，不对本规范文档仓库强加目标产品安全控制；未激活不影响本文件必须编制、评审和建立 Git 基线。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品、软件、系统、服务、AI 能力和 Agent 能力的 Security Requirement、Threat Model、Security Architecture、PII 管理、Privacy Impact、Compliance Obligation、Security Verification、Vulnerability Remediation 和 AI Impact 治理。

本规范实现以下目标：

1. 使 Security Requirement 进入 C04 Requirement、C05 Acceptance 和 Verification，而非只存在于安全文档；
2. 使 Asset、Threat Actor、Threat Scenario、Attack Path、Trust Boundary、Control 和 Residual Risk 可追踪；
3. 使 Identity、Authentication、Authorization、Secret、Cryptography、Data、Network、Component、Logging 和 Monitoring 设计受控；
4. 使 PII 的收集、使用、存储、传输、共享、保留、删除和审计具有明确目的、责任和 Evidence；
5. 使 Privacy Risk、AI Impact 和受影响方在设计、发布、运行和重大 Change 时得到评价；
6. 使法律、监管、合同、组织和标准义务由有权角色识别、解释、实施、验证和复核；
7. 使 Web App 根据 Risk 选择并固定 OWASP ASVS 版本和验证级别；
8. 使 LLM 应用根据 Risk 选择并固定 OWASP LLMSVS 版本和验证层级；
9. 使每个 Vulnerability 都有受影响资产、版本、Severity Method、Evidence、Owner、期限、修复版本、复测和 Disclosure 记录；
10. 使安全命令、工具、目标、环境、授权、速率、输出、Stop 和 Evidence 可审计；
11. 防止 Agent 自批安全结论、法律结论、Privacy Impact、AI Impact、Risk Acceptance 或 Release Gate；
12. 防止用自动化扫描成功、工具零发现、单张 Threat Diagram 或通用 Checklist 代替正式判断；
13. 在 E02 未激活、已激活、待判定、条件激活和退役期间保持治理状态可追溯。

## 3. 适用范围

E02 在任一触发条件成立时必须激活：

- 存在账号；
- 存在 Identity；
- 存在 Authentication；
- 存在 Authorization 或 Permission；
- 存在 External API；
- 存在互联网公开服务；
- 处理 PII；
- 处理 Sensitive Information；
- 处理 Payment Information；
- 处理 Secret、Credential、Token、Certificate 或 Key；
- 处于受监管行业；
- 存在法律、监管或合同 Security/Privacy Obligation；
- AI System 对个人、群体或社会产生显著影响。

激活后的 E02 适用于：

- Web App、SaaS、API、Service、Mobile Backend、Internal Tool 和 Agent Capability；
- Product、Initiative、PRD、Requirement、Design、Code、Configuration、Deployment 和 Operation；
- Human User、Service Identity、Machine Identity、Agent、Tool、Plugin、Supplier 和 External Party；
- Personal Data、Sensitive Data、Credential、Secret、Log、Telemetry、Model Input/Output 和 Derived Data；
- Development、Test、Staging、Production、Backup、Disaster Recovery 和 Retirement Environment；
- Security、Privacy、Compliance、AI Impact 和 Vulnerability 的设计、验证、发布、运行和改进；
- P2 档位下 SRS、THM、SAR、PII、PIA、COR、SVP、VUR 和适用 AIA；
- 人类、规则工具、扫描工具、测试工具、CI/CD 和 Agent 参与的安全活动；
- E04 已激活时的记录、元数据、访问、保留、审计、更正和历史恢复控制。

### 3.1 当前仓库状态

当前仓库只生产规范文档，不处理账号、External API、PII、Payment、Secret 或监管业务数据，因此：

1. `编制适用性 = 必须编制`；
2. `当前激活状态 = 未激活`；
3. E02 文件、模板骨架和检查规则必须完成；
4. 当前仓库不创建目标产品 SRS 至 AIA 实例；
5. 后续目标产品在 Discovery Ready 前必须重新执行全部触发条件判定；
6. 任一触发条件为 Unknown 时，禁止判为未激活；
7. 本规范文件中的示例不得包含真实 PII、Secret、Token、Vulnerability Exploit 或受限法律意见。

### 3.2 横向生效边界

E02 激活后：

1. C01 至 C03 继续管理 Evidence、Product、Scope、PRD 和 Feature；
2. C04 继续管理原子 Requirement 和 Requirement Set；
3. C05 继续管理 Acceptance、Verification、Validation 和 Evidence；
4. C06 继续管理 UX 和 Technical Design；
5. C07 至 C09 继续管理 Authority、Context、Agent Run、Command 和 Evidence；
6. C10 继续管理 Decision、Trace 和 Lineage；
7. C11 继续管理 Revision、Snapshot、Baseline、Change 和 Release Configuration；
8. C12 继续管理 Review、Gate、Waiver、Risk Acceptance 和 Product Health；
9. E01 继续管理 Architecture Concern、View、Decision、Fitness 和 Conformance；
10. E02 管理 Security、Privacy、Compliance、Vulnerability 和 AI Impact 的领域控制；
11. E03 管理 Data、Dataset、Model Data、RAG Data 和 Data Quality；
12. E04 管理 Knowledge、Record、Metadata、Access、Retention 和 Audit；
13. E05 管理 Service、SLO、Incident、Continuity 和 Operation。

## 4. 不适用范围

本规范不负责：

- 代替 C02 Risk Register；
- 代替 C04 Requirement Record；
- 代替 C05 Acceptance Criteria、Verification Plan、Evidence 或 Acceptance Decision；
- 代替 C06 Technical Design Specification；
- 代替 C07 Human Authority 或 C09 Agent Run Record；
- 代替 C10 Decision Record 或 Traceability Matrix；
- 代替 C11 Baseline、Change Request 或 Release Configuration；
- 代替 C12 Gate Decision、Exception or Waiver Record 或 Risk Acceptance Record；
- 代替 E01 Architecture Description 或 Architecture Conformance Review；
- 代替 E03 Data Contract、Dataset、Model Card 或 Data Quality；
- 代替 E04 Record、Retention、Audit 或 Disposition；
- 代替 E05 Incident Record、SLO 或 Service Review；
- 提供具体司法辖区法律意见；
- 声明产品、组织、服务或供应商获得 ISO、IEC、OWASP 或监管认证；
- 规定唯一 Threat Modeling Framework、Risk Method、Severity Method、Tool、Scanner、Cloud、Identity Provider 或 Cryptographic Product；
- 保存 Secret 明文、完整 Credential、可直接利用的未授权 Exploit 或 Agent 私有思维链；
- 授权对第三方、共享环境、生产环境或真实个人执行未批准测试。

E02 可以消费上述事实，但禁止：

- 用 SRS 复制并替代 C04 REQ 正文；
- 用 THM 取代 C02 Risk；
- 用 SAR 取代 C06 TDS 或 E01 ARC；
- 用 PII Register 证明处理具有合法依据；
- 用 PIA 或 AIA 取代有权批准；
- 用 COR 代替法律结论；
- 用 SVP 代替执行 Evidence；
- 用 Scanner Report 代替 VUR；
- 用 VUR Severity 自动推导 C02 Risk；
- 用零发现自动推导 Release Gate Pass；
- 用普通 EWR 绕过 Non-waivable Obligation；
- 用 Security 结论覆盖 Safety 结论。

## 5. 规范性用语与受控判定

### 5.1 规范性用语

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

法律、监管、合同、Security、Privacy、Safety、PII、Secret、不可逆数据、Non-waivable Gate 和 Authority Boundary 不得通过普通 EWR 绕过。

### 5.2 扩展适用性判定值

以下值是 E02 Activation Status，不是 DOC、CASE 或 DEC State：

| 值 | 语义 |
|---|---|
| Not Evaluated | 尚未评价；禁止进入 Discovery Ready |
| Pending | 存在未知项或等待 Evidence/Authority；禁止判为未激活 |
| Inactive | 全部触发条件明确为 No |
| Conditionally Active | 在明确 Scope、条件和期限内激活 |
| Active | 任一触发条件成立，E02 完整适用 |
| Retiring | 正在退出但仍需维持整改、通知、保留和历史控制 |
| Retired | 当前 Scope 不再适用；历史资产继续保留 |

### 5.3 触发条件判定值

| 值 | 语义 |
|---|---|
| Yes | 条件已由 Evidence 证实 |
| No | 条件已由 Evidence 证实不成立 |
| Unknown | 缺少充分 Evidence 或 Authority |
| Not Applicable | 条件定义对 Scope 不适用，必须记录理由和批准人 |

`Unknown` 必须映射为 E02 `Pending`，禁止映射为 `Inactive`。

### 5.4 领域判定值

| 字段 | 受控值 |
|---|---|
| Control Applicability | Applicable、Not Applicable、Pending Determination |
| Control Implementation Result | Implemented、Partially Implemented、Not Implemented、Not Verified、Unknown |
| Verification Result | Pass、Fail、Blocked、Not Applicable、Not Evaluated |
| Finding Validity | Untriaged、Confirmed、False Positive、Duplicate、Inconclusive |
| Obligation Applicability | Applicable、Not Applicable、Pending Legal Determination |
| Privacy Impact Result | Controlled、Controlled with Open Treatment、Uncontrolled、Inconclusive |
| AI Impact Result | Controlled、Controlled with Open Treatment、Uncontrolled、Inconclusive |
| Disclosure Disposition | Not Required、Coordinating、Embargoed、Published、Restricted |
| Residual Risk Disposition | Treatment Required、Acceptance Requested、Accepted by Authority、Rejected by Authority、Unknown |

上述字段是领域判断，不得替代正式产物 State、C02 Risk State、C05 Evidence State 或 C12 Gate Outcome。

### 5.5 不适用和未知规则

1. `Not Applicable` 必须记录对象、范围、事实、理由、Reviewer、Approver 和复评触发；
2. `Unknown`、`Pending Determination`、`Not Verified` 和 `Inconclusive` 禁止计为 Pass；
3. 关键字段 Unknown 时，必须分派 Owner、Due Date 和所需 Evidence；
4. 法律适用性 Unknown 时，必须进入 `Pending Legal Determination`；
5. ASVS/LLMSVS Requirement 不适用时，必须逐项保留 Versioned ID 和理由；
6. AIA 不适用时，必须记录 AI 不存在或显著影响触发不成立的 Evidence；
7. 不适用批准不能覆盖新 Evidence；触发条件变化时必须重评。

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Information Security | 保护信息的 Confidentiality、Integrity 和 Availability，并处理适用真实性、问责、不可否认和可靠性要求 |
| Cybersecurity | 面向互联数字环境、系统、服务、网络和使用活动的 Security Risk 管理 |
| Privacy | 与 PII Processing 对个人、权利、自由、尊严和合理预期影响有关的治理领域 |
| Compliance | 对适用法律、监管、合同、组织政策和已采纳标准义务的识别、实施、证明和复核 |
| Safety | 防止对人员、财产或环境造成不可接受伤害；与 Security 分开评价 |
| PII | 能识别、关联或合理关联到自然人的信息；具体法律定义由 COR 和有权角色确认 |
| Sensitive Information | 因法律、合同、业务、个人或 Security 影响要求增强保护的信息 |
| Data Subject | PII 所涉及的自然人；具体法律称谓由 COR 确认 |
| PII Controller | 决定 PII Processing 目的和方式并承担对应责任的组织角色 |
| PII Processor | 代表 PII Controller 处理 PII 的组织角色 |
| Processing | 对信息执行收集、生成、访问、使用、组合、存储、传输、共享、分析、保留、删除或销毁 |
| Asset | 对产品、组织、用户或外部方具有价值并需要保护的对象 |
| Threat | 能利用 Vulnerability 或改变环境而造成不利结果的潜在原因 |
| Threat Actor | 具有能力、机会或意图实施 Threat Scenario 的主体 |
| Threat Scenario | 在明确 Scope 和条件下，Threat Actor 通过 Attack Path 影响 Asset 的场景 |
| Vulnerability | Asset、Control、Process、Configuration 或 Design 中可被利用或导致不利结果的弱点 |
| Control | 修改 Risk 或满足 Obligation/Requirement 的组织、人员、物理或技术措施 |
| Control Objective | Control 预期实现的可验证保护结果 |
| Trust Boundary | 身份、权限、数据、控制或信任假设发生变化的边界 |
| Attack Surface | 可被 Threat Actor 接触并影响 Asset 的接口、入口、依赖和能力集合 |
| Attack Path | Threat Actor 从入口到影响 Asset 的可追踪步骤和前置条件 |
| Security Architecture | Security Boundary、Control、Identity、Data、Network、Component、Decision 和验证接口的受控设计 |
| Privacy Impact | Processing 对个人、权利、自由、尊严、选择、访问、排除或其他利益造成的影响 |
| Compliance Obligation | 来自法律、监管、合同、组织或已采纳标准的受控义务 |
| Vulnerability Severity | 依据固定方法对技术弱点特征和影响作出的领域评级；不等于业务 Risk |
| Security Verification | 按固定 Scope、Baseline、Method、Environment 和 Evidence 验证 Security Requirement/Control 的活动 |
| AI System Impact Assessment | 对 AI System 及可预见用途影响个人、群体和社会的正式、文件化评价 |
| Secret Reference | 指向受控 Secret Store 中对象和版本的引用，不包含 Secret Value |

`Risk` 和 `Residual Risk` 的唯一语义直接适用 C02，Risk Acceptance 权限直接适用 C12；E02 只增加 Security、Privacy、Compliance 和 Safety 专业域的识别、分析与控制要求，不建立平行通用定义。

### 6.1 Security、Privacy、Compliance 与 Safety 边界

1. 同一事件可以同时产生 Security、Privacy、Compliance 和 Safety 影响；
2. 四个领域必须分别记录 Concern、Authority、Criteria、Evidence 和 Conclusion；
3. Security Control 实施不自动证明 Privacy 合法性；
4. Privacy Control 实施不自动证明 Compliance；
5. Compliance Obligation 满足不自动证明产品安全；
6. Safety Risk 不得用 Security Severity 替代；
7. 领域结论冲突时必须进入 C10 Decision、C12 Gate 和对应专业 Authority。

### 6.2 Vulnerability、Risk、Finding 与 Incident 边界

1. Tool Finding 是观察或候选，不是已确认 Vulnerability；
2. 确认后的 Vulnerability 使用 VUR 管理；
3. Vulnerability Severity 描述技术弱点，不替代 C02 Risk；
4. Risk 需要业务情境、Likelihood、Impact、现有 Control 和 Residual Risk；
5. Vulnerability 被利用或造成运行影响时进入 E05 Incident；
6. Incident 关闭不自动关闭 VUR；
7. VUR 关闭不自动接受 Residual Risk；
8. Gate Outcome 由 C12 GTE 管理。

## 7. 角色、职责与职责分离

### 7.1 角色

| 角色 | 必须职责 | 禁止事项 |
|---|---|---|
| Product Owner | 提供业务用途、用户、价值、Scope 和产品取舍 | 单方批准法律、Privacy、Security 或 AI Impact 偏离 |
| Security Authority | 批准 Security Policy、Control Baseline、验证级别和专业例外边界 | 自批自身实现和验证结果 |
| Privacy Authority | 确认 Privacy 角色、PIA 范围、咨询和 Privacy Decision | 用通用 Security 结论替代 Privacy 判断 |
| Compliance/Legal Authority | 确认 Obligation 来源、适用范围、解释、Non-waivable 项和法律结论 | 将搜索摘要或 Agent 输出作为最终法律意见 |
| AI Impact Authority | 批准 AIA Scope、Threshold、影响结论、Control 和复评 | 将模型性能分数等同于社会影响可控 |
| Security Architect | 编制 SAR、Security Boundary、Control Design 和 E01/C06 接口 | 批准自身高风险 Architecture Decision |
| Threat Model Owner | 维护 THM、Asset、Threat、Attack Path 和 Control | 隐藏 Unknown 或未处置 Threat |
| Security Requirement Owner | 维护 SRS 与 C04/C05 Trace | 在 SRS 中创建无 C04 身份的强制 Requirement |
| PII Owner/Steward | 维护 PII 数据生命周期、Owner、Access、Retention 和 Deletion | 自行确定合法依据 |
| Compliance Owner | 维护 COR、Evidence、Review Date 和 Gap | 把 COR 状态写成法律结论 |
| Security Verification Lead | 编制 SVP、固定 Tool/Environment、组织验证和 Evidence | 将 Tool Exit 0 自动写为 Pass |
| Independent Security Reviewer | 独立复核 THM、SAR、SVP、VUR 和 Release 输入 | 复核自身未分离的高风险输出 |
| Vulnerability Owner | 处理 VUR、Remediation、Due、Retest 和 Closure Evidence | 降低 Severity 规避 Gate |
| Disclosure Authority | 决定对供应商、客户、监管方或公众的 Disclosure | 未授权发布 Vulnerability 细节 |
| Environment Authority | 授权 Target、Environment、Account、Window 和测试影响 | 授权超出自身管理边界的目标 |
| Records Steward | 按 E04 管理 Access、Retention、Correction 和 Disposition | 以保密为由无痕删除审计历史 |
| Agent/Automation Operator | 起草、提取、建模、扫描、计算、比对和报告 | 作最终法律结论、Risk Acceptance、Gate、Baseline 或自我批准 |

### 7.2 最低职责分离

以下场景必须分离 Author、Implementer、Verifier 和 Approver：

1. High/Critical C02 Risk；
2. 互联网公开服务；
3. PII、Payment、Credential、Secret 或受监管数据；
4. Privileged Access、Authentication、Authorization 或 Cryptography；
5. Active、Destructive 或 Production Security Test；
6. Non-waivable Obligation；
7. High Severity 或已被利用 Vulnerability；
8. AI 对个人、群体或社会产生显著影响；
9. Risk Acceptance、Waiver、Disclosure 和 Release Gate；
10. Agent 生成或修改关键 Control。

最小规则：

- Agent 不得成为最终 Approver；
- Control Implementer 不得单独接受自己的 Verification；
- Vulnerability Reporter 不得被要求删除不利 Evidence；
- Legal/Compliance Conclusion 必须由有权专业角色确认；
- Risk Acceptance Authority 必须符合 C12；
- Release Authority 不替代 Security、Privacy、Compliance 或 AI Impact Authority。

### 7.3 Agent 使用规则

Agent 可以：

- 提取蓝图、Requirement、Asset、Data Flow、Dependency 和 Control 候选；
- 生成 THM、SAR、PIA、AIA 和 SVP Draft；
- 执行预授权的静态检查、配置检查、测试和证据整理；
- 对固定 Baseline 计算覆盖率、差异和重复项；
- 提出 VUR 候选、Remediation 候选和复评触发；
- 执行 Redaction 和 Secret Pattern 检查；
- 标记冲突、Unknown、过期来源和缺失 Trace。

Agent 禁止：

- 推断未提供的法律、监管或合同义务；
- 声称数据处理具有合法依据；
- 把未确认 Tool Finding 写成 Confirmed Vulnerability；
- 自行选择或降低 ASVS/LLMSVS Level；
- 自行接受 Residual Risk；
- 自行批准 PIA、AIA、SAR、SVP、VUR Closure 或 Gate；
- 执行未授权扫描、枚举、利用、压力、数据提取或外部副作用；
- 在 Context、Command、Log、Screenshot 或 Report 中回显 Secret；
- 删除失败 Evidence、降低 Severity、修改分母或缩小 Scope 以提高通过率；
- 将 Unknown 改写为 No、Inactive、Pass 或 Controlled。

## 8. 受控产物与关系

### 8.1 正式产物

| 代码 | 正式产物名称 | 状态模型 | 核心职责 |
|---|---|---|---|
| SRS | Security Requirement Set | DOC | 汇总 Security Requirement 和验证承接 |
| THM | Threat Model | DOC | 建模 Asset、Threat、Attack Path、Control 和 Residual Risk |
| SAR | Security Architecture | DOC | 定义 Security Boundary 和 Control Design |
| PII | Privacy and PII Register | DOC | 管理 PII Processing 生命周期 |
| PIA | Privacy Impact Assessment | DOC | 评价 Privacy Impact 和 Control |
| COR | Compliance Obligation Register | DOC | 管理 Obligation 来源、适用、实施和 Evidence |
| SVP | Security Verification Plan | DOC | 固定验证 Baseline、Level、Scope、Method、Tool 和 Evidence |
| VUR | Vulnerability and Remediation Record | CASE | 管理 Vulnerability 处置闭环 |
| AIA | AI Impact Assessment | DOC | 评价 AI 对个人、群体和社会的影响 |

九类产物不得合并身份。一个物理文件可以承载多个受控成员，但每个成员必须有独立 ID、Revision、State、Source、Owner、Trace 和 History。

### 8.2 单一事实源

| 事实 | 权威来源 |
|---|---|
| Product/Scope | C01 至 C03 |
| Requirement | C04 REQ/RQS |
| Acceptance/Verification/Evidence | C05 |
| UX/Technical Design | C06 |
| Human Authority | C07 |
| Context | C08 |
| Command/Run/Evidence Capture | C09 |
| Decision/Trace | C10 |
| Revision/Baseline/Change/Release Configuration | C11 |
| Gate/Waiver/Risk Acceptance/Health | C12 |
| Architecture | E01 |
| Security Requirement Index | SRS |
| Threat Model | THM |
| Security Architecture | SAR |
| PII Processing Inventory | PII |
| Privacy Impact | PIA |
| Compliance Obligation | COR |
| Security Verification Planning | SVP |
| Vulnerability Remediation | VUR |
| AI Impact | AIA |

禁止在 E02 复制上游权威正文。E02 必须使用永久 ID、Revision 和受控关系链接。

### 8.3 最低关系链

最低 Trace 必须满足：

```text
Need/Problem/Goal
  → PRD/Feature
  → C04 Requirement
  → SRS Entry
  → THM Threat/Control
  → SAR Control Element
  → SVP Criterion
  → C05 Evidence
  → C12 Gate
  → Release Configuration
```

PII/Compliance/AI 链：

```text
Processing / AI Use / Obligation Source
  → PII / COR / AIA
  → PIA / THM / C02 Risk
  → C04 Requirement
  → SAR Control
  → SVP Criterion
  → C05 Evidence
  → C12 Gate
```

Vulnerability 链：

```text
Finding Source
  → VUR
  → Affected Asset + Version
  → C02 Risk
  → C11 Change
  → Fixed Revision
  → Retest Evidence
  → VUR Closure Review
```

### 8.4 受控关系

E02 必须使用公共关系语义：

- SRS `contains` Security Requirement Reference；
- SRS Entry `addresses` Asset、Threat、Risk 或 Obligation；
- Requirement `designed-by` SAR Control Element；
- Requirement/Criterion `verified-by` C05 Evidence；
- THM `addresses` Asset、Threat 和 C02 Risk；
- Control `constrains` Design、Configuration、Access 或 Processing；
- PIA `addresses` PII Processing 和 Privacy Risk；
- COR Entry `constrains` Requirement、Control、Process 或 Release；
- AIA `addresses` AI Impact Concern 和 Risk；
- VUR `observed-from` Finding Source；
- C11 Change `addresses` VUR；
- SVP `depends-on` SRS、THM、SAR、PII、PIA、COR 和适用 AIA；
- BSL `contains` 固定 Revision；
- 后继资产 `supersedes` 旧资产。

禁止使用未受控关系 related-to 或模糊“相关”。关系方向不确定时必须建立 Trace Link 问题。

## 9. E02 治理生命周期

### 9.1 生命周期

```text
Applicability
  → Context and Asset Identification
  → Requirement and Obligation Identification
  → Threat / Privacy / AI Impact Assessment
  → Control and Security Architecture
  → Verification Planning
  → Authorized Execution
  → Evidence Review
  → Gate and Release
  → Monitoring / Vulnerability / Incident
  → Change / Improvement / Reassessment
  → Retirement
```

### 9.2 启动输入

E02 启动至少需要：

- Product、Initiative、PRD、Scope 和 Environment；
- User、Role、Identity、Permission 和 External Party；
- Interface、API、Data Flow、Dependency 和 Supplier；
- Asset、PII、Sensitive Information、Payment 和 Secret 候选；
- 司法辖区、行业、合同、客户和组织义务候选；
- AI Use、Affected Party、Foreseeable Use 和 Impact 候选；
- C02 Risk、C04 Requirement、C06 Design 和 E01 Architecture；
- 当前 Baseline、Change、Release 和 Incident/Vulnerability History；
- 适用 Authority 和 Decision Boundary。

输入不完整时 E02 保持 Pending，不得用通用 Checklist 填充未知事实。

### 9.3 迭代规则

以下变化必须触发对应产物复评：

1. Scope、User、Role、Identity 或 Permission；
2. External API、Internet Exposure 或 Trust Boundary；
3. PII Category、Purpose、Source、Sharing、Location、Retention 或 Deletion；
4. Supplier、Subprocessor、Model Provider、Plugin、Tool 或 Dependency；
5. Secret、Key、Certificate、Cryptographic Method 或 Credential Flow；
6. Threat Intelligence、Vulnerability、Exploit 或 Incident；
7. Requirement、Architecture、Design、Configuration 或 Release；
8. 司法辖区、法律、监管、合同或组织 Policy；
9. ASVS、LLMSVS、ISO 或内部 Control Baseline；
10. AI Use、Model、Data、Affected Party、Human Oversight 或 Impact Threshold；
11. Verification Tool、Rule Set、Environment 或 Evidence Validity；
12. Risk Criteria、Severity Method、Waiver 或 Acceptance。

### 9.4 阶段完成条件

阶段完成必须同时满足：

- 适用性已由有权人类确认；
- Required Artifact 已创建；
- 必填字段无未处置空值；
- Unknown 有 Owner、Due 和所需 Evidence；
- Requirement、Control、Evidence、Risk、Obligation 和 Release Trace 完整；
- Non-waivable 项无未解决 Fail；
- Secret 未出现在文档、日志或报告；
- 逐项 Review 已完成；
- Authority、Decision、State 和 Revision 可定位；
- C12 Gate 输入已形成。

## 10. 适用性与领域治理过程

### 10.1 Extension Applicability Decision

目标产品必须在 Discovery Ready 前建立 C10 Decision Record，至少记录：

- Product、Initiative、Scope、Environment 和版本；
- 九组触发条件逐项 Yes/No/Unknown/Not Applicable；
- 每项 Evidence；
- PII、Secret、External Exposure、Regulated Activity 和 AI Impact 初判；
- Required Artifact；
- Activation Status；
- Owner、Reviewer、Approver；
- 生效时间、失效时间和复评触发；
- 未解决 Risk、Obligation 和 Blocker；
- E01、E03、E04、E05 联动结论。

### 10.2 强制激活规则

1. 任一触发条件为 Yes，E02 必须为 Active；
2. 多个触发条件成立不降低控制，只增加适用 Scope；
3. AI 显著影响成立时 AIA 必须创建；
4. 仅因 AI 存在但显著影响不成立，不强制 AIA；仍须处理 Security/Privacy/Data Risk；
5. 外部 API 包含仅出站调用和仅入站服务；
6. Internal Tool 处理 Identity、PII 或 Secret 时仍须激活；
7. Test Data 包含真实 PII 时仍须激活；
8. 使用 Managed Service 不转移组织自身责任；
9. 法律或监管触发 Unknown 时状态必须 Pending；
10. 未激活不免除已识别 Risk 进入 C02、C05、C06、C11 和 C12。

### 10.3 Pending 规则

Pending 时：

- 禁止进入 Discovery Ready，除非 C12 明确允许的非风险探索范围；
- 必须列出 Unknown、Evidence Gap、Owner 和 Due；
- 可以编制 Draft 和执行无副作用的只读调研；
- 禁止建立生产账号、接入真实 PII、配置真实 Secret 或公开服务；
- 禁止把默认工具设置当作批准 Control；
- 超期必须升级 C12；
- 新 Evidence 到达后必须重新评估全部受影响触发条件。

### 10.4 Security Risk and Control Process

1. 识别 Scope、Asset、Threat Source、Threat Actor 和 Trust Boundary；
2. 建立 THM；
3. 将 Threat Scenario 映射 C02 Risk；
4. 识别 Security Requirement 和 Obligation；
5. 选择 Control Objective 和 Control；
6. 建立 SAR；
7. 将 Requirement、Control、Acceptance 和 Verification 连接；
8. 分析 Residual Risk；
9. 需要 Acceptance 时进入 C12 RAR；
10. 监测 Control Failure、Threat Change 和 Vulnerability；
11. 通过 C11 Change 维护实现；
12. 通过 C12 Gate 和 Health 复核。

### 10.5 Privacy Process

1. 识别 PII Category、Data Subject、Purpose 和 Processing；
2. 确认 PII Controller、Processor、Joint Controller 或其他适用角色；
3. 在 PII Register 记录完整 Data Lifecycle；
4. 由有权角色确认合法依据责任和 Obligation；
5. 对 Purpose、Necessity、Proportionality 和 Data Minimization 形成评价；
6. 建立 PIA；
7. 识别 Privacy Risk、Affected Party 和 Impact；
8. 设计 Control、Notice、Choice、Access、Correction、Deletion 和 Complaint 接口；
9. 将 Control 转入 C04/C06/C05；
10. 记录咨询、批准、Residual Risk 和复评触发；
11. 监测 Purpose Drift、Unauthorized Sharing、Retention Breach 和 Complaint；
12. 通过 Change、VUR、Incident 和 Gate 处理失败。

### 10.6 Compliance Process

1. 识别法律、监管、合同、组织和已采纳标准来源；
2. 固定 Source Identifier、Jurisdiction/Scope、Version、Effective Date 和 Authority；
3. 由有权角色作 Applicability 和 Interpretation；
4. 在 COR 记录 Requirement Summary，禁止复制不必要全文；
5. 映射 Asset、Process、Requirement、Control、Evidence 和 Owner；
6. 识别 Non-waivable、Deadline、Reporting、Retention 和 Disclosure；
7. 记录实施 Gap 和 CASE Member Status；
8. 通过 C04/C06/C05 实施与验证；
9. 通过 C12 Gate 处理 Nonconformity；
10. 来源变化时进入 C11 Change；
11. 复核日期到期时 Reopen；
12. 保留旧来源、解释、Decision 和 Evidence History。

### 10.7 AI Impact Assessment Process

1. 确认 AI System、Provider/Developer/User 角色和 Foreseeable Use；
2. 确认 Affected Individual、Group 和 Society；
3. 固定 AIA Scope、Timing、Threshold 和 Authority；
4. 记录 Expected Benefit；
5. 识别 Adverse Impact、Distribution、Scale、Duration、Reversibility 和 Uncertainty；
6. 评价 Data、Model、Human Oversight、Security、Privacy、Safety、Fairness 和 Accessibility；
7. 记录 Consultation、Dissent 和 Evidence Limitation；
8. 设计 Control、Restriction、Human Intervention、Monitoring、Appeal 和 Exit；
9. 分析 Residual Impact 和 C02 Risk；
10. 由有权人类批准；
11. 发布前完成；
12. 用途、模型、数据、群体、阈值、事件或监测结果变化时复评。

### 10.8 Vulnerability Management Process

1. 接收 Tool、Researcher、Supplier、User、Incident、Audit 或内部 Review Finding；
2. 创建 VUR，保留 Source 和时间；
3. 验证 Finding Validity；
4. 固定 Affected Asset、Version、Environment 和 Exploit Condition；
5. 使用受控 Severity Method 和 Version；
6. 映射 C02 Risk、Requirement、Control 和 Release；
7. 决定 Containment、Mitigation、Remediation 或 Exception 路径；
8. 分派 Owner、Due、Fix Version 和 Verification Method；
9. 通过 C11 Change 实施；
10. 在独立环境复测；
11. 记录 Disclosure Disposition；
12. 由独立 Reviewer 关闭；
13. 已利用或造成运行影响时进入 E05 Incident；
14. False Positive、Duplicate 和 Inconclusive 仍保留 Evidence。

### 10.9 Security Verification Process

1. 固定 SRS、THM、SAR、PII、PIA、COR 和适用 AIA Revision；
2. 选择 ASVS/LLMSVS 或其他 Control Baseline 的 Version 和 Level；
3. 建立 SVP；
4. 固定 Requirement/Criterion、Method、Environment、Tool、Data 和 Oracle；
5. 进行 Authorization 和 Safety Review；
6. 执行 C09 Run；
7. 捕获 C05 Evidence；
8. 对每个 Criterion 作独立结果判断；
9. Fail/Blocked/Inconclusive 进入 VUR、Risk、Change 或 Gate；
10. 形成 Coverage 和 Residual Gap；
11. 由 C12 Release Ready 作 Gate Decision；
12. 变化后按影响范围重新验证。

### 10.10 Emergency、Incident 与 Disclosure

1. 发现正在发生的泄漏、越权、攻击、数据破坏或重大 Control Failure 时立即执行 C07 Stop；
2. 只允许预授权安全保存、隔离、只读诊断和 Evidence 封存；
3. Incident 使用 E05；E05 未激活时仍须通过 C12 建立受控事件处置并复评 E05；
4. Emergency Change 使用 C11；
5. Notification 和 Disclosure 由 COR、PII/PIA、Incident、Disclosure Authority 和 Legal Authority 决定；
6. Agent 禁止向外部方自主发送 Vulnerability、PII 或 Incident 细节；
7. 通知延迟、范围和内容必须有依据和批准；
8. 事故恢复不自动证明 Root Cause、Remediation 或 Compliance 已关闭。

## 11. Security、Privacy、Compliance 与 AI Control

### 11.1 Asset、Boundary 与 Attack Surface

SRS、THM 和 SAR 必须识别：

- Information、Identity、Service、Component、Infrastructure、Model、Data、Secret 和 Business Process Asset；
- Asset Owner、Value、Classification 和 Applicable Scope；
- System、Network、Tenant、Account、Process、Data 和 Human Trust Boundary；
- External Interface、API、UI、Webhook、File、Message、Admin、Tool 和 Supplier Entry Point；
- Privilege Change、Data Classification Change 和 Trust Assumption；
- Threat Actor Capability、Access、Intent 和 Constraint；
- Attack Path、Precondition、Detection、Control 和 Impact；
- Unknown Asset 和 Shadow Dependency。

禁止以组件清单代替 Asset 价值和 Trust Boundary 分析。

### 11.2 Identity、Authentication 与 Authorization

必须：

1. 为 Human、Service、Machine、Agent 和 Tool Identity 定义唯一性和生命周期；
2. 明确 Enrollment、Proofing、Authentication、Recovery、Suspension、Revocation 和 Deletion；
3. 对每项 Authorization 定义 Subject、Object、Action、Condition、Decision Point 和 Deny Behavior；
4. 使用最小权限、Need-to-know、Least Functionality 和 Time-bounded Access；
5. Privileged Access 必须独立、可审计、短时、可撤销；
6. 默认拒绝未识别 Identity、Scope 或 Condition；
7. 权限变化进入 C11 Change 和 Verification；
8. 防止跨 Tenant、跨 User、跨 Role 和跨 Environment 访问；
9. Session、Token 和 Recovery Control 必须进入 SRS/SAR/SVP；
10. Agent Delegation 不得扩大人类已批准权限；
11. Access Review 必须有频率、Owner、Evidence 和 Removal SLA；
12. Break-glass Access 必须有前置条件、时间限制、审计和事后复核。

### 11.3 Secret、Key 与 Cryptography

必须：

- Secret 只保存 Reference、Version、Owner、Purpose、Scope 和 Rotation Metadata；
- 禁止在 Markdown、Source、Command、Prompt、Log、Screenshot、Ticket 或 Evidence 中保存 Secret Value；
- Key/Credential 的生成、分发、存储、使用、轮换、撤销、备份和销毁受控；
- Cryptographic Objective、Algorithm/Protocol、Parameter、Key Length、Provider 和 Version 可追踪；
- 禁止自制未评审 Cryptographic Algorithm；
- 过期、弱化、撤销和迁移条件明确；
- Production Secret 与非生产隔离；
- Agent、Tool 和 CI 只获得任务所需最小 Secret；
- Secret Access 有主体、时间、用途和审计；
- Secret 泄漏立即 Stop、Rotate、Invalidate、Assess 和 Record；
- Certificate Expiry、Trust Store 和 Revocation 进入监测；
- Cryptographic Change 触发兼容、数据迁移和回滚评价。

### 11.4 Data Protection 与 PII Lifecycle

每类 PII/Sensitive Data 必须定义：

1. Category 和 Data Element；
2. Data Subject；
3. Source；
4. Purpose；
5. Collection Method；
6. Lawful Basis Responsibility；
7. Data Minimization；
8. Accuracy/Correction；
9. Storage Location；
10. Encryption/Protection；
11. Access Role；
12. Internal Use；
13. External Sharing/Recipient；
14. Cross-boundary Transfer；
15. Retention Start、Duration 和 Trigger；
16. Deletion/Anonymization Method；
17. Backup/Replica Handling；
18. Audit/Monitoring；
19. Data Subject Request Interface；
20. Owner、Processor 和 Subprocessor；
21. Incident/Notification Interface；
22. Evidence 和 Last Review。

禁止：

- 因“未来有用”无限收集；
- 因“审计”无限保留完整敏感原文；
- 用 Masking 自动证明 Anonymization；
- 将 Production PII 默认复制到 Test；
- 在 Prompt、Telemetry 或 Analytics 中隐藏新的 Processing Purpose；
- 删除权威审计历史来掩盖不合规处理。

### 11.5 Network、Component、Supplier 与 Supply Chain

必须：

- 固定 Network Zone、Ingress、Egress、Protocol、Port、Service 和 Trust Boundary；
- 对 External Service、Package、Image、Model、Dataset、Plugin、MCP Server 和 Tool 建立 Inventory；
- 记录 Supplier、Version、Source、Integrity、License、Support、Update 和 Exit；
- 对 Dependency Confusion、Tampering、Malicious Update、Compromise 和 Availability 评价 Threat；
- 对 Supplier Access、Subprocessor、Data Location、Incident Notification 和 Deletion 建立 Obligation；
- 使用受控 Artifact Repository 和完整性校验；
- 监测 Vulnerability、End-of-life、Ownership Change 和 Breach；
- 高风险 Supplier Change 进入 C11 Change 和 C12 Gate；
- 禁止因供应商声明而跳过独立验证；
- 退出策略必须覆盖 Credential Revocation、Data Return/Deletion 和 Evidence。

### 11.6 Secure Development、Configuration 与 Change

必须：

1. Security Requirement 在设计前建立；
2. Threat Model 在关键 Design Freeze 前完成；
3. Secure Coding、Review、Static、Dynamic、Composition、Configuration 和 IaC 检查按 Risk 选择；
4. Development、Test 和 Production Environment 隔离；
5. Source、Build、Package、Artifact 和 Deployment Trace 完整；
6. Default Configuration 必须经过安全评价；
7. Debug、Sample、Test Account 和 Unused Capability 在 Release 前删除或禁用；
8. Security Configuration 进入 C11 CI/Baseline；
9. Change 评价 Security、Privacy、Compliance、AI Impact 和 Vulnerability；
10. Emergency Change 保留授权、时间、影响、验证、回滚和事后 Review；
11. Rollback 不得恢复已知 Vulnerability 或撤销强制 Obligation；
12. Release Configuration 必须固定 Control 和 Verification Revision。

### 11.7 Logging、Monitoring 与 Error Handling

必须：

- 定义 Security Event、Privacy Event、Compliance Event 和 AI Anomaly；
- 记录 Actor、Action、Object、Result、Time、Environment 和 Correlation；
- 使用可验证时间源；
- 防止 Log Tampering 和 Unauthorized Deletion；
- 限制 Log 中的 PII、Secret、Token、Prompt、Model Output 和 Vulnerability Detail；
- Redaction 后仍保留审计所需结构；
- Error Message 不向未授权方暴露内部结构和 Sensitive Data；
- Alert 有 Severity Method、Owner、Routing、SLA 和 Escalation；
- Monitoring Coverage 与 Blind Spot 可见；
- Detection Rule 和 Threshold 进入 Revision/Change；
- Alert Suppression 有范围、理由、批准和失效；
- Monitoring Failure 本身产生告警；
- Evidence Retention 服从 E04、COR、PII 和 Incident；
- 监测结果进入 VUR、Incident、AIA、PIA 或 C12 Health。

### 11.8 Privacy by Design

Privacy Control 必须覆盖：

1. Purpose Specification；
2. Necessity；
3. Data Minimization；
4. Transparency/Notice；
5. Choice/Consent Interface；
6. Access/Correction；
7. Retention/Deletion；
8. Sharing/Transfer；
9. Security Safeguard；
10. Accountability/Evidence；
11. Complaint/Appeal；
12. Child、Vulnerable Group 或其他增强保护条件；
13. Automated Decision 和 Human Review；
14. Processor/Subprocessor；
15. Privacy Default；
16. Purpose Drift Detection。

“Consent”只能在有权角色确认其适用时使用，禁止把所有 Processing 都默认标记为 Consent。

### 11.9 Compliance Control

每项 Obligation 必须：

- 指向权威来源，不以新闻、博客或搜索摘要为唯一来源；
- 记录 Jurisdiction/Organization Scope、Version、Effective Date 和 Source Validity；
- 记录 Authority 和 Interpretation Date；
- 摘要化 Requirement，不复制不必要标准或法律全文；
- 指向 Asset、Process、Data、Supplier、Requirement 和 Control；
- 指向 Evidence、Owner、Review Date 和 Gap；
- 标记 Non-waivable、Reporting、Notification、Retention、Deletion 和 Record Requirement；
- 在 Source 变化时触发 Change；
- 在 Applicability 不确定时保持 Pending；
- 在实施后执行独立 Verification；
- 在冲突时升级 Legal/Compliance Authority 和 C10 Decision；
- 在 Gate 中区分 Implemented、Verified 和 Legally Concluded。

### 11.10 AI 与 LLM Control

适用 AI/LLM 时必须评价：

- AI Use、Foreseeable Misuse 和 Prohibited Use；
- Affected Party、Benefit、Adverse Impact 和 Impact Distribution；
- Data/Model Source、Version、Limitation 和 E03 Trace；
- Human Oversight、Intervention、Override、Appeal 和 Exit；
- Prompt Injection、Indirect Injection、Jailbreak 和 Output Manipulation；
- Tool/Plugin/MCP Permission、Parameter Validation 和 Side Effect；
- Model/Provider Credential、Rate、Cost 和 Availability；
- RAG/Memory Tenant Isolation、Access、Poisoning 和 Leakage；
- Training/Fine-tuning/Real-time Learning Authorization 和 Audit；
- Model/Component/Supplier Vulnerability 和 Provenance；
- Output Schema、Validation、Encoding 和 Downstream Trust；
- Monitoring、Anomaly、Abuse、Drift、Incident 和 Decommission；
- LLMSVS 2.0 V1 至 V8；
- ASVS 5.0.0 的一般应用安全要求；
- ISO/IEC 42005 AIA 和 ISO/IEC 23894 AI Risk。

LLMSVS 不替代 ASVS、PIA、AIA、THM、Secure Development 或 C02 Risk。

### 11.11 安全验证命令和工具

每个 Security Verification Command/Tool Run 必须固定：

- Run ID；
- SVP Criterion；
- Tool Name、Version、Digest；
- Rule Set/Plugin/Signature Revision；
- Configuration Revision；
- Command Structure；
- Parameter Source；
- Target Asset 和 Version；
- Environment、Tenant、Account；
- Authorized Scope；
- Permitted Action；
- Prohibited Action；
- Passive/Active/Destructive Classification；
- Rate、Concurrency、Timeout、Budget；
- Test Data Classification；
- Secret Reference；
- Output Redaction；
- Stop Condition；
- Rollback/Recovery；
- Evidence Locator；
- Reviewer。

禁止：

- 在命令参数中写 Secret Value；
- 在未授权目标执行扫描或利用；
- 自动跟随范围外链接、子域、租户、账号或环境；
- 关闭 Rate Limit、Safety Check 或 Audit 以提高覆盖；
- 把工具数据库自动更新当作已批准 Baseline Change；
- 用 Exit 0 代替 Pass；
- 用无发现代替完整覆盖；
- 删除失败输出；
- 在普通日志保存完整敏感响应；
- 让 Agent 自行扩大测试范围。

### 11.12 Fail Closed、Stop 与恢复

必须立即 Stop 的条件：

- Authorization 不可验证；
- Target、Environment、Tenant 或 Version 不一致；
- 命令将超出 Scope；
- 发现 Secret、PII 或受限数据泄漏；
- 产生未批准外部副作用；
- 服务可用性、完整性或数据安全受到影响；
- Tool/Rule/Configuration Revision 漂移；
- Evidence 无法安全保存；
- Agent 尝试绕过 Control；
- Non-waivable Obligation Fail；
- Active Attack 或 Exploitation 迹象；
- Human Authority 撤销。

Stop 后只允许预授权安全保存、隔离、只读诊断、Evidence 封存和通知。恢复必须由有权人类确认新 Scope、Control、Risk、Environment 和 Authorization。

## 12. 状态模型与转换

### 12.1 状态模型

| 产物 | 模型 | 允许状态 |
|---|---|---|
| SRS、THM、SAR、PII、PIA、COR、SVP、AIA | DOC | Draft、In Review、Changes Required、Approved、Baselined、Rejected、Superseded、Retired |
| VUR | CASE | Open、In Progress、Blocked、Resolved、Closed、Reopened、Cancelled |

### 12.2 状态边界

以下字段不得写入 State：

- Activation Status；
- Control Applicability；
- Control Implementation Result；
- Verification Result；
- Finding Validity；
- Obligation Applicability；
- Privacy Impact Result；
- AI Impact Result；
- Severity；
- Disclosure Disposition；
- Residual Risk Disposition；
- Gate Outcome。

### 12.3 DOC 转换规则

1. Draft 只能用于编制；
2. In Review 必须固定被评审 Revision；
3. Changes Required 必须列出 Finding、Owner 和 Due；
4. Approved 必须记录 Approver、Authority、时间和条件；
5. Baselined 必须引用 C11 BSL；
6. Baselined 后修改必须创建 Change 和新 Revision；
7. Rejected 保留原因和 Evidence；
8. Superseded 指向后继资产；
9. Retired 保留历史、义务、风险、通知和处置；
10. Agent 禁止执行 Approved/Baselined。

### 12.4 VUR 转换规则

```text
Open → In Progress → Resolved → Closed
          ↕ Blocked          Closed → Reopened → In Progress
          ↘ Cancelled
```

附加规则：

1. Open 时必须记录 Source 和 Affected Asset；
2. In Progress 时必须有 Owner、Due 和 Treatment；
3. Blocked 必须记录 Blocker、解除 Owner 和 Escalation；
4. Resolved 必须有 Fix/Mitigation Revision 和 Retest Plan；
5. Closed 必须有独立 Retest Evidence 和 Closure Reviewer；
6. False Positive 或 Duplicate 也必须走 Resolved/Closed 并保留依据；
7. 新 Evidence、回归、受影响版本扩大或修复失效必须 Reopen；
8. Cancelled 不能用于规避 Vulnerability；
9. Closed 不表示 C02 Risk 自动关闭；
10. Agent 禁止关闭自身发现或修复的高风险 VUR。

### 12.5 COR Member Status

COR 登记册成员使用 CASE Member Status：

- Open：义务已登记，尚未完成适用性/实现/验证；
- In Progress：正在解释、实施或验证；
- Blocked：缺 Authority、Evidence、Control 或外部条件；
- Resolved：当前周期已形成处理结果，等待独立复核；
- Closed：当前有效范围和复核周期已完成；
- Reopened：来源、Scope、Evidence 或实现变化；
- Cancelled：经有权确认该登记项为误登记或重复；禁止用于已生效义务。

Closed 不表示法律或合同义务永久终止。Source Validity、Effective Date、Review Date 和 Reopen Trigger 必须保留。

### 12.6 Baseline 与版本规则

1. SRS、THM、SAR、PII、PIA、COR、SVP 和适用 AIA 必须在 Release Ready 前固定 Revision；
2. 关键 Control、ASVS/LLMSVS Version、Tool Rule Set 和 Obligation Source 必须进入 BSL；
3. VUR 不以 DOC Baselined 状态管理，但受影响版本、修复版本和 Evidence Snapshot 必须固定；
4. Secret Baseline 只包含 Reference 和 Version；
5. PII Baseline 不包含不必要样本值；
6. 法律和标准来源更新必须保留旧 Revision；
7. Release 必须可重建其 Security/Privacy/Compliance 输入。

## 13. 正式产物最低内容

### 13.1 通用必填信息

九类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 E02 类型专属要求。

### 13.2 SRS Security Requirement Set

SRS 类型专属必填：

- Asset；
- Threat Source；
- Security Requirement Reference；
- Control Objective；
- Applicable Component；
- Risk Level；
- Acceptance；
- Verification Method；
- Exception；
- Requirement Owner；
- Priority/Criticality；
- THM Link；
- SAR Control Link；
- Obligation Link；
- Verification Criterion；
- Coverage Status。

SRS 只索引和组织 C04 REQ。强制 Security Statement 必须拥有 C04 Requirement ID。

### 13.3 THM Threat Model

THM 类型专属必填：

- Scope；
- Asset；
- Trust Boundary；
- Threat Actor；
- Threat Scenario；
- Attack Path；
- Existing Control；
- Risk Rating；
- Treatment；
- Residual Risk；
- Entry Point；
- Precondition；
- Impact；
- Detection；
- Assumption；
- Unknown；
- Owner；
- Review Trigger；
- Diagram/Model Reference。

### 13.4 SAR Security Architecture

SAR 类型专属必填：

- Security Boundary；
- Identity and Access；
- Key and Secret；
- Data Protection；
- Network Control；
- Component Control；
- Logging and Monitoring；
- Decision；
- Verification；
- Update Rule；
- Security Objective；
- Trust Assumption；
- Control Element ID；
- Interface；
- Supplier/Dependency；
- Failure/Recovery；
- Applicable Version；
- E01/C06 Link。

### 13.5 PII Privacy and PII Register

PII 类型专属必填：

- Data Category；
- PII Type；
- Data Subject；
- Source；
- Purpose；
- Lawful Basis Responsibility；
- Storage Location；
- Access；
- Sharing；
- Retention；
- Deletion；
- Owner；
- Controller/Processor Role；
- Collection Method；
- Internal Use；
- Recipient；
- Transfer；
- Protection；
- Backup/Replica；
- Data Subject Interface；
- Processor/Subprocessor；
- Last Review；
- Evidence。

### 13.6 PIA Privacy Impact Assessment

PIA 类型专属必填：

- Processing Activity；
- Purpose；
- Necessity；
- Data Subject；
- Data Flow；
- Privacy Risk；
- Impact；
- Control；
- Consultation；
- Approval；
- Residual Risk；
- Review Trigger；
- Scope；
- PII Link；
- Interested Party；
- Proportionality；
- Alternative；
- Limitation；
- Impact Result；
- Monitoring；
- Complaint/Appeal Interface。

### 13.7 COR Compliance Obligation Register

COR 类型专属必填：

- Obligation Source；
- Jurisdiction or Organizational Scope；
- Requirement Summary；
- Applicable Asset；
- Owner；
- Evidence；
- Member Status；
- Review Date；
- Source Identifier；
- Source Version；
- Effective Date；
- Source Validity；
- Obligation Applicability；
- Legal/Compliance Authority；
- Interpretation Reference；
- Control/Requirement Link；
- Non-waivable Flag；
- Deadline/Notification；
- Gap；
- Reopen Trigger。

COR 必须声明：本登记册不代替法律结论。

### 13.8 SVP Security Verification Plan

SVP 类型专属必填：

- ASVS or Other Control Baseline；
- Baseline Version；
- Verification Scope；
- Level；
- Method；
- Environment；
- Tool；
- Independence；
- Evidence；
- Threshold；
- Failure Handling；
- Criterion ID；
- Requirement/Control Link；
- Target Asset and Version；
- Test Data；
- Authorization；
- Command/Configuration Reference；
- Stop Condition；
- Coverage；
- Retest Rule；
- Reviewer。

### 13.9 VUR Vulnerability and Remediation Record

VUR 类型专属必填：

- Vulnerability Source；
- Affected Asset；
- Affected Version；
- Severity；
- Exploit Condition；
- Evidence；
- Treatment；
- Owner；
- Due；
- Fixed Version；
- Retest；
- Disclosure Status；
- Finding Validity；
- Severity Method and Version；
- Environment；
- First Seen；
- C02 Risk Link；
- Control/Requirement Link；
- Containment；
- Remediation Change；
- Closure Reviewer；
- Reopen Trigger。

### 13.10 AIA AI Impact Assessment

AIA 类型专属必填：

- AI Use；
- Affected Individual or Group；
- Expected Benefit；
- Potential Harm；
- Data Limitation；
- Model Limitation；
- Human Oversight；
- Control；
- Monitoring；
- Approval；
- Review Trigger；
- AI System and Version；
- Foreseeable Use/Misuse；
- Impact Scope；
- Impact Scale；
- Duration/Reversibility；
- Distribution；
- Consultation；
- Uncertainty；
- Residual Impact；
- AI Impact Result；
- Appeal/Intervention；
- Exit/Restriction；
- E03 Model/Data Link。

## 14. 质量要求

### 14.1 SRS

SRS 必须：

- 100% 成员指向 C04 REQ；
- 每项有 Asset/Threat/Obligation 来源；
- 每项有 Acceptance 和 Verification；
- 每项有 THM/SAR/SVP 承接或明确 Gap；
- 无模糊“安全”“合规”“保护充分”陈述；
- Exception 指向 C12 EWR；
- Coverage 可计算；
- 版本和 Baseline 可定位。

### 14.2 THM

THM 必须：

- Scope 和 Version 固定；
- Asset 与 Owner 完整；
- Trust Boundary 可识别；
- Threat Actor、Scenario、Path 和 Impact 可区分；
- Control 映射到 Requirement/Design；
- Risk 使用 C02；
- Unknown 和 Assumption 可见；
- 变化触发明确；
- Diagram 与文本事实一致；
- 不把 Framework 分类名当作完整 Threat。

### 14.3 SAR

SAR 必须：

- Security Boundary 与 E01/C06 一致；
- Identity/Access、Secret/Key、Data、Network、Component、Logging 和 Monitoring 有适用结论；
- Control Element 有永久 ID；
- Failure、Recovery、Update 和 Verification 完整；
- Trust Assumption 可验证；
- Supplier 和 External Interface 可追踪；
- 不包含 Secret Value；
- 决策引用 C10；
- Release 版本可定位。

### 14.4 PII 与 PIA

PII 必须：

- Processing 生命周期完整；
- Purpose、Owner、Role、Access、Sharing、Retention、Deletion 无空白；
- Lawful Basis 记录责任和引用，不由 Agent 推断；
- Backup、Log、Telemetry、Prompt 和 Derived Data 纳入；
- PII 样本不进入普通文档。

PIA 必须：

- Scope、Purpose、Necessity、Data Flow、Affected Party 和 Impact 完整；
- Control 与 C04/C06/C05 可追踪；
- Consultation、Approval、Residual Risk 和 Review Trigger 完整；
- Unknown 不计为 Controlled；
- 不把 Security Test Pass 当作 Privacy Conclusion。

### 14.5 COR

COR 必须：

- 来源权威、版本和有效期可验证；
- Applicability 有 Authority；
- Summary 不歪曲来源；
- Asset、Requirement、Control、Evidence、Owner 和 Review Date 完整；
- Non-waivable 项清晰；
- Gap 有 CASE Member Status；
- Closed 项有本周期复核 Evidence；
- 来源变化可 Reopen；
- 明确不代替法律结论。

### 14.6 SVP

SVP 必须：

- 固定 Baseline、Version 和 Level；
- ASVS ID 带 `v5.0.0-`；
- LLMSVS ID 带 `2.0`；
- Scope、Target、Environment、Tool 和 Rule Set 固定；
- Method、Oracle、Threshold 和 Evidence 明确；
- 自动化与人工方法分离；
- Active/Destructive/Production 测试有 Authority；
- Secret 和 PII 输出受控；
- Fail/Blocked/Inconclusive 处置明确；
- Coverage 不隐藏不适用和未验证项；
- Independence 满足 Risk；
- 复测规则完整。

### 14.7 VUR

VUR 必须：

- 一个独立 Vulnerability 一个永久 ID；
- Finding Validity 可追踪；
- Asset 和 Version 精确；
- Severity Method/Version 和理由完整；
- Severity 与 C02 Risk 分开；
- Owner、Due、Treatment 和 Fix Version 完整；
- Retest 使用固定环境和 Evidence；
- Disclosure 由 Authority 决定；
- False Positive/Duplicate 保留依据；
- Closed 有独立 Reviewer；
- Reopen Trigger 可执行。

### 14.8 AIA

AIA 必须：

- 在显著影响触发成立时创建；
- AI System、Use、Foreseeable Use 和 Version 固定；
- Affected Party 不只包含直接 User；
- Benefit、Adverse Impact、Distribution、Duration、Reversibility 和 Uncertainty 完整；
- Data/Model Limitation 和 E03 Trace 完整；
- Human Oversight、Intervention、Appeal、Restriction 和 Exit 明确；
- Monitoring 有指标、阈值、Owner 和频率；
- Consultation 和反对意见保留；
- Unknown 不计为 Controlled；
- Approval 由有权人类作出。

## 15. 验证、评审与 Gate

### 15.1 验证层次

| 层次 | 对象 | 最低方法 |
|---|---|---|
| Structure | 九类产物、字段、State、Revision | Inspection |
| Trace | Requirement、Threat、Control、Evidence、Risk、Obligation、Release | Automated Check + Review |
| Design | SAR、PIA、AIA、Trust Boundary、Control | Analysis + Review |
| Implementation | Code、Configuration、Infrastructure、Identity、Secret | Test + Inspection + Analysis |
| Operational | Monitoring、Alert、Access Review、Deletion、Incident | Observation + Test |
| Independent Assurance | 高风险 Security/Privacy/Compliance/AI Impact | Independent Review/Assessment |

### 15.2 ASVS 与 LLMSVS 选择

1. Web App/SaaS/API 必须评价 ASVS 5.0.0；
2. LLM Application 必须同时评价 ASVS 5.0.0 和 LLMSVS 2.0；
3. Level 由 Security Authority 依据 Risk、PII、交易、监管、Exposure 和 Criticality 决定；
4. Level 选择必须进入 C10 Decision；
5. Level 降低属于受控 Change；
6. 选择较低 Level 不免除特定高风险 Requirement；
7. Requirement ID 必须版本化；
8. 版本升级前后 Coverage 不得直接比较，必须建立 Mapping；
9. Bleeding Edge 只能用于预研，不得作为 Release Baseline；
10. OWASP 不提供产品认证，禁止对外声称 OWASP Certified。

### 15.3 强制 Security Review

Review 必须覆盖：

- Applicability 和 Scope；
- Asset、Threat、Trust Boundary 和 Attack Path；
- SRS、THM、SAR 一致性；
- Identity、Access、Secret、Data、Network、Supplier；
- PII、PIA、COR 和 AIA；
- ASVS/LLMSVS Version、Level 和 Coverage；
- Command、Tool、Environment、Authorization 和 Stop；
- VUR、Residual Risk、Waiver 和 Disclosure；
- Evidence Validity 和 Independence；
- Change、Release、Monitoring、Incident 和 Retirement；
- Unknown、Not Applicable 和 Inconclusive；
- Agent 权限和自批风险。

### 15.4 五个 Gate

| Gate | E02 强制条件 |
|---|---|
| Discovery Ready | Activation 决定完成；初始 Asset/PII/Obligation/AI Impact 和 Authority 已识别 |
| Specification Ready | SRS、THM、SAR、PII、PIA、COR、适用 AIA 已评审；Requirement/Acceptance/Verification Trace 完整 |
| Agent Execution Ready | Context、Scope、Permission、Secret Reference、Tool、Target、Stop 和 Evidence Plan 已批准 |
| Release Ready | SVP 已执行；Evidence 已复核；VUR、Risk、Obligation、Waiver 和 Non-waivable 项满足条件 |
| Learning Closed | Vulnerability、Incident、Complaint、Impact、Control Failure 已回流 Change、Risk、Requirement 和 Health |

### 15.5 Release Blocker

以下情况必须阻断 Release：

- E02 应激活但未激活；
- Activation Pending；
- Non-waivable Obligation 未满足；
- 未经授权处理 PII、Payment 或 Secret；
- High/Critical Risk 未处理且无有权 RAR；
- 已确认高影响 Vulnerability 未处理且无合法 Release 路径；
- Security/Privacy/Compliance/AI Impact Authority 缺失；
- 关键 SRS/THM/SAR/PIA/COR/SVP/AIA 未 Approved 或固定；
- Required Verification Fail、Blocked、Not Evaluated 或 Inconclusive；
- Secret 泄漏或未完成轮换；
- Evidence 无效、版本不匹配或 Scope 不完整；
- Agent 自批关键输出；
- Production Test 未授权；
- Gate 输入被删减或篡改。

### 15.6 符合性声明

项目只能声明：

- 对本 E02 指定 Revision 的符合性；
- 对固定 ASVS/LLMSVS Requirement Set 的 Coverage 和 Result；
- 对固定 ISO 条款映射的项目控制实现情况；
- 明确 Scope、Exclusion、Unknown、Evidence 和 Review Date。

项目禁止声明：

- 已获得 ISO/IEC 27001、27701 或其他认证，除非有独立有效证书；
- OWASP 对产品或供应商作了认证；
- 零 Vulnerability；
- 绝对安全；
- 对所有法律普遍合规；
- AIA/PIA 已消除全部影响；
- Agent 生成结论等同专业法律意见。

## 16. 追踪、审计与记录

### 16.1 必须审计事件

必须记录：

- Activation 创建、变化、Pending 和失效；
- Asset、PII、Obligation、AI Use 和 Supplier 新增/删除；
- SRS、THM、SAR、PII、PIA、COR、SVP、AIA Revision/State；
- VUR 创建、Severity、Treatment、Due、Retest、Closure、Reopen；
- Control Applicability、Implementation 和 Verification Result；
- ASVS/LLMSVS Version/Level 选择和变化；
- Tool/Rule/Configuration Update；
- Active/Destructive/Production Test Authorization；
- Secret Access、Rotation、Revocation 和 Exposure；
- PII Access、Sharing、Transfer、Retention 和 Deletion Evidence；
- Legal/Compliance Interpretation 和 Review；
- Waiver、Risk Acceptance、Gate 和 Disclosure；
- Stop、Incident、Emergency Change 和 Recovery；
- Agent 生成、修改、验证和被拒绝的输出；
- Correction、Supersession、Retirement 和 Disposition。

### 16.2 最小审计字段

- Event ID；
- Event Type；
- Actor；
- Role；
- Authority Reference；
- Time and Timezone；
- Object ID and Revision；
- Previous/New Value；
- Reason；
- Source/Evidence；
- Environment；
- Result；
- Sensitive Data Handling；
- Correlation ID；
- Retention Rule；
- Correction Link。

### 16.3 敏感记录

1. Audit 不得成为 Secret 或 PII 泄漏渠道；
2. 普通记录保存 Reference、Fingerprint、Classification 和必要摘要；
3. 原始敏感 Evidence 进入受限存储；
4. Redaction 必须保留方法、执行者和可复核性；
5. 无权 Reviewer 只能看到完成判断所需最小信息；
6. 删除请求与法定保留冲突时交由 Privacy/Legal Authority 决定；
7. 不允许为隐藏失败而删除记录；
8. REC 更正使用新记录，禁止原位覆盖。

### 16.4 Coverage 和健康指标

最低指标：

- E02 Applicability Completion Rate；
- Security Requirement Trace Coverage；
- Threat Scenario Control Coverage；
- Control Verification Coverage；
- PII Lifecycle Field Completeness；
- PIA/AIA Review Freshness；
- Obligation Evidence Coverage；
- Open VUR by Severity；
- Remediation Due Compliance；
- Retest Success/Failure；
- ASVS/LLMSVS Applicable Requirement Coverage；
- Unknown/Not Evaluated Count；
- Secret Exposure Count；
- Unauthorized Test Count；
- Reopened Vulnerability Count；
- Repeat Control Failure；
- Privacy Complaint/Incident Count；
- Security Gate Rejection Rate。

每个指标必须服从 C12 Metric Definition、Threshold、Segment、Data Quality 和 Anti-gaming 规则。

## 17. 裁剪、激活、停用与退役

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。E02 的 Active、Conditionally Active、Retiring、Retired、Inactive、Pending、Not Evaluated 必须按统一状态语义解析；Trigger、Unknown 或冲突不得被局部规则降级。

### 17.0 Task Profile 驱动的激活

E02 在 Identity/Security/Privacy Change Surface、PII/敏感数据处理、外部暴露或信任边界变化、安全 Requirement、合规义务、威胁或漏洞，或 C02 High/Critical 安全风险成立时激活。Unknown 不得判定为未激活。

已有安全与合规 Baseline 未变化时 `Reference`；只创建受影响的 SRS、THM、SAR、PII、PIA、COR、SVP、VUR 或 AIA 实例。实际漏洞和整改按事件记录，Agent 不得自批 Privacy Impact、Waiver 或 Risk Acceptance。

### 17.1 P2 保留边界

P2 必须保留：

- 九类产物身份；
- 公共状态模型；
- 全部通用必填信息；
- 蓝图专属最低字段；
- Activation Trigger；
- Authority 和职责分离；
- Requirement/Control/Evidence/Risk/Obligation Trace；
- PII Lifecycle；
- ASVS/LLMSVS Version Pinning；
- 命令、工具、环境和 Evidence 控制；
- VUR Closure/Reopen；
- Gate、Audit 和国际标准映射。

### 17.2 允许裁剪

允许在记录理由和批准后：

- 仅创建适用 AIA；
- 删除确实不适用的 Control Candidate，但保留判定；
- 选择适合 Risk 的 Verification Method 和 Level；
- 合并物理文件，但不合并资产身份；
- 使用其他受控 Threat/Severity Method；
- 使用组织已有 ISMS/PIMS 资产，通过 Trace 引用；
- 对非生产原型限制 E02 Scope，但不得处理真实 PII/Secret 或公开暴露；
- 使用自动化生成 Draft 和检查结果。

禁止裁剪：

- Authority；
- Secret Protection；
- PII Purpose/Retention/Deletion；
- Non-waivable Obligation；
- Independent Review；
- Evidence；
- History；
- VUR；
- Release Blocker；
- Unknown/Pending；
- Agent 禁止事项。

### 17.3 停用

E02 从 Active 进入 Retiring 必须：

1. 确认所有触发条件在目标 Scope 不再成立；
2. 禁止新增受控 Processing/Exposure；
3. 关闭或转移 Open VUR、Risk、Incident 和 Obligation；
4. 撤销 Identity、Access、Secret、Token 和 Supplier Access；
5. 完成 PII Return、Deletion、Anonymization 或 Lawful Retention；
6. 完成客户、供应商、监管或其他通知；
7. 保留审计、Evidence、Decision 和 Disclosure；
8. 由 Security、Privacy、Compliance 和 Product Authority 共同批准；
9. 更新 C11 Baseline 和 C12 Gate；
10. 设置 Retired 生效时间和复评触发。

### 17.4 退役

Retired 后：

- 历史产物只读保留；
- Secret 必须撤销或销毁；
- PII 只按已批准 Retention Rule 保留；
- 未完成法律/合同义务继续有效；
- 新 Scope、恢复服务、重新处理 PII 或重新公开时必须重新激活；
- 禁止删除 Vulnerability、Incident、Waiver、Risk Acceptance 和 Gate 历史；
- 标准升级无需追溯改写历史，但需要保证历史引用可解释。

## 18. 与其他规范接口

### 18.1 C01 至 C04

- C01 提供 Evidence、Need、Problem、Intent 和未经授权数据 Stop；
- C02 提供 Scope、Risk、Dependency、Authority Need 和扩展适用性；
- C03 提供 PRD、Feature、Role、Permission、Data、Security 和 Quality Summary；
- C04 提供权威 Security/Privacy/Compliance/AI Requirement；
- SRS 只索引 C04 REQ；
- Requirement 变化触发 THM、SAR、PIA、COR、SVP 和 AIA 影响分析。

### 18.2 C05 至 C06

- C05 管理 Acceptance、Verification Method、Evidence 和 Acceptance Decision；
- SVP 为 C05 提供 Security Baseline、Level、Criterion、Environment 和 Independence；
- C06 管理 UX、Permission、Data Flow、Interface、Failure 和 Technical Design；
- SAR/THM/PIA/AIA 向 C06 提供 Control 和 Constraint；
- E02 不复制 TDS；
- Security/Privacy/AI 设计变化必须重新验证。

### 18.3 C07 至 C09

- C07 管理 Human/Agent Authority、Stop、Recovery 和高影响批准；
- C08 管理敏感 Context、Source、Access、Redaction 和 Freshness；
- C09 管理真实 Command、Tool Call、Run、Output、Failure 和 Evidence Capture；
- E02 定义 Security-specific Scope、Tool、Stop 和敏感输出规则；
- Secret 只作为 Reference 进入 Context/Run；
- Agent 越权或泄漏必须 Stop 并进入 VUR/Incident/C12。

### 18.4 C10 至 C12

- C10 管理 Activation、Control/Level/Exception Decision 和 Trace；
- C11 管理 Security CI、Revision、Baseline、Change、Emergency Change 和 Release；
- C12 管理 Review、Gate、EWR、RAR 和 Health；
- Non-waivable Obligation 禁止普通 EWR；
- Risk Acceptance 不改写 VUR、Evidence、Requirement 或 Obligation；
- Release Gate 必须消费固定 E02 Revision 和 Verification Evidence。

### 18.5 E01、E03 至 E05

- E01 管理 Security/Privacy/Compliance Architecture Concern、Trust Boundary 和 Conformance；
- E03 管理 Dataset、Model、RAG、Quality、Lineage、Retention 和 Data/Model Version；
- E04 管理 E02 Record、Metadata、Access、Retention、Correction、Disposition 和 Audit；
- E05 管理 Incident、SLO、Service、Continuity、Recovery 和运行 Review；
- 同一对象的事实必须由单一规范拥有，其余规范用 Trace 消费；
- 扩展激活状态必须在 Change、Release 和 Incident 后联合复评。

## 19. 参考标准治理

### 19.1 参考层级

| 层级 | 来源 | E02 使用 |
|---|---|---|
| R1 | ISO/IEC 27001:2022 + Amd 1:2024 | ISMS Requirement、Risk、Role、Operation、Evaluation、Improvement |
| R1 | ISO/IEC 27002:2022 | Organizational、People、Physical、Technological Control |
| R1 | ISO/IEC 27701:2025 | 独立 PIMS、PII Controller/Processor、Privacy Risk 和 Operation |
| R1 | ISO/IEC 42005:2025 | AI System Impact Assessment |
| R1 | ISO/IEC 23894:2023 | AI Risk Principles、Framework 和 Process |
| R2 | OWASP ASVS 5.0.0 | Web Application Security Verification |
| R2 | OWASP LLMSVS 2.0 | LLM Security Verification |
| R3 | OWASP AISVS 1.0 | 监测；未经蓝图 Change 不进入强制 Baseline |

R1 优先于 R2；R2 不得用于覆盖法律、合同或组织 Authority。

### 19.2 版本固定

每个引用必须记录：

- Standard/Framework Name；
- Version/Edition；
- Amendment/Correction；
- Language；
- Official Source；
- Retrieved Date；
- Requirement/Clause ID；
- Applicable Scope；
- Adoption Decision；
- Mapping Revision；
- Supersession Status。

### 19.3 标准变化

以下变化触发 C11 Change：

- ISO 新版、Amendment、Correction、Withdrawal；
- OWASP Stable Release；
- Requirement ID 变化；
- Level 定义变化；
- 法律、监管、合同或组织 Policy 变化；
- Tool Rule Set 对标准映射变化；
- 新标准与现有标准范围重叠。

变化处理必须：

1. 比较旧新版本；
2. 识别新增、修改、删除和重编号；
3. 评价 SRS、THM、SAR、PII、PIA、COR、SVP、VUR、AIA 影响；
4. 更新 Trace；
5. 决定迁移窗口；
6. 重新验证受影响 Control；
7. 保留旧 Baseline 和 Evidence；
8. 禁止自动把历史 Pass 迁移为新版本 Pass。

### 19.4 法律来源治理

1. E02 不提供通用法律结论；
2. 具体产品必须识别 Jurisdiction、Industry、Contract 和 Role；
3. Legal/Compliance Authority 必须确认 Applicability 和 Interpretation；
4. Agent 和搜索摘要只能作为候选线索；
5. 义务原文访问必须遵守版权、许可和保密；
6. COR 保存必要摘要和权威链接；
7. 解释冲突进入 C10 Decision；
8. Non-waivable 标记必须有 Authority；
9. 来源失效或替代必须保留历史；
10. Review Date 到期必须 Reopen。

## 20. 模板、检查清单与国际标准条例映射

### 20.1 Extension Applicability Decision 骨架

```yaml
asset_id: DEC-E02-<id>
artifact_type: Decision Record
product_scope:
environment:
assessment_date:
triggers:
  account_identity_permission_external_api:
    result:
    evidence:
  internet_public_service:
    result:
    evidence:
  pii_sensitive_payment_secret:
    result:
    evidence:
  regulated_activity:
    result:
    evidence:
  significant_ai_impact:
    result:
    evidence:
activation_status:
required_artifacts:
unknowns:
owner:
reviewer:
approver:
effective_at:
expires_at:
reassessment_triggers:
trace_links:
```

### 20.2 SRS 骨架

```yaml
asset_id: SRS-<id>
artifact_type: Security Requirement Set
state: Draft
revision:
applicable_scope:
baseline_reference:
members:
  - member_id:
    asset:
    threat_source:
    requirement_reference:
    control_objective:
    applicable_component:
    risk_level:
    acceptance:
    verification_method:
    exception_reference:
    thm_link:
    sar_control_link:
    obligation_link:
    verification_criterion:
    coverage_status:
owner:
trace_links:
access_classification:
retention_rule:
history_reference:
```

### 20.3 THM 骨架

```yaml
asset_id: THM-<id>
artifact_type: Threat Model
state: Draft
revision:
scope:
assets:
trust_boundaries:
entry_points:
threat_scenarios:
  - scenario_id:
    threat_actor:
    asset:
    precondition:
    attack_path:
    existing_control:
    impact:
    risk_reference:
    treatment:
    residual_risk:
    detection:
    assumption:
    unknown:
owner:
review_trigger:
model_reference:
trace_links:
```

### 20.4 SAR 骨架

```yaml
asset_id: SAR-<id>
artifact_type: Security Architecture
state: Draft
revision:
applicable_scope:
security_objectives:
security_boundaries:
identity_and_access:
key_and_secret:
data_protection:
network_controls:
component_controls:
logging_and_monitoring:
supplier_dependencies:
control_elements:
  - control_element_id:
    objective:
    design:
    requirement_links:
    decision_links:
    verification_links:
failure_and_recovery:
update_rules:
applicable_version:
e01_c06_links:
```

### 20.5 PII 成员骨架

```yaml
member_id: PII-ITEM-<id>
data_category:
pii_type:
data_subject:
source:
purpose:
lawful_basis_responsibility:
controller_processor_role:
collection_method:
storage_location:
access_roles:
internal_use:
sharing_recipients:
transfer:
retention:
deletion:
backup_replica:
protection:
data_subject_interface:
processor_subprocessor:
owner:
last_review:
evidence:
trace_links:
```

### 20.6 PIA 骨架

```yaml
asset_id: PIA-<id>
artifact_type: Privacy Impact Assessment
state: Draft
revision:
scope:
processing_activity:
purpose:
necessity:
proportionality:
alternatives:
data_subjects:
data_flow:
pii_links:
privacy_risks:
impacts:
controls:
consultation:
limitations:
residual_risk:
impact_result:
monitoring:
complaint_appeal_interface:
approval:
review_triggers:
```

### 20.7 COR 成员骨架

```yaml
member_id: COR-ITEM-<id>
obligation_source:
source_identifier:
source_version:
jurisdiction_or_organizational_scope:
effective_date:
source_validity:
requirement_summary:
obligation_applicability:
legal_compliance_authority:
interpretation_reference:
applicable_assets:
requirement_control_links:
non_waivable:
deadline_notification:
evidence:
gap:
member_status: Open
owner:
review_date:
reopen_trigger:
```

### 20.8 SVP 骨架

```yaml
asset_id: SVP-<id>
artifact_type: Security Verification Plan
state: Draft
revision:
applicable_scope:
control_baselines:
  - name:
    version:
    level:
    official_source:
criteria:
  - criterion_id:
    requirement_control_links:
    target_asset_version:
    method:
    environment:
    tool_version_digest:
    rule_configuration_revision:
    test_data:
    authorization:
    threshold_or_oracle:
    evidence_requirement:
    independence:
    stop_condition:
    failure_handling:
    retest_rule:
coverage:
reviewer:
```

### 20.9 VUR 骨架

```yaml
asset_id: VUR-<id>
artifact_type: Vulnerability and Remediation Record
state: Open
vulnerability_source:
finding_validity:
affected_assets_versions:
environment:
exploit_conditions:
severity:
severity_method_version:
evidence:
first_seen:
risk_links:
requirement_control_links:
containment:
treatment:
owner:
due:
remediation_change:
fixed_version:
retest:
disclosure_disposition:
closure_reviewer:
reopen_trigger:
history_reference:
```

### 20.10 AIA 骨架

```yaml
asset_id: AIA-<id>
artifact_type: AI Impact Assessment
state: Draft
revision:
ai_system_version:
ai_use:
foreseeable_use_misuse:
affected_individuals_groups:
expected_benefits:
potential_harms:
impact_scope_scale:
duration_reversibility:
distribution:
data_limitations:
model_limitations:
human_oversight:
consultation:
uncertainty:
controls:
monitoring:
residual_impact:
ai_impact_result:
appeal_intervention:
exit_restriction:
approval:
review_triggers:
e03_links:
```

### 20.11 Security Verification Command Control 骨架

```yaml
run_id:
svp_criterion:
tool:
  name:
  version:
  digest:
  rule_set_revision:
  configuration_revision:
command_structure:
parameter_sources:
target_asset_version:
environment_tenant_account:
authorized_scope:
permitted_actions:
prohibited_actions:
action_classification:
rate_concurrency_timeout_budget:
test_data_classification:
secret_references:
output_redaction:
stop_conditions:
rollback_recovery:
evidence_locator:
reviewer:
```

### 20.12 P2 生产检查清单

- [ ] E02 Applicability 在 Discovery Ready 前完成；
- [ ] 所有触发条件有 Result 和 Evidence；
- [ ] Unknown 映射 Pending；
- [ ] 9 类产物身份未合并；
- [ ] AIA 适用性已判定；
- [ ] 通用必填字段完整；
- [ ] DOC/CASE State 使用正确；
- [ ] 领域 Result 未注册为 State；
- [ ] SRS 100% 引用 C04 REQ；
- [ ] Security Requirement 有 Acceptance；
- [ ] Security Requirement 有 Verification；
- [ ] THM Scope 和 Version 固定；
- [ ] Asset 和 Owner 完整；
- [ ] Trust Boundary 完整；
- [ ] Threat Actor/Scenario/Path 可区分；
- [ ] THM Risk 指向 C02；
- [ ] SAR 与 E01/C06 一致；
- [ ] Identity/Access 完整；
- [ ] Secret 只存 Reference；
- [ ] PII Lifecycle 完整；
- [ ] Purpose 和 Owner 完整；
- [ ] Lawful Basis 由有权角色处理；
- [ ] PIA Purpose/Necessity/Impact 完整；
- [ ] COR Source/Scope/Version/Authority 完整；
- [ ] COR 声明不代替法律结论；
- [ ] Non-waivable 项明确；
- [ ] ASVS Version 固定 5.0.0；
- [ ] ASVS ID 带版本；
- [ ] LLM 应用评价 LLMSVS 2.0；
- [ ] Level 有 Risk 和 Authority；
- [ ] SVP Scope/Environment/Tool 固定；
- [ ] Active/Destructive/Production Test 已授权；
- [ ] Command/Tool/Rule/Config 可重建；
- [ ] Stop Condition 完整；
- [ ] Output Redaction 完整；
- [ ] Evidence 由 C05 管理；
- [ ] Tool Success 未自动写 Pass；
- [ ] VUR Asset/Version 精确；
- [ ] Finding Validity 已判断；
- [ ] Severity Method/Version 完整；
- [ ] Severity 与 Risk 分离；
- [ ] Owner/Due/Fix/Retest 完整；
- [ ] Closure 有独立 Reviewer；
- [ ] Disclosure 有 Authority；
- [ ] AIA Affected Party 不限直接 User；
- [ ] AIA Data/Model Limitation 完整；
- [ ] AIA Human Oversight/Appeal/Exit 完整；
- [ ] Agent 无自批；
- [ ] Requirement/Control/Evidence Trace 完整；
- [ ] VUR/Risk/Change/Release Trace 完整；
- [ ] Gate 输入固定 Revision；
- [ ] Non-waivable Fail 阻断；
- [ ] Secret/PII 未出现在普通文档；
- [ ] Audit 和 History 完整；
- [ ] Retention/Deletion 冲突已升级；
- [ ] 标准版本变化进入 C11；
- [ ] E01/E03/E04/E05 接口完整；
- [ ] 文末国际标准映射完整。

### 20.13 反例

反例 1：

> 系统应安全登录，权限合理，日志完整。

不符合：

- “安全”“合理”“完整”无 Criterion；
- Authentication、Authorization、Logging 是独立 Requirement；
- 无 Threat、Asset、Risk、Acceptance 和 Verification；
- 应拆分为 C04 REQ 并进入 SRS。

反例 2：

> 扫描工具没有报错，因此产品符合 ASVS。

不符合：

- Tool Result 不等于 Verification Result；
- 未固定 ASVS Version、Level、Scope 和 Requirement ID；
- 自动化不能覆盖全部 Requirement；
- 无独立 Evidence Review。

反例 3：

> 用户同意隐私政策，所以全部数据处理都合法。

不符合：

- Consent 是否适用需有权判断；
- 不同 Purpose、PII、Data Subject 和 Jurisdiction 必须分别评价；
- PII Register、PIA、COR 和 Evidence 缺失；
- Privacy Policy 接受不自动构成所有处理的合法依据。

反例 4：

> 这是内部工具，不需要 E02。

不符合：

- Internal Tool 仍可处理 Identity、Permission、PII、Secret 或 Regulated Data；
- 必须逐项执行触发条件判定；
- Unknown 不能映射 Inactive。

反例 5：

> 漏洞评分低，可以直接关闭。

不符合：

- Severity 不等于 C02 Risk；
- 需固定 Affected Asset、Version、Exploit Condition 和 Business Context；
- Closed 需要 Remediation/Disposition、Retest Evidence 和独立 Reviewer。

反例 6：

> Agent 已完成 Threat Model 和法律合规分析，可以批准上线。

不符合：

- Agent 只能起草和检查；
- 法律结论、Residual Risk、PIA/AIA、Security Review 和 Gate 必须由有权人类决定；
- 自批违反 C07/C12 和本规范。

### 20.14 标准复评清单

- [ ] ISO 产品页 Status/Edition 未变化；
- [ ] ISO Amendment/Correction 已检查；
- [ ] ISO/IEC 27701 仍使用 2025 独立 MSS；
- [ ] ASVS Stable Release 未变化；
- [ ] ASVS Requirement ID Mapping 当前；
- [ ] LLMSVS 版本化正文 Status 当前；
- [ ] LLMSVS 与 ASVS Mapping 当前；
- [ ] OWASP AISVS 与 LLMSVS 范围已复评；
- [ ] 法律/监管/合同 Source 有效；
- [ ] Tool Rule Set 与采用版本一致；
- [ ] 标准变化已进入 C11 Change；
- [ ] 历史 Baseline 未被重写。

### 20.15 国际标准条例映射

以下映射依据 ISO 官方产品页、ISO OBP 公开目录和 OWASP 官方版本化页面。项目产物代码、状态值、触发阈值、命令字段、模板和 Gate 是本项目工程化控制，不表示国际标准逐字规定。未取得标准全文授权时，不据此声明完整符合性。

| 国际标准及条款/公开主题 | 条款或公开主题 | 本规范落实位置 |
|---|---|---|
| ISO/IEC 27001:2022 第 1 章 | ISMS Requirements Scope | 2、3、4、15.6 |
| ISO/IEC 27001:2022 4.1–4.4 | Context、Interested Parties、Scope、ISMS | 3、9.2、10.1–10.3、19.4 |
| ISO/IEC 27001:2022 5.1–5.3 | Leadership、Policy、Roles/Authorities | 7、10.4–10.10、15 |
| ISO/IEC 27001:2022 6.1 | Risk and Opportunities | 6、8、10.4、11、14 |
| ISO/IEC 27001:2022 6.2 | Security Objectives | 2、11、13.2、14.1 |
| ISO/IEC 27001:2022 7.1–7.5 | Resources、Competence、Communication、Documented Information | 7、13、16、18.5 |
| ISO/IEC 27001:2022 8.1–8.3 | Operational Control、Risk Assessment/Treatment | 9、10、11、15 |
| ISO/IEC 27001:2022 9.1–9.3 | Evaluation、Internal Audit、Management Review | 15、16.4、18.4 |
| ISO/IEC 27001:2022 10.1–10.2 | Nonconformity、Corrective Action、Improvement | 10.8、12.4、16、17 |
| ISO/IEC 27001:2022 Annex A | Information Security Control Reference | 10.4、11、15.2、19.1 |
| ISO/IEC 27001:2022/Amd 1:2024 4.1、4.2 | Climate Change Relevance and Interested Party Requirement | 9.2、19.1–19.3 |
| ISO/IEC 27002:2022 第 4 章 | Structure、Themes、Attributes、Control Layout | 8、11、13、14 |
| ISO/IEC 27002:2022 第 5 章 | Organizational Controls | 7、10.6、11.1、11.5–11.9 |
| ISO/IEC 27002:2022 第 6 章 | People Controls | 7、11.2、11.7、16 |
| ISO/IEC 27002:2022 第 7 章 | Physical Controls | 5.5、11.1、11.5、15.1 |
| ISO/IEC 27002:2022 第 8 章 | Technological Controls | 11.2–11.7、11.10–11.12、15 |
| ISO/IEC 27701:2025 第 1 章 | PIMS Requirements and Guidance Scope | 2、3、6、10.5 |
| ISO/IEC 27701:2025 4.1–4.4 | Context、Interested Parties、PIMS Scope、PIMS | 3、6、10.1、10.5、13.5–13.7 |
| ISO/IEC 27701:2025 5.1–5.3 | Leadership、Privacy Policy、Roles/Authorities | 7、10.5、10.6 |
| ISO/IEC 27701:2025 6.1–6.3 | Privacy Risk、Objectives、Planning of Changes | 9.3、10.5、11.4、11.8 |
| ISO/IEC 27701:2025 7.1–7.5 | Resources、Competence、Communication、Documented Information | 7、13.5–13.7、16 |
| ISO/IEC 27701:2025 第 8 章 | Operational Planning and Control | 10.5、11.4、11.8、14.4 |
| ISO/IEC 27701:2025 第 9 章 | Performance Evaluation | 15、16.4 |
| ISO/IEC 27701:2025 第 10 章 | Improvement | 10.5、12、16、17 |
| ISO/IEC 42005:2025 5.1–5.3 | AIA Process、Documentation、Integration | 9、10.7、13.10 |
| ISO/IEC 42005:2025 5.4–5.6 | Timing、Scope、Responsibilities | 7、9.3、10.7 |
| ISO/IEC 42005:2025 5.7 | Sensitive/Restricted Use and Impact Thresholds | 5.4、10.7、13.10 |
| ISO/IEC 42005:2025 5.8–5.9 | Perform and Analyse AIA | 10.7、11.10、13.10、14.8 |
| ISO/IEC 42005:2025 5.10–5.11 | Recording、Reporting、Approval | 7、10.7、16 |
| ISO/IEC 42005:2025 5.12 | Monitoring and Review | 9.3、10.7、16.4 |
| ISO/IEC 42005:2025 第 6 章 | AIA Documentation | 13.10、20.10 |
| ISO/IEC 23894:2023 第 4 章 | AI Risk Management Principles | 6、7、10.7、11.10 |
| ISO/IEC 23894:2023 5.2–5.7 | Leadership、Integration、Design、Implementation、Evaluation、Improvement | 7、9、10.7、15、16 |
| ISO/IEC 23894:2023 6.2 | Communication and Consultation | 7、10.7、13.10 |
| ISO/IEC 23894:2023 6.3 | Scope、Context、Criteria | 3、5、9.2、10.7 |
| ISO/IEC 23894:2023 6.4–6.5 | Risk Assessment and Treatment | 10.7、11.10、13.10、14.8 |
| ISO/IEC 23894:2023 6.6–6.7 | Monitoring/Review、Recording/Reporting | 9.3、10.7、16 |
| ISO/IEC 23894:2023 Annex A–C | Objectives、Risk Sources、Lifecycle Mapping | 10.7、11.10、14.8 |
| OWASP ASVS 5.0.0 | Versioned Requirement IDs and Application Security Verification | 13.8、14.6、15.2、20.8 |
| OWASP ASVS 5.0.0 | Stable Version 5.0.0；`v<version>-<id>` Reference | 15.2、19.2、20.14 |
| OWASP LLMSVS 2.0 V1–V2 | Secure Configuration/Maintenance、Model Lifecycle | 11.5、11.6、11.10、13.8 |
| OWASP LLMSVS 2.0 V3–V4 | Real-time Learning、Model Memory/Storage | 11.4、11.7、11.10 |
| OWASP LLMSVS 2.0 V5–V6 | Secure Integration、Agents/Plugins | 7.3、11.2、11.10–11.12 |
| OWASP LLMSVS 2.0 V7–V8 | Dependency/Component、Monitoring/Anomaly | 10.8、11.5、11.7、16.4 |

规范性国际标准来源：

1. ISO, [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) 与 [ISO/IEC 27001:2022/Amd 1:2024](https://www.iso.org/standard/88435.html)。
2. ISO, [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html)。
3. ISO, [ISO/IEC 27701:2025](https://www.iso.org/standard/27701)。
4. ISO, [ISO/IEC 42005:2025](https://www.iso.org/standard/42005)。
5. ISO, [ISO/IEC 23894:2023](https://www.iso.org/standard/77304.html)。

开放行业规范来源：

1. OWASP, [Application Security Verification Standard 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)。
2. OWASP, [Large Language Model Security Verification Standard 2.0](https://owasp.org/www-project-llm-verification-standard/LLMSVS-v2.0-en.html)。

监测来源：

1. OWASP, [Artificial Intelligence Security Verification Standard 1.0](https://owasp.org/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/)。
