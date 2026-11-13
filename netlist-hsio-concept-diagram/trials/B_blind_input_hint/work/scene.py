"""Scene model: every view = drawing primitives + semantic objects (symbols with pins, wires, dots, labels, ports).
Renderers (HTML/PPTX) only use 'draw' primitives + hotspots; the checker only uses semantic objects + geometry."""
import math

BLACK = '#111'
GRAY = '#777'
CLK_W = 3.2
DATA_W = 1.6
BUS_W = 3.2
SYM_W = 1.6


def fmt_si(v):
    return v


class View:
    def __init__(self, vid, cell, level, title, w, h, scope=None):
        self.id = vid; self.cell = cell; self.level = level; self.title = title
        self.w = w; self.h = h
        self.draw = []          # primitives
        self.symbols = []       # semantic symbols
        self.wires = []
        self.dots = []
        self.labels = []        # net labels / gray labels / ports (all name a net)
        self.texts = []         # every text primitive id (for overlap check) is in draw with 'tid'
        self.hot = []           # clickable hotspots
        self.symmetry = []
        self.allowed_cross = []
        self.notes = []
        self.omitted = []       # list of dicts
        self.scope = scope      # list of member element names covered by this view (None = whole cell)
        self.extra_checks = {}
        self._tid = 0

    # ---------------- primitives ----------------
    def line(self, pts, w=SYM_W, c=BLACK, dash=None, owner=None):
        self.draw.append({'t': 'line', 'pts': [list(map(float, p)) for p in pts], 'w': w, 'c': c, 'dash': dash, 'owner': owner})

    def poly(self, pts, fill=BLACK, stroke=None, w=1.0, owner=None):
        self.draw.append({'t': 'poly', 'pts': [list(map(float, p)) for p in pts], 'fill': fill, 'stroke': stroke, 'w': w, 'owner': owner})

    def circle(self, cx, cy, r, fill='none', stroke=BLACK, w=SYM_W, owner=None):
        self.draw.append({'t': 'circle', 'cx': cx, 'cy': cy, 'r': r, 'fill': fill, 'stroke': stroke, 'w': w, 'owner': owner})

    def rect(self, x, y, w, h, fill='none', stroke=BLACK, sw=SYM_W, dash=None, owner=None, rx=0):
        self.draw.append({'t': 'rect', 'x': x, 'y': y, 'w': w, 'h': h, 'fill': fill, 'stroke': stroke, 'sw': sw, 'dash': dash, 'owner': owner, 'rx': rx})

    def text(self, x, y, s, size=12, anchor='start', color=BLACK, weight='normal', italic=False, cls='lbl', owner=None, base='middle'):
        self._tid += 1
        tid = '%s_t%d' % (self.id, self._tid)
        self.draw.append({'t': 'text', 'x': x, 'y': y, 's': s, 'size': size, 'anchor': anchor, 'color': color,
                          'weight': weight, 'italic': italic, 'cls': cls, 'owner': owner, 'tid': tid, 'base': base})
        return tid

    # ---------------- semantic ----------------
    def wire(self, pts, cls='data', net=None):
        pts = [list(map(float, p)) for p in pts]
        w = {'data': DATA_W, 'clock': CLK_W, 'bus': BUS_W, 'plain': DATA_W, 'power': DATA_W}[cls]
        self.wires.append({'pts': pts, 'cls': cls, 'net': net})
        self.draw.append({'t': 'line', 'pts': pts, 'w': w, 'c': BLACK, 'dash': None, 'owner': 'wire', 'cls': cls})
        return pts

    def dot(self, x, y):
        self.dots.append([float(x), float(y)])
        self.draw.append({'t': 'circle', 'cx': x, 'cy': y, 'r': 3.2, 'fill': BLACK, 'stroke': BLACK, 'w': 0.5, 'owner': 'dot'})

    def netlabel(self, name, ax, ay, tx=None, ty=None, anchor='start', gray=False, size=11, kind='net'):
        """net label: names the wire (or pin) at (ax, ay)"""
        if tx is None:
            tx, ty = ax + 4, ay - 8
        tid = self.text(tx, ty, name, size=size, anchor=anchor, color=GRAY if gray else BLACK, cls='gray' if gray else 'netlabel')
        self.labels.append({'name': name, 'at': [float(ax), float(ay)], 'kind': kind, 'tid': tid})

    def port(self, name, x, y, d='right', io='in', cls='data', label_side=None):
        """Virtuoso pin glyph. (x,y) = attach point (wire end). d = direction the glyph points."""
        L, H = 18, 10
        w = 2.2 if cls in ('clock', 'bus') else 1.4
        if d == 'right':
            pts = [(x - L, y - H / 2), (x - 6, y - H / 2), (x, y), (x - 6, y + H / 2), (x - L, y + H / 2)]
            if io == 'out':
                pts = [(x, y - H / 2), (x + L - 6, y - H / 2), (x + L, y), (x + L - 6, y + H / 2), (x, y + H / 2)]
        elif d == 'left':
            pts = [(x + L, y - H / 2), (x + 6, y - H / 2), (x, y), (x + 6, y + H / 2), (x + L, y + H / 2)]
            if io == 'out':
                pts = [(x, y - H / 2), (x - L + 6, y - H / 2), (x - L, y), (x - L + 6, y + H / 2), (x, y + H / 2)]
        elif d == 'up':
            pts = [(x - H / 2, y + L), (x - H / 2, y + 6), (x, y), (x + H / 2, y + 6), (x + H / 2, y + L)]
            if io == 'out':
                pts = [(x - H / 2, y), (x - H / 2, y - L + 6), (x, y - L), (x + H / 2, y - L + 6), (x + H / 2, y)]
        else:  # down
            pts = [(x - H / 2, y - L), (x - H / 2, y - 6), (x, y), (x + H / 2, y - 6), (x + H / 2, y - L)]
            if io == 'out':
                pts = [(x - H / 2, y), (x - H / 2, y + L - 6), (x, y + L), (x + H / 2, y + L - 6), (x + H / 2, y)]
        self.poly(pts, fill='#fff', stroke=BLACK, w=w, owner='port')
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        bb = [min(xs), min(ys), max(xs), max(ys)]
        if label_side is None:
            label_side = {'right': 'left' if io == 'in' else 'right', 'left': 'right' if io == 'in' else 'left',
                          'up': 'below' if io == 'in' else 'above', 'down': 'above' if io == 'in' else 'below'}[d]
        if label_side == 'left':
            tid = self.text(bb[0] - 4, y, name, size=12, anchor='end', weight='bold', cls='port')
        elif label_side == 'right':
            tid = self.text(bb[2] + 4, y, name, size=12, anchor='start', weight='bold', cls='port')
        elif label_side == 'above':
            tid = self.text(x, bb[1] - 8, name, size=12, anchor='middle', weight='bold', cls='port')
        else:
            tid = self.text(x, bb[3] + 9, name, size=12, anchor='middle', weight='bold', cls='port')
        self.labels.append({'name': name, 'at': [float(x), float(y)], 'kind': 'port', 'tid': tid, 'io': io})
        self.symbols.append({'id': 'pin_' + name + '_%d' % len(self.symbols), 'kind': 'portglyph', 'body': [bb], 'pins': [], 'members': []})

    # ---------------- symbols ----------------
    def add_symbol(self, sid, kind, body, pins, members, link=None, info=None):
        s = {'id': sid, 'kind': kind, 'body': body, 'pins': pins, 'members': members, 'link': link, 'info': info or {}}
        self.symbols.append(s)
        if link:
            xs = [b[0] for b in body] + [b[2] for b in body]
            ys = [b[1] for b in body] + [b[3] for b in body]
            self.hot.append({'x': min(xs) - 4, 'y': min(ys) - 4, 'w': max(xs) - min(xs) + 8, 'h': max(ys) - min(ys) + 8, 'link': link, 'sym': sid})
        return s


