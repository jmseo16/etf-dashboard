"""Signal classification + same-role device merging (analysis only, no drawing).

1. Net classes, from circuit structure (names only break ties):
     power  supply / ground rails
     bias   gate of current sources (source on a rail), diode-connected mirror
            nodes, passive-only DC nodes (VCM)
     ctrl   gate of switches in series with a current source or across a
            degeneration node: static option / trim codes (IDAC bits, gain, R/C codes)
     clk    clock nets
     hs     everything else carrying signal (diff-pair inputs, CMOS inputs, outputs)
   Classes propagate up the hierarchy through instance pins
   (priority clk > hs > ctrl > bias > power).

2. Same-role merging ("slices"): devices whose names differ only in a number and
   whose pins connect either to the same net in every member or to a different
   net in every member (T_G0..T_G3) form one iterated group, written the Virtuoso
   way: MS_G<0:3>, nets T_G<0:3>, pins G<0:3>. Passives of the same kind between
   the same two nets are merged as a parallel group.
"""
import re

from .analyze import BIAS_RE, CLK_RE, diff_partner, is_ground, is_rail, is_supply, pin_map

PRIORITY = {"clk": 5, "hs": 4, "ctrl": 3, "bias": 2, "power": 1}
DISPLAY_GROUP = {"hs": "high-speed", "clk": "high-speed", "ctrl": "option/control",
                 "bias": "power/bias", "power": "power/bias"}
_DIG = re.compile(r"\d+")


# ---------------------------------------------------------------------------
# 1. classification
# ---------------------------------------------------------------------------
def _mos_role(d, P):
    """cs: source on a rail (current source / CS input / inverter half)
       diode: gate tied to drain   series: channel between two non-rail nets"""
    s, dr = P["s"], P["d"]
    if d["type"] == "pmos":
        src_rail = is_supply(s) or is_supply(dr)
    else:
        src_rail = is_ground(s) or is_ground(dr)
    if P["g"] in (P["d"], P["s"]):
        return "diode"
    return "cs" if src_rail else "series"


def _leaf_classes(cell):
    devs = cell["devices"]
    pm = {d["name"]: pin_map(d) for d in devs}
    conns = {}
    for d in devs:
        for p, n in d["pins"]:
            if d["kind"] == "M" and p == "b":
                continue
            conns.setdefault(n, []).append((d, p))
    role = {d["name"]: _mos_role(d, pm[d["name"]]) for d in devs if d["kind"] == "M"}
    # devices fed by a current source in series (switch in a switched current branch)
    cs_drain_nets = set()
    for d in devs:
        if d["kind"] == "M" and role[d["name"]] == "cs":
            P = pm[d["name"]]
            cs_drain_nets.add(P["d"] if not is_rail(P["d"]) else P["s"])
    out = {}
    nets = list(conns)
    for net in nets:
        C = conns[net]
        gates = [(d, p) for d, p in C if d["kind"] == "M" and p == "g"]
        chan = [(d, p) for d, p in C if not (d["kind"] == "M" and p == "g")]
        if is_rail(net):
            out[net] = "power"
            continue
        if CLK_RE.search(net):
            out[net] = "clk"
            continue
        if not chan:  # only drives gates
            partner, _ = diff_partner(net, nets)
            # a net driving both NMOS and PMOS gates is a CMOS logic input
            complementary = len({d["type"] for d, _ in gates}) == 2
            roles = {role[d["name"]] for d, _ in gates}
            if BIAS_RE.search(net) and not complementary:
                out[net] = "bias"        # VBN / VBP: name wins over the P/N pairing
            elif partner or complementary:
                out[net] = "hs"
            elif roles == {"cs"}:
                out[net] = "bias"
            elif roles <= {"series"} and all(
                    any(x in cs_drain_nets or _is_degen_node(x, conns, pm) for x in (pm[d["name"]]["d"], pm[d["name"]]["s"]))
                    for d, _ in gates):
                out[net] = "ctrl"
            else:
                out[net] = "hs"
            continue
        # nets with channel / passive connections
        diode_here = any(d["kind"] == "M" and role.get(d["name"]) == "diode" and pm[d["name"]]["d"] == net
                         for d, _ in C)
        others = [(d, p) for d, p in chan if not (d["kind"] == "M" and role.get(d["name"]) in ("diode", "cs"))
                  and not (d["kind"] == "C")]
        if diode_here and not others:
            out[net] = "bias"
        elif all(d["kind"] in "RC" for d, _ in chan) and any(
                d["kind"] == "C" and any(is_rail(n) for _, n in d["pins"]) for d, _ in chan) and not gates:
            out[net] = "bias"          # common-mode / decoupled DC node
        elif BIAS_RE.search(net) and not gates:
            out[net] = "bias"
        else:
            out[net] = "hs"
    return out


