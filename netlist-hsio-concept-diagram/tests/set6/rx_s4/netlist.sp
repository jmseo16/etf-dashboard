** Generated for: hspiceD
** Generated on: Nov 22 14:12:39 2026
** Design library name: pod_rx
** Design cell name: dqrx_eq
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
** Cell name: nor2_c
** View name: schematic
.subckt nor2_c a b y vdd vss
mp0 net7 a vdd vdd pch_lvt w=960n l=30n m=1
mp1 y b net7 vdd pch_lvt w=960n l=30n m=1
mn0 y a vss vss nch_lvt w=240n l=30n m=1
mn1 y b vss vss nch_lvt w=240n l=30n m=1
.ends nor2_c
** End of subcircuit definition.

** Library name: pod_std
** Cell name: ls_lh
** View name: schematic
.subckt ls_lh in out vdd vddq vss
mp2 inb in vdd vdd pch w=320n l=30n m=1
mn2 inb in vss vss nch w=160n l=30n m=1
mn0 nb in vss vss nch_18 w=1.2u l=150n m=1
mn1 nq inb vss vss nch_18 w=1.2u l=150n m=1
mp0 nb nq vddq vddq pch_18 w=400n l=150n m=1
mp1 nq nb vddq vddq pch_18 w=400n l=150n m=1
mp3 out nb vddq vddq pch_18 w=1.6u l=100n m=1
mn3 out nb vss vss nch_18 w=800n l=100n m=1
.ends ls_lh
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: esd_dq
** View name: schematic
.subckt esd_dq pad pad_r vddq vssq
d0 pad vddq pdio_esd area=60p pj=64u
d1 vssq pad ndio_esd area=60p pj=64u
r0 pad pad_r 150
d2 pad_r vddq pdio_esd area=6p pj=14u
d3 vssq pad_r ndio_esd area=6p pj=14u
mn0 pad_r net9 vssq vssq nch_18 w=20u l=150n m=2
r1 net9 vssq 10k
.ends esd_dq
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: odt_pu
** View name: schematic
.subckt odt_pu pad enb<2> enb<1> enb<0> vddq
mp2 net12 enb<2> vddq vddq pch_18 w=24u l=100n m=4
r2 net12 pad 60
mp1 net11 enb<1> vddq vddq pch_18 w=24u l=100n m=2
r1 net11 pad 120
mp0 net10 enb<0> vddq vddq pch_18 w=24u l=100n m=1
r0 net10 pad 240
.ends odt_pu
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: odt_dec
** View name: schematic
.subckt odt_dec odt_en rtt<2> rtt<1> rtt<0> enb<2> enb<1> enb<0> vdd vddq vss
xi5 net20 enb<2> vdd vddq vss ls_lh
xi4 net21 enb<1> vdd vddq vss ls_lh
xi3 net22 enb<0> vdd vddq vss ls_lh
xi2 odt_en rtt<2> net20 vdd vss nand2_a
xi1 odt_en rtt<1> net21 vdd vss nand2_a
xi0 odt_en rtt<0> net22 vdd vss nand2_a
.ends odt_dec
** End of subcircuit definition.

** Library name: pod_rx
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

