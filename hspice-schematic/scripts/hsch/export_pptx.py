"""Scene -> editable PowerPoint (.pptx).

Everything is a native PowerPoint shape, so the drawing can be edited in PowerPoint:
  * one slide per cell of the hierarchy (same order as the viewer)
  * every device / block / pin is a named group (move it as one piece)
  * every wire is a straight line, grouped per net ("net QP")
  * every label is a real text box (W/L, names, values, pin names)
  * clicking a block in slide-show mode jumps to the slide of its cell, and each lower
    level has a "▲ parent" link back - the same drill-down as the HTML viewer
"""
from __future__ import annotations

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .geom import vpin_shape
from .verify import text_width

INK = RGBColor(0x11, 0x11, 0x11)
BLUE = RGBColor(0x1D, 0x5F, 0xA8)
GREY = RGBColor(0x55, 0x55, 0x55)
PURPLE = RGBColor(0x6B, 0x4F, 0x9E)
RED = RGBColor(0xE8, 0x26, 0x1C)
DARKRED = RGBColor(0x8C, 0x0D, 0x07)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# font px per text class (same as the viewer CSS), plus style
TEXT_STYLE = {
    "lbl-name": (9, GREY, False, True), "lbl-wl": (9, BLUE, False, False),
    "lbl-val": (9, BLUE, False, False), "lbl-cell": (9, RGBColor(0x77, 0x77, 0x77), False, False),
    "lbl-net": (10, PURPLE, False, True), "lbl-port": (10, INK, True, False),
    "lbl-rail": (10, INK, True, False), "term-t": (10, INK, True, False),
    "pin-t": (9, RGBColor(0x33, 0x33, 0x33), False, False), "blk-t": (13, INK, True, False),
    "sum-t": (22, INK, False, False), "pol-t": (12, INK, True, False),
    "rail-t": (10, INK, True, False), "sym-t": (10, INK, False, False),
}
STROKE = {"chan": 3.2, "gate": 2.0, "plate": 2.2}

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
MARGIN_X, TOP, BOTTOM = Inches(0.35), Inches(0.75), Inches(0.3)


