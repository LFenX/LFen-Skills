#!/usr/bin/env python3
"""Server-rendered pages for the governance console.

Multi-page with real URLs: every view is linkable, back and forward work, and no
client framework is involved. Rendering stays pure so the server can be tested by
calling these functions directly.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any, Iterable

import audit_console

RELATION_LABELS = audit_console.RELATION_LABELS
SEVERITY_BADGE = {"warn": "warn", "info": "mute", "error": "neg"}

NAV = (
    ("治理", (
        ("/", "总览", None),
        ("/tasks", "任务", "tasks"),
        ("/lineage", "血缘与衍生", "lineage"),
        ("/unresolved", "未决项", "unresolved"),
    )),
    ("文档", (
        ("/docs", "项目文档", "requirements"),
        ("/intake", "待分类", "intake"),
        ("/archive", "迁移归档", "archives"),
    )),
    ("资产", (
        ("/artifacts", "生成物", "artifacts"),
        ("/integrity", "完整性与审计", "findings"),
    )),
)


def e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _counts(model: dict[str, Any]) -> dict[str, int]:
    docs = model["docs"]
    return {
        "tasks": len(model["tasks"]),
        "lineage": sum(len(t["next_tasks"]) for t in model["tasks"]),
        "unresolved": len(model["unresolved"]),
        "requirements": len(docs.get("requirements", [])),
        "intake": len(docs.get("intake", [])),
        "archives": len(docs.get("archives", [])),
        "artifacts": sum(len(f["items"]) for f in model["artifacts"]),
        "findings": len(model["doc_findings"]) + len(model["integrity"].get("errors", [])),
    }


def badge(text: str, tone: str = "") -> str:
    return f'<span class="badge {tone}">{e(text)}</span>'


def task_link(model: dict[str, Any], task_id: str) -> str:
    """Link a task only when it exists.

    next_tasks may name a successor that has not been created yet -- that is the
    normal recording order -- so linking every target would produce 404s in the UI.
    """

    known = {task["task_id"] for task in model.get("tasks", [])}
    if task_id in known:
        return f"<a class='mono' href='/tasks/{e(task_id)}'>{e(task_id)}</a>"
    return f"<span class='mono'>{e(task_id)}</span> {badge('尚未创建', 'warn')}"


def relation_badge(relation: str) -> str:
    label, tone = RELATION_LABELS.get(relation, [relation, "neutral"])
    return badge(label, {"negative": "neg", "positive": "pos"}.get(tone, ""))


def empty(message: str, hint: str = "") -> str:
    extra = f"<p class='hint'>{e(hint)}</p>" if hint else ""
    return f"<div class='empty'><p>{e(message)}</p>{extra}</div>"


def table(headers: Iterable[str], rows: Iterable[str], min_width: str = "") -> str:
    body = "".join(rows)
    if not body:
        return ""
    head = "".join(f"<th{' class=num' if h.startswith('#') else ''}>{e(h.lstrip('#'))}</th>" for h in headers)
    style = f' style="min-width:{min_width}"' if min_width else ""
    return f"<div class='tablewrap'><table{style}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def shell(model: dict[str, Any], *, path: str, title: str, crumbs: list[tuple[str, str]], body: str) -> str:
    counts = _counts(model)
    nav_html = []
    for group, links in NAV:
        nav_html.append(f"<h6>{e(group)}</h6>")
        for href, label, key in links:
            current = ' aria-current="page"' if href == path or (href != "/" and path.startswith(href)) else ""
            count = f"<span class='count'>{counts[key]}</span>" if key else ""
            nav_html.append(f'<a href="{e(href)}"{current}>{e(label)}{count}</a>')
    crumb = " / ".join(
        f'<a href="{e(href)}">{e(text)}</a>' if href else f"<b>{e(text)}</b>" for href, text in crumbs
    )
    stale = ""
    if not model["state_present"]:
        stale = ("<div class='card'><h3>ProjectState 尚未建立</h3><p class='hint'>"
                 "运行 rebuild_project_state.py 后任务与血缘视图才会有内容。</p></div>")
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · 治理控制台</title>
<link rel="stylesheet" href="/static/console.css">
</head><body>
<div class="shell">
<aside class="side">
  <div class="brand"><b>治理控制台</b><span>{e(model['project_id'])}</span></div>
  <nav class="nav">{''.join(nav_html)}</nav>
  <div class="foot">只读视图 · 每次请求实时探查<br>DerivedView 不得作为新事实的唯一来源</div>
</aside>
<div class="main">
  <div class="topbar">
    <div class="crumb">{crumb}</div>
    <form class="search" action="/search" method="get" role="search">
      <input type="search" name="q" placeholder="检索任务、文档、生成物  （按 / 聚焦）"
             aria-label="全局检索" data-global-search>
    </form>
    <button class="btn" data-theme-toggle type="button">主题</button>
  </div>
  <main class="content">{stale}{body}</main>
</div>
</div>
<script src="/static/console.js"></script>
</body></html>"""


