# C04 原子需求与需求演进规范

## 1. 文档控制信息

| 文档属性 | 内容 |
|---|---|
| 文档编号 | C04 |
| 英文名称 | Atomic Requirement and Requirement Evolution Specification |
| 正式文件名 | `C04_Atomic_Requirement_and_Evolution_Standard.md` |
| 版本 | V0.3 Candidate |
| 状态 | In Review |
| 编制日期 | 2026-07-28 |
| 责任人 | 项目负责人 |
| 编制者 | Coding Agent |
| 批准人 | 待项目负责人批准 |
| 适用档位 | P2 标准 |
| 上位蓝图 | VC-PPG-BP-001、VC-PPG-BP-002 |
| 公共治理依赖 | VC-PPG-DEC-001、VC-PPG-COM-001、VC-PPG-COM-002 |
| 上游规范 | C01 V0.3、C02 V0.3、C03 V0.3 |
| 生产前调研 | RVR-C04-0001 |
| 下游规范 | C05、C06、C07、C08、C09、C10、C11、C12 |
| 访问级别 | Internal |
| 保留要求 | 正式修订、评审、分类、批准、替代、退役和基线记录永久保留 |

本文件在项目负责人批准前不得作为正式基线或 Agent 的高优先级执行约束。

> **V6.3 元模型适配规则：** 本规范列出的三位代码自 V6.3 起统一作为 `legacy_kind/Domain Profile`，不再作为正式顶层产物类型。本规范正文中历史表述“正式产物”“正式产物类型”均按“受控领域 Profile”解释；其专业语义、专属字段、领域状态和 Owner 保留。实例必须先归入 VC-PPG-COM-002 的六类元类型，再由 VC-PPG-MAP-001 解析 Profile。该规则优先于本规范正文中的 V6.2/V6.2.1 类型措辞，但不改变既有专业控制。

## 2. 目的

本规范规定原子 Requirement、Requirement Set、属性、类型、写作、质量、生命周期、分类、澄清、补丁、修订、替代、拆分、合并、追踪和验证交接规则。

本规范用于实现以下控制目标：

1. 使每条 Requirement 只表达一个必要、明确、可行、可验证且可追踪的规范性义务；
2. 使 Requirement 永久身份与标题、状态、版本、文件和实现位置分离；
3. 使 Requirement Set 同时接受覆盖、一致性、整体可行性、可理解性和可确认性检查；
4. 使 Clarification or Patch、Requirement Revision、New Requirement、Defect Fix、Technical Refactoring 和 Requirement Supersession 能被一致分类；
5. 防止通过新建 Requirement 规避 Change Request、Defect 或 Engineering Change 管理；
6. 防止已批准或已基线 Requirement 被静默覆盖、历史丢失或追踪断裂；
7. 使 Coding Agent 只能在受控事实源和人类授权边界内生成 Draft、候选分类和质量检查结果。

## 3. 适用范围

本规范适用于：

- 从 PRD、Feature、User Scenario、Quality Attribute、Constraint、Risk、外部义务和运行观察建立 Requirement；
- 功能、业务规则、数据、权限与访问、接口、UI 与交互行为、质量、安全、审计与记录、Agent 行为约束；
- Requirement Record 和 Requirement Set 的创建、评审、批准、基线、使用和退役；
- Requirement 的 Clarification、Patch、Revision、Supersession、Replacement、Split 和 Merge；
- Agent、设计、实现、验证、运营或用户反馈发现的需求缺口分类；
- Requirement 与 PRD、Feature、Acceptance、Design、Code、Verification、Release 和 Observation 的双向追踪；
- 人类主导、Agent 辅助和多 Agent 参与的需求工程活动。

本规范适用于交互式产品、服务、API、数据产品、内部工具、Agent 能力和包含软硬件的 ICT 产品。安全、数据、架构或运营专业扩展是否激活由第 18 章规定。

## 4. 不适用范围

以下内容不由本规范定义：

- Stakeholder Need、Evidence、Problem、Product Definition 和 Product Intent 的发现规则，由 C01 管理；
- Initiative、Scope、Assumption、Constraint、Risk 和 Success Metric 的建立规则，由 C02 管理；
- PRD Package、Feature、User Scenario、Non-goal、Dependency 和 Quality Attribute Summary 的组织规则，由 C03 管理；
- Acceptance Criterion、Verification、Validation、测试设计和验证证据，由 C05 管理；
- Technical Design、Architecture、接口设计、数据设计和实现选择，由 C06 管理；
- 人机职责、工具授权、批准权限和升级路径的完整模型，由 C07 管理；
- Agent Context 的组装、新鲜度和隔离，由 C08 管理；
- 命令、Tool Call、重试、执行证据和 Agent Run，由 C09 管理；
- Decision、Traceability Matrix 和 Provenance 的统一机制，由 C10 管理；
- Configuration Item、Snapshot、Baseline、Change Request 和 Release Configuration，由 C11 管理；
- Gate Decision、Waiver 和产品健康评价，由 C12 管理；
- 项目任务分解、缺陷处理流程、工程变更流程、源代码实现和法律意见。

C04 可以引用上述对象，但禁止建立同名平行资产、复制正文形成第二事实源或替代专业批准。

## 5. 规范性用语

### 5.1 中文关键词

“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。

“建议”只用于非规范性实践，不作为符合性判定依据。

### 5.2 英文关键词

英文 Requirement 使用 MUST、MUST NOT、SHOULD、SHOULD NOT 或 MAY 时，适用文档必须声明 RFC 2119 与 RFC 8174 的 BCP 14 语义。只有全大写形式具有该特殊含义；小写形式按普通英文解释。

中英文并存时必须声明一条 Authoritative Statement。其他语言文本必须标记为 Informative Translation；翻译不得获得独立 Requirement ID，不得改变义务含义。

### 5.3 规则优先级

发生冲突时按以下顺序处理：

1. 适用法律、监管要求和有效合同义务；
2. 已批准 Exception、Waiver 或 Risk Acceptance 的明确范围；
3. VC-PPG-COM-001、VC-PPG-COM-002 和 VC-PPG-DEC-001；
4. 本规范已批准或已基线版本；
5. 当前 Product、Initiative、Scope 和 PRD 的已批准资产；
6. C05、C06、C10、C11、C12 等专业资产的当前有效 Baseline；
7. R2 工程参考、模板和示例。

冲突无法判定时必须停止 Requirement Ready 和下游授权，并提交人类决策。

### 5.4 可判定表达

所有强制语句必须能够通过 Asset ID、字段、受控枚举、Trace Link、数值、时间、状态、Revision、批准记录、Evidence 或检查结果直接判定。

禁止使用没有同句判定条件的“尽量”“最好”“酌情”“快速”“合理”“适当”“友好”“高性能”“通常”“相关”“等等”和“必要时”。实现技术只有在法律、监管、合同、互操作、兼容、安全或已批准架构约束真实要求时才能进入 Requirement Statement。

## 6. 术语与定义

| 术语 | 定义 | 使用限制 |
|---|---|---|
| Requirement | 对产品、系统、参与者或 Agent 的单一、必要、明确、可行、可验证并可追踪的规范性义务 | 不是 User Story、Task、Change Request、Defect 或设计方案 |
| Atomic Requirement | 只包含一个可独立验证义务的 Requirement | “原子”不表示语句必须短，也不表示只能有一个条件 |
| Requirement Record | 承载 Requirement 当前受控内容、属性、状态、Revision 和关系的正式产物 | 使用 REQ 身份和 DOC 状态模型 |
| Requirement Set | 处于同一受控范围并接受整体质量检查的 Requirement 集合 | 不是 PRD 正文或 Requirement 副本集合 |
| Normative Statement | Requirement Record 中唯一具有权威约束力的需求陈述 | 背景、理由、示例和翻译不是 Normative Statement |
| Primary Type | Requirement 的唯一主类型 | 一条 Requirement 禁止同时具有多个 Primary Type |
| Secondary Tag | 用于检索或辅助治理的受控标签 | 不改变 Primary Type、状态或流程 |
| Clarification or Patch Event | 消除歧义、补充遗漏或明确边界，且不改变原业务意图和独立义务的事件 | 保持 REQ ID；建立事件和新快照 |
| Requirement Revision | 在同一业务意图下改变行为、约束或验收含义的受控修订记录 | 保持 REQ ID；已基线时执行 Change Request |
| New Requirement | 引入新的、可独立验证的业务义务或利益相关方结果 | 创建新 REQ ID |
| Defect Fix | 修复实现或产物对已批准 Requirement 的不符合 | 建立 Defect 和修复记录，不创建替代性 Requirement |
| Technical Refactoring | 外部行为和验收保持不变的内部改进 | 建立 Engineering Change 或技术债记录 |
| Requirement Supersession | 原 Requirement 不再有效并由另一 Requirement 接替 | 保留原 ID、历史和替代关系 |
| Requirement Snapshot | Requirement 在指定时间和 Revision 的不可变完整表示 | 正式 Snapshot Record 由 C11 管理 |
| Requirement Ready | Requirement 或 Requirement Set 满足本规范并获得授权 Gate Decision 后的门禁结论 | 不是 DOC State |
| Verification Method Reference | 指向 C05 Verification Method 的受控引用 | 不在 C04 重新定义方法体系 |
| Acceptance Reference | 指向 C05 Acceptance Criterion 的受控引用 | 不复制 Acceptance Criterion 正文 |
| Applicability | Requirement 生效的产品、版本、用户、角色、环境、地区、时间或条件边界 | 不能用空白表示全局适用 |

