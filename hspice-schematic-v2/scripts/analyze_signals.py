#!/usr/bin/env python3
"""Print the signal classification and same-role merge groups of a netlist.

usage: analyze_signals.py NETLIST [--top CELL]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import reachable  # noqa: E402
from hsch.analyze import extract_auto_blocks  # noqa: E402
from hsch.parser import parse_file  # noqa: E402
from hsch.signals import classify_signals, compress, report  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist")
    ap.add_argument("--top")
    a = ap.parse_args()
    ir0 = parse_file(a.netlist)
    if a.top:
        ir0["top"] = a.top
    ir = extract_auto_blocks(ir0)
    cls = classify_signals(ir)
    order = reachable(ir, ir["top"])
    print(f"top = {ir['top']}")
    if ir0["warnings"]:
        print("parser warnings:\n  " + "\n  ".join(ir0["warnings"]))
    print(report(ir, cls, order))
    # what the top-level drawing would route as wires vs. labels
    top = ir["cells"][ir["top"]]
    nets = sorted({n for d in top["devices"] for _, n in d["pins"]} | set(top["ports"]))
    kinds = {}
    for n in nets:
        kinds.setdefault(cls[ir["top"]].get(n, "?"), []).append(n)
    print(f"\n## top-level nets by class ({len(nets)} nets)")
    for k in ("hs", "clk", "ctrl", "bias", "power", "?"):
        if kinds.get(k):
            print(f"  {k:5s} ({len(kinds[k])}): {compress(kinds[k])}")


if __name__ == "__main__":
    main()
