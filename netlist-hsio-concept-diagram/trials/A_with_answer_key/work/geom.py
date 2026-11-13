"""Symbol library + view builder.  Every symbol is emitted as primitive drawing ops
(lines / polygons / circles / text) so that HTML and PPTX render the same geometry, and
the checker reads pins and bodies from the same data."""
import math

INK, GRAY, CLK_W, BUS_W, DATA_W, PWR_W = '#1f2328', '#8a8f98', 3.2, 3.2, 1.6, 1.6
FONT = 11          # px, monospace estimate 0.6em per char

def tw(s, size=FONT):
    return 0.6 * size * len(s)

class View:
    def __init__(s, vid, title, cell, level, w, h, note=''):
        s.d = dict(id=vid, title=title, cell=cell, level=level, w=w, h=h, note=note,
                   syms=[], wires=[], dots=[], ports=[], tags=[], texts=[], axes=[],
                   sym_pairs=[], allowed_cross=[], omitted=[], links={}, asym_wires=[], rails=[])
    # ---- generic
    def sym(s, sid, kind, ops, pins, body, pinmap=None, hidden=None, link=None, represents=None,
            slices=1, label=None):
        d = dict(id=sid, kind=kind, ops=ops, pins=pins, body=body, pinmap=pinmap or {},
                 hidden=hidden or {}, link=link, represents=represents or [], slices=slices)
        s.d['syms'].append(d)
        if label: s.text(*label)
        return d
    def wire(s, pts, cls='data', net=None, loop=False):
        pts = [list(p) for p in pts]
        s.d['wires'].append(dict(pts=pts, cls=cls, net=net, loop=loop))
    def dot(s, x, y): s.d['dots'].append([x, y])
    def text(s, x, y, t, size=FONT, anchor='start', color=INK, cls='', italic=False, bold=False):
        s.d['texts'].append(dict(x=x, y=y, t=t, size=size, anchor=anchor, color=color, cls=cls,
                                 italic=italic, bold=bold))
    def port(s, name, x, y, side, cls='data', bits=None):
        """Virtuoso-style pin. (x,y) = connection point. side = where the pin sits relative to the
        wire end: 'L' (pin on the left edge), 'R', 'T', 'B'."""
        w, h = 22, 12
        if side == 'L':
            pts = [[x - w - 2, y - h/2], [x - 8, y - h/2], [x - 2, y], [x - 8, y + h/2], [x - w - 2, y + h/2]]
            tx, ty, an = x - w - 6, y + 4, 'end'
        elif side == 'R':
            pts = [[x + 2, y - h/2], [x + w - 4, y - h/2], [x + w + 2, y], [x + w - 4, y + h/2], [x + 2, y + h/2]]
            tx, ty, an = x + w + 6, y + 4, 'start'
        elif side == 'B':
            pts = [[x - h/2, y + w + 2], [x - h/2, y + 8], [x, y + 2], [x + h/2, y + 8], [x + h/2, y + w + 2]]
            tx, ty, an = x, y + w + 15, 'middle'
        else:
            pts = [[x - h/2, y - w - 2], [x - h/2, y - 8], [x, y - 2], [x + h/2, y - 8], [x + h/2, y - w - 2]]
            tx, ty, an = x, y - w - 6, 'middle'
        s.d['ports'].append(dict(name=name, x=x, y=y, side=side, cls=cls, poly=pts))
        s.text(tx, ty, name, anchor=an, bold=True, size=FONT)
    def tag(s, x, y, net, side, cls='hidden'):
        """short grey name tag at a pin end (hidden net, no wire)."""
        an = {'L': 'end', 'R': 'start', 'T': 'middle', 'B': 'middle'}[side]
        tx = x - 3 if side == 'L' else x + 3 if side == 'R' else x
        ty = y + 4 if side in 'LR' else (y - 5 if side == 'T' else y + 13)
        s.d['tags'].append(dict(net=net, x=x, y=y, side=side, kind=cls))
        s.text(tx, ty, net, anchor=an, color=GRAY if cls == 'hidden' else INK, size=10 if cls == 'hidden' else FONT,
               bold=(cls != 'hidden'))
    def label(s, x, y, net, side, cls='data'):
        """visible net label (connection by name, e.g. INP at a second pair's gate)."""
        s.tag(x, y, net, side, cls='label')
    def rail(s, net, y, x0, x1):
        s.wire([[x0, y], [x1, y]], cls='power', net=net)
        s.d['rails'].append(dict(net=net, y=y, x0=x0, x1=x1))
        s.text(x0 - 6, y + 4, net, anchor='end', bold=True)
    def axis(s, x, y0, y1): s.d['axes'].append(dict(x=x, y0=y0, y1=y1))
    def pair(s, a, b, axis): s.d['sym_pairs'].append([a, b, axis])
    def allow(s, x, y, why): s.d['allowed_cross'].append(dict(x=x, y=y, why=why))
    def omit(s, what, kind, why): s.d['omitted'].append(dict(item=what, kind=kind, why=why))

