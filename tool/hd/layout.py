"""Symbol geometry and placement.

Placement rules (first principle: wires should be straight):
  * transistors are stacked vertically between the rails; devices in series share one column,
  * a differential circuit is mirrored about its own axis, several pairs sit side by side,
  * blocks are placed left to right in signal order and each block is moved vertically so that
    its first input pin is on the same height as the pin that drives it.
"""
import math
from collections import OrderedDict, defaultdict
from . import netlist as NL

G = 10
ROW = 120      # vertical pitch of transistor rows
XP = 200       # horizontal pitch of transistor columns
ESC = {'l': (-1, 0), 'r': (1, 0), 't': (0, -1), 'b': (0, 1)}
RELAX = [0]     # spacing step used when a screen is too crowded for its labels


def snap(v, g=G):
    return int(round(float(v) / g)) * g


def snap_up(v, g=G):
    return int(math.ceil(float(v) / g - 1e-9)) * g


def tw(s, size=10):
    """Estimated text width in px."""
    return sum(size * (1.0 if ord(ch) > 0x2e7f else 0.58) for ch in s)


class Text(object):
    def __init__(self, s, x, y, size=10, anchor='start', color='#111', italic=False, bold=False, kind='text'):
        self.s, self.x, self.y, self.size, self.anchor, self.color, self.italic, self.bold, self.kind = s, x, y, size, anchor, color, italic, bold, kind

    def bbox(self):
        w = tw(self.s, self.size)
        x0 = self.x if self.anchor == 'start' else (self.x - w if self.anchor == 'end' else self.x - w / 2.0)
        return (x0, self.y - self.size * 0.82, x0 + w, self.y + self.size * 0.22)


# ----------------------------------------------------------------------------- symbol geometry
def geom_inst(K):
    """Box / triangle geometry of an instance symbol. Sets K.w, K.h, relative pin positions, K.shapes, K.texts."""
    K.shapes, K.texts = [], []
    name = K.id
    mult = getattr(K, 'mult', 1)
    if K.sym in ('inv', 'buf') and len(K.pins) == 2 and all(len(P.nets) == 1 for P in K.pins.values()):
        outx = 50 if K.sym == 'inv' else 40
        for P in K.pins.values():
            if P.dir == 'out':
                P.rx, P.ry, P.side = outx, 0, 'r'
            else:
                P.rx, P.ry, P.side = 0, 0, 'l'
        K.shapes.append(('poly', [(0, -20), (0, 20), (40, 0)]))
        if K.sym == 'inv':
            K.shapes.append(('circle', 45, 0, 5))
        K.box = (0, -20, outx, 20)
        K.texts.append(Text(name, 0, -25, 9, 'start', '#555', italic=True, kind='inst'))
        K.texts.append(Text(K.cell + (' ×%d' % mult if mult > 1 else ''), 0, 31, 8, 'start', '#777', kind='cell'))
        return
    K.sym = 'box'
    L = [P for P in K.pins.values() if P.side == 'l']
    R = [P for P in K.pins.values() if P.side == 'r']
    T = [P for P in K.pins.values() if P.side == 't']
    B = [P for P in K.pins.values() if P.side == 'b']
    title = K.title + (' ×%d' % mult if mult > 1 else '')
    lw = max([tw(P.name, 9) for P in L] + [0]) + 8
    rw = max([tw(P.name, 9) for P in R] + [0]) + 8
    mid = max(tw(title, 12), tw(K.sub, 9)) + 16
    pt = snap_up(max([tw(P.name, 9) for P in T] + [20]) + 12, 20)
    pb = snap_up(max([tw(P.name, 9) for P in B] + [20]) + 12, 20)
    w = snap_up(max(80, lw + rw + mid, 2 * max(lw, rw) + mid - 8, len(T) * pt + 20, len(B) * pb + 20), 20)
    h = max(60, 20 * max(len(L), len(R)) + 20)
    if T:
        h += 10
    if B:
        h += 10 + (10 if getattr(K, 'role', '') == 'samp' else 0)
    h = snap_up(h, 20)
    for lst, x in ((L, 0), (R, w)):
        y0 = snap((h - 20 * (len(lst) - 1)) / 2.0)
        for i, P in enumerate(lst):
            P.rx, P.ry = x, y0 + 20 * i
            K.texts.append(Text(P.name, 4 if x == 0 else w - 4, P.ry + 3, 9, 'start' if x == 0 else 'end', '#444', kind='pin'))
    for lst, y, pitch in ((T, 0, pt), (B, h, pb)):
        x0 = snap((w - pitch * (len(lst) - 1)) / 2.0)
        for i, P in enumerate(lst):
            P.rx, P.ry = x0 + pitch * i, y
            K.texts.append(Text(P.name, P.rx, 11 if y == 0 else h - (12 if getattr(K, 'role', '') == 'samp' else 5), 9, 'middle', '#444', kind='pin'))
    K.w, K.h = w, h
    K.box = (0, 0, w, h)
    K.shapes.append(('rect', 0, 0, w, h))
    ty = h / 2.0 + 4
    K.texts.append(Text(title, w / 2.0, ty, 12, 'middle', '#111', bold=True, kind='title'))
    if K.sub:
        K.texts.append(Text(K.sub, w / 2.0, ty + 13, 9, 'middle', '#777', kind='cell'))
    if T:
        K.texts.append(Text(name, -4, -4, 9, 'end', '#555', italic=True, kind='inst'))
    else:
        K.texts.append(Text(name, 0, -5, 9, 'start', '#555', italic=True, kind='inst'))
    if getattr(K, 'role', '') == 'samp':
        for P in B:
            K.shapes.append(('poly', [(P.rx - 5, h), (P.rx, h - 7), (P.rx + 5, h)]))
        if B and h < 80:
            pass
    if K.bubble:
        for P in R:
            K.shapes.append(('circle', w + 5, P.ry, 5))
            P.rx = w + 10


