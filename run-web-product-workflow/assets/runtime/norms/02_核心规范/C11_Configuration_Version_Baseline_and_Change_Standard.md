# C11 配置、版本、基线与变更控制规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C11 |
| 英文名称 | Configuration, Version, Baseline and Change Control Specification |
| 正式文件名 | `C11_Configuration_Version_Baseline_and_Change_Standard.md` |
| 版本 | V6.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V6.3 至 C10 V6.3 |
| 生产前调研 | RVR-C11-0001 |
| 下游规范 | C12、E01 至 E05 |
| 横向适用 | 产品、需求、设计、代码、配置、测试、证据、模型、数据、知识、运维和治理资产 |
| 访问级别 | 内部 |
| 保留要求 | 按适用 Retention Rule 保留；永久标识、批准基线、Change、Release Configuration、替代、退役、更正和审计历史禁止无痕删除 |

本文件在项目负责人批准前不得作为正式基线、Gate 通过依据或自动状态写入授权。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范为所有受控 Product Asset 建立永久身份、版本或修订、不可变快照、批准基线、变更请求、影响分析、变更决定、发布配置、替代和退役控制。

本规范实现以下目标：

1. 使业务身份与文件路径、数据库键、URL、Git Commit、版本号和状态分离；
2. 使同一资产的每次内容变化具有可识别 Revision 和事实记录；
3. 使重要时点的完整状态可以通过 Snapshot 定位、校验和重建；
4. 使批准 Baseline 成为不可静默覆盖的资产—版本集合；
5. 使对已批准或已基线化资产的 Change 在实施前经过分类、影响分析和授权；
6. 使紧急变更在缩短路径时仍保留责任、最小记录、事后验证和复盘；
7. 使 Release 可以重建精确的 Requirement、Design、Code、Configuration、Evidence、环境和批准版本；
8. 使替代、退役、归档、恢复和回滚保留原身份、历史和生效边界；
9. 使配置状态记账、完整性检查和审计可以自动执行并人工复核；
10. 使 Agent 和自动化工具只能在授权边界内起草、分析、执行和记录，不能自批。

## 3. 适用范围

本规范适用于：

- Need、Problem、Intent、Goal、Initiative、Scope、PRD、Feature、Requirement 和 Acceptance 资产；
- UX、Architecture、Design、Interface、Schema、Data Model、Failure Design 和 Decision 资产；
- Source Code、Configuration、Infrastructure as Code、Build Script、Migration、Policy、Prompt、Model 和 Dataset；
- Test、Evidence、Coverage、Validation、Agent Run、Review、Gate、Risk、Waiver 和 Release 资产；
- 文档库、代码库、制品库、模型库、数据目录、知识库、工单系统和部署平台中的正式受控对象；
- 人工编制、规则生成、工具生成、Agent 生成、外部导入和供应商交付的受控对象；
- P2 档位下 10 类 C11 正式产物的身份、状态、必填信息、模板和质量检查；
- E01 至 E05 扩展规范对配置、记录、安全、数据、知识和运维的附加控制接口。

只要某项资产用于批准、设计、实现、验证、发布、运行、审计、维护或风险判断，即使其载体不是 Markdown 或 Git 文件，也适用本规范。

### 3.1 配置项纳入判定

满足以下任一条件的 Product Asset 必须登记为 Configuration Item：

1. 被批准、基线化、发布或用于 Gate；
2. 是 Requirement、Design、Code、Configuration、Test、Evidence 或 Release 的正式输入；
3. 变化会影响行为、兼容性、安全、隐私、合规、数据、可运维性或外部承诺；
4. 需要唯一标识、版本、完整性、访问、保留、恢复或审计；
5. 由多个角色、Agent、仓库、环境或组织共同消费；
6. 是可执行制品、部署配置、数据库迁移、模型、数据集、提示词或策略；
7. 被法规、合同、政策、Decision、Risk、Waiver 或 Retention Rule 约束；
8. 被纳入 Baseline 或 Release Configuration。

以下对象可以不登记为独立 Configuration Item：

- 不进入正式决策、交付或记录的临时草稿；
- 可由受控源确定性再生且无独立批准、版本或保留需求的中间文件；
- 不含产品事实且不作为证据的本地缓存；
- 不影响受控资产的个人工作笔记。

排除必须由 IDP 或适用配置管理计划给出可检查规则。临时对象一旦被引用为 Evidence、Decision 输入或发布输入，必须先纳入控制。

## 4. 不适用范围

本规范不负责定义以下对象的业务内容：

- C01 的 Need、Problem、Discovery Evidence、Product Definition、Intent 和 Goal；
- C02 的 Initiative、Scope、Risk、Constraint、Dependency 和 Agent Modification Boundary；
- C03 的 PRD、Feature、Scenario、Release Intent 和 Non-goal；
- C04 的 Requirement 身份、语义、质量、演进和冲突；
- C05 的 Acceptance Criteria、Verification、Validation 和 Evidence 充分性；
- C06 的 UX、技术设计、Architecture、Interface、Data、State 和 Failure Design；
- C07 的 Agent Role、Accountability、Authorization、Approval、Stop、Escalation 和 Resume；
- C08 的 Agent Context、Source、Priority、Freshness、Trust 和 Context Fingerprint；
- C09 的 Agent Run、Command、Tool、Actual Change、Validation、Failure 和 Human Review；
- C10 的 Decision、Trace、Coverage、Lineage、Impact Query 和 Untracked Change 报告；
- C12 的 Review、Gate、Exception/Waiver、Risk Acceptance、Release Readiness 和 Product Health；
- E01 至 E05 的领域专属控制。

C11 管理上述资产的配置身份、Revision、Snapshot、Baseline、Change 和 Release Configuration，但禁止：

- 通过 Version 或 Revision 改写 Requirement 业务身份；
- 通过 Baseline 代替批准内容本身；
- 通过 CHG 代替新 Requirement、Defect、Task、Incident、Risk 或 Decision 的事实源；
- 通过 Git Commit 代替 Asset ID、Approval 或 Release Configuration；
- 通过 Hash 声明作者真实性、授权、业务正确性或证据充分性；
- 通过回滚记录代替 C05 验证或 C12 Release Decision；
- 通过删除历史解决错误、冲突或不再适用。

## 5. 规范性用语与受控判定

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性示例，不作为符合性判定依据。

### 5.2 领域判定值

以下值不是正式产物 State：

| 字段 | 受控值 |
|---|---|
| CI Member Status | `Registered`、`Controlled`、`Suspended`、`Superseded`、`Retired` |
| Change Path | `Normal`、`Pre-authorized Standard`、`Emergency` |
| Change Classification | `Clarification/Patch`、`Revision`、`New Requirement`、`Defect Fix`、`Refactor`、`Supersession` |
| Decision Outcome | `Approve`、`Approve with Conditions`、`Reject`、`Defer` |
| Implementation Status | `Not Started`、`In Progress`、`Completed`、`Failed`、`Rolled Back`、`Cancelled` |
| Verification Status | `Not Started`、`In Progress`、`Pass`、`Fail`、`Blocked`、`Invalidated` |
| Integrity Result | `Pass`、`Fail`、`Not Verified` |
| Reconstruction Result | `Reconstructed`、`Partially Reconstructed`、`Not Reconstructable` |
| Compatibility Impact | `Compatible`、`Conditionally Compatible`、`Breaking`、`Unknown` |

IDP、CIR、IMA 只使用 DOC State；CHG 只使用 CASE State；BSL、CHD 只使用 DEC State；VRR、SNP、RLC、SRR 只使用 REC State。

### 5.3 事实、推断和决定

| 类型 | 允许内容 | 禁止内容 |
|---|---|---|
| Fact | 已存在 Asset、Revision、Snapshot、Diff、Commit、Evidence、Approval、Deployment 和实际状态 | 未核验的工具摘要 |
| Inference | 明确标记的影响候选、未知项、潜在兼容性和待确认关系 | 直接写为已批准、已验证或已发布 |
| Change Decision | 有权 Authority 对 Change、Baseline、条件、Residual Risk 和有效边界作出的 C10 Decision | Agent 私有推理或无授权结论 |
| Configuration Record | 某时点已发生的版本、快照、发布、替代、退役或更正事实 | 专业化自 E04 Record；不得表示预测未来完成状态 |

### 5.4 控制优先级

发生冲突时按以下顺序判定：

1. 适用法律、合同、监管、组织政策和有效 C12 Decision；
2. 当前批准的 IDP、Authority 和 Retention Rule；
3. 当前有效 Baseline 与已批准 CHD；
4. 所属资产规范和当前批准 Revision；
5. 受控工具配置、自动化规则和工作说明；
6. Agent 建议、默认值和个人习惯。

下位工具不得覆盖上位受控事实。冲突必须进入 CHG、Risk、Waiver 或 Escalation。

## 6. 术语与定义

| 术语 | 定义 |
|---|---|
| Product Asset | 在产品生命周期内被创建、使用、批准、验证、发布、运行、保留或处置的受控对象 |
| Configuration Item | 因需唯一标识、版本、基线和受控变更而纳入配置管理的 Product Asset；并非所有临时草稿 |
| Asset ID | 在指定命名空间内永久、唯一且不复用的业务标识 |
| Version | 表示内容或发布状态的标记；不是永久业务身份 |
| Revision | 同一 Asset ID 下的一次受控内容变化；不自动产生新资产或新 Requirement |
| Snapshot | 某一时点完整资产状态的不可变表示；不是持续变化的文件、Branch 或工作区 |
| Baseline | 经批准并固定的资产—版本集合；后续只能通过受控变更和后继基线改变 |
| Change Request | 对已批准或已基线化资产提出变更的控制记录；不是新 Requirement、Defect 或 Task |
| Impact Analysis | 对 Change 的范围、全链路影响、兼容性、迁移、Risk、成本、时序和未知项的受控分析 |
| Change Decision | Authority 对 Change 候选处置形成的批准、条件批准、拒绝或延期决定 |
| Release Configuration | 可重建一次 Release 的精确资产版本、构建、环境、证据、批准和回滚信息 |
| Configuration Status Accounting | 对 CI、Revision、Snapshot、Baseline、Change 和 Release 当前及历史状态的记账与报告 |
| Supersession | 新资产或新 Revision 使旧对象退出当前有效集合，但旧身份和历史永久保留 |
| Retirement | 资产停止在指定范围内使用并进入受控保留或处置状态 |
| Configuration Recovery | 从保留副本、Snapshot 或 Baseline 读取或重建历史配置状态的受控活动 |
| Rollback | 将当前系统或资产变更到一个先前已知配置的受控变更；不保证外部副作用或数据自动恢复 |
| Configuration Audit | 核对配置身份、实际内容、批准集合、记录和实现之间一致性的审查 |
| Functional Configuration Audit | 核对已实现配置是否满足规定功能和验证要求 |
| Physical Configuration Audit | 核对实际构成、版本、标识和记录是否与批准配置一致 |
| Drift | 当前实际状态与声明的 Baseline 或 Release Configuration 之间未经批准的偏差 |

### 6.1 必须区分的五个概念

