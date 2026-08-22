---
name: run-web-product-workflow
description: 按团队 V6.3 Candidate 规范推进 Web 产品或工程变化，用同一六元模型在 Minimal 聚合载体与完整流程之间确定性裁剪，并维护需求、计划、执行、验证、验收、发布和证据。用于新产品、新功能、需求修订、缺陷或工程变更、迁移退役、生产处置，或用户明确要求 Grill Me、Task Profile、Artifact Manifest、VC-PPG-PRO-001、C01-C12、E01-E05 或“最轻框架”时。
---

# Web 产品生产流程

## 总原则

保持人的操作简单，把正式治理留在后台：

1. 先检查仓库、文档、环境和既有 Baseline，再提问。
2. 只向人询问无法发现且会改变目标、范围、验收、风险或授权的信息。
3. 把未填写的非必填项设为默认值；用户回复“默认”时直接采用推荐默认值并记录依据。
4. 对人使用通俗中文。除非用户要求审阅治理细节，不展示 Task Profile、Artifact Manifest、状态模型和规范代码。
5. 不推测批准人、授权范围、验收结果、事实证据或风险接受结论。
6. 不因任务较小删除控制目标；缩放实例数量、物理载体、内容深度和派生视图。
7. 相同事实只维护一份权威定义；其他文件引用或按需生成视图。
8. 所有问题拆解、方案制定和重大修订必须完整应用 [第一性原理执行规范](references/first-principles-method.md)：先分离事实、约束、假设和未知，再从基础要素、因果链、真实备选方案和决策标准推导计划；禁止用惯例或类比代替证据。

## 读取规范

先完整读取 [规范源路由图](references/spec-source-map.md) 和 [第一性原理执行规范](references/first-principles-method.md)。涉及项目文档创建、整理、迁移或 README 时，再完整读取 [项目文档目录与迁移规范](references/project-document-layout.md)。只在输入包含平台签发的 Token 提示词时，再完整读取 [平台接入说明](references/platform-bootstrap.md)。

本 Skill 的规范快照、映射和 Schema 是 `assets/runtime/` 下的机器运行资产，由 `assets/runtime/embedded-manifest.json` 将稳定逻辑路径解析为物理路径。禁止从当前工作目录、父目录、同级目录、环境变量或外部仓库查找、回退或覆盖同名规范。任一必需资产缺失、未登记、越界或哈希不符时，所有正式生成、校验和登记入口均停止并报告 Skill 包不完整。

禁止向上下文递归读取 `assets/runtime/norms/` 全部文件。只能先编译 Norm Packet、Source Pack 和 Retrieval Plan，再通过有界条款查询获取当前动作所需原文；原始运行资产不是人类阅读入口。

按当前任务应用完整规则、只加载相关上下文：

- 始终应用公共术语、六类元类型与137个兼容Profile、137→6映射、P2完整裁剪决议、VC-PPG-TAIL-001 和跨规范Profile归属索引；默认由解析器执行，不把全文放入上下文。
- 始终应用 VC-PPG-PRO-001 的八阶段顺序、任务类型路由、阶段进入/退出、组合和 Emergency 规则；只加载当前 Stage 的控制卡和源章节定位。
- 始终保持 C02、C05、C07-C12 的最小治理闭环；只读取当前阶段命中的原文章节。
- 新产品、产品定义、需求、验收或设计变化分别读取 C01-C06 中被触发的规范。
- 仅在触发条件成立或为 Unknown 时读取并激活 E01-E05。
- 将当前 V6.3 标记为 Candidate/In Review/Proposed 时，只作为候选规则执行；不得声称其已批准或已建立正式 Baseline。Skill 包只发布 V6.3 Candidate 快照；V6.2/V6.2.1 通过规范仓 Git 历史或用户提供的旧任务包兼容读取。

禁止在 `SKILL.md` 中重新定义六类元类型、137个兼容Profile、状态模型、风险等级或国际标准映射。规范正文与规范映射只在 `AI-Native的产品开发生产规范` 仓库修订；Skill 实现、脚本、引用包装和运行快照只在 `LFen-Skills/run-web-product-workflow` 修订。规范模板目录、`.codex` 与 `.agents` 入口必须以 Junction 指向该唯一 Skill 源；运行时以内置发布快照为唯一规范事实源。

