** Generated for: hspiceD
** Generated on: Nov 22 14:12:38 2026
** Design library name: pod_rx2
** Design cell name: dq_rx_ct
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: pod_std
** Cell name: inv_a
** View name: schematic
.subckt inv_a a y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mn0 y a vss vss nch w=160n l=30n m=1
.ends inv_a
** End of subcircuit definition.

** Library name: pod_std
** Cell name: inv_c
** View name: schematic
.subckt inv_c a y vdd vss
mp0 y a vdd vdd pch_lvt w=960n l=30n m=2
mn0 y a vss vss nch_lvt w=480n l=30n m=2
.ends inv_c
** End of subcircuit definition.

** Library name: pod_std
** Cell name: nand2_a
** View name: schematic
.subckt nand2_a a b y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mp1 y b vdd vdd pch w=320n l=30n m=1
mn0 y a net5 vss nch w=320n l=30n m=1
mn1 net5 b vss vss nch w=320n l=30n m=1
.ends nand2_a
** End of subcircuit definition.

** Library name: pod_std
** Cell name: nand2_c
** View name: schematic
.subckt nand2_c a b y vdd vss
mp0 y a vdd vdd pch_lvt w=640n l=30n m=2
mp1 y b vdd vdd pch_lvt w=640n l=30n m=2
mn0 y a net5 vss nch_lvt w=640n l=30n m=2
mn1 net5 b vss vss nch_lvt w=640n l=30n m=2
.ends nand2_c
** End of subcircuit definition.

