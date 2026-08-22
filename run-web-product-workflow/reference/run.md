# run

用于执行已冻结计划。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

执行前：

```console
python <skill-root>/scripts/validate_task_package.py <project-root>/.project-governance/tasks/<TaskID> --check-mapping --execution-ready
python <skill-root>/scripts/get_context.py --task-dir <project-root>/.project-governance/tasks/<TaskID> --action run_started --query-text <action-summary>
python <skill-root>/scripts/check_write_guard.py --task-dir <project-root>/.project-governance/tasks/<TaskID> <target-path>
python <skill-root>/scripts/append_run_event.py <project-root>/.project-governance/tasks/<TaskID> --run-id <RunID> --attempt-id <AttemptID> --event-type run_started --summary <summary> --status started
```

同目录存在 `before.json` 时，写守卫使用完整载体的 `allowed_paths`，忽略 stray `task-record.json`。守卫失败只警告放行；明确拒绝时停止该写入。

执行中只记录物质事件：mutation、failure、retry、verification、external-effect、gate、rollback、run_finished。普通读取和搜索不写 RunLedger。

失败后先追加 `failure`，再用新 AttemptID 追加 `retry`。范围、权限、验收或计划变化必须先停止受影响动作，再用 Amendment 修订；禁止静默覆盖。

本地 norm index 只保留当前活动 digest。旧缓存不是审计档案。
