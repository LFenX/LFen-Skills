# E04 知识与正式记录治理扩展规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | E04 |
| 英文名称 | Knowledge and Records Governance Extension Specification |
| 正式文件名 | `E04_Knowledge_and_Records_Governance_Extension_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 编制适用性 | 必须编制 |
| 当前激活状态 | 已激活 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 核心规范依赖 | C01 至 C12 V6.3 |
| 已编制扩展依赖 | E01、E02、E03 V6.3 |
| 生产前调研 | RVR-E04-0001 |
| 后续规范 | E05 |
| 访问级别 | 内部 |
| 保留要求 | 按 RCS、RTS、法律、监管、合同、许可、Security、Privacy、Legal Hold、C05 Evidence 和 C11 Baseline 要求保留；来源、版本、批准、访问、迁移、替代、处置和更正历史禁止无痕删除 |

本文件在项目负责人批准前不得作为已批准的 E04 正文。VC-PPG-DEC-001 已独立规定 E04 控制目标对当前规范生产活动立即生效；因此本文件的 `Draft` 状态不改变 `当前激活状态 = 已激活`。修改当前激活状态必须建立 C11 Change Request。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定产品知识、正式记录、术语、来源、Provenance、分类、访问、保留、新鲜度、替代、检索、迁移、处置、审计和历史恢复治理。

本规范实现以下目标：

1. 使 Formal Knowledge 与 Chat、Prompt、Session Memory、Scratchpad 和临时 Tool Output 分离；
2. 使每项 Knowledge 具有稳定 ID、类型、名称、Source、Owner、Revision、Validity、Access、Retention、Freshness 和 Supersession；
3. 使每项 Source 具有主体、获取方式、时间、版本、可信级别、许可或使用限制和完整性；
4. 使 Record 具有业务用途、分类、Metadata、Sensitivity、Integrity、Access、Retention 和 Disposition；
5. 使 Record 的 Authenticity、Reliability、Integrity 和 Useability 可验证；
6. 使术语定义、禁止同义词、Scope、Owner、批准版本和替代术语受控；
7. 使 Knowledge Freshness 依据时间、事件、依赖变化、来源变化和冲突持续复核；
8. 使 Superseded Knowledge 保留历史和血缘，但不进入默认 Agent Context；
9. 使 Retrieval Result 随附 Source、Revision、Validity、Freshness、Classification 和 Retrieval Time；
10. 使 Access 遵循明确授权、最小披露、敏感过滤、拒绝、日志和例外规则；
11. 使 Retention、Archive、Legal Hold、Migration、Conversion 和 Disposition 有 Authority、范围、验证和 Evidence；
12. 使知识和记录命令具有固定工具、目标、版本、模式、资源上限、Stop、Rollback 和输出控制；
13. 防止用 Search Hit、Vector Similarity、Tool Success、文件存在、Git Commit 或 Agent Confidence 自动推导知识有效、记录权威或处置合规；
14. 防止 Agent 自批 Knowledge Validity、Access Exception、Retention、Disposition、Waiver、Risk Acceptance 或 Gate；
15. 使当前规范仓库的正式文档、调研来源、检查记录和 Git 历史从生成时即受最低 E04 控制；
16. 在 Active、Pending、Conditionally Active、Retiring 和 Retired 期间保持知识与记录可追溯和可恢复。

## 3. 适用范围

E04 在任一触发条件成立时必须激活：

- 存在多 Agent、多会话或多人长期维护；
- 产品知识需要跨项目复用；
- 需要审计、Evidence 保留或历史恢复；
- Decision、Requirement、Design、Context、Source 或运行记录数量快速增长。

激活后的 E04 适用于：

- Product、Initiative、Requirement、Design、Decision、Code、Configuration、Release 和 Operation 知识；
- Policy、Standard、Specification、Plan、Record、Report、Register、Matrix、Checklist、Template 和 Evidence；
- Document、Repository、Issue Tracker、Knowledge Base、Wiki、Object Storage、Database、Search Index 和 Vector Store；
- Human-authored、Agent-generated、Tool-generated、Imported、Derived 和 Migrated 内容；
- Source Document、Source Data、Observation、External Standard、Contract、Decision、Run 和 Evidence；
- Chat、Prompt、Session Summary、Stable Context Manifest、Retrieval Result 和 Agent Run 进入 Formal Knowledge 的 Capture 过程；
- Development、Review、Approval、Release、Operation、Archive、Migration、Disposition 和 Recovery 阶段；
- P2 档位下 KAC、VOC、SPR、RCS、RTS、KFR、SKR 和 RAP；
- Owner、Author、Source Steward、Records Manager、Configuration Manager、Reviewer、Approver、Operator、Auditor、Agent 和 Tool；
- Backup、Replica、Cache、Export、Embedding、Index、Snapshot、Archive 和 Disposal Copy。

### 3.1 当前仓库状态

当前仓库已满足全部 E04 激活条件，因此：

1. `编制适用性 = 必须编制`；
2. `当前激活状态 = 已激活`；
3. 规范文档必须保留控制信息、来源、版本、状态、依赖、评审和 Git 历史；
4. 每份正式规范生产前必须有调研记录，生产后必须有结构与符合性检查记录；
5. 被后续版本替代的规范、蓝图、决议和记录必须保留 Git 历史和受控替代关系；
6. 当前正式上下文只能引用可定位 Revision；不得把未复核会话摘要作为默认事实源；
7. 本仓库使用 Git 作为实现层版本与历史载体，但 Git Hash 不替代业务 Asset ID、Revision、DOC State、Approval 或 Baseline；
8. E04 V0.1 Draft 自身遵循来源登记、文档控制、检查、独立 Git 基线和历史不可无痕覆盖要求；
9. E04 详细正文在批准前不是已批准规范，但其上位决议规定的控制目标继续生效；
10. 修改本节激活结论必须引用已批准 C11 Change Request。

### 3.2 横向生效边界

1. C01 至 C03 管理 Evidence、Product、Scope、PRD、Feature、Risk 和指标意图；
2. C04 管理原子 Requirement 和 Requirement Set；
3. C05 管理 Acceptance、Verification、Validation 和 Evidence；
4. C06 管理 UX 与 Technical Design；
5. C07 至 C09 管理 Authority、Agent Role、Context、Run、Command 和运行记录；
6. C10 管理 Decision、Trace Link、Lineage、Impact Query 和 Orphan；
7. C11 管理 Revision、Snapshot、Baseline、Change、Release Configuration 和恢复点；
8. C12 管理 Review、Gate、Waiver、Risk Acceptance 和 Product Health；
9. E01 管理 Architecture Concern、View、Decision、Fitness 和 Conformance；
10. E02 管理 Security、Privacy、Compliance、PII、License 和 AI Impact；
11. E03 管理 Data/AI Data Requirement、Contract、Quality、Dataset、Corpus 和 Data Lineage；
12. E04 管理 Knowledge、Record、Vocabulary、Source、Provenance、Access、Retention、Freshness、Supersession 和 Retrieval；
13. E05 管理 Service、SLO、Monitoring、Incident、Continuity 和 Operation。

## 4. 不适用范围

本规范不负责：

- 代替 C04 Requirement Record；
- 代替 C05 Acceptance Criteria、Verification Plan、Evidence 或 Acceptance Decision；
- 代替 C06 Technical Design Specification；
- 代替 C07 Human Authority 或 C09 Agent Run Record；
- 代替 C10 Decision Record、Trace Link Register、Bidirectional Traceability Matrix 或 Impact Query；
- 代替 C11 Change Request、Baseline、Release Configuration 或恢复执行；
- 代替 C12 Gate Decision、Exception or Waiver Record 或 Risk Acceptance Record；
- 代替 E02 Access Risk、Privacy、PII、Compliance、License 或 Legal 结论；
- 代替 E03 Data Contract、Data Dictionary、Data Lineage、Corpus Record 或 Data Retention Rule；
- 代替 E05 Incident、Service Review、Backup Operation 或 Continuity Plan；
- 规定唯一 DMS、ECM、Knowledge Base、Wiki、Search Engine、Vector Database、Repository、Archive 或 Backup 产品；
- 规定唯一 Embedding Model、Ranking Algorithm、Chunking Strategy、OCR、Classification Model 或 Storage Format；
- 保存 Agent 私有思维链；
- 声明项目、组织、流程、记录系统或知识系统获得 ISO 认证；
- 提供著作权、许可、个人信息、保密、Legal Hold、监管或处置的法律结论。

E04 可以消费上述事实，但禁止：

- 用 KAC 复制并替代 Knowledge 正文；
- 用 VOC 替代 C04 Requirement 或 E03 Data Dictionary；
- 用 SPR 自动证明 Source 真实、合法、完整或可用于任意目的；
- 用 RCS 替代 E02 Security/Privacy Classification 的有权判断；
- 用 RTS 自动作出法律保留、删除或匿名化结论；
- 用 KFR 自动证明产品正确、Requirement 满足或模型有效；
- 用 SKR 删除被替代 Knowledge；
- 用 RAP 授予超过 E02、合同、许可或 Authority Boundary 的权限；
- 用高检索分数自动判定知识真实、当前或适用；
- 用 Git Commit 自动判定文档已批准、已发布或形成 Baseline；
- 用备份存在自动证明记录可恢复；
- 用工具 Exit Code 自动判定 Capture、Migration、Retention 或 Disposition 通过；
- 用普通 EWR 绕过 Security、Privacy、Legal Hold、不可逆处置、Non-waivable Gate 或 Authority Boundary。

## 5. 规范性用语与受控判定

### 5.1 规范性用语

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

法律、监管、合同、Security、Privacy、Safety、PII、许可、Legal Hold、不可逆处置、Non-waivable Gate 和 Authority Boundary 不得通过普通 EWR 绕过。

### 5.2 扩展适用性判定值

以下值是 E04 Activation Status，不是 DOC State：

| 值 | 语义 |
|---|---|
| Not Evaluated | 尚未评价；禁止进入 Discovery Ready |
| Pending | 存在未知项或等待 Evidence/Authority；禁止判为 Inactive |
| Inactive | 全部触发条件明确为 No |
| Conditionally Active | 在明确 Scope、条件和期限内激活 |
| Active | 任一触发条件成立，E04 完整适用 |
| Retiring | 正在退出但仍需维护迁移、访问、保留、处置、依赖和历史控制 |
| Retired | 当前 Scope 不再适用；历史 Knowledge 和 Record 继续保留 |

### 5.3 触发条件判定值

| 值 | 语义 |
|---|---|
| Yes | 条件已由 Evidence 证实 |
| No | 条件已由 Evidence 排除 |
| Unknown | 证据不足、Scope 不明确或等待有权判断 |
| Not Applicable | 条件本身不属于被评 Scope；必须有理由和批准者 |

任一 Yes 使 E04 进入 Active 或 Conditionally Active。任一 Unknown 使 E04 进入 Pending。当前仓库四项触发条件均为 Yes。

### 5.4 领域判定值

以下值是字段级 Result，不是资产 State：

| 判定域 | 允许值 |
|---|---|
| Knowledge Validity | Current、Conditionally Current、Stale、Conflicted、Superseded、Withdrawn、Unknown |
| Freshness Result | Fresh、Due for Review、Stale、Conflicted、Not Evaluated |
| Source Trust | Authoritative、Verified、Corroborated、Unverified、Disputed、Prohibited |
| Record Authority | Authoritative、Conditionally Authoritative、Non-authoritative、Unknown |
| Access Result | Allowed、Allowed with Filtering、Denied、Pending Authority、Not Evaluated |
| Capture Result | Complete、Partial、Failed、Not Evaluated |
| Migration Result | Verified、Conditionally Verified、Failed、Not Evaluated |
| Disposition Result | Completed、Partially Completed、Failed、Blocked、Not Due |
| Retrieval Fitness | Fit for Context、Conditionally Fit、Not Fit、Unknown |

每个 Result 必须记录 Scope、对象 Revision、Criteria、Evidence、Evaluator 和时间。禁止把 Result 注册为 DOC State。

### 5.5 未知和不适用

1. Source、Owner、Revision、Validity、Access、Retention、License、Legal Hold 或 Replacement 未知时必须显式记录 Unknown/Pending；
2. 空值禁止替代 Unknown、Not Applicable 或 Not Evaluated；
3. Unknown Source 或 Unknown Use Restriction 的 Knowledge 禁止进入默认 Context；
4. Unknown Legal Hold 的 Record 禁止执行不可逆 Disposition；
5. Unknown Freshness 的 Knowledge 不得被标为 Current；
6. Not Applicable 必须记录 Scope、理由、依据和批准者；
7. Agent 禁止推断未知的权限、许可、真实性、有效性或删除义务。

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Knowledge | 在明确 Scope、用途和责任下可被理解、复用或用于行动的信息及其语义 |
| Formal Knowledge | 已完成 Capture、Source 登记、Owner 指派、Revision 固定、Review 和 KAC 登记的受控 Knowledge |
| Temporary Context | 为单次会话、任务或运行临时组装且尚未成为 Formal Knowledge 的输入集合 |
| Record | 作为业务活动、决定、事实或事务 Evidence 而创建、接收并保留的信息 |
| Authoritative Record | 在规定 Scope 内满足 Authenticity、Reliability、Integrity 和 Useability 要求的 Record |
| Knowledge Source | Knowledge 或 Record 直接取自、观察自、生成自或接收自的主体或对象；专业化自 VC-PPG-COM-001 Source |
| Knowledge Provenance | Knowledge Source 的获取、生成、处理、责任主体、时间、方法、版本和使用限制历史；专业化自 VC-PPG-COM-001 Provenance |
| Metadata | 描述资产内容、背景、结构、管理过程、责任、关系和控制的信息 |
| Knowledge Asset | 具有稳定 Knowledge ID、Owner、Revision、Validity 和治理边界的 Formal Knowledge |
| Record Capture | 将 Record 连同 Metadata、分类、权限和保留规则纳入受控记录系统的动作 |
| Record Classification | 按业务功能、用途、敏感性、完整性、访问和保留需求组织 Record 的规则 |
| Retention | Record 或 Knowledge 在起算事件后必须保留的期间和条件 |
| Legal Hold | 暂停常规 Disposition 的有权保留指令 |
| Disposition | 经授权执行 Archive、Transfer、Anonymization、Deletion、Destruction 或其他最终处理的过程 |
| Freshness | Knowledge Revision 相对时间、事件、依赖、来源和使用 Context 的当前适用程度 |
| Stale Knowledge | 已超过复核条件或关键依赖已变化，不能继续默认作为 Current 的 Knowledge |
| Conflicted Knowledge | 与同 Scope 下另一受控 Knowledge 存在未解决矛盾的 Knowledge |
| Superseded Knowledge | 已由新 Knowledge 使其退出当前有效集合的旧 Knowledge |
| Retrieval | 按 Query、Scope、Identity、Policy 和 Ranking 从受控知识集合取得候选内容的过程 |
| Retrieval Result | 固定 Query、策略、索引、候选 Knowledge Revision、排名、过滤、来源和时间的检索输出 |
| Context Manifest | 固定某次 Context 所含资产、Revision、来源、优先级、有效期、敏感级别和完整性的信息 |
| Controlled Vocabulary | 对正式术语、定义、Scope、禁止同义词和替代术语的受控集合 |
| Knowledge Owner | 对 Knowledge 内容、用途、有效性、复核和替代负责的人类角色 |
| Source Steward | 对 Source 身份、Provenance、可信级别、版本和使用限制登记负责的角色 |
| Records Manager | 对 Record 分类、Capture、保留、访问、迁移和处置过程负责的角色 |
| Disposition Authority | 有权批准 Record 最终处置的人类角色 |
| Authenticity | Record 能够证明其所声称身份、创建者、接收者、时间和背景的属性 |
| Reliability | Record 内容能够在规定 Scope 内作为对业务活动准确表示而被信赖的属性 |
| Integrity | Record 完整且未被未授权改变，授权变化可追踪的属性 |
| Useability | Record 可被定位、检索、呈现、理解并与业务活动关联的属性 |

`Evidence` 的唯一语义直接适用 VC-PPG-COM-001；其验证充分性直接适用 C05，Review 与 Gate 使用直接适用 C12。E04 只定义 Record 和 Knowledge 对 Evidence 的承载与治理关系，不建立平行 Evidence 定义。

### 6.1 Knowledge、Record 与 Evidence 边界

1. Knowledge 强调可理解和复用；Record 强调业务活动或决定的 Evidence；
2. 同一对象可以同时承担 Knowledge 和 Record 角色，但必须分别满足适用控制；
3. Evidence 是对象在某个 Verification/Decision 中的用途，不自动等于 Authoritative Record；
4. KAC 登记不自动使对象成为 Evidence；Evidence 仍必须固定 Revision、Criteria 和 Provenance；
5. Report 是对 Evidence 的分析，不自动替代原始 Evidence；
6. Template、Checklist、Search Index 和 Embedding 不是原 Knowledge 的权威替代物。

### 6.2 Source、Provenance、Lineage 与 Trace 边界

1. Source 回答“直接来自哪里”；
2. Provenance 回答“如何取得、生成、处理并形成当前 Revision”；
3. Asset Lineage 使用 C10 受控关系描述跨资产演进；
4. Trace Link 描述两个受控资产之间的明确方向关系；
5. Git History 是实现层历史 Evidence，不替代 SPR、KAC、C10 Trace 或 C11 Change；
6. 相似性、链接或同目录不构成受控关系。

### 6.3 Session、Context 与 Formal Knowledge 边界

1. Chat、Prompt、Session Memory、Scratchpad、Agent Summary 和 Tool Output 默认属于 Temporary Context；
2. Temporary Context 不能仅因被多次使用而自动成为 Formal Knowledge；
3. Capture 为 Formal Knowledge 必须完成内容提炼、Source/Provenance、Owner、Revision、Review、Access、Retention 和 KAC 登记；
4. 禁止保留 Agent 私有思维链；可以保留任务输入、批准所需理由摘要、输出、命令、Evidence 和人类决定；
5. Stable Context Manifest 固定 Context 成员，不证明成员内容真实、当前或已授权；
6. Context 过期后必须失效或重建，禁止只更新生成时间而复用旧成员。

### 6.4 Revision、Snapshot、Baseline 与 Git 边界

1. Asset ID 表示业务身份；Revision 表示该身份的受控内容版本；
2. Snapshot 是特定时点状态；Baseline 是经批准的配置集合；
3. Git Commit Hash 可定位实现状态，但不表示业务批准；
4. Git Tag 只有在 C11 明确绑定 Baseline 时才是 Baseline 实现引用；
5. 修改 Current Knowledge 必须创建新 Revision；禁止覆盖历史 Revision；
6. 修正文案错误是否保持身份，按公共需求演进和 C11 Change 规则判定。

## 7. 角色、职责与职责分离

### 7.1 角色

| 角色 | 必须职责 | 禁止事项 |
|---|---|---|
| 项目负责人 | 批准 E04、Policy、重大例外、激活变化和处置权限 | 不得批准自己无权处理的法律事项 |
| Knowledge Owner | 内容边界、Validity、Freshness、冲突、替代和消费方影响 | 不得无 Evidence 把 Unknown 判 Current |
| Records Manager | RCS、Capture、Metadata、RTS 执行、迁移和处置协调 | 不得绕过 Legal Hold 或 Disposition Authority |
| Source Steward | Source 身份、版本、获取、可信级别、限制和 Integrity | 不得把可访问推断为可授权使用 |
| Vocabulary Owner | 术语、定义、禁止同义词、Scope 和替代词 | 不得在 VOC 中重写上位公共术语 |
| Access Authority | RAP、角色映射、最小披露、例外和周期复核 | 不得授予超出 E02 或合同边界的权限 |
| Disposition Authority | 批准 Archive、Transfer、Anonymization、Deletion 或 Destruction | 不得批准受 Legal Hold 对象 |
| Configuration Manager | Revision、Snapshot、Baseline、Change、状态核算和恢复点 | 不得把 Commit 自动标为 Approved |
| Reviewer | 独立检查内容、来源、有效性、访问、保留和 Evidence | 不得评审自己的高风险处置 |
| Auditor | 检查记录系统、访问、变化、保留、处置和恢复 Evidence | 不得修改被审计原始记录 |
| Operator | 按批准命令执行 Capture、Index、Migration、Archive、Restore 或 Disposition | 不得扩大 Target 或跳过 Dry-run |
| Agent | 在授权 Context 内检索、总结、生成候选内容和检查结果 | 不得批准、授权、接受 Risk、关闭 Gate 或执行未授权不可逆处置 |

### 7.2 最低职责分离

以下事项必须至少有两个不同责任主体：

1. 高风险 Knowledge 创建与 Validity 批准；
2. Access Exception 申请与批准；
3. RTS 制定与不可逆 Disposition 批准；
4. Migration 执行与结果验证；
5. Supersession 提议与生效批准；
6. Legal Hold 解除与 Disposition 执行；
7. 高风险 Retrieval Policy 变更与验证；
8. Agent 生成知识与人类 Review；
9. Audit 执行与被审计记录维护；
10. Baseline 建立与 Gate Decision。

### 7.3 Authority 规则

1. Authority 必须引用 C07 Human Authority 或等价已批准来源；
2. Authority 必须限定操作、对象、Revision、环境、期限和资源上限；
3. 群组成员身份不能代替 Authority Evidence；
4. 自动化 Token、Service Account 和 Agent Role 只能执行被明确委托的动作；
5. Authority 缺失、过期、冲突或撤销时必须 Fail Closed；
6. 紧急访问必须记录原因、最小 Scope、时限、审计和事后复核；
7. 法律、监管、Privacy 和 Legal Hold 结论必须由有权角色处理。

## 8. 受控产物与关系

### 8.1 正式产物

| 代码 | 正式产物 | 状态模型 | 治理目的 |
|---|---|---|---|
| KAC | Knowledge Asset Catalog | DOC | 登记 Knowledge 身份、来源、Owner、Revision、Validity、Access、Retention、Freshness 和 Replacement |
| VOC | Controlled Vocabulary | DOC | 管理正式术语、定义、禁止同义词、Scope 和替代术语 |
| SPR | Source and Provenance Register | DOC | 管理 Source 身份、获取、版本、可信、使用限制、Integrity 和关联 Knowledge |
| RCS | Record Classification Scheme | DOC | 管理 Record 分类、用途、Sensitivity、Integrity、Access、Retention 和 Disposition |
| RTS | Retention Schedule | DOC | 管理起算事件、期间、依据、Archive、Legal Hold、Disposition、Approval 和 Review |
| KFR | Knowledge Freshness Report | DOC | 评价 Knowledge Revision 新鲜度、冲突、影响、Owner 和行动 |
| SKR | Superseded Knowledge Register | DOC | 登记旧新 Knowledge、替代原因、生效、Context 影响、迁移和历史保留 |
| RAP | Retrieval and Access Policy | DOC | 管理分类、角色、检索 Scope、最小披露、显示、过滤、日志、拒绝和例外 |

八类产物必须保持独立身份、Revision、DOC State 和模板。允许同一 Repository 承载多个实例，禁止把八类产物合并为单一无类型“知识台账”。

### 8.2 通用必填字段

八类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。E04 不拆分或改名公共字段。

### 8.3 成员与容器

1. KAC、VOC、SPR、RCS、RTS、KFR、SKR 和 RAP 均是 DOC 资产；
2. KAC、VOC、SPR、RCS、RTS、SKR 和 RAP 包含受控成员；KFR 包含固定检查对象和评价结果，不使用 Register Member Status；
3. 容器 DOC State 不等于成员 Validity、Member Status 或 KFR 的 Freshness Result；
4. 受控成员必须有稳定 Member ID、Member Status、Effective Time 和 History Reference；
5. 删除成员必须由 Revision 和历史表示，禁止直接从历史 Revision 抹除；
6. Catalog 中的 `Current` 成员不能自动使其指向的 Knowledge 进入 Approved；
7. KFR 的 `Fresh` 结果不能改变被检查 Knowledge 的 DOC State；
8. SKR 成员生效后必须触发 KAC、RAP、Index、Cache、Context 和 C10 Trace 检查。

### 8.4 受控关系

只允许使用公共基线定义的关系：

| 关系 | E04 使用 |
|---|---|
| derives-from | Knowledge 从 Source、Requirement、Decision 或其他 Knowledge 派生 |
| contains | Knowledge Package 或 Catalog 包含独立成员知识 |
| refines | 新 Revision 提高细节但不改变上位义务 |
| extends | Knowledge 增加独立能力或适用范围 |
| depends-on | Knowledge Validity、Freshness 或 Use 依赖另一资产 |
| constrains | Policy、RAP、RTS 或 RCS 限制另一资产 |
| verified-by | 仅用于 Requirement 或 Criterion 由 Verification Evidence 证明；E04 负责该 Evidence 的记录治理 |
| validated-by | 仅用于 Need、Intent 或 Goal 由 Validation 结果支持；E04 负责该结果的记录治理 |
| affected-by | Knowledge/Record 受 Change、Risk、Incident 或 Source Change 影响 |
| supersedes | 当前 Knowledge 使旧 Knowledge 退出当前有效集合 |
| replaces | 当前 Knowledge 直接接替旧 Knowledge 的职责或义务 |
| generated-by | Knowledge、Record 或 Report 由 Run、Tool 或 Process 生成 |
| observed-from | Learning、Issue 或 Knowledge 来自运行观察 |
| released-in | Knowledge/Record Revision 包含于 Release Configuration |
| implemented-by | 仅用于 Requirement 或 Design 由可定位代码、配置或部署资产实现 |

禁止使用 `related-to`、“相关”“参考了”或无方向超链接作为正式关系。

### 8.5 最低关系链

至少必须可查询：

```text
Knowledge -derives-from-> Source
Catalog -contains-> Knowledge
Context -depends-on-> Knowledge
New Knowledge -supersedes-> Old Knowledge
Knowledge -affected-by-> Change/Risk/Incident
Record -depends-on-> Retention Rule
Requirement -verified-by-> Evidence
```

关系箭头仅表示查询方向示意；正式登记必须使用第 8.4 节关系词和明确源/目标。

## 9. E04 治理生命周期

### 9.1 生命周期

```text
Scope and Appraisal
  -> Identification
  -> Creation or Receipt
  -> Capture
  -> Classification and Indexing
  -> Review and Approval
  -> Baseline or Publication
  -> Retrieval and Use
  -> Freshness Monitoring
  -> Change or Supersession
  -> Retention, Archive or Migration
  -> Authorized Disposition
  -> Audit and Improvement
