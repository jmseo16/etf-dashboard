"""Symbol library. Every symbol is built in local coordinates (grid = 10 px) and then
transformed (mirror / rotate / translate) into absolute coordinates.

A symbol instance is a dict:
  prims   : drawing primitives  ('line', x1,y1,x2,y2, cls) | ('poly', [(x,y)..], cls)
            | ('circle', cx,cy,r, cls) | ('path', d, cls) | ('text', x,y,txt, cls, anchor)
  pins    : {pin_name: (x, y, dir)}   dir in 'LRUD' = direction the wire leaves the pin
  keepout : [(x0,y0,x1,y1)]           rectangles the router must not cross
  labels  : [('text', x, y, [(txt, cls)...], anchor)]   annotation text (toggle-able)
  bbox    : (x0,y0,x1,y1)
"""
from __future__ import annotations

import math

G = 10  # routing grid

_ROT = {"U": "R", "R": "D", "D": "L", "L": "U"}
_MIR = {"L": "R", "R": "L", "U": "U", "D": "D"}

ENG = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"),
       (1e-6, "µ"), (1e-9, "n"), (1e-12, "p"), (1e-15, "f"), (1e-18, "a")]


def eng(v):
    if v is None:
        return "?"
    if v == 0:
        return "0"
    a = abs(v)
    for scale, suf in ENG:
        if a >= scale * 0.9995:
            m = v / scale
            s = f"{m:.3g}"
            if "e" in s:
                s = f"{m:.0f}"
            return s + suf
    return f"{v:.3g}"


# --------------------------------------------------------------------------
# transform helpers
# --------------------------------------------------------------------------
class Xf:
    """mirror (x -> -x) then rotate cw by rot*90 then translate."""

    def __init__(self, ox=0, oy=0, mirror=False, rot=0):
        self.ox, self.oy, self.mirror, self.rot = ox, oy, mirror, rot % 4

    def pt(self, x, y):
        if self.mirror:
            x = -x
        for _ in range(self.rot):
            x, y = -y, x
        return (x + self.ox, y + self.oy)

    def dir(self, d):
        if self.mirror:
            d = _MIR[d]
        for _ in range(self.rot):
            d = _ROT[d]
        return d

    def anchor(self, a):
        if self.rot % 2:
            return "middle"
        if self.mirror:
            return {"start": "end", "end": "start"}.get(a, a)
        return a


def transform(sym, xf):
    out = {"prims": [], "pins": {}, "keepout": [], "labels": [], "meta": sym.get("meta", {})}
    for p in sym["prims"]:
        k = p[0]
        if k == "line":
            (a, b), (c, d) = xf.pt(p[1], p[2]), xf.pt(p[3], p[4])
            out["prims"].append(("line", a, b, c, d, p[5]))
        elif k == "poly":
            out["prims"].append(("poly", [xf.pt(x, y) for x, y in p[1]], p[2]))
        elif k == "circle":
            cx, cy = xf.pt(p[1], p[2])
            out["prims"].append(("circle", cx, cy, p[3], p[4]))
        elif k == "polyline":
            out["prims"].append(("polyline", [xf.pt(x, y) for x, y in p[1]], p[2]))
        elif k == "text":
            x, y = xf.pt(p[1], p[2])
            out["prims"].append(("text", x, y, p[3], p[4], xf.anchor(p[5]) if len(p) > 5 else "middle"))
    for name, (x, y, d) in sym["pins"].items():
        px, py = xf.pt(x, y)
        out["pins"][name] = (px, py, xf.dir(d))
    for (x0, y0, x1, y1) in sym["keepout"]:
        a, b = xf.pt(x0, y0)
        c, d = xf.pt(x1, y1)
        out["keepout"].append((min(a, c), min(b, d), max(a, c), max(b, d)))
    for (x, y, parts, anchor) in sym.get("labels", []):
        lx, ly = xf.pt(x, y)
        out["labels"].append((lx, ly, parts, xf.anchor(anchor)))
    xs, ys = [], []
    for (x0, y0, x1, y1) in out["keepout"]:
        xs += [x0, x1]
        ys += [y0, y1]
    for (x, y, _) in out["pins"].values():
        xs.append(x)
        ys.append(y)
    out["bbox"] = (min(xs), min(ys), max(xs), max(ys))
    return out


