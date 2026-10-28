# WakaTime 多工具统计接入 skill

- 变更时间：2026-10-28T19:28:29+08:00
- 任务：T-WAKATIME-SKILL-20261028-001
- 原始要求：总结本次接入的过程、步骤和经验为专属 skill，放入 LFen-Skills，按基本流程上传；精准分类并使用多级目录。

## 变更

- 新增 `skills/coding-activity-analytics/wakatime/setup-wakatime-ai-tracking/`：正文、UI 元数据、两份参考文档、只读诊断脚本及隔离测试。
- 新增“编程活动统计 / WakaTime”两级分类，保留所有既有 skill 的名称和路径。
- 文档覆盖 Codex 桌面与 CLI 区分、Cursor/VS Code、Claude Code、OpenCode 社区插件、Grok Bot 选择、多设备、凭证保护、非 Git 项目、Other、模型版本、队列积压和已验证边界。
- 诊断仅使用本机 CLI 的版本、队列数量及有限样本读取；不上传、不改配置、不生成 heartbeat，不输出密钥或原始会话/项目/路径。
- 登记 `catalog/taxonomy.json`；生成 README 中英文、SKILLS 中英文、CATALOG 和 JSON 索引，新增说明沿用 category-path。
- 任务契约、执行和工程结果按现有 `.project-governance/tasks/` 机制留档。

## 执行记录

- 原仓库已有其他任务改动，本任务使用基于最新 origin/main 的独立 Git worktree。
- Windows 长路径导致首次 checkout 失败；Git 使用命令级 longpaths 完成。治理索引在长目录出现 SQLite 打开失败，改用工作区内短路径恢复。未修改仓库业务脚本。
- 初次执行上下文遗漏数据处理扩展，编辑检查明确阻断；保留 failure，经正式 Amendment 补齐 E03 后使用新 Attempt，检查通过后才编写内容。

## 验证与上传

- Skill 结构验证通过；诊断脚本 9 项测试通过；目录 22 项、安装链接 10 项测试通过。
- 安装器 17 项测试中 16 项通过，1 项 POSIX 专用测试在 Windows 跳过；`bash -n install.sh` 通过。
- 本机只读冒烟通过，完整模型版本保留；未发送新 heartbeat 或请求上传。
- 新增 skill 分类为两级，原 9 个 skill 路径不变；本地引用、UI 元数据、目录一致性和 `git diff --check` 通过。
- 对本任务文件执行实际 key 精确匹配及私人项目路径检查，命中数为 0；不保存 key 或私有路径清单。
- 详细验证见本任务 `evidence/verification.json`。提交推送及远端核验尚待执行。

## 范围限制

本任务交付可复用 skill；没有重新安装用户开发工具、修改实时 WakaTime 配置、处理历史统计或再次执行补传。案例里尚未核验的桌面事件和云端细分仍明确标注未核验。