```

### 9.2 Scope 与 Appraisal

1. 明确业务活动、受影响方、使用 Context、Record 义务和 Knowledge 风险；
2. 识别必须创建和保留的 Record；
3. 识别默认可检索、条件可检索和禁止检索的 Knowledge；
4. 识别法律、监管、合同、Security、Privacy、许可和 Legal Hold 约束；
5. 确定 KAC、RCS、RTS 和 RAP Scope；
6. 未完成 Appraisal 时禁止使用统一永久保留或统一立即删除规则。

### 9.3 Identification 与 Creation

1. 创建稳定 Asset ID 和明确 Artifact Type；
2. 固定 Source、Author/Creator、时间、工具、方法和初始 Revision；
3. 记录 Purpose、Intended Use、Prohibited Use 和 Consumer；
4. 指派 Owner、Reviewer 和适用 Authority；
5. 生成内容不得覆盖 Source 原件；
6. Agent 生成内容必须标记 `generated-by`，不得伪装为人类原作。

### 9.4 Capture 与 Classification

1. Capture 必须同时登记正文或指针、Metadata、Classification、Access 和 Retention；
2. Capture Result 为 Partial/Failed 时禁止进入默认检索；
3. Record 必须映射 RCS Category；
4. Knowledge 必须映射 KAC Type 和 RAP Classification；
5. Source 必须进入 SPR；
6. 术语变更必须进入 VOC；
7. 捕获后必须验证可定位、可读取、完整性和访问控制。

### 9.5 Review、Approval 与 Baseline

1. Review 必须固定对象 Revision、Criteria、Source 和 Evidence；
2. 高风险或默认 Context Knowledge 必须有人类 Reviewer；
3. Approval 只能由有权人执行；
4. 批准结果通过 DOC State/C12 Decision 表示，不通过文件名或目录推断；
5. Baseline 由 C11 建立，并记录成员 Revision、Git 引用或存储指针和恢复方式；
6. 审批后修改必须创建新 Revision 和适用 Change。

### 9.6 Retrieval 与 Use

1. 每次检索必须执行 Identity、Scope、RAP、Classification、Freshness 和 Validity 过滤；
2. 默认只返回 Current 且 Fresh/允许条件内的 Knowledge；
3. Conditionally Current 必须显示条件和到期时间；
4. Stale、Conflicted、Superseded、Withdrawn 或 Unknown 禁止默认返回；
5. 历史查询可以返回非 Current 内容，但必须显著标记并禁止混入默认上下文；
6. Retrieval Result 必须固定 Query、Policy Revision、Index Revision、候选和过滤结果；
7. Context Manifest 必须固定最终采用的 Knowledge Revision。

### 9.7 Freshness、Change 与 Supersession

1. Freshness 由时间周期和事件触发共同管理；
2. Source Change、Requirement Change、Decision Supersession、Standard Update、Incident、Defect、Consumer Feedback 和 Owner Review 均可触发；
3. 发现冲突时必须将相关 Knowledge 标记 Conflicted 或 Conditionally Current，禁止静默选择；
4. 内容变化按 C11 建立 Revision/Change；
5. 旧 Knowledge 退出当前有效集合时建立 SKR 和 `supersedes`/`replaces`；
6. Supersession 必须更新 Context、Index、Cache、Embedding、Link、Reference 和 Consumer；
7. 历史 Revision 继续按 RTS 保留。

### 9.8 Retention、Migration 与 Disposition

1. Retention 必须映射 RCS Category 和 RTS Rule；
2. 起算事件必须可验证，不得只写“项目结束后”而无事件定义；
3. Migration/Conversion 前必须固定 Source、Target Format、Mapping、Tool、Checksum、Sample 和 Rollback；
4. Migration 后必须验证数量、结构、Metadata、权限、内容完整性、可检索性和关系；
5. Legal Hold 检查必须在 Disposition 批准和执行前分别进行；
6. 不可逆处置默认 Dry-run，并由独立 Reviewer 验证 Scope；
7. Backup、Replica、Cache、Export、Index 和 Derived Copy 必须进入处置范围或记录合法排除理由；
8. Disposition 完成后保留最小处置记录，不保留应被销毁的原内容。

### 9.9 Audit 与 Improvement

1. 周期检查 KAC 完整性、VOC 冲突、SPR 未知来源、RCS 覆盖、RTS 到期、KFR 逾期、SKR 迁移和 RAP 例外；
2. Audit 必须使用只读数据集或受控快照；
3. 发现不符合时进入适用 Defect、Risk、Change 或 Corrective Action；
4. Audit Report 不得修改原始日志；
5. 改进效果必须重新验证；
6. 历史审计 Evidence 按 RTS 保留。

## 10. 适用性与治理过程

### 10.1 Applicability Decision

每个目标产品必须在 Discovery Ready 前完成：

1. 固定 Product、Scope、Revision 和 Decision Owner；
2. 逐项判断四个触发条件；
3. 每项记录 Yes/No/Unknown/Not Applicable 和 Evidence；
4. 任一 Unknown 映射 Pending；
5. 决定 Activation Status、Effective Time 和 Review Trigger；
6. 识别需要实例化的八类产物；
7. 通过 C12 Review；
8. 将 Activation Decision 纳入 C11 Baseline。

### 10.2 当前项目即时控制

本规范仓库从现在起必须：

- 每份规范有固定文件名、文档编号、Revision 和 DOC State；
- 每次生产前调研记录官方 Source、访问日期、版本和状态；
- 每次生产后建立结构与符合性检查记录；
- 每个阶段形成独立 Git Commit；
- 文件修改通过 Diff 可查，禁止覆盖 Git 历史；
- 外部标准引用固定版本和官方链接；
- 当前知识引用明确到文件 Revision 或 Git Baseline；
- 会话内容只作为工作材料，正式结论必须写入受控文件；
- 过期或被替代结论不得继续作为默认上下文；
- E04 激活状态变化必须走 C11 Change。

### 10.3 Knowledge Onboarding

1. 识别 Knowledge Purpose、Scope、Consumer 和 Risk；
2. 创建或复用 Knowledge ID；
3. 登记 Source/Provenance；
4. 确认许可、访问和敏感限制；
5. 指派 Owner；
6. 固定 Revision 和 Integrity Reference；
7. 执行内容、术语、冲突和 Freshness Review；
8. 登记 KAC；
9. 应用 RAP 和 RTS；
10. 建立 Trace；
11. 批准后进入默认检索；
12. 记录下次复核时间和事件触发器。

### 10.4 Record Capture

1. 判断对象是否必须作为 Record；
2. 指定 Record ID 和 Category；
3. 捕获 Content/Pointer 和 Metadata；
4. 固定 Creator、Receiver、Time、Business Activity 和 Integrity；
5. 应用 RCS、RAP 和 RTS；
6. 验证可检索、可呈现和上下文关联；
7. 记录 Capture Result；
8. Capture 失败时保留失败 Evidence 并重试或升级。

### 10.5 Vocabulary Governance

1. 新术语先检查公共术语基线和现有 VOC；
2. 正式名称必须唯一；
3. 定义必须说明 Scope 和排除边界；
4. 禁止同义词必须能被扫描；
5. 上位术语不得在局部规范中重定义；
6. 术语变化必须识别所有 Consumer；
7. 替代术语保留原 Term ID 和迁移规则；
8. 术语冲突未解决时不得批准引用该术语的新基线。

### 10.6 Freshness Evaluation

1. 固定 Knowledge ID/Revision；
2. 读取时间规则和事件触发器；
3. 检查 Source、依赖、标准、Requirement、Decision 和运行事实是否变化；
4. 查找同 Scope 冲突 Knowledge；
5. 评价 Consumer Impact；
6. 形成 Freshness Result 和 Knowledge Validity 建议；
7. 指派 Action、Owner、Due Date；
8. 独立 Review；
9. 更新 KFR、KAC、SKR 和 Index；
10. 保留 Evidence。

### 10.7 Retrieval and Context Assembly

1. 固定 Query、Purpose、Requester、Agent Role、Scope 和时间；
2. 解析 Identity 与 Authority；
3. 加载 RAP Revision；
4. 按 Classification 和最小披露过滤；
5. 排除 Prohibited Source 和禁止用途；
6. 按 Validity/Freshness 排除非默认知识；
7. 执行关键词、结构化或向量检索；
8. 记录候选、Score、过滤原因和排序；
9. 检查冲突、重复和版本；
10. 选择明确 Revision；
11. 生成 Context Manifest；
12. 执行 Token/Byte/Record Budget；
13. 对敏感字段 Redact；
14. 输出 Source、Validity、Freshness 和限制；
15. 将 Retrieval 和 Context 绑定 C09 Agent Run；
16. 使用结束后执行缓存和临时上下文保留规则。

### 10.8 Supersession

1. 提出旧新 Knowledge 和原因；
2. 验证身份处理是 Revision、Supersession 还是 Replacement；
3. 固定生效时间与 Scope；
4. 查询直接和间接 Consumer；
5. 建立 SKR 成员和 C10 关系；
6. 更新 KAC Validity；
7. 更新 VOC、RAP、RCS、RTS 和依赖文档；
8. 重建 Index/Embedding 或执行失效；
9. 迁移 Stable Context Manifest 和缓存；
10. 验证旧 Knowledge 不再默认返回；
11. 保留历史；
12. 记录完成 Evidence。

### 10.9 Retention and Disposition

1. 固定 Record Category、Rule Revision 和起算事件；
2. 计算到期时间并保留计算依据；
3. 检查法律、监管、合同、Privacy、Security、License 和 Legal Hold；
4. 查询 Primary、Backup、Replica、Cache、Export、Index 和 Derived Copy；
5. 生成候选清单；
6. 执行只读 Review 和 Dry-run；
7. 取得 Disposition Authority；
8. 建立 Snapshot/Recovery 条件；依法不得保留副本时记录不可恢复边界；
9. 分批执行并监测 Stop Conditions；
10. 验证范围、结果、残留和失败项；
11. 形成 Disposition Result；
12. 保留最小处置记录和 Evidence。

## 11. 知识与正式记录控制

### 11.1 正式知识与临时会话分离

1. Chat、Prompt、Session Memory、Agent Summary 和 Scratch 文件默认非正式；
2. 临时材料必须设置短期 Retention 和 Access；
3. 正式结论必须写入明确 Artifact Type；
4. Capture 前必须去除 Secret、Credential、无关 PII 和私有思维链；
5. 会话摘要必须引用 Source，不得把模型补全写成事实；
6. 未完成 Review 的 Agent 输出只能进入 Draft；
7. 临时材料过期后按 RTS 处置，不得以“未来有用”为由永久保留。

### 11.2 Knowledge Identity 与 Catalog

1. 每项 Formal Knowledge 必须有稳定 Knowledge ID；
2. ID 不得包含可变状态、Owner、日期或文件路径；
3. Current Revision 必须唯一；
4. 同 Scope 下多个 Current Knowledge 冲突时全部标记 Conflicted；
5. KAC 必须能查询 Source、Owner、Validity、Freshness、Access、Retention 和 Replacement；
6. Catalog 断链、重复 ID 或无 Owner 必须阻断默认检索；
7. Knowledge 移动位置不得改变业务 ID。

### 11.3 Source 与 Provenance

1. 每项 Knowledge 至少有一个直接 Source；
2. Source 必须有 Source ID、主体、获取方式、时间和版本；
3. Agent/Tool 生成内容必须固定 Tool/Model、Revision、Input Reference 和 Run；
4. Derived Knowledge 必须保留所有关键 Source 和 Transformation；
5. Source Trust 必须有 Criteria 和 Evaluator；
6. Unverified/Disputed Source 禁止作为唯一高风险事实源；
7. Prohibited Source 禁止进入检索、摘要、训练或默认 Context；
8. 来源消失时保留合法允许的最小 Evidence、引用和 Integrity Reference；
9. 未知许可或使用限制必须进入 Pending Authority。

### 11.4 Record Authenticity、Reliability、Integrity 与 Useability

| 属性 | 最低检查 |
|---|---|
| Authenticity | ID、Creator/Receiver、时间、业务活动、来源系统、签名或等价 Integrity Evidence 可核验 |
| Reliability | 创建过程、输入来源、职责、时间接近性、自动化规则和已知限制可检查 |
| Integrity | Hash/Version/Access/Change History 完整，未授权修改能够发现 |
| Useability | 可定位、可读取、可呈现、可理解、可关联业务活动，依赖格式和工具可用 |

1. 四项属性必须按 Record Category 设 Criteria；
2. 不是所有 Record 都要求数字签名；采用的机制必须与 Risk 相称；
3. 转换格式后必须重新验证 Integrity 和 Useability；
4. 任一关键属性 Unknown 时不得标为 Authoritative；
5. 截图、复制文本和搜索摘要不能自动替代 Source Record。

### 11.5 Metadata

Metadata 至少覆盖：

- Identity；
- Title/Description；
- Creator、Receiver、Owner；
- Creation、Receipt、Capture、Update Time；
- Business Activity 和 Purpose；
- Source、Provenance、Tool/Run；
- Revision、State、Validity；
- Classification、Access、Retention；
- Format、Location、Integrity；
- Trace Links；
- Supersession、Migration 和 Disposition History。

Metadata Schema 变化必须受 C11 控制，并验证旧记录兼容和迁移。

### 11.6 Controlled Vocabulary

1. 正式术语必须唯一、可引用且 Scope 明确；
2. 定义不得循环引用；
3. 同义词只能指向一个正式术语；
4. 禁止同义词必须进入 Lint/Review；
5. 缩写首次出现必须展开；
6. 术语变化必须分析 Requirement、Design、Data、Code、Test、Prompt 和 Documentation 影响；
7. 被替代术语保留历史，不从旧 Baseline 重写；
8. 多语言翻译不得建立第二业务身份。

### 11.7 Record Classification

1. 分类以业务功能和用途为主，不仅按文件扩展名或存储位置；
2. 每个 Category 必须有 Sensitivity、Integrity、Owner、Access、Retention 和 Disposition；
3. 分类冲突时采用更严格控制并提交有权复核；
4. 分类变化必须查询现有成员和访问影响；
5. 未分类 Record 禁止进入长期存储和默认共享；
6. 分类结果不得仅由 ML/Agent 自动批准；
7. RCS 必须覆盖日志、访问记录、运行记录、导出、备份和处置记录。

### 11.8 Retention、Legal Hold 与 Disposition

1. RTS 必须使用明确起算事件、期间、依据和处置方式；
2. “永久”必须有有权依据和周期复核，禁止作为默认值；
3. Legal Hold 优先于常规 Disposition；
4. Retention 到期表示进入处置评审，不表示自动删除；
5. 处置方式必须区分 Archive、Transfer、Anonymize、Delete 和 Destroy；
6. 处置必须覆盖所有受控副本或记录排除理由；
7. 不可逆处置必须由 Disposition Authority 批准；
8. 处置失败必须 Fail Closed 并保留失败 Evidence；
9. 处置记录本身按独立 RTS 保留；
10. 数据类对象同时受 E03 RDR 约束时采用更严格适用规则并记录冲突处理。

### 11.9 Freshness

1. 每类 Knowledge 必须规定 Time-based 和 Event-based Review Trigger；
2. Freshness 评价固定 Revision、Scope 和 Intended Use；
3. Source 更新不自动使派生 Knowledge Current；
4. 未变化时间戳不证明内容新鲜；
5. Fresh 只对被评 Scope 和时间有效；
6. Due for Review 不得静默延长；
7. Stale/Conflicted 必须从默认检索移除或显著隔离；
8. 高风险知识必须有更短复核周期或事件监测；
9. KFR 必须记录影响 Consumer、Action、Owner 和 Due；
10. 复核完成后仍需由有权角色更新 Validity。

### 11.10 Conflict 与错误知识

1. 发现冲突时保留全部候选及 Source；
2. 禁止按最后更新时间、最高相似度或模型置信度自动选择；
3. 建立 Conflict Scope、影响、Owner 和截止时间；
4. 高风险冲突必须阻断相关 Gate 或自动动作；
5. 解决冲突后建立 Decision、Revision 或 Supersession；
6. 已传播错误必须查询 Context、Run、Output、Decision 和 Consumer；
7. 更正不得覆盖原历史；
8. 必要时触发 E05 Incident 或 C02 Risk。

### 11.11 Superseded Knowledge

1. 旧 Knowledge 必须保留原 ID、Revision、Source 和历史；
2. SKR 必须记录新旧对象、原因、生效时间、迁移和保留位置；
3. `supersedes` 与 `replaces` 必须按公共关系语义使用；
4. 被替代内容不得继续作为默认 Context；
5. Index、Vector、Cache 和搜索摘要必须更新或失效；
6. 历史查询必须展示 Superseded 标记和当前替代指针；
7. 无替代对象的 Withdrawn Knowledge 必须说明原因和替代工作方式；
8. Consumer 未迁移完成时不能关闭 Supersession。

### 11.12 Retrieval、Ranking 与显示

1. Retrieval 必须先授权后排名；
2. Ranking Score 只用于候选排序，不表示真实、有效或适用；
3. 检索必须固定 Query、Filter、Index、Embedding/Model、Policy 和时间；
4. 输出至少显示 Knowledge ID、Revision、Title、Source、Validity、Freshness、Classification 和限制；
5. 默认排除 Validity 为 Stale、Conflicted、Superseded、Withdrawn 或 Unknown 的 Knowledge，并排除使用 Prohibited Source 的 Knowledge；
6. 历史检索必须使用显式历史模式；
7. 结果为空时禁止自动放宽权限或引入未知 Source；
8. 结果冲突必须呈现冲突，不得由 Agent 静默合并；
9. 受限内容必须执行片段级过滤和最小披露；
10. 高风险自动动作必须固定 Context Manifest。

### 11.13 Access、Export 与最小披露

1. 访问必须基于身份、角色、用途、Scope、分类和时间；
2. 默认 Deny；权限不足返回 Denied，不返回敏感存在性细节；
3. Export、Bulk Retrieval、Cross-project Reuse 和 External Sharing 必须单独授权；
4. 输出必须继承 Source 和 Knowledge 的最严格分类；
5. 临时缓存不得降低访问控制；
6. 访问例外必须有申请人、理由、Scope、期限、批准人和审计；
7. 权限撤销必须使 Token、Cache、Index 和离线副本按规则失效；
8. RAP 不得授予超过 E02、合同或许可的权利；
9. Retrieval Log 必须避免记录不必要的 Secret、PII 和全文；
10. 最小披露不等于内容任意截断；截断后仍须保持语义和来源。

### 11.14 Agent Context 与 Memory

1. Agent Context 必须由 SCM 或等价 Context Manifest 固定；
2. Manifest 必须列出 Source Asset、Revision、Priority、Validity、Freshness、Sensitivity 和 Integrity；
3. Agent Long-term Memory 必须视为 Knowledge Store，适用 KAC、SPR、RAP、RTS 和 KFR；
4. 未经 Capture 的 Session Memory 禁止跨任务默认复用；
5. Agent 不得访问未授权历史会话；
6. Prompt Injection 或恶意 Source 风险由 E02 与 RAP 共同控制；
7. Agent 输出引用必须能回到 Source Revision；
8. Model Update、Embedding Update、Index Rebuild 或 Policy Change 后必须评估 Context 可重复性；
9. Token Budget 压缩不得删除关键限制、冲突和来源；
10. 禁止保存或要求 Agent 私有思维链。

### 11.15 Migration、Conversion 与 Recovery

1. 迁移前固定 Source/Target Inventory、Schema/Format Mapping、Tool、Version 和 Checksum；
2. 迁移必须默认可回滚或有批准的不可回滚边界；
3. 验证数量、Metadata、关系、权限、Retention、Integrity、Search 和 Rendering；
4. Sampling 不能替代关键 Record 的全量完整性验证；
5. 旧系统退役前必须验证 Target 可用和恢复；
6. Recovery Test 必须固定 Backup/Snapshot、时间点、环境和验收 Criteria；
7. 恢复成功不证明恢复内容为 Current，仍需 Validity/Freshness 检查；
8. 迁移/恢复失败必须记录缺口、影响和处置；
9. Source 系统关闭后保留必要的 Reader、Format Documentation 或 Conversion Path；
10. Migration Result 由独立 Reviewer 确认。

### 11.16 命令与工具控制

知识与记录工具命令必须包含：

| 控制项 | 最低要求 |
|---|---|
| Operation | search、capture、classify、index、export、migrate、archive、restore、hold、dispose 等明确动作 |
| Tool | Tool Name、Version、Digest、Plugin/Connector Revision |
| Target | Asset/Record/Category/Repository、Revision、Environment、Tenant、Partition |
| Input | Query、Manifest、Rule、Mapping、Policy 的受控引用 |
| Authority | Requester、Operator、Approval、Scope、有效期 |
| Mode | read-only、dry-run、write；默认 read-only/dry-run |
| Limits | Record/Byte/Token、Concurrency、Timeout、Rate、Cost |
| Output | Location、Classification、Redaction、Retention、Integrity |
| Safety | Preconditions、Stop Conditions、Snapshot、Transaction、Rollback |
| Evidence | Run ID、Command Hash、Log、Result、Reviewer |

强制规则：

1. 禁止依赖交互式默认值执行 Write、Export、Migration 或 Disposition；
2. 禁止使用 Latest、Head、All、通配 Environment 或未解析变量作为高风险 Target；
3. Secret 只能使用 Secret Reference，禁止写入命令文本、日志或模板；
4. Search/Export 必须限制输出量并应用 Redaction；
5. Index Rebuild 必须固定 Source Set 和 Revision；
6. Write 前必须 Dry-run；不能 Dry-run 时记录理由和替代验证；
7. 不可逆动作必须有双人 Review 和 Stop Conditions；
8. 命令 Exit Code 只表示进程结果，不表示治理 Result；
9. 每次命令绑定 C09 Agent Run/Execution Record 和 C05/E04 Evidence；
10. 失败重试不得扩大 Scope 或绕过限额。

### 11.17 Audit Log

1. 记录创建、Capture、Review、Approval、Access、Export、Change、Supersession、Migration、Hold、Disposition 和 Recovery 事件；
2. 日志必须有 Actor、Action、Target、Revision、Time、Result 和 Correlation ID；
3. 日志时间必须有统一时间源和时区；
4. 日志写入和读取权限分离；
5. 日志完整性机制与 Risk 相称；
6. 日志不得成为 Secret/PII 全文仓库；
7. 审计查询必须只读并记录查询自身；
8. 日志保留按 RCS/RTS，不得无限期默认保留；
9. 日志缺口必须进入 Risk/Incident；
10. Agent 生成日志不得由同一 Agent 自行判定完整。

### 11.18 Fail Closed 与恢复

以下情形必须 Fail Closed：

- Authority、Identity、Source、Revision 或 Classification Unknown；
- Knowledge Validity 为 Stale、Conflicted、Superseded、Withdrawn 或 Unknown 且请求为默认 Context；
- Legal Hold 状态 Unknown 或 Active；
- Disposition Scope 含未知副本；
- Migration Integrity 验证失败；
- Access Policy 加载失败；
- Index Revision 与 Source Manifest 不一致；
- Audit Log 无法写入且操作属于高风险；
- Tool Target 超出批准 Scope；
- Output Redaction 失败。

Fail Closed 后必须记录原因、影响、临时控制、Owner 和恢复条件。

## 12. 状态模型与转换

### 12.1 DOC State

KAC、VOC、SPR、RCS、RTS、KFR、SKR 和 RAP 使用公共 DOC State：

```text
DOC: Draft -> In Review -> Approved -> Baselined -> Superseded/Retired
                 -> Changes Required -> Draft
                 -> Rejected
