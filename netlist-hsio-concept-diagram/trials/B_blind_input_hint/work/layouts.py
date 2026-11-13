"""Step 3 (plan sections 4, 5): concept-diagram views. Writes scenes.json
Every template takes element names from the structural analysis (roles), not from the netlist text."""
import json, sys, collections, re
from netlist import parse, num
from scene import *

W = sys.argv[1]
NL = sys.argv[2]
cells, order = parse(NL)
A = json.load(open(W + '/analysis.json'))
ROLES = A['roles']; CN = A['cellnet']; EFF = A['eff']; INST = A['cell_insts']
VIEWS = []


def el(cell, name):
    for e in cells[cell]['elems']:
        if e['name'] == name:
            return e
    raise KeyError(cell + ':' + name)


def role(cell, name):
    return ROLES[cell][name]['role']


def T(dev, t):
    return [[(dev, t)]]


def TM(devs, t):
    return [[(d, t)] for d in devs]


def topbot(cell, dev):
    """terminal letters (top, bottom) for drawing: NMOS top = structural drain, PMOS top = structural source"""
    e = el(cell, dev)
    pre = INST[cell][0]
    s, d = EFF[pre + dev]
    gs = lambda n: n if n in ('VDD', 'VSS') else None
    # map global back to terminal letter
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
    """top/bottom/gate per-slice terms for one or merged devices"""
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
    Ws = [e['params'].get('w', '?') for e in es]
    Ls = sorted({e['params'].get('l', '?') for e in es}, key=lambda x: num(x) or 0)
    ms = [e['params'].get('m') for e in es]
    if len(es) == 1:
        s = '%s/%s' % (Ws[0], Ls[0])
        if ms[0] and ms[0] != '1':
            s += ' ×%s' % ms[0]
        return s
    return ['W ' + ','.join(Ws), 'L ' + '/'.join(Ls)]


def cls_of(cell, net):
    c = CN[cell].get(net, [])
    if 'data' in c:
        return 'data'
    if 'clock' in c:
        return 'clock'
    if 'important_control' in c:
        return 'bus'
    return 'plain'


def hidden_list(cell, shown=None):
    """omitted (hidden) nets of the cell by class"""
    out = []
    for n, c in sorted(CN[cell].items()):
        k = [x for x in c if x in ('general_control', 'bias', 'power')]
        if k and not any(x in c for x in ('data', 'clock', 'important_control')):
            out.append({'net': n, 'class': '/'.join(k)})
    return out


def gnd_at(V, x, y, net='VSS', l=12):
    V.wire([(x, y), (x, y + l)], cls='power')
    gnd(V, x, y + l, net)


def busslash(V, x, y, n, vertical=True):
    if vertical:
        V.line([(x - 7, y + 7), (x + 7, y - 7)], w=1.4, owner='bus')
        V.text(x + 9, y + 4, str(n), size=10, anchor='start', cls='buswidth')
    else:
        V.line([(x - 7, y + 7), (x + 7, y - 7)], w=1.4, owner='bus')
        V.text(x, y + 16, str(n), size=10, anchor='middle', cls='buswidth')


def legend(V, x, y, lines, title='묶음·병합 (bundles / merged)'):
    V.text(x, y, title, size=11, anchor='start', weight='bold', cls='legend')
    for i, ln in enumerate(lines):
        V.text(x, y + 16 + 14 * i, ln, size=10, anchor='start', color='#444', cls='size')


def stub_label(V, p, name, d, cls='data', L=24, side=None):
    """short wire from pin p in direction d with a net label at its end"""
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


def port_is_output(cell, port, depth=0):
    """structural port direction: output if, inside the cell, the net reaches a MOS channel (drain/source)
    directly or through a sub-instance output port"""
    c = cells[cell]
    for e in c['elems']:
        if e['kind'] == 'mos':
            if port in (e['terms']['d'], e['terms']['s']) and e['terms']['g'] not in ('VDD', 'VSS'):
                return True
        elif e['kind'] == 'inst':
            for p, n in e['pins'].items():
                if n == port and depth < 8 and port_is_output(e['cell'], p, depth + 1):
                    return True
    return False


def new_view(*a, **k):
    V = View(*a, **k)
    VIEWS.append(V)
    return V


# =====================================================================================
# U: CTLE (single-axis textbook template, plan 5.4)
# =====================================================================================
def view_ctle(cell):
    r = ROLES[cell]
    ins = [m for m in r if r[m]['role'] == 'input']
    # P side = input whose gate is the first input port
    ports = cells[cell]['ports']
    ins.sort(key=lambda m: ports.index(el(cell, m)['terms']['g']))
    mP, mN = ins
    sP = el(cell, mP)['terms'][topbot(cell, mP)[1]]; sN = el(cell, mN)['terms'][topbot(cell, mN)[1]]
    oP = el(cell, mP)['terms'][topbot(cell, mP)[0]]; oN = el(cell, mN)['terms'][topbot(cell, mN)[0]]
    loads = {oP: [], oN: []}; tails = {}
    deg_r, deg_c, gate_r = [], [], {}
    for m, v in r.items():
        e = el(cell, m)
        if e['kind'] == 'mos' and v['role'] in ('load', 'tail', 'active_inductor') and m not in ins:
            ts = set(e['terms'].values())
            for o in (oP, oN):
                if o in ts:
                    loads[o].append(m)
            for s_ in (sP, sN):
                if s_ in ts and v['role'] == 'tail':
                    tails[s_] = m
        if v['role'] == 'switch' or (e['kind'] in ('res',) and {sP, sN} <= set(e['terms'].values())):
            deg_r.append(m)
        if e['kind'] == 'cap' and {sP, sN} <= set(e['terms'].values()):
            deg_c.append(m)
        if v['role'] == 'gate_r':
            gate_r[[n for n in e['terms'].values() if n not in ('VDD', 'VSS')][0]] = m
    def ai(o):
        return [m for m in loads[o] if r[m]['role'] == 'active_inductor'][0]
    def pl(o):
        return [m for m in loads[o] if r[m]['role'] != 'active_inductor'][0]
    V = new_view('u_ctle', cell, 'unit', '%s — unit level (CTLE, 대칭)' % cell, 900, 680)
    AX = 440
    rail(V, 160, 720, 70, 'VDD')
    for side, o, s_, inp in ((-1, oP, sP, mP), (1, oN, sN, mN)):
        g = 'left' if side < 0 else 'right'
        cL = AX + side * 80        # input / pmos load column
        cA = AX + side * 200       # active inductor column
        xR = AX + side * 260       # gate resistor x
        A_ = ai(o); P_ = pl(o); Rg = gate_r[el(cell, A_)['terms']['g']]
        # gate resistor from VDD to the active-inductor gate
        rr = res(V, 'R_' + Rg, xR, 110, 'v', name=Rg, size=el(cell, Rg)['value'], a=T(Rg, 'p' if el(cell, Rg)['terms']['p'] == 'VDD' else 'n'),
                 b=T(Rg, 'n' if el(cell, Rg)['terms']['p'] == 'VDD' else 'p'), label_side='left' if side < 0 else 'right', members=[Rg])
        V.wire([(xR, 70), (xR, 80)], cls='power'); V.dot(xR, 70)
        tA, bA, gA = mosT(cell, A_)
        ma = mos(V, A_, cA, 160, 'n', gate=g, name=A_, size=wl(cell, A_), top=tA, bot=bA, gterm=gA, members=[A_], arrow_at='bottom')
        V.wire([(xR, 140), (xR, 160), (ma['pins'][2]['x'], 160)], cls='plain')
        V.wire([(cA, 130), (cA, 70)], cls='power'); V.dot(cA, 70)
        tP, bP, gP = mosT(cell, P_)
        mp = mos(V, P_, cL, 160, 'p', gate=g, name=P_, size=wl(cell, P_), top=tP, bot=bP, gterm=gP, members=[P_])
        gray_gate(V, mp['pins'][2], el(cell, P_)['terms']['g'], g)
        V.wire([(cL, 130), (cL, 70)], cls='power'); V.dot(cL, 70)
        tI, bI, gI = mosT(cell, inp)
        mi = mos(V, inp, cL, 290, 'n', gate=g, name=inp, size=wl(cell, inp), top=tI, bot=bI, gterm=gI, members=[inp])
        V.wire([(cL, 190), (cL, 260)], cls='data')          # output node column
        xo = AX + side * 330
        V.wire([(xo, 220), (cL, 220)], cls='data'); V.dot(cL, 220)
        V.wire([(cA, 190), (cA, 220)], cls='data'); V.dot(cA, 220)
        V.port(o, xo, 220, d='left' if side < 0 else 'right', io='out')
        gx = mi['pins'][2]['x']
        V.wire([(gx, 290), (gx + side * 120, 290)], cls='data')
        V.port(el(cell, inp)['terms']['g'], gx + side * 120, 290, d='right' if side < 0 else 'left', io='in')
        # source column and tail
        tl = tails[s_]
        tT, bT, gT = mosT(cell, tl)
        mt = mos(V, tl, cL, 480, 'n', gate=g, name=tl, size=wl(cell, tl), top=tT, bot=bT, gterm=gT, members=[tl])
        gray_gate(V, mt['pins'][2], el(cell, tl)['terms']['g'], g)
        V.wire([(cL, 320), (cL, 450)], cls='plain')
        V.wire([(cL, 360), (AX + side * 30, 360)], cls='plain'); V.dot(cL, 360)
        V.wire([(cL, 420), (AX + side * 30, 420)], cls='plain'); V.dot(cL, 420)
        gnd_at(V, cL, 510)
    # degeneration: variable R (fixed R || switch banks) and fixed C (merged)
    ra = [];
    rb = []
    for m in deg_r:
        e = el(cell, m)
        if e['kind'] == 'res':
            ra.append((m, 'p' if e['terms']['p'] == sP else 'n')); rb.append((m, 'n' if e['terms']['p'] == sP else 'p'))
        else:
            if sP in (e['terms']['d'], e['terms']['s']):
                ra.append((m, 'd' if e['terms']['d'] == sP else 's'))
            if sN in (e['terms']['d'], e['terms']['s']):
                rb.append((m, 'd' if e['terms']['d'] == sN else 's'))
    res(V, 'R_S', AX, 360, 'h', name='R_S (가변)', a=[ra], b=[rb], var=True, members=deg_r, label_side='above')
    ca = [(m, 'p' if el(cell, m)['terms']['p'] == sP else 'n') for m in deg_c]
    cb = [(m, 'n' if el(cell, m)['terms']['p'] == sP else 'p') for m in deg_c]
    cap(V, 'C_S', AX, 420, 'h', name='C_S', a=[ca], b=[cb], members=deg_c, label_side='below')
    # legend
    rfix = [m for m in deg_r if el(cell, m)['kind'] == 'res']
    rsw = [m for m in deg_r if el(cell, m)['kind'] == 'mos']
    single = [m for m in rsw if not re.search(r'C\d', el(cell, m)['terms']['g'])]
    lines = ['R_S (가변 R) = %s %sΩ ∥ 스위치 MOS 묶음 %s' % (', '.join(rfix), ', '.join(el(cell, m)['value'] for m in rfix),
                                                    ', '.join('%s(%s)' % (m, wl(cell, m)) for m in rsw[:3])),
             '      ∥ 직렬 스위치 쌍 %s' % ', '.join('%s(%s)' % (m, wl(cell, m)) for m in rsw[3:]),
             'C_S (고정 C) = %s = %s (스위치와 직렬 아님 → 고정, Q1)' % (' ∥ '.join(deg_c), ' + '.join(el(cell, m)['value'] for m in deg_c))]
    V.notes.append('R_S 스위치 게이트 %s: 일반 제어 → 그리지 않음 (가변 화살표가 "조절 가능"을 뜻함)' % ', '.join(sorted({el(cell, m)['terms']['g'] for m in rsw})))
    legend(V, 60, 585, lines)
    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [[ai(oP), ai(oN)], [pl(oP), pl(oN)], [mP, mN], [tails[sP], tails[sN]],
                                                              ['R_' + gate_r[el(cell, ai(oP))['terms']['g']], 'R_' + gate_r[el(cell, ai(oN))['terms']['g']]]],
                       'self': ['R_S', 'C_S'], 'x0': 100, 'x1': 780, 'exempt_wires': []})
    V.omitted = hidden_list(cell)
    return V


