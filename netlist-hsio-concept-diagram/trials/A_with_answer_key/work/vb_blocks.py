"""Block-level views (§4): only visible nets, left->right flow, clocks from below,
important-control bus from above, feedback below/right."""
from vb_common import *
from vb_units import bus_mark, inv_sym, BUF_DEVS, TERM_DEVS, TG_DEVS

def ibox(v, inst, x0, y0, x1, y1, label, pins, link, sub=None, label_y=None, big=False, pin_names=True):
    """instance box: pins = [(port, side, off, cls, shown)]"""
    pm = {p[0]: [[[inst, p[0]]]] for p in pins}
    return box(v, inst, x0, y0, x1, y1, label, pins, link=link, represents=[inst], pinmap=pm, sub=sub,
               label_y=label_y, big=big, pin_names=pin_names)

def iamp(v, inst, x0, yc, label, ins, outs, link, clk=None, sub=None, pin_alias=None):
    pa = pin_alias or {}
    pm = {p: [[[inst, pa.get(p, p)]]] for p in list(ins) + list(outs) + ([clk] if clk else [])}
    return amp(v, inst, x0, yc, label, ins, outs, clk=clk, link=link, represents=[inst], pinmap=pm, sub=sub)

def mark(v, sid, x, y, up, text, represents, pinmap, link):
    """§3.4 'R/ESD 표시 on the input line': lead from the line + small labelled box."""
    sg = -1 if up else 1
    by0, by1 = (y + sg * 20, y + sg * 38) if not up else (y - 38, y - 20)
    ops = [L((x, y), (x, y + sg * 20)), P((x - 26, by0), (x + 26, by0), (x + 26, by1), (x - 26, by1), (x - 26, by0),
                                          fill='#ffffff', w=1.2)]
    d = v.sym(sid, 'mark', ops, {'a': [x, y]}, [x - 26, min(by0, by1), x + 26, max(by0, by1)], pinmap=pinmap,
              link=link, represents=represents)
    v.text(x, (by0 + by1) / 2 + 3.5, text, anchor='middle', size=9)
    return d

def tgbox(v, sid, x, y0, represents, a_ref, b_ref, link):
    """vertical TG concept box, pin a at bottom (y0), b at top (y0-60)."""
    ops = [L((x, y0), (x, y0 - 15)), L((x, y0 - 45), (x, y0 - 60)),
           P((x - 13, y0 - 45), (x + 13, y0 - 45), (x + 13, y0 - 15), (x - 13, y0 - 15), (x - 13, y0 - 45), fill='#fff', w=1.4)]
    d = v.sym(sid, 'tg', ops, {'a': [x, y0], 'b': [x, y0 - 60]}, [x - 13, y0 - 45, x + 13, y0 - 15],
              pinmap={'a': [a_ref], 'b': [b_ref]}, link=link, represents=represents)
    v.text(x, y0 - 26, 'TG', anchor='middle', size=9, bold=True)
    return d

# ------------------------------------------------------------------ SR latch
def view_sr():
    c = 'SR_LATCH'
    v = View('SR_LATCH', 'SR_LATCH — NAND SR latch (블록, 사전 외 → 박스)', c, 'block', 560, 360)
    nand = lambda inst, y0, order: ibox(v, inst, 200, y0, 280, y0 + 80, 'NAND2',
                                         [(order[0], 'L', 20, 'data', order[0]), (order[1], 'L', 60, 'data', order[1]),
                                          ('Y', 'R', 40, 'data', 'Y')], 'NAND2', sub=inst, label_y=y0 + 44)
    nand('X1', 80, ('A', 'B')); nand('X2', 240, ('B', 'A'))
    v.wire([[80, 100], [180, 100]], 'data', 'SB'); v.port('SB', 80, 100, 'L')
    v.wire([[80, 300], [180, 300]], 'data', 'RB'); v.port('RB', 80, 300, 'L')
    v.wire([[300, 120], [480, 120]], 'data', 'Q'); v.port('Q', 480, 120, 'R')
    v.wire([[300, 280], [480, 280]], 'data', 'QB'); v.port('QB', 480, 280, 'R')
    v.wire([[340, 120], [340, 180], [150, 180], [150, 260], [180, 260]], 'data', 'Q'); v.dot(340, 120)
    v.wire([[360, 280], [360, 220], [140, 220], [140, 140], [180, 140]], 'data', 'QB'); v.dot(360, 280)
    v.allow(150, 220, 'cross-coupled NAND (Q→X2.B, QB→X1.B)')
    return finalize(v)

