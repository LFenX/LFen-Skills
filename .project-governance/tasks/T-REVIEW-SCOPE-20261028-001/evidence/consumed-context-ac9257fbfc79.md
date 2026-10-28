# Clause Context: T-REVIEW-SCOPE-20261028-001 / edit_in_scope

- Status: `Complete`
- Query digest: `ac9257fbfc79b514c2fdc977dec48485b51427bc78d9825ae4a0d0447d165ec8`
- Index digest: `b5a5c6ecc8dc73772c89ea27e2b834eb72653122ce824da44ccdadb275fe22a3`
- Coverage: `5/5`
- Budget: `11879/12000` chars
- Fallback: `none`

## Source Index

- `C09`: `references/02_核心规范/C09_Agent_Execution_and_Evidence_Standard.md` / `V6.3 Candidate` / SHA-256 `6897694e362bf48cb3a13bb4e68d79d7173945daad2ba3e8f0b6c75be944c01e`
- `C12`: `references/02_核心规范/C12_Review_Quality_Gate_and_Product_Health_Standard.md` / `V6.3 Candidate` / SHA-256 `508ab6263bb1db5b1568cb16233ce7413a51da2f73bbe9eb39a56c9ad08d5565`
- `C11`: `references/02_核心规范/C11_Configuration_Version_Baseline_and_Change_Standard.md` / `V6.3 Candidate` / SHA-256 `88ec56f78f6d3da6f94b1684c7b1296ed1825bfcc961f0f8d3636c8c6a26f7e1`
- `C07`: `references/02_核心规范/C07_Human_Agent_Collaboration_Standard.md` / `V6.3 Candidate` / SHA-256 `a1fc4e903d8b690f938d6e8fdf45a57abff2e94bcefbdb9729db1914804f016a`

> 完整 lane rank 和逐条来源字段保存在同目录 `query-result.json`。

## Citations

### 1. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:322:d81d2e63` · Lines `434-434`

```text
1. Delete、Deploy、External Mutation、生产操作、权限变化、不可逆操作和 High/Critical Risk Action 至少为 Approval Required；Prohibited 仍禁止。
```

### 2. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:325:f5a1c28d` · Lines `437-437`

```text
4. 执行前必须记录 Before Snapshot、影响范围、可恢复性、备份/回滚、幂等策略、观察窗口和验证。
```

### 3. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:327:c4bf94d5` · Lines `439-439`

```text
6. Deploy 必须引用 C11 Release Configuration、C12 Gate/Approval、窗口、监测、回滚和 Owner。
```

### 4. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:328:befa9592` · Lines `440-440`

```text
7. “清理”“修复”“格式化”“回滚”“恢复”不得扩大批准目标。
```

### 5. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:329:48963d8d` · Lines `441-441`

```text
8. Retry 高影响 Action 前必须先确认上次 Attempt 的外部副作用和幂等状态。
```

### 6. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:331:0e9a1176` · Lines `443-443`

```text
10. 操作后必须验证 Actual Effect；只有命令成功但目标状态未知时为 Blocked。
```

### 7. C12 — C12 评审、质量门禁与产品健康规范 > 2. 目的

- `P0` · Locator `C12:508ab626:28e7276d:36:af7a1d0d` · Lines `45-45`

```text
10. 使 Agent 和自动化工具可以计算、检查和起草，但不能自批高风险输出或风险接受；
```

### 8. C12 — C12 评审、质量门禁与产品健康规范 > 5. 规范性用语与受控判定 > 5.1 中文关键词

- `P0` · Locator `C12:508ab626:e1e3a126:100:edb98f49` · Lines `127-127`

```text
“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。
```

### 9. C12 — C12 评审、质量门禁与产品健康规范 > 5. 规范性用语与受控判定 > 5.1 中文关键词

- `P0` · Locator `C12:508ab626:e1e3a126:101:6775b219` · Lines `129-129`

```text
“必须”和“禁止”规则不得通过普通 EWR 绕过。法律、监管、合同、Safety、Security、Privacy、不可逆数据和明确 Non-waivable Gate 项不得豁免。
```

### 10. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:323:8502f895` · Lines `435-435`

```text
2. 目标必须解析为精确仓库、路径、资源、记录、租户、账户、环境和版本。
```

### 11. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:324:2a399565` · Lines `436-436`

