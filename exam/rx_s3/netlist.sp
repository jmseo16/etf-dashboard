** Generated for: hspiceD
** Generated on: Nov 22 14:02:51 2026
** Design library name: pod_rx
** Design cell name: dq_rx_unit
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

** Library name: pod_rx
** Cell name: dfe_sum
** View name: schematic
.subckt dfe_sum inp inn hp hn tap<3> tap<2> tap<1> tap<0> sgn sgnb en vbn outp outn vdd vss
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
mn10 net54 tap<3> net58 vss nch w=400n l=30n m=8
mn11 net58 vbn vss vss nch w=1u l=240n m=8
mn12 net54 tap<2> net57 vss nch w=400n l=30n m=4
mn13 net57 vbn vss vss nch w=1u l=240n m=4
mn14 net54 tap<1> net56 vss nch w=400n l=30n m=2
mn15 net56 vbn vss vss nch w=1u l=240n m=2
mn16 net54 tap<0> net55 vss nch w=400n l=30n m=1
mn17 net55 vbn vss vss nch w=1u l=240n m=1
.ends dfe_sum
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: sa_dt
** View name: schematic
.subckt sa_dt inp inn ck outp outn ofp<1> ofp<0> ofn<1> ofn<0> vdd vss
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
mn7 net62 ofn<1> net66 vss nch w=200n l=30n m=2
mn8 vss net66 vss vss nch w=400n l=200n m=2
mn9 net62 ofn<0> net65 vss nch w=200n l=30n m=1
mn10 vss net65 vss vss nch w=400n l=200n m=1
mn11 net63 ofp<1> net68 vss nch w=200n l=30n m=2
mn12 vss net68 vss vss nch w=400n l=200n m=2
mn13 net63 ofp<0> net67 vss nch w=200n l=30n m=1
mn14 vss net67 vss vss nch w=400n l=200n m=1
.ends sa_dt
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
** Cell name: ck_rcv
** View name: schematic
.subckt ck_rcv inp inn en ckt ckc vdd vss
xi0 en net79 vdd vss inv_a
mn0 net80 en vss vss nch_lvt w=2u l=30n m=2
mn1 net81 inp net80 vss nch_lvt w=1u l=30n m=2
mn2 net82 inn net80 vss nch_lvt w=1u l=30n m=2
mp0 net81 net81 vdd vdd pch_lvt w=1u l=30n m=2
mp1 net82 net81 vdd vdd pch_lvt w=1u l=30n m=2
mn3 net83 en vss vss nch_lvt w=2u l=30n m=2
mn4 net84 inn net83 vss nch_lvt w=1u l=30n m=2
mn5 net85 inp net83 vss nch_lvt w=1u l=30n m=2
mp2 net84 net84 vdd vdd pch_lvt w=1u l=30n m=2
mp3 net85 net84 vdd vdd pch_lvt w=1u l=30n m=2
mn6 net82 net79 vss vss nch w=320n l=30n m=1
mn7 net85 net79 vss vss nch w=320n l=30n m=1
xi1 net82 net86 vdd vss inv_c
xi2 net85 net87 vdd vss inv_c
xi3 net86 net87 vdd vss inv_a
xi4 net87 net86 vdd vss inv_a
xi5 net86 net88 vdd vss inv_c
xi6 net87 net89 vdd vss inv_c
xi7 net88 ckc vdd vss inv_c
xi8 net89 ckt vdd vss inv_c
.ends ck_rcv
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: ck_gate
** View name: schematic
.subckt ck_gate ckt ckc enb dly<1> dly<0> cko ckob vdd vss
xi0 ckc enb net90 vdd vss nor2_c
xi1 ckt enb net91 vdd vss nor2_c
xi2 net90 net92 vdd vss inv_c
xi3 net92 cko vdd vss inv_c
xi4 net91 net93 vdd vss inv_c
xi5 net93 ckob vdd vss inv_c
mn0 net92 dly<1> net94 vss nch w=400n l=30n m=2
mn1 vss net94 vss vss nch w=1u l=200n m=2
mn2 net92 dly<0> net95 vss nch w=400n l=30n m=1
mn3 vss net95 vss vss nch w=1u l=200n m=1
mn4 net93 dly<1> net96 vss nch w=400n l=30n m=2
mn5 vss net96 vss vss nch w=1u l=200n m=2
mn6 net93 dly<0> net97 vss nch w=400n l=30n m=1
mn7 vss net97 vss vss nch w=1u l=200n m=1
.ends ck_gate
** End of subcircuit definition.

** Library name: pod_rx
** Cell name: dq_rx_unit
** View name: schematic
.subckt dq_rx_unit pad vref ck_t ck_c lb_p lb_n lb_en rx_en ck_en odt_en rtt<2> rtt<1> rtt<0> tap<3> tap<2> tap<1> tap<0> tap_sgn ofe_p<1> ofe_p<0> ofe_n<1> ofe_n<0> ofo_p<1> ofo_p<0> ofo_n<1> ofo_n<0> ckdly<1> ckdly<0> ibias dout_e dout_o vdd vddq vss vssq
xi20 pad net1 vddq vssq esd_dq
xi21 pad net2<2> net2<1> net2<0> vddq odt_pu
xi22 odt_en rtt<2> rtt<1> rtt<0> net2<2> net2<1> net2<0> vdd vddq vss odt_dec
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
xi25 ck_t ck_c rx_en net30 net31 vdd vss ck_rcv
xi13 rx_en ck_en net107 vdd vss nand2_a
xi32 net30 net31 net107 ckdly<1> ckdly<0> net8 net9 vdd vss ck_gate
xi26 net6 net7 net16 net17 tap<3> tap<2> tap<1> tap<0> net106 net105 rx_en ibias net10 net11 vdd vss dfe_sum
xi27 net6 net7 net14 net15 tap<3> tap<2> tap<1> tap<0> net106 net105 rx_en ibias net12 net13 vdd vss dfe_sum
xi28 net10 net11 net8 net18 net19 ofe_p<1> ofe_p<0> ofe_n<1> ofe_n<0> vdd vss sa_dt
xi29 net12 net13 net9 net24 net25 ofo_p<1> ofo_p<0> ofo_n<1> ofo_n<0> vdd vss sa_dt
xi30 net18 net19 net14 net15 vdd vss sr_nor
xi31 net24 net25 net16 net17 vdd vss sr_nor
xi7 net14 net26 vdd vss inv_a
xi8 net26 dout_e vdd vss inv_c
xi9 net15 net27 vdd vss inv_a
xi10 net16 net28 vdd vss inv_a
xi11 net28 dout_o vdd vss inv_c
xi12 net17 net29 vdd vss inv_a
.ends dq_rx_unit
** End of subcircuit definition.

.END