# =====================================================================================
# U: multi-pair (VGA / summer): pair-wise symmetry side by side (plan 5.2-2, figure B)
# =====================================================================================
def view_multipair(cell, vid, kind):
    r = ROLES[cell]
    pre = INST[cell][0]
    ins = [m for m in r if r[m]['role'] == 'input']
    bysrc = collections.defaultdict(list)
    for m in ins:
        bysrc[EFF[pre + m][0]].append(m)
    pairs = list(bysrc.values())
    ports = cells[cell]['ports']
    def pkey(p):
        return min(A['data_trace'].get(A['l2g'][pre].get(el(cell, m)['terms']['g'], ''), {}).get('depth', 99) for m in p)
    for p in pairs:
        p.sort(key=lambda m: ports.index(el(cell, m)['terms']['g']) if el(cell, m)['terms']['g'] in ports else 0)
    pairs.sort(key=pkey)
    main, extra = pairs[0], pairs[1:]
    # P/N orientation of extra pairs: P device = the one whose drain equals main P drain
    oP = el(cell, main[0])['terms'][topbot(cell, main[0])[0]]
    oN = el(cell, main[1])['terms'][topbot(cell, main[1])[0]]
    exP = [p[0] if el(cell, p[0])['terms'][topbot(cell, p[0])[0]] == oP else p[1] for p in extra]
    exN = [p[1] if el(cell, p[0])['terms'][topbot(cell, p[0])[0]] == oP else p[0] for p in extra]
    # loads and tails
    loadP = [m for m in r if r[m]['role'] == 'load' and oP in el(cell, m)['terms'].values()][0]
    loadN = [m for m in r if r[m]['role'] == 'load' and oN in el(cell, m)['terms'].values()][0]
    tsrc = EFF[pre + main[0]][0]
    loc = {v: k for k, v in A['l2g'][pre].items()}
    tnode = loc.get(tsrc, tsrc)
    mtail = [m for m in r if r[m]['role'] == 'tail' and el(cell, m)['terms']['d'] == tnode or (r[m]['role'] == 'tail' and el(cell, m)['terms']['s'] == tnode)][0]
    exsrc = [loc.get(EFF[pre + p][0], EFF[pre + p][0]) for p in exP]
    # tail bundles of extra pairs: switched current sources (switch+cs) or DAC instances
    bundles = []
    for sn in exsrc:
        mem = []
        for e in cells[cell]['elems']:
            if e['kind'] == 'inst' and sn in e['pins'].values():
                mem.append(e['name'])
            elif e['kind'] == 'mos' and r.get(e['name'], {}).get('role') == 'switch' and sn in (e['terms']['d'], e['terms']['s']):
                mem.append(e['name'])
                o = e['terms']['s'] if e['terms']['d'] == sn else e['terms']['d']
                for f in cells[cell]['elems']:
                    if f['kind'] == 'mos' and f is not e and o in (f['terms']['d'], f['terms']['s']):
                        mem.append(f['name'])
        bundles.append(mem)
    n = len(extra)
    V = new_view(vid, cell, 'unit', '%s — unit level (%s, 쌍별 대칭 나란히: 그림 B)' % (cell, 'VGA' if kind == 'vga' else 'DFE summer Σ'), 1000 if kind == 'vga' else 1120, 660)
    A1, A2 = 330, 700 if kind == 'vga' else 800
    xPm, xNm = A1 - 70, A1 + 70
    xPe, xNe = A2 - 100, A2 + 100
    yL, yN, yP, yM = 140, 200, 230, 300
    rail(V, 200, 930 if kind == 'vga' else 1000, 70, 'VDD')
    tl, bl, gl = mosT(cell, loadP)
    m1 = mos(V, loadP, xPm, yL, 'p', 'left', loadP, wl(cell, loadP), tl, bl, gl, members=[loadP])
    gray_gate(V, m1['pins'][2], el(cell, loadP)['terms']['g'], 'left')
    tl, bl, gl = mosT(cell, loadN)
    m2 = mos(V, loadN, xNm, yL, 'p', 'right', loadN, wl(cell, loadN), tl, bl, gl, members=[loadN])
    gray_gate(V, m2['pins'][2], el(cell, loadN)['terms']['g'], 'right')
    for x in (xPm, xNm):
        V.wire([(x, yL - 30), (x, 70)], cls='power'); V.dot(x, 70)
    for side, dev, x in ((-1, main[0], xPm), (1, main[1], xNm)):
        t_, b_, g_ = mosT(cell, dev)
        mm = mos(V, dev, x, yM, 'n', 'left' if side < 0 else 'right', dev, wl(cell, dev), t_, b_, g_, members=[dev])
        V.wire([(x, yL + 30), (x, yM - 30)], cls='data')
        gx = mm['pins'][2]['x']
        V.wire([(gx, yM), (gx + side * 40, yM)], cls='data')
        V.port(el(cell, dev)['terms']['g'], gx + side * 40, yM, d='right' if side < 0 else 'left', io='in')
    # output buses: N upper, P lower; P bus crosses the N column (1 structural crossing per pair)
    V.dot(xPm, yP); V.dot(xNm, yN)
    V.wire([(xPm, yP), (xPe, yP), (xPe, yM - 30)], cls='data')
    V.wire([(xNm, yN), (xNe, yN), (xNe, yM - 30)], cls='data')
    xo = 930 if kind == 'vga' else 1000
    V.wire([(xPe, yP), (xo, yP)], cls='data'); V.dot(xPe, yP)
    V.wire([(xNe, yN), (xo, yN)], cls='data'); V.dot(xNe, yN)
    V.port(oN, xo, yN, d='right', io='out')
    V.port(oP, xo, yP, d='right', io='out')
    V.allowed_cross.append({'at': [xNm, yP], 'reason': 'figure B: P output bus crosses the main pair N drain column'})
    V.allowed_cross.append({'at': [xNe, yP], 'reason': 'figure B: P output exit crosses the extra pair N drain column'})
    # merged extra pair
    gnet = lambda devs: el(cell, devs[0])['terms']['g']
    def busname(devs):
        gs = [el(cell, d)['terms']['g'] for d in devs]
        if len(set(gs)) == 1:
            return gs[0]
        m = [re.match(r'^(\D*)(\d+)(\D*)$', g) for g in gs]
        idx = [int(x.group(2)) for x in m]
        return '%s<%d:%d>%s' % (m[0].group(1), min(idx), max(idx), m[0].group(3))
    def mname(devs):
        m = [re.match(r'^(.*?)(\d+)(.*)$', d) for d in devs]
        idx = [int(x.group(2)) for x in m]
        return '%s<%d:%d>%s' % (m[0].group(1), min(idx), max(idx), m[0].group(3))
    for side, devs, x in ((-1, exP, xPe), (1, exN, xNe)):
        t_, b_, g_ = mosT(cell, devs)
        mm = mos(V, 'merged_' + devs[0], x, yM, 'n', 'left' if side < 0 else 'right', mname(devs), wl(cell, devs), t_, b_, g_,
                 members=devs, extra_info={'merged': True})
        gp = mm['pins'][2]
        bn = busname(devs)
        if bn in ports and kind == 'vga':
            stub_label(V, gp, bn, 'left' if side < 0 else 'right', cls='data', L=24)
        else:
            V.wire([(gp['x'], yM), (gp['x'] + side * 24, yM)], cls='data')
            V.port(bn, gp['x'] + side * 24, yM, d='right' if side < 0 else 'left', io='in')
    # tails
    V.wire([(xPm, yM + 30), (xPm, yM + 50), (xNm, yM + 50), (xNm, yM + 30)], cls='plain')
    V.dot(A1, yM + 50)
    V.wire([(A1, yM + 50), (A1, yM + 80)], cls='plain')
    t_, b_, g_ = mosT(cell, mtail)
    mt = mos(V, mtail, A1, yM + 110, 'n', 'left', mtail, wl(cell, mtail), t_, b_, g_, members=[mtail])
    gray_gate(V, mt['pins'][2], el(cell, mtail)['terms']['g'], 'left')
    gnd_at(V, A1, yM + 140)
    V.wire([(xPe, yM + 30), (xPe, yM + 50), (xNe, yM + 50), (xNe, yM + 30)], cls='plain')
    V.dot(A2, yM + 50)
    V.wire([(A2, yM + 50), (A2, yM + 80)], cls='plain')
    # bundle terminals
    topT, botT, busT = [], [], []
    for sn, mem in zip(exsrc, bundles):
        tt, bb, cc = [], [], []
        for m in mem:
            e = el(cell, m)
            if e['kind'] == 'inst':
                for p, nn in e['pins'].items():
                    if nn == sn: tt.append((m, p))
                    elif nn == 'VSS': bb.append((m, p))
                    elif 'important_control' in CN[cell].get(nn, []): cc.append((m, p))
            else:
                for t, nn in e['terms'].items():
                    if t == 'b': continue
                    if nn == sn: tt.append((m, t))
                    elif nn == 'VSS': bb.append((m, t))
        topT.append(tt); botT.append(bb)
        if cc: busT.extend(cc)
    allmem = [m for b in bundles for m in b]
    isdac = any(el(cell, m)['kind'] == 'inst' for m in allmem)
    if isdac:
        dac_cell = el(cell, allmem[0])['cell']
        ctrl = sorted({p for m in allmem for p, nn in el(cell, m)['pins'].items() if 'important_control' in CN[cell].get(nn, [])})
        busnets = [nn for m in allmem for p, nn in el(cell, m)['pins'].items() if 'important_control' in CN[cell].get(nn, [])]
        bn = 'W<1:4>_<0:3>'
        g = re.match(r'^(\D+)(\d+)_(\d+)$', busnets[0])
        ii = sorted({int(re.match(r'^\D+(\d+)_', x).group(1)) for x in busnets}); jj = sorted({int(re.match(r'^\D+\d+_(\d+)$', x).group(1)) for x in busnets})
        bn = '%s<%d:%d>_<%d:%d>' % (g.group(1), ii[0], ii[-1], jj[0], jj[-1])
        vs = visrc(V, 'ISRC', A2, yM + 110, name=mname(allmem), size='', top=[sum(topT, [])] if False else topT, bot=botT,
                   bus=[[(m, p)] for m in allmem for p, nn in el(cell, m)['pins'].items() if 'important_control' in CN[cell].get(nn, [])],
                   bus_side='right', members=allmem, label_side='left')
        vs['info']['bus_order'] = busnets
        bx = A2 + 40
        V.wire([(bx, yM + 110), (A2 + 170, yM + 110)], cls='bus')
        busslash(V, A2 + 110, yM + 110, len(busnets), vertical=False)
        V.port(bn, A2 + 170, yM + 110, d='left', io='in', cls='bus')
        dsub = cells[dac_cell]
        dr = ROLES[dac_cell]
        sw = [m for m in dr if dr[m]['role'] == 'switch']; cs = [m for m in dr if dr[m]['role'] != 'switch']
        lines = ['%s 탭 쌍 %d개 병합 (게이트 %s / %s), W/L 나열' % (mname(exP), n, busname(exP), busname(exN)),
                 '가변 전류원 = %s (%s ×%d, 전류 DAC): 스위치 %s %s, 전류원 %s %s' % (mname(allmem), dac_cell, len(allmem), '/'.join(sw), wl(dac_cell, sw)[0] if isinstance(wl(dac_cell, sw), list) else wl(dac_cell, sw),
                                                                                    '/'.join(cs), ' '.join(wl(dac_cell, cs)) if isinstance(wl(dac_cell, cs), list) else wl(dac_cell, cs)),
                 '중요 제어 %s (%db, DFE 탭 계수) = 가변 전류원으로 들어가는 버스' % (bn, len(busnets))]
        V.notes.append('DAC 바이어스 입력 %s 는 그리지 않음 (바이어스)' % ', '.join(sorted({nn for m in allmem for p, nn in el(cell, m)['pins'].items() if 'bias' in CN[cell].get(nn, [])})))
    else:
        sws = [m for m in allmem if r[m]['role'] == 'switch']
        css = [m for m in allmem if r[m]['role'] != 'switch']
        vs = visrc(V, 'ISRC', A2, yM + 110, name=mname(css).replace('MB', 'I'), size='', top=topT, bot=botT, members=allmem, label_side='left')
        lines = ['%s 이득 쌍 %d개 병합 (게이트 = 주 쌍과 같은 %s/%s)' % (mname(exP), n, busname(exP), busname(exN)),
                 '가변 전류원 = 스위치 %s (%s) + 전류원 %s (%s)' % (mname(sws), ', '.join(wl(cell, sws)), mname(css), ', '.join(wl(cell, css)))]
        V.notes.append('이득 스위치 게이트 %s: 일반 제어(이득) → 그리지 않음 (가변 화살표로 표시); 전류원 게이트 %s: 바이어스' % (
            ', '.join(el(cell, m)['terms']['g'] for m in sws), ', '.join(sorted({el(cell, m)['terms']['g'] for m in css}))))
    gnd_at(V, A2, yM + 140)
    legend(V, 60, 520, lines)
    V.symmetry.append({'axis': A1, 'orient': 'v', 'pairs': [[loadP, loadN], [main[0], main[1]]], 'self': [mtail], 'x0': 150, 'x1': A1 + (A1 - 150),
                       'exempt_wires': ['figure B output buses']})
    V.symmetry.append({'axis': A2, 'orient': 'v', 'pairs': [['merged_' + exP[0], 'merged_' + exN[0]]], 'self': ['ISRC'], 'x0': A2 - 150, 'x1': A2 + 150,
                       'exempt_wires': ['figure B output buses', 'coefficient bus'], 'ymin': yM - 30})
    V.symmetry[0]['ymin'] = yM - 30
    V.omitted = hidden_list(cell)
    return V


