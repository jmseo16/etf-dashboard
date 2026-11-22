** Generated for: hspiceD
** Generated on: Nov 22 15:03:44 2026
** Design library name: rxb_lib
** Design cell name: rx_byte8
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: rxb_std
** Cell name: inv1
** View name: schematic
.subckt inv1 a y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mn0 y a vss vss nch w=150n l=30n m=1
.ends inv1
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: inv4
** View name: schematic
.subckt inv4 a y vdd vss
mp0 y a vdd vdd pch_lvt w=600n l=30n m=2
mn0 y a vss vss nch_lvt w=300n l=30n m=2
.ends inv4
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: nd2x1
** View name: schematic
.subckt nd2x1 a b y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mp1 y b vdd vdd pch w=300n l=30n m=1
mn0 y a net3 vss nch w=300n l=30n m=1
mn1 net3 b vss vss nch w=300n l=30n m=1
.ends nd2x1
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: nd2x2
** View name: schematic
.subckt nd2x2 a b y vdd vss
mp0 y a vdd vdd pch_lvt w=600n l=30n m=1
mp1 y b vdd vdd pch_lvt w=600n l=30n m=1
mn0 y a net3 vss nch_lvt w=600n l=30n m=1
mn1 net3 b vss vss nch_lvt w=600n l=30n m=1
.ends nd2x2
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: lsup
** View name: schematic
.subckt lsup in out outb vdd vddq vss
mp2 net4 in vdd vdd pch w=300n l=30n m=1
mn2 net4 in vss vss nch w=150n l=30n m=1
mn0 net5 in vss vss nch_18 w=1.2u l=150n m=1
mn1 net6 net4 vss vss nch_18 w=1.2u l=150n m=1
mp0 net5 net6 vddq vddq pch_18 w=400n l=150n m=1
mp1 net6 net5 vddq vddq pch_18 w=400n l=150n m=1
mp3 out net5 vddq vddq pch_18 w=1.6u l=100n m=1
mn3 out net5 vss vss nch_18 w=800n l=100n m=1
mp4 outb net6 vddq vddq pch_18 w=1.6u l=100n m=1
mn4 outb net6 vss vss nch_18 w=800n l=100n m=1
.ends lsup
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: lattg
** View name: schematic
.subckt lattg d en enb q vdd vss
mn0 d en net7 vss nch w=300n l=30n m=1
mp0 d enb net7 vdd pch w=300n l=30n m=1
xi0 net7 net8 vdd vss inv1
xi1 net8 q vdd vss inv1
mn1 q enb net7 vss nch w=150n l=30n m=1
mp1 q en net7 vdd pch w=150n l=30n m=1
.ends lattg
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: dff
** View name: schematic
.subckt dff d ck q vdd vss
xi0 ck net10 vdd vss inv1
xi1 net10 net11 vdd vss inv1
mn0 d net10 net12 vss nch w=300n l=30n m=1
mp0 d net11 net12 vdd pch w=300n l=30n m=1
xi2 net12 net13 vdd vss inv1
xi3 net13 net14 vdd vss inv1
mn1 net14 net11 net12 vss nch w=150n l=30n m=1
mp1 net14 net10 net12 vdd pch w=150n l=30n m=1
mn2 net13 net11 net15 vss nch w=300n l=30n m=1
mp2 net13 net10 net15 vdd pch w=300n l=30n m=1
xi4 net15 net16 vdd vss inv1
xi5 net16 net17 vdd vss inv1
mn3 net17 net10 net15 vss nch w=150n l=30n m=1
mp3 net17 net11 net15 vdd pch w=150n l=30n m=1
xi6 net15 q vdd vss inv1
.ends dff
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: mux2
** View name: schematic
.subckt mux2 d0 d1 s z vdd vss
xi0 s net18 vdd vss inv1
mn0 d0 net18 z vss nch_lvt w=300n l=30n m=1
mp0 d0 s z vdd pch_lvt w=300n l=30n m=1
mn1 d1 s z vss nch_lvt w=300n l=30n m=1
mp1 d1 net18 z vdd pch_lvt w=300n l=30n m=1
.ends mux2
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: dlyc
** View name: schematic
.subckt dlyc a y vdd vss
mp0 net19 a vdd vdd pch w=300n l=60n m=1
mn0 net19 a vss vss nch w=150n l=60n m=1
mp1 y net19 vdd vdd pch w=300n l=60n m=1
mn1 y net19 vss vss nch w=150n l=60n m=1
.ends dlyc
** End of subcircuit definition.

