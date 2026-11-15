# netlist_g.sp: designer's note (for the verifier only)

Top cell `fcl_link_top`, a forwarded-clock serial-link IO. There are 55 subckts, the hierarchy is 6 levels deep, and the flattened netlist has 3992 MOS (sum of m = 4687), 74 R and 20 C. The top has 111 pins.

## 1. Domains and conventions

| Domain | Rails | How they reach the cells |
|---|---|---|
| Core digital | `vddd` / `vssd` | `.global`, never a pin. All FCL_STD cells and the digital blocks use these nets directly, and so do the output stage of `fca_c2c`, the local clock inverters of `fca_pfd` and the level-down inverter in `fcs_inrx`. |
| Analog / CML | `avdd` / `avss` | Pins on every analog cell: CML, DLL delay line, charge pump, PI core, Tx driver, RO, ESD. |
| Slow pad IO | `vddq` / `vssq` | Pins. Thick-oxide devices (`nch_hv`/`pch_hv`) only. |

- Device sizes:
  - Global `.param` values (`wn1`, `wp1`, `lmin`, `lcs`, `wcml`, `wtail` …) and quoted expressions (`W='2*wn1'`).
  - A subckt default parameter `rl=` on the CML cells, overridden per instance (`rl=450` on the clock receiver, `rl=420` on the PI).
  - `m=` on devices and on instances (DAC legs m=1/2/4/8, clock drivers m=2, phase drivers m=2).
- Names:
  - Instances are `X<n>` and iterated instances `X<n>[i]`.
  - Devices are `MN<n>`/`MP<n>`/`R<n>`/`C<n>`.
  - Buses use `[i]`.
- Phases are named by phase angle: `ph[k]` = k × 45°.
- The only comments are the netlister header and the per-cell banners.

## 2. Block list

```
fcl_link_top
 ├ X0  fca_bias        ibias mirror -> vbn_rx, vbn_tx, ib_cp; vcm = 0.75 avdd divider
 ├ X1  fca_fwd         forwarded-clock lane
 │      ├ fca_trm, fca_cmla (rl=450), 2x fca_c2c (true / swapped inputs = complement)
 │      ├ fca_dll
 │      │   ├ fca_dline: 4x fca_dcell + 1 dummy fca_dcell (VCDL, 8 phases)
 │      │   ├ fca_pfd   (2x fcd_dffr, D=vddd, NAND/NOR reset with delay)
 │      │   ├ fca_isw   (charge pump with own bias mirror)
 │      │   ├ fca_lpf   (4k + 20p, 1.5p)
 │      │   └ devices: vctl->vcp converter MN0/MP0, reset PMOS MP1, MOS decap MN1
 │      └ fca_phd       8 inverting drivers, index rotated by 4
 ├ X2[3:0] fcr_lane    data lanes
 │      ├ fca_trm, fca_cmla
 │      ├ fcr_smp       data fca_clff (ckp) + edge fca_clff (ckn) + 2x fca_c2c
 │      ├ fcr_phmix     fcr_phsel (two 8:1 TG trees) + fca_mix2w (PI core)
 │      ├ fca_c2c       PI clock -> CMOS clock for the digital
 │      └ fcr_dig       fcd_ckbuf, fcr_bbx (Alexander PD), fcr_vote, fcr_dsr8, fcr_jdiv8, fcr_acc (5x fcr_ube/fcr_ubo)
 ├ X3  fcx_lane        fcd_ckbuf, fcr_jdiv8, fcx_ser8, fcx_ffe, fcx_drv (9x fca_tleg)
 ├ X4  fct_mon         fct_cs5 (ring of NAND + 4x fct_csi), fcd_ckbuf, fct_rip3 (/8), gate, 2x fct_rip3 (6-bit count)
 ├ X5  fcs_pads        5x fcs_inrx (fce_hv + R + Schmitt + level-down), fcs_creg (4x fcd_dffr)
 ├ X6..X11 fce_lv      ESD on fck_p/n, rx_p/n[3:0], tx_p/n
 └ X12..X14            rail clamps: fce_clmp (avdd/avss), fce_clmp (vddd/vssd), fce_clmphv (vddq/vssq)
```

The deepest path is `fcl_link_top/X2[i]/X5 (fcr_dig)/X5 (fcr_acc)/X5 (fcr_ube)/X0 (fcd_dffr)`.

