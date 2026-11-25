** Generated for: hspiceD
** Generated on: Nov 24 14:12:33 2026
** Design library name: lp5_tx
** Design cell name: dq_tx_unit
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: lp5_std
** Cell name: inv_s
** View name: schematic
.subckt inv_s a y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mn0 y a vss vss nch w=160n l=30n m=1
.ends inv_s
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: nand2_s
** View name: schematic
.subckt nand2_s a b y vdd vss
mp0 y a vdd vdd pch w=320n l=30n m=1
mp1 y b vdd vdd pch w=320n l=30n m=1
mn0 y a net5 vss nch w=320n l=30n m=1
mn1 net5 b vss vss nch w=320n l=30n m=1
.ends nand2_s
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: nor2_s
** View name: schematic
.subckt nor2_s a b y vdd vss
mp0 net7 a vdd vdd pch w=640n l=30n m=1
mp1 y b net7 vdd pch w=640n l=30n m=1
mn0 y a vss vss nch w=160n l=30n m=1
mn1 y b vss vss nch w=160n l=30n m=1
.ends nor2_s
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: inv_q
** View name: schematic
.subckt inv_q a y vddq vssq
mp0 y a vddq vddq pch_18 w=1.2u l=150n m=1
mn0 y a vssq vssq nch_18 w=600n l=150n m=1
.ends inv_q
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: nand2_q
** View name: schematic
.subckt nand2_q a b y vddq vssq
mp0 y a vddq vddq pch_18 w=1.2u l=150n m=1
mp1 y b vddq vddq pch_18 w=1.2u l=150n m=1
mn0 y a net5 vssq nch_18 w=1.2u l=150n m=1
mn1 net5 b vssq vssq nch_18 w=1.2u l=150n m=1
.ends nand2_q
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: aoi21_q
** View name: schematic
.subckt aoi21_q a b c y vddq vssq
mp0 net3 a vddq vddq pch_18 w=2.4u l=150n m=1
mp1 net3 b vddq vddq pch_18 w=2.4u l=150n m=1
mp2 y c net3 vddq pch_18 w=2.4u l=150n m=1
mn0 y a net4 vssq nch_18 w=1.2u l=150n m=1
mn1 net4 b vssq vssq nch_18 w=1.2u l=150n m=1
mn2 y c vssq vssq nch_18 w=600n l=150n m=1
.ends aoi21_q
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: lsup
** View name: schematic
.subckt lsup in out vdd vddq vss vssq
mp2 net9 in vdd vdd pch w=320n l=30n m=1
mn2 net9 in vss vss nch w=160n l=30n m=1
mn0 net10 in vssq vssq nch_18 w=1.2u l=150n m=1
mn1 net11 net9 vssq vssq nch_18 w=1.2u l=150n m=1
mp0 net10 net11 vddq vddq pch_18 w=400n l=150n m=1
mp1 net11 net10 vddq vddq pch_18 w=400n l=150n m=1
mp3 out net10 vddq vddq pch_18 w=1.6u l=150n m=1
mn3 out net10 vssq vssq nch_18 w=800n l=150n m=1
.ends lsup
** End of subcircuit definition.