** Library name: rxb_std
** Cell name: ckdrv
** View name: schematic
.subckt ckdrv a y vdd vss
xi0 a net20 vdd vss inv4
xi1 net20 y vdd vss inv4
.ends ckdrv
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: esd_pad
** View name: schematic
.subckt esd_pad pad pad_r vddq vssq
d0 pad vddq pdio_esd area=60p pj=64u
d1 vssq pad ndio_esd area=60p pj=64u
r0 pad pad_r rppolywo w=2u l=1.2u
d2 pad_r vddq pdio_esd area=6p pj=14u
d3 vssq pad_r ndio_esd area=6p pj=14u
mn0 pad_r net21 vssq vssq nch_18 w=20u l=150n m=2
r1 net21 vssq rppolyhri w=0.4u l=4u
.ends esd_pad
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: odt_leg3
** View name: schematic
.subckt odt_leg3 pad enb<2> enb<1> enb<0> vddq
mp2 net24 enb<2> vddq vddq pch_18 w=24u l=100n m=4
r2 net24 pad rppolywo w=4u l=1.2u m=4
mp1 net23 enb<1> vddq vddq pch_18 w=24u l=100n m=2
r1 net23 pad rppolywo w=4u l=1.2u m=2
mp0 net22 enb<0> vddq vddq pch_18 w=24u l=100n m=1
r0 net22 pad rppolywo w=4u l=1.2u m=1
.ends odt_leg3
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: odt_ctl
** View name: schematic
.subckt odt_ctl odt_en rtt<2> rtt<1> rtt<0> enb<2> enb<1> enb<0> vdd vddq vss
xi2 odt_en rtt<2> net25 vdd vss nd2x1
xi1 odt_en rtt<1> net26 vdd vss nd2x1
xi0 odt_en rtt<0> net27 vdd vss nd2x1
xi5 net25 enb<2> net28 vdd vddq vss lsup
xi4 net26 enb<1> net29 vdd vddq vss lsup
xi3 net27 enb<0> net30 vdd vddq vss lsup
.ends odt_ctl
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: bias_gen
** View name: schematic
.subckt bias_gen ibias en vbp vdd vddq vss vssq
xi0 en net31 vdd vss inv1
mn0 ibias ibias vssq vssq nch_18 w=2u l=400n m=4
mn1 vbp ibias vssq vssq nch_18 w=2u l=400n m=4
mp0 vbp vbp vddq vddq pch_18 w=4u l=400n m=4
mn2 ibias net31 vssq vssq nch_18 w=1u l=150n m=1
mp1 vbp en vddq vddq pch_18 w=1u l=150n m=1
.ends bias_gen
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: vref_dac
** View name: schematic
.subckt vref_dac code<5> code<4> code<3> code<2> code<1> code<0> vbp vref vdd vddq vss vssq
xi5 code<5> net40 vdd vss inv1
xi4 code<4> net39 vdd vss inv1
xi3 code<3> net38 vdd vss inv1
xi2 code<2> net37 vdd vss inv1
xi1 code<1> net36 vdd vss inv1
xi0 code<0> net35 vdd vss inv1
mp10 net50 vbp vddq vddq pch_18 w=2u l=400n m=32
mp11 net32 net40 net50 vddq pch_18 w=1u l=100n m=32
mp8 net49 vbp vddq vddq pch_18 w=2u l=400n m=16
mp9 net32 net39 net49 vddq pch_18 w=1u l=100n m=16
mp6 net48 vbp vddq vddq pch_18 w=2u l=400n m=8
mp7 net32 net38 net48 vddq pch_18 w=1u l=100n m=8
mp4 net47 vbp vddq vddq pch_18 w=2u l=400n m=4
mp5 net32 net37 net47 vddq pch_18 w=1u l=100n m=4
mp2 net46 vbp vddq vddq pch_18 w=2u l=400n m=2
mp3 net32 net36 net46 vddq pch_18 w=1u l=100n m=2
mp0 net45 vbp vddq vddq pch_18 w=2u l=400n m=1
mp1 net32 net35 net45 vddq pch_18 w=1u l=100n m=1
mp12 net51 vbp vddq vddq pch_18 w=2u l=400n m=64
mp13 net32 vssq net51 vddq pch_18 w=1u l=100n m=64
r0 net32 vssq rppolywo w=1u l=12u
r1 net32 vref rppolyhri w=0.4u l=10u
mn0 vssq vref vssq vssq nch_18 w=20u l=2u m=4
.ends vref_dac
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dqs_amp
** View name: schematic
.subckt dqs_amp inp inn vbn en outp outn vddq vssq
r0 vddq outn rppolywo w=0.4u l=2.4u
r1 vddq outp rppolywo w=0.4u l=2.4u
mn0 outn inp net52 vssq nch_18 w=4u l=100n m=2
mn1 outp inn net52 vssq nch_18 w=4u l=100n m=2
mn2 net52 en net53 vssq nch_18 w=8u l=100n m=1
mn3 net53 vbn vssq vssq nch_18 w=4u l=400n m=4
.ends dqs_amp
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: ac_cpl
** View name: schematic
.subckt ac_cpl in out en vdd vss
c0 in net54 mimcap_2p0 w=6u l=6u
r0 net54 net55 rppolyhri w=0.4u l=20u
mp0 net55 net54 vdd vdd pch_lvt w=1.2u l=40n m=1
mn0 net55 net54 net56 vss nch_lvt w=600n l=40n m=1
mn1 net56 en vss vss nch w=1.2u l=30n m=1
mp1 net55 en vdd vdd pch w=300n l=30n m=1
xi0 net55 out vdd vss inv4
.ends ac_cpl
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dqs_rcv
** View name: schematic
.subckt dqs_rcv inp inn vbn enq en ckt ckc vdd vddq vss vssq
xi0 inp inn vbn enq net57 net58 vddq vssq dqs_amp
xi1 net57 net59 en vdd vss ac_cpl
xi2 net58 net60 en vdd vss ac_cpl
xi3 net59 net60 vdd vss inv1
xi4 net60 net59 vdd vss inv1
xi5 net59 net61 vdd vss inv1
xi6 net61 ckt vdd vss inv4
xi7 net60 net62 vdd vss inv1
xi8 net62 ckc vdd vss inv4
.ends dqs_rcv
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dqs_gate
** View name: schematic
.subckt dqs_gate ckt ckc open gt gc vdd vss
xi0 open ckc ckt net63 vdd vss lattg
xi1 open ckt ckc net64 vdd vss lattg
xi2 ckt net63 net65 vdd vss nd2x2
xi3 net65 gt vdd vss inv4
xi4 ckc net64 net66 vdd vss nd2x2
xi5 net66 gc vdd vss inv4
.ends dqs_gate
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dly_line
** View name: schematic
.subckt dly_line in out s<2> s<1> s<0> vdd vss
xi0 in net67 vdd vss dlyc
xi1 in net67 s<0> net68 vdd vss mux2
xi2 net68 net69 vdd vss dlyc
xi3 net69 net70 vdd vss dlyc
xi4 net70 net71 vdd vss dlyc
xi5 net69 net71 s<1> net72 vdd vss mux2
xi6 net72 net73 vdd vss dlyc
xi7 net73 net74 vdd vss dlyc
xi8 net74 net75 vdd vss dlyc
xi9 net75 net76 vdd vss dlyc
xi10 net76 net77 vdd vss dlyc
xi11 net73 net77 s<2> net78 vdd vss mux2
xi12 net78 out vdd vss dlyc
.ends dly_line
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: sb_amp
** View name: schematic
.subckt sb_amp inp inn out en enb vddq vssq
mp6 net80 enb vddq vddq pch_18 w=8u l=100n m=1
mp5 net81 net79 net80 vddq pch_18 w=4u l=150n m=1
mn6 net83 en vssq vssq nch_18 w=4u l=100n m=1
mn5 net82 net79 net83 vssq nch_18 w=2u l=150n m=1
mp1 net79 inp net81 vddq pch_18 w=2u l=100n m=1
mn1 net79 inp net82 vssq nch_18 w=1u l=100n m=1
mp2 out inn net81 vddq pch_18 w=2u l=100n m=1
mn2 out inn net82 vssq nch_18 w=1u l=100n m=1
.ends sb_amp
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: sa_dfe
** View name: schematic
.subckt sa_dfe inp inn ck h1p h1n h2p h2n w1<2> w1<1> w1<0> w2<1> w2<0> outp outn vdd vss
mn0 net84 ck vss vss nch_lvt w=3u l=30n m=2
mn1 net85 inp net84 vss nch_lvt w=2u l=30n m=2
mn2 net86 inn net84 vss nch_lvt w=2u l=30n m=2
mn3 outn outp net85 vss nch_lvt w=1u l=30n m=1
mn4 outp outn net86 vss nch_lvt w=1u l=30n m=1
mp0 outn outp vdd vdd pch_lvt w=1u l=30n m=1
mp1 outp outn vdd vdd pch_lvt w=1u l=30n m=1
mp2 outn ck vdd vdd pch_lvt w=500n l=30n m=1
mp3 outp ck vdd vdd pch_lvt w=500n l=30n m=1
mp4 net85 ck vdd vdd pch_lvt w=500n l=30n m=1
mp5 net86 ck vdd vdd pch_lvt w=500n l=30n m=1
mn10 net86 h1p net89 vss nch_lvt w=250n l=30n m=4
mn11 net85 h1n net89 vss nch_lvt w=250n l=30n m=4
mn12 net89 w1<2> net84 vss nch_lvt w=500n l=30n m=4
mn13 net86 h1p net88 vss nch_lvt w=250n l=30n m=2
mn14 net85 h1n net88 vss nch_lvt w=250n l=30n m=2
mn15 net88 w1<1> net84 vss nch_lvt w=500n l=30n m=2
mn16 net86 h1p net87 vss nch_lvt w=250n l=30n m=1
mn17 net85 h1n net87 vss nch_lvt w=250n l=30n m=1
mn18 net87 w1<0> net84 vss nch_lvt w=500n l=30n m=1
mn20 net86 h2p net91 vss nch_lvt w=250n l=30n m=2
mn21 net85 h2n net91 vss nch_lvt w=250n l=30n m=2
mn22 net91 w2<1> net84 vss nch_lvt w=500n l=30n m=2
mn23 net86 h2p net90 vss nch_lvt w=250n l=30n m=1
mn24 net85 h2n net90 vss nch_lvt w=250n l=30n m=1
mn25 net90 w2<0> net84 vss nch_lvt w=500n l=30n m=1
.ends sa_dfe
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: sr_nand
** View name: schematic
.subckt sr_nand sb rb q qb vdd vss
xi0 sb qb q vdd vss nd2x2
xi1 rb q qb vdd vss nd2x2
.ends sr_nand
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dq_afe
** View name: schematic
.subckt dq_afe pad vref en_c odtb<2> odtb<1> odtb<0> outp outn vdd vddq vss vssq
xi0 pad net1 vddq vssq esd_pad
xi1 pad odtb<2> odtb<1> odtb<0> vddq odt_leg3
xi2 en_c net2 net3 vdd vddq vss lsup
xi3 net1 vref outp net2 net3 vddq vssq sb_amp
xi4 vref net1 outn net2 net3 vddq vssq sb_amp
.ends dq_afe
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dq_smp
** View name: schematic
.subckt dq_smp inp inn ckt ckc w1<2> w1<1> w1<0> w2<1> w2<0> qr qf vdd vss
xi0 inp inn ckt net13 net14 net11 net12 w1<2> w1<1> w1<0> w2<1> w2<0> net9 net10 vdd vss sa_dfe
xi1 net10 net9 net11 net12 vdd vss sr_nand
xi2 inp inn ckc net11 net12 net13 net14 w1<2> w1<1> w1<0> w2<1> w2<0> net15 net16 vdd vss sa_dfe
xi3 net16 net15 net13 net14 vdd vss sr_nand
xi4 net11 net17 vdd vss inv1
xi5 net17 qr vdd vss inv4
xi6 net13 net18 vdd vss inv1
xi7 net18 qf vdd vss inv4
.ends dq_smp
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dq_lane
** View name: schematic
.subckt dq_lane pad vref ckt ckc en_c w1<2> w1<1> w1<0> w2<1> w2<0> odtb<2> odtb<1> odtb<0> qr qf vdd vddq vss vssq
xi0 pad vref en_c odtb<2> odtb<1> odtb<0> net1 net2 vdd vddq vss vssq dq_afe
xi1 net1 net2 ckt ckc w1<2> w1<1> w1<0> w2<1> w2<0> qr qf vdd vss dq_smp
.ends dq_lane
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: wl_det
** View name: schematic
.subckt wl_det d ck en q vdd vss
xi0 ck en net105 vdd vss nd2x2
xi1 net105 net106 vdd vss inv4
xi2 d net106 net107 vdd vss dff
xi3 net107 net108 vdd vss inv1
xi4 net108 q vdd vss inv4
.ends wl_det
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: dqs_div
** View name: schematic
.subckt dqs_div ck en mon vdd vss
xi0 ck en net1 vdd vss nd2x2
xi1 net1 net2 vdd vss inv4
xi2 net3 net2 net4 vdd vss dff
xi3 net4 net3 vdd vss inv1
xi4 net4 net5 vdd vss inv1
xi5 net5 mon vdd vss inv4
.ends dqs_div
** End of subcircuit definition.

