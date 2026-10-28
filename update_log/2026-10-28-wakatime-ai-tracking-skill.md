# WakaTime 多工具统计接入 skill

- 变更时间：2026-10-28T19:28:29+08:00
- 任务：T-WAKATIME-SKILL-20261028-001
- 原始要求：总结本次接入的过程、步骤和经验为专属 skill，放入 LFen-Skills，按基本流程上传；精准分类并使用多级目录。

## 变更

- 新增 `skills/coding-activity-analytics/wakatime/setup-wakatime-ai-tracking/`：正文、UI 元数据、两份参考文档、只读诊断脚本及隔离测试。
- 新增“编程活动统计 / WakaTime”两级分类，保留所有既有 skill 的名称和路径。
- 文档覆盖 Codex 桌面与 CLI 区分、Cursor/VS Code、Claude Code、OpenCode 社区插件、Grok Bot 选择、多设备、凭证保护、非 Git 项目、Other、模型版本、队列积压和已验证边界。
- 初版诊断调用本机 CLI 的版本、队列数量及有限样本；后续单轮审查发现该 CLI 在错误恢复时存在写入和诊断上传分支，初版的只读承诺不成立。已按新的明确授权移除全部 CLI 调用，详见当日独立修复日志。
- 登记 `catalog/taxonomy.json`；生成 README 中英文、SKILLS 中英文、CATALOG 和 JSON 索引，新增说明沿用 category-path。
- 任务契约、执行和工程结果按现有 `.project-governance/tasks/` 机制留档。

## 执行记录

- 原仓库已有其他任务改动，本任务使用基于最新 origin/main 的独立 Git worktree。
- Windows 长路径导致首次 checkout 失败；Git 使用命令级 longpaths 完成。治理索引在长目录出现 SQLite 打开失败，改用工作区内短路径恢复。未修改仓库业务脚本。
- 初次执行上下文遗漏数据处理扩展，编辑检查明确阻断；保留 failure，经正式 Amendment 补齐 E03 后使用新 Attempt，检查通过后才编写内容。

- 留档阶段发现 S7 旧查询与 S8 不一致；保留 7 份历史查询及请求原件，核对字节不变后由正式工具重建索引，S8 任务包检查通过。未改动治理工具实现。

## 验证与上传

- Skill 结构验证通过；诊断脚本 9 项测试通过；目录 22 项、安装链接 10 项测试通过。
- 安装器 17 项测试中 16 项通过，1 项 POSIX 专用测试在 Windows 跳过；`bash -n install.sh` 通过。
- 本机只读冒烟通过，完整模型版本保留；未发送新 heartbeat 或请求上传。
- 新增 skill 分类为两级，原 9 个 skill 路径不变；本地引用、UI 元数据、目录一致性和 `git diff --check` 通过。
- 对本任务文件执行实际 key 精确匹配及私人项目路径检查，命中数为 0；不保存 key 或私有路径清单。
- 详细验证见本任务 `evidence/verification.json`。内容提交 `f9e8a0f8177418f0c2e4da26470827495fcdad35` 已常规推送至 `origin/main`，`ls-remote` 核对一致；两项 GitHub Actions（Validate skill catalog、Skill gates）均已成功。后续工程结果记录沿用该已验证内容版本。

- 留档后的项目视图生成曾被旧安装副本的 schema 阻断；改用仓库当前治理工具后重建和任务包检查通过，未修改历史任务。详情见 `evidence/finalization.json`。

## 范围限制

本任务交付可复用 skill；没有重新安装用户开发工具、修改实时 WakaTime 配置、处理历史统计或再次执行补传。案例里尚未核验的桌面事件和云端细分仍明确标注未核验。

## 一轮审查与后续修复

- 用户明确指定只做一轮；独立只读审查完整报告见 `.project-governance/tasks/T-WAKATIME-SKILL-20261028-001/evidence/review-round-01.md`。
- 本轮确认 F01（P1，真实队列 CLI 探针未隔离）和 F02（P2，两种凭证配置漏脱敏）；保留原始问题，不记为干净轮次。
- 用户随后明确授权“修复、复验并上传，不再审查”，限 1 批、30 分钟。修复与实际复验由 `T-WAKATIME-FIX-20261028-001` 留档，见 `update_log/2026-10-28-wakatime-diagnostic-fixes.md`。
- 原审查仍为一轮；后续工程测试不计为第二轮，也不宣称两轮审查通过。