** Library name: lp5_std
** Cell name: dff_s
** View name: schematic
.subckt dff_s d ck q vdd vss
xi0 ck net20 vdd vss inv_s
xi1 net20 net21 vdd vss inv_s
mn0 d net20 net22 vss nch w=320n l=30n m=1
mp0 d net21 net22 vdd pch w=320n l=30n m=1
xi2 net22 net23 vdd vss inv_s
xi3 net23 net24 vdd vss inv_s
mn1 net24 net21 net22 vss nch w=160n l=30n m=1
mp1 net24 net20 net22 vdd pch w=160n l=30n m=1
mn2 net23 net21 net25 vss nch w=320n l=30n m=1
mp2 net23 net20 net25 vdd pch w=320n l=30n m=1
xi4 net25 q vdd vss inv_s
xi5 q net26 vdd vss inv_s
mn3 net26 net20 net25 vss nch w=160n l=30n m=1
mp3 net26 net21 net25 vdd pch w=160n l=30n m=1
.ends dff_s
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: tx_dgate
** View name: schematic
.subckt tx_dgate din dly oe dp dn fp fn vdd vss
xi0 oe net30 vdd vss inv_s
xi1 din oe net31 vdd vss nand2_s
xi2 net31 dp vdd vss inv_s
xi3 din net30 dn vdd vss nor2_s
xi4 dly net30 fp vdd vss nor2_s
xi5 dly oe net32 vdd vss nand2_s
xi6 net32 fn vdd vss inv_s
.ends tx_dgate
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: code_ls3
** View name: schematic
.subckt code_ls3 i<2> i<1> i<0> o<2> o<1> o<0> vdd vddq vss vssq
xi2 i<2> o<2> vdd vddq vss vssq lsup
xi1 i<1> o<1> vdd vddq vss vssq lsup
xi0 i<0> o<0> vdd vddq vss vssq lsup
.ends code_ls3
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: odt_dec
** View name: schematic
.subckt odt_dec odt_en oe rtt<2> rtt<1> rtt<0> tpu<2> tpu<1> tpu<0> vdd vddq vss vssq
xi0 odt_en net40 vdd vss inv_s
xi1 net40 oe net41 vdd vss nor2_s
xi2 net41 rtt<2> net42 vdd vss nand2_s
xi3 net42 net43 vdd vss inv_s
xi4 net43 tpu<2> vdd vddq vss vssq lsup
xi5 net41 rtt<1> net44 vdd vss nand2_s
xi6 net44 net45 vdd vss inv_s
xi7 net45 tpu<1> vdd vddq vss vssq lsup
xi8 net41 rtt<0> net46 vdd vss nand2_s
xi9 net46 net47 vdd vss inv_s
xi10 net47 tpu<0> vdd vddq vss vssq lsup
.ends odt_dec
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: sr_ls
** View name: schematic
.subckt sr_ls sr<1> sr<0> en<1> enb<1> en<0> enb<0> vdd vddq vss vssq
xi0 sr<1> en<1> vdd vddq vss vssq lsup
xi1 en<1> enb<1> vddq vssq inv_q
xi2 sr<0> en<0> vdd vddq vss vssq lsup
xi3 en<0> enb<0> vddq vssq inv_q
.ends sr_ls
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: pdrv_sr
** View name: schematic
.subckt pdrv_sr in en<1> enb<1> en<0> enb<0> out vddq vssq
mp0 out in vddq vddq pch_18 w=4u l=150n m=1
mn0 out in vssq vssq nch_18 w=2u l=150n m=1
mp1 net50 enb<1> vddq vddq pch_18 w=4u l=150n m=2
mp2 out in net50 vddq pch_18 w=4u l=150n m=2
mn1 out in net51 vssq nch_18 w=2u l=150n m=2
mn2 net51 en<1> vssq vssq nch_18 w=2u l=150n m=2
mp3 net52 enb<0> vddq vddq pch_18 w=4u l=150n m=1
mp4 out in net52 vddq pch_18 w=4u l=150n m=1
mn3 out in net53 vssq nch_18 w=2u l=150n m=1
mn4 net53 en<0> vssq vssq nch_18 w=2u l=150n m=1
.ends pdrv_sr
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: seg_ctl
** View name: schematic
.subckt seg_ctl dp dn cpu cpd tpu sr<1> srb<1> sr<0> srb<0> pg ng vddq vssq
xi0 dp cpu tpu net60 vddq vssq aoi21_q
xi1 net60 net61 vddq vssq inv_q
xi2 net61 sr<1> srb<1> sr<0> srb<0> pg vddq vssq pdrv_sr
xi3 dn cpd net62 vddq vssq nand2_q
xi4 net62 sr<1> srb<1> sr<0> srb<0> ng vddq vssq pdrv_sr
.ends seg_ctl
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: ffe_ctl
** View name: schematic
.subckt ffe_ctl dp dn w pg ng vddq vssq
xi0 dp w net70 vddq vssq nand2_q
xi1 net70 net71 vddq vssq inv_q
xi2 net71 pg vddq vssq inv_q
xi3 dn w net72 vddq vssq nand2_q
xi4 net72 ng vddq vssq inv_q
.ends ffe_ctl
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: drv_leg1
** View name: schematic
.subckt drv_leg1 pg ng pad vddq vssq
mp0 net80 pg vddq vddq pch_18 w=12u l=150n m=1
r0 net80 pad 240
mn0 net81 ng vssq vssq nch_18 w=8u l=150n m=1
r1 net81 pad 240
.ends drv_leg1
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: drv_leg2
** View name: schematic
.subckt drv_leg2 pg ng pad vddq vssq
mp0 net80 pg vddq vddq pch_18 w=12u l=150n m=2
r0 net80 pad 120
mn0 net81 ng vssq vssq nch_18 w=8u l=150n m=2
r1 net81 pad 120
.ends drv_leg2
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: drv_leg4
** View name: schematic
.subckt drv_leg4 pg ng pad vddq vssq
mp0 net80 pg vddq vddq pch_18 w=12u l=150n m=4
r0 net80 pad 60
mn0 net81 ng vssq vssq nch_18 w=8u l=150n m=4
r1 net81 pad 60
.ends drv_leg4
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: esd_tx
** View name: schematic
.subckt esd_tx pad vddq vssq
d0 pad vddq pdio_esd area=60p pj=64u
d1 vssq pad ndio_esd area=60p pj=64u
mn0 pad net90 vssq vssq nch_18 w=20u l=150n m=4
r0 net90 vssq 10k
.ends esd_tx
** End of subcircuit definition.