```

Changes Required 和 Rejected 从 In Review 进入；具体允许转换、Authority 和 Evidence 以公共状态模型为准。禁止为 E04 产物新增 Released、Withdrawn 或其他平行 DOC State。

### 12.2 Knowledge Validity

```text
Unknown -> Current / Conditionally Current / Stale / Conflicted / Withdrawn
Current <-> Conditionally Current
Current / Conditionally Current / Stale / Conflicted -> Superseded / Withdrawn
Stale / Conflicted -> Current / Conditionally Current（完成复核或更正后）
```

规则：

1. Validity 是 KAC 成员属性，不是 DOC State；
2. Current 必须有 Source、Owner、Revision、Review 和 Freshness；
3. Conditionally Current 必须有条件、Scope、到期和 Action；
4. Stale/Conflicted 禁止默认检索；
5. Superseded 必须有 SKR 或明确新 Knowledge；
6. Withdrawn 必须有原因、有效时间和替代工作方式；
7. 任何状态可因 Evidence 失效回到 Unknown/Conflicted，但必须保留历史。

### 12.3 Freshness Result

```text
Not Evaluated -> Fresh / Due for Review / Stale / Conflicted
Fresh -> Due for Review / Stale / Conflicted
Due for Review -> Fresh / Stale / Conflicted
Stale / Conflicted -> Fresh（完成复核并满足原 Criteria 后）
```

Freshness Result 只对 KFR 固定 Scope、Revision 和检查时间有效。

### 12.4 Source Trust

Source Trust 由 SPR 成员记录：

```text
Unverified -> Verified / Corroborated / Authoritative / Disputed / Prohibited
Verified / Corroborated / Authoritative -> Disputed / Prohibited
Disputed -> Verified / Corroborated / Authoritative / Prohibited（取得新 Evidence 和复核后）
```

Authoritative 必须限定业务 Scope；不得把一个 Scope 的 Authority 外推到所有用途。Prohibited 解除必须有新的有权决定、Scope 和 Evidence，禁止由工具自动转换。

### 12.5 Member Status

KAC/VOC/SPR/RCS/RTS/SKR/RAP 成员使用：

```text
Proposed -> Active -> Deprecated -> Retired
Proposed -> Rejected
```

语义：

- Proposed：成员候选已登记，尚未生效；
- Active：成员在明确 Scope 和时间内生效；
- Deprecated：成员仍为历史或迁移输入，但禁止新增默认消费；
- Retired：成员退出活动集合，仅按保留规则保存；
- Rejected：成员候选未被接受，保留拒绝原因。

Member Status 与容器 DOC State、Knowledge Validity 和 Access Result 分离。Active 成员内容发生变化时必须创建容器新 Revision，禁止原位覆盖历史。

### 12.6 Record Authority 与结果状态

1. Record Authority 是评价结果，不改变 Record 容器状态；
2. Capture、Migration、Access、Disposition 和 Retrieval Fitness 各使用独立 Result；
3. Tool Success 禁止自动写入 Complete、Verified、Allowed、Completed 或 Fit；
4. Result 变化必须保留 Criteria、Evidence 和 Evaluator；
5. Invalidated Evidence 必须触发受影响结果复评。

### 12.7 状态转换最低字段

每次转换必须记录：

- Object ID/Revision；
- Previous Value；
- New Value；
- Trigger；
- Criteria；
- Evidence；
- Requested By；
- Approved By；
- Effective Time；
- Expiry/Review Time；
- Affected Context/Consumer；
- History Reference。

## 13. 正式产物最低内容

### 13.1 通用结构

除 VC-PPG-COM-002 第 3 章和第 3.1 节外，每类正式产物还必须包含适用的类型专属成员、记录完整性要求、Review/Exception/Change 引用、Verification/Evidence 引用和标准映射。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义。

### 13.2 KAC Knowledge Asset Catalog

KAC 每个成员至少包含：

- Knowledge ID；
- Knowledge Type；
- Name；
- Purpose/Intended Use；
- Source IDs；
- Owner；
- Current Revision；
- Knowledge Validity；
- Applicable Scope；
- Consumers；
- Access Classification；
- RAP Rule；
- Retention Rule；
- Freshness Rule；
- Last/Next Review；
- Integrity Reference；
- Replacement/Supersession；
- Trace Links；
- Member Status；
- History Reference。

### 13.3 VOC Controlled Vocabulary

VOC 每个成员至少包含：

- Term ID；
- Term；
- Formal Name；
- Definition；
- Exclusions；
- Prohibited Synonyms；
- Allowed Abbreviation；
- Applicable Scope；
- Source；
- Owner；
- Approved Revision；
- Effective Time；
- Replacement Term；
- Consumers；
- Member Status；
- History Reference。

### 13.4 SPR Source and Provenance Register

SPR 每个成员至少包含：

- Source ID；
- Source Entity；
- Source Type；
- Acquisition Method；
- Acquisition Time；
- Source Revision/Date；
- Locator；
- Source Trust；
- Trust Criteria/Evaluator；
- License or Use Restriction；
- Security/Privacy Classification；
- Related Knowledge IDs；
- Transformation/Tool/Run；
- Integrity Reference；
- Availability/Preservation；
- Member Status；
- History Reference。

### 13.5 RCS Record Classification Scheme

RCS 每个成员至少包含：

- Record Category ID；
- Record Category；
- Business Purpose/Function；
- Included/Excluded Records；
- Sensitivity；
- Authenticity Criteria；
- Reliability Criteria；
- Integrity Requirement；
- Useability Requirement；
- Owner；
- Retention Rule ID；
- Allowed Access Roles；
- Capture Requirement；
- Metadata Requirement；
- Storage/Format Requirement；
- Disposition Method；
- Review Cycle；
- Member Status；
- History Reference。

### 13.6 RTS Retention Schedule

RTS 每个成员至少包含：

- Retention Rule ID；
- Record Category；
- Trigger Event；
- Trigger Evidence；
- Retention Period；
- Legal/Regulatory/Contract/Business Basis；
- Archive Location；
- Format/Readability Requirement；
- Legal Hold Check；
- Disposition Method；
- Disposition Authority；
- Backup/Replica/Cache Coverage；
- Exception；
- Review Cycle；
- Last/Next Review；
- Member Status；
- History Reference。

### 13.7 KFR Knowledge Freshness Report

KFR 至少包含：

- Report ID；
- Scope；
- Check Time；
- Criteria/Rule Revision；
- Knowledge ID/Revision；
- Last Review Time；
- Source/Dependency Changes；
- Conflict Check；
- Freshness Result；
- Knowledge Validity Recommendation；
- Stale/Conflicted Items；
- Consumer/Context Impact；
- Action；
- Owner；
- Due Date；
- Reviewer；
- Evidence；
- Follow-up Result。

### 13.8 SKR Superseded Knowledge Register

SKR 每个成员至少包含：

- Supersession ID；
- Old Knowledge ID/Revision；
- New Knowledge ID/Revision；
- Relation Type；
- Reason；
- Decision/Change Reference；
- Effective Time；
- Affected Context/Consumer；
- Migration Actions；
- Index/Cache/Embedding Action；
- Verification；
- Retention Location/Rule；
- Owner；
- Member Status；
- History Reference。

### 13.9 RAP Retrieval and Access Policy

RAP 每个成员至少包含：

- Policy Rule ID；
- Knowledge/Record Classification；
- Allowed Roles/Identities；
- Allowed Purpose；
- Retrieval Scope；
- Minimum Disclosure；
- Source/Revision/Freshness Display；
- Sensitive Filtering/Redaction；
- Query/Result Logging；
- Export/Bulk Access Rule；
- Denial Behavior；
- Exception Process；
- Time/Environment/Tenant Constraints；
- Cache/Offline Copy Rule；
- Review Cycle；
- Owner；
- Member Status；
- History Reference。

## 14. 质量要求

### 14.1 总体质量

E04 实例必须满足：

- Complete：必填字段、Source、Owner、Revision、Access、Retention 和关系完整；
- Correct：内容与 Source、Scope、Criteria 和 Evidence 一致；
- Consistent：术语、状态、ID、Revision、关系和时间无冲突；
- Current：适用 Freshness 规则已执行；
- Traceable：可正向和反向查询 Source、Change、Context、Run、Output 和 Consumer；
- Controlled：Authority、Access、Retention、Change、Disposition 和 History 受控；
- Recoverable：适用 Record 和 Baseline 可按 Criteria 恢复；
- Usable：可定位、检索、呈现、理解和复核。

### 14.2 Formal Knowledge 质量

1. 100% KAC 成员有 Source、Owner、Revision、Validity、Access、Retention 和 Freshness；
2. 默认 Context 中 Validity 为 Stale、Conflicted、Superseded、Withdrawn 或 Unknown 的成员为 0，使用 Prohibited Source 的成员为 0；
3. 高风险知识 100% 有独立 Reviewer；
4. 未知 Source/Use Restriction 的知识 0 个默认发布；
5. Supersession 100% 有新旧关系和 Consumer 迁移；
6. Formal Knowledge 0 个以 Chat 链接作为唯一正文。

### 14.3 Record 质量

1. 100% Record 映射 RCS Category 和 RTS Rule；
2. 关键 Record 的 Authenticity、Reliability、Integrity、Useability 100% 已评价；
3. 未分类 Record 0 个进入长期受控存储；
4. 处置候选 100% 完成 Legal Hold 检查；
5. 不可逆处置 100% 有 Authority、Dry-run、范围验证和 Evidence；
6. Migration 关键记录丢失数为 0。

### 14.4 Retrieval 质量

1. 100% Retrieval Result 显示 Source、Revision、Validity、Freshness 和 Classification；
2. 100% 高风险 Agent Run 固定 Context Manifest；
3. 未授权检索结果泄露数为 0；
4. Policy/Index/Source Revision 不一致时 100% Fail Closed；
5. 冲突知识静默合并数为 0；
6. 历史知识误入默认 Context 数为 0。

### 14.5 质量判定规则

1. 单项关键控制 Fail 时总体不得判 Pass；
2. Unknown 不得计入 Pass 分母的已满足数；
3. 采样结果必须记录 Population、Sample、Method、Seed 和 Limitation；
4. Tool Success 不等于 Governance Pass；
5. 零告警不证明零缺口；
6. 指标目标必须有业务依据和 Owner；
7. 质量结论必须固定时间范围和 Revision；
8. Dashboard 只展示结果，不替代 Evidence。

## 15. 验证、评审与 Gate

### 15.1 Verification 层级

| 层级 | 验证对象 | 最低验证 |
|---|---|---|
| V1 | Schema/Format | 必填字段、类型、枚举、引用和语法 |
| V2 | Content | Source、定义、Criteria、限制和一致性 |
| V3 | Relationship | Trace 方向、Revision、孤立和影响查询 |
| V4 | Control | Access、Retention、Hold、Change、Disposition 和 Audit |
| V5 | Operation | Retrieval、Capture、Migration、Recovery、Index 和命令 |
| V6 | Outcome | 默认 Context、历史恢复、错误传播和 Consumer 影响 |

### 15.2 最低评审

1. KAC：Knowledge Owner + Reviewer；
2. VOC：Vocabulary Owner + 主要 Consumer；
3. SPR：Source Steward + Access/License Authority；
4. RCS：Records Manager + Business Owner + E02 Reviewer；
5. RTS：Records Manager + Disposition Authority + 适用 Legal/Compliance；
6. KFR：Knowledge Owner 之外的 Reviewer；
7. SKR：Knowledge Owner + Configuration Manager + Consumer Representative；
8. RAP：Access Authority + E02 Reviewer + System Owner；
9. 高风险 Agent Context：Human Authority + Domain Reviewer。

### 15.3 Gate 输入

适用 Gate 至少输入：

- Applicability Decision；
- 八类适用产物的固定 Revision；
- 未关闭 Source/Validity/Access/Retention Unknown；
- KFR 结果；
- Supersession 和迁移状态；
- Access 测试；
- Recovery/Migration 测试；
- Audit 缺口；
- EWR/RAR；
- C05 Evidence；
- C10 Impact Query；
- C11 Baseline；
- E02/E03/E05 接口结果。

### 15.4 阻断条件

以下任一成立必须阻断相关发布、自动动作或处置：

- 默认 Context 包含 Stale、Conflicted、Superseded、Withdrawn 或 Unknown Knowledge；
- Source/License/Access/Retention/Legal Hold Unknown；
- 高风险 Knowledge 无人类 Review；
- Record 未分类或无 RTS；
- 不可逆处置无 Authority；
- Migration Integrity Fail；
- Retrieval 绕过 RAP；
- Supersession 后旧知识仍默认返回；
- 关键 Audit Log 缺失；
- Evidence 已失效；
- Agent 尝试自批。

### 15.5 Acceptance 边界

1. E04 Verification Pass 不表示产品已满足用户需求；
2. KFR Fresh 不表示 Requirement、Model 或 Product 正确；
3. Record Authoritative 不表示其内容在所有 Scope 为真；
4. Retrieval Fit 不表示输出已被业务批准；
5. Gate Decision 只能由 C12 有权角色作出；
6. Agent 和工具只能提交候选结论与 Evidence。

## 16. 追踪、审计与记录

### 16.1 必须追踪

至少必须追踪：

- Knowledge -> Source；
- Knowledge -> Owner；
- Knowledge -> Revision/Baseline；
- Knowledge -> Requirement/Decision/Design；
- Knowledge -> Context/Agent Run/Output；
- Knowledge -> Freshness Report；
- Knowledge -> Supersession；
- Record -> Category；
- Record -> Retention Rule；
- Record -> Access；
- Record -> Migration/Disposition；
- Result -> Criteria/Evidence/Reviewer；
- Policy -> Implementation/Verification。

### 16.2 审计事件

必须记录：

- Create/Receive；
- Capture/Classify；
- Review/Approve/Release；
- Retrieve/View/Export；
- Change/Supersede/Withdraw；
- Hold/Release Hold；
- Archive/Transfer/Migrate/Convert；
- Restore；
- Dispose；
- Access Grant/Revoke/Exception；
- Policy/Rule/Index Update；
- Audit/Corrective Action。

### 16.3 审计记录字段

每个事件至少包含：

- Event ID；
- Actor/Identity；
- Role/Authority；
- Operation；
- Target ID/Revision；
- Source/Target Environment；
- Timestamp/Timezone；
- Request/Run/Correlation ID；
- Policy/Rule Revision；
- Before/After Reference；
- Result；
- Error/Stop；
- Evidence Location；
- Access Classification；
- Retention Rule。

### 16.4 指标

| 指标 | 计算边界 | 禁止推论 |
|---|---|---|
| Catalog Coverage | 有 KAC 成员的 Formal Knowledge / 应登记 Knowledge | 不证明内容正确 |
| Source Coverage | 有有效 SPR Source 的 Knowledge / KAC 成员 | 不证明使用合法 |
| Current Coverage | Current 且 Fresh 的可用 Knowledge / 应可用 Knowledge | 不证明无冲突 |
| Freshness Overdue Rate | 逾期未复核 / 到期应复核 | 不证明未逾期项正确 |
| Supersession Leakage | 被替代知识仍进入默认 Context 的次数 | 零不证明历史完整 |
| Record Classification Coverage | 有 RCS/RTS 的 Record / 应治理 Record | 不证明处置正确 |
| Access Denial Accuracy | 经复核正确拒绝 / 抽样拒绝 | 不证明无泄露 |
| Retrieval Provenance Coverage | 带 Source/Revision/Freshness 的结果 / 抽样结果 | 不证明检索相关 |
| Migration Integrity Failure | 迁移验证失败的关键对象数 | 零不证明全量可用 |
| Disposition Exception Rate | 例外处置 / 到期候选 | 不评价法律充分性 |
| Recovery Success Rate | 按 Criteria 成功恢复 / 已执行恢复测试 | 不证明内容 Current |

### 16.5 Evidence 失效

1. Source 被撤回、Revision 变化、Integrity 失败或 Criteria 变化时 Evidence 可以失效；
2. 失效 Evidence 必须标记并查询受影响 Knowledge、Result、Decision 和 Gate；
3. 禁止删除原 Evidence 以隐藏失效；
4. 受影响 Current Knowledge 必须复评；
5. 失效范围不明时进入 Conflicted/Unknown 并 Fail Closed。

## 17. 裁剪、激活、停用与退役

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。E04 的 Active、Conditionally Active、Retiring、Retired、Inactive、Pending、Not Evaluated 必须按统一状态语义解析；Trigger、Unknown 或冲突不得被局部规则降级。

### 17.0 Task Profile 驱动的激活

E04 在正式知识资产、记录分类、来源/版本/新鲜度、保留/处置、Legal Hold、检索权限或受监管记录发生变化时激活。普通临时执行上下文不因此自动激活 E04，但必须遵守 C08 的来源和失效规则。

KAC、VOC、SPR、RCS、RTS、RAP 已有有效 Baseline 时 `Reference`；KFR 按新鲜度检查需要 `Generate`；SKR 只在知识被替代时更新。禁止为同一术语、来源或保留规则建立平行定义。

### 17.1 P2 裁剪规则

P2 不允许删除：

- E04 Applicability Decision；
- 八类正式产物定义和模板；
- Source/Owner/Revision/Validity/Access/Retention/Freshness；
- Record Classification 和 Disposition；
- Formal Knowledge 与 Temporary Context 分离；
- Supersession 历史和默认检索排除；
- Retrieval Source/Freshness 显示；
- Agent Authority Boundary；
- 命令 Dry-run、Stop、Rollback 和 Evidence；
- 国际标准映射。

### 17.2 可裁剪实现

满足风险和 Evidence 要求时可以：

- 用 Markdown/Git 实现 KAC、VOC、SPR、RCS、RTS、KFR、SKR、RAP；
- 用同一受控 Repository 存放八类产物；
- 以表格代替专用知识管理平台；
- 使用人工 Freshness Review；
- 使用文件 Hash 和 Git History 作为部分 Integrity Evidence；
- 对低风险知识使用简化独立 Review；
- 不使用向量检索，仅使用结构化或全文检索。

裁剪不得改变产物身份、最低字段、状态轴、关系和 Authority。

### 17.3 激活

1. 当前仓库依据 VC-PPG-DEC-001 已 Active；
2. 新目标产品任一触发条件 Yes 即激活；
3. 激活必须确定 Scope、Effective Time、Owner、产物实例和 Gate；
4. 从 Pending 转 Active 必须关闭关键 Unknown；
5. Activation Decision 纳入 C11 Baseline；
6. 激活不是 DOC Approval。

### 17.4 条件激活

Conditionally Active 必须记录：

- 限定 Scope；
- 未完成项；
- 临时控制；
- 禁止动作；
- Owner；
- Due Date；
- Expiry；
- Review Trigger；
- Exit Criteria。

到期未完成时不得自动延长。

### 17.5 停用与退役

1. 当前 E04 激活状态变化必须建立 C11 Change Request；
2. Retiring 期间继续维护访问、保留、Legal Hold、迁移、替代、恢复和审计；
3. 所有活跃 Consumer 必须迁移或批准关闭；
4. 默认 Context、Index、Cache 和 Agent Memory 必须移除退役知识；
5. 历史 Record 按 RTS 保留；
6. 系统退役前必须验证 Export/Archive/Reader/Recovery；
7. Retired 不表示允许删除历史；
8. 重新激活必须重做 Applicability、Freshness、Access 和 Integrity 检查。

## 18. 与其他规范接口

### 18.1 C01 至 C03

1. C01 Evidence Register 可作为 E04 Record，仍由 C05 判定充分性；
2. Product/Scope/PRD/Feature Knowledge 进入 KAC 时引用原资产，不复制替代；
3. C02 Risk、Metric 和 Dependency 的 Source/Freshness 受 E04 管理；
4. 风险知识过期必须触发 C02 复评；
5. Product Context 的默认知识集合必须固定 Revision。

### 18.2 C04 至 C06

1. Requirement、Acceptance、UX 和 Technical Design 可以登记为 Knowledge/Record；
2. KAC 不替代 REQ/AC/TDS 正文；
3. VOC 术语变化必须查询 Requirement、Design 和 Test；
4. Knowledge Freshness Fail 可使相关 Verification Evidence 失效；
5. C05 管理证据充分性，E04 管理 Evidence 的记录、来源、访问和保留。

### 18.3 C07 至 C09

1. C07 决定 Human/Agent Authority；
2. C08 SCM 固定 Context 成员，E04 决定成员知识有效性和检索资格；
3. C09 记录 Agent Run、Command、Input、Output 和 Evidence；
4. E04 禁止未经 Capture 的会话记忆跨任务默认复用；
5. Retrieval/Context Manifest 必须绑定 Agent Run；
6. Agent 不得自批 KFR、SKR、RAP Exception 或 Disposition。

### 18.4 C10 至 C12

1. C10 提供受控关系、双向追踪、影响查询和 Orphan 检查；
2. E04 使用 `derives-from`、`depends-on`、`affected-by`、`supersedes`、`replaces`、`generated-by` 和 `observed-from`；
3. C11 管理 Revision、Snapshot、Baseline、Change、Release 和恢复配置；
4. E04 KAC/SKR 不替代 C11；
5. C12 管理 Review、Gate、Waiver 和 Risk Acceptance；
6. E04 阻断条件进入 C12 Gate；
7. Evidence 失效必须反向查询既有 Gate。

### 18.5 E01、E02、E03 与 E05

1. E01 Architecture Model/Decision/Conformance 作为 Knowledge/Record 时适用 E04；
2. E02 决定 Security、Privacy、PII、Compliance、License、Access Risk 和 Legal Authority；
3. E04 RAP 执行但不扩大 E02 权限；
4. E03 管理 Dataset/Corpus、Data Provenance、Lineage 和数据处置规则；
5. E04 管理 Corpus 相关文档知识、正式记录、访问、知识新鲜度和 Supersession；
6. E03 RDR 与 E04 RTS 同时适用时采用更严格规则并保留决定；
7. E05 Incident、Service Review、Runbook 和 Operational Record 进入 E04；
8. Incident 发现错误知识时触发 KFR/SKR/Context 影响查询；
9. E05 负责恢复运行，E04 验证恢复记录和知识的可用性与当前性。

## 19. 参考标准治理

### 19.1 参考层级

| 层级 | 标准 | E04 用途 |
|---|---|---|
| R1 | ISO 15489-1:2016 | Records 原则、权威属性、Metadata、分类、访问、保留和处置过程 |
| R1 | ISO 10007:2017 | Configuration 责任、识别、Baseline、Change、Status Accounting 和 Audit |
| R1 | ISO/IEC 27001:2022 + Amd 1:2024 | Risk、角色、Documented Information、Access、Operation、Audit 和 Improvement |
| R1 | ISO/IEC 42001:2023 | AI Management、Documented Information、AI Resources、Provenance、Context、Logs 和 Responsible Use |

### 19.2 版本固定

1. 所有标准引用固定编号和年份；
2. ISO 15489-1 固定 2016 Edition 2；
3. ISO 10007 固定 2017 Edition 3；
4. ISO 10007:2017 当前处于待修订状态，ISO/WD 10007 不作为规范依据；
5. ISO/IEC 27001 固定 2022 Edition 3，并记录 Amd 1:2024；
6. ISO/IEC 42001 固定 2023 Edition 1；
7. 标准产品页状态、Amendment、Correction 和新 Edition 必须周期核验；
8. 标准年份不得使用“最新版”替代。

### 19.3 标准变化

出现以下变化必须建立 C11 Change：

- 新 Edition 发布；
- Amendment/Correction 发布或撤销；
- 标准状态变为 Withdrawn/Replaced；
- 公开条款结构变化影响现有映射；
- 法律、监管、合同要求采用不同版本；
- 工具或控制声称的符合性范围变化。

Change 必须分析术语、产物、字段、State、Process、Command、Template、Gate、Evidence、Training 和历史 Baseline。

### 19.4 版权与符合性边界

1. 本规范只引用 ISO 官方产品页和公开目录可确认的条款主题；
2. 本规范不复制受版权保护的标准全文；
3. 工程化 ID、字段、状态、阈值、模板、命令和 Gate 是本项目控制；
4. 未获得标准全文和正式符合性评估时，禁止声明完整符合；
5. 官方产品页用于标准身份和生命周期核验，不替代标准授权文本；
6. 国际标准不能替代适用法律、监管、合同或有权法律意见。

## 20. 模板、检查清单与国际标准条例映射

### 20.1 Extension Applicability Decision 骨架

```yaml
decision_id:
product_scope_revision:
decision_owner:
evaluation_time:
triggers:
  multi_agent_session_long_term:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  cross_project_reuse:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  audit_evidence_history_recovery:
    result: Yes|No|Unknown|Not Applicable
    evidence:
  growing_decision_context:
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

