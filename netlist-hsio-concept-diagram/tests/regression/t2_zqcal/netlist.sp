** Generated for: hspiceD
** Generated on: Nov 14 10:58:02 2026
** Design library name: ddr_zqcal
** Design cell name: zqcal_top
** Design view name: schematic
**
** DDR5-style ZQ calibration engine.
**  - pull-up cal  : PU replica array on ZQ pad vs external RZQ=240 Ohm to VSS, V(zq) vs VREF
**  - pull-down cal: PU replica (cal'd code) + PD replica array on internal node npd, V(npd) vs VREF
**  - VREF = VDDQ/2 from resistor ladder with 2b trim
**  - one shared comparator (vddq preamp + vdd StrongARM latch) with phase-swapped input crossbar
**  - 6b SAR per array, 15-stage one-hot sequencer, /8 step prescaler
**  - final codes transferred to DQ driver code registers on zq_latch (only when zq_done)
** Supplies: vdd = 0.8V core, vddq = 1.1V IO.  Thick-oxide devices nch_18/pch_18 on vddq.

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    MEASOUT=1
+    PARHIER=LOCAL
+    PSF=2

** Library name: ddr_stdcell
** Cell name: inv_d1
** View name: schematic
.subckt inv_d1 a y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mn0 y a vss vss nch w=180n l=30n m=1
.ends inv_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nand2_d1
** View name: schematic
.subckt nand2_d1 a b y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mp1 y b vdd vdd pch w=360n l=30n m=1
mn0 y a net7 vss nch w=360n l=30n m=1
mn1 net7 b vss vss nch w=360n l=30n m=1
.ends nand2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nor2_d1
** View name: schematic
.subckt nor2_d1 a b y vdd vss
mp0 net9 a vdd vdd pch w=720n l=30n m=1
mp1 y b net9 vdd pch w=720n l=30n m=1
mn0 y a vss vss nch w=180n l=30n m=1
mn1 y b vss vss nch w=180n l=30n m=1
.ends nor2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nand3_d1
** View name: schematic
.subckt nand3_d1 a b c y vdd vss
mp0 y a vdd vdd pch w=360n l=30n m=1
mp1 y b vdd vdd pch w=360n l=30n m=1
mp2 y c vdd vdd pch w=360n l=30n m=1
mn0 y a net11 vss nch w=540n l=30n m=1
mn1 net11 b net12 vss nch w=540n l=30n m=1
mn2 net12 c vss vss nch w=540n l=30n m=1
.ends nand3_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: nor3_d1
** View name: schematic
.subckt nor3_d1 a b c y vdd vss
mp0 net13 a vdd vdd pch w=1.08u l=30n m=1
mp1 net14 b net13 vdd pch w=1.08u l=30n m=1
mp2 y c net14 vdd pch w=1.08u l=30n m=1
mn0 y a vss vss nch w=180n l=30n m=1
mn1 y b vss vss nch w=180n l=30n m=1
mn2 y c vss vss nch w=180n l=30n m=1
.ends nor3_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: and2_d1
** View name: schematic
.subckt and2_d1 a b y vdd vss
xi0 a b net5 vdd vss nand2_d1
xi1 net5 y vdd vss inv_d1
.ends and2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: or2_d1
** View name: schematic
.subckt or2_d1 a b y vdd vss
xi0 a b net5 vdd vss nor2_d1
xi1 net5 y vdd vss inv_d1
.ends or2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: and3_d1
** View name: schematic
.subckt and3_d1 a b c y vdd vss
xi0 a b c net6 vdd vss nand3_d1
xi1 net6 y vdd vss inv_d1
.ends and3_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: mux2_d1
** View name: schematic
** y = s ? b : a  (transmission gate)
.subckt mux2_d1 a b s y vdd vss
mp0 sb s vdd vdd pch w=270n l=30n m=1
mn0 sb s vss vss nch w=180n l=30n m=1
mn1 y sb a vss nch w=270n l=30n m=1
mp1 y s a vdd pch w=360n l=30n m=1
mn2 y s b vss nch w=270n l=30n m=1
mp2 y sb b vdd pch w=360n l=30n m=1
.ends mux2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: dffr_d1
** View name: schematic
** positive-edge DFF, active-low async reset
.subckt dffr_d1 d ck rstb q qb vdd vss
mp10 ckb ck vdd vdd pch w=270n l=30n m=1
mn10 ckb ck vss vss nch w=180n l=30n m=1
mn0 m1 ckb d vss nch w=180n l=30n m=1
mp0 m1 ck d vdd pch w=270n l=30n m=1
mp1 m1b m1 vdd vdd pch w=270n l=30n m=1
mp2 m1b rstb vdd vdd pch w=270n l=30n m=1
mn1 m1b m1 net21 vss nch w=270n l=30n m=1
mn2 net21 rstb vss vss nch w=270n l=30n m=1
mp3 m1f m1b vdd vdd pch w=180n l=30n m=1
mn3 m1f m1b vss vss nch w=135n l=30n m=1
mn4 m1 ck m1f vss nch w=135n l=30n m=1
mp4 m1 ckb m1f vdd pch w=180n l=30n m=1
mn5 s1 ck m1b vss nch w=180n l=30n m=1
mp5 s1 ckb m1b vdd pch w=270n l=30n m=1
mp6 q s1 vdd vdd pch w=360n l=30n m=1
mn6 q s1 vss vss nch w=270n l=30n m=1
mp7 qb q vdd vdd pch w=180n l=30n m=1
mp8 qb rstb vdd vdd pch w=180n l=30n m=1
mn7 qb q net22 vss nch w=180n l=30n m=1
mn8 net22 rstb vss vss nch w=180n l=30n m=1
mn9 s1 ckb qb vss nch w=135n l=30n m=1
mp9 s1 ck qb vdd pch w=180n l=30n m=1
.ends dffr_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: dffs_d1
** View name: schematic
** positive-edge DFF, active-low async set
.subckt dffs_d1 d ck setb q qb vdd vss
xi0 d net6 vdd vss inv_d1
xi1 net6 ck setb qb q vdd vss dffr_d1
.ends dffs_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: sync2_d1
** View name: schematic
.subckt sync2_d1 d ck rstb q vdd vss
xi0 d ck rstb net4 net5 vdd vss dffr_d1
xi1 net4 ck rstb q net6 vdd vss dffr_d1
.ends sync2_d1
** End of subcircuit definition.

** Library name: ddr_stdcell
** Cell name: sr_latch_nand
** View name: schematic
.subckt sr_latch_nand sb rb q qb vdd vss
mp0 q sb vdd vdd pch w=360n l=30n m=1
mp1 q qb vdd vdd pch w=360n l=30n m=1
mn0 q sb net1 vss nch w=360n l=30n m=1
mn1 net1 qb vss vss nch w=360n l=30n m=1
mp2 qb rb vdd vdd pch w=360n l=30n m=1
mp3 qb q vdd vdd pch w=360n l=30n m=1
mn2 qb rb net2 vss nch w=360n l=30n m=1
mn3 net2 q vss vss nch w=360n l=30n m=1
.ends sr_latch_nand
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_ls
** View name: schematic
** vdd -> vddq level shifter, out = in, outb = ~in (both buffered, vddq levels)
.subckt zq_ls in out outb vdd vddq vss
mp0 inb in vdd vdd pch w=360n l=30n m=1
mn0 inb in vss vss nch w=180n l=30n m=1
mn1 n1 in vss vss nch_18 w=1u l=150n m=1
mn2 n2 inb vss vss nch_18 w=1u l=150n m=1
mp1 n1 n2 vddq vddq pch_18 w=300n l=150n m=1
mp2 n2 n1 vddq vddq pch_18 w=300n l=150n m=1
mp3 outb n2 vddq vddq pch_18 w=1u l=150n m=1
mn3 outb n2 vss vss nch_18 w=500n l=150n m=1
mp4 out n1 vddq vddq pch_18 w=1u l=150n m=1
mn4 out n1 vss vss nch_18 w=500n l=150n m=1
.ends zq_ls
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_predrv
** View name: schematic
** code gating + level shift for one 6b+base replica array
** g<k>/gb<k> = (code<k> & en) at vddq, g<6>/gb<6> = en (base leg)
.subckt zq_predrv code<5> code<4> code<3> code<2> code<1> code<0> en g<6> g<5> g<4> g<3> g<2> g<1> g<0>
+ gb<6> gb<5> gb<4> gb<3> gb<2> gb<1> gb<0> vdd vddq vss
xi0<5> code<5> en c<5> vdd vss and2_d1
xi0<4> code<4> en c<4> vdd vss and2_d1
xi0<3> code<3> en c<3> vdd vss and2_d1
xi0<2> code<2> en c<2> vdd vss and2_d1
xi0<1> code<1> en c<1> vdd vss and2_d1
xi0<0> code<0> en c<0> vdd vss and2_d1
xi1<5> c<5> g<5> gb<5> vdd vddq vss zq_ls
xi1<4> c<4> g<4> gb<4> vdd vddq vss zq_ls
xi1<3> c<3> g<3> gb<3> vdd vddq vss zq_ls
xi1<2> c<2> g<2> gb<2> vdd vddq vss zq_ls
xi1<1> c<1> g<1> gb<1> vdd vddq vss zq_ls
xi1<0> c<0> g<0> gb<0> vdd vddq vss zq_ls
xi2 en g<6> gb<6> vdd vddq vss zq_ls
.ends zq_predrv
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pu_unit
** View name: schematic
** unit pull-up leg (PMOS + poly R), ~15.4k Ohm; 64 units = 240 Ohm
.subckt zq_pu_unit gb pad vddq
mp0 net1 gb vddq vddq pch_18 w=1u l=150n m=1
r0 net1 pad r=10k
.ends zq_pu_unit
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pd_unit
** View name: schematic
** unit pull-down leg (NMOS + poly R)
.subckt zq_pd_unit g pad vss
mn0 net1 g vss vss nch_18 w=500n l=150n m=1
r0 pad net1 r=10k
.ends zq_pd_unit
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pu_array
** View name: schematic
** base leg (32u) + binary-weighted code legs 32u..1u, active-low gates
.subckt zq_pu_array gb<6> gb<5> gb<4> gb<3> gb<2> gb<1> gb<0> pad vddq
xi0 gb<6> pad vddq zq_pu_unit m=32
xi1<5> gb<5> pad vddq zq_pu_unit m=32
xi1<4> gb<4> pad vddq zq_pu_unit m=16
xi1<3> gb<3> pad vddq zq_pu_unit m=8
xi1<2> gb<2> pad vddq zq_pu_unit m=4
xi1<1> gb<1> pad vddq zq_pu_unit m=2
xi1<0> gb<0> pad vddq zq_pu_unit m=1
.ends zq_pu_array
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pd_array
** View name: schematic
** base leg (32u) + binary-weighted code legs 32u..1u, active-high gates
.subckt zq_pd_array g<6> g<5> g<4> g<3> g<2> g<1> g<0> pad vss
xi0 g<6> pad vss zq_pd_unit m=32
xi1<5> g<5> pad vss zq_pd_unit m=32
xi1<4> g<4> pad vss zq_pd_unit m=16
xi1<3> g<3> pad vss zq_pd_unit m=8
xi1<2> g<2> pad vss zq_pd_unit m=4
xi1<1> g<1> pad vss zq_pd_unit m=2
xi1<0> g<0> pad vss zq_pd_unit m=1
.ends zq_pd_array
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pad_esd
** View name: schematic
** ZQ pad: ggNMOS / gate-off PMOS clamps, isolated sense tap for comparator
.subckt zq_pad_esd pad sense vddq vss
mn0 pad vss vss vss nch_18 w=40u l=200n m=4
mp0 pad vddq vddq vddq pch_18 w=40u l=200n m=4
c0 pad vss c=300f
r0 pad sense r=1k
c1 sense vss c=50f
.ends zq_pad_esd
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pu_cal_path
** View name: schematic
** pull-up calibration branch: PU replica drives ZQ pad against external RZQ
.subckt zq_pu_cal_path pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> en_pu zq zq_s vdd vddq vss
xi0 pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> en_pu net20<6> net20<5> net20<4> net20<3> net20<2> net20<1> net20<0>
+ gbu<6> gbu<5> gbu<4> gbu<3> gbu<2> gbu<1> gbu<0> vdd vddq vss zq_predrv
xi1 gbu<6> gbu<5> gbu<4> gbu<3> gbu<2> gbu<1> gbu<0> zq vddq zq_pu_array
xi2 zq zq_s vddq vss zq_pad_esd
.ends zq_pu_cal_path
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_pd_cal_path
** View name: schematic
** pull-down calibration branch: PU replica (calibrated pu code) over PD replica -> npd
.subckt zq_pd_cal_path pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> en_pd npd vdd vddq vss
xi0 pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> en_pd net30<6> net30<5> net30<4> net30<3> net30<2> net30<1> net30<0>
+ gbr<6> gbr<5> gbr<4> gbr<3> gbr<2> gbr<1> gbr<0> vdd vddq vss zq_predrv
xi1 pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> en_pd gd<6> gd<5> gd<4> gd<3> gd<2> gd<1> gd<0>
+ net31<6> net31<5> net31<4> net31<3> net31<2> net31<1> net31<0> vdd vddq vss zq_predrv
xi2 gbr<6> gbr<5> gbr<4> gbr<3> gbr<2> gbr<1> gbr<0> npd vddq zq_pu_array
xi3 gd<6> gd<5> gd<4> gd<3> gd<2> gd<1> gd<0> npd vss zq_pd_array
* weak discharge of npd while the branch is disabled (gbr<6> high)
mn0 npd gbr<6> vss vss nch_18 w=300n l=500n m=1
c0 npd vss c=100f
.ends zq_pd_cal_path
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_vref_ladder
** View name: schematic
** 32-unit ladder: tap<0>=15/32, tap<1>=16/32 (VDDQ/2), tap<2>=17/32, tap<3>=18/32 of VDDQ
.subckt zq_vref_ladder enb tap<3> tap<2> tap<1> tap<0> vddq vss
mp0 ntop enb vddq vddq pch_18 w=4u l=150n m=2
r0 ntop tap<3> r=14k
r1 tap<3> tap<2> r=1k
r2 tap<2> tap<1> r=1k
r3 tap<1> tap<0> r=1k
r4 tap<0> vss r=15k
c0 tap<1> vss c=200f
.ends zq_vref_ladder
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_vref_mux
** View name: schematic
** 2b decoded 4:1 transmission-gate tap select (vddq domain)
.subckt zq_vref_mux tap<3> tap<2> tap<1> tap<0> s1 s1b s0 s0b vout vddq vss
mp0 net40 s1 vddq vddq pch_18 w=1u l=150n m=1
mp1 e<0> s0 net40 vddq pch_18 w=1u l=150n m=1
mn0 e<0> s1 vss vss nch_18 w=300n l=150n m=1
mn1 e<0> s0 vss vss nch_18 w=300n l=150n m=1
mp2 net41 s1 vddq vddq pch_18 w=1u l=150n m=1
mp3 e<1> s0b net41 vddq pch_18 w=1u l=150n m=1
mn2 e<1> s1 vss vss nch_18 w=300n l=150n m=1
mn3 e<1> s0b vss vss nch_18 w=300n l=150n m=1
mp4 net42 s1b vddq vddq pch_18 w=1u l=150n m=1
mp5 e<2> s0 net42 vddq pch_18 w=1u l=150n m=1
mn4 e<2> s1b vss vss nch_18 w=300n l=150n m=1
mn5 e<2> s0 vss vss nch_18 w=300n l=150n m=1
mp6 net43 s1b vddq vddq pch_18 w=1u l=150n m=1
mp7 e<3> s0b net43 vddq pch_18 w=1u l=150n m=1
mn6 e<3> s1b vss vss nch_18 w=300n l=150n m=1
mn7 e<3> s0b vss vss nch_18 w=300n l=150n m=1
mp8 eb<0> e<0> vddq vddq pch_18 w=600n l=150n m=1
mn8 eb<0> e<0> vss vss nch_18 w=300n l=150n m=1
mp9 eb<1> e<1> vddq vddq pch_18 w=600n l=150n m=1
mn9 eb<1> e<1> vss vss nch_18 w=300n l=150n m=1
mp10 eb<2> e<2> vddq vddq pch_18 w=600n l=150n m=1
mn10 eb<2> e<2> vss vss nch_18 w=300n l=150n m=1
mp11 eb<3> e<3> vddq vddq pch_18 w=600n l=150n m=1
mn11 eb<3> e<3> vss vss nch_18 w=300n l=150n m=1
mn12 vout e<0> tap<0> vss nch_18 w=2u l=150n m=1
mp12 vout eb<0> tap<0> vddq pch_18 w=2u l=150n m=1
mn13 vout e<1> tap<1> vss nch_18 w=2u l=150n m=1
mp13 vout eb<1> tap<1> vddq pch_18 w=2u l=150n m=1
mn14 vout e<2> tap<2> vss nch_18 w=2u l=150n m=1
mp14 vout eb<2> tap<2> vddq pch_18 w=2u l=150n m=1
mn15 vout e<3> tap<3> vss nch_18 w=2u l=150n m=1
mp15 vout eb<3> tap<3> vddq pch_18 w=2u l=150n m=1
.ends zq_vref_mux
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_vref_gen
** View name: schematic
.subckt zq_vref_gen en vref_trim<1> vref_trim<0> vref vdd vddq vss
xi0 en net50 en_hb vdd vddq vss zq_ls
xi1 vref_trim<1> s1 s1b vdd vddq vss zq_ls
xi2 vref_trim<0> s0 s0b vdd vddq vss zq_ls
xi3 en_hb tap<3> tap<2> tap<1> tap<0> vddq vss zq_vref_ladder
xi4 tap<3> tap<2> tap<1> tap<0> s1 s1b s0 s0b vref_raw vddq vss zq_vref_mux
r0 vref_raw vref r=20k
c0 vref vss c=4p
.ends zq_vref_gen
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_bias
** View name: schematic
** 10uA external reference -> filtered NMOS bias for comparator preamp tail
.subckt zq_bias ibias en vbn vdd vss
mp0 enb en vdd vdd pch w=360n l=30n m=1
mn0 enb en vss vss nch w=180n l=30n m=1
mn1 ibias ibias vss vss nch_18 w=4u l=500n m=1
r0 ibias vbn r=20k
c0 vbn vss c=1p
mn2 vbn enb vss vss nch w=360n l=30n m=1
.ends zq_bias
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_inmux
** View name: schematic
** comparator input crossbar: ph=0 (PU cal): vinp=vref, vinn=zq_s
**                            ph=1 (PD cal): vinp=npd,  vinn=vref
.subckt zq_inmux zq_s npd vref ph vinp vinn vdd vddq vss
xi0 ph ph_h ph_hb vdd vddq vss zq_ls
mn0 vinp ph_hb vref vss nch_18 w=2u l=150n m=1
mp0 vinp ph_h vref vddq pch_18 w=2u l=150n m=1
mn1 vinp ph_h npd vss nch_18 w=2u l=150n m=1
mp1 vinp ph_hb npd vddq pch_18 w=2u l=150n m=1
mn2 vinn ph_hb zq_s vss nch_18 w=2u l=150n m=1
mp2 vinn ph_h zq_s vddq pch_18 w=2u l=150n m=1
mn3 vinn ph_h vref vss nch_18 w=2u l=150n m=1
mp3 vinn ph_hb vref vddq pch_18 w=2u l=150n m=1
.ends zq_inmux
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_preamp
** View name: schematic
** NMOS-input preamp, diode || cross-coupled PMOS loads (vddq)
.subckt zq_preamp inp inn vbn en outp outn vddq vss
mn0 ntail vbn nten vss nch_18 w=4u l=500n m=2
mn1 nten en vss vss nch w=1u l=30n m=1
mn2 outn inp ntail vss nch_18 w=8u l=300n m=2
mn3 outp inn ntail vss nch_18 w=8u l=300n m=2
mp0 outn outn vddq vddq pch_18 w=2u l=300n m=1
mp1 outp outp vddq vddq pch_18 w=2u l=300n m=1
mp2 outn outp vddq vddq pch_18 w=1.5u l=300n m=1
mp3 outp outn vddq vddq pch_18 w=1.5u l=300n m=1
.ends zq_preamp
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_sa_latch
** View name: schematic
** StrongARM regenerative latch, precharge while clk=0
.subckt zq_sa_latch inp inn clk outp outn vdd vss
mn0 ntail clk vss vss nch w=1u l=30n m=2
mn1 nx inp ntail vss nch w=2u l=60n m=2
mn2 ny inn ntail vss nch w=2u l=60n m=2
mn3 outn outp nx vss nch w=1u l=30n m=1
mn4 outp outn ny vss nch w=1u l=30n m=1
mp0 outn outp vdd vdd pch w=1u l=30n m=1
mp1 outp outn vdd vdd pch w=1u l=30n m=1
mp2 outn clk vdd vdd pch w=400n l=30n m=1
mp3 outp clk vdd vdd pch w=400n l=30n m=1
mp4 nx clk vdd vdd pch w=400n l=30n m=1
mp5 ny clk vdd vdd pch w=400n l=30n m=1
.ends zq_sa_latch
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_cmp
** View name: schematic
** q = 1 when inp > inn (sampled on clk rise, held by SR latch)
.subckt zq_cmp inp inn vbn en clk q vdd vddq vss
xi0 inp inn vbn en ap an vddq vss zq_preamp
xi1 ap an clk op on vdd vss zq_sa_latch
xi2 on op q_i qb_i vdd vss sr_latch_nand
mp0 q qb_i vdd vdd pch w=720n l=30n m=1
mn0 q qb_i vss vss nch w=360n l=30n m=1
.ends zq_cmp
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_cmp_top
** View name: schematic
.subckt zq_cmp_top zq_s npd vref ph_pd en cmp_clk ibias cmp_q vdd vddq vss
xi0 ibias en vbn_c vdd vss zq_bias
xi1 zq_s npd vref ph_pd vinp vinn vdd vddq vss zq_inmux
xi2 vinp vinn vbn_c en cmp_clk cmp_q vdd vddq vss zq_cmp
c0 vinp vss c=20f
c1 vinn vss c=20f
.ends zq_cmp_top
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_sar_bit
** View name: schematic
** SAR bit: trial-set when token is on the next-higher bit (t_up),
** decide (keep if cmp=1) when token is on this bit (t), else hold
.subckt zq_sar_bit t_up t cmp ck rstb b vdd vss
xi0 b cmp t m vdd vss mux2_d1
xi1 t_up m d vdd vss or2_d1
xi2 d ck rstb b net60 vdd vss dffr_d1
.ends zq_sar_bit
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_sar6
** View name: schematic
** 6b SAR code register; t<6> = start token, t<5:0> = bit-decision tokens
.subckt zq_sar6 t<6> t<5> t<4> t<3> t<2> t<1> t<0> cmp ck rstb b<5> b<4> b<3> b<2> b<1> b<0> vdd vss
mp0 net61 ck vdd vdd pch w=720n l=30n m=1
mn0 net61 ck vss vss nch w=360n l=30n m=1
mp1 ckl net61 vdd vdd pch w=1.44u l=30n m=1
mn1 ckl net61 vss vss nch w=720n l=30n m=1
xi0<5> t<6> t<5> cmp ckl rstb b<5> vdd vss zq_sar_bit
xi0<4> t<5> t<4> cmp ckl rstb b<4> vdd vss zq_sar_bit
xi0<3> t<4> t<3> cmp ckl rstb b<3> vdd vss zq_sar_bit
xi0<2> t<3> t<2> cmp ckl rstb b<2> vdd vss zq_sar_bit
xi0<1> t<2> t<1> cmp ckl rstb b<1> vdd vss zq_sar_bit
xi0<0> t<1> t<0> cmp ckl rstb b<0> vdd vss zq_sar_bit
.ends zq_sar6
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_fsm
** View name: schematic
** /8 step prescaler, start sync, busy/done, 15-stage one-hot sequencer
** sequence: w0 w1 (settle) | tu<5:0> (PU SAR) | td<5:0> (PD SAR) | done
.subckt zq_fsm zq_clk zq_start rstb step_clk cmp_clk w1 tu<5> tu<4> tu<3> tu<2> tu<1> tu<0> td<5> td<4> td<3> td<2> td<1> td<0>
+ busy en_pu en_pd zq_done vdd vss
xi0 q0b zq_clk rstb q0 q0b vdd vss dffr_d1
xi1 q1b q0b rstb q1 q1b vdd vss dffr_d1
xi2 q2b q1b rstb q2 q2b vdd vss dffr_d1
xi3 q2b net70 vdd vss inv_d1
xi4 net70 step_clk vdd vss inv_d1
xi5 q2 q1 q0 nlast vdd vss and3_d1
xi6 nlast busy cmp_clk vdd vss and2_d1
xi7 zq_start step_clk rstb st_s vdd vss sync2_d1
xi8 st_s step_clk rstb st_d st_db vdd vss dffr_d1
xi9 st_s st_db start_p vdd vss and2_d1
xi27 start_p busyb st_go vdd vss and2_d1
xi10 busy st_go net71 vdd vss or2_d1
xi11 td<0> td0b vdd vss inv_d1
xi12 net71 td0b busy_d vdd vss and2_d1
xi13 busy_d step_clk rstb busy busyb vdd vss dffr_d1
xi14 st_go step_clk rstb w0 net73 vdd vss dffr_d1
xi15 w0 step_clk rstb w1 net74 vdd vss dffr_d1
xi16<5> w1 step_clk rstb tu<5> net75<5> vdd vss dffr_d1
xi16<4> tu<5> step_clk rstb tu<4> net75<4> vdd vss dffr_d1
xi16<3> tu<4> step_clk rstb tu<3> net75<3> vdd vss dffr_d1
xi16<2> tu<3> step_clk rstb tu<2> net75<2> vdd vss dffr_d1
xi16<1> tu<2> step_clk rstb tu<1> net75<1> vdd vss dffr_d1
xi16<0> tu<1> step_clk rstb tu<0> net75<0> vdd vss dffr_d1
xi17<5> tu<0> step_clk rstb td<5> net76<5> vdd vss dffr_d1
xi17<4> td<5> step_clk rstb td<4> net76<4> vdd vss dffr_d1
xi17<3> td<4> step_clk rstb td<3> net76<3> vdd vss dffr_d1
xi17<2> td<3> step_clk rstb td<2> net76<2> vdd vss dffr_d1
xi17<1> td<2> step_clk rstb td<1> net76<1> vdd vss dffr_d1
xi17<0> td<1> step_clk rstb td<0> net76<0> vdd vss dffr_d1
xi18 st_go st_gob vdd vss inv_d1
xi19 td<0> done net77 vdd vss or2_d1
xi20 net77 st_gob done_d vdd vss and2_d1
xi21 done_d step_clk rstb done doneb vdd vss dffr_d1
mp0 zq_done doneb vdd vdd pch w=720n l=30n m=1
mn0 zq_done doneb vss vss nch w=360n l=30n m=1
xi22 td<5> td<4> td<3> net78 vdd vss nor3_d1
xi23 td<2> td<1> td<0> net79 vdd vss nor3_d1
xi24 net78 net79 en_pd vdd vss nand2_d1
xi25 en_pd en_pdb vdd vss inv_d1
xi26 busy en_pdb en_pu vdd vss and2_d1
.ends zq_fsm
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zq_code_reg
** View name: schematic
** DQ driver code registers, loaded on zq_latch only after zq_done; reset to mid-code 100000
.subckt zq_code_reg pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> zq_latch zq_done rstb
+ pu_code<5> pu_code<4> pu_code<3> pu_code<2> pu_code<1> pu_code<0> pd_code<5> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> vdd vss
xi0 zq_latch zq_done lat_en vdd vss and2_d1
xi1 lat_en net80 vdd vss inv_d1
xi2 net80 lat_ck vdd vss inv_d1
xi3 pu_b<5> lat_ck rstb pu_code<5> net81<5> vdd vss dffs_d1
xi4<4> pu_b<4> lat_ck rstb pu_code<4> net81<4> vdd vss dffr_d1
xi4<3> pu_b<3> lat_ck rstb pu_code<3> net81<3> vdd vss dffr_d1
xi4<2> pu_b<2> lat_ck rstb pu_code<2> net81<2> vdd vss dffr_d1
xi4<1> pu_b<1> lat_ck rstb pu_code<1> net81<1> vdd vss dffr_d1
xi4<0> pu_b<0> lat_ck rstb pu_code<0> net81<0> vdd vss dffr_d1
xi5 pd_b<5> lat_ck rstb pd_code<5> net82<5> vdd vss dffs_d1
xi6<4> pd_b<4> lat_ck rstb pd_code<4> net82<4> vdd vss dffr_d1
xi6<3> pd_b<3> lat_ck rstb pd_code<3> net82<3> vdd vss dffr_d1
xi6<2> pd_b<2> lat_ck rstb pd_code<2> net82<2> vdd vss dffr_d1
xi6<1> pd_b<1> lat_ck rstb pd_code<1> net82<1> vdd vss dffr_d1
xi6<0> pd_b<0> lat_ck rstb pd_code<0> net82<0> vdd vss dffr_d1
.ends zq_code_reg
** End of subcircuit definition.

** Library name: ddr_zqcal
** Cell name: zqcal_top
** View name: schematic
.subckt zqcal_top zq ibias_zq zq_clk zq_start zq_latch rstb vref_trim<1> vref_trim<0>
+ pu_code<5> pu_code<4> pu_code<3> pu_code<2> pu_code<1> pu_code<0> pd_code<5> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0>
+ zq_busy zq_done zq_cmp_mon vdd vddq vss
xi0 zq_clk zq_start rstb step_clk cmp_clk w1 tu<5> tu<4> tu<3> tu<2> tu<1> tu<0> td<5> td<4> td<3> td<2> td<1> td<0>
+ zq_busy en_pu en_pd zq_done vdd vss zq_fsm
xi1 w1 tu<5> tu<4> tu<3> tu<2> tu<1> tu<0> zq_cmp_mon step_clk rstb pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> vdd vss zq_sar6
xi2 tu<0> td<5> td<4> td<3> td<2> td<1> td<0> zq_cmp_mon step_clk rstb pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> vdd vss zq_sar6
xi3 pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> zq_latch zq_done rstb
+ pu_code<5> pu_code<4> pu_code<3> pu_code<2> pu_code<1> pu_code<0> pd_code<5> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> vdd vss zq_code_reg
xi4 zq_busy vref_trim<1> vref_trim<0> vref vdd vddq vss zq_vref_gen
xi5 pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> en_pu zq zq_s vdd vddq vss zq_pu_cal_path
xi6 pu_b<5> pu_b<4> pu_b<3> pu_b<2> pu_b<1> pu_b<0> pd_b<5> pd_b<4> pd_b<3> pd_b<2> pd_b<1> pd_b<0> en_pd npd vdd vddq vss zq_pd_cal_path
xi7 zq_s npd vref en_pd zq_busy cmp_clk ibias_zq zq_cmp_mon vdd vddq vss zq_cmp_top
c0 vdd vss c=10p
c1 vddq vss c=20p
.ends zqcal_top
** End of subcircuit definition.
