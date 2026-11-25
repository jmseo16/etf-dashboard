** Generated for: hspiceD
** Generated on: Nov 24 16:47:02 2026
** Design library name: ser_lib
** Design cell name: txser4_top
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: ser_stdc
** Cell name: ivx
** View name: schematic
.subckt ivx a y vcc gnd
mp0 y a vcc vcc pch_lvt w=400n l=30n m=1
mn0 y a gnd gnd nch_lvt w=200n l=30n m=1
.ends ivx
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: ivx4
** View name: schematic
.subckt ivx4 a y vcc gnd
mp0 y a vcc vcc pch_lvt w=800n l=30n m=2
mn0 y a gnd gnd nch_lvt w=400n l=30n m=2
.ends ivx4
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: nd2
** View name: schematic
.subckt nd2 a b y vcc gnd
mp0 y a vcc vcc pch_lvt w=400n l=30n m=1
mp1 y b vcc vcc pch_lvt w=400n l=30n m=1
mn0 y a net3 gnd nch_lvt w=400n l=30n m=1
mn1 net3 b gnd gnd nch_lvt w=400n l=30n m=1
.ends nd2
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: nr2
** View name: schematic
.subckt nr2 a b y vcc gnd
mp0 net3 a vcc vcc pch_lvt w=800n l=30n m=1
mp1 y b net3 vcc pch_lvt w=800n l=30n m=1
mn0 y a gnd gnd nch_lvt w=200n l=30n m=1
mn1 y b gnd gnd nch_lvt w=200n l=30n m=1
.ends nr2
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: tg
** View name: schematic
.subckt tg a y c cb vcc gnd
mn0 a c y gnd nch_lvt w=400n l=30n m=1
mp0 a cb y vcc pch_lvt w=400n l=30n m=1
.ends tg
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: tgmux2
** View name: schematic
.subckt tgmux2 i0 i1 s sb y vcc gnd
xu0 i0 y sb s vcc gnd tg
xu1 i1 y s sb vcc gnd tg
.ends tgmux2
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: dlat
** View name: schematic
.subckt dlat d c cb q vcc gnd
xu0 d net1 c cb vcc gnd tg
xu1 net1 net2 vcc gnd ivx
xu2 net2 net3 vcc gnd ivx
xu3 net3 net1 cb c vcc gnd tg
xu4 net2 q vcc gnd ivx
.ends dlat
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: dffr
** View name: schematic
.subckt dffr d ck rst q vcc gnd
xu0 ck net1 vcc gnd ivx
xu1 net1 net2 vcc gnd ivx
xu2 rst net3 vcc gnd ivx
xu3 d net4 net1 net2 vcc gnd tg
xu4 net4 net3 net5 vcc gnd nd2
xu5 net5 net6 vcc gnd ivx
xu6 net6 net4 net2 net1 vcc gnd tg
xu7 net5 net7 net2 net1 vcc gnd tg
xu8 net7 rst q vcc gnd nr2
xu9 q net8 vcc gnd ivx
xu10 net8 net7 net1 net2 vcc gnd tg
.ends dffr
** End of subcircuit definition.

