"""Layouts for rx_l1 (rxbyte_top) — all 18 views."""
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
    gate = [[(name, 'g')]]
    return top, bot, gate

def new_view(vid, cell, level, title, w, h):
    V = View(vid, cell, level, title, w, h)
    VIEWS.append(V)
    return V

# =============================================================================
# 1. VIEW_INV: u_invx1
# =============================================================================
def view_inv():
    cell = 'invx1'
    V = new_view('u_invx1', cell, 'unit', f'{cell} — unit level (인버터)', 480, 400)
    rail(V, 80, 400, 70, 'vdd', 'VDD')
    rail(V, 80, 400, 330, 'vss', 'VSS')

    tp, bp, gp = mosT(cell, 'mp0')
    mos(V, 'mp0', 240, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp, bp, gp, members=['mp0'])
    V.wire([(240, 110), (240, 70)], cls='power'); V.dot(240, 70)

    tn, bn, gn = mosT(cell, 'mn0')
    mos(V, 'mn0', 240, 260, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn, bn, gn, members=['mn0'])
    V.wire([(240, 290), (240, 330)], cls='power'); V.dot(240, 330)

    V.wire([(200, 140), (160, 140), (160, 200)], cls='data')
    V.wire([(200, 260), (160, 260), (160, 200)], cls='data'); V.dot(160, 200)
    V.wire([(80, 200), (160, 200)], cls='data')
    V.port('a', 80, 200, d='right', io='in')

    V.wire([(240, 170), (240, 200)], cls='data')
    V.wire([(240, 230), (240, 200)], cls='data'); V.dot(240, 200)
    V.wire([(240, 200), (380, 200)], cls='data')
    V.port('y', 380, 200, d='right', io='out')

    V.omitted = []
    return V

# =============================================================================
# 2. VIEW_LVLUP: u_lvlup
# =============================================================================
def view_lvlup():
    cell = 'lvlup'
    V = new_view('u_lvlup', cell, 'unit', f'{cell} — unit level (레벨 시프터)', 820, 480)
    rail(V, 60, 760, 70, 'vddq', 'VDDQ')
    rail(V, 60, 760, 410, 'vss', 'VSS')
    rail(V, 60, 240, 120, 'vdd', 'VDD')

    # Input inverter mp2 / mn2 at X = 150
    tp2, bp2, gp2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 150, 180, 'p', 'left', 'mp2', wl(cell, 'mp2'), tp2, bp2, gp2, members=['mp2'])
    V.wire([(150, 150), (150, 120)], cls='power'); V.dot(150, 120)

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 150, 320, 'n', 'left', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(150, 350), (150, 410)], cls='power'); V.dot(150, 410)

    # Input wire 'in' at y = 250
    V.port('in', 60, 250, d='right', io='in')
    V.wire([(60, 250), (100, 250)], cls='data')
    V.wire([(100, 180), (110, 180)], cls='data')
    V.wire([(100, 320), (110, 320)], cls='data'); V.dot(100, 320)
    V.wire([(100, 180), (100, 250)], cls='data')
    V.wire([(100, 250), (100, 320)], cls='data'); V.dot(100, 250)
    V.wire([(100, 320), (100, 370), (290, 370), (290, 340)], cls='data')

    # Inverter output net4 from (150, 210) to (150, 290)
    V.wire([(150, 210), (150, 250)], cls='plain')
    V.wire([(150, 290), (150, 250)], cls='plain'); V.dot(150, 250)
    V.wire([(150, 250), (450, 250), (450, 340)], cls='plain')

    # Differential pair mn0 at X = 330, mn1 at X = 490
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 330, 340, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(330, 370), (330, 410)], cls='power'); V.dot(330, 410)

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 490, 340, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(490, 370), (490, 410)], cls='power'); V.dot(490, 410)

    # Cross-coupled PMOS mp0 at X = 330, mp1 at X = 490
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', 330, 160, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(330, 130), (330, 70)], cls='power'); V.dot(330, 70)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 490, 160, 'p', 'right', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(490, 130), (490, 70)], cls='power'); V.dot(490, 70)

    # net5: mp0.d (330, 190) -> mn0.d (330, 310)
    V.wire([(330, 190), (330, 220)], cls='plain')
    V.wire([(330, 310), (330, 220)], cls='plain'); V.dot(330, 220)
    V.wire([(330, 220), (530, 220), (530, 160)], cls='plain'); V.dot(530, 220)

    # net6: mp1.d (490, 190) -> mn1.d (490, 310)
    V.wire([(490, 190), (490, 200)], cls='plain')
    V.wire([(490, 310), (490, 200)], cls='plain'); V.dot(490, 200)
    V.wire([(490, 200), (290, 200), (290, 160)], cls='plain')

    # Output inverters mp3/mn3 (out from net5) at X = 630
    tp3, bp3, gp3 = mosT(cell, 'mp3')
    mos(V, 'mp3', 630, 160, 'p', 'left', 'mp3', wl(cell, 'mp3'), tp3, bp3, gp3, members=['mp3'])
    V.wire([(630, 130), (630, 70)], cls='power'); V.dot(630, 70)

    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 630, 340, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])
    V.wire([(630, 370), (630, 410)], cls='power'); V.dot(630, 410)

    V.wire([(330, 220), (590, 220)], cls='plain'); V.dot(590, 220)
    V.wire([(590, 220), (590, 160)], cls='plain')
    V.wire([(590, 220), (590, 340)], cls='plain')

    V.wire([(630, 190), (630, 240)], cls='data')
    V.wire([(630, 310), (630, 240)], cls='data'); V.dot(630, 240)
    V.wire([(630, 240), (740, 240)], cls='data')
    V.port('out', 740, 240, d='right', io='out')

    # Output inverters mp4/mn4 (outb from net6) at X = 710
    tp4, bp4, gp4 = mosT(cell, 'mp4')
    mos(V, 'mp4', 710, 160, 'p', 'left', 'mp4', wl(cell, 'mp4'), tp4, bp4, gp4, members=['mp4'])
    V.wire([(710, 130), (710, 70)], cls='power'); V.dot(710, 70)

    tn4, bn4, gn4 = mosT(cell, 'mn4')
    mos(V, 'mn4', 710, 340, 'n', 'left', 'mn4', wl(cell, 'mn4'), tn4, bn4, gn4, members=['mn4'])
    V.wire([(710, 370), (710, 410)], cls='power'); V.dot(710, 410)

    V.wire([(490, 200), (670, 200)], cls='plain'); V.dot(670, 200)
    V.wire([(670, 200), (670, 160)], cls='plain')
    V.wire([(670, 200), (670, 340)], cls='plain')

    V.wire([(710, 190), (710, 280)], cls='data')
    V.wire([(710, 310), (710, 280)], cls='data'); V.dot(710, 280)
    V.wire([(710, 280), (760, 280)], cls='data')
    V.port('outb', 760, 280, d='right', io='out')

    V.omitted = []
    return V

# =============================================================================
# 3. VIEW_CKBUF: u_ckbuf
# =============================================================================
def view_ckbuf():
    cell = 'ckbuf'
    V = new_view('u_ckbuf', cell, 'unit', f'{cell} — unit level (클럭 버퍼)', 520, 320)
    V.port('a', 60, 160, d='right', io='in', cls='clock')
    inv(V, 'xi0', 160, 160, 'xi0', [[('xi0', 'a')]], [[('xi0', 'y')]], members=['xi0'], cls='clock')
    V.wire([(60, 160), (140, 160)], cls='clock')
    inv(V, 'xi1', 320, 160, 'xi1', [[('xi1', 'a')]], [[('xi1', 'y')]], members=['xi1'], cls='clock')
    V.wire([(222, 160), (300, 160)], cls='clock')
    V.netlabel('net20', 260, 160)
    V.wire([(382, 160), (460, 160)], cls='clock')
    V.port('y', 460, 160, d='right', io='out', cls='clock')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 4. VIEW_PADESD: u_padesd