# --- pages ------------------------------------------------------------------


def page_overview(model: dict[str, Any]) -> str:
    counts = _counts(model)
    audit = model["derivation"]
    rel = audit.get("relation_counts", {})
    worst = max((r["caused_chain_depth"] for r in audit.get("by_task", [])), default=0)
    integrity_errors = len(model["integrity"].get("errors", []))
    docs = model["docs"]
    metrics = [
        ("", counts["tasks"], "受控任务"),
        ("is-neg" if rel.get("affected-by") else "", rel.get("affected-by", 0), "本次引入的衍生"),
        ("is-pos" if rel.get("observed-from") else "", rel.get("observed-from", 0), "顺带发现的问题"),
        ("is-neg" if worst >= 3 else "", worst, "最长回归链"),
        ("is-warn" if counts["unresolved"] else "", counts["unresolved"], "未决项"),
        ("is-neg" if integrity_errors else "is-pos", integrity_errors or "完好", "受保护资产核对"),
    ]
    grid = "".join(
        f"<div class='metric {tone}'><b>{e(value)}</b><span>{e(label)}</span></div>"
        for tone, value, label in metrics
    )
    findings = model["doc_findings"]
    finding_rows = "".join(
        f"<div class='finding'>{badge(f['category'], SEVERITY_BADGE.get(f['severity'], ''))}"
        f"<div><p>{e(f['summary'])}</p><p class='detail'>{e(f['detail'])}</p></div></div>"
        for f in findings[:6]
    )
    docs_body = (
        f"<dl class='kv'><dt>需求目录</dt><dd>{counts['requirements']}</dd>"
        f"<dt>待分类</dt><dd>{counts['intake']}</dd>"
        f"<dt>迁移归档</dt><dd>{counts['archives']}</dd>"
        f"<dt>布局外资产</dt><dd>{len(docs.get('stray', []))}</dd></dl>"
    )
    return f"""<h1>总览</h1>
<p class="lede">控制台每次请求都重新探查 <code>.project-governance</code> 与 <code>LG_project_docs</code>，
不缓存、不冻结。所有数字都可以点进去看到它的来源记录。</p>
<div class="grid">{grid}</div>
<div class="card"><h3>文档域</h3><p class="hint">项目文档目录的规模与形态。</p>{docs_body}
<p style="margin:12px 0 0"><a href="/docs">查看项目文档 →</a></p></div>
<div class="card"><h3>待处理的审计发现</h3>
<p class="hint">布局、登记与纳管方面需要人来决定的事项。</p>
{finding_rows or empty('没有文档域审计发现。')}
{'<p style="margin:12px 0 0"><a href="/integrity">查看全部 →</a></p>' if findings else ''}</div>"""


