"""Layouts for rx_s1 (dq_rx_unit) — all 12 views."""
import json, sys, re
from netlist import parse, num, fmt_si
from scene import (
    View, BLACK, GRAY, SYM_W, CLK_W, pin, rail, gnd, vdd_tee, offpage,
    mos, res, cap, inv, box, tri, gray_gate
)

def gnd_at(V, x, y, net='VSS', l=12):
    V.wire([(x, y), (x, y + l)], cls='power')
    gnd(V, x, y + l, net)

def vdd_at(V, x, y, net='VDD', l=12):
    V.wire([(x, y), (x, y - l)], cls='power')
    vdd_tee(V, x, y - l, net)

def busslash(V, x, y, name, n, vertical=True):
    V.line([(x - 7, y + 7), (x + 7, y - 7)], w=1.4, owner='bus')
    if re.search(r'<\d+:\d+>', name):
        return
    if vertical:
        V.text(x + 9, y + 4, str(n), size=10, anchor='start', cls='buswidth')
    else:
        V.text(x, y + 16, str(n), size=10, anchor='middle', cls='buswidth')

W = sys.argv[1] if len(sys.argv) > 1 else '.'
NL = sys.argv[2] if len(sys.argv) > 2 else '../../input/netlist.sp'
cells, _ = parse(NL)
VIEWS = []

def el(c, name):
    return [e for e in cells[c]['elems'] if e['name'] == name][0]

def wl(c, name):
    e = el(c, name)
    p = e.get('params', {})
    w_val = p.get('w', e.get('w', ''))
    l_val = p.get('l', e.get('l', ''))
    m_val = p.get('m', '1')
    s = f"{fmt_si(w_val)}/{fmt_si(l_val)}"
    if m_val and m_val != '1':
        s += f" ×{m_val}"
    return s

def mosT(c, name):
    e = el(c, name)
    is_pmos = (e['type'] == 'p')
    top_term = 's' if is_pmos else 'd'
    bot_term = 'd' if is_pmos else 's'
    top = [[(name, top_term)]]
    bot = [[(name, bot_term)]]
    g = [[(name, 'g')]]
    return top, bot, g

def new_view(sid, cell, level, title, w, h):
    V = View(sid, cell, level, title, w=w, h=h)
    VIEWS.append(V)
    return V

# =============================================================================
# 1. VIEW_INV: u_inv (inv_a)
# =============================================================================
def view_inv():
    cell = 'inv_a'
    V = new_view('u_inv', cell, 'unit', f'{cell} — unit level (인버터)', 480, 400)
    rail(V, 80, 400, 70, 'vdd', 'VDD')
    rail(V, 80, 400, 330, 'vss', 'VSS')

    X = 240
    tp, bp, gp = mosT(cell, 'mp0')
    mos(V, 'mp0', X, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp, bp, gp, members=['mp0'])
    V.wire([(X, 110), (X, 70)], cls='power'); V.dot(X, 70)

    tn, bn, gn = mosT(cell, 'mn0')
    mos(V, 'mn0', X, 260, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn, bn, gn, members=['mn0'])
    V.wire([(X, 290), (X, 330)], cls='power'); V.dot(X, 330)

    V.wire([(X - 40, 140), (X - 40, 260)], cls='data')
    V.wire([(120, 200), (X - 40, 200)], cls='data'); V.dot(X - 40, 200)
    V.port('a', 120, 200, d='right', io='in')

    V.wire([(X, 170), (X, 230)], cls='data'); V.dot(X, 200)
    V.wire([(X, 200), (360, 200)], cls='data')
    V.port('y', 360, 200, d='right', io='out')

    V.omitted = []
    return V

# =============================================================================
# 2. VIEW_NAND: u_nand (nand2_a)
# =============================================================================
def view_nand():
    cell = 'nand2_a'
    V = new_view('u_nand', cell, 'unit', f'{cell} — unit level (2입력 NAND)', 580, 460)
    rail(V, 80, 500, 70, 'vdd', 'VDD')
    rail(V, 80, 500, 390, 'vss', 'VSS')

    LP, RP = 220, 340
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', LP, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(LP, 110), (LP, 70)], cls='power'); V.dot(LP, 70)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', RP, 140, 'p', 'right', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(RP, 110), (RP, 70)], cls='power'); V.dot(RP, 70)

    # Output node y
    V.wire([(LP, 170), (LP, 200), (RP, 200), (RP, 170)], cls='data')
    V.wire([(RP, 200), (440, 200)], cls='data'); V.dot(RP, 200)
    V.port('y', 440, 200, d='right', io='out')

    # Series NMOS: mn0 (top) at RP, y=260; mn1 (bot) at RP, y=340
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', RP, 260, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(RP, 200), (RP, 230)], cls='data') # connects y to mn0.d

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', RP, 340, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(RP, 290), (RP, 310)], cls='plain') # net5
    V.wire([(RP, 370), (RP, 390)], cls='power'); V.dot(RP, 390)

    # Input a: connects mp0.g (LP-40, 140) and mn0.g (RP-40, 260)
    V.wire([(120, 140), (LP - 40, 140)], cls='data'); V.dot(LP - 40, 140)
    V.wire([(LP - 40, 140), (LP - 40, 260), (RP - 40, 260)], cls='data')
    V.port('a', 120, 140, d='right', io='in')

    # Input b: connects mp1.g (RP+40, 140) and mn1.g (RP-40, 340)
    V.wire([(120, 340), (RP - 40, 340)], cls='data')
    V.port('b', 120, 340, d='right', io='in')
    V.wire([(160, 340), (160, 280), (RP + 60, 280), (RP + 60, 140), (RP + 40, 140)], cls='data')
    V.dot(160, 340)

    V.omitted = []
    return V

# =============================================================================
# 3. VIEW_NOR: u_nor (nor2_c)
# =============================================================================
def view_nor():
    cell = 'nor2_c'
    V = new_view('u_nor', cell, 'unit', f'{cell} — unit level (2입력 NOR)', 580, 480)
    rail(V, 80, 500, 70, 'vdd', 'VDD')
    rail(V, 80, 500, 410, 'vss', 'VSS')

    XP = 240
    # Series PMOS: mp0 (top) at XP, 140; mp1 (bot) at XP, 220
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', XP, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(XP, 110), (XP, 70)], cls='power'); V.dot(XP, 70)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', XP, 220, 'p', 'left', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(XP, 170), (XP, 190)], cls='plain') # net5

    # Parallel NMOS: mn0 at LN=XP, 320; mn1 at RN=360, 320
    LN, RN = XP, 360
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', LN, 320, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(LN, 350), (LN, 410)], cls='power'); V.dot(LN, 410)

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', RN, 320, 'n', 'right', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(RN, 350), (RN, 410)], cls='power'); V.dot(RN, 410)

    # Output node y
    V.wire([(XP, 250), (XP, 290)], cls='data'); V.dot(XP, 270)
    V.wire([(XP, 270), (RN, 270), (RN, 290)], cls='data')
    V.wire([(RN, 270), (460, 270)], cls='data'); V.dot(RN, 270)
    V.port('y', 460, 270, d='right', io='out')

    # Input a: mp0.g (XP-40, 140) and mn0.g (LN-40, 320)
    # Route at x=180 to avoid mp1.g at (200, 220)
    V.port('a', 120, 140, d='right', io='in')
    V.wire([(120, 140), (XP - 40, 140)], cls='data'); V.dot(180, 140)
    V.wire([(180, 140), (180, 320), (LN - 40, 320)], cls='data')

    # Input b: mp1.g (XP-40, 220) and mn1.g (RN+40, 320)
    V.port('b', 120, 220, d='right', io='in')
    V.wire([(120, 220), (XP - 40, 220)], cls='data'); V.dot(150, 220)
    V.wire([(150, 220), (150, 380), (RN + 40, 380), (RN + 40, 320)], cls='data')

    V.omitted = []
    return V

