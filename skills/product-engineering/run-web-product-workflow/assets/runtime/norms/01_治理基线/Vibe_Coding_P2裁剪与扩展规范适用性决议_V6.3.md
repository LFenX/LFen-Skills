# Vibe Coding P2 裁剪与扩展规范适用性决议 V6.3 Candidate

| 文档属性 | 内容 |
|---|---|
| 文档编号 | VC-PPG-DEC-001 |
| 版本 | V6.3 Candidate |
| 状态 | Proposed |
| 决议日期 | 待评审；V6.2/V6.2.1 历史由 Git 保留 |
| 决议责任人 | 项目负责人 |
| 批准依据 | CHD-0004 Proposed；尚无 V6.3 人类批准 |
| 上位基线 | 尚未建立；V6.3 Candidate 不替代现有 Baseline |
| 适用范围 | V6.3 Candidate 规范文档的生成、评审、裁剪与后续应用；V6.2/V6.2.1 仅作历史兼容输入 |

## 1. 决议目的

本决议固定 V6.3 Candidate 规范体系的裁剪规则，区分“扩展规范是否需要编制”与“扩展规范是否在当前任务中激活”，并为 C01 至 C12、E01 至 E05 的生成和任务实例缩放提供无歧义输入。

本决议不修改 VC-PPG-BP-001 和 VC-PPG-BP-002 的编号、名称、职责、依赖关系或正式基线内容。

## 2. P2 裁剪决议

V6.3 Candidate 规范体系继承 **P2 标准档位**。P2 描述规范体系完整度，不是任务风险等级；任务实例只按同一元模型执行确定性裁剪。

强制执行规则如下：

1. C01 至 C12 必须分别形成独立正式规范文件，不得合并为 P1 文档。
2. 每份正式规范必须使用 VC-PPG-BP-001 规定的统一二十章结构。
3. VC-PPG-BP-002 为单项规范规定的必备内容必须映射到统一二十章结构，不得以专属章节列表替代统一结构。
4. 每项强制产物必须具备模板骨架和检查清单；模板可以作为所属规范附录，不要求拆分为独立文件。
5. 公共术语、规范性用语、受控关系、产物命名和状态模型作为跨规范公共基线独立管理。
6. C10、C11 和 C12 对 C01 至 C09 横向生效；C05 在 C03 至 C09 的相关阶段持续生效。
7. P2 不允许取消核心对象、永久标识、来源、责任人、版本、追踪、执行证据、变更记录和质量门禁。

## 3. 正式文件命名决议

C01 至 C12 使用 VC-PPG-BP-002 已给出的建议文件名，并将其确定为 V6.3 Candidate 规范文件名：

| 编号 | 正式文件名 |
|---|---|
| C01 | `C01_Product_Discovery_Evidence_and_Intent_Standard.md` |
| C02 | `C02_Initiative_and_Scope_Standard.md` |
| C03 | `C03_PRD_and_Feature_Standard.md` |
| C04 | `C04_Atomic_Requirement_and_Evolution_Standard.md` |
| C05 | `C05_Acceptance_Verification_and_Validation_Standard.md` |
| C06 | `C06_UX_and_Technical_Design_Standard.md` |
| C07 | `C07_Human_Agent_Collaboration_Standard.md` |
| C08 | `C08_Agent_Context_Governance_Standard.md` |
| C09 | `C09_Agent_Execution_and_Evidence_Standard.md` |
| C10 | `C10_Decision_Traceability_and_Lineage_Standard.md` |
| C11 | `C11_Configuration_Version_Baseline_and_Change_Standard.md` |
| C12 | `C12_Review_Quality_Gate_and_Product_Health_Standard.md` |

扩展规范正式文件名固定如下：

| 编号 | 正式文件名 |
|---|---|
| E01 | `E01_Architecture_Governance_Extension_Standard.md` |
| E02 | `E02_Security_Privacy_and_Compliance_Extension_Standard.md` |
| E03 | `E03_Data_and_AI_Data_Governance_Extension_Standard.md` |
| E04 | `E04_Knowledge_and_Records_Governance_Extension_Standard.md` |
| E05 | `E05_Product_Operations_and_Service_Management_Extension_Standard.md` |

