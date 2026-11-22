"""gen_l1.py - views for exam circuit rx_l1 (rxbyte_top). Reuses hs.py and the generic view helpers of lib_s1.py (copied from the rx_s1 generator).
usage: gen_l1.py <netlist> <workdir>.  REDUCED SCOPE: only the views listed in ORDER are drawn (see MISSING.md)."""
import sys, json
src = open('lib_s1.py').read().split("if __name__ == '__main__':")[0].replace("TOP = 'dq_rx_unit'", "TOP = 'rxbyte_top'")
exec(src)
TOP = 'rxbyte_top'
CONF.clear(); CONF.update({'top': TOP, 'unused_ok': {}, 'extra_names': {}, 'allow_cross': {}, 'alias': {}})
POL = Polarity(cells, TOP)
VIEWS.clear()
AL = CONF['alias']
for nm, bits in {'dq<7:0>': ['dq7', 'dq6', 'dq5', 'dq4', 'dq3', 'dq2', 'dq1', 'dq0'], 'dq<3:0>': ['dq3', 'dq2', 'dq1', 'dq0'], 'dq<7:4>': ['dq7', 'dq6', 'dq5', 'dq4'],
                 'qr<3:0>': ['qr3', 'qr2', 'qr1', 'qr0'], 'qr<7:4>': ['qr7', 'qr6', 'qr5', 'qr4'], 'qf<3:0>': ['qf3', 'qf2', 'qf1', 'qf0'], 'qf<7:4>': ['qf7', 'qf6', 'qf5', 'qf4'],
                 'rtt<2:0>': ['rtt2', 'rtt1', 'rtt0'], 't1w<2:0>': ['t1w2', 't1w1', 't1w0'], 't2w<1:0>': ['t2w1', 't2w0'], 'vrc<5:0>': ['vrc5', 'vrc4', 'vrc3', 'vrc2', 'vrc1', 'vrc0'],
                 'enb<2:0>': ['enb2', 'enb1', 'enb0'], 'oenb<2:0>': ['net207', 'net206', 'net205'], 'c<5:0>': ['c5', 'c4', 'c3', 'c2', 'c1', 'c0'],
                 'w1<2:0>': ['w1_2', 'w1_1', 'w1_0'], 'w2<1:0>': ['w2_1', 'w2_0'], 'odtb<2:0>': ['odtb2', 'odtb1', 'odtb0'], 'ddl<2:0>': ['ddl2', 'ddl1', 'ddl0']}.items():
    AL[nm] = bits
import hs
hs.ALIAS.update(AL)
ORDER = ['b_top', 'b_dqslice', 'b_srnand', 'u_sbamp', 'u_padesd', 'u_invx1', 'u_invx4', 'u_nand2x1', 'u_nand2x2']


def finish():
    ids = {x.V.id for x in VIEWS}
    for x in VIEWS:
        x.V.hot = [t for t in x.V.hot if t['link'] in ids]
    out = []
    for h in sorted(VIEWS, key=lambda x: ORDER.index(x.V.id) if x.V.id in ORDER else 99):
        h.done()
        d = dict(h.V.__dict__); d.pop('_tid', None); out.append(d)
    json.dump(out, open(WD + '/scenes.json', 'w'), indent=0, default=list, ensure_ascii=False)
    json.dump(CONF, open(WD + '/conf.json', 'w'), indent=0, ensure_ascii=False)
    print('views:', [v['id'] for v in out])


def bus_terms(inst, ports):
    return [[(inst, p)] for p in ports]


def bpin(h, inst, name, ports):
    return (name, bus_terms(inst, ports))


