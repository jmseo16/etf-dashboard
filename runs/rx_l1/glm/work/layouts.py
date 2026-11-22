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
    g = [[(name, 'g')]]
    return top, bot, g

def new_view(sid, cell, level, title, w, h):
    V = View(sid, cell, level, title, w=w, h=h)
    VIEWS.append(V)
    return V

# =============================================================================
# 1. VIEW_INVX1: u_invx1
# =============================================================================
def view_invx1():
    cell = 'invx1'
    V = new_view('u_invx1', cell, 'unit', f'{cell} — unit level (인버터)', 480, 400)
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
# 2. VIEW_LVLUP: u_lvlup
# =============================================================================
def view_lvlup():
    cell = 'lvlup'
    V = new_view('u_lvlup', cell, 'unit', f'{cell} — unit level (레벨 시프터)', 800, 480)
    rail(V, 60, 740, 70, 'vddq', 'VDDQ')
    rail(V, 60, 740, 410, 'vss', 'VSS')
    rail(V, 60, 240, 130, 'vdd', 'VDD')

    # Input inverter mp2 / mn2 at X = 150
    tp2, bp2, gp2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 150, 200, 'p', 'left', 'mp2', wl(cell, 'mp2'), tp2, bp2, gp2, members=['mp2'])
    V.wire([(150, 170), (150, 130)], cls='power'); V.dot(150, 130)

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 150, 320, 'n', 'left', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(150, 350), (150, 410)], cls='power'); V.dot(150, 410)

    # Input wire 'in'
    V.wire([(110, 200), (110, 320)], cls='data')
    V.wire([(70, 260), (110, 260)], cls='data'); V.dot(110, 260)
    V.port('in', 70, 260, d='right', io='in')

    # Inverter output net4
    V.wire([(150, 230), (150, 290)], cls='plain'); V.dot(150, 260)
    V.wire([(150, 260), (450, 260), (450, 340)], cls='plain')

    # Differential pair mn0 at X = 330, mn1 at X = 490
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 330, 340, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(330, 370), (330, 410)], cls='power'); V.dot(330, 410)
    V.wire([(110, 260), (290, 260), (290, 340)], cls='data'); V.dot(110, 260)

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

    # Drain connections: mp0.d -> mn0.d (net5), mp1.d -> mn1.d (net6)
    V.wire([(330, 190), (330, 310)], cls='plain'); V.dot(330, 230)
    V.wire([(490, 190), (490, 310)], cls='plain'); V.dot(490, 230)

    # Cross coupling
    V.wire([(330, 230), (530, 230), (530, 160)], cls='plain')
    V.wire([(490, 210), (290, 210), (290, 160)], cls='plain'); V.dot(490, 210)

    # Output inverters mp3/mn3 (out from net5) at X = 630, mp4/mn4 (outb from net6) at X = 710
    tp3, bp3, gp3 = mosT(cell, 'mp3')
    mos(V, 'mp3', 630, 160, 'p', 'left', 'mp3', wl(cell, 'mp3'), tp3, bp3, gp3, members=['mp3'])
    V.wire([(630, 130), (630, 70)], cls='power'); V.dot(630, 70)

    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 630, 340, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])
    V.wire([(630, 370), (630, 410)], cls='power'); V.dot(630, 410)

    # net5 feeds mp3/mn3 gates
    V.wire([(330, 230), (590, 230)], cls='plain')
    V.wire([(590, 160), (590, 340)], cls='plain'); V.dot(590, 230)
    V.wire([(630, 190), (630, 250), (670, 250)], cls='data'); V.dot(630, 250)
    V.wire([(630, 310), (630, 250)], cls='data')
    V.port('out', 670, 250, d='right', io='out')

    tp4, bp4, gp4 = mosT(cell, 'mp4')
    mos(V, 'mp4', 710, 160, 'p', 'left', 'mp4', wl(cell, 'mp4'), tp4, bp4, gp4, members=['mp4'])
    V.wire([(710, 130), (710, 70)], cls='power'); V.dot(710, 70)

    tn4, bn4, gn4 = mosT(cell, 'mn4')
    mos(V, 'mn4', 710, 340, 'n', 'left', 'mn4', wl(cell, 'mn4'), tn4, bn4, gn4, members=['mn4'])
    V.wire([(710, 370), (710, 410)], cls='power'); V.dot(710, 410)

    # net6 feeds mp4/mn4 gates
    V.wire([(490, 210), (670, 210), (670, 160)], cls='plain')
    V.wire([(670, 160), (670, 340)], cls='plain')
    V.wire([(710, 190), (710, 250), (750, 250)], cls='data'); V.dot(710, 250)
    V.wire([(710, 310), (710, 250)], cls='data')
    V.port('outb', 750, 250, d='right', io='out')

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
    res(V, 'r0', 160, 120, orient='h', name='r0', size='', a=[('r0', 'p')], b=[('r0', 'n')], members=['r0'])
    V.wire([(60, 120), (130, 120)], cls='data')
    V.wire([(190, 120), (460, 120)], cls='data'); V.dot(280, 120)
    V.port('pad_r', 460, 120, d='right', io='out')

    tn, bn, gn = mosT(cell, 'mn0')
    mos(V, 'mn0', 280, 200, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn, bn, gn, members=['mn0'])
    V.wire([(280, 120), (280, 170)], cls='data')
    V.wire([(280, 230), (280, 300)], cls='power'); V.dot(280, 300)

    # r1 from net21 (mn0.g) to vssq
    V.wire([(240, 200), (200, 200), (200, 220)], cls='plain')
    res(V, 'r1', 200, 250, orient='v', name='r1', size='', a=[('r1', 'p')], b=[('r1', 'n')], members=['r1'])
    V.wire([(200, 280), (200, 300)], cls='power'); V.dot(200, 300)

    V.omitted = [{'net': 'vddq', 'class': '전원'}]
    return V

# =============================================================================
# 5. VIEW_ODTLEG3: u_odtleg3
# =============================================================================
def view_odtleg3():
    cell = 'odtleg3'
    V = new_view('u_odtleg3', cell, 'unit', f'{cell} — unit level (종단 레그)', 680, 440)
    rail(V, 80, 600, 70, 'vddq', 'VDDQ')

    for i, (mname, rname, enb, x) in enumerate([('mp0', 'r0', 'enb0', 180),
                                                ('mp1', 'r1', 'enb1', 320),
                                                ('mp2', 'r2', 'enb2', 460)]):
        tp, bp, gp = mosT(cell, mname)
        mos(V, mname, x, 150, 'p', 'left', mname, wl(cell, mname), tp, bp, gp, members=[mname])
        V.wire([(x, 120), (x, 70)], cls='power'); V.dot(x, 70)
        V.wire([(x - 40, 150), (x - 70, 150)], cls='bus')
        V.port(enb, x - 70, 150, d='right', io='in', cls='bus')

        res(V, rname, x, 250, orient='v', name=rname, size='', a=[(rname, 'p')], b=[(rname, 'n')], members=[rname])
        V.wire([(x, 180), (x, 220)], cls='plain')
        V.wire([(x, 280), (x, 340)], cls='data')

    V.wire([(180, 340), (460, 340)], cls='data')
    V.dot(180, 340); V.dot(320, 340); V.dot(460, 340)
    V.wire([(460, 340), (580, 340)], cls='data')
    V.port('pad', 580, 340, d='right', io='in')

    V.omitted = []
    return V

