# LPDDR5-style x8 DQ byte IO: designer's note (verifier only)

`netlist_f.sp` is an `hspiceD`-style export of one top cell, **`LP5_DQ_BYTE`**: the memory-side IO of one LPDDR5-style byte (8 DQ pins, WCK/WCKB, ZQ). It is self-contained, with placeholder `.MODEL` cards and no `.include`. The top cell is a `.SUBCKT` that nothing instantiates.

| Item | Value |
|---|---|
| Subcircuits | 49 (libraries LP5IO_STD 7, TX 9, ODT 3, RX 8, REF 2, CLK 10, CAL 5, ESD 3, TOP 2) |
| Hierarchy depth | 5 levels, for example `LP5_DQ_BYTE / DQ_SLICE / RX_DQ / RX_PHASE / DT_CMP` |
| Cells mixing devices and instances | 12: `TX_PDRV`, `RX_DQ`, `TAP_DAC`, `VREF_R2R`, `CML2CMOS`, `DIV2_IQ`, `DCC_LOOP`, `CLK_TREE`, `ZQ_CAL`, `PAD_IN`, `DQ_SLICE`, `LP5_DQ_BYTE` |
| Flattened MOS | 3973 (NCH 842, NCH_LVT 1572, PCH 424, PCH_LVT 1107, NCH_IO 15, PCH_IO 13) |
| Flattened R / C | 219 / 57 |
| Device lines in the file | 195 X, 220 M, 38 R, 21 C |
| Top pins | 114 |

## Conventions

**Supplies:**
- `VDD` is the core supply, about 0.75 V. It feeds the logic, the clock path, the predrivers and the receiver.
- `VDDQ` is the LVSTL IO supply, about 0.5 V. It feeds the driver pull-ups, the ZQ divider and the VREF ladder.
- `VSS` is the core ground. `VSSQ` is the IO ground, used by the driver pull-downs, ODT, the ZQ replica and ESD.
- Every NMOS bulk is on `VSS`/`VSSQ` and every PMOS bulk on `VDD`/`VDDQ`. A device whose source or drain touches an IO rail has its bulk on the IO rail. For example, the pull-up NMOS has its drain on `VDDQ` and its bulk on `VSSQ`.

**Devices:**
- `NCH`/`PCH` are core devices; `NCH_LVT`/`PCH_LVT` are low-Vt devices for the HS data and clock cells.
- `NCH_IO`/`PCH_IO` are thick-oxide devices, used only in ESD.
- The LVSTL driver, ODT and ZQ replica use thin `NCH`, because VDDQ is about 0.5 V.

**Naming:**
- Cells are uppercase.
- Instances have descriptive names (`X_SER`, `X_PH0`, `X_DQ3`). MOS devices are `M_*`, resistors `R_*`, capacitors `C_*`.
- Buses are `NAME[n]`, MSB first, and every repeated instance is written out individually.
- Leg weights are instance multipliers `M=` on X lines.

**Comments:** only the export header and the `Library name` / `Cell name` / `View name` / `End of subcircuit definition.` lines.

## Top-level pins

