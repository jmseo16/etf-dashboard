** Generated for: hspiceD
** Generated on: Nov 12 16:48:21 2026
** Design library name: hsio_tx28
** Design cell name: tx_top
** Design view name: schematic
** Note: device models (nch, pch, nch_lvt) are provided by the foundry PDK
**       model library, which is included by the testbench, not here.

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2

** Library name: hsio_tx28
** Cell name: dlatch
** View name: schematic
** C2MOS-style latch, transparent when clk=1 (q follows d)
.subckt dlatch d clk clkb q vdd vss
m0 net10 d vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m1 x clkb net10 vdd pch l=30e-9 w=600e-9 m=1 nf=1
m2 x clk net11 vss nch l=30e-9 w=400e-9 m=1 nf=1
m3 net11 d vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m4 net12 q vdd vdd pch l=30e-9 w=300e-9 m=1 nf=1
m5 x clk net12 vdd pch l=30e-9 w=300e-9 m=1 nf=1
m6 x clkb net13 vss nch l=30e-9 w=200e-9 m=1 nf=1
m7 net13 q vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m8 q x vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m9 q x vss vss nch l=30e-9 w=500e-9 m=1 nf=2
.ends dlatch
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: dff
** View name: schematic
** positive-edge master/slave flop
.subckt dff d clk clkb q qb vdd vss
xi0 d clkb clk qm vdd vss dlatch
xi1 qm clk clkb q vdd vss dlatch
m0 qb q vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m1 qb q vss vss nch l=30e-9 w=400e-9 m=1 nf=1
.ends dff
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: mux2to1
** View name: schematic
** half-rate 2:1 mux: out = d0 (clk=1), d1 (clk=0)
.subckt mux2to1 d0 d1 clk clkb out vdd vss
xi0 d0 clk clkb a net08 vdd vss dff
xi1 d1 clk clkb b1 net09 vdd vss dff
xi2 b1 clkb clk b vdd vss dlatch
m0 net014 a vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m1 nsel clkb net014 vdd pch l=30e-9 w=800e-9 m=1 nf=2
m2 nsel clk net015 vss nch l=30e-9 w=500e-9 m=1 nf=2
m3 net015 a vss vss nch l=30e-9 w=500e-9 m=1 nf=2
m4 net016 b vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m5 nsel clk net016 vdd pch l=30e-9 w=800e-9 m=1 nf=2
m6 nsel clkb net017 vss nch l=30e-9 w=500e-9 m=1 nf=2
m7 net017 b vss vss nch l=30e-9 w=500e-9 m=1 nf=2
m8 out nsel vdd vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m9 out nsel vss vss nch l=30e-9 w=800e-9 m=1 nf=2
.ends mux2to1
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: ser4to1
** View name: schematic
** 4:1 tree serializer, d0 first. out/outb complementary (tgate delay match)
.subckt ser4to1 d0 d1 d2 d3 ck2 ck2b ck4 ck4b out outb vdd vss
xi0 d0 d2 ck4 ck4b e0 vdd vss mux2to1
xi1 d1 d3 ck4 ck4b e1 vdd vss mux2to1
xi2 e0 e1 ck2 ck2b nser vdd vss mux2to1
m0 net020 nser vdd vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m1 net020 nser vss vss nch l=30e-9 w=800e-9 m=1 nf=2
m2 out net020 vdd vdd pch l=30e-9 w=2.4e-6 m=1 nf=4
m3 out net020 vss vss nch l=30e-9 w=1.6e-6 m=1 nf=4
m4 net021 vss nser vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m5 net021 vdd nser vss nch l=30e-9 w=800e-9 m=1 nf=2
m6 outb net021 vdd vdd pch l=30e-9 w=2.4e-6 m=1 nf=4
m7 outb net021 vss vss nch l=30e-9 w=1.6e-6 m=1 nf=4
.ends ser4to1
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_ffe_tapgen
** View name: schematic
** word-level shift: main=w2, pre={w1<0>,w2<3:1>}, post={w2<2:0>,w3<3>}
.subckt tx_ffe_tapgen din<0> din<1> din<2> din<3> ck ckb main<0> main<1>
+ main<2> main<3> pre<0> pre<1> pre<2> pre<3> post<0> post<1> post<2>
+ post<3> vdd vss
xi0 din<0> ck ckb pre<3> net030 vdd vss dff
xi1 din<1> ck ckb w1<1> net031 vdd vss dff
xi2 din<2> ck ckb w1<2> net032 vdd vss dff
xi3 din<3> ck ckb w1<3> net033 vdd vss dff
xi4 pre<3> ck ckb post<1> net034 vdd vss dff
xi5 w1<1> ck ckb post<2> net035 vdd vss dff
xi6 w1<2> ck ckb post<3> net036 vdd vss dff
xi7 w1<3> ck ckb pre<2> net037 vdd vss dff
xi8 pre<2> ck ckb post<0> net038 vdd vss dff
** w2<0>=post<1>, w2<1>=post<2>, w2<2>=post<3>, w2<3>=pre<2>
** main bits are buffered copies of w2 (separate load from tap nets)
m0 net040 post<1> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m1 net040 post<1> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m2 main<0> net040 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m3 main<0> net040 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m4 net041 post<2> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m5 net041 post<2> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m6 main<1> net041 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m7 main<1> net041 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m8 net042 post<3> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m9 net042 post<3> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m10 main<2> net042 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m11 main<2> net042 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m12 net043 pre<2> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m13 net043 pre<2> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m14 main<3> net043 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m15 main<3> net043 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
** pre<0>=w2<1>, pre<1>=w2<2> buffered
m16 net044 post<2> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m17 net044 post<2> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m18 pre<0> net044 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m19 pre<0> net044 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m20 net045 post<3> vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m21 net045 post<3> vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m22 pre<1> net045 vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m23 pre<1> net045 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
.ends tx_ffe_tapgen
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: cml2cmos
** View name: schematic
.subckt cml2cmos inp inn nbias out vdd vss
m0 net050 inp ntail vss nch_lvt l=40e-9 w=2e-6 m=1 nf=2
m1 outa inn ntail vss nch_lvt l=40e-9 w=2e-6 m=1 nf=2
m2 net050 net050 vdd vdd pch l=60e-9 w=1.5e-6 m=1 nf=2
m3 outa net050 vdd vdd pch l=60e-9 w=1.5e-6 m=1 nf=2
m4 ntail nbias vss vss nch l=500e-9 w=4e-6 m=2 nf=2
m5 net051 outa vdd vdd pch l=30e-9 w=1e-6 m=1 nf=2
m6 net051 outa vss vss nch l=30e-9 w=500e-9 m=1 nf=1
m7 out net051 vdd vdd pch l=30e-9 w=2.4e-6 m=1 nf=4
m8 out net051 vss vss nch l=30e-9 w=1.2e-6 m=1 nf=2
.ends cml2cmos
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_clkrx
** View name: schematic
** half-rate CML clock receiver: 100ohm diff term, CML buffer, CML->CMOS
.subckt tx_clkrx ckin_p ckin_n nbias ck2 ck2b vdd vss
r0 ckin_p ncm 50
r1 ckin_n ncm 50
c0 ncm vss 1e-12
m0 ob_n ckin_p ntail vss nch_lvt l=30e-9 w=6e-6 m=1 nf=6
m1 ob_p ckin_n ntail vss nch_lvt l=30e-9 w=6e-6 m=1 nf=6
r2 vdd ob_n 400
r3 vdd ob_p 400
m2 ntail nbias vss vss nch l=500e-9 w=8e-6 m=4 nf=4
xi0 ob_p ob_n nbias ck2 vdd vss cml2cmos
xi1 ob_n ob_p nbias ck2b vdd vss cml2cmos
.ends tx_clkrx
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_bias
** View name: schematic
** 50uA reference -> nbias (diode), forced low when bias_en=0
.subckt tx_bias ibias bias_en nbias vdd vss
r0 ibias nbias 200
m0 nbias nbias vss vss nch l=500e-9 w=4e-6 m=1 nf=2
m1 nbias bias_enb vss vss nch l=30e-9 w=1e-6 m=1 nf=1
m2 bias_enb bias_en vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m3 bias_enb bias_en vss vss nch l=30e-9 w=200e-9 m=1 nf=1
c0 nbias vss 2e-12
.ends tx_bias
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_ctrl_dec
** View name: schematic
** static control decode: output enable / eidle / segment enables / complements
.subckt tx_ctrl_dec oe eidle en_main<0> en_main<1> en_main<2> en_main<3>
+ sel_pre<0> sel_pre<1> sel_post<0> sel_post<1> sel_post<2> zcal_n<0>
+ zcal_n<1> en_m<0> en_m<1> en_m<2> en_m<3> enb_m<0> enb_m<1> enb_m<2>
+ enb_m<3> en_t enb_t selb_pre<0> selb_pre<1> selb_post<0> selb_post<1>
+ selb_post<2> znb<0> znb<1> keep_en keep_enb vdd vss
** keep_enb = !eidle ; keep_en = eidle (buffered)
m0 keep_enb eidle vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m1 keep_enb eidle vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m2 keep_en keep_enb vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m3 keep_en keep_enb vss vss nch l=30e-9 w=200e-9 m=1 nf=1
** enb_t = nand(oe, !eidle) ; en_t = !enb_t
m4 enb_t oe vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m5 enb_t keep_enb vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m6 enb_t oe net060 vss nch l=30e-9 w=400e-9 m=1 nf=1
m7 net060 keep_enb vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m8 en_t enb_t vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m9 en_t enb_t vss vss nch l=30e-9 w=400e-9 m=1 nf=1
** main segment enables: enb_m<k> = nand(en_main<k>, en_t)
m10 enb_m<0> en_main<0> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m11 enb_m<0> en_t vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m12 enb_m<0> en_main<0> net061 vss nch l=30e-9 w=400e-9 m=1 nf=1
m13 net061 en_t vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m14 en_m<0> enb_m<0> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m15 en_m<0> enb_m<0> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m16 enb_m<1> en_main<1> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m17 enb_m<1> en_t vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m18 enb_m<1> en_main<1> net062 vss nch l=30e-9 w=400e-9 m=1 nf=1
m19 net062 en_t vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m20 en_m<1> enb_m<1> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m21 en_m<1> enb_m<1> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m22 enb_m<2> en_main<2> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m23 enb_m<2> en_t vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m24 enb_m<2> en_main<2> net063 vss nch l=30e-9 w=400e-9 m=1 nf=1
m25 net063 en_t vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m26 en_m<2> enb_m<2> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m27 en_m<2> enb_m<2> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m28 enb_m<3> en_main<3> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m29 enb_m<3> en_t vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m30 enb_m<3> en_main<3> net064 vss nch l=30e-9 w=400e-9 m=1 nf=1
m31 net064 en_t vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m32 en_m<3> enb_m<3> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m33 en_m<3> enb_m<3> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
** tap select complements
m34 selb_pre<0> sel_pre<0> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m35 selb_pre<0> sel_pre<0> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m36 selb_pre<1> sel_pre<1> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m37 selb_pre<1> sel_pre<1> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m38 selb_post<0> sel_post<0> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m39 selb_post<0> sel_post<0> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m40 selb_post<1> sel_post<1> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m41 selb_post<1> sel_post<1> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m42 selb_post<2> sel_post<2> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m43 selb_post<2> sel_post<2> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
** pull-down impedance code complements
m44 znb<0> zcal_n<0> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m45 znb<0> zcal_n<0> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m46 znb<1> zcal_n<1> vdd vdd pch l=30e-9 w=400e-9 m=1 nf=1
m47 znb<1> zcal_n<1> vss vss nch l=30e-9 w=200e-9 m=1 nf=1
.ends tx_ctrl_dec
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_tapmux
** View name: schematic
** out = d0 (sel=0), d1 (sel=1)
.subckt tx_tapmux d0 d1 sel selb out vdd vss
m0 net070 d0 vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m1 net072 sel net070 vdd pch l=30e-9 w=800e-9 m=1 nf=2
m2 net072 selb net071 vss nch l=30e-9 w=500e-9 m=1 nf=2
m3 net071 d0 vss vss nch l=30e-9 w=500e-9 m=1 nf=2
m4 net073 d1 vdd vdd pch l=30e-9 w=800e-9 m=1 nf=2
m5 net072 selb net073 vdd pch l=30e-9 w=800e-9 m=1 nf=2
m6 net072 sel net074 vss nch l=30e-9 w=500e-9 m=1 nf=2
m7 net074 d1 vss vss nch l=30e-9 w=500e-9 m=1 nf=2
m8 out net072 vdd vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m9 out net072 vss vss nch l=30e-9 w=800e-9 m=1 nf=2
.ends tx_tapmux
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_predrv
** View name: schematic
** tapered CMOS pre-driver, non-inverting (FO~3 taper)
.subckt tx_predrv in out vdd vss
m0 net080 in vdd vdd pch l=30e-9 w=600e-9 m=1 nf=1
m1 net080 in vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m2 net081 net080 vdd vdd pch l=30e-9 w=1.8e-6 m=1 nf=2
m3 net081 net080 vss vss nch l=30e-9 w=1.2e-6 m=1 nf=2
m4 net082 net081 vdd vdd pch l=30e-9 w=5.4e-6 m=1 nf=6
m5 net082 net081 vss vss nch l=30e-9 w=3.6e-6 m=1 nf=4
m6 out net082 vdd vdd pch l=30e-9 w=16e-6 m=1 nf=16
m7 out net082 vss vss nch l=30e-9 w=10.8e-6 m=1 nf=12
.ends tx_predrv
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: sst_slice
** View name: schematic
** unit SST driver slice (~1.25k ohm per leg at mid zcal), hi-Z when en=0
.subckt sst_slice d en enb zp0 zp1 znb0 znb1 out vddq vss
** pull-up gate: nand2(d,en), nand3(d,en,zp0), nand3(d,en,zp1)
m0 gpu0 d vddq vddq pch l=30e-9 w=400e-9 m=1 nf=1
m1 gpu0 en vddq vddq pch l=30e-9 w=400e-9 m=1 nf=1
m2 gpu0 d net090 vss nch l=30e-9 w=400e-9 m=1 nf=1
m3 net090 en vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m4 gpu1 d vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m5 gpu1 en vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m6 gpu1 zp0 vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m7 gpu1 d net091 vss nch l=30e-9 w=400e-9 m=1 nf=1
m8 net091 en net092 vss nch l=30e-9 w=400e-9 m=1 nf=1
m9 net092 zp0 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
m10 gpu2 d vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m11 gpu2 en vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m12 gpu2 zp1 vddq vddq pch l=30e-9 w=300e-9 m=1 nf=1
m13 gpu2 d net093 vss nch l=30e-9 w=400e-9 m=1 nf=1
m14 net093 en net094 vss nch l=30e-9 w=400e-9 m=1 nf=1
m15 net094 zp1 vss vss nch l=30e-9 w=400e-9 m=1 nf=1
** pull-down gate: nor2(d,enb), nor3(d,enb,znb0), nor3(d,enb,znb1)
m16 net095 d vddq vddq pch l=30e-9 w=800e-9 m=1 nf=2
m17 gpd0 enb net095 vddq pch l=30e-9 w=800e-9 m=1 nf=2
m18 gpd0 d vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m19 gpd0 enb vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m20 net096 d vddq vddq pch l=30e-9 w=900e-9 m=1 nf=2
m21 net097 enb net096 vddq pch l=30e-9 w=900e-9 m=1 nf=2
m22 gpd1 znb0 net097 vddq pch l=30e-9 w=900e-9 m=1 nf=2
m23 gpd1 d vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m24 gpd1 enb vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m25 gpd1 znb0 vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m26 net098 d vddq vddq pch l=30e-9 w=900e-9 m=1 nf=2
m27 net099 enb net098 vddq pch l=30e-9 w=900e-9 m=1 nf=2
m28 gpd2 znb1 net099 vddq pch l=30e-9 w=900e-9 m=1 nf=2
m29 gpd2 d vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m30 gpd2 enb vss vss nch l=30e-9 w=200e-9 m=1 nf=1
m31 gpd2 znb1 vss vss nch l=30e-9 w=200e-9 m=1 nf=1
** output legs: base + binary zcal fingers, separate series R for PU / PD
m32 npu gpu0 vddq vddq pch l=30e-9 w=1.6e-6 m=1 nf=2
m33 npu gpu1 vddq vddq pch l=30e-9 w=400e-9 m=1 nf=1
m34 npu gpu2 vddq vddq pch l=30e-9 w=800e-9 m=1 nf=1
m35 npd gpd0 vss vss nch l=30e-9 w=1e-6 m=1 nf=2
m36 npd gpd1 vss vss nch l=30e-9 w=250e-9 m=1 nf=1
m37 npd gpd2 vss vss nch l=30e-9 w=500e-9 m=1 nf=1
r0 npu out 900
r1 npd out 900
.ends sst_slice
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_pad_esd
** View name: schematic
** primary pad ESD: GGNMOS to vss, gate-tied PMOS to vddq, pad parasitic
.subckt tx_pad_esd pad vddq vss
m0 pad ngate vss vss nch l=150e-9 w=40e-6 m=1 nf=20
r0 ngate vss 5000
m1 pad pgate vddq vddq pch l=150e-9 w=60e-6 m=1 nf=30
r1 pgate vddq 5000
c0 pad vss 120e-15
.ends tx_pad_esd
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: esd_rc_clamp
** View name: schematic
** RC-triggered rail clamp (tau ~ 200ns)
.subckt esd_rc_clamp vdd vss
r0 vdd ntrig 100e3
c0 ntrig vss 2e-12
m0 ngc ntrig vdd vdd pch l=60e-9 w=20e-6 m=1 nf=10
m1 ngc ntrig vss vss nch l=60e-9 w=5e-6 m=1 nf=4
m2 vdd ngc vss vss nch l=60e-9 w=20e-6 m=50 nf=20
.ends esd_rc_clamp
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_drv_pad
** View name: schematic
** one single-ended SST output: 15u main + 3u pre + 7u post slices (25 units)
.subckt tx_drv_pad dm dpre dpost en_m<0> en_m<1> en_m<2> en_m<3> enb_m<0>
+ enb_m<1> enb_m<2> enb_m<3> en_t enb_t sel_pre<0> sel_pre<1> selb_pre<0>
+ selb_pre<1> sel_post<0> sel_post<1> sel_post<2> selb_post<0> selb_post<1>
+ selb_post<2> zp<0> zp<1> znb<0> znb<1> keep_en keep_enb pad vdd vddq vss
** main tap: dummy tapmux for delay matching, sel tied low
xi0 dm dm vss vdd net0100 vdd vss tx_tapmux
xi1 net0100 dmain_pd vddq vss tx_predrv m=4
xi2 dmain_pd en_m<0> enb_m<0> zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=1
xi3 dmain_pd en_m<1> enb_m<1> zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=2
xi4 dmain_pd en_m<2> enb_m<2> zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=4
xi5 dmain_pd en_m<3> enb_m<3> zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=8
** pre-cursor slices: each code bit steers its slices to main (0) or pre (1)
xi6 dm dpre sel_pre<0> selb_pre<0> net0101 vdd vss tx_tapmux
xi7 net0101 dpre_pd<0> vddq vss tx_predrv m=1
xi8 dpre_pd<0> en_t enb_t zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=1
xi9 dm dpre sel_pre<1> selb_pre<1> net0102 vdd vss tx_tapmux
xi10 net0102 dpre_pd<1> vddq vss tx_predrv m=1
xi11 dpre_pd<1> en_t enb_t zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=2
** post-cursor slices
xi12 dm dpost sel_post<0> selb_post<0> net0103 vdd vss tx_tapmux
xi13 net0103 dpost_pd<0> vddq vss tx_predrv m=1
xi14 dpost_pd<0> en_t enb_t zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=1
xi15 dm dpost sel_post<1> selb_post<1> net0104 vdd vss tx_tapmux
xi16 net0104 dpost_pd<1> vddq vss tx_predrv m=1
xi17 dpost_pd<1> en_t enb_t zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=2
xi18 dm dpost sel_post<2> selb_post<2> net0105 vdd vss tx_tapmux
xi19 net0105 dpost_pd<2> vddq vss tx_predrv m=2
xi20 dpost_pd<2> en_t enb_t zp<0> zp<1> znb<0> znb<1> drv_out vddq vss sst_slice m=4
** electrical-idle common-mode keeper (~vddq/2 through 2k||2k)
m0 net0106 keep_enb vddq vddq pch l=30e-9 w=2e-6 m=1 nf=2
r0 net0106 drv_out 2000
m1 net0107 keep_en vss vss nch l=30e-9 w=1e-6 m=1 nf=1
r1 net0107 drv_out 2000
** CDM series resistor + pad ESD
r2 drv_out pad 10
xi21 pad vddq vss tx_pad_esd
.ends tx_drv_pad
** End of subcircuit definition.