# =============================================================================
# 6. VIEW_SBAMP: u_sbamp
# =============================================================================
def view_sbamp():
    cell = 'sbamp'
    V = new_view('u_sbamp', cell, 'unit', f'{cell} — unit level (차동 프리앰프)', 720, 500)
    rail(V, 80, 640, 70, 'vddq', 'VDDQ')
    rail(V, 80, 640, 430, 'vssq', 'VSSQ')

    # Header enable mp6 at X = 240, y = 130
    tp6, bp6, gp6 = mosT(cell, 'mp6')
    mos(V, 'mp6', 240, 130, 'p', 'left', 'mp6', wl(cell, 'mp6'), tp6, bp6, gp6, members=['mp6'])
    V.wire([(240, 100), (240, 70)], cls='power'); V.dot(240, 70)
    V.wire([(120, 130), (200, 130)], cls='data')
    V.port('enb', 120, 130, d='right', io='in')

    # Diode-connected load mp5 (top) and mn5 (bot) at X = 240
    tp5, bp5, gp5 = mosT(cell, 'mp5')
    mos(V, 'mp5', 240, 210, 'p', 'left', 'mp5', wl(cell, 'mp5'), tp5, bp5, gp5, members=['mp5'])
    V.wire([(240, 160), (240, 180)], cls='plain') # net80

    tn5, bn5, gn5 = mosT(cell, 'mn5')
    mos(V, 'mn5', 240, 290, 'n', 'left', 'mn5', wl(cell, 'mn5'), tn5, bn5, gn5, members=['mn5'])

    # Footer enable mn6 at X = 240, y = 370
    tn6, bn6, gn6 = mosT(cell, 'mn6')
    mos(V, 'mn6', 240, 370, 'n', 'left', 'mn6', wl(cell, 'mn6'), tn6, bn6, gn6, members=['mn6'])
    V.wire([(240, 320), (240, 340)], cls='plain') # net83
    V.wire([(240, 400), (240, 430)], cls='power'); V.dot(240, 430)
    V.wire([(120, 370), (200, 370)], cls='data')
    V.port('en', 120, 370, d='right', io='in')

    # Differential pair: Left branch mp1/mn1 (inp) at X = 420; Right branch mp2/mn2 (inn) at X = 540
    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 420, 210, 'p', 'left', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 420, 290, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])

    tp2, bp2, gp2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 540, 210, 'p', 'right', 'mp2', wl(cell, 'mp2'), tp2, bp2, gp2, members=['mp2'])

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 540, 290, 'n', 'right', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])

    # Rails net81 and net82 connecting sources
    V.wire([(240, 240), (420, 180), (540, 180)], cls='plain') # net81
    V.wire([(240, 260), (420, 320), (540, 320)], cls='plain') # net82

    # net79 (drain of mp1/mn1) connects to gate of mp5/mn5
    V.wire([(420, 240), (420, 260)], cls='plain'); V.dot(420, 250)
    V.wire([(420, 250), (330, 250), (330, 210), (200, 210)], cls='plain'); V.dot(330, 250)
    V.wire([(330, 250), (330, 290), (200, 290)], cls='plain')

    # Inputs inp and inn
    V.wire([(380, 210), (380, 290)], cls='data')
    V.wire([(320, 250), (380, 250)], cls='data'); V.dot(380, 250)
    V.port('inp', 320, 250, d='right', io='in')

    V.wire([(580, 210), (580, 290)], cls='data')
    V.wire([(580, 250), (620, 250)], cls='data'); V.dot(580, 250)
    V.port('inn', 620, 250, d='left', io='in')

    # Output out from mp2/mn2 drains
    V.wire([(540, 240), (540, 260)], cls='data'); V.dot(540, 250)
    V.wire([(540, 250), (640, 250)], cls='data')
    V.port('out', 640, 250, d='right', io='out')

    V.omitted = []
    return V

# =============================================================================
# 7. VIEW_DQSAMP: u_dqsamp
# =============================================================================
def view_dqsamp():
    cell = 'dqsamp'
    V = new_view('u_dqsamp', cell, 'unit', f'{cell} — unit level (CML 클럭 버퍼)', 640, 480)
    rail(V, 80, 560, 70, 'vddq', 'VDDQ')
    rail(V, 80, 560, 410, 'vssq', 'VSSQ')

    # Load resistors r0 (outn) at X = 240, r1 (outp) at X = 400
    res(V, 'r0', 240, 130, orient='v', name='r0', size='', a=[('r0', 'p')], b=[('r0', 'n')], members=['r0'])
    V.wire([(240, 100), (240, 70)], cls='power'); V.dot(240, 70)
    V.wire([(240, 160), (240, 210)], cls='clock'); V.dot(240, 190)
    V.wire([(240, 190), (140, 190)], cls='clock')
    V.port('outn', 140, 190, d='left', io='out', cls='clock')

    res(V, 'r1', 400, 130, orient='v', name='r1', size='', a=[('r1', 'p')], b=[('r1', 'n')], members=['r1'])
    V.wire([(400, 100), (400, 70)], cls='power'); V.dot(400, 70)
    V.wire([(400, 160), (400, 210)], cls='clock'); V.dot(400, 190)
    V.wire([(400, 190), (500, 190)], cls='clock')
    V.port('outp', 500, 190, d='right', io='out', cls='clock')

    # Differential pair: mn0 (inp -> outn) at X = 240; mn1 (inn -> outp) at X = 400
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 240, 240, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(200, 240), (120, 240)], cls='clock')
    V.port('inp', 120, 240, d='right', io='in', cls='clock')

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 400, 240, 'n', 'right', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(440, 240), (520, 240)], cls='clock')
    V.port('inn', 520, 240, d='left', io='in', cls='clock')

    # Common source node net52
    V.wire([(240, 270), (240, 290), (400, 290), (400, 270)], cls='plain')
    V.dot(320, 290)

    # Tail transistors mn2 (en) and mn3 (vbn) at X = 320
    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 320, 320, 'n', 'left', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(320, 290), (320, 290)], cls='plain')
    V.wire([(280, 320), (200, 320)], cls='data')
    V.port('en', 200, 320, d='right', io='in')

    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 320, 380, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])
    V.wire([(320, 350), (320, 350)], cls='plain') # net53
    V.wire([(320, 410), (320, 410)], cls='power'); V.dot(320, 410)
    V.wire([(280, 380), (200, 380)], cls='plain')
    V.port('vbn', 200, 380, d='right', io='in')

    V.omitted = []
    return V

# =============================================================================
# 8. VIEW_ACAMP: u_acamp
# =============================================================================
def view_acamp():
    cell = 'acamp'
    V = new_view('u_acamp', cell, 'unit', f'{cell} — unit level (AC 증폭기)', 680, 420)
    rail(V, 80, 600, 70, 'vdd', 'VDD')
    rail(V, 80, 600, 350, 'vss', 'VSS')

    # AC coupling cap c0
    V.port('in', 60, 200, d='right', io='in', cls='clock')
    cap(V, 'c0', 140, 200, orient='h', name='c0', size='', a=[('c0', 'p')], b=[('c0', 'n')], members=['c0'])
    V.wire([(60, 200), (110, 200)], cls='clock')
    V.wire([(170, 200), (220, 200)], cls='clock'); V.dot(220, 200)

    # Feedback resistor r0 from net54 to net55
    res(V, 'r0', 220, 130, orient='h', name='r0', size='', a=[('r0', 'p')], b=[('r0', 'n')], members=['r0'])
    V.wire([(220, 200), (220, 130), (190, 130)], cls='plain')
    V.wire([(250, 130), (340, 130), (340, 200)], cls='plain')

    # CMOS inverter mp0 / mn0 with tail mn1 and header mp1
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', 300, 160, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(300, 130), (300, 70)], cls='power'); V.dot(300, 70)

    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 300, 250, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])

    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 300, 310, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(300, 280), (300, 280)], cls='plain') # net56
    V.wire([(300, 340), (300, 350)], cls='power'); V.dot(300, 350)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 380, 160, 'p', 'right', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(380, 130), (380, 70)], cls='power'); V.dot(380, 70)

    # Enable port
    V.wire([(200, 310), (260, 310)], cls='data'); V.dot(200, 310)
    V.wire([(200, 160), (420, 160)], cls='data')
    V.wire([(200, 160), (200, 310)], cls='data')
    V.wire([(120, 310), (200, 310)], cls='data')
    V.port('en', 120, 310, d='right', io='in')

    # Connect gate of mp0/mn0 to net54
    V.wire([(220, 200), (260, 200)], cls='clock')
    V.wire([(260, 160), (260, 250)], cls='clock'); V.dot(260, 200)

    # Output node net55
    V.wire([(300, 190), (300, 220)], cls='clock'); V.dot(300, 200)
    V.wire([(300, 200), (340, 200)], cls='clock'); V.dot(340, 200)
    V.wire([(380, 190), (340, 190), (340, 200)], cls='plain')

    # Output inverter xi0: pin A at 420, pin Y at 502
    inv(V, 'xi0', 440, 200, 'xi0', [[('xi0', 'a')]], [[('xi0', 'y')]], members=['xi0'], cls='clock')
    V.wire([(340, 200), (420, 200)], cls='clock')
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

    # Top NAND xi0 (sb, qb -> q) at X = 280, y = 140
    box(V, 'xi0', 240, 110, 80, 60, 'NAND2', 'xi0',
        left=[('sb', 130, [('xi0', 'a')], 'data'), ('qb', 150, [('xi0', 'b')], 'data')],
        right=[('q', 140, [('xi0', 'y')], 'data')])

    # Bot NAND xi1 (rb, q -> qb) at X = 280, y = 250
    box(V, 'xi1', 240, 220, 80, 60, 'NAND2', 'xi1',
        left=[('q', 240, [('xi1', 'b')], 'data'), ('rb', 260, [('xi1', 'a')], 'data')],
        right=[('qb', 250, [('xi1', 'y')], 'data')])

    # Inputs
    V.wire([(80, 130), (220, 130)], cls='data')
    V.port('sb', 80, 130, d='right', io='in')

    V.wire([(80, 260), (220, 260)], cls='data')
    V.port('rb', 80, 260, d='right', io='in')

    # Outputs
    V.wire([(340, 140), (460, 140)], cls='data'); V.dot(380, 140)
    V.port('q', 460, 140, d='right', io='out')

    V.wire([(340, 250), (460, 250)], cls='data'); V.dot(380, 250)
    V.port('qb', 460, 250, d='right', io='out')

    # Cross feedback
    V.wire([(380, 140), (380, 190), (180, 190), (180, 240), (220, 240)], cls='data')
    V.wire([(380, 250), (380, 200), (190, 200), (190, 150), (220, 150)], cls='data')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 10. VIEW_SADFE: u_sadfe