def geom_dev(K):
    """Geometry of a device symbol in its own coordinates (origin = centre). Uses K.orient ('v'|'h'), K.gside, K.top."""
    K.shapes, K.texts = [], []
    o = K.orient
    name, size = K.id, K.size_text
    if K.kind == 'mos':
        gs = K.gside                      # 'l' / 'r' for vertical, 't' / 'b' for horizontal
        p = K.mtype == 'p'
        if o == 'v':
            sx = -1 if gs == 'l' else 1
            K.shapes += [('line', sx * 12, -12, sx * 12, 12), ('line', sx * 6, -16, sx * 6, 16),
                         ('line', sx * 6, -15, 0, -15), ('line', 0, -15, 0, -30), ('line', sx * 6, 15, 0, 15), ('line', 0, 15, 0, 30)]
            if p:
                K.shapes += [('circle', sx * 16, 0, 3), ('line', sx * 19, 0, sx * 30, 0)]
            else:
                K.shapes += [('line', sx * 12, 0, sx * 30, 0)]
            # arrow on the source lead
            sy = (-15 if K.top == 's' else 15)
            K.shapes.append(('poly', [(sx * 6, sy), (sx * 1, sy - 3), (sx * 1, sy + 3)] if not p else [(0, sy), (sx * 5, sy - 3), (sx * 5, sy + 3)]))
            K.pins[K.top].rx, K.pins[K.top].ry, K.pins[K.top].side = 0, -30, 't'
            bot = 'd' if K.top == 's' else 's'
            K.pins[bot].rx, K.pins[bot].ry, K.pins[bot].side = 0, 30, 'b'
            K.pins['g'].rx, K.pins['g'].ry, K.pins['g'].side = sx * 30, 0, gs
            K.box = (min(sx * 20, 0) - (0 if sx < 0 else 4), -22, max(sx * 20, 0) + (4 if sx < 0 else 0), 22)
            tx = 8 if sx < 0 else -8
            K.texts.append(Text(name, tx, -5, 9, 'start' if sx < 0 else 'end', '#555', italic=True, kind='inst'))
            K.texts.append(Text(size, tx, 8, 9, 'start' if sx < 0 else 'end', '#1a56a0', kind='size'))
        else:
            sy = -1 if gs == 't' else 1
            K.shapes += [('line', -12, sy * 12, 12, sy * 12), ('line', -16, sy * 6, 16, sy * 6),
                         ('line', -15, sy * 6, -15, 0), ('line', -15, 0, -30, 0), ('line', 15, sy * 6, 15, 0), ('line', 15, 0, 30, 0)]
            if p:
                K.shapes += [('circle', 0, sy * 16, 3), ('line', 0, sy * 19, 0, sy * 30)]
            else:
                K.shapes += [('line', 0, sy * 12, 0, sy * 30)]
            tgs = getattr(K, 'tg', None)          # transmission-gate half: channel pins join the other half vertically
            K.pins[K.left].rx, K.pins[K.left].ry, K.pins[K.left].side = -30, 0, ('l' if not tgs else ('b' if p else 't'))
            rt = 'd' if K.left == 's' else 's'
            K.pins[rt].rx, K.pins[rt].ry, K.pins[rt].side = 30, 0, ('r' if not tgs else ('b' if p else 't'))
            K.pins['g'].rx, K.pins['g'].ry, K.pins['g'].side = 0, sy * 30, gs
            K.box = (-22, min(sy * 20, 0) - (0 if sy < 0 else 4), 22, max(sy * 20, 0) + (4 if sy < 0 else 0))
            if tgs:
                ty = -22 if sy < 0 else 14
                K.texts.append(Text(name, 38, ty, 9, 'start', '#555', italic=True, kind='inst'))
                K.texts.append(Text(size, 38, ty + 10, 9, 'start', '#1a56a0', kind='size'))
            else:
                ty = 14 if sy < 0 else -18
                K.texts.append(Text(name, 0, ty, 9, 'middle', '#555', italic=True, kind='inst'))
                K.texts.append(Text(size, 0, ty + 11, 9, 'middle', '#1a56a0', kind='size'))
        return
    a, b = list(K.pins.keys())
    first, second = (K.top, b if K.top == a else a) if o == 'v' else (K.left, b if K.left == a else a)
    if o == 'v':
        K.pins[first].rx, K.pins[first].ry, K.pins[first].side = 0, -30, 't'
        K.pins[second].rx, K.pins[second].ry, K.pins[second].side = 0, 30, 'b'
        K.box = (-8, -20, 8, 20)
        if K.kind == 'res':
            pts = [(0, -30), (0, -18), (6, -15), (-6, -9), (6, -3), (-6, 3), (6, 9), (-6, 15), (0, 18), (0, 30)]
            K.shapes.append(('polyline', pts))
        elif K.kind == 'cap':
            K.shapes += [('line', 0, -30, 0, -4), ('line', -9, -4, 9, -4), ('line', -9, 4, 9, 4), ('line', 0, 4, 0, 30)]
        else:
            up = (first == 'k')          # cathode on top: triangle points up
            K.shapes += [('line', 0, -30, 0, -8), ('line', 0, 8, 0, 30)]
            if up:
                K.shapes += [('poly', [(-8, 8), (8, 8), (0, -8)]), ('line', -8, -8, 8, -8)]
            else:
                K.shapes += [('poly', [(-8, -8), (8, -8), (0, 8)]), ('line', -8, 8, 8, 8)]
        K.texts.append(Text(name, 12, -3, 9, 'start', '#555', italic=True, kind='inst'))
        K.texts.append(Text(size, 12, 9, 9, 'start', '#1a56a0', kind='size'))
    else:
        K.pins[first].rx, K.pins[first].ry, K.pins[first].side = -30, 0, 'l'
        K.pins[second].rx, K.pins[second].ry, K.pins[second].side = 30, 0, 'r'
        K.box = (-20, -8, 20, 8)
        if K.kind == 'res':
            pts = [(-30, 0), (-18, 0), (-15, -6), (-9, 6), (-3, -6), (3, 6), (9, -6), (15, 6), (18, 0), (30, 0)]
            K.shapes.append(('polyline', pts))
        elif K.kind == 'cap':
            K.shapes += [('line', -30, 0, -4, 0), ('line', -4, -9, -4, 9), ('line', 4, -9, 4, 9), ('line', 4, 0, 30, 0)]
        else:
            K.shapes += [('line', -30, 0, -8, 0), ('line', 8, 0, 30, 0), ('poly', [(-8, -8), (-8, 8), (8, 0)]), ('line', 8, -8, 8, 8)]
        K.texts.append(Text(name, 0, -12, 9, 'middle', '#555', italic=True, kind='inst'))
        K.texts.append(Text(size, 0, 19, 9, 'middle', '#1a56a0', kind='size'))