### 20.2 KAC 骨架

```yaml
asset_id:
artifact_type: Knowledge Asset Catalog
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
  - knowledge_id:
    knowledge_type:
    name:
    purpose_intended_use:
    source_ids:
    knowledge_owner:
    knowledge_revision:
    knowledge_validity: Current|Conditionally Current|Stale|Conflicted|Superseded|Withdrawn|Unknown
    knowledge_scope:
    consumers:
    knowledge_access:
    rap_rule:
    knowledge_retention:
    freshness_rule:
    last_review:
    next_review:
    integrity_reference:
    replacement_supersession:
    member_trace_links:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.3 VOC 骨架

```yaml
asset_id:
artifact_type: Controlled Vocabulary
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
  - term_id:
    term:
    formal_name:
    definition:
    exclusions:
    prohibited_synonyms:
    allowed_abbreviation:
    term_scope:
    term_source:
    term_owner:
    approved_revision:
    effective_time:
    replacement_term:
    consumers:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.4 SPR 骨架

```yaml
asset_id:
artifact_type: Source and Provenance Register
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
  - source_id:
    source_entity:
    source_type:
    acquisition_method:
    acquisition_time:
    source_revision_date:
    locator:
    source_trust: Authoritative|Verified|Corroborated|Unverified|Disputed|Prohibited
    trust_criteria_evaluator:
    license_use_restriction:
    security_privacy_classification:
    related_knowledge_ids:
    transformation_tool_run:
    integrity_reference:
    availability_preservation:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.5 RCS 骨架

```yaml
asset_id:
artifact_type: Record Classification Scheme
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
  - record_category_id:
    record_category:
    business_purpose_function:
    included_records:
    excluded_records:
    sensitivity:
    authenticity_criteria:
    reliability_criteria:
    integrity_requirement:
    useability_requirement:
    category_owner:
    retention_rule_id:
    allowed_access_roles:
    capture_requirement:
    metadata_requirement:
    storage_format_requirement:
    disposition_method:
    review_cycle:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.6 RTS 骨架