# =============================================================================
def view_sadfe():
    cell = 'sadfe'
    V = new_view('u_sadfe', cell, 'unit', f'{cell} — unit level (StrongARM DFE)', 920, 620)
    rail(V, 80, 840, 70, 'vdd', 'VDD')
    rail(V, 80, 840, 550, 'vss', 'VSS')

    # Precharge PMOS: mp2, mp0, mp1, mp3 at y = 140
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    mos(V, 'mp0', 380, 140, 'p', 'left', 'mp0', wl(cell, 'mp0'), tp0, bp0, gp0, members=['mp0'])
    V.wire([(380, 110), (380, 70)], cls='power'); V.dot(380, 70)

    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp1', 540, 140, 'p', 'right', 'mp1', wl(cell, 'mp1'), tp1, bp1, gp1, members=['mp1'])
    V.wire([(540, 110), (540, 70)], cls='power'); V.dot(540, 70)

    tp2, bp2, gp2 = mosT(cell, 'mp2')
    mos(V, 'mp2', 260, 140, 'p', 'left', 'mp2', wl(cell, 'mp2'), tp2, bp2, gp2, members=['mp2'])
    V.wire([(260, 110), (260, 70)], cls='power'); V.dot(260, 70)

    tp3, bp3, gp3 = mosT(cell, 'mp3')
    mos(V, 'mp3', 660, 140, 'p', 'right', 'mp3', wl(cell, 'mp3'), tp3, bp3, gp3, members=['mp3'])
    V.wire([(660, 110), (660, 70)], cls='power'); V.dot(660, 70)

    tp4, bp4, gp4 = mosT(cell, 'mp4')
    mos(V, 'mp4', 260, 220, 'p', 'left', 'mp4', wl(cell, 'mp4'), tp4, bp4, gp4, members=['mp4'])
    V.wire([(260, 190), (260, 170)], cls='power')

    tp5, bp5, gp5 = mosT(cell, 'mp5')
    mos(V, 'mp5', 660, 220, 'p', 'right', 'mp5', wl(cell, 'mp5'), tp5, bp5, gp5, members=['mp5'])
    V.wire([(660, 190), (660, 170)], cls='power')

    tn3, bn3, gn3 = mosT(cell, 'mn3')
    mos(V, 'mn3', 380, 220, 'n', 'left', 'mn3', wl(cell, 'mn3'), tn3, bn3, gn3, members=['mn3'])

    tn4, bn4, gn4 = mosT(cell, 'mn4')
    mos(V, 'mn4', 540, 220, 'n', 'right', 'mn4', wl(cell, 'mn4'), tn4, bn4, gn4, members=['mn4'])

    # Cross coupling
    V.wire([(380, 170), (380, 190)], cls='data'); V.dot(380, 180) # outn
    V.wire([(540, 170), (540, 190)], cls='data'); V.dot(540, 180) # outp
    V.wire([(260, 170), (380, 170)], cls='data')
    V.wire([(540, 170), (660, 170)], cls='data')

    V.wire([(380, 180), (500, 180), (500, 140), (580, 140)], cls='data')
    V.wire([(500, 180), (500, 220), (580, 220)], cls='data')
    V.wire([(540, 180), (420, 180), (420, 140), (340, 140)], cls='data')
    V.wire([(420, 180), (420, 220), (340, 220)], cls='data')

    # Outputs
    V.wire([(380, 180), (380, 170), (160, 170)], cls='data')
    V.port('outn', 160, 170, d='left', io='out')

    V.wire([(540, 180), (540, 170), (760, 170)], cls='data')
    V.port('outp', 760, 170, d='right', io='out')

    # Main input pair: mn1 (inp) at X = 380, mn2 (inn) at X = 540
    tn1, bn1, gn1 = mosT(cell, 'mn1')
    mos(V, 'mn1', 380, 320, 'n', 'left', 'mn1', wl(cell, 'mn1'), tn1, bn1, gn1, members=['mn1'])
    V.wire([(380, 250), (380, 290)], cls='plain'); V.dot(380, 270) # net85
    V.wire([(260, 250), (260, 270), (380, 270)], cls='plain')
    V.wire([(340, 320), (160, 320)], cls='data')
    V.port('inp', 160, 320, d='right', io='in')

    tn2, bn2, gn2 = mosT(cell, 'mn2')
    mos(V, 'mn2', 540, 320, 'n', 'right', 'mn2', wl(cell, 'mn2'), tn2, bn2, gn2, members=['mn2'])
    V.wire([(540, 250), (540, 290)], cls='plain'); V.dot(540, 270) # net86
    V.wire([(660, 250), (660, 270), (540, 270)], cls='plain')
    V.wire([(580, 320), (760, 320)], cls='data')
    V.port('inn', 760, 320, d='left', io='in')

    # Common tail node net84
    V.wire([(380, 350), (380, 390), (540, 390), (540, 350)], cls='plain')
    V.dot(460, 390)

    # Clock tail mn0 at X = 460, y = 450
    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 460, 450, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(460, 390), (460, 420)], cls='plain')
    V.wire([(460, 480), (460, 550)], cls='power'); V.dot(460, 550)

    # Clock net ck
    V.wire([(420, 450), (160, 450)], cls='clock')
    V.port('ck', 160, 450, d='right', io='in', cls='clock')
    V.wire([(220, 140), (180, 140), (180, 220), (220, 220)], cls='clock')
    V.wire([(180, 220), (180, 450)], cls='clock'); V.dot(180, 450)
    V.wire([(700, 140), (740, 140), (740, 220), (700, 220)], cls='clock')
    V.wire([(740, 220), (740, 450), (420, 450)], cls='clock'); V.dot(420, 450)

    # DFE tap ports
    V.port('w1_2', 160, 490, d='right', io='in', cls='bus')
    V.port('w1_1', 160, 510, d='right', io='in', cls='bus')
    V.port('w1_0', 160, 530, d='right', io='in', cls='bus')
    V.port('w2_1', 760, 490, d='left', io='in', cls='bus')
    V.port('w2_0', 760, 510, d='left', io='in', cls='bus')
    V.port('h1p', 160, 370, d='right', io='in')
    V.port('h1n', 160, 390, d='right', io='in')
    V.port('h2p', 760, 370, d='left', io='in')
    V.port('h2n', 760, 390, d='left', io='in')

    # Tap 1 at X = 300, y = 370
    tn12, bn12, gn12 = mosT(cell, 'mn12')
    mos(V, 'mn12', 300, 450, 'n', 'left', 'mn12', wl(cell, 'mn12'), tn12, bn12, gn12, members=['mn12'])
    V.wire([(260, 450), (220, 450), (220, 490), (160, 490)], cls='bus')
    V.wire([(300, 480), (300, 500), (460, 500)], cls='plain'); V.dot(460, 500)

    tn10, bn10, gn10 = mosT(cell, 'mn10')
    mos(V, 'mn10', 300, 370, 'n', 'left', 'mn10', wl(cell, 'mn10'), tn10, bn10, gn10, members=['mn10', 'mn11', 'mn13', 'mn14', 'mn15', 'mn16', 'mn17', 'mn18'])
    V.wire([(300, 340), (300, 270), (540, 270)], cls='plain'); V.dot(540, 270)
    V.wire([(300, 400), (300, 420)], cls='plain') # net89
    V.wire([(260, 370), (160, 370)], cls='data')
    V.wire([(160, 390), (240, 390), (240, 270)], cls='data')

    # Tap 2 at X = 620, y = 370
    tn22, bn22, gn22 = mosT(cell, 'mn22')
    mos(V, 'mn22', 620, 450, 'n', 'right', 'mn22', wl(cell, 'mn22'), tn22, bn22, gn22, members=['mn22'])
    V.wire([(660, 450), (700, 450), (700, 490), (760, 490)], cls='bus')
    V.wire([(620, 480), (620, 500), (460, 500)], cls='plain')

    tn20, bn20, gn20 = mosT(cell, 'mn20')
    mos(V, 'mn20', 620, 370, 'n', 'right', 'mn20', wl(cell, 'mn20'), tn20, bn20, gn20, members=['mn20', 'mn21', 'mn23', 'mn24', 'mn25'])
    V.wire([(620, 340), (620, 270), (540, 270)], cls='plain')
    V.wire([(620, 400), (620, 420)], cls='plain') # net91
    V.wire([(660, 370), (760, 370)], cls='data')
    V.wire([(760, 390), (680, 390), (680, 270), (380, 270)], cls='data')

    V.wire([(160, 510), (200, 510)], cls='bus')
    V.wire([(160, 530), (200, 530)], cls='bus')
    V.wire([(760, 510), (720, 510)], cls='bus')

    V.omitted = []
    return V