def page_tasks(model: dict[str, Any]) -> str:
    rows = []
    for task in model["tasks"]:
        hay = " ".join([task["task_id"], task["objective"], task["status"], task["carrier"], task["risk_level"]])
        rows.append(
            f'<tr data-filter="{e(hay)}" data-group="{e(task["carrier"])}">'
            f'<td class="num">{e(task["ordinal"])}</td>'
            f'<td><a class="mono" href="/tasks/{e(task["task_id"])}">{e(task["task_id"])}</a></td>'
            f'<td>{badge(task["carrier"], "mute")}</td>'
            f'<td>{e(task["status"])}</td>'
            f'<td>{e(task["risk_level"] or "-")}</td>'
            f'<td class="wrap">{e(task["objective"])}</td>'
            f'<td class="num">{len(task["next_tasks"]) or ""}</td></tr>'
        )
    carriers = sorted({t["carrier"] for t in model["tasks"]})
    options = "".join(f"<option value='{e(c)}'>{e(c)}</option>" for c in carriers)
    body = table(["#序号", "任务", "载体", "状态", "风险", "目标", "#衍生"], rows) or empty(
        "还没有受控任务。", "用 init_task.py 或 manage_minimal_task.py init 建立第一个任务。"
    )
    return f"""<h1>任务</h1>
<p class="lede">来自 ProjectState 的任务图与每个任务的契约记录。点任务 ID 进入详情。</p>
<div data-filter-scope>
  <div class="filters">
    <input type="search" placeholder="筛选任务…" data-filter-input aria-label="筛选任务">
    <select data-filter-select aria-label="按载体筛选"><option value="">全部载体</option>{options}</select>
    <span class="spacer"></span><span class="result" data-filter-count></span>
  </div>
  {body}
</div>"""


def page_task(model: dict[str, Any], task_id: str) -> str | None:
    task = next((t for t in model["tasks"] if t["task_id"] == task_id), None)
    if task is None:
        return None
    profile = (
        f"<dl class='kv'>"
        f"<dt>载体</dt><dd>{badge(task['carrier'], 'mute')} {e(task.get('lifecycle', ''))}</dd>"
        f"<dt>状态</dt><dd>{e(task['status'])}</dd>"
        f"<dt>Delivery Scenario</dt><dd>{e(task['delivery_scenario'] or '-')}</dd>"
        f"<dt>Development Type</dt><dd>{e('、'.join(task['development_types']) or '-')}</dd>"
        f"<dt>Change Surface</dt><dd>{e('、'.join(task['change_surfaces']) or '-')}</dd>"
        f"<dt>Risk</dt><dd>{e(task['risk_level'] or '-')}</dd>"
        f"</dl>"
    )
    def bullets(title: str, items: list[str], mono: bool = False) -> str:
        if not items:
            return ""
        cls = " class='mono'" if mono else ""
        lis = "".join(f"<li{cls}>{e(x)}</li>" for x in items)
        return f"<div class='card'><h3>{e(title)}</h3><ul class='plain'>{lis}</ul></div>"

    events = "".join(
        f"<li>{badge(ev['event_type'], 'mute')}<span>{e(ev['summary'])}</span>"
        f"<time>{e(ev['timestamp'])}</time></li>"
        for ev in task["events"]
    )
    events_card = (
        f"<div class='card'><h3>执行事件</h3><p class='hint'>RunLedger 只追加；这里按记录顺序展示。</p>"
        f"<ul class='timeline'>{events}</ul></div>"
        if events else ""
    )
    links = []
    for link in task["next_tasks"]:
        links.append(
            f"<li>{relation_badge(link['relation'])} "
            f"{task_link(model, link['task_id'])} — {e(link['reason'])}</li>"
        )
    for link in task["derived_from"]:
        links.append(
            f"<li>{badge('被派生自', 'mute')} "
            f"{task_link(model, link['task_id'])} — {e(link['reason'])}</li>"
        )
    for other in task["required_by"]:
        links.append(f"<li>{badge('被依赖', 'mute')} {task_link(model, other)}</li>")
    for other in task["depends_on"]:
        links.append(f"<li>{badge('依赖', 'mute')} {task_link(model, other)}</li>")
    lineage_card = (
        f"<div class='card'><h3>血缘</h3><ul class='plain'>{''.join(links)}</ul></div>"
        if links else ""
    )
    incomplete = "".join(
        f"<div class='finding'>{badge('未决', 'warn')}<div><p>{e(item.get('summary', ''))}</p>"
        f"<p class='detail'>影响：{e(item.get('impact', ''))} · 负责人：{e(item.get('owner', ''))} · "
        f"回归条件：{e(item.get('reentry_condition', ''))}</p></div></div>"
        for item in task["incomplete_items"]
    )
    incomplete_card = f"<div class='card'><h3>未决项</h3>{incomplete}</div>" if incomplete else ""
    files = "".join(
        f"<tr data-filter='{e(f['path'])}'><td><a class='mono' href='/preview?path={e(f['path'])}'>{e(f['name'])}</a></td>"
        f"<td class='mono'>{e(f['path'])}</td><td class='num'>{f['size']}</td><td>{e(f['modified'])}</td></tr>"
        for f in task["files"]
    )
    files_card = (
        f"<div class='card'><h3>任务文件</h3><p class='hint'>该任务目录下的受控记录，点文件名可预览。</p>"
        f"{table(['文件', '路径', '#字节', '修改时间'], [files])}</div>"
        if files else ""
    )
    return f"""<h1 class="mono">{e(task['task_id'])}</h1>
<p class="lede">{e(task['objective'])}</p>
<div class="card"><h3>分类</h3>{profile}</div>
{bullets('允许路径', task['allowed_paths'], mono=True)}
{bullets('验收', task['acceptance'])}
{events_card}
{bullets('成立事实', task['established_facts'])}
{bullets('实际变化', task['actual_changes'])}
{incomplete_card}
{lineage_card}
{files_card}"""


