"""Editable PPTX: one slide per view built from native shapes (freeform lines, ovals, rectangles, text boxes),
click on a block jumps to its child slide, slide notes hold the omitted list. Usage: make_pptx.py <workdir> <outdir>"""
import json, sys, copy
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

W, OUT = sys.argv[1], sys.argv[2]
scenes = json.load(open(W + '/scenes.json'))
texts = json.load(open(W + '/texts.json'))
ann = json.load(open(OUT + '/annotations.json'))
cls_md = open(OUT + '/classification.md').read()

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
EMU_IN = 914400
FONT = 'Arial'


def rgb(c):
    c = c.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    return RGBColor.from_string(c.upper())


def add_text(slide, x, y, w, h, s, size_pt, color='#111', bold=False, italic=False, align='l', valign='m', wrap=False):
    tb = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(max(w, 1))), Emu(int(max(h, 1))))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = wrap
    tf.vertical_anchor = {'m': MSO_ANCHOR.MIDDLE, 't': MSO_ANCHOR.TOP}[valign]
    p = tf.paragraphs[0]
    p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
    r = p.add_run()
    r.text = s
    f = r.font
    f.size = Pt(size_pt); f.bold = bold; f.italic = italic; f.name = FONT
    f.color.rgb = rgb(color)
    return tb


def no_shadow(shape):
    sp = shape._element.spPr
    etree.SubElement(sp, qn('a:effectLst'))
    st = shape._element.find(qn('p:style'))
    if st is not None:
        shape._element.remove(st)


