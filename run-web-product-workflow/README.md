# run-web-product-workflow

按团队 V6.3 规范推进 Web 产品与工程变化的生产流程 Skill：同一六元模型，在 Minimal 与完整载体之间裁剪，并维护需求、计划、执行、验证、验收、发布和证据。

本文件面向**人**：消费者如何接入、维护者如何发布。Agent 的执行契约只有一份权威定义，在 [`SKILL.md`](SKILL.md)，本文件不复述。

| 项 | 值 |
|---|---|
| 版本 | `6.3.0-candidate` |
| 发布 tag | `rwpw-v6.3.0-candidate` |
| 运行依赖 | Python 3.11+；标准库。仅 `audit_norm_retrieval.py` 需 `jsonschema>=4.18,<5` |
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

无需安装平台插件，无需 Token，本 skill 不调用任何平台绑定接口。

## 两个必须先分清的概念

**`<skill-root>` 不是 `<project-root>`。** 治理脚本永远在 `<skill-root>/scripts/`；治理记录永远写进 `<project-root>/.project-governance/`。工作区若是本 skill 的子目录，项目根通常是上一级 Git 仓。

**`reference/`（无 s）和 `references/`（有 s）是两个不同的目录。** 这是本包最容易踩的坑：

| 目录 | 内容 | 谁读 |
|---|---|---|
| `reference/` | 9 张命令卡（init/clarify/plan/run/verify/close/status/migrate/minimal） | Agent 按路由按需读一张 |
| `references/` | skill 说明：规范源路由图、第一性原理、项目文档布局 | Agent 在完整载体前读 |
| `assets/runtime/norms/` | 规范正文快照 | **不直读**，只能过 `get_context.py` 检索 |

规范的逻辑路径写作 `references/01_治理基线/...`，但那是 Manifest 里的逻辑标识，**不是 skill 根下的可打开文件**，磁盘位置在 `assets/runtime/norms/`。递归读取 norms 目录是被明确禁止的——那会一次性烧掉几万行上下文，也正是本 skill 的检索层要解决的问题。

## 目录结构

```
SKILL.md                     Agent 入口，126 行，self-test 硬卡 < 200 行
reference/                   命令卡，每张 22-46 行
references/                  skill 说明（路由图 / 第一性原理 / 文档布局）
scripts/                     19 个治理脚本
assets/runtime/norms/        规范正文快照（22 份）
assets/runtime/schemas/      产物 JSON Schema（11 份）
assets/runtime/mappings/     裁剪适用性与 Profile 映射
assets/runtime/evaluations/  检索评测 gold set 与预算基线
assets/runtime/embedded-manifest.json   44 个受保护文件的 SHA-256
assets/project-templates/    消费项目的 README 模板
agents/openai.yaml           Codex 侧 skill 元数据
```

## 维护者门禁

发布前必须全绿。CI（`.github/workflows/skill-gates.yml`）在每次改动本 skill 时自动执行同样两条：

```bash
python run-web-product-workflow/scripts/self_test.py --project-root .
```

189 条正反向断言，覆盖入口结构、frontmatter、命令卡完整性、文档治理、消费方引导、Minimal 载体单向升级、缓存回收与写入守卫。

```bash
python run-web-product-workflow/scripts/audit_norm_retrieval.py --validate-only --runtime-only
```

校验受保护的检索契约：28 个 gold case、41 条 REQ / 25 条 AC 覆盖、8 个 hard gate、12 项结构检查，以及 taxonomy 与 gold set 的哈希。

### 已知门禁缺陷

`audit_norm_consistency.py --runtime-only` **目前必然返回 exit 3**：runtime-only 模式仍会去读 `.project-governance/tasks/RUNTIME-ONLY/before.json`，而该文件按定义不存在，因而恒定产生一条 `task_contract_snapshot_missing` Blocker。SKILL.md「维护入口」把它列为消费项目审计命令，实际不可用。修复涉及门禁语义变更，需要人决定控制目标，**未纳入 CI**。带真实 `--task-id` 运行不受此影响。

## 修订内置规范

本包是规范正文的**唯一编辑事实源**，不镜像任何外部规范仓库。直接修订 `assets/runtime/norms/` 下的正文，然后就地重封 Manifest：

```bash
python run-web-product-workflow/scripts/sync_embedded_references.py
```

该命令重算全部受保护资产的 SHA-256 并重写 `embedded-manifest.json`，不读取任何外部目录。重封后重跑上面两条门禁，再提交并打新 tag。禁止手工编辑登记哈希——写入守卫会拒绝。

## 发布信任根

`embedded-manifest.json` 只证明包内受保护文件与登记哈希一致，**不证明来源可信**。信任根是本 skill 所在的 Git 提交，发布时用 annotated tag 标记（`rwpw-v6.3.0-candidate`）。签名与仓库访问策略由维护者本地流程管理，本 skill 不要求 Agent 自建 GPG 或 PKI。

## 边界

会做：发现上下文、分类、起草、维护追踪、生成派生视图、运行检查、报告缺口。

不会做：替人确认目标与验收、替人取舍范围、替人批准、替人发布、替人接受剩余风险、替人过最终 Gate。工具成功、聊天回复、沉默或 Ask 点击都不等于批准。