def page_lineage(model: dict[str, Any]) -> str:
    audit = model["derivation"]
    rows = []
    for record in audit.get("by_task", []):
        if not (record["caused"] or record["surfaced"] or record["derived_from"]):
            continue
        width = min(record["caused_chain_depth"] * 24, 150)
        bar = f"<span class='bar' style='width:{width}px'></span>" if width else ""
        rows.append(
            f"<tr><td><a class='mono' href='/tasks/{e(record['task_id'])}'>{e(record['task_id'])}</a></td>"
            f"<td class='num'>{record['caused'] or ''}</td><td class='num'>{record['surfaced'] or ''}</td>"
            f"<td class='num'>{record['derived_from'] or ''}</td>"
            f"<td class='num'>{record['caused_chain_depth'] or ''}</td><td>{bar}</td></tr>"
        )
    audit_table = table(
        ["任务", "#本次引入", "#顺带发现", "#被派生", "#回归链深", ""], rows
    ) or empty("还没有任务记录衍生关系。", "收尾时用 --next-task TASK::relation::reason 记录。")
    dangling = "".join(
        f"<tr><td>{task_link(model, d['task_id'])}</td>"
        f"<td>{task_link(model, d['target'])}</td><td>{relation_badge(d['relation'])}</td></tr>"
        for d in audit.get("recorded_but_not_created", [])
    )
    graph_rows = []
    for task in model["tasks"]:
        if not (task["next_tasks"] or task["derived_from"] or task["required_by"]):
            continue
        chips = "".join(
            f"{relation_badge(l['relation'])}{task_link(model, l['task_id'])} "
            for l in task["next_tasks"]
        ) + "".join(
            f"{badge('被派生自', 'mute')}{task_link(model, l['task_id'])} "
            for l in task["derived_from"]
        ) + "".join(
            f"{badge('被依赖', 'mute')}{task_link(model, x)} " for x in task["required_by"]
        )
        graph_rows.append(
            f"<div class='finding'><a class='mono' href='/tasks/{e(task['task_id'])}'>{e(task['task_id'])}</a>"
            f"<div><p>{e(task['objective'])}</p><p class='detail'>{chips}</p></div></div>"
        )
    return f"""<h1>血缘与衍生</h1>
<p class="lede">关系值来自 C10 §8.2 受控词表，界面显示中文标签（§8.3 允许显示层另行标注）。
回归链只沿「本次引入」计算——顺带发现问题是任务在做该做的事，不记进同一笔账。</p>
<div class="card"><h3>衍生审计</h3><p class="hint">按关系符号分开统计，链深归因到源头任务。</p>{audit_table}</div>
<div class="card"><h3>已识别但尚未接手</h3>
<p class="hint">被记录为衍生目标、但项目里还不存在的任务。这是线索，不是错误。</p>
{table(['来源任务', '目标', '关系'], [dangling]) or empty('没有悬空的衍生目标。')}</div>
<div class="card"><h3>关系图</h3><p class="hint">前向与两种反向边。</p>
{''.join(graph_rows) or empty('还没有任务之间的关系。')}</div>"""


