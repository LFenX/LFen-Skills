# 新设备完整执行手册

供没有原对话、办公室文件或其他 skill 的 Agent 从本包执行。使用原 WakaTime 账户和 dashboard，不建立替代看板，不清账号历史。以下 PowerShell 命令从本 skill 根目录执行；所有变量都是在目标电脑上解析。

## 0. 预检与分流

1. 读取本 skill 的 SKILL.md、collector-contract.md 和工具接入步骤。恢复用户实际选择，当前案例包含 Codex、Cursor、VS Code、Claude Code、OpenCode、Grok Bot；另一设备只装其实际使用工具。
2. 检查操作系统、架构、Python、Git、Node（官方 Codex 插件需要）、工具真实版本、现有 hooks/notify、WakaTime 插件和配置入口。只输出脱敏摘要，不打印整份配置或 transcript。
3. 自动定制包支持 Windows x64、Python 3.11+、Git、Go 1.27.3。macOS/Linux/ARM：官方基础接入可按各工具官方说明执行；本包定制部署未验证，禁止直接运行 Windows 命令或宣称相同修复已生效。
4. `WAKATIME_HOME` 必须未设置；本自动安装只接受标准 `USERPROFILE/.wakatime` 和 `USERPROFILE/.wakatime.cfg`。环境变量、XDG、import_cfg、api_urls、项目专用 key、项目配置或插件使用自定义入口时，先确认真实路由；不能通过复制默认配置或改环境变量冒充标准路径。inspect 不验证凭证或所有覆盖来源。
5. **暂停 WakaTime 采集链，再安装**。尚未装插件的新设备先完成下面部署；已有插件的设备先暂停相关扩展/插件并保留原状态。当前 Agent 的 Codex 插件也会产生活动，不能一边触发 hook 一边改配置。`--collectors-stopped` 是操作者确认，不是脚本已自动停进程的证明。

```powershell
$wakaSkill = (Get-Location).Path
$wakaPython = (python -c "import sys; print(sys.executable)").Trim()
& $wakaPython --version
git --version
& $wakaPython -B -X utf8 scripts/inspect_wakatime.py
& $wakaPython -B -X utf8 scripts/deploy_tracking.py inspect --profile $env:USERPROFILE
```

若 python 是系统占位程序或版本不足，从 Python 官方安装可用解释器再继续。不要将钥匙或令牌输入终端命令。

| sync_state | 操作 |
| --- | --- |
| fresh | 尚无 AI 进度且无旧队列；用 `--fresh-device` 建本机当前 UTC 下限 |
| existing | INI/checkpoint 一致；省略 fresh，沿用现有进度 |
| blocked_state_needs_inspection | 保留文件，停止部署/手工同步；定位实际状态，不重置或回拨 |

`fresh` 不等于已证明账号从未收到此设备数据；还要检查旧采集链。曾用过同设备/恢复过系统时先排除重传风险。

## 1. 固定源码、构建和隔离回归

将中间文件放在任务自己的 work 目录，禁止放入用户项目或覆盖已有构建目录。下面使用系统 TEMP 下的新 GUID 目录，不涉及真实会话、密钥和队列。

```powershell
$wakaWork = Join-Path $env:TEMP ('wakatime-device-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $wakaWork -ErrorAction Stop | Out-Null
$wakaSource = Join-Path $wakaWork 'upstream'
git -c core.longpaths=true clone --no-checkout https://github.com/wakatime/wakatime-cli.git $wakaSource
if ($LASTEXITCODE -ne 0) { throw '官方源码获取失败，停止。' }
git -c core.longpaths=true -C $wakaSource cat-file -e '37ab01e6d80dbe9a05f0ee3cd90012e988090c7a^{commit}'
if ($LASTEXITCODE -ne 0) { throw '固定提交不可用，不能改用 latest。' }
$wakaGo = (Get-Command go -ErrorAction Stop).Source
& $wakaGo version
$wakaBuild = Join-Path $wakaWork 'build'
& $wakaPython -B -X utf8 (Join-Path $wakaSkill 'scripts/build_collector.py') --source $wakaSource --output $wakaBuild --go $wakaGo
if ($LASTEXITCODE -ne 0) { throw '隔离构建或回归失败，禁止部署。' }
$wakaManifest = Join-Path $wakaBuild 'build.json'
```

