"""Block-level placement + routing.

  * each subckt instance becomes a block symbol chosen by the recogniser
    (differential triangle, summer circle, DFF/latch box, generic box);
  * pins are put on sides by role: data in -> left, out -> right, clock and
    feedback inputs -> bottom, bias -> top (drawn as name labels), supplies hidden;
  * columns follow signal flow (longest path over data edges, feedback edges
    removed by DFS), blocks are aligned so the main data wires are straight.
"""
from __future__ import annotations

from .analyze import diff_partner, is_ground, is_supply, BIAS_RE
from .geom import Xf, block_symbol, ground_glyph, transform, vdd_glyph
from .layout_leaf import (CHAR, OPP, _device_symbol, _register_vpin, _rename_pins, _snap, _terminal,
                          _vpin, _wire_label, fit_bounds)
from .router import Router
from .verify import FONT, _ov, _seg_hits_rect, text_box

LAYER_GAP = 170
STACK_GAP = 90
PORT_DX = 130


def layout_block(cell, ir, roles, classes):
    insts = [d for d in cell["devices"] if d["kind"] == "X"]
    ports = cell["ports"]
    prole = roles[cell["name"]]

    def pin_role(d, p):
        r = roles.get(d["ref"], {}).get(p, "inout")
        return r

    # ---------------- nets ----------------
    net_pins = {}
    for d in insts:
        for p, n in d["pins"]:
            net_pins.setdefault(n, []).append((d["name"], p, pin_role(d, p)))

    def is_label_net(n):
        if is_supply(n) or is_ground(n):
            return False
        pins = net_pins.get(n, [])
        if n in ports and prole.get(n) == "bias":
            return True
        if any(r == "out" for _, _, r in pins):
            return False
        return bool(pins) and all(r == "bias" for _, _, r in pins) and (n in ports or BIAS_RE.search(n))

    # ---------------- data graph + feedback ----------------
    drivers = {}
    for d in insts:
        for p, n in d["pins"]:
            if pin_role(d, p) == "out":
                drivers.setdefault(n, []).append(d["name"])
    succ = {d["name"]: [] for d in insts}
    for d in insts:
        for p, n in d["pins"]:
            if pin_role(d, p) in ("in", "inout"):
                for src in drivers.get(n, []):
                    if src != d["name"]:
                        succ[src].append((d["name"], p))
    # DFS from blocks fed by input ports (fallback: netlist order)
    starts = []
    for d in insts:
        if any(n in ports and prole.get(n) in ("in", "clk") and pin_role(d, p) in ("in", "inout")
               for p, n in d["pins"]):
            starts.append(d["name"])
    starts += [d["name"] for d in insts if d["name"] not in starts]
    state, fb = {}, set()

    def dfs(u):
        state[u] = 1
        for v, p in succ[u]:
            if state.get(v) == 1:
                fb.add((v, p))
            elif v not in state:
                dfs(v)
        state[u] = 2

    for s in starts:
        if s not in state:
            dfs(s)
    # longest path layering on forward edges
    layer = {d["name"]: 0 for d in insts}
    for _ in range(len(insts) + 1):
        for u in succ:
            for v, p in succ[u]:
                if (v, p) in fb:
                    continue
                if layer[v] < layer[u] + 1:
                    layer[v] = layer[u] + 1

    # ---------------- symbols ----------------
    by_name = {d["name"]: d for d in insts}
    syms = {}
    for d in insts:
        sub_ports = ir["cells"][d["ref"]]["ports"] if d["ref"] in ir["cells"] else [p for p, _ in d["pins"]]
        sides = {"L": [], "R": [], "T": [], "B": []}
        marks = {}
        for p, n in d["pins"]:
            r = pin_role(d, p)
            if r in ("power", "ground"):
                continue
            if (d["name"], p) in fb:
                sides["B"].append(p)
            elif r == "out":
                sides["R"].append(p)
            elif r == "clk":
                sides["B"].append(p)
                marks[p] = "clk"
            elif r == "bias":
                sides["T"].append(p)
            else:
                sides["L"].append(p)
            pol = diff_partner(p, sub_ports)[1]
            if pol and p not in marks:
                marks[p] = pol
        cls = classes.get(d["ref"], {"shape": "box", "title": d["ref"]})
        shape = cls["shape"]
        title = cls["title"]
        if shape == "sum":
            marks = {k: v for k, v in marks.items() if v == "clk"}
        arrows = set(sides["L"]) | set(sides["B"])
        syms[d["name"]] = block_symbol(shape, title, sides, marks, arrows)

    # ---------------- placement ----------------
    layers = {}
    for d in insts:
        layers.setdefault(layer[d["name"]], []).append(d["name"])
    pos = {}
    pin_abs = {}

    def place(name, x, y):
        pos[name] = (x, y)
        t = transform(syms[name], Xf(x, y))
        pin_abs[name] = t
        return t

    x = 0
    for k in sorted(layers):
        names = layers[k]

        def bary(nm):
            ys = []
            for p, n in by_name[nm]["pins"]:
                for src in drivers.get(n, []):
                    if src in pin_abs:
                        for sp, sn in by_name[src]["pins"]:
                            if sn == n:
                                ys.append(pin_abs[src]["pins"][sp][1])
            return sum(ys) / len(ys) if ys else 0

        names.sort(key=lambda nm: (bary(nm), by_name[nm].get("line") or 0))
        width = max(syms[nm]["meta"]["w"] for nm in names)
        ycur = None
        for nm in names:
            s = syms[nm]
            # align the first left pin with its driver
            target = None
            for side_pin in [p for p, _ in by_name[nm]["pins"]]:
                if side_pin in s["pins"] and s["pins"][side_pin][2] == "L":
                    n = dict(by_name[nm]["pins"])[side_pin]
                    for src in drivers.get(n, []):
                        if src in pin_abs and src != nm:
                            sp = next(p for p, nn in by_name[src]["pins"] if nn == n)
                            target = pin_abs[src]["pins"][sp][1] - s["pins"][side_pin][1]
                            break
                    break
            y = target if target is not None else (0 if ycur is None else ycur)
            if ycur is not None and y < ycur:
                y = ycur
            y = _snap(y)
            place(nm, _snap(x + (width - s["meta"]["w"]) / 2), y)
            ycur = y + s["meta"]["h"] + STACK_GAP
        x += width + LAYER_GAP

    # ---------------- lone passives (load caps, terminations) ----------------
    prims = [d for d in cell["devices"] if d["kind"] != "X"]
    prim_t, prim_rail = {}, {}
    bodies = [(pos[n][0], pos[n][1], pos[n][0] + syms[n]["meta"]["w"], pos[n][1] + syms[n]["meta"]["h"])
              for n in pos]
    per_net = {}
    for d in prims:
        P = dict(d["pins"])
        sym = _device_symbol(d)
        names = [p for p, _ in d["pins"]]
        a, b2 = (P.get(names[0]), P.get(names[1])) if len(names) >= 2 else (None, None)
        sig = a if not (is_supply(a) or is_ground(a)) else b2
        if sig is a and len(names) >= 2 and not (is_supply(b2) or is_ground(b2)):
            sig = a  # floating passive between two signals: still hang it off the first net
        sig_pin = names[0] if sig == a else names[1]
        if sig_pin != "p":
            sym = _rename_pins(sym, {"p": "n", "n": "p"})
        ref = None
        for i, p, r in net_pins.get(sig, []):
            if i in pin_abs and p in pin_abs[i]["pins"]:
                cand = pin_abs[i]["pins"][p]
                if ref is None or r == "out":
                    ref = cand
        rx, ry = (ref[0], ref[1]) if ref else (0, 0)
        kk = per_net.get(sig, 0)
        per_net[sig] = kk + 1
        x = _snap(rx + (60 if ref and ref[2] == "R" else -60 if ref and ref[2] == "L" else 0) + 50 * kk)
        y = _snap(ry + 90)
        for _ in range(40):
            t = transform(sym, Xf(x, y))
            bb = t["bbox"]
            grow = (bb[0] - 30, bb[1] - 30, bb[2] + 60, bb[3] + 40)
            if not any(_ov(grow, bd) for bd in bodies):
                break
            x += 40
        bodies.append(t["bbox"])
        prim_t[d["name"]] = t
        prim_rail[d["name"]] = [p for p in names if p != sig_pin]

    # ---------------- ports ----------------
    all_t = list(pin_abs.values()) + list(prim_t.values())
    if all_t:
        bx0 = min(t["bbox"][0] for t in all_t)
        bx1 = max(t["bbox"][2] for t in all_t)
        by1 = max(t["bbox"][3] for t in all_t)
    else:
        bx0 = bx1 = by1 = 0
    port_pins = []
    used_y = {"L": set(), "R": set()}

    def free_y(side, y):
        y = _snap(y)
        while y in used_y[side] or y - 10 in used_y[side] or y + 10 in used_y[side]:
            y += 20
        used_y[side].add(y)
        return y

    clk_i = 0
    for pn in ports:
        r = prole.get(pn, "inout")
        if r in ("power", "ground") or is_label_net(pn):
            continue
        sinks = [(i, p) for i, p, _ in net_pins.get(pn, [])]
        ref_y = None
        for i, p in sinks:
            if p in pin_abs[i]["pins"]:
                ref_y = pin_abs[i]["pins"][p][1]
                break
        if r == "out":
            drv = [(i, p) for i, p, rr in net_pins.get(pn, []) if rr == "out"]
            if drv and drv[0][1] in pin_abs[drv[0][0]]["pins"]:
                ref_y = pin_abs[drv[0][0]]["pins"][drv[0][1]][1]
            y = free_y("R", ref_y if ref_y is not None else 0)
            port_pins.append((pn, _snap(bx1 + PORT_DX), y, "L"))
        elif any(pin_abs[i]["pins"].get(p, (0, 0, "L"))[2] == "D" for i, p in sinks):
            # clock-like inputs enter from below, right under their first sink pin
            sx = next(pin_abs[i]["pins"][p][0] for i, p in sinks if pin_abs[i]["pins"].get(p, (0, 0, "L"))[2] == "D")
            port_pins.append((pn, _snap(sx), _snap(by1 + 70), "U"))
            clk_i += 1
        else:
            y = free_y("L", ref_y if ref_y is not None else 0)
            port_pins.append((pn, _snap(bx0 - PORT_DX), y, "R"))

    # ---------------- routing ----------------
    xs = [t["bbox"][0] for t in all_t] + [t["bbox"][2] for t in all_t] + [p[1] for p in port_pins]
    ys = [t["bbox"][1] for t in all_t] + [t["bbox"][3] for t in all_t] + [p[2] for p in port_pins]
    if not xs:
        xs, ys = [0, 100], [0, 100]
    bounds = (min(xs) - 120, min(ys) - 120, max(xs) + 120, max(ys) + 140)
    R = Router(bounds)
    symbols, pin_list, terminals, labels = [], [], [], []
    route_pins = {}
    for d in insts:
        t = pin_abs[d["name"]]
        for rect in t["keepout"]:
            R.block_rect(*rect)
        nmap = dict(d["pins"])
        for p, (px, py, dr) in t["pins"].items():
            n = nmap[p]
            R.add_pin(n, px, py, dr)
            pin_list.append({"inst": d["name"], "pin": p, "x": px, "y": py, "dir": dr, "net": n})
            route_pins.setdefault(n, []).append((px, py, dr))
        cls = classes.get(d["ref"], {})
        inst_label = d["name"] if not d.get("auto") else "(자동)"
        sub_label = d["ref"] if not d.get("auto") else cls.get("label", "")
        parts = [(inst_label, "lbl-name"), (" : ", "lbl-name"), (sub_label, "lbl-cell")]
        bx, by = pos[d["name"]]
        bw, bh = syms[d["name"]]["meta"]["w"], syms[d["name"]]["meta"]["h"]
        symbols.append({"inst": d["name"], "kind": "X", "ref": d["ref"], "auto": bool(d.get("auto")),
                        "prims": t["prims"], "labels": [], "label_parts": parts, "bbox": t["bbox"],
                        "keepout": t["keepout"], "body": (bx, by, bx + bw, by + bh),
                        "hidden_pins": [p for p, n in d["pins"] if p not in t["pins"]],
                        "cls": cls.get("class")})

    rails_out = []
    for d in prims:
        t = prim_t[d["name"]]
        nmap = dict(d["pins"])
        for rect in t["keepout"]:
            R.block_rect(*rect)
        for p, (px, py, dr) in t["pins"].items():
            n = nmap[p]
            R.add_pin(n, px, py, dr)
            pin_list.append({"inst": d["name"], "pin": p, "x": px, "y": py, "dir": dr, "net": n})
            if is_ground(n) or is_supply(n):
                dx, dy = {"D": (0, 10), "U": (0, -10), "L": (-10, 0), "R": (10, 0)}[dr]
                R.add_fixed_wire(n, [(px, py), (px + dx, py + dy)])
                glyph = ground_glyph(px + dx, py + dy) if is_ground(n) else vdd_glyph(px + dx, py + dy, n)
                rails_out.append({"net": n, "kind": "gnd" if is_ground(n) else "vdd",
                                  "x": px + dx, "y": py + dy, "prims": glyph, "named": False})
                if is_ground(n):
                    R.block_rect(px + dx - 10, py + dy + 1, px + dx + 10, py + dy + 18)
            else:
                route_pins.setdefault(n, []).append((px, py, dr))
        symbols.append({"inst": d["name"], "kind": d["kind"], "type": d["type"], "prims": t["prims"],
                        "labels": t["labels"], "bbox": t["bbox"], "keepout": t["keepout"],
                        "params": d["params"]})

    def pin_kind(n):
        r = prole.get(n, "inout")
        return "out" if r == "out" else ("io" if r in ("inout", "power", "ground") else "in")

    # Virtuoso-style pins: inputs left, outputs right, clocks below
    for (pn, px, py, dr) in port_pins:
        R.add_pin(pn, px, py, dr)
        route_pins.setdefault(pn, []).append((px, py, dr))
        pin_list.append({"inst": "PORT", "pin": pn, "x": px, "y": py, "dir": dr, "net": pn})
        tm = _vpin(pn, px, py, dr, pin_kind(pn))
        _register_vpin(R, tm)
        terminals.append(tm)

    # supplies are hidden on block symbols; the cell's own VDD / VSS pins sit top-left /
    # bottom-left, each tied to its rail symbol
    sup_ports = [p for p in ports if prole.get(p) in ("power", "ground")]
    if sup_ports and all_t:
        xp = _snap(bx0 - PORT_DX)
        ytop = _snap(min(t["bbox"][1] for t in all_t) - 60)
        ybot = _snap(max([t["bbox"][3] for t in all_t] + [p[2] for p in port_pins]) + 50)
        k_top = k_bot = 0
        for pn in sup_ports:
            is_p = prole.get(pn) == "power"
            py = ytop - 30 * k_top if is_p else ybot + 30 * k_bot
            if is_p:
                k_top += 1
            else:
                k_bot += 1
            R.add_fixed_wire(pn, [(xp, py), (xp + 20, py)])
            if is_p:
                glyph = [g for g in vdd_glyph(xp + 20, py, pn) if g[0] != "text"]
                R.block_rect(xp + 10, py - 10, xp + 30, py - 1)
            else:
                glyph = ground_glyph(xp + 20, py)
                R.block_rect(xp + 10, py + 1, xp + 30, py + 18)
            rails_out.append({"net": pn, "kind": "vdd" if is_p else "gnd", "x": xp + 20, "y": py,
                              "prims": glyph, "named": False})
            tm = _vpin(pn, xp, py, "R", "io")
            _register_vpin(R, tm)
            terminals.append(tm)
            pin_list.append({"inst": "PORT", "pin": pn, "x": xp, "y": py, "dir": "R", "net": pn})

    # bias / label-only nets: short stub + name
    for n in list(route_pins):
        if not is_label_net(n):
            continue
        first = n in ports
        for (px, py, dr) in route_pins[n]:
            dx, dy = {"U": (0, -20), "D": (0, 20), "L": (-20, 0), "R": (20, 0)}[dr]
            pts = [(px, py), (px + dx, py + dy)]
            R.add_fixed_wire(n, pts)
            if first:
                # the port itself: one Virtuoso pin; further taps carry the name only
                first = False
                tm = _vpin(n, px + dx, py + dy, OPP[dr], pin_kind(n))
                _register_vpin(R, tm)
                terminals.append(tm)
                pin_list.append({"inst": "PORT", "pin": n, "x": px + dx, "y": py + dy, "dir": OPP[dr], "net": n})
                continue
            tm = _terminal(n, px + dx, py + dy, dr, False)
            tm["plain"] = True
            if dr in "UD":
                tm["rot"] = True
                tm["tx"], tm["ty"] = px + 3.5, py + dy + (-5 if dr == "U" else 5)
                tm["anchor"] = "start" if dr == "U" else "end"
                tw = len(n) * CHAR
                y0r, y1r = (py + dy - 5 - tw, py + dy - 5) if dr == "U" else (py + dy + 5, py + dy + 5 + tw)
                R.soft_rect(px - 6, y0r, px + 4, y1r, 30)
            terminals.append(tm)
        route_pins.pop(n)

    # data nets first (straight), then feedback, then clocks
    def cat(n):
        roles_here = [r for _, _, r in net_pins.get(n, [])]
        if any(r == "clk" for r in roles_here):
            return 2
        if any(p[2] in "UD" for p in route_pins[n]):
            return 1
        return 0

    order = sorted(route_pins, key=lambda n: (cat(n), _spread(route_pins[n]), n))
    warnings = []
    for n in order:
        P = route_pins[n]
        if len(P) < 2:
            if P:
                terminals.append(_terminal(n, P[0][0], P[0][1], P[0][2], n in ports))
            continue
        failed = R.route_net(n, P)
        for fx, fy in failed:
            dr = next(p[2] for p in P if p[0] == fx and p[1] == fy)
            warnings.append(f"{n}: ({fx},{fy}) 핀은 배선 불가 - 이름표로 연결")
            terminals.append(_terminal(n, fx, fy, dr, False, by_label=True))
        if failed:
            labels.append(_wire_label(R, n, "lbl-port", force=True))

    for n in order:
        if len(route_pins[n]) >= 2 and n not in ports:
            lab = _wire_label(R, n, "lbl-net", others=labels, symbols=symbols)
            if lab:
                labels.append(lab)

    wires, dots = [], []
    for n in R.edges:
        for s in R.segments(n):
            wires.append({"net": n, "x1": s[0], "y1": s[1], "x2": s[2], "y2": s[3]})
        for (x, y) in R.junctions(n):
            dots.append({"net": n, "x": x, "y": y})
    _place_instance_labels(symbols, wires, terminals, labels)
    sc = {
        "cell": cell["name"], "kind": "block", "title": cell["name"],
        "symbols": symbols, "pins": pin_list, "wires": wires, "dots": dots,
        "labels": [l for l in labels if l], "rails": rails_out, "terminals": terminals,
        "warnings": warnings, "ports": ports, "bounds": bounds,
        "meta": {"layers": layer, "feedback": sorted(f"{a}.{b}" for a, b in fb)},
    }
    sc["bounds"] = fit_bounds(sc)
    return sc