def pin(name, x, y, terms):
    """terms: list (per slice) of list of (element, terminal). For block instances element=inst name, terminal=port."""
    return {'name': name, 'x': float(x), 'y': float(y), 'terms': terms}


# ============================ device symbols ============================
def mos(V, sid, cx, cy, mtype, gate='left', name='', size='', top=None, bot=None, gterm=None, link=None,
        name_side=None, members=None, extra_info=None, arrow_at=None):
    """Razavi 3-terminal MOS. (cx,cy): drain/source column x, center y.
    top/bot/gterm: per-slice lists of (element, terminal) for the top pin, bottom pin and gate.
    Pins: top (cx, cy-30), bottom (cx, cy+30), gate (cx-40 or cx+40, cy)."""
    s = -1 if gate == 'left' else 1
    chx = cx + s * 14
    gpx = cx + s * 20
    V.line([(chx, cy - 18), (chx, cy + 18)], w=2.6, owner=sid)
    V.line([(gpx, cy - 14), (gpx, cy + 14)], w=2.0, owner=sid)
    V.line([(cx + s * 40, cy), (gpx, cy)], w=SYM_W, owner=sid)
    V.line([(chx, cy - 12), (cx, cy - 12), (cx, cy - 30)], w=SYM_W, owner=sid)
    V.line([(chx, cy + 12), (cx, cy + 12), (cx, cy + 30)], w=SYM_W, owner=sid)
    # arrow on the (structural) source lead
    if mtype == 'n':
        ay = cy + 12 if arrow_at != 'top' else cy - 12
        tip = cx - s * 1
        V.poly([(tip, ay), (tip + s * 7, ay - 4), (tip + s * 7, ay + 4)], owner=sid)
    else:
        ay = cy - 12 if arrow_at != 'bottom' else cy + 12
        tip = chx - s * 1
        V.poly([(tip, ay), (tip - s * 7, ay - 4), (tip - s * 7, ay + 4)], owner=sid)
    ns = name_side or ('right' if gate == 'left' else 'left')
    if ns == 'right':
        tx, anc = cx + 6, 'start'
    else:
        tx, anc = cx - 6, 'end'
    if name:
        V.text(tx, cy - 7, name, size=11, anchor=anc, italic=True, cls='devname', owner=sid)
    if size:
        lines = size if isinstance(size, list) else [size]
        for i, ln in enumerate(lines):
            V.text(tx, cy + 7 + i * 12, ln, size=10, anchor=anc, color='#555', cls='size', owner=sid)
    bx0, bx1 = sorted([gpx, chx])
    body = [[bx0 - 1, cy - 18, bx1 + 1, cy + 18]]
    pins = [pin('T', cx, cy - 30, top), pin('B', cx, cy + 30, bot), pin('G', cx + s * 40, cy, gterm)]
    return V.add_symbol(sid, 'nmos' if mtype == 'n' else 'pmos', body, pins, members or [], link,
                        dict(cx=cx, cy=cy, gate=gate, **(extra_info or {})))