# --------------------------------------------------------------------------
# transistor-level symbols (local coords, gate on the LEFT, channel at x = 0)
# --------------------------------------------------------------------------
def mos(typ, name, wl_text, m_text):
    """3-terminal MOSFET, Razavi style: arrow on the source
    (NMOS pointing out of the channel, PMOS pointing in)."""
    # Reference-figure style: the thick channel ends exactly at the drain/source stubs,
    # gate plate slightly shorter and separated by a gap, arrow on the source stub.
    pr = [
        ("line", -30, 0, -15, 0, "sym"),            # gate lead
        ("line", -15, -10, -15, 10, "sym gate"),    # gate plate
        ("line", -9, -12, -9, 12, "sym chan"),      # channel (thick)
        ("line", -9, -12, 0, -12, "sym"),           # upper stub
        ("line", 0, -12, 0, -30, "sym"),
        ("line", -9, 12, 0, 12, "sym"),             # lower stub
        ("line", 0, 12, 0, 30, "sym"),
    ]
    if typ == "pmos":
        # source on top, arrow pointing into the channel
        pr.append(("poly", [(-8.5, -12), (-3.5, -15.5), (-3.5, -8.5)], "sym arrow"))
        pins = {"s": (0, -30, "U"), "g": (-30, 0, "L"), "d": (0, 30, "D")}
    else:
        # arrow pointing away from the channel, towards the source lead
        pr.append(("poly", [(-0.6, 12), (-5.6, 8.5), (-5.6, 15.5)], "sym arrow"))
        pins = {"d": (0, -30, "U"), "g": (-30, 0, "L"), "s": (0, 30, "D")}
    labels = [
        (6, -12, [(name, "lbl-name")], "start"),
        (6, 1, [(wl_text, "lbl-wl")], "start"),
        (6, 13, [(m_text, "lbl-wl")], "start"),
    ]
    return {"prims": pr, "pins": pins,
            "keepout": [(-15, -29, 1, 29), (-29, -1, -14, 1)],
            "labels": labels,
            "meta": {"label_w": max(len(name), len(wl_text), len(m_text)) * 5.6 + 8}}


def resistor(name, val_text):
    zz = [(0, -18)]
    for i in range(6):
        zz.append((6 if i % 2 == 0 else -6, -15 + i * 6))
    zz.append((0, 18))
    pr = [("line", 0, -30, 0, -18, "sym"), ("polyline", zz, "sym"), ("line", 0, 18, 0, 30, "sym")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-7, -29, 7, 29)],
            "labels": [(11, -5, [(name, "lbl-name")], "start"), (11, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 12}}


def capacitor(name, val_text):
    pr = [("line", 0, -30, 0, -4, "sym"), ("line", -10, -4, 10, -4, "sym plate"),
          ("line", -10, 4, 10, 4, "sym plate"), ("line", 0, 4, 0, 30, "sym")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-11, -29, 11, 29)],
            "labels": [(14, -5, [(name, "lbl-name")], "start"), (14, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 14}}


def inductor(name, val_text):
    pr = [("line", 0, -30, 0, -16, "sym"), ("line", 0, 16, 0, 30, "sym")]
    for i in range(4):
        yc = -12 + i * 8
        pts = [(4 * math.sin(math.pi * k / 8), yc - 4 * math.cos(math.pi * k / 8)) for k in range(9)]
        pr.append(("polyline", pts, "sym"))
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-6, -29, 6, 29)],
            "labels": [(11, -5, [(name, "lbl-name")], "start"), (11, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 12}}


def source(kind, name, val_text):
    pr = [("line", 0, -30, 0, -12, "sym"), ("circle", 0, 0, 12, "sym"), ("line", 0, 12, 0, 30, "sym")]
    if kind == "vsrc":
        pr += [("text", 0, -3, "+", "sym-t", "middle"), ("text", 0, 8, "−", "sym-t", "middle")]
    else:
        pr += [("line", 0, 7, 0, -6, "sym"), ("poly", [(0, -8), (-3.5, -2), (3.5, -2)], "sym arrow")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-13, -29, 13, 29)],
            "labels": [(16, -5, [(name, "lbl-name")], "start"), (16, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 16}}


