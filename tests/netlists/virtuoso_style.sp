** Generated for: hspiceD
** Library name: test_lib
** Cell name: top_mixed
** View name: schematic
.subckt ota5t vinp vinn vout vbn vdd vss
mm1 net1 vinp tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm2 vout vinn tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm3 net1 net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm4 vout net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm5 tail vbn vss vss nch_lvt w=8e-6
+ l=200e-9 m=2
.ends ota5t
** Cell name: inv
.subckt inv in out vdd vss
mn0 out in vss vss nch_lvt w=1e-6 l=45e-9 $ pull-down
mp0 out in vdd vdd pch_lvt w=2e-6 l=45e-9
.ends inv
.SUBCKT nand2 A B Y VDD VSS
MN1 Y A X VSS nch_lvt W=1u L=45n
MN2 X B VSS VSS nch_lvt W=1u L=45n
MP1 Y A VDD VDD pch_lvt W=1u L=45n
MP2 Y B VDD VDD pch_lvt W=1u L=45n
.ENDS
.subckt top_mixed a b o en vb vdd vss
xi0 a b n1 vb vdd vss ota5t
xi1 n1 n2 vdd vss inv
xi3 n2 en n3 vdd vss nand2
xi2 n3 o vdd vss inv
c0 n1 vss 10f
r0 o vss 1k
.ends top_mixed
