"""concept.pptx: one slide per view, every line/symbol/text as an editable native shape,
omitted list in the slide notes (plan §2)."""
import json, sys
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE

views = json.load(open(sys.argv[1])); summary = json.load(open(sys.argv[2])); out = sys.argv[3]
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
EMU_PX = 9525
WCLS = {'data': 1.6, 'clock': 3.2, 'bus': 3.2, 'power': 1.6, 'internal': 1.6}

def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

class Canvas:
    def __init__(s, slide, v, top=Inches(0.75), margin=Inches(0.3)):
        s.sl = slide
        aw, ah = prs.slide_width - 2 * margin, prs.slide_height - top - Inches(0.2)
        s.k = min(aw / (v['w'] * EMU_PX), ah / (v['h'] * EMU_PX))
        s.ox, s.oy = margin, top
    def X(s, x): return int(s.ox + x * EMU_PX * s.k)
    def Y(s, y): return int(s.oy + y * EMU_PX * s.k)
    def W(s, w): return max(Pt(0.5), int(w * EMU_PX * s.k * 0.75 * 1.0))
    def poly(s, pts, w=1.6, color='#1f2328', fill=None, closed=False, dash=False, name=None):
        if len(pts) < 2: return
        fb = s.sl.shapes.build_freeform(s.X(pts[0][0]), s.Y(pts[0][1]), scale=1.0)
        fb.add_line_segments([(s.X(x), s.Y(y)) for x, y in pts[1:]], close=closed)
        sh = fb.convert_to_shape()
        if fill and fill != 'none':
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        else:
            sh.fill.background()
        sh.line.color.rgb = rgb(color); sh.line.width = int(w * EMU_PX * s.k)
        if dash: sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if name: sh.name = name
        return sh
    def circle(s, x, y, r, fill=None, w=1.6):
        sh = s.sl.shapes.add_shape(MSO_SHAPE.OVAL, s.X(x - r), s.Y(y - r), int(2 * r * EMU_PX * s.k), int(2 * r * EMU_PX * s.k))
        if fill and fill != 'none':
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        else:
            sh.fill.background()
        sh.line.color.rgb = rgb('#1f2328'); sh.line.width = int(w * EMU_PX * s.k)
        sh.shadow.inherit = False
        return sh
    def text(s, t):
        size = t['size']; wpx = 0.6 * size * len(t['t']) + 4; hpx = size * 1.3
        x = t['x'] - (wpx - 4 if t['anchor'] == 'end' else (wpx - 4) / 2 if t['anchor'] == 'middle' else 0) - 2
        tb = s.sl.shapes.add_textbox(s.X(x), s.Y(t['y'] - size * 0.95), int(wpx * EMU_PX * s.k), int(hpx * EMU_PX * s.k))
        tf = tb.text_frame; tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = {'start': PP_ALIGN.LEFT, 'middle': PP_ALIGN.CENTER, 'end': PP_ALIGN.RIGHT}[t['anchor']]
        r = p.add_run(); r.text = t['t']
        f = r.font; f.size = Pt(max(4, size * 0.75 * EMU_PX * s.k / 9525 * 1.0)); f.name = 'Consolas'
        f.bold = bool(t.get('bold')); f.italic = bool(t.get('italic')); f.color.rgb = rgb(t['color'])
        if t.get('cls') == 'wl': tb.name = 'WL ' + t['t']
        return tb

def title(slide, text, sub=''):
    tb = slide.shapes.add_textbox(Inches(0.3), Inches(0.15), Inches(12.7), Inches(0.5))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = text; r.font.size = Pt(18); r.font.bold = True
    if sub:
        p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = sub; r2.font.size = Pt(10)
        r2.font.color.rgb = rgb('#5b6470')

# cover slide with the confirmation table
s0 = prs.slides.add_slide(BLANK)
title(s0, 'RX AFE 개념도 — 분류 확인 표', 'netlist: rx_afe_top.sp · top cell RX_AFE_TOP')
tb = s0.shapes.add_textbox(Inches(0.4), Inches(1.0), Inches(12.5), Inches(6.2))
tf = tb.text_frame; tf.word_wrap = True
for i, line in enumerate(summary['lines']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    r = p.add_run(); r.text = line; r.font.size = Pt(11); r.font.name = 'Consolas'
s0.notes_slide.notes_text_frame.text = '\n'.join(summary.get('notes', []))

for v in views:
    sl = prs.slides.add_slide(BLANK)
    title(sl, v['title'], v.get('note', ''))
    cv = Canvas(sl, v)
    for a in v['axes']:
        cv.poly([[a['x'], a['y0'] - 12], [a['x'], a['y1'] + 12]], w=1, color='#e8a0a5', dash=True)
    for w in v['wires']:
        cv.poly(w['pts'], w=WCLS.get(w['cls'], 1.6), name='net ' + (w.get('net') or ''))
    for sy in v['syms']:
        for o in sy['ops']:
            if o['t'] == 'line': cv.poly(o['pts'], w=o['w'], color=o['c'])
            elif o['t'] == 'poly': cv.poly(o['pts'], w=o['w'], color=o['c'], fill=o['fill'], closed=True)
            elif o['t'] == 'circle': cv.circle(o['x'], o['y'], o['r'], fill=o['fill'], w=o['w'])
    for p in v['ports']:
        cv.poly(p['poly'], w=1.4 if p['cls'] == 'data' else 2.4, fill='#ffffff', closed=True)
    for d in v['dots']:
        cv.circle(d[0], d[1], 3.3, fill='#1f2328', w=0.5)
    for t in v['texts']:
        if t['t'].strip(): cv.text(t)
    om = ['생략 목록 (%s):' % v['cell']] + ['- %s [%s] %s' % (o['item'], o['kind'], o['why']) for o in v['omitted']]
    if not v['omitted']: om.append('(없음)')
    links = [s['represents'][0] + ' → ' + s['link'] for s in v['syms'] if s.get('link')]
    if links: om += ['', '하위 보기: ' + ', '.join(links)]
    sl.notes_slide.notes_text_frame.text = '\n'.join(om)
prs.save(out)
print('saved', out, len(prs.slides._sldIdLst), 'slides')