未在本章定义的公共术语以 VC-PPG-COM-001 为准。

## 7. 角色与职责

| 角色 | 强制职责 | 禁止事项 |
|---|---|---|
| Requirement Owner | 对 Requirement 的业务含义、来源、适用边界、Priority 和生命周期负责 | 不得单独批准自己编制的高风险 Requirement |
| Requirement Author | 按本规范编写 Statement、Rationale、属性和 Trace | 不得虚构来源、阈值或批准 |
| Requirement Set Owner | 管理集合边界、成员、覆盖、一致性和整体质量 | 不得复制成员正文形成第二事实源 |
| Source Owner or Stakeholder | 确认原始 Need、业务规则、外部义务或约束的含义 | 不得以口头意见直接覆盖已批准 Requirement |
| Classification Decider | 对 Patch、Revision、New Requirement、Defect、Refactoring 或 Supersession 作授权分类 | 不得在缺少影响分析时批准高影响分类 |
| Requirement Quality Reviewer | 检查单项与集合质量，记录 Finding 和整改要求 | 不得将作者自检作为唯一独立评审 |
| Verification Representative | 确认 Requirement 可由 C05 建立方法和 Acceptance 承接 | 不得把计划中的测试当作已通过证据 |
| Engineering Representative | 核验技术可行性、依赖和设计承接 | 不得用当前实现限制重写业务义务 |
| Configuration or Change Authority | 管理 Revision、Snapshot、Baseline 和 Change Request 接口 | 不得允许静默覆盖已批准或已基线内容 |
| Independent Reviewer | 复核来源、原子性、明确性、可行性、可验证性、冲突和演进分类 | 不得是全部内容的唯一作者 |
| Gate Approver | 按 C12 对 Requirement Ready 作授权决定 | 不得绕过阻断项作口头批准 |
| Coding Agent | 生成 Draft、提出类型或演进分类候选、运行检查、同步关系和报告缺口 | 不得批准 Requirement、最终决定高风险分类、改变 Priority/Criticality、覆盖 Baseline 或关闭阻断 Finding |

同一人可以承担多个非冲突角色，但 Gate Approver 禁止与该对象的唯一 Author 和唯一 Reviewer 为同一人。具体授权、替代和升级安排由 C07 管理。

## 8. 管理对象与关系

### 8.1 正式产物

本规范管理七类正式产物：

1. Requirement Record（REQ）；
2. Requirement Set（RQS）；
3. Clarification or Patch Event（CPE）；
4. Requirement Revision（RRV）；
5. Requirement Supersession Record（RSP）；
6. Requirement Quality Review（RQR）；
7. Requirement Classification Record（RCL）。

七类产物可以在同一工具或页面展示，但必须分别保留 Asset ID、Artifact Type、Owner、State、Revision 或记录身份、Trace Links、Access Classification、Retention Rule 和 History Reference。

### 8.2 Requirement 类型体系

| Primary Type | 判定边界 | 示例性来源 |
|---|---|---|
| Functional | 规定产品、系统或 Agent 应提供的外部可观察能力 | Feature、User Scenario |
| Business Rule | 规定业务判断、计算、资格、流程或政策义务 | 业务政策、Decision |
| Data | 规定数据语义、质量、时效、保留或处理义务 | DCR、QAS、外部义务 |
| Permission and Access | 规定主体对对象的允许、拒绝、授权或隔离义务 | 角色、Scope、Security |
| Interface | 规定系统边界交互、协议语义、输入输出或兼容义务 | 外部系统、Dependency |
| UI and Interaction Behavior | 规定界面、内容、反馈、状态或交互行为义务 | User Scenario、UX 约束 |
| Quality | 规定可度量的性能、可靠性、兼容、可维护、灵活性或其他质量义务 | QAS、Risk |
| Security | 规定机密性、完整性、可用性、防护或安全响应义务 | Risk、外部义务 |
| Audit and Recording | 规定事件记录、可追溯性、时间、主体或保留义务 | 审计政策、Compliance |
| Agent Behavior Constraint | 规定 Agent 的上下文、工具、行动、停止、升级或输出约束 | ARD、Scope、Risk |

每条 Requirement 必须选择一个 Primary Type。跨类型关注点使用 Secondary Tag 或 Trace Link 表示；无法选择主类型时必须建立 RCL，不得以 `Other` 规避分类。

### 8.3 最低关系链

```text
Requirement
  ├─ derives-from → Stakeholder Need / External Obligation / Risk / Constraint
  ├─ refines → Feature
  ├─ designed-by → Design Element
  ├─ implemented-by → Code / Configuration
  ├─ verified-by → Acceptance Criterion / Verification Evidence
  ├─ released-in → Release Configuration
  ├─ affected-by → Change / Defect / Observation / Risk
  └─ supersedes / replaces → Prior Requirement

PRD Package
  └─ contains → Feature

Requirement Set
  └─ contains → Requirement
```

实际 Trace Link 必须使用 VC-PPG-COM-001 规定的方向和语义。禁止使用 `related-to` 或中文“相关”作为正式关系。

### 8.4 事实源边界

| 信息 | 唯一事实源 | C04 允许动作 |
|---|---|---|
| Need、Problem、Intent、Goal | C01 | 引用当前 Revision，不重写 |
| Initiative、Scope、Risk、Constraint | C02 | 引用并接受边界约束 |
| PRD、Feature、Scenario、QAS | C03 | 作为 Requirement 来源和上游 Trace |
| Requirement Statement 与属性 | C04 REQ | 维护唯一权威内容 |
| Acceptance 与 Verification | C05 | 引用方法、标准和 Evidence |
| Design 与 Architecture | C06 | 记录 designed-by 关系 |
| Trace 与 Decision | C10 | 提交关系和决定记录 |
| Revision、Snapshot、Baseline、Change | C11 | 引用配置事实源 |
| Gate Decision | C12 | 接收结论，不建立平行状态 |

摘要、索引、缓存或翻译与 REQ 事实源不一致时必须标记 Stale，并禁止用于设计、执行、验证或批准。

## 9. 生命周期与工作机制

### 9.1 生命周期

```text
C03 Handoff
  → Eligibility Check
  → Source and Classification
  → Draft Requirement Record
  → Atomicity and Attribute Check
  → Requirement Set Assembly
  → Quality Review
  → Approval and Requirement Ready Decision
  → Baseline
  → Design / Implementation / Verification / Release
  → Observation or Change Trigger
  → Classification Decision
  → Patch / Revision / New Requirement / Defect / Refactoring / Supersession
  → Re-review, Re-baseline or Retire
```

### 9.2 Eligibility Check

Requirement Author 必须核验来源资产的 ID、Revision、State、Owner、Scope、Access Classification 和 Trace 可用性。来源未达到 Approved 或 Baselined 时可以创建 Draft REQ，但禁止进入 In Review、Approved、Baselined 或 Requirement Ready。

### 9.3 建立与分类

每个候选义务必须先判定是否为 Requirement，再选择 Primary Type。候选内容属于问题、需要、Feature、Acceptance、Design、Task、Defect 或 Engineering Change 时必须回到相应事实源，不得强制转写为 REQ。

### 9.4 编写与属性化

Author 必须先建立永久 REQ ID，再填写 Authoritative Statement、Source、Rationale、Applicability、Priority、Criticality、Verification、Acceptance 和 Trace。缺失信息必须显式标记 `TBD` 并建立 Owner、期限和阻断结论；禁止留空。

### 9.5 质量评审与集合检查

RQR 必须分别记录单项 Requirement 和 Requirement Set 的检查结果。单项质量通过不代表集合覆盖完整；集合通过不免除成员单项缺陷。

### 9.6 批准、基线与交接