# =============================================================================
def view_padesd():
    cell = 'padesd'
    V = new_view('u_padesd', cell, 'unit', f'{cell} — unit level (종단 및 ESD)', 540, 360)
    rail(V, 80, 460, 300, 'vssq', 'VSSQ')

    V.port('pad', 60, 120, d='right', io='in')
    res(V, 'r0', 160, 120, orient='h', name='r0', size='', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'])
    V.wire([(60, 120), (130, 120)], cls='data')
    V.wire([(190, 120), (280, 120)], cls='data'); V.dot(280, 120)
    V.wire([(280, 120), (460, 120)], cls='data')
    V.port('pad_r', 460, 120, d='right', io='out')

    tn, bn, gn = mosT(cell, 'mn0')
    mos(V, 'mn0', 280, 200, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn, bn, gn, members=['mn0'])
    V.wire([(280, 120), (280, 170)], cls='data')
    V.wire([(280, 230), (280, 300)], cls='power'); V.dot(280, 300)

    V.wire([(240, 200), (200, 200), (200, 220)], cls='plain')
    res(V, 'r1', 200, 250, orient='v', name='r1', size='', a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'])
    V.wire([(200, 280), (200, 300)], cls='power'); V.dot(200, 300)

    V.omitted = [{'net': 'vddq', 'class': '전원'}]
    return V

# =============================================================================
# 5. VIEW_ODTLEG3: u_odtleg3
# =============================================================================
def view_odtleg3():
    cell = 'odtleg3'
    V = new_view('u_odtleg3', cell, 'unit', f'{cell} — unit level (ODT 레그)', 720, 440)
    rail(V, 60, 660, 80, 'vddq', 'VDDQ')

    xs = [180, 340, 500]
    for i, x in enumerate(xs):
        mp_name = f'mp{i}'
        r_name = f'r{i}'
        enb_name = f'enb{i}'
        net_mid = f'net{22+i}'

        # PMOS switch
        tp, bp, gp = mosT(cell, mp_name)
        mos(V, mp_name, x, 160, 'p', 'left', mp_name, wl(cell, mp_name), tp, bp, gp, members=[mp_name])
        V.wire([(x, 130), (x, 80)], cls='power'); V.dot(x, 80)

        # Gate enb
        V.port(enb_name, x - 50, 110, d='down', io='in')
        V.wire([(x - 50, 110), (x - 50, 160), (x - 40, 160)], cls='data')

        # Resistor in series
        res(V, r_name, x, 270, orient='v', name=r_name, size='',
            a=[[(r_name, 'p')]], b=[[(r_name, 'n')]], members=[r_name])
        V.wire([(x, 190), (x, 240)], cls='plain')
        V.netlabel(net_mid, x, 215)

        # Connect resistor bottom to pad bus at y=360
        V.wire([(x, 300), (x, 360)], cls='plain')
        if i > 0:
            V.dot(x, 360)

    # Pad bus line
    V.wire([(180, 360), (640, 360)], cls='plain')
    V.port('pad', 640, 360, d='right', io='in')

    V.omitted = []
    return V
# =============================================================================
# 6. VIEW_SBAMP: u_sbamp
# =============================================================================
def view_sbamp():
    cell = 'sbamp'
    V = new_view('u_sbamp', cell, 'unit', f'{cell} — unit level (샘플링 증폭기)', 760, 480)
    rail(V, 60, 700, 70, 'vddq', 'VDDQ')
    rail(V, 60, 700, 430, 'vssq', 'VSSQ')

    # Header enable mp6 at (180, 120)
    tp6, bp6, gp6 = mosT(cell, 'mp6')
    mos(V, 'mp6', 180, 120, 'p', 'left', 'mp6', wl(cell, 'mp6'), tp6, bp6, gp6, members=['mp6'])
    V.wire([(180, 90), (180, 70)], cls='power'); V.dot(180, 70)
    V.wire([(80, 120), (140, 120)], cls='data')
    V.port('enb', 80, 120, d='right', io='in')

    # Diode load mp5 at (180, 200) and mn5 at (180, 290)
    tp5, bp5, gp5 = mosT(cell, 'mp5')
    mos(V, 'mp5', 180, 200, 'p', 'left', 'mp5', wl(cell, 'mp5'), tp5, bp5, gp5, members=['mp5'])
    V.wire([(180, 150), (180, 170)], cls='plain') # net80 connects mp6.d to mp5.s

    tn5, bn5, gn5 = mosT(cell, 'mn5')
    mos(V, 'mn5', 180, 290, 'n', 'left', 'mn5', wl(cell, 'mn5'), tn5, bn5, gn5, members=['mn5'])

    # Footer enable mn6 at (180, 370)
    tn6, bn6, gn6 = mosT(cell, 'mn6')
    mos(V, 'mn6', 180, 370, 'n', 'left', 'mn6', wl(cell, 'mn6'), tn6, bn6, gn6, members=['mn6'])
    V.wire([(180, 320), (180, 340)], cls='plain') # net83 connects mn5.s to mn6.d
    V.wire([(180, 400), (180, 430)], cls='power'); V.dot(180, 430)
    V.wire([(80, 370), (140, 370)], cls='data')
    V.port('en', 80, 370, d='right', io='in')

    # Differential pairs: left branch mp1/mn1 at X = 400, right branch mp2/mn2 at X = 580
    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 400, 140, 'p', 'left', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 400, 350, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])

    tp2, bp2, gp2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 580, 140, 'p', 'right', 'mp2', wl(cell, 'mp2'), tp2, bp2, gp2, members=['mp2'])

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 580, 350, 'n', 'right', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])

    # net81 rail (top sources: mp5.d at (180, 230), mp1.s at (400, 110), mp2.s at (580, 110))
    V.wire([(180, 230), (240, 230), (240, 110), (400, 110)], cls='plain'); V.dot(400, 110)
    V.wire([(400, 110), (580, 110)], cls='plain')

    # net82 rail (bottom sources: mn5.d at (180, 260), mn1.s at (400, 380), mn2.s at (580, 380))
    V.wire([(180, 260), (240, 260), (240, 380), (400, 380)], cls='plain'); V.dot(400, 380)
    V.wire([(400, 380), (580, 380)], cls='plain')

    # net79 (mp1.d at (400, 170) and mn1.d at (400, 320))
    V.wire([(400, 170), (400, 245)], cls='plain')
    V.wire([(400, 320), (400, 245)], cls='plain'); V.dot(400, 245)
    V.wire([(400, 245), (120, 245)], cls='plain')
    V.wire([(120, 245), (120, 200), (140, 200)], cls='plain'); V.dot(120, 245)
    V.wire([(120, 245), (120, 290), (140, 290)], cls='plain')

    # out (mp2.d at (580, 170) and mn2.d at (580, 320))
    V.wire([(580, 170), (580, 245)], cls='data')
    V.wire([(580, 320), (580, 245)], cls='data'); V.dot(580, 245)
    V.wire([(580, 245), (680, 245)], cls='data')
    V.port('out', 680, 245, d='right', io='out')

    # Inputs inp and inn
    V.port('inp', 320, 80, d='down', io='in')
    V.wire([(320, 80), (320, 140), (360, 140)], cls='data'); V.dot(320, 140)
    V.wire([(320, 140), (320, 350), (360, 350)], cls='data')

    V.port('inn', 640, 80, d='down', io='in')
    V.wire([(640, 80), (640, 140), (620, 140)], cls='data'); V.dot(640, 140)
    V.wire([(640, 140), (640, 350), (620, 350)], cls='data')

    V.omitted = []
    return V

# =============================================================================
# 7. VIEW_DQSAMP: u_dqsamp
# =============================================================================
def view_dqsamp():
    cell = 'dqsamp'
    V = new_view('u_dqsamp', cell, 'unit', f'{cell} — unit level (CML 클럭 버퍼)', 640, 480)
    rail(V, 80, 560, 70, 'vddq', 'VDDQ')
    rail(V, 80, 560, 430, 'vssq', 'VSSQ')

    res(V, 'r0', 240, 130, orient='v', name='r0', size='', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'])
    V.wire([(240, 100), (240, 70)], cls='power'); V.dot(240, 70)
    V.wire([(240, 160), (240, 190)], cls='clock'); V.dot(240, 190)
    V.wire([(240, 190), (140, 190)], cls='clock')
    V.port('outn', 140, 190, d='left', io='out', cls='clock')

    res(V, 'r1', 400, 130, orient='v', name='r1', size='', a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'])
    V.wire([(400, 100), (400, 70)], cls='power'); V.dot(400, 70)
    V.wire([(400, 160), (400, 190)], cls='clock'); V.dot(400, 190)
    V.wire([(400, 190), (500, 190)], cls='clock')
    V.port('outp', 500, 190, d='right', io='out', cls='clock')

    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 240, 230, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(240, 190), (240, 200)], cls='clock')
    V.wire([(200, 230), (120, 230)], cls='clock')
    V.port('inp', 120, 230, d='right', io='in', cls='clock')

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 400, 230, 'n', 'right', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(400, 190), (400, 200)], cls='clock')
    V.wire([(440, 230), (520, 230)], cls='clock')
    V.port('inn', 520, 230, d='left', io='in', cls='clock')

    V.wire([(240, 260), (240, 280), (320, 280)], cls='plain'); V.dot(320, 280)
    V.wire([(400, 260), (400, 280), (320, 280)], cls='plain')

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 320, 310, 'n', 'left', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(320, 280), (320, 280)], cls='plain')
    V.wire([(280, 310), (200, 310)], cls='data')
    V.port('en', 200, 310, d='right', io='in')

    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 320, 380, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])
    V.wire([(320, 340), (320, 350)], cls='plain')
    V.wire([(320, 410), (320, 430)], cls='power'); V.dot(320, 430)
    gray_gate(V, {'x': 280, 'y': 380}, 'vbn', 'left')

    V.omitted = [{'net': 'vbn', 'class': '바이어스'}]
    return V

# =============================================================================
# 8. VIEW_ACAMP: u_acamp
# =============================================================================
def view_acamp():
    cell = 'acamp'
    V = new_view('u_acamp', cell, 'unit', f'{cell} — unit level (AC 증폭기)', 680, 420)
    rail(V, 80, 600, 70, 'vdd', 'VDD')
    rail(V, 80, 600, 360, 'vss', 'VSS')

    V.port('in', 60, 200, d='right', io='in', cls='clock')
    cap(V, 'c0', 130, 200, orient='h', name='c0', size='', a=[[('c0', 'p')]], b=[[('c0', 'n')]], members=['c0'])
    V.wire([(60, 200), (100, 200)], cls='clock')
    V.wire([(160, 200), (220, 200)], cls='clock'); V.dot(220, 200)

    res(V, 'r0', 260, 120, orient='h', name='r0', size='', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'])
    V.wire([(220, 200), (220, 120), (230, 120)], cls='plain')
    V.wire([(290, 120), (340, 120), (340, 200)], cls='plain')

    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', 300, 160, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(300, 130), (300, 70)], cls='power'); V.dot(300, 70)

    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 300, 250, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 300, 320, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(300, 280), (300, 290)], cls='plain')
    V.wire([(300, 350), (300, 360)], cls='power'); V.dot(300, 360)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 380, 160, 'p', 'right', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(380, 130), (380, 70)], cls='power'); V.dot(380, 70)

    V.port('en', 80, 320, d='right', io='in')
    V.wire([(80, 320), (180, 320)], cls='data'); V.dot(180, 320)
    V.wire([(180, 320), (260, 320)], cls='data')
    V.wire([(180, 320), (180, 380), (450, 380), (450, 160), (420, 160)], cls='data')

    V.wire([(220, 200), (240, 200)], cls='clock'); V.dot(240, 200)
    V.wire([(240, 200), (240, 160), (260, 160)], cls='clock')
    V.wire([(240, 200), (240, 250), (260, 250)], cls='clock')

    V.wire([(300, 190), (300, 200)], cls='clock')
    V.wire([(300, 220), (300, 200)], cls='clock'); V.dot(300, 200)
    V.wire([(300, 200), (340, 200)], cls='clock'); V.dot(340, 200)
    V.wire([(340, 200), (380, 200)], cls='clock'); V.dot(380, 200)
    V.wire([(380, 190), (380, 200)], cls='plain')

    inv(V, 'xi0', 440, 200, 'xi0', [[('xi0', 'a')]], [[('xi0', 'y')]], members=['xi0'], cls='clock')
    V.wire([(380, 200), (420, 200)], cls='clock')
    V.wire([(502, 200), (580, 200)], cls='clock')
    V.port('out', 580, 200, d='right', io='out', cls='clock')

    V.omitted = []
    return V

# =============================================================================
# 9. VIEW_SRNAND: u_srnand
# =============================================================================
def view_srnand():
    cell = 'srnand'
    V = new_view('u_srnand', cell, 'unit', f'{cell} — unit level (SR 래치)', 560, 380)

    box(V, 'xi0', 240, 110, 80, 60, 'NAND2', 'xi0',
        left=[('a', 130, [[('xi0', 'a')]], 'data'), ('b', 150, [[('xi0', 'b')]], 'data')],
        right=[('y', 140, [[('xi0', 'y')]], 'data')], bubbles=('y',), members=['xi0'])

    box(V, 'xi1', 240, 220, 80, 60, 'NAND2', 'xi1',
        left=[('b', 240, [[('xi1', 'b')]], 'data'), ('a', 260, [[('xi1', 'a')]], 'data')],
        right=[('y', 250, [[('xi1', 'y')]], 'data')], bubbles=('y',), members=['xi1'])

    V.port('sb', 80, 130, d='right', io='in')
    V.wire([(80, 130), (220, 130)], cls='data')

    V.port('rb', 80, 260, d='right', io='in')
    V.wire([(80, 260), (220, 260)], cls='data')

    V.wire([(340, 140), (460, 140)], cls='data'); V.dot(380, 140)
    V.port('q', 460, 140, d='right', io='out')

    V.wire([(340, 250), (460, 250)], cls='data'); V.dot(380, 250)
    V.port('qb', 460, 250, d='right', io='out')

    V.wire([(380, 140), (380, 180), (180, 180), (180, 240), (220, 240)], cls='data')
    V.wire([(380, 250), (380, 210), (160, 210), (160, 150), (220, 150)], cls='data')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 10. VIEW_SADFE: u_sadfe
