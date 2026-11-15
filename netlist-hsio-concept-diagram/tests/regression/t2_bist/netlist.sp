** Generated for: hspiceD
** Generated on: Nov 14 09:41:27 2026
** Design library name: hsio_bist_lib
** Design cell name: hsio_bist_top
** Design view name: schematic
**
** HSIO loopback BIST: PRBS7/PRBS15 4b-parallel generator -> 4:1 half-rate
** serializer -> CML TX driver -> internal loopback mux -> CTLE -> StrongARM
** samplers (even/odd) -> 1:4 deserializer -> self-synchronizing PRBS checker
** -> error counter / lock detect.  Mode register, start/stop control.
** Supplies: vdd = 0.9V core logic/clock, vddq = 1.0V CML/TX/RX analog.
** Nominal: 8Gb/s, ckp/ckn = 4GHz half-rate clock, word clock = 2GHz.

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: hsio_stdcell
** Cell name: inv_x1
** View name: schematic
.subckt inv_x1 a y vdd vss
mp0 y a vdd vdd pch w=400n l=30n m=1
mn0 y a vss vss nch w=200n l=30n m=1
.ends inv_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: inv_x4
** View name: schematic
.subckt inv_x4 a y vdd vss
mp0 y a vdd vdd pch_lvt w=800n l=30n m=2 nf=2
mn0 y a vss vss nch_lvt w=400n l=30n m=2 nf=2
.ends inv_x4
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: nand2_x1
** View name: schematic
.subckt nand2_x1 a b y vdd vss
mp0 y a vdd vdd pch w=400n l=30n m=1
mp1 y b vdd vdd pch w=400n l=30n m=1
mn0 y a net08 vss nch w=400n l=30n m=1
mn1 net08 b vss vss nch w=400n l=30n m=1
.ends nand2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: nor2_x1
** View name: schematic
.subckt nor2_x1 a b y vdd vss
mp0 net011 a vdd vdd pch w=800n l=30n m=1
mp1 y b net011 vdd pch w=800n l=30n m=1
mn0 y a vss vss nch w=200n l=30n m=1
mn1 y b vss vss nch w=200n l=30n m=1
.ends nor2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: nand3_x1
** View name: schematic
.subckt nand3_x1 a b c y vdd vss
mp0 y a vdd vdd pch w=400n l=30n m=1
mp1 y b vdd vdd pch w=400n l=30n m=1
mp2 y c vdd vdd pch w=400n l=30n m=1
mn0 y a net014 vss nch w=600n l=30n m=1
mn1 net014 b net015 vss nch w=600n l=30n m=1
mn2 net015 c vss vss nch w=600n l=30n m=1
.ends nand3_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: and2_x1
** View name: schematic
.subckt and2_x1 a b y vdd vss
xi0 a b net5 vdd vss nand2_x1
xi1 net5 y vdd vss inv_x1
.ends and2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: or2_x1
** View name: schematic
.subckt or2_x1 a b y vdd vss
xi0 a b net5 vdd vss nor2_x1
xi1 net5 y vdd vss inv_x1
.ends or2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: and3_x1
** View name: schematic
.subckt and3_x1 a b c y vdd vss
xi0 a b c net7 vdd vss nand3_x1
xi1 net7 y vdd vss inv_x1
.ends and3_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: xor2_x1
** View name: schematic
** static complementary XOR, y = a ^ b
.subckt xor2_x1 a b y vdd vss
mp0 ab a vdd vdd pch w=300n l=30n m=1
mn0 ab a vss vss nch w=200n l=30n m=1
mp1 bb b vdd vdd pch w=300n l=30n m=1
mn1 bb b vss vss nch w=200n l=30n m=1
mp2 net019 ab vdd vdd pch w=600n l=30n m=1
mp3 y b net019 vdd pch w=600n l=30n m=1
mp4 net020 a vdd vdd pch w=600n l=30n m=1
mp5 y bb net020 vdd pch w=600n l=30n m=1
mn2 y a net021 vss nch w=400n l=30n m=1
mn3 net021 b vss vss nch w=400n l=30n m=1
mn4 y ab net022 vss nch w=400n l=30n m=1
mn5 net022 bb vss vss nch w=400n l=30n m=1
.ends xor2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: mux2_x1
** View name: schematic
** transmission-gate mux, y = s ? b : a
.subckt mux2_x1 a b s y vdd vss
mp0 sb s vdd vdd pch w=300n l=30n m=1
mn0 sb s vss vss nch w=200n l=30n m=1
mn1 y sb a vss nch w=300n l=30n m=1
mp1 y s a vdd pch w=400n l=30n m=1
mn2 y s b vss nch w=300n l=30n m=1
mp2 y sb b vdd pch w=400n l=30n m=1
.ends mux2_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: dlat_x1
** View name: schematic
** D-latch, transparent while ck=1 (ckb is the complement, supplied externally)
.subckt dlat_x1 d ck ckb q qb vdd vss
mn0 m ck d vss nch_lvt w=300n l=30n m=1
mp0 m ckb d vdd pch_lvt w=400n l=30n m=1
mp1 qb m vdd vdd pch_lvt w=600n l=30n m=1
mn1 qb m vss vss nch_lvt w=400n l=30n m=1
mp2 q qb vdd vdd pch_lvt w=600n l=30n m=1
mn2 q qb vss vss nch_lvt w=400n l=30n m=1
mn3 m ckb q vss nch_lvt w=150n l=30n m=1
mp3 m ck q vdd pch_lvt w=200n l=30n m=1
.ends dlat_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: dff_x1
** View name: schematic
** positive-edge master/slave DFF, no reset
.subckt dff_x1 d ck q qb vdd vss
mp8 ckb ck vdd vdd pch w=300n l=30n m=1
mn8 ckb ck vss vss nch w=200n l=30n m=1
mn0 m1 ckb d vss nch w=200n l=30n m=1
mp0 m1 ck d vdd pch w=300n l=30n m=1
mp1 m1b m1 vdd vdd pch w=300n l=30n m=1
mn1 m1b m1 vss vss nch w=200n l=30n m=1
mp2 m1f m1b vdd vdd pch w=200n l=30n m=1
mn2 m1f m1b vss vss nch w=150n l=30n m=1
mn3 m1 ck m1f vss nch w=150n l=30n m=1
mp3 m1 ckb m1f vdd pch w=200n l=30n m=1
mn4 s1 ck m1b vss nch w=200n l=30n m=1
mp4 s1 ckb m1b vdd pch w=300n l=30n m=1
mp5 q s1 vdd vdd pch w=400n l=30n m=1
mn5 q s1 vss vss nch w=300n l=30n m=1
mp6 qb q vdd vdd pch w=200n l=30n m=1
mn6 qb q vss vss nch w=150n l=30n m=1
mn7 s1 ckb qb vss nch w=150n l=30n m=1
mp7 s1 ck qb vdd pch w=200n l=30n m=1
.ends dff_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: dffr_x1
** View name: schematic
** positive-edge DFF with active-low async reset (q=0 when rstb=0)
.subckt dffr_x1 d ck rstb q qb vdd vss
mp10 ckb ck vdd vdd pch w=300n l=30n m=1
mn10 ckb ck vss vss nch w=200n l=30n m=1
mn0 m1 ckb d vss nch w=200n l=30n m=1
mp0 m1 ck d vdd pch w=300n l=30n m=1
mp1 m1b m1 vdd vdd pch w=300n l=30n m=1
mp2 m1b rstb vdd vdd pch w=300n l=30n m=1
mn1 m1b m1 net21 vss nch w=300n l=30n m=1
mn2 net21 rstb vss vss nch w=300n l=30n m=1
mp3 m1f m1b vdd vdd pch w=200n l=30n m=1
mn3 m1f m1b vss vss nch w=150n l=30n m=1
mn4 m1 ck m1f vss nch w=150n l=30n m=1
mp4 m1 ckb m1f vdd pch w=200n l=30n m=1
mn5 s1 ck m1b vss nch w=200n l=30n m=1
mp5 s1 ckb m1b vdd pch w=300n l=30n m=1
mp6 q s1 vdd vdd pch w=400n l=30n m=1
mn6 q s1 vss vss nch w=300n l=30n m=1
mp7 qb q vdd vdd pch w=200n l=30n m=1
mp8 qb rstb vdd vdd pch w=200n l=30n m=1
mn7 qb q net22 vss nch w=200n l=30n m=1
mn8 net22 rstb vss vss nch w=200n l=30n m=1
mn9 s1 ckb qb vss nch w=150n l=30n m=1
mp9 s1 ck qb vdd pch w=200n l=30n m=1
.ends dffr_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: dffs_x1
** View name: schematic
** positive-edge DFF with active-low async set (q=1 when setb=0)
.subckt dffs_x1 d ck setb q qb vdd vss
xi0 d net6 vdd vss inv_x1
xi1 net6 ck setb qb q vdd vss dffr_x1
.ends dffs_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: icg_x1
** View name: schematic
** latch-based integrated clock gate, gck = ck & en(latched while ck=0)
.subckt icg_x1 en ck gck vdd vss
xi0 ck ckb_i vdd vss inv_x1
xi1 en ckb_i ck enl net9 vdd vss dlat_x1
xi2 enl ck gck vdd vss and2_x1
.ends icg_x1
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: sync2_x1
** View name: schematic
.subckt sync2_x1 d ck rstb q vdd vss
xi0 d ck rstb net4 net5 vdd vss dffr_x1
xi1 net4 ck rstb q net6 vdd vss dffr_x1
.ends sync2_x1
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: bist_bias
** View name: schematic
** 100uA external reference -> diode -> RC filtered CML tail bias vbn
.subckt bist_bias ibias en vbn vdd vss
xi0 en enb vdd vss inv_x1
mn0 ibias ibias vss vss nch_lvt w=1u l=100n m=2
r0 ibias vbn r=10k
c0 vbn vss c=2p
mn1 vbn enb vss vss nch w=400n l=30n m=1
mn2 ibias enb vss vss nch w=1u l=30n m=1
.ends bist_bias
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: ck_rx_acbuf
** View name: schematic
** AC-coupled self-biased inverter clock receiver, CML/low-swing -> CMOS
.subckt ck_rx_acbuf ckp ckn ck ckb vdd vss
c0 ckp net1 c=250f
c1 ckn net2 c=250f
r0 net1 net3 r=20k
r1 net2 net4 r=20k
mp0 net3 net1 vdd vdd pch_lvt w=2u l=30n m=2
mn0 net3 net1 vss vss nch_lvt w=1u l=30n m=2
mp1 net4 net2 vdd vdd pch_lvt w=2u l=30n m=2
mn1 net4 net2 vss vss nch_lvt w=1u l=30n m=2
mp2 net4 net3 vdd vdd pch_lvt w=400n l=30n m=1
mn2 net4 net3 vss vss nch_lvt w=200n l=30n m=1
mp3 net3 net4 vdd vdd pch_lvt w=400n l=30n m=1
mn3 net3 net4 vss vss nch_lvt w=200n l=30n m=1
mp4 ck net3 vdd vdd pch_lvt w=2u l=30n m=4
mn4 ck net3 vss vss nch_lvt w=1u l=30n m=4
mp5 ckb net4 vdd vdd pch_lvt w=2u l=30n m=4
mn5 ckb net4 vss vss nch_lvt w=1u l=30n m=4
.ends ck_rx_acbuf
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: dly_cell
** View name: schematic
** 2-inverter delay stage with binary-weighted switched load caps
.subckt dly_cell in out c<2> c<1> c<0> vdd vss
mp0 n1 in vdd vdd pch_lvt w=1u l=30n m=1
mn0 n1 in vss vss nch_lvt w=500n l=30n m=1
mn1 n1 c<0> nc0 vss nch_lvt w=400n l=30n m=1
mn2 n1 c<1> nc1 vss nch_lvt w=400n l=30n m=2
mn3 n1 c<2> nc2 vss nch_lvt w=400n l=30n m=4
c0 nc0 vss c=3f
c1 nc1 vss c=6f
c2 nc2 vss c=12f
mp1 out n1 vdd vdd pch_lvt w=2u l=30n m=1
mn4 out n1 vss vss nch_lvt w=1u l=30n m=1
.ends dly_cell
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: rxck_dly
** View name: schematic
** RX sampling-clock delay trim, code rdly<2:0>, phase-locked by weak cross-coupling
.subckt rxck_dly ck ckb rdly<2> rdly<1> rdly<0> rck rckb vdd vss
xi0 ck dp rdly<2> rdly<1> rdly<0> vdd vss dly_cell
xi1 ckb dn rdly<2> rdly<1> rdly<0> vdd vss dly_cell
mp0 dn dp vdd vdd pch_lvt w=300n l=30n m=1
mn0 dn dp vss vss nch_lvt w=150n l=30n m=1
mp1 dp dn vdd vdd pch_lvt w=300n l=30n m=1
mn1 dp dn vss vss nch_lvt w=150n l=30n m=1
xi2 dn rck vdd vss inv_x4
xi3 dp rckb vdd vss inv_x4
.ends rxck_dly
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: bist_clkgen
** View name: schematic
.subckt bist_clkgen ckp ckn rstb rdly<2> rdly<1> rdly<0> ck ckb wclk wclkb rck rckb vdd vss
xi0 ckp ckn ck_i ckb_i vdd vss ck_rx_acbuf
xi1 ckb_i ck vdd vss inv_x4
xi2 ck_i ckb vdd vss inv_x4
xi3 wclkb_i ck rstb wclk_i wclkb_i vdd vss dffr_x1
xi4 wclkb_i wclk vdd vss inv_x4
xi5 wclk_i wclkb vdd vss inv_x4
xi6 ck ckb rdly<2> rdly<1> rdly<0> rck rckb vdd vss rxck_dly
.ends bist_clkgen
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: ser_mux2_cml
** View name: schematic
** final half-rate 2:1 CML mux: op/on = a when ck=1, b when ck=0
.subckt ser_mux2_cml a ab b bb ck ckb vbn op on vddq vss
mn0 ntail vbn vss vss nch_lvt w=4u l=100n m=8
mn1 nsa ck ntail vss nch_lvt w=4u l=30n m=2
mn2 nsb ckb ntail vss nch_lvt w=4u l=30n m=2
mn3 on a nsa vss nch_lvt w=3u l=30n m=2
mn4 op ab nsa vss nch_lvt w=3u l=30n m=2
mn5 on b nsb vss nch_lvt w=3u l=30n m=2
mn6 op bb nsb vss nch_lvt w=3u l=30n m=2
r0 op vddq r=250
r1 on vddq r=250
.ends ser_mux2_cml
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: tx_cml_drv
** View name: schematic
** CML line driver, 2x50 Ohm back-termination to vddq, ~8mA tail
.subckt tx_cml_drv inp inn en vbn txp txn vddq vss
mn0 txn inp ntl vss nch_lvt w=8u l=30n m=8
mn1 txp inn ntl vss nch_lvt w=8u l=30n m=8
mn2 ntl vbn nten vss nch_lvt w=4u l=100n m=40
mn3 nten en vss vss nch_lvt w=8u l=30n m=16
r0 txp vddq r=50
r1 txn vddq r=50
c0 txp vss c=150f
c1 txn vss c=150f
.ends tx_cml_drv
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: ser4to1
** View name: schematic
** 4:1 serializer: retime @wclk, 4:2 TG mux @wclk, latch retime @ck, 2:1 CML mux @ck
** output bit order: d<0>, d<1>, d<2>, d<3>
.subckt ser4to1 d<3> d<2> d<1> d<0> wclk wclkb ck ckb vbn txs txsb vddq vdd vss
xi0<3> d<3> wclk dr<3> net040<3> vdd vss dff_x1
xi0<2> d<2> wclk dr<2> net040<2> vdd vss dff_x1
xi0<1> d<1> wclk dr<1> net040<1> vdd vss dff_x1
xi0<0> d<0> wclk dr<0> net040<0> vdd vss dff_x1
xi1<1> dr<1> wclkb wclk b1l net041<1> vdd vss dlat_x1
xi1<0> dr<0> wclkb wclk a0l net041<0> vdd vss dlat_x1
xi2<1> dr<3> wclkb wclk net042<1> net043<1> vdd vss dlat_x1
xi2<0> dr<2> wclkb wclk net042<0> net043<0> vdd vss dlat_x1
xi3<1> net042<1> wclk wclkb b3h net044<1> vdd vss dlat_x1
xi3<0> net042<0> wclk wclkb a2h net044<0> vdd vss dlat_x1
xi4 a2h a0l wclk sa vdd vss mux2_x1
xi5 b3h b1l wclk sb vdd vss mux2_x1
xi6 sa ckb ck sar sarb vdd vss dlat_x1
xi7 sb ckb ck net045 net046 vdd vss dlat_x1
xi8 net045 ck ckb sbr sbrb vdd vss dlat_x1
xi9 sar sarb sbr sbrb ck ckb vbn txs txsb vddq vss ser_mux2_cml
.ends ser4to1
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: bist_tx_hs
** View name: schematic
.subckt bist_tx_hs tx_d<3> tx_d<2> tx_d<1> tx_d<0> wclk wclkb ck ckb vbn tx_en txp txn vddq vdd vss
xi0 tx_d<3> tx_d<2> tx_d<1> tx_d<0> wclk wclkb ck ckb vbn txs txsb vddq vdd vss ser4to1
xi1 txs txsb en_q vbn txp txn vddq vss tx_cml_drv
* tx_en level buffer into vddq domain
mp0 net07 tx_en vdd vdd pch w=400n l=30n m=1
mn0 net07 tx_en vss vss nch w=200n l=30n m=1
mp1 en_q net07 vddq vddq pch w=800n l=30n m=1
mn1 en_q net07 vss vss nch w=400n l=30n m=1
c0 vbn vss c=500f
.ends bist_tx_hs
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: lpbk_mux
** View name: schematic
** RX termination + CML 2:1 mux: external pads (lpbk_en=0) or TX-pad loopback (lpbk_en=1)
.subckt lpbk_mux rxp rxn txp txn lpbk_en vbn rxi_p rxi_n vddq vdd vss
r0 rxp nvcm r=50
r1 rxn nvcm r=50
r2 vddq nvcm r=3k
r3 nvcm vss r=7k
c0 nvcm vss c=2p
r4 txp nlp_p r=200
r5 txn nlp_n r=200
xi0 lpbk_en lpbk_enb vdd vss inv_x1
mn0 ntail vbn vss vss nch_lvt w=4u l=100n m=8
mn1 nse lpbk_enb ntail vss nch_lvt w=4u l=30n m=2
mn2 nsl lpbk_en ntail vss nch_lvt w=4u l=30n m=2
mn3 rxi_n rxp nse vss nch_lvt w=3u l=30n m=2
mn4 rxi_p rxn nse vss nch_lvt w=3u l=30n m=2
mn5 rxi_n nlp_p nsl vss nch_lvt w=3u l=30n m=2
mn6 rxi_p nlp_n nsl vss nch_lvt w=3u l=30n m=2
r6 rxi_p vddq r=250
r7 rxi_n vddq r=250
.ends lpbk_mux
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: rx_ctle
** View name: schematic
** source-degenerated CTLE (RC zero), resistive loads
.subckt rx_ctle inp inn vbn en outp outn vddq vss
mn0 outn inp ns0 vss nch_lvt w=6u l=30n m=4
mn1 outp inn ns1 vss nch_lvt w=6u l=30n m=4
r0 ns0 ns1 r=400
c0 ns0 ns1 c=150f
mn2 ns0 vbn nt vss nch_lvt w=4u l=100n m=6
mn3 ns1 vbn nt vss nch_lvt w=4u l=100n m=6
mn4 nt en vss vss nch_lvt w=8u l=30n m=4
r1 outp vddq r=300
r2 outn vddq r=300
.ends rx_ctle
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: sa_strongarm
** View name: schematic
** StrongARM sense amp, precharge high while clk=0, evaluate on clk rise
.subckt sa_strongarm inp inn clk outp outn vdd vss
mn0 ntail clk vss vss nch_lvt w=2u l=30n m=2
mn1 nx inp ntail vss nch_lvt w=2u l=30n m=2
mn2 ny inn ntail vss nch_lvt w=2u l=30n m=2
mn3 outn outp nx vss nch_lvt w=1u l=30n m=1
mn4 outp outn ny vss nch_lvt w=1u l=30n m=1
mp0 outn outp vdd vdd pch_lvt w=1u l=30n m=1
mp1 outp outn vdd vdd pch_lvt w=1u l=30n m=1
mp2 outn clk vdd vdd pch_lvt w=500n l=30n m=1
mp3 outp clk vdd vdd pch_lvt w=500n l=30n m=1
mp4 nx clk vdd vdd pch_lvt w=500n l=30n m=1
mp5 ny clk vdd vdd pch_lvt w=500n l=30n m=1
.ends sa_strongarm
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: sr_latch_nand
** View name: schematic
.subckt sr_latch_nand sb rb q qb vdd vss
mp0 q sb vdd vdd pch w=400n l=30n m=1
mp1 q qb vdd vdd pch w=400n l=30n m=1
mn0 q sb net1 vss nch w=400n l=30n m=1
mn1 net1 qb vss vss nch w=400n l=30n m=1
mp2 qb rb vdd vdd pch w=400n l=30n m=1
mp3 qb q vdd vdd pch w=400n l=30n m=1
mn2 qb rb net2 vss nch w=400n l=30n m=1
mn3 net2 q vss vss nch w=400n l=30n m=1
.ends sr_latch_nand
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: rx_sampler
** View name: schematic
.subckt rx_sampler inp inn clk q qb vdd vss
xi0 inp inn clk outp outn vdd vss sa_strongarm
xi1 outn outp q qb vdd vss sr_latch_nand
.ends rx_sampler
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: rx_deser
** View name: schematic
** 2(half-rate) -> 4 deserializer; rwclk = rck/2 launched from rckb
** rx_d<0> is the oldest bit of the word
.subckt rx_deser de do rck rckb rstb rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk rwclkb vdd vss
xi0 de rck e1 net050 vdd vss dff_x1
xi1 do rck o1 net051 vdd vss dff_x1
xi2 e1 rck e2 net052 vdd vss dff_x1
xi3 o1 rck o2 net053 vdd vss dff_x1
xi4 rwclkb_i rckb rstb rwclk_i rwclkb_i vdd vss dffr_x1
xi5 rwclkb_i rwclk vdd vss inv_x4
xi6 rwclk_i rwclkb vdd vss inv_x4
xi7<3> o1 rwclk rx_d<3> net054<3> vdd vss dff_x1
xi7<2> e1 rwclk rx_d<2> net054<2> vdd vss dff_x1
xi7<1> o2 rwclk rx_d<1> net054<1> vdd vss dff_x1
xi7<0> e2 rwclk rx_d<0> net054<0> vdd vss dff_x1
.ends rx_deser
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: bist_rx_hs
** View name: schematic
.subckt bist_rx_hs rxi_p rxi_n vbn rx_en rck rckb rstb rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk rwclkb vddq vdd vss
xi0 rxi_p rxi_n vbn rx_en ap an vddq vss rx_ctle
xi1 ap an rck de net060 vdd vss rx_sampler
xi2 ap an rckb do net061 vdd vss rx_sampler
xi3 de do rck rckb rstb rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk rwclkb vdd vss rx_deser
c0 ap vss c=8f
c1 an vss c=8f
.ends bist_rx_hs
** End of subcircuit definition.

