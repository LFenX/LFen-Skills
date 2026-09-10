---
name: match-tabular-records
description: 按单个字段或有序多字段组合键对账两张 CSV/XLSX 表，支持精确、文本、编号、数字、日期、日期时间等可配置归一化。产出 inner join 匹配表、双向不匹配详情、可选的次键补充匹配、重复键与非法键审计、子集统计，以及校验过的格式化 Excel 工作簿。用于跨文件匹配、包含性检查、名单对账、数据覆盖率分析，或按 ID、名称、标题、作者、日期、账号字段、订单号等任意用户指定的键列比对记录。
---

# 表格记录对账

使用内置的确定性脚本比对两份表格导出，不修改任何源文件。

## 工作流程

1. 确认两个源文件路径，并把文件 A 的每个键字段映射到文件 B 中语义等价的键字段。
2. 简单连接用一对键；组合连接用多对有序的键。
3. 为每对键选择归一化模式。除非业务语义要求显式指定，否则用 `auto`。
4. 仅当用户希望在主键未匹配的行中找出疑似等价记录时，才添加可选的次键对。
5. 运行 `scripts/match_tabular_records.py`。
6. 读取 JSON 结果，汇报匹配行数/键数、双向差异、匹配率、重复键/非法键、子集关系和次键匹配情况。
7. 核心匹配完成后，应用被触发的业务输出档案。
8. 有表格渲染工具时，渲染并检查全部四个输出工作表。
9. 独立校验源集合、公式、工作簿结构和视觉布局。
10. 只交付最终校验通过的工作簿。

## 命令

单字段匹配：

```powershell
python scripts/match_tabular_records.py `
  "C:\path\file-a.csv" `
  "C:\path\file-b.xlsx" `
  --left-key "稿件ID" `
  --right-key "作品ID" `
  --key-normalizer id `
  --output "C:\path\字段匹配结果.xlsx"
```

组合键匹配：

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

主键 ID 匹配 + 标题作者补充匹配：

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

## 归一化模式

- `auto`：根据两侧字段名推断；编号类用 `id`，日期类用 `date`，其余用 `text`。
- `id`：归一化编号格式、前导撇号、整数小数、科学计数法、空白字符、Unicode 全半角和大小写。
- `text`：应用 NFKC、移除不可见字符、折叠空白、大小写折叠。
- `number`：去除显示分隔符和尾随零后，按精确十进制值比较。
- `date`：按 `yyyy-mm-dd` 日历日期比较。
- `datetime`：按秒级时间戳比较。
- `exact`：按源标量表示直接比较，不去除空白、不转换大小写。

`--key-normalizer` 可以每对键重复指定一次，也可以只给一次应用到所有键对；`--secondary-normalizer` 同理。

## 必须遵守的语义

- 以有序归一化字段元组作为键；不得把字段拼接成串做内部比较。
- 主键任一组件为空或非法的行不参与匹配。
- 存在重复键时使用笛卡尔积 inner join，并单独汇报重复组。
- 非法键记录保留在对应方向的不匹配详情表中。
- 次键匹配是未匹配行之间的一对一补充判断；绝不并入主 inner join。
- 子集结论基于去重后的合法归一化主键集合。
- 输出中键组件按文本保存，防止科学计数法或精度丢失。
- 字段无法唯一识别时，停下来请求显式映射。

归一化、组合键、重复键、次键配对和输出规则详见 [references/matching-rules.md](references/matching-rules.md)。

## 业务输出档案

### 小红书审核后台 vs 全量提交

当两侧数据链是小红书审核后台数据与全量提交笔记数据、映射键为 `稿件ID = 稿件id`，或用户要求沿用之前/参考的处理样式时，必须读取并应用 [references/xhs-review-output-profile.md](references/xhs-review-output-profile.md)。

该档案是输出契约的必需部分，不是可选的排版建议。它定义了：

- 多轮增量匹配的累计历史 ID 剔除；
- 特定链路的工作表命名和状态取值；
- 动态字段分组、命名和源顺序保留；
- 根据实际表头位置生成的「人工复核优于 Agent」公式；
- 行与分区的排序；
- Excel 颜色、字体、列宽、行高、自动换行、条件格式和冻结窗格；
- 独立的集合、公式、命名、OOXML 和视觉校验。

档案被触发时，不要交付通用的文件 A/文件 B 工作簿，要后处理成档案定义的最终工作簿。把档案当作规则系统而不是冻结的列模板：保留真实源字段、跳过不存在的字段组、绝不为了模仿历史工作簿而添加空白占位列。

## 输出

只创建四个可见工作表：

- `匹配表_inner join`
- `不匹配详情_文件A`
- `不匹配详情_文件B`
- `分析汇总`

脚本会重新打开输出文件，校验 OOXML 完整性、工作表顺序、图形、匹配与不匹配键集合、键的文本存储方式，以及是否存在 Excel 错误。

修改本 Skill 后运行回归测试：

```powershell
python scripts/self_test.py
```