# =============================================================================
def view_sadfe():
    cell = 'sadfe'
    V = new_view('u_sadfe', cell, 'unit', f'{cell} — unit level (StrongARM DFE)', 980, 640)
    rail(V, 60, 920, 70, 'vdd', 'VDD')
    rail(V, 60, 920, 580, 'vss', 'VSS')

    # Precharge & latch PMOS
    for name, x, orient in [('mp2', 300, 'left'), ('mp4', 360, 'left'), ('mp0', 420, 'left'),
                             ('mp1', 540, 'right'), ('mp5', 600, 'right'), ('mp3', 660, 'right')]:
        tp, bp, gp = mosT(cell, name)
        mos(V, name, x, 140, 'p', orient, name, wl(cell, name), tp, bp, gp, members=[name])
        V.wire([(x, 110), (x, 70)], cls='power'); V.dot(x, 70)

    # Cross-coupled NMOS mn3 (420), mn4 (540) at y = 240
    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 420, 240, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])

    tn4, bn4, gn4 = mosT(cell, 'mn4')
    mos(V, 'mn4', 540, 240, 'n', 'right', 'mn4', wl(cell, 'mn4'), tn4, bn4, gn4, members=['mn4'])

    # outn trunk at y = 180
    V.wire([(140, 180), (580, 180)], cls='data')
    V.port('outn', 140, 180, d='left', io='out')
    V.wire([(300, 170), (300, 180)], cls='data'); V.dot(300, 180)
    V.wire([(420, 170), (420, 180)], cls='data'); V.dot(420, 180)
    V.wire([(420, 210), (420, 180)], cls='data') # mn3.T
    V.dot(580, 180)
    V.wire([(580, 180), (580, 140)], cls='data') # mp1.G
    V.wire([(580, 180), (580, 240)], cls='data') # mn4.G

    # outp trunk at y = 200
    V.wire([(380, 200), (840, 200)], cls='data')
    V.port('outp', 840, 200, d='right', io='out')
    V.wire([(660, 170), (660, 200)], cls='data'); V.dot(660, 200)
    V.wire([(540, 170), (540, 200)], cls='data'); V.dot(540, 200)
    V.wire([(540, 210), (540, 200)], cls='data') # mn4.T
    V.dot(380, 200)
    V.wire([(380, 200), (380, 140)], cls='data') # mp0.G
    V.wire([(380, 200), (380, 240)], cls='data') # mn3.G

    V.allowed_cross.append({'at': [420.0, 200.0], 'reason': 'StrongARM cross-coupling'})

    # Main input pair mn1(420), mn2(540) at y = 330
    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 420, 330, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(380, 330), (140, 330)], cls='data'); V.port('inp', 140, 330, d='right', io='in')

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 540, 330, 'n', 'right', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(580, 330), (840, 330)], cls='data'); V.port('inn', 840, 330, d='left', io='in')

    # net85: mp4.d(360, 170), mn3.s(420, 270), mn1.d(420, 300)
    V.wire([(360, 170), (360, 260), (420, 260)], cls='plain'); V.dot(420, 260)
    V.wire([(420, 260), (420, 270)], cls='plain'); V.dot(420, 270)
    V.wire([(420, 270), (420, 300)], cls='plain'); V.netlabel('net85', 420, 280)

    # net86: mp5.d(600, 170), mn4.s(540, 270), mn2.d(540, 300)
    V.wire([(600, 170), (600, 290), (540, 290)], cls='plain'); V.dot(540, 290)
    V.wire([(540, 270), (540, 290)], cls='plain')
    V.wire([(540, 290), (540, 300)], cls='plain'); V.netlabel('net86', 540, 280)

    # Common tail node net84 at y = 430
    V.wire([(420, 360), (420, 430), (480, 430)], cls='plain'); V.dot(480, 430)
    V.wire([(540, 360), (540, 430), (480, 430)], cls='plain')

    # mn0 at (480, 490)
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 480, 490, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(480, 430), (480, 460)], cls='plain')
    V.wire([(480, 520), (480, 580)], cls='power'); V.dot(480, 580)

    # ck trunk at y = 550: connects mn0.g(440,490), mp2.g(260,140), mp4.g(320,140), mp5.g(640,140), mp3.g(700,140)
    V.port('ck', 140, 550, d='right', io='in', cls='clock')
    V.wire([(140, 550), (440, 550)], cls='clock'); V.dot(220, 550); V.dot(440, 550)
    V.wire([(440, 550), (440, 490)], cls='clock') # mn0.G

    # Left ck bus at x=220
    V.wire([(220, 550), (220, 140)], cls='clock'); V.dot(220, 140)
    V.wire([(220, 140), (260, 140)], cls='clock') # mp2.G
    V.wire([(220, 140), (220, 100), (320, 100), (320, 140)], cls='clock') # mp4.G

    # Right ck bus at x=880 (clear of TAP2 right pins at 800 and ports at 840)
    V.wire([(440, 550), (880, 550), (880, 140)], cls='clock'); V.dot(880, 140)
    V.wire([(880, 140), (700, 140)], cls='clock') # mp3.G
    V.wire([(880, 140), (880, 100), (640, 100), (640, 140)], cls='clock') # mp5.G

    # DFE Tap 1 Bank (mn10..mn18) at (200, 340)
    d85_pins = [[('mn11', 'd')], [('mn14', 'd')], [('mn17', 'd')]]
    d86_pins = [[('mn10', 'd')], [('mn13', 'd')], [('mn16', 'd')]]
    h1p_pins = [[('mn10', 'g')], [('mn13', 'g')], [('mn16', 'g')]]
    h1n_pins = [[('mn11', 'g')], [('mn14', 'g')], [('mn17', 'g')]]
    s84_pins = [[('mn12', 's')], [('mn15', 's')], [('mn18', 's')]]

    box(V, 'TAP1', 200, 340, 120, 80, 'TAP1', None,
        top=[('net85', 240, d85_pins, 'plain'), ('net86', 280, d86_pins, 'plain')],
        left=[('w1_2', 360, [[('mn12', 'g')]], 'data'), ('w1_1', 380, [[('mn15', 'g')]], 'data'), ('w1_0', 400, [[('mn18', 'g')]], 'data')],
        right=[('h1p', 360, h1p_pins, 'data'), ('h1n', 380, h1n_pins, 'data')],
        bottom=[('net84', 260, s84_pins, 'plain')],
        members=['mn10', 'mn11', 'mn12', 'mn13', 'mn14', 'mn15', 'mn16', 'mn17', 'mn18'])

    # TAP1 to net85 (y=260) and net86 (y=290)
    V.wire([(240, 320), (240, 260), (360, 260)], cls='plain'); V.dot(360, 260)
    V.wire([(280, 320), (280, 290), (540, 290)], cls='plain')
    V.allowed_cross.append({'at': [420.0, 290.0], 'reason': 'TAP1 net86 crossing mn1 drain net85'})

    # TAP1 to net84 (y=430)
    V.wire([(260, 440), (260, 430), (420, 430)], cls='plain'); V.dot(420, 430)

    V.port('w1_2', 140, 360, d='right', io='in'); V.wire([(140, 360), (180, 360)], cls='data')
    V.port('w1_1', 140, 380, d='right', io='in'); V.wire([(140, 380), (180, 380)], cls='data')
    V.port('w1_0', 140, 400, d='right', io='in'); V.wire([(140, 400), (180, 400)], cls='data')

    V.wire([(340, 360), (370, 360)], cls='data'); V.port('h1p', 370, 360, d='left', io='in')
    V.wire([(340, 380), (370, 380)], cls='data'); V.port('h1n', 370, 380, d='left', io='in')

    # DFE Tap 2 Bank (mn20..mn25) at (660, 340)
    d85_p2 = [[('mn21', 'd')], [('mn24', 'd')]]
    d86_p2 = [[('mn20', 'd')], [('mn23', 'd')]]
    h2p_pins = [[('mn20', 'g')], [('mn23', 'g')]]
    h2n_pins = [[('mn21', 'g')], [('mn24', 'g')]]
    s84_p2 = [[('mn22', 's')], [('mn25', 's')]]

    box(V, 'TAP2', 660, 340, 120, 80, 'TAP2', None,
        top=[('net85', 700, d85_p2, 'plain'), ('net86', 740, d86_p2, 'plain')],
        left=[('h2p', 360, h2p_pins, 'data'), ('h2n', 380, h2n_pins, 'data')],
        right=[('w2_1', 360, [[('mn22', 'g')]], 'data'), ('w2_0', 380, [[('mn25', 'g')]], 'data')],
        bottom=[('net84', 720, s84_p2, 'plain')],
        members=['mn20', 'mn21', 'mn22', 'mn23', 'mn24', 'mn25'])

    # TAP2 connections to net85 (via y=260) and net86 (via y=290)
    V.wire([(700, 320), (700, 260), (420, 260)], cls='plain')
    V.wire([(740, 320), (740, 290), (600, 290)], cls='plain'); V.dot(600, 290)

    # TAP2 to net84 (y=430)
    V.wire([(720, 440), (720, 430), (540, 430)], cls='plain'); V.dot(540, 430)

    V.port('h2p', 610, 360, d='right', io='in'); V.wire([(610, 360), (640, 360)], cls='data')
    V.port('h2n', 610, 380, d='right', io='in'); V.wire([(610, 380), (640, 380)], cls='data')

    V.port('w2_1', 840, 360, d='left', io='in'); V.wire([(800, 360), (840, 360)], cls='data')
    V.port('w2_0', 840, 380, d='left', io='in'); V.wire([(800, 380), (840, 380)], cls='data')

    V.omitted = [{'net': 'net<91:87>', 'class': '내부'}]
    return V
