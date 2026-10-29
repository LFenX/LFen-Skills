# Tailscale SSH skill 审查补命令

- 变更时间：2026-10-29T16:30:08+08:00
- 分支：`cursor/setup-tailscale-ssh-skill-8c21`
- 原始要求：同一分支追加提交，让别的 agent 照着 skill 做不会失败。不改已实测事实。未在本次环境实测的新增内容要标注。只改 `SKILL.md`；转换脚本已在 Windows 真机通过 `--self-test`，并在转换真实密钥后 plink 登录成功，本次不改脚本。

## 变更

- `skills/remote-access/setup-tailscale-ssh-between-windows-pcs/SKILL.md`
  - 安装、`sshd.exe -t`、重启和防火墙改为可复制的管理员 PowerShell。已安装的 `sshd` 不重复安装。
  - `sshd_config` 写明就地修改已有 `ListenAddress` / `PasswordAuthentication`，`Match Group administrators` 必须在文件最末尾。本机 Tailscale IPv4 用 `tailscale ip -4`。
  - 密钥生成改为非交互。PowerShell 5.1 使用 `-N '""'`；PowerShell 7 的 `-N ""` 标为未在本次环境实测。已有私钥用 `Test-Path` 检查，不覆盖。
  - 前提写明脚本只接受无口令 ed25519；RSA 或有口令的密钥改走 PuTTYgen，或新生成 ed25519。
  - 公钥用 `Add-Content -Encoding ascii` 写入，避免 PowerShell 5.1 的 `>` / `>>` 写成 UTF-16。`icacls` 放在写入之后，并检查只剩 SYSTEM 与 `BUILTIN\Administrators`。
  - 验证写明 `ssh -i` 用发起连接那台机器的私钥。验收标准：两个方向都要通过。已记录真机上的两个方向。
  - `.ppk` 必须先 `plink -batch` 再开 `putty.exe`。主机密钥未缓存时 `-batch` 会拒绝，标为标准行为、未在本次环境实测。
  - PuTTY 安装路径和 Python 兜底的实测结果只保留在「实测环境」。
  - `MAC failed` 的处理改为直接用转换脚本。新增 PuTTY「打不开/没成功」时先在终端用 `ssh` 或 `plink -batch` 排查。
  - 前提增加：Tailscale 尚未上线时 `sshd` 可能绑定失败，上线后 `Restart-Service sshd`。标为已知行为、未在本次环境实测。

## 原因

审查指出只写步骤、不给可复制命令时，agent 会卡在安装、防火墙、交互式 `ssh-keygen`、UTF-16 公钥文件和只验证一个方向。这些补丁按审查写进正文；草稿里的实测现象和 PPK 编码没有改写成新的根因。

## 实际验证

- `python scripts/update_catalog.py`：退出码 0。输出仍是 11 个 skill。frontmatter 未改，生成文件相对工作区没有差异。
- `python scripts/update_catalog.py --check`：退出码 0。11 个 skill，7 个一级分类，Markdown 与 JSON 一致。正文最后两句标注补上之后又执行一次，结果相同。
- `python scripts/test_update_catalog.py`：22 项通过，退出码 0。
- `python scripts/test_check_install_links.py`：10 项通过，退出码 0。
- `python scripts/test_installers.py`：17 项中 10 项通过，7 项跳过，退出码 0。跳过原因是本环境不是 Windows。这 7 项不能记为通过。
- `bash -n install.sh`：退出码 0。
- `python scripts/check_install_links.py --no-fetch`：退出码 2。本环境没有 `~/.lfenskills`。不能记为通过。
- `python skills/remote-access/setup-tailscale-ssh-between-windows-pcs/scripts/openssh_ed25519_to_ppk.py --self-test`：退出码 0，输出 `self-test passed`。脚本文件本次没有修改。
- `git diff --check`：退出码 0。最后两句标注补上之后又执行一次，退出码仍为 0。

## 未执行

- 没有在 Windows 上重跑安装、防火墙、`ssh-keygen`、`Add-Content` 或 `plink -batch` 的主机密钥拒绝。这些已在正文标成未在本次环境实测。
- 审查所说的 Windows 真机 `--self-test` 与真实密钥 plink 登录，不是本环境这次执行的结果，只写入「实测环境」。
- 治理工作流 `self_test.py`、两条 norm audit、WakaTime、小红书、表格匹配和 outbox 测试本次没有重跑。本次没有改这些目录，也没有改 skill frontmatter。
