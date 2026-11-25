** Generated for: hspiceD
** Generated on: Nov 22 14:12:38 2026
** Design library name: ddr_rxa
** Design cell name: dqrx_slice
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: ddr_std
** Cell name: inv_a
** View name: schematic
.subckt inv_a a y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mn0 y a vss vss nch w=160n l=30n m=1
.ends inv_a
** End of subcircuit definition.

** Library name: ddr_std
** Cell name: inv_c
** View name: schematic
.subckt inv_c a y vdd vss
mp0 y a vdd vdd pch_lvt w=960n l=30n m=2
mn0 y a vss vss nch_lvt w=480n l=30n m=2
.ends inv_c
** End of subcircuit definition.

** Library name: ddr_std
** Cell name: nand2_a
** View name: schematic
.subckt nand2_a a b y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mp1 y b vdd vdd pch w=320n l=30n m=1
mn0 y a net5 vss nch w=320n l=30n m=1
mn1 net5 b vss vss nch w=320n l=30n m=1
.ends nand2_a
** End of subcircuit definition.

** Library name: ddr_std
** Cell name: nand2_c
** View name: schematic
.subckt nand2_c a b y vdd vss
mp0 y a vdd vdd pch_lvt w=640n l=30n m=2
mp1 y b vdd vdd pch_lvt w=640n l=30n m=2
mn0 y a net5 vss nch_lvt w=640n l=30n m=2
mn1 net5 b vss vss nch_lvt w=640n l=30n m=2
.ends nand2_c
** End of subcircuit definition.

** Library name: ddr_std
** Cell name: nor2_c
** View name: schematic
.subckt nor2_c a b y vdd vss
mp0 net7 a vdd vdd pch_lvt w=960n l=30n m=1
mp1 y b net7 vdd pch_lvt w=960n l=30n m=1
mn0 y a vss vss nch_lvt w=240n l=30n m=1
mn1 y b vss vss nch_lvt w=240n l=30n m=1
.ends nor2_c
** End of subcircuit definition.

** Library name: ddr_std
** Cell name: mux2_t
** View name: schematic
.subckt mux2_t d0 d1 s z vdd vss
xi0 s net3 vdd vss inv_a
mn0 d0 net3 z vss nch w=320n l=30n m=1
mp0 d0 s z vdd pch w=320n l=30n m=1
mn1 d1 s z vss nch w=320n l=30n m=1
mp1 d1 net3 z vdd pch w=320n l=30n m=1
.ends mux2_t
** End of subcircuit definition.

** Library name: ddr_std
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

** Library name: ddr_rxa
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

** Library name: ddr_rxa
** Cell name: odt_leg
** View name: schematic
.subckt odt_leg pad enb vddq
mp0 net3 enb vddq vddq pch_18 w=24u l=100n m=1
r0 net3 pad 240
.ends odt_leg
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: odt_pu
** View name: schematic
.subckt odt_pu pad enb_2 enb_1 enb_0 vddq
xi6 pad enb_2 vddq odt_leg
xi5 pad enb_2 vddq odt_leg
xi4 pad enb_2 vddq odt_leg
xi3 pad enb_2 vddq odt_leg
xi2 pad enb_1 vddq odt_leg
xi1 pad enb_1 vddq odt_leg
xi0 pad enb_0 vddq odt_leg
.ends odt_pu
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: odt_dec
** View name: schematic
.subckt odt_dec odt_en rtt_2 rtt_1 rtt_0 enb_2 enb_1 enb_0 vdd vddq vss
xi5 net20 enb_2 vdd vddq vss ls_lh
xi4 net21 enb_1 vdd vddq vss ls_lh
xi3 net22 enb_0 vdd vddq vss ls_lh
xi2 odt_en rtt_2 net20 vdd vss nand2_a
xi1 odt_en rtt_1 net21 vdd vss nand2_a
xi0 odt_en rtt_0 net22 vdd vss nand2_a
.ends odt_dec
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: rx_ctl
** View name: schematic
.subckt rx_ctl rx_on lpbk_en pwrdn dfe_pol en sel_m sel_l pol polb pd vdd vss
xi0 pwrdn net1 vdd vss inv_a
xi1 net1 pd vdd vss inv_a
xi2 rx_on net1 net2 vdd vss nand2_a
xi3 net2 en vdd vss inv_c
xi4 lpbk_en net3 vdd vss inv_a
xi5 en net3 net4 vdd vss nand2_a
xi6 net4 sel_m vdd vss inv_a
xi7 en lpbk_en net5 vdd vss nand2_a
xi8 net5 sel_l vdd vss inv_a
xi9 dfe_pol polb vdd vss inv_a
xi10 polb pol vdd vss inv_a
.ends rx_ctl
** End of subcircuit definition.

** Library name: ddr_rxa
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

