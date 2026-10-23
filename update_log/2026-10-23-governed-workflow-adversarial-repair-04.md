# 对抗性审查第四轮返修

- 建立时间：2026-10-23T12:54:50.030919Z（UTC）。
- 原任务：T-ADVERSARIAL-20261023-001；返修任务：T-ADVERSARIAL-20261023-005。
- 原因：第四轮确认 AR04-F01，已结束会话在普通修订变Stale后可沿用旧Accepted追加新轮。
- 授权：原实际会话尚未通过，沿用用户“开始审查”已涵盖的本范围修复与复验。
- 计划涉及：既有审查脚本、Schema/受保护契约、signals/审阅Markdown、回归、verify命令卡、既有分发与安装副本及任务记录。
- 验证待执行；不覆盖并行安装治理脚本，不新增无Offer授权模式。

- 修复：以机器计算的 session_completed 保留历史结束事实，证明失效后返回 RestartRequired，旧 Accepted 不能追加 Round/Blocked；真实新决定重新计数。未结束 Stale 会话继续沿用原授权。
- 文件：既有 adversarial_review.py、signals.py、self_test.py、verify.md、Full/Minimal Schema、官方重封 embedded-manifest、控制台分发及安装端 7 个本方文件。
- 验证：协议 50、边界 105；源码完整 self_test 13:08:49–13:10:22 UTC 退出 0；两个第四轮原始反例均拒绝旧授权追加且记录字节不变。
- 安装：保留并行治理 add9aff 补丁，13:15:33–13:17:10 UTC 完整 self_test 退出 0，96 文件期间稳定。
- 规范：检索验证通过；一致性 Complete，Blocker/Major/Minor 均 0，1 项任务快照不适用 Observation；skill 与目录、工作树格式校验通过。
- 记录重试：首次内部 amend_record 调用参数名错误，在函数进入前被 Python 拒绝，未改写任务；核对 API 后重试成功，证据 recording-retry.json。
- 冻结源码：f0f3ce7fedddffcc889a3ec941009839521f0705a62e19b1fcea11aaf585e6af（96 文件）。GitHub 发布及门禁待实际完成。
- 实际审查：四轮均有问题，当前连续无问题 0；AR04-F01 等待下一轮独立复核。人工验收保持 Pending。

- 收尾校验：S8时旧S5查询仍活动导致失败，归档写守卫先明确拒绝未列路径；正式Amendment仅补本任务两个派生路径，保留旧查询后重建历史索引。Scope变更使旧计划失效，官方get_context重编译并完整消费8/8结果；A03重新校验EXECUTION READY通过。失败与恢复均追加账本并保留原件；未修改源码或重新索取授权。

- GitHub：ff0c31d38ee89f27c9f20a840776d29af1304b69已推送；Actions39960619568三个Python门禁成功，release按策略skipped。工程结果正式保存Implemented/ManagedByParent，用户验收Pending；接续原会话下一轮完整独立审查。