# =============================================================================
# 11. VIEW_VREFDAC: u_vrefdac
# =============================================================================
def view_vrefdac():
    cell = 'vrefdac'
    V = new_view('u_vrefdac', cell, 'unit', f'{cell} — unit level (기준 전압 DAC)', 840, 480)
    rail(V, 80, 760, 70, 'vddq', 'VDDQ')
    rail(V, 80, 760, 410, 'vssq', 'VSSQ')

    xs = [180, 260, 340, 420, 500, 580]
    for i, x in enumerate(xs):
        mp_top = f'mp{2*i}'
        mp_sw = f'mp{2*i+1}'
        inv_name = f'xi{i}'
        c_name = f'c{i}'

        tp, bp, gp = mosT(cell, mp_top)
        mos(V, mp_top, x, 140, 'p', 'left', mp_top, wl(cell, mp_top), tp, bp, gp, members=[mp_top])
        V.wire([(x, 110), (x, 70)], cls='power'); V.dot(x, 70)

        tps, bps, gps = mosT(cell, mp_sw)
        mos(V, mp_sw, x, 220, 'p', 'left', mp_sw, wl(cell, mp_sw), tps, bps, gps, members=[mp_sw])
        V.wire([(x, 170), (x, 190)], cls='plain') # net45..net50
        V.wire([(x, 250), (x, 290)], cls='plain') # connects to net32

        # Inverter xi<i>: pin A at x - 40, pin Y at x + 42
        inv(V, inv_name, x - 20, 340, inv_name, [[(inv_name, 'a')]], [[(inv_name, 'y')]], members=[inv_name], cls='data')
        V.wire([(x + 42, 340), (x + 42, 280), (x - 40, 280), (x - 40, 220)], cls='plain')
        V.wire([(x - 80, 340), (x - 40, 340)], cls='bus')
        V.port(c_name, x - 80, 340, d='right', io='in', cls='bus')

    # Bias vbp rail
    V.wire([(140, 140), (580, 140)], cls='plain'); V.dot(180, 140); V.dot(260, 140); V.dot(340, 140); V.dot(420, 140); V.dot(500, 140); V.dot(580, 140)
    V.wire([(100, 140), (140, 140)], cls='plain')
    V.port('vbp', 100, 140, d='right', io='in')

    # Dummy/replica leg mp12, mp13 at X = 660
    tp12, bp12, gp12 = mosT(cell, 'mp12')
    mos(V, 'mp12', 660, 140, 'p', 'left', 'mp12', wl(cell, 'mp12'), tp12, bp12, gp12, members=['mp12'])
    V.wire([(660, 110), (660, 70)], cls='power'); V.dot(660, 70)
    V.wire([(580, 140), (620, 140)], cls='plain')

    tp13, bp13, gp13 = mosT(cell, 'mp13')
    mos(V, 'mp13', 660, 220, 'p', 'left', 'mp13', wl(cell, 'mp13'), tp13, bp13, gp13, members=['mp13'])
    V.wire([(660, 170), (660, 190)], cls='plain')
    V.wire([(660, 250), (660, 290)], cls='plain')
    V.wire([(620, 220), (620, 410)], cls='power'); V.dot(620, 410)

    # Bus net32
    V.wire([(180, 290), (660, 290)], cls='plain')
    for x in xs:
        V.dot(x, 290)
    V.dot(660, 290)

    # Output network: r0 to vssq, r1 to vref, mn0 clamp
    res(V, 'r0', 700, 340, orient='v', name='r0', size='', a=[('r0', 'p')], b=[('r0', 'n')], members=['r0'])
    V.wire([(660, 290), (700, 290), (700, 310)], cls='plain'); V.dot(700, 290)
    V.wire([(700, 370), (700, 410)], cls='power'); V.dot(700, 410)

    res(V, 'r1', 750, 290, orient='h', name='r1', size='', a=[('r1', 'p')], b=[('r1', 'n')], members=['r1'])
    V.wire([(700, 290), (720, 290)], cls='plain')
    V.wire([(780, 290), (810, 290)], cls='data'); V.dot(810, 290)
    V.port('vref', 810, 290, d='right', io='out')

    tn0, bn0, gn0 = mosT(cell, 'mn0')
    mos(V, 'mn0', 810, 350, 'n', 'left', 'mn0', wl(cell, 'mn0'), tn0, bn0, gn0, members=['mn0'])
    V.wire([(810, 290), (770, 290), (770, 350)], cls='data')
    V.wire([(810, 320), (810, 380), (810, 410)], cls='power'); V.dot(810, 410)

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 12. VIEW_ODTCTL: b_odtctl
# =============================================================================
def view_odtctl():
    cell = 'odtctl'
    V = new_view('b_odtctl', cell, 'block', f'{cell} — 블록 레벨', 640, 420)

    V.port('odt_en', 80, 140, d='right', io='in')
    V.port('rtt2', 80, 200, d='right', io='in', cls='bus')
    V.port('rtt1', 80, 260, d='right', io='in', cls='bus')
    V.port('rtt0', 80, 320, d='right', io='in', cls='bus')

    # NAND gates xi2, xi1, xi0
    box(V, 'xi2', 180, 180, 70, 50, 'NAND2', 'xi2', left=[('a', 195, [('xi2', 'a')], 'data'), ('b', 215, [('xi2', 'b')], 'data')], right=[('y', 205, [('xi2', 'y')], 'data')])
    box(V, 'xi1', 180, 240, 70, 50, 'NAND2', 'xi1', left=[('a', 255, [('xi1', 'a')], 'data'), ('b', 275, [('xi1', 'b')], 'data')], right=[('y', 265, [('xi1', 'y')], 'data')])
    box(V, 'xi0', 180, 300, 70, 50, 'NAND2', 'xi0', left=[('a', 315, [('xi0', 'a')], 'data'), ('b', 335, [('xi0', 'b')], 'data')], right=[('y', 325, [('xi0', 'y')], 'data')])

    # odt_en distributes to all 3 NANDs
    V.wire([(80, 140), (140, 140), (140, 195), (160, 195)], cls='data'); V.dot(140, 195)
    V.wire([(140, 195), (140, 255), (160, 255)], cls='data'); V.dot(140, 255)
    V.wire([(140, 255), (140, 315), (160, 315)], cls='data')

    V.wire([(80, 200), (120, 200), (120, 215), (160, 215)], cls='bus')
    V.wire([(80, 260), (120, 260), (120, 275), (160, 275)], cls='bus')
    V.wire([(80, 320), (120, 320), (120, 335), (160, 335)], cls='bus')

    # Level shifters xi5, xi4, xi3
    box(V, 'xi5', 340, 180, 80, 50, 'LVLUP', 'xi5', left=[('in', 205, [('xi5', 'in')], 'data')], right=[('outb', 205, [('xi5', 'outb')], 'data')])
    box(V, 'xi4', 340, 240, 80, 50, 'LVLUP', 'xi4', left=[('in', 265, [('xi4', 'in')], 'data')], right=[('outb', 265, [('xi4', 'outb')], 'data')])
    box(V, 'xi3', 340, 300, 80, 50, 'LVLUP', 'xi3', left=[('in', 325, [('xi3', 'in')], 'data')], right=[('outb', 325, [('xi3', 'outb')], 'data')])

    V.wire([(250, 205), (320, 205)], cls='plain'); V.netlabel('net27', 285, 205)
    V.wire([(250, 265), (320, 265)], cls='plain'); V.netlabel('net26', 285, 265)
    V.wire([(250, 325), (320, 325)], cls='plain'); V.netlabel('net25', 285, 325)

    V.wire([(440, 205), (540, 205)], cls='bus')
    V.port('enb2', 540, 205, d='right', io='out', cls='bus')

    V.wire([(440, 265), (540, 265)], cls='bus')
    V.port('enb1', 540, 265, d='right', io='out', cls='bus')

    V.wire([(440, 325), (540, 325)], cls='bus')
    V.port('enb0', 540, 325, d='right', io='out', cls='bus')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 13. VIEW_WLDET: b_wldet