| Pin | Class | Function |
|---|---|---|
| `DQ[7:0]` | hs_data_io | Bidirectional data pads. Write data goes in to the CTLE and DFE receiver; read data goes out from the LVSTL driver with de-emphasis. |
| `WCK`, `WCKB` | clock_in | Differential write clock at half the data rate. Its ÷2 gives four quarter-rate phases that clock both Tx and Rx. |
| `ZQ` | reference | Pad to the external RZQ, which goes to VDDQ. |
| `TXD[31:0]` | word_rate_data | Core read data. `TXD[4n+k]` is DQ n, UI k. It is launched on `TXCLK` rising. |
| `RXD[31:0]` | word_rate_data | Receive decisions. `RXD[4n+k]` is DQ n, UI k. The four bits are staggered by one UI and are all stable around `RXCLK` rising. |
| `TXCLK`, `RXCLK` | clock_out | Quarter-rate word clocks: buffered left-spine phase 2 and phase 0. |
| `OE` | important_control | Driver enable. 0 turns all legs off (Hi-Z); 1 also forces ODT off. |
| `EQ_EN` | important_control | De-emphasis (post-cursor segment) enable. |
| `SR[1:0]` | important_control | Main-segment predriver slew code. |
| `ODT_EN`, `ODT_CODE[2:0]` | important_control | Pull-down ODT enable and strength. |
| `VREF_CODE[3:0]` | important_control | Receiver threshold: VDDQ/2 × code/16. |
| `CTLE_CODE[1:0]` | important_control | CTLE peaking. |
| `DFE_TAP[2:0]` | important_control | DFE h1 magnitude α. 0 turns the DFE off. |
| `RX_EN` | important_control | Rx PMOS bias and the VREF ladder. |
| `CAL_EN` | important_control | Rx offset-cal mode. |
| `CAL_DONE` | status_out | Offset calibration finished. |
| `ZQ_CLK` | clock_in | Slow, free-running ZQ clock. |
| `ZQ_START` | command | One-cycle pulse that starts a ZQ calibration. |
| `ZQ_DONE` | status_out | ZQ calibration finished. |
| `ZQ_CODE[4:0]` | status_out | ZQ code readback. The same nets drive the Tx legs. |
| `CK_EN` | important_control | WCK receiver enable. |
| `DCC_EN` | important_control | Duty loop on. When 0, VCTRL is held at its preset. |
| `DCC_RST` | general_control | Forces VCTRL to its preset. |
| `DIV_RST` | general_control | ÷2 I/Q reset. |
| `IBIAS` | bias | Reference current. |
| `VDD`, `VSS`, `VDDQ`, `VSSQ` | power | Supplies and grounds. |

## Block list and signal flow

### Clock: WCK to the quarter-rate phases (`X_CKGEN` = `CLK_GEN`, `X_CKTREE` = `CLK_TREE`)

1. `WCK`/`WCKB` enter through `PAD_IN`: dual-diode ESD plus a 100 Ω secondary series R.
2. `CML_BUF` is a PMOS-input CML stage (the inputs sit at low common mode) with 600 Ω loads to VSS. Its tail is enabled by `CK_EN`.
3. `CML2CMOS` is an NMOS 5T differential-to-single-ended amplifier followed by `INV_D1` and `INV_D4`. Its output is `CKC`.
4. `DCA_CS` is the in-path, current-starved duty adjuster, giving `CKA`.
   - Only the pull-down of its first inverter is starved, by `M_NS` (gate `VCTRL`).
   - `M_NM`, with its gate tied to VDD, keeps a minimum current.
5. `DIV2_IQ` is the ÷2 quadrature generator: two `DLAT_D` latches in a ring.
   - `X_L1` is transparent on CK high and `X_L2` on CK low.
   - The ring inverts in its wiring (`X_L1.D` = `PH[3]`, which is `X_L2.QB`).
   - Outputs: `PH[0]` = I, `PH[1]` = Q, `PH[2]` = IB, `PH[3]` = QB. `PH[k]` is high during 90° steps k and k+1.
6. `CLK_TREE` distributes the four phases.
   - Each phase has a two-inverter root, then one **inverting** `INV_D4` spine driver per side with 30 Ω / 20 fF wire RC.
   - The left spine `PHL` serves DQ0–3; the right spine `PHR` serves DQ4–7.
   - Because the spine drivers invert, `PHL[(k+2)%4]` is driven from `PH[k]`.
7. Spine taps: `PHL[2]` goes to `TXCLK` (two `INV_D4`) and to the cal clock; `PHL[0]` goes to `RXCLK`.

### DCC, analog (`DCC_LOOP` inside `CLK_GEN`)

- `DCC_DET` senses `CKA`, the full-rate CMOS clock, with a phase splitter.
  - The true side is two inverters; the complement side is one inverter plus an always-on TG for delay matching.
  - Each side feeds a 100 kΩ / 1 pF low-pass filter, with 0.5 pF across `VP`/`VN`.
  - VP ≈ D·VDD and VN ≈ (1−D)·VDD, where D is the duty cycle.
