---
name: setup-wakatime-ai-tracking
description: "将 Codex 桌面客户端、Cursor、VS Code、Claude Code、OpenCode 和 Grok Bot 的真实活动接入原 WakaTime dashboard，支持家用电脑等多设备。包含固定源码修复补丁、Cursor stop 元数据钩子、Windows 新设备部署与回滚，核对 Editors 发起方、具体模型、Token 缓存、会话项目关联、语言和重复同步；不用于模型供应商配置或 GitHub 主页卡片。"
metadata:
  description_en: "Connect Codex desktop, Cursor, VS Code, Claude Code, OpenCode, and Grok Bot to the existing WakaTime dashboard across devices. Includes a pinned collector patch, Cursor stop metadata hook, and Windows deployment and rollback. Verify actor attribution, precise model, cache-aware tokens, session/project joins, language, and deduplication. Excludes model-provider configuration and GitHub profile cards."
---

# WakaTime 多工具接入与准确性核验

把用户实际使用的开发工具接入同一 WakaTime 账户，并以真实活动验证采集、上传和仪表盘归因。安装完成、hooks 受信任和统计准确是不同结论。

## 新电脑直接入口

接入另一台电脑时，先读 [新设备完整执行手册](references/new-device-runbook.md)，按“预检 → 隔离构建 → 部署 → 配置密钥 → 官方插件 → 真实事件验收”执行。不能先启用上传再建立新设备时间下限。

修复包基于官方 CLI 固定提交，属于本 skill 的本地修改，不能冒称官方已合入。自动构建和部署支持 **Windows x64 / Python 3.11+ / Go 1.27.3**；其他系统只走官方基础接入，定制修复须先移植与验证。读取 [采集契约和支持边界](references/collector-contract.md) 后再决定是否部署。

## 先确定对象和授权

1. 从当前对话恢复已确认的工具、设备、账户和排除项；不重复要求注册或提供已经回答的信息。
2. 检查实际程序、版本、已装插件、现有 WakaTime 配置入口和队列；只输出脱敏摘要。使用用户主目录及实际安装位置，不硬编码本次案例的用户名、盘符或项目路径。
3. 分清用户操作界面和底层来源字段：ChatGPT 客户端中的 Codex、独立 Codex CLI、VS Code 内的 Codex 扩展不能只凭同名标签互相替代。`source=vscode` 也不能单独证明用户打开了 VS Code。
   工具归属按实际活动发起方核对：Codex 调用 Cursor 作为编辑器时，该活动归 Codex，Cursor 只作为宿主编辑器信息；不能按编辑器进程名直接归为 Cursor。Cursor 自身发起的活动单独区分，历史记录缺少关联证据时保留未决。
4. 保留用户最新选择。Grok Bot 已被选入时继续统计；未确认其实际产品和来源时先检查，不按名字安装陌生包或添加排除规则。
5. 只处理用户要求的接入与修复；不附带修改 GitHub 卡片、公开隐私设置、历史统计或其他工具配置。

## 按需要读取

- 安装、密钥输入、hooks 信任、多设备：读 [工具接入步骤](references/tool-setup.md)。
- 项目名、Other、模型显示、重复来源、离线同步：读 [准确性与恢复](references/accuracy-and-recovery.md)。
- 新设备操作命令、凭证与状态隔离、回滚、真实验收：读 [新设备执行手册](references/new-device-runbook.md)。
- 固定补丁、Cursor 会话关联、Token 校准范围、历史重载教训：读 [采集契约](references/collector-contract.md)。
- 本地检查：在本 skill 目录运行 `python scripts/inspect_wakatime.py`。仅读取配置状态和检查 CLI 文件是否存在，不启动 CLI、不读取真实队列、不修改配置、不调用网络上传、不产生新 heartbeat。输出 `offline_queue.status=not_checked` 不是空队列或同步成功的证明。

执行前核对当前官方安装页、插件来源和本机帮助。未知 CLI 的 `--help`/`--version` 也只在合成 HOME、空配置和隔离环境探测。参考版本不是永久兼容保证；固定补丁不能直接套到更新的上游提交。

## 接入顺序