slides = {}
order = [v['id'] for v in scenes]
# summary slide first
s0 = prs.slides.add_slide(blank)
add_text(s0, Inches(0.4), Inches(0.25), Inches(12), Inches(0.5), 'RX_AFE_TOP — High-Speed IO 개념도 (분류 확인 표)', 22, bold=True, valign='t')
tbl = cls_md.split('```')[1].strip().splitlines()
y = Inches(0.95)
for ln in tbl:
    add_text(s0, Inches(0.4), y, Inches(12.5), Inches(0.3), ln, 10, valign='t', wrap=True)
    y += Inches(0.1) + Inches(0.2) * (1 + len(ln) // 150)
y += Inches(0.1)
add_text(s0, Inches(0.4), y, Inches(12), Inches(0.3), '가정한 답 (질문에 답할 사람이 없어 선택한 답)', 13, bold=True, valign='t'); y += Inches(0.38)
for q in ann['_questions_and_assumed_answers']:
    s = '%s %s: %s' % (q['id'], q['item'], q['assumed'])
    tb = add_text(s0, Inches(0.4), y, Inches(12.5), Inches(0.3), s, 9, valign='t', wrap=True)
    y += Inches(0.42) if len(s) > 170 else Inches(0.27)
s0.notes_slide.notes_text_frame.text = '분류 확인 표와 질문/가정한 답 전문은 classification.md, annotations.json 참조.'

for v in scenes:
    slides[v['id']] = prs.slides.add_slide(blank)

for v in scenes:
    sl = slides[v['id']]
    top = Inches(0.75)
    avail_w, avail_h = prs.slide_width - Inches(0.6), prs.slide_height - top - Inches(0.3)
    sc = min(avail_w / v['w'], avail_h / v['h'])        # EMU per px
    ox = (prs.slide_width - v['w'] * sc) / 2
    oy = top
    X = lambda x: ox + x * sc
    Y = lambda y: oy + y * sc
    pt = lambda px: px * sc / 12700.0                   # px -> points at this scale
    add_text(sl, Inches(0.3), Inches(0.15), Inches(12.5), Inches(0.45), v['title'], 18, bold=True)
    tbox = {t['tid']: t for t in texts.get(v['id'], [])}
    for d in v['draw']:
        if d['t'] in ('line', 'poly'):
            pts = d['pts']
            closed = d['t'] == 'poly'
            fb = sl.shapes.build_freeform(int(X(pts[0][0])), int(Y(pts[0][1])), scale=1.0)
            fb.add_line_segments([(int(X(p[0])), int(Y(p[1]))) for p in pts[1:]], close=closed)
            shp = fb.convert_to_shape()
            if closed:
                if d.get('fill') and d['fill'] != 'none':
                    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(d['fill'])
                else:
                    shp.fill.background()
                if d.get('stroke'):
                    shp.line.color.rgb = rgb(d['stroke']); shp.line.width = Pt(max(pt(d['w']), 0.25))
                else:
                    shp.line.fill.background()
            else:
                shp.fill.background()
                shp.line.color.rgb = rgb(d['c']); shp.line.width = Pt(max(pt(d['w']), 0.25))
            no_shadow(shp)
        elif d['t'] == 'circle':
            r = d['r']
            shp = sl.shapes.add_shape(MSO_SHAPE.OVAL, Emu(int(X(d['cx'] - r))), Emu(int(Y(d['cy'] - r))), Emu(int(2 * r * sc)), Emu(int(2 * r * sc)))
            if d['fill'] != 'none':
                shp.fill.solid(); shp.fill.fore_color.rgb = rgb(d['fill'])
            else:
                shp.fill.background()
            shp.line.color.rgb = rgb(d['stroke']); shp.line.width = Pt(max(pt(d['w']), 0.25))
            no_shadow(shp)
        elif d['t'] == 'rect':
            shp = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(X(d['x']))), Emu(int(Y(d['y']))), Emu(int(d['w'] * sc)), Emu(int(d['h'] * sc)))
            if d['fill'] != 'none':
                shp.fill.solid(); shp.fill.fore_color.rgb = rgb(d['fill'])
            else:
                shp.fill.background()
            shp.line.color.rgb = rgb(d['stroke']); shp.line.width = Pt(max(pt(d['sw']), 0.25))
            no_shadow(shp)
    # texts after shapes (on top)
    for d in v['draw']:
        if d['t'] != 'text':
            continue
        b = tbox.get(d['tid'])
        wpx = (b['x1'] - b['x0']) if b else len(d['s']) * d['size'] * 0.6
        wpx += 6
        hpx = d['size'] * 1.4
        if d['anchor'] == 'start':
            x0, al = d['x'], 'l'
        elif d['anchor'] == 'end':
            x0, al = d['x'] - wpx, 'r'
        else:
            x0, al = d['x'] - wpx / 2, 'c'
        add_text(sl, X(x0), Y(d['y'] - hpx / 2), wpx * sc, hpx * sc, d['s'], pt(d['size']),
                 color=d['color'], bold=d['weight'] == 'bold', italic=d['italic'], align=al)
    # clickable hotspots -> child slide
    for h in v['hot']:
        if h['link'] not in slides:
            continue
        shp = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(X(h['x']))), Emu(int(Y(h['y']))), Emu(int(h['w'] * sc)), Emu(int(h['h'] * sc)))
        shp.fill.solid(); shp.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        sf = shp._element.spPr.find(qn('a:solidFill'))
        clr = sf.find(qn('a:srgbClr'))
        a = etree.SubElement(clr, qn('a:alpha')); a.set('val', '0')
        shp.line.fill.background()
        no_shadow(shp)
        shp.click_action.target_slide = slides[h['link']]
        shp.name = 'link to ' + h['link']
    # back link to parent
    parents = [p for p in scenes if any(h['link'] == v['id'] for h in p['hot'])]
    if parents:
        tb = add_text(sl, Inches(11.6), Inches(0.2), Inches(1.5), Inches(0.35), '▲ 위로 (%s)' % parents[0]['cell'], 10, color='#1d5fbf', align='r')
        tb.click_action.target_slide = slides[parents[0]['id']]
    # notes: omitted list
    lines = ['생략 목록 (이 화면):']
    for o in v['omitted']:
        lines.append(('- %s — %s' % (o['net'], o['class'])) if 'net' in o else ('- %s (%s) — %s' % (o['block'], o['cell'], o['reason'])))
    if not v['omitted']:
        lines.append('- 없음')
    if v['notes']:
        lines.append('주석:')
        lines += ['- ' + n for n in v['notes']]
    lines.append('클릭 가능한 블록 → 하위 화면: ' + ', '.join(sorted({h['link'] for h in v['hot']})) if v['hot'] else '하위 화면 없음')
    sl.notes_slide.notes_text_frame.text = '\n'.join(lines)

prs.save(OUT + '/concept.pptx')
print('slides', len(prs.slides))
