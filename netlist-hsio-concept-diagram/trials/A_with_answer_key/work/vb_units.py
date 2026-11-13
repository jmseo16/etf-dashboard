"""Unit-level (MOSFET) views, §5.  Layout = textbook templates (§5.4) parameterised by the
analysed device groups."""
from vb_common import *

def bus_mark(v, x, y, bits, vertical=False):
    if vertical:
        v.d['texts'].append(dict(x=x + 9, y=y + 4, t=str(bits), size=9, anchor='start', color=INK, cls='',
                                 italic=False, bold=False))
        v.d['syms'].append(dict(id='bm_%d_%d' % (x, y), kind='mark', ops=[L((x - 6, y + 6), (x + 6, y - 6), w=1.2)],
                                pins={}, body=[x, y, x, y], pinmap={}, hidden={}, represents=[], slices=1))
    else:
        v.d['texts'].append(dict(x=x, y=y - 9, t=str(bits), size=9, anchor='middle', color=INK, cls='',
                                 italic=False, bold=False))
        v.d['syms'].append(dict(id='bm_%d_%d' % (x, y), kind='mark', ops=[L((x - 5, y + 7), (x + 5, y - 7), w=1.2)],
                                pins={}, body=[x, y, x, y], pinmap={}, hidden={}, represents=[], slices=1))

def M(v, cell, names, x, y, gate, s_top=None, pol=None, sid=None, lab_side=None):
    d0 = dev(cell, names[0])
    pol = pol or d0['pol']
    if s_top is None: s_top = (pol == 'p')
    term = {'top': 'S' if s_top else 'D', 'bot': 'D' if s_top else 'S', 'g': 'G'}
    return mos(v, sid or names[0], pol, x, y, gate=gate, s_top=s_top, name=mname(names), wl=wl(cell, names),
               represents=names, pinmap=mos_pm(names, term), slices=len(names), lab_side=lab_side)

# ------------------------------------------------------------------ INV
def view_inv():
    c = 'INV'
    v = View('INV', 'INV — CMOS 인버터 (유닛)', c, 'unit', 380, 290)
    v.rail('VDD', 50, 150, 250); v.rail('VSS', 250, 150, 250)
    M(v, c, ['MP'], 200, 80, 'L'); M(v, c, ['MN'], 200, 200, 'L')
    v.dot(200, 50); v.wire([[200, 230], [200, 250]], 'power', 'VSS'); v.dot(200, 250)
    v.wire([[200, 110], [200, 170]], 'data', 'Y'); v.dot(200, 140)
    v.wire([[200, 140], [300, 140]], 'data', 'Y'); v.port('Y', 300, 140, 'R')
    v.wire([[170, 80], [140, 80], [140, 200], [170, 200]], 'data', 'A'); v.dot(140, 140)
    v.wire([[60, 140], [140, 140]], 'data', 'A'); v.port('A', 60, 140, 'L')
    return finalize(v)

# ------------------------------------------------------------------ NAND2
def view_nand2():
    c = 'NAND2'
    v = View('NAND2', 'NAND2 — CMOS NAND (유닛, 사전 외)', c, 'unit', 470, 390)
    v.rail('VDD', 50, 130, 350); v.rail('VSS', 350, 130, 350)
    M(v, c, ['MP1'], 180, 80, 'L'); M(v, c, ['MP2'], 300, 80, 'L')
    M(v, c, ['MN1'], 240, 200, 'L'); M(v, c, ['MN2'], 240, 290, 'L')
    v.dot(180, 50); v.dot(300, 50)
    v.wire([[180, 110], [180, 140], [300, 140], [300, 110]], 'data', 'Y')
    v.wire([[240, 170], [240, 140]], 'data', 'Y'); v.dot(240, 140)
    v.wire([[300, 140], [390, 140]], 'data', 'Y'); v.dot(300, 140); v.port('Y', 390, 140, 'R')
    v.wire([[240, 230], [240, 260]], 'internal', 'MID')
    v.wire([[240, 320], [240, 350]], 'power', 'VSS'); v.dot(240, 350)
    v.wire([[150, 80], [110, 80], [110, 200], [210, 200]], 'data', 'A'); v.dot(110, 140)
    v.wire([[50, 140], [110, 140]], 'data', 'A'); v.port('A', 50, 140, 'L')
    v.wire([[50, 290], [210, 290]], 'data', 'B'); v.port('B', 50, 290, 'L')
    v.label(270, 80, 'B', 'L')
    return finalize(v)