没有 Go 1.27.3 时，从 [Go 官方下载](https://go.dev/dl/) 校验对应 Windows amd64 包及 SHA-256，解压到任务工具目录，给 `$wakaGo` 赋其实际 `bin/go.exe` 路径；不替换系统其他项目的 Go。构建首次从官方 module proxy 拉取 go.sum 校验依赖，需网络。网络或 Go 版本失败时停止，不关闭校验、不换未知镜像。

构建脚本会导出固定提交、验证补丁 SHA、执行补丁 `--check`、以合成 HOME 运行 Go 回归，再编译和隔离版本探测。`build.json` 只有通过后才产生。测试只针对本地合成来源与回环服务，不向真实账号造活动。

## 2. 计划与部署

先确认本机已有统计未在并行写入，按实际 `sync_state` 二选一。`home-pc` 是示例；使用与办公室不同且本机专属的名称。脚本不改变任何 projectmap、排除项或项目文件。

**新设备、使用 Cursor 的示例：**

```powershell
& $wakaPython -B -X utf8 scripts/deploy_tracking.py plan --profile $env:USERPROFILE --manifest $wakaManifest --fresh-device --cursor --hostname home-pc
if ($LASTEXITCODE -ne 0) { throw '预检失败，停止。' }
& $wakaPython -B -X utf8 scripts/deploy_tracking.py install --profile $env:USERPROFILE --manifest $wakaManifest --fresh-device --cursor --hostname home-pc --collectors-stopped
if ($LASTEXITCODE -ne 0) { throw '部署失败，保留日志与状态；不得直接重置后重跑。' }
```

**已有一致进度的设备：**上面两条去掉 `--fresh-device`，其他按实际工具选择。没有 Cursor 则去掉 `--cursor`。不要对已有进度强行 fresh。

Grok Bot 需要软件版本时，从本机已确认可执行文件的 `VersionInfo` 读取，传 `--grok-bot-version <实测版本>`。不要把案例版本、产品名或 Grok 模型号填进去。未能测到就不传，保持未知。

部署仅写两个 CLI、必要设置和选择启用的 Cursor stop hook；Cursor 原有其他 hook 条目保留。备份在本机 `.wakatime/lfen-tracking-deployment/`，包含当前 Windows 用户绑定的 DPAPI 加密原文件，不能迁往另一机器。新设备同时建立当前时间下限、空 checkpoint 和空 Cursor journal；存在的队列/journal/checkpoint不覆盖。

重复运行同一安装应返回 `already_installed`，不回拨时间、不添加第二条 hook。之后用户修改了非本包配置时，重复检查仍可确认本包选项，但自动回滚会因完整文件摘要变化停下，要求局部合并。若构建不同、私有配置格式不支持、旧同名元数据 hook 已存在或同步状态冲突，停止并给出具体分歧，不堆叠新钩子。

## 3. 账户、原生插件与信任

1. 本机配置 API Key：用户从 [原账户密钥页](https://wakatime.com/api-key) 复制，经本机受保护配置编辑器或官方插件密码框输入；不要发聊天、传命令行或导出截图。新配置尚无 key 时不宣布鉴权成功。
2. 按 [tool-setup.md](tool-setup.md) 安装/启用实际选择的官方插件。Codex 使用官方 `codex-cli-wakatime`，不能再叠加社区 Stop/PostToolUse 上传链。Cursor/VS Code 各装各自扩展，Claude/OpenCode按已确认版本接入。
3. Codex 的 SessionStart / UserPromptSubmit / PostToolUse 按真实运行时审阅信任；新定义需要重新信任时引导用户操作。安装脚本不改信任摘要，不伪造用户同意。
4. Cursor 自定义 stop 只记录元数据，不发心跳。应用内 Agent 对话才能触发；在 Codex 中聊天不等于执行 Cursor Agent。重载后先核对 hooks 状态与实际一轮事件。
5. 本地构建保持 `<local-build>`，实测官方插件 1.0.0 会保留；插件升级后重新核对实际二进制摘要和版本逻辑，不关闭所有工具升级，不自动覆盖/强制回退未知版本。
6. Grok Bot 由原生 AI parser 读取本机消息镜像，Windows 当前解析器路径为 APPDATA/Grok Bot；没有独立官方 Grok Bot 插件可据此臆造安装命令。不记录未经暴露的具体模型。

## 4. 会话与项目验收

每个实际工具独立测试，使用真实项目的正常活动，不造 heartbeat、不把合成夹具上传。可使用已有项目，不初始化 Git、不改项目名称。

1. 新建短 Codex 桌面会话，在实际项目读取/编辑一个代码文件。核对开始消息与同轮 context 的型号；尚 pending 时等待正常后续 hook，不能手动回拨。
2. Cursor 自带 Agent 在实际项目完成一轮，等待结束回调和至少 10 秒稳定，再由原生 WakaTime 扩展/官方 hook 正常同步。journal 原始字段与实际 session/turn 精确对应，云端 Editor 为 Cursor；模型来自同轮原生与 stop。未知校准组合要明确 Token 覆盖限制。
3. 使用 Grok Bot、Claude Code、OpenCode、VS Code 的，分别核对其真实活动。一个工具成功不能替代其他工具或第二台机器验收。
4. 云端使用已登录原 dashboard、授权导出或按官方要求授权的 API；检查新机器名、真实时间/项目、Editor、文件语言、具体型号/effort、Token 三类。只读 GET 可退避，任何未知上传结果先读回，不自动整批重试。
5. 保存同一精确会话第一次读回的 ID、时间、项目、实体、型号与 Token 摘要；**正常重复同步**后再读回：同一事件不新增、三类 Token 不再增长。保存验收范围和状态，原始路径/会话不放进公开仓库。
6. 原有项目历史不参与本次操作，已有统计不应变化；新真实活动按原规则继续累积。项目名称跨设备一致时，设备路径映射各自配置并以真实文件事件验证。

手动同步不是默认必需。只有已确认需要时，从实际已装插件代码取得 `--plugin` 标识，先校验再发送：

```powershell
$wakaPlugin = Read-Host '输入本机官方插件已实测的 plugin 标识（不含密钥）'
& $wakaPython -B -X utf8 scripts/native_sync.py --profile $env:USERPROFILE --plugin $wakaPlugin
if ($LASTEXITCODE -ne 0) { throw '原生进度不一致，禁止发送。' }
& $wakaPython -B -X utf8 scripts/native_sync.py --profile $env:USERPROFILE --plugin $wakaPlugin --send
```

该发送读取真实本地活动、写原生 checkpoint/队列并联系 WakaTime；不是只读命令。退出码只证明命令结束，实际入云仍需读回。超时或错误不清队列、不重复并行启动。

## 5. 故障恢复和交付

```powershell
& $wakaPython -B -X utf8 scripts/deploy_tracking.py inspect --profile $env:USERPROFILE
```

按问题处理：401/403修本机凭证；429遵守等待；hook未信任走原生信任入口；APPDATA/来源不匹配核对当前版本；没有准确 ID 保持未关联；版本不在 Token 校准范围保持原值；新 Editor null 先检查 actual user-agent，不用软件版本冒充模型。

要撤销本包时先暂停采集链：

```powershell
& $wakaPython -B -X utf8 scripts/deploy_tracking.py rollback --profile $env:USERPROFILE --collectors-stopped
if ($LASTEXITCODE -ne 0) { throw '有新修改或状态未知，保留现场并逐项合并，禁止覆盖。' }
```

回滚仅恢复摘要一致的本包文件；密钥和其他后续修改导致配置摘要变化时停止。**已采集的 journal、队列、内部进度和新设备下限保留**，防止撤销后重放历史。已有正常流量后切回官方版仍须观察新会话及去重；不删除整目录，不把部署备份同步到家用设备。

向用户报告：工具/版本、构建摘要、已加载的 hook、真实会话与新机器证据、项目与去重结果、Token 校准覆盖、未验证项和错误分类。安装、单元测试、loopback通过不等于家用电脑真实入云通过；缺少实际目标设备时交付执行包与验收流程，明确待该设备完成，不能保证未来任意版本零错误。

可复制给另一台电脑 Agent 的提示：

> 使用 $setup-wakatime-ai-tracking，按 references/new-device-runbook.md 把这台电脑实际使用的 Codex、Cursor、VS Code、Claude Code、OpenCode、Grok Bot 接入我原来的 WakaTime 账户。先检测工具和系统，复用固定修复补丁与最小钩子，只采集本机接入后的新活动。密钥由我在本机输入；不复制其他设备配置/会话/队列/checkpoint，不改现有项目统计。以真实会话核对 Editors、具体型号、语言、Token 缓存、机器名和重复同步；不支持的版本停止相关步骤并报告，不猜字段，不清历史。
