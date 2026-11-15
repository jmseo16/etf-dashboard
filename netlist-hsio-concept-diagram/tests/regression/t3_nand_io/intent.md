# NAND flash IO, full block: designer's note

`nand_io_full.sp` is a Virtuoso `hspiceD` export of one top cell, **`nf_io_top`**. It is the complete DDR (Toggle/ONFI-style) byte IO of a NAND die: 8 DQ pins, DQS/DQSB, RE/nRE, ZQ and VREF.

The file is self-contained. It has placeholder `.MODEL` cards and no `.include`. The top cell is itself a `.subckt`, and nothing instantiates it.

| Item | Value |
|---|---|
| Subcircuits | 92 |
| Hierarchy depth | 6 levels (for example `nf_io_top` / `io_dq_slice` / `tx_dq_slice` / `tx_predrv` / `tx_predrv_leg` / `nand2_q`) |
| Cells mixing devices and instances | 22 (`rx_saff`, `tx_dca`, `tx_ser2`, `tx_predrv_leg`, `rx_vref_gen`, `zq_cal`, `io_pad_bidir`, ...) |
| Flattened MOS (instances) | 6833 (sum of `m=`: 7407) |
| Flattened R / C | 279 / 118 |
| Device lines in the file | 494 X, 292 M, 67 R, 36 C |

## Conventions

**Supplies:**
- `vdd` is the core supply, about 1.0 V. `vccq` is the IO supply, 1.2 V.
- The grounds are `vss` (core) and `vssq` (IO).
- `vss` and `vssq` are coupled only through the back-to-back ESD devices in `esd_rail`.

**Device flavours:**
- `nch`/`pch` are core devices.
- `nch_lvt`/`pch_lvt` are low-Vt core devices, used in the high-speed clock and data cells.
- `nch_hv`/`pch_hv` are thick-oxide IO devices. They are used everywhere on VCCQ and on every pad-facing gate.
- No core device touches `vccq`/`vssq`. Every NMOS bulk is on `vss`/`vssq` and every PMOS bulk on `vdd`/`vccq`; the structure check confirms both.

**Naming:**
- Instances are `XI<n>`. MOS devices are `MM<n>`, with a few named devices: `MMtail`, `MMclamp`, `MMN1`...
- Iterated instances are expanded MSB first (`XI7<7>` ... `XI7<0>`).
- Buses are MSB first (`code<4:0>`).
- Internal nets mix Virtuoso `net0xx` names with meaningful names.

**Libraries** (shown in the `** Library name:` comments):
- `NFIO_STD`: gates, flops, level shifters, clock buffers.
- `NFIO_RX`: receive path.
- `NFIO_TX`: transmit and RE clock path.
- `NFIO_CAL`: DCC and ZQ.
- `NFIO_ESD`: ESD.
- `NFIO_IO`: pad cells, ODT, control and bias hubs, slices, top.

## Top-level pins of `nf_io_top`

### High-speed pads (bidirectional, with ESD)

| Pin | Function |
|---|---|
| `dq<7:0>` | **High-speed data in/out.** Write data comes in to the Rx slices. Read data goes out from the Tx slices on the same pad. |
| `dqs`, `dqsb` | **Strobe, bidirectional.** On writes it is an input: a center-aligned strobe whose two edges sample DQ (`dqsb` is replaced by VREF in single-ended mode). On reads it is driven as an output strobe, generated from RE through a DQ-identical Tx slice, so it is edge-aligned to DQ. |
| `re`, `reb` | **Clock input**, RE/nRE (differential read enable; `reb` is replaced by VREF in single-ended mode). It is the read clock for all outputs. |

### Core-side data and clocks

| Pin | Function |
|---|---|
| `din<31:0>` | **Word-rate data out** to the core: 1:4 deserialized write data. `din<4n+3:4n>` holds DQ<n> UI3..UI0, so `din<4n>` is the first UI. All 4 bits of a word update together, once per DQS/2 period. |
| `din_clk` | **Clock out**: DQS/2 word clock (`div_p` buffered). The core captures `din` on its rising edge, which falls in the middle of the stable window. |
| `dout_e<7:0>`, `dout_o<7:0>` | **Word-rate data in** from the core: even and odd read data per DQ. The even bit is sent while the RE-derived clock is high, the odd bit while it is low. |
| `rclk_core` | **Clock out**: RE-derived clock (core tap of the Tx tree) that launches `dout_e`/`dout_o` and `dqs_burst`. |
| `cal_clk` | **Slow clock in** (about 10 MHz, from the core oscillator). It clocks the ZQ SAR and counter and the DCC comparator and counter. It is not a high-speed clock. |