# =====================================================================================
# U: StrongARM core (plan 5.4 template)
# =====================================================================================
def view_strongarm(cell, members):
    r = ROLES[cell]
    pre = INST[cell][0]
    E = lambda m: el(cell, m)
    tail = [m for m in members if r[m]['role'] == 'clocked_tail'][0]
    ins = [m for m in members if r[m]['role'] == 'input' and E(m)['type'] == 'n']
    ports = cells[cell]['ports']
    ins.sort(key=lambda m: ports.index(E(m)['terms']['g']))
    iP, iN = ins
    dP = E(iP)['terms']['d'] if E(iP)['terms']['s'] == E(tail)['terms']['d'] else E(iP)['terms']['s']
    dN = E(iN)['terms']['d'] if E(iN)['terms']['s'] == E(tail)['terms']['d'] else E(iN)['terms']['s']
    crossN = [m for m in members if r[m]['role'] == 'cross' and E(m)['type'] == 'n']
    crossP = [m for m in members if r[m]['role'] == 'cross' and E(m)['type'] == 'p']
    cnP = [m for m in crossN if dP in (E(m)['terms']['s'], E(m)['terms']['d'])][0]
    cnN = [m for m in crossN if m != cnP][0]
    oP = E(cnP)['terms']['d'] if E(cnP)['terms']['s'] == dP else E(cnP)['terms']['s']
    oN = E(cnN)['terms']['d'] if E(cnN)['terms']['s'] == dN else E(cnN)['terms']['s']
    cpP = [m for m in crossP if oP in (E(m)['terms']['d'],)][0]
    cpN = [m for m in crossP if m != cpP][0]
    resets = [m for m in members if r[m]['role'] == 'reset']
    rsO = {o: [m for m in resets if o in (E(m)['terms']['d'], E(m)['terms']['s'])][0] for o in (oP, oN)}
    rsD = {o: [m for m in resets if o in (E(m)['terms']['d'], E(m)['terms']['s'])][0] for o in (dP, dN)}
    odd = [m for m in members if m not in [tail, iP, iN, cnP, cnN, cpP, cpN] + resets]
    clk = E(tail)['terms']['g']
    V = new_view('u_strongarm', cell, 'unit', '%s — unit level (StrongARM core, 대칭)' % cell, 820, 700,
                 scope=members)
    AX = 410; L, R = 330, 490
    rail(V, 180, 640, 60, 'VDD')
    for side, cp, cn, inp, o, d in ((-1, cpP, cnP, iP, oP, dP), (1, cpN, cnN, iN, oN, dN)):
        x = L if side < 0 else R
        gi = 'right' if side < 0 else 'left'      # inner gates for cross-coupled
        go = 'left' if side < 0 else 'right'
        t_, b_, g_ = mosT(cell, cp)
        mcp = mos(V, cp, x, 130, 'p', gi, cp, wl(cell, cp), t_, b_, g_, members=[cp])
        V.wire([(x, 100), (x, 60)], cls='power'); V.dot(x, 60)
        t_, b_, g_ = mosT(cell, cn)
        mcn = mos(V, cn, x, 260, 'n', gi, cn, wl(cell, cn), t_, b_, g_, members=[cn])
        tx = x - side * 40
        V.wire([(tx, 130), (tx, 260)], cls='data')        # gate tie of the inverter
        V.wire([(x, 160), (x, 230)], cls='data')          # output node column
        t_, b_, g_ = mosT(cell, inp)
        mi = mos(V, inp, x, 430, 'n', go, inp, wl(cell, inp), t_, b_, g_, members=[inp])
        V.wire([(x, 290), (x, 400)], cls='data')          # DP / DN column
        gx = mi['pins'][2]['x']
        V.wire([(gx, 430), (gx + side * 40, 430)], cls='data')
        V.port(E(inp)['terms']['g'], gx + side * 40, 430, d='right' if side < 0 else 'left', io='in')
        # reset of output node (from rail)
        xr = x + side * 100
        m = rsO[o]
        t_, b_, g_ = mosT(cell, m)
        mr = mos(V, m, xr, 130, 'p', go, m, wl(cell, m), t_, b_, g_, members=[m])
        V.wire([(xr, 100), (xr, 60)], cls='power'); V.dot(xr, 60)
        stub_label(V, mr['pins'][2], clk, 'left' if side < 0 else 'right', cls='clock', L=24)
        xe = x + side * 190
        V.wire([(xe, 180), (x, 180)], cls='data'); V.dot(x, 180)
        V.wire([(xr, 160), (xr, 180)], cls='data'); V.dot(xr, 180)
        V.netlabel(o, xe, 180, tx=xe + (2 if side < 0 else -2), ty=172, anchor='start' if side < 0 else 'end')
        # reset of DP/DN (local VDD)
        m = rsD[d]
        t_, b_, g_ = mosT(cell, m)
        md = mos(V, m, xr, 310, 'p', go, m, wl(cell, m), t_, b_, g_, members=[m])
        vdd_tee(V, xr, 280, 'VDD')
        stub_label(V, md['pins'][2], clk, 'left' if side < 0 else 'right', cls='clock', L=24)
        V.wire([(xr, 340), (xr, 360), (x, 360)], cls='data'); V.dot(x, 360)
    # cross-coupling X (diagonals)
    V.wire([(L, 205), (R - 40, 250)], cls='data'); V.dot(L, 205); V.dot(R - 40, 250)
    V.wire([(R, 205), (L + 40, 250)], cls='data'); V.dot(R, 205); V.dot(L + 40, 250)
    for at, why in (([AX, 227.5], 'cross-coupled X'), ([L + 40, 220], 'cross-coupled: node wire crosses inverter gate tie'),
                    ([R - 40, 220], 'cross-coupled: node wire crosses inverter gate tie')):
        V.allowed_cross.append({'at': at, 'reason': why})
    # odd (asymmetric) devices, e.g. PMOS VDD->DP with gate DN
    exempt = []
    for m in odd:
        e = E(m)
        t_, b_, g_ = mosT(cell, m)
        gside = 'right' if e['terms']['g'] == dN else 'left'
        mo = mos(V, m, AX, 330, e['type'], gside, m, wl(cell, m), t_, b_, g_, members=[m], extra_info={'asymmetric': True})
        vdd_tee(V, AX, 300, 'VDD')
        gp = mo['pins'][2]
        tgt = R if e['terms']['g'] == dN else L
        V.wire([(gp['x'], 330), (tgt, 330)], cls='data'); V.dot(tgt, 330)
        dn_ = e['terms']['d']
        tgt2 = L if dn_ == dP else R
        V.wire([(AX, 360), (AX, 390), (tgt2, 390)], cls='data'); V.dot(tgt2, 390)
        exempt.append(m)
        V.notes.append('%s: PMOS S=VDD, D=%s, G=%s — 거울 짝 없음 (netlist 비대칭, Q4)' % (m, dn_, e['terms']['g']))
    # tail
    V.wire([(L, 460), (L, 480), (R, 480), (R, 460)], cls='plain'); V.dot(AX, 480)
    V.wire([(AX, 480), (AX, 510)], cls='plain')
    t_, b_, g_ = mosT(cell, tail)
    mt = mos(V, tail, AX, 540, 'n', 'left', tail, wl(cell, tail), t_, b_, g_, members=[tail])
    V.wire([(AX - 40, 540), (AX - 80, 540)], cls='clock')
    V.port(clk, AX - 80, 540, d='right', io='in', cls='clock')
    gnd_at(V, AX, 570)
    V.text(40, 640, '비대칭: ' + '; '.join(V.notes), size=10, color='#a33', cls='note')
    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [[cpP, cpN], [cnP, cnN], [iP, iN], [rsO[oP], rsO[oN]], [rsD[dP], rsD[dN]]],
                       'self': [tail], 'x0': 120, 'x1': 700, 'exempt_wires': ['asymmetric device ' + ','.join(exempt)],
                       'exempt_syms': exempt, 'exempt_boxes': [[AX - 45, 290, R + 1, 395]]})
    V.omitted = [x for x in hidden_list(cell) if x['net'] in ('VDD', 'VSS')]
    return V


