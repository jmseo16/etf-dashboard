# Designer intent notes

All three netlists are HSPICE (hspiceD-style) schematic exports. The top cell of each one is a `.subckt` that nothing else instantiates. Device models (`nch`, `pch`, `nch_lvt`, `pch_lvt`, `nch_18`, `pch_18`) come from the PDK and are not included. Every subcircuit is defined in its own file. Bus pins are written MSB first.

---

## 1. bist.sp: HSIO loopback BIST

**Top cell:** `hsio_bist_top`

**Supplies:** `vdd` = 0.9 V core (logic, clocks, samplers); `vddq` = 1.0 V (CML serializer output, TX driver, loopback mux, CTLE); `vss`.

**High-speed data**
- Out: `txp` / `txn`. These are the CML TX pads (50 Ohm back-terminated to vddq). The PRBS pattern leaves the chip here.
- In: `rxp` / `rxn`. These are the external RX pads (2x50 Ohm termination to a self-biased CM node of 0.7*vddq). The loopback mux selects them when `lpbk_en`=0.
- Internal loopback: the TX pads `txp/txn` are tapped through 200 Ohm series resistors into the second input of the loopback mux.

**Clock inputs:** `ckp` / `ckn` is the 4 GHz half-rate differential clock (8 Gb/s, DDR). From it the chip derives: ck/ckb (serializer final mux), wclk/wclkb = ck/2 (TX word clock, 4 bits/word), rck/rckb (RX sampling clock = ck through the delay trim), and rwclk/rwclkb = rck/2 (RX word clock).

**Control**
- `cfg<8:0>` + `cfg_wr` (rising edge writes) feed the mode register:
  - `cfg<8>` prbs_sel: 0 = PRBS7 (x^7+x^6+1), 1 = PRBS15 (x^15+x^14+1), for both the generator and the checker.
  - `cfg<7>` lpbk_en: 1 = internal TX→RX loopback, 0 = external rxp/rxn.
  - `cfg<6>` tx_en: enables the TX CML driver tail, and the generator runs only when it is set.
  - `cfg<5>` rx_en: CTLE tail enable.
  - `cfg<4>` chk_en: checker run enable.
  - `cfg<3>` err_inj: a 0→1 write injects a single bit error, by inverting tx_d<0> for one word.
  - `cfg<2:0>` rdly<2:0>: binary-weighted switched-cap delay trim of the RX sampling clock (rck/rckb) relative to the TX clock. This sets the sampling phase in loopback.
- `bist_start`, `bist_stop`: asynchronous level/edge requests, synchronized to wclk. Start sets RUN and clears the error counter and lock detector (clr_b pulse). Stop clears RUN and sets DONE.
- `rstb`: global active-low asynchronous reset. It also seeds the LFSR with 0...01.
- `bist_en`: bias enable.

**Bias:** `ibias` is a 100 uA reference current into the diode in `bist_bias`. It produces `vbn` for all CML tails: ser mux 1.6 mA, TX driver 8 mA, loopback mux 1.6 mA, CTLE 2x1.2 mA.

**Status outputs (slow / test):** `err_cnt<9:0>` (number of errored 4-bit words after lock), `err_ovf` (sticky counter overflow), `bist_lock` (15 consecutive clean words), `bist_err` (registered per-word error flag), `bist_busy`, `bist_done`.

**Blocks**

| block (cell) | function | HS path? |
|---|---|---|
| `bist_bias` | ibias diode, RC filter, power-down → vbn | no (bias) |
| `bist_clkgen` (`ck_rx_acbuf`, `inv_x4`, `dffr_x1` div2, `rxck_dly`/`dly_cell`) | AC-coupled self-biased clock RX, buffers, /2 word clock, RX clock delay trim | clock path |
| `mode_reg` | 9b parallel-load config register | no |
| `bist_ctrl` | start/stop/err_inj synchronizers, RUN/DONE flops, gen_run/chk_run/inj_p/clr_b | no |
| `prbs_gen` (`icg_x1`, 15 state flops, `prbs_pred4`) | 4-bit-per-word parallel PRBS7/15 LFSR, clock gated by gen_run, bit-0 error-inject XOR | no (digital word-rate source) |
| `bist_tx_hs` → `ser4to1` (dff retime, dlat alignment latches, `mux2_x1` 4:2 at wclk, ck latches, `ser_mux2_cml` 2:1 at ck) → `tx_cml_drv` | 4:1 serializer and CML line driver; bit order d<0> first | **yes** |
| `lpbk_mux` | RX termination, loopback tap, CML 2:1 select (lpbk_en) | **yes** |
| `bist_rx_hs` → `rx_ctle` → 2x `rx_sampler` (`sa_strongarm` + `sr_latch_nand`) → `rx_deser` | CTLE, even (rck) / odd (rckb) StrongARM samplers, 2→4 deserializer, rwclk generation | **yes** (deser output is word-rate) |
| `prbs_chk` (15-bit history, `prbs_pred4`, 4 XOR compare, OR4, err flop, sync2 of chk_run) | self-synchronizing checker → bist_err | no |
| `lock_det4` | 4b saturating clean-word counter → bist_lock | no |
| `err_cnt10` | 10b ripple counter of error words (gated by lock & run & !ovf) + sticky overflow | no |

