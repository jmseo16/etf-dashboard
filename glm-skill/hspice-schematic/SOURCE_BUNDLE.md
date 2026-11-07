# hspice-schematic — 기준 구현 전체 소스 (SOURCE_BUNDLE)

`SKILL.md`(구현 명세서)와 함께 쓰는 파일이다. 아래 각 `### FILE: <경로>` 블록을 그 경로에 **그대로** 저장하면 기준 구현과 똑같은 도구가 된다. 파일마다 SHA-256이 적혀 있으니 복원 후 반드시 대조한다.

## 복원 방법

1. 코드를 실행할 수 있으면: 아래 복원 스크립트를 `restore.py`로 저장하고
   `python3 restore.py SOURCE_BUNDLE.md <저장할 폴더>` 실행 → 모든 줄이 `OK`, `0 checksum mismatches`여야 한다.
2. 실행할 수 없으면: 각 블록의 내용을 한 글자도 바꾸지 말고 그 경로의 파일로 만든다 (코드 블록 바깥 줄바꿈 규칙: `newline=1`이면 파일 끝에 줄바꿈 하나).
3. 그다음 `SKILL.md` §14 검증 절차를 실행한다 (`pip install python-pptx`, 검증용 Node.js + Playwright).

### 복원 스크립트 (restore.py)

