** Generated for: hspiceD
** Generated on: Nov 14 12:16:45 2026
** Design library name: ddr_dqrx
** Design cell name: dqs_dq_rx_top
** Design view name: schematic
**
** DRAM-style byte receive path (x8):
**  DQS_t/DQS_c -> ESD -> diff amp -> C2C -> WDCA duty adjust (wdca<3:0>) -> RPT clock tree
**  (unmatched, no DQ/DQS delay matching) -> per-bit local clock buffers
**  DQ<7:0> -> ESD -> preamp (vs VREFDQ) -> VGA (vga_gain<2:0>) -> StrongARM samplers
**  rising sampler (dqs_t_b) -> dq_r<7:0>, falling sampler (dqs_c_b) -> dq_f<7:0>
**  VREFDQ = 16-step ladder DAC (vref_code<3:0>, 0.625..0.859 VDDQ) + unity-gain buffer
** Supplies: vddq = 1.1V (pads, preamps, VREF, nch_18/pch_18), vdd = 0.8V core (VGA, samplers, clocks)

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: ddr_stdcell
** Cell name: inv_x1
** View name: schematic
.subckt inv_x1 a y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mn0 y a vss vss nch w=180n l=30n m=1
.ends inv_x1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nand2_x1
** View name: schematic
.subckt nand2_x1 a b y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mp1 y b vdd vdd pch w=360n l=30n m=1
mn0 y a net7 vss nch w=360n l=30n m=1
mn1 net7 b vss vss nch w=360n l=30n m=1
.ends nand2_x1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nor2_x1
** View name: schematic
.subckt nor2_x1 a b y vdd vss
mp0 net9 a vdd vdd pch w=720n l=30n m=1
mp1 y b net9 vdd pch w=720n l=30n m=1
mn0 y a vss vss nch w=180n l=30n m=1
mn1 y b vss vss nch w=180n l=30n m=1
.ends nor2_x1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nand3_x1
** View name: schematic
.subckt nand3_x1 a b c y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mp1 y b vdd vdd pch w=360n l=30n m=1
mp2 y c vdd vdd pch w=360n l=30n m=1
mn0 y a net11 vss nch w=540n l=30n m=1
mn1 net11 b net12 vss nch w=540n l=30n m=1
mn2 net12 c vss vss nch w=540n l=30n m=1
.ends nand3_x1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: and3_x1
** View name: schematic
.subckt and3_x1 a b c y vdd vss
xi0 a b c net6 vdd vss nand3_x1
xi1 net6 y vdd vss inv_x1
.ends and3_x1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: sr_latch_nand
** View name: schematic
.subckt sr_latch_nand sb rb q qb vdd vss
mp0 q sb vdd vdd pch_lvt w=400n l=30n m=1
mp1 q qb vdd vdd pch_lvt w=400n l=30n m=1
mn0 q sb net1 vss nch_lvt w=400n l=30n m=1
mn1 net1 qb vss vss nch_lvt w=400n l=30n m=1
mp2 qb rb vdd vdd pch_lvt w=400n l=30n m=1
mp3 qb q vdd vdd pch_lvt w=400n l=30n m=1
mn2 qb rb net2 vss nch_lvt w=400n l=30n m=1
mn3 net2 q vss vss nch_lvt w=400n l=30n m=1
.ends sr_latch_nand
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: ls_vdd2vddq
** View name: schematic
** vdd -> vddq level shifter, out = in, outb = ~in
.subckt ls_vdd2vddq in out outb vdd vddq vss
mp0 inb in vdd vdd pch w=360n l=30n m=1
mn0 inb in vss vss nch w=180n l=30n m=1
mn1 n1 in vss vss nch_18 w=1u l=150n m=1
mn2 n2 inb vss vss nch_18 w=1u l=150n m=1
mp1 n1 n2 vddq vddq pch_18 w=300n l=150n m=1
mp2 n2 n1 vddq vddq pch_18 w=300n l=150n m=1
mp3 outb n2 vddq vddq pch_18 w=1u l=150n m=1
mn3 outb n2 vss vss nch_18 w=500n l=150n m=1
mp4 out n1 vddq vddq pch_18 w=1u l=150n m=1
mn4 out n1 vss vss nch_18 w=500n l=150n m=1
.ends ls_vdd2vddq
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: rx_esd
** View name: schematic
** pad clamps + CDM series resistor + secondary clamp
.subckt rx_esd pad core vddq vss
mn0 pad vss vss vss nch_18 w=20u l=200n m=2
mp0 pad vddq vddq vddq pch_18 w=20u l=200n m=2
r0 pad core r=100
mn1 core vss vss vss nch_18 w=2u l=200n m=1
.ends rx_esd
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: rx_bias
** View name: schematic
** 50uA reference -> vbn_c (core nch_lvt tails) and, via PMOS mirror on vddq, vbn_q (nch_18 tails)
.subckt rx_bias ibias en vbn_q vbn_c vdd vddq vss
mp2 enb en vdd vdd pch w=360n l=30n m=1
mn5 enb en vss vss nch w=180n l=30n m=1
mn0 ibias ibias vss vss nch_lvt w=2u l=100n m=2
r0 ibias vbn_c r=10k
c0 vbn_c vss c=2p
mn1 nbp vbn_c vss vss nch_lvt w=2u l=100n m=2
mp0 nbp nbp vddq vddq pch_18 w=4u l=300n m=2
mp1 vbn_q nbp vddq vddq pch_18 w=4u l=300n m=2
mn2 vbn_q vbn_q vss vss nch_18 w=4u l=300n m=1
c1 vbn_q vss c=2p
mn3 vbn_c enb vss vss nch w=360n l=30n m=1
mn4 vbn_q enb vss vss nch w=360n l=30n m=1
.ends rx_bias
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: vref_ladder16
** View name: schematic
** tap<k> = (40+k)/64 * VDDQ  (0.625 .. 0.859 VDDQ), 32k total
.subckt vref_ladder16 enb tap<15> tap<14> tap<13> tap<12> tap<11> tap<10> tap<9> tap<8> tap<7> tap<6> tap<5> tap<4> tap<3> tap<2> tap<1> tap<0> vddq vss
mp0 ntop enb vddq vddq pch_18 w=4u l=150n m=2
r0 ntop tap<15> r=4.5k
r1<14> tap<15> tap<14> r=500
r1<13> tap<14> tap<13> r=500
r1<12> tap<13> tap<12> r=500
r1<11> tap<12> tap<11> r=500
r1<10> tap<11> tap<10> r=500
r1<9> tap<10> tap<9> r=500
r1<8> tap<9> tap<8> r=500
r1<7> tap<8> tap<7> r=500
r1<6> tap<7> tap<6> r=500
r1<5> tap<6> tap<5> r=500
r1<4> tap<5> tap<4> r=500
r1<3> tap<4> tap<3> r=500
r1<2> tap<3> tap<2> r=500
r1<1> tap<2> tap<1> r=500
r1<0> tap<1> tap<0> r=500
r2 tap<0> vss r=20k
.ends vref_ladder16
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: pdec2to4
** View name: schematic
** y<k> = 1 when {s1,s0} = k
.subckt pdec2to4 s1 s0 y<3> y<2> y<1> y<0> vdd vss
xi0 s1 s1b vdd vss inv_x1
xi1 s0 s0b vdd vss inv_x1
xi2 s1 s0 y<0> vdd vss nor2_x1
xi3 s1 s0b y<1> vdd vss nor2_x1
xi4 s1b s0 y<2> vdd vss nor2_x1
xi5 s1b s0b y<3> vdd vss nor2_x1
.ends pdec2to4
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: vref_dec4to16
** View name: schematic
** one-hot active-low tap select, selb<k> = 0 when c<3:0> = k
.subckt vref_dec4to16 c<3> c<2> c<1> c<0> selb<15> selb<14> selb<13> selb<12> selb<11> selb<10> selb<9> selb<8>
+ selb<7> selb<6> selb<5> selb<4> selb<3> selb<2> selb<1> selb<0> vdd vss
xi0 c<1> c<0> a<3> a<2> a<1> a<0> vdd vss pdec2to4
xi1 c<3> c<2> b<3> b<2> b<1> b<0> vdd vss pdec2to4
xi2<15> b<3> a<3> selb<15> vdd vss nand2_x1
xi2<14> b<3> a<2> selb<14> vdd vss nand2_x1
xi2<13> b<3> a<1> selb<13> vdd vss nand2_x1
xi2<12> b<3> a<0> selb<12> vdd vss nand2_x1
xi2<11> b<2> a<3> selb<11> vdd vss nand2_x1
xi2<10> b<2> a<2> selb<10> vdd vss nand2_x1
xi2<9> b<2> a<1> selb<9> vdd vss nand2_x1
xi2<8> b<2> a<0> selb<8> vdd vss nand2_x1
xi2<7> b<1> a<3> selb<7> vdd vss nand2_x1
xi2<6> b<1> a<2> selb<6> vdd vss nand2_x1
xi2<5> b<1> a<1> selb<5> vdd vss nand2_x1
xi2<4> b<1> a<0> selb<4> vdd vss nand2_x1
xi2<3> b<0> a<3> selb<3> vdd vss nand2_x1
xi2<2> b<0> a<2> selb<2> vdd vss nand2_x1
xi2<1> b<0> a<1> selb<1> vdd vss nand2_x1
xi2<0> b<0> a<0> selb<0> vdd vss nand2_x1
.ends vref_dec4to16
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: vref_sw16
** View name: schematic
** PMOS-only tap switches (taps are > 0.6 VDDQ), gate low = selected
.subckt vref_sw16 tap<15> tap<14> tap<13> tap<12> tap<11> tap<10> tap<9> tap<8> tap<7> tap<6> tap<5> tap<4> tap<3> tap<2> tap<1> tap<0>
+ selb<15> selb<14> selb<13> selb<12> selb<11> selb<10> selb<9> selb<8> selb<7> selb<6> selb<5> selb<4> selb<3> selb<2> selb<1> selb<0> vout vddq
mp15 vout selb<15> tap<15> vddq pch_18 w=2u l=150n m=1
mp14 vout selb<14> tap<14> vddq pch_18 w=2u l=150n m=1
mp13 vout selb<13> tap<13> vddq pch_18 w=2u l=150n m=1
mp12 vout selb<12> tap<12> vddq pch_18 w=2u l=150n m=1
mp11 vout selb<11> tap<11> vddq pch_18 w=2u l=150n m=1
mp10 vout selb<10> tap<10> vddq pch_18 w=2u l=150n m=1
mp9 vout selb<9> tap<9> vddq pch_18 w=2u l=150n m=1
mp8 vout selb<8> tap<8> vddq pch_18 w=2u l=150n m=1
mp7 vout selb<7> tap<7> vddq pch_18 w=2u l=150n m=1
mp6 vout selb<6> tap<6> vddq pch_18 w=2u l=150n m=1
mp5 vout selb<5> tap<5> vddq pch_18 w=2u l=150n m=1
mp4 vout selb<4> tap<4> vddq pch_18 w=2u l=150n m=1
mp3 vout selb<3> tap<3> vddq pch_18 w=2u l=150n m=1
mp2 vout selb<2> tap<2> vddq pch_18 w=2u l=150n m=1
mp1 vout selb<1> tap<1> vddq pch_18 w=2u l=150n m=1
mp0 vout selb<0> tap<0> vddq pch_18 w=2u l=150n m=1
.ends vref_sw16
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: vref_ota_buf
** View name: schematic
** 5T OTA unity-gain VREF buffer (vddq)
.subckt vref_ota_buf vin vout vbn en vddq vss
mn0 ntl vbn nte vss nch_18 w=4u l=300n m=2
mn1 nte en vss vss nch w=1u l=30n m=1
mn2 nd vin ntl vss nch_18 w=8u l=300n m=2
mn3 vout vout ntl vss nch_18 w=8u l=300n m=2
mp0 nd nd vddq vddq pch_18 w=4u l=300n m=2
mp1 vout nd vddq vddq pch_18 w=4u l=300n m=2
c0 vout vss c=2p
.ends vref_ota_buf
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: vrefdq_gen
** View name: schematic
.subckt vrefdq_gen vref_code<3> vref_code<2> vref_code<1> vref_code<0> vref_en vbn_q vref_buf vdd vddq vss
xi0 vref_en net10 en_hb vdd vddq vss ls_vdd2vddq
xi1 en_hb tap<15> tap<14> tap<13> tap<12> tap<11> tap<10> tap<9> tap<8> tap<7> tap<6> tap<5> tap<4> tap<3> tap<2> tap<1> tap<0> vddq vss vref_ladder16
xi2 vref_code<3> vref_code<2> vref_code<1> vref_code<0> selb<15> selb<14> selb<13> selb<12> selb<11> selb<10> selb<9> selb<8>
+ selb<7> selb<6> selb<5> selb<4> selb<3> selb<2> selb<1> selb<0> vdd vss vref_dec4to16
xi3 tap<15> tap<14> tap<13> tap<12> tap<11> tap<10> tap<9> tap<8> tap<7> tap<6> tap<5> tap<4> tap<3> tap<2> tap<1> tap<0>
+ selb<15> selb<14> selb<13> selb<12> selb<11> selb<10> selb<9> selb<8> selb<7> selb<6> selb<5> selb<4> selb<3> selb<2> selb<1> selb<0> vref_raw vddq vref_sw16
c0 vref_raw vss c=500f
xi4 vref_raw vref_buf vbn_q vref_en vddq vss vref_ota_buf
c1 vref_buf vss c=10p
.ends vrefdq_gen
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_amp
** View name: schematic
** DQS_t/DQS_c differential input amplifier (vddq), ~400uA tail, out cm ~0.65V
.subckt dqs_amp inp inn vbn en outp outn vddq vss
mn0 ntail vbn nten vss nch_18 w=4u l=300n m=8
mn1 nten en vss vss nch w=4u l=30n m=1
mn2 outn inp ntail vss nch_18 w=12u l=150n m=2
mn3 outp inn ntail vss nch_18 w=12u l=150n m=2
r0 outp vddq r=2.2k
r1 outn vddq r=2.2k
.ends dqs_amp
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_c2c
** View name: schematic
** dual 5T OTA diff-to-CMOS converter; outtb = ~DQS_t, outcb = ~DQS_c (inverted, CMOS vdd)
.subckt dqs_c2c inp inn vbn en outtb outcb vdd vss
mn0 ntl vbn nte vss nch_lvt w=2u l=100n m=2
mn1 ntl2 vbn nte vss nch_lvt w=2u l=100n m=2
mn2 nte en vss vss nch_lvt w=4u l=30n m=2
mn3 nd1 inp ntl vss nch_lvt w=2u l=30n m=2
mn4 o_t inn ntl vss nch_lvt w=2u l=30n m=2
mp0 nd1 nd1 vdd vdd pch_lvt w=2u l=30n m=1
mp1 o_t nd1 vdd vdd pch_lvt w=2u l=30n m=1
mn5 nd2 inn ntl2 vss nch_lvt w=2u l=30n m=2
mn6 o_c inp ntl2 vss nch_lvt w=2u l=30n m=2
mp2 nd2 nd2 vdd vdd pch_lvt w=2u l=30n m=1
mp3 o_c nd2 vdd vdd pch_lvt w=2u l=30n m=1
mp4 outtb o_t vdd vdd pch_lvt w=1.6u l=30n m=1
mn7 outtb o_t vss vss nch_lvt w=800n l=30n m=1
mp5 outcb o_c vdd vdd pch_lvt w=1.6u l=30n m=1
mn8 outcb o_c vss vss nch_lvt w=800n l=30n m=1
mp6 outcb outtb vdd vdd pch_lvt w=300n l=30n m=1
mn9 outcb outtb vss vss nch_lvt w=150n l=30n m=1
mp7 outtb outcb vdd vdd pch_lvt w=300n l=30n m=1
mn10 outtb outcb vss vss nch_lvt w=150n l=30n m=1
.ends dqs_c2c
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: wdca_dec
** View name: schematic
** wdca<3> = sign (1: widen DQS_t high phase), wdca<2:0> = magnitude
** up<k> = en & sign & mag<k>, dn<k> = en & ~sign & mag<k>
.subckt wdca_dec wdca<3> wdca<2> wdca<1> wdca<0> wdca_en up<2> up<1> up<0> up_b<2> up_b<1> up_b<0>
+ dn<2> dn<1> dn<0> dn_b<2> dn_b<1> dn_b<0> vdd vss
xi0 wdca<3> sgn_b vdd vss inv_x1
xi1<2> wdca_en wdca<3> wdca<2> up<2> vdd vss and3_x1
xi1<1> wdca_en wdca<3> wdca<1> up<1> vdd vss and3_x1
xi1<0> wdca_en wdca<3> wdca<0> up<0> vdd vss and3_x1
xi2<2> up<2> up_b<2> vdd vss inv_x1
xi2<1> up<1> up_b<1> vdd vss inv_x1
xi2<0> up<0> up_b<0> vdd vss inv_x1
xi3<2> wdca_en sgn_b wdca<2> dn<2> vdd vss and3_x1
xi3<1> wdca_en sgn_b wdca<1> dn<1> vdd vss and3_x1
xi3<0> wdca_en sgn_b wdca<0> dn<0> vdd vss and3_x1
xi4<2> dn<2> dn_b<2> vdd vss inv_x1
xi4<1> dn<1> dn_b<1> vdd vss inv_x1
xi4<0> dn<0> dn_b<0> vdd vss inv_x1
.ends wdca_dec
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: wdca_stage
** View name: schematic
** inverting duty-adjust stage: binary-weighted extra pull-up legs (pdb<k>=0 enables)
** and pull-down legs (nen<k>=1 enables) skew rise vs fall
.subckt wdca_stage in out pdb<2> pdb<1> pdb<0> nen<2> nen<1> nen<0> vdd vss
mp0 out in vdd vdd pch_lvt w=1.2u l=30n m=1
mn0 out in vss vss nch_lvt w=600n l=30n m=1
mp1 out in np0 vdd pch_lvt w=300n l=30n m=1
mp2 np0 pdb<0> vdd vdd pch_lvt w=300n l=30n m=1
mp3 out in np1 vdd pch_lvt w=300n l=30n m=2
mp4 np1 pdb<1> vdd vdd pch_lvt w=300n l=30n m=2
mp5 out in np2 vdd pch_lvt w=300n l=30n m=4
mp6 np2 pdb<2> vdd vdd pch_lvt w=300n l=30n m=4
mn1 out in nn0 vss nch_lvt w=150n l=30n m=1
mn2 nn0 nen<0> vss vss nch_lvt w=150n l=30n m=1
mn3 out in nn1 vss nch_lvt w=150n l=30n m=2
mn4 nn1 nen<1> vss vss nch_lvt w=150n l=30n m=2
mn5 out in nn2 vss nch_lvt w=150n l=30n m=4
mn6 nn2 nen<2> vss vss nch_lvt w=150n l=30n m=4
.ends wdca_stage
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_rx_wdca
** View name: schematic
** DQS input buffer with built-in write duty-cycle adjuster
.subckt dqs_rx_wdca dqs_t dqs_c vbn_q vbn_c dqs_en wdca<3> wdca<2> wdca<1> wdca<0> wdca_en dqs_t_i dqs_c_i vdd vddq vss
xi0 dqs_t dqs_t_p vddq vss rx_esd
xi1 dqs_c dqs_c_p vddq vss rx_esd
xi2 dqs_t_p dqs_c_p vbn_q dqs_en da_p da_n vddq vss dqs_amp
xi3 da_p da_n vbn_c dqs_en dtb dcb vdd vss dqs_c2c
xi4 wdca<3> wdca<2> wdca<1> wdca<0> wdca_en up<2> up<1> up<0> up_b<2> up_b<1> up_b<0>
+ dn<2> dn<1> dn<0> dn_b<2> dn_b<1> dn_b<0> vdd vss wdca_dec
xi5 dtb dqs_t_i up_b<2> up_b<1> up_b<0> dn<2> dn<1> dn<0> vdd vss wdca_stage
xi6 dcb dqs_c_i dn_b<2> dn_b<1> dn_b<0> up<2> up<1> up<0> vdd vss wdca_stage
mp0 dqs_c_i dqs_t_i vdd vdd pch_lvt w=200n l=30n m=1
mn0 dqs_c_i dqs_t_i vss vss nch_lvt w=100n l=30n m=1
mp1 dqs_t_i dqs_c_i vdd vdd pch_lvt w=200n l=30n m=1
mn1 dqs_t_i dqs_c_i vss vss nch_lvt w=100n l=30n m=1
.ends dqs_rx_wdca
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: rpt_stage
** View name: schematic
** non-inverting differential CMOS repeater (2 inverters per rail, cross-coupled midpoints)
.subckt rpt_stage in_t in_c out_t out_c vdd vss
mp0 n1 in_t vdd vdd pch_lvt w=1u l=30n m=1
mn0 n1 in_t vss vss nch_lvt w=500n l=30n m=1
mp1 out_t n1 vdd vdd pch_lvt w=2u l=30n m=3
mn1 out_t n1 vss vss nch_lvt w=1u l=30n m=3
mp2 n2 in_c vdd vdd pch_lvt w=1u l=30n m=1
mn2 n2 in_c vss vss nch_lvt w=500n l=30n m=1
mp3 out_c n2 vdd vdd pch_lvt w=2u l=30n m=3
mn3 out_c n2 vss vss nch_lvt w=1u l=30n m=3
mp4 n2 n1 vdd vdd pch_lvt w=300n l=30n m=1
mn4 n2 n1 vss vss nch_lvt w=150n l=30n m=1
mp5 n1 n2 vdd vdd pch_lvt w=300n l=30n m=1
mn5 n1 n2 vss vss nch_lvt w=150n l=30n m=1
.ends rpt_stage
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_lcb
** View name: schematic
** per-bit local strobe buffer, gated by en (both outputs low when disabled)
.subckt dqs_lcb in_t in_c en out_t out_c vdd vss
xi0 in_t en n1 vdd vss nand2_x1
xi1 in_c en n2 vdd vss nand2_x1
mp0 out_t n1 vdd vdd pch_lvt w=2u l=30n m=2
mn0 out_t n1 vss vss nch_lvt w=1u l=30n m=2
mp1 out_c n2 vdd vdd pch_lvt w=2u l=30n m=2
mn1 out_c n2 vss vss nch_lvt w=1u l=30n m=2
.ends dqs_lcb
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_clk_tree
** View name: schematic
** unmatched DQS/DQSB distribution: trunk RPT at strobe buffer, left branch (2 RPT)
** to DQ<3:0> spine, right branch (2 RPT) to DQ<4:7> spine, RC wire segments, per-bit LCB
.subckt dqs_clk_tree dqs_t_i dqs_c_i rx_en dqs_t_b<7> dqs_t_b<6> dqs_t_b<5> dqs_t_b<4> dqs_t_b<3> dqs_t_b<2> dqs_t_b<1> dqs_t_b<0>
+ dqs_c_b<7> dqs_c_b<6> dqs_c_b<5> dqs_c_b<4> dqs_c_b<3> dqs_c_b<2> dqs_c_b<1> dqs_c_b<0> vdd vss
xi0 dqs_t_i dqs_c_i trk_t trk_c vdd vss rpt_stage
* left branch
r0 trk_t lw_t r=60
r1 trk_c lw_c r=60
c0 lw_t vss c=25f
c1 lw_c vss c=25f
xi1 lw_t lw_c l1_t l1_c vdd vss rpt_stage
r2 l1_t lw2_t r=60
r3 l1_c lw2_c r=60
c2 lw2_t vss c=25f
c3 lw2_c vss c=25f
xi2 lw2_t lw2_c l2_t l2_c vdd vss rpt_stage
r4<3> l2_t tp_t<3> r=25
r5<3> l2_c tp_c<3> r=25
r4<2> tp_t<3> tp_t<2> r=25
r5<2> tp_c<3> tp_c<2> r=25
r4<1> tp_t<2> tp_t<1> r=25
r5<1> tp_c<2> tp_c<1> r=25
r4<0> tp_t<1> tp_t<0> r=25
r5<0> tp_c<1> tp_c<0> r=25
c4<3> tp_t<3> vss c=12f
c5<3> tp_c<3> vss c=12f
c4<2> tp_t<2> vss c=12f
c5<2> tp_c<2> vss c=12f
c4<1> tp_t<1> vss c=12f
c5<1> tp_c<1> vss c=12f
c4<0> tp_t<0> vss c=12f
c5<0> tp_c<0> vss c=12f
* right branch
r6 trk_t rw_t r=60
r7 trk_c rw_c r=60
c6 rw_t vss c=25f
c7 rw_c vss c=25f
xi3 rw_t rw_c r1_t r1_c vdd vss rpt_stage
r8 r1_t rw2_t r=60
r9 r1_c rw2_c r=60
c8 rw2_t vss c=25f
c9 rw2_c vss c=25f
xi4 rw2_t rw2_c r2_t r2_c vdd vss rpt_stage
r10<4> r2_t tp_t<4> r=25
r11<4> r2_c tp_c<4> r=25
r10<5> tp_t<4> tp_t<5> r=25
r11<5> tp_c<4> tp_c<5> r=25
r10<6> tp_t<5> tp_t<6> r=25
r11<6> tp_c<5> tp_c<6> r=25
r10<7> tp_t<6> tp_t<7> r=25
r11<7> tp_c<6> tp_c<7> r=25
c10<4> tp_t<4> vss c=12f
c11<4> tp_c<4> vss c=12f
c10<5> tp_t<5> vss c=12f
c11<5> tp_c<5> vss c=12f
c10<6> tp_t<6> vss c=12f
c11<6> tp_c<6> vss c=12f
c10<7> tp_t<7> vss c=12f
c11<7> tp_c<7> vss c=12f
* per-bit local clock buffers
xi5<7> tp_t<7> tp_c<7> rx_en dqs_t_b<7> dqs_c_b<7> vdd vss dqs_lcb
xi5<6> tp_t<6> tp_c<6> rx_en dqs_t_b<6> dqs_c_b<6> vdd vss dqs_lcb
xi5<5> tp_t<5> tp_c<5> rx_en dqs_t_b<5> dqs_c_b<5> vdd vss dqs_lcb
xi5<4> tp_t<4> tp_c<4> rx_en dqs_t_b<4> dqs_c_b<4> vdd vss dqs_lcb
xi5<3> tp_t<3> tp_c<3> rx_en dqs_t_b<3> dqs_c_b<3> vdd vss dqs_lcb
xi5<2> tp_t<2> tp_c<2> rx_en dqs_t_b<2> dqs_c_b<2> vdd vss dqs_lcb
xi5<1> tp_t<1> tp_c<1> rx_en dqs_t_b<1> dqs_c_b<1> vdd vss dqs_lcb
xi5<0> tp_t<0> tp_c<0> rx_en dqs_t_b<0> dqs_c_b<0> vdd vss dqs_lcb
.ends dqs_clk_tree
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_preamp
** View name: schematic
** single-ended DQ vs VREFDQ preamp (vddq), ~300uA tail, out cm ~0.65V
.subckt dq_preamp inp inn vbn en outp outn vddq vss
mn0 ntail vbn nten vss nch_18 w=4u l=300n m=6
mn1 nten en vss vss nch w=2u l=30n m=1
mn2 outn inp ntail vss nch_18 w=10u l=150n m=2
mn3 outp inn ntail vss nch_18 w=10u l=150n m=2
r0 outp vddq r=3k
r1 outn vddq r=3k
.ends dq_preamp
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_vga
** View name: schematic
** source-degenerated VGA (vdd); g<2:0> switches binary-weighted degeneration R in parallel
** (more bits on -> lower Rdeg -> higher gain)
.subckt dq_vga inp inn vbn en g<2> g<1> g<0> outp outn vdd vss
mn0 outn inp ns0 vss nch_lvt w=4u l=30n m=2
mn1 outp inn ns1 vss nch_lvt w=4u l=30n m=2
mn2 ns0 vbn nt vss nch_lvt w=2u l=100n m=6
mn3 ns1 vbn nt vss nch_lvt w=2u l=100n m=6
mn4 nt en vss vss nch_lvt w=4u l=30n m=2
r0 ns0 ns1 r=4k
r1 ns0 nd0 r=4k
mn5 nd0 g<0> ns1 vss nch_lvt w=1u l=30n m=1
r2 ns0 nd1 r=2k
mn6 nd1 g<1> ns1 vss nch_lvt w=1u l=30n m=2
r3 ns0 nd2 r=1k
mn7 nd2 g<2> ns1 vss nch_lvt w=1u l=30n m=4
c0 ns0 ns1 c=50f
r4 outp vdd r=1.5k
r5 outn vdd r=1.5k
.ends dq_vga
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_sa
** View name: schematic
** StrongARM sense amplifier, precharge while clk=0, evaluate on clk rise
.subckt dq_sa inp inn clk outp outn vdd vss
mn0 ntail clk vss vss nch_lvt w=2u l=30n m=2
mn1 nx inp ntail vss nch_lvt w=2u l=30n m=2
mn2 ny inn ntail vss nch_lvt w=2u l=30n m=2
mn3 outn outp nx vss nch_lvt w=1u l=30n m=1
mn4 outp outn ny vss nch_lvt w=1u l=30n m=1
mp0 outn outp vdd vdd pch_lvt w=1u l=30n m=1
mp1 outp outn vdd vdd pch_lvt w=1u l=30n m=1
mp2 outn clk vdd vdd pch_lvt w=500n l=30n m=1
mp3 outp clk vdd vdd pch_lvt w=500n l=30n m=1
mp4 nx clk vdd vdd pch_lvt w=500n l=30n m=1
mp5 ny clk vdd vdd pch_lvt w=500n l=30n m=1
.ends dq_sa
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_sampler
** View name: schematic
** SA + SR hold latch + output driver; q = (inp > inn) at clk rise
.subckt dq_sampler inp inn clk q vdd vss
xi0 inp inn clk outp outn vdd vss dq_sa
xi1 outn outp q_i qb_i vdd vss sr_latch_nand
mp0 q qb_i vdd vdd pch w=720n l=30n m=1
mn0 q qb_i vss vss nch w=360n l=30n m=1
.ends dq_sampler
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_rx_bit
** View name: schematic
** per-bit receiver: ESD -> preamp(vs filtered VREF) -> VGA -> rise/fall samplers
.subckt dq_rx_bit dq vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> dqs_t_b dqs_c_b dq_r dq_f vdd vddq vss
xi0 dq dq_i vddq vss rx_esd
r0 vref_buf vref_f r=5k
c0 vref_f vss c=200f
xi1 dq_i vref_f vbn_q rx_en pa_p pa_n vddq vss dq_preamp
xi2 pa_p pa_n vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> va_p va_n vdd vss dq_vga
xi3 va_p va_n dqs_t_b dq_r vdd vss dq_sampler
xi4 va_p va_n dqs_c_b dq_f vdd vss dq_sampler
.ends dq_rx_bit
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dq_rx_nibble
** View name: schematic
.subckt dq_rx_nibble dq<3> dq<2> dq<1> dq<0> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0>
+ dqs_t_b<3> dqs_t_b<2> dqs_t_b<1> dqs_t_b<0> dqs_c_b<3> dqs_c_b<2> dqs_c_b<1> dqs_c_b<0>
+ dq_r<3> dq_r<2> dq_r<1> dq_r<0> dq_f<3> dq_f<2> dq_f<1> dq_f<0> vdd vddq vss
xi0<3> dq<3> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> dqs_t_b<3> dqs_c_b<3> dq_r<3> dq_f<3> vdd vddq vss dq_rx_bit
xi0<2> dq<2> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> dqs_t_b<2> dqs_c_b<2> dq_r<2> dq_f<2> vdd vddq vss dq_rx_bit
xi0<1> dq<1> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> dqs_t_b<1> dqs_c_b<1> dq_r<1> dq_f<1> vdd vddq vss dq_rx_bit
xi0<0> dq<0> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0> dqs_t_b<0> dqs_c_b<0> dq_r<0> dq_f<0> vdd vddq vss dq_rx_bit
c0 vref_buf vss c=1p
c1 vbn_q vss c=500f
c2 vbn_c vss c=500f
.ends dq_rx_nibble
** End of subcircuit definition.

