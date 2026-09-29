# 安装命令审查

- 审查时间：2026-09-29 14:27（UTC+8）。
- 涉及文件：`install.ps1`、`install.sh`、`README.md`、`README.en.md`、`scripts/test_check_install_links.py`、`.project-governance/tasks/T-INSTALL-20260914-005/after.json`、本日志。
- 摘要：只审查安装命令和安装器行为，未修改安装器。确认 Windows 一行安装命令在当前 PowerShell 5.1 环境中因 `Invoke-WebRequest` 默认解析而报错；`curl | bash` 的脚本标准输入与菜单输入冲突；PowerShell 克隆更新失败仍报告安装完成。复核两项既有遗留问题：macOS 自带 Bash 3.2 不支持脚本使用的关联数组；`~/.lfenskills` 是非 Git 目录时，Shell 安装器会递归删除该目录。
- 原因：用户要求核查 skill 项目的安装命令是否存在 bug。

## 验证

- `python -m unittest scripts/test_check_install_links.py -v`：10/10 通过；这些测试不执行 README 的在线一行命令。
- `bash -n install.sh`：通过。PowerShell AST 解析 `install.ps1`：通过。
- Windows PowerShell 5.1 下，`Invoke-WebRequest` 获取 README 指定 URL：报 `System.NullReferenceException`，调用栈位于 `PromptForChoice`；添加 `-UseBasicParsing` 后 HTTP 200。微软文档说明安全更新后默认解析会要求确认，避免确认需使用 `-UseBasicParsing`：[Invoke-WebRequest 文档](https://learn.microsoft.com/en-us/powershell/module/Microsoft.PowerShell.Utility/Invoke-WebRequest?view=powershell-5.1)。未执行远端脚本。
- 在隔离的临时 HOME 和本地 Git 远端下，把 `install.sh` 内容经标准输入送入 Bash：菜单出现后进入 `Invalid choice, exiting.`，退出码 1；未建立安装链接。直接文件执行路径未以此场景复测。
- 在隔离的临时 USERPROFILE 中建立有提交但无上游分支的 Git 克隆；`git pull` 退出码 1，而 `install.ps1 -Codex -AllSkills` 建立链接、打印 `Done` 并退出 0。
- macOS 未做活体验证；Apple 开发者论坛的官方示例显示系统 Bash 3.2：[Apple 资料](https://developer.apple.com/forums/tags/xcselect)。脚本第 19、90、269 行使用 `declare -A`，其关联数组语法见 [GNU Bash 手册](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)。此前任务的 `after.json` 已将 Bash 版本和非 Git 目录删除列为遗留问题。
- 当前工作区安装器与 README 未修改；未运行真实安装或更新。
- 临时复现目录的递归清理命令被执行策略拒绝；两份隔离数据仍留在系统 `%TEMP%` 的 `lfen-installer-audit-d2e460a52d1e40c6a7cb76f32370870c` 与 `lfen-bash-audit-6efb2616b5014c6eb31cc474a2edb93a`，未触及用户现有安装目录。
