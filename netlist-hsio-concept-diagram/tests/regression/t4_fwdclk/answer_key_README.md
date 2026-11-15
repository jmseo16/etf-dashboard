# Answer key format

`netlist_g.json` is the designer's ground truth for `netlist_g.sp`, a forwarded-clock serial-link IO. Its top cell is `fcl_link_top`. The format is the same as the iter3 key (`nand_io_full.json`). This key adds a few fields and classes, all defined below.

## Top-level fields

- `netlist`: the netlist file.
- `top`: the top cell. It is a `.subckt`, and nothing instantiates it.
- `supplies`, `grounds`: the supply and ground **ports** of the top: `avdd`/`vddq` and `avss`/`vssq`.
- `globals` (new): supplies that are `.global` nets and not pins: `vddd`/`vssd`. The FCL_STD cells and the digital cells built from them have no supply pins. The analog, CML, ESD and pad cells take `avdd`/`avss` or `vddq`/`vssq` as pins.
- `ports`: one entry per top-cell port. A bus is written `name[MSB:LSB]`. The 111 pins are grouped into 28 entries. Each entry has:
  - `class`: one of the port classes below.
  - `function`: a one-line description.
- `cells`: an entry for **every** subcircuit in the netlist (55). That covers all hierarchical cells and all leaf cells, whether or not they are on the high-speed path.

## Port classes

| Class | Meaning |
|---|---|
| `hs_data_in` / `hs_data_out` / `hs_data_io` | Bit-rate data. `rx_p/rx_n[3:0]` are inputs and `tx_p/tx_n` are outputs. `hs_data_io` is not used here. |
| `clock_in` / `clock_out` | Clocks and strobes. `fck_p/fck_n` is the forwarded clock. `cstb_pad` is the slow command strobe; its function text says it is not a high-speed clock. `rx_wck[3:0]` and `tx_wck` are word clocks. |
| `word_rate_data` | Core-side parallel data: `rxd[31:0]` (1:8 deser outputs) and `txd[7:0]` (serializer input). |
| `important_control` | Controls that change high-speed behaviour: the Tx FFE weights `txffe_pre/main/post`. |
| `general_control` | Resets: `rst_n`, `dll_rst_n`. |
| `command` | Defined for completeness; not used at the top. |
| `status_out` | Read-back: `rx_pic[19:0]` (CDR codes) and `cmd_q[3:0]` (command register). |
| `test_digital` | `ro_div`, `ro_cnt[5:0]`, `fc_rst_n`. |
| `test_analog` (new) | Analog observation pin: `dll_vmon`, the DLL control voltage through 20 k. |
| `reference` | Defined for completeness; not used at the top. The termination common mode is generated inside. |
| `bias` | Bias current: `ibias`. |
| `power` | Supplies and grounds. |
| `slow_signal` | The slow single-ended CMOS command pads `cmd_pad[3:0]`. |

## Per-cell fields

| Field | Meaning |
|---|---|
| `role` | What the block is. |
| `on_high_speed_path` | `true` if the cell carries bit-rate data or a high-speed clock in series: the receive data path, the DLL and phase distribution, the phase interpolator and samplers, the deserializer, the Johnson word-clock divider, the serializer, FFE and driver. Loop-control cells are `false`: PFD, charge pump, loop filter, vote and accumulator. So are bias, termination, ESD, the test oscillator and the slow pads. A generic library cell is `true` if any instance of it sits on such a path. One subtle case: `fcr_bbx` (the Alexander PD) is `true`, because its two data-retime flops are also the first two deserializer stages. |
| `inverting` | The polarity from the main input to the main output. It may be a single value or an object. **Extended:** <ul><li>`true`/`false` for a cell with one main output.</li><li>An object `{output_pin: true/false}` for a cell with several main outputs, such as a differential pair: `{"outp": false, "outn": true}` means `outp` follows the true input.</li><li>`null` when there is no single in→out polarity: several functions, a loop, a passive network, or an enable-only path.</li></ul> |
| `children` | Subcircuit instances only. MOS, R and C devices are not listed. An iterated instance is listed once under its iterated name (`X0[7:0]`), which stands for `X0[7]` … `X0[0]`. |
| `signal_flow` | A list of `[source, destination, net, net_class]` entries. It gives the main paths and is not an exhaustive connectivity dump. |
| `controls` | Maps a control net (or bus `[MSB:LSB]`, or a `p/n` pair such as `ck/ckb`) to what it sets. |
| `notes` | Feedback loops, unused outputs, intentional asymmetry, look-alike traps and so on. |

