# clarify

用于仍有会改变目标、范围、验收、风险或授权的问题时。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

流程：

1. 先查现有材料，再提问。
2. 每轮只问 3-5 个问题，并给推荐默认。
3. 用户回答“全部默认”时采用推荐默认并记录 basis。
4. 没有实质未知时为零轮。
5. High/Critical、不可逆、生产发布、权限扩大、安全/隐私、例外和风险接受必须单独确认。

每轮同步更新第一性原理分析：

- Facts：已证实内容。
- Constraints：项目、权限、规范和环境边界。
- Assumptions：可验证但未证实判断。
- Unknowns：缺失信息、Owner、解除条件和是否阻断。

澄清不是批准。正式 Gate、发布、风险接受和 Authority 仍必须从权威事实源核验。
