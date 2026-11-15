** Generated for: hspiceD
** Generated on: Nov 14 09:12:44 2026
** Design library name: NFIO_IO
** Design cell name: nf_io_top
** Design view name: schematic

.TEMP 25.0
.OPTION ARTIST=2 INGOLD=2 PARHIER=LOCAL PSF=2

** Device model cards (placeholder, keeps this netlist self-contained)
.MODEL nch     NMOS LEVEL=54 VERSION=4.5 VTH0=0.40  TOXE=2.1n
.MODEL pch     PMOS LEVEL=54 VERSION=4.5 VTH0=-0.40 TOXE=2.1n
.MODEL nch_lvt NMOS LEVEL=54 VERSION=4.5 VTH0=0.30  TOXE=2.1n
.MODEL pch_lvt PMOS LEVEL=54 VERSION=4.5 VTH0=-0.30 TOXE=2.1n
.MODEL nch_hv  NMOS LEVEL=54 VERSION=4.5 VTH0=0.50  TOXE=5.2n
.MODEL pch_hv  PMOS LEVEL=54 VERSION=4.5 VTH0=-0.50 TOXE=5.2n

** Library name: NFIO_STD
** Cell name: inv_x1
** View name: schematic
.subckt inv_x1 in out vdd vss
MM0 out in vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 out in vdd vdd pch W=0.4u L=0.06u m=1 nf=1
.ends inv_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: inv_x2
** View name: schematic
.subckt inv_x2 in out vdd vss
MM0 out in vss vss nch W=0.4u L=0.06u m=1 nf=2
MM1 out in vdd vdd pch W=0.8u L=0.06u m=1 nf=2
.ends inv_x2
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: inv_lvt_x2
** View name: schematic
.subckt inv_lvt_x2 in out vdd vss
MM0 out in vss vss nch_lvt W=0.4u L=0.06u m=1 nf=1
MM1 out in vdd vdd pch_lvt W=0.8u L=0.06u m=1 nf=2
.ends inv_lvt_x2
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nand2_x1
** View name: schematic
.subckt nand2_x1 a b out vdd vss
MM0 out a net08 vss nch W=0.4u L=0.06u m=1 nf=1
MM1 net08 b vss vss nch W=0.4u L=0.06u m=1 nf=1
MM2 out a vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM3 out b vdd vdd pch W=0.4u L=0.06u m=1 nf=1
.ends nand2_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nor2_x1
** View name: schematic
.subckt nor2_x1 a b out vdd vss
MM0 out a vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 out b vss vss nch W=0.2u L=0.06u m=1 nf=1
MM2 net08 a vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM3 out b net08 vdd pch W=0.8u L=0.06u m=1 nf=1
.ends nor2_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nand3_x1
** View name: schematic
.subckt nand3_x1 a b c out vdd vss
MM0 out a net09 vss nch W=0.6u L=0.06u m=1 nf=1
MM1 net09 b net010 vss nch W=0.6u L=0.06u m=1 nf=1
MM2 net010 c vss vss nch W=0.6u L=0.06u m=1 nf=1
MM3 out a vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM4 out b vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM5 out c vdd vdd pch W=0.4u L=0.06u m=1 nf=1
.ends nand3_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nor3_x1
** View name: schematic
.subckt nor3_x1 a b c out vdd vss
MM0 out a vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 out b vss vss nch W=0.2u L=0.06u m=1 nf=1
MM2 out c vss vss nch W=0.2u L=0.06u m=1 nf=1
MM3 net09 a vdd vdd pch W=1.2u L=0.06u m=1 nf=2
MM4 net010 b net09 vdd pch W=1.2u L=0.06u m=1 nf=2
MM5 out c net010 vdd pch W=1.2u L=0.06u m=1 nf=2
.ends nor3_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: xor2_x1
** View name: schematic
.subckt xor2_x1 a b out vdd vss
MM0 ab a vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 ab a vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM2 bb b vss vss nch W=0.2u L=0.06u m=1 nf=1
MM3 bb b vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM4 out a net011 vss nch W=0.4u L=0.06u m=1 nf=1
MM5 net011 b vss vss nch W=0.4u L=0.06u m=1 nf=1
MM6 out ab net012 vss nch W=0.4u L=0.06u m=1 nf=1
MM7 net012 bb vss vss nch W=0.4u L=0.06u m=1 nf=1
MM8 net013 a vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM9 net013 b vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM10 out ab net013 vdd pch W=0.8u L=0.06u m=1 nf=1
MM11 out bb net013 vdd pch W=0.8u L=0.06u m=1 nf=1
.ends xor2_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: xnor2_x1
** View name: schematic
.subckt xnor2_x1 a b out vdd vss
MM0 ab a vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 ab a vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM2 bb b vss vss nch W=0.2u L=0.06u m=1 nf=1
MM3 bb b vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM4 out a net011 vss nch W=0.4u L=0.06u m=1 nf=1
MM5 net011 bb vss vss nch W=0.4u L=0.06u m=1 nf=1
MM6 out ab net012 vss nch W=0.4u L=0.06u m=1 nf=1
MM7 net012 b vss vss nch W=0.4u L=0.06u m=1 nf=1
MM8 net013 a vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM9 net013 bb vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM10 out ab net013 vdd pch W=0.8u L=0.06u m=1 nf=1
MM11 out b net013 vdd pch W=0.8u L=0.06u m=1 nf=1
.ends xnor2_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nand2_lvt
** View name: schematic
.subckt nand2_lvt a b out vdd vss
MM0 out a net08 vss nch_lvt W=0.8u L=0.06u m=1 nf=2
MM1 net08 b vss vss nch_lvt W=0.8u L=0.06u m=1 nf=2
MM2 out a vdd vdd pch_lvt W=0.8u L=0.06u m=1 nf=2
MM3 out b vdd vdd pch_lvt W=0.8u L=0.06u m=1 nf=2
.ends nand2_lvt
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: inv_q
** View name: schematic
.subckt inv_q in out vccq vssq
MM0 out in vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM1 out in vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
.ends inv_q
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nand2_q
** View name: schematic
.subckt nand2_q a b out vccq vssq
MM0 out a net08 vssq nch_hv W=2u L=0.2u m=1 nf=1
MM1 net08 b vssq vssq nch_hv W=2u L=0.2u m=1 nf=1
MM2 out a vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM3 out b vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
.ends nand2_q
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: nor2_q
** View name: schematic
.subckt nor2_q a b out vccq vssq
MM0 out a vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM1 out b vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM2 net08 a vccq vccq pch_hv W=4u L=0.2u m=1 nf=2
MM3 out b net08 vccq pch_hv W=4u L=0.2u m=1 nf=2
.ends nor2_q
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: tie_hilo
** View name: schematic
.subckt tie_hilo hi lo vdd vss
MM0 net05 net05 vss vss nch W=0.2u L=0.06u m=1 nf=1
MM1 hi net05 vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM2 net06 net06 vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM3 lo net06 vss vss nch W=0.2u L=0.06u m=1 nf=1
.ends tie_hilo
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: ls_up
** View name: schematic
.subckt ls_up in out outb vdd vss vccq vssq
MM0 inb in vss vss nch W=0.3u L=0.06u m=1 nf=1
MM1 inb in vdd vdd pch W=0.6u L=0.06u m=1 nf=1
MM2 net09 in vssq vssq nch_hv W=2u L=0.2u m=1 nf=1
MM3 net010 inb vssq vssq nch_hv W=2u L=0.2u m=1 nf=1
MM4 net09 net010 vccq vccq pch_hv W=0.5u L=0.2u m=1 nf=1
MM5 net010 net09 vccq vccq pch_hv W=0.5u L=0.2u m=1 nf=1
MM6 out net09 vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM7 out net09 vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM8 outb out vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM9 outb out vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
.ends ls_up
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: ls_dn
** View name: schematic
.subckt ls_dn in out vccq vssq vdd vss
MM0 net07 in vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM1 net07 in vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM2 out net07 vss vss nch_hv W=1u L=0.2u m=1 nf=1
MM3 out net07 vdd vdd pch_hv W=2u L=0.2u m=1 nf=1
.ends ls_dn
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: ckbuf
** View name: schematic
.subckt ckbuf in out vdd vss
MM0 net03 in vss vss nch_lvt W=0.6u L=0.06u m=1 nf=1
MM1 net03 in vdd vdd pch_lvt W=1.2u L=0.06u m=1 nf=2
MM2 out net03 vss vss nch_lvt W=2.4u L=0.06u m=1 nf=4
MM3 out net03 vdd vdd pch_lvt W=4.8u L=0.06u m=1 nf=4
.ends ckbuf
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: ckbuf_x8
** View name: schematic
.subckt ckbuf_x8 in out vdd vss
MM0 net03 in vss vss nch_lvt W=1.2u L=0.06u m=1 nf=2
MM1 net03 in vdd vdd pch_lvt W=2.4u L=0.06u m=1 nf=4
MM2 out net03 vss vss nch_lvt W=4.8u L=0.06u m=1 nf=8
MM3 out net03 vdd vdd pch_lvt W=9.6u L=0.06u m=1 nf=8
.ends ckbuf_x8
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: ckgate
** View name: schematic
.subckt ckgate ck en out vdd vss
XI0 ck en net04 vdd vss nand2_lvt
XI1 net04 out vdd vss inv_lvt_x2
.ends ckgate
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: mux2_x1
** View name: schematic
.subckt mux2_x1 d0 d1 s sb z vdd vss
XI0 d0 sb net05 vdd vss nand2_x1
XI1 d1 s net06 vdd vss nand2_x1
XI2 net05 net06 z vdd vss nand2_x1
.ends mux2_x1
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: dff_tg
** View name: schematic
.subckt dff_tg d ck q vdd vss
XI0 ck ckb vdd vss inv_x1
XI1 ckb cki vdd vss inv_x1
MM0 d ckb m1 vss nch W=0.3u L=0.06u m=1 nf=1
MM1 d cki m1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI2 m1 m2 vdd vss inv_x1
XI3 m2 m3 vdd vss inv_x1
MM2 m3 cki m1 vss nch W=0.2u L=0.06u m=1 nf=1
MM3 m3 ckb m1 vdd pch W=0.2u L=0.06u m=1 nf=1
MM4 m2 cki s1 vss nch W=0.3u L=0.06u m=1 nf=1
MM5 m2 ckb s1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI4 s1 q vdd vss inv_x1
XI5 q s3 vdd vss inv_x1
MM6 s3 ckb s1 vss nch W=0.2u L=0.06u m=1 nf=1
MM7 s3 cki s1 vdd pch W=0.2u L=0.06u m=1 nf=1
.ends dff_tg
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: dffr_tg
** View name: schematic
.subckt dffr_tg d ck rn q qb vdd vss
XI0 ck ckb vdd vss inv_x1
XI1 ckb cki vdd vss inv_x1
XI6 rn rst vdd vss inv_x1
MM0 d ckb m1 vss nch W=0.3u L=0.06u m=1 nf=1
MM1 d cki m1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI2 m1 rn m2 vdd vss nand2_x1
XI3 m2 m3 vdd vss inv_x1
MM2 m3 cki m1 vss nch W=0.2u L=0.06u m=1 nf=1
MM3 m3 ckb m1 vdd pch W=0.2u L=0.06u m=1 nf=1
MM4 m2 cki s1 vss nch W=0.3u L=0.06u m=1 nf=1
MM5 m2 ckb s1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI4 s1 rst q vdd vss nor2_x1
XI5 q s3 vdd vss inv_x1
MM6 s3 ckb s1 vss nch W=0.2u L=0.06u m=1 nf=1
MM7 s3 cki s1 vdd pch W=0.2u L=0.06u m=1 nf=1
XI7 q qb vdd vss inv_x1
.ends dffr_tg
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: dffs_tg
** View name: schematic
.subckt dffs_tg d ck sn q qb vdd vss
XI0 ck ckb vdd vss inv_x1
XI1 ckb cki vdd vss inv_x1
XI6 sn set vdd vss inv_x1
MM0 d ckb m1 vss nch W=0.3u L=0.06u m=1 nf=1
MM1 d cki m1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI2 m1 set m2 vdd vss nor2_x1
XI3 m2 m3 vdd vss inv_x1
MM2 m3 cki m1 vss nch W=0.2u L=0.06u m=1 nf=1
MM3 m3 ckb m1 vdd pch W=0.2u L=0.06u m=1 nf=1
MM4 m2 cki s1 vss nch W=0.3u L=0.06u m=1 nf=1
MM5 m2 ckb s1 vdd pch W=0.4u L=0.06u m=1 nf=1
XI4 s1 sn q vdd vss nand2_x1
XI5 q s3 vdd vss inv_x1
MM6 s3 ckb s1 vss nch W=0.2u L=0.06u m=1 nf=1
MM7 s3 cki s1 vdd pch W=0.2u L=0.06u m=1 nf=1
XI7 q qb vdd vss inv_x1
.ends dffs_tg
** End of subcircuit definition.