REQ/RQS 的 Approved 由授权人作出；Baselined 必须关联 C11 Baseline Record。Requirement Ready 必须由 C12 Gate Decision 给出。下游交接必须包含当前 Revision、Statement、Applicability、Priority、Criticality、Verification、Acceptance、Trace、Open Finding 和 Baseline。

### 9.7 运行反馈与演进

Agent、设计、实现、验证、运营或用户反馈发现缺口时必须形成可追溯触发信息并执行第 10.8 章分类。任何主体禁止直接修改当前 REQ 内容后补写理由。

## 10. 强制规则

### 10.1 Requirement 身份与粒度

1. 每条 Requirement 必须具有唯一、永久、不可复用的 REQ ID。
2. REQ ID 采用受控产物目录规定的类型代码与顺序号；版本、日期、状态、Owner、标题、文件路径和 Git 提交禁止进入 ID。
3. 同一义务的标题、文字、状态或 Revision 变化必须保持 REQ ID。
4. 新的独立可验证义务必须创建新 REQ ID。
5. 被 Rejected、Superseded 或 Retired 的 REQ ID 必须永久保留，禁止重新分配。
6. 一个 REQ 只能有一个 Authoritative Statement 和一个 Primary Type。
7. 一个 Statement 包含两个可以分别实现、分别失败、分别验收或具有不同适用条件的义务时必须拆分。
8. 一个义务需要多个限定条件才能准确表达时可以保留为一条 Requirement，但条件必须共同作用于同一验证结论。

### 10.2 Requirement Statement 结构

Requirement Statement 应采用以下可判定骨架：

```text
[适用条件或触发事件]，<明确主体> 必须/禁止/应/不应/可以 <可观察动作或结果> <明确对象> [量值、阈值、时限、顺序或边界]。
```

Statement 必须满足：

1. 主体唯一且可识别；
2. 规范性关键词唯一；
3. 动作或结果可观察；
4. 对象、范围和边界明确；
5. 条件、例外、量值、单位、时间基准和容差在需要时明确；
6. 术语来自受控词汇或在首次使用处定义；
7. 代词、比较级、主观形容词和开放式集合具有唯一指代或被删除；
8. 否定表达不引入双重否定；
9. 实现方式只在真实约束存在时出现，并引用约束来源；
10. 示例、理由、注释和翻译与 Statement 分栏记录。

### 10.3 原子性判定

原子性检查必须依次回答：

1. 是否只有一个责任主体；
2. 是否只有一个规范性动作；
3. 是否只有一个可独立验证的结果；
4. 是否只有一组共同适用条件；
5. 是否能用一个 Acceptance 结论判定通过或失败；
6. 任一子句删除后是否改变同一义务，而不是移除另一项独立义务。

出现 `and`、`or`、“以及”“同时”“分别”“包括但不限于”、分号或多项列表时必须触发人工原子性复核，但连接词本身不自动判定不合格。若各子项能独立通过或失败，必须拆分为独立 REQ。

### 10.4 类型、来源与理由

1. Primary Type 必须从第 8.2 章十类中选择。
2. 无法分类或多类冲突时必须建立 RCL，并在决定前保持 Draft。
3. Source 必须指向可定位资产、外部义务或 Evidence；聊天摘要、模型记忆或口头转述不能作为唯一来源。
4. 外部法律、监管、合同或标准义务必须记录来源版本、适用范围、解释责任人和复核日期。
5. Rationale 必须解释该义务为何必要及不满足的影响，禁止重复 Statement。
6. 由 Agent 推导的候选必须标记 Generated Candidate，保留生成 Run 和推导输入；未获人类确认不得进入 Approved。
7. 来源冲突时必须建立 Finding 或 Decision 候选并停止 Ready，不得由 Author 私自选择。

### 10.5 Applicability、Priority 与 Criticality

1. Applicability 必须明确产品、版本、Feature、用户或角色、环境、地区、数据类别、时间窗口和触发条件中的适用维度。
2. 空白 Applicability 禁止解释为“全局适用”。
3. 条件不适用必须给出可测试条件；禁止使用“必要时”“视情况”。
4. Priority 表示交付排序，Criticality 表示失效影响或控制强度；两者必须分栏，禁止互相推导。
5. Priority 必须追踪 C02/C03 的授权来源；Criticality 必须追踪 Risk、安全、合规、业务连续性或其他批准依据。
6. Coding Agent 可以发现缺口或冲突，禁止最终设定或改变 Priority 和 Criticality。

### 10.6 Verification 与 Acceptance

1. 每条 REQ 必须记录 Verification Method Reference 或 C05 尚未建立时的 Method Candidate。
2. Method Candidate 只能用于 Draft；进入 Requirement Ready 前必须替换为 C05 受控引用。
3. 每条 REQ 必须记录 Acceptance Reference；不适用时必须由 C05/C12 记录依据和批准。
4. Verification 必须覆盖 Statement、Applicability、阈值、边界、异常条件和适用版本。
5. “代码已实现”“测试已写”“Reviewer 认为合理”禁止作为 Requirement 满足结论。
6. Requirement 的可验证性评审与真实 Verification Result 必须分离。

### 10.7 Requirement Set

1. 每个 RQS 必须具有唯一边界、Owner、成员准入规则和 Baseline 引用。
2. RQS 成员必须通过 REQ ID 和 Current Revision 引用，禁止复制 Statement。
3. 一个 REQ 可以属于多个 RQS，但每个成员关系必须说明范围和版本。
4. RQS 必须检查上游 Scope、Feature、Scenario、业务规则、Constraint、Risk 和 Quality Attribute 覆盖。
5. RQS 必须检查成员之间的重复、冲突、空缺、不可共同实现和术语不一致。
6. Candidate、Rejected、Superseded、Retired 或 Stale REQ 禁止计入当前完整覆盖。
7. RQS 的 Baselined 必须固定成员 REQ ID 与 Revision；仅记录“最新版本”不构成 Baseline。

### 10.8 演进分类决策

| 判定问题 | 是时分类 | 身份与控制 |
|---|---|---|
| 是否只是消除歧义、补充遗漏或明确边界，且行为、约束、验收含义和独立义务均不变 | Clarification or Patch Event | 保持 REQ ID；建立 CPE、新 Revision 标识和新 Snapshot |
| 是否保持同一业务意图，但改变行为、约束、适用边界、阈值或验收含义 | Requirement Revision | 保持 REQ ID；建立 RRV；重新评审，已基线时关联 Change Request |
| 是否引入新的、可独立验证义务或利益相关方结果 | New Requirement | 创建新 REQ ID；建立 RCL 和 `derives-from`、`extends` 或 `replaces` |
| 是否为实现或产物不符合已批准 REQ | Defect Fix | 建立 Defect 和修复记录；REQ 不变，除非另有独立需求问题 |
| 是否保持外部行为、约束和验收不变，仅改变内部结构或技术债 | Technical Refactoring | 建立 Engineering Change 或技术债记录；禁止创建产品 REQ |
| 是否使原 REQ 失效并由另一 REQ 接替 | Requirement Supersession | 保留旧 ID；建立 RSP、有效边界和 `supersedes` 或 `replaces` |

分类必须按表格顺序提供证据。无法证明“不改变”的候选不得按 Patch 或 Refactoring 处理；无法证明“新的独立义务”的候选不得创建新 REQ。

### 10.9 Clarification or Patch

1. CPE 必须记录触发、原 Statement、Patch 内容、不改变独立义务的证据、影响分析、新 Snapshot、记录者和时间。
2. CPE 可以修正拼写、术语指代、缺失单位、边界说明或非规范性说明，但前提是外部行为、约束和验收含义不变。
3. 增加新条件、新例外、新阈值、新角色、新结果或新的 Acceptance 结论禁止按 Patch 处理。
4. Draft REQ 的 Patch 必须记录 Revision 历史；Approved REQ 的 Patch 必须重新进入评审和批准。
5. Baselined REQ 的任何受控内容变化必须关联 C11 Change Request，即使分类为 Patch。
6. CPE 记录一经 Recorded 禁止原位修改；记录错误通过新的 correction 记录处理。

### 10.10 Requirement Revision

1. RRV 必须记录 REQ ID、旧 Revision、新 Revision、变化内容、同一业务意图证据、原因、影响、批准和生效时间。
2. Revision 可以改变行为、约束、Applicability、Priority、Criticality、阈值或 Acceptance 含义，但禁止引入另一项独立义务。
3. Revision 必须执行上游、设计、实现、Verification、Release、Context 和未完成工作影响分析。
4. Approved REQ 修订后必须重新评审和批准；Baselined REQ 必须先取得 Change Decision。
5. 新 Revision 生效前，旧 Revision 必须继续可定位、可重建和可查询。
6. RRV 禁止替代 C11 Version or Revision Record；两者通过 Trace Link 连接。