````python
import hashlib, os, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
dest = sys.argv[2] if len(sys.argv) > 2 else "."
pat = re.compile(r"^### FILE: (\S+)\n<!-- sha256=([0-9a-f]{64}) newline=([01]) -->\n````\w*\n(.*?)\n````$", re.S | re.M)
n = bad = 0
for path, sha, nl, body in pat.findall(src):
    data = body + ("\n" if nl == "1" else "")
    if body == "" and nl == "0":
        data = ""
    full = os.path.join(dest, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    ok = hashlib.sha256(data.encode("utf-8")).hexdigest() == sha
    bad += not ok
    n += 1
    print(("OK   " if ok else "BAD  ") + path)
print(f"{n} files restored, {bad} checksum mismatches")
sys.exit(1 if bad else 0)
````

## 파일 목록

- `hspice-schematic/SKILL.md` (85 lines)
- `hspice-schematic/references/style_rules.md` (60 lines)
- `hspice-schematic/scripts/build.py` (137 lines)
- `hspice-schematic/scripts/hsch/__init__.py` (0 lines)
- `hspice-schematic/scripts/hsch/parser.py` (336 lines)
- `hspice-schematic/scripts/hsch/analyze.py` (405 lines)
- `hspice-schematic/scripts/hsch/geom.py` (472 lines)
- `hspice-schematic/scripts/hsch/router.py` (356 lines)
- `hspice-schematic/scripts/hsch/layout_leaf.py` (1114 lines)
- `hspice-schematic/scripts/hsch/layout_block.py` (492 lines)
- `hspice-schematic/scripts/hsch/render.py` (178 lines)
- `hspice-schematic/scripts/hsch/verify.py` (431 lines)
- `hspice-schematic/scripts/hsch/export_pptx.py` (266 lines)
- `hspice-schematic/scripts/screenshot.js` (33 lines)
- `hspice-schematic/scripts/ui_selftest.js` (274 lines)
- `hspice-schematic/assets/viewer.css` (120 lines)
- `hspice-schematic/assets/viewer.js` (414 lines)
- `tests/test_hsch.py` (220 lines)
- `tests/netlists/input_buffer_system.sp` (44 lines)
- `tests/netlists/virtuoso_style.sp` (31 lines)

## 파일 내용

### FILE: hspice-schematic/SKILL.md
<!-- sha256=86d9905ee21811526e49a88684984d45411aea2a464840038f89bcb35ed6fca8 newline=1 -->
````markdown
---
name: hspice-schematic
description: Draw an interactive, textbook-style (Razavi) schematic from an HSPICE / Virtuoso-exported netlist and verify it against the netlist. Use whenever the user gives a SPICE/HSPICE netlist (.sp, .cir, .net, pasted text with .SUBCKT) and wants to see it as a schematic, block diagram, or transistor-level drawing, or asks to check/visualise a circuit's hierarchy.
---

# HSPICE netlist → interactive schematic

Produces one self-contained HTML file (works offline): a block diagram of the top cell; click
any block to open the level below, down to transistors. Every drawing is checked against the
netlist before it is handed over. Next to it an editable PowerPoint (`OUT.pptx`, also
downloadable from the viewer's ⬇ PPT button): one slide per cell, every wire a line, every
device / block / pin a named group, every label a text box, blocks link to their slides.

## Workflow

1. **Save the netlist** to a file (keep the user's text exactly; do not "fix" it).
2. **Build** (parses, extracts auto-blocks, recognises blocks, places, routes, renders, verifies):
   ```bash
   python3 scripts/build.py NETLIST.sp -o OUT.html --report OUT_report.json
   ```
   The console prints one line per view (`[PASS]/[FAIL]`, crossings, lint count) and the
   recognised class of every cell with the reason.
3. **Connectivity must pass.** `CONNECTIVITY: ALL VIEWS MATCH NETLIST` means the verifier
   rebuilt the connectivity purely from the drawn geometry (wires, junctions, pins, name labels)
   and it matches the netlist pin-for-pin. If any view FAILS, do not deliver — read the
   `OPEN:` / `SHORT:` lines, fix the cause, rebuild.
4. **Visual review.** Render every view and look at each image:
   ```bash
   node scripts/screenshot.js OUT.html shots/
   ```
   Check against `references/style_rules.md` (mirror symmetry, VDD top / ground bottom,
   PMOS above NMOS, loads above drains, tails centred, no overlapping text). Lint must be 0.
5. **Viewer self-test** (whenever the viewer or renderer changed, and before delivering):
   ```bash
   node scripts/ui_selftest.js OUT.html
   ```
   Presses every control on desktop and on an emulated phone (real touch events: pan,
   pinch, thumb taps) and asserts the drawing stays put / on screen, toggles only change
   labels, navigation lands on the right cell, no tooltip is left behind, no JS errors.
   Must end with `0 failed`.
   To check the PowerPoint visually: `soffice --headless --convert-to pdf OUT.pptx` then
   `pdftoppm -r 70 -png OUT.pdf slide`.
6. **Fix recognition if needed** with an annotations file and rebuild with
   `--annotations ann.json`:
   ```json
   {"cells": {"MY_SLICER": {"class": "latch"}, "TOP__AUTO0": {"class": "summer", "label": "Summer"}},
    "mos_types": {"nch_lvt_mac": "nmos", "pch_hvt_mac": "pmos"}}
   ```
   Classes: `ctle, buffer, diff_buffer, amplifier, comparator, inverter, nand, nor, and, or, xor,
   summer, latch, dff, mux, dfe, generic`. `mos_types` maps model names whose N/P type cannot be
   guessed (model names are never shown in the drawing).
7. **Deliver** the HTML and summarise: hierarchy, recognised blocks (with reasons), auto-blocks
   created, verification result, anything that needed an override.

## What the tool does automatically

- **Parser**: `+` continuation, `*` / `$` comments, case-insensitive names, `.subckt/.ends`,
  `.param`, `.global`, `.include` (if the file exists), M/R/C/L/V/I/E/G/F/H/D/Q/X elements.
- **Auto-blocks**: in a cell that mixes subckt instances and loose devices, each
  channel-connected group of devices becomes its own block (e.g. the DFE summer); a lone R/C/L
  is drawn as itself. Flattened connectivity is asserted unchanged.
- **Recognition**: name hints + topology (diff pair, cross-coupled pair, clock pair,
  degeneration, summing pairs, CMOS inverter, NAND/NOR, master-slave latches).
- **Transistor level**: global mirror symmetry when the cell is symmetric, otherwise local
  mirroring of each matched pair around its own tail; cross-coupled pairs drawn as an X.
- **Block level**: left→right signal flow, feedback enters from below, clocks from below,
  bias pins as name stubs, arrowheads on inputs, instance labels placed where nothing overlaps.
- **Viewer**: pan / zoom, click to descend, breadcrumb, Esc to go up, net highlight
  (hover / click), tooltips with W/L/m and pin nets, port mapping of the current instance,
  toggles for W/L·m, R/C values, device names, net names.

## Files

- `scripts/build.py` – CLI entry point
- `scripts/hsch/parser.py` – netlist → IR
- `scripts/hsch/analyze.py` – rails, port roles, auto-blocks, recognition
- `scripts/hsch/layout_leaf.py` – transistor-level placement (symmetry, tree packing)
- `scripts/hsch/layout_block.py` – block-level placement
- `scripts/hsch/router.py` – grid maze router (no overlaps, crossings only straight through)
- `scripts/hsch/render.py`, `assets/viewer.*` – HTML/SVG + viewer
- `scripts/hsch/export_pptx.py` – editable PowerPoint export
- `scripts/hsch/verify.py` – connectivity extraction from the drawing + visual lint
- `scripts/screenshot.js` – PNG per view for visual review
- `scripts/ui_selftest.js` – automated test of every viewer control (desktop + phone)
- `references/style_rules.md` – the drawing rules (from the user's reference figures)
````

### FILE: hspice-schematic/references/style_rules.md
<!-- sha256=935663a22c644c14c418658070d5e0c4a0218c56b4b8ddda8aaf4c3de886b5a8 newline=1 -->
````markdown
# Schematic style rules (textbook / Razavi style)

Extracted from reference figures supplied by the user (merged CTLE + DFE summer,
source-degenerated CTLE, wireline transceiver block diagram) plus Razavi
conventions. The layout engine implements every rule marked **[auto]**; rules
marked **[lint]** are checked by `verify.py`.

## Transistor level

1. **Mirror symmetry** [auto][lint] – every differential pair (σ-matched devices:
   `INP/INN`, `OUTP/OUTN`, `SP/SN`, … propagated through equal-size devices) is drawn
   as an exact mirror image about a vertical axis. When the whole cell is
   symmetric (each band has at most one self-symmetric device), the axis is global
   (CTLE, CML latch); otherwise each pair is mirrored about its own centred tail
   (merged CTLE/DFE summer: main pair + tap pairs side by side).
2. **Matched siblings are mirrored** [auto] – two equal devices sharing a source node
   (clock pair, tap pair, tail pair) are placed symmetrically around the device that
   feeds them, gates mirrored.
3. **Gate facing** [auto] – input pairs face *outward* (IN on the left, IN̄ on the right);
   cross-coupled and shared-gate pairs face *inward*. Cross-coupled gates are wired
   with two diagonal lines forming an "X" on the axis.
4. **Vertical order** [auto][lint] – supply rail on top, ground at the bottom, PMOS
   above NMOS, loads directly above the drains they feed, tail current source centred
   below the pair it feeds.
5. **One straight horizontal per node** [auto] – drain/source nodes are drawn as a
   single horizontal bus with vertical drops; when two buses overlap at the same
   height the second one is offset by one track (e.g. the two summer output buses).
6. **Degeneration** [auto] – passives between the two source nodes of a pair are drawn
   horizontally between the columns, R above C, with dots at the four junctions.
7. **MOSFET symbol** [auto] – 3-terminal; thick channel line that ends exactly at the
   drain/source stubs; gate plate separated from the channel by a clearly visible
   gate-oxide gap (Razavi proportions: body 21 px wide × 30 px tall, oxide gap 9 px on a
   10 px grid); arrow on the source stub pointing away from the channel (NMOS) / into the
   channel (PMOS); drain and source leave vertically.
8. **Rails** [auto] – VDD is one horizontal rail; every ground connection gets its own
   ground symbol. When VDD / VSS are ports of the cell they get an inout pin (rule 9):
   VDD at the left end of the rail, VSS bottom-left tied to its own ground symbol.
9. **Ports = Virtuoso schematic pins** [auto][test] – every port of the cell is drawn as a
   red Virtuoso pin with its name: input = pentagon pointing into the circuit, output =
   pentagon pointing out, inout = hexagon. Single-gate inputs (IN, CLK, VBIAS) sit right
   at the end of the gate lead; routed outputs leave on their own half of a symmetric
   cell (QP left, QN right) or on the right otherwise; a self-symmetric input shared by a
   mirrored pair (CTLE VBIAS) enters from below on the axis; at block level inputs are
   left, outputs right, clocks below, bias pins on the stub above the block.
10. **Junctions** [auto][lint] – a dot at every T junction, never a 4-way junction,
    crossings without dots only.
11. **Annotations** [auto] – device name, W/L and m next to the device on the side
    opposite the gate; each class can be toggled off in the viewer.

## Block level

12. **Signal flow** [auto] – left to right; inputs enter on the left with an arrowhead,
    outputs leave on the right; feedback inputs enter from below.
13. **Clock** [auto] – clocks enter from below, straight up into the clock pin.
14. **Bias** [auto] – bias pins are short stubs with the net name; no long bias wires.
15. **Symbols** [auto] – differential amplifier/CTLE = triangle with +/− marks;
    summer = circle with Σ; latch / flip-flop = box (flip-flop clock marked with ▷);
    anything else = box with the cell name.
16. **No overlapping text** [lint] – no label may overlap another label, a wire or a
    symbol outline. The instance label goes to the free side of the symbol.
````

### FILE: hspice-schematic/scripts/build.py
<!-- sha256=e2d49b851a4c0dd5ae062ea1a90a87874502c2c52518aa1d53181069080e0ed2 newline=1 -->
````python
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

    scenes, info = {}, {"top": ir["top"], "cells": {}}
    for c in cells:
        cell = ir["cells"][c]
        cl = classes[c]
        is_block = any(d["kind"] == "X" for d in cell["devices"])
        display = f"{cl['label']} (auto)" if cell.get("auto") else c
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
````

### FILE: hspice-schematic/scripts/hsch/__init__.py
<!-- sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 newline=0 -->
````python

````

### FILE: hspice-schematic/scripts/hsch/parser.py
<!-- sha256=fb3fb65e552e83019aaf941efc5670488ebadd60e12e7de8736c3ac7748dc910 newline=1 -->
````python
"""HSPICE netlist parser -> hierarchical IR (plain dicts, JSON-serialisable).

IR layout:
{
  "top": "CELL" | null,
  "roots": [...],                      # cells not instantiated by any other cell
  "globals": [...],
  "cells": {
    "CELL": {
      "name": "CELL",
      "ports": ["A", "B", ...],
      "params": {...},
      "devices": [
        {"name": "M1", "kind": "M", "type": "nmos",
         "pins": [["d","OUTP"],["g","INP"],["s","SP"],["b","VSS"]],
         "model": "NCH", "params": {"w": "16u", "l": "45n"}, "ref": null}
        ...
      ]
    }
  },
  "warnings": [...]
}
"""
from __future__ import annotations

import os
import re

TOP_CELL = "__TOP__"

_SI = {
    "t": 1e12, "g": 1e9, "meg": 1e6, "x": 1e6, "k": 1e3, "mil": 25.4e-6,
    "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18,
}
_NUM_RE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)(meg|mil|[tgxkmunpfa])?[a-z]*$", re.I)


def parse_value(text):
    """Parse an HSPICE number with optional SI suffix. Returns float or None."""
    if text is None:
        return None
    s = str(text).strip().strip("'\"")
    m = _NUM_RE.match(s)
    if not m:
        return None
    v = float(m.group(1))
    suf = (m.group(2) or "").lower()
    return v * _SI.get(suf, 1.0)


def _logical_lines(text):
    """Strip comments, join '+' continuation lines. Yields (lineno, line)."""
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("*"):
            continue
        # '$' starts an inline comment (HSPICE) when at start or preceded by whitespace
        line = re.sub(r"(^|\s)\$.*$", "", line)
        # '//' is not HSPICE, but some generators emit it
        if not line.strip():
            continue
        if line.lstrip().startswith("+"):
            if out:
                out[-1] = (out[-1][0], out[-1][1] + " " + line.lstrip()[1:])
            continue
        out.append((i, line.strip()))
    return out


def _tokenize(line):
    # normalise "a = b" -> "a=b", keep quoted expressions together
    line = re.sub(r"\s*=\s*", "=", line)
    tokens, buf, quote = [], "", None
    for ch in line:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            buf += ch
        elif ch in " \t,()":
            if buf:
                tokens.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    return tokens


def _split_params(tokens):
    pos, params = [], {}
    for t in tokens:
        if "=" in t and not t.startswith("="):
            k, v = t.split("=", 1)
            params[k.lower()] = v
        else:
            pos.append(t)
    return pos, params


_PMOS_HINT = re.compile(r"(^p|pch|pmos|pfet|_p\b)", re.I)
_NMOS_HINT = re.compile(r"(^n|nch|nmos|nfet|_n\b)", re.I)


class Netlist:
    def __init__(self):
        self.cells = {}
        self.globals = []
        self.params = {}
        self.models = {}          # model name (lower) -> type (nmos/pmos/...)
        self.warnings = []
        self._canon = {}          # (cell, lower) -> display spelling

    # ---- name canonicalisation (HSPICE is case-insensitive) ----
    def canon(self, cell, name):
        key = (cell if not self._is_global(name) else "*", name.lower())
        if key not in self._canon:
            self._canon[key] = name
        return self._canon[key]

    def _is_global(self, name):
        return name.lower() in {g.lower() for g in self.globals} or name == "0"

    def new_cell(self, name, ports, params):
        cell = {"name": name, "ports": ports, "params": params, "devices": []}
        self.cells[name] = cell
        return cell


def parse_file(path, mos_type_map=None):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return parse_text(text, base_dir=os.path.dirname(os.path.abspath(path)), mos_type_map=mos_type_map)


def parse_text(text, base_dir=".", mos_type_map=None):
    nl = Netlist()
    mos_type_map = {k.lower(): v for k, v in (mos_type_map or {}).items()}
    lines = _logical_lines(text)
    _expand_includes(lines, base_dir, nl)

    # first pass: globals and models so canonicalisation / typing works
    for _, line in lines:
        low = line.lower()
        if low.startswith(".global"):
            nl.globals.extend(_tokenize(line)[1:])
        elif low.startswith(".model"):
            toks = _tokenize(line)
            if len(toks) >= 3:
                nl.models[toks[1].lower()] = toks[2].lower()

    cur = None
    top_devices = []
    for lineno, line in lines:
        toks = _tokenize(line)
        if not toks:
            continue
        head = toks[0].lower()
        if head.startswith("."):
            if head in (".subckt", ".macro"):
                pos, params = _split_params(toks[1:])
                pos = [p for p in pos if p.lower() not in ("params:", "param:")]
                if not pos:
                    nl.warnings.append(f"line {lineno}: .SUBCKT without name")
                    continue
                name = pos[0]
                cur = nl.new_cell(name, [], params)
                cur["ports"] = [nl.canon(name, p) for p in pos[1:]]
            elif head in (".ends", ".eom"):
                cur = None
            elif head == ".param":
                _, params = _split_params(toks[1:])
                (cur["params"] if cur else nl.params).update(params)
            # other dot-cards (.global/.model/.option/.end/.temp/...) are ignored here
            continue
        cell_name = cur["name"] if cur else TOP_CELL
        dev = _parse_element(toks, cell_name, nl, mos_type_map, lineno)
        if dev is None:
            continue
        (cur["devices"] if cur else top_devices).append(dev)

    if top_devices:
        nl.new_cell(TOP_CELL, [], {})["devices"] = top_devices

    # resolve subckt instance pin names
    for cell in nl.cells.values():
        for d in cell["devices"]:
            if d["kind"] != "X":
                continue
            ref = _find_cell(nl, d["ref"])
            if ref is None:
                nl.warnings.append(f"{cell['name']}/{d['name']}: unknown subckt '{d['ref']}' (treated as black box)")
                d["pins"] = [[f"p{i+1}", n] for i, (_, n) in enumerate(d["pins"])]
                continue
            d["ref"] = ref["name"]
            nets = [n for _, n in d["pins"]]
            if len(nets) != len(ref["ports"]):
                nl.warnings.append(
                    f"{cell['name']}/{d['name']}: {len(nets)} nodes but {ref['name']} has {len(ref['ports'])} ports")
            d["pins"] = [[ref["ports"][i] if i < len(ref["ports"]) else f"p{i+1}", n] for i, n in enumerate(nets)]

    instantiated = {d["ref"] for c in nl.cells.values() for d in c["devices"] if d["kind"] == "X"}
    roots = [c for c in nl.cells if c not in instantiated]
    top = TOP_CELL if TOP_CELL in nl.cells else (_pick_top(nl, roots) if roots else None)
    return {
        "top": top,
        "roots": roots,
        "globals": nl.globals,
        "params": nl.params,
        "cells": nl.cells,
        "warnings": nl.warnings,
    }


def _expand_includes(lines, base_dir, nl, depth=0):
    i = 0
    while i < len(lines):
        lineno, line = lines[i]
        low = line.lower()
        if low.startswith(".include") or low.startswith(".inc ") or (low.startswith(".lib") and len(_tokenize(line)) == 2):
            toks = _tokenize(line)
            path = toks[1].strip("'\"") if len(toks) > 1 else ""
            full = os.path.join(base_dir, path)
            if depth < 8 and path and os.path.isfile(full):
                with open(full, encoding="utf-8", errors="replace") as f:
                    sub = _logical_lines(f.read())
                _expand_includes(sub, os.path.dirname(full), nl, depth + 1)
                lines[i:i + 1] = sub
                i += len(sub)
                continue
            nl.warnings.append(f"line {lineno}: include '{path}' not found (ignored)")
        i += 1


def _find_cell(nl, name):
    for c in nl.cells.values():
        if c["name"].lower() == str(name).lower():
            return c
    return None


def _pick_top(nl, roots):
    def depth(name, seen=()):
        cell = nl.cells[name]
        subs = [d["ref"] for d in cell["devices"] if d["kind"] == "X" and d["ref"] in nl.cells and d["ref"] not in seen]
        return 1 + max((depth(s, seen + (name,)) for s in subs), default=0)
    return max(roots, key=lambda r: (depth(r), len(nl.cells[r]["devices"])))


def _mos_type(model, nl, mos_type_map):
    m = model.lower()
    if m in mos_type_map:
        return mos_type_map[m]
    mt = nl.models.get(m, "")
    if mt in ("pmos", "nmos"):
        return mt
    if _PMOS_HINT.search(model):
        return "pmos"
    if _NMOS_HINT.search(model):
        return "nmos"
    nl.warnings.append(f"model '{model}': cannot tell NMOS/PMOS, assuming nmos (add it to the type map)")
    return "nmos"


def _parse_element(toks, cell, nl, mos_type_map, lineno):
    name = toks[0]
    letter = name[0].upper()
    pos, params = _split_params(toks[1:])
    C = lambda n: nl.canon(cell, n)

    def dev(kind, typ, pins, model=None, ref=None):
        return {"name": name, "kind": kind, "type": typ,
                "pins": [[p, C(n)] for p, n in pins],
                "model": model, "params": params, "ref": ref, "line": lineno}

    try:
        if letter == "M":
            if len(pos) < 5:
                raise ValueError("MOSFET needs 4 nodes + model")
            d, g, s, b, model = pos[:5]
            return dev("M", _mos_type(model, nl, mos_type_map), [("d", d), ("g", g), ("s", s), ("b", b)], model=model)
        if letter in "RCL":
            if len(pos) < 2:
                raise ValueError("2 nodes required")
            typ = {"R": "res", "C": "cap", "L": "ind"}[letter]
            key = {"R": "r", "C": "c", "L": "l"}[letter]
            model = None
            if len(pos) >= 3:
                if parse_value(pos[2]) is not None or pos[2].startswith("'"):
                    params.setdefault(key, pos[2])
                else:
                    model = pos[2]
                    if len(pos) >= 4:
                        params.setdefault(key, pos[3])
            return dev(letter, typ, [("p", pos[0]), ("n", pos[1])], model=model)
        if letter in "VI":
            if len(pos) < 2:
                raise ValueError("2 nodes required")
            rest = " ".join(pos[2:])
            if rest:
                params.setdefault("value", rest)
            return dev(letter, "vsrc" if letter == "V" else "isrc", [("p", pos[0]), ("n", pos[1])])
        if letter in "EG":
            if len(pos) < 4:
                raise ValueError("4 nodes required")
            if len(pos) > 4:
                params.setdefault("gain", pos[4])
            return dev(letter, "vcvs" if letter == "E" else "vccs",
                       [("p", pos[0]), ("n", pos[1]), ("cp", pos[2]), ("cn", pos[3])])
        if letter in "FH":
            if len(pos) < 3:
                raise ValueError("2 nodes + vsrc required")
            params.setdefault("vctrl", pos[2])
            return dev(letter, "cccs" if letter == "F" else "ccvs", [("p", pos[0]), ("n", pos[1])])
        if letter == "D":
            return dev("D", "diode", [("a", pos[0]), ("k", pos[1])], model=pos[2] if len(pos) > 2 else None)
        if letter == "Q":
            pins = [("c", pos[0]), ("b", pos[1]), ("e", pos[2])]
            model = pos[3] if len(pos) > 3 else None
            return dev("Q", "bjt", pins, model=model)
        if letter == "X":
            if len(pos) < 2:
                raise ValueError("subckt instance needs nodes + name")
            ref = pos[-1]
            return dev("X", "inst", [(f"p{i+1}", n) for i, n in enumerate(pos[:-1])], ref=ref)
    except (ValueError, IndexError) as e:
        nl.warnings.append(f"line {lineno}: cannot parse '{name}': {e}")
        return None
    nl.warnings.append(f"line {lineno}: unsupported element '{name}' (ignored)")
    return None
````

### FILE: hspice-schematic/scripts/hsch/analyze.py
<!-- sha256=5b1cdffb65e96baa812fc3c5c3d983b8f497ab97a4c66e2ff7be6bc184455fd5 newline=1 -->
````python
"""Circuit analysis on the parsed IR:
  * supply / ground net detection
  * port direction (in / out / clk / bias / power / ground)
  * automatic block extraction for cells that mix primitives and subckt instances
  * topology recognition -> block class + symbol
"""
from __future__ import annotations

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
````

### FILE: hspice-schematic/scripts/hsch/geom.py
<!-- sha256=c31fdd221aa28e4c1066195c9a7843e44653945f49d21e1137a7567a74ead8bc newline=1 -->
````python
"""Symbol library. Every symbol is built in local coordinates (grid = 10 px) and then
transformed (mirror / rotate / translate) into absolute coordinates.

A symbol instance is a dict:
  prims   : drawing primitives  ('line', x1,y1,x2,y2, cls) | ('poly', [(x,y)..], cls)
            | ('circle', cx,cy,r, cls) | ('path', d, cls) | ('text', x,y,txt, cls, anchor)
  pins    : {pin_name: (x, y, dir)}   dir in 'LRUD' = direction the wire leaves the pin
  keepout : [(x0,y0,x1,y1)]           rectangles the router must not cross
  labels  : [('text', x, y, [(txt, cls)...], anchor)]   annotation text (toggle-able)
  bbox    : (x0,y0,x1,y1)
"""
from __future__ import annotations

import math

G = 10  # routing grid

_ROT = {"U": "R", "R": "D", "D": "L", "L": "U"}
_MIR = {"L": "R", "R": "L", "U": "U", "D": "D"}

ENG = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"),
       (1e-6, "µ"), (1e-9, "n"), (1e-12, "p"), (1e-15, "f"), (1e-18, "a")]


def eng(v):
    if v is None:
        return "?"
    if v == 0:
        return "0"
    a = abs(v)
    for scale, suf in ENG:
        if a >= scale * 0.9995:
            m = v / scale
            s = f"{m:.3g}"
            if "e" in s:
                s = f"{m:.0f}"
            return s + suf
    return f"{v:.3g}"


# --------------------------------------------------------------------------
# transform helpers
# --------------------------------------------------------------------------
class Xf:
    """mirror (x -> -x) then rotate cw by rot*90 then translate."""

    def __init__(self, ox=0, oy=0, mirror=False, rot=0):
        self.ox, self.oy, self.mirror, self.rot = ox, oy, mirror, rot % 4

    def pt(self, x, y):
        if self.mirror:
            x = -x
        for _ in range(self.rot):
            x, y = -y, x
        return (x + self.ox, y + self.oy)

    def dir(self, d):
        if self.mirror:
            d = _MIR[d]
        for _ in range(self.rot):
            d = _ROT[d]
        return d

    def anchor(self, a):
        if self.rot % 2:
            return "middle"
        if self.mirror:
            return {"start": "end", "end": "start"}.get(a, a)
        return a


def transform(sym, xf):
    out = {"prims": [], "pins": {}, "keepout": [], "labels": [], "meta": sym.get("meta", {})}
    for p in sym["prims"]:
        k = p[0]
        if k == "line":
            (a, b), (c, d) = xf.pt(p[1], p[2]), xf.pt(p[3], p[4])
            out["prims"].append(("line", a, b, c, d, p[5]))
        elif k == "poly":
            out["prims"].append(("poly", [xf.pt(x, y) for x, y in p[1]], p[2]))
        elif k == "circle":
            cx, cy = xf.pt(p[1], p[2])
            out["prims"].append(("circle", cx, cy, p[3], p[4]))
        elif k == "polyline":
            out["prims"].append(("polyline", [xf.pt(x, y) for x, y in p[1]], p[2]))
        elif k == "text":
            x, y = xf.pt(p[1], p[2])
            out["prims"].append(("text", x, y, p[3], p[4], xf.anchor(p[5]) if len(p) > 5 else "middle"))
    for name, (x, y, d) in sym["pins"].items():
        px, py = xf.pt(x, y)
        out["pins"][name] = (px, py, xf.dir(d))
    for (x0, y0, x1, y1) in sym["keepout"]:
        a, b = xf.pt(x0, y0)
        c, d = xf.pt(x1, y1)
        out["keepout"].append((min(a, c), min(b, d), max(a, c), max(b, d)))
    for (x, y, parts, anchor) in sym.get("labels", []):
        lx, ly = xf.pt(x, y)
        out["labels"].append((lx, ly, parts, xf.anchor(anchor)))
    xs, ys = [], []
    for (x0, y0, x1, y1) in out["keepout"]:
        xs += [x0, x1]
        ys += [y0, y1]
    for (x, y, _) in out["pins"].values():
        xs.append(x)
        ys.append(y)
    out["bbox"] = (min(xs), min(ys), max(xs), max(ys))
    return out


# --------------------------------------------------------------------------
# transistor-level symbols (local coords, gate on the LEFT, channel at x = 0)
# --------------------------------------------------------------------------
def mos(typ, name, wl_text, m_text):
    """3-terminal MOSFET, Razavi style: arrow on the source
    (NMOS pointing out of the channel, PMOS pointing in)."""
    # Reference-figure (Razavi) style: the thick channel ends exactly at the drain/source
    # stubs; a wide gate-oxide gap (9 px) separates it from the gate plate; the body is
    # 21 px wide and 30 px tall; arrow on the source stub.
    pr = [
        ("line", -30, 0, -20, 0, "sym"),            # gate lead
        ("line", -20, -13, -20, 13, "sym gate"),    # gate plate
        ("line", -11, -15, -11, 15, "sym chan"),    # channel (thick)
        ("line", -11, -15, 0, -15, "sym"),          # upper stub
        ("line", 0, -15, 0, -30, "sym"),
        ("line", -11, 15, 0, 15, "sym"),            # lower stub
        ("line", 0, 15, 0, 30, "sym"),
    ]
    if typ == "pmos":
        # source on top, arrow pointing into the channel
        pr.append(("poly", [(-10.4, -15), (-4.6, -19), (-4.6, -11)], "sym arrow"))
        pins = {"s": (0, -30, "U"), "g": (-30, 0, "L"), "d": (0, 30, "D")}
    else:
        # arrow pointing away from the channel, towards the source lead
        pr.append(("poly", [(-0.6, 15), (-6.4, 11), (-6.4, 19)], "sym arrow"))
        pins = {"d": (0, -30, "U"), "g": (-30, 0, "L"), "s": (0, 30, "D")}
    labels = [
        (6, -12, [(name, "lbl-name")], "start"),
        (6, 1, [(wl_text, "lbl-wl")], "start"),
        (6, 13, [(m_text, "lbl-wl")], "start"),
    ]
    return {"prims": pr, "pins": pins,
            "keepout": [(-21, -29, 1, 29), (-29, -1, -20, 1)],
            "labels": labels,
            "meta": {"label_w": max(len(name), len(wl_text), len(m_text)) * 5.6 + 8}}


def resistor(name, val_text):
    zz = [(0, -18)]
    for i in range(6):
        zz.append((6 if i % 2 == 0 else -6, -15 + i * 6))
    zz.append((0, 18))
    pr = [("line", 0, -30, 0, -18, "sym"), ("polyline", zz, "sym"), ("line", 0, 18, 0, 30, "sym")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-7, -29, 7, 29)],
            "labels": [(11, -5, [(name, "lbl-name")], "start"), (11, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 12}}


def capacitor(name, val_text):
    pr = [("line", 0, -30, 0, -4, "sym"), ("line", -10, -4, 10, -4, "sym plate"),
          ("line", -10, 4, 10, 4, "sym plate"), ("line", 0, 4, 0, 30, "sym")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-11, -29, 11, 29)],
            "labels": [(14, -5, [(name, "lbl-name")], "start"), (14, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 14}}