# ----------------------------------------------------------------------------- levels of nets (vertical order)
def net_levels(V):
    """Longest-path level of every net above ground / below supply, from the declared source and drain."""
    rl, sup = V.rails, V.sup
    gnd = rl - sup
    up = defaultdict(list)       # lower net -> [(upper net, comp)]
    dn = defaultdict(list)
    devs = [K for K in V.comps if K.kind != 'inst']
    # transmission gates (an n and a p device across the same two nets) are pass devices: no up/down direction
    tg = defaultdict(set)
    for K in devs:
        if K.kind == 'mos':
            tg[frozenset((K.pins['d'].nets[0], K.pins['s'].nets[0]))].add(K.mtype)
    for K in devs:
        if K.kind == 'mos':
            d, s = K.pins['d'].nets[0], K.pins['s'].nets[0]
            if len(tg[frozenset((d, s))]) == 2 and d not in rl and s not in rl and d != s:
                K.lo = K.hi = None
                continue
            lo, hi = (s, d) if K.mtype == 'n' else (d, s)
            # a rail fixes the direction regardless of the source/drain naming
            if lo in sup or hi in gnd:
                lo, hi = hi, lo
        else:
            a, b = [P.nets[0] for P in K.pins.values()]
            if a in rl and b in rl:
                lo, hi = (a, b) if a in gnd else (b, a)
            elif a in gnd or b in sup:
                lo, hi = a, b
            elif b in gnd or a in sup:
                lo, hi = b, a
            else:
                K.lo = K.hi = None
                continue
        K.lo, K.hi = lo, hi
        up[lo].append((hi, K))
        dn[hi].append((lo, K))
    lg = dict((r, 0) for r in gnd)
    changed, guard = True, 0
    while changed and guard < 60:
        changed, guard = False, guard + 1
        for lo in list(lg):
            for hi, K in up.get(lo, ()):
                if hi in rl:
                    continue
                if lg.get(hi, -1) < lg[lo] + 1 and lg[lo] + 1 < 40:
                    lg[hi] = lg[lo] + 1
                    changed = True
    ls = dict((r, 0) for r in sup)
    changed, guard = True, 0
    while changed and guard < 60:
        changed, guard = False, guard + 1
        for hi in list(ls):
            for lo, K in dn.get(hi, ()):
                if lo in rl:
                    continue
                if ls.get(lo, -1) < ls[hi] + 1 and ls[hi] + 1 < 40:
                    ls[lo] = ls[hi] + 1
                    changed = True
    return lg, ls, gnd


def classify_devices(V):
    """Vertical devices get K.orient='v' with K.lo/K.hi; pass devices and series passives become horizontal."""
    lg, ls, gnd = net_levels(V)
    rl = V.rails
    vert, horiz = [], []
    for K in V.comps:
        if K.kind == 'inst':
            continue
        if K.lo is None:
            K.orient = 'h'
            horiz.append(K)
            continue
        anchored = (K.lo in rl or K.lo in lg) or (K.hi in rl or K.hi in ls)
        if K.kind == 'mos' and not anchored:
            K.orient = 'h'
            horiz.append(K)
            continue
        if K.kind != 'mos' and K.lo not in rl and K.hi not in rl:
            K.orient = 'h'
            horiz.append(K)
            continue
        K.orient = 'v'
        vert.append(K)
    gmax = max([v for n, v in lg.items() if n not in rl] + [0])
    smax = max([v for n, v in ls.items() if n not in rl] + [0])

    def level(n):
        if n in gnd:
            return 0
        if n in lg:
            return lg[n]
        if n in ls and n not in rl:
            return gmax + 1 + (smax - ls[n])
        return None
    for K in vert:
        l = level(K.lo) if K.lo not in V.sup else None
        if l is None:
            h = level(K.hi) if K.hi not in rl else None
            l = (h - 1) if h is not None else 0
        K.level = max(l, 0)
    return vert, horiz, level