def _text_boxes_of(symbols, terminals, labels):
    boxes = []
    for s in symbols:
        for p in s["prims"]:
            if p[0] == "text":
                cls = p[4].split()[0]
                boxes.append(text_box(p[3], p[1], p[2], p[5] if len(p) > 5 else "middle", FONT.get(cls, 10)))
        for (lx, ly, parts, anc) in s["labels"]:
            boxes.append(text_box("".join(t for t, _ in parts), lx, ly, anc, FONT["devlbl"]))
    for t in terminals:
        boxes.append(text_box(t["net"], t["tx"], t["ty"], t["anchor"], FONT["term-t"], t.get("rot", False)))
    for l in labels:
        if l:
            boxes.append(text_box(l["text"], l["x"], l["y"], l["anchor"], FONT["netlabel"]))
    return boxes


def _place_instance_labels(symbols, wires, terminals, labels):
    """Put each 'inst : cell' label on the first side of its symbol where it touches
    no other text, wire or symbol (rule 16: no overlapping text)."""
    segs = [(w["x1"], w["y1"], w["x2"], w["y2"]) for w in wires]
    for s in symbols:   # symbol outlines and pin leads are obstacles too
        for p in s["prims"]:
            if p[0] == "line":
                segs.append(p[1:5])
            elif p[0] in ("polyline", "poly"):
                pts = list(p[1]) + ([p[1][0]] if p[0] == "poly" else [])
                segs += [(a[0], a[1], c[0], c[1]) for a, c in zip(pts, pts[1:])]
    bodies = [s.get("body") or s["bbox"] for s in symbols]
    for s in symbols:
        if "label_parts" not in s:
            continue
        txt = "".join(t for t, _ in s["label_parts"])
        x0, y0, x1, y1 = s["bbox"]
        bx0, by0, bx1, by1 = s["body"]
        cx = (bx0 + bx1) / 2
        cands = [(cx, by1 + 16, "middle"), (cx, by0 - 8, "middle"),
                 (bx1 + 6, by1 + 14, "start"), (bx0 - 6, by1 + 14, "end"),
                 (bx1 + 6, by0 - 6, "start"), (bx0 - 6, by0 - 6, "end"),
                 (cx, y1 + 16, "middle"), (cx, y0 - 8, "middle"),
                 (x1 + 6, y1 + 14, "start"), (x0 - 6, y0 - 6, "end")]
        others = _text_boxes_of(symbols, terminals, labels)
        best = None
        for i, (lx, ly, anc) in enumerate(cands):
            b = text_box(txt, lx, ly, anc, FONT["devlbl"])
            bb = (b[0] - 2, b[1] - 2, b[2] + 2, b[3] + 2)
            score = sum(100 for o in others if _ov(bb, o))
            score += sum(60 for g in segs if _seg_hits_rect(g, bb))
            score += sum(60 for bd in bodies if _ov(bb, bd))
            if best is None or score < best[0]:
                best = (score, lx, ly, anc)
            if score == 0:
                break
        s["labels"] = [(best[1], best[2], s["label_parts"], best[3])]


def _spread(P):
    return (max(p[0] for p in P) - min(p[0] for p in P)) + (max(p[1] for p in P) - min(p[1] for p in P))