# =============================================================================
# 4. VIEW_LS: u_ls (ls_lh)
# =============================================================================
def view_ls():
    cell = 'ls_lh'
    V = new_view('u_ls', cell, 'unit', f'{cell} — unit level (레벨 시프터)', 780, 520)
    rail(V, 80, 260, 70, 'vdd', 'VDD')
    rail(V, 300, 700, 70, 'vddq', 'VDDQ')

    # Input inverter (mp2, mn2)
    t2, b2, g2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 180, 140, 'p', 'left', 'mp2', wl(cell, 'mp2'), t2, b2, g2, members=['mp2'])
    V.wire([(180, 110), (180, 70)], cls='power'); V.dot(180, 70)

    t2n, b2n, g2n = mosT(cell, 'mn2')
    mos(V, 'mn2', 180, 260, 'n', 'left', 'mn2', wl(cell, 'mn2'), t2n, b2n, g2n, members=['mn2'])
    gnd_at(V, 180, 290, 'vss')

    # Input wire: (80, 200) -> (140, 200) -> joins gate vertical segment (140, 140) to (140, 260)
    V.port('in', 80, 200, d='right', io='in')
    V.wire([(80, 200), (140, 200)], cls='data')
    V.wire([(140, 140), (140, 260)], cls='data'); V.dot(140, 200)

    # Branch to mn0.g (320, 280) taps from (120, 200)
    V.wire([(120, 200), (120, 350), (320, 350), (320, 280)], cls='data'); V.dot(120, 200)

    # Inverter output inb (180, 200)
    V.wire([(180, 170), (180, 230)], cls='plain'); V.dot(180, 200)
    # inb to mn1.g (520, 280)
    V.wire([(180, 200), (240, 200), (240, 370), (520, 370), (520, 280)], cls='plain')

    # Cross-coupled pair: mp0 (left), mp1 (right)
    L, R = 360, 480
    t0p, b0p, g0p = mosT(cell, 'mp0')
    mos(V, 'mp0', L, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), t0p, b0p, g0p, members=['mp0'])
    V.wire([(L, 110), (L, 70)], cls='power'); V.dot(L, 70)

    t1p, b1p, g1p = mosT(cell, 'mp1')
    mos(V, 'mp1', R, 140, 'p', 'right', 'mp1', wl(cell, 'mp1'), t1p, b1p, g1p, members=['mp1'])
    V.wire([(R, 110), (R, 70)], cls='power'); V.dot(R, 70)

    t0n, b0n, g0n = mosT(cell, 'mn0')
    mos(V, 'mn0', L, 280, 'n', 'left', 'mn0', wl(cell, 'mn0'), t0n, b0n, g0n, members=['mn0'])
    gnd_at(V, L, 310, 'vss')

    t1n, b1n, g1n = mosT(cell, 'mn1')
    mos(V, 'mn1', R, 280, 'n', 'right', 'mn1', wl(cell, 'mn1'), t1n, b1n, g1n, members=['mn1'])
    gnd_at(V, R, 310, 'vss')

    # Drains nb (L) and nq (R)
    V.wire([(L, 170), (L, 250)], cls='plain') # nb
    V.wire([(R, 170), (R, 250)], cls='plain') # nq

    # Cross-coupling: nb taps at (L, 180) -> (520, 180) -> (520, 140) = mp1.g
    V.wire([(L, 180), (520, 180), (520, 140)], cls='plain'); V.dot(L, 180)
    # nq taps at (R, 230) -> (320, 230) -> (320, 140) = mp0.g
    V.wire([(R, 230), (320, 230), (320, 140)], cls='plain'); V.dot(R, 230)

    # Output inverter (mp3, mn3) driven by nb from (520, 180)
    OX = 620
    t3p, b3p, g3p = mosT(cell, 'mp3')
    mos(V, 'mp3', OX, 140, 'p', 'left', 'mp3', wl(cell, 'mp3'), t3p, b3p, g3p, members=['mp3'])
    V.wire([(OX, 110), (OX, 70)], cls='power'); V.dot(OX, 70)

    t3n, b3n, g3n = mosT(cell, 'mn3')
    mos(V, 'mn3', OX, 280, 'n', 'left', 'mn3', wl(cell, 'mn3'), t3n, b3n, g3n, members=['mn3'])
    gnd_at(V, OX, 310, 'vss')

    # Connect nb to mp3.g (580, 140) and mn3.g (580, 280) via vertical trunk at x=560
    V.wire([(520, 180), (560, 180)], cls='plain'); V.dot(520, 180)
    V.wire([(560, 140), (560, 280)], cls='plain'); V.dot(560, 180)
    V.wire([(560, 140), (580, 140)], cls='plain')
    V.wire([(560, 280), (580, 280)], cls='plain')

    # Output 'out'
    V.wire([(OX, 170), (OX, 250)], cls='data'); V.dot(OX, 210)
    V.wire([(OX, 210), (720, 210)], cls='data')
    V.port('out', 720, 210, d='right', io='out')

    V.omitted = []
    return V

# =============================================================================
# 5. VIEW_SR_NOR: u_sr_nor (sr_nor)
# =============================================================================
def view_sr_nor():
    cell = 'sr_nor'
    V = new_view('u_sr_nor', cell, 'unit', f'{cell} — unit level (SR 래치)', 660, 480)
    # Netlist: xi0 r qb q vdd vss nor2_c
    #          xi1 s q qb vdd vss nor2_c
    box(V, 'xi0', 240, 120, 120, 70, 'NOR2', 'xi0',
        left=[('a', 140, [[('xi0', 'a')]]), ('b', 170, [[('xi0', 'b')]])],
        right=[('y', 155, [[('xi0', 'y')]])], members=['xi0'])
    box(V, 'xi1', 240, 270, 120, 70, 'NOR2', 'xi1',
        left=[('b', 290, [[('xi1', 'b')]]), ('a', 320, [[('xi1', 'a')]])],
        right=[('y', 305, [[('xi1', 'y')]])], members=['xi1'])

    V.port('r', 120, 140, d='right', io='in')
    V.wire([(120, 140), (220, 140)], cls='data')
    V.port('s', 120, 320, d='right', io='in')
    V.wire([(120, 320), (220, 320)], cls='data')

    V.wire([(380, 155), (500, 155)], cls='data'); V.dot(420, 155)
    V.port('q', 500, 155, d='right', io='out')

    V.wire([(380, 305), (500, 305)], cls='data'); V.dot(440, 305)
    V.port('qb', 500, 305, d='right', io='out')

    V.wire([(420, 155), (420, 220), (180, 220), (180, 290), (220, 290)], cls='plain')
    V.wire([(440, 305), (440, 240), (160, 240), (160, 170), (220, 170)], cls='plain')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}
    ]
    return V

# =============================================================================
# 6. VIEW_CK_GBUF: u_ck_gbuf (ck_gbuf)
# =============================================================================
def view_ck_gbuf():
    cell = 'ck_gbuf'
    V = new_view('u_ck_gbuf', cell, 'unit', f'{cell} — unit level (클럭 게이팅 버퍼)', 700, 480)
    box(V, 'xi0', 220, 110, 110, 60, 'NAND2', 'xi0',
        left=[('a', 125, [[('xi0', 'a')]], 'clock'), ('b', 155, [[('xi0', 'b')]])],
        right=[('y', 140, [[('xi0', 'y')]])], members=['xi0'])
    box(V, 'xi2', 400, 110, 90, 60, 'INV', 'xi2',
        left=[('a', 140, [[('xi2', 'a')]])],
        right=[('y', 140, [[('xi2', 'y')]], 'clock')], members=['xi2'])

    box(V, 'xi1', 220, 270, 110, 60, 'NAND2', 'xi1',
        left=[('a', 285, [[('xi1', 'a')]], 'clock'), ('b', 315, [[('xi1', 'b')]])],
        right=[('y', 300, [[('xi1', 'y')]])], members=['xi1'])
    box(V, 'xi3', 400, 270, 90, 60, 'INV', 'xi3',
        left=[('a', 300, [[('xi3', 'a')]])],
        right=[('y', 300, [[('xi3', 'y')]], 'clock')], members=['xi3'])

    V.port('ck', 100, 125, d='right', io='in', cls='clock')
    V.wire([(100, 125), (200, 125)], cls='clock')
    V.port('ckb', 100, 285, d='right', io='in', cls='clock')
    V.wire([(100, 285), (200, 285)], cls='clock')

    V.port('en', 100, 220, d='right', io='in')
    V.wire([(100, 220), (160, 220)], cls='data')
    V.wire([(160, 155), (200, 155)], cls='data')
    V.wire([(160, 315), (200, 315)], cls='data')
    V.wire([(160, 155), (160, 315)], cls='data'); V.dot(160, 220)

    V.wire([(350, 140), (380, 140)], cls='clock'); V.netlabel('net70', 365, 140)
    V.wire([(510, 140), (580, 140)], cls='clock')
    V.port('cko', 580, 140, d='right', io='out', cls='clock')

    V.wire([(350, 300), (380, 300)], cls='clock'); V.netlabel('net71', 365, 300)
    V.wire([(510, 300), (580, 300)], cls='clock')
    V.port('ckob', 580, 300, d='right', io='out', cls='clock')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}
    ]
    return V