---

## 2. zqcal.sp: ZQ calibration

**Top cell:** `zqcal_top`

**Supplies:** `vdd` = 0.8 V core logic and comparator latch; `vddq` = 1.1 V IO (replica legs, level shifters, VREF ladder, preamp; thick-oxide nch_18/pch_18); `vss`.

**There are no high-speed data inputs or outputs.** This is a slow mixed-signal calibration loop. Analog nodes:
- `zq`: the ZQ pad. An external RZQ = 240 Ohm to VSS sits off-chip. The pull-up replica array drives the pad, and the comparator senses it through a 1 kOhm isolation resistor (zq_s).
- Internal `npd`: the pull-down calibration node, made of the replica PU array (calibrated PU code) over the PD replica array.
- Internal `vref`: VDDQ/2 (trim selectable).

**Clock:** `zq_clk` (about 200 MHz) is the FSM/prescaler clock. Derived clocks: step_clk = zq_clk/8 (sequencer and SAR registers); cmp_clk = the 8th zq_clk period of each step, while busy (comparator strobe).

**Control inputs**
- `zq_start`: calibration start command (synchronized, edge-detected, ignored while busy).
- `zq_latch`: transfers the SAR results to the DQ driver code registers. It takes effect only when `zq_done`=1.
- `rstb`: async reset. The output codes reset to mid-scale 100000 (bit 5 uses a set flop).
- `vref_trim<1:0>`: VREF ladder tap. 00 = 15/32, 01 = 16/32 (nominal VDDQ/2), 10 = 17/32, 11 = 18/32 of VDDQ.

**Bias:** `ibias_zq` is a 10 uA reference current into the diode in `zq_bias`. It produces the tail bias for the comparator preamp.

**Code outputs (to the DQ drivers):** `pu_code<5:0>` and `pd_code<5:0>` are binary codes; 1 enables a leg. The leg weights are 32/16/8/4/2/1 units on top of an always-on 32-unit base leg. One unit is about 15.4 kOhm, so code 32 gives about 240 Ohm.

**Status:** `zq_busy`, `zq_done`, and `zq_cmp_mon` (comparator decision, test monitor; it also feeds both SARs).

**Algorithm:** the sequence is w0, w1 (analog settle), tu<5..0> (PU SAR), td<5..0> (PD SAR), done. The PU SAR sets trial bit k when the token is on bit k+1. When the token is on bit k, it keeps the bit if cmp=1. The PU phase compares vref against zq (cmp=1 means V(zq) < vref, so the PU is still too weak). The PD phase swaps the comparator inputs through `zq_inmux` and compares npd against vref (cmp=1 means V(npd) > vref, so the PD is still too weak). The decision polarity is therefore the same in both phases. en_pu powers the pad PU array during w0..tu0. en_pd powers the replica PU+PD branch during td5..td0.

**Blocks**

| block | function |
|---|---|
| `zq_fsm` | /8 ripple prescaler, start sync+edge, busy/done, 15-stage one-hot sequencer, en_pu/en_pd decode, cmp_clk |
| `zq_sar6` ×2 (`zq_sar_bit` = mux2 + or2 + dffr) | 6b SAR registers pu_b<5:0> and pd_b<5:0> |
| `zq_code_reg` | DQ driver code registers (pu_code, pd_code), loaded by zq_latch & zq_done |
| `zq_pu_cal_path` (`zq_predrv` → `zq_pu_array` → `zq_pu_unit`, `zq_pad_esd`) | pad pull-up replica, code-gated level-shifted gates, ESD, sense tap |
| `zq_pd_cal_path` (2x `zq_predrv`, `zq_pu_array`, `zq_pd_array`) | pull-down calibration divider, node npd |
| `zq_vref_gen` (`zq_ls`, `zq_vref_ladder`, `zq_vref_mux`, RC filter) | VDDQ/2 reference with 2b trim, power-gated |
| `zq_cmp_top` (`zq_bias`, `zq_inmux`, `zq_cmp` = `zq_preamp` + `zq_sa_latch` + `sr_latch_nand`) | phase-swapped comparator |