| 概念 | 回答的问题 | 是否可变 | 是否需要批准 | 不得替代 |
|---|---|---|---|---|
| Asset ID | 这是什么资产 | 永久不变 | 分配规则需批准 | Version、路径、Commit |
| Revision/Version | 该资产处于哪次内容或发布状态 | 通过新值演进 | 依资产状态和规则 | Asset ID、Snapshot |
| Snapshot | 某时点完整状态是什么 | 不可变 | 捕获本身可自动；作为基线输入需核验 | Baseline、Approval |
| Baseline | 哪组资产版本已被批准固定 | 原记录不可变 | 必须 | 工作区、Branch、Release |
| Release Configuration | 实际发布了哪组可重建配置 | 原记录不可变 | 发布依 C12 授权 | Baseline、部署日志单项 |

## 7. 角色、职责与权限

| 角色 | 主要职责 | 禁止事项 |
|---|---|---|
| Configuration Management Owner | 批准配置策略、CI 范围、状态记账和审计计划 | 绕过 Change Authority 修改批准基线 |
| Identifier Authority | 管理命名空间、分配、唯一性、不复用和迁移 | 重用已退役 ID |
| Configuration Item Owner | 维护资产内容、Revision、位置和关系 | 将个人工作区声明为正式 Snapshot |
| Change Proposer | 提交 CHG、理由、触发和拟议状态 | 以 CHG 取代新 Requirement 或 Defect |
| Change Owner | 组织分类、IMA、计划、实施、验证和关闭 | 自批超出授权的 Change |
| Change Authority | 审阅 IMA，批准、条件批准、拒绝或延期 | 批准无范围、无影响或无验证计划的重大 Change |
| Baseline Authority | 批准 BSL 及其生效、替代和范围 | 原位编辑 Approved BSL |
| Release Authority | 在 C12 中决定 Release，并消费 RLC | 以构建成功代替 Release Approval |
| Implementer | 按 CHD 和 C09 Run 实施实际变化 | 擅自扩大范围或修改批准条件 |
| Verification Owner | 按 C05 独立验证变更和重建 | 只依据版本号声称兼容 |
| Records Steward | 按 E04 管理元数据、访问、保留、更正和处置 | 无痕删除旧 Revision、Baseline 或 Decision |
| Security/Data/Operations Owner | 对适用 E02、E03、E05 影响进行评审 | 在扩展未激活时忽略潜在适用性 |
| Agent/Automation Operator | 起草、分析、执行授权命令、记录结果和提出异常 | 自批、自验、自行接受 Residual Risk |
| Independent Reviewer | 审核身份、影响、基线、发布重建和历史完整性 | 只审表面字段不核对实际对象 |

### 7.1 最低职责分离

1. High/Critical Risk、Breaking Change、安全、隐私、合规、外部承诺、不可逆数据变化和生产紧急变更中，Proposer、Implementer、Verifier 与 Authority 必须按 C07 分离；
2. Agent 可以创建 Draft IDP/CIR/IMA、Open CHG、Proposed BSL/CHD 和 Recorded 候选记录，但无明确授权时不得批准或关闭自身工作；
3. Baseline Authority 不得批准无法解析成员版本或完整性失败的 BSL；
4. Release Authority 不得仅以 CHD Approved、构建成功或测试通过作为 Release Decision；
5. 更正原始 Record 的角色不得删除原值，必须由 Records Steward 监督更正链。

## 8. 正式产物与唯一事实源

### 8.0 V6.3 三阶段修订与生成边界

TaskContract 在首个 `run_started` Event 时冻结。之后 Scope、Acceptance、Authority、Plan 或 Task Profile 的变化必须增加 Revision 并写入 `amendments[]`，包含旧值、新值、原因、依据和时间。TaskOutcome 形成后采用同一纠错规则，禁止静默覆盖终态事实。

RunLedger 只追加；更正通过新 Event 引用原 Event。ProjectState 和 DerivedView 由生成器重建，禁止直接编辑或纳入独立变更源。Git Commit/Diff 可作为代码和文档变化的权威证据，但外部副作用、失败、验证环境、批准和决定必须由相应元类型或 AuthorityAsset 保存。

`AI-Native的产品开发生产规范` 仓库是规范正文与规范映射的唯一编辑事实源；`LFen-Skills/run-web-product-workflow` 是 Skill 实现、脚本、引用包装和运行快照的唯一编辑事实源。规范模板目录及安装入口必须以受控 Junction 指向该 Skill 事实源，不得保留平行可编辑副本。Skill 内置规范只能由受控同步脚本从显式指定的规范仓库刷新；运行时禁止从工作目录、父目录、环境变量或其他外部仓库查找同名规范。

### 8.1 正式产物

| 代码 | 正式产物 | 状态模型 | 唯一事实源 |
|---|---|---|---|
| IDP | Identifier Policy | DOC | 标识与版本方案 |
| CIR | Configuration Item Register | DOC | CI 当前登记与索引 |
| VRR | Version or Revision Record | REC | 版本/修订变化事实 |
| SNP | Snapshot Record | REC | 不可变状态捕获事实 |
| BSL | Baseline Record | DEC | 批准基线决定 |
| CHG | Change Request | CASE | 变更控制案件 |
| IMA | Impact Analysis | DOC | 变更影响分析 |
| CHD | Change Decision | DEC | 变更处置决定 |
| RLC | Release Configuration Record | REC | 实际发布配置事实 |
| SRR | Supersession and Retirement Record | REC | 替代与退役事实 |

10 类产物不得因使用同一工单、数据库或 Markdown 文件而失去独立身份。工具可以联表展示，但必须支持分别导出、校验、授权和保留。

### 8.2 唯一事实源边界

| 信息 | 唯一事实源 | C11 使用规则 |
|---|---|---|
| 资产业务语义 | 所属 C01 至 C10、E01 至 E05 规范 | 固定 Asset ID 和 Revision，不改写业务语义 |
| 标识与版本方案 | IDP | 所有工具字段必须映射 |
| CI 当前索引 | CIR | 不复制资产正文 |
| 内容变化事实 | VRR + C09 Actual Change | 引用实际 Diff/Commit/Artifact |
| 某时点完整状态 | SNP | 必须可定位并校验 |
| 批准配置集合 | BSL | 禁止由当前 Branch 反推 |
| 变更控制 | CHG + IMA + CHD | 不替代 Requirement、Defect、Risk 或 Task |
| 实际 Release 构成 | RLC | 不由计划 Baseline 或构建标签推断 |
| 替代与退役 | SRR | 保留旧身份和有效边界 |
| Trace 与 Impact Query | C10 | C11 消费结果，不建立平行 Link 事实源 |
| Gate 与 Release Decision | C12 | C11 提供配置证据，不作 Gate Decision |

### 8.3 最低关系

C11 必须使用公共受控关系集合。至少建立：

- CIR `contains` Configuration Item；
- VRR、SNP、BSL、CHG、IMA、CHD、RLC、SRR `addresses` 或 `affected-by` 对应资产和事件；
- IMA `generated-by` 适用 C10 Impact Query 或分析 Run；
- CHD `depends-on` CHG 与 IMA；
- 新 BSL `supersedes` 旧 BSL；
- 新资产或 Revision 按语义 `supersedes` 或 `replaces` 旧对象；
- Release 中的资产 `released-in` RLC；
- RLC `generated-by` 构建、部署或 Agent Run；
- Evidence `observed-from` 实际验证或运行。

禁止使用无受控语义的 `related-to` 作为正式关系。

## 9. 生命周期与工作机制

### 9.1 配置与变更总流程

```text
定义 IDP
  → 识别 Configuration Item
  → 分配永久 Asset ID 并登记 CIR
  → 创建或导入初始 Revision
  → 记录 VRR
  → 捕获并校验 SNP
  → 提议 BSL
  → 审核成员、完整性、范围和批准
  → Approved BSL 生效
  → 触发 Change
  → C04 分类
  → 创建 CHG 与 IMA
  → CHD 决定
  → C09 受控实施
  → C05 验证与 C10 追溯检查
  → 更新 VRR/SNP/CIR
  → 创建后继 BSL
  → C12 Release Decision
  → 记录 RLC
  → 监视 Drift、替代、退役与恢复
  → 保留审计历史
```

### 9.2 初始化

产品在首次基线前必须建立：

- Approved IDP；
- Configuration Management Owner、Identifier Authority、Change Authority 和 Baseline Authority；
- CIR；
- CI 纳入/排除规则；
- 每类资产 Version/Revision Scheme；
- Snapshot 捕获、完整性算法、存储和保留规则；
- Baseline 类型、命名、批准和后继规则；
- Normal、Pre-authorized Standard、Emergency Change Path；
- IMA 深度与 Risk 分级规则；
- C09 实施、C05 验证、C10 追溯和 C12 Gate 接口；
- E04 元数据、访问、保留、更正和处置接口；
- 配置状态记账和审计计划。

### 9.3 持续控制

1. CIR 必须反映每个 CI 的当前 Revision、State、位置、Owner 和 Baseline；
2. 资产内容发生受控变化时必须创建 VRR；
3. 用于 Baseline、Release、审计或恢复的状态必须创建 SNP；
4. 已批准/基线化资产变化必须先创建 CHG，除非适用已批准的 Pre-authorized Standard Change；
5. 实施完成不等于验证通过，验证通过不等于 Release Approved；
6. 每次 Release 必须记录 RLC；
7. 每次替代或退役必须记录 SRR；
8. Drift、完整性失败、无来源变化或无法重建必须进入 CHG、UCR、Risk、Incident 或 Stop/Escalation。

## 10. 配置、版本、基线与变更控制规则

### 10.1 Configuration Item 范围

1. CI 粒度必须足以独立识别、变更、验证、批准、发布或恢复；
2. 粒度不得细到每个临时行、缓存或不可独立控制的片段；
3. 聚合资产与成员资产可以同时成为 CI，但必须使用 `contains` 保持独立身份；
4. 外部资产必须登记 Authority、来源、Version、访问位置、获取时间、许可证/合同限制和完整性；
5. 运行时动态配置、Feature Flag、Secret Reference、模型权重和数据 Schema 只要影响行为即必须纳入；
6. Secret 的值禁止写入 CIR、SNP、BSL 或 RLC；只记录 Secret Reference、Version/Rotation 和权限边界；
7. CI 范围变化必须通过 IDP Revision 或适用 CHG，不得直接改登记规则。

### 10.2 永久标识与命名空间

1. Asset ID 格式必须遵循 `<Artifact Type Code>-<Sequence>` 或 IDP 批准的等价稳定格式；
2. Asset ID 必须在命名空间内唯一；
3. Asset ID 一经分配永久保留；删除、替代、退役、迁移或工具更换后禁止复用；
4. Asset ID 禁止包含 Version、Revision、日期、State、Owner、标题、组织名称或可变位置；
5. 文件名、目录、URL、数据库主键、工单号、Branch、Tag、Commit 或制品坐标不得替代 Asset ID；
6. 工具迁移必须保留原 Asset ID；无法原样承载时使用稳定映射表，不得重新编号后丢失原 ID；
7. 错误分配的 ID 必须标记为 Retired/Voided 并记录原因，禁止回收；
8. 资产拆分时原 ID 保留并通过 `supersedes`、`replaces`、`contains` 或 `derives-from` 连接新 ID；
9. 资产合并时各原 ID 保留，新的聚合资产使用新 ID；
10. Identifier Authority 必须定期检查重复、空洞误复用、非受控别名和迁移映射。

### 10.3 身份、Version、Revision、Snapshot 与 Baseline 分离