### Reference and bias

| Pin | Function |
|---|---|
| `vref_ext` | Reference: external VREFQ pad (with ESD), used when `vref_int_en=0`. |
| `zq` | Reference: ZQ pad to the external RZQ, 300 Ω to VSSQ. Primary ESD only, with no series R. |
| `ibias` | Bias: about 10 µA from the bandgap. It is mirrored to the ZQ comparators (sink) and the VREF buffer (source). |

Internal reference and bias nets:
- `vref_rx` (VREFQ) is shared by the 8 DQ receivers, the single-ended DQS reference and the single-ended RE reference.
- `vref_zq` (VCCQ/2) is inside `zq_cal`.
- `vbp_sr`/`vbn_sr` are the pre-driver slew bias.
- `ib_zq` and `ib_vref` are the mirrored bias currents.

### Commands, status, test

| Pin | Class | Function |
|---|---|---|
| `zq_start` | command | One `cal_clk` pulse that starts the pull-up SAR (ZQ calibration command). |
| `dcc_train` | command | DCC training. 1 = run the duty loop while the host toggles RE. 0 = hold the code, clear the lock, gate off the detector and update clock. |
| `zq_done` | status out | Pull-up SAR finished. It also starts PD tracking. |
| `zq_pu_code<4:0>`, `zq_pd_code<4:0>` | status out | Read back the ZQ result. The same nets drive the driver strength internally. |
| `dcc_lock` | status out | DCC locked after two dither events. It also freezes the code. |
| `dcc_code<4:0>` | status out | Current DCC code (offset binary, 10000 neutral). |
| `tm_rxobs` / `rx_obs` | test | Observe `div_p` (DQS/2) on `rx_obs`. |

### Control codes and what they control

| Pin | Controls |
|---|---|
| `rx_en` | Rx power: DQ/DQS receivers (Bazes tails), strobe trees and chains, the VREF DAC qualifier, the observe gate. |
| `rx_mode_um` | **Rx path select.** 0 = matched: DQ goes through `dq_match_dly` and DQS through the 1→3→9 H-trees. 1 = unmatched: DQ goes direct and DQS through the 9-stage repeater chain, whose tap *n* drives DQ<n>. The inactive network is clock-gated (`en_m`/`en_u`; `selub` gates the DQ replica). |
| `dqs_se` | Single-ended DQS (DQS vs VREF) vs differential DQS/DQSB. |
| `vref_int_en` | Internal VREF DAC (ladder + OTA, powered only when selected) vs `vref_ext`. |
| `vref_code<4:0>` | Internal VREF tap, about 34.5 %…71.4 % of VCCQ in about 1.2 % steps. |
| `dqs_dly<2:0>` | Cap-load delay trim on both Rx strobe phases. |
| `dq_dskw<23:0>` | Per-bit Rx DQ deskew, 3 bits per bit (`dq_dskw<3n+2:3n>` for DQ<n>), for training in unmatched mode. |
| `rx_rst_n` | Resets the DQS/2 divider. The release point sets the deser word alignment. |
| `tx_en` | RE receiver enable. |
| `re_se` | Single-ended RE vs differential RE/nRE. |
| `dq_oe` | DQ driver enable. 0 = every PU and PD leg off (Hi-Z). 1 also forces the DQ-group ODT off. |
| `dqs_oe` | DQS/DQSB driver enable (preamble to postamble). 1 also forces the DQS-group ODT off. |
| `dqs_burst` | 1 = DQS/DQSB toggle with RE. 0 = DQS low and DQSB high (preamble/postamble). It is retimed in the slices. |
| `sr_code<1:0>` | Output slew: starving current of the pre-driver final stages. |
| `odt_en`, `odt_code<2:0>` | Termination on DQ/DQS/DQSB: about 300/150/100/75/60/50/43 Ω Thevenin for codes 1..7. It is effective only while that pin group is not driving. |
| `zq_en`, `zq_rst_n` | ZQ analog enable (VREF divider, comparators, replica gates, PD tracking). The reset gives SAR code 0 and PD counter 10000. |
| `drv_ovr_en`, `pu_ovr<4:0>`, `pd_ovr<4:0>` | Driver strength source. 0 = ZQ codes, 1 = override codes (bring-up/test). |
| `dcc_rst_n` | Resets the DCC code to 10000. |