** Library name: hsio_stdcell
** Cell name: tiehi_x1
** View name: schematic
.subckt tiehi_x1 hi vdd vss
mn0 net3 net3 vss vss nch w=200n l=30n m=1
mp0 hi net3 vdd vdd pch w=300n l=30n m=1
.ends tiehi_x1
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: prbs_pred4
** View name: schematic
** 4-bit look-ahead of x^7+x^6+1 (sel=0) or x^15+x^14+1 (sel=1); r<k> = b[n-k]
** p<k> = predicted b[n+k]
.subckt prbs_pred4 r<15> r<14> r<13> r<12> r<11> r<7> r<6> r<5> r<4> r<3> sel p<3> p<2> p<1> p<0> vdd vss
xi0<3> r<3> r<4> q7<3> vdd vss xor2_x1
xi0<2> r<4> r<5> q7<2> vdd vss xor2_x1
xi0<1> r<5> r<6> q7<1> vdd vss xor2_x1
xi0<0> r<6> r<7> q7<0> vdd vss xor2_x1
xi1<3> r<11> r<12> q15<3> vdd vss xor2_x1
xi1<2> r<12> r<13> q15<2> vdd vss xor2_x1
xi1<1> r<13> r<14> q15<1> vdd vss xor2_x1
xi1<0> r<14> r<15> q15<0> vdd vss xor2_x1
xi2<3> q7<3> q15<3> sel p<3> vdd vss mux2_x1
xi2<2> q7<2> q15<2> sel p<2> vdd vss mux2_x1
xi2<1> q7<1> q15<1> sel p<1> vdd vss mux2_x1
xi2<0> q7<0> q15<0> sel p<0> vdd vss mux2_x1
.ends prbs_pred4
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: prbs_gen
** View name: schematic
** 4b/word parallel PRBS7/PRBS15 generator (Fibonacci LFSR, 4 steps per wclk)
** state r<k> = b[n-k]; tx_d<3:1> = r<1:3>, tx_d<0> = r<4> ^ inj (single-bit error inject)
.subckt prbs_gen wclk gen_run prbs_sel inj rstb tx_d<3> tx_d<2> tx_d<1> tx_d<0> vdd vss
xi0 gen_run wclk gclk vdd vss icg_x1
xi1 p<3> gclk rstb tx_d<3> net070 vdd vss dffs_x1
xi2<2> p<2> gclk rstb tx_d<2> net071<2> vdd vss dffr_x1
xi2<3> p<1> gclk rstb tx_d<1> net071<3> vdd vss dffr_x1
xi2<4> p<0> gclk rstb r<4> net071<4> vdd vss dffr_x1
xi2<5> tx_d<3> gclk rstb r<5> net071<5> vdd vss dffr_x1
xi2<6> tx_d<2> gclk rstb r<6> net071<6> vdd vss dffr_x1
xi2<7> tx_d<1> gclk rstb r<7> net071<7> vdd vss dffr_x1
xi2<8> r<4> gclk rstb r<8> net071<8> vdd vss dffr_x1
xi2<9> r<5> gclk rstb r<9> net071<9> vdd vss dffr_x1
xi2<10> r<6> gclk rstb r<10> net071<10> vdd vss dffr_x1
xi2<11> r<7> gclk rstb r<11> net071<11> vdd vss dffr_x1
xi2<12> r<8> gclk rstb r<12> net071<12> vdd vss dffr_x1
xi2<13> r<9> gclk rstb r<13> net071<13> vdd vss dffr_x1
xi2<14> r<10> gclk rstb r<14> net071<14> vdd vss dffr_x1
xi2<15> r<11> gclk rstb r<15> net071<15> vdd vss dffr_x1
xi3 r<15> r<14> r<13> r<12> r<11> r<7> r<6> r<5> r<4> tx_d<1> prbs_sel p<3> p<2> p<1> p<0> vdd vss prbs_pred4
xi4 r<4> inj tx_d<0> vdd vss xor2_x1
.ends prbs_gen
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: prbs_chk
** View name: schematic
** self-synchronizing PRBS checker: received history c<k> = b[n-k] predicts rx_d<3:0>
.subckt prbs_chk rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk prbs_sel chk_run rstb err_q run_s vdd vss
xi0 chk_run rwclk rstb run_s vdd vss sync2_x1
xi1<1> rx_d<3> rwclk c<1> net080<1> vdd vss dff_x1
xi1<2> rx_d<2> rwclk c<2> net080<2> vdd vss dff_x1
xi1<3> rx_d<1> rwclk c<3> net080<3> vdd vss dff_x1
xi1<4> rx_d<0> rwclk c<4> net080<4> vdd vss dff_x1
xi1<5> c<1> rwclk c<5> net080<5> vdd vss dff_x1
xi1<6> c<2> rwclk c<6> net080<6> vdd vss dff_x1
xi1<7> c<3> rwclk c<7> net080<7> vdd vss dff_x1
xi1<8> c<4> rwclk c<8> net080<8> vdd vss dff_x1
xi1<9> c<5> rwclk c<9> net080<9> vdd vss dff_x1
xi1<10> c<6> rwclk c<10> net080<10> vdd vss dff_x1
xi1<11> c<7> rwclk c<11> net080<11> vdd vss dff_x1
xi1<12> c<8> rwclk c<12> net080<12> vdd vss dff_x1
xi1<13> c<9> rwclk c<13> net080<13> vdd vss dff_x1
xi1<14> c<10> rwclk c<14> net080<14> vdd vss dff_x1
xi1<15> c<11> rwclk c<15> net080<15> vdd vss dff_x1
xi2 c<15> c<14> c<13> c<12> c<11> c<7> c<6> c<5> c<4> c<3> prbs_sel p<3> p<2> p<1> p<0> vdd vss prbs_pred4
xi3<3> rx_d<3> p<3> e<3> vdd vss xor2_x1
xi3<2> rx_d<2> p<2> e<2> vdd vss xor2_x1
xi3<1> rx_d<1> p<1> e<1> vdd vss xor2_x1
xi3<0> rx_d<0> p<0> e<0> vdd vss xor2_x1
xi4 e<0> e<1> n01 vdd vss nor2_x1
xi5 e<2> e<3> n23 vdd vss nor2_x1
xi6 n01 n23 e_any vdd vss nand2_x1
xi7 e_any run_s err_d vdd vss and2_x1
xi8 err_d rwclk rstb err_q net081 vdd vss dffr_x1
.ends prbs_chk
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: err_cnt10
** View name: schematic
** 10b ripple error counter (counts error words after lock) + sticky overflow
.subckt err_cnt10 err_q run_s lock rwclkb clr_b cnt<9> cnt<8> cnt<7> cnt<6> cnt<5> cnt<4> cnt<3> cnt<2> cnt<1> cnt<0> ovf vdd vss
xi0 err_q lock run_s en1 vdd vss and3_x1
xi1 en1 ovfb rwclkb net090 vdd vss nand3_x1
xi2 net090 cnt_clk vdd vss inv_x1
xi3<0> cntb<0> cnt_clk clr_b cnt<0> cntb<0> vdd vss dffr_x1
xi3<1> cntb<1> cntb<0> clr_b cnt<1> cntb<1> vdd vss dffr_x1
xi3<2> cntb<2> cntb<1> clr_b cnt<2> cntb<2> vdd vss dffr_x1
xi3<3> cntb<3> cntb<2> clr_b cnt<3> cntb<3> vdd vss dffr_x1
xi3<4> cntb<4> cntb<3> clr_b cnt<4> cntb<4> vdd vss dffr_x1
xi3<5> cntb<5> cntb<4> clr_b cnt<5> cntb<5> vdd vss dffr_x1
xi3<6> cntb<6> cntb<5> clr_b cnt<6> cntb<6> vdd vss dffr_x1
xi3<7> cntb<7> cntb<6> clr_b cnt<7> cntb<7> vdd vss dffr_x1
xi3<8> cntb<8> cntb<7> clr_b cnt<8> cntb<8> vdd vss dffr_x1
xi3<9> cntb<9> cntb<8> clr_b cnt<9> cntb<9> vdd vss dffr_x1
xi4 net091 vdd vss tiehi_x1
xi5 net091 cntb<9> clr_b ovf ovfb vdd vss dffr_x1
.ends err_cnt10
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: lock_det4
** View name: schematic
** 4b saturating counter of consecutive error-free words; lock after 15 clean words
.subckt lock_det4 err_q run_s rwclk clr_b lock vdd vss
xi0 run_s run_sb vdd vss inv_x1
xi1 err_q run_sb ok vdd vss nor2_x1
xi2 q<0> q<1> c1 vdd vss and2_x1
xi3 c1 q<2> c2 vdd vss and2_x1
xi4 c2 q<3> sat vdd vss and2_x1
xi5 sat satb vdd vss inv_x1
xi6 q<0> satb t<1> vdd vss and2_x1
xi7 c1 satb t<2> vdd vss and2_x1
xi8 c2 satb t<3> vdd vss and2_x1
xi9<3> q<3> t<3> x<3> vdd vss xor2_x1
xi9<2> q<2> t<2> x<2> vdd vss xor2_x1
xi9<1> q<1> t<1> x<1> vdd vss xor2_x1
xi9<0> q<0> satb x<0> vdd vss xor2_x1
xi10<3> x<3> ok d<3> vdd vss and2_x1
xi10<2> x<2> ok d<2> vdd vss and2_x1
xi10<1> x<1> ok d<1> vdd vss and2_x1
xi10<0> x<0> ok d<0> vdd vss and2_x1
xi11<3> d<3> rwclk clr_b q<3> net100<3> vdd vss dffr_x1
xi11<2> d<2> rwclk clr_b q<2> net100<2> vdd vss dffr_x1
xi11<1> d<1> rwclk clr_b q<1> net100<1> vdd vss dffr_x1
xi11<0> d<0> rwclk clr_b q<0> net100<0> vdd vss dffr_x1
xi12 sat ok lk_d vdd vss and2_x1
xi13 lk_d rwclk clr_b lock net101 vdd vss dffr_x1
.ends lock_det4
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: mode_reg
** View name: schematic
** 9b mode register, parallel write on cfg_wr rising edge
** cfg<8>=prbs_sel cfg<7>=lpbk_en cfg<6>=tx_en cfg<5>=rx_en cfg<4>=chk_en
** cfg<3>=err_inj cfg<2:0>=rdly<2:0>
.subckt mode_reg cfg<8> cfg<7> cfg<6> cfg<5> cfg<4> cfg<3> cfg<2> cfg<1> cfg<0> cfg_wr rstb prbs_sel lpbk_en tx_en rx_en chk_en err_inj rdly<2> rdly<1> rdly<0> vdd vss
xi0 cfg_wr net110 vdd vss inv_x1
xi1 net110 wr_ckb vdd vss inv_x1
xi2<8> cfg<8> wr_ckb rstb prbs_sel net111<8> vdd vss dffr_x1
xi2<7> cfg<7> wr_ckb rstb lpbk_en net111<7> vdd vss dffr_x1
xi2<6> cfg<6> wr_ckb rstb tx_en net111<6> vdd vss dffr_x1
xi2<5> cfg<5> wr_ckb rstb rx_en net111<5> vdd vss dffr_x1
xi2<4> cfg<4> wr_ckb rstb chk_en net111<4> vdd vss dffr_x1
xi2<3> cfg<3> wr_ckb rstb err_inj net111<3> vdd vss dffr_x1
xi2<2> cfg<2> wr_ckb rstb rdly<2> net111<2> vdd vss dffr_x1
xi2<1> cfg<1> wr_ckb rstb rdly<1> net111<1> vdd vss dffr_x1
xi2<0> cfg<0> wr_ckb rstb rdly<0> net111<0> vdd vss dffr_x1
.ends mode_reg
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: bist_ctrl
** View name: schematic
** start/stop run FSM (wclk domain), err_inj edge -> 1-cycle inject pulse
.subckt bist_ctrl bist_start bist_stop err_inj tx_en chk_en rstb wclk gen_run chk_run inj_p clr_b bist_busy bist_done vdd vss
xi0 bist_start wclk rstb st_s vdd vss sync2_x1
xi1 bist_stop wclk rstb sp_s vdd vss sync2_x1
xi2 err_inj wclk rstb ij_s vdd vss sync2_x1
xi3 st_s wclk rstb st_d st_db vdd vss dffr_x1
xi4 st_s st_db start_p vdd vss and2_x1
xi5 ij_s wclk rstb ij_d ij_db vdd vss dffr_x1
xi6 ij_s ij_db inj_p vdd vss and2_x1
xi7 run start_p net120 vdd vss or2_x1
xi8 sp_s sp_sb vdd vss inv_x1
xi9 net120 sp_sb d_run vdd vss and2_x1
xi10 d_run wclk rstb run runb vdd vss dffr_x1
xi11 run sp_s net121 vdd vss and2_x1
xi12 done net121 net122 vdd vss or2_x1
xi13 start_p start_pb vdd vss inv_x1
xi14 net122 start_pb d_done vdd vss and2_x1
xi15 d_done wclk rstb done doneb vdd vss dffr_x1
xi16 run tx_en gen_run vdd vss and2_x1
xi17 run chk_en chk_run vdd vss and2_x1
xi18 rstb start_pb clr_b vdd vss and2_x1
mp0 bist_busy runb vdd vdd pch w=800n l=30n m=1
mn0 bist_busy runb vss vss nch w=400n l=30n m=1
mp1 bist_done doneb vdd vdd pch w=800n l=30n m=1
mn1 bist_done doneb vss vss nch w=400n l=30n m=1
.ends bist_ctrl
** End of subcircuit definition.

