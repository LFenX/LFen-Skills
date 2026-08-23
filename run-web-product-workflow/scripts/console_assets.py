#!/usr/bin/env python3
"""Static assets for the governance console, served from /static/.

Kept as module constants rather than files on disk so the Skill package ships one
fewer directory and the server has nothing to resolve at runtime.
"""

from __future__ import annotations

CSS = """
:root{
  --bg:#f4f6f8; --surface:#ffffff; --surface-2:#fafbfc; --ink:#14171c; --muted:#5c6470;
  --line:#e0e4e9; --line-strong:#c9d0d8; --accent:#2563a8; --accent-soft:#e9f1fa;
  --neg:#b3261e; --neg-soft:#fdecea; --pos:#166b3f; --pos-soft:#e6f4ec;
  --warn:#8a5a00; --warn-soft:#fdf2df; --radius:10px; --shadow:0 1px 2px rgba(16,24,40,.06);
  --mono:ui-monospace,SFMono-Regular,"Cascadia Mono",Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",sans-serif;
}
:root[data-theme="dark"], :root:not([data-theme="light"]) {}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#101318; --surface:#171b21; --surface-2:#1d222a; --ink:#e6e9ee; --muted:#98a1ad;
    --line:#272d36; --line-strong:#39414d; --accent:#7fb3ea; --accent-soft:#17263a;
    --neg:#ff9d94; --neg-soft:#3a211f; --pos:#7fd8a6; --pos-soft:#16301f;
    --warn:#f2c26b; --warn-soft:#332912; --shadow:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --bg:#101318; --surface:#171b21; --surface-2:#1d222a; --ink:#e6e9ee; --muted:#98a1ad;
  --line:#272d36; --line-strong:#39414d; --accent:#7fb3ea; --accent-soft:#17263a;
  --neg:#ff9d94; --neg-soft:#3a211f; --pos:#7fd8a6; --pos-soft:#16301f;
  --warn:#f2c26b; --warn-soft:#332912; --shadow:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.6 var(--sans);}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code,.mono{font-family:var(--mono);font-size:12.8px}

/* layout */
.shell{display:grid;grid-template-columns:236px 1fr;min-height:100vh}
.side{background:var(--surface);border-right:1px solid var(--line);display:flex;flex-direction:column;
  position:sticky;top:0;height:100vh;overflow-y:auto}
.brand{padding:16px 18px 12px;border-bottom:1px solid var(--line)}
.brand b{display:block;font-size:15px;letter-spacing:.01em}
.brand span{display:block;color:var(--muted);font-size:12px;margin-top:2px;word-break:break-all}
.nav{padding:10px 10px 16px;flex:1}
.nav h6{margin:14px 8px 6px;font-size:11px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase}
.nav a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 10px;border-radius:7px;
  color:var(--ink);font-size:13.6px}
.nav a:hover{background:var(--surface-2);text-decoration:none}
.nav a[aria-current="page"]{background:var(--accent-soft);color:var(--accent);font-weight:600}
.nav .count{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.nav a[aria-current="page"] .count{color:var(--accent)}
.side .foot{padding:12px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:11.5px}
.main{min-width:0;display:flex;flex-direction:column}
.topbar{display:flex;gap:14px;align-items:center;padding:12px 24px;border-bottom:1px solid var(--line);
  background:var(--surface);position:sticky;top:0;z-index:5}
.crumb{color:var(--muted);font-size:13px;flex:1;min-width:0}
.crumb a{color:var(--muted)}
.crumb b{color:var(--ink)}
.content{padding:22px 24px 64px;max-width:1240px;width:100%}
h1{margin:0 0 4px;font-size:20px}
.lede{margin:0 0 20px;color:var(--muted);font-size:13.4px;max-width:78ch}
h2{margin:26px 0 10px;font-size:15.5px}

/* controls */
.search{flex:0 0 300px;position:relative}
.search input{width:100%;padding:7px 11px;border:1px solid var(--line-strong);border-radius:8px;
  background:var(--surface-2);color:var(--ink);font:13.5px var(--sans)}
.search input:focus{outline:2px solid var(--accent-soft);border-color:var(--accent)}
.btn{border:1px solid var(--line-strong);background:var(--surface);color:var(--ink);border-radius:7px;
  padding:6px 11px;font:13px var(--sans);cursor:pointer}
.btn:hover{background:var(--surface-2)}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 14px}
.filters input,.filters select{padding:6px 10px;border:1px solid var(--line-strong);border-radius:7px;
  background:var(--surface);color:var(--ink);font:13px var(--sans)}
.filters .spacer{flex:1}
.filters .result{color:var(--muted);font-size:12.5px;font-variant-numeric:tabular-nums}

/* surfaces */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:16px 18px;margin:0 0 16px}
.card>h3{margin:0 0 3px;font-size:14.5px}
.card>.hint{margin:0 0 12px;color:var(--muted);font-size:12.8px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));margin:0 0 20px}
.metric{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px;
  box-shadow:var(--shadow)}
.metric b{display:block;font-size:25px;line-height:1.15;font-variant-numeric:tabular-nums}
.metric span{color:var(--muted);font-size:12.4px}
.metric.is-neg b{color:var(--neg)} .metric.is-pos b{color:var(--pos)} .metric.is-warn b{color:var(--warn)}

/* table */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.6px;min-width:560px}
thead th{position:sticky;top:0;background:var(--surface-2);text-align:left;padding:9px 12px;
  border-bottom:1px solid var(--line);font-size:11.6px;letter-spacing:.05em;color:var(--muted);text-transform:uppercase}
tbody td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--surface-2)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
td.wrap{max-width:44ch}

/* atoms */
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11.8px;white-space:nowrap;
  background:var(--accent-soft);color:var(--accent)}
.badge.neg{background:var(--neg-soft);color:var(--neg)}
.badge.pos{background:var(--pos-soft);color:var(--pos)}
.badge.warn{background:var(--warn-soft);color:var(--warn)}
.badge.mute{background:var(--surface-2);color:var(--muted)}
.bar{display:inline-block;height:6px;border-radius:3px;background:var(--neg);vertical-align:middle}
.empty{border:1px dashed var(--line-strong);border-radius:var(--radius);padding:26px;text-align:center;color:var(--muted)}
.empty p{margin:0 0 4px}
.kv{display:grid;grid-template-columns:minmax(96px,auto) 1fr;gap:6px 16px;font-size:13.4px;margin:0}
.kv dt{color:var(--muted)}
.kv dd{margin:0;word-break:break-word}
ul.plain{margin:6px 0;padding-left:19px}
ul.plain li{margin:3px 0}
.timeline{list-style:none;margin:6px 0;padding:0}
.timeline li{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:baseline;
  padding:6px 0;border-bottom:1px solid var(--line)}
.timeline li:last-child{border-bottom:0}
.timeline time{color:var(--muted);font-family:var(--mono);font-size:11.8px;white-space:nowrap}
pre{background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:12px 14px;
  overflow:auto;font-family:var(--mono);font-size:12.6px;line-height:1.55;margin:0}
.md h1,.md h2,.md h3{margin:18px 0 8px}
.md h1{font-size:19px} .md h2{font-size:16px} .md h3{font-size:14.5px}
.md p{margin:8px 0} .md ul,.md ol{margin:8px 0;padding-left:22px}
.md code{background:var(--surface-2);padding:1px 5px;border-radius:4px}
.md pre code{background:none;padding:0}
.md table{min-width:0;margin:10px 0}
.md blockquote{margin:10px 0;padding:2px 14px;border-left:3px solid var(--line-strong);color:var(--muted)}
.md img{max-width:100%}
.preview-frame{width:100%;height:70vh;border:1px solid var(--line);border-radius:8px;background:#fff}
.preview-img{max-width:100%;border:1px solid var(--line);border-radius:8px;background:var(--surface-2)}
.finding{display:grid;grid-template-columns:auto 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}
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
  var KEY='rwpw-console-theme';
  function apply(t){ if(t){document.documentElement.setAttribute('data-theme',t);} }
  try{ apply(localStorage.getItem(KEY)); }catch(e){}
  document.addEventListener('click', function(e){
    var b=e.target.closest('[data-theme-toggle]'); if(!b) return;
    var cur=document.documentElement.getAttribute('data-theme');
    var next = cur==='dark' ? 'light' : 'dark';
    apply(next); try{ localStorage.setItem(KEY,next); }catch(e){}
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