# =============================================================================
def view_wldet():
    cell = 'wldet'
    V = new_view('b_wldet', cell, 'block', f'{cell} — 블록 레벨', 740, 360)

    V.port('ck', 60, 140, d='right', io='in', cls='clock')
    V.port('en', 60, 180, d='right', io='in')
    V.port('d', 60, 240, d='right', io='in', cls='clock')

    # NAND2 xi0 and INV xi1 gating ck
    box(V, 'xi0', 160, 140, 60, 50, 'NAND2', 'xi0', left=[('a', 150, [('xi0', 'a')], 'clock'), ('b', 170, [('xi0', 'b')], 'data')], right=[('y', 160, [('xi0', 'y')], 'clock')])
    V.wire([(60, 140), (140, 140), (140, 150)], cls='clock')
    V.wire([(60, 180), (140, 180), (140, 170)], cls='data')

    inv(V, 'xi1', 280, 160, 'xi1', [[('xi1', 'a')]], [[('xi1', 'y')]], members=['xi1'], cls='clock')
    V.wire([(240, 160), (260, 160)], cls='clock'); V.netlabel('net105', 250, 160)

    # DFF xi2: pin ck at 360, 200; pin d at 360, 240; pin q at 480, 220
    box(V, 'xi2', 380, 180, 80, 80, 'DFF', 'xi2', left=[('ck', 200, [('xi2', 'ck')], 'clock'), ('d', 240, [('xi2', 'd')], 'clock')], right=[('q', 220, [('xi2', 'q')], 'data')])
    V.wire([(342, 160), (360, 160), (360, 200)], cls='clock'); V.netlabel('net106', 350, 160)
    V.wire([(60, 240), (360, 240)], cls='clock')

    # Output inverters xi3, xi4: xi3 pin A at 480, Y at 562; xi4 pin A at 580, Y at 662
    inv(V, 'xi3', 500, 220, 'xi3', [[('xi3', 'a')]], [[('xi3', 'y')]], members=['xi3'], cls='data')
    V.wire([(480, 220), (480, 220)], cls='data'); V.netlabel('net107', 480, 210)

    inv(V, 'xi4', 600, 220, 'xi4', [[('xi4', 'a')]], [[('xi4', 'y')]], members=['xi4'], cls='data')
    V.wire([(562, 220), (580, 220)], cls='data'); V.netlabel('net108', 570, 210)

    V.wire([(662, 220), (700, 220)], cls='data')
    V.port('q', 700, 220, d='right', io='out')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 14. VIEW_DLY3: b_dly3
# =============================================================================
def view_dly3():
    cell = 'dly3'
    V = new_view('b_dly3', cell, 'block', f'{cell} — 블록 레벨', 860, 360)

    V.port('in', 60, 180, d='right', io='in', cls='clock')
    V.port('s0', 240, 80, d='down', io='in', cls='bus')
    V.port('s1', 480, 80, d='down', io='in', cls='bus')
    V.port('s2', 720, 80, d='down', io='in', cls='bus')

    # Stage 0: xi0 (buf) + xi1 (mux)
    box(V, 'xi0', 120, 210, 50, 40, 'BUF', 'xi0', left=[('a', 230, [('xi0', 'a')], 'clock')], right=[('y', 230, [('xi0', 'y')], 'clock')])
    box(V, 'xi1', 210, 170, 60, 60, 'MUX2', 'xi1', left=[('d0', 180, [('xi1', 'd0')], 'clock'), ('d1', 210, [('xi1', 'd1')], 'clock')], top=[('s', 240, [('xi1', 's')], 'bus')], right=[('z', 195, [('xi1', 'z')], 'clock')])
    V.wire([(60, 180), (100, 180), (190, 180)], cls='clock'); V.dot(100, 180)
    V.wire([(100, 180), (100, 230)], cls='clock')
    V.wire([(170, 230), (180, 230), (180, 210), (190, 210)], cls='clock')
    V.wire([(240, 80), (240, 150)], cls='bus')

    # Stage 1: xi2..xi4 (bufs) + xi5 (mux)
    V.wire([(290, 195), (320, 195), (430, 195)], cls='clock'); V.dot(320, 195)
    box(V, 'xi5', 450, 180, 60, 60, 'MUX2', 'xi5', left=[('d0', 195, [('xi5', 'd0')], 'clock'), ('d1', 225, [('xi5', 'd1')], 'clock')], top=[('s', 480, [('xi5', 's')], 'bus')], right=[('z', 210, [('xi5', 'z')], 'clock')])
    V.wire([(320, 195), (320, 240), (430, 240), (430, 225)], cls='clock')
    V.wire([(480, 80), (480, 160)], cls='bus')

    # Stage 2: xi6..xi10 (bufs) + xi11 (mux)
    V.wire([(530, 210), (560, 210), (670, 210)], cls='clock'); V.dot(560, 210)
    box(V, 'xi11', 690, 190, 60, 60, 'MUX2', 'xi11', left=[('d0', 210, [('xi11', 'd0')], 'clock'), ('d1', 235, [('xi11', 'd1')], 'clock')], top=[('s', 720, [('xi11', 's')], 'bus')], right=[('z', 220, [('xi11', 'z')], 'clock')])
    V.wire([(560, 210), (560, 250), (670, 250), (670, 235)], cls='clock')
    V.wire([(720, 80), (720, 170)], cls='bus')

    # Output buf xi12
    box(V, 'xi12', 770, 205, 50, 40, 'BUF', 'xi12', left=[('a', 220, [('xi12', 'a')], 'clock')], right=[('y', 220, [('xi12', 'y')], 'clock')])
    V.wire([(770, 220), (770, 220)], cls='clock')
    V.wire([(840, 220), (840, 220)], cls='clock')
    V.port('out', 840, 220, d='right', io='out', cls='clock')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 15. VIEW_DQSGATE: b_dqsgate