def inductor(name, val_text):
    pr = [("line", 0, -30, 0, -16, "sym"), ("line", 0, 16, 0, 30, "sym")]
    for i in range(4):
        yc = -12 + i * 8
        pts = [(4 * math.sin(math.pi * k / 8), yc - 4 * math.cos(math.pi * k / 8)) for k in range(9)]
        pr.append(("polyline", pts, "sym"))
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-6, -29, 6, 29)],
            "labels": [(11, -5, [(name, "lbl-name")], "start"), (11, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 12}}


def source(kind, name, val_text):
    pr = [("line", 0, -30, 0, -12, "sym"), ("circle", 0, 0, 12, "sym"), ("line", 0, 12, 0, 30, "sym")]
    if kind == "vsrc":
        pr += [("text", 0, -3, "+", "sym-t", "middle"), ("text", 0, 8, "−", "sym-t", "middle")]
    else:
        pr += [("line", 0, 7, 0, -6, "sym"), ("poly", [(0, -8), (-3.5, -2), (3.5, -2)], "sym arrow")]
    return {"prims": pr, "pins": {"p": (0, -30, "U"), "n": (0, 30, "D")},
            "keepout": [(-13, -29, 13, 29)],
            "labels": [(16, -5, [(name, "lbl-name")], "start"), (16, 8, [(val_text, "lbl-val")], "start")],
            "meta": {"label_w": max(len(name), len(val_text)) * 5.6 + 16}}


def generic_box(name, pin_names, title=None):
    """Fallback symbol for anything we have no drawing for (E/G/D/Q/...)."""
    n = len(pin_names)
    left = pin_names[: (n + 1) // 2]
    right = pin_names[(n + 1) // 2:]
    h = max(2, max(len(left), len(right)) + 1) * 20
    w = 60
    pr = [("polyline", [(0, 0), (w, 0), (w, h), (0, h), (0, 0)], "sym"),
          ("text", w / 2, -6, title or name, "sym-t", "middle")]
    pins = {}
    for i, p in enumerate(left):
        y = 20 * (i + 1)
        pins[p] = (-20, y, "L")
        pr += [("line", -20, y, 0, y, "sym"), ("text", 4, y + 3, p, "pin-t", "start")]
    for i, p in enumerate(right):
        y = 20 * (i + 1)
        pins[p] = (w + 20, y, "R")
        pr += [("line", w, y, w + 20, y, "sym"), ("text", w - 4, y + 3, p, "pin-t", "end")]
    return {"prims": pr, "pins": pins, "keepout": [(-19, -1, w + 19, h + 1)], "labels": [],
            "meta": {"label_w": 0}}


# --------------------------------------------------------------------------
# rail / port glyphs
# --------------------------------------------------------------------------
VPIN_LEN = 20
_VPIN_LOCAL = {
    # attach point at (0, 0); the circuit lies towards +x; the body extends to -x
    "in": [(0, 0), (-7, -5), (-20, -5), (-20, 5), (-7, 5)],      # points into the circuit
    "out": [(0, -5), (-13, -5), (-20, 0), (-13, 5), (0, 5)],     # points out of the circuit
    "io": [(0, 0), (-5, -5), (-15, -5), (-20, 0), (-15, 5), (-5, 5)],
}
_VDIR = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}


def vpin_shape(kind, x, y, d):
    """Virtuoso schematic pin glyph. (x, y) is where the wire attaches, d is the direction
    from the pin towards the circuit."""
    dx, dy = _VDIR[d]
    px, py = -dy, dx
    return [(x + lx * dx + ly * px, y + lx * dy + ly * py) for lx, ly in _VPIN_LOCAL[kind]]


def vpin_body_rect(x, y, d):
    """keep-out rectangle of the glyph body (excludes the attach point)."""
    pts = [(x + lx * _VDIR[d][0], y + lx * _VDIR[d][1]) for lx in (-6, -20)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if d in "LR":
        return (min(xs), y - 6, max(xs), y + 6)
    return (x - 6, min(ys), x + 6, max(ys))


def ground_glyph(x, y):
    """Ground symbol hanging below (x, y)."""
    return [("line", x, y, x, y + 8, "sym"), ("line", x - 9, y + 8, x + 9, y + 8, "sym"),
            ("line", x - 6, y + 12, x + 6, y + 12, "sym"), ("line", x - 3, y + 16, x + 3, y + 16, "sym")]


def vdd_glyph(x, y, name):
    return [("line", x, y, x, y - 8, "sym"), ("line", x - 8, y - 8, x + 8, y - 8, "sym"),
            ("text", x, y - 12, name, "rail-t", "middle")]


# --------------------------------------------------------------------------
# block-level symbols
# --------------------------------------------------------------------------
def _pin_text(name):
    return name


def _arrow_in(x, y, d):
    """filled arrowhead with its tip at (x, y) pointing in direction d (R/U/L/D)"""
    if d == "R":
        pts = [(x, y), (x - 8, y - 4), (x - 8, y + 4)]
    elif d == "L":
        pts = [(x, y), (x + 8, y - 4), (x + 8, y + 4)]
    elif d == "U":
        pts = [(x, y), (x - 4, y + 8), (x + 4, y + 8)]
    else:
        pts = [(x, y), (x - 4, y - 8), (x + 4, y - 8)]
    return ("poly", pts, "arrowhead")


def _tw(names, size=9):
    return max([len(n) for n in names] + [0]) * size * 0.58


def block_symbol(shape, title, sides, pin_marks=None, arrows=()):
    """Build a block symbol.

    shape : 'amp' | 'inv' | 'sum' | 'box' | 'dff' | 'latch' | 'mux'
    sides : {'L': [pins], 'R': [pins], 'T': [pins], 'B': [pins]}
    pin_marks : {pin: '+' | '-' | 'clk'}  (polarity / clock markers)
    Local origin = top-left of the body.  Pins end on the 10 px grid.
    """
    pin_marks = pin_marks or {}
    L, R, T, B = (sides.get(k, []) for k in "LRTB")
    pr, pins = [], {}
    if shape in ("amp", "inv"):
        nl = max(len(L), 1)
        h = max(80, 20 * (nl + 1) + 20)
        h = int(math.ceil(h / 20.0) * 20)
        w = max(80, int(h * 0.9 // 20 * 20))
        mid = h / 2
        body = [(0, 0), (w, mid), (0, h), (0, 0)]
        pr.append(("polyline", body, "blk"))
        # left pins, spaced 20, centred
        ys = _spread(len(L), mid, 20)
        for p, y in zip(L, ys):
            pins[p] = (-20, y, "L")
            pr.append(("line", -20, y, 0, y, "blk"))
            if p in arrows:
                pr.append(_arrow_in(0, y, "R"))
            mk = pin_marks.get(p)
            if mk in ("+", "-"):
                pr.append(("text", 7, y + 3.5, "+" if mk == "+" else "−", "pol-t", "middle"))
        tip = w
        if shape == "inv":
            pr.append(("circle", w + 5, mid, 5, "blk"))
            tip = w + 10
        # right pins: on the slanted edges near the tip
        ys = _spread(len(R), mid, 20)
        for p, y in zip(R, ys):
            # x on the edge at height y
            ex = w * (1 - abs(y - mid) / mid) if mid else w
            if shape == "inv" and len(R) == 1:
                ex = tip
            px = int(math.ceil((max(ex, tip) + 20) / 10.0) * 10)
            pins[p] = (px, y, "R")
            pr.append(("line", ex, y, px, y, "blk"))
            mk = pin_marks.get(p)
            if mk in ("+", "-") and len(R) > 1:
                pr.append(("text", ex + 7, y + (-4 if y < mid else 11), "+" if mk == "+" else "−", "pol-t", "middle"))
        # top / bottom pins on the slanted edges
        for side, plist in (("T", T), ("B", B)):
            xs = [20 * (i + 1) for i in range(len(plist))]
            for p, x in zip(plist, xs):
                edge_y = mid * (x / w) if side == "T" else h - mid * (x / w)
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, edge_y, x, py, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, edge_y, "D" if side == "T" else "U"))
        if title:
            pr.append(("text", w * 0.36, mid + 4, title, "blk-t", "middle"))
        keep = [(-9, -9, w + 9, h + 9)]
        bw, bh = w, h
    elif shape == "sum":
        nb = max(len(B), len(T), 1)
        r = max(30, 10 * nb + 10)
        r = int(math.ceil(r / 10.0) * 10)
        cx = cy = r + 10
        pr.append(("circle", cx, cy, r, "blk"))
        pr.append(("text", cx, cy + 7, "Σ", "sum-t", "middle"))
        for side, plist in (("L", L), ("R", R)):
            ys = _spread(len(plist), cy, 20)
            for p, y in zip(plist, ys):
                dx = math.sqrt(max(r * r - (y - cy) ** 2, 0))
                ex = cx - dx if side == "L" else cx + dx
                px = -10 if side == "L" else 2 * cx + 10
                pins[p] = (px, y, side)
                pr.append(("line", px, y, ex, y, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(ex, y, "R" if side == "L" else "L"))
                mk = pin_marks.get(p)
                if mk in ("+", "-") and side == "L":
                    pr.append(("text", ex + 8, y + 3.5, "+" if mk == "+" else "−", "pol-t", "middle"))
        for side, plist in (("T", T), ("B", B)):
            xs = _spread(len(plist), cx, 20)
            for p, x in zip(plist, xs):
                dy = math.sqrt(max(r * r - (x - cx) ** 2, 0))
                ey = cy - dy if side == "T" else cy + dy
                py = -10 if side == "T" else 2 * cy + 10
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, ey, x, py, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, ey, "D" if side == "T" else "U"))
                mk = pin_marks.get(p)
                if mk in ("+", "-"):
                    pr.append(("text", x + (6 if x >= cx else -6), ey + (8 if side == "B" else -2),
                               "+" if mk == "+" else "−", "pol-t", "middle"))
        keep = [(cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9)]
        bw, bh = 2 * cx, 2 * cy
    elif shape in ("nand", "and", "nor", "or", "xor"):
        n = max(len(L), 2)
        h = max(60, 20 * (n + 1))
        h = int(math.ceil(h / 20.0) * 20)
        w = h
        mid = h / 2
        if shape in ("nand", "and"):
            body = [(0, 0), (w / 2, 0)]
            body += [(w / 2 + mid * math.sin(math.pi * k / 16), mid - mid * math.cos(math.pi * k / 16)) for k in range(1, 17)]
            body += [(0, h), (0, 0)]
            back = lambda y: 0.0
        else:
            back = lambda y: 10 * math.sin(math.pi * y / h)
            body = [(0, 0)]
            body += [(w * 0.55 * (k / 8.0) + w * 0.45 * (k / 8.0) ** 3, mid * (k / 8.0) ** 2) for k in range(1, 9)]
            body += [(w * 0.55 * (k / 8.0) + w * 0.45 * (k / 8.0) ** 3, h - mid * (k / 8.0) ** 2) for k in range(8, 0, -1)]
            body += [(0, h)]
            body += [(back(h - h * k / 12), h - h * k / 12) for k in range(1, 13)]
            if shape == "xor":
                pr.append(("polyline", [(back(h * k / 12) - 6, h * k / 12) for k in range(13)], "blk"))
        pr.append(("polyline", body, "blk"))
        ys = _spread(len(L), mid, 20)
        for p, y in zip(L, ys):
            pins[p] = (-20, y, "L")
            pr.append(("line", -20, y, back(y), y, "blk"))
            if p in arrows:
                pr.append(_arrow_in(back(y), y, "R"))
        tip = w + (10 if shape in ("nand", "nor") else 0)
        if shape in ("nand", "nor"):
            pr.append(("circle", w + 5, mid, 5, "blk"))
        for p, y in zip(R, _spread(len(R), mid, 20)):
            px = int(math.ceil((tip + 20) / 10.0) * 10)
            pins[p] = (px, y, "R")
            pr.append(("line", tip, y, px, y, "blk"))
        for side, plist in (("T", T), ("B", B)):
            for i, p in enumerate(plist):
                x = 20 * (i + 1)
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, 0 if side == "T" else h, x, py, "blk"))
        keep = [(-9, -9, w + 9 + (10 if shape in ("nand", "nor") else 0), h + 9)]
        bw, bh = w + (10 if shape in ("nand", "nor") else 0), h
    else:  # box family: box / dff / latch / mux
        tw = len(title or "") * 13 * 0.62 + 16
        tb = max(len(T), len(B))
        tb_pitch = max(40, int(math.ceil((_tw(T + B) + 14) / 10.0)) * 10)
        w = max(100, tw + _tw(L) + _tw(R) + 30, tb_pitch * (tb + 1))
        w = int(math.ceil(w / 20.0) * 20)
        n = max(len(L), len(R), 1)
        h = max(80, 20 * (n + 1) + 20)
        h = int(math.ceil(h / 20.0) * 20)
        if shape == "mux":
            body = [(0, 0), (w, 20), (w, h - 20), (0, h), (0, 0)]
        else:
            body = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
        pr.append(("polyline", body, "blk"))
        for side, plist in (("L", L), ("R", R)):
            ys = _spread(len(plist), h / 2, 20)
            for p, y in zip(plist, ys):
                px = -20 if side == "L" else w + 20
                pins[p] = (px, y, side)
                pr.append(("line", px, y, 0 if side == "L" else w, y, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(0 if side == "L" else w, y, "R" if side == "L" else "L"))
                txt = _pin_text(p)
                pr.append(("text", 5 if side == "L" else w - 5, y + 3.5, txt, "pin-t",
                           "start" if side == "L" else "end"))
        for side, plist in (("T", T), ("B", B)):
            xs = _spread(len(plist), w / 2, tb_pitch)
            for p, x in zip(plist, xs):
                py = -20 if side == "T" else h + 20
                pins[p] = (x, py, "U" if side == "T" else "D")
                pr.append(("line", x, py, x, 0 if side == "T" else h, "blk"))
                if p in arrows:
                    pr.append(_arrow_in(x, 0 if side == "T" else h, "D" if side == "T" else "U"))
                if pin_marks.get(p) == "clk" and shape == "dff":
                    pr.append(("polyline", [(x - 6, h), (x, h - 9), (x + 6, h)], "blk"))
                    pr.append(("text", x, h - 12, p, "pin-t", "middle"))
                else:
                    pr.append(("text", x, (12 if side == "T" else h - 6), p, "pin-t", "middle"))
        if title:
            pr.append(("text", w / 2, h / 2 + 5, title, "blk-t", "middle"))
        keep = [(-9, -9, w + 9, h + 9)]
        bw, bh = w, h
    return {"prims": pr, "pins": pins, "keepout": keep, "labels": [],
            "meta": {"w": bw, "h": bh}}


def _spread(n, center, pitch):
    """n positions on the 10-grid, `pitch` apart, centred on `center`."""
    if n == 0:
        return []
    start = center - pitch * (n - 1) / 2.0
    out = []
    for i in range(n):
        v = start + i * pitch
        out.append(int(round(v / 10.0)) * 10)
    return out
````

### FILE: hspice-schematic/scripts/hsch/router.py
<!-- sha256=57636c8eef5aab19776452b3e7c604c1c65bd37f5a3455c237812d8de20ab157 newline=1 -->
````python
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
````

### FILE: hspice-schematic/scripts/hsch/layout_leaf.py
<!-- sha256=1ae1c57851d4c47cfecd5ea26a06c7943ae532d1ac6c6be07ba36c8fcad266b4 newline=1 -->
````python
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
                warnings.append(f"{sup}: could not reach rail from ({fx},{fy}); using local symbol")
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
            warnings.append(f"{net}: unroutable pin at ({fx},{fy}) - connected by name label")
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
    for s_ in sc["symbols"]:
        xs += [s_["bbox"][0], s_["bbox"][2]]
        ys += [s_["bbox"][1], s_["bbox"][3]]
        for (lx, ly, parts, anc) in s_["labels"]:
            w = len("".join(t for t, _ in parts)) * CHAR
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
````

### FILE: hspice-schematic/scripts/hsch/layout_block.py
<!-- sha256=0025b38f5b4a22ec17b4374deda220977250b265e9a17609162c4a5512830377 newline=1 -->
````python
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
        inst_label = d["name"] if not d.get("auto") else "(auto)"
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
            warnings.append(f"{n}: unroutable pin at ({fx},{fy}) - connected by name label")
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
````

### FILE: hspice-schematic/scripts/hsch/render.py
<!-- sha256=80765cc47157a3cdd7dea7ac791453e7d293820f7c16c1ebf7aa5c5b906257d8 newline=1 -->
````python
"""Scene -> single self-contained HTML file (inline SVG + vanilla JS viewer)."""
from __future__ import annotations

import html
import json
import os

from .geom import vpin_shape

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "..", "assets")


