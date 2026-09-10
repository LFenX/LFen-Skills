<p align="center">
  <img src="assets/logo.svg" alt="LFen Skills" width="160">
</p>

<h1 align="center">LFen Skills</h1>

<p align="center">
  <b>给 AI 编码助手装技能，一条命令装进 7 个平台。</b><br>
  自包含的 Agent Skills 集合，junction 链接、`git pull` 原地更新、单一配置源自动生成分类目录
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg?style=flat-square" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/badge/skills-5-8B5CF6?style=flat-square" alt="skills">
  <img src="https://img.shields.io/badge/platforms-7-0EA5E9?style=flat-square" alt="platforms">
  <img src="https://img.shields.io/github/license/LFenX/LFen-Skills?style=flat-square" alt="license">
</p>

```text
  ██╗     ███████╗███████╗███╗   ██╗
  ██║     ██╔════╝██╔════╝████╗  ██║
  ██║     █████╗  █████╗  ██╔██╗ ██║
  ██║     ██╔══╝  ██╔══╝  ██║╚██╗██║
  ███████╗██║     ███████╗██║ ╚████║
  ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝
  Skills install

  Select target platforms:

   › [x] OpenCode       (also covers Cline/Warp/Zed/Kilo +17 more)
     [x] Claude Code
     [ ] Codex
     [ ] Cursor
     [ ] Gemini CLI
     [ ] GitHub Copilot
     [ ] Windsurf

  [↑↓] Navigate  [Space] Toggle  [a] Select All  [Enter] Confirm  [q] Quit
```

<p align="center">🌐 语言 / Language</p>

<details open>
<summary>&nbsp;🇨🇳&nbsp; 中文</summary>

## 为什么不是复制粘贴？

| | 手动复制 skill 文件夹 | 用安装脚本 |
| --- | --- | --- |
| 装到多个平台 | 每个平台复制一遍 | 菜单里一次勾选 7 个 |
| 更新 | 逐个重新复制，容易漏 | 克隆目录 `git pull`，所有 junction 原地生效 |
| 装没装、装在哪 | 自己翻目录 | `-Status` 一条命令列出 |

## 一条命令装好

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

装完重启 AI 工具即可。常用命令：

```powershell
.\install.ps1 -Status                    # 查看各平台安装状态
.\install.ps1 -Update                    # 选择性刷新 skill
.\install.ps1 -All -AllSkills -Force     # 静默全量安装
```

## 看一眼就能用

- skill 都在 `skills/<分类>/<名称>/`，每个自包含，单独拷走也能用
- 更新已装 skill：进 `~/.lfenskills` 执行 `git pull`，无需重装
- 完整清单看 [`CATALOG.md`](CATALOG.md)，工具读 [`catalog/index.json`](catalog/index.json)
- 加新 skill：写 `SKILL.md` → 登记 `catalog/taxonomy.json` → `python scripts/update_catalog.py --check`

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

## Skill 分类一览