def _is_degen_node(net, conns, pm):
    """a node that is the source of a signal device and is also fed by a current
    source: switches between two such nodes are degeneration (option) switches"""
    if is_rail(net):
        return False
    has_src = any(d["kind"] == "M" and p == "s" for d, p in conns.get(net, []))
    has_cs = any(d["kind"] == "M" and p == "d" and is_rail(pm[d["name"]]["s"]) for d, p in conns.get(net, []))
    return has_src and has_cs


def classify_signals(ir):
    """returns {cell: {net: class}} for every net of every cell"""
    memo = {}

    def rec(cname):
        if cname in memo:
            return memo[cname]
        cell = ir["cells"][cname]
        insts = [d for d in cell["devices"] if d["kind"] == "X" and d["ref"] in ir["cells"]]
        prims = [d for d in cell["devices"] if d not in insts]
        res = _leaf_classes({"devices": prims}) if prims else {}
        if insts:
            acc = {}
            for d in insts:
                sub = rec(d["ref"])
                for p, n in d["pins"]:
                    c = sub.get(p, "hs")
                    acc.setdefault(n, []).append(c)
            for n, cs in acc.items():
                if is_rail(n):
                    res[n] = "power"
                    continue
                cands = cs + ([res[n]] if n in res else [])
                res[n] = max(cands, key=lambda c: PRIORITY[c])
                if CLK_RE.search(n):
                    res[n] = "clk"
        memo[cname] = res
        return res

    for c in ir["cells"]:
        rec(c)
    # downward pass: an output that only ever feeds clock nets is part of the clock network
    changed = True
    while changed:
        changed = False
        ctx = {}
        for cname, cell in ir["cells"].items():
            for d in cell["devices"]:
                if d["kind"] == "X" and d["ref"] in memo:
                    for p, n in d["pins"]:
                        ctx.setdefault((d["ref"], p), set()).add(memo[cname].get(n, "hs"))
        for (sub, p), cs in ctx.items():
            if cs == {"clk"} and memo[sub].get(p) == "hs":
                memo[sub][p] = "clk"
                changed = True
    return memo


# ---------------------------------------------------------------------------
# 2. same-role merging
# ---------------------------------------------------------------------------
def _tpl(name):
    return _DIG.sub("#", name)


def bus_name(names):
    """['T_G0','T_G1','T_G2','T_G3'] -> 'T_G<0:3>' ; ['W1_0','W2_0'] -> 'W<1:2>_0'"""
    names = list(dict.fromkeys(names))
    if len(names) == 1:
        return names[0]
    parts = [_DIG.findall(n) for n in names]
    if len({len(p) for p in parts}) != 1 or len({_tpl(n) for n in names}) != 1:
        return "{" + ",".join(names) + "}"
    pieces = _DIG.split(names[0])
    nd = len(parts[0])
    vals = [[int(p[k]) for p in parts] for k in range(nd)]
    varying = [k for k in range(nd) if len(set(vals[k])) > 1]
    sets = {k: sorted(set(vals[k])) for k in varying}
    full = 1
    for k in varying:
        full *= len(sets[k])
    grid = (full == len(names) and len({tuple(p[k] for k in varying) for p in parts}) == len(names)
            and all(sets[k] == list(range(sets[k][0], sets[k][-1] + 1)) for k in varying))
    out = pieces[0]
    for k in range(nd):
        if k not in varying:
            out += parts[0][k]
        elif grid:
            out += f"<{sets[k][0]}:{sets[k][-1]}>"
        else:
            out += "<" + ",".join(str(v) for v in vals[k]) + ">"
        out += pieces[k + 1]
    return out if (grid or len(varying) == 1) else "{" + ",".join(names) + "}"