禁止为同一规范建立中文名、缩写名或版本名不同的平行正式文件。翻译标题只能出现在同一正式文件的文档控制信息中。

## 4. 扩展规范适用性决议

扩展规范采用“双层适用性”判定：

- **编制适用性**：该扩展是否必须作为可复用规范模块进入 V6.3 规范体系。
- **当前激活状态**：该扩展的控制要求是否立即约束当前规范仓库的生产活动。

| 扩展 | 编制适用性 | 当前激活状态 | 判定依据 | 当前要求 |
|---|---|---|---|---|
| E01 架构治理 | 必须编制 | 未激活 | 当前仓库仅生产规范文档，不存在多服务、多仓库运行系统、关键容量或架构迁移 | 完成正式扩展规范；目标产品触发条件成立时激活 |
| E02 安全、隐私与合规 | 必须编制 | 未激活 | 当前仓库不处理账号、外部 API、个人信息、支付、密钥或监管业务数据 | 完成正式扩展规范；目标产品触发条件成立时激活 |
| E03 数据与 AI 数据治理 | 必须编制 | 未激活 | 当前仓库不生产分析数据、数据契约、模型训练、RAG 或评估数据集 | 完成正式扩展规范；目标产品触发条件成立时激活 |
| E04 知识与正式记录治理 | 必须编制 | 已激活 | 当前项目明确涉及 Coding Agent 上下文、长期规范维护、来源追踪、基线、审计与历史恢复 | 正式规范生成过程立即执行 E04 控制目标 |
| E05 产品运营与服务管理 | 必须编制 | 未激活 | 当前仓库没有生产服务、SLA/SLO、灰度、告警、值守或事故运行对象 | 完成正式扩展规范；目标产品触发条件成立时激活 |

所有五份扩展规范都必须编制，原因是本项目交付的是可复用的完整规范体系，而不是单个目标产品的裁剪实例。未激活表示不将对应运行控制强加于当前文档仓库，不表示允许删除该扩展规范。

## 5. 目标产品激活规则

具体 Web App 或 SaaS 采用本体系时，必须在 Discovery Ready 之前建立一份扩展适用性记录，并逐项回答 E01 至 E05 的全部触发条件。

判定规则如下：

1. 任一“必须启用”风险条件成立时，对应扩展状态必须设为“已激活”。
2. 任一“应启用”条件成立但决定不激活时，必须建立 Exception or Waiver Record，记录范围、理由、风险、责任人、批准人和失效时间。
3. 触发条件未知时，状态必须设为“待判定”，不得视为“未激活”。
4. 产品范围、数据、架构、外部暴露或运营方式发生变化时，必须重新执行适用性判定。
5. 未激活扩展的已识别风险仍必须进入 C02、C05、C06、C11 和 C12。

## 6. P2 交付集合

P2 基线完成前必须存在：

1. 公共术语与规范性用语基线；
2. 受控产物目录、必填信息和统一状态模型；
3. C01 至 C12 十二份独立核心规范；
4. E01 至 E05 五份条件扩展规范；
5. 各规范的模板骨架和检查清单；
6. 跨规范产物归属索引；
7. 跨规范引用和依赖检查报告；
8. V6.2 完整符合性检查报告；
9. 包含准确文件版本和批准信息的 Git 基线。

## 7. 变更控制

以下变化必须建立 Change Request，不得直接覆盖本决议：

- 从 P2 改为 P1 或 P3；
- 合并或拆分任一核心规范；
- 修改 C01 至 C12 或 E01 至 E05 的编号、正式名称或文件名；
- 取消任一扩展规范的编制；
- 修改 E04 当前激活状态；
- 取消模板、检查清单、追踪或质量门禁要求。

后续决议替代本文件时，必须保留本文件及其 Git 历史，并建立 `supersedes` 关系。

## 8. 符合性检查

本决议满足以下条件时有效：

