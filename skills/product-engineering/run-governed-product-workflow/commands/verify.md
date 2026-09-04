# verify

用于验证和验收前准备。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

验证必须证明原始结果和约束成立，不只证明命令运行成功。记录：

- 验证对象和版本。
- 方法、输入、预期、实际和结果。
- Evidence 引用。
- 未覆盖范围和残留风险。

## 逐条对照，不抽查

**验收基准是需求原文**：`request_snapshot` 里的用户原话，以及澄清各轮里用户逐条的回答。

不是任务卡、完成判据或验收清单——那些是 Agent 起草的派生物，起草时就可能漏掉原文里的要求。**用派生判据验自己写的实现，查多少遍都不会红**：漏掉的那条既不在判据里，也不在实现里，两边一致，全绿。

执行方式：

1. 从 `request_snapshot` 与澄清记录里把用户的要求**逐条摘出**，编号成清单。一句话含多个要求的要拆开——「阻断并提示 X **或者**提交 Y 让管理员审查」是两条，不是一条。交互、呈现、文案类的要求同样入清单，它们最容易在起草判据时被当成细节丢掉。
2. 清单**必须穷举**，包括看起来早就做过的、看起来是小事的。不得以「这条显然没问题」为由跳过。
3. 每条给出三样：**状态**（已实现 / 未实现 / 部分实现）、**证据**（文件与行号、命令输出、或活体验证结果）、部分实现时**差在哪**。
4. 「未实现」与「部分实现」逐条列出，不得省略、不得合并进结论段落。
5. 只给结论、不给逐条清单的复查，视为未完成。

抽查漏得有系统性：Agent 倾向于复查自己记得的、自己实现过的条目，而漏掉的恰恰是自己起草时就没接住的那些。逐条对照是唯一能把这类漏项翻出来的方式。

需求原文与派生判据不一致时，以原文为准，并按 Amendment 修订派生判据；不得反过来用判据裁剪原文。

完整载体常用命令：

```console
python <skill-root>/scripts/validate_task_package.py <project-root>/.project-governance/tasks/<TaskID> --check-mapping
python <skill-root>/scripts/audit_tailoring_coverage.py
python <skill-root>/scripts/audit_norm_consistency.py --project-root <project-root> --project-id <ProjectID> --task-id <TaskID> --runtime-only
```

`<skill-root>/scripts/audit_norm_retrieval.py --validate-only --runtime-only` 可不传规范开发仓 TaskID。

验收决定、发布批准和风险接受不能由验证脚本代替。