** Library name: hsio_tx28
** Cell name: tx_top
** View name: schematic
.subckt tx_top din<0> din<1> din<2> din<3> ckhr_p ckhr_n clk_div4 txp txn oe
+ eidle en_main<0> en_main<1> en_main<2> en_main<3> sel_pre<0> sel_pre<1>
+ sel_post<0> sel_post<1> sel_post<2> zcal_p<0> zcal_p<1> zcal_n<0>
+ zcal_n<1> bias_en ibias_50u vdd vddq vss
** bias + clock receive + /2 (half-rate -> quarter-rate)
xi0 ibias_50u bias_en nbias vdd vss tx_bias
xi1 ckhr_p ckhr_n nbias ck2 ck2b vdd vss tx_clkrx
xi2 ck4b ck2 ck2b ck4 ck4b vdd vss dff
m0 net0110 ck4 vdd vdd pch l=30e-9 w=1.2e-6 m=1 nf=2
m1 net0110 ck4 vss vss nch l=30e-9 w=800e-9 m=1 nf=2
m2 clk_div4 net0110 vdd vdd pch l=30e-9 w=4.8e-6 m=1 nf=4
m3 clk_div4 net0110 vss vss nch l=30e-9 w=3.2e-6 m=1 nf=4
** FFE tap data generation (retimed on ck4 falling edge)
xi3 din<0> din<1> din<2> din<3> ck4b ck4 main<0> main<1> main<2> main<3>
+ pre<0> pre<1> pre<2> pre<3> post<0> post<1> post<2> post<3> vdd vss
+ tx_ffe_tapgen
** 4:1 serializers, one per tap
xi4 main<0> main<1> main<2> main<3> ck2 ck2b ck4 ck4b main_p main_n vdd vss ser4to1
xi5 pre<0> pre<1> pre<2> pre<3> ck2 ck2b ck4 ck4b pre_p pre_n vdd vss ser4to1
xi6 post<0> post<1> post<2> post<3> ck2 ck2b ck4 ck4b post_p post_n vdd vss ser4to1
** control decode
xi7 oe eidle en_main<0> en_main<1> en_main<2> en_main<3> sel_pre<0> sel_pre<1>
+ sel_post<0> sel_post<1> sel_post<2> zcal_n<0> zcal_n<1> en_m<0> en_m<1>
+ en_m<2> en_m<3> enb_m<0> enb_m<1> enb_m<2> enb_m<3> en_t enb_t selb_pre<0>
+ selb_pre<1> selb_post<0> selb_post<1> selb_post<2> znb<0> znb<1> keep_en
+ keep_enb vdd vss tx_ctrl_dec
** output drivers: pre/post taps fed with inverted polarity (negative taps)
xi8 main_p pre_n post_n en_m<0> en_m<1> en_m<2> en_m<3> enb_m<0> enb_m<1>
+ enb_m<2> enb_m<3> en_t enb_t sel_pre<0> sel_pre<1> selb_pre<0> selb_pre<1>
+ sel_post<0> sel_post<1> sel_post<2> selb_post<0> selb_post<1> selb_post<2>
+ zcal_p<0> zcal_p<1> znb<0> znb<1> keep_en keep_enb txp vdd vddq vss tx_drv_pad
xi9 main_n pre_p post_p en_m<0> en_m<1> en_m<2> en_m<3> enb_m<0> enb_m<1>
+ enb_m<2> enb_m<3> en_t enb_t sel_pre<0> sel_pre<1> selb_pre<0> selb_pre<1>
+ sel_post<0> sel_post<1> sel_post<2> selb_post<0> selb_post<1> selb_post<2>
+ zcal_p<0> zcal_p<1> znb<0> znb<1> keep_en keep_enb txn vdd vddq vss tx_drv_pad
** rail clamps
xi10 vddq vss esd_rc_clamp
xi11 vdd vss esd_rc_clamp
** MOS decap
m4 vss vdd vss vss nch l=1e-6 w=5e-6 m=40 nf=1
m5 vss vddq vss vss nch l=1e-6 w=5e-6 m=80 nf=1
.ends tx_top
** End of subcircuit definition.