# ---------------------------------------------------------------- b_srnand
def view_b_srnand(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (교차 결합 NAND2)' % cell, 700, 520)
    g0 = draw_inst_box(h, 'xi0', 270, 110, [('a', 135), ('b', 165)], [('y', 150)], w=110, hh=80, link='u_nand2x2', pcls={'a': 'data_in', 'b': 'data_in', 'y': 'data_out'}, main_in=['a'])
    g1 = draw_inst_box(h, 'xi1', 270, 330, [('a', 355), ('b', 385)], [('y', 370)], w=110, hh=80, link='u_nand2x2', pcls={'a': 'data_in', 'b': 'data_in', 'y': 'data_out'}, main_in=['a'])
    for n, y in (('sb', 135), ('rb', 355)):
        h.port(n, 130, y, 'right', 'in')
    h.port('q', 580, 150, 'right', 'out'); h.port('qb', 580, 370, 'right', 'out')
    h.auto('sb', [h.pt(g0, 'a'), (130, 135)]); h.auto('rb', [h.pt(g1, 'a'), (130, 355)])
    h.auto('q', [h.pt(g0, 'y'), h.pt(g1, 'b'), (580, 150)]); h.auto('qb', [h.pt(g1, 'y'), h.pt(g0, 'b'), (580, 370)])
    omit(h, ['vdd', 'vss'], 'power')
    return h


# ---------------------------------------------------------------- u_padesd (same element names as esd_dq)
def view_padesd(cell, vid):
    h = view_esd(cell, vid)
    h.V.title = '%s — unit level (패드 ESD: 다이오드 클램프 + 직렬 R + GGNMOS)' % cell
    return h


# ---------------------------------------------------------------- u_sbamp
def view_sbamp(cell, vid):
    h = new(vid, cell, 'unit', '%s — unit level (인버터형 증폭기: PMOS/NMOS 스택 + 헤더/풋터 enable)' % cell, 900, 760)
    P6 = h.mos('mp6', 450, 130, 'left', top='s'); P5 = h.mos('mp5', 450, 230, 'left', top='s')
    P1 = h.mos('mp1', 340, 340, 'left', top='s'); P2 = h.mos('mp2', 560, 340, 'right', top='s')
    N1 = h.mos('mn1', 340, 450, 'left', top='d'); N2 = h.mos('mn2', 560, 450, 'right', top='d')
    N5 = h.mos('mn5', 450, 570, 'left', top='d'); N6 = h.mos('mn6', 450, 670, 'left', top='d')
    pw(h, P6, 'T', 'vddq', 'up'); pw(h, N6, 'B', 'vssq', 'down')
    for p_, n_ in (('inp', (100, 395)), ('inn', (800, 395)), ('enb', (260, 130)), ('en', (260, 670)), ('out', (800, 270))):
        pass
    h.port('inp', 90, 395, 'right', 'in'); h.port('inn', 800, 395, 'left', 'in'); h.port('enb', 280, 130, 'right', 'in'); h.port('en', 280, 670, 'right', 'in')
    h.port('out', 800, 270, 'right', 'out')
    h.auto('net80', [h.pt(P6, 'B'), h.pt(P5, 'T')], cls='plain'); h.auto('net83', [h.pt(N5, 'B'), h.pt(N6, 'T')], cls='plain')
    h.auto('net81', [h.pt(P5, 'B'), h.pt(P1, 'T'), h.pt(P2, 'T')], cls='plain'); h.auto('net82', [h.pt(N5, 'T'), h.pt(N1, 'B'), h.pt(N2, 'B')], cls='plain')
    h.auto('net79', [h.pt(P1, 'B'), h.pt(N1, 'T'), h.pt(P5, 'G'), h.pt(N5, 'G')], name='net79')
    h.auto('out', [h.pt(P2, 'B'), h.pt(N2, 'T'), (800, 270)])
    h.auto('inp', [h.pt(P1, 'G'), h.pt(N1, 'G'), (90, 395)], name='inp'); h.auto('inn', [h.pt(P2, 'G'), h.pt(N2, 'G'), (800, 395)], name='inn')
    h.auto('enb', [h.pt(P6, 'G'), (280, 130)], name='enb'); h.auto('en', [h.pt(N6, 'G'), (280, 670)], name='en')
    return h



def var_marker(h, sid, x, y, pad_net_inst, enb_ports, up=True):
    """ODT variable termination R hanging on a pad node (concept symbol), pad pin at its lower end"""
    od = scene.res(h.V, sid, x, y, 'v', name=sid, size='', a=None, b=[[(sid, 'pad')]], members=[sid], var=True)
    od['info']['concept'] = True
    h.V.line([(x + 6, y + 10), (x + 46, y + 10)], w=1.6, owner=sid)
    od['pins'].append(scene.pin('enb<2:0>', x + 46, y + 10, bus_terms(sid, enb_ports)))
    h.V.circle(x, y - 33, 3, fill='#fff', owner=sid)
    h.reg(od)
    h.V.hot.append({'x': x - 25, 'y': y - 35, 'w': 85, 'h': 70, 'link': 'u_odtleg3', 'sym': sid})
    return od


def view_b_dqslice(cell, vid):
    h = new(vid, cell, 'block', '%s — 블록 레벨 (DQ 한 줄: ESD/ODT → 증폭기 2개 → 2탭 DFE 샘플러 2개 → SR latch)' % cell, 1500, 1000)
    pt = h.pt
    for n, xy, d, io in (('pad', (110, 300), 'right', 'in'), ('vref', (110, 560), 'right', 'in'), ('en', (470, 90), 'down', 'in'), ('enb', (520, 90), 'down', 'in'),
                         ('w1<2:0>', (720, 90), 'down', 'in'), ('w2<1:0>', (800, 90), 'down', 'in'), ('odtb<2:0>', (110, 130), 'right', 'in'),
                         ('ckt', (110, 900), 'right', 'in'), ('ckc', (110, 940), 'right', 'in'), ('qr', (1400, 300), 'right', 'out'), ('qf', (1400, 620), 'right', 'out')):
        h.port(n, xy[0], xy[1], d, io)
    esd = h.box('xi0', 200, 260, 90, 80, 'ESD', 'xi0', left=[('pad', 300, T('xi0', 'pad'), 'data')], right=[('pad_r', 300, T('xi0', 'pad_r'), 'data')], link='u_padesd', members=['xi0'], sub='padesd')
    esd['info']['pcls'] = {'pad': 'data_in', 'pad_r': 'data_out'}
    od = var_marker(h, 'xi1', 160, 220, None, ['enb2', 'enb1', 'enb0'])
    amps = {}
    for inst, yc, ins in (('xi2', 330, ('inp', 'inn')), ('xi3', 560, ('inp', 'inn'))):
        sym = h.tri(inst, 400, yc, 'AMP', inst, w=90, h=120, ins=[('inp', -30, T(inst, 'inp')), ('inn', 30, T(inst, 'inn'))], outs=[('out', 0, T(inst, 'out'))],
                    top=[('enb', 25, T(inst, 'enb'), 'data'), ('en', 55, T(inst, 'en'), 'data')], members=[inst], sub='', link='u_sbamp')
        sym['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'out': 'data_out', 'en': 'control', 'enb': 'control'}
        amps[inst] = sym
    for inst_ in amps:
        h.default_lens[pt(amps[inst_], 'enb')] = 30; h.default_lens[pt(amps[inst_], 'en')] = 60
    sa = {}
    for inst, yc, ckp in (('xi4', 320, 'ckt'), ('xi6', 640, 'ckc')):
        sym = h.tri(inst, 640, yc, 'SA', inst, w=120, h=240,
                    ins=[('inp', -80, T(inst, 'inp')), ('inn', -50, T(inst, 'inn')), ('h1p', -10, T(inst, 'h1p')), ('h1n', 20, T(inst, 'h1n')), ('h2p', 50, T(inst, 'h2p')), ('h2n', 80, T(inst, 'h2n'))],
                    outs=[('outp', -30, T(inst, 'outp')), ('outn', 30, T(inst, 'outn'))],
                    top=[('w1<2:0>', 25, bus_terms(inst, ['w1_2', 'w1_1', 'w1_0']), 'bus'), ('w2<1:0>', 90, bus_terms(inst, ['w2_1', 'w2_0']), 'bus')],
                    bottom=[('ck', 50, T(inst, 'ck'), 'clock')], clock_mark=True, members=[inst], sub='')
        sym['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'h1p': 'data_in', 'h1n': 'data_in', 'h2p': 'data_in', 'h2n': 'data_in', 'outp': 'data_out', 'outn': 'data_out', 'ck': 'clock',
                               'w1<2:0>': 'control', 'w2<1:0>': 'control'}
        sa[inst] = sym
    sr = {}
    for inst, y0 in (('xi5', 250), ('xi7', 570)):
        sr[inst] = draw_inst_box(h, inst, 900, y0, [('sb', y0 + 40), ('rb', y0 + 110)], [('q', y0 + 40), ('qb', y0 + 110)], w=110, hh=150, link='b_srnand',
                                 pcls={'sb': 'data_in', 'rb': 'data_in', 'q': 'data_out', 'qb': 'data_out'}, main_in=['sb', 'rb'])
    inv = {}
    for inst_ in sa:
        for pn_, LL_ in (('inp', 30), ('inn', 60), ('h1p', 30), ('h1n', 60), ('h2p', 30), ('h2n', 60)):
            h.default_lens[pt(sa[inst_], pn_)] = LL_
    for inst, yc, x0, lk in (('xi8', 290, 1080, 'u_invx1'), ('xi9', 290, 1200, 'u_invx4'), ('xi10', 610, 1080, 'u_invx1'), ('xi11', 610, 1200, 'u_invx4')):
        inv[inst] = inv_inst(h, inst, x0, yc, link=lk)
    h.auto('pad', [pt(esd, 'pad'), pt(od, 'B'), (110, 300)], name='pad')
    h.auto('net92', [pt(esd, 'pad_r'), pt(amps['xi2'], 'inp'), pt(amps['xi3'], 'inn')], name='net92')
    h.auto('vref', [pt(amps['xi2'], 'inn'), pt(amps['xi3'], 'inp'), (110, 560)], name='vref')
    for a, b in (('xi2', 'net93'), ('xi3', 'net94')):
        pass
    h.auto('net93', [pt(amps['xi2'], 'out'), pt(sa['xi4'], 'inp'), pt(sa['xi6'], 'inp')], name='net93')
    h.auto('net94', [pt(amps['xi3'], 'out'), pt(sa['xi4'], 'inn'), pt(sa['xi6'], 'inn')], name='net94')
    h.auto('net95', [pt(sa['xi4'], 'outp'), pt(sr['xi5'], 'rb')], name='net95'); h.auto('net96', [pt(sa['xi4'], 'outn'), pt(sr['xi5'], 'sb')], name='net96')
    h.auto('net97', [pt(sa['xi6'], 'outp'), pt(sr['xi7'], 'rb')], name='net97'); h.auto('net98', [pt(sa['xi6'], 'outn'), pt(sr['xi7'], 'sb')], name='net98')
    h.auto('net99', [pt(sr['xi5'], 'q'), pt(inv['xi8'], 'a'), pt(sa['xi4'], 'h2p'), pt(sa['xi6'], 'h1p')], name='net99')
    h.auto('net100', [pt(sr['xi5'], 'qb'), pt(sa['xi4'], 'h2n'), pt(sa['xi6'], 'h1n')], name='net100')
    h.auto('net101', [pt(sr['xi7'], 'q'), pt(inv['xi10'], 'a'), pt(sa['xi4'], 'h1p'), pt(sa['xi6'], 'h2p')], name='net101')
    h.auto('net102', [pt(sr['xi7'], 'qb'), pt(sa['xi4'], 'h1n'), pt(sa['xi6'], 'h2n')], name='net102')
    h.auto('net103', [pt(inv['xi8'], 'y'), pt(inv['xi9'], 'a')]); h.auto('net104', [pt(inv['xi10'], 'y'), pt(inv['xi11'], 'a')])
    h.auto('qr', [pt(inv['xi9'], 'y'), (1400, 300)]); h.auto('qf', [pt(inv['xi11'], 'y'), (1400, 620)])
    h.auto('en', [pt(amps['xi2'], 'en'), pt(amps['xi3'], 'en'), (470, 90)], name='en'); h.auto('enb', [pt(amps['xi2'], 'enb'), pt(amps['xi3'], 'enb'), (520, 90)], name='enb')
    h.auto('w1<2:0>', [pt(sa['xi4'], 'w1<2:0>'), pt(sa['xi6'], 'w1<2:0>'), (720, 90)], name='w1<2:0>', cls='bus')
    h.auto('w2<1:0>', [pt(sa['xi4'], 'w2<1:0>'), pt(sa['xi6'], 'w2<1:0>'), (800, 90)], name='w2<1:0>', cls='bus')
    h.auto('odtb<2:0>', [pt(od, 'enb<2:0>'), (110, 130)], name='odtb<2:0>', cls='bus')
    h.auto('ckt', [pt(sa['xi4'], 'ck'), (110, 900)], name='ckt', cls='clock'); h.auto('ckc', [pt(sa['xi6'], 'ck'), (110, 940)], name='ckc', cls='clock')
    omit(h, ['vdd', 'vddq', 'vss', 'vssq'], 'power')
    return h


def view_b_top(vid):
    h = new(vid, TOP, 'block', '%s — 블록 레벨 (최상위, 축소 범위)' % TOP, 2100, 1300)
    pt = h.pt
    PRT = {'dqs_t': (110, 150), 'dqs_c': (110, 260), 'gate_open': (110, 380), 'rx_en': (110, 470), 'slp': (110, 540), 'odt_en': (110, 680), 'rtt<2:0>': (110, 720), 'vrc<5:0>': (110, 830),
           'wl_ck': (110, 1130), 'wl_en': (110, 1190), 'wl_out': (2000, 1130), 't1w<2:0>': (1500, 60), 't2w<1:0>': (1560, 60),
           'dq<3:0>': (1600, 80), 'dq<7:4>': (1600, 140)}
    for n, xy in PRT.items():
        if n in ('wl_out',):
            h.port(n, xy[0], xy[1], 'right', 'out')
        elif n in ('t1w<2:0>', 't2w<1:0>'):
            h.port(n, xy[0], xy[1], 'down', 'in')
        else:
            h.port(n, xy[0], xy[1], 'right', 'in')
    # DQS path
    esd = {}
    for inst, y, pad, padr in (('xi4', 150, 'dqs_t', 'net208'), ('xi5', 260, 'dqs_c', 'net209')):
        esd[inst] = h.box(inst, 250, y - 40, 90, 80, 'ESD', inst, left=[('pad', y, T(inst, 'pad'), 'data')], right=[('pad_r', y, T(inst, 'pad_r'), 'data')], members=[inst], sub='padesd')
        esd[inst]['info']['pcls'] = {'pad': 'data_in', 'pad_r': 'data_out'}
    od6 = var_marker(h, 'xi6', 190, 70, None, ['enb2', 'enb1', 'enb0'])
    od7 = var_marker(h, 'xi7', 190, 330, None, ['enb2', 'enb1', 'enb0'])
    dec = h.box('xi3', 150, 650, 140, 100, 'DEC', 'xi3', left=[('odt_en', 680, T('xi3', 'odt_en'), 'data'), ('rtt<2:0>', 720, bus_terms('xi3', ['rtt2', 'rtt1', 'rtt0']), 'bus')],
                right=[('enb<2:0>', 700, bus_terms('xi3', ['enb2', 'enb1', 'enb0']), 'bus')], members=['xi3'], sub='odtctl')
    vref = h.box('xi2', 150, 810, 140, 100, 'VREF', 'xi2', left=[('c<5:0>', 830, bus_terms('xi2', ['c5', 'c4', 'c3', 'c2', 'c1', 'c0']), 'bus')], right=[('vref', 860, T('xi2', 'vref'), 'data')], members=['xi2'], sub='vrefdac')
    lv = draw_inst_box(h, 'xi0', 150, 450, [('in', 470)], [('out', 470), ('outb', 500)], w=90, hh=70, label='LS', main_in=['in'], pcls={}, logic_out=False)
    lv['info']['gate'] = True
    rx = h.box('xi8', 470, 110, 130, 200, 'DQS RX', 'xi8', left=[('inp', 150, T('xi8', 'inp'), 'data'), ('inn', 260, T('xi8', 'inn'), 'data')],
               right=[('ckt', 150, T('xi8', 'ckt'), 'data'), ('ckc', 260, T('xi8', 'ckc'), 'data')], top=[('en', 520, T('xi8', 'en'), 'data'), ('enq', 560, T('xi8', 'enq'), 'data')], members=['xi8'], sub='dqsrx')
    rx['info']['pcls'] = {'inp': 'data_in', 'inn': 'data_in', 'ckt': 'data_out', 'ckc': 'data_out', 'en': 'control', 'enq': 'control'}
    h.V.omitted.append({'block': 'xi1', 'cell': 'biasgen', 'reason': '고속 신호와 무관'})
    gt = h.box('xi9', 760, 110, 130, 200, 'GATE', 'xi9', left=[('ckt', 150, T('xi9', 'ckt'), 'data'), ('ckc', 260, T('xi9', 'ckc'), 'data')],
               right=[('gt', 150, T('xi9', 'gt'), 'data'), ('gc', 260, T('xi9', 'gc'), 'data')], top=[('open', 800, T('xi9', 'open'), 'data')], members=['xi9'], sub='dqsgate')
    gt['info']['pcls'] = {'ckt': 'clock', 'ckc': 'clock', 'gt': 'data_out', 'gc': 'data_out', 'open': 'control'}
    gt['info']['clock_left_ok'] = True
    dl = {}
    for inst, y in (('xi10', 150), ('xi11', 260)):
        dl[inst] = h.box(inst, 1040, y - 40, 100, 80, 'DLY', inst, left=[('in', y, T(inst, 'in'), 'data')], right=[('out', y, T(inst, 'out'), 'data')], members=[inst], sub='dly3')
        dl[inst]['info']['pcls'] = {}
    bufs = {}
    MERGED = {'xi14': ['xi14', 'xi15'], 'xi16': ['xi16', 'xi17'], 'xi18': ['xi18', 'xi19'], 'xi20': ['xi20', 'xi21']}
    LBL = {'xi14': 'xi14 … xi15', 'xi16': 'xi16 … xi17', 'xi18': 'xi18 … xi19', 'xi20': 'xi20 … xi21'}
    def buf(inst, x0, yc):
        s_ = h.tri(inst, x0, yc, 'BUF', LBL.get(inst, inst), w=60, h=60, ins=[('a', 0, T(inst, 'a'))], outs=[('y', 0, T(inst, 'y'))], members=MERGED.get(inst, [inst]), sub='')
        s_['info']['pcls'] = {'a': 'data_in', 'y': 'data_out'}
        return s_
    b1 = {'xi12': buf('xi12', 1240, 150), 'xi13': buf('xi13', 1240, 260)}
    stage2 = [('xi14', 'net216', 'net218', 400), ('xi16', 'net217', 'net219', 520), ('xi18', 'net216', 'net220', 640), ('xi20', 'net217', 'net221', 760), ('xi22', 'net216', 'net222', 880), ('xi23', 'net217', 'net223', 1000)]
    b2 = {}
    for inst, a, y, yc in stage2:
        b2[inst] = buf(inst, 1420, yc)
    h.V.notes.append('ckbuf 쌍(xi14/xi15, xi16/xi17, xi18/xi19, xi20/xi21)은 입력·출력이 같은 병렬 인스턴스라 하나의 BUF 로 합침: xi14 … xi15, xi16 … xi17, xi18 … xi19, xi20 … xi21 (질문 Q2). 합친 블록의 첫 인스턴스만 연결을 그림')
    slA = h.box('xi30', 1700, 200, 190, 300, 'DQ<3:0>', 'xi30 … xi33', left=[('pad', 250, [[('xi33', 'pad')], [('xi32', 'pad')], [('xi31', 'pad')], [('xi30', 'pad')]], 'bus'), ('vref', 290, T('xi30', 'vref'), 'data'),
                ('ckt', 400, T('xi30', 'ckt'), 'data'), ('ckc', 440, T('xi30', 'ckc'), 'data')],
                right=[('qr', 280, [[('xi33', 'qr')], [('xi32', 'qr')], [('xi31', 'qr')], [('xi30', 'qr')]], 'bus'), ('qf', 340, [[('xi33', 'qf')], [('xi32', 'qf')], [('xi31', 'qf')], [('xi30', 'qf')]], 'bus')],
                top=[('en', 1740, T('xi30', 'en'), 'data'), ('enb', 1780, T('xi30', 'enb'), 'data'), ('w1<2:0>', 1830, bus_terms('xi30', ['w1_2', 'w1_1', 'w1_0']), 'bus'), ('w2<1:0>', 1875, bus_terms('xi30', ['w2_1', 'w2_0']), 'bus')], link='b_dqslice',
                members=['xi30', 'xi31', 'xi32', 'xi33'], sub='dqslice')
    slB = h.box('xi34', 1700, 600, 190, 300, 'DQ<7:4>', 'xi34 … xi37', left=[('pad', 610, [[('xi37', 'pad')], [('xi36', 'pad')], [('xi35', 'pad')], [('xi34', 'pad')]], 'bus'), ('vref', 650, T('xi34', 'vref'), 'data'),
                ('ckt', 760, T('xi34', 'ckt'), 'data'), ('ckc', 800, T('xi34', 'ckc'), 'data')],
                right=[('qr', 650, [[('xi37', 'qr')], [('xi36', 'qr')], [('xi35', 'qr')], [('xi34', 'qr')]], 'bus'), ('qf', 700, [[('xi37', 'qf')], [('xi36', 'qf')], [('xi35', 'qf')], [('xi34', 'qf')]], 'bus')],
                top=[('en', 1740, T('xi34', 'en'), 'data'), ('enb', 1780, T('xi34', 'enb'), 'data'), ('w1<2:0>', 1830, bus_terms('xi34', ['w1_2', 'w1_1', 'w1_0']), 'bus'), ('w2<1:0>', 1875, bus_terms('xi34', ['w2_1', 'w2_0']), 'bus')], link='b_dqslice',
                members=['xi34', 'xi35', 'xi36', 'xi37'], sub='dqslice')
    for sl_ in (slA, slB):
        sl_['info']['virtual'] = False
        sl_['info']['pcls'] = {}
    rep = h.box('xi38', 1700, 920, 150, 160, 'DQ dummy', 'xi38', left=[('vref', 960, T('xi38', 'vref'), 'data'), ('ckt', 1000, T('xi38', 'ckt'), 'data'), ('ckc', 1040, T('xi38', 'ckc'), 'data')],
               right=[('qr', 960, T('xi38', 'qr'), 'data'), ('qf', 1000, T('xi38', 'qf'), 'data')], link='b_dqslice', members=['xi38'], sub='dqslice')
    rep['info']['pcls'] = {}
    wl = h.box('xi39', 1700, 1120, 150, 100, 'WL', 'xi39', left=[('d', 1150, T('xi39', 'd'), 'data'), ('ck', 1190, T('xi39', 'ck'), 'data')], right=[('q', 1150, T('xi39', 'q'), 'data')],
               top=[('en', 1760, T('xi39', 'en'), 'data')], members=['xi39'], sub='wldet')
    wl['info']['pcls'] = {}
    pw_ = h.box('mp0', 150, 560, 100, 80, 'PWR SW', 'mp0', top=[('slp', 200, [[('mp0', 'g')]], 'data')], members=['mp0'], sub='헤더')
    pw_['info']['virtual'] = True; pw_['info']['pcls'] = {}
    d0 = h.diode('d0', 1190, 235, flip=True); d1 = h.diode('d1', 1190, 345, flip=True)
    pw(h, d0, 'A', 'vss', 'down'); pw(h, d1, 'A', 'vss', 'down')
    # d0: anode vss, cathode net214 -> cathode is at the bottom; flip so cathode up? (drawn with anode up to the rail)
    for sl_ in (slA, slB):
        for pn_, LL_ in (('en', 30), ('enb', 60), ('w1<2:0>', 30), ('w2<1:0>', 60)):
            h.default_lens[pt(sl_, pn_)] = LL_
    h.default_lens[pt(lv, 'out')] = 30; h.default_lens[pt(lv, 'outb')] = 60
    # ---- routing
    h.auto('dqs_t', [pt(esd['xi4'], 'pad'), pt(od6, 'B'), PRT['dqs_t']], name='dqs_t'); h.auto('dqs_c', [pt(esd['xi5'], 'pad'), pt(od7, 'B'), PRT['dqs_c']], name='dqs_c')
    h.auto('net208', [pt(esd['xi4'], 'pad_r'), pt(rx, 'inp')]); h.auto('net209', [pt(esd['xi5'], 'pad_r'), pt(rx, 'inn')])
    h.auto('net210', [pt(rx, 'ckt'), pt(gt, 'ckt')]); h.auto('net211', [pt(rx, 'ckc'), pt(gt, 'ckc')])
    h.auto('net212', [pt(gt, 'gt'), pt(dl['xi10'], 'in')]); h.auto('net213', [pt(gt, 'gc'), pt(dl['xi11'], 'in')])
    h.auto('net214', [pt(dl['xi10'], 'out'), pt(b1['xi12'], 'a'), pt(d0, 'K')]); h.auto('net215', [pt(dl['xi11'], 'out'), pt(b1['xi13'], 'a'), pt(d1, 'K')])
    h.auto('net216', [pt(b1['xi12'], 'y')] + [pt(b2[i], 'a') for i in ('xi14', 'xi18', 'xi22')], name='net216')
    h.auto('net217', [pt(b1['xi13'], 'y')] + [pt(b2[i], 'a') for i in ('xi16', 'xi20', 'xi23')], name='net217')
    h.auto('net218', [pt(b2['xi14'], 'y'), pt(slA, 'ckt')], name='net218'); h.auto('net219', [pt(b2['xi16'], 'y'), pt(slA, 'ckc')], name='net219')
    h.auto('net220', [pt(b2['xi18'], 'y'), pt(slB, 'ckt')], name='net220'); h.auto('net221', [pt(b2['xi20'], 'y'), pt(slB, 'ckc')], name='net221')
    h.auto('net222', [pt(b2['xi22'], 'y'), pt(rep, 'ckt'), pt(wl, 'ck')], name='net222'); h.auto('net223', [pt(b2['xi23'], 'y'), pt(rep, 'ckc')], name='net223')
    h.auto('net204', [pt(vref, 'vref'), pt(slA, 'vref'), pt(slB, 'vref'), pt(rep, 'vref')], name='net204')
    h.auto('rx_en', [pt(lv, 'in'), pt(rx, 'en'), PRT['rx_en']], name='rx_en')
    h.auto('net201', [pt(lv, 'out'), pt(rx, 'enq'), pt(slA, 'en'), pt(slB, 'en')], name='net201'); h.auto('net202', [pt(lv, 'outb'), pt(slA, 'enb'), pt(slB, 'enb')], name='net202')
    h.auto('gate_open', [pt(gt, 'open'), PRT['gate_open']], name='gate_open'); h.auto('slp', [pt(pw_, 'slp'), PRT['slp']], name='slp')
    h.auto('odt_en', [pt(dec, 'odt_en'), PRT['odt_en']]); h.auto('rtt<2:0>', [pt(dec, 'rtt<2:0>'), PRT['rtt<2:0>']], cls='bus')
    h.auto('oenb<2:0>', [pt(dec, 'enb<2:0>'), pt(od6, 'enb<2:0>'), pt(od7, 'enb<2:0>')], name='oenb<2:0>', cls='bus', dirs={pt(od6, 'enb<2:0>'): ['up'], pt(od7, 'enb<2:0>'): ['up']})
    h.auto('vrc<5:0>', [pt(vref, 'c<5:0>'), PRT['vrc<5:0>']], cls='bus')
    h.auto('t1w<2:0>', [pt(slA, 'w1<2:0>'), pt(slB, 'w1<2:0>'), PRT['t1w<2:0>']], name='t1w<2:0>', cls='bus')
    h.auto('t2w<1:0>', [pt(slA, 'w2<1:0>'), pt(slB, 'w2<1:0>'), PRT['t2w<1:0>']], name='t2w<1:0>', cls='bus')
    h.auto('dq<3:0>', [pt(slA, 'pad'), PRT['dq<3:0>']], cls='bus'); h.auto('dq<7:4>', [pt(slB, 'pad'), PRT['dq<7:4>']], cls='bus')
    h.auto('wl_ck', [pt(wl, 'd'), PRT['wl_ck']]); h.auto('wl_en', [pt(wl, 'en'), PRT['wl_en']]); h.auto('wl_out', [pt(wl, 'q'), PRT['wl_out']])
    for n_, xy in (('qr<3:0>', (1990, 300)), ('qf<3:0>', (1990, 360))):
        h.port(n_, xy[0], xy[1], 'right', 'out')
    h.auto('qr<3:0>', [pt(slA, 'qr'), (1990, 300)], cls='bus'); h.auto('qf<3:0>', [pt(slA, 'qf'), (1990, 360)], cls='bus')
    for n_, xy in (('qr<7:4>', (1990, 660)), ('qf<7:4>', (1990, 720))):
        h.port(n_, xy[0], xy[1], 'right', 'out')
    h.auto('qr<7:4>', [pt(slB, 'qr'), (1990, 660)], cls='bus'); h.auto('qf<7:4>', [pt(slB, 'qf'), (1990, 720)], cls='bus')
    for inst, net in (('xi38', 'net224'), ('xi38', 'net225')):
        pass
    for pn_, net in (('qr', 'net224'), ('qf', 'net225')):
        h.stub(pt(rep, pn_), 'right', net, name=net, L=40)
    CONF['unused_ok'][vid] = ['net224', 'net225']
    omit(h, ['ddl<2:0>', ], 'general_control'); omit(h, ['ibias', 'net203'], 'bias'); omit(h, ['vdd', 'vddq', 'vssq', 'net200'], 'power')
    return h


if __name__ == '__main__':
    view_b_top('b_top')
    view_b_dqslice('dqslice', 'b_dqslice')
    view_b_srnand('srnand', 'b_srnand')
    view_sbamp('sbamp', 'u_sbamp')
    view_padesd('padesd', 'u_padesd')
    view_inv('invx1', 'u_invx1'); view_inv('invx4', 'u_invx4')
    view_nand('nand2x1', 'u_nand2x1'); view_nand('nand2x2', 'u_nand2x2')
    finish()
