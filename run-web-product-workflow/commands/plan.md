# plan

用于制定或修订执行计划。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

必须从第一性原理推导：

1. 结果：可观察目标状态。
2. 事实：已有证据。
3. 约束：权限、范围、规范、兼容和不可逆边界。
4. 假设与未知：标明验证方式和阻断性。
5. 基础要素与因果链。
6. 至少比较选定方案与保持现状；Medium 及以上再给一个真实替代方案。
7. 每个计划步骤引用决策标准和验收。

完整载体物质动作前运行一次：

```console
python <skill-root>/scripts/get_context.py --task-dir <project-root>/.project-governance/tasks/<TaskID> --action plan_execution --query-text <current-action-summary>
```

返回 `Blocked` 时停止受影响动作；返回 Clause Context 时按引用执行，不用手动四步查询。
