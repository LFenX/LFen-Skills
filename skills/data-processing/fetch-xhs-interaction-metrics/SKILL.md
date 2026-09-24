---
name: fetch-xhs-interaction-metrics
description: 根据公开小红书笔记链接提取点赞、收藏、评论及可见的分享数，优先使用页面结构化状态、网络响应和 DOM；仅在所需字段缺失且遇到登录墙或 App 限制时进入已有浏览器会话兜底。用于单条或少量小红书图文/视频笔记的互动数据核取，不用于直播间、私密内容或绕过验证码与访问控制。
description_en: Extract likes, collections, comments, and visible share counts from public Xiaohongshu note URLs, preferring structured page state, network responses, and DOM; use an existing browser session only when required fields remain missing behind a login or app-only gate. Use for one or a small number of public image or video notes, not livestreams, private content, or bypassing CAPTCHAs and access controls.
---

# 小红书笔记互动数据抓取

从用户提供的完整小红书笔记链接读取互动数据，并保留页面原始显示值。默认所需字段为点赞、收藏、评论；分享数只在页面可见时采集。

## 执行门控

1. 先运行 `scripts/fetch_xhs_interactions.py`。脚本只启动无登录的无头浏览器，按结构化状态、同源网络响应、DOM 的顺序取数。
2. 结果为 `ok` 时立即停止，不打开交互式浏览器，不截图。
3. 结果为 `partial` 时，只在用户所需字段仍缺失时继续；不要为了补充用户未要求的分享数启动兜底。
4. 结果为 `browser_session_required`，或 `fallback.required` 为 `true` 时，才使用当前环境已有且用户有权使用的浏览器会话打开原链接。先读 DOM 或无障碍树；登录弹窗可关闭时再关闭，但不要把登录本身作为默认步骤。
5. 遇到验证码、风险校验、私密/已删除内容或强制登录且没有授权会话时停止并如实报告，不规避访问控制。
6. 只有结构化状态、网络响应、DOM 和无障碍树均无法取数，且用户仍明确要求继续时，才使用截图/OCR或视觉模型。

这个门控是硬约束：成功的上一级不再运行下一级。

## 命令

在 Skill 目录运行：

```powershell
python scripts/fetch_xhs_interactions.py "https://www.xiaohongshu.com/explore/<note-id>?..."
```

写入 JSON 文件：

```powershell
python scripts/fetch_xhs_interactions.py "<url>" --output "C:\path\xhs-interactions.json"
```

若用户只需要评论数，缩小必需字段可以避免不必要的浏览器兜底：

```powershell
python scripts/fetch_xhs_interactions.py "<url>" --required commented
```

使用用户明确提供的 Playwright `storage_state` 时：

```powershell
python scripts/fetch_xhs_interactions.py "<url>" --storage-state "C:\secure\state.json"
```

不得复制、提交或在结果中输出 `storage_state`、Cookie、二维码、`xsec_token` 等凭据。脚本会在结果 URL 中遮蔽常见令牌参数。

脚本依赖 Python Playwright 与 Chromium。依赖缺失时先报告；仅在当前环境允许安装依赖时执行：

```powershell
python -m pip install "playwright>=1.40,<2"
python -m playwright install chromium
```

## 浏览器会话兜底

仅当门控进入此层时：

1. 使用现有浏览器会话打开原始链接，保留查询参数用于导航。
2. 等页面主体加载后，从页面状态、互动栏 DOM 或无障碍树读取点赞、收藏、评论。
3. 登录弹窗覆盖页面但底层节点仍可读时，直接读取底层节点，不登录、不截图二维码。
4. 对每个值记录页面原始文本和来源。若 DOM 与结构化状态冲突，优先采用与当前笔记 ID 对应的结构化状态，并保留冲突说明。
5. 得到用户所需字段后立即停止。

## 输出语义

- `display`：页面或结构化数据的原始显示值，例如 `2.5万`。
- `normalized_value`：便于计算的整数；`2.5万` 可归一为 `25000`。
- `exact`：只有原始值为未缩写整数时才为 `true`。不得把 `2.5万` 表述成精确的 `25000`。
- `status=ok`：所有 `--required` 字段齐全。
- `status=partial`：已取得部分字段，仍缺少至少一个必需字段。
- `status=browser_session_required`：无头结构化抓取未取得必需字段，且检测到登录墙或 App 限制。
- 退出码 `0` 表示必需字段齐全；`2` 表示需要按门控决定是否兜底；`1` 表示参数、依赖或运行错误。

只把实际观察到的值写入结果；不根据点赞与评论比例推算收藏、分享或其他字段。

## 验证

修改本 Skill 后运行：

```powershell
python scripts/self_test.py
python scripts/fetch_xhs_interactions.py "<一条当前可访问的公开笔记 URL>"
```

实时测试可能因链接令牌、地区、风控和登录状态得到 `browser_session_required`；这属于受控分支，不等同于脚本故障。
