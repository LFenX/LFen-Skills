# 准确性与恢复

来源核对日期：2026-10-29；官方基线 v2.28.0 与本 skill 固定修改版必须分开。已封装修复、session/turn 去重及 Token 校准范围见 [采集契约](collector-contract.md)。实际运行必须记录所装版本、日期范围、时区和指标单位。

## 1. 先取得脱敏本地摘要

在本 skill 目录运行：

```powershell
python scripts/inspect_wakatime.py
```

脚本只读取所选配置的状态并检查 CLI 文件是否存在，不启动任何 CLI。输出 `cli_executed=false`、`offline_queue.status=not_checked`；不获取版本、真实队列数量、事件、语言或模型。不输出 key、项目名、文件路径、hostname 值、提示词、代码或原始 user-agent。

非标准 CLI 位置使用 `--cli`；非标准配置使用 `--config`，值是本机文件路径。脚本不执行 `api_key_vault_cmd`，不递归读取导入配置，不扫描整个会话目录。`api_key_in_selected_config` 仅表示选中文件有该字段，不是有效凭证或全部配置已解析的证明。

未检查的队列不能报告为零或已同步。旧命令的 `--sample-limit`、`--timeout` 继续接受，但不触发读取或子进程；解析摘要函数只用于隔离输入及测试。摘要对选中配置的敏感值、项目专用 key、凭证前缀及旧 UUID v4 保守脱敏；不把未知模型或缺少样本视为采集失败。配置解析失败返回固定错误类别，不输出异常原文。

