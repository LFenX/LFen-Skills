# Clause Context: T-REVIEW-SCOPE-20261028-001 / run_started

- Status: `Expanded`
- Query digest: `195131bf2da4eb0d9f45d715d383af5d3b4242e63c1dc8694ecfdc940b6a3656`
- Index digest: `b5a5c6ecc8dc73772c89ea27e2b834eb72653122ce824da44ccdadb275fe22a3`
- Coverage: `9/9`
- Budget: `9765/12000` chars
- Fallback: `section`

## Source Index

- `C07`: `references/02_核心规范/C07_Human_Agent_Collaboration_Standard.md` / `V6.3 Candidate` / SHA-256 `a1fc4e903d8b690f938d6e8fdf45a57abff2e94bcefbdb9729db1914804f016a`
- `C08`: `references/02_核心规范/C08_Agent_Context_Governance_Standard.md` / `V6.3 Candidate` / SHA-256 `262f2a190f130cb97955e58fca57d2216e2edf949d2f271413e5dff5d6faeb6d`
- `C09`: `references/02_核心规范/C09_Agent_Execution_and_Evidence_Standard.md` / `V6.3 Candidate` / SHA-256 `6897694e362bf48cb3a13bb4e68d79d7173945daad2ba3e8f0b6c75be944c01e`
- `C12`: `references/02_核心规范/C12_Review_Quality_Gate_and_Product_Health_Standard.md` / `V6.3 Candidate` / SHA-256 `508ab6263bb1db5b1568cb16233ce7413a51da2f73bbe9eb39a56c9ad08d5565`
- `C05`: `references/02_核心规范/C05_Acceptance_Verification_and_Validation_Standard.md` / `V6.3 Candidate` / SHA-256 `7973bcb4ea442030772e36b7418cc1e03f55e0b3aaa6072f4ec1c198d1b537c7`
- `C10`: `references/02_核心规范/C10_Decision_Traceability_and_Lineage_Standard.md` / `V6.3 Candidate` / SHA-256 `0eba391e52d509b37f7e6882b631729627eee8d27a887ccf391c58cc8e6a7534`

> 完整 lane rank 和逐条来源字段保存在同目录 `query-result.json`。

## Citations

### 1. C07 — C07 人机协作与责任规范 > 5. 规范性用语 > 5.3 规则优先级

- `P0` · Locator `C07:a1fc4e90:38ee3d27:76:69e5d4b3` · Lines `106-106`

```text
5. 本规范已批准或已基线版本中的“必须”“禁止”及第 10.17 节例外边界；
```

### 2. C07 — C07 人机协作与责任规范 > 5. 规范性用语 > 5.3 规则优先级

- `P0` · Locator `C07:a1fc4e90:38ee3d27:80:c42e79ef` · Lines `110-110`

```text
9. Agent 生成的建议、推断或默认行为。
```

### 3. C07 — C07 人机协作与责任规范 > 5. 规范性用语 > 5.3 规则优先级

- `P0` · Locator `C07:a1fc4e90:38ee3d27:81:ae1605be` · Lines `112-112`

```text
同一优先级冲突、来源有效性不明或无法判断适用范围时，必须停止受影响操作并按 ESP 升级。Agent 禁止自行选择更宽权限的解释。
```

### 4. C07 — C07 人机协作与责任规范 > 8. 治理对象与关系 > 8.0 V6.3 TaskContract 权限边界

- `P0` · Locator `C07:a1fc4e90:9063a02e:152:4c41b9ee` · Lines `207-207`

```text
“我被允许做什么”属于任务执行前输入，必须进入 TaskContract 的 `authority`、`scope`、`required_gates` 和 `stop_conditions`，不得等待任务结束后补写。Run 开始时这些字段冻结；后续权限扩大、范围变化或新 Gate 必须先停止受影响动作，并通过带 Authority 依据的 Amendment 修订。
```

### 5. C08 — C08 Agent 上下文治理规范 > 5. 规范性用语与受控判定 > 5.4 规则优先级

- `P0` · Locator `C08:262f2a19:416d3219:103:b1aad2c4` · Lines `138-138`

```text
高优先级 Context 失效时必须排除并报告，禁止退而使用其过期版本。相同优先级或不同事实源存在语义冲突时，禁止仅按时间戳、文件名、搜索排名或出现次数自动解决。
```

### 6. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:353:c80124a4` · Lines `476-476`

```text
8. 解析失败、内容截断、编码异常、OCR 不确定或附件版本不明时必须报告，不得静默补写。
```

