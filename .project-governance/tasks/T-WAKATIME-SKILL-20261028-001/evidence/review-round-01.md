# WAKATIME-REVIEW-01：独立只读对抗性审查

- 审查者：独立子 Agent `/root/wakatime_review_one`。
- 对象：内容提交 `f9e8a0f8177418f0c2e4da26470827495fcdad35`。
- 审查完成：2026-10-28T12:22:32Z；报告由父 Agent 根据子 Agent 完整回报保存。
- 结论：一轮完整覆盖，确认 F01（P1）、F02（P2），不是无问题轮次。
- 期间工作区正常同步至 `6a84c81c8780ea7f53f57293f7a4b7583df4b878`，十三个 WakaTime 内容文件仍与原验证摘要 13/13 一致。
- 本轮未修改代码、执行真实 CLI、读取个人凭证或真实队列，未启动第二轮。

## 原始要求与覆盖

原件：本任务 `evidence/user-request.json`。

> 请你将你上述接入这些的过程和步骤经验总结为一个专属的skill，放到 LFen-skills仓库中，注意遵循基本的操作流程来上传

> 分类要精准，如果用现有文件夹那要搞多级文件夹，否则容易和其他skill混淆

| 要求 | 核查结果 |
| --- | --- |
| 总结接入步骤经验并形成 skill | 六个源文件齐全，但诊断器存在 F01、F02，与自身承诺不一致 |
| 放入 LFen-Skills 并上传 | 内容提交存在，两项 CI 均绑定该提交且成功 |
| 基本操作流程 | 分类登记、生成、验证、测试、独立更新日志、提交上传均有证据；归档摘要已复核 |
| 精准分类、多级目录 | 编程活动统计 / WakaTime，两级目录；原九个 skill 名称和路径全部保留 |

背景逐项核查：桌面 Codex / CLI / VS Code 来源区别（SKILL 第16行及 tool-setup 36–57）；Cursor / VS Code（15–34）；Claude Code（59–70）；OpenCode 社区来源与保留配置（72–89）；保留 Grok Bot（SKILL 第17行及 tool-setup 91–95）；Other 归因边界（accuracy-and-recovery 29–46）；非 Git 项目（48–64）；重复采集（19–27）；多设备（tool-setup 97–112）；GPT 系列、版本和指标区别（accuracy-and-recovery 66–78）。均覆盖，没有将尚未核验的历史现场表述为已修正。

## 完整范围

全文核查 SKILL.md、agents/openai.yaml、两份 references、inspect_wakatime.py、test_inspect_wakatime.py；核查 taxonomy / index / README 中英文 / SKILLS 中英文 / CATALOG 的分类、路径、生成及安装入口；全文核查独立更新日志，并核对 before / after / run / evidence 的原话、范围、状态、验证、失败恢复和发布证明。

## F01（P1）：真实队列探针未隔离

违反 SKILL.md 第24行、accuracy-and-recovery 第13–17行及更新日志的只读、无上传承诺。代码位置为 inspect_wakatime.py 第95–107、173–199行。

默认 collect 将原始配置交给 CLI 的 --offline-count / --print-offline-heartbeats，继承原环境。文档所引用 v2.28.0 的调用链为 CountHeartbeats / ReadHeartbeats → openDB。数据库按默认可写方式打开；损坏分支会将原队列改名为 .corrupt.*。ErrOpenDB 强制 ShouldLogError=true、SendDiagsOnErrors=true，继而进入诊断发送、凭证加载及 api_key_vault_cmd 执行路径。包装器仍输出 read_only=true，且失败后继续下一个队列探针。

预期：原队列、配置不变，不执行凭证命令，不发送诊断请求，报告不可读。实际副作用分支由官方源码确认；本轮没有对真实队列执行，也没有认定用户历史环境已经受损。

源码证据：