1. 同一 Asset ID 可以有多个 Revision；
2. Revision 变化不自动产生新 Asset ID；
3. Version 可以表达产品发布或公共 API 兼容性，Revision 表达同一资产内容演进；
4. 一次 Revision 必须至少对应一个可定位内容状态；重要 Revision 应形成 SNP；
5. SNP 必须固定内容和依赖边界；Branch、HEAD、工作区或 `latest` 只是可变引用；
6. BSL 必须列出 Asset ID + Revision/Version + Snapshot/Integrity；
7. BSL 的批准对象是集合，不是单个 Commit 名称；
8. RLC 记录实际发布构成，可以引用 BSL，但必须记录与 BSL 的差异；
9. 任一层缺失时禁止用相邻层推断：有 Commit 不等于有 Snapshot，有 Snapshot 不等于有 Baseline，有 Baseline 不等于已 Release。

### 10.4 Version 与 Revision 规则

IDP 必须为每类资产定义：

- Scheme 名称与适用范围；
- 起始值；
- 单调递增或排序规则；
- 何时产生新 Revision；
- 何时产生新 Version；
- 兼容性判定方法；
- 预发布、草稿、构建元数据和分支语义；
- 被替代、撤回和纠错处理；
- 工具字段映射；
- 人工与自动分配权限。

控制规则：

1. 禁止以 Version 值作为永久身份；
2. 禁止原位修改已发布 Version 的内容；
3. 文档、需求和记录可以使用单调 Revision、日期序列或批准的其他方案；
4. 只有声明清晰公共 API 且 IDP 正式采纳时才使用 SemVer；
5. 采用 SemVer 时，Major/Minor/Patch 必须依据公共 API 兼容性，不得依据工作量、营销或日期猜测；
6. Version 的兼容性声明必须由 C05 Evidence 支持；
7. Build Metadata 不得被误用为更高优先级 Version；
8. 撤回 Version 不得删除，必须记录原因、替代版本和消费方通知；
9. 发现已发布 Version 内容被修改时必须 Stop、记录 Integrity Failure 并启动 CHG/Incident。

### 10.5 Snapshot 与完整性

SNP 必须固定：

- Asset ID、Revision/Version；
- 捕获时间和创建者；
- 内容位置和存储边界；
- 完整性算法、Digest 和校验结果；
- 仓库/制品库/数据源身份；
- 解析后的 Commit/Object ID，不只记录 Branch/Tag；
- 未跟踪、忽略、本地修改、Submodule、LFS、外部依赖和生成物状态；
- Toolchain、Schema、模型、数据或环境的适用引用；
- 可访问性、保留和不可变控制；
- 与前后 Revision、CHG、BSL、RLC 的关系。

规则：

1. Snapshot 创建后禁止原位改写；
2. Snapshot 错误通过 Corrected REC 和新 SNP 纠正；
3. Hash 算法、范围和规范化规则必须可复现；
4. `Integrity Result = Pass` 只说明按记录算法和范围校验一致；
5. 无法覆盖的外部状态必须列为 Exclusion/Unknown，不得默认为已捕获；
6. 失去访问、对象缺失或算法失效时必须标记风险并建立迁移或再固化计划；
7. Snapshot 恢复测试应按 Risk 和 Retention Rule 定期执行。

### 10.6 Baseline 建立与维护

BSL 必须在 `Proposed` 时完成：

- Baseline ID、Purpose、Scope 和 Type；
- Included Asset ID、Revision/Version、SNP 和 Integrity；
- Exclusion 与理由；
- Dependency、Constraint、Risk、Waiver 和已知 Unknown；
- 候选生效时间、Authority 和适用环境；
- 前一 Baseline 和预期 Successor；
- 成员解析与重建检查。

批准规则：

1. Baseline Authority 必须核对成员身份、版本、Snapshot、完整性、关系和批准状态；
2. 成员无法解析、Integrity Fail、关键 Unknown 未处置或必需批准缺失时禁止批准；
3. `Approved` BSL 自生效时间起不可变；
4. 对 Approved BSL 的任何内容修正必须创建新 BSL 或 Corrected 记录，并保留原 BSL；
5. 后继 BSL 使用 `supersedes` 指向旧 BSL；
6. 旧 BSL 转为 `Superseded` 不删除、不改变原成员清单；
7. BSL 可以具有 `Conditionally Approved`，但必须记录条件、Owner、期限和阻断边界；
8. BSL 不自动等于 Release；实际发布由 RLC 和 C12 Decision 证明。

### 10.7 变更触发与 C04 分类

以下事件必须触发分类：

- 对 Approved、Baselined、Released 或受外部承诺约束资产的内容变化；
- Scope、Requirement、Design、Code、Configuration、Schema、Data、Model、Prompt、Policy 或 Evidence 变化；
- Defect、Incident、Vulnerability、Audit Finding、Drift、Dependency Update 或环境变化；
- 新法规、合同、Risk、Waiver 条件或运行反馈；
- 替代、退役、迁移、恢复和回滚；
- 发现未经授权的实际变化。

分类必须复用 C04：

| 分类 | 身份处理 | C11 处理 |
|---|---|---|
| Clarification/Patch | 同一 Requirement ID | 记录新 Revision/事件；已基线化时创建 CHG |
| Revision | 同一 Asset/Requirement ID | 新 Revision；已基线化时创建 CHG、IMA、CHD |
| New Requirement | 新 Requirement ID | 先走 C04，再由 C11 纳入配置；不得只建 CHG |
| Defect Fix | 保留 Requirement ID，创建 Defect | CHG 连接 Defect、实际修复和验证 |
| Refactor | 不创建产品 Requirement | 创建 Engineering Change/技术债来源和 CHG |
| Supersession | 旧 ID 保留，新对象按语义取新 ID或新 Revision | 建立 `supersedes/replaces` 和 SRR |

禁止把所有修改都登记成新 Requirement，也禁止用“只是 Patch”绕过已基线资产的 Change Control。

### 10.8 Change Request 创建与分流

CHG 创建时必须记录：

- Change ID；
- Proposer、Reason、Trigger；
- Change Path 和 C04 Classification；
- Affected Asset ID、Original State/Revision/Baseline；
- Proposed State/Revision；
- 初始 Scope、Risk 和 Urgency；
- Planned Version/Baseline；
- Change Owner、Approver/Authority；
- Decision、Implementation Status、Verification Status；
- 关联 Requirement、Defect、Incident、Risk、Waiver、Run 和 Evidence。

分流规则：

1. `Normal`：完整 IMA 和事前 CHD；
2. `Pre-authorized Standard`：必须已有 Approved 变更模型、范围、步骤、验证、回滚和 Authority；超出任一边界立即转 Normal；
3. `Emergency`：仅在延迟会造成更大现实损害且适用 Emergency Authority 时使用；
4. CHG 重复时不得删除，必须连接主 CHG 并进入 `Cancelled` 或 `Closed`；
5. 未知范围、无 Owner、无原状态或无法识别资产的 CHG 必须 `Blocked`；
6. 发现实际变化先于 CHG 时，必须创建 C10 UCR 并按 Risk 决定 Stop、隔离、回滚或追认；追认不消除违规事实。

### 10.9 Impact Analysis

IMA 必须在实施前固定分析 Snapshot，至少覆盖：

- Change、分析范围、环境、时间点和判定准则；
- C10 Impact Query 参数、结果和完整性；
- Need、Requirement、Acceptance、UX、Design、Architecture；
- Code、Configuration、Interface、Schema、Data、Model、Prompt；
- Test、Evidence、Coverage、Release、Operations 和 Context；
- 直接、间接、跨仓库、跨环境和外部消费方；
- 兼容性、迁移、数据转换、回滚和恢复；
- Security、Privacy、Compliance、Safety 和供应链；
- 成本、资源、时序、停机、窗口和依赖；
- Risk、Residual Risk、Unknown、Assumption 和限制；
- 备选方案、不变更后果和推荐处置；
- 分析者、复核者、证据和有效期。

控制规则：

1. 分析深度与 Risk、不可逆性、影响范围和外部承诺相称；
2. `No Impact` 必须列出已检查域和证据，不得只写结论；
3. C10 Query 为 `Partial` 或 `Indeterminate` 时，IMA 必须显式记录未知影响；
4. 兼容性不得仅由 SemVer、文件 Diff 或测试数量推断；
5. 数据删除、Schema 迁移、密钥轮换、模型变化和 Feature Flag 必须评估不可逆副作用；
6. IMA 过期、资产 Revision 变化或 Scope 扩大时必须重新分析；
7. Agent 输出的影响候选必须经有权人员复核后才能作为决定依据。

### 10.10 Change Decision 与 Authority

CHD 必须记录：

- CHG、IMA 和候选处置；
- Decision Outcome；
- Rationale；
- Conditions、Risk、Residual Risk 和接受者；
- Authority、参与者、决定时间；
- 允许的资产、命令、环境、时段和最大变化边界；
- Planned Version、SNP、Baseline 和 Release；
- 验证、回滚、监视和停止条件；
- 生效、到期和替代关系。

规则：

1. CHD 的正式 State 使用 DEC State；
2. `Decision Outcome = Approve` 对应 CHD `Approved`；
3. `Approve with Conditions` 对应 `Conditionally Approved`，条件未满足不得扩大实施；
4. `Defer` 不产生实施授权，CHD 保持 `Under Review` 或按事实进入 `Rejected/Expired`；
5. `Rejected` CHD 保留理由，不删除 CHG；
6. CHD 只授权声明范围；任何扩大必须更新 IMA 并形成新决定；
7. Agent、Proposer 或 Implementer 不得在无明示 Authority 时批准自身 CHD；
8. CHD Approved 不等于 Release Approved。

### 10.11 实施计划

实施前必须确定：

- 精确输入 Baseline/Snapshot；
- 资产和路径白名单；
- 允许命令、工具、权限和环境；
- 计划 Diff、迁移、依赖和配置变化；
- 顺序、窗口、并发和停止点；
- 备份、恢复和 Rollback Plan；
- 验证、监视和接受准则；
- 失败、超范围、Integrity Fail 和数据异常的 Stop/Escalation；
- C09 Run ID 与 Human Review；
- 记录更新责任和完成时限。

计划中的 `Rollback Version` 必须可解析并经过恢复可行性检查。禁止把“Git revert”当作所有系统的通用回滚方案。

### 10.12 受控实施

1. 实施必须在 C09 Agent Run 或等价受控 Run 中执行；
2. Run 必须使用批准的输入 Snapshot、权限、命令和范围；
3. 实际命令、Exit Code、stdout/stderr 摘要、Diff、Commit、Artifact 和异常必须记录；
4. Actual Change 与 Planned Change 必须比较；
5. 超范围变化、未跟踪文件、意外依赖、环境漂移或验证前置失败必须 Stop；
6. 实施过程禁止覆盖原 Snapshot、原 BSL、原 RLC 或原 Record；
7. 每次重试必须产生可区分的 Run Attempt；
8. 手工热修、控制台修改、数据库直改和 Feature Flag 切换同样适用；
9. 实施完成后更新 VRR、SNP 和 CIR，但不得自动批准 BSL 或 Release；
10. 自动化的幂等性声明必须由实际重复执行或等价证据支持。

### 10.13 验证、接受与关闭

