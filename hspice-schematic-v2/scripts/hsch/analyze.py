"""Circuit analysis on the parsed IR:
  * supply / ground net detection
  * port direction (in / out / clk / bias / power / ground)
  * automatic block extraction for cells that mix primitives and subckt instances
  * topology recognition -> block class + symbol
"""

import copy
import re

SUPPLY_RE = re.compile(r"^(a|d)?(vdd|vcc|vpwr|vdda|vddd|vddh|vddl)\w*$", re.I)
GROUND_RE = re.compile(r"^((a|d)?(vss|gnd|vgnd|vssa|vssd)\w*|0)$", re.I)
CLK_RE = re.compile(r"(^|_)(clk|ck|clock|phi|ph)\w*$|^(clk|ck)", re.I)
BIAS_RE = re.compile(r"^(vb|vbias|bias|vref|ibias|iref|vcm|vbn|vbp)|bias", re.I)

PRIMITIVE_KINDS = set("MRCLVIEGFHDQ")


def is_supply(n):
    return bool(SUPPLY_RE.match(n))


def is_ground(n):
    return bool(GROUND_RE.match(n))


def is_rail(n):
    return is_supply(n) or is_ground(n)


def pin_map(dev):
    return {p: n for p, n in dev["pins"]}


# ---------------------------------------------------------------------------
# differential naming:  INP/INN, OUTP/OUTN, DP/DN, X_P/X_N, VIN+/VIN-
# ---------------------------------------------------------------------------
_DIFF_RE = re.compile(r"^(.*?)(_?)(p|n|plus|minus|\+|-)$", re.I)


def diff_partner(name, nets):
    m = _DIFF_RE.match(name)
    if not m or not m.group(1):
        return None, None
    base, sep, suf = m.groups()
    low = suf.lower()
    swap = {"p": "n", "n": "p", "plus": "minus", "minus": "plus", "+": "-", "-": "+"}[low]
    cand = base + sep + (swap.upper() if suf.isupper() else swap)
    lut = {x.lower(): x for x in nets}
    other = lut.get(cand.lower())
    if other is None:
        return None, None
    pol = "+" if low in ("p", "plus", "+") else "-"
    return other, pol


def polarity(name, nets):
    _, pol = diff_partner(name, nets)
    return pol


# ---------------------------------------------------------------------------
# port roles
# ---------------------------------------------------------------------------
def port_roles(ir):
    """returns {cell: {port: role}} ; role in in/out/clk/bias/power/ground/inout"""
    memo = {}

    def roles(cname):
        if cname in memo:
            return memo[cname]
        memo[cname] = {}
        cell = ir["cells"][cname]
        conn = {p: [] for p in cell["ports"]}
        for d in cell["devices"]:
            sub = roles(d["ref"]) if d["kind"] == "X" and d["ref"] in ir["cells"] else None
            for pin, net in d["pins"]:
                if net not in conn:
                    continue
                if d["kind"] == "M":
                    conn[net].append("ds" if pin in ("d", "s") else ("g" if pin == "g" else "b"))
                elif d["kind"] == "X":
                    conn[net].append("sub:" + (sub.get(pin, "inout") if sub else "inout"))
                elif d["kind"] in "VEGFH" and pin in ("p", "n"):
                    conn[net].append("drv")
                else:
                    conn[net].append("pass")
        out = {}
        for p, kinds in conn.items():
            if is_supply(p):
                out[p] = "power"
                continue
            if is_ground(p):
                out[p] = "ground"
                continue
            subs = [k[4:] for k in kinds if k.startswith("sub:")]
            if "ds" in kinds or "drv" in kinds or "out" in subs:
                r = "out"
            elif "g" in kinds or any(s in ("in", "clk", "bias") for s in subs):
                r = "in"
                if subs and all(s == "clk" for s in subs) and "g" not in kinds:
                    r = "clk"
                elif subs and all(s == "bias" for s in subs) and "g" not in kinds:
                    r = "bias"
            elif any(s in ("power", "ground") for s in subs):
                r = "power" if "power" in subs else "ground"
            else:
                r = "inout"
            if r == "in":
                if BIAS_RE.search(p):
                    r = "bias"
                elif CLK_RE.search(p):
                    r = "clk"
            out[p] = r
        memo[cname] = out
        return out

    for c in ir["cells"]:
        roles(c)
    return memo


