** Generated for: hspiceD
** Generated on: Nov 14 09:12:44 2026
** Design library name: wgdhcu
** Design cell name: udmp
** Design view name: wxatw

.TEMP 25.0
.OPTION ARTIST=2 INGOLD=2 PARHIER=LOCAL PSF=2

** Device model cards
.MODEL vw445g PMOS LEVEL=54 VERSION=4.5 VTH0=-0.30 TOXE=2.1n
.MODEL ycgzf PMOS LEVEL=54 VERSION=4.5 VTH0=-0.50 TOXE=5.2n
.MODEL ka1ebp NMOS LEVEL=54 VERSION=4.5 VTH0=0.40  TOXE=2.1n
.MODEL ns67 NMOS LEVEL=54 VERSION=4.5 VTH0=0.30  TOXE=2.1n
.MODEL jil3gy NMOS LEVEL=54 VERSION=4.5 VTH0=0.50  TOXE=5.2n
.MODEL ad57k3 PMOS LEVEL=54 VERSION=4.5 VTH0=-0.40 TOXE=2.1n

** Library name: zn2ats
** Cell name: vmgkr
** View name: wxatw
.subckt vmgkr vssq pto2s rjct lweqg vccq wove xr7h
Me6th6v lweqg rjct theyww vccq ycgzf W=8u L=0.2u m=2 nf=4
Mdkq1p2 rwmoqj xr7h theyww vccq ycgzf W=8u L=0.2u m=2 nf=4
Mg6c3i6 rwmoqj xr7h nedm57 vssq jil3gy W=4u L=0.2u m=2 nf=2
Mhzb5un theyww rwmoqj dhczr vccq ycgzf W=12u L=0.2u m=2 nf=4
Mzpxq lweqg rjct nedm57 vssq jil3gy W=4u L=0.2u m=2 nf=2
Mjpqt78 dhczr wove vccq vccq ycgzf W=16u L=0.2u m=1 nf=4
Mv644b lweqg wove vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mjlzb nedm57 rwmoqj pxyrf5 vssq jil3gy W=6u L=0.2u m=2 nf=2
Mcrtr rwmoqj pto2s vccq vccq ycgzf W=1u L=0.2u m=1 nf=1
Mook2 pxyrf5 pto2s vssq vssq jil3gy W=8u L=0.2u m=1 nf=2
.ends vmgkr
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: bj6r
** View name: wxatw
.subckt bj6r zt7ee8 tywlx vss vtam vdd
Mn7nehr zt7ee8 i03t mhh3s vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Mrgm4v ec55 pk1ach mhh3s vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mnkfax wmzx pk1ach b9v55 vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Xjppv pk1ach vdd vss i03t l5tu7
Xbwmhlx ec55 vdd vss wmzx l5tu7
Xmd2853 i03t vdd vss vtam l5tu7
Xc5kno4 xwfqvz vdd vss tywlx l5tu7
Xfk5z wmzx vdd vss mhh3s l5tu7
Mg39ay ec55 i03t mhh3s vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Mp9l02h zt7ee8 pk1ach mhh3s vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Xfrw71 tywlx vdd vss b9v55 l5tu7
Mujex xwfqvz i03t b9v55 vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mgrmz wmzx i03t b9v55 vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mc16mit xwfqvz pk1ach b9v55 vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
.ends bj6r
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: fwhwl
** View name: wxatw
.subckt fwhwl xx9mog xt581u<1> mita<2> mita<3> jx9e<1> mita<0> vssq xt581u<2> xt581u<0>
+ sq6v18 mita<4> c2108<3> mita<1> vccq c2108<4> jx9e<0> c2108<0> c2108<2> jx9e<2>
+ c2108<1>
Ctk4uyq sq6v18 vssq 0.2p
Xag486n vssq c2108<1> c2108<4> mita<0> mita<3> vccq mita<4> c2108<3> c2108<0> sq6v18
+ mita<2> mita<1> c2108<2> f8zz
Xe58n vssq xx9mog sq6v18 vccq i6p6kc
Xuuqsg jx9e<1> jx9e<2> xt581u<0> vccq xt581u<1> sq6v18 jx9e<0> xt581u<2> vssq ryk2
.ends fwhwl
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: ye8xk0
** View name: wxatw
.subckt ye8xk0 vssq a87hc vccq k1x6x
Xx44wou vssq a87hc k1x6x vccq i6p6kc
Cus442v k1x6x vssq 0.15p
.ends ye8xk0
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: l0sxx
** View name: wxatw
.subckt l0sxx ej5ebo rfomo fj7kaj yb1z y07ql<1> vdd y3h4vh vss y07ql<3> y07ql<0>
+ y07ql<2>
Xgl2uo woj6 y07ql<2> vss fj7kaj vdd bj6r
Xjjxh jcjxgh y07ql<0> vss fj7kaj vdd bj6r
Xt847 ej5ebo y07ql<3> vss fj7kaj vdd bj6r
Xgsu13 ej5ebo btk1 vss y3h4vh vdd bj6r
Xt9ui btk1 y07ql<1> vss fj7kaj vdd bj6r
Xv3o0 rfomo woj6 vss yb1z vdd bj6r
Xpaz53w woj6 jcjxgh vss y3h4vh vdd bj6r
.ends l0sxx
** End of subcircuit definition.

** Library name: ato68m
** Cell name: ajlh
** View name: wxatw
.subckt ajlh ypzua vss h77r vdd
Muwwvgh yjxr h77r vss vss ns67 W=2u L=0.06u m=1 nf=4
Mqit7 ypzua yjxr vdd vdd vw445g W=16u L=0.06u m=1 nf=16
Meovf yjxr h77r vdd vdd vw445g W=4u L=0.06u m=1 nf=4
Mfveqd ypzua yjxr vss vss ns67 W=8u L=0.06u m=1 nf=8
.ends ajlh
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: ji9j
** View name: wxatw
.subckt ji9j ns8xwf zueh vdd e5s98 l0zypq vss
Xwqz7 edx908 vss cbgn vdd l0zypq aga5n egkf2y zuhc6m
Xw15uhu vss p7uifz yhqg iirk vdd yavkxw
Xtjg6 d5ewky vss cbgn vdd l0zypq qtqp zueh zuhc6m
Xdv9mi3 qtqp zueh vss yhqg vdd d9b5zl
Xt4vi16 oy5v vdd vss p7uifz l5tu7
Xrvyt5i ii2ly3 vss cbgn vdd l0zypq e5s98 iiukb zuhc6m
Xsy6w7 vss egkf2y edx908 p7uifz vdd yavkxw
Xtafu2y cbgn vdd vss ns8xwf l5tu7
Xe6w3 vss mqims aga5n oy5v vdd yavkxw
Xural fskbcd vss cbgn vdd l0zypq iirk vdd zuhc6m
Xe8pf32 vss iiukb ii2ly3 mqims vdd yavkxw
.ends ji9j
** End of subcircuit definition.

** Library name: fxoq
** Cell name: i6p6kc
** View name: wxatw
.subckt i6p6kc vssq vfryt y3akw4 vccq
Rj26d iys2 vssq 10k
Mgjykmj vfryt vssq vssq vssq jil3gy W=10u L=0.3u m=1 nf=2
Rj57v pc2x8 vccq 10k
Mr33a y3akw4 iys2 vssq vssq jil3gy W=60u L=0.3u m=2 nf=12
Rv9j046 y3akw4 vfryt 200
Mk3q5 y3akw4 pc2x8 vccq vccq ycgzf W=60u L=0.3u m=2 nf=12
.ends i6p6kc
** End of subcircuit definition.

** Library name: ato68m
** Cell name: unj9o
** View name: wxatw
.subckt unj9o s885oa<3> yqfl s885oa<1> i5q7 s885oa<2> s885oa<4> vdd s885oa<0> vss
Xjgg1k co7nh vdd vss yqfl xz3c
Xy6iq vss u9myn i5q7 vdd yydl
Xpz90 s885oa<2> s885oa<0> s885oa<3> vdd u9myn vss s885oa<4> co7nh s885oa<1> wtth
.ends unj9o
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: we5v
** View name: wxatw
.subckt we5v vss agnm<0> eyha agnm<1> z1zpqz hch4x zdjooo agnm<3> j3zd vccq omlh qm5cj
+ u1d4 wy3vv gvr6 e1eb<1> e1eb<0> vssq e1eb<2> faqfgf bqc6 agnm<2> vdd
Xfxcymh vss ojk5b qm5cj zdjooo fy8h b76vx vdd kr7x
Xzn1tt bqc6 vssq vccq vccq fi7rh vssq q8m8
Xpnitc i8uru2 jqhm vccq vssq vdd vss edau8i
Xonzvxn r8ws tswc omlh z7dl8 agnm<1> vdd eyha vss agnm<3> agnm<0> agnm<2> l0sxx
Xgk3hga vdd fy8h r8ws z7dl8 l56kpw vss tswc bxgg
Xot9fv3 vss i8uru2 b76vx e1eb<0> e1eb<1> vdd e1eb<2> ismh
Xojjo vss z1zpqz qm5cj zdjooo l56kpw u1d4 vdd kr7x
Xqp63 b76vx ojk5b vss vdd qm5cj xbcz59
Xafue vss j3zd qm5cj zdjooo z7dl8 faqfgf vdd kr7x
Xm8bpx vssq wy3vv gvr6 jqhm vccq hch4x fi7rh vmgkr
.ends we5v
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: yavkxw
** View name: wxatw
.subckt yavkxw vss cwi5m d470n n7av vdd
Mdm5zc1 n23hb n7av vss vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mptqi cwi5m d470n vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mo509jr cwi5m d470n n23hb vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mc17t0a cwi5m n7av vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
.ends yavkxw
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: z78y9
** View name: wxatw
.subckt z78y9 vccq siir dk75u vssq
Cvgja dk75u vssq 1p
Mic1ra kos8 siir vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Runvly dk75u vssq 10k
Ry4pe kos8 dk75u 10k
.ends z78y9
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: bxgg
** View name: wxatw
.subckt bxgg vdd q5bjz g3u8ja p4rq ukw8 vss hjd6z7
Xa98n8v ukw8 hjd6z7 vss ewfie2 vdd q5bjz u0vlr
Xk2zc57 p4rq g3u8ja vss fj73n vdd q5bjz u0vlr
.ends bxgg
** End of subcircuit definition.

** Library name: ato68m
** Cell name: siyoi
** View name: wxatw
.subckt siyoi vss l0z1uw z1xj xfij vdd
Mc41u9l l0z1uw vss z1ulz vdd vw445g W=0.6u L=0.06u m=1 nf=1
Mznveo xfij zjra vss vss ns67 W=1.2u L=0.06u m=1 nf=2
Mq3mq xfij zjra vdd vdd vw445g W=2.4u L=0.06u m=1 nf=2
Moimv67 zjra l0z1uw vdd vdd vw445g W=1.2u L=0.06u m=1 nf=2
Mgmj1lq z1xj z1ulz vss vss ns67 W=1.2u L=0.06u m=1 nf=2
Msh5aj8 l0z1uw vdd z1ulz vss ns67 W=0.6u L=0.06u m=1 nf=1
Mcd6s zjra l0z1uw vss vss ns67 W=0.6u L=0.06u m=1 nf=1
Mw8kq z1xj z1ulz vdd vdd vw445g W=2.4u L=0.06u m=1 nf=2
.ends siyoi
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: wfrbt
** View name: wxatw
.subckt wfrbt g5s2 okacgj g9n4zp vss vdd
Msm8l g9n4zp okacgj gole vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mkbyisi g9n4zp w6fo woxw vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
My82t4i x68p g5s2 vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mymeq x68p g5s2 vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Miiulm6 w6fo okacgj vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mrmsj woxw okacgj vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mr3js w6fo okacgj vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
My8f9vj rjg3ce g5s2 vss vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mu3ap g9n4zp w6fo rjg3ce vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mj62u woxw x68p vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mgijgj g9n4zp g5s2 woxw vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mi9g3x gole x68p vss vss ka1ebp W=0.4u L=0.06u m=1 nf=1
.ends wfrbt
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: kr7x
** View name: wxatw
.subckt kr7x vss w73d59 t0a3l q1ghmr gwfbl s2jpi vdd
Xk3552 vss w73d59 t0a3l vdd fk1oi yo4ne
Xskt9w vss s2jpi q1ghmr vdd g5af4r yo4ne
Xc807v vss fk1oi g5af4r vdd gwfbl yo4ne
.ends kr7x
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: un713b
** View name: wxatw
.subckt un713b wkqkft<5> wqm5q1 n45ct<6> n1jm<2> lgp56p<1> n45ct<3> hb53 wkqkft<1>
+ n45ct<2> vgvk6<3> n45ct<0> wap5kq n1jm<6> n45ct<1> o9g8 wkqkft<8> l5d9x wkqkft<0>
+ vgvk6<4> vssq vdd n1jm<3> s8ql n1jm<1> r8qt33 vgvk6<7> n45ct<7> jhzo vgvk6<2> vgvk6<0>
+ lgp56p<0> n1jm<7> wkqkft<6> n1jm<8> n1jm<5> lgp56p<2> yly3 vgvk6<5> wkqkft<3> vgvk6<8>
+ vgvk6<1> vccq n45ct<5> n1jm<4> wkqkft<4> n1jm<0> wkqkft<2> vgvk6<6> n45ct<4> vss
+ n45ct<8> wkqkft<7>
Xn9e3a vss wap5kq vdd dy98 zsmws uye5vz
Xqd2e r8qt33 s8ql vccq wqm5q1 qtdhx vssq q8m8
Xo1nhy o9g8 vssq vccq vccq bigl vssq q8m8
Xcjz2 vss n45ct<8> n45ct<2> n45ct<6> n45ct<7> n45ct<5> n45ct<4> kkalkx n45ct<3> n45ct<1>
+ vdd n45ct<0> wggy
Xrawl vss jhzo vdd kkalkx zsmws uye5vz
Xzafk vss y7t3bu uiryh lgp56p<0> lgp56p<1> vdd lgp56p<2> ismh
Xqd8h vdd vgvk6<0> vgvk6<5> vgvk6<2> vgvk6<7> vgvk6<6> vgvk6<8> uw7vmi vgvk6<4> vss
+ vgvk6<3> vgvk6<1> ax7dv
Xg2mqxz vss jhzo vdd r3jf uiryh uye5vz
Xku8m vss ushjm zsmws lgp56p<0> lgp56p<1> vdd lgp56p<2> ismh
Xq4oy vdd wkqkft<0> wkqkft<5> wkqkft<2> wkqkft<7> wkqkft<6> wkqkft<8> dy98 wkqkft<4> vss
+ wkqkft<3> wkqkft<1> ax7dv
Xec8ei vss n1jm<8> n1jm<2> n1jm<6> n1jm<7> n1jm<5> n1jm<4> r3jf n1jm<3> n1jm<1> vdd
+ n1jm<0> wggy
Xqk570y y7t3bu h7i2d5 vccq vssq vdd vss edau8i
Xydha ushjm uw6e vccq vssq vdd vss edau8i
Xex8p5 vssq l5d9x bigl h7i2d5 vccq hb53 qtdhx vmgkr
Xey70 vss wap5kq vdd uw7vmi uiryh uye5vz
Xbyvi yly3 wqm5q1 vccq s8ql qtdhx vssq q8m8
Xne2gtq vssq l5d9x qtdhx uw6e vccq hb53 bigl vmgkr
.ends un713b
** End of subcircuit definition.