```text
3. 工作区根、用户主目录、系统根、整个账户/租户、未解析变量、宽泛通配符或计算后未复核目标禁止作为破坏性 Target。
```

### 12. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:326:32ce4083` · Lines `438-438`

```text
5. External Mutation 必须使用服务支持的 Idempotency Key 或记录不可幂等及补偿措施。
```

### 13. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:330:7404e213` · Lines `442-442`

```text
9. 删除或覆盖前必须识别用户已有、未提交、未跟踪和并行 Agent 变化；未知时 Stop。
```

### 14. C11 — C11 配置、版本、基线与变更控制规范 > 8. 正式产物与唯一事实源 > 8.0 V6.3 三阶段修订与生成边界

- `P1` · Locator `C11:88ec56f7:0c539819:172:3b2cf7dd` · Lines `227-227`

```text
RunLedger 只追加；更正通过新 Event 引用原 Event。ProjectState 和 DerivedView 由生成器重建，禁止直接编辑或纳入独立变更源。Git Commit/Diff 可作为代码和文档变化的权威证据，但外部副作用、失败、验证环境、批准和决定必须由相应元类型或 AuthorityAsset 保存。
```

### 15. C07 — C07 人机协作与责任规范 > 7. 参与者与职责 > 7.2 Agent 角色

- `P1` · Locator `C07:a1fc4e90:63ef8775:140:08fad459` · Lines `189-189`

```text
| Orchestrator Agent | 在授权范围内分解任务、分派子任务、收集结果和报告冲突 | 子 Agent 授权不得超过自身授权与子任务 Scope 的交集 |
```

### 16. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.6 Tool 与权限

- `P1` · Locator `C09:6897694e:d3202194:293:71561ebf` · Lines `398-398`

```text
5. 未知版本、未知 Identity、未知租户、未知数据保留或未知副作用的 Tool 不得用于高风险 Action。
```

### 17. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.6 Tool 与权限

- `P2` · Locator `C09:6897694e:d3202194:294:1da2eb1f` · Lines `399-399`

```text
6. Dry Run 只有在工具官方语义明确且未产生真实副作用时才能记录为 Dry Run；名称包含 `dry-run` 不构成证明。
```

### 18. C09 — C09 Agent 执行与证据规范 > 12. V6.3 必需载体与条件 Profile

- `P2` · Locator `C09:6897694e:0a9756f4:488:e528a9f5` · Lines `652-652`

```text
| RunLedger / `run.jsonl` | 每个实际 Run；无事件时允许空文件 | RUN、重要 TIL、失败、重试、验证、外部副作用和回滚事件 |
```

### 19. C09 — C09 Agent 执行与证据规范 > 9. 生命周期与工作机制 > 9.7 Failure、Retry 与 Rollback

- `P2` · Locator `C09:6897694e:00fcee58:229:a4dd6a88` · Lines `313-313`

```text
任一 Failed/Blocked、非预期副作用、Stop、验证失败或证据缺失必须建立 FER。Retry 或 Rollback 只能在副作用、权限、Plan、风险和新鲜 Context 可判定时执行。
```

### 20. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.1 Run 身份与边界

- `P2` · Locator `C09:6897694e:27fd4d8d:236:f501bc1a` · Lines `327-327`

```text
1. 每次 Agent Run 必须创建唯一 RUN ID，格式为 `RUN-<NNNN>`。
```

### 21. C07 — C07 人机协作与责任规范 > 10. 强制规则 > 10.6 Autonomous 操作

- `P2` · Locator `C07:a1fc4e90:c8a022bf:291:234366cb` · Lines `402-402`

```text
7. 操作可审计，且不会产生未声明的外部副作用；
```

### 22. C09 — C09 Agent 执行与证据规范 > 19. 符合性检查 > 19.2 强制检查项

- `P2` · Locator `C09:6897694e:4fe40d94:770:ff3aba72` · Lines `1018-1018`

```text
18. Tool 默认行为、缓存、重试和副作用是否可知；
```

### 23. C09 — C09 Agent 执行与证据规范 > 20. 附录 > 20.13 Retry 与 Rollback 判定表

- `P2` · Locator `C09:6897694e:e0e42fcb:854:fe53c231` · Lines `1320-1320`

```text
| RUN 已终端 | 建立新 RUN | 新 RUN 中授权 | 回链原 RUN |
```