** Library name: ddr_rxa
** Cell name: rx_fe
** View name: schematic
.subckt rx_fe inp vref lbp lbn sel_m sel_l vbn outp outn vddq vssq
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
.ends rx_fe
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: dfe_add
** View name: schematic
.subckt dfe_add inp inn hp hn w_3 w_2 w_1 w_0 pol polb en vbn outp outn vdd vss
r0 vdd outn 600
r1 vdd outp 600
mn0 outn inp net50 vss nch_lvt w=2u l=30n m=2
mn1 outp inn net50 vss nch_lvt w=2u l=30n m=2
mn2 net50 en net51 vss nch w=4u l=30n m=1
mn3 net51 vbn vss vss nch w=1u l=240n m=8
mn4 net52 hp net54 vss nch_lvt w=1u l=30n m=1
mn5 net53 hn net54 vss nch_lvt w=1u l=30n m=1
mn6 outp polb net52 vss nch_lvt w=1u l=30n m=1
mn7 outn polb net53 vss nch_lvt w=1u l=30n m=1
mn8 outn pol net52 vss nch_lvt w=1u l=30n m=1
mn9 outp pol net53 vss nch_lvt w=1u l=30n m=1
mn10 net54 w_3 net58 vss nch w=400n l=30n m=8
mn11 net58 vbn vss vss nch w=1u l=240n m=8
mn12 net54 w_2 net57 vss nch w=400n l=30n m=4
mn13 net57 vbn vss vss nch w=1u l=240n m=4
mn14 net54 w_1 net56 vss nch w=400n l=30n m=2
mn15 net56 vbn vss vss nch w=1u l=240n m=2
mn16 net54 w_0 net55 vss nch w=400n l=30n m=1
mn17 net55 vbn vss vss nch w=1u l=240n m=1
.ends dfe_add
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: sa_dt
** View name: schematic
.subckt sa_dt inp inn ck outp outn ofp_1 ofp_0 ofn_1 ofn_0 vdd vss
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
mn7 net62 ofn_1 net66 vss nch w=200n l=30n m=2
mn8 vss net66 vss vss nch w=400n l=200n m=2
mn9 net62 ofn_0 net65 vss nch w=200n l=30n m=1
mn10 vss net65 vss vss nch w=400n l=200n m=1
mn11 net63 ofp_1 net68 vss nch w=200n l=30n m=2
mn12 vss net68 vss vss nch w=400n l=200n m=2
mn13 net63 ofp_0 net67 vss nch w=200n l=30n m=1
mn14 vss net67 vss vss nch w=400n l=200n m=1
.ends sa_dt
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: sr_nor
** View name: schematic
.subckt sr_nor s r q qb vdd vss
xi0 r qb q vdd vss nor2_c
xi1 s q qb vdd vss nor2_c
.ends sr_nor
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: slc_ph
** View name: schematic
.subckt slc_ph inp inn ck q qb ofp_1 ofp_0 ofn_1 ofn_0 vdd vss
xi0 inp inn ck net1 net2 ofp_1 ofp_0 ofn_1 ofn_0 vdd vss sa_dt
xi1 net1 net2 q qb vdd vss sr_nor
.ends slc_ph
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: ck_gbuf
** View name: schematic
.subckt ck_gbuf ck ckb en cko ckob vdd vss
xi0 ck en net70 vdd vss nand2_c
xi1 ckb en net71 vdd vss nand2_c
xi2 net70 cko vdd vss inv_c
xi3 net71 ckob vdd vss inv_c
.ends ck_gbuf
** End of subcircuit definition.

** Library name: ddr_rxa
** Cell name: dqrx_slice
** View name: schematic
.subckt dqrx_slice dq_pad vref_in clk_t clk_c lpbk_p lpbk_n lpbk_en rx_on pwrdn odt_en rtt_2 rtt_1 rtt_0 dfe_w_3 dfe_w_2 dfe_w_1 dfe_w_0 dfe_pol ofs_ep_1 ofs_ep_0 ofs_en_1 ofs_en_0 ofs_op_1 ofs_op_0 ofs_on_1 ofs_on_0 mon_sel ib_rx q_even q_odd mon_q vdd vddq vss vssq
xi20 dq_pad net1 vddq vssq esd_dq
xi21 dq_pad net21 net22 net23 vddq odt_pu
xi22 odt_en rtt_2 rtt_1 rtt_0 net21 net22 net23 vdd vddq vss odt_dec
r0 vref_in net3 5k
mn0 vssq net3 vssq vssq nch_18 w=10u l=2u m=4
xi1 rx_on lpbk_en pwrdn dfe_pol net30 net31 net32 net33 net34 net35 vdd vss rx_ctl
mp0 net5 net35 vdd vdd pch_hvt w=8u l=40n m=8
xi23 ib_rx net30 net4 vdd vddq vss vssq rx_bias
xi24 net1 net3 lpbk_p lpbk_n net31 net32 net4 net6 net7 vddq vssq rx_fe
xi25 clk_t clk_c net30 net8 net9 vdd vss ck_gbuf
xi26 net6 net7 net16 net17 dfe_w_3 dfe_w_2 dfe_w_1 dfe_w_0 net33 net34 net30 ib_rx net10 net11 net5 vss dfe_add
xi27 net6 net7 net14 net15 dfe_w_3 dfe_w_2 dfe_w_1 dfe_w_0 net33 net34 net30 ib_rx net12 net13 net5 vss dfe_add
xi28 net10 net11 net8 net14 net15 ofs_ep_1 ofs_ep_0 ofs_en_1 ofs_en_0 net5 vss slc_ph
xi29 net12 net13 net9 net16 net17 ofs_op_1 ofs_op_0 ofs_on_1 ofs_on_0 net5 vss slc_ph
xi7 net14 net18 vdd vss inv_a
xi8 net18 net35 q_even vdd vss nor2_c
xi9 net15 net19 vdd vss inv_a
xi10 net16 net26 vdd vss inv_a
xi11 net26 net35 q_odd vdd vss nor2_c
xi12 net17 net27 vdd vss inv_a
xi13 net18 net26 mon_sel net28 vdd vss mux2_t
xi14 net28 mon_q vdd vss inv_c
.ends dqrx_slice
** End of subcircuit definition.

.END