# ------------------------------------------------------------------ CML latch (§5.4)
def view_cml_latch():
    c = 'CML_LATCH'
    v = View('CML_LATCH', 'CML_LATCH — CML latch (유닛, 교과서 배치)', c, 'unit', 820, 570)
    ax = 400
    v.rail('VDD', 60, 200, 600); v.rail('VSS', 540, 200, 600)
    v.axis(ax, 60, 540)
    M(v, c, ['MP_LP'], 250, 90, 'L'); M(v, c, ['MP_LN'], 550, 90, 'R')
    v.tag(220, 90, 'VSS', 'L'); v.tag(580, 90, 'VSS', 'R')
    v.dot(250, 60); v.dot(550, 60)
    M(v, c, ['M1'], 250, 220, 'L'); M(v, c, ['M2'], 550, 220, 'R')
    M(v, c, ['M3'], 350, 220, 'R'); M(v, c, ['M4'], 450, 220, 'L')
    M(v, c, ['M5'], 320, 370, 'L'); M(v, c, ['M6'], 480, 370, 'R')
    M(v, c, ['MB'], ax, 480, 'L'); v.tag(370, 480, 'VBN', 'L')
    for a, b in (('MP_LP', 'MP_LN'), ('M1', 'M2'), ('M3', 'M4'), ('M5', 'M6')): v.pair(a, b, ax)
    # outputs (single pair -> QP left end, QN right end)
    v.wire([[250, 120], [250, 190]], 'data', 'QP'); v.wire([[550, 120], [550, 190]], 'data', 'QN')
    v.wire([[250, 140], [60, 140]], 'data', 'QP'); v.dot(250, 140); v.port('QP', 60, 140, 'L')
    v.wire([[550, 140], [740, 140]], 'data', 'QN'); v.dot(550, 140); v.port('QN', 740, 140, 'R')
    v.wire([[250, 170], [350, 170], [350, 190]], 'data', 'QP'); v.dot(250, 170)
    v.wire([[550, 170], [450, 170], [450, 190]], 'data', 'QN'); v.dot(550, 170)
    v.wire([[380, 220], [450, 170]], 'data', 'QN'); v.dot(450, 170)
    v.wire([[420, 220], [350, 170]], 'data', 'QP'); v.dot(350, 170)
    v.allow(400, 205.7, 'cross-coupled X')
    v.wire([[220, 220], [60, 220]], 'data', 'DP'); v.port('DP', 60, 220, 'L')
    v.wire([[580, 220], [740, 220]], 'data', 'DN'); v.port('DN', 740, 220, 'R')
    i0 = len(v.d['wires'])
    v.wire([[250, 250], [250, 310], [550, 310], [550, 250]], 'internal', 'TAIL_T')
    v.wire([[350, 250], [350, 280], [480, 280], [480, 340]], 'internal', 'TAIL_H')
    v.wire([[450, 250], [450, 280]], 'internal', 'TAIL_H'); v.dot(450, 280)
    v.wire([[320, 340], [320, 310]], 'internal', 'TAIL_T'); v.dot(320, 310)
    v.allow(480, 310, 'latch template: input pair outside / cross-coupled inside (TAIL_H must cross TAIL_T)')
    v.d['asym_wires'] += list(range(i0, len(v.d['wires'])))
    v.wire([[290, 370], [60, 370]], 'clock', 'CLK'); v.port('CLK', 60, 370, 'L', 'clock')
    v.wire([[510, 370], [740, 370]], 'clock', 'CLKB'); v.port('CLKB', 740, 370, 'R', 'clock')
    v.wire([[320, 400], [320, 430], [480, 430], [480, 400]], 'internal', 'TAIL')
    v.wire([[ax, 430], [ax, 450]], 'internal', 'TAIL'); v.dot(ax, 430)
    v.wire([[ax, 510], [ax, 540]], 'power', 'VSS'); v.dot(ax, 540)
    return finalize(v)

