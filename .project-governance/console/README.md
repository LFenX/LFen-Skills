# 治理控制台

本项目自己的只读治理控制台。启动器就在本目录，它从自身位置推断项目根，**不需要任何路径参数**：

```
python .project-governance/console/console.py start
```

`start` 会选一个空闲端口、后台运行并打开浏览器。另有 `status`（是否在运行、地址）、`open`（重新打开）、`stop`（停止）、`verify`（核对快照与装配记录）。

## 为什么控制台在项目里

控制台由 `run-governed-product-workflow` 在建立本项目治理目录时装配。skill 里的那一份是**模板**；能跑的这一份属于本项目。

`snapshot/` 是逐字节固定的代码快照。skill 升级、卸载或换机器都不改变这台控制台的行为——它多年后仍能按当时的样子重建。`deployment.json` 记录来源、版本、装配时间和每个快照文件的 SHA-256，改动可检出。

## 页面

| 页面 | 内容 |
|---|---|
| 总览 | 任务、衍生、未决、文档、完整性六域摘要 |
| 任务 | 主任务列表；衍生任务收在主任务下，展开可见，主任务带子树审计数 |
| 任务详情 | 用户原话、分类、裁剪结果、产物清单、允许路径、验收、执行事件、成立事实、血缘 |
| 血缘与衍生 | 按受控关系分类的衍生审计：谁引入了返工，谁顺带发现了问题 |
| 未决项 | 遗留问题与各自的重入条件 |
| 项目文档 / 待分类 / 迁移归档 | `LG_project_docs/` 的布局与登记审计，含非本 skill 产生的资产 |
| 产物结构 | 六类受控产物各自的用途与落盘位置 |
| 生成物 | `generated/` 下的检索上下文、审计报告、评审视图、查询请求 |
| 完整性与审计 | skill 受保护资产的哈希核对 + 项目文档域审计发现 |

## 数据来源，以及零的含义

- **文档、生成物、完整性**：每次请求实时扫描，看到的就是当下磁盘上的样子。
- **任务、血缘**：来自 `project-state.json` 快照。任务记录在快照之后被改动时，页面顶部会告警并点名是哪些文件——此时先重建 ProjectState 再据此下结论。
- **完整性页**：它核对的是 **skill** 的受保护资产，不是项目的。skill 不可达时该页显示「**无法核对**」而不是「全部一致」——**零在这里意味着没有核对，不是没有问题**。其余页面只读项目自身文件，不受影响。

要在 skill 移动或重装后恢复核对，设置环境变量 `LG_SKILL_ROOT` 指向 skill 根，或更新 `deployment.json` 里的 `skill_root`。

## 边界

控制台**只读**，只服务 `127.0.0.1`，只接受 `GET`/`HEAD`，每个被请求的路径解析后必须落在 `.project-governance/` 或 `LG_project_docs/` 之内。它从不写入任何治理记录。

按 C10 §8.0，DerivedView 不得作为跟踪事实的唯一来源：这里看到的一切都可以在上述两个目录的原始文件中核对，控制台只是视图。

## 装配记录

<!-- LG-MANAGED:START -->
- 装配时间：`2026-09-05T07:39:49Z`
- 来源 skill：`run-governed-product-workflow` 版本 `6.3.0-candidate`
- 装配时的 skill 路径：`D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow`
- 快照文件：9 个，哈希记录于 `deployment.json`
- 核对快照是否被改动：`python .project-governance/console/console.py verify`
<!-- LG-MANAGED:END -->

标记区由工具更新；标记外内容可由项目维护者补充。
