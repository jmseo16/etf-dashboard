** Generated for: hspiceD
** Generated on: Nov 25 09:03:48 2026
** Design library name: bytx
** Design cell name: txbyte
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: bytx_std
** Cell name: iv1
** View name: schematic
.subckt iv1 a y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mn0 y a vss vss nch w=150n l=30n m=1
.ends iv1
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: iv4
** View name: schematic
.subckt iv4 a y vdd vss
mp0 y a vdd vdd pch_lvt w=600n l=30n m=4
mn0 y a vss vss nch_lvt w=300n l=30n m=4
.ends iv4
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: na2
** View name: schematic
.subckt na2 a b y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mp1 y b vdd vdd pch w=300n l=30n m=1
mn0 y a net3 vss nch w=300n l=30n m=1
mn1 net3 b vss vss nch w=300n l=30n m=1
.ends na2
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: no2
** View name: schematic
.subckt no2 a b y vdd vss
mp0 net3 a vdd vdd pch w=600n l=30n m=1
mp1 y b net3 vdd pch w=600n l=30n m=1
mn0 y a vss vss nch w=150n l=30n m=1
mn1 y b vss vss nch w=150n l=30n m=1
.ends no2
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: aoi22
** View name: schematic
.subckt aoi22 a b c d y vdd vss
mp0 net1 a vdd vdd pch_lvt w=800n l=30n m=1
mp1 net1 b vdd vdd pch_lvt w=800n l=30n m=1
mp2 y c net1 vdd pch_lvt w=800n l=30n m=1
mp3 y d net1 vdd pch_lvt w=800n l=30n m=1
mn0 y a net2 vss nch_lvt w=400n l=30n m=1
mn1 net2 b vss vss nch_lvt w=400n l=30n m=1
mn2 y c net3 vss nch_lvt w=400n l=30n m=1
mn3 net3 d vss vss nch_lvt w=400n l=30n m=1
.ends aoi22
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: ivh
** View name: schematic
.subckt ivh a y vddq vssq
mp0 y a vddq vddq pch_18 w=2u l=150n m=1
mn0 y a vssq vssq nch_18 w=1u l=150n m=1
.ends ivh
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: nah
** View name: schematic
.subckt nah a b y vddq vssq
mp0 y a vddq vddq pch_18 w=2u l=150n m=1
mp1 y b vddq vddq pch_18 w=2u l=150n m=1
mn0 y a net3 vssq nch_18 w=2u l=150n m=1
mn1 net3 b vssq vssq nch_18 w=2u l=150n m=1
.ends nah
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: lsu
** View name: schematic
.subckt lsu in out vdd vddq vss vssq
mp2 net4 in vdd vdd pch w=300n l=30n m=1
mn2 net4 in vss vss nch w=150n l=30n m=1
mn0 net5 in vssq vssq nch_18 w=1.5u l=150n m=1
mn1 net6 net4 vssq vssq nch_18 w=1.5u l=150n m=1
mp0 net5 net6 vddq vddq pch_18 w=500n l=150n m=1
mp1 net6 net5 vddq vddq pch_18 w=500n l=150n m=1
mp3 out net5 vddq vddq pch_18 w=2u l=150n m=1
mn3 out net5 vssq vssq nch_18 w=1u l=150n m=1
.ends lsu
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: tlat
** View name: schematic
.subckt tlat d c cb q vdd vss
mn0 d c net1 vss nch_lvt w=400n l=30n m=1
mp0 d cb net1 vdd pch_lvt w=400n l=30n m=1
xi0 net1 net2 vdd vss iv1
xi1 net2 net3 vdd vss iv1
mn1 net3 cb net1 vss nch w=150n l=30n m=1
mp1 net3 c net1 vdd pch w=150n l=30n m=1
xi2 net2 q vdd vss iv1
.ends tlat
** End of subcircuit definition.