# ------------------------------------------------------------------ CTLE (§5.4)
def view_ctle():
    c = 'CTLE_STAGE'
    v = View('CTLE_STAGE', 'CTLE_STAGE — RC-degenerated CTLE (유닛)', c, 'unit', 820, 470)
    ax = 400
    v.rail('VDD', 60, 110, 690); v.rail('VSS', 440, 110, 690); v.axis(ax, 60, 440)
    res(v, 'R_IND_P', 140, 90, 'V', name='R_IND_P', val=wl(c, ['R_IND_P']), represents=['R_IND_P'],
        pinmap={'a': [[['R_IND_P', 'A']]], 'b': [[['R_IND_P', 'B']]]}, lab=('L', 0))
    res(v, 'R_IND_N', 660, 90, 'V', name='R_IND_N', val=wl(c, ['R_IND_N']), represents=['R_IND_N'],
        pinmap={'a': [[['R_IND_N', 'A']]], 'b': [[['R_IND_N', 'B']]]}, lab=('R', 0))
    M(v, c, ['M_IND_P'], 200, 120, 'L', s_top=True); M(v, c, ['M_IND_N'], 600, 120, 'R', s_top=True)
    M(v, c, ['MP_LP'], 320, 90, 'L'); M(v, c, ['MP_LN'], 480, 90, 'R')
    v.tag(290, 90, 'VBP', 'L'); v.tag(510, 90, 'VBP', 'R')
    M(v, c, ['M1'], 320, 230, 'L'); M(v, c, ['M2'], 480, 230, 'R')
    M(v, c, ['MBP'], 320, 380, 'L'); M(v, c, ['MBN'], 480, 380, 'R')
    v.tag(290, 380, 'VBN', 'L'); v.tag(510, 380, 'VBN', 'R')
    for a, b in (('R_IND_P', 'R_IND_N'), ('M_IND_P', 'M_IND_N'), ('MP_LP', 'MP_LN'), ('M1', 'M2'), ('MBP', 'MBN')):
        v.pair(a, b, ax)
    for x in (140, 200, 320, 480, 600, 660): v.dot(x, 60)
    v.wire([[200, 90], [200, 60]], 'power', 'VDD'); v.wire([[600, 90], [600, 60]], 'power', 'VDD')
    v.wire([[140, 120], [170, 120]], 'internal', 'G_IND_P'); v.wire([[660, 120], [630, 120]], 'internal', 'G_IND_N')
    v.wire([[60, 170], [320, 170]], 'data', 'OUTP'); v.port('OUTP', 60, 170, 'L')
    v.wire([[740, 170], [480, 170]], 'data', 'OUTN'); v.port('OUTN', 740, 170, 'R')
    v.wire([[200, 150], [200, 170]], 'data', 'OUTP'); v.dot(200, 170)
    v.wire([[600, 150], [600, 170]], 'data', 'OUTN'); v.dot(600, 170)
    v.wire([[320, 120], [320, 200]], 'data', 'OUTP'); v.dot(320, 170)
    v.wire([[480, 120], [480, 200]], 'data', 'OUTN'); v.dot(480, 170)
    v.wire([[290, 230], [60, 230]], 'data', 'INP'); v.port('INP', 60, 230, 'L')
    v.wire([[510, 230], [740, 230]], 'data', 'INN'); v.port('INN', 740, 230, 'R')
    v.wire([[320, 260], [320, 350]], 'internal', 'SP'); v.wire([[480, 260], [480, 350]], 'internal', 'SN')
    rb = ['R_DEG_BASE', 'MR0', 'MR1', 'MR2', 'MC0P', 'MC0N', 'MC1P', 'MC1N', 'MC2P', 'MC2N']
    pa = [['R_DEG_BASE', 'A'], ['MR0', 'D'], ['MR1', 'D'], ['MR2', 'D'], ['MC0P', 'D'], ['MC1P', 'D'], ['MC2P', 'D']]
    pb = [['R_DEG_BASE', 'B'], ['MR0', 'S'], ['MR1', 'S'], ['MR2', 'S'], ['MC0N', 'S'], ['MC1N', 'S'], ['MC2N', 'S']]
    res(v, 'R_S', ax, 290, 'H', var=True, represents=rb, pinmap={'a': [pa], 'b': [pb]})
    v.text(ax, 247, 'R_S (var)', anchor='middle', italic=True, size=10)
    v.text(ax, 260, '800∥MR<0:2>∥MC<0:2>P-N', anchor='middle', size=9, cls='wl', color='#55606e')
    cb = ['C_DEG_BASE', 'C0_CAP', 'C1_CAP', 'C2_CAP']
    cap(v, 'C_S', ax, 330, 'H', represents=cb, pinmap={'a': [[[n, 'A'] for n in cb]], 'b': [[[n, 'B'] for n in cb]]})
    v.text(ax, 357, 'C_S (fixed x4)', anchor='middle', italic=True, size=10)
    v.text(ax, 369, wl(c, cb), anchor='middle', size=9, cls='wl', color='#55606e')
    v.wire([[320, 290], [370, 290]], 'internal', 'SP'); v.wire([[430, 290], [480, 290]], 'internal', 'SN')
    v.wire([[320, 330], [370, 330]], 'internal', 'SP'); v.wire([[430, 330], [480, 330]], 'internal', 'SN')
    for x in (320, 480):
        v.dot(x, 290); v.dot(x, 330)
        v.wire([[x, 410], [x, 440]], 'power', 'VSS'); v.dot(x, 440)
    return finalize(v)

