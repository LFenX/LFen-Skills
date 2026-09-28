# 加入 AI 客诉系统升级技能

- 变更时间：2026-09-28 21:22（UTC+8）。
- 涉及文件：`skills/ai-complaint-system/aics-cloud-upgrade/`、`catalog/taxonomy.json`、`CATALOG.md`、`catalog/index.json`、`README.md`、`README.en.md`、`SKILLS.md`、`SKILLS.en.md`、本日志。
- 变更摘要：在 `skills/` 下新增分类 `ai-complaint-system`，显示名为 Ai Complaint System，并放入 `aics-cloud-upgrade`。分类目录由 `scripts/update_catalog.py` 重新生成。
- 原因：把本机已核对过的 AICS 升级顺序收进技能库。公开仓库不写入镜像仓库密码和 Cursor API 密钥。

## 验证

- `python scripts/update_catalog.py`：通过，目录更新为 8 个 skill、5 个一级分类。
- `python scripts/update_catalog.py --check`：通过。
