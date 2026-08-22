# minimal

Minimal 是同一六元模型的物理载体裁剪，不是第二套流程。

路径：脚本在 `<skill-root>/scripts/`；`<project-root>` 为含 `.project-governance` 的消费项目根，不是 skill 根。

## 资格

唯一事实源是 `VC-PPG-DEC-001 §16.4`。下表是它的人类可读投影，每行绑定 `schemas/minimal-task-record.schema.json` 中 `eligibility` 的受控字段；`self_test.py` 校验本表覆盖全部字段，投影与 schema 漂移时失败。

| 条件 | schema 字段 | 记录值 |
|---|---|---|
| C02 Risk 为 Low | `risk_level` | `Low` |
| 变化可逆且回退路径已记录 | `reversible` | `true` |
| 只有一个可独立验收的 Scope | `single_scope` | `true` |
| 无外部系统副作用 | `external_system_effect` | `false` |
| 无生产发布 | `production_release` | `false` |
| 无安全/隐私影响 | `security_privacy_impact` | `false` |
| E01–E05 全部 Inactive | `extension_triggers` | 五项均 `Inactive` |
| 无阻断 Unknown、权限扩大、独立复核 | `blocking_unknowns` | `[]` |
| 无专用 Gate | `special_gates` | `[]` |

九条**全部**成立才可用。任意一条不成立或为 Unknown，走完整载体——Unknown 不得当作 No。


若裁剪图显示 Change Surface 或 Delivery Scenario 会触发 E01-E05，初始化必须拒绝 Minimal 并改走完整载体；当前允许的 Minimal Change Surface 为 `UI/UX`、`API/Integration`、`Agent/Collaboration`。

`--selection-source explicit-user` 用于用户明确说“采用最轻框架”；`--selection-source automatic` 用于 agent 判定资格全部成立并告知默认采用 Minimal。

初始化。只需 §16.4 在 init 期要求的字段加基础 ID、Task Profile 三元和资格证据：

```console
python <skill-root>/scripts/manage_minimal_task.py init --project-root <project-root> --project-id <ProjectID> --work-item-id <WorkItemID> --task-id <TaskID> --ordinal <N> --objective <text> --scope <single-scope> --allowed-path <path> --acceptance <criterion> --delivery-scenario DS-03 --development-type DT-08 --change-surface UI/UX --selected-approach <approach> --alternative-rejected <rejected-alternative> --selection-source automatic --authority-ref <authority-ref> --eligibility-evidence-ref <risk-low-ref> --eligibility-evidence-ref <reversible-ref> --eligibility-evidence-ref <single-scope-ref> --eligibility-evidence-ref <no-external-effect-ref> --eligibility-evidence-ref <no-production-ref>
```

资格证据至少 5 条且互不相同，不设默认值：它是 Minimal 被允许的证明，编造默认等于伪造证据。

其余字段省略时由脚本写入带 `script default:` 前缀的可追溯值，并在 `selection.basis` 记录默认来源；需要时照常显式传入即可覆盖：`--plan-step`、`--verification`、`--basis`、`--fact`、`--fundamental`、`--causal-link`、`--decision-criterion`、`--out-of-scope`、`--forbidden-action`、`--assumption`、`--rollback`、`--constraint`

追加事件：

```console
python <skill-root>/scripts/manage_minimal_task.py append <project-root>/.project-governance/tasks/<TaskID> --event-type run_started --summary <summary> --status started
python <skill-root>/scripts/manage_minimal_task.py append <project-root>/.project-governance/tasks/<TaskID> --event-type mutation --summary <summary> --status recorded --evidence-ref <evidence-ref>
```

收尾：

```console
python <skill-root>/scripts/manage_minimal_task.py close <project-root>/.project-governance/tasks/<TaskID> --status Implemented --fact <fact> --change <change> --verification "Passed::<summary>::<evidence-ref>"
```

校验：

```console
python <skill-root>/scripts/manage_minimal_task.py validate --project-root <project-root> <project-root>/.project-governance/tasks/<TaskID>
```

升级：

```console
python <skill-root>/scripts/init_task.py --project-root <project-root> --project-id <ProjectID> --work-item-id <WorkItemID> --task-id <TaskID> --ordinal <N> --objective <text> --acceptance <criterion> --development-type <DT> --change-surface <surface> --in-scope <scope> --baseline-inheritance Revise --upgrade-minimal-reason <reason> --upgrade-minimal-basis <evidence-ref>
```

其余参数同普通 `init_task.py`；只允许 Minimal 到完整载体，禁止反向降级。
