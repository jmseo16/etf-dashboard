# Design intent notes

Process assumed: generic 28 nm-class CMOS, core devices `nch`, `pch`, `nch_lvt` (models come from the PDK, not included). Nominal vdd = vddq = 0.9 V.

## tx.sp: 4:1 SST serial-link transmitter with 3-tap FFE

**Top cell:** `tx_top`

- **High-speed data in:** `din<3:0>`: quarter-rate parallel data, sent with `din<0>` first. It is launched by the digital logic on `clk_div4` and sampled inside on the falling edge of ck4.
- **High-speed data out:** `txp` / `txn`, the differential pads (SST voltage-mode, about 50 ohm per side with all segments on and mid-range zcal).
- **Clock in:** `ckhr_p` / `ckhr_n`, the half-rate differential CML clock from the PLL.
- **Clock out:** `clk_div4`, the quarter-rate CMOS clock sent to the digital parallel interface.
- **Digital control:**
  - `oe`: output enable. When 0, all driver slices go hi-Z.
  - `eidle`: electrical idle. All slices go hi-Z and the 2k/2k common-mode keeper is switched onto each pad.
  - `en_main<3:0>`: enables for the binary-weighted main-tap slices (1/2/4/8 units). Sets the main strength and swing.
  - `sel_pre<1:0>`: steers pre-cursor slice groups of 1 and 2 units from main data (0) to inverted next-bit data (1). Sets the pre-tap weight, 0 to 3 out of 25 units.
  - `sel_post<2:0>`: steers post-cursor slice groups of 1, 2 and 4 units from main data to inverted previous-bit data. Sets the post-tap weight, 0 to 7 out of 25 units.
  - `zcal_p<1:0>` / `zcal_n<1:0>`: impedance-calibration fingers (weights 1x and 2x) in every slice, for the pull-up and pull-down legs separately.
  - `bias_en`: enables the bias. When 0, `nbias` is pulled low and the clock receiver turns off.
- **Bias:** `ibias_50u`, a 50 uA reference current sunk into a diode-connected NMOS. It is mirrored to the CML clock buffer (x8, 400 uA) and to the CML-to-CMOS tails (x2).
- **Power:** `vdd` (core logic, clock path, tap muxes), `vddq` (pre-drivers, SST slices, pad ESD), `vss`.

**Sub-blocks**

- `tx_bias`: turns the reference current into the `nbias` voltage, with a power-down pull-down and a decap.
- `tx_clkrx`: 100 ohm differential input termination (50 + 50 ohm to an AC-grounded common-mode node), a resistively loaded CML clock buffer, and two `cml2cmos` cells with swapped inputs. Outputs `ck2` / `ck2b`.
- `cml2cmos`: 5T NMOS-input OTA followed by two inverters (non-inverting).
- `dff` (instance xi2 in the top cell): divide-by-2 with `qb` fed back to `d`. Turns `ck2` into `ck4` / `ck4b`.
- `tx_ffe_tapgen`: 9 DFFs clocked on the falling edge of ck4. Builds three time-aligned 4-bit words:
  - main = the input word delayed by one word;
  - pre = main advanced by 1 UI;
  - post = main delayed by 1 UI.
- `ser4to1` (x3: main, pre, post): 2-level tree of `mux2to1` cells (ck4 stage, then ck2 stage). Produces complementary full-rate outputs. A tgate in the outb path matches its delay to the extra inverter in the out path.
- `mux2to1`: two DFFs plus a half-cycle latch on the d1 path, then a clocked tristate-inverter selector.
- `dff` / `dlatch`: master-slave flop built from C2MOS-style latches.
- `tx_ctrl_dec`: static gates that produce:
  - the internal enable `en_t = oe & !eidle`;
  - per-bit main enables gated with `en_t`;
  - complements of the select and zcal_n codes;
  - keeper controls.
