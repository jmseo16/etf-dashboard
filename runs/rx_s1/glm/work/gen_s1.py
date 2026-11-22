"""gen_s1.py - views for exam circuit rx_s1 (dq_rx_unit). New code on top of hs.py / scene.py.
Usage: gen_s1.py <netlist> <workdir>"""
import json, sys, re, collections
from netlist import parse, fmt_si, Polarity
from hs import H, expand
import scene

NL, WD = sys.argv[1], sys.argv[2]
cells, order = parse(NL)
TOP = 'dq_rx_unit'
VIEWS = []
CONF = {'top': TOP, 'output_syms': {}, 'unused_ok': {}, 'extra_names': {}}
POL = Polarity(cells, TOP)


def new(vid, cell, level, title, w, h, scope=None):
    h_ = H(cells, vid, cell, level, title, w, h, scope)
    VIEWS.append(h_)
    return h_


def finish():
    out = []
    for h in VIEWS:
        h.done()
        d = dict(h.V.__dict__)
        d.pop('_tid', None)
        out.append(d)
    json.dump(out, open(WD + '/scenes.json', 'w'), indent=0, default=list, ensure_ascii=False)
    json.dump(CONF, open(WD + '/conf.json', 'w'), indent=0, ensure_ascii=False)
    print('views:', [v['id'] for v in out])


def pw(h, sym, pname, net, direction):
    p = h.pt(sym, pname)
    h.rail_pin(p[0], p[1], net, direction)


KO = {'general_control': '일반 제어 (K7 정적 트림)', 'bias': '바이어스 (K11)', 'power': '전원'}


def omit(h, nets, cls, why=None):
    for n in nets:
        h.V.omitted.append({'net': n, 'class': KO.get(cls, cls)})