1. Verification Owner 必须使用 C05 的 Verification/Validation/Evidence；
2. 验证输入必须固定实施后 Snapshot 和环境；
3. 必须验证 Change 目标、Non-regression、兼容性、迁移、回滚和监视项；
4. `Implementation Status = Completed` 与 `Verification Status = Pass` 独立记录；
5. 验证失败时 CHG 不得 `Resolved/Closed`，除非 Authority 明确取消并处置残留状态；
6. 验证通过后必须检查 C10 Trace、Coverage、Orphan 和 Untracked Change；
7. 需要基线化时创建并批准后继 BSL；
8. CHG `Resolved` 表示方案已实施并满足解决条件，`Closed` 表示记录、验证、通知和后继项均完成；
9. 新证据推翻结论时 CHG 必须 `Reopened`；
10. 关闭不得删除失败 Attempt、Rejected CHD 或旧 Snapshot。

### 10.14 紧急变更

Emergency Change 仅在以下条件同时满足时允许：

1. 存在正在发生或即将发生的重大业务、安全、隐私、合规、可用性、数据或人身影响；
2. Normal Path 的等待会增加现实损害；
3. 适用的 Emergency Authority、范围和通道已预定义或即时明确；
4. 仍可执行最低限度的身份、授权、备份、影响、验证和记录。

实施前最低信息：

- Emergency CHG ID；
- Trigger、Incident/Risk 和紧急理由；
- 受影响服务、环境和资产；
- 原状态/Snapshot；
- 拟议动作、最大边界和禁止范围；
- Emergency Authority 及批准时间；
- 最低 Impact/Risk；
- 即时验证、监视、回滚和停止条件；
- Implementer 和 Observer。

实施后必须：

1. 固化 C09 Run、Actual Change、VRR 和 SNP；
2. 在 IDP 或 Emergency Policy 规定时限内补全 IMA 和 CHD；
3. 完成独立验证、完整性、追溯和 Drift 检查；
4. 更新 CIR、BSL 和 RLC；
5. 记录未完成项、Residual Risk 和临时控制；
6. 执行 Post-implementation Review；
7. 决定保留、修正、替代或回滚；
8. 向受影响消费方通知；
9. 禁止以“紧急”为由永久豁免补录和验证。

本规范不设虚构的统一补录小时数；具体时限必须由 Approved IDP、Incident Policy 或适用法规按 Risk 定义。

### 10.15 Release Configuration

每次部署、交付、上线、模型发布、数据发布或外部制品发布必须建立 RLC，至少固定：

- Release ID、Version、Environment、Region/Tenant 和 Release Time；
- Requirement、Design、Code、Configuration、Schema、Data、Model、Prompt 和 Policy 的 Asset ID + Revision/SNP；
- Source Repository、Commit/Object ID、Tag 解析结果、Submodule 和 LFS；
- Build ID、Toolchain、Dependency Lock、制品坐标和 Digest；
- Migration、Feature Flag、Runtime Parameter 和 Secret Reference Version；
- Test/Evidence/Coverage、CHG/CHD、BSL、Waiver 和 C12 Gate Decision；
- Deploy Run、Operator、Approval 和实际结果；
- Previous/Target/Rollback Version；
- Rollback/Recovery 前提、数据边界和演练证据；
- 已知差异、Risk、监视和通知；
- 完整性与重建结果。

规则：

1. RLC 记录实际发布，不得只复制计划或候选 Baseline；
2. RLC 必须声明与目标 BSL 的所有差异；
3. 同一 Release ID 在不同环境的实际配置不同必须建立可区分实例；
4. Secret 只记录引用和 Version，不记录明文；
5. 动态配置和 Feature Flag 的发布时状态必须固定；
6. 无法重建任何关键成员时 `Reconstruction Result` 不得为 `Reconstructed`；
7. RLC 创建后禁止原位覆盖；更正使用 Corrected REC；
8. Release Authority 必须在 C12 消费 RLC，不得由 C11 自动批准上线。

### 10.16 Drift 与无来源变化

Drift 检查至少比较：

- CIR 当前 Revision 与实际对象；
- 当前环境与 RLC；
- BSL 成员与仓库/制品库解析结果；
- Dependency Lock 与实际依赖；
- Schema/Migration 与数据库实际状态；
- Feature Flag/Runtime Config 与声明值；
- Model/Data/Prompt Version 与运行引用；
- Evidence、Approval 和 Waiver 有效性。

处置规则：

1. Drift 必须记录实际值、声明值、检测时间、范围和证据；
2. 未授权 Drift 进入 C10 UCR 和 CHG/Incident；
3. 禁止直接修改 CIR、BSL 或 RLC 使其“匹配”未经授权的实际状态；
4. 先判断隔离、停止、回滚、修复或受控追认；
5. 追认必须保留 Drift 起始时间、违规窗口和影响；
6. 自动 Drift Remediation 只在预授权范围内执行，超界必须停止。

### 10.17 替代、退役、归档与处置

1. 替代或退役必须创建 SRR；
2. 旧 Asset ID、Revision、Snapshot、Baseline、Change、Decision 和 Release 历史必须保留；
3. 新对象必须通过 `supersedes` 或 `replaces` 明确关系和生效范围；
4. 无替代对象时必须记录 `No Replacement`、影响和消费方迁移；
5. 退役前必须识别当前消费方、接口、数据、保留、法律冻结和恢复需求；
6. 删除物理载体前必须取得 E04 Retention/Disposition 授权；
7. 归档位置、访问权限、Integrity 和读取工具必须记录；
8. 退役不得导致已发布 Release 无法审计；
9. Retired ID 禁止复用；
10. 已退役资产恢复使用必须创建新 CHG/CHD 和适用 Revision，不得直接改回旧状态。

### 10.18 恢复与回滚

1. Recovery 必须指定 Source SNP/BSL/RLC、Target、Purpose、Authority 和隔离边界；
2. 读取历史内容不改变历史对象 State；
3. 恢复到生产或当前工作空间属于新 Change；
4. Rollback 必须记录目标版本、实际动作、数据影响、外部副作用和验证；
5. 代码回滚不自动回滚 Schema、Data、消息、缓存、Secret、第三方调用或用户行为；
6. 不可逆迁移必须具有向前修复或补偿策略；
7. 恢复结果必须校验 Integrity、可读性、依赖和可执行性；
8. 恢复失败必须保留 Attempt 并进入 Incident/Risk；
9. 定期恢复测试的频率由 Risk、RTO/RPO、Retention Rule 和 E05 决定。

### 10.19 状态记账与配置审核

Configuration Status Accounting 必须能够回答：

- 当前有哪些 CI、Owner、Revision、State 和位置；
- 每个 CI 属于哪些 Baseline 和 Release；
- 某 Revision 由哪个 CHG、CHD、Run 和 Evidence 产生；
- 当前 Open/Blocked/Reopened CHG 有哪些；
- 哪些 BSL 已批准、条件批准、替代或过期；
- 哪些 Snapshot 或 Release 无法完整性校验或重建；
- 哪些资产已替代、退役、归档或处于法律冻结；
- 哪些 Drift、UCR、Unknown、Waiver 和 Residual Risk 未关闭。

配置审核必须包括：

1. Identification Audit：标识唯一、不复用、映射和别名；
2. Functional Configuration Audit：功能、Requirement 和 Verification 一致；
3. Physical Configuration Audit：实际构成、Version、制品和记录一致；
4. Baseline Audit：成员、Approval、Integrity、不可变和后继关系；
5. Change Audit：分类、IMA、CHD、Run、验证和关闭；
6. Release Reconstruction Audit：RLC 的完整性和重建能力；
7. Records Audit：元数据、访问、保留、更正、归档和处置；
8. Automation Audit：Agent/工具权限、规则版本、日志和人工复核。

审核发现必须进入 C12 Review Record、CHG、Risk、Incident 或 UCR；禁止在 C11 创建平行 Review 产物。

### 10.20 Coding Agent 与自动化边界

Agent 可以：

- 识别候选 CI、重复 ID、缺失字段、Drift 和无来源变化；
- 起草 IDP、CIR、IMA、CHG、BSL、CHD、RLC 和 SRR；
- 解析 Commit、Digest、Dependency、Diff 和环境元数据；
- 在 C07 Authorization 与 C09 Run 范围内执行版本、快照、构建、迁移和回滚命令；
- 生成状态记账、完整性、重建和符合性检查结果；
- 提出 Change 分类、影响候选和风险候选。

Agent 禁止：

- 自行批准 IDP、BSL、CHD、Risk Acceptance 或 Release；
- 把概率推断写成事实；
- 将 Branch、HEAD、`latest`、文件路径或版本号当作永久身份；
- 覆盖 Approved BSL、已发布 Version 或 Recorded RLC；
- 擅自扩大资产、命令、权限、环境或时间边界；
- 删除失败、拒绝、替代、退役或更正历史；
- 在未验证时声明兼容、可回滚、已重建或已通过；
- 读取或写出 Secret 明文；
- 因工具成功而自动写入业务批准状态。

## 11. 状态模型

### 11.1 DOC State：IDP、CIR、IMA

```text
Draft → In Review → Approved → Baselined
                 ↘ Changes Required → Draft
                 ↘ Rejected
Approved/Baselined → Superseded → Retired
```

规则：

1. `Approved` 表示有权角色批准内容；
2. `Baselined` 表示该 Revision 已纳入 Approved BSL；
3. IMA 的 `Baselined` 只表示分析 Revision 被固定，不表示 Change 已批准；
4. `Changes Required` 必须返回 Draft 形成新 Revision；
5. `Superseded/Retired` 不删除历史。

### 11.2 CASE State：CHG

```text
Open → In Progress → Resolved → Closed
          ↕ Blocked       ↘ Reopened → In Progress
Open/In Progress/Blocked → Cancelled
```

规则：

1. `Open` 表示已登记，未完成分流；
2. `In Progress` 可包含分析、决定等待、实施或验证，但领域状态必须分别记录；
3. `Blocked` 必须记录阻断项、Owner 和解除条件；
4. `Resolved` 必须有处置结果和验证结论；
5. `Closed` 必须完成记录、通知和后继项；
6. `Reopened` 保留原关闭历史；
7. `Cancelled` 不得掩盖已发生的实际变化。

### 11.3 DEC State：BSL、CHD

```text
Proposed → Under Review → Approved
                       ↘ Conditionally Approved
                       ↘ Rejected
                       ↘ Waived
Approved/Conditionally Approved → Superseded
任何有期限的有效决定 → Expired
```

规则：

1. BSL 一般禁止使用 `Waived`；只有上位政策明确允许跳过某候选基线决定时才可使用，且不得把未批准集合视为 Baseline；
2. CHD `Waived` 仅表示适用 Authority 明确豁免某项变更控制义务，不等于 Approve Change；
3. `Conditionally Approved` 条件必须可验证、有 Owner 和期限；
4. `Expired` 不得自动恢复为有效；
5. 后继决定使用新 DEC 并建立 `supersedes`。

### 11.4 REC State：VRR、SNP、RLC、SRR

```text
Recorded → Corrected → Superseded → Archived
```

规则：

1. REC 记录已发生事实，创建时不得预写未来完成结果；
2. `Corrected` 必须保留原值、更正值、原因、时间和责任人；
3. `Superseded` 表示有更完整或后继记录，不否定原事实；
4. `Archived` 只改变活跃存储或访问层，不删除记录；
5. 禁止使用 REC State 表达审批。

## 12. 产物进入、退出与质量条件

