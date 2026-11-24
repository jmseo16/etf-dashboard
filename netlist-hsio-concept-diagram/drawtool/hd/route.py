"""Wire routing on a 10 px grid and scene assembly.

First principle: a connection is a straight line whenever the two ends can be joined by one.
The search minimises (number of bends, then length); a wire never crosses another net on a block
screen. When no clean wire exists the two ends get the same net label instead (never a loose end).
"""
import heapq
from collections import OrderedDict, defaultdict
from . import layout as LY
from .layout import G, ESC, Text, tw, snap
from .views import bus_label

DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]          # R D L U
BIT = {(1, 0): 1, (0, 1): 2, (-1, 0): 4, (0, -1): 8}
BEND, CROSS = 40, 120
MAXEXP = 20000


AUTO = __import__('re').compile(r'^(net|n)\d+$')


class Term(object):
    """Something a wire ends on: a symbol pin or a port."""
    def __init__(self, key, x, y, esc, owner, pin=None, port=None):
        self.key, self.x, self.y, self.esc = key, x, y, esc
        self.cell = (x // G, y // G)
        self.owner, self.pin, self.port = owner, pin, port
        self.wired = False
        self.nowire = False       # must be joined by a net label (keeps a differential pair drawn the same way)


class Router(object):
    def __init__(self, allow_cross=None):
        self.block = set()
        self.h, self.v = {}, {}
        self.arms = defaultdict(int)             # (net, cell) -> direction bits
        self.pincell = {}
        self.cells = defaultdict(set)            # net -> wire cells
        self.paths = defaultdict(list)           # net -> list of cell paths
        self.allow_cross = allow_cross or (lambda a, b: False)
        self.textboxes = []
        self.boxes = []
        self.fourway = []
        self.soft = {}                           # cell -> extra cost (room kept free in front of pins)
        self.softnet = {}

    def block_rect(self, x0, y0, x1, y1, pad=0):
        for gx in range(int((x0 - pad) // G), int(-(-(x1 + pad) // G)) + 1):
            for gy in range(int((y0 - pad) // G), int(-(-(y1 + pad) // G)) + 1):
                if x0 - pad < gx * G < x1 + pad and y0 - pad < gy * G < y1 + pad:
                    self.block.add((gx, gy))

    def block_text(self, T):
        b = T.bbox()
        self.textboxes.append(b)
        for gx in range(int((b[0] - 5) // G), int(-(-(b[2] + 5) // G)) + 1):
            for gy in range(int((b[1] - 5) // G), int(-(-(b[3] + 5) // G)) + 1):
                if b[0] - 5 <= gx * G <= b[2] + 5 and b[1] - 5 <= gy * G <= b[3] + 5:
                    self.block.add((gx, gy))

    def free_rect(self, x0, y0, x1, y1, key=None):
        for b in self.textboxes + self.boxes:
            if min(x1, b[2]) - max(x0, b[0]) > 0.5 and min(y1, b[3]) - max(y0, b[1]) > 0.5:
                return False
        for gx in range(int(x0 // G), int(-(-x1 // G)) + 1):
            for gy in range(int(y0 // G), int(-(-y1 // G)) + 1):
                if x0 - 1 <= gx * G <= x1 + 1 and y0 - 1 <= gy * G <= y1 + 1:
                    c = (gx, gy)
                    if c in self.block or c in self.h or c in self.v or (c in self.pincell and self.pincell[c] != key):
                        return False
        return True

    # ---------------------------------------------------------------- occupancy
    def can_step(self, net, b, d, goals):
        """Return 0 (free), 1 (crossing another net, must go straight), or -1 (blocked)."""
        if b in self.block and b not in goals:
            return -1
        pn = self.pincell.get(b)
        if pn is not None and pn != net:
            return -1
        if b in self.cells[net]:
            a = self.arms[(net, b)]
            if bin(a).count('1') >= 3 and not a & BIT[(-d[0], -d[1])]:
                return -1                 # a fourth line into one point: never
        same, perp = (self.h, self.v) if d[1] == 0 else (self.v, self.h)
        o = same.get(b)
        if o is not None and o != net:
            return -1
        o = perp.get(b)
        if o is not None and o != net:
            a = self.arms[(o, b)]
            if self.allow_cross(net, o) and a in (5, 10):
                return 1
            return -1
        return 0

    def add_path(self, net, path):
        for a, b in zip(path, path[1:]):
            d = (b[0] - a[0], b[1] - a[1])
            m = self.h if d[1] == 0 else self.v
            m[a] = net
            m[b] = net
            self.arms[(net, a)] |= BIT[d]
            self.arms[(net, b)] |= BIT[(-d[0], -d[1])]
            self.cells[net].add(a)
            self.cells[net].add(b)
        self.paths[net].append(path)
        for c in path:
            if bin(self.arms[(net, c)]).count('1') == 4:
                self.fourway.append((net, c, len(self.paths[net])))

    # ---------------------------------------------------------------- search
    def route(self, net, start, esc, goals, limit=MAXEXP):
        """Least-bend path from a terminal cell to any goal cell.
        goals: {cell: None | set of allowed arrival directions}. Returns the cell path or None."""
        if not goals:
            return None
        gx0 = min(c[0] for c in goals)
        gx1 = max(c[0] for c in goals)
        gy0 = min(c[1] for c in goals)
        gy1 = max(c[1] for c in goals)

        def hfun(c):
            dx = gx0 - c[0] if c[0] < gx0 else (c[0] - gx1 if c[0] > gx1 else 0)
            dy = gy0 - c[1] if c[1] < gy0 else (c[1] - gy1 if c[1] > gy1 else 0)
            return dx + dy
        first = (start[0] + esc[0], start[1] + esc[1])
        st = self.can_step(net, first, esc, goals)
        if st < 0:
            return None
        # state: (cell, dir index, run (1|2), turned (0|1), must_straight (0|1))
        s0 = (first, DIRS.index(esc), 1, 0, 1 if st == 1 else 0)
        best = {s0: 1 + (CROSS if st == 1 else 0)}
        prev = {s0: None}
        pq = [(best[s0] + hfun(first), best[s0], s0)]
        nexp = 0
        own = self.cells[net]
        while pq:
            f, g, s = heapq.heappop(pq)
            if best.get(s, 1e18) < g:
                continue
            c, di, run, turned, ms = s
            d = DIRS[di]
            if c in goals and not ms and c != start:
                ok = goals[c] is None or d in goals[c]
                if ok and goals[c] is None:
                    # joining an existing wire of this net: no 4-way junction
                    a = self.arms[(net, c)] | BIT[(-d[0], -d[1])]
                    ok = bin(a).count('1') <= 3
                if ok and (run >= 2 or not turned):
                    path = [c]
                    t = s
                    while prev[t] is not None:
                        t = prev[t]
                        path.append(t[0])
                    path.append(start)
                    path.reverse()
                    return path
                if c in self.block or (c in self.pincell and self.pincell[c] == net) or goals[c] is not None:
                    continue
            nexp += 1
            if nexp > limit:
                return None
            for ni, nd in enumerate(DIRS):
                if nd == (-d[0], -d[1]):
                    continue
                turn = ni != di
                if turn and (run < 2 or ms):
                    continue
                b = (c[0] + nd[0], c[1] + nd[1])
                r = self.can_step(net, b, nd, goals)
                if r < 0:
                    continue
                if turn and c in own:
                    pass
                ng = g + 1 + (BEND if turn else 0) + (CROSS if r == 1 else 0) + (0 if self.softnet.get(b) == net else self.soft.get(b, 0))
                ns = (b, ni, 1 if turn else 2, 1 if (turned or turn) else 0, 1 if r == 1 else 0)
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = s
                    heapq.heappush(pq, (ng + hfun(b), ng, ns))
        return None

    def straight_free(self, net, a, b):
        """Cells strictly between a and b on one line are free for this net."""
        if a[0] == b[0]:
            d = (0, 1 if b[1] > a[1] else -1)
        elif a[1] == b[1]:
            d = (1 if b[0] > a[0] else -1, 0)
        else:
            return False
        c = (a[0] + d[0], a[1] + d[1])
        goals = {b: None}
        last = 0
        while c != b:
            r = self.can_step(net, c, d, goals)
            if r < 0:
                return False
            last = r
            c = (c[0] + d[0], c[1] + d[1])
        return last == 0


def segments(path):
    """Cell path -> list of straight segments in px."""
    out = []
    i = 0
    while i < len(path) - 1:
        j = i + 1
        d = (path[j][0] - path[i][0], path[j][1] - path[i][1])
        while j + 1 < len(path) and (path[j + 1][0] - path[j][0], path[j + 1][1] - path[j][1]) == d:
            j += 1
        out.append([path[i][0] * G, path[i][1] * G, path[j][0] * G, path[j][1] * G])
        i = j
    return out


def build_scene(V, allow_pairs=()):
    """Draw one view. When labels or ports find no room the screen is redrawn with wider spacing (up to 3 steps)."""
    import copy
    best = None
    reserve = set()
    nowire = set()
    for pstep in range(3):
        S = _try_scene(V, allow_pairs, nowire)
        add = _pair_fix(V, S)
        if not add - nowire:
            break
        nowire |= add
    for k_ in ('_labelled', '_split', '_cross'):
        S.pop(k_, None)
    return S


def _pair_fix(V, S):
    """Pins to hang on labels so that both nets of a differential pair reach a symbol the same way."""
    lab = defaultdict(set)
    for cid, pin, key in S.get('_labelled', []):
        lab[cid].add(key)
    pairs = set()
    keys = [P.nets for K in V.comps for P in K.pins.values() if len(P.nets) == 1 and P.name not in K.rail_pins and P.name not in K.gray_pins]
    ks = sorted(set(keys))
    from .analyze import _pair_name
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if _pair_name(a[0], b[0]):
                pairs.add((a, b))
    for a, b in S.get('_cross', []):
        pairs.add((tuple(a), tuple(b)))
    add = set()
    for K in V.comps:
        mine = dict((P.nets, P.name) for P in K.pins.values())
        for a, b in pairs:
            if a in mine and b in mine and ((a in lab[K.id]) != (b in lab[K.id])):
                add.add((K.id, mine[a]))
                add.add((K.id, mine[b]))
    return add


def _try_scene(V, allow_pairs, nowire):
    import copy
    best = None
    reserve = set()
    for step in range(4):
        LY.RELAX[0] = max(0, step - 1)
        V2 = copy.deepcopy(V)
        V2.reserve = set(reserve)
        V2.nowire = set(nowire)
        S = _build_scene(V2, allow_pairs)
        n = len(S.get('problems', []))
        if best is None or n < best[0]:
            best = (n, S)
        if n == 0:
            break
        reserve.update(tuple(x) for x in S.get('problem_pins', []))
    LY.RELAX[0] = 0
    best[1].pop('problem_pins', None)
    return best[1]


def _build_scene(V, allow_pairs=()):
    """Place, route and assemble the drawable scene of one view."""
    units, key_pins = LY.place(V)
    allow = set()
    for a, b in allow_pairs:
        allow.add((a, b))
        allow.add((b, a))
    fb = set(getattr(V, 'feedback', ()))
    R = Router(allow_cross=lambda a, b: (a, b) in allow or a in fb or b in fb)
    S = {'id': V.id, 'title': V.title, 'level': V.level, 'cell': V.cell, 'symbols': [], 'wires': [], 'dots': [], 'labels': [],
         'ports': [], 'texts': [], 'tags': [], 'slashes': []}
    comps = [K for U in units for K in U.comps]
    # ------------------------------------------------ symbols, obstacles, rail tags, gray labels
    terms = defaultdict(list)
    gray_done = set()
    for K in comps:
        bx = K.box
        R.block_rect(K.x + bx[0] - 1, K.y + bx[1] - 1, K.x + bx[2] + 1, K.y + bx[3] + 1)
        R.boxes.append((K.x + bx[0], K.y + bx[1], K.x + bx[2], K.y + bx[3]))
        if K.kind == 'mos' or (K.kind in ('res', 'cap', 'dio') and getattr(K, 'orient', '') == 'v'):   # leads outside the box: no wire over them
            for P in K.pins.values():
                if P.name == 'g':
                    continue
                if P.rx == 0:
                    R.block_rect(P.x - 1, min(K.y, P.y) + (1 if P.y < K.y else 0), P.x + 1, max(K.y, P.y) - (1 if P.y > K.y else 0))
                else:
                    R.block_rect(min(K.x, P.x) + (1 if P.x < K.x else 0), P.y - 1, max(K.x, P.x) - (1 if P.x > K.x else 0), P.y + 1)
        for T in K.texts:
            T2 = Text(T.s, K.x + T.x, K.y + T.y, T.size, T.anchor, T.color, T.italic, T.bold, T.kind)
            T2.owner = K.id
            if T2.s:
                S['texts'].append(T2)
                if not (K.kind == 'inst' and K.sym == 'box' and T.kind in ('pin', 'title', 'cell')):
                    R.block_text(T2)
        sym = {'id': K.id, 'kind': K.kind, 'members': K.members, 'cell': K.cell or '', 'target': K.target or '',
               'box': [K.x + bx[0], K.y + bx[1], K.x + bx[2], K.y + bx[3]], 'shapes': [], 'pins': [], 'x': K.x, 'y': K.y}
        for sh in K.shapes:
            sym['shapes'].append(_shift(sh, K.x, K.y))
        for P in K.pins.values():
            esc = ESC[P.side]
            mode = 'rail' if P.name in K.rail_pins else ('gray' if P.name in K.gray_pins else 'wire')
            sym['pins'].append({'name': P.name, 'x': P.x, 'y': P.y, 'side': P.side, 'bits': P.bits, 'mode': mode, 'nets': list(P.nets)})
            cell = (P.x // G, P.y // G)
            if mode == 'rail':
                rn = K.rail_pins[P.name]
                _rail_tag(S, R, P.x, P.y, esc, rn, rn in V.sup)
                R.block.add(cell)
            elif mode == 'gray':
                gk = (P.x, P.y, K.gray_pins[P.name])
                if getattr(K, 'tg', False):  # halves of a transmission gate face each other: label sideways instead
                    esc = (1, 0) if P.rx > 0 else (-1, 0)
                if gk not in gray_done:
                    gray_done.add(gk)
                    _stub_label(S, R, P.x, P.y, esc, K.gray_pins[P.name], gray=True, bits=[K.gray_pins[P.name]])
                R.block.add(cell)
            else:
                t = Term(P.nets, P.x, P.y, esc, K, pin=P)
                terms[P.nets].append(t)
                R.pincell[t.cell] = P.nets
                R.block.discard(t.cell)
        S['symbols'].append(sym)
    # the two cells in front of a pin are reserved for that pin; a soft lane keeps room for a label
    for key, lst in terms.items():
        for t in lst:
            hard = (t.owner.id, t.pin.name) in getattr(V, 'reserve', ())
            for k in range(1, 9 if hard else 3):
                for w in ((-1, 0, 1) if hard and k > 2 else (0,)):
                    c = (t.cell[0] + t.esc[0] * k + w * abs(t.esc[1]), t.cell[1] + t.esc[1] * k + w * abs(t.esc[0]))
                    if c not in R.pincell and c not in R.block:
                        R.pincell[c] = key
            for k in range(3, 7):
                for w in (-1, 0, 1):
                    c = (t.cell[0] + t.esc[0] * k + w * abs(t.esc[1]), t.cell[1] + t.esc[1] * k + w * abs(t.esc[0]))
                    R.soft[c] = max(R.soft.get(c, 0), 25)
                    R.softnet[c] = key
    allow.update(getattr(V, 'cross_ok', ()))
    # ------------------------------------------------ routing
    comp_of = {}

    def find(t):
        while comp_of[t] is not t:
            t = comp_of[t]
        return t
    for lst in terms.values():
        for t in lst:
            comp_of[t] = t

    def join(a, b):
        ra, rb = find(a), find(b)
        if ra is not rb:
            comp_of[ra] = rb

    nowire = getattr(V, 'nowire', set())
    for lst_ in terms.values():
        for t_ in lst_:
            if t_.pin is not None and (t_.owner.id, t_.pin.name) in nowire:
                t_.nowire = True

    def port_shape(name, tup, kcls, pdir, px, py, d):
        if d == (-1, 0):
            poly = [(px - 16, py - 5), (px - 5, py - 5), (px, py), (px - 5, py + 5), (px - 16, py + 5)] if pdir == 'in' else \
                   [(px, py - 5), (px - 11, py - 5), (px - 16, py), (px - 11, py + 5), (px, py + 5)]
            T = Text(name, px - 20, py + 4, 11, 'end', '#111', bold=True, kind='port')
            box = (px - 20 - tw(name, 11), py - 8, px - 1, py + 8)
        elif d == (1, 0):
            poly = [(px, py - 5), (px + 11, py - 5), (px + 16, py), (px + 11, py + 5), (px, py + 5)] if pdir == 'out' else \
                   [(px + 16, py - 5), (px + 5, py - 5), (px, py), (px + 5, py + 5), (px + 16, py + 5)]
            T = Text(name, px + 20, py + 4, 11, 'start', '#111', bold=True, kind='port')
            box = (px + 1, py - 8, px + 20 + tw(name, 11), py + 8)
        elif d == (0, -1):
            poly = [(px - 5, py - 16), (px + 5, py - 16), (px + 5, py - 5), (px, py), (px - 5, py - 5)] if pdir == 'in' else \
                   [(px - 5, py), (px + 5, py), (px + 5, py - 11), (px, py - 16), (px - 5, py - 11)]
            T = Text(name, px, py - 20, 11, 'middle', '#111', bold=True, kind='port')
            box = (px - tw(name, 11) / 2, py - 30, px + tw(name, 11) / 2, py - 1)
        else:
            poly = [(px - 5, py + 16), (px + 5, py + 16), (px + 5, py + 5), (px, py), (px - 5, py + 5)] if pdir == 'in' else \
                   [(px - 5, py), (px + 5, py), (px + 5, py + 11), (px, py + 16), (px - 5, py + 11)]
            T = Text(name, px, py + 28, 11, 'middle', '#111', bold=True, kind='port')
            box = (px - tw(name, 11) / 2, py + 1, px + tw(name, 11) / 2, py + 30)
        S['texts'].append(T)
        R.block_rect(box[0], box[1], box[2], box[3])
        R.block_text(T)
        S['ports'].append({'name': name, 'x': px, 'y': py, 'dir': pdir, 'bits': list(tup), 'cls': kcls, 'shape': [list(q) for q in poly]})
        placed_port_boxes.append(box)

    def port_pref(kcls, pdir):
        if pdir == 'out':
            return [(1, 0)]
        if V.level == 'block' and kcls == 'hs_clock':
            return [(0, 1), (-1, 0)]
        if V.level == 'block' and kcls not in ('hs_data', 'hs_clock', 'reference'):
            return [(0, -1), (-1, 0)]
        return [(-1, 0)]

    def outward(px, py, d, name=''):
        """A port faces open space: no symbol lies just beyond it (its symbol and name, plus 60 px) in the direction it points."""
        reach = (16 + tw(name or 'xxxx', 11) + 40) if d[0] else 60
        for b in R.boxes + [tuple(q) for q in placed_port_boxes]:
            if d[0]:
                if b[1] < py + 10 and b[3] > py - 10 and ((d[0] < 0 and px - reach < b[2] and b[0] < px - 1) or (d[0] > 0 and b[0] < px + reach and b[2] > px + 1)):
                    return False
            else:
                if b[0] < px + 10 and b[2] > px - 10 and ((d[1] < 0 and py - reach < b[3] and b[1] < py - 1) or (d[1] > 0 and b[1] < py + reach and b[3] > py + 1)):
                    return False
        return True
    placed_port_boxes = []

    # ports first try to sit straight in front of a pin (60 px lead, so other pins can join the lead)
    deferred = []
    for name, tup, kcls, pdir in V.ports:
        lst = terms.get(tup, [])
        pref = port_pref(kcls, pdir)
        done = False
        cands = []
        for t in lst:
            if t.owner is None or t.nowire:
                continue
            if getattr(t.owner, 'tg', False) and t.pin is not None:
                # transmission gate: the port leaves the middle of the frame sideways, away from the gate
                d = (-1, 0) if t.pin.rx < 0 else (1, 0)
                my = t.owner.y + (20 if t.owner.mtype == 'p' else -20)
                y1 = int(my // G)
                stp = 1 if y1 > t.cell[1] else -1
                head = [(t.cell[0], yy) for yy in range(t.cell[1], y1 + stp, stp)] if y1 != t.cell[1] else [t.cell]
                cands.append((t, d, head))
            elif t.esc in pref:
                cands.append((t, t.esc, [t.cell]))
        for t, d, head in sorted(cands, key=lambda c: (pref.index(c[1]) if c[1] in pref else 9)):
            if d not in pref:
                continue
            n = 6
            st = head[-1]
            cells = head[:-1] + [(st[0] + d[0] * k, st[1] + d[1] * k) for k in range(0, n + 1)]
            if any((c in R.block or c in R.h or c in R.v or (c in R.pincell and R.pincell[c] != tup)) for c in cells[1:]):
                continue
            px, py = cells[-1][0] * G, cells[-1][1] * G
            need = tw(name, 11) + 22
            if d[0] < 0:
                box = (px - need, py - 8, px - 2, py + 8)
            elif d[0] > 0:
                box = (px + 2, py - 8, px + need, py + 8)
            elif d[1] < 0:
                box = (px - need / 2 + 8, py - 32, px + need / 2 - 8, py - 2)
            else:
                box = (px - need / 2 + 8, py + 2, px + need / 2 - 8, py + 32)
            if not R.free_rect(*box, key=tup) or not outward(px, py, d, name):
                continue
            R.add_path(tup, cells)
            pt = Term(tup, px, py, (-d[0], -d[1]), None, port=name)
            pt.wired = t.wired = True
            terms[tup].append(pt)
            comp_of[pt] = pt
            join(pt, t)
            R.pincell[pt.cell] = tup
            port_shape(name, tup, kcls, pdir, px, py, d)
            done = True
            break
        if not done:
            deferred.append((name, tup, kcls, pdir))

    # trunks: a node of a transistor stack is one horizontal line with straight drops to every device on it
    for U in units:
        if U.kind != 'cluster':
            continue
        bynet = defaultdict(list)
        for K in U.comps:
            for P in K.pins.values():
                if P.name == 'g' or P.name in K.rail_pins or P.name in K.gray_pins:
                    continue
                t = [t for t in terms[P.nets] if t.pin is P][0]
                if not t.nowire:
                    bynet[P.nets].append(t)
        for key, lst in sorted(bynet.items(), key=lambda kv: -len(kv[1])):
            if len(lst) < 2:
                continue
            ys = sorted(set(t.y + t.esc[1] * 30 for t in lst))
            lev = defaultdict(list)
            for t in lst:
                lev[t.y + t.esc[1] * 30].append(t)
            for ty, tl in lev.items():
                if len(tl) < 2:
                    continue
                xs = sorted(set(t.x for t in tl))
                ok = True
                for t in tl:
                    if not R.straight_free(key, t.cell, (t.x // G, ty // G)) and (t.x // G, ty // G) not in R.cells[key]:
                        ok = False
                if len(xs) > 1 and not R.straight_free(key, (xs[0] // G - 1, ty // G), (xs[-1] // G + 1, ty // G)):
                    ok = False
                if not ok:
                    continue
                both = [x for x in xs[1:-1] if len(set(t.esc[1] for t in tl if t.x == x)) == 2]
                if both:
                    continue                      # a through column inside the trunk would make a 4-way point: route normally
                for t in tl:
                    c0, c1 = t.cell, (t.x // G, ty // G)
                    d = (0, 1 if c1[1] > c0[1] else -1)
                    path, c = [c0], c0
                    while c != c1:
                        c = (c[0] + d[0], c[1] + d[1])
                        path.append(c)
                    R.add_path(key, path)
                    t.wired = True
                if len(xs) > 1:
                    R.add_path(key, [(gx, ty // G) for gx in range(xs[0] // G, xs[-1] // G + 1)])
                for t in tl[1:]:
                    join(t, tl[0])
    # phase A: straight lines between facing terminals, shortest first
    cands = []
    for key, lst in terms.items():
        for i, a in enumerate(lst):
            for b in lst[i + 1:]:
                if a.x == b.x and a.y != b.y:
                    d = (0, 1 if b.y > a.y else -1)
                elif a.y == b.y and a.x != b.x:
                    d = (1 if b.x > a.x else -1, 0)
                else:
                    continue
                if a.esc == d and b.esc == (-d[0], -d[1]):
                    cands.append((abs(a.x - b.x) + abs(a.y - b.y), len(cands), key, a, b, d))
    cands.sort(key=lambda t: t[:2])
    for dist, _, key, a, b, d in cands:
        if find(a) is find(b) or a.wired or b.wired or a.nowire or b.nowire:
            continue
        between = [(a.cell[0] + d[0] * k, a.cell[1] + d[1] * k) for k in range(1, max(abs(a.cell[0] - b.cell[0]), abs(a.cell[1] - b.cell[1])))]
        if any(c in R.cells[key] for c in between):
            continue
        if R.straight_free(key, a.cell, b.cell):
            path = [a.cell]
            c = a.cell
            while c != b.cell:
                c = (c[0] + d[0], c[1] + d[1])
                path.append(c)
            R.add_path(key, path)
            a.wired = b.wired = True
            join(a, b)

    # phase B: the rest. Nodes of transistor stacks first, then data, clock, control; small nets first
    def prio(kv):
        key, lst = kv
        chan = any(t.owner is not None and t.owner.kind != 'inst' and t.pin.name != 'g' for t in lst)
        c = V.netcls.get(key[0], 'other')
        return (2 if key in fb else (0 if chan else 1), {'hs_data': 0, 'hs_clock': 1, 'reference': 2}.get(c, 3), len(lst), _span(lst))
    for key, lst in sorted(terms.items(), key=prio):
        if len(lst) < 2:
            continue
        progress = True
        while progress:
            progress = False
            groups = defaultdict(list)
            for t in lst:
                groups[find(t)].append(t)
            if len(groups) <= 1:
                break
            for g in sorted(groups.values(), key=lambda g: (len(g), _span(g))):
                myroot = find(g[0])
                mycells = _comp_cells(R, key, g)
                goals = {}
                for c in R.cells[key]:
                    if c not in mycells:
                        goals[c] = None
                for t in lst:
                    if t.nowire:
                        goals.pop(t.cell, None)
                    elif find(t) is not myroot and not t.wired:
                        goals[t.cell] = {(-t.esc[0], -t.esc[1])}
                    elif find(t) is not myroot:
                        goals.pop(t.cell, None)
                best = None
                for t in g:
                    if t.wired or t.nowire:
                        continue
                    p = R.route(key, t.cell, t.esc, goals)
                    if p is not None:
                        best = (t, p)
                        break
                if not goals:
                    continue
                if best is None and all(t.wired for t in g) and mycells:
                    p = _branch(R, key, mycells, goals)
                    if p is not None:
                        best = (g[0], p)
                if best is None:
                    continue
                t, p = best
                man = abs(p[0][0] - p[-1][0]) + abs(p[0][1] - p[-1][1])
                if key not in fb and len(p) - 1 > 1.5 * man and len(p) - 1 - man >= 8:
                    continue                      # a detour (more than 1.5 x the direct distance): labels are clearer
                R.add_path(key, p)
                t.wired = True
                end = p[-1]
                hit = [u for u in lst if u.cell == end]
                if hit:
                    hit[0].wired = True
                    join(t, hit[0])
                else:
                    for r2, g2 in groups.items():
                        if r2 is not myroot and end in _comp_cells(R, key, g2):
                            join(t, g2[0])
                            break
                progress = True
                break
    # ------------------------------------------------ remaining ports: attached to the finished wires, never loose
    for name, tup, kcls, pdir in deferred:
        lst = terms.get(tup, [])
        if not lst:
            continue
        groups = defaultdict(list)
        for t in lst:
            groups[find(t)].append(t)
        pref = port_pref(kcls, pdir)
        got = None
        allp = pref + [d for d in DIRS if d not in pref]
        # facing outward first (preferred side, then any side); only if there is no such place, anywhere
        okp = lambda x, y, d, _n=name: outward(x, y, d, _n)
        for pr, strict, ok in ((pref, True, okp), (pref, False, okp), (allp, False, okp), (pref, False, None)):
            for g in sorted(groups.values(), key=lambda g: -len(g)):
                got = _attach(R, tup, g, _comp_cells(R, tup, g), pr, name, port=True, strict=strict, ok=ok)
                if got:
                    break
            if got:
                break
        if not got:
            S.setdefault('problems', []).append('port %s: no room' % name)
            continue
        (x0, y0), (px, py), d, t0, path = got
        if path:
            R.add_path(tup, path)
        if t0 is not None:
            t0.wired = True
        pt = Term(tup, px, py, (-d[0], -d[1]), None, port=name)
        pt.wired = True
        terms[tup].append(pt)
        comp_of[pt] = pt
        join(pt, g[0])
        R.pincell[pt.cell] = tup
        port_shape(name, tup, kcls, pdir, px, py, d)
    # ------------------------------------------------ labels for what is not joined by wires
    for key, lst in terms.items():
        groups = defaultdict(list)
        for t in lst:
            groups[find(t)].append(t)
        name = bus_label(key)
        if all(AUTO.match(x) for x in key):
            # an auto-generated net name says nothing: name the label after the block pin that drives it
            drv_ = [t for t in lst if t.pin is not None and t.owner.kind == 'inst' and t.pin.dir == 'out' and len(t.owner.members) == 1]
            if drv_:
                name = '%s.%s' % (drv_[0].owner.id, drv_[0].pin.name)
        if len(groups) == 1 and (len(lst) > 1 or lst[0].port):
            continue
        for r, g in groups.items():
            if any(t.port for t in g):
                continue                      # the port names this part of the net
            got = _attach(R, key, g, _comp_cells(R, key, g), [(-1, 0), (1, 0), (0, -1), (0, 1)], name, port=False, strict=False)
            if not got:
                t = g[0]
                S.setdefault('problems', []).append('label %s: no room' % name)
                for u in g:
                    if u.pin is not None:
                        S.setdefault('problem_pins', []).append((u.owner.id, u.pin.name))
                S['labels'].append({'text': name, 'x': t.x, 'y': t.y, 'ax': t.x, 'ay': t.y, 'gray': False, 'bits': list(key), 'seg': None})
                S['texts'].append(Text(name, t.x + 3, t.y - 4, 9, 'start', '#0a6d3a', kind='label'))
                continue
            (x0, y0), (px, py), d, t0, path = got[:5]
            if path:
                R.add_path(key, path)
            if t0 is not None:
                t0.wired = True
            if d[0] < 0:
                T = Text(name, px - 3, py + 3, 9, 'end', '#0a6d3a', kind='label')
            elif d[0] > 0:
                T = Text(name, px + 3, py + 3, 9, 'start', '#0a6d3a', kind='label')
            elif d[1] < 0:
                T = Text(name, px, py - 4, 9, 'middle', '#0a6d3a', kind='label')
            else:
                T = Text(name, px, py + 10, 9, 'middle', '#0a6d3a', kind='label')
            S['texts'].append(T)
            R.block_text(T)
            S['labels'].append({'text': name, 'x': px, 'y': py, 'ax': px, 'ay': py, 'gray': False, 'bits': list(key), 'seg': None})
    # ------------------------------------------------ wires, dots, bus marks
    for key, paths in R.paths.items():
        segs = []
        for p in paths:
            segs += segments(p)
        S['wires'].append({'net': list(key), 'segs': segs, 'bus': len(key)})
        seen = set()
        for c in R.cells[key]:
            if bin(R.arms[(key, c)]).count('1') >= 3:
                S['dots'].append([c[0] * G, c[1] * G])
        if len(key) > 1:
            best = max(segs, key=lambda s: abs(s[0] - s[2]) + abs(s[1] - s[3]))
            if abs(best[0] - best[2]) + abs(best[1] - best[3]) >= 20:
                mx, my = snap((best[0] + best[2]) / 2.0), snap((best[1] + best[3]) / 2.0)
                S['slashes'].append([mx, my, 'h' if best[1] == best[3] else 'v'])
    if R.fourway and __import__('os').environ.get('HD_DEBUG'):
        print('4way', V.id, R.fourway[:3])
    # humps: where a feedback wire crosses another wire, the feedback wire jumps over it
    S['humps'] = []
    for c, hn in R.h.items():
        vn = R.v.get(c)
        if vn is not None and vn != hn and (hn in fb or vn in fb):
            S['humps'].append([c[0] * G, c[1] * G, 'h' if hn in fb else 'v'])
    S['humps'].sort()
    S['feedback'] = sorted(list(k) for k in fb)
    S['has_mos'] = any(K.kind == 'mos' for K in comps)
    S['_cross'] = list(getattr(V, 'cross_ok', ()))
    # which pins hang on a label (not on the wire of the net's largest group)
    S['_labelled'] = []
    for key, lst in terms.items():
        groups = defaultdict(list)
        for t in lst:
            groups[find(t)].append(t)
        if len(groups) < 2:
            continue
        main = max(groups.values(), key=len)
        for g in groups.values():
            if g is not main:
                S['_labelled'] += [(t.owner.id, t.pin.name, key) for t in g if t.pin is not None]
        S['_split'] = S.get('_split', []) + [key]
    _normalise(S)
    S['legend'] = list(V.legend)
    S['omitted'] = list(V.omitted)
    return S


def _span(lst):
    return (max(t.x for t in lst) - min(t.x for t in lst)) + (max(t.y for t in lst) - min(t.y for t in lst))


def _comp_cells(R, key, group):
    """Wire cells connected to the terminals of one component."""
    start = [t.cell for t in group]
    seen, fr = set(), [c for c in start if c in R.cells[key]]
    seen.update(fr)
    while fr:
        c = fr.pop()
        a = R.arms[(key, c)]
        for d in DIRS:
            if a & BIT[d]:
                b = (c[0] + d[0], c[1] + d[1])
                if b in R.cells[key] and b not in seen:
                    seen.add(b)
                    fr.append(b)
    return seen


def _attach(R, key, group, cells, pref, name, port, strict, ok=None):
    """Find where a port or a net label can hang on a component: a 2-cell lead out of an unwired pin,
    or a branch off one of its wires. Returns ((x0,y0), (x1,y1), dir, terminal|None, cell path) or None."""
    need = tw(name, 11 if port else 9) + (22 if port else 6)
    half = tw(name, 11 if port else 9) / 2.0 + 2

    def fits(c, d):
        path = [c]
        for n in range(1, 6):
            q = (c[0] + n * d[0], c[1] + n * d[1])
            if q in R.block or q in R.h or q in R.v or (q in R.pincell and R.pincell[q] != key):
                return None
            path.append(q)
            if n < 2:
                continue
            x, y = q[0] * G, q[1] * G
            if d[0] < 0:
                box = (x - need, y - 8, x - 2, y + 8)
            elif d[0] > 0:
                box = (x + 2, y - 8, x + need, y + 8)
            elif d[1] < 0:
                box = (x - half, y - (32 if port else 14), x + half, y - 2)
            else:
                box = (x - half, y + 2, x + half, y + (32 if port else 14))
            if R.free_rect(*box, key=key) and (ok is None or ok(x, y, d)):
                return list(path)
        return None
    cand = []
    for t in group:
        if not t.wired and t.pin is not None:
            cand.append((0 if t.esc in pref else 1, t.cell, t.esc, t))
    for c in sorted(cells):
        a = R.arms[(key, c)]
        n = bin(a).count('1')
        if n >= 3 or (c in R.pincell and n < 2 and any(t.cell == c for t in group)):
            continue
        for d in DIRS:
            if a & BIT[d]:
                continue
            cand.append((0 if d in pref else 1, c, d, None))
    side = pref[0]
    cand.sort(key=lambda t: (t[0], 0 if t[3] is not None else 1, t[1][0] * side[0] * -1 + t[1][1] * side[1] * -1))
    for rank, c, d, t in cand:
        if strict and rank:
            break
        p = fits(c, d)
        if p:
            return ((c[0] * G, c[1] * G), (p[-1][0] * G, p[-1][1] * G), d, t, p)
    return None


def _branch(R, key, mycells, goals):
    """Cleanest branch from an existing wire of the component to the goals."""
    best = None
    for c in sorted(mycells):
        a = R.arms[(key, c)]
        if bin(a).count('1') >= 3:
            continue
        for d in DIRS:
            if a & BIT[d]:
                continue
            p = R.route(key, c, d, goals, limit=4000)
            if p is not None:
                cost = len(p) + 40 * (len(segments(p)) - 1)
                if best is None or cost < best[0]:
                    best = (cost, p)
    return best[1] if best else None


def _shift(sh, dx, dy):
    k = sh[0]
    if k == 'line':
        return ['line', sh[1] + dx, sh[2] + dy, sh[3] + dx, sh[4] + dy]
    if k == 'rect':
        return ['rect', sh[1] + dx, sh[2] + dy, sh[3], sh[4]]
    if k == 'circle':
        return ['circle', sh[1] + dx, sh[2] + dy, sh[3]]
    return [k, [[x + dx, y + dy] for x, y in sh[1]]]


def _rail_tag(S, R, x, y, esc, net, is_sup):
    ex, ey = esc
    sh = []
    if ey != 0:
        y1 = y + ey * 8
        sh.append(['line', x, y, x, y1])
        if is_sup:
            sh.append(['line', x - 8, y1, x + 8, y1])
            T = Text(net, x, y1 - 3 if ey < 0 else y1 + 10, 8, 'middle', '#b03030', kind='rail')
        else:
            sh += [['line', x - 8, y1, x + 8, y1], ['line', x - 5, y1 + ey * 3, x + 5, y1 + ey * 3], ['line', x - 2, y1 + ey * 6, x + 2, y1 + ey * 6]]
            T = Text(net, x + 11, y1 + (6 if ey > 0 else -2), 8, 'start', '#30508a', kind='rail')
    else:
        x1 = x + ex * 8
        sh.append(['line', x, y, x1, y])
        sh.append(['line', x1, y - 8, x1, y + 8])
        T = Text(net, x1 + ex * 3, y + 3, 8, 'start' if ex > 0 else 'end', '#b03030' if is_sup else '#30508a', kind='rail')
    S['tags'].append({'x': x, 'y': y, 'net': net, 'shapes': sh})
    S['texts'].append(T)
    R.block_text(T)
    R.block_rect(min(x, x + ex * 14) - 8 * abs(ey), min(y, y + ey * 14) - 8 * abs(ex), max(x, x + ex * 14) + 8 * abs(ey), max(y, y + ey * 14) + 8 * abs(ex))


def _stub_label(S, R, x, y, esc, name, gray, bits, net=None, router=None, as_wire=False):
    """Short lead out of a pin ending in a net name."""
    ex, ey = esc
    ln = 20 if not gray else 10
    x1, y1 = x + ex * ln, y + ey * ln
    col = '#888' if gray else '#0a6d3a'
    if ex < 0:
        T = Text(name, x1 - 3, y1 + 3, 9, 'end', col, kind='label')
    elif ex > 0:
        T = Text(name, x1 + 3, y1 + 3, 9, 'start', col, kind='label')
    elif ey < 0:
        T = Text(name, x1, y1 - 4, 9, 'middle', col, kind='label')
    else:
        T = Text(name, x1, y1 + 10, 9, 'middle', col, kind='label')
    S['texts'].append(T)
    S['labels'].append({'text': name, 'x': x1, 'y': y1, 'ax': x, 'ay': y, 'gray': gray, 'bits': bits,
                        'seg': [x, y, x1, y1]})
    R.block_text(T)
    c = (x // G, y // G)
    for k in range(1, ln // G + 1):
        R.block.add((c[0] + ex * k, c[1] + ey * k))


def _normalise(S):
    """Shift everything so that the drawing starts at (40, 40); set the canvas size."""
    xs, ys = [], []
    for sym in S['symbols']:
        xs += [sym['box'][0], sym['box'][2]]
        ys += [sym['box'][1], sym['box'][3]]
        for p in sym['pins']:
            xs.append(p['x'])
            ys.append(p['y'])
    for w in S['wires']:
        for s in w['segs']:
            xs += [s[0], s[2]]
            ys += [s[1], s[3]]
    for T in S['texts']:
        b = T.bbox()
        xs += [b[0], b[2]]
        ys += [b[1], b[3]]
    for p in S['ports']:
        xs.append(p['x'])
        ys.append(p['y'])
    dx = 40 - snap(min(xs)) if xs else 0
    dy = 40 - snap(min(ys)) if ys else 0
    dx, dy = snap(dx), snap(dy)

    def sh(v):
        k = v[0]
        if k == 'line':
            return ['line', v[1] + dx, v[2] + dy, v[3] + dx, v[4] + dy]
        if k == 'rect':
            return ['rect', v[1] + dx, v[2] + dy, v[3], v[4]]
        if k == 'circle':
            return ['circle', v[1] + dx, v[2] + dy, v[3]]
        return [k, [[x + dx, y + dy] for x, y in v[1]]]
    for sym in S['symbols']:
        sym['box'] = [sym['box'][0] + dx, sym['box'][1] + dy, sym['box'][2] + dx, sym['box'][3] + dy]
        sym['shapes'] = [sh(v) for v in sym['shapes']]
        for p in sym['pins']:
            p['x'] += dx
            p['y'] += dy
    for w in S['wires']:
        w['segs'] = [[s[0] + dx, s[1] + dy, s[2] + dx, s[3] + dy] for s in w['segs']]
    S['dots'] = [[x + dx, y + dy] for x, y in S['dots']]
    S['humps'] = [[x + dx, y + dy, o] for x, y, o in S.get('humps', [])]
    S['slashes'] = [[x + dx, y + dy, o] for x, y, o in S['slashes']]
    for l in S['labels']:
        for k in ('x', 'ax'):
            l[k] += dx
        for k in ('y', 'ay'):
            l[k] += dy
        if l.get('seg'):
            l['seg'] = [l['seg'][0] + dx, l['seg'][1] + dy, l['seg'][2] + dx, l['seg'][3] + dy]
    for p in S['ports']:
        p['x'] += dx
        p['y'] += dy
        p['shape'] = [[x + dx, y + dy] for x, y in p['shape']]
    for t in S['tags']:
        t['x'] += dx
        t['y'] += dy
        t['shapes'] = [sh(v) for v in t['shapes']]
    texts = []
    for T in S['texts']:
        T.x += dx
        T.y += dy
        b = T.bbox()
        texts.append({'s': T.s, 'x': T.x, 'y': T.y, 'size': T.size, 'anchor': T.anchor, 'color': T.color, 'italic': T.italic,
                      'bold': T.bold, 'kind': T.kind, 'bbox': [round(v, 1) for v in b], 'owner': getattr(T, 'owner', '')})
    S['texts'] = texts
    S['w'] = snap(max(xs) + dx + 60) if xs else 200
    S['h'] = snap(max(ys) + dy + 60) if ys else 200
