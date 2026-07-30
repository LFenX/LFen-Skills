---
name: match-tabular-records
description: Reconcile two CSV/XLSX tables by one field or an ordered composite of multiple fields, with configurable exact, text, identifier, number, date, or datetime normalization. Produce an inner join, two directional unmatched-detail sheets, optional secondary-key matching, duplicate and invalid-key audits, subset statistics, and a validated formatted Excel workbook. Use for cross-file matching, inclusion checks, list reconciliation, data coverage analysis, or record comparison by IDs, names, titles, authors, dates, account fields, order numbers, or any user-specified key columns.
---

# Match Tabular Records

Use the bundled deterministic script to compare two tabular exports without modifying either source.

## Workflow

1. Confirm the two source paths and map each file-A key field to its semantically equivalent file-B key field.
2. Use one key pair for a simple join or multiple ordered key pairs for a composite join.
3. Select a normalizer for each pair. Use `auto` unless business semantics require an explicit mode.
4. Add optional secondary key pairs only when the user wants to identify likely equivalents among primary-key-unmatched rows.
5. Run `scripts/match_tabular_records.py`.
6. Read the JSON result and report matched rows/keys, directional differences, rates, duplicate/invalid keys, subset relationship, and secondary matches.
7. Render and inspect all four output sheets when spreadsheet rendering tools are available.
8. Return only the final validated workbook.

## Commands

Single-field matching:

```powershell
python scripts/match_tabular_records.py `
  "C:\path\file-a.csv" `
  "C:\path\file-b.xlsx" `
  --left-key "稿件ID" `
  --right-key "作品ID" `
  --key-normalizer id `
  --output "C:\path\字段匹配结果.xlsx"
```

Composite matching:

```powershell
python scripts/match_tabular_records.py `
  "C:\path\file-a.xlsx" `
  "C:\path\file-b.xlsx" `
  --left-key "内容标题" --right-key "笔记标题" `
  --left-key "作者昵称" --right-key "作者" `
  --key-normalizer text `
  --key-normalizer text `
  --output "C:\path\标题作者匹配结果.xlsx"
```

Primary ID matching plus supplementary title-and-author matching:

```powershell
python scripts/match_tabular_records.py `
  "C:\path\file-a.csv" `
  "C:\path\file-b.xlsx" `
  --left-key "稿件ID" --right-key "作品ID" `
  --key-normalizer id `
  --left-secondary-key "内容标题" --right-secondary-key "内容标题" `
  --left-secondary-key "作者昵称" --right-secondary-key "作者" `
  --secondary-normalizer text `
  --secondary-normalizer text `
  --output "C:\path\匹配与补充分析.xlsx"
```

## Normalizers

- `auto`: Infer from both field names; identifiers use `id`, dates use `date`, otherwise use `text`.
- `id`: Normalize identifier formatting, leading apostrophes, integer decimals, scientific notation, whitespace, Unicode width, and case.
- `text`: Apply NFKC, remove invisible characters, collapse whitespace, and case-fold.
- `number`: Compare exact decimal values after removing display separators and trailing zeroes.
- `date`: Compare calendar dates as `yyyy-mm-dd`.
- `datetime`: Compare timestamps to seconds.
- `exact`: Compare source scalar representations without trimming or case conversion.

Repeat `--key-normalizer` once per key pair, or provide it once to apply to every pair. The same rule applies to `--secondary-normalizer`.

## Required Semantics

- Treat ordered normalized field tuples as keys; do not concatenate fields for internal comparison.
- Do not match rows whose primary key has any blank or invalid component.
- Use a Cartesian inner join when duplicate keys exist and report duplicate groups separately.
- Keep invalid-key records in the corresponding unmatched sheet.
- Treat secondary matches as one-to-one supplementary judgments among unmatched rows; never add them to the primary inner join.
- Base subset conclusions on unique valid normalized primary-key sets.
- Preserve key components as text in the output to prevent scientific notation or precision loss.
- Stop and request explicit mappings when fields cannot be identified unambiguously.

Read [references/matching-rules.md](references/matching-rules.md) for normalization, composite-key, duplicate, secondary-pairing, and output rules.

## Output

Create exactly four visible sheets:

- `匹配表_inner join`
- `不匹配详情_文件A`
- `不匹配详情_文件B`
- `分析汇总`

The script reopens the output and verifies OOXML integrity, sheet order, shapes, matched and unmatched key sets, key text storage, and absence of Excel errors.

Run regression tests after changing the skill:

```powershell
python scripts/self_test.py
```