# ------------------------------------------------------------------ pair-wise symmetric (option B)
def pairwise(v, c, loads, main, mtail, extra, xtail_kind, xtail, a1=300, a2=760, inn_port=True,
             extra_gate_ports=None, bus=None):
    """main pair on axis a1, merged extra pair on axis a2.  OUTN upper bus, OUTP lower bus,
    both leaving at the right end (§5.2-2, figure B)."""
    v.rail('VDD', 60, 110, a2 + 160); v.rail('VSS', 460, 110, a2 + 160)
    xl, xr = a1 - 80, a1 + 80
    el, er = a2 - 120, a2 + 120
    v.axis(a1, 60, 460); v.d['axes'][-1].update(xl=a1 - 150, xr=a1 + 150)
    v.axis(a2, 230, 460); v.d['axes'][-1].update(xl=a2 - 150, xr=a2 + 150)
    M(v, c, [loads[0]], xl, 90, 'L'); M(v, c, [loads[1]], xr, 90, 'R')
    v.tag(xl - 30, 90, 'VBP', 'L'); v.tag(xr + 30, 90, 'VBP', 'R'); v.dot(xl, 60); v.dot(xr, 60)
    M(v, c, [main[0]], xl, 260, 'L'); M(v, c, [main[1]], xr, 260, 'R')
    M(v, c, extra[0], el, 260, 'L', sid='XP'); M(v, c, extra[1], er, 260, 'R', sid='XN')
    v.pair(loads[0], loads[1], a1); v.pair(main[0], main[1], a1); v.pair('XP', 'XN', a2)
    M(v, c, [mtail], a1, 370, 'L'); v.tag(a1 - 30, 370, 'VBN', 'L')
    xend = a2 + 220
    i0 = len(v.d['wires'])
    v.wire([[xr, 120], [xr, 230]], 'data', 'OUTN'); v.wire([[xl, 120], [xl, 230]], 'data', 'OUTP')
    v.wire([[xr, 160], [xend, 160]], 'data', 'OUTN'); v.dot(xr, 160)
    v.wire([[xl, 190], [xend, 190]], 'data', 'OUTP'); v.dot(xl, 190)
    v.wire([[er, 160], [er, 230]], 'data', 'OUTN'); v.dot(er, 160)
    v.wire([[el, 190], [el, 230]], 'data', 'OUTP'); v.dot(el, 190)
    v.d['asym_wires'] += list(range(i0, len(v.d['wires'])))
    v.allow(xr, 190, 'option B: OUTP bus crosses main-pair N drain line')
    v.allow(er, 190, 'option B: OUTP bus crosses extra-pair N drain line')
    v.port('OUTN', xend, 160, 'R'); v.port('OUTP', xend, 190, 'R')
    v.wire([[xl - 30, 260], [xl - 60, 260]], 'data', 'INP'); v.port('INP', xl - 60, 260, 'L')
    v.wire([[xr + 30, 260], [xr + 60, 260]], 'data', 'INN'); v.port('INN', xr + 60, 260, 'R')
    if extra_gate_ports:
        v.port(extra_gate_ports[0], el - 30, 260, 'L', 'data'); v.port(extra_gate_ports[1], er + 30, 260, 'R', 'data')
    else:
        v.label(el - 30, 260, 'INP', 'L'); v.label(er + 30, 260, 'INN', 'R')
    for (p, n, ax) in ((xl, xr, a1), (el, er, a2)):
        v.wire([[p, 290], [p, 320], [n, 320], [n, 290]], 'internal', 'tail')
        v.wire([[ax, 320], [ax, 340]], 'internal', 'tail'); v.dot(ax, 320)
        v.wire([[ax, 400], [ax, 460]], 'power', 'VSS'); v.dot(ax, 460)
    return xend