# ------------------------------------------------------------------ CML DFF
LATCH_PINS = lambda d_top='DP', d_bot='DN', ck_l='CLK', ck_r='CLKB': [
    (d_top, 'L', 40, 'data', d_top), (d_bot, 'L', 70, 'data', d_bot), ('QP', 'R', 40, 'data', 'QP'),
    ('QN', 'R', 70, 'data', 'QN'), (ck_l, 'B', 30, 'clock', ck_l), (ck_r, 'B', 70, 'clock', ck_r)]
def view_dff():
    c = 'CML_DFF'
    v = View('CML_DFF', 'CML_DFF — master/slave CML latch (블록)', c, 'block', 660, 430,
             note='master(X_M)의 CLK 핀에는 CLKB, CLKB 핀에는 CLK가 연결됨(netlist 그대로) → 클럭 레일이 겹쳐 구조상 교차 1.')
    ibox(v, 'X_M', 160, 130, 260, 240, 'LATCH', LATCH_PINS(), 'CML_LATCH', sub='X_M', label_y=180)
    ibox(v, 'X_S', 380, 130, 480, 240, 'LATCH', LATCH_PINS(), 'CML_LATCH', sub='X_S', label_y=180)
    v.wire([[60, 170], [140, 170]], 'data', 'DP'); v.port('DP', 60, 170, 'L')
    v.wire([[60, 200], [140, 200]], 'data', 'DN'); v.port('DN', 60, 200, 'L')
    v.wire([[280, 170], [360, 170]], 'data', 'MP'); v.wire([[280, 200], [360, 200]], 'data', 'MN')
    v.wire([[500, 170], [580, 170]], 'data', 'QP'); v.port('QP', 580, 170, 'R')
    v.wire([[500, 200], [580, 200]], 'data', 'QN'); v.port('QN', 580, 200, 'R')
    v.wire([[230, 260], [230, 290], [410, 290], [410, 260]], 'clock', 'CLK')
    v.wire([[320, 290], [320, 360]], 'clock', 'CLK'); v.dot(320, 290); v.port('CLK', 320, 360, 'B', 'clock')
    v.wire([[190, 260], [190, 320], [520, 320], [520, 360]], 'clock', 'CLKB'); v.port('CLKB', 520, 360, 'B', 'clock')
    v.wire([[450, 260], [450, 320]], 'clock', 'CLKB'); v.dot(450, 320)
    v.allow(320, 320, 'master latch clock pins swapped → nested CLK/CLKB rails')
    return finalize(v)