- `DCC_OTA` is a 5T Gm stage that integrates onto `C_INT`; that node is `VCTRL`.
  - Its inputs are **crossed**: `VN` goes to INP and `VP` to INN.
  - So a duty above 50 % lowers VCTRL, which slows the DCA rising edge and lowers the duty: negative feedback.
- A TG forces VCTRL to `VPRE` (0.6·VDD, from a resistor divider) when `DCC_RST`=1 or `DCC_EN`=0.
- There is no digital code.
- The DCC corrects the full-rate clock because the ÷2 outputs are 50 % by construction. What depends on the input duty is their I/Q spacing.

### Tx, per DQ (`TX_DQ` = `TX_SER4` → `TX_PDRV` → `TX_DRV`)

**4:1 serializer (`TX_SER4`):**
- The core launches `TXD[3:0]` on `PH[2]`, which is `TXCLK`.
- Bits are captured on staggered phases. `X_FF0` and `X_FF1` both capture on `PH[3]`, `X_FF2` on `PH[0]` and `X_FF3` on `PH[1]`. All four flops are TSPC (`DFF_TSPC`).
- `SER_MUX4` shows bit k in window k = `PH[k]`·`PH[k+3]`.
  - It is built from four 3-high clocked inverters on one node, so it **inverts**.
  - The main mux `X_MUXM` is therefore fed the flops' QB, which makes `DS` non-inverting.

**FFE post-cursor (in `TX_SER4`):**
- A second `SER_MUX4`, `X_MUXP`, is fed the flops' **Q**, rotated by one lane. `D[k]` = bit k−1, and `D[0]` = bit 3 of the previous word, which `X_FF3` still holds.
- Its output `PS` = ~bit(k−1), the "1-UI-delayed inverted data". There is no delay flop: the rotation is the delay.

**Predriver (`TX_PDRV`):**
- Main segment: `PUG_M` = `SLEW_INV`(~DS) = DS and `PDG_M` = `SLEW_INV`(DS) = ~DS.
- `SLEW_INV` has a base leg plus x1/x2 legs enabled by the static `SR[1:0]`/`SRB[1:0]` code.
- Post segment: plain inverters give `PDG_P` = ~PS and `PUG_P` = PS.

**Driver legs (`TX_DRV`):**
- Main: 5 binary `TX_LEG_M` legs, M = 16/8/4/2/1.
- Post: 3 `TX_LEG_P` legs, M = 16/8/4. A post leg is a 1/4-size unit.
- A leg is an NMOS–NMOS LVSTL leg.
  - Pull-up: `VDDQ` → enable NMOS → data NMOS (**source follower, non-inverting from gate to pad**) → 300 Ω → pad.
  - Pull-down: pad → 300 Ω → data NMOS → enable NMOS → `VSSQ`.

**Segment enables (`TX_CTRL`, shared by the byte):**
- `EN_M[4:0]` = `ZQ_CODE` AND `OE`.
- `EN_P[2:0]` = `EN_M[4:2]` AND `EQ_EN`.
- They gate the stacked enable devices of the legs. The predriver itself has no enable.

### ODT, per DQ (`ODT_PD`, decode `ODT_CTRL`)

- Pull-down only, to VSSQ: 3 `ODT_LEG` legs (600 Ω + NMOS), M = 4/2/1.
- `ODT_G[k]` = `ODT_CODE[k]` AND `ODT_EN` AND NOT `OE`.

### Pad, per DQ (`DQ_SLICE`)

- `ESD_DIO2`: gate-tied PCH_IO to VDDQ and NCH_IO to VSSQ.
- `C_PAD`.
- ODT and the Tx legs connect on the pad node, ahead of the 150 Ω secondary R `R_SEC`.
- The receiver connects after `R_SEC`, on `PADR`.

### Rx, per DQ (`RX_DQ`)

**Cal input mux:**
- `M_ISO` is a series NMOS from `PADR` to `RXIN`, on when `CAL_ENB`=1.
- `M_CSN`/`M_CSP` form a TG from `RXIN` to `VREF`, on in cal mode.

