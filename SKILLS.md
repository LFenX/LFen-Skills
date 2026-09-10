<p align="center">
  <img src="assets/banner.svg" alt="LFen Skills" width="100%">
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg?style=for-the-badge" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/badge/skills-5-8B5CF6?style=for-the-badge" alt="skills">
  <img src="https://img.shields.io/badge/platforms-7-0EA5E9?style=for-the-badge" alt="platforms">
  <img src="https://img.shields.io/github/license/LFenX/LFen-Skills?style=for-the-badge" alt="license">
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/%F0%9F%8F%A0_README-334155?style=for-the-badge" alt="README"></a>
  <img src="https://img.shields.io/badge/%F0%9F%93%A6_Skills_%E4%B8%80%E8%A7%88-8B5CF6?style=for-the-badge" alt="Skills 一览">
  <a href="SKILLS.en.md"><img src="https://img.shields.io/badge/%F0%9F%8C%90_English-334155?style=for-the-badge" alt="English"></a>
</p>

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