# =====================================================================================
# U: CML latch (plan 5.4: input pair outside, cross-coupled X inside, clock pair mirrored, tail on axis)
# =====================================================================================
def view_cml_latch(cell):
    r = ROLES[cell]
    E = lambda m: el(cell, m)
    ins = [m for m in r if r[m]['role'] == 'input']
    ports = cells[cell]['ports']
    ins.sort(key=lambda m: ports.index(E(m)['terms']['g']))
    iP, iN = ins
    qP = E(iP)['terms'][topbot(cell, iP)[0]]; qN = E(iN)['terms'][topbot(cell, iN)[0]]
    cr = [m for m in r if r[m]['role'] == 'cross']
    cP = [m for m in cr if qP == E(m)['terms']['d']][0]; cN = [m for m in cr if m != cP][0]
    loads = [m for m in r if r[m]['role'] == 'load']
    lP = [m for m in loads if qP in E(m)['terms'].values()][0]; lN = [m for m in loads if m != lP][0]
    st = [m for m in r if r[m]['role'] == 'clock_steering']
    tT = E(iP)['terms'][topbot(cell, iP)[1]]
    sT = [m for m in st if tT in (E(m)['terms']['d'], E(m)['terms']['s'])][0]; sH = [m for m in st if m != sT][0]
    tail = [m for m in r if r[m]['role'] == 'tail'][0]
    V = new_view('u_latch', cell, 'unit', '%s — unit level (CML latch, 대칭)' % cell, 800, 700)
    AX = 380; X1, X2 = 200, 320
    rail(V, 150, 610, 70, 'VDD')
    for side, ld, inp, cc, q in ((-1, lP, iP, cP, qP), (1, lN, iN, cN, qN)):
        xo = AX + side * (AX - X1); xi = AX + side * (AX - X2)
        go = 'left' if side < 0 else 'right'; gi = 'right' if side < 0 else 'left'
        t_, b_, g_ = mosT(cell, ld)
        ml = mos(V, ld, xi, 140, 'p', go, ld, wl(cell, ld), t_, b_, g_, members=[ld])
        V.wire([(xi, 110), (xi, 70)], cls='power'); V.dot(xi, 70)
        gp = ml['pins'][2]
        V.wire([(gp['x'], 140), (gp['x'] + side * 20, 140), (gp['x'] + side * 20, 160)], cls='power')
        gnd(V, gp['x'] + side * 20, 160, E(ld)['terms']['g'])
        t_, b_, g_ = mosT(cell, cc)
        mc = mos(V, cc, xi, 300, 'n', gi, cc, wl(cell, cc), t_, b_, g_, members=[cc])
        V.wire([(xi, 170), (xi, 270)], cls='data')
        t_, b_, g_ = mosT(cell, inp)
        mi = mos(V, inp, xo, 300, 'n', go, inp, wl(cell, inp), t_, b_, g_, members=[inp])
        xp = AX + side * 290
        V.wire([(xp, 200), (xi, 200)], cls='data'); V.dot(xi, 200); V.dot(xo, 200)
        V.wire([(xo, 200), (xo, 270)], cls='data')
        V.port(q, xp, 200, d='left' if side < 0 else 'right', io='out')
        gx = mi['pins'][2]['x']
        V.wire([(gx, 300), (gx + side * 30, 300)], cls='data')
        V.port(E(inp)['terms']['g'], gx + side * 30, 300, d='right' if side < 0 else 'left', io='in')
    # X
    V.wire([(X2, 230), (2 * AX - X2 - 40, 300)], cls='data'); V.dot(X2, 230)
    V.wire([(2 * AX - X2, 230), (X2 + 40, 300)], cls='data'); V.dot(2 * AX - X2, 230)
    V.allowed_cross.append({'at': [AX, 230 + 70 * (AX - X2) / (2 * AX - X2 - 40 - X2)], 'reason': 'cross-coupled X'})
    # tails
    xoL, xoR = X1, 2 * AX - X1; xiL, xiR = X2, 2 * AX - X2
    V.wire([(xiL, 330), (xiL, 360), (xiR, 360), (xiR, 330)], cls='plain')
    V.wire([(xoL, 330), (xoL, 400), (xoR, 400), (xoR, 330)], cls='plain')
    xs1, xs2 = AX - 50, AX + 50
    for m, x, side, net_y in ((sT, xs1, -1, 400), (sH, xs2, 1, 360)):
        t_, b_, g_ = mosT(cell, m)
        ms = mos(V, m, x, 460, 'n', 'left' if side < 0 else 'right', m, wl(cell, m), t_, b_, g_, members=[m])
        V.wire([(x, 430), (x, net_y)], cls='plain'); V.dot(x, net_y)
        gp = ms['pins'][2]
        V.wire([(gp['x'], 460), (gp['x'] + side * 40, 460)], cls='clock')
        V.port(E(m)['terms']['g'], gp['x'] + side * 40, 460, d='right' if side < 0 else 'left', io='in', cls='clock')
    V.allowed_cross.append({'at': [xs2, 400], 'reason': 'steering into inner (cross-coupled) tail crosses the outer (input) tail (topologically unavoidable)'})
    V.wire([(xs1, 490), (xs1, 510), (xs2, 510), (xs2, 490)], cls='plain'); V.dot(AX, 510)
    V.wire([(AX, 510), (AX, 540)], cls='plain')
    t_, b_, g_ = mosT(cell, tail)
    mt = mos(V, tail, AX, 570, 'n', 'left', tail, wl(cell, tail), t_, b_, g_, members=[tail])
    gray_gate(V, mt['pins'][2], E(tail)['terms']['g'], 'left')
    gnd_at(V, AX, 600)
    mixed = [n for n, v in CN[cell].items() if 'data' in v and 'clock' in v]
    if mixed:
        V.text(30, 665, '참고: %s 는 DFE 경로에서 데이터, CLK_DIST_TREE에서 클럭 (선 굵기는 데이터 기준)' % ', '.join(mixed), size=10, color='#555', cls='note')
    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [[lP, lN], [iP, iN], [cP, cN], [sT, sH]], 'self': [tail], 'x0': 60, 'x1': 700,
                       'exempt_wires': ['steering drains go to different tails (structural)'], 'exempt_boxes': [[xs1 - 1, 355, xs2 + 1, 435]]})
    V.omitted = hidden_list(cell)
    return V


# =====================================================================================
# U: CML buffer (single pair), termination units, TG, CMOS gates
# =====================================================================================
def view_cml_buffer(cell, members, vid):
    r = ROLES[cell]; E = lambda m: el(cell, m)
    ins = [m for m in members if r[m]['role'] == 'input']
    ports = cells[cell]['ports']
    ins.sort(key=lambda m: ports.index(E(m)['terms']['g']))
    iP, iN = ins
    oP = E(iP)['terms'][topbot(cell, iP)[0]]; oN = E(iN)['terms'][topbot(cell, iN)[0]]
    lP = [m for m in members if r[m]['role'] == 'load' and oP in E(m)['terms'].values()][0]
    lN = [m for m in members if r[m]['role'] == 'load' and oN in E(m)['terms'].values()][0]
    tail = [m for m in members if r[m]['role'] == 'tail'][0]
    V = new_view(vid, cell, 'unit', '%s — unit level (CML 클럭 버퍼, 대칭)' % cell, 760, 560, scope=members)
    AX = 380
    rail(V, 160, 600, 70, 'VDD')
    for side, ld, inp, o in ((-1, lP, iP, oP), (1, lN, iN, oN)):
        x = AX + side * 70
        g = 'left' if side < 0 else 'right'
        t_, b_, g_ = mosT(cell, ld)
        ml = mos(V, ld, x, 140, 'p', g, ld, wl(cell, ld), t_, b_, g_, members=[ld])
        V.wire([(x, 110), (x, 70)], cls='power'); V.dot(x, 70)
        gp = ml['pins'][2]
        V.wire([(gp['x'], 140), (gp['x'] + side * 20, 140), (gp['x'] + side * 20, 160)], cls='power')
        gnd(V, gp['x'] + side * 20, 160, E(ld)['terms']['g'])
        t_, b_, g_ = mosT(cell, inp)
        mi = mos(V, inp, x, 300, 'n', g, inp, wl(cell, inp), t_, b_, g_, members=[inp])
        V.wire([(x, 170), (x, 270)], cls='clock')
        xe = AX + side * 250
        V.wire([(xe, 220), (x, 220)], cls='clock'); V.dot(x, 220)
        V.netlabel(o, xe, 220, tx=xe + (2 if side < 0 else -2), ty=211, anchor='start' if side < 0 else 'end')
        gx = mi['pins'][2]['x']
        V.wire([(gx, 300), (gx + side * 60, 300)], cls='clock')
        V.port(E(inp)['terms']['g'], gx + side * 60, 300, d='right' if side < 0 else 'left', io='in', cls='clock')
    V.wire([(AX - 70, 330), (AX - 70, 350), (AX + 70, 350), (AX + 70, 330)], cls='plain'); V.dot(AX, 350)
    V.wire([(AX, 350), (AX, 380)], cls='plain')
    t_, b_, g_ = mosT(cell, tail)
    mt = mos(V, tail, AX, 410, 'n', 'left', tail, wl(cell, tail), t_, b_, g_, members=[tail])
    gray_gate(V, mt['pins'][2], E(tail)['terms']['g'], 'left')
    gnd_at(V, AX, 440)
    V.symmetry.append({'axis': AX, 'orient': 'v', 'pairs': [[lP, lN], [iP, iN]], 'self': [tail], 'x0': 80, 'x1': 680, 'exempt_wires': []})
    V.omitted = [x for x in hidden_list(cell) if x['net'] in [n for m in members for n in E(m)['terms'].values()]]
    return V


def view_termination(cell, members, vid, title):
    """termination R to CM node (+ C to ground) and ESD clamps, drawn device by device."""
    r = ROLES[cell]; E = lambda m: el(cell, m)
    rs = [m for m in members if r[m]['role'] == 'termination']
    caps = [m for m in members if r[m]['role'] == 'cap_to_rail']
    esd = [m for m in members if r[m]['role'] == 'esd']
    ports = cells[cell]['ports']
    pad = lambda m: [n for n in E(m)['terms'].values() if n in ports and n not in ('VDD', 'VSS')][0]
    rs.sort(key=lambda m: ports.index(pad(m)))
    cm = [n for n in E(rs[0])['terms'].values() if n != pad(rs[0])][0]
    V = new_view(vid, cell, 'unit', title, 640, 600 if esd else 510, scope=members)
    yP, yN = 150, (450 if esd else 370)
    yC = (yP + yN) / 2
    xr = 400
    for i, (m, yl) in enumerate(((rs[0], yP), (rs[1], yN))):
        p = pad(m)
        cl = 'clock' if 'clock' in CN[cell].get(p, []) else 'data'
        V.port(p, 120, yl, d='right', io='in', cls=cl)
        # resistor from the pad line toward the CM node
        up = (i == 1)
        ry = (yl + yC) / 2
        tp = 'p' if E(m)['terms']['p'] == p else 'n'
        on = 'n' if tp == 'p' else 'p'
        if not up:
            res(V, m, xr, ry, 'v', name=m, size=E(m)['value'], a=T(m, tp), b=T(m, on), members=[m])
            V.wire([(120, yl), (xr, yl), (xr, ry - 30)], cls=cl)
            V.wire([(xr, ry + 30), (xr, yC)], cls='plain')
        else:
            res(V, m, xr, ry, 'v', name=m, size=E(m)['value'], a=T(m, on), b=T(m, tp), members=[m])
            V.wire([(120, yl), (xr, yl), (xr, ry + 30)], cls=cl)
            V.wire([(xr, ry - 30), (xr, yC)], cls='plain')
        # ESD on this pad
        pe = [x for x in esd if p in E(x)['terms'].values()]
        for x in pe:
            e = E(x)
            t_, b_, g_ = mosT(cell, x)
            if e['type'] == 'p':
                col = 200
                mm = mos(V, x, col, yl - 50, 'p', 'left', x, wl(cell, x), t_, b_, g_, members=[x])
                vdd_tee(V, col, yl - 80, 'VDD')
                V.wire([(col - 40, yl - 50), (col - 40, yl - 72)], cls='power'); vdd_tee(V, col - 40, yl - 72, 'VDD')
                V.wire([(col, yl - 20), (col, yl)], cls=cl); V.dot(col, yl)
            else:
                col = 280
                mm = mos(V, x, col, yl + 50, 'n', 'left', x, wl(cell, x), t_, b_, g_, members=[x])
                V.wire([(col, yl + 20), (col, yl)], cls=cl); V.dot(col, yl)
                gnd_at(V, col, yl + 80, l=8)
                V.wire([(col - 40, yl + 50), (col - 40, yl + 70)], cls='power'); gnd(V, col - 40, yl + 70, 'VSS')
    V.dot(xr, yC)
    for c in caps:
        e = E(c)
        tc = 'p' if e['terms']['p'] == cm else 'n'
        xc = 480 if esd else 520
        cap(V, c, xc, yC + 30, 'v', name=c, size=e['value'], a=T(c, tc), b=T(c, 'n' if tc == 'p' else 'p'), members=[c])
        V.wire([(xr, yC), (xc, yC)], cls='plain')
        gnd_at(V, xc, yC + 60, l=10)
    V.notes.append('공통모드 노드 %s 는 이 유닛 안에서만 그림 (블록 레벨에서는 바이어스로 숨김)' % cm)
    V.text(40, (600 if esd else 510) - 25, V.notes[-1], size=10, color='#555', cls='note')
    V.omitted = []
    return V


