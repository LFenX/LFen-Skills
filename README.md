<p align="center">
  <img src="assets/logo.svg" alt="LFen Skills" width="160">
</p>

<h1 align="center">LFen Skills</h1>

<p align="center">
  可复用的 Agent Skills 集合<br>
  每个 skill 自包含，目录与索引由单一配置源自动生成并持续校验
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/badge/Skills-5-8B5CF6" alt="Skills">
  <img src="https://img.shields.io/badge/Categories-3-0EA5E9" alt="Categories">
  <img src="https://img.shields.io/badge/PRs-welcome-F59E0B" alt="PRs Welcome">
</p>

---

## ✨ 亮点

- **自包含**：每个 skill 独立成目录，附带自己的说明、脚本与资源，可单独安装与复用
- **单一配置源**：分类只维护在 `catalog/taxonomy.json`，README 摘要、`CATALOG.md`、`catalog/index.json` 全部由脚本生成
- **CI 防漂移**：自动校验遗漏、重复归类、物理路径、非法元数据与生成物漂移
- **三维分类**：主分类定位能力域，适用范围界定复用边界，标签支持跨领域检索

## 🗂 仓库结构

```text
LFen-skills/
├── skills/                    # 自包含 skill，按主分类组织
│   ├── data-processing/       # 数据处理
│   ├── product-engineering/   # 产品研发
│   └── dev-tools/             # 开发工具
├── catalog/                   # 分类源（taxonomy.json）与机器可读索引（index.json）
├── scripts/
│   └── update_catalog.py      # 目录生成与校验脚本
├── CATALOG.md                 # 生成的分类目录（勿直接编辑）
└── assets/                    # Logo 等静态资源
```

## 📦 Skill 分类一览

<!-- catalog-summary:start -->
| 分类 | 定义 | Skills |
| --- | --- | --- |
| [数据处理](CATALOG.md#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) |
| [产品研发](CATALOG.md#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md), [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md), [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) |
| [开发工具](CATALOG.md#dev-tools) | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) |
<!-- catalog-summary:end -->

完整清单、适用范围、标签与参考来源见 [`CATALOG.md`](CATALOG.md)；工具可读取 [`catalog/index.json`](catalog/index.json)。

## 🧭 分类模型

分类采用三个互补维度：

1. **主分类**：按用户任务与能力域组织，每个 skill 只能归入一个最具体的叶子分类。
2. **适用范围**：区分通用、团队和项目级能力，不表示质量等级。
3. **标签**：表达跨领域主题和检索关键词，不通过重复归类实现多维导航。

分类树最多两层。只有同一领域形成多个稳定主题后才增加子分类；物理目录与分类源一一对应，避免“文档分类”和“文件位置”分离。

## 🚀 新增 Skill

1. 在 `skills/<主分类>/` 下新增 `<skill-name>/SKILL.md`，目录名必须与 frontmatter 的 `name` 一致。
2. 将 skill 名称加入 `catalog/taxonomy.json` 的同名叶子分类，并在 `skill_metadata` 中填写 `scope` 与排序后的 `tags`。
3. 运行 `python scripts/update_catalog.py` 更新 README 摘要、`CATALOG.md` 和 `catalog/index.json`。
4. 运行 `python scripts/update_catalog.py --check` 检查遗漏、重复归类、物理路径、非法元数据和生成物漂移。

## 🔧 常用命令

```bash
# 重新生成 README 摘要、CATALOG.md 与 catalog/index.json
python scripts/update_catalog.py

# 校验配置、物理目录与全部生成物是否一致（CI 同款检查）
python scripts/update_catalog.py --check
```

`catalog/taxonomy.json` 是人工维护的唯一分类源；各 `SKILL.md` 的 `name` 与 `description` 是能力元数据源。README 摘要、`CATALOG.md` 和 `catalog/index.json` 都是可重建生成物，请勿直接编辑。移动目录时，必须同步所有外部 junction 目标。

## 📚 参考仓库

- [Anthropic Skills](https://github.com/anthropics/skills)：每个 skill 保持自包含，并按用户任务与能力用途提供概念分类。
- [Microsoft Skills](https://github.com/microsoft/skills)：保持 skill 自包含，并在目录页按语言和领域主题分层展示、强调按需选择。
- [NVIDIA Skills](https://github.com/NVIDIA/skills)：使用产品域、注册元数据和自动校验支持规模化发现与维护。