# ---------------------------------------------------------------------------
# automatic blocks
# ---------------------------------------------------------------------------
def _channel_nets(d):
    pm = pin_map(d)
    if d["kind"] == "M":
        return [pm["d"], pm["s"]]
    if d["kind"] in "EG":
        return [pm["p"], pm["n"]]
    return [n for p, n in d["pins"]]


def extract_auto_blocks(ir):
    """For every cell that contains both subckt instances and primitives, move each
    channel-connected group of primitives into a new cell and instantiate it.
    Returns a new IR; original device names are kept inside the new cells."""
    ir = copy.deepcopy(ir)
    new_cells = {}
    for cname, cell in list(ir["cells"].items()):
        prims = [d for d in cell["devices"] if d["kind"] in PRIMITIVE_KINDS]
        insts = [d for d in cell["devices"] if d["kind"] == "X"]
        if not prims or not insts:
            continue
        # union-find over primitives joined through non-rail channel nets
        parent = list(range(len(prims)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        by_net = {}
        for i, d in enumerate(prims):
            for n in _channel_nets(d):
                if is_rail(n):
                    continue
                by_net.setdefault(n, []).append(i)
        for ids in by_net.values():
            for j in ids[1:]:
                parent[find(j)] = find(ids[0])
        groups = {}
        for i in range(len(prims)):
            groups.setdefault(find(i), []).append(prims[i])
        # nets used outside each group
        used_outside = {}
        for d in cell["devices"]:
            for _, n in d["pins"]:
                used_outside.setdefault(n, set()).add(id(d))
        kept = [d for d in cell["devices"] if d["kind"] == "X"]
        k = -1
        for _, devs in sorted(groups.items(), key=lambda kv: min(d["line"] or 0 for d in kv[1])):
            if len(devs) == 1 and devs[0]["kind"] in "RCL":
                kept.append(devs[0])   # a lone R/C/L is drawn as itself in the block view
                continue
            k += 1
            ids = {id(d) for d in devs}
            nets = []
            for d in devs:
                for p, n in d["pins"]:
                    if n not in nets:
                        nets.append(n)
            ports = [n for n in nets
                     if n in cell["ports"] or is_rail(n) or (used_outside.get(n, set()) - ids)]
            order = {p: i for i, p in enumerate(cell["ports"])}
            ports.sort(key=lambda n: (order.get(n, 10_000), nets.index(n)))
            sub = f"{cname}__AUTO{k}"
            new_cells[sub] = {"name": sub, "ports": ports, "params": {}, "devices": devs,
                              "auto": True, "parent": cname}
            kept.append({"name": f"XAUTO{k}", "kind": "X", "type": "inst", "ref": sub,
                         "pins": [[p, p] for p in ports], "model": None, "params": {},
                         "line": min(d["line"] or 0 for d in devs), "auto": True})
        kept.sort(key=lambda d: d.get("line") or 0)
        cell["devices"] = kept
    ir["cells"].update(new_cells)
    return ir


def flatten(ir, cname, prefix=""):
    """Flatten to primitives. Returns {flat_dev_name: {pin: flat_net}} with the
    *original* hierarchical device names (auto blocks are transparent)."""
    out = {}
    glob = {g.lower() for g in ir.get("globals", [])}

    def rec(cn, path, portmap):
        cell = ir["cells"][cn]

        def res(n):
            if n in portmap:
                return portmap[n]
            if is_rail(n) or n.lower() in glob:
                return n
            return path + n

        for d in cell["devices"]:
            if d["kind"] == "X" and d["ref"] in ir["cells"]:
                seg = path if d.get("auto") else path + d["name"] + "/"
                rec(d["ref"], seg, {p: res(n) for p, n in d["pins"]})
            else:
                out[path + d["name"]] = {p: res(n) for p, n in d["pins"]}

    rec(cname, prefix, {})
    return out


# ---------------------------------------------------------------------------
# topology recognition
# ---------------------------------------------------------------------------
def _size(d):
    p = d["params"]
    return (str(p.get("w", "")).lower(), str(p.get("l", "")).lower())


def features(cell):
    mos = [d for d in cell["devices"] if d["kind"] == "M"]
    pm = {d["name"]: pin_map(d) for d in cell["devices"]}
    f = {"diff_pairs": [], "cross_coupled": [], "clock_pairs": [], "degen": [],
         "res_loads": [], "inverters": [], "n_mos": len(mos)}
    for i, a in enumerate(mos):
        for b in mos[i + 1:]:
            if a["type"] != b["type"]:
                continue
            A, B = pm[a["name"]], pm[b["name"]]
            same_src = A["s"] == B["s"] and not is_rail(A["s"])
            if same_src and A["g"] == B["d"] and B["g"] == A["d"]:
                f["cross_coupled"].append((a["name"], b["name"]))
            elif same_src and A["d"] != B["d"] and A["g"] != B["g"]:
                if CLK_RE.search(A["g"]) and CLK_RE.search(B["g"]):
                    f["clock_pairs"].append((a["name"], b["name"]))
                else:
                    f["diff_pairs"].append((a["name"], b["name"], A["s"]))
            elif (_size(a) == _size(b) and A["s"] != B["s"] and not is_rail(A["s"]) and not is_rail(B["s"])
                  and A["d"] != B["d"]):
                for d in cell["devices"]:
                    if d["kind"] in "RC" and set(n for _, n in d["pins"]) == {A["s"], B["s"]}:
                        f["degen"].append((a["name"], b["name"], d["name"], d["kind"]))
    for d in cell["devices"]:
        if d["kind"] == "R":
            nets = [n for _, n in d["pins"]]
            if any(is_supply(n) for n in nets):
                f["res_loads"].append(d["name"])
    for a in mos:
        for b in mos:
            if a["type"] == "nmos" and b["type"] == "pmos":
                A, B = pm[a["name"]], pm[b["name"]]
                if A["g"] == B["g"] and A["d"] == B["d"] and is_ground(A["s"]) and is_supply(B["s"]):
                    f["inverters"].append((a["name"], b["name"]))
    return f


def _gate_topology(cell):
    """2+-input static CMOS NAND / NOR: one network parallel, the dual in series."""
    mos = [d for d in cell["devices"] if d["kind"] == "M"]
    if len(mos) != len(cell["devices"]):
        return None
    n = [pin_map(d) for d in mos if d["type"] == "nmos"]
    p = [pin_map(d) for d in mos if d["type"] == "pmos"]
    if len(n) != len(p) or len(n) < 2:
        return None
    if {d["g"] for d in n} != {d["g"] for d in p} or len({d["g"] for d in n}) != len(n):
        return None
    par_p = all(is_supply(d["s"]) for d in p) and len({d["d"] for d in p}) == 1
    par_n = all(is_ground(d["s"]) for d in n) and len({d["d"] for d in n}) == 1
    ser_n = sum(1 for d in n if is_ground(d["s"])) == 1
    ser_p = sum(1 for d in p if is_supply(d["s"])) == 1
    if par_p and ser_n:
        return "nand"
    if par_n and ser_p:
        return "nor"
    return None


NAME_HINTS = [
    (re.compile(r"nand", re.I), "nand"),
    (re.compile(r"xor", re.I), "xor"),
    (re.compile(r"(^|_)nor\d*($|_)", re.I), "nor"),
    (re.compile(r"(^|_)and\d*($|_)", re.I), "and"),
    (re.compile(r"(^|_)or\d*($|_)", re.I), "or"),
    (re.compile(r"ctle|equali[sz]", re.I), "ctle"),
    (re.compile(r"latch", re.I), "latch"),
    (re.compile(r"dff|flop|(^|_)ff(_|$)", re.I), "dff"),
    (re.compile(r"sum", re.I), "summer"),
    (re.compile(r"dfe", re.I), "dfe"),
    (re.compile(r"mux", re.I), "mux"),
    (re.compile(r"inv", re.I), "inverter"),
    (re.compile(r"buf|drv|driver", re.I), "buffer"),
    (re.compile(r"ota|opamp|amp", re.I), "amplifier"),
    (re.compile(r"comp", re.I), "comparator"),
]

CLASS_SYMBOL = {
    "ctle": ("amp", "CTLE"),
    "buffer": ("amp", ""),
    "diff_buffer": ("amp", ""),
    "amplifier": ("amp", ""),
    "comparator": ("amp", "CMP"),
    "inverter": ("inv", ""),
    "summer": ("sum", ""),
    "latch": ("latch", "LATCH"),
    "dff": ("dff", "DFF"),
    "mux": ("mux", "MUX"),
    "dfe": ("box", "DFE"),
    "nand": ("nand", ""), "and": ("and", ""), "nor": ("nor", ""), "or": ("or", ""), "xor": ("xor", ""),
    "generic": ("box", None),
}

CLASS_TITLE = {
    "ctle": "CTLE", "buffer": "Buffer", "diff_buffer": "Diff. buffer", "amplifier": "Amplifier",
    "comparator": "Comparator", "inverter": "Inverter", "summer": "Summer", "latch": "Latch",
    "dff": "D flip-flop", "mux": "MUX", "dfe": "DFE", "generic": "Block",
    "nand": "NAND", "and": "AND", "nor": "NOR", "or": "OR", "xor": "XOR",
}


def classify(ir, cname, cache=None):
    cache = {} if cache is None else cache
    if cname in cache:
        return cache[cname]
    cell = ir["cells"][cname]
    insts = [d for d in cell["devices"] if d["kind"] == "X"]
    reason = []
    cls = None
    if not cell.get("auto"):
        for rx, c in NAME_HINTS:
            if rx.search(cname):
                cls = c
                reason.append(f"name '{cname}'")
                break
    topo = None
    if not insts:
        f = features(cell)
        if f["cross_coupled"] and (f["clock_pairs"] or f["diff_pairs"]):
            topo = "latch"
            reason.append("cross-coupled pair + steering pairs")
        elif f["degen"] and f["diff_pairs"] == [] and f["res_loads"]:
            topo = "ctle"
            reason.append("source-degenerated pair (R/C between sources) with loads")
        elif len(f["diff_pairs"]) >= 2:
            drains = {}
            pm = {d["name"]: pin_map(d) for d in cell["devices"]}
            for a, b, _ in f["diff_pairs"]:
                key = frozenset((pm[a]["d"], pm[b]["d"]))
                drains[key] = drains.get(key, 0) + 1
            if max(drains.values()) >= 2:
                topo = "summer"
                reason.append("several diff pairs summing into the same drains")
        if topo is None:
            topo = _gate_topology(cell)
            if topo:
                reason.append(f"series/parallel CMOS network ({topo.upper()})")
        if topo is None and f["diff_pairs"]:
            topo = "diff_buffer"
            reason.append("differential pair")
        if topo is None and f["inverters"]:
            topo = "inverter" if len(f["inverters"]) == 1 else "buffer"
            reason.append("CMOS inverter(s)")
    else:
        subs = [classify(ir, d["ref"], cache)["class"] for d in insts if d["ref"] in ir["cells"]]
        if len(subs) == 2 and all(s == "latch" for s in subs):
            topo = "dff"
            reason.append("two latches in series (master/slave)")
    if cls is None:
        cls = topo or "generic"
    elif topo and topo != cls:
        reason.append(f"(topology suggests {topo})")
    shape, title = CLASS_SYMBOL.get(cls, ("box", None))
    res = {"class": cls, "shape": shape, "title": title if title is not None else cname,
           "label": CLASS_TITLE.get(cls, cls), "reason": "; ".join(reason) or "no pattern"}
    cache[cname] = res
    return res


def classify_all(ir, overrides=None):
    cache = {}
    out = {c: classify(ir, c, cache) for c in ir["cells"]}
    for c, ov in (overrides or {}).get("cells", {}).items():
        if c in out:
            out[c].update({k: v for k, v in ov.items() if k in ("class", "shape", "title", "label")})
            if "class" in ov and "shape" not in ov:
                out[c]["shape"], t = CLASS_SYMBOL.get(ov["class"], ("box", None))
                out[c].setdefault("title", t)
    return out