Ten cells mix devices with instances: `fca_c2c`, `fca_dll`, `fca_pfd`, `fcl_link_top`, `fcr_jdiv8`, `fcr_ube`, `fcr_ubo`, `fcs_inrx`, `fct_cs5`, `fcx_drv`.

## 3. Signal flow

**Forwarded clock**
1. `fck_p/n` arrives with 100 Ω termination to `vcm` and goes through the CML receiver (`fa_p/n`).
2. Two `fca_c2c` make CMOS `ckp` and `ckn`. The second has its inputs swapped.
3. The DLL delay line has four non-inverting differential stages of 45° each. Stage k gives `ph[k]` (true) and `ph[k+4]` (complement): stage 1 gives `ph1`/`ph5`, …, stage 4 gives `ph4`/`ph0`.
4. The PFD compares `ref = ckp` with `fb = ph[0]`. At lock, 4 × delay = T/2, so `ph[0]` = `ckn` delayed by T/2, which lines up with `ckp`.
5. `fca_phd` inverts each phase into `pho[(k+4) mod 8]`, which preserves the phase names.
6. The top net `ph[7:0]` goes to all four lanes, and `ph[0]` also goes to the Tx.

**Data lane** (full-rate; one forwarded-clock period = one UI)
1. `rx_p/n` arrives with termination and goes through `fca_cmla` (`la_p/n`).
2. `fcr_smp` samples twice per UI:
   - The data sampler (CML master-slave) samples at `pck_p` rising.
   - The edge sampler is the same cell with its clocks swapped, so it samples at `pck_n` rising, half a UI later.
   - Each sample is converted to CMOS as `dsam`/`esam`.
3. The PI clock `pck_p/n` comes from `fcr_phmix`:
   - `code[4:2] = k` selects `a = ph[k]` and `b = ph[k+1]`.
   - `code[1:0] = w` sets the tails: A carries 4 − w units and B carries w units.
   - The output phase is (k + w/4) × 45°, in 32 steps over 360°.
4. `fca_c2c` turns `pck` into the CMOS `ck`. `fcd_ckbuf` makes `cka`/`ckab` from it.
5. `fcr_bbx` (Alexander PD):
   - On ck falling, `s0 = D[k]` and `s1 = D[k-1]`.
   - The edge sample is retimed on ck rising (`e0`) and then on ck falling (`e1` = E between D[k-1] and D[k]).
   - `up = e1 ^ s0`: the edge sample equals the earlier bit, so the clock is early and the phase code increases.
   - `dn = s1 ^ e1`: the edge sample equals the later bit, so the clock is late.
6. `fcr_vote` shifts `up`/`dn` on ck falling and outputs `vub`/`vdb`, the active-low majority of the last three decisions.
7. `fcr_acc` is clocked by `wck` rising:
   - It counts up when only up wins, counts down when only dn wins, and holds when both or neither win or when `hold = cmd_q[1]`.
   - The count wraps mod 32.
   - `code` drives the PI. This closes the CDR loop, and the code is read back on `rx_pic`.
8. The deserializer, `fcr_dsr8`:
   - The shift register is `s0`, `s1` (inside the PD) followed by `sr[7:2]`, all on ck falling.
   - `fcr_jdiv8` runs on ck rising. It makes `wck` (÷8, 50 % duty) and `ld = q0 & ~q1`, a one-UI pulse.
   - `ld` opens 8 latches. The latches pass one shift edge and close half a UI later.
   - In `rxd[8n+7:8n]`, the oldest bit is `rxd[8n]`.

**Tx**
1. `ph[0]` goes through `fcd_ckbuf` to `fcr_jdiv8`, which makes `ld` and `tx_wck`.
2. `fcx_ser8` is a shift-load register. `ld = 1` loads `txd[7:0]`; otherwise it shifts toward `sq[0]`. `txd[0]` leaves first, and `so` is the serial stream.
3. `fcx_ffe` makes the taps: `pre = so` (d[n+1]), `main = so` delayed 1 UI (d[n]), `post = so` delayed 2 UI (d[n-1]). Each tap is single-to-differential.
4. In `fcx_drv`, three lvt diff pairs sum into `R0`/`R1` (50 Ω to avdd), which are the termination.
   - The main pair is wired with true polarity. The pre and post pairs are cross-wired, so they subtract.
   - Each tail is a binary DAC of `fca_tleg` instances with m = 1/2/4/8 (main, 4 bits), 1/2 (pre, 2 bits) and 1/2/4 (post, 3 bits). The weights come straight from the register ports `txffe_*`.

