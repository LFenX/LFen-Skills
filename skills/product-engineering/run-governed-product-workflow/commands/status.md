# status

无参数或只问“现在状态”时先跑：

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

```console
python <skill-root>/scripts/signals.py --project-root <project-root>
```

输出 JSON 包含：

- blocking_unknowns：仍阻断的 Unknown。
- pending_acceptance_tasks：活动任务及已有工程结果但待用户决定的任务。
- task_progress：每项任务的工程结果是否已保存、独立用户决定、待验收标志和 `adversarial_review` 的状态、轮数、连续无问题轮数与未解决问题。
- snapshot_stale：TaskContract Source Snapshot 与当前仓库差异。
- minimal_eligibility_facts：已有 Minimal 资格事实。
- update_available：本地索引与当前 skill 运行快照不一致时提示。
- recommended_commands：当前需要的建议命令和理由。

`signals.py` 只报告，不自动执行推荐命令。

历史终态缺少新增证明时按兼容规则读取，保留原状态；项目状态、审阅视图与控制台展示 `proof_validation`，其中 `HistoricalNotRevalidated` 表示未追溯补验当前证明，不能表述为当前门禁已通过。活动任务的证明状态表示待终态核验。原始结构或血缘损坏仍须报告，不能用历史兼容掩盖。规则见 [verify](verify.md)。

`pending_acceptance_tasks` 包括尚未保存工程结果的活动任务，以及结果已保存但 `user_decision` 为 `Pending` / `Deferred` 的任务。结合 `engineering_recorded`、RunLedger、原文覆盖、验证证据和未完成项说明进度；不能仅凭一个 pending 标志宣称工程验证通过。工程结果已保存时展示版本及用户决定，不建议重新执行，也不要求用户回到原对话重复验收。

`Implemented` 表示工程实现和必要验证完成，用户未答时仍须保存 `after.json` / `task_outcome` 并将 `user_decision` 记为 `Pending`。人的拒绝或推迟独立于工程状态；不伪造批准，不用 `Deferred` / `Blocked` 填补缺少验收答复。旧文件未单列用户决定时明确显示历史未单列，不推定通过。

对抗性审查 `NotOffered` 时先主动询问；`AwaitingUser`、`Declined`、`Deferred` 不得启动或自动催问；`InProgress`、`Blocked` 只针对已经明确同意的审查，按 [verify](verify.md#完工后可选对抗性审查) 处理。`Passed` 仅由同版连续两轮完整无问题计算得出，不代表人的验收。`LegacyUntracked` 表示旧结果未记录该协议，不批量补造询问和轮次。同一已授权审查的返修从原审查任务继续，不递归询问。

`Stale` 表示当前交付、原文或报告已与轮次证明不符，连续计数为 0；保留原件，解除问题后在已有授权内重新完整审查。`ManagedByParent` 点名返修所属的原审查，不能单独启动；`LegacyNotRevalidated` 表示旧轮次缺少新版报告绑定，不自动重启，也不称为新版两轮通过。状态中的 `reviewed_delivery` 明确本次审查覆盖哪个实际交付版本。

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