def view_vga():
    c = 'VGA_STAGE'
    v = View('VGA_STAGE', 'VGA_STAGE — 이득 단을 스위치로 더하는 VGA (유닛, 쌍별 대칭)', c, 'unit', 1120, 490)
    k = ['0', '1', '2', '3']
    xp = ['M_G%s_P' % i for i in k]; xn = ['M_G%s_N' % i for i in k]
    bundle = []
    for i in k: bundle += ['MS_G' + i, 'MB_G' + i]
    pairwise(v, c, ['MP_LP', 'MP_LN'], ['M_MAIN_P', 'M_MAIN_N'], 'MB_M', [xp, xn], 'var', None)
    isrc(v, 'I_G', 760, 370, var=True, name='I_G<0:3> (var)', val='MS_G<0:3>+MB_G<0:3>',
         represents=bundle, pinmap={'top': [[['MS_G' + i, 'D']] for i in k],
                                    'bot': [[['MB_G' + i, 'S']] for i in k]})
    return finalize(v)

def view_summer():
    c = 'DFE_SUMMER'
    v = View('DFE_SUMMER', 'DFE_SUMMER — DFE 합산기 Σ (유닛, 쌍별 대칭)', c, 'unit', 1160, 490)
    k = ['1', '2', '3', '4']
    xp = ['M_T%sP' % i for i in k]; xn = ['M_T%sN' % i for i in k]
    pairwise(v, c, ['MP_LP', 'MP_LN'], ['M_MP', 'M_MN'], 'MB_M', [xp, xn], 'var', None,
             extra_gate_ports=('T<1:4>P', 'T<1:4>N'))
    dacs = ['X_DAC' + i for i in k]
    ctrl = [[[d, 'B%d' % b]] for d in dacs for b in range(4)]
    isrc(v, 'I_TAP', 760, 370, var=True, name='X_DAC<1:4> (IDAC)', val='tap current x4',
         represents=dacs, pinmap={'top': [[[d, 'IOUT']] for d in dacs], 'bot': [[[d, 'VSS']] for d in dacs],
                                  'ctrl': ctrl}, ctrl=True)
    v.wire([[800, 370], [980, 370]], 'bus', 'W<1:4>_<0:3>'); v.port('W<1:4>_<0:3>', 980, 370, 'R', 'bus')
    bus_mark(v, 940, 370, 16)
    return finalize(v)