# =============================================================================
# 7. VIEW_ODT_DEC: u_odt_dec (odt_dec)
# =============================================================================
def view_odt_dec():
    cell = 'odt_dec'
    V = new_view('u_odt_dec', cell, 'unit', f'{cell} — unit level (ODT 디코더)', 780, 500)
    ys = [120, 240, 360]
    nands = ['xi0', 'xi1', 'xi2']
    lss = ['xi3', 'xi4', 'xi5']
    bits = ['0', '1', '2']
    nets = ['net22', 'net21', 'net20']

    V.port('odt_en', 80, 80, d='right', io='in')
    V.wire([(80, 80), (160, 80), (160, 370)], cls='data')
    V.dot(160, 130); V.dot(160, 250)

    for k in range(3):
        y = ys[k]
        ni, li = nands[k], lss[k]
        b = bits[k]
        netn = nets[k]

        box(V, ni, 220, y - 20, 110, 60, 'NAND2', ni,
            left=[('b', y - 10, [[(ni, 'b')]]), ('a', y + 10, [[(ni, 'a')]])],
            right=[('y', y, [[(ni, 'y')]])], members=[ni])

        box(V, li, 430, y - 20, 90, 60, 'LS', li,
            left=[('in', y, [[(li, 'in')]])],
            right=[('out', y, [[(li, 'out')]])], link='u_ls', members=[li])

        V.wire([(160, y + 10), (200, y + 10)], cls='data')
        V.port(f'rtt<{b}>', 80, y - 10, d='right', io='in')
        V.wire([(80, y - 10), (200, y - 10)], cls='data')

        V.wire([(350, y), (410, y)], cls='data')
        V.netlabel(netn, 380, y)

        V.wire([(540, y), (640, y)], cls='data')
        V.port(f'enb<{b}>', 640, y, d='right', io='out')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'},
        {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}
    ]
    return V

# =============================================================================
# 8. VIEW_TERM: u_term (esd_dq)
# =============================================================================
def view_term():
    cell = 'esd_dq'
    V = new_view('u_term', cell, 'unit', f'{cell} — unit level (종단 및 ESD)', 920, 600)
    rail(V, 80, 840, 80, 'vddq', 'VDDQ')
    rail(V, 80, 840, 520, 'vssq', 'VSSQ')

    y_pad = 280
    V.port('pad', 80, y_pad, d='right', io='in')
    V.port('pad_r', 840, y_pad, d='right', io='out')

    # Diodes d0, d1 at x=200
    V.wire([(80, y_pad), (320, y_pad)], cls='data')
    V.dot(200, y_pad)
    # d0
    V.wire([(200, y_pad), (200, 220)], cls='plain')
    V.poly([(190, 220), (210, 220), (200, 170)], fill='#fff', stroke=BLACK, owner='d0')
    V.line([(190, 170), (210, 170)], owner='d0')
    V.wire([(200, 170), (200, 80)], cls='power'); V.dot(200, 80)
    V.add_symbol('d0', 'diode', [[185, 165, 215, 225]], [pin('p', 200, 220, [[('d0', 'p')]]), pin('n', 200, 170, [[('d0', 'n')]])], members=['d0'])
    V.text(220, 195, 'd0', size=9, owner='d0')

    # d1
    V.wire([(200, y_pad), (200, 340)], cls='plain')
    V.poly([(190, 390), (210, 390), (200, 340)], fill='#fff', stroke=BLACK, owner='d1')
    V.line([(190, 340), (210, 340)], owner='d1')
    V.wire([(200, 390), (200, 520)], cls='power'); V.dot(200, 520)
    V.add_symbol('d1', 'diode', [[185, 335, 215, 395]], [pin('p', 200, 390, [[('d1', 'p')]]), pin('n', 200, 340, [[('d1', 'n')]])], members=['d1'])
    V.text(220, 365, 'd1', size=9, owner='d1')

    # Resistor r0 150 ohm horizontal
    res(V, 'r0', 350, y_pad, orient='h', name='r0', size=fmt_si(el(cell, 'r0')['value']),
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='above')

    # Node pad_r
    V.wire([(380, y_pad), (840, y_pad)], cls='data')
    V.dot(480, y_pad); V.dot(640, y_pad)

    # Diodes d2, d3 at x=480
    V.wire([(480, y_pad), (480, 220)], cls='plain')
    V.poly([(470, 220), (490, 220), (480, 170)], fill='#fff', stroke=BLACK, owner='d2')
    V.line([(470, 170), (490, 170)], owner='d2')
    V.wire([(480, 170), (480, 80)], cls='power'); V.dot(480, 80)
    V.add_symbol('d2', 'diode', [[465, 165, 495, 225]], [pin('p', 480, 220, [[('d2', 'p')]]), pin('n', 480, 170, [[('d2', 'n')]])], members=['d2'])
    V.text(500, 195, 'd2', size=9, owner='d2')

    V.wire([(480, y_pad), (480, 340)], cls='plain')
    V.poly([(470, 390), (490, 390), (480, 340)], fill='#fff', stroke=BLACK, owner='d3')
    V.line([(470, 340), (490, 340)], owner='d3')
    V.wire([(480, 390), (480, 520)], cls='power'); V.dot(480, 520)
    V.add_symbol('d3', 'diode', [[465, 335, 495, 395]], [pin('p', 480, 390, [[('d3', 'p')]]), pin('n', 480, 340, [[('d3', 'n')]])], members=['d3'])
    V.text(500, 365, 'd3', size=9, owner='d3')

    # Clamp NMOS mn0 at x=640
    t_, b_, g_ = mosT(cell, 'mn0')
    mos(V, 'mn0', 640, 380, 'n', gate='left', name='mn0', size=wl(cell, 'mn0'), top=t_, bot=b_, gterm=g_, members=['mn0'])
    V.wire([(640, y_pad), (640, 350)], cls='plain')
    V.wire([(640, 410), (640, 520)], cls='power'); V.dot(640, 520)

    # Gate resistor r1 10k
    res(V, 'r1', 580, 450, orient='v', name='r1', size=fmt_si(el(cell, 'r1')['value']),
        a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='left')
    V.wire([(600, 380), (580, 380), (580, 420)], cls='plain')
    V.wire([(580, 480), (580, 520)], cls='power'); V.dot(580, 520)

    V.omitted = []
    return V