def view_tg(cell, groups, vid):
    r = ROLES[cell]; E = lambda m: el(cell, m)
    V = new_view(vid, cell, 'unit', '%s — unit level (전달 게이트 M_TIE, 게이트가 VSS/VDD에 묶여 항상 OFF)' % cell, 800, 440,
                 scope=[m for g in groups for m in g])
    for gi, g in enumerate(groups):
        nm = [m for m in g if E(m)['type'] == 'n'][0]; pm = [m for m in g if E(m)['type'] == 'p'][0]
        a, b = E(nm)['terms']['d'], E(nm)['terms']['s']
        ports = cells[cell]['ports']
        if a in ports:
            a, b = b, a     # a: internal node (top), b: port (bottom)
        side = -1 if gi == 0 else 1
        cx = 380 + side * 190
        xn, xp = cx - 80, cx + 80
        if side > 0:
            xn, xp = cx + 80, cx - 80
        ta = 'd' if E(nm)['terms']['d'] == a else 's'
        mos(V, nm, xn, 200, 'n', 'left' if xn < cx else 'right', nm, wl(cell, nm), T(nm, ta), T(nm, 's' if ta == 'd' else 'd'), T(nm, 'g'), members=[nm], arrow_at='bottom')
        tp = 'd' if E(pm)['terms']['d'] == a else 's'
        mos(V, pm, xp, 200, 'p', 'right' if xp > cx else 'left', pm, wl(cell, pm), T(pm, tp), T(pm, 's' if tp == 'd' else 'd'), T(pm, 'g'), members=[pm], arrow_at='top')
        V.wire([(xn, 170), (xn, 130), (xp, 130), (xp, 170)], cls='data')
        V.wire([(xn, 230), (xn, 270), (xp, 270), (xp, 230)], cls='data')
        V.dot(cx, 130); V.dot(cx, 270)
        V.wire([(cx, 130), (cx, 100)], cls='data')
        V.netlabel(a, cx, 100, tx=cx, ty=90, anchor='middle')
        V.wire([(cx, 270), (cx, 310)], cls='data')
        V.port(b, cx, 310, d='down', io='out')
        gxn = xn - 40 if xn < cx else xn + 40
        V.wire([(gxn, 200), (gxn, 225)], cls='power'); gnd(V, gxn, 225, E(nm)['terms']['g'])
        gxp = xp + 40 if xp > cx else xp - 40
        V.wire([(gxp, 200), (gxp, 175)], cls='power'); vdd_tee(V, gxp, 175, E(pm)['terms']['g'])
    V.text(40, 400, '두 TG 모두 NMOS 게이트=VSS, PMOS 게이트=VDD → 항상 OFF. O_DOUTP/N 은 사실상 떠 있음 (Q3).', size=11, color='#a33', cls='note')
    V.symmetry.append({'axis': 380, 'orient': 'v', 'pairs': [[groups[0][0], groups[1][0]], [groups[0][1], groups[1][1]]], 'self': [], 'x0': 60, 'x1': 700, 'exempt_wires': []})
    V.omitted = []
    return V


def view_inv(cell):
    E = lambda m: el(cell, m)
    r = ROLES[cell]
    mp = [m for m in r if E(m)['type'] == 'p'][0]; mn = [m for m in r if E(m)['type'] == 'n'][0]
    a = E(mp)['terms']['g']; y = E(mp)['terms']['d'] if E(mp)['terms']['s'] == 'VDD' else E(mp)['terms']['s']
    V = new_view('u_inv', cell, 'unit', '%s — unit level (CMOS 인버터 / 버퍼)' % cell, 480, 420)
    rail(V, 160, 360, 70, 'VDD')
    t_, b_, g_ = mosT(cell, mp)
    mos(V, mp, 240, 140, 'p', 'left', mp, wl(cell, mp), t_, b_, g_, members=[mp])
    V.wire([(240, 110), (240, 70)], cls='power'); V.dot(240, 70)
    t_, b_, g_ = mosT(cell, mn)
    mos(V, mn, 240, 280, 'n', 'left', mn, wl(cell, mn), t_, b_, g_, members=[mn])
    V.wire([(200, 140), (200, 280)], cls='data'); V.dot(200, 210)
    V.wire([(120, 210), (200, 210)], cls='data')
    V.port(a, 120, 210, d='right', io='in')
    V.wire([(240, 170), (240, 250)], cls='data'); V.dot(240, 210)
    V.wire([(240, 210), (340, 210)], cls='data')
    V.port(y, 340, 210, d='right', io='out')
    gnd_at(V, 240, 310)
    V.text(30, 395, '참고: A/Y 는 슬라이서 출력 버퍼(데이터)와 CLK_DIST_TREE 체인(클럭)에 함께 쓰임', size=10, color='#555', cls='note')
    V.omitted = hidden_list(cell)
    return V


def view_nand(cell):
    E = lambda m: el(cell, m)
    r = ROLES[cell]
    ps = [m for m in r if E(m)['type'] == 'p']; ns = [m for m in r if E(m)['type'] == 'n']
    ports = cells[cell]['ports']
    ps.sort(key=lambda m: ports.index(E(m)['terms']['g']))
    y = [n for n in E(ps[0])['terms'].values() if n in ports and n not in ('VDD', 'VSS') and n != E(ps[0])['terms']['g']][0]
    nTop = [m for m in ns if y in E(m)['terms'].values()][0]; nBot = [m for m in ns if m != nTop][0]
    V = new_view('u_nand', cell, 'unit', '%s — unit level (정적 CMOS 게이트, 사전에 없음 → 소자 그대로)' % cell, 560, 520)
    rail(V, 160, 420, 70, 'VDD')
    xs = [220, 340]
    for x, m in zip(xs, ps):
        t_, b_, g_ = mosT(cell, m)
        mos(V, m, x, 140, 'p', 'left', m, wl(cell, m), t_, b_, g_, members=[m])
        V.wire([(x, 110), (x, 70)], cls='power'); V.dot(x, 70)
    V.wire([(220, 170), (220, 200), (340, 200), (340, 170)], cls='data')
    V.dot(280, 200); V.dot(340, 200)
    V.wire([(340, 200), (440, 200)], cls='data')
    V.port(y, 440, 200, d='right', io='out')
    t_, b_, g_ = mosT(cell, nTop)
    mos(V, nTop, 280, 260, 'n', 'left', nTop, wl(cell, nTop), t_, b_, g_, members=[nTop])
    V.wire([(280, 200), (280, 230)], cls='data')
    t_, b_, g_ = mosT(cell, nBot)
    mos(V, nBot, 280, 360, 'n', 'left', nBot, wl(cell, nBot), t_, b_, g_, members=[nBot])
    V.wire([(280, 290), (280, 330)], cls='plain')
    gnd_at(V, 280, 390)
    ga = E(ps[0])['terms']['g']; gb = E(ps[1])['terms']['g']
    V.wire([(110, 260), (240, 260)], cls='data'); V.dot(180, 260)
    V.wire([(180, 140), (180, 260)], cls='data')
    V.port(ga, 110, 260, d='right', io='in')
    V.wire([(110, 360), (240, 360)], cls='data')
    V.port(gb, 110, 360, d='right', io='in')
    stub_label(V, {'x': 300, 'y': 140}, gb, 'down', cls='data', L=24, side='right')
    V.omitted = hidden_list(cell)
    return V


# =====================================================================================
# B: block-level views
# =====================================================================================
def inst_terms(inst, port):
    return [[(inst, port)]]