- `tx_drv_pad` (x2, one per pad). Each contains:
  - `tx_tapmux` per slice group, including a dummy mux on the main path for delay matching;
  - a `tx_predrv` tapered inverter chain per group;
  - binary-weighted `sst_slice` instances, 25 units in total;
  - the idle common-mode keeper;
  - a 10 ohm CDM series resistor;
  - `tx_pad_esd`.

  The negative FFE taps come from feeding the opposite polarity of pre/post data into each pad.
- `sst_slice`: unit SST leg. NAND/NOR gating gives data, enable and hi-Z control. The pull-up and pull-down stacks each have a base finger plus two zcal fingers, and their own 900 ohm series resistor.
- `tx_pad_esd`: GGNMOS to vss and gate-tied PMOS to vddq (with gate resistors), plus 120 fF pad parasitic.
- `esd_rc_clamp` (on vddq and on vdd): RC-triggered big-NMOS rail clamp.
- Top-level MOS decaps.

## dcc.sp: digitally controlled duty-cycle corrector (differential clock)

**Top cell:** `dcc_top`

- **Clock in:** `clkin_p` / `clkin_n`, a differential CML clock from the distribution network.
- **Clock out:** `clkout_p` / `clkout_n`, the duty-corrected CMOS clocks.
- **Detector clock:** `cmp_clk`, a slow comparator clock (for example tens of MHz) from the DCC controller.
- **Detector out:** `dcd_out` / `dcd_outb`. `dcd_out = 1` when avg(clkout_p) > avg(clkout_n), meaning the p duty is above 50% (with `dcd_swap = 0`). The FSM that turns this into codes is off-block.
- **Digital control:**
  - `clk_en`: enables the bias and receivers. When 0, the receiver outputs are forced high.
  - `dcc_en`: correction enable. When 0, all trim legs are off and the clock passes through.
  - `dcc_sign`: correction direction. 1 increases the clkout_p duty and decreases the clkout_n duty; 0 does the reverse.
  - `dcc_mag<4:0>`: binary correction magnitude, 0 to 31 unit legs.
  - `dcd_en`: gates the comparator clock.
  - `dcd_swap`: chopper. Swaps the comparator inputs to cancel offset; the controller inverts `dcd_out` when it is set.
- **Bias:** `ibias_25u`, a 25 uA reference mirrored x4 into each CML-to-CMOS receiver tail.
- **Power:** `vdd`, `vss`.

**Sub-blocks**

- `dcc_bias`: diode-connected reference with a power-down pull-down and a decap.
- `cml2cmos_rx` (x2, with swapped inputs for p and n): 5T OTA plus two inverters, with a PMOS pull-up that sets a defined state when disabled.
- `dcc_code_dec`: NAND3 + inverter decode into four control buses:
  - `a = en & sign & mag`, and its complement `ab`;
  - `b = en & !sign & mag`, and its complement `bb`.
- `dcc_path` (x2): `dcc_adj_stage` followed by a 2/6/16x inverter buffer chain (4 inversions, non-inverting overall), with a fixed MOS-cap load on the adjust node.
  - p path: PU legs are driven by `b`, PD legs by `a`.
  - n path: PU legs by `a`, PD legs by `b`.

  Stronger PD in the adjust stage gives a higher output duty, and stronger PU gives a lower output duty.
- `dcc_adj_stage`: inverting stage made of a base inverter in parallel with binary-weighted (1/2/4/8/16) `dcc_adj_leg` instances.
- `dcc_adj_leg`: unit leg with a series PMOS switch on the PU side and a series NMOS switch on the PD side, each enabled independently.
- `dcd`: duty-cycle detector. It contains:
  - two `rc_lpf` second-order RC averagers (200k / 0.5p, 200k / 1p);
  - the `dcd_swap` chopper, built from `dcc_tgate` cells;
  - an AND clock gate made of transistors;
  - an `sa_comp` StrongARM comparator with an `nch_lvt` input pair and a NAND SR latch (`dcc_nand2`).
- `dcc_decap`: MOS decap cell (x2 at the top level).
