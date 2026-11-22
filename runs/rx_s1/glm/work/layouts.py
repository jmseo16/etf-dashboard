"""Concept-diagram views for rx_s1 (dq_rx_unit). Writes scenes.json.
Plan v6.1 compliance: zero crossing in block diagram, textbook unit schematics.
"""
import json, sys, collections, re, math
from netlist import parse, num, fmt_si, group_bus, Polarity
from scene import *
from spec_rules import ANALOG_ROLES, CLASS_KO

W = sys.argv[1]
NL = sys.argv[2]
cells, order = parse(NL)
A = json.load(open(W + '/analysis.json'))
ROLES = A['roles']; CN = A['cellnet']; EFF = A['eff']; INST = A['cell_insts']
VIEWS = []
POL = Polarity(cells, A['top'])

VID = {
    'top': 'b_top',
    'term': 'u_term',
    'pre': 'u_pre',
    'dfe_sum': 'u_dfe_sum',
    'sa_dt': 'u_sa_dt',
    'sr_nor': 'u_sr_nor',
    'ck_gbuf': 'u_ck_gbuf',
    'odt_dec': 'u_odt_dec',
    'ls': 'u_ls',
    'nor': 'u_nor',
    'nand': 'u_nand',
    'inv': 'u_inv'
}


def new_view(*a, **k):
    V = View(*a, **k)
    VIEWS.append(V)
    return V


def el(cell, name):
    for e in cells[cell]['elems']:
        if e['name'] == name:
            return e
    raise KeyError(cell + ':' + name)


def role(cell, name):
    return ROLES[cell][name]['role']


def T(dev, t):
    return [[(dev, t)]]


def topbot(cell, dev):
    e = el(cell, dev)
    pre = INST[cell][0]
    s, d = EFF[pre + dev]
    ts = e['terms']
    g2l = A['l2g'][pre]
    loc = {v: k for k, v in g2l.items()}
    sl = loc.get(s, s)
    st = 's' if ts['s'] == sl else 'd'
    dt = 'd' if st == 's' else 's'
    if e['type'] == 'n':
        return dt, st
    return st, dt


def mosT(cell, devs):
    if isinstance(devs, str):
        devs = [devs]
    tb = [topbot(cell, d) for d in devs]
    top = [[(d, t[0])] for d, t in zip(devs, tb)]
    bot = [[(d, t[1])] for d, t in zip(devs, tb)]
    g = [[(d, 'g')] for d in devs]
    return top, bot, g


def wl(cell, devs):
    if isinstance(devs, str):
        devs = [devs]
    es = [el(cell, d) for d in devs]
    Ws = [fmt_si(e['params'].get('w', '?')) for e in es]
    Ls = sorted({fmt_si(e['params'].get('l', '?')) for e in es}, key=lambda x: num(x) or 0)
    ms = [e['params'].get('m') for e in es]
    if len(es) == 1:
        s = '%s/%s' % (Ws[0], Ls[0])
        if ms[0] and int(ms[0]) > 1:
            s += ' m=%s' % ms[0]
        return s
    mstr = ' m=%s' % ms[0] if (ms[0] and int(ms[0]) > 1) else ''
    return '%s/%s ×%d%s' % (Ws[0], Ls[0], len(es), mstr)


def inst_terms(cell, inst, port):
    return [[(inst, port)]]


def expand_bus(name):
    m = list(re.finditer(r'<(\d+):(\d+)>', name))
    if not m:
        return [name]
    import itertools
    parts, last, rng = [], 0, []
    for g in m:
        parts.append(name[last:g.start()]); last = g.end()
        a, b = int(g.group(1)), int(g.group(2))
        rng.append(range(a, b - 1, -1) if a >= b else range(a, b + 1))
    parts.append(name[last:])
    out = []
    for combo in itertools.product(*rng):
        x = parts[0]
        for k, v in enumerate(combo):
            x += str(v) + parts[k + 1]
        out.append(x)
    return out


def finalize_omitted(V):
    drawn = set()
    for lb in V.labels:
        if lb['kind'] in ('net', 'port', 'power', 'offpage'):
            drawn |= set(expand_bus(lb['name']))
    for s_ in V.symbols:
        for p_ in s_.get('pins', []):
            on = any(any(abs(p_['x'] - a[0]) < 0.6 and abs(p_['y'] - a[1]) < 0.6 for a in (w['pts'][0], w['pts'][-1])) for w in V.wires)
            if on:
                for sl in p_['terms'] or []:
                    for e, t in sl:
                        f = el(V.cell, e)
                        drawn.add(f['pins'][t] if f['kind'] == 'inst' else f['terms'][t])
    blocks = [o for o in V.omitted if 'block' in o]
    nets = [o for o in V.omitted if 'net' in o and o['net'] not in drawn]
    bycls = collections.defaultdict(list)
    for o in nets:
        bycls[o['class']].append(o['net'])
    out = []
    for k in ('general_control', 'bias', 'power'):
        if k not in bycls:
            continue
        for bn, bits, _ in sorted(group_bus(bycls[k]), key=lambda t: t[0]):
            out.append({'net': bn, 'bits': bits, 'class': CLASS_KO.get(k, k)})
    for o in blocks:
        out.append(o)
    V.omitted = out


def gnd_at(V, x, y, net='vss', l=12):
    V.wire([(x, y), (x, y + l)], cls='power')
    gnd(V, x, y + l, net)


def busslash(V, x, y, name, n, vertical=True):
    V.line([(x - 7, y + 7), (x + 7, y - 7)], w=1.4, owner='bus')
    if re.search(r'<\d+:\d+>', name):
        return
    if vertical:
        V.text(x + 9, y + 4, str(n), size=10, anchor='start', cls='buswidth')
    else:
        V.text(x, y + 16, str(n), size=10, anchor='middle', cls='buswidth')


def stub_label(V, p, name, d, cls='data', L=24, side=None):
    x, y = p['x'], p['y']
    if d == 'left':
        e = (x - L, y)
    elif d == 'right':
        e = (x + L, y)
    elif d == 'down':
        e = (x, y + L)
    else:
        e = (x, y - L)
    V.wire([(x, y), e], cls=cls)
    if d in ('left', 'right'):
        if side == 'below':
            V.netlabel(name, (x + e[0]) / 2, y, tx=(x + e[0]) / 2, ty=y + 9, anchor='middle')
        else:
            V.netlabel(name, (x + e[0]) / 2, y, tx=(x + e[0]) / 2, ty=y - 8, anchor='middle')
    else:
        if side == 'left':
            V.netlabel(name, e[0], e[1], tx=e[0] - 4, ty=e[1] - 2, anchor='end')
        elif side == 'right':
            V.netlabel(name, e[0], e[1], tx=e[0] + 4, ty=e[1] - 2, anchor='start')
        else:
            V.netlabel(name, e[0], e[1], tx=e[0], ty=e[1] + (9 if d == 'down' else -9), anchor='middle')
    return e