| 产物 | 创建触发 | 进入有效使用的条件 | 退出当前有效集合 |
|---|---|---|---|
| IDP | 产品初始化或标识规则变化 | Approved；范围、命名空间、分配、不复用、迁移明确 | 被新 IDP Superseded |
| CIR | 首个 CI 识别 | Approved；成员可解析、Owner 和当前 Revision 完整 | 被新 CIR Revision 替代；登记仍保留 |
| VRR | 同一资产内容/版本变化 | Recorded；Old/New、原因、作者、时间、实际引用完整 | 被更正/后继记录替代 |
| SNP | 需固定时点状态 | Recorded；位置、范围、Digest、不可变和可访问性通过 | 被后继 Snapshot 替代但永久保留 |
| BSL | 需批准资产集合 | Approved；成员、Integrity、Authority、生效完整 | Superseded/Expired |
| CHG | 已批准/基线资产变化 | Open；提议者、原因、触发、原/拟状态和 Owner 完整 | Closed/Cancelled，历史保留 |
| IMA | Change 进入决定前 | Approved；范围、全链路影响、Risk、Unknown、推荐完整 | Change/输入变化后 Superseded |
| CHD | Change 需要授权处置 | Approved/Conditionally Approved；范围、条件、Authority 完整 | Superseded/Expired |
| RLC | 实际发布或部署 | Recorded；实际构成、Digest、Evidence、Approval、Rollback 完整 | 被更正/后继 Release 替代 |
| SRR | 替代或退役生效 | Recorded；旧对象、替代、原因、范围、迁移、保留、通知完整 | 被更正/后继处置记录替代 |

## 13. 必填信息规范

十类正式产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C11 类型专属要求。

### 13.1 IDP — Identifier Policy

必须包含：

- Policy ID、Title、Revision、State、Owner、Approver；
- Scope、Namespace 和 Artifact Type Code；
- ID Syntax、Sequence Assignment 和 Collision Handling；
- Uniqueness Boundary；
- No-reuse Rule；
- Retired/Voided ID Handling；
- Alias、External ID 和 Tool Mapping；
- Split、Merge、Migration 和 Import Rule；
- Version/Revision Scheme by Asset Type；
- Snapshot/Baseline/Release ID Rule；
- Responsibility、Access、Retention、Effective Time；
- Previous Policy、Change 和 Approval。

### 13.2 CIR — Configuration Item Register

每个成员必须包含：

- CI/Asset ID、Type、Name；
- Authoritative Location；
- Owner；
- Current Revision/Version；
- Formal State；
- CI Member Status；
- Current Snapshot；
- Baseline Membership；
- Repository/System/Environment；
- Access Classification；
- Retention Classification；
- Integrity Status；
- Upstream/Downstream Reference；
- Last Change、Last Verification、Last Updated。

### 13.3 VRR — Version or Revision Record

必须包含：

- Record ID；
- Asset ID；
- Old Version/Revision；
- New Version/Revision；
- Change Summary；
- Reason 和 Classification；
- Author/Implementer；
- Occurred Time；
- CHG/CHD；
- Approval 或适用预授权；
- C09 Run、Actual Diff、Commit/Artifact；
- Previous/New Snapshot；
- Compatibility Impact；
- Verification Reference；
- Correction/Supersession Reference。

### 13.4 SNP — Snapshot Record

必须包含：

- Snapshot ID；
- Asset ID 和 Revision/Version；
- Capture Time；
- Content Location；
- Repository/System Identity；
- Capture Scope 和 Exclusion；
- Integrity Algorithm、Digest、Result；
- Creator/Tool/Run；
- Commit/Object/Artifact/Data/Model Reference；
- Untracked/Dirty/Submodule/LFS/External Dependency 状态；
- Immutability Control；
- Access 和 Retention；
- Related VRR、BSL、CHG、RLC；
- Recovery Test 和可访问性状态。

### 13.5 BSL — Baseline Record

必须包含：

- Baseline ID；
- Purpose、Type、Scope；
- Included Asset ID、Version/Revision、Snapshot/Digest；
- Exclusion、Unknown 和已知差异；
- Dependency、Constraint、Risk、Waiver；
- Approver/Baseline Authority；
- Decision State；
- Approval 和 Effective Time；
- Integrity/Resolution Result；
- Applicable Product/Environment；
- Previous Baseline；
- Successor Baseline；
- Supersession/Expiry；
- Change/Review/Evidence。

### 13.6 CHG — Change Request

必须包含：

- Change ID；
- Proposer；
- Reason；
- Trigger；
- Change Path；
- C04 Classification；
- Affected Assets；
- Original State/Revision/Baseline；
- Proposed State/Revision；
- Scope 和 Non-scope；
- Impact Analysis；
- Risk/Unknown；
- Planned Version/Baseline；
- Owner；
- Approver/Authority；
- Decision；
- Implementation Status；
- Verification Status；
- Planned/Actual Time；
- Requirement/Defect/Incident/Run/Evidence；
- Closure、Residual Item 和通知。

### 13.7 IMA — Impact Analysis

必须包含：

- Analysis ID、CHG、Revision、State；
- Analyst、Reviewer、Analysis Time、Validity；
- Scope、Context、Criteria 和 Input Snapshot；
- C10 Impact Query；
- affected Need/Requirement/Design/Code/Test/Release/Context；
- Interface、Compatibility、Migration、Data 和 Operations；
- Security/Privacy/Compliance/Safety；
- Risk、Cost、Timing、Resource；
- Assumption、Unknown、Exclusion 和 Confidence；
- Alternative、No-change Impact；
- Recommendation；
- Evidence 和 Required Follow-up。

### 13.8 CHD — Change Decision

必须包含：

- Decision ID、CHG、IMA；
- Candidate Dispositions；
- Decision Outcome 和 DEC State；
- Rationale；
- Conditions；
- Risk/Residual Risk/Acceptance；
- Authority、Participants、Decision Time；
- Authorized Asset/Command/Environment/Window；
- Planned Baseline/Version；
- Verification/Rollback/Monitoring/Stop；
- Effective/Expiry；
- Supersedes/Replaces；
- Follow-up Owner。

### 13.9 RLC — Release Configuration Record

必须包含：

- RLC ID、Release ID/Version、Product；
- Environment、Region/Tenant；
- Requirement/Design/Code/Configuration/Evidence Version；
- Repository、Commit/Object、Tag Resolution；
- Build/Artifact/Toolchain/Dependency/Digest；
- Schema/Migration/Data/Model/Prompt；
- Runtime Config/Feature Flag/Secret Reference；
- BSL、CHG、CHD、Waiver、C12 Decision；
- Deploy Run、Approval、Deploy Time、Operator；
- Previous/Target/Rollback Version；
- Verification、Monitoring 和 Notification；
- Integrity Result；
- Reconstruction Result；
- Actual Difference 和 Residual Risk。

### 13.10 SRR — Supersession and Retirement Record

必须包含：

- Record ID；
- Old Asset/Revision/Baseline/Release；
- Replacement 或 No Replacement；
- Relationship；
- Reason；
- Effective Scope/Time；
- Migration/Consumer Impact；
- Retention Location/Rule；
- Integrity 和 Access；
- Approver；
- Downstream Notifications；
- Recovery Conditions；
- Data/Secret/License/Legal Hold 处置；
- Related CHG/CHD/BSL/RLC；
- Correction/Supersession。

## 14. 质量标准

### 14.1 身份质量

- 100% 正式 CI 拥有唯一 Asset ID；
- 0 个 Asset ID 含 Version、State、日期或 Owner；
- 0 个 Retired/Voided ID 被复用；
- 100% 外部 ID 和工具键可映射到 Asset ID；
- Split/Merge/Migration 不丢失原身份和关系。

### 14.2 Revision 与 Snapshot 质量

- 每次受控内容变化都有 VRR；
- Old/New Revision 均可解析；
- 用于 Baseline/Release 的 Snapshot 均不可变且 Integrity Pass；
- Branch/HEAD/路径不作为唯一 Snapshot 定位；
- Exclusion、Unknown、外部依赖和未跟踪状态明确。

### 14.3 Baseline 质量

- Approved BSL 成员 100% 固定到 Asset ID + Revision + Snapshot；
- 0 个 Approved BSL 被原位覆盖；
- 成员、批准、生效和完整性全部可验证；
- 后继 BSL 保留前序和差异；
- Baseline 与 Release 不混同。

### 14.4 Change 质量

- 100% 已批准/基线资产的受控变化有合规来源；
- 100% Normal Change 在实施前有有效 IMA 和 CHD；
- 100% Change 通过 C04 分类；
- Patch、Defect Fix、Refactor 不误建为新 Requirement；
- 超范围变化为 0；若发生则全部 Stop、记录和处置；
- Implementation、Verification、Closure 三者不混同。

### 14.5 Release 与恢复质量

- 每次实际 Release 有唯一 RLC；
- 关键成员 100% 可解析并校验；
- 实际 Release 与 BSL 差异 100% 披露；
- Rollback/Recovery 前提、数据边界和验证明确；
- 无法重建时禁止标记 `Reconstructed`。

### 14.6 记录与审计质量

- 所有更正保留原值和更正链；
- 所有替代、退役和归档保留身份、关系、有效时间和访问；
- 状态记账可回答当前与历史配置；
- Agent/自动化活动可追到规则版本、授权、Run 和人工复核；
- E04 元数据、访问、保留和处置字段完整。

## 15. 评审、批准与阻断

### 15.1 Configuration Ready

进入首次 Baseline 前必须满足：

- IDP Approved；
- CIR Approved；
- 角色和 Authority 明确；
- 所有必需 CI 已登记；
- 当前 Revision 和 SNP 可解析；
- Version/Revision Scheme 明确；
- Snapshot、Integrity、Retention 和 Recovery 规则有效；
- Open 身份冲突、复用、关键 Unknown 为 0；
- E04 接口已实现；
- 配置审核通过或发现已受控处置。

### 15.2 Change Ready

Normal Change 实施前必须满足：

- CHG Open/In Progress 且字段完整；
- C04 Classification 已确认；
- IMA Approved 且未过期；
- C10 Impact Query 可接受；
- CHD Approved/Conditionally Approved；
- 条件、权限、范围、时间窗和 Stop 明确；
- 输入 BSL/SNP Integrity Pass；
- C09 Run Plan、C05 Verification、Rollback/Recovery 可执行；
- 所需 E01 至 E05 Owner 已参与；
- Blocking Risk、Unknown、Dependency 已处置。

### 15.3 Baseline Ready

BSL 批准前必须满足：

- Scope 与 Purpose 明确；
- 成员可解析且无重复冲突；
- 每个成员固定 Revision/SNP/Digest；
- 所需资产本身已批准；
- 关键 Trace、Evidence 和 Change 完整；
- Integrity 与重建检查通过；
- Exclusion、Unknown、Risk、Waiver 已披露；
- Authority 与 Effective Time 明确。

### 15.4 Release Configuration Ready

RLC 供 C12 Gate 使用前必须满足：

- 实际构成已记录；
- 构建、制品、依赖、配置、迁移、数据、模型和环境可解析；
- 与 BSL 差异已列明；
- CHG/CHD/C05 Evidence/C10 Trace 完整；
- Rollback/Recovery 与监视可执行；
- Secret 未泄露；
- Integrity Pass；
- Reconstruction Result 与证据一致；
- Release Authority 尚未决定时不得标记已发布批准。

### 15.5 强制阻断

出现以下任一情形必须阻断 Baseline、Change 实施或 Release：