# ------------------------------------------------------------------ half-rate DFE slice
def view_slice():
    c = 'HALF_RATE_DFE_SLICE'
    v = View('HALF_RATE_DFE_SLICE', 'HALF_RATE_DFE_SLICE — Σ → StrongARM → latch → DFF → DFF (블록)', c, 'block', 1380, 500,
             note='탭 입력(T1_FB, T2~T4)은 아래에서 Σ로 들어감(피드백은 아래로). W 버스는 위에서 Σ로.')
    sp = [('INP', 'L', 45, 'data', 'INP'), ('INN', 'L', 75, 'data', 'INN'), ('OUTP', 'R', 45, 'data', 'OUTP'),
          ('OUTN', 'R', 75, 'data', 'OUTN'), ('W', 'T', 70, 'bus', '')]
    bx = [15, 30, 50, 65, 85, 100, 120, 135]
    tports = ['T1P', 'T1N', 'T2P', 'T2N', 'T3P', 'T3N', 'T4P', 'T4N']
    for p, o in zip(tports, bx): sp.append((p, 'B', o, 'data', ''))
    s = box(v, 'X_SUM', 220, 140, 360, 260, 'Σ', sp, link='DFE_SUMMER', represents=['X_SUM'], big=True,
            pinmap={**{p[0]: [[['X_SUM', p[0]]]] for p in sp if p[0] != 'W'},
                    'W': [[['X_SUM', 'W%d_%d' % (i, b)]] for i in range(1, 5) for b in range(4)]},
            sub='DFE_SUMMER', label_y=202)
    for k in range(4): v.text(220 + (bx[2 * k] + bx[2 * k + 1]) / 2, 254, 'T%d' % (k + 1), anchor='middle', size=9,
                              color='#55606e')
    v.wire([[120, 185], [200, 185]], 'data', 'INP'); v.port('INP', 120, 185, 'L')
    v.wire([[120, 215], [200, 215]], 'data', 'INN'); v.port('INN', 120, 215, 'L')
    fb = ['T1_FB_P', 'T1_FB_N', 'T2_INP', 'T2_INN', 'T3_INP', 'T3_INN', 'T4_INP', 'T4_INN']
    for k, (n, o) in enumerate(zip(fb, bx)):
        y = 320 + 20 * k
        v.wire([[120, y], [220 + o, y], [220 + o, 280]], 'data', n); v.port(n, 120, y, 'L')
    v.wire([[290, 40], [290, 120]], 'bus', 'W'); v.port('W<1:4>_<0:3>', 290, 40, 'T', 'bus'); bus_mark(v, 290, 80, 16, True)
    iamp(v, 'X_SLICER', 440, 200, 'SA', ['INP', 'INN'], ['QP', 'QN'], 'STRONGARM_SLICER', clk='CLK', sub='STRONGARM')
    v.wire([[380, 185], [420, 185]], 'data', 'SUMP'); v.wire([[380, 215], [420, 215]], 'data', 'SUMN')
    lp = LATCH_PINS()
    ibox(v, 'X_LATCH1', 620, 140, 720, 260, 'LATCH', [(a, b, o + 5, d, e) for a, b, o, d, e in lp], 'CML_LATCH',
         sub='X_LATCH1', label_y=196)
    v.wire([[550, 185], [600, 185]], 'data', 'SA_QP'); v.wire([[550, 215], [600, 215]], 'data', 'SA_QN')
    dp = [('DP', 'L', 45, 'data', 'DP'), ('DN', 'L', 75, 'data', 'DN'), ('QP', 'R', 45, 'data', 'QP'),
          ('QN', 'R', 75, 'data', 'QN'), ('CLK', 'B', 30, 'clock', 'CLK'), ('CLKB', 'B', 70, 'clock', 'CLKB')]
    ibox(v, 'X_DFF2', 800, 140, 900, 260, 'DFF', dp, 'CML_DFF', sub='X_DFF2', label_y=196)
    ibox(v, 'X_DFF3', 980, 140, 1080, 260, 'DFF', dp, 'CML_DFF', sub='X_DFF3', label_y=196)
    v.wire([[740, 185], [780, 185]], 'data', 'D_OUTP'); v.wire([[740, 215], [780, 215]], 'data', 'D_OUTN')
    v.wire([[750, 185], [750, 80], [1260, 80]], 'data', 'D_OUTP'); v.dot(750, 185); v.port('D_OUTP', 1260, 80, 'R')
    v.wire([[770, 215], [770, 100], [1260, 100]], 'data', 'D_OUTN'); v.dot(770, 215); v.port('D_OUTN', 1260, 100, 'R')
    v.allow(770, 185, 'differential pair fork (D_OUT → port and DFF2)')
    v.wire([[920, 185], [960, 185]], 'data', 'T2_OUTP'); v.wire([[920, 215], [960, 215]], 'data', 'T2_OUTN')
    v.wire([[930, 185], [930, 120], [1260, 120]], 'data', 'T2_OUTP'); v.dot(930, 185); v.port('T2_OUTP', 1260, 120, 'R')
    v.wire([[950, 215], [950, 140], [1260, 140]], 'data', 'T2_OUTN'); v.dot(950, 215); v.port('T2_OUTN', 1260, 140, 'R')
    v.allow(950, 185, 'differential pair fork (T2_OUT → port and DFF3)')
    v.wire([[1100, 185], [1260, 185]], 'data', 'T3_OUTP'); v.port('T3_OUTP', 1260, 185, 'R')
    v.wire([[1100, 215], [1260, 215]], 'data', 'T3_OUTN'); v.port('T3_OUTN', 1260, 215, 'R')
    # clocks from below
    v.wire([[476, 270], [476, 400]], 'clock', 'CLK'); v.port('CLK', 476, 400, 'B', 'clock')
    v.wire([[476, 340], [1010, 340], [1010, 280]], 'clock', 'CLK'); v.dot(476, 340)
    for x in (655, 830): v.wire([[x, 280], [x, 340]], 'clock', 'CLK'); v.dot(x, 340)
    v.wire([[695, 280], [695, 310], [1150, 310], [1150, 400]], 'clock', 'CLKB'); v.port('CLKB', 1150, 400, 'B', 'clock')
    for x in (870, 1050): v.wire([[x, 280], [x, 310]], 'clock', 'CLKB'); v.dot(x, 310)
    v.allow(830, 310, 'interleaved CLK/CLKB pins of latch/DFF row')
    v.allow(1010, 310, 'interleaved CLK/CLKB pins of latch/DFF row')
    return finalize(v)