- Git 中可定位上位蓝图标签 `v6.2-blueprint-baseline`；
- C01 至 C12 的正式文件名唯一；
- E01 至 E05 同时具有编制适用性和当前激活状态；
- P2 禁止裁剪项明确；
- 变更本决议需要受控记录。

## 9. V6.3 完整裁剪候选决议

### 9.1 P2 的解释

P2 要求十二份核心规范、五份扩展规范、六类正式元类型、137 个兼容领域 Profile、公共状态模型、模板能力、追踪和门禁能力在规范体系中完整。P2 不要求每个任务实例化全部 Profile，也不要求每个逻辑对象占用独立文件。

P2 的最小物理结构固定为：每个 TaskID 使用 `before.json`、`run.jsonl`、`after.json` 三份任务载体；项目级 `project-state.json` 从有效 TaskOutcome 与 AuthorityAsset 自动物化；长期需求、设计、决定和基线保留原生格式；审核矩阵、上下文包和报告作为 DerivedView 按需生成。

### 9.2 完整裁剪的定义

完整裁剪必须同时解决四个问题：

1. **规范适用性**：C01–C12、E01–E05 中哪些规范约束当前任务；
2. **控制强度**：适用规范按 minimum、standard、enhanced 或 maximum 执行到何种深度；
3. **Profile 实例化**：137 个 Profile 中哪些执行 `Create/Revise`、`Reference`、`Generate`、`On Event` 或 `N/A`；
4. **阶段上下文加载**：当前 S1–S8 阶段需要把哪些规则卡和源章节装入 Agent 上下文。

“不加载全文”不等于“不适用”，“不创建文件”不等于“不执行控制”，“共享物理载体”不等于“合并逻辑身份”。任何裁剪器只要没有同时回答以上四层，就不是完整裁剪器。

### 9.3 唯一机器规则伴随件

`Vibe_Coding_裁剪适用性规则_V6.3.json`（VC-PPG-TAIL-001）是本决议的机器可审计伴随件，必须与本决议共同修订。职责边界如下：

- 本决议定义语义、代数、优先级、禁止项和人类可读矩阵；
- VC-PPG-TAIL-001 穷举受控值、22 个规范源、17 个 C/E 标准、适用性事实、阶段路由、不可裁剪控制和 Profile 计数；
- VC-PPG-COM-002 与 VC-PPG-IDX-001 分别继续作为元类型/状态语义和 137 Profile 归属/实例语义的唯一来源；
- VC-PPG-PRO-001 继续作为 S1–S8 执行顺序与 Gate 的唯一来源。

机器表与本决议冲突、缺项、规则表哈希或 22 个规范源聚合哈希变化、或无法解析时，结果必须为 `Stop/Revise`，不得退回凭经验裁剪。

## 10. 适用性输入向量

### 10.1 分类输入

每个 TaskContract 的 Task Profile 必须包含：一个 Delivery Scenario、一个或多个 Development Type、一个 Primary Development Type、一个或多个 Change Surface、一个 C02 Risk Level、E01–E05 各自状态及其 `extension_evidence_refs`、一个或多个 Baseline Inheritance、一个 Execution Mode、Confidence、Basis 和 Open Questions。

Primary Development Type 只用于排序和展示。全部 Development Type 与 Change Surface 必须取并集，禁止用 Primary 值覆盖其他值。选择多个 Development Type 时，`development_type_scopes` 必须为每个类型绑定至少一个 `scope.in_scope` 中的精确值；DT-03/DT-07、DT-03/DT-08、DT-04/DT-05、DT-05/DT-07、DT-05/DT-08 等语义冲突组合不得共享同一子范围，否则 S4 fail-closed。机器校验只能证明字段值精确引用且显式相等时冲突；两个不同文本是否在业务语义上重叠，必须由独立 Review 或人类 Gate 复核。

分类事实必须与类型和变更面一致：架构、安全、数据、运营/发布事实为 Yes 时必须分别包含 Architecture、Identity/Security/Privacy、Data/AI、Deploy Surface；迁移/退役事实为 Yes 时必须包含 DT-09；产品意图、需求或外部行为变化必须包含 VC-PPG-TAIL-001 指定的相容 Development Type。事实与标签不一致时保留双方并形成 blocker，禁止选择控制更少的一方。