** Library name: ato68m
** Cell name: ne2krl
** View name: wxatw
.subckt ne2krl oyg9a u7979u<5> muv94i qg5xh u7979u<0> vssq vdd g7xd<1> u7979u<3> dwoow
+ u7979u<2> pt8gu g7xd<2> ae9l u7979u<6> u7979u<8> xagan vss g7xd<3> u7979u<1> u7979u<9>
+ u7979u<7> g7xd<4> g7xd<0> vccq u7979u<4> l95t3 g9sl
Xfzn10e g7xd<3> hc7sd g7xd<1> q2wale g7xd<2> g7xd<4> vdd g7xd<0> vss unj9o
Xbimsss t48x u7979u<6> u7979u<8> u7979u<9> l95t3 u7979u<0> u7979u<2> vss vdd u7979u<4>
+ u7979u<7> u7979u<1> u7979u<5> ectk u7979u<3> hux9
Xjwlg0f vdd dwoow ae9l qg5xh oyg9a vssq q2wale g9sl vccq pt8gu vss muv94i ciz0t2
Xug4k xagan vss ectk vdd ajlh
Xhw5d vdd vss hc7sd t48x f7hz
.ends ne2krl
** End of subcircuit definition.

** Library name: ato68m
** Cell name: ciz0t2
** View name: wxatw
.subckt ciz0t2 vdd bt0b1y jlgd g8jthl edkvt vssq c3qhh oi8e vccq wbac vss mkdw1
Xg18yy oi8e wbac vccq g8jthl rg3xy vssq q8m8
Xq0hcna c3qhh xkra vccq vssq vdd vss edau8i
Xtq6k3 vssq bt0b1y rg3xy xkra vccq jlgd kmsu0y vmgkr
Xwk3u7 vssq bt0b1y kmsu0y jnrb4 vccq jlgd rg3xy vmgkr
Xqy3gl edkvt g8jthl vccq wbac rg3xy vssq q8m8
Xln8g mkdw1 vssq vccq vccq kmsu0y vssq q8m8
.ends ciz0t2
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: fgjco
** View name: wxatw
.subckt fgjco s802 opjbuu ymovk vssq d3u11d vccq g5k3l r5jy
Cvzljq cmokm g5k3l 0.8p
Macfm n8lleo d3u11d vssq vssq jil3gy W=4u L=1u m=2 nf=1
Myri2kk w9rzz s802 n8lleo vssq jil3gy W=4u L=0.5u m=2 nf=1
Mov8f g5k3l w9rzz vccq vccq ycgzf W=8u L=0.3u m=4 nf=2
Mz2n1 w9rzz ymovk vccq vccq ycgzf W=1u L=0.2u m=1 nf=1
Mjxevhe g5k3l d3u11d vssq vssq jil3gy W=4u L=1u m=8 nf=1
Mjoryzz mhm4u opjbuu n8lleo vssq jil3gy W=4u L=0.5u m=2 nf=1
Mbh07 d3u11d d3u11d vssq vssq jil3gy W=2u L=1u m=1 nf=1
Mk0piw mhm4u mhm4u vccq vccq ycgzf W=4u L=0.5u m=2 nf=1
Mqszi d3u11d r5jy vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Rbkfiuz w9rzz cmokm 5k
Mybh4 w9rzz mhm4u vccq vccq ycgzf W=4u L=0.5u m=2 nf=1
.ends fgjco
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: kfwj
** View name: wxatw
.subckt kfwj vdd lajhyo vss b3vsp
Murs6 b3vsp lajhyo vdd vdd vw445g W=0.8u L=0.06u m=1 nf=2
Mv8vr b3vsp lajhyo vss vss ns67 W=0.4u L=0.06u m=1 nf=1
.ends kfwj
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: mu5k
** View name: wxatw
.subckt mu5k bofaru ef1pig vem9ep vdd c28g vss
Mbxhhx vem9ep bofaru vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mswgt vem9ep ef1pig vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mi363 cxv7t9 bofaru uqdpc vdd ad57k3 W=1.2u L=0.06u m=1 nf=2
Msz5s vem9ep c28g cxv7t9 vdd ad57k3 W=1.2u L=0.06u m=1 nf=2
Mbwrfo uqdpc ef1pig vdd vdd ad57k3 W=1.2u L=0.06u m=1 nf=2
Mggcv6 vem9ep c28g vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
.ends mu5k
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: uq60
** View name: wxatw
.subckt uq60 vss bt2g vdd r5j7y
Mlhrv3 yt9oyf yt9oyf vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Ma30z bt2g yt9oyf vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mjsw5 r5j7y on5kwo vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Maer2t on5kwo on5kwo vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
.ends uq60
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: uqsz
** View name: wxatw
.subckt uqsz vssq qavq g6wk iyh7t3 vccq
Ml3v5y g6wk qavq vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mf4fl g6wk iyh7t3 vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Me5jr9 g6wk iyh7t3 w81a vssq jil3gy W=2u L=0.2u m=1 nf=1
Mg661vj w81a qavq vssq vssq jil3gy W=2u L=0.2u m=1 nf=1
.ends uqsz
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: mzrz
** View name: wxatw
.subckt mzrz n7dx vdd opsm m5o5 nwa8 sj7n vss
Xwmzi vss sj7n arb6 b8eo2 vdd yavkxw
Xsfvu6d vss b8eo2 opsm n7dx vdd yavkxw
Xkbhcu vss arb6 nwa8 m5o5 vdd yavkxw
.ends mzrz
** End of subcircuit definition.

** Library name: ato68m
** Cell name: z0nj9x
** View name: wxatw
.subckt z0nj9x pvye3<2> g7sku<2> oz24o<1> erhxo<2> vdd a56fy<0> erhxo<1> pvye3<3>
+ g7sku<4> g7sku<1> erhxo<3> oz24o<3> vss gxfh8k<4> a56fy<4> pvye3<0> a56fy<2> oz24o<0>
+ g7sku<0> a56fy<1> oz24o<2> a56fy<3> erhxo<0> oz24o<4> g7sku<3> gxfh8k<1> gxfh8k<2>
+ pvye3<4> pvye3<1> gxfh8k<0> s9yo erhxo<4> gxfh8k<3>
Xaw47a2 vdd s2rg bf6o vss w4yyx
Xqm45n4<2> s2rg vdd erhxo<2> bf6o gxfh8k<2> g7sku<2> vss mzrz
Xqm45n4<0> s2rg vdd erhxo<0> bf6o gxfh8k<0> g7sku<0> vss mzrz
Xxcjkk<2> s2rg vdd a56fy<2> bf6o pvye3<2> oz24o<2> vss mzrz
Xqm45n4<4> s2rg vdd erhxo<4> bf6o gxfh8k<4> g7sku<4> vss mzrz
Xxcjkk<0> s2rg vdd a56fy<0> bf6o pvye3<0> oz24o<0> vss mzrz
Xqm45n4<1> s2rg vdd erhxo<1> bf6o gxfh8k<1> g7sku<1> vss mzrz
Xqm45n4<3> s2rg vdd erhxo<3> bf6o gxfh8k<3> g7sku<3> vss mzrz
Xhz2ea vdd bf6o s9yo vss w4yyx
Xxcjkk<1> s2rg vdd a56fy<1> bf6o pvye3<1> oz24o<1> vss mzrz
Xxcjkk<3> s2rg vdd a56fy<3> bf6o pvye3<3> oz24o<3> vss mzrz
Xxcjkk<4> s2rg vdd a56fy<4> bf6o pvye3<4> oz24o<4> vss mzrz
.ends z0nj9x
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: u0vlr
** View name: wxatw
.subckt u0vlr o8w9v a47gj8 vss xe1z vdd lutju3
Xvdvult vdd lutju3 vss oqyb kfwj
Xqpc4 vss pi5pn8 a47gj8 vdd xe1z yo4ne
Mz3kkw pmvw pi5pn8 vdd vdd vw445g W=0.8u L=0.06u m=1 nf=1
Mnwbui suosok o8w9v vdd vdd vw445g W=0.4u L=0.06u m=1 nf=1
Muvyh0 lutju3 vss ew0r vdd vw445g W=0.4u L=0.06u m=1 nf=1
Mcf343t pi5pn8 o8w9v vdd vdd vw445g W=0.4u L=0.06u m=1 nf=1
Mhr3r1l pi5pn8 pmvw rzc2y vss ns67 W=0.8u L=0.06u m=1 nf=1
Mz8e9s rzc2y oqyb ii01 vss ns67 W=1.6u L=0.06u m=1 nf=2
Mvlky ii01 o8w9v vss vss ns67 W=2u L=0.06u m=1 nf=2
Mhy31g pmvw pi5pn8 suosok vss ns67 W=0.8u L=0.06u m=1 nf=1
Myiee1u pi5pn8 pmvw vdd vdd vw445g W=0.8u L=0.06u m=1 nf=1
Ms2f24 suosok ew0r ii01 vss ns67 W=1.6u L=0.06u m=1 nf=2
Majpvvd rzc2y o8w9v vdd vdd vw445g W=0.4u L=0.06u m=1 nf=1
Xhf9iv0 vss pmvw xe1z vdd a47gj8 yo4ne
Mdzm9 pmvw o8w9v vdd vdd vw445g W=0.4u L=0.06u m=1 nf=1
Mauja lutju3 vdd ew0r vss ns67 W=0.4u L=0.06u m=1 nf=1
.ends u0vlr
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: kwgk
** View name: wxatw
.subckt kwgk n1tu<2> t8wk<2> i8t88i<2> n1tu<1> rj921 n1tu<0> ve2gc<0> vss sjh5s fvqxf<1>
+ vccq fvqxf<0> ve2gc<2> fvqxf<2> vssq t8wk<1> vdd t8wk<0> i8t88i<0> ve2gc<1> i8la
+ i8t88i<1>
Xpt7eg vss vdd vssq e7hf38 vccq wurv gmbd2x sprh
Xmpj5<2> oqpq6<2> vssq fvqxf<2> vccq cathu m=4
Xmrkirk<2> vss vdd vssq n1tu<2> vccq okrg<2> htfc<2> sprh
Xb8gtc uch9 vss sjh5s figew vdd wxlvj5
Xnzf7zh<2> o3zhc<2> vssq ve2gc<2> vccq cathu m=4
Xnzf7zh<1> o3zhc<1> vssq ve2gc<1> vccq cathu m=4
Xber4jk<0> o3zhc<0> vssq vqr5l<0> vccq cathu
Xber4jk<1> o3zhc<1> vssq vqr5l<1> vccq cathu
Xxnaw<1> n81jl<1> vssq t8wk<1> vccq cathu m=4
Xajvm9<0> vqr5l<0> vssq i8t88i<0> vccq cathu m=4
Xgq95p<1> oqpq6<1> vssq n81jl<1> vccq cathu
Xxnaw<0> n81jl<0> vssq t8wk<0> vccq cathu m=4
Xu8p5o<0> vssq gmbd2x oqpq6<0> htfc<0> vccq uqsz
Xnzf7zh<0> o3zhc<0> vssq ve2gc<0> vccq cathu m=4
Xza767 figew vdd vss rj921 l5tu7
Xgk5nz<2> vssq f8urs o3zhc<2> htfc<2> vccq uqsz
Xajvm9<2> vqr5l<2> vssq i8t88i<2> vccq cathu m=4
Xgk5nz<1> vssq f8urs o3zhc<1> htfc<1> vccq uqsz
Xajvm9<1> vqr5l<1> vssq i8t88i<1> vccq cathu m=4
Xmrkirk<0> vss vdd vssq n1tu<0> vccq okrg<0> htfc<0> sprh
Xgq95p<0> oqpq6<0> vssq n81jl<0> vccq cathu
Xxnaw<2> n81jl<2> vssq t8wk<2> vccq cathu m=4
Xber4jk<2> o3zhc<2> vssq vqr5l<2> vccq cathu
Xw8blig e7hf38 vss i8la figew vdd wxlvj5
Xmpj5<1> oqpq6<1> vssq fvqxf<1> vccq cathu m=4
Xgk5nz<0> vssq f8urs o3zhc<0> htfc<0> vccq uqsz
Xwvh1e vss vdd vssq uch9 vccq i2e2 f8urs sprh
Xu8p5o<1> vssq gmbd2x oqpq6<1> htfc<1> vccq uqsz
Xmpj5<0> oqpq6<0> vssq fvqxf<0> vccq cathu m=4
Xmrkirk<1> vss vdd vssq n1tu<1> vccq okrg<1> htfc<1> sprh
Xgq95p<2> oqpq6<2> vssq n81jl<2> vccq cathu
Xu8p5o<2> vssq gmbd2x oqpq6<2> htfc<2> vccq uqsz
.ends kwgk
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: vui2
** View name: wxatw
.subckt vui2 nuje vdd j1agx4 aqhzb8 vss dtkw ok1s8r
Mj217 l77xw nuje mq5wc vss ka1ebp W=4u L=0.2u m=1 nf=4
Mbf7v2 mq5wc dtkw vss vss ka1ebp W=2u L=0.1u m=1 nf=2
Mky92 wt2p i82z chgef vss ka1ebp W=0.8u L=0.06u m=1 nf=1
Xh0w4 vss aqhzb8 wt2p j1agx4 vdd yavkxw
Mz9bgq9 chgef dtkw vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mwe9p wt2p i82z vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Xt5bitv vss j1agx4 i82z aqhzb8 vdd yavkxw
Mh60d wt2p dtkw vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mn41zpm l77xw dtkw vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mpctvyj i82z wt2p l77xw vss ka1ebp W=0.8u L=0.06u m=1 nf=1
Myqa1r i82z dtkw vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mgpswqz chgef ok1s8r mq5wc vss ka1ebp W=4u L=0.2u m=1 nf=4
Mb4ek i82z wt2p vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
.ends vui2
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: wxlvj5
** View name: wxatw
.subckt wxlvj5 ivw5 vss yj5sd dt9b vdd
Mbt9kan ut7or dt9b vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mpekes ivw5 yj5sd vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mlhrp ivw5 yj5sd ut7or vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mooslpk ivw5 dt9b vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
.ends wxlvj5
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: ryk2
** View name: wxatw
.subckt ryk2 lzeog<1> lzeog<2> htzjl<0> vccq htzjl<1> jo1e5g lzeog<0> htzjl<2> vssq
Mspzmg m4ir<2> htzjl<2> vccq vccq ycgzf W=2u L=0.2u m=4 nf=1
Rgm9m9w m4ir<1> jo1e5g 240
Mqmpsi m4ir<1> htzjl<1> vccq vccq ycgzf W=2u L=0.2u m=2 nf=1
Rp7ixje eejsx<1> jo1e5g 240
Rv3wvt eejsx<2> jo1e5g 120
Mwkf5 eejsx<0> lzeog<0> vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mbf471 eejsx<1> lzeog<1> vssq vssq jil3gy W=1u L=0.2u m=2 nf=1
Rz9j82q m4ir<0> jo1e5g 480
Rv95t eejsx<0> jo1e5g 480
Mucxf5d m4ir<0> htzjl<0> vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mf8a4vs eejsx<2> lzeog<2> vssq vssq jil3gy W=1u L=0.2u m=4 nf=1
Rzj8sy m4ir<2> jo1e5g 120
.ends ryk2
** End of subcircuit definition.

