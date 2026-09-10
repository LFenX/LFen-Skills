<p align="center">
  <img src="assets/logo.svg" alt="LFen Skills" width="460">
</p>

<p align="center">
  Agent Skills distilled from my own work and study — feel free to take whatever is useful to you.<br>
  Every skill is self-contained, installed to 7 platforms with one command.
</p>

<p align="center">
  <a href="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml">
    <img src="https://github.com/LFenX/LFen-Skills/actions/workflows/catalog.yml/badge.svg?style=flat-square" alt="Catalog CI">
  </a>
  <img src="https://img.shields.io/github/license/LFenX/LFen-Skills?style=flat-square" alt="license">
</p>

<p align="center">
  <a href="README.md">中文</a> &nbsp;|&nbsp; <b>English</b>
</p>

## Skills

### 📊 Data Processing

> Matching, cleaning, transforming, and verifying structured data

- **[`match-tabular-records`](skills/data-processing/match-tabular-records/SKILL.md)** — Reconcile two CSV/XLSX tables by a single key or an ordered composite of multiple fields, with per-type normalization for text, identifiers, numbers, and dates. Produces an inner join, two directional unmatched-detail sheets, duplicate and invalid-key audits, and a validated formatted Excel workbook. Use for cross-file matching, list reconciliation, and coverage analysis.

### 📐 Product Engineering

> Product definition, development execution, quality control, and delivery

- **[`build-large-web-project-zero-to-one`](skills/product-engineering/build-large-web-project-zero-to-one/SKILL.md)** — From a basic product brief to a shipped, complex web admin: requirement tracing, PRD, product package, frontend-backend integration, acceptance, and rework loops — with traceable records in Feishu docs and bases.
- **[`run-governed-product-workflow`](skills/product-engineering/run-governed-product-workflow/SKILL.md)** — Drive any task that changes product behavior: features, changes, bug fixes, refactors, migrations, releases, and re-reviews. Maintains verifiable requirements, plans, execution, verification, and acceptance per the team's V6.3 norms — minimal tasks keep just one file, but never skip clarification or acceptance.
- **[`run-koc-feedback-workflow`](skills/product-engineering/run-koc-feedback-workflow/SKILL.md)** — Filter, claim, and drive development items from a KOC feedback base, syncing clarification, planning, execution, review, rework, and completion status back to the table throughout the lifecycle.

### 🔧 Dev Tools

> Setup, integration, and troubleshooting for dev environments and AI coding assistants

- **[`add-opencode-model-provider`](skills/dev-tools/add-opencode-model-provider/SKILL.md)** — Connect opencode to third-party OpenAI-compatible model providers (e.g. a LiteLLM gateway): provider configuration, model registration, gateway verification, and common error troubleshooting.

Full catalog in [`CATALOG.md`](CATALOG.md); machine-readable index in [`catalog/index.json`](catalog/index.json).

## Install

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

Follow the prompts to pick platforms and skills. Skills are linked (junction on Windows, symlink elsewhere) to a local clone at `~/.lfenskills`, so a plain `git pull` there updates everything in place.

```powershell
.\install.ps1 -Status                    # Show what's installed where
.\install.ps1 -Update                    # Selectively refresh skills
.\install.ps1 -All -AllSkills -Force     # Silent full install
```

## Supported Platforms

| Platform | Skill Directory | Notes |
| --- | --- | --- |
| OpenCode | `~/.agents/skills/` | Also covers Cline, Warp, Zed, Kilo, Kimi, Droid, Firebender, and 20+ more |
| Claude Code | `~/.claude/skills/` | |
| Codex | `~/.codex/skills/` | |
| Cursor | `~/.cursor/skills/` | |
| Gemini CLI | `~/.gemini/skills/` | |
| GitHub Copilot | `~/.copilot/skills/` | |
| Windsurf | `~/.codeium/windsurf/skills/` | |

## Adding a Skill

1. Create `skills/<category>/<skill-name>/SKILL.md` — the directory name must match the frontmatter `name`.
2. Add the skill to the matching leaf category in `catalog/taxonomy.json`, with `scope` and sorted `tags` under `skill_metadata`.
3. Run `python scripts/update_catalog.py` to regenerate the README summary, `CATALOG.md`, and `catalog/index.json`.
4. Run `python scripts/update_catalog.py --check` to verify, then commit and push.

## License

[MIT](LICENSE)
