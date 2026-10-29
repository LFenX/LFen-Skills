# 工具接入步骤

来源核对日期：2026-10-29。新电脑先按 [完整执行手册](new-device-runbook.md) 建立本机采集下限，再启用这里的上传插件。执行时重新核对官方页面和当前工具帮助；不得把本次 Windows 版本组合外推为所有平台均已验证。

## 1. 配置来源与凭证

WakaTime CLI v2.28.0 的配置查找顺序为：显式 `--config`、有效 `WAKATIME_HOME` 下的 `.wakatime.cfg`、已经存在的 `~/.wakatime.cfg`、XDG 配置。已有空文件同样影响优先级；部分插件直接使用 `~/.wakatime.cfg`。同时检查项目 `.wakatime`、导入配置、`project_api_key` 和 `api_urls` 覆盖，但不输出内容中的凭证。

在 Windows 中 `~` 通常是 `%USERPROFILE%`，macOS/Linux 使用实际用户主目录。读取配置时只报告 key 是否存在，不报告其值、长度、摘要或尾号；不得把完整配置复制进公开 skill。

用户已有 key 时保留它。编辑器可通过官方密码输入框配置；用户自己从 [密钥页](https://wakatime.com/api-key) 复制完整 key 并确认。不把 key 通过聊天传递，也不默认轮换已有 key。

来源：[CLI 配置与优先级](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/USAGE.md)、[WakaTime 隐私说明](https://wakatime.com/privacy)。

## 2. Cursor 与 VS Code

分别检查对应程序的扩展列表；两个编辑器的扩展安装互不替代。CLI 已在 PATH 时执行：

```powershell
code --list-extensions --show-versions
cursor --list-extensions --show-versions
code --install-extension WakaTime.vscode-wakatime
cursor --install-extension WakaTime.vscode-wakatime
```

只安装用户选择的编辑器；程序不在 PATH 时，从已确认的安装位置调用其 CLI，不凭空拼路径。

命令面板搜索 `WakaTime`，从当前版本实际显示的列表选择 API Key 命令。本次 v30.2.1 显示的是 `WakaTime: Api Key`；官网搜索词是 `WakaTime API Key`。不能要求用户逐字找到一个当前版本没有显示的名称。

若出现 `Invalid api key`，先确认用户已输入完整值并按回车；密码框截图不含有效 key 不能据此推断账户错误。不要让用户把 key 发到聊天。

用户在真实项目编辑并保存后，核对真实活动、插件日志的错误类别和服务端结果；不只看状态栏图标。

来源：[Cursor 官方接入](https://wakatime.com/cursor)、[VS Code 官方接入](https://wakatime.com/vs-code)。

## 3. Codex：先确认实际客户端

用户使用 ChatGPT 桌面客户端中的 Codex 时，以该客户端为验证目标。下面命令用于安装管理插件；插件名带 CLI 不表示用户实际改用 CLI 工作。

WakaTime 官方入口：

```powershell
codex plugin marketplace add wakatime/codex-cli-wakatime
codex plugin add codex-cli-wakatime@wakatime
```

安装前盘点全局 hooks、已有 WakaTime npm 包和插件，保留其他 hooks 与 notify。不要为了支持桌面端再叠加社区 `codex-wakatime` 的 Stop/PostToolUse hooks。

本次官方插件 v1.0.0 定义 `SessionStart`、`UserPromptSubmit`、`PostToolUse` 三类事件；Windows runner 调用 Node，用户通过运行时原生入口审阅并信任。信任定义变更后重新确认状态，不直接修改信任哈希。

只读检查可使用当前运行时的 hooks 状态接口。若需另起 app-server，仅 initialize 和 `hooks/list`，不启动 thread/turn；关闭自己启动的子进程。该检查证明插件被发现及受信任，不能证明原先已打开的桌面会话加载了它。

后续修复已对真实 Codex 新记录核对 Editor/模型，并对新会话开头先消息后 context、重复同步做隔离验证。固定修复在 [采集契约](collector-contract.md) 和随包补丁中。未来接入仍须在目标桌面客户端以真实任务验收，办公室证据不能代替另一台设备。

版本兼容问题先看本机 `codex --help`、插件代码和当前官方文档。不要无过滤输出巨大的插件市场目录。插件使用的历史参数别名未列入 `--help`，也不能直接认定为失效；先验证参数解析及官方实现。

来源：[WakaTime 官方安装页](https://wakatime.com/codex-cli)、[官方插件源码](https://github.com/wakatime/codex-cli-wakatime)、[Codex hooks 文档](https://learn.chatgpt.com/docs/hooks)。

## 4. Claude Code

按官方插件市场安装，确认当前 CLI 支持的用户作用域参数：

```powershell
claude plugin marketplace add https://github.com/wakatime/claude-code-wakatime.git
claude plugin install claude-code-wakatime@wakatime --scope user
```

沿用共享 WakaTime 配置。检查插件启用状态和实际客户端加载情况，再用真实任务验证；不要重写用户整个 Claude 配置。

来源：[WakaTime 官方 Claude Code 安装页](https://wakatime.com/claude-code)、[官方插件仓库](https://github.com/wakatime/claude-code-wakatime)。

## 5. OpenCode

`angristan/opencode-wakatime` 是社区插件，不能标为 WakaTime 官方插件。检查实际 OpenCode 版本和现有 JSON/JSONC 配置，包括用户指定的配置覆盖。

本次验证的社区包版本为 1.4.0，安装方式如下；这不是对未来最新版本的断言：

```powershell
npm install --global --ignore-scripts opencode-wakatime@1.4.0
opencode-wakatime --install
```

安装器注册 npm 插件。核对现有 `opencode.jsonc`、`opencode.json` 或 `config.json` 的实际修改，保留注释、供应商、模型、凭证与其他插件；仅追加缺失的 WakaTime 注册，不复制整份示例覆盖用户配置。

当前项目说明同时覆盖 v1/v2，字段及入口必须按实际版本核对。不能把本次 v1 的 `plugin` 字段和 `opencode debug config` 验证方式无条件用于其他版本。若运行配置检查，只输出 WakaTime 注册状态，不打印包含供应商 key 的整份结果。

检查项目级重复注册或遗留独立插件文件。只清理已确认属于该 WakaTime 安装的冗余项；重启 OpenCode 后验证真实活动。

来源：[社区插件说明及安装器行为](https://github.com/angristan/opencode-wakatime)。

## 6. Grok Bot 与额外采集来源

CLI 的 AI 活动同步能扫描多个工具的本地记录。看到 Grok Bot 不代表本次曾安装同名插件，也不证明其底层模型一定是 Grok。

先核对实际程序、日志来源和当前 CLI 对应 parser；遵守用户最新的保留/排除选择。未识别实际产品时不按名字下载程序。额外来源与重复采集的处理见 [准确性与恢复](accuracy-and-recovery.md)。

## 7. 多设备

每台设备独立执行所需工具的接入步骤，并使用同一 WakaTime 账户的 API Key。仅登录 GitHub、同一个 ChatGPT 账户或同一个编辑器账户，不代表已经安装采集器。

通过安全入口分别配置 key；不要把整份用户配置、密钥、离线数据库、内部 checkpoint 或信任记录放进 Git、聊天或云盘共享。仅复用已经确认可公开的规则模板。

不同设备使用不同的 `hostname`，例如一台 `office-pc`，另一台 `home-laptop`。可用本包部署参数合并；手工方式同样只编辑各自已有 `[settings]`，不覆盖整个文件：

```ini
[settings]
hostname = office-pc
```

同一项目在不同盘符或系统上的路径分别映射到一致项目名。然后逐台正常编辑、逐台核对来源和上传结果；不能用一台设备的成功替代其他设备验收。

来源：[WakaTime FAQ](https://wakatime.com/faq)、[hostname 与配置规则](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/USAGE.md)。