# ---------------------------------------------------------------- primitive op helpers
def L(*pts, w=DATA_W, c=INK): return dict(t='line', pts=[list(p) for p in pts], w=w, c=c)
def P(*pts, fill=INK, c=INK, w=1): return dict(t='poly', pts=[list(p) for p in pts], fill=fill, c=c, w=w)
def C(x, y, r, fill='none', w=DATA_W): return dict(t='circle', x=x, y=y, r=r, fill=fill, w=w, c=INK)

def arrowhead(x0, y0, x1, y1, size=6):
    a = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - size * math.cos(a - 0.45), y1 - size * math.sin(a - 0.45))
    p2 = (x1 - size * math.cos(a + 0.45), y1 - size * math.sin(a + 0.45))
    return P((x1, y1), p1, p2)

def var_arrow(cx, cy, r=17):
    return [L((cx - r, cy + r), (cx + r - 2, cy - r + 2), w=1.3), arrowhead(cx - r, cy + r, cx + r, cy - r)]

# ---------------------------------------------------------------- device symbols
def mos(v, sid, pol, x, y, gate='L', s_top=None, name='', wl='', represents=(), pinmap=None, hidden=None,
        slices=1, lab_side=None):
    """Razavi 3-terminal MOS.  (x,y): centre on the drain/source line. pins: top/bot/g."""
    if s_top is None: s_top = (pol == 'p')
    sg = -1 if gate == 'L' else 1
    gx, px, cx = x + sg * 30, x + sg * 14, x + sg * 9
    ops = [L((gx, y), (px, y)), L((px, y - 14), (px, y + 14), w=2),
           L((cx, y - 18), (cx, y + 18), w=3.2),
           L((cx, y - 12), (x, y - 12), (x, y - 30)), L((cx, y + 12), (x, y + 12), (x, y + 30))]
    sy = y - 12 if s_top else y + 12
    if pol == 'n':
        ops.append(arrowhead(cx, sy, x - sg * 0.5, sy))
    else:
        ops.append(arrowhead(x, sy, cx + sg * 0.5 * -1, sy))
    pins = {'top': [x, y - 30], 'bot': [x, y + 30], 'g': [gx, y]}
    term = {'top': 'S' if s_top else 'D', 'bot': 'D' if s_top else 'S', 'g': 'G'}
    body = [min(px, x) - 2, y - 20, max(px, x) + 2, y + 20]
    pm = pinmap if pinmap is not None else {p: [[[r, term[p]]] for r in represents] for p in pins}
    side = lab_side or ('R' if gate == 'L' else 'L')
    lx = x + 6 if side == 'R' else x - 6
    an = 'start' if side == 'R' else 'end'
    d = v.sym(sid, 'mos_' + pol, ops, pins, body, pinmap=pm, hidden=hidden, represents=list(represents),
              slices=slices)
    d['term'] = term; d['xy'] = [x, y]; d['gate'] = gate
    if name: v.text(lx, y - 3, name, anchor=an, italic=True, size=10)
    if wl: v.text(lx, y + 10, wl, anchor=an, size=9, cls='wl', color='#55606e')
    return d

