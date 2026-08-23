# status

无参数或只问“现在状态”时先跑：

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

```console
python <skill-root>/scripts/signals.py --project-root <project-root>
```

输出 JSON 包含：

- blocking_unknowns：仍阻断的 Unknown。
- pending_acceptance_tasks：未收尾任务。
- snapshot_stale：TaskContract Source Snapshot 与当前仓库差异。
- minimal_eligibility_facts：已有 Minimal 资格事实。
- update_available：本地索引与当前 skill 运行快照不一致时提示。
- recommended_commands：2-3 个建议命令和理由。

`signals.py` 只报告，不自动执行推荐命令。

`signals.py` 的 `derivation_audit` 按 C10 §8.2 关系符号分开统计衍生：`affected-by`（本次引入）计入回归链深，`observed-from`（顺带发现）单独计数——前者链长说明修复方式有系统性问题，后者多则相反。`recorded_but_not_created` 列出已记录为衍生目标但项目里尚不存在的任务，那是「发现了却没人接手」的线索。

需要人来审计时生成审计台：

```console
python <skill-root>/scripts/generate_audit_console.py --project-root <project-root> --project-id <ProjectID>
```

产出 `generated/reviews/audit-console.html`，自包含单文件，可直接用浏览器打开。它是 DerivedView，可随时重建，按 C10 §8.0 不得作为新追踪事实的唯一来源。

同目录存在 `before.json` 时以完整载体为准，忽略 stray `task-record.json`。Minimal `lifecycle_state=Upgraded` 不是可执行活跃任务；若没有其他待验收任务，才推荐用 `init_task.py` 的升级参数完成完整载体，禁止对该 Minimal 继续 `run` / `verify` / `close`。Upgraded 残留不得取消其他待验收任务的 `run` 建议。

口语入口映射：

| 口语 | 先映射 |
|---|---|
| 修 bug / 缺陷 | 缺陷或工程变更；若有产品面再进入本 skill |
| 新页面 / 新功能 | 新功能或产品定义变化 |
| 最轻框架 | 先判 Minimal 硬边界 |
| 迁移 / 退役 | 迁移替代退役 |
| 发布 / 回滚 | 生产处置或发布观察 |

写入 Task Profile 时仍必须落到受控 DS/DT/Change Surface。
