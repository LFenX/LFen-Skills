# migrate

用于首次采用本 skill 时整理旧产品文档。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

计划：

```console
python <skill-root>/scripts/manage_project_docs.py plan-migration --project-root <project-root> --migration-id <MigrationID>
```

先向用户展示计划路径、文件数、未分类项和计划 SHA-256。用户明确确认同一摘要后才应用：

```console
python <skill-root>/scripts/manage_project_docs.py apply-migration --plan <project-root>/LG_project_docs/_archive/legacy-migrations/<MigrationID>/migration-plan.json --confirm-plan-sha256 <sha256> --authorized-by <evidence-ref>
```

规则：

- 先按原路径建立逐文件哈希备份。
- 再复制到 `<project-root>/LG_project_docs/requirements/<RequirementID>/<DocumentType>/` 或 `<project-root>/LG_project_docs/_intake/unclassified/<DocumentType>/`。
- 全部验证通过后移除旧位置文件。
- 不递归删除旧目录。
- 完成后报告备份位置、移动结果、未分类和冲突。