# =============================================================================
def view_dqsgate():
    cell = 'dqsgate'
    V = new_view('b_dqsgate', cell, 'block', f'{cell} — 블록 레벨', 720, 420)

    V.port('open', 60, 140, d='right', io='in')
    V.port('ckt', 60, 220, d='right', io='in', cls='clock')
    V.port('ckc', 60, 300, d='right', io='in', cls='clock')

    # Top branch: xi0 (lat_tg), xi2 (nand2x2), xi3 (invx4) -> gt
    box(V, 'xi0', 160, 120, 70, 60, 'LAT', 'xi0', left=[('d', 140, [('xi0', 'd')], 'data'), ('en', 160, [('xi0', 'en')], 'clock')], bottom=[('enb', 195, [('xi0', 'enb')], 'clock')], right=[('q', 150, [('xi0', 'q')], 'data')])
    box(V, 'xi2', 280, 135, 70, 50, 'NAND2', 'xi2', left=[('b', 150, [('xi2', 'b')], 'data'), ('a', 170, [('xi2', 'a')], 'clock')], right=[('y', 160, [('xi2', 'y')], 'clock')])
    inv(V, 'xi3', 400, 160, 'xi3', [[('xi3', 'a')]], [[('xi3', 'y')]], members=['xi3'], cls='clock')

    # Bot branch: xi1 (lat_tg), xi4 (nand2x2), xi5 (invx4) -> gc
    box(V, 'xi1', 160, 240, 70, 60, 'LAT', 'xi1', left=[('d', 260, [('xi1', 'd')], 'data'), ('en', 280, [('xi1', 'en')], 'clock')], bottom=[('enb', 195, [('xi1', 'enb')], 'clock')], right=[('q', 270, [('xi1', 'q')], 'data')])
    box(V, 'xi4', 280, 255, 70, 50, 'NAND2', 'xi4', left=[('b', 270, [('xi4', 'b')], 'data'), ('a', 290, [('xi4', 'a')], 'clock')], right=[('y', 280, [('xi4', 'y')], 'clock')])
    inv(V, 'xi5', 400, 280, 'xi5', [[('xi5', 'a')]], [[('xi5', 'y')]], members=['xi5'], cls='clock')

    # Routing
    V.wire([(60, 140), (120, 140), (140, 140)], cls='data'); V.dot(120, 140)
    V.wire([(120, 140), (120, 260), (140, 260)], cls='data')

    V.wire([(60, 220), (100, 220), (100, 320), (195, 320), (195, 320)], cls='clock'); V.dot(100, 220)
    V.wire([(100, 220), (250, 220), (250, 170), (260, 170)], cls='clock')

    V.wire([(60, 300), (90, 300), (90, 160), (140, 160)], cls='clock'); V.dot(90, 300)
    V.wire([(90, 300), (140, 280)], cls='clock')
    V.wire([(90, 300), (250, 300), (250, 290), (260, 290)], cls='clock')

    V.wire([(250, 150), (260, 150)], cls='data'); V.netlabel('net65', 255, 150)
    V.wire([(370, 160), (380, 160)], cls='clock'); V.netlabel('net67', 375, 160)
    V.wire([(462, 160), (520, 160)], cls='clock')
    V.port('gt', 520, 160, d='right', io='out', cls='clock')

    V.wire([(250, 270), (260, 270)], cls='data'); V.netlabel('net66', 255, 270)
    V.wire([(370, 280), (380, 280)], cls='clock'); V.netlabel('net68', 375, 280)
    V.wire([(462, 280), (520, 280)], cls='clock')
    V.port('gc', 520, 280, d='right', io='out', cls='clock')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vss', 'class': '전원'}]
    return V

# =============================================================================
# 16. VIEW_DQSRX: b_dqsrx
# =============================================================================
def view_dqsrx():
    cell = 'dqsrx'
    V = new_view('b_dqsrx', cell, 'block', f'{cell} — 블록 레벨', 860, 420)

    V.port('inp', 60, 150, d='right', io='in', cls='clock')
    V.port('inn', 60, 270, d='right', io='in', cls='clock')
    V.port('enq', 60, 100, d='right', io='in')
    V.port('en', 60, 210, d='right', io='in')
    V.port('vbn', 60, 330, d='right', io='in')

    # DQS amplifier xi0
    box(V, 'xi0', 160, 160, 90, 100, 'DQSAMP', 'xi0',
        left=[('en', 180, [('xi0', 'en')], 'data'), ('inp', 200, [('xi0', 'inp')], 'clock'), ('inn', 220, [('xi0', 'inn')], 'clock'), ('vbn', 240, [('xi0', 'vbn')], 'plain')],
        right=[('outp', 190, [('xi0', 'outp')], 'clock'), ('outn', 230, [('xi0', 'outn')], 'clock')])

    V.wire([(60, 100), (120, 100), (120, 180), (140, 180)], cls='data')
    V.wire([(60, 150), (140, 200)], cls='clock')
    V.wire([(60, 270), (140, 220)], cls='clock')
    V.wire([(60, 330), (120, 330), (120, 240), (140, 240)], cls='plain')

    # AC amplifiers xi1 and xi2
    box(V, 'xi1', 320, 160, 80, 60, 'ACAMP', 'xi1', left=[('in', 190, [('xi1', 'in')], 'clock'), ('en', 170, [('xi1', 'en')], 'data')], right=[('out', 190, [('xi1', 'out')], 'clock')])
    box(V, 'xi2', 320, 240, 80, 60, 'ACAMP', 'xi2', left=[('in', 250, [('xi2', 'in')], 'clock'), ('en', 270, [('xi2', 'en')], 'data')], right=[('out', 250, [('xi2', 'out')], 'clock')])

    V.wire([(270, 190), (300, 190)], cls='clock'); V.netlabel('net58', 285, 190)
    V.wire([(270, 230), (285, 230), (285, 250), (300, 250)], cls='clock'); V.netlabel('net57', 285, 240)

    V.wire([(60, 210), (100, 210), (100, 170), (300, 170)], cls='data'); V.dot(100, 210)
    V.wire([(100, 210), (100, 270), (300, 270)], cls='data')

    # Output inverters xi3, xi5, xi6 -> ckt
    inv(V, 'xi3', 460, 190, 'xi3', [[('xi3', 'a')]], [[('xi3', 'y')]], members=['xi3'], cls='clock')
    V.wire([(420, 190), (440, 190)], cls='clock'); V.netlabel('net60', 430, 190)

    inv(V, 'xi5', 560, 190, 'xi5', [[('xi5', 'a')]], [[('xi5', 'y')]], members=['xi5'], cls='clock')
    V.wire([(522, 190), (540, 190)], cls='clock'); V.netlabel('net61', 530, 190)

    inv(V, 'xi6', 660, 190, 'xi6', [[('xi6', 'a')]], [[('xi6', 'y')]], members=['xi6'], cls='clock')
    V.wire([(622, 190), (640, 190)], cls='clock'); V.netlabel('net63', 630, 190)

    V.wire([(722, 190), (780, 190)], cls='clock')
    V.port('ckt', 780, 190, d='right', io='out', cls='clock')

    # Output inverters xi4, xi7, xi8 -> ckc
    inv(V, 'xi4', 460, 250, 'xi4', [[('xi4', 'a')]], [[('xi4', 'y')]], members=['xi4'], cls='clock')
    V.wire([(420, 250), (440, 250)], cls='clock'); V.netlabel('net59', 430, 250)

    inv(V, 'xi7', 560, 250, 'xi7', [[('xi7', 'a')]], [[('xi7', 'y')]], members=['xi7'], cls='clock')
    V.wire([(522, 250), (540, 250)], cls='clock'); V.netlabel('net62', 530, 250)

    inv(V, 'xi8', 660, 250, 'xi8', [[('xi8', 'a')]], [[('xi8', 'y')]], members=['xi8'], cls='clock')
    V.wire([(622, 250), (640, 250)], cls='clock'); V.netlabel('net64', 630, 250)

    V.wire([(722, 250), (780, 250)], cls='clock')
    V.port('ckc', 780, 250, d='right', io='out', cls='clock')

    V.omitted = [{'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'}, {'net': 'vss', 'class': '전원'}, {'net': 'vssq', 'class': '전원'}]
    return V

