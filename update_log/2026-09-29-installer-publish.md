# 安装器修复发布

- 变更时间：2026-09-29 15:05（UTC+8）。
- 涉及文件：`install.ps1`、`install.sh`、`README.md`、`README.en.md`、`scripts/test_installers.py`、`.github/workflows/catalog.yml`、`update_log/2026-09-29-installer-fixes.md`、本日志。
- 变更摘要及原因：将安装器修复和单项 skill 一键安装命令发布至 `main`，使 README 中的远程命令获取新版安装器。发布前先并入远端新增 AICS skill 的提交，未改动该 skill。
- 发布提交：`1f1f2bd13470564895cd9cb6779c3c3fe30e3f77`；`git push origin main` 成功，`git ls-remote origin refs/heads/main` 返回同一提交。

## 验证

- 并入远端提交后，Windows 执行 `python -m unittest discover -s scripts -p 'test_*.py'`：27 项，26 项通过，1 项跳过，退出码 0。
- `python scripts/update_catalog.py --check`：通过，目录包含 8 个 skill。
- `git diff --check origin/main..HEAD`：通过（发布前）。
- 发布后读取 `https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1`：HTTP 200，响应中包含 `-Skill` 参数。
- 发布提交的 GitHub Actions：`Validate skill catalog` 与 `Skill gates` 均完成且结论为 `success`（运行 ID 分别为 `36534572818`、`36534572779`）。