# =============================================================================
# 11. VIEW_VREFDAC: u_vrefdac
# =============================================================================
def view_vrefdac():
    cell = 'vrefdac'
    V = new_view('u_vrefdac', cell, 'unit', f'{cell} — unit level (기준 전압 DAC)', 1020, 520)
    rail(V, 60, 960, 70, 'vddq', 'VDDQ')
    rail(V, 60, 960, 460, 'vssq', 'VSSQ')

    xs = [160, 260, 360, 460, 560, 660]
    for i, x in enumerate(xs):
        mp_top = f'mp{2*i}'
        mp_sw = f'mp{2*i+1}'

        tp, bp, gp = mosT(cell, mp_top)
        mos(V, mp_top, x, 150, 'p', 'left', mp_top, wl(cell, mp_top), tp, bp, gp, members=[mp_top])
        V.wire([(x, 120), (x, 70)], cls='power'); V.dot(x, 70)

        tps, bps, gps = mosT(cell, mp_sw)
        mos(V, mp_sw, x, 230, 'p', 'left', mp_sw, wl(cell, mp_sw), tps, bps, gps, members=[mp_sw])
        V.wire([(x, 180), (x, 200)], cls='plain')
        V.wire([(x, 260), (x, 290)], cls='plain')
        if i > 0:
            V.dot(x, 290)

    # Bias vbp rail at y = 125
    V.wire([(80, 125), (700, 125)], cls='plain')
    gray_gate(V, {'x': 80, 'y': 125}, 'vbp', 'left')
    for x in xs:
        V.wire([(x - 40, 125), (x - 40, 150)], cls='plain')
        V.dot(x - 40, 125)

    # Single INV_BANK box for xi0..xi5 (placed at x-40 to align with mp_sw gates)
    inv_top = [(f'net{35+i}', xs[i] - 40, [[(f'xi{i}', 'y')]], 'plain') for i in range(6)]
    inv_bot = [(f'c{i}', xs[i] - 40, [[(f'xi{i}', 'a')]], 'data') for i in range(6)]
    box(V, 'INV_BANK', 100, 330, 600, 40, 'INV_BANK', None,
        top=inv_top, bottom=inv_bot, members=['xi0', 'xi1', 'xi2', 'xi3', 'xi4', 'xi5'])

    for i, x in enumerate(xs):
        V.wire([(x - 40, 310), (x - 40, 230)], cls='plain')
        V.port(f'c{i}', x - 40, 420, d='up', io='in')
        V.wire([(x - 40, 420), (x - 40, 390)], cls='data')

    # Summing line net32 at y = 290
    V.wire([(160, 290), (840, 290)], cls='plain')

    # Dummy leg mp12, mp13 at X = 740
    tp12, bp12, gp12 = mosT(cell, 'mp12')
    mos(V, 'mp12', 740, 150, 'p', 'left', 'mp12', wl(cell, 'mp12'), tp12, bp12, gp12, members=['mp12'])
    V.wire([(740, 120), (740, 70)], cls='power'); V.dot(740, 70)
    V.wire([(700, 125), (700, 150)], cls='plain') # vbp to mp12 gate at (700, 150)

    tp13, bp13, gp13 = mosT(cell, 'mp13')
    mos(V, 'mp13', 740, 230, 'p', 'left', 'mp13', wl(cell, 'mp13'), tp13, bp13, gp13, members=['mp13'])
    V.wire([(740, 180), (740, 200)], cls='plain')
    V.wire([(740, 260), (740, 290)], cls='plain'); V.dot(740, 290)
    V.wire([(700, 230), (700, 460)], cls='power'); V.dot(700, 460) # gate of mp13 tied to VSSQ

    # Resistor r0 (between net32 and vssq) at X = 800
    res(V, 'r0', 800, 350, orient='v', name='r0', size=fmt_si(el(cell, 'r0')['value']),
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'])
    V.wire([(800, 290), (800, 320)], cls='plain'); V.dot(800, 290)
    V.wire([(800, 380), (800, 460)], cls='power'); V.dot(800, 460)

    # Resistor r1 (between net32 and vref) at X = 860
    res(V, 'r1', 860, 350, orient='v', name='r1', size=fmt_si(el(cell, 'r1')['value']),
        a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'])
    V.wire([(840, 290), (860, 290), (860, 320)], cls='plain')

    # Port vref from r1.B (860, 380)
    V.wire([(860, 380), (940, 380)], cls='plain')
    V.port('vref', 940, 380, d='right', io='out')

    # mn0 MOS capacitor at X = 900: gate to vref, drain & source to VSSQ
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 900, 420, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(860, 380), (860, 420)], cls='plain'); V.dot(860, 380) # to mn0.G at (860, 420)
    V.wire([(900, 390), (920, 390), (920, 460)], cls='power') # drain to VSSQ
    V.wire([(900, 450), (920, 450)], cls='power'); V.dot(920, 450) # source to VSSQ
    V.dot(920, 460)

    V.omitted = [
        {'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}
    ]
    return V
# =============================================================================
# 12. VIEW_ODTCTL: b_odtctl
# =============================================================================
def view_odtctl():
    cell = 'odtctl'
    V = new_view('b_odtctl', cell, 'block', f'{cell} — 블록 레벨', 760, 480)

    # odt_en from top
    V.port('odt_en', 120, 70, d='down', io='in')
    V.wire([(120, 70), (120, 160)], cls='data'); V.dot(120, 160)
    V.wire([(120, 160), (120, 240)], cls='data'); V.dot(120, 240)
    V.wire([(120, 240), (120, 320)], cls='data')

    rtts = ['rtt2', 'rtt1', 'rtt0']
    rtt_xs = [220, 230, 240]
    ys = [160, 240, 320]
    for i, y in enumerate(ys):
        nand_id = f'xi{2-i}'
        lvl_id = f'xi{5-i}'
        rtt_name = rtts[i]
        rtt_x = rtt_xs[i]
        out_name = f'enb{2-i}'
        net_mid = f'net{25+i}'

        box(V, nand_id, 180, y - 25, 70, 50, 'NAND2', nand_id,
            top=[('a', 200, [[(nand_id, 'a')]], 'data'), ('b', rtt_x, [[(nand_id, 'b')]], 'data')],
            right=[('y', y, [[(nand_id, 'y')]], 'data')], bubbles=('y',), members=[nand_id])

        V.wire([(120, y), (200, y), (200, y - 45)], cls='data')

        V.port(rtt_name, rtt_x, 70, d='down', io='in')
        V.wire([(rtt_x, 70), (rtt_x, y - 45)], cls='data')

        box(V, lvl_id, 360, y - 25, 80, 50, 'LVLUP', lvl_id,
            top=[('in', 400, [[(lvl_id, 'in')]], 'data')],
            right=[('out', y, [[(lvl_id, 'out')]], 'data')], members=[lvl_id])

        V.wire([(270, y), (310, y), (310, y - 45), (400, y - 45)], cls='data')
        V.netlabel(net_mid, 300, y)

        V.wire([(460, y), (560, y)], cls='data')
        V.port(out_name, 560, y, d='right', io='out')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'}, {'net': 'vss', 'class': '전원'},
        {'net': 'net<30:28>', 'class': '미사용'}
    ]
    return V
# =============================================================================
# 13. VIEW_WLDET: b_wldet
# =============================================================================
def view_wldet():
    cell = 'wldet'
    V = new_view('b_wldet', cell, 'block', f'{cell} — 블록 레벨', 780, 360)

    yc = 165
    V.port('ck', 60, yc, d='right', io='in', cls='clock')
    V.port('en', 190, 70, d='down', io='in')
    V.port('d', 60, 220, d='right', io='in', cls='clock')

    box(V, 'xi0', 160, 140, 60, 50, 'NAND2', 'xi0',
        left=[('a', yc, [[('xi0', 'a')]], 'clock')],
        top=[('b', 190, [[('xi0', 'b')]], 'data')],
        right=[('y', yc, [[('xi0', 'y')]], 'clock')], bubbles=('y',), members=['xi0'])
    V.wire([(60, yc), (140, yc)], cls='clock')
    V.wire([(190, 70), (190, 120)], cls='data')

    inv(V, 'xi1', 270, yc, 'xi1', [[('xi1', 'a')]], [[('xi1', 'y')]], members=['xi1'], cls='clock')
    V.wire([(240, yc), (250, yc)], cls='clock'); V.netlabel('net105', 245, yc)

    box(V, 'xi2', 390, 135, 80, 60, 'DFF', 'xi2',
        left=[('ck', yc, [[('xi2', 'ck')]], 'clock'), ('d', 185, [[('xi2', 'd')]], 'clock')],
        right=[('q', yc, [[('xi2', 'q')]], 'clock')], members=['xi2'])
    V.wire([(332, yc), (370, yc)], cls='clock'); V.netlabel('net106', 350, yc)
    V.wire([(60, 220), (350, 220), (350, 185), (370, 185)], cls='clock')

    inv(V, 'xi3', 530, yc, 'xi3', [[('xi3', 'a')]], [[('xi3', 'y')]], members=['xi3'], cls='clock')
    V.wire([(490, yc), (510, yc)], cls='clock'); V.netlabel('net107', 500, yc)

    inv(V, 'xi4', 630, yc, 'xi4', [[('xi4', 'a')]], [[('xi4', 'y')]], members=['xi4'], cls='clock')
    V.wire([(592, yc), (610, yc)], cls='clock'); V.netlabel('net108', 600, yc)

    V.wire([(692, yc), (730, yc)], cls='clock')
    V.port('q', 730, yc, d='right', io='out')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 14. VIEW_DLY3: b_dly3