** Library name: ato68m
** Cell name: ewiu3i
** View name: wxatw
.subckt ewiu3i corbyn g85ca vccq z4yfga vssq
Rvihh h8143 g85ca 300
Rsyrz kbkg4 g85ca 300
Msmp5q2 kbkg4 z4yfga vssq vssq jil3gy W=4u L=0.2u m=1 nf=2
Mju5rvq h8143 corbyn vccq vccq ycgzf W=8u L=0.2u m=1 nf=4
.ends ewiu3i
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: a44p
** View name: wxatw
.subckt a44p horj<0> gcyl horj<1> yh2uhk vssq sj8uy horj<4> horj<3> vccq vdd n1tzk
+ horj<2> hmdp vss
Ri9di pa6c<0> vssq 14.5k
Rw31p<12> pa6c<13> pa6c<12> 500
Rw31p<20> pa6c<21> pa6c<20> 500
Mf0ow vssq sj8uy vssq vssq jil3gy W=10u L=2u m=4 nf=1
Rw31p<2> pa6c<3> pa6c<2> 500
Xdi59j<4> vss vdd vssq horj<4> vccq qqn0<4> grt0<4> sprh
Rw31p<7> pa6c<8> pa6c<7> 500
Rw31p<29> pa6c<30> pa6c<29> 500
Rw31p<18> pa6c<19> pa6c<18> 500
Rw31p<16> pa6c<17> pa6c<16> 500
Rw31p<19> pa6c<20> pa6c<19> 500
Rw31p<10> pa6c<11> pa6c<10> 500
Rw31p<4> pa6c<5> pa6c<4> 500
Rw31p<15> pa6c<16> pa6c<15> 500
Ron77 lvogd pa6c<31> 12k
Xtkxo3p d26i aejl n1tzk vssq yh2uhk vccq aejl hmdp fgjco
Rw31p<9> pa6c<10> pa6c<9> 500
Rw31p<5> pa6c<6> pa6c<5> 500
Rw31p<23> pa6c<24> pa6c<23> 500
Rw31p<30> pa6c<31> pa6c<30> 500
Xdi59j<1> vss vdd vssq horj<1> vccq qqn0<1> grt0<1> sprh
Rw31p<25> pa6c<26> pa6c<25> 500
Mn5yvw lvogd hmdp vccq vccq ycgzf W=4u L=0.2u m=1 nf=2
Rw31p<28> pa6c<29> pa6c<28> 500
Rw31p<24> pa6c<25> pa6c<24> 500
Cbg9z sj8uy vssq 2p
Xdi59j<0> vss vdd vssq horj<0> vccq qqn0<0> grt0<0> sprh
Rw31p<1> pa6c<2> pa6c<1> 500
Xdi59j<2> vss vdd vssq horj<2> vccq qqn0<2> grt0<2> sprh
Xlayjel pa6c<19> pa6c<11> pa6c<8> d26i qqn0<4> grt0<2> pa6c<1> pa6c<5> pa6c<14> pa6c<17>
+ vccq pa6c<12> pa6c<0> pa6c<24> grt0<4> vssq pa6c<18> pa6c<15> pa6c<22> pa6c<6> qqn0<2>
+ pa6c<20> pa6c<31> pa6c<7> pa6c<10> pa6c<16> pa6c<3> pa6c<9> pa6c<27> pa6c<2> qqn0<3>
+ qqn0<0> pa6c<28> pa6c<26> pa6c<23> pa6c<21> pa6c<4> grt0<3> pa6c<13> qqn0<1> grt0<1>
+ pa6c<29> grt0<0> pa6c<25> pa6c<30> vv7jcn
Rw31p<22> pa6c<23> pa6c<22> 500
Rw31p<13> pa6c<14> pa6c<13> 500
Rw31p<0> pa6c<1> pa6c<0> 500
Rw31p<21> pa6c<22> pa6c<21> 500
Xdi59j<3> vss vdd vssq horj<3> vccq qqn0<3> grt0<3> sprh
Rw31p<26> pa6c<27> pa6c<26> 500
Rw31p<6> pa6c<7> pa6c<6> 500
Xnrq6jn gcyl aejl sj8uy hmdp n1tzk vccq vssq ptto
Rw31p<8> pa6c<9> pa6c<8> 500
Rw31p<27> pa6c<28> pa6c<27> 500
Rw31p<3> pa6c<4> pa6c<3> 500
Rw31p<17> pa6c<18> pa6c<17> 500
Rw31p<11> pa6c<12> pa6c<11> 500
Rw31p<14> pa6c<15> pa6c<14> 500
.ends a44p
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: jw9qyf
** View name: wxatw
.subckt jw9qyf aoqpe<3> p2wx<1> ppp9<4> aoqpe<4> ppp9<1> vssq p2wx<3> aoqpe<1> vss vccq
+ p2wx<4> ppp9<2> p2wx<0> aoqpe<2> ppp9<3> p2wx<2> sso1 aoqpe<0> ppp9<0> vdd
Xnm9a9l<3> vss vdd vssq p2wx<3> vccq l2kk<3> nzkv<3> sprh
Xc0kx7<4> aoqpe<4> vssq ppp9<4> vccq cathu
Xm6tdah<3> vssq sso1 aoqpe<3> nzkv<3> vccq uqsz
Xc0kx7<0> aoqpe<0> vssq ppp9<0> vccq cathu
Xc0kx7<3> aoqpe<3> vssq ppp9<3> vccq cathu
Xnm9a9l<4> vss vdd vssq p2wx<4> vccq l2kk<4> nzkv<4> sprh
Xm6tdah<4> vssq sso1 aoqpe<4> nzkv<4> vccq uqsz
Xm6tdah<0> vssq sso1 aoqpe<0> nzkv<0> vccq uqsz
Xm6tdah<2> vssq sso1 aoqpe<2> nzkv<2> vccq uqsz
Xnm9a9l<2> vss vdd vssq p2wx<2> vccq l2kk<2> nzkv<2> sprh
Xnm9a9l<1> vss vdd vssq p2wx<1> vccq l2kk<1> nzkv<1> sprh
Xm6tdah<1> vssq sso1 aoqpe<1> nzkv<1> vccq uqsz
Xc0kx7<1> aoqpe<1> vssq ppp9<1> vccq cathu
Xc0kx7<2> aoqpe<2> vssq ppp9<2> vccq cathu
Xnm9a9l<0> vss vdd vssq p2wx<0> vccq l2kk<0> nzkv<0> sprh
.ends jw9qyf
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: d9b5zl
** View name: wxatw
.subckt d9b5zl h2mq0 ehcrkj vss r5ly vdd
Mdxao gi2xp h2mq0 vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mz4qc r5ly jsk8t2 gi2xp vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mnqiiq8 gi2xp ehcrkj vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Ms9ks lypj h2mq0 vss vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mbp5t vve2n ehcrkj vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mbj1c7u jsk8t2 h2mq0 vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mw0w1nq r5ly ehcrkj lypj vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mj1ieg4 r5ly vve2n gi2xp vdd ad57k3 W=0.8u L=0.06u m=1 nf=1
Mowoq2 jsk8t2 h2mq0 vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mhy35 vve2n ehcrkj vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mczu9 r5ly vve2n k4iyy vss ka1ebp W=0.4u L=0.06u m=1 nf=1
Mvy9431 k4iyy jsk8t2 vss vss ka1ebp W=0.4u L=0.06u m=1 nf=1
.ends d9b5zl
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: wggy
** View name: wxatw
.subckt wggy vss zf3r<8> zf3r<2> zf3r<6> zf3r<7> zf3r<5> zf3r<4> ekxus zf3r<3> zf3r<1>
+ vdd zf3r<0>
Xcj63v<8> vss zf3r<8> lt3d<2> vdd yydl
Xcj63v<5> vss zf3r<5> lt3d<1> vdd yydl
Cfwmc zf3r<2> vss 5f
Xcj63v<6> vss zf3r<6> lt3d<2> vdd yydl
Xyaeycy vss h70hkm ekxus vdd yydl
Xrt3sdz<2> vss lt3d<2> h70hkm vdd yydl
Cowac3i lt3d<2> vss 8f
Xcj63v<0> vss zf3r<0> lt3d<0> vdd yydl
Xcj63v<7> vss zf3r<7> lt3d<2> vdd yydl
Cvlhjx zf3r<8> vss 5f
Cxecaym zf3r<1> vss 5f
Cyiskqr lt3d<0> vss 8f
Cz3u9 zf3r<4> vss 5f
Xrt3sdz<1> vss lt3d<1> h70hkm vdd yydl
Cfzwam zf3r<3> vss 5f
Xrt3sdz<0> vss lt3d<0> h70hkm vdd yydl
Cixzl zf3r<7> vss 5f
Xcj63v<1> vss zf3r<1> lt3d<0> vdd yydl
Cxcgfqw zf3r<5> vss 5f
Xcj63v<4> vss zf3r<4> lt3d<1> vdd yydl
Xcj63v<2> vss zf3r<2> lt3d<0> vdd yydl
Chf7vg zf3r<0> vss 5f
Ciftu zf3r<6> vss 5f
Cbeea h70hkm vss 12f
Xcj63v<3> vss zf3r<3> lt3d<1> vdd yydl
Crjg1lr lt3d<1> vss 8f
.ends wggy
** End of subcircuit definition.

