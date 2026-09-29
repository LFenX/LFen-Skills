# 安装命令选择区与下载失败状态

- 变更时间：2026-09-29 15:22（UTC+8）。
- 用户原话：「这个命令是不是有问题，另外，要给出安装每一个skill的命令，通过按钮切换」。
- 用户确认：在 GitHub README 使用折叠按钮；每个 skill 展示全部 7 个平台的完整命令。
- 涉及文件：`README.md`、`README.en.md`、`SKILLS.md`、`SKILLS.en.md`、`scripts/update_catalog.py`、`install.sh`、本日志。
- 原因：现有单项安装示例仅展示一个 skill；长代码块在 GitHub 横向滚动，末尾参数不易看到。Bash 的 `curl | bash` 在下载失败时可返回 0。

## PRD：README 安装命令选择区

- 目标用户：从 GitHub README 复制命令安装 LFen skill 的 Windows、macOS 与 Linux 用户。
- 页面结构：安装章节保留交互式入口；单项安装区按 skill 展开，再按目标平台展开；每个平台显示 Windows PowerShell 和 macOS/Linux Bash 两段完整命令。
- 交互：点击 skill 或平台的折叠标题显示相应命令；代码块由 GitHub 提供复制按钮。每次最多展开一个 skill 和该 skill 内的一个平台。
- 约束：GitHub README 不运行自定义 JavaScript；技能清单从仓库现有目录生成；命令显式指定平台及 skill；不新增网页或改变目录结构。
- 验收：8 个现有 skill 各有 7 平台的两种系统命令；新增 skill 后目录生成脚本能同步命令；PowerShell 与 Bash 命令可解析并正确传参；Bash 下载失败返回非零；中英文 README 一致，目录检查通过。
- GitHub 折叠区与代码块依据：[GitHub Docs：Organizing information with collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)；README HTML 清洗依据：[github/markup](https://github.com/github/markup)。

## 变更与验证

- `scripts/update_catalog.py` 从现有 skill 目录生成中英文 README 的双层折叠区，并同步 README 与 SKILLS 四页的技能数量徽章；8 个 skill × 7 个平台 × 2 个系统，共每份 README 112 段命令。新增 skill 后运行生成器即可加入新按钮，`--check` 会检测漂移。
- PowerShell 下载和调用写为同一表达式，分行展示，避免代码块横向裁切，也避免下载失败后调用旧变量。Bash 命令增加外层 `pipefail`；`install.sh` 内的远程用法和无终端提示同步修正。
- Windows：`python -m unittest discover -s scripts -p 'test_*.py'`，27 项中 26 项通过、1 项按平台跳过，退出码 0。WSL Ubuntu：同一命令，27 项中 20 项通过、7 项按平台跳过，退出码 0。
- `python scripts/update_catalog.py --check`、Git Bash `bash -n install.sh`、`git diff --check` 均通过。
- 对两份 README 的生成区分别解析 56 段 PowerShell 命令和 56 段 Bash 命令：PowerShell AST 与 `bash -n` 全部通过。
- GitHub Markdown 渲染 API 分别返回 HTTP 200；两份 README 均渲染出 8 个 skill 折叠按钮、56 个平台折叠按钮和 112 个代码块，且保留分组 `name` 属性。
- 隔离下载失败验证：生成的 PowerShell 命令在 Windows PowerShell 5.1 返回 1，生成的 Bash 命令在 Git Bash 返回 37；GNU Bash 3.2 的 `-o pipefail` 可用。未在 macOS 原生系统执行，也未逐一执行全部 56 个安装组合。
- 独立复核从生成区抽取 Codex 命令，只将 skill 名改为隔离仓的 `demo`：PowerShell 在线 `irm` 命令与 Bash 本地 `file://` 命令均返回 0，在临时 HOME 生成 Codex 安装链接。
