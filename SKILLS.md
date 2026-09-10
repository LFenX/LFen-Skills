<p align="center">
  <img src="assets/banner.svg" alt="LFen Skills" width="100%">
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
  <a href="README.md"><img src="https://img.shields.io/badge/README-475569?style=flat" alt="README"></a>
  <img src="https://img.shields.io/badge/Skills_%E4%B8%80%E8%A7%88-8B5CF6?style=flat" alt="Skills 一览">
  <a href="SKILLS.en.md"><img src="https://img.shields.io/badge/English-475569?style=flat" alt="English"></a>
</p>

## 索引

<!-- catalog-detail:start -->
| 分类 | Skill | 能力说明 |
| --- | --- | --- |
| [**数据处理**](CATALOG.md#data-processing) |  | 结构化数据的匹配、清洗、转换、分析与质量核验。 |
|  | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) | Reconcile two CSV/XLSX tables by one field or an ordered composite of multiple fields, with configurable exact, text, identifier, number, date, or datetime normalization. Produce an inner join, two directional unmatched-detail sheets, optional secondary-key matching, duplicate and invalid-key audits, subset statistics, and a validated formatted Excel workbook. Use for cross-file matching, inclusion checks, list reconciliation, data coverage analysis, or record comparison by IDs, names, titles, authors, dates, account fields, order numbers, or any user-specified key columns. |
| [**产品研发**](CATALOG.md#product-engineering) |  | 产品定义、研发执行、质量控制、交付与运营流程。 |
|  | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md) | 从基础产品说明到前后端联调和验收，使用需求追溯、PRD、产品包、飞书云文档/多维表格留痕、模板或指定 UI、控件绑定与返修闭环，协助 Coding Agent 从 0 到 1 构建复杂大型 Web 生产后台。适用于新项目交付；不用于仅治理审计、单点 bug、纯后端库修改或已交付产品复查。 |
|  | [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md) | 用于推进具体开发任务：新功能、改需求、修 bug、重构、迁移退役、发布上线、复查验收；前端、后端、脚本、配置、文档同等适用。按团队 V6.3 规范维护可核对的需求、计划、执行、验证、验收和证据，用同一六元模型在 Minimal 与完整载体之间裁剪——小任务只写一个文件，但不因为任务小就跳过澄清和验收。凡是会改变产品行为、外部可见接口、文档布局或发布结果的改动都适用。也用于对已交付内容的复查——“review 一遍 / 再查一遍 / 是否闭环 / 有没有遗漏 / 需求是否都实现了 / 验收”，此类请求走 verify，按总原则 10 逐条对照需求原文，不抽查。用户提到 Grill Me、Task Profile、Artifact Manifest、VC-PPG、C01-C12、E01-E05 或“最轻框架”时同样适用。不用于纯只读问答，以及不改变任何行为的一次性 git 命令。 |
|  | [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) | 从 KOC 后台反馈 Base 筛选、列举、认领并推进开发登记项，在用户授权后同步澄清、规划、执行、复核、返修和完成状态。用于以飞书多维表格登记项驱动 funplus-UA-KOC-Management-Platform 的缺陷修复、体验优化或新功能；不得处理“唤起开发者”仅为 LFen 的记录。 |
| [**开发工具**](CATALOG.md#dev-tools) |  | 开发环境、工具链与 AI 编码助手的配置、接入、排障与维护。 |
|  | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) | 为 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）。覆盖 provider 配置结构、模型注册、网关验证、常见错误排查。当用户要添加新的模型供应商、配置 opencode.json 的 provider 段、或模型配置后不生效时使用。 |
<!-- catalog-detail:end -->

---

## 📊 数据处理

> 结构化数据的匹配、清洗、转换与质量核验

### [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md)

![通用](https://img.shields.io/badge/%E9%80%9A%E7%94%A8-2ea44f?style=flat-square)
`data-matching` `data-quality` `excel`

两张 CSV/XLSX 表按键对账。支持单字段或多字段组合键，文本、编号、数字、日期各自归一化；产出匹配合集、双向未匹配明细、重复与非法键审计，最终输出校验过的格式化 Excel 工作簿。

**适用**：跨文件核对、名单比对、覆盖率分析、按任意键列（ID、姓名、日期、单号等）做记录比对。

---

## 📐 产品研发

> 产品定义、研发执行、质量控制与交付流程

### [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md)

![通用](https://img.shields.io/badge/%E9%80%9A%E7%94%A8-2ea44f?style=flat-square)
`agentic-development` `frontend-backend` `product-specification` `sop` `web-admin`

从一份基础产品说明出发，走完需求追溯、PRD、产品包、前后端联调到验收返修的全流程，帮 Coding Agent 从 0 到 1 交付复杂 Web 生产后台；过程在飞书云文档 / 多维表格留痕。

**适用**：新项目交付。不用于仅治理审计、单点 bug 修复或已交付产品复查。

### [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md)

![团队](https://img.shields.io/badge/%E5%9B%A2%E9%98%9F-0EA5E9?style=flat-square)
`product-delivery` `product-governance` `verification`

推进任何改变产品行为的开发任务：新功能、改需求、修 bug、重构、迁移、发布、复查验收。按团队 V6.3 规范维护需求、计划、执行、验证、验收的证据链——小任务只留一个文件，但不跳过澄清和验收。

**适用**：会改变产品行为、外部接口、文档布局或发布结果的任何改动，以及已交付内容的逐条复查。

### [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md)

![项目](https://img.shields.io/badge/%E9%A1%B9%E7%9B%AE-F59E0B?style=flat-square)
`feedback-management` `feishu-base` `koc`

从 KOC 反馈多维表格筛选、认领、推进开发登记项，澄清、规划、执行、复核、返修、完成状态全程同步回表，驱动 KOC 管理平台的缺陷修复与功能迭代。

**适用**：以飞书多维表格登记项驱动 funplus-UA-KOC-Management-Platform 的迭代开发。

---

## 🔧 开发工具

> 开发环境与 AI 编码助手的配置、接入与排障

### [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md)

![通用](https://img.shields.io/badge/%E9%80%9A%E7%94%A8-2ea44f?style=flat-square)
`model-provider` `openai-compatible` `opencode` `tool-configuration`

给 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）：provider 配置结构、模型注册、网关验证、常见错误排查。

**适用**：添加新的模型供应商、配置 `opencode.json` 的 provider 段、或模型配置后不生效时。

---

<p align="center">
  <a href="CATALOG.md">CATALOG.md</a> &nbsp;·&nbsp; <a href="catalog/index.json">catalog/index.json</a> &nbsp;·&nbsp; <a href="README.md">返回 README</a>
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,50:22D3EE,100:F59E0B&height=100&section=footer" width="100%" alt="">
</p>
