# 流程技能本地修复同步 GitHub

- 变更时间：2026-10-23 15:48（Asia/Shanghai，UTC+8）。
- 用户原话：`run-governed-product-workflow`  似乎没有将最新的修复内容更新到github上
- 涉及目录：`skills/product-engineering/run-governed-product-workflow/`。
- 配套文件：`scripts/update_catalog.py`、`scripts/test_update_catalog.py`、`.github/workflows/catalog.yml`、本日志。

## 原因与变更

- 当前工作区 `D:/LFEN_project/dev_project/LFen-Skills` 与远端 `origin/main` 均位于 `07f712ada4ec6774dab36b344cf2e80d3caba8c8`；首次检查时工作区干净。
- Codex 与 `.agents` 的技能入口实际通过 Junction 指向 `C:/Users/Administrator/.lfenskills/skills/product-engineering/run-governed-product-workflow`。该安装仓中的修复尚未提交：相对于当前工作区，技能有 23 个修改文件及新增的 `scripts/get_approval_subject.py`。
- 同步真实验收、批准绑定、需求逐条复核、历史证明兼容、验证补录、控制台与项目文档兼容及其回归用例。保留本仓后续安装器修改；目录解析器仅合入 `metadata.description_en` 的兼容改动，CI 合入对应测试。
- 受保护资产由官方 `scripts/sync_embedded_references.py` 重新封装，未手写 Manifest；未将安装仓的个人配置、生成缓存及任务历史复制到当前仓库。
- 同步期间用户指出 `before.json` 膨胀，后续修复另见 `update_log/2026-10-23-governed-workflow-amendment-growth.md`。

## 实际验证

- Git 远端读取：`git fetch origin`、`git ls-remote origin refs/heads/main` 成功，确认遗漏发生在未提交的安装仓文件。
- 首次组合补丁的 `git apply --check` 因当前仓 CI 已增加安装器测试而失败，检查阶段未写文件；随后仅对目录解析器应用补丁，对 CI 合入对应增量，保留现有测试。
- `python -X utf8 -m unittest discover -s scripts -p 'test_*.py' -v`：49 项，48 项通过，1 项 POSIX PTY 用例因 Windows 平台跳过，退出码 0。
- 官方 `skill-creator/scripts/quick_validate.py`：`Skill is valid!`，退出码 0。
- `python -X utf8 scripts/update_catalog.py --check`：8 个 skill、5 个一级分类通过；无需重写中英文 README 或生成目录。
- 技能完整 `self_test.py --project-root <当前仓库>`：同步版本通过；后续膨胀修复版本再次通过，包含新增 22 项增长回归。
- `audit_norm_retrieval.py --validate-only --runtime-only`：Passed，46 个受保护资产、28 个 gold case、23 项 CLI 契约通过。
- `audit_norm_consistency.py --runtime-only`：Complete，Blocker/Major/Minor 均为 0；1 项 Observation 为未指定 TaskContract 的快照检查不适用。
- Git 发布结果以本次提交及远端分支核验为准；工程验证不冒充人的验收决定。
