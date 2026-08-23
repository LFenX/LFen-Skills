# verify

用于验证和验收前准备。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

验证必须证明原始结果和约束成立，不只证明命令运行成功。记录：

- 验证对象和版本。
- 方法、输入、预期、实际和结果。
- Evidence 引用。
- 未覆盖范围和残留风险。

完整载体常用命令：

```console
python <skill-root>/scripts/validate_task_package.py <project-root>/.project-governance/tasks/<TaskID> --check-mapping
python <skill-root>/scripts/audit_tailoring_coverage.py
python <skill-root>/scripts/audit_norm_consistency.py --project-root <project-root> --project-id <ProjectID> --task-id <TaskID> --runtime-only
```

`<skill-root>/scripts/audit_norm_retrieval.py --validate-only --runtime-only` 可不传规范开发仓 TaskID。

验收决定、发布批准和风险接受不能由验证脚本代替。