def res(v, sid, x, y, orient='V', var=False, name='', val='', represents=(), pinmap=None, hidden=None,
        lab=('R', 0)):
    if orient == 'V':
        zz = [(x, y - 30), (x, y - 18)]
        for i in range(6):
            zz.append((x + (6 if i % 2 == 0 else -6), y - 15 + i * 6))
        zz += [(x, y + 18), (x, y + 30)]
        pins = {'a': [x, y - 30], 'b': [x, y + 30]}; body = [x - 8, y - 20, x + 8, y + 20]
    else:
        zz = [(x - 30, y), (x - 18, y)]
        for i in range(6):
            zz.append((x - 15 + i * 6, y + (6 if i % 2 == 0 else -6)))
        zz += [(x + 18, y), (x + 30, y)]
        pins = {'a': [x - 30, y], 'b': [x + 30, y]}; body = [x - 20, y - 8, x + 20, y + 8]
    ops = [L(*zz)] + (var_arrow(x, y) if var else [])
    d = v.sym(sid, 'var_res' if var else 'res', ops, pins, body, pinmap=pinmap or {}, hidden=hidden,
              represents=list(represents)); d['xy'] = [x, y]
    _devlabel(v, x, y, orient, name, val, lab)
    return d

def cap(v, sid, x, y, orient='H', var=False, name='', val='', represents=(), pinmap=None, hidden=None,
        lab=('B', 0)):
    if orient == 'H':
        ops = [L((x - 30, y), (x - 4, y)), L((x + 4, y), (x + 30, y)),
               L((x - 4, y - 12), (x - 4, y + 12), w=2.2), L((x + 4, y - 12), (x + 4, y + 12), w=2.2)]
        pins = {'a': [x - 30, y], 'b': [x + 30, y]}; body = [x - 7, y - 14, x + 7, y + 14]
    else:
        ops = [L((x, y - 30), (x, y - 4)), L((x, y + 4), (x, y + 30)),
               L((x - 12, y - 4), (x + 12, y - 4), w=2.2), L((x - 12, y + 4), (x + 12, y + 4), w=2.2)]
        pins = {'a': [x, y - 30], 'b': [x, y + 30]}; body = [x - 14, y - 7, x + 14, y + 7]
    if var: ops += var_arrow(x, y, 15)
    d = v.sym(sid, 'var_cap' if var else 'cap', ops, pins, body, pinmap=pinmap or {}, hidden=hidden,
              represents=list(represents)); d['xy'] = [x, y]
    _devlabel(v, x, y, orient, name, val, lab)
    return d

def isrc(v, sid, x, y, var=True, name='', val='', represents=(), pinmap=None, hidden=None, ctrl=None,
         lab_side='L'):
    ops = [L((x, y - 30), (x, y - 14)), L((x, y + 14), (x, y + 30)), C(x, y, 14),
           L((x, y - 8), (x, y + 6), w=1.4), arrowhead(x, y - 8, x, y + 8, 5)]
    pins = {'top': [x, y - 30], 'bot': [x, y + 30]}
    if var: ops += var_arrow(x, y, 19)
    if ctrl:
        ops.append(L((x + 14, y), (x + 40, y), w=BUS_W))
        pins['ctrl'] = [x + 40, y]
    d = v.sym(sid, 'var_isrc' if var else 'isrc', ops, pins, [x - 16, y - 16, x + 16, y + 16],
              pinmap=pinmap or {}, hidden=hidden, represents=list(represents))
    lx = x - 24 if lab_side == 'L' else x + 24
    an = 'end' if lab_side == 'L' else 'start'
    if name: v.text(lx, y - 3, name, anchor=an, italic=True, size=10)
    if val: v.text(lx, y + 10, val, anchor=an, size=9, cls='wl', color='#55606e')
    return d

def _devlabel(v, x, y, orient, name, val, lab):
    side, off = lab
    if orient == 'V':
        lx, an = (x + 12, 'start') if side == 'R' else (x - 12, 'end')
        if name: v.text(lx, y - 3 + off, name, anchor=an, italic=True, size=10)
        if val: v.text(lx, y + 10 + off, val, anchor=an, size=9, cls='wl', color='#55606e')
    else:
        ly = y - 22 + off if side == 'T' else y + 26 + off
        if name: v.text(x, ly, name, anchor='middle', italic=True, size=10)
        if val: v.text(x, ly + 12, val, anchor='middle', size=9, cls='wl', color='#55606e')