### 10.2 适用性事实

分类标签不能覆盖所有触发条件。Task Profile 还必须逐项记录以下事实，值只允许 `Yes`、`No`、`Unknown`：

| 事实 | Yes 时至少激活 | 目的 |
|---|---|---|
| product_intent_change | C01 | 识别产品意图、证据或 Discovery 变化 |
| initiative_scope_change | C02 | 识别 Initiative、Scope 或边界变化 |
| requirement_change | C03、C04 | 识别功能或原子需求变化 |
| external_behavior_change | C03、C05 | 识别用户或外部系统可观察行为变化 |
| design_change | C06 | 识别 UX、接口、数据、失败或回退设计变化 |
| architecture_impact | E01 | 识别架构边界、依赖或多仓变化 |
| security_privacy_impact | E02 | 识别身份、安全、隐私或合规影响 |
| data_ai_impact | E03 | 识别数据、Schema、模型、RAG 或评估数据影响 |
| formal_knowledge_records | E04 | 识别正式知识、记录、保留或检索要求 |
| operations_impact | E05 | 识别服务管理、可观测性或运行影响 |
| production_release | C11、C12、E05 | 识别生产发布、回退和观察要求 |
| irreversible_change | C02、C07、C11、C12 | 识别不可逆动作和加强 Gate |
| actual_execution | C09 | 区分建议/审阅与实际改变状态 |
| authority_available | C07、C12 | 证明受影响动作具有有效 Authority |
| migration_retirement | C04、C11、C12 | 识别迁移、替代、停用和退役边界 |
| external_system_effect | C09–C12 | 识别仓库外副作用和证据要求 |
| formal_review_or_gate | C10、C12 | 识别正式评审、批准或 Gate 决定 |

S1–S3 可以保留明确的 Unknown 并指定 Owner。S4 起，影响执行、权限、扩展、安全、数据、不可逆性、外部副作用或发布的 Unknown、`blocking=true` Open Question、`blocked_by` 非空或 Low Confidence 必须阻断受影响动作。Unknown 禁止转换为 No、Inactive、N/A 或 Low Risk。

## 11. 裁剪合并代数

### 11.1 并集与最强控制

任务适用规范按以下集合取并集：

`Always ∪ DS ∪ all(DT) ∪ all(Surface) ∪ Risk ∪ Extension ∪ Facts ∪ Baseline ∪ Mode`

Stage 只选择当前上下文，不从任务适用集合中减项。多个规则命中同一规范时执行最强控制，不平均、不抵消、不以文件数量为判断依据。

### 11.2 优先级

发生差异时按以下顺序解析：

1. 法律、Policy、已批准 Baseline 与责任人范围内的明确 Authority；
2. Critical > High > Medium > Low 的控制强度；
3. 已激活扩展和明确事实 > 通用分类路由；
4. 所有 Development Type 与 Change Surface 的并集；
5. Delivery Scenario、Baseline、Mode 和 Stage 的增加规则；
6. 所属专业规范的 Profile 专用规则 > 通用 Profile 规则；
7. 同级规则冲突时保留双方、记录冲突并停止受影响动作。

### 11.3 禁止减项的维度

以下信息只能改变执行深度、引用方式或加载范围，不能移除已适用控制：Primary Development Type、Stage、`Reference`、Emergency、物理载体合并、DerivedView 未生成、任务规模小、时间紧、已有 Git 历史或“Agent 能记住”。

### 11.4 风险强度

| Risk | 强度 | 额外要求 |
|---|---|---|
| Low | minimum | 仍保留 Scope、Acceptance、Authority、Evidence 和 Gate |
| Medium | standard | 增加标准 Trace、Change 和 Review 深度 |
| High | enhanced | 独立复查；禁止无据 N/A；关键 Unknown 必须关闭 |
| Critical | maximum | 独立复查和明确人类 Gate；不得由 Agent 接受剩余风险 |