原因：v2.28.0 的本地队列查询以可写方式打开数据库；损坏恢复会改名原队列，错误分支还会强制启用诊断发送并加载凭证。因此 `--offline-count` 和 `--print-offline-heartbeats` 不能被包装成无副作用的只读探针。真实 CLI 操作需按实际恢复、凭证与网络行为核对，不能据参数名称认定安全。来源：[队列打开与恢复](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/offline/offline.go#L445-L603)、[强制诊断分支](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/offline/error.go#L29-L42)。

## 2. 多个 Codex 标签

从实际进程、安装记录、hooks、原始 session source 和采集器链调查。v2.28.0 的 Codex parser 可以按 session `source` 生成 `codex-<source>`；本次桌面记录出现过 `source=vscode`。单看 `Codex Vscode` 不能推出用户正在 VS Code 编码。

用户已明确：Codex 使用 Cursor 的编辑器能力时，主工具应统计为 Codex，Cursor 是宿主编辑器。核对活动发起方、会话、时间与项目关联，再确定归属；编辑器名不等于 AI 工具名。保留原始来源供追溯，不把所有 Cursor 历史记录统一改名为 Codex，也不将缺少关联证据的记录强行归类。模型另按原始 model 核验。

本次曾额外安装社区 `codex-wakatime`，与内置 AI 同步并存，出现额外来源。修复时备份并移除了本次新增的社区 hooks 和包，保留其他 notify，改用 WakaTime 官方插件。该修复经验不构成“所有同名来源都是重复”的规则。

卸载前确认归属，只移除已经识别的冗余采集器；不清空整个 hooks 配置，不禁用用户仍在使用的集成。未来事件的来源修正不能承诺自动重写旧图表。

来源：[Codex source 与事件解析](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/ai/codex.go)、[官方 Codex 插件](https://github.com/wakatime/codex-cli-wakatime)。

## 3. Other 占比高

按相同日期窗口检查事件类型、实际文件和语言字段：

| 本地证据 | 结论与下一步 |
| --- | --- |
| `type=app` 且 language 为空 | 该样本没有具体代码文件语言；继续核对服务端归类，不能直接叫作语言识别失败 |
| `type=file`、文件存在、语言为空或错误 | 核对扩展名、内容、编辑器语言模式及当前语言检测器支持情况 |
| AI 实际改了文件，但记录只有 app | 检查工具事件、patch 解析和文件上下文是否丢失 |
| 本地语言正确但云端显示错误 | 核对上传、日期/时区、筛选、规则和云端原始记录 |

后续已区分真实 file、app 与动态拼接路径，并重载了有可复核来源的历史；最终观察的 Other 为 4.37%，仅是当时窗口的结果，不是未来设备的通过阈值。仍有缺源记录保留。不能把样本扩展成“全部 Other 都是聊天”，也不能仅凭比例断定代码语言全未识别。

`guess_language=true` 不能补出不存在的文件上下文。本次启用后出现无实际文件的语言猜测告警，已恢复原值；这不是修复 Other 的通用开关。只对真实文件和验证过的规则做窄范围覆盖，不给整个项目聊天统一指定主要语言。

源码支持的 patch 路径与 shell/任意文件写入并不等价。搜索直接 `apply_patch` 计数为零，也不能排除经 code-mode 包装的 `tools.apply_patch`；核对实际事件结构，不读取或输出无关提示词。

来源：[CLI AI 活动处理](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/ai/ai.go)、[Codex 文件事件解析](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/ai/codex.go)、[语言识别与自定义规则 FAQ](https://wakatime.com/faq)。

## 4. 非 Git 项目名称

不要求创建 GitHub 仓库或初始化 Git。优先采用用户明确名称、客户端已有项目标签及真实项目根；同一路径有多个不同标签时保持未决，不凭目录名代替用户选择。

全局映射示例，合并到现有配置，跨设备各自使用对应路径：

```ini
[projectmap]
(?i)^D\x3a/Projects/local-app(/|$) = LocalApp
^/Users/dev/Projects/local-app(/|$) = LocalApp
```

Windows 示例用 `\x3a` 匹配盘符冒号，避免 INI 将未引用键中的 `:` 当分隔符；边界使用 `(/|$)`，不要在未引用键里引入含冒号的 `(?:...)`。正则需锚定项目根和边界，防止把 `local-app-backup` 归入 `local-app`；嵌套项目需核对匹配顺序。确认 CLI 对输入路径的规范化方式后再使用相应斜杠表达式。只有用户选择项目内配置时，才写 `.wakatime-project`；不要静默向所有项目加文件。

验证分两层：原生配置读取确认规则已保存，再用真实项目事件确认命中结果；只有前一层通过时，不能声称项目显示已校准。不要承诺本地映射自动重命名既有云端历史。

来源：[projectmap 配置](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/USAGE.md)。

## 5. 都显示 GPT

依次比较原始 model、推理强度、采集出的模型 token、云端保存值与展示分组。v2.28.0 从 Codex `turn_context` 读取型号和 effort，再生成带版本的 user-agent token；例如本次观察到的 `gpt-6.1-sol`、`max` 会按代码形成 `gpt/6.1-sol-max`。

WakaTime 的模型名称和版本是不同概念；FAQ 在 GPT 下列出多个版本。因此图上仅写 GPT，不足以证明采集器丢失版本。反过来，源码支持版本也不能证明当前账户已经正确上传、保存和展示。

Models 显示 `lines` 时统计 AI 代码变更行数；GPT 为 100% 不等于所有聊天、请求或 token 都来自 GPT。不能从 Grok Bot、Cursor、OpenCode 等工具名直接猜底层模型。

后续原始记录已核对 GPT 6.1-sol/max、GPT 6-astra/xhigh、Composer 2.5 和 Cursor Grok 的具体版本；原生 Models 图仍按系列汇总。Grok Bot 缺少具体型号时仍为未知；模型尚未出现时等待同轮 context，不借前轮型号。详细行为与支持范围见采集契约。

如果用户要按具体版本分别展示，先检查当前官方界面/API 是否提供该维度。没有已验证入口时说明限制，不通过改插件名或编造字段模拟模型版本。

来源：[model/effort 解析](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/ai/codex.go)、[模型 token 规范化](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/ai/ai.go)、[模型版本 FAQ](https://wakatime.com/faq)、[AI 指标定义](https://wakatime.com/developers)。

## 6. 同步积压与限流

先记录能够安全取得的队列状态、样本时间范围、认证/网络/限流错误类别。无法只读取得数量时写“未检查”，不要运行底层可写诊断取数。队列大不直接等于模型识别失败；也不能把旧记录当刚发生的新活动。

AI 活动手工同步优先使用本包 `native_sync.py` 固定真实配置与资源，先验证 INI/checkpoint。新设备下限未建立、进度不一致时拒绝上传。不得使用 `WAKATIME_HOME=用户主目录` 的临时脚本读取另一份旧进度。

确有离线队列需补传且已有授权时，核对当前 CLI 的 `--sync-offline-activity` 行为；只在隔离环境读帮助。标准 Windows 路径经确认后可有界补传真实记录：

```powershell
$wakaCli = Join-Path $env:USERPROFILE '.wakatime\wakatime-cli-windows-amd64.exe'
if (-not (Test-Path -LiteralPath $wakaCli)) { throw '未找到标准位置的 WakaTime CLI，请先确认实际路径。' }
& $wakaCli --sync-offline-activity 1000 --timeout 15
$syncExitCode = $LASTEXITCODE
Write-Output ('同步命令退出码：' + $syncExitCode)
```

`1000` 是活动数量参数；`--timeout` 是请求超时，不保证整个进程在该秒数内结束。由执行工具另设有限总时长，超时后保留队列并检查实际效果，不立即叠加新进程。一次队列下降不是全部上传或某一进程独立完成的证明，其他采集器也能同时同步。

遇到 401/403/429、backoff 或网络超时时，先解决对应原因，遵守服务端重试等待；不删内部配置来绕过退避，不清空 offline 数据库，不反复全量重放。命令非零退出或超时必须如实报告。

来源：[CLI 参数与离线机制](https://github.com/wakatime/wakatime-cli)、[离线 FAQ](https://wakatime.com/faq)。

## 7. 云端读取与历史修正

插件 API Key 用于发送活动；其他 API 集成按当前官方文档使用 OAuth。不要复用 key 在临时脚本里读取任意账户统计。使用已登录仪表盘、授权导出或正式授权集成核验云端；浏览器停留登录页时不能假装已经看到数据。

配置变更默认核验后续真实事件。需要修正历史时，先明确范围、保留原记录和精确 manifest；删除、批量重标记、扩大公开权限需有对应明确授权。原始事件重放、合并 Token、同时间 UUID 排序和历史客户端版本缺失均会引入误差，见采集契约的历史修复边界；新电脑接入不包含这些操作。

来源：[WakaTime API 授权规则](https://wakatime.com/developers)。