def res(V, sid, x, y, orient='v', name='', size='', a=None, b=None, var=False, members=None, label_side='right'):
    if orient == 'v':
        pts = [(x, y - 30), (x, y - 20)]
        n = 6
        for i in range(n):
            yy = y - 20 + (i + 0.5) * 40 / n
            pts.append((x + (6 if i % 2 == 0 else -6), yy))
        pts += [(x, y + 20), (x, y + 30)]
        V.line(pts, owner=sid)
        body = [[x - 7, y - 20, x + 7, y + 20]]
        pins = [pin('A', x, y - 30, a), pin('B', x, y + 30, b)]
    else:
        pts = [(x - 30, y), (x - 20, y)]
        n = 6
        for i in range(n):
            xx = x - 20 + (i + 0.5) * 40 / n
            pts.append((xx, y + (-6 if i % 2 == 0 else 6)))
        pts += [(x + 20, y), (x + 30, y)]
        V.line(pts, owner=sid)
        body = [[x - 20, y - 7, x + 20, y + 7]]
        pins = [pin('A', x - 30, y, a), pin('B', x + 30, y, b)]
    if var:
        _var_arrow(V, x, y, sid)
        body = [[x - 16, y - 16, x + 16, y + 16]]
    _dev_text(V, x, y, orient, name, size, label_side, sid, off=20 if var else 10)
    return V.add_symbol(sid, 'varres' if var else 'res', body, pins, members or [], None, dict(x=x, y=y))


