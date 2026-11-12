"""Display transformation (v2): the circuit as it is DRAWN, plus a proof that it is
the same circuit as the netlist.

  * leaf cells   : same-role devices merged into one iterated device (MS_G<0:3>),
                   parallel passive banks merged into one device
  * block cells  : option / bias pin families of an instance become one bus pin
                   (W1_0..W4_3 -> W<1:4>_<0:3>); the cell's own ports likewise
  * expand_check : expands every bus back to single devices / pins / nets and
                   compares pin-by-pin with the original cell -> list of errors

The drawing is verified against the view cell by the normal verifier; together with
expand_check this proves drawing == netlist.
"""
import copy

from .analyze import pin_map
from .signals import bus_name, expand_bus, find_slices, is_bus, port_buses


def _is_bulk(d, p):
    return d["kind"] == "M" and p == "b"


# ---------------------------------------------------------------------------
def leaf_view(cell):
    """returns (view_cell, groups_used)"""
    devs = cell["devices"]
    by_name = {d["name"]: d for d in devs}
    groups = find_slices(cell)
    # a device may belong to one group only
    taken, cand = set(), []
    for g in groups:
        if taken & set(g["members"]):
            continue
        cand.append(g)
        taken |= set(g["members"])
    # a varying (bus) net may only be used by devices of groups that map it into the
    # same bus name; otherwise merging would hide a connection -> drop the group
    while True:
        bus_of = {}
        for g in cand:
            if g["kind"] != "iterated":
                continue
            for p, bn in g["pins"].items():
                if is_bus(bn):
                    for n in expand_bus(bn):
                        bus_of.setdefault(n, set()).add(bn)
        member_of = {m: g for g in cand for m in g["members"]}
        bad = None
        for d in devs:
            for p, n in d["pins"]:
                if _is_bulk(d, p) or n not in bus_of:
                    continue
                g = member_of.get(d["name"])
                if g is None or g["kind"] != "iterated" or g["pins"].get(p) not in bus_of[n] or len(bus_of[n]) > 1:
                    bad = g or next(gg for gg in cand if any(
                        n in expand_bus(bn) for bn in gg["pins"].values() if is_bus(bn)))
                    break
            if bad:
                break
        if bad is None:
            break
        cand.remove(bad)
    member_of = {m: g for g in cand for m in g["members"]}
    out_devs, done = [], set()
    for d in devs:
        g = member_of.get(d["name"])
        if g is None:
            out_devs.append(d)
            continue
        if id(g) in done:
            continue
        done.add(id(g))
        first = by_name[g["members"][0]]
        nd = copy.deepcopy(first)
        nd["name"] = g["name"]
        nd["merged"] = {"kind": g["kind"], "members": list(g["members"]),
                        "params": [by_name[m]["params"] for m in g["members"]]}
        if g["kind"] == "iterated":
            nd["pins"] = [[p, g["pins"].get(p, n)] for p, n in first["pins"]]
        out_devs.append(nd)
    view = dict(cell)
    view["devices"] = out_devs
    view["ports"] = _collapse_ports(cell["ports"], out_devs)
    return view, cand


def _collapse_ports(ports, devs):
    """ports that now only appear inside one bus net are listed under the bus name"""
    used = {}
    for d in devs:
        for p, n in d["pins"]:
            for m in (expand_bus(n) if is_bus(n) else [n]):
                used.setdefault(m, set()).add(n)
    out = []
    for p in ports:
        names = used.get(p, {p})
        if len(names) == 1:
            n = next(iter(names))
            if is_bus(n) and all(m in ports for m in expand_bus(n)):
                if n not in out:
                    out.append(n)
                continue
        out.append(p)
    return out


# ---------------------------------------------------------------------------
def block_view(cell, pbuses):
    """pbuses: {cell: [(bus_pin, [member pins])]} for every cell"""
    view = dict(cell)
    devs = []
    for d in cell["devices"]:
        if d["kind"] != "X" or not pbuses.get(d["ref"]):
            devs.append(d)
            continue
        P = pin_map(d)
        pins = list(d["pins"])
        for bus_pin, members in pbuses[d["ref"]]:
            nets = [P[m] for m in members]
            bn = bus_name(nets)
            if len(set(nets)) != len(nets) or not is_bus(bn) or bn.startswith("{") or expand_bus(bn) != nets:
                continue          # the parent wiring is not a clean bus: keep single pins
            first = members[0]
            new = []
            for p, n in pins:
                if p == first:
                    new.append([bus_pin, bn])
                elif p not in members:
                    new.append([p, n])
            pins = new
        nd = dict(d)
        nd["pins"] = pins
        devs.append(nd)
    view["devices"] = devs
    own = pbuses.get(cell["name"], [])
    ports = []
    for p in cell["ports"]:
        hit = next((b for b, mem in own if p in mem), None)
        if hit is None:
            ports.append(p)
        elif hit not in ports:
            ports.append(hit)
    view["ports"] = ports
    return view