** Library name: NFIO_STD
** Cell name: latch_tg
** View name: schematic
.subckt latch_tg d en enb q vdd vss
MM0 d en l1 vss nch_lvt W=0.4u L=0.06u m=1 nf=1
MM1 d enb l1 vdd pch_lvt W=0.6u L=0.06u m=1 nf=1
XI0 l1 lb vdd vss inv_x1
XI1 lb q vdd vss inv_lvt_x2
MM2 q enb l1 vss nch W=0.2u L=0.06u m=1 nf=1
MM3 q en l1 vdd pch W=0.2u L=0.06u m=1 nf=1
.ends latch_tg
** End of subcircuit definition.

** Library name: NFIO_ESD
** Cell name: esd_io_pad
** View name: schematic
.subckt esd_io_pad pad pad_rx vccq vssq
MM0 pad net05 vccq vccq pch_hv W=60u L=0.3u m=2 nf=12
RR0 net05 vccq 10k
MM1 pad net06 vssq vssq nch_hv W=60u L=0.3u m=2 nf=12
RR1 net06 vssq 10k
RR2 pad pad_rx 200
MM2 pad_rx vssq vssq vssq nch_hv W=10u L=0.3u m=1 nf=2
.ends esd_io_pad
** End of subcircuit definition.

** Library name: NFIO_ESD
** Cell name: esd_prim
** View name: schematic
.subckt esd_prim pad vccq vssq
MM0 pad net05 vccq vccq pch_hv W=60u L=0.3u m=2 nf=12
RR0 net05 vccq 10k
MM1 pad net06 vssq vssq nch_hv W=60u L=0.3u m=2 nf=12
RR1 net06 vssq 10k
.ends esd_prim
** End of subcircuit definition.

** Library name: NFIO_ESD
** Cell name: esd_rc_clamp
** View name: schematic
.subckt esd_rc_clamp vtop vbot
RR0 vtop net05 500k
CC0 net05 vbot 1p
MM0 net06 net05 vbot vbot nch_hv W=2u L=0.2u m=1 nf=1
MM1 net06 net05 vtop vtop pch_hv W=8u L=0.2u m=1 nf=2
MM2 net07 net06 vbot vbot nch_hv W=8u L=0.2u m=1 nf=2
MM3 net07 net06 vtop vtop pch_hv W=8u L=0.2u m=1 nf=2
MM4 net08 net07 vbot vbot nch_hv W=16u L=0.2u m=1 nf=4
MM5 net08 net07 vtop vtop pch_hv W=48u L=0.2u m=1 nf=8
MMclamp vtop net08 vbot vbot nch_hv W=50u L=0.2u m=40 nf=20
.ends esd_rc_clamp
** End of subcircuit definition.

** Library name: NFIO_ESD
** Cell name: esd_b2b
** View name: schematic
.subckt esd_b2b va vb
MM0 va va vb vb nch_hv W=20u L=0.3u m=2 nf=4
MM1 vb vb va va nch_hv W=20u L=0.3u m=2 nf=4
.ends esd_b2b
** End of subcircuit definition.