# =====================================================================================
# 1. VIEW_TOP: dq_rx_unit block diagram
# =====================================================================================
def view_top():
    cell = 'dq_rx_unit'
    V = new_view('b_top', cell, 'block', 'DQ_RX_UNIT — 블록 레벨 (최상위)', 1580, 920)

    # Omitted items for side panel
    for p in ('ofe_p<1>', 'ofe_p<0>', 'ofe_n<1>', 'ofe_n<0>', 'ofo_p<1>', 'ofo_p<0>', 'ofo_n<1>', 'ofo_n<0>'):
        V.omitted.append({'net': p, 'class': 'general_control'})
    V.omitted.append({'net': 'ibias', 'class': 'bias'})
    for p in ('vdd', 'vddq', 'vss', 'vssq'):
        V.omitted.append({'net': p, 'class': 'power'})
    V.omitted.append({'block': 'xi23', 'cell': 'rx_bias', 'class': 'bias', 'reason': '바이어스 발생기 (고속 경로 밖)'})

    # Left input ports
    # pad
    y_pad = 280
    V.port('pad', 90, y_pad, d='right', io='in')
    V.wire([(90, y_pad), (180, y_pad)], cls='data')

    # esd_dq marker at x=180
    # xi20: pad, net1, vddq, vssq
    V.circle(180, y_pad, 12, fill='#fff', stroke=BLACK, owner='xi20')
    V.text(180, y_pad, 'ESD', size=9, anchor='middle', weight='bold', owner='xi20')
    V.add_symbol('xi20', 'esd', [[168, y_pad - 12, 192, y_pad + 12]],
                 [pin('pad', 180, y_pad, [[('xi20', 'pad')]]), pin('pad_r', 180, y_pad, [[('xi20', 'pad_r')]])],
                 members=['xi20'], link='u_term')
    V.text(180, y_pad - 18, 'xi20 (esd_dq)', size=9, anchor='middle', italic=True, color='#444')
    V.wire([(180, y_pad), (280, y_pad)], cls='data')
    V.netlabel('net1', 230, y_pad - 8)

    # odt_pu marker at x=280
    # xi21: pad, net2<2>, net2<1>, net2<0>, vddq
    # Drawn as variable resistor to VDDQ
    res(V, 'xi21', 280, y_pad - 50, orient='v', name='xi21 (odt_pu)', size='60/120/240Ω',
        a=[[('xi21', 'vddq')]], b=[[('xi21', 'pad')]], var=True, members=['xi21'], label_side='right')
    V.wire([(280, y_pad - 20), (280, y_pad)], cls='data')
    V.dot(280, y_pad)
    V.wire([(280, y_pad - 80), (280, y_pad - 90)], cls='power')
    vdd_tee(V, 280, y_pad - 90, 'vddq', 'VDDQ')
    # ODT control bus from odt_dec to odt_pu
    # xi22: odt_en, rtt<2>, rtt<1>, rtt<0>, net2<2>, net2<1>, net2<0>, vdd, vddq, vss
    box(V, 'xi22', 120, 80, 110, 60, 'DEC', 'xi22 (odt_dec)',
        left=[('odt_en', 100, [[('xi22', 'odt_en')]], 'data'), ('rtt<2:0>', 125, [[('xi22', 'rtt<2>')], [('xi22', 'rtt<1>')], [('xi22', 'rtt<0>')]], 'bus')],
        right=[('enb<2:0>', 110, [[('xi22', 'enb<2>')], [('xi22', 'enb<1>')], [('xi22', 'enb<0>')]], 'bus')],
        link='u_odt_dec', members=['xi22'])
    V.port('odt_en', 60, 100, d='right', io='in')
    V.wire([(60, 100), (100, 100)], cls='data')
    V.port('rtt<2:0>', 60, 125, d='right', io='in', cls='bus')
    V.wire([(60, 125), (100, 125)], cls='bus')
    busslash(V, 80, 125, 'rtt<2:0>', 3, vertical=True)
    # output of odt_dec: net2<2:0> bus to odt_pu
    V.wire([(230, 110), (260, 110), (260, y_pad - 50)], cls='bus')
    busslash(V, 260, 140, 'net2<2:0>', 3, vertical=True)
    V.netlabel('net2<2:0>', 265, 130)

    # vref input with RC filter (r0 5k, mn0 MOS cap)
    y_vref = 380
    V.port('vref', 90, y_vref, d='right', io='in')
    V.wire([(90, y_vref), (150, y_vref)], cls='plain')
    res(V, 'r0', 180, y_vref, orient='h', name='r0', size='5k',
        a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='above')
    V.wire([(210, y_vref), (280, y_vref)], cls='plain')
    # mn0 MOS cap to vssq at x=250
    cap(V, 'mn0', 250, y_vref + 40, orient='v', name='mn0', size='10u/2u m=4',
        a=[[('mn0', 'g')]], b=[[('mn0', 's')]], members=['mn0'], label_side='right')
    V.wire([(250, y_vref), (250, y_vref + 10)], cls='plain')
    V.dot(250, y_vref)
    gnd_at(V, 250, y_vref + 70, 'vssq')
    V.netlabel('net3', 270, y_vref - 8)

    # loopback data inputs: lb_p, lb_n
    y_lbp, y_lbn = 460, 500
    V.port('lb_p', 90, y_lbp, d='right', io='in')
    V.wire([(90, y_lbp), (330, y_lbp)], cls='data')
    V.port('lb_n', 90, y_lbn, d='right', io='in')
    V.wire([(90, y_lbn), (330, y_lbn)], cls='data')

    # Wire pad (net1) and vref (net3) into rx_pre
    V.wire([(280, y_pad), (330, y_pad)], cls='data')
    V.wire([(280, y_vref), (330, y_vref)], cls='plain')

    # rx_pre (PREAMP) block at x0=350, y0=240, w=120, h=300
    # xi24: net1, net3, lb_p, lb_n, net102, net104, net4, net6, net7, vddq, vssq
    box(V, 'xi24', 350, 240, 120, 300, 'PREAMP', 'xi24 (rx_pre)',
        left=[
            ('inp', y_pad, [[('xi24', 'inp')]], 'data'),
            ('vref', y_vref, [[('xi24', 'vref')]], 'plain'),
            ('lbp', y_lbp, [[('xi24', 'lbp')]], 'data'),
            ('lbn', y_lbn, [[('xi24', 'lbn')]], 'data')
        ],
        right=[
            ('outp', 320, [[('xi24', 'outp')]], 'data'),
            ('outn', 380, [[('xi24', 'outn')]], 'data')
        ],
        top=[('sel_m', 380, [[('xi24', 'sel_m')]], 'data'), ('sel_l', 420, [[('xi24', 'sel_l')]], 'data')],
        link='u_pre', members=['xi24'])

    # Control logic above rx_pre: lb_en and rx_en to sel_m (net102) and sel_l (net104)
    # Shown cleanly with ports and logic stubs
    V.port('rx_en', 380, 50, d='down', io='in')
    V.wire([(380, 50), (380, 220)], cls='data')
    V.netlabel('rx_en', 385, 90)

    V.port('lb_en', 420, 50, d='down', io='in')
    V.wire([(420, 50), (420, 220)], cls='data')
    V.netlabel('lb_en', 425, 90)

    # Clock block: ck_gbuf at bottom left
    # xi25: ck, ckb, rx_en, net8, net9, vdd, vss
    y_ck, y_ckb = 740, 780
    V.port('ck', 90, y_ck, d='right', io='in', cls='clock')
    V.port('ckb', 90, y_ckb, d='right', io='in', cls='clock')
    V.wire([(90, y_ck), (330, y_ck)], cls='clock')
    V.wire([(90, y_ckb), (330, y_ckb)], cls='clock')

    box(V, 'xi25', 350, 710, 120, 100, 'CLK GBUF', 'xi25 (ck_gbuf)',
        left=[('ck', y_ck, [[('xi25', 'ck')]], 'clock'), ('ckb', y_ckb, [[('xi25', 'ckb')]], 'clock')],
        right=[('cko', y_ck, [[('xi25', 'cko')]], 'clock'), ('ckob', y_ckb, [[('xi25', 'ckob')]], 'clock')],
        top=[('en', 410, [[('xi25', 'en')]], 'data')],
        link='u_ck_gbuf', members=['xi25'])
    # rx_en branch to ck_gbuf top
    stub_label(V, {'x': 410, 'y': 690}, 'rx_en', 'up', cls='data', L=20)

    # Clocks out of ck_gbuf: net8 (cko, even clock), net9 (ckob, odd clock)
    # Using netlabels to avoid crossing across the whole diagram!
    stub_label(V, {'x': 490, 'y': y_ck}, 'net8', 'right', cls='clock', L=40)
    stub_label(V, {'x': 490, 'y': y_ckb}, 'net9', 'right', cls='clock', L=40)

    # Outputs of rx_pre: net6 (outp), net7 (outn)
    # Route net6 and net7 to Even slice (upper) and Odd slice (lower)
    V.wire([(490, 320), (550, 320)], cls='data')
    V.wire([(490, 380), (550, 380)], cls='data')
    V.netlabel('net6', 510, 312)
    V.netlabel('net7', 510, 372)

    # Even slice (upper lane, y around 260..420)
    # ----------------------------------------------------
    # xi26: dfe_sum (even)
    # pins: inp=net6, inn=net7, hp=net16, hn=net17, tap<3:0>, sgn=net106, sgnb=net105, en=rx_en, vbn=ibias, outp=net10, outn=net11
    box(V, 'xi26', 600, 250, 110, 150, 'Σ (SUM)', 'xi26 (dfe_sum)',
        left=[
            ('inp', 290, [[('xi26', 'inp')]], 'data'),
            ('inn', 350, [[('xi26', 'inn')]], 'data'),
            ('hp', 310, [[('xi26', 'hp')]], 'data'),
            ('hn', 370, [[('xi26', 'hn')]], 'data')
        ],
        right=[
            ('outp', 300, [[('xi26', 'outp')]], 'data'),
            ('outn', 360, [[('xi26', 'outn')]], 'data')
        ],
        top=[
            ('tap<3:0>', 630, [[('xi26', 'tap<3>')], [('xi26', 'tap<2>')], [('xi26', 'tap<1>')], [('xi26', 'tap<0>')]], 'bus'),
            ('tap_sgn', 670, [[('xi26', 'sgn')]], 'data')
        ],
        link='u_dfe_sum', members=['xi26'])

    # Connect net6, net7 to xi26
    V.wire([(550, 320), (570, 320), (570, 290), (580, 290)], cls='data')
    V.wire([(550, 380), (560, 380), (560, 350), (580, 350)], cls='data')
    V.dot(570, 320); V.dot(560, 380)

    # Feedback hp (net16), hn (net17) from odd slice via clean netlabel stubs (0 crossings!)
    stub_label(V, {'x': 580, 'y': 310}, 'net16', 'left', cls='data', L=30)
    stub_label(V, {'x': 580, 'y': 370}, 'net17', 'left', cls='data', L=30)

    # Top control bus to xi26: tap<3:0> and tap_sgn
    V.port('tap<3:0>', 630, 160, d='down', io='in', cls='bus')
    V.wire([(630, 160), (630, 230)], cls='bus')
    busslash(V, 630, 195, 'tap<3:0>', 4, vertical=True)
    V.port('tap_sgn', 670, 160, d='down', io='in')
    V.wire([(670, 160), (670, 230)], cls='data')

    # xi28: sa_dt (even comparator)
    # pins: inp=net10, inn=net11, ck=net8, outp=net18, outn=net19
    tri(V, 'xi28', 770, 330, 'SA', 'xi28 (sa_dt)', w=80, h=100,
        ins=[('inp', -30, [[('xi28', 'inp')]]), ('inn', 30, [[('xi28', 'inn')]])],
        outs=[('outp', -30, [[('xi28', 'outp')]]), ('outn', 30, [[('xi28', 'outn')]])],
        bottom=[('ck', 40, [[('xi28', 'ck')]], 'clock')],
        clock_mark=True, link='u_sa_dt', members=['xi28'])

    # Wires from xi26 to xi28: net10, net11
    V.wire([(730, 300), (750, 300)], cls='data')
    V.netlabel('net10', 735, 292)
    V.wire([(730, 360), (750, 360)], cls='data')
    V.netlabel('net11', 735, 352)

    # Clock into xi28: net8 (even clock)
    stub_label(V, {'x': 810, 'y': 400}, 'net8', 'down', cls='clock', L=20)

    # xi30: sr_nor (even SR latch)
    # pins: s=net18, r=net19, q=net14, qb=net15
    box(V, 'xi30', 910, 260, 90, 130, 'SR LATCH', 'xi30 (sr_nor)',
        left=[('s', 300, [[('xi30', 's')]], 'data'), ('r', 360, [[('xi30', 'r')]], 'data')],
        right=[('q', 300, [[('xi30', 'q')]], 'data'), ('qb', 360, [[('xi30', 'qb')]], 'data')],
        link='u_sr_nor', members=['xi30'])

    # Wires from xi28 to xi30: net18, net19
    V.wire([(870, 300), (890, 300)], cls='data')
    V.netlabel('net18', 875, 292)
    V.wire([(870, 360), (890, 360)], cls='data')
    V.netlabel('net19', 875, 352)

    # Outputs of xi30: net14 (q) and net15 (qb)
    # net14 goes to xi7 and branches to odd slice feedback (netlabel)
    V.wire([(1020, 300), (1070, 300)], cls='data')
    V.dot(1040, 300)
    V.wire([(1040, 300), (1040, 270)], cls='data')
    V.netlabel('net14', 1045, 265)

    # net15 goes to xi9 (unused inverter)
    V.wire([(1020, 360), (1070, 360)], cls='data')
    V.dot(1040, 360)
    V.wire([(1040, 360), (1040, 390)], cls='data')
    V.netlabel('net15', 1045, 395)

    # Inverters for even output:
    # xi7: a=net14, y=net26
    inv(V, 'xi7', 1070, 300, 'xi7 (inv_a)', [[('xi7', 'a')]], [[('xi7', 'y')]], link='u_inv', members=['xi7'])
    # xi8: a=net26, y=dout_e
    V.wire([(1132, 300), (1170, 300)], cls='data')
    V.netlabel('net26', 1145, 292)
    inv(V, 'xi8', 1170, 300, 'xi8 (inv_c)', [[('xi8', 'a')]], [[('xi8', 'y')]], link='u_inv', members=['xi8'])
    V.wire([(1232, 300), (1310, 300)], cls='data')
    V.port('dout_e', 1310, 300, d='right', io='out')

    # Unused inverter xi9: a=net15, y=net27
    inv(V, 'xi9', 1070, 360, 'xi9 (inv_a)', [[('xi9', 'a')]], [[('xi9', 'y')]], link='u_inv', members=['xi9'])
    # net27: unused output (short wire + netlabel per §3.5-4)
    V.wire([(1132, 360), (1170, 360)], cls='data')
    V.netlabel('net27', 1175, 352)

    # Odd slice (lower lane, y around 500..660)
    # ----------------------------------------------------
    # xi27: dfe_sum (odd)
    # pins: inp=net6, inn=net7, hp=net14, hn=net15, tap<3:0>, sgn=net106, sgnb=net105, en=rx_en, vbn=ibias, outp=net12, outn=net13
    box(V, 'xi27', 600, 490, 110, 150, 'Σ (SUM)', 'xi27 (dfe_sum)',
        left=[
            ('inp', 530, [[('xi27', 'inp')]], 'data'),
            ('inn', 590, [[('xi27', 'inn')]], 'data'),
            ('hp', 550, [[('xi27', 'hp')]], 'data'),
            ('hn', 610, [[('xi27', 'hn')]], 'data')
        ],
        right=[
            ('outp', 540, [[('xi27', 'outp')]], 'data'),
            ('outn', 600, [[('xi27', 'outn')]], 'data')
        ],
        top=[
            ('tap<3:0>', 630, [[('xi27', 'tap<3>')], [('xi27', 'tap<2>')], [('xi27', 'tap<1>')], [('xi27', 'tap<0>')]], 'bus'),
            ('tap_sgn', 670, [[('xi27', 'sgn')]], 'data')
        ],
        link='u_dfe_sum', members=['xi27'])

    # Branch net6 and net7 down to xi27
    V.wire([(570, 320), (570, 530), (580, 530)], cls='data')
    V.wire([(560, 380), (560, 590), (580, 590)], cls='data')

    # Feedback hp (net14), hn (net15) from even slice via clean netlabel stubs (0 crossings!)
    stub_label(V, {'x': 580, 'y': 550}, 'net14', 'left', cls='data', L=30)
    stub_label(V, {'x': 580, 'y': 610}, 'net15', 'left', cls='data', L=30)

    # Control to xi27: tap<3:0> and tap_sgn
    stub_label(V, {'x': 630, 'y': 470}, 'tap<3:0>', 'up', cls='bus', L=20)
    stub_label(V, {'x': 670, 'y': 470}, 'tap_sgn', 'up', cls='data', L=20)

    # xi29: sa_dt (odd comparator)
    # pins: inp=net12, inn=net13, ck=net9, outp=net24, outn=net25
    tri(V, 'xi29', 770, 570, 'SA', 'xi29 (sa_dt)', w=80, h=100,
        ins=[('inp', -30, [[('xi29', 'inp')]]), ('inn', 30, [[('xi29', 'inn')]])],
        outs=[('outp', -30, [[('xi29', 'outp')]]), ('outn', 30, [[('xi29', 'outn')]])],
        bottom=[('ck', 40, [[('xi29', 'ck')]], 'clock')],
        clock_mark=True, link='u_sa_dt', members=['xi29'])

    # Wires from xi27 to xi29: net12, net13
    V.wire([(730, 540), (750, 540)], cls='data')
    V.netlabel('net12', 735, 532)
    V.wire([(730, 600), (750, 600)], cls='data')
    V.netlabel('net13', 735, 592)

    # Clock into xi29: net9 (odd clock)
    stub_label(V, {'x': 810, 'y': 640}, 'net9', 'down', cls='clock', L=20)

    # xi31: sr_nor (odd SR latch)
    # pins: s=net24, r=net25, q=net16, qb=net17
    box(V, 'xi31', 910, 500, 90, 130, 'SR LATCH', 'xi31 (sr_nor)',
        left=[('s', 540, [[('xi31', 's')]], 'data'), ('r', 600, [[('xi31', 'r')]], 'data')],
        right=[('q', 540, [[('xi31', 'q')]], 'data'), ('qb', 600, [[('xi31', 'qb')]], 'data')],
        link='u_sr_nor', members=['xi31'])

    # Wires from xi29 to xi31: net24, net25
    V.wire([(870, 540), (890, 540)], cls='data')
    V.netlabel('net24', 875, 532)
    V.wire([(870, 600), (890, 600)], cls='data')
    V.netlabel('net25', 875, 592)

    # Outputs of xi31: net16 (q) and net17 (qb)
    V.wire([(1020, 540), (1070, 540)], cls='data')
    V.dot(1040, 540)
    V.wire([(1040, 540), (1040, 510)], cls='data')
    V.netlabel('net16', 1045, 505)

    V.wire([(1020, 600), (1070, 600)], cls='data')
    V.dot(1040, 600)
    V.wire([(1040, 600), (1040, 630)], cls='data')
    V.netlabel('net17', 1045, 635)

    # Inverters for odd output:
    # xi10: a=net16, y=net28
    inv(V, 'xi10', 1070, 540, 'xi10 (inv_a)', [[('xi10', 'a')]], [[('xi10', 'y')]], link='u_inv', members=['xi10'])
    # xi11: a=net28, y=dout_o
    V.wire([(1132, 540), (1170, 540)], cls='data')
    V.netlabel('net28', 1145, 532)
    inv(V, 'xi11', 1170, 540, 'xi11 (inv_c)', [[('xi11', 'a')]], [[('xi11', 'y')]], link='u_inv', members=['xi11'])
    V.wire([(1232, 540), (1310, 540)], cls='data')
    V.port('dout_o', 1310, 540, d='right', io='out')

    # Unused inverter xi12: a=net17, y=net29
    inv(V, 'xi12', 1070, 600, 'xi12 (inv_a)', [[('xi12', 'a')]], [[('xi12', 'y')]], link='u_inv', members=['xi12'])
    V.wire([(1132, 600), (1170, 600)], cls='data')
    V.netlabel('net29', 1175, 592)

    finalize_omitted(V)
    return V