## `signal_flow` endpoint syntax

- `PORT.<pin>` is a pin of the cell itself.
- `<inst>.<pin>` is a pin of a child instance, using the pin name from that child's `.subckt` line.
  - A range of an iterated instance is allowed (`X0[7:2].q`), including a stepped range (`X1[3:1:2].y` = `X1[3]`, `X1[1]`).
  - So is a bus pin of an iterated range. `X2[3:0].rxd[7:0]` with net `rxd[31:0]` maps `X2[3].rxd[7]` to `rxd[31]`, …, `X2[0].rxd[0]` to `rxd[0]`.
  - When the net is narrower than the expanded endpoint, every instance connects to that same bus. For example, `X2[3:0].ph[7:0]` with net `ph[7:0]` means all four lanes get `ph[7:0]`.
- `<MOS>.<d|g|s|b>` is a MOS terminal.
- A bare device name (`R0`, `C1`) is a passive R or C, where the terminal does not matter.
- Net names follow the netlist:
  - Buses use `[MSB:LSB]`. An ascending range (`rxd[0:7]`) lists bits in that order and is used when the bit order reverses.
  - A stepped range is `[start:stop:step]`, for example `ph[7:1:2]` for the odd phases.

## `net_class` values

`net_class` is the direction-free form of the port classes, plus three new classes for loops. The values are:
- `hs_data`
- `clock`: includes the DLL phases, PI output, CMOS sampling clocks, word clocks, the Johnson load pulse `ld`, and the slow strobe.
- `word_rate_data`
- `important_control`
- `general_control`
- `command`
- `status`
- `reference`: the termination common mode `vcm`.
- `bias`: bias currents and gate voltages, tail nodes, charge-pump bias.
- `slow_signal`: slow pad signals before the command register.
- `test_digital`
- `test_analog` (new)
- `power`: ESD and clamp nodes.
- `loop_control` (new): analog loop control voltages. These are the DLL `vctl` (charge pump → loop filter → delay-line NMOS starve gates) and `vcp` (the PMOS starve bias derived from `vctl`). They keep this class where the same nodes bias the replica ring oscillator.
- `loop_error` (new): phase-error signals inside a loop. These are the PFD `up/dn/upb/dnb` and its reset nodes, the Alexander-PD `up/dn`, the vote outputs `vub/vdb`, and the decoded count enables `u/d`.
- `pi_code` (new): the digital CDR state that steers the interpolator. It covers the accumulator code and carries, `code[4:2]` as the phase-pair select (`k`, `kb`), and `code[1:0]`/`codeb[1:0]` as the interpolator tail weights `w`/`wb`. At the lane port the same code is shown as `status` for the read-back path.

Classes follow what a signal does, not its name. For example, `ld` is a capture strobe (`clock`), not data. `vcn` in `fct_cs5` is the DLL control voltage (`loop_control`), even though it only biases the oscillator there.

## Conventions

- Iterated instances and buses are written MSB first, except where an ascending range marks a bit-order reversal.
- In a lane word, `rxd[8n]` is the oldest bit, the first UI of the word. In the Tx, `txd[0]` is sent first.
- Phases are named by phase, not by stage: `ph[k]` / `pho[k]` is at k × 45°.
- Device multiplicity (`m=`) on instances (DAC legs, clock drivers) and on devices is shown in the netlist and mentioned in `role` and `notes`.
  - The flattened MOS count (3992) counts device instances and ignores `m`.
  - The sum of `m` is 4687.
- The netlist uses `.param` values (W/L names and expressions), subckt default parameters (`rl=` on the CML cells) and instance overrides (`rl=450`, `rl=420`).

## Checks run on this file (`scripts/check_key.py`)

- The `ports` entries expand to exactly the 111 pins of `fcl_link_top`, every class is from the lists above, and every port has a function.
- `globals` are declared `.global` in the netlist.
- Every subcircuit has an entry, and every entry names a subcircuit.
- Every child list matches the netlist exactly, including iterated instances, and every child has a role.
- Every endpoint names an existing instance or device and an existing pin.
- Every net exists in its cell.
- Every endpoint, scalar or range, really connects to the net named for it, bit by bit for ranges.
- Every `controls` key is a net of the cell.
- `inverting` is a bool, `null`, or an object whose keys are pins of the cell.
- A mutation test (wrong net, wrong pin, reversed bus, missing child, bad class, dropped port) was run once by hand, and the checker rejected each mutation.