def page_unresolved(model: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr data-filter='{e(item.get('task_id', '') + item.get('summary', ''))}'>"
        f"<td><a class='mono' href='/tasks/{e(item.get('task_id', ''))}'>{e(item.get('task_id', ''))}</a></td>"
        f"<td>{badge(item.get('category', ''), 'mute')}</td>"
        f"<td class='wrap'>{e(item.get('summary', ''))}</td>"
        f"<td class='wrap'>{e(item.get('impact', ''))}</td>"
        f"<td>{e(item.get('owner', ''))}</td>"
        f"<td class='wrap'>{e(item.get('reentry_condition', ''))}</td></tr>"
        for item in model["unresolved"]
    )
    return f"""<h1>未决项</h1>
<p class="lede"><code>reentry_condition</code> 说明什么条件下应该回来继续——这是「没有完全修复」的正式记录处。</p>
<div data-filter-scope><div class="filters">
  <input type="search" placeholder="筛选…" data-filter-input aria-label="筛选未决项">
  <span class="spacer"></span><span class="result" data-filter-count></span></div>
{table(['任务', '类别', '摘要', '影响', '负责人', '回归条件'], [rows]) or empty('没有未决项。')}</div>"""


def page_docs(model: dict[str, Any]) -> str:
    docs = model["docs"]
    if not docs.get("present"):
        return ("<h1>项目文档</h1>" + empty(
            f"{docs['root']}/ 尚未建立。",
            "运行 manage_project_docs.py init --project-root <project-root> 建立目录。"))
    rows = "".join(
        f"<tr data-filter='{e(r['requirement_id'])}'>"
        f"<td><a class='mono' href='/docs/{e(r['requirement_id'])}'>{e(r['requirement_id'])}</a></td>"
        f"<td class='num'>{r['file_count']}</td>"
        f"<td>{'、'.join(e(k) for k in r['groups'] if k != '_root') or '-'}</td>"
        f"<td>{badge('有', 'pos') if r['has_readme'] else badge('缺失', 'warn')}</td>"
        f"<td>{''.join(badge(t, 'mute') for t in r['custom_types']) or ''}</td></tr>"
        for r in docs["requirements"]
    )
    stray = "".join(
        f"<tr><td class='mono'><a href='/preview?path={e(s['path'])}'>{e(s['path'])}</a></td>"
        f"<td class='num'>{s['size']}</td><td>{e(s['modified'])}</td></tr>"
        for s in docs["stray"]
    )
    return f"""<h1>项目文档</h1>
<p class="lede">按需求身份分类，再按文档类型分类。这里也包含并非本 skill 产生的资产——
布局外的文件会单独列出，供你决定归属。</p>
<div data-filter-scope><div class="filters">
  <input type="search" placeholder="筛选需求…" data-filter-input aria-label="筛选需求">
  <span class="spacer"></span><span class="result" data-filter-count></span></div>
{table(['需求', '#文档', '类型', 'README', '自定义类型'], [rows]) or empty('还没有需求文档目录。')}</div>
<div class="card"><h3>布局外资产</h3>
<p class="hint">在 {e(docs['root'])} 内但不落在 requirements/、_intake 或 _archive 的文件。</p>
{table(['路径', '#字节', '修改时间'], [stray]) or empty('没有布局外资产。')}</div>"""