```yaml
asset_id:
artifact_type: Retention Schedule
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
  - retention_rule_id:
    record_category:
    trigger_event:
    trigger_evidence:
    retention_period:
    basis:
    archive_location:
    format_readability_requirement:
    legal_hold_check:
    disposition_method:
    approver:
    disposition_authority:
    copy_coverage:
    exception:
    review_cycle:
    last_review:
    next_review:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.7 KFR 骨架

```yaml
asset_id:
artifact_type: Knowledge Freshness Report
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
report_id:
check_scope:
check_time:
criteria_rule_revision:
evaluations:
  - knowledge_id_revision:
    last_review_time:
    source_dependency_changes:
    conflict_check:
    freshness_result: Fresh|Due for Review|Stale|Conflicted|Not Evaluated
    validity_recommendation:
    stale_conflicted_items:
    consumer_context_impact:
    action:
    action_owner:
    due_date:
    reviewer:
    evidence:
    follow_up_result:
```

### 20.8 SKR 骨架

```yaml
asset_id:
artifact_type: Superseded Knowledge Register
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
  - supersession_id:
    old_knowledge_id_revision:
    new_knowledge_id_revision:
    relation_type: supersedes|replaces
    reason:
    decision_change_reference:
    effective_time:
    affected_context_consumer:
    migration_actions:
    index_cache_embedding_action:
    verification:
    retention_location_rule:
    supersession_owner:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.9 RAP 骨架