def cap(V, sid, x, y, orient='v', name='', size='', a=None, b=None, var=False, members=None, label_side='right'):
    if orient == 'v':
        V.line([(x, y - 30), (x, y - 4)], owner=sid)
        V.line([(x - 12, y - 4), (x + 12, y - 4)], w=2.4, owner=sid)
        V.line([(x - 12, y + 4), (x + 12, y + 4)], w=2.4, owner=sid)
        V.line([(x, y + 4), (x, y + 30)], owner=sid)
        body = [[x - 12, y - 5, x + 12, y + 5]]
        pins = [pin('A', x, y - 30, a), pin('B', x, y + 30, b)]
    else:
        V.line([(x - 30, y), (x - 4, y)], owner=sid)
        V.line([(x - 4, y - 12), (x - 4, y + 12)], w=2.4, owner=sid)
        V.line([(x + 4, y - 12), (x + 4, y + 12)], w=2.4, owner=sid)
        V.line([(x + 4, y), (x + 30, y)], owner=sid)
        body = [[x - 5, y - 12, x + 5, y + 12]]
        pins = [pin('A', x - 30, y, a), pin('B', x + 30, y, b)]
    if var:
        _var_arrow(V, x, y, sid)
        body = [[x - 16, y - 16, x + 16, y + 16]]
    _dev_text(V, x, y, orient, name, size, label_side, sid, off=16 if var else 14)
    return V.add_symbol(sid, 'varcap' if var else 'cap', body, pins, members or [], None, dict(x=x, y=y))


def _var_arrow(V, x, y, sid):
    V.line([(x - 15, y + 15), (x + 14, y - 14)], w=1.3, owner=sid)
    V.poly([(x + 16, y - 16), (x + 7, y - 13), (x + 13, y - 7)], owner=sid)


def _dev_text(V, x, y, orient, name, size, side, sid, off=10):
    lines = size if isinstance(size, list) else ([size] if size else [])
    if orient == 'v':
        if side == 'right':
            tx, anc = x + off + 2, 'start'
        else:
            tx, anc = x - off - 2, 'end'
        if name:
            V.text(tx, y - 7, name, size=11, anchor=anc, italic=True, cls='devname', owner=sid)
        for i, ln in enumerate(lines):
            V.text(tx, y + 7 + 12 * i, ln, size=10, anchor=anc, color='#555', cls='size', owner=sid)
    else:
        if side == 'above':
            if name:
                V.text(x, y - off - 6 - 12 * len(lines), name, size=11, anchor='middle', italic=True, cls='devname', owner=sid)
            for i, ln in enumerate(lines):
                V.text(x, y - off - 6 - 12 * (len(lines) - 1 - i), ln, size=10, anchor='middle', color='#555', cls='size', owner=sid)
        else:
            if name:
                V.text(x, y + off + 8, name, size=11, anchor='middle', italic=True, cls='devname', owner=sid)
            for i, ln in enumerate(lines):
                V.text(x, y + off + 20 + 12 * i, ln, size=10, anchor='middle', color='#555', cls='size', owner=sid)


def visrc(V, sid, x, y, name='', size='', top=None, bot=None, bus=None, bus_side='right', members=None, label_side='left'):
    """variable current source (circle + arrow + diagonal arrow). pins top (x,y-30), bottom (x,y+30), optional bus pin."""
    V.line([(x, y - 30), (x, y - 16)], owner=sid)
    V.line([(x, y + 16), (x, y + 30)], owner=sid)
    V.circle(x, y, 16, owner=sid)
    V.line([(x, y - 9), (x, y + 6)], w=1.4, owner=sid)
    V.poly([(x, y + 10), (x - 4, y + 3), (x + 4, y + 3)], owner=sid)
    V.line([(x - 20, y + 20), (x + 18, y - 18)], w=1.3, owner=sid)
    V.poly([(x + 21, y - 21), (x + 11, y - 18), (x + 18, y - 11)], owner=sid)
    pins = [pin('T', x, y - 30, top), pin('B', x, y + 30, bot)]
    body = [[x - 21, y - 21, x + 21, y + 21]]
    if bus is not None:
        s = 1 if bus_side == 'right' else -1
        V.line([(x + s * 16, y), (x + s * 40, y)], w=BUS_W, owner=sid)
        pins.append(pin('BUS', x + s * 40, y, bus))
    _dev_text(V, x, y, 'v', name, size, label_side, sid, off=22)
    return V.add_symbol(sid, 'visrc', body, pins, members or [], None, dict(x=x, y=y))