def page_requirement(model: dict[str, Any], requirement_id: str) -> str | None:
    docs = model["docs"]
    req = next((r for r in docs.get("requirements", []) if r["requirement_id"] == requirement_id), None)
    if req is None:
        return None
    sections = []
    for group, items in req["groups"].items():
        title = "目录根" if group == "_root" else group
        tone = " " + badge("自定义类型", "mute") if group in req["custom_types"] else ""
        rows = "".join(
            f"<tr data-filter='{e(item['path'])}'>"
            f"<td><a class='mono' href='/preview?path={e(item['path'])}'>{e(item['name'])}</a></td>"
            f"<td>{badge(item['kind'], 'mute')}</td>"
            f"<td class='num'>{item['size']}</td><td>{e(item['modified'])}</td></tr>"
            for item in items
        )
        sections.append(
            f"<div class='card'><h3>{e(title)}{tone}</h3>"
            f"{table(['文件', '类型', '#字节', '修改时间'], [rows])}</div>"
        )
    readme = "" if req["has_readme"] else (
        f"<div class='card'><h3>{badge('缺失', 'warn')} README.md</h3>"
        "<p class='hint'>项目文档目录与迁移规范 §4 要求每个需求目录的 README 解释其下每个文件和目录的作用。</p></div>"
    )
    return f"""<h1 class="mono">{e(requirement_id)}</h1>
<p class="lede">{req['file_count']} 个文档 · <span class="mono">{e(req['path'])}</span></p>
{readme}{''.join(sections) or empty('该需求目录下还没有文档。')}"""


def page_intake(model: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr data-filter='{e(item['path'])}'>"
        f"<td><a class='mono' href='/preview?path={e(item['path'])}'>{e(item['name'])}</a></td>"
        f"<td>{badge(item.get('document_type', ''), 'mute')}</td>"
        f"<td class='mono'>{e(item['path'])}</td><td class='num'>{item['size']}</td></tr>"
        for item in model["docs"].get("intake", [])
    )
    return f"""<h1>待分类</h1>
<p class="lede">身份无法可靠确定时文档进入 <code>_intake/unclassified/</code>，由人确认——规范禁止猜测身份。</p>
{table(['文件', '推断类型', '路径', '#字节'], [rows]) or empty('没有待分类文档。')}"""


def page_archive(model: dict[str, Any]) -> str:
    cards = []
    for item in model["docs"].get("archives", []):
        checks = "".join([
            badge("plan", "pos" if item["has_plan"] else "warn"),
            " ",
            badge("manifest", "pos" if item["has_manifest"] else "warn"),
            " ",
            badge("report", "pos" if item["has_report"] else "warn"),
        ])
        report_link = (
            f"<p style='margin:10px 0 0'><a href='/preview?path={e(item['path'])}/migration-report.md'>查看迁移报告 →</a></p>"
            if item["has_report"] else ""
        )
        cards.append(
            f"<div class='card'><h3 class='mono'>{e(item['migration_id'])}</h3>"
            f"<p class='hint'>{item['file_count']} 个文件 · <span class='mono'>{e(item['path'])}</span></p>"
            f"<p>{checks}</p>{report_link}</div>"
        )
    return f"""<h1>迁移归档</h1>
<p class="lede">采用 skill 时旧文档的迁移记录。每次迁移都保留原路径备份、计划、清单与报告。</p>
{''.join(cards) or empty('没有迁移归档。')}"""