## Signal flow and sub-blocks

### Rx (write data in)

1. **Pad.** `dq<n>` → `io_dq_slice/XI0 io_pad_bidir`. This is GDPMOS/GGNMOS primary protection, then 200 Ω + GGNMOS secondary protection, giving `pad_rx`.
2. **Front end.** `rx_dq_slice`: always-on input TG `rx_tg_q` → `rx_amp_bz` (Bazes self-biased receiver on VCCQ, DQ vs `vref_rx`) → `rx_ls_dn` (VCCQ→VDD) → `dly_trim3` (deskew).
3. **Path select.** `dq_match_dly` (a replica of the strobe `ckgate` + root/branch/leaf `ckbuf`), then three `mux2_hs` cells select data, rise strobe and fall strobe for matched or unmatched mode.
4. **Sampling.** `rx_samp_pair` holds two StrongARM `rx_saff`: rise samples on the true strobe, fall samples on the complement strobe.
5. **Deserialization.** `rx_deser4`: the rise sample is retimed onto the fall strobe. UI0/UI1 are captured on `div_p`. UI2/UI3 are captured on `div_n` and UI0/UI1 re-registered on `div_n`, so the 4-bit word changes once per word.
6. **Strobe path.** `rx_dqs_path` takes `dqs_rx`/`dqsb_rx` from the two `io_dqs_slice` pad cells:
   - An always-on DQS TG, plus DQSB/VREF select TGs.
   - Two identical `rx_amp_bz` with swapped inputs make the true and complement strobes, with equal latency.
   - Then `rx_ls_dn`, `dly_trim3` and `ckgate`.
   - Then the matched `rx_dqs_tree` ×2 and the unmatched `rx_rpt_chain` ×2.
7. **Word clock.** `rx_ckdiv_slice`: a mode mux on leaf/tap 8 of the true strobe, then the `dffr_tg` toggle divider giving `div_p`/`div_n`, then the `din_clk` driver.

**Matching by construction:** the DQ pad cell, TG, receiver, level shifter, trim, clock gate, buffers and mux are the same cells as on the strobe side. In matched mode the strobe-to-data delay difference cancels.

### Tx (read data out)

1. **RE input.** RE/nRE pads (`io_pad_in`) → `re_clk_path`.
2. **Receiver.** `tx_re_rx`: TGs, Bazes receiver, a dummy swapped receiver for input-load symmetry, `rx_ls_dn`.
3. **Duty adjust.** `tx_ckbuf_dca`: `ckbuf` → **`tx_dca`** (the DCC actuator) → `ckbuf_x8`.
4. **Distribution.** `tx_rpt_chain` (4 repeaters + RC wire) → `tx_cktree`:
   - Root, 2 branches of 6 leaves each.
   - `lf<7:0>` go to the DQ slices, `lf<8>` to DQS, `lf<9>` to DQSB.
   - A core tap feeds `tx_rpt` → `rclk_core`.
   - **`lf_dcc` = `ck_dcc`** is the DCC sense leaf, beside the DQS leaves.
5. **Per pin `tx_dq_slice`:**
   - `ck_split` (ck/ckb).
   - `tx_ser2`: even and odd DFFs on ck falling, a half-cycle latch on the odd path, and a TG mux. ck high sends even, ck low sends odd.
   - `ls_up_hs` (VDD→VCCQ).
   - `tx_predrv`: 5 × `tx_predrv_leg` (NAND/NOR with enables, then a current-starved final stage) → `pg<4:0>`/`ng<4:0>`.
6. **Main driver.** The pad cell's `tx_out_drv`: 5 × `tx_drv_unit` with m = 16/8/4/2/1. Each unit is pch_hv 8 µm + 300 Ω up and nch_hv 4 µm + 300 Ω down.
7. **DQS/DQSB.** These use the same `tx_dq_slice` and `io_pad_bidir` (`io_dqs_slice`). The constant patterns from `tx_ctrl` are DQS e=`dqs_burst`, o=0 and DQSB e=~`dqs_burst`, o=1.

### DCC loop (closed, on the RE → repeater → driver clock path)

The loop runs: `dcc_code` → `tx_dca` → RPT chain → tree → `ck_dcc` → `dcc_ctrl`.