# ------------------------------------------------------------------ clock distribution
def view_clktree():
    c = 'CLK_DIST_TREE'
    v = View('CLK_DIST_TREE', 'CLK_DIST_TREE — 종단 → CML 버퍼 → latch 2개 → CMOS 버퍼 체인 (블록)', c, 'block', 1340, 400,
             note='이름은 X_DIV_M/S(분주기)이지만 출력→입력 피드백 루프가 없어 ÷2 구조가 아님 → LATCH로 그림 (질문 Q4). '
                  'X_DIV_M의 데이터 핀 DP/DN에 클럭 B1N/B1P가 들어감.')
    v.wire([[100, 185], [220, 185]], 'clock', 'CLK_INP'); v.port('CLK_INP', 100, 185, 'L', 'clock')
    v.wire([[100, 215], [220, 215]], 'clock', 'CLK_INN'); v.port('CLK_INN', 100, 215, 'L', 'clock')
    mark(v, 'TERM_P', 150, 185, True, 'R_T', ['R_TERM_P'], {'a': [[['R_TERM_P', 'A']]]}, None)
    mark(v, 'TERM_N', 150, 215, False, 'R_T', ['R_TERM_N'], {'a': [[['R_TERM_N', 'A']]]}, None)
    v.dot(150, 185); v.dot(150, 215)
    amp(v, 'BUF', 240, 200, 'BUF', ['INP', 'INN'], ['OUTP', 'OUTN'], link='CLK_BUF', represents=BUF_DEVS,
        pinmap={'INP': [[['MN_B1P', 'G']]], 'INN': [[['MN_B1N', 'G']]],
                'OUTP': [[['MN_B1P', 'D'], ['MP_B1P', 'D']]], 'OUTN': [[['MN_B1N', 'D'], ['MP_B1N', 'D']]]},
        sub='CML (MP/MN_B1*)')
    v.wire([[350, 185], [440, 185]], 'clock', 'B1P'); v.wire([[350, 215], [440, 215]], 'clock', 'B1N')
    ibox(v, 'X_DIV_M', 460, 140, 560, 260, 'LATCH', [('DN', 'L', 45, 'clock', 'DN'), ('DP', 'L', 75, 'clock', 'DP'),
         ('QP', 'R', 45, 'clock', 'QP'), ('QN', 'R', 75, 'clock', 'QN'), ('CLK', 'B', 30, 'clock', 'CLK'),
         ('CLKB', 'B', 70, 'clock', 'CLKB')], 'CML_LATCH', sub='X_DIV_M', label_y=196)
    ibox(v, 'X_DIV_S', 720, 140, 820, 260, 'LATCH', [(a, b, o + 5 if b in 'LR' else o, d, e) for a, b, o, d, e in LATCH_PINS()], 'CML_LATCH', sub='X_DIV_S', label_y=196)
    v.wire([[410, 215], [410, 310], [750, 310], [750, 280]], 'clock', 'B1N'); v.dot(410, 215)
    v.wire([[530, 280], [530, 310]], 'clock', 'B1N'); v.dot(530, 310)
    v.wire([[380, 185], [380, 340], [790, 340], [790, 280]], 'clock', 'B1P'); v.dot(380, 185)
    v.wire([[490, 280], [490, 340]], 'clock', 'B1P'); v.dot(490, 340)
    v.allow(380, 215, 'differential pair fork (B1P/B1N → data pins and clock pins)')
    v.allow(490, 310, 'B1P/B1N drive both CLK and CLKB of the two latches → nested rails')
    v.wire([[580, 185], [700, 185]], 'clock', 'CLKI'); v.wire([[580, 215], [700, 215]], 'clock', 'CLKIB')
    v.wire([[610, 185], [610, 80], [1240, 80]], 'clock', 'CLKI'); v.dot(610, 185); v.port('CLKI', 1240, 80, 'R', 'clock')
    v.wire([[640, 215], [640, 110], [1240, 110]], 'clock', 'CLKIB'); v.dot(640, 215); v.port('CLKIB', 1240, 110, 'R', 'clock')
    v.allow(640, 185, 'differential pair fork (CLKI/CLKIB → ports and X_DIV_S)')
    v.wire([[840, 185], [1240, 185]], 'clock', 'CLKQ'); v.port('CLKQ', 1240, 185, 'R', 'clock')
    v.wire([[840, 215], [1240, 215]], 'clock', 'CLKQB'); v.port('CLKQB', 1240, 215, 'R', 'clock')
    chains = [('CLKI', 80, 40, 'X_INV_I1', 'X_INV_I2', 'CLKI_B1', 'CLKI_BUF', 880),
              ('CLKIB', 110, 150, 'X_INV_IB1', 'X_INV_IB2', 'CLKIB_B1', 'CLKIB_BUF', 880),
              ('CLKQB', 215, 255, 'X_INV_QB1', 'X_INV_QB2', 'CLKQB_B1', 'CLKQB_BUF', 880),
              ('CLKQ', 185, 305, 'X_INV_Q1', 'X_INV_Q2', 'CLKQ_B1', 'CLKQ_BUF', 860)]
    for net, yl, yr, i1, i2, mid, out, xt in chains:
        v.wire([[xt, yl], [xt, yr], [900, yr]], 'clock', net); v.dot(xt, yl)
        inv_sym(v, i1, 920, yr, i1); inv_sym(v, i2, 1020, yr, i2)
        v.wire([[980, yr], [1000, yr]], 'clock', mid)
        v.label(1080, yr, out, 'R')
    v.allow(860, 215, 'differential pair fork (CLKQ/CLKQB → ports and buffer chains)')
    v.omit('C_VCM', 'device', '공통모드 디커플링 C (VCM_CLK–VSS)')
    return finalize(v)