** Library name: NFIO_ESD
** Cell name: esd_rail
** View name: schematic
.subckt esd_rail vdd vss vccq vssq
XI0 vccq vssq esd_rc_clamp
XI1 vdd vss esd_rc_clamp
XI2 vss vssq esd_b2b
.ends esd_rail
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rpt_buf
** View name: schematic
.subckt rpt_buf in out vdd vss
MM0 net03 in vss vss nch_lvt W=1.2u L=0.06u m=1 nf=2
MM1 net03 in vdd vdd pch_lvt W=2.4u L=0.06u m=1 nf=4
MM2 out net03 vss vss nch_lvt W=4.8u L=0.06u m=1 nf=8
MM3 out net03 vdd vdd pch_lvt W=9.6u L=0.06u m=1 nf=8
.ends rpt_buf
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: wire_rc_rx
** View name: schematic
.subckt wire_rc_rx a b vss
CC0 a vss 8f
RR0 a b 120
CC1 b vss 8f
.ends wire_rc_rx
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_tg_q
** View name: schematic
.subckt rx_tg_q a z en enb vccq vssq
MM0 a en z vssq nch_hv W=4u L=0.2u m=1 nf=2
MM1 a enb z vccq pch_hv W=8u L=0.2u m=1 nf=4
.ends rx_tg_q
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: amux2_q
** View name: schematic
.subckt amux2_q d0 d1 s sb z vccq vssq
MM0 d1 s z vssq nch_hv W=1u L=0.2u m=1 nf=1
MM1 d1 sb z vccq pch_hv W=2u L=0.2u m=1 nf=1
MM2 d0 sb z vssq nch_hv W=1u L=0.2u m=1 nf=1
MM3 d0 s z vccq pch_hv W=2u L=0.2u m=1 nf=1
.ends amux2_q
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_amp_bz
** View name: schematic
.subckt rx_amp_bz inp inn en_q enb_q out vccq vssq
MMN1 nbias inp ntail vssq nch_hv W=4u L=0.2u m=2 nf=2
MMN2 out inn ntail vssq nch_hv W=4u L=0.2u m=2 nf=2
MMP1 nbias inp ptail vccq pch_hv W=8u L=0.2u m=2 nf=4
MMP2 out inn ptail vccq pch_hv W=8u L=0.2u m=2 nf=4
MMNT ntail nbias net011 vssq nch_hv W=6u L=0.2u m=2 nf=2
MMPT ptail nbias net012 vccq pch_hv W=12u L=0.2u m=2 nf=4
MMNE net011 en_q vssq vssq nch_hv W=8u L=0.2u m=1 nf=2
MMPE net012 enb_q vccq vccq pch_hv W=16u L=0.2u m=1 nf=4
MM0 nbias en_q vccq vccq pch_hv W=1u L=0.2u m=1 nf=1
MM1 out enb_q vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
.ends rx_amp_bz
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_ls_dn
** View name: schematic
.subckt rx_ls_dn in out vccq vssq vdd vss
MM0 net07 in vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM1 net07 in vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM2 out net07 vss vss nch_hv W=1.5u L=0.2u m=1 nf=1
MM3 out net07 vdd vdd pch_hv W=3u L=0.2u m=1 nf=2
.ends rx_ls_dn
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: vref_buf_ota
** View name: schematic
.subckt vref_buf_ota inp inn out ib en enb vccq vssq
MM0 ib ib vssq vssq nch_hv W=2u L=1u m=1 nf=1
MM1 ntail ib vssq vssq nch_hv W=4u L=1u m=2 nf=1
MM2 net05 inn ntail vssq nch_hv W=4u L=0.5u m=2 nf=1
MM3 net06 inp ntail vssq nch_hv W=4u L=0.5u m=2 nf=1
MM4 net05 net05 vccq vccq pch_hv W=4u L=0.5u m=2 nf=1
MM5 net06 net05 vccq vccq pch_hv W=4u L=0.5u m=2 nf=1
MM6 out net06 vccq vccq pch_hv W=8u L=0.3u m=4 nf=2
MM7 out ib vssq vssq nch_hv W=4u L=1u m=8 nf=1
MM8 ib enb vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
MM9 net06 en vccq vccq pch_hv W=1u L=0.2u m=1 nf=1
RR0 net06 net07 5k
CC0 net07 out 0.8p
.ends vref_buf_ota
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_saff
** View name: schematic
.subckt rx_saff d ck q qb vdd vss
MM12 d vss d_i vdd pch_lvt W=0.4u L=0.06u m=1 nf=1
MM13 d vdd d_i vss nch_lvt W=0.4u L=0.06u m=1 nf=1
XI0 d db_i vdd vss inv_lvt_x2
MMtail ntail ck vss vss nch_lvt W=2u L=0.06u m=1 nf=2
MM1 nx d_i ntail vss nch_lvt W=1.6u L=0.06u m=1 nf=2
MM2 ny db_i ntail vss nch_lvt W=1.6u L=0.06u m=1 nf=2
MM3 son sop nx vss nch_lvt W=0.8u L=0.06u m=1 nf=1
MM4 sop son ny vss nch_lvt W=0.8u L=0.06u m=1 nf=1
MM5 son sop vdd vdd pch_lvt W=0.8u L=0.06u m=1 nf=1
MM6 sop son vdd vdd pch_lvt W=0.8u L=0.06u m=1 nf=1
MM7 son ck vdd vdd pch_lvt W=0.4u L=0.06u m=1 nf=1
MM8 sop ck vdd vdd pch_lvt W=0.4u L=0.06u m=1 nf=1
MM9 nx ck vdd vdd pch_lvt W=0.4u L=0.06u m=1 nf=1
MM10 ny ck vdd vdd pch_lvt W=0.4u L=0.06u m=1 nf=1
XI1 son qb q vdd vss nand2_lvt
XI2 sop q qb vdd vss nand2_lvt
.ends rx_saff
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: dly_trim3
** View name: schematic
.subckt dly_trim3 in out code<2> code<1> code<0> vdd vss
XI0 in net05 vdd vss inv_lvt_x2
MM0 net05 code<0> net06 vss nch_lvt W=0.4u L=0.06u m=1 nf=1
MM1 net05 code<1> net07 vss nch_lvt W=0.4u L=0.06u m=2 nf=1
MM2 net05 code<2> net08 vss nch_lvt W=0.4u L=0.06u m=4 nf=1
MM3 vss net06 vss vss nch W=0.5u L=0.2u m=1 nf=1
MM4 vss net07 vss vss nch W=0.5u L=0.2u m=2 nf=1
MM5 vss net08 vss vss nch W=0.5u L=0.2u m=4 nf=1
XI1 net05 out vdd vss inv_lvt_x2
.ends dly_trim3
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: mux2_hs
** View name: schematic
.subckt mux2_hs d0 d1 s sb z vdd vss
XI0 d0 sb net05 vdd vss nand2_lvt
XI1 d1 s net06 vdd vss nand2_lvt
XI2 net05 net06 z vdd vss nand2_lvt
.ends mux2_hs
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: dq_match_dly
** View name: schematic
.subckt dq_match_dly in en out vdd vss
XI0 in en net011 vdd vss ckgate
XI1 net011 net012 vdd vss ckbuf
CC0 net012 vss 17f
XI2 net012 net013 vdd vss ckbuf
CC1 net013 vss 13f
XI3 net013 out vdd vss ckbuf
CC2 out vss 5f
.ends dq_match_dly
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_dqs_tree
** View name: schematic
.subckt rx_dqs_tree in lf<8> lf<7> lf<6> lf<5> lf<4> lf<3> lf<2> lf<1> lf<0> vdd vss
XI0 in net010 vdd vss ckbuf
CC0 net010 vss 12f
XI1<2> net010 br<2> vdd vss ckbuf
XI1<1> net010 br<1> vdd vss ckbuf
XI1<0> net010 br<0> vdd vss ckbuf
CC1 br<2> vss 8f
CC2 br<1> vss 8f
CC3 br<0> vss 8f
XI2<8> br<2> lf<8> vdd vss ckbuf
XI2<7> br<2> lf<7> vdd vss ckbuf
XI2<6> br<2> lf<6> vdd vss ckbuf
XI2<5> br<1> lf<5> vdd vss ckbuf
XI2<4> br<1> lf<4> vdd vss ckbuf
XI2<3> br<1> lf<3> vdd vss ckbuf
XI2<2> br<0> lf<2> vdd vss ckbuf
XI2<1> br<0> lf<1> vdd vss ckbuf
XI2<0> br<0> lf<0> vdd vss ckbuf
CC4 lf<8> vss 5f
CC5 lf<7> vss 5f
CC6 lf<6> vss 5f
CC7 lf<5> vss 5f
CC8 lf<4> vss 5f
CC9 lf<3> vss 5f
CC10 lf<2> vss 5f
CC11 lf<1> vss 5f
CC12 lf<0> vss 5f
.ends rx_dqs_tree
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_rpt_chain
** View name: schematic
.subckt rx_rpt_chain in tap<8> tap<7> tap<6> tap<5> tap<4> tap<3> tap<2> tap<1> tap<0>
+ vdd vss
XI0<8> rn<8> tap<8> vdd vss rpt_buf
XI0<7> rn<7> tap<7> vdd vss rpt_buf
XI0<6> rn<6> tap<6> vdd vss rpt_buf
XI0<5> rn<5> tap<5> vdd vss rpt_buf
XI0<4> rn<4> tap<4> vdd vss rpt_buf
XI0<3> rn<3> tap<3> vdd vss rpt_buf
XI0<2> rn<2> tap<2> vdd vss rpt_buf
XI0<1> rn<1> tap<1> vdd vss rpt_buf
XI0<0> in tap<0> vdd vss rpt_buf
XI1<7> tap<7> rn<8> vss wire_rc_rx
XI1<6> tap<6> rn<7> vss wire_rc_rx
XI1<5> tap<5> rn<6> vss wire_rc_rx
XI1<4> tap<4> rn<5> vss wire_rc_rx
XI1<3> tap<3> rn<4> vss wire_rc_rx
XI1<2> tap<2> rn<3> vss wire_rc_rx
XI1<1> tap<1> rn<2> vss wire_rc_rx
XI1<0> tap<0> rn<1> vss wire_rc_rx
.ends rx_rpt_chain
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_samp_pair
** View name: schematic
.subckt rx_samp_pair d ckr ckf dr df vdd vss
XI0 d ckr dr net07 vdd vss rx_saff
XI1 d ckf df net08 vdd vss rx_saff
.ends rx_samp_pair
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_deser4
** View name: schematic
.subckt rx_deser4 dr df ckf div_p div_n rd<3> rd<2> rd<1> rd<0> vdd vss
XI0 dr ckf e0 vdd vss dff_tg
XI1 e0 div_p p0 vdd vss dff_tg
XI2 df div_p p1 vdd vss dff_tg
XI5 p0 div_n rd<0> vdd vss dff_tg
XI6 p1 div_n rd<1> vdd vss dff_tg
XI3 e0 div_n rd<2> vdd vss dff_tg
XI4 df div_n rd<3> vdd vss dff_tg
.ends rx_deser4
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_dq_slice
** View name: schematic
.subckt rx_dq_slice dq vref_rx en_q enb_q dskw<2> dskw<1> dskw<0> ckt_m ckc_m ckt_u
+ ckc_u selu selub div_p div_n rd<3> rd<2> rd<1> rd<0> vdd vss vccq vssq
XI9 dq dq_m vccq vssq vccq vssq rx_tg_q
XI0 dq_m vref_rx en_q enb_q net010 vccq vssq rx_amp_bz
XI1 net010 net011 vccq vssq vdd vss rx_ls_dn
XI2 net011 dq_d dskw<2> dskw<1> dskw<0> vdd vss dly_trim3
XI3 dq_d selub dq_mt vdd vss dq_match_dly
XI4 dq_mt dq_d selu selub dsam vdd vss mux2_hs
XI5 ckt_m ckt_u selu selub ckr vdd vss mux2_hs
XI6 ckc_m ckc_u selu selub ckf vdd vss mux2_hs
XI7 dsam ckr ckf dr df vdd vss rx_samp_pair
XI8 dr df ckf div_p div_n rd<3> rd<2> rd<1> rd<0> vdd vss rx_deser4
.ends rx_dq_slice
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_dqs_path
** View name: schematic
.subckt rx_dqs_path dqs dqsb vref_rx dqs_se_q dqs_dif_q en_q enb_q dqs_dly<2> dqs_dly<1>
+ dqs_dly<0> en_m en_u ckt_m<8> ckt_m<7> ckt_m<6> ckt_m<5> ckt_m<4> ckt_m<3> ckt_m<2>
+ ckt_m<1> ckt_m<0> ckc_m<8> ckc_m<7> ckc_m<6> ckc_m<5> ckc_m<4> ckc_m<3> ckc_m<2>
+ ckc_m<1> ckc_m<0> ckt_u<8> ckt_u<7> ckt_u<6> ckt_u<5> ckt_u<4> ckt_u<3> ckt_u<2>
+ ckt_u<1> ckt_u<0> ckc_u<8> ckc_u<7> ckc_u<6> ckc_u<5> ckc_u<4> ckc_u<3> ckc_u<2>
+ ckc_u<1> ckc_u<0> vdd vss vccq vssq
XI0 dqs dqs_m vccq vssq vccq vssq rx_tg_q
XI1 dqsb ref_m dqs_dif_q dqs_se_q vccq vssq rx_tg_q
XI2 vref_rx ref_m dqs_se_q dqs_dif_q vccq vssq rx_tg_q
XI3 dqs_m ref_m en_q enb_q st0 vccq vssq rx_amp_bz
XI4 ref_m dqs_m en_q enb_q sc0 vccq vssq rx_amp_bz
XI5 st0 st1 vccq vssq vdd vss rx_ls_dn
XI6 sc0 sc1 vccq vssq vdd vss rx_ls_dn
XI7 st1 st2 dqs_dly<2> dqs_dly<1> dqs_dly<0> vdd vss dly_trim3
XI8 sc1 sc2 dqs_dly<2> dqs_dly<1> dqs_dly<0> vdd vss dly_trim3
XI9 st2 en_m stm vdd vss ckgate
XI10 sc2 en_m scm vdd vss ckgate
XI11 st2 en_u stu vdd vss ckgate
XI12 sc2 en_u scu vdd vss ckgate
XI13 stm ckt_m<8> ckt_m<7> ckt_m<6> ckt_m<5> ckt_m<4> ckt_m<3> ckt_m<2> ckt_m<1>
+ ckt_m<0> vdd vss rx_dqs_tree
XI14 scm ckc_m<8> ckc_m<7> ckc_m<6> ckc_m<5> ckc_m<4> ckc_m<3> ckc_m<2> ckc_m<1>
+ ckc_m<0> vdd vss rx_dqs_tree
XI15 stu ckt_u<8> ckt_u<7> ckt_u<6> ckt_u<5> ckt_u<4> ckt_u<3> ckt_u<2> ckt_u<1>
+ ckt_u<0> vdd vss rx_rpt_chain
XI16 scu ckc_u<8> ckc_u<7> ckc_u<6> ckc_u<5> ckc_u<4> ckc_u<3> ckc_u<2> ckc_u<1>
+ ckc_u<0> vdd vss rx_rpt_chain
.ends rx_dqs_path
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_ckdiv_slice
** View name: schematic
.subckt rx_ckdiv_slice ckt_m ckt_u selu selub rst_n div_p div_n rclk_div vdd vss
XI0 ckt_m ckt_u selu selub ckd vdd vss mux2_hs
XI1 net08 ckd rst_n net07 net08 vdd vss dffr_tg
XI2 net07 div_p vdd vss ckbuf
XI3 net08 div_n vdd vss ckbuf
XI4 div_p rclk_div vdd vss rpt_buf
.ends rx_ckdiv_slice
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_ctrl
** View name: schematic
.subckt rx_ctrl rx_en rx_mode_um dqs_se vref_int_en tm_rxobs en_q enb_q dqs_se_q
+ dqs_dif_q vint_q vintb_q selu selub en_m en_u obs_en vdd vss vccq vssq
XI0 rx_en en_q enb_q vdd vss vccq vssq ls_up
XI1 dqs_se dqs_se_q dqs_dif_q vdd vss vccq vssq ls_up
XI3 vref_int_en rx_en net010 vdd vss nand2_x1
XI4 net010 net011 vdd vss inv_x1
XI2 net011 vint_q vintb_q vdd vss vccq vssq ls_up
XI5 rx_mode_um selub vdd vss inv_x2
XI6 selub selu vdd vss inv_x2
XI7 rx_en selub net012 vdd vss nand2_x1
XI8 net012 en_m vdd vss inv_x1
XI9 rx_en selu net013 vdd vss nand2_x1
XI10 net013 en_u vdd vss inv_x1
XI11 tm_rxobs rx_en net014 vdd vss nand2_x1
XI12 net014 obs_en vdd vss inv_x1
.ends rx_ctrl
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: vref_mux32
** View name: schematic
.subckt vref_mux32 t<31> t<30> t<29> t<28> t<27> t<26> t<25> t<24> t<23> t<22> t<21>
+ t<20> t<19> t<18> t<17> t<16> t<15> t<14> t<13> t<12> t<11> t<10> t<9> t<8> t<7> t<6>
+ t<5> t<4> t<3> t<2> t<1> t<0> s<4> s<3> s<2> s<1> s<0> sb<4> sb<3> sb<2> sb<1> sb<0> z
+ vccq vssq
XI0<15> t<30> t<31> s<0> sb<0> m0<15> vccq vssq amux2_q
XI0<14> t<28> t<29> s<0> sb<0> m0<14> vccq vssq amux2_q
XI0<13> t<26> t<27> s<0> sb<0> m0<13> vccq vssq amux2_q
XI0<12> t<24> t<25> s<0> sb<0> m0<12> vccq vssq amux2_q
XI0<11> t<22> t<23> s<0> sb<0> m0<11> vccq vssq amux2_q
XI0<10> t<20> t<21> s<0> sb<0> m0<10> vccq vssq amux2_q
XI0<9> t<18> t<19> s<0> sb<0> m0<9> vccq vssq amux2_q
XI0<8> t<16> t<17> s<0> sb<0> m0<8> vccq vssq amux2_q
XI0<7> t<14> t<15> s<0> sb<0> m0<7> vccq vssq amux2_q
XI0<6> t<12> t<13> s<0> sb<0> m0<6> vccq vssq amux2_q
XI0<5> t<10> t<11> s<0> sb<0> m0<5> vccq vssq amux2_q
XI0<4> t<8> t<9> s<0> sb<0> m0<4> vccq vssq amux2_q
XI0<3> t<6> t<7> s<0> sb<0> m0<3> vccq vssq amux2_q
XI0<2> t<4> t<5> s<0> sb<0> m0<2> vccq vssq amux2_q
XI0<1> t<2> t<3> s<0> sb<0> m0<1> vccq vssq amux2_q
XI0<0> t<0> t<1> s<0> sb<0> m0<0> vccq vssq amux2_q
XI1<7> m0<14> m0<15> s<1> sb<1> m1<7> vccq vssq amux2_q
XI1<6> m0<12> m0<13> s<1> sb<1> m1<6> vccq vssq amux2_q
XI1<5> m0<10> m0<11> s<1> sb<1> m1<5> vccq vssq amux2_q
XI1<4> m0<8> m0<9> s<1> sb<1> m1<4> vccq vssq amux2_q
XI1<3> m0<6> m0<7> s<1> sb<1> m1<3> vccq vssq amux2_q
XI1<2> m0<4> m0<5> s<1> sb<1> m1<2> vccq vssq amux2_q
XI1<1> m0<2> m0<3> s<1> sb<1> m1<1> vccq vssq amux2_q
XI1<0> m0<0> m0<1> s<1> sb<1> m1<0> vccq vssq amux2_q
XI2<3> m1<6> m1<7> s<2> sb<2> m2<3> vccq vssq amux2_q
XI2<2> m1<4> m1<5> s<2> sb<2> m2<2> vccq vssq amux2_q
XI2<1> m1<2> m1<3> s<2> sb<2> m2<1> vccq vssq amux2_q
XI2<0> m1<0> m1<1> s<2> sb<2> m2<0> vccq vssq amux2_q
XI3<1> m2<2> m2<3> s<3> sb<3> m3<1> vccq vssq amux2_q
XI3<0> m2<0> m2<1> s<3> sb<3> m3<0> vccq vssq amux2_q
XI4 m3<0> m3<1> s<4> sb<4> z vccq vssq amux2_q
.ends vref_mux32
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_vref_gen
** View name: schematic
.subckt rx_vref_gen vref_ext vref_code<4> vref_code<3> vref_code<2> vref_code<1>
+ vref_code<0> vint_q vintb_q ib_vref vref_rx vdd vss vccq vssq
MM0 vtop vintb_q vccq vccq pch_hv W=4u L=0.2u m=1 nf=2
RR0 vtop t<31> 12k
RR1<30> t<31> t<30> 500
RR1<29> t<30> t<29> 500
RR1<28> t<29> t<28> 500
RR1<27> t<28> t<27> 500
RR1<26> t<27> t<26> 500
RR1<25> t<26> t<25> 500
RR1<24> t<25> t<24> 500
RR1<23> t<24> t<23> 500
RR1<22> t<23> t<22> 500
RR1<21> t<22> t<21> 500
RR1<20> t<21> t<20> 500
RR1<19> t<20> t<19> 500
RR1<18> t<19> t<18> 500
RR1<17> t<18> t<17> 500
RR1<16> t<17> t<16> 500
RR1<15> t<16> t<15> 500
RR1<14> t<15> t<14> 500
RR1<13> t<14> t<13> 500
RR1<12> t<13> t<12> 500
RR1<11> t<12> t<11> 500
RR1<10> t<11> t<10> 500
RR1<9> t<10> t<9> 500
RR1<8> t<9> t<8> 500
RR1<7> t<8> t<7> 500
RR1<6> t<7> t<6> 500
RR1<5> t<6> t<5> 500
RR1<4> t<5> t<4> 500
RR1<3> t<4> t<3> 500
RR1<2> t<3> t<2> 500
RR1<1> t<2> t<1> 500
RR1<0> t<1> t<0> 500
RR2 t<0> vssq 14.5k
XI0<4> vref_code<4> vc<4> vcb<4> vdd vss vccq vssq ls_up
XI0<3> vref_code<3> vc<3> vcb<3> vdd vss vccq vssq ls_up
XI0<2> vref_code<2> vc<2> vcb<2> vdd vss vccq vssq ls_up
XI0<1> vref_code<1> vc<1> vcb<1> vdd vss vccq vssq ls_up
XI0<0> vref_code<0> vc<0> vcb<0> vdd vss vccq vssq ls_up
XI1 t<31> t<30> t<29> t<28> t<27> t<26> t<25> t<24> t<23> t<22> t<21> t<20> t<19> t<18>
+ t<17> t<16> t<15> t<14> t<13> t<12> t<11> t<10> t<9> t<8> t<7> t<6> t<5> t<4> t<3>
+ t<2> t<1> t<0> vc<4> vc<3> vc<2> vc<1> vc<0> vcb<4> vcb<3> vcb<2> vcb<1> vcb<0> vint
+ vccq vssq vref_mux32
XI2 vint vbuf vbuf ib_vref vint_q vintb_q vccq vssq vref_buf_ota
XI3 vref_ext vbuf vint_q vintb_q vref_rx vccq vssq amux2_q
CC0 vref_rx vssq 2p
MM1 vssq vref_rx vssq vssq nch_hv W=10u L=2u m=4 nf=1
.ends rx_vref_gen
** End of subcircuit definition.