### 10.11 New Requirement

1. New Requirement 必须能独立回答“谁在何种条件下承担什么可验证义务”。
2. 新 REQ 必须记录产生来源、与原对象的 `derives-from`、`extends` 或 `replaces` 关系以及对 Scope、Feature、RQS 和 Release 的影响。
3. 仅因文字变化、实现失败、重构需要、测试缺失、任务拆分或版本升级，禁止创建 New Requirement。
4. 新 REQ 超出当前 Scope 时必须先进入 C02/C11 的范围或变更控制。
5. Agent 发现新的候选义务时只能创建 Draft 和分类候选，禁止直接批准或加入 Baseline。

### 10.12 Defect、Refactoring 与 Requirement Gap

1. 已批准 Requirement 存在且实现偏离时必须按 Defect Fix 处理。
2. Requirement 本身错误、不完整或歧义时必须按 Patch、Revision 或 New Requirement 处理，禁止只关闭 Defect。
3. 外部行为和 Acceptance 不变的内部结构、依赖升级、代码清理或性能优化只能在已批准质量义务不变时按 Technical Refactoring 处理。
4. Refactoring 改变外部行为、资源阈值、安全边界或兼容性时必须重新分类。
5. 发现产品应承担但当前没有 REQ 的义务时为 Requirement Gap；必须先分类，不得直接作为 Task 执行。
6. 同一触发可以同时产生 Defect 和 Requirement Revision，但两者必须保持独立身份和关系。

### 10.13 Supersession、Replacement、Split、Merge 与 Retirement

1. Supersession 必须建立 RSP，记录旧 REQ、新 REQ、替代类型、有效边界、原因、迁移影响、未完成下游处理、批准人和生效时间。
2. Split 必须为每个独立义务创建新 REQ ID，将原 REQ 置为 Superseded，并逐项记录替代范围。
3. Merge 必须创建一个满足原子性的新 REQ；所有旧 REQ 保持历史并分别记录替代关系。
4. 只消除重复而保留某一现有 REQ 时，可以由该 REQ 替代其他重复项，但必须证明内容和适用边界覆盖完整。
5. 无替代退役使用 REQ 的 Retired 状态并关联 C11 Supersession and Retirement Record；禁止伪造替代 REQ。
6. Superseded 或 Retired REQ 禁止用于新设计、实现或 Verification，但历史 Release 的 Trace 必须保留。

### 10.14 Review、批准与基线

1. REQ/RQS 进入 In Review 前必须通过必填信息、原子性、受控词汇和关系自动检查。
2. Approved 前必须完成 Source Owner、Requirement Quality、Engineering、Verification 和适用专业方评审。
3. 高 Criticality、安全、隐私、合规、财务权限或 Agent 高风险行为 Requirement 必须由独立 Reviewer 和授权 Approver 评审。
4. Author、Coding Agent 或自动检查工具禁止批准自身产物。
5. Baselined 必须关联 C11 Baseline Record、Snapshot 和完整性校验。
6. Review Record、RQR 的 Accepted 和 Gate Decision 必须保持独立；任一记录禁止替代另一记录。

### 10.15 Coding Agent 行为边界

Coding Agent 可以：

- 从已授权来源提取候选义务并创建 Draft REQ/RQS；
- 提出 Primary Type、演进分类、拆分和 Trace Link 候选；
- 运行模糊词、连接词、属性、重复、冲突、孤立和版本新鲜度检查；
- 生成 RQR 草案、影响查询和待人类决定清单；
- 在批准后按明确 Change Decision 实施机械同步。

Coding Agent 禁止：

- 虚构 Source、Rationale、阈值、Priority、Criticality、Acceptance 或批准；
- 以新 REQ 规避 Revision、Change Request、Defect 或 Engineering Change；
- 将 User Story、Task、Design、Test Case 或模型建议宣布为 Approved Requirement；
- 静默覆盖 Approved/Baselined Statement、Revision、Snapshot 或 Trace；
- 自行解决冲突、扩大 Scope、接受剩余 Risk、作 Waiver 或 Gate Decision；
- 将自然语言检查结果表述为业务正确性、完整 Verification 或国际标准认证。

## 11. 受控状态

### 11.1 DOC 状态：REQ 与 RQS

| State | 进入条件 | 允许后续 |
|---|---|---|
| Draft | 已建立永久 ID、Owner 和 Source；允许存在显式 TBD | In Review、Rejected |
| In Review | 必填字段完整，自动检查通过，已指定 Reviewer | Changes Required、Approved、Rejected |
| Changes Required | 存在需整改 Finding | Draft、In Review、Rejected |
| Approved | 授权人批准当前 Revision | Baselined、In Review、Superseded、Retired |
| Baselined | 已纳入 C11 Baseline 并固定 Revision/Snapshot | 通过 Change Request 进入修订、Superseded、Retired |
| Rejected | 候选义务不成立或不获批准 | 保留历史；新证据出现时创建修订流程 |
| Superseded | 已被其他 Requirement 或 Set 接替 | 仅历史查询 |
| Retired | 无替代且不再适用 | 仅历史查询 |

### 11.2 REC 状态：CPE、RRV 与 RSP

| State | 含义 | 规则 |
|---|---|---|
| Recorded | 事件已按事实记录 | 禁止原位改写 |
| Corrected | 存在后续 correction 记录 | 原记录保持可见 |
| Superseded | 后续记录替代其治理结论 | 事实历史不得删除 |
| Archived | 已移入长期保留位置 | 必须保持可检索和完整性 |

### 11.3 EXEC 状态：RQR

| State | 使用条件 |
|---|---|
| Planned | 已定义对象、范围和准则 |
| Ready | 输入、Reviewer 和检查工具可用 |
| Running | 评审正在执行 |
| Blocked | 输入、权限或 Evidence 缺失 |
| Completed | 检查活动结束，结论待接受 |
| Failed | 评审执行失败，结果不可用 |
| Accepted | 授权人接受评审结果 |
| Rejected | 授权人拒绝评审结果 |
| Cancelled | 评审被授权取消并记录理由 |

### 11.4 DEC 状态：RCL

| State | 使用条件 |
|---|---|
| Proposed | 已形成分类候选和证据 |
| Under Review | 授权 Decider 正在评审 |
| Approved | 分类决定已批准 |
| Conditionally Approved | 分类在明确条件、期限和责任下批准 |
| Rejected | 候选分类被拒绝 |
| Waived | 经授权豁免规定分类流程 |
| Superseded | 后续分类决定替代当前决定 |
| Expired | 条件、期限或适用边界已失效 |

### 11.5 状态与结论分离

Requirement Ready、Quality Result、Classification、Applicability、Coverage 和 Verification Result 均不是 State。`Candidate`、`Generated Candidate` 和 `Stale` 分别是候选、生成来源和新鲜度标记，也不是 State。状态变化必须记录原状态、新状态、对象 Revision、触发、操作者、时间、理由、批准和关联记录。人类批准是 Approved、Conditionally Approved、Waived、Accepted 和 Baselined 的必要条件。

## 12. 必需产物

| 类型代码 | 正式产物 | 状态模型 | 最低用途 |
|---|---|---|---|
| REQ | Requirement Record | DOC | 承载单一规范性义务、属性、当前 Revision 和 Trace |
| RQS | Requirement Set | DOC | 管理同一范围成员、完整性、一致性、整体可行性和 Baseline |
| CPE | Clarification or Patch Event | REC | 记录不改变独立义务的澄清或补丁及新 Snapshot |
| RRV | Requirement Revision | REC | 记录同一业务意图下的语义修订 |
| RSP | Requirement Supersession Record | REC | 记录替代、拆分、合并和迁移处理 |
| RQR | Requirement Quality Review | EXEC | 记录单项和集合质量评审、Finding、整改和复核 |
| RCL | Requirement Classification Record | DEC | 对候选对象和演进事件作受控分类决定 |

七类产物禁止合并身份。P2 下禁止以一个“Requirement Register”替代七类产物。

## 13. 产物必填信息

### 13.1 通用必填信息

七类产物必须引用并满足 VC-PPG-COM-002 第 3 章的通用必填信息和第 3.1 节的适用公共字段组。REC 类型使用不可变记录标识表达修订事实。后续模板出现同名公共字段时只表示必须显示或引用该值，不形成第二定义；其余条目为 C04 类型专属要求。

### 13.2 Requirement Record

