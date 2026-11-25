** Generated for: hspiceD
** Generated on: Nov 22 15:03:18 2026
** Design library name: wr_byte
** Design cell name: rxbyte_eq
** Design view name: schematic

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: wr_std
** Cell name: invx1
** View name: schematic
.subckt invx1 a y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mn0 y a vss vss nch w=150n l=30n m=1
.ends invx1
** End of subcircuit definition.

** Library name: wr_std
** Cell name: invx4
** View name: schematic
.subckt invx4 a y vdd vss
mp0 y a vdd vdd pch_lvt w=600n l=30n m=2
mn0 y a vss vss nch_lvt w=300n l=30n m=2
.ends invx4
** End of subcircuit definition.

** Library name: wr_std
** Cell name: nand2x1
** View name: schematic
.subckt nand2x1 a b y vdd vss
mp0 y a vdd vdd pch w=300n l=30n m=1
mp1 y b vdd vdd pch w=300n l=30n m=1
mn0 y a net3 vss nch w=300n l=30n m=1
mn1 net3 b vss vss nch w=300n l=30n m=1
.ends nand2x1
** End of subcircuit definition.

** Library name: wr_std
** Cell name: nand2x2
** View name: schematic
.subckt nand2x2 a b y vdd vss
mp0 y a vdd vdd pch_lvt w=600n l=30n m=1
mp1 y b vdd vdd pch_lvt w=600n l=30n m=1
mn0 y a net3 vss nch_lvt w=600n l=30n m=1
mn1 net3 b vss vss nch_lvt w=600n l=30n m=1
.ends nand2x2
** End of subcircuit definition.

** Library name: wr_std
** Cell name: lvlup
** View name: schematic
.subckt lvlup in out outb vdd vddq vss
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
.ends lvlup
** End of subcircuit definition.

** Library name: wr_std
** Cell name: lat_tg
** View name: schematic
.subckt lat_tg d en enb q vdd vss
mn0 d en net7 vss nch w=300n l=30n m=1
mp0 d enb net7 vdd pch w=300n l=30n m=1
xi0 net7 net8 vdd vss invx1
xi1 net8 q vdd vss invx1
mn1 q enb net7 vss nch w=150n l=30n m=1
mp1 q en net7 vdd pch w=150n l=30n m=1
.ends lat_tg
** End of subcircuit definition.

** Library name: wr_std
** Cell name: dfftg
** View name: schematic
.subckt dfftg d ck q vdd vss
xi0 ck net10 vdd vss invx1
xi1 net10 net11 vdd vss invx1
mn0 d net10 net12 vss nch w=300n l=30n m=1
mp0 d net11 net12 vdd pch w=300n l=30n m=1
xi2 net12 net13 vdd vss invx1
xi3 net13 net14 vdd vss invx1
mn1 net14 net11 net12 vss nch w=150n l=30n m=1
mp1 net14 net10 net12 vdd pch w=150n l=30n m=1
mn2 net13 net11 net15 vss nch w=300n l=30n m=1
mp2 net13 net10 net15 vdd pch w=300n l=30n m=1
xi4 net15 net16 vdd vss invx1
xi5 net16 net17 vdd vss invx1
mn3 net17 net10 net15 vss nch w=150n l=30n m=1
mp3 net17 net11 net15 vdd pch w=150n l=30n m=1
xi6 net15 q vdd vss invx1
.ends dfftg
** End of subcircuit definition.

** Library name: wr_std
** Cell name: mux2tg
** View name: schematic
.subckt mux2tg d0 d1 s z vdd vss
xi0 s net18 vdd vss invx1
mn0 d0 net18 z vss nch_lvt w=300n l=30n m=1
mp0 d0 s z vdd pch_lvt w=300n l=30n m=1
mn1 d1 s z vss nch_lvt w=300n l=30n m=1
mp1 d1 net18 z vdd pch_lvt w=300n l=30n m=1
.ends mux2tg
** End of subcircuit definition.