## 12. C01–C12 完整适用性矩阵

“始终最低适用”表示每个正式任务至少执行所列不可裁剪控制，不表示每个阶段加载全文。

| 规范 | 适用触发 | 不可裁剪控制 | 可缩放内容 |
|---|---|---|---|
| C01 | DS-01；DT-01/DT-02；产品意图事实 Yes | 产品身份与意图链、证据/推断分离、Assumption/Unknown、Discovery Gate | Discovery 深度、研究方法、视图数量 |
| C02 | 始终最低适用；Scope/Risk 事实 Yes 时加深 | In/Out Scope、Risk、Boundary、Dependency、Unknown 不得冒充 Low/N/A | Initiative 说明深度、独立资产数量 |
| C03 | DS-01/DS-02；DT-01/02/03/05；需求或外部行为事实 Yes | 可观察行为、状态/边界、Requirement-Acceptance 关系、替代链 | PRD 载体、示例数量、说明深度 |
| C04 | 需求增删改、缺陷关联、迁移替代退役；DT-01–06/09 | 原子身份、Revision/Supersession、Defect 关联、迁移边界 | 单独 Requirement 文件数量 |
| C05 | 始终最低适用；行为、质量、接口、数据、权限、部署或缺陷变化时加深 | Acceptance、Verification Evidence、Validation Conclusion、失败/阻断可见 | 验证方法和矩阵视图 |
| C06 | 任何 UX/API/Data/Identity/AI/Architecture 设计面或 design_change=Yes | Surface 决定、接口/数据契约、失败/回退、设计追踪 | 设计稿形式和拆分数量 |
| C07 | 始终最低适用 | Accountable Human、Authority Boundary、Stop/Escalation、人类 Gate 不得自批 | 协作说明长度和视图 |
| C08 | 始终最低适用 | Context 来源/版本、优先级/新鲜度、Assumption/Conflict、Context Delta | 已知稳定上下文用 Reference |
| C09 | 始终最低适用；actual_execution=Yes 时完整执行三载体和账本 | 执行前契约、重要事件顺序、终态事实、副作用/Evidence | 禁止要求逐工具调用全量日志 |
| C10 | 始终最低适用 | Source→Change、Decision Authority、跨 Task Lineage、DerivedView 非权威 | 矩阵按需 Generate |
| C11 | 始终最低适用；Revision/Baseline/Change/Release/退役时加深 | Source Snapshot、Revision/Amendment、Change ID、Baseline/Supersession/Rollback | 稳定资产用 Reference |
| C12 | 始终最低适用 | Entry/Exit Gate、必要独立复查、人类 Acceptance、Residual Risk/Health | Review 载体和报告视图 |

任何 Task Profile 至少得到 C02、C05、C07、C08、C09、C10、C11、C12 的最低控制闭包。某项没有发生实际事件时，控制结论可以是“不发生/不适用且有依据”，不能删除判定过程。

## 13. E01–E05 完整激活与生命周期

### 13.1 扩展状态语义

| 状态 | 规范适用性 | S4 起规则 |
|---|---|---|
| Active | 适用 | 加载全部适用控制 |
| Conditionally Active | 适用 | 加载触发、边界、Gate 和命中控制 |
| Retiring | 适用 | 保留活动控制并增加退役/后继边界；必须有退役计划/决定 Evidence 引用 |
| Retired | 不适用当前活动 | `extension_evidence_refs` 必须包含退役证据；新触发出现时重新激活或提供有效替代规则 |
| Inactive | 不适用 | 所有触发事实必须为 No，且不得存在 Surface/DS 触发 |
| Pending | 未决 | 阻断受影响执行 |
| Not Evaluated | 未决 | 阻断受影响执行 |

### 13.2 扩展触发闭包