class _Map:
    def __init__(self, bounds):
        x0, y0, x1, y1 = bounds
        w = SLIDE_W - 2 * MARGIN_X
        h = SLIDE_H - TOP - BOTTOM
        self.s = min(w / max(x1 - x0, 1), h / max(y1 - y0, 1))     # EMU per px
        self.ox = MARGIN_X + (w - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = TOP + (h - (y1 - y0) * self.s) / 2 - y0 * self.s

    def x(self, v):
        return Emu(int(self.ox + v * self.s))

    def y(self, v):
        return Emu(int(self.oy + v * self.s))

    def d(self, v):
        return Emu(max(1, int(v * self.s)))

    def pt(self, px):
        return Pt(max(px * self.s / 12700.0, 0.25))


def _style_line(line, m, width_px=1.6, color=INK):
    line.color.rgb = color
    line.width = m.pt(width_px)


def _line(shapes, m, x1, y1, x2, y2, width_px=1.6, color=INK, name=None):
    c = shapes.add_connector(MSO_CONNECTOR.STRAIGHT, m.x(x1), m.y(y1), m.x(x2), m.y(y2))
    _style_line(c.line, m, width_px, color)
    if name:
        c.name = name
    return c


def _poly(shapes, m, pts, closed, fill=None, width_px=1.6, color=INK):
    fb = shapes.build_freeform(m.x(pts[0][0]), m.y(pts[0][1]), scale=1.0)
    fb.add_line_segments([(m.x(x), m.y(y)) for x, y in pts[1:]], close=closed)
    shp = fb.convert_to_shape()
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    _style_line(shp.line, m, width_px, color)
    shp.shadow.inherit = False
    return shp


def _circle(shapes, m, cx, cy, r, fill=None, width_px=1.6, color=INK):
    shp = shapes.add_shape(MSO_SHAPE.OVAL, m.x(cx - r), m.y(cy - r), m.d(2 * r), m.d(2 * r))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if width_px:
        _style_line(shp.line, m, width_px, color)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def _text(shapes, m, x, y, runs, anchor="start", rot=False, name=None):
    """runs: [(text, css_class)]; (x, y) is the SVG text anchor / baseline."""
    runs = [(t, c) for t, c in runs if t]
    if not runs:
        return None
    size = max(TEXT_STYLE.get(c, (10,))[0] for _, c in runs)
    w = sum(text_width(t, size, 0.62) for t, _ in runs) + 4
    h = size * 1.35
    if rot:   # rotate(-90): text runs upwards from (x, y) for anchor=start
        cx = x - size * 0.3
        cy = y - w / 2 if anchor == "start" else (y + w / 2 if anchor == "end" else y)
        left, top = cx - w / 2, cy - h / 2
    else:
        left = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
        if anchor == "start":
            left -= 1
        top = y - size * 1.0
    tb = shapes.add_textbox(m.x(left), m.y(top), m.d(w), m.d(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = {"start": PP_ALIGN.LEFT, "end": PP_ALIGN.RIGHT}.get(anchor, PP_ALIGN.CENTER)
    for t, c in runs:
        px, color, bold, italic = TEXT_STYLE.get(c, (10, INK, False, False))
        r = p.add_run()
        r.text = t
        r.font.size = m.pt(px)
        r.font.name = "Arial"
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        if any(ord(ch) >= 0x1100 for ch in t):
            _east_asian(r, "Malgun Gothic")
    if rot:
        tb.rotation = 270
    if name:
        tb.name = name
    return tb


def _transparent(shape):
    from pptx.oxml.ns import qn
    clr = shape.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    a = clr.makeelement(qn("a:alpha"), {"val": "0"})
    clr.append(a)


def _east_asian(run, face):
    from pptx.oxml.ns import qn
    rpr = run._r.get_or_add_rPr()
    ea = rpr.find(qn("a:ea"))
    if ea is None:
        ea = rpr.makeelement(qn("a:ea"), {})
        rpr.append(ea)
    ea.set("typeface", face)


def _prims(shapes, m, prims):
    for p in prims:
        k = p[0]
        if k == "line":
            cls = p[5].split()
            w = max([STROKE.get(c, 0) for c in cls] + [1.6])
            _line(shapes, m, p[1], p[2], p[3], p[4], w)
        elif k == "polyline":
            closed = len(p[1]) > 2 and p[1][0] == p[1][-1]
            pts = p[1][:-1] if closed else p[1]
            fill = WHITE if ("blk" in p[2] and closed) else None
            _poly(shapes, m, pts, closed, fill=fill)
        elif k == "poly":
            _poly(shapes, m, p[1], True, fill=INK, width_px=0.6)
        elif k == "circle":
            _circle(shapes, m, p[1], p[2], p[3], fill=WHITE if "blk" in p[4] else None)
        elif k == "text":
            _text(shapes, m, p[1], p[2], [(p[3], p[4].split()[0])], p[5] if len(p) > 5 else "middle")


def export_pptx(scenes, info, order, out_path, title=None, show_net_names=False):
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    blank = prs.slide_layouts[6]
    slides = {c: prs.slides.add_slide(blank) for c in order}
    parent_of = {}
    for c in order:
        for s in scenes[c]["symbols"]:
            if s["kind"] == "X" and s["ref"] in slides:
                parent_of.setdefault(s["ref"], (c, s["inst"]))
    for c in order:
        sc, slide = scenes[c], slides[c]
        m = _Map(sc["bounds"])
        ci = info["cells"].get(c, {})
        head = slide.shapes.add_textbox(Inches(0.35), Inches(0.2), Inches(9), Inches(0.4))
        tp = head.text_frame.paragraphs[0]
        r = tp.add_run()
        r.text = ci.get("display", c)
        r.font.size, r.font.bold, r.font.name = Pt(20), True, "Arial"
        r = tp.add_run()
        r.text = "   " + ci.get("label", "") + ("  ·  연결 검증 완료 (netlist와 일치)" if ci.get("verify", {}).get("ok") else "")
        r.font.size, r.font.name = Pt(11), "Arial"
        r.font.color.rgb = GREY
        _east_asian(r, "Malgun Gothic")
        if c in parent_of:
            pc, pinst = parent_of[c]
            up = slide.shapes.add_textbox(Inches(10.4), Inches(0.22), Inches(2.6), Inches(0.35))
            up.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
            ur = up.text_frame.paragraphs[0].add_run()
            ur.text = f"▲ {pc}"
            ur.font.size, ur.font.name = Pt(11), "Arial"
            ur.font.color.rgb = BLUE
            up.click_action.target_slide = slides[pc]
            up.name = "link to parent"
        # wires, one group per net
        by_net = {}
        for w in sc["wires"]:
            by_net.setdefault(w["net"], []).append(w)
        for d in sc["dots"]:
            by_net.setdefault(d["net"], [])
        for net, ws in by_net.items():
            g = slide.shapes.add_group_shape()
            g.name = f"net {net}"
            for w in ws:
                _line(g.shapes, m, w["x1"], w["y1"], w["x2"], w["y2"])
            for d in sc["dots"]:
                if d["net"] == net:
                    _circle(g.shapes, m, d["x"], d["y"], 2.6, fill=INK, width_px=0)
            if not ws and not any(d["net"] == net for d in sc["dots"]):
                g._element.getparent().remove(g._element)
        # devices / blocks
        for s in sc["symbols"]:
            g = slide.shapes.add_group_shape()
            g.name = s["inst"]
            if s["kind"] == "X" and s["ref"] in slides:
                bx0, by0, bx1, by1 = s.get("body") or s["bbox"]
                hit = g.shapes.add_shape(MSO_SHAPE.RECTANGLE, m.x(bx0), m.y(by0), m.d(bx1 - bx0), m.d(by1 - by0))
                hit.fill.solid()
                hit.fill.fore_color.rgb = WHITE
                _transparent(hit)                    # invisible click target
                hit.line.fill.background()
                hit.shadow.inherit = False
                hit.click_action.target_slide = slides[s["ref"]]
                hit.name = f"open {s['ref']}"
            _prims(g.shapes, m, s["prims"])
            for (lx, ly, parts, anc) in s["labels"]:
                _text(g.shapes, m, lx, ly, parts, anc)
        # rails
        for r_ in sc["rails"]:
            g = slide.shapes.add_group_shape()
            g.name = f"{r_['kind']} {r_['net']}"
            _prims(g.shapes, m, r_["prims"])
            if r_.get("named"):
                _text(g.shapes, m, r_["x"] + 12, r_["y"] + 16, [(r_["net"], "rail-t")], "start")
        # pins and name tags
        for t in sc["terminals"]:
            g = slide.shapes.add_group_shape()
            g.name = f"pin {t['net']}" if t.get("vpin") else f"label {t['net']}"
            if t.get("vpin"):
                _poly(g.shapes, m, vpin_shape(t["vpin"], t["x"], t["y"], t["vdir"]), True,
                      fill=RED, width_px=0.9, color=DARKRED)
            _text(g.shapes, m, t["tx"], t["ty"], [(t["net"], "term-t")], t["anchor"], rot=t.get("rot", False))
        for l in sc["labels"]:
            if l["cls"] == "lbl-net" and not show_net_names:
                continue     # same default as the viewer ("넷 이름" off)
            _text(slide.shapes, m, l["x"], l["y"], [(l["text"], l["cls"])], l["anchor"], name=f"label {l['net']}")
        notes = slide.notes_slide.notes_text_frame
        notes.text = (f"{c}: {ci.get('label', '')}\n인식 근거: {ci.get('reason', '')}\n"
                      f"포트: {', '.join(ci.get('ports', []))}\n"
                      f"블록을 클릭하면(슬라이드 쇼) 그 블록의 슬라이드로 이동합니다.")
    prs.save(out_path)
    return out_path
