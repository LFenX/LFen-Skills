# run-web-product-workflow

按团队 V6.3 规范推进 Web 产品与工程变化的生产流程 Skill：同一六元模型，在 Minimal 与完整载体之间裁剪，并维护需求、计划、执行、验证、验收、发布和证据。

本文件面向**人**：消费者如何接入、维护者如何发布。Agent 的执行契约只有一份权威定义，在 [`SKILL.md`](SKILL.md)，本文件不复述。

| 项 | 值 |
|---|---|
| 版本 | `6.3.0-candidate` |
| 发布 tag | `rwpw-v6.3.0-candidate` |
| 运行依赖 | 标准库；仅 `audit_norm_retrieval.py` 需 `jsonschema>=4.18,<5` |
| Python | 3.11 / 3.12 / 3.13。CI 在三个版本上跑完整门禁，自检结果不依赖解释器版本 |
| 规范快照 | 22 份 norm，共约 2.9 万行，受 `embedded-manifest.json` 的 SHA-256 保护 |

## 五分钟跑通

在你的项目里（不是本 skill 目录）：

```bash
mkdir -p .project-governance
```

确认 skill 包完好——这是消费方校验发布快照的唯一入口：

```bash
python <skill-root>/scripts/self_test.py --project-root <project-root>
```

退出码 0 且末尾为 `"positive": "passed"` / `"negative": "passed"` 即可用。之后在 Agent 里直接说要做的事，或用命令词 `init` / `clarify` / `plan` / `run` / `verify` / `close` / `status` / `migrate` / `minimal` 开头。不带参数时走 `status`。

不确定该走 Minimal 还是完整载体时，先筛查——它只问会否决资格的那几条事实，不需要先做完整分类：

```bash
python <skill-root>/scripts/manage_minimal_task.py screen --risk Low --single-scope yes
```

不带 `--fact` 运行会列出需要哪些事实。

无需安装平台插件，无需 Token，本 skill 不调用任何平台绑定接口。

## 两个必须先分清的概念

**`<skill-root>` 不是 `<project-root>`。** 治理脚本永远在 `<skill-root>/scripts/`；治理记录永远写进 `<project-root>/.project-governance/`。工作区若是本 skill 的子目录，项目根通常是上一级 Git 仓。

**`references/` 这个前缀有两种含义。** 命令卡放在 `commands/`，与它无关；真正容易混淆的是 `references/` 既是目录名、又是规范的逻辑命名空间：

| 目录 | 内容 | 谁读 |
|---|---|---|
| `commands/` | 9 张命令卡（init/clarify/plan/run/verify/close/status/migrate/minimal） | Agent 按路由按需读一张 |
| `references/` | skill 说明：规范源路由图、第一性原理、项目文档布局 | Agent 按触发读，见 SKILL.md「读取分层」 |
| `assets/runtime/norms/` | 规范正文快照 | **不直读**，只能过 `get_context.py` 检索 |

Manifest 里以 `references/` 开头的逻辑路径共 25 条，其中 **22 条不是该目录下的文件**——`references/01_治理基线/...` 是逻辑标识，磁盘位置在 `assets/runtime/norms/`，直接打开会失败。只有 3 条是 `references/` 下的真文件。递归读取 norms 目录是被明确禁止的——那会一次性烧掉几万行上下文，也正是本 skill 的检索层要解决的问题。

## 目录结构

```
SKILL.md                     Agent 入口，self-test 硬卡 < 200 行
commands/                    命令卡，按路由读一张
references/                  skill 说明（路由图 / 第一性原理 / 文档布局）
scripts/                     28 个治理脚本
assets/runtime/norms/        规范正文快照（22 份）
assets/runtime/schemas/      产物 JSON Schema（11 份）
assets/runtime/mappings/     裁剪适用性与 Profile 映射
assets/runtime/evaluations/  检索评测 gold set 与预算基线
assets/runtime/embedded-manifest.json   44 个受保护文件的 SHA-256
assets/project-templates/    消费项目的 README 模板
agents/openai.yaml           Codex 侧 skill 元数据
```

## 维护者门禁

发布前必须全绿。CI（`.github/workflows/skill-gates.yml`）在每次推送和 PR 上自动执行同样三条：

