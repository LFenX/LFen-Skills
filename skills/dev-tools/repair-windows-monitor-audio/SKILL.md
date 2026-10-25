---
name: repair-windows-monitor-audio
description: "排查 Windows 通过 HDMI/DP 连接的显示器扬声器在待机或唤醒后全局无声的问题，保存证据并分层检查默认输出、音频服务、端点和 NVIDIA 独立音频控制器。适用于音量正常、系统有播放信号却听不到声音，希望定位故障并尝试不重启电脑恢复的场景。"
metadata:
  description_en: "Diagnose system-wide silence from HDMI/DisplayPort monitor speakers after standby or wake on Windows. Preserve evidence and distinguish default outputs, Windows Audio, endpoints, and NVIDIA's independent audio controller before an explicitly authorized recovery without rebooting the PC."
---

# Windows 显示器音频排查与局部恢复

目标是定位本次故障所处的层级、验证实际听感，并保留能解释恢复结果的证据。适用范围是 Windows 显示器音频；恢复助手只支持已验证父子关系的 NVIDIA HDAUDIO 设备和其独立 PCI 音频控制器，不能用于其他厂商或整张显卡。

## 先保存故障现场

先确认无声影响一个应用还是全系统、平时从哪台显示器出声、何种待机后发生、重启显示器和电脑各自的结果。长待机才发生时，记录大致时长；短时无法复现不能当作排除依据。不要先重启整机、重装驱动、改省电注册表或同时调整多个开关。

Windows PowerShell 5.1 / PowerShell 7 下，先做只读采集：

```powershell
& ./scripts/collect-audio-state.ps1 -ReportPath ./work/audio-before.json
```

采集器使用 Windows 自带的 PnP、服务、事件日志与 Core Audio；无需安装音频模块。报告含本机设备名和实例标识，保存在本地，分享时脱敏。

检查三类默认输出（Console、Multimedia、Communications）、音量/静音、设备状态、Windows Audio 与 AudioEndpointBuilder。存在远程软件虚拟声卡不等于它劫持了输出。设备状态 OK 也不证明物理扬声器已经工作。

获得用户同意播放测试音后，可运行：

```powershell
& ./scripts/collect-audio-state.ps1 -PlayTestTone -ReportPath ./work/audio-test.json
```

默认输出必须是用户要测试的显示器。采集器拒绝在 Console 与 Multimedia 默认设备不同的情况下播放，以免把测试声送往另一设备。测试音有固定的低振幅，不修改系统音量；实际响度仍取决于设备音量。

峰值非零只证明音频引擎内有信号，也可能混有其他应用的音频。必须询问用户是否在目标扬声器上听到声音，不能由 API 成功或音量条跳动代替听感。需要检查流时钟时单独使用 `-MeasureClock`；它会打开短暂的静音共享流，时钟推进不能证明 HDMI 实际出声。

## 按证据选择下一层

| 观察 | 下一步与解释边界 |
| --- | --- |
| 默认输出、音量或单应用设置错误 | 只改相关设置，重复相同测试；恢复后停止扩大操作。 |
| 端点缺失或断开 | 核对显示器输入与信号连接；查断开/恢复事件。必要时让用户重连信号线，再验证端点和听感。 |
| 系统信号存在、目标扬声器仍全局无声 | 保留报告后，区分服务层恢复、链路重建和控制器重置；每次只做一类操作。 |
| 重启 Windows Audio 成功，但实际仍无声 | 记录服务层恢复无效；不能据此排除所有驱动或设备状态问题。 |
| PnPUtil 返回 3010 或设备要求重启 | 本次没有证明即时恢复成功；不要自动加 `/reboot`，也不要清除待重启标记。 |
| Kernel-PnP 225 指出 audiodg.exe 持有设备句柄 | 说明设备重启被占用阻挡，不能直接当作最初失声原因。 |
| 子设备等待系统重启，后续命令返回 50 | 停止重复操作该子设备。仅在父控制器身份验证通过后考虑下述定向恢复。 |