# ------------------------------------------------------------------ StrongARM (§5.4)
def view_strongarm():
    c = 'STRONGARM_SLICER'
    v = View('STRONGARM_SLICER', 'STRONGARM_SLICER — StrongARM 비교기 + SR latch (유닛, 교과서 배치)', c, 'unit', 1300, 640,
             note='M11(PMOS, VDD→DP, 게이트 DN)은 netlist에 짝이 없는 비대칭 소자 — 그대로 그림(확인 질문 Q3).')
    A = 460
    v.rail('VDD', 60, 80, 760); v.rail('VSS', 580, 80, 760); v.axis(A, 60, 580)
    v.d['axes'][-1].update(xl=180, xr=740)
    M(v, c, ['M11'], 100, 90, 'L'); v.label(70, 90, 'DN', 'L')
    M(v, c, ['M7'], 200, 90, 'L'); v.label(170, 90, 'CLK', 'L')
    M(v, c, ['M9'], 300, 90, 'L'); v.label(270, 90, 'CLK', 'L')
    M(v, c, ['M5'], 400, 90, 'R'); M(v, c, ['M6'], 520, 90, 'L')
    M(v, c, ['M10'], 620, 90, 'R'); v.label(650, 90, 'CLK', 'R')
    M(v, c, ['M8'], 720, 90, 'R'); v.label(750, 90, 'CLK', 'R')
    M(v, c, ['M3'], 400, 300, 'R'); M(v, c, ['M4'], 520, 300, 'L')
    M(v, c, ['M1'], 400, 410, 'L'); M(v, c, ['M2'], 520, 410, 'R')
    M(v, c, ['M_TAIL'], A, 520, 'L')
    for a, b in (('M7', 'M8'), ('M9', 'M10'), ('M5', 'M6'), ('M3', 'M4'), ('M1', 'M2')): v.pair(a, b, A)
    for x in (100, 200, 300, 400, 520, 620, 720): v.dot(x, 60)
    v.wire([[400, 120], [400, 270]], 'data', 'OUTP'); v.wire([[520, 120], [520, 270]], 'data', 'OUTN')
    v.wire([[300, 120], [300, 150], [400, 150]], 'data', 'OUTP'); v.dot(400, 150)
    v.wire([[620, 120], [620, 150], [520, 150]], 'data', 'OUTN'); v.dot(520, 150)
    v.label(350, 150, 'OUTP', 'T'); v.label(570, 150, 'OUTN', 'T')
    v.wire([[430, 90], [520, 190]], 'data', 'OUTN'); v.dot(520, 190)
    v.wire([[490, 90], [400, 190]], 'data', 'OUTP'); v.dot(400, 190)
    v.allow(460, 123.3, 'cross-coupled X (PMOS)')
    v.wire([[430, 300], [520, 230]], 'data', 'OUTN'); v.dot(520, 230)
    v.wire([[490, 300], [400, 230]], 'data', 'OUTP'); v.dot(400, 230)
    v.allow(460, 276.7, 'cross-coupled X (NMOS)')
    v.wire([[400, 330], [400, 380]], 'data', 'DP'); v.wire([[520, 330], [520, 380]], 'data', 'DN')
    v.wire([[200, 120], [200, 355], [400, 355]], 'data', 'DP'); v.dot(400, 355)
    v.wire([[720, 120], [720, 355], [520, 355]], 'data', 'DN'); v.dot(520, 355)
    v.label(620, 355, 'DN', 'B')
    i0 = len(v.d['wires'])
    v.wire([[100, 120], [100, 355], [200, 355]], 'data', 'DP'); v.dot(200, 355)
    v.wire([[430, 520], [80, 520]], 'clock', 'CLK'); v.port('CLK', 80, 520, 'L', 'clock')
    v.d['asym_wires'] += list(range(i0, len(v.d['wires'])))
    v.wire([[370, 410], [80, 410]], 'data', 'INP'); v.port('INP', 80, 410, 'L')
    v.wire([[550, 410], [840, 410]], 'data', 'INN'); v.port('INN', 840, 410, 'R')
    v.wire([[400, 440], [400, 470], [520, 470], [520, 440]], 'internal', 'TAIL')
    v.wire([[A, 470], [A, 490]], 'internal', 'TAIL'); v.dot(A, 470)
    v.wire([[A, 550], [A, 580]], 'power', 'VSS'); v.dot(A, 580)
    # SR latch + inverters (sub-blocks)
    box(v, 'X_SR', 980, 150, 1070, 250, 'SR LATCH', [('SB', 'L', 30, 'data', 'SB'), ('RB', 'L', 70, 'data', 'RB'),
        ('Q', 'R', 30, 'data', 'Q'), ('QB', 'R', 70, 'data', 'QB')], link='SR_LATCH', represents=['X_SR'],
        pinmap={'SB': [[['X_SR', 'SB']]], 'RB': [[['X_SR', 'RB']]], 'Q': [[['X_SR', 'Q']]], 'QB': [[['X_SR', 'QB']]]},
        sub='SR_LATCH', label_y=196)
    v.label(960, 180, 'OUTP', 'L'); v.label(960, 220, 'OUTN', 'L')
    v.wire([[1090, 180], [1230, 180]], 'data', 'QP'); v.port('QP', 1230, 180, 'R')
    v.wire([[1090, 220], [1230, 220]], 'data', 'QN'); v.port('QN', 1230, 220, 'R')
    inv_sym(v, 'X_BUFP', 1140, 110, 'X_BUFP'); inv_sym(v, 'X_BUFN', 1140, 290, 'X_BUFN')
    v.wire([[1120, 180], [1120, 110]], 'data', 'QP'); v.dot(1120, 180)
    v.wire([[1120, 220], [1120, 290]], 'data', 'QN'); v.dot(1120, 220)
    v.label(1200, 110, 'QPB', 'R'); v.label(1200, 290, 'QNB', 'R')
    return finalize(v)