** Library name: pod_std
** Cell name: ls_lh2
** View name: schematic
.subckt ls_lh2 in out outb vdd vddq vss
mp2 inb in vdd vdd pch w=320n l=30n m=1
mn2 inb in vss vss nch w=160n l=30n m=1
mn0 nb in vss vss nch_18 w=1.2u l=150n m=1
mn1 nq inb vss vss nch_18 w=1.2u l=150n m=1
mp0 nb nq vddq vddq pch_18 w=400n l=150n m=1
mp1 nq nb vddq vddq pch_18 w=400n l=150n m=1
mp3 out nb vddq vddq pch_18 w=1.6u l=100n m=1
mn3 out nb vss vss nch_18 w=800n l=100n m=1
mp4 outb nq vddq vddq pch_18 w=1.6u l=100n m=1
mn4 outb nq vss vss nch_18 w=800n l=100n m=1
.ends ls_lh2
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: esd_gc
** View name: schematic
.subckt esd_gc pad pad_r vddq vssq
d0 pad vddq pdio_esd area=60p pj=64u
d1 vssq pad ndio_esd area=60p pj=64u
r0 pad pad_r 200
mn0 pad_r net9 vssq vssq nch_18 w=20u l=150n m=2
c0 pad_r net9 150f
r1 net9 vssq 8k
mp0 pad_r net10 vddq vddq pch_18 w=20u l=150n m=2
r2 net10 vddq 8k
.ends esd_gc
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: odt_ct
** View name: schematic
.subckt odt_ct pad enb<2> enb<1> enb<0> en<2> en<1> en<0> vddq vssq
mp2 net12 enb<2> vddq vddq pch_18 w=24u l=100n m=4
r2 net12 pad 120
mp1 net11 enb<1> vddq vddq pch_18 w=24u l=100n m=2
r1 net11 pad 240
mp0 net10 enb<0> vddq vddq pch_18 w=24u l=100n m=1
r0 net10 pad 480
mn2 net15 en<2> vssq vssq nch_18 w=12u l=100n m=4
r5 net15 pad 120
mn1 net14 en<1> vssq vssq nch_18 w=12u l=100n m=2
r4 net14 pad 240
mn0 net13 en<0> vssq vssq nch_18 w=12u l=100n m=1
r3 net13 pad 480
.ends odt_ct
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: odt_dec2
** View name: schematic
.subckt odt_dec2 odt_en rtt<2> rtt<1> rtt<0> enb<2> enb<1> enb<0> en<2> en<1> en<0> vdd vddq vss
xi5 net20 enb<2> en<2> vdd vddq vss ls_lh2
xi4 net21 enb<1> en<1> vdd vddq vss ls_lh2
xi3 net22 enb<0> en<0> vdd vddq vss ls_lh2
xi2 odt_en rtt<2> net20 vdd vss nand2_a
xi1 odt_en rtt<1> net21 vdd vss nand2_a
xi0 odt_en rtt<0> net22 vdd vss nand2_a
.ends odt_dec2
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: rx_bias
** View name: schematic
.subckt rx_bias ibias en vbn_q vdd vddq vss vssq
xi0 en enb vdd vss inv_a
mn0 ibias ibias vss vss nch w=1u l=240n m=4
mn1 net30 ibias vss vss nch w=1u l=240n m=4
mp0 net30 net30 vddq vddq pch_18 w=2u l=400n m=4
mp1 vbn_q net30 vddq vddq pch_18 w=2u l=400n m=4
mn2 vbn_q vbn_q vssq vssq nch_18 w=2u l=400n m=4
mn3 ibias enb vss vss nch w=400n l=30n m=1
mn4 vbn_q enb vssq vssq nch_18 w=800n l=150n m=1
.ends rx_bias
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: rx_pre
** View name: schematic
.subckt rx_pre inp vref lbp lbn sel_m sel_l vbn outp outn vddq vssq
r0 vddq outn 800
r1 vddq outp 800
mn0 outn inp net40 vssq nch_18 w=4u l=100n m=2
mn1 outp vref net40 vssq nch_18 w=4u l=100n m=2
mn8 outp inp outp vssq nch_18 w=1u l=100n m=1
mn9 outn vref outn vssq nch_18 w=1u l=100n m=1
mn2 net40 sel_m net41 vssq nch_18 w=8u l=100n m=1
mn3 net41 vbn vssq vssq nch_18 w=8u l=400n m=2
mn4 outn lbp net42 vssq nch_18 w=4u l=100n m=2
mn5 outp lbn net42 vssq nch_18 w=4u l=100n m=2
mn6 net42 sel_l net43 vssq nch_18 w=8u l=100n m=1
mn7 net43 vbn vssq vssq nch_18 w=8u l=400n m=2
.ends rx_pre
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: dfe_sum5
** View name: schematic
.subckt dfe_sum5 inp inn hp hn tap<4> tap<3> tap<2> tap<1> tap<0> sgn sgnb en vbn outp outn vdd vss
r0 vdd outn 600
r1 vdd outp 600
mn0 outn inp net50 vss nch_lvt w=2u l=30n m=2
mn1 outp inn net50 vss nch_lvt w=2u l=30n m=2
mn2 net50 en net51 vss nch w=4u l=30n m=1
mn3 net51 vbn vss vss nch w=1u l=240n m=8
mn4 net52 hp net54 vss nch_lvt w=1u l=30n m=1
mn5 net53 hn net54 vss nch_lvt w=1u l=30n m=1
mn6 outp sgnb net52 vss nch_lvt w=1u l=30n m=1
mn7 outn sgnb net53 vss nch_lvt w=1u l=30n m=1
mn8 outn sgn net52 vss nch_lvt w=1u l=30n m=1
mn9 outp sgn net53 vss nch_lvt w=1u l=30n m=1
mn18 net54 tap<4> net59 vss nch w=400n l=30n m=16
mn19 net59 vbn vss vss nch w=1u l=240n m=16
mn10 net54 tap<3> net58 vss nch w=400n l=30n m=8
mn11 net58 vbn vss vss nch w=1u l=240n m=8
mn12 net54 tap<2> net57 vss nch w=400n l=30n m=4
mn13 net57 vbn vss vss nch w=1u l=240n m=4
mn14 net54 tap<1> net56 vss nch w=400n l=30n m=2
mn15 net56 vbn vss vss nch w=1u l=240n m=2
mn16 net54 tap<0> net55 vss nch w=400n l=30n m=1
mn17 net55 vbn vss vss nch w=1u l=240n m=1
.ends dfe_sum5
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: sa_sarm
** View name: schematic
.subckt sa_sarm inp inn ck outp outn ofp<2> ofp<1> ofp<0> ofn<2> ofn<1> ofn<0> vdd vss
mn0 net61 ck vss vss nch_lvt w=3u l=30n m=2
mn1 net62 inp net61 vss nch_lvt w=2u l=30n m=2
mn2 net63 inn net61 vss nch_lvt w=2u l=30n m=2
mn3 outn outp net62 vss nch_lvt w=1u l=30n m=1
mn4 outp outn net63 vss nch_lvt w=1u l=30n m=1
mp0 outn outp vdd vdd pch_lvt w=1u l=30n m=1
mp1 outp outn vdd vdd pch_lvt w=1u l=30n m=1
mp2 outn ck vdd vdd pch_lvt w=500n l=30n m=1
mp3 outp ck vdd vdd pch_lvt w=500n l=30n m=1
mp4 net62 ck vdd vdd pch_lvt w=500n l=30n m=1
mp5 net63 ck vdd vdd pch_lvt w=500n l=30n m=1
mn5 net62 ofn<2> net66 vss nch w=200n l=30n m=4
mn6 vss net66 vss vss nch w=400n l=200n m=4
mn7 net62 ofn<1> net65 vss nch w=200n l=30n m=2
mn8 vss net65 vss vss nch w=400n l=200n m=2
mn9 net62 ofn<0> net64 vss nch w=200n l=30n m=1
mn10 vss net64 vss vss nch w=400n l=200n m=1
mn11 net63 ofp<2> net69 vss nch w=200n l=30n m=4
mn12 vss net69 vss vss nch w=400n l=200n m=4
mn13 net63 ofp<1> net68 vss nch w=200n l=30n m=2
mn14 vss net68 vss vss nch w=400n l=200n m=2
mn15 net63 ofp<0> net67 vss nch w=200n l=30n m=1
mn16 vss net67 vss vss nch w=400n l=200n m=1
.ends sa_sarm
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: sr_nand
** View name: schematic
.subckt sr_nand sb rb q qb vdd vss
xi0 sb qb q vdd vss nand2_c
xi1 rb q qb vdd vss nand2_c
.ends sr_nand
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: ck_gbuf
** View name: schematic
.subckt ck_gbuf ck ckb en cko ckob vdd vss
xi0 ck en net70 vdd vss nand2_c
xi1 ckb en net71 vdd vss nand2_c
xi2 net70 cko vdd vss inv_c
xi3 net71 ckob vdd vss inv_c
.ends ck_gbuf
** End of subcircuit definition.

