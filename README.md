<p align="center">
  <img src="assets/logo.svg" alt="LFen Skills" width="460">
</p>

<p align="center">
  我自己工作学习中沉淀的 Agent Skills，对你有用欢迎自取。<br>
  每个 skill 自包含，一条命令安装到 7 个平台。
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg?style=flat-square" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/github/license/LFenX/LFen-Skills?style=flat-square" alt="license">
</p>

<p align="center">
  <b>中文</b> &nbsp;|&nbsp; <a href="README.en.md">English</a>
</p>

## Skills 一览

### 📊 数据处理

> 结构化数据的匹配、清洗、转换与质量核验

- **[`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md)** — 两张 CSV/XLSX 表按键对账：支持单字段或多字段组合键，文本、编号、数字、日期各自归一化；产出匹配合集、双向未匹配明细、重复与非法键审计，最终输出校验过的格式化 Excel 工作簿。适合跨文件核对、名单比对、覆盖率分析。

### 📐 产品研发

> 产品定义、研发执行、质量控制与交付流程

- **[`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md)** — 从一份基础产品说明出发，走完需求追溯、PRD、产品包、前后端联调到验收返修的全流程，帮 Coding Agent 从 0 到 1 交付复杂 Web 生产后台；过程在飞书云文档 / 多维表格留痕。
- **[`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md)** — 推进任何改变产品行为的开发任务：新功能、改需求、修 bug、重构、迁移、发布、复查验收。按团队 V6.3 规范维护需求、计划、执行、验证、验收的证据链——小任务只留一个文件，但不跳过澄清和验收。
- **[`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md)** — 从 KOC 反馈多维表格筛选、认领、推进开发登记项，澄清、规划、执行、复核、返修、完成状态全程同步回表，驱动 KOC 管理平台的缺陷修复与功能迭代。

### 🔧 开发工具

> 开发环境与 AI 编码助手的配置、接入与排障

- **[`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md)** — 给 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）：provider 配置结构、模型注册、网关验证、常见错误排查。

<details>
<summary>📑 索引表（脚本自动生成，勿直接编辑）</summary>

<!-- catalog-summary:start -->
| 分类 | 定义 | Skills |
| --- | --- | --- |
| [数据处理](CATALOG.md#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) |
| [产品研发](CATALOG.md#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md), [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md), [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) |
| [开发工具](CATALOG.md#dev-tools) | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) |
<!-- catalog-summary:end -->

完整清单见 [`CATALOG.md`](CATALOG.md)；机器可读索引见 [`catalog/index.json`](catalog/index.json)。

</details>

## 安装

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

运行后按提示选平台、选 skill 即可。skill 以 junction（Windows）/ symlink 链接到本地 `~/.lfenskills` 克隆，之后 `git pull` 原地更新。

```powershell
.\install.ps1 -Status                    # 查看各平台安装状态
.\install.ps1 -Update                    # 选择性刷新 skill
.\install.ps1 -All -AllSkills -Force     # 静默全量安装
```

## 支持平台

| 平台 | Skill 目录 | 备注 |
| --- | --- | --- |
| OpenCode | `~/.agents/skills/` | 同时覆盖 Cline、Warp、Zed、Kilo、Kimi、Droid、Firebender 等 20+ 工具 |
| Claude Code | `~/.claude/skills/` | |
| Codex | `~/.codex/skills/` | |
| Cursor | `~/.cursor/skills/` | |
| Gemini CLI | `~/.gemini/skills/` | |
| GitHub Copilot | `~/.copilot/skills/` | |
| Windsurf | `~/.codeium/windsurf/skills/` | |

## 新增 Skill

1. 在 `skills/<主分类>/` 下新增 `<skill-name>/SKILL.md`，目录名必须与 frontmatter 的 `name` 一致。
2. 将 skill 名称加入 `catalog/taxonomy.json` 的同名叶子分类，并在 `skill_metadata` 中填写 `scope` 与排序后的 `tags`。
3. 运行 `python scripts/update_catalog.py` 重新生成 README 摘要、`CATALOG.md` 和 `catalog/index.json`。
4. 运行 `python scripts/update_catalog.py --check` 检查遗漏、重复归类、非法元数据和生成物漂移，然后提交推送。

## 许可证

[MIT](LICENSE)