def view_top(cell):
    c = cells[cell]
    insts = {e['name']: e for e in c['elems'] if e['kind'] == 'inst'}
    B = A['block']
    blockrole = lambda i: B[insts[i]['cell']]['role']
    hs_in = [p for p in c['ports'] if 'data' in CN[cell][p] and p in A['hs_inputs']]
    groups = A['groups'][cell]
    V = new_view('b_top', cell, 'block', '%s — 블록 레벨 (최상위)' % cell, 1420, 840)
    P, N = hs_in
    yP, yN = 150, 170
    # input ports + termination/ESD markers
    V.port(P, 110, yP, d='right', io='in'); V.port(N, 110, yN, d='right', io='in')
    term = [g for g in groups if g['role'].startswith('termination')][0]
    term_marker(V, 'TERM_P', 160, yP, True, 'R_T 50Ω', [[(m, t) for m in term['members'] for t, n in el(cell, m)['terms'].items() if n == P and t != 'b']], esd=True,
                link='u_rxterm', members=term['members'])
    term_marker(V, 'TERM_N', 160, yN, False, 'R_T 50Ω', [[(m, t) for m in term['members'] for t, n in el(cell, m)['terms'].items() if n == N and t != 'b']], esd=True,
                link='u_rxterm', members=[])
    V.dot(160, yP); V.dot(160, yN)
    V.wire([(160, yP), (160, yP - 12)], cls='data'); V.wire([(160, yN), (160, yN + 12)], cls='data')
    # chain of amplifier stages from the HS input: follow instance connectivity
    chain = []
    cur = (P, N)
    while True:
        nxt = [i for i, e in insts.items() if e['pins'].get(cells[e['cell']]['ports'][0]) == cur[0] and B[e['cell']]['role'] in ('ctle', 'vga', 'cml_buffer')]
        if not nxt:
            break
        i = nxt[0]; e = insts[i]; sp = cells[e['cell']]['ports']
        outs = [p for p in sp if 'data' in CN[e['cell']].get(p, []) and p not in sp[:2]]
        chain.append((i, sp[0], sp[1], outs[0], outs[1]))
        cur = (e['pins'][outs[0]], e['pins'][outs[1]])
    x0 = 240
    prev = None
    for k, (i, a, b_, o1, o2) in enumerate(chain):
        e = insts[i]
        lab = {'ctle': 'CTLE', 'vga': 'VGA', 'cml_buffer': 'BUF'}[B[e['cell']]['role']]
        tri(V, i, x0, 160, lab, i, ins=[(a, -10, inst_terms(i, a)), (b_, 10, inst_terms(i, b_))],
            outs=[(o1, -10, inst_terms(i, o1)), (o2, 10, inst_terms(i, o2))], link={'ctle': 'u_ctle', 'vga': 'u_vga'}[B[e['cell']]['role']],
            members=[i], sub=e['cell'])
        if prev is None:
            V.wire([(110, yP), (x0 - 20, yP)], cls='data'); V.wire([(110, yN), (x0 - 20, yN)], cls='data')
        else:
            V.wire([(prev, yP), (x0 - 20, yP)], cls='data'); V.wire([(prev, yN), (x0 - 20, yN)], cls='data')
            V.netlabel(insts[chain[k - 1][0]]['pins'][chain[k - 1][3]], prev + 2, yP, tx=prev + 3, ty=yP - 8)
            V.netlabel(insts[chain[k - 1][0]]['pins'][chain[k - 1][4]], prev + 2, yN, tx=prev + 3, ty=yN + 9)
        prev = x0 + 100
        x0 += 160
    vP, vN = cur
    # slices: instances whose first data port is driven by the chain output
    slices = [i for i, e in insts.items() if vP in e['pins'].values() and B[e['cell']]['role'] == 'composite']
    slices.sort(key=lambda i: list(insts).index(i))
    scell = insts[slices[0]]['cell']
    sp = cells[scell]['ports']
    vis = lambda p: any(x in CN[scell].get(p, []) for x in ('data', 'clock', 'important_control'))
    # classify slice pins: main inputs, feedback inputs (left), outputs (right), clocks (bottom), bus (top)
    sr = A['cellnet'][scell]
    sub = {e['name']: e for e in cells[scell]['elems'] if e['kind'] == 'inst'}
    def driven(p):
        # port net is an output pin of a sub instance? (structural: connects to a drain inside)
        g = A['l2g'][INST[scell][0]][p]
        return any(d['terms'].get('d') == g or d['terms'].get('s') == g for d in [])
    left_main = sp[:2]
    clocks = [p for p in sp if 'clock' in sr[p]]
    bus = [p for p in sp if 'important_control' in sr[p]]
    pre = INST[scell][0]
    outs_s = [p for p in sp if 'data' in sr[p] and p not in left_main and port_is_output(scell, p)]
    fb_in = [p for p in sp if 'data' in sr[p] and p not in left_main and p not in outs_s]
    # order feedback inputs: T1_FB first then T2..T4 (by the summer tap they feed)
    summ = [e for e in sub.values() if B[e['cell']]['role'] == 'summer'][0]
    tap_order = [summ['pins'][q] for q in cells[summ['cell']]['ports'] if 'data' in CN[summ['cell']].get(q, []) and q not in cells[summ['cell']]['ports'][:2]]
    fb_in.sort(key=lambda p: tap_order.index(p) if p in tap_order else 99)
    bx, bw = 860, 260
    slice_y = {slices[0]: 125, slices[1]: 445}
    pinpos = {}
    for si in slices:
        y0 = slice_y[si]
        e = insts[si]
        lefts = [(left_main[0], y0 + 25), (left_main[1], y0 + 45)] + [(p, y0 + 85 + 20 * k) for k, p in enumerate(fb_in)]
        rights = [(p, y0 + 25 + 20 * k + (20 if k >= 2 else 0)) for k, p in enumerate(outs_s)]
        h = max(y for _, y in lefts) - y0 + 25
        sym = box(V, si, bx, y0, bw, h, scell, si, left=[(p, y, inst_terms(si, p), 'data') for p, y in lefts],
                  right=[(p, y, inst_terms(si, p), 'data') for p, y in rights],
                  bottom=[(clocks[0], bx + 60, inst_terms(si, clocks[0]), 'clock'), (clocks[1], bx + 120, inst_terms(si, clocks[1]), 'clock')],
                  top=[('W<1:4>_<0:3>', bx + 200, [[(si, p)] for p in bus], 'bus')], link='b_slice', members=[si])
        pinpos[si] = {p['name']: p for p in sym['pins']}
        pinpos[si]['_h'] = h
    # VGA -> slices (P branch crosses N line once)
    s0, s1 = slices
    V.wire([(prev, yP), (840, yP)], cls='data'); V.wire([(prev, yN), (840, yN)], cls='data')
    V.netlabel(vP, prev + 2, yP, tx=prev + 3, ty=yP - 8); V.netlabel(vN, prev + 2, yN, tx=prev + 3, ty=yN + 9)
    y1P = pinpos[s1][left_main[0]]['y']; y1N = pinpos[s1][left_main[1]]['y']
    V.wire([(780, yP), (780, y1P), (840, y1P)], cls='data'); V.dot(780, yP)
    V.wire([(760, yN), (760, y1N), (840, y1N)], cls='data'); V.dot(760, yN)
    V.allowed_cross.append({'at': [780, yN], 'reason': 'differential pair split to a block below: P branch must cross N line once'})
    # feedback / clock / bus connections by net label (wiring would go around a block -> twisted)
    for si in slices:
        e = insts[si]
        for p in fb_in:
            stub_label(V, pinpos[si][p], e['pins'][p], 'left', L=46)
        for p in outs_s[2:]:
            stub_label(V, pinpos[si][p], e['pins'][p], 'right', L=46)
        for k, p in enumerate(clocks):
            stub_label(V, pinpos[si][p], e['pins'][p], 'down', cls='clock', L=22, side='left' if k == 0 else 'right')
    # outputs to ports
    for si in slices:
        e = insts[si]
        for p in outs_s[:2]:
            pp = pinpos[si][p]
            V.wire([(pp['x'], pp['y']), (1300, pp['y'])], cls='data')
            V.port(e['pins'][p], 1300, pp['y'], d='right', io='out')
    # important control bus: one trunk from the top into the first slice; second slice by label
    bnm = 'W<1:4>_<0:3>'
    wp = pinpos[s0]['W<1:4>_<0:3>']
    V.wire([(wp['x'], 50), (wp['x'], wp['y'])], cls='bus')
    V.port(bnm, wp['x'], 50, d='down', io='in', cls='bus', label_side='right')
    busslash(V, wp['x'], 78, len(bus))
    wp1 = pinpos[s1]['W<1:4>_<0:3>']
    stub_label(V, wp1, bnm, 'up', cls='bus', L=20, side='right')
    # TG (always-off) between the odd slice output and O_DOUT
    tg = [g for g in groups if g['role'] == 'tg']
    e1 = insts[s1]
    for k, g in enumerate(tg):
        nm = [m for m in g['members'] if el(cell, m)['type'] == 'n'][0]
        a, b_ = el(cell, nm)['terms']['d'], el(cell, nm)['terms']['s']
        portnet = a if a in c['ports'] else b_
        inner = b_ if portnet == a else a
        pp = [pinpos[s1][p] for p in outs_s[:2] if e1['pins'][p] == portnet][0]
        xt = 1220
        up = (k == 0)
        yc = pp['y'] - 40 if up else pp['y'] + 40
        ta = [[(m, t) for m in g['members'] for t in ('d', 's') if el(cell, m)['terms'][t] == (inner if up else portnet)]]
        tb_ = [[(m, t) for m in g['members'] for t in ('d', 's') if el(cell, m)['terms'][t] == (portnet if up else inner)]]
        switch_open(V, 'TG%d' % k, xt, yc, 'v', ta, tb_, 'TG', '/'.join(g['members']) + ' (off)', link='u_tg', members=g['members'])
        if up:
            V.wire([(xt, yc + 30), (xt, pp['y'])], cls='data'); V.dot(xt, pp['y'])
            stub_label(V, {'x': xt, 'y': yc - 30}, inner, 'up', L=16, side='right')
        else:
            V.wire([(xt, yc - 30), (xt, pp['y'])], cls='data'); V.dot(xt, pp['y'])
            stub_label(V, {'x': xt, 'y': yc + 30}, inner, 'down', L=16, side='right')
    # clock block
    ck = [i for i, e in insts.items() if any('clock' in CN[e['cell']].get(p, []) for p in cells[e['cell']]['ports']) and i not in slices][0]
    ce = insts[ck]; cp = cells[ce['cell']]['ports']
    cin = [p for p in cp if 'clock' in CN[ce['cell']][p] and ce['pins'][p] in c['ports']]
    cout = [p for p in cp if 'clock' in CN[ce['cell']][p] and p not in cin]
    bx0, by0 = 380, 630
    sym = box(V, ck, bx0, by0, 200, 140, ce['cell'], ck, left=[(p, by0 + 40 + 20 * k, inst_terms(ck, p), 'clock') for k, p in enumerate(cin)],
              right=[(p, by0 + 40 + 20 * k + (20 if k >= 2 else 0), inst_terms(ck, p), 'clock') for k, p in enumerate(cout)], link='b_clk', members=[ck])
    for p in sym['pins']:
        if p['name'] in cin:
            V.wire([(110, p['y']), (p['x'], p['y'])], cls='clock')
            V.port(ce['pins'][p['name']], 110, p['y'], d='right', io='in', cls='clock')
        else:
            stub_label(V, p, ce['pins'][p['name']], 'right', cls='clock', L=50)
    # omitted
    om = []
    for i, e in insts.items():
        if B[e['cell']]['symbol'] == 'omit':
            om.append({'block': i, 'cell': e['cell'], 'reason': '고속 신호와 연결 없음 (%s)' % B[e['cell']]['role']})
    V.omitted = hidden_list(cell) + om
    V.text(40, 800, '연결 규칙: 블록을 돌아가야 하는 넷(귀환 탭, 클럭 분배, 두 번째 슬라이스의 계수 버스)은 같은 이름의 넷 이름표로 연결 (Virtuoso 방식)', size=10, color='#555', cls='note')
    return V


def view_slice(cell):
    c = cells[cell]
    insts = {e['name']: e for e in c['elems'] if e['kind'] == 'inst'}
    B = A['block']
    rl = {i: B[e['cell']]['role'] for i, e in insts.items()}
    sp = c['ports']
    cn = CN[cell]
    V = new_view('b_slice', cell, 'block', '%s — 블록 레벨' % cell, 1420, 520)
    summ = [i for i in insts if rl[i] == 'summer'][0]
    se = insts[summ]; sports = cells[se['cell']]['ports']
    main_in = sports[:2]
    taps = [p for p in sports if 'data' in CN[se['cell']].get(p, []) and p not in main_in and p not in sports[-2:] and
            not any(x in p for x in ())]
    souts = [p for p in sports if 'data' in CN[se['cell']].get(p, []) and p not in main_in and p not in taps]
    # outputs = pins whose net is driven inside the summer (drains): use the trace: OUTP/OUTN are reached via (g->d)
    pre = INST[se['cell']][0]
    souts = [p for p in sports if 'data' in CN[se['cell']].get(p, []) and A['data_trace'][A['l2g'][pre][p]]['via'].startswith(pre)]
    taps = [p for p in sports if 'data' in CN[se['cell']].get(p, []) and p not in main_in and p not in souts]
    bus = [p for p in sports if 'important_control' in CN[se['cell']].get(p, [])]
    # summer box
    sx, sy, sw, sh = 200, 150, 200, 110
    sym = box(V, summ, sx, sy, sw, sh, 'Σ', summ, left=[(main_in[0], 200, inst_terms(summ, main_in[0]), 'data'), (main_in[1], 220, inst_terms(summ, main_in[1]), 'data')],
              right=[(souts[0], 200, inst_terms(summ, souts[0]), 'data'), (souts[1], 220, inst_terms(summ, souts[1]), 'data')],
              bottom=[(p, sx + 30 + 20 * k, inst_terms(summ, p), 'data') for k, p in enumerate(taps)],
              top=[('W<1:4>_<0:3>', sx + 100, [[(summ, p)] for p in bus], 'bus')], link='u_summer', members=[summ], big=True, sub=se['cell'])
    pp = {p['name']: p for p in sym['pins']}
    # main inputs
    for k, p in enumerate(main_in):
        V.wire([(110, pp[p]['y']), (pp[p]['x'], pp[p]['y'])], cls='data')
        V.port(se['pins'][p], 110, pp[p]['y'], d='right', io='in')
    # tap inputs from ports at left-bottom (nested L shapes, no crossing)
    for k, p in enumerate(taps):
        y = 300 + 20 * k
        V.wire([(110, y), (pp[p]['x'], y), (pp[p]['x'], pp[p]['y'])], cls='data')
        V.port(se['pins'][p], 110, y, d='right', io='in')
    # W bus
    wp = pp['W<1:4>_<0:3>']
    V.wire([(wp['x'], 80), (wp['x'], wp['y'])], cls='bus')
    V.port('W<1:4>_<0:3>', wp['x'], 80, d='down', io='in', cls='bus', label_side='right')
    busslash(V, wp['x'], 105, len(bus))
    # slicer
    sl = [i for i in insts if rl[i] == 'composite' and insts[i]['pins'].get(cells[insts[i]['cell']]['ports'][0]) == se['pins'][souts[0]]][0]
    le = insts[sl]; lp = cells[le['cell']]['ports']
    lclk = [p for p in lp if 'clock' in CN[le['cell']].get(p, [])]
    louts = [p for p in lp if 'data' in CN[le['cell']].get(p, []) and p not in lp[:2]]
    tri(V, sl, 520, 210, 'SA', sl, ins=[(lp[0], -10, inst_terms(sl, lp[0])), (lp[1], 10, inst_terms(sl, lp[1]))],
        outs=[(louts[0], -10, inst_terms(sl, louts[0])), (louts[1], 10, inst_terms(sl, louts[1]))],
        bottom=[(lclk[0], 30, inst_terms(sl, lclk[0]), 'clock')], link='b_sa', members=[sl], clock_mark=True, sub=le['cell'])
    for k, p in enumerate(souts):
        y = pp[p]['y']
        V.wire([(420, y), (500, y)], cls='data')
        V.netlabel(se['pins'][p], 460, y, tx=460, ty=y - 8 if k == 0 else y + 9, anchor='middle')
    # latch and DFF chain (follow data connectivity)
    chain = []
    curP = le['pins'][louts[0]]
    x = 700
    prev_x = 620
    names = []
    while True:
        nx = [i for i, e in insts.items() if rl[i] in ('latch', 'dff') and e['pins'][cells[e['cell']]['ports'][0]] == curP and i not in chain]
        if not nx:
            break
        i = nx[0]; e = insts[i]; ip = cells[e['cell']]['ports']
        ck = [p for p in ip if CN[e['cell']].get(p, []) == ['clock']]
        qo = [p for p in ip if ('data' in CN[e['cell']].get(p, []) or 'clock' in CN[e['cell']].get(p, [])) and p not in ip[:2] and p not in ck]
        lab = 'LATCH' if rl[i] == 'latch' else 'DFF'
        sym = box(V, i, x, 160, 100, 100, lab, i, left=[(ip[0], 200, inst_terms(i, ip[0]), 'data'), (ip[1], 220, inst_terms(i, ip[1]), 'data')],
                  right=[(qo[0], 200, inst_terms(i, qo[0]), 'data'), (qo[1], 220, inst_terms(i, qo[1]), 'data')],
                  bottom=[(ck[0], x + 30, inst_terms(i, ck[0]), 'clock'), (ck[1], x + 70, inst_terms(i, ck[1]), 'clock')],
                  link='u_latch' if rl[i] == 'latch' else 'b_dff', members=[i], sub=e['cell'])
        chain.append(i)
        V.wire([(prev_x, 200), (x - 20, 200)], cls='data'); V.wire([(prev_x, 220), (x - 20, 220)], cls='data')
        if len(chain) == 1:
            V.netlabel(le['pins'][louts[0]], (prev_x + x - 20) / 2, 200, tx=(prev_x + x - 20) / 2, ty=192, anchor='middle')
            V.netlabel(le['pins'][louts[1]], (prev_x + x - 20) / 2, 220, tx=(prev_x + x - 20) / 2, ty=229, anchor='middle')
        else:
            # branch to output ports at the existing line: P up, N down
            xb = prev_x + 30
            pn = insts[chain[-2]]['pins']
            V.dot(xb, 200); V.dot(xb, 220)
            V.wire([(xb, 200), (xb, 150)], cls='data'); V.port(pn[qprev[0]], xb, 150, d='up', io='out')
            V.wire([(xb, 220), (xb, 270)], cls='data'); V.port(pn[qprev[1]], xb, 270, d='down', io='out')
        qprev = qo
        curP = e['pins'][qo[0]]
        prev_x = x + 120
        x += 220
    # last outputs to the right
    pn = insts[chain[-1]]['pins']
    V.wire([(prev_x, 200), (prev_x + 80, 200)], cls='data'); V.port(pn[qprev[0]], prev_x + 80, 200, d='right', io='out')
    V.wire([(prev_x, 220), (prev_x + 80, 220)], cls='data'); V.port(pn[qprev[1]], prev_x + 80, 220, d='right', io='out')
    # clocks: primary trunk wired from below; complementary phase by labels (avoids interleaving crossings)
    ck0 = lclk[0]
    cknet = le['pins'][ck0]
    xs = [520 + 30]
    for i in chain:
        e = insts[i]; ip = cells[e['cell']]['ports']
        ck = [p for p in ip if CN[e['cell']].get(p, []) == ['clock']]
        sm = [s for s in V.symbols if s['id'] == i][0]
        for p in sm['pins']:
            if p['name'] in ck:
                if e['pins'][p['name']] == cknet:
                    xs.append(p['x'])
                else:
                    stub_label(V, p, e['pins'][p['name']], 'down', cls='clock', L=20, side='right')
    yT = 330
    V.wire([(500, yT), (max(xs), yT)], cls='clock')
    for x_ in xs:
        top = 275 if x_ == 550 else 280
        V.wire([(x_, yT), (x_, top)], cls='clock')
        if x_ != max(xs):
            V.dot(x_, yT)
    V.port(cknet, 500, yT, d='right', io='in', cls='clock')
    other = [p for p in sp if 'clock' in cn[p] and p != cknet][0]
    V.wire([(500, 370), (540, 370)], cls='clock')
    V.port(other, 500, 370, d='right', io='in', cls='clock')
    V.text(40, 495, '클럭: %s 는 줄기+가지로 배선, %s 는 같은 이름 이름표로 연결 (두 줄기를 모두 배선하면 핀 순서가 엇갈려 교차가 생김)' % (cknet, other), size=10, color='#555', cls='note')
    V.omitted = hidden_list(cell)
    return V