### 7. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:322:d81d2e63` · Lines `434-434`

```text
1. Delete、Deploy、External Mutation、生产操作、权限变化、不可逆操作和 High/Critical Risk Action 至少为 Approval Required；Prohibited 仍禁止。
```

### 8. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:325:f5a1c28d` · Lines `437-437`

```text
4. 执行前必须记录 Before Snapshot、影响范围、可恢复性、备份/回滚、幂等策略、观察窗口和验证。
```

### 9. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:327:c4bf94d5` · Lines `439-439`

```text
6. Deploy 必须引用 C11 Release Configuration、C12 Gate/Approval、窗口、监测、回滚和 Owner。
```

### 10. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:328:befa9592` · Lines `440-440`

```text
7. “清理”“修复”“格式化”“回滚”“恢复”不得扩大批准目标。
```

### 11. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:329:48963d8d` · Lines `441-441`

```text
8. Retry 高影响 Action 前必须先确认上次 Attempt 的外部副作用和幂等状态。
```

### 12. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:331:0e9a1176` · Lines `443-443`

```text
10. 操作后必须验证 Actual Effect；只有命令成功但目标状态未知时为 Blocked。
```

### 13. C12 — C12 评审、质量门禁与产品健康规范 > 2. 目的

- `P0` · Locator `C12:508ab626:28e7276d:36:af7a1d0d` · Lines `45-45`

```text
10. 使 Agent 和自动化工具可以计算、检查和起草，但不能自批高风险输出或风险接受；
```

### 14. C12 — C12 评审、质量门禁与产品健康规范 > 5. 规范性用语与受控判定 > 5.1 中文关键词

- `P0` · Locator `C12:508ab626:e1e3a126:100:edb98f49` · Lines `127-127`

```text
“必须、禁止、应、不应、可以、可选”直接适用 VC-PPG-COM-001 的规范性用语定义；唯一语义以该公共基线为准，本文件不得复制或改写。
```

### 15. C12 — C12 评审、质量门禁与产品健康规范 > 5. 规范性用语与受控判定 > 5.1 中文关键词

- `P0` · Locator `C12:508ab626:e1e3a126:101:6775b219` · Lines `129-129`

```text
“必须”和“禁止”规则不得通过普通 EWR 绕过。法律、监管、合同、Safety、Security、Privacy、不可逆数据和明确 Non-waivable Gate 项不得豁免。
```

### 16. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:323:8502f895` · Lines `435-435`

```text
2. 目标必须解析为精确仓库、路径、资源、记录、租户、账户、环境和版本。
```

### 17. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:324:2a399565` · Lines `436-436`

```text
3. 工作区根、用户主目录、系统根、整个账户/租户、未解析变量、宽泛通配符或计算后未复核目标禁止作为破坏性 Target。
```

### 18. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:326:32ce4083` · Lines `438-438`

```text
5. External Mutation 必须使用服务支持的 Idempotency Key 或记录不可幂等及补偿措施。
```

### 19. C09 — C09 Agent 执行与证据规范 > 10. 强制规则 > 10.8 高影响、破坏性与外部操作

- `P0` · Locator `C09:6897694e:47ee626b:330:7404e213` · Lines `442-442`

```text
9. 删除或覆盖前必须识别用户已有、未提交、未跟踪和并行 Agent 变化；未知时 Stop。
```

### 20. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:346:bfe312a1` · Lines `469-469`

```text
1. Attachment 必须记录文件名、媒体类型、大小、Source Owner、上传时间、Digest、Access 和用途。
```

### 21. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:352:17878c15` · Lines `475-475`

```text
7. Summary 禁止替代 Normative Source；如用于辅助，必须标记 Derived、Coverage、Omission 和生成者。
```

### 22. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:348:83b980eb` · Lines `471-471`

```text
3. OCR、Parser、Converter、Translator、Summarizer 和 Chunker 必须记录工具/版本、参数、输入、输出、范围、错误和遗漏。
```

### 23. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:349:effe49e0` · Lines `472-472`

```text
4. Retrieval 必须记录 Query、Corpus/Index Snapshot、Filter、检索时间、候选、选择依据、未选项和 Source Locator。
```

### 24. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.12 Attachment、Retrieval 与 Transformation

- `P0` · Locator `C08:262f2a19:a5c224ba:351:b8e85ec4` · Lines `474-474`

```text
6. Chunk 必须可定位回原 Source 范围；跨 Source 拼接必须保留每段 Provenance。
```

