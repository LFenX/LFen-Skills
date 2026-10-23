# run

用于执行已冻结计划。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

执行前：

```console
python <skill-root>/scripts/get_context.py --help
python <skill-root>/scripts/get_context.py --task-dir <project-root>/.project-governance/tasks/<TaskID> --action edit_in_scope --query-text <action-summary>
python <skill-root>/scripts/validate_task_package.py <project-root>/.project-governance/tasks/<TaskID> --check-mapping --execution-ready
python <skill-root>/scripts/check_write_guard.py --task-dir <project-root>/.project-governance/tasks/<TaskID> <target-path>
python <skill-root>/scripts/append_run_event.py <project-root>/.project-governance/tasks/<TaskID> --run-id <RunID> --attempt-id <AttemptID> --event-type run_started --summary <summary> --status started
```

上述查询用于 S5 范围内编辑；先核对当前 CLI help、动作契约和 Task 阶段，并完整消费实际返回的上下文。`run_started` 仍是账本事件，不能把它误作 S5 的查询 action；当前动作契约把 `run_started` 查询限定在 S4，把 `edit_in_scope` 限定在 S5。阶段不符时用官方工具对齐，不靠反复调用错误 action 绕过。已经开始的同一 Run 不重复追加 `run_started`。

执行门需要真实 Proceed 决定：保留实际展示、回答原话、决定人、时间和 `evidence_ref`，明确 `outcome=Approved`；仅有 kind、非空文字或过去的拒绝/推迟不能充当批准。决定记录不得伪造，格式检查不证明人已授权。真实 Acceptance 仍在完工交接阶段单独核验，不能沿用 Proceed。

新物质事件要求当前 `proof_contract_version` 和有效 Proceed。旧活动任务缺少版本时，先按 [verify](verify.md) 的正式 Amendment 采用当前契约；补版本不能补授权，也不能把历史终态兼容用于新执行。

同目录存在 `before.json` 时，写守卫使用完整载体的 `allowed_paths`，忽略 stray `task-record.json`。守卫失败只警告放行；明确拒绝时停止该写入。

执行中只记录物质事件：mutation、failure、retry、verification、external-effect、gate、rollback、run_finished。普通读取和搜索不写 RunLedger。

失败后先追加 `failure`，再用新 AttemptID 追加 `retry`。范围、权限、验收或计划变化必须先停止受影响动作，再用 Amendment 修订；禁止静默覆盖。

Amendment 只记录真实字段变更：同值写入返回 `UNCHANGED`，不改文件、修订号或历史；批量操作忽略同值项，真实变更保留原值、新值和依据。`tailoring_resolution` 是派生快照，自动重算不新增 Amendment；阶段刷新使用 `refresh_tailoring_resolution.py`，不得把派生快照作为普通字段修订。

失败次数不证明出现新需求或新授权缺口。先核对原始目标、Scope、验收、Authority、安全边界和持续授权；同范围内的工具参数、编码、依赖、夹具、断言或实现修正，在这些条件未变且没有新阻断未知时，保留原失败和 FER，记录修正与新 Attempt 后继续获批验证，不重复索取相同授权。出现真实新未知、影响扩大、权限变化或未明副作用时仍须停止并澄清；机器明确 Blocked/REFUSED 时按官方路径处理，不伪造回答、删失败或另建载体绕行。

工程验证完成并拟以 `Implemented` 收尾时，先按 [verify](verify.md) 完成真实验收交接。完整载体在记录真实 Acceptance 和 required Gate 后才写成功的 `run_finished`，再按 [close](close.md) 生成 outcome；不得用成功测试或提前封账代替人侧验收。真实失败或阻断仍按实际结果记录并收尾，不假装已验收，也不为记录失败索要肯定验收。

本地 norm index 只保留当前活动 digest。旧缓存不是审计档案。