```yaml
asset_id:
artifact_type: Retrieval and Access Policy
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
  - policy_rule_id:
    knowledge_record_classification:
    allowed_roles_identities:
    allowed_purpose:
    retrieval_scope:
    minimum_disclosure:
    source_revision_freshness_display:
    sensitive_filtering_redaction:
    query_result_logging:
    export_bulk_access_rule:
    denial_behavior:
    exception_process:
    time_environment_tenant_constraints:
    cache_offline_copy_rule:
    review_cycle:
    rule_owner:
    member_status: Proposed|Active|Deprecated|Retired|Rejected
    member_history_reference:
```

### 20.10 Knowledge and Records Command Control 骨架

```yaml
command_id:
operation:
tool_name_version_digest:
plugin_connector_revision:
target:
  asset_record_category:
  revision:
  environment:
  tenant:
  partition:
input_references:
requester_operator:
authority_approval:
mode: read-only|dry-run|write
limits:
  records_bytes_tokens:
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
evidence:
reviewer:
```

### 20.11 Retrieval Result 与 Context Manifest 骨架

```yaml
retrieval_id:
query_purpose:
requester_agent_role:
scope:
retrieval_time:
rap_revision:
index_revision:
embedding_model_revision:
candidates:
  - knowledge_id:
    revision:
    source:
    validity:
    freshness:
    classification:
    score:
    filter_result:
    filter_reason:
selected_context:
  manifest_id:
  members:
  token_byte_budget:
  redactions:
  conflicts:
  expiry:
retrieval_fitness:
limitations:
agent_run:
evidence:
```