** Library name: bytx_std
** Cell name: msff
** View name: schematic
.subckt msff d ck rb q vdd vss
xi0 ck net1 vdd vss iv1
xi1 net1 net2 vdd vss iv1
xi2 rb net9 vdd vss iv1
mn0 d net1 net4 vss nch w=300n l=30n m=1
mp0 d net2 net4 vdd pch w=300n l=30n m=1
xi3 net4 rb net5 vdd vss na2
xi4 net5 net6 vdd vss iv1
mn1 net6 net2 net4 vss nch w=150n l=30n m=1
mp1 net6 net1 net4 vdd pch w=150n l=30n m=1
mn2 net5 net2 net7 vss nch w=300n l=30n m=1
mp2 net5 net1 net7 vdd pch w=300n l=30n m=1
xi5 net7 net9 q vdd vss no2
xi6 q net8 vdd vss iv1
mn3 net8 net1 net7 vss nch w=150n l=30n m=1
mp3 net8 net2 net7 vdd pch w=150n l=30n m=1
.ends msff
** End of subcircuit definition.

** Library name: bytx
** Cell name: ser4
** View name: schematic
.subckt ser4 d0 d1 d2 d3 wck wckb fck fckb q vdd vss
xi0 d0 wck wckb net1 vdd vss tlat
xi1 d1 wck wckb net2 vdd vss tlat
xi2 d2 wckb wck net3 vdd vss tlat
xi3 d3 wckb wck net4 vdd vss tlat
xi4 net1 wck net3 wckb net5 vdd vss aoi22
xi5 net2 wck net4 wckb net6 vdd vss aoi22
xi6 net6 fckb fck net7 vdd vss tlat
xi7 net5 fck net7 fckb net8 vdd vss aoi22
xi8 net8 net9 vdd vss iv1
xi9 net9 q vdd vss iv4
.ends ser4
** End of subcircuit definition.

** Library name: bytx
** Cell name: legw1
** View name: schematic
.subckt legw1 dp dn zp zn pad vddq vssq
xi0 dp zp net1 vddq vssq nah
xi1 net1 net2 vddq vssq ivh
xi2 net2 net3 vddq vssq ivh
xi3 dn zn net4 vddq vssq nah
xi4 net4 net5 vddq vssq ivh
mp0 net6 net3 vddq vddq pch_18 w=10u l=150n m=1
r0 net6 pad 480
mn0 net7 net5 vssq vssq nch_18 w=6u l=150n m=1
r1 net7 pad 480
.ends legw1
** End of subcircuit definition.

** Library name: bytx
** Cell name: legw2
** View name: schematic
.subckt legw2 dp dn zp zn pad vddq vssq
xi0 dp zp net1 vddq vssq nah
xi1 net1 net2 vddq vssq ivh
xi2 net2 net3 vddq vssq ivh
xi3 dn zn net4 vddq vssq nah
xi4 net4 net5 vddq vssq ivh
mp0 net6 net3 vddq vddq pch_18 w=10u l=150n m=2
r0 net6 pad 240
mn0 net7 net5 vssq vssq nch_18 w=6u l=150n m=2
r1 net7 pad 240
.ends legw2
** End of subcircuit definition.

** Library name: bytx
** Cell name: legw4
** View name: schematic
.subckt legw4 dp dn zp zn pad vddq vssq
xi0 dp zp net1 vddq vssq nah
xi1 net1 net2 vddq vssq ivh
xi2 net2 net3 vddq vssq ivh
xi3 dn zn net4 vddq vssq nah
xi4 net4 net5 vddq vssq ivh
mp0 net6 net3 vddq vddq pch_18 w=10u l=150n m=4
r0 net6 pad 120
mn0 net7 net5 vssq vssq nch_18 w=6u l=150n m=4
r1 net7 pad 120
.ends legw4
** End of subcircuit definition.

** Library name: bytx
** Cell name: legw8
** View name: schematic
.subckt legw8 dp dn zp zn pad vddq vssq
xi0 dp zp net1 vddq vssq nah
xi1 net1 net2 vddq vssq ivh
xi2 net2 net3 vddq vssq ivh
xi3 dn zn net4 vddq vssq nah
xi4 net4 net5 vddq vssq ivh
mp0 net6 net3 vddq vddq pch_18 w=10u l=150n m=8
r0 net6 pad 60
mn0 net7 net5 vssq vssq nch_18 w=6u l=150n m=8
r1 net7 pad 60
.ends legw8
** End of subcircuit definition.