# =============================================================================
# 9. VIEW_PRE: u_pre (rx_pre)
# =============================================================================
def view_pre():
    cell = 'rx_pre'
    V = new_view('u_pre', cell, 'unit', f'{cell} — unit level (CTLE 프리앰프)', 960, 680)
    rail(V, 140, 820, 80, 'vddq', 'VDDQ')
    rail(V, 140, 820, 600, 'vssq', 'VSSQ')

    L_COL, R_COL = 360, 600

    # Load resistors: r0 on left (outn), r1 on right (outp)
    res(V, 'r0', L_COL, 140, orient='v', name='r0', size=fmt_si(el(cell, 'r0')['value']),
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='left')
    V.wire([(L_COL, 110), (L_COL, 80)], cls='power'); V.dot(L_COL, 80)

    res(V, 'r1', R_COL, 140, orient='v', name='r1', size=fmt_si(el(cell, 'r1')['value']),
        a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='right')
    V.wire([(R_COL, 110), (R_COL, 80)], cls='power'); V.dot(R_COL, 80)

    # Drain rails: outn on left (L_COL), outp on right (R_COL)
    V.wire([(L_COL, 170), (L_COL, 250)], cls='data'); V.dot(L_COL, 220)
    V.wire([(R_COL, 170), (R_COL, 250)], cls='data'); V.dot(R_COL, 220)

    # Output ports
    V.wire([(L_COL, 220), (180, 220)], cls='data')
    V.port('outn', 180, 220, d='left', io='out')
    V.wire([(R_COL, 220), (780, 220)], cls='data')
    V.port('outp', 780, 220, d='right', io='out')

    # Main pair: mn0 (inp -> outn) on left, mn1 (vref -> outp) on right
    t0, b0, g0 = mosT(cell, 'mn0')
    mos(V, 'mn0', L_COL, 280, 'n', 'left', 'mn0', wl(cell, 'mn0'), t0, b0, g0, members=['mn0'])
    t1, b1, g1 = mosT(cell, 'mn1')
    mos(V, 'mn1', R_COL, 280, 'n', 'right', 'mn1', wl(cell, 'mn1'), t1, b1, g1, members=['mn1'])

    # Input ports
    # inp enters at y=240, jogs to (320, 240) then down to mn0.g (320, 280) to avoid mn4.g at (220, 280)
    V.port('inp', 140, 240, d='right', io='in')
    V.wire([(140, 240), (L_COL - 40, 240), (L_COL - 40, 280)], cls='data')
    # vref enters at y=240, jogs to (640, 240) then down to mn1.g (640, 280) to avoid mn5.g at (740, 280)
    V.port('vref', 820, 240, d='left', io='in')
    V.wire([(820, 240), (R_COL + 40, 240), (R_COL + 40, 280)], cls='data')

    # Main pair sources join at net40
    AX = 480
    V.wire([(L_COL, 310), (L_COL, 340), (R_COL, 340), (R_COL, 310)], cls='plain')
    V.dot(AX, 340)

    # Main tail mn2 (sel_m) & mn3 (vbn)
    t2, b2, g2 = mosT(cell, 'mn2')
    mos(V, 'mn2', AX, 400, 'n', 'left', 'mn2', wl(cell, 'mn2'), t2, b2, g2, members=['mn2'])
    V.wire([(AX, 340), (AX, 370)], cls='plain')

    t3, b3, g3 = mosT(cell, 'mn3')
    mos(V, 'mn3', AX, 500, 'n', 'left', 'mn3', wl(cell, 'mn3'), t3, b3, g3, members=['mn3'])
    V.wire([(AX, 430), (AX, 470)], cls='plain') # net41
    gnd_at(V, AX, 530, 'vssq')

    # Loopback pair mn4 (lbp -> outn), mn5 (lbn -> outp)
    LL, RR = 260, 700
    t4, b4, g4 = mosT(cell, 'mn4')
    mos(V, 'mn4', LL, 280, 'n', 'left', 'mn4', wl(cell, 'mn4'), t4, b4, g4, members=['mn4'])
    t5, b5, g5 = mosT(cell, 'mn5')
    mos(V, 'mn5', RR, 280, 'n', 'right', 'mn5', wl(cell, 'mn5'), t5, b5, g5, members=['mn5'])

    # Drains connect to outn at y=220 and outp at y=220
    V.wire([(LL, 250), (LL, 220)], cls='data'); V.dot(LL, 220)
    V.wire([(RR, 250), (RR, 220)], cls='data'); V.dot(RR, 220)

    V.port('lbp', 140, 280, d='right', io='in')
    V.wire([(140, 280), (LL - 40, 280)], cls='data')
    V.port('lbn', 820, 280, d='left', io='in')
    V.wire([(820, 280), (RR + 40, 280)], cls='data')

    # Sources of mn4, mn5 join at net42
    V.wire([(LL, 310), (LL, 360), (RR, 360), (RR, 310)], cls='plain')
    V.dot(AX - 80, 360)

    # Loopback tail mn6 (sel_l) & mn7 (vbn)
    t6, b6, g6 = mosT(cell, 'mn6')
    mos(V, 'mn6', AX - 80, 420, 'n', 'left', 'mn6', wl(cell, 'mn6'), t6, b6, g6, members=['mn6'])
    V.wire([(AX - 80, 360), (AX - 80, 390)], cls='plain')

    t7, b7, g7 = mosT(cell, 'mn7')
    mos(V, 'mn7', AX - 80, 500, 'n', 'left', 'mn7', wl(cell, 'mn7'), t7, b7, g7, members=['mn7'])
    V.wire([(AX - 80, 450), (AX - 80, 470)], cls='plain') # net43
    gnd_at(V, AX - 80, 530, 'vssq')

    # Select signals
    V.port('sel_m', 140, 400, d='right', io='in')
    V.wire([(140, 400), (AX - 40, 400)], cls='data')
    V.port('sel_l', 140, 420, d='right', io='in')
    V.wire([(140, 420), (AX - 80 - 40, 420)], cls='data')

    # vbn to mn3.g and mn7.g
    V.wire([(AX - 80 - 40, 500), (AX - 40, 500)], cls='plain')
    gray_gate(V, {'x': AX - 80 - 40, 'y': 500}, 'vbn', 'left')

    # MOS caps:
    # mn9: s/d outn at 390 (a), gate vref at 450 (b)
    cap(V, 'mn9', 420, 180, orient='h', name='mn9', size=wl(cell, 'mn9'),
        a=[[('mn9', 's')], [('mn9', 'd')]], b=[[('mn9', 'g')]], members=['mn9'], label_side='above')
    V.wire([(L_COL, 180), (390, 180)], cls='data'); V.dot(L_COL, 180)
    # vref gate wire routes at y=160
    V.wire([(450, 180), (450, 160), (640, 160), (640, 240)], cls='data'); V.dot(640, 240)

    # mn8: gate inp at 510 (a), s/d outp at 570 (b)
    cap(V, 'mn8', 540, 180, orient='h', name='mn8', size=wl(cell, 'mn8'),
        a=[[('mn8', 'g')]], b=[[('mn8', 's')], [('mn8', 'd')]], members=['mn8'], label_side='above')
    V.wire([(570, 180), (R_COL, 180)], cls='data'); V.dot(R_COL, 180)
    # inp gate wire routes at y=150 (completely clear of y=220 drain line)
    V.wire([(510, 180), (510, 150), (320, 150), (320, 240)], cls='data'); V.dot(320, 240)

    V.omitted = []
    return V

