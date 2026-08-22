---
name: run-web-product-workflow
description: 按团队 V6.3 Candidate 规范推进 Web 产品或工程变化，用同一六元模型在 Minimal 与完整流程之间裁剪，并维护需求、计划、执行、验证、验收、发布和证据。用于新产品、新功能、需求修订、带产品面的缺陷修复或工程变更、迁移退役、生产处置，或用户明确要求 Grill Me、Task Profile、Artifact Manifest、VC-PPG、C01-C12、E01-E05 或“最轻框架”时。Not for read-only Q&A, git one-liners, or edits that do not change product behavior, docs layout, or release. Not for backend-only library patches with no Web product surface.
metadata:
  version: 6.3.0-candidate
---

# Web 产品生产流程

## 总原则

保持人的操作简单，把正式治理留在后台。

1. 先检查仓库、文档、环境和既有 Baseline，再提问。
2. 只向人询问无法发现且会改变目标、范围、验收、风险或授权的信息。
3. 用户回复“默认”时采用推荐默认值并记录依据。
4. 对人使用通俗中文；除非用户要求审阅治理细节，不展示完整规范矩阵。
5. 不推测批准人、授权范围、验收结果、事实证据或风险接受结论。
6. 不因任务较小删除控制目标；只裁剪实例数量、物理载体、内容深度和派生视图。
7. 相同事实只维护一份权威定义；其他文件引用或按需生成。
8. 问题拆解、方案制定和重大修订必须应用 [第一性原理执行规范](references/first-principles-method.md)。

## 路径约定

- `<skill-root>`：本 `SKILL.md` 所在目录。所有治理脚本都是 `<skill-root>/scripts/...`，禁止在消费项目的 `scripts/` 下寻找同名文件。
- `<project-root>`：含 `.project-governance/` 的消费项目根。不等于 skill 根；工作区若是本 skill 子目录，项目根通常是上一级 Git 仓。
- `reference/`：命令卡。`references/`：skill 说明（路由图、第一性原理、文档布局）。
- 规范逻辑路径形如 `references/01_治理基线/...`，磁盘文件在 `assets/runtime/norms/`；禁止把逻辑路径当 skill 根下的文件打开。产品文档里的 `LG_project_docs/.../references/` 是需求外部资料，与规范快照无关。
- 本 skill 不读取平台 Token、不安装平台插件、不调用平台绑定接口。

## 读取分流

完整载体或不确定是否 Minimal 时，先读 [规范源路由图](references/spec-source-map.md) 和 [第一性原理执行规范](references/first-principles-method.md)。

已确定符合 Minimal 资格时，不完整读取 `spec-source-map.md`；只有存在会改变目标、范围、验收、风险或授权的未知时，才完整读取第一性原理参考。

涉及项目文档创建、整理、迁移或 README 时，再读 [项目文档目录与迁移规范](references/project-document-layout.md)。

禁止递归读取 `assets/runtime/norms/` 全部文件。完整载体物质动作前只运行一次：

```console
python <skill-root>/scripts/get_context.py --task-dir <project-root>/.project-governance/tasks/<TaskID> --action <action> --query-text <current-action-summary>
```

返回 `Blocked` 时停止受影响动作；返回 Clause Context 时消费其引用。只有合法且未升级、未收尾的 Minimal 任务调用该命令才会说明跳过查询并 exit 0。本地 norm index 只保留当前活动 digest。

## 路由

用户第一词匹配命令时，只读对应文件：

| 命令 | 读取 |
|---|---|
| init | [reference/init.md](reference/init.md) |
| clarify | [reference/clarify.md](reference/clarify.md) |
| plan | [reference/plan.md](reference/plan.md) |
| run | [reference/run.md](reference/run.md) |
| verify | [reference/verify.md](reference/verify.md) |
| close | [reference/close.md](reference/close.md) |
| status | [reference/status.md](reference/status.md) |
| migrate | [reference/migrate.md](reference/migrate.md) |
| minimal | [reference/minimal.md](reference/minimal.md) |

意图可唯一映射时直接进入对应命令；例如“修 bug/缺陷”先判是否有产品面，再判 Minimal 资格，随后走 `minimal` 或 `run`。两可时只问一次。无参数时读取 `reference/status.md` 并运行：

```console
python <skill-root>/scripts/signals.py --project-root <project-root>
```