| 扩展 | 触发事实/路由 | 不可裁剪控制 |
|---|---|---|
| E01 Architecture | architecture_impact=Yes；Architecture/Multi-repo | 架构边界、决定/依赖、多仓影响、架构风险与验证 |
| E02 Security/Privacy | security_privacy_impact=Yes；Identity/Security/Privacy | 身份/访问、Threat/Vulnerability、Privacy/Obligation、安全 Evidence 与剩余风险 |
| E03 Data/AI Data | data_ai_impact=Yes；Data/Schema；AI/Data Governance | Source/Lineage、Schema/Quality、License/Permitted Use、Retention/Deletion |
| E04 Knowledge/Records | formal_knowledge_records=Yes | Classification、Source/Version/Freshness、Retention/Disposition、Legal Hold/Retrieval |
| E05 Operations/Service | operations_impact 或 production_release=Yes；Deploy/Operations；DS-04 | Release/Rollback、SLO/Observability、Incident/Problem、Feedback Closure |

Trigger 命中而状态为 Inactive/Retired、关键 Trigger 为 Unknown、或 Active 状态没有 Authority/Scope 时，必须形成冲突并停止受影响动作。Waiver 只能由有权人类在允许范围和时限内作出，不能由 Agent 自动把扩展改为 Inactive。

## 14. 137 Profile 实例化闭包

### 14.1 所有权闭包

VC-PPG-IDX-001 第 4 章列出的 137 个 Profile 必须且只能各有一个 Owner Standard。VC-PPG-TAIL-001 的 17 个 `profile_count` 总和必须为 137，审计器必须同时验证 Profile Code 无重复、Owner 无孤儿、六元类型映射无遗漏。

### 14.2 实例动作解析

1. Owner Standard 不适用时，其 Profile 默认不实例化；裁剪快照保存 Owner 级依据，不要求在 Artifact Manifest 展开 137 行 N/A。
2. Owner Standard 适用时，按 VC-PPG-IDX-001 第 9 章解析：有效稳定 Baseline 优先 `Reference`；权威内容新建或变化使用 `Create/Revise`；派生视图按需 `Generate`；事件事实仅在事件发生时 `On Event`；其余有完整依据时才允许 `N/A`。
3. `N/A` 必须包含规则引用、事实依据、Scope、Owner 和重新评估触发点。Unknown、无权限、无时间或“没有模板”不是 N/A 依据。
4. 同一物理载体可以承载多个逻辑 Profile，但每个 Profile 必须保留独立 ID、Meta Type、Legacy Kind、State、Revision、Owner、Scope、Trace 和 History。
5. TaskContract 的 `profile_coverage_digest` 证明当前适用 Owner 集映射到哪些 Profile；需要逐 Profile 审核时由编译器生成 DerivedView，不复制为新的 AuthorityAsset。

### 14.3 三类任务事实与长期资产

- `before.json` 保存执行前的目标、范围、权限、验收、计划、Task Profile、适用性事实、裁剪快照和 Artifact Manifest；
- `run.jsonl` 只记录重要执行事件、失败、重试、验证、外部副作用和 Evidence 引用；Git Diff 保存代码/文档具体变化；
- `after.json` 保存已成立事实、实际变化、验证结论、未完成项、遗留问题、决定和后继 TaskID；
- 长期需求、设计、决定、例外、基线和正式记录按 Profile 触发保存为 AuthorityAsset；
- 审核矩阵、状态页、上下文包和迁移表按需生成 DerivedView。

## 15. S1–S8 阶段加载规则

Stage 决定 Agent 当前先看什么，不改变任务适用性。默认编译规则如下：

| Stage | 当前最小上下文 | Unknown 处理 |
|---|---|---|
| S1 初次澄清 | C02、C07、C08、C10 与已触发专业规范的 Trigger/Scope | 记录、分派 Owner |
| S2 Scope/Acceptance | C02、C05、C07、C12 | 记录、分派 Owner |
| S3 Requirement/Design | C05、C10、C11、C12 与全部命中 C01/C03/C04/C06/E | 关闭执行阻断事实 |
| S4 Plan/Readiness | C02、C05、C07–C12 与全部激活 E | fail-closed；有 blocker 不得启动 Run |
| S5 Execution | C05、C07–C12 与全部激活 E | 停止受影响动作 |
| S6 Verification/Outcome | C05、C09–C12 与全部激活 E | 不得宣称 Passed/Implemented |
| S7 Release/Observation | C05、C07、C09–C12 与 E05/其他激活 E | 不得 Release/关闭观察 |
| S8 Closure/State | C09–C12；正式记录时含 E04 | 保留未决项并建立后继 TaskID |