# =====================================================================================
# 2. VIEW_TERM: u_term (esd_dq and odt_pu)
# =====================================================================================
def view_term():
    cell = 'esd_dq'
    V = new_view('u_term', cell, 'unit', 'ESD_DQ & ODT_PU — unit level (종단 및 ESD)', 960, 640)
    rail(V, 80, 880, 80, 'vddq', 'VDDQ')
    rail(V, 80, 880, 560, 'vssq', 'VSSQ')

    # pad line across
    V.wire([(80, 300), (880, 300)], cls='data')
    V.port('pad', 80, 300, d='right', io='in')
    V.port('pad_r', 880, 300, d='right', io='out')

    # esd_dq components:
    # d0: pad -> vddq; d1: vssq -> pad
    V.dot(200, 300)
    # diode d0 to vddq
    V.wire([(200, 300), (200, 220)], cls='plain')
    V.circle(200, 190, 12, owner='d0')
    V.text(200, 190, 'D0', size=9, anchor='middle', owner='d0')
    V.wire([(200, 160), (200, 80)], cls='power')
    V.dot(200, 80)
    V.add_symbol('d0', 'diode', [[188, 178, 212, 202]], [pin('p', 200, 220, [[('d0', 'p')]]), pin('n', 200, 160, [[('d0', 'n')]])], members=['d0'])

    # diode d1 from vssq
    V.wire([(200, 300), (200, 380)], cls='plain')
    V.circle(200, 410, 12, owner='d1')
    V.text(200, 410, 'D1', size=9, anchor='middle', owner='d1')
    V.wire([(200, 440), (200, 560)], cls='power')
    V.dot(200, 560)
    V.add_symbol('d1', 'diode', [[188, 398, 212, 422]], [pin('p', 200, 440, [[('d1', 'p')]]), pin('n', 200, 380, [[('d1', 'n')]])], members=['d1'])

    # series resistor r0 150 ohm
    res(V, 'r0', 360, 300, orient='h', name='r0', size='150Ω', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='above')

    # clamp NMOS mn0 with gate resistor r1 (10k)
    V.dot(500, 300)
    t_, b_, g_ = mosT('esd_dq', 'mn0')
    mos(V, 'mn0', 500, 400, 'n', gate='left', name='mn0', size=wl('esd_dq', 'mn0'), top=t_, bot=b_, gterm=g_, members=['mn0'])
    V.wire([(500, 300), (500, 370)], cls='plain')
    V.wire([(500, 430), (500, 560)], cls='power'); V.dot(500, 560)

    # r1 10k from gate net9 to vssq
    res(V, 'r1', 440, 480, orient='v', name='r1', size='10k', a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='left')
    V.wire([(460, 400), (440, 400), (440, 450)], cls='plain')
    V.wire([(440, 510), (440, 560)], cls='power'); V.dot(440, 560)

    finalize_omitted(V)
    return V