Inside `dcc_ctrl`:
- `dcc_det`: a gated clock and its complement drive matched 2-pole RC filters (50 k/0.5 p, 50 k/0.25 p), giving `vp`≈D·VDD and `vn`≈(1−D)·VDD.
- `sa_cmp`: StrongARM comparator on `upd_clk` = `cal_clk` & `dcc_train`.
- `updn_cnt5`: up/down counter, reset to 10000.
- `dcc_lock_det`.
- The counter output `dcc_code` feeds back to `tx_dca`.

**Polarity:** duty > 50 % → `up`=1 → code counts up → the DCA pull-up legs speed the falling output edge → shorter high phase.

**Code map:** 1xxxx shortens the high phase by `code<3:0>` units. 0xxxx lengthens it by `~code<3:0>` units. 10000 and 01111 are both neutral, so the code is monotonic with one duplicate step.

**Lock:** after two valid decision reversals (the first decision after training starts is ignored), `dcc_lock`=1 drives the counter `hold` and freezes the code.

### ZQ calibration (`zq_cal`) → driver strength

**Pull-up loop:**
- `zq_vref` gives VCCQ/2.
- `zq_pu_rep` holds the replica PU legs on the ZQ pin, against RZQ.
- `zq_cmp` (static comparator + `ls_dn`) feeds `zq_sar5`, a 5-step SAR. A comparator 1 means ZQ is above VREF, so the PU is too strong and the trial bit is cleared. The result is `pu_code`.

**Pull-down loop:**
- `zq_pd_rep` is an internal PU copy on top of the PD replica legs, at node `npd`.
- `zq_cmp` feeds `updn_cnt5`, which tracks after `zq_done` and dithers ±1 LSB. The result is `pd_code`.

**Scaling:** the replica unit is 1/8 of the driver unit (1 µm + 2.4 kΩ vs 8 µm + 300 Ω). Matching RZQ = 300 Ω therefore sets the drivers to about 37.5 Ω.

**Code path to the drivers:**
1. `zq_cal.pu_code/pd_code` → `io_ctrl/drv_code_mux` (ZQ or override).
2. → `tx_ctrl`: level shift, then gate with `dq_oe` (DQ group) and `dqs_oe` (DQS group). This gives `pu_en_d/s<4:0>` (active-high PU enables) and `pd_dis_d/s<4:0>` (active-high PD disables).
3. → the per-leg pre-drivers of every DQ and DQS/DQSB slice.

### ESD and ODT

- **`io_pad_bidir`** (DQ ×8, DQS, DQSB) contains:
  - `esd_io_pad`: primary GDPMOS/GGNMOS plus a 200 Ω/GGNMOS secondary on the receiver side.
  - The main driver.
  - `odt_leg_pin`: 3 binary center-tapped PU/PD pairs.
  - A 0.2 pF pad cap.
- **`io_pad_in`** (RE, nRE, VREF_EXT): `esd_io_pad` and a pad cap.
- **ZQ:** `esd_prim`, primary only.
- **`esd_rail`:** RC-triggered clamps VCCQ-VSSQ and VDD-VSS, and `esd_b2b` VSS-VSSQ.
- **`odt_ctrl`** (in `io_ctrl`) makes separate gate buses for the DQ group and the DQS group: `odt_en & ~dq_oe` and `odt_en & ~dqs_oe`. The termination therefore never fights the driver it shares a pad with.

### Control and bias hubs (static)

- **`io_ctrl`** = `rx_ctrl` + `drv_code_mux` + `tx_ctrl` + `odt_ctrl`. All inputs are VDD-domain register/command bits. The `_q` outputs and the leg/ODT gate buses are VCCQ.
- **`io_bias`** = `ib_dist` + `tx_sr_bias` + `rx_vref_gen` (32-tap ladder, `vref_mux32` TG tree, `vref_buf_ota`, ext/int `amux2_q`, decap).

## What is and is not on the high-speed path

**On the path (in series with data or strobe/clock):**
- Rx: pad cells (passive pass-through), `rx_dq_slice` and below, `rx_dqs_path`, `rx_dqs_tree`, `rx_rpt_chain`, `rx_ckdiv_slice`.
- Tx: `re_clk_path` and below (including `tx_dca`), `tx_dq_slice` and below, `tx_out_drv`.
- Shared library cells: the HS library cells, and `dffr_tg`/`nand2_x1`/`nor2_x1` inside the divider.