# ---------------------------------------------------------------------------
def expand_check(view, orig, pbuses):
    """expand the drawn (view) cell back to single devices/pins/nets and compare it
    with the original netlist cell. returns a list of error strings ([] = identical)."""
    errs = []
    want = {}
    for d in orig["devices"]:
        want[d["name"]] = {p: n for p, n in d["pins"] if not _is_bulk(d, p)}
    got = {}
    sub_bus = {}
    for c, lst in pbuses.items():
        sub_bus[c] = dict(lst)
    for d in view["devices"]:
        P = [(p, n) for p, n in d["pins"] if not _is_bulk(d, p)]
        mg = d.get("merged")
        if mg and mg["kind"] == "parallel":
            for m in mg["members"]:
                got[m] = ("parallel", {n for _, n in P})
            continue
        names = mg["members"] if mg else [d["name"]]
        if mg and expand_bus(d["name"]) != names:
            errs.append(f"{d['name']}: name does not expand to its members")
        for i, m in enumerate(names):
            pm = {}
            for p, n in P:
                if d["kind"] == "X" and p in sub_bus.get(d.get("ref"), {}):
                    mp, mn = sub_bus[d["ref"]][p], expand_bus(n)
                    if len(mp) != len(mn):
                        errs.append(f"{d['name']}.{p}: bus width {len(mp)} vs net {n} width {len(mn)}")
                        continue
                    pm.update(zip(mp, mn))
                    continue
                nets = expand_bus(n)
                if mg and len(nets) > 1:
                    if len(nets) != len(names):
                        errs.append(f"{d['name']}.{p}: net {n} has {len(nets)} bits for {len(names)} devices")
                        continue
                    pm[p] = nets[i]
                else:
                    pm[p] = n
            got[m] = pm
    for name, pins in want.items():
        if name not in got:
            errs.append(f"device {name} missing from the drawing")
            continue
        g = got[name]
        if isinstance(g, tuple):                      # parallel bank member: net set must match
            if g[1] != set(pins.values()):
                errs.append(f"{name}: parallel bank nets {sorted(g[1])} != {sorted(set(pins.values()))}")
        elif g != pins:
            diff = {p: (pins.get(p), g.get(p)) for p in set(pins) | set(g) if pins.get(p) != g.get(p)}
            errs.append(f"{name}: pins differ {diff}")
    for name in got:
        if name not in want:
            errs.append(f"drawing has device {name} that is not in the netlist")
    vp = [m for p in view["ports"] for m in expand_bus(p)]
    if sorted(vp) != sorted(orig["ports"]):
        errs.append(f"ports differ: drawn {sorted(set(vp) - set(orig['ports']))} / missing {sorted(set(orig['ports']) - set(vp))}")
    return errs


def build_view_ir(ir, sigcls):
    """returns (view_ir, net_classes_for_view, pbuses, merge_info)"""
    pbuses = {c: port_buses(cell, sigcls.get(c, {})) for c, cell in ir["cells"].items()}
    vir = dict(ir)
    vir["cells"] = {}
    vcls = {}
    merges = {}
    for c, cell in ir["cells"].items():
        is_block = any(d["kind"] == "X" for d in cell["devices"])
        if is_block:
            v = block_view(cell, pbuses)
            merges[c] = []
        else:
            v, used = leaf_view(cell)
            merges[c] = used
        vir["cells"][c] = v
        cls = dict(sigcls.get(c, {}))
        for d in v["devices"]:
            for p, n in d["pins"]:
                if is_bus(n) and n not in cls:
                    cls[n] = cls.get(expand_bus(n)[0], "hs")
        for p in v["ports"]:
            if is_bus(p) and p not in cls:
                cls[p] = cls.get(expand_bus(p)[0], "hs")
        vcls[c] = cls
    return vir, vcls, pbuses, merges
