# 第一性原理执行规范

## 1. 目的

本规范把“第一性原理”转换为可检查的任务分析契约。它不要求固定篇幅；所有任务都应用同一推理结构，内容深度随风险、不可逆性和未知量缩放。

## 2. 权威依据

- [Stanford Encyclopedia of Philosophy：Aristotle’s Metaphysics](https://plato.stanford.edu/entries/aristotle-metaphysics/) 将第一哲学关联到最基本的原因、起点和原则；因此分析必须追溯到不可再由当前问题内其他主张推出的基础事实或约束。
- [GOV.UK Service Standard：Understand users and their needs](https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs) 要求基于研究证据理解用户及其目标，不能用未经验证的假设代替需要；因此“用户需要、事实、假设”必须分开记录。
- [NASA Systems Engineering Handbook：System Design Processes](https://www.nasa.gov/reference/4-0-system-design-processes/) 将利益相关方期望、技术需求、逻辑分解和设计解联系为可追踪转换；因此计划步骤必须能回溯到目标、基础要素和验收标准。
- [NASA Systems Engineering Handbook：Decision Analysis](https://www.nasa.gov/reference/6-8-decision-analysis/) 要求用明确标准系统评价备选方案；因此不能只写单一方案后宣称其最优。
- [NIST SP 800-160 Vol. 1 Rev. 1](https://www.nist.gov/publications/engineering-trustworthy-secure-systems) 采用系统工程视角建立可信系统；因此完整性、权限、证据和生命周期约束必须作为系统约束进入推导，而不是末尾补丁。

这些资料支持本 Skill 的方法设计，不替代项目规范、Authority、专业标准或具体领域证据。

## 3. 不可省略的推理链

每次问题拆解、方案制定和重大修订必须按以下顺序建立 `first_principles_analysis`：

1. **结果**：用可观察状态描述真正要改变什么，不把预设实现写成需要。
2. **事实**：只记录已有证据支持的陈述；每项绑定 `evidence_refs`。
3. **约束**：记录权限、范围、兼容、时间、规范、数据和不可逆边界；每项绑定 `source_refs`。
4. **假设**：记录尚未证实但暂用于推导的陈述，并给出验证方式。
5. **未知**：记录缺失信息、Owner、解除条件以及是否阻断；阻断未知在 S4 前必须关闭。
6. **基础要素**：从事实与约束中提取不可再分而仍保持业务意义的要素。
7. **因果链**：明确“基础要素为什么推出某个设计或控制”，证据不足时保持 Unknown。
8. **备选方案**：至少比较选定方案和保持现状；Medium 及以上还必须包含一个真实可行替代方案。
9. **决策标准**：直接来自目标、验收、约束和风险，不以习惯、流行度或个人偏好代替。
10. **推导计划**：每个计划步骤引用其基础要素和决策标准；无法追踪的步骤不得进入执行计划。
11. **验证**：验证结果是否满足原始结果和约束，而不是只证明任务步骤已执行。

## 4. 深度缩放

| 深度 | 适用条件 | 最低要求 |
|---|---|---|
| `Concise` | Low 且可逆、边界清晰 | 选定方案与保持现状；每步可追踪 |
| `Standard` | Medium 或涉及跨组件/正式记录 | 再增加一个可行替代方案和完整因果链 |
| `Deep` | High/Critical、不可逆、生产、安全/隐私、重大迁移 | 展开失效路径、独立复核点、回滚与残余风险 |

深度只缩放内容数量，不删除事实/约束/假设/未知/基础要素/因果链/备选方案/标准/计划追踪/验证这些控制目标。

## 5. 禁止项

- 禁止把假设、类比、惯例、工具输出或多数意见写成事实。
- 禁止先选技术方案，再倒推用户需要和验收标准。
- 禁止把任务列表当作问题拆解；步骤必须有因果和验收来源。
- 禁止提供虚假备选方案、虚假证据、虚假根因或无真实取舍的“推荐方案”。
- 禁止用“过去一直这样做”证明方案正确。
- 禁止在关键证据缺失时补写确定性结论。

## 6. 变更规则

新证据改变事实、约束、未知、方案或验收时，先修订 `first_principles_analysis`，再修订计划和 Tailoring Resolution。Run 开始后的修订必须通过 Amendment 保留历史。
