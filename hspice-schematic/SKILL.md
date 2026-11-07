---
name: hspice-schematic
description: Draw an interactive, textbook-style (Razavi) schematic from an HSPICE / Virtuoso-exported netlist and verify it against the netlist. Use whenever the user gives a SPICE/HSPICE netlist (.sp, .cir, .net, pasted text with .SUBCKT) and wants to see it as a schematic, block diagram, or transistor-level drawing, or asks to check/visualise a circuit's hierarchy.
---

# HSPICE netlist → interactive schematic

Produces one self-contained HTML file (works offline): a block diagram of the top cell; click
any block to open the level below, down to transistors. Every drawing is checked against the
netlist before it is handed over.

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
- `scripts/hsch/verify.py` – connectivity extraction from the drawing + visual lint
- `scripts/screenshot.js` – PNG per view for visual review
- `scripts/ui_selftest.js` – automated test of every viewer control (desktop + phone)
- `references/style_rules.md` – the drawing rules (from the user's reference figures)