** Library name: ato68m
** Cell name: f8zz
** View name: wxatw
.subckt f8zz vssq vm8mz<1> vm8mz<4> tejk<0> tejk<3> vccq tejk<4> vm8mz<3> vm8mz<0> fegzn
+ tejk<2> tejk<1> vm8mz<2>
Xtln1c vm8mz<4> fegzn vccq tejk<4> vssq ewiu3i m=16
Xsim8kt vm8mz<2> fegzn vccq tejk<2> vssq ewiu3i m=4
Xqy9f2 vm8mz<1> fegzn vccq tejk<1> vssq ewiu3i m=2
Xwcfz8 vm8mz<0> fegzn vccq tejk<0> vssq ewiu3i m=1
Xog257k vm8mz<3> fegzn vccq tejk<3> vssq ewiu3i m=8
.ends f8zz
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: mlg3h7
** View name: wxatw
.subckt mlg3h7 smp7x ia95r9<3> ia95r9<4> ia95r9<2> vss wmrv t84nq weqh8 xnec38 ia95r9<1>
+ ia95r9<0> vdd
Xfuedi<4> x8qi1<4> vss xnec38 vdd weqh8 taot5e<4> taot5e<5> zuhc6m
Xfuedi<0> x8qi1<0> vss xnec38 vdd weqh8 taot5e<0> taot5e<1> zuhc6m
Xu9ilaq<3> vss vtyk<3> ia95r9<3> meqzo<3> vdd yavkxw
Xu9ilaq<2> vss vtyk<2> ia95r9<2> meqzo<2> vdd yavkxw
Xftcjbc<4> cle72<4> vtyk<4> vss u1h2<4> yhueki<4> vdd p7glz
Xvh92<3> u1h2<3> vdd vss taot5e<4> l5tu7
Xyhcl<3> taot5e<4> taot5e<5> meqzo<3> vdd taot5e<3> vss mu5k
Xfuedi<2> x8qi1<2> vss xnec38 vdd weqh8 taot5e<2> taot5e<3> zuhc6m
Xftcjbc<2> cle72<2> vtyk<2> vss u1h2<2> yhueki<2> vdd p7glz
Xtc75p<0> vss cle72<0> taot5e<0> jju5 vdd yavkxw
Xu9ilaq<0> vss vtyk<0> ia95r9<0> meqzo<0> vdd yavkxw
Xtc75p<4> vss cle72<4> taot5e<4> jju5 vdd yavkxw
Xvh92<4> u1h2<4> vdd vss taot5e<5> l5tu7
Xyhcl<1> taot5e<2> taot5e<5> meqzo<1> vdd taot5e<1> vss mu5k
Xmq9v0 jju5 vdd vss wmrv l5tu7
Xyhcl<4> taot5e<5> taot5e<5> meqzo<4> vdd taot5e<4> vss mu5k
Xftcjbc<3> cle72<3> vtyk<3> vss u1h2<3> yhueki<3> vdd p7glz
Xftcjbc<1> cle72<1> vtyk<1> vss u1h2<1> yhueki<1> vdd p7glz
Xu9ilaq<4> vss vtyk<4> ia95r9<4> meqzo<4> vdd yavkxw
Xfuedi<1> x8qi1<1> vss xnec38 vdd weqh8 taot5e<1> taot5e<2> zuhc6m
Xxwav<1> kie1<1> vss xnec38 vdd weqh8 ia95r9<1> yhueki<1> zuhc6m
Xtc75p<1> vss cle72<1> taot5e<1> jju5 vdd yavkxw
Xftcjbc<0> cle72<0> vtyk<0> vss u1h2<0> yhueki<0> vdd p7glz
Xamjl vss cjexx pc3z o0u4s vdd yavkxw
Xm4v3 o0u4s vdd vss taot5e<0> l5tu7
Xyhcl<2> taot5e<3> taot5e<5> meqzo<2> vdd taot5e<2> vss mu5k
Xtyl6yi vss pc3z t84nq u1h2<4> vdd yavkxw
Xtc75p<2> vss cle72<2> taot5e<2> jju5 vdd yavkxw
Xtc75p<3> vss cle72<3> taot5e<3> jju5 vdd yavkxw
Xvh92<1> u1h2<1> vdd vss taot5e<2> l5tu7
Xxwav<4> kie1<4> vss xnec38 vdd weqh8 ia95r9<4> yhueki<4> zuhc6m
Xvh92<2> u1h2<2> vdd vss taot5e<3> l5tu7
Xyhcl<0> taot5e<1> taot5e<5> meqzo<0> vdd taot5e<0> vss mu5k
Xfuedi<3> x8qi1<3> vss xnec38 vdd weqh8 taot5e<3> taot5e<4> zuhc6m
Xl3q0k6 xek4 vss xnec38 vdd weqh8 t84nq cjexx zuhc6m
Xvh92<0> u1h2<0> vdd vss taot5e<1> l5tu7
Xxwav<2> kie1<2> vss xnec38 vdd weqh8 ia95r9<2> yhueki<2> zuhc6m
Xxwav<3> kie1<3> vss xnec38 vdd weqh8 ia95r9<3> yhueki<3> zuhc6m
Xu9ilaq<1> vss vtyk<1> ia95r9<1> meqzo<1> vdd yavkxw
Xxwav<0> kie1<0> vss xnec38 vdd weqh8 ia95r9<0> yhueki<0> zuhc6m
Xfuedi<5> x8qi1<5> vss xnec38 vdd weqh8 taot5e<5> smp7x zuhc6m
.ends mlg3h7
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: sprh
** View name: wxatw
.subckt sprh vss vdd vssq ya3zs vccq p67ma vd4xb
Mukwx cwhtb7 jd21v vccq vccq ycgzf W=0.5u L=0.2u m=1 nf=1
Mrjduv gz98 ya3zs vss vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Mjk8zc p67ma vd4xb vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mcuvs22 p67ma vd4xb vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mug6q jd21v cwhtb7 vccq vccq ycgzf W=0.5u L=0.2u m=1 nf=1
Mj8q1 vd4xb cwhtb7 vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mb6xra vd4xb cwhtb7 vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mn1oiue jd21v gz98 vssq vssq jil3gy W=2u L=0.2u m=1 nf=1
Mqctq cwhtb7 ya3zs vssq vssq jil3gy W=2u L=0.2u m=1 nf=1
Mkro221 gz98 ya3zs vdd vdd ad57k3 W=0.6u L=0.06u m=1 nf=1
.ends sprh
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: ptto
** View name: wxatw
.subckt ptto axz6m g94lcx h5q1 e5ms o83wq vccq vssq
Mb9x7x axz6m e5ms h5q1 vssq jil3gy W=1u L=0.2u m=1 nf=1
Mjnj7hl axz6m o83wq h5q1 vccq ycgzf W=2u L=0.2u m=1 nf=1
Me7chj g94lcx e5ms h5q1 vccq ycgzf W=2u L=0.2u m=1 nf=1
Mirgz g94lcx o83wq h5q1 vssq jil3gy W=1u L=0.2u m=1 nf=1
.ends ptto
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: vwt2x6
** View name: wxatw
.subckt vwt2x6 ebqty<1> ici43i vccq vss orzf<4> ebqty<0> orzf<0> jxzrv ebqty<2> al9b
+ ebqty<4> lwz7yh jitjma wqqd4l orzf<3> orzf<1> orzf<2> weve ebqty<3> vssq vdd
Xu01k5 t0t3w5 vdd vss y433b l5tu7
Xxhfc vccq ikiq<1> j4tbt<4> j4tbt<0> j4tbt<2> ikiq<3> ikiq<2> vssq j4tbt<1> ikiq<4> v79w
+ ikiq<0> j4tbt<3> jrilr9
Xzbhho vss vdd vssq weve vccq xhhhbx iu5i sprh
Xx8k9i ikiq<3> orzf<1> r19gn<4> ikiq<4> r19gn<1> vssq orzf<3> ikiq<1> vss vccq orzf<4>
+ r19gn<2> orzf<0> ikiq<2> r19gn<3> orzf<2> iu5i ikiq<0> r19gn<0> vdd jw9qyf
Xgeyt xydzi<3> ebqty<1> j4tbt<4> xydzi<4> j4tbt<1> vssq ebqty<3> xydzi<1> vss vccq
+ ebqty<4> j4tbt<2> ebqty<0> xydzi<2> j4tbt<3> ebqty<2> iu5i xydzi<0> j4tbt<0> vdd
+ jw9qyf
Xomko8g vss y433b weve wqqd4l vdd yavkxw
Xagfy vccq xhhhbx jp74k vssq z78y9
Xujit ikiq<0> ikiq<4> ikiq<2> lwz7yh vccq ikiq<1> ikiq<3> vmswp
Xeq82m jitjma orzf<3> orzf<4> orzf<2> vss sfqi wqqd4l al9b jxzrv orzf<1> orzf<0> vdd
+ mlg3h7
Xljla jxzrv kuda4 ebqty<2> al9b ebqty<3> ebqty<0> vss t0t3w5 vdd vss ebqty<4> ebqty<1>
+ fn5wjn
Xs9tjaq vss v79w ici43i jp74k vssq kuda4 xhhhbx vccq vdd zhq5
Mjqc0jq ici43i ici43i vccq vccq ycgzf W=2u L=1u m=1 nf=1
Xlly87 vss lwz7yh ici43i jp74k vssq sfqi xhhhbx vccq vdd zhq5
.ends vwt2x6
** End of subcircuit definition.

** Library name: ato68m
** Cell name: gugmik
** View name: wxatw
.subckt gugmik ga5p<1> w13km<4> a3wl<3> wsx8n<2> wsx8n<4> d63tq<3> pmv9 zkl7 b1qd<0>
+ f74rbw prz11 d63tq<1> vccq wsx8n<3> w13km<1> c204 w13km<0> d63tq<2> eiu8s u68ig
+ a3wl<2> a3wl<4> w13km<3> a3wl<1> b1qd<3> ga5p<2> ga5p<3> ga5p<0> d63tq<4> b1qd<4> vdd
+ yqhbir ga5p<4> a3wl<0> wsx8n<1> vssq wy8qmy b1qd<2> vss b1qd<1> fa6b5 c5iy w13km<2>
+ wsx8n<0> j4u4x memc d63tq<0>
Xqqan<2> ofna8o<2> vssq b1qd<2> vccq cathu
Xqqan<4> ofna8o<4> vssq b1qd<4> vccq cathu
Xq0ugo<3> vssq cyu5j uasqwt<3> kntskg<3> vccq uqsz
Xd21q vdd u68ig jut9f vss w4yyx
Xz9bhmy<3> vssq oi4cv ofna8o<3> kntskg<3> vccq uqsz
Xyv497e<3> vss vdd vssq ga5p<3> vccq xn2l<3> kntskg<3> sprh
Xllrmss jut9f vdd vss pmv9 l5tu7
Xyv497e<1> vss vdd vssq ga5p<1> vccq xn2l<1> kntskg<1> sprh
Xyv497e<0> vss vdd vssq ga5p<0> vccq xn2l<0> kntskg<0> sprh
Xcu3l<4> uasqwt<4> vssq a3wl<4> vccq cathu
Xqz20h9<3> vssq cyu5j d63tq<3> r9fn<3> vccq uqsz
Xg1rvv vss c5iy vdd wy8qmy uq60
Xqfhwtj<3> vssq oi4cv w13km<3> r9fn<3> vccq uqsz
Xv5lm5m vss vdd vssq eiu8s vccq cfn15 oi4cv sprh
Xyv497e<4> vss vdd vssq ga5p<4> vccq xn2l<4> kntskg<4> sprh
Xcu3l<0> uasqwt<0> vssq a3wl<0> vccq cathu
Xqfhwtj<2> vssq oi4cv w13km<2> r9fn<2> vccq uqsz
Xyx9odm vss vdd vssq j4u4x vccq memc f74rbw sprh
Xge434b vss vdd vssq c204 vccq yqhbir fa6b5 sprh
Xz9bhmy<0> vssq oi4cv ofna8o<0> kntskg<0> vccq uqsz
Xqz20h9<2> vssq cyu5j d63tq<2> r9fn<2> vccq uqsz
Xcu3l<1> uasqwt<1> vssq a3wl<1> vccq cathu
Xq0ugo<2> vssq cyu5j uasqwt<2> kntskg<2> vccq uqsz
Xa9zgh vdd prz11 u68ig vss w4yyx
Xq0ugo<0> vssq cyu5j uasqwt<0> kntskg<0> vccq uqsz
Xswgz9m vss vdd vssq zkl7 vccq oq0e5 cyu5j sprh
Xqfhwtj<1> vssq oi4cv w13km<1> r9fn<1> vccq uqsz
Xqz20h9<0> vssq cyu5j d63tq<0> r9fn<0> vccq uqsz
Xkoiw80<1> vss vdd vssq wsx8n<1> vccq kz82m<1> r9fn<1> sprh
Xyv497e<2> vss vdd vssq ga5p<2> vccq xn2l<2> kntskg<2> sprh
Xkoiw80<0> vss vdd vssq wsx8n<0> vccq kz82m<0> r9fn<0> sprh
Xkoiw80<3> vss vdd vssq wsx8n<3> vccq kz82m<3> r9fn<3> sprh
Xq0ugo<1> vssq cyu5j uasqwt<1> kntskg<1> vccq uqsz
Xcu3l<3> uasqwt<3> vssq a3wl<3> vccq cathu
Xqqan<3> ofna8o<3> vssq b1qd<3> vccq cathu
Xz9bhmy<4> vssq oi4cv ofna8o<4> kntskg<4> vccq uqsz
Xz9bhmy<1> vssq oi4cv ofna8o<1> kntskg<1> vccq uqsz
Xqqan<1> ofna8o<1> vssq b1qd<1> vccq cathu
Xkoiw80<4> vss vdd vssq wsx8n<4> vccq kz82m<4> r9fn<4> sprh
Xqz20h9<4> vssq cyu5j d63tq<4> r9fn<4> vccq uqsz
Xqfhwtj<4> vssq oi4cv w13km<4> r9fn<4> vccq uqsz
Xqz20h9<1> vssq cyu5j d63tq<1> r9fn<1> vccq uqsz
Xq0ugo<4> vssq cyu5j uasqwt<4> kntskg<4> vccq uqsz
Xz9bhmy<2> vssq oi4cv ofna8o<2> kntskg<2> vccq uqsz
Xkoiw80<2> vss vdd vssq wsx8n<2> vccq kz82m<2> r9fn<2> sprh
Xcu3l<2> uasqwt<2> vssq a3wl<2> vccq cathu
Xqfhwtj<0> vssq oi4cv w13km<0> r9fn<0> vccq uqsz
Xqqan<0> ofna8o<0> vssq b1qd<0> vccq cathu
.ends gugmik
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: z1nko
** View name: wxatw
.subckt z1nko vss vdd rmpjk i0d54c z2xp hheuw ekzl8
Meujs g2s74 zp66m ynkq vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Xh5aso lelk8 vdd vss rmpjk l5tu7
Mh6a1 hheuw zz3s28 ynkq vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mcmr2 p9y8w zz3s28 zd7cw vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Xxaoy42 i0d54c vdd vss z2xp l5tu7
Mpjn9 hheuw zp66m ynkq vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Xjoq7p zp66m vdd vss ekzl8 l5tu7
Xoa08y vss z2xp zd7cw rmpjk vdd yavkxw
Mb7v4we wf28 zz3s28 zd7cw vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Mz510a p9y8w zp66m zd7cw vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Xh24xp wf28 vdd vss z2xp l5tu7
Xwxd819 p9y8w vss lelk8 ynkq vdd wxlvj5
Mf3slrb g2s74 zz3s28 ynkq vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mpq8j wf28 zp66m zd7cw vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Xhudj zz3s28 vdd vss zp66m l5tu7
Xap3l2 g2s74 vdd vss p9y8w l5tu7
.ends z1nko
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: ax7dv
** View name: wxatw
.subckt ax7dv vdd y39jdi<0> y39jdi<5> y39jdi<2> y39jdi<7> y39jdi<6> y39jdi<8> xyx5vk
+ y39jdi<4> vss y39jdi<3> y39jdi<1>
Xqlyzt2<4> vdd vss y39jdi<4> ygrb1y<4> q8t9
Xqlyzt2<6> vdd vss y39jdi<6> ygrb1y<6> q8t9
Xsj7179<5> ygrb1y<6> vss y39jdi<5> yqsu
Xsj7179<2> ygrb1y<3> vss y39jdi<2> yqsu
Xqlyzt2<3> vdd vss y39jdi<3> ygrb1y<3> q8t9
Xqlyzt2<2> vdd vss y39jdi<2> ygrb1y<2> q8t9
Xqlyzt2<7> vdd vss y39jdi<7> ygrb1y<7> q8t9
Xsj7179<0> ygrb1y<1> vss y39jdi<0> yqsu
Xsj7179<6> ygrb1y<7> vss y39jdi<6> yqsu
Xqlyzt2<8> vdd vss y39jdi<8> ygrb1y<8> q8t9
Xqlyzt2<0> vdd vss y39jdi<0> xyx5vk q8t9
Xsj7179<7> ygrb1y<8> vss y39jdi<7> yqsu
Xsj7179<3> ygrb1y<4> vss y39jdi<3> yqsu
Xsj7179<4> ygrb1y<5> vss y39jdi<4> yqsu
Xsj7179<1> ygrb1y<2> vss y39jdi<1> yqsu
Xqlyzt2<1> vdd vss y39jdi<1> ygrb1y<1> q8t9
Xqlyzt2<5> vdd vss y39jdi<5> ygrb1y<5> q8t9
.ends ax7dv
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: vv7jcn
** View name: wxatw
.subckt vv7jcn no0rjq<19> no0rjq<11> no0rjq<8> bebidw l4lpzy<4> h9j9qr<2> no0rjq<1>
+ no0rjq<5> no0rjq<14> no0rjq<17> vccq no0rjq<12> no0rjq<0> no0rjq<24> h9j9qr<4> vssq
+ no0rjq<18> no0rjq<15> no0rjq<22> no0rjq<6> l4lpzy<2> no0rjq<20> no0rjq<31> no0rjq<7>
+ no0rjq<10> no0rjq<16> no0rjq<3> no0rjq<9> no0rjq<27> no0rjq<2> l4lpzy<3> l4lpzy<0>
+ no0rjq<28> no0rjq<26> no0rjq<23> no0rjq<21> no0rjq<4> h9j9qr<3> no0rjq<13> l4lpzy<1>
+ h9j9qr<1> no0rjq<29> h9j9qr<0> no0rjq<25> no0rjq<30>
Xafttpq sqn5av<0> sqn5av<1> bebidw l4lpzy<4> h9j9qr<4> vccq vssq ptto
Xr547<0> tbt0<0> tbt0<1> jts48<0> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xr547<3> tbt0<6> tbt0<7> jts48<3> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<1> no0rjq<2> no0rjq<3> tbt0<1> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<8> no0rjq<16> no0rjq<17> tbt0<8> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<9> no0rjq<18> no0rjq<19> tbt0<9> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xr547<7> tbt0<14> tbt0<15> jts48<7> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<14> no0rjq<28> no0rjq<29> tbt0<14> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xr547<6> tbt0<12> tbt0<13> jts48<6> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xr547<2> tbt0<4> tbt0<5> jts48<2> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<13> no0rjq<26> no0rjq<27> tbt0<13> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xr547<1> tbt0<2> tbt0<3> jts48<1> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<2> no0rjq<4> no0rjq<5> tbt0<2> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<6> no0rjq<12> no0rjq<13> tbt0<6> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<7> no0rjq<14> no0rjq<15> tbt0<7> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<15> no0rjq<30> no0rjq<31> tbt0<15> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<3> no0rjq<6> no0rjq<7> tbt0<3> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xwe6i<3> jts48<6> jts48<7> yetp2<3> l4lpzy<2> h9j9qr<2> vccq vssq ptto
Xd6u2yj<0> yetp2<0> yetp2<1> sqn5av<0> l4lpzy<3> h9j9qr<3> vccq vssq ptto
Xfv3d4<4> no0rjq<8> no0rjq<9> tbt0<4> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xwe6i<0> jts48<0> jts48<1> yetp2<0> l4lpzy<2> h9j9qr<2> vccq vssq ptto
Xwe6i<1> jts48<2> jts48<3> yetp2<1> l4lpzy<2> h9j9qr<2> vccq vssq ptto
Xwe6i<2> jts48<4> jts48<5> yetp2<2> l4lpzy<2> h9j9qr<2> vccq vssq ptto
Xfv3d4<10> no0rjq<20> no0rjq<21> tbt0<10> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xr547<5> tbt0<10> tbt0<11> jts48<5> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<0> no0rjq<0> no0rjq<1> tbt0<0> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xfv3d4<11> no0rjq<22> no0rjq<23> tbt0<11> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xr547<4> tbt0<8> tbt0<9> jts48<4> l4lpzy<1> h9j9qr<1> vccq vssq ptto
Xfv3d4<12> no0rjq<24> no0rjq<25> tbt0<12> l4lpzy<0> h9j9qr<0> vccq vssq ptto
Xd6u2yj<1> yetp2<2> yetp2<3> sqn5av<1> l4lpzy<3> h9j9qr<3> vccq vssq ptto
Xfv3d4<5> no0rjq<10> no0rjq<11> tbt0<5> l4lpzy<0> h9j9qr<0> vccq vssq ptto
.ends vv7jcn
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: l5tu7
** View name: wxatw
.subckt l5tu7 rsu1kh vdd vss dgta
Ma3le20 rsu1kh dgta vss vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mf0r8q rsu1kh dgta vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
.ends l5tu7
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: vmswp
** View name: wxatw
.subckt vmswp uvvoh<0> uvvoh<4> uvvoh<2> trqhu vccq uvvoh<1> uvvoh<3>
Ryqkjl l8klk<3> trqhu 300
Mhc3i l8klk<3> uvvoh<3> vccq vccq ycgzf W=1u L=0.2u m=8 nf=1
Ra7e2jd l8klk<2> trqhu 600
Mw90j4s l8klk<2> uvvoh<2> vccq vccq ycgzf W=1u L=0.2u m=4 nf=1
Rk32k7 l8klk<1> trqhu 1.2k
Rijtr l8klk<4> trqhu 150
Msvq28 l8klk<1> uvvoh<1> vccq vccq ycgzf W=1u L=0.2u m=2 nf=1
Mbpwel2 l8klk<0> uvvoh<0> vccq vccq ycgzf W=1u L=0.2u m=1 nf=1
Maiu11n l8klk<4> uvvoh<4> vccq vccq ycgzf W=1u L=0.2u m=16 nf=1
Rpo0v2z l8klk<0> trqhu 2.4k
.ends vmswp
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: w4yyx
** View name: wxatw
.subckt w4yyx vdd j0tii8 skjz vss
Mhract6 j0tii8 skjz vss vss ka1ebp W=0.4u L=0.06u m=1 nf=2
Mi2hy3t j0tii8 skjz vdd vdd ad57k3 W=0.8u L=0.06u m=1 nf=2
.ends w4yyx
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: zhq5
** View name: wxatw
.subckt zhq5 vss nj6dtl hgvv beay8 vssq kdzjl0 xo1a vccq vdd
Xldtd vdd vssq vss vccq kdzjl0 kavl2r zmf6
Mq8ejwv c3idw xo1a vccq vccq ycgzf W=4u L=0.2u m=1 nf=1
Meti8ar aia002 hgvv c3idw vccq ycgzf W=4u L=1u m=2 nf=1
Mvt0k1 h7a0 beay8 aia002 vccq ycgzf W=4u L=0.5u m=2 nf=1
Mfb7m7 h7a0 h7a0 vssq vssq jil3gy W=2u L=0.5u m=1 nf=1
Mzf62b rwoz1i nj6dtl aia002 vccq ycgzf W=4u L=0.5u m=2 nf=1
Mpje9 kavl2r rwoz1i vssq vssq jil3gy W=2u L=0.3u m=1 nf=1
Mgqnkx4 kavl2r hgvv vccq vccq ycgzf W=2u L=1u m=1 nf=1
Mesxn rwoz1i h7a0 vssq vssq jil3gy W=2u L=0.5u m=1 nf=1
.ends zhq5
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: qp91a5
** View name: wxatw
.subckt qp91a5 xegk t2tu01 vccq ukid qagu5 a3si7p vdd m4x6 ikliqn z207 vss h33l0e mj8kv
+ yavt3 djfa wihj vssq k8ji i7frj wysjp
Xb4ldl vss p5ts ukid ikliqn vdd yavkxw
Xxqmjyl vss fs4d4 t2tu01 ikliqn vdd yavkxw
Xp51e2 vss vdd vssq bwl924 vccq wysjp k8ji sprh
Xv1as vss vdd vssq ikliqn vccq yavt3 i7frj sprh
Xs4fy9q vdd z207 m4x6 vss w4yyx
Xz050 bwl924 vdd vss p5ts l5tu7
Xma4v qagu5 vdd vss g0k4x0 l5tu7
Xyxu6 vss xw1ga ikliqn m4x6 vdd yavkxw
Xomug wihj vdd vss xw1ga l5tu7
Xeuv9 h33l0e vdd vss fs4d4 l5tu7
Xromg vss g0k4x0 ikliqn z207 vdd yavkxw
Xbtwh vdd m4x6 mj8kv vss w4yyx
Xp7n5uf vss vdd vssq djfa vccq xegk a3si7p sprh
.ends qp91a5
** End of subcircuit definition.

