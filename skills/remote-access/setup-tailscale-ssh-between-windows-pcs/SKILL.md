---
name: setup-tailscale-ssh-between-windows-pcs
description: "在已登录同一 Tailscale 账号的 Windows 电脑之间，只经 Tailscale 内网用 SSH 密钥互登，并准备 PuTTY 可用的 .ppk。覆盖 OpenSSH Server、只监听 Tailscale 地址、防火墙限于 100.64.0.0/10、管理员公钥位置、双向验证，以及用 Python 把 OpenSSH ed25519 私钥转为 PPK v2。不用于公网暴露 SSH，也不用于 UU 远程或 ToDesk 等远程桌面。"
metadata:
  description_en: "Set up SSH-key login between Windows PCs that already share one Tailscale account, using only the Tailscale network, and prepare a PuTTY .ppk. Covers OpenSSH Server, listening only on the Tailscale address, limiting the firewall to 100.64.0.0/10, administrator public-key placement, checks in both directions, and converting an OpenSSH ed25519 private key to PPK v2 with Python. Does not cover exposing SSH to the public internet or remote-desktop tools such as UU Remote or ToDesk."
---

# 两台 Windows 经 Tailscale 内网 SSH 互登

两台（或多台）Windows 电脑已经登录同一个 Tailscale 账号时，只通过 Tailscale 内网用 SSH 密钥互相登录，并让 OpenSSH 与 PuTTY 都能连上。地址、用户名和密钥路径一律用本机查询结果，下文尖括号是占位符。

标了「标准 Windows 用法，未在本次环境实测」「标准用法，未在本次环境实测」「标准行为，未在本次环境实测」或「已知行为，未在本次环境实测」的句子，不是本次环境的实测结论。

## 适用与不适用

适用：两边 `tailscale status` 能看到对方，需要用 SSH 密钥从 Tailscale 地址 `100.x.x.x` 互登，并在需要时使用 PuTTY / plink。

不适用：把 SSH 暴露到公网；使用 UU 远程、ToDesk 或其他远程桌面。

## 前提

- 两台都安装了 Tailscale 并且在线。`tailscale status` 能看到对方，记下对方的 `100.x.x.x` 地址。
- 两边都有管理员权限。安装 OpenSSH Server、改防火墙、写 `sshd_config` 需要管理员权限。下面的安装、防火墙和重启 `sshd` 都在管理员 PowerShell 里执行。
- 先核对两边实际登录的 Windows 用户名，不要假设相同。家里机用户名与工作机用户名可能不同。用 `whoami` 核对，登录时使用 `<对方用户名>`。
- 本 skill 的转换脚本只接受无口令的 OpenSSH ed25519 私钥。现有密钥是 RSA（如 `id_rsa`）或带口令时，不要用脚本。改用 PuTTYgen 图形界面 Load/Save，或按下面的非交互命令新生成一对 ed25519。
- `sshd` 只监听 Tailscale 地址时，开机时如果 Tailscale 还没起来，`sshd` 可能绑定失败。遇到这种情况，在 Tailscale 上线后执行 `Restart-Service sshd`。已知行为，未在本次环境实测。

## 完整配置流程

每台需要被登录的机器都做 1–4。第 5 步在每台生成密钥后，只把公钥交给对方。验证命令对每个方向各做一次。只验证一个方向不算完成。

1. 安装并启动 OpenSSH Server。先检查服务是否已在：

```powershell
Get-Service sshd
```

找不到服务就是未安装，执行下面三条。已经列得出 `sshd` 时，跳过 `Add-WindowsCapability`；启动类型不是 Automatic 或状态不是 Running 时，仍执行 `Set-Service` 和 `Start-Service`。这条判断是标准 Windows 用法，未在本次环境实测。

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service sshd -StartupType Automatic
Start-Service sshd
```

以上安装命令是标准 Windows 用法，未在本次环境实测。服务名是 `sshd`，启动类型为自动。

2. 编辑 `C:\ProgramData\ssh\sshd_config` 前先备份。本机 Tailscale IPv4 用：

```powershell
tailscale ip -4
```

`tailscale ip -4` 是标准 Windows 用法，未在本次环境实测。把查到的地址写入 `ListenAddress <本机 Tailscale IP>`。只监听 Tailscale 地址，不监听 `0.0.0.0`。同时设置 `PubkeyAuthentication yes` 和 `PasswordAuthentication no`。

已存在的 `ListenAddress`、`PasswordAuthentication` 行要就地改，不要重复追加。`Match Group administrators` 块必须在文件最末尾，其它全局指令必须写在它之前。文件末尾保留：

```text
Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

3. 改完先校验，通过后再重启，然后确认监听地址：

```powershell
& "$env:WINDIR\System32\OpenSSH\sshd.exe" -t
Restart-Service sshd
Get-NetTCPConnection -LocalPort 22
```

`sshd.exe -t` 与 `Restart-Service sshd` 是标准 Windows 用法，未在本次环境实测。`Get-NetTCPConnection` 的结果应只在 `<本机 Tailscale IP>` 上 Listen。

