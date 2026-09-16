---
name: record-skill-incident
description: "把已确认的 Agent Skill 问题整理成 JSON：可核对观察与推理原因必须分开。落盘默认写到 D:/skill_problem/<skill-name>/，没有 skill_problem 或该 skill 目录时先创建。创建实际文档前必须向人征求是否落盘和文件名。用于讨论 skill 规范缺失、模型未执行规范、门禁只申报不走、复查用派生物自验，并且人已经确认问题属实、要求留档的时候。未征求意见不得写文件；不得把推理写成事实。"
description_en: "Record a confirmed Agent Skill incident as JSON, keeping verifiable observations separate from inferred causes. Default storage is D:/skill_problem/<skill-name>/; create skill_problem or the skill folder if missing. Ask the human before creating any file or choosing a filename. Use when discussing skill-spec gaps, models not following a skill, gates that were declared but not passed, or reviews that checked derived criteria instead of source text, after the human has confirmed the problem and wants a record. Do not write a file without consent. Do not present inferences as facts."
---

# 记录 Skill 问题

讨论并确认某个 Agent Skill 出了问题后，按固定 JSON 把前因后果留下。观察是观察，推理是推理。**落盘必须先问人。**

本 skill 只负责这件事。不负责改被讨论的那个 skill，也不负责推进产品需求。

## 何时使用

人在讨论 skill 本身，并且已经确认问题属实，要求留档或整理原因时使用。典型说法：

- skill 的规范在，但模型没有执行
- 是 skill 的原因还是模型执行的原因
- 复查全绿却漏了原文
- 门只申报了、没有走过
- 把这次 skill 问题记下来

未确认、只是猜测、或人只要口头分析时，只在对话里说，不进入落盘流程。

## 兼容约定

一份 `SKILL.md` 同时给 Cursor、Claude、OpenCode 和 OpenAI Codex 用。

- 只依赖本文件和同级 [schema.json](schema.json)。Codex 额外读 [agents/openai.yaml](agents/openai.yaml)。
- 不要调用某个编辑器才有的专用工具。征求意见时：有结构化提问工具就用；否则在对话里清楚问。
- 路径一律用正斜杠，例如 `D:/skill_problem/run-governed-product-workflow/`。
- 不要为了某个平台改写 JSON 字段名。

## 工作流程

### 1. 先确认，再整理

同时满足才继续：

1. 人指出了具体 skill 或具体执行过程。
2. 人确认问题属实，或仓库里有可核对证据支持该确认。
3. 人要求整理、留档或写成文件。

缺任一条：只做口头分析，停止。

### 2. 分开观察和推理

从任务账本、skill 原文、代码、测试、矩阵、commit 里收集材料。每条必须能标成下面两类之一：

| 类别 | 含义 | 写法 |
| --- | --- | --- |
| 观察 | 能打开某个文件或记录直接读到 | `observed_facts`，带 `source` |
| 推理 | 由观察推出的原因或机制 | `inferred: true`，并写 `not_a_fact: true` |

禁止把 reading、任务卡、自己写的矩阵当成需求原文。禁止把「模型当时在想什么」写成事实。

一句话里有多个要求，拆开记。原文和派生物打架时，以原文为准。

字段定义见 [schema.json](schema.json)。

### 3. 按 skill 名决定默认目录

默认根目录是 `D:/skill_problem/`。每份记录放进**被讨论、已确认出问题的那个 skill** 的同名文件夹，不要放进 `record-skill-incident` 自己的目录。

```
D:/skill_problem/<skill-name>/<YYYYMMDD>-<short-slug>.json
```

`<skill-name>` 必须等于该 skill 目录名，小写短横线，例如 `run-governed-product-workflow`。

- `D:/skill_problem/` 不存在：先创建这个目录，再写文件。
- `D:/skill_problem/<skill-name>/` 不存在：一并创建。
- 一次讨论涉及多个 skill：问人要以哪个 skill 名为文件夹；未指定就用主要被追责的那个。
- 对不上任何 skill 名：先问人，不得自造产品仓库路径，也不得把文件直接扔在 `D:/skill_problem/` 根下。

**默认不要写进当前产品仓库。** 人指定了别的根目录时，仍按 `<根目录>/<skill-name>/` 组织。

### 4. 落盘前必须问人

整理完成后，**先给出摘要，再提问。未得到明确同意，不得创建、覆盖或移动任何文件。** 创建默认目录本身也算落盘准备，必须在人同意创建这份记录之后才做。

必须问清：

1. 要不要创建这份 JSON 文件？
2. 归到哪个 skill 名的文件夹？默认用上面确认的那个 skill。
3. 文件名叫什么？建议 `{YYYYMMDD}-{short-slug}.json`。

人说「不要」「先不写」「只要看内容」：只把 JSON 贴在对话里，或告诉人可以复制，然后结束。不要提前创建空目录。

人只说「记下来」但没给 skill 名或文件名：仍要问这两项，不得自行写进项目目录，也不得写在 `D:/skill_problem/` 根下。

### 5. 同意之后才写

1. 若 `D:/skill_problem/` 或 `D:/skill_problem/<skill-name>/` 不存在，先创建再写文件。
2. 完整路径为 `D:/skill_problem/<skill-name>/<filename>.json`。编码 UTF-8。
3. 每个推理字段都带 `inferred: true` 和 `not_a_fact: true`。
4. `file_placement` 写入真实的 `skill_name`、`directory`、`path`；`not_in_project` 必须为 true，除非人明确要求写进仓库。
5. 写完后只回报路径，不要把全文再贴一遍，除非人要看。

## 禁止

- 未提问或人未同意就写文件。
- 把推理、信心、反事实写成鉴定结论。
- 默认写进正在开发的产品仓库，或把文件直接放在 `D:/skill_problem/` 根下。
- 改被讨论的那个 skill，或把本记录当成产品验收材料。
- 用任务卡、完成判据或自己写的复查矩阵代替 skill / 需求原文。

## 最小示例

人确认「规范要求从原文复查，模型却用自己写的 R 卡复查」之后，先问是否创建文件、归到哪个 skill 文件夹、文件名。同意后若 `D:/skill_problem/some-skill/` 不存在就创建，再写：

```json
{
  "document_id": "20260916-example",
  "created_at": "2026-09-16T21:58:00+08:00",
  "language": "zh",
  "title": "示例：复查对照了派生物而不是原文",
  "epistemic_rule": {
    "observed_fact": "能在文件里直接读到的内容。",
    "inferred": "由观察推出的原因，不是已证实的事实。"
  },
  "observed_facts": {
    "skill_text": [
      {
        "id": "F-01",
        "source": "some-skill/SKILL.md",
        "text": "复查必须以需求原文为基准，不能用任务卡替代。"
      }
    ],
    "model_execution": [
      {
        "id": "F-02",
        "source": "tasks/T-EXAMPLE/run.jsonl",
        "text": "账本写的是按 R-01 到 R-10 复核，不是按 request_snapshot。"
      }
    ]
  },
  "inferred_causes": [
    {
      "inferred": true,
      "not_a_fact": true,
      "hypothesis": "模型用自己起草的条目验自己写的实现，漏掉的原文要求不会变红。",
      "confidence": "high",
      "basis": ["F-01", "F-02"]
    }
  ],
  "file_placement": {
    "skill_name": "some-skill",
    "directory": "D:/skill_problem/some-skill",
    "path": "D:/skill_problem/some-skill/20260916-example.json",
    "not_in_project": true
  }
}
```