** Library name: bytx
** Cell name: esdc
** View name: schematic
.subckt esdc pad vddq vssq
d0 pad vddq pdio_esd area=50p pj=60u
d1 vssq pad ndio_esd area=50p pj=60u
mn0 pad net1 vssq vssq nch_18 w=20u l=150n m=4
r0 net1 vssq 10k
.ends esdc
** End of subcircuit definition.

** Library name: bytx
** Cell name: drvdq
** View name: schematic
.subckt drvdq q oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 pad vdd vddq vss vssq
xi0 oe net1 vdd vss iv1
xi1 q oe net2 vdd vss na2
xi2 net2 net3 vdd vss iv1
xi3 q net1 net4 vdd vss no2
xi4 net3 net5 vdd vddq vss vssq lsu
xi5 net4 net6 vdd vddq vss vssq lsu
xi6 net5 net6 zp0 zn0 pad vddq vssq legw1
xi7 net5 net6 zp1 zn1 pad vddq vssq legw2
xi8 net5 net6 zp2 zn2 pad vddq vssq legw4
xi9 net5 net6 zp3 zn3 pad vddq vssq legw8
xi10 pad vddq vssq esdc
.ends drvdq
** End of subcircuit definition.

** Library name: bytx
** Cell name: lanedq
** View name: schematic
.subckt lanedq d0 d1 d2 d3 wck wckb fck fckb oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 pad vdd vddq vss vssq
xi0 d0 d1 d2 d3 wck wckb fck fckb net1 vdd vss ser4
xi1 net1 oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 pad vdd vddq vss vssq drvdq
.ends lanedq
** End of subcircuit definition.

** Library name: bytx
** Cell name: lanedqs
** View name: schematic
.subckt lanedqs wck wckb fck fckb oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 dqs dqsb vdd vddq vss vssq
xi0 vdd vss vdd vss wck wckb fck fckb net1 vdd vss ser4
xi1 net1 net2 vdd vss iv1
xi2 net1 oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 dqs vdd vddq vss vssq drvdq
xi3 net2 oe zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 dqsb vdd vddq vss vssq drvdq
.ends lanedqs
** End of subcircuit definition.

** Library name: bytx
** Cell name: refgen
** View name: schematic
.subckt refgen en vb vdd vss
xi0 en net1 vdd vss iv1
r0 vdd net2 25k
mp0 vb net1 net2 vdd pch w=1u l=100n m=1
mn0 vb vb vss vss nch w=1u l=1u m=2
mn1 vb net1 vss vss nch w=300n l=30n m=1
.ends refgen
** End of subcircuit definition.

** Library name: bytx
** Cell name: ckrcv
** View name: schematic
.subckt ckrcv ckt ckc en vb ck ckb vdd vss
r0 vdd net1 1k
r1 vdd net2 1k
mn0 net1 ckt net3 vss nch_lvt w=4u l=30n m=2
mn1 net2 ckc net3 vss nch_lvt w=4u l=30n m=2
mn2 net3 en net4 vss nch w=8u l=30n m=1
mn3 net4 vb vss vss nch w=1u l=1u m=8
xi0 net2 net5 vdd vss iv1
xi1 net5 ck vdd vss iv4
xi2 net1 net6 vdd vss iv1
xi3 net6 ckb vdd vss iv4
.ends ckrcv
** End of subcircuit definition.

