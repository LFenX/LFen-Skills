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

历史终态缺少新增证明时按兼容规则读取，保留原状态；项目状态、审阅视图与控制台展示 `proof_validation`，其中 `HistoricalNotRevalidated` 表示未追溯补验当前证明，不能表述为当前门禁已通过。活动任务的证明状态表示待终态核验。原始结构或血缘损坏仍须报告，不能用历史兼容掩盖。规则见 [verify](verify.md)。

`pending_acceptance_tasks` 表示尚未生成终态 outcome 的任务，不单凭这个字段宣称“工程验证已通过、只待人验收”。必须结合当前任务的 RunLedger、原文覆盖、验证证据、未验项及真实决定说明实际进度：仍在执行、验证未通过、存在阻断，或确已交付而待人验收。报告待人验收时给出交付对象与版本及证据；已有同版本有效验收则核对后继续 close，不重复询问。

没有用户答复不构成 `Implemented`，也不自动构成 `Deferred` / `Blocked`。后两种状态必须反映其各自真实事实，不能用于填补缺失的 Acceptance。`after.json` 和 Minimal `task_outcome` 仍是正式终态；暂未产生终态时如实报告，不伪造闭环。

`signals.py` 的 `derivation_audit` 按 C10 §8.2 关系符号分开统计衍生：`affected-by`（本次引入）计入回归链深，`observed-from`（顺带发现）单独计数——前者链长说明修复方式有系统性问题，后者多则相反。`recorded_but_not_created` 列出已记录为衍生目标但项目里尚不存在的任务，那是「发现了却没人接手」的线索。

需要人来审计时启动治理控制台：

```console
python <skill-root>/scripts/console.py start --project-root <project-root>
```

只读本地服务，启动后自动打开浏览器；`status` 查地址、`open` 重新打开、`stop` 停止。它每次请求都重新探查 `.project-governance` 与 `LG_project_docs`（含并非本 skill 产生的资产），提供任务、血缘、未决项、项目文档、生成物与完整性各页。只读视图，按 C10 §8.0 不得作为新追踪事实的唯一来源。

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