### 确定性裁剪与上下文编译

1. 首次使用或规范变化后运行 `scripts/audit_tailoring_coverage.py`；闭包失败即停止。Task Profile、合并代数、阻断条件和 Gate 以 VC-PPG-DEC-001、VC-PPG-PRO-001 与 VC-PPG-TAIL-001 为唯一权威定义，Skill 只调用解析器，不内联重定义。
2. 默认载体使用 `scripts/governance_artifacts.py` 计算 `tailoring_resolution`；禁止手工编造。Task Profile、规则表或 Source Snapshot 变化后，用 `scripts/refresh_tailoring_resolution.py` 原子修订并重新编译。
3. 默认载体使用 `scripts/compile_norm_context.py` 生成 Norm Packet、Source Pack 和 `retrieval-plan.json`，再把计划中的 `request_template` 保存为 JSON，仅填写 `action` 与 `query_text` 后调用完整查询入口：

```console
python scripts/query_norm_context.py --task-dir <task-directory> --request-json-file <UTF-8-request.json>
```

4. `Complete` 消费带引用的 Clause Context；`Expanded` 按返回事件读取父章节、完整命中源或分页；`Blocked` 停止受影响动作。查询层保持 `Shadow` DerivedView，不构成 Authority、Gate、发布或 Baseline 结论。

首次采用的项目没有本地 Ready 索引时，`query_norm_context.py` 必须从受 Manifest 保护的 Skill 发布资产执行 runtime-only 一致性审计，生成内容寻址本地索引和发布元数据；不得要求消费项目复制或伪造规范开发项目的 `T-015` TaskOutcome。显式诊断时可运行 `build_norm_index.py --bootstrap-task-dir <task-directory>`，或运行 `audit_norm_retrieval.py --validate-only --runtime-only` 验证受保护运行契约。运行态从 `Ready` 冻结为 `Frozen` 只改变 `lifecycle_state/frozen_at`，Retrieval Plan 使用排除这两个运行态字段的规范化契约摘要；其他 TaskContract 变化仍使计划陈旧。

首次规范查询尚无 `query-history/<TaskID>` 是合法初态；`rebuild_query_history_index.py` 必须创建该目录并索引完整活动发布。查询意图分类使用词法边界和显式复合词排除；`数据库/database/metadata` 不得仅因包含“数据/data”片段而激活 Data Control，明确的“数据”、`data` 或 `dataset` 意图仍须激活。

正式启用前运行 `scripts/audit_norm_shadow.py`，显式传入已批准的中位数、单例、强制覆盖和错误放行阈值。只把 `ReadyForIndependentReview` 解释为技术证据就绪；独立复核、人工验收和发布批准仍须分别核验，禁止由评测结果代替。

Shadow 阈值、算法、Legacy Baseline 与代表性样本必须由结构化 CHG Authority 唯一绑定；CLI 值只能精确匹配。评测结论写入 `evaluations/<TaskID>/publications/<digest>/` 的不可变快照，`active-publication.json` 只作活动指针；禁止覆盖既有结论或把 Legacy 固定路径当作当前结果。

仅在诊断查询运行时、或 Query Result 明确返回 `Expanded` 且指向 Source Pack 时，使用以下 `rg` 模式。`rg` 不是正常查询入口，不得绕过 `Blocked`、Authority 或 Gate，不对运行资产目录执行全量读取：

```console
rg -n 'SOURCE-BEGIN|^#{1,6} |VC-PPG-|C0[1-9]|C1[0-2]|E0[1-5]' <norm-source-pack.md>
rg -n '<当前动作关键词>|Gate|Authority|Evidence|Outcome|必须|禁止|不得' <norm-source-pack.md>
```

## AI Native Product Operating System 平台接入

只在输入包含平台签发的完整 Token 提示词时激活本分支。必须执行“读取规范”中链接的平台接入说明完整流程；未触发时不加载该参考文件。

## 接收最小输入

只要求用户提供一项必填内容：

```text
期望结果（对应原“需求描述”）：
- 任务类型：默认由 Agent 判断；可写新产品/新功能/优化/缺陷修复/工程变更/内容配置/迁移替代退役/生产处置
- 当前情况：默认由 Agent 检查现有材料
- 希望变成什么：【必填】
- 验收示例：默认由 Agent 提议，二次确认时由人确认
- 明确不做：默认无额外排除项
```

