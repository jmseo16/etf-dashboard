"""Plan section 6: verification.
Re-reads connectivity ONLY from drawn geometry (wire polylines, pin coordinates, junction dots, labels/ports/power
symbols) and compares it with the netlist; then runs the quality checks.
Usage: verify.py <workdir> <netlist> <out verify_report.json>"""
import json, sys, re, math, itertools, collections
from netlist import parse

W, NL, OUTF = sys.argv[1], sys.argv[2], sys.argv[3]
cells, order = parse(NL)
A = json.load(open(W + '/analysis.json'))
CN = A['cellnet']
scenes = json.load(open(W + '/scenes.json'))
texts = json.load(open(W + '/texts.json'))
EPS = 0.6
HIDDEN = {'general_control', 'bias', 'power', 'unused', 'internal'}


def expand(name):
    groups = list(re.finditer(r'<(\d+):(\d+)>', name))
    if not groups:
        return [name]
    parts = []; last = 0; ranges = []
    for g in groups:
        parts.append(name[last:g.start()]); last = g.end()
        a, b = int(g.group(1)), int(g.group(2))
        ranges.append(list(range(a, b + 1)) if a <= b else list(range(a, b - 1, -1)))
    parts.append(name[last:])
    out = []
    for combo in itertools.product(*ranges):
        s = parts[0]
        for k, v in enumerate(combo):
            s += str(v) + parts[k + 1]
        out.append(s)
    return out


def collapse(vec):
    vec = tuple(vec)
    return (vec[0],) if len(set(vec)) == 1 else vec


def segs(pts):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def on_seg(p, a, b, tol=EPS):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(x - x1, y - y1) <= tol
    t = ((x - x1) * dx + (y - y1) * dy) / L2
    if t < -1e-9 or t > 1 + 1e-9:
        return False
    px, py = x1 + t * dx, y1 + t * dy
    return math.hypot(x - px, y - py) <= tol


def same(p, q, tol=EPS):
    return abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol


def seg_intersection(a, b, c, d):
    """proper intersection point of segments ab and cd (None if parallel/none)"""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1)), t, u
    return None


def seg_hits_box(a, b, box, shrink=1.0):
    x0, y0, x1, y1 = box[0] + shrink, box[1] + shrink, box[2] - shrink, box[3] - shrink
    if x0 >= x1 or y0 >= y1:
        return False
    # Liang-Barsky clip
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    p = [-dx, dx, -dy, dy]; q = [ax - x0, x1 - ax, ay - y0, y1 - ay]
    u0, u1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                u0 = max(u0, t)
            else:
                u1 = min(u1, t)
    return u1 - u0 > 1e-6


class UF:
    def __init__(self):
        self.p = {}
    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def u(self, a, b):
        self.p[self.f(a)] = self.f(b)


def local_net(cell, elem, term):
    for e in cells[cell]['elems']:
        if e['name'] == elem:
            if e['kind'] == 'inst':
                return e['pins'][term]
            return e['terms'][term]
    raise KeyError(elem)


def elem_of(cell, name):
    for e in cells[cell]['elems']:
        if e['name'] == name:
            return e
    return None


