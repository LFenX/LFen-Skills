<p align="center">
  <img src="assets/banner.svg" alt="LFen Skills" width="100%">
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Manrope&size=22&pause=1200&color=8B5CF6&center=true&vCenter=true&width=700&lines=Agent+Skills+distilled+from+my+work+and+study;Take+whatever+is+useful+to+you;One+command+%C2%B7+7+platforms" alt="Agent Skills distilled from my work and study">
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
  <img src="https://img.shields.io/badge/README-8B5CF6?style=flat" alt="README">
  <a href="SKILLS.en.md"><img src="https://img.shields.io/badge/Skills-475569?style=flat" alt="Skills"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-475569?style=flat" alt="中文"></a>
</p>

## Install

**Windows**

```powershell
iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
```

<p align="center">
  <img src="assets/install-demo.gif" alt="install demo" width="100%">
</p>

Follow the prompts to pick platforms and skills. Skills are linked (junction on Windows, symlink elsewhere) to a local clone at `~/.lfenskills`, so a plain `git pull` there updates everything in place.

```powershell
.\install.ps1 -Status                    # Show what's installed where
.\install.ps1 -Update                    # Selectively refresh skills
.\install.ps1 -All -AllSkills -Force     # Silent full install
```

## Skills

Detailed introductions for every skill live on the **[Skills](SKILLS.en.md)** page. Full catalog in [`CATALOG.md`](CATALOG.md); machine-readable index in [`catalog/index.json`](catalog/index.json).

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

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,50:22D3EE,100:F59E0B&height=100&section=footer" width="100%" alt="">
</p>