| 字段 | 强制要求 |
|---|---|
| Requirement ID | 永久 REQ ID，不含版本、状态或标题 |
| Title | 简洁表达义务对象，不替代 Statement |
| Authoritative Language | 指明权威语言 |
| Normative Statement | 唯一原子、明确、可验证的权威义务 |
| Primary Type | 第 8.2 章十类之一 |
| Secondary Tags | 受控标签；无时填 None |
| Source | 来源资产 ID、Revision 或外部来源版本 |
| Rationale | 必要性及不满足影响 |
| PRD and Feature | 当前 PRD/Feature ID 与 Revision |
| Target Actor or Subject | 承担义务的产品、系统、角色或 Agent |
| Preconditions and Applicability | 生效条件和适用边界 |
| Priority | 排序及授权来源 |
| Criticality | 失效影响等级及依据 |
| Owner | 对业务含义和生命周期负责的人类角色 |
| State | DOC 状态 |
| Current Revision | 当前受控内容修订 |
| Verification Method | C05 引用或 Draft 阶段 Method Candidate |
| Acceptance Reference | C05 Acceptance ID；缺失时为阻断项 |
| Upstream Trace | Need、Goal、Scope、PRD、Feature、Scenario、Constraint、Risk 或外部义务 |
| Downstream Trace | Design、Code、Verification、Release 或 Observation 引用 |
| Risk and Assumption | 关联 Risk/Assumption；无时填 None 并记录检查依据 |
| Created and Modified | 创建、最近修改时间与操作者 |
| Baseline and Snapshot | 当前 Baseline/Snapshot；Draft 时填 Not Baselined |
| Open Findings | Finding、Owner、期限和阻断结论 |

### 13.3 Requirement Set

| 字段 | 强制要求 |
|---|---|
| Boundary | Product、PRD、Feature、Release、专业域和适用版本 |
| Member Requirements | REQ ID、固定 Revision、Primary Type 和成员状态 |
| Admission Rule | 成员进入、移除和版本更新条件 |
| Completeness Evidence | 上游覆盖来源、查询范围和统计时间 |
| Consistency Check | 冲突、重复、术语、单位、边界和接口检查 |
| Coverage Conclusion | Covered、Partially Covered、Not Covered；Candidate 不计 Covered |
| Overall Feasibility | 资源、技术、时序、依赖和冲突的集合结论 |
| Validation Conclusion | 集合是否可由 Stakeholder 确认满足 Need/Intent |
| Open Gaps | Gap、Owner、期限和阻断结论 |
| Baseline | Baseline ID、成员 Revision 集和完整性引用 |

### 13.4 Clarification or Patch Event

| 字段 | 强制要求 |
|---|---|
| Requirement | REQ ID 与原 Revision |
| Trigger | 发现来源、时间和触发资产 |
| Original Content | 原 Statement 或受影响字段的不可变引用 |
| Clarification or Patch | 具体变化 |
| No Independent Obligation Change Evidence | 行为、约束、Applicability 和 Acceptance 含义不变的证据 |
| Impact Analysis | 上下游、版本、发布、Context 和未完成工作影响 |
| New Snapshot | 新 Revision、Snapshot 和完整性引用 |
| Change Control | Approved/Baselined 对象的评审、Change Request 和批准引用 |
| Recorder | 记录者、时间和授权来源 |

### 13.5 Requirement Revision

| 字段 | 强制要求 |
|---|---|
| Requirement ID | 保持不变的 REQ ID |
| Old and New Revision | 旧、新修订及快照 |
| Change | Statement、属性或适用边界变化 |
| Same Business Intent Evidence | 证明仍服务同一业务意图 |
| Reason | 触发、来源和必要性 |
| Impact | 上游、RQS、Design、Code、Verification、Release、Context 和 Risk |
| Change Request | 已基线时必须；其他状态记录 Not Required 依据 |
| Approval | Reviewer、Approver、决定、条件和时间 |
| Effective Time | 新 Revision 生效时间与旧 Revision 停用边界 |

### 13.6 Requirement Supersession Record

| 字段 | 强制要求 |
|---|---|
| Prior Requirement | 旧 REQ ID 与 Revision |
| Successor Requirement | 新 REQ ID 与 Revision；无替代时不得使用 RSP |
| Supersession Type | Replace、Split、Merge 或 Duplicate Consolidation |
| Effective Boundary | Product、Release、环境、用户、地区和时间 |
| Reason | 替代必要性及决定来源 |
| Migration Impact | Design、Code、Data、Verification、Release、用户和兼容影响 |
| Unfinished Downstream Handling | 未完成 Task、Defect、Verification、Release 和 Context 的处理 |
| Relations | `supersedes` 或 `replaces` 的明确方向 |
| Approval and Effective Time | Approver、Decision、Change/Baseline 和生效时间 |

### 13.7 Requirement Quality Review

| 字段 | 强制要求 |
|---|---|
| Reviewed Object | REQ/RQS ID、Revision、Snapshot 和 Baseline |
| Review Scope | 单项、集合、变化范围和排除项 |
| Criteria | 第 14 章适用准则和阈值 |
| Per-item Results | 每项准则 Pass、Fail、Blocked 或 Not Applicable 及证据 |
| Findings | Finding ID、严重度、位置、影响和依据 |
| Reviewer | 姓名或角色、独立性和时间 |
| Conclusion | Pass、Pass with Findings、Fail 或 Blocked |
| Remediation | 行动、Owner、期限和关闭 Evidence |
| Recheck | 复核范围、结果、Reviewer 和时间 |

### 13.8 Requirement Classification Record

| 字段 | 强制要求 |
|---|---|
| Classified Object | 候选义务、REQ、Change、Defect、Task 或观察引用 |
| Trigger and Evidence | 发现来源、原始内容和可复核 Evidence |
| Candidate Classes | Requirement 类型或六类演进候选 |
| Decision Questions | 第 10.8 章问题及逐项答案 |
| Final Classification | 唯一分类 |
| Rationale | 选择和排除其他分类的理由 |
| Identity Handling | 保持 REQ ID、创建新 ID 或不创建 REQ |
| Required Control Flow | CPE、RRV、RSP、Defect、Engineering Change、Change Request 或 Scope Change |
| Impact and Risk | 受影响资产、未知项和风险 |
| Decider and Time | 授权人、决定、条件、生效与失效时间 |

## 14. 质量准则

### 14.1 单项 Requirement 质量

| 准则 | 通过条件 |
|---|---|
| Necessary | 有有效来源和 Rationale；删除会造成已确认 Need、Scope、Risk 或外部义务缺口 |
| Appropriate | 位于正确抽象层级，不把 Need、Feature、Design、Task、Defect 或 Test Case 当作 Requirement |
| Unambiguous | 主体、动作、对象、条件、术语、量值、单位、时间和例外只有一种受控解释 |
| Complete | Statement 与属性足以被实现、验证和治理；无未解释空白或开放式引用 |
| Singular | 只有一个可独立验证义务 |
| Feasible | 在已知技术、资源、时序、依赖和约束下可实现；未知项显式阻断 |
| Verifiable | 存在可执行方法、可观察结果、阈值和 Acceptance Reference |
| Correct | 与来源、Scope、PRD、Feature、业务规则和外部义务一致 |
| Conforming | 使用正式模板、关键词、类型、字段、标识和受控词汇 |
| Traceable | 上游来源和适用下游关系可正向、反向查询且 Revision 匹配 |

任一准则 Fail 或 Blocked 时禁止 Requirement Ready。

### 14.2 Requirement Set 质量

| 准则 | 通过条件 |
|---|---|
| Complete Coverage | 所有 In Scope Feature、Scenario、业务规则、Constraint、Risk 和适用 Quality Attribute 均有当前 REQ 覆盖 |
| Consistent | 成员不存在逻辑冲突、重复义务、术语冲突、单位冲突或适用边界重叠错误 |
| Jointly Feasible | 成员在资源、时序、架构、接口、数据和依赖上能够共同实现 |
| Comprehensible | 边界、结构、术语、分组、关系和优先级可由目标 Reviewer 理解 |
| Validatable | Stakeholder 能基于集合确认其是否满足上游 Need、Intent 和 Scenario |

### 14.3 质量度量

RQR 应记录：

- REQ 总数及按 Primary Type、Priority、Criticality、State 的分布；
- 单项质量 Fail、Blocked 和 Finding 数；
- 上游来源、Feature、Acceptance、Design、Verification 和 Release 覆盖率；
- 孤立、重复、冲突、Stale、Superseded 误用和无 Owner 数；
- Patch、Revision、New Requirement、Defect、Refactoring 和 Supersession 的分类数量；
- 自动检查误报、漏报和人工推翻记录。

