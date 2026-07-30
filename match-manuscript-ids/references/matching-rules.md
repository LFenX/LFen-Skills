# Matching Rules

## Field Detection

The script scans the first 30 rows for a header containing the requested ID field or a common alias.

ID aliases:

```text
稿件ID, 作品ID, 笔记ID, 内容ID, 视频ID, 稿件编号, 作品编号,
manuscript_id, work_id, note_id, content_id, video_id, aid, avid
```

Optional fields use these alias groups:

- Title: `内容标题`, `稿件标题`, `作品标题`, `笔记标题`, `视频标题`, `标题`, `title`
- Author: `作者`, `作者昵称`, `发布账号`, `博主`, `博主昵称`, `UP主`, `UP主昵称`, `author`, `uploader`, `nickname`
- Link: `笔记链接`, `作品链接`, `内容链接`, `视频链接`, `链接`, `url`, `link`
- Date: `发布时间`, `发布日期`, `投稿时间`, `创建时间`, `publish_time`, `publish_date`

Use explicit CLI mappings when a source uses a business-specific field name or contains multiple plausible ID columns.

## ID Normalization

Normalization is deterministic:

1. Apply Unicode NFKC normalization.
2. Remove control, format, line-separator, paragraph-separator, and whitespace characters.
3. Remove one or more leading Excel text apostrophes.
4. Preserve digit strings, including leading zeroes.
5. Convert integer-valued decimal strings such as `123.0` to `123`.
6. Convert exact integer scientific notation such as `1.23E+5` to `123000`.
7. Extract IDs when the ID cell itself contains a supported Xiaohongshu or Bilibili URL.
8. Case-fold nonnumeric IDs unless `--id-case-sensitive` is set.

Numeric Excel cells with 16 or more integer digits are flagged as potential source precision risks. The output cannot recover digits already rounded in the source workbook.

## Match Semantics

- `inner join`: Every file-A row is paired with every file-B row sharing the same normalized ID.
- File-A unmatched: Valid IDs absent from file B plus blank/invalid file-A IDs.
- File-B unmatched: Valid IDs absent from file A plus blank/invalid file-B IDs.
- Duplicate groups: A normalized ID appearing more than once within one source.
- Match rate: Matched unique valid IDs divided by that source's unique valid IDs.
- Subset: Calculated from unique valid normalized ID sets.

## Title And Author Supplement

Title and author are NFKC-normalized, whitespace-collapsed, and case-folded. Only ID-unmatched rows are considered. Rows are paired one-to-one within a common normalized title-author group, preferring the nearest available publish time and then source-row order.

These pairs remain in the unmatched-detail sheets with a supplementary-match marker. They do not increase the exact ID-match count.

## Output Rules

- Never overwrite either source file.
- Store ID columns as text.
- Prefix source columns with `文件A_` and `文件B_` in the inner join.
- Retain source row numbers for traceability.
- Keep the four visible sheets in the prescribed order.
- Include empty unmatched sheets with formatted headers.
- Include the source paths, field mappings, counts, rates, normalization audit, link audit, title-author analysis, and final relationship in `分析汇总`.
