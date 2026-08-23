#!/usr/bin/env python3
"""Render the governance audit console.

Pure rendering: this module must not import governance_artifacts, so the writer
there can call it without a cycle. It turns the agent-readable records into one
self-contained page a person can audit, which is the point -- asset review stops
being something only the agent can do.
"""

from __future__ import annotations

import json
from typing import Any


# C10 8.2 relation identities stay in the data; 8.3 rule 5 allows a display layer to
# label them for humans as long as the underlying link is not flipped.
RELATION_LABELS = {
    "affected-by": ["本次引入", "negative"],
    "observed-from": ["顺带发现", "positive"],
    "addresses": ["承接处理", "neutral"],
    "extends": ["后续增强", "neutral"],
    "refines": ["细化", "neutral"],
}

# C10 8.2 relations mean opposite things in review. Successors related by
# observed-from mean the run surfaced hidden problems; successors related by
# affected-by mean the run created the work. Chain depth follows only affected-by, so
# a repair that kept propagating is attributable to the task that started it while a
# task that merely found things is not penalised for it.
NEGATIVE_RELATIONS = ("affected-by",)
POSITIVE_RELATIONS = ("observed-from",)


def derivation_audit(state: dict[str, Any]) -> dict[str, Any]:
    """Compute the succession audit from a ProjectState document."""

    graph = state.get("task_graph", [])
    by_id = {node["task_id"]: node for node in graph}
    known = set(by_id)

    def chain_depth(task_id: str, relations: tuple[str, ...], seen: frozenset[str]) -> int:
        node = by_id.get(task_id)
        if node is None or task_id in seen:
            return 0
        deeper = [
            1 + chain_depth(link["task_id"], relations, seen | {task_id})
            for link in node.get("next_tasks", [])
            if link["relation"] in relations
        ]
        return max(deeper, default=0)

    counts: dict[str, int] = {}
    per_task: list[dict[str, Any]] = []
    dangling: list[dict[str, str]] = []
    for node in graph:
        links = node.get("next_tasks", [])
        for link in links:
            counts[link["relation"]] = counts.get(link["relation"], 0) + 1
            if link["task_id"] not in known:
                dangling.append(
                    {"task_id": node["task_id"], "target": link["task_id"], "relation": link["relation"]}
                )
        if not links and not node.get("derived_from"):
            continue
        per_task.append(
            {
                "task_id": node["task_id"],
                "caused": sum(1 for link in links if link["relation"] in NEGATIVE_RELATIONS),
                "surfaced": sum(1 for link in links if link["relation"] in POSITIVE_RELATIONS),
                "derived_from": len(node.get("derived_from", [])),
                "caused_chain_depth": chain_depth(node["task_id"], NEGATIVE_RELATIONS, frozenset()),
            }
        )
    per_task.sort(key=lambda item: (-item["caused_chain_depth"], -item["caused"], item["task_id"]))
    return {
        "available": True,
        "relation_counts": dict(sorted(counts.items())),
        "by_task": per_task,
        "recorded_but_not_created": sorted(dangling, key=lambda item: (item["task_id"], item["target"])),
    }