def inv_sym(v, sid, x0, yc, inst):
    ops = [P((x0, yc - 18), (x0 + 34, yc), (x0, yc + 18), (x0, yc - 18), fill='#ffffff', w=DATA_W),
           C(x0 + 38, yc, 4, fill='#ffffff'), L((x0 - 20, yc), (x0, yc)), L((x0 + 42, yc), (x0 + 60, yc))]
    return v.sym(sid, 'inv', ops, {'A': [x0 - 20, yc], 'Y': [x0 + 60, yc]}, [x0, yc - 18, x0 + 42, yc + 18],
                 pinmap={'A': [[[inst, 'A']]], 'Y': [[[inst, 'Y']]]}, link='INV', represents=[inst])

# ------------------------------------------------------------------ CML clock buffer (group inside CLK_DIST_TREE)
BUF_DEVS = ['MP_B1P', 'MP_B1N', 'MN_B1P', 'MN_B1N', 'MB_B1']
def view_clkbuf():
    c = 'CLK_DIST_TREE'
    v = View('CLK_BUF', 'CLK_DIST_TREE / CML 클럭 버퍼 (유닛, 소자 묶음 MP_B1*·MN_B1*·MB_B1)', c, 'unit', 820, 470,
             note='B1P/B1N은 셀 포트가 아니라 묶음 경계 넷이므로 핀 모양으로 표시함.')
    ax = 400
    v.rail('VDD', 60, 260, 540); v.rail('VSS', 440, 260, 540); v.axis(ax, 60, 440)
    M(v, c, ['MP_B1P'], 320, 90, 'L'); M(v, c, ['MP_B1N'], 480, 90, 'R')
    v.tag(290, 90, 'VSS', 'L'); v.tag(510, 90, 'VSS', 'R'); v.dot(320, 60); v.dot(480, 60)
    M(v, c, ['MN_B1P'], 320, 230, 'L'); M(v, c, ['MN_B1N'], 480, 230, 'R')
    M(v, c, ['MB_B1'], ax, 350, 'L'); v.tag(370, 350, 'VBN', 'L')
    v.pair('MP_B1P', 'MP_B1N', ax); v.pair('MN_B1P', 'MN_B1N', ax)
    v.wire([[320, 120], [320, 200]], 'clock', 'B1P'); v.wire([[480, 120], [480, 200]], 'clock', 'B1N')
    v.wire([[320, 160], [100, 160]], 'clock', 'B1P'); v.dot(320, 160); v.port('B1P', 100, 160, 'L', 'clock')
    v.wire([[480, 160], [700, 160]], 'clock', 'B1N'); v.dot(480, 160); v.port('B1N', 700, 160, 'R', 'clock')
    v.wire([[290, 230], [100, 230]], 'clock', 'CLK_INP'); v.port('CLK_INP', 100, 230, 'L', 'clock')
    v.wire([[510, 230], [700, 230]], 'clock', 'CLK_INN'); v.port('CLK_INN', 700, 230, 'R', 'clock')
    v.wire([[320, 260], [320, 290], [480, 290], [480, 260]], 'internal', 'T_B1')
    v.wire([[ax, 290], [ax, 320]], 'internal', 'T_B1'); v.dot(ax, 290)
    v.wire([[ax, 380], [ax, 440]], 'power', 'VSS'); v.dot(ax, 440)
    return finalize(v, BUF_DEVS)

