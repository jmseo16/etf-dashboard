"""Plan §6 checker.  Connectivity is re-read from the drawn geometry only (wire polylines,
pin points, port/tag/rail names, junction dots) and compared with the netlist."""
import json, sys, math, itertools
from collections import defaultdict
from util import expand

NL = json.load(open(sys.argv[1]))['cells']
AN = json.load(open(sys.argv[2]))
VIEWS = json.load(open(sys.argv[3]))
OUT = sys.argv[4]
VISIBLE = {'data', 'clock', 'both', 'important'}
HIDDEN_OK = {'power', 'bias', 'general'}
EPS = 0.6

def on_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    cr = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
    if abs(cr) > EPS * max(1, math.hypot(x2 - x1, y2 - y1)): return False
    return min(x1, x2) - EPS <= x <= max(x1, x2) + EPS and min(y1, y2) - EPS <= y <= max(y1, y2) + EPS
def same(p, q): return abs(p[0] - q[0]) < EPS and abs(p[1] - q[1]) < EPS
def seg_cross(a, b, c, d):
    """proper interior intersection point of segments ab, cd (None if none / touching at ends)."""
    def orient(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    if (o1 > EPS and o2 < -EPS or o1 < -EPS and o2 > EPS) and (o3 > EPS and o4 < -EPS or o3 < -EPS and o4 > EPS):
        t = o3 / (o3 - o4)
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return None
def collinear_overlap(a, b, c, d):
    if not (on_seg(c, a, b) and on_seg(d, a, b)) and not (on_seg(a, c, d) and on_seg(b, c, d)) and \
       not (on_seg(c, a, b) and on_seg(a, c, d)) and not (on_seg(c, a, b) and on_seg(b, c, d)) and \
       not (on_seg(d, a, b) and on_seg(a, c, d)) and not (on_seg(d, a, b) and on_seg(b, c, d)):
        return 0
    def orient(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if abs(orient(a, b, c)) > 1 or abs(orient(a, b, d)) > 1: return 0
    L1 = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    ux, uy = (b[0] - a[0]) / L1, (b[1] - a[1]) / L1
    t = sorted([0, L1]); s = sorted([(c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy])
    return max(0, min(t[1], s[1]) - max(t[0], s[0]))
def seg_rect(a, b, r):
    """does segment ab pass through the interior of rect r (shrunk by 1)?"""
    x0, y0, x1, y1 = r[0] + 1, r[1] + 1, r[2] - 1, r[3] - 1
    for k in range(0, 41):
        t = k / 40
        x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        if x0 < x < x1 and y0 < y < y1: return True
    return False

def local_net(cell, ref):
    dev, term = ref
    for d in NL[cell]['devices']:
        if d['name'] == dev:
            if d['type'] == 'X': return d['pins'][term]
            return d[term]
    raise KeyError('%s: no device %s' % (cell, dev))
def dev_terms(d):
    if d['type'] == 'M': return {t: d[t] for t in ('D', 'G', 'S')}
    if d['type'] in 'RCL': return {'A': d['A'], 'B': d['B']}
    return dict(d['pins'])

def text_box(t):
    w = 0.6 * t['size'] * len(t['t']); h = t['size'] * 0.95
    x = t['x'] - (w if t['anchor'] == 'end' else w / 2 if t['anchor'] == 'middle' else 0)
    return [x, t['y'] - h * 0.78, x + w, t['y'] + h * 0.22]
def ov(a, b, pad=0):
    return min(a[2], b[2]) - max(a[0], b[0]) > pad and min(a[3], b[3]) - max(a[1], b[1]) > pad

def check(v):
    cell = v['cell']; cls = AN['local_classes'][cell]
    rep = {'view': v['id'], 'errors': [], 'warnings': []}
    E, W = rep['errors'], rep['warnings']
    wires = v['wires']
    # ---------------- union-find over wires / pins / ports / tags
    parent = {}
    def f(k):
        parent.setdefault(k, k)
        while parent[k] != k:
            parent[k] = parent[parent[k]]; k = parent[k]
        return k
    def u(a, b): parent[f(a)] = f(b)
    segs = []
    for i, w in enumerate(wires):
        f(('w', i))
        for a, b in zip(w['pts'], w['pts'][1:]): segs.append((i, a, b))
    tjunc = []          # points that need a dot
    def touch(p, i):
        """branches of wire i at point p"""
        P = wires[i]['pts']
        if same(p, P[0]) or same(p, P[-1]):
            return 1 if len(P) > 1 and not (same(P[0], P[-1])) else 2
        for k in range(1, len(P) - 1):
            if same(p, P[k]): return 2
        for a, b in zip(P, P[1:]):
            if on_seg(p, a, b): return 2
        return 0
    pts = []
    for s in v['syms']:
        for pn, p in s['pins'].items(): pts.append((('p', s['id'], pn), p))
    for k, pt in enumerate(v['ports']): pts.append((('port', k), [pt['x'], pt['y']]))
    for k, tg in enumerate(v['tags']): pts.append((('tag', k), [tg['x'], tg['y']]))
    cand = [w['pts'][0] for w in wires] + [w['pts'][-1] for w in wires] + [p for _, p in pts]
    uniq = []
    for p in cand:
        if not any(same(p, q) for q in uniq): uniq.append(p)
    for p in uniq:
        hit = [(i, touch(p, i)) for i in range(len(wires))]
        hit = [(i, t) for i, t in hit if t]
        for (i, _), (j, _) in zip(hit, hit[1:]): u(('w', i), ('w', j))
        npin = sum(1 for key, q in pts if same(p, q) and key[0] == 'p')
        br = sum(t for _, t in hit) + (1 if npin and hit else 0)
        if br >= 3: tjunc.append(tuple(p))
    for key, p in pts:
        f(key)
        for i in range(len(wires)):
            if touch(p, i): u(key, ('w', i))
        for key2, q in pts:
            if key2 != key and same(p, q): u(key, key2)
    tj = []
    for p in tjunc:
        if not any(same(p, q) for q in tj): tj.append(p)
    dots = v['dots']
    rep['missing_dots'] = [p for p in tj if not any(same(p, d) for d in dots)]
    rep['stray_dots'] = [d for d in dots if not any(same(d, p) for p in tj)]
    # ---------------- names on components
    names = defaultdict(set)
    for k, pt in enumerate(v['ports']): names[f(('port', k))].add(pt['name'])
    for k, tg in enumerate(v['tags']):
        names[f(('tag', k))].add('VSS' if tg['net'] == '__VSS__' else tg['net'])
    for r in v['rails']:
        for i, w in enumerate(wires):
            if w['cls'] == 'power' and same(w['pts'][0], [r['x0'], r['y']]) and same(w['pts'][-1], [r['x1'], r['y']]):
                names[f(('w', i))].add(r['net'])
    # merge components by name (label connectivity)
    byname = {}
    for c, ns in list(names.items()):
        for n in ns:
            if n in byname: u(c, byname[n])
            byname[n] = f(c)
    comp_names = defaultdict(set)
    for c, ns in names.items(): comp_names[f(c)] |= ns
    # ---------------- expected nets of pins
    comp_exp = defaultdict(list)
    sym_by_id = {s['id']: s for s in v['syms']}
    for s in v['syms']:
        for pn, slices in s['pinmap'].items():
            if not slices: continue
            tup = []
            for sl in slices:
                nets = {local_net(cell, r) for r in sl}
                if len(nets) != 1: E.append('%s.%s slice nets differ %s' % (s['id'], pn, sorted(nets)))
                tup.append(sorted(nets)[0])
            key = ('p', s['id'], pn)
            comp_exp[f(key)].append((s['id'] + '.' + pn, tuple(tup)))
            # connected?
            alone = all(f(key) != f(k2) for k2, _ in pts if k2 != key) and \
                not any(f(key) == f(('w', i)) for i in range(len(wires)))
            if alone: E.append('pin %s.%s (%s) is not connected/tagged' % (s['id'], pn, '/'.join(tup)))
    drawn_nets = set()
    for c, lst in comp_exp.items():
        tups = [t for _, t in lst]
        n = max(len(t) for t in tups)
        bt = [t * n if len(t) == 1 else t for t in tups]
        if any(t != bt[0] for t in bt):
            E.append('component joins different nets: ' + '; '.join('%s=%s' % (k, '/'.join(t)) for k, t in lst))
        for nm in comp_names.get(c, ()):
            ex = tuple(expand(nm)) if nm not in ('VSS', 'VDD') else (nm,)
            if len(ex) == 1: ex = ex * n
            if ex != bt[0] and not (len(set(bt[0])) == 1 and set(ex) == set(bt[0])):
                E.append('name %s on component but pins expect %s' % (nm, '/'.join(bt[0])))
        drawn_nets |= set(bt[0])
    for c, ns in comp_names.items():
        if c not in comp_exp:
            for nm in ns:
                if nm not in ('VDD', 'VSS'): W.append('name %s has no pin on it (dangling)' % nm)
            drawn_nets |= {x for nm in ns for x in expand(nm)}
    # split visible nets (same expected net in >1 component)
    seen = defaultdict(set)
    for c, lst in comp_exp.items():
        for _, t in lst:
            if len(t) == 1: seen[t[0]].add(c)
    for net, cs in seen.items():
        if len(cs) > 1 and set(cls.get(net, [])) & VISIBLE:
            E.append('visible net %s drawn in %d unconnected pieces' % (net, len(cs)))
    # ---------------- coverage / omission (§6-3, §6-4)
    scope = v.get('scope') or [d['name'] for d in NL[cell]['devices']]
    represented = defaultdict(list)
    for s in v['syms']:
        for r in s['represents']: represented[r].append(s['id'])
    omitted_items = {o['item'] for o in v['omitted']}
    for dn in scope:
        if dn not in represented and dn not in omitted_items:
            E.append('device %s neither drawn nor in omitted list' % dn)
        if len(represented.get(dn, [])) > 1: E.append('device %s in several symbols' % dn)
    devs = {d['name']: d for d in NL[cell]['devices']}
    for s in v['syms']:
        if not s['represents']: continue
        covered = set()
        for pn, slices in s['pinmap'].items():
            for sl in slices:
                for r in sl: covered.add(tuple(r))
        group = set(s['represents'])
        for dn in s['represents']:
            for t, net in dev_terms(devs[dn]).items():
                if (dn, t) in covered: continue
                c = set(cls.get(net, []))
                users = {d['name'] for d in NL[cell]['devices'] if net in dev_terms(d).values()}
                ports = set(NL[cell]['ports'])
                if users <= group and net not in ports:
                    continue                                     # bundle-internal net (§6-4)
                if c & VISIBLE:
                    E.append('%s: terminal %s.%s on visible net %s not drawn' % (s['id'], dn, t, net))
                elif net not in omitted_items and net not in drawn_nets and not any(
                        tg['net'] == net for tg in v['tags']):
                    E.append('%s: hidden terminal %s.%s net %s not in omitted list' % (s['id'], dn, t, net))
        # bundle-internal nets must not be used outside the bundle
        if len(group) > 1:
            for dn in group:
                for t, net in dev_terms(devs[dn]).items():
                    users = {d['name'] for d in NL[cell]['devices'] if net in dev_terms(d).values()}
                    if (dn, t) in covered or net in NL[cell]['ports']: continue
                    if users <= group and net in drawn_nets:
                        E.append('%s: bundle-internal net %s is drawn outside' % (s['id'], net))
    # nets of the scope: drawn or omitted, omitted only if hidden class
    scope_nets = set()
    for dn in scope: scope_nets |= set(dev_terms(devs[dn]).values())
    tagged = {tg['net'] for tg in v['tags'] if tg['kind'] == 'hidden'}
    for net in scope_nets:
        c = set(cls.get(net, []))
        if net in drawn_nets:
            if v['level'] == 'block' and not (c & VISIBLE) and net not in ('VDD', 'VSS'):
                E.append('block view draws hidden net %s (%s)' % (net, ','.join(c)))
            continue
        if net in tagged: continue
        users = [d for d in NL[cell]['devices'] if d['name'] in scope and net in dev_terms(d).values()]
        if all(d['name'] in omitted_items for d in users): continue
        if net in omitted_items:
            if c & VISIBLE: E.append('visible net %s is in omitted list' % net)
            continue
        if any(net in dev_terms(devs[r]).values() and len(sym_by_id[sid]['represents']) > 1
               for r, sids in represented.items() for sid in sids):
            continue                                              # bundle-internal
        E.append('net %s (%s) neither drawn nor omitted' % (net, ','.join(sorted(c))))
    for o in v['omitted']:
        if o['kind'] == 'net' and set(cls.get(o['item'], [])) & VISIBLE:
            E.append('omitted net %s is visible class' % o['item'])
    # ---------------- quality checks (§6-5)
    q = {}
    texts = [t for t in v['texts'] if t['t'].strip()]
    boxes = [text_box(t) for t in texts]
    q['text_overlap'] = [(texts[i]['t'], texts[j]['t']) for i, j in itertools.combinations(range(len(boxes)), 2)
                         if ov(boxes[i], boxes[j], 0.5)]
    tw_hits = []
    for k, b in enumerate(boxes):
        for w in wires:
            for a, c in zip(w['pts'], w['pts'][1:]):
                if seg_rect(a, c, [b[0] - 1, b[1] - 1, b[2] + 1, b[3] + 1]):
                    tw_hits.append(texts[k]['t']); break
        for s in v['syms']:
            if s['kind'] in ('box', 'amp', 'mark', 'tg', 'inv'): continue
            if ov(b, s['body'], 1): tw_hits.append(texts[k]['t'] + '@' + s['id'])
    q['text_on_wire_or_symbol'] = sorted(set(tw_hits))
    through = []
    for i, w in enumerate(wires):
        for a, c in zip(w['pts'], w['pts'][1:]):
            for s in v['syms']:
                if s['kind'] == 'gnd': continue
                if seg_rect(a, c, s['body']): through.append('%s through %s' % (w.get('net') or i, s['id']))
    q['wire_through_symbol'] = through
    twist, jog = [], []
    for i, w in enumerate(wires):
        p = w['pts']
        ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))
        md = abs(p[-1][0] - p[0][0]) + abs(p[-1][1] - p[0][1])
        if md > 0 and ln / md > 1.5 + 1e-9 and not w.get('loop'): twist.append('%s ratio %.2f' % (w.get('net') or i, ln / md))
        if len(p) > 2:
            for a, b in zip(p, p[1:]):
                if math.hypot(b[0] - a[0], b[1] - a[1]) < 20 - 1e-6:
                    jog.append('%s seg %.0f px' % (w.get('net') or i, math.hypot(b[0] - a[0], b[1] - a[1])))
    q['twist'] = twist; q['short_jog'] = jog
    rep['loop_wires_exempt_from_twist'] = [w.get('net') for w in wires if w.get('loop')]
    close = []
    for a, b in itertools.combinations(dots, 2):
        if math.hypot(a[0] - b[0], a[1] - b[1]) <= 20 + 1e-6: close.append([a, b])
    q['close_junction'] = close
    q['missing_dot'] = rep.pop('missing_dots'); q['stray_dot'] = rep.pop('stray_dots')
    crosses, allowed = [], []
    for (i, a, b), (j, c, d) in itertools.combinations(segs, 2):
        if i == j: continue
        p = seg_cross(a, b, c, d)
        if p:
            why = [al['why'] for al in v['allowed_cross'] if abs(al['x'] - p[0]) < 3 and abs(al['y'] - p[1]) < 3]
            (allowed if why else crosses).append({'at': [round(p[0], 1), round(p[1], 1)],
                                                  'nets': [wires[i].get('net'), wires[j].get('net')],
                                                  'why': why[0] if why else ''})
        elif collinear_overlap(a, b, c, d) > 1:
            crosses.append({'at': a, 'nets': [wires[i].get('net'), wires[j].get('net')], 'why': 'overlap'})
    q['avoidable_crossing'] = crosses; q['structural_crossing'] = allowed
    # symmetry
    sym = []
    for a, b, ax in v['sym_pairs']:
        sa, sb = sym_by_id[a], sym_by_id[b]
        xa, ya = sa['xy']; xb, yb = sb['xy']
        if abs(xb - (2 * ax - xa)) > 0.5 or abs(ya - yb) > 0.5: sym.append('%s/%s position' % (a, b))
        if sa.get('gate') and sb.get('gate') and sa['gate'] == sb['gate']: sym.append('%s/%s gate side' % (a, b))
    for axd in v['axes']:
        ax, xl, xr = axd['x'], axd.get('xl', -1e9), axd.get('xr', 1e9)
        segset = set()
        for i, w in enumerate(wires):
            for a, b in zip(w['pts'], w['pts'][1:]):
                segset.add((round(a[0]), round(a[1]), round(b[0]), round(b[1])))
                segset.add((round(b[0]), round(b[1]), round(a[0]), round(a[1])))
        for i, w in enumerate(wires):
            if i in v['asym_wires'] or w['cls'] == 'power': continue
            xs = [p[0] for p in w['pts']]
            if min(xs) < xl or max(xs) > xr: continue
            if not (axd['y0'] <= min(p[1] for p in w['pts']) and max(p[1] for p in w['pts']) <= axd['y1']): continue
            for a, b in zip(w['pts'], w['pts'][1:]):
                m = (round(2 * ax - a[0]), round(a[1]), round(2 * ax - b[0]), round(b[1]))
                if m not in segset:
                    sym.append('wire %s not mirrored about x=%s' % (w.get('net') or i, ax)); break
    q['symmetry'] = sym
    rep['quality'] = q
    rep['counts'] = {k: len(x) for k, x in q.items()}
    rep['connectivity_ok'] = not E
    return rep

reports = [check(v) for v in VIEWS]
json.dump({'views': reports}, open(OUT, 'w'), indent=1)
for r in reports:
    bad = {k: c for k, c in r['counts'].items() if c and k != 'structural_crossing'}
    print('%-26s conn=%s  errors=%d  %s  structural_x=%d' % (r['view'], 'OK' if r['connectivity_ok'] else 'FAIL',
          len(r['errors']), bad, r['counts']['structural_crossing']))
    for e in r['errors'][:12]: print('    E', e)
    for w in r['warnings'][:6]: print('    W', w)
