"""inject.py - error injection for the exam checker (plan 4.1: every implemented check gets at least one injected error).
Each injection mutates a copy of one view (and texts) and must raise the target check's count above the baseline.
usage: inject.py <workdir> <netlist> <out json>"""
import json, sys, copy, re, collections
from netlist import parse
from check import Checker, CHECKS


def main():
    W, NL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
    cells, order = parse(NL)
    scenes = json.load(open(W + '/scenes.json'))
    texts = json.load(open(W + '/texts.json'))
    conf = json.load(open(W + '/conf.json'))
    C = Checker(cells, scenes, texts, conf)
    byid = {v['id']: v for v in scenes}
    base = {}
    for v in scenes:
        R, sha = C.run(v)
        base[v['id']] = ({k: len(R.get(k, [])) for k, _ in CHECKS}, sha)
    res = []

    def trial(name, vid, check, mut, tmut=None):
        v = copy.deepcopy(byid[vid])
        t = copy.deepcopy(texts)
        ok = mut(v)
        if tmut:
            tmut(t.setdefault(vid, []))
        C2 = Checker(cells, scenes, t, conf)
        R, sha = C2.run(v)
        n = len(R.get(check, []))
        if check == '16-sha':
            caught = sha != base[vid][1]
            n = int(caught)
        else:
            caught = n > base[vid][0][check]
        res.append({'name': name, 'view': vid, 'check': check, 'baseline': base[vid][0].get(check), 'after': n, 'caught': bool(caught), 'applied': ok is not False})

    def wires_of(v, net):
        return [i for i, w in enumerate(v['wires']) if w['net'] == net]

    # ---- required list (plan 4.1)
    def drop_wire(net, pick=0):
        def m(v):
            i = wires_of(v, net)[pick]
            pts = v['wires'][i]['pts']
            v['draw'] = [d for d in v['draw'] if not (d['t'] == 'line' and d.get('owner') == 'wire' and d['pts'] == pts)]
            del v['wires'][i]
        return m
    trial('OPEN: b_top net1 선 끊기', 'b_top', '1-conn', drop_wire('net1'))
    trial('OPEN: u_rx_pre net40 선 끊기', 'u_rx_pre', '1-conn', drop_wire('net40'))

    def short_pins(vid_syms):
        def m(v):
            pa = [p for s in v['symbols'] if s['id'] == vid_syms[0] for p in s['pins'] if p['name'] == vid_syms[1]][0]
            pb = [p for s in v['symbols'] if s['id'] == vid_syms[2] for p in s['pins'] if p['name'] == vid_syms[3]][0]
            v['wires'].append({'pts': [[pa['x'], pa['y']], [pa['x'], pb['y']], [pb['x'], pb['y']]], 'cls': 'data', 'net': None})
            v['draw'].append({'t': 'line', 'pts': [[pa['x'], pa['y']], [pa['x'], pb['y']], [pb['x'], pb['y']]], 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire'})
        return m
    trial('SHORT: b_top xi28 outp–outn 선', 'b_top', '1-conn', short_pins(('xi28', 'outp', 'xi28', 'outn')))
    trial('SHORT: u_dfe_sum 두 소자 핀 잇기', 'u_dfe_sum', '1-conn', short_pins(('mn0', 'T', 'mn1', 'T')))

    def add_wire(pts, net='x'):
        def m(v):
            v['wires'].append({'pts': pts, 'cls': 'data', 'net': net}); v['draw'].append({'t': 'line', 'pts': pts, 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire'})
        return m
    trial('블록 교차: b_top pad 선을 가로지르는 선', 'b_top', '5-cross', add_wire([[150, 440], [150, 500]]))

    def del_bubble(vid_inst):
        def m(v):
            n0 = len(v['draw'])
            v['draw'] = [d for d in v['draw'] if not (d['t'] == 'circle' and d.get('owner') == vid_inst and abs(d['r'] - 4) < 1e-6)]
            return len(v['draw']) < n0
        return m
    trial('동그라미 지우기: b_top xi7 인버터', 'b_top', '13-polarity', del_bubble('xi7'))
    trial('동그라미 지우기: b_odt_dec xi2 NAND', 'b_odt_dec', '13-polarity', del_bubble('xi2'))

    def add_bubble(inst, pin):
        def m(v):
            p = [q for s in v['symbols'] if s['id'] == inst for q in s['pins'] if q['name'] == pin][0]
            v['draw'].append({'t': 'circle', 'cx': p['x'] - 30, 'cy': p['y'], 'r': 4, 'fill': '#fff', 'stroke': '#111', 'w': 1.6, 'owner': inst})
        return m
    trial('동그라미 더하기: b_top xi28 (비반전 출력)', 'b_top', '13-polarity', add_bubble('xi28', 'outp'))

    def del_unused(net):
        def m(v):
            i = wires_of(v, net)
            for k in sorted(i, reverse=True):
                pts = v['wires'][k]['pts']
                v['draw'] = [d for d in v['draw'] if not (d['t'] == 'line' and d.get('owner') == 'wire' and d['pts'] == pts)]
                del v['wires'][k]
            v['labels'] = [l for l in v['labels'] if l['name'] != net]
        return m
    trial('미사용 출력 지우기: b_top net27', 'b_top', '10-outpin', del_unused('net27'))

    def rename_pin(sym, old, new):
        def m(v):
            for s in v['symbols']:
                if s['id'] == sym:
                    for p in s['pins']:
                        if p['name'] == old:
                            p['name'] = new
        return m
    trial('없는 핀 이름: b_top xi24 sel_m → sel_x', 'b_top', '23-blockpins', rename_pin('xi24', 'sel_m', 'sel_x'))
    trial('없는 핀 이름: b_sr_nor xi0 a → z', 'b_sr_nor', '23-blockpins', rename_pin('xi0', 'a', 'z'))
    trial('없는 인스턴스 이름: b_top xi24 → xi99', 'b_top', '14-names', lambda v: [d.__setitem__('s', 'xi99') for d in v['draw'] if d['t'] == 'text' and d['s'] == 'xi24'])
    trial('없는 넷 이름표: b_top net7 → net77', 'b_top', '14-names', lambda v: [l.__setitem__('name', 'net77') for l in v['labels'] if l['name'] == 'net7'])
    trial('그리지도 생략하지도 않은 넷: b_top 생략 목록에서 ibias 빼기', 'b_top', '3-omit', lambda v: v.__setitem__('omitted', [o for o in v['omitted'] if o.get('net') != 'ibias']))
    trial('그렸는데 생략 목록에 넣음: b_top rx_en', 'b_top', '3-omit', lambda v: v['omitted'].append({'net': 'rx_en', 'class': '바이어스'}))

    def jog(v):
        i = wires_of(v, 'net1')[0]
        pts = v['wires'][i]['pts']
        old = copy.deepcopy(pts)
        x0, y0 = pts[0]; x1, y1 = pts[-1]
        new = [[x0, y0], [x0 + 5, y0], [x0 + 5, y0 - 6], [x1, y0 - 6], [x1, y1]] if len(pts) == 2 and abs(y0 - y1) < 1e-6 else None
        if new is None:
            return False
        v['wires'][i]['pts'] = new
        for d in v['draw']:
            if d['t'] == 'line' and d.get('owner') == 'wire' and d['pts'] == old:
                d['pts'] = new
    trial('짧은 꺾임(<20px): b_top net1', 'b_top', '5-short', jog)

    def overlap(v):
        pass
    def t_overlap(tb):
        a, b = tb[0], tb[1]
        b.update(x0=a['x0'], x1=a['x1'], y0=a['y0'], y1=a['y1'])
    trial('글자 겹침: b_top 두 글자 상자 겹치기', 'b_top', '5-overlap', lambda v: None, t_overlap)

    def dash(v):
        for d in v['draw']:
            if d['t'] == 'line' and d.get('owner') == 'wire':
                d['dash'] = '4 3'; break
    trial('점선: b_top 선 하나를 점선으로', 'b_top', '11-dash', dash)
    trial('선 굵기: b_top 선 하나를 2.4로', 'b_top', '11-dash', lambda v: [d.__setitem__('w', 2.4) for d in v['draw'] if d['t'] == 'line' and d.get('owner') == 'wire'][:1])

    def pinside(v):
        for s in v['symbols']:
            if s['id'] == 'xi24':
                for p in s['pins']:
                    if p['name'] == 'inp':
                        p['side'] = 'top'
    trial('핀 방향 위반: b_top xi24 inp(데이터 입력)를 위쪽으로', 'b_top', '18-pinside', pinside)
    trial('핀 방향 위반: b_sa_dt S1 ck(클럭)를 위쪽으로', 'b_sa_dt', '18-pinside', lambda v: [p.__setitem__('side', 'top') for s in v['symbols'] if s['id'] == 'S1' for p in s['pins'] if p['name'] == 'ck'])

    # ---- the other implemented checks
    def del_label_pair(net):
        def m(v):
            k = [i for i, l in enumerate(v['labels']) if l['name'] == net and l['kind'] == 'net']
            if len(k) < 2:
                return False
            v['labels'].pop(k[0])
        return m
    trial('짝 없는 이름표: b_top net14 이름표 하나 지우기', 'b_top', '2-label', del_label_pair('net14'))

    def del_port_wire(v):
        i = wires_of(v, 'ck')[0]
        pts = v['wires'][i]['pts']
        v['draw'] = [d for d in v['draw'] if not (d['t'] == 'line' and d.get('owner') == 'wire' and d['pts'] == pts)]
        del v['wires'][i]
    trial('떠 있는 포트: b_top ck 선 지우기', 'b_top', '6-port', del_port_wire)

    def del_dot(v):
        v['dots'] = v['dots'][:-1]
        v['draw'] = [d for d in v['draw'] if not (d['t'] == 'circle' and d.get('owner') == 'dot')][:-0 or None]
    def del_one_dot(v):
        # pick a dot where a wire END lands on the interior of another wire (a real T junction)
        def is_T(dx, dy):
            for a_, wa in enumerate(v['wires']):
                for e_ in (wa['pts'][0], wa['pts'][-1]):
                    if abs(e_[0] - dx) < 0.6 and abs(e_[1] - dy) < 0.6:
                        for b_, wb in enumerate(v['wires']):
                            if a_ == b_:
                                continue
                            P = wb['pts']
                            if any(abs(P[q][0] - P[q + 1][0]) < 1e-6 and abs(P[q][0] - dx) < 0.6 and min(P[q][1], P[q + 1][1]) + 0.6 < dy < max(P[q][1], P[q + 1][1]) - 0.6 or
                                   abs(P[q][1] - P[q + 1][1]) < 1e-6 and abs(P[q][1] - dy) < 0.6 and min(P[q][0], P[q + 1][0]) + 0.6 < dx < max(P[q][0], P[q + 1][0]) - 0.6 for q in range(len(P) - 1)):
                                return True
            return False
        cand = [i_ for i_, (dx, dy) in enumerate(v['dots']) if is_T(dx, dy)]
        if not cand:
            return False
        x, y = v['dots'].pop(cand[0])
        for k, d in enumerate(v['draw']):
            if d['t'] == 'circle' and d.get('owner') == 'dot' and abs(d['cx'] - x) < 1e-6 and abs(d['cy'] - y) < 1e-6:
                v['draw'].pop(k); break
    trial('접점 점 삭제: u_nand2_a', 'u_nand2_a', '1-touch', del_one_dot)

    def kink(v):
        i = wires_of(v, 'net6')[0]
        pts = v['wires'][i]['pts']
        old = copy.deepcopy(pts)
        x0, y0 = pts[0]; x1, y1 = pts[-1]
        new = [[x0, y0], [x0, y0 - 300], [x1, y0 - 300], [x1, y1]]
        v['wires'][i]['pts'] = new
        for d in v['draw']:
            if d['t'] == 'line' and d.get('owner') == 'wire' and d['pts'] == old:
                d['pts'] = new
    trial('꼬임: b_top net6 선을 크게 돌리기', 'b_top', '5-kink', kink)

    def pierce(v):
        v['wires'].append({'pts': [[385, 520], [385, 600]], 'cls': 'data', 'net': 'x'})
        v['draw'].append({'t': 'line', 'pts': [[385, 520], [385, 600]], 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire'})
    trial('선이 몸체 관통: b_top ESD 박스 안쪽 선', 'b_top', '5-pierce', lambda v: add_wire([[355, 440], [355, 500]])(v))
    trial('R 값 틀림: u_odt_pu r2 60 → 61', 'u_odt_pu', '24-rcvalue', lambda v: [d.__setitem__('s', '61') for d in v['draw'] if d['t'] == 'text' and d['s'] == '60'])
    trial('핀 이름 지우기: b_top xi28 출력 핀 이름 outp', 'b_top', '15-pinnames', lambda v: v.__setitem__('draw', [d for d in v['draw'] if not (d['t'] == 'text' and d.get('owner') == 'xi28' and d.get('cls') == 'pintext' and d['s'] == 'outp')]))
    trial('화면 지문: b_top 선 하나 이동', 'b_top', '16-sha', lambda v: [d.__setitem__('pts', [[p[0] + 10, p[1]] for p in d['pts']]) for d in v['draw'] if d['t'] == 'line' and d.get('owner') == 'wire'][:1])

    def t_out(tb):
        tb[0].update(x0=-50, x1=-10)
    trial('글자 밖으로: b_top 글자 상자를 화면 밖으로', 'b_top', '25-inside', lambda v: None, t_out)
    trial('같은 직선 위 자유 선 끝: b_top 40px 미만', 'b_top', '5-endline', lambda v: (v['wires'].append({'pts': [[300, 60], [330, 60]], 'cls': 'data', 'net': 'a'}), v['wires'].append({'pts': [[370, 60], [345, 60]], 'cls': 'data', 'net': 'b'}), v['draw'].append({'t': 'line', 'pts': [[300, 60], [330, 60]], 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire'}), v['draw'].append({'t': 'line', 'pts': [[370, 60], [345, 60]], 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire'})))

    def dots4(v):
        # a 4-way junction: put two crossing wires with a dot at the crossing
        v['wires'].append({'pts': [[600, 20], [600, 60]], 'cls': 'data', 'net': 'a'}); v['wires'].append({'pts': [[580, 40], [620, 40]], 'cls': 'data', 'net': 'a'})
        v['dots'].append([600, 40])
    trial('4방향 접점: b_top', 'b_top', '5-dots', dots4)
    json.dump(res, open(OUT, 'w'), indent=1, ensure_ascii=False)
    tot = len(res); got = sum(1 for r in res if r['caught'])
    print('injected', tot, 'caught', got)
    for r in res:
        if not r['caught']:
            print('NOT CAUGHT', r)


if __name__ == '__main__':
    main()