# ------------------------------------------------------------------ top
SLICE_R = ['D_OUTP', 'D_OUTN', 'T2_OUTP', 'T2_OUTN', 'T3_OUTP', 'T3_OUTN', 'T4_INN', 'T4_INP', 'T2_INN', 'T2_INP',
           'T1_FB_P', 'T1_FB_N', 'T3_INP', 'T3_INN']
def slice_box(v, inst, x0, y0):
    pins = [('INP', 'L', 55, 'data', 'INP'), ('INN', 'L', 85, 'data', 'INN'), ('W', 'T', 20, 'bus', ''),
            ('CLK', 'B', 20, 'clock', ''), ('CLKB', 'B', 40, 'clock', '')]
    pins += [(n, 'R', 20 + 20 * k, 'data', n) for k, n in enumerate(SLICE_R)]
    pm = {p[0]: [[[inst, p[0]]]] for p in pins if p[0] != 'W'}
    pm['W'] = [[[inst, 'W%d_%d' % (i, b)]] for i in range(1, 5) for b in range(4)]
    box(v, inst, x0, y0, x0 + 220, y0 + 300, inst, pins, link='HALF_RATE_DFE_SLICE', represents=[inst], pinmap=pm,
        sub='HALF_RATE_DFE_SLICE', label_y=y0 + 160)
    v.text(x0 + 20, y0 + 296, 'CLK', anchor='middle', size=8, color='#55606e')
    v.text(x0 + 44, y0 + 286, 'CLKB', anchor='middle', size=8, color='#55606e')

def slice_loops(v, x, y0, t2lab, t1lab, t3lab):
    """own feedback loops on the right side (T3_OUT→T4_IN inner, T2_OUT→T2_IN outer) + labelled inputs."""
    Y = lambda k: y0 + 20 + 20 * k
    v.wire([[x, Y(5)], [x + 20, Y(5)], [x + 20, Y(6)], [x, Y(6)]], 'data', 'T3_OUTN', loop=True)
    v.wire([[x, Y(4)], [x + 40, Y(4)], [x + 40, Y(7)], [x, Y(7)]], 'data', 'T3_OUTP', loop=True)
    v.wire([[x, Y(3)], [x + 60, Y(3)], [x + 60, Y(8)], [x, Y(8)]], 'data', 'T2_OUTN', loop=True)
    v.wire([[x, Y(2)], [x + 80, Y(2)], [x + 80, Y(9)], [x, Y(9)]], 'data', 'T2_OUTP', loop=True)
    v.label(x + 62, Y(2), t2lab + 'P', 'T'); v.label(x + 30, Y(3), t2lab + 'N', 'T')
    for k, lab in ((10, t1lab[0]), (11, t1lab[1]), (12, t3lab + 'P'), (13, t3lab + 'N')):
        v.wire([[x, Y(k)], [x + 30, Y(k)]], 'data', lab); v.label(x + 30, Y(k), lab, 'R')