# =====================================================================================
# 3. VIEW_PRE: u_pre (rx_pre unit view)
# =====================================================================================
def view_pre():
    cell = 'rx_pre'
    V = new_view('u_pre', cell, 'unit', 'RX_PRE — unit level (전치증폭기/MUX, 대칭)', 980, 720)
    rail(V, 100, 880, 80, 'vddq', 'VDDQ')
    rail(V, 100, 880, 640, 'vssq', 'VSSQ')
    AX = 490

    # Resistor loads r0 (800 ohm, outn), r1 (800 ohm, outp)
    xL, xR = AX - 120, AX + 120
    res(V, 'r1', xL, 160, orient='v', name='r1', size='800Ω', a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='left')
    res(V, 'r0', xR, 160, orient='v', name='r0', size='800Ω', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='right')
    V.wire([(xL, 80), (xL, 130)], cls='power'); V.dot(xL, 80)
    V.wire([(xR, 80), (xR, 130)], cls='power'); V.dot(xR, 80)

    # Outputs outp (xL), outn (xR)
    y_out = 220
    V.wire([(xL, 190), (xL, y_out)], cls='data')
    V.wire([(xR, 190), (xR, y_out)], cls='data')
    V.wire([(xL, y_out), (80, y_out)], cls='data'); V.port('outp', 80, y_out, d='left', io='out')
    V.wire([(xR, y_out), (900, y_out)], cls='data'); V.port('outn', 900, y_out, d='right', io='out')
    V.dot(xL, y_out); V.dot(xR, y_out)

    # Main input pair: mn0 (inp, xL), mn1 (vref, xR)
    y_main = 300
    t0, b0, g0 = mosT(cell, 'mn0')
    t1, b1, g1 = mosT(cell, 'mn1')
    mos(V, 'mn0', xL, y_main, 'n', gate='left', name='mn0', size=wl(cell, 'mn0'), top=t0, bot=b0, gterm=g0, members=['mn0'])
    mos(V, 'mn1', xR, y_main, 'n', gate='right', name='mn1', size=wl(cell, 'mn1'), top=t1, bot=b1, gterm=g1, members=['mn1'])
    V.wire([(xL, y_out), (xL, y_main - 30)], cls='data')
    V.wire([(xR, y_out), (xR, y_main - 30)], cls='data')

    # Ports for inp and vref
    V.wire([(xL - 40, y_main), (80, y_main)], cls='data'); V.port('inp', 80, y_main, d='left', io='in')
    V.wire([(xR + 40, y_main), (900, y_main)], cls='plain'); V.port('vref', 900, y_main, d='right', io='in')

    # Common source node net40, switch mn2 (sel_m) and tail mn3 (vbn)
    V.wire([(xL, y_main + 30), (xL, 360), (xR, 360), (xR, y_main + 30)], cls='plain')
    V.dot(AX, 360)
    t2, b2, g2 = mosT(cell, 'mn2')
    mos(V, 'mn2', AX, 410, 'n', gate='left', name='mn2', size=wl(cell, 'mn2'), top=t2, bot=b2, gterm=g2, members=['mn2'])
    V.wire([(AX, 360), (AX, 380)], cls='plain')
    V.port('sel_m', AX - 70, 410, d='right', io='in')
    V.wire([(AX - 70, 410), (AX - 40, 410)], cls='data')

    t3, b3, g3 = mosT(cell, 'mn3')
    mos(V, 'mn3', AX, 510, 'n', gate='left', name='mn3', size=wl(cell, 'mn3'), top=t3, bot=b3, gterm=g3, members=['mn3'])
    V.wire([(AX, 440), (AX, 480)], cls='plain')
    V.port('vbn', AX - 70, 510, d='right', io='in')
    V.wire([(AX - 70, 510), (AX - 40, 510)], cls='plain')
    V.wire([(AX, 540), (AX, 640)], cls='power'); V.dot(AX, 640)

    # Neutralization capacitors: mn8 (outp/inp), mn9 (outn/vref)
    cap(V, 'mn8', xL - 60, 250, orient='v', name='mn8 (cap)', size=wl(cell, 'mn8'), a=[[('mn8', 'g')]], b=[[('mn8', 'd')]], members=['mn8'])
    cap(V, 'mn9', xR + 60, 250, orient='v', name='mn9 (cap)', size=wl(cell, 'mn9'), a=[[('mn9', 'g')]], b=[[('mn9', 'd')]], members=['mn9'])

    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [['mn0', 'mn1'], ['mn8', 'mn9'], ['r1', 'r0']]})
    finalize_omitted(V)
    return V