采用以下默认值，不要求用户改写：

- 目标产品、仓库、目录和环境：自动发现。
- 截止时间：无固定期限。
- 参考资料：使用当前可访问材料。
- 额外约束：无；已发现约束仍然生效。
- 敏感数据或合规要求：未声明；必须通过检查和追问确认，禁止据此判为不存在。
- 验收决策：由发起人在验收门禁时确认；这不等于预先认定其具有组织授权。
- 发布决策：仅在涉及发布时，发布前确认有权角色。

若用户已经给出更多信息，直接吸收，不要求按模板重填。

## 选择 Minimal 聚合载体

把用户所称“最轻框架”实现为同一六元模型的 Minimal 物理载体裁剪，不建立第二套任务档位。优先级固定为：硬边界 > 用户显式选择 > 自动判定。

只有 `Risk=Low`、可逆、单一 Scope、无外部系统副作用、无生产发布、无安全/隐私影响、E01-E05 全部 Inactive、无阻断 Unknown 或专用 Gate 时，才使用 `.project-governance/tasks/<TaskID>/task-record.json` 聚合 TaskContract、RunLedger 和 TaskOutcome。完整资格与升级触发以 VC-PPG-DEC-001 §16.4 为唯一事实源。

满足资格时：

- 用户写“采用最轻框架”则直接选择；自动判定成立时主动告知默认采用 Minimal。
- 无歧义且用户已明确要求执行时，Grill Me 为零轮，S1 摘要与首次回复合并，不重复询问 `Proceed`。
- 跳过 Norm Packet、Source Pack、Retrieval Plan 和逐动作 Shadow 查询；收尾时仍重建 ProjectState，审核视图可一次生成或批处理。
- 使用 `scripts/manage_minimal_task.py init|append|close|validate`。执行中跨越任一硬边界时停止受影响动作，再用 `scripts/init_task.py --upgrade-minimal-reason <reason> --upgrade-minimal-basis <evidence-ref> ...` 单向升级；禁止完整载体降回 Minimal。

## 执行 Grill Me 多轮澄清

先检查、后提问，并遵循以下循环：

1. 每轮只问 3-5 个最能消除歧义的问题。
2. 问题使用业务语言，给出推荐默认答案；允许用户回复“全部默认”。
3. 每轮结束后等待用户回答，不在同一轮自行假定答案并继续。
4. 没有会改变目标、范围、验收、风险或授权的未知时为零轮；存在未知时按需要完成 1-5 轮，未对齐前不得执行。
5. 每轮更新“已确认、Agent 判断、仍待确认”，不重复已回答问题。
6. 当继续提问不会改变目标、范围、验收、关键约束或风险时停止。
7. 若出现 High/Critical、不可逆变化、生产发布、权限扩大、安全/隐私影响或风险接受，必须单独向有权人类确认。

第一轮优先澄清“为谁解决什么问题、希望出现什么行为、怎样算完成”。后续轮次再澄清边界、异常、数据、权限、兼容、发布和观察。

每轮澄清必须同步修订第一性原理分析：已证实内容进入 Facts，项目或规范边界进入 Constraints，待验证判断进入 Assumptions，缺失信息进入 Unknowns。不得把推荐方案提前写成用户需要。

## 使用 Ask 处理澄清后的人工停点

Ask 指当前宿主提供的用户提问工具，例如 `request_user_input`、`ask_user` 或等价能力。以下规则只在 Grill Me 需求澄清结束后生效；需求澄清仍按上一节使用文字问题逐轮等待回答。