def view_clk(cell):
    c = cells[cell]
    insts = {e['name']: e for e in c['elems'] if e['kind'] == 'inst'}
    B = A['block']; rl = {i: B[e['cell']]['role'] for i, e in insts.items()}
    groups = A['groups'][cell]
    cp = c['ports']
    cin = [p for p in cp if 'clock' in CN[cell][p] and A['clock_trace'].get(A['l2g'][INST[cell][0]][p], {}).get('via') == 'start']
    V = new_view('b_clk', cell, 'block', '%s — 블록 레벨' % cell, 1300, 480)
    yP, yN = 200, 220
    V.port(cin[0], 110, yP, d='right', io='in', cls='clock'); V.port(cin[1], 110, yN, d='right', io='in', cls='clock')
    term = [g for g in groups if g['role'] == 'termination'][0]
    tm = lambda net: [[(m, t) for m in term['members'] for t, n in el(cell, m)['terms'].items() if n == net]]
    term_marker(V, 'TERM_P', 160, yP, True, 'R_T 50Ω', tm(cin[0]), link='u_clkterm', members=term['members'])
    term_marker(V, 'TERM_N', 160, yN, False, 'R_T 50Ω', tm(cin[1]), link='u_clkterm', members=[])
    V.dot(160, yP); V.dot(160, yN)
    V.wire([(160, yP), (160, yP - 12)], cls='clock'); V.wire([(160, yN), (160, yN + 12)], cls='clock')
    buf = [g for g in groups if g['role'] == 'cml_buffer'][0]
    bm = buf['members']
    E = lambda m: el(cell, m)
    ins = sorted([m for m in bm if ROLES[cell][m]['role'] == 'input'], key=lambda m: cp.index(E(m)['terms']['g']))
    oP = E(ins[0])['terms'][topbot(cell, ins[0])[0]]; oN = E(ins[1])['terms'][topbot(cell, ins[1])[0]]
    def gt(net):
        return [[(m, t) for m in bm for t, n in E(m)['terms'].items() if n == net and t != 'b']]
    tri(V, 'BUF', 240, 210, 'BUF', '', ins=[('INP', -10, gt(cin[0])), ('INN', 10, gt(cin[1]))], outs=[(oP, -10, gt(oP)), (oN, 10, gt(oN))],
        link='u_clkbuf', members=bm, sub='CML buffer (MP/MN_B1*, MB_B1)', cls='clock')
    V.wire([(110, yP), (220, yP)], cls='clock'); V.wire([(110, yN), (220, yN)], cls='clock')
    # latches: master fed by buffer output
    lat = [i for i in insts if rl[i] == 'latch']
    m_ = [i for i in lat if oP in insts[i]['pins'].values() and set(insts[i]['pins'].values()) & {oP, oN}
          and insts[i]['pins'][cells[insts[i]['cell']]['ports'][0]] in (oP, oN)][0]
    s_ = [i for i in lat if i != m_][0]
    lp = cells[insts[m_]['cell']]['ports']
    lck = [p for p in lp if CN[insts[m_]['cell']][p] == ['clock']]
    lq = [p for p in lp if p not in lp[:2] and p not in lck and ('data' in CN[insts[m_]['cell']][p] or 'clock' in CN[insts[m_]['cell']][p])]
    me = insts[m_]; se_ = insts[s_]
    for i, x in ((m_, 460), (s_, 700)):
        e = insts[i]
        box(V, i, x, 160, 100, 100, 'LATCH', i, left=[(lp[0], 200, inst_terms(i, lp[0]), 'clock'), (lp[1], 220, inst_terms(i, lp[1]), 'clock')],
            right=[(lq[0], 200, inst_terms(i, lq[0]), 'clock'), (lq[1], 220, inst_terms(i, lq[1]), 'clock')],
            bottom=[(lck[0], x + 30, inst_terms(i, lck[0]), 'clock'), (lck[1], x + 70, inst_terms(i, lck[1]), 'clock')], link='u_latch', members=[i],
            sub=e['cell'])
        sm = [s for s in V.symbols if s['id'] == i][0]
        for k, p in enumerate([p for p in sm['pins'] if p['name'] in lck]):
            stub_label(V, p, e['pins'][p['name']], 'down', cls='clock', L=20, side='left' if k == 0 else 'right')
    # buffer -> master data inputs (as connected; swap -> one X crossing)
    dP, dN = me['pins'][lp[0]], me['pins'][lp[1]]
    yof = {oP: yP, oN: yN}
    for net, ytarget in ((dP, 200), (dN, 220)):
        ys = yof[net]
        if ys == ytarget:
            V.wire([(340, ys), (440, ys)], cls='clock')
        else:
            V.wire([(340, ys), (370, ys), (410, ytarget), (440, ytarget)], cls='clock')
    if dP != oP:
        V.allowed_cross.append({'at': [390, 210], 'reason': 'netlist connects BUF P output to latch N input (swap)'})
    V.netlabel(oP, 350, yP, tx=352, ty=yP - 8, anchor='start'); V.netlabel(oN, 350, yN, tx=352, ty=yN + 9, anchor='start')
    # master Q -> slave D, branches to ports + INV chains
    invs = [i for i in insts if rl[i] == 'inverter']
    def chain_from(net):
        out = []; cur = net
        while True:
            nx = [i for i in invs if insts[i]['pins']['A'] == cur]
            if not nx:
                return out, cur
            out.append(nx[0]); cur = insts[nx[0]]['pins']['Y']
    def draw_inv_chain(net, x, y, up):
        ch, endnet = chain_from(net)
        xx = x
        V.wire([(x - 20, y), (x, y)], cls='clock') if False else None
        for k, i in enumerate(ch):
            inv(V, i, xx + 20, y, i, inst_terms(i, 'A'), inst_terms(i, 'Y'), link='u_inv', members=[i], flip_label=up, cls='clock')
            if k > 0:
                pass
            xx += 102
        return ch, endnet
    qP, qN = me['pins'][lq[0]], me['pins'][lq[1]]
    for net, y, yb, yi, up in ((qP, 200, 100, 60, True), (qN, 220, 320, 360, False)):
        V.wire([(580, y), (680, y)], cls='clock')
        V.dot(620, y)
        V.wire([(620, y), (620, yb), (1150, yb)], cls='clock')
        V.port(net, 1150, yb, d='right', io='out', cls='clock')
        V.dot(660, yb)
        V.wire([(660, yb), (660, yi), (680, yi)], cls='clock')
        ch, endnet = chain_from(net)
        xx = 700
        for k, i in enumerate(ch):
            inv(V, i, xx, yi, i, inst_terms(i, 'A'), inst_terms(i, 'Y'), link='u_inv', members=[i], flip_label=up, cls='clock')
            if k > 0:
                V.wire([(xx - 40, yi), (xx - 20, yi)], cls='clock')
                V.netlabel(insts[ch[k - 1]]['pins']['Y'], xx - 30, yi, tx=xx - 30, ty=yi + (9 if up else -9), anchor='middle', size=9) if False else None
            xx += 102
        stub_label(V, {'x': xx - 40, 'y': yi}, endnet, 'right', cls='clock', L=24, side='above' if up else 'below')
    sP, sN = se_['pins'][lq[0]], se_['pins'][lq[1]]
    for net, y, yi, up in ((sP, 200, 150, True), (sN, 220, 270, False)):
        V.wire([(820, y), (1150, y)], cls='clock')
        V.port(net, 1150, y, d='right', io='out', cls='clock')
        V.dot(860, y)
        V.wire([(860, y), (860, yi), (880, yi)], cls='clock')
        ch, endnet = chain_from(net)
        xx = 900
        for k, i in enumerate(ch):
            inv(V, i, xx, yi, i, inst_terms(i, 'A'), inst_terms(i, 'Y'), link='u_inv', members=[i], flip_label=up, cls='clock')
            if k > 0:
                V.wire([(xx - 40, yi), (xx - 20, yi)], cls='clock')
            xx += 102
        stub_label(V, {'x': xx - 40, 'y': yi}, endnet, 'right', cls='clock', L=24, side='above' if up else 'below')
    V.text(40, 455, '주의: 이름은 DIV(÷2)이지만 구조상 귀환 루프 없음 → LATCH 2개 직렬로 그대로 그림 (Q2). INV 체인 출력은 연결 없음 (Q6).', size=10, color='#a33', cls='note')
    V.omitted = hidden_list(cell)
    return V


