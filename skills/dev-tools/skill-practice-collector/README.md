# Skill Practice Collector

集中式 Skill 实践数据采集平台。该目录是独立的 Web 服务，不属于任何单一 Skill，也不负责修改 Skill。

## 已冻结边界

- 使用 Node.js / npm 部署，单台内网服务器。
- 使用 PostgreSQL 保存原始事件、规范化事件、聚合指标和人工维护的发现记录。
- 采集器接收用户原文、澄清过程、需求条目、计划步骤、实际执行步骤、验证证据、重试链和产物指标。
- 不上传源码，不保存来源 IP；发送方使用稳定的脱敏标识。
- 历史任务只读兼容解析，不改写原始账本。
- 采集客户端使用本地 outbox、批量 gzip POST、幂等键和失败补传。
- 不提供自动优化、自动改写 Skill、自动提交代码或自动发布功能。
- 优化只能由人员根据采集结果手动发起，并重新走受控开发流程。

## 任务拆分

### Task 1：独立服务蓝图与事件契约（当前任务）

产出目录边界、服务分层、Canonical Event 草案、接口边界、数据保留和验收规则。

验收：蓝图明确采集器与 Skill 的依赖方向；明确采集内容、排除内容、幂等策略和人工优化边界。

### Task 2：现有 Skill 事件账本正确性修复

修复并发追加、事件唯一性、重复 `run_started`、跨时区时间排序、RFC3339 校验和 JSON Schema 运行时校验。

验收：并发和非法输入反向测试通过；既有 `self_test.py` 继续通过；Full 与 Minimal 账本语义可统一读取。

### Task 3：统一 Canonical Event 与本地采集客户端

在不上传源码的前提下，增加阶段、耗时、等待、失败分类、阻断分类、重试原因、计划/执行步骤和产物指标；提供一个低开销的 outbox 批量发送脚本。

验收：一个任务可以由单个脚本完成采集、压缩、发送、幂等重试和离线补传。

### Task 4：PostgreSQL 服务端与批量 POST API

使用 npm/Node.js 实现数据库模型、迁移、批量接收、幂等去重、事件规范化和原始事件不可变存储。

验收：重复批次不重复入库；非法事件被逐条拒收并返回 `request_id`；服务不可用时客户端不丢数据。

### Task 5：监控台 UI 与指标聚合

实现任务总览、阶段耗时、卡点、失败/重试链、流程控制有效性、版本对比和数据质量页面。

验收：页面可以按 Skill、版本、项目、阶段和时间范围检索，并能回到原始事件证据。

### Task 6：历史兼容、试采和生产验收

解析既有治理任务，接入 10～20 个真实任务，验证采集覆盖率、事件完整性、指标可计算性和隐私边界。

验收：形成试采报告；未达到数据质量门槛时停止推广，不自动修改 Skill。

## 服务分层

```text
Skill / 其他生产工具
        ↓ HTTP 契约
轻量客户端与本地 outbox
        ↓ 批量 gzip POST
Ingest API
        ↓
Raw Event（不可变）
        ↓
Canonical Event / Task Evidence
        ↓
Aggregates / Findings
        ↓
只读监控台
```

未来接入其他 Skill 时，只增加 `adapters/<skill-name>`，不修改核心存储、聚合和 UI。

## 接口边界

```http
POST /api/v1/ingest/events
Content-Type: application/json
Content-Encoding: gzip
Authorization: Bearer <producer-token>
Idempotency-Key: <batch-id>
```

响应使用统一业务包：

```json
{
  "data": {"accepted": 1, "duplicate": 0, "rejected": 0},
  "meta": {"request_id": "req_...", "server_time": "..."}
}
```

采集器前端不配置或展示 POST 地址；服务地址只存在于发送脚本或部署配置中。

## Canonical Event 最小字段

```text
event_id, task_id, run_id, attempt_id, sequence
skill_name, skill_version, producer_id_hash, project_id_hash
stage, event_type, status, occurred_at, duration_ms, wait_ms
failure_class, error_code, blocker_code, retry_reason
request_snapshot_ref, requirement_ref, plan_step_ref, execution_step_ref
artifact_refs, metrics, payload
```

`payload` 允许保存用户原文、澄清问答和计划/执行文本；源码、凭据和来源 IP 不进入 payload。

## 采集边界

采集器只保存可追溯的事实和来源，不生成 `Compliant`、`Non-compliant` 或 `Unknown` 结论，也不创建优化任务。人员可在后续监控台或分析工具中自行解释这些事实，并手动发起新的 Skill 维护任务。

阶段耗时和等待时间只接受任务记录明确报告的数值，或 `measure` 子命令实际测得的数值；缺失时记录 `unavailable`，不按两个时间戳的间隔猜测。原文按 UTF-8 原样保留，机器路径、来源 IP、源码和凭据不会进入事件。

## 客户端入口

客户端使用 Python 标准库，不要求在每个任务中追加人工记录：

```text
python client/cli.py sync --task-dir <task-dir> --outbox <local-outbox.db> [--endpoint <internal-api>]
python client/cli.py flush --outbox <local-outbox.db> --endpoint <internal-api>
python client/cli.py status --outbox <local-outbox.db>
python client/cli.py measure --task-dir <task-dir> --stage execution --step-id <id> -- <command>
```

`sync` 先把事件写入 SQLite outbox，再按需发送；网络失败不会删除数据。POST 请求体为 gzip 压缩的 `{data:{schema_version,batch_id,event_count,events}}`，`batch_id` 同时放在 `Idempotency-Key` 请求头。服务端必须逐条返回 `accepted`、`duplicate`、`rejected` 计数和 `meta.request_id`；拒收批次保留，需人工显式重放。

## 数据清理

数据默认持续保留。删除必须是人工主动操作，并记录清理范围、操作者、时间和原因。采集服务不自动清理历史数据。