# =============================================================================
# 10. VIEW_DFE_SUM: u_dfe_sum (dfe_sum)
# =============================================================================
def view_dfe_sum():
    cell = 'dfe_sum'
    V = new_view('u_dfe_sum', cell, 'unit', f'{cell} — unit level (DFE 합산기)', 1060, 720)
    rail(V, 140, 920, 70, 'vdd', 'VDD')
    rail(V, 140, 920, 650, 'vss', 'VSS')

    L_COL, R_COL = 360, 680
    AX = 520

    # Load resistors: r0 on left (outn), r1 on right (outp)
    res(V, 'r0', L_COL, 130, orient='v', name='r0', size=fmt_si(el(cell, 'r0')['value']),
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='left')
    V.wire([(L_COL, 100), (L_COL, 70)], cls='power'); V.dot(L_COL, 70)

    res(V, 'r1', R_COL, 130, orient='v', name='r1', size=fmt_si(el(cell, 'r1')['value']),
        a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='right')
    V.wire([(R_COL, 100), (R_COL, 70)], cls='power'); V.dot(R_COL, 70)

    # Output rails: outn on left, outp on right
    V.wire([(L_COL, 160), (L_COL, 250)], cls='data'); V.dot(L_COL, 210)
    V.wire([(R_COL, 160), (R_COL, 250)], cls='data'); V.dot(R_COL, 210)

    V.wire([(L_COL, 210), (180, 210)], cls='data')
    V.port('outn', 180, 210, d='left', io='out')
    V.wire([(R_COL, 210), (860, 210)], cls='data')
    V.port('outp', 860, 210, d='right', io='out')

    # Main differential pair: mn0 (inp -> outn), mn1 (inn -> outp)
    t0, b0, g0 = mosT(cell, 'mn0')
    mos(V, 'mn0', L_COL, 280, 'n', 'left', 'mn0', wl(cell, 'mn0'), t0, b0, g0, members=['mn0'])
    t1, b1, g1 = mosT(cell, 'mn1')
    mos(V, 'mn1', R_COL, 280, 'n', 'right', 'mn1', wl(cell, 'mn1'), t1, b1, g1, members=['mn1'])

    # Ports inp, inn
    V.port('inp', 140, 280, d='right', io='in')
    V.wire([(140, 280), (L_COL - 40, 280)], cls='data')
    V.port('inn', 900, 280, d='left', io='in')
    V.wire([(900, 280), (R_COL + 40, 280)], cls='data')

    # Main pair sources join at net50
    MX = 400
    V.wire([(L_COL, 310), (L_COL, 340), (R_COL, 340), (R_COL, 310)], cls='plain')
    V.dot(MX, 340)

    # Main tail mn2 (en) & mn3 (vbn)
    t2, b2, g2 = mosT(cell, 'mn2')
    mos(V, 'mn2', MX, 400, 'n', 'left', 'mn2', wl(cell, 'mn2'), t2, b2, g2, members=['mn2'])
    V.wire([(MX, 340), (MX, 370)], cls='plain')

    t3, b3, g3 = mosT(cell, 'mn3')
    mos(V, 'mn3', MX, 500, 'n', 'left', 'mn3', wl(cell, 'mn3'), t3, b3, g3, members=['mn3'])
    V.wire([(MX, 430), (MX, 470)], cls='plain') # net51
    gnd_at(V, MX, 530, 'vss')

    # SGN_QUAD (steering switches mn6..mn9)
    # Left pin outn connects to outn (L_COL), right pin outp connects to outp (R_COL)
    box(V, 'SGN_QUAD', AX - 50, 220, 100, 60, 'STEER', None,
        left=[('outn', 240, [[('mn7', 'd')], [('mn8', 'd')]])],
        right=[('outp', 240, [[('mn6', 'd')], [('mn9', 'd')]])],
        top=[('sgn', AX - 20, [[('mn8', 'g')], [('mn9', 'g')]]), ('sgnb', AX + 20, [[('mn6', 'g')], [('mn7', 'g')]])],
        bottom=[('net52', AX - 25, [[('mn6', 's')], [('mn8', 's')]]), ('net53', AX + 25, [[('mn7', 's')], [('mn9', 's')]])],
        members=['mn6', 'mn7', 'mn8', 'mn9'])

    V.wire([(AX - 70, 240), (L_COL, 240)], cls='data'); V.dot(L_COL, 240)
    V.wire([(AX + 70, 240), (R_COL, 240)], cls='data'); V.dot(R_COL, 240)

    # Ports sgn, sgnb route at y=175 and y=190 (avoiding r1.B at 160!)
    V.port('sgn', 900, 175, d='left', io='in')
    V.wire([(900, 175), (AX - 20, 175), (AX - 20, 200)], cls='data')
    V.port('sgnb', 900, 190, d='left', io='in')
    V.wire([(900, 190), (AX + 20, 190), (AX + 20, 200)], cls='data')

    # Tap differential pair mn4 (hp -> net52), mn5 (hn -> net53)
    t4, b4, g4 = mosT(cell, 'mn4')
    mos(V, 'mn4', AX - 25, 360, 'n', 'left', 'mn4', wl(cell, 'mn4'), t4, b4, g4, members=['mn4'])
    t5, b5, g5 = mosT(cell, 'mn5')
    mos(V, 'mn5', AX + 25, 360, 'n', 'right', 'mn5', wl(cell, 'mn5'), t5, b5, g5, members=['mn5'])

    # Connect bottom leads of SGN_QUAD (at y=300) to drains of mn4, mn5 (at y=330)
    V.wire([(AX - 25, 300), (AX - 25, 330)], cls='plain')
    V.wire([(AX + 25, 300), (AX + 25, 330)], cls='plain')

    # Ports hp, hn
    V.port('hp', 140, 360, d='right', io='in')
    V.wire([(140, 360), (AX - 65, 360)], cls='data')
    V.port('hn', 900, 360, d='left', io='in')
    V.wire([(900, 360), (AX + 65, 360)], cls='data')

    # Sources of mn4, mn5 join to net54 at y=410
    V.wire([(AX - 25, 390), (AX - 25, 410), (AX + 25, 410), (AX + 25, 390)], cls='plain')
    V.dot(AX, 410)

    # IDAC 4-bit mn10..mn17
    # Note: slice terms listed LSB first: mn10, mn12, mn14, mn16 (bit 0 to bit 3)
    # Each bit is in its own slice [[(...)], [(...)]]!
    tap_slices = [[('mn16', 'g')], [('mn14', 'g')], [('mn12', 'g')], [('mn10', 'g')]]
    box(V, 'IDAC', AX - 60, 460, 120, 80, 'IDAC', None,
        top=[('net54', AX, [[('mn10', 'd')], [('mn12', 'd')], [('mn14', 'd')], [('mn16', 'd')]])],
        left=[('tap<3:0>', 480, tap_slices, 'bus'),
              ('vbn', 510, [[('mn11', 'g')], [('mn13', 'g')], [('mn15', 'g')], [('mn17', 'g')]])],
        bottom=[('vss', AX, [[('mn11', 's')], [('mn13', 's')], [('mn15', 's')], [('mn17', 's')]])],
        members=['mn10', 'mn11', 'mn12', 'mn13', 'mn14', 'mn15', 'mn16', 'mn17'])

    V.wire([(AX, 410), (AX, 440)], cls='plain')
    gnd_at(V, AX, 560, 'vss')

    # Port en
    V.port('en', 140, 400, d='right', io='in')
    V.wire([(140, 400), (MX - 40, 400)], cls='data')

    # Port tap<3:0> bus enters from left at y=480
    V.port('tap<3:0>', 140, 480, d='right', io='in', cls='bus')
    V.wire([(140, 480), (AX - 80, 480)], cls='bus')
    busslash(V, 200, 480, 'tap<3:0>', 4, vertical=True)

    # vbn to mn3.g (MX-40, 500) and IDAC.vbn (AX-80, 510)
    V.wire([(MX - 40, 500), (AX - 80, 500), (AX - 80, 510)], cls='plain')
    gray_gate(V, {'x': MX - 40, 'y': 500}, 'vbn', 'left')

    V.omitted = []
    return V