# =====================================================================================
# 4. VIEW_DFE_SUM: u_dfe_sum (dfe_sum unit view)
# =====================================================================================
def view_dfe_sum():
    cell = 'dfe_sum'
    V = new_view('u_dfe_sum', cell, 'unit', 'DFE_SUM — unit level (DFE summer Σ, 대칭)', 1120, 720)
    rail(V, 80, 1040, 70, 'vdd', 'VDD')
    rail(V, 80, 1040, 650, 'vss', 'VSS')
    AX = 560

    # Load resistors r1 (outp), r0 (outn) 600 ohm
    xL, xR = AX - 140, AX + 140
    res(V, 'r1', xL, 140, orient='v', name='r1', size='600Ω', a=[[('r1', 'p')]], b=[[('r1', 'n')]], members=['r1'], label_side='left')
    res(V, 'r0', xR, 140, orient='v', name='r0', size='600Ω', a=[[('r0', 'p')]], b=[[('r0', 'n')]], members=['r0'], label_side='right')
    V.wire([(xL, 70), (xL, 110)], cls='power'); V.dot(xL, 70)
    V.wire([(xR, 70), (xR, 110)], cls='power'); V.dot(xR, 70)

    # Output ports
    y_out = 190
    V.wire([(xL, 170), (xL, y_out)], cls='data'); V.wire([(xR, 170), (xR, y_out)], cls='data')
    V.wire([(xL, y_out), (80, y_out)], cls='data'); V.port('outp', 80, y_out, d='left', io='out')
    V.wire([(xR, y_out), (1040, y_out)], cls='data'); V.port('outn', 1040, y_out, d='right', io='out')
    V.dot(xL, y_out); V.dot(xR, y_out)

    # Main differential pair: mn0 (inp, xL), mn1 (inn, xR)
    y_main = 270
    t0, b0, g0 = mosT(cell, 'mn0')
    t1, b1, g1 = mosT(cell, 'mn1')
    mos(V, 'mn0', xL, y_main, 'n', gate='left', name='mn0', size=wl(cell, 'mn0'), top=t0, bot=b0, gterm=g0, members=['mn0'])
    mos(V, 'mn1', xR, y_main, 'n', gate='right', name='mn1', size=wl(cell, 'mn1'), top=t1, bot=b1, gterm=g1, members=['mn1'])
    V.wire([(xL, y_out), (xL, y_main - 30)], cls='data')
    V.wire([(xR, y_out), (xR, y_main - 30)], cls='data')

    V.wire([(xL - 40, y_main), (80, y_main)], cls='data'); V.port('inp', 80, y_main, d='left', io='in')
    V.wire([(xR + 40, y_main), (1040, y_main)], cls='data'); V.port('inn', 1040, y_main, d='right', io='in')

    # Main pair tail: mn2 (en) + mn3 (vbn)
    V.wire([(xL, y_main + 30), (xL, 330), (xR, 330), (xR, y_main + 30)], cls='plain')
    V.dot(AX, 330)
    t2, b2, g2 = mosT(cell, 'mn2')
    mos(V, 'mn2', AX, 380, 'n', gate='left', name='mn2', size=wl(cell, 'mn2'), top=t2, bot=b2, gterm=g2, members=['mn2'])
    V.wire([(AX, 330), (AX, 350)], cls='plain')
    V.port('en', AX - 70, 380, d='right', io='in')
    V.wire([(AX - 70, 380), (AX - 40, 380)], cls='data')

    t3, b3, g3 = mosT(cell, 'mn3')
    mos(V, 'mn3', AX, 480, 'n', gate='left', name='mn3', size=wl(cell, 'mn3'), top=t3, bot=b3, gterm=g3, members=['mn3'])
    V.wire([(AX, 410), (AX, 450)], cls='plain')
    V.port('vbn', AX - 70, 480, d='right', io='in')
    V.wire([(AX - 70, 480), (AX - 40, 480)], cls='plain')
    V.wire([(AX, 510), (AX, 650)], cls='power'); V.dot(AX, 650)

    # Feedback tap pair: mn4 (hp), mn5 (hn)
    # Merged IDAC current sources
    V.text(AX, 580, 'IDAC 탭 전류원 (tap<3:0> 가중치 합산)', size=11, anchor='middle', weight='bold')

    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [['mn0', 'mn1'], ['r1', 'r0'], ['mn4', 'mn5']]})
    finalize_omitted(V)
    return V