def gnd(V, x, y, net):
    V.line([(x, y), (x, y + 8)], owner='gnd')
    V.line([(x - 10, y + 8), (x + 10, y + 8)], w=1.8, owner='gnd')
    V.line([(x - 6, y + 12), (x + 6, y + 12)], w=1.6, owner='gnd')
    V.line([(x - 2, y + 16), (x + 2, y + 16)], w=1.4, owner='gnd')
    V.labels.append({'name': net, 'at': [float(x), float(y)], 'kind': 'power'})
    V.symbols.append({'id': 'gnd_%d_%d' % (x, y), 'kind': 'gnd', 'body': [[x - 10, y + 7, x + 10, y + 17]], 'pins': [], 'members': []})


def vdd_tee(V, x, y, net, label='VDD'):
    V.line([(x, y), (x, y - 8)], owner='vdd')
    V.line([(x - 10, y - 8), (x + 10, y - 8)], w=1.8, owner='vdd')
    tid = V.text(x, y - 17, label, size=10, anchor='middle', cls='power')
    V.labels.append({'name': net, 'at': [float(x), float(y)], 'kind': 'power', 'tid': tid})
    V.symbols.append({'id': 'vdd_%d_%d' % (x, y), 'kind': 'vdd', 'body': [[x - 10, y - 9, x + 10, y - 7]], 'pins': [], 'members': []})


def rail(V, x0, x1, y, net, label='VDD'):
    V.wire([(x0, y), (x1, y)], cls='power', net=net)
    tid = V.text(x0 - 6, y, label, size=12, anchor='end', weight='bold', cls='power')
    V.labels.append({'name': net, 'at': [float(x0), float(y)], 'kind': 'power', 'tid': tid})


def gray_gate(V, p, name, side):
    """short gray label at a gate pin of an invisible net (no wire)"""
    x, y = p['x'], p['y']
    if side == 'left':
        tid = V.text(x - 3, y, name, size=10, anchor='end', color=GRAY, cls='gray')
    else:
        tid = V.text(x + 3, y, name, size=10, anchor='start', color=GRAY, cls='gray')
    V.labels.append({'name': name, 'at': [x, y], 'kind': 'gray', 'tid': tid})


