#!/usr/bin/env python3
"""Static assets for the governance console, served from /static/.

Kept as module constants rather than files on disk so the Skill package ships one
fewer directory and the server has nothing to resolve at runtime.
"""

from __future__ import annotations

# Warm paper ground, terracotta accent, quiet borders, generous line height.
# Tokens only -- every component below reads from these, so the palette is one edit.
CSS = """
:root{
  --bg:#f5f4ef; --surface:#fdfcfa; --surface-2:#f0eee8; --ink:#1f1e1c; --muted:#6b665e;
  --line:#e3e0d8; --line-strong:#cdc8bc; --accent:#c8613f; --accent-soft:#f6e9e3;
  --neg:#b03a2b; --neg-soft:#f8e6e2; --pos:#3f6b4a; --pos-soft:#e6f0e7;
  --warn:#8a6520; --warn-soft:#f7eeda; --radius:12px; --shadow:0 1px 2px rgba(31,30,28,.05);
  --mono:ui-monospace,SFMono-Regular,"Cascadia Mono",Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",sans-serif;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#1c1b19; --surface:#26241f; --surface-2:#2f2c26; --ink:#eeece6; --muted:#a49d92;
    --line:#37342d; --line-strong:#4a463d; --accent:#e08a68; --accent-soft:#3a2a22;
    --neg:#ef9583; --neg-soft:#3b2420; --pos:#8dc79c; --pos-soft:#1f3325;
    --warn:#e0b871; --warn-soft:#372c17; --shadow:0 1px 2px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --bg:#1c1b19; --surface:#26241f; --surface-2:#2f2c26; --ink:#eeece6; --muted:#a49d92;
  --line:#37342d; --line-strong:#4a463d; --accent:#e08a68; --accent-soft:#3a2a22;
  --neg:#ef9583; --neg-soft:#3b2420; --pos:#8dc79c; --pos-soft:#1f3325;
  --warn:#e0b871; --warn-soft:#372c17; --shadow:0 1px 2px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 var(--sans);
  -webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:2px}
code,.mono{font-family:var(--mono);font-size:12.8px}

.shell{display:grid;grid-template-columns:248px 1fr;min-height:100vh}
.side{background:var(--surface);border-right:1px solid var(--line);display:flex;flex-direction:column;
  position:sticky;top:0;height:100vh;overflow-y:auto}
.brand{padding:20px 20px 14px}
.brand b{display:block;font-size:15.5px;letter-spacing:-.01em}
.brand span{display:block;color:var(--muted);font-size:12px;margin-top:3px;word-break:break-all}
.nav{padding:6px 12px 18px;flex:1}
.nav h6{margin:16px 10px 6px;font-size:11px;letter-spacing:.09em;color:var(--muted);text-transform:uppercase}
.nav a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 11px;
  border-radius:8px;color:var(--ink);font-size:13.8px}
.nav a:hover{background:var(--surface-2);text-decoration:none}
.nav a[aria-current="page"]{background:var(--accent-soft);color:var(--accent);font-weight:600}
.nav .count{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.nav a[aria-current="page"] .count{color:var(--accent)}
.side .foot{padding:14px 18px;border-top:1px solid var(--line);color:var(--muted);font-size:11.5px;line-height:1.75}
.main{min-width:0;display:flex;flex-direction:column}
.topbar{display:flex;gap:14px;align-items:center;padding:13px 28px;border-bottom:1px solid var(--line);
  background:var(--surface);position:sticky;top:0;z-index:5}
.crumb{color:var(--muted);font-size:13px;flex:1;min-width:0}
.crumb a{color:var(--muted)}
.crumb b{color:var(--ink);font-weight:600}
.content{padding:26px 28px 72px;max-width:1280px;width:100%}
h1{margin:0 0 6px;font-size:22px;letter-spacing:-.015em}
.lede{margin:0 0 22px;color:var(--muted);font-size:13.6px;max-width:80ch}
h2{margin:28px 0 10px;font-size:16px}

.search{flex:0 0 320px}
.search input{width:100%;padding:8px 13px;border:1px solid var(--line-strong);border-radius:9px;
  background:var(--bg);color:var(--ink);font:13.5px var(--sans)}
.search input:focus{outline:2px solid var(--accent-soft);border-color:var(--accent)}
.btn{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);border-radius:8px;
  padding:6px 12px;font:13px var(--sans);cursor:pointer}
.btn:hover{background:var(--surface-2)}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 14px}
.filters input,.filters select{padding:7px 11px;border:1px solid var(--line-strong);border-radius:8px;
  background:var(--surface);color:var(--ink);font:13px var(--sans)}
.filters .spacer{flex:1}
.filters .result{color:var(--muted);font-size:12.5px;font-variant-numeric:tabular-nums}

.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:18px 20px;margin:0 0 16px}
.card>h3{margin:0 0 3px;font-size:14.8px}
.card>.hint{margin:0 0 13px;color:var(--muted);font-size:12.9px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));margin:0 0 22px}
.metric{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:14px 16px;box-shadow:var(--shadow)}
.metric b{display:block;font-size:26px;line-height:1.15;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.metric span{color:var(--muted);font-size:12.4px}
.metric.is-neg b{color:var(--neg)}
.metric.is-pos b{color:var(--pos)}
.metric.is-warn b{color:var(--warn)}

.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.6px;min-width:560px}
thead th{position:sticky;top:0;background:var(--surface-2);text-align:left;padding:10px 13px;
  border-bottom:1px solid var(--line);font-size:11.6px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase}
tbody td{padding:10px 13px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--surface-2)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
td.wrap{max-width:44ch}
td .detail{color:var(--muted);font-size:12.4px;margin-top:3px}

/* Hierarchy: a derived task sits visibly beneath the task that caused it. */
.twist{border:0;background:none;color:var(--muted);cursor:pointer;font-size:12px;padding:0 5px 0 0;
  width:18px;display:inline-block;transition:transform .12s ease}
.twist[aria-expanded="true"]{transform:rotate(90deg);color:var(--accent)}
.twist-space{display:inline-block;width:18px}
.indent{display:inline-block;width:calc(var(--d,0) * 22px)}
tr.depth-1 td,tr.depth-2 td,tr.depth-3 td{background:var(--surface-2)}
tr.depth-1 td:first-child,tr.depth-2 td:first-child,tr.depth-3 td:first-child{color:var(--muted)}

.badge{display:inline-block;padding:1.5px 9px;border-radius:999px;font-size:11.8px;white-space:nowrap;
  background:var(--accent-soft);color:var(--accent)}
.badge.neg{background:var(--neg-soft);color:var(--neg)}
.badge.pos{background:var(--pos-soft);color:var(--pos)}
.badge.warn{background:var(--warn-soft);color:var(--warn)}
.badge.mute{background:var(--surface-2);color:var(--muted)}
.bar{display:inline-block;height:6px;border-radius:3px;background:var(--neg);vertical-align:middle}
.empty{border:1px dashed var(--line-strong);border-radius:var(--radius);padding:28px;text-align:center;color:var(--muted)}
.empty p{margin:0 0 4px}
.kv{display:grid;grid-template-columns:minmax(104px,auto) 1fr;gap:7px 18px;font-size:13.4px;margin:0}
.kv dt{color:var(--muted)}
.kv dd{margin:0;word-break:break-word}
ul.plain{margin:6px 0;padding-left:20px}
ul.plain li{margin:3px 0}
details summary{cursor:pointer;color:var(--accent);font-size:13px;margin-top:8px}
.quote{background:var(--surface-2);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;
  padding:12px 16px;margin:0;white-space:pre-wrap;font-size:13.8px;line-height:1.75}
.timeline{list-style:none;margin:6px 0;padding:0}
.timeline li{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:baseline;
  padding:7px 0;border-bottom:1px solid var(--line)}
.timeline li:last-child{border-bottom:0}
.timeline time{color:var(--muted);font-family:var(--mono);font-size:11.8px;white-space:nowrap}
pre{background:var(--surface-2);border:1px solid var(--line);border-radius:9px;padding:13px 15px;
  overflow:auto;font-family:var(--mono);font-size:12.6px;line-height:1.6;margin:0}
.md h1,.md h2,.md h3{margin:18px 0 8px}
.md h1{font-size:19px}
.md h2{font-size:16px}
.md h3{font-size:14.5px}
.md p{margin:9px 0}
.md ul,.md ol{margin:9px 0;padding-left:22px}
.md code{background:var(--surface-2);padding:1px 5px;border-radius:4px}
.md pre code{background:none;padding:0}
.md table{min-width:0;margin:10px 0}
.md blockquote{margin:10px 0;padding:2px 14px;border-left:3px solid var(--line-strong);color:var(--muted)}
.md img{max-width:100%}
.preview-frame{width:100%;height:70vh;border:1px solid var(--line);border-radius:9px;background:#fff}
.preview-img{max-width:100%;border:1px solid var(--line);border-radius:9px;background:var(--surface-2)}
.finding{display:grid;grid-template-columns:auto 1fr;gap:11px;padding:11px 0;border-bottom:1px solid var(--line)}
.finding:last-child{border-bottom:0}
.finding p{margin:0}
.finding .detail{color:var(--muted);font-size:12.8px;margin-top:3px}
.is-hidden{display:none !important}

@media (max-width:900px){
  .shell{grid-template-columns:1fr}
  .side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
  .nav{display:flex;flex-wrap:wrap;gap:4px}
  .nav h6{width:100%;margin:8px}
  .search{flex:1 1 160px}
  .content{padding:18px 16px 48px}
}
"""