def check_view(v):
    cell = v['cell']
    cn = CN[cell]
    errs = []
    info = {}
    wires = v['wires']
    syms = [s for s in v['symbols'] if s.get('pins') is not None]
    pins = []
    for s in syms:
        for p in s.get('pins', []):
            pins.append((s, p))
    dots = [tuple(d) for d in v['dots']]
    labels = v['labels']
    # ---------------- 1. geometry -> nets ----------------
    uf = UF()
    W_ = ['w%d' % i for i in range(len(wires))]
    for i in range(len(wires)):
        uf.f(W_[i])
    # wire-wire connections (endpoint on other wire / shared vertex)
    junction_pts = collections.defaultdict(lambda: 0)
    for i, w in enumerate(wires):
        for end in (w['pts'][0], w['pts'][-1]):
            for j, w2 in enumerate(wires):
                if j == i:
                    continue
                for a, b in segs(w2['pts']):
                    if on_seg(end, a, b):
                        uf.u(W_[i], W_[j]); break
    # branch count at every candidate point
    cand = set()
    for w in wires:
        for p in w['pts']:
            cand.add((round(p[0], 1), round(p[1], 1)))
    for s, p in pins:
        cand.add((round(p['x'], 1), round(p['y'], 1)))
    for d in dots:
        cand.add((round(d[0], 1), round(d[1], 1)))
    def branches(P):
        n = 0
        for w in wires:
            pts = w['pts']
            for k, q in enumerate(pts):
                if same(P, q):
                    n += 1 if k in (0, len(pts) - 1) else 2
                    break
            else:
                for a, b in segs(pts):
                    if on_seg(P, a, b):
                        n += 2; break
        for s, p in pins:
            if same(P, (p['x'], p['y'])):
                n += 1
        return n
    missing_dot, extra_dot = [], []
    for P in cand:
        br = branches(P)
        has = any(same(P, d) for d in dots)
        if br >= 3 and not has:
            # a pin sitting exactly at the corner of its own lead counts as 2-branch: ignore pin+wire end only
            missing_dot.append(P)
        if has and br < 3:
            extra_dot.append(P)
    for d in dots:
        if branches(d) < 3 and d not in extra_dot:
            extra_dot.append(d)
    # pins -> wires
    pinnode = {}
    open_pins = []
    pin_mid = []
    for idx, (s, p) in enumerate(pins):
        key = 'p%d' % idx
        pinnode[idx] = key
        uf.f(key)
        hit = False
        for i, w in enumerate(wires):
            if same((p['x'], p['y']), w['pts'][0]) or same((p['x'], p['y']), w['pts'][-1]):
                uf.u(key, W_[i]); hit = True
            else:
                for a, b in segs(w['pts']):
                    if on_seg((p['x'], p['y']), a, b):
                        pin_mid.append((s['id'], p['name'])); uf.u(key, W_[i]); hit = True; break
        # pin touching another pin directly
        for jdx, (s2, p2) in enumerate(pins):
            if jdx != idx and same((p['x'], p['y']), (p2['x'], p2['y'])):
                uf.u(key, 'p%d' % jdx); hit = True
        if not hit:
            open_pins.append(idx)
    # names
    names = collections.defaultdict(set)   # root -> names
    label_unattached = []
    gray_on = {}
    for lb in labels:
        at = lb['at']
        attached = None
        for i, w in enumerate(wires):
            if any(on_seg(at, a, b) for a, b in segs(w['pts'])):
                attached = W_[i]; break
        if attached is None:
            for idx, (s, p) in enumerate(pins):
                if same(at, (p['x'], p['y'])):
                    attached = pinnode[idx]
                    if lb['kind'] == 'gray':
                        gray_on[idx] = lb['name']
                    break
        if attached is None:
            label_unattached.append(lb['name'])
            continue
        lb['_node'] = attached
    # merge by name
    byname = collections.defaultdict(list)
    for lb in labels:
        if '_node' in lb:
            nm = lb['name']
            byname[nm].append(lb['_node'])
    for nm, nodes in byname.items():
        for n in nodes[1:]:
            uf.u(nodes[0], n)
    for lb in labels:
        if '_node' in lb:
            names[uf.f(lb['_node'])].add(lb['name'])
    # open wire ends
    open_ends = []
    for i, w in enumerate(wires):
        for end in (w['pts'][0], w['pts'][-1]):
            ok = False
            for j, w2 in enumerate(wires):
                if j != i and any(on_seg(end, a, b) for a, b in segs(w2['pts'])):
                    ok = True; break
            if not ok:
                ok = any(same(end, (p['x'], p['y'])) for s, p in pins)
            if not ok:
                ok = any(on_seg(lb['at'], end, end, tol=EPS) or same(lb['at'], end) for lb in labels) or \
                     any(on_seg(tuple(lb['at']), w['pts'][0], w['pts'][-1]) and lb['kind'] in ('net', 'port') for lb in labels if '_node' in lb and lb['_node'] == W_[i])
            if not ok and w['cls'] == 'power' and any(lb['kind'] == 'power' and '_node' in lb and uf.f(lb['_node']) == uf.f(W_[i]) for lb in labels):
                ok = True      # supply rail drawn as a long bar
            if not ok:
                open_ends.append(end)
    # ---------------- 2. expected nets from the netlist ----------------
    pin_vec = {}
    decl_err = []
    for idx, (s, p) in enumerate(pins):
        vec = []
        for sl in p['terms']:
            nets = {local_net(cell, e, t) for e, t in sl}
            if len(nets) != 1:
                decl_err.append('%s.%s slice %s -> %s' % (s['id'], p['name'], sl, sorted(nets)))
            vec.append(sorted(nets)[0])
        pin_vec[idx] = collapse(vec)
    groups = collections.defaultdict(list)
    for idx in pin_vec:
        groups[uf.f(pinnode[idx])].append(idx)
    mismatch = []
    for root, idxs in groups.items():
        vecs = {pin_vec[i] for i in idxs}
        nm = names.get(root, set())
        if len(vecs) > 1:
            mismatch.append({'net_pins': ['%s.%s' % (pins[i][0]['id'], pins[i][1]['name']) for i in idxs], 'netlist': sorted(map(list, vecs))})
        for n in nm:
            ex = expand(n)
            rg = [(int(x), int(y)) for x, y in re.findall(r'<(\d+):(\d+)>', n)]
            if rg and all(x > y for x, y in rg):
                ex = ex[::-1]          # names are written <MSB:LSB>; slice vectors are listed LSB first
            ev = collapse(ex)
            for vv in vecs:
                if ev != vv:
                    mismatch.append({'name': n, 'pins': ['%s.%s' % (pins[i][0]['id'], pins[i][1]['name']) for i in idxs], 'netlist': list(vv)})
    # named nets without pins: name must be a net of the cell
    for root, nm in names.items():
        if root not in groups:
            for n in nm:
                for x in expand(n):
                    if x not in cn:
                        mismatch.append({'name': n, 'error': 'label names a net that does not exist in the cell'})
    # completeness: a netlist net must not be split into two drawn nets
    where = collections.defaultdict(set)
    for root, idxs in groups.items():
        for i in idxs:
            where[pin_vec[i]].add(root)
    split = {str(list(k)): len(r) for k, r in where.items() if len(r) > 1}
    # open pins: only allowed with a gray label (hidden net)
    bad_open = []
    for idx in open_pins:
        s, p = pins[idx]
        nm = names.get(uf.f(pinnode[idx]), set())
        if not nm:
            bad_open.append('%s.%s' % (s['id'], p['name']))
    # gray labels only on hidden nets
    gray_bad = [n for i, n in gray_on.items() if not (set(cn.get(n, [])) & HIDDEN)]
    # ---------------- 3. coverage / hidden pins / omitted list / bundles ----------------
    scope = v.get('scope')
    elems = [e for e in cells[cell]['elems']]
    if scope:
        elems = [e for e in elems if e['name'] in scope]
    covered = collections.Counter()
    for s in v['symbols']:
        for m in s.get('members', []):
            covered[m] += 1
    omitted_blocks = {o['block'] for o in v['omitted'] if 'block' in o}
    uncovered = [e['name'] for e in elems if covered[e['name']] == 0 and e['name'] not in omitted_blocks]
    double = [m for m, c in covered.items() if c > 1]
    # drawn terminals per element
    drawn = collections.defaultdict(set)
    for idx, (s, p) in enumerate(pins):
        for sl in p['terms']:
            for e, t in sl:
                drawn[e].add(t)
    hidden_bad = []
    bundle_bad = []
    for s in v['symbols']:
        mem = s.get('members', [])
        if not mem:
            continue
        for m in mem:
            e = elem_of(cell, m)
            if e is None:
                continue
            terms = e['pins'] if e['kind'] == 'inst' else {k: n for k, n in e['terms'].items() if not (e['kind'] == 'mos' and k == 'b')}
            for t, n in terms.items():
                if t in drawn[m]:
                    continue
                cls = set(cn.get(n, []))
                # internal to the symbol's bundle?
                users = set()
                for f in cells[cell]['elems']:
                    vals = f['pins'].values() if f['kind'] == 'inst' else [x for k, x in f['terms'].items() if not (f['kind'] == 'mos' and k == 'b')]
                    if n in vals:
                        users.add(f['name'])
                if n in cells[cell]['ports'] and not (cls & HIDDEN):
                    hidden_bad.append('%s.%s=%s (%s) not drawn' % (m, t, n, '/'.join(sorted(cls))))
                elif users <= set(mem):
                    continue      # internal net of the bundle / group
                elif cls & {'data', 'clock', 'important_control'}:
                    hidden_bad.append('%s.%s=%s (%s) not drawn' % (m, t, n, '/'.join(sorted(cls))))
                elif not (cls & HIDDEN):
                    hidden_bad.append('%s.%s=%s (%s) not drawn' % (m, t, n, '/'.join(sorted(cls))))
                elif 'internal' in cls and len(mem) > 1:
                    bundle_bad.append('%s: internal net %s used outside the bundle by %s' % (s['id'], n, sorted(users - set(mem))))
    # visible ports of the cell present as port glyphs?
    portnames = set()
    for lb in labels:
        if lb['kind'] == 'port':
            portnames |= set(expand(lb['name']))
    vis_ports = [p for p in cells[cell]['ports'] if set(cn.get(p, [])) & {'data', 'clock', 'important_control'}]
    if scope:
        sc_nets = set()
        for e in elems:
            sc_nets |= set(e['pins'].values() if e['kind'] == 'inst' else e['terms'].values())
        vis_ports = [p for p in vis_ports if p in sc_nets]
    missing_ports = [p for p in vis_ports if p not in portnames]
    hidden_ports_drawn = [p for p in portnames if p in cn and not (set(cn[p]) & {'data', 'clock', 'important_control'})]
    # omitted list = hidden classification (block views)
    om_nets = {o['net'] for o in v['omitted'] if 'net' in o}
    drawn_nets = set()
    for idx in pin_vec:
        drawn_nets |= set(pin_vec[idx])
    for lb in labels:
        drawn_nets |= set(expand(lb['name']))
    om_bad = []
    group_internal = set()
    for s in v['symbols']:
        mem = set(s.get('members', []))
        if len(mem) > 1:
            for f in cells[cell]['elems']:
                if f['name'] in mem:
                    for n in (f['pins'].values() if f['kind'] == 'inst' else f['terms'].values()):
                        users = {g['name'] for g in cells[cell]['elems'] if n in (g['pins'].values() if g['kind'] == 'inst' else g['terms'].values())}
                        if users <= mem and n not in cells[cell]['ports']:
                            group_internal.add(n)
    if v['level'] == 'block':
        for n, c in cn.items():
            if n in drawn_nets or n in group_internal:
                continue
            if set(c) & {'data', 'clock', 'important_control'}:
                om_bad.append('visible net %s not drawn' % n)
            elif n not in om_nets and not (set(c) <= {'internal'}):
                om_bad.append('hidden net %s missing from omitted list' % n)
    conn_errors = {
        'declaration_errors': decl_err, 'net_mismatch': mismatch, 'split_nets': split, 'open_pins': bad_open,
        'open_wire_ends': [list(map(lambda z: round(z, 1), e)) for e in open_ends], 'pin_on_wire_interior': pin_mid,
        'missing_junction_dot': [list(p) for p in missing_dot], 'superfluous_dot': [list(p) for p in extra_dot],
        'unattached_labels': label_unattached, 'gray_label_on_visible_net': gray_bad,
        'uncovered_elements': uncovered, 'elements_drawn_twice': double, 'visible_terminal_hidden': hidden_bad,
        'bundle_internal_net_used_outside': bundle_bad, 'missing_ports': missing_ports, 'hidden_ports_drawn': hidden_ports_drawn,
        'omitted_list_errors': om_bad,
    }
    n_err = sum(len(x) for x in conn_errors.values())
    # ---------------- 4. quality ----------------
    allsegs = []
    for i, w in enumerate(wires):
        for a, b in segs(w['pts']):
            allsegs.append((i, a, b))
    # crossings
    crossings = []
    for (i, a, b), (j, c, d) in itertools.combinations(allsegs, 2):
        if i == j:
            continue
        r = seg_intersection(a, b, c, d)
        if not r:
            continue
        P, t, u = r
        if 1e-6 < t < 1 - 1e-6 and 1e-6 < u < 1 - 1e-6:
            if any(same(P, dd, 1.0) for dd in dots):
                continue
            crossings.append(P)
    allowed = []
    avoidable = []
    for P in crossings:
        m = [a for a in v['allowed_cross'] if math.hypot(P[0] - a['at'][0], P[1] - a['at'][1]) <= 12]
        if m:
            allowed.append({'at': [round(P[0], 1), round(P[1], 1)], 'reason': m[0]['reason']})
        else:
            avoidable.append([round(P[0], 1), round(P[1], 1)])
    # wires through symbols
    through = []
    for s in v['symbols']:
        for bx in s.get('body', []):
            for (i, a, b) in allsegs:
                if seg_hits_box(a, b, bx, shrink=1.0):
                    through.append('%s by wire %d' % (s['id'], i))
    # twisted lines
    twisted = []
    for i, w in enumerate(wires):
        pts = w['pts']
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs(pts))
        man = abs(pts[-1][0] - pts[0][0]) + abs(pts[-1][1] - pts[0][1])
        if man > 0 and L / man > 1.5 + 1e-9:
            twisted.append({'wire': i, 'ratio': round(L / man, 2)})
    # short jogs
    jogs = []
    for i, w in enumerate(wires):
        if len(w['pts']) >= 3:
            for a, b in segs(w['pts']):
                if math.hypot(b[0] - a[0], b[1] - a[1]) < 20 - 1e-6:
                    jogs.append({'wire': i, 'len': round(math.hypot(b[0] - a[0], b[1] - a[1]), 1)})
    # close junctions
    close = []
    for p, q in itertools.combinations(dots, 2):
        if math.hypot(p[0] - q[0], p[1] - q[1]) < 20 - 1e-6:
            close.append([list(p), list(q)])
    # text overlap (measured bboxes)
    tb = {t['tid']: t for t in texts.get(v['id'], [])}
    tlist = [t for t in tb.values()]
    overlaps = []
    for a, b in itertools.combinations(tlist, 2):
        ix = min(a['x1'], b['x1']) - max(a['x0'], b['x0'])
        iy = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
        if ix > 0.5 and iy > 0.5:
            overlaps.append('"%s" x "%s"' % (a['s'], b['s']))
    # text vs lines (wires + symbol strokes + port glyph edges + rect borders)
    strokes = []
    for d in v['draw']:
        if d['t'] == 'line':
            for a, b in segs(d['pts']):
                strokes.append((a, b, d.get('owner')))
        elif d['t'] == 'poly' and d.get('owner') == 'port':
            pts = d['pts'] + [d['pts'][0]]
            for a, b in segs(pts):
                strokes.append((a, b, 'port'))
        elif d['t'] == 'rect':
            x, y, w_, h_ = d['x'], d['y'], d['w'], d['h']
            pts = [(x, y), (x + w_, y), (x + w_, y + h_), (x, y + h_), (x, y)]
            for a, b in segs(pts):
                strokes.append((a, b, d.get('owner')))
        elif d['t'] == 'circle' and d.get('owner') not in ('dot',):
            r = d['r']
            strokes.append(((d['cx'] - r, d['cy']), (d['cx'] + r, d['cy']), d.get('owner')))
    text_line = []
    for t in tlist:
        box_ = [t['x0'], t['y0'], t['x1'], t['y1']]
        for a, b, own in strokes:
            if seg_hits_box(a, b, box_, shrink=1.5):
                text_line.append('"%s" x line(%s)' % (t['s'], own))
                break
    # symmetry
    sym_v = []
    symd = {s['id']: s for s in v['symbols']}
    for g in v['symmetry']:
        ax = g['axis']
        for a, b in g['pairs']:
            sa, sb = symd.get(a), symd.get(b)
            if not sa or not sb:
                sym_v.append('pair %s/%s missing' % (a, b)); continue
            ia, ib = sa['info'], sb['info']
            if g['orient'] == 'v':
                if 'cx' in ia:
                    ok = abs((ia['cx'] + ib['cx']) / 2 - ax) < 0.6 and abs(ia['cy'] - ib['cy']) < 0.6 and ia['gate'] != ib['gate'] and sa['kind'] == sb['kind']
                else:
                    ok = abs((ia['x'] + ib['x']) / 2 - ax) < 0.6 and abs(ia['y'] - ib['y']) < 0.6
                if not ok:
                    sym_v.append('pair %s/%s not mirrored about x=%s' % (a, b, ax))
            else:
                ok = abs((ia['y0'] + ia['h'] / 2 + ib['y0'] + ib['h'] / 2) / 2 - ax) < 0.6 and abs(ia['x0'] - ib['x0']) < 0.6
                if not ok:
                    sym_v.append('pair %s/%s not mirrored about y=%s' % (a, b, ax))
        for a in g['self']:
            sa = symd.get(a)
            if not sa:
                continue
            ia = sa['info']
            cx = ia.get('cx', ia.get('x'))
            if abs(cx - ax) > 0.6:
                sym_v.append('%s not on axis' % a)
        # wire mirror check
        if g['orient'] == 'v':
            ymin = g.get('ymin', -1e9)
            ex = g.get('exempt_boxes', [])
            def clip(a, b):
                if a[1] < ymin and b[1] < ymin:
                    return None
                if a[1] < ymin:
                    a = (a[0] + (b[0] - a[0]) * (ymin - a[1]) / (b[1] - a[1]), ymin)
                if b[1] < ymin:
                    b = (b[0] + (a[0] - b[0]) * (ymin - b[1]) / (a[1] - b[1]), ymin)
                return a, b
            selfgate = [(p['x'], p['y']) for a in g['self'] if a in symd for p in symd[a]['pins'] if p['name'] == 'G']
            insegs = []
            for (i, a, b) in allsegs:
                if any(same(a, q) or same(b, q) for q in selfgate):
                    continue
                if min(a[0], b[0]) >= g['x0'] - 0.1 and max(a[0], b[0]) <= g['x1'] + 0.1:
                    c = clip(a, b)
                    if c and math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]) > 1:
                        if any(seg_hits_box(c[0], c[1], bx, shrink=0) or (bx[0] <= c[0][0] <= bx[2] and bx[1] <= c[0][1] <= bx[3]) for bx in ex):
                            continue
                        insegs.append(c)
            def covered_by(a, b):
                # mirrored segment must lie on the union of in-region segments (sample points)
                for k in range(11):
                    t = k / 10
                    P = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                    if not any(on_seg(P, c, d, tol=0.8) for c, d in insegs) and not any(on_seg(P, c, d, tol=0.8) for _, c, d in allsegs):
                        return False
                return True
            unmatched = 0
            for a, b in insegs:
                ma = (2 * ax - a[0], a[1]); mb = (2 * ax - b[0], b[1])
                if not covered_by(ma, mb):
                    unmatched += 1
            if unmatched:
                sym_v.append('%d wire segment(s) without mirror image about x=%s' % (unmatched, ax))
        else:
            for (i, a, b) in allsegs:
                if min(a[0], b[0]) >= g['x0'] and max(a[0], b[0]) <= g['x1']:
                    ma = (a[0], 2 * ax - a[1]); mb = (b[0], 2 * ax - b[1])
                    ok = all(any(on_seg((ma[0] + t / 10 * (mb[0] - ma[0]), ma[1] + t / 10 * (mb[1] - ma[1])), c, d, tol=0.8) for _, c, d in allsegs) for t in range(11))
                    if not ok:
                        sym_v.append('wire %d has no mirror image about y=%s' % (i, ax))
    quality = {
        'text_overlap': len(overlaps) + len(text_line), 'text_text_overlap': overlaps, 'text_line_overlap': text_line,
        'wire_through_symbol': through, 'symmetry_violations': sym_v, 'twisted_lines': twisted, 'short_jogs': jogs,
        'close_junctions': close, 'avoidable_crossings': avoidable, 'structural_crossings': allowed,
    }
    counts = {'text_overlap': len(overlaps) + len(text_line), 'wire_through_symbol': len(through), 'symmetry_violations': len(sym_v),
              'twisted_lines': len(twisted), 'short_jogs': len(jogs), 'close_junctions': len(close),
              'avoidable_crossings': len(avoidable), 'structural_crossings_allowed': len(allowed)}
    return {'view': v['id'], 'cell': cell, 'level': v['level'], 'title': v['title'],
            'connectivity': {'pass': n_err == 0, 'error_count': n_err, 'errors': {k: x for k, x in conn_errors.items() if x},
                             'drawn_nets': len(groups), 'drawn_pins': len(pins)},
            'quality_counts': counts, 'quality_details': {k: x for k, x in quality.items() if x and k != 'text_overlap'},
            'quality_pass': all(counts[k] == 0 for k in counts if k != 'structural_crossings_allowed')}


rep = [check_view(v) for v in scenes]
summary = {'views': len(rep), 'connectivity_pass': sum(r['connectivity']['pass'] for r in rep),
           'quality_pass': sum(r['quality_pass'] for r in rep)}
json.dump({'summary': summary, 'views': rep}, open(OUTF, 'w'), indent=1, ensure_ascii=False)
for r in rep:
    c = r['connectivity']
    print('%-12s conn=%s err=%d  %s' % (r['view'], 'PASS' if c['pass'] else 'FAIL', c['error_count'],
                                        {k: v for k, v in r['quality_counts'].items() if v}))
    if not c['pass']:
        for k, x in c['errors'].items():
            print('     ', k, str(x)[:600])
print(summary)