** Library name: NFIO_RX
** Cell name: rx_obs_buf
** View name: schematic
.subckt rx_obs_buf div_p obs_en rx_obs vdd vss
XI0 div_p obs_en net05 vdd vss nand2_x1
XI1 net05 rx_obs vdd vss inv_x2
.ends rx_obs_buf
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: ls_up_hs
** View name: schematic
.subckt ls_up_hs in out vdd vss vccq vssq
MM0 inb in vss vss nch_lvt W=0.6u L=0.06u m=1 nf=1
MM1 inb in vdd vdd pch_lvt W=1.2u L=0.06u m=1 nf=2
MM2 net07 in vssq vssq nch_hv W=3u L=0.2u m=1 nf=2
MM3 net08 inb vssq vssq nch_hv W=3u L=0.2u m=1 nf=2
MM4 net07 net08 vccq vccq pch_hv W=0.8u L=0.2u m=1 nf=1
MM5 net08 net07 vccq vccq pch_hv W=0.8u L=0.2u m=1 nf=1
MM6 out net07 vssq vssq nch_hv W=2u L=0.2u m=1 nf=2
MM7 out net07 vccq vccq pch_hv W=4u L=0.2u m=1 nf=2
.ends ls_up_hs
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_rpt
** View name: schematic
.subckt tx_rpt in out vdd vss
MM0 net03 in vss vss nch_lvt W=2u L=0.06u m=1 nf=4
MM1 net03 in vdd vdd pch_lvt W=4u L=0.06u m=1 nf=4
MM2 out net03 vss vss nch_lvt W=8u L=0.06u m=1 nf=8
MM3 out net03 vdd vdd pch_lvt W=16u L=0.06u m=1 nf=16
.ends tx_rpt
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: wire_rc_tx
** View name: schematic
.subckt wire_rc_tx a b vss
CC0 a vss 15f
RR0 a b 200
CC1 b vss 15f
.ends wire_rc_tx
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: ck_split
** View name: schematic
.subckt ck_split in ck ckb vdd vss
MM0 net05 in vss vss nch_lvt W=0.6u L=0.06u m=1 nf=1
MM1 net05 in vdd vdd pch_lvt W=1.2u L=0.06u m=1 nf=2
MM2 ck net05 vss vss nch_lvt W=1.2u L=0.06u m=1 nf=2
MM3 ck net05 vdd vdd pch_lvt W=2.4u L=0.06u m=1 nf=2
MM4 in vdd net06 vss nch_lvt W=0.6u L=0.06u m=1 nf=1
MM5 in vss net06 vdd pch_lvt W=0.6u L=0.06u m=1 nf=1
MM6 ckb net06 vss vss nch_lvt W=1.2u L=0.06u m=1 nf=2
MM7 ckb net06 vdd vdd pch_lvt W=2.4u L=0.06u m=1 nf=2
.ends ck_split
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_ser2
** View name: schematic
.subckt tx_ser2 de do ck ckb ds vdd vss
XI0 de ckb qe vdd vss dff_tg
XI1 do ckb qo vdd vss dff_tg
XI2 qo ck ckb qol vdd vss latch_tg
MM0 qe ck mx vss nch_lvt W=0.8u L=0.06u m=1 nf=1
MM1 qe ckb mx vdd pch_lvt W=1.2u L=0.06u m=1 nf=2
MM2 qol ckb mx vss nch_lvt W=0.8u L=0.06u m=1 nf=1
MM3 qol ck mx vdd pch_lvt W=1.2u L=0.06u m=1 nf=2
XI3 mx net011 vdd vss inv_lvt_x2
XI4 net011 ds vdd vss inv_lvt_x2
.ends tx_ser2
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_predrv_leg
** View name: schematic
.subckt tx_predrv_leg ds_q pu_en pd_dis vbp_sr vbn_sr pg ng vccq vssq
XI0 ds_q pu_en net010 vccq vssq nand2_q
XI1 net010 net011 vccq vssq inv_q
MM0 net012 vbp_sr vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM1 pg net011 net012 vccq pch_hv W=2u L=0.2u m=1 nf=1
MM2 pg net011 net013 vssq nch_hv W=1u L=0.2u m=1 nf=1
MM3 net013 vbn_sr vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
XI2 ds_q pd_dis net014 vccq vssq nor2_q
XI3 net014 net015 vccq vssq inv_q
MM4 net016 vbp_sr vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
MM5 ng net015 net016 vccq pch_hv W=2u L=0.2u m=1 nf=1
MM6 ng net015 net017 vssq nch_hv W=1u L=0.2u m=1 nf=1
MM7 net017 vbn_sr vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
.ends tx_predrv_leg
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_predrv
** View name: schematic
.subckt tx_predrv ds_q pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0> pd_dis<4> pd_dis<3>
+ pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr vbn_sr pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3>
+ ng<2> ng<1> ng<0> vccq vssq
XI5 ds_q net05 vccq vssq inv_q
XI6 net05 ds_buf vccq vssq inv_q m=4
XI4 ds_buf pu_en<4> pd_dis<4> vbp_sr vbn_sr pg<4> ng<4> vccq vssq tx_predrv_leg m=8
XI3 ds_buf pu_en<3> pd_dis<3> vbp_sr vbn_sr pg<3> ng<3> vccq vssq tx_predrv_leg m=4
XI2 ds_buf pu_en<2> pd_dis<2> vbp_sr vbn_sr pg<2> ng<2> vccq vssq tx_predrv_leg m=2
XI1 ds_buf pu_en<1> pd_dis<1> vbp_sr vbn_sr pg<1> ng<1> vccq vssq tx_predrv_leg m=1
XI0 ds_buf pu_en<0> pd_dis<0> vbp_sr vbn_sr pg<0> ng<0> vccq vssq tx_predrv_leg m=1
.ends tx_predrv
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_drv_unit
** View name: schematic
.subckt tx_drv_unit pg ng pad vccq vssq
MM0 net05 pg vccq vccq pch_hv W=8u L=0.2u m=1 nf=4
RR0 net05 pad 300
MM1 net06 ng vssq vssq nch_hv W=4u L=0.2u m=1 nf=2
RR1 net06 pad 300
.ends tx_drv_unit
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_out_drv
** View name: schematic
.subckt tx_out_drv pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2> ng<1> ng<0> pad vccq
+ vssq
XI4 pg<4> ng<4> pad vccq vssq tx_drv_unit m=16
XI3 pg<3> ng<3> pad vccq vssq tx_drv_unit m=8
XI2 pg<2> ng<2> pad vccq vssq tx_drv_unit m=4
XI1 pg<1> ng<1> pad vccq vssq tx_drv_unit m=2
XI0 pg<0> ng<0> pad vccq vssq tx_drv_unit m=1
.ends tx_out_drv
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_dq_slice
** View name: schematic
.subckt tx_dq_slice de do ck_lf pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0> pd_dis<4>
+ pd_dis<3> pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr vbn_sr pg<4> pg<3> pg<2> pg<1> pg<0>
+ ng<4> ng<3> ng<2> ng<1> ng<0> vdd vss vccq vssq
XI0 ck_lf ck ckb vdd vss ck_split
XI1 de do ck ckb ds vdd vss tx_ser2
XI2 ds ds_q vdd vss vccq vssq ls_up_hs
XI3 ds_q pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0> pd_dis<4> pd_dis<3> pd_dis<2>
+ pd_dis<1> pd_dis<0> vbp_sr vbn_sr pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2>
+ ng<1> ng<0> vccq vssq tx_predrv
.ends tx_dq_slice
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_dca
** View name: schematic
.subckt tx_dca in out code<4> code<3> code<2> code<1> code<0> vdd vss
XI0<3> code<4> code<3> pen_b<3> vdd vss nand2_x1
XI0<2> code<4> code<2> pen_b<2> vdd vss nand2_x1
XI0<1> code<4> code<1> pen_b<1> vdd vss nand2_x1
XI0<0> code<4> code<0> pen_b<0> vdd vss nand2_x1
XI1<3> code<4> code<3> nen<3> vdd vss nor2_x1
XI1<2> code<4> code<2> nen<2> vdd vss nor2_x1
XI1<1> code<4> code<1> nen<1> vdd vss nor2_x1
XI1<0> code<4> code<0> nen<0> vdd vss nor2_x1
MM0 x in vdd vdd pch_lvt W=1u L=0.06u m=1 nf=2
MM1 x in vss vss nch_lvt W=0.5u L=0.06u m=1 nf=1
MM2 pl<3> in vdd vdd pch_lvt W=0.15u L=0.06u m=8 nf=1
MM3 x pen_b<3> pl<3> vdd pch_lvt W=0.15u L=0.06u m=8 nf=1
MM4 pl<2> in vdd vdd pch_lvt W=0.15u L=0.06u m=4 nf=1
MM5 x pen_b<2> pl<2> vdd pch_lvt W=0.15u L=0.06u m=4 nf=1
MM6 pl<1> in vdd vdd pch_lvt W=0.15u L=0.06u m=2 nf=1
MM7 x pen_b<1> pl<1> vdd pch_lvt W=0.15u L=0.06u m=2 nf=1
MM8 pl<0> in vdd vdd pch_lvt W=0.15u L=0.06u m=1 nf=1
MM9 x pen_b<0> pl<0> vdd pch_lvt W=0.15u L=0.06u m=1 nf=1
MM10 nl<3> in vss vss nch_lvt W=0.1u L=0.06u m=8 nf=1
MM11 x nen<3> nl<3> vss nch_lvt W=0.1u L=0.06u m=8 nf=1
MM12 nl<2> in vss vss nch_lvt W=0.1u L=0.06u m=4 nf=1
MM13 x nen<2> nl<2> vss nch_lvt W=0.1u L=0.06u m=4 nf=1
MM14 nl<1> in vss vss nch_lvt W=0.1u L=0.06u m=2 nf=1
MM15 x nen<1> nl<1> vss nch_lvt W=0.1u L=0.06u m=2 nf=1
MM16 nl<0> in vss vss nch_lvt W=0.1u L=0.06u m=1 nf=1
MM17 x nen<0> nl<0> vss nch_lvt W=0.1u L=0.06u m=1 nf=1
CC0 x vss 6f
XI2 x out vdd vss inv_lvt_x2
.ends tx_dca
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_ckbuf_dca
** View name: schematic
.subckt tx_ckbuf_dca in dcc_code<4> dcc_code<3> dcc_code<2> dcc_code<1> dcc_code<0> out
+ vdd vss
XI0 in net010 vdd vss ckbuf
XI1 net010 net011 dcc_code<4> dcc_code<3> dcc_code<2> dcc_code<1> dcc_code<0> vdd vss
+ tx_dca
XI2 net011 out vdd vss ckbuf_x8
.ends tx_ckbuf_dca
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_re_rx
** View name: schematic
.subckt tx_re_rx re reb vref re_se_q re_dif_q en_q enb_q ck_re vdd vss vccq vssq
XI0 re re_m vccq vssq vccq vssq rx_tg_q
XI1 reb ref_m re_dif_q re_se_q vccq vssq rx_tg_q
XI2 vref ref_m re_se_q re_dif_q vccq vssq rx_tg_q
XI3 re_m ref_m en_q enb_q net010 vccq vssq rx_amp_bz
XI5 ref_m re_m en_q enb_q net011 vccq vssq rx_amp_bz
XI4 net010 ck_re vccq vssq vdd vss rx_ls_dn
.ends tx_re_rx
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_rpt_chain
** View name: schematic
.subckt tx_rpt_chain in out vdd vss
XI0<3> w<3> r<3> vdd vss tx_rpt
XI0<2> w<2> r<2> vdd vss tx_rpt
XI0<1> w<1> r<1> vdd vss tx_rpt
XI0<0> in r<0> vdd vss tx_rpt
XI1<3> r<3> out vss wire_rc_tx
XI1<2> r<2> w<3> vss wire_rc_tx
XI1<1> r<1> w<2> vss wire_rc_tx
XI1<0> r<0> w<1> vss wire_rc_tx
.ends tx_rpt_chain
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_cktree
** View name: schematic
.subckt tx_cktree in lf<9> lf<8> lf<7> lf<6> lf<5> lf<4> lf<3> lf<2> lf<1> lf<0> lf_core
+ lf_dcc vdd vss
XI0 in r0 vdd vss ckbuf_x8
CC0 r0 vss 20f
XI1<1> r0 br<1> vdd vss ckbuf
XI1<0> r0 br<0> vdd vss ckbuf
CC1 br<1> vss 10f
CC2 br<0> vss 10f
XI2<9> br<1> lf<9> vdd vss ckbuf
XI2<8> br<1> lf<8> vdd vss ckbuf
XI2<7> br<1> lf<7> vdd vss ckbuf
XI2<6> br<1> lf<6> vdd vss ckbuf
XI2<5> br<1> lf<5> vdd vss ckbuf
XI2<4> br<0> lf<4> vdd vss ckbuf
XI2<3> br<0> lf<3> vdd vss ckbuf
XI2<2> br<0> lf<2> vdd vss ckbuf
XI2<1> br<0> lf<1> vdd vss ckbuf
XI2<0> br<0> lf<0> vdd vss ckbuf
XI3 br<0> lf_core vdd vss ckbuf
XI4 br<1> lf_dcc vdd vss ckbuf
.ends tx_cktree
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: re_clk_path
** View name: schematic
.subckt re_clk_path re reb vref re_se_q re_dif_q en_q enb_q dcc_code<4> dcc_code<3>
+ dcc_code<2> dcc_code<1> dcc_code<0> ck_lf<9> ck_lf<8> ck_lf<7> ck_lf<6> ck_lf<5>
+ ck_lf<4> ck_lf<3> ck_lf<2> ck_lf<1> ck_lf<0> ck_dcc rclk_core vdd vss vccq vssq
XI0 re reb vref re_se_q re_dif_q en_q enb_q ck_re vdd vss vccq vssq tx_re_rx
XI1 ck_re dcc_code<4> dcc_code<3> dcc_code<2> dcc_code<1> dcc_code<0> ck_g vdd vss
+ tx_ckbuf_dca
XI2 ck_g ck_rpt vdd vss tx_rpt_chain
XI3 ck_rpt ck_lf<9> ck_lf<8> ck_lf<7> ck_lf<6> ck_lf<5> ck_lf<4> ck_lf<3> ck_lf<2>
+ ck_lf<1> ck_lf<0> lf_core ck_dcc vdd vss tx_cktree
XI4 lf_core rclk_core vdd vss tx_rpt
.ends re_clk_path
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_sr_bias
** View name: schematic
.subckt tx_sr_bias sr_code<1> sr_code<0> vbp_sr vbn_sr vdd vss vccq vssq
XI0<1> sr_code<1> sr_q<1> srb_q<1> vdd vss vccq vssq ls_up
XI0<0> sr_code<0> sr_q<0> srb_q<0> vdd vss vccq vssq ls_up
RR0 vccq nref 24k
MM1 nref nref vssq vssq nch_hv W=2u L=1u m=1 nf=1
MM2 vbp_sr nref vssq vssq nch_hv W=2u L=1u m=2 nf=1
MM3 net011 nref vssq vssq nch_hv W=2u L=1u m=1 nf=1
MM4 vbp_sr sr_q<0> net011 vssq nch_hv W=2u L=0.2u m=1 nf=1
MM5 net012 nref vssq vssq nch_hv W=2u L=1u m=2 nf=1
MM6 vbp_sr sr_q<1> net012 vssq nch_hv W=2u L=0.2u m=1 nf=1
MM7 vbp_sr vbp_sr vccq vccq pch_hv W=4u L=1u m=2 nf=1
MM8 vbn_sr vbp_sr vccq vccq pch_hv W=4u L=1u m=2 nf=1
MM9 vbn_sr vbn_sr vssq vssq nch_hv W=2u L=1u m=2 nf=1
CC0 vbp_sr vccq 2p
CC1 vbn_sr vssq 2p
.ends tx_sr_bias
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: tx_ctrl
** View name: schematic
.subckt tx_ctrl tx_en dq_oe dqs_oe dqs_burst re_se pu_code<4> pu_code<3> pu_code<2>
+ pu_code<1> pu_code<0> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> en_q
+ enb_q re_se_q re_dif_q pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> pu_en_s<4> pu_en_s<3>
+ pu_en_s<2> pu_en_s<1> pu_en_s<0> pd_dis_s<4> pd_dis_s<3> pd_dis_s<2> pd_dis_s<1>
+ pd_dis_s<0> dqs_e dqs_o dqsb_e dqsb_o vdd vss vccq vssq
XI0 tx_en en_q enb_q vdd vss vccq vssq ls_up
XI1 re_se re_se_q re_dif_q vdd vss vccq vssq ls_up
XI2 dq_oe dqoe_q net010 vdd vss vccq vssq ls_up
XI3 dqs_oe dqsoe_q net011 vdd vss vccq vssq ls_up
XI4<4> pu_code<4> puc_q<4> pucb_q<4> vdd vss vccq vssq ls_up
XI4<3> pu_code<3> puc_q<3> pucb_q<3> vdd vss vccq vssq ls_up
XI4<2> pu_code<2> puc_q<2> pucb_q<2> vdd vss vccq vssq ls_up
XI4<1> pu_code<1> puc_q<1> pucb_q<1> vdd vss vccq vssq ls_up
XI4<0> pu_code<0> puc_q<0> pucb_q<0> vdd vss vccq vssq ls_up
XI5<4> pd_code<4> pdc_q<4> pdcb_q<4> vdd vss vccq vssq ls_up
XI5<3> pd_code<3> pdc_q<3> pdcb_q<3> vdd vss vccq vssq ls_up
XI5<2> pd_code<2> pdc_q<2> pdcb_q<2> vdd vss vccq vssq ls_up
XI5<1> pd_code<1> pdc_q<1> pdcb_q<1> vdd vss vccq vssq ls_up
XI5<0> pd_code<0> pdc_q<0> pdcb_q<0> vdd vss vccq vssq ls_up
XI6<4> puc_q<4> dqoe_q pub_d<4> vccq vssq nand2_q
XI6<3> puc_q<3> dqoe_q pub_d<3> vccq vssq nand2_q
XI6<2> puc_q<2> dqoe_q pub_d<2> vccq vssq nand2_q
XI6<1> puc_q<1> dqoe_q pub_d<1> vccq vssq nand2_q
XI6<0> puc_q<0> dqoe_q pub_d<0> vccq vssq nand2_q
XI7<4> pub_d<4> pu_en_d<4> vccq vssq inv_q
XI7<3> pub_d<3> pu_en_d<3> vccq vssq inv_q
XI7<2> pub_d<2> pu_en_d<2> vccq vssq inv_q
XI7<1> pub_d<1> pu_en_d<1> vccq vssq inv_q
XI7<0> pub_d<0> pu_en_d<0> vccq vssq inv_q
XI8<4> pdc_q<4> dqoe_q pd_dis_d<4> vccq vssq nand2_q
XI8<3> pdc_q<3> dqoe_q pd_dis_d<3> vccq vssq nand2_q
XI8<2> pdc_q<2> dqoe_q pd_dis_d<2> vccq vssq nand2_q
XI8<1> pdc_q<1> dqoe_q pd_dis_d<1> vccq vssq nand2_q
XI8<0> pdc_q<0> dqoe_q pd_dis_d<0> vccq vssq nand2_q
XI9<4> puc_q<4> dqsoe_q pub_s<4> vccq vssq nand2_q
XI9<3> puc_q<3> dqsoe_q pub_s<3> vccq vssq nand2_q
XI9<2> puc_q<2> dqsoe_q pub_s<2> vccq vssq nand2_q
XI9<1> puc_q<1> dqsoe_q pub_s<1> vccq vssq nand2_q
XI9<0> puc_q<0> dqsoe_q pub_s<0> vccq vssq nand2_q
XI10<4> pub_s<4> pu_en_s<4> vccq vssq inv_q
XI10<3> pub_s<3> pu_en_s<3> vccq vssq inv_q
XI10<2> pub_s<2> pu_en_s<2> vccq vssq inv_q
XI10<1> pub_s<1> pu_en_s<1> vccq vssq inv_q
XI10<0> pub_s<0> pu_en_s<0> vccq vssq inv_q
XI11<4> pdc_q<4> dqsoe_q pd_dis_s<4> vccq vssq nand2_q
XI11<3> pdc_q<3> dqsoe_q pd_dis_s<3> vccq vssq nand2_q
XI11<2> pdc_q<2> dqsoe_q pd_dis_s<2> vccq vssq nand2_q
XI11<1> pdc_q<1> dqsoe_q pd_dis_s<1> vccq vssq nand2_q
XI11<0> pdc_q<0> dqsoe_q pd_dis_s<0> vccq vssq nand2_q
XI12 dqs_burst net012 vdd vss inv_x1
XI13 net012 dqs_e vdd vss inv_x2
XI14 dqs_e dqsb_e vdd vss inv_x2
XI15 dqsb_o dqs_o vdd vss tie_hilo
.ends tx_ctrl
** End of subcircuit definition.