def find_slices(cell):
    """returns a list of merge groups:
       {"kind": "iterated"|"parallel", "name": bus name, "members": [dev names],
        "pins": {pin: bus-or-shared net name}, "sizes": [...]}"""
    devs = [d for d in cell["devices"]]
    groups = {}
    for d in devs:
        pins = tuple((p, _tpl(n)) for p, n in d["pins"] if not (d["kind"] == "M" and p == "b"))
        key = (d["kind"], d["type"], d.get("ref"), _tpl(d["name"]), pins)
        if _DIG.search(d["name"]):
            groups.setdefault(key, []).append(d)
    out, used = [], set()
    for key, mem in groups.items():
        if len(mem) < 2:
            continue
        ok = True
        pinmap = {}
        for p, _ in key[4]:
            nets = [pin_map(d)[p] for d in mem]
            if len(set(nets)) == 1:
                pinmap[p] = nets[0]
            elif len(set(nets)) == len(nets):
                pinmap[p] = bus_name(nets)
            else:
                ok = False
                break
        if not ok:
            continue
        mem = sorted(mem, key=lambda d: [int(x) for x in _DIG.findall(d["name"])])
        out.append({"kind": "iterated", "name": bus_name([d["name"] for d in mem]),
                    "members": [d["name"] for d in mem], "pins": pinmap,
                    "sizes": [_size_text(d) for d in mem], "type": key[1], "ref": key[2]})
        used |= {d["name"] for d in mem}
    # parallel passives between the same two nets (e.g. a degeneration cap bank)
    par = {}
    for d in devs:
        if d["kind"] in "RCL":
            nets = frozenset(n for _, n in d["pins"])
            par.setdefault((d["kind"], nets), []).append(d)
    for (kind, nets), mem in par.items():
        if len(mem) < 2:
            continue
        names = [d["name"] for d in mem]
        absorbed = [g for g in out if g["kind"] == "iterated" and set(g["members"]) <= set(names)]
        label = [g["name"] for g in absorbed] + [n for n in names
                                                  if not any(n in g["members"] for g in absorbed)]
        out = [g for g in out if g not in absorbed]
        out.append({"kind": "parallel", "name": " ∥ ".join(sorted(label, key=len)), "members": names,
                    "pins": dict(zip(("p", "n"), sorted(nets))), "sizes": [_size_text(d) for d in mem],
                    "type": mem[0]["type"], "ref": None})
    return out


def _size_text(d):
    p = d["params"]
    if d["kind"] == "M":
        return f"{p.get('w', '?')}/{p.get('l', '?')}"
    if d["kind"] in "RCL":
        return str(p.get({"R": "r", "C": "c", "L": "l"}[d["kind"]], "?"))
    return d.get("ref") or ""


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def report(ir, classes, order):
    lines = []
    for c in order:
        cell = ir["cells"][c]
        cls = classes[c]
        by = {}
        for p in cell["ports"]:
            by.setdefault(cls.get(p, "?"), []).append(p)
        lines.append(f"\n## {c}" + ("  (auto block)" if cell.get("auto") else ""))
        for k in ("hs", "clk", "ctrl", "bias", "power"):
            if by.get(k):
                lines.append(f"  {k:5s}: {compress(by[k])}")
        for g in find_slices(cell):
            pins = ", ".join(f"{p}={n}" for p, n in g["pins"].items())
            lines.append(f"  MERGE {g['kind']:8s} {g['name']}  x{len(g['members'])}  [{pins}]  sizes {', '.join(g['sizes'])}")
    return "\n".join(lines)


def compress(names):
    """collapse index families into bus notation for display"""
    fam = {}
    for n in names:
        fam.setdefault(_tpl(n), []).append(n)
    out = []
    for t, ns in fam.items():
        out.append(bus_name(ns) if len(ns) > 1 and "#" in t else ", ".join(ns))
    return ", ".join(out)


# ---------------------------------------------------------------------------
# bus helpers used by the display transformation
# ---------------------------------------------------------------------------
_BUS = re.compile(r"<([^<>]+)>")


def is_bus(name):
    return bool(_BUS.search(name)) or (name.startswith("{") and name.endswith("}"))


def expand_bus(name):
    """'W<1:4>_<0:3>' -> W1_0, W1_1, ..., W4_3 (first index outermost);
    'B<0,2,5>' -> B0, B2, B5 ; '{a,b}' -> a, b ; plain name -> [name]"""
    if name.startswith("{") and name.endswith("}"):
        return name[1:-1].split(",")
    parts = _BUS.split(name)
    if len(parts) == 1:
        return [name]
    out = [""]
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out = [o + part for o in out]
            continue
        if ":" in part:
            a, b = (int(x) for x in part.split(":"))
            vals = list(range(a, b + 1)) if a <= b else list(range(a, b - 1, -1))
        else:
            vals = [int(x) for x in part.split(",")]
        out = [o + str(v) for o in out for v in vals]
    return out


def port_buses(cell, cls):
    """families of option / bias ports that are shown as ONE bus pin on the block
    symbol (W1_0..W4_3 -> W<1:4>_<0:3>). returns [(bus, [members in bus order])]"""
    fam = {}
    for p in cell["ports"]:
        if cls.get(p) in ("ctrl", "bias") and _DIG.search(p) and not is_rail(p):
            fam.setdefault(_tpl(p), []).append(p)
    out = []
    for t, mem in fam.items():
        if len(mem) < 2:
            continue
        b = bus_name(mem)
        if b.startswith("{"):
            continue
        out.append((b, expand_bus(b)))
    return out