# =====================================================================================
# 5. VIEW_SA_DT: u_sa_dt (sa_dt unit view)
# =====================================================================================
def view_sa_dt():
    cell = 'sa_dt'
    V = new_view('u_sa_dt', cell, 'unit', 'SA_DT — unit level (Double-Tail 동적 비교기, 대칭)', 1080, 720)
    rail(V, 80, 1000, 70, 'vdd', 'VDD')
    rail(V, 80, 1000, 650, 'vss', 'VSS')
    AX = 540

    # 1st stage: clocked tail mn0, input pair mn1/mn2, precharge mp0/mp1
    xL, xR = AX - 140, AX + 140
    # Precharge PMOS mp0 (xL), mp1 (xR)
    tp0, bp0, gp0 = mosT(cell, 'mp0')
    tp1, bp1, gp1 = mosT(cell, 'mp1')
    mos(V, 'mp0', xL, 150, 'p', gate='left', name='mp0', size=wl(cell, 'mp0'), top=tp0, bot=bp0, gterm=gp0, members=['mp0'])
    mos(V, 'mp1', xR, 150, 'p', gate='right', name='mp1', size=wl(cell, 'mp1'), top=tp1, bot=bp1, gterm=gp1, members=['mp1'])
    V.wire([(xL, 70), (xL, 120)], cls='power'); V.dot(xL, 70)
    V.wire([(xR, 70), (xR, 120)], cls='power'); V.dot(xR, 70)

    # 1st stage diff pair: mn1 (inp), mn2 (inn)
    y_in = 260
    t1, b1, g1 = mosT(cell, 'mn1')
    t2, b2, g2 = mosT(cell, 'mn2')
    mos(V, 'mn1', xL, y_in, 'n', gate='left', name='mn1', size=wl(cell, 'mn1'), top=t1, bot=b1, gterm=g1, members=['mn1'])
    mos(V, 'mn2', xR, y_in, 'n', gate='right', name='mn2', size=wl(cell, 'mn2'), top=t2, bot=b2, gterm=g2, members=['mn2'])
    V.wire([(xL, 180), (xL, y_in - 30)], cls='data')
    V.wire([(xR, 180), (xR, y_in - 30)], cls='data')

    V.wire([(xL - 40, y_in), (80, y_in)], cls='data'); V.port('inp', 80, y_in, d='left', io='in')
    V.wire([(xR + 40, y_in), (1000, y_in)], cls='data'); V.port('inn', 1000, y_in, d='right', io='in')

    # Clocked tail mn0 (ck)
    V.wire([(xL, y_in + 30), (xL, 330), (xR, 330), (xR, y_in + 30)], cls='plain')
    V.dot(AX, 330)
    t0, b0, g0 = mosT(cell, 'mn0')
    mos(V, 'mn0', AX, 380, 'n', gate='left', name='mn0', size=wl(cell, 'mn0'), top=t0, bot=b0, gterm=g0, members=['mn0'])
    V.wire([(AX, 330), (AX, 350)], cls='plain')
    V.wire([(AX, 410), (AX, 650)], cls='power'); V.dot(AX, 650)

    # Clock port ck
    V.port('ck', AX - 70, 380, d='right', io='in', cls='clock')
    V.wire([(AX - 70, 380), (AX - 40, 380)], cls='clock')

    # 2nd stage: cross-coupled latch and output ports outp, outn
    V.port('outp', 80, 500, d='left', io='out')
    V.port('outn', 1000, 500, d='right', io='out')

    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [['mp0', 'mp1'], ['mn1', 'mn2']]})
    finalize_omitted(V)
    return V


