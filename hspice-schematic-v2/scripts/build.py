#!/usr/bin/env python3
"""HSPICE netlist -> interactive schematic HTML (+ verification report).

usage: build.py NETLIST [-o out.html] [--annotations ann.json] [--top CELL]
                [--ir-json ir.json] [--report report.json] [--pptx out.pptx]
writes OUT.html (interactive viewer) and OUT.pptx (editable PowerPoint, one slide per cell)

annotations.json (optional, written by Claude or the user to fix recognition):
{
  "cells": {"CTLE": {"class": "ctle", "title": "CTLE"},
            "DFE_1TAP__AUTO0": {"class": "summer", "label": "Summer"}},
  "mos_types": {"nch_lvt": "nmos", "pch_lvt": "pmos"}
}
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hsch.analyze import classify_all, extract_auto_blocks, flatten, port_roles  # noqa: E402
from hsch.collapse import build_view_ir, expand_check  # noqa: E402
from hsch.export_pptx import export_pptx  # noqa: E402
from hsch.signals import classify_signals, expand_bus, is_bus  # noqa: E402
from hsch.layout_block import layout_block  # noqa: E402
from hsch.layout_leaf import layout_leaf  # noqa: E402
from hsch.parser import parse_file  # noqa: E402
from hsch.render import render_html  # noqa: E402
from hsch.verify import summarize, verify_html  # noqa: E402


def reachable(ir, top):
    order, seen = [], set()

    def rec(c):
        if c in seen or c not in ir["cells"]:
            return
        seen.add(c)
        order.append(c)
        for d in ir["cells"][c]["devices"]:
            if d["kind"] == "X":
                rec(d["ref"])

    rec(top)
    for r in ir["roots"]:
        rec(r)
    return order


def build(netlist, out, annotations=None, top=None, ir_json=None, report_path=None, quiet=False,
          pptx=None):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)   # output folder may not exist yet
    ann = {}
    if annotations:
        with open(annotations, encoding="utf-8") as f:
            ann = json.load(f)
    ir0 = parse_file(netlist, mos_type_map=ann.get("mos_types"))
    if top:
        ir0["top"] = top
    if not ir0["top"]:
        raise SystemExit("no cells found in netlist")
    ir = extract_auto_blocks(ir0)
    # the transformation must not change the flattened circuit
    f0, f1 = flatten(ir0, ir0["top"]), flatten(ir, ir["top"])
    if f0 != f1:
        raise SystemExit("internal error: auto-block extraction changed connectivity")
    roles = port_roles(ir)
    classes = classify_all(ir, ann)
    cells = reachable(ir, ir["top"])
    # v2: what is drawn (merged devices, bus pins) + net classes
    sigcls = classify_signals(ir)
    vir, vcls, pbuses, merges = build_view_ir(ir, sigcls)
    vroles = {}
    for c, vcell in vir["cells"].items():
        r = dict(roles.get(c, {}))
        for p in vcell["ports"]:
            k = vcls[c].get(p, "hs")
            if is_bus(p):
                r[p] = "bias" if k in ("ctrl", "bias") else r.get(expand_bus(p)[0], "inout")
            elif k in ("ctrl", "bias") and r.get(p) in ("in", "inout", "bias"):
                r[p] = "bias"         # option / bias inputs: label stubs, not wires
        vroles[c] = r

    scenes, info = {}, {"top": ir["top"], "cells": {}}
    for c in cells:
        cell = vir["cells"][c]
        cl = classes[c]
        is_block = any(d["kind"] == "X" for d in cell["devices"])
        display = f"{cl['label']} (auto)" if cell.get("auto") else c
        if is_block:
            sc = layout_block(cell, vir, vroles, classes, netcls=vcls[c])
        else:
            sc = layout_leaf(cell, vroles[c], display, netcls=vcls[c])
        sc["netcls"] = vcls[c]
        scenes[c] = sc
        insts = {}
        for d in cell["devices"]:
            prm = {k: v for k, v in d["params"].items() if k in ("w", "l", "m", "r", "c")}
            if d["kind"] in "RCL" and not prm:
                prm = {}
            if d.get("merged"):
                for k in ("w", "l", "m", "r", "c"):
                    vals = [str(q.get(k)) for q in d["merged"]["params"] if q.get(k) is not None]
                    if vals:
                        prm[k] = ", ".join(vals)
                prm["members"] = ", ".join(d["merged"]["members"])
            insts[d["name"]] = {"type": d["type"], "ref": d.get("ref"), "auto": bool(d.get("auto")),
                                "pins": {p: n for p, n in d["pins"] if not (d["kind"] == "M" and p == "b")},
                                "params": prm}
        info["cells"][c] = {"display": display, "label": cl["label"], "class": cl["class"],
                            "reason": cl["reason"], "auto": bool(cell.get("auto")),
                            "ports": cell["ports"], "roles": vroles[c], "insts": insts,
                            "netcls": vcls[c],
                            "warnings": sc["warnings"]}

    title = f"{ir['top']} schematic"
    render_html(scenes, info, title, out)
    report = verify_html(out, vir, vroles)
    for c, r in report.items():
        # the drawn (merged / bus) circuit must expand back to exactly the netlist
        ex = expand_check(vir["cells"][c], ir["cells"][c], pbuses)
        r["expand_ok"] = not ex
        if ex:
            r["ok"] = False
            r["errors"] = r["errors"] + ["EXPAND: " + e for e in ex]
        info["cells"][c]["verify"] = r
    pptx_path = os.path.splitext(out)[0] + ".pptx" if pptx is None else pptx
    if pptx_path:
        export_pptx(scenes, info, cells, pptx_path)
    # same drawing, now with verification results (and the editable .pptx) embedded
    render_html(scenes, info, title, out, pptx_path=pptx_path)
    text, ok = summarize(report)
    if ir0["warnings"]:
        text = "PARSER WARNINGS:\n  " + "\n  ".join(ir0["warnings"]) + "\n" + text
    if ir_json:
        with open(ir_json, "w", encoding="utf-8") as f:
            json.dump({"ir": ir, "roles": roles, "classes": classes}, f, indent=1, ensure_ascii=False)
    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({"ok": ok, "views": report, "classes": classes}, f, indent=1, ensure_ascii=False)
    if not quiet:
        print(text)
        print("classification:")
        for c in cells:
            print(f"  {c:28s} -> {classes[c]['class']:12s} ({classes[c]['reason']})")
        print(f"wrote {out}")
        if pptx_path:
            print(f"wrote {pptx_path}  (editable PowerPoint: one slide per cell)")
    return ok, report, scenes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--annotations")
    ap.add_argument("--top")
    ap.add_argument("--ir-json")
    ap.add_argument("--report")
    ap.add_argument("--pptx", help="editable PowerPoint output (default: next to the HTML; '' to skip)")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.netlist)[0] + "_schematic.html"
    ok, _, _ = build(a.netlist, out, a.annotations, a.top, a.ir_json, a.report, pptx=a.pptx)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