def generic_box(name, pin_names, title=None):
    """Fallback symbol for anything we have no drawing for (E/G/D/Q/...)."""
    n = len(pin_names)
    left = pin_names[: (n + 1) // 2]
    right = pin_names[(n + 1) // 2:]
    h = max(2, max(len(left), len(right)) + 1) * 20
    w = 60
    pr = [("polyline", [(0, 0), (w, 0), (w, h), (0, h), (0, 0)], "sym"),
          ("text", w / 2, -6, title or name, "sym-t", "middle")]
    pins = {}
    for i, p in enumerate(left):
        y = 20 * (i + 1)
        pins[p] = (-20, y, "L")
        pr += [("line", -20, y, 0, y, "sym"), ("text", 4, y + 3, p, "pin-t", "start")]
    for i, p in enumerate(right):
        y = 20 * (i + 1)
        pins[p] = (w + 20, y, "R")
        pr += [("line", w, y, w + 20, y, "sym"), ("text", w - 4, y + 3, p, "pin-t", "end")]
    return {"prims": pr, "pins": pins, "keepout": [(-19, -1, w + 19, h + 1)], "labels": [],
            "meta": {"label_w": 0}}


# --------------------------------------------------------------------------
# rail / port glyphs
# --------------------------------------------------------------------------
def ground_glyph(x, y):
    """Ground symbol hanging below (x, y)."""
    return [("line", x, y, x, y + 8, "sym"), ("line", x - 9, y + 8, x + 9, y + 8, "sym"),
            ("line", x - 6, y + 12, x + 6, y + 12, "sym"), ("line", x - 3, y + 16, x + 3, y + 16, "sym")]


def vdd_glyph(x, y, name):
    return [("line", x, y, x, y - 8, "sym"), ("line", x - 8, y - 8, x + 8, y - 8, "sym"),
            ("text", x, y - 12, name, "rail-t", "middle")]


# --------------------------------------------------------------------------
# block-level symbols
# --------------------------------------------------------------------------
def _pin_text(name):
    return name


def _arrow_in(x, y, d):
    """filled arrowhead with its tip at (x, y) pointing in direction d (R/U/L/D)"""
    if d == "R":
        pts = [(x, y), (x - 8, y - 4), (x - 8, y + 4)]
    elif d == "L":
        pts = [(x, y), (x + 8, y - 4), (x + 8, y + 4)]
    elif d == "U":
        pts = [(x, y), (x - 4, y + 8), (x + 4, y + 8)]
    else:
        pts = [(x, y), (x - 4, y - 8), (x + 4, y - 8)]
    return ("poly", pts, "arrowhead")


def _tw(names, size=9):
    return max([len(n) for n in names] + [0]) * size * 0.58


def block_symbol(shape, title, sides, pin_marks=None, arrows=()):
    """Build a block symbol.

    shape : 'amp' | 'inv' | 'sum' | 'box' | 'dff' | 'latch' | 'mux'
    sides : {'L': [pins], 'R': [pins], 'T': [pins], 'B': [pins]}
    pin_marks : {pin: '+' | '-' | 'clk'}  (polarity / clock markers)
    Local origin = top-left of the body.  Pins end on the 10 px grid.
    """
    pin_marks = pin_marks or {}
    L, R, T, B = (sides.get(k, []) for k in "LRTB")
    pr, pins = [], {}
    if shape in ("amp", "inv"):
        nl = max(len(L), 1)
        h = max(80, 20 * (nl + 1) + 20)
        h = int(math.ceil(h / 20.0) * 20)
        w = max(80, int(h * 0.9 // 20 * 20))
        mid = h / 2
        body = [(0, 0), (w, mid), (0, h), (0, 0)]
        pr.append(("polyline", body, "blk"))
        # left pins, spaced 20, centred
        ys = _spread(len(L), mid, 20)
        for p, y in zip(L, ys):
            pins[p] = (-20, y, "L")
            pr.append(("line", -20, y, 0, y, "blk"))
            if p in arrows:
                pr.append(_arrow_in(0, y, "R"))
            mk = pin_marks.get(p)
            if mk in ("+", "-"):
                pr.append(("text", 7, y + 3.5, "+" if mk == "+" else "−", "pol-t", "middle"))
        tip = w
        if shape == "inv":
            pr.append(("circle", w + 5, mid, 5, "blk"))
            tip = w + 10
        # right pins: on the slanted edges near the tip
        ys = _spread(len(R), mid, 20)
        for p, y in zip(R, ys):
            # x on the edge at height y
            ex = w * (1 - abs(y - mid) / mid) if mid else w
            if shape == "inv" and len(R) == 1:
                ex = tip
            px = int(math.ceil((max(ex, tip) + 20) / 10.0) * 10)
            pins[p] = (px, y, "R")
            pr.append(("line", ex, y, px, y, "blk"))
            mk = pin_marks.get(p)
            if mk in ("+", "-") and len(R) > 1:
                pr.append(("text", ex + 7, y + (-4 if y < mid else 11), "+" if mk == "+" else "−", "pol-t", "middle"))
        # top / bottom pins on the slanted edges
        for side, plist in (("T", T), ("B", B)):
            xs = [20 * (i + 1) for i in range(len(plist))]
            for p, x in zip(plist, xs):
                edge_y = mid * (x / w) if side == "T" else h - mid * (x / w)
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, edge_y, x, py, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, edge_y, "D" if side == "T" else "U"))
        if title:
            pr.append(("text", w * 0.36, mid + 4, title, "blk-t", "middle"))
        keep = [(-9, -9, w + 9, h + 9)]
        bw, bh = w, h
    elif shape == "sum":
        nb = max(len(B), len(T), 1)
        r = max(30, 10 * nb + 10)
        r = int(math.ceil(r / 10.0) * 10)
        cx = cy = r + 10
        pr.append(("circle", cx, cy, r, "blk"))
        pr.append(("text", cx, cy + 7, "Σ", "sum-t", "middle"))
        for side, plist in (("L", L), ("R", R)):
            ys = _spread(len(plist), cy, 20)
            for p, y in zip(plist, ys):
                dx = math.sqrt(max(r * r - (y - cy) ** 2, 0))
                ex = cx - dx if side == "L" else cx + dx
                px = -10 if side == "L" else 2 * cx + 10
                pins[p] = (px, y, side)
                pr.append(("line", px, y, ex, y, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(ex, y, "R" if side == "L" else "L"))
                mk = pin_marks.get(p)
                if mk in ("+", "-") and side == "L":
                    pr.append(("text", ex + 8, y + 3.5, "+" if mk == "+" else "−", "pol-t", "middle"))
        for side, plist in (("T", T), ("B", B)):
            xs = _spread(len(plist), cx, 20)
            for p, x in zip(plist, xs):
                dy = math.sqrt(max(r * r - (x - cx) ** 2, 0))
                ey = cy - dy if side == "T" else cy + dy
                py = -10 if side == "T" else 2 * cy + 10
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, ey, x, py, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, ey, "D" if side == "T" else "U"))
                mk = pin_marks.get(p)
                if mk in ("+", "-"):
                    pr.append(("text", x + (6 if x >= cx else -6), ey + (8 if side == "B" else -2),
                               "+" if mk == "+" else "−", "pol-t", "middle"))
        keep = [(cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9)]
        bw, bh = 2 * cx, 2 * cy
    elif shape in ("nand", "and", "nor", "or", "xor"):
        n = max(len(L), 2)
        h = max(60, 20 * (n + 1))
        h = int(math.ceil(h / 20.0) * 20)
        w = h
        mid = h / 2
        if shape in ("nand", "and"):
            body = [(0, 0), (w / 2, 0)]
            body += [(w / 2 + mid * math.sin(math.pi * k / 16), mid - mid * math.cos(math.pi * k / 16)) for k in range(1, 17)]
            body += [(0, h), (0, 0)]
            back = lambda y: 0.0
        else:
            back = lambda y: 10 * math.sin(math.pi * y / h)
            body = [(0, 0)]
            body += [(w * 0.55 * (k / 8.0) + w * 0.45 * (k / 8.0) ** 3, mid * (k / 8.0) ** 2) for k in range(1, 9)]
            body += [(w * 0.55 * (k / 8.0) + w * 0.45 * (k / 8.0) ** 3, h - mid * (k / 8.0) ** 2) for k in range(8, 0, -1)]
            body += [(0, h)]
            body += [(back(h - h * k / 12), h - h * k / 12) for k in range(1, 13)]
            if shape == "xor":
                pr.append(("polyline", [(back(h * k / 12) - 6, h * k / 12) for k in range(13)], "blk"))
        pr.append(("polyline", body, "blk"))
        ys = _spread(len(L), mid, 20)
        for p, y in zip(L, ys):
            pins[p] = (-20, y, "L")
            pr.append(("line", -20, y, back(y), y, "blk"))
            if p in arrows:
                pr.append(_arrow_in(back(y), y, "R"))
        tip = w + (10 if shape in ("nand", "nor") else 0)
        if shape in ("nand", "nor"):
            pr.append(("circle", w + 5, mid, 5, "blk"))
        for p, y in zip(R, _spread(len(R), mid, 20)):
            px = int(math.ceil((tip + 20) / 10.0) * 10)
            pins[p] = (px, y, "R")
            pr.append(("line", tip, y, px, y, "blk"))
        for side, plist in (("T", T), ("B", B)):
            for i, p in enumerate(plist):
                x = 20 * (i + 1)
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, 0 if side == "T" else h, x, py, "blk"))
        keep = [(-9, -9, w + 9 + (10 if shape in ("nand", "nor") else 0), h + 9)]
        bw, bh = w + (10 if shape in ("nand", "nor") else 0), h
    else:  # box family: box / dff / latch / mux
        tw = len(title or "") * 13 * 0.62 + 16
        tb = max(len(T), len(B))
        tb_pitch = max(40, int(math.ceil((_tw(T + B) + 14) / 10.0)) * 10)
        w = max(100, tw + _tw(L) + _tw(R) + 30, tb_pitch * (tb + 1))
        w = int(math.ceil(w / 20.0) * 20)
        n = max(len(L), len(R), 1)
        h = max(80, 20 * (n + 1) + 20)
        h = int(math.ceil(h / 20.0) * 20)
        if shape == "mux":
            body = [(0, 0), (w, 20), (w, h - 20), (0, h), (0, 0)]
        else:
            body = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
        pr.append(("polyline", body, "blk"))
        for side, plist in (("L", L), ("R", R)):
            ys = _spread(len(plist), h / 2, 20)
            for p, y in zip(plist, ys):
                px = -20 if side == "L" else w + 20
                pins[p] = (px, y, side)
                pr.append(("line", px, y, 0 if side == "L" else w, y, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(0 if side == "L" else w, y, "R" if side == "L" else "L"))
                txt = _pin_text(p)
                pr.append(("text", 5 if side == "L" else w - 5, y + 3.5, txt, "pin-t",
                           "start" if side == "L" else "end"))
        for side, plist in (("T", T), ("B", B)):
            xs = _spread(len(plist), w / 2, tb_pitch)
            for p, x in zip(plist, xs):
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, py, x, 0 if side == "T" else h, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, 0 if side == "T" else h, "D" if side == "T" else "U"))
                if pin_marks.get(p) == "clk" and shape == "dff":
                    pr.append(("polyline", [(x - 6, h), (x, h - 9), (x + 6, h)], "blk"))
                    pr.append(("text", x, h - 12, p, "pin-t", "middle"))
                else:
                    pr.append(("text", x, (12 if side == "T" else h - 6), p, "pin-t", "middle"))
        if title:
            pr.append(("text", w / 2, h / 2 + 5, title, "blk-t", "middle"))
        keep = [(-9, -9, w + 9, h + 9)]
        bw, bh = w, h
    return {"prims": pr, "pins": pins, "keepout": keep, "labels": [],
            "meta": {"w": bw, "h": bh}}


def _spread(n, center, pitch):
    """n positions on the 10-grid, `pitch` apart, centred on `center`."""
    if n == 0:
        return []
    start = center - pitch * (n - 1) / 2.0
    out = []
    for i in range(n):
        v = start + i * pitch
        out.append(int(round(v / 10.0)) * 10)
    return out
