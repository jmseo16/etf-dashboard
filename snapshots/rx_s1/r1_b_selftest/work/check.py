"""check.py - exam checker (new code). Re-reads connectivity from drawn geometry ONLY (wire polylines, pin points,
junction dots, label/port/power anchors; symbol strokes for shorts) and compares with the netlist, then runs the quality
checks. Usage: check.py <workdir> <netlist> <outdir>   (workdir has scenes.json, texts.json, conf.json)
Implemented checks are listed in CHECKS; plan 4.1 numbers that are not implemented are listed in NOT_IMPLEMENTED
and are reported as such (never as passed)."""
import json, sys, re, math, collections, copy, hashlib, itertools, os
from netlist import parse, Polarity
from hs import expand, seg_inter, seg_box, EPS

CHECKS = [
    ('1-conn', '4.1-1 연결 재추출 (기하만): SHORT / OPEN / 없는 핀·소자'),
    ('1-touch', '4.1-1 선 끝이 다른 선 위에 닿았는데 접점 점 없음'),
    ('2-label', '4.1-2 짝 없는 이름표 (예외: 화면 밖 연결 기호, 미사용 출력)'),
    ('3-omit', '4.1-3 생략 = 분류: 그리지 않은 넷은 생략 목록에, 그린 넷은 생략 목록에 없음'),
    ('5-overlap', '4.1-5 글씨 겹침'),
    ('5-pierce', '4.1-5 선이 심볼·몸체를 관통'),
    ('5-kink', '4.1-5 꼬임 (선 길이 > 1.5 x 가로+세로)'),
    ('5-short', '4.1-5 짧은 꺾임 (< 20px)'),
    ('5-dots', '4.1-5 접점 근접 (< 20px) / 4방향 접점'),
    ('5-cross', '4.1-5/1.4-9 교차 (허용 수 초과)'),
    ('5-endline', '1.4-7 같은 직선 위 다른 넷의 자유 선 끝 < 40px'),
    ('6-port', '4.1-6 떠 있는 포트 / 붙지 않은 핀'),
    ('10-outpin', '4.1-10 붙지 않은 출력 핀'),
    ('11-dash', '4.1-11 점선 / 선 굵기 != 1.6'),
    ('13-polarity', '4.1-13 출력별 극성 (동그라미 vs netlist 계산)'),
    ('14-names', '4.1-14 이름 일치 (인스턴스·소자·넷·포트 이름이 netlist에 있음)'),
    ('15-pinnames', '4.1-15 출력이 둘 이상인 기호의 핀 이름'),
    ('16-sha', '4.1-16 scene_sha'),
    ('18-pinside', '4.1-18 핀 방향 (블록 화면)'),
    ('23-blockpins', '4.1-23 블록 핀 이름 = 셀 포트 이름'),
    ('24-rcvalue', '4.1-24 R/C 값 = 실제 값'),
    ('25-inside', '4.1-25 글자·그림이 화면 밖으로 나가지 않음'),
]
NOT_IMPLEMENTED = {
    '4': '기호 = 묶음 (합친 소자를 쓰지 않아 해당 없음)', '7': '선 종류 일치 (모든 선이 같은 실선이라 11번이 대신함)',
    '8': '합친 블록 범례 (합친 블록 없음)', '9': '설명 수치 (주석에 수치를 쓰지 않음, 자동 검사는 구현 안 함)',
    '12': 'CCI 배치 (구현 안 함)', '17': '생성 코드 변경 범위 (수정 회차에서 손으로 보고)',
    '19': '회색 이름표 범위 (구현 안 함)', '20': '질문 형식 (구현 안 함, 손 확인)', '21': '끝점 핀 (구현 안 함, 손 확인)',
    '22': '표 간 분류 일치 (구현 안 함, 손 확인)'}

TOL = 0.6


def on_seg(p, a, b, tol=TOL):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(x - x1, y - y1) <= tol
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)) <= tol