# ------------------------------------------------------------------ RX input termination / ESD (top-level devices)
TERM_DEVS = ['R_RX_P', 'R_RX_N', 'C_RX_VCM', 'M_ESD_P1', 'M_ESD_N1', 'M_ESD_P2', 'M_ESD_N2']
def view_rx_term():
    c = 'RX_AFE_TOP'
    v = View('RX_TERM', 'RX_AFE_TOP / 입력 종단 · ESD (유닛, 소자 그대로)', c, 'unit', 940, 430,
             note='C_RX_VCM(VCM_RX–VSS 디커플링)은 고속 신호와 무관하여 생략.')
    A = 470
    v.rail('VDD', 100, 140, 800); v.rail('VSS', 370, 140, 800); v.axis(A, 100, 370)
    for side, sg in (('P', -1), ('N', 1)):
        x = lambda d: A + sg * d
        pad = 'RX_IN' + side
        esdp, esdn, rt = ('M_ESD_P1', 'M_ESD_N1', 'R_RX_P') if side == 'P' else ('M_ESD_P2', 'M_ESD_N2', 'R_RX_N')
        g = 'L' if side == 'P' else 'R'
        M(v, c, [esdp], x(290), 130, g); M(v, c, [esdn], x(210), 290, g)
        v.tag(x(290) + (-30 if g == 'L' else 30), 130, 'VDD', g); v.tag(x(210) + (-30 if g == 'L' else 30), 290, 'VSS', g)
        res(v, rt, x(130), 270, 'V', name=rt, val=wl(c, [rt]), represents=[rt],
            pinmap={'a': [[[rt, 'A']]], 'b': [[[rt, 'B']]]}, lab=('R' if side == 'P' else 'L', 0))
        v.tag(x(130), 300, 'VCM_RX', 'B')
        v.pair(esdp, 'M_ESD_P2', A) if side == 'P' else None
        v.dot(x(290), 100); v.dot(x(210), 370)
        v.wire([[x(290), 160], [x(290), 210]], 'data', pad)
        v.wire([[x(210), 260], [x(210), 210]], 'data', pad)
        v.wire([[x(130), 240], [x(130), 210]], 'data', pad)
        v.wire([[x(400), 210], [x(80), 210]], 'data', pad)
        v.dot(x(290), 210); v.dot(x(210), 210); v.dot(x(130), 210)
        v.port(pad, x(400), 210, g)
        v.wire([[x(210), 320], [x(210), 370]], 'power', 'VSS')
        v.text(x(80) - sg * 4, 196, ('→ X_CTLE1.INP' if side == 'P' else 'X_CTLE1.INN ←'), anchor='end' if side == 'P' else 'start',
               size=9, color='#55606e')
    v.pair('M_ESD_N1', 'M_ESD_N2', A); v.pair('R_RX_P', 'R_RX_N', A)
    v.omit('C_RX_VCM', 'device', '디커플링 C (VCM_RX–VSS), 고속 신호와 무관')
    return finalize(v, TERM_DEVS)

# ------------------------------------------------------------------ transmission gates M_TIE (top-level devices)
TG_DEVS = ['M_TIE_P', 'M_TIE_P2', 'M_TIE_N', 'M_TIE_N2']
def view_tg():
    c = 'RX_AFE_TOP'
    v = View('RX_TG', 'RX_AFE_TOP / 전달 게이트 M_TIE (유닛)', c, 'unit', 760, 380,
             note='주의: NMOS 게이트=VSS, PMOS 게이트=VDD → 구조상 항상 OFF. 질문 Q1 참조 (그림은 netlist 그대로).')
    A = 380
    v.axis(A, 60, 320)
    for side, sg in (('P', -1), ('N', 1)):
        x = lambda d: A + sg * d
        n, p = ('M_TIE_P', 'M_TIE_P2') if side == 'P' else ('M_TIE_N', 'M_TIE_N2')
        gn, gp = ('L', 'R') if side == 'P' else ('R', 'L')
        M(v, c, [n], x(250), 190, gn, s_top=True); M(v, c, [p], x(100), 190, gp, s_top=True)
        v.tag(x(250) + (-30 if gn == 'L' else 30), 190, 'VSS', gn)
        v.tag(x(100) + (30 if gp == 'R' else -30), 190, 'VDD', gp)
        out = 'DOUT_ODD_' + side; inn = 'O_DOUT' + side
        v.wire([[x(250), 160], [x(250), 120], [x(175), 120]], 'data', out)
        v.wire([[x(100), 160], [x(100), 120], [x(175), 120]], 'data', out)
        v.wire([[x(175), 120], [x(175), 80]], 'data', out); v.dot(x(175), 120); v.port(out, x(175), 80, 'T')
        v.wire([[x(250), 220], [x(250), 260], [x(175), 260]], 'data', inn)
        v.wire([[x(100), 220], [x(100), 260], [x(175), 260]], 'data', inn)
        v.wire([[x(175), 260], [x(175), 300]], 'data', inn); v.dot(x(175), 260); v.label(x(175), 300, inn, 'B')
    v.pair('M_TIE_P', 'M_TIE_N', A); v.pair('M_TIE_P2', 'M_TIE_N2', A)
    return finalize(v, TG_DEVS)

UNIT_VIEWS = [view_ctle, view_vga, view_summer, view_strongarm, view_cml_latch, view_clkbuf, view_rx_term, view_tg,
              view_inv, view_nand2]
