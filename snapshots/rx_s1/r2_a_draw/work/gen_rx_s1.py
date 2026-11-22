import sys, os, base64, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import BOXES, FRAMES, PORT_POS, EDGES
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
out = sys.argv[1]
os.makedirs(out, exist_ok=True)

def center(b): return (b['x']+b['w']/2, b['y']+b['h']/2)
def clip(b, tx, ty):
    cx, cy = center(b); dx, dy = tx-cx, ty-cy
    sx = (b['w']/2)/abs(dx) if dx else 1e9
    sy = (b['h']/2)/abs(dy) if dy else 1e9
    t = min(sx, sy)
    return (cx+dx*t, cy+dy*t)
def pt_of(name):
    if name.startswith('P:'): return PORT_POS[name[2:]]
    return center(BOXES[name])
def seg(a, b):
    pa, pb = pt_of(a), pt_of(b)
    if not a.startswith('P:'): pa = clip(BOXES[a], *pb)
    if not b.startswith('P:'): pb = clip(BOXES[b], *pa)
    return pa, pb

def route(a, b):
    (x1,y1),(x2,y2) = seg(a,b)
    if abs(y1-y2) < 0.5 or abs(x1-x2) < 0.5:
        return [(x1,y1),(x2,y2)]
    xm = (x1+x2)/2
    return [(x1,y1),(xm,y1),(xm,y2),(x2,y2)]
lines = []
for a, b, nets in EDGES:
    pts = route(a,b)
    lines.append(dict(a=a,b=b,nets=nets,pts=pts,label=', '.join(nets)))

def svg():
    s = ['<svg viewBox="0 0 1200 680" xmlns="http://www.w3.org/2000/svg" id="stage" style="width:100%;max-width:1200px">']
    for f in FRAMES:
        s.append(f'<rect x="{f["x"]}" y="{f["y"]}" width="{f["w"]}" height="{f["h"]}" fill="none" stroke="#888" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{f["x"]+6}" y="{f["y"]+14}" font-size="12" fill="#555">{f["title"]}</text>')
    for l in lines:
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x,y in l['pts'])
        s.append(f'<path d="{d}" fill="none" stroke="#1f3a5f" stroke-width="1.6"/>')
        mx, my = l['pts'][0][0], l['pts'][0][1]
        s.append(f'<text x="{mx+3:.1f}" y="{my-3:.1f}" font-size="9" fill="#2a5">{l["label"]}</text>')
    for k,b in BOXES.items():
        s.append(f'<rect x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" fill="#fff" stroke="#1f3a5f" stroke-width="1.6" rx="3"/>')
        s.append(f'<text x="{b["x"]+b["w"]/2}" y="{b["y"]+b["h"]/2-2}" text-anchor="middle" font-size="13" font-weight="600">{b["title"]}</text>')
        s.append(f'<text x="{b["x"]+b["w"]/2}" y="{b["y"]+b["h"]/2+14}" text-anchor="middle" font-size="10" fill="#444">{b["sub"]}</text>')

    for p,(x,y) in PORT_POS.items():
        s.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#1f3a5f"/><text x="{x+6}" y="{y+4}" font-size="11">{p}</text>')
    s.append('</svg>')
    return '\n'.join(s)

pptx_path = os.path.join(out, 'concept.pptx')
prs = Presentation(); prs.slide_width = Inches(12); prs.slide_height = Inches(6.8)
slide = prs.slides.add_slide(prs.slide_layouts[6])
def px(v): return Inches(v/100.0)
for f in FRAMES:
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(f['x']), px(f['y']), px(f['w']), px(f['h']))
    sh.fill.background(); sh.line.color.rgb = __import__("pptx").dml.color.RGBColor(0x88,0x88,0x88)
    sh.text_frame.text = f['title']; sh.text_frame.paragraphs[0].runs[0].font.size = Pt(9)
for l in lines:
    for (xa,ya),(xb,yb) in zip(l['pts'], l['pts'][1:]):
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, px(xa), px(ya), px(xb), px(yb))
for k,b in BOXES.items():
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(b['x']), px(b['y']), px(b['w']), px(b['h']))
    sh.name = 'blk_'+k
    sh.fill.solid(); sh.fill.fore_color.rgb = __import__('pptx').dml.color.RGBColor(255,255,255)
    tf = sh.text_frame; tf.text = b['title'] + '\n' + b['sub']
    for p in tf.paragraphs:
        for r in p.runs: r.font.size = Pt(9)
for p,(x,y) in PORT_POS.items():
    tb = slide.shapes.add_textbox(px(x-2), px(y-6), px(60), px(12)); tb.text_frame.text = p
    tb.text_frame.paragraphs[0].runs[0].font.size = Pt(8)
prs.save(pptx_path)

html_path = os.path.join(out, 'concept.html')
b64 = base64.b64encode(open(pptx_path,'rb').read()).decode()
html = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>rx_s1 개념도 (블록 레벨)</title>
<style>:root{{--fg:#1b1b1b;--bg:#fff}} @media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--fg:#eee;--bg:#111}}}}
body{{background:var(--bg);color:var(--fg);font-family:sans-serif;margin:16px}}
a.dl{{font-size:13px}}</style></head><body>
<h3 id="b_top">DQ_RX_UNIT (rx_s1) — 블록 레벨</h3>
<p style="font-size:13px">화면 id: b_top · 생략 목록: 바이어스 발생기(RX_BIAS), 바이어스 IBIAS, 트림 OFE/OFO, 전원, 미사용 출력 2개 (net27, net29), 모니터 없음.
질문 4개는 가정한 답으로 그렸다 (classification.md 참조).</p>
{svg()}
<p><a class="dl" download="concept.pptx" href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64}">PPT 내려받기</a></p>
</body></html>'''
open(html_path,'w',encoding='utf-8').write(html)
print('wrote', html_path, pptx_path)