# ============================ block symbols ============================
def tri(V, sid, x0, yc, label, inst, w=80, h=90, ins=None, outs=None, bottom=None, top=None, link=None,
        clock_mark=False, members=None, sub='', cls='data'):
    """amplifier triangle pointing right. ins/outs: list of (pinname, dy, terms). bottom/top: list of (pinname, dx, terms, cls)"""
    V.poly([(x0, yc - h / 2), (x0 + w, yc), (x0, yc + h / 2)], fill='#fff', stroke=BLACK, w=SYM_W, owner=sid)
    V.text(x0 + w * 0.36, yc, label, size=12, anchor='middle', weight='bold', cls='blk', owner=sid)
    pins = []
    lw = CLK_W if cls == 'clock' else SYM_W
    for (pn, dy, terms) in (ins or []):
        V.line([(x0 - 20, yc + dy), (x0, yc + dy)], w=lw, owner=sid)
        pins.append(pin(pn, x0 - 20, yc + dy, terms))
    for (pn, dy, terms) in (outs or []):
        xe = x0 + w * (1 - abs(dy) / (h / 2))
        V.line([(xe, yc + dy), (x0 + w + 20, yc + dy)], w=lw, owner=sid)
        pins.append(pin(pn, x0 + w + 20, yc + dy, terms))
    for (pn, dx, terms, cl) in (bottom or []):
        ye = yc + (h / 2) * (1 - dx / w)
        V.line([(x0 + dx, ye), (x0 + dx, yc + h / 2 + 20)], w=CLK_W if cl == 'clock' else SYM_W, owner=sid)
        pins.append(pin(pn, x0 + dx, yc + h / 2 + 20, terms))
        if clock_mark:
            V.poly([(x0 + dx - 6, ye), (x0 + dx, ye - 8), (x0 + dx + 6, ye)], fill='none', stroke=BLACK, w=1.2, owner=sid)
    for (pn, dx, terms, cl) in (top or []):
        ye = yc - (h / 2) * (1 - dx / w)
        V.line([(x0 + dx, ye), (x0 + dx, yc - h / 2 - 20)], w=BUS_W if cl == 'bus' else SYM_W, owner=sid)
        pins.append(pin(pn, x0 + dx, yc - h / 2 - 20, terms))
    if inst:
        V.text(x0 + w / 2 - 6, yc - h / 2 - 10, inst, size=10, anchor='middle', italic=True, color='#444', cls='inst', owner=sid)
    if sub:
        if bottom:
            V.text(x0 + w / 2 - 6, yc - h / 2 - 23, sub, size=10, anchor='middle', color='#444', cls='inst', owner=sid)
        else:
            V.text(x0 + w / 2 - 6, yc + h / 2 + 12, sub, size=10, anchor='middle', color='#444', cls='inst', owner=sid)
    body = [[x0, yc - h / 2, x0 + w * 0.5, yc + h / 2], [x0 + w * 0.5, yc - h / 4, x0 + w * 0.85, yc + h / 4]]
    return V.add_symbol(sid, 'tri', body, pins, members or [], link, dict(x0=x0, yc=yc, w=w, h=h))


def box(V, sid, x0, y0, w, h, label, inst, left=None, right=None, bottom=None, top=None, link=None, members=None,
        big=False, pin_text=True, sub=None):
    """block box. left/right: list of (pinname, y, terms, cls); bottom/top: list of (pinname, x, terms, cls). pins at 20px from edge."""
    V.rect(x0, y0, w, h, fill='#fff', stroke=BLACK, sw=SYM_W, owner=sid)
    V.text(x0 + w / 2, y0 + h / 2 - (8 if sub else 0), label, size=22 if big else 13, anchor='middle', weight='bold', cls='blk', owner=sid)
    if sub:
        V.text(x0 + w / 2, y0 + h / 2 + 12, sub, size=10, anchor='middle', color='#444', cls='blk', owner=sid)
    if inst:
        V.text(x0, y0 - 9, inst, size=10, anchor='start', italic=True, color='#444', cls='inst', owner=sid)
    pins = []
    def lw(cl):
        return CLK_W if cl in ('clock', 'bus') else SYM_W
    for (pn, y, terms, cl) in (left or []):
        V.line([(x0 - 20, y), (x0, y)], w=lw(cl), owner=sid)
        pins.append(pin(pn, x0 - 20, y, terms))
        if pin_text:
            V.text(x0 + 4, y, pn, size=9, anchor='start', color='#555', cls='pintext', owner=sid)
    for (pn, y, terms, cl) in (right or []):
        V.line([(x0 + w, y), (x0 + w + 20, y)], w=lw(cl), owner=sid)
        pins.append(pin(pn, x0 + w + 20, y, terms))
        if pin_text:
            V.text(x0 + w - 4, y, pn, size=9, anchor='end', color='#555', cls='pintext', owner=sid)
    for (pn, x, terms, cl) in (bottom or []):
        V.line([(x, y0 + h), (x, y0 + h + 20)], w=lw(cl), owner=sid)
        pins.append(pin(pn, x, y0 + h + 20, terms))
        if pin_text:
            V.text(x, y0 + h - 8, pn, size=9, anchor='middle', color='#555', cls='pintext', owner=sid)
    for (pn, x, terms, cl) in (top or []):
        V.line([(x, y0), (x, y0 - 20)], w=lw(cl), owner=sid)
        pins.append(pin(pn, x, y0 - 20, terms))
        if pin_text:
            V.text(x, y0 + 9, pn, size=9, anchor='middle', color='#555', cls='pintext', owner=sid)
    return V.add_symbol(sid, 'box', [[x0, y0, x0 + w, y0 + h]], pins, members or [], link, dict(x0=x0, y0=y0, w=w, h=h))