1. 当前会话存在 Ask 且当前模式允许调用时，所有需要等待人的中间确认、选择或外部操作完成通知必须使用 Ask；不得只在回复末尾要求用户手工输入固定选项。
2. 每次 Ask 只展示当前门禁需要的 1-3 个问题。每题提供 2-3 个互斥短选项，把有事实支持的推荐项放在第一位并标记“推荐”；若工具自动提供 `Other`，不得重复添加同义选项。
3. 对话本身可以承载的流程确认直接展示决定选项。仍存在推进选择时，S2 使用 `Proceed / Revise / Stop`；用户已明确要求执行同一清晰范围时不重复询问。两者都不构成资产批准、Gate、风险接受、发布或 Baseline 决定。
4. 必须在 AI Native Product Operating System 平台完成的正式决定，先通过平台 MCP 创建或定位待决项并向用户给出准确入口，再使用 Ask 询问“是否已在平台提交”，固定提供 `已提交（推荐） / 尚未提交 / 提交遇阻`：
   - 选择“已提交”后，立即按当前 Project、Task、Decision ID 和消费游标读取平台权威结果；核对对象、Revision、Scope、Authority、Outcome、时间和有效性。
   - “已提交”只触发恢复读取，不是批准、决定或 Approval Evidence。禁止把 Ask 点击、聊天回复、沉默或工具调用成功写成正式决定。
   - 结果有效时按平台 Outcome 继续、修订、拒绝、停止或转入下一门禁；可继续时直接推进到下一个真实停点，不再追问“是否继续”。
   - 未读到结果、结果仍为 Draft/Pending、游标未前进、对象不匹配、过期或冲突时，报告准确状态并保持 Fail-Closed；问题处理后再次使用同一组 Ask 选项。
   - 选择“尚未提交”时给出平台入口和待完成动作；选择“提交遇阻”时给出可执行诊断或升级路径。两者均不得继续受门禁影响的动作。
5. 必须在其他外部系统完成的复核、签署、发布准备或证据提交采用同一模式：Ask 只确认完成状态，随后从权威事实源核验；不能核验时保持 Pending/Blocked。
6. Ask 不存在或当前模式禁止调用时，退化为包含同组选项的简短文字询问并等待用户回复；禁止静默采用推荐项、模拟 Ask 或越过人类门禁。
7. High/Critical、不可逆变化、生产发布、权限扩大、安全/隐私影响、例外、风险接受和最终 Gate 必须各自单独提问并核验 Authority，不得与普通进度确认合并。
8. 平台或其他权威事实源已经提供有效结果时，直接消费并继续，不重复要求用户确认“已提交”。

## 建立执行前 TaskContract

澄清结束并取得明确执行指令后，按载体资格初始化 Minimal 或默认任务记录。以下为默认载体的 Task Profile：

```text
Execution Scope =
Delivery Scenario
× Development Type
× Development Type Scopes（多类型时逐项绑定）
× Change Surfaces
× C02 Risk Level
× E01-E05 Extension Triggers
× Applicability Facts
× Baseline Inheritance
× Normal/Emergency Mode
```

同时记录：

- ProjectID、WorkItemID、TaskID、ordinal、depends_on、supersedes、blocked_by；
- 目标、In Scope、Out of Scope、允许路径和禁止动作；
- 权限、Authority 引用、Stop Condition、Gate、Acceptance、计划、验证和回退；
- 每项判断的事实依据；
- VC-PPG-TAIL-001 的全部 Applicability Facts；
- E01-E05 的证据引用；Retiring/Retired 状态禁止无证据；
- 当前 Stage 的确定性 `tailoring_resolution`；
- High、Medium 或 Low 置信度；
- 未决问题及其 Owner；
- 哪些结论来自用户确认，哪些来自 Agent 检查；
- 需要人类决定的门禁。
- `first_principles_analysis`：结果、事实、约束、假设、未知、基础要素、因果链、备选方案、决策标准、选定方案、计划追踪、验证与来源引用。

只使用 C02 的 `Low / Medium / High / Critical`，禁止创建任务挡位或第二套风险等级。Emergency 作为执行模式叠加，不作为开发类型。

优先调用：

```console
python scripts/init_task.py --project-root <root> --project-id <P-ID> --work-item-id <W-ID> --task-id <T-ID> --ordinal <N> --objective <text> --acceptance <criterion> --in-scope <scope> --delivery-scenario DS-03 --development-type DT-06 --change-surface Agent/Collaboration --baseline-inheritance Revise --tailoring-stage S1 --applicability-fact actual_execution=Yes --applicability-fact authority_available=Yes
```