如果需要重启服务，先记录所有正在运行的依赖服务，并在 `finally` 中恢复它们。不能假定 `Restart-Service -Force` 会还原每个依赖服务原先的状态。

## NVIDIA 控制器的定向恢复

这是一项会短暂中断音频的管理员操作。先展示目标并核对当前请求是否已授权这次恢复；已有明确授权时继续，不重复询问。技能被安装、以前成功过或一次采集操作本身，都不构成执行恢复的授权。

```powershell
# 默认只读：输出发现的音频子设备、父控制器及待重启状态。
& ./scripts/restart-nvidia-audio-controller.ps1

# 多个候选时，基于只读报告选择准确的 HDAUDIO 实例，不取列表第一项。
& ./scripts/restart-nvidia-audio-controller.ps1 -AudioDeviceInstanceId '<已核实的 HDAUDIO 实例>'
```

助手验证：音频子设备为 NVIDIA MEDIA/HDAUDIO，直接父设备为 NVIDIA PCI 设备、Class=System、Service=HDAudBus。必须区分独立音频控制器与 Class=Display 的图形设备；实例 ID、PCI 地址和功能号以当前电脑查询结果为准，不能照抄案例。

预检通过且用户授权后，在管理员 PowerShell 中执行：

```powershell
& ./scripts/restart-nvidia-audio-controller.ps1 -Apply -ReportPath ./work/audio-recovery.json
```

脚本只执行一次定向恢复：记录运行中的依赖服务，停止 Windows Audio，等待 audiodg 退出，重新核验目标，调用一次 `pnputil /restart-device <音频控制器>`，在 `finally` 中恢复服务。不会重置图像显卡、强杀进程、卸载驱动、改注册表或重启系统。`-Apply -WhatIf` 只预览。

以下情况停止恢复并报告：设备候选不唯一、父子关系/厂商/类别/服务不符、父控制器已经要求重启、音频服务不是 Running、audiodg 未退出、PnP 命令非零、设备恢复异常或服务恢复失败。不要批量重启 System 设备，不自动换目标或循环重试。

PnP 命令退出 0 之后仍需：确认音频控制器与子设备状态正常、相关服务 Running、默认输出正确，再播放相同测试音并收集用户听感。脚本返回 `ControllerRestarted` 只代表控制器重启完成，不代表音频已恢复；保留 `audibility=NotVerified` 直到用户确认。

## 长待机触发的后续验证

显示器自己的自动待机与深度睡眠、Windows 自动息屏/睡眠、NVIDIA 音频空闲省电是不同设置。先查询当前值及具体型号手册，再考虑单变量实验。

关闭深度睡眠后当前故障未立即恢复，不足以排除它与下次触发有关；一次控制器重置成功，也不能证明硬件损坏或某个特定驱动缺陷。要验证防复发，先恢复正常播放基线，再按相同时长待机，记录同一测试结果；没有数小时/隔夜试验就明确写“尚未验证”。

## 案例与来源

遇到 LG 27UP850 + NVIDIA 或需理解 3010、50、audiodg 占用和控制器层级差异时，读 [2026-10-26 实测案例](references/2026-10-26-lg-27up850.md)。它是一次成功恢复记录，不是通用根因结论。

- [PnPUtil 命令](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax)与[返回值](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-return-values)。
- [Core Audio 峰值位于端点音量衰减之前](https://learn.microsoft.com/en-us/windows/win32/api/endpointvolume/nn-endpointvolume-iaudiometerinformation)。
- [NVIDIA 空闲音频节能说明](https://nvidia.custhelp.com/app/answers/detail/a_id/5441)：讨论播放起始丢音，不能直接等同于持续完全无声。

完成时报告有效操作、实际听感、服务/设备收尾状态、保留设置与未验证触发条件。恢复即停止；不要为了验证 Skill 再重置一台正在正常发声的电脑。