** Library name: ato68m
** Cell name: w4tk6
** View name: wxatw
.subckt w4tk6 vccq bn1xm<2> e5bxo<4> vdd e5bxo<2> jrf7<2> c79ay<4> e5bxo<3> xun2gj
+ c79ay<0> fz5p9 k0zg vssq bn1xm<3> gvsv e5bxo<0> vss c79ay<3> jrf7<3> c79ay<2> y9bamv
+ c79ay<1> e5bxo<1> jrf7<0> bn1xm<1> jrf7<1> jrf7<4> bn1xm<0> bn1xm<4>
Xv3q9r xun2gj e5bxo<0> jrf7<0> c79ay<3> jrf7<3> bn1xm<1> e5bxo<3> d78f e5bxo<2> jrf7<4>
+ c79ay<4> jrf7<2> e5bxo<4> bn1xm<4> vccq c79ay<1> c79ay<2> jrf7<1> bn1xm<3> bn1xm<0>
+ e5bxo<1> c79ay<0> k0zg vssq bn1xm<2> i8uv
Xyzl2 x7xcd vdd gvsv vss aoar1 owc3 fz5p9 xoa6
Xslpfuj vss y9bamv owc3 aoar1 vdd siyoi
Xhwd5 x7xcd vss vdd d78f vccq vssq v1zh
.ends w4tk6
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: zmf6
** View name: wxatw
.subckt zmf6 vdd vssq vss vccq w8ln6b wjuku
Mz4mh g9e1 wjuku vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mboq4y g9e1 wjuku vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mnaktll w8ln6b g9e1 vss vss jil3gy W=1u L=0.2u m=1 nf=1
Mrll728 w8ln6b g9e1 vdd vdd ycgzf W=2u L=0.2u m=1 nf=1
.ends zmf6
** End of subcircuit definition.

** Library name: fxoq
** Cell name: so79m
** View name: wxatw
.subckt so79m bq58xy yuzoi
Ms27x7 t9y58 hye86 bq58xy bq58xy jil3gy W=16u L=0.2u m=1 nf=4
Md9jl hye86 yttrs bq58xy bq58xy jil3gy W=8u L=0.2u m=1 nf=2
Mi3bh7u yttrs v5uxb yuzoi yuzoi ycgzf W=8u L=0.2u m=1 nf=2
Mbgob yuzoi t9y58 bq58xy bq58xy jil3gy W=50u L=0.2u m=40 nf=20
Rl8yoj yuzoi v5uxb 500k
Cl93t v5uxb bq58xy 1p
Mkq8exc hye86 yttrs yuzoi yuzoi ycgzf W=8u L=0.2u m=1 nf=2
Mqm8e t9y58 hye86 yuzoi yuzoi ycgzf W=48u L=0.2u m=1 nf=8
Mw28a6 yttrs v5uxb bq58xy bq58xy jil3gy W=2u L=0.2u m=1 nf=1
.ends so79m
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: ismh
** View name: wxatw
.subckt ismh vss kwpzs d5af p59e<0> p59e<1> vdd p59e<2>
Mkxuc vss fuw8 vss vss ka1ebp W=0.5u L=0.2u m=2 nf=1
Medxw qzjk p59e<1> fuw8 vss ns67 W=0.4u L=0.06u m=2 nf=1
Ms71d3 vss kb5ucs vss vss ka1ebp W=0.5u L=0.2u m=4 nf=1
Xeza6cb vdd kwpzs vss qzjk kfwj
Mgd4by qzjk p59e<2> kb5ucs vss ns67 W=0.4u L=0.06u m=4 nf=1
Xulmbfr vdd qzjk vss d5af kfwj
Ma7yi vss rh83ow vss vss ka1ebp W=0.5u L=0.2u m=1 nf=1
Mg5zi qzjk p59e<0> rh83ow vss ns67 W=0.4u L=0.06u m=1 nf=1
.ends ismh
** End of subcircuit definition.

** Library name: ato68m
** Cell name: hux9
** View name: wxatw
.subckt hux9 u4yvu4 ne8j3p<6> ne8j3p<8> ne8j3p<9> jq5c ne8j3p<0> ne8j3p<2> vss vdd
+ ne8j3p<4> ne8j3p<7> ne8j3p<1> ne8j3p<5> sfzfn ne8j3p<3>
Xjj2g74<1> vss qyapv<1> xthed vdd yydl
Cov8t xthed vss 20f
Xpaw1c<3> vss ne8j3p<3> qyapv<0> vdd yydl
Xpaw1c<7> vss ne8j3p<7> qyapv<1> vdd yydl
Xuu37 vss jq5c qyapv<1> vdd yydl
Xjj2g74<0> vss qyapv<0> xthed vdd yydl
Xh6aem u4yvu4 vdd vss xthed xz3c
Xh14igt vss sfzfn qyapv<0> vdd yydl
Xpaw1c<0> vss ne8j3p<0> qyapv<0> vdd yydl
Xpaw1c<8> vss ne8j3p<8> qyapv<1> vdd yydl
Xpaw1c<5> vss ne8j3p<5> qyapv<1> vdd yydl
Ciudtzw qyapv<0> vss 10f
Cexq9za qyapv<1> vss 10f
Xpaw1c<1> vss ne8j3p<1> qyapv<0> vdd yydl
Xpaw1c<6> vss ne8j3p<6> qyapv<1> vdd yydl
Xpaw1c<9> vss ne8j3p<9> qyapv<1> vdd yydl
Xpaw1c<2> vss ne8j3p<2> qyapv<0> vdd yydl
Xpaw1c<4> vss ne8j3p<4> qyapv<0> vdd yydl
.ends hux9
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: pk25sw
** View name: wxatw
.subckt pk25sw ucs47<2> oq2fh<4> w7yq21<0> d7ug fc07cv<0> mf7h<2> z4gmk eb8dw4 moxhkk<0>
+ mf7h<3> cx5y6w<2> xoly7 moxhkk<3> wh97l<0> dauk6 wh97l<3> nv7l cx5y6w<1> mf7h<1> hx7e
+ vss oq2fh<2> w7yq21<1> cx5y6w<0> ucs47<0> w0ai<0> k1l7 vccq wh97l<1> h11f w0ai<3>
+ h3wh<2> yfwdms zuxxu w0ai<4> fc07cv<3> w7yq21<2> cfei8y<0> sx8f o80w7c fwb3 mf7h<4>
+ fc07cv<4> moxhkk<1> h85b<1> vvqk fc07cv<2> fc07cv<1> mghp q89m5x<2> q89m5x<1> e5ouu5
+ h85b<2> erzo9 rthrq mf1ax thrzz moxhkk<2> oq2fh<0> tf33qx cfei8y<2> h3wh<0> w0ai<2>
+ wcueo w7yq21<4> w7yq21<3> l2kqux h85b<0> ucs47<1> ucs47<4> oq2fh<1> wh97l<4> oq2fh<3>
+ cfei8y<1> wh97l<2> y9g3 moxhkk<4> q89m5x<0> vdd e7kwb ucs47<3> ru1afb h3wh<1> mf7h<0>
+ vssq lw0od y738z zd9cz rv4v w0ai<1>
Xllzf7 h11f xoly7 vccq tf33qx e7kwb yfwdms vdd wcueo rv4v mghp vss o80w7c hx7e rthrq
+ y9g3 y738z vssq mf1ax k1l7 zuxxu qp91a5
Xymkoo3 h85b<2> cfei8y<2> cx5y6w<2> h85b<1> fwb3 h85b<0> q89m5x<0> vss e5ouu5 h3wh<1>
+ vccq h3wh<0> q89m5x<2> h3wh<2> vssq cfei8y<1> vdd cfei8y<0> cx5y6w<0> q89m5x<1> z4gmk
+ cx5y6w<1> kwgk
Xl88vos sl0ay<1> w7yq21<4> fc07cv<3> w21eq<2> w21eq<4> w0ai<3> nv7l e5ouu5 moxhkk<0>
+ lw0od thrzz w0ai<1> vccq w21eq<3> w7yq21<1> sx8f w7yq21<0> w0ai<2> z4gmk l2kqux
+ fc07cv<2> fc07cv<4> w7yq21<3> fc07cv<1> moxhkk<3> sl0ay<2> sl0ay<3> sl0ay<0> w0ai<4>
+ moxhkk<4> vdd zd9cz sl0ay<4> fc07cv<0> w21eq<1> vssq erzo9 moxhkk<2> vss moxhkk<1>
+ vvqk ru1afb w7yq21<2> w21eq<0> d7ug dauk6 w0ai<0> gugmik
Xltv5nm wh97l<2> w21eq<2> sl0ay<1> oq2fh<2> vdd ucs47<0> oq2fh<1> wh97l<3> w21eq<4>
+ w21eq<1> oq2fh<3> sl0ay<3> vss mf7h<4> ucs47<4> wh97l<0> ucs47<2> sl0ay<0> w21eq<0>
+ ucs47<1> sl0ay<2> ucs47<3> oq2fh<0> sl0ay<4> w21eq<3> mf7h<1> mf7h<2> wh97l<4>
+ wh97l<1> mf7h<0> eb8dw4 oq2fh<4> mf7h<3> z0nj9x
.ends pk25sw
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: n26dpi
** View name: wxatw
.subckt n26dpi b4fj c2dhp zhw6z gi5kb vdd vss
Mpxs6zy c2dhp b4fj pil0s vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Xfssvi1 vdd ve5m5 vss c2dhp kfwj
Mfmg8 zhw6z b4fj pil0s vdd vw445g W=0.6u L=0.06u m=1 nf=1
Mivis c2dhp gi5kb pil0s vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Xu3xa6e ve5m5 vdd vss pil0s l5tu7
Mwg1n zhw6z gi5kb pil0s vss ns67 W=0.4u L=0.06u m=1 nf=1
.ends n26dpi
** End of subcircuit definition.