1. Asset ID 冲突、复用或无法解析；
2. Approved BSL 被修改或成员漂移；
3. 输入 Snapshot Integrity Fail；
4. Normal Change 无有效 IMA/CHD；
5. 实际范围超出授权；
6. 关键影响为 Unknown 且无有权 Risk Acceptance；
7. Breaking Change 无迁移、通知或验证；
8. Emergency Change 无 Authority、原状态或即时回滚边界；
9. Release 关键配置、Evidence 或 Gate Decision 缺失；
10. RLC 声称可重建但关键成员不可获取；
11. Agent 试图自批或写入超权状态；
12. Secret 明文进入受控记录；
13. 无来源 Drift、UCR 或实际变更未处置；
14. 法律冻结、Retention 或处置约束被违反。

## 16. 规范本身的变更、审计与保留

1. 本规范批准后自身成为 C11 管理的 Configuration Item；
2. 对本规范的修改必须创建 VRR、SNP，并在已基线化后创建 CHG；
3. 修改正式产物名称、状态模型、必填字段、Authority、阻断规则或国际标准映射属于重大 Revision；
4. 只修正错别字且不改变语义可按 Clarification/Patch 处理，但仍保留 Revision 记录；
5. 本规范的 Approved BSL 禁止原位覆盖；
6. 审计记录放入 `06_报告与审计`，不得与正式规范同级；
7. 保留、访问、更正、归档和处置遵循 E04；
8. 标准版本更新必须触发适用性复评和 IMA；
9. 本规范被后继版本替代时必须保留旧文件、Asset ID、Revision、批准和映射历史。

## 17. P2 裁剪与扩展规范适用性

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C11 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

C11 对任何配置项 Revision、Snapshot、Baseline、Change、Release、Supersession 或 Retirement 生效。IDP、CIR 和既有 Baseline 未变化时 `Reference`；VRR、SNP、RLC、SRR 按实际事件记录；CHG、IMA、CHD 只在已批准/基线化资产变更或规则触发时建立。

Normal 与 Emergency 共享永久 ID、实际变更、验证和人类 Authority。Emergency 只允许先执行恢复服务或控制损害所必需的动作，必须在恢复后补齐 CHG/IMA/CHD、RUN、Evidence、Risk 和 Review；不得自动批准 BSL 或 Release。

### 17.1 P2 必须保留

P2 必须：

- 保留全部 10 类正式产物；
- 保留公共状态模型；
- 保留永久 ID、Revision、Snapshot、Baseline 和 Change Decision；
- 保留 C04 分类、C07 Authority、C09 Run、C10 Trace 和 C12 Gate 接口；
- 为每类产物提供独立模板和可导出记录；
- 执行本规范第 19 章所有 P2 Mandatory Check；
- 保留 Normal、Pre-authorized Standard、Emergency 三种路径的受控边界。

P2 可以：

- 在同一 Git 仓库、文档系统或工单平台承载多个产物；
- 由自动化生成 CIR、VRR、SNP、RLC 和状态记账；
- 对 Low Risk 标准变更使用预授权模型；
- 对同类 CI 采用共享 Version Scheme。

P2 禁止：

- 合并身份导致无法区分 CHG、IMA、CHD、BSL 和 RLC；
- 以 Git 历史替代 Change Decision；
- 以一张 Change Register 省略独立字段和状态；
- 省略业务 ID、Baseline Approval、Release Configuration 或历史保留。

### 17.2 E01 架构扩展

当前项目未激活 E01，但涉及以下事项必须重新评估：

- Architecture Baseline、ADR、Interface 和 Dependency；
- Breaking Architecture Change；
- 跨系统、跨仓库和跨团队配置；
- 技术债、弃用和架构退役。

激活后由 E01 增加架构专属字段，不改变 C11 身份、状态和 Change 主链。

### 17.3 E02 安全、隐私与合规扩展

当前项目未激活 E02，但以下 Change 必须触发适用性复评：

- 身份、权限、加密、Secret、日志、审计；
- 个人信息、跨境、保留、删除和同意；
- 漏洞、威胁模型、供应链和合规控制；
- Emergency Security Change。

Secret 只记录 Reference 和 Version，禁止写入 C11 正文或模板实例。

### 17.4 E03 数据与 AI 数据扩展

当前项目未激活 E03，但以下资产必须触发复评：

- Dataset、Schema、Label、Feature、Model、Prompt 和评测集；
- 数据血缘、训练/推理配置、模型权重；
- 不可逆迁移、删除、偏差和再训练；
- 数据或模型 Release。

激活后 E03 增加数据/模型专属 Snapshot 和质量证据，不替代 C11 RLC。

### 17.5 E04 知识与记录扩展

E04 当前激活。C11 必须：

- 为所有产物提供 Record Metadata；
- 记录 Classification、Access、Retention、Disposition 和 Legal Hold；
- 保留原始 Record、更正链、替代和退役历史；
- 维护权威位置、格式、读取工具和迁移信息；
- 在归档或处置前验证 Integrity、可读性和 Authority；
- 禁止因仓库清理、工具迁移或人员离开丢失批准历史。

### 17.6 E05 运维扩展

当前项目未激活 E05，但以下事项必须触发复评：

- 生产环境、部署、Feature Flag、运行配置和 Drift；
- Incident、Emergency Change、Rollback、Recovery；
- RTO/RPO、备份、监视、容量和服务退役；
- 多区域、多租户和运行时差异。

激活后 E05 增加运行专属控制，不改变 CHG、RLC 和 SRR 主身份。

## 18. 上下游交接

| 来源/去向 | C11 接收 | C11 输出 |
|---|---|---|
| C01 | Need、Intent、Goal Revision | 配置身份、Baseline、Change 影响 |
| C02 | Scope、Risk、Constraint、Dependency、边界 | Change Scope、Risk、受控配置 |
| C03 | PRD、Feature、Release Intent | PRD/Feature Revision、Release Configuration 输入 |
| C04 | Requirement ID、Revision、分类规则 | Requirement Baseline、Change、Supersession |
| C05 | Verification/Validation/Evidence | 验证状态、Evidence Version、Release Evidence |
| C06 | Design、Architecture、Interface、Schema | Design Revision、Baseline、Change |
| C07 | Role、Authority、Authorization、Stop | Baseline/Change Authority、Agent 边界事实 |
| C08 | Context、Fingerprint、Source Version | Snapshot/Baseline/Configuration State |
| C09 | Run、Command、Actual Diff、Commit、Artifact、Validation | 批准输入、计划范围、End Snapshot、VRR |
| C10 | Trace、Impact Query、UCR、Lineage | Asset、Revision、Snapshot、Baseline、Change、RLC |
| C12 | Review、Gate、Waiver、Risk Acceptance、Release Decision | Configuration Ready、RLC、Drift、审计证据 |
| E01 | 架构配置与演进要求 | Architecture Baseline/Change 接口 |
| E02 | 安全、隐私、合规要求 | Security Configuration/Change 接口 |
| E03 | 数据、模型、提示词要求 | Data/Model Snapshot/Release 接口 |
| E04 | 元数据、访问、保留、处置规则 | 全部 C11 Record 与历史 |
| E05 | 部署、运行、Incident、Recovery 要求 | Release/Runtime Configuration 接口 |

### 18.1 交接不变量

1. 上游业务资产的身份和语义仍由所属规范管理；
2. C11 为其分配配置身份和 Revision，不改变其业务审批；
3. C10 Link 固定端点 Revision，但不复制 C11 版本事实；
4. C09 记录实际执行，C11 记录批准配置与版本事实；
5. C12 作 Gate/Release Decision，C11 只提供可审计配置证据；
6. E04 管理记录生命周期，C11 不建立平行保留体系。

## 19. P2 强制检查

| 检查编号 | 检查项 | 通过条件 |
|---|---|---|
| C11-P2-001 | IDP 存在 | Approved 且可解析 |
| C11-P2-002 | 命名空间明确 | 范围和 Authority 已定义 |
| C11-P2-003 | Asset ID 唯一 | 无重复 |
| C11-P2-004 | ID 不含可变信息 | 无 Version/日期/State/Owner |
| C11-P2-005 | ID 不复用 | Retired/Voided ID 未重用 |
| C11-P2-006 | 工具映射完整 | 外部键可回到 Asset ID |
| C11-P2-007 | CIR 存在 | Approved 且成员可导出 |
| C11-P2-008 | CI 范围完整 | 必需资产无漏登记 |
| C11-P2-009 | CI Owner 完整 | 无无主正式 CI |
| C11-P2-010 | Current Revision 可解析 | 100% 可访问 |
| C11-P2-011 | State 合规 | 只用公共状态 |
| C11-P2-012 | 领域值未冒充 State | 全部字段分离 |
| C11-P2-013 | Version Scheme 明确 | 每类 CI 有规则 |
| C11-P2-014 | SemVer 适用正确 | 仅声明公共 API 时采用 |
| C11-P2-015 | 已发布版本不可改写 | 无原位内容变化 |
| C11-P2-016 | VRR 完整 | 每次受控变化有记录 |
| C11-P2-017 | Old/New 可解析 | 无悬空 Revision |
| C11-P2-018 | 实际变化可追 | 有 C09 Diff/Commit/Artifact |
| C11-P2-019 | SNP 不可变 | 有不可变控制 |
| C11-P2-020 | SNP 完整性 | Algorithm、Scope、Digest 完整 |
| C11-P2-021 | 可变引用未冒充快照 | Branch/HEAD/latest 非唯一定位 |
| C11-P2-022 | 外部状态披露 | Exclusion/Unknown 完整 |
| C11-P2-023 | BSL 成员固定 | Asset + Revision + SNP |
| C11-P2-024 | BSL Authority | Approver 与时间完整 |
| C11-P2-025 | BSL 不可覆盖 | 无原位修改 |
| C11-P2-026 | BSL 后继关系 | Supersession 可追 |
| C11-P2-027 | Baseline/Release 分离 | 无状态混同 |
| C11-P2-028 | CHG 必填信息 | 蓝图字段全部存在 |
| C11-P2-029 | C04 分类 | 每项 Change 已分类 |
| C11-P2-030 | Patch 处理正确 | 未错误创建新 Requirement |
| C11-P2-031 | Defect Fix 处理正确 | 有 Defect 来源 |
| C11-P2-032 | Refactor 处理正确 | 无虚构产品 Requirement |
| C11-P2-033 | IMA 范围完整 | 全链路域已检查 |
| C11-P2-034 | C10 Impact Query | 参数、结果、完整性固定 |
| C11-P2-035 | Unknown 披露 | 无静默未知项 |
| C11-P2-036 | 兼容性有证据 | 非版本号推断 |
| C11-P2-037 | CHD 存在 | Normal Change 事前批准 |
| C11-P2-038 | Authority 有效 | 范围和时间未超权 |
| C11-P2-039 | 职责分离 | 高风险场景符合 C07 |
| C11-P2-040 | Agent 未自批 | 无自动越权状态写入 |
| C11-P2-041 | 实施输入固定 | BSL/SNP Integrity Pass |
| C11-P2-042 | 实际范围一致 | 无未处置超范围变化 |
| C11-P2-043 | 实施/验证分离 | 两个字段独立 |
| C11-P2-044 | 关闭条件完整 | 记录、验证、通知完成 |
| C11-P2-045 | 紧急授权 | Emergency Authority 可追 |
| C11-P2-046 | 紧急最低记录 | 原状态、动作、验证、回滚完整 |
| C11-P2-047 | 紧急事后补录 | IMA/CHD/Review 按政策完成 |
| C11-P2-048 | 每次 Release 有 RLC | 无缺失 |
| C11-P2-049 | RLC 实际构成 | 非计划配置复制 |
| C11-P2-050 | 发布可重建 | 关键资产与工具可获取 |
| C11-P2-051 | BSL 差异披露 | 全部差异有来源 |
| C11-P2-052 | Secret 安全 | 无明文 |
| C11-P2-053 | Drift 检查 | 声明与实际已比较 |
| C11-P2-054 | 无来源变化处置 | UCR/CHG/Incident 可追 |
| C11-P2-055 | SRR 完整 | 替代/退役事实完整 |
| C11-P2-056 | 旧身份保留 | 无删除或复用 |
| C11-P2-057 | Recovery 受控 | Source、Target、Authority 完整 |
| C11-P2-058 | Rollback 已验证 | 覆盖数据和外部副作用 |
| C11-P2-059 | 状态记账可回答 | 当前与历史配置可查询 |
| C11-P2-060 | 配置审核 | 身份、功能、物理、基线、发布已检查 |
| C11-P2-061 | E04 元数据 | Access/Retention/Disposition 完整 |
| C11-P2-062 | 更正链完整 | 原值、原因、责任保留 |
| C11-P2-063 | 扩展适用性复评 | E01/E02/E03/E05 触发器已检查 |
| C11-P2-064 | 国际标准映射 | 第 20.18 节完整 |