** Library name: ser_stdc
** Cell name: lsh
** View name: schematic
.subckt lsh in out vcc vccio gnd gndio
mp2 net4 in vcc vcc pch_lvt w=400n l=30n m=1
mn2 net4 in gnd gnd nch_lvt w=200n l=30n m=1
mn0 net5 in gndio gndio nch_18 w=2u l=150n m=1
mn1 net6 net4 gndio gndio nch_18 w=2u l=150n m=1
mp0 net5 net6 vccio vccio pch_18 w=600n l=150n m=1
mp1 net6 net5 vccio vccio pch_18 w=600n l=150n m=1
mp3 out net5 vccio vccio pch_18 w=3.2u l=150n m=2
mn3 out net5 gndio gndio nch_18 w=1.6u l=150n m=2
.ends lsh
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: bgen
** View name: schematic
.subckt bgen en vb vcc gnd
xu0 en net1 vcc gnd ivx
r0 vcc net2 20k
mp0 vb net1 net2 vcc pch w=1u l=100n m=1
mn0 vb vb gnd gnd nch w=1u l=1u m=2
mn1 vb net1 gnd gnd nch w=400n l=30n m=1
.ends bgen
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: ckrx
** View name: schematic
.subckt ckrx inp inn en vb op on vcc gnd
r0 vcc net1 1k
r1 vcc net2 1k
mn0 net1 inp net3 gnd nch_lvt w=4u l=30n m=2
mn1 net2 inn net3 gnd nch_lvt w=4u l=30n m=2
mn2 net3 en net4 gnd nch w=8u l=30n m=1
mn3 net4 vb gnd gnd nch w=1u l=1u m=8
xu0 net2 net5 vcc gnd ivx
xu1 net5 op vcc gnd ivx4
xu2 net1 net6 vcc gnd ivx
xu3 net6 on vcc gnd ivx4
.ends ckrx
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: dcc1
** View name: schematic
.subckt dcc1 a y tp_1 tp_0 tn_1 tn_0 vcc gnd
xu0 tp_1 net1 vcc gnd ivx
xu1 tp_0 net2 vcc gnd ivx
mp0 y a vcc vcc pch_lvt w=800n l=30n m=4
mn0 y a gnd gnd nch_lvt w=400n l=30n m=4
mp1 net3 net1 vcc vcc pch_lvt w=800n l=30n m=2
mp2 y a net3 vcc pch_lvt w=800n l=30n m=2
mp3 net4 net2 vcc vcc pch_lvt w=800n l=30n m=1
mp4 y a net4 vcc pch_lvt w=800n l=30n m=1
mn1 y a net5 gnd nch_lvt w=400n l=30n m=2
mn2 net5 tn_1 gnd gnd nch_lvt w=400n l=30n m=2
mn3 y a net6 gnd nch_lvt w=400n l=30n m=1
mn4 net6 tn_0 gnd gnd nch_lvt w=400n l=30n m=1
.ends dcc1
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: cgate
** View name: schematic
.subckt cgate ck en y vcc gnd
xu0 ck en net1 vcc gnd nd2
xu1 net1 y vcc gnd ivx4
.ends cgate
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: ckbuf
** View name: schematic
.subckt ckbuf a y vcc gnd
xu0 a net1 vcc gnd ivx
xu1 net1 y vcc gnd ivx4
.ends ckbuf
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: ser4x
** View name: schematic
.subckt ser4x d_0 d_1 d_2 d_3 wk wkb fk fkb rst y yb vcc gnd
xu0 d_0 wk rst net1 vcc gnd dffr
xu1 d_1 wk rst net2 vcc gnd dffr
xu2 d_2 wk rst net3 vcc gnd dffr
xu3 d_3 wk rst net4 vcc gnd dffr
xu4 net3 wk wkb net5 vcc gnd dlat
xu5 net4 wk wkb net6 vcc gnd dlat
xu6 net5 net1 wk wkb net7 vcc gnd tgmux2
xu7 net6 net2 wk wkb net8 vcc gnd tgmux2
xu8 net7 net9 vcc gnd ivx
xu9 net8 net10 vcc gnd ivx
xu10 net10 fk fkb net11 vcc gnd dlat
xu11 net11 net9 fk fkb net12 vcc gnd tgmux2
xu12 net12 y vcc gnd ivx4
xu13 y yb vcc gnd ivx4
.ends ser4x
** End of subcircuit definition.

** Library name: ser_lib
** Cell name: txser4_top
** View name: schematic
.subckt txser4_top ckp ckn d_0 d_1 d_2 d_3 en rst tsel lpbk_en dcc_p_1 dcc_p_0 dcc_n_1 dcc_n_0 dout_p dout_n lb_out vcc vccio gnd gndio
xb0 en net1 vcc gnd bgen
xrx0 ckp ckn en net1 net2 net3 vcc gnd ckrx
xdc0 net2 net4 dcc_p_1 dcc_p_0 dcc_n_1 dcc_n_0 vcc gnd dcc1
xdc1 net3 net5 dcc_n_1 dcc_n_0 dcc_p_1 dcc_p_0 vcc gnd dcc1
xcg0 net4 en net6 vcc gnd cgate
xcg1 net5 en net7 vcc gnd cgate
xcb0 net6 net8 vcc gnd ckbuf
xcb1 net7 net9 vcc gnd ckbuf
xdv0 net10 net8 rst net11 vcc gnd dffr
xdi0 net11 net10 vcc gnd ivx
xcb2 net11 net12 vcc gnd ckbuf
xcb3 net10 net13 vcc gnd ckbuf
xts0 tsel net14 vcc gnd ivx
xtm0 d_0 gnd tsel net14 net15 vcc gnd tgmux2
xti0 net15 net16 vcc gnd ivx
xtm1 d_1 vcc tsel net14 net17 vcc gnd tgmux2
xti1 net17 net18 vcc gnd ivx
xtm2 d_2 gnd tsel net14 net19 vcc gnd tgmux2
xti2 net19 net20 vcc gnd ivx
xtm3 d_3 vcc tsel net14 net21 vcc gnd tgmux2
xti3 net21 net22 vcc gnd ivx
xsr0 net16 net18 net20 net22 net12 net13 net8 net9 rst net23 net24 vcc gnd ser4x
xls0 net24 dout_p vcc vccio gnd gndio lsh
xls1 net23 dout_n vcc vccio gnd gndio lsh
xlb0 net24 lpbk_en net25 vcc gnd nd2
xlb1 net25 lb_out vcc gnd ivx
.ends txser4_top
** End of subcircuit definition.

.END
