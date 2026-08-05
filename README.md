# LFen Skills

LFen Skills 是可复用的 Agent Skills 集合。Skill 继续保存在仓库根目录；分类只用于发现和导航，不改变 skill 的安装路径。

## 当前分类

当前只设置两个一级分类。以下区块由分类脚本同步：

<!-- catalog-summary:start -->
| 分类 | 定义 | Skills |
| --- | --- | --- |
| [数据处理](CATALOG.md#data-processing) | 结构化数据的匹配、清洗、转换、分析与质量核验。 | [`match-tabular-records`](match-tabular-records/SKILL.md) |
| [产品研发](CATALOG.md#product-engineering) | 产品定义、研发执行、质量控制、交付与运营流程。 | [`run-web-product-workflow`](run-web-product-workflow/SKILL.md) |
<!-- catalog-summary:end -->

完整清单、分类规则与参考来源见 [`CATALOG.md`](CATALOG.md)。

## 更新分类

分类的唯一配置源是 [`catalog/taxonomy.json`](catalog/taxonomy.json)。新增 skill 后：

1. 在仓库根目录新增 `<skill-name>/SKILL.md`。
2. 将 skill 名称加入 `catalog/taxonomy.json` 的一个分类节点。
3. 运行 `python scripts/update_catalog.py` 更新 README 摘要与 `CATALOG.md`。
4. 运行 `python scripts/update_catalog.py --check` 检查遗漏、重复归类和目录漂移。

一级分类上限固定为两个。某个领域出现多个稳定主题时，在对应分类的 `children` 中增加子分类；禁止为了单个 skill 提前创建子分类。CI 会检查目录是否与配置及仓库内容一致。

## 参考仓库

- [Anthropic Skills](https://github.com/anthropics/skills#skill-sets)：按 Creative & Design、Development & Technical、Enterprise & Communication、Document Skills 等用途域展示 skill。
- [Microsoft Skills](https://github.com/microsoft/skills#adding-new-skills)：使用一级目录与领域子分类组织大规模 skill 清单，同时将分类导航与 skill 的规范目录分离。
- [NVIDIA Skills](https://github.com/NVIDIA/skills#skill-catalog)：按产品域维护目录，并通过自动同步支持持续新增和更新。