### 24. C09 — C09 Agent 执行与证据规范 > 7. 角色与职责

- `P2` · Locator `C09:6897694e:95fdca46:125:7356df63` · Lines `170-170`

```text
| Run Controller / Orchestrator | 分配 Run/子 Run、维护顺序、共享写入和停止协调 | 不得向子 Agent 授予自身没有的权限 |
```

### 25. C09 — C09 Agent 执行与证据规范 > 19. 符合性检查 > 19.2 强制检查项

- `P2` · Locator `C09:6897694e:4fe40d94:793:27098503` · Lines `1041-1041`

```text
41. Retry 是否创建新 Attempt 并检查副作用/幂等；
```

### 26. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.3 RUN Completed 条件

- `P2` · Locator `C09:6897694e:4d4144f4:651:47736d43` · Lines `857-857`

```text
只有全部满足时 RUN 可以进入 Completed：
```

### 27. C11 — C11 配置、版本、基线与变更控制规范 > 10. 配置、版本、基线与变更控制规则 > 10.9 Impact Analysis

- `P2` · Locator `C11:88ec56f7:2470b427:382:c81a8d3c` · Lines `519-519`

```text
5. 数据删除、Schema 迁移、密钥轮换、模型变化和 Feature Flag 必须评估不可逆副作用；
```

### 28. C09 — C09 Agent 执行与证据规范 > 14. 质量要求

- `P2` · Locator `C09:6897694e:0d3fa301:617:e3bea0af` · Lines `815-815`

```text
6. 原子：副作用、权限和失败不可分时拆分 Action/TIL；
```

### 29. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.2 RUN Ready 条件

- `P2` · Locator `C09:6897694e:e35baeb1:640:c15bfa97` · Lines `843-843`

```text
只有全部满足时 RUN 可以进入 Ready：
```

### 30. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.3 RUN Completed 条件

- `P2` · Locator `C09:6897694e:4d4144f4:650:41d43d96` · Lines `855-855`

```text
### 15.3 RUN Completed 条件
```

### 31. C07 — C07 人机协作与责任规范 > 2. 目的

- `P2` · Locator `C07:a1fc4e90:c77e3c5d:30:307cd56b` · Lines `39-39`

```text
5. 使高影响、不可逆、破坏性、跨 Scope、安全、隐私、合规、生产和外部副作用操作获得有权人类批准；
```

### 32. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.4 RUN Accepted 条件

- `P2` · Locator `C09:6897694e:d5731510:661:6238bc88` · Lines `870-870`

```text
### 15.4 RUN Accepted 条件
```

### 33. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.5 Step、Action 与 Attempt

- `P2` · Locator `C09:6897694e:e40e94e8:281:25e39cb3` · Lines `384-384`

```text
2. 每个 Action 只承担一个可独立判定授权、副作用和结果的 Operation。
```

### 34. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.2 RUN Ready 条件

- `P2` · Locator `C09:6897694e:e35baeb1:639:feb6ae36` · Lines `841-841`

```text
### 15.2 RUN Ready 条件
```

### 35. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.1 Run 身份与边界

- `P2` · Locator `C09:6897694e:27fd4d8d:240:60645040` · Lines `331-331`

```text
5. RUN 必须绑定一个主要 Task/交付目标；无关工作建立新 Run。
```

### 36. C09 — C09 Agent 执行与证据规范 > 19. 符合性检查 > 19.2 强制检查项

- `P2` · Locator `C09:6897694e:4fe40d94:806:76d821d4` · Lines `1054-1054`

```text
54. 是否能重建主要副作用、TaskContract Revision、Diff 和验证；
```

### 37. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.3 RUN Completed 条件

- `P2` · Locator `C09:6897694e:4d4144f4:659:92f7e6dd` · Lines `866-866`

```text
- 未发生未记录副作用或 Evidence 缺口。
```

### 38. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.4 RUN Accepted 条件

- `P2` · Locator `C09:6897694e:d5731510:662:1c1a2862` · Lines `872-872`

```text
RUN 从 Completed 转为 Accepted 必须同时满足：
```

### 39. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.7 命令规范

- `P2` · Locator `C09:6897694e:824cdbf7:317:d95f8e3a` · Lines `427-427`

