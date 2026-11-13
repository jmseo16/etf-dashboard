"""concept.html: single offline file, view-only, click a block to descend, W/L·m toggle,
omitted list in the side panel, embedded PPTX download."""
import json, sys, base64, os, html

views = json.load(open(sys.argv[1]))
rep = json.load(open(sys.argv[2])) if os.path.exists(sys.argv[2]) else {'views': []}
pptx = sys.argv[3]; out = sys.argv[4]
summary = json.load(open(sys.argv[5])) if len(sys.argv) > 5 and os.path.exists(sys.argv[5]) else {}
b64 = base64.b64encode(open(pptx, 'rb').read()).decode() if os.path.exists(pptx) else ''
R = {r['view']: {'ok': r['connectivity_ok'], 'counts': r['counts'], 'errors': r['errors'][:5],
                 'structural': [c['why'] for c in r['quality']['structural_crossing']]} for r in rep['views']}

page = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RX AFE 개념도</title>
<style>
:root{--bg:#f6f7f9;--panel:#ffffff;--ink:#1f2328;--muted:#5b6470;--line:#d9dde3;--accent:#1f6feb;--ok:#1a7f37;--bad:#cf222e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 "Noto Sans KR","WenQuanYi Zen Hei","Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 16px;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
header h1{font-size:16px;margin:0;font-weight:700}
#crumbs{display:flex;flex-wrap:wrap;gap:4px;align-items:center;font-size:13px}
#crumbs a{color:var(--accent);text-decoration:none;cursor:pointer}
#crumbs span.sep{color:var(--muted)}
.tools{margin-left:auto;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.tools label{font-size:13px;display:flex;gap:4px;align-items:center;cursor:pointer}
.btn{border:1px solid var(--line);background:#fff;border-radius:6px;padding:4px 10px;font:inherit;font-size:13px;color:var(--ink);text-decoration:none;cursor:pointer}
main{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px;padding:12px 16px}
#stage{background:#fff;border:1px solid var(--line);border-radius:8px;overflow:auto;-webkit-overflow-scrolling:touch;align-self:start}
#stage svg{display:block;width:100%;height:auto;min-width:560px}
#vtitle{font-weight:700;padding:10px 12px 0}
#vnote{color:var(--muted);font-size:12px;padding:2px 12px 8px}
aside{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;font-size:13px;align-self:start}
aside h2{font-size:13px;margin:12px 0 6px;color:var(--muted);text-transform:none}
aside h2:first-child{margin-top:0}
aside ul{margin:0;padding-left:16px}
aside li{margin:2px 0}
.ok{color:var(--ok);font-weight:700}.bad{color:var(--bad);font-weight:700}
code{font-family:"DejaVu Sans Mono",Consolas,monospace;font-size:12px}
.clk{cursor:pointer}
#svgwrap text,#svgwrap circle{pointer-events:none}
.clk:hover rect{fill:rgba(31,111,235,.08);stroke:var(--accent);stroke-dasharray:4 3}
.hide-wl .wl{display:none}
table.om{border-collapse:collapse;width:100%}
table.om td{border-top:1px solid var(--line);padding:3px 4px;vertical-align:top}
@media (max-width:820px){main{grid-template-columns:1fr;padding:8px}#stage svg{min-width:640px}header{padding:8px}}
</style></head><body>
<header><h1>RX AFE 개념도</h1><nav id="crumbs"></nav>
<div class="tools"><label><input type="checkbox" id="wl" checked> W/L·m 표시</label>
<a class="btn" id="dl" download="concept.pptx">PPT 내려받기</a></div></header>
<main><section id="stage"><div id="vtitle"></div><div id="vnote"></div><div id="svgwrap"></div></section>
<aside id="side"></aside></main>
<script>
const VIEWS = __VIEWS__;
const REP = __REP__;
const SUMMARY = __SUMMARY__;
const PPTX = "__PPTX__";
const byId = Object.fromEntries(VIEWS.map(v => [v.id, v]));
const W = {data:1.6, clock:3.2, bus:3.2, power:1.6, internal:1.6};
let stack = [{id: VIEWS[0].id, label: VIEWS[0].cell}];
function esc(s){return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function pts(p){return p.map(q => q[0].toFixed(1)+','+q[1].toFixed(1)).join(' ');}
function op(o){
  if(o.t==='line') return `<polyline points="${pts(o.pts)}" fill="none" stroke="${o.c}" stroke-width="${o.w}" stroke-linejoin="round" stroke-linecap="round"/>`;
  if(o.t==='poly') return `<polygon points="${pts(o.pts)}" fill="${o.fill}" stroke="${o.c}" stroke-width="${o.w}"/>`;
  if(o.t==='circle') return `<circle cx="${o.x}" cy="${o.y}" r="${o.r}" fill="${o.fill}" stroke="${o.c}" stroke-width="${o.w}"/>`;
  return '';
}
function render(v){
  let s = `<svg viewBox="0 0 ${v.w} ${v.h}" style="max-width:${Math.max(v.w, 640)}px" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans Mono, Consolas, Menlo, monospace">`;
  s += `<rect width="${v.w}" height="${v.h}" fill="#ffffff"/>`;
  for(const a of v.axes) s += `<line x1="${a.x}" y1="${a.y0-12}" x2="${a.x}" y2="${a.y1+12}" stroke="#d1242f" stroke-opacity=".45" stroke-width="1" stroke-dasharray="6 5"/>`;
  for(const w of v.wires) s += `<polyline class="w-${w.cls}" points="${pts(w.pts)}" fill="none" stroke="#1f2328" stroke-width="${W[w.cls]||1.6}" stroke-linejoin="round"><title>${esc(w.net||'')}</title></polyline>`;
  for(const sy of v.syms){
    let g = sy.ops.map(op).join('');
    if(sy.link && byId[sy.link]){
      const b = sy.body;
      s += `<g class="clk" data-link="${sy.link}" data-label="${esc(sy.represents[0]||sy.id)}"><title>${esc((sy.represents||[]).join(', '))} → ${esc(byId[sy.link].cell)} (클릭: 하위 보기)</title>${g}<rect x="${b[0]-4}" y="${b[1]-4}" width="${b[2]-b[0]+8}" height="${b[3]-b[1]+8}" fill="rgba(0,0,0,0)" stroke="none"/></g>`;
    } else s += `<g><title>${esc((sy.represents||[]).join(', '))}</title>${g}</g>`;
  }
  for(const p of v.ports) s += `<polygon points="${pts(p.poly)}" fill="#fff" stroke="#1f2328" stroke-width="${p.cls==='data'?1.4:2.4}"/>`;
  for(const d of v.dots) s += `<circle cx="${d[0]}" cy="${d[1]}" r="3.3" fill="#1f2328"/>`;
  for(const t of v.texts){
    s += `<text x="${t.x}" y="${t.y}" font-size="${t.size}" text-anchor="${t.anchor}" fill="${t.color}"${t.cls?` class="${t.cls}"`:''}${t.italic?' font-style="italic"':''}${t.bold?' font-weight="700"':''}>${esc(t.t)}</text>`;
  }
  return s + '</svg>';
}
function side(v){
  const r = REP[v.id] || {};
  let h = `<h2>보기</h2><div><b>${esc(v.cell)}</b> · ${v.level==='block'?'블록 레벨':'유닛 레벨'}</div>`;
  if(r.counts){
    const bad = Object.entries(r.counts).filter(([k,c]) => c && k!=='structural_crossing');
    h += `<h2>검증 (§6)</h2><div>연결 대조: ${r.ok?'<span class="ok">통과</span>':'<span class="bad">실패</span>'}</div>`;
    h += `<div>품질 검사: ${bad.length?bad.map(([k,c])=>`<span class="bad">${k} ${c}</span>`).join(', '):'<span class="ok">모두 0</span>'}</div>`;
    if(r.structural && r.structural.length) h += `<div>구조상 교차 ${r.structural.length}: <ul>${r.structural.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`;
  }
  const links = v.syms.filter(s => s.link && byId[s.link]);
  if(links.length) h += `<h2>하위 보기 (클릭)</h2><ul>${links.map(s=>`<li><a href="#" data-link="${s.link}" data-label="${esc(s.represents[0]||s.id)}">${esc(s.represents.join(', '))}</a> → ${esc(byId[s.link].cell)}</li>`).join('')}</ul>`;
  h += `<h2>생략 목록</h2>`;
  if(!v.omitted.length) h += '<div>(없음)</div>';
  else h += `<table class="om">${v.omitted.map(o=>`<tr><td><code>${esc(o.item)}</code></td><td>${o.kind==='net'?'넷':o.kind==='device'?'소자':'블록'}</td><td>${esc(o.why)}</td></tr>`).join('')}</table>`;
  if(v.id === VIEWS[0].id && SUMMARY.lines){
    h += `<h2>분류 요약</h2><pre style="white-space:pre-wrap;font-size:12px;margin:0">${esc(SUMMARY.lines.join('\n'))}</pre>`;
  }
  return h;
}
function show(){
  const cur = stack[stack.length-1]; const v = byId[cur.id];
  document.getElementById('vtitle').textContent = v.title;
  document.getElementById('vnote').textContent = v.note || '';
  document.getElementById('svgwrap').innerHTML = render(v);
  document.getElementById('side').innerHTML = side(v);
  document.getElementById('crumbs').innerHTML = stack.map((c,i)=> i<stack.length-1 ? `<a data-i="${i}">${esc(c.label)}</a><span class="sep">›</span>` : `<b>${esc(c.label)}</b>`).join('');
  document.querySelectorAll('[data-link]').forEach(el => el.addEventListener('click', e => {
    e.preventDefault(); const id = el.getAttribute('data-link');
    stack.push({id, label: el.getAttribute('data-label') + ' (' + byId[id].cell + ')'}); sync(); show();
  }));
  document.querySelectorAll('#crumbs a').forEach(el => el.addEventListener('click', () => {
    stack = stack.slice(0, +el.getAttribute('data-i') + 1); sync(); show();
  }));
  applyWL();
}
function sync(){ try{ history.replaceState(null, '', '#v=' + stack.map(c=>c.id).join('/')); }catch(e){} }
function applyWL(){ document.getElementById('svgwrap').classList.toggle('hide-wl', !document.getElementById('wl').checked); }
document.getElementById('wl').addEventListener('change', applyWL);
const dl = document.getElementById('dl');
if(PPTX) dl.href = 'data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,' + PPTX; else dl.style.display='none';
(function init(){
  const m = location.hash.match(/v=([^&]+)/);
  if(m){ const ids = m[1].split('/').filter(id => byId[id]);
    if(ids.length) stack = ids.map(id => ({id, label: byId[id].cell})); }
  show();
})();
window.__views = VIEWS.map(v => v.id);
</script></body></html>'''
page = page.replace('__VIEWS__', json.dumps(views, ensure_ascii=False)).replace('__REP__', json.dumps(R, ensure_ascii=False))
page = page.replace('__SUMMARY__', json.dumps(summary, ensure_ascii=False)).replace('__PPTX__', b64)
open(out, 'w').write(page)
print('wrote', out, len(page) // 1024, 'KB')