### 25. C09 — C09 Agent 执行与证据规范 > 7. 角色与职责

- `P1` · Locator `C09:6897694e:95fdca46:134:7d49ca91` · Lines `180-180`

```text
高风险 Run 的 Agent、Validation Executor、Independent Reviewer、Human Review Authority 和 Risk Acceptance Authority 必须执行 C07/C12 规定的职责分离。
```

### 26. C05 — C05 验收、验证与确认规范 > 10. 强制规则 > 10.16 Coverage 与 Acceptance Gate

- `P1` · Locator `C05:7973bcb4:454bead4:345:2c4368fc` · Lines `501-501`

```text
### 10.16 Coverage 与 Acceptance Gate
```

### 27. C10 — C10 决策、追踪与资产血缘规范 > 10. 强制规则 > 10.4 Decision Authority 与生效

- `P1` · Locator `C10:0eba391e:8a23fa35:273:cd4d0077` · Lines `378-378`

```text
1. DEC Author、Owner、Participants 和 Decision Authority 必须分别记录。
```

### 28. C07 — C07 人机协作与责任规范 > 7. 参与者与职责 > 7.1 人类角色

- `P1` · Locator `C07:a1fc4e90:87f4049d:125:dda8e57a` · Lines `170-170`

```text
| Authorization Owner | 根据 Authority Source 建立、收缩、撤销 Agent Authorization | 不得授予自身不具备的 Authority |
```

### 29. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.3 Source、Authority 与 Owner

- `P2` · Locator `C08:262f2a19:25ef3380:259:428a210e` · Lines `353-353`

```text
4. Authority Instruction 必须验证人类身份、Authority、Scope、时间和 C07 Authorization。
```

### 30. C07 — C07 人机协作与责任规范 > 10. 强制规则 > 10.3 Authority、Authorization、Permission 与 Approval

- `P2` · Locator `C07:a1fc4e90:c675f0aa:258:488e4c05` · Lines `356-356`

```text
1. Authority 必须有来源、适用对象、决定类型、环境和有效期。
```

### 31. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.3 Source、Authority 与 Owner

- `P2` · Locator `C08:262f2a19:25ef3380:257:0b9df886` · Lines `351-351`

```text
2. Source Authority Level 是该来源可提供的最高资格，具体 Context 不得高于来源上限。
```

### 32. C10 — C10 决策、追踪与资产血缘规范 > 10. 强制规则 > 10.4 Decision Authority 与生效

- `P2` · Locator `C10:0eba391e:8a23fa35:277:1d077b40` · Lines `382-382`

```text
5. 口头、聊天或 Tool Result 只有被捕获为受控 Evidence 并由 Authority 确认后才能支持 Decision。
```

### 33. C10 — C10 决策、追踪与资产血缘规范 > 10. 强制规则 > 10.4 Decision Authority 与生效

- `P3` · Locator `C10:0eba391e:8a23fa35:272:2c912aee` · Lines `376-376`

```text
### 10.4 Decision Authority 与生效
```

### 34. C07 — C07 人机协作与责任规范 > 10. 强制规则 > 10.3 Authority、Authorization、Permission 与 Approval

- `P3` · Locator `C07:a1fc4e90:c675f0aa:254:a4a0ef4c` · Lines `348-348`

```text
### 10.3 Authority、Authorization、Permission 与 Approval
```

### 35. C07 — C07 人机协作与责任规范 > 10. 强制规则 > 10.3 Authority、Authorization、Permission 与 Approval

- `P3` · Locator `C07:a1fc4e90:c675f0aa:256:49cc3fcb` · Lines `352-352`

```text
`Capability ⊇ Technical Permission ⊆ Formal Authorization ⊆ Human Authority`
```

### 36. C08 — C08 Agent 上下文治理规范 > 10. 强制规则 > 10.3 Source、Authority 与 Owner

- `P3` · Locator `C08:262f2a19:25ef3380:252:0ccc3a2c` · Lines `342-342`

```text
### 10.3 Source、Authority 与 Owner
```

### 37. C07 — C07 人机协作与责任规范 > 10. 强制规则 > 10.3 Authority、Authorization、Permission 与 Approval

- `P3` · Locator `C07:a1fc4e90:c675f0aa:257:5e73b6f1` · Lines `354-354`

```text
特定 Approval 只能在 Formal Authorization 和 Human Authority 内放行准确动作，不能扩大其边界。
```

> 此文件是 DerivedView。检索定位符不是规范正文的正式 Clause ID，召回命中不构成授权、批准或 Gate Outcome。