JS = """
(function(){
  var KEY='rgpw-console-theme';
  function apply(t){ if(t){document.documentElement.setAttribute('data-theme',t);} }
  try{ apply(localStorage.getItem(KEY)); }catch(e){}
  document.addEventListener('click', function(e){
    var b=e.target.closest('[data-theme-toggle]'); if(!b) return;
    var cur=document.documentElement.getAttribute('data-theme');
    var next = cur==='dark' ? 'light' : 'dark';
    apply(next); try{ localStorage.setItem(KEY,next); }catch(e){}
  });

  // Expand a main task to reveal the tasks derived from it. Child rows carry
  // data-child-of so the whole subtree toggles from a single root, at any depth.
  document.addEventListener('click', function(e){
    var t=e.target.closest('[data-expand]'); if(!t) return;
    e.preventDefault();
    var id=t.getAttribute('data-expand');
    var open=t.getAttribute('aria-expanded')==='true';
    t.setAttribute('aria-expanded', open ? 'false' : 'true');
    document.querySelectorAll('[data-child-of="'+id.replace(/"/g,'\\\\"')+'"]').forEach(function(row){
      if(open){ row.setAttribute('hidden',''); } else { row.removeAttribute('hidden'); }
    });
  });

  // Client-side filtering for list pages. Rows carry a data-filter haystack so the
  // same code serves tasks, documents and artifacts without per-page JS.
  function bindFilter(root){
    var input = root.querySelector('[data-filter-input]');
    var select = root.querySelector('[data-filter-select]');
    var result = root.querySelector('[data-filter-count]');
    var rows = Array.prototype.slice.call(root.querySelectorAll('[data-filter]'));
    if(!rows.length) return;
    function run(){
      var q = (input && input.value || '').trim().toLowerCase();
      var f = (select && select.value) || '';
      var shown = 0;
      rows.forEach(function(row){
        var hay = (row.getAttribute('data-filter')||'').toLowerCase();
        var group = row.getAttribute('data-group')||'';
        var ok = (!q || hay.indexOf(q) !== -1) && (!f || group === f);
        row.classList.toggle('is-hidden', !ok);
        if(ok) shown++;
      });
      if(result) result.textContent = shown + ' / ' + rows.length;
    }
    if(input) input.addEventListener('input', run);
    if(select) select.addEventListener('change', run);
    run();
  }
  document.querySelectorAll('[data-filter-scope]').forEach(bindFilter);

  document.addEventListener('keydown', function(e){
    if(e.key==='/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)){
      var s=document.querySelector('[data-global-search]');
      if(s){ e.preventDefault(); s.focus(); s.select(); }
    }
  });
})();
"""