** Library name: pod_rx2
** Cell name: dq_rx_ct
** View name: schematic
.subckt dq_rx_ct pad vref ck ckb lb_p lb_n lb_en rx_en odt_en rtt<2> rtt<1> rtt<0> tap<4> tap<3> tap<2> tap<1> tap<0> tap_sgn ofe_p<2> ofe_p<1> ofe_p<0> ofe_n<2> ofe_n<1> ofe_n<0> ofo_p<2> ofo_p<1> ofo_p<0> ofo_n<2> ofo_n<1> ofo_n<0> ibias dout_e dout_o vdd vddq vss vssq
xi20 pad net1 vddq vssq esd_gc
xi21 pad net2<2> net2<1> net2<0> net5<2> net5<1> net5<0> vddq vssq odt_ct
xi22 odt_en rtt<2> rtt<1> rtt<0> net2<2> net2<1> net2<0> net5<2> net5<1> net5<0> vdd vddq vss odt_dec2
r0 vref net3 5k
mn0 vssq net3 vssq vssq nch_18 w=10u l=2u m=4
xi23 ibias rx_en net4 vdd vddq vss vssq rx_bias
xi0 lb_en net100 vdd vss inv_a
xi1 rx_en net100 net101 vdd vss nand2_a
xi2 net101 net102 vdd vss inv_a
xi3 rx_en lb_en net103 vdd vss nand2_a
xi4 net103 net104 vdd vss inv_a
xi5 tap_sgn net105 vdd vss inv_a
xi6 net105 net106 vdd vss inv_a
xi24 net1 net3 lb_p lb_n net102 net104 net4 net6 net7 vddq vssq rx_pre
xi25 ck ckb rx_en net8 net9 vdd vss ck_gbuf
d0 vss net8 ndio_ant area=0.12p pj=1.4u
d1 vss net9 ndio_ant area=0.12p pj=1.4u
xi26 net6 net7 net16 net17 tap<4> tap<3> tap<2> tap<1> tap<0> net106 net105 rx_en ibias net10 net11 vdd vss dfe_sum5
xi27 net6 net7 net14 net15 tap<4> tap<3> tap<2> tap<1> tap<0> net106 net105 rx_en ibias net12 net13 vdd vss dfe_sum5
xi28 net10 net11 net8 net18 net19 ofe_p<2> ofe_p<1> ofe_p<0> ofe_n<2> ofe_n<1> ofe_n<0> vdd vss sa_sarm
xi29 net12 net13 net9 net24 net25 ofo_p<2> ofo_p<1> ofo_p<0> ofo_n<2> ofo_n<1> ofo_n<0> vdd vss sa_sarm
xi30 net19 net18 net14 net15 vdd vss sr_nand
xi31 net25 net24 net16 net17 vdd vss sr_nand
xi7 net14 net26 vdd vss inv_a
xi8 net26 dout_e vdd vss inv_c
xi9 net15 net27 vdd vss inv_a
xi10 net16 net28 vdd vss inv_a
xi11 net28 dout_o vdd vss inv_c
xi12 net17 net29 vdd vss inv_a
.ends dq_rx_ct
** End of subcircuit definition.

.END