** Library name: NFIO_TX
** Cell name: drv_code_mux
** View name: schematic
.subckt drv_code_mux zq_pu<4> zq_pu<3> zq_pu<2> zq_pu<1> zq_pu<0> zq_pd<4> zq_pd<3>
+ zq_pd<2> zq_pd<1> zq_pd<0> ovr_en pu_ovr<4> pu_ovr<3> pu_ovr<2> pu_ovr<1> pu_ovr<0>
+ pd_ovr<4> pd_ovr<3> pd_ovr<2> pd_ovr<1> pd_ovr<0> pu_code<4> pu_code<3> pu_code<2>
+ pu_code<1> pu_code<0> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> vdd vss
XI0 ovr_en net010 vdd vss inv_x2
XI1 net010 sel vdd vss inv_x2
XI2<4> zq_pu<4> pu_ovr<4> sel net010 pu_code<4> vdd vss mux2_x1
XI2<3> zq_pu<3> pu_ovr<3> sel net010 pu_code<3> vdd vss mux2_x1
XI2<2> zq_pu<2> pu_ovr<2> sel net010 pu_code<2> vdd vss mux2_x1
XI2<1> zq_pu<1> pu_ovr<1> sel net010 pu_code<1> vdd vss mux2_x1
XI2<0> zq_pu<0> pu_ovr<0> sel net010 pu_code<0> vdd vss mux2_x1
XI3<4> zq_pd<4> pd_ovr<4> sel net010 pd_code<4> vdd vss mux2_x1
XI3<3> zq_pd<3> pd_ovr<3> sel net010 pd_code<3> vdd vss mux2_x1
XI3<2> zq_pd<2> pd_ovr<2> sel net010 pd_code<2> vdd vss mux2_x1
XI3<1> zq_pd<1> pd_ovr<1> sel net010 pd_code<1> vdd vss mux2_x1
XI3<0> zq_pd<0> pd_ovr<0> sel net010 pd_code<0> vdd vss mux2_x1
.ends drv_code_mux
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: sa_cmp
** View name: schematic
.subckt sa_cmp inp inn clk q qb vdd vss
MMtail ntail clk vss vss nch W=2u L=0.1u m=1 nf=2
MM1 nx inp ntail vss nch W=4u L=0.2u m=1 nf=4
MM2 ny inn ntail vss nch W=4u L=0.2u m=1 nf=4
MM3 son sop nx vss nch W=0.8u L=0.06u m=1 nf=1
MM4 sop son ny vss nch W=0.8u L=0.06u m=1 nf=1
MM5 son sop vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM6 sop son vdd vdd pch W=0.8u L=0.06u m=1 nf=1
MM7 son clk vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM8 sop clk vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM9 nx clk vdd vdd pch W=0.4u L=0.06u m=1 nf=1
MM10 ny clk vdd vdd pch W=0.4u L=0.06u m=1 nf=1
XI0 son qb q vdd vss nand2_x1
XI1 sop q qb vdd vss nand2_x1
.ends sa_cmp
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: dcc_det
** View name: schematic
.subckt dcc_det ck en vp vn vdd vss
XI0 ck en net010 vdd vss nand2_x1
XI1 net010 net011 vdd vss inv_x1
XI2 net011 net012 vdd vss inv_x1
RR0 net011 net013 50k
CC0 net013 vss 0.5p
RR1 net013 vp 50k
CC1 vp vss 0.25p
RR2 net010 net014 50k
CC2 net014 vss 0.5p
RR3 net014 vn 50k
CC3 vn vss 0.25p
.ends dcc_det
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: updn_cnt5
** View name: schematic
.subckt updn_cnt5 up clk en hold rst_n code<4> code<3> code<2> code<1> code<0> vdd vss
XI0 clk ckn vdd vss inv_x1
XI1<4> code<4> up p<4> vdd vss xnor2_x1
XI1<3> code<3> up p<3> vdd vss xnor2_x1
XI1<2> code<2> up p<2> vdd vss xnor2_x1
XI1<1> code<1> up p<1> vdd vss xnor2_x1
XI1<0> code<0> up p<0> vdd vss xnor2_x1
XI2 p<0> p<1> p<2> net010 vdd vss nand3_x1
XI3 p<3> p<4> net011 vdd vss nand2_x1
XI4 net010 net011 sat vdd vss nor2_x1
XI5 en enb vdd vss inv_x1
XI6 enb hold sat t<0> vdd vss nor3_x1
XI7<3> t<3> p<3> tn<4> vdd vss nand2_x1
XI7<2> t<2> p<2> tn<3> vdd vss nand2_x1
XI7<1> t<1> p<1> tn<2> vdd vss nand2_x1
XI7<0> t<0> p<0> tn<1> vdd vss nand2_x1
XI8<3> tn<4> t<4> vdd vss inv_x1
XI8<2> tn<3> t<3> vdd vss inv_x1
XI8<1> tn<2> t<2> vdd vss inv_x1
XI8<0> tn<1> t<1> vdd vss inv_x1
XI9<4> code<4> t<4> dn<4> vdd vss xor2_x1
XI9<3> code<3> t<3> dn<3> vdd vss xor2_x1
XI9<2> code<2> t<2> dn<2> vdd vss xor2_x1
XI9<1> code<1> t<1> dn<1> vdd vss xor2_x1
XI9<0> code<0> t<0> dn<0> vdd vss xor2_x1
XI10 dn<4> ckn rst_n code<4> net012 vdd vss dffs_tg
XI11<3> dn<3> ckn rst_n code<3> cqb<3> vdd vss dffr_tg
XI11<2> dn<2> ckn rst_n code<2> cqb<2> vdd vss dffr_tg
XI11<1> dn<1> ckn rst_n code<1> cqb<1> vdd vss dffr_tg
XI11<0> dn<0> ckn rst_n code<0> cqb<0> vdd vss dffr_tg
.ends updn_cnt5
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: dcc_lock_det
** View name: schematic
.subckt dcc_lock_det up clk rst_n lock vdd vss
XI0 clk ckn vdd vss inv_x1
XI1 up ckn rst_n up_d net010 vdd vss dffr_tg
XI2 vdd ckn rst_n vld net011 vdd vss dffr_tg
XI3 up up_d net013 vdd vss xor2_x1
XI4 net013 vld dithb vdd vss nand2_x1
XI5 dithb dith vdd vss inv_x1
XI6 s0b dithb d0 vdd vss nand2_x1
XI7 d0 ckn rst_n s0 s0b vdd vss dffr_tg
XI8 s0 dith net012 vdd vss nand2_x1
XI9 lockb net012 d1 vdd vss nand2_x1
XI10 d1 ckn rst_n lock lockb vdd vss dffr_tg
.ends dcc_lock_det
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: dcc_ctrl
** View name: schematic
.subckt dcc_ctrl ck_dcc cal_clk dcc_train dcc_rst_n dcc_code<4> dcc_code<3> dcc_code<2>
+ dcc_code<1> dcc_code<0> dcc_lock vdd vss
XI5 cal_clk dcc_train net012 vdd vss nand2_x1
XI6 net012 upd_clk vdd vss inv_x1
XI0 ck_dcc dcc_train vp vn vdd vss dcc_det
XI1 vp vn upd_clk up net011 vdd vss sa_cmp
XI2 up upd_clk dcc_train dcc_lock dcc_rst_n dcc_code<4> dcc_code<3> dcc_code<2>
+ dcc_code<1> dcc_code<0> vdd vss updn_cnt5
XI3 up upd_clk dcc_train dcc_lock vdd vss dcc_lock_det
.ends dcc_ctrl
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_vref
** View name: schematic
.subckt zq_vref enb vref vccq vssq
MM0 net05 enb vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
RR0 net05 vref 10k
RR1 vref vssq 10k
CC0 vref vssq 1p
.ends zq_vref
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_pu_rep
** View name: schematic
.subckt zq_pu_rep gb<4> gb<3> gb<2> gb<1> gb<0> pad vccq
MM4 np<4> gb<4> vccq vccq pch_hv W=1u L=0.2u m=16 nf=1
RR4 np<4> pad 150
MM3 np<3> gb<3> vccq vccq pch_hv W=1u L=0.2u m=8 nf=1
RR3 np<3> pad 300
MM2 np<2> gb<2> vccq vccq pch_hv W=1u L=0.2u m=4 nf=1
RR2 np<2> pad 600
MM1 np<1> gb<1> vccq vccq pch_hv W=1u L=0.2u m=2 nf=1
RR1 np<1> pad 1.2k
MM0 np<0> gb<0> vccq vccq pch_hv W=1u L=0.2u m=1 nf=1
RR0 np<0> pad 2.4k
.ends zq_pu_rep
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_pd_rep
** View name: schematic
.subckt zq_pd_rep pu_gb<4> pu_gb<3> pu_gb<2> pu_gb<1> pu_gb<0> pd_g<4> pd_g<3> pd_g<2>
+ pd_g<1> pd_g<0> npd vccq vssq
XI0 pu_gb<4> pu_gb<3> pu_gb<2> pu_gb<1> pu_gb<0> npd vccq zq_pu_rep
MM4 nd<4> pd_g<4> vssq vssq nch_hv W=0.5u L=0.2u m=16 nf=1
RR4 nd<4> npd 150
MM3 nd<3> pd_g<3> vssq vssq nch_hv W=0.5u L=0.2u m=8 nf=1
RR3 nd<3> npd 300
MM2 nd<2> pd_g<2> vssq vssq nch_hv W=0.5u L=0.2u m=4 nf=1
RR2 nd<2> npd 600
MM1 nd<1> pd_g<1> vssq vssq nch_hv W=0.5u L=0.2u m=2 nf=1
RR1 nd<1> npd 1.2k
MM0 nd<0> pd_g<0> vssq vssq nch_hv W=0.5u L=0.2u m=1 nf=1
RR0 nd<0> npd 2.4k
.ends zq_pd_rep
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_cmp
** View name: schematic
.subckt zq_cmp inp inn vbp enb_q out vdd vss vccq vssq
MM1 net05 enb_q vccq vccq pch_hv W=4u L=0.2u m=1 nf=1
MM0 ntail vbp net05 vccq pch_hv W=4u L=1u m=2 nf=1
MM2 net06 inp ntail vccq pch_hv W=4u L=0.5u m=2 nf=1
MM3 net07 inn ntail vccq pch_hv W=4u L=0.5u m=2 nf=1
MM4 net06 net06 vssq vssq nch_hv W=2u L=0.5u m=1 nf=1
MM5 net07 net06 vssq vssq nch_hv W=2u L=0.5u m=1 nf=1
MM6 net08 net07 vssq vssq nch_hv W=2u L=0.3u m=1 nf=1
MM7 net08 vbp vccq vccq pch_hv W=2u L=1u m=1 nf=1
XI0 net08 out vccq vssq vdd vss ls_dn
.ends zq_cmp
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_gate_drv
** View name: schematic
.subckt zq_gate_drv code<4> code<3> code<2> code<1> code<0> en_q g_q<4> g_q<3> g_q<2>
+ g_q<1> g_q<0> gb_q<4> gb_q<3> gb_q<2> gb_q<1> gb_q<0> vdd vss vccq vssq
XI0<4> code<4> cq<4> cqb<4> vdd vss vccq vssq ls_up
XI0<3> code<3> cq<3> cqb<3> vdd vss vccq vssq ls_up
XI0<2> code<2> cq<2> cqb<2> vdd vss vccq vssq ls_up
XI0<1> code<1> cq<1> cqb<1> vdd vss vccq vssq ls_up
XI0<0> code<0> cq<0> cqb<0> vdd vss vccq vssq ls_up
XI1<4> cq<4> en_q gb_q<4> vccq vssq nand2_q
XI1<3> cq<3> en_q gb_q<3> vccq vssq nand2_q
XI1<2> cq<2> en_q gb_q<2> vccq vssq nand2_q
XI1<1> cq<1> en_q gb_q<1> vccq vssq nand2_q
XI1<0> cq<0> en_q gb_q<0> vccq vssq nand2_q
XI2<4> gb_q<4> g_q<4> vccq vssq inv_q
XI2<3> gb_q<3> g_q<3> vccq vssq inv_q
XI2<2> gb_q<2> g_q<2> vccq vssq inv_q
XI2<1> gb_q<1> g_q<1> vccq vssq inv_q
XI2<0> gb_q<0> g_q<0> vccq vssq inv_q
.ends zq_gate_drv
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_sar5
** View name: schematic
.subckt zq_sar5 cmp clk start rst_n code<4> code<3> code<2> code<1> code<0> done vdd vss
XI12 cmp cmpb vdd vss inv_x1
XI0<5> start clk rst_n ph<5> phb<5> vdd vss dffr_tg
XI0<4> ph<5> clk rst_n ph<4> phb<4> vdd vss dffr_tg
XI0<3> ph<4> clk rst_n ph<3> phb<3> vdd vss dffr_tg
XI0<2> ph<3> clk rst_n ph<2> phb<2> vdd vss dffr_tg
XI0<1> ph<2> clk rst_n ph<1> phb<1> vdd vss dffr_tg
XI0<0> ph<1> clk rst_n ph<0> phb<0> vdd vss dffr_tg
XI1<4> ph<5> ph<5> ph<4> hd<4> vdd vss nor3_x1
XI1<3> ph<5> ph<4> ph<3> hd<3> vdd vss nor3_x1
XI1<2> ph<5> ph<3> ph<2> hd<2> vdd vss nor3_x1
XI1<1> ph<5> ph<2> ph<1> hd<1> vdd vss nor3_x1
XI1<0> ph<5> ph<1> ph<0> hd<0> vdd vss nor3_x1
XI2<4> ph<4> cmpb x1<4> vdd vss nand2_x1
XI2<3> ph<3> cmpb x1<3> vdd vss nand2_x1
XI2<2> ph<2> cmpb x1<2> vdd vss nand2_x1
XI2<1> ph<1> cmpb x1<1> vdd vss nand2_x1
XI2<0> ph<0> cmpb x1<0> vdd vss nand2_x1
XI3<4> code<4> hd<4> x2<4> vdd vss nand2_x1
XI3<3> code<3> hd<3> x2<3> vdd vss nand2_x1
XI3<2> code<2> hd<2> x2<2> vdd vss nand2_x1
XI3<1> code<1> hd<1> x2<1> vdd vss nand2_x1
XI3<0> code<0> hd<0> x2<0> vdd vss nand2_x1
XI4<4> ph<5> x3<4> vdd vss inv_x1
XI4<3> ph<4> x3<3> vdd vss inv_x1
XI4<2> ph<3> x3<2> vdd vss inv_x1
XI4<1> ph<2> x3<1> vdd vss inv_x1
XI4<0> ph<1> x3<0> vdd vss inv_x1
XI5<4> x1<4> x2<4> x3<4> dc<4> vdd vss nand3_x1
XI5<3> x1<3> x2<3> x3<3> dc<3> vdd vss nand3_x1
XI5<2> x1<2> x2<2> x3<2> dc<2> vdd vss nand3_x1
XI5<1> x1<1> x2<1> x3<1> dc<1> vdd vss nand3_x1
XI5<0> x1<0> x2<0> x3<0> dc<0> vdd vss nand3_x1
XI6<4> dc<4> clk rst_n code<4> codeb<4> vdd vss dffr_tg
XI6<3> dc<3> clk rst_n code<3> codeb<3> vdd vss dffr_tg
XI6<2> dc<2> clk rst_n code<2> codeb<2> vdd vss dffr_tg
XI6<1> dc<1> clk rst_n code<1> codeb<1> vdd vss dffr_tg
XI6<0> dc<0> clk rst_n code<0> codeb<0> vdd vss dffr_tg
XI7 done x3<4> y1 vdd vss nand2_x1
XI8 ph<0> y2 vdd vss inv_x1
XI9 y1 y2 dd vdd vss nand2_x1
XI10 dd clk rst_n done doneb vdd vss dffr_tg
.ends zq_sar5
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: zq_cal
** View name: schematic
.subckt zq_cal zq zq_en zq_start zq_clk zq_rst_n ib_zq pu_code<4> pu_code<3> pu_code<2>
+ pu_code<1> pu_code<0> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> zq_done
+ vdd vss vccq vssq
XI0 zq_en en_q enb_q vdd vss vccq vssq ls_up
XI1 enb_q vref_zq vccq vssq zq_vref
MM0 ib_zq ib_zq vccq vccq pch_hv W=2u L=1u m=1 nf=1
XI2 vref_zq zq ib_zq enb_q cmp_pu vdd vss vccq vssq zq_cmp
XI3 cmp_pu zq_clk zq_start zq_rst_n pu_code<4> pu_code<3> pu_code<2> pu_code<1>
+ pu_code<0> zq_done vdd vss zq_sar5
XI4 pu_code<4> pu_code<3> pu_code<2> pu_code<1> pu_code<0> en_q pu_g<4> pu_g<3> pu_g<2>
+ pu_g<1> pu_g<0> pu_gb<4> pu_gb<3> pu_gb<2> pu_gb<1> pu_gb<0> vdd vss vccq vssq
+ zq_gate_drv
XI5 pu_gb<4> pu_gb<3> pu_gb<2> pu_gb<1> pu_gb<0> zq vccq zq_pu_rep
XI6 pu_gb<4> pu_gb<3> pu_gb<2> pu_gb<1> pu_gb<0> pd_g<4> pd_g<3> pd_g<2> pd_g<1> pd_g<0>
+ npd vccq vssq zq_pd_rep
XI7 pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> en_q pd_g<4> pd_g<3> pd_g<2>
+ pd_g<1> pd_g<0> pd_gb<4> pd_gb<3> pd_gb<2> pd_gb<1> pd_gb<0> vdd vss vccq vssq
+ zq_gate_drv
XI8 vref_zq npd ib_zq enb_q cmp_pd vdd vss vccq vssq zq_cmp
XI10 zq_en zq_done net010 vdd vss nand2_x1
XI11 net010 pd_en vdd vss inv_x1
XI9 cmp_pd zq_clk pd_en vss zq_rst_n pd_code<4> pd_code<3> pd_code<2> pd_code<1>
+ pd_code<0> vdd vss updn_cnt5
.ends zq_cal
** End of subcircuit definition.