编译器同时生成两层 DerivedView：小型 Norm Packet 只保存控制卡、Profile 计数、规则 ID、源路径与优先章节定位；Complete Norm Source Pack 保存全部治理源、索引、已适用标准和待判定标准的完整 UTF-8 原文与逐文件 SHA-256。控制卡和章节定位只是非穷尽导航，绝不是全部规范义务；物质动作前必须在 Source Pack 中搜索并读取约束该动作的原文，无法安全缩小时读取完整命中源。TaskContract 必须同时保存规则表 SHA-256、22 个规范源加 Profile 映射的聚合 SHA-256、解析器 SHA-256、TaskContract Schema SHA-256 和完整命中源清单；任一来源或执行实现变化后旧快照和旧包立即失效。

## 16. 重新分类、失败封闭与执行 Gate

### 16.1 强制重新分类事件

以下任一变化必须修订 TaskContract、重新计算裁剪快照并重新编译阶段上下文：Scope、Acceptance、Authority、Risk、任一 DT/Surface、扩展状态、Baseline、Mode、适用性事实、新 Evidence、Source Snapshot、稳定引用的新鲜度、外部副作用、不可逆动作、生产发布或人类 Gate。

Run 开始后的变化必须通过 Amendment 留痕；实际影响后续执行的变化同时写入 RunLedger。禁止只改标签或直接覆盖旧值。

### 16.2 失败封闭条件

以下情况必须 `Stop/Revise`：

- 规则表缺失、解析失败、哈希不匹配或没有覆盖某受控值；
- Task Profile 缺少任何必填维度或适用性事实；
- S4 起存在阻断 Unknown、Pending、Not Evaluated；
- S4 起 Confidence 为 Low、存在 Blocking Open Question 或 `blocked_by` 非空；
- Inactive/Retired 扩展与 Fact、Surface 或 DS Trigger 冲突；
- Authority 缺失、越界、过期或互相冲突；
- `authority_available=Yes` 但任一 Authority 引用未绑定结构化评估、状态非 `Valid`、缺少 Evidence、验证时间在未来、已过期、未覆盖全部 `scope.in_scope` 或评估作用域无法精确解析；当前 Fact 或 Run Event 缺少 `read / edit-in-scope / validate / external-effect / rollback` 中必需的受控权限；High/Critical 缺少 `independent-review`，Critical 缺少 `human-acceptance`，安全/隐私、生产发布或不可逆变化分别缺少 `security-privacy-review`、`release-approval` 或 `irreversible-change-approval` Gate 计划；
- High/Critical 缺少独立复查，Critical 缺少明确人类 Gate；
- Artifact Manifest 使用无据 N/A、预建虚构事件记录或把 DerivedView 当成 Authority；
- Primary Type、Stage、Reference、Emergency 或载体选择导致已适用控制被删除。

### 16.3 执行与终态 Gate

S4 及以后只有裁剪快照无 blocker 时才允许 `run_started`。S6 只有必要 Verification 有 Evidence 且无 Required Failed/Blocked 时才能形成 Implemented。S8 必须保留所有未完成项、原因、影响、Owner、重新进入条件和后继 TaskID；关闭任务不得把 Unknown 静默改成 No。

### 16.4 Minimal 物理载体裁剪

Minimal 是同一六元模型下的物理载体裁剪结果，不是新的任务档位、风险等级、流程、状态模型或元类型。选择优先级固定为：硬边界高于用户显式请求，用户显式请求高于自动判定。

只有以下事实全部成立时，才允许使用 `.project-governance/tasks/<TaskID>/task-record.json` 聚合承载 TaskContract、RunLedger 和 TaskOutcome：