**VREF (`VREF_R2R`, shared):**
- A 4-bit voltage-mode R-2R ladder.
- `VTOP` = VDDQ/2 comes from a divider enabled by `RX_EN`.
- Each bit has an NMOS-only SPDT switch (VTOP or VSSQ) into its 2R leg.
- The output impedance is 1 kΩ at every code, with 2 pF of decoupling. VREF is distributed unbuffered.

**CTLE (`CTLE_SC`):**
- Pseudo-differential PMOS pair: `RXIN` against `VREF`.
- Two PMOS tails (`VBP`), 1.5 kΩ loads to VSS, and 800 Ω degeneration.
- A 2-bit statically switched series-cap bank sits across the sources (`CTLE_CODE`).
- `OUTP` is the drain of the VREF-side device.

**Loop-unrolled 1-tap DFE, 4 phases (`X_PH0..3` = `RX_PHASE`):**
- Phase k is clocked by `PH[k]`, with `CKB` = `PH[k+2]`.
- Each phase holds two `DT_CMP` double-tail comparators.
  - `X_CMPH` decides x > +α.
  - `X_CMPL` is the same cell with INP/INN, OUTP/OUTN and VTRN/VTRP all cross-wired, so its α device becomes −α.
- A `DFE_MUXLAT` picks H when the previous phase's decision is 1. It is a mux merged into a ratioed SR latch.
- Phase k's select is `RXD[k−1]`, and phase 0 uses `RXD[3]`.

**DFE α (`TAP_DAC`, shared):**
- A 3-bit PMOS current DAC into the NMOS diode `VALF`, which biases `M_AL` on each comparator's FP node.
- It is forced off when `CAL_ENB`=0.

**Offset calibration (per DQ):**
- In cal mode the CTLE input is shorted to VREF, the pad is isolated and α = 0.
- The phase-0 decision drives the counter: `DB0` → UP and `RXD[0]` → UPB of `RX_CAL_CNT`, a 3-bit saturating up/down counter.
- The counter feeds `RX_TRIM_DAC`. This 3-bit steering DAC makes `VTRN` ∝ code and `VTRP` ∝ 7−code, which bias `M_TN`/`M_TP` in all 8 comparators.

**Cal sequencing (`CAL_CTRL`, shared):**
- `PHL[2]` ÷4 gives `CAL_CK`, so the counters run synchronously with the decisions. A further ÷2 clocks a 5-stage shift-register timer of `CAL_EN`.
- `CAL_DONE` = S4·`CAL_EN`, about 9–10 `CAL_CK` edges after `CAL_EN`.
- `CAL_RUN` = `CAL_EN`·NOT `CAL_DONE` enables the counters.

**Bias (`BIAS_GEN`):** from `IBIAS` it makes:
- `VBP_B`, always on: CML buffer and ZQ comparator.
- `VBN`: CML2CMOS and DCC OTA.
- `VBP_A`, gated by `RX_EN`: CTLE, trim DACs and tap DAC.

### ZQ (`ZQ_CAL`)

- A VDDQ/2 divider, enabled by BUSY, gives `ZREF`.
- `ZQ_CMP` is a continuous-time two-stage comparator with a PMOS input pair. It compares the ZQ pad against `ZREF`. Its output `OUTB` is active-low "keep".
- `ZQ_SAR5`, a 5-bit SAR, works MSB first.
  - A one-hot token register is started by `ZQ_START`.
  - Each bit has a hold/decide TG mux, cleared synchronously by START.
  - CODE = C OR T. DONE is sticky, and BUSY = NOT DONE.
- 5 binary `ZQ_RLEG` replica pull-down legs (M = 16..1) sit on the pad. Each is a 1/6-scale copy of the `TX_LEG_M` pull-down half: R, then an "ON" NMOS gated by BUSY, then an enable NMOS gated by the code.
- A bit is kept while ZQ > VDDQ/2, meaning the pull-down is still too weak.
- `ZQ_CODE[4:0]` drives `TX_CTRL` (all main legs, and the post legs from bits 4:2) and is also a readback port.
- One code serves both pull-up and pull-down legs.

### ESD

