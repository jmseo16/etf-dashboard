# Answer keys

There is one JSON file per netlist: `bist.json` (`../bist.sp`), `zqcal.json` (`../zqcal.sp`) and `dqs_rx.json` (`../dqs_rx.sp`). Each one is the ground truth for checking a block diagram drawn from that netlist.

**Top-level fields**
- `top`: the top cell.
- `supplies` / `grounds`: supply and ground net names.
- `ports`: one entry per top-level port. A bus is grouped as `name<msb:lsb>`. Each entry has a `class` (`hs_data_in`, `hs_data_out`, `clock_in`, `clock_out`, `important_control`, `general_control`, `bias`, `power`, `slow_signal` or `test_digital`) and a one-line `function`.

**`cells`**

The keys cover every cell that contains subcircuit instances, plus the leaf cells on the high-speed, clock or strobe path (and a few other notable leaf cells). Each cell has these fields:
- `role`: what the block is.
- `on_high_speed_path`: whether the block carries the high-speed data, clock or strobe.
- `inverting`: the polarity from main input to main output. `null` means it does not apply (logic or control blocks).
- `children`: the subcircuit instances only. Iterated instances are grouped, e.g. `xi0<3:0>`. Direct MOS, R and C devices are not listed as children. Their counts are appended at the end of `notes` as `[direct primitives in this cell: ...]`.
- `signal_flow`: rows of `[from, to, net, class]` in rough flow order.
  - `from` and `to` are written as `<inst>.<pin>`. `PORT.<pin>` means the cell's own port. In leaf cells, a device terminal is written as `mn0.g` (MOS d/g/s/b) or `r0.p` / `r0.n` (first / second node of an R or C).
  - `net` is the net name inside that cell.
  - `class` is one of `hs_data`, `word_data`, `clock`, `strobe`, `analog`, `reference`, `bias`, `control`, `code`, `decision`, `status`, `data` or `logic`.
  - For buses and repeated bit slices, only representative bits are listed (for example `<0>` and `<3>`). The other bits are wired the same way.
- `controls`: each control net or bus, and what it sets.
- `notes`: feedback loops, unused outputs, deliberate asymmetry and other things a reviewer needs to know.

Every `from`/`to` pair in `signal_flow` was checked by script against the netlist. Both ends resolve to the stated net.