** Library name: hsio_bist_lib
** Cell name: hsio_bist_top
** View name: schematic
.subckt hsio_bist_top ckp ckn rxp rxn txp txn ibias rstb bist_en bist_start bist_stop cfg<8> cfg<7> cfg<6> cfg<5> cfg<4> cfg<3> cfg<2> cfg<1> cfg<0> cfg_wr
+ err_cnt<9> err_cnt<8> err_cnt<7> err_cnt<6> err_cnt<5> err_cnt<4> err_cnt<3> err_cnt<2> err_cnt<1> err_cnt<0> err_ovf bist_lock bist_err bist_busy bist_done vdd vddq vss
xi0 ibias bist_en vbn vdd vss bist_bias
xi1 ckp ckn rstb rdly<2> rdly<1> rdly<0> ck ckb wclk wclkb rck rckb vdd vss bist_clkgen
xi2 cfg<8> cfg<7> cfg<6> cfg<5> cfg<4> cfg<3> cfg<2> cfg<1> cfg<0> cfg_wr rstb prbs_sel lpbk_en tx_en rx_en chk_en err_inj rdly<2> rdly<1> rdly<0> vdd vss mode_reg
xi3 bist_start bist_stop err_inj tx_en chk_en rstb wclk gen_run chk_run inj_p clr_b bist_busy bist_done vdd vss bist_ctrl
xi4 wclk gen_run prbs_sel inj_p rstb tx_d<3> tx_d<2> tx_d<1> tx_d<0> vdd vss prbs_gen
xi5 tx_d<3> tx_d<2> tx_d<1> tx_d<0> wclk wclkb ck ckb vbn tx_en txp txn vddq vdd vss bist_tx_hs
xi6 rxp rxn txp txn lpbk_en vbn rxi_p rxi_n vddq vdd vss lpbk_mux
xi7 rxi_p rxi_n vbn rx_en rck rckb rstb rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk rwclkb vddq vdd vss bist_rx_hs
xi8 rx_d<3> rx_d<2> rx_d<1> rx_d<0> rwclk prbs_sel chk_run rstb bist_err run_s vdd vss prbs_chk
xi9 bist_err run_s rwclk clr_b bist_lock vdd vss lock_det4
xi10 bist_err run_s bist_lock rwclkb clr_b err_cnt<9> err_cnt<8> err_cnt<7> err_cnt<6> err_cnt<5> err_cnt<4> err_cnt<3> err_cnt<2> err_cnt<1> err_cnt<0> err_ovf vdd vss err_cnt10
c0 vdd vss c=20p
c1 vddq vss c=20p
.ends hsio_bist_top
** End of subcircuit definition.