** Library name: pod_rx
** Cell name: rx_pre_dg
** View name: schematic
.subckt rx_pre_dg inp vref lbp lbn sel_m sel_l pk<1> pk<0> vbn outp outn vddq vssq
r0 vddq outn 1.2k
r1 vddq outp 1.2k
mp0 outn vssq vddq vddq pch_18 w=1u l=150n m=1
mp1 outp vssq vddq vddq pch_18 w=1u l=150n m=1
mn0 outn inp net40 vssq nch_18 w=4u l=100n m=2
mn1 outp vref net44 vssq nch_18 w=4u l=100n m=2
r2 net40 net44 300
mn2 net40 sel_m net41 vssq nch_18 w=4u l=100n m=1
mn3 net41 vbn vssq vssq nch_18 w=8u l=400n m=1
mn10 net44 sel_m net45 vssq nch_18 w=4u l=100n m=1
mn11 net45 vbn vssq vssq nch_18 w=8u l=400n m=1
mn12 net40 pk<1> net46 vssq nch_18 w=2u l=150n m=2
c0 net46 net44 400f
mn13 net40 pk<0> net47 vssq nch_18 w=2u l=150n m=1
c1 net47 net44 200f
mn4 outn lbp net42 vssq nch_18 w=4u l=100n m=2
mn5 outp lbn net42 vssq nch_18 w=4u l=100n m=2
mn6 net42 sel_l net43 vssq nch_18 w=8u l=100n m=1
mn7 net43 vbn vssq vssq nch_18 w=8u l=400n m=2
.ends rx_pre_dg
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: dfe_sum3
** View name: schematic
.subckt dfe_sum3 inp inn hp hn tap<2> tap<1> tap<0> sgn sgnb en vbn outp outn vdd vss
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
xi0 tap<2> net55 vdd vss inv_a
xi1 tap<1> net56 vdd vss inv_a
xi2 tap<0> net57 vdd vss inv_a
mn10 vbn tap<2> net58 vss nch w=400n l=30n m=1
mp10 vbn net55 net58 vdd pch w=400n l=30n m=1
mn11 net58 net55 vss vss nch w=200n l=30n m=1
mn12 net54 net58 vss vss nch w=1u l=240n m=4
mn13 vbn tap<1> net59 vss nch w=400n l=30n m=1
mp13 vbn net56 net59 vdd pch w=400n l=30n m=1
mn14 net59 net56 vss vss nch w=200n l=30n m=1
mn15 net54 net59 vss vss nch w=1u l=240n m=2
mn16 vbn tap<0> net60 vss nch w=400n l=30n m=1
mp16 vbn net57 net60 vdd pch w=400n l=30n m=1
mn17 net60 net57 vss vss nch w=200n l=30n m=1
mn18 net54 net60 vss vss nch w=1u l=240n m=1
.ends dfe_sum3
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: sa_ci
** View name: schematic
.subckt sa_ci inp inn ck outp outn of<2> of<1> of<0> ofs vdd vss
xi0 ck net60 vdd vss inv_c
mn0 net61 ck vss vss nch_lvt w=2u l=30n m=2
mn1 net62 inp net61 vss nch_lvt w=2u l=30n m=2
mn2 net63 inn net61 vss nch_lvt w=2u l=30n m=2
mp0 net62 ck vdd vdd pch_lvt w=1u l=30n m=1
mp1 net63 ck vdd vdd pch_lvt w=1u l=30n m=1
mp2 net64 net60 vdd vdd pch_lvt w=4u l=30n m=1
mp3 outp outn net64 vdd pch_lvt w=1u l=30n m=1
mp4 outn outp net64 vdd pch_lvt w=1u l=30n m=1
mn3 outp outn vss vss nch_lvt w=500n l=30n m=1
mn4 outn outp vss vss nch_lvt w=500n l=30n m=1
mn5 outp net62 vss vss nch_lvt w=1u l=30n m=1
mn6 outn net63 vss vss nch_lvt w=1u l=30n m=1
xi1 ofs net65 vdd vss inv_a
xi2 of<2> ofs net70 vdd vss nand2_a
xi3 net70 net71 vdd vss inv_a
xi4 of<2> net65 net72 vdd vss nand2_a
xi5 net72 net73 vdd vss inv_a
xi6 of<1> ofs net74 vdd vss nand2_a
xi7 net74 net75 vdd vss inv_a
xi8 of<1> net65 net76 vdd vss nand2_a
xi9 net76 net77 vdd vss inv_a
xi10 of<0> ofs net78 vdd vss nand2_a
xi11 net78 net79 vdd vss inv_a
xi12 of<0> net65 net80 vdd vss nand2_a
xi13 net80 net81 vdd vss inv_a
mn7 net62 net73 net61 vss nch w=200n l=60n m=4
mn8 net63 net71 net61 vss nch w=200n l=60n m=4
mn9 net62 net77 net61 vss nch w=200n l=60n m=2
mn10 net63 net75 net61 vss nch w=200n l=60n m=2
mn11 net62 net81 net61 vss nch w=200n l=60n m=1
mn12 net63 net79 net61 vss nch w=200n l=60n m=1
.ends sa_ci
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: sr_nor
** View name: schematic
.subckt sr_nor s r q qb vdd vss
xi0 r qb q vdd vss nor2_c
xi1 s q qb vdd vss nor2_c
.ends sr_nor
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: ck_gbuf
** View name: schematic
.subckt ck_gbuf ck ckb en cko ckob vdd vss
xi0 ck en net70 vdd vss nand2_c
xi1 ckb en net71 vdd vss nand2_c
xi2 net70 cko vdd vss inv_c
xi3 net71 ckob vdd vss inv_c
.ends ck_gbuf
** End of subcircuit definition.

