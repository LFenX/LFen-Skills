# close

用于收尾并生成 TaskOutcome。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

先分流：

- 存在 `before.json` 且不存在活动 `task-record.json`：按完整载体收尾。
- 存在合法 `task-record.json` 且 `lifecycle_state` 为 `Ready` 或 `Frozen`：按 Minimal 收尾。
- 两者同时存在：停止；先确认是否已升级，禁止混用载体。
- `task-record.json` 为 `Upgraded`：停止；先用 `init_task.py --upgrade-minimal-reason --upgrade-minimal-basis` 完成完整载体升级。
- `task-record.json` 为 `Completed`：停止；该 Minimal 任务已收尾。

完整载体：

```console
python <skill-root>/scripts/close_task.py <project-root>/.project-governance/tasks/<TaskID> --status <Implemented|Deferred|Cancelled|Blocked|Superseded> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python <skill-root>/scripts/rebuild_project_state.py --project-root <project-root> --project-id <ProjectID>
python <skill-root>/scripts/generate_review_views.py --project-root <project-root> --project-id <ProjectID>
```

TaskOutcome 写明成立事实、实际变化、验证、遗留项、责任人和后续 TaskID。TaskOutcome 建立后修订必须使用：

```console
python <skill-root>/scripts/amend_record.py <project-root>/.project-governance/tasks/<TaskID>/after.json --path <field> --value-json <json> --reason <reason> --basis <basis>
```

旧 V6.2/V6.2.1 已收尾任务只做安全身份兼容读取，不要求当前 manifest 仍发布同一路径。

Minimal 载体：

```console
python <skill-root>/scripts/manage_minimal_task.py close <project-root>/.project-governance/tasks/<TaskID> --status <Implemented|Deferred|Cancelled|Blocked|Superseded> --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
python <skill-root>/scripts/manage_minimal_task.py validate --project-root <project-root> <project-root>/.project-governance/tasks/<TaskID>
python <skill-root>/scripts/rebuild_project_state.py --project-root <project-root> --project-id <ProjectID>
python <skill-root>/scripts/generate_review_views.py --project-root <project-root> --project-id <ProjectID>
```

Minimal 收尾只适用于未升级的合法 `task-record.json`；升级后必须走完整载体收尾。