def view_top():
    c = 'RX_AFE_TOP'
    v = View('RX_AFE_TOP', 'RX_AFE_TOP — RX AFE 최상위 (블록)', c, 'block', 1420, 980,
             note='포트 37개 → 9개 그림 (데이터 입력 2, 클럭 입력 2, 출력 4, W 버스 1). 슬라이스 사이 피드백은 이름표로 연결.')
    v.wire([[100, 185], [200, 185]], 'data', 'RX_INP'); v.port('RX_INP', 100, 185, 'L')
    v.wire([[100, 215], [200, 215]], 'data', 'RX_INN'); v.port('RX_INN', 100, 215, 'L')
    mark(v, 'TERM_ESD_P', 150, 185, True, 'R·ESD', ['R_RX_P', 'M_ESD_P1', 'M_ESD_N1'],
         {'a': [[['R_RX_P', 'A'], ['M_ESD_P1', 'D'], ['M_ESD_N1', 'D']]]}, 'RX_TERM')
    mark(v, 'TERM_ESD_N', 150, 215, False, 'R·ESD', ['R_RX_N', 'M_ESD_P2', 'M_ESD_N2'],
         {'a': [[['R_RX_N', 'A'], ['M_ESD_P2', 'D'], ['M_ESD_N2', 'D']]]}, 'RX_TERM')
    v.dot(150, 185); v.dot(150, 215)
    iamp(v, 'X_CTLE1', 220, 200, 'CTLE', ['INP', 'INN'], ['OUTP', 'OUTN'], 'CTLE_STAGE', sub='X_CTLE1')
    iamp(v, 'X_CTLE2', 380, 200, 'CTLE', ['INP', 'INN'], ['OUTP', 'OUTN'], 'CTLE_STAGE', sub='X_CTLE2')
    iamp(v, 'X_VGA', 540, 200, 'VGA', ['INP', 'INN'], ['OUTP', 'OUTN'], 'VGA_STAGE', sub='X_VGA')
    v.wire([[330, 185], [360, 185]], 'data', 'CTLE1_P'); v.wire([[330, 215], [360, 215]], 'data', 'CTLE1_N')
    v.wire([[490, 185], [520, 185]], 'data', 'CTLE2_P'); v.wire([[490, 215], [520, 215]], 'data', 'CTLE2_N')
    slice_box(v, 'X_DFE_EVEN', 780, 130); slice_box(v, 'X_DFE_ODD', 780, 560)
    v.wire([[650, 185], [760, 185]], 'data', 'VGA_P'); v.wire([[650, 215], [760, 215]], 'data', 'VGA_N')
    v.wire([[700, 185], [700, 615], [760, 615]], 'data', 'VGA_P'); v.dot(700, 185)
    v.wire([[680, 215], [680, 645], [760, 645]], 'data', 'VGA_N'); v.dot(680, 215)
    v.allow(700, 215, 'differential pair fork (VGA → even / odd slice)')
    # outputs
    v.wire([[1020, 150], [1300, 150]], 'data', 'DOUT_EVEN_P'); v.port('DOUT_EVEN_P', 1300, 150, 'R')
    v.wire([[1020, 170], [1300, 170]], 'data', 'DOUT_EVEN_N'); v.port('DOUT_EVEN_N', 1300, 170, 'R')
    v.wire([[1020, 580], [1300, 580]], 'data', 'DOUT_ODD_P'); v.port('DOUT_ODD_P', 1300, 580, 'R')
    v.wire([[1020, 600], [1300, 600]], 'data', 'DOUT_ODD_N'); v.port('DOUT_ODD_N', 1300, 600, 'R')
    slice_loops(v, 1020, 130, 'E_T2', ('O_DOUTP', 'O_DOUTN'), 'O_T2')
    slice_loops(v, 1020, 560, 'O_T2', ('DOUT_EVEN_P', 'DOUT_EVEN_N'), 'E_T2')
    # TG (M_TIE): DOUT_ODD -> O_DOUT
    tgbox(v, 'TG_P', 1160, 580, ['M_TIE_P', 'M_TIE_P2'], [['M_TIE_P', 'S'], ['M_TIE_P2', 'S']],
          [['M_TIE_P', 'D'], ['M_TIE_P2', 'D']], 'RX_TG')
    v.dot(1160, 580); v.label(1160, 520, 'O_DOUTP', 'T')
    v.d['syms'].append(dict(id='TG_N', kind='tg', ops=[L((1200, 600), (1200, 615)), L((1200, 645), (1200, 660)),
        P((1187, 615), (1213, 615), (1213, 645), (1187, 645), (1187, 615), fill='#fff', w=1.4)],
        pins={'a': [1200, 600], 'b': [1200, 660]}, body=[1187, 615, 1213, 645],
        pinmap={'a': [[['M_TIE_N', 'S'], ['M_TIE_N2', 'S']]], 'b': [[['M_TIE_N', 'D'], ['M_TIE_N2', 'D']]]},
        hidden={}, link='RX_TG', represents=['M_TIE_N', 'M_TIE_N2'], slices=1))
    v.text(1200, 634, 'TG', anchor='middle', size=9, bold=True)
    v.dot(1200, 600); v.label(1200, 660, 'O_DOUTN', 'B')
    # W bus from the top: one trunk, two branches
    v.wire([[800, 40], [800, 110]], 'bus', 'W'); v.port('W<1:4>_<0:3>', 800, 40, 'T', 'bus'); bus_mark(v, 800, 92, 16, True)
    v.wire([[800, 70], [740, 70], [740, 520], [800, 520], [800, 540]], 'bus', 'W'); v.dot(800, 70)
    v.allow(740, 185, 'W bus to the lower slice crosses the main data pair')
    v.allow(740, 215, 'W bus to the lower slice crosses the main data pair')
    # clocks from below
    ibox(v, 'X_CLK', 300, 700, 480, 820, 'CLK TREE', [('CLK_INP', 'L', 35, 'clock', 'CLK_INP'),
         ('CLK_INN', 'L', 65, 'clock', 'CLK_INN'), ('CLKI', 'R', 25, 'clock', 'CLKI'), ('CLKIB', 'R', 45, 'clock', 'CLKIB'),
         ('CLKQ', 'R', 85, 'clock', 'CLKQ'), ('CLKQB', 'R', 105, 'clock', 'CLKQB')], 'CLK_DIST_TREE',
         sub='CLK_DIST_TREE', label_y=766)
    v.wire([[100, 735], [280, 735]], 'clock', 'CLK_INP'); v.port('CLK_INP', 100, 735, 'L', 'clock')
    v.wire([[100, 765], [280, 765]], 'clock', 'CLK_INN'); v.port('CLK_INN', 100, 765, 'L', 'clock')
    v.wire([[500, 785], [530, 785]], 'clock', 'CLKQ'); v.label(530, 785, 'CLKQ', 'R')
    v.wire([[500, 805], [530, 805]], 'clock', 'CLKQB'); v.label(530, 805, 'CLKQB', 'R')
    v.wire([[500, 725], [710, 725], [710, 470], [800, 470], [800, 450]], 'clock', 'CLKI')
    v.wire([[710, 725], [710, 920], [820, 920], [820, 880]], 'clock', 'CLKI'); v.dot(710, 725)
    v.wire([[500, 745], [730, 745], [730, 490], [820, 490], [820, 450]], 'clock', 'CLKIB')
    v.wire([[730, 745], [730, 900], [800, 900], [800, 880]], 'clock', 'CLKIB'); v.dot(730, 745)
    v.allow(710, 745, 'two clock wires each branch up (even) and down (odd)')
    for x in (710, 730):
        for y in (615, 645): v.allow(x, y, 'clock to the upper slice must cross the lower slice data input pair')
    v.allow(740, 470, 'W bus branch and clock to the upper slice both enter the gap between slices')
    v.allow(740, 490, 'W bus branch and clock to the upper slice both enter the gap between slices')
    v.omit('X_BIAS', 'block', 'BIAS_GEN: 바이어스 발생기 — 고속 신호와 연결 없음 (§4-3)')
    v.omit('C_RX_VCM', 'device', '입력 공통모드 디커플링 C (VCM_RX–VSS)')
    return finalize(v)

BLOCK_VIEWS = [view_top, view_clktree, view_slice, view_dff, view_sr]