- `ESD_DIO2` primary dual diodes on every pad: DQ, WCK, WCKB and ZQ.
- `ESD_CLAMP` RC-triggered rail clamps, one on VDDQ/VSSQ and one on VDD/VSS: 200 kΩ / 2 pF RC → inverter → 50 µm × 40 NMOS.
- Secondary series R: `R_SEC` 150 Ω in `DQ_SLICE` and 100 Ω in `PAD_IN`.
- Top-level decaps: `M_DCAP`, an NMOS, and `C_DCQ`.

## Timing summary (quarter-rate cycle = 4 UI, 90° per UI)

- **Tx launch and capture:**
  - The core launches TXD on `PH[2]`.
  - Captures: bit 0 and bit 1 on `PH[3]` (270°), bit 2 on `PH[0]` (360°), bit 3 on `PH[1]` (450°). Each is at least 90° inside the core window.
- **Tx mux windows:** bit k is shown at [360+90k, 450+90k].
- **Post lane hold:** the post lane's hold margin at the end of each window is one flop clock-to-Q. This is accepted: the window closes on the same edge that updates the flop.
- **Rx decisions:**
  - Phase k evaluates on `PH[k]` rising.
  - The phase-k decision must settle within one UI, because phase k+1 needs it as its select. This is the critical DFE loop timing.
- **RXD alignment:**
  - `RXD[k]` is valid from about 90k°+t to 90k°+360°+t.
  - All four bits are valid together in [270°+t, 360°+t]. `RXCLK` (phase 0) falls in that window when t is about 45°.

## Feedback loops

1. **DCC:** `CKA` → `DCC_DET` → `DCC_OTA` / `C_INT` (`VCTRL`) → `DCA_CS` → `CKA`. This is analog, continuous and negative, closed through the crossed OTA inputs.
2. **÷2 ring:** `X_L1` → `X_L2` → `X_L1`, with an inversion in the ring wiring.
3. **ZQ SAR:** CODE → replica legs → ZQ pad → `ZQ_CMP` → `ZQ_SAR5` → CODE. It is clocked by `ZQ_CLK`. The code path to the Tx legs is open loop at run time.
4. **DFE decision loop, per DQ:** `RXD[3]` → phase-0 select → `RXD[0]` → phase-1 select → … → `RXD[3]`. One phase per UI.
5. **Rx offset-cal loop, per DQ:** phase-0 decision → `RX_CAL_CNT` (UP = decision complement) → `RX_TRIM_DAC` → `M_TN`/`M_TP` in the comparators → decisions. It is active only while `CAL_RUN`=1.
6. **Local state:** the `DFE_MUXLAT` keepers, the `DLAT_D` keepers, and the comparator latches. In `CAL_CTRL`, `X_DV0..X_DV2` are T flops with D tied to their own QB.

## Intentional asymmetries

- **Tx capture phases** are uneven: bits 0 and 1 share `PH[3]`, then `PH[0]` and `PH[1]`. The post lane is the main lane rotated by one, and its D[0] is the previous word's bit 3.
- **Post segment:**
  - It has only 3 legs, on ZQ bits [4:2]. Its unit is 1/4 of the main unit, so the post/main strength ratio is about 7/31.
  - Its predriver has no slew control.
  - Total drive strength changes with `EQ_EN` (not compensated).
- **ZQ:** only a pull-down replica exists; the pull-up NMOS legs reuse the pull-down code. The replica is a 1/6-scale leg, so the drive is RZQ/6.
- **Offset cal:** only phase 0 is observed (its decision drives the counter), and all 8 comparators of a DQ share one trim code. The L comparators get the trim biases swapped so the correction has the same physical sign.
- **Clock taps:** DQ0–3 sit on the left spine, DQ4–7 on the right. `TXCLK`, `RXCLK` and the cal clock all tap the left spine (phases 2, 0 and 2).
- **DCC sensing:** it senses only the full-rate CMOS clock `CKA` (one phase plus a locally generated complement), not the four divided phases.
- **ODT** is pull-down only and is forced off by `OE`.

## Unused outputs, ties and intended single-connection nets