1. C02 Risk 为 `Low`；
2. 变化可逆，且回退路径已记录；
3. `scope.in_scope` 只有一个可独立验收的 Scope；
4. `external_system_effect=No`；
5. `production_release=No`；
6. `security_privacy_impact=No`；
7. E01 至 E05 全部为 `Inactive`；
8. 不存在阻断 Unknown、权限扩大、独立复核或专用 Gate。

Minimal 仍必须记录唯一 TaskID、目标、单一 Scope、允许路径、Authority 引用、一句可验证 Acceptance、选定方案、未采用替代方案的理由、实际变化、验证结果、终态和升级检查。未提供的非阻断字段由脚本写入可追溯默认值，并在 basis、事实或约束中标明脚本默认来源。它可以跳过 Norm Packet、Source Pack、Retrieval Plan、逐动作条款查询和每任务即时 DerivedView；原因是资格事实已证明没有扩展规范、专用 Gate 或外部副作用，且 Shadow 查询不产生治理结论。ProjectState 必须索引 Minimal 任务；DerivedView 可以在收尾时一次生成或批处理。

无歧义且用户已经明确要求在已声明范围内执行时，S1 摘要可以与首次回复合并，Grill Me 为零轮，S2 不重复要求 `Proceed`；必须保存该用户指令引用。若仍有会改变目标、Scope、Acceptance、风险或授权的问题，Minimal 不得用于绕过澄清。

执行中出现 Scope 扩大、Risk 升级、不可逆变化、生产发布、安全/隐私影响、外部系统副作用、任一 E01–E05 激活、权限扩大或专用 Gate 时，必须先停止受影响动作，记录触发事实和原因，再单向升级为默认三文件载体和完整流程。只允许 Minimal → 默认载体；禁止默认载体 → Minimal。

## 17. 符合性、审计与候选边界

### 17.1 完整性检查

符合本决议必须自动证明：

1. 四份治理规范、C01–C12、E01–E05 和跨规范索引共 22 个规范源各出现一次；
2. DS-01–04、DT-01–09、八类 Change Surface、四级 Risk、七种 Extension State、四种 Baseline、两种 Mode、S1–S8、17 个 Applicability Fact、五种实例动作和五种 Execution Permission 全部覆盖；
3. 17 个标准全部可从 Always、分类、Surface、Fact 或扩展规则到达；
4. 每个标准具有存在于源文档中的章节定位和非空不可裁剪控制；
5. 137 个 Profile 无重复、无孤儿、Owner 计数与六元类型映射一致；
6. 正向场景得到正确并集，反向场景能拒绝 Unknown、冲突、过期快照、非法 N/A、占位 Authority、任一未评估/非 Valid/过期/作用域不全的 Authority、权限不足和越权执行；
7. 源 Skill 与安装镜像的规范、规则表、Schema 和生成器哈希一致。

结构审计通过只证明规则闭包，不等于业务事实正确、Evidence 内容真实、文本作用域语义完全不重叠、风险已接受、人类已验收或 Candidate 已批准。`required_gates` 只是事前计划的转换控制，不是 Gate 已通过的证据；消费受保护转换前必须从其 Authority 事实源验证实际 Outcome。

### 17.2 人类确认

Agent 完成环境检查、Task Profile、适用性事实和裁剪快照后，人类可以作出 `Proceed`、`Revise` 或 `Stop`。High/Critical、不可逆变化、生产发布、权限扩大、安全/隐私影响、Waiver 和风险接受必须由具有 Authority 的人类单独决定。

### 17.3 生效边界

VC-PPG-TAIL-001、VC-PPG-PRO-001 与本决议均为 V6.3 Candidate / In Review。CHD-0004、CHD-0005 及后继决议、独立 Review、Human Acceptance、Gate Decision 和新 Baseline 未完成前，不得宣称替代已批准的 V6.2.0 事实。

### 17.4 统一流程规范候选注册

VC-PPG-PRO-001 统一 DS-01–04、DT-01–09 的 S1–S8 顺序、阶段 Gate、组合任务和 Emergency 叠加。它不是 C13，不新增第七个元类型，不替代 C01–C12、E01–E05 的 Profile、专业控制、Evidence 或 Gate。
