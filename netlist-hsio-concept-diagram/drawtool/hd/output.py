"""Files written by the tool: HTML viewer, PPTX, reports."""
import base64
import json
import os
from collections import OrderedDict
from xml.sax.saxutils import escape
from . import render as RD
from .analyze import KTEXT, VISIBLE
from . import netlist as NL
from .views import _compress

CLS_KO = {'hs_data': '고속 데이터', 'hs_clock': '고속 클럭', 'reference': '기준', 'status': '상태 출력', 'bias': '바이어스', 'hidden': '일반 제어(숨김)',
          'rail': '전원', 'other': '내부'}


def classification(A, cells, top, views):
    """(markdown text, dict) of the port classification."""
    tp = [p for p in cells[top].ports if p not in A.rails]
    rows = []
    info = OrderedDict()
    for p in tp:
        if p in A.data_seeds:
            c, k, why = '고속 데이터 입력', '', '패드/차동쌍 → 입력 트랜지스터 → 샘플러 데이터 입력'
        elif p in A.clk_seeds:
            c, k, why = '고속 클럭 입력', '', '클럭 역할 게이트(꼬리·프리차지·latch 전달 게이트)에 도달'
        elif p in A.out_ports and A.cls.get(p) == 'status':
            c, k, why = '상태 출력', 'O1', '안에서 구동, 고속 추적이 닿지 않음'
        elif p in A.out_ports:
            c, k, why = '고속 출력 (%s)' % CLS_KO.get(A.cls.get(p), ''), '', '고속 추적이 닿는 출력'
        elif p in A.ref:
            c, k, why = '기준', '', '차동쌍 한쪽 입력(다른 쪽이 고속 데이터)'
        elif p in A.port_k:
            kk = A.port_k[p]
            k = kk if kk != 'status_in' else 'K9'
            vis = kk in VISIBLE or kk == 'status_in'
            c = ('중요 제어' if vis else ('바이어스' if kk == 'K11' else '일반 제어')) + ' — ' + KTEXT.get(k, k)
            why = A.port_why.get(p, '')
        else:
            c, k, why = CLS_KO.get(A.cls.get(p, 'other'), '내부'), '', ''
        draw = '그림' if (A.cls.get(p) in VISIBLE or p in A.data_seeds or p in A.clk_seeds) else '숨김'
        info[p] = {'class': c, 'k': k, 'why': why, 'draw': draw}
    # one line per bus
    groups = OrderedDict()
    for p in tp:
        s, ix = NL.bus_split(p)
        key = (s if ix is not None else p, info[p]['class'], info[p]['k'], info[p]['draw'])
        groups.setdefault(key, []).append(p)
    md = ['# 분류 확인 표 — %s' % top, '',
          '고속 데이터 입력 : %s' % (', '.join(_compress(A.data_seeds)) or '(없음)'),
          '클럭 입력        : %s' % (', '.join(_compress(A.clk_seeds)) or '(없음)'),
          '고속 출력        : %s' % (', '.join(_compress(sorted(p for p in A.out_ports if A.cls.get(p) != 'status'))) or '(없음)'),
          '중요 제어        : %s' % (', '.join('%s (%s)' % (n, A.port_k[ps[0]] if A.port_k[ps[0]] != 'status_in' else 'K9')
                                             for n, ps in _bus_groups([p for p in tp if p in A.port_k and (A.port_k[p] in VISIBLE or A.port_k[p] == 'status_in')])) or '(없음)'),
          '숨김             : %s' % (', '.join('%s (%s)' % (n, A.port_k[ps[0]]) for n, ps in _bus_groups([p for p in tp if p in A.port_k and A.port_k[p] not in VISIBLE and A.port_k[p] != 'status_in'])) or '(없음)'),
          '질문             : %d개' % len(A.questions), '',
          '| 포트 | 분류 | 끝점 | 근거 | 그림 |', '|---|---|---|---|---|']
    for (stem, c, k, draw), ps in groups.items():
        name = _compress(ps)[0] if len(ps) > 1 else ps[0]
        md.append('| `%s` | %s | %s | %s | %s |' % (name, c, k, info[ps[0]]['why'], draw))
    md += ['', '## 질문과 가정한 답', '']
    if not A.questions:
        md.append('(없음 — 구조로 모두 정해졌습니다)')
    for q in A.questions:
        md.append('- **%s** — %s  \n  선택지: %s  \n  가정한 답: **%s**' % (q['id'], q['q'], ' / '.join(q['options']), q['default']))
    return '\n'.join(md) + '\n', info


def _bus_groups(ports):
    g = OrderedDict()
    for p in ports:
        s, ix = NL.bus_split(p)
        g.setdefault(s if ix is not None else p, []).append(p)
    return [(_compress(ps)[0] if len(ps) > 1 else ps[0], ps) for ps in g.values()]