# =============================================================================
def view_dly3():
    cell = 'dly3'
    V = new_view('b_dly3', cell, 'block', f'{cell} — 블록 레벨', 1040, 380)

    V.port('in', 60, 180, d='right', io='in', cls='clock')
    V.port('s0', 250, 70, d='down', io='in')
    V.port('s1', 510, 70, d='down', io='in')
    V.port('s2', 770, 70, d='down', io='in')

    # Stage 0: xi0 (BUF) + xi1 (MUX)
    box(V, 'xi0', 120, 220, 50, 40, 'BUF', 'xi0',
        left=[('a', 240, [[('xi0', 'a')]], 'clock')], right=[('y', 240, [[('xi0', 'y')]], 'clock')],
        members=['xi0'])
    box(V, 'xi1', 220, 160, 60, 60, 'MUX2', 'xi1',
        left=[('d0', 180, [[('xi1', 'd0')]], 'clock'), ('d1', 200, [[('xi1', 'd1')]], 'clock')],
        top=[('s', 250, [[('xi1', 's')]], 'data')], right=[('z', 190, [[('xi1', 'z')]], 'clock')],
        members=['xi1'])

    V.wire([(60, 180), (100, 180), (200, 180)], cls='clock'); V.dot(100, 180)
    V.wire([(100, 180), (100, 240)], cls='clock')
    V.wire([(190, 240), (200, 240), (200, 200)], cls='clock'); V.netlabel('net67', 195, 240)
    V.wire([(250, 70), (250, 140)], cls='data')

    # Stage 1: xi2 (BUF) + DLY_2BUF + xi5 (MUX)
    box(V, 'xi2', 330, 170, 50, 40, 'BUF', 'xi2',
        left=[('a', 190, [[('xi2', 'a')]], 'clock')], right=[('y', 190, [[('xi2', 'y')]], 'clock')],
        members=['xi2'])
    V.wire([(300, 190), (310, 190)], cls='clock'); V.netlabel('net68', 305, 190)

    box(V, 'DLY_2BUF', 400, 220, 50, 40, '2×BUF', None,
        left=[('a', 240, [[('xi3', 'a')]], 'clock')], right=[('y', 240, [[('xi4', 'y')]], 'clock')],
        members=['xi3', 'xi4'])

    box(V, 'xi5', 480, 160, 60, 60, 'MUX2', 'xi5',
        left=[('d0', 180, [[('xi5', 'd0')]], 'clock'), ('d1', 200, [[('xi5', 'd1')]], 'clock')],
        top=[('s', 510, [[('xi5', 's')]], 'data')], right=[('z', 190, [[('xi5', 'z')]], 'clock')],
        members=['xi5'])

    V.wire([(400, 190), (440, 190), (440, 180), (460, 180)], cls='clock'); V.dot(400, 190); V.netlabel('net69', 420, 190)
    V.wire([(400, 190), (400, 240), (380, 240)], cls='clock')
    V.wire([(470, 240), (475, 240), (475, 200), (460, 200)], cls='clock'); V.netlabel('net71', 472, 240)
    V.wire([(510, 70), (510, 140)], cls='data')

    # Stage 2: xi6 (BUF) + DLY_4BUF + xi11 (MUX)
    box(V, 'xi6', 590, 170, 50, 40, 'BUF', 'xi6',
        left=[('a', 190, [[('xi6', 'a')]], 'clock')], right=[('y', 190, [[('xi6', 'y')]], 'clock')],
        members=['xi6'])
    V.wire([(560, 190), (570, 190)], cls='clock'); V.netlabel('net72', 565, 190)

    box(V, 'DLY_4BUF', 660, 220, 50, 40, '4×BUF', None,
        left=[('a', 240, [[('xi7', 'a')]], 'clock')], right=[('y', 240, [[('xi10', 'y')]], 'clock')],
        members=['xi7', 'xi8', 'xi9', 'xi10'])

    box(V, 'xi11', 740, 160, 60, 60, 'MUX2', 'xi11',
        left=[('d0', 180, [[('xi11', 'd0')]], 'clock'), ('d1', 200, [[('xi11', 'd1')]], 'clock')],
        top=[('s', 770, [[('xi11', 's')]], 'data')], right=[('z', 190, [[('xi11', 'z')]], 'clock')],
        members=['xi11'])

    V.wire([(660, 190), (700, 190), (700, 180), (720, 180)], cls='clock'); V.dot(660, 190); V.netlabel('net73', 680, 190)
    V.wire([(660, 190), (660, 240), (640, 240)], cls='clock')
    V.wire([(730, 240), (735, 240), (735, 200), (720, 200)], cls='clock'); V.netlabel('net77', 732, 240)
    V.wire([(770, 70), (770, 140)], cls='data')

    # Output buf xi12
    box(V, 'xi12', 860, 170, 50, 40, 'BUF', 'xi12',
        left=[('a', 190, [[('xi12', 'a')]], 'clock')], right=[('y', 190, [[('xi12', 'y')]], 'clock')],
        members=['xi12'])
    V.wire([(820, 190), (840, 190)], cls='clock'); V.netlabel('net78', 830, 190)
    V.wire([(930, 190), (980, 190)], cls='clock')
    V.port('out', 980, 190, d='right', io='out', cls='clock')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'},
        {'net': 'net70', 'class': '내부'}, {'net': 'net74', 'class': '내부'},
        {'net': 'net75', 'class': '내부'}, {'net': 'net76', 'class': '내부'}
    ]
    return V
# =============================================================================
# 15. VIEW_DQSGATE: b_dqsgate
# =============================================================================
def view_dqsgate():
    cell = 'dqsgate'
    V = new_view('b_dqsgate', cell, 'block', f'{cell} — 블록 레벨', 740, 440)

    # open from top at x = 130
    V.port('open', 130, 70, d='down', io='in')
    V.wire([(130, 70), (130, 100)], cls='data'); V.dot(130, 100)
    V.wire([(130, 100), (215, 100)], cls='data')
    V.wire([(130, 100), (130, 230), (215, 230)], cls='data')

    # Clock inputs from left
    V.port('ckt', 60, 200, d='right', io='in', cls='clock')
    V.port('ckc', 60, 330, d='right', io='in', cls='clock')

    # Top branch: xi0 (lat_tg), xi2 (nand2x2), xi3 (invx4) -> gt
    box(V, 'xi0', 180, 120, 70, 60, 'LAT', 'xi0',
        top=[('d', 215, [[('xi0', 'd')]], 'data')],
        left=[('en', 150, [[('xi0', 'en')]], 'clock')],
        bottom=[('enb', 215, [[('xi0', 'enb')]], 'clock')],
        right=[('q', 150, [[('xi0', 'q')]], 'clock')], members=['xi0'])

    # ckc to xi0.en (160, 150)
    V.wire([(60, 330), (80, 330)], cls='clock'); V.dot(80, 330)
    V.wire([(80, 330), (80, 150), (160, 150)], cls='clock')

    # ckt to xi0.enb (215, 200) and xi2.a (290, 165)
    V.wire([(60, 200), (215, 200)], cls='clock'); V.dot(90, 200); V.dot(215, 200)
    # ckt branch to xi1.en (160, 280)
    V.wire([(90, 200), (90, 280), (160, 280)], cls='clock')

    box(V, 'xi2', 310, 130, 70, 50, 'NAND2', 'xi2',
        left=[('b', 145, [[('xi2', 'b')]], 'clock'), ('a', 165, [[('xi2', 'a')]], 'clock')],
        right=[('y', 155, [[('xi2', 'y')]], 'clock')], bubbles=('y',), members=['xi2'])
    V.wire([(270, 150), (280, 150), (280, 145), (290, 145)], cls='clock'); V.netlabel('net63', 275, 150)
    V.wire([(215, 200), (280, 200), (280, 165), (290, 165)], cls='clock')

    inv(V, 'xi3', 430, 155, 'xi3', [[('xi3', 'a')]], [[('xi3', 'y')]], members=['xi3'], cls='clock')
    V.wire([(400, 155), (410, 155)], cls='clock'); V.netlabel('net65', 405, 155)
    V.wire([(492, 155), (660, 155)], cls='clock')
    V.port('gt', 660, 155, d='right', io='out', cls='clock')

    # Bot branch: xi1 (lat_tg), xi4 (nand2x2), xi5 (invx4) -> gc
    box(V, 'xi1', 180, 250, 70, 60, 'LAT', 'xi1',
        top=[('d', 215, [[('xi1', 'd')]], 'data')],
        left=[('en', 280, [[('xi1', 'en')]], 'clock')],
        bottom=[('enb', 215, [[('xi1', 'enb')]], 'clock')],
        right=[('q', 280, [[('xi1', 'q')]], 'clock')], members=['xi1'])

    # ckc to xi1.enb (215, 330) and xi4.a (290, 295)
    V.wire([(80, 330), (215, 330)], cls='clock'); V.dot(215, 330)

    box(V, 'xi4', 310, 260, 70, 50, 'NAND2', 'xi4',
        left=[('b', 275, [[('xi4', 'b')]], 'clock'), ('a', 295, [[('xi4', 'a')]], 'clock')],
        right=[('y', 285, [[('xi4', 'y')]], 'clock')], bubbles=('y',), members=['xi4'])
    V.wire([(270, 280), (280, 280), (280, 275), (290, 275)], cls='clock'); V.netlabel('net64', 275, 280)
    V.wire([(215, 330), (280, 330), (280, 295), (290, 295)], cls='clock')

    inv(V, 'xi5', 430, 285, 'xi5', [[('xi5', 'a')]], [[('xi5', 'y')]], members=['xi5'], cls='clock')
    V.wire([(400, 285), (410, 285)], cls='clock'); V.netlabel('net66', 405, 285)
    V.wire([(492, 285), (660, 285)], cls='clock')
    V.port('gc', 660, 285, d='right', io='out', cls='clock')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V
