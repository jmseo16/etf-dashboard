# Answer key format

`nand_io_full.json` is the designer's ground truth for `nand_io_full.sp`, the full NAND flash IO block. Its top cell is `nf_io_top`. The format is the same as the sub-block keys in `material/answer_key`. The class vocabulary is extended as described below.

## Top-level fields

- `netlist`: the netlist file.
- `top`: the top cell. It is a `.subckt`, and nothing instantiates it.
- `supplies`, `grounds`: the supply and ground port names. They are `vdd`/`vccq` and `vss`/`vssq`.
- `ports`: one entry per top-cell port. A bus is written as `name<MSB:LSB>`; the 153 pins are grouped into 49 entries. Each entry has:
  - `class`: one of the port classes below.
  - `function`: a one-line description.
- `cells`: an entry for **every** subcircuit in the netlist (92). That covers all hierarchical cells and all leaf cells, whether or not they are on the high-speed path.

## Port classes

| Class | Meaning |
|---|---|
| `hs_data_in` / `hs_data_out` / `hs_data_io` | High-speed (bit-rate) data. `dq<7:0>` is `hs_data_io` because the pad is bidirectional. |
| `clock_in` / `clock_out` | Clocks and strobes. `dqs`/`dqsb` are bidirectional strobe pads and are classed `clock_in`; their function text says they are also driven on reads. `cal_clk` is a slow calibration clock. |
| `word_rate_data` | Core-side parallel data: `din<31:0>` (1:4 deser output) and `dout_e/o<7:0>` (serializer inputs). |
| `important_control` | Mode, enable and strength controls that change the high-speed behaviour (`rx_mode_um`, `dq_oe`, `odt_code`, ...). |
| `general_control` | Trims, resets and overrides (`dq_dskw`, `dqs_dly`, `sr_code`, `pu_ovr`, ...). |
| `command` | Command-decoder strobes that start an operation: `zq_start`, `dcc_train`. |
| `status_out` | Read-back and status: `zq_done`, `zq_pu_code`, `zq_pd_code`, `dcc_lock`, `dcc_code`. |
| `test_digital` | `tm_rxobs`, `rx_obs`. |
| `reference` | Reference voltage or resistor pins: `vref_ext`, `zq`. |
| `bias` | Bias current: `ibias`. |
| `power` | Supplies and grounds. |
| `slow_signal` | Defined for completeness; not used at the top. |

## Per-cell fields

| Field | Meaning |
|---|---|
| `role` | What the block is. |
| `on_high_speed_path` | `true` if the cell carries the high-speed data or clock/strobe signal in series: the mission data path, the strobe/clock distribution, the pad pass-through, the DCA in the RE path. Static control, bias, calibration (DCC detector/comparator/counter, ZQ), termination, test and rail-ESD cells are `false`. A generic library cell is `true` if any instance of it sits on such a path. |
| `inverting` | The polarity from the main input to the main output. It is `null` for cells with several outputs or several functions (for example the bidirectional slices), or with no single in→out path. |
| `children` | Subcircuit instances only. MOS, R and C devices are not listed. An iterated instance is listed once under its Virtuoso iterated name (`XI7<7:0>`), which stands for the expanded `XI7<7>` … `XI7<0>`. |
| `signal_flow` | A list of `[source, destination, net, net_class]` entries. It gives the main paths and is not an exhaustive connectivity dump. Bidirectional pads appear in both directions. |
| `controls` | Maps a control net (or bus `MSB:LSB`) to what it sets. |
| `notes` | Feedback loops, unused outputs, intentional asymmetry, mode muxes, and so on. |

## `signal_flow` endpoint syntax

- `PORT.<pin>` is a pin of the cell itself.
- `<inst>.<pin>` is a pin of a child instance, using the pin name from that child's `.subckt` line.
  - A range of an iterated instance is allowed (`XI7<7:0>.de`), including a stepped range (`XI0<14:0:2>.z`).
  - So is a bus pin (`XI7<7:0>.rd<3:0>`, whose net is the matching bus `din<31:0>`: `XI7<7>.rd<3>` maps to `din<31>`, …, `XI7<0>.rd<0>` maps to `din<0>`).
  - When a bus pin of an iterated range lists a narrower net (`XI7<7:0>.pu_en<4:0>` with `pu_en_d<4:0>`), every instance connects to that same bus.
- `<MOS>.<d|g|s|b>` is a MOS terminal.
- A bare device name (`RR0`, or an iterated group `RR1<30:0>`) is a passive R or C, or a ladder, where the terminal does not matter.
- Net names follow the netlist.
  - Buses use `<MSB:LSB>`.
  - A stepped range is `<start:stop:step>`, for example `t<31:1:2>` for the odd taps.

## `net_class` values

`net_class` is the direction-free form of the port classes. The values are:
- `hs_data`
- `clock`
- `word_rate_data`
- `important_control`
- `general_control`
- `command`
- `status`
- `reference` (VREF nodes, ladder taps, ZQ pin and replica nodes)
- `bias` (bias currents, self-bias and slew-bias nodes)
- `slow_signal` (loop-internal analog/digital nodes: detector outputs, comparator outputs, SAR phases)
- `test_digital`
- `power`

## Conventions

- Iterated instances and buses are written MSB first.
- In a bit slice, `rd<0>` / `din<4n>` is the first UI of the 4-UI word.
- Device multiplicity (`m=`) on subcircuit instances is shown in the netlist and mentioned in `role` and `notes`. The flattened MOS count (6833) counts device instances and ignores `m`; the sum of `m` is 7407.

## Checks run on this file (`scripts/check_key.py`)

- The `ports` entries expand to exactly the 153 pins of `nf_io_top`, and every class is from the list above.
- Every subcircuit has an entry, and every entry names a subcircuit.
- Every child list matches the netlist exactly, including iterated instances.
- Every endpoint names an existing instance or device and an existing pin.
- Every net exists in its cell.
- Every endpoint, scalar or range, really connects to the net named for it (bit by bit for ranges).
- Every `controls` key is a net of the cell.