# ----------------------------------------------------------------------------- symmetry
def _terms(K):
    return (K.lo, K.pins['g'].nets[0], K.hi) if K.kind == 'mos' else (K.lo, K.hi)


def _key(K):
    return (K.kind, getattr(K, 'mtype', ''), K.size_text)


def find_symmetry(devs, rails):
    """Mirror symmetry of a transistor group: {comp: partner or itself} and the net map, or None."""
    mos = [K for K in devs if K.kind == 'mos']
    seeds = []
    for i, a in enumerate(mos):
        for b in mos[i + 1:]:
            if _key(a) != _key(b) or a.pins['g'].nets[0] == b.pins['g'].nets[0]:
                continue
            if (a.lo == b.lo and a.hi != b.hi) or (a.hi == b.hi and a.lo != b.lo):
                shared = a.lo if a.lo == b.lo else a.hi
                seeds.append((0 if shared not in rails else 1, len(seeds), a, b))
    seeds.sort(key=lambda t: t[:2])
    for _, _, a0, b0 in seeds[:12]:
        M = dict((r, r) for r in rails)
        part = {}

        def consistent(a, b):
            for na, nb in zip(_terms(a), _terms(b)):
                if na in M and M[na] != nb:
                    return False
                if nb in M and M[nb] != na:
                    return False
            return True

        def bind(a, b):
            part[a], part[b] = b, a
            for na, nb in zip(_terms(a), _terms(b)):
                M[na], M[nb] = nb, na
        if not consistent(a0, b0):
            continue
        bind(a0, b0)
        progress = True
        while progress:
            progress = False
            un = [K for K in devs if K not in part]
            for a in un:
                if a in part:
                    continue
                known = [n for n in _terms(a) if n in M and n not in rails]
                if not known:
                    continue
                cands = [b for b in un if b is not a and b not in part and _key(b) == _key(a) and consistent(a, b)
                         and tuple(M.get(n, None) for n in _terms(a)) != _terms(a)]
                cands = [b for b in cands if any(M.get(na) == nb for na, nb in zip(_terms(a), _terms(b)) if na not in rails)]
                if len(cands) == 1:
                    bind(a, cands[0])
                    progress = True
            if progress:
                continue
            for a in un:
                if a in part:
                    continue
                t = _terms(a)
                known = [n for n in t if n in M]
                if known and all(M[n] == n for n in known) and any(n not in rails for n in known):
                    part[a] = a
                    for n in t:
                        M[n] = n
                    progress = True
                    break
        if all(K in part for K in devs) and any(part[K] is not K for K in devs):
            return part, M
    return None


# ----------------------------------------------------------------------------- transistor cluster layout
def _chains(devs, block_nets=()):
    """Link the device below a node with the device above it so that they share a column."""
    by_hi, by_lo = defaultdict(list), defaultdict(list)
    for K in devs:
        by_hi[K.hi].append(K)
        by_lo[K.lo].append(K)
    parent = dict((K, K) for K in devs)

    def find(x):
        while parent[x] is not x:
            x = parent[x]
        return x

    def score(K):
        w = NL.num(K.dev.params.get('w', '0')) or 0
        try:
            m = float(K.dev.params.get('m', '1'))
        except ValueError:
            m = 1.0
        return (1 if K.kind == 'mos' else 0, w * m)
    linked_up, linked_dn = set(), set()
    for n in list(by_hi):
        if n in block_nets or n not in by_lo:
            continue
        downs = [K for K in by_hi[n]]
        ups = [K for K in by_lo[n]]
        a = max(downs, key=score)
        b = max(ups, key=score)
        if a in linked_up or b in linked_dn or a is b:
            continue
        linked_up.add(a)
        linked_dn.add(b)
        parent[find(a)] = find(b)
    cols = OrderedDict()
    for K in devs:
        cols.setdefault(find(K), []).append(K)
    return list(cols.values())