# =============================================================================
# 11. VIEW_SA_DT: u_sa_dt (sa_dt)
# =============================================================================
def view_sa_dt():
    cell = 'sa_dt'
    V = new_view('u_sa_dt', cell, 'unit', f'{cell} — unit level (StrongArm 감지 증폭기)', 1060, 720)
    AX = 530
    L_COL, R_COL = 380, 680
    rail(V, 140, 920, 70, 'vdd', 'VDD')
    rail(V, 140, 920, 640, 'vss', 'VSS')

    # Inverter xi0 (ck -> net60)
    inv(V, 'xi0', 180, 130, 'xi0', [[('xi0', 'a')]], [[('xi0', 'y')]], members=['xi0'])
    V.port('ck', 100, 130, d='right', io='in', cls='clock')
    V.wire([(100, 130), (160, 130)], cls='clock')

    # Clocked PMOS tail mp2 (net60)
    t2, b2, g2 = mosT(cell, 'mp2')
    mos(V, 'mp2', AX, 140, 'p', 'left', 'mp2', wl(cell, 'mp2'), t2, b2, g2, members=['mp2'])
    V.wire([(AX, 110), (AX, 70)], cls='power'); V.dot(AX, 70)
    V.wire([(242, 130), (AX - 40, 130), (AX - 40, 140)], cls='clock') # net60

    # Cross-coupled PMOS pair mp3, mp4 at y=230
    DL, DR = 450, 610
    t3, b3, g3 = mosT(cell, 'mp3')
    mos(V, 'mp3', DL, 230, 'p', 'left', 'mp3', wl(cell, 'mp3'), t3, b3, g3, members=['mp3'])
    t4, b4, g4 = mosT(cell, 'mp4')
    mos(V, 'mp4', DR, 230, 'p', 'right', 'mp4', wl(cell, 'mp4'), t4, b4, g4, members=['mp4'])

    # mp2 drain (net64) connects to sources of mp3, mp4
    V.wire([(AX, 170), (AX, 190)], cls='plain')
    V.wire([(DL, 190), (DR, 190)], cls='plain'); V.dot(AX, 190)
    V.wire([(DL, 190), (DL, 200)], cls='plain')
    V.wire([(DR, 190), (DR, 200)], cls='plain')

    # Cross-coupled NMOS pair mn3, mn4 at y=310
    t3n, b3n, g3n = mosT(cell, 'mn3')
    mos(V, 'mn3', DL, 310, 'n', 'left', 'mn3', wl(cell, 'mn3'), t3n, b3n, g3n, members=['mn3'])
    gnd_at(V, DL, 340, 'vss')

    t4n, b4n, g4n = mosT(cell, 'mn4')
    mos(V, 'mn4', DR, 310, 'n', 'right', 'mn4', wl(cell, 'mn4'), t4n, b4n, g4n, members=['mn4'])
    gnd_at(V, DR, 340, 'vss')

    # Output nodes: outp at DL, outn at DR
    V.wire([(DL, 260), (DL, 280)], cls='data'); V.dot(DL, 270)
    V.wire([(DR, 260), (DR, 280)], cls='data'); V.dot(DR, 270)

    # Cross-coupling
    V.wire([(DL, 270), (DL + 30, 270), (DL + 30, 245), (DR + 40, 245)], cls='data'); V.dot(DL, 270)
    V.wire([(DR + 40, 230), (DR + 40, 310)], cls='data'); V.dot(DR + 40, 245)
    V.wire([(DR, 270), (DR - 30, 270), (DR - 30, 295), (DL - 40, 295)], cls='data'); V.dot(DR, 270)
    V.wire([(DL - 40, 230), (DL - 40, 310)], cls='data'); V.dot(DL - 40, 295)

    # Output ports
    V.wire([(DL, 270), (DL - 60, 270), (DL - 60, 210), (140, 210)], cls='data'); V.dot(DL - 60, 270)
    V.port('outp', 140, 210, d='left', io='out')
    V.wire([(DR, 270), (DR + 60, 270), (DR + 60, 210), (920, 210)], cls='data'); V.dot(DR + 60, 270)
    V.port('outn', 920, 210, d='right', io='out')

    # Intermediate drive NMOS mn5 (d=outp, g=net62), mn6 (d=outn, g=net63)
    t5n, b5n, g5n = mosT(cell, 'mn5')
    mos(V, 'mn5', L_COL, 310, 'n', 'left', 'mn5', wl(cell, 'mn5'), t5n, b5n, g5n, members=['mn5'])
    gnd_at(V, L_COL, 340, 'vss')
    V.wire([(L_COL, 280), (L_COL, 270), (DL, 270)], cls='data')

    t6n, b6n, g6n = mosT(cell, 'mn6')
    mos(V, 'mn6', R_COL, 310, 'n', 'right', 'mn6', wl(cell, 'mn6'), t6n, b6n, g6n, members=['mn6'])
    gnd_at(V, R_COL, 340, 'vss')
    V.wire([(R_COL, 280), (R_COL, 270), (DR, 270)], cls='data')

    # Precharge PMOS mp0, mp1 (ck)
    t0p, b0p, g0p = mosT(cell, 'mp0')
    mos(V, 'mp0', L_COL, 400, 'p', 'left', 'mp0', wl(cell, 'mp0'), t0p, b0p, g0p, members=['mp0'])
    vdd_at(V, L_COL, 370, 'vdd')

    t1p, b1p, g1p = mosT(cell, 'mp1')
    mos(V, 'mp1', R_COL, 400, 'p', 'right', 'mp1', wl(cell, 'mp1'), t1p, b1p, g1p, members=['mp1'])
    vdd_at(V, R_COL, 370, 'vdd')

    # Differential input pair mn1, mn2
    t1n, b1n, g1n = mosT(cell, 'mn1')
    mos(V, 'mn1', L_COL, 480, 'n', 'left', 'mn1', wl(cell, 'mn1'), t1n, b1n, g1n, members=['mn1'])
    t2n, b2n, g2n = mosT(cell, 'mn2')
    mos(V, 'mn2', R_COL, 480, 'n', 'right', 'mn2', wl(cell, 'mn2'), t2n, b2n, g2n, members=['mn2'])

    # Node net62 at L_COL, net63 at R_COL
    V.wire([(L_COL, 430), (L_COL, 450)], cls='plain'); V.dot(L_COL, 440)
    V.wire([(R_COL, 430), (R_COL, 450)], cls='plain'); V.dot(R_COL, 440)

    # Route net62 and net63 cleanly without overlapping gate plates or symbol strokes!
    # net62 routes via x=330, connecting mn1.T/mp0.B (L_COL, 440), OFN_DAC right pin (330, 340), and mn5.G (340, 310)
    V.wire([(L_COL, 440), (330, 440), (330, 340)], cls='plain')
    V.wire([(330, 340), (330, 310), (L_COL - 40, 310)], cls='plain')
    V.dot(330, 340)

    # net63 routes via x=730, connecting mn2.T/mp1.B (R_COL, 440), OFP_DAC left pin (730, 340), and mn6.G (720, 310)
    V.wire([(R_COL, 440), (730, 440), (730, 340)], cls='plain')
    V.wire([(730, 340), (730, 310), (R_COL + 40, 310)], cls='plain')
    V.dot(730, 340)

    # Input ports inp, inn
    V.port('inp', 140, 480, d='right', io='in')
    V.wire([(140, 480), (L_COL - 40, 480)], cls='data')
    V.port('inn', 920, 480, d='left', io='in')
    V.wire([(920, 480), (R_COL + 40, 480)], cls='data')

    # Tail mn0
    t0n, b0n, g0n = mosT(cell, 'mn0')
    mos(V, 'mn0', AX, 560, 'n', 'left', 'mn0', wl(cell, 'mn0'), t0n, b0n, g0n, members=['mn0'])
    V.wire([(L_COL, 510), (L_COL, 530), (AX, 530)], cls='plain')
    V.wire([(R_COL, 510), (R_COL, 530), (AX, 530)], cls='plain')
    V.dot(AX, 530)
    gnd_at(V, AX, 590, 'vss')

    # Clock to mp0, mp1, mn0 (route down x=80, tap to mp0.g, down to 620, across to 880, tap to mn0.g, up to mp1.g)
    V.wire([(100, 130), (80, 130), (80, 400)], cls='clock'); V.dot(80, 400)
    V.wire([(80, 400), (L_COL - 40, 400)], cls='clock')
    V.wire([(80, 400), (80, 620), (880, 620), (880, 400), (R_COL + 40, 400)], cls='clock')
    V.wire([(AX - 40, 620), (AX - 40, 560)], cls='clock'); V.dot(AX - 40, 620)

    # Offset DACs OFN (mn7..mn10) and OFP (mn11..mn14)
    # y0=320, h=40 -> right pin net62 at 340, left pin vss at (210, 340)
    box(V, 'OFN_DAC', L_COL - 150, 320, 80, 40, 'OFN', None,
        right=[('net62', 340, [[('mn7', 'd')], [('mn9', 'd')]])],
        left=[('vss', 340, [[('mn8', 's')], [('mn10', 's')]])],
        members=['mn7', 'mn8', 'mn9', 'mn10'])
    gnd_at(V, L_COL - 170, 340, 'vss', l=0)

    # y0=320, h=40 -> left pin net63 at 340, right pin vss at (870, 340)
    box(V, 'OFP_DAC', R_COL + 70, 320, 80, 40, 'OFP', None,
        left=[('net63', 340, [[('mn11', 'd')], [('mn13', 'd')]])],
        right=[('vss', 340, [[('mn12', 's')], [('mn14', 's')]])],
        members=['mn11', 'mn12', 'mn13', 'mn14'])
    gnd_at(V, R_COL + 170, 340, 'vss', l=0)

    V.allowed_cross = [
        {'at': [330, 400], 'reason': 'ck to mp0 crosses net62'},
        {'at': [730, 400], 'reason': 'ck to mp1 crosses net63'}
    ]
    V.omitted = [
        {'net': 'ofn<1:0>', 'class': '일반 제어'},
        {'net': 'ofp<1:0>', 'class': '일반 제어'}
    ]
    return V