** Library name: NFIO_CAL
** Cell name: ib_dist
** View name: schematic
.subckt ib_dist ibias ib_zq ib_vref vccq vssq
MM0 ibias ibias vssq vssq nch_hv W=2u L=1u m=2 nf=1
MM1 ib_zq ibias vssq vssq nch_hv W=2u L=1u m=2 nf=1
MM2 net05 ibias vssq vssq nch_hv W=2u L=1u m=2 nf=1
MM3 net05 net05 vccq vccq pch_hv W=4u L=1u m=2 nf=1
MM4 ib_vref net05 vccq vccq pch_hv W=4u L=1u m=2 nf=1
.ends ib_dist
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: odt_leg_pin
** View name: schematic
.subckt odt_leg_pin pu_gb<2> pu_gb<1> pu_gb<0> pd_g<2> pd_g<1> pd_g<0> pad vccq vssq
MM2 np<2> pu_gb<2> vccq vccq pch_hv W=2u L=0.2u m=4 nf=1
RR2 np<2> pad 120
MM1 np<1> pu_gb<1> vccq vccq pch_hv W=2u L=0.2u m=2 nf=1
RR1 np<1> pad 240
MM0 np<0> pu_gb<0> vccq vccq pch_hv W=2u L=0.2u m=1 nf=1
RR0 np<0> pad 480
MM5 nn<2> pd_g<2> vssq vssq nch_hv W=1u L=0.2u m=4 nf=1
RR5 nn<2> pad 120
MM4 nn<1> pd_g<1> vssq vssq nch_hv W=1u L=0.2u m=2 nf=1
RR4 nn<1> pad 240
MM3 nn<0> pd_g<0> vssq vssq nch_hv W=1u L=0.2u m=1 nf=1
RR3 nn<0> pad 480
.ends odt_leg_pin
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: odt_ctrl
** View name: schematic
.subckt odt_ctrl odt_en dq_oe dqs_oe odt_code<2> odt_code<1> odt_code<0> pu_gb_d<2>
+ pu_gb_d<1> pu_gb_d<0> pd_g_d<2> pd_g_d<1> pd_g_d<0> pu_gb_s<2> pu_gb_s<1> pu_gb_s<0>
+ pd_g_s<2> pd_g_s<1> pd_g_s<0> vdd vss vccq vssq
XI6 odt_en net013 vdd vss inv_x1
XI7 net013 dq_oe net014 vdd vss nor2_x1
XI8 net013 dqs_oe net015 vdd vss nor2_x1
XI0 net014 oen_d net010 vdd vss vccq vssq ls_up
XI9 net015 oen_s net016 vdd vss vccq vssq ls_up
XI1<2> odt_code<2> oc_q<2> ocb_q<2> vdd vss vccq vssq ls_up
XI1<1> odt_code<1> oc_q<1> ocb_q<1> vdd vss vccq vssq ls_up
XI1<0> odt_code<0> oc_q<0> ocb_q<0> vdd vss vccq vssq ls_up
XI2<2> oc_q<2> oen_d nb_d<2> vccq vssq nand2_q
XI2<1> oc_q<1> oen_d nb_d<1> vccq vssq nand2_q
XI2<0> oc_q<0> oen_d nb_d<0> vccq vssq nand2_q
XI3<2> nb_d<2> nc_d<2> vccq vssq inv_q
XI3<1> nb_d<1> nc_d<1> vccq vssq inv_q
XI3<0> nb_d<0> nc_d<0> vccq vssq inv_q
XI4<2> nc_d<2> pu_gb_d<2> vccq vssq inv_q m=4
XI4<1> nc_d<1> pu_gb_d<1> vccq vssq inv_q m=4
XI4<0> nc_d<0> pu_gb_d<0> vccq vssq inv_q m=4
XI5<2> nb_d<2> pd_g_d<2> vccq vssq inv_q m=4
XI5<1> nb_d<1> pd_g_d<1> vccq vssq inv_q m=4
XI5<0> nb_d<0> pd_g_d<0> vccq vssq inv_q m=4
XI10<2> oc_q<2> oen_s nb_s<2> vccq vssq nand2_q
XI10<1> oc_q<1> oen_s nb_s<1> vccq vssq nand2_q
XI10<0> oc_q<0> oen_s nb_s<0> vccq vssq nand2_q
XI11<2> nb_s<2> nc_s<2> vccq vssq inv_q
XI11<1> nb_s<1> nc_s<1> vccq vssq inv_q
XI11<0> nb_s<0> nc_s<0> vccq vssq inv_q
XI12<2> nc_s<2> pu_gb_s<2> vccq vssq inv_q m=4
XI12<1> nc_s<1> pu_gb_s<1> vccq vssq inv_q m=4
XI12<0> nc_s<0> pu_gb_s<0> vccq vssq inv_q m=4
XI13<2> nb_s<2> pd_g_s<2> vccq vssq inv_q m=4
XI13<1> nb_s<1> pd_g_s<1> vccq vssq inv_q m=4
XI13<0> nb_s<0> pd_g_s<0> vccq vssq inv_q m=4
.ends odt_ctrl
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_pad_bidir
** View name: schematic
.subckt io_pad_bidir pad pad_rx pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2> ng<1>
+ ng<0> odt_pu_gb<2> odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> vccq
+ vssq
XI0 pad pad_rx vccq vssq esd_io_pad
XI1 pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2> ng<1> ng<0> pad vccq vssq tx_out_drv
XI2 odt_pu_gb<2> odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> pad vccq
+ vssq odt_leg_pin
CC0 pad vssq 0.2p
.ends io_pad_bidir
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_pad_in
** View name: schematic
.subckt io_pad_in pad pad_rx vccq vssq
XI0 pad pad_rx vccq vssq esd_io_pad
CC0 pad vssq 0.15p
.ends io_pad_in
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_ctrl
** View name: schematic
.subckt io_ctrl rx_en rx_mode_um dqs_se vref_int_en tm_rxobs tx_en re_se dq_oe dqs_oe
+ dqs_burst odt_en odt_code<2> odt_code<1> odt_code<0> drv_ovr_en pu_ovr<4> pu_ovr<3>
+ pu_ovr<2> pu_ovr<1> pu_ovr<0> pd_ovr<4> pd_ovr<3> pd_ovr<2> pd_ovr<1> pd_ovr<0>
+ zq_pu<4> zq_pu<3> zq_pu<2> zq_pu<1> zq_pu<0> zq_pd<4> zq_pd<3> zq_pd<2> zq_pd<1>
+ zq_pd<0> rx_en_q rx_enb_q dqs_se_q dqs_dif_q vint_q vintb_q selu selub en_m en_u
+ obs_en tx_en_q tx_enb_q re_se_q re_dif_q pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1>
+ pu_en_d<0> pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> pu_en_s<4>
+ pu_en_s<3> pu_en_s<2> pu_en_s<1> pu_en_s<0> pd_dis_s<4> pd_dis_s<3> pd_dis_s<2>
+ pd_dis_s<1> pd_dis_s<0> dqs_e dqs_o dqsb_e dqsb_o odt_pu_gb_d<2> odt_pu_gb_d<1>
+ odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0> odt_pu_gb_s<2> odt_pu_gb_s<1>
+ odt_pu_gb_s<0> odt_pd_g_s<2> odt_pd_g_s<1> odt_pd_g_s<0> vdd vss vccq vssq
XI0 rx_en rx_mode_um dqs_se vref_int_en tm_rxobs rx_en_q rx_enb_q dqs_se_q dqs_dif_q
+ vint_q vintb_q selu selub en_m en_u obs_en vdd vss vccq vssq rx_ctrl
XI1 zq_pu<4> zq_pu<3> zq_pu<2> zq_pu<1> zq_pu<0> zq_pd<4> zq_pd<3> zq_pd<2> zq_pd<1>
+ zq_pd<0> drv_ovr_en pu_ovr<4> pu_ovr<3> pu_ovr<2> pu_ovr<1> pu_ovr<0> pd_ovr<4>
+ pd_ovr<3> pd_ovr<2> pd_ovr<1> pd_ovr<0> pu_code<4> pu_code<3> pu_code<2> pu_code<1>
+ pu_code<0> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> vdd vss drv_code_mux
XI2 tx_en dq_oe dqs_oe dqs_burst re_se pu_code<4> pu_code<3> pu_code<2> pu_code<1>
+ pu_code<0> pd_code<4> pd_code<3> pd_code<2> pd_code<1> pd_code<0> tx_en_q tx_enb_q
+ re_se_q re_dif_q pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0> pd_dis_d<4>
+ pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> pu_en_s<4> pu_en_s<3> pu_en_s<2>
+ pu_en_s<1> pu_en_s<0> pd_dis_s<4> pd_dis_s<3> pd_dis_s<2> pd_dis_s<1> pd_dis_s<0>
+ dqs_e dqs_o dqsb_e dqsb_o vdd vss vccq vssq tx_ctrl
XI3 odt_en dq_oe dqs_oe odt_code<2> odt_code<1> odt_code<0> odt_pu_gb_d<2>
+ odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0> odt_pu_gb_s<2>
+ odt_pu_gb_s<1> odt_pu_gb_s<0> odt_pd_g_s<2> odt_pd_g_s<1> odt_pd_g_s<0> vdd vss vccq
+ vssq odt_ctrl
.ends io_ctrl
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_bias
** View name: schematic
.subckt io_bias ibias sr_code<1> sr_code<0> vref_ext vref_code<4> vref_code<3>
+ vref_code<2> vref_code<1> vref_code<0> vint_q vintb_q vbp_sr vbn_sr vref_rx ib_zq vdd
+ vss vccq vssq
XI0 ibias ib_zq ib_vref vccq vssq ib_dist
XI1 sr_code<1> sr_code<0> vbp_sr vbn_sr vdd vss vccq vssq tx_sr_bias
XI2 vref_ext vref_code<4> vref_code<3> vref_code<2> vref_code<1> vref_code<0> vint_q
+ vintb_q ib_vref vref_rx vdd vss vccq vssq rx_vref_gen
.ends io_bias
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_dq_slice
** View name: schematic
.subckt io_dq_slice pad vref_rx en_q enb_q dskw<2> dskw<1> dskw<0> ckt_m ckc_m ckt_u
+ ckc_u selu selub div_p div_n rd<3> rd<2> rd<1> rd<0> de do ck_lf pu_en<4> pu_en<3>
+ pu_en<2> pu_en<1> pu_en<0> pd_dis<4> pd_dis<3> pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr
+ vbn_sr odt_pu_gb<2> odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> vdd
+ vss vccq vssq
XI0 pad pad_rx pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2> ng<1> ng<0> odt_pu_gb<2>
+ odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> vccq vssq io_pad_bidir
XI1 pad_rx vref_rx en_q enb_q dskw<2> dskw<1> dskw<0> ckt_m ckc_m ckt_u ckc_u selu selub
+ div_p div_n rd<3> rd<2> rd<1> rd<0> vdd vss vccq vssq rx_dq_slice
XI2 de do ck_lf pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0> pd_dis<4> pd_dis<3>
+ pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr vbn_sr pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3>
+ ng<2> ng<1> ng<0> vdd vss vccq vssq tx_dq_slice
.ends io_dq_slice
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: io_dqs_slice
** View name: schematic
.subckt io_dqs_slice pad pad_rx de do ck_lf pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0>
+ pd_dis<4> pd_dis<3> pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr vbn_sr odt_pu_gb<2>
+ odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> vdd vss vccq vssq
XI0 pad pad_rx pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3> ng<2> ng<1> ng<0> odt_pu_gb<2>
+ odt_pu_gb<1> odt_pu_gb<0> odt_pd_g<2> odt_pd_g<1> odt_pd_g<0> vccq vssq io_pad_bidir
XI2 de do ck_lf pu_en<4> pu_en<3> pu_en<2> pu_en<1> pu_en<0> pd_dis<4> pd_dis<3>
+ pd_dis<2> pd_dis<1> pd_dis<0> vbp_sr vbn_sr pg<4> pg<3> pg<2> pg<1> pg<0> ng<4> ng<3>
+ ng<2> ng<1> ng<0> vdd vss vccq vssq tx_dq_slice
.ends io_dqs_slice
** End of subcircuit definition.

