# 项目文档目录与迁移规范

这些路径均相对于 `<project-root>`，不是 skill 根。

## 1. 唯一默认位置

`.project-governance/` 只保存机器治理记录、权威资产登记和派生视图。其他产品原生文档统一保存到 `LG_project_docs/`：

```text
LG_project_docs/
├── README.md
├── requirements/
│   └── <RequirementID>/
│       ├── README.md
│       ├── discovery/
│       ├── prd/
│       ├── requirements/
│       ├── design/
│       ├── ui-previews/
│       ├── decisions/
│       ├── verification/
│       ├── release/
│       └── references/
├── _intake/
│   └── unclassified/<DocumentType>/
└── _archive/
    └── legacy-migrations/<MigrationID>/
        ├── original/
        ├── migration-plan.json
        ├── manifest.json
        └── migration-report.md
```

先按需求身份分类，再按文档类型分类。优先使用已有 RequirementID；没有 RequirementID 时使用 TaskID；两者都无法可靠确定时进入 `_intake/unclassified/<DocumentType>/`，禁止猜测身份。

## 2. 文档类型

| 目录 | 内容 |
|---|---|
| `discovery` | 用户研究、问题证据、机会与意图 |
| `prd` | PRD、Feature 定义 |
| `requirements` | 原子需求、需求澄清、演进说明 |
| `design` | UX、技术设计、架构说明 |
| `ui-previews` | 用于评审的 HTML、PNG、JPG、WebP、SVG |
| `decisions` | ADR、设计或产品决定原生内容 |
| `verification` | 测试说明、验收证据、验证报告 |
| `release` | 发布说明、迁移手册、回滚说明 |
| `references` | 外部资料、本地兼容输入和无法归入前述类型的参考文档 |

用户要求新的文档类型时，可以在具体 Requirement 目录下新增类型目录，但必须先更新该 Requirement 的 `README.md` 和项目级 `LG_project_docs/README.md` 的受管清单。

## 3. 明确例外

以下文件不迁入 `LG_project_docs/`：

- 仓库根目录的 `README*`、`LICENSE*`、`CONTRIBUTING*`、`CHANGELOG*`、`SECURITY*`、`CODE_OF_CONDUCT*`。
- 与代码组件同目录、直接说明该组件构建或 API 的 `README.md`。
- 应用运行所需的 HTML、图片、图标、静态资源和测试 Fixture；只有被 TaskContract/AuthorityAsset 声明为产品文档时才受本文档目录约束。
- 第三方依赖、构建输出、缓存和 VCS 内部文件。

例外不能用于规避产品文档登记。无法确认是运行资产还是文档时进入 `_intake`，由人确认。

## 4. README 契约

- `.project-governance/README.md` 解释六类治理载体和实际目录清单。
- `LG_project_docs/README.md` 解释分类规则、需求目录和自定义文档类型。
- 每个 `requirements/<RequirementID>/README.md` 解释该需求下每个文件和目录的作用。
- `<!-- LG-MANAGED:START -->` 与 `<!-- LG-MANAGED:END -->` 之间由工具刷新；标记外内容属于用户，不得覆盖。

## 5. 旧文档迁移

采用 Skill 时先运行 `plan-migration`，生成源路径、SHA-256、分类依据、备份路径和目标路径。向用户展示计划及其文件 SHA-256；只有用户明确确认同一摘要后才运行 `apply-migration`。

应用顺序固定为：

1. 校验所有源文件仍与计划哈希一致，且目标无冲突。
2. 按原相对路径复制到 `_archive/.../original/` 并复验哈希。
3. 复制到分类后的活动目录并复验哈希。
4. 所有副本验证通过后删除旧位置的原文件；不递归删除旧目录。
5. 写入 `manifest.json` 和 `migration-report.md`，刷新 README，并明确告知用户移动、未分类、冲突和遗留项。

任何源漂移、目标冲突、越界或哈希失败都必须在删除旧文件前停止。

旧 `*_需求澄清备案*.md` 与 `*_执行计划.md` 迁移后仍只作兼容参考；新任务的对应职能分别由 TaskContract 的目标/范围/验收/Authority 和 `plan` 字段承担。