```text
6. 复合命令若任一部分具有副作用、独立权限或独立失败条件，必须拆分 Action/TIL。
```

### 40. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.2 RUN Ready 条件

- `P2` · Locator `C09:6897694e:e35baeb1:641:e0261fc0` · Lines `845-845`

```text
- AEP 为 Approved/Baselined 且绑定当前 RUN；
```

### 41. C09 — C09 Agent 执行与证据规范 > 6. 术语与定义

- `P2` · Locator `C09:6897694e:041c2647:115:f6c81857` · Lines `156-156`

```text
| Run Completion | Run 已结束计划动作并记录全部结果 | 对应 RUN Completed/Failed/Cancelled，不表示接受 |
```

### 42. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.13 Failure、Stop 与 Retry

- `P2` · Locator `C09:6897694e:7c53d277:379:a3f5a43c` · Lines `501-501`

```text
7. 非幂等或副作用未知的 Action 禁止自动 Retry。
```

### 43. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.1 Run 身份与边界

- `P2` · Locator `C09:6897694e:27fd4d8d:241:ba1e354d` · Lines `332-332`

```text
6. Parent/Child Run 必须分别具有 RUN ID、Scope、Agent Instance、Authorization、ECP Revision 和交接。
```

### 44. C09 — C09 Agent 执行与证据规范 > 8. 治理对象与关系 > 8.0 V6.3 最小执行记录覆盖规则

- `P2` · Locator `C09:6897694e:b1dd146f:139:d80c7578` · Lines `189-189`

```text
2. RUN 与 TIL 语义进入只追加 RunLedger（`run.jsonl`）。普通读取、目录查看、搜索和未产生重要结果的无副作用调用不记录。
```

### 45. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.5 阻断条件

- `P2` · Locator `C09:6897694e:434e9ab2:672:ab22d9cf` · Lines `886-886`

```text
- Run/Step/Action/Attempt 身份缺失或复用；
```

### 46. C07 — C07 人机协作与责任规范 > 9. 生命周期与工作机制 > 9.3 Boundary and Risk Review

- `P2` · Locator `C07:a1fc4e90:509cf2df:208:9a9a77d5` · Lines `283-283`

```text
4. 确认目标对象、环境、版本、最大修改范围和外部副作用。
```

### 47. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.7 命令规范

- `P2` · Locator `C09:6897694e:824cdbf7:320:956657f2` · Lines `430-430`

```text
9. 命令可重放记录不构成再次执行授权；重放前必须重新核验 Authorization、Context、Snapshot、Risk 和副作用。
```

### 48. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.3 RUN Completed 条件

- `P2` · Locator `C09:6897694e:4d4144f4:660:fde59ac6` · Lines `868-868`

```text
验证 Action 已按计划执行但 Verification Result = Fail 时，Run 动作可以 Completed，但不能伪装为成功交付；RUN State 必须依据实际完成条件记录为 Completed、Failed 或 Blocked。
```

### 49. C11 — C11 配置、版本、基线与变更控制规范 > 6. 术语与定义

- `P2` · Locator `C11:88ec56f7:7b574ff8:135:f0d09366` · Lines `178-178`

```text
| Rollback | 将当前系统或资产变更到一个先前已知配置的受控变更；不保证外部副作用或数据自动恢复 |
```

### 50. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.1 Run 身份与边界

- `P2` · Locator `C09:6897694e:27fd4d8d:237:a3124f3b` · Lines `328-328`

```text
2. RUN ID 禁止复用；终止、失败、重启、恢复或不同 Agent Instance 不得覆盖原 RUN。
```

### 51. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.6 Tool 与权限

- `P2` · Locator `C09:6897694e:d3202194:292:80041ed7` · Lines `397-397`

```text
4. Tool 自动重试、缓存、会话记忆、插件、扩展、默认工作目录和外部副作用必须可知。
```

### 52. C09 — C09 Agent 执行与证据规范 > 15. 评审、批准与 Run 接受 > 15.3 RUN Completed 条件

- `P2` · Locator `C09:6897694e:4d4144f4:655:1115c89b` · Lines `862-862`

```text
- 需要审核或 Gate 时 VDR DerivedView 已形成；
```

> 此文件是 DerivedView。检索定位符不是规范正文的正式 Clause ID，召回命中不构成授权、批准或 Gate Outcome。
