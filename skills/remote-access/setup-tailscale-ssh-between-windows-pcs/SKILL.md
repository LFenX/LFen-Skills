---
name: setup-tailscale-ssh-between-windows-pcs
description: "在已登录同一 Tailscale 账号的 Windows 电脑之间，只经 Tailscale 内网用 SSH 密钥互登，并准备 PuTTY 可用的 .ppk。覆盖 OpenSSH Server、只监听 Tailscale 地址、防火墙限于 100.64.0.0/10、管理员公钥位置、双向验证，以及用 Python 把 OpenSSH ed25519 私钥转为 PPK v2。不用于公网暴露 SSH，也不用于 UU 远程或 ToDesk 等远程桌面。"
metadata:
  description_en: "Set up SSH-key login between Windows PCs that already share one Tailscale account, using only the Tailscale network, and prepare a PuTTY .ppk. Covers OpenSSH Server, listening only on the Tailscale address, limiting the firewall to 100.64.0.0/10, administrator public-key placement, checks in both directions, and converting an OpenSSH ed25519 private key to PPK v2 with Python. Does not cover exposing SSH to the public internet or remote-desktop tools such as UU Remote or ToDesk."
---

# 两台 Windows 经 Tailscale 内网 SSH 互登

两台（或多台）Windows 电脑已经登录同一个 Tailscale 账号时，只通过 Tailscale 内网用 SSH 密钥互相登录，并让 OpenSSH 与 PuTTY 都能连上。地址、用户名和密钥路径一律用本机查询结果，下文尖括号是占位符。

## 适用与不适用

适用：两边 `tailscale status` 能看到对方，需要用 SSH 密钥从 Tailscale 地址 `100.x.x.x` 互登，并在需要时使用 PuTTY / plink。

不适用：把 SSH 暴露到公网；使用 UU 远程、ToDesk 或其他远程桌面。

## 前提

- 两台都安装了 Tailscale 并且在线。`tailscale status` 能看到对方，记下对方的 `100.x.x.x` 地址。
- 两边都有管理员权限。安装 OpenSSH Server、改防火墙、写 `sshd_config` 需要管理员权限。
- 先核对两边实际登录的 Windows 用户名，不要假设相同。家里机用户名与工作机用户名可能不同。用 `whoami` 核对，登录时使用 `<对方用户名>`。

## 完整配置流程

每台需要被登录的机器都做 1–4。第 5 步在每台生成密钥后，只把公钥交给对方。验证命令对每个方向各做一次。

1. 安装并启动 OpenSSH Server。使用 Windows 可选功能 `OpenSSH.Server`，服务名 `sshd`，启动类型设为自动。
2. 编辑 `C:\ProgramData\ssh\sshd_config` 前先备份。写入：
   - `ListenAddress <本机 Tailscale IP>`。只监听 Tailscale 地址，不监听 `0.0.0.0`。
   - `PubkeyAuthentication yes`
   - `PasswordAuthentication no`
   - 文件末尾保留默认的 `Match Group administrators` 与 `AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys`。
3. 改完先运行 `sshd -t`。校验通过后再重启服务 `sshd`。然后确认监听地址：

```powershell
Get-NetTCPConnection -LocalPort 22
```

结果应只在 `<本机 Tailscale IP>` 上 Listen。

4. 防火墙只放行来自 Tailscale 网段 `100.64.0.0/10` 的 TCP 22。删除或禁用默认的「任意来源放行 22」规则。
5. 每台生成密钥，只把公钥交给对方：

```powershell
ssh-keygen -t ed25519
```

公钥放在哪里，取决于对方账号是否属于管理员组：

- 管理员组账号：写入 `C:\ProgramData\ssh\administrators_authorized_keys`。ACL 只留给 SYSTEM 与 Administrators：

```text
icacls <文件> /inheritance:r
icacls <文件> /grant "SYSTEM:(F)" "Administrators:(F)"
```

- 普通账号：写入 `%USERPROFILE%\.ssh\authorized_keys`。

普通 `.ssh\authorized_keys` 对管理员组账号无效。这是最常见的 `Permission denied (publickey)` 原因。

## 验证命令

每个方向都做。`<对方 Tailscale IP>` 使用 `tailscale status` 里看到的地址，`<对方用户名>` 使用对方机器上 `whoami` 的结果。

```powershell
Test-NetConnection <对方 Tailscale IP> -Port 22
ssh -i <私钥路径> -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new <对方用户名>@<对方 Tailscale IP> "echo OK"
```

`Test-NetConnection` 的 `TcpTestSucceeded` 应为 `True`。`ssh` 应输出 `OK`。

需要 PuTTY 时，先有 `.ppk`，再验证：