# =============================================================================
# 17. VIEW_SLICE: b_slice
# =============================================================================
def view_slice():
    cell = 'dqslice'
    V = new_view('b_slice', cell, 'block', f'{cell} — 블록 레벨', 1060, 520)

    V.port('pad', 60, 200, d='right', io='in')
    V.port('vref', 60, 260, d='right', io='in')
    V.port('ckt', 360, 440, d='up', io='in', cls='clock')
    V.port('ckc', 600, 440, d='up', io='in', cls='clock')

    # Front-end: padesd (xi0) and odtleg3 (xi1)
    box(V, 'xi0', 120, 160, 60, 50, 'ESD', 'xi0', left=[('pad', 185, [('xi0', 'pad')], 'data')], right=[('pad_r', 185, [('xi0', 'pad_r')], 'data')])
    box(V, 'xi1', 120, 230, 60, 50, 'ODT', 'xi1', left=[('pad', 255, [('xi1', 'pad')], 'data')])

    V.wire([(60, 200), (90, 200), (90, 185), (100, 185)], cls='data'); V.dot(90, 200)
    V.wire([(90, 200), (90, 255), (100, 255)], cls='data')

    # Preamp pair: sbamp xi2 and xi3
    tri(V, 'xi2', 240, 200, 'VGA', 'xi2', ins=[('inp', -15, [('xi2', 'inp')]), ('inn', 15, [('xi2', 'inn')])], outs=[('out', 0, [('xi2', 'out')])])
    tri(V, 'xi3', 240, 300, 'VGA', 'xi3', ins=[('inp', -15, [('xi3', 'inp')]), ('inn', 15, [('xi3', 'inn')])], outs=[('out', 0, [('xi3', 'out')])])

    # pad_r to xi2.inp and xi3.inn
    V.wire([(200, 185), (220, 185)], cls='data'); V.dot(200, 185); V.netlabel('net92', 190, 180)
    V.wire([(200, 185), (200, 315), (220, 315)], cls='data')

    # vref to xi2.inn and xi3.inp
    V.wire([(60, 260), (210, 260)], cls='data'); V.dot(210, 260)
    V.wire([(210, 260), (210, 215), (220, 215)], cls='data')
    V.wire([(210, 260), (210, 285), (220, 285)], cls='data')

    # StrongARM comparators xi4 (ckt) and xi6 (ckc)
    box(V, 'xi4', 380, 180, 90, 80, 'SADFE', 'xi4',
        left=[('inp', 200, [('xi4', 'inp')], 'data'), ('inn', 230, [('xi4', 'inn')], 'data')],
        bottom=[('ck', 425, [('xi4', 'ck')], 'clock')],
        right=[('outp', 200, [('xi4', 'outp')], 'data'), ('outn', 230, [('xi4', 'outn')], 'data')])

    box(V, 'xi6', 620, 280, 90, 80, 'SADFE', 'xi6',
        left=[('inp', 300, [('xi6', 'inp')], 'data'), ('inn', 330, [('xi6', 'inn')], 'data')],
        bottom=[('ck', 665, [('xi6', 'ck')], 'clock')],
        right=[('outp', 300, [('xi6', 'outp')], 'data'), ('outn', 330, [('xi6', 'outn')], 'data')])

    # Connect preamps to comparators
    V.wire([(340, 200), (360, 200)], cls='data'); V.dot(350, 200); V.netlabel('net93', 345, 195)
    V.wire([(350, 200), (350, 270), (580, 270), (580, 300), (600, 300)], cls='data')

    V.wire([(340, 300), (350, 300), (350, 230), (360, 230)], cls='data'); V.dot(350, 300); V.netlabel('net94', 345, 295)
    V.wire([(350, 300), (600, 300), (600, 330)], cls='data')

    # Clock inputs
    V.wire([(360, 440), (425, 440), (425, 280)], cls='clock')
    V.wire([(600, 440), (665, 440), (665, 380)], cls='clock')

    # SR latches xi5 and xi7
    box(V, 'xi5', 520, 190, 60, 60, 'SR', 'xi5', left=[('rb', 200, [('xi5', 'rb')], 'data'), ('sb', 230, [('xi5', 'sb')], 'data')], right=[('q', 210, [('xi5', 'q')], 'data'), ('qb', 230, [('xi5', 'qb')], 'data')])
    box(V, 'xi7', 760, 290, 60, 60, 'SR', 'xi7', left=[('rb', 300, [('xi7', 'rb')], 'data'), ('sb', 330, [('xi7', 'sb')], 'data')], right=[('q', 310, [('xi7', 'q')], 'data'), ('qb', 330, [('xi7', 'qb')], 'data')])

    V.wire([(490, 200), (500, 200)], cls='data'); V.netlabel('net95', 495, 195)
    V.wire([(490, 230), (500, 230)], cls='data'); V.netlabel('net96', 495, 225)

    V.wire([(730, 300), (740, 300)], cls='data'); V.netlabel('net97', 735, 295)
    V.wire([(730, 330), (740, 330)], cls='data'); V.netlabel('net98', 735, 325)

    # Inverter drivers xi8/xi9 (qr) and xi10/xi11 (qf)
    inv(V, 'xi8', 640, 210, 'xi8', [[('xi8', 'a')]], [[('xi8', 'y')]], members=['xi8'], cls='data')
    V.wire([(600, 210), (620, 210)], cls='data'); V.netlabel('net99', 610, 205)

    inv(V, 'xi9', 740, 210, 'xi9', [[('xi9', 'a')]], [[('xi9', 'y')]], members=['xi9'], cls='data')
    V.wire([(702, 210), (720, 210)], cls='data'); V.netlabel('net103', 710, 205)

    V.wire([(802, 210), (880, 210)], cls='data')
    V.port('qr', 880, 210, d='right', io='out')

    inv(V, 'xi10', 840, 310, 'xi10', [[('xi10', 'a')]], [[('xi10', 'y')]], members=['xi10'], cls='data')
    V.wire([(840, 310), (840, 310)], cls='data'); V.netlabel('net101', 830, 305)

    inv(V, 'xi11', 930, 310, 'xi11', [[('xi11', 'a')]], [[('xi11', 'y')]], members=['xi11'], cls='data')
    V.wire([(902, 310), (910, 310)], cls='data'); V.netlabel('net104', 905, 305)

    V.wire([(992, 310), (1040, 310)], cls='data')
    V.port('qf', 1040, 310, d='right', io='out')

    V.omitted = [
        {'net': 'en', 'class': '일반 제어'}, {'net': 'enb', 'class': '일반 제어'},
        {'net': 'odtb0', 'class': '일반 제어'}, {'net': 'odtb1', 'class': '일반 제어'}, {'net': 'odtb2', 'class': '일반 제어'},
        {'net': 'w1_0', 'class': '중요 제어'}, {'net': 'w1_1', 'class': '중요 제어'}, {'net': 'w1_2', 'class': '중요 제어'},
        {'net': 'w2_0', 'class': '중요 제어'}, {'net': 'w2_1', 'class': '중요 제어'},
        {'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}, {'net': 'vssq', 'class': '전원'}
    ]
    return V

# =============================================================================
# 18. VIEW_TOP: b_top
# =============================================================================
def view_top():
    cell = 'rxbyte_top'
    V = new_view('b_top', cell, 'block', f'{cell} — 블록 레벨 (최상위)', 1280, 800)

    # Global control & power ports
    V.port('dqs_t', 80, 220, d='right', io='in', cls='clock')
    V.port('dqs_c', 80, 260, d='right', io='in', cls='clock')
    V.port('gate_open', 80, 160, d='right', io='in')
    V.port('rx_en', 80, 110, d='right', io='in')

    # Front-end DQS ESD/ODT
    box(V, 'xi4', 160, 205, 50, 35, 'ESD', 'xi4', left=[('pad', 220, [('xi4', 'pad')], 'clock')], right=[('pad_r', 220, [('xi4', 'pad_r')], 'clock')])
    box(V, 'xi5', 160, 245, 50, 35, 'ESD', 'xi5', left=[('pad', 260, [('xi5', 'pad')], 'clock')], right=[('pad_r', 260, [('xi5', 'pad_r')], 'clock')])
    V.wire([(80, 220), (140, 220)], cls='clock')
    V.wire([(80, 260), (140, 260)], cls='clock')

    # DQS Receiver xi8
    box(V, 'xi8', 260, 210, 80, 70, 'DQSRX', 'xi8',
        left=[('inp', 225, [('xi8', 'inp')], 'clock'), ('inn', 255, [('xi8', 'inn')], 'clock')],
        right=[('ckt', 225, [('xi8', 'ckt')], 'clock'), ('ckc', 255, [('xi8', 'ckc')], 'clock')])
    V.wire([(230, 220), (230, 225), (240, 225)], cls='clock'); V.netlabel('net208', 235, 220)
    V.wire([(230, 260), (230, 255), (240, 255)], cls='clock'); V.netlabel('net209', 235, 260)

    # DQS Gating xi9
    box(V, 'xi9', 400, 210, 80, 70, 'DQSGATE', 'xi9',
        left=[('ckt', 225, [('xi9', 'ckt')], 'clock'), ('ckc', 255, [('xi9', 'ckc')], 'clock'), ('open', 215, [('xi9', 'open')], 'data')],
        right=[('gt', 225, [('xi9', 'gt')], 'clock'), ('gc', 255, [('xi9', 'gc')], 'clock')])
    V.wire([(360, 225), (380, 225)], cls='clock'); V.netlabel('net210', 370, 220)
    V.wire([(360, 255), (380, 255)], cls='clock'); V.netlabel('net211', 370, 260)
    V.wire([(80, 160), (370, 160), (370, 215), (380, 215)], cls='data')

    # Delay lines xi10, xi11
    box(V, 'xi10', 530, 210, 70, 45, 'DLY3', 'xi10', left=[('in', 225, [('xi10', 'in')], 'clock')], right=[('out', 225, [('xi10', 'out')], 'clock')])
    box(V, 'xi11', 530, 265, 70, 45, 'DLY3', 'xi11', left=[('in', 280, [('xi11', 'in')], 'clock')], right=[('out', 280, [('xi11', 'out')], 'clock')])
    V.wire([(500, 225), (510, 225)], cls='clock'); V.netlabel('net212', 505, 220)
    V.wire([(500, 255), (500, 280), (510, 280)], cls='clock'); V.netlabel('net213', 505, 265)

    # Clock tree buffers: xi12, xi13
    box(V, 'xi12', 650, 210, 60, 35, 'CKBUF', 'xi12', left=[('a', 225, [('xi12', 'a')], 'clock')], right=[('y', 225, [('xi12', 'y')], 'clock')])
    box(V, 'xi13', 650, 265, 60, 35, 'CKBUF', 'xi13', left=[('a', 280, [('xi13', 'a')], 'clock')], right=[('y', 280, [('xi13', 'y')], 'clock')])
    V.wire([(620, 225), (630, 225)], cls='clock'); V.netlabel('net214', 625, 220)
    V.wire([(620, 280), (630, 280)], cls='clock'); V.netlabel('net215', 625, 275)

    # Tree roots: net216, net217
    V.wire([(730, 225), (750, 225)], cls='clock'); V.netlabel('net216', 740, 220)
    V.wire([(730, 280), (750, 280)], cls='clock'); V.netlabel('net217', 740, 275)

    # DQ Slices xi30..xi37
    box(V, 'xi30', 880, 200, 140, 100, 'DQSLICE[0]', 'xi30',
        left=[('pad', 220, [('xi30', 'pad')], 'data'), ('vref', 240, [('xi30', 'vref')], 'data'), ('ckt', 260, [('xi30', 'ckt')], 'clock'), ('ckc', 280, [('xi30', 'ckc')], 'clock')],
        right=[('qr', 230, [('xi30', 'qr')], 'data'), ('qf', 270, [('xi30', 'qf')], 'data')])

    box(V, 'xi37', 880, 350, 140, 100, 'DQSLICE[7]', 'xi37',
        left=[('pad', 370, [('xi37', 'pad')], 'data'), ('vref', 390, [('xi37', 'vref')], 'data'), ('ckt', 410, [('xi37', 'ckt')], 'clock'), ('ckc', 430, [('xi37', 'ckc')], 'clock')],
        right=[('qr', 380, [('xi37', 'qr')], 'data'), ('qf', 420, [('xi37', 'qf')], 'data')])

    # DQ inputs
    V.port('dq0', 800, 220, d='right', io='in')
    V.wire([(800, 220), (860, 220)], cls='data')

    V.port('dq7', 800, 370, d='right', io='in')
    V.wire([(800, 370), (860, 370)], cls='data')

    # DQ outputs
    V.wire([(1040, 230), (1120, 230)], cls='data')
    V.port('qr0', 1120, 230, d='right', io='out')

    V.wire([(1040, 270), (1120, 270)], cls='data')
    V.port('qf0', 1120, 270, d='right', io='out')

    V.wire([(1040, 380), (1120, 380)], cls='data')
    V.port('qr7', 1120, 380, d='right', io='out')

    V.wire([(1040, 420), (1120, 420)], cls='data')
    V.port('qf7', 1120, 420, d='right', io='out')

    # Replica slice xi38 & Write Leveling detector xi39
    box(V, 'xi38', 880, 500, 140, 80, 'DQSLICE_REP', 'xi38',
        left=[('pad', 520, [('xi38', 'pad')], 'data'), ('vref', 540, [('xi38', 'vref')], 'data'), ('ckt', 560, [('xi38', 'ckt')], 'clock')],
        members=['xi38'])

    box(V, 'xi39', 880, 620, 140, 80, 'WLDET', 'xi39',
        left=[('d', 640, [('xi39', 'd')], 'clock'), ('ck', 660, [('xi39', 'ck')], 'clock'), ('en', 680, [('xi39', 'en')], 'data')],
        right=[('q', 660, [('xi39', 'q')], 'data')])

    V.port('wl_ck', 800, 640, d='right', io='in', cls='clock')
    V.wire([(800, 640), (860, 640)], cls='clock')

    V.port('wl_en', 800, 680, d='right', io='in')
    V.wire([(800, 680), (860, 680)], cls='data')

    V.wire([(1040, 660), (1120, 660)], cls='data')
    V.port('wl_out', 1120, 660, d='right', io='out')

    # Clock connections
    V.wire([(750, 225), (830, 225), (830, 260), (860, 260)], cls='clock'); V.dot(830, 225); V.netlabel('net218', 835, 220)
    V.wire([(830, 225), (830, 410), (860, 410)], cls='clock'); V.dot(830, 410); V.netlabel('net220', 835, 405)
    V.wire([(830, 410), (830, 560), (860, 560)], cls='clock'); V.dot(830, 560); V.netlabel('net222', 835, 555)
    V.wire([(830, 560), (830, 660), (860, 660)], cls='clock')

    V.wire([(750, 280), (840, 280), (860, 280)], cls='clock'); V.netlabel('net219', 845, 275)
    V.wire([(840, 280), (840, 430), (860, 430)], cls='clock'); V.dot(840, 280); V.netlabel('net221', 845, 425)

    # Control blocks: xi0, xi2
    box(V, 'xi0', 260, 90, 80, 50, 'LVLUP', 'xi0', left=[('in', 110, [('xi0', 'in')], 'data')], right=[('out', 105, [('xi0', 'out')], 'data'), ('outb', 125, [('xi0', 'outb')], 'data')])
    V.wire([(80, 110), (240, 110)], cls='data')

    box(V, 'xi2', 400, 90, 80, 50, 'VREFDAC', 'xi2', right=[('vref', 115, [('xi2', 'vref')], 'data')])
    V.wire([(500, 115), (780, 115), (780, 240), (860, 240)], cls='data'); V.netlabel('net204', 550, 110)
    V.wire([(780, 240), (780, 390), (860, 390)], cls='data'); V.dot(780, 240)
    V.wire([(780, 390), (780, 540), (860, 540)], cls='data'); V.dot(780, 390)

    # Omitted list
    V.omitted = [
        {'net': 'dq1', 'class': '고속 데이터'}, {'net': 'dq2', 'class': '고속 데이터'}, {'net': 'dq3', 'class': '고속 데이터'},
        {'net': 'dq4', 'class': '고속 데이터'}, {'net': 'dq5', 'class': '고속 데이터'}, {'net': 'dq6', 'class': '고속 데이터'},
        {'net': 'qr1', 'class': '고속 데이터'}, {'net': 'qr2', 'class': '고속 데이터'}, {'net': 'qr3', 'class': '고속 데이터'},
        {'net': 'qr4', 'class': '고속 데이터'}, {'net': 'qr5', 'class': '고속 데이터'}, {'net': 'qr6', 'class': '고속 데이터'},
        {'net': 'qf1', 'class': '고속 데이터'}, {'net': 'qf2', 'class': '고속 데이터'}, {'net': 'qf3', 'class': '고속 데이터'},
        {'net': 'qf4', 'class': '고속 데이터'}, {'net': 'qf5', 'class': '고속 데이터'}, {'net': 'qf6', 'class': '고속 데이터'},
        {'net': 'slp', 'class': '중요 제어'}, {'net': 'odt_en', 'class': '중요 제어'},
        {'net': 'rtt<2:0>', 'class': '중요 제어'}, {'net': 'vrc<5:0>', 'class': '중요 제어'},
        {'net': 't1w<2:0>', 'class': '중요 제어'}, {'net': 't2w<1:0>', 'class': '중요 제어'},
        {'net': 'ddl<2:0>', 'class': '중요 제어'},
        {'net': 'ibias', 'class': '바이어스'},
        {'net': 'vdd', 'class': '전원'}, {'net': 'vddq', 'class': '전원'},
        {'net': 'vss', 'class': '전원'}, {'net': 'vssq', 'class': '전원'}
    ]
    return V

def build_all():
    view_invx1()
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
    json.dump(out, open(W + '/scenes.json', 'w'), indent=0, default=list, ensure_ascii=False)
    print(f"Generated {len(VIEWS)} views successfully in {W}/scenes.json")

if __name__ == '__main__':
    build_all()
