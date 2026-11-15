** Generated for: hspiceD
** Generated on: Nov 13 10:05:44 2026
** Design library name: hsio_clk28
** Design cell name: dcc_top
** Design view name: schematic
** Note: device models (nch, pch, nch_lvt) are provided by the foundry PDK
**       model library, which is included by the testbench, not here.

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2

** Library name: hsio_clk28
** Cell name: dcc_inv
** View name: schematic
.subckt dcc_inv in out vdd vss
m0 out in vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m1 out in vss vss nch l=30e-9 w=400e-9 m=1 nf=1
.ends dcc_inv
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_nand2
** View name: schematic
.subckt dcc_nand2 a b y vdd vss
m0 y a vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m1 y b vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m2 y a net5 vss nch l=30e-9 w=400e-9 m=1 nf=1
m3 net5 b vss vss nch l=30e-9 w=400e-9 m=1 nf=1
.ends dcc_nand2
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_nand3
** View name: schematic
.subckt dcc_nand3 a b c y vdd vss
m0 y a vdd vdd pch l=30e-9 w=300e-9 m=1 nf=1
m1 y b vdd vdd pch l=30e-9 w=300e-9 m=1 nf=1
m2 y c vdd vdd pch l=30e-9 w=300e-9 m=1 nf=1
m3 y a net6 vss nch l=30e-9 w=450e-9 m=1 nf=1
m4 net6 b net7 vss nch l=30e-9 w=450e-9 m=1 nf=1
m5 net7 c vss vss nch l=30e-9 w=450e-9 m=1 nf=1
.ends dcc_nand3
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_tgate
** View name: schematic
.subckt dcc_tgate a b en enb vdd vss
m0 a en b vss nch l=30e-9 w=400e-9 m=1 nf=1
m1 a enb b vdd pch l=30e-9 w=600e-9 m=1 nf=1
.ends dcc_tgate
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_adj_leg
** View name: schematic
** unit switchable PU / PD leg in parallel with the adjust inverter
.subckt dcc_adj_leg in out pu_enb pd_en vdd vss
m0 net10 pu_enb vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m1 out in net10 vdd pch l=30e-9 w=200e-9 m=1 nf=1
m2 out in net11 vss nch l=30e-9 w=120e-9 m=1 nf=1
m3 net11 pd_en vss vss nch l=30e-9 w=240e-9 m=1 nf=1
.ends dcc_adj_leg
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_adj_stage
** View name: schematic
** inverting duty-adjust stage: base inverter + binary-weighted PU/PD legs
.subckt dcc_adj_stage in out pu_enb<0> pu_enb<1> pu_enb<2> pu_enb<3>
+ pu_enb<4> pd_en<0> pd_en<1> pd_en<2> pd_en<3> pd_en<4> vdd vss
m0 out in vdd vdd pch l=30e-9 w=3e-6 m=1 nf=4
m1 out in vss vss nch l=30e-9 w=1.5e-6 m=1 nf=2
xi0 in out pu_enb<0> pd_en<0> vdd vss dcc_adj_leg m=1
xi1 in out pu_enb<1> pd_en<1> vdd vss dcc_adj_leg m=2
xi2 in out pu_enb<2> pd_en<2> vdd vss dcc_adj_leg m=4
xi3 in out pu_enb<3> pd_en<3> vdd vss dcc_adj_leg m=8
xi4 in out pu_enb<4> pd_en<4> vdd vss dcc_adj_leg m=16
.ends dcc_adj_stage
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_path
** View name: schematic
** adjust stage + FO4 output buffer chain (4 inversions total, non-inverting)
.subckt dcc_path in out pu_enb<0> pu_enb<1> pu_enb<2> pu_enb<3> pu_enb<4>
+ pd_en<0> pd_en<1> pd_en<2> pd_en<3> pd_en<4> vdd vss
xi0 in net09 pu_enb<0> pu_enb<1> pu_enb<2> pu_enb<3> pu_enb<4> pd_en<0>
+ pd_en<1> pd_en<2> pd_en<3> pd_en<4> vdd vss dcc_adj_stage
xi1 net09 net011 vdd vss dcc_inv m=2
xi2 net011 net013 vdd vss dcc_inv m=6
xi3 net013 out vdd vss dcc_inv m=16
** fixed load on adjust output (slows edges to widen trim range)
m0 vss net09 vss vss nch l=100e-9 w=1e-6 m=2 nf=1
.ends dcc_path
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_code_dec
** View name: schematic
** a<k> = en & sign & mag<k> ; b<k> = en & !sign & mag<k> (+ complements)
.subckt dcc_code_dec en sign mag<0> mag<1> mag<2> mag<3> mag<4> a<0> a<1>
+ a<2> a<3> a<4> ab<0> ab<1> ab<2> ab<3> ab<4> b<0> b<1> b<2> b<3> b<4>
+ bb<0> bb<1> bb<2> bb<3> bb<4> vdd vss
m0 signb sign vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m1 signb sign vss vss nch l=30e-9 w=200e-9 m=1 nf=1
xi0 en sign mag<0> ab<0> vdd vss dcc_nand3
xi1 en sign mag<1> ab<1> vdd vss dcc_nand3
xi2 en sign mag<2> ab<2> vdd vss dcc_nand3
xi3 en sign mag<3> ab<3> vdd vss dcc_nand3
xi4 en sign mag<4> ab<4> vdd vss dcc_nand3
xi5 en signb mag<0> bb<0> vdd vss dcc_nand3
xi6 en signb mag<1> bb<1> vdd vss dcc_nand3
xi7 en signb mag<2> bb<2> vdd vss dcc_nand3
xi8 en signb mag<3> bb<3> vdd vss dcc_nand3
xi9 en signb mag<4> bb<4> vdd vss dcc_nand3
xi10 ab<0> a<0> vdd vss dcc_inv
xi11 ab<1> a<1> vdd vss dcc_inv
xi12 ab<2> a<2> vdd vss dcc_inv
xi13 ab<3> a<3> vdd vss dcc_inv
xi14 ab<4> a<4> vdd vss dcc_inv
xi15 bb<0> b<0> vdd vss dcc_inv
xi16 bb<1> b<1> vdd vss dcc_inv
xi17 bb<2> b<2> vdd vss dcc_inv
xi18 bb<3> b<3> vdd vss dcc_inv
xi19 bb<4> b<4> vdd vss dcc_inv
.ends dcc_code_dec
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: cml2cmos_rx
** View name: schematic
** 5T OTA CML->CMOS converter, output forced high when en=0
.subckt cml2cmos_rx inp inn nbias en out vdd vss
m0 net20 inp ntail vss nch_lvt l=40e-9 w=2e-6 m=1 nf=2
m1 outa inn ntail vss nch_lvt l=40e-9 w=2e-6 m=1 nf=2
m2 net20 net20 vdd vdd pch l=60e-9 w=1.5e-6 m=1 nf=2
m3 outa net20 vdd vdd pch l=60e-9 w=1.5e-6 m=1 nf=2
m4 ntail nbias vss vss nch l=500e-9 w=4e-6 m=2 nf=2
m5 outa en vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
xi0 outa net21 vdd vss dcc_inv m=1
xi1 net21 out vdd vss dcc_inv m=3
.ends cml2cmos_rx
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_bias
** View name: schematic
** 25uA reference -> nbias, forced low when en=0
.subckt dcc_bias ibias en nbias vdd vss
r0 ibias nbias 200
m0 nbias nbias vss vss nch l=500e-9 w=2e-6 m=1 nf=1
m1 nbias enb vss vss nch l=30e-9 w=1e-6 m=1 nf=1
m2 enb en vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m3 enb en vss vss nch l=30e-9 w=200e-9 m=1 nf=1
c0 nbias vss 1e-12
.ends dcc_bias
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: rc_lpf
** View name: schematic
** 2nd-order RC averager, ~1.6MHz / ~0.8MHz poles
.subckt rc_lpf in out vss
r0 in net30 200e3
c0 net30 vss 500e-15
r1 net30 out 200e3
c1 out vss 1e-12
.ends rc_lpf
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcd_swap
** View name: schematic
** chopper: swap=0 a->outp b->outn ; swap=1 a->outn b->outp
.subckt dcd_swap a b swap swapb outp outn vdd vss
xi0 a outp swapb swap vdd vss dcc_tgate
xi1 b outn swapb swap vdd vss dcc_tgate
xi2 a outn swap swapb vdd vss dcc_tgate
xi3 b outp swap swapb vdd vss dcc_tgate
.ends dcd_swap
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: sa_comp
** View name: schematic
** StrongARM comparator + NAND SR latch. outp=1 when inp>inn
.subckt sa_comp inp inn clk outp outn vdd vss
m0 ntail clk vss vss nch l=40e-9 w=2e-6 m=1 nf=2
m1 nx1 inp ntail vss nch_lvt l=100e-9 w=4e-6 m=1 nf=4
m2 nx2 inn ntail vss nch_lvt l=100e-9 w=4e-6 m=1 nf=4
m3 sa_on sa_op nx1 vss nch l=30e-9 w=1e-6 m=1 nf=2
m4 sa_op sa_on nx2 vss nch l=30e-9 w=1e-6 m=1 nf=2
m5 sa_on sa_op vdd vdd pch l=30e-9 w=1e-6 m=1 nf=2
m6 sa_op sa_on vdd vdd pch l=30e-9 w=1e-6 m=1 nf=2
m7 sa_on clk vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m8 sa_op clk vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m9 nx1 clk vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m10 nx2 clk vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
xi0 sa_on outn outp vdd vss dcc_nand2
xi1 sa_op outp outn vdd vss dcc_nand2
.ends sa_comp
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcd
** View name: schematic
** duty-cycle detector: avg(clkout_p) vs avg(clkout_n), clocked compare
.subckt dcd ckp ckn cmp_clk dcd_en dcd_swap dcd_out dcd_outb vdd vss
xi0 ckp vavg_p vss rc_lpf
xi1 ckn vavg_n vss rc_lpf
m0 swapb dcd_swap vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m1 swapb dcd_swap vss vss nch l=30e-9 w=200e-9 m=1 nf=1
xi2 vavg_p vavg_n dcd_swap swapb net40 net41 vdd vss dcd_swap
** comparator clock gate: clk_g = cmp_clk & dcd_en
m2 net42 cmp_clk vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m3 net42 dcd_en vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m4 net42 cmp_clk net43 vss nch l=30e-9 w=400e-9 m=1 nf=1
m5 net43 dcd_en vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m6 clk_g net42 vdd vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m7 clk_g net42 vss vss nch l=30e-9 w=600e-9 m=1 nf=1
xi3 net40 net41 clk_g dcd_out dcd_outb vdd vss sa_comp
** extra filtering at comparator inputs (kickback)
c0 net40 vss 200e-15
c1 net41 vss 200e-15
.ends dcd
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_decap
** View name: schematic
.subckt dcc_decap vdd vss
m0 vss vdd vss vss nch l=1e-6 w=4e-6 m=24 nf=1
m1 vdd vss vdd vdd pch l=1e-6 w=4e-6 m=12 nf=1
.ends dcc_decap
** End of subcircuit definition.