def page_artifacts(model: dict[str, Any]) -> str:
    sections = []
    for family in model["artifacts"]:
        rows = []
        for item in family["items"]:
            env = item.get("envelope") or {}
            status = env.get("integrity_status", "")
            tone = {"Complete": "pos", "Failed": "neg", "Stale": "warn"}.get(status, "mute")
            rows.append(
                f"<tr data-filter='{e(item['path'])}'>"
                f"<td><a class='mono' href='/preview?path={e(item['path'])}'>{e(item['name'])}</a></td>"
                f"<td class='mono'>{e(item['group'] if item['group'] != '.' else '')}</td>"
                f"<td>{badge(env.get('view_kind', '—'), 'mute')}</td>"
                f"<td>{badge(status or '无信封', tone)}</td>"
                f"<td class='num'>{item['size']}</td><td>{e(item['modified'])}</td></tr>"
            )
        sections.append(
            f"<div class='card' data-filter-scope><h3>{e(family['label'])}"
            f"<span class='badge mute' style='margin-left:8px'>{len(family['items'])}</span></h3>"
            f"<p class='hint'>{e(family['hint'])}</p>"
            f"<div class='filters'><input type='search' placeholder='筛选…' data-filter-input "
            f"aria-label='筛选{e(family['label'])}'><span class='spacer'></span>"
            f"<span class='result' data-filter-count></span></div>"
            f"{table(['文件', '分组', 'view_kind', '完整性', '#字节', '修改时间'], rows) or empty('该族下没有生成物。')}</div>"
        )
    return f"""<h1>生成物</h1>
<p class="lede">DerivedView 与检索产物。每个文件配一个 <code>.view.json</code> 信封，记录 view_kind、来源清单与快照摘要。</p>
{''.join(sections)}"""


def page_integrity(model: dict[str, Any]) -> str:
    integrity = model["integrity"]
    errors = integrity.get("errors", [])
    roles = "".join(
        f"<tr><td>{e(role)}</td><td class='num'>{count}</td></tr>" for role, count in integrity.get("roles", {}).items()
    )
    error_rows = "".join(f"<tr><td class='mono'>{e(err)}</td></tr>" for err in errors)
    findings = model["doc_findings"]
    groups: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        groups.setdefault(finding["category"], []).append(finding)
    finding_cards = []
    for category, items in sorted(groups.items()):
        rows = "".join(
            f"<div class='finding'>{badge(item['severity'], SEVERITY_BADGE.get(item['severity'], ''))}"
            f"<div><p>{e(item['summary'])}</p><p class='detail'>{e(item['detail'])}</p>"
            + (
                f"<p class='detail mono'><a href='/preview?path={e(item['path'])}'>{e(item['path'])}</a></p>"
                if item.get("path") and item.get("previewable", True)
                else (f"<p class='detail mono'>{e(item['path'])}</p>" if item.get("path") else "")
            )
            + "</div></div>"
            for item in items
        )
        finding_cards.append(
            f"<div class='card'><h3>{e(category)}<span class='badge mute' style='margin-left:8px'>{len(items)}</span></h3>{rows}</div>"
        )
    status = badge("全部一致", "pos") if not errors else badge(f"{len(errors)} 处不符", "neg")
    return f"""<h1>完整性与审计</h1>
<p class="lede">左半是 skill 自身受保护运行资产的哈希核对，右半是项目文档域的布局与登记审计。</p>
<div class="card"><h3>受保护运行资产 {status}</h3>
<p class="hint">{integrity.get('total', 0)} 项资产按 embedded-manifest.json 的 SHA-256 逐一核对。</p>
{table(['角色', '#数量'], [roles])}
{table(['不符项'], [error_rows]) if error_rows else ''}</div>
{''.join(finding_cards) or "<div class='card'><h3>文档域审计</h3>" + empty('没有发现。') + "</div>"}"""