口语入口可以映射到受控 DS/DT/Change Surface；写入 Task Profile 时必须使用受控值，禁止把 `defect-fix`、`automation` 等别名写进记录。

## Minimal 硬边界

用户所称“最轻框架”只能实现为同一六元模型的 Minimal 物理载体裁剪，不建立第二套任务档位、风险等级、流程、状态模型或元类型。

优先级固定：硬边界 > 用户显式选择 > 自动判定。

只有 `Risk=Low`、可逆、单一 Scope、无外部系统副作用、无生产发布、无安全/隐私影响、E01-E05 全部 Inactive、无阻断 Unknown、无专用 Gate 时，才使用 `<project-root>/.project-governance/tasks/<TaskID>/task-record.json` 聚合 TaskContract、RunLedger 和 TaskOutcome。完整资格与升级触发以 VC-PPG-DEC-001 §16.4 为唯一事实源。

满足资格时读取 [reference/minimal.md](reference/minimal.md)。无歧义且用户已明确要求执行时 Grill Me 为零轮，S1 摘要与首次回复合并，不重复询问 `Proceed`。执行中跨越任一硬边界时停止受影响动作并单向升级为完整载体；禁止完整载体降回 Minimal。

## 完整载体

不满足 Minimal、风险不明、范围不明、涉及规范快照/脚本运行契约、生产、不可逆、外部副作用、安全/隐私、High/Critical 或专用 Gate 时，使用完整三文件载体：

- `<project-root>/.project-governance/tasks/<TaskID>/before.json`：执行前 TaskContract。
- `<project-root>/.project-governance/tasks/<TaskID>/run.jsonl`：只追加 RunLedger。
- `<project-root>/.project-governance/tasks/<TaskID>/after.json`：终态 TaskOutcome。

首次 `run_started` 会冻结 TaskContract。之后 Scope、Acceptance、Authority、Plan 或 Task Profile 变化必须先停止受影响动作，再用 `<skill-root>/scripts/amend_record.py` 或 `<skill-root>/scripts/refresh_tailoring_resolution.py` 修订；禁止静默覆盖。

项目文档默认进入 `<project-root>/LG_project_docs/requirements/<RequirementID>/<DocumentType>/`；旧 `*_需求澄清备案*.md` 和 `*_执行计划.md` 只兼容读取，不再作为新任务默认载体。

## 事实与权限边界

允许 Agent：发现上下文、分类、起草、维护追踪、生成派生视图、运行检查和报告缺口。

必须由人完成：目标和验收确认、范围取舍、批准、发布、例外、剩余风险接受和最终 Gate。

Ask 只是交互和恢复通道；正式决定、批准和 Gate 以权威事实源为准。工具成功、聊天回复、沉默或 Ask 点击都不等于批准。

写治理文件或 skill runtime 文件前先按 [reference/run.md](reference/run.md) 调用 `<skill-root>/scripts/check_write_guard.py`。守卫失败只警告放行；守卫明确拒绝时停止该写入。

发现冲突、越权、关键证据不足或 Stop Condition 时立即停止受影响动作并升级。

## 维护入口

- `<skill-root>/scripts/amend_record.py`：按 Amendment 修订已建立记录。
- `<skill-root>/scripts/self_test.py --project-root <project-root>`：完整正反向自检。
- `<skill-root>/scripts/sync_embedded_references.py --spec-root <norm-repository>`：从规范事实源刷新快照与 Manifest。
- `<skill-root>/scripts/migrate_legacy_artifacts.py`：兼容读取旧治理产物，不迁移产品原生文档。
- `<skill-root>/scripts/audit_norm_consistency.py --project-root <project-root> --runtime-only`：消费项目 runtime-only 审计；正式规范仓审计必须显式传 `--task-id`。
- `<skill-root>/scripts/audit_norm_retrieval.py --validate-only --runtime-only`：验证受保护查询契约。
- `<skill-root>/scripts/rebuild_query_history_index.py --project-root <project-root> --task-id <TaskID> --reason <reason>`：合法初态可创建缺失的 query-history。

## 面向人的输出

每次只展示当前阶段需要的信息：

```text
当前结论
默认采用
需要你回答/决定
下一步
```

二次确认固定展示：要解决的问题、期望结果、本次会做、本次不做、如何验收、主要风险或未知、采用的默认项、Ask：Proceed / Revise / Stop。