def _f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


def _e(s):
    return html.escape(str(s), quote=True)


def prim_svg(p):
    k = p[0]
    if k == "line":
        return f'<line class="{p[5]}" x1="{_f(p[1])}" y1="{_f(p[2])}" x2="{_f(p[3])}" y2="{_f(p[4])}"/>'
    if k == "polyline":
        pts = " ".join(f"{_f(x)},{_f(y)}" for x, y in p[1])
        return f'<polyline class="{p[2]}" points="{pts}"/>'
    if k == "poly":
        pts = " ".join(f"{_f(x)},{_f(y)}" for x, y in p[1])
        return f'<polygon class="{p[2]}" points="{pts}"/>'
    if k == "circle":
        return f'<circle class="{p[4]}" cx="{_f(p[1])}" cy="{_f(p[2])}" r="{_f(p[3])}"/>'
    if k == "path":
        return f'<path class="{p[2]}" d="{p[1]}"/>'
    if k == "text":
        anc = p[5] if len(p) > 5 else "middle"
        return f'<text class="{p[4]}" x="{_f(p[1])}" y="{_f(p[2])}" text-anchor="{anc}">{_e(p[3])}</text>'
    return ""


def _path_d(prims_path, ox=0, oy=0):
    return prims_path


def scene_svg(sc):
    x0, y0, x1, y1 = sc["bounds"]
    out = [f'<svg class="sch" xmlns="http://www.w3.org/2000/svg" data-cell="{_e(sc["cell"])}" '
           f'viewBox="{_f(x0)} {_f(y0)} {_f(x1 - x0)} {_f(y1 - y0)}" data-bounds="{_f(x0)},{_f(y0)},{_f(x1)},{_f(y1)}">']
    out.append('<g class="layer-wires">')
    for w in sc["wires"]:
        out.append(f'<line class="wire{" diag" if w.get("diag") else ""}" data-net="{_e(w["net"])}" x1="{_f(w["x1"])}" y1="{_f(w["y1"])}" '
                   f'x2="{_f(w["x2"])}" y2="{_f(w["y2"])}"/>')
    out.append("</g>")
    out.append('<g class="layer-syms">')
    for s in sc["symbols"]:
        is_blk = s["kind"] == "X"
        cls = "symg blkg clickable" if is_blk else "symg dev"
        keep = ";".join(",".join(_f(v) for v in r) for r in s.get("keepout", []))
        attrs = f'class="{cls}" data-inst="{_e(s["inst"])}" data-keep="{keep}"'
        if is_blk:
            attrs += f' data-ref="{_e(s["ref"])}" data-hidden="{_e(",".join(s.get("hidden_pins", [])))}"'
            if s.get("body"):
                attrs += f' data-body="{",".join(_f(v) for v in s["body"])}"'
        else:
            attrs += f' data-type="{_e(s["type"])}"'
        out.append(f"<g {attrs}>")
        if is_blk:
            bx0, by0, bx1, by1 = s["bbox"]
            out.append(f'<rect class="hit" x="{_f(bx0)}" y="{_f(by0)}" width="{_f(bx1 - bx0)}" height="{_f(by1 - by0)}"/>')
        for p in s["prims"]:
            out.append(prim_svg(p))
        for (lx, ly, parts, anchor) in s["labels"]:
            spans = "".join(f'<tspan class="{c}">{_e(t)}</tspan>' if c else _e(t) for t, c in parts)
            out.append(f'<text class="devlbl" x="{_f(lx)}" y="{_f(ly)}" text-anchor="{anchor}">{spans}</text>')
        out.append("</g>")
    out.append("</g>")
    out.append('<g class="layer-rails">')
    for r in sc["rails"]:
        out.append(f'<g class="rail" data-net="{_e(r["net"])}" data-ax="{_f(r["x"])}" data-ay="{_f(r["y"])}">')
        for p in r["prims"]:
            out.append(prim_svg(p))
        if r.get("named"):
            out.append(f'<text class="rail-t" x="{_f(r["x"] + 12)}" y="{_f(r["y"] + 16)}">{_e(r["net"])}</text>')
        out.append("</g>")
    out.append("</g>")
    out.append('<g class="layer-dots">')
    for d in sc["dots"]:
        out.append(f'<circle class="dot" data-net="{_e(d["net"])}" cx="{_f(d["x"])}" cy="{_f(d["y"])}" r="2.6"/>')
    out.append("</g>")
    out.append('<g class="layer-labels">')
    for t in sc["terminals"]:
        cls = "term port" if t["port"] else ("term bylabel" if t.get("by_label") else "term")
        out.append(f'<g class="{cls}" data-net="{_e(t["net"])}" data-ax="{_f(t["x"])}" data-ay="{_f(t["y"])}">')
        if t.get("vpin"):
            pts = vpin_shape(t["vpin"], t["x"], t["y"], t["vdir"])
            out.append(f'<polygon class="vpin vpin-{t["vpin"]}" points="' + " ".join(f"{_f(a)},{_f(b)}" for a, b in pts) + '"/>')
        if (t["port"] or t.get("portsym")) and not t.get("plain"):
            out.append(f'<circle class="termc" cx="{_f(t["x"])}" cy="{_f(t["y"])}" r="3.2"/>')
        if t.get("arrow"):
            x, y = t["x"], t["y"]
            pts = ([(x + 4, y), (x - 5, y - 4), (x - 5, y + 4)] if t["arrow"] == "R"
                   else [(x - 4, y), (x + 5, y - 4), (x + 5, y + 4)])
            out.append('<polygon class="arrowhead" points="' + " ".join(f"{_f(a)},{_f(b)}" for a, b in pts) + '"/>')
        rot = (f' transform="rotate(-90 {_f(t["tx"])} {_f(t["ty"])})" data-rot="1"' if t.get("rot") else "")
        out.append(f'<text class="term-t" x="{_f(t["tx"])}" y="{_f(t["ty"])}" text-anchor="{t["anchor"]}"{rot}>{_e(t["net"])}</text>')
        out.append("</g>")
    for l in sc["labels"]:
        out.append(f'<text class="netlabel {l["cls"]}" data-net="{_e(l["net"])}" data-ax="{_f(l["ax"])}" '
                   f'data-ay="{_f(l["ay"])}" x="{_f(l["x"])}" y="{_f(l["y"])}" text-anchor="{l["anchor"]}">{_e(l["text"])}</text>')
    out.append("</g>")
    out.append('<g class="layer-pins">')
    for p in sc["pins"]:
        out.append(f'<circle class="pin" data-inst="{_e(p["inst"])}" data-pin="{_e(p["pin"])}" '
                   f'data-net="{_e(p["net"])}" cx="{_f(p["x"])}" cy="{_f(p["y"])}" r="2"/>')
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def render_html(scenes, info, title, out_path, pptx_path=None):
    with open(os.path.join(ASSETS, "viewer.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ASSETS, "viewer.js"), encoding="utf-8") as f:
        js = f.read()
    views = []
    for cell, sc in scenes.items():
        views.append(f'<div class="view" data-cell="{_e(cell)}" hidden>{scene_svg(sc)}</div>')
    data = json.dumps(info, ensure_ascii=False).replace("</", "<\\/")
    ppt_btn, ppt_blob = "", ""
    if pptx_path and os.path.exists(pptx_path):
        import base64
        with open(pptx_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        name = os.path.basename(pptx_path)
        ppt_btn = '<button id="btn-ppt" title="PowerPoint에서 수정 가능한 파일 (셀마다 슬라이드 1장)">⬇ PPT</button>'
        ppt_blob = f'<script id="hsch-pptx" type="application/octet-stream" data-name="{_e(name)}">{b64}</script>'

    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)}</title>
<style>{css}</style>
</head>
<body>
<header class="bar">
  <div class="crumbs" id="crumbs"></div>
  <div class="tools">
    <label><input type="checkbox" data-toggle="wl" checked> W/L·m</label>
    <label><input type="checkbox" data-toggle="val" checked> R/C 값</label>
    <label><input type="checkbox" data-toggle="name" checked> 소자 이름</label>
    <label><input type="checkbox" data-toggle="net"> 넷 이름</label>
    <button id="btn-up" title="상위 블록 (Esc)">↑ 상위</button>
    <button id="btn-fit" title="화면 맞춤 (F)">⤢ 맞춤</button>
    {ppt_btn}
    <select id="cell-jump" title="셀로 이동"></select>
  </div>
</header>
<main>
  <section class="canvas" id="canvas">
    {''.join(views)}
    <div class="tip" id="tip" hidden></div>
  </section>
  <aside class="side" id="side"></aside>
</main>
<script id="hsch-data" type="application/json">{data}</script>
{ppt_blob}
<script>{js}</script>
</body>
</html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path
````

### FILE: hspice-schematic/scripts/hsch/verify.py
<!-- sha256=8a81ad0b4a7a5534b736024a61d54408efbf1be54d06d0737c6a0fb5a1e1ea0c newline=1 -->
````python
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


def text_box(txt, x, y, anchor, size, rot=False):
    w = len(txt) * size * 0.58
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
            dangling.append(f"{kind} '{name}' at ({x:g},{y:g}) touches nothing")
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
                    errors.append(f"{d['name']}.{p}: hidden pin but net {n} is not a supply")
                continue
            ir_pin_net[(d["name"], p)] = n
    for (inst, pin) in groups:
        if inst == "PORT":
            ir_pin_net.setdefault((inst, pin), pin)
    drawn = set(groups)
    for k in ir_pin_net:
        if k not in drawn:
            errors.append(f"pin {k[0]}.{k[1]} not drawn")
    for k in drawn:
        if k not in ir_pin_net:
            errors.append(f"drawn pin {k[0]}.{k[1]} does not exist in netlist")
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
            errors.append(f"OPEN: net {n} drawn as {len(gs)} pieces: " + " | ".join(parts))
    for g, ns in group_nets.items():
        if len(ns) > 1:
            errors.append(f"SHORT: nets {', '.join(sorted(ns))} are connected in the drawing")
    for g, labelset in info["names"].items():
        ns = group_nets.get(g, set())
        for lab in labelset:
            if ns and lab not in ns:
                errors.append(f"label '{lab}' sits on net {', '.join(sorted(ns))}")
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
        errors.append(f"port {p} is not named anywhere in the drawing")

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
            lint.append(f"4-way junction at ({x:g},{y:g})")
        if branches == 3 and (x, y) not in dots:
            lint.append(f"T-junction without dot at ({x:g},{y:g})")
    for (x, y) in dots:
        ends, inter = info["junctions"].get((x, y), ([], []))
        pins_here = sum(1 for _, _, px, py in view["pins"] if px == x and py == y)
        if len(ends) + 2 * len(inter) + pins_here < 3:
            lint.append(f"dot at ({x:g},{y:g}) is not on a junction")
    for s in view["symbols"]:
        for (x0, y0, x1, y1) in s["keep"]:
            for w in W:
                if _seg_hits_rect(w, (x0 + 1, y0 + 1, x1 - 1, y1 - 1)):
                    lint.append(f"wire passes through {s['inst']}")
                    break
    lint += [f"pin {p} lands on the middle of a wire" for p in info["pin_on_interior"]]
    T = view["texts"]
    over = 0
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            if _ov(_shrink(T[i]["box"]), _shrink(T[j]["box"])):
                over += 1
                lint.append(f"text overlap: '{T[i]['txt']}' / '{T[j]['txt']}'")
    for t in T:
        b = _shrink(t["box"], 1.5)
        for w in W:
            if _seg_hits_rect(w, b):
                over += 1
                lint.append(f"text '{t['txt']}' overlaps a wire")
                break
        for sg in view.get("symsegs", []):
            if _seg_hits_rect(sg[:4], b):
                over += 1
                lint.append(f"text '{t['txt']}' overlaps the drawing of {view['symbols'][sg[4]]['inst']}")
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
                lint.append(f"text '{t['txt']}' overlaps symbol {s_['inst']}")
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
                lint.append(f"pair {a}/{b} not at the same height")
                continue
            if "g" in pa and "g" in pb:
                ca = [x for p, (x, _) in pa.items() if p != "g"][0]
                cb = [x for p, (x, _) in pb.items() if p != "g"][0]
                if abs((pa["g"][0] - ca) + (pb["g"][0] - cb)) > 0.5:
                    lint.append(f"pair {a}/{b} is not drawn as a mirror image")
    # textbook conventions
    ys = {"pmos": [], "nmos": []}
    for d in cell["devices"]:
        if d["kind"] == "M":
            pts = [p for p in view["pins"] if p[0] == d["name"]]
            if pts:
                ys[d["type"]].append(sum(p[3] for p in pts) / len(pts))
    if ys["pmos"] and ys["nmos"] and min(ys["pmos"]) > max(ys["nmos"]):
        lint.append("PMOS devices are drawn below NMOS devices")
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
````

### FILE: hspice-schematic/scripts/hsch/export_pptx.py
<!-- sha256=4b9f4f9fcf32a79968be124a41c881c8c99b89335b5f84411eb3d579ea78a46f newline=1 -->
````python
"""Scene -> editable PowerPoint (.pptx).

Everything is a native PowerPoint shape, so the drawing can be edited in PowerPoint:
  * one slide per cell of the hierarchy (same order as the viewer)
  * every device / block / pin is a named group (move it as one piece)
  * every wire is a straight line, grouped per net ("net QP")
  * every label is a real text box (W/L, names, values, pin names)
  * clicking a block in slide-show mode jumps to the slide of its cell, and each lower
    level has a "▲ parent" link back - the same drill-down as the HTML viewer
"""
from __future__ import annotations

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .geom import vpin_shape

INK = RGBColor(0x11, 0x11, 0x11)
BLUE = RGBColor(0x1D, 0x5F, 0xA8)
GREY = RGBColor(0x55, 0x55, 0x55)
PURPLE = RGBColor(0x6B, 0x4F, 0x9E)
RED = RGBColor(0xE8, 0x26, 0x1C)
DARKRED = RGBColor(0x8C, 0x0D, 0x07)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# font px per text class (same as the viewer CSS), plus style
TEXT_STYLE = {
    "lbl-name": (9, GREY, False, True), "lbl-wl": (9, BLUE, False, False),
    "lbl-val": (9, BLUE, False, False), "lbl-cell": (9, RGBColor(0x77, 0x77, 0x77), False, False),
    "lbl-net": (10, PURPLE, False, True), "lbl-port": (10, INK, True, False),
    "lbl-rail": (10, INK, True, False), "term-t": (10, INK, True, False),
    "pin-t": (9, RGBColor(0x33, 0x33, 0x33), False, False), "blk-t": (13, INK, True, False),
    "sum-t": (22, INK, False, False), "pol-t": (12, INK, True, False),
    "rail-t": (10, INK, True, False), "sym-t": (10, INK, False, False),
}
STROKE = {"chan": 3.2, "gate": 2.0, "plate": 2.2}

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
MARGIN_X, TOP, BOTTOM = Inches(0.35), Inches(0.75), Inches(0.3)


class _Map:
    def __init__(self, bounds):
        x0, y0, x1, y1 = bounds
        w = SLIDE_W - 2 * MARGIN_X
        h = SLIDE_H - TOP - BOTTOM
        self.s = min(w / max(x1 - x0, 1), h / max(y1 - y0, 1))     # EMU per px
        self.ox = MARGIN_X + (w - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = TOP + (h - (y1 - y0) * self.s) / 2 - y0 * self.s

    def x(self, v):
        return Emu(int(self.ox + v * self.s))

    def y(self, v):
        return Emu(int(self.oy + v * self.s))

    def d(self, v):
        return Emu(max(1, int(v * self.s)))

    def pt(self, px):
        return Pt(max(px * self.s / 12700.0, 0.25))


def _style_line(line, m, width_px=1.6, color=INK):
    line.color.rgb = color
    line.width = m.pt(width_px)


def _line(shapes, m, x1, y1, x2, y2, width_px=1.6, color=INK, name=None):
    c = shapes.add_connector(MSO_CONNECTOR.STRAIGHT, m.x(x1), m.y(y1), m.x(x2), m.y(y2))
    _style_line(c.line, m, width_px, color)
    if name:
        c.name = name
    return c


def _poly(shapes, m, pts, closed, fill=None, width_px=1.6, color=INK):
    fb = shapes.build_freeform(m.x(pts[0][0]), m.y(pts[0][1]), scale=1.0)
    fb.add_line_segments([(m.x(x), m.y(y)) for x, y in pts[1:]], close=closed)
    shp = fb.convert_to_shape()
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    _style_line(shp.line, m, width_px, color)
    shp.shadow.inherit = False
    return shp


def _circle(shapes, m, cx, cy, r, fill=None, width_px=1.6, color=INK):
    shp = shapes.add_shape(MSO_SHAPE.OVAL, m.x(cx - r), m.y(cy - r), m.d(2 * r), m.d(2 * r))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if width_px:
        _style_line(shp.line, m, width_px, color)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def _text(shapes, m, x, y, runs, anchor="start", rot=False, name=None):
    """runs: [(text, css_class)]; (x, y) is the SVG text anchor / baseline."""
    runs = [(t, c) for t, c in runs if t]
    if not runs:
        return None
    size = max(TEXT_STYLE.get(c, (10,))[0] for _, c in runs)
    n = sum(len(t) for t, _ in runs)
    w = n * size * 0.62 + 4
    h = size * 1.35
    if rot:   # rotate(-90): text runs upwards from (x, y) for anchor=start
        cx = x - size * 0.3
        cy = y - w / 2 if anchor == "start" else (y + w / 2 if anchor == "end" else y)
        left, top = cx - w / 2, cy - h / 2
    else:
        left = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
        if anchor == "start":
            left -= 1
        top = y - size * 1.0
    tb = shapes.add_textbox(m.x(left), m.y(top), m.d(w), m.d(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = {"start": PP_ALIGN.LEFT, "end": PP_ALIGN.RIGHT}.get(anchor, PP_ALIGN.CENTER)
    for t, c in runs:
        px, color, bold, italic = TEXT_STYLE.get(c, (10, INK, False, False))
        r = p.add_run()
        r.text = t
        r.font.size = m.pt(px)
        r.font.name = "Arial"
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    if rot:
        tb.rotation = 270
    if name:
        tb.name = name
    return tb


def _transparent(shape):
    from pptx.oxml.ns import qn
    clr = shape.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    a = clr.makeelement(qn("a:alpha"), {"val": "0"})
    clr.append(a)


def _prims(shapes, m, prims):
    for p in prims:
        k = p[0]
        if k == "line":
            cls = p[5].split()
            w = max([STROKE.get(c, 0) for c in cls] + [1.6])
            _line(shapes, m, p[1], p[2], p[3], p[4], w)
        elif k == "polyline":
            closed = len(p[1]) > 2 and p[1][0] == p[1][-1]
            pts = p[1][:-1] if closed else p[1]
            fill = WHITE if ("blk" in p[2] and closed) else None
            _poly(shapes, m, pts, closed, fill=fill)
        elif k == "poly":
            _poly(shapes, m, p[1], True, fill=INK, width_px=0.6)
        elif k == "circle":
            _circle(shapes, m, p[1], p[2], p[3], fill=WHITE if "blk" in p[4] else None)
        elif k == "text":
            _text(shapes, m, p[1], p[2], [(p[3], p[4].split()[0])], p[5] if len(p) > 5 else "middle")


def export_pptx(scenes, info, order, out_path, title=None, show_net_names=False):
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    blank = prs.slide_layouts[6]
    slides = {c: prs.slides.add_slide(blank) for c in order}
    parent_of = {}
    for c in order:
        for s in scenes[c]["symbols"]:
            if s["kind"] == "X" and s["ref"] in slides:
                parent_of.setdefault(s["ref"], (c, s["inst"]))
    for c in order:
        sc, slide = scenes[c], slides[c]
        m = _Map(sc["bounds"])
        ci = info["cells"].get(c, {})
        head = slide.shapes.add_textbox(Inches(0.35), Inches(0.2), Inches(9), Inches(0.4))
        tp = head.text_frame.paragraphs[0]
        r = tp.add_run()
        r.text = ci.get("display", c)
        r.font.size, r.font.bold, r.font.name = Pt(20), True, "Arial"
        r = tp.add_run()
        r.text = "   " + ci.get("label", "") + ("  ·  connectivity verified" if ci.get("verify", {}).get("ok") else "")
        r.font.size, r.font.name = Pt(11), "Arial"
        r.font.color.rgb = GREY
        if c in parent_of:
            pc, pinst = parent_of[c]
            up = slide.shapes.add_textbox(Inches(10.4), Inches(0.22), Inches(2.6), Inches(0.35))
            up.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
            ur = up.text_frame.paragraphs[0].add_run()
            ur.text = f"▲ {pc}"
            ur.font.size, ur.font.name = Pt(11), "Arial"
            ur.font.color.rgb = BLUE
            up.click_action.target_slide = slides[pc]
            up.name = "link to parent"
        # wires, one group per net
        by_net = {}
        for w in sc["wires"]:
            by_net.setdefault(w["net"], []).append(w)
        for d in sc["dots"]:
            by_net.setdefault(d["net"], [])
        for net, ws in by_net.items():
            g = slide.shapes.add_group_shape()
            g.name = f"net {net}"
            for w in ws:
                _line(g.shapes, m, w["x1"], w["y1"], w["x2"], w["y2"])
            for d in sc["dots"]:
                if d["net"] == net:
                    _circle(g.shapes, m, d["x"], d["y"], 2.6, fill=INK, width_px=0)
            if not ws and not any(d["net"] == net for d in sc["dots"]):
                g._element.getparent().remove(g._element)
        # devices / blocks
        for s in sc["symbols"]:
            g = slide.shapes.add_group_shape()
            g.name = s["inst"]
            if s["kind"] == "X" and s["ref"] in slides:
                bx0, by0, bx1, by1 = s.get("body") or s["bbox"]
                hit = g.shapes.add_shape(MSO_SHAPE.RECTANGLE, m.x(bx0), m.y(by0), m.d(bx1 - bx0), m.d(by1 - by0))
                hit.fill.solid()
                hit.fill.fore_color.rgb = WHITE
                _transparent(hit)                    # invisible click target
                hit.line.fill.background()
                hit.shadow.inherit = False
                hit.click_action.target_slide = slides[s["ref"]]
                hit.name = f"open {s['ref']}"
            _prims(g.shapes, m, s["prims"])
            for (lx, ly, parts, anc) in s["labels"]:
                _text(g.shapes, m, lx, ly, parts, anc)
        # rails
        for r_ in sc["rails"]:
            g = slide.shapes.add_group_shape()
            g.name = f"{r_['kind']} {r_['net']}"
            _prims(g.shapes, m, r_["prims"])
            if r_.get("named"):
                _text(g.shapes, m, r_["x"] + 12, r_["y"] + 16, [(r_["net"], "rail-t")], "start")
        # pins and name tags
        for t in sc["terminals"]:
            g = slide.shapes.add_group_shape()
            g.name = f"pin {t['net']}" if t.get("vpin") else f"label {t['net']}"
            if t.get("vpin"):
                _poly(g.shapes, m, vpin_shape(t["vpin"], t["x"], t["y"], t["vdir"]), True,
                      fill=RED, width_px=0.9, color=DARKRED)
            _text(g.shapes, m, t["tx"], t["ty"], [(t["net"], "term-t")], t["anchor"], rot=t.get("rot", False))
        for l in sc["labels"]:
            if l["cls"] == "lbl-net" and not show_net_names:
                continue     # same default as the viewer ("넷 이름" off)
            _text(slide.shapes, m, l["x"], l["y"], [(l["text"], l["cls"])], l["anchor"], name=f"label {l['net']}")
        notes = slide.notes_slide.notes_text_frame
        notes.text = (f"{c}: {ci.get('label', '')}. Recognised because: {ci.get('reason', '')}.\n"
                      f"Ports: {', '.join(ci.get('ports', []))}")
    prs.save(out_path)
    return out_path
````

### FILE: hspice-schematic/scripts/screenshot.js
<!-- sha256=d1e98517be301cc7303ada1bdb7a2c03851e37fdc81d9d0dc18517bc3d808d8d newline=1 -->
````javascript
#!/usr/bin/env node
// usage: node screenshot.js schematic.html OUTDIR [--scale 1|2] [--width 1400] [--height 900]
// Renders every cell view of the schematic to OUTDIR/<cell>.png for visual review.
const path = require("path");
const fs = require("fs");
let pw;
try { pw = require("playwright"); } catch (e) { console.error("playwright not available"); process.exit(2); }

(async () => {
  const args = process.argv.slice(2);
  const html = path.resolve(args[0]);
  const out = path.resolve(args[1] || "shots");
  const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? Number(args[i + 1]) : d; };
  fs.mkdirSync(out, { recursive: true });
  const browser = await pw.chromium.launch();
  const page = await browser.newPage({
    viewport: { width: opt("--width", 1400), height: opt("--height", 900) },
    deviceScaleFactor: opt("--scale", 1),
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto("file://" + html);
  const cells = await page.evaluate(() => window.HSCH.cells());
  for (const c of cells) {
    await page.evaluate((cell) => window.HSCH.show(cell), c);
    await page.waitForTimeout(50);
    const file = path.join(out, c + ".png");
    await page.locator("#canvas").screenshot({ path: file });
    console.log(file);
  }
  await browser.close();
  if (errors.length) { console.error("page errors:\n" + errors.join("\n")); process.exit(1); }
})();
````

### FILE: hspice-schematic/scripts/ui_selftest.js
<!-- sha256=5e0db59bc0950cd7a06e53032f9f4506bff43ff8a80dfa9f6b41759c80123235 newline=1 -->
````javascript
#!/usr/bin/env node
// Viewer self-test: presses every control on desktop and on an emulated phone (real touch
// events) and asserts what must hold afterwards: the drawing stays on screen, pans 1:1 with
// the pointer, toggles change only labels, navigation lands on the right cell, no tooltip is
// left behind, no JS errors.
// usage: node ui_selftest.js schematic.html      (exit code 1 on any failure)
const path = require("path");
const pw = require("playwright");

const html = "file://" + path.resolve(process.argv[2]);
let fails = 0, passes = 0;
function check(name, ok, detail) {
  if (ok) passes++; else fails++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${ok || !detail ? "" : "  -> " + detail}`);
}

async function probe(p) {
  return p.evaluate(() => {
    const v = document.querySelector(".view:not([hidden])");
    const svg = v.querySelector("svg");
    const c = document.getElementById("canvas").getBoundingClientRect();
    const g = v.querySelector(".layer-syms").getBoundingClientRect();
    const pin = v.querySelector("circle.pin").getBoundingClientRect();   // never hidden by toggles
    const ix = Math.max(0, Math.min(g.right, c.right) - Math.max(g.left, c.left));
    const iy = Math.max(0, Math.min(g.bottom, c.bottom) - Math.max(g.top, c.top));
    const vis = (ix * iy) / Math.max(1, Math.min(g.width * g.height, c.width * c.height));
    return {
      cell: v.dataset.cell, vb: svg.getAttribute("viewBox").split(" ").map(Number),
      bounds: svg.getAttribute("data-bounds").split(",").map(Number),
      gx: pin.x, gy: pin.y, gw: g.width, vis,
      tip: !document.getElementById("tip").hidden,
      crumbs: document.querySelectorAll("#crumbs a").length,
      hl: v.querySelectorAll(".hl").length,
      body: document.body.className,
    };
  });
}
const near = (a, b, tol = 2) => Math.abs(a - b) <= tol;
const sameVB = (a, b) => a.vb.every((x, i) => near(x, b.vb[i], 0.01));
const fitted = (s) => near(s.vb[0], s.bounds[0], 0.01) && near(s.vb[2], s.bounds[2] - s.bounds[0], 0.01);
const TOG = { wl: ".lbl-wl", val: ".lbl-val", name: ".lbl-name", net: ".lbl-net" };

async function toggleChecks(p, label, tapFn) {
  for (const [t, sel] of Object.entries(TOG)) {
    const before = await probe(p);
    const disp0 = await p.evaluate((s) => { const e = document.querySelector(".view:not([hidden]) " + s); return e ? getComputedStyle(e).display : null; }, sel);
    await tapFn(`[data-toggle="${t}"]`);
    const after = await probe(p);
    const disp1 = await p.evaluate((s) => { const e = document.querySelector(".view:not([hidden]) " + s); return e ? getComputedStyle(e).display : null; }, sel);
    check(`${label}: toggle ${t} keeps the drawing in place`, sameVB(before, after) && near(before.gx, after.gx) && near(before.gy, after.gy),
          `vb ${before.vb} -> ${after.vb}, content (${before.gx|0},${before.gy|0}) -> (${after.gx|0},${after.gy|0})`);
    if (disp0 !== null) check(`${label}: toggle ${t} switches its labels`, disp0 !== disp1, `${disp0} -> ${disp1}`);
    await tapFn(`[data-toggle="${t}"]`);
    const back = await probe(p);
    check(`${label}: toggle ${t} twice restores`, sameVB(before, back) && back.body === before.body,
          `vb ${before.vb} -> ${back.vb}, body '${before.body}' -> '${back.body}'`);
  }
}

async function desktop(b) {
  const p = await b.newPage({ viewport: { width: 1300, height: 850 } });
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(html);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload();
  let s = await probe(p);
  const top = s.cell;
  check("desktop: opens on the top cell, fitted, visible", fitted(s) && s.vis > 0.9 && !s.tip);
  await toggleChecks(p, "desktop", (sel) => p.click(sel));

  // mouse drag pans 1:1
  const c = await p.locator("#canvas").boundingBox();
  const cx = c.x + c.width / 2, cy = c.y + c.height / 2;
  s = await probe(p);
  await p.mouse.move(cx + 200, cy + 150); await p.mouse.down();
  await p.mouse.move(cx + 260, cy + 180, { steps: 6 }); await p.mouse.move(cx + 300, cy + 200, { steps: 6 });
  await p.mouse.up();
  let s2 = await probe(p);
  check("desktop: drag pans 1:1", near(s2.gx - s.gx, 100) && near(s2.gy - s.gy, 50), `moved (${(s2.gx - s.gx).toFixed(1)},${(s2.gy - s.gy).toFixed(1)}) expected (100,50)`);
  check("desktop: drag does not navigate", s2.cell === top);
  await toggleChecks(p, "desktop after pan", (sel) => p.click(sel));

  // wheel zoom + clamp
  s = await probe(p);
  await p.mouse.move(cx, cy); await p.mouse.wheel(0, -400); await p.waitForTimeout(50);
  s2 = await probe(p);
  check("desktop: wheel zooms in", s2.vb[2] < s.vb[2] && s2.vis > 0.05);
  for (let i = 0; i < 40; i++) await p.mouse.wheel(0, 2000);
  s2 = await probe(p);
  check("desktop: zoom-out is clamped", s2.vb[2] <= (s2.bounds[2] - s2.bounds[0]) * 20 + 1 && s2.vis > 0);
  await p.click("#btn-fit");
  check("desktop: 맞춤 restores the full view", fitted(await probe(p)));
  await p.mouse.wheel(0, -500); await p.mouse.dblclick(c.x + 30, c.y + 30);
  check("desktop: double-click fits", fitted(await probe(p)));

  // hover tooltip
  const dev = p.locator('.view:not([hidden]) .symg[data-inst="X_CTLE"] .hit, .view:not([hidden]) .symg .hit').first();
  await dev.hover({ force: true });
  check("desktop: hover on a block shows a tooltip", (await probe(p)).tip);
  await p.mouse.move(c.x + 5, c.y + 5);
  check("desktop: moving away hides it", !(await probe(p)).tip);

  // navigation by click, breadcrumb, 상위, keys
  const blocks = await p.$$eval(".view:not([hidden]) .symg.clickable", (els) => els.map((e) => [e.dataset.inst, e.dataset.ref]));
  for (const [inst, ref] of blocks) {
    await p.locator(`.view:not([hidden]) .symg[data-inst="${inst}"] .hit`).click({ force: true });
    s = await probe(p);
    check(`desktop: click ${inst} opens ${ref}`, s.cell === ref && s.crumbs === 2 && !s.tip && s.vis > 0.9 && fitted(s), JSON.stringify(s));
    await p.click("#btn-up");
    check(`desktop: 상위 returns from ${ref}`, (await probe(p)).cell === top);
  }
  // deepest path, breadcrumb jump, Esc / Backspace / F
  async function deepest() {
    for (let d = 0; d < 8; d++) {
      const all = await p.$$(".view:not([hidden]) .symg.clickable .hit");
      if (!all.length) break;
      await all[all.length - 1].click({ force: true });   // last block = deepest path here
    }
  }
  await deepest();
  s = await probe(p);
  check("desktop: can descend to a transistor-level cell", s.crumbs >= 2 && !(await p.$(".view:not([hidden]) .symg.clickable")));
  const depth = s.crumbs;
  await p.keyboard.press("Escape");
  check("desktop: Esc goes up one level", (await probe(p)).crumbs === depth - 1);
  await p.keyboard.press("Backspace");
  check("desktop: Backspace goes up one level", (await probe(p)).crumbs === depth - 2 || depth - 2 < 1);
  await deepest();
  await p.locator("#crumbs a").first().click();
  s = await probe(p);
  check("desktop: breadcrumb root returns to top", s.cell === top && s.crumbs === 1);
  await p.click("#btn-up");
  check("desktop: 상위 at the top does nothing", (await probe(p)).cell === top);
  await p.mouse.wheel(0, -300); await p.keyboard.press("f");
  check("desktop: F fits", fitted(await probe(p)));
  // checkbox focus must not swallow Esc
  await deepest(); const d0 = (await probe(p)).crumbs;
  await p.click('[data-toggle="wl"]'); await p.click('[data-toggle="wl"]');
  await p.keyboard.press("Escape");
  check("desktop: Esc works after clicking a toggle", (await probe(p)).crumbs === d0 - 1);

  // cell selector
  const opts = await p.$$eval("#cell-jump option", (os) => os.map((o) => o.value));
  for (const o of opts) {
    await p.selectOption("#cell-jump", o);
    s = await probe(p);
    check(`desktop: selector opens ${o}`, s.cell === o && s.crumbs === 1 && s.vis > 0.9);
  }
  await p.selectOption("#cell-jump", top);

  // net highlight: click sticks, second click clears, side-panel hover highlights
  const wire = p.locator(".view:not([hidden]) line.wire").first();
  await wire.click({ force: true });
  check("desktop: clicking a net highlights it", (await probe(p)).hl > 0);
  await wire.click({ force: true });
  await p.mouse.move(c.x + 5, c.y + 5);
  check("desktop: clicking it again clears the highlight", (await probe(p)).hl === 0);
  const link = p.locator("#side .netlink").first();
  if (await link.count()) { await link.hover(); check("desktop: side-panel net hover highlights", (await probe(p)).hl > 0); }

  // PPT download button
  if (await p.$("#btn-ppt")) {
    const [dl] = await Promise.all([p.waitForEvent("download", { timeout: 5000 }), p.click("#btn-ppt")]);
    const fp = await dl.path();
    const buf = require("fs").readFileSync(fp);
    check("desktop: ⬇ PPT downloads a .pptx", dl.suggestedFilename().endsWith(".pptx") && buf.length > 10000 &&
          buf[0] === 0x50 && buf[1] === 0x4b, `${dl.suggestedFilename()} ${buf.length} bytes`);
    check("desktop: PPT button keeps the drawing in place", (await probe(p)).vis > 0.9);
  }
  // persistence + resize
  await p.click('[data-toggle="wl"]');
  await p.reload();
  check("desktop: toggle state survives reload", !(await p.isChecked('[data-toggle="wl"]')) && (await probe(p)).body.includes("hide-wl"));
  await p.click('[data-toggle="wl"]');
  await p.setViewportSize({ width: 700, height: 900 });
  check("desktop: drawing visible after resize", (await probe(p)).vis > 0.9);
  check("desktop: no JS errors", errs.length === 0, errs.join(" | "));
  await p.close();
}

async function mobile(b) {
  const ctx = await b.newContext({ ...pw.devices["Pixel 7"] });
  const p = await ctx.newPage();
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  await p.goto(html);
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload();
  await p.evaluate(() => { window.__cancel = 0; window.addEventListener("pointercancel", () => window.__cancel++, true); });
  const cdp = await ctx.newCDPSession(p);
  const touch = (type, pts) => cdp.send("Input.dispatchTouchEvent", { type, touchPoints: pts.map(([x, y], i) => ({ x, y, id: i })) });
  async function finger(x0, y0, x1, y1, steps = 10) {
    await touch("touchStart", [[x0, y0]]);
    for (let i = 1; i <= steps; i++) await touch("touchMove", [[x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps]]);
    await touch("touchEnd", []);
  }
  async function thumbTap(sel) {          // a real thumb tap wiggles a few px
    const bb = await p.locator(sel).first().boundingBox();
    const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2;
    await touch("touchStart", [[x, y]]); await touch("touchMove", [[x + 2, y + 3]]); await touch("touchMove", [[x + 3, y + 4]]);
    await touch("touchEnd", []);
    await p.waitForTimeout(30);
  }
  const c = await p.locator("#canvas").boundingBox();
  const cx = c.x + c.width / 2, cy = c.y + c.height / 2;
  let s = await probe(p);
  const top = s.cell;
  check("phone: opens fitted and visible", fitted(s) && s.vis > 0.9);
  await finger(cx - 40, cy - 30, cx + 40, cy + 20);
  let s2 = await probe(p);
  check("phone: one-finger pan is 1:1", near(s2.gx - s.gx, 80, 3) && near(s2.gy - s.gy, 50, 3), `moved (${(s2.gx - s.gx).toFixed(1)},${(s2.gy - s.gy).toFixed(1)}) expected (80,50)`);
  check("phone: the browser does not cancel the pan", (await p.evaluate(() => window.__cancel)) === 0);
  await toggleChecks(p, "phone after pan", thumbTap);
  // pinch
  s = await probe(p);
  await touch("touchStart", [[cx - 30, cy], [cx + 30, cy]]);
  for (let i = 1; i <= 8; i++) await touch("touchMove", [[cx - 30 - i * 12, cy], [cx + 30 + i * 12, cy]]);
  await touch("touchEnd", []);
  s2 = await probe(p);
  check("phone: pinch-out zooms in", s2.vb[2] < s.vb[2] * 0.6 && s2.vis > 0.05, `vb width ${s.vb[2]} -> ${s2.vb[2]}`);
  await touch("touchStart", [[cx - 120, cy], [cx + 120, cy]]);
  for (let i = 1; i <= 8; i++) await touch("touchMove", [[cx - 120 + i * 12, cy], [cx + 120 - i * 12, cy]]);
  await touch("touchEnd", []);
  check("phone: pinch-in zooms out again", (await probe(p)).vb[2] > s2.vb[2]);
  await toggleChecks(p, "phone after pinch", thumbTap);
  await thumbTap("#btn-fit");
  check("phone: 맞춤 restores the view", fitted(await probe(p)));
  // tap a block right after a pinch must still navigate
  await touch("touchStart", [[cx - 30, cy], [cx + 30, cy]]); await touch("touchMove", [[cx - 50, cy], [cx + 50, cy]]); await touch("touchEnd", []);
  await thumbTap("#btn-fit");
  const blk = await p.$eval(".view:not([hidden]) .symg.clickable", (e) => [e.dataset.inst, e.dataset.ref]);
  await p.locator(`.view:not([hidden]) .symg[data-inst="${blk[0]}"] .hit`).hover({ force: true });
  await thumbTap(`.view:not([hidden]) .symg[data-inst="${blk[0]}"] .hit`);
  s = await probe(p);
  check(`phone: tap ${blk[0]} opens ${blk[1]} with no tooltip left`, s.cell === blk[1] && !s.tip && s.vis > 0.9, JSON.stringify(s));
  await toggleChecks(p, "phone inside a block", thumbTap);
  // transistor-level view: tap a device -> tooltip, tap empty paper -> gone
  const devSel = ".view:not([hidden]) .symg.dev";
  if (await p.$(devSel)) {
    await thumbTap(devSel);
    check("phone: tapping a device shows its tooltip", (await probe(p)).tip);
    await thumbTap("#canvas .view:not([hidden]) svg");   // centre of the paper
    const c2 = await p.locator("#canvas").boundingBox();
    await touch("touchStart", [[c2.x + 6, c2.y + 6]]); await touch("touchEnd", []); await p.waitForTimeout(30);
    check("phone: tapping empty paper hides it", !(await probe(p)).tip);
  }
  await thumbTap("#btn-up");
  check("phone: 상위 returns", (await probe(p)).cell === top);
  // tap a block immediately after a pan (browser would normally swallow this click)
  await finger(cx - 30, cy, cx + 30, cy, 4);
  await thumbTap("#btn-fit");
  await finger(cx - 20, cy - 10, cx + 20, cy + 10, 4);
  const blk2 = await p.$eval(".view:not([hidden]) .symg.clickable", (e) => [e.dataset.inst, e.dataset.ref]);
  await thumbTap(`.view:not([hidden]) .symg[data-inst="${blk2[0]}"] .hit`);
  s = await probe(p);
  check("phone: tap on a block right after a pan still opens it", s.cell === blk2[1] && !s.tip, JSON.stringify(s));
  await thumbTap("#crumbs a");
  check("phone: breadcrumb tap returns to top", (await probe(p)).cell === top);
  await p.setViewportSize({ width: 915, height: 412 });
  check("phone: landscape keeps the drawing visible", (await probe(p)).vis > 0.9);
  check("phone: no JS errors", errs.length === 0, errs.join(" | "));
  await ctx.close();
}

(async () => {
  const b = await pw.chromium.launch();
  try { await desktop(b); await mobile(b); }
  catch (e) { fails++; console.log("FAIL  harness error: " + e.stack); }
  await b.close();
  console.log(`\n${passes} passed, ${fails} failed`);
  process.exit(fails ? 1 : 0);
})();
````

### FILE: hspice-schematic/assets/viewer.css
<!-- sha256=a30d1a2a0bf08a4f1a0706f11683ff4a62785d9ee44c22805d3c63e107a3e3fd newline=1 -->
````css
:root {
  --ink: #111;
  --paper: #fff;
  --ui-bg: #f6f6f4;
  --ui-fg: #222;
  --ui-mute: #6b6b6b;
  --ui-line: #d9d9d4;
  --accent: #d0451b;
  --wl: #1d5fa8;
  --val: #1d5fa8;
  --net: #6b4f9e;
  --blk-hover: #fff4e5;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; }
body {
  background: var(--ui-bg); color: var(--ui-fg);
  font: 13px/1.4 -apple-system, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", Roboto, sans-serif;
  display: flex; flex-direction: column;
}
.bar {
  display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between;
  padding: 8px 16px; border-bottom: 1px solid var(--ui-line); background: var(--ui-bg);
}
.crumbs { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; font-weight: 600; }
.crumbs a { color: var(--ui-fg); text-decoration: none; padding: 2px 6px; border-radius: 4px; cursor: pointer; }
.crumbs a:hover { background: #e9e9e4; }
.crumbs a.cur { color: var(--accent); cursor: default; }
.crumbs .sep { color: var(--ui-mute); }
.tools { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; }
.tools label { display: inline-flex; gap: 4px; align-items: center; cursor: pointer; user-select: none; }
.bar, .side { touch-action: manipulation; }   /* no double-tap zoom eating quick taps */
.tools button, .tools select {
  font: inherit; padding: 3px 9px; border: 1px solid var(--ui-line); border-radius: 5px;
  background: #fff; color: var(--ui-fg); cursor: pointer;
}
.tools button:hover { border-color: #aaa; }
main { flex: 1; display: flex; min-height: 0; }
.canvas { flex: 1; position: relative; background: var(--paper); overflow: hidden; min-width: 0;
  touch-action: none; overscroll-behavior: contain; }
.view { position: absolute; inset: 0; }
.view[hidden] { display: none; }
svg.sch { width: 100%; height: 100%; display: block; cursor: grab; user-select: none; }
svg.sch.dragging { cursor: grabbing; }
.side {
  width: 300px; max-width: 40vw; overflow: auto; padding: 12px 14px;
  border-left: 1px solid var(--ui-line); background: var(--ui-bg);
}
.side h2 { font-size: 15px; margin: 0 0 4px; }
.side h3 { font-size: 12px; margin: 14px 0 4px; color: var(--ui-mute); text-transform: uppercase; letter-spacing: .04em; }
.side .why { color: var(--ui-mute); font-size: 12px; }
.side table { border-collapse: collapse; width: 100%; font-size: 12px; }
.side td { padding: 2px 4px; border-bottom: 1px solid #ebebe6; vertical-align: top; }
.side td:first-child { color: var(--ui-mute); white-space: nowrap; }
.side .netlink { cursor: pointer; color: var(--net); }
.side .netlink:hover { text-decoration: underline; }
.side .warn { color: #a04000; font-size: 12px; }
.tip {
  position: absolute; pointer-events: none; background: rgba(20, 20, 20, .92); color: #fff;
  padding: 6px 8px; border-radius: 5px; font-size: 12px; max-width: 280px; z-index: 5; white-space: pre-line;
}
@media (max-width: 760px) {
  main { flex-direction: column; }
  .side { width: auto; max-width: none; max-height: 34vh; border-left: 0; border-top: 1px solid var(--ui-line); }
}

/* ---------- schematic ink (paper stays white, like a textbook) ---------- */
svg.sch text { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; fill: var(--ink); }
.sym, .blk { stroke: var(--ink); stroke-width: 1.6; fill: none; stroke-linecap: square; stroke-linejoin: miter; }
.sym.chan { stroke-width: 3.4; stroke-linecap: butt; }
.sym.gate { stroke-width: 2; stroke-linecap: butt; }
.sym.plate { stroke-width: 2.2; stroke-linecap: butt; }
.sym.arrow { fill: var(--ink); stroke-width: 0.8; }
.blk { stroke-width: 1.6; fill: none; }
polyline.blk, circle.blk { fill: #fff; }
.blk-t { font-size: 13px; font-weight: 700; }
.sum-t { font-size: 22px; }
.pol-t { font-size: 12px; font-weight: 700; }
.pin-t { font-size: 9px; fill: #333 !important; }
.sym-t { font-size: 10px; }
.rail-t { font-size: 10px; font-weight: 600; }
.wire { stroke: var(--ink); stroke-width: 1.6; stroke-linecap: square; }
.wire.diag { stroke-linecap: round; }
.arrowhead { fill: var(--ink); stroke: none; }
.dot { fill: var(--ink); }
.hl.arrowhead { fill: var(--accent); }
.pin { fill: transparent; stroke: none; }
.devlbl { font-size: 9px; }
.lbl-name { fill: #333; font-style: italic; }
.lbl-wl, .lbl-val { fill: var(--wl); }
.lbl-cell { fill: #777; }
.netlabel { font-size: 10px; }
.lbl-port { font-weight: 700; }
.lbl-rail { font-weight: 700; }
.lbl-net { fill: var(--net); font-style: italic; }
.term-t { font-size: 10px; font-weight: 600; }
.term.bylabel .term-t { fill: var(--net); font-style: italic; }
.termc { fill: #fff; stroke: var(--ink); stroke-width: 1.2; }
/* Virtuoso schematic pins: red pentagon (in / out) or hexagon (inout) */
.vpin { fill: #e8261c; stroke: #8c0d07; stroke-width: 0.9; stroke-linejoin: miter; }
.hl .vpin { fill: var(--accent); }
.hit { fill: transparent; stroke: none; }
.symg.clickable { cursor: pointer; }
.symg.clickable:hover .hit { fill: var(--blk-hover); }
.symg.clickable:hover .blk { stroke: var(--accent); }

/* toggles */
body.hide-wl .lbl-wl { display: none; }
body.hide-val .lbl-val { display: none; }
body.hide-name .lbl-name { display: none; }
body:not(.show-net) .lbl-net { display: none; }

/* net highlight */
.hl.wire { stroke: var(--accent); stroke-width: 2.4; }
.hl.dot { fill: var(--accent); }
.hl.netlabel, .hl .term-t { fill: var(--accent) !important; }
.hl .termc { stroke: var(--accent); }
.pin.hl { fill: var(--accent); }
.symg.dev:hover .sym { stroke: var(--accent); }
.symg.dev:hover .sym.arrow { fill: var(--accent); }
````

### FILE: hspice-schematic/assets/viewer.js
<!-- sha256=a20f871f9ecd23917d8c703ff77c9379115f28f490d02fe7ebd10b169c955a06 newline=1 -->
````javascript
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("hsch-data").textContent);
  var canvas = document.getElementById("canvas");
  var side = document.getElementById("side");
  var tip = document.getElementById("tip");
  var crumbs = document.getElementById("crumbs");
  var stack = [];            // [{cell, inst}]
  var views = {};
  var viewBoxes = {};
  var sticky = null;

  Array.prototype.forEach.call(document.querySelectorAll(".view"), function (v) {
    views[v.getAttribute("data-cell")] = v;
  });

  function store(k, v) { try { localStorage.setItem("hsch:" + k, v); } catch (e) {} }
  function load(k) { try { return localStorage.getItem("hsch:" + k); } catch (e) { return null; } }

  // ---------------------------------------------------------------- reliable taps
  // Touch browsers drop the click of a tap that follows a pan/fling within ~300 ms and
  // delay clicks in general. On touch we act on the finger-up of a short tap and swallow
  // the click that may follow; mouse and keyboard keep using the normal click.
  var lastTouch = 0;
  var TAP_SLOP = 12;
  function onTap(el, fn) {
    var down = null, fired = 0;
    el.addEventListener("pointerdown", function (ev) {
      if (ev.pointerType !== "mouse") { lastTouch = Date.now(); down = { id: ev.pointerId, x: ev.clientX, y: ev.clientY }; }
    });
    el.addEventListener("pointerup", function (ev) {
      if (!down || ev.pointerId !== down.id) return;
      var d = Math.abs(ev.clientX - down.x) + Math.abs(ev.clientY - down.y);
      down = null;
      lastTouch = Date.now();
      if (d > TAP_SLOP) return;
      fired = Date.now();
      fn(ev, false);
    });
    el.addEventListener("pointercancel", function () { down = null; });
    el.addEventListener("click", function (ev) {
      if (Date.now() - fired < 800) { ev.preventDefault(); ev.stopPropagation(); return; }
      fn(ev, true);
    }, true);
  }

  // ---------------------------------------------------------------- toggles
  var TOGGLES = { wl: "hide-wl", val: "hide-val", name: "hide-name", net: "show-net" };
  Array.prototype.forEach.call(document.querySelectorAll("[data-toggle]"), function (cb) {
    var key = cb.getAttribute("data-toggle");
    var saved = load("t-" + key);
    if (saved !== null) cb.checked = saved === "1";
    function apply() {
      var cls = TOGGLES[key];
      var on = cb.checked;
      if (cls.indexOf("hide-") === 0) document.body.classList.toggle(cls, !on);
      else document.body.classList.toggle(cls, on);
      store("t-" + key, on ? "1" : "0");
    }
    cb.addEventListener("change", apply);         // mouse / keyboard (native toggle)
    onTap(cb.closest("label") || cb, function (ev, fromClick) {
      if (fromClick) return;                      // native click toggles, change -> apply
      cb.checked = !cb.checked;                   // touch: toggle on finger-up
      apply();
    });
    apply();
  });

  // ---------------------------------------------------------------- navigation
  function cellInfo(c) { return DATA.cells[c] || {}; }

  function show(cell, push) {
    if (!views[cell]) return;
    Object.keys(views).forEach(function (k) { views[k].hidden = k !== cell; });
    if (push === undefined) stack = [{ cell: cell, inst: null }];
    sticky = null;
    clearHL();
    hideTip();   // a tooltip must never survive a change of view
    resetGesture();
    if (!viewBoxes[cell]) fit(cell);
    renderCrumbs();
    renderSide();
    var sel = document.getElementById("cell-jump");
    sel.value = cell;
  }

  function current() { return stack[stack.length - 1].cell; }

  function descend(inst, ref) {
    if (!views[ref]) return;
    stack.push({ cell: ref, inst: inst });
    show(ref, true);
  }

  function up() {
    if (stack.length > 1) { stack.pop(); show(current(), true); }
  }

  function renderCrumbs() {
    crumbs.innerHTML = "";
    stack.forEach(function (s, i) {
      if (i) { var sp = document.createElement("span"); sp.className = "sep"; sp.textContent = "›"; crumbs.appendChild(sp); }
      var a = document.createElement("a");
      var info = cellInfo(s.cell);
      a.textContent = (s.inst ? s.inst + " : " : "") + (info.display || s.cell);
      if (i === stack.length - 1) a.className = "cur";
      else onTap(a, function () { stack = stack.slice(0, i + 1); show(s.cell, true); });
      crumbs.appendChild(a);
    });
  }

  // ---------------------------------------------------------------- side panel
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function renderSide() {
    var c = current();
    var info = cellInfo(c);
    var h = "<h2>" + esc(info.display || c) + "</h2>";
    h += '<div class="why">' + esc(info.label || "") + (info.auto ? " · 자동 생성 블록" : "") + "</div>";
    if (info.reason) h += '<div class="why">인식 근거: ' + esc(info.reason) + "</div>";
    // port mapping from parent
    if (stack.length > 1) {
      var parent = stack[stack.length - 2].cell;
      var inst = stack[stack.length - 1].inst;
      var pi = (cellInfo(parent).insts || {})[inst];
      if (pi) {
        h += "<h3>포트 연결 (" + esc(inst) + " @ " + esc(parent) + ")</h3><table>";
        Object.keys(pi.pins).forEach(function (p) {
          h += "<tr><td>" + esc(p) + '</td><td><span class="netlink" data-net="' + esc(p) + '">' + esc(pi.pins[p]) + "</span></td></tr>";
        });
        h += "</table>";
      }
    }
    if (info.ports && info.ports.length) {
      h += "<h3>포트</h3><table>";
      info.ports.forEach(function (p) {
        h += '<tr><td>' + esc((info.roles || {})[p] || "") + '</td><td><span class="netlink" data-net="' + esc(p) + '">' + esc(p) + "</span></td></tr>";
      });
      h += "</table>";
    }
    var v = info.verify;
    if (v) {
      h += "<h3>검증</h3>";
      h += "<div>" + (v.ok ? "✅ 연결 일치 (원본 netlist와 동일)" : "❌ 연결 불일치") + "</div>";
      (v.errors || []).forEach(function (e) { h += '<div class="warn">' + esc(e) + "</div>"; });
      if (v.lint) {
        h += '<div class="why">교차 ' + v.lint.crossings + " · 경고 " + (v.lint.warnings || []).length + "</div>";
        (v.lint.warnings || []).slice(0, 8).forEach(function (w) { h += '<div class="warn">' + esc(w) + "</div>"; });
      }
    }
    (info.warnings || []).forEach(function (w) { h += '<div class="warn">' + esc(w) + "</div>"; });
    h += '<h3>사용법</h3><div class="why">블록 클릭/탭 → 내부 보기 · Esc → 상위 · 휠 또는 두 손가락 → 확대/축소 · 드래그 → 이동 · 넷 클릭 → 강조 고정 · 소자 탭 → 정보 · F/더블클릭 → 화면 맞춤</div>';
    side.innerHTML = h;
    Array.prototype.forEach.call(side.querySelectorAll(".netlink"), function (el) {
      el.addEventListener("mouseenter", function () { hl(el.getAttribute("data-net")); });
      el.addEventListener("mouseleave", function () { if (!sticky) clearHL(); else hl(sticky); });
    });
  }

  // ---------------------------------------------------------------- highlight
  function svgOf(cell) { return views[cell].querySelector("svg"); }
  function clearHL() {
    Array.prototype.forEach.call(document.querySelectorAll(".hl"), function (e) { e.classList.remove("hl"); });
  }
  function hl(net) {
    clearHL();
    if (!net) return;
    var s = svgOf(current());
    Array.prototype.forEach.call(s.querySelectorAll('[data-net="' + (window.CSS && CSS.escape ? CSS.escape(net) : net) + '"]'), function (e) {
      e.classList.add("hl");
    });
  }

  // ---------------------------------------------------------------- tooltip
  function devTip(cell, inst) {
    var info = (cellInfo(cell).insts || {})[inst];
    if (!info) return inst;
    var t = inst + "  (" + info.type + ")";
    var p = info.params || {};
    var keys = ["w", "l", "m", "r", "c", "l"];
    var shown = {};
    keys.forEach(function (k) { if (p[k] !== undefined && !shown[k]) { t += "\n" + k.toUpperCase() + " = " + p[k]; shown[k] = 1; } });
    if (info.ref) t += "\n→ " + (cellInfo(info.ref).display || info.ref) + "  (클릭해서 열기)";
    Object.keys(info.pins).forEach(function (pn) { t += "\n" + pn + " : " + info.pins[pn]; });
    return t;
  }

  function showTipFor(target, cx, cy) {
    var g = target.closest ? target.closest(".symg") : null;
    var netEl = target.closest ? target.closest("[data-net]") : null;
    var r = canvas.getBoundingClientRect();
    var text = null;
    if (g && !netEl) text = devTip(current(), g.getAttribute("data-inst"));
    else if (netEl) text = "net: " + netEl.getAttribute("data-net");
    if (!text) { hideTip(); return null; }
    tip.textContent = text;
    tip.hidden = false;
    tip.style.left = Math.max(4, Math.min(cx - r.left + 14, r.width - 290)) + "px";
    tip.style.top = Math.max(4, Math.min(cy - r.top + 14, r.height - 60)) + "px";
    return netEl;
  }
  canvas.addEventListener("mousemove", function (ev) {
    // touch screens emit compatibility mouse events after a tap: ignore them, or a
    // tooltip pops up on whatever is under the finger in the view we just opened
    if (Date.now() - lastTouch < 800) return;
    var netEl = showTipFor(ev.target, ev.clientX, ev.clientY);
    if (netEl) { if (!sticky) hl(netEl.getAttribute("data-net")); }
    else if (!sticky) clearHL();
  });
  function hideTip() { tip.hidden = true; tip.textContent = ""; }
  canvas.addEventListener("mouseleave", function () { hideTip(); if (!sticky) clearHL(); });

  // ---------------------------------------------------------------- pan / zoom
  function getVB(cell) { return viewBoxes[cell]; }
  function setVB(cell, vb) {
    viewBoxes[cell] = vb;
    svgOf(cell).setAttribute("viewBox", vb.join(" "));
  }
  function fit(cell) {
    var b = svgOf(cell).getAttribute("data-bounds").split(",").map(Number);
    setVB(cell, [b[0], b[1], b[2] - b[0], b[3] - b[1]]);
  }

  // ---------------------------------------------------------------- pointer gestures
  // One finger / mouse drag = pan, two fingers = pinch zoom, wheel = zoom.
  // Every pointer is tracked by id and captured by the canvas, and pointercancel /
  // lostpointercapture end the gesture, so a cancelled touch can never leave a stale
  // drag behind (that stale drag is what threw the drawing off-screen on the next tap).
  var pointers = {};
  var gesture = null;
  var moved = false;
  var multi = false;

  function geom(s, vb) {
    var r = s.getBoundingClientRect();
    var sc = Math.min(r.width / vb[2], r.height / vb[3]) || 1;
    return { r: r, sc: sc, ox: (r.width - vb[2] * sc) / 2, oy: (r.height - vb[3] * sc) / 2 };
  }
  function toUser(s, vb, cx, cy) {
    var g = geom(s, vb);
    return { x: vb[0] + (cx - g.r.left - g.ox) / g.sc, y: vb[1] + (cy - g.r.top - g.oy) / g.sc };
  }
  function clampK(cell, vb, k) {
    var b = svgOf(cell).getAttribute("data-bounds").split(",").map(Number);
    var w0 = b[2] - b[0];
    var w = vb[2] * k;
    if (w < w0 * 0.05) k = (w0 * 0.05) / vb[2];
    if (w > w0 * 20) k = (w0 * 20) / vb[2];
    return k;
  }
  function zoomAt(vb, mx, my, k) {
    return [mx - (mx - vb[0]) * k, my - (my - vb[1]) * k, vb[2] * k, vb[3] * k];
  }
  function resetGesture() { pointers = {}; gesture = null; }
  function startGesture() {
    var ids = Object.keys(pointers);
    if (!ids.length) { gesture = null; return; }
    var vb = getVB(current()).slice();
    if (ids.length === 1) {
      var p = pointers[ids[0]];
      gesture = { vb: vb, x: p.x, y: p.y };
    } else {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      gesture = { vb: vb, x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, dist: Math.hypot(a.x - b.x, a.y - b.y) || 1 };
    }
  }
  function endPointer(ev) {
    // lostpointercapture bubbles up from the element that held the implicit touch capture
    // when the canvas takes over; only the canvas losing capture ends the gesture
    if (ev.type === "lostpointercapture" && ev.target !== canvas) return;
    if (!(ev.pointerId in pointers)) return;
    delete pointers[ev.pointerId];
    svgOf(current()).classList.remove("dragging");
    startGesture();            // pinch -> pan hand-over without a jump
  }

  canvas.addEventListener("wheel", function (ev) {
    var s = svgOf(current());
    if (!s.contains(ev.target) && ev.target !== s) return;
    ev.preventDefault();
    hideTip();
    var vb = getVB(current()).slice();
    var m = toUser(s, vb, ev.clientX, ev.clientY);
    var k = clampK(current(), vb, Math.exp(ev.deltaY * 0.0015));
    setVB(current(), zoomAt(vb, m.x, m.y, k));
  }, { passive: false });

  canvas.addEventListener("pointerdown", function (ev) {
    var s = svgOf(current());
    if (!s.contains(ev.target) && ev.target !== s) return;
    if (ev.pointerType === "mouse" && ev.button !== 0) return;
    if (ev.pointerType !== "mouse") { hideTip(); lastTouch = Date.now(); }
    if (!Object.keys(pointers).length) { moved = false; multi = false; }
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    if (Object.keys(pointers).length > 1) multi = true;
    // capture only once a real drag/pinch starts: capturing on pointerdown would retarget
    // the following click to the canvas and break clicking blocks / nets
    if (Object.keys(pointers).length > 1) capture(ev.pointerId);
    startGesture();
  });
  function capture(id) {
    try { if (!canvas.hasPointerCapture(id)) canvas.setPointerCapture(id); } catch (e) {}
  }
  canvas.addEventListener("pointermove", function (ev) {
    if (!(ev.pointerId in pointers) || !gesture) return;
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    var s = svgOf(current());
    var ids = Object.keys(pointers);
    var vb = gesture.vb;
    if (ids.length === 1) {
      var dx = ev.clientX - gesture.x, dy = ev.clientY - gesture.y;
      var slop = ev.pointerType === "mouse" ? 4 : 12;               // a thumb tap wobbles
      if (!moved && Math.abs(dx) + Math.abs(dy) <= slop) return;   // still a tap
      moved = true;
      capture(ev.pointerId);
      s.classList.add("dragging");
      hideTip();
      var sc = geom(s, vb).sc;
      setVB(current(), [vb[0] - dx / sc, vb[1] - dy / sc, vb[2], vb[3]]);
    } else {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      var dist = Math.hypot(a.x - b.x, a.y - b.y) || 1;
      moved = true;
      hideTip();
      var anchor = toUser(s, vb, gesture.x, gesture.y);
      var k = clampK(current(), vb, gesture.dist / dist);
      var nvb = zoomAt(vb, anchor.x, anchor.y, k);
      var sc2 = geom(s, nvb).sc;
      nvb[0] -= (mx - gesture.x) / sc2;
      nvb[1] -= (my - gesture.y) / sc2;
      setVB(current(), nvb);
    }
  });
  ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (t) {
    canvas.addEventListener(t, endPointer);
  });

  // what a click (mouse) or a tap (touch) on the drawing does
  function canvasAction(target, cx, cy, isTouch) {
    var g = target.closest ? target.closest(".symg.clickable") : null;
    var netEl = target.closest ? target.closest("[data-net]") : null;
    if (netEl && !g) {
      var n = netEl.getAttribute("data-net");
      sticky = sticky === n ? null : n;
      if (sticky) hl(sticky); else clearHL();
      if (isTouch) { if (sticky) showTipFor(target, cx, cy); else hideTip(); }
      return;
    }
    if (g) { hideTip(); descend(g.getAttribute("data-inst"), g.getAttribute("data-ref")); return; }
    sticky = null; clearHL();
    if (isTouch) showTipFor(target, cx, cy);   // tap a transistor -> its W/L and nets
    else hideTip();
  }
  var canvasTapAt = 0;
  canvas.addEventListener("pointerup", function (ev) {
    if (ev.pointerType === "mouse" || moved || multi) return;
    if (Object.keys(pointers).length) return;            // other fingers still down
    lastTouch = Date.now();
    canvasTapAt = Date.now();
    canvasAction(ev.target, ev.clientX, ev.clientY, true);
  });
  canvas.addEventListener("click", function (ev) {
    if (Date.now() - canvasTapAt < 800) return;          // already handled as a tap
    if (moved) { moved = false; return; }
    canvasAction(ev.target, ev.clientX, ev.clientY, false);
  });
  canvas.addEventListener("dblclick", function () { fit(current()); });

  onTap(document.getElementById("btn-up"), function () { up(); });
  var pptBtn = document.getElementById("btn-ppt");
  if (pptBtn) onTap(pptBtn, function () {
    var el = document.getElementById("hsch-pptx");
    var bin = atob(el.textContent.trim());
    var arr = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    var blob = new Blob([arr], { type: "application/vnd.openxmlformats-officedocument.presentationml.presentation" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = el.getAttribute("data-name") || "schematic.pptx";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
  });
  onTap(document.getElementById("btn-fit"), function () { fit(current()); });
  document.addEventListener("keydown", function (ev) {
    var tg = ev.target || {};
    if ((tg.tagName === "INPUT" && tg.type !== "checkbox") || /select|textarea/i.test(tg.tagName || "")) return;
    if (ev.key === "Escape" || ev.key === "Backspace") { up(); ev.preventDefault(); }
    if (ev.key === "f" || ev.key === "F") fit(current());
  });

  var sel = document.getElementById("cell-jump");
  Object.keys(views).forEach(function (c) {
    var o = document.createElement("option");
    o.value = c; o.textContent = cellInfo(c).display || c;
    sel.appendChild(o);
  });
  sel.addEventListener("change", function () { show(sel.value); });

  // public hook for scripted screenshots / tests
  window.HSCH = {
    show: function (cell) { show(cell); },
    path: function (insts) {           // e.g. ["X_DFE","X_DFF","X_MASTER"]
      show(DATA.top);
      insts.forEach(function (i) {
        var info = (cellInfo(current()).insts || {})[i];
        if (info && info.ref) descend(i, info.ref);
      });
    },
    cells: function () { return Object.keys(views); }
  };
  show(DATA.top);
})();
````

### FILE: tests/test_hsch.py
<!-- sha256=7b4f0edaff505b383268f5d59227bf798be5210eed512160a9b05b96c1457e5a newline=1 -->
````python
"""Regression tests:  python3 -m unittest discover -s tests -v"""
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hspice-schematic", "scripts"))

from build import build  # noqa: E402
from hsch.analyze import classify_all, extract_auto_blocks, flatten, port_roles  # noqa: E402
from hsch.parser import parse_file, parse_text, parse_value  # noqa: E402
from hsch.verify import check_view, parse_html, text_box  # noqa: E402

NET = os.path.join(ROOT, "tests", "netlists")
IBS = os.path.join(NET, "input_buffer_system.sp")
VIRT = os.path.join(NET, "virtuoso_style.sp")


class TestParser(unittest.TestCase):
    def test_values(self):
        self.assertAlmostEqual(parse_value("16u"), 16e-6)
        self.assertAlmostEqual(parse_value("45n"), 45e-9)
        self.assertAlmostEqual(parse_value("150f"), 150e-15)
        self.assertAlmostEqual(parse_value("1k"), 1e3)
        self.assertAlmostEqual(parse_value("2meg"), 2e6)
        self.assertAlmostEqual(parse_value("1.6e-05"), 1.6e-5)
        self.assertAlmostEqual(parse_value("10fF"), 10e-15)
        self.assertIsNone(parse_value("'w1*2'"))

    def test_continuation_comments_case(self):
        ir = parse_text("""
* comment
.SUBCKT a in out vdd vss
mm1 out in vss vss nch w=1u $ inline comment
+ l = 45n
.ends
.subckt TOP x y vdd vss
xi0 x y vdd vss A
.ends
""")
        d = ir["cells"]["a"]["devices"][0]
        self.assertEqual(d["params"]["l"], "45n")
        self.assertEqual(d["type"], "nmos")
        self.assertEqual(ir["top"], "TOP")
        x = ir["cells"]["TOP"]["devices"][0]
        self.assertEqual(x["ref"], "a")             # case-insensitive subckt lookup
        self.assertEqual(dict(x["pins"])["in"], "x")

    def test_mos_type_from_model(self):
        ir = parse_file(VIRT)
        types = {d["name"]: d["type"] for d in ir["cells"]["ota5t"]["devices"]}
        self.assertEqual(types["mm3"], "pmos")
        self.assertEqual(types["mm1"], "nmos")
        mm5 = [d for d in ir["cells"]["ota5t"]["devices"] if d["name"] == "mm5"][0]
        self.assertEqual(mm5["params"]["l"], "200e-9")  # '+' continuation


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.ir0 = parse_file(IBS)
        self.ir = extract_auto_blocks(self.ir0)

    def test_auto_block(self):
        dfe = self.ir["cells"]["DFE_1TAP"]
        kinds = sorted(d["kind"] for d in dfe["devices"])
        self.assertEqual(kinds, ["X", "X"])
        auto = self.ir["cells"]["DFE_1TAP__AUTO0"]
        self.assertEqual(len(auto["devices"]), 8)
        for p in ("INP", "INN", "OUTP", "OUTN", "SUMP", "SUMN", "VBIAS_MAIN", "VBIAS_TAP"):
            self.assertIn(p, auto["ports"])
        self.assertNotIn("TAIL_M", auto["ports"])

    def test_flatten_unchanged(self):
        self.assertEqual(flatten(self.ir0, self.ir0["top"]), flatten(self.ir, self.ir["top"]))

    def test_roles(self):
        r = port_roles(self.ir)
        self.assertEqual(r["CML_LATCH"]["QP"], "out")
        self.assertEqual(r["CML_LATCH"]["CLK"], "clk")
        self.assertEqual(r["CTLE"]["VBIAS"], "bias")
        self.assertEqual(r["DFE_1TAP"]["OUTP"], "out")
        self.assertEqual(r["DFE_1TAP__AUTO0"]["OUTP"], "in")   # tap input inside the summer

    def test_classes(self):
        c = classify_all(self.ir)
        self.assertEqual(c["CTLE"]["class"], "ctle")
        self.assertEqual(c["CML_LATCH"]["class"], "latch")
        self.assertEqual(c["CML_DFF"]["class"], "dff")
        self.assertEqual(c["DFE_1TAP__AUTO0"]["class"], "summer")
        ir2 = extract_auto_blocks(parse_file(VIRT))
        c2 = classify_all(ir2)
        self.assertEqual(c2["nand2"]["class"], "nand")
        self.assertEqual(c2["inv"]["class"], "inverter")


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.out = {}
        for name, path in (("ibs", IBS), ("virt", VIRT)):
            html = os.path.join(cls.tmp, name + ".html")
            ok, report, scenes = build(path, html, quiet=True)
            cls.out[name] = (ok, report, scenes, html)

    def test_connectivity_and_lint_clean(self):
        for name, (ok, report, _, _) in self.out.items():
            self.assertTrue(ok, f"{name}: connectivity mismatch {report}")
            for cell, r in report.items():
                self.assertEqual(r["lint"]["warnings"], [], f"{name}/{cell}")

    def test_global_mirror_symmetry(self):
        _, _, scenes, _ = self.out["ibs"]
        pairs = {"CTLE": [("M1", "M2"), ("RLP", "RLN"), ("MBP", "MBN")],
                 "CML_LATCH": [("M1", "M2"), ("M3", "M4"), ("RLP", "RLN"), ("M5", "M6")]}
        for cell, plist in pairs.items():
            pins = {}
            for p in scenes[cell]["pins"]:
                pins.setdefault(p["inst"], []).append((p["x"], p["y"]))
            axes = set()
            for a, b in plist:
                xa = sorted(x for x, _ in pins[a])
                xb = sorted(x for x, _ in pins[b])
                axes.add((xa[0] + xb[-1]) / 2.0)
                self.assertEqual(sorted(y for _, y in pins[a]), sorted(y for _, y in pins[b]))
            self.assertEqual(len(axes), 1, f"{cell}: pairs mirrored about different axes {axes}")
        # tail device of the latch sits on the axis
        mb = [p["x"] for p in scenes["CML_LATCH"]["pins"] if p["inst"] == "MB" and p["pin"] == "d"][0]
        self.assertEqual(mb, axes.pop())

    def test_pptx_editable_and_navigable(self):
        from pptx import Presentation
        from pptx.shapes.group import GroupShape
        from pptx.util import Inches
        _, _, scenes, html = self.out["ibs"]
        prs = Presentation(os.path.splitext(html)[0] + ".pptx")
        slides = list(prs.slides)
        self.assertEqual(len(slides), len(scenes))

        def walk(shapes):
            for sh in shapes:
                yield sh
                if isinstance(sh, GroupShape):
                    yield from walk(sh.shapes)

        title_of = {sl.slide_id: cell for sl, cell in zip(slides, scenes)}   # slide order == view order
        for sl, cell in zip(slides, scenes):
            sc = scenes[cell]
            shapes = list(walk(sl.shapes))
            texts = {sh.text_frame.text for sh in shapes if sh.has_text_frame}
            for p in sc["ports"]:
                self.assertIn(p, texts, f"{cell}: port {p} missing as editable text")
            nets = [sh for sh in sl.shapes if isinstance(sh, GroupShape) and sh.name.startswith("net ")]
            n_lines = sum(1 for g in nets for sh in g.shapes if sh.shape_type == 9 or "Connector" in sh.name)
            self.assertEqual(n_lines, len(sc["wires"]), f"{cell}: wire count")
            for sh in shapes:
                if sh.name.startswith("open "):
                    ref = sh.name[5:]
                    tgt = sh.click_action.target_slide
                    self.assertIsNotNone(tgt, f"{cell}: {sh.name} has no jump")
                    self.assertEqual(title_of[tgt.slide_id], ref)
            for sh in sl.shapes:
                self.assertGreaterEqual(sh.left, 0)
                self.assertGreaterEqual(sh.top, 0)
                self.assertLessEqual(sh.left + sh.width, prs.slide_width + Inches(0.05), f"{cell}: {sh.name} off slide")
                self.assertLessEqual(sh.top + sh.height, prs.slide_height + Inches(0.05), f"{cell}: {sh.name} off slide")

    def test_every_port_has_a_virtuoso_pin(self):
        for name in ("ibs", "virt"):
            _, _, scenes, _ = self.out[name]
            for cell, sc in scenes.items():
                pins = {t["net"] for t in sc["terminals"] if t.get("vpin")}
                for p in sc["ports"]:
                    self.assertIn(p, pins, f"{name}/{cell}: port {p} has no pin glyph")

    def test_toggles_and_offline(self):
        with open(self.out["ibs"][3], encoding="utf-8") as f:
            html = f.read()
        for t in ("wl", "val", "name", "net"):
            self.assertIn(f'data-toggle="{t}"', html)
        self.assertIsNone(re.search(r'<script[^>]+src=', html), "viewer must not load external scripts")

    def _view(self, cell):
        html = self.out["ibs"][3]
        return parse_html(html)[cell]

    def test_verifier_detects_open(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("CTLE")
        v["wires"] = v["wires"][1:]   # delete a wire
        r = check_view(v, ir["cells"]["CTLE"], {})
        self.assertFalse(r["ok"])
        self.assertTrue(any("OPEN" in e or "touches nothing" in e for e in r["errors"]), r["errors"])

    def test_verifier_detects_short(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("CTLE")
        # draw an extra wire from the INP gate pin to the INN gate pin
        P = {(i, p): (x, y) for i, p, x, y in v["pins"]}
        (x1, y1), (x2, y2) = P[("M1", "g")], P[("M2", "g")]
        v["wires"].append((x1, y1, x1, y1 - 200))
        v["wires"].append((x1, y1 - 200, x2, y1 - 200))
        v["wires"].append((x2, y1 - 200, x2, y2))
        r = check_view(v, ir["cells"]["CTLE"], {})
        self.assertTrue(any("SHORT" in e for e in r["errors"]), r["errors"])

    def test_verifier_detects_text_overlap(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("INPUT_BUFFER_SYSTEM")
        w = v["wires"][0]
        v["texts"].append({"txt": "X", "box": text_box("XXXX", (w[0] + w[2]) / 2, w[1] + 3, "middle", 10),
                           "kind": "netlabel", "sym": None})
        r = check_view(v, ir["cells"]["INPUT_BUFFER_SYSTEM"], {})
        self.assertTrue(any("overlaps a wire" in x for x in r["lint"]["warnings"]))


if __name__ == "__main__":
    unittest.main()
````

### FILE: tests/netlists/input_buffer_system.sp
<!-- sha256=6ca8df952e6f24f1db04ea594579790d38ae55f3f8a7af9a78229a98ff031411 newline=1 -->
````spice
.SUBCKT CTLE INP INN OUTP OUTN VBIAS VDD VSS
RLP VDD OUTP 600
RLN VDD OUTN 600
M1 OUTP INP SP VSS NCH W=16u L=45n
M2 OUTN INN SN VSS NCH W=16u L=45n
RS SP SN 1000
CS SP SN 150f
MBP SP VBIAS VSS VSS NCH W=32u L=90n
MBN SN VBIAS VSS VSS NCH W=32u L=90n
.ENDS CTLE

.SUBCKT CML_LATCH DP DN CLK CLKB QP QN VBIAS VDD VSS
RLP VDD QP 500
RLN VDD QN 500
M1 QP DP TAIL_T VSS NCH W=12u L=45n
M2 QN DN TAIL_T VSS NCH W=12u L=45n
M3 QP QN TAIL_H VSS NCH W=12u L=45n
M4 QN QP TAIL_H VSS NCH W=12u L=45n
M5 TAIL_T CLK TAIL VSS NCH W=16u L=45n
M6 TAIL_H CLKB TAIL VSS NCH W=16u L=45n
MB TAIL VBIAS VSS VSS NCH W=32u L=90n
.ENDS CML_LATCH

.SUBCKT CML_DFF DP DN CLK CLKB QP QN VBIAS VDD VSS
X_MASTER DP DN CLKB CLK MP MN VBIAS VDD VSS CML_LATCH
X_SLAVE MP MN CLK CLKB QP QN VBIAS VDD VSS CML_LATCH
.ENDS CML_DFF

.SUBCKT DFE_1TAP INP INN CLK CLKB OUTP OUTN VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS
RLP VDD SUMP 500
RLN VDD SUMN 500
M1 SUMP INP TAIL_M VSS NCH W=20u L=45n
M2 SUMN INN TAIL_M VSS NCH W=20u L=45n
MB_M TAIL_M VBIAS_MAIN VSS VSS NCH W=40u L=90n
M3 SUMP OUTP TAIL_T1 VSS NCH W=8u L=45n
M4 SUMN OUTN TAIL_T1 VSS NCH W=8u L=45n
MB_T1 TAIL_T1 VBIAS_TAP VSS VSS NCH W=16u L=90n
X_DFF SUMP SUMN CLK CLKB OUTP OUTN VBIAS_DFF VDD VSS CML_DFF
.ENDS DFE_1TAP

.SUBCKT INPUT_BUFFER_SYSTEM RX_INP RX_INN CLK CLKB DOUTP DOUTN VBIAS_CTLE VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS
X_CTLE RX_INP RX_INN CTLE_OUTP CTLE_OUTN VBIAS_CTLE VDD VSS CTLE
X_DFE CTLE_OUTP CTLE_OUTN CLK CLKB DOUTP DOUTN VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS DFE_1TAP
.ENDS INPUT_BUFFER_SYSTEM
````

### FILE: tests/netlists/virtuoso_style.sp
<!-- sha256=8bfe6be1699e2846331ea52c10bf389b41c3a0b3f68d51463c0c82c0427cb883 newline=1 -->
````spice
** Generated for: hspiceD
** Library name: test_lib
** Cell name: top_mixed
** View name: schematic
.subckt ota5t vinp vinn vout vbn vdd vss
mm1 net1 vinp tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm2 vout vinn tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm3 net1 net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm4 vout net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm5 tail vbn vss vss nch_lvt w=8e-6
+ l=200e-9 m=2
.ends ota5t
** Cell name: inv
.subckt inv in out vdd vss
mn0 out in vss vss nch_lvt w=1e-6 l=45e-9 $ pull-down
mp0 out in vdd vdd pch_lvt w=2e-6 l=45e-9
.ends inv
.SUBCKT nand2 A B Y VDD VSS
MN1 Y A X VSS nch_lvt W=1u L=45n
MN2 X B VSS VSS nch_lvt W=1u L=45n
MP1 Y A VDD VDD pch_lvt W=1u L=45n
MP2 Y B VDD VDD pch_lvt W=1u L=45n
.ENDS
.subckt top_mixed a b o en vb vdd vss
xi0 a b n1 vb vdd vss ota5t
xi1 n1 n2 vdd vss inv
xi3 n2 en n3 vdd vss nand2
xi2 n3 o vdd vss inv
c0 n1 vss 10f
r0 o vss 1k
.ends top_mixed
````