生成器自动捕获 Git Source Snapshot，包括已 `git init` 但尚无 Commit 的 `UNBORN` 仓库，并默认写入 TaskContract、RunLedger、TaskOutcome 三个必需 Manifest 项。Task Profile 只使用规范受控值：`DS-01..DS-04`、`DT-01..DT-09`、8 类 Change Surface 以及 `New / Reference / Revise / Supersede`；不得自建 `automation`、`defect-fix` 等别名。任务具有多个 Development Type 时必须传入主类型；E01-E05 和 Applicability Fact 未判定时分别保持 `Not Evaluated` 和 `Unknown`，不得默认写成 `Inactive` 或 `No`。进入 S4 前必须逐项关闭会阻断执行的 Unknown 并刷新快照。

命令默认权限为 `read / edit-in-scope / validate`。任务命中 `external_system_effect=Yes` 或 `production_release=Yes` 时必须显式增加 `--execution-permission external-effect`；需要执行回滚事件时必须增加 `--execution-permission rollback`。声明权限不代替平台实际授权、`allowed_paths`、`forbidden_actions` 和 Stop Condition。

结构化 JSON 优先使用脚本 `--help` 中实际提供的 `--*-json-file <UTF-8-json>`；只有同一参数组明确列出 `--*-json-base64` 时才允许 Base64。输入文件不是第三份治理产物。

```powershell
$jsonB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content -LiteralPath <input.json> -Raw -Encoding utf8)))
```

```bash
json_b64="$(python -c 'import base64,sys; print(base64.b64encode(open(sys.argv[1],"rb").read()).decode())' <input.json>)"
```

Run 第一个事件写入时 TaskContract 自动冻结。`run_started` 前必须把裁剪快照刷新到 S4 或更晚且 blocker 为空。一个 Task 的账本只使用一个 RunID。验证失败时先追加 `failure`，再用新 AttemptID 追加 `retry`；`run_finished` 后禁止追加。后续范围、验收、权限、分类或计划变化必须使用 `scripts/amend_record.py`；涉及 Task Profile 时优先使用 `scripts/refresh_tailoring_resolution.py` 原子更新，禁止直接覆盖。

## 生成产物清单

Artifact Manifest 是 `before.json` 和 `after.json` 的字段，只列当前任务实际创建、修订、引用或已触发的元类型/Profile。动作仅使用：

- `Create/Revise`
- `Reference`
- `Generate`
- `On Event`
- `N/A`

遵循以下规则：

1. 稳定且未变化的 Baseline 内容使用 `Reference`。
2. 查询、评审、审计或 Gate 需要的矩阵和报告使用 `Generate`。
3. Failure、Incident、Waiver、Risk Acceptance 等事实未发生时不创建空记录；发生后使用 `On Event`。
4. `N/A` 必须引用规则、事实依据、范围、Owner 和重新评估触发点；Unknown、High/Critical 无独立依据或扩展冲突时禁止使用。
5. AuthorityAsset 可以保留原生格式并共享载体，但必须保持身份、Profile、字段、状态、关系和历史可区分。
6. VCM/DCM/BTM/RCR/ALR/VDR 等作为 DerivedView 生成；VER/VAE 保存权威证据；CAS/CCS/FER 语义进入 TaskOutcome。
7. 不创建独立 Task Profile、Artifact Manifest、ECP、AEP、RUN、TIL、CAS、CCS 或 FER 文件；旧Profile只用于兼容读取。
8. `after.json` 的终态 Manifest 必须保留全部冻结计划项及其计划字段，只增加 Outcome；收尾时实际产生的 ProjectState、DerivedView 或其他资产可作为新项追加，但必须使用 `Created / Revised / Referenced / Generated` 的实际 Outcome。TaskOutcome 建立后追加时必须通过 Amendment。

需要机器校验时运行：

```console
python scripts/validate_task_package.py <task-directory> --check-mapping --execution-ready
python scripts/audit_tailoring_coverage.py
python scripts/compile_norm_context.py --task-dir <task-directory> --stage S4 --enforce
python scripts/query_norm_context.py --task-dir <task-directory> --request-json-file <UTF-8-request.json>
python scripts/audit_norm_shadow.py --project-root <root> --project-id <P-ID> --task-id <T-ID> --task-dir <task-directory> --output-dir <evaluation-directory> --approval-ref <authority-ref> --median-reduction-threshold <percent> --minimum-case-reduction-threshold <percent> --mandatory-coverage-threshold 100 --false-allow-threshold 0 --publication-state pre-review
```