**Not on the path:**
- Control: `io_ctrl` (`rx_ctrl`, `tx_ctrl`, `odt_ctrl`, `drv_code_mux`, `mux2_x1`, `ls_up`, `inv_x2`, `tie_hilo`).
- Bias and reference: `io_bias` (`ib_dist`, `tx_sr_bias`, `rx_vref_gen`, `vref_mux32`, `vref_buf_ota`, `amux2_q`).
- Calibration: `zq_cal` and all its children, and `dcc_ctrl` (`dcc_det`, `sa_cmp`, `updn_cnt5`, `dcc_lock_det`; it only loads the sense leaf).
- Termination and rail ESD: `odt_leg_pin` (a shunt load), `esd_rail`, `esd_rc_clamp`, `esd_b2b`, `esd_prim`.
- Test: `rx_obs_buf`.

**Signal categories:**
- Word-rate digital: `din<31:0>`, `dout_e/o<7:0>`, and inside the cells `p0/p1/rd` of the deser and `de/do/qe/qo` of the serializer.
- Slow loop-internal signals: `vp/vn/up`, `cmp_pu/cmp_pd`, SAR phase.

## Intentional asymmetries and unused nets

- **Dummy loads (unused outputs):**
  - `ckc_m<8>` and `ckc_u<8>`: the complement-strobe leaf/tap 8.
  - `tx_re_rx/net011`: the dummy receiver output.
  - `dcc_det/net012`.
- **Unused flop `qb` outputs:** the sampler `qb`s (`rx_samp_pair/net07`, `net08`), `zq_sar5 phb/codeb/doneb`, `updn_cnt5 cqb/net012`, `dcc_lock_det/net010`, `net011`, and the DCC comparator `qb` (`dcc_ctrl/net011`).
- **Unused level-shifter complements:** in `tx_ctrl`, `odt_ctrl`, `tx_sr_bias` and `zq_gate_drv`.
- **Unused gate-driver outputs:** `zq_cal pu_g<4:0>` and `pd_gb<4:0>`.
- **Other asymmetries:**
  - The ratioed `ls_up_hs` has unequal rise/fall delays.
  - The DCA's rise/fall asymmetry is the correction mechanism.
  - The `div_n` buffer is one inverter later than `div_p`. This is tolerated, because the deser window is a full DQS period.
- **Tie-offs:**
  - `dcc_lock_det/XI2` has its D tied to `vdd` (a valid flag).
  - The ZQ PD counter `hold` is tied to `vss`.

## Integration changes vs. the separate sub-block netlists

- The main driver legs moved from `tx_dq_slice` into the shared pad cell. The pad cap moved from `tx_out_drv` to `io_pad_bidir`.
- The DCC now lives in the RE path: the standalone `dcc_dca` was dropped and `tx_dca` is used. The detector now senses tree leaf `lf_dcc`, which was the dummy leaf. The local monitor tap was removed. A lock detector was added.
- `rx_deser4` now has 6 flops, so all 4 output bits update together. In the old version half the word changed on the core capture edge.
- The ZQ replica legs were rescaled to 1/8 of the driver unit, so the calibrated code gives the right driver impedance.
- `ib_dist` now also sources the VREF buffer bias.
- ODT now has per-group auto-off.
- The SE RE reference is the shared `vref_rx`.
- `wire_rc` was split into `wire_rc_rx`/`wire_rc_tx` (different RC), and duplicate library cells were merged.

## Checks run (scripts in `scripts/`)

**`check_netlist.py`:** all 92 subckts are defined before use and used, there is exactly one top, and the pin counts match. MOS have 4 terminals, a known model and W/L. The bulk/domain rules hold. No pin is unconnected inside its cell. Every single-connection net is in the intentional list above.

**`check_logic.py`:** a unit-delay switch-level simulation (`swsim.py`) of the netlist's own transistors. It passed 994 checks:
- Every standard gate and level shifter.
- Every flop and latch.
- `tx_dca` decode and polarity for all 32 codes.
- Tree and chain polarity.
- The DQS-slice serializer through the pad: even/odd order, Hi-Z, partial strength, ODT.
- Samplers + 6-flop deser + divider, with words checked in UI order.
- `updn_cnt5`: count, saturate, hold, reset.
- `zq_sar5` with a behavioural comparator: all 32 targets in 5 steps.
- The closed DCC loop with a behavioural duty model: it locks within ±1 LSB from both sides, freezes, and releases on `dcc_train`=0.
- `io_ctrl` decode on random vectors.

**Not simulated:** the analog cells (Bazes receivers, OTA, ZQ comparators, ESD, RC detector) were checked by inspection only.

**`check_key.py`:** validates the answer key against the netlist.
