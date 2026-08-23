# 内置规范源路由图

## 1. 路径和事实源

- 唯一编辑事实源：`LFen-Skills/run-web-product-workflow`；规范正文、规范映射、Schema、评测集和 Skill 实现都只能在该处修订。本 Skill 自带完整规范，不镜像也不依赖任何外部规范仓库。
- 统一入口：规范模板目录、`.codex` 与 `.agents` 中的同名路径必须是指向该事实源的 Junction，不得保留平行可编辑副本。
- 运行规范事实源：Skill 的 `assets/runtime/`；其中的规范、映射和 Schema 是受哈希保护的机器运行资产。
- 稳定逻辑路径：TaskContract、Norm Packet 和历史记录继续使用 `references/...`、`mappings/...`、`schemas/...`。
- 物理路径：`assets/runtime/embedded-manifest.json` 把逻辑路径唯一解析为磁盘路径。规范逻辑路径 `references/<分类>/...` 对应 `assets/runtime/norms/<分类>/...`；`mappings/...` 对应 `assets/runtime/mappings/...`；`schemas/...` 对应 `assets/runtime/schemas/...`。禁止把逻辑路径当作 skill 根下的文件打开，也禁止绕过 Manifest 自行拼接。
- 命令卡在 `commands/`。本目录 `references/` 只放 skill 说明，不是规范快照目录；以 `references/` 开头的规范逻辑路径解析到 `assets/runtime/norms/`。
- 任一必需资产缺失、未登记、越界、重复或哈希不符时失败关闭。

## 2. 固定治理源与索引

| Source ID | 稳定逻辑路径 | 读取时机/检索词 |
|---|---|---|
| VC-PPG-COM-001 | `references/01_治理基线/Vibe_Coding_公共术语与规范性用语基线_V6.3.md` | 始终；术语、规范性用语、事实边界 |
| VC-PPG-COM-002 | `references/01_治理基线/Vibe_Coding_受控产物目录与状态模型_V6.3.md` | 始终；六元类型、Profile、状态 |
| VC-PPG-DEC-001 | `references/01_治理基线/Vibe_Coding_P2裁剪与扩展规范适用性决议_V6.3.md` | 始终；裁剪、并集、失败关闭、Minimal 载体资格 |
| VC-PPG-PRO-001 | `references/01_治理基线/Vibe_Coding_任务类型裁剪与统一执行流程规范_V6.3.md` | 始终；阶段、任务类型、出入条件 |
| VC-PPG-IDX-001 | `references/05_记录与登记册/V6.3_跨规范产物归属索引.md` | 始终；Profile 归属、消费方、实例策略 |

## 3. 核心规范 C01-C12

| Source ID | 稳定逻辑路径 | 读取时机/检索词 |
|---|---|---|
| C01 | `references/02_核心规范/C01_Product_Discovery_Evidence_and_Intent_Standard.md` | Need、Evidence、Intent |
| C02 | `references/02_核心规范/C02_Initiative_and_Scope_Standard.md` | 始终；Scope、Risk、Initiative |
| C03 | `references/02_核心规范/C03_PRD_and_Feature_Standard.md` | PRD、Feature、外部行为 |
| C04 | `references/02_核心规范/C04_Atomic_Requirement_and_Evolution_Standard.md` | Requirement、Revision、Migration |
| C05 | `references/02_核心规范/C05_Acceptance_Verification_and_Validation_Standard.md` | 始终；Acceptance、Verification、Validation |
| C06 | `references/02_核心规范/C06_UX_and_Technical_Design_Standard.md` | Design、UI/UX、技术方案 |
| C07 | `references/02_核心规范/C07_Human_Agent_Collaboration_Standard.md` | 始终；Authority、Ask、人机边界 |
| C08 | `references/02_核心规范/C08_Agent_Context_Governance_Standard.md` | 始终；Context、Snapshot、裁剪 |
| C09 | `references/02_核心规范/C09_Agent_Execution_and_Evidence_Standard.md` | 始终；Run、Evidence、Permission |
| C10 | `references/02_核心规范/C10_Decision_Traceability_and_Lineage_Standard.md` | 始终；Decision、Trace、Lineage |
| C11 | `references/02_核心规范/C11_Configuration_Version_Baseline_and_Change_Standard.md` | 始终；Change、Version、Baseline |
| C12 | `references/02_核心规范/C12_Review_Quality_Gate_and_Product_Health_Standard.md` | 始终；Review、Gate、Outcome |