** Library name: hsio_clk28
** Cell name: dcc_top
** View name: schematic
.subckt dcc_top clkin_p clkin_n clkout_p clkout_n cmp_clk clk_en dcc_en
+ dcc_sign dcc_mag<0> dcc_mag<1> dcc_mag<2> dcc_mag<3> dcc_mag<4> dcd_en
+ dcd_swap dcd_out dcd_outb ibias_25u vdd vss
xi0 ibias_25u clk_en nbias vdd vss dcc_bias
xi1 clkin_p clkin_n nbias clk_en ckp_rx vdd vss cml2cmos_rx
xi2 clkin_n clkin_p nbias clk_en ckn_rx vdd vss cml2cmos_rx
xi3 dcc_en dcc_sign dcc_mag<0> dcc_mag<1> dcc_mag<2> dcc_mag<3> dcc_mag<4>
+ a<0> a<1> a<2> a<3> a<4> ab<0> ab<1> ab<2> ab<3> ab<4> b<0> b<1> b<2> b<3>
+ b<4> bb<0> bb<1> bb<2> bb<3> bb<4> vdd vss dcc_code_dec
** p path: PU legs <- b (sign=0), PD legs <- a (sign=1)
xi4 ckp_rx clkout_p bb<0> bb<1> bb<2> bb<3> bb<4> a<0> a<1> a<2> a<3> a<4>
+ vdd vss dcc_path
** n path: opposite correction so clkout_n stays complementary
xi5 ckn_rx clkout_n ab<0> ab<1> ab<2> ab<3> ab<4> b<0> b<1> b<2> b<3> b<4>
+ vdd vss dcc_path
xi6 clkout_p clkout_n cmp_clk dcd_en dcd_swap dcd_out dcd_outb vdd vss dcd
xi7 vdd vss dcc_decap
xi8 vdd vss dcc_decap
.ends dcc_top
** End of subcircuit definition.