旧V6.2/V6.2.1任务包仍可直接传给同一校验器兼容读取。

## 管理项目文档

新任务初始化时同步创建 `.project-governance/README.md`、`LG_project_docs/README.md` 和基础目录。`.project-governance/` 以外的新产品原生文档统一进入 `LG_project_docs/requirements/<RequirementID>/<DocumentType>/`；没有可靠 RequirementID 时使用 TaskID，仍无法确定时进入 `_intake/unclassified/<DocumentType>/`。仓库级 README/License/贡献说明、代码组件 README 和应用运行静态资产按 [项目文档目录与迁移规范](references/project-document-layout.md) 处理例外。

优先调用：

```console
python scripts/manage_project_docs.py init --project-root <root>
python scripts/manage_project_docs.py ensure-requirement --project-root <root> --requirement-id <RequirementID-or-TaskID>
python scripts/manage_project_docs.py validate --project-root <root>
python scripts/manage_project_docs.py refresh-readme --project-root <root>
```

项目首次采用本 Skill 时必须检查旧文档目录。命令必须包含完整必填参数：

```console
python scripts/manage_project_docs.py plan-migration --project-root <root> --migration-id <MigrationID>
python scripts/manage_project_docs.py apply-migration --plan <migration-plan.json> --confirm-plan-sha256 <sha256> --authorized-by <evidence-ref>
```

先向用户展示计划路径、文件数、未分类项和计划文件 SHA-256；只有用户明确确认同一摘要后才应用。工具先按原路径建立逐文件哈希备份，再复制到新活动目录，全部验证通过后才移除旧位置文件；不递归删除旧目录。完成后报告备份位置、移动结果、未分类和冲突。

## 按原流程推进

阶段名称、顺序、进入/退出和任务类型路由以 VC-PPG-PRO-001 为唯一事实源。保持代码目录习惯；产品原生文档必须遵守本 Skill 的项目文档目录契约。下列内容只是面向人的交互实现摘要，不得覆盖正式规范：

1. **初次澄清**：检查材料；只在存在实质未知时执行 Grill Me。
2. **二次确认**：给出通俗任务摘要、默认项、未决问题和验收示例；仍存在推进选择时用 Ask 等待 `Proceed / Revise / Stop`。
3. **条件深化**：只在产品、新功能或需求修订时生成 PRD；只在 UI 变化且需要视觉决策时生成 HTML/PNG；只在设计或扩展规范触发时深化对应内容。
4. **计划**：将唯一执行计划写入 TaskContract，列范围、步骤、验证、风险、回退和所需人类门禁。
5. **执行**：按冻结的 TaskContract 修改；Git保存代码/文档Diff，RunLedger只追加变更、失败、重试、验证、外部副作用、门禁和回滚事件。普通读取和搜索不记录，不保存敏感原文。
6. **验证与验收**：先由 Agent 运行可复核验证，再由人作验收决定；需要平台决定时用 Ask 接收“已提交”通知并读取权威结果，工具成功不等于验收通过。
7. **发布与观察**：仅在适用时执行；发布、回滚、风险接受和观察结论由有权角色决定，并按“Ask + 权威事实源核验”的模式恢复执行。
8. **收尾**：生成 TaskOutcome，记录 `Implemented / Deferred / Cancelled / Blocked / Superseded`、已成立事实、验证、遗留问题、理由、责任人和后继 TaskID；随后重建 ProjectState 和需要的 DerivedView。

使用以下载体：

- `.project-governance/tasks/<TaskID>/before.json`：执行前TaskContract。
- `.project-governance/tasks/<TaskID>/run.jsonl`：最小只追加RunLedger。
- `.project-governance/tasks/<TaskID>/after.json`：任务终态TaskOutcome。
- `.project-governance/tasks/<TaskID>/task-record.json`：仅限 Minimal 资格成立时聚合上述三类逻辑对象。
- `.project-governance/project-state.json`：生成的跨任务当前状态，禁止直接编辑。
- `.project-governance/authority/`：按触发保存原生格式的需求、设计、决定、证据和基线。
- `.project-governance/generated/reviews/`、`generated/matrices/`：按需生成的人类审核视图；每个 Markdown 视图同时生成符合 `derived-view.schema.json` 的 `.view.json` 来源与完整性封套。
- `.project-governance/generated/contexts/<TaskID>/<Stage>/`：按阶段生成 Norm Packet、完整 Source Pack 和 Shadow Retrieval Plan DerivedView；不是权威事实源。
- `LG_project_docs/requirements/<RequirementID>/<DocumentType>/`：PRD、需求、设计、HTML/PNG 评审稿、决定、验证、发布和参考资料等原生产品文档。
- `LG_project_docs/_archive/legacy-migrations/<MigrationID>/`：旧文档原路径备份、清单和迁移报告。

