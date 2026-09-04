# Project Governance

本目录由 `run-web-product-workflow` 管理，保存机器可验证的任务契约、运行事件、任务结果、项目状态、权威资产登记和派生视图。产品原生文档保存在 `LG_project_docs/`，不得混放。

## 固定结构

- `tasks/<TaskID>/before.json`：执行前 TaskContract。
- `tasks/<TaskID>/run.jsonl`：只追加 RunLedger。
- `tasks/<TaskID>/after.json`：终态 TaskOutcome。
- `authority/`：按触发登记的 AuthorityAsset。
- `generated/`：可重建的 DerivedView、上下文、审计和迁移视图。
- `runtime-cache/`：可重建的本地运行缓存。
- `project-state.json`：跨任务生成的 ProjectState，禁止手工编辑。

## 实际内容

<!-- LG-MANAGED:START -->
- `authority/`：目录
- `console/`：目录
- `generated/`：目录
- `project-state.json`：文件
- `runtime-cache/`：目录
- `tasks/`：目录
<!-- LG-MANAGED:END -->

标记区由工具更新；标记外内容可由项目维护者补充。