def on_poly(p, pts):
    return any(on_seg(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def is_end(p, pts):
    return math.hypot(p[0] - pts[0][0], p[1] - pts[0][1]) <= TOL or math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) <= TOL


class UF:
    def __init__(s):
        s.p = {}

    def f(s, x):
        s.p.setdefault(x, x)
        while s.p[x] != x:
            s.p[x] = s.p[s.p[x]]
            x = s.p[x]
        return x

    def u(s, a, b):
        s.p[s.f(a)] = s.f(b)


def keyt(k):
    return tuple(k) if isinstance(k, (list, tuple)) else (k,)


class Checker:
    def __init__(self, cells, scenes, texts, conf):
        self.cells = cells
        self.scenes = scenes
        self.texts = texts
        self.conf = conf
        self.POL = Polarity(cells, conf['top'])

    # ---------------- helpers
    def netof(self, cell, term):
        e, t = term
        f = {x['name']: x for x in self.cells[cell]['elems']}[e]
        return f['pins'][t] if f['kind'] == 'inst' else f['terms'][t]

    def run(self, v):
        cell = v['cell']
        R = collections.defaultdict(list)
        cd = self.cells[cell]
        elems = {e['name']: e for e in cd['elems']}
        scope = v.get('scope')
        scope_el = [e for e in cd['elems'] if scope is None or e['name'] in scope]
        # ---- pins / wires / labels
        pins = []
        for s in v['symbols']:
            for p in s.get('pins', []):
                if p.get('terms'):
                    key = tuple(self.netof(cell, sl[0]) for sl in p['terms'])
                    pins.append(dict(x=p['x'], y=p['y'], key=key, sym=s['id'], name=p['name'], side=p.get('side'), kind=s['kind']))
        wires = [w['pts'] for w in v['wires']]
        dots = [tuple(d) for d in v['dots']]
        labs = [l for l in v['labels']]
        uf = UF()
        for i in range(len(wires)):
            uf.f(('w', i))
        for j in range(len(pins)):
            uf.f(('p', j))
        # wire-wire
        for i, A in enumerate(wires):
            for j, B in enumerate(wires):
                if i == j:
                    continue
                for pa in (A[0], A[-1]):
                    if on_poly(pa, B):
                        if is_end(pa, B) or any(math.hypot(pa[0] - d[0], pa[1] - d[1]) <= TOL for d in dots):
                            uf.u(('w', i), ('w', j))
                        else:
                            R['1-touch'].append('%s: 선 끝 %s 이(가) 다른 선 위에 있는데 접점 점이 없음' % (v['id'], pa))
        # pin-wire
        for j, p in enumerate(pins):
            for i, A in enumerate(wires):
                pt = (p['x'], p['y'])
                if on_poly(pt, A):
                    if is_end(pt, A) or any(math.hypot(pt[0] - d[0], pt[1] - d[1]) <= TOL for d in dots):
                        uf.u(('p', j), ('w', i))
                    else:
                        R['1-touch'].append('%s: 핀 %s.%s 가 선 가운데에 있는데 접점 점이 없음' % (v['id'], p['sym'], p['name']))
        # pin-pin at same point
        for j, p in enumerate(pins):
            for k, q in enumerate(pins):
                if j < k and abs(p['x'] - q['x']) <= TOL and abs(p['y'] - q['y']) <= TOL:
                    uf.u(('p', j), ('p', k))
        # labels
        lab_nodes = []
        for k, l in enumerate(labs):
            uf.f(('l', k))
            pt = tuple(l['at'])
            for i, A in enumerate(wires):
                if on_poly(pt, A):
                    uf.u(('l', k), ('w', i))
            for j, p in enumerate(pins):
                if abs(p['x'] - pt[0]) <= TOL and abs(p['y'] - pt[1]) <= TOL:
                    uf.u(('l', k), ('p', j))
        byname = collections.defaultdict(list)
        for k, l in enumerate(labs):
            if l['kind'] in ('net', 'port', 'power', 'offpage'):
                byname[tuple(expand(l['name']))].append(k)
        for nm, ks in byname.items():
            for k in ks[1:]:
                uf.u(('l', ks[0]), ('l', k))
        comps = collections.defaultdict(lambda: dict(pins=[], labs=[], wires=[]))
        for j in range(len(pins)):
            comps[uf.f(('p', j))]['pins'].append(j)
        for k, l in enumerate(labs):
            if l['kind'] in ('net', 'port', 'power', 'offpage'):
                comps[uf.f(('l', k))]['labs'].append(k)
        for i in range(len(wires)):
            comps[uf.f(('w', i))]['wires'].append(i)
        # ---- SHORT / OPEN
        gray_at = [tuple(l['at']) for l in labs if l['kind'] == 'gray']
        keyc = collections.defaultdict(set)
        grayr = set((round(a[0], 1), round(a[1], 1)) for a in gray_at)
        for c, d in comps.items():
            keys = set(pins[j]['key'] for j in d['pins'] if (round(pins[j]['x'], 1), round(pins[j]['y'], 1)) not in grayr) | set(tuple(expand(labs[k]['name'])) for k in d['labs'])
            # a one-bit label naming one bit of a pin bus is not a different net
            if len(keys) > 1:
                names = sorted(['/'.join(k) for k in keys])
                R['1-conn'].append('%s: SHORT — 한 덩어리에 다른 넷 %s' % (v['id'], ' , '.join(names)))
            for k in keys:
                keyc[k].add(c)
        for k, cs in keyc.items():
            if len(cs) > 1:
                R['1-conn'].append('%s: OPEN — 넷 %s 이(가) 조각 %d개' % (v['id'], '/'.join(k), len(cs)))
        # missing elements
        drawn_members = set()
        concept_members = set()
        for s in v['symbols']:
            drawn_members |= set(s.get('members') or [])
            if (s.get('info') or {}).get('concept') or (s.get('info') or {}).get('virtual'):
                concept_members |= set(s.get('members') or [])
        omitted_blocks = {o['block'] for o in v['omitted'] if 'block' in o}
        for e in scope_el:
            if e['name'] not in drawn_members and e['name'] not in omitted_blocks:
                R['1-conn'].append('%s: 그려지지 않은 소자 %s' % (v['id'], e['name']))
        for m in drawn_members:
            if m not in elems:
                R['14-names'].append('%s: 없는 소자 이름 %s' % (v['id'], m))
        # pin completeness: every terminal of every drawn member is a pin
        pinterms = set()
        for s in v['symbols']:
            for p in s.get('pins', []):
                for sl in p.get('terms') or []:
                    for tm in sl:
                        pinterms.add((tm[0], tm[1]))
        for e in scope_el:
            if e['name'] in drawn_members and e['name'] not in concept_members:
                tl = ('d', 'g', 's') if e['kind'] == 'mos' else (('p', 'n') if e['kind'] in ('res', 'cap', 'dio', 'ind') else tuple(e['pins']))
                for t in tl:
                    if e['kind'] == 'inst' and t not in [p['name'] for s in v['symbols'] for p in s.get('pins', []) if (e['name'], t) in [(a, b) for sl in (p.get('terms') or []) for (a, b) in sl]]:
                        pass
                    if (e['name'], t) not in pinterms and not (e['kind'] == 'inst' and False):
                        # instance pins may be hidden by design (hidden nets); only report MOS/R/C/D terminals
                        if e['kind'] != 'inst':
                            R['1-conn'].append('%s: 소자 %s 의 단자 %s 에 핀이 없음' % (v['id'], e['name'], t))
        # ---- floating pins / outputs
        grayset = set((round(a[0], 1), round(a[1], 1)) for a in gray_at)
        for j, p in enumerate(pins):
            c = comps[uf.f(('p', j))]
            alone = len(c['wires']) == 0 and len(c['labs']) == 0 and len(c['pins']) == 1
            if alone and (round(p['x'], 1), round(p['y'], 1)) not in grayset:
                key = p['key']
                if p.get('side') == 'right' and p['kind'] in ('tri', 'box', 'inv'):
                    R['10-outpin'].append('%s: 붙지 않은 출력 핀 %s.%s' % (v['id'], p['sym'], p['name']))
                else:
                    R['6-port'].append('%s: 붙지 않은 핀 %s.%s (%s)' % (v['id'], p['sym'], p['name'], '/'.join(key)))
        for k, l in enumerate(labs):
            if l['kind'] == 'port':
                c = comps[uf.f(('l', k))]
                if not c['wires'] and not any(pins[j]['x'] == l['at'][0] and pins[j]['y'] == l['at'][1] for j in c['pins']):
                    R['6-port'].append('%s: 떠 있는 포트 %s' % (v['id'], l['name']))
        # ---- label pairing
        cnt = collections.Counter()
        for l in labs:
            if l['kind'] in ('net', 'port'):
                cnt[l['name']] += 1
        for l in labs:
            if l['kind'] == 'net' and cnt[l['name']] < 2:
                if l['name'] in self.conf.get('unused_ok', {}).get(v['id'], []):
                    continue
                # a label that sits on a wire which also reaches pins/ports is paired by the net itself
                R['2-label'].append('%s: 짝 없는 이름표 %s' % (v['id'], l['name']))
        # ---- omitted list vs drawn
        drawn = set()
        for c, d in comps.items():
            has_wire = bool(d['wires']) or bool(d['labs'])
            for j in d['pins']:
                if has_wire or len(d['pins']) > 1:
                    drawn |= set(pins[j]['key'])
            for k in d['labs']:
                drawn |= set(expand(labs[k]['name']))
        all_nets = set()
        for e in scope_el:
            vals = e['pins'].values() if e['kind'] == 'inst' else e['terms'].values()
            for n in vals:
                all_nets.add(n)
        # bulk-only connections are not drawn (3-terminal symbols): a net seen only as bulk is not in all_nets via d/g/s
        for e in scope_el:
            if e['kind'] == 'mos':
                pass
        allx = set()
        for e in scope_el:
            if e['kind'] == 'mos':
                for t in ('d', 'g', 's'):
                    allx.add(e['terms'][t])
            elif e['kind'] == 'inst':
                allx |= set(e['pins'].values())
            else:
                allx |= set(e['terms'].values())
        omitted = set()
        for o in v['omitted']:
            if 'net' in o:
                omitted |= set(expand(o['net']))
        users = collections.defaultdict(set)
        for e in scope_el:
            vals = e['pins'].values() if e['kind'] == 'inst' else ([e['terms'][t] for t in ('d', 'g', 's')] if e['kind'] == 'mos' else e['terms'].values())
            for n in vals:
                users[n].add(e['name'])
        internal = {n for n, u in users.items() if u <= concept_members and n not in drawn}
        for n in sorted(allx - drawn - omitted - internal):
            R['3-omit'].append('%s: 그리지도 생략하지도 않은 넷 %s' % (v['id'], n))
        for n in sorted(omitted & drawn):
            R['3-omit'].append('%s: 그렸는데 생략 목록에 있는 넷 %s' % (v['id'], n))
        # ---- geometry / quality
        segs = []   # (a,b,wire idx)
        for i, W in enumerate(wires):
            for q in range(len(W) - 1):
                segs.append((tuple(W[q]), tuple(W[q + 1]), i))
        strokes = []
        for d in v['draw']:
            if d['t'] == 'line' and d.get('owner') not in ('wire', 'dot', 'bus'):
                for q in range(len(d['pts']) - 1):
                    strokes.append((tuple(d['pts'][q]), tuple(d['pts'][q + 1]), d.get('owner')))
        bodies = []
        for s in v['symbols']:
            if s['kind'] in ('gnd', 'vdd'):
                continue
            for b in s['body']:
                bodies.append((b, s['id']))
        wcls = {}
        for i, W in enumerate(wires):
            wcls[i] = uf.f(('w', i))
        ncross = 0
        cross_list = []
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                A, B = segs[a], segs[b]
                if A[2] == B[2]:
                    continue
                r = seg_inter(A[0], A[1], B[0], B[1])
                if r is None:
                    continue
                if wcls[A[2]] == wcls[B[2]]:
                    continue
                if r[0] == 'o':
                    R['5-cross'].append('%s: 서로 다른 선이 겹침' % v['id'])
                    continue
                cross_list.append((round(r[1], 1), round(r[2], 1)))
        # crossings are points where two different (unconnected) wires meet but are not joined
        allowed = self.conf.get('allow_cross', {}).get(v['id'], 0)
        ucross = sorted(set(cross_list))
        if len(ucross) > allowed:
            for pt in ucross:
                R['5-cross'].append('%s: 교차 %s (허용 %d개)' % (v['id'], pt, allowed))
        for (a, b, i) in segs:
            for (c, d, own) in strokes:
                r = seg_inter(a, b, c, d)
                if r is None:
                    continue
                if r[0] == 'o':
                    R['5-pierce'].append('%s: 선이 %s 의 획과 겹침' % (v['id'], own)); continue
                pt = (r[1], r[2])
                # touching at a pin tip is how the wire attaches
                if any(abs(pt[0] - p['x']) <= 0.6 and abs(pt[1] - p['y']) <= 0.6 for p in pins):
                    continue
                if any(abs(pt[0] - tuple(l['at'])[0]) <= 0.6 and abs(pt[1] - tuple(l['at'])[1]) <= 0.6 for l in labs if l['kind'] in ('power',)):
                    continue
                R['5-pierce'].append('%s: 선이 %s 의 획을 지남 %s' % (v['id'], own, (round(pt[0], 1), round(pt[1], 1))))
            for (bx, sid) in bodies:
                if seg_box(a, b, bx, 0):
                    R['5-pierce'].append('%s: 선이 %s 몸체를 관통' % (v['id'], sid))
        for i, W in enumerate(wires):
            if len(W) >= 3 or True:
                L = sum(abs(W[q + 1][0] - W[q][0]) + abs(W[q + 1][1] - W[q][1]) for q in range(len(W) - 1))
                man = abs(W[-1][0] - W[0][0]) + abs(W[-1][1] - W[0][1])
                if len(W) >= 3 and man > 0 and L > 1.5 * man + 1e-6:
                    R['5-kink'].append('%s: 꼬임 길이 %.0f > 1.5 x %.0f' % (v['id'], L, man))
                if len(W) >= 3:
                    for q in range(len(W) - 1):
                        sl = abs(W[q + 1][0] - W[q][0]) + abs(W[q + 1][1] - W[q][1])
                        if sl < 20 - 1e-6:
                            R['5-short'].append('%s: 꺾인 선분 %.0f < 20 at %s' % (v['id'], sl, W[q]))
                for q in range(len(W) - 1):
                    if not (abs(W[q][0] - W[q + 1][0]) < 1e-6 or abs(W[q][1] - W[q + 1][1]) < 1e-6):
                        R['5-kink'].append('%s: 비스듬한 선' % v['id'])
        # dots proximity + 4-way
        for a in range(len(dots)):
            for b in range(a + 1, len(dots)):
                dd = math.hypot(dots[a][0] - dots[b][0], dots[a][1] - dots[b][1])
                if dd < 20 - 1e-6:
                    R['5-dots'].append('%s: 접점 근접 %.1f' % (v['id'], dd))
        for d in dots:
            dirs = set()
            for (a, b, i) in segs:
                if on_seg(d, a, b):
                    for e in (a, b):
                        if math.hypot(e[0] - d[0], e[1] - d[1]) > 0.6:
                            dx, dy = e[0] - d[0], e[1] - d[1]
                            dirs.add(('x', 1 if dx > 0 else -1) if abs(dy) < 0.6 else ('y', 1 if dy > 0 else -1))
                    if all(math.hypot(e[0] - d[0], e[1] - d[1]) > 0.6 for e in (a, b)):
                        if abs(a[1] - b[1]) < 0.6:
                            dirs |= {('x', 1), ('x', -1)}
                        else:
                            dirs |= {('y', 1), ('y', -1)}
            if len(dirs) >= 4:
                R['5-dots'].append('%s: 4방향 접점 %s' % (v['id'], d))
        # free ends on the same line < 40
        ends = []
        for i, W in enumerate(wires):
            for e in (W[0], W[-1]):
                if any(abs(e[0] - p['x']) <= TOL and abs(e[1] - p['y']) <= TOL for p in pins):
                    continue
                if any(on_poly(e, W2) for j, W2 in enumerate(wires) if j != i):
                    continue
                if any(abs(e[0] - tuple(l['at'])[0]) <= TOL and abs(e[1] - tuple(l['at'])[1]) <= TOL for l in labs if l['kind'] in ('power', 'port', 'offpage')):
                    continue
                ends.append((e, wcls[i]))
        for a in range(len(ends)):
            for b in range(a + 1, len(ends)):
                (p, ca), (q, cb) = ends[a], ends[b]
                if ca == cb:
                    continue
                if (abs(p[1] - q[1]) < 1 or abs(p[0] - q[0]) < 1) and math.hypot(p[0] - q[0], p[1] - q[1]) < 40:
                    R['5-endline'].append('%s: 같은 직선 위 다른 넷의 자유 선 끝 %s %s' % (v['id'], p, q))
        # dash / width
        for d in v['draw']:
            if d['t'] == 'line' and d.get('dash'):
                R['11-dash'].append('%s: 점선' % v['id'])
            if d['t'] == 'line' and d.get('owner') == 'wire' and abs(d['w'] - 1.6) > 1e-6:
                R['11-dash'].append('%s: 배선 굵기 %s' % (v['id'], d['w']))
        # text overlap + inside
        tb = self.texts.get(v['id'], [])
        for a in range(len(tb)):
            A = tb[a]
            if A['x0'] < -1 or A['y0'] < -1 or A['x1'] > v['w'] + 1 or A['y1'] > v['h'] + 1:
                R['25-inside'].append('%s: 글자 "%s" 가 화면 밖' % (v['id'], A['s']))
            for b in range(a + 1, len(tb)):
                B = tb[b]
                ox = min(A['x1'], B['x1']) - max(A['x0'], B['x0'])
                oy = min(A['y1'], B['y1']) - max(A['y0'], B['y0'])
                if ox > 1.0 and oy > 1.0:
                    R['5-overlap'].append('%s: 글씨 겹침 "%s" / "%s"' % (v['id'], A['s'], B['s']))
        # names
        ports = set(cd['ports'])
        nets_all = set(allx) | ports
        concept_ids = {s_['id'] for s_ in v['symbols'] if (s_.get('info') or {}).get('concept') or (s_.get('info') or {}).get('virtual')}
        for k in ('devname', 'inst'):
            for d in v['draw']:
                if d['t'] == 'text' and d.get('cls') == k and d.get('owner') not in concept_ids:
                    nm = d['s']
                    base = re.sub(r'\s*\(.*\)$', '', nm)
                    if base not in elems and not nm.startswith('X_') and base not in self.cells:
                        R['14-names'].append('%s: 이름 %s 이(가) netlist에 없음' % (v['id'], nm))
        for l in labs:
            if l['kind'] in ('net', 'port', 'offpage', 'gray'):
                for n in expand(l['name']):
                    if n not in nets_all and n not in self.conf.get('extra_names', {}).get(v['id'], []):
                        R['14-names'].append('%s: 넷/포트 이름 %s 이(가) netlist에 없음' % (v['id'], n))
        # R/C values
        for s in v['symbols']:
            if s['kind'] in ('res', 'cap', 'varres', 'varcap') and s.get('members'):
                e = elems.get(s['members'][0])
                if e is None or e['kind'] not in ('res', 'cap'):
                    continue
                txt = [d['s'] for d in v['draw'] if d['t'] == 'text' and d.get('owner') == s['id'] and d.get('cls') == 'size']
                from netlist import fmt_si, si_equal
                if txt and not (txt[0] == e['value'] or txt[0] == fmt_si(e['value'])):
                    R['24-rcvalue'].append('%s: %s 값 %s != %s' % (v['id'], s['id'], txt[0], e['value']))
        # block-level: polarity, pin names, pin sides, block pins
        want_side = {'data_in': 'left', 'data_out': 'right', 'control': 'top', 'reference': 'left', 'clock': 'bottom'}
        for s in v['symbols']:
            info = s.get('info') or {}
            pc = info.get('pcls') or {}
            for p in s['pins']:
                c_ = pc.get(p['name'])
                if c_ and not info.get('gate') and p.get('side') != want_side[c_] and not (c_ == 'clock' and p.get('side') == 'left' and info.get('clock_left_ok')):
                    R['18-pinside'].append('%s: %s.%s (%s) 가 %s 쪽에 있음' % (v['id'], s['id'], p['name'], c_, p.get('side')))
            if s['kind'] in ('tri', 'box', 'inv') and s.get('members'):
                inst = elems.get(s['members'][0])
                if inst is None or inst['kind'] != 'inst':
                    continue
                pn = [p['name'] for p in s['pins']]
                sub = self.cells[inst['cell']]
                if not info.get('virtual'):
                    for n in pn:
                        if not all(x in sub['ports'] for x in expand(n)):
                            R['23-blockpins'].append('%s: %s 의 핀 이름 %s 이(가) 셀 %s 포트에 없음' % (v['id'], s['id'], n, inst['cell']))
                pol = info.get('pol')
                if pol:
                    res = self.POL.outputs(inst['cell'], pol['ins'], pol['outs'])
                    circles = [d for d in v['draw'] if d['t'] == 'circle' and d.get('owner') == s['id'] and abs(d['r'] - 4) < 1e-6]
                    for opin, onet in zip(pol['outpins'], pol['outs']):
                        if opin not in pol.get('logic', []):
                            continue
                        pp = [p for p in s['pins'] if p['name'] == opin][0]
                        has = any(abs(c['cy'] - pp['y']) < 1.0 and 0 < pp['x'] - c['cx'] < 40 for c in circles)
                        want = res.get(onet) == 'inv'
                        if has != want:
                            R['13-polarity'].append('%s: %s.%s 동그라미 %s, netlist 극성 %s' % (v['id'], s['id'], opin, '있음' if has else '없음', res.get(onet)))
                outs = [p for p in s['pins'] if p.get('side') == 'right']
                if len(outs) >= 2 and s['kind'] == 'tri':
                    for p in outs:
                        if not any(d['t'] == 'text' and d.get('owner') == s['id'] and d.get('cls') == 'pintext' and d['s'] == p['name'] for d in v['draw']):
                            R['15-pinnames'].append('%s: %s 출력 핀 이름 %s 없음' % (v['id'], s['id'], p['name']))
        # scene sha
        sha = hashlib.sha256(json.dumps({k: v[k] for k in ('title', 'w', 'h', 'draw', 'hot')}, sort_keys=True, default=list).encode()).hexdigest()
        return R, sha


def main():
    W, NL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
    cells, order = parse(NL)
    scenes = json.load(open(W + '/scenes.json'))
    texts = json.load(open(W + '/texts.json')) if os.path.exists(W + '/texts.json') else {}
    conf = json.load(open(W + '/conf.json'))
    C = Checker(cells, scenes, texts, conf)
    report = {'summary': {}, 'views': {}}
    tot = collections.Counter()
    npass = 0
    for v in scenes:
        R, sha = C.run(v)
        counts = {k: len(R.get(k, [])) for k, _ in CHECKS}
        for k in counts:
            tot[k] += counts[k]
        report['views'][v['id']] = {'scene_sha': sha, 'counts': counts, 'details': {k: R[k][:12] for k in R if R[k]}}
        if sum(counts.values()) == 0:
            npass += 1
    report['summary'] = {'views': len(scenes), 'connectivity_pass': sum(1 for v in report['views'].values() if v['counts']['1-conn'] + v['counts']['1-touch'] + v['counts']['6-port'] == 0),
                         'quality_pass': sum(1 for v in report['views'].values() if sum(v['counts'][k] for k in ('5-overlap', '5-pierce', '5-kink', '5-short', '5-dots', '5-cross', '5-endline')) == 0),
                         'all_zero_views': npass}
    report['totals'] = dict(tot)
    report['total_count'] = sum(tot.values())
    report['not_implemented'] = NOT_IMPLEMENTED
    json.dump(report, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(report['summary'], 'total', report['total_count'])
    print({k: n for k, n in tot.items() if n})


if __name__ == '__main__':
    main()