** Library name: ato68m
** Cell name: v18jr
** View name: wxatw
.subckt v18jr rq3o vssq gquo vccq rhxtq atea x8g750 d3v2w gea1
Mhyhyi rq3o i6ta n9hx vssq jil3gy W=1u L=0.2u m=1 nf=1
Xl7fl ggq1 vssq rl6hg1 vccq cathu
Mf9bd emfbm gea1 vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Maih8rb d3v2w rl6hg1 wduh vssq jil3gy W=1u L=0.2u m=1 nf=1
Mkwep87 n9hx gquo vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Xkftjm rthbwe vssq i6ta vccq cathu
Mqt3p9 d3v2w rl6hg1 nma6 vccq ycgzf W=2u L=0.2u m=1 nf=1
Mfexd wduh gquo vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mhedg8y rq3o i6ta emfbm vccq ycgzf W=2u L=0.2u m=1 nf=1
Ml51ko2 nma6 gea1 vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Xyrjby vssq rhxtq rthbwe x8g750 vccq uqsz
Xc2cwvl vccq vssq x8g750 atea ggq1 m5vzy
.ends v18jr
** End of subcircuit definition.

** Library name: ato68m
** Cell name: l8ij1
** View name: wxatw
.subckt l8ij1 sxkfbs vss jvzv
Czf5dmf jvzv vss 15f
Rv1skc sxkfbs jvzv 200
Cfyxwm sxkfbs vss 15f
.ends l8ij1
** End of subcircuit definition.

** Library name: ato68m
** Cell name: f7hz
** View name: wxatw
.subckt f7hz vdd vss epzwg5 f6sf
Xa89d<3> it6j<3> vss f6sf l8ij1
Xa89d<0> it6j<0> vss vhln98<1> l8ij1
Xntkhcb<2> it6j<2> vss vhln98<2> vdd ajlh
Xa89d<1> it6j<1> vss vhln98<2> l8ij1
Xntkhcb<1> it6j<1> vss vhln98<1> vdd ajlh
Xntkhcb<0> it6j<0> vss epzwg5 vdd ajlh
Xa89d<2> it6j<2> vss vhln98<3> l8ij1
Xntkhcb<3> it6j<3> vss vhln98<3> vdd ajlh
.ends f7hz
** End of subcircuit definition.

** Library name: fxoq
** Cell name: texe
** View name: wxatw
.subckt texe q6ve vssq vccq
Ryt5sle zxx75 vssq 10k
Rkj2u v5r3b vccq 10k
Mzfkfti q6ve v5r3b vccq vccq ycgzf W=60u L=0.3u m=2 nf=12
Mig72ly q6ve zxx75 vssq vssq jil3gy W=60u L=0.3u m=2 nf=12
.ends texe
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: cathu
** View name: wxatw
.subckt cathu rm91 vssq kkjm54 vccq
Mjmze kkjm54 rm91 vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mejae kkjm54 rm91 vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
.ends cathu
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: yqsu
** View name: wxatw
.subckt yqsu xtr5 vss z2i9an
Chox4 z2i9an vss 8f
Ch692r xtr5 vss 8f
Ryt2n6 z2i9an xtr5 120
.ends yqsu
** End of subcircuit definition.

** Library name: ato68m
** Cell name: wtth
** View name: wxatw
.subckt wtth v2qwm<2> v2qwm<0> v2qwm<3> vdd qqmq vss v2qwm<4> wyfs90 v2qwm<1>
Mz1tve xghw3p hna1da<1> uqjh<1> vdd vw445g W=0.15u L=0.06u m=2 nf=1
Mhwdl orqxt<2> qqmq vss vss ns67 W=0.1u L=0.06u m=4 nf=1
Mgc37y xghw3p hna1da<3> uqjh<3> vdd vw445g W=0.15u L=0.06u m=8 nf=1
Xnju4a vdd xghw3p vss wyfs90 kfwj
Xa0noq<1> vxfw<1> vss v2qwm<1> v2qwm<4> vdd wxlvj5
Xa0noq<0> vxfw<0> vss v2qwm<0> v2qwm<4> vdd wxlvj5
Mb0mq xghw3p vxfw<3> orqxt<3> vss ns67 W=0.1u L=0.06u m=8 nf=1
Mr40z0u xghw3p qqmq vss vss ns67 W=0.5u L=0.06u m=1 nf=1
Xvs8sld<3> vss hna1da<3> v2qwm<4> v2qwm<3> vdd yavkxw
Mvs7i uqjh<0> qqmq vdd vdd vw445g W=0.15u L=0.06u m=1 nf=1
Mixj91 xghw3p hna1da<2> uqjh<2> vdd vw445g W=0.15u L=0.06u m=4 nf=1
Mfqamig xghw3p vxfw<2> orqxt<2> vss ns67 W=0.1u L=0.06u m=4 nf=1
Xvs8sld<2> vss hna1da<2> v2qwm<4> v2qwm<2> vdd yavkxw
Mswke orqxt<0> qqmq vss vss ns67 W=0.1u L=0.06u m=1 nf=1
Xvs8sld<1> vss hna1da<1> v2qwm<4> v2qwm<1> vdd yavkxw
Cnqfv xghw3p vss 6f
Mfg9z8 xghw3p hna1da<0> uqjh<0> vdd vw445g W=0.15u L=0.06u m=1 nf=1
Mk0kzew orqxt<3> qqmq vss vss ns67 W=0.1u L=0.06u m=8 nf=1
Mus7q2 uqjh<2> qqmq vdd vdd vw445g W=0.15u L=0.06u m=4 nf=1
Xvs8sld<0> vss hna1da<0> v2qwm<4> v2qwm<0> vdd yavkxw
Md5fy5 xghw3p vxfw<1> orqxt<1> vss ns67 W=0.1u L=0.06u m=2 nf=1
Mv7yj xghw3p vxfw<0> orqxt<0> vss ns67 W=0.1u L=0.06u m=1 nf=1
Mc36rz uqjh<1> qqmq vdd vdd vw445g W=0.15u L=0.06u m=2 nf=1
Mg9ws4 uqjh<3> qqmq vdd vdd vw445g W=0.15u L=0.06u m=8 nf=1
Xa0noq<2> vxfw<2> vss v2qwm<2> v2qwm<4> vdd wxlvj5
Mlyui orqxt<1> qqmq vss vss ns67 W=0.1u L=0.06u m=2 nf=1
Mlt3qs xghw3p qqmq vdd vdd vw445g W=1u L=0.06u m=1 nf=2
Xa0noq<3> vxfw<3> vss v2qwm<3> v2qwm<4> vdd wxlvj5
.ends wtth
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: c4ar97
** View name: wxatw
.subckt c4ar97 ku2m<3> h7prkn<2> h7prkn<0> sl4q h5gc66<2> hglux7 zhyrhp<3> vccq ywgc6
+ ku2m<2> xc9i4d<2> niwz46 ku2m<4> vssq b2ceco<2> b2ceco<1> vss rqqv xc9i4d<0> xju54u
+ h7prkn<1> h5gc66<3> zhyrhp<1> zhyrhp<4> vdd juby h5gc66<0> ku2m<0> wqhk jla3n
+ zhyrhp<2> t8soy no1qx6 h5gc66<1> vfk9b b2ceco<0> la6qn ku2m<1> w0zvi b41v2u i391
+ zhyrhp<0> gusg xc9i4d<1>
Xal7gi gh1dv xc9i4d<1> v1v5<2> v1v5<3> b2ceco<1> v1v5<0> vssq xc9i4d<2> xc9i4d<0> juby
+ v1v5<4> gw5es<3> v1v5<1> vccq gw5es<4> b2ceco<0> gw5es<0> gw5es<2> b2ceco<2> gw5es<1>
+ fwhwl
Xzkbs9 vccq v1v5<2> gw5es<4> vdd gw5es<2> ku2m<2> zhyrhp<4> gw5es<3> ywgc6 zhyrhp<0>
+ niwz46 i391 vssq v1v5<3> xju54u gw5es<0> vss zhyrhp<3> ku2m<3> zhyrhp<2> rqqv
+ zhyrhp<1> gw5es<1> ku2m<0> v1v5<1> ku2m<1> ku2m<4> v1v5<0> v1v5<4> w4tk6
Xv5u7z vss h5gc66<0> b41v2u h5gc66<1> w0zvi no1qx6 vfk9b h5gc66<3> jla3n vccq t8soy gusg
+ sl4q hglux7 wqhk h7prkn<1> h7prkn<0> vssq h7prkn<2> la6qn gh1dv h5gc66<2> vdd we5v
.ends c4ar97
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: m5vzy
** View name: wxatw
.subckt m5vzy vccq vssq jewpc0 z88s bopi
Mnt8o bopi jewpc0 vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mpwzr bopi z88s vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mu568qh bopi z88s wim4 vccq ycgzf W=4u L=0.2u m=1 nf=2
Myyw6 wim4 jewpc0 vccq vccq ycgzf W=4u L=0.2u m=1 nf=2
.ends m5vzy
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: j19e
** View name: wxatw
.subckt j19e gkrpou meld q57a vss vdd
Xykoi vdd meld xd7g vss w4yyx
Xa1qza vss xd7g q57a gkrpou vdd yavkxw
.ends j19e
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: zuhc6m
** View name: wxatw
.subckt zuhc6m qz5196 vss er9lh vdd ln1ps rzaf u79k
My6h4 u79k bqfj kj7a vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mdppb8 f3l0jo bqfj myapv vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Mnrsfz ydmep bqfj myapv vss ka1ebp W=0.3u L=0.06u m=1 nf=1
Mo8mz ydmep qtycf myapv vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Xq1uq8b rzaf vss l27ue5 myapv vdd wxlvj5
Xfh1t fx4m vdd vss ydmep l5tu7
Xefqc f3l0jo vdd vss rzaf l5tu7
Xoyhw vss ydmep kj7a ln1ps vdd yavkxw
Xprl6xl qtycf vdd vss er9lh l5tu7
Xe9su bqfj vdd vss qtycf l5tu7
Xswb0w8 qz5196 vdd vss rzaf l5tu7
Mcaf02 f3l0jo qtycf myapv vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Mz7sp fx4m bqfj kj7a vss ka1ebp W=0.2u L=0.06u m=1 nf=1
Xrv12 l27ue5 vdd vss ln1ps l5tu7
Mglu4q1 fx4m qtycf kj7a vdd ad57k3 W=0.2u L=0.06u m=1 nf=1
Mcbwhg u79k qtycf kj7a vss ka1ebp W=0.3u L=0.06u m=1 nf=1
.ends zuhc6m
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: fn5wjn
** View name: wxatw
.subckt fn5wjn fm57 hgpa fwkdy<2> yhy5i fwkdy<3> fwkdy<0> t1ehl9 j8kvf vdd vss fwkdy<4>
+ fwkdy<1>
Xgztb sxk8i vdd vss fm57 l5tu7
Xa6wmnv t1ehl9 p9fro b6ut<0> vdd mezh vss mu5k
Xclub4<0> ye9xuu<0> vss sxk8i vdd yhy5i fwkdy<0> hmut<0> zuhc6m
Xw8ut4<1> b6ut<1> fwkdy<1> vss hmut<1> vdd d9b5zl
Xmq2a2k vss a3zjvd a4pp<3> a4pp<4> vdd yavkxw
Xclub4<3> ye9xuu<3> vss sxk8i vdd yhy5i fwkdy<3> hmut<3> zuhc6m
Xp39l5o<0> vss t5ptau<1> b6ut<0> a4pp<0> vdd yavkxw
Xclub4<1> ye9xuu<1> vss sxk8i vdd yhy5i fwkdy<1> hmut<1> zuhc6m
Xr5lnz<2> hgpa fwkdy<2> a4pp<2> vss vdd wfrbt
Xktw9 mezh vss a3zjvd budac9 vdd wxlvj5
Xp39l5o<2> vss t5ptau<3> b6ut<2> a4pp<2> vdd yavkxw
Xw8ut4<2> b6ut<2> fwkdy<2> vss hmut<2> vdd d9b5zl
Xr5lnz<0> hgpa fwkdy<0> a4pp<0> vss vdd wfrbt
Xp39l5o<3> vss t5ptau<4> b6ut<3> a4pp<3> vdd yavkxw
Xp39l5o<1> vss t5ptau<2> b6ut<1> a4pp<1> vdd yavkxw
Xw8ut4<0> b6ut<0> fwkdy<0> vss hmut<0> vdd d9b5zl
Xs4yq<1> b6ut<2> vdd vss t5ptau<2> l5tu7
Xclub4<2> ye9xuu<2> vss sxk8i vdd yhy5i fwkdy<2> hmut<2> zuhc6m
Xs4yq<3> b6ut<4> vdd vss t5ptau<4> l5tu7
Xedjqf vss vdd yhy5i of41s fwkdy<4> hmut<4> sxk8i z1nko
Xr5lnz<3> hgpa fwkdy<3> a4pp<3> vss vdd wfrbt
Xqx78ew p9fro vdd vss j8kvf l5tu7
Xw8ut4<4> b6ut<4> fwkdy<4> vss hmut<4> vdd d9b5zl
Xr5lnz<4> hgpa fwkdy<4> a4pp<4> vss vdd wfrbt
Xs4yq<0> b6ut<1> vdd vss t5ptau<1> l5tu7
Xr5lnz<1> hgpa fwkdy<1> a4pp<1> vss vdd wfrbt
Xs4yq<2> b6ut<3> vdd vss t5ptau<3> l5tu7
Xw8ut4<3> b6ut<3> fwkdy<3> vss hmut<3> vdd d9b5zl
Xhex60 a4pp<0> a4pp<1> vss a4pp<2> budac9 vdd p7glz
.ends fn5wjn
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: hggq3i
** View name: wxatw
.subckt hggq3i f8cf<3> h9cgax vdd lgrjzh l5h79s a9zfaz f8cf<0> oizj vss tjt1w<0> vccq
+ ztsou0 f8cf<1> f8cf<2> cv8o vssq tjt1w<1> lici f8cf<4>
Xzagd cv8o vccq vss vssq lici tjt1w<1> tjt1w<0> vdd h1n10i
Xe5hm f8cf<0> a9zfaz f8cf<1> xfz1zm vssq h9cgax f8cf<4> f8cf<3> vccq vdd oizj f8cf<2>
+ l5h79s vss a44p
Xzskm lgrjzh vssq ztsou0 vccq xfz1zm lyoln
.ends hggq3i
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: yo4ne
** View name: wxatw
.subckt yo4ne vss btpi6 lmlt vdd muua0
Mqpaxg0 muua0 btpi6 vdd vdd vw445g W=0.8u L=0.06u m=1 nf=2
Mrlxfw muua0 btpi6 smdyu vss ns67 W=0.8u L=0.06u m=1 nf=2
Mzex4l muua0 lmlt vdd vdd vw445g W=0.8u L=0.06u m=1 nf=2
Mak81sd smdyu lmlt vss vss ns67 W=0.8u L=0.06u m=1 nf=2
.ends yo4ne
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: jrilr9
** View name: wxatw
.subckt jrilr9 vccq yz6qt<1> afu0<4> afu0<0> afu0<2> yz6qt<3> yz6qt<2> vssq afu0<1>
+ yz6qt<4> mh4eq yz6qt<0> afu0<3>
Xkt2g yz6qt<0> yz6qt<4> yz6qt<2> mh4eq vccq yz6qt<1> yz6qt<3> vmswp
Mf621f lyh4<4> afu0<4> vssq vssq jil3gy W=0.5u L=0.2u m=16 nf=1
Rg1lqc lyh4<0> mh4eq 2.4k
Myfyy lyh4<3> afu0<3> vssq vssq jil3gy W=0.5u L=0.2u m=8 nf=1
Rzcha lyh4<2> mh4eq 600
Rlpn71i lyh4<3> mh4eq 300
Ml8t13l lyh4<1> afu0<1> vssq vssq jil3gy W=0.5u L=0.2u m=2 nf=1
Rv47r2 lyh4<1> mh4eq 1.2k
Ru85qz lyh4<4> mh4eq 150
Mjpxw lyh4<0> afu0<0> vssq vssq jil3gy W=0.5u L=0.2u m=1 nf=1
Me54zv3 lyh4<2> afu0<2> vssq vssq jil3gy W=0.5u L=0.2u m=4 nf=1
.ends jrilr9
** End of subcircuit definition.

