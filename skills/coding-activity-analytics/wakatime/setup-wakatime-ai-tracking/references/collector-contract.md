# 采集契约与已验证边界

本文件记录 2026-10-29 的实际修复，不把案例环境当作未来设备的事实。

## 1. 固定构建与来源

- 上游：[WakaTime CLI](https://github.com/wakatime/wakatime-cli)，基线 `v2.28.0`，提交 `37ab01e6d80dbe9a05f0ee3cd90012e988090c7a`。
- 随包补丁：`assets/wakatime-session-20261029.patch`，SHA-256 `50d12b1969a8b780ec57c192a4e187875dad041a9177191b4743f359df9f5608`。
- 修改版 commit 标识 `37ab01e6-lfen-session-20261029f`，版本输出 `<local-build>`。不是官方发布。源码许可保留于 `assets/WAKATIME-CLI-LICENSE`。
- 可复现构建固定 Go 1.27.3 Windows x64。`build.json` 保存本次产物摘要；编译路径/时间不同会影响字节，不能拿另一台电脑的二进制 SHA 冒充本机验证。
- 构建从固定提交 `git archive`，不会带入工作区未跟踪诊断程序。源码补丁内的路径、会话和 Token 是合成测试夹具。

## 2. 维度分别取证

| 维度 | 正确来源 | 禁止替代 |
| --- | --- | --- |
| Editor/工具 | 发起活动的 Codex、Cursor Agent、Claude Code、OpenCode、Grok Bot | 用宿主窗口或模型供应商冒充工具 |
| 宿主 | 实际编辑器来源，作为 provenance 保留 | Codex 调用 Cursor 就归 Cursor |
| 模型 | 当前 turn 的原生 model、effort；Cursor stop 与同代原生记录交叉验证 | 上一轮型号、UI 选中型号、软件版本 |
| 项目/时间 | 原生会话根、文件和原始活动时间 | 根据最近项目、账单行时间或 hook 到达时间猜关联 |
| 语言 | 实际 file 路径/内容、已验证检测器 | 对所有 app 聊天套用项目主语言 |
| Token | 原生去重累计差分，或已校准且精确关联的 stop 元数据 | 缺失填零、缓存重复计入、跨请求汇总后猜分摊 |

`ai_tool_identity=true` 明确发起方；`ai_strict_patch_paths=true` 不把动态拼接表达式误作真实文件。两项只修元数据，沿用原项目、原始时间、实体和已记录度量。

缺源保持未知。原生 Grok Bot 样本未提供具体模型，保持 `model=null`；原生服务将其 Editor 显示为 **Grok**。该显示名与模型名不是同一维度。没有人工确认排除项时保留 Grok Bot。

## 3. Codex 开头型号与去重

新用户消息先于同轮 `turn_context` 到达时，以 `task_started/turn_context` 的 **turn_id** 关联；新轮清空前轮型号。尚未取得同轮上下文的开头活动保持 pending，同会话后续活动不能越过它提交 checkpoint。下一次重新读取原始来源，取得模型后保留原时间上传。

回归覆盖先消息后 context、跨轮换模型、缺失/错误 turn_id、不借前轮型号及重复同步。unknown 不拿 Codex 软件版本填充；没有上下文时要报告 pending，不能为消除 Unknown Editor 伪造型号。

## 4. Cursor stop 元数据

`cursor_stop_metadata.py` 仅保存：工具、记录时间、模型/供应商/客户端版本、conversation/generation 的 SHA-256、四类原始 Token 和去重键。忽略 prompt、消息、文件路径、密钥和账号。数据库仅存本机 `.wakatime/cursor-stop-metadata.sqlite3`；不是上传器。

- 原生 `composerId + requestId` 与 stop `conversation_id + generation_id` 分别哈希精确连接。缺任一 ID、冲突、无项目上下文或已上传边界，不猜配、不追加历史使用量。
- 以 generation 去重，并在 checkpoint 持久化使用量提交标记。重复 stop、重复同步或重启不会重复加 Token。
- 安装时先建立空 journal，使 stop 尚未到达时能进入等待分支。完成回调字段齐全后等待 10 秒稳定；同会话后续活动不能越过未完成代。15 分钟未完成回退原生活动，缺 Token 继续如实缺失。
- Journal 读取最多最近 10,000 行；长期离线、严重积压或晚到回调超出窗口必须单独诊断。该钩子只覆盖 parent turn，不宣称覆盖全部子代理。
- 已有原生 Token 时不覆盖。Journal 不独立造活动、不改项目、不把 hook 观测时间写成活动时间。

**补充 Token 的精确校准范围**：Cursor `3.24.18`，原始 model 为 `grok-4.7-xhigh` 或 `cursor-grok-4.6-xhigh-fast`，四字段均存在、cache_write=0、input>=cache_read。普通输入 = 原始 input - cache_read，缓存独立保留，输出沿用原值。该范围来自同账号官方用量的实际核对。

其他客户端/模型/非零 cache_write：不套用上述算式，不新增校准条目；保留原始字段，待同账号证据确认。hook 存到了 Token 不等于云端获得完整 Token。已核对的实样普通输入 31,511、缓存 57,152、输出 1,526，仅作为当次证据，不能当新电脑预期数值。

`cursor-grok-` 的路由前缀只在同代原生 modelInfo/官方用量已对应的语义下规范为 `grok-`；原始值仍保留于 journal。不能通过型号字符串修改价格或账单。

## 5. 原生状态、设备与配置

CLI 中 `WAKATIME_HOME` 指 **resources 目录本身**。默认资源是 `~/.wakatime`；默认插件配置常为 `~/.wakatime.cfg`。官方 Codex 插件 1.0.0 却将同名环境变量当 home 再拼 `.wakatime`，因此本自动流程拒绝继承自定义 WAKATIME_HOME，不全局设置它。

手工同步使用 `native_sync.py` 显式 `--config`、`--internal-config`，仅给子进程设置资源环境。执行前要求 INI 截止时间等于 checkpoint 的 global 或 previous_global。原生 progress 缺失、损坏或不一致必须停；禁删文件、清零或回拨。

新设备：在采集器启用前建立本机当前 UTC 下限与空 checkpoint，不导入更早会话。既有设备：原 checkpoint 不动；Cursor 的 `ai_cursor_stop_since` 是本机新增 hook 的生效时间，不能抄案例日期。

`hostname` 使用本机唯一名称。共享项目名称，各自设置锚定根路径的 projectmap；安装器不写 projectmap、不更改项目结构、不要求 Git/GitHub。所有原有 key、notify、hooks、项目规则与排除项保留。

## 6. 看板逐项验收

| 看板 | 核对方法与边界 |
| --- | --- |
| Projects / 时间 | 真实项目名、时间范围、时区、timeout；本次安装不改历史活动，不清空账号 |
| Editors | Codex 为 Codex，Cursor 自己的 Agent 为 Cursor，Grok Bot 原生归 Grok；查来源和重复采集链 |
| Languages | 单独分析 file/app；Other 不设必须降到某比例，动态路径和无文件聊天继续未知 |
| Models | 原生饼图按系列/代码变更行数分组；具体版本与 effort 查授权原始记录，不把 GPT 占比直接判错 |
| Tokens | 输入/缓存/输出分开；缺字段与 0 分开，跨会话及重复同步核对不增长 |
| Cost | API 单价估算，不是订阅账单；缺具体版本/价格不等于免费 |
| OS / Machines | 本机系统和独立 hostname；多设备后验证出现不同机器，单台 Windows=100% 符合事实 |
| Categories / AI / 其他 | 对照本次来源的实际事件类型、指标单位和覆盖窗口；100% 不自动构成错误 |

依据：[官方指标与 API](https://wakatime.com/developers)、[模型与费用口径 FAQ](https://wakatime.com/faq)。细分依赖真实 source，不增加未经验证的 OpenLIT/网络抓取器来猜客户端内未暴露的型号。

## 7. 历史修复经验：不属于新电脑安装

以下是危险路径说明，随包不提供账号专属 DELETE/重载执行器。

1. 修改识别器不会自动改旧图。需要历史修复时另定日期、机器和精确 ID 清单；冻结备份与不可变 manifest，取得对应授权再变更。
2. 原始事件数量不等于云端已合并 heartbeat 数。直接重放会重复、丢失合并 Token 或改变时长。没有完整合并证据时保留旧计数，不猜分摊。
3. 同时间跨项目活动的 UUID 排序会影响归属。仅“总时长相同”不足以证明项目统计保留；逐日逐项目核对，并保留原同时间最后归属。无法保证时停止重载。
4. 导出缺失客户端版本时不能覆盖已正确保存的 user-agent。Composer 2.5 + `cursor/unknown` 曾导致 Unknown Editor；保留当时已测历史版本，不能拿今天版本代替。
5. 有并发真实活动时，以每次操作前快照比较同范围字段，新活动另列；不能因整个窗口总数变化就误删正常数据。
6. 已知效果与结果未知分开；POST/DELETE 超时禁止自动重试。先只读确认实际效果，不能整批重放。GET 可遵守服务端退避、gzip 和响应大小上限，不关闭 TLS。
7. 必须恢复历史上传时按原 measured machine 设置 URL 编码的 `X-Machine-Name`；不能默认归到执行机器。custom rules 不支持修 Editor/模型，仅按官方支持维度使用。
8. 缺源记录保留，不为了图表好看删除。原生模型系列图、缺失请求 ID 的账单和缺源 Grok Bot 模型仍有事实边界。

来源：[官方 heartbeat 接口](https://wakatime.com/developers#heartbeats)、[custom rules 范围](https://wakatime.com/faq#custom-rules)、[原生 CLI 固定源码](https://github.com/wakatime/wakatime-cli/tree/37ab01e6d80dbe9a05f0ee3cd90012e988090c7a)。