No block is on a high-speed data path. The analog decision path is zq/npd/vref → inmux → preamp → latch → cmp_q → SAR.

---

## 3. dqs_rx.sp: DQS/DQ byte receive path

**Top cell:** `dqs_dq_rx_top`

**Supplies:** `vddq` = 1.1 V (pads/ESD, DQS amp, DQ preamps, VREFDQ ladder/buffer, bias mirror; thick-oxide nch_18/pch_18); `vdd` = 0.8 V core (DQS C2C, WDCA, repeater tree, local clock buffers, VGAs, samplers, decoders); `vss`.

**High-speed data in:** `dq<7:0>`. These are single-ended POD-style DQ inputs, each compared with VREFDQ.
**High-speed data out:** `dq_r<7:0>` (data sampled on the DQS_t rising edge, the even bits) and `dq_f<7:0>` (data sampled on the DQS_c rising edge, i.e. the DQS_t falling edge, the odd bits). Each one is held by an SR latch for a full strobe cycle.
**Strobe in:** `dqs_t` / `dqs_c` (differential DQS/DQSB).

**Control codes and enables**
- `wdca<3:0>`: write duty-cycle adjust, built into the DQS buffer. `wdca<3>` is the sign: 1 widens the DQS_t high phase and 0 narrows it. `wdca<2:0>` is the magnitude, a binary-weighted 1/2/4 skew-leg strength. On the t rail, sign=1 enables extra pull-up legs; on the c rail it enables extra pull-down legs. Sign=0 does the reverse. `wdca_en`=0 forces no adjustment.
- `vga_gain<2:0>`: shared by all 8 bits. Each bit switches a degeneration resistor in parallel (bit0: 4k, bit1: 2k, bit2: 1k, over a 4k base). More resistance switched in lowers Rdeg and raises the gain (about 0.6x to 1.6x).
- `vref_code<3:0>`: VREFDQ = (40+code)/64 × VDDQ, i.e. 0.625 to 0.859 VDDQ in 1.56 % steps.
- `vref_en`: VREFDQ ladder header (via level shifter) and buffer enable.
- `rx_en`: bias generator, DQ preamp/VGA tails, and the per-bit local DQS clock gating. When it is 0, all sampler clocks are held low (precharge).
- `dqs_en`: DQS amp and C2C tail enable.

**Bias:** `ibias` is a 50 uA reference current into `rx_bias`. It produces vbn_c (nch_lvt tails: VGA, C2C) and vbn_q (nch_18 tails: DQ preamp, DQS amp, VREF buffer).

**Strobe path (unmatched):** dqs_t/dqs_c → `rx_esd` → `dqs_amp` → `dqs_c2c` (inverting) → `wdca_stage` (inverting, duty skew) → dqs_t_i/dqs_c_i → `dqs_clk_tree`. The tree has a trunk `rpt_stage`. The left branch (2 RPT plus RC wire) feeds the spine for DQ3, DQ2, DQ1, DQ0. The right branch (2 RPT plus RC wire) feeds the spine for DQ4, DQ5, DQ6, DQ7. Each bit has its own `dqs_lcb` (non-inverting, gated by rx_en), which drives dqs_t_b<k>/dqs_c_b<k>. No delay matching to DQ is applied; the RC spine gives each bit a different strobe arrival time.

**Data path, per bit (`dq_rx_bit`):** dq → `rx_esd` → `dq_preamp` (vs RC-filtered vref_buf) → `dq_vga` → two `dq_sampler` (`dq_sa` StrongARM + `sr_latch_nand` + driver). One is clocked by dqs_t_b and produces dq_r; the other is clocked by dqs_c_b and produces dq_f.

**Blocks not on the high-speed path:** `rx_bias`; `vrefdq_gen` (`ls_vdd2vddq`, `vref_ladder16`, `vref_dec4to16`/`pdec2to4`, `vref_sw16`, `vref_ota_buf`); `wdca_dec` (static code decoder, though it controls a block that is on the strobe path); the enable gating inside `dqs_lcb` (static).