任何 `Fail` 必须生成明确 Finding、Owner、处置期限和阻断结论；禁止只给总分。

## 20. 模板、清单与国际标准条款映射

### 20.1 通用产物头

```yaml
artifact_id: ""
artifact_type: ""
title: ""
revision: ""
formal_state: ""
owner: ""
approver_or_authority: ""
created_at: ""
updated_at: ""
effective_at: ""
supersedes: []
related_assets: []
access_classification: ""
retention_classification: ""
source_snapshot: ""
change_id: ""
```

### 20.2 IDP 模板

```yaml
identifier_policy:
  policy_id: "IDP-0001"
  revision: "R1"
  formal_state: "Draft"
  scope: ""
  namespaces:
    - namespace: ""
      uniqueness_boundary: ""
      authority: ""
  artifact_type_codes: []
  id_syntax: "<artifact_type_code>-<sequence>"
  assignment_rule: ""
  collision_rule: ""
  no_reuse_rule: "Retired and voided IDs MUST NOT be reused."
  retired_id_handling: ""
  alias_and_external_id_mapping: ""
  split_merge_rule: ""
  migration_rule: ""
  version_schemes:
    - asset_type: ""
      scheme: ""
      public_api_declared: false
      semver_adopted: false
  snapshot_id_rule: ""
  baseline_id_rule: ""
  release_id_rule: ""
  owner: ""
  approver: ""
  effective_at: ""
```

### 20.3 CIR 模板

```yaml
configuration_item_register:
  register_id: "CIR-0001"
  revision: "R1"
  formal_state: "Draft"
  items:
    - asset_id: ""
      asset_type: ""
      name: ""
      authoritative_location: ""
      owner: ""
      current_revision: ""
      formal_state: ""
      ci_member_status: "Registered"
      current_snapshot: ""
      baselines: []
      repository_or_system: ""
      environment: ""
      access_classification: ""
      retention_classification: ""
      integrity_result: "Not Verified"
      last_change: ""
      last_verified_at: ""
```

### 20.4 VRR 模板

```yaml
version_or_revision_record:
  record_id: "VRR-0001"
  formal_state: "Recorded"
  asset_id: ""
  old_revision: ""
  new_revision: ""
  old_version: ""
  new_version: ""
  change_summary: ""
  reason: ""
  change_classification: ""
  author_or_implementer: ""
  occurred_at: ""
  change_id: ""
  change_decision_id: ""
  approval_or_preauthorization: ""
  run_id: ""
  actual_diff: ""
  commit_or_artifact: ""
  previous_snapshot: ""
  new_snapshot: ""
  compatibility_impact: "Unknown"
  verification_reference: ""
```

### 20.5 SNP 模板

```yaml
snapshot_record:
  snapshot_id: "SNP-0001"
  formal_state: "Recorded"
  asset_id: ""
  revision_or_version: ""
  captured_at: ""
  creator: ""
  content_location: ""
  repository_or_system_identity: ""
  capture_scope: []
  exclusions: []
  integrity:
    algorithm: ""
    digest: ""
    result: "Not Verified"
  commit_or_object_id: ""
  dirty_state: ""
  untracked_state: ""
  submodule_state: ""
  lfs_state: ""
  external_dependencies: []
  immutability_control: ""
  access_classification: ""
  retention_classification: ""
  recovery_test: ""
```

### 20.6 BSL 模板

```yaml
baseline_record:
  baseline_id: "BSL-0001"
  formal_state: "Proposed"
  purpose: ""
  baseline_type: ""
  scope: ""
  included_assets:
    - asset_id: ""
      revision_or_version: ""
      snapshot_id: ""
      digest: ""
  exclusions: []
  unknowns: []
  dependencies: []
  risks: []
  waivers: []
  approver: ""
  approval_at: ""
  effective_at: ""
  integrity_result: "Not Verified"
  applicable_product_or_environment: ""
  previous_baseline: ""
  successor_baseline: ""
```

### 20.7 CHG 模板

```yaml
change_request:
  change_id: "CHG-0001"
  formal_state: "Open"
  proposer: ""
  reason: ""
  trigger: ""
  change_path: "Normal"
  change_classification: ""
  affected_assets: []
  original_state:
    revisions: []
    baseline: ""
    snapshot: ""
  proposed_state:
    revisions: []
    baseline: ""
  scope: []
  non_scope: []
  impact_analysis_id: ""
  risks: []
  unknowns: []
  planned_version: ""
  planned_baseline: ""
  owner: ""
  approver_or_authority: ""
  decision_id: ""
  implementation_status: "Not Started"
  verification_status: "Not Started"
  related_requirement_defect_incident: []
  run_ids: []
  evidence: []
  closure: ""
```

### 20.8 IMA 模板

```yaml
impact_analysis:
  analysis_id: "IMA-0001"
  revision: "R1"
  formal_state: "Draft"
  change_id: ""
  analyst: ""
  reviewer: ""
  analyzed_at: ""
  valid_until_or_condition: ""
  scope: ""
  context: ""
  criteria: []
  input_snapshot: ""
  impact_query:
    query_id: ""
    completeness: ""
  affected:
    needs: []
    requirements: []
    designs: []
    code: []
    tests: []
    releases: []
    contexts: []
  compatibility_impact: "Unknown"
  migration: ""
  security_privacy_compliance: ""
  risks: []
  cost_and_timing: ""
  assumptions: []
  unknowns: []
  exclusions: []
  alternatives: []
  no_change_impact: ""
  recommendation: ""
  evidence: []
```

### 20.9 CHD 模板

```yaml
change_decision:
  decision_id: "CHD-0001"
  formal_state: "Proposed"
  change_id: ""
  impact_analysis_id: ""
  candidate_dispositions: []
  decision_outcome: ""
  rationale: ""
  conditions: []
  risks: []
  residual_risk: ""
  risk_acceptance: ""
  authority: ""
  participants: []
  decided_at: ""
  authorized_assets: []
  authorized_commands: []
  authorized_environments: []
  authorized_window: ""
  planned_version: ""
  planned_baseline: ""
  verification_plan: ""
  rollback_plan: ""
  monitoring_plan: ""
  stop_conditions: []
  effective_at: ""
  expires_at: ""
  supersedes: ""
```

### 20.10 RLC 模板

```yaml
release_configuration_record:
  rlc_id: "RLC-0001"
  formal_state: "Recorded"
  release_id: ""
  release_version: ""
  product: ""
  environment: ""
  region_or_tenant: ""
  released_at: ""
  asset_versions:
    requirements: []
    designs: []
    code: []
    configurations: []
    evidence: []
  source:
    repositories: []
    commits_or_objects: []
    resolved_tags: []
    submodules: []
    lfs_objects: []
  build:
    build_id: ""
    toolchain: []
    dependency_locks: []
    artifacts_and_digests: []
  runtime:
    schemas_and_migrations: []
    data_and_models: []
    prompts_and_policies: []
    feature_flags: []
    secret_references: []
  governance:
    baselines: []
    changes: []
    decisions: []
    waivers: []
    gate_decision: ""
  deployment:
    run_id: ""
    operator: ""
    approval: ""
    actual_result: ""
  rollback:
    previous_version: ""
    rollback_version: ""
    prerequisites: []
    data_boundaries: []
    evidence: []
  integrity_result: "Not Verified"
  reconstruction_result: "Not Reconstructable"
  actual_differences: []
  residual_risks: []
```

### 20.11 SRR 模板

```yaml
supersession_and_retirement_record:
  record_id: "SRR-0001"
  formal_state: "Recorded"
  old_asset: ""
  old_revision_baseline_or_release: ""
  replacement: ""
  no_replacement: false
  relationship: ""
  reason: ""
  effective_scope: ""
  effective_at: ""
  migration: ""
  consumer_impact: ""
  retention_location: ""
  retention_rule: ""
  integrity_result: "Not Verified"
  access_classification: ""
  approver: ""
  downstream_notifications: []
  recovery_conditions: []
  data_secret_license_legal_hold: ""
  related_change_and_decision: []
```

### 20.12 身份与版本判定表

| 情形 | 新 Asset ID | 新 Revision | 新 Snapshot | 新 BSL | 新 RLC |
|---|---:|---:|---:|---:|---:|
| 未改变语义的内容修正 | 否 | 是 | 是 | 已基线时是 | 实际发布时是 |
| 同一资产功能修订 | 否 | 是 | 是 | 已基线时是 | 实际发布时是 |
| 新独立义务/资产 | 是 | 初始 | 是 | 纳入时是 | 实际发布时是 |
| Defect Fix | Requirement 否；Defect 是 | 是 | 是 | 已基线时是 | 实际发布时是 |
| Refactor | 产品 Requirement 否；Change 是 | 是 | 是 | 已基线时是 | 实际发布时是 |
| 仅重新捕获同一内容 | 否 | 否 | 是 | 否 | 否 |
| 仅批准现有 Snapshot 集合 | 否 | 否 | 否 | 是 | 否 |
| 实际部署相同 BSL 到新环境 | 否 | 否 | 环境需固定 | 否 | 是 |
| 替代为新独立资产 | 是 | 初始 | 是 | 是 | 实际发布时是 |
| 恢复历史内容到当前 | 否或按语义判定 | 是 | 是 | 是 | 实际发布时是 |

### 20.13 C04 变更分类清单

- [ ] 是否只是阐明而未改变义务；
- [ ] 是否改变同一资产的内容或行为；
- [ ] 是否产生新的独立、可验证义务；
- [ ] 是否修复不符合既有 Requirement 的行为；
- [ ] 是否只改变内部结构而不改变产品义务；
- [ ] 是否使旧资产退出有效集合；
- [ ] 是否已保留原 ID 和 Revision；
- [ ] 已基线资产是否创建 CHG；
- [ ] 是否建立 derives-from、extends、supersedes 或 replaces；
- [ ] 是否更新 Verification、Trace、Baseline 和 Release Configuration。

