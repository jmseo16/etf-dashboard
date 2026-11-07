"""Grid maze router (A*) for orthogonal schematic wiring.

Rules that keep the drawing electrically unambiguous:
  * a wire never runs collinear on top of another net's wire,
  * a wire may cross another net only perpendicularly, going straight through
    (no bend, no endpoint, no junction at a crossing),
  * a wire never touches another net's pin or junction,
  * a wire never enters a symbol keep-out area,
  * a wire leaves / enters a pin along the pin's lead direction,
  * no 4-way junctions.
All coordinates handed to the router are in pixels and must lie on the grid.
"""
from __future__ import annotations

import heapq

DIRS = {"R": (1, 0), "L": (-1, 0), "D": (0, 1), "U": (0, -1)}
OPP = {"R": "L", "L": "R", "U": "D", "D": "U"}
ORI = {"R": "h", "L": "h", "U": "v", "D": "v"}

STEP, BEND, CROSS, NEAR_PIN = 1.0, 6.0, 14.0, 12.0


class RouteError(Exception):
    pass


class Router:
    def __init__(self, bounds, g=10):
        self.g = g
        x0, y0, x1, y1 = bounds
        self.x0, self.y0 = int(x0 // g), int(y0 // g)
        self.x1, self.y1 = int(-(-x1 // g)), int(-(-y1 // g))
        self.hard = set()
        self.soft = {}
        self.wire = {}        # cell -> {net: set(ori)}
        self.node = {}        # cell -> net (pins, bends, junctions, endpoints)
        self.pins = {}        # cell -> (net, dir)
        self.edges = {}       # net -> set(frozenset(a,b))
        self.tree = {}        # net -> set(cells)

    # ---------------- setup ----------------
    def c(self, x, y):
        return (int(round(x / self.g)), int(round(y / self.g)))

    def block_rect(self, x0, y0, x1, y1):
        cx0, cy0 = int(-(-x0 // self.g)), int(-(-y0 // self.g))
        cx1, cy1 = int(x1 // self.g), int(y1 // self.g)
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                self.hard.add((cx, cy))

    def soft_rect(self, x0, y0, x1, y1, cost):
        cx0, cy0 = int(x0 // self.g), int(y0 // self.g)
        cx1, cy1 = int(-(-x1 // self.g)), int(-(-y1 // self.g))
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                self.soft[(cx, cy)] = self.soft.get((cx, cy), 0) + cost

    def add_pin(self, net, x, y, d):
        cell = self.c(x, y)
        self.pins[cell] = (net, d)
        self.node[cell] = net
        self.hard.discard(cell)
        # keep the cell right in front of a pin attractive only for its own net
        dx, dy = DIRS[d]
        front = (cell[0] + dx, cell[1] + dy)
        self.soft.setdefault(("pinfront", front), net)

    def add_fixed_wire(self, net, pts):
        """Register a pre-drawn polyline (e.g. a rail or a stub) for `net`."""
        cells = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            a, b = self.c(xa, ya), self.c(xb, yb)
            cells += _line_cells(a, b)
        self._commit(net, _dedup(cells), fixed=True)

    def try_fixed(self, net, polylines):
        """Commit a planned set of orthogonal polylines for `net` only if every cell
        obeys the routing rules (no overlap, crossings only straight-through, no
        4-way junction, no foreign pins/nodes). Returns True if committed."""
        edges = []
        for pts in polylines:
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                cells = _line_cells(self.c(xa, ya), self.c(xb, yb))
                edges += [(a, b) for a, b in zip(cells, cells[1:])]
        ori, deg = {}, {}
        for a, b in edges:
            o = "h" if a[1] == b[1] else "v"
            for c in (a, b):
                ori.setdefault(c, set()).add(o)
                deg[c] = deg.get(c, 0) + 1
        for c in ori:
            own_pin = c in self.pins and self.pins[c][0] == net
            if c in self.pins and not own_pin:
                return False
            if own_pin:
                if deg[c] + self._deg(net, c) > 3:
                    return False
                continue
            if c in self.hard:
                return False
            nn = self.node.get(c)
            if nn is not None and nn != net:
                return False
            if deg[c] + self._deg(net, c) >= 4:
                return False
            fw = self._foreign_wire(c, net)
            is_node = len(ori[c]) > 1 or deg[c] != 2
            if fw and (is_node or len(fw) > 1 or (ori[c] & fw)):
                return False
        for pts in polylines:
            cells = []
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                cells += _line_cells(self.c(xa, ya), self.c(xb, yb))
            self._commit(net, _dedup(cells))
        return True

    def tree_add_pin(self, net, x, y):
        self.tree.setdefault(net, set()).add(self.c(x, y))

    # ---------------- query helpers ----------------
    def _foreign_wire(self, cell, net):
        w = self.wire.get(cell)
        if not w:
            return None
        oris = set()
        for n, o in w.items():
            if n != net:
                oris |= o
        return oris or None

    def _deg(self, net, cell):
        d = 0
        for e in self.edges.get(net, ()):
            if cell in e:
                d += 1
        if cell in self.pins and self.pins[cell][0] == net:
            d += 1  # the symbol lead counts as one branch
        return d

    # ---------------- routing ----------------
    def route_net(self, net, pins):
        """pins: [(x, y, dir)]. Connects all of them into one tree."""
        pcells = [(self.c(x, y), d) for x, y, d in pins]
        tree = self.tree.setdefault(net, set())
        remaining = list(pcells)
        if not tree:
            first = remaining.pop(0)
            tree.add(first[0])
        # route nearest pin first
        failures = []
        while remaining:
            remaining.sort(key=lambda pc: min(abs(pc[0][0] - t[0]) + abs(pc[0][1] - t[1]) for t in tree))
            cell, d = remaining.pop(0)
            if cell in tree:
                continue
            path = self._astar(net, cell, d, tree)
            if path is None:
                failures.append(cell)
                continue
            self._commit(net, path)
        return [(x * self.g, y * self.g) for x, y in failures]

    def _astar(self, net, start, sdir, tree):
        if not tree:
            return None
        tx0 = min(t[0] for t in tree); tx1 = max(t[0] for t in tree)
        ty0 = min(t[1] for t in tree); ty1 = max(t[1] for t in tree)

        def h(c):
            dx = max(tx0 - c[0], 0, c[0] - tx1)
            dy = max(ty0 - c[1], 0, c[1] - ty1)
            return dx + dy

        # first step is forced along the pin direction
        dx, dy = DIRS[sdir]
        first = (start[0] + dx, start[1] + dy)
        ok, crossing = self._can_enter(net, first, sdir, tree)
        if not ok:
            return None
        if self._is_target(net, first, sdir, tree):
            return [start, first]
        g0 = STEP + (CROSS if crossing else 0) + self._soft(net, first)
        openh = [(g0 + h(first), g0, first, sdir, crossing)]
        best = {(first, sdir): g0}
        parent = {(first, sdir): (start, None)}
        limit = 60000
        while openh and limit:
            limit -= 1
            f, g, cell, d, crossing = heapq.heappop(openh)
            if best.get((cell, d), 1e18) < g - 1e-9:
                continue
            for nd in ("R", "L", "U", "D"):
                if nd == OPP[d]:
                    continue
                if crossing and nd != d:
                    continue  # no bends on a crossing cell
                bend = nd != d
                if bend and self._foreign_wire(cell, net):
                    continue
                ddx, ddy = DIRS[nd]
                nxt = (cell[0] + ddx, cell[1] + ddy)
                if not (self.x0 - 2 <= nxt[0] <= self.x1 + 2 and self.y0 - 2 <= nxt[1] <= self.y1 + 2):
                    continue
                ok, ncross = self._can_enter(net, nxt, nd, tree)
                if not ok:
                    continue
                ng = g + STEP + (BEND if bend else 0) + (CROSS if ncross else 0) + self._soft(net, nxt)
                if self._is_target(net, nxt, nd, tree):
                    if bend and self._foreign_wire(cell, net):
                        continue
                    parent[(nxt, nd)] = (cell, d)
                    return self._rebuild(parent, (nxt, nd))
                key = (nxt, nd)
                if ng < best.get(key, 1e18) - 1e-9:
                    best[key] = ng
                    parent[key] = (cell, d)
                    heapq.heappush(openh, (ng + h(nxt), ng, nxt, nd, ncross))
        return None

    def _rebuild(self, parent, key):
        cells = [key[0]]
        while key in parent:
            prev = parent[key]
            cells.append(prev[0])
            if prev[1] is None:
                break
            key = prev
        return cells[::-1]

    def _soft(self, net, cell):
        s = self.soft.get(cell, 0)
        pf = self.soft.get(("pinfront", cell))
        if pf is not None and pf != net:
            s += NEAR_PIN
        return s

    def _can_enter(self, net, cell, d, tree):
        """Can a wire of `net` moving in direction d step into `cell`?
        returns (ok, is_crossing)"""
        if cell in self.pins:
            pnet, pdir = self.pins[cell]
            if pnet != net:
                return False, False
            # own pin: only as target and only along its lead
            return (cell in tree and d == OPP[pdir]), False
        if cell in self.hard:
            return False, False
        nn = self.node.get(cell)
        if nn is not None and nn != net:
            return False, False
        fw = self._foreign_wire(cell, net)
        if fw:
            if ORI[d] in fw or len(fw) > 1:
                return False, False
            if cell in tree:
                return False, False
            return True, True
        return True, False

    def _is_target(self, net, cell, d, tree):
        if cell not in tree:
            return False
        if self._foreign_wire(cell, net):
            return False
        if cell in self.pins:
            return self.pins[cell][0] == net and d == OPP[self.pins[cell][1]]
        if self._deg(net, cell) >= 3:
            return False
        # arriving collinear into the middle of a wire would overlap it
        own = self.wire.get(cell, {}).get(net, set())
        if own == {ORI[d]} and self._deg(net, cell) >= 2:
            return False
        return True

    def _commit(self, net, cells, fixed=False):
        es = self.edges.setdefault(net, set())
        tree = self.tree.setdefault(net, set())
        for a, b in zip(cells, cells[1:]):
            es.add(frozenset((a, b)))
            o = "h" if a[1] == b[1] else "v"
            for c in (a, b):
                self.wire.setdefault(c, {}).setdefault(net, set()).add(o)
        for c in cells:
            tree.add(c)
            oris = self.wire.get(c, {}).get(net, set())
            if len(oris) > 1 or self._deg(net, c) != 2 or c in self.pins:
                self.node[c] = net
        if cells:
            self.node[cells[0]] = net
            self.node[cells[-1]] = net

    # ---------------- output ----------------
    def segments(self, net):
        """Merge unit edges into maximal straight segments (pixel coords)."""
        es = self.edges.get(net, set())
        hs, vs = {}, {}
        for e in es:
            a, b = sorted(e)
            if a[1] == b[1]:
                hs.setdefault(a[1], []).append(a[0])
            else:
                vs.setdefault(a[0], []).append(a[1])
        segs = []
        for y, xs in hs.items():
            for s, t in _runs(sorted(set(xs))):
                segs.append((s * self.g, y * self.g, (t + 1) * self.g, y * self.g))
        for x, ys in vs.items():
            for s, t in _runs(sorted(set(ys))):
                segs.append((x * self.g, s * self.g, x * self.g, (t + 1) * self.g))
        return segs

    def junctions(self, net):
        out = []
        cells = set()
        for e in self.edges.get(net, ()):
            cells |= e
        for c in cells:
            if self._deg(net, c) >= 3:
                out.append((c[0] * self.g, c[1] * self.g))
        return out


def _runs(sorted_starts):
    """[0,1,2,5,6] -> [(0,2),(5,6)] (unit edge start indices)"""
    if not sorted_starts:
        return []
    out, s, p = [], sorted_starts[0], sorted_starts[0]
    for v in sorted_starts[1:]:
        if v == p + 1:
            p = v
            continue
        out.append((s, p))
        s = p = v
    out.append((s, p))
    return out


def _line_cells(a, b):
    (x0, y0), (x1, y1) = a, b
    if x0 == x1:
        step = 1 if y1 >= y0 else -1
        return [(x0, y) for y in range(y0, y1 + step, step)]
    if y0 == y1:
        step = 1 if x1 >= x0 else -1
        return [(x, y0) for x in range(x0, x1 + step, step)]
    raise RouteError("fixed wires must be orthogonal")


def _dedup(cells):
    out = []
    for c in cells:
        if not out or out[-1] != c:
            out.append(c)
    return out