def layout_cluster(devs, V, level=None):
    """Place the vertical devices of one channel-connected cluster. Sets K.cx, K.cy, K.gside, K.top."""
    rails = V.rails
    index = dict((K, i) for i, K in enumerate(devs))
    for K in devs:
        top = level(K.hi) if (level and K.hi not in rails) else None
        K.rows = set(range(K.level, max(K.level + 1, top if top is not None else 0)))
    sym = find_symmetry(devs, rails) if len(devs) >= 3 else None
    xs = {}
    if sym:
        part, M = sym
        center = [K for K in devs if part[K] is K]
        pairs = [K for K in devs if part[K] is not K]
        # side of each pair member
        left = set()
        adj = defaultdict(list)
        for K in pairs:
            for n in (K.lo, K.hi):
                if n not in rails and M.get(n) != n:
                    adj[n].append(K)
        todo = sorted(pairs, key=lambda K: index[K])
        seen = set()
        for K0 in todo:
            if K0 in seen:
                continue
            first = K0 if index[K0] < index[part[K0]] else part[K0]
            stack = [first]
            left.add(first)
            seen.update((first, part[first]))
            while stack:
                K = stack.pop()
                for n in (K.lo, K.hi):
                    for J in adj.get(n, ()):
                        if J not in seen:
                            seen.update((J, part[J]))
                            left.add(J)
                            stack.append(J)
        # groups: every pair with what hangs on it; one axis per group
        gp = dict((K, K) for K in devs)

        def find(x):
            while gp[x] is not x:
                x = gp[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra is not rb:
                if index[ra] < index[rb]:
                    gp[rb] = ra
                else:
                    gp[ra] = rb
        for K in pairs:
            union(K, part[K])
        # heads: pairs whose two devices share their source node (a differential pair)
        def src_net(K):
            return K.lo if getattr(K, 'mtype', 'n') == 'n' else K.hi
        heads = [K for K in pairs if K.kind == 'mos' and src_net(K) == src_net(part[K]) and src_net(K) not in rails
                 and K.pins['g'].nets[0] != part[K].pins['g'].nets[0]]
        head_set = set(heads)
        owner = {}
        for K in sorted(heads, key=lambda K: index[K]):
            owner[K] = find(K)
        # other paired devices join the first head they touch through a one-sided node
        changed = True
        while changed:
            changed = False
            for K in sorted(pairs, key=lambda K: index[K]):
                if K in owner or K in head_set:
                    continue
                for n in (K.lo, K.hi):
                    own = sorted([owner[J] for J in adj.get(n, ()) if J in owner], key=lambda r: index[r])
                    if own:
                        owner[K] = own[0]
                        owner[part[K]] = own[0]
                        changed = True
                        break
        for K in pairs:
            if K in owner:
                union(K, owner[K])
        for n, lst in adj.items():
            free = [K for K in lst if K not in owner]
            for K in free[1:]:
                union(free[0], K)
            if free and len(free) < len(lst):
                union(free[0], [K for K in lst if K in owner][0])
        for c in center:
            above = [K for K in devs if K.lo == c.hi and c.hi not in rails]
            below = [K for K in devs if K.hi == c.lo and c.lo not in rails]
            pa = [K for K in above if part[K] is not K]
            pb = [K for K in below if part[K] is not K]
            for K in pa:
                union(c, K)
            if not pa:
                for K in pb:
                    union(c, K)
            if len(above) == 1 and part[above[0]] is above[0]:
                union(c, above[0])
        groups = OrderedDict()
        for K in devs:
            groups.setdefault(find(K), []).append(K)
        gx = 0
        for root, gd in groups.items():
            cen = [K for K in gd if part[K] is K]
            lef = [K for K in gd if K in left]
            placed = []                        # (x, level)
            selfnets = set(n for n, m in M.items() if n == m)
            ccols = _chains(cen)
            # centre columns that share a row are spread around the axis
            comps_ = []
            for col in ccols:
                lv = set(r for K in col for r in K.rows)
                hit = [c for c in comps_ if c[1] & lv]
                if hit:
                    base = hit[0]
                    base[0].append(col)
                    base[1].update(lv)
                    for h in hit[1:]:
                        base[0].extend(h[0])
                        base[1].update(h[1])
                        comps_.remove(h)
                else:
                    comps_.append([[col], set(lv)])
            for cols_, lv in comps_:
                k = len(cols_)
                for i, col in enumerate(cols_):
                    off = int((i - (k - 1) / 2.0) * XP)
                    for K in col:
                        xs[K] = ('g', root, snap(off))
                        for r_ in K.rows:
                            placed.append((off, r_))
            lcols = _chains(lef, block_nets=selfnets)
            lcols.sort(key=lambda col: (0 if any((K.lo in selfnets and K.lo not in rails) or (K.hi in selfnets and K.hi not in rails) for K in col) else 1,
                                        min(index[K] for K in col)))
            for col in lcols:
                s = 1
                while True:
                    x = -s * XP
                    rows_ = set(r for K in col for r in K.rows)
                    if not any(abs(x - px) < XP and pl in rows_ for px, pl in placed) and \
                            not any(abs(-x - px) < XP and pl in rows_ for px, pl in placed if px > 0):
                        break
                    s += 1
                for K in col:
                    xs[K] = ('g', root, x)
                    xs[part[K]] = ('g', root, -x)
                    for r_ in K.rows:
                        placed.append((x, r_))
                        placed.append((-x, r_))
            ext = max([abs(x) for x, l in placed] + [0])
            for K in gd:
                xs[K] = gx + ext + xs[K][2]
            gx += 2 * ext + XP + 30
        for K in devs:
            K.sym_side = 'c' if part[K] is K else ('l' if K in left else 'r')
            K.partner = part[K]
        if not hasattr(V, 'cross_ok'):
            V.cross_ok = set()
        for a_, b_ in M.items():
            if a_ != b_:
                V.cross_ok.add(((a_,), (b_,)))
                V.cross_ok.add(((b_,), (a_,)))
    else:
        cols = _chains(devs)
        # keep columns that share a node next to each other
        order, seen = [], set()
        net_cols = defaultdict(list)
        for ci, col in enumerate(cols):
            for K in col:
                for n in (K.lo, K.hi):
                    if n not in rails:
                        net_cols[n].append(ci)

        def visit(ci):
            if ci in seen:
                return
            seen.add(ci)
            order.append(ci)
            for K in cols[ci]:
                for n in (K.lo, K.hi):
                    for cj in net_cols.get(n, ()):
                        visit(cj)
        for ci in range(len(cols)):
            visit(ci)
        slots = []                              # per slot: rows used
        for ci in order:
            lv = set(r for K in cols[ci] for r in K.rows)
            x = len(slots) * XP
            slots.append(lv)
            for K in cols[ci]:
                xs[K] = x
        for K in devs:
            K.sym_side = None
    for K in devs:
        K.cx = xs[K]
        K.cy = -(K.level * ROW) - ROW // 2
        K.top_net, K.bot_net = K.hi, K.lo
    # gate side: towards the other pins of the gate net, outwards when the net comes from outside
    pos = defaultdict(list)
    for K in devs:
        for n in (K.lo, K.hi):
            pos[n].append(K.cx)
        if K.kind == 'mos':
            pos[('g', K.pins['g'].nets[0])].append(K.cx)
    for K in devs:
        if K.kind != 'mos':
            K.top = [p for p, P in K.pins.items() if P.nets[0] == K.hi][0]
            continue
        g = K.pins['g'].nets[0]
        others = [x for x in pos.get(g, []) if True] + [x for x in pos.get(('g', g), []) if x != K.cx]
        chan = [x for x in pos.get(g, [])]
        if chan:
            c = sum(chan) / float(len(chan))
            K.gside = 'r' if c > K.cx + 1 else ('l' if c < K.cx - 1 else ('l' if K.sym_side != 'r' else 'r'))
        elif K.sym_side == 'r':
            K.gside = 'r'
        elif K.sym_side == 'l':
            K.gside = 'l'
        else:
            og = [x for x in pos.get(('g', g), []) if x != K.cx]
            K.gside = 'r' if og and sum(og) / len(og) > K.cx and K.sym_side is None and False else 'l'
        d, s = K.pins['d'].nets[0], K.pins['s'].nets[0]
        K.top = 'd' if (d == K.hi and s == K.lo) or (d == K.hi) else 's'
    for K in devs:
        geom_dev(K)
    x0 = min(K.cx + K.box[0] for K in devs) - 40
    return devs


# ----------------------------------------------------------------------------- units and flow placement
class Unit(object):
    def __init__(self, comps, kind):
        self.comps, self.kind = comps, kind
        self.x = self.y = 0
        self.layer = None

    def rel_bbox(self):
        """Bounding box of the unit in its own coordinates, text included."""
        x0 = y0 = 1e9
        x1 = y1 = -1e9
        for K in self.comps:
            ox, oy = getattr(K, 'cx', 0), getattr(K, 'cy', 0)
            bx = K.box
            x0, y0, x1, y1 = min(x0, ox + bx[0]), min(y0, oy + bx[1]), max(x1, ox + bx[2]), max(y1, oy + bx[3])
            for P in K.pins.values():
                x0, y0, x1, y1 = min(x0, ox + P.rx), min(y0, oy + P.ry), max(x1, ox + P.rx), max(y1, oy + P.ry)
                if P.name in K.rail_pins or P.name in K.gray_pins:
                    ex, ey = ESC[P.side]
                    x0, y0 = min(x0, ox + P.rx + ex * 30 - 20), min(y0, oy + P.ry + ey * 26 - 6)
                    x1, y1 = max(x1, ox + P.rx + ex * 30 + 20), max(y1, oy + P.ry + ey * 26 + 6)
            for T in K.texts:
                b = T.bbox()
                x0, y0, x1, y1 = min(x0, ox + b[0]), min(y0, oy + b[1]), max(x1, ox + b[2]), max(y1, oy + b[3])
        return x0, y0, x1, y1


def place(V):
    """Place every component of the view. Returns (units, ports) with absolute pin coordinates in K.pins[*].x/.y."""
    vert, horiz, level = classify_devices(V)
    rails = V.rails
    units = []
    # clusters of vertical devices
    parent = dict((K, K) for K in vert)

    def find(x):
        while parent[x] is not x:
            x = parent[x]
        return x
    bynet = defaultdict(list)
    for K in vert:
        for n in (K.lo, K.hi):
            if n not in rails:
                bynet[n].append(K)
    for n, lst in bynet.items():
        for K in lst[1:]:
            parent[find(K)] = find(lst[0])
    clusters = OrderedDict()
    for K in vert:
        clusters.setdefault(find(K), []).append(K)
    comp_unit = {}
    for K in V.comps:
        if K.kind == 'inst':
            geom_inst(K)
            K.cx = K.cy = 0
            U = Unit([K], 'inst')
            units.append((V.comps.index(K), U))
            comp_unit[K] = U
    for root, devs in clusters.items():
        layout_cluster(devs, V, level)
        U = Unit(devs, 'cluster')
        units.append((min(V.comps.index(K) for K in devs), U))
        for K in devs:
            comp_unit[K] = U
    tgmap = defaultdict(list)
    for K in horiz:
        if K.kind == 'mos':
            tgmap[frozenset((K.pins['d'].nets[0], K.pins['s'].nets[0]))].append(K)
    done_h = set()
    for K in horiz:
        if K in done_h:
            continue
        K.cx = K.cy = 0
        grp = [K]
        if K.kind == 'mos':
            K.gside = 't' if K.mtype == 'p' else 'b'
            K.left = 'd'
            mates = tgmap[frozenset((K.pins['d'].nets[0], K.pins['s'].nets[0]))]
            if len(mates) == 2 and set(m.mtype for m in mates) == {'n', 'p'}:
                grp = sorted(mates, key=lambda m: m.mtype != 'p')
                for m in grp:
                    m.tg = True
                    m.cx, m.cy = 0, (-20 if m.mtype == 'p' else 20)
                    m.gside = 't' if m.mtype == 'p' else 'b'
                    m.left = 'd'
        else:
            K.left = list(K.pins.keys())[0]
        U = Unit(grp, 'pass')
        U.tg = len(grp) == 2
        for m in grp:
            done_h.add(m)
            comp_unit[m] = U
        units.append((V.comps.index(K), U))
    units = [U for _, U in sorted(units, key=lambda t: t[0])]
    # ------------------------------------------------ signal order: who drives each net
    key_pins = defaultdict(list)
    for K in V.comps:
        for P in K.pins.values():
            if P.name in K.rail_pins or P.name in K.gray_pins:
                continue
            key_pins[P.nets].append((K, P))
    in_ports = set(t for name, t, k, d in V.ports if d == 'in')
    drv = defaultdict(set)         # net key -> units that drive it
    snk = defaultdict(set)
    for key, lst in key_pins.items():
        for K, P in lst:
            U = comp_unit[K]
            if K.kind == 'inst':
                (drv if P.dir == 'out' else snk)[key].add(U)
            elif K.kind == 'mos' and P.name == 'g':
                snk[key].add(U)
            elif U.kind == 'cluster':
                drv[key].add(U)
    ready = set(in_ports)
    layer = {}
    pending = list(units)
    # pass devices: the side that is reached first is the input
    def unit_inputs(U):
        if U.kind == 'pass':
            return None
        return [k for k in snk if U in snk[k] and not (U in drv[k])]
    guard = 0
    avail = dict((k, 0) for k in ready)
    while pending and guard < 10000:
        guard += 1
        progressed = False
        for U in list(pending):
            if U.kind == 'pass':
                K = U.comps[0]
                keys = [P.nets for P in K.pins.values() if P.name != 'g' and P.name not in K.rail_pins and P.name not in K.gray_pins]
                got = [k for k in keys if k in avail]
                if got:
                    layer[U] = max(avail[k] for k in got)
                    src = got[0]
                    for K2 in U.comps:
                        K2.left = [p for p, P in K2.pins.items() if P.nets == src and p != 'g'][0]
                    for k in keys:
                        if k not in avail:
                            avail[k] = layer[U] + 1
                    pending.remove(U)
                    progressed = True
                continue
            ins = [k for k in unit_inputs(U) if drv[k] - {U} or k in in_ports]
            if all(k in avail for k in ins):
                layer[U] = max([avail[k] for k in ins] + [0])
                for k in drv:
                    if U in drv[k]:
                        avail[k] = max(avail.get(k, 0), layer[U] + 1)
                pending.remove(U)
                progressed = True
        if not progressed:
            # feedback loop: release the unit with the most inputs already known (first in netlist order on ties)
            def sc(U):
                if U.kind == 'pass':
                    return -1
                ins = [k for k in unit_inputs(U) if drv[k] - {U} or k in in_ports]
                return sum(1 for k in ins if k in avail) / float(len(ins) or 1)
            top_sc = max(sc(U) for U in pending)
            rel = [U for U in pending if sc(U) == top_sc]
            newly = []
            for U in rel:
                if U.kind == 'pass':
                    layer[U] = 0
                    K = U.comps[0]
                    for P in K.pins.values():
                        if P.name != 'g' and P.nets not in avail:
                            newly.append((P.nets, 1))
                else:
                    ins = [k for k in unit_inputs(U) if k in avail]
                    layer[U] = max([avail[k] for k in ins] + [0])
                    for k in drv:
                        if U in drv[k]:
                            newly.append((k, layer[U] + 1))
                pending.remove(U)
            for k, v in newly:
                avail[k] = max(avail.get(k, 0), v)
    for U in units:
        U.layer = layer.get(U, 0)
        for K in U.comps:
            if U.kind == 'pass':
                geom_dev(K)
    # ------------------------------------------------ coordinates
    def skip(K, P):
        return P.name in K.rail_pins or P.name in K.gray_pins

    def is_in(U, K, P):
        return (K.kind == 'inst' and P.dir == 'in' and P.side == 'l') or (K.kind == 'mos' and P.name == 'g' and U.kind != 'pass') or \
               (U.kind == 'pass' and P.name == getattr(K, 'left', None))

    def is_out(U, K, P):
        return (K.kind == 'inst' and P.dir == 'out') or (U.kind == 'cluster' and P.name != 'g') or \
               (U.kind == 'pass' and P.name not in ('g', getattr(K, 'left', None)))
    layers = defaultdict(list)
    for U in units:
        layers[U.layer].append(U)
    fan = defaultdict(int)         # unit -> number of pins it drives in other units
    for key, lst in key_pins.items():
        ds = set(comp_unit[K] for K, P in lst if is_out(comp_unit[K], K, P))
        if len(ds) == 1:
            D = list(ds)[0]
            fan[D] += sum(1 for K, P in lst if comp_unit[K] is not D)

    def assign(force):
        """One left-to-right pass. `force` fixes the height of some units (straight wires first: a unit that could
        not sit level with its driver moves the driver instead). Returns the connections that are still not level."""
        x = 0
        placed_pin = {}            # net key -> (x, y, unit) of a pin that drives it (already placed)
        placed_any = {}
        primary = {}               # unit -> net key it was aligned on
        for li in sorted(layers):
            col = layers[li]
            boxes = [U.rel_bbox() for U in col]
            wmax = max(b[2] - b[0] for b in boxes)
            want = []
            for U, b in zip(col, boxes):
                y = None
                for K in U.comps:
                    for P in K.pins.values():
                        if skip(K, P):
                            continue
                        if is_in(U, K, P) and P.nets in placed_pin and y is None:
                            y = placed_pin[P.nets][1] - ((getattr(K, 'cy', 0) + P.ry) if not getattr(U, 'tg', False) else 0)
                            primary[U] = P.nets
                if y is None:
                    for K in U.comps:
                        for P in K.pins.values():
                            if skip(K, P) or y is not None:
                                continue
                            if P.nets in placed_any and (K.kind == 'inst' and P.dir == 'in' and P.side == 'l'):
                                y = placed_any[P.nets][1] + 80 - (getattr(K, 'cy', 0) + P.ry)
                if U in force:
                    y = force[U]
                want.append(y)
            nets_of = []
            for U in col:
                ns = set()
                for K in U.comps:
                    for P in K.pins.values():
                        if not skip(K, P):
                            ns.add(P.nets)
                nets_of.append(ns)
            cls_rank = []
            for U in col:
                r = 9
                for K in U.comps:
                    for P in K.pins.values():
                        r = min(r, {'hs_data': 0, 'reference': 1, 'hs_clock': 2}.get(P.cls, 5))
                cls_rank.append(r)
            first = sorted(range(len(col)), key=lambda i: (want[i] is None, want[i] if want[i] is not None else 0, cls_rank[i], i))
            # units with a wanted height first; the others go into the free room behind the unit they share a net with
            order = [i for i in first if want[i] is not None] + [i for i in first if want[i] is None]
            used = []                   # (top, bottom, has bottom pins, index)
            for i in order:
                U, b = col[i], boxes[i]
                has_t = any(P.side == 't' and not skip(K, P) for K in U.comps for P in K.pins.values())
                has_b = any(P.side == 'b' and not skip(K, P) for K in U.comps for P in K.pins.values())
                y = want[i]
                if y is None:
                    rel = [u for u in used if nets_of[i] & nets_of[u[3]]]
                    ref = rel[-1] if rel else (max(used, key=lambda u: u[1]) if used else None)
                    y = (ref[1] + 40 + 30 * RELAX[0] + (60 if has_t else 0) + (60 if ref[2] else 0) - b[1]) if ref else -b[1]
                y = snap(y)
                # no overlap with units already in this layer: push down
                moved = True
                while moved:
                    moved = False
                    for t, bt, hb, _ in used:
                        gap = 30 + 30 * RELAX[0] + (60 if has_t else 0) + (60 if hb else 0)
                        gap_up = 30 + 30 * RELAX[0] + (60 if has_b else 0)
                        if y + b[1] < bt + gap and y + b[3] > t - gap_up:
                            y = snap_up(bt + gap - b[1])
                            moved = True
                used.append((y + b[1], y + b[3], has_b, i))
                U.x, U.y = snap_up(x - b[0]), y
                for K in U.comps:
                    K.x, K.y = U.x + getattr(K, 'cx', 0), U.y + getattr(K, 'cy', 0)
                    for P in K.pins.values():
                        P.x, P.y = K.x + P.rx, K.y + P.ry
            for U in col:
                for K in U.comps:
                    for P in K.pins.values():
                        if skip(K, P):
                            continue
                        if is_out(U, K, P):
                            placed_pin.setdefault(P.nets, (P.x, P.y if not getattr(U, 'tg', False) else U.y, U, P.side))
                        placed_any.setdefault(P.nets, (P.x, P.y))
            x = snap_up(x + wmax + 140 + 60 * RELAX[0])
        # connections between facing pins that are not level
        mis = []
        level_ = defaultdict(int)          # unit -> sinks that already sit level with it
        for U in units:
            if getattr(U, 'tg', False):
                continue
            for K in U.comps:
                for P in K.pins.values():
                    if skip(K, P) or not is_in(U, K, P) or P.nets not in placed_pin:
                        continue
                    dx, dy, D, dside = placed_pin[P.nets]
                    if D is U or D.layer >= U.layer or getattr(D, 'tg', False):
                        continue
                    if P.side != 'l' or dside != 'r' or dx >= P.x:
                        continue
                    off = P.y - dy
                    if off:
                        mis.append((U, D, off, primary.get(U) == P.nets, len(key_pins[P.nets]) == 2))
                    else:
                        level_[D] += 1
        return [m for m in mis if not level_[m[1]]]
    force, best = {}, None
    for it in range(24):
        mis = assign(force)
        score = sum(1 for m in mis if m[3] or m[4])
        if best is None or score < best[0]:
            best = (score, dict(force))
        if not score:
            break
        changed = False
        for U, D, off, prim, two in mis:
            if D in force:
                continue
            if prim or (two and fan[D] == 1):
                force[D] = D.y + off
                changed = True
                break                      # one move at a time: the next pass sees its effect
        if not changed:
            break
    if best[1] != force:
        assign(best[1])
    return units, key_pins