** Library name: NFIO_IO
** Cell name: nf_io_top
** View name: schematic
.subckt nf_io_top dq<7> dq<6> dq<5> dq<4> dq<3> dq<2> dq<1> dq<0> dqs dqsb re reb zq
+ vref_ext din<31> din<30> din<29> din<28> din<27> din<26> din<25> din<24> din<23>
+ din<22> din<21> din<20> din<19> din<18> din<17> din<16> din<15> din<14> din<13>
+ din<12> din<11> din<10> din<9> din<8> din<7> din<6> din<5> din<4> din<3> din<2> din<1>
+ din<0> din_clk dout_e<7> dout_e<6> dout_e<5> dout_e<4> dout_e<3> dout_e<2> dout_e<1>
+ dout_e<0> dout_o<7> dout_o<6> dout_o<5> dout_o<4> dout_o<3> dout_o<2> dout_o<1>
+ dout_o<0> rclk_core rx_en rx_mode_um dqs_se vref_int_en vref_code<4> vref_code<3>
+ vref_code<2> vref_code<1> vref_code<0> dqs_dly<2> dqs_dly<1> dqs_dly<0> dq_dskw<23>
+ dq_dskw<22> dq_dskw<21> dq_dskw<20> dq_dskw<19> dq_dskw<18> dq_dskw<17> dq_dskw<16>
+ dq_dskw<15> dq_dskw<14> dq_dskw<13> dq_dskw<12> dq_dskw<11> dq_dskw<10> dq_dskw<9>
+ dq_dskw<8> dq_dskw<7> dq_dskw<6> dq_dskw<5> dq_dskw<4> dq_dskw<3> dq_dskw<2>
+ dq_dskw<1> dq_dskw<0> rx_rst_n tm_rxobs rx_obs tx_en re_se dq_oe dqs_oe dqs_burst
+ sr_code<1> sr_code<0> odt_en odt_code<2> odt_code<1> odt_code<0> cal_clk zq_en
+ zq_start zq_rst_n zq_done zq_pu_code<4> zq_pu_code<3> zq_pu_code<2> zq_pu_code<1>
+ zq_pu_code<0> zq_pd_code<4> zq_pd_code<3> zq_pd_code<2> zq_pd_code<1> zq_pd_code<0>
+ drv_ovr_en pu_ovr<4> pu_ovr<3> pu_ovr<2> pu_ovr<1> pu_ovr<0> pd_ovr<4> pd_ovr<3>
+ pd_ovr<2> pd_ovr<1> pd_ovr<0> dcc_train dcc_rst_n dcc_lock dcc_code<4> dcc_code<3>
+ dcc_code<2> dcc_code<1> dcc_code<0> ibias vdd vccq vss vssq
XI0 rx_en rx_mode_um dqs_se vref_int_en tm_rxobs tx_en re_se dq_oe dqs_oe dqs_burst
+ odt_en odt_code<2> odt_code<1> odt_code<0> drv_ovr_en pu_ovr<4> pu_ovr<3> pu_ovr<2>
+ pu_ovr<1> pu_ovr<0> pd_ovr<4> pd_ovr<3> pd_ovr<2> pd_ovr<1> pd_ovr<0> zq_pu_code<4>
+ zq_pu_code<3> zq_pu_code<2> zq_pu_code<1> zq_pu_code<0> zq_pd_code<4> zq_pd_code<3>
+ zq_pd_code<2> zq_pd_code<1> zq_pd_code<0> rx_en_q rx_enb_q dqs_se_q dqs_dif_q vint_q
+ vintb_q selu selub en_m en_u obs_en tx_en_q tx_enb_q re_se_q re_dif_q pu_en_d<4>
+ pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0> pd_dis_d<4> pd_dis_d<3> pd_dis_d<2>
+ pd_dis_d<1> pd_dis_d<0> pu_en_s<4> pu_en_s<3> pu_en_s<2> pu_en_s<1> pu_en_s<0>
+ pd_dis_s<4> pd_dis_s<3> pd_dis_s<2> pd_dis_s<1> pd_dis_s<0> dqs_e dqs_o dqsb_e dqsb_o
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ odt_pu_gb_s<2> odt_pu_gb_s<1> odt_pu_gb_s<0> odt_pd_g_s<2> odt_pd_g_s<1> odt_pd_g_s<0>
+ vdd vss vccq vssq io_ctrl
XI1 ibias sr_code<1> sr_code<0> vref_ext_rx vref_code<4> vref_code<3> vref_code<2>
+ vref_code<1> vref_code<0> vint_q vintb_q vbp_sr vbn_sr vref_rx ib_zq vdd vss vccq vssq
+ io_bias
XI2 zq zq_en zq_start cal_clk zq_rst_n ib_zq zq_pu_code<4> zq_pu_code<3> zq_pu_code<2>
+ zq_pu_code<1> zq_pu_code<0> zq_pd_code<4> zq_pd_code<3> zq_pd_code<2> zq_pd_code<1>
+ zq_pd_code<0> zq_done vdd vss vccq vssq zq_cal
XI3 re_rx reb_rx vref_rx re_se_q re_dif_q tx_en_q tx_enb_q dcc_code<4> dcc_code<3>
+ dcc_code<2> dcc_code<1> dcc_code<0> ck_lf<9> ck_lf<8> ck_lf<7> ck_lf<6> ck_lf<5>
+ ck_lf<4> ck_lf<3> ck_lf<2> ck_lf<1> ck_lf<0> ck_dcc rclk_core vdd vss vccq vssq
+ re_clk_path
XI4 ck_dcc cal_clk dcc_train dcc_rst_n dcc_code<4> dcc_code<3> dcc_code<2> dcc_code<1>
+ dcc_code<0> dcc_lock vdd vss dcc_ctrl
XI5 dqs_rx dqsb_rx vref_rx dqs_se_q dqs_dif_q rx_en_q rx_enb_q dqs_dly<2> dqs_dly<1>
+ dqs_dly<0> en_m en_u ckt_m<8> ckt_m<7> ckt_m<6> ckt_m<5> ckt_m<4> ckt_m<3> ckt_m<2>
+ ckt_m<1> ckt_m<0> ckc_m<8> ckc_m<7> ckc_m<6> ckc_m<5> ckc_m<4> ckc_m<3> ckc_m<2>
+ ckc_m<1> ckc_m<0> ckt_u<8> ckt_u<7> ckt_u<6> ckt_u<5> ckt_u<4> ckt_u<3> ckt_u<2>
+ ckt_u<1> ckt_u<0> ckc_u<8> ckc_u<7> ckc_u<6> ckc_u<5> ckc_u<4> ckc_u<3> ckc_u<2>
+ ckc_u<1> ckc_u<0> vdd vss vccq vssq rx_dqs_path
XI6 ckt_m<8> ckt_u<8> selu selub rx_rst_n div_p div_n din_clk vdd vss rx_ckdiv_slice
XI7<7> dq<7> vref_rx rx_en_q rx_enb_q dq_dskw<23> dq_dskw<22> dq_dskw<21> ckt_m<7>
+ ckc_m<7> ckt_u<7> ckc_u<7> selu selub div_p div_n din<31> din<30> din<29> din<28>
+ dout_e<7> dout_o<7> ck_lf<7> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ vdd vss vccq vssq io_dq_slice
XI7<6> dq<6> vref_rx rx_en_q rx_enb_q dq_dskw<20> dq_dskw<19> dq_dskw<18> ckt_m<6>
+ ckc_m<6> ckt_u<6> ckc_u<6> selu selub div_p div_n din<27> din<26> din<25> din<24>
+ dout_e<6> dout_o<6> ck_lf<6> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ vdd vss vccq vssq io_dq_slice
XI7<5> dq<5> vref_rx rx_en_q rx_enb_q dq_dskw<17> dq_dskw<16> dq_dskw<15> ckt_m<5>
+ ckc_m<5> ckt_u<5> ckc_u<5> selu selub div_p div_n din<23> din<22> din<21> din<20>
+ dout_e<5> dout_o<5> ck_lf<5> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ vdd vss vccq vssq io_dq_slice
XI7<4> dq<4> vref_rx rx_en_q rx_enb_q dq_dskw<14> dq_dskw<13> dq_dskw<12> ckt_m<4>
+ ckc_m<4> ckt_u<4> ckc_u<4> selu selub div_p div_n din<19> din<18> din<17> din<16>
+ dout_e<4> dout_o<4> ck_lf<4> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ vdd vss vccq vssq io_dq_slice
XI7<3> dq<3> vref_rx rx_en_q rx_enb_q dq_dskw<11> dq_dskw<10> dq_dskw<9> ckt_m<3>
+ ckc_m<3> ckt_u<3> ckc_u<3> selu selub div_p div_n din<15> din<14> din<13> din<12>
+ dout_e<3> dout_o<3> ck_lf<3> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0>
+ pd_dis_d<4> pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr
+ odt_pu_gb_d<2> odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0>
+ vdd vss vccq vssq io_dq_slice
XI7<2> dq<2> vref_rx rx_en_q rx_enb_q dq_dskw<8> dq_dskw<7> dq_dskw<6> ckt_m<2> ckc_m<2>
+ ckt_u<2> ckc_u<2> selu selub div_p div_n din<11> din<10> din<9> din<8> dout_e<2>
+ dout_o<2> ck_lf<2> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0> pd_dis_d<4>
+ pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr odt_pu_gb_d<2>
+ odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0> vdd vss vccq
+ vssq io_dq_slice
XI7<1> dq<1> vref_rx rx_en_q rx_enb_q dq_dskw<5> dq_dskw<4> dq_dskw<3> ckt_m<1> ckc_m<1>
+ ckt_u<1> ckc_u<1> selu selub div_p div_n din<7> din<6> din<5> din<4> dout_e<1>
+ dout_o<1> ck_lf<1> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0> pd_dis_d<4>
+ pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr odt_pu_gb_d<2>
+ odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0> vdd vss vccq
+ vssq io_dq_slice
XI7<0> dq<0> vref_rx rx_en_q rx_enb_q dq_dskw<2> dq_dskw<1> dq_dskw<0> ckt_m<0> ckc_m<0>
+ ckt_u<0> ckc_u<0> selu selub div_p div_n din<3> din<2> din<1> din<0> dout_e<0>
+ dout_o<0> ck_lf<0> pu_en_d<4> pu_en_d<3> pu_en_d<2> pu_en_d<1> pu_en_d<0> pd_dis_d<4>
+ pd_dis_d<3> pd_dis_d<2> pd_dis_d<1> pd_dis_d<0> vbp_sr vbn_sr odt_pu_gb_d<2>
+ odt_pu_gb_d<1> odt_pu_gb_d<0> odt_pd_g_d<2> odt_pd_g_d<1> odt_pd_g_d<0> vdd vss vccq
+ vssq io_dq_slice
XI8 dqs dqs_rx dqs_e dqs_o ck_lf<8> pu_en_s<4> pu_en_s<3> pu_en_s<2> pu_en_s<1>
+ pu_en_s<0> pd_dis_s<4> pd_dis_s<3> pd_dis_s<2> pd_dis_s<1> pd_dis_s<0> vbp_sr vbn_sr
+ odt_pu_gb_s<2> odt_pu_gb_s<1> odt_pu_gb_s<0> odt_pd_g_s<2> odt_pd_g_s<1> odt_pd_g_s<0>
+ vdd vss vccq vssq io_dqs_slice
XI9 dqsb dqsb_rx dqsb_e dqsb_o ck_lf<9> pu_en_s<4> pu_en_s<3> pu_en_s<2> pu_en_s<1>
+ pu_en_s<0> pd_dis_s<4> pd_dis_s<3> pd_dis_s<2> pd_dis_s<1> pd_dis_s<0> vbp_sr vbn_sr
+ odt_pu_gb_s<2> odt_pu_gb_s<1> odt_pu_gb_s<0> odt_pd_g_s<2> odt_pd_g_s<1> odt_pd_g_s<0>
+ vdd vss vccq vssq io_dqs_slice
XI10 re re_rx vccq vssq io_pad_in
XI11 reb reb_rx vccq vssq io_pad_in
XI12 vref_ext vref_ext_rx vccq vssq io_pad_in
XI13 zq vccq vssq esd_prim
XI14 vdd vss vccq vssq esd_rail
XI15 div_p obs_en rx_obs vdd vss rx_obs_buf
MM0 vss vdd vss vss nch W=5u L=1u m=40 nf=1
MM1 vssq vccq vssq vssq nch_hv W=5u L=1u m=40 nf=1
.ends nf_io_top
** End of subcircuit definition.

.END