## 4. 扩展规范 E01-E05

| Source ID | 稳定逻辑路径 | 读取时机/检索词 |
|---|---|---|
| E01 | `references/03_扩展规范/E01_Architecture_Governance_Extension_Standard.md` | Architecture、多仓、边界 |
| E02 | `references/03_扩展规范/E02_Security_Privacy_and_Compliance_Extension_Standard.md` | Security、Privacy、Compliance |
| E03 | `references/03_扩展规范/E03_Data_and_AI_Data_Governance_Extension_Standard.md` | Data、AI、Model、Dataset |
| E04 | `references/03_扩展规范/E04_Knowledge_and_Records_Governance_Extension_Standard.md` | Knowledge、Record、Retention |
| E05 | `references/03_扩展规范/E05_Product_Operations_and_Service_Management_Extension_Standard.md` | Operations、Release、Rollback、SLO |

## 5. 读取和校验策略

1. 先校验 Manifest 的44个受保护文件（22 norm、3 mapping、11 schema、3 skill-reference、2 evaluation、3 asset-template），再校验22源、17标准、137 Profile 和全部受控维度闭包。物质动作前运行 `<skill-root>/scripts/get_context.py`，不要直接 Read 下表逻辑路径。
2. 由 Task Profile、Applicability Facts 和 Stage 编译 `norm-packet.md`、`norm-source-pack.md` 与 `retrieval-plan.json`。
3. Source Pack 必须包含固定治理源、索引、已适用和待判定标准的完整原文与逐文件 SHA-256。
4. Norm Packet 只是非穷尽导航；物质动作前从 Retrieval Plan 生成有界查询，优先消费带引用的 Clause Context。
5. 查询结果为 `Expanded` 时按回退事件读取父章节、完整命中源或有序分页；`Blocked` 时停止，不得用 `rg` 绕过。
6. Source Pack 始终保留为完整命中源回退；Unknown、Pending、冲突、过期或哈希错误从配置阶段起失败关闭。
7. 条款查询层保持 `Shadow`；Candidate、In Review 或 Proposed 必须保留原状态，禁止写成 Approved 或 Baselined。
8. 修订 `assets/runtime/` 下任一受保护资产后，必须运行 `<skill-root>/scripts/sync_embedded_references.py` 就地重算并重封 Manifest；禁止手工编辑登记哈希，禁止从父目录、工作目录、环境变量或任何外部仓库读取规范。
9. 消费项目缺少本地 Ready 索引时，使用受 Manifest 保护的 runtime-only 发布资产建立内容寻址缓存；禁止向消费项目复制开发任务历史充当授权。
10. 只有 VC-PPG-DEC-001 §16.4 的 Minimal 资格全部成立时，才跳过第 2–5 项的 Shadow 派生物；`task-record.json` 仍须由结构校验器检查并进入 ProjectState。

## 6. 发布信任根

`embedded-manifest.json` 只证明 Skill 包内受保护文件与登记哈希一致，不证明发布来源可信。

发布信任根是 `LFen-Skills/run-web-product-workflow` 所在 Git 提交；维护者发布时建议使用 annotated tag，例如 `rwpw-v6.3.0-candidate`。消费方校验当前发布快照时运行：

```console
python <skill-root>/scripts/self_test.py --project-root <project-root>
```

本 Skill 不要求 Agent 流程自建 GPG 或 PKI。Tag、签名和仓库访问策略由维护者本地发布流程管理。