def view_sa_block(cell, core_members):
    c = cells[cell]
    insts = {e['name']: e for e in c['elems'] if e['kind'] == 'inst'}
    B = A['block']; rl = {i: B[e['cell']]['role'] for i, e in insts.items()}
    cp = c['ports']
    V = new_view('b_sa', cell, 'block', '%s — 블록 레벨' % cell, 900, 400)
    E = lambda m: el(cell, m)
    r = ROLES[cell]
    ins = sorted([m for m in core_members if r[m]['role'] == 'input' and E(m)['type'] == 'n'], key=lambda m: cp.index(E(m)['terms']['g']))
    clk = [m for m in core_members if r[m]['role'] == 'clocked_tail'][0]
    crossN = [m for m in core_members if r[m]['role'] == 'cross' and E(m)['type'] == 'n']
    # outputs of the core: nets that leave the group (to sub instances)
    used = collections.Counter()
    for e in c['elems']:
        if e['kind'] == 'inst':
            for n in e['pins'].values():
                used[n] += 1
    outs = [n for n in sorted({E(m)['terms']['d'] for m in crossN}) if used[n]]
    sr = [i for i in insts if set(insts[i]['pins'].values()) & set(outs)][0]
    srp = cells[insts[sr]['cell']]['ports']
    outs.sort(key=lambda n: [insts[sr]['pins'][p] for p in srp].index(n))
    def gt(net):
        return [[(m, t) for m in core_members for t, n in E(m)['terms'].items() if n == net and t != 'b']]
    inP, inN = E(ins[0])['terms']['g'], E(ins[1])['terms']['g']
    ck = E(clk)['terms']['g']
    tri(V, 'SA_CORE', 200, 210, 'SA', 'StrongARM core', ins=[(inP, -10, gt(inP)), (inN, 10, gt(inN))], outs=[(outs[0], -10, gt(outs[0])), (outs[1], 10, gt(outs[1]))],
        bottom=[(ck, 30, gt(ck), 'clock')], link='u_strongarm', members=core_members, clock_mark=True)
    V.wire([(110, 200), (180, 200)], cls='data'); V.port(inP, 110, 200, d='right', io='in')
    V.wire([(110, 220), (180, 220)], cls='data'); V.port(inN, 110, 220, d='right', io='in')
    V.wire([(230, 275), (230, 300)], cls='clock'); V.port(ck, 230, 300, d='up', io='in', cls='clock')
    srq = [p for p in srp if 'data' in CN[insts[sr]['cell']][p] and insts[sr]['pins'][p] not in outs]
    box(V, sr, 380, 160, 110, 100, insts[sr]['cell'], sr, left=[(srp[0], 200, inst_terms(sr, srp[0]), 'data'), (srp[1], 220, inst_terms(sr, srp[1]), 'data')],
        right=[(srq[0], 200, inst_terms(sr, srq[0]), 'data'), (srq[1], 220, inst_terms(sr, srq[1]), 'data')], link='b_sr', members=[sr])
    for k, n in enumerate(outs):
        y = 200 + 20 * k
        V.wire([(300, y), (360, y)], cls='data')
        V.netlabel(n, 330, y, tx=330, ty=y - 8 if k == 0 else y + 9, anchor='middle')
    invs = [i for i in insts if rl[i] == 'inverter']
    for k, (p, y, yi, up) in enumerate(((srq[0], 200, 140, True), (srq[1], 220, 280, False))):
        net = insts[sr]['pins'][p]
        V.wire([(510, y), (760, y)], cls='data'); V.port(net, 760, y, d='right', io='out')
        V.dot(560, y)
        V.wire([(560, y), (560, yi), (580, yi)], cls='data')
        iv = [i for i in invs if insts[i]['pins']['A'] == net][0]
        inv(V, iv, 600, yi, iv, inst_terms(iv, 'A'), inst_terms(iv, 'Y'), link='u_inv', members=[iv], flip_label=up)
        stub_label(V, {'x': 662, 'y': yi}, insts[iv]['pins']['Y'], 'right', L=30, side='above' if up else 'below')
    V.text(40, 370, '출력 버퍼 %s 의 출력은 연결 없음 (Q6)' % ', '.join(invs), size=10, color='#555', cls='note')
    V.omitted = hidden_list(cell)
    return V


def view_dff(cell):
    c = cells[cell]
    insts = [e for e in c['elems'] if e['kind'] == 'inst']
    cp = c['ports']
    sub = insts[0]['cell']; lp = cells[sub]['ports']
    lck = [p for p in lp if CN[sub][p] == ['clock']]
    lq = [p for p in lp if p not in lp[:2] and p not in lck and ('data' in CN[sub][p] or 'clock' in CN[sub][p])]
    # master = the one whose D pins are cell ports
    m_ = [e for e in insts if e['pins'][lp[0]] in cp][0]; s_ = [e for e in insts if e is not m_][0]
    V = new_view('b_dff', cell, 'block', '%s — 블록 레벨 (master-slave)' % cell, 760, 420)
    for e, x in ((m_, 200), (s_, 420)):
        box(V, e['name'], x, 160, 100, 100, 'LATCH', e['name'], left=[(lp[0], 200, inst_terms(e['name'], lp[0]), 'data'), (lp[1], 220, inst_terms(e['name'], lp[1]), 'data')],
            right=[(lq[0], 200, inst_terms(e['name'], lq[0]), 'data'), (lq[1], 220, inst_terms(e['name'], lq[1]), 'data')],
            bottom=[(lck[0], x + 30, inst_terms(e['name'], lck[0]), 'clock'), (lck[1], x + 70, inst_terms(e['name'], lck[1]), 'clock')], link='u_latch',
            members=[e['name']], sub=sub)
    V.wire([(110, 200), (180, 200)], cls='data'); V.port(m_['pins'][lp[0]], 110, 200, d='right', io='in')
    V.wire([(110, 220), (180, 220)], cls='data'); V.port(m_['pins'][lp[1]], 110, 220, d='right', io='in')
    V.wire([(320, 200), (400, 200)], cls='data'); V.netlabel(m_['pins'][lq[0]], 360, 200, tx=360, ty=192, anchor='middle')
    V.wire([(320, 220), (400, 220)], cls='data'); V.netlabel(m_['pins'][lq[1]], 360, 220, tx=360, ty=229, anchor='middle')
    V.wire([(540, 200), (620, 200)], cls='data'); V.port(s_['pins'][lq[0]], 620, 200, d='right', io='out')
    V.wire([(540, 220), (620, 220)], cls='data'); V.port(s_['pins'][lq[1]], 620, 220, d='right', io='out')
    # clocks: the net on the slave CLK pin is the trunk (wired); the other phase by labels
    ck = s_['pins'][lck[0]]; ckb = s_['pins'][lck[1]]
    xs = []
    for e, x in ((m_, 200), (s_, 420)):
        sm = [s for s in V.symbols if s['id'] == e['name']][0]
        for p in sm['pins']:
            if p['name'] in lck:
                if e['pins'][p['name']] == ck:
                    xs.append(p['x'])
                else:
                    stub_label(V, p, e['pins'][p['name']], 'down', cls='clock', L=20, side='left' if p['name'] == lck[0] else 'right')
    yT = 330
    V.wire([(150, yT), (max(xs), yT)], cls='clock')
    for x in xs:
        V.wire([(x, yT), (x, 280)], cls='clock')
        if x != max(xs):
            V.dot(x, yT)
    V.port(ck, 150, yT, d='right', io='in', cls='clock')
    V.wire([(150, 370), (190, 370)], cls='clock'); V.port(ckb, 150, 370, d='right', io='in', cls='clock')
    V.omitted = hidden_list(cell)
    return V


def view_sr(cell):
    c = cells[cell]
    insts = [e for e in c['elems'] if e['kind'] == 'inst']
    cp = c['ports']
    sub = insts[0]['cell']; gp = cells[sub]['ports']
    gin = [p for p in gp if 'data' in CN[sub][p]][:2]; gout = [p for p in gp if 'data' in CN[sub][p]][2]
    x1 = [e for e in insts if e['pins'][gin[0]] == cp[0]][0]; x2 = [e for e in insts if e is not x1][0]
    V = new_view('b_sr', cell, 'block', '%s — 블록 레벨 (교차 결합 게이트; 사전에 없음 → 박스)' % cell, 640, 420)
    # x1 on top (A upper, B lower); x2 mirrored (B upper, A lower)
    box(V, x1['name'], 250, 130, 90, 70, sub, x1['name'], left=[(gin[0], 150, inst_terms(x1['name'], gin[0]), 'data'), (gin[1], 180, inst_terms(x1['name'], gin[1]), 'data')],
        right=[(gout, 165, inst_terms(x1['name'], gout), 'data')], link='u_nand', members=[x1['name']])
    box(V, x2['name'], 250, 260, 90, 70, sub, x2['name'], left=[(gin[1], 280, inst_terms(x2['name'], gin[1]), 'data'), (gin[0], 310, inst_terms(x2['name'], gin[0]), 'data')],
        right=[(gout, 295, inst_terms(x2['name'], gout), 'data')], link='u_nand', members=[x2['name']])
    V.wire([(110, 150), (230, 150)], cls='data'); V.port(x1['pins'][gin[0]], 110, 150, d='right', io='in')
    V.wire([(110, 310), (230, 310)], cls='data'); V.port(x2['pins'][gin[0]], 110, 310, d='right', io='in')
    V.wire([(360, 165), (520, 165)], cls='data'); V.port(x1['pins'][gout], 520, 165, d='right', io='out')
    V.wire([(360, 295), (520, 295)], cls='data'); V.port(x2['pins'][gout], 520, 295, d='right', io='out')
    V.dot(400, 165); V.dot(400, 295)
    V.wire([(400, 165), (400, 215), (210, 245), (210, 280), (230, 280)], cls='data')
    V.wire([(400, 295), (400, 245), (210, 215), (210, 180), (230, 180)], cls='data')
    V.allowed_cross.append({'at': [305, 230], 'reason': 'cross-coupled X'})
    V.symmetry.append({'axis': 230, 'orient': 'h', 'pairs': [[x1['name'], x2['name']]], 'self': [], 'x0': 100, 'x1': 600, 'exempt_wires': []})
    V.omitted = hidden_list(cell)
    return V


# =====================================================================================
def main():
    top = A['top']
    B = A['block']
    G = A['groups']
    view_top(top)
    slice_cell = [e['cell'] for e in cells[top]['elems'] if e['kind'] == 'inst' and B[e['cell']]['role'] == 'composite' and 'important_control' in str(CN[e['cell']])][0]
    view_slice(slice_cell)
    clk_cell = [e['cell'] for e in cells[top]['elems'] if e['kind'] == 'inst' and B[e['cell']]['role'] == 'composite' and e['cell'] != slice_cell][0]
    view_clk(clk_cell)
    for c, b in B.items():
        if not INST.get(c):
            continue
        if b['role'] == 'ctle':
            view_ctle(c)
        elif b['role'] == 'vga':
            view_multipair(c, 'u_vga', 'vga')
        elif b['role'] == 'summer':
            view_multipair(c, 'u_summer', 'summer')
        elif b['role'] == 'latch':
            view_cml_latch(c)
        elif b['role'] == 'dff':
            view_dff(c)
        elif b['role'] == 'inverter':
            view_inv(c)
        elif b['role'] == 'static_cmos_gate':
            view_nand(c)
        elif b['role'] == 'cross_coupled_gates':
            view_sr(c)
    for c, gs in G.items():
        for g in gs:
            if g['role'] == 'strongarm':
                view_sa_block(c, g['members'])
                view_strongarm(c, g['members'])
            if g['role'] == 'cml_buffer' and B[c]['role'] == 'composite':
                view_cml_buffer(c, g['members'], 'u_clkbuf')
            if g['role'] == 'termination' and c != top:
                view_termination(c, g['members'], 'u_clkterm', '%s — unit level (클럭 입력 종단, 소자 그대로)' % c)
            if g['role'] == 'termination_esd':
                view_termination(c, g['members'], 'u_rxterm', '%s — unit level (입력 종단 + ESD, 소자 그대로)' % c)
        tgs = [g['members'] for g in gs if g['role'] == 'tg']
        if tgs:
            view_tg(c, tgs, 'u_tg')
    order_ids = ['b_top', 'b_slice', 'b_clk', 'u_rxterm', 'u_tg', 'u_ctle', 'u_vga', 'u_summer', 'b_sa', 'u_strongarm', 'b_sr', 'u_nand', 'u_inv',
                 'u_latch', 'b_dff', 'u_clkterm', 'u_clkbuf']
    vs = sorted(VIEWS, key=lambda v: order_ids.index(v.id) if v.id in order_ids else 99)
    out = []
    for v in vs:
        d = dict(v.__dict__)
        d.pop('_tid', None)
        out.append(d)
    json.dump(out, open(W + '/scenes.json', 'w'), indent=0, default=list, ensure_ascii=False)
    print('views:', [v.id for v in vs])


if __name__ == '__main__':
    main()
