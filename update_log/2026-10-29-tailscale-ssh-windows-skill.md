# 远程访问分类与 Tailscale SSH skill

- 变更时间：2026-10-29T16:05:39+08:00
- 原始要求：按仓库现有规则新增通用 skill `setup-tailscale-ssh-between-windows-pcs`，并新增一级分类 `remote-access`（远程访问）。素材为已实测草稿；事实不改，示例用户名和 IP 用占位符。

## 变更

- 新增 `skills/remote-access/setup-tailscale-ssh-between-windows-pcs/`：`SKILL.md`、`agents/openai.yaml`、`scripts/openssh_ed25519_to_ppk.py`。
- `catalog/taxonomy.json` 登记一级分类「远程访问」和该 skill。scope 为 `general`。标签为 `openssh`、`putty`、`remote-access`、`ssh-keys`、`tailscale`、`windows`。
- 由 `python scripts/update_catalog.py` 重写 `CATALOG.md`、`catalog/index.json`、`README.md`、`README.en.md`、`SKILLS.md`、`SKILLS.en.md` 的生成区，并把 skill 徽章计数改为 11。
- 草稿中的具体 Windows 用户名改为占位符。保留的事实是：两边实际登录用户名可以不同，家里机用户名与工作机用户名可能不同；管理员组账号的公钥必须写入 `administrators_authorized_keys`。
- 失败表保留「推测：known_hosts 里已有该 IP 的旧主机密钥（未逐项核实）」。

## 原因

把两台 Windows 经 Tailscale 内网做 SSH 密钥互登、以及 PuTTY `.ppk` 转换的已实测流程，收成可复用 skill。分类按草稿定为一级叶子 `remote-access`，深度为 1，不超过 2 层。

## 实际验证

- `python scripts/update_catalog.py`：退出码 0。输出「已更新 README.md、README.en.md、SKILLS.md、SKILLS.en.md、CATALOG.md 与 catalog/index.json：11 个 skill」。
- `python scripts/update_catalog.py --check`：退出码 0。输出「分类目录校验通过：11 个 skill，7 个一级分类，Markdown 与 JSON 目录一致」。正文定稿后再次执行，结果相同。
- `python scripts/test_update_catalog.py`：22 项通过，退出码 0。
- `python scripts/test_check_install_links.py`：10 项通过，退出码 0。
- `python scripts/test_installers.py`：17 项中 10 项通过，7 项跳过，退出码 0。跳过原因是本环境不是 Windows，`install.ps1` 测试要求 `powershell.exe`。这 7 项不能记为通过。
- `bash -n install.sh`：退出码 0。
- `python scripts/check_install_links.py --no-fetch`：退出码 2。输出「安装克隆 /home/ubuntu/.lfenskills 不存在或没有任何 SKILL.md」。这不是通过。
- `python .github/scripts/check_release_tag.py rgpw-v6.3.0-candidate`：退出码 0，`tag` 与 `expected` 都是 `rgpw-v6.3.0-candidate`。
- `python skills/remote-access/setup-tailscale-ssh-between-windows-pcs/scripts/openssh_ed25519_to_ppk.py --self-test`：退出码 0，输出 `self-test passed`。该检查只确认临时密钥的 PPK v2 结构与 MAC 自洽，不保留密钥文件。
- 用本机 `puttygen` Release 0.81，对 3 个临时 OpenSSH ed25519 密钥分别执行 `--ppk-param version=2 -O private -C openssh-ed25519`。脚本写出的 `.ppk` 与 puttygen 字节相同，标准输出只有输出路径。临时文件已删除。这只核对本脚本实现；不把 Linux puttygen 的命令行参数写成 Windows 图形版 PuTTYgen 的用法。草稿记录的 Windows 图形版不支持 `-O private -o`，本次没有在 Windows 上重做。
- 非 ASCII 注释被拒绝，退出码 1，标准错误为「注释只接受单行 ASCII。」，不写输出文件。非法私钥文件退出码 1，标准错误不回显文件内容。
- `python skills/coding-activity-analytics/wakatime/setup-wakatime-ai-tracking/scripts/test_inspect_wakatime.py`：11 项通过，退出码 0。
- `python skills/data-processing/fetch-xhs-interaction-metrics/scripts/self_test.py`：7 项通过，退出码 0。
- `python skills/data-processing/match-tabular-records/scripts/self_test.py`：第一次失败，`ModuleNotFoundError: No module named 'openpyxl'`。随后只在当前环境执行 `python -m pip install openpyxl`，再次运行退出码 0，输出 `self_test: passed`。未把 openpyxl 写入仓库。
- `python skills/dev-tools/skill-practice-collector/client/test_outbox.py`：2 项通过，退出码 0。
- `python skills/product-engineering/run-governed-product-workflow/scripts/audit_norm_retrieval.py --validate-only --runtime-only`：退出码 0，`status` 为 `Passed`。
- `python skills/product-engineering/run-governed-product-workflow/scripts/audit_norm_consistency.py --project-root . --runtime-only`：退出码 0。`Blocker`、`Major`、`Minor` 均为 0，`Observation` 为 1，类别是 `task_contract_snapshot_not_applicable`。
- `python skills/product-engineering/run-governed-product-workflow/scripts/self_test.py --project-root .`：退出码 0。`positive` 与 `negative` 均为 `passed`。
- `git diff --check`：退出码 0。

## 未执行或未通过

- 没有在原始 Windows 机器上重跑 `plink` 或启动 PuTTY。草稿里的「plink 输出 OK」仍只代表当时的实测，不代表本次交付环境复现了该结果。
- `python scripts/check_install_links.py --no-fetch` 退出码 2，见上。
- `scripts/test_installers.py` 的 7 项 PowerShell 测试被跳过，见上。
- 仓库内没有 `skill-creator/scripts/quick_validate.py`，未执行。
- `skills/dev-tools/repair-windows-monitor-audio/tests/test-recovery.ps1` 未执行：本环境没有 Windows PowerShell。
- `audit_norm_integration.py`、`audit_norm_shadow.py`、`audit_tailoring_coverage.py`、`audit_console.py`、`validate_task_package.py` 未执行。它们不是本次 catalog 工作流的入口，且需要既有任务目录；本次没有修改这些脚本。