度量必须注明查询范围、时间、Revision、算法和限制。数量或覆盖率禁止单独作为质量充分性结论。

## 15. 验证与符合性检查

### 15.1 自动检查

工具必须或应执行以下检查：

1. REQ ID 唯一、格式正确且未复用；
2. 七类产物必填字段无空白；
3. REQ/RQS、CPE/RRV/RSP、RQR、RCL 使用正确状态模型；
4. 每条 REQ 只有一个 Authoritative Statement、规范性关键词和 Primary Type；
5. Statement 命中模糊词、开放式量词、代词、比较级、双重否定、分号、列表或多个规范性关键词时产生 Finding；
6. 数值具有单位、比较符、时间基准和适用条件；
7. Source、Owner、Revision、Verification、Acceptance 和 Trace 可解析；
8. Approved/Baselined REQ 不含 TBD、Candidate 或 Stale 引用；
9. RQS 成员固定 Revision，不引用“latest”；
10. 重复或高相似 Statement 产生人工复核 Finding；
11. Requirement 间否定、阈值、角色、权限、接口和时间顺序冲突产生候选 Finding；
12. Patch 变化触及行为、约束、Applicability、阈值或 Acceptance 时阻断；
13. 新 REQ 缺少独立义务证据或关系时阻断；
14. Baselined 内容变化缺少 Change Request 时阻断；
15. Superseded/Retired REQ 被新下游资产引用时阻断；
16. 两组 ISO 标准官方页面出现替代版本时阻断 C04 Baseline。

自动检查只产生 Evidence 和 Finding，禁止自动批准、自动关闭高风险 Finding 或最终判定业务正确性。

### 15.2 人工评审

人工评审必须覆盖：

- 来源真实性、业务必要性、抽象层级和 Scope 一致性；
- Statement 的唯一解释、原子性、完整性和领域术语；
- Priority、Criticality、Applicability、Risk 和 Assumption；
- Verification 可执行性和 Acceptance 充分性；
- RQS 覆盖、冲突、重复、整体可行性和可确认性；
- 演进分类、身份处理、影响分析、迁移和有效边界；
- 安全、隐私、合规、数据、架构和 Agent 风险扩展适用性；
- Agent 生成内容的来源、幻觉、越权和事实源覆盖风险。

### 15.3 Requirement Ready 阻断条件

存在以下任一情况时禁止 Requirement Ready：

1. 上游来源未 Approved/Baselined 或 Revision 不可定位；
2. REQ 必填字段为空、TBD 无 Owner/期限或 Authoritative Language 未声明；
3. Statement 包含多个独立义务或不可唯一解释；
4. Source、Rationale、Owner、Priority、Criticality、Verification 或 Acceptance 缺失；
5. Primary Type 未决或类型冲突未关闭；
6. Scope、PRD、Feature、Constraint、Risk 或外部义务冲突；
7. RQS 存在覆盖缺口、重复、冲突、整体不可行或无法确认；
8. RQR 未 Accepted 或存在阻断 Finding；
9. Agent 是唯一 Author、唯一 Reviewer 和实际 Approver；
10. Approved/Baselined 内容被静默修改；
11. Patch、Revision、New Requirement、Defect、Refactoring 或 Supersession 分类无 RCL 或证据不足；
12. Baselined 变化缺少 Change Request、Impact Analysis 或 Change Decision；
13. 新 Revision、Snapshot、RSP 或历史内容不可定位；
14. Superseded/Retired REQ 仍被当前下游执行引用；
15. 适用扩展未激活或高风险专业评审缺失；
16. ISO/IEC/IEEE 29148 或 ISO 10007 已有替代版本但未完成影响复核。

### 15.4 符合性声明限制

通过本章检查只证明符合 C04 当前内部草案规则，不构成 ISO、IEC、IEEE、INCOSE 认证或完整标准符合性声明。

## 16. 追踪与记录要求

### 16.1 最低追踪覆盖

每条当前 REQ 必须至少具备：

```text
Source / Need / External Obligation
  → Requirement
  → PRD / Feature / Requirement Set
  → Acceptance / Verification Method
```

进入设计、实现、验证或发布后，还必须按适用范围建立：

```text
Requirement
  → Design
  → Code / Configuration
  → Verification Evidence
  → Release
  → Operational Observation
```

每条关系必须记录源 ID 与 Revision、受控关系、目标 ID 与 Revision、建立依据、建立者、时间、有效版本范围和成员状态，并支持正向与反向查询。

### 16.2 演进追踪

每次演进必须能够从触发资产查询到 RCL、CPE/RRV/RSP 或专业记录、Change Request、影响分析、新 Revision/Snapshot、Review、Gate、Baseline 和受影响下游。禁止只在 Git 提交信息、聊天或代码注释中记录演进。

### 16.3 记录保留

1. REQ/RQS 的所有 Revision、Snapshot、Review、批准、基线、替代和退役历史永久保留。
2. CPE、RRV、RSP 作为 REC 一经 Recorded 禁止删除或原位改写。
3. RQR、RCL、Finding、Evidence 和人类决定必须与被评审 Revision 永久关联。
4. 被拒绝候选、失败分类和未采用 Draft 必须按 Retention Rule 保留，不得复用 ID。
5. 敏感 Requirement 的访问限制不得破坏授权 Reviewer 的可追溯性；访问由 C07/C08 管理。

## 17. 裁剪规则

本章必须与 VC-PPG-DEC-001 第 9–17 章及 VC-PPG-TAIL-001 取并集执行。本规范的专业规则可以增加或加深 C04 控制，不得删除 Always、Risk、Stage 或其他命中规范的控制；缺项、Unknown 或同级冲突必须 fail-closed。

### 17.0 Task Profile 驱动的适用性

C04 在新增、澄清、修订、分类、替代或退役 Requirement 时适用。DT-06 缺陷修复必须引用被违反的现有 Requirement Revision；只有发现需求本身缺失或错误时才转为 DT-03/DT-05。DT-07 外部行为不变时创建工程变更，不创建产品 Requirement。

CPE、RRV、RSP、RQR、RCL 均为事件或决定触发，不得预建空记录。Artifact Manifest 必须明确采用 `Create/Revise`、`Reference`、`On Event` 或 `N/A` 的依据。

### 17.1 当前 P2 决议

当前项目采用 P2，以下内容禁止裁剪：

- 七类正式产物的独立身份；
- REQ 永久 ID、Source、Owner、State、Current Revision、Verification、Acceptance、Trace 和历史；
- Requirement Set 的边界、成员固定 Revision、覆盖、一致性、整体可行性和 Baseline；
- Patch、Revision、New Requirement、Defect、Refactoring、Supersession 的分类证据；
- Approved/Baselined 变更的 Review、Change Request、Impact Analysis、Snapshot 和批准；
- 单项与集合质量评审；
- 人类批准、独立性和 Gate 记录。

同页展示、自动生成视图、索引或工具内关联不构成身份合并。

### 17.2 允许的呈现裁剪

可以隐藏不适用于特定 Primary Type 的辅助字段，但底层资产必须记录 `Not Applicable`、依据和批准。可以将七类产物存入同一受控数据库，但必须支持独立 ID、状态、修订、权限、查询和导出。

### 17.3 未来裁剪

未来改为 P1 或其他档位必须通过正式决议和 Change Request。裁剪不得删除永久身份、来源、责任、版本、追踪、Evidence、变更、Gate 或保留控制。

## 18. 扩展接口

| 扩展 | 激活条件 | C04 追加要求 | 不替代对象 |
|---|---|---|---|
| E01 架构治理 | 多系统边界、关键质量权衡、复杂迁移或架构演进 | Requirement 追踪 Concern、Viewpoint、Architecture Decision 和 Fitness Criteria | C06 Design、C10 Decision |
| E02 安全、隐私与合规 | 处理身份、权限、个人信息、受监管数据、高风险 AI 或关键安全义务 | 激活 Security Requirement Set、Threat/Privacy/Compliance 来源、独立评审和安全验证接口 | C04 REQ、C05 Verification |
| E03 数据与 AI 数据治理 | 数据质量、数据合同、训练/评估数据或保留处置影响产品义务 | 数据类 REQ 追踪 Data Requirement Set、Data Contract、DQS、Lineage 和 Dataset | REQ Primary Type、C03 QAS |
| E04 知识与正式记录 | Requirement 依赖知识资产、外部资料或长期检索 | 记录来源、Provenance、新鲜度、访问和替代知识 | C10 Trace、C11 Configuration |
| E05 产品运营与服务管理 | Requirement 包含 SLO、监控、告警、事件、发布后观察或回滚义务 | 追踪 Service Definition、SLO、Monitoring、Incident、Observation 和 Post-release Review | C05、C11、C12 |

