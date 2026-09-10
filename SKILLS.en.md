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
  <a href="README.en.md"><img src="https://img.shields.io/badge/README-64748B?style=flat" alt="README"></a>
  <a href="SKILLS.en.md"><img src="https://img.shields.io/badge/%E2%97%8F_Skills-8B5CF6?style=flat" alt="Skills"></a>
  <a href="SKILLS.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-64748B?style=flat" alt="中文"></a>
</p>

## Index

<!-- catalog-detail:start -->
| Category | Skill | Description |
| --- | --- | --- |
| [**Data Processing**](CATALOG.md#data-processing) |  | Matching, cleaning, transforming, analyzing, and verifying structured data. |
|  | [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md) | Reconcile two CSV/XLSX tables by one field or an ordered composite of multiple fields, with configurable exact, text, identifier, number, date, or datetime normalization. Produce an inner join, two directional unmatched-detail sheets, optional secondary-key matching, duplicate and invalid-key audits, subset statistics, and a validated formatted Excel workbook. Use for cross-file matching, inclusion checks, list reconciliation, data coverage analysis, or record comparison by IDs, names, titles, authors, dates, account fields, order numbers, or any user-specified key columns. |
| [**Product Engineering**](CATALOG.md#product-engineering) |  | Product definition, development execution, quality control, delivery, and operations. |
|  | [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md) | From a basic product brief to frontend-backend integration and acceptance, using requirement tracing, PRD, product package, Feishu doc and base records, template or designated UI, control binding, and rework loops to help a coding agent build a complex large-scale web admin from zero to one. Use for new project delivery. Not for governance-only audits, single-point bugs, pure backend library changes, or re-reviews of delivered products. |
|  | [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md) | Drive concrete development tasks such as new features, requirement changes, bug fixes, refactors, migrations and retirement, releases, and re-acceptance — frontend, backend, scripts, config, and docs alike. Maintains verifiable requirements, plans, execution, verification, acceptance, and evidence per the team V6.3 norms, scaling between the Minimal and full carrier with the same six-element model — a small task keeps just one file but never skips clarification or acceptance. Applies to any change that alters product behavior, externally visible interfaces, documentation layout, or release outcomes. Also for reviewing delivered work — review again, check closed-loop, anything missed, all requirements implemented, acceptance — via verify, checked item by item against the original requirement text without sampling. Applies when the user mentions Grill Me, Task Profile, Artifact Manifest, VC-PPG, C01-C12, E01-E05, or the lightest framework. Not for pure read-only Q&A or one-off git commands that change no behavior. |
|  | [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md) | Filter, list, claim, and drive development items from the KOC feedback base, syncing clarification, planning, execution, review, rework, and completion status after user authorization. Use for base-item-driven defect fixes, experience improvements, or new features of funplus-UA-KOC-Management-Platform. Do not process records whose evoking developer is only LFen. |
| [**Dev Tools**](CATALOG.md#dev-tools) |  | Setup, integration, troubleshooting, and maintenance for dev environments, toolchains, and AI coding assistants. |
|  | [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md) | Connect opencode to third-party OpenAI-compatible model providers such as a LiteLLM gateway. Covers provider configuration structure, model registration, gateway verification, and common error troubleshooting. Use when adding a new model provider, configuring the provider section of opencode.json, or when a model config does not take effect. |
<!-- catalog-detail:end -->

---

## 📊 Data Processing

> Matching, cleaning, transforming, and verifying structured data

### [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md)

![general](https://img.shields.io/badge/general-2ea44f?style=flat-square)
`data-matching` `data-quality` `excel`

Reconcile two CSV/XLSX tables by a single key or an ordered composite of multiple fields, with per-type normalization for text, identifiers, numbers, and dates. Produces an inner join, two directional unmatched-detail sheets, duplicate and invalid-key audits, and a validated formatted Excel workbook.

**Use for**: cross-file matching, list reconciliation, coverage analysis, and record comparison by any key columns (IDs, names, dates, order numbers, and more).

---

## 📐 Product Engineering

> Product definition, development execution, quality control, and delivery

### [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md)

![general](https://img.shields.io/badge/general-2ea44f?style=flat-square)
`agentic-development` `frontend-backend` `product-specification` `sop` `web-admin`

From a basic product brief to a shipped, complex web admin: requirement tracing, PRD, product package, frontend-backend integration, acceptance, and rework loops — with traceable records in Feishu docs and bases.

**Use for**: new project delivery. Not for governance-only audits, single-point bug fixes, or re-reviews of shipped products.

### [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md)

![team](https://img.shields.io/badge/team-0EA5E9?style=flat-square)
`product-delivery` `product-governance` `verification`

Drive any task that changes product behavior: features, changes, bug fixes, refactors, migrations, releases, and re-reviews. Maintains verifiable requirements, plans, execution, verification, and acceptance per the team's V6.3 norms — minimal tasks keep just one file, but never skip clarification or acceptance.

**Use for**: any change that affects product behavior, external interfaces, documentation layout, or release outcomes, plus item-by-item re-reviews of delivered work.

### [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md)

![project](https://img.shields.io/badge/project-F59E0B?style=flat-square)
`feedback-management` `feishu-base` `koc`

Filter, claim, and drive development items from a KOC feedback base, syncing clarification, planning, execution, review, rework, and completion status back to the table throughout the lifecycle.

**Use for**: base-driven iteration of the funplus-UA-KOC-Management-Platform.

---

## 🔧 Dev Tools

> Setup, integration, and troubleshooting for dev environments and AI coding assistants

### [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md)

![general](https://img.shields.io/badge/general-2ea44f?style=flat-square)
`model-provider` `openai-compatible` `opencode` `tool-configuration`

Connect opencode to third-party OpenAI-compatible model providers (e.g. a LiteLLM gateway): provider configuration, model registration, gateway verification, and common error troubleshooting.

**Use for**: adding a new model provider, configuring the `provider` section of `opencode.json`, or when a model config doesn't take effect.

---

<p align="center">
  <a href="CATALOG.md">CATALOG.md</a> &nbsp;·&nbsp; <a href="catalog/index.json">catalog/index.json</a> &nbsp;·&nbsp; <a href="README.en.md">Back to README</a>
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,50:22D3EE,100:F59E0B&height=100&section=footer" width="100%" alt="">
</p>