** Cell name: ck_gbuf
** View name: schematic
.subckt ck_gbuf ck ckb en cko ckob vdd vss
xi0 ck en net70 vdd vss nand2_c
xi1 ckb en net71 vdd vss nand2_c
xi2 net70 cko vdd vss inv_c
xi3 net71 ckob vdd vss inv_c
.ends ck_gbuf
** End of subcircuit definition.

** Library name: pod_rx

** Library name: pod_rx
** Cell name: dqrx_eq
** View name: schematic
.subckt dqrx_eq pad vref ck ckb lb_p lb_n lb_en rx_en odt_en rtt<2> rtt<1> rtt<0> tap<2> tap<1> tap<0> tap_sgn pk<1> pk<0> ofe<2> ofe<1> ofe<0> ofe_s ofo<2> ofo<1> ofo<0> ofo_s ibias dout_e dout_o vdd vddq vss vssq
xi20 pad net1 vddq vssq esd_dq
xi21 pad net2<2> net2<1> net2<0> vddq odt_pu
xi22 odt_en rtt<2> rtt<1> rtt<0> net2<2> net2<1> net2<0> vdd vddq vss odt_dec
r0 vref net30 4k
mn0 vssq net30 vssq vssq nch_18 w=10u l=2u m=2
r1 net30 net3 4k
mn1 vssq net3 vssq vssq nch_18 w=10u l=2u m=4
xi23 ibias rx_en net4 vdd vddq vss vssq rx_bias
xi0 lb_en net100 vdd vss inv_a
xi1 rx_en net100 net101 vdd vss nand2_a
xi2 net101 net102 vdd vss inv_a
xi3 rx_en lb_en net103 vdd vss nand2_a
xi4 net103 net104 vdd vss inv_a
xi5 tap_sgn net105 vdd vss inv_a
xi6 net105 net106 vdd vss inv_a
xi13 pk<1> net31<1> vdd vddq vss ls_lh
xi14 pk<0> net31<0> vdd vddq vss ls_lh
xi24 net1 net3 lb_p lb_n net102 net104 net31<1> net31<0> net4 net6 net7 vddq vssq rx_pre_dg
xi25 ck ckb rx_en net8 net9 vdd vss ck_gbuf
xi26 net6 net7 net16 net17 tap<2> tap<1> tap<0> net106 net105 rx_en ibias net10 net11 vdd vss dfe_sum3
xi27 net6 net7 net14 net15 tap<2> tap<1> tap<0> net106 net105 rx_en ibias net12 net13 vdd vss dfe_sum3
xi28 net10 net11 net8 net18 net19 ofe<2> ofe<1> ofe<0> ofe_s vdd vss sa_ci
xi29 net12 net13 net9 net24 net25 ofo<2> ofo<1> ofo<0> ofo_s vdd vss sa_ci
xi30 net18 net19 net14 net15 vdd vss sr_nor
xi31 net24 net25 net16 net17 vdd vss sr_nor
xi7 net14 net26 vdd vss inv_a
xi8 net26 dout_e vdd vss inv_c
xi9 net15 net27 vdd vss inv_a
xi10 net16 net28 vdd vss inv_a
xi11 net28 dout_o vdd vss inv_c
xi12 net17 net29 vdd vss inv_a
.ends dqrx_eq
** End of subcircuit definition.

.END