def html(scenes, views, summary_lines, questions, pptx_bytes, title):
    parent = {}
    for S in scenes:
        for sym in S['symbols']:
            if sym.get('target') and sym['target'] not in parent and sym['target'] != S['id']:
                parent[sym['target']] = S['id']
    data = OrderedDict()
    for S in scenes:
        data[S['id']] = {'title': S['title'], 'svg': RD.svg(S), 'omitted': S.get('omitted', []), 'legend': S.get('legend', []),
                         'parent': parent.get(S['id'], ''), 'children': sorted(set(sym['target'] for sym in S['symbols'] if sym.get('target')))}
    b64 = base64.b64encode(pptx_bytes).decode('ascii') if pptx_bytes else ''
    js = json.dumps(data, ensure_ascii=False)
    page = u'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title><style>
body{margin:0;font-family:Helvetica,Arial,sans-serif;background:#f4f4f2;color:#111}
#bar{display:flex;gap:10px;align-items:center;padding:8px 14px;background:#fff;border-bottom:1px solid #ccc;position:sticky;top:0}
#bar h1{font-size:16px;margin:0;flex:1}#bar button,#bar label{font-size:13px;padding:4px 10px;border:1px solid #bbb;background:#fff;border-radius:4px;cursor:pointer}
#wrap{display:flex;gap:14px;padding:14px;align-items:flex-start;flex-wrap:wrap}
#fig{background:#fff;border:1px solid #ccc;border-radius:6px;overflow:auto;max-width:100%%;flex:1 1 640px}
#side{flex:0 0 320px;background:#fff;border:1px solid #ccc;border-radius:6px;padding:10px 14px;font-size:13px;line-height:1.5}
#side h2{font-size:14px;margin:12px 0 4px}#side ul{margin:0;padding-left:18px}#side a{color:#1a56a0;cursor:pointer}
.hot:hover rect:last-child{fill:#1a56a0;fill-opacity:.08}
</style></head><body>
<div id="bar"><h1 id="ttl"></h1><button id="up">▲ 위로</button><label><input type="checkbox" id="wl" checked> W/L·m 표시</label><button id="ppt">PPT 내려받기</button></div>
<div id="wrap"><div id="fig"></div><div id="side"></div></div>
<script>
var D=%(js)s, SUM=%(summ)s, Q=%(q)s, PPT="%(b64)s", FIRST="%(first)s";
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function show(id){ if(!D[id]) id=FIRST; var v=D[id];
 document.getElementById('ttl').textContent=v.title;
 document.getElementById('fig').innerHTML=v.svg;
 var h='<h2>이 화면</h2><div>'+esc(id)+'</div>';
 if(v.children.length){h+='<div style="color:#666">클릭하면 내려감:</div><ul>'+v.children.map(function(c){return '<li><a data-go="'+c+'">'+esc(D[c].title)+'</a></li>';}).join('')+'</ul>';}
 h+='<h2>생략 목록</h2><ul>'+(v.omitted.length?v.omitted.map(function(x){return '<li>'+esc(x)+'</li>';}).join(''):'<li>(없음)</li>')+'</ul>';
 h+='<h2>주석</h2><ul>'+(v.legend.length?v.legend.map(function(x){return '<li>'+esc(x)+'</li>';}).join(''):'<li>(없음)</li>')+'</ul>';
 h+='<h2>분류 요약</h2><ul>'+SUM.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';
 h+='<h2>질문 (가정한 답)</h2><ul>'+(Q.length?Q.map(function(x){return '<li>'+esc(x)+'</li>';}).join(''):'<li>(없음)</li>')+'</ul>';
 h+='<h2>모든 화면</h2><ul>'+Object.keys(D).map(function(k){return '<li><a data-go="'+k+'">'+esc(D[k].title)+'</a></li>';}).join('')+'</ul>';
 document.getElementById('side').innerHTML=h;
 document.getElementById('up').disabled=!v.parent; document.getElementById('up').onclick=function(){location.hash=v.parent;};
 applyWL();
 Array.prototype.forEach.call(document.querySelectorAll('.hot'),function(g){g.onclick=function(){location.hash=g.getAttribute('data-target');};});
 Array.prototype.forEach.call(document.querySelectorAll('[data-go]'),function(a){a.onclick=function(){location.hash=a.getAttribute('data-go');};});
}
function applyWL(){var on=document.getElementById('wl').checked;Array.prototype.forEach.call(document.querySelectorAll('.sz'),function(t){t.style.display=on?'':'none';});}
document.getElementById('wl').onchange=applyWL;
document.getElementById('ppt').onclick=function(){ if(!PPT){alert('PPTX가 들어 있지 않습니다');return;}
 var b=atob(PPT),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
 var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([u],{type:'application/vnd.openxmlformats-officedocument.presentationml.presentation'}));a.download='concept.pptx';a.click();};
window.onhashchange=function(){show(location.hash.slice(1));}; show(location.hash.slice(1)||FIRST);
</script></body></html>''' % {'title': escape(title), 'js': js.replace('</', '<\\/'), 'summ': json.dumps(summary_lines, ensure_ascii=False),
                               'q': json.dumps(questions, ensure_ascii=False), 'b64': b64, 'first': scenes[0]['id']}
    return page


def pptx(scenes, summary_lines, path):
    """Editable PPTX: one summary slide and one slide per screen. Returns True when written."""
    try:
        from pptx import Presentation
        from pptx.util import Emu, Pt
        from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
        from pptx.dml.color import RGBColor
    except Exception:
        return False
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    blank = prs.slide_layouts[6]
    sl = prs.slides.add_slide(blank)
    tb = sl.shapes.add_textbox(Emu(400000), Emu(300000), Emu(11000000), Emu(6000000))
    tb.text_frame.text = 'HSIO 개념도 — 요약'
    for ln in summary_lines:
        p = tb.text_frame.add_paragraph()
        p.text = ln
        p.font.size = Pt(12)
    for S in scenes:
        sl = prs.slides.add_slide(blank)
        k = min(11600000.0 / S['w'], 6000000.0 / S['h'])
        ox, oy = 300000, 600000

        def X(v):
            return Emu(int(ox + v * k))

        def Y(v):
            return Emu(int(oy + v * k))
        t = sl.shapes.add_textbox(Emu(300000), Emu(100000), Emu(11000000), Emu(400000))
        t.text_frame.text = S['title']
        t.text_frame.paragraphs[0].font.size = Pt(16)

        def line(x1, y1, x2, y2):
            c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, X(x1), Y(y1), X(x2), Y(y2))
            c.line.color.rgb = RGBColor(0x11, 0x11, 0x11)
            c.line.width = Pt(1.0)

        def shape(v):
            if v[0] == 'line':
                line(v[1], v[2], v[3], v[4])
            elif v[0] == 'rect':
                r = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, X(v[1]), Y(v[2]), Emu(int(v[3] * k)), Emu(int(v[4] * k)))
                r.fill.background()
                r.line.color.rgb = RGBColor(0x11, 0x11, 0x11)
            elif v[0] == 'circle':
                r = sl.shapes.add_shape(MSO_SHAPE.OVAL, X(v[1] - v[3]), Y(v[2] - v[3]), Emu(int(2 * v[3] * k)), Emu(int(2 * v[3] * k)))
                r.fill.background()
                r.line.color.rgb = RGBColor(0x11, 0x11, 0x11)
            elif v[0] == 'fpoly':
                fb = sl.shapes.build_freeform(X(v[1][0][0]), Y(v[1][0][1]), scale=1.0)
                fb.add_line_segments([(X(a), Y(b)) for a, b in v[1][1:]], close=True)
                f = fb.convert_to_shape()
                f.fill.solid()
                f.fill.fore_color.rgb = RGBColor(0x11, 0x11, 0x11)
                f.line.color.rgb = RGBColor(0x11, 0x11, 0x11)
            else:
                pts = v[1] + ([v[1][0]] if v[0] == 'poly' else [])
                for a, b in zip(pts, pts[1:]):
                    line(a[0], a[1], b[0], b[1])
        for w in S['wires']:
            for s in w['segs']:
                line(*s)
        for l in S['labels']:
            if l.get('seg'):
                line(*l['seg'])
        for tg in S['tags']:
            for v in tg['shapes']:
                shape(v)
        for sym in S['symbols']:
            for v in sym['shapes']:
                shape(v)
        import math
        for x, y, d in S.get('humps', []):
            r = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, X(x - 5), Y(y - 5), Emu(int(10 * k)), Emu(int(10 * k)))
            r.fill.solid()
            r.fill.fore_color.rgb = RGBColor(0xff, 0xff, 0xff)
            r.line.fill.background()
            if d == 'h':
                line(x, y - 7, x, y + 7)
                pts = [(x - 5 * math.cos(math.pi * i / 6), y - 5 * math.sin(math.pi * i / 6)) for i in range(7)]
            else:
                line(x - 7, y, x + 7, y)
                pts = [(x + 5 * math.sin(math.pi * i / 6), y - 5 * math.cos(math.pi * i / 6)) for i in range(7)]
            for a, b in zip(pts, pts[1:]):
                line(a[0], a[1], b[0], b[1])
        for p in S['ports']:
            shape(['poly', p['shape']])
        for x, y in S['dots']:
            shape(['circle', x, y, 3])
        for T in S['texts']:
            b = T['bbox']
            tb = sl.shapes.add_textbox(X(b[0]), Y(b[1] - 2), Emu(int((b[2] - b[0] + 6) * k)), Emu(int((b[3] - b[1] + 4) * k)))
            tf = tb.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.text = T['s']
            tf.paragraphs[0].font.size = Pt(max(4, T['size'] * k / 12700.0 * 0.95))
        notes = sl.notes_slide.notes_text_frame
        notes.text = '생략 목록:\n' + '\n'.join(S.get('omitted', []))
    prs.save(path)
    return True