- `CAL_CTRL`: QB of `X_S0..X_S4` (nets `S0B..S4B`) is unused. The timer uses only Q.
- `ZQ_SAR5`: Q of `X_C4..X_C0` (nets `C4..C0`) is unused, because CODE and the hold mux use QB (`CB`). QB of `X_FD` (`DONEB`) is unused.
- The checker allows exactly these 11 per-cell nets. After flattening there are 0 single-connection nets and 0 gate-only (undriven) nets.
- Gates tied to rails, all on purpose:
  - `DCA_CS.M_NM`: gate at VDD, the minimum-current device.
  - `DCC_DET.M_GN`/`M_GP`: gates at VDD/VSS, an always-on delay-matching TG.
  - `ESD_DIO2`: gate-tied diodes.
  - Top `M_DCAP`: an NMOS decap.

## Look-alike traps

1. **Loop-unrolled DFE (`RX_PHASE`).** It looks like two samplers per phase (data plus edge, or a double sampler) followed by a serializer mux. Really, H and L are speculative comparators with thresholds ±α, and `DFE_MUXLAT` picks one using the previous phase's decision. `SEL`/`SELB` are data, not static controls.
2. **`X_CMPL` is not an inverted or complementary sampler.** It is the same `DT_CMP` with INP/INN, OUTP/OUTN and VTRN/VTRP cross-wired. Its single α device (on the cell's FP) therefore gives −α.
3. **`DFE_MUXLAT` is a 2:1 mux plus an SR latch in one ratioed cell.** Its set and reset AND-OR pull-down networks resemble a 4-input complex gate or a NAND-based SR latch.
4. **NMOS pull-up from VDDQ (`TX_LEG_M/P.M_PU`).** It is a source follower, non-inverting from gate to pad. So the PU gate carries true data (`PUG_M` = DS). It is not an inverting stage or an open-drain pull-down.
5. **Stacked `M_PUE`/`M_PDE` in the legs** look like the second input of a NAND/NOR stack. They are static strength and OE enables (`EN_M`/`EN_P`).
6. **ODT legs** (NMOS + R to VSSQ) look like a driver pull-down segment. They are static termination, with gates from `ODT_CTRL`.
7. **ZQ replica legs (`ZQ_RLEG`)** have the same topology as the driver pull-down. The "data" gate is BUSY and the enable gate is the code.
8. **`SER_MUX4`** (four 3-high clocked-inverter stacks on one node) looks like a 4-input NAND/NOR or a tri-state bus. It is a 4:1 phase-window mux, and it inverts.
9. **`X_MUXP`** looks like a duplicate or redundant serializer, for example for a strobe. It is the FFE post-cursor lane: the same flops' Q rotated by one bit, which gives 1-UI-delayed inverted data.
10. **`CLK_TREE`** looks like a matched buffer tree with straight indices. The spine drivers invert, so output index (k+2)%4 is driven from root k. Logically `PHL[j]` = `PH[j]`.
11. **`DIV2_IQ`**: two latches on complementary clocks look like a master-slave DFF. The ring inverts and both latch outputs are used, so it is a ÷2 Johnson I/Q generator.
12. **`DCA_CS`** looks like a VCDL or current-starved delay cell. Only one edge is starved, so it adjusts duty. `M_NM` (gate tied to VDD) is a minimum-current device, not a switch.
13. **`DCC_DET`**: the TG with gates on VDD/VSS is a delay-matching element. The RC filters sense duty and are not in series with the clock.
14. **`DCC_OTA` + `C_INT`** look like a buffer, regulator or comparator. They are a Gm-C integrator with crossed inputs; the output `VCTRL` is analog.
15. **`CML2CMOS`**: the 5T stage looks like a bias OTA but sits in series with the clock.
16. **`CTLE_SC`**: the "switched-capacitor" degeneration is a static code selecting caps (not clocked). `OUTP` is the drain of the VREF-side device.
17. **`RX_TRIM_DAC`** looks like a bias generator or current mirror. It is the offset-cal DAC. Its outputs feed small injection devices (`M_TN`/`M_TP`), and `TAP_DAC` feeds `M_AL`, inside each comparator; these look like extra input-pair devices.
18. **`VREF_R2R`**: each `M_H`/`M_L` pair looks like an NMOS-only inverter. It is an analog SPDT switch into a 2R leg.
19. **The cal input mux (`M_ISO` series NMOS plus the TG to VREF)** looks like ESD or a pass gate in the data path. `M_ISO` belongs to the cal mux.
20. **`RX_CAL_CNT`**: the TG muxes compute XNOR (`PJ` = C ? UP : UPB) and XOR (`DN` = C ? GB : G). The flop outputs are the selects, not the data. The counter's UP pin is the decision **complement** `DB0`.
21. **`ZQ_SAR5`**: the NAND2 on the two QBs is an OR (CODE = C | T). The comparator output is active-low (`KEEPB`).
22. **`CAL_CTRL`**: the 5-stage shift register is a timer for `CAL_DONE`, not a deserializer or delay line. The three T flops form a ripple divider.
23. **`BIAS_GEN.M_OFF`** is a PMOS from VDD onto `VBP_A`. It is the Rx power-down (sources off), not a startup device.

## Design limits and assumptions

- The TSPC flops are dynamic.
  - `ZQ_CLK` must be free-running so the SAR hold muxes refresh the code.
  - The Rx trim codes are refreshed by `CAL_CK`, which runs whenever WCK runs. After WCK has been stopped, rerun the offset calibration.
- The ZQ code drives the Tx legs live, including trial codes during calibration. So `ZQ_START` must be issued while the bus is idle.
- The ZQ code is undefined until the first `ZQ_START`. The offset-cal counters have no reset: a calibration resumes from the previous trim, and the window of about 9–10 `CAL_CK` edges covers the full 0..7 range.

## Checks (`scripts/`, run `run_all.sh`)

- `gen_netlist.py` writes the netlist from `gen_lib.py` and `cells_*.py`. `build_key.py` writes the key from `key_part1..3.py`.
- `check_netlist.py` covers:
  - parse, a single top, and define-before-use;
  - every subckt instantiated (except the top) and pin counts on all 195 instances;
  - models and W/L, and that every pin is used;
  - per-cell unused outputs against the intended list above;
  - flattened floating and gate-only nets;
  - bulk and rail rules;
  - statistics.
- `check_logic.py` holds 2132 switch-level checks of every digital cell:
  - gates, TG mux, TSPC flop, the 4:1 window mux, slew inverter and predriver;
  - `TX_CTRL`/`ODT_CTRL` (exhaustive), the serializer main and post lanes, and `TX_DQ` pad levels (full, main-dominant, weak, equal-strength de-emphasis, Hi-Z);
  - the double-tail comparator with rail inputs, `RX_PHASE`, `DFE_MUXLAT`, `DLAT_D` and the `DIV2_IQ` I/Q sequence;
  - `DCA_CS`, the `DCC_DET`/`DCC_LOOP` logic, `CLK_TREE` rotation and the `TAP_DAC`/`VREF_R2R` decode;
  - `RX_CAL_CNT` up/down/saturate/hold, plus an offset-cal loop against a behavioural comparator;
  - the `CAL_CTRL` ÷4 and timer;
  - `ZQ_SAR5` for all 32 targets, and `ZQ_CAL` gating;
  - a loop-unrolled DFE harness against a behavioural ±α comparator (0 errors with the DFE; errors with a fixed threshold).
- `check_top.py` holds 637 top-level switch-level checks. The analog front ends are bypassed by forcing nets.
  - All 8 DQ pads serialize `TXD` correctly through the rotating tree.
  - All 32 `RXD` bits capture the forced CTLE outputs.
  - `TXCLK`, `RXCLK` and the cal-clock phases are correct.
  - The strength codes reach the legs, ODT is interlocked with OE, the pads are terminated with OE=0, and `CAL_EN` gates the tap DAC.
- `check_key.py` is the answer-key consistency check.
- Not switch-level checked (analog): `CML_BUF`, `CML2CMOS` (5T), `CTLE_SC`, `DCC_OTA`, `ZQ_CMP`, `BIAS_GEN`, `RX_TRIM_DAC`, the ESD cells and the leg resistors. Their wiring and polarity are covered by the key and by the top-level check.
