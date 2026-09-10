<p align="center">
  <img src="assets/banner.svg" alt="LFen Skills" width="100%">
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Manrope&size=22&pause=1200&color=8B5CF6&center=true&vCenter=true&width=700&lines=%E6%88%91%E8%87%AA%E5%B7%B1%E5%B7%A5%E4%BD%9C%E5%AD%A6%E4%B9%A0%E4%B8%AD%E6%B2%89%E6%B7%80%E7%9A%84+Agent+Skills;%E5%AF%B9%E4%BD%A0%E6%9C%89%E7%94%A8+%C2%B7+%E6%AC%A2%E8%BF%8E%E8%87%AA%E5%8F%96;%E4%B8%80%E6%9D%A1%E5%91%BD%E4%BB%A4%E5%AE%89%E8%A3%85%E5%88%B0+7+%E4%B8%AA%E5%B9%B3%E5%8F%B0" alt="我自己工作学习中沉淀的 Agent Skills">
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/LFenX/LFen-Skills/catalog.yml?branch=main&style=flat&label=catalog&labelColor=1E1B4B" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/badge/skills-5-8B5CF6?style=flat&labelColor=1E1B4B" alt="skills">
  <img src="https://img.shields.io/badge/platforms-7-0EA5E9?style=flat&labelColor=1E1B4B" alt="platforms">
  <img src="https://img.shields.io/badge/license-MIT-475569?style=flat&labelColor=1E1B4B" alt="license">
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/%E2%97%8F_README-8B5CF6?style=flat" alt="README"></a>
  <a href="SKILLS.md"><img src="https://img.shields.io/badge/Skills_%E4%B8%80%E8%A7%88-64748B?style=flat" alt="Skills 一览"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/English-64748B?style=flat" alt="English"></a>
</p>

## 安装

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

<details open>
<summary><b>Windows（PowerShell）</b></summary>

<p align="center">
  <img src="assets/install-demo-windows.gif" alt="Windows 安装演示" width="100%">
</p>

</details>

<details>
<summary><b>macOS / Linux（bash）</b></summary>

<p align="center">
  <img src="assets/install-demo-macos.gif" alt="macOS 安装演示" width="100%">
</p>

</details>

运行后按提示选平台、选 skill 即可。skill 以 junction（Windows）/ symlink 链接到本地 `~/.lfenskills` 克隆，之后 `git pull` 原地更新。

```powershell
.\install.ps1 -Status                    # 查看各平台安装状态
.\install.ps1 -Update                    # 选择性刷新 skill
.\install.ps1 -All -AllSkills -Force     # 静默全量安装
```

## Skills

各 skill 的详细介绍见 **[Skills 一览](SKILLS.md)**。

<details>
<summary>📑 索引表（脚本自动生成，勿直接编辑）</summary>

<!-- catalog-summary:start -->
| 分类 | Skill | 能力说明 |
| --- | --- | --- |
| [**数据处理**](CATALOG.md#data-processing) |  | 结构化数据的匹配、清洗、转换、分析与质量核验。 |
|  | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) | 按单个字段或有序多字段组合键对账两张 CSV/XLSX 表，支持精确、文本、编号、数字、日期、日期时间等可配置归一化。 |
| [**产品研发**](CATALOG.md#product-engineering) |  | 产品定义、研发执行、质量控制、交付与运营流程。 |
|  | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md) | 从基础产品说明到前后端联调和验收，使用需求追溯、PRD、产品包、飞书云文档/多维表格留痕、模板或指定 UI、控件绑定与返修闭环，协助 Coding Agent 从 0 到 1 构建复杂大型 Web 生产后台。 |
|  | [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md) | 用于推进具体开发任务：新功能、改需求、修 bug、重构、迁移退役、发布上线、复查验收；前端、后端、脚本、配置、文档同等适用。 |
|  | [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) | 从 KOC 后台反馈 Base 筛选、列举、认领并推进开发登记项，在用户授权后同步澄清、规划、执行、复核、返修和完成状态。 |
| [**开发工具**](CATALOG.md#dev-tools) |  | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 |
|  | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) | 为 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）。 |
<!-- catalog-summary:end -->

完整清单见 [`CATALOG.md`](CATALOG.md)；机器可读索引见 [`catalog/index.json`](catalog/index.json)。

</details>

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

1. 在 `skills/<主分类>/` 下新增 `<skill-name>/SKILL.md`，目录名必须与 frontmatter 的 `name` 一致，frontmatter 必须包含 `name`、`description`（中文）和 `description_en`（英文）。
2. 将 skill 名称加入 `catalog/taxonomy.json` 的同名叶子分类，并在 `skill_metadata` 中填写 `scope` 与排序后的 `tags`。
3. 运行 `python scripts/update_catalog.py` 重新生成 README 摘要、`CATALOG.md` 和 `catalog/index.json`。
4. 运行 `python scripts/update_catalog.py --check` 检查遗漏、重复归类、非法元数据和生成物漂移，然后提交推送。

## 许可证

[MIT](LICENSE)

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,50:22D3EE,100:F59E0B&height=100&section=footer" width="100%" alt="">
</p>
