# 安装器修复与单项安装命令

- 变更时间：2026-09-29 14:51（UTC+8）。
- 涉及文件：`install.ps1`、`install.sh`、`README.md`、`README.en.md`、`scripts/test_installers.py`、`.github/workflows/catalog.yml`、本日志。
- 变更原因：修复已确认的安装入口与安装器缺陷，并提供无需菜单、显式指定目标平台的单个 skill 安装命令。
- 变更摘要：Windows 在线命令添加 `-UseBasicParsing`；PowerShell 安装器增加 `-Skill NAME`，Git 克隆或更新失败时中止；Shell 安装器增加 `--skill NAME`，管道交互从控制终端读取选项，无终端且未提供选择时清晰报错；Shell 目录数据结构兼容 Bash 3.2；已有非 Git 的 `~/.lfenskills` 不再删除；克隆、更新或链接失败不再报告成功，同名真实目录挡住单项安装时也返回失败。单项参数仅供安装，搭配更新或状态模式时提前拒绝，防止修改其他 skill 链接。中英文 README 给出 Codex 的单项安装示例并说明状态命令仍按全量清单检查。CI 添加安装器隔离测试，Windows 与 Ubuntu 分别运行。

## 验证

- Windows：`python -m unittest discover -s scripts -p 'test_*.py' -v`，27 项中 26 项通过、1 项 POSIX PTY 测试因平台不适用跳过，退出码 0。
- WSL Ubuntu：同一测试命令，27 项中 20 项通过、7 项 Windows PowerShell 测试因平台不适用跳过，退出码 0。
- 使用 GNU Bash 3.2.0 在 WSL 隔离 HOME、本地 Git 仓库下实测：`bash -n`、管道单项安装、PTY 菜单安装、`--status`、`--update --all-skills` 均按预期执行。未在 macOS 原生系统验证。
- Git Bash `bash -n install.sh`、PowerShell AST 解析 `install.ps1`、`python scripts/update_catalog.py --check`、`git diff --check`：全部通过。
- PowerShell 在线入口的 `iwr -UseBasicParsing` 已在本机 Windows PowerShell 5.1 对 README 指定 URL 做只读获取验证（HTTP 200）；未执行远端旧版本脚本。在线一行安装示例需在本次改动发布到 `main` 后才会获取新版安装器。
- 单项安装后 `-Status` / `--status` 仍按全量 catalog 报告其他 skill 缺失；该既有规则已在 README 明示，本任务未修改状态定义。