** Library name: lp5_tx
** Cell name: dq_tx_unit
** View name: schematic
.subckt dq_tx_unit pad din ck oe odt_en rtt<2> rtt<1> rtt<0> zqpu<2> zqpu<1> zqpu<0> zqpd<2> zqpd<1> zqpd<0> ffe<1> ffe<0> sr<1> sr<0> vdd vddq vss vssq
d0 vss din ndio_ant area=1p pj=4u
xi0 din ck net1 vdd vss dff_s
xi1 din net1 oe net2 net3 net4 net5 vdd vss tx_dgate
xi2 net2 net6 vdd vddq vss vssq lsup
xi3 net3 net7 vdd vddq vss vssq lsup
xi4 net4 net8 vdd vddq vss vssq lsup
xi5 net5 net9 vdd vddq vss vssq lsup
xi6 zqpu<2> zqpu<1> zqpu<0> net10<2> net10<1> net10<0> vdd vddq vss vssq code_ls3
xi7 zqpd<2> zqpd<1> zqpd<0> net11<2> net11<1> net11<0> vdd vddq vss vssq code_ls3
xi8 odt_en oe rtt<2> rtt<1> rtt<0> net12<2> net12<1> net12<0> vdd vddq vss vssq odt_dec
xi9 sr<1> sr<0> net13 net14 net15 net16 vdd vddq vss vssq sr_ls
xi10 ffe<1> net17<1> vdd vddq vss vssq lsup
xi11 ffe<0> net17<0> vdd vddq vss vssq lsup
xi12 net6 net7 net10<0> net11<0> net12<0> net13 net14 net15 net16 net18<0> net19<0> vddq vssq seg_ctl
xi13 net6 net7 net10<1> net11<1> net12<1> net13 net14 net15 net16 net18<1> net19<1> vddq vssq seg_ctl
xi14 net6 net7 net10<2> net11<2> net12<2> net13 net14 net15 net16 net18<2> net19<2> vddq vssq seg_ctl
xi15 net18<0> net19<0> pad vddq vssq drv_leg1
xi16 net18<1> net19<1> pad vddq vssq drv_leg2
xi17 net18<2> net19<2> pad vddq vssq drv_leg4
xi18 net8 net9 net17<0> net20 net21 vddq vssq ffe_ctl
xi19 net20 net21 pad vddq vssq drv_leg1
xi20 net8 net9 net17<1> net22 net23 vddq vssq ffe_ctl
xi21 net22 net23 pad vddq vssq drv_leg2
xi22 pad vddq vssq esd_tx
xi23 vddq vssq pad vddq vssq drv_leg1
.ends dq_tx_unit
** End of subcircuit definition.

.END
