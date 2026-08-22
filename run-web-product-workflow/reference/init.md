# init

用于首次建立受控任务。先检查仓库、现有 `<project-root>/.project-governance/`、`<project-root>/LG_project_docs/`、未提交变化和用户给出的材料。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

默认完整载体：

```console
python <skill-root>/scripts/init_task.py --project-root <project-root> --project-id <ProjectID> --work-item-id <WorkItemID> --task-id <TaskID> --ordinal <N> --objective <text> --acceptance <criterion> --development-type <DT-01..DT-09> --change-surface <controlled-surface> --delivery-scenario <DS-01..DS-04> --in-scope <scope> --baseline-inheritance Revise --basis <evidence-ref> --authority-reference <authority-ref>
```

进入 S4 前关闭阻断 Unknown，并写入结构化 `authority_assessments`。涉及 Task Profile 变化时使用：

```console
python <skill-root>/scripts/refresh_tailoring_resolution.py <project-root>/.project-governance/tasks/<TaskID>/before.json --stage S4 --applicability-fact <key=Yes|No|Unknown> --reason <reason> --basis <basis>
```

首次采用项目时初始化文档目录：

```console
python <skill-root>/scripts/manage_project_docs.py init --project-root <project-root>
python <skill-root>/scripts/manage_project_docs.py refresh-readme --project-root <project-root>
```

写入 Task Profile 时必须使用受控值；入口口语可以映射，不能原样写入 `defect-fix`、`automation` 等别名。