** Library name: wr_std
** Cell name: dlybuf
** View name: schematic
.subckt dlybuf a y vdd vss
mp0 net19 a vdd vdd pch w=300n l=60n m=1
mn0 net19 a vss vss nch w=150n l=60n m=1
mp1 y net19 vdd vdd pch w=300n l=60n m=1
mn1 y net19 vss vss nch w=150n l=60n m=1
.ends dlybuf
** End of subcircuit definition.

** Library name: wr_std
** Cell name: ckbuf
** View name: schematic
.subckt ckbuf a y vdd vss
xi0 a net20 vdd vss invx4
xi1 net20 y vdd vss invx4
.ends ckbuf
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: padesd
** View name: schematic
.subckt padesd pad pad_r vddq vssq
d0 pad vddq pdio_esd area=60p pj=64u
d1 vssq pad ndio_esd area=60p pj=64u
r0 pad pad_r rppolywo w=2u l=1.2u
d2 pad_r vddq pdio_esd area=6p pj=14u
d3 vssq pad_r ndio_esd area=6p pj=14u
mn0 pad_r net21 vssq vssq nch_18 w=20u l=150n m=2
r1 net21 vssq rppolyhri w=0.4u l=4u
.ends padesd
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: odtleg3
** View name: schematic
.subckt odtleg3 pad enb2 enb1 enb0 vddq
mp2 net24 enb2 vddq vddq pch_18 w=24u l=100n m=4
r2 net24 pad rppolywo w=4u l=1.2u m=4
mp1 net23 enb1 vddq vddq pch_18 w=24u l=100n m=2
r1 net23 pad rppolywo w=4u l=1.2u m=2
mp0 net22 enb0 vddq vddq pch_18 w=24u l=100n m=1
r0 net22 pad rppolywo w=4u l=1.2u m=1
.ends odtleg3
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: odtctl
** View name: schematic
.subckt odtctl odt_en rtt2 rtt1 rtt0 enb2 enb1 enb0 vdd vddq vss
xi2 odt_en rtt2 net25 vdd vss nand2x1
xi1 odt_en rtt1 net26 vdd vss nand2x1
xi0 odt_en rtt0 net27 vdd vss nand2x1
xi5 net25 enb2 net28 vdd vddq vss lvlup
xi4 net26 enb1 net29 vdd vddq vss lvlup
xi3 net27 enb0 net30 vdd vddq vss lvlup
.ends odtctl
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: biasgen
** View name: schematic
.subckt biasgen ibias en vbp vdd vddq vss vssq
xi0 en net31 vdd vss invx1
mn0 ibias ibias vssq vssq nch_18 w=2u l=400n m=4
mn1 vbp ibias vssq vssq nch_18 w=2u l=400n m=4
mp0 vbp vbp vddq vddq pch_18 w=4u l=400n m=4
mn2 ibias net31 vssq vssq nch_18 w=1u l=150n m=1
mp1 vbp en vddq vddq pch_18 w=1u l=150n m=1
.ends biasgen
** End of subcircuit definition.