### 20.12 P2 生产检查清单

- [ ] E04 Applicability 在 Discovery Ready 前完成；
- [ ] 四项触发条件逐项有 Result 和 Evidence；
- [ ] 当前仓库状态为 Active；
- [ ] 激活状态变化引用 C11 Change Request；
- [ ] 编制适用性、Activation Status 和 DOC State 分离；
- [ ] 八类正式产物身份未合并；
- [ ] 八类产物均使用 DOC State；
- [ ] 通用必填字段完整；
- [ ] 容器 State 与成员状态分离；
- [ ] Knowledge Validity 与 DOC State 分离；
- [ ] Freshness/Access/Capture/Migration/Disposition Result 与 State 分离；
- [ ] Knowledge ID、Revision、Git Hash 和 Baseline 分离；
- [ ] Formal Knowledge 与 Temporary Context 分离；
- [ ] Chat/Prompt/Session Summary 未直接作为正式事实源；
- [ ] Agent 私有思维链未保存；
- [ ] Agent Generated 内容标记 generated-by；
- [ ] KAC 100% 有 Source、Owner、Revision 和 Validity；
- [ ] KAC 100% 有 Access、Retention 和 Freshness；
- [ ] KAC 无重复 Knowledge ID；
- [ ] Current Revision 唯一；
- [ ] Unknown Source 未进入默认 Context；
- [ ] Source 全部进入 SPR；
- [ ] SPR Acquisition、Time、Revision 和 Locator 完整；
- [ ] Source Trust 有 Criteria/Evaluator；
- [ ] License/Use Restriction 已记录；
- [ ] 可访问未被推导为可授权使用；
- [ ] Derived Knowledge 有关键 Source 和 Transformation；
- [ ] VOC 正式术语唯一；
- [ ] VOC 定义、Scope 和 Exclusion 完整；
- [ ] 禁止同义词可扫描；
- [ ] 上位公共术语未重定义；
- [ ] 替代术语保留历史和 Consumer 迁移；
- [ ] Record 100% 映射 RCS；
- [ ] RCS 按业务功能/用途分类；
- [ ] Sensitivity、Integrity、Access 和 Owner 完整；
- [ ] Authenticity Criteria 完整；
- [ ] Reliability Criteria 完整；
- [ ] Integrity Requirement 完整；
- [ ] Useability Requirement 完整；
- [ ] Record 100% 映射 RTS；
- [ ] RTS Trigger Event 可验证；
- [ ] Retention Period 有依据；
- [ ] “永久”保留有依据和周期复核；
- [ ] Archive Location 和 Format Readability 完整；
- [ ] Legal Hold 检查完整；
- [ ] Disposition Method 和 Authority 完整；
- [ ] Backup/Replica/Cache/Export/Index 在处置范围；
- [ ] 到期未自动等同删除；
- [ ] KFR 固定 Knowledge Revision 和 Criteria；
- [ ] KFR 同时执行时间和事件检查；
- [ ] Source/Dependency/Conflict 已检查；
- [ ] Freshness Result 有 Consumer Impact；
- [ ] Stale/Conflicted 有 Action、Owner 和 Due；
- [ ] Fresh 未被推导为内容绝对正确；
- [ ] SKR 新旧 Knowledge 和 Relation 完整；
- [ ] supersedes/replaces 方向正确；
- [ ] 被替代知识保留历史；
- [ ] 被替代知识未进入默认 Context；
- [ ] Index/Cache/Embedding 已更新或失效；
- [ ] Context/Consumer 迁移已验证；
- [ ] RAP Classification 与 Allowed Role 完整；
- [ ] Identity、Purpose、Scope 和时间受控；
- [ ] 默认 Deny；
- [ ] 最小披露和敏感过滤完整；
- [ ] Source/Revision/Freshness 显示完整；
- [ ] Query/Result Log 有保留规则；
- [ ] Export/Bulk/Cross-project Access 单独授权；
- [ ] 例外有 Scope、期限、批准和审计；
- [ ] Retrieval 先授权后排名；
- [ ] Ranking Score 未被推导为真实或 Current；
- [ ] 默认过滤 Stale/Conflicted/Superseded/Withdrawn/Unknown；
- [ ] 历史查询显式标记历史模式；
- [ ] 空结果未自动放宽权限；
- [ ] 冲突未被 Agent 静默合并；
- [ ] Retrieval Result 带 Source、Revision、Validity、Freshness、Classification；
- [ ] 高风险 Agent Run 固定 Context Manifest；
- [ ] Context Manifest 有成员 Revision 和到期；
- [ ] Token/Byte/Record Budget 完整；
- [ ] Access 撤销覆盖 Token/Cache/Offline Copy；
- [ ] Capture 同时登记 Metadata、RCS、RAP 和 RTS；
- [ ] Capture Partial/Failed 未进入默认检索；
- [ ] Migration 固定 Source/Target、Mapping、Tool 和 Checksum；
- [ ] Migration 验证 Metadata、关系、权限、Retention 和 Search；
- [ ] Recovery 验证固定 Snapshot 和 Criteria；
- [ ] Recovery Success 未被推导为内容 Current；
- [ ] Command 固定 Operation、Tool、Version 和 Digest；
- [ ] Target 固定 Asset/Revision/Environment/Tenant/Partition；
- [ ] 高风险 Target 不使用 Latest/All/未解析变量；
- [ ] 参数来自受控引用；
- [ ] Secret 只使用 Reference；
- [ ] 默认 Read-only/Dry-run；
- [ ] Write/Export/Migration/Disposition 单独授权；
- [ ] Resource Limits 完整；
- [ ] Output Classification/Redaction/Retention 完整；
- [ ] Stop/Snapshot/Transaction/Rollback 完整；
- [ ] Exit Code 未自动写治理 Pass；
- [ ] C09 Run 和 C05/E04 Evidence 已绑定；
- [ ] Audit Log 有 Actor、Action、Target、Revision、Time 和 Correlation；
- [ ] 日志不保存不必要 Secret/PII 全文；
- [ ] Audit Query 只读；
- [ ] Critical Fail Closed 条件完整；
- [ ] Evidence 失效已反向查询；
- [ ] C01 至 C12 接口完整；
- [ ] E01/E02/E03/E05 接口完整；
- [ ] ISO 10007 待修订状态受监测；
- [ ] ISO/IEC 27001 Amd 1:2024 已记录；
- [ ] 标准版本变化进入 C11；
- [ ] 历史 Baseline 和 Evidence 未重写；
- [ ] 文末国际标准条例映射完整。