旧`*_需求澄清备案*.md`和`*_执行计划.md`只作兼容读取，不再是新任务默认载体。PRD、设计和HTML/PNG仅在专业触发成立时作为AuthorityAsset原生内容创建。

执行与收尾优先调用：

```console
python scripts/append_run_event.py <task-directory> --run-id <RUN-ID> --attempt-id <A-ID> --event-type <type> --summary <text> --status <status>
python scripts/refresh_tailoring_resolution.py <before.json> --stage S4 --reason <reason> --basis <basis>
python scripts/compile_norm_context.py --task-dir <task-directory> --stage S4 --enforce
python scripts/register_authority_asset.py --project-root <root> --project-id <P-ID> --asset-id <ID> --legacy-kind <Profile> --title <title> --owner <owner> --state <state> --revision <revision> --content-ref <native-file-or-url> --source <source> --scope <scope> --profile-fields-json-file <UTF-8-json-object-file>
python scripts/close_task.py <task-directory> --status <result> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python scripts/rebuild_project_state.py --project-root <root> --project-id <P-ID>
python scripts/generate_review_views.py --project-root <root> --project-id <P-ID>
```

`generate_review_views.py` 默认使用 Skill 内嵌索引，从任意项目目录执行都不依赖当前工作目录。只在验证其他固定 Revision 的索引时显式传入 `--profile-index <absolute-path>`。

## 维护与诊断入口

- `scripts/amend_record.py`：按 Amendment 修订已建立记录；禁止直接覆盖。
- `scripts/self_test.py --project-root <governed-project-root>`：运行完整正反向自检；项目根必须已存在 `.project-governance`。普通脚本产生的 `__pycache__` 不影响自检，且自检不依赖 Python `assert`。
- `scripts/sync_embedded_references.py --spec-root <norm-repository>`：从规范事实源刷新快照与 Manifest。
- `scripts/migrate_legacy_artifacts.py`：兼容读取旧治理产物，不承担产品原生文档迁移。
- `scripts/audit_norm_integration.py`、`scripts/audit_norm_consistency.py`：发布前诊断；前者仅用于具备 `T-008/S5` 规范开发快照的规范仓库，消费项目使用后者的 `--runtime-only`；`scripts/audit_norm_retrieval.py` 额外依赖 `requirements.txt` 中声明的 `jsonschema`。
- `scripts/rebuild_query_history_index.py`：从合法的活动查询集创建或重建查询历史索引。

## 面向人的输出

每次只展示当前阶段需要的信息：

```text
当前结论
默认采用
需要你回答/决定
下一步
```

二次确认固定展示：

```text
要解决的问题
期望结果
本次会做
本次不做
如何验收
主要风险或未知
采用的默认项
Ask：Proceed / Revise / Stop
```

把正式规范代码、完整关系矩阵和未触发产物留在后台记录中。仅在用户要求审阅、Gate 需要或出现冲突时展开。

## 权限与事实边界

- 允许 Agent：发现上下文、分类、起草、维护追踪、生成派生视图、运行检查和报告缺口。
- 必须由人完成：目标和验收确认、范围取舍、批准、发布、例外、剩余风险接受和最终 Gate。
- Ask 只是交互和恢复通道；正式决定、批准和 Gate 仍以其权威事实源为准。只有 S2 或明确允许以当前对话承载的普通选择，才能直接采用 Ask 选项结果。Authority Reference 必须具有 `authority_assessments`；占位引用、自报 Valid 但无 Evidence、过期或未覆盖当前 Scope 都不允许执行。
- 发现冲突、越权、关键证据不足或 Stop Condition 时立即停止受影响动作并升级。
- Emergency 可先执行恢复服务或控制损害所必需的动作，但必须补齐事实记录、变化、验证、风险、批准和事后评审。