**Test ring oscillator**
1. `fct_cs5` is a ring of a current-starved NAND (`en = cmd_q[0]`) and four current-starved inverters, which makes five inverting stages.
   - It is starved by the DLL `vctl`/`vcp`, so it is a replica of the delay-line stage.
2. `fcd_ckbuf` feeds `fct_rip3`, which divides by 8 to give `ro_div`.
3. A NAND gate controlled by `cmd_q[2]` passes the divided clock to two cascaded `fct_rip3`, giving `ro_cnt[5:0]`.
4. `fc_rst_n` clears the divider and the counter.
5. The DLL `vctl` is also brought out through 20 k to `dll_vmon`.

**Slow control**
1. `cmd_pad[3:0]` and `cstb_pad` each go through `fcs_inrx`: `fce_hv` ESD, a 200 Ω series R, a secondary GGNMOS, a 6T Schmitt trigger on vddq, and a thick-oxide inverter to vddd.
2. `fcs_creg` (4× `fcd_dffr`) captures on the strobe's rising edge.
3. The register bits are `cmd_q[0]` RO enable, `cmd_q[1]` CDR hold (all lanes), `cmd_q[2]` count window, and `cmd_q[3]` spare (read back only).
4. `rst_n` clears the register.

**ESD**
- The CML pads use `fce_lv` (GGNMOS + gate-tied PMOS).
- The slow pads use `fce_hv` inside `fcs_inrx`.
- There are three RC-triggered rail clamps (R 60 k, C 2 p, 3 inverters, NMOS m=40).

## 4. Loops

1. **DLL:** `ph[0]` → `fca_pfd` → `upb`/`dn` → `fca_isw` → `vctl` (`fca_lpf`) → `fca_dline` (vcn), and through MN0/MP0 → `vcp` → `fca_dline`. Negative feedback: UP (ref leads) raises `vctl`, which means more current and less delay. `dll_rst_n = 0` pulls `vctl` to avdd (minimum delay), so lock is acquired from the short side.
2. **CDR, per lane:** samplers → `fcr_bbx` → `fcr_vote` → `fcr_acc` → `code` → `fcr_phsel`/`fca_mix2w` → `pck` → samplers and digital clock. The loop is bang-bang, decimated to one update per word.
3. **PFD reset:** `up & dn` → NOR with the external reset → two-inverter delay → the flops' `rb`.
4. **Ring oscillator:** `r4` → NAND → `r0` … → `r4`.
5. **Johnson divider:** `wckb` → `X0.d`, an inverted twisted-ring feedback.
6. **Ripple counters:** each flop's `qb` → its own `d`.
7. **Local feedback that is not a block-level loop:**
   - Schmitt hysteresis (MP2/MN3).
   - Flop and latch keepers.
   - The CML latch regeneration pair.
   - The weak cross-coupled pair in each delay cell.

## 5. Intentional asymmetry

- `fcr_phsel` uses two trees. Tree B has the same structure as tree A but its inputs are rotated by one phase, and `ph[0]` wraps into `X4[3].d1`. There is no select incrementer.
- `a`/`ab` and `b`/`bb` come from different inverter depths, a one-gate skew.
- `fca_phd` is one inverting driver per phase, with the index rotated by 4.
- `fca_dline` has a fifth, dummy delay cell that loads `ph[4]`/`ph[0]`. Its outputs `dmp`/`dmn` are unused.
- `fca_fwd/X3` is the same `fca_c2c` as X2, but its inputs are swapped to make `ckn`.
- `fcr_smp/X1` (edge) is the same `fca_clff` as X0, with `ckp`/`ckn` swapped. In `fca_clff`, the master gets the clocks swapped.
- Clock edges in `fcr_dig` are mixed on purpose. These run on ck falling, through instances with the ck pin wired to `ckab`:
  - the data retime in `fcr_bbx`,
  - the deser shift,
  - the vote.

  These run on ck rising:
  - the edge retime `e0`,
  - the Johnson divider.

  The accumulator runs on `wck`.