扩展激活只增加控制，不得删除 C04 基础产物、字段、状态或演进分类。

## 19. 参考标准

### 19.1 R1 国际标准

1. [ISO/IEC/IEEE 29148:2018, Systems and software engineering — Life cycle processes — Requirements engineering](https://www.iso.org/standard/72089.html)。
2. [ISO 10007:2017, Quality management — Guidelines for configuration management](https://www.iso.org/standard/70400.html)。

### 19.2 R2 工程参考

1. [INCOSE Guide for Writing Requirements, Version 4](https://portal.incose.org/commerce/store?productId=INCOSE-GUIDEWRITINGREQ)，2023。
2. [RFC 2119, Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/info/rfc2119/)，BCP 14。
3. [RFC 8174, Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/info/rfc8174/)，BCP 14。

### 19.3 来源与复核边界

本规范依据 RVR-C04-0001 核验的官方元数据和公开条款目录形成原创治理规则。引用条款主题不表示复制标准正文，也不构成完整符合性或认证。C04 批准或基线前必须复核两组 ISO 标准是否已发布替代版本。

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
current_revision: "<当前 Revision 或记录标识>"
created_at: "<ISO 8601 时间>"
updated_at: "<ISO 8601 时间>"
applicable_scope: "<产品、PRD、Feature、Release 或环境>"
trace_links:
  - relation: "<受控关系>"
    target_id: "<目标 ID>"
    target_revision: "<目标 Revision>"
access_classification: "<访问级别>"
retention_rule: "<保留规则>"
history_reference: "<Revision、Snapshot、Git 或记录引用>"
```

### 20.2 Requirement Record 模板骨架

```yaml
requirement_id: "REQ-0001"
title: "<义务对象>"
authoritative_language: "zh-CN"
normative_statement: "<条件>，<主体> 必须 <可观察动作或结果> <对象> <阈值或边界>。"
primary_type: "<十类之一>"
secondary_tags: []
source: [{asset_id: "<ID>", revision: "<Revision>"}]
rationale: "<必要性与不满足影响>"
prd_and_feature: [{prd_id: "<PRD>", feature_id: "<FTR>"}]
target_actor_or_subject: "<主体>"
preconditions_and_applicability: "<条件与边界>"
priority: {value: "<受控值>", source: "<授权来源>"}
criticality: {value: "<受控值>", basis: "<Risk/义务来源>"}
owner: "<人类责任人>"
state: "Draft"
current_revision: "<Revision>"
verification_method: "<C05 引用或 Method Candidate>"
acceptance_reference: "<ACC ID 或阻断说明>"
upstream_trace: []
downstream_trace: []
risk_and_assumption: []
created_and_modified: {created_at: "<时间>", modified_at: "<时间>", modified_by: "<主体>"}
baseline_and_snapshot: "Not Baselined"
open_findings: []
```

### 20.3 Requirement Set 模板骨架

```yaml
requirement_set_id: "RQS-0001"
boundary: "<PRD/Feature/Release/专业域/适用版本>"
admission_rule: "<成员准入、移除和 Revision 更新规则>"
members:
  - requirement_id: "REQ-0001"
    revision: "<固定 Revision>"
    primary_type: "<类型>"
    state: "<DOC State>"
completeness_evidence: "<覆盖查询与 Evidence>"
consistency_check: "<重复、冲突、术语、单位和边界结论>"
coverage_conclusion: "<Covered | Partially Covered | Not Covered>"
overall_feasibility: "<结论与 Evidence>"
validation_conclusion: "<结论与 Stakeholder>"
open_gaps: []
baseline: "<BSL ID 或 Not Baselined>"
```

### 20.4 Clarification or Patch Event 模板骨架

```yaml
event_id: "CPE-0001"
requirement: {id: "REQ-0001", original_revision: "<Revision>"}
trigger: {source: "<资产或 Evidence>", time: "<时间>"}
original_content_reference: "<Snapshot 或不可变引用>"
clarification_or_patch: "<变化>"
no_independent_obligation_change_evidence:
  behavior_unchanged: "<Evidence>"
  constraints_unchanged: "<Evidence>"
  applicability_unchanged: "<Evidence>"
  acceptance_meaning_unchanged: "<Evidence>"
impact_analysis: "<受影响资产与未知项>"
new_snapshot: {revision: "<新 Revision>", snapshot_id: "<SNP ID>"}
change_control: "<Review/CHG/批准引用>"
recorder: {actor: "<记录者>", time: "<时间>"}
state: "Recorded"
```

### 20.5 Requirement Revision 模板骨架

```yaml
revision_record_id: "RRV-0001"
requirement_id: "REQ-0001"
old_revision: "<旧 Revision>"
new_revision: "<新 Revision>"
change: "<Statement、属性或边界变化>"
same_business_intent_evidence: "<Evidence>"
reason: "<触发与来源>"
impact:
  upstream: []
  downstream: []
  risk_and_unknowns: []
change_request: "<CHG ID 或 Not Required + 依据>"
approval: {reviewers: [], approver: "<授权人>", decision: "<决定>", time: "<时间>"}
effective_time: "<时间与旧 Revision 停用边界>"
state: "Recorded"
```

### 20.6 Requirement Supersession Record 模板骨架

```yaml
supersession_record_id: "RSP-0001"
prior_requirement: {id: "<旧 REQ>", revision: "<Revision>"}
successor_requirements:
  - {id: "<新 REQ>", revision: "<Revision>"}
supersession_type: "<Replace | Split | Merge | Duplicate Consolidation>"
effective_boundary: "<产品、Release、环境、用户、地区、时间>"
reason: "<理由与决定来源>"
migration_impact: "<设计、代码、数据、验证、发布和用户影响>"
unfinished_downstream_handling: []
relations:
  - {relation: "<supersedes | replaces>", source: "<新 REQ>", target: "<旧 REQ>"}
approval_and_effective_time: {approver: "<授权人>", decision: "<DEC/CHD>", time: "<时间>"}
state: "Recorded"
```

### 20.7 Requirement Quality Review 模板骨架

```yaml
quality_review_id: "RQR-0001"
reviewed_object: {id: "<REQ/RQS>", revision: "<Revision>", snapshot: "<SNP>"}
review_scope: "<单项/集合/变化范围/排除项>"
criteria:
  - id: "<准则 ID>"
    result: "<Pass | Fail | Blocked | Not Applicable>"
    evidence: "<Evidence>"
findings:
  - {id: "<Finding ID>", severity: "<级别>", location: "<位置>", impact: "<影响>", basis: "<依据>"}
reviewer: {actor: "<Reviewer>", independence: "<独立性>", time: "<时间>"}
conclusion: "<Pass | Pass with Findings | Fail | Blocked>"
remediation: []
recheck: {scope: "<范围>", result: "<结果>", reviewer: "<Reviewer>", time: "<时间>"}
state: "Completed"
```

### 20.8 Requirement Classification Record 模板骨架

```yaml
classification_record_id: "RCL-0001"
classified_object: "<候选义务/REQ/Change/Defect/Task/Observation>"
trigger_and_evidence: "<来源与原始 Evidence>"
candidate_classes: []
decision_questions:
  independent_obligation_changed: "<Yes | No | Unknown>"
  behavior_constraint_or_acceptance_changed: "<Yes | No | Unknown>"
  implementation_nonconformance: "<Yes | No | Unknown>"
  external_behavior_unchanged: "<Yes | No | Unknown>"
  prior_requirement_ceases_to_apply: "<Yes | No | Unknown>"
final_classification: "<唯一分类>"
rationale: "<选择与排除理由>"
identity_handling: "<Keep ID | New ID | No REQ>"
required_control_flow: []
impact_and_risk: "<受影响资产、未知项和 Risk>"
decider_and_time: {decider: "<授权人>", decision: "<决定>", time: "<时间>", expiry: "<失效时间或 None>"}
state: "Proposed"
```

### 20.9 演进分类速查表

| 变化实例 | 正确分类 | REQ ID | 必需记录 |
|---|---|---|---|
| 修正拼写且含义不变 | Patch | 保持 | CPE、新 Snapshot |
| 补充单位且原来源已唯一规定该单位 | Patch | 保持 | CPE、来源证据、新 Snapshot |
| 将响应阈值从 2 秒改为 1 秒 | Revision | 保持 | RCL、RRV；已基线时 CHG/IMA/CHD |
| 新增导出审计日志的独立义务 | New Requirement | 新建 | RCL、新 REQ、Trace |
| 代码未执行已有权限拒绝规则 | Defect Fix | 保持 | Defect、修复与 Verification |
| 重构权限模块但外部行为不变 | Technical Refactoring | 不新建 | Engineering Change、回归 Evidence |
| 一条 REQ 含两个可独立验收义务 | Split and Supersession | 子义务新建 | RCL、新 REQ、RSP、Trace |
| 旧接口义务由新接口义务接替 | Supersession | 新旧并存 | RSP、迁移、有效边界 |

### 20.10 C04 质量检查清单

- [ ] 七类正式产物具有独立 ID、状态、Owner 和历史。
- [ ] REQ ID 永久、唯一、不可复用且不含版本或状态。
- [ ] 每条 REQ 只有一个 Authoritative Statement。
- [ ] 每条 Statement 只有一个规范性关键词和一个独立义务。
- [ ] 主体、动作、对象、条件、阈值、单位、时间和例外可唯一解释。
- [ ] Primary Type 来自十类受控集合且只有一个。
- [ ] Source、Rationale、PRD/Feature、Applicability、Priority、Criticality 和 Owner 完整。
- [ ] Current Revision、Verification、Acceptance、Trace、Risk/Assumption 和时间完整。
- [ ] 实现技术具有真实 Constraint 来源。
- [ ] 模糊词、开放式量词、代词、比较级和多义连接词已关闭。
- [ ] RQS 固定成员 REQ ID 与 Revision，不复制 Statement。
- [ ] RQS 完整性、一致性、整体可行性、可理解性和可确认性均通过。
- [ ] Candidate、Stale、Rejected、Superseded、Retired REQ 未计入当前覆盖。
- [ ] RQR 同时覆盖单项与集合质量。
- [ ] Patch 具有“不改变独立义务、行为、约束、Applicability 和 Acceptance”的证据。
- [ ] Revision 具有同一业务意图证据和完整影响分析。
- [ ] New Requirement 具有新的独立可验证义务证据。
- [ ] Defect Fix 未被伪装为 New Requirement。
- [ ] Technical Refactoring 未被伪装为 Product Requirement。
- [ ] Supersession、Split、Merge 保留旧 ID、历史和有效边界。
- [ ] Approved 内容变化已重新评审；Baselined 内容变化具有 C11 Change Request。
- [ ] 新 Revision、Snapshot、Change、Review、Gate 和 Baseline 可追踪。
- [ ] Agent 生成候选保留 Run、输入和人类确认。
- [ ] 高 Criticality 或专业 Requirement 已完成独立评审和扩展检查。
- [ ] Requirement Ready 阻断项为零。
- [ ] 两组 ISO 标准版本新鲜度已在基线前复核。

### 20.11 正反例

正例：

```text
当已认证用户连续 5 次提交错误密码时，身份认证服务必须在第 5 次失败后的 1 秒内将该账户锁定 15 分钟。
```

该 Statement 具有单一主体、单一锁定行为、明确触发、次数、时限和持续时间。登录审计记录是另一项可独立验证义务，必须建立独立 REQ。

反例：

```text
系统应快速、安全地登录用户，并记录所有相关信息，必要时通知管理员。
```

不符合原因：包含认证、记录和通知三个独立义务；“快速”“安全”“所有相关信息”“必要时”无判定条件；主体、阈值、通知触发和对象不明确。

Patch 与 Revision 反例：

```text
原阈值为 2 秒，修改为 1 秒，但登记为“文字澄清”。
```

阈值变化改变验收含义，必须分类为 Requirement Revision；已基线时必须进入 C11 Change Request。

### 20.12 参考的国际标准条款映射总表

| 参考 | 条款 | 公开主题 | C04 落地位置 | 采用方式与限制 |
|---|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | 4.4 | 信息项内容符合性 | 第 12、13、15、20 章 | 七类产物具有字段、模板和检查；不声明完整符合 |
| ISO/IEC/IEEE 29148:2018 | 4.5 | 裁剪符合性 | 第 17 章 | P2 保留身份、字段和控制结果 |
| ISO/IEC/IEEE 29148:2018 | 5.2.3 | Need 向 Requirement 转换 | 第 8.4、9.2–9.4、10.4 章 | 上游对象作为来源，不复制事实源 |
| ISO/IEC/IEEE 29148:2018 | 5.2.4 | Requirement 构造 | 第 10.1–10.3、20.2 章 | 原子 Statement 骨架与检查 |
| ISO/IEC/IEEE 29148:2018 | 5.2.5 | 单项 Requirement 特性 | 第 14.1、15.1–15.3、20.10 章 | 建立十项单项质量准则 |
| ISO/IEC/IEEE 29148:2018 | 5.2.6 | Requirement Set 特性 | 第 10.7、13.3、14.2、20.3 章 | 检查覆盖、一致、整体可行、可理解和可确认 |
| ISO/IEC/IEEE 29148:2018 | 5.2.7 | Requirement 语言准则 | 第 5.4、10.2–10.3、15.1 章 | 禁止不可判定语言；工具结果仍需人工复核 |
| ISO/IEC/IEEE 29148:2018 | 5.2.8 | Requirement 属性 | 第 10.4–10.6、13.2、20.2 章 | 建立 ID、来源、责任、Revision、Priority、Criticality、Verification 和 Trace |
| ISO/IEC/IEEE 29148:2018 | 5.3 | 实践考虑 | 第 7、9、10.14–10.15 章 | 规定角色、迭代、评审和工具边界 |
| ISO/IEC/IEEE 29148:2018 | 5.4 | Requirement 信息项 | 第 8.1、12、13 章 | REQ/RQS 作为内部正式信息项 |
| ISO/IEC/IEEE 29148:2018 | 6.3–6.4 | Stakeholder 与 System/Software Requirements 定义 | 第 3、8.4、9、16 章 | 建立来源和下游承接，不替代 C01–C03/C06 |
| ISO/IEC/IEEE 29148:2018 | 6.6.1 | Requirements management 概览 | 第 7–13、16 章 | 管理身份、状态、Revision、Owner 和关系 |
| ISO/IEC/IEEE 29148:2018 | 6.6.2 | Change management | 第 9.7、10.8–10.13、16.2 章 | 区分六类演进并连接 C11 |
| ISO/IEC/IEEE 29148:2018 | 6.6.3 | Requirements measurement | 第 14.3、15 章 | 记录质量与覆盖指标；不替代 Gate |
| ISO/IEC/IEEE 29148:2018 | 7、8.1–8.5、9.1–9.6 | 信息项、纲要与内容 | 第 12、13、20.1–20.8 章 | 建立内部模板；不复制标准模板正文 |
| ISO 10007:2017 | 4.1 | 职责和权限 | 第 7、10.14–10.15 章 | 分离 Author、Reviewer、Authority 和 Approver |
| ISO 10007:2017 | 4.2 | Dispositioning authority | 第 7、10.8、11.4 章 | 分类、批准、替代和退役由授权人决定 |
| ISO 10007:2017 | 5.2 | 配置管理策划 | 第 8、9、16–18 章 | 定义 Requirement 配置控制接口 |
| ISO 10007:2017 | 5.3.1 | 配置项选择 | 第 8.1、10.1、12 章 | REQ/RQS 及演进记录具有独立身份 |
| ISO 10007:2017 | 5.3.2 | 配置信息 | 第 13、16 章 | 保留 Revision、状态、关系和历史 |
| ISO 10007:2017 | 5.3.3 | 配置基线 | 第 9.6、10.14、11.1、17 章 | Baselined 固定 Revision/Snapshot 并引用 C11 |
| ISO 10007:2017 | 5.4.2 | 变更需要的提出、标识与记录 | 第 9.7、10.8、13.8 章 | 触发必须分类并形成 RCL |
| ISO 10007:2017 | 5.4.3 | 变更评价 | 第 10.8–10.13、13.4–13.8 章 | 记录影响、Risk、身份和控制流 |
| ISO 10007:2017 | 5.4.4 | 变更处置 | 第 7、10.14、11.4 章 | 授权人批准分类和处置 |
| ISO 10007:2017 | 5.4.5 | 变更实施与验证 | 第 9.6–9.7、10.9–10.13、16.2 章 | 连接新 Revision、Snapshot、Verification 和生效 |
| ISO 10007:2017 | 5.5.1–5.5.3 | 配置状态记账、信息与报告 | 第 11、13、14.3、16.2–16.3 章 | 保留当前状态、记录、报告和不可变历史 |
| ISO 10007:2017 | 5.6 | 配置审核 | 第 14–15 章、20.10 | Ready/Baseline 前执行身份、版本、内容和关系检查 |
| ISO 10007:2017 | Annex A | 配置管理计划结构与内容 | 第 18、19.3 章 | 仅作为 C11 接口参考；不复制指导性正文 |
