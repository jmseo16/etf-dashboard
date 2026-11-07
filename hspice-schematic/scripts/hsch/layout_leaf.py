"""Transistor-level placement + routing (Razavi textbook style).

Placement idea
  * every channel element (MOS D-S, R, C, L, sources) is "vertical" between a lower
    and an upper net; nets get a height rank by longest path from ground
    (supply on top, ground at the bottom, PMOS above NMOS falls out naturally);
  * devices form a tree that grows from the rail with the fewest connections
    (normally the tail current source) - children of a net are the devices that
    stack on it.  A Reingold-Tilford-style packing puts series devices in one
    column and centres a tail device under the branches it feeds;
  * differential symmetry (INP/INN, OUTP/OUTN, ... propagated through matched
    devices) decides gate facing: input pairs face out, cross-coupled / shared-gate
    pairs face in;
  * passives between two nets of the same rank (source degeneration) are drawn
    horizontally between the columns.
"""
from __future__ import annotations

from .analyze import diff_partner, is_ground, is_supply, pin_map
from .geom import (VPIN_LEN, Xf, capacitor, eng, generic_box, ground_glyph, inductor, mos, resistor,
                   source, transform, vdd_glyph, vpin_body_rect)
from .parser import parse_value
from .router import Router

RP = 120     # vertical pitch between net ranks
GAP = 20     # minimum horizontal clearance between columns
HGAP = 110   # clearance needed to fit a horizontal passive between two columns
CHAR = 5.6   # label character width estimate (px)


