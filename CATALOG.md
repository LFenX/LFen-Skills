# LFen Skills 分类目录

> 此文件由 `python scripts/update_catalog.py` 根据 `catalog/taxonomy.json` 和各 `SKILL.md` 生成，请勿直接编辑。

## 分类总览

| 一级分类 | 定义 | Skill 数量 |
| --- | --- | ---: |
| [数据处理](#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | 1 |
| [产品研发](#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | 3 |
| [开发工具](#dev-tools) | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 | 1 |

共收录 **5** 个 skill。机器可读目录见 [`catalog/index.json`](catalog/index.json)。

## 适用范围

| 范围 | 定义 | Skill 数量 |
| --- | --- | ---: |
| 通用 | 不依赖 LFen 团队或单一项目上下文，可跨项目复用。 | 3 |
| 团队 | 依赖 LFen 团队规范、流程或共享约定。 | 1 |
| 项目 | 面向一个明确项目、系统或业务工作流。 | 1 |

## 分类明细

<a id="data-processing"></a>
## 数据处理

结构化数据的匹配、清洗、转换、分析与质量核验。

| Skill | 适用范围 | 标签 | 能力说明 |
| --- | --- | --- | --- |
| [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) | 通用 | `data-matching`, `data-quality`, `excel` | Reconcile two CSV/XLSX tables by one field or an ordered composite of multiple fields, with configurable exact, text, identifier, number, date, or datetime normalization. Produce an inner join, two directional unmatched-detail sheets, optional secondary-key matching, duplicate and invalid-key audits, subset statistics, and a validated formatted Excel workbook. Use for cross-file matching, inclusion checks, list reconciliation, data coverage analysis, or record comparison by IDs, names, titles, authors, dates, account fields, order numbers, or any user-specified key columns. |

<a id="product-engineering"></a>
## 产品研发

产品定义、研发执行、质量控制、交付与运营流程。

| Skill | 适用范围 | 标签 | 能力说明 |
| --- | --- | --- | --- |
| [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md) | 通用 | `agentic-development`, `frontend-backend`, `product-specification`, `sop`, `web-admin` | 从基础产品说明到前后端联调和验收，使用需求追溯、PRD、产品包、飞书云文档/多维表格留痕、模板或指定 UI、控件绑定与返修闭环，协助 Coding Agent 从 0 到 1 构建复杂大型 Web 生产后台。适用于新项目交付；不用于仅治理审计、单点 bug、纯后端库修改或已交付产品复查。 |
| [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md) | 团队 | `product-delivery`, `product-governance`, `verification` | 用于推进具体开发任务：新功能、改需求、修 bug、重构、迁移退役、发布上线、复查验收；前端、后端、脚本、配置、文档同等适用。按团队 V6.3 规范维护可核对的需求、计划、执行、验证、验收和证据，用同一六元模型在 Minimal 与完整载体之间裁剪——小任务只写一个文件，但不因为任务小就跳过澄清和验收。凡是会改变产品行为、外部可见接口、文档布局或发布结果的改动都适用。也用于对已交付内容的复查——“review 一遍 / 再查一遍 / 是否闭环 / 有没有遗漏 / 需求是否都实现了 / 验收”，此类请求走 verify，按总原则 10 逐条对照需求原文，不抽查。用户提到 Grill Me、Task Profile、Artifact Manifest、VC-PPG、C01-C12、E01-E05 或“最轻框架”时同样适用。不用于纯只读问答，以及不改变任何行为的一次性 git 命令。 |
| [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) | 项目 | `feedback-management`, `feishu-base`, `koc` | 从 KOC 后台反馈 Base 筛选、列举、认领并推进开发登记项，在用户授权后同步澄清、规划、执行、复核、返修和完成状态。用于以飞书多维表格登记项驱动 funplus-UA-KOC-Management-Platform 的缺陷修复、体验优化或新功能；不得处理“唤起开发者”仅为 LFen 的记录。 |

<a id="dev-tools"></a>
## 开发工具

开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。

| Skill | 适用范围 | 标签 | 能力说明 |
| --- | --- | --- | --- |
| [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) | 通用 | `model-provider`, `openai-compatible`, `opencode`, `tool-configuration` | 为 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）。覆盖 provider 配置结构、模型注册、网关验证、常见错误排查。当用户要添加新的模型供应商、配置 opencode.json 的 provider 段、或模型配置后不生效时使用。 |

## 分类演进规则

1. 主分类按用户任务与能力域划分；每个 skill 只归入一个最具体的叶子分类。
2. 横向检索使用 `tags`，不得通过重复归类表达跨领域能力。
3. `scope` 只描述复用边界：通用、团队或项目，不表示质量等级。
4. 分类树最多 2 层；只有同一领域形成多个稳定主题后才增加子分类。
5. 物理目录统一为 `skills/<category-path>/<skill-name>/`；skill 名称不变，外部安装入口通过 junction 指向该物理路径。
6. Markdown 与 JSON 目录均由生成器重建；遗漏、重复、路径不一致、非法元数据或生成物漂移会使校验失败。

## 参考仓库与采纳点

- [Anthropic Skills](https://github.com/anthropics/skills)：保持每个 skill 自包含，并按用户任务与能力用途提供概念分类。
- [Microsoft Skills](https://github.com/microsoft/skills)：保留自包含 skill，并以稳定主分类组织物理目录；目录页继续承担跨主题导航和按需选择。
- [NVIDIA Skills](https://github.com/NVIDIA/skills)：将分类物理目录、导航文档和机器索引统一从单一源生成，并通过自动校验防止路径与内容漂移。