- Counter bits alternate between `fcr_ube` (active-high carry in, active-low carry out) and `fcr_ubo` (the opposite).
- The FFE DACs differ in size: main 4 bits, pre 2 bits, post 3 bits. The pre and post pairs are cross-wired (negative taps). The main pair is m=8, post m=4 and pre m=2.
- The PI tails are complementary: A has a fixed unit plus `wb`-legs, B has `w`-legs only.
- `fca_cmla` uses `rl=600` in the lanes and `rl=450` in the clock lane. `fca_mix2w` uses `rl=420` instead of its default of 500.
- The Tx uses DLL phase `ph[0]` directly as its bit clock.
- The vote samples 3 of 8 PD decisions per word. This decimation is a design choice.

## 6. Unused outputs and intended stubs

- Flat level: no floating nets and no gate-only (undriven) nets.
- Per cell, there are 51 single-connection nets. All are deliberately unused outputs and are listed in `scripts/intended_stubs.json`:
  - Flop `qb` outputs:
    - `fcr_bbx`: s0b, s1b, e0b, e1b
    - `fcr_vote`: u1b, u2b, d1b, d2b
    - `fcr_dsr8`: srb[7:2]
    - `fcx_ser8`: sqb[7:0]
    - `fcx_ffe`: d1b, d2b
    - `fcs_creg`: cqb[3:0]
    - `fcr_jdiv8`: q0b, q2b
  - `fca_dll`: up, dnb (the PFD outputs the pump does not use).
  - `fca_dline`: dmp, dmn (dummy cell).
  - `fcr_acc`: cb2, cb3, cb4, cub5, cdb5.
  - `fct_mon`: dq[1:0], dqb[2:0], cb[1:0], cb[5:3].
  - `fcx_ser8`: sob.
  - `fcx_lane`: wckb.
- `cmd_q[3]` drives nothing inside; it is read back only.

## 7. Look-alike traps

| # | Block | Looks like | Really is | How the netlist tells them apart |
|---|---|---|---|---|
| 1 | `fca_mix2w` (in `fcr_phmix`) | Summer / FFE (it is wired like `fcx_drv`) | Phase interpolator | <ul><li>The pair inputs are two adjacent DLL clock phases, coming through `fcr_phsel` from `ph[7:0]`. They are not delayed copies of one data stream.</li><li>The tail weights are complementary (A = 1 + legs on `wb`, B = legs on `w`), so the total is always 4 units.</li><li>The weights come from the CDR accumulator `code`/`codeb`, not from register ports.</li><li>The loads carry slew caps C0/C1.</li><li>The output goes to the sampler clock pins and to `fca_c2c`, not to a pad.</li><li>No pair is cross-wired for a negative tap.</li></ul> |
| 2 | `fca_isw` | Tri-state or current-starved inverter | DLL charge pump | <ul><li>The inner gates are two different signals: `upb` from the PFD UP flop's qb, and `dn` from the DN flop's q.</li><li>The outer gates are bias nodes: `vbp` from the diode MP0, and `ib` from the diode MN0 that `ib_cp` feeds.</li><li>The output `vctl` is an analog node. It goes to the R+C filter (`fca_lpf`), the MOS decap MN1, and three sets of bias/starve gates: the delay-line NMOS starve devices, the vcp converter MN0, and, at the top, the RO replica. It also goes to the 20 k monitor. It never drives a logic input.</li></ul> |
| 3 | `fct_cs5` | Buffer chain of starved inverters | 5-stage ring oscillator | <ul><li>The last node `r4` returns to the gate of the first (NAND) stage: MN1.g / MP1.g. The chain is closed.</li><li>There are 5 inverting stages, an odd number.</li><li>The only other input is the enable `en`. When `en = 0`, MP2 forces `r0` high and the ring holds the static pattern 1,0,1,0,1.</li><li>The switch-level sim never settles with `en = 1`.</li></ul> |
| 4 | `fcs_inrx` Schmitt (MP0/MP1/MN1/MN2 + MP2/MN3) | Latch, because the output feeds back | Schmitt trigger | <ul><li>A single input `pi` drives all four stack gates.</li><li>The feedback devices take the gate `sx` (the output). One channel terminal sits on a stack midpoint (`p1` or `n1`, the d pin) and the other goes to the opposite rail (MP2 to vssq, MN3 to vddq).</li><li>There is no cross-coupled inverter pair, no clock and no second data input.</li><li>The output follows the input.</li></ul> |
| 5 | `fcr_bbx` | BIST/PRBS checker or a plain sampler bank (DFFs + XORs) | Alexander bang-bang PD | <ul><li>The inputs are a data sample and an edge sample of the same signal, half a UI apart.</li><li>The flops use both clock edges: X0, X1 and X3 have ck/ckb swapped.</li><li>Each XOR compares an edge sample with a neighbouring data bit.</li><li>There is no LFSR, no pattern generator and no error counter.</li><li>The outputs go to `fcr_vote` → `fcr_acc` → PI code, which is a loop.</li><li>The data flops are also the first deserializer stages.</li></ul> |
| 6 | `fca_dcell` / `fca_dline` | Static slew-limited inverters with fixed starve bias | Voltage-controlled delay line of a DLL | <ul><li>The starve gates `vcn`/`vcp` are `vctl` (charge pump + loop filter) and its PMOS mirror `vcp`, not fixed bias.</li><li>The chain's tap `ph[0]` returns to the PFD `fb` input.</li><li>The weak cross-coupled pair (L = lcs, W = wkn/wkp) only keeps the two outputs complementary. It is not a latch: there is no clock, and the starved drivers overpower it.</li></ul> |