# =============================================================================
# 16. VIEW_DQSRX: b_dqsrx
# =============================================================================
def view_dqsrx():
    cell = 'dqsrx'
    V = new_view('b_dqsrx', cell, 'block', f'{cell} — 블록 레벨', 860, 440)

    V.port('inp', 60, 160, d='right', io='in', cls='clock')
    V.port('inn', 60, 220, d='right', io='in', cls='clock')

    V.port('enq', 195, 70, d='down', io='in')
    V.port('en', 350, 70, d='down', io='in')

    box(V, 'xi0', 160, 140, 70, 60, 'DQSAMP', 'xi0',
        left=[('inp', 160, [[('xi0', 'inp')]], 'clock'), ('inn', 180, [[('xi0', 'inn')]], 'clock')],
        top=[('en', 195, [[('xi0', 'en')]], 'data')],
        right=[('outp', 160, [[('xi0', 'outp')]], 'clock'), ('outn', 180, [[('xi0', 'outn')]], 'clock')],
        members=['xi0'])
    V.wire([(60, 160), (140, 160)], cls='clock')
    V.wire([(60, 220), (100, 220), (100, 180), (140, 180)], cls='clock')
    V.wire([(195, 70), (195, 120)], cls='data')

    box(V, 'xi1', 320, 130, 60, 50, 'ACAMP', 'xi1',
        left=[('in', 155, [[('xi1', 'in')]], 'clock')],
        top=[('en', 350, [[('xi1', 'en')]], 'data')],
        right=[('out', 155, [[('xi1', 'out')]], 'clock')], bubbles=('out',), members=['xi1'])
    V.wire([(250, 160), (300, 160), (300, 155)], cls='clock'); V.netlabel('net57', 270, 160)

    box(V, 'xi2', 320, 220, 60, 50, 'ACAMP', 'xi2',
        left=[('in', 245, [[('xi2', 'in')]], 'clock')],
        top=[('en', 350, [[('xi2', 'en')]], 'data')],
        right=[('out', 245, [[('xi2', 'out')]], 'clock')], bubbles=('out',), members=['xi2'])
    V.wire([(250, 180), (280, 180), (280, 245), (300, 245)], cls='clock'); V.netlabel('net58', 270, 180)

    V.wire([(350, 70), (350, 110)], cls='data'); V.dot(350, 110)
    V.wire([(350, 110), (350, 200)], cls='data')

    # CCI cross-coupled inverters pair (2-pin parallel box)
    box(V, 'CCI', 440, 175, 50, 50, 'CCI', None,
        top=[('net59', 465, [[('xi3', 'a'), ('xi4', 'y')]], 'clock')],
        bottom=[('net60', 465, [[('xi4', 'a'), ('xi3', 'y')]], 'clock')],
        members=['xi3', 'xi4'])

    V.wire([(400, 155), (465, 155)], cls='clock'); V.netlabel('net59', 410, 155); V.dot(465, 155)
    V.wire([(465, 155), (520, 155)], cls='clock')

    V.wire([(400, 245), (465, 245)], cls='clock'); V.netlabel('net60', 410, 245); V.dot(465, 245)
    V.wire([(465, 245), (520, 245)], cls='clock')

    inv(V, 'xi5', 540, 155, 'xi5', [[('xi5', 'a')]], [[('xi5', 'y')]], members=['xi5'], cls='clock')
    inv(V, 'xi6', 660, 155, 'xi6', [[('xi6', 'a')]], [[('xi6', 'y')]], members=['xi6'], cls='clock')
    V.wire([(602, 155), (640, 155)], cls='clock'); V.netlabel('net61', 620, 155)
    V.wire([(722, 155), (800, 155)], cls='clock')
    V.port('ckt', 800, 155, d='right', io='out', cls='clock')

    inv(V, 'xi7', 540, 245, 'xi7', [[('xi7', 'a')]], [[('xi7', 'y')]], members=['xi7'], cls='clock')
    inv(V, 'xi8', 660, 245, 'xi8', [[('xi8', 'a')]], [[('xi8', 'y')]], members=['xi8'], cls='clock')
    V.wire([(602, 245), (640, 245)], cls='clock'); V.netlabel('net62', 620, 245)
    V.wire([(722, 245), (800, 245)], cls='clock')
    V.port('ckc', 800, 245, d='right', io='out', cls='clock')

    V.omitted = [
        {'net': 'vbn', 'class': '바이어스'},
        {'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}, {'net': 'vssq', 'class': '전원'}
    ]
    return V

# =============================================================================
# 17. VIEW_SLICE: b_slice
# =============================================================================
def view_slice():
    cell = 'dqslice'
    V = new_view('b_slice', cell, 'block', f'{cell} — 블록 레벨 (DQ 슬라이스)', 1150, 560)

    # Pad input and ESD/ODT
    V.port('pad', 60, 160, d='right', io='in')
    box(V, 'xi0', 100, 135, 60, 50, 'ESD', 'xi0',
        left=[('pad', 160, [[('xi0', 'pad')]], 'data')],
        right=[('pad_r', 160, [[('xi0', 'pad_r')]], 'data')], members=['xi0'])
    V.wire([(60, 160), (80, 160)], cls='data')

    box(V, 'xi1', 100, 220, 60, 50, 'ODT', 'xi1',
        left=[('pad', 245, [[('xi1', 'pad')]], 'data')],
        top=[('enb2', 110, [[('xi1', 'enb2')]], 'data'), ('enb1', 125, [[('xi1', 'enb1')]], 'data'), ('enb0', 140, [[('xi1', 'enb0')]], 'data')],
        members=['xi1'])
    V.wire([(70, 160), (70, 245), (80, 245)], cls='data'); V.dot(70, 160)

    V.port('odtb2', 110, 60, d='down', io='in'); V.wire([(110, 60), (110, 200)], cls='data')
    V.port('odtb1', 125, 60, d='down', io='in'); V.wire([(125, 60), (125, 200)], cls='data')
    V.port('odtb0', 140, 60, d='down', io='in'); V.wire([(140, 60), (140, 200)], cls='data')

    # SBAMP pair xi2 and xi3
    V.port('vref', 60, 310, d='right', io='in')

    box(V, 'xi2', 220, 130, 60, 60, 'SBAMP', 'xi2',
        left=[('inp', 145, [[('xi2', 'inp')]], 'data'), ('inn', 175, [[('xi2', 'inn')]], 'data')],
        top=[('en', 235, [[('xi2', 'en')]], 'data'), ('enb', 255, [[('xi2', 'enb')]], 'data')],
        right=[('out', 160, [[('xi2', 'out')]], 'data')], members=['xi2'])

    box(V, 'xi3', 220, 240, 60, 60, 'SBAMP', 'xi3',
        left=[('inp', 255, [[('xi3', 'inp')]], 'data'), ('inn', 285, [[('xi3', 'inn')]], 'data')],
        top=[('en', 235, [[('xi3', 'en')]], 'data'), ('enb', 255, [[('xi3', 'enb')]], 'data')],
        right=[('out', 270, [[('xi3', 'out')]], 'data')], members=['xi3'])

    # net92 connects xi0.pad_r(180, 160) to xi2.inp(200, 145) and xi3.inn(200, 285)
    V.wire([(180, 160), (190, 160)], cls='data'); V.netlabel('net92', 185, 160); V.dot(190, 160)
    V.wire([(190, 160), (190, 145), (200, 145)], cls='data')
    V.wire([(190, 160), (190, 285), (200, 285)], cls='data')

    # vref connects (60, 310) to xi2.inn(200, 175) and xi3.inp(200, 255)
    V.wire([(60, 310), (195, 310)], cls='data')
    V.wire([(195, 310), (195, 175), (200, 175)], cls='data'); V.dot(195, 255)
    V.wire([(195, 255), (200, 255)], cls='data')

    # Control ports en, enb routed around the left (x=170, 175) to avoid xi2.out at x=300
    V.port('en', 235, 45, d='down', io='in')
    V.wire([(235, 45), (235, 110)], cls='data'); V.dot(235, 80)
    V.wire([(235, 80), (170, 80), (170, 215), (235, 215), (235, 220)], cls='data')

    V.port('enb', 255, 45, d='down', io='in')
    V.wire([(255, 45), (255, 110)], cls='data'); V.dot(255, 70)
    V.wire([(255, 70), (165, 70), (165, 210), (255, 210), (255, 220)], cls='data')

    # SADFE pair xi4 (rising) and xi6 (falling)
    w_top = [
        ('w1_2', 450, [[('xi4', 'w1_2')]], 'data'),
        ('w1_1', 465, [[('xi4', 'w1_1')]], 'data'),
        ('w1_0', 480, [[('xi4', 'w1_0')]], 'data'),
        ('w2_1', 495, [[('xi4', 'w2_1')]], 'data'),
        ('w2_0', 510, [[('xi4', 'w2_0')]], 'data')
    ]
    box(V, 'xi4', 430, 120, 120, 100, 'SADFE', 'xi4',
        left=[('inp', 145, [[('xi4', 'inp')]], 'data'), ('inn', 165, [[('xi4', 'inn')]], 'data'),
              ('h1p', 195, [[('xi4', 'h1p')]], 'data'), ('h2p', 215, [[('xi4', 'h2p')]], 'data')],
        top=w_top,
        bottom=[('ck', 480, [[('xi4', 'ck')]], 'clock')],
        right=[('outp', 155, [[('xi4', 'outp')]], 'data'), ('outn', 175, [[('xi4', 'outn')]], 'data')],
        members=['xi4'])

    w_top_6 = [
        ('w1_2', 450, [[('xi6', 'w1_2')]], 'data'),
        ('w1_1', 465, [[('xi6', 'w1_1')]], 'data'),
        ('w1_0', 480, [[('xi6', 'w1_0')]], 'data'),
        ('w2_1', 495, [[('xi6', 'w2_1')]], 'data'),
        ('w2_0', 510, [[('xi6', 'w2_0')]], 'data')
    ]
    box(V, 'xi6', 430, 300, 120, 100, 'SADFE', 'xi6',
        left=[('inp', 325, [[('xi6', 'inp')]], 'data'), ('inn', 345, [[('xi6', 'inn')]], 'data'),
              ('h1p', 375, [[('xi6', 'h1p')]], 'data'), ('h2p', 395, [[('xi6', 'h2p')]], 'data')],
        top=w_top_6,
        bottom=[('ck', 480, [[('xi6', 'ck')]], 'clock')],
        right=[('outp', 335, [[('xi6', 'outp')]], 'data'), ('outn', 355, [[('xi6', 'outn')]], 'data')],
        members=['xi6'])

    # net93: xi2.out(300, 160) to xi4.inp(410, 145) and xi6.inp(410, 325)
    V.wire([(300, 160), (320, 160)], cls='data'); V.netlabel('net93', 310, 160); V.dot(320, 160)
    V.wire([(320, 160), (320, 145), (410, 145)], cls='data')
    V.wire([(320, 160), (320, 325), (410, 325)], cls='data')

    # net94: xi3.out(300, 270) to xi4.inn(410, 165) and xi6.inn(410, 345)
    V.wire([(300, 270), (325, 270)], cls='data'); V.netlabel('net94', 310, 270); V.dot(325, 270)
    V.wire([(325, 270), (325, 165), (410, 165)], cls='data')
    V.wire([(325, 270), (325, 345), (410, 345)], cls='data')

    # DFE weight ports and connections (distinct Y jogs and distinct X trunks)
    weights = ['w1_2', 'w1_1', 'w1_0', 'w2_1', 'w2_0']
    w_xs = [450, 465, 480, 495, 510]
    j_xs = [360, 355, 350, 345, 340]
    for i, wname in enumerate(weights):
        wx = w_xs[i]
        jx = j_xs[i]
        jy_top = 55 + 5 * i
        jy_bot = 255 + 5 * i
        V.port(wname, wx, 45, d='down', io='in')
        V.wire([(wx, 45), (wx, 100)], cls='data'); V.dot(wx, jy_top)
        V.wire([(wx, jy_top), (jx, jy_top), (jx, jy_bot), (wx, jy_bot), (wx, 280)], cls='data')

    # Clocks
    V.port('ckt', 560, 520, d='up', io='in', cls='clock')
    V.wire([(560, 520), (560, 250), (480, 250), (480, 240)], cls='clock')

    V.port('ckc', 480, 520, d='up', io='in', cls='clock')
    V.wire([(480, 520), (480, 420)], cls='clock')

    # SR Latches xi5 and xi7
    box(V, 'xi5', 610, 130, 70, 70, 'SRLATCH', 'xi5',
        left=[('rb', 155, [[('xi5', 'rb')]], 'data'), ('sb', 175, [[('xi5', 'sb')]], 'data')],
        right=[('q', 165, [[('xi5', 'q')]], 'data')], members=['xi5'])
    V.wire([(570, 155), (590, 155)], cls='data'); V.netlabel('net95', 580, 155)
    V.wire([(570, 175), (590, 175)], cls='data'); V.netlabel('net96', 580, 175)

    box(V, 'xi7', 610, 310, 70, 70, 'SRLATCH', 'xi7',
        left=[('rb', 335, [[('xi7', 'rb')]], 'data'), ('sb', 355, [[('xi7', 'sb')]], 'data')],
        right=[('q', 345, [[('xi7', 'q')]], 'data')], members=['xi7'])
    V.wire([(570, 335), (590, 335)], cls='data'); V.netlabel('net97', 580, 335)
    V.wire([(570, 355), (590, 355)], cls='data'); V.netlabel('net98', 580, 355)

    # Output inverters xi8, xi9 -> qr
    inv(V, 'xi8', 760, 165, 'xi8', [[('xi8', 'a')]], [[('xi8', 'y')]], members=['xi8'])
    V.wire([(700, 165), (720, 165)], cls='data'); V.netlabel('net99', 710, 165); V.dot(720, 165)
    V.wire([(720, 165), (740, 165)], cls='data')
    inv(V, 'xi9', 860, 165, 'xi9', [[('xi9', 'a')]], [[('xi9', 'y')]], members=['xi9'])
    V.wire([(822, 165), (840, 165)], cls='data'); V.netlabel('net103', 830, 165)
    V.wire([(922, 165), (980, 165)], cls='data')
    V.port('qr', 980, 165, d='right', io='out')

    # Output inverters xi10, xi11 -> qf
    inv(V, 'xi10', 760, 345, 'xi10', [[('xi10', 'a')]], [[('xi10', 'y')]], members=['xi10'])
    V.wire([(700, 345), (720, 345)], cls='data'); V.netlabel('net101', 710, 345); V.dot(720, 345)
    V.wire([(720, 345), (740, 345)], cls='data')
    inv(V, 'xi11', 860, 345, 'xi11', [[('xi11', 'a')]], [[('xi11', 'y')]], members=['xi11'])
    V.wire([(822, 345), (840, 345)], cls='data'); V.netlabel('net104', 830, 345)
    V.wire([(922, 345), (980, 345)], cls='data')
    V.port('qf', 980, 345, d='right', io='out')

    # Feedback:
    # net99 from (720, 165) to xi4.h2p(410, 215) and xi6.h1p(410, 375)
    V.wire([(720, 165), (720, 85), (380, 85), (380, 215), (410, 215)], cls='data'); V.dot(380, 215)
    V.wire([(380, 215), (380, 375), (410, 375)], cls='data')

    # net101 from (720, 345) to xi4.h1p(410, 195) and xi6.h2p(410, 395)
    V.wire([(720, 345), (720, 480), (370, 480), (370, 395), (410, 395)], cls='data'); V.dot(370, 395)
    V.wire([(370, 395), (370, 195), (410, 195)], cls='data')

    V.omitted = [
        {'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}, {'net': 'vssq', 'class': '전원'},
        {'net': 'net100', 'class': '내부'}, {'net': 'net102', 'class': '내부'}
    ]
    return V

def view_top():
    cell = 'rxbyte_top'
    V = new_view('b_top', cell, 'block', f'{cell} — 블록 레벨 (최상위 수신기)', 1400, 600)
    rail(V, 60, 1350, 70, 'vdd', 'VDD')

    # PMOS power switch mp0 at (120, 110)
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', 120, 110, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(120, 80), (120, 70)], cls='power'); V.dot(120, 70)
    V.port('slp', 60, 110, d='right', io='in')
    V.wire([(60, 110), (80, 110)], cls='data')

    # Control port rx_en at (60, 180)
    V.port('rx_en', 60, 180, d='right', io='in')

    # DQS pads & ESD
    V.port('dqs_t', 60, 240, d='right', io='in', cls='clock')
    V.port('dqs_c', 60, 300, d='right', io='in', cls='clock')
    
    box(V, 'xi4', 160, 225, 50, 30, 'ESD', 'xi4',
        left=[('pad', 240, [[('xi4', 'pad')]], 'clock')],
        right=[('pad_r', 240, [[('xi4', 'pad_r')]], 'clock')],
        members=['xi4'])
    V.wire([(60, 240), (140, 240)], cls='clock'); V.dot(90, 240)

    box(V, 'xi5', 160, 285, 50, 30, 'ESD', 'xi5',
        left=[('pad', 300, [[('xi5', 'pad')]], 'clock')],
        right=[('pad_r', 300, [[('xi5', 'pad_r')]], 'clock')],
        members=['xi5'])
    V.wire([(60, 300), (140, 300)], cls='clock'); V.dot(100, 300)

    # DQS ODT legs xi6 and xi7: enb on top at x=170, pad on bottom at x=190
    odt_enb_6 = [[('xi6', 'enb%d' % i)] for i in range(3)]
    box(V, 'xi6', 150, 345, 60, 30, 'ODT', 'xi6',
        top=[('enb<2:0>', 170, odt_enb_6, 'bus')],
        bottom=[('pad', 190, [[('xi6', 'pad')]], 'clock')],
        members=['xi6'])
    odt_enb_7 = [[('xi7', 'enb%d' % i)] for i in range(3)]
    box(V, 'xi7', 150, 420, 60, 30, 'ODT', 'xi7',
        top=[('enb<2:0>', 170, odt_enb_7, 'bus')],
        bottom=[('pad', 190, [[('xi7', 'pad')]], 'clock')],
        members=['xi7'])

    # dqs_t to xi6.pad(190, 395) via separate trunk at x=90
    V.wire([(90, 240), (90, 395), (190, 395)], cls='clock')
    # dqs_c to xi7.pad(190, 470) via separate trunk at x=100
    V.wire([(100, 300), (100, 470), (190, 470)], cls='clock')

    # DQS RX (xi8): w=90, h=90 at (290, 215)
    box(V, 'xi8', 290, 215, 90, 90, 'DQSRX', 'xi8',
        left=[('inp', 240, [[('xi8', 'inp')]], 'clock'), ('inn', 290, [[('xi8', 'inn')]], 'clock')],
        top=[('en', 315, [[('xi8', 'en')]], 'data'), ('enq', 355, [[('xi8', 'enq')]], 'data')],
        right=[('ckt', 240, [[('xi8', 'ckt')]], 'clock'), ('ckc', 280, [[('xi8', 'ckc')]], 'clock')],
        members=['xi8'])
    V.wire([(230, 240), (270, 240)], cls='clock'); V.netlabel('net208', 250, 240)
    V.wire([(230, 300), (250, 300), (250, 290), (270, 290)], cls='clock'); V.netlabel('net209', 245, 300)

    # LVLUP xi0 at (170, 510): in on top, out/outb on right
    box(V, 'xi0', 170, 510, 50, 40, 'LVLUP', 'xi0',
        top=[('in', 195, [[('xi0', 'in')]], 'data')],
        right=[('out', 520, [[('xi0', 'out')]], 'data'), ('outb', 535, [[('xi0', 'outb')]], 'data')],
        bubbles=('outb',),
        members=['xi0'])

    # BIASGEN xi1 at (260, 510): w=70, en on top at x=295
    box(V, 'xi1', 260, 510, 70, 40, 'BIASGEN', 'xi1',
        top=[('en', 295, [[('xi1', 'en')]], 'data')],
        members=['xi1'])

    # rx_en distribution: to xi8.en(315, 195), xi0.in(195, 490), xi1.en(295, 490)
    V.wire([(60, 180), (315, 180), (315, 195)], cls='data')
    V.wire([(80, 180), (80, 475), (195, 475), (195, 490)], cls='data'); V.dot(80, 180); V.dot(195, 475)
    V.wire([(195, 475), (295, 475), (295, 490)], cls='data')

    # net201 (xi0.out) and net202 (xi0.outb)
    # xi0 right pins are at (240, 520) and (240, 535)
    V.wire([(240, 520), (250, 520)], cls='data'); V.netlabel('net201', 250, 520)
    V.wire([(355, 195), (355, 150), (905, 150), (905, 160)], cls='data'); V.netlabel('net201', 370, 150)

    V.wire([(240, 535), (250, 535)], cls='data'); V.netlabel('net202', 250, 535)
    V.wire([(925, 160), (925, 140)], cls='data'); V.netlabel('net202', 925, 140)

    # net200: mp0 drain at (120, 140) to DQ_SLICES.net200(880, 160)
    V.wire([(120, 140), (120, 130), (880, 130), (880, 160)], cls='power')
    V.netlabel('net200', 140, 130)

    # DQS Gate (xi9)
    box(V, 'xi9', 430, 220, 70, 70, 'DQSGATE', 'xi9',
        left=[('ckt', 240, [[('xi9', 'ckt')]], 'clock'), ('ckc', 280, [[('xi9', 'ckc')]], 'clock')],
        top=[('open', 465, [[('xi9', 'open')]], 'data')],
        right=[('gt', 240, [[('xi9', 'gt')]], 'clock'), ('gc', 280, [[('xi9', 'gc')]], 'clock')],
        members=['xi9'])
    V.wire([(400, 240), (410, 240)], cls='clock'); V.netlabel('net210', 405, 240)
    V.wire([(400, 280), (410, 280)], cls='clock'); V.netlabel('net211', 405, 280)
    V.port('gate_open', 465, 120, d='down', io='in')
    V.wire([(465, 120), (465, 200)], cls='data')

    # DLY3 pair (xi10, xi11) at x0=560
    ddl_terms_10 = [[('xi10', 's%d' % i)] for i in range(3)]
    box(V, 'xi10', 560, 225, 60, 40, 'DLY3', 'xi10',
        left=[('in', 240, [[('xi10', 'in')]], 'clock')],
        top=[('ddl<2:0>', 590, ddl_terms_10, 'bus')],
        right=[('out', 240, [[('xi10', 'out')]], 'clock')],
        members=['xi10', 'd0'])
    V.wire([(520, 240), (540, 240)], cls='clock'); V.netlabel('net212', 530, 240)

    ddl_terms_11 = [[('xi11', 's%d' % i)] for i in range(3)]
    box(V, 'xi11', 560, 285, 60, 40, 'DLY3', 'xi11',
        left=[('in', 300, [[('xi11', 'in')]], 'clock')],
        top=[('ddl<2:0>', 590, ddl_terms_11, 'bus')],
        right=[('out', 300, [[('xi11', 'out')]], 'clock')],
        members=['xi11', 'd1'])
    V.wire([(520, 280), (520, 300), (540, 300)], cls='clock'); V.netlabel('net213', 530, 300)

    # ddl<2:0> bus port
    V.port('ddl<2:0>', 590, 120, d='down', io='in', cls='bus')
    V.wire([(590, 120), (590, 205)], cls='bus'); V.dot(590, 170)
    busslash(V, 590, 145, 'ddl<2:0>', 3, vertical=False)
    V.wire([(590, 170), (530, 170), (530, 275), (590, 275), (590, 265)], cls='bus')

    # Clock Tree at x0=670
    box(V, 'xi12', 670, 220, 110, 50, 'CK_TREE_T', None,
        left=[('in', 240, [[('xi12', 'a')]], 'clock')],
        right=[('ckt0_3', 230, [[('xi14', 'y'), ('xi15', 'y')]], 'clock'),
               ('ckt4_7', 245, [[('xi18', 'y'), ('xi19', 'y')]], 'clock'),
               ('ckt_wl', 260, [[('xi22', 'y')]], 'clock')],
        members=['xi12', 'xi14', 'xi15', 'xi18', 'xi19', 'xi22'])
    V.wire([(640, 240), (650, 240)], cls='clock'); V.netlabel('net214', 645, 240)

    box(V, 'xi13', 670, 290, 110, 50, 'CK_TREE_C', None,
        left=[('in', 300, [[('xi13', 'a')]], 'clock')],
        right=[('ckc0_3', 300, [[('xi16', 'y'), ('xi17', 'y')]], 'clock'),
               ('ckc4_7', 315, [[('xi20', 'y'), ('xi21', 'y')]], 'clock'),
               ('ckc_wl', 330, [[('xi23', 'y')]], 'clock')],
        members=['xi13', 'xi16', 'xi17', 'xi20', 'xi21', 'xi23'])
    V.wire([(640, 300), (650, 300)], cls='clock'); V.netlabel('net215', 645, 300)

    # DQ Slices bundle at x0=860
    dq_pad_terms = [[('xi%d' % (30 + i), 'pad')] for i in range(8)]
    dq_qr_terms = [[('xi%d' % (30 + i), 'qr')] for i in range(8)]
    dq_qf_terms = [[('xi%d' % (30 + i), 'qf')] for i in range(8)]
    dq_ckt0_terms = [[('xi%d' % (30 + i), 'ckt') for i in range(4)]]
    dq_ckt4_terms = [[('xi%d' % (34 + i), 'ckt') for i in range(4)]]
    dq_ckc0_terms = [[('xi%d' % (30 + i), 'ckc') for i in range(4)]]
    dq_ckc4_terms = [[('xi%d' % (34 + i), 'ckc') for i in range(4)]]
    dq_vref_terms = [[('xi%d' % (30 + i), 'vref') for i in range(8)]]
    dq_en_terms = [[('xi%d' % (30 + i), 'en') for i in range(8)]]
    dq_enb_terms = [[('xi%d' % (30 + i), 'enb') for i in range(8)]]
    dq_t1w_terms = [[('xi%d' % (30 + j), 'w1_%d' % i) for j in range(8)] for i in range(3)]
    dq_t2w_terms = [[('xi%d' % (30 + j), 'w2_%d' % i) for j in range(8)] for i in range(2)]
    dq_odtb_terms = [[('xi%d' % (30 + j), 'odtb%d' % i) for j in range(8)] for i in range(3)]
    dq_net200_terms = [[('xi%d' % (30 + i), 'vdd')] for i in range(8)]

    box(V, 'DQ_SLICES', 860, 180, 140, 180, '8×DQ_SLICE', None,
        left=[('dq<7:0>', 200, dq_pad_terms, 'bus'),
              ('vref', 220, dq_vref_terms, 'data'),
              ('ckt0_3', 240, dq_ckt0_terms, 'clock'),
              ('ckc0_3', 260, dq_ckc0_terms, 'clock'),
              ('ckt4_7', 280, dq_ckt4_terms, 'clock'),
              ('ckc4_7', 300, dq_ckc4_terms, 'clock')],
        top=[('net200', 880, dq_net200_terms, 'power'),
             ('en', 905, dq_en_terms, 'data'),
             ('enb', 925, dq_enb_terms, 'data'),
             ('t1w<2:0>', 950, dq_t1w_terms, 'bus'),
             ('t2w<1:0>', 975, dq_t2w_terms, 'bus')],
        bottom=[('odtb<2:0>', 930, dq_odtb_terms, 'bus')],
        right=[('qr<7:0>', 230, dq_qr_terms, 'bus'), ('qf<7:0>', 290, dq_qf_terms, 'bus')],
        members=['xi30', 'xi31', 'xi32', 'xi33', 'xi34', 'xi35', 'xi36', 'xi37'])

    # Clock tree to DQ_SLICES connections
    V.wire([(800, 230), (840, 230), (840, 240)], cls='clock'); V.netlabel('net218', 815, 230)
    V.wire([(800, 300), (835, 300), (835, 260), (840, 260)], cls='clock'); V.netlabel('net219', 815, 300)
    V.wire([(800, 245), (830, 245), (830, 280), (840, 280)], cls='clock'); V.netlabel('net220', 815, 245)
    V.wire([(800, 315), (840, 315), (840, 300)], cls='clock'); V.netlabel('net221', 815, 315)

    # DQ<7:0> Bus Input
    V.port('dq<7:0>', 790, 200, d='right', io='in', cls='bus')
    V.wire([(790, 200), (840, 200)], cls='bus')
    busslash(V, 810, 200, 'dq<7:0>', 8)

    # QR<7:0> and QF<7:0> Bus Outputs
    V.wire([(1020, 230), (1100, 230)], cls='bus')
    V.port('qr<7:0>', 1100, 230, d='right', io='out', cls='bus')
    busslash(V, 1060, 230, 'qr<7:0>', 8)

    V.wire([(1020, 290), (1100, 290)], cls='bus')
    V.port('qf<7:0>', 1100, 290, d='right', io='out', cls='bus')
    busslash(V, 1060, 290, 'qf<7:0>', 8)

    # Top Control Ports: t1w<2:0> and t2w<1:0>
    V.port('t1w<2:0>', 950, 110, d='down', io='in', cls='bus')
    V.wire([(950, 110), (950, 160)], cls='bus')
    busslash(V, 950, 135, 't1w<2:0>', 3, vertical=False)

    V.port('t2w<1:0>', 975, 110, d='down', io='in', cls='bus')
    V.wire([(975, 110), (975, 160)], cls='bus')
    busslash(V, 975, 135, 't2w<1:0>', 2, vertical=False)

    # Reference / Bias generator blocks
    # VREFDAC xi2: c<5:0> on bottom (at y=490)
    vrc_terms = [[('xi2', 'c%d' % i)] for i in range(6)]
    box(V, 'xi2', 370, 420, 80, 50, 'VREFDAC', 'xi2',
        bottom=[('c<5:0>', 410, vrc_terms, 'bus')],
        right=[('vref', 445, [[('xi2', 'vref')]], 'data')],
        members=['xi2'])
    V.port('vrc<5:0>', 410, 560, d='up', io='in', cls='bus')
    V.wire([(410, 560), (410, 490)], cls='bus')
    busslash(V, 410, 530, 'vrc<5:0>', 6, vertical=False)

    # net204 (vref) from xi2 at y=445 to DQ_SLICES.vref(840, 220) and xi38.vref(890, 500)
    V.wire([(470, 445), (845, 445), (845, 220), (840, 220)], cls='data'); V.netlabel('net204', 490, 445); V.dot(845, 445)
    V.wire([(845, 445), (845, 520), (890, 520), (890, 500)], cls='data')

    # ODTCTL xi3: enb<2:0> at y=460, odt_en and rtt<2:0> on bottom!
    rtt_terms = [[('xi3', 'rtt%d' % i)] for i in range(3)]
    odtb_terms = [[('xi3', 'enb%d' % i)] for i in range(3)]
    box(V, 'xi3', 490, 435, 80, 50, 'ODTCTL', 'xi3',
        bottom=[('odt_en', 510, [[('xi3', 'odt_en')]], 'data'), ('rtt<2:0>', 545, rtt_terms, 'bus')],
        right=[('enb<2:0>', 460, odtb_terms, 'bus')],
        members=['xi3'])
    V.port('odt_en', 510, 560, d='up', io='in')
    V.wire([(510, 560), (510, 505)], cls='data')
    V.port('rtt<2:0>', 545, 560, d='up', io='in', cls='bus')
    V.wire([(545, 560), (545, 505)], cls='bus')
    busslash(V, 545, 530, 'rtt<2:0>', 3, vertical=False)

    # odtb<2:0> from xi3: routes up to y=370, across to DQ_SLICES(930, 380) and xi6/xi7(170)
    V.wire([(590, 460), (600, 460), (600, 370), (930, 370), (930, 380)], cls='bus'); V.dot(600, 370)
    busslash(V, 650, 370, 'odtb<2:0>', 3)
    # branch left at y=370 to xi6(170, 325) and xi7(170, 400)
    V.wire([(600, 370), (170, 370)], cls='bus'); V.dot(170, 370)
    V.wire([(170, 370), (170, 325)], cls='bus')
    V.wire([(170, 370), (170, 400)], cls='bus')

    # Timing Slice xi38: vref, ckt, ckc on bottom!
    box(V, 'xi38', 870, 420, 110, 60, 'DUMMY_SLICE', None,
        bottom=[('vref', 890, [[('xi38', 'vref')]], 'data'),
                ('ckt', 920, [[('xi38', 'ckt')]], 'clock'),
                ('ckc', 950, [[('xi38', 'ckc')]], 'clock')],
        members=['xi38'])

    # Clock tree to xi38 and xi39: net222 and net223
    # net222 from CK_TREE_T (800, 260) -> (820, 260) -> (820, 540) -> xi38.ckt(920, 540) -> (920, 500) and xi39.ck(1065, 540)
    V.wire([(800, 260), (820, 260), (820, 540), (920, 540), (920, 500)], cls='clock'); V.netlabel('net222', 820, 350); V.dot(920, 540)
    # net223 from CK_TREE_C (800, 330) -> (830, 330) -> (830, 530) -> xi38.ckc(950, 530) -> (950, 500)
    V.wire([(800, 330), (830, 330), (830, 530), (950, 530), (950, 500)], cls='clock'); V.netlabel('net223', 830, 400)

    # xi39 WLDET at x0=1020
    box(V, 'xi39', 1020, 420, 90, 60, 'WLDET', 'xi39',
        top=[('d', 1050, [[('xi39', 'd')]], 'data'), ('en', 1080, [[('xi39', 'en')]], 'data')],
        bottom=[('ck', 1065, [[('xi39', 'ck')]], 'clock')],
        right=[('q', 450, [[('xi39', 'q')]], 'data')],
        members=['xi39'])

    # wl_ck port to xi39.d(1050, 400)
    V.port('wl_ck', 1050, 110, d='down', io='in')
    V.wire([(1050, 110), (1050, 400)], cls='data')

    # wl_en port to xi39.en(1080, 400)
    V.port('wl_en', 1080, 110, d='down', io='in')
    V.wire([(1080, 110), (1080, 400)], cls='data')

    # net222 to xi39.ck(1065, 500)
    V.wire([(920, 540), (1065, 540), (1065, 500)], cls='clock')

    # wl_out port from xi39.q(1130, 450)
    V.wire([(1130, 450), (1200, 450)], cls='data')
    V.port('wl_out', 1200, 450, d='right', io='out')

    V.omitted = [
        {'net': 'ibias', 'class': '바이어스'},
        {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'},
        {'net': 'vssq', 'class': '전원'},
        {'net': 'net203', 'class': '바이어스'},
        {'net': 'net216', 'class': '클럭'},
        {'net': 'net217', 'class': '클럭'},
        {'net': 'net224', 'class': '내부'},
        {'net': 'net225', 'class': '내부'}
    ]
    return V


# =============================================================================
# BUILD ALL
# =============================================================================
def build_all():
    view_inv()
    view_lvlup()
    view_ckbuf()
    view_padesd()
    view_odtleg3()
    view_sbamp()
    view_dqsamp()
    view_acamp()
    view_srnand()
    view_sadfe()
    view_vrefdac()
    view_odtctl()
    view_wldet()
    view_dly3()
    view_dqsgate()
    view_dqsrx()
    view_slice()
    view_top()

    out = []
    for v in VIEWS:
        d = dict(v.__dict__)
        d.pop('_tid', None)
        out.append(d)
    with open(W + '/scenes.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=0, default=list, ensure_ascii=False)
    print(f"Generated {len(VIEWS)} views into {W}/scenes.json")

if __name__ == '__main__':
    build_all()