** Library name: wr_std
** Cell name: mux2hv
** View name: schematic
.subckt mux2hv d0 d1 s sb z vddq vssq
mn0 d0 sb z vssq nch_18 w=1u l=150n m=1
mp0 d0 s z vddq pch_18 w=1u l=150n m=1
mn1 d1 s z vssq nch_18 w=1u l=150n m=1
mp1 d1 sb z vddq pch_18 w=1u l=150n m=1
.ends mux2hv
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: vrefbuf
** View name: schematic
.subckt vrefbuf inp out vbp vddq vssq
mp0 net40 vbp vddq vddq pch_18 w=4u l=400n m=4
mp1 net41 inp net40 vddq pch_18 w=4u l=200n m=4
mp2 out out net40 vddq pch_18 w=4u l=200n m=4
mn0 net41 net41 vssq vssq nch_18 w=2u l=400n m=2
mn1 out net41 vssq vssq nch_18 w=2u l=400n m=2
c0 net41 out mimcap_2p0 w=10u l=10u
.ends vrefbuf
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: vrefrs
** View name: schematic
.subckt vrefrs c4 c3 c2 c1 c0 vbp vref vdd vddq vss vssq
xi0 c0 net300 net305 vdd vddq vss lvlup
xi1 c1 net301 net306 vdd vddq vss lvlup
xi2 c2 net302 net307 vdd vddq vss lvlup
xi3 c3 net303 net308 vdd vddq vss lvlup
xi4 c4 net304 net309 vdd vddq vss lvlup
r40 net100 vssq rppolywo w=1u l=16u
r0 net100 net101 rppolywo w=1u l=2u
r1 net101 net102 rppolywo w=1u l=2u
r2 net102 net103 rppolywo w=1u l=2u
r3 net103 net104 rppolywo w=1u l=2u
r4 net104 net105 rppolywo w=1u l=2u
r5 net105 net106 rppolywo w=1u l=2u
r6 net106 net107 rppolywo w=1u l=2u
r7 net107 net108 rppolywo w=1u l=2u
r8 net108 net109 rppolywo w=1u l=2u
r9 net109 net110 rppolywo w=1u l=2u
r10 net110 net111 rppolywo w=1u l=2u
r11 net111 net112 rppolywo w=1u l=2u
r12 net112 net113 rppolywo w=1u l=2u
r13 net113 net114 rppolywo w=1u l=2u
r14 net114 net115 rppolywo w=1u l=2u
r15 net115 net116 rppolywo w=1u l=2u
r16 net116 net117 rppolywo w=1u l=2u
r17 net117 net118 rppolywo w=1u l=2u
r18 net118 net119 rppolywo w=1u l=2u
r19 net119 net120 rppolywo w=1u l=2u
r20 net120 net121 rppolywo w=1u l=2u
r21 net121 net122 rppolywo w=1u l=2u
r22 net122 net123 rppolywo w=1u l=2u
r23 net123 net124 rppolywo w=1u l=2u
r24 net124 net125 rppolywo w=1u l=2u
r25 net125 net126 rppolywo w=1u l=2u
r26 net126 net127 rppolywo w=1u l=2u
r27 net127 net128 rppolywo w=1u l=2u
r28 net128 net129 rppolywo w=1u l=2u
r29 net129 net130 rppolywo w=1u l=2u
r30 net130 net131 rppolywo w=1u l=2u
r41 net131 vddq rppolywo w=1u l=10u
xi10 net100 net101 net300 net305 net140 vddq vssq mux2hv
xi11 net102 net103 net300 net305 net141 vddq vssq mux2hv
xi12 net104 net105 net300 net305 net142 vddq vssq mux2hv
xi13 net106 net107 net300 net305 net143 vddq vssq mux2hv
xi14 net108 net109 net300 net305 net144 vddq vssq mux2hv
xi15 net110 net111 net300 net305 net145 vddq vssq mux2hv
xi16 net112 net113 net300 net305 net146 vddq vssq mux2hv
xi17 net114 net115 net300 net305 net147 vddq vssq mux2hv
xi18 net116 net117 net300 net305 net148 vddq vssq mux2hv
xi19 net118 net119 net300 net305 net149 vddq vssq mux2hv
xi20 net120 net121 net300 net305 net150 vddq vssq mux2hv
xi21 net122 net123 net300 net305 net151 vddq vssq mux2hv
xi22 net124 net125 net300 net305 net152 vddq vssq mux2hv
xi23 net126 net127 net300 net305 net153 vddq vssq mux2hv
xi24 net128 net129 net300 net305 net154 vddq vssq mux2hv
xi25 net130 net131 net300 net305 net155 vddq vssq mux2hv
xi26 net140 net141 net301 net306 net156 vddq vssq mux2hv
xi27 net142 net143 net301 net306 net157 vddq vssq mux2hv
xi28 net144 net145 net301 net306 net158 vddq vssq mux2hv
xi29 net146 net147 net301 net306 net159 vddq vssq mux2hv
xi30 net148 net149 net301 net306 net160 vddq vssq mux2hv
xi31 net150 net151 net301 net306 net161 vddq vssq mux2hv
xi32 net152 net153 net301 net306 net162 vddq vssq mux2hv
xi33 net154 net155 net301 net306 net163 vddq vssq mux2hv
xi34 net156 net157 net302 net307 net164 vddq vssq mux2hv
xi35 net158 net159 net302 net307 net165 vddq vssq mux2hv
xi36 net160 net161 net302 net307 net166 vddq vssq mux2hv
xi37 net162 net163 net302 net307 net167 vddq vssq mux2hv
xi38 net164 net165 net303 net308 net168 vddq vssq mux2hv
xi39 net166 net167 net303 net308 net169 vddq vssq mux2hv
xi40 net168 net169 net304 net309 net170 vddq vssq mux2hv
xi41 net170 net171 vbp vddq vssq vrefbuf
r42 net171 vref rppolyhri w=0.4u l=6u
mn0 vssq vref vssq vssq nch_18 w=20u l=2u m=4
.ends vrefrs
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: dqsamp
** View name: schematic
.subckt dqsamp inp inn vbn en outp outn vddq vssq
r0 vddq outn rppolywo w=0.4u l=2.4u
r1 vddq outp rppolywo w=0.4u l=2.4u
mn0 outn inp net52 vssq nch_18 w=4u l=100n m=2
mn1 outp inn net52 vssq nch_18 w=4u l=100n m=2
mn2 net52 en net53 vssq nch_18 w=8u l=100n m=1
mn3 net53 vbn vssq vssq nch_18 w=4u l=400n m=4
.ends dqsamp
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: acamp
** View name: schematic
.subckt acamp in out en vdd vss
c0 in net54 mimcap_2p0 w=6u l=6u
r0 net54 net55 rppolyhri w=0.4u l=20u
mp0 net55 net54 vdd vdd pch_lvt w=1.2u l=40n m=1
mn0 net55 net54 net56 vss nch_lvt w=600n l=40n m=1
mn1 net56 en vss vss nch w=1.2u l=30n m=1
mp1 net55 en vdd vdd pch w=300n l=30n m=1
xi0 net55 out vdd vss invx4
.ends acamp
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: dqsrx
** View name: schematic
.subckt dqsrx inp inn vbn enq en ckt ckc vdd vddq vss vssq
xi0 inp inn vbn enq net57 net58 vddq vssq dqsamp
xi1 net57 net59 en vdd vss acamp
xi2 net58 net60 en vdd vss acamp
xi3 net59 net60 vdd vss invx1
xi4 net60 net59 vdd vss invx1
xi5 net59 net61 vdd vss invx1
xi6 net61 ckt vdd vss invx4
xi7 net60 net62 vdd vss invx1
xi8 net62 ckc vdd vss invx4
.ends dqsrx
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: dqsgate
** View name: schematic
.subckt dqsgate ckt ckc open gt gc vdd vss
xi0 open ckc ckt net63 vdd vss lat_tg
xi1 open ckt ckc net64 vdd vss lat_tg
xi2 ckt net63 net65 vdd vss nand2x2
xi3 net65 gt vdd vss invx4
xi4 ckc net64 net66 vdd vss nand2x2
xi5 net66 gc vdd vss invx4
.ends dqsgate
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: dly3
** View name: schematic
.subckt dly3 in out s2 s1 s0 vdd vss
xi0 in net67 vdd vss dlybuf
xi1 in net67 s0 net68 vdd vss mux2tg
xi2 net68 net69 vdd vss dlybuf
xi3 net69 net70 vdd vss dlybuf
xi4 net70 net71 vdd vss dlybuf
xi5 net69 net71 s1 net72 vdd vss mux2tg
xi6 net72 net73 vdd vss dlybuf
xi7 net73 net74 vdd vss dlybuf
xi8 net74 net75 vdd vss dlybuf
xi9 net75 net76 vdd vss dlybuf
xi10 net76 net77 vdd vss dlybuf
xi11 net73 net77 s2 net78 vdd vss mux2tg
xi12 net78 out vdd vss dlybuf
.ends dly3
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: ctledg
** View name: schematic
.subckt ctledg inp inn pk1 pk0 vbn en enb outp outn vddq vssq
mp2 net80 enb vddq vddq pch_18 w=16u l=100n m=1
r0 net80 outn rppolywo w=0.4u l=3u
r1 net80 outp rppolywo w=0.4u l=3u
mp0 outn vssq net80 vddq pch_18 w=1u l=200n m=1
mp1 outp vssq net80 vddq pch_18 w=1u l=200n m=1
mn0 outn inp net81 vssq nch_18 w=4u l=100n m=2
mn1 outp inn net82 vssq nch_18 w=4u l=100n m=2
r2 net81 net82 rppolywo w=1u l=1.5u
mn2 net81 en net83 vssq nch_18 w=8u l=100n m=1
mn3 net83 vbn vssq vssq nch_18 w=4u l=400n m=2
mn4 net82 en net84 vssq nch_18 w=8u l=100n m=1
mn5 net84 vbn vssq vssq nch_18 w=4u l=400n m=2
mn6 net81 pk1 net85 vssq nch_18 w=2u l=150n m=2
c0 net85 net82 mimcap_2p0 w=8u l=8u
mn7 net81 pk0 net86 vssq nch_18 w=2u l=150n m=1
c1 net86 net82 mimcap_2p0 w=6u l=6u
.ends ctledg
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: sadfe1
** View name: schematic
.subckt sadfe1 inp inn ck h1p h1n w3 w2 w1 w0 outp outn vdd vss
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
mn10 net86 h1p net87 vss nch_lvt w=250n l=30n m=8
mn11 net85 h1n net87 vss nch_lvt w=250n l=30n m=8
mn12 net87 w3 net84 vss nch_lvt w=500n l=30n m=8
mn13 net86 h1p net88 vss nch_lvt w=250n l=30n m=4
mn14 net85 h1n net88 vss nch_lvt w=250n l=30n m=4
mn15 net88 w2 net84 vss nch_lvt w=500n l=30n m=4
mn16 net86 h1p net89 vss nch_lvt w=250n l=30n m=2
mn17 net85 h1n net89 vss nch_lvt w=250n l=30n m=2
mn18 net89 w1 net84 vss nch_lvt w=500n l=30n m=2
mn19 net86 h1p net90 vss nch_lvt w=250n l=30n m=1
mn20 net85 h1n net90 vss nch_lvt w=250n l=30n m=1
mn21 net90 w0 net84 vss nch_lvt w=500n l=30n m=1
.ends sadfe1
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: srnand
** View name: schematic
.subckt srnand sb rb q qb vdd vss
xi0 sb qb q vdd vss nand2x2
xi1 rb q qb vdd vss nand2x2
.ends srnand
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: dqslice
** View name: schematic
.subckt dqslice pad vref ckt ckc en enb vbn pk1 pk0 w3 w2 w1 w0 odtb2 odtb1 odtb0 qr qf vdd vddq vss vssq
xi0 pad net92 vddq vssq padesd
xi1 pad odtb2 odtb1 odtb0 vddq odtleg3
xi2 net92 vref pk1 pk0 vbn en enb net93 net94 vddq vssq ctledg
xi4 net93 net94 ckt net101 net102 w3 w2 w1 w0 net95 net96 vdd vss sadfe1
xi5 net96 net95 net99 net100 vdd vss srnand
xi6 net93 net94 ckc net99 net100 w3 w2 w1 w0 net97 net98 vdd vss sadfe1
xi7 net98 net97 net101 net102 vdd vss srnand
xi8 net99 net103 vdd vss invx1
xi9 net103 qr vdd vss invx4
xi10 net101 net104 vdd vss invx1
xi11 net104 qf vdd vss invx4
.ends dqslice
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: wldet
** View name: schematic
.subckt wldet d ck en q vdd vss
xi0 ck en net105 vdd vss nand2x2
xi1 net105 net106 vdd vss invx4
xi2 d net106 net107 vdd vss dfftg
xi3 net107 net108 vdd vss invx1
xi4 net108 q vdd vss invx4
.ends wldet
** End of subcircuit definition.