Extra traps (documented in the key):
- **`fce_clmp`/`fce_clmphv`:** a three-inverter chain driving a big NMOS between the rails. It looks like a buffer chain, but it is an RC-triggered ESD clamp. Its input is the R–C node, and it is off in steady state.
- **`fcr_jdiv8`:** four flops in a row, like the deser shift register, but closed with inverted feedback (`wckb` → `X0.d`). It is a ÷8 divider plus a pulse decode.
- **`fca_pfd`:** reset flops again, but D is tied to vddd and the outputs reset themselves through NAND → delay → `rb`. It is a PFD, not a sampler and not the Alexander PD.
- **`fcr_phsel`:** TG mux trees like a serializer, but they select a static clock phase and change only when the code steps.
- **`fca_cl`:** contains a cross-coupled pair, but that is the CML latch's regeneration half. The clock steers the tail between the track pair and the regeneration pair.
- **`fca_phd`:** a single inverter per phase looks like it inverts the phases, but the index rotation by 4 restores them.

## 8. Checks (`scripts/run_all.sh`)

| Check | Script | Result |
|---|---|---|
| Parse, including `.global`, `.param`, subckt params and instance overrides | `check_netlist.py` | PASS |
| One top, nothing instantiates it, all 54 others are instantiated | `check_netlist.py` | PASS |
| Pin counts: 207 instances, 1243 instance pins | `check_netlist.py` | PASS |
| Bulks on the correct rails: n on vssd/avss/vssq, p on vddd/avdd/vddq, and the bulk equals the rail a source sits on | `check_netlist.py` | PASS, 0 violations |
| IO rails touched only by `_hv` devices | `check_netlist.py` | PASS |
| Floating and undriven nets: 0 at the flat level; the 51 per-cell stubs match the intended list | `check_netlist.py` | PASS |
| Export style: only netlister comments, legal tokens | `check_export.py` | PASS |
| Switch-level logic: 892 checks, 36/36 digital cells | `check_logic.py` | PASS |
| Answer-key consistency: 55 cells, 111 pins, 545 flows / 1090 endpoints | `check_key.py` | PASS |

The logic checks cover:
- truth tables of all leaf gates;
- flop and latch capture/hold and asynchronous reset;
- the PFD lead/lag and self-reset;
- all 64 phase-select cases;
- the PD up/dn equations against random D/E;
- the vote majority;
- accumulator up/down/wrap/cancel/hold over 140 steps;
- the Johnson sequence and load pulse;
- ripple count, the RO ÷8 divider and gated count wrap;
- that the ring oscillates when enabled;
- Schmitt polarity and feedback nodes, and the clamp steady state and trigger;
- delay-line static phase mapping, and the phase-distribution rotation;
- the closed-loop CDR with a behavioural sampler model: lock to targets 11 and 24, one step at a time in the short direction, then dithering ±1;
- deser words against the transmitted bits;
- that `hold` freezes the code;
- Tx serializer word order and FFE tap delays and complements.

CML and analog cells are not logic-simulated:
- `fca_cmla`, `fca_cl`, `fca_clff`, `fca_c2c`, `fca_mix2w`;
- `fca_isw`, `fca_lpf`, `fca_bias`, `fca_trm`, `fca_tleg`, `fcx_drv`, `fce_lv`.