# ---------------------------------------------------------------- static CMOS gate units
def view_inv(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (정적 CMOS 인버터)' % cell, 480, 420)
    e = h.el
    mp = [n for n, x in e.items() if x['type'] == 'p'][0]; mn = [n for n, x in e.items() if x['type'] == 'n'][0]
    a, y = e[mp]['terms']['g'], e[mp]['terms']['d']
    vdd, vss = e[mp]['terms']['s'], e[mn]['terms']['s']
    P = h.mos(mp, 240, 150, 'left', top='s'); N = h.mos(mn, 240, 250, 'left', top='d')
    pw(h, P, 'T', vdd, 'up'); pw(h, N, 'B', vss, 'down')
    h.port(a, 110, 200, 'right', 'in')
    h.port(y, 350, 200, 'right', 'out')
    h.auto(a, [h.pt(P, 'G'), h.pt(N, 'G'), (110, 200)])
    h.auto(y, [h.pt(P, 'B'), h.pt(N, 'T'), (350, 200)])
    return h


def view_nand(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (정적 CMOS NAND)' % cell, 560, 520)
    e = h.el
    ps = sorted([n for n, x in e.items() if x['type'] == 'p'], key=lambda n: cells[cell]['ports'].index(e[n]['terms']['g']))
    ns = [n for n, x in e.items() if x['type'] == 'n']
    y = e[ps[0]]['terms']['d']
    top = [n for n in ns if e[n]['terms']['d'] == y][0]; bot = [n for n in ns if n != top][0]
    vdd = e[ps[0]]['terms']['s']; vss = e[bot]['terms']['s']
    P0 = h.mos(ps[0], 200, 150, 'left', top='s'); P1 = h.mos(ps[1], 360, 150, 'right', top='s')
    N0 = h.mos(top, 280, 290, 'left', top='d'); N1 = h.mos(bot, 280, 390, 'right', top='d')
    pw(h, P0, 'T', vdd, 'up'); pw(h, P1, 'T', vdd, 'up'); pw(h, N1, 'B', vss, 'down')
    ga, gb = e[ps[0]]['terms']['g'], e[ps[1]]['terms']['g']
    h.port(y, 460, 215, 'right', 'out')
    h.port(ga, 100, 290, 'right', 'in')
    h.port(gb, 460, 390, 'left', 'in')
    h.auto(y, [h.pt(P0, 'B'), h.pt(P1, 'B'), h.pt(N0, 'T'), (460, 215)])
    h.auto(e[top]['terms']['s'], [h.pt(N0, 'B'), h.pt(N1, 'T')], cls='plain')
    h.auto(ga, [h.pt(P0, 'G'), h.pt(N0, 'G'), (100, 290)], dirs={})
    h.auto(gb, [h.pt(P1, 'G'), h.pt(N1, 'G'), (460, 390)])
    return h


def view_nor(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (정적 CMOS NOR)' % cell, 560, 520)
    e = h.el
    ps = sorted([n for n, x in e.items() if x['type'] == 'p'], key=lambda n: cells[cell]['ports'].index(e[n]['terms']['g']))
    ns = sorted([n for n, x in e.items() if x['type'] == 'n'], key=lambda n: cells[cell]['ports'].index(e[n]['terms']['g']))
    y = [x['terms']['d'] for n, x in e.items() if n in ns][0]
    vdd = e[ps[0]]['terms']['s']; vss = e[ns[0]]['terms']['s']
    mid = e[ps[0]]['terms']['d']
    # ps[0] top (source vdd), ps[1] below (source = mid, drain y)
    P0 = h.mos(ps[0], 280, 140, 'left', top='s'); P1 = h.mos(ps[1], 280, 240, 'right', top='s')
    N0 = h.mos(ns[0], 200, 370, 'left', top='d'); N1 = h.mos(ns[1], 360, 370, 'right', top='d')
    pw(h, P0, 'T', vdd, 'up'); pw(h, N0, 'B', vss, 'down'); pw(h, N1, 'B', vss, 'down')
    ga, gb = e[ps[0]]['terms']['g'], e[ps[1]]['terms']['g']
    h.port(y, 470, 310, 'right', 'out')
    h.port(ga, 100, 250, 'right', 'in')
    h.port(gb, 460, 160, 'left', 'in')
    h.auto(mid, [h.pt(P0, 'B'), h.pt(P1, 'T')], cls='plain')
    h.auto(y, [h.pt(P1, 'B'), h.pt(N0, 'T'), h.pt(N1, 'T'), (470, 310)])
    h.auto(ga, [h.pt(P0, 'G'), h.pt(N0, 'G'), (100, 250)])
    h.auto(gb, [h.pt(P1, 'G'), h.pt(N1, 'G'), (460, 160)])
    return h



def mos_pair_gate_ports(h, key, pts, port_xy, io='in', d='right', **kw):
    h.auto(key, pts + [port_xy], **kw)
    h.port(key, port_xy[0], port_xy[1], d, io)


# ---------------------------------------------------------------- level shifter (ls_lh)
def view_ls(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (레벨 시프터 vdd → vddq)' % cell, 760, 460)
    E = h.el
    P2 = h.mos('mp2', 120, 130, 'left', top='s'); N2 = h.mos('mn2', 120, 230, 'left', top='d')
    N0 = h.mos('mn0', 320, 330, 'left', top='d'); N1 = h.mos('mn1', 480, 330, 'right', top='d')
    P0 = h.mos('mp0', 320, 150, 'right', top='s'); P1 = h.mos('mp1', 480, 150, 'left', top='s')
    P3 = h.mos('mp3', 660, 150, 'left', top='s'); N3 = h.mos('mn3', 660, 250, 'left', top='d')
    pw(h, P2, 'T', 'vdd', 'up'); pw(h, N2, 'B', 'vss', 'down')
    for s_, n in ((P0, 'vddq'), (P1, 'vddq'), (P3, 'vddq')):
        pw(h, s_, 'T', n, 'up')
    for s_ in (N0, N1, N3):
        pw(h, s_, 'B', 'vss', 'down')
    # nb: mp0.d, mn0.d, mp1.g, mp3.g, mn3.g   nq: mp1.d mn1.d mp0.g   inb: mp2.d mn2.d mn1.g   in: mp2.g mn2.g mn0.g
    pn = {k: h.pt(v, p) for k, (v, p) in dict(P0B=(P0, 'B'), P0G=(P0, 'G'), P1B=(P1, 'B'), P1G=(P1, 'G'), N0T=(N0, 'T'), N0G=(N0, 'G'),
                                               N1T=(N1, 'T'), N1G=(N1, 'G'), P2B=(P2, 'B'), P2G=(P2, 'G'), N2T=(N2, 'T'), N2G=(N2, 'G'),
                                               P3G=(P3, 'G'), P3B=(P3, 'B'), N3G=(N3, 'G'), N3T=(N3, 'T')).items()}
    # core nodes (vertical wires) and the cross-coupled X
    h.manual('nb', [pn['P0B'], pn['N0T']])
    h.manual('nq', [pn['P1B'], pn['N1T']])
    h.manual('nb', [(320, 215), (400, 215), (400, 150), pn['P1G']])
    h.manual('nq', [(480, 195), (380, 195), (380, 150), pn['P0G']])
    CONF['allow_cross'] = CONF.get('allow_cross', {}); CONF['allow_cross'][vid] = 1
    h.port('in', 50, 180, 'right', 'in', label_side='above')
    h.port('out', 700, 200, 'right', 'out')
    h.auto('nb', [pn['P3G'], pn['N3G'], (400, 215)], name='nb')
    h.auto('inb', [pn['P2B'], pn['N2T'], pn['N1G']], name='inb')
    h.auto('in', [pn['P2G'], pn['N2G'], pn['N0G'], (50, 180)], name='in')
    h.auto('out', [pn['P3B'], pn['N3T'], (700, 200)])
    return h


# ---------------------------------------------------------------- ESD cell
def view_esd(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (입력 ESD: 다이오드 클램프 + 직렬 R + GGNMOS)' % cell, 700, 520)
    D0 = h.diode('d0', 150, 150, flip=True); D1 = h.diode('d1', 210, 350, flip=True)
    R0 = h.res('r0', 270, 250, 'h', label_side='above')
    D2 = h.diode('d2', 340, 150, flip=True); D3 = h.diode('d3', 400, 350, flip=True)
    M = h.mos('mn0', 520, 350, 'left', top='d'); R1 = h.res('r1', 480, 440, 'v', label_side='right')
    for s_, n in ((D0, 'vddq'), (D2, 'vddq')):
        pw(h, s_, 'K', n, 'up')
    for s_, n in ((D1, 'vssq'), (D3, 'vssq')):
        pw(h, s_, 'A', n, 'down')
    pw(h, M, 'B', 'vssq', 'down'); pw(h, R1, 'B', 'vssq', 'down')
    h.port('pad', 60, 250, 'right', 'in')
    h.port('pad_r', 610, 250, 'right', 'out')
    h.auto('pad', [h.pt(D0, 'A'), h.pt(D1, 'K'), h.pt(R0, 'A'), (60, 250)], name='pad')
    h.auto('pad_r', [h.pt(D2, 'A'), h.pt(D3, 'K'), h.pt(R0, 'B'), h.pt(M, 'T'), (610, 250)], name='pad_r')
    h.auto('net9', [h.pt(M, 'G'), h.pt(R1, 'A')], name='net9')
    return h


# ---------------------------------------------------------------- ODT pull-up legs
def view_odt(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (ODT 풀업 다리 3개: PMOS 스위치 + 직렬 R, 이진 가중)' % cell, 980, 520)
    xs = [230, 500, 770]
    legs = [('mp2', 'r2', 'enb<2>'), ('mp1', 'r1', 'enb<1>'), ('mp0', 'r0', 'enb<0>')]
    pins = []
    for x, (m, r, en) in zip(xs, legs):
        h.port(en, x - 130, 150, 'right', 'in')
    h.port('pad', 900, 380, 'left', 'in')
    for x, (m, r, en) in zip(xs, legs):
        P = h.mos(m, x, 150, 'left', top='s'); Rr = h.res(r, x, 270, 'v', label_side='right')
        pw(h, P, 'T', 'vddq', 'up')
        net = h.el[m]['terms']['d']
        h.auto(net, [h.pt(P, 'B'), h.pt(Rr, 'A')], cls='plain')
        h.auto(en, [h.pt(P, 'G'), (x - 130, 150)], name=en)
        pins.append(h.pt(Rr, 'B'))
    h.auto('pad', pins + [(900, 380)], name='pad')
    return h


# ---------------------------------------------------------------- vref RC filter (virtual block of the top cell)
def view_lpf(vid):
    h = new(vid, TOP, 'unit', '%s — unit level (기준 전압 RC 필터: r0 + MOS 커패시터 mn0)' % TOP, 620, 380, scope=['r0', 'mn0'])
    R0 = h.res('r0', 250, 190, 'h', label_side='above')
    # MOS used as a capacitor (gate = net3, drain = source = vssq): drawn as a plain capacitor symbol
    sym = scene.cap(h.V, 'mn0', 400, 280, 'v', name='mn0', size=h.size_of(h.el['mn0']) + ' (MOS C)', a=[[('mn0', 'g')]], b=[[('mn0', 'd')]], members=['mn0'])
    sym['info']['concept'] = True
    h.reg(sym)
    pw(h, sym, 'B', 'vssq', 'down')
    h.port('vref', 70, 190, 'right', 'in')
    h.port('net3', 540, 190, 'right', 'out')
    h.auto('vref', [h.pt(R0, 'A'), (70, 190)], name='vref')
    h.auto('net3', [h.pt(R0, 'B'), h.pt(sym, 'A'), (540, 190)], name='net3')
    h.V.notes.append('mn0 은 게이트(net3)–드레인=소스(vssq)로 묶인 MOS 커패시터이므로 커패시터 기호로 그림 (명세서에 MOS 커패시터 규칙 없음 — 질문 Q6)')
    return h



# ---------------------------------------------------------------- rx_pre: R-load pseudo-differential amp with a loopback pair
def view_rx_pre(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (R 부하 의사 차동 증폭기 + 루프백 입력쌍)' % cell, 900, 900)
    M4 = h.mos('mn4', 230, 300, 'left', top='d'); M0 = h.mos('mn0', 370, 300, 'right', top='d')
    M1 = h.mos('mn1', 510, 300, 'left', top='d'); M5 = h.mos('mn5', 650, 300, 'right', top='d')
    R0 = h.res('r0', 300, 150, 'v', label_side='left'); R1 = h.res('r1', 580, 150, 'v', label_side='right')
    pw(h, R0, 'A', 'vddq', 'up'); pw(h, R1, 'A', 'vddq', 'up')
    M2 = h.mos('mn2', 440, 430, 'left', top='d'); M3 = h.mos('mn3', 440, 530, 'left', top='d')
    M6 = h.mos('mn6', 440, 690, 'left', top='d'); M7 = h.mos('mn7', 440, 790, 'left', top='d')
    pw(h, M3, 'B', 'vssq', 'down'); pw(h, M7, 'B', 'vssq', 'down')
    # MOS capacitors (gate -> drain=source) drawn as capacitor symbols
    C8 = scene.cap(h.V, 'mn8', 760, 500, 'v', name='mn8', size=h.size_of(h.el['mn8']) + ' (MOS C)', a=[[('mn8', 'g')]], b=[[('mn8', 'd')]], members=['mn8'])
    C9 = scene.cap(h.V, 'mn9', 140, 500, 'v', name='mn9', size=h.size_of(h.el['mn9']) + ' (MOS C)', a=[[('mn9', 'g')]], b=[[('mn9', 'd')]], members=['mn9'])
    for c in (C8, C9):
        c['info']['concept'] = True; h.reg(c)
    h.port('outn', 110, 220, 'left', 'out')
    h.port('outp', 800, 220, 'right', 'out')
    h.port('inp', 410, 140, 'down', 'in')
    h.port('vref', 470, 140, 'down', 'in')
    h.port('lbp', 110, 300, 'right', 'in')
    h.port('lbn', 790, 300, 'left', 'in')
    h.port('sel_m', 300, 430, 'right', 'in')
    h.port('sel_l', 300, 690, 'right', 'in')
    h.auto('outn', [h.pt(R0, 'B'), h.pt(M4, 'T'), h.pt(M0, 'T'), h.pt(C9, 'B'), (110, 220)], name='outn')
    h.auto('outp', [h.pt(R1, 'B'), h.pt(M1, 'T'), h.pt(M5, 'T'), h.pt(C8, 'B'), (800, 220)], name='outp')
    h.auto('net40', [h.pt(M0, 'B'), h.pt(M1, 'B'), h.pt(M2, 'T')], cls='plain')
    h.auto('net41', [h.pt(M2, 'B'), h.pt(M3, 'T')], cls='plain')
    h.auto('net42', [h.pt(M4, 'B'), h.pt(M5, 'B'), h.pt(M6, 'T')], cls='plain')
    h.auto('net43', [h.pt(M6, 'B'), h.pt(M7, 'T')], cls='plain')
    h.auto('inp', [h.pt(M0, 'G'), h.pt(C8, 'A'), (410, 140)], name='inp', dirs={h.pt(M0, 'G'): ['down']})
    h.auto('vref', [h.pt(M1, 'G'), h.pt(C9, 'A'), (470, 140)], name='vref', dirs={h.pt(M1, 'G'): ['down']})
    h.auto('lbp', [h.pt(M4, 'G'), (110, 300)], name='lbp')
    h.auto('lbn', [h.pt(M5, 'G'), (790, 300)], name='lbn')
    h.auto('sel_m', [h.pt(M2, 'G'), (300, 430)], name='sel_m')
    h.auto('sel_l', [h.pt(M6, 'G'), (300, 690)], name='sel_l')
    h.gray(h.pt(M3, 'G'), 'left', 'vbn'); h.gray(h.pt(M7, 'G'), 'left', 'vbn')
    omit(h, ['vbn'], 'bias')
    h.V.notes.append('비대칭: mn8/mn9 는 D=S 묶음 MOS 커패시터 — inp→outp, vref→outn 으로 서로 교차 (netlist 대로, 질문 Q7)')
    return h



def varcap_sym(h, sid, x, y, orient, a_term, b_term, members, name, size=''):
    sym = scene.cap(h.V, sid, x, y, orient, name=name, size=size, a=[[a_term]], b=[[b_term]], members=members, var=True)
    sym['info']['concept'] = True
    return h.reg(sym)


# ---------------------------------------------------------------- dfe_sum: summer (main pair + feedback pair + sign steering + tap DAC)
def view_dfe_sum(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (Σ: 주 입력쌍 + 귀환 탭쌍, 부호 선택, 탭 전류 DAC)' % cell, 1120, 760)
    M0 = h.mos('mn0', 230, 320, 'left', top='d'); M1 = h.mos('mn1', 390, 320, 'left', top='d')
    R0 = h.res('r0', 230, 170, 'v', label_side='left'); R1 = h.res('r1', 390, 170, 'v', label_side='right')
    pw(h, R0, 'A', 'vdd', 'up'); pw(h, R1, 'A', 'vdd', 'up')
    M2 = h.mos('mn2', 310, 450, 'left', top='d'); M3 = h.mos('mn3', 310, 560, 'left', top='d')
    pw(h, M3, 'B', 'vss', 'down')
    M8 = h.mos('mn8', 540, 320, 'left', top='d'); M6 = h.mos('mn6', 620, 320, 'right', top='d')
    M7 = h.mos('mn7', 780, 320, 'left', top='d'); M9 = h.mos('mn9', 860, 320, 'right', top='d')
    M4 = h.mos('mn4', 580, 470, 'left', top='d'); M5 = h.mos('mn5', 820, 470, 'right', top='d')
    D = h.V
    vs = scene.visrc(D, 'X_DAC<3:0>', 700, 610, name='X_DAC<3:0>', size='', top=[[('mn10', 'd')]], bot=[[('mn11', 's')]],
                     bus=[[('mn10', 'g')], [('mn12', 'g')], [('mn14', 'g')], [('mn16', 'g')]], bus_side='right',
                     members=['mn10', 'mn11', 'mn12', 'mn13', 'mn14', 'mn15', 'mn16', 'mn17'], label_side='left')
    vs['info']['concept'] = True; h.reg(vs)
    pw(h, vs, 'B', 'vss', 'down')
    # ports first
    h.port('inp', 90, 320, 'right', 'in'); h.port('inn', 350, 120, 'down', 'in')
    h.port('en', 150, 450, 'right', 'in'); h.port('hp', 460, 470, 'right', 'in'); h.port('hn', 980, 470, 'left', 'in')
    h.port('sgnb', 700, 170, 'down', 'in'); h.port('sgn', 1020, 320, 'left', 'in')
    h.port('tap<3:0>', 1030, 610, 'left', 'in')
    h.port('outn', 110, 230, 'left', 'out'); h.port('outp', 1060, 230, 'right', 'out')
    h.auto('inp', [h.pt(M0, 'G'), (90, 320)], name='inp')
    h.auto('inn', [h.pt(M1, 'G'), (350, 120)], name='inn')
    h.auto('en', [h.pt(M2, 'G'), (150, 450)], name='en')
    h.auto('hp', [h.pt(M4, 'G'), (460, 470)], name='hp'); h.auto('hn', [h.pt(M5, 'G'), (980, 470)], name='hn')
    h.auto('sgnb', [h.pt(M6, 'G'), h.pt(M7, 'G'), (700, 170)], name='sgnb')
    h.auto('sgn', [h.pt(M8, 'G'), h.pt(M9, 'G'), (1020, 320)], name='sgn')
    h.auto('tap<3:0>', [h.pt(vs, 'BUS'), (1030, 610)], name='tap<3:0>', cls='bus')
    h.V.line([(936, 617), (950, 603)], w=1.4, owner='bus')
    h.auto('net50', [h.pt(M0, 'B'), h.pt(M1, 'B'), h.pt(M2, 'T')], cls='plain')
    h.auto('net51', [h.pt(M2, 'B'), h.pt(M3, 'T')], cls='plain')
    h.auto('net52', [h.pt(M8, 'B'), h.pt(M6, 'B'), h.pt(M4, 'T')], cls='plain')
    h.auto('net53', [h.pt(M7, 'B'), h.pt(M9, 'B'), h.pt(M5, 'T')], cls='plain')
    h.auto('net54', [h.pt(M4, 'B'), h.pt(M5, 'B'), h.pt(vs, 'T')], cls='plain')
    h.auto('outn', [h.pt(R0, 'B'), h.pt(M0, 'T'), h.pt(M8, 'T'), h.pt(M7, 'T'), (110, 230)], name='outn')
    h.auto('outp', [h.pt(R1, 'B'), h.pt(M1, 'T'), h.pt(M6, 'T'), h.pt(M9, 'T'), (1060, 230)], name='outp')
    h.gray(h.pt(M3, 'G'), 'left', 'vbn')
    omit(h, ['vbn'], 'bias')
    h.V.notes.append('탭 DAC: 전류원 8개 (스위치 mn10/12/14/16 + 꼬리 mn11/13/15/17)를 가변 전류원 X_DAC<3:0> 하나로 묶음. 범례: mn10..mn17 = 스위치 W 400n L 30n m 8/4/2/1, 꼬리 W 1u L 240n m 8/4/2/1')
    return h


# ---------------------------------------------------------------- sa_dt virtual blocks
def view_sa1(vid):
    scope = ['mn0', 'mn1', 'mn2', 'mp0', 'mp1', 'mn7', 'mn8', 'mn9', 'mn10', 'mn11', 'mn12', 'mn13', 'mn14']
    h = new(vid, 'sa_dt', 'unit', 'sa_dt — unit level (double-tail 1단: 입력쌍 + 클럭 꼬리 + 리셋 + 오프셋 C 뱅크)', 900, 700, scope=scope)
    M1 = h.mos('mn1', 350, 330, 'left', top='d'); M2 = h.mos('mn2', 550, 330, 'right', top='d')
    P0 = h.mos('mp0', 350, 190, 'left', top='s'); P1 = h.mos('mp1', 550, 190, 'right', top='s')
    M0 = h.mos('mn0', 450, 480, 'left', top='d')
    pw(h, P0, 'T', 'vdd', 'up'); pw(h, P1, 'T', 'vdd', 'up'); pw(h, M0, 'B', 'vss', 'down')
    C62 = varcap_sym(h, 'C_OF_N', 230, 265, 'h', ('mn8', 'd'), ('mn7', 'd'), ['mn7', 'mn8', 'mn9', 'mn10'], 'C_OF_N')
    C63 = varcap_sym(h, 'C_OF_P', 670, 265, 'h', ('mn11', 's'), ('mn13', 's'), ['mn11', 'mn12', 'mn13', 'mn14'], 'C_OF_P')
    # concept symbol C_OF_P: A side should be net63. use mn11.d (net63): fix terms below
    C63['pins'][0]['terms'] = [[('mn11', 'd')]]; C63['pins'][1]['terms'] = [[('mn12', 'd')]]
    pw(h, C62, 'A', 'vss', 'down'); pw(h, C63, 'B', 'vss', 'down')
    h.port('inp', 150, 330, 'right', 'in'); h.port('inn', 750, 330, 'left', 'in'); h.port('ck', 330, 560, 'right', 'in')
    h.offpage('net62', 100, 190, 'left'); h.offpage('net63', 800, 190, 'right')
    h.auto('net61', [h.pt(M1, 'B'), h.pt(M2, 'B'), h.pt(M0, 'T')], cls='plain')
    h.auto('net62', [h.pt(P0, 'B'), h.pt(M1, 'T'), h.pt(C62, 'B'), (100, 190)], name='net62')
    h.auto('net63', [h.pt(P1, 'B'), h.pt(M2, 'T'), h.pt(C63, 'A'), (800, 190)], name='net63')
    h.auto('inp', [h.pt(M1, 'G'), (150, 330)], name='inp'); h.auto('inn', [h.pt(M2, 'G'), (750, 330)], name='inn')
    h.auto('ck', [h.pt(M0, 'G'), h.pt(P0, 'G'), h.pt(P1, 'G'), (330, 560)], name='ck')
    omit(h, ['ofn<1>', 'ofn<0>', 'ofp<1>', 'ofp<0>'], 'general_control')
    h.V.notes.append('C_OF_N / C_OF_P: 스위치(mn7/mn9, mn11/mn13)와 MOS 커패시터(mn8/mn10, mn12/mn14)를 묶은 가변 C. 범례: C_OF_N = mn7+mn8 (W 200n/400n, m 2) ∥ mn9+mn10 (m 1), C_OF_P = mn11+mn12 (m 2) ∥ mn13+mn14 (m 1)')
    return h


def view_sa2(vid):
    scope = ['mp2', 'mp3', 'mp4', 'mn3', 'mn4', 'mn5', 'mn6']
    h = new(vid, 'sa_dt', 'unit', 'sa_dt — unit level (double-tail 2단: 교차 결합 래치 + 헤더 + 1단 출력 입력)', 900, 640, scope=scope)
    P2 = h.mos('mp2', 450, 130, 'left', top='s')
    P3 = h.mos('mp3', 330, 280, 'right', top='s'); P4 = h.mos('mp4', 570, 280, 'left', top='s')
    N3 = h.mos('mn3', 330, 400, 'right', top='d'); N4 = h.mos('mn4', 570, 400, 'left', top='d')
    N5 = h.mos('mn5', 210, 400, 'left', top='d'); N6 = h.mos('mn6', 690, 400, 'right', top='d')
    pw(h, P2, 'T', 'vdd', 'up')
    for m in (N3, N4, N5, N6):
        pw(h, m, 'B', 'vss', 'down')
    h.port('net60', 330, 130, 'right', 'in')
    h.port('outp', 90, 340, 'left', 'out'); h.port('outn', 810, 340, 'right', 'out')
    h.offpage('net62', 100, 400, 'left'); h.offpage('net63', 800, 400, 'right')
    h.auto('net60', [h.pt(P2, 'G'), (330, 130)], name='net60')
    h.auto('net64', [h.pt(P2, 'B'), h.pt(P3, 'T'), h.pt(P4, 'T')], cls='plain')
    h.auto('outp', [h.pt(P3, 'B'), h.pt(N3, 'T'), h.pt(N5, 'T'), h.pt(P4, 'G'), h.pt(N4, 'G'), (90, 340)], name='outp')
    h.auto('outn', [h.pt(P4, 'B'), h.pt(N4, 'T'), h.pt(N6, 'T'), h.pt(P3, 'G'), h.pt(N3, 'G'), (810, 340)], name='outn')
    h.auto('net62', [h.pt(N5, 'G'), (100, 400)], name='net62'); h.auto('net63', [h.pt(N6, 'G'), (800, 400)], name='net63')
    return h



# ================================================================ block-level helpers
def T(inst, port):
    return [[(inst, port)]]


def Tbus(inst, ports):
    return [[(inst, p)] for p in ports]


def set_pol(sym, h, ins, outs, logic=None):
    """record what the checker must compare: main input net(s) and output (pin, net) in drawn order"""
    inst = h.el[sym['members'][0]]
    sym['info']['pol'] = {'ins': ins, 'outs': [n for _, n in outs], 'outpins': [p for p, _ in outs], 'logic': logic if logic is not None else [p for p, _ in outs]}


def gate_box(h, inst, x0, y0, ins, outs, w=100, hh=None, link=None, label=None, bubble=True, sub=None):
    """logic cell box. ins: [(port, net)] ; outs: [(port, net)]. pin y spacing 30"""
    cell = h.el[inst]['cell']
    n = max(len(ins), len(outs))
    hh = hh or max(70, 30 * len(ins) + 20)
    left = [(p, y0 + 25 + 30 * k, T(inst, p), 'data') for k, (p, _) in enumerate(ins)]
    mid = y0 + hh / 2
    right = [(p, mid if len(outs) == 1 else y0 + 25 + 30 * k, T(inst, p), 'data') for k, (p, _) in enumerate(outs)]
    pol = POL.outputs(cell, [n for _, n in ins[:1]] if len(ins) < 2 else [h.el[inst]['pins'][ins[0][0]], h.el[inst]['pins'][ins[1][0]]],
                      [h.el[inst]['pins'][p] for p, _ in outs]) if False else None
    sym = h.box(inst, x0, y0, w, hh, label or cell, inst, left=left, right=right, link=link, members=[inst], sub=sub)
    return sym


def inst_pol(h, inst, in_ports, out_ports):
    """bubble set from the netlist polarity of the instance's cell (main input = first of in_ports)"""
    cell = h.el[inst]['cell']
    r = POL.outputs(cell, in_ports, out_ports)
    return {p for p in out_ports if r.get(p) == 'inv'}


def draw_inst_box(h, inst, x0, y0, left, right, w=100, hh=None, label=None, link=None, sub=None, top=None, bottom=None, pcls=None,
                  main_in=None, logic_out=True, bus_pins=()):
    """generic instance box. left/right: [(port, ycoord)]; top/bottom [(port, xcoord)].
    Bubbles come from the cell polarity (main_in = list of cell ports), recorded for the checker."""
    cell = h.el[inst]['cell']
    mi = main_in if main_in is not None else [p for p, _ in left[:1]]
    outs = [p for p, _ in right]
    res = POL.outputs(cell, mi, outs) if (mi and outs and logic_out) else {}
    bub = tuple(p for p in outs if res.get(p) == 'inv')
    L = [(p, y, T(inst, p), 'data') for p, y in left]
    Rr = [(p, y, T(inst, p), 'data') for p, y in right]
    Tp = [(p, x, T(inst, p), 'bus' if p in bus_pins else 'data') for p, x in (top or [])]
    Bt = [(p, x, T(inst, p), 'clock') for p, x in (bottom or [])]
    hh = hh or max(70, 20 + 30 * max(len(left), len(right)))
    sym = h.box(inst, x0, y0, w, hh, label or cell, inst, left=L, right=Rr, top=Tp, bottom=Bt, link=link, members=[inst], sub=sub if sub else (cell if label else None), bubbles=bub)
    sym['info']['pol'] = {'ins': mi, 'outs': outs, 'outpins': outs, 'logic': outs if logic_out else []}
    sym['info']['pcls'] = pcls or {}
    sym['info']['gate'] = True
    return sym


def inv_inst(h, inst, x0, yc, link=None):
    cell = h.el[inst]['cell']
    pins = h.el[inst]['pins']
    sym = h.inv(inst, x0, yc, inst, T(inst, 'a'), T(inst, 'y'), link=link, members=[inst])
    sym['pins'][0]['name'] = 'a'; sym['pins'][1]['name'] = 'y'
    for p in h.pins:
        if p['sym'] == inst:
            p['name'] = {'A': 'a', 'Y': 'y'}.get(p['name'], p['name'])
    sym['info']['pol'] = {'ins': ['a'], 'outs': ['y'], 'outpins': ['y'], 'logic': ['y']}
    sym['pins'][0]['side'] = 'left'; sym['pins'][1]['side'] = 'right'
    for p in h.pins:
        if p['sym'] == inst:
            p['side'] = 'left' if p['name'] == 'a' else 'right'
    sym['info']['pcls'] = {'a': 'data_in', 'y': 'data_out'}
    return sym


# ---------------------------------------------------------------- b_sr_nor
def view_b_sr(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (교차 결합 NOR2)' % cell, 700, 520)
    x0 = 270
    g0 = draw_inst_box(h, 'xi0', x0, 110, [('a', 135), ('b', 165)], [('y', 150)], w=110, hh=80, link='u_nor2_c', pcls={'a': 'data_in', 'b': 'data_in', 'y': 'data_out'}, main_in=['a'])
    g1 = draw_inst_box(h, 'xi1', x0, 330, [('a', 355), ('b', 385)], [('y', 370)], w=110, hh=80, link='u_nor2_c', pcls={'a': 'data_in', 'b': 'data_in', 'y': 'data_out'}, main_in=['a'])
    h.port('r', 130, 135, 'right', 'in'); h.port('s', 130, 355, 'right', 'in')
    h.port('q', 580, 150, 'right', 'out'); h.port('qb', 580, 370, 'right', 'out')
    h.auto('r', [h.pt(g0, 'a'), (130, 135)]); h.auto('s', [h.pt(g1, 'a'), (130, 355)])
    h.auto('q', [h.pt(g0, 'y'), h.pt(g1, 'b'), (580, 150)])
    h.auto('qb', [h.pt(g1, 'y'), h.pt(g0, 'b'), (580, 370)])
    omit(h, ['vdd', 'vss'], 'power')
    return h


# ---------------------------------------------------------------- b_ck_gbuf
def view_b_ckg(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (클럭 게이트 + 버퍼)' % cell, 820, 560)
    g0 = draw_inst_box(h, 'xi0', 280, 110, [('a', 135), ('b', 165)], [('y', 150)], w=100, hh=80, link='u_nand2_c', main_in=['a'], pcls={'a': 'data_in', 'b': 'control', 'y': 'data_out'})
    g1 = draw_inst_box(h, 'xi1', 280, 340, [('a', 365), ('b', 395)], [('y', 380)], w=100, hh=80, link='u_nand2_c', main_in=['a'], pcls={'a': 'data_in', 'b': 'control', 'y': 'data_out'})
    i2 = inv_inst(h, 'xi2', 500, 150, link='u_inv_c'); i3 = inv_inst(h, 'xi3', 500, 380, link='u_inv_c')
    h.port('ck', 120, 135, 'right', 'in'); h.port('ckb', 120, 365, 'right', 'in'); h.port('en', 120, 250, 'right', 'in')
    h.port('cko', 700, 150, 'right', 'out'); h.port('ckob', 700, 380, 'right', 'out')
    h.auto('ck', [h.pt(g0, 'a'), (120, 135)]); h.auto('ckb', [h.pt(g1, 'a'), (120, 365)])
    h.auto('en', [h.pt(g0, 'b'), h.pt(g1, 'b'), (120, 250)])
    h.auto('net70', [h.pt(g0, 'y'), h.pt(i2, 'a')]); h.auto('net71', [h.pt(g1, 'y'), h.pt(i3, 'a')])
    h.auto('cko', [h.pt(i2, 'y'), (700, 150)]); h.auto('ckob', [h.pt(i3, 'y'), (700, 380)])
    omit(h, ['vdd', 'vss'], 'power')
    return h


# ---------------------------------------------------------------- b_odt_dec
def view_b_odtdec(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (ODT 디코더: NAND + 레벨 시프터, 3줄)' % cell, 900, 700)
    rows = [('xi2', 'xi5', 'rtt<2>', 'net20', 'enb<2>'), ('xi1', 'xi4', 'rtt<1>', 'net21', 'enb<1>'), ('xi0', 'xi3', 'rtt<0>', 'net22', 'enb<0>')]
    nandpins = {}
    ps = []
    for k, (nd, ls, rt, mid, en) in enumerate(rows):
        y0 = 120 + 190 * k
        g = draw_inst_box(h, nd, 280, y0, [('a', y0 + 25), ('b', y0 + 55)], [('y', y0 + 40)], w=100, hh=80, link='u_nand2_a', main_in=['b'],
                          pcls={'a': 'control', 'b': 'control', 'y': 'data_out'})
        l = draw_inst_box(h, ls, 500, y0 + 5, [('in', y0 + 40)], [('out', y0 + 40)], w=80, hh=70, link='u_ls_lh', label='LS', main_in=['in'],
                          pcls={'in': 'control', 'out': 'control'}, sub=None)
        h.port(rt, 130, y0 + 55, 'right', 'in'); h.port(en, 760, y0 + 40, 'right', 'out')
        ps.append((g, l, rt, mid, en, y0))
    h.port('odt_en', 130, 90, 'right', 'in')
    h.auto('odt_en', [h.pt(g, 'a') for g, *_ in ps] + [(130, 90)], name='odt_en')
    for g, l, rt, mid, en, y0 in ps:
        h.auto(rt, [h.pt(g, 'b'), (130, y0 + 55)], name=rt)
        h.auto(mid, [h.pt(g, 'y'), h.pt(l, 'in')], name=mid)
        h.auto(en, [h.pt(l, 'out'), (760, y0 + 40)], name=en)
    omit(h, ['vdd', 'vddq', 'vss'], 'power')
    return h


# ---------------------------------------------------------------- b_sa_dt
def view_b_sa(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (double-tail 비교기)' % cell, 1000, 560)
    s1 = h.box('S1', 280, 110, 150, 160, 'stage1', None, left=[('inp', 150, [[('mn1', 'g')]], 'data'), ('inn', 230, [[('mn2', 'g')]], 'data')],
               right=[('net62', 150, [[('mp0', 'd')]], 'data'), ('net63', 230, [[('mp1', 'd')]], 'data')],
               bottom=[('ck', 355, [[('mn0', 'g')]], 'clock')], link='u_sa_dt_stage1', members=['mn0', 'mn1', 'mn2', 'mp0', 'mp1', 'mn7', 'mn8', 'mn9', 'mn10', 'mn11', 'mn12', 'mn13', 'mn14'], sub='sa_dt 1단')
    s2 = h.box('S2', 650, 110, 150, 160, 'stage2', None, left=[('net62', 150, [[('mn5', 'g')]], 'data'), ('net63', 230, [[('mn6', 'g')]], 'data')],
               right=[('outp', 150, [[('mn3', 'd')]], 'data'), ('outn', 230, [[('mn4', 'd')]], 'data')],
               bottom=[('net60', 725, [[('mp2', 'g')]], 'clock')], link='u_sa_dt_stage2', members=['mp2', 'mp3', 'mp4', 'mn3', 'mn4', 'mn5', 'mn6'], bubbles=('outp', 'outn'), sub='sa_dt 2단')
    for sy in (s1, s2):
        sy['info']['virtual'] = True
    s1['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'net62': 'data_out', 'net63': 'data_out', 'ck': 'clock'}
    s2['info']['pcls'] = {'net62': 'data_in', 'net63': 'data_in', 'outp': 'data_out', 'outn': 'data_out', 'net60': 'clock'}
    i0 = inv_inst(h, 'xi0', 500, 440, link='u_inv_c')
    h.port('inp', 100, 150, 'right', 'in'); h.port('inn', 100, 230, 'right', 'in'); h.port('ck', 100, 440, 'right', 'in')
    h.port('outp', 930, 150, 'right', 'out'); h.port('outn', 930, 230, 'right', 'out')
    h.auto('net62', [h.pt(s1, 'net62'), h.pt(s2, 'net62')]); h.auto('net63', [h.pt(s1, 'net63'), h.pt(s2, 'net63')])
    h.auto('inp', [h.pt(s1, 'inp'), (100, 150)]); h.auto('inn', [h.pt(s1, 'inn'), (100, 230)])
    h.auto('outp', [h.pt(s2, 'outp'), (930, 150)]); h.auto('outn', [h.pt(s2, 'outn'), (930, 230)])
    h.auto('ck', [h.pt(s1, 'ck'), h.pt(i0, 'a'), (100, 440)], cls='clock')
    h.auto('net60', [h.pt(i0, 'y'), h.pt(s2, 'net60')], cls='clock')
    omit(h, ['ofn<1>', 'ofn<0>', 'ofp<1>', 'ofp<0>'], 'general_control'); omit(h, ['vdd', 'vss'], 'power')
    return h



# ================================================================ top block view
def view_top(vid):
    h = new(vid, TOP, 'block', '%s — 블록 레벨 (최상위)' % TOP, 1780, 1200)
    # ---- ports (fixed points first, so the router treats them as obstacles)
    P = dict(pad=(110, 470), vref=(110, 560), lb_p=(110, 620), lb_n=(110, 660), odt_en=(110, 195), **{'rtt<2:0>': (110, 235)},
             lb_en=(110, 85), rx_en=(110, 130), tap_sgn=(960, 100), ck=(110, 1030), ckb=(110, 1070), dout_e=(1650, 380), dout_o=(1650, 770))
    h.port('pad', *P['pad'], 'right', 'in'); h.port('vref', *P['vref'], 'right', 'in')
    h.port('lb_p', *P['lb_p'], 'right', 'in'); h.port('lb_n', *P['lb_n'], 'right', 'in')
    h.port('odt_en', *P['odt_en'], 'right', 'in'); h.port('rtt<2:0>', *P['rtt<2:0>'], 'right', 'in')
    h.port('lb_en', *P['lb_en'], 'right', 'in'); h.port('rx_en', *P['rx_en'], 'right', 'in')
    h.port('tap_sgn', *P['tap_sgn'], 'right', 'in')
    h.port('ck', *P['ck'], 'right', 'in'); h.port('ckb', *P['ckb'], 'right', 'in')
    h.port('dout_e', *P['dout_e'], 'right', 'out'); h.port('dout_o', *P['dout_o'], 'right', 'out')
    h.port('tap<3:0>', 815, 100, 'down', 'in')
    # ---- data path
    esd = h.box('xi20', 310, 430, 90, 80, 'ESD', 'xi20', left=[('pad', 470, T('xi20', 'pad'), 'data')], right=[('pad_r', 470, T('xi20', 'pad_r'), 'data')],
                link='u_esd_dq', members=['xi20'], sub='esd_dq')
    esd['info']['pcls'] = {'pad': 'data_in', 'pad_r': 'data_out'}
    od = scene.res(h.V, 'xi21', 240, 380, 'v', name='xi21', size='', a=None, b=[[('xi21', 'pad')]], members=['xi21'], var=True)
    od['info']['concept'] = True
    h.V.line([(246, 390), (286, 390)], w=1.6, owner='xi21')
    od['pins'].append(scene.pin('enb<2:0>', 286, 390, Tbus('xi21', ['enb<2>', 'enb<1>', 'enb<0>'])))
    h.V.circle(240, 347, 3, fill='#fff', owner='xi21')
    h.reg(od)
    h.V.hot.append({'x': 215, 'y': 345, 'w': 85, 'h': 70, 'link': 'u_odt_pu', 'sym': 'xi21'})
    dec = h.box('xi22', 220, 170, 130, 100, 'DEC', 'xi22', left=[('odt_en', 195, T('xi22', 'odt_en'), 'data'), ('rtt<2:0>', 235, Tbus('xi22', ['rtt<2>', 'rtt<1>', 'rtt<0>']), 'bus')],
                right=[('enb<2:0>', 215, Tbus('xi22', ['enb<2>', 'enb<1>', 'enb<0>']), 'bus')], link='b_odt_dec', members=['xi22'], sub='odt_dec')
    dec['info']['pcls'] = {}
    amp = h.tri('xi24', 520, 560, 'AMP', 'xi24', w=110, h=250,
                ins=[('inp', -90, T('xi24', 'inp')), ('vref', 0, T('xi24', 'vref')), ('lbp', 60, T('xi24', 'lbp')), ('lbn', 100, T('xi24', 'lbn'))],
                outs=[('outp', -30, T('xi24', 'outp')), ('outn', 30, T('xi24', 'outn'))],
                top=[('sel_m', 35, T('xi24', 'sel_m'), 'data'), ('sel_l', 70, T('xi24', 'sel_l'), 'data')],
                members=['xi24'], sub='rx_pre', pm={'inp': '+', 'vref': '−', 'lbp': '+', 'lbn': '−'}, link='u_rx_pre')
    amp['info']['pcls'] = {'inp': 'data_in', 'vref': 'reference', 'lbp': 'data_in', 'lbn': 'data_in', 'outp': 'data_out', 'outn': 'data_out', 'sel_m': 'control', 'sel_l': 'control'}
    lpf = h.box('LPF', 330, 530, 90, 60, 'LPF', None, left=[('vref', 560, [[('r0', 'p')]], 'data')], right=[('net3', 560, [[('r0', 'n')]], 'data')],
                link='u_top_lpf', members=['r0', 'mn0'], sub='r0 + mn0')
    lpf['info']['virtual'] = True; lpf['info']['pcls'] = {'vref': 'reference', 'net3': 'data_out'}
    sig = {}
    for inst, y0 in (('xi26', 330), ('xi27', 720)):
        L = [(p, y0 + 30 * (k + 1), T(inst, p), 'data') for k, p in enumerate(['inp', 'inn', 'hp', 'hn'])]
        R_ = [('outp', y0 + 45, T(inst, 'outp'), 'data'), ('outn', y0 + 105, T(inst, 'outn'), 'data')]
        TP = [('tap<3:0>', 815, Tbus(inst, ['tap<3>', 'tap<2>', 'tap<1>', 'tap<0>']), 'bus'), ('sgn', 850, T(inst, 'sgn'), 'data'),
              ('sgnb', 885, T(inst, 'sgnb'), 'data'), ('en', 920, T(inst, 'en'), 'data')]
        sym = h.box(inst, 790, y0, 150, 150, '\u03a3', inst, left=L, right=R_, top=TP, link='u_dfe_sum', members=[inst], sub='dfe_sum')
        sym['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'hp': 'data_in', 'hn': 'data_in', 'outp': 'data_out', 'outn': 'data_out',
                               'tap<3:0>': 'control', 'sgn': 'control', 'sgnb': 'control', 'en': 'control'}
        sig[inst] = sym
    for inst_ in sig:
        for pn_, LL_ in (('tap<3:0>', 30), ('sgn', 60), ('sgnb', 30), ('en', 60), ('hp', 30), ('hn', 60), ('inp', 30), ('inn', 60)):
            h.default_lens[h.pt(sig[inst_], pn_)] = LL_
    sa = {}
    for inst, yc in (('xi28', 405), ('xi29', 795)):
        sym = h.tri(inst, 1040, yc, 'SA', inst, w=80, h=110, ins=[('inp', -30, T(inst, 'inp')), ('inn', 30, T(inst, 'inn'))],
                    outs=[('outp', -25, T(inst, 'outp')), ('outn', 25, T(inst, 'outn'))], bottom=[('ck', 40, T(inst, 'ck'), 'clock')],
                    clock_mark=True, members=[inst], sub='sa_dt', pm={'inp': '+', 'inn': '−'}, link='b_sa_dt')
        r = POL.outputs('sa_dt', ['inp', 'inn'], ['outp', 'outn'])
        sym['info']['pol'] = {'ins': ['inp', 'inn'], 'outs': ['outp', 'outn'], 'outpins': ['outp', 'outn'], 'logic': ['outp', 'outn']}
        sym['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'outp': 'data_out', 'outn': 'data_out', 'ck': 'clock'}
        sa[inst] = sym
    sr = {}
    for inst, ys in (('xi30', (380, 430, 345)), ('xi31', (770, 820, 735))):
        sr[inst] = draw_inst_box(h, inst, 1200, ys[2], [('s', ys[0]), ('r', ys[1])], [('q', ys[0]), ('qb', ys[1])], w=110, hh=110, link='b_sr_nor',
                                 pcls={'s': 'data_in', 'r': 'data_in', 'q': 'data_out', 'qb': 'data_out'}, main_in=['s', 'r'])
    inv = {}
    for inst, yc, x0, lk in (('xi7', 380, 1400, 'u_inv_a'), ('xi8', 380, 1520, 'u_inv_c'), ('xi9', 430, 1400, 'u_inv_a'),
                             ('xi10', 770, 1400, 'u_inv_a'), ('xi11', 770, 1520, 'u_inv_c'), ('xi12', 820, 1400, 'u_inv_a')):
        inv[inst] = inv_inst(h, inst, x0, yc, link=lk)
    # ---- control logic
    c = {}
    c['xi0'] = inv_inst(h, 'xi0', 430, 85, link='u_inv_a')
    c['xi1'] = draw_inst_box(h, 'xi1', 560, 30, [('a', 55), ('b', 85)], [('y', 65)], w=90, hh=70, link='u_nand2_a', main_in=['a'], pcls={})
    c['xi2'] = inv_inst(h, 'xi2', 720, 65, link='u_inv_a')
    c['xi3'] = draw_inst_box(h, 'xi3', 560, 150, [('a', 175), ('b', 205)], [('y', 185)], w=90, hh=70, link='u_nand2_a', main_in=['a'], pcls={})
    c['xi4'] = inv_inst(h, 'xi4', 720, 185, link='u_inv_a')
    c['xi5'] = inv_inst(h, 'xi5', 1000, 100, link='u_inv_a'); c['xi6'] = inv_inst(h, 'xi6', 1130, 100, link='u_inv_a')
    ckg = draw_inst_box(h, 'xi25', 300, 1000, [('ck', 1030), ('ckb', 1070)], [('cko', 1030), ('ckob', 1070)], w=120, hh=100, link='b_ck_gbuf',
                        top=[('en', 360)], label='CK GATE', main_in=['ck', 'ckb'], pcls={'ck': 'clock', 'ckb': 'clock'}, logic_out=False)
    ckg['info']['gate'] = True
    # ---- routing: local / short nets first, long ones last (they fall back to labels)
    pt = h.pt
    h.auto('pad', [pt(esd, 'pad'), pt(od, 'B'), P['pad']], name='pad')
    h.auto('net1', [pt(esd, 'pad_r'), pt(amp, 'inp')])
    h.auto('net3', [pt(lpf, 'net3'), pt(amp, 'vref')])
    h.auto('vref', [pt(lpf, 'vref'), P['vref']])
    h.auto('lb_p', [pt(amp, 'lbp'), P['lb_p']]); h.auto('lb_n', [pt(amp, 'lbn'), P['lb_n']])
    for k in ('xi26', 'xi27'):
        pass
    h.auto('net100', [pt(c['xi0'], 'y'), pt(c['xi1'], 'b')]); h.auto('net101', [pt(c['xi1'], 'y'), pt(c['xi2'], 'a')])
    h.auto('net103', [pt(c['xi3'], 'y'), pt(c['xi4'], 'a')])
    h.auto('net105', [pt(c['xi5'], 'y'), pt(c['xi6'], 'a'), pt(sig['xi26'], 'sgnb'), pt(sig['xi27'], 'sgnb')], name='net105')
    h.auto('net106', [pt(c['xi6'], 'y'), pt(sig['xi26'], 'sgn'), pt(sig['xi27'], 'sgn')], name='net106')
    h.auto('tap_sgn', [pt(c['xi5'], 'a'), P['tap_sgn']])
    h.auto('net102', [pt(c['xi2'], 'y'), pt(amp, 'sel_m')], name='net102'); h.auto('net104', [pt(c['xi4'], 'y'), pt(amp, 'sel_l')], name='net104')
    h.auto('lb_en', [pt(c['xi0'], 'a'), pt(c['xi3'], 'b'), P['lb_en']], name='lb_en')
    h.auto('rx_en', [pt(c['xi1'], 'a'), pt(c['xi3'], 'a'), pt(sig['xi26'], 'en'), pt(sig['xi27'], 'en'), pt(ckg, 'en'), P['rx_en']], name='rx_en')
    h.auto('tap<3:0>', [pt(sig['xi26'], 'tap<3:0>'), pt(sig['xi27'], 'tap<3:0>'), (815, 100)], name='tap<3:0>', cls='bus')
    h.auto('odt_en', [pt(dec, 'odt_en'), P['odt_en']]); h.auto('rtt<2:0>', [pt(dec, 'rtt<2:0>'), P['rtt<2:0>']], cls='bus')
    h.auto('net2<2:0>', [pt(dec, 'enb<2:0>'), pt(od, 'enb<2:0>')], name='net2<2:0>', cls='bus')
    h.auto('net6', [pt(amp, 'outp'), pt(sig['xi26'], 'inp'), pt(sig['xi27'], 'inp')], name='net6')
    h.auto('net7', [pt(amp, 'outn'), pt(sig['xi26'], 'inn'), pt(sig['xi27'], 'inn')], name='net7')
    for sg, sy, yc in (('xi26', 'xi28', 0), ('xi27', 'xi29', 0)):
        o = 'net10' if sg == 'xi26' else 'net12'; on = 'net11' if sg == 'xi26' else 'net13'
        h.auto(o, [pt(sig[sg], 'outp'), pt(sa[sy], 'inp')]); h.auto(on, [pt(sig[sg], 'outn'), pt(sa[sy], 'inn')])
    for sy, sx, a_, b_ in (('xi28', 'xi30', 'net18', 'net19'), ('xi29', 'xi31', 'net24', 'net25')):
        h.auto(a_, [pt(sa[sy], 'outp'), pt(sr[sx], 's')]); h.auto(b_, [pt(sa[sy], 'outn'), pt(sr[sx], 'r')])
    h.auto('net14', [pt(sr['xi30'], 'q'), pt(inv['xi7'], 'a'), pt(sig['xi27'], 'hp')], name='net14')
    h.auto('net15', [pt(sr['xi30'], 'qb'), pt(inv['xi9'], 'a'), pt(sig['xi27'], 'hn')], name='net15')
    h.auto('net16', [pt(sr['xi31'], 'q'), pt(inv['xi10'], 'a'), pt(sig['xi26'], 'hp')], name='net16')
    h.auto('net17', [pt(sr['xi31'], 'qb'), pt(inv['xi12'], 'a'), pt(sig['xi26'], 'hn')], name='net17')
    h.auto('net26', [pt(inv['xi7'], 'y'), pt(inv['xi8'], 'a')]); h.auto('net28', [pt(inv['xi10'], 'y'), pt(inv['xi11'], 'a')])
    h.auto('dout_e', [pt(inv['xi8'], 'y'), P['dout_e']]); h.auto('dout_o', [pt(inv['xi11'], 'y'), P['dout_o']])
    # unused outputs: short wire + label
    for inst, net in (('xi9', 'net27'), ('xi12', 'net29')):
        h.stub(pt(inv[inst], 'y'), 'right', net, name=net, L=40)
    CONF['unused_ok'][vid] = ['net27', 'net29']
    h.auto('net8', [pt(ckg, 'cko'), pt(sa['xi28'], 'ck')], name='net8', cls='clock'); h.auto('net9', [pt(ckg, 'ckob'), pt(sa['xi29'], 'ck')], name='net9', cls='clock')
    h.auto('ck', [pt(ckg, 'ck'), P['ck']], cls='clock'); h.auto('ckb', [pt(ckg, 'ckb'), P['ckb']], cls='clock')
    omit(h, ['ofe_p<1:0>', 'ofe_n<1:0>', 'ofo_p<1:0>', 'ofo_n<1:0>'], 'general_control'); omit(h, ['ibias', 'net4'], 'bias'); omit(h, ['vdd', 'vddq', 'vss', 'vssq'], 'power')
    h.V.omitted.append({'block': 'xi23', 'cell': 'rx_bias', 'reason': '고속 신호와 무관'})
    return h


if __name__ == '__main__':
    view_inv('inv_a', 'u_inv_a')
    view_inv('inv_c', 'u_inv_c')
    view_nand('nand2_a', 'u_nand2_a')
    view_nand('nand2_c', 'u_nand2_c')
    view_nor('nor2_c', 'u_nor2_c')
    view_ls('ls_lh', 'u_ls_lh')
    view_esd('esd_dq', 'u_esd_dq')
    view_odt('odt_pu', 'u_odt_pu')
    view_lpf('u_top_lpf')
    view_rx_pre('rx_pre', 'u_rx_pre')
    view_dfe_sum('dfe_sum', 'u_dfe_sum')
    view_sa1('u_sa_dt_stage1')
    view_sa2('u_sa_dt_stage2')
    view_b_sr('sr_nor', 'b_sr_nor')
    view_b_ckg('ck_gbuf', 'b_ck_gbuf')
    view_b_odtdec('odt_dec', 'b_odt_dec')
    view_b_sa('sa_dt', 'b_sa_dt')
    view_top('b_top')
    finish()
