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
| [`run-web-product-workflow`](run-web-product-workflow/SKILL.md) | 按团队的 AI Native Web 产品生产规范推进需求澄清、任务分类、计划、开发、验证、验收、发布与观察，并自动裁剪适用规范、缩放产物和维护证据。用于新产品、模板派生、新功能、需求修订、缺陷修复、工程或配置变更、迁移替代退役、生产处置，以及用户要求使用通用生产流程、Grill Me、多轮澄清、Task Profile、Artifact Manifest、C01-C12 或 E01-E05 时。 |

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
