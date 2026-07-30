---
name: match-manuscript-ids
description: Compare two CSV/XLSX datasets by manuscript, work, note, content, or video ID; normalize formatting differences; produce an inner join, two directional unmatched-detail sheets, title-and-author supplementary analysis, subset statistics, and a validated formatted Excel workbook. Use when the user asks to match, reconcile, audit, or determine inclusion/subset relationships between two exported content lists by 稿件ID、作品ID、笔记ID、内容ID、视频ID or equivalent fields.
---

# Match Manuscript IDs

Use the bundled deterministic script to compare two tabular exports without modifying either source file.

## Workflow

1. Confirm the two source paths and the semantic equivalence of their ID fields.
2. Run `scripts/match_manuscript_ids.py --help` when field names, worksheets, or header positions are unusual.
3. Prefer explicit `--left-id` and `--right-id` arguments when the user has named the fields. Let the script auto-detect common title, author, link, and publish-time fields unless explicit mappings are needed.
4. Generate one workbook with exactly four visible sheets:
   - `匹配表_inner join`
   - `不匹配详情_文件A`
   - `不匹配详情_文件B`
   - `分析汇总`
5. Read the script's JSON result. Report exact matches, directional unmatched counts, both match rates, duplicate/invalid-ID warnings, subset relationship, and title-author supplementary matches.
6. Render and inspect all four output sheets when spreadsheet rendering tools are available. Check headers, visible full IDs, empty-detail-sheet presentation, widths, frozen panes, and overlaps.
7. Return only the final validated workbook to the user.

## Command

```powershell
python scripts/match_manuscript_ids.py `
  "C:\path\file-a.csv" `
  "C:\path\file-b.xlsx" `
  --left-id "稿件ID" `
  --right-id "作品ID" `
  --output "C:\path\稿件ID匹配结果.xlsx" `
  --json-report "C:\path\稿件ID匹配结果.json"
```

Use these overrides only when auto-detection is insufficient:

```text
--left-sheet / --right-sheet
--left-header-row / --right-header-row
--left-title / --right-title
--left-author / --right-author
--left-link / --right-link
--left-date / --right-date
--left-label / --right-label
--id-case-sensitive
--skip-title-author
```

## Matching Requirements

- Match on normalized ID, not Excel display formatting.
- Preserve canonical IDs as text in the output to avoid scientific notation and precision loss.
- Treat NFKC variants, surrounding/invisible whitespace, a leading Excel apostrophe, integer-valued decimals, and scientific notation as formatting differences.
- Do not repair a missing ID from a separate link field. Use links only for audit unless the ID cell itself contains a supported URL.
- Keep invalid-ID records in the corresponding unmatched sheet.
- Use a Cartesian inner join for duplicate IDs and report duplicate groups separately.
- Evaluate title-and-author matches only among ID-unmatched records and mark them as supplementary, not exact ID matches.
- Base subset conclusions on unique valid normalized ID sets. Report invalid IDs separately.
- Stop and request an explicit mapping if the ID field cannot be identified unambiguously.

Read [references/matching-rules.md](references/matching-rules.md) for normalization rules, field aliases, output semantics, and edge cases.

## Validation

The script reopens every generated workbook and verifies:

- ZIP/OOXML integrity;
- exact four-sheet order;
- expected data-row counts;
- matched and unmatched ID sets;
- ID cells stored as strings;
- absence of Excel error values;
- consistency between workbook contents and computed statistics.

Run the regression test after changing the skill:

```powershell
python scripts/self_test.py
```