```bash
python skills/product-engineering/run-web-product-workflow/scripts/self_test.py --project-root .
```

正反向断言，覆盖入口结构、frontmatter、命令卡与 references 完整性、Minimal 资格投影与 schema 的双向对账、澄清判据、文档治理、消费方引导、Minimal 载体单向升级、缓存回收与写入守卫。

```bash
python skills/product-engineering/run-web-product-workflow/scripts/audit_norm_retrieval.py --validate-only --runtime-only
```

校验受保护的检索契约：28 个 gold case、41 条 REQ / 25 条 AC 覆盖、8 个 hard gate、12 项结构检查，以及 taxonomy 与 gold set 的哈希。

其中 CLI 契约钉的是各脚本 `--help` 的**规范化投影**，不是原文：argparse 的换行位置和 `optional arguments:` / `options:` 标题都随 Python 版本变化，与脚本接受什么命令行无关。参数、metavar、help 文案和描述的任何变化仍然改变摘要。

```bash
python skills/product-engineering/run-web-product-workflow/scripts/audit_norm_consistency.py --project-root . --runtime-only
```

校验 Manifest、内嵌快照与任务来源边界。不带 `--task-id` 时没有可比对的冻结 TaskContract，该项记为 `task_contract_snapshot_not_applicable`（Observation），不构成 Blocker；一旦指定 `--task-id`，缺失或漂移的 TaskContract 仍然是 Blocker 并返回 exit 3。

### 发布信任链

tag 只是标签，除非有东西检查它指向什么。推送 `rwpw-v*` tag 时，CI 在三条门禁全绿之后额外执行一个 release 作业，拒绝与 `SKILL.md` 的 `metadata.version` 不匹配的 tag。因此发布信任根是机器验证的，不是人手写的：

```bash
python .github/scripts/check_release_tag.py rwpw-v6.3.0-candidate
```

### 治理控制台

浏览与审计两个资产目录——`.project-governance` 和 `LG_project_docs`，**包括其中并非本 skill 产生的资产**：

```bash
python skills/product-engineering/run-web-product-workflow/scripts/console.py start --project-root .
```

只读本地服务，绑 `127.0.0.1`，启动后自动打开浏览器。`status` 查看地址、`open` 重新打开、`stop` 停止；端口被占用时自动顺延。

多页面：总览、任务与任务详情、血缘与衍生审计、未决项、项目文档与需求下钻、待分类、迁移归档、生成物、完整性与审计、全局检索、文件预览（Markdown 渲染、JSON、图片、HTML 沙箱）。

每次请求都重新探查目录，不缓存也不需要重新生成。只服务 `GET`/`HEAD`，所有受请求路径必须落在上述两个目录之内，越界一律 403。

### 维护者评测工具

`scripts/audit_norm_shadow.py` 评测 Shadow 检索质量——无关上下文降幅、强制条款覆盖率、错误放行数。它需要真实 task-dir、审批引用和阈值，是维护者评测入口，不是消费方运行时工具，也不在 CI 门禁中。它是本包内最接近「检索效用度量」的资产。

## 修订内置规范

本包是规范正文的**唯一编辑事实源**，不镜像任何外部规范仓库。直接修订 `assets/runtime/norms/` 下的正文，然后就地重封 Manifest：

```bash
python skills/product-engineering/run-web-product-workflow/scripts/sync_embedded_references.py
```

该命令重算全部受保护资产的 SHA-256 并重写 `embedded-manifest.json`，不读取任何外部目录。重封后重跑上面两条门禁，再提交并打新 tag。禁止手工编辑登记哈希——写入守卫会拒绝。

## 发布信任根

`embedded-manifest.json` 只证明包内受保护文件与登记哈希一致，**不证明来源可信**。信任根是本 skill 所在的 Git 提交，发布时用 annotated tag 标记（`rwpw-v6.3.0-candidate`）。签名与仓库访问策略由维护者本地流程管理，本 skill 不要求 Agent 自建 GPG 或 PKI。

## 边界

会做：发现上下文、分类、起草、维护追踪、生成派生视图、运行检查、报告缺口。

不会做：替人确认目标与验收、替人取舍范围、替人批准、替人发布、替人接受剩余风险、替人过最终 Gate。工具成功、聊天回复、沉默或 Ask 点击都不等于批准。