1. 记录现有插件、hooks、notify、配置来源及排除规则。对含凭证的配置，只在用户控制的安全位置备份；不得进入公开仓库、交付附件或普通日志。
2. 优先使用对应工具的 WakaTime 官方插件。OpenCode 社区插件单独标明来源。先盘点旧采集链，再决定是否替换，避免并行添加同职责的 Codex hooks。
3. 引导用户在官方插件的密码输入框或本机受保护配置入口输入 API Key；不索要聊天粘贴，不把实际 key 放进命令参数、截图、工具输出或提交。
4. hooks 按运行时提供的审阅入口由用户信任。新定义要求重新信任时说明具体变更；禁止直接改信任摘要、伪造已同意或创建假对话触发。
5. 打开真实项目，正常编辑并保存；AI 工具使用一次真实任务。利用用户已经完成的活动，不创建测试文件或伪造 heartbeat 来让图表出现数据。
6. 对照下面的证据层次逐项报告。没有访问云端的条件时，交付可确认的本地结果及缺失证据，不宣布全部准确。

## 核验证据

| 层次 | 可确认的事实 | 不能据此确认 |
| --- | --- | --- |
| 安装 | 对应插件已安装、启用，配置键存在 | 运行中的客户端已加载、鉴权成功 |
| 执行 | 实际目标客户端执行了已信任 hooks 或原生插件事件 | 云端已收到全部活动 |
| 采集 | 本地记录具有实际文件、项目上下文、模型字段 | 仪表盘已按相同维度展示 |
| 上传 | 服务端成功响应、队列变化与时间窗口相符 | 所有记录都已上传、历史显示已改正 |
| 展示 | 已登录仪表盘或授权导出的记录与真实活动对应 | 未检查的设备、日期、项目同样准确 |

插件管理命令通过、另起 app-server 的 `hooks/list` 返回 trusted，只证明注册和信任状态；不能替代当前已打开桌面进程的实际执行证据。需要重开客户端时说明原因，并沿用既有授权。

## 元数据核对

- **工具**：对照真实客户端、采集器来源和原始 source。多个 Codex 标签先调查重复来源；保留用户实际在用的集成及原有 notify，逐项移除已确认由本次接入新增的冗余项。
- **项目**：没有 GitHub 仓库也能统计。名称来自用户明确选择、客户端已有项目标签或项目根；全局 `projectmap` 可避免给项目增加文件。配置可读不等于真实事件命中了映射。
- **语言**：区分 `type=file` 与 `type=app`、空语言和服务端 Other。只对有实际文件上下文的事件讨论语言识别；不能把项目主要语言套给全部聊天活动。
- **模型**：区分工具名、模型系列、版本与推理强度。保留原始 model 标识，再检查采集 token 和云端维度；`GPT` 标签本身不能证明版本丢失。
- **指标**：先看单位和日期。Models 的代码变更行数占比，不等于请求次数、token、费用或聊天时间占比。
- **设备**：每台设备独立安装、使用同一账户的 key、保留独立机器名和 checkpoint。路径映射逐台配置，已有项目统计保留。禁止把办公室的配置整包、会话、队列、checkpoint 或钩子信任记录复制到家用电脑。

## 已封装的执行资源

| 资源 | 职责 |
| --- | --- |
| `assets/wakatime-session-20261029.patch` | 已验证 f 版源码修复及 Go 回归夹具 |
| `scripts/build_collector.py` | 固定提交导出、补丁校验、合成 HOME 测试与 Windows 构建 |
| `scripts/deploy_tracking.py` | 只读预检/计划、合并配置、备份部署和严格摘要回滚；不启动 CLI、不上传 |
| `scripts/cursor_stop_metadata.py` | 本地 stop 元数据白名单、哈希关联、去重入库；不独立产生 heartbeat |
| `scripts/native_sync.py` | 校验原生 INI/checkpoint 一致；默认只检验上下文，`--send` 才补传真实活动 |

执行脚本都在本 skill 内，不依赖原会话的 `work/`、其他 skill 或办公室路径。测试使用合成数据，测试事件不能发往真实账号。版本升级后重新验证；不要静默让官方自动更新覆盖本地构建。

## 输出与停止条件

输出已接入工具、真实执行及上传证据、已修正项、未核验项和所用官方来源。每次只向用户请求当前缺少且能解除阻断的信息，不索取已经给出的错误示例。

遇到失效密钥、hooks 未信任、运行中客户端未加载、接口限流、数据来源不明或无法读取已登录仪表盘时，停止受影响的验证或上传重试，继续独立的只读检查。不得清队列、重置内部 checkpoint、关闭 TLS 验证、反复强制重试，或通过删除历史数据改善图表外观。

本次经验的适用边界和官方来源见两份参考文档；它们不能替代未来运行中的实际证据。