def _r10(v):
    return int(-(-v // 10) * 10)


def _snap(v):
    return int(round(v / 10.0)) * 10


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
def wl_text(d):
    p = d["params"]
    w, l = parse_value(p.get("w")), parse_value(p.get("l"))
    wl = f"{eng(w)}/{eng(l)}" if (w is not None and l is not None) else f"{p.get('w', '?')}/{p.get('l', '?')}"
    m = p.get("m", p.get("mult", "1"))
    mv = parse_value(m)
    return wl, f"m={eng(mv) if mv is not None else m}"


def val_text(d):
    p = d["params"]
    key = {"R": "r", "C": "c", "L": "l"}.get(d["kind"])
    raw = p.get(key) if key else p.get("value")
    v = parse_value(raw)
    unit = {"R": "Ω", "C": "F", "L": "H"}.get(d["kind"], "")
    if v is None:
        return str(raw or "")
    return eng(v) + unit


# ---------------------------------------------------------------------------
class Node:
    __slots__ = ("dev", "children", "band", "lext", "rext", "rel", "x", "cont", "nets", "order", "mirror")

    def __init__(self, dev):
        self.dev, self.children = dev, []
        self.band = 0
        self.lext = self.rext = 20
        self.rel = self.x = 0
        self.cont = (0, 0)
        self.nets = set()
        self.order = 0
        self.mirror = False


def layout_leaf(cell, roles, title=None):
    devs = [d for d in cell["devices"]]
    ports = cell["ports"]
    pm = {d["name"]: pin_map(d) for d in devs}

    # ---------------- rails ----------------
    all_nets = []
    for d in devs:
        for p, n in d["pins"]:
            if n not in all_nets:
                all_nets.append(n)
    supplies = [n for n in ports if is_supply(n)] + [n for n in all_nets if is_supply(n) and n not in ports]
    grounds = [n for n in ports if is_ground(n)] + [n for n in all_nets if is_ground(n) and n not in ports]
    sup = supplies[0] if supplies else None
    gnd = grounds[0] if grounds else None

    # ---------------- orientation ----------------
    vert = {}       # dev name -> (lo_net, up_net, lo_pin, up_pin)
    horiz = []      # passives between same-rank nets (decided after ranking)
    other = []      # generic boxes
    two_term = []
    for d in devs:
        P = pm[d["name"]]
        k = d["kind"]
        if k == "M":
            lp, up = ("s", "d") if d["type"] == "nmos" else ("d", "s")
            if is_ground(P[up]) or is_supply(P[lp]):
                lp, up = up, lp
            vert[d["name"]] = (P[lp], P[up], lp, up)
        elif k == "Q":
            vert[d["name"]] = (P["e"], P["c"], "e", "c")
        elif k == "D":
            vert[d["name"]] = (P["k"], P["a"], "k", "a")
        elif k in "RCLVI":
            a, b = P["p"], P["n"]
            if is_ground(a) or is_supply(b):
                vert[d["name"]] = (a, b, "p", "n")
            elif is_ground(b) or is_supply(a):
                vert[d["name"]] = (b, a, "n", "p")
            else:
                two_term.append(d)
        else:
            other.append(d)

    # ---------------- ranks (longest path from ground) ----------------
    h = {g: 0 for g in grounds}
    edges = [(lo, up) for lo, up, _, _ in vert.values()]
    for _ in range(len(all_nets) + 2):
        changed = False
        for lo, up in edges:
            if lo in h and not is_supply(up) and up not in grounds:
                if h.get(up, -1) < h[lo] + 1:
                    h[up] = h[lo] + 1
                    changed = True
        if not changed:
            break
    top = max([h[lo] + 1 for lo, up in edges if is_supply(up) and lo in h] + [max(h.values(), default=0) + 1])
    for s in supplies:
        h[s] = top
    # nets only reachable from the supply side: ALAP from the top
    for _ in range(len(all_nets) + 2):
        changed = False
        for lo, up in edges:
            if up in h and lo not in h:
                h[lo] = h[up] - 1
                changed = True
        if not changed:
            break
    low = min([v for n, v in h.items() if n not in grounds] + [1])
    if low < 1:
        for n in h:
            if n not in grounds:
                h[n] += 1 - low
        top = max(h.values())
    for s in supplies:
        h[s] = top

    # passives between internal nets: vertical if ranks differ, else horizontal
    for d in two_term:
        a, b = pm[d["name"]]["p"], pm[d["name"]]["n"]
        if a in h and b in h and h[a] != h[b]:
            lo, up, lp, upn = (a, b, "p", "n") if h[a] < h[b] else (b, a, "n", "p")
            vert[d["name"]] = (lo, up, lp, upn)
        else:
            horiz.append(d)

    # ---------------- differential symmetry ----------------
    sigma = _symmetry(devs, pm, ports, all_nets, supplies + grounds)

    # ---------------- tree ----------------
    gcount = sum(1 for lo, up in edges if lo in grounds)
    scount = sum(1 for lo, up in edges if up in supplies)
    from_top = scount > 0 and scount < gcount
    by_name = {d["name"]: d for d in devs}
    line_of = {d["name"]: (d.get("line") or 0, i) for i, d in enumerate(devs)}
    adj = {}
    for name, (lo, up, _, _) in vert.items():
        adj.setdefault(up if from_top else lo, []).append(name)
    visited_d, visited_n = set(), set()

    def order_kids(kids):
        kids = sorted(kids, key=lambda n: line_of[n])
        out, used = [], set()
        for k in kids:
            if k in used:
                continue
            out.append(k)
            used.add(k)
            s = sigma["dev"].get(k)
            if s and s != k and s in kids and s not in used:
                out.append(s)
                used.add(s)
        return out

    def expand(net):
        nodes = []
        for name in order_kids([k for k in adj.get(net, []) if k not in visited_d]):
            if name in visited_d:
                continue
            visited_d.add(name)
            node = Node(by_name[name])
            lo, up, _, _ = vert[name]
            nxt = lo if from_top else up
            node.nets = {lo, up}
            if nxt not in visited_n and not is_supply(nxt) and not is_ground(nxt):
                visited_n.add(nxt)
                node.children = expand(nxt)
            nodes.append(node)
        return nodes

    roots = []
    start_rails = supplies if from_top else grounds
    for r in start_rails:
        visited_n.add(r)
        roots += expand(r)
    # anything left (floating sub-circuits, devices hanging off the other rail)
    for name in sorted(vert, key=lambda n: (h.get(vert[n][0], 0), line_of[n])):
        if name in visited_d:
            continue
        lo, up, _, _ = vert[name]
        seed = up if from_top else lo
        visited_n.add(seed)
        adj.setdefault(seed, [])
        if name not in adj[seed]:
            adj[seed].append(name)
        roots += expand(seed)

    # in-order index for left/right decisions
    order = []

    def walk(n):
        order.append(n)
        for c in n.children:
            walk(c)

    flat = []

    def collect(n):
        flat.append(n)
        for c in n.children:
            collect(c)

    for r in roots:
        collect(r)
    # left-to-right order: by leaf order. compute via packing order (DFS)
    for i, n in enumerate(flat):
        n.order = i
        lo, up, _, _ = vert[n.dev["name"]]
        n.band = h.get(up, 1)

    nodes_by_dev = {n.dev["name"]: n for n in flat}

    # ---------------- pin counts per net (for label-only nets) ----------------
    pin_count = {}
    for d in devs:
        for p, n in d["pins"]:
            if d["kind"] == "M" and p == "b":
                continue
            pin_count[n] = pin_count.get(n, 0) + 1

    # ---------------- mirror pairs ----------------
    def gate_net(name):
        return pm[name].get("g")

    def matched(a, b):
        return (a["kind"] == b["kind"] and a["type"] == b["type"]
                and _size(a) == _size(b))

    def is_inward(a, b):
        A, B = pm[a], pm[b]
        if "g" not in A or "g" not in B:
            return False
        return A["g"] == B["g"] or (A["g"] == B.get("d") and B["g"] == A.get("d"))

    pairs = []          # (left_node, right_node)
    paired = set()
    for n in flat:
        name = n.dev["name"]
        s = sigma["dev"].get(name)
        if name in paired or not s or s == name or s not in nodes_by_dev:
            continue
        m = nodes_by_dev[s]
        if m.band != n.band:
            continue
        a, b = (n, m) if n.order < m.order else (m, n)
        pairs.append((a, b))
        paired |= {name, s}
    # matched siblings (clock pair, tap pair, tail pair): mirrored around their parent
    def sib_pairs(children):
        out = []
        free = [c for c in children if c.dev["name"] not in paired]
        for i, a in enumerate(free):
            for b in free[i + 1:]:
                if a.dev["name"] in paired or b.dev["name"] in paired:
                    continue
                if matched(a.dev, b.dev):
                    out.append((a, b) if a.order < b.order else (b, a))
                    paired.update({a.dev["name"], b.dev["name"]})
        return out

    for n in flat:
        pairs += sib_pairs(n.children)   # children of a non-rail node only

    # ---- global mirror mode: possible when everything is paired or can sit on the axis
    axis = [n for n in flat if n.dev["name"] not in paired]
    axis_ok = all(sigma["dev"].get(n.dev["name"]) == n.dev["name"] for n in axis)
    bands_axis = {}
    for n in axis:
        bands_axis.setdefault(n.band, []).append(n)
    axis_ok = axis_ok and all(len(v) == 1 for v in bands_axis.values())
    axis_ok = axis_ok and all(sigma["dev"].get(d["name"]) == d["name"] for d in horiz)
    axis_ok = axis_ok and bool(pairs) and not other
    # each sigma pair must really be mirror-able (both on sigma)
    sym_mode = axis_ok

    # ---------------- facing ----------------
    for n in flat:
        n.mirror = False
    for a, b in pairs:
        if a.dev["kind"] != "M":
            continue
        inward = is_inward(a.dev["name"], b.dev["name"])
        # inward: left device gate on the right (mirrored); outward: right device mirrored
        a.mirror, b.mirror = (True, False) if inward else (False, True)
    if not sym_mode:
        # neighbours in the same band sharing a gate (current mirrors) face each other
        by_band = {}
        for n in flat:
            if n.dev["kind"] == "M" and n.dev["name"] not in paired:
                by_band.setdefault(n.band, []).append(n)
        for band, lst in by_band.items():
            lst.sort(key=lambda n: n.order)
            for a, b in zip(lst, lst[1:]):
                if gate_net(a.dev["name"]) == gate_net(b.dev["name"]):
                    a.mirror, b.mirror = True, False

    # ---------------- symbols (local) + extents ----------------
    local_sym = {}
    for n in flat:
        d = n.dev
        sym = _device_symbol(d)
        local_sym[d["name"]] = sym
        lw = _r10(sym["meta"]["label_w"])
        if d["kind"] == "M":
            g = pm[d["name"]]["g"]
            gate_side = 40
            if pin_count.get(g, 0) == 1 and not is_supply(g) and not is_ground(g):
                gate_side += _r10(len(g) * CHAR + 14 + VPIN_LEN)
            else:
                gate_side += 10
            label_side = max(lw, 20)
            n.lext, n.rext = (label_side, gate_side) if n.mirror else (gate_side, label_side)
        else:
            n.lext, n.rext = 20, max(lw, 20)

    # ---------------- packing ----------------
    hpairs = [(pm[d["name"]]["p"], pm[d["name"]]["n"]) for d in horiz]

    def extra_gap(left_nets, right_nets):
        for a, b in hpairs:
            if (a in left_nets and b in right_nets) or (b in left_nets and a in right_nets):
                return HGAP
        return 0

    def pack(node):
        if not node.children:
            node.cont = (-node.lext, node.rext)
            return
        for c in node.children:
            pack(c)
        xs, hi, lo_ = _pack_row(node.children, extra_gap)
        centre = _snap((xs[0] + xs[-1]) / 2.0)
        for c, x in zip(node.children, xs):
            c.rel = x - centre
            node.nets |= c.nets
        node.cont = (min(lo_ - centre, -node.lext), max(hi - centre, node.rext))

    if sym_mode:
        _place_symmetric(flat, pairs, axis, vert, sigma, pm, pin_count, horiz, h)
    else:
        for r in roots:
            pack(r)
        if roots:
            xs, _, _ = _pack_row(roots, extra_gap)
        else:
            xs = []

        def absolute(node, x):
            node.x = x
            for c in node.children:
                absolute(c, x + c.rel)

        for r, x in zip(roots, xs):
            absolute(r, x)
    xpairs = [(a.dev["name"], b.dev["name"]) for a, b in pairs
              if a.dev["kind"] == "M" and a.mirror and not b.mirror
              and pm[a.dev["name"]]["g"] == pm[b.dev["name"]].get("d")
              and pm[b.dev["name"]]["g"] == pm[a.dev["name"]].get("d")]

    # ---------------- y positions ----------------
    def y_of(rank):
        return (top - rank) * RP

    placed = []   # (dev, Xf)
    for n in flat:
        d = n.dev
        lo, up, lp, upn = vert[d["name"]]
        cy = y_of(h.get(up, 1)) + RP // 2
        xf = Xf(n.x, cy, mirror=n.mirror)
        sym = local_sym[d["name"]]
        # a MOS whose D/S got swapped by the rail rule is drawn with renamed pins
        if d["kind"] == "M":
            natural = ("s", "d") if d["type"] == "nmos" else ("d", "s")
            if (lp, upn) != natural:
                sym = _rename_pins(sym, {"s": "d", "d": "s"})
        elif d["kind"] in "RCLVI":
            if (lp, upn) == ("p", "n"):
                sym = _rename_pins(sym, {"p": "n", "n": "p"})
        placed.append((d, transform(sym, xf), False))

    # horizontal passives between columns of the nets they bridge
    anchor = {}
    for n in flat:
        for net in vert[n.dev["name"]][:2]:
            anchor.setdefault(net, []).append(n.x)
    stack = {}
    for d in horiz:
        a, b = pm[d["name"]]["p"], pm[d["name"]]["n"]
        xa = sum(anchor.get(a, [0])) / len(anchor.get(a, [0]))
        xb = sum(anchor.get(b, [0])) / len(anchor.get(b, [0]))
        key = frozenset((a, b))
        k = stack.get(key, 0)
        stack[key] = k + 1
        ra = h.get(a, h.get(b, 1))
        # parallel passives between the same two nodes: R_S above, C_S below (rule 6),
        # all inside the vertical span of the source lines so each taps them directly
        offs = [-10, 20, -40, 50]
        y = y_of(ra) + (offs[k] if k < len(offs) else 30 * k)
        xc = _snap((xa + xb) / 2.0)
        left_is_a = xa <= xb
        sym = _device_symbol(d)
        # rot=3 puts pin 'p' on the left, rot=1 on the right
        xf = Xf(xc, y, rot=3 if left_is_a else 1)
        t = transform(sym, xf)
        nm = d["name"]
        ly = y - 12 if k % 2 == 0 else y + 21
        t["labels"] = [(xc, ly, [(nm, "lbl-name"), (" ", ""), (val_text(d), "lbl-val")], "middle")]
        placed.append((d, t, True))
    # leftovers: generic devices on the right
    xr = max([n.x + n.rext for n in flat] + [0]) + 80
    for d in other:
        sym = generic_box(d["name"], [p for p, _ in d["pins"]], d["type"].upper())
        t = transform(sym, Xf(_snap(xr), RP))
        placed.append((d, t, False))
        xr += 140

    return _route_and_emit(cell, ports, roles, placed, pm, sup, gnd, supplies, grounds, pin_count,
                           title, y_of(top) if sup else None, h, sigma, xpairs, sym_mode)


def _size(d):
    p = d["params"]
    return tuple(str(p.get(k, "")).lower() for k in ("w", "l", "m", "nf", "r", "c"))


def _place_symmetric(flat, pairs, axis, vert, sigma, pm, pin_count, horiz, h):
    """Global mirror placement: left representatives are packed outward from the axis,
    partners get the mirrored x, self-symmetric devices sit on the axis (x = 0)."""
    sn = sigma["net"]
    left = {a.dev["name"]: a for a, _ in pairs}
    partner = {a.dev["name"]: b for a, b in pairs}

    def inner_score(n):
        name = n.dev["name"]
        if n.dev["kind"] != "M":
            return 0
        b = partner[name].dev["name"]
        A, B = pm[name], pm[b]
        if A["g"] == B["g"] or (A["g"] == B.get("d") and B["g"] == A.get("d")):
            return 2
        if pin_count.get(A["g"], 0) == 1:
            return -1
        return 0

    # columns: left reps stacked in series through a non-self-symmetric node
    col = {name: [left[name]] for name in left}
    owner = {name: name for name in left}
    by_up, by_lo = {}, {}
    for name, n in left.items():
        lo, up = vert[name][:2]
        by_up.setdefault(up, []).append(n)
        by_lo.setdefault(lo, []).append(n)
    for net in sorted(set(by_up) | set(by_lo), key=lambda x: -h.get(x, 0)):
        if sn.get(net, None) == net:
            continue  # tails / self-symmetric nodes are centred, never column-aligned
        above, below = by_lo.get(net, []), by_up.get(net, [])
        if not above or not below:
            continue
        a = min(above, key=inner_score)
        b = min(below, key=inner_score)
        ca, cb = owner[a.dev["name"]], owner[b.dev["name"]]
        if ca == cb:
            continue
        bands_a = {m.band for m in col[ca]}
        if any(m.band in bands_a for m in col[cb]):
            continue
        col[ca] += col.pop(cb)
        for m in col[ca]:
            owner[m.dev["name"]] = ca
    cols = list(col.values())
    cols.sort(key=lambda c: (-max(inner_score(m) for m in c), min(m.order for m in c)))

    # clearance from the axis per band
    half = {}
    for n in axis:
        half[n.band] = max(half.get(n.band, 0), max(n.lext, n.rext) + GAP)
    hranks = {h.get(pm[d["name"]]["p"], 0) for d in horiz}
    for r in hranks:
        for b in (r, r + 1):
            half[b] = max(half.get(b, 0), HGAP // 2)
    last = {}
    for c in cols:
        x = 0
        for m in c:
            if m.band in last:
                prev = last[m.band]
                req = prev.x - prev.lext - GAP - m.rext
            else:
                req = -max(half.get(m.band, GAP // 2), GAP // 2) - m.rext
            x = min(x, req)
        x = int(x // 10) * 10
        for m in c:
            m.x = x
            last[m.band] = m
    for a, b in pairs:
        b.x = -a.x
    for n in axis:
        n.x = 0


def _pack_row(nodes, extra_gap):
    xs = [0]
    lo, hi = nodes[0].cont
    acc_nets = set(nodes[0].nets)
    for c in nodes[1:]:
        gap = GAP + extra_gap(acc_nets, c.nets)
        off = hi - c.cont[0] + gap
        xs.append(off)
        hi = off + c.cont[1]
        lo = min(lo, off + c.cont[0])
        acc_nets |= c.nets
    return xs, hi, lo


def _rename_pins(sym, mapping):
    s = dict(sym)
    s["pins"] = {mapping.get(k, k): v for k, v in sym["pins"].items()}
    return s


def _device_symbol(d):
    k = d["kind"]
    if k == "M":
        wl, m = wl_text(d)
        return mos(d["type"], d["name"], wl, m)
    if k == "R":
        return resistor(d["name"], val_text(d))
    if k == "C":
        return capacitor(d["name"], val_text(d))
    if k == "L":
        return inductor(d["name"], val_text(d))
    if k in "VI":
        return source(d["type"], d["name"], val_text(d))
    return generic_box(d["name"], [p for p, _ in d["pins"]], d["type"].upper())


# ---------------------------------------------------------------------------
# symmetry
# ---------------------------------------------------------------------------
def _symmetry(devs, pm, ports, nets, rails):
    """Find the differential mirror involution sigma on nets and devices."""
    sn = {}
    for r in rails:
        sn[r] = r
    for n in nets:
        if n in sn:
            continue
        o, _ = diff_partner(n, nets)
        if o and o not in sn:
            sn[n], sn[o] = o, n
    sd = {}

    def sig(d):
        return (d["kind"], d["type"], tuple(sorted((k, str(v)) for k, v in d["params"].items() if k in ("w", "l", "m", "nf", "r", "c", "l"))))

    nonpolar = set("RCL")
    changed = True
    while changed:
        changed = False
        for d in devs:
            if d["name"] in sd:
                continue
            P = pm[d["name"]]
            pins = [(p, n) for p, n in d["pins"] if not (d["kind"] == "M" and p == "b")]
            cands = []
            for e in devs:
                if e["name"] in sd and sd[e["name"]] != d["name"]:
                    continue
                if sig(e) != sig(d):
                    continue
                Q = pm[e["name"]]
                options = [dict((p, p) for p, _ in pins)]
                if d["kind"] in nonpolar:
                    options.append({"p": "n", "n": "p"})
                for perm in options:
                    ok, new = True, {}
                    for p, n in pins:
                        tgt = Q[perm[p]]
                        cur = sn.get(n, new.get(n))
                        if cur is None:
                            back = sn.get(tgt, new.get(tgt))
                            if back is not None and back != n:
                                ok = False
                                break
                            new[n] = tgt
                            new[tgt] = n
                        elif cur != tgt:
                            ok = False
                            break
                    if ok:
                        cands.append((e["name"], new))
                        break
            # prefer a partner whose image needed no guessing
            cands.sort(key=lambda c: (len(c[1]), c[0] == d["name"]))
            if len(cands) >= 1 and (len(cands) == 1 or len(cands[0][1]) < len(cands[1][1])):
                e, new = cands[0]
                sd[d["name"]] = e
                sd[e] = d["name"]
                sn.update(new)
                changed = True
    return {"net": sn, "dev": sd}


# ---------------------------------------------------------------------------
# routing + scene
# ---------------------------------------------------------------------------
def _route_and_emit(cell, ports, roles, placed, pm, sup, gnd, supplies, grounds, pin_count,
                    title, y_rail, h, sigma, xpairs=(), meta_sym=False):
    xs, ys = [], []
    for _, t, _ in placed:
        x0, y0, x1, y1 = t["bbox"]
        xs += [x0, x1]
        ys += [y0, y1]
    if not xs:
        xs, ys = [0, 100], [0, 100]
    bounds = (min(xs) - 120, min(ys) - 100, max(xs) + 120, max(ys) + 100)
    R = Router(bounds)

    symbols, pin_list = [], []
    net_pins = {}
    for d, t, is_h in placed:
        for rect in t["keepout"]:
            R.block_rect(*rect)
        for (lx, ly, parts, anchor) in t["labels"]:
            txt = "".join(p for p, _ in parts)
            w = len(txt) * CHAR
            x0 = lx if anchor == "start" else (lx - w if anchor == "end" else lx - w / 2)
            R.soft_rect(x0, ly - 8, x0 + w, ly + 3, 25)
        for pname, (x, y, dr) in t["pins"].items():
            net = pm[d["name"]].get(pname)
            if net is None:
                continue
            R.add_pin(net, x, y, dr)
            net_pins.setdefault(net, []).append((x, y, dr, d["name"], pname))
            pin_list.append({"inst": d["name"], "pin": pname, "x": x, "y": y, "dir": dr, "net": net})
        symbols.append({"inst": d["name"], "kind": d["kind"], "type": d["type"], "prims": t["prims"],
                        "labels": t["labels"], "bbox": t["bbox"], "params": d["params"], "keepout": t["keepout"],
                        "model": d.get("model")})

    wires_fixed = {}
    rails_out, labels, terminals = [], [], []
    warnings = []

    # ---- ground glyphs ----
    for g in grounds:
        for (x, y, dr, inst, pname) in net_pins.get(g, []):
            dx, dy = {"D": (0, 10), "U": (0, -10), "L": (-10, 0), "R": (10, 0)}[dr]
            sx, sy = x + dx, y + dy
            pts = [(x, y), (sx, sy)]
            R.add_fixed_wire(g, pts)
            R.tree_add_pin(g, x, y)
            wires_fixed.setdefault(g, []).append(pts)
            R.block_rect(sx - 10, sy + 1, sx + 10, sy + 18)
            rails_out.append({"net": g, "kind": "gnd", "x": sx, "y": sy, "prims": ground_glyph(sx, sy),
                              "named": g != gnd})
    # ---- supply rail ----
    if sup and net_pins.get(sup):
        sp = net_pins[sup]
        top_pins = [p for p in sp if p[2] == "U"]
        if top_pins:
            x0 = min(p[0] for p in top_pins) - 30
            x1 = max(p[0] for p in top_pins) + 30
            pts = [(x0, y_rail), (x1, y_rail)]
            R.add_fixed_wire(sup, pts)
            wires_fixed.setdefault(sup, []).append(pts)
            if sup in ports:
                tm = _vpin(sup, x0, y_rail, "R", "io")
                _register_vpin(R, tm)
                terminals.append(tm)
                pin_list.append({"inst": "PORT", "pin": sup, "x": x0, "y": y_rail, "dir": "R", "net": sup})
            else:
                xc = _snap((x0 + x1) / 2.0)
                labels.append({"net": sup, "text": sup, "x": xc, "y": y_rail - 7, "ax": xc, "ay": y_rail,
                               "anchor": "middle", "cls": "lbl-rail"})
                R.soft_rect(xc - len(sup) * 4, y_rail - 18, xc + len(sup) * 4, y_rail - 4, 40)
            failed = R.route_net(sup, [(x, y, dr) for (x, y, dr, _, _) in sp])
            for fx, fy in failed:
                warnings.append(f"{sup}: ({fx},{fy})에서 전원선까지 배선 불가 - 전원 기호로 대체")
                rails_out.append({"net": sup, "kind": "vdd", "x": fx, "y": fy, "prims": vdd_glyph(fx, fy, sup)})
        else:
            for (x, y, dr, _, _) in sp:
                rails_out.append({"net": sup, "kind": "vdd", "x": x, "y": y, "prims": vdd_glyph(x, y, sup)})
    for s in supplies:
        if s == sup:
            continue
        for (x, y, dr, _, _) in net_pins.get(s, []):
            rails_out.append({"net": s, "kind": "vdd", "x": x, "y": y, "prims": vdd_glyph(x, y, s)})

    # ---- channel buses: one straight horizontal per drain/source node ----
    top_rank = max(h.values()) if h else 0
    chan = {}
    for d, t, is_h in placed:
        if is_h or d["kind"] not in "MRCLVIQD":
            continue
        for pname, (x, y, dr) in t["pins"].items():
            net = pm[d["name"]].get(pname)
            if dr in "UD" and net and net not in supplies and net not in grounds:
                chan.setdefault(net, []).append((x, y, dr))
    bus_nets = sorted([n for n in chan if len(chan[n]) >= 2],
                      key=lambda n: (-h.get(n, 0), min(p[0] for p in chan[n])))
    for net in bus_nets:
        P = chan[net]
        above = [p[1] for p in P if p[2] == "D"]   # pins of devices sitting above the node
        below = [p[1] for p in P if p[2] == "U"]   # pins of devices sitting below the node
        lim0 = max(above) if above else -1e9
        lim1 = min(below) if below else 1e9
        if lim0 >= lim1:
            continue
        xs_ = sorted(set(p[0] for p in P))
        if len(xs_) == 1:
            ys_ = [p[1] for p in P]
            R.try_fixed(net, [[(xs_[0], min(ys_)), (xs_[0], max(ys_))]])
            continue
        if net in h:
            yr = (top_rank - h[net]) * RP
        else:
            yr = _snap(((lim0 if above else lim1 - 60) + (lim1 if below else lim0 + 60)) / 2.0)
        for off in (0, -20, 20, -10, 10):
            yb = yr + off
            if not (lim0 < yb < lim1):
                continue
            polys = [[(xs_[0], yb), (xs_[-1], yb)]] + [[(x, y), (x, yb)] for x, y, _ in P if y != yb]
            if R.try_fixed(net, polys):
                break

    # ---- horizontal passives: straight lead into the node's vertical line ----
    for d, t, is_h in placed:
        if not is_h:
            continue
        for pname, (x, y, dr) in t["pins"].items():
            net = pm[d["name"]].get(pname)
            step = 10 if dr == "R" else -10
            cx = x + step
            for _ in range(60):
                c = R.c(cx, y)
                if c in R.hard or (c in R.pins and R.pins[c][0] != net):
                    break
                own = R.wire.get(c, {})
                if own.get(net) == {"v"} and len(own) == 1:
                    R.try_fixed(net, [[(x, y), (cx, y)]])
                    break
                if own:
                    break
                cx += step

    # ---- cross-coupled pairs: two diagonals forming an X on the symmetry axis ----
    diags, extra_dots, preconn = [], [], set()
    pins_of = {}
    for p in pin_list:
        pins_of[(p["inst"], p["pin"])] = p
    for a, b in xpairs:
        plan = []
        for src, dst in ((a, b), (b, a)):
            dp, gp = pins_of.get((src, "d")), pins_of.get((dst, "g"))
            if not dp or not gp:
                plan = None
                break
            off = -10 if dp["dir"] == "U" else 10
            sx, sy = dp["x"], dp["y"] + off
            gc = R.c(sx, sy)
            own = R.wire.get(gc, {})
            if own.get(dp["net"]) != {"v"} or len(own) != 1 or R._deg(dp["net"], gc) != 2:
                plan = None
                break
            plan.append((dp["net"], sx, sy, gp))
        if not plan:
            continue
        for net, sx, sy, gp in plan:
            diags.append({"net": net, "x1": sx, "y1": sy, "x2": gp["x"], "y2": gp["y"], "diag": True})
            extra_dots.append({"net": net, "x": sx, "y": sy})
            R.node[R.c(sx, sy)] = net
            preconn.add((gp["x"], gp["y"]))
            n_steps = int(max(abs(gp["x"] - sx), abs(gp["y"] - sy)) // 2) + 1
            for i in range(n_steps + 1):
                t = i / float(n_steps)
                cx, cy = R.c(sx + (gp["x"] - sx) * t, sy + (gp["y"] - sy) * t)
                if (cx, cy) not in (R.c(sx, sy), R.c(gp["x"], gp["y"])):
                    R.hard.add((cx, cy))

    # ---- signal nets ----
    for net in list(net_pins):
        net_pins[net] = [p for p in net_pins[net] if (p[0], p[1]) not in preconn] or net_pins[net][:0]
    sig_nets = [n for n in net_pins if n not in supplies and n not in grounds and net_pins[n]]

    def bbox_size(n):
        P = net_pins[n]
        return (max(p[0] for p in P) - min(p[0] for p in P)) + (max(p[1] for p in P) - min(p[1] for p in P))

    # ---- Virtuoso-style pins for every port of the cell ----
    def pin_kind(n):
        r = roles.get(n, "inout")
        return "out" if r == "out" else ("io" if r == "inout" else "in")

    port_plan = {}
    for net in ports:
        if net in supplies or net in grounds or not net_pins.get(net):
            continue
        P = net_pins[net]
        if len(P) == 1 and not R.tree.get(net):
            x, y, dr, inst, pname = P[0]
            tm = _vpin(net, x, y, OPP[dr], pin_kind(net))
            _register_vpin(R, tm)
            terminals.append(tm)
            pin_list.append({"inst": "PORT", "pin": net, "x": x, "y": y, "dir": OPP[dr], "net": net})
            port_plan[net] = "single"
        elif (len(P) >= 2 and not R.tree.get(net) and bbox_size(net) > 240
              and all(pm[p[3]].get("g") == net and p[4] == "g" for p in P)):
            # rule 9b: an input that only drives far-apart gates (NAND/NOR inputs): one pin,
            # the other gates carry the same name
            for i, (x, y, dr, inst, pname) in enumerate(P):
                if i == 0:
                    tm = _vpin(net, x, y, OPP[dr], pin_kind(net))
                    _register_vpin(R, tm)
                    pin_list.append({"inst": "PORT", "pin": net, "x": x, "y": y, "dir": OPP[dr], "net": net})
                else:
                    tm = _terminal(net, x, y, dr, False)
                    tm["plain"] = True
                terminals.append(tm)
            port_plan[net] = "gates"
    # drawing extents (symbols, their annotations, pin tags placed so far)
    ex0, ex1 = [], []
    for sy_ in symbols:
        ex0.append(sy_["bbox"][0]); ex1.append(sy_["bbox"][2])
        for (lx, ly, parts, anc) in sy_["labels"]:
            w = len("".join(t for t, _ in parts)) * CHAR
            lx0 = lx if anc == "start" else (lx - w if anc == "end" else lx - w / 2)
            ex0.append(lx0); ex1.append(lx0 + w)
    for tm in terminals:
        w = len(tm["net"]) * CHAR + VPIN_LEN
        ex0.append(tm["x"] - (w + 8 if tm.get("vdir") == "R" else 0))
        ex1.append(tm["x"] + (w + 8 if tm.get("vdir") == "L" else 0))
    left_edge = _snap(min(ex0 + [0]) - 30)
    right_edge = _snap(max(ex1 + [0]) + 30)
    used_y = {"L": set(), "R": set()}
    sym_axis = 0 if meta_sym else None
    for net in ports:
        if net in port_plan or net in supplies or net in grounds or not net_pins.get(net):
            continue
        P = net_pins[net]
        mx = sum(p[0] for p in P) / len(P)
        kind = pin_kind(net)
        on_axis = sym_axis is not None and abs(mx - sym_axis) <= 1
        if sym_axis is not None and not on_axis:
            side = "L" if mx < sym_axis else "R"
        elif on_axis and kind == "in":
            side = "B"     # self-symmetric input (shared bias of a mirrored pair): from below, on the axis
        else:
            side = "L" if kind == "in" else "R"
        y_net = (top_rank - h[net]) * RP if net in h else _snap(sum(p[1] for p in P) / len(P))
        if side == "B":
            px = _snap(sym_axis)
            py = _snap(max([sy_["bbox"][3] for sy_ in symbols] + [r["y"] + 18 for r in rails_out]) + 30)
            d = "U"
        else:
            # attach where a straight lead from the edge meets a plain vertical stretch of the
            # net: outermost first, then nearest the node, upper before lower (keeps mirrors equal)
            cands = []
            for c in R.tree.get(net, ()):
                own = R.wire.get(c, {})
                if own.get(net) != {"v"} or len(own) != 1 or R._deg(net, c) != 2:
                    continue
                cands.append(((c[0] if side == "L" else -c[0]), abs(c[1] * R.g - y_net), c[1], c[1] * R.g))
            cands.sort()
            free = [c for c in cands if all(abs(c[3] - u) >= 20 for u in used_y[side])]
            py = free[0][3] if free else (cands[0][3] if cands else y_net)
            while any(abs(py - u) < 20 for u in used_y[side]):
                py += 20
            used_y[side].add(py)
            px = left_edge if side == "L" else right_edge
            d = "R" if side == "L" else "L"
        tm = _vpin(net, px, py, d, kind)
        _register_vpin(R, tm)
        terminals.append(tm)
        R.add_pin(net, px, py, d)
        net_pins[net].append((px, py, d, "PORT", net))
        pin_list.append({"inst": "PORT", "pin": net, "x": px, "y": py, "dir": d, "net": net})
        port_plan[net] = "route"
    # VSS: inout pin at the bottom-left tied to its own ground symbol
    if gnd and gnd in ports and net_pins.get(gnd):
        yg = _snap(max(r["y"] for r in rails_out if r["net"] == gnd) if any(r["net"] == gnd for r in rails_out) else 0)
        px, py = left_edge, yg
        R.add_fixed_wire(gnd, [(px, py), (px + 20, py)])
        R.block_rect(px + 10, py + 1, px + 30, py + 18)
        rails_out.append({"net": gnd, "kind": "gnd", "x": px + 20, "y": py, "prims": ground_glyph(px + 20, py),
                          "named": False})
        tm = _vpin(gnd, px, py, "R", "io")
        _register_vpin(R, tm)
        terminals.append(tm)
        pin_list.append({"inst": "PORT", "pin": gnd, "x": px, "y": py, "dir": "R", "net": gnd})

    # channel nets (ranked) first, then gate-only nets; small first
    sig_nets.sort(key=lambda n: (n not in h, bbox_size(n)))
    for net in sig_nets:
        P = net_pins[net]
        if port_plan.get(net) in ("single", "gates"):
            continue
        if len(P) == 1:
            x, y, dr, inst, pname = P[0]
            if not R.tree.get(net):
                tm = _terminal(net, x, y, dr, net in ports)
                tm["plain"] = True
                terminals.append(tm)
                continue
        # start from the pin nearest the centroid of the net
        cx = sum(p[0] for p in P) / len(P)
        cy = sum(p[1] for p in P) / len(P)
        P = sorted(P, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        failed = R.route_net(net, [(x, y, dr) for (x, y, dr, _, _) in P])
        for fx, fy in failed:
            dr = next(p[2] for p in P if p[0] == fx and p[1] == fy)
            warnings.append(f"{net}: ({fx},{fy}) 핀은 배선 불가 - 이름표로 연결")
            terminals.append(_terminal(net, fx, fy, dr, False, by_label=True))
        if failed:
            labels.append(_wire_label(R, net, "lbl-port", force=True))

    # ---- labels for routed nets ----
    for net in sig_nets:
        if not R.edges.get(net):
            continue
        if net in ports and port_plan.get(net) == "route":
            continue       # named by its Virtuoso pin
        cls = "lbl-port" if net in ports else "lbl-net"
        lab = _wire_label(R, net, cls, others=labels, symbols=symbols)
        if lab:
            labels.append(lab)

    labels = [l for l in labels if l]
    wires, dots = [], []
    for net in R.edges:
        for s in R.segments(net):
            wires.append({"net": net, "x1": s[0], "y1": s[1], "x2": s[2], "y2": s[3]})
        for (x, y) in R.junctions(net):
            dots.append({"net": net, "x": x, "y": y})
    wires += diags
    dots += extra_dots

    sc = {
        "cell": cell["name"], "kind": "leaf", "title": title or cell["name"],
        "symbols": symbols, "pins": pin_list, "wires": wires, "dots": dots,
        "labels": labels, "rails": rails_out, "terminals": terminals,
        "warnings": warnings, "ports": ports, "bounds": bounds,
        "meta": {"ranks": h, "sigma": sigma["dev"]},
    }
    sc["bounds"] = fit_bounds(sc)
    return sc


OPP = {"L": "R", "R": "L", "U": "D", "D": "U"}


def _vpin(net, x, y, d, kind):
    """Virtuoso-style pin whose wire attaches at (x, y); d = direction towards the circuit."""
    gap = VPIN_LEN + 5
    t = {"net": net, "x": x, "y": y, "vpin": kind, "vdir": d, "port": True, "plain": True}
    if d == "R":
        t.update(tx=x - gap, ty=y + 3.5, anchor="end")
    elif d == "L":
        t.update(tx=x + gap, ty=y + 3.5, anchor="start")
    elif d == "D":                       # body above the attach point, name further up
        t.update(tx=x + 3.5, ty=y - gap, anchor="start", rot=True)
    else:                                # body below, name further down
        t.update(tx=x + 3.5, ty=y + gap, anchor="end", rot=True)
    return t


def _register_vpin(R, t):
    R.block_rect(*vpin_body_rect(t["x"], t["y"], t["vdir"]))
    w = len(t["net"]) * CHAR
    if t["vdir"] == "R":
        R.soft_rect(t["tx"] - w, t["ty"] - 9, t["tx"], t["ty"] + 2, 40)
    elif t["vdir"] == "L":
        R.soft_rect(t["tx"], t["ty"] - 9, t["tx"] + w, t["ty"] + 2, 40)
    elif t["vdir"] == "D":
        R.soft_rect(t["tx"] - 9, t["ty"] - w, t["tx"] + 2, t["ty"], 40)
    else:
        R.soft_rect(t["tx"] - 9, t["ty"], t["tx"] + 2, t["ty"] + w, 40)


def fit_bounds(sc, margin=36):
    xs, ys = [], []
    from .verify import text_width
    for s_ in sc["symbols"]:
        xs += [s_["bbox"][0], s_["bbox"][2]]
        ys += [s_["bbox"][1], s_["bbox"][3]]
        for (lx, ly, parts, anc) in s_["labels"]:
            w = text_width("".join(t for t, _ in parts), 9.6)
            lx0 = lx if anc == "start" else (lx - w if anc == "end" else lx - w / 2)
            xs += [lx0, lx0 + w]
            ys += [ly - 10, ly + 3]
    for w in sc["wires"]:
        xs += [w["x1"], w["x2"]]
        ys += [w["y1"], w["y2"]]
    for r in sc["rails"]:
        xs += [r["x"] - 12, r["x"] + 12]
        ys += [r["y"] - 24, r["y"] + 18]
    for t in sc["terminals"]:
        w = len(t["net"]) * 6.2
        if t.get("rot"):
            xs += [t["tx"] - 10, t["tx"] + 2]
            ys += [t["ty"] - w, t["ty"] + w]
        else:
            x0 = t["tx"] if t["anchor"] == "start" else (t["tx"] - w if t["anchor"] == "end" else t["tx"] - w / 2)
            xs += [x0, x0 + w, t["x"]]
            ys += [t["ty"] - 10, t["ty"] + 3, t["y"]]
    for l in sc["labels"]:
        w = len(l["text"]) * 6.2
        xs += [l["x"] - w, l["x"] + w]
        ys += [l["y"] - 10, l["y"] + 3]
    if not xs:
        return sc["bounds"]
    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def _terminal(net, x, y, dr, is_port, by_label=False):
    """Name tag on a single pin (port input, bias, or label-connected pin)."""
    off = 7
    if dr == "L":
        tx, ty, anc = x - off, y + 3.5, "end"
    elif dr == "R":
        tx, ty, anc = x + off, y + 3.5, "start"
    elif dr == "U":
        tx, ty, anc = x, y - off - 2, "middle"
    else:
        tx, ty, anc = x, y + off + 9, "middle"
    return {"net": net, "x": x, "y": y, "tx": tx, "ty": ty, "anchor": anc, "port": is_port,
            "by_label": by_label}


def _wire_label(R, net, cls, others=(), symbols=(), force=False):
    segs = R.segments(net)
    if not segs:
        return None
    cands = []
    for (x1, y1, x2, y2) in segs:
        L = abs(x2 - x1) + abs(y2 - y1)
        w = len(net) * CHAR
        if y1 == y2:
            for t in (0.5, 0.25, 0.75):
                ax = _snap(x1 + (x2 - x1) * t)
                cands.append((L >= w + 10, L, {"net": net, "text": net, "x": ax, "y": y1 - 5, "ax": ax, "ay": y1,
                                                "anchor": "middle", "cls": cls}))
        else:
            ay = _snap((y1 + y2) / 2.0)
            cands.append((L >= 30, L * 0.6, {"net": net, "text": net, "x": x1 + 5, "y": ay + 3.5, "ax": x1, "ay": ay,
                                             "anchor": "start", "cls": cls}))

    def overlap(c):
        w = len(net) * CHAR
        x0 = c["x"] - (w / 2 if c["anchor"] == "middle" else 0)
        bx = (x0, c["y"] - 9, x0 + w, c["y"] + 1)
        score = 0
        for o in others:
            if not o:
                continue
            ow = len(o["text"]) * CHAR
            ox0 = o["x"] - (ow / 2 if o["anchor"] == "middle" else (ow if o["anchor"] == "end" else 0))
            if _ov(bx, (ox0, o["y"] - 9, ox0 + ow, o["y"] + 1)):
                score += 100
        for s in symbols:
            if _ov(bx, s["bbox"]):
                score += 40
            for (lx, ly, parts, anc) in s["labels"]:
                txt = "".join(p for p, _ in parts)
                lw = len(txt) * CHAR
                lx0 = lx if anc == "start" else (lx - lw if anc == "end" else lx - lw / 2)
                if _ov(bx, (lx0, ly - 8, lx0 + lw, ly + 2)):
                    score += 60
        for cell, nets in R.wire.items():
            if cell[0] * R.g >= bx[0] and cell[0] * R.g <= bx[2] and bx[1] <= cell[1] * R.g <= bx[3]:
                if any(n != net for n in nets):
                    score += 15
        return score

    cands.sort(key=lambda c: (overlap(c[2]), not c[0], -c[1]))
    return cands[0][2]


def _ov(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