def page_search(model: dict[str, Any], query: str, hits: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"<tr><td>{badge(hit['kind'], 'mute')}</td>"
        f"<td><a href='{e(hit['href'])}'>{e(hit['label'])}</a></td>"
        f"<td class='wrap'>{e(hit['context'])}</td></tr>"
        for hit in hits
    )
    if not query:
        body = empty("输入关键词开始检索。", "按 / 可以快速聚焦顶部搜索框。")
    else:
        body = table(["类型", "结果", "上下文"], [rows]) or empty(f"没有匹配 “{query}” 的结果。")
    return f"""<h1>检索</h1>
<p class="lede">跨任务、需求、文档与生成物的子串检索。</p>{body}"""


# --- preview ----------------------------------------------------------------

_MD_INLINE = (
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
)


def markdown_to_html(text: str) -> str:
    """Small, deliberately conservative Markdown subset.

    Enough for governance documents -- headings, lists, tables, code fences, quotes --
    without pulling in a dependency. Everything is escaped first, so document content
    can never inject markup.
    """

    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_code = False
    list_type: str | None = None
    table_buffer: list[list[str]] = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    def flush_table() -> None:
        if not table_buffer:
            return
        header, *rest = table_buffer
        body_rows = [row for row in rest if not all(set(cell.strip()) <= {"-", ":", " "} for cell in row)]
        head = "".join(f"<th>{inline(cell)}</th>" for cell in header)
        body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in body_rows)
        out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
        table_buffer.clear()

    def inline(value: str) -> str:
        result = e(value)
        for pattern, repl in _MD_INLINE:
            result = pattern.sub(repl, result)
        return result

    for line in lines:
        if line.strip().startswith("```"):
            flush_table(); close_list()
            out.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(e(line))
            continue
        if line.strip().startswith("|") and line.strip().endswith("|"):
            close_list()
            table_buffer.append([cell.strip() for cell in line.strip().strip("|").split("|")])
            continue
        flush_table()
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            close_list()
            level = min(len(heading.group(1)), 4)
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith("> "):
            close_list()
            out.append(f"<blockquote>{inline(stripped[2:])}</blockquote>")
            continue
        bullet = re.match(r"^[-*+]\s+(.*)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if bullet or ordered:
            want = "ul" if bullet else "ol"
            if list_type != want:
                close_list()
                out.append(f"<{want}>")
                list_type = want
            out.append(f"<li>{inline((bullet or ordered).group(1))}</li>")
            continue
        close_list()
        out.append(f"<p>{inline(stripped)}</p>")
    flush_table(); close_list()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def page_preview(model: dict[str, Any], relative: str, kind: str, payload: str | None, note: str = "") -> str:
    header = f"<h1 class='mono' style='word-break:break-all'>{e(relative)}</h1>"
    hint = f"<p class='lede'>{e(note)}</p>" if note else ""
    raw_link = f"<p style='margin:0 0 14px'><a href='/raw?path={e(relative)}'>下载原始文件</a></p>"
    if kind == "image":
        body = f"<img class='preview-img' src='/raw?path={e(relative)}' alt='{e(relative)}'>"
    elif kind == "html":
        body = (f"<p class='lede'>该文件在沙箱 iframe 中渲染，不在控制台文档内执行脚本。</p>"
                f"<iframe class='preview-frame' sandbox src='/raw?path={e(relative)}' title='{e(relative)}'></iframe>")
    elif kind == "markdown":
        body = f"<div class='card md'>{markdown_to_html(payload or '')}</div>"
    elif kind == "json":
        body = f"<pre>{e(payload or '')}</pre>"
    elif kind == "text":
        body = f"<pre>{e(payload or '')}</pre>"
    else:
        body = empty("该类型不支持预览。", "可以下载原始文件查看。")
    return header + hint + raw_link + body


def page_error(model: dict[str, Any], code: int, message: str, detail: str = "") -> str:
    return f"<h1>{code}</h1>" + empty(message, detail)


def format_json(text: str) -> str:
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except (json.JSONDecodeError, ValueError):
        return text
