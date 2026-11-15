# Answer key format

`netlist_f.json` is the designer's ground truth for `netlist_f.sp`, an LPDDR5-style x8 DQ byte IO (memory side). Its top cell is `LP5_DQ_BYTE`. The format and the class vocabulary are the same as the iter3 key (`nand_io_full.json`). Only the bus and instance notation changes, because this netlist uses bracket buses and individually written instances. No new classes are needed.

## Top-level fields

- `netlist`: the netlist file.
- `top`: the top cell. It is a `.subckt`, and nothing instantiates it.
- `supplies`, `grounds`: the supply and ground port names.
  - `VDD` is the core supply (about 0.75 V); `VDDQ` is the LVSTL IO supply (about 0.5 V).
  - The grounds are `VSS` (core) and `VSSQ` (IO).
- `ports`: one entry per top-cell port or bus. A bus is written `NAME[MSB:LSB]`. The 114 pins are grouped into 32 entries. Each entry has:
  - `class`: one of the port classes below.
  - `function`: a one-line description.
- `cells`: one entry for **every** subcircuit in the netlist (49). That covers hierarchical cells and leaf cells, whether or not they are on the high-speed path.

## Port classes

| Class | Meaning |
|---|---|
| `hs_data_in` / `hs_data_out` / `hs_data_io` | High-speed (bit-rate) data. `DQ[7:0]` is `hs_data_io` because the pad is bidirectional. |
| `clock_in` / `clock_out` | Clocks. `WCK`/`WCKB` are the high-speed write clock. `TXCLK`/`RXCLK` are quarter-rate word clocks to the core. `ZQ_CLK` is a slow calibration clock; its function text says so. |
| `word_rate_data` | Core-side parallel data: `TXD[31:0]` (serializer inputs) and `RXD[31:0]` (DFE decisions, one bit per UI per DQ). |
| `important_control` | Controls that change the high-speed behaviour in mission mode: enables, strengths, equalization, slew, threshold, termination, and mode switches (`OE`, `EQ_EN`, `SR`, `ODT_*`, `VREF_CODE`, `CTLE_CODE`, `DFE_TAP`, `RX_EN`, `CK_EN`, `DCC_EN`, `CAL_EN`). |
| `general_control` | Resets and settings that only initialize or restart something and leave the steady-state high-speed path unchanged (`DIV_RST`, `DCC_RST`). |
| `command` | A strobe that starts an operation: `ZQ_START`. |
| `status_out` | Read-back and status: `ZQ_DONE`, `ZQ_CODE[4:0]`, `CAL_DONE`. |
| `test_digital` | Defined for completeness; not used. |
| `reference` | Reference voltage or resistor pins: `ZQ`. |
| `bias` | Bias current: `IBIAS`. |
| `power` | Supplies and grounds. |
| `slow_signal` | Defined for completeness; not used at the top. |

Controls are classed by their effect, not by their name.
- `SR[1:0]` (slew) sets the output edge rate, so it is `important_control`.
- `DCC_EN` decides whether the clock duty is corrected, so it is `important_control`.
- `CAL_EN` disconnects the receiver input and forces the DFE tap to zero, so it is `important_control`.
- `DCC_RST` and `DIV_RST` only restart a loop or align a phase, so they are `general_control`.

## Per-cell fields

| Field | Meaning |
|---|---|
| `role` | What the block is. |
| `on_high_speed_path` | `true` if the cell carries the high-speed data or clock in series: the Tx data path (serializer, predriver, legs), the Rx data path (CTLE, comparators, DFE mux-latch), the WCK clock path (pad series R, CML buffer, CML-to-CMOS, DCA, divider, tree), and the slices and top that contain them. Static control, bias, calibration (DCC detector/OTA, ZQ, offset-cal counter/DAC/timer), termination, VREF and ESD shunt cells are `false`. A generic library cell is `true` if any instance of it sits on such a path. |
| `inverting` | Polarity from the main input to the main output. It is `null` for cells with several outputs or functions, or with no single in-to-out path. For multi-output cells that still have a clear main output (for example `DFF_TSPC`, `TX_PDRV`, `TX_SER4`), the value refers to the main output and `notes` explains the others. |
| `children` | Subcircuit instances only, one entry per instance (this netlist has no iterated instances). MOS, R and C devices are not listed. |
| `signal_flow` | A list of `[source, destination, net, net_class]` entries. It gives the main paths and is not an exhaustive connectivity dump. Bidirectional pads appear in both directions. |
| `controls` | Maps a control net (or bus `[MSB:LSB]`) of the cell to what it sets. |
| `notes` | Feedback loops, unused outputs, intentional asymmetry, cross-wiring and so on. |

## `signal_flow` endpoint syntax

- `PORT.<pin>` is a pin of the cell itself.
- `<inst>.<pin>` is a pin of a child instance, using the pin name from that child's `.SUBCKT` line.
  - A bus pin range is allowed: `X_SER.TXD[3:0]`. Its net is a bus of the same width, matched bit by bit, MSB first.
  - `X_DQ1.TXD[3:0]` with net `TXD[7:4]` means `X_DQ1.TXD[3]` is on `TXD[7]`, and so on.
- `<MOS>.<d|g|s|b>` is a MOS terminal.
- A bare device name (`R_SEC`, `C_INT`) is a passive R or C; the terminal does not matter, but the device must touch the named net.
- Net names follow the netlist.
  - Buses use `[MSB:LSB]`.
  - A stepped range `[start:stop:step]` is accepted by the checker but not used.

## `net_class` values

`net_class` is the direction-free form of the port classes:
- `hs_data`
- `clock`
- `word_rate_data`
- `important_control`
- `general_control`
- `command`
- `status`
- `reference` (VREF nodes, ladder nodes, ZQ pad and divider, CTLE VREF input)
- `bias` (bias voltages, including the code-set DAC outputs `VALF`, `VTRN`, `VTRP`)
- `slow_signal` (loop-internal nodes: DCC detector outputs and `VCTRL`, counter and SAR internals, comparator decisions inside calibration loops)
- `test_digital`
- `power`

## Conventions

- Buses are written MSB first.
- In a DQ slice, `TXD[0]` / `RXD[0]` (top-level `TXD[4n]` / `RXD[4n]`) is the first UI of the 4-UI word.
- Instance multiplicity (`M=` on an X line) gives leg weights. It is shown in the netlist and mentioned in `role` or `children`. The flattened MOS count (3973) counts device instances and ignores `M`.

## Checks run on this file (`scripts/check_key.py`)

- The `ports` entries expand to exactly the 114 pins of `LP5_DQ_BYTE`, and every class is from the list above.
- The key's top is the netlist's only uninstantiated cell.
- Every subcircuit has an entry, and every entry names a subcircuit; every entry has all seven fields, and `role`/`notes` are non-empty.
- Every child list matches the netlist exactly (instance name and cell), with a role per child.
- Every endpoint names an existing pin, instance, MOS terminal or passive device.
- Every net exists in its cell.
- Every endpoint, scalar or range, really connects to the net named for it (bit by bit for ranges).
- Every `controls` key is a net of the cell.