### 20.13 反例

反例 1：

> 这段聊天大家一直在引用，所以已经是正式知识。

不符合：

- 使用频率不构成 Capture、Review 或 Approval；
- 无 Source、Owner、Revision、Validity、Access 和 Retention；
- 必须提炼为受控产物并登记 KAC/SPR。

反例 2：

> 检索分数最高，因此该内容是真实且最新的。

不符合：

- Ranking Score 只表示算法排序；
- 未检查 Source Trust、Knowledge Validity 和 Freshness；
- 未检查同 Scope 冲突和访问限制。

反例 3：

> 新规范已发布，可以删除旧规范。

不符合：

- Superseded Knowledge 必须保留历史和血缘；
- 未建立 SKR、Consumer 迁移和 RTS；
- 旧内容只是不再进入默认 Context。

反例 4：

> Git 中有 Commit，所以文档已经批准并形成 Baseline。

不符合：

- Commit 只定位实现状态；
- Approval 需要有权决定；
- Baseline 必须由 C11 固定成员 Revision 和恢复方式。

反例 5：

> 保留期已到，脚本返回成功，因此处置合规完成。

不符合：

- 到期只触发处置评审；
- 未检查 Legal Hold、Authority、所有副本和失败残留；
- Exit Code 不等于 Disposition Result。

反例 6：

> Agent 已自动总结多个来源并批准为 Current。

不符合：

- Agent 可以生成候选总结，不能批准 Validity；
- Source 冲突、许可、访问和 Freshness 未由有权角色复核；
- 高风险知识必须有人类 Reviewer。

反例 7：

> 恢复测试成功，所以恢复出的知识可以直接用于当前决策。

不符合：

- Recovery Success 只证明恢复 Criteria；
- 恢复内容仍可处于 Stale、Conflicted 或 Superseded；
- 必须重新执行 KFR 和 Context 过滤。

### 20.14 标准复评清单

- [ ] ISO 15489-1:2016 产品页状态未变化；
- [ ] ISO 15489-1 新 Edition/Amendment/Correction 已检查；
- [ ] ISO 10007:2017 仍是发布版；
- [ ] ISO 10007 生命周期状态已复核；
- [ ] ISO/WD 10007 未被当作正式依据；
- [ ] ISO 10007 新 Edition 发布情况已检查；
- [ ] ISO/IEC 27001:2022 产品页状态未变化；
- [ ] ISO/IEC 27001:2022/Amd 1:2024 已纳入；
- [ ] ISO/IEC 27001 新 Amendment/Correction 已检查；
- [ ] ISO/IEC 42001:2023 产品页状态未变化；
- [ ] ISO/IEC 42001 新 Amendment/Correction 已检查；
- [ ] Record、Configuration、Access 和 AI Context 映射未冲突；
- [ ] KAC/RCS/RTS/RAP 实现仍覆盖标准主题；
- [ ] 标准变化已进入 C11 Change；
- [ ] 历史 Baseline、Mapping 和 Evidence 未被重写。

### 20.15 国际标准条例映射

以下映射依据 ISO 官方产品页和公开预览目录。项目产物代码、状态值、触发规则、命令字段、模板和 Gate 是本项目工程化控制，不表示国际标准逐字规定。未取得标准全文授权时，不据此声明完整符合性。

| 国际标准及条款 | 条款或公开主题 | 本规范落实位置 |
|---|---|---|
| ISO 15489-1:2016 第 4 章 | Principles for Managing Records | 2、9、11.4、14.3 |
| ISO 15489-1:2016 5.2.1 | Records 概述 | 6、9.3–9.4、10.4 |
| ISO 15489-1:2016 5.2.2.1 | Authenticity | 6、11.4、13.5、14.3 |
| ISO 15489-1:2016 5.2.2.2 | Reliability | 6、11.4、13.5、14.3 |
| ISO 15489-1:2016 5.2.2.3 | Integrity | 6、11.4、11.15、13.5 |
| ISO 15489-1:2016 5.2.2.4 | Useability | 6、11.4、11.15、14.1 |
| ISO 15489-1:2016 5.2.3 | Metadata for Records | 6、11.5、13.5 |
| ISO 15489-1:2016 5.3.1–5.3.2 | Records Systems and Characteristics | 9、11.15、11.17、14 |
| ISO 15489-1:2016 6.2 | Policies | 8、11.7–11.8、13.5–13.9 |
| ISO 15489-1:2016 6.3 | Responsibilities | 7 |
| ISO 15489-1:2016 6.4 | Monitoring and Evaluation | 9.9、15、16 |
| ISO 15489-1:2016 6.5 | Competence and Training | 7、15.2 |
| ISO 15489-1:2016 7.2–7.5 | Appraisal、Business Context、Record Requirements、Implementation | 9.2、10.1–10.4、13.5–13.6 |
| ISO 15489-1:2016 8.2 | Metadata Schemas | 11.5、13.1 |
| ISO 15489-1:2016 8.3 | Business Classification Schemes | 11.7、13.5 |
| ISO 15489-1:2016 8.4 | Access and Permissions Rules | 11.13、13.9 |
| ISO 15489-1:2016 8.5 | Disposition Authorities | 7、11.8、13.6 |
| ISO 15489-1:2016 9.2–9.3 | Creating and Capturing Records | 9.3–9.4、10.4、11.1 |
| ISO 15489-1:2016 9.4–9.5 | Classification and Indexing | 9.4、11.7、11.12 |
| ISO 15489-1:2016 9.6–9.8 | Access、Storing、Use and Reuse | 9.6、11.12–11.14 |
| ISO 15489-1:2016 9.9 | Migrating and Converting Records | 9.8、10.9、11.15 |
| ISO 15489-1:2016 9.10 | Disposition | 9.8、10.9、11.8 |
| ISO 10007:2017 4.1 | Responsibilities and Authorities | 7.1–7.3 |
| ISO 10007:2017 4.2 | Dispositioning Authority | 7.1–7.2、11.8 |
| ISO 10007:2017 5.2 | Configuration Management Planning | 9、10、17、19 |
| ISO 10007:2017 5.3.1 | Product/Service and Configuration Item Selection | 8.1–8.3、11.2 |
| ISO 10007:2017 5.3.2 | Configuration Information | 6.4、11.2、11.5、13.2 |
| ISO 10007:2017 5.3.3 | Baselines | 3.1、6.4、9.5、18.4 |
| ISO 10007:2017 5.4.1–5.4.2 | Change Initiation、Identification and Documentation | 9.7、10.8、11.11 |
| ISO 10007:2017 5.4.3–5.4.5 | Change Evaluation、Disposition、Implementation and Verification | 9.7、10.8、15 |
| ISO 10007:2017 5.5.1–5.5.2 | Configuration Status Accounting and Reports | 8、12、16 |
| ISO 10007:2017 5.6 | Configuration Audit | 9.9、15、16 |
| ISO 10007:2017 Annex A | Configuration Management Plan Structure | 9、10、13、20 |
| ISO/IEC 27001:2022 第 4 章 | Context、Interested Parties、Scope、ISMS | 3、9.2、10.1、18.5 |
| ISO/IEC 27001:2022 第 5 章 | Leadership、Policy、Roles | 7、11.13、13.9 |
| ISO/IEC 27001:2022 第 6 章 | Risk、Objectives、Planning of Changes | 5、9、11、17 |
| ISO/IEC 27001:2022 7.2–7.4 | Competence、Awareness、Communication | 7、15.2、18 |
| ISO/IEC 27001:2022 7.5.1 | Documented Information General | 8、11.5、13 |
| ISO/IEC 27001:2022 7.5.2 | Creating and Updating | 9.3–9.5、10.3–10.5 |
| ISO/IEC 27001:2022 7.5.3 | Control of Documented Information | 11.2、11.5、11.13、12 |
| ISO/IEC 27001:2022 第 8 章 | Operational Planning and Control | 9、10、11.12–11.18 |
| ISO/IEC 27001:2022 9.1 | Monitoring、Measurement、Analysis and Evaluation | 9.9、14、16.4 |
| ISO/IEC 27001:2022 9.2–9.3 | Internal Audit and Management Review | 15、16 |
| ISO/IEC 27001:2022 10.1–10.2 | Improvement、Nonconformity and Corrective Action | 9.9、11.10、16.5 |
| ISO/IEC 27001:2022 Annex A | Information Security Controls | 11.3、11.7–11.8、11.12–11.18、18.5 |
| ISO/IEC 27001:2022/Amd 1:2024 4.1–4.2 | Climate Action Changes | 19.2–19.3、20.14 |
| ISO/IEC 42001:2023 第 4 章 | Context and AI Management System | 3、9.2、10.1、18 |
| ISO/IEC 42001:2023 第 5 章 | Leadership、AI Policy、Roles | 7、11.14 |
| ISO/IEC 42001:2023 第 6 章 | Risk、Impact、Objectives、Changes | 9.7、11.3、11.9–11.14 |
| ISO/IEC 42001:2023 7.5.1–7.5.3 | Documented Information | 8、9.3–9.5、11.5、13 |
| ISO/IEC 42001:2023 第 8 章 | Operational Planning、AI Risk and Impact Processes | 10.7、11.12–11.18 |
| ISO/IEC 42001:2023 第 9 章 | Monitoring、Audit、Management Review | 9.9、14–16 |
| ISO/IEC 42001:2023 第 10 章 | Improvement and Corrective Action | 9.9、11.10、16.5 |
| ISO/IEC 42001:2023 Annex A、B.2 | AI Policy Controls and Guidance | 7、11.13–11.14 |
| ISO/IEC 42001:2023 Annex B.3 | Internal Organization | 7、15.2 |
| ISO/IEC 42001:2023 Annex B.4 | Resources、Documentation、Data、Tooling、System、Human Resources | 8、10.7、11.3、11.14–11.16 |
| ISO/IEC 42001:2023 Annex B.5 | AI System Impact Assessment | 10.6–10.7、15.3–15.5 |
| ISO/IEC 42001:2023 Annex B.6 | AI System Life Cycle、Technical Documentation、Event Logs | 9、11.14、11.17、18 |
| ISO/IEC 42001:2023 Annex B.7 | Data Acquisition、Quality、Provenance、Preparation | 11.3、18.5 |
| ISO/IEC 42001:2023 Annex B.8 | User/Interested Party Information and Reporting | 11.12–11.14、16 |
| ISO/IEC 42001:2023 Annex B.9 | Responsible Use of AI Systems | 7.3、10.7、11.14 |
| ISO/IEC 42001:2023 Annex B.10 | Third-party and Customer Relationships | 11.3、11.13、18.5 |

规范性国际标准来源：

1. ISO, [ISO 15489-1:2016 — Records management — Concepts and principles](https://www.iso.org/standard/62542.html)。
2. ISO, [ISO 10007:2017 — Guidelines for configuration management](https://www.iso.org/standard/70400.html)。
3. ISO, [ISO/WD 10007 — Guidelines for configuration management（制定中）](https://www.iso.org/standard/92170.html)。
4. ISO, [ISO/IEC 27001:2022 — Information security management systems — Requirements](https://www.iso.org/standard/27001)。
5. ISO, [ISO/IEC 27001:2022/Amd 1:2024 — Climate action changes](https://www.iso.org/standard/88435.html)。
6. ISO, [ISO/IEC 42001:2023 — Artificial intelligence management system](https://www.iso.org/standard/42001)。