** Library name: ddr_dqrx
** Cell name: dqs_dq_rx_top
** View name: schematic
.subckt dqs_dq_rx_top dqs_t dqs_c dq<7> dq<6> dq<5> dq<4> dq<3> dq<2> dq<1> dq<0> ibias rx_en dqs_en vref_en
+ vref_code<3> vref_code<2> vref_code<1> vref_code<0> vga_gain<2> vga_gain<1> vga_gain<0> wdca<3> wdca<2> wdca<1> wdca<0> wdca_en
+ dq_r<7> dq_r<6> dq_r<5> dq_r<4> dq_r<3> dq_r<2> dq_r<1> dq_r<0> dq_f<7> dq_f<6> dq_f<5> dq_f<4> dq_f<3> dq_f<2> dq_f<1> dq_f<0> vdd vddq vss
xi0 ibias rx_en vbn_q vbn_c vdd vddq vss rx_bias
xi1 vref_code<3> vref_code<2> vref_code<1> vref_code<0> vref_en vbn_q vref_buf vdd vddq vss vrefdq_gen
xi2 dqs_t dqs_c vbn_q vbn_c dqs_en wdca<3> wdca<2> wdca<1> wdca<0> wdca_en dqs_t_i dqs_c_i vdd vddq vss dqs_rx_wdca
xi3 dqs_t_i dqs_c_i rx_en dqs_t_b<7> dqs_t_b<6> dqs_t_b<5> dqs_t_b<4> dqs_t_b<3> dqs_t_b<2> dqs_t_b<1> dqs_t_b<0>
+ dqs_c_b<7> dqs_c_b<6> dqs_c_b<5> dqs_c_b<4> dqs_c_b<3> dqs_c_b<2> dqs_c_b<1> dqs_c_b<0> vdd vss dqs_clk_tree
xi4 dq<3> dq<2> dq<1> dq<0> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0>
+ dqs_t_b<3> dqs_t_b<2> dqs_t_b<1> dqs_t_b<0> dqs_c_b<3> dqs_c_b<2> dqs_c_b<1> dqs_c_b<0>
+ dq_r<3> dq_r<2> dq_r<1> dq_r<0> dq_f<3> dq_f<2> dq_f<1> dq_f<0> vdd vddq vss dq_rx_nibble
xi5 dq<7> dq<6> dq<5> dq<4> vref_buf vbn_q vbn_c rx_en vga_gain<2> vga_gain<1> vga_gain<0>
+ dqs_t_b<7> dqs_t_b<6> dqs_t_b<5> dqs_t_b<4> dqs_c_b<7> dqs_c_b<6> dqs_c_b<5> dqs_c_b<4>
+ dq_r<7> dq_r<6> dq_r<5> dq_r<4> dq_f<7> dq_f<6> dq_f<5> dq_f<4> vdd vddq vss dq_rx_nibble
c0 vdd vss c=20p
c1 vddq vss c=20p
.ends dqs_dq_rx_top
** End of subcircuit definition.
