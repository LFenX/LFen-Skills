# 显示器音频排查 Skill

变更时间：2026-10-26 07:51:33 +08:00（Asia/Singapore）；详细执行时间见任务 `T-AUDIO-20261026-001` 的 RunLedger。

## 变更与原因

- 新增 `skills/dev-tools/repair-windows-monitor-audio/`：把 LG 27UP850 + RTX 3060 的免整机重启恢复经历整理为可复用的分层诊断流程与脱敏案例。
- `collect-audio-state.ps1` 与 `CoreAudioProbe.cs`：默认只读采集，测试音和静音流时钟均为显式可选项。
- `restart-nvidia-audio-controller.ps1`：默认只读预检，动态验证 NVIDIA HDAUDIO 与独立 PCI HDAudBus 控制器父子关系；仅显式 `-Apply` 执行一次，并恢复此前运行的全部依赖服务。
- 增加 PowerShell 隔离测试，覆盖误选目标、权限、待重启、占用、原生命令失败、服务恢复和重检目标变化。
- 更新 `catalog/taxonomy.json`，由原有生成器同步中英文 README、SKILLS、CATALOG 与机器索引。
- 按用户指定，优先向“LFEN Blog：模板整理与文章共创”发送详细材料、证据索引、事实边界和题图/正文说明图要求。文章及图片由该会话集成网站。

## 实际验证

- PowerShell 7 与 Windows PowerShell 5.1 各通过 16 项隔离恢复检查，未操作真实服务/设备。
- 两个 PowerShell 版本的真实默认采集均为 `ReadOnlySnapshot`，没有播放测试音或执行恢复；真实预检正确识别 `System/HDAudBus`。服务状态及音频引擎实例保持不变。
- Skill frontmatter 校验通过；使用仓库支持的 `metadata.description_en` 提供英文描述。
- catalog 生成及 `--check` 通过，目录含 9 个 Skill；catalog 回归 22 项、安装入口检查器回归 10 项通过。
- 初次 Skill 校验缺少 PyYAML，已仅在聊天工作目录安装验证依赖；初次 PS5.1 测试夹具缺少 ServiceProcess 程序集，补齐夹具后重新通过。原失败保存在任务证据中。

- 安装器回归共 17 项，16 项通过，1 项 POSIX PTY 交互测试因本机为 Windows 跳过；远端矩阵由提交后的 GitHub Actions 验证。

最终发布与远端确认以任务后续证据和交付记录为准，不在此预填成功。

## 未验证边界

- 本次 Skill 制作没有再次执行真实 `-Apply`；历史成功修复单独标为现场案例，隔离测试不冒充二次真实修复。
- 没有数小时/隔夜防复发验证；深度睡眠与具体驱动缺陷仍是未确认触发条件。
- 不包含凭证、原始私人日志或本机唯一设备实例 ID；不修改系统节能注册表、安装器或其他 Skill。
