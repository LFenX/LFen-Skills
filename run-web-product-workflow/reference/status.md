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