** Library name: ato68m
** Cell name: h1n10i
** View name: wxatw
.subckt h1n10i y52pv7 vccq vss vssq o9b9u4 vdm8zj<1> vdm8zj<0> vdd
Mzyq3i nryhj zogu vssq vssq jil3gy W=2u L=1u m=2 nf=1
Cryil o9b9u4 vssq 2p
Xzwrv<1> vss vdd vssq vdm8zj<1> vccq kao3td<1> i95j9<1> sprh
Xzwrv<0> vss vdd vssq vdm8zj<0> vccq kao3td<0> i95j9<0> sprh
Mgf7ex o9b9u4 o9b9u4 vssq vssq jil3gy W=2u L=1u m=2 nf=1
Cgk658 y52pv7 vccq 2p
Mwvoi y52pv7 zogu vssq vssq jil3gy W=2u L=1u m=2 nf=1
Rij0yew vccq zogu 24k
Meus7sk y52pv7 y52pv7 vccq vccq ycgzf W=4u L=1u m=2 nf=1
Mr6gzo y52pv7 i95j9<1> nryhj vssq jil3gy W=2u L=0.2u m=1 nf=1
Mqhj5 o9b9u4 y52pv7 vccq vccq ycgzf W=4u L=1u m=2 nf=1
Mfby6 zogu zogu vssq vssq jil3gy W=2u L=1u m=1 nf=1
Mus81t g44a zogu vssq vssq jil3gy W=2u L=1u m=1 nf=1
Mz7aw y52pv7 i95j9<0> g44a vssq jil3gy W=2u L=0.2u m=1 nf=1
.ends h1n10i
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: wlyjd
** View name: wxatw
.subckt wlyjd y95wm lze378<1> lze378<4> vdd vss c3ykk1 lze378<0> lze378<3> ehcfwv i7zg
+ lze378<2> owbme
Xjfgd op7f vdd rlip gidww vss rz2bge t5n19 vui2
Xh0o48 y95wm ehcfwv vss t5n19 vdd op7f qiex8
Xhugq rz2bge gidww lze378<2> c3ykk1 lze378<3> lze378<0> i7zg y95wm vdd vss lze378<4>
+ lze378<1> fn5wjn
Xwe14 vss dwuax owbme y95wm vdd yavkxw
Xpn2mu rz2bge vdd vss dwuax l5tu7
Xp215zj rz2bge gidww vdd i7zg y95wm vss ji9j
.ends wlyjd
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: uye5vz
** View name: wxatw
.subckt uye5vz vss adj5 vdd ovk306 k8hwgq
Xugo9 vss k8hwgq adj5 vdd j4ii yo4ne
Xrq87r vdd j4ii vss ovk306 kfwj
.ends uye5vz
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: udmp
** View name: wxatw
.subckt udmp ww3p dxmd<4> yo1i<2> k0qtd a2djg cu2af5<14> wbjp erflz2<18> cu2af5<19>
+ jsfy<0> wvk9mh dxmd<1> erflz2<3> jmfj<1> ymob<3> yo1i<0> erflz2<15> j9y56<4>
+ erflz2<31> cu2af5<10> cu2af5<1> cu2af5<18> u09t92<1> ps7xf1 e9k4l<0> cu2af5<4> mu0x<3>
+ wzymw4 e92if2 j9y56<3> ae1v o83e<1> jc9f4p<2> kd9h erflz2<17> yxapm<1> erflz2<9> y4hg
+ ymob<2> erflz2<6> j9y56<6> cu2af5<3> jmfj<2> yo1i<1> cu2af5<15> erflz2<10> erflz2<0>
+ cu2af5<16> wcu58e mu0x<4> bodg erflz2<7> dxmd<7> erflz2<14> o83e<5> o83e<3> e9k4l<1>
+ cu2af5<6> lxv2s o83e<2> hpaa mu0x<0> u09t92<2> erflz2<20> a46hb afvfm erflz2<30>
+ o83e<0> tvxkez erflz2<2> yxapm<2> j9y56<1> erflz2<26> yxapm<0> jmfj<4> o83e<7> p4xy
+ u09t92<4> jsfy<1> cu2af5<13> j9y56<7> erflz2<24> erflz2<1> oaov36 mu0x<2> j9y56<0>
+ yxapm<4> cu2af5<7> jc9f4p<0> mu0x<1> cu2af5<20> dxmd<6> erflz2<19> bo8fy jc9f4p<1>
+ iu7a dxmd<5> erflz2<11> jsfy<3> dxmd<0> erflz2<25> vccq jsfy<2> erflz2<21> dxmd<2>
+ erflz2<13> ymob<4> u09t92<0> cu2af5<9> erflz2<16> erflz2<12> erflz2<8> cu2af5<22>
+ cu2af5<5> ydj9 fv9mp erflz2<5> j9y56<2> o83e<4> cu2af5<11> cu2af5<2> z6y7x cu2af5<12>
+ yxapm<3> d53w dxmd<3> erflz2<22> cu2af5<8> d4ih7z hhqjm yemsy erflz2<28> aed2r
+ cu2af5<17> ymob<0> vdd jmfj<3> f84c0z vssq jmfj<0> o83e<6> u09t92<3> jsfy<4> vss
+ ymob<1> cu2af5<0> erflz2<4> cu2af5<21> erflz2<23> erflz2<29> erflz2<27> j9y56<5>
+ cu2af5<23>
Xua319<2> iwhf<3> cu2af5<8> cu2af5<6> ewdhfx<2> erflz2<10> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<2> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<2> kqlkvr<0>
+ o83e<2> cu2af5<7> erflz2<11> a30s<1> a30s<4> vdd dxmd<2> erflz2<8> iwhf<0> k8aj95
+ i9c6fh<2> a30s<2> v6qvx pjb1s erflz2<9> wefw ki6i<0> unig<2> iwhf<1> co4b96<2> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xo3irq vssq ktu6j vccq iu7a ye8xk0
Xqvsu1b wo9gkl<0> vss fig90<4> dii8j<2> vssq wo9gkl<1> uae4<1> vccq wo9gkl<4> eg3j
+ e4ajkt<8> fig90<2> fig90<0> vdd uae4<0> fig90<3> tvw39 wo9gkl<2> dii8j<0> f2im uae4<2>
+ a2djg rm5yv5 fig90<1> iyul dii8j<1> wo9gkl<3> jq2jj
Xua319<7> iwhf<3> cu2af5<23> cu2af5<21> ewdhfx<7> erflz2<30> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<7> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<7> kqlkvr<0>
+ o83e<7> cu2af5<22> erflz2<31> a30s<1> a30s<4> vdd dxmd<7> erflz2<28> iwhf<0> k8aj95
+ i9c6fh<7> a30s<2> v6qvx pjb1s erflz2<29> wefw ki6i<0> unig<7> iwhf<1> co4b96<7> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xuaq5 vssq vccq vss vdd gja4
Ms9a9p vssq vccq vssq vssq jil3gy W=5u L=1u m=40 nf=1
Xqxg6k ymob<2> u09t92<4> wo9gkl<0> y4hg iwhf<0> yxapm<2> lxv2s ww3p fig90<0> yxapm<3>
+ kqlkvr<2> yemsy fig90<3> mu0x<0> vju3nz mu0x<3> ae1v kqlkvr<1> yxapm<1> hhqjm vss
+ u09t92<2> wo9gkl<1> kqlkvr<0> ymob<0> a30s<0> pvfsp vccq mu0x<1> pkwroo a30s<3>
+ uae4<2> jg2jd8 hmn4i a30s<4> iwhf<3> wo9gkl<2> dii8j<0> hpaa gf7hqy a46hb yxapm<4>
+ iwhf<4> fig90<1> yo1i<1> utri iwhf<2> iwhf<1> wefw ki6i<2> ki6i<1> fv9mp yo1i<2> qkb02
+ pjb1s v5uf pjbk1 fig90<2> u09t92<0> oaov36 dii8j<2> uae4<0> a30s<2> twln6i wo9gkl<4>
+ wo9gkl<3> rm5yv5 yo1i<0> ymob<1> ymob<4> u09t92<1> mu0x<4> u09t92<3> dii8j<1> mu0x<2>
+ p4xy fig90<4> ki6i<0> vdd muaybf ymob<3> f2im uae4<1> yxapm<0> vssq bfhaz nj7z n0f91i
+ afvfm a30s<1> pk25sw
Xua319<4> iwhf<3> cu2af5<14> cu2af5<12> ewdhfx<4> erflz2<18> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<4> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<4> kqlkvr<0>
+ o83e<4> cu2af5<13> erflz2<19> a30s<1> a30s<4> vdd dxmd<4> erflz2<16> iwhf<0> k8aj95
+ i9c6fh<4> a30s<2> v6qvx pjb1s erflz2<17> wefw ki6i<0> unig<4> iwhf<1> co4b96<4> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xgtozu jsfy<3> k8aj95 vdd e92if2 hmn4i g3t2c jsfy<0> v5uf vss e9k4l<0> vccq q5bmjf
+ jsfy<1> jsfy<2> tvw39 vssq e9k4l<1> eg3j jsfy<4> hggq3i
Xmvda6v ps7xf1 jmfj<1> jmfj<4> vdd vss bo8fy jmfj<0> jmfj<3> ohychn wvk9mh jmfj<2>
+ tvxkez wlyjd
Xmp8aqt ewdhfx<5> jg2jd8 co4b96<6> i9c6fh<2> jc9f4p<1> co4b96<3> pjb1s ewdhfx<1>
+ co4b96<2> unig<3> co4b96<0> muaybf i9c6fh<6> co4b96<1> iyul ewdhfx<8> pvfsp ewdhfx<0>
+ unig<4> vssq vdd i9c6fh<3> pkwroo i9c6fh<1> k8aj95 unig<7> co4b96<7> nj7z unig<2>
+ unig<0> jc9f4p<0> i9c6fh<7> ewdhfx<6> i9c6fh<8> i9c6fh<5> jc9f4p<2> noy8c unig<5>
+ ewdhfx<3> unig<8> unig<1> vccq co4b96<5> i9c6fh<4> ewdhfx<4> i9c6fh<0> ewdhfx<2>
+ unig<6> co4b96<4> vss co4b96<8> ewdhfx<7> un713b
Xha8j9l gf7hqy f84c0z xquh vss vdd j19e
Xua319<5> iwhf<3> cu2af5<17> cu2af5<15> ewdhfx<5> erflz2<22> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<5> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<5> kqlkvr<0>
+ o83e<5> cu2af5<16> erflz2<23> a30s<1> a30s<4> vdd dxmd<5> erflz2<20> iwhf<0> k8aj95
+ i9c6fh<5> a30s<2> v6qvx pjb1s erflz2<21> wefw ki6i<0> unig<5> iwhf<1> co4b96<5> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xvemppa wo9gkl<0> vss fig90<4> dii8j<2> vssq wo9gkl<1> uae4<1> vccq wo9gkl<4> eg3j
+ e4ajkt<9> fig90<2> fig90<0> vdd uae4<0> fig90<3> tvw39 wo9gkl<2> dii8j<0> qkb02
+ uae4<2> kd9h pjbk1 fig90<1> noy8c dii8j<1> wo9gkl<3> jq2jj
Xua319<6> iwhf<3> cu2af5<20> cu2af5<18> ewdhfx<6> erflz2<26> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<6> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<6> kqlkvr<0>
+ o83e<6> cu2af5<19> erflz2<27> a30s<1> a30s<4> vdd dxmd<6> erflz2<24> iwhf<0> k8aj95
+ i9c6fh<6> a30s<2> v6qvx pjb1s erflz2<25> wefw ki6i<0> unig<6> iwhf<1> co4b96<6> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xsuj0kt vssq g3t2c vccq d53w ye8xk0
Xdgf0zu yxapm<1> q5bmjf vccq vss mu0x<4> yxapm<0> mu0x<0> tvxkez yxapm<2> wzymw4
+ yxapm<4> aed2r d4ih7z wbjp mu0x<3> mu0x<1> mu0x<2> k0qtd yxapm<3> vssq vdd vwt2x6
Xrwnkhp xquh wefw twln6i wcu58e ewdhfx<8> bodg vdd v6qvx co4b96<8> vss xeip
Xgxymzp aed2r vssq vccq texe
Xzvie k8aj95 e4ajkt<5> ktu6j n0f91i e4ajkt<0> vssq vdd jmfj<1> e4ajkt<3> bfhaz e4ajkt<2>
+ utri jmfj<2> vju3nz e4ajkt<6> e4ajkt<8> z6y7x vss jmfj<3> e4ajkt<1> e4ajkt<9>
+ e4ajkt<7> jmfj<4> jmfj<0> vccq e4ajkt<4> ohychn c4vsk ne2krl
Xua319<1> iwhf<3> cu2af5<5> cu2af5<3> ewdhfx<1> erflz2<6> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<1> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<1> kqlkvr<0>
+ o83e<1> cu2af5<4> erflz2<7> a30s<1> a30s<4> vdd dxmd<1> erflz2<4> iwhf<0> k8aj95
+ i9c6fh<1> a30s<2> v6qvx pjb1s erflz2<5> wefw ki6i<0> unig<1> iwhf<1> co4b96<1> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xua319<0> iwhf<3> cu2af5<2> cu2af5<0> ewdhfx<0> erflz2<2> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<0> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<0> kqlkvr<0>
+ o83e<0> cu2af5<1> erflz2<3> a30s<1> a30s<4> vdd dxmd<0> erflz2<0> iwhf<0> k8aj95
+ i9c6fh<0> a30s<2> v6qvx pjb1s erflz2<1> wefw ki6i<0> unig<0> iwhf<1> co4b96<0> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xua319<3> iwhf<3> cu2af5<11> cu2af5<9> ewdhfx<3> erflz2<14> pvfsp a30s<3> vccq eg3j
+ iwhf<2> kqlkvr<2> j9y56<3> iwhf<4> vssq ki6i<2> ki6i<1> vss e4ajkt<3> kqlkvr<0>
+ o83e<3> cu2af5<10> erflz2<15> a30s<1> a30s<4> vdd dxmd<3> erflz2<12> iwhf<0> k8aj95
+ i9c6fh<3> a30s<2> v6qvx pjb1s erflz2<13> wefw ki6i<0> unig<3> iwhf<1> co4b96<3> xquh
+ tvw39 a30s<0> twln6i kqlkvr<1> c4ar97
Xoi61 vssq c4vsk vccq ydj9 ye8xk0
Mwizki vss vdd vss vss ka1ebp W=5u L=1u m=40 nf=1
.ends udmp
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: yydl
** View name: wxatw
.subckt yydl vss lnolwu o822u vdd
Mr8xy taw7 o822u vdd vdd vw445g W=1.2u L=0.06u m=1 nf=2
Mlz55 lnolwu taw7 vss vss ns67 W=2.4u L=0.06u m=1 nf=4
Myro58s taw7 o822u vss vss ns67 W=0.6u L=0.06u m=1 nf=1
Mjcyl6d lnolwu taw7 vdd vdd vw445g W=4.8u L=0.06u m=1 nf=4
.ends yydl
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: lyoln
** View name: wxatw
.subckt lyoln vfw3l vssq ve6oy vccq bma5
Mv1ac ufpsl ufpsl vccq vccq ycgzf W=4u L=1u m=2 nf=1
Mzonmf ufpsl vfw3l vssq vssq jil3gy W=2u L=1u m=2 nf=1
Mj63o ve6oy vfw3l vssq vssq jil3gy W=2u L=1u m=2 nf=1
Mr98eyh bma5 ufpsl vccq vccq ycgzf W=4u L=1u m=2 nf=1
Mn53lpo vfw3l vfw3l vssq vssq jil3gy W=2u L=1u m=2 nf=1
.ends lyoln
** End of subcircuit definition.

