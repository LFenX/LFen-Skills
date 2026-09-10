<p align="center">
  <img src="assets/logo.svg" alt="LFen Skills" width="460">
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg?style=flat-square" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/github/license/LFenX/LFen-Skills?style=flat-square" alt="license">
</p>

<p align="center">
  <a href="README.en.md">🏠 README</a> &nbsp;·&nbsp; <b>📦 Skills</b> &nbsp;·&nbsp; <a href="SKILLS.md">中文</a>
</p>

---

## 📊 Data Processing

> Matching, cleaning, transforming, and verifying structured data

### [`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md)

Reconcile two CSV/XLSX tables by a single key or an ordered composite of multiple fields, with per-type normalization for text, identifiers, numbers, and dates. Produces an inner join, two directional unmatched-detail sheets, duplicate and invalid-key audits, and a validated formatted Excel workbook.

**Use for**: cross-file matching, list reconciliation, coverage analysis, and record comparison by any key columns (IDs, names, dates, order numbers, and more).

---

## 📐 Product Engineering

> Product definition, development execution, quality control, and delivery

### [`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md)

From a basic product brief to a shipped, complex web admin: requirement tracing, PRD, product package, frontend-backend integration, acceptance, and rework loops — with traceable records in Feishu docs and bases.

**Use for**: new project delivery. Not for governance-only audits, single-point bug fixes, or re-reviews of shipped products.

### [`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md)

Drive any task that changes product behavior: features, changes, bug fixes, refactors, migrations, releases, and re-reviews. Maintains verifiable requirements, plans, execution, verification, and acceptance per the team's V6.3 norms — minimal tasks keep just one file, but never skip clarification or acceptance.

**Use for**: any change that affects product behavior, external interfaces, documentation layout, or release outcomes, plus item-by-item re-reviews of delivered work.

### [`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md)

Filter, claim, and drive development items from a KOC feedback base, syncing clarification, planning, execution, review, rework, and completion status back to the table throughout the lifecycle.

**Use for**: base-driven iteration of the funplus-UA-KOC-Management-Platform.

---

## 🔧 Dev Tools

> Setup, integration, and troubleshooting for dev environments and AI coding assistants

### [`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md)

Connect opencode to third-party OpenAI-compatible model providers (e.g. a LiteLLM gateway): provider configuration, model registration, gateway verification, and common error troubleshooting.

**Use for**: adding a new model provider, configuring the `provider` section of `opencode.json`, or when a model config doesn't take effect.

---

<p align="center">
  <a href="CATALOG.md">CATALOG.md</a> &nbsp;·&nbsp; <a href="catalog/index.json">catalog/index.json</a> &nbsp;·&nbsp; <a href="README.en.md">Back to README</a>
</p>
