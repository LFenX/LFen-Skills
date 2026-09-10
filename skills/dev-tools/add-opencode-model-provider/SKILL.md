---
name: add-opencode-model-provider
description: "为 opencode 接入第三方 OpenAI 兼容模型供应商（如 LiteLLM 网关）。覆盖 provider 配置结构、模型注册、网关验证、常见错误排查。当用户要添加新的模型供应商、配置 opencode.json 的 provider 段、或模型配置后不生效时使用。"
---

# 为 opencode 接入第三方模型供应商

## 适用范围

当用户需要为 opencode 接入一个 OpenAI 兼容的第三方模型网关（如 LiteLLM、One API、vLLM 等）时，按本 Skill 完成配置、验证和排查。

## 前置条件

- 已获得供应商的 API Key 和 base URL
- opencode 版本 >= 1.0（使用 `opencode --version` 确认）

## 配置结构

在 `opencode.json`（项目级或全局 `~/.config/opencode/opencode.json`）中添加：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "<provider-id>": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "<显示名称>",
      "options": {
        "apiKey": "<your-api-key>",
        "baseURL": "<https://your-gateway/v1>"
      },
      "models": {
        "<model-id-1>": {
          "name": "<模型显示名>",
          "tool_call": true
        },
        "<model-id-2>": {
          "name": "<模型显示名>",
          "tool_call": true
        }
      }
    }
  },
  "model": "<provider-id>/<model-id-1>",
  "small_model": "<provider-id>/<model-id-2>"
}
```

### 必填字段说明

| 字段 | 说明 |
| --- | --- |
| `provider.<id>.npm` | 必须为 `@ai-sdk/openai-compatible`（OpenAI 兼容接口） |
| `provider.<id>.options.baseURL` | 网关地址，必须以 `/v1` 结尾。**注意大小写：`baseURL`，不是 `baseUrl`** |
| `provider.<id>.options.apiKey` | 网关 API Key |
| `provider.<id>.models` | 模型列表，key 为模型 ID（与网关中的 model name 一致），value 至少包含 `name` 和 `tool_call` |
| `model` | 格式 `provider-id/model-key`，model-key 必须与 `models` 中的 key 完全一致 |
| `small_model` | 同上，用于标题生成等轻量任务 |

## 配置流程

### 1. 验证网关可达性

先测试网关的 `/v1/models` 端点，获取可用模型列表：

```powershell
Invoke-RestMethod -Uri "https://<gateway>/v1/models" `
  -Headers @{ Authorization = "Bearer <api-key>" } `
  -TimeoutSec 30
```

记录返回的 `id` 列表，这就是可用的模型 ID。

### 2. 逐个验证模型可用性

**不要仅凭 `/v1/models` 列表决定配置哪些模型**。网关可能返回名存实亡的模型（无健康部署）。对每个候选模型发送真实 chat 请求：

```powershell
$body = @{
  model = "<model-id>"
  messages = @(@{ role = "user"; content = "hi" })
  max_tokens = 1
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "https://<gateway>/v1/chat/completions" `
  -Method Post `
  -Headers @{ Authorization = "Bearer <api-key>" } `
  -ContentType "application/json" `
  -Body $body `
  -TimeoutSec 60
```

- 返回 `choices[0].message` → 可用
- 返回 `no healthy deployments` → 不可用，不要配置

### 3. 验证工具调用能力

opencode 重度依赖 tool calling。对主力模型（`model` 字段指定的）必须验证：

```powershell
$body = @{
  model = "<model-id>"
  messages = @(@{ role = "user"; content = "what is 2+2" })
  tools = @(@{
    type = "function"
    function = @{
      name = "add"
      description = "add two numbers"
      parameters = @{
        type = "object"
        properties = @{ a = @{ type = "number" }; b = @{ type = "number" } }
        required = @("a", "b")
      }
    }
  })
  max_tokens = 200
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "https://<gateway>/v1/chat/completions" `
  -Method Post `
  -Headers @{ Authorization = "Bearer <api-key>" } `
  -ContentType "application/json" `
  -Body $body `
  -TimeoutSec 60
```

返回的 `choices[0].message` 应包含 `tool_calls` 数组。

### 4. 写入配置并验证

完成配置后，用 `opencode models` 验证 opencode 是否正确加载了模型：

```bash
opencode models | grep <provider-id>
```

应列出所有配置的模型。

### 5. 重启 opencode

配置在启动时加载，修改后必须退出并重启 opencode 才能生效。

## 模型 ID 中有斜杠的特殊情况

许多网关的模型 ID 包含 `/`（如 `dashscope/qwen3.6-plus`、`anthropic-data-ai/claude-opus-5`）。在 `models` 对象中直接使用完整 ID 作为 key 即可，opencode 支持：

```json
"models": {
  "dashscope/qwen3.6-plus": { "name": "Qwen 3.6 Plus", "tool_call": true }
}
```

对应的 `model` 字段为 `"funplus/dashscope/qwen3.6-plus"`。

## 常见错误

| 症状 | 原因 | 修复 |
| --- | --- | --- |
| `opencode models` 中看不到供应商模型 | 缺少 `npm` 或 `models` 字段 | 补充 `npm: "@ai-sdk/openai-compatible"` 和 `models` 对象 |
| 模型可选但请求报错 | `baseUrl` 写成了 `baseURL` 的小写形式 | 改为 `baseURL` |
| 某个模型请求失败 "no healthy deployments" | 该模型在网关上未配置或已下线 | 从 `models` 中移除该条目 |
| 配置后不生效 | 未重启 opencode | 退出并重启 opencode |
| 工具调用失败或无响应 | 模型选择错了或网关不支持 tool calling | 切换到已验证支持 tool calling 的模型 |

## 完整示例

以下是一个接入 LiteLLM 网关的完整 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "funplus": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Funplus LiteLLM",
      "options": {
        "apiKey": "sk-xxxx",
        "baseURL": "https://litellm.funplus.com.cn/v1"
      },
      "models": {
        "claude-opus-5": {
          "name": "claude-opus-5",
          "tool_call": true
        },
        "claude-sonnet-4-6": {
          "name": "Claude Code Sonnet 4.6",
          "tool_call": true
        },
        "dashscope/deepseek-v4-pro": {
          "name": "dashscope/deepseek-v4-pro",
          "tool_call": true
        },
        "dashscope/qwen3.6-plus": {
          "name": "dashscope/qwen3.6-plus",
          "tool_call": true
        }
      }
    }
  },
  "model": "funplus/claude-opus-5",
  "small_model": "funplus/dashscope/qwen3.6-plus"
}
```