# 修复 before.json 修订历史重复膨胀

- 变更时间：2026-10-23 15:48（Asia/Shanghai，UTC+8）。
- 用户原话：我看最近的before文档产生了近8000行，这看起来是一个严重的bug
- 涉及文件：`skills/product-engineering/run-governed-product-workflow/scripts/governance_artifacts.py`、`scripts/amend_record.py`、`scripts/self_test.py`、`commands/run.md`（均相对于技能目录），以及本日志。

## 可核对事实与原因

- 仓库中 `.project-governance/tasks/T-CATALOG-20260903-002/before.json` 为 8350 行、revision 18，含 17 条 Amendment。
- `amendments` 的独立缩进序列化占 7447 行；其中 8 条 `tailoring_resolution` 修订合计 6961 行。根因是派生裁剪结果反复以完整 `old_value` / `new_value` 写入修订历史。
- 当前 `_refresh_tailoring_after_amendment` 在真实修订后仍为派生结果再加修订；单字段和批量修订也未跳过同值输入。该行为与已有 `refresh_derived_tailoring` 的“派生视图刷新不属于契约修订”语义不一致。
- 新增回归用例在修复前真实失败：`SelfTestFailure: an unchanged amendment rewrote the contract`。

## 修复范围

- 派生裁剪结果继续刷新当前快照，不再新增 Amendment 或增加修订号；直接修订该派生字段时提示使用现有刷新入口。
- 同值单字段及全同值批量操作不写文件、不增修订；混合批量只记录真实字段变更，保留真实变更的新旧值、原因及依据。
- 无变化路径仍执行结构及语义校验；JSON 布尔值与数字不会被当成相同输入；不可变字段、无效批量和失败原子性继续校验。
- CLI 对同值操作输出 `UNCHANGED`。沿用已有目录、命名和 JSON 载体；未迁移或压缩既有审计历史。

## 实际验证

- `run_amendment_growth_fixture()`：22 项检查通过，包括真实新旧值、修订数量、旧历史保全、批量原子性、字段类型与不可变约束、派生字段入口及 CLI 行为。
- 同一隔离任务模型对照实测：

| 操作 | 修复前安装版本 | 修复后工作区版本 |
|---|---:|---:|
| 新建任务行数 | 772 | 772 |
| 12 次同值操作后行数 | 941 | 772 |
| 同值操作新增修订 | 12 | 0 |
| 再做 6 次真实风险字段修改后行数 | 5381 | 833 |
| 6 次真实修改新增修订 | 12 | 6 |
| 派生结果新增历史条数 | 6 | 0 |

- 完整 `self_test.py --project-root <当前仓库>`：退出码 0；正反向测试通过，包括 40 项历史证明兼容、16 项验证补录、22 项增长回归等既有控制。
- 受保护运行资产一致性与查询契约审计通过；新增行为未改变 CLI 参数契约。
- 原 8350 行文件内容与 HEAD 相同，文件 SHA-256 为 `0ae867c224df53439f74c2b2583810659c3d0affaffde7ff76a9a6a90b1edf19`；修复对后续修订生效。
- 本次未执行旧历史压缩或迁移；未记录新的人的 Acceptance，待交付后真实确认。
