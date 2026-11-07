"""Verify a rendered schematic against the netlist.

1. Connectivity ("LVS of the drawing"): connectivity is rebuilt only from what is drawn
   - wire geometry, pin positions, junctions and name labels - exactly the way a
   person reads a schematic, then compared pin-by-pin with the IR.
     * wires touching end-to-end or end-on-interior (T) are connected
     * wires crossing interior-to-interior are NOT connected
     * a pin connects to the wire that touches it
     * a name label (port tag, net label, rail glyph) connects everything with the same name
   The data-net attributes in the SVG are NOT used for extraction.
2. Visual lint: crossings, T-junctions without dots, 4-way junctions, wires through
   symbols, overlapping labels, PMOS-above-NMOS, rails top/bottom.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser

from .analyze import is_ground, is_supply



FONT = {"devlbl": 9, "netlabel": 10, "term-t": 10, "pin-t": 9, "blk-t": 13, "sum-t": 22,
        "pol-t": 12, "rail-t": 10, "sym-t": 10}


def text_width(txt, size, latin=0.58):
    """estimated rendered width: Hangul / CJK glyphs are about 1 em wide"""
    return sum((1.0 if ord(ch) >= 0x1100 else latin) for ch in txt) * size


def text_box(txt, x, y, anchor, size, rot=False):
    w = text_width(txt, size)
    if rot:  # rotate(-90) about (x, y): text runs upward for anchor=start
        y0 = y - w if anchor == "start" else (y if anchor == "end" else y - w / 2)
        return (x - size * 0.8, y0, x + size * 0.2, y0 + w)
    x0 = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
    return (x0, y - size * 0.75, x0 + w, y + size * 0.2)


class _P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.views = {}
        self.cur = None
        self.gstack = []
        self.text = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if tag == "svg" and "sch" in cls:
            self.cur = {"wires": [], "pins": [], "dots": [], "names": [], "symbols": [], "texts": []}
            self.views[a["data-cell"]] = self.cur
            self.gstack = []
            return
        v = self.cur
        if v is None:
            return
        if tag == "g":
            ctx = {"cls": cls, "a": a, "sym": None, "name": ""}
            if "symg" in cls:
                keep = []
                for r in (a.get("data-keep") or "").split(";"):
                    if r:
                        keep.append(tuple(float(x) for x in r.split(",")))
                body = tuple(float(x) for x in a["data-body"].split(",")) if a.get("data-body") else None
                v["symbols"].append({"inst": a["data-inst"], "type": a.get("data-type"), "keep": keep,
                                     "hidden": [h for h in (a.get("data-hidden") or "").split(",") if h],
                                     "ref": a.get("data-ref"), "body": body})
                ctx["sym"] = len(v["symbols"]) - 1
            elif "rail" in cls:
                v["names"].append(("rail", a["data-net"], float(a["data-ax"]), float(a["data-ay"])))
            self.gstack.append(ctx)
        elif tag == "line" and "wire" in cls:
            v["wires"].append(tuple(float(a[k]) for k in ("x1", "y1", "x2", "y2")))
        elif tag in ("line", "polyline", "polygon") and any(g["sym"] is not None for g in self.gstack):
            sym = next(g["sym"] for g in reversed(self.gstack) if g["sym"] is not None)
            if tag == "line":
                pts = [(float(a["x1"]), float(a["y1"])), (float(a["x2"]), float(a["y2"]))]
            else:
                pts = [tuple(float(c) for c in p.split(",")) for p in a["points"].split()]
                if tag == "polygon":
                    pts.append(pts[0])
            for p, q in zip(pts, pts[1:]):
                v.setdefault("symsegs", []).append((p[0], p[1], q[0], q[1], sym))
        elif tag == "circle" and "pin" in cls:
            v["pins"].append((a["data-inst"], a["data-pin"], float(a["cx"]), float(a["cy"])))
        elif tag == "circle" and "dot" in cls:
            v["dots"].append((float(a["cx"]), float(a["cy"])))
        elif tag == "text":
            kind = next((k for k in FONT if k in cls), "sym-t")
            sym = next((g["sym"] for g in reversed(self.gstack) if g["sym"] is not None), None)
            self.text = {"kind": kind, "cls": cls, "x": float(a.get("x", 0)), "y": float(a.get("y", 0)),
                         "anchor": a.get("text-anchor", "start"),
                         "rot": bool(a.get("data-rot")) or "rotate" in (a.get("transform") or ""),
                         "txt": "", "sym": sym, "a": a}

    def handle_data(self, data):
        if self.text is not None:
            self.text["txt"] += data

    def handle_endtag(self, tag):
        v = self.cur
        if v is None:
            return
        if tag == "svg":
            self.cur = None
            return
        if tag == "text" and self.text is not None:
            t = self.text
            self.text = None
            txt = t["txt"].strip()
            box = text_box(txt, t["x"], t["y"], t["anchor"], FONT[t["kind"]], t["rot"])
            v["texts"].append({"txt": txt, "box": box, "kind": t["kind"], "sym": t["sym"]})
            if t["kind"] == "netlabel":
                v["names"].append(("label", txt, float(t["a"]["data-ax"]), float(t["a"]["data-ay"])))
            elif t["kind"] == "term-t" and self.gstack and "term" in self.gstack[-1]["cls"]:
                self.gstack[-1]["name"] = txt
        elif tag == "g" and self.gstack:
            g = self.gstack.pop()
            if "term" in g["cls"]:
                v["names"].append(("term", g["name"], float(g["a"]["data-ax"]), float(g["a"]["data-ay"])))


def parse_html(path):
    p = _P()
    with open(path, encoding="utf-8") as f:
        p.feed(f.read())
    return p.views


# ---------------------------------------------------------------------------
class UF:
    def __init__(self):
        self.p = {}

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def u(self, a, b):
        ra, rb = self.f(a), self.f(b)
        if ra != rb:
            self.p[ra] = rb


def _on(seg, x, y, eps=0.5):
    """point on segment (any direction)"""
    x1, y1, x2, y2 = seg
    if not (min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps):
        return False
    L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1.0
    return abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) / L < eps


def _cross(a, b):
    """True if two segments cross at a point interior to both."""
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(d) < 1e-9:
        return False
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    return 1e-6 < t < 1 - 1e-6 and 1e-6 < u < 1 - 1e-6


def _is_end(seg, x, y, eps=0.5):
    return (abs(seg[0] - x) < eps and abs(seg[1] - y) < eps) or (abs(seg[2] - x) < eps and abs(seg[3] - y) < eps)


def extract(view):
    """Return (groups, info): groups maps ('pin', inst, pin) -> group id."""
    uf = UF()
    W = view["wires"]
    for i in range(len(W)):
        uf.f(("w", i))
    # point index: every endpoint + pin + name anchor
    pts = set()
    for s in W:
        pts.add((s[0], s[1]))
        pts.add((s[2], s[3]))
    for _, _, x, y in view["pins"]:
        pts.add((x, y))
    for _, _, x, y in view["names"]:
        pts.add((x, y))
    junction_info = {}
    for (x, y) in pts:
        ends = [i for i, s in enumerate(W) if _is_end(s, x, y)]
        inter = [i for i, s in enumerate(W) if not _is_end(s, x, y) and _on(s, x, y)]
        if ends:
            for i in ends[1:] + inter:
                uf.u(("w", ends[0]), ("w", i))
        junction_info[(x, y)] = (ends, inter)
    pin_on_interior = []
    for inst, pin, x, y in view["pins"]:
        key = ("pin", inst, pin)
        uf.f(key)
        ends, inter = junction_info[(x, y)]
        for i in ends + inter:
            uf.u(key, ("w", i))
        if inter and not ends:
            pin_on_interior.append(f"{inst}.{pin}")
    # pins touching pins directly
    by_pt = {}
    for inst, pin, x, y in view["pins"]:
        by_pt.setdefault((x, y), []).append(("pin", inst, pin))
    for lst in by_pt.values():
        for k in lst[1:]:
            uf.u(lst[0], k)
    dangling = []
    for kind, name, x, y in view["names"]:
        key = ("name", name)
        uf.f(key)
        ends, inter = junction_info[(x, y)]
        touched = [("w", i) for i in ends + inter] + by_pt.get((x, y), [])
        if not touched:
            dangling.append(f"이름표 '{name}' ({x:g},{y:g})이(가) 아무것에도 닿지 않음")
        for t in touched:
            uf.u(key, t)
    groups = {}
    for inst, pin, x, y in view["pins"]:
        groups[(inst, pin)] = uf.f(("pin", inst, pin))
    names = {}
    for kind, name, x, y in view["names"]:
        names.setdefault(uf.f(("name", name)), set()).add(name)
    return groups, {"pin_on_interior": pin_on_interior, "dangling": dangling, "names": names,
                    "junctions": junction_info, "uf": uf}


def check_view(view, cell, roles):
    errors, lint = [], []
    groups, info = extract(view)
    errors += info["dangling"]
    hidden = {s["inst"]: set(s["hidden"]) for s in view["symbols"]}
    ir_pin_net = {}
    for d in cell["devices"]:
        for p, n in d["pins"]:
            if d["kind"] == "M" and p == "b":
                continue
            if p in hidden.get(d["name"], set()):
                if not (is_supply(n) or is_ground(n)):
                    errors.append(f"{d['name']}.{p}: 숨긴 핀인데 넷 {n}은 전원이 아님")
                continue
            ir_pin_net[(d["name"], p)] = n
    for (inst, pin) in groups:
        if inst == "PORT":
            ir_pin_net.setdefault((inst, pin), pin)
    drawn = set(groups)
    for k in ir_pin_net:
        if k not in drawn:
            errors.append(f"핀 {k[0]}.{k[1]}이(가) 그려지지 않음")
    for k in drawn:
        if k not in ir_pin_net:
            errors.append(f"그려진 핀 {k[0]}.{k[1]}이(가) netlist에 없음")
    net_groups, group_nets = {}, {}
    for k, n in ir_pin_net.items():
        if k not in groups:
            continue
        g = groups[k]
        net_groups.setdefault(n, set()).add(g)
        group_nets.setdefault(g, set()).add(n)
    for n, gs in net_groups.items():
        if len(gs) > 1:
            parts = []
            for g in gs:
                parts.append("{" + ", ".join(sorted(f"{i}.{p}" for (i, p), gg in groups.items() if gg == g and ir_pin_net.get((i, p)) == n)) + "}")
            errors.append(f"끊김(OPEN): 넷 {n}이(가) {len(gs)}조각으로 그려짐: " + " | ".join(parts))
    for g, ns in group_nets.items():
        if len(ns) > 1:
            errors.append(f"단락(SHORT): 넷 {', '.join(sorted(ns))}이(가) 그림에서 이어져 있음")
    for g, labelset in info["names"].items():
        ns = group_nets.get(g, set())
        for lab in labelset:
            if ns and lab not in ns:
                errors.append(f"이름표 '{lab}'이(가) 넷 {', '.join(sorted(ns))} 위에 있음")
    # every port must be visible (pin tag, port symbol, label or rail)
    seen_names = set().union(*info["names"].values()) if info["names"] else set()
    for p in cell["ports"]:
        if p in seen_names:
            continue
        if p in net_groups and all(ip[0] == "PORT" for ip in ir_pin_net if ir_pin_net[ip] == p) is False:
            pass
        hidden_only = all(k[1] in hidden.get(k[0], set()) for k in
                          [(d["name"], pp) for d in cell["devices"] for pp, nn in d["pins"] if nn == p])
        if (is_supply(p) or is_ground(p)) and hidden_only:
            continue
        if not any(n == p for n in net_groups):
            if hidden_only:
                continue
        errors.append(f"포트 {p}이(가) 그림 어디에도 없음")

    # ---------------- lint ----------------
    W = view["wires"]
    crossings = 0
    for i in range(len(W)):
        for j in range(i + 1, len(W)):
            if _cross(W[i], W[j]):
                crossings += 1
    dots = set(view["dots"])
    for (x, y), (ends, inter) in info["junctions"].items():
        pins_here = sum(1 for _, _, px, py in view["pins"] if px == x and py == y)
        branches = len(ends) + 2 * len(inter) + pins_here
        if branches >= 4 and (len(inter) >= 2 or len(ends) + pins_here >= 4 or (inter and len(ends) + pins_here >= 2)):
            lint.append(f"({x:g},{y:g})에 4방향 접점")
        if branches == 3 and (x, y) not in dots:
            lint.append(f"({x:g},{y:g}) T 접점에 점 없음")
    for (x, y) in dots:
        ends, inter = info["junctions"].get((x, y), ([], []))
        pins_here = sum(1 for _, _, px, py in view["pins"] if px == x and py == y)
        if len(ends) + 2 * len(inter) + pins_here < 3:
            lint.append(f"({x:g},{y:g})의 점이 접점이 아님")
    for s in view["symbols"]:
        for (x0, y0, x1, y1) in s["keep"]:
            for w in W:
                if _seg_hits_rect(w, (x0 + 1, y0 + 1, x1 - 1, y1 - 1)):
                    lint.append(f"배선이 {s['inst']}을(를) 관통")
                    break
    lint += [f"pin {p} lands on the middle of a wire" for p in info["pin_on_interior"]]
    T = view["texts"]
    over = 0
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            if _ov(_shrink(T[i]["box"]), _shrink(T[j]["box"])):
                over += 1
                lint.append(f"글씨 겹침: '{T[i]['txt']}' / '{T[j]['txt']}'")
    for t in T:
        b = _shrink(t["box"], 1.5)
        for w in W:
            if _seg_hits_rect(w, b):
                over += 1
                lint.append(f"글씨 '{t['txt']}'이(가) 배선과 겹침")
                break
        for sg in view.get("symsegs", []):
            if _seg_hits_rect(sg[:4], b):
                over += 1
                lint.append(f"글씨 '{t['txt']}'이(가) {view['symbols'][sg[4]]['inst']} 그림과 겹침")
                break
        for k, s_ in enumerate(view["symbols"]):
            body = s_.get("body")
            if not body:
                continue
            inside = body[0] <= b[0] and b[2] <= body[2] and body[1] <= b[1] and b[3] <= body[3]
            if inside and t["sym"] == k:
                continue
            if _ov(b, body):
                over += 1
                lint.append(f"글씨 '{t['txt']}'이(가) 심볼 {s_['inst']}과(와) 겹침")
    # rule 1: sigma-matched pairs must be drawn as mirror images
    from .layout_leaf import _symmetry
    from .analyze import pin_map as _pm
    if not any(d["kind"] == "X" for d in cell["devices"]):
        devs = cell["devices"]
        pmap = {d["name"]: _pm(d) for d in devs}
        nets = sorted({n for d in devs for _, n in d["pins"]})
        rails = [n for n in nets if is_supply(n) or is_ground(n)]
        sig = _symmetry(devs, pmap, cell["ports"], nets, rails)["dev"]
        P = {}
        for inst, pin, x, y in view["pins"]:
            P.setdefault(inst, {})[pin] = (x, y)
        seen = set()
        for a, b in sig.items():
            if a == b or (b, a) in seen or a not in P or b not in P:
                continue
            seen.add((a, b))
            pa, pb = P[a], P[b]
            ya = sorted(y for _, y in pa.values())
            yb = sorted(y for _, y in pb.values())
            if ya != yb:
                lint.append(f"쌍 {a}/{b}의 높이가 다름")
                continue
            if "g" in pa and "g" in pb:
                ca = [x for p, (x, _) in pa.items() if p != "g"][0]
                cb = [x for p, (x, _) in pb.items() if p != "g"][0]
                if abs((pa["g"][0] - ca) + (pb["g"][0] - cb)) > 0.5:
                    lint.append(f"쌍 {a}/{b}이(가) 대칭으로 그려지지 않음")
    # textbook conventions
    ys = {"pmos": [], "nmos": []}
    for d in cell["devices"]:
        if d["kind"] == "M":
            pts = [p for p in view["pins"] if p[0] == d["name"]]
            if pts:
                ys[d["type"]].append(sum(p[3] for p in pts) / len(pts))
    if ys["pmos"] and ys["nmos"] and min(ys["pmos"]) > max(ys["nmos"]):
        lint.append("PMOS가 NMOS보다 아래에 그려짐")
    return {"ok": not errors, "errors": errors,
            "lint": {"crossings": crossings, "text_overlaps": over, "warnings": lint}}


def _seg_hits_rect(w, r):
    x0, y0, x1, y1 = r
    if x0 > x1 or y0 > y1:
        return False
    a, b, c, d = w
    n = int(max(abs(c - a), abs(d - b)) // 2) + 1
    for i in range(n + 1):
        t = i / float(n)
        x, y = a + (c - a) * t, b + (d - b) * t
        if x0 < x < x1 and y0 < y < y1:
            return True
    return False


def _ov(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _shrink(b, d=0.5):
    return (b[0] + d, b[1] + d, b[2] - d, b[3] - d)


def verify_html(html_path, ir, roles):
    views = parse_html(html_path)
    report = {}
    for cname, view in views.items():
        cell = ir["cells"][cname]
        report[cname] = check_view(view, cell, roles.get(cname, {}))
    return report


def summarize(report):
    lines = []
    ok = all(r["ok"] for r in report.values())
    for c, r in report.items():
        mark = "PASS" if r["ok"] else "FAIL"
        lines.append(f"[{mark}] {c}: crossings={r['lint']['crossings']} lint={len(r['lint']['warnings'])}")
        for e in r["errors"]:
            lines.append(f"    ERROR {e}")
        for w in r["lint"]["warnings"]:
            lines.append(f"    lint  {w}")
    lines.append("CONNECTIVITY: " + ("ALL VIEWS MATCH NETLIST" if ok else "MISMATCH"))
    return "\n".join(lines), ok