- [队列打开与恢复](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/offline/offline.go#L445-L603)
- [损坏错误策略](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/offline/error.go#L29-L42)
- [诊断分派与发送](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/cmd/run.go#L241-L305)
- [凭证加载与命令执行](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/params/params.go#L562-L605)

隔离 mock 结果：

```json
{"read_only":true,"errors":["count_format_invalid"],"sampled_records":0,"probe_count":3,"all_use_original_config":true,"has_queue_snapshot_arg":false,"has_internal_config_isolation":false,"explicit_environment":false}
```

最小修复：暂停默认真实队列 CLI 探针，明确返回队列未检查；若保留自动摘要，只能操作隔离副本并使用无凭证配置、隔离内部目录及环境。普通关闭诊断参数不能覆盖强制诊断分支。增加原队列不变、vault 与网络调用为零的回归检查。

## F02（P2）：旧格式凭证的两种配置形式漏脱敏

违反不输出凭证的约束。inspect_wakatime.py 第60–65行未去除外围引号，也未收集 [project_api_key] 以项目正则为键的值；第132–159行未保守识别旧 UUID v4 凭证。

复现条件：CLI 接受的无 waka_ 前缀 UUID v4 凭证位于带双引号的 settings.api_key 或 [project_api_key]，且被污染的 language 或 gpt/<凭证> 元数据含该值。预期两种形式均脱敏；实际语言、模型输出均保留合成凭证。普通 settings 和 api_urls 对照脱敏成功。这不是正常采集器必然把凭证写入元数据的断言。

依据：[旧凭证格式](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/params/params.go#L45-L47)、[配置字符串处理](https://github.com/wakatime/wakatime-cli/blob/v2.28.0/pkg/vipertools/vipertools.go#L118-L121)。

在仓库根目录执行的合成反例（不读取真实配置，仅输出布尔值）：

```python
import importlib.util
import json
import tempfile
from pathlib import Path

script = Path("skills/coding-activity-analytics/wakatime/setup-wakatime-ai-tracking/scripts/inspect_wakatime.py")
spec = importlib.util.spec_from_file_location("review_probe", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
synthetic = "12345678-1234-4abc-8def-123456789abc"
cases = {
    "settings": f"[settings]\napi_key = {synthetic}\n",
    "quoted_settings": f'[settings]\napi_key = "{synthetic}"\n',
    "project_api_key": "[settings]\n[project_api_key]\n" + f"^/Projects/local-app = {synthetic}\n",
    "api_urls": "[settings]\n[api_urls]\n" + f"^/Projects/local-app = https://example.invalid/api/v1|{synthetic}\n",
}
with tempfile.TemporaryDirectory(prefix="wakatime-review-") as directory:
    for name, contents in cases.items():
        config = Path(directory) / f"{name}.cfg"
        config.write_text(contents, encoding="utf-8")
        _, secrets = module.config_summary(config)
        report = module.queue_summary([{"type": "app", "language": synthetic, "user_agent": "gpt/" + synthetic}], secrets)
        print(json.dumps({"case": name, "credential_in_language_output": synthetic in report["languages"], "credential_in_model_output": "gpt/" + synthetic in report["known_model_tokens"]}))
```

```json
{"case":"settings","credential_in_language_output":false,"credential_in_model_output":false}
{"case":"quoted_settings","credential_in_language_output":true,"credential_in_model_output":true}
{"case":"project_api_key","credential_in_language_output":true,"credential_in_model_output":true}
{"case":"api_urls","credential_in_language_output":false,"credential_in_model_output":false}
```

最小修复：规范化敏感值引号、收集 project_api_key 的值、保守过滤旧 UUID v4，补齐失败输入及成功对照；不执行 vault 或加载导入配置。

## 实际验证

Python 使用 -B -X utf8；临时数据均为合成数据。

| 验证 | 实际结果 |
| --- | --- |
| skill-creator quick_validate | Skill is valid |
| 诊断脚本测试 | 9 通过 |
| update_catalog --check | 10 skill / 6 一级分类，一致 |
| test_update_catalog | 22 通过 |
| test_check_install_links | 10 通过 |
| git diff --check | 退出0 |
| 基线 fbb125d 与内容提交路径对比 | 原9项保留，仅新增本skill |
| 内容摘要 | 13/13 匹配 |
| 历史查询归档 manifest | 28/28 匹配 |
| 归档索引与请求 | 摘要匹配，7份请求 |
| F01 mock | 原配置、原环境未隔离，失败后继续 |
| F02 合成对照 | 两种泄露、两个正常脱敏 |

本轮复跑41项测试全通过；这些测试未覆盖两个缺陷。未重跑安装器17项；原记录16通过、1 Windows跳过，不计入本轮复跑。

发布核对：[Validate skill catalog](https://github.com/LFenX/LFen-Skills/actions/runs/40682015423)、[Skill gates](https://github.com/LFenX/LFen-Skills/actions/runs/40682015443) 均 completed/success，head_sha=f9e8a0f。远端后续推进不反证原上传记录；[比较](https://github.com/LFenX/LFen-Skills/compare/f9e8a0f8177418f0c2e4da26470827495fcdad35...6a84c81c8780ea7f53f57293f7a4b7583df4b878)未覆盖本次内容。

## 限制与交接

before 保留原话，after 为 Implemented、用户决定 Pending，未伪造最终验收。原只读冒烟与精确敏感扫描只能证明原样本，不能推断所有输入安全。

真实工具安装、hooks、设备、云端仪表盘不属于本次沉淀任务，本轮未执行；未读取个人配置、项目、聊天日志，未独立追溯历史现场观察与原真实密钥扫描。本轮冻结范围已覆盖，没有范围内未检查项；上述是现场追溯与环境覆盖限制。

F01、F02 在本轮结束时均未修复。后续授权修复及复验应另行留档，不能改写本轮发现、补成无问题轮次或追加第二轮。
