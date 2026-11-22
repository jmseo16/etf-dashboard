"""hs.py - exam generator framework (new code, built on the reference scene.py primitives).
A Builder wraps a scene.View, registers symbol pins with the netlist net each pin touches, and routes nets with the
SKILL section 7-7 candidate order (straight, L, L, Z) rejecting crossings / body penetration / kinks. A net that cannot be
routed gets a short stub + net label (block level) - the caller decides.
Nothing here is specific to one netlist."""
import math, re, collections, itertools
import scene
from scene import View, pin, BLACK, GRAY
from netlist import fmt_si

EPS = 1e-6


ALIAS = {}


def expand(name):
    if name in ALIAS:
        return list(ALIAS[name])
    m = re.search(r'<(\d+):(\d+)>', name)
    if not m:
        return [name]
    a, b = int(m.group(1)), int(m.group(2))
    rng = range(a, b - 1, -1) if a >= b else range(a, b + 1)
    return [name[:m.start()] + '<%d>' % i + name[m.end():] for i in rng]


def seg_inter(a, b, c, d):
    """intersection of segments ab and cd: returns None, a point ('p',x,y) or an overlap ('o',len)"""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    ax = abs(x1 - x2) < EPS; ay = abs(y1 - y2) < EPS
    cx = abs(x3 - x4) < EPS; cy = abs(y3 - y4) < EPS
    if (ax or ay) and (cx or cy):
        bx0, bx1 = max(min(x1, x2), min(x3, x4)), min(max(x1, x2), max(x3, x4))
        by0, by1 = max(min(y1, y2), min(y3, y4)), min(max(y1, y2), max(y3, y4))
        if bx0 > bx1 + EPS or by0 > by1 + EPS:
            return None
        if bx1 - bx0 > EPS or by1 - by0 > EPS:
            return ('o', max(bx1 - bx0, by1 - by0))
        return ('p', bx0, by0)
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < EPS:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    if -EPS <= t <= 1 + EPS and -EPS <= u <= 1 + EPS:
        return ('p', x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def seg_box(a, b, box, pad=0):
    """does segment ab (axis aligned) enter the open interior of box (grown by pad)?"""
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    sx0, sx1 = sorted([a[0], b[0]]); sy0, sy1 = sorted([a[1], b[1]])
    return sx0 < x1 - EPS and sx1 > x0 + EPS and sy0 < y1 - EPS and sy1 > y0 + EPS


class H:
    def __init__(self, cells, vid, cell, level, title, w, h, scope=None):
        self.cells = cells
        self.cell = cell
        self.cd = cells[cell]
        self.el = {e['name']: e for e in self.cd['elems']}
        self.V = View(vid, cell, level, title, w, h, scope)
        self.pins = []          # dict(x,y,key,sym,name)
        self.bodies = []        # (box, symid)
        self.wire_net = []      # net key per V.wires entry
        self.groups = collections.defaultdict(list)   # key -> pin dict
        self.fail = []
        self.port_pts = []
        self.default_lens = {}
        self.rays = []
        self.v_extra = {}

    # ------------------------------------------------------------ netlist access
    def netof(self, term):
        e, t = term
        f = self.el[e]
        return f['pins'][t] if f['kind'] == 'inst' else f['terms'][t]

    def reg(self, sym):
        for p in sym['pins']:
            if not p['terms']:
                continue
            nets = tuple(self.netof(sl[0]) for sl in p['terms'])
            key = nets[0] if len(nets) == 1 else nets
            d = dict(x=p['x'], y=p['y'], key=key, sym=sym['id'], name=p['name'], side=p.get('side'))
            if sym['kind'] in ('tri', 'box') and p.get('side') in ('left', 'right', 'top', 'bottom'):
                dx, dy = {'left': (-44, 0), 'right': (44, 0), 'top': (0, -44), 'bottom': (0, 44)}[p['side']]
                self.rays.append(((p['x'], p['y']), (p['x'] + dx, p['y'] + dy)))
            self.pins.append(d)
            self.groups[key].append(d)
        for b in sym['body']:
            self.bodies.append((b, sym['id']))
        return sym

    # ------------------------------------------------------------ symbols
    def size_of(self, e):
        p = e['params']
        s = '%s/%s' % (fmt_si(p.get('w', '?')), fmt_si(p.get('l', '?')))
        m = p.get('m', '1')
        if m not in ('1', '1.0'):
            s += ' ×' + m
        return s

    def mos(self, name, cx, cy, gate='left', top='d', name_side=None, link=None, show_size=True):
        e = self.el[name]
        bot = 's' if top == 'd' else 'd'
        sym = scene.mos(self.V, name, cx, cy, e['type'], gate=gate, name=name, size=self.size_of(e) if show_size else '',
                        top=[[(name, top)]], bot=[[(name, bot)]], gterm=[[(name, 'g')]], members=[name], name_side=name_side, link=link,
                        arrow_at=None)
        return self.reg(sym)

    def res(self, name, x, y, orient='v', label_side='right', var=False, show_size=True):
        e = self.el[name]
        sz = fmt_si(e['value']) if show_size and not re.match(r'^[a-z]', e['value'] or '') else (e['value'] if show_size else '')
        sym = scene.res(self.V, name, x, y, orient, name=name, size=sz, a=[[(name, 'p')]], b=[[(name, 'n')]], members=[name],
                        label_side=label_side, var=var)
        return self.reg(sym)

    def cap(self, name, x, y, orient='v', label_side='right'):
        e = self.el[name]
        sym = scene.cap(self.V, name, x, y, orient, name=name, size=fmt_si(e['value']) if e['value'] else '',
                        a=[[(name, 'p')]], b=[[(name, 'n')]], members=[name], label_side=label_side)
        return self.reg(sym)

    def diode(self, name, x, y, orient='v', flip=False, label_side='right'):
        """diode: anode at p. vertical: p (x,y-30) / n (x,y+30) unless flip"""
        V = self.V
        e = self.el[name]
        sid = name
        s = -1 if flip else 1
        V.line([(x, y - 30), (x, y - 8)], owner=sid)
        V.line([(x, y + 8), (x, y + 30)], owner=sid)
        # triangle pointing from anode to cathode; cathode bar
        if not flip:
            V.poly([(x - 8, y - 8), (x + 8, y - 8), (x, y + 6)], fill='#fff', stroke=BLACK, w=1.6, owner=sid)
            V.line([(x - 8, y + 8), (x + 8, y + 8)], w=2.4, owner=sid)
            a, c = (x, y - 30), (x, y + 30)
        else:
            V.poly([(x - 8, y + 8), (x + 8, y + 8), (x, y - 6)], fill='#fff', stroke=BLACK, w=1.6, owner=sid)
            V.line([(x - 8, y - 8), (x + 8, y - 8)], w=2.4, owner=sid)
            a, c = (x, y + 30), (x, y - 30)
        tx = x + 12 if label_side == 'right' else x - 12
        anc = 'start' if label_side == 'right' else 'end'
        V.text(tx, y - 6, name, size=11, anchor=anc, italic=True, cls='devname', owner=sid)
        pa = pin('A', a[0], a[1], [[(name, 'p')]]); pc = pin('K', c[0], c[1], [[(name, 'n')]])
        sym = V.add_symbol(sid, 'diode', [[x - 9, y - 9, x + 9, y + 9]], [pa, pc], [name], None, dict(x=x, y=y))
        return self.reg(sym)

    def custom(self, sid, kind, body, pins_xy_terms, members=None, link=None):
        pins = [pin(n, x, y, t) for (n, x, y, t) in pins_xy_terms]
        sym = self.V.add_symbol(sid, kind, body, pins, members or [], link, {})
        return self.reg(sym)

    def tri(self, sid, x0, yc, label, inst, **kw):
        sym = scene.tri(self.V, sid, x0, yc, label, inst, **kw)
        return self.reg(sym)

    def box(self, sid, x0, y0, w, h, label, inst, **kw):
        sym = scene.box(self.V, sid, x0, y0, w, h, label, inst, **kw)
        return self.reg(sym)

    def inv(self, sid, x0, yc, inst, a_terms, y_terms, **kw):
        sym = scene.inv(self.V, sid, x0, yc, inst, a_terms, y_terms, **kw)
        return self.reg(sym)

    def pt(self, sym, pname):
        for p in sym['pins']:
            if p['name'] == pname:
                return (p['x'], p['y'])
        raise KeyError(pname)

    # ------------------------------------------------------------ power / port / label
    def rail_pin(self, x, y, net, direction, L=12):
        """short wire from a device pin to a local power symbol (plan 3.4-6 '국소 전원·접지 기호')"""
        V = self.V
        if direction == 'down':
            V.wire([(x, y), (x, y + L)], cls='power', net=net); self.wire_net.append(net)
            scene.gnd(V, x, y + L, net)
        else:
            V.wire([(x, y), (x, y - L)], cls='power', net=net); self.wire_net.append(net)
            scene.vdd_tee(V, x, y - L, net, label=net.upper())

    def port(self, name, x, y, d='right', io='in', cls='data', label_side=None, key=None):
        self.V.port(name, x, y, d=d, io=io, cls=cls, label_side=label_side)
        sy = self.V.symbols[-1]
        for b in sy['body']:
            self.bodies.append((b, 'pin_' + name))
        self.port_pts.append((float(x), float(y)))
        return (x, y)

    def offpage(self, name, x, y, d='left'):
        scene.offpage(self.V, name, x, y, d)
        sy = self.V.symbols[-1]
        for b in sy['body']:
            self.bodies.append((b, 'pin_off_' + name))
        return (x, y)

    def manual(self, key, pts, cls='data', color=None):
        self.add_wire(pts, key, cls, color)

    def stub(self, pt, d, key, name=None, L=40, cls='data', gray=False, size=11, bus=False):
        """short wire + net label"""
        x, y = pt
        e = {'left': (x - L, y), 'right': (x + L, y), 'up': (x, y - L), 'down': (x, y + L)}[d]
        self.add_wire([(x, y), e], key, cls)
        nm = name or (key if isinstance(key, str) else '?')
        if d in ('left', 'right'):
            self.V.netlabel(nm, (x + e[0]) / 2, y, tx=(x + e[0]) / 2, ty=y - 8, anchor='middle', gray=gray, size=size)
        elif d == 'down':
            self.V.netlabel(nm, e[0], e[1], tx=e[0], ty=e[1] + 9, anchor='middle', gray=gray, size=size)
        else:
            self.V.netlabel(nm, e[0], e[1], tx=e[0], ty=e[1] - 9, anchor='middle', gray=gray, size=size)
        if bus:
            self.V.line([(e[0] - 7 if d in ('left', 'right') else e[0] - 7, e[1] + 7), (e[0] + 7, e[1] - 7)], w=1.4, owner='bus')
        return e

    def gray(self, pt, d, name):
        """hidden-net gate: gray label only, no wire"""
        x, y = pt
        if d == 'left':
            self.V.text(x - 3, y, name, size=10, anchor='end', color=GRAY, cls='gray')
        else:
            self.V.text(x + 3, y, name, size=10, anchor='start', color=GRAY, cls='gray')
        self.V.labels.append({'name': name, 'at': [float(x), float(y)], 'kind': 'gray', 'tid': self.V._tid and 'x'})

    def add_wire(self, pts, key, cls='data', color=None):
        self.V.wire(pts, cls=cls, net=key if isinstance(key, str) else None)
        self.wire_net.append(key)
        if color:
            self.V.draw[-1]['c'] = color

    # ------------------------------------------------------------ routing
    def strokes(self):
        """all drawn line segments (symbol strokes) with owner"""
        out = []
        for d in self.V.draw:
            if d['t'] == 'line' and d.get('owner') not in ('wire', 'dot', 'bus'):
                for i in range(len(d['pts']) - 1):
                    out.append((tuple(d['pts'][i]), tuple(d['pts'][i + 1]), d.get('owner')))
            elif d['t'] == 'poly' and d.get('owner') not in ('port', 'dot', 'offpage'):
                pts = d['pts']
                for i in range(len(pts)):
                    out.append((tuple(pts[i]), tuple(pts[(i + 1) % len(pts)]), d.get('owner')))
        return out

    def wsegs(self):
        out = []
        for w, k in zip(self.V.wires, self.wire_net):
            p = w['pts']
            for i in range(len(p) - 1):
                out.append((tuple(p[i]), tuple(p[i + 1]), k))
        return out

    def valid(self, path, key, s, t, strokes, ws, allow_same=True):
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-9:
                return False
            if not (abs(a[0] - b[0]) < EPS or abs(a[1] - b[1]) < EPS):
                return False
            # a wire may not pass through some other pin / port attach point
            for q in [(p['x'], p['y']) for p in self.pins] + self.port_pts:
                if (abs(q[0] - s[0]) < 0.5 and abs(q[1] - s[1]) < 0.5) or (abs(q[0] - t[0]) < 0.5 and abs(q[1] - t[1]) < 0.5):
                    continue
                if seg_inter(a, b, q, q) is not None:
                    return False
            # outward corridors of block pins stay free (they are where label stubs go)
            for (ra, rb) in self.rays:
                if (abs(ra[0] - s[0]) < 0.5 and abs(ra[1] - s[1]) < 0.5) or (abs(ra[0] - t[0]) < 0.5 and abs(ra[1] - t[1]) < 0.5):
                    continue
                r_ = seg_inter(a, b, ra, rb)
                if r_ is not None:
                    return False
            # bodies
            for bx, sid in self.bodies:
                if seg_box(a, b, bx, 0 if sid.startswith('pin_') else 3):
                    return False
            for (c, d, own) in strokes:
                r = seg_inter(a, b, c, d)
                if r is None:
                    continue
                if r[0] == 'o':
                    return False
                px, py = r[1], r[2]
                # touching at the route ends (pin lead tips) is how a wire attaches
                if (abs(px - s[0]) < 0.5 and abs(py - s[1]) < 0.5) or (abs(px - t[0]) < 0.5 and abs(py - t[1]) < 0.5):
                    continue
                return False
            for (c, d, k2) in ws:
                r = seg_inter(a, b, c, d)
                if r is None:
                    continue
                if k2 == key and allow_same:
                    if r[0] == 'o':
                        return False
                    continue
                return False
        # corner segments >= 20 (except the first/last which attach to a lead)
        for i in range(len(path) - 1):
            L = abs(path[i + 1][0] - path[i][0]) + abs(path[i + 1][1] - path[i][1])
            if L < 20 - EPS and 0 < i < len(path) - 2:
                return False
            if L < 20 - EPS and len(path) > 2:
                return False
        return True

    def candidates(self, s, t):
        (x1, y1), (x2, y2) = s, t
        c = []
        if abs(x1 - x2) < EPS or abs(y1 - y2) < EPS:
            c.append([s, t])
        c.append([s, (x2, y1), t])
        c.append([s, (x1, y2), t])
        xs = sorted({(x1 + x2) / 2, round((x1 + x2) / 20) * 10, *[x1 + k for k in (-60, -40, -20, 20, 40, 60)], *[x2 + k for k in (-60, -40, -20, 20, 40, 60)]})
        ys = sorted({(y1 + y2) / 2, round((y1 + y2) / 20) * 10, *[y1 + k for k in (-60, -40, -20, 20, 40, 60)], *[y2 + k for k in (-60, -40, -20, 20, 40, 60)]})
        for xm in xs:
            c.append([s, (xm, y1), (xm, y2), t])
        for ym in ys:
            c.append([s, (x1, ym), (x2, ym), t])
        out = []
        man = abs(x1 - x2) + abs(y1 - y2)
        for p in c:
            # drop duplicate points
            q = [p[0]]
            for pt in p[1:]:
                if abs(pt[0] - q[-1][0]) > EPS or abs(pt[1] - q[-1][1]) > EPS:
                    q.append(pt)
            L = sum(abs(q[i + 1][0] - q[i][0]) + abs(q[i + 1][1] - q[i][1]) for i in range(len(q) - 1))
            if len(q) >= 2 and L <= 1.5 * max(man, 20) + EPS:
                out.append((L, len(q), q))
        out.sort(key=lambda z: (z[1] if z[1] <= 3 else 4, z[0]))
        return [q for _, _, q in out]

    def feet(self, key, t, ws):
        out = []
        for (a, b, k) in ws:
            if k != key:
                continue
            if abs(a[0] - b[0]) < EPS:
                if min(a[1], b[1]) + 20 <= t[1] <= max(a[1], b[1]) - 20:
                    out.append((a[0], t[1]))
            elif abs(a[1] - b[1]) < EPS:
                if min(a[0], b[0]) + 20 <= t[0] <= max(a[0], b[0]) - 20:
                    out.append((t[0], a[1]))
        return out

    def route(self, key, pts, cls='data', color=None, first=None):
        """join all points of net `key` with wires; returns the list of points that could not be joined"""
        pts = list(dict.fromkeys(pts))
        if len(pts) < 2:
            return []
        if first is not None:
            pts.sort(key=lambda p: (p != first,))
        verts = [pts[0]]
        rest = pts[1:]
        failed = []
        while rest:
            best = None
            for t in rest:
                for s in verts:
                    d = abs(s[0] - t[0]) + abs(s[1] - t[1])
                    if best is None or d < best[0]:
                        best = (d, s, t)
            _, s0, t = best
            strokes = self.strokes(); ws = self.wsegs()
            done = False
            starts = verts + self.feet(key, t, ws)
            for s in sorted(starts, key=lambda v: abs(v[0] - t[0]) + abs(v[1] - t[1]))[:6]:
                for path in self.candidates(s, t):
                    if self.valid(path, key, s, t, strokes, ws):
                        self.add_wire(path, key, cls, color)
                        verts.extend(path)
                        done = True
                        break
                if done:
                    break
            rest.remove(t)
            if done:
                verts.append(t)
            else:
                failed.append(t)
        return failed


    def auto(self, key, pts, name=None, cls='data', dirs=None, L=30, color=None, first=None, anchor_label=True, lens=None):
        """route net `key` through pts; points that cannot be wired get a stub + label (same name on the anchor point)."""
        failed = self.route(key, pts, cls=cls, color=color, first=first)
        if not failed:
            return []
        nm = name or (key if isinstance(key, str) else None)
        lab_pts = list(failed)
        anchor = (first or pts[0])
        if anchor not in failed and anchor_label:
            lab_pts.append(anchor)
        sidemap = {'left': 'left', 'right': 'right', 'top': 'up', 'bottom': 'down'}
        allpts = [(p['x'], p['y']) for p in self.pins] + self.port_pts
        for p in lab_pts:
            strokes = self.strokes(); ws = self.wsegs()
            pref = []
            for q in self.pins:
                if abs(q['x'] - p[0]) < 0.5 and abs(q['y'] - p[1]) < 0.5 and q.get('side') in sidemap:
                    pref = [sidemap[q['side']]]
            order = (dirs or {}).get(p, []) + pref + ['left', 'right', 'down', 'up']
            base = (lens or self.default_lens).get(p, L)
            done = False
            for d in order:
                for LL in (base, base + 20, base + 40, max(base - 10, 24)):
                    e = {'left': (p[0] - LL, p[1]), 'right': (p[0] + LL, p[1]), 'up': (p[0], p[1] - LL), 'down': (p[0], p[1] + LL)}[d]
                    if any(math.hypot(e[0] - q[0], e[1] - q[1]) < 14 and (abs(q[0] - p[0]) > 0.5 or abs(q[1] - p[1]) > 0.5) for q in allpts):
                        continue
                    # the stub end must not sit on a corner/end of another net's wire or on some other pin
                    if self.valid([p, e], key, p, e, strokes, ws):
                        self.stub(p, d, key, name=nm, L=LL, cls=cls)
                        done = True
                        break
                if done:
                    break
            if not done:
                self.fail.append((key, p))
        return failed

    def finalize(self):
        """junction dots: a point where wire ends (1 each), wire pass-throughs (2 each) and pins (1) add up to >= 3"""
        V = self.V
        key = lambda p: (round(p[0], 3), round(p[1], 3))
        score = collections.Counter()
        ends = set()
        for wi, w in enumerate(V.wires):
            p = w['pts']
            score[key(p[0])] += 1; score[key(p[-1])] += 1
            ends.add(key(p[0])); ends.add(key(p[-1]))
        for pt in list(ends):
            for wi, w in enumerate(V.wires):
                p = w['pts']
                for i in range(len(p) - 1):
                    a, b = p[i], p[i + 1]
                    if seg_inter(a, b, pt, pt) is None:
                        continue
                    if i == 0 and key(a) == pt or i == len(p) - 2 and key(b) == pt:
                        continue          # this wire's own end, already counted
                    # interior point or corner of that wire; count corner once (when matched on segment i's end)
                    if key(a) == pt and i > 0:
                        continue
                    score[pt] += 2
        for p in self.pins:
            k = key((p['x'], p['y']))
            if k in ends:
                score[k] += 1
        have = {key(d) for d in V.dots}
        for pt in ends:
            if score[pt] >= 3 and pt not in have:
                V.dot(pt[0], pt[1])
        # bus marks (plan 3.5-2): one slash per drawn wire of a bus net; no bit count when the name has <a:b>
        for w, k in zip(V.wires, self.wire_net):
            if isinstance(k, str) and re.search(r'<\d+:\d+>', k):
                p = w['pts']
                best = max(range(len(p) - 1), key=lambda i: abs(p[i + 1][0] - p[i][0]) + abs(p[i + 1][1] - p[i][1]))
                mx = (p[best][0] + p[best + 1][0]) / 2; my = (p[best][1] + p[best + 1][1]) / 2
                V.line([(mx - 7, my + 7), (mx + 7, my - 7)], w=1.4, owner='bus')
        return self

    def done(self):
        self.finalize()
        return self.V