STYLE = """
:root{
  --bg:#f6f7f9; --panel:#fff; --ink:#16181d; --muted:#606772; --line:#dfe3e8;
  --neg:#c0392b; --neg-bg:#fdecea; --pos:#1e7a46; --pos-bg:#e8f6ee;
  --neu:#2f6fb5; --neu-bg:#eaf1fa;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#14161a; --panel:#1c1f25; --ink:#e8eaed; --muted:#9aa2ad; --line:#2c313a;
  --neg:#ff8a80; --neg-bg:#3a2320; --pos:#7ee0a8; --pos-bg:#1c3328;
  --neu:#8ab8ee; --neu-bg:#1d2a3a;
}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 72px}
header h1{margin:0 0 6px;font-size:22px}
header .meta{color:var(--muted);font-size:13px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:20px 0}
.panel>h2{margin:0 0 4px;font-size:16px}
.panel>.hint{margin:0 0 14px;color:var(--muted);font-size:13px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:520px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12.5px;letter-spacing:.04em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;white-space:nowrap}
.negative{color:var(--neg);background:var(--neg-bg)}
.positive{color:var(--pos);background:var(--pos-bg)}
.neutral{color:var(--neu);background:var(--neu-bg)}
.stats{display:flex;flex-wrap:wrap;gap:10px}
.stat{flex:1 1 150px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:24px;font-variant-numeric:tabular-nums;line-height:1.2}
.stat span{color:var(--muted);font-size:12.5px}
.empty{color:var(--muted);font-size:13.5px;padding:6px 0}
.tid{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:13px}
button.tid{background:none;border:0;color:var(--neu);cursor:pointer;padding:0;text-decoration:underline}
.chain{height:6px;border-radius:3px;background:var(--neg);display:inline-block;vertical-align:middle}
.row{padding:8px 0;border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.links{margin-top:5px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
dialog{border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--ink);
  max-width:760px;width:calc(100% - 40px);padding:0}
dialog::backdrop{background:rgba(0,0,0,.45)}
dialog .head{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;border-bottom:1px solid var(--line)}
dialog .body{padding:16px 18px;max-height:70vh;overflow:auto}
dialog h3{margin:0;font-size:15px}
dialog h4{margin:16px 0 6px;font-size:12.5px;color:var(--muted);letter-spacing:.04em}
dialog ul{margin:4px 0;padding-left:20px}
dialog li{margin:3px 0;font-size:13.5px}
.close{border:1px solid var(--line);background:none;color:var(--ink);border-radius:6px;padding:3px 10px;cursor:pointer}
footer{color:var(--muted);font-size:12.5px;margin-top:26px;line-height:1.8}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12.5px}
"""