<!-- catalog-summary:start -->
| 分类 | 定义 | Skills |
| --- | --- | --- |
| [数据处理](CATALOG.md#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) |
| [产品研发](CATALOG.md#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md), [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md), [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) |
| [开发工具](CATALOG.md#dev-tools) | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) |
<!-- catalog-summary:end -->

## 分类模型

每个 skill 只归入一个最具体的叶子分类；`scope` 区分通用 / 团队 / 项目级复用边界，不表示质量；跨领域检索走标签，不重复归类。分类的唯一配置源是 `catalog/taxonomy.json`，README 摘要、`CATALOG.md`、`catalog/index.json` 全部由脚本生成、CI 校验，请勿直接编辑。

## 新增 Skill

1. 在 `skills/<主分类>/` 下新增 `<skill-name>/SKILL.md`，目录名必须与 frontmatter 的 `name` 一致。
2. 将 skill 名称加入 `catalog/taxonomy.json` 的同名叶子分类，并在 `skill_metadata` 中填写 `scope` 与排序后的 `tags`。
3. 运行 `python scripts/update_catalog.py` 重新生成 README 摘要、`CATALOG.md` 和 `catalog/index.json`。
4. 运行 `python scripts/update_catalog.py --check` 检查遗漏、重复归类、非法元数据和生成物漂移，然后提交推送——CI 会自动校验。

## 参考仓库

- [Anthropic Skills](https://github.com/anthropics/skills)：自包含 skill，按用户任务与能力用途分类。
- [Microsoft Skills](https://github.com/microsoft/skills)：稳定主分类目录，按语言和领域分层导航。
- [NVIDIA Skills](https://github.com/NVIDIA/skills)：注册元数据 + 自动校验，支撑规模化发现与维护。

</details>

<details>
<summary>&nbsp;🇬🇧&nbsp; English</summary>

## Why not copy-paste?

| | Copying skill folders by hand | Using the install script |
| --- | --- | --- |
| Install to multiple platforms | Copy once per platform | Tick 7 platforms in one menu |
| Updates | Re-copy each skill, easy to miss | `git pull` in the clone, every junction updates in place |
| What's installed where | Hunt through directories | One `-Status` command lists it all |

## One Command to Install

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

Restart your AI tool and you're done. Other commands:

```powershell
.\install.ps1 -Status                    # Show what's installed where
.\install.ps1 -Update                    # Selectively refresh skills
.\install.ps1 -All -AllSkills -Force     # Silent full install
```

## Look Once and Use

- Skills live in `skills/<category>/<name>/` — each is self-contained, so you can copy a single one too
- Update installed skills: run `git pull` in `~/.lfenskills` — no reinstall needed
- Full catalog in [`CATALOG.md`](CATALOG.md); tools can read [`catalog/index.json`](catalog/index.json)
- Add a skill: write `SKILL.md` → register in `catalog/taxonomy.json` → `python scripts/update_catalog.py --check`

## Platform Support

| Platform | Skill Directory | Notes |
| --- | --- | --- |
| OpenCode | `~/.agents/skills/` | Also covers Cline, Warp, Zed, Kilo, Kimi, Droid, Firebender, and 20+ more |
| Claude Code | `~/.claude/skills/` | |
| Codex | `~/.codex/skills/` | |
| Cursor | `~/.cursor/skills/` | |
| Gemini CLI | `~/.gemini/skills/` | |
| GitHub Copilot | `~/.copilot/skills/` | |
| Windsurf | `~/.codeium/windsurf/skills/` | |

## Skill Catalog

<!-- catalog-summary:start -->
| Category | Description | Skills |
| --- | --- | --- |
| [Data Processing](CATALOG.md#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) |
| [Product Engineering](CATALOG.md#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md), [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md), [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) |
| [Dev Tools](CATALOG.md#dev-tools) | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) |
<!-- catalog-summary:end -->

## Taxonomy Model

Each skill belongs to exactly one most-specific leaf category. `scope` marks reuse boundaries (general / team / project), not quality. Cross-domain discovery goes through tags, never duplicate categorization. The single source of truth is `catalog/taxonomy.json`; the README summary, `CATALOG.md`, and `catalog/index.json` are all generated and CI-validated — do not edit them directly.

## Adding a New Skill

1. Create `skills/<category>/<skill-name>/SKILL.md` — the directory name must match the frontmatter `name`.
2. Add the skill to the matching leaf category in `catalog/taxonomy.json`, with `scope` and sorted `tags` under `skill_metadata`.
3. Run `python scripts/update_catalog.py` to regenerate the README summary, `CATALOG.md`, and `catalog/index.json`.
4. Run `python scripts/update_catalog.py --check` to verify everything, then commit and push — CI validates automatically.

## References

- [Anthropic Skills](https://github.com/anthropics/skills): self-contained skills categorized by user task.
- [Microsoft Skills](https://github.com/microsoft/skills): stable category directories with layered navigation.
- [NVIDIA Skills](https://github.com/NVIDIA/skills): registered metadata plus automated validation at scale.

</details>

<br>

<p align="center">
  <a href="CATALOG.md">CATALOG.md</a> ·
  <a href="catalog/index.json">catalog/index.json</a> ·
  <a href="install.ps1">install.ps1</a> ·
  <a href="install.sh">install.sh</a> ·
  <a href="LICENSE">License</a>
</p>

<p align="center">
  <sub>MIT License · LFen Skills</sub>
</p>
