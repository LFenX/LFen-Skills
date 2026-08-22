# LFen Skills 分类目录

> 此文件由 `python scripts/update_catalog.py` 生成。请修改 `catalog/taxonomy.json`，不要直接编辑此文件。

## 分类总览

| 一级分类 | 定义 | Skill 数量 |
| --- | --- | ---: |
| [数据处理](#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | 1 |
| [产品研发](#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | 1 |

共收录 **2** 个 skill。

<a id="data-processing"></a>
## 数据处理

结构化数据的匹配、清洗、转换、分析与质量核验。

| Skill | 能力说明 |
| --- | --- |
| [`match-tabular-records`](match-tabular-records/SKILL.md) | Reconcile two CSV/XLSX tables by one field or an ordered composite of multiple fields, with configurable exact, text, identifier, number, date, or datetime normalization. Produce an inner join, two directional unmatched-detail sheets, optional secondary-key matching, duplicate and invalid-key audits, subset statistics, and a validated formatted Excel workbook. Use for cross-file matching, inclusion checks, list reconciliation, data coverage analysis, or record comparison by IDs, names, titles, authors, dates, account fields, order numbers, or any user-specified key columns. |

<a id="product-engineering"></a>
## 产品研发

产品定义、研发执行、质量控制、交付与运营流程。

| Skill | 能力说明 |
| --- | --- |
| [`run-web-product-workflow`](run-web-product-workflow/SKILL.md) | 按团队 V6.3 Candidate 规范推进 Web 产品或工程变化，用同一六元模型在 Minimal 与完整流程之间裁剪，并维护需求、计划、执行、验证、验收、发布和证据。用于新产品、新功能、需求修订、带产品面的缺陷修复或工程变更、迁移退役、生产处置，或用户明确要求 Grill Me、Task Profile、Artifact Manifest、VC-PPG、C01-C12、E01-E05 或“最轻框架”时。Not for read-only Q&A, git one-liners, or edits that do not change product behavior, docs layout, or release. Not for backend-only library patches with no Web product surface. |

## 分类演进规则

1. 一级分类最多保留 2 个，按稳定的用户任务域划分。
2. 每个 skill 只归入一个最具体的分类节点，禁止重复归类。
3. 新增 skill 时先放入现有一级分类；同一主题形成多个 skill 后再增加子分类。
4. 分类只影响目录展示，不移动 skill 根目录，不修改 `SKILL.md` frontmatter。
5. 目录由脚本从 `SKILL.md` 的 `name` 与 `description` 动态生成；校验失败时禁止合入。

## 参考仓库与采纳点

- [Anthropic Skills](https://github.com/anthropics/skills#skill-sets)：按用户任务与能力用途划分领域，而不是按脚本语言划分。
- [Microsoft Skills](https://github.com/microsoft/skills#adding-new-skills)：用一级分类和按需子分类组织目录，并让分类导航独立于 skill 的规范目录。
- [NVIDIA Skills](https://github.com/NVIDIA/skills#skill-catalog)：从元数据自动生成目录，以支持 skill 持续新增和更新。