4. 防火墙只放行来自 Tailscale 网段 `100.64.0.0/10` 的 TCP 22，并禁用默认的任意来源放行 22。先列出现有规则，再禁用 `OpenSSH-Server-In-TCP`，然后新建规则：

```powershell
Get-NetFirewallRule -DisplayName '*OpenSSH*'
Disable-NetFirewallRule -Name OpenSSH-Server-In-TCP
New-NetFirewallRule -DisplayName 'SSH from Tailscale only' -Direction Inbound -Protocol TCP -LocalPort 22 -RemoteAddress 100.64.0.0/10 -Action Allow
```

以上防火墙命令是标准 Windows 用法，未在本次环境实测。

5. 每台生成密钥。生成必须非交互，否则会停在口令提示。已有密钥时不要覆盖，先检查：

```powershell
Test-Path <私钥路径>
```

结果为 `True` 时不要再运行 `ssh-keygen`。结果为 `False` 时，在 Windows PowerShell 5.1 执行：

```powershell
ssh-keygen -t ed25519 -f <私钥路径> -N '""'
```

PowerShell 5.1 下空口令要写成 `'""'`。PowerShell 7 下是 `ssh-keygen -t ed25519 -f <私钥路径> -N ""`。PowerShell 7 的这条写法未在本次环境实测。

只把公钥交给对方。公钥内容要从对方机器的 `.pub` 文件读取后写入本机。不要在聊天中粘贴公钥以外的任何密钥材料。

公钥放在哪里，取决于对方账号是否属于管理员组：

- 管理员组账号：写入 `C:\ProgramData\ssh\administrators_authorized_keys`。
- 普通账号：写入 `%USERPROFILE%\.ssh\authorized_keys`。

普通 `.ssh\authorized_keys` 对管理员组账号无效。这是最常见的 `Permission denied (publickey)` 原因。

Windows PowerShell 5.1 的 `>` / `>>` 会把文件写成 UTF-16，sshd 无法解析。用：

```powershell
Add-Content -Path <文件> -Value '<公钥一行>' -Encoding ascii
```

写完检查每个公钥独占一行、文件末尾有换行。这是标准用法，未在本次环境实测。

管理员组账号的 `icacls` 必须在写入之后执行：

```text
icacls <文件> /inheritance:r
icacls <文件> /grant "SYSTEM:(F)" "Administrators:(F)"
icacls <文件>
```

最后一条是检查。结果只应有 SYSTEM 和 `BUILTIN\Administrators`。这条预期输出是标准 Windows 用法，未在本次环境实测。

## 验证命令

每个方向都做。`<对方 Tailscale IP>` 使用 `tailscale status` 里看到的地址，`<对方用户名>` 使用对方机器上 `whoami` 的结果。

`ssh -i` 的 `<私钥路径>` 必须是发起连接的那台机器上的私钥。这对密钥的公钥要在目标机器的授权文件里。不要拿目标机器的密钥路径。

```powershell
Test-NetConnection <对方 Tailscale IP> -Port 22
ssh -i <私钥路径> -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new <对方用户名>@<对方 Tailscale IP> "echo OK"
```

`Test-NetConnection` 的 `TcpTestSucceeded` 应为 `True`。`ssh` 应输出 `OK`。

需要 PuTTY 时，先有 `.ppk`。必须先用 `plink -batch` 验证，成功后再开 `putty.exe`：

```text
plink -batch -ssh <对方用户名>@<对方 Tailscale IP> -i <key.ppk> "echo OK"
putty.exe -ssh <对方用户名>@<对方 Tailscale IP> -i <key.ppk>
```

`plink` 应输出 `OK`。`plink` 第一次连接、主机密钥尚未缓存时，`-batch` 会拒绝。先用 `ssh` 或 `putty` 连一次并接受主机密钥，再重跑 `plink -batch`。标准行为，未在本次环境实测。

无论 PuTTY 是否可用，保底是再开一个窗口。这里的 `<私钥路径>` 同样是发起连接那台机器上的私钥：

```text
cmd /k ssh -i <私钥路径> <对方用户名>@<对方 Tailscale IP>
```

## 验收标准

两个方向都要通过，只验证一个方向不算完成。已在真机验证过的两个方向是：家里机用管理员账户登录工作机的管理员账户；工作机用 ed25519 密钥登录家里机（`ssh` 与 `plink` + `.ppk`）。

## PuTTY 与 .ppk 转换

用 `Get-Command putty` 定位 `putty`、`plink` 和 `puttygen`，不要只查 `C:\Program Files`。实测安装位置和 Python 兜底的验证结果只写在「实测环境」。

推荐：打开 PuTTYgen 图形界面，Load 时把文件类型选为 All Files，选中 OpenSSH 私钥，再 Save private key，存成 `.ppk`。

Windows 上的 PuTTYgen 是图形程序，不支持 `-O private -o` 这类命令行参数，会弹窗 `unrecognised option '-O'`。在非交互 shell 里启动还会挂住，需要手动结束进程。不要用 SendKeys 模拟按键操作 PuTTYgen：实测保存动作未必生效，目标文件可能仍是之前手写的旧文件。

