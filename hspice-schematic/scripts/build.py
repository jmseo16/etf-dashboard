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
from hsch.export_pptx import export_pptx  # noqa: E402
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

    scenes, info = {}, {"top": ir["top"], "cells": {}}
    for c in cells:
        cell = ir["cells"][c]
        cl = classes[c]
        is_block = any(d["kind"] == "X" for d in cell["devices"])
        display = f"{cl['label']} (자동)" if cell.get("auto") else c
        sc = layout_block(cell, ir, roles, classes) if is_block else layout_leaf(cell, roles[c], display)
        scenes[c] = sc
        insts = {}
        for d in cell["devices"]:
            prm = {k: v for k, v in d["params"].items() if k in ("w", "l", "m", "r", "c")}
            if d["kind"] in "RCL" and not prm:
                prm = {}
            insts[d["name"]] = {"type": d["type"], "ref": d.get("ref"), "auto": bool(d.get("auto")),
                                "pins": {p: n for p, n in d["pins"] if not (d["kind"] == "M" and p == "b")},
                                "params": prm}
        info["cells"][c] = {"display": display, "label": cl["label"], "class": cl["class"],
                            "reason": cl["reason"], "auto": bool(cell.get("auto")),
                            "ports": cell["ports"], "roles": roles[c], "insts": insts,
                            "warnings": sc["warnings"]}

    title = f"{ir['top']} schematic"
    render_html(scenes, info, title, out)
    report = verify_html(out, ir, roles)
    for c, r in report.items():
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