```text
plink -batch -ssh <对方用户名>@<对方 Tailscale IP> -i <key.ppk> "echo OK"
putty.exe -ssh <对方用户名>@<对方 Tailscale IP> -i <key.ppk>
```

`plink` 应输出 `OK`。无论 PuTTY 是否可用，保底是再开一个窗口：

```text
cmd /k ssh -i <私钥路径> <对方用户名>@<对方 Tailscale IP>
```

## PuTTY 与 .ppk 转换

实测 PuTTY 安装在非默认目录（如 `D:\PuTTY`）。用 `Get-Command putty` 先定位，不要只查 `C:\Program Files`。`plink` 与 `puttygen` 同样使用实际路径。

推荐：打开 PuTTYgen 图形界面，Load 时把文件类型选为 All Files，选中 OpenSSH 私钥，再 Save private key，存成 `.ppk`。

Windows 上的 PuTTYgen 是图形程序，不支持 `-O private -o` 这类命令行参数，会弹窗 `unrecognised option '-O'`。在非交互 shell 里启动还会挂住，需要手动结束进程。不要用 SendKeys 模拟按键操作 PuTTYgen：实测保存动作未必生效，目标文件可能仍是之前手写的旧文件。

图形界面不能用时，在本 skill 目录用 Python 3 和 `cryptography` 把 OpenSSH ed25519 私钥转成 PPK v2。这条路径已在真实环境验证：plink 输出 `OK`，并成功启动 PuTTY 窗口。依赖：

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

本地只检查编码和 MAC、不保留密钥文件：

```text
python scripts/openssh_ed25519_to_ppk.py --self-test
```

`--self-test` 通过只说明临时密钥的文件结构与 MAC 自洽。它不能代替上文已在真实环境完成的 plink 验证。

## 失败经验

下表是实测现象。标了「推测」的原因没有逐项核实，不能写成已确认根因。

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `Permission denied (publickey,keyboard-interactive)` | 两边实际登录的 Windows 用户名不同（家里机用户名与工作机用户名可能不同）；另外管理员组账号的公钥必须写进 `administrators_authorized_keys` | 先 `whoami` 确认用户名；管理员组账号写 `administrators_authorized_keys` |
| `Host key verification failed` | 推测：known_hosts 里已有该 IP 的旧主机密钥（未逐项核实） | `ssh-keygen -R <对方 Tailscale IP>` 或加 `-o StrictHostKeyChecking=accept-new` |
| 读 `administrators_authorized_keys` 报「访问被拒绝」 | 文件 ACL 只允许 SYSTEM/Administrators，普通会话读不到 | 用提升权限的 PowerShell 读写，不要放宽 ACL |
| `plink: unknown option "-o"` | plink 不支持 OpenSSH 的 `-o` | 用 `-batch -i <key.ppk>`；超时用 shell 层控制 |
| PuTTYgen 弹 `unrecognised option '-O'` | 图形版无命令行转换 | 用图形界面手动 Load/Save，或 Python 兜底 |
| `Unable to load private key (MAC failed)` | 手写 PPK 的 MAC 算法/私钥块编码不对（私钥块当成 64 字节并带长度前缀） | 按上文的 MAC 与私钥块规则重写 |
| `Server refused public-key signature despite accepting key!` | 私钥块编码不对：试过原始 64 字节（seed+公钥）、原始 32 字节、公钥+seed、mpint 小端/大端均失败 | 私钥块必须是 `ssh_string(seed)`，改后 plink 返回 OK |
| 通过「指定电脑」Shell 传脚本时 PowerShell 的 `$变量` 被吞掉 | 内联命令经过多层转义 | 把脚本写成 `.ps1` / `.py` 文件再执行，不要内联复杂脚本 |

## 实测环境

- Windows 10/11 两台。OpenSSH Server 随系统提供。
- PuTTY 安装在非默认目录（如 `D:\PuTTY`）。用 `Get-Command putty` 先定位，不要只查 `C:\Program Files`。
- PuTTYgen 无法做命令行转换之后，Python 3 + `cryptography` 兜底已在真实环境验证：plink 输出 `OK`，并成功启动 PuTTY 窗口。

## 安全约束

- 不在聊天或日志里输出私钥、token；只传公钥。命令、截图和提交里也不放私钥或 `.ppk` 正文。
- `sshd` 只监听 Tailscale 地址，防火墙只放行 `100.64.0.0/10` 的 TCP 22。禁用密码登录。
- 不修改或停止对方机器上正在线上运行的服务；只改 SSH 相关配置。
- 改 `sshd_config` 前先备份，改后 `sshd -t` 校验再重启。