** Library name: wr_byte
** Cell name: rxbyte_eq
** View name: schematic
.subckt rxbyte_eq dq7 dq6 dq5 dq4 dq3 dq2 dq1 dq0 dqs_t dqs_c qr7 qr6 qr5 qr4 qr3 qr2 qr1 qr0 qf7 qf6 qf5 qf4 qf3 qf2 qf1 qf0 wl_out rx_en gate_open wl_en wl_ck slp odt_en rtt2 rtt1 rtt0 vrc4 vrc3 vrc2 vrc1 vrc0 t1w3 t1w2 t1w1 t1w0 pk1 pk0 ddl2 ddl1 ddl0 ibias vdd vddq vss vssq
mp0 net200 slp vdd vdd pch_hvt w=12u l=40n m=16
xi0 rx_en net201 net202 vdd vddq vss lvlup
xi1 ibias rx_en net203 vdd vddq vss vssq biasgen
xi2 vrc4 vrc3 vrc2 vrc1 vrc0 net203 net204 vdd vddq vss vssq vrefrs
xi3 odt_en rtt2 rtt1 rtt0 net207 net206 net205 vdd vddq vss odtctl
xi40 pk1 net226 net227 vdd vddq vss lvlup
xi41 pk0 net228 net229 vdd vddq vss lvlup
xi4 dqs_t net208 vddq vssq padesd
xi5 dqs_c net209 vddq vssq padesd
xi6 dqs_t net207 net206 net205 vddq odtleg3
xi7 dqs_c net207 net206 net205 vddq odtleg3
xi8 net208 net209 ibias net201 rx_en net210 net211 vdd vddq vss vssq dqsrx
xi9 net210 net211 gate_open net212 net213 vdd vss dqsgate
xi10 net212 net214 ddl2 ddl1 ddl0 vdd vss dly3
xi11 net213 net215 ddl2 ddl1 ddl0 vdd vss dly3
d0 vss net214 ndio_ant area=0.12p pj=1.4u
d1 vss net215 ndio_ant area=0.12p pj=1.4u
xi12 net214 net216 vdd vss ckbuf
xi13 net215 net217 vdd vss ckbuf
xi14 net216 net218 vdd vss ckbuf
xi15 net216 net218 vdd vss ckbuf
xi16 net217 net219 vdd vss ckbuf
xi17 net217 net219 vdd vss ckbuf
xi18 net216 net220 vdd vss ckbuf
xi19 net216 net220 vdd vss ckbuf
xi20 net217 net221 vdd vss ckbuf
xi21 net217 net221 vdd vss ckbuf
xi22 net216 net222 vdd vss ckbuf
xi23 net217 net223 vdd vss ckbuf
xi30 dq0 net204 net218 net219 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr0 qf0 net200 vddq vss vssq dqslice
xi31 dq1 net204 net218 net219 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr1 qf1 net200 vddq vss vssq dqslice
xi32 dq2 net204 net218 net219 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr2 qf2 net200 vddq vss vssq dqslice
xi33 dq3 net204 net218 net219 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr3 qf3 net200 vddq vss vssq dqslice
xi34 dq4 net204 net220 net221 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr4 qf4 net200 vddq vss vssq dqslice
xi35 dq5 net204 net220 net221 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr5 qf5 net200 vddq vss vssq dqslice
xi36 dq6 net204 net220 net221 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr6 qf6 net200 vddq vss vssq dqslice
xi37 dq7 net204 net220 net221 net201 net202 ibias net226 net228 t1w3 t1w2 t1w1 t1w0 net207 net206 net205 qr7 qf7 net200 vddq vss vssq dqslice
xi38 vssq net204 net222 net223 vssq vddq ibias vssq vssq vss vss vss vss vddq vddq vddq net224 net225 net200 vddq vss vssq dqslice
xi39 wl_ck net222 wl_en wl_out vdd vss wldet
.ends rxbyte_eq
** End of subcircuit definition.

.END