### 20.14 Emergency Change 清单

- [ ] Emergency CHG 已创建；
- [ ] Incident/Risk 与紧急理由明确；
- [ ] 原状态/Snapshot 已固定；
- [ ] 最大范围和禁止范围明确；
- [ ] Emergency Authority 已批准；
- [ ] 最低影响和 Risk 已评估；
- [ ] 备份、即时验证、监视和回滚可执行；
- [ ] Implementer 与 Observer 明确；
- [ ] C09 Run 和实际变化已记录；
- [ ] IMA/CHD 已按政策补全；
- [ ] 独立验证和追溯已完成；
- [ ] BSL/RLC/CIR 已更新；
- [ ] Post-implementation Review 已完成；
- [ ] 受影响方已通知；
- [ ] 临时控制与 Residual Risk 已处置。

### 20.15 Release 重建清单

- [ ] Release ID、环境和时间可解析；
- [ ] Requirement、Design、Code、Configuration、Evidence Revision 完整；
- [ ] Repository、Commit/Object、Tag 解析结果完整；
- [ ] Build Toolchain、Dependency Lock、Artifact Digest 完整；
- [ ] Schema、Migration、Data、Model、Prompt、Policy 完整；
- [ ] Runtime Config、Feature Flag 和 Secret Reference Version 完整；
- [ ] BSL、CHG、CHD、Waiver、Gate Decision 完整；
- [ ] Deploy Run 和 Approval 完整；
- [ ] Previous/Target/Rollback Version 可解析；
- [ ] 外部依赖和保留位置可访问；
- [ ] Integrity Check 通过；
- [ ] 重建在隔离环境验证；
- [ ] 差异、Unknown 和 Residual Risk 已披露。

### 20.16 配置审核记录模板

```yaml
configuration_audit:
  review_id: ""
  audit_type: ""
  scope: ""
  baseline_or_release: ""
  snapshot: ""
  criteria: []
  checks:
    - check_id: ""
      result: "Pass|Fail|Blocked|Not Applicable"
      evidence: []
      finding: ""
  findings: []
  owner: ""
  due_at: ""
  blocker_decision: ""
  reviewer: ""
  reviewed_at: ""
```

配置审核结果应承载为 C12 Review Record 或本项目既有检查记录，不新增 C11 正式产物类型。

### 20.17 示例

#### 示例 A：正确的文档修订

```text
Asset ID: C04
Old Revision: V0.1
New Revision: V0.2
CHG: CHG-0042
VRR: VRR-0088
SNP: SNP-0110
Successor Baseline: BSL-0012
```

Version 改变，Asset ID 仍为 C04。旧 V0.1、旧 Snapshot 和旧 Baseline 均保留。

#### 示例 B：错误的 Git 快照声明

```text
snapshot: main
```

错误原因：`main` 是可移动 Branch。正确记录必须包含 Repository Identity、解析后的 Commit/Object ID、Dirty/Untracked/Submodule/LFS、外部依赖、Digest 和捕获时间。

#### 示例 C：正确的 Defect Fix

```text
Requirement: REQ-0182
Defect: DEF-0031
Change: CHG-0056
Requirement ID: unchanged
New Revision: R4
Verification: VER-0210
```

禁止为了修复 DEF-0031 创建内容相同的“新 Requirement”。

#### 示例 D：Emergency Change

紧急修复先取得 Emergency Authority，固定原生产 Snapshot，限制到单一 Feature Flag，执行即时验证和监视；事后补齐 IMA、CHD、VRR、SNP、RLC 和 Review。紧急路径不删除控制步骤，只改变允许的时序。

### 20.18 国际标准条款映射

以下映射基于 ISO 官方产品页和公开目录。对未公开的标准正文不作逐字转录；项目控制要求是对标准主题的工程化落实，不表示标准逐字规定了本项目字段名、状态值、Git 或模板。

| 国际标准及条款 | 公开主题 | 本规范落实位置 |
|---|---|---|
| ISO 10007:2017 第 1 章 | 范围 | 第 2 至 4 章 |
| ISO 10007:2017 第 4 章 | 配置管理职责 | 第 7 章 |
| ISO 10007:2017 4.1 | 职责和权限 | 7.1、10.10、15.5 |
| ISO 10007:2017 4.2 | 处置权限 | 10.10、10.14、10.17 |
| ISO 10007:2017 5.1 | 配置管理过程总则 | 第 9、10 章 |
| ISO 10007:2017 5.2 | 配置管理策划 | 9.2、10.1、17.1 |
| ISO 10007:2017 5.3 | 配置标识 | 10.2 至 10.6、13.1 至 13.5 |
| ISO 10007:2017 5.4 | 变更控制 | 10.7 至 10.14、13.6 至 13.8 |
| ISO 10007:2017 5.5 | 配置状态记账 | 10.19、第 11、19 章 |
| ISO 10007:2017 5.6 | 配置审核 | 10.19、15.1 至 15.4、20.16 |
| ISO 10007:2017 附录 A.3 | 配置管理政策 | 9.2、13.1、16 |
| ISO 10007:2017 附录 A.4 | 配置标识 | 10.1 至 10.6 |
| ISO 10007:2017 附录 A.5 | 变更控制 | 10.7 至 10.14 |
| ISO 10007:2017 附录 A.6 | 状态记账 | 10.19、第 19 章 |
| ISO 10007:2017 附录 A.7 | 配置审核 | 10.19、20.16 |
| ISO/IEC/IEEE 12207:2026 第 1 章 | 软件生命周期过程范围 | 第 2 至 4、18 章 |
| ISO/IEC/IEEE 12207:2026 4.1 | 符合性总则 | 第 5、15、19 章 |
| ISO/IEC/IEEE 12207:2026 4.2 | 完整符合 | 17.1 的 P2 保留边界 |
| ISO/IEC/IEEE 12207:2026 4.3 | 裁剪符合 | 第 17 章 |
| ISO/IEC/IEEE 12207:2026 5.2 | 软件系统概念 | 3.1、第 6、8 章 |
| ISO/IEC/IEEE 12207:2026 5.3 | 组织和项目概念 | 第 7、9 章 |
| ISO/IEC/IEEE 12207:2026 5.4 | 生命周期概念 | 9.1、10.17、10.18 |
| ISO/IEC/IEEE 12207:2026 5.5 | 过程概念 | 9.3、第 10 章 |
| ISO/IEC/IEEE 12207:2026 5.7 | 过程应用 | 第 9、15、18 章 |
| ISO/IEC/IEEE 12207:2026 第 6.2 章 | 组织项目使能过程 | 7、9.2、16、17 |
| ISO/IEC/IEEE 12207:2026 第 6.3 章 | 技术管理过程 | 10.1 至 10.19 |
| ISO/IEC/IEEE 12207:2026 第 6.4 章 | 技术过程 | 10.11 至 10.18、18 |
| ISO/IEC/IEEE 14764:2022 第 5 章 | 标准应用 | 第 3、4、17 章 |
| ISO/IEC/IEEE 14764:2022 5.2 | 维护过程 | 9.3、10.7 至 10.18 |
| ISO/IEC/IEEE 14764:2022 5.3 | 维护组织 | 第 7、9.2 章 |
| ISO/IEC/IEEE 14764:2022 6.1 | 维护活动和任务 | 10.8、10.11 至 10.13 |
| ISO/IEC/IEEE 14764:2022 6.2 | 问题与修改分析 | 10.7 至 10.10、13.6 至 13.8 |
| ISO/IEC/IEEE 14764:2022 第 7 章 | 软件处置 | 10.17、13.10 |
| ISO/IEC/IEEE 14764:2022 7.2 | 处置策略 | 10.17、10.18、17.5 |
| ISO/IEC/IEEE 14764:2022 8.1 | 实施考虑总则 | 10.11 至 10.14 |
| ISO/IEC/IEEE 14764:2022 8.2 | 维护类型 | 10.7、20.13 |
| ISO/IEC/IEEE 14764:2022 8.3 | 安排 | 7.1、10.10、10.14 |
| ISO/IEC/IEEE 14764:2022 8.4 | 工具 | 10.12、10.20 |
| ISO 15489-1:2016 第 4 章 | 记录管理原则 | 10.5、10.17、16 |
| ISO 15489-1:2016 5.2 | 记录 | 8.1、11.4、13.3 至 13.10 |
| ISO 15489-1:2016 5.3 | 记录系统 | 8.2、10.19、17.5 |
| ISO 15489-1:2016 6.2 | 记录政策 | 9.2、13.1、16 |
| ISO 15489-1:2016 6.3 | 责任 | 第 7 章 |
| ISO 15489-1:2016 6.4 | 监视与评价 | 10.19、第 19 章 |
| ISO 15489-1:2016 6.5 | 能力 | 7、10.20 |
| ISO 15489-1:2016 第 7 章 | 评价 | 3.1、10.17、17.5 |
| ISO 15489-1:2016 8.2 | 记录元数据 | 13.1 至 13.10、17.5 |
| ISO 15489-1:2016 8.3 | 业务分类方案 | 10.1、10.7、13.1 |
| ISO 15489-1:2016 8.4 | 访问和权限规则 | 7、10.5、10.17、17.5 |
| ISO 31000:2018 第 4 章 | 风险管理原则 | 10.9、14、15 |
| ISO 31000:2018 5.2 | 领导与承诺 | 7、7.1 |
| ISO 31000:2018 5.3 | 整合 | 8.2、18 |
| ISO 31000:2018 5.4 | 风险框架设计 | 9.2、10.9 |
| ISO 31000:2018 5.5 | 实施 | 10.11 至 10.14 |
| ISO 31000:2018 5.6 | 评价 | 10.13、10.19 |
| ISO 31000:2018 5.7 | 改进 | 10.14、10.16、16 |
| ISO 31000:2018 6.2 | 沟通和协商 | 10.9、10.10、10.14、10.17 |
| ISO 31000:2018 6.3 | 范围、环境和准则 | 10.9、13.7 |
| ISO 31000:2018 6.4 | 风险评估 | 10.9、15.2 |
| ISO 31000:2018 6.5 | 风险处置 | 10.10 至 10.14 |
| ISO 31000:2018 6.6 | 监视和评审 | 10.13、10.14、10.19 |
| ISO 31000:2018 6.7 | 记录和报告 | 10.19、13、19 |

规范性国际标准来源：

1. ISO, [ISO 10007:2017](https://www.iso.org/standard/70400.html)；公开条款目录见 [ISO OBP](https://www.iso.org/obp/ui/en/#iso:std:iso:10007:ed-3:v1:en)。
2. ISO, [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html)；公开条款目录见 [ISO OBP](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:12207:ed-2:v1:en)。
3. ISO, [ISO/IEC/IEEE 14764:2022](https://www.iso.org/standard/80710.html)；公开条款目录见 [ISO OBP](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:14764:ed-3:v1:en)。
4. ISO, [ISO 15489-1:2016](https://www.iso.org/standard/62542.html)；公开条款目录见 [ISO OBP](https://www.iso.org/obp/ui/en/#iso:std:iso:15489:-1:ed-2:v1:en)。
5. ISO, [ISO 31000:2018](https://www.iso.org/standard/65694.html)；公开条款目录见 [ISO OBP](https://www.iso.org/obp/ui/en/#iso:std:iso:31000:ed-2:v1:en)。