# =====================================================================================
# 6. VIEW_SR_NOR: u_sr_nor (sr_nor unit view)
# =====================================================================================
def view_sr_nor():
    cell = 'sr_nor'
    V = new_view('u_sr_nor', cell, 'unit', 'SR_NOR — unit level (교차 결합 NOR 래치)', 820, 520)
    # xi0, xi1: nor2_c
    # xi0: r, qb, q, vdd, vss
    # xi1: s, q, qb, vdd, vss
    box(V, 'xi0', 280, 140, 100, 80, 'NOR2', 'xi0',
        left=[('r', 160, [[('xi0', 'a')]], 'data'), ('qb', 200, [[('xi0', 'b')]], 'data')],
        right=[('q', 180, [[('xi0', 'y')]], 'data')],
        bubbles=('q',), link='u_nor', members=['xi0'])

    box(V, 'xi1', 280, 300, 100, 80, 'NOR2', 'xi1',
        left=[('q', 320, [[('xi1', 'b')]], 'data'), ('s', 360, [[('xi1', 'a')]], 'data')],
        right=[('qb', 340, [[('xi1', 'y')]], 'data')],
        bubbles=('qb',), link='u_nor', members=['xi1'])

    # External ports
    V.port('r', 100, 160, d='right', io='in'); V.wire([(100, 160), (260, 160)], cls='data')
    V.port('s', 100, 360, d='right', io='in'); V.wire([(100, 360), (260, 360)], cls='data')
    V.port('q', 620, 180, d='right', io='out'); V.wire([(400, 180), (620, 180)], cls='data')
    V.port('qb', 620, 340, d='right', io='out'); V.wire([(400, 340), (620, 340)], cls='data')

    # Cross coupling
    V.dot(480, 180); V.dot(480, 340)
    V.wire([(480, 180), (480, 260), (220, 260), (220, 320), (260, 320)], cls='data')
    V.wire([(480, 340), (480, 275), (200, 275), (200, 200), (260, 200)], cls='data')
    V.allowed_cross.append({'at': [220, 275], 'reason': 'SR latch cross-coupling feedback'})

    finalize_omitted(V)
    return V


# =====================================================================================
# 7. VIEW_CK_GBUF: u_ck_gbuf
# =====================================================================================
def view_ck_gbuf():
    cell = 'ck_gbuf'
    V = new_view('u_ck_gbuf', cell, 'unit', 'CK_GBUF — unit level (클럭 게이팅 버퍼)', 860, 520)
    # xi0 (nand2_c): ck, en, net70
    # xi1 (nand2_c): ckb, en, net71
    # xi2 (inv_c): net70, cko
    # xi3 (inv_c): net71, ckob
    box(V, 'xi0', 260, 140, 90, 70, 'NAND2', 'xi0',
        left=[('ck', 160, [[('xi0', 'a')]], 'clock'), ('en', 190, [[('xi0', 'b')]], 'data')],
        right=[('net70', 175, [[('xi0', 'y')]], 'clock')],
        bubbles=('net70',), link='u_nand', members=['xi0'])

    box(V, 'xi1', 260, 310, 90, 70, 'NAND2', 'xi1',
        left=[('ckb', 330, [[('xi1', 'a')]], 'clock'), ('en', 360, [[('xi1', 'b')]], 'data')],
        right=[('net71', 345, [[('xi1', 'y')]], 'clock')],
        bubbles=('net71',), link='u_nand', members=['xi1'])

    inv(V, 'xi2', 450, 175, 'xi2 (inv_c)', [[('xi2', 'a')]], [[('xi2', 'y')]], link='u_inv', members=['xi2'], cls='clock')
    inv(V, 'xi3', 450, 345, 'xi3 (inv_c)', [[('xi3', 'a')]], [[('xi3', 'y')]], link='u_inv', members=['xi3'], cls='clock')

    # Ports
    V.port('ck', 80, 160, d='right', io='in', cls='clock'); V.wire([(80, 160), (240, 160)], cls='clock')
    V.port('ckb', 80, 330, d='right', io='in', cls='clock'); V.wire([(80, 330), (240, 330)], cls='clock')
    V.port('en', 80, 250, d='right', io='in'); V.wire([(80, 250), (180, 250)], cls='data')
    V.wire([(180, 250), (180, 190), (240, 190)], cls='data'); V.dot(180, 250)
    V.wire([(180, 250), (180, 360), (240, 360)], cls='data')

    V.wire([(370, 175), (430, 175)], cls='clock'); V.netlabel('net70', 390, 165)
    V.wire([(370, 345), (430, 345)], cls='clock'); V.netlabel('net71', 390, 335)

    V.wire([(512, 175), (660, 175)], cls='clock'); V.port('cko', 660, 175, d='right', io='out', cls='clock')
    V.wire([(512, 345), (660, 345)], cls='clock'); V.port('ckob', 660, 345, d='right', io='out', cls='clock')

    finalize_omitted(V)
    return V