def inv(V, sid, x0, yc, inst, a_terms, y_terms, link=None, members=None, flip_label=False, cls='data'):
    """inverter (CMOS buffer) triangle w=36 h=32 + bubble. pins A (x0-20,yc), Y (x0+36+8+20, yc)"""
    w, h = 34, 30
    V.poly([(x0, yc - h / 2), (x0 + w, yc), (x0, yc + h / 2)], fill='#fff', stroke=BLACK, w=SYM_W, owner=sid)
    V.circle(x0 + w + 4, yc, 4, fill='#fff', owner=sid)
    lw = CLK_W if cls == 'clock' else SYM_W
    V.line([(x0 - 20, yc), (x0, yc)], w=lw, owner=sid)
    V.line([(x0 + w + 8, yc), (x0 + w + 28, yc)], w=lw, owner=sid)
    if inst:
        V.text(x0 + 14, yc + (h / 2 + 10) * (-1 if flip_label else 1), inst, size=9, anchor='middle', italic=True, color='#444', cls='inst', owner=sid)
    pins = [pin('A', x0 - 20, yc, a_terms), pin('Y', x0 + w + 28, yc, y_terms)]
    return V.add_symbol(sid, 'inv', [[x0, yc - h / 2, x0 + w * 0.6, yc + h / 2], [x0 + w * 0.6, yc - 6, x0 + w + 8, yc + 6]], pins, members or [], link,
                        dict(x0=x0, yc=yc))


def switch_open(V, sid, x, y, orient, a_terms, b_terms, label, sub, link=None, members=None):
    """open switch glyph (e.g. always-off TG). vertical: pins (x, y-30) top, (x, y+30) bottom"""
    if orient == 'v':
        V.line([(x, y - 30), (x, y - 12)], owner=sid)
        V.line([(x, y + 12), (x, y + 30)], owner=sid)
        V.circle(x, y - 12, 2.5, fill='#fff', owner=sid)
        V.circle(x, y + 12, 2.5, fill='#fff', owner=sid)
        V.line([(x, y + 12), (x + 13, y - 9)], w=1.8, owner=sid)
        pins = [pin('A', x, y - 30, a_terms), pin('B', x, y + 30, b_terms)]
        body = [[x - 4, y - 14, x + 15, y + 14]]
        V.text(x + 20, y - 6, label, size=11, anchor='start', weight='bold', cls='blk', owner=sid)
        V.text(x + 20, y + 8, sub, size=9, anchor='start', color='#555', cls='blk', owner=sid)
    return V.add_symbol(sid, 'switch', body, pins, members or [], link, dict(x=x, y=y))


def term_marker(V, sid, x, y, up, label, terms, esd=False, link=None, members=None):
    """termination (+ESD) marker hanging from a line at (x,y): pin at (x,y). up=True draws above."""
    s = -1 if up else 1
    # stem (a wire from the line to the pin) is drawn by the caller: pin at (x, y + s*12)
    # resistor zigzag
    pts = [(x, y + s * 12)]
    for i in range(5):
        pts.append((x + (5 if i % 2 == 0 else -5), y + s * (14 + i * 5)))
    pts += [(x, y + s * 38), (x, y + s * 44)]
    V.line(pts, owner=sid)
    V.circle(x, y + s * 47, 3, fill='#fff', owner=sid)
    body = [sorted_box(x - 7, y + s * 12, x + 7, y + s * 50)]
    tx = x + 9
    V.text(tx, y + s * 26, label, size=9, anchor='start', color='#333', cls='blk', owner=sid)
    if esd:
        # small ESD diode pair glyph to the right of the resistor
        ex = x + 9; ey = y + s * 40
        V.text(ex, ey, 'ESD', size=9, anchor='start', color='#333', weight='bold', cls='blk', owner=sid)
    return V.add_symbol(sid, 'term', body, [pin('P', x, y + s * 12, terms)], members or [], link, dict(x=x, y=y))


def sorted_box(x0, y0, x1, y1):
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