# =============================================================================
# 12. VIEW_TOP: b_top (dq_rx_unit)
# =============================================================================
def view_top():
    cell = 'dq_rx_unit'
    V = new_view('b_top', cell, 'block', f'{cell} — 블록 레벨 (최상위)', 1580, 920)

    for p in ('ofe_p<1:0>', 'ofe_n<1:0>', 'ofo_p<1:0>', 'ofo_n<1:0>'):
        V.omitted.append({'net': p, 'class': '일반 제어 (K7)'})
    V.omitted.append({'net': 'ibias', 'class': '바이어스'})
    V.omitted.append({'net': 'net4', 'class': '바이어스'})
    for p in ('vdd', 'vddq', 'vss'):
        V.omitted.append({'net': p, 'class': '전원'})
    V.omitted.append({'block': 'xi23', 'cell': 'rx_bias', 'class': 'bias', 'reason': '바이어스 발생기 (고속 경로 밖)'})

    # Pad input & termination
    y_pad = 260
    V.port('pad', 80, y_pad, d='right', io='in')
    V.wire([(80, y_pad), (140, y_pad)], cls='data')

    box(V, 'xi20', 160, y_pad - 25, 70, 50, 'ESD', 'xi20',
        left=[('pad', y_pad, [[('xi20', 'pad')]])],
        right=[('pad_r', y_pad, [[('xi20', 'pad_r')]])], link='u_term', members=['xi20'])

    enb_slices = [[('xi21', f'enb<{i}>')] for i in range(3)]
    box(V, 'xi21', 160, y_pad - 120, 70, 50, 'ODT', 'xi21',
        bottom=[('pad', 195, [[('xi21', 'pad')]])],
        left=[('enb<2:0>', y_pad - 95, enb_slices, 'bus')],
        link='u_term', members=['xi21'])
    V.wire([(140, y_pad), (140, y_pad - 50), (195, y_pad - 50)], cls='data'); V.dot(140, y_pad)

    rtt_slices = [[('xi22', f'rtt<{i}>')] for i in range(3)]
    enb_dec_slices = [[('xi22', f'enb<{i}>')] for i in range(3)]
    box(V, 'xi22', 80, y_pad - 230, 90, 60, 'DEC', 'xi22',
        left=[('odt_en', y_pad - 215, [[('xi22', 'odt_en')]]),
              ('rtt<2:0>', y_pad - 195, rtt_slices, 'bus')],
        right=[('enb<2:0>', y_pad - 205, enb_dec_slices, 'bus')],
        link='u_odt_dec', members=['xi22'])

    V.port('odt_en', 40, y_pad - 215, d='right', io='in')
    V.wire([(40, y_pad - 215), (60, y_pad - 215)], cls='data')
    V.port('rtt<2:0>', 40, y_pad - 195, d='right', io='in', cls='bus')
    V.wire([(40, y_pad - 195), (60, y_pad - 195)], cls='bus')
    busslash(V, 50, y_pad - 195, 'rtt<2:0>', 3, vertical=True)

    V.wire([(190, y_pad - 205), (230, y_pad - 205), (230, y_pad - 95), (140, y_pad - 95)], cls='bus')
    V.netlabel('net2<2:0>', 230, y_pad - 150)
    busslash(V, 230, y_pad - 150, 'net2<2:0>', 3, vertical=True)

    V.wire([(250, y_pad), (340, y_pad)], cls='data')
    V.netlabel('net1', 290, y_pad)

    # VREF filter: r0 (5k), mn0 (clamp/cap to vssq)
    # r0 centered at 170: pin A is at 140, pin B is at 200
    y_vref = 340
    V.port('vref', 80, y_vref, d='right', io='in')
    V.wire([(80, y_vref), (140, y_vref)], cls='data')
    res(V, 'r0', 170, y_vref, orient='h', name='r0', size=fmt_si(el(cell, 'r0')['value']),
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='above')

    t_m0, b_m0, g_m0 = mosT(cell, 'mn0')
    # Place mn0 at x=280, cy=300
    # Netlist: mn0 vssq net3 vssq vssq -> D=vssq (top at 270), G=net3 (left at 240, 300), S=vssq (bot at 330)
    mos(V, 'mn0', 280, 300, 'n', 'left', 'mn0', wl(cell, 'mn0'), t_m0, b_m0, g_m0, members=['mn0'])
    V.wire([(200, y_vref), (340, y_vref)], cls='data'); V.dot(240, y_vref)
    V.wire([(240, y_vref), (240, 300)], cls='plain') # net3 to mn0.g (left at 240, 300)
    # mn0.T (top at 270) and mn0.B (bot at 330) to vssq
    V.wire([(280, 330), (300, 330), (300, 270), (280, 270)], cls='power')
    V.wire([(300, 270), (300, 250)], cls='power'); gnd(V, 300, 250, 'vssq'); V.dot(300, 270)
    V.netlabel('net3', 310, y_vref)

    # PREAMP (xi24)
    box(V, 'xi24', 360, 240, 120, 220, 'PREAMP', 'xi24',
        left=[('inp', 260, [[('xi24', 'inp')]], 'data'),
              ('vref', 340, [[('xi24', 'vref')]], 'data'),
              ('lbp', 380, [[('xi24', 'lbp')]], 'data'),
              ('lbn', 400, [[('xi24', 'lbn')]], 'data'),
              ('sel_m', 420, [[('xi24', 'sel_m')]]),
              ('sel_l', 440, [[('xi24', 'sel_l')]])],
        right=[('outp', 290, [[('xi24', 'outp')]], 'data'),
               ('outn', 330, [[('xi24', 'outn')]], 'data')],
        link='u_pre', members=['xi24'])

    V.port('lb_p', 80, 380, d='right', io='in')
    V.wire([(80, 380), (340, 380)], cls='data')
    V.port('lb_n', 80, 400, d='right', io='in')
    V.wire([(80, 400), (340, 400)], cls='data')

    # Mode decoder logic: xi0..xi4
    box(V, 'MODE_DEC', 160, 500, 90, 70, 'MODE', None,
        left=[('rx_en', 520, [[('xi1', 'a')], [('xi3', 'a')]]),
              ('lb_en', 550, [[('xi0', 'a')], [('xi3', 'b')]])],
        right=[('sel_m', 520, [[('xi2', 'y')]]),
               ('sel_l', 550, [[('xi4', 'y')]])],
        members=['xi0', 'xi1', 'xi2', 'xi3', 'xi4'])

    V.port('rx_en', 80, 520, d='right', io='in')
    V.wire([(80, 520), (140, 520)], cls='data')
    V.port('lb_en', 80, 550, d='right', io='in')
    V.wire([(80, 550), (140, 550)], cls='data')

    # Connect MODE_DEC outputs (y=520, y=550) to xi24 inputs (y=420, y=440)
    V.wire([(270, 520), (300, 520), (300, 420), (340, 420)], cls='data'); V.netlabel('net102', 290, 520)
    V.wire([(270, 550), (320, 550), (320, 440), (340, 440)], cls='data'); V.netlabel('net104', 290, 550)

    # CK_BUF (xi25)
    box(V, 'xi25', 360, 680, 120, 80, 'CK_BUF', 'xi25',
        left=[('ck', 700, [[('xi25', 'ck')]], 'clock'),
              ('ckb', 720, [[('xi25', 'ckb')]], 'clock'),
              ('en', 740, [[('xi25', 'en')]])],
        right=[('cko', 700, [[('xi25', 'cko')]], 'clock'),
               ('ckob', 720, [[('xi25', 'ckob')]], 'clock')],
        link='u_ck_gbuf', members=['xi25'])

    V.port('ck', 80, 700, d='right', io='in', cls='clock')
    V.wire([(80, 700), (340, 700)], cls='clock')
    V.port('ckb', 80, 720, d='right', io='in', cls='clock')
    V.wire([(80, 720), (340, 720)], cls='clock')

    # rx_en branch to CK_BUF.en
    V.wire([(110, 520), (110, 740), (340, 740)], cls='data'); V.dot(110, 520)

    # SGN_BUF (xi5, xi6)
    box(V, 'xi5_6', 360, 580, 110, 50, 'SGN_BUF', None,
        left=[('tap_sgn', 600, [[('xi5', 'a')]])],
        right=[('sgn', 595, [[('xi6', 'y')]]), ('sgnb', 615, [[('xi5', 'y'), ('xi6', 'a')]])],
        members=['xi5', 'xi6'])
    V.port('tap_sgn', 80, 600, d='right', io='in')
    V.wire([(80, 600), (340, 600)], cls='data')

    # Summer outputs net6, net7
    V.wire([(500, 290), (540, 290)], cls='data'); V.netlabel('net6', 510, 290)
    V.wire([(500, 330), (540, 330)], cls='data'); V.netlabel('net7', 510, 330)

    SUM_W, SUM_H = 130, 150
    # Even Summer xi26
    tap26_slices = [[('xi26', f'tap<{i}>')] for i in range(4)]
    box(V, 'xi26', 600, 220, SUM_W, SUM_H, 'Σ', 'xi26',
        left=[('inp', 250, [[('xi26', 'inp')]], 'data'),
              ('inn', 270, [[('xi26', 'inn')]], 'data'),
              ('hp', 300, [[('xi26', 'hp')]], 'data'),
              ('hn', 320, [[('xi26', 'hn')]], 'data'),
              ('sgn', 340, [[('xi26', 'sgn')]]),
              ('sgnb', 350, [[('xi26', 'sgnb')]])],
        right=[('outp', 260, [[('xi26', 'outp')]], 'data'),
               ('outn', 300, [[('xi26', 'outn')]], 'data')],
        bottom=[('tap<3:0>', 630, tap26_slices, 'bus'),
                ('en', 670, [[('xi26', 'en')]])],
        link='u_dfe_sum', members=['xi26'])

    # Odd Summer xi27
    tap27_slices = [[('xi27', f'tap<{i}>')] for i in range(4)]
    box(V, 'xi27', 600, 440, SUM_W, SUM_H, 'Σ', 'xi27',
        left=[('inp', 470, [[('xi27', 'inp')]], 'data'),
              ('inn', 490, [[('xi27', 'inn')]], 'data'),
              ('hp', 520, [[('xi27', 'hp')]], 'data'),
              ('hn', 540, [[('xi27', 'hn')]], 'data'),
              ('sgn', 560, [[('xi27', 'sgn')]]),
              ('sgnb', 570, [[('xi27', 'sgnb')]])],
        right=[('outp', 480, [[('xi27', 'outp')]], 'data'),
               ('outn', 520, [[('xi27', 'outn')]], 'data')],
        bottom=[('tap<3:0>', 630, tap27_slices, 'bus'),
                ('en', 670, [[('xi27', 'en')]])],
        link='u_dfe_sum', members=['xi27'])

    # Connect net6, net7 to xi26 and xi27
    V.wire([(540, 290), (560, 290), (560, 250), (580, 250)], cls='data')
    V.wire([(560, 290), (560, 470), (580, 470)], cls='data'); V.dot(560, 290)
    V.wire([(540, 330), (550, 330), (550, 270), (580, 270)], cls='data')
    V.wire([(550, 330), (550, 490), (580, 490)], cls='data'); V.dot(550, 330)

    # Connect sgn, sgnb from SGN_BUF to xi26, xi27
    V.wire([(490, 595), (570, 595), (570, 560)], cls='data'); V.netlabel('net106', 500, 595)
    V.wire([(570, 560), (580, 560)], cls='data'); V.dot(570, 560)
    V.wire([(570, 560), (570, 340), (580, 340)], cls='data')

    V.wire([(490, 615), (575, 615), (575, 570)], cls='data'); V.netlabel('net105', 500, 615)
    V.wire([(575, 570), (580, 570)], cls='data'); V.dot(575, 570)
    V.wire([(575, 570), (575, 350), (580, 350)], cls='data')

    # Port tap<3:0> bus & connect to xi26, xi27 bottom pins (at y=390 and y=610)
    V.port('tap<3:0>', 80, 640, d='right', io='in', cls='bus')
    V.wire([(80, 640), (630, 640)], cls='bus')
    busslash(V, 120, 640, 'tap<3:0>', 4, vertical=True)
    V.wire([(630, 640), (630, 610)], cls='bus')
    V.wire([(630, 610), (630, 390)], cls='bus'); V.dot(630, 610)

    # rx_en branch to xi26.en, xi27.en (at y=390 and y=610)
    V.wire([(110, 740), (110, 760), (670, 760)], cls='data'); V.dot(110, 740)
    V.wire([(670, 760), (670, 610)], cls='data')
    V.wire([(670, 610), (670, 390)], cls='data'); V.dot(670, 610)

    # SA Even xi28, Odd xi29
    tri(V, 'xi28', 820, 280, 'SA', 'xi28',
        ins=[('inp', -12, [[('xi28', 'inp')]], 'data'), ('inn', 12, [[('xi28', 'inn')]], 'data')],
        outs=[('outp', -12, [[('xi28', 'outp')]], 'data'), ('outn', 12, [[('xi28', 'outn')]], 'data')],
        bottom=[('ck', 25, [[('xi28', 'ck')]], 'clock')],
        pm={'inp': '+', 'inn': '−'}, link='u_sa_dt', members=['xi28'])

    tri(V, 'xi29', 820, 500, 'SA', 'xi29',
        ins=[('inp', -12, [[('xi29', 'inp')]], 'data'), ('inn', 12, [[('xi29', 'inn')]], 'data')],
        outs=[('outp', -12, [[('xi29', 'outp')]], 'data'), ('outn', 12, [[('xi29', 'outn')]], 'data')],
        bottom=[('ck', 25, [[('xi29', 'ck')]], 'clock')],
        pm={'inp': '+', 'inn': '−'}, link='u_sa_dt', members=['xi29'])

    V.wire([(750, 260), (790, 260), (790, 268), (800, 268)], cls='data'); V.netlabel('net10', 765, 260)
    V.wire([(750, 300), (790, 300), (790, 292), (800, 292)], cls='data'); V.netlabel('net11', 765, 300)
    V.wire([(750, 480), (790, 480), (790, 488), (800, 488)], cls='data'); V.netlabel('net12', 765, 480)
    V.wire([(750, 520), (790, 520), (790, 512), (800, 512)], cls='data'); V.netlabel('net13', 765, 520)

    # Clocks to SA
    # xi25.cko is at (500, 700), xi28.ck is at (845, 345)
    # xi25.ckob is at (500, 720), xi29.ck is at (845, 565)
    V.wire([(500, 700), (830, 700), (830, 345), (845, 345)], cls='clock'); V.netlabel('net8', 650, 700)
    V.wire([(500, 720), (860, 720), (860, 565), (845, 565)], cls='clock'); V.netlabel('net9', 650, 720)

    # SR latches xi30, xi31
    box(V, 'xi30', 940, 240, 100, 80, 'SR', 'xi30',
        left=[('s', 268, [[('xi30', 's')]], 'data'),
              ('r', 292, [[('xi30', 'r')]], 'data')],
        right=[('q', 260, [[('xi30', 'q')]], 'data'),
               ('qb', 300, [[('xi30', 'qb')]], 'data')],
        link='u_sr_nor', members=['xi30'])

    box(V, 'xi31', 940, 460, 100, 80, 'SR', 'xi31',
        left=[('s', 488, [[('xi31', 's')]], 'data'),
              ('r', 512, [[('xi31', 'r')]], 'data')],
        right=[('q', 480, [[('xi31', 'q')]], 'data'),
               ('qb', 520, [[('xi31', 'qb')]], 'data')],
        link='u_sr_nor', members=['xi31'])

    V.netlabel('net18', 920, 268)
    V.netlabel('net19', 920, 292)
    V.netlabel('net24', 920, 488)
    V.netlabel('net25', 920, 512)

    # Output inverters xi7, xi8 (even) and xi10, xi11 (odd)
    # Dummy inverters xi9, xi12
    # Inverter pin Y is at x0 + 62 (1192 and 1312)
    inv(V, 'xi7', 1130, 260, 'xi7', [[('xi7', 'a')]], [[('xi7', 'y')]], link='u_inv', members=['xi7'])
    inv(V, 'xi8', 1250, 260, 'xi8', [[('xi8', 'a')]], [[('xi8', 'y')]], link='u_inv', members=['xi8'])
    V.wire([(1060, 260), (1110, 260)], cls='data')
    V.wire([(1192, 260), (1230, 260)], cls='data'); V.netlabel('net26', 1210, 260)
    V.wire([(1312, 260), (1350, 260)], cls='data')
    V.port('dout_e', 1350, 260, d='right', io='out')

    inv(V, 'xi9', 1130, 300, 'xi9', [[('xi9', 'a')]], [[('xi9', 'y')]], link='u_inv', members=['xi9'])
    V.wire([(1060, 300), (1110, 300)], cls='data')
    V.wire([(1192, 300), (1250, 300)], cls='data'); V.netlabel('net27', 1220, 300)

    inv(V, 'xi10', 1130, 480, 'xi10', [[('xi10', 'a')]], [[('xi10', 'y')]], link='u_inv', members=['xi10'])
    inv(V, 'xi11', 1250, 480, 'xi11', [[('xi11', 'a')]], [[('xi11', 'y')]], link='u_inv', members=['xi11'])
    V.wire([(1060, 480), (1110, 480)], cls='data')
    V.wire([(1192, 480), (1230, 480)], cls='data'); V.netlabel('net28', 1210, 480)
    V.wire([(1312, 480), (1350, 480)], cls='data')
    V.port('dout_o', 1350, 480, d='right', io='out')

    inv(V, 'xi12', 1130, 520, 'xi12', [[('xi12', 'a')]], [[('xi12', 'y')]], link='u_inv', members=['xi12'])
    V.wire([(1060, 520), (1110, 520)], cls='data')
    V.wire([(1192, 520), (1250, 520)], cls='data'); V.netlabel('net29', 1220, 520)

    # Feedback: xi30 outputs (net14, net15) -> xi27 (hp, hn at 520, 540)
    # Feedback: xi31 outputs (net16, net17) -> xi26 (hp, hn at 300, 320)
    # Loop around the top/bottom perimeter to avoid crossing summer bottom pins and leads:
    # xi30 (top latch) loops over the top:
    V.wire([(1070, 260), (1070, 180), (525, 180), (525, 520), (580, 520)], cls='data')
    V.dot(1070, 260); V.netlabel('net14', 1070, 220)

    V.wire([(1080, 300), (1080, 190), (520, 190), (520, 540), (580, 540)], cls='data')
    V.dot(1080, 300); V.netlabel('net15', 1080, 240)

    # xi31 (bottom latch) loops under the bottom:
    V.wire([(1070, 480), (1070, 780), (535, 780), (535, 300), (580, 300)], cls='data')
    V.dot(1070, 480); V.netlabel('net16', 1070, 600)

    V.wire([(1080, 520), (1080, 790), (530, 790), (530, 320), (580, 320)], cls='data')
    V.dot(1080, 520); V.netlabel('net17', 1080, 620)

    V.omitted = [o for o in V.omitted if o.get('net') != 'vssq']
    return V

def build_all():
    view_top()
    view_term()
    view_pre()
    view_dfe_sum()
    view_sa_dt()
    view_sr_nor()
    view_ck_gbuf()
    view_odt_dec()
    view_ls()
    view_nor()
    view_nand()
    view_inv()

    out = []
    for v in VIEWS:
        d = dict(v.__dict__)
        d.pop('_tid', None)
        out.append(d)
    json.dump(out, open(W + '/scenes.json', 'w'), indent=0, default=list, ensure_ascii=False)
    print(f"Generated {len(VIEWS)} views successfully in {W}/scenes.json")

if __name__ == '__main__':
    build_all()