# =====================================================================================
# 8. VIEW_ODT_DEC: u_odt_dec
# =====================================================================================
def view_odt_dec():
    cell = 'odt_dec'
    V = new_view('u_odt_dec', cell, 'unit', 'ODT_DEC — unit level (ODT 디코더)', 920, 560)
    # xi0..xi2 (nand2_a): odt_en, rtt<i> -> net2<i>
    # xi3..xi5 (ls_lh): net2<i> -> enb<i>
    y_lanes = [140, 270, 400]
    for k, idx in enumerate(['2', '1', '0']):
        y = y_lanes[k]
        box(V, 'xi%d' % (2 - k), 260, y - 35, 90, 70, 'NAND2', 'xi%d' % (2 - k),
            left=[('odt_en', y - 15, [[('xi%d' % (2 - k), 'a')]], 'data'), ('rtt<%s>' % idx, y + 15, [[('xi%d' % (2 - k), 'b')]], 'data')],
            right=[('net2%s' % idx, y, [[('xi%d' % (2 - k), 'y')]], 'data')],
            bubbles=('net2%s' % idx,), link='u_nand', members=['xi%d' % (2 - k)])

        box(V, 'xi%d' % (5 - k), 480, y - 35, 90, 70, 'LS', 'xi%d (ls_lh)' % (5 - k),
            left=[('in', y, [[('xi%d' % (5 - k), 'in')]], 'data')],
            right=[('out', y, [[('xi%d' % (5 - k), 'out')]], 'data')],
            link='u_ls', members=['xi%d' % (5 - k)])

        V.port('rtt<%s>' % idx, 80, y + 15, d='right', io='in')
        V.wire([(80, y + 15), (240, y + 15)], cls='data')

        V.wire([(370, y), (460, y)], cls='data')
        V.netlabel('net2%s' % idx, 400, y - 8)

        V.wire([(590, y), (700, y)], cls='data')
        V.port('enb<%s>' % idx, 700, y, d='right', io='out')

    # Common odt_en port
    V.port('odt_en', 80, 80, d='right', io='in')
    V.wire([(80, 80), (160, 80), (160, y_lanes[2] - 15)], cls='data')
    for y in y_lanes:
        V.wire([(160, y - 15), (240, y - 15)], cls='data'); V.dot(160, y - 15)

    finalize_omitted(V)
    return V


# =====================================================================================
# 9. VIEW_LS: u_ls (ls_lh)
# =====================================================================================
def view_ls():
    cell = 'ls_lh'
    V = new_view('u_ls', cell, 'unit', 'LS_LH — unit level (Level Shifter, 대칭)', 900, 640)
    rail(V, 80, 820, 70, 'vddq', 'VDDQ')
    rail(V, 80, 820, 570, 'vss', 'VSS')
    AX = 450

    V.port('in', 80, 300, d='right', io='in')
    V.port('out', 820, 300, d='right', io='out')

    finalize_omitted(V)
    return V


# =====================================================================================
# 10. VIEW_NOR: u_nor (nor2_c)
# =====================================================================================
def view_nor():
    cell = 'nor2_c'
    V = new_view('u_nor', cell, 'unit', 'NOR2_C — unit level (CMOS NOR 게이트)', 720, 580)
    rail(V, 80, 640, 70, 'vdd', 'VDD')
    rail(V, 80, 640, 510, 'vss', 'VSS')
    V.port('a', 80, 200, d='right', io='in')
    V.port('b', 80, 320, d='right', io='in')
    V.port('y', 640, 260, d='right', io='out')

    finalize_omitted(V)
    return V


# =====================================================================================
# 11. VIEW_NAND: u_nand (nand2_a / nand2_c)
# =====================================================================================
def view_nand():
    cell = 'nand2_a'
    V = new_view('u_nand', cell, 'unit', 'NAND2 — unit level (CMOS NAND 게이트)', 720, 580)
    rail(V, 80, 640, 70, 'vdd', 'VDD')
    rail(V, 80, 640, 510, 'vss', 'VSS')
    V.port('a', 80, 200, d='right', io='in')
    V.port('b', 80, 320, d='right', io='in')
    V.port('y', 640, 260, d='right', io='out')

    finalize_omitted(V)
    return V


# =====================================================================================
# 12. VIEW_INV: u_inv (inv_a / inv_c)
# =====================================================================================
def view_inv():
    cell = 'inv_a'
    V = new_view('u_inv', cell, 'unit', 'INV — unit level (CMOS 인버터)', 640, 520)
    rail(V, 80, 560, 70, 'vdd', 'VDD')
    rail(V, 80, 560, 450, 'vss', 'VSS')
    V.port('a', 80, 260, d='right', io='in')
    V.port('y', 560, 260, d='right', io='out')

    finalize_omitted(V)
    return V


# Build all views
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

# Save scenes.json
def scene_to_dict(V):
    return {
        'id': V.id, 'cell': V.cell, 'level': V.level, 'title': V.title,
        'w': V.w, 'h': V.h,
        'draw': V.draw, 'symbols': V.symbols, 'wires': V.wires, 'dots': V.dots,
        'labels': V.labels, 'texts': V.texts, 'hot': V.hot,
        'symmetry': V.symmetry, 'allowed_cross': V.allowed_cross,
        'notes': V.notes, 'omitted': V.omitted, 'scope': V.scope,
        'extra_checks': V.extra_checks
    }

json.dump([scene_to_dict(v) for v in VIEWS], open(W + '/scenes.json', 'w'), indent=1)
print("Views created: %d views" % len(VIEWS))
print([v.id for v in VIEWS])
