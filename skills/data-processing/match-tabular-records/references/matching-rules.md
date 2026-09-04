# Matching Rules

## Primary Key Mapping

Each `--left-key` must have a positionally corresponding `--right-key`.

```text
left key 1  <-> right key 1
left key 2  <-> right key 2
...
```

One pair creates a simple key. Multiple pairs create an ordered tuple. Internal comparison uses tuples, not delimiter-joined strings, so field values containing punctuation cannot collide.

If no key arguments are provided, the script attempts single-field ID detection from the first 30 rows. Explicit mappings are required for non-ID matching and ambiguous files.

## Normalization

### `exact`

Compare the source scalar representation exactly. Blank values are invalid.

### `text`

Apply Unicode NFKC, remove control and invisible formatting characters, collapse whitespace, trim, and case-fold unless `--case-sensitive` is set.

### `id`

Apply text normalization plus:

1. Remove leading Excel text apostrophes.
2. Remove whitespace within the identifier.
3. Preserve digit strings and leading zeroes.
4. Convert integer decimal strings such as `123.0` to `123`.
5. Convert exact integer scientific notation such as `1.23E+5` to `123000`.
6. Extract identifiers when the key cell itself contains a supported Xiaohongshu or Bilibili URL.

Numeric Excel cells with 16 or more integer digits are flagged as source precision risks. Digits already rounded in the source cannot be recovered.

### `number`

Parse an exact decimal after removing comma display separators. Normalize exponent notation and trailing zeroes. Non-numeric values are invalid.

### `date` and `datetime`

Accept Excel date/datetime cells and common ISO-style strings. `date` compares only `yyyy-mm-dd`; `datetime` compares to whole seconds.

### `auto`

Choose `id` for identifier-like field names, `date` for date/time-like names, and `text` otherwise. Use an explicit mode whenever business semantics differ from the field name.

## Validity And Duplicates

- A composite primary key is valid only when every normalized component is nonblank.
- Rows with invalid keys remain in the source-side unmatched sheet.
- A duplicate group is one valid normalized tuple appearing more than once within a source.
- The inner join is many-to-many: all rows sharing the same key are paired.
- Match rates and subset conclusions use unique valid normalized tuples.

## Secondary Matching

Secondary fields are optional and also form ordered tuples. They are evaluated only among primary-key-unmatched records.

Rows sharing a secondary tuple are paired one-to-one. Pairing prefers the nearest available publish date/time when date fields are mapped, then source-row order. Secondary matches remain in the unmatched sheets with a marker and counterpart trace fields.

## Output Rules

- Never overwrite either source file.
- Keep normalized primary-key components in separate leading columns.
- Retain source row numbers.
- Prefix original columns with `文件A_` and `文件B_` in the inner join.
- Store key and identifier columns as strings while using a non-scientific display format.
- Keep the four prescribed visible sheets in order.
- Format empty unmatched sheets with headers and no fabricated data row.
- Include key mappings, normalizers, counts, rates, raw/trimmed/normalized audits, duplicate and invalid counts, precision warnings, secondary matching, and final relationship in `分析汇总`.