图形界面不能用，且私钥是无口令 OpenSSH ed25519 时，在本 skill 目录用 Python 3 和 `cryptography` 转换。RSA 或有口令的私钥不要用脚本。依赖：

```text
python -m pip install cryptography
```

转换命令只接受本机文件路径，不接受把私钥贴进参数：

```text
python scripts/openssh_ed25519_to_ppk.py --private-key <私钥路径> --output <key.ppk>
```

脚本是 [scripts/openssh_ed25519_to_ppk.py](scripts/openssh_ed25519_to_ppk.py)。它只写 `.ppk` 文件；标准输出不打印私钥、seed、公钥或 `.ppk` 正文。默认注释是 `openssh-ed25519`，不从私钥文件抄注释，且只接受单行 ASCII。输出文件已存在时不覆盖，除非加上 `--force`。

已实测可用的 PPK v2 编码：

- 公钥块 = `ssh_string("ssh-ed25519") + ssh_string(32字节公钥)`
- 私钥块 = `ssh_string(32字节 seed)`（只有 seed，带 4 字节长度前缀）
- MAC = HMAC-SHA1。密钥为 `sha1("putty-private-key-file-mac-key")`。数据为 `ssh_string(算法名) + ssh_string("none") + ssh_string(注释) + ssh_string(公钥块) + ssh_string(私钥块)`
- 文件头 `PuTTY-User-Key-File-2: ssh-ed25519`，`Encryption: none`。Public-Lines / Private-Lines 为 base64，按 64 字符换行。

```text
python scripts/openssh_ed25519_to_ppk.py --self-test
```

转换得到 `.ppk` 后，必须先用上一节的 `plink -batch` 验证，再开 `putty.exe`。

## 失败经验

下表里，标了「推测」或「未逐项核实」的原因不能写成已确认根因。最后一行是 PuTTY 打不开时的排查顺序，不是已确认的单一原因。

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `Permission denied (publickey,keyboard-interactive)` | 两边实际登录的 Windows 用户名不同（家里机用户名与工作机用户名可能不同）；另外管理员组账号的公钥必须写进 `administrators_authorized_keys` | 先 `whoami` 确认用户名；管理员组账号写 `administrators_authorized_keys` |
| `Host key verification failed` | 推测：known_hosts 里已有该 IP 的旧主机密钥（未逐项核实） | `ssh-keygen -R <对方 Tailscale IP>` 或加 `-o StrictHostKeyChecking=accept-new` |
| 读 `administrators_authorized_keys` 报「访问被拒绝」 | 文件 ACL 只允许 SYSTEM/Administrators，普通会话读不到 | 用提升权限的 PowerShell 读写，不要放宽 ACL |
| `plink: unknown option "-o"` | plink 不支持 OpenSSH 的 `-o` | 用 `-batch -i <key.ppk>`；超时用 shell 层控制 |
| PuTTYgen 弹 `unrecognised option '-O'` | 图形版无命令行转换 | 用图形界面手动 Load/Save，或 Python 兜底 |
| `Unable to load private key (MAC failed)` | 手写 PPK 的 MAC 计算或文件内容不对（具体哪一项未逐项核实） | 直接用本 skill 的转换脚本，不要再手写 |
| `Server refused public-key signature despite accepting key!` | 私钥块编码不对：试过原始 64 字节（seed+公钥）、原始 32 字节、公钥+seed、mpint 小端/大端均失败 | 私钥块必须是 `ssh_string(seed)`，改后 plink 返回 OK |
| 通过「指定电脑」Shell 传脚本时 PowerShell 的 `$变量` 被吞掉 | 内联命令经过多层转义 | 把脚本写成 `.ps1` / `.py` 文件再执行，不要内联复杂脚本 |
| 家里机用户说 PuTTY「打不开/没成功」 | 尚未区分密钥格式、用户名和网络 | 先用 `ssh` 或 `plink -batch` 在终端判断是密钥格式、用户名还是网络问题，再开 GUI |

## 实测环境

- Windows 10/11 两台。OpenSSH Server 随系统提供。
- PuTTY 安装在非默认目录（如 `D:\PuTTY`）。用 `Get-Command putty` 先定位，不要只查 `C:\Program Files`。
- PuTTYgen 无法做命令行转换之后，Python 3 + `cryptography` 兜底已在真实环境验证：plink 输出 `OK`，并成功启动 PuTTY 窗口。
- 转换脚本已在 Windows 真机端到端验证：`--self-test` 通过；转换真实无口令 ed25519 私钥后，plink 登录成功。

## 安全约束

- 不在聊天或日志里输出私钥、token；只传公钥。命令、截图和提交里也不放私钥或 `.ppk` 正文。
- `sshd` 只监听 Tailscale 地址，防火墙只放行 `100.64.0.0/10` 的 TCP 22。禁用密码登录。
- 不修改或停止对方机器上正在线上运行的服务；只改 SSH 相关配置。
- 改 `sshd_config` 前先备份。改后用 `& "$env:WINDIR\System32\OpenSSH\sshd.exe" -t` 校验，再 `Restart-Service sshd`。