** Library name: ato68m
** Cell name: v1zh
** View name: wxatw
.subckt v1zh eskzp vss vdd xjezk4 vccq vssq
Mu11t8o k59x eskzp vssq vssq jil3gy W=3u L=0.2u m=1 nf=2
Mr36xky eh6r k59x vccq vccq ycgzf W=0.8u L=0.2u m=1 nf=1
Mkhris5 xjezk4 k59x vssq vssq jil3gy W=2u L=0.2u m=1 nf=2
Mzce3l8 k59x eh6r vccq vccq ycgzf W=0.8u L=0.2u m=1 nf=1
Mgmf1 xjezk4 k59x vccq vccq ycgzf W=4u L=0.2u m=1 nf=2
Me8ykav t7xuy eskzp vdd vdd vw445g W=1.2u L=0.06u m=1 nf=2
Miusu t7xuy eskzp vss vss ns67 W=0.6u L=0.06u m=1 nf=1
Mz3wjxy eh6r t7xuy vssq vssq jil3gy W=3u L=0.2u m=1 nf=2
.ends v1zh
** End of subcircuit definition.

** Library name: fxoq
** Cell name: epfg
** View name: wxatw
.subckt epfg kbxtf xuo51
Mq5wf7q xuo51 xuo51 kbxtf kbxtf jil3gy W=20u L=0.3u m=2 nf=4
Mbsj8 kbxtf kbxtf xuo51 xuo51 jil3gy W=20u L=0.3u m=2 nf=4
.ends epfg
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: q8t9
** View name: wxatw
.subckt q8t9 vdd vss xxhqv jv878
Mf1wwo xxhqv bc2dul vdd vdd vw445g W=9.6u L=0.06u m=1 nf=8
Mq4po xxhqv bc2dul vss vss ns67 W=4.8u L=0.06u m=1 nf=8
Mjw6oo0 bc2dul jv878 vdd vdd vw445g W=2.4u L=0.06u m=1 nf=4
Mom5u bc2dul jv878 vss vss ns67 W=1.2u L=0.06u m=1 nf=2
.ends q8t9
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: q8m8
** View name: wxatw
.subckt q8m8 w2jsk rbsi8 vccq qpkdub lii3yp vssq
Mhw93bc w2jsk qpkdub lii3yp vssq jil3gy W=4u L=0.2u m=1 nf=2
Mu0x5 w2jsk rbsi8 lii3yp vccq ycgzf W=8u L=0.2u m=1 nf=4
.ends q8m8
** End of subcircuit definition.

** Library name: ato68m
** Cell name: i8uv
** View name: wxatw
.subckt i8uv v1yg l89fyg<0> by73<0> cn4cm<3> by73<3> lmh4<1> l89fyg<3> jzyuz l89fyg<2>
+ by73<4> cn4cm<4> by73<2> l89fyg<4> lmh4<4> vccq cn4cm<1> cn4cm<2> by73<1> lmh4<3>
+ lmh4<0> l89fyg<1> cn4cm<0> kl8id vssq lmh4<2>
Xducwl p4ogt vssq jj2gv vccq cathu m=4
Xmlge16 l89fyg<3> vssq v1yg vccq by73<3> cn4cm<3> jj2gv lmh4<3> kl8id v18jr m=4
Xob95 l89fyg<1> vssq v1yg vccq by73<1> cn4cm<1> jj2gv lmh4<1> kl8id v18jr m=1
Xv6vs l89fyg<2> vssq v1yg vccq by73<2> cn4cm<2> jj2gv lmh4<2> kl8id v18jr m=2
Xcur4 jzyuz vssq p4ogt vccq cathu
Xthhcu l89fyg<0> vssq v1yg vccq by73<0> cn4cm<0> jj2gv lmh4<0> kl8id v18jr m=1
Xhjcn5 l89fyg<4> vssq v1yg vccq by73<4> cn4cm<4> jj2gv lmh4<4> kl8id v18jr m=8
.ends i8uv
** End of subcircuit definition.

** Library name: wgdhcu
** Cell name: jq2jj
** View name: wxatw
.subckt jq2jj b1r77<0> vss msw9c<4> cuu5s<2> vssq b1r77<1> lehf6<1> vccq b1r77<4> amrqqn
+ li3i2 msw9c<2> msw9c<0> vdd lehf6<0> msw9c<3> gs4i3y b1r77<2> cuu5s<0> o4wqa lehf6<2>
+ o9l5 bmsxl msw9c<1> pksyp cuu5s<1> b1r77<3>
Xzol5aw vccq qgqqq<2> vxf7<4> vdd vxf7<2> msw9c<2> b1r77<4> vxf7<3> amrqqn b1r77<0>
+ bmsxl gs4i3y vssq qgqqq<3> o4wqa vxf7<0> vss b1r77<3> msw9c<3> b1r77<2> li3i2 b1r77<1>
+ vxf7<1> msw9c<0> qgqqq<1> msw9c<1> msw9c<4> qgqqq<0> qgqqq<4> w4tk6
Xvr2h pksyp cuu5s<1> qgqqq<2> qgqqq<3> lehf6<1> qgqqq<0> vssq cuu5s<2> cuu5s<0> o9l5
+ qgqqq<4> vxf7<3> qgqqq<1> vccq vxf7<4> lehf6<0> vxf7<0> vxf7<2> lehf6<2> vxf7<1> fwhwl
.ends jq2jj
** End of subcircuit definition.

** Library name: ie6vq
** Cell name: qiex8
** View name: wxatw
.subckt qiex8 qhjzw yhliyw vss z3f38 vdd m45q
Cg5uj z3f38 vss 0.25p
Rb01jjf hb2uf jjh5 50k
Rzawg z7n3 m45q 50k
Xq12z ugr2g vdd vss hb2uf l5tu7
Cuujy z7n3 vss 0.5p
Xgyiz vss bgf4e yhliyw qhjzw vdd yavkxw
Cg6m5 jjh5 vss 0.5p
Xwkno4 hb2uf vdd vss bgf4e l5tu7
Ri19jcs jjh5 z3f38 50k
Ry89rft bgf4e z7n3 50k
Cra2xu m45q vss 0.25p
.ends qiex8
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: xz3c
** View name: wxatw
.subckt xz3c goo5 vdd vss eos5
Mu1m8 yem9g goo5 vdd vdd vw445g W=2.4u L=0.06u m=1 nf=4
Mh4mi eos5 yem9g vdd vdd vw445g W=9.6u L=0.06u m=1 nf=8
Mhj67m eos5 yem9g vss vss ns67 W=4.8u L=0.06u m=1 nf=8
Mopw1 yem9g goo5 vss vss ns67 W=1.2u L=0.06u m=1 nf=2
.ends xz3c
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: xbcz59
** View name: wxatw
.subckt xbcz59 hbl7f i2gg8v vss vdd pay7
Xgjmy vss nwllgn g2cx vdd yydl
Cpa0b14 gowsi vss 13f
Xd875 vss gowsi nwllgn vdd yydl
Xkr9os vss pay7 vdd g2cx hbl7f uye5vz
Cvz07s9 nwllgn vss 17f
Csd7h2m i2gg8v vss 5f
Xka9bp vss i2gg8v gowsi vdd yydl
.ends xbcz59
** End of subcircuit definition.

** Library name: ato68m
** Cell name: xoa6
** View name: wxatw
.subckt xoa6 ynj1co vdd nql66 vss r86k3 r9nk9 g6nmv
Xqk4fj vdd gmhk vss ynj1co kfwj
Mvg5u2y l0lwu r86k3 prq01t vdd vw445g W=1.2u L=0.06u m=1 nf=2
Xu70i g6nmv yo1jrm vss r9nk9 vdd bj6r
Mrahz0 yo1jrm r9nk9 prq01t vdd vw445g W=1.2u L=0.06u m=1 nf=2
Xmv1sm vdd prq01t vss gmhk kfwj
Xbt6aqi nql66 q10f vss r9nk9 vdd bj6r
Mht0l29 l0lwu r9nk9 prq01t vss ns67 W=0.8u L=0.06u m=1 nf=1
Xq0xp r9nk9 l0lwu q10f r86k3 vdd vss n26dpi
Mgle1 yo1jrm r86k3 prq01t vss ns67 W=0.8u L=0.06u m=1 nf=1
.ends xoa6
** End of subcircuit definition.

** Library name: fxoq
** Cell name: gja4
** View name: wxatw
.subckt gja4 vssq vccq vss vdd
Xp4tu vssq vccq so79m
Xq817 vssq vss epfg
Xu7002u vss vdd so79m
.ends gja4
** End of subcircuit definition.

** Library name: cyanj8
** Cell name: p7glz
** View name: wxatw
.subckt p7glz rtpwb yim6 vss dzywsx mg5z23 vdd
Mzblkgt mg5z23 rtpwb uzuh5 vss ka1ebp W=0.6u L=0.06u m=1 nf=1
Mat188 mg5z23 rtpwb vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mwy7am mg5z23 dzywsx vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mpyh62 mg5z23 yim6 vdd vdd ad57k3 W=0.4u L=0.06u m=1 nf=1
Mwerwu z32ps dzywsx vss vss ka1ebp W=0.6u L=0.06u m=1 nf=1
Mjfo5d uzuh5 yim6 z32ps vss ka1ebp W=0.6u L=0.06u m=1 nf=1
.ends p7glz
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: xeip
** View name: wxatw
.subckt xeip k1rmky rwbe oq6t jxah5g ud2h jjezn vdd lpksua e791n vss
Xri471 vdd vss jjezn k1rmky q8t9
Xlejs vss e791n oq6t rwbe lwzwvs ud2h vdd kr7x
Xjf2rk vss lpksua tv4b3j vdd yydl
Xj41x0 vss k1rmky s7ww vdd yydl
Xjco9 tv4b3j vss lwzwvs vdd jxah5g s7ww tv4b3j zuhc6m
.ends xeip
** End of subcircuit definition.

** Library name: zn2ats
** Cell name: edau8i
** View name: wxatw
.subckt edau8i to2mwe k3s6f vccq vssq vdd vss
Mq5ym6p biwe7 k3s6f vccq vccq ycgzf W=2u L=0.2u m=1 nf=1
Mzwmh biwe7 k3s6f vssq vssq jil3gy W=1u L=0.2u m=1 nf=1
Mp53l to2mwe biwe7 vdd vdd ycgzf W=3u L=0.2u m=1 nf=2
Mswdjq to2mwe biwe7 vss vss jil3gy W=1.5u L=0.2u m=1 nf=1
.ends edau8i
** End of subcircuit definition.

.END