** Library name: bytx
** Cell name: dccor
** View name: schematic
.subckt dccor a ab y yb c0 c1 c2 vdd vss
xi0 c0 net1 vdd vss iv1
xi1 c1 net2 vdd vss iv1
xi2 c2 net3 vdd vss iv1
mp0 y a vdd vdd pch_lvt w=800n l=30n m=4
mn0 y a vss vss nch_lvt w=400n l=30n m=4
mp1 yb ab vdd vdd pch_lvt w=800n l=30n m=4
mn1 yb ab vss vss nch_lvt w=400n l=30n m=4
mp2 net4 net1 vdd vdd pch_lvt w=800n l=30n m=1
mp3 y a net4 vdd pch_lvt w=800n l=30n m=1
mp4 net5 net2 vdd vdd pch_lvt w=800n l=30n m=2
mp5 y a net5 vdd pch_lvt w=800n l=30n m=2
mp6 net6 net3 vdd vdd pch_lvt w=800n l=30n m=4
mp7 y a net6 vdd pch_lvt w=800n l=30n m=4
mn2 yb ab net7 vss nch_lvt w=400n l=30n m=1
mn3 net7 c0 vss vss nch_lvt w=400n l=30n m=1
mn4 yb ab net8 vss nch_lvt w=400n l=30n m=2
mn5 net8 c1 vss vss nch_lvt w=400n l=30n m=2
mn6 yb ab net9 vss nch_lvt w=400n l=30n m=4
mn7 net9 c2 vss vss nch_lvt w=400n l=30n m=4
.ends dccor
** End of subcircuit definition.

** Library name: bytx
** Cell name: cgt
** View name: schematic
.subckt cgt ck ckb en fck fckb vdd vss
xi0 ck en net1 vdd vss na2
xi1 net1 fck vdd vss iv4
xi2 ckb en net2 vdd vss na2
xi3 net2 fckb vdd vss iv4
.ends cgt
** End of subcircuit definition.

** Library name: bytx
** Cell name: ckgen
** View name: schematic
.subckt ckgen ckt ckc pdb rstn vb c0 c1 c2 fck fckb wck wckb vdd vss
xi0 ckt ckc pdb vb net1 net2 vdd vss ckrcv
xi1 net2 net1 net3 net4 c0 c1 c2 vdd vss dccor
xi2 net3 net4 pdb fck fckb vdd vss cgt
xi3 wckb fck rstn wck vdd vss msff
xi4 wck wckb vdd vss iv1
.ends ckgen
** End of subcircuit definition.

** Library name: bytx
** Cell name: ckrep
** View name: schematic
.subckt ckrep a y vdd vss
xi0 a net1 vdd vss iv1
xi1 net1 y vdd vss iv4
.ends ckrep
** End of subcircuit definition.

** Library name: bytx
** Cell name: ckbr
** View name: schematic
.subckt ckbr a y0 y1 y2 vdd vss
xi0 a net1 vdd vss ckrep
xi1 net1 y0 vdd vss ckrep
xi2 net1 y1 vdd vss ckrep
xi3 net1 y2 vdd vss ckrep
.ends ckbr
** End of subcircuit definition.

** Library name: bytx
** Cell name: cktree
** View name: schematic
.subckt cktree fck fckb wck wckb f0 f1 f2 fb0 fb1 fb2 w0 w1 w2 wb0 wb1 wb2 vdd vss
xi0 fck f0 f1 f2 vdd vss ckbr
xi1 fckb fb0 fb1 fb2 vdd vss ckbr
xi2 wck w0 w1 w2 vdd vss ckbr
xi3 wckb wb0 wb1 wb2 vdd vss ckbr
.ends cktree
** End of subcircuit definition.

** Library name: bytx
** Cell name: zqbit
** View name: schematic
.subckt zqbit zi pdb zo vdd vddq vss vssq
xi0 zi pdb net1 vdd vss na2
xi1 net1 net2 vdd vss iv1
xi2 net2 net3 vdd vddq vss vssq lsu
xi3 net3 net4 vddq vssq ivh
xi4 net4 zo vddq vssq ivh
.ends zqbit
** End of subcircuit definition.