SCRIPT = """
const D = JSON.parse(document.getElementById('payload').textContent);
const LBL = __LABELS__;
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const tag = r => { const m = LBL[r] || [r,'neutral']; return '<span class="tag ' + m[1] + '">' + esc(m[0]) + '</span>'; };
const app = document.getElementById('app');
const add = h => app.insertAdjacentHTML('beforeend', h);
const panel = (t,h,inner) => '<section class="panel"><h2>' + esc(t) + '</h2><p class="hint">' + esc(h) + '</p>' + inner + '</section>';
const none = m => '<p class="empty">' + esc(m) + '</p>';

const A = D.derivation_audit;
const counts = A.relation_counts || {};
const byTask = A.by_task || [];
const worst = byTask.reduce((m,r) => Math.max(m, r.caused_chain_depth), 0);

add('<div class="stats">'
  + '<div class="stat"><b>' + D.tasks.length + '</b><span>受控任务</span></div>'
  + '<div class="stat"><b>' + (counts['affected-by'] || 0) + '</b><span>本次引入的衍生</span></div>'
  + '<div class="stat"><b>' + (counts['observed-from'] || 0) + '</b><span>顺带发现的问题</span></div>'
  + '<div class="stat"><b>' + worst + '</b><span>最长回归链</span></div>'
  + '<div class="stat"><b>' + D.unresolved.length + '</b><span>未决项</span></div>'
  + '<div class="stat"><b>' + (D.manifest.mismatched.length ? D.manifest.mismatched.length + ' 处不符' : '完好') + '</b><span>受保护资产 ' + D.manifest.total + ' 项</span></div>'
  + '</div>');

const rows = byTask.filter(r => r.caused || r.surfaced || r.derived_from);
add(panel('衍生审计',
  '按关系符号分开统计。回归链只沿「本次引入」计算——顺带发现问题是任务在做该做的事，不该记进同一笔账。',
  rows.length
    ? '<div class="scroll"><table><thead><tr><th>任务</th><th class="num">本次引入</th><th class="num">顺带发现</th><th class="num">被派生</th><th class="num">回归链深</th><th></th></tr></thead><tbody>'
      + rows.map(r => '<tr><td><button class="tid" data-task="' + esc(r.task_id) + '">' + esc(r.task_id) + '</button></td>'
        + '<td class="num">' + (r.caused || '') + '</td><td class="num">' + (r.surfaced || '') + '</td>'
        + '<td class="num">' + (r.derived_from || '') + '</td><td class="num">' + (r.caused_chain_depth || '') + '</td>'
        + '<td>' + (r.caused_chain_depth ? '<span class="chain" style="width:' + Math.min(r.caused_chain_depth * 22, 140) + 'px"></span>' : '') + '</td></tr>').join('')
      + '</tbody></table></div>'
    : none('还没有任务记录衍生关系。')));

const dang = A.recorded_but_not_created || [];
add(panel('已识别但尚未接手',
  '被记录为衍生目标、但项目里还不存在的任务。这是「发现了却没人跟进」的线索，不是错误。',
  dang.length
    ? '<div class="scroll"><table><thead><tr><th>来源任务</th><th>目标</th><th>关系</th></tr></thead><tbody>'
      + dang.map(d => '<tr><td class="tid">' + esc(d.task_id) + '</td><td class="tid">' + esc(d.target) + '</td><td>' + tag(d.relation) + '</td></tr>').join('')
      + '</tbody></table></div>'
    : none('没有悬空的衍生目标。')));

const linked = D.tasks.filter(t => t.next_tasks.length || t.derived_from.length || t.required_by.length);
add(panel('任务血缘',
  '「被派生自」是 next_tasks 的反向边；「被依赖」是 depends_on 的反向——没修完的续作正是靠它从源头查到。',
  linked.length
    ? linked.map(t => '<div class="row"><div><button class="tid" data-task="' + esc(t.task_id) + '">' + esc(t.task_id) + '</button>'
        + ' <span style="color:var(--muted)">#' + t.ordinal + ' ' + esc(t.objective) + '</span></div><div class="links">'
        + t.next_tasks.map(l => tag(l.relation) + '<span class="tid">&rarr; ' + esc(l.task_id) + '</span>').join('')
        + t.derived_from.map(l => '<span class="tag neutral">被派生自</span><span class="tid">' + esc(l.task_id) + '</span>').join('')
        + t.required_by.map(x => '<span class="tag neutral">被依赖</span><span class="tid">' + esc(x) + '</span>').join('')
        + '</div></div>').join('')
    : none('还没有任务之间的关系。')));

add(panel('未决项与回归条件',
  'reentry_condition 说明什么条件下应该回来继续——这是「没有完全修复」的正式记录处。',
  D.unresolved.length
    ? '<div class="scroll"><table><thead><tr><th>任务</th><th>摘要</th><th>影响</th><th>负责人</th><th>回归条件</th></tr></thead><tbody>'
      + D.unresolved.map(u => '<tr><td class="tid">' + esc(u.task_id) + '</td><td>' + esc(u.summary) + '</td><td>'
        + esc(u.impact) + '</td><td>' + esc(u.owner) + '</td><td>' + esc(u.reentry_condition) + '</td></tr>').join('')
      + '</tbody></table></div>'
    : none('没有未决项。')));

add(panel('任务清单', '点任务 ID 查看契约、执行事件与终态。',
  '<div class="scroll"><table><thead><tr><th class="num">#</th><th>任务</th><th>载体</th><th>状态</th><th>风险</th><th>目标</th></tr></thead><tbody>'
  + D.tasks.map(t => '<tr><td class="num">' + t.ordinal + '</td>'
    + '<td><button class="tid" data-task="' + esc(t.task_id) + '">' + esc(t.task_id) + '</button></td>'
    + '<td><span class="tag neutral">' + esc(t.carrier) + '</span></td><td>' + esc(t.status) + '</td>'
    + '<td>' + esc(t.risk_level) + '</td><td>' + esc(t.objective) + '</td></tr>').join('')
  + '</tbody></table></div>'));

add(panel('受保护资产完整性',
  D.manifest.total + ' 项运行资产按 embedded-manifest.json 的 SHA-256 逐一核对。',
  D.manifest.mismatched.length
    ? '<div class="scroll"><table><thead><tr><th>逻辑路径</th><th>状态</th></tr></thead><tbody>'
      + D.manifest.mismatched.map(m => '<tr><td class="tid">' + esc(m) + '</td><td><span class="tag negative">哈希不符</span></td></tr>').join('')
      + '</tbody></table></div>'
    : '<p class="empty"><span class="tag positive">全部一致</span> 未发现哈希不符。</p>'));

const dlg = document.getElementById('drill');
dlg.querySelector('.close').onclick = () => dlg.close();
const sect = (title, items, fmt) => (!items || !items.length) ? '' : '<h4>' + esc(title) + '</h4><ul>' + items.map(fmt).join('') + '</ul>';
document.addEventListener('click', e => {
  const b = e.target.closest('button[data-task]');
  if (!b) return;
  const t = D.tasks.find(x => x.task_id === b.dataset.task);
  if (!t) return;
  document.getElementById('drill-title').textContent = t.task_id + ' · ' + t.carrier;
  document.getElementById('drill-body').innerHTML =
    '<p>' + esc(t.objective) + '</p>'
    + '<h4>分类</h4><ul>'
    + '<li>Delivery Scenario：' + esc(t.delivery_scenario || '-') + '</li>'
    + '<li>Development Type：' + esc((t.development_types || []).join('、') || '-') + '</li>'
    + '<li>Change Surface：' + esc((t.change_surfaces || []).join('、') || '-') + '</li>'
    + '<li>Risk：' + esc(t.risk_level || '-') + '</li></ul>'
    + sect('允许路径', t.allowed_paths, x => '<li class="tid">' + esc(x) + '</li>')
    + sect('验收', t.acceptance, x => '<li>' + esc(x) + '</li>')
    + sect('执行事件', t.events, x => '<li><span class="tag neutral">' + esc(x.event_type) + '</span> ' + esc(x.summary)
        + ' <span style="color:var(--muted)">' + esc(x.timestamp) + '</span></li>')
    + sect('成立事实', t.established_facts, x => '<li>' + esc(x) + '</li>')
    + sect('实际变化', t.actual_changes, x => '<li>' + esc(x) + '</li>')
    + sect('衍生', t.next_tasks, l => '<li>' + tag(l.relation) + ' <span class="tid">' + esc(l.task_id) + '</span> — ' + esc(l.reason) + '</li>');
  dlg.showModal();
});
"""

TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>治理审计台 · __PROJECT__</title>
<style>__STYLE__</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>治理审计台</h1>
  <div class="meta">__PROJECT__ · 生成于 __GENERATED__ · 由 <code>generate_audit_console.py</code> 从受控记录重建</div>
</header>
<div id="app"></div>
<footer>
  本页是 DerivedView，可随时重建，<strong>不是新事实的来源</strong>。结论以 TaskContract、RunLedger、TaskOutcome 和 ProjectState 为准（C10 §8.0）。<br>
  关系标签是显示层措辞，底层存的是 C10 §8.2 受控关系值（§8.3 允许显示层另行标注）。
</footer>
</div>
<dialog id="drill">
  <div class="head"><h3 id="drill-title"></h3><button class="close">关闭</button></div>
  <div class="body" id="drill-body"></div>
</dialog>
<script id="payload" type="application/json">__DATA__</script>
<script>__SCRIPT__</script>
</body>
</html>
"""


def render(payload: dict[str, Any]) -> str:
    """Return one self-contained page. No network, no build step, no dependencies."""

    # A literal </script> inside either embedded block would close the host element
    # early, so both the data and the code are escaped for that sequence.
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    script = SCRIPT.replace("__LABELS__", json.dumps(RELATION_LABELS, ensure_ascii=False))
    return (
        TEMPLATE.replace("__STYLE__", STYLE)
        .replace("__SCRIPT__", script)
        .replace("__PROJECT__", str(payload.get("project_id", "")))
        .replace("__GENERATED__", str(payload.get("generated_at", "")))
        .replace("__DATA__", data)
    )
