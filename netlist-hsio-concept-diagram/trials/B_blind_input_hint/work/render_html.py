"""Single offline HTML: click a block to go down a level, view only, W/L·m toggle, side panel with the omitted list,
PPTX download (embedded). Usage: render_html.py <workdir> <outdir>"""
import json, sys, base64, os, html

W, OUT = sys.argv[1], sys.argv[2]
scenes = json.load(open(W + '/scenes.json'))
ann = json.load(open(OUT + '/annotations.json'))
A = json.load(open(W + '/analysis.json'))
pptx_b64 = ''
if os.path.exists(OUT + '/concept.pptx'):
    pptx_b64 = base64.b64encode(open(OUT + '/concept.pptx', 'rb').read()).decode()

# parent links (for breadcrumb)
parent = {}
for v in scenes:
    for h in v['hot']:
        parent.setdefault(h['link'], v['id'])

slim = []
for v in scenes:
    slim.append({'id': v['id'], 'cell': v['cell'], 'level': v['level'], 'title': v['title'], 'w': v['w'], 'h': v['h'],
                 'draw': v['draw'], 'hot': v['hot'], 'omitted': v['omitted'], 'notes': v['notes'],
                 'children': sorted({(h['link']) for h in v['hot']})})
summary = {
    'hs_inputs': ann['hs_inputs'], 'clock_inputs': ann['clock_inputs'], 'hs_outputs': ann['hs_outputs'],
    'buses': ann.get('_important_control_buses', {}), 'general': ann['_general_controls'], 'bias': ann['_bias'],
    'questions': [{'id': q['id'], 'item': q['item'], 'assumed': q['assumed']} for q in ann['_questions_and_assumed_answers']],
}
data = {'views': slim, 'parent': parent, 'summary': summary}

page = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RX_AFE_TOP 개념도</title>
<style>
:root{--bg:#fafaf8;--fg:#111;--mut:#666;--line:#ddd;--acc:#1d5fbf;--panel:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 "Liberation Sans",Arial,"Noto Sans KR","WenQuanYi Zen Hei",sans-serif}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:8px 16px;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
header h1{font-size:16px;margin:0}
#crumb{display:flex;flex-wrap:wrap;align-items:center;min-width:0;overflow-wrap:anywhere}
#crumb a{color:var(--acc);text-decoration:none;cursor:pointer;overflow-wrap:anywhere}
header h1,aside{overflow-wrap:anywhere}
#crumb span.sep{color:var(--mut);margin:0 4px}
.ctl{display:flex;gap:12px;align-items:center;margin-left:auto;flex-wrap:wrap}
button,.btn{font:inherit;border:1px solid var(--line);background:#fff;border-radius:6px;padding:4px 10px;cursor:pointer;color:var(--fg);text-decoration:none}
main{display:flex;gap:16px;padding:12px 16px;align-items:flex-start}
#stage{flex:1 1 auto;min-width:0;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px;overflow:auto}
#stage svg{display:block;max-width:100%;height:auto}
aside{flex:0 0 330px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:13px}
aside h2{font-size:14px;margin:10px 0 4px}
aside ul{margin:4px 0;padding-left:18px}
aside li{margin:1px 0}
.mut{color:var(--mut)}
.hot{fill:transparent;stroke:transparent;cursor:pointer}
.hot:hover{fill:rgba(29,95,191,.07);stroke:rgba(29,95,191,.55);stroke-dasharray:4 3}
body.nosize .size{display:none}
#views a{color:var(--acc);cursor:pointer}
@media (max-width:900px){main{flex-direction:column;padding:8px}aside{flex:none;width:100%}header{padding:8px}
 #stage{width:100%;-webkit-overflow-scrolling:touch}#stage svg{max-width:none;width:640px}}
</style></head><body>
<header><h1 id="ttl"></h1><div id="crumb"></div>
<div class="ctl"><button id="back" title="상위 계층">▲ 위로</button>
<label><input type="checkbox" id="wl" checked> W/L·m 표시</label>
<a class="btn" id="dl" download="concept.pptx">PPT 내려받기</a></div></header>
<main><div id="stage"></div><aside id="side"></aside></main>
<script>
const DATA = __DATA__;
const PPTX = "__PPTX__";
const NS = 'http://www.w3.org/2000/svg';
const byId = {}; DATA.views.forEach(v => byId[v.id] = v);
function el(t, a, p){const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e;}
function render(v){
  const svg = el('svg', {viewBox: `0 0 ${v.w} ${v.h}`, width: v.w, height: v.h, 'font-family': '"Liberation Sans",Arial,"Noto Sans KR","WenQuanYi Zen Hei",sans-serif', id: 'sv_' + v.id});
  el('rect', {x: 0, y: 0, width: v.w, height: v.h, fill: '#fff'}, svg);
  for (const d of v.draw){
    if (d.t === 'line'){
      el('polyline', {points: d.pts.map(p => p.join(',')).join(' '), fill: 'none', stroke: d.c, 'stroke-width': d.w,
        'stroke-linejoin': 'miter', 'stroke-linecap': 'butt', 'stroke-dasharray': d.dash || 'none', 'data-owner': d.owner || ''}, svg);
    } else if (d.t === 'poly'){
      el('polygon', {points: d.pts.map(p => p.join(',')).join(' '), fill: d.fill, stroke: d.stroke || 'none', 'stroke-width': d.w}, svg);
    } else if (d.t === 'circle'){
      el('circle', {cx: d.cx, cy: d.cy, r: d.r, fill: d.fill, stroke: d.stroke, 'stroke-width': d.w}, svg);
    } else if (d.t === 'rect'){
      el('rect', {x: d.x, y: d.y, width: d.w, height: d.h, fill: d.fill, stroke: d.stroke, 'stroke-width': d.sw, rx: d.rx || 0}, svg);
    } else if (d.t === 'text'){
      const t = el('text', {x: d.x, y: d.y, 'font-size': d.size, 'text-anchor': d.anchor, fill: d.color, 'font-weight': d.weight,
        'font-style': d.italic ? 'italic' : 'normal', 'dominant-baseline': 'central', class: d.cls, 'data-tid': d.tid}, svg);
      t.textContent = d.s;
    }
  }
  for (const h of v.hot){
    const r = el('rect', {x: h.x, y: h.y, width: h.w, height: h.h, class: 'hot', rx: 4}, svg);
    const tt = el('title', {}, r); tt.textContent = '클릭: ' + (byId[h.link] ? byId[h.link].title : h.link);
    r.addEventListener('click', () => go(h.link));
  }
  return svg;
}
function crumbs(id){const c = []; let x = id; while (x){c.unshift(x); x = DATA.parent[x];} return c;}
function go(id){ if (!byId[id]) id = DATA.views[0].id; if (location.hash !== '#' + id) location.hash = id; else show(id); }
function show(id){
  const v = byId[id] || DATA.views[0];
  document.getElementById('ttl').textContent = v.title;
  const st = document.getElementById('stage'); st.innerHTML = ''; st.appendChild(render(v));
  const cr = document.getElementById('crumb'); cr.innerHTML = '';
  crumbs(v.id).forEach((c, i, arr) => { if (i) {const s = document.createElement('span'); s.className = 'sep'; s.textContent = '›'; cr.appendChild(s);}
    const a = document.createElement('a'); a.textContent = byId[c].cell + (byId[c].level === 'unit' ? ' (unit)' : ''); a.onclick = () => go(c); cr.appendChild(a); });
  document.getElementById('back').disabled = !DATA.parent[v.id];
  const sd = document.getElementById('side'); const S = DATA.summary;
  let h = `<h2>이 화면</h2><div>${v.cell} · ${v.level === 'unit' ? '유닛(MOSFET) 레벨' : '블록 레벨'}</div>`;
  if (v.children.length){ h += '<div class="mut">클릭하면 내려감:</div><ul>' + v.children.map(c => `<li><a onclick="go('${c}')">${byId[c] ? byId[c].title : c}</a></li>`).join('') + '</ul>'; }
  h += '<h2>생략 목록 (이 화면)</h2><ul>';
  if (!v.omitted.length) h += '<li class="mut">없음</li>';
  for (const o of v.omitted){ h += o.net ? `<li>${o.net} — ${o.class}</li>` : `<li>${o.block} (${o.cell}) — ${o.reason}</li>`; }
  h += '</ul>';
  if (v.notes.length) h += '<h2>주석</h2><ul>' + v.notes.map(n => `<li>${n}</li>`).join('') + '</ul>';
  h += `<h2>분류 요약 (전체)</h2><ul><li>고속 데이터 입력: ${S.hs_inputs.join(', ')}</li><li>클럭 입력: ${S.clock_inputs.join(', ')}</li><li>고속 출력: ${S.hs_outputs.join(', ')}</li>`;
  for (const b in S.buses) h += `<li>중요 제어 버스: ${b} (${S.buses[b].bits.length}b) — ${S.buses[b].function}</li>`;
  h += `<li>일반 제어(생략): ${S.general.join(', ')}</li><li>바이어스(생략): ${S.bias.join(', ')}</li></ul>`;
  h += '<h2>가정한 답 (질문)</h2><ul>' + S.questions.map(q => `<li><b>${q.id}</b> ${q.item}: ${q.assumed}</li>`).join('') + '</ul>';
  h += '<h2>모든 화면</h2><ul id="views">' + DATA.views.map(x => `<li><a onclick="go('${x.id}')">${x.title}</a></li>`).join('') + '</ul>';
  sd.innerHTML = h;
  window.scrollTo(0, 0);
}
document.getElementById('back').onclick = () => { const v = location.hash.slice(1); if (DATA.parent[v]) go(DATA.parent[v]); };
document.getElementById('wl').onchange = e => document.body.classList.toggle('nosize', !e.target.checked);
if (PPTX) document.getElementById('dl').href = 'data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,' + PPTX;
else document.getElementById('dl').style.display = 'none';
window.addEventListener('hashchange', () => show(location.hash.slice(1)));
show(location.hash.slice(1) || DATA.views[0].id);
</script></body></html>
'''
page = page.replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__PPTX__', pptx_b64)
open(OUT + '/concept.html', 'w').write(page)
print('html bytes', len(page))