# ---------------------------------------------------------------- block symbols
def amp(v, sid, x0, yc, label, pins_in, pins_out, clk=None, w=90, h=100, link=None, represents=(),
        pinmap=None, hidden=None, sub=None, dy=15):
    """triangle pointing right.  pins_in/out: names for (P,N); diff offset +-dy."""
    ops = [P((x0, yc - h/2), (x0 + w, yc), (x0, yc + h/2), (x0, yc - h/2), fill='#ffffff', w=DATA_W)]
    pins = {}
    for i, n in enumerate(pins_in):
        y = yc - dy if i == 0 else yc + dy
        ops.append(L((x0 - 20, y), (x0, y))); pins[n] = [x0 - 20, y]
    for i, n in enumerate(pins_out):
        y = yc - dy if i == 0 else yc + dy
        xe = x0 + w * (1 - abs(y - yc) / (h / 2))
        ops.append(L((xe, y), (x0 + w + 20, y))); pins[n] = [x0 + w + 20, y]
    if clk:
        cxp = x0 + w * 0.4
        ye = yc + h/2 * (1 - 0.4)
        ops.append(L((cxp, ye), (cxp, yc + h/2 + 20), w=CLK_W)); pins[clk] = [cxp, yc + h/2 + 20]
        ops.append(L((cxp - 6, ye - 1), (cxp, ye - 9), (cxp + 6, ye - 1), w=1.2))
    d = v.sym(sid, 'amp', ops, pins, [x0, yc - h/2, x0 + w, yc + h/2], pinmap=pinmap, hidden=hidden,
              link=link, represents=list(represents))
    v.text(x0 + w * 0.36, yc + 4, label, anchor='middle', bold=True, size=12)
    if sub: v.text(x0 + w * 0.5, (yc - h/2 - 6) if clk else (yc + h/2 + 16), sub, anchor='middle', size=9, color='#55606e')
    return d

def box(v, sid, x0, y0, x1, y1, label, pins, link=None, represents=(), pinmap=None, hidden=None,
        sub=None, pin_names=True, label_y=None, big=False):
    """pins: list of (name, side, offset_along, cls, shown_name)."""
    ops = [P((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), fill='#ffffff', w=DATA_W)]
    pp = {}
    for (n, side, off, cls, shown) in pins:
        wl = CLK_W if cls in ('clock', 'bus') else DATA_W
        if side == 'L': a, b = (x0 - 20, y0 + off), (x0, y0 + off)
        elif side == 'R': a, b = (x1 + 20, y0 + off), (x1, y0 + off)
        elif side == 'T': a, b = (x0 + off, y0 - 20), (x0 + off, y0)
        else: a, b = (x0 + off, y1 + 20), (x0 + off, y1)
        ops.append(L(a, b, w=wl)); pp[n] = list(a)
        if pin_names and shown:
            if side == 'L': v.text(x0 + 4, y0 + off + 3.5, shown, size=9, color='#55606e')
            elif side == 'R': v.text(x1 - 4, y0 + off + 3.5, shown, size=9, anchor='end', color='#55606e')
            elif side == 'B': v.text(x0 + off, y1 - 5, shown, size=9, anchor='middle', color='#55606e')
            else: v.text(x0 + off, y0 + 12, shown, size=9, anchor='middle', color='#55606e')
    d = v.sym(sid, 'box', ops, pp, [x0, y0, x1, y1], pinmap=pinmap, hidden=hidden, link=link,
              represents=list(represents))
    ly = label_y if label_y is not None else (y0 + y1) / 2 + 4
    v.text((x0 + x1) / 2, ly, label, anchor='middle', bold=True, size=18 if big else 12)
    if sub: v.text((x0 + x1) / 2, ly + 14, sub, anchor='middle', size=9, color='#55606e')
    return d

def gnd(v, x, y):
    v.d['tags'].append(dict(net='__VSS__', x=x, y=y, side='B', kind='gnd'))
    v.d['syms'].append(dict(id='gnd_%d_%d' % (x, y), kind='gnd', ops=[L((x - 10, y), (x + 10, y)),
                       L((x - 6, y + 4), (x + 6, y + 4)), L((x - 2, y + 8), (x + 2, y + 8))],
                       pins={}, body=[x - 10, y, x + 10, y + 8], pinmap={}, hidden={}, represents=[], slices=1))