** Library name: rxb_lib
** Cell name: rx_byte8
** View name: schematic
.subckt rx_byte8 dq<7> dq<6> dq<5> dq<4> dq<3> dq<2> dq<1> dq<0> dqs_t dqs_c qr<7> qr<6> qr<5> qr<4> qr<3> qr<2> qr<1> qr<0> qf<7> qf<6> qf<5> qf<4> qf<3> qf<2> qf<1> qf<0> wl_q dqs_mon rx_en gate_en wl_en wl_ck tst_en pwr_dn odt_en rtt<2> rtt<1> rtt<0> vref_code<5> vref_code<4> vref_code<3> vref_code<2> vref_code<1> vref_code<0> h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> dly<2> dly<1> dly<0> ibias vdd vddq vss vssq
mp0 net200 pwr_dn vdd vdd pch_hvt w=12u l=40n m=16
xi0 rx_en net201 net202 vdd vddq vss lsup
xi1 ibias rx_en net203 vdd vddq vss vssq bias_gen
xi2 vref_code<5> vref_code<4> vref_code<3> vref_code<2> vref_code<1> vref_code<0> net203 net204 vdd vddq vss vssq vref_dac
xi3 odt_en rtt<2> rtt<1> rtt<0> net207 net206 net205 vdd vddq vss odt_ctl
xi4 dqs_t net208 vddq vssq esd_pad
xi5 dqs_c net209 vddq vssq esd_pad
xi6 dqs_t net207 net206 net205 vddq odt_leg3
xi7 dqs_c net207 net206 net205 vddq odt_leg3
xi8 net208 net209 ibias net201 rx_en net210 net211 vdd vddq vss vssq dqs_rcv
xi9 net210 net211 gate_en net212 net213 vdd vss dqs_gate
xi10 net212 net214 dly<2> dly<1> dly<0> vdd vss dly_line
xi11 net213 net215 dly<2> dly<1> dly<0> vdd vss dly_line
d0 vss net214 ndio_ant area=0.12p pj=1.4u
d1 vss net215 ndio_ant area=0.12p pj=1.4u
xi12 net214 net216 vdd vss ckdrv
xi13 net215 net217 vdd vss ckdrv
xi14 net216 net218 vdd vss ckdrv
xi15 net216 net218 vdd vss ckdrv
xi16 net217 net219 vdd vss ckdrv
xi17 net217 net219 vdd vss ckdrv
xi18 net216 net220 vdd vss ckdrv
xi19 net216 net220 vdd vss ckdrv
xi20 net217 net221 vdd vss ckdrv
xi21 net217 net221 vdd vss ckdrv
xi22 net216 net222 vdd vss ckdrv
xi23 net217 net223 vdd vss ckdrv
xi30 dq<0> net204 net218 net219 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<0> qf<0> net200 vddq vss vssq dq_lane
xi31 dq<1> net204 net218 net219 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<1> qf<1> net200 vddq vss vssq dq_lane
xi32 dq<2> net204 net218 net219 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<2> qf<2> net200 vddq vss vssq dq_lane
xi33 dq<3> net204 net218 net219 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<3> qf<3> net200 vddq vss vssq dq_lane
xi34 dq<4> net204 net220 net221 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<4> qf<4> net200 vddq vss vssq dq_lane
xi35 dq<5> net204 net220 net221 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<5> qf<5> net200 vddq vss vssq dq_lane
xi36 dq<6> net204 net220 net221 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<6> qf<6> net200 vddq vss vssq dq_lane
xi37 dq<7> net204 net220 net221 rx_en h1w<2> h1w<1> h1w<0> h2w<1> h2w<0> net207 net206 net205 qr<7> qf<7> net200 vddq vss vssq dq_lane
xi38 vssq net204 net222 net223 vss vss vss vss vss vss vddq vddq vddq net224 net225 net200 vddq vss vssq dq_lane
xi39 wl_ck net222 wl_en wl_q vdd vss wl_det
xi40 net216 tst_en dqs_mon vdd vss dqs_div
.ends rx_byte8
** End of subcircuit definition.

.END