** Library name: bytx
** Cell name: zqdist
** View name: schematic
.subckt zqdist zqp0 zqp1 zqp2 zqp3 zqn0 zqn1 zqn2 zqn3 pdb zp0 zp1 zp2 zp3 zn0 zn1 zn2 zn3 vdd vddq vss vssq
xi0 zqp0 pdb zp0 vdd vddq vss vssq zqbit
xi1 zqp1 pdb zp1 vdd vddq vss vssq zqbit
xi2 zqp2 pdb zp2 vdd vddq vss vssq zqbit
xi3 zqp3 pdb zp3 vdd vddq vss vssq zqbit
xi4 zqn0 pdb zn0 vdd vddq vss vssq zqbit
xi5 zqn1 pdb zn1 vdd vddq vss vssq zqbit
xi6 zqn2 pdb zn2 vdd vddq vss vssq zqbit
xi7 zqn3 pdb zn3 vdd vddq vss vssq zqbit
.ends zqdist
** End of subcircuit definition.

** Library name: bytx
** Cell name: txbyte
** View name: schematic
.subckt txbyte dq0 dq1 dq2 dq3 dq4 dq5 dq6 dq7 dqs dqsb wd0 wd1 wd2 wd3 wd4 wd5 wd6 wd7 wd8 wd9 wd10 wd11 wd12 wd13 wd14 wd15 wd16 wd17 wd18 wd19 wd20 wd21 wd22 wd23 wd24 wd25 wd26 wd27 wd28 wd29 wd30 wd31 ckt ckc oe pd rstn zqp0 zqp1 zqp2 zqp3 zqn0 zqn1 zqn2 zqn3 dcc0 dcc1 dcc2 vdd vddq vss vssq
xi0 pd net1 vdd vss iv1
xi1 net1 net2 vdd vss refgen
xi2 ckt ckc net1 rstn net2 dcc0 dcc1 dcc2 net3 net4 net5 net6 vdd vss ckgen
xi3 net3 net4 net5 net6 net7 net8 net9 net10 net11 net12 net13 net14 net15 net16 net17 net18 vdd vss cktree
xi4 zqp0 zqp1 zqp2 zqp3 zqn0 zqn1 zqn2 zqn3 net1 net20 net21 net22 net23 net24 net25 net26 net27 vdd vddq vss vssq zqdist
xi10 wd0 wd1 wd2 wd3 net13 net16 net7 net10 oe net20 net21 net22 net23 net24 net25 net26 net27 dq0 vdd vddq vss vssq lanedq
xi11 wd4 wd5 wd6 wd7 net13 net16 net7 net10 oe net20 net21 net22 net23 net24 net25 net26 net27 dq1 vdd vddq vss vssq lanedq
xi12 wd8 wd9 wd10 wd11 net13 net16 net7 net10 oe net20 net21 net22 net23 net24 net25 net26 net27 dq2 vdd vddq vss vssq lanedq
xi13 wd12 wd13 wd14 wd15 net13 net16 net7 net10 oe net20 net21 net22 net23 net24 net25 net26 net27 dq3 vdd vddq vss vssq lanedq
xi14 wd16 wd17 wd18 wd19 net14 net17 net8 net11 oe net20 net21 net22 net23 net24 net25 net26 net27 dq4 vdd vddq vss vssq lanedq
xi15 wd20 wd21 wd22 wd23 net14 net17 net8 net11 oe net20 net21 net22 net23 net24 net25 net26 net27 dq5 vdd vddq vss vssq lanedq
xi16 wd24 wd25 wd26 wd27 net14 net17 net8 net11 oe net20 net21 net22 net23 net24 net25 net26 net27 dq6 vdd vddq vss vssq lanedq
xi17 wd28 wd29 wd30 wd31 net14 net17 net8 net11 oe net20 net21 net22 net23 net24 net25 net26 net27 dq7 vdd vddq vss vssq lanedq
xi18 net15 net18 net9 net12 oe net20 net21 net22 net23 net24 net25 net26 net27 dqs dqsb vdd vddq vss vssq lanedqs
xi19 vss vss vss vss net15 net18 net9 net12 vss net20 net21 net22 net23 net24 net25 net26 net27 net40 vdd vddq vss vssq lanedq
.ends txbyte
** End of subcircuit definition.

.END
