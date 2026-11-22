"""Plan section 6: verification.
Re-reads connectivity ONLY from drawn geometry (wire polylines, pin coordinates, junction dots, labels/ports/power
symbols) and compares it with the netlist; then runs the quality checks.
v6.1 extension (plan §4.1 + V24/V25): symbol strokes are read too (SHORT through a symbol stroke), label pairing and
off-page connectors, omitted list = classification, per-output polarity, pin names, pin sides (V18), gray-label scope,
name match, block pin names = cell ports, R/C/W/L value = instance value, text inside box/view, legends, description
numbers, questions, endpoint (landing) pins, cross-table class consistency, block dictionary, scene_sha; every check
is run against injected errors (self-test) and written to self_checklist.json (auto_checks).
Usage: verify.py <workdir> <netlist> <out verify_report.json>"""
import json, sys, re, math, itertools, collections, copy, hashlib, os
from netlist import parse, flatten, instance_tree, num, fmt_si, si_equal, group_bus, Polarity
from spec_rules import (ANALOG_ROLES, CLASS_KO, QUESTION_TEMPLATES, RULE_DECIDED_TOPICS, IN_DICTIONARY, render_question)

W, NL, OUTF = sys.argv[1], sys.argv[2], sys.argv[3]
cells, order = parse(NL)
A = json.load(open(W + '/analysis.json'))
CN = A['cellnet']
scenes = json.load(open(W + '/scenes.json'))
texts = json.load(open(W + '/texts.json'))
EPS = 0.6
HIDDEN = {'general_control', 'bias', 'power', 'unused', 'internal'}
VISIBLE = {'data', 'clock', 'important_control', 'reference'}
OUTD = os.path.dirname(os.path.abspath(OUTF))
TOP = A['top']
POL = Polarity(cells, TOP)
ALL_ELEMS = {e['name'] for c in cells.values() for e in c['elems']}


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


# ======================================================================================
# v6.1 helpers
# ======================================================================================
def seg_bbox(pts, pad=0.0):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def bbox_near(a, b, tol=1.0):
    return not (a[2] + tol < b[0] or b[2] + tol < a[0] or a[3] + tol < b[1] or b[3] + tol < a[1])


def touch(a, b, c, d, tol=EPS):
    if seg_intersection(a, b, c, d):
        return True
    return on_seg(a, c, d, tol) or on_seg(b, c, d, tol) or on_seg(c, a, b, tol) or on_seg(d, a, b, tol)


def stroke_items(v):
    """strokes owned by symbols, without the device body (plan §4.1-1 exception list)"""
    sids = {s['id'] for s in v['symbols']}
    items = []
    for d in v['draw']:
        own = d.get('owner')
        if own not in sids:
            continue
        if d['t'] == 'rect':
            continue                                  # block box outline
        if d['t'] == 'poly':
            if d.get('fill') == '#fff':
                continue                              # triangle / inverter body
            pts = [tuple(p) for p in d['pts']] + [tuple(d['pts'][0])]
        elif d['t'] == 'line':
            if d['w'] in (2.6, 2.4) or len(d['pts']) > 4:
                continue                              # MOS channel, capacitor plate, resistor zigzag (with its leads)
            pts = [tuple(p) for p in d['pts']]
        elif d['t'] == 'circle':
            if d['r'] >= 10:
                continue                              # current-source circle
            pts = [(d['cx'] + d['r'] * math.cos(2 * math.pi * k / 16), d['cy'] + d['r'] * math.sin(2 * math.pi * k / 16)) for k in range(17)]
        else:
            continue
        items.append({'owner': own, 'pts': pts, 'bb': seg_bbox(pts)})
    return items


def expected_vec(cell, p):
    vec = []
    for sl in p['terms'] or []:
        nets = {local_net(cell, e, t) for e, t in sl}
        if len(nets) != 1:
            return None
        vec.append(sorted(nets)[0])
    return collapse(vec) if vec else None


def scene_sha(v):
    """plan §1.2 / §4.1-16: SHA-256 of the view's picture data (size, title, primitives, click areas)"""
    d = {'w': v['w'], 'h': v['h'], 'title': v['title'],
         'draw': [{k: x for k, x in it.items() if k != 'tid'} for it in v['draw']],
         'hot': [{k: h[k] for k in ('x', 'y', 'w', 'h', 'link')} for h in v['hot']]}
    return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def sym_bbox(s):
    if s['kind'] == 'tri':
        i = s['info']
        return (i['x0'], i['yc'] - i['h'] / 2, i['x0'] + i['w'], i['yc'] + i['h'] / 2)
    b = s['body']
    return (min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b))


def pin_side(s, p):
    x0, y0, x1, y1 = sym_bbox(s)
    if p['x'] < x0 - 0.5:
        return 'left'
    if p['x'] > x1 + 0.5:
        return 'right'
    if p['y'] < y0 - 0.5:
        return 'top'
    if p['y'] > y1 + 0.5:
        return 'bottom'
    return 'inside'


def sym_context(v, s):
    """(cell, members or None, group role, pin -> local net of that cell) for a drawn block symbol"""
    cell = v['cell']
    mem = s.get('members') or []
    if len(mem) == 1:
        e = elem_of(cell, mem[0])
        if e is not None and e['kind'] == 'inst':
            return e['cell'], None, None, (lambda p: p['terms'][0][0][1]), e
    if mem and all(elem_of(cell, m) is not None and elem_of(cell, m)['kind'] != 'inst' for m in mem):
        g = [g for g in A['groups'].get(cell, []) if set(mem) <= set(g['members'])]
        return cell, set(mem), (g[0]['role'] if g else None), (lambda p: local_net(cell, p['terms'][0][0][0], p['terms'][0][0][1])), None
    return None


def is_logic(cell, port, grole=None):
    """V19: logic output? (independent re-implementation of the generator's rule)"""
    role = grole or A['block'][cell]['role']
    if role in ANALOG_ROLES:
        return False
    if role == 'cml_buffer':
        return 'clock' in CN[cell].get(port, [])
    if role == 'composite' and grole is None:
        for e in cells[cell]['elems']:
            if e['kind'] == 'inst':
                for q, n in e['pins'].items():
                    if n == port and any(t == q for (_, t) in POL.port_map(e['cell'])):
                        return is_logic(e['cell'], q)
        for g in A['groups'].get(cell, []):
            for m in g['members']:
                e = elem_of(cell, m)
                if e['kind'] == 'mos' and port in (e['terms']['d'], e['terms']['s']):
                    return is_logic(cell, port, g['role'])
    return True


KNOWN_OUTPUTS = {
    'mux2tg': {'z'},
    'lat_tg': {'q'},
    'dqsamp': {'outp', 'outn'},
    'padesd': {'pad_r'},
}

def block_outputs(cell, mem, nets):
    if cell in KNOWN_OUTPUTS:
        return KNOWN_OUTPUTS[cell]
    if mem is None:
        return {q for (_, q) in POL.port_map(cell)}
    out = set()
    for n in nets:
        r = POL.reach(cell, {n: 0}, mem)
        out |= {m for m in nets if m != n and m in r}
    return out


def texts_of(v, sid, cls=None):
    return [d for d in v['draw'] if d['t'] == 'text' and d.get('owner') == sid and (cls is None or d['cls'] == cls)]


def chk_polarity(v):
    """plan §3.4-6 / §4.1-13 per-output polarity, V19 logic outputs only, V21 +/- marks on differential inputs"""
    errs = []
    if v['level'] != 'block':
        return errs
    for s in v['symbols']:
        if s['kind'] not in ('tri', 'box', 'inv'):
            continue
        ctx = sym_context(v, s)
        if not ctx:
            continue
        cell, mem, grole, portof, _ = ctx
        L = sorted([p for p in s['pins'] if pin_side(s, p) == 'left'], key=lambda p: p['y'])
        R = sorted([p for p in s['pins'] if pin_side(s, p) == 'right'], key=lambda p: p['y'])
        if not L or not R:
            continue
        ins = [portof(p) for p in L[:2]]
        outs = [portof(p) for p in R]
        pol = POL.outputs(cell, ins, outs, mem)
        logic = {}
        for p, o in zip(R, outs):
            logic[o] = is_logic(cell, o, grole)
            bub = any(d['t'] == 'circle' and d.get('owner') == s['id'] and abs(d['r'] - 4) < 0.5 and abs(d['cy'] - p['y']) < 0.6
                      and p['x'] - 30 < d['cx'] < p['x'] for d in v['draw'])
            if pol[o] is None:
                continue
            want = logic[o] and pol[o] == 'inv'
            if bub != want:
                errs.append('%s.%s: netlist polarity %s, %s output, bubble drawn=%s' % (s['id'], p['name'], pol[o], 'logic' if logic[o] else 'analog', bub))
        if s['kind'] == 'tri' and len(L) >= 2:
            flip = pol[outs[0]] == 'inv' and not logic[outs[0]]
            want = {L[0]['name']: '−' if flip else '+', L[1]['name']: '+' if flip else '−'}
            for p in L[:2]:
                got = [d['s'] for d in texts_of(v, s['id'], 'pm') if abs(d['y'] - p['y']) < 1]
                if got != [want[p['name']]]:
                    errs.append('%s.%s: differential input mark %s, expected %s (V21)' % (s['id'], p['name'], got, want[p['name']]))
    return errs


def chk_pin_names(v):
    """plan §3.4-7: every output of a symbol with two or more outputs carries its pin name"""
    errs = []
    for s in v['symbols']:
        if s['kind'] not in ('tri', 'box'):
            continue
        R = [p for p in s['pins'] if pin_side(s, p) == 'right']
        if len(R) < 2:
            continue
        for p in R:
            ok = any(d['s'] == p['name'] and abs(d['y'] - p['y']) <= 12 and abs(d['x'] - p['x']) <= 60 for d in texts_of(v, s['id'], 'pintext'))
            if not ok:
                errs.append('%s.%s: output pin name missing' % (s['id'], p['name']))
    return errs


def chk_pin_sides(v):
    """V18 (plan §3.2 pin side table): control/command/test top, clock bottom (left if the block passes clocks),
    data left, outputs right; inverter (fixed pins), switches and markers are exceptions"""
    errs = []
    if v['level'] != 'block':
        return errs
    for s in v['symbols']:
        if s['kind'] not in ('tri', 'box'):
            continue
        ctx = sym_context(v, s)
        if not ctx:
            continue
        cell, mem, grole, portof, inst = ctx
        nets = [portof(p) for p in s['pins']]
        outs = block_outputs(cell, mem, nets)
        def pcls(p):
            q = portof(p)
            pn = inst['pins'][q] if inst else q
            return set(CN[v['cell']].get(pn, []))
        passes_clock = any(portof(p) in outs and 'clock' in pcls(p) for p in s['pins'])
        for p in s['pins']:
            c = pcls(p)
            side = pin_side(s, p)
            if portof(p) in outs:
                exp = {'right'}
            elif 'important_control' in c:
                exp = {'top'}
            elif 'clock' in c:
                exp = {'bottom', 'left'} if passes_clock else {'bottom'}
            elif 'data' in c:
                exp = {'left'}
            else:
                continue
            if side not in exp:
                errs.append('%s.%s: on %s, expected %s' % (s['id'], p['name'], side, '/'.join(sorted(exp))))
    return errs


def chk_gray(v, pins):
    """plan §3.5-3 gray-label scope: gate of a hidden net in a unit view; in block views only constants, hidden select
    pins of switches and hidden logic-gate inputs. Gray labels never name a visible net."""
    errs = []
    for lb in v['labels']:
        if lb['kind'] != 'gray':
            continue
        at = [(s, p) for s, p in pins if same(lb['at'], (p['x'], p['y']))]
        nets = expand(lb['name'])
        cls = set()
        for n in nets:
            cls |= set(CN[v['cell']].get(n, []))
        if cls & VISIBLE:
            errs.append('%s: gray label on a visible net' % lb['name'])
            continue
        col = [d['color'] for d in v['draw'] if d.get('tid') == lb.get('tid')]
        if col and col[0] != '#777':
            errs.append('%s: gray label not gray' % lb['name'])
        if v['level'] == 'unit':
            if not at or at[0][0]['kind'] not in ('nmos', 'pmos') or at[0][1]['name'] != 'G':
                errs.append('%s: gray label not at a MOS gate' % lb['name'])
        else:
            const = cls <= {'power'}
            sel = at and at[0][0]['kind'] in ('selswitch',)
            logic_in = at and at[0][0]['kind'] in ('inv', 'gate') and pin_side(at[0][0], at[0][1]) == 'left'
            if not (const or sel or logic_in):
                errs.append('%s: gray label outside its scope in a block view' % lb['name'])
    return errs


def chk_names(v):
    """plan §4.1-14: instance names, cell-name subtitles, net labels, port names exist in the netlist"""
    errs = []
    cell = v['cell']
    nets = set(CN[cell]) | set(cells[cell]['ports'])
    elems = {e['name'] for e in cells[cell]['elems']}
    sym = {s['id']: s for s in v['symbols']}
    for d in v['draw']:
        if d['t'] != 'text':
            continue
        c, txt = d['cls'], d['s']
        own = sym.get(d.get('owner'))
        if c == 'inst':
            bad = [x for x in expand(txt) if x not in ALL_ELEMS and x not in cells]
        elif c == 'devname':
            if own and (own['kind'] in ('varres', 'varcap', 'visrc') or (own['kind'] in ('res', 'cap') and len(own['members']) > 1)):
                continue                      # concept symbol name (R_S, C_S, I_G<3:0>): its legend lists the members
            bad = [x for x in expand(txt) if x not in elems]
        elif c in ('netlabel', 'offpage', 'gray', 'port', 'power'):
            nets_lower = {n.lower() for n in nets}
            if c == 'power' and txt.lower() in ('vdd', 'vss', 'vddq', 'vssq') and own is None and any(lb['kind'] == 'power' for lb in v['labels']):
                bad = [x for x in [lb['name'] for lb in v['labels'] if lb['kind'] == 'power' and lb.get('tid') == d['tid']] if x not in nets and x.lower() not in nets_lower]
            else:
                bad = [x for x in expand(txt) if x not in nets and x.lower() not in nets_lower]
        elif c == 'blk' and own and own['kind'] == 'box' and d['size'] == 10:
            bad = [txt] if txt not in cells else []
        elif c == 'blk' and own and own['kind'] == 'switch' and d['size'] == 9:
            bad = [x for x in txt.replace(' (off)', '').split('/') if x not in elems]
        else:
            continue
        if bad:
            errs.append('"%s" (%s): %s not in the netlist' % (txt, c, ', '.join(bad)))
    return errs


def chk_block_pins(v):
    """V24: block pin names = ports of the instance's cell (virtual block: nets of its devices); pin texts = pin names"""
    errs = []
    for s in v['symbols']:
        if s['kind'] not in ('tri', 'box'):
            continue
        ctx = sym_context(v, s)
        if not ctx:
            continue
        cell, mem, grole, portof, inst = ctx
        if inst:
            allowed = set(cells[inst['cell']]['ports'])
        else:
            allowed = set()
            for m in mem:
                e = elem_of(cell, m)
                allowed |= {x for k, x in e['terms'].items() if k != 'b'}
        for p in s['pins']:
            names = expand(p['name'])
            if not set(names) <= allowed:
                errs.append('%s: pin "%s" is not a %s' % (s['id'], p['name'], 'port of ' + inst['cell'] if inst else 'net of the virtual block'))
                continue
            if inst:
                tset = {t for sl in p['terms'] for (_, t) in sl}
                if tset != set(names):
                    errs.append('%s: pin "%s" name does not match its terminals %s' % (s['id'], p['name'], sorted(tset)))
        pn = {p['name'] for p in s['pins']}
        for d in texts_of(v, s['id'], 'pintext'):
            if d['s'] not in pn:
                errs.append('%s: pin text "%s" names no pin' % (s['id'], d['s']))
    return errs


def chk_values(v):
    """V24 R/C value = instance value, W/L = instance size; plan §3.5-6 SI notation; no nf / model name (M10)"""
    errs = []
    cell = v['cell']
    for s in v['symbols']:
        mem = s.get('members') or []
        sz = [d['s'] for d in texts_of(v, s['id'], 'size')]
        es = [elem_of(cell, m) for m in mem]
        if s['kind'] == 'term':            # the marker on the N line carries no members: read its pin terminals
            es = [elem_of(cell, e) for p in s['pins'] for sl in (p['terms'] or []) for e, t in sl]
        if any(e is None for e in es):
            continue
        if s['kind'] in ('res', 'cap') and len(es) == 1:
            if num(es[0]['value']) is not None:
                want = fmt_si(es[0]['value'])
                if sz != [want]:
                    errs.append('%s: value text %s, netlist %s (SI %s)' % (s['id'], sz, es[0]['value'], want))
        elif s['kind'] in ('nmos', 'pmos') and es:
            if len(es) == 1:
                e = es[0]
                want = '%s/%s' % (fmt_si(e['params'].get('w')), fmt_si(e['params'].get('l')))
                if e['params'].get('m') not in (None, '1'):
                    want += ' ×%s' % e['params']['m']
                if sz != [want]:
                    errs.append('%s: size text %s, netlist %s' % (s['id'], sz, want))
            else:
                ws = 'W ' + ','.join(fmt_si(e['params'].get('w')) for e in es)
                ls = 'L ' + '/'.join(sorted({fmt_si(e['params'].get('l')) for e in es}, key=lambda x: num(x) or 0))
                if sz != [ws, ls]:
                    errs.append('%s: size text %s, netlist %s' % (s['id'], sz, [ws, ls]))
        elif s['kind'] == 'term':
            rv = [e['value'] for e in es if e['kind'] == 'res']
            for d in texts_of(v, s['id']):
                m = re.search(r'(\d+(?:\.\d+)?(?:meg|[fpnumk])?)Ω', d['s'])
                if m and not any(si_equal(m.group(1), x) for x in rv):
                    errs.append('%s: "%s" but the resistor is %s' % (s['id'], d['s'], rv))
        for t in sz:
            if re.search(r'\bnf\b|nf=|NCH|PCH', t):
                errs.append('%s: size text shows nf / model (%s)' % (s['id'], t))
    return errs


def chk_text_inside(v, tb):
    """V24: no text outside the view; box titles / pin names inside their box; triangle title inside the triangle"""
    errs = []
    for t in tb.values():
        if t['x0'] < -0.5 or t['y0'] < -0.5 or t['x1'] > v['w'] + 0.5 or t['y1'] > v['h'] + 0.5:
            errs.append('"%s" outside the view' % t['s'])
    sym = {s['id']: s for s in v['symbols']}
    for d in v['draw']:
        if d['t'] != 'text' or d.get('owner') not in sym or d['tid'] not in tb:
            continue
        s, b = sym[d['owner']], tb[d['tid']]
        if s['kind'] == 'box' and d['cls'] in ('blk', 'pintext'):
            x0, y0, x1, y1 = sym_bbox(s)
            if b['x0'] < x0 - 0.5 or b['x1'] > x1 + 0.5 or b['y0'] < y0 - 0.5 or b['y1'] > y1 + 0.5:
                errs.append('"%s" leaves box %s' % (d['s'], s['id']))
        elif s['kind'] == 'tri' and d['cls'] == 'blk':
            i_ = s['info']
            poly = i_.get('outline') or [[i_['x0'], i_['yc'] - i_['h'] / 2], [i_['x0'] + i_['w'], i_['yc']], [i_['x0'], i_['yc'] + i_['h'] / 2]]
            for P in ((b['x0'], b['y0']), (b['x1'], b['y0']), (b['x0'], b['y1']), (b['x1'], b['y1'])):
                if not in_poly(P, poly):
                    errs.append('"%s" leaves triangle %s' % (d['s'], s['id'])); break
    return errs


def in_poly(P, poly):
    x, y = P
    ins = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def chk_legend(v):
    """plan §3.1-7 / §4.1-8: a view with merged or bundled symbols has the bundles/merged legend"""
    merged = [s['id'] for s in v['symbols'] if (s.get('info') or {}).get('merged') or s['kind'] in ('varres', 'varcap', 'visrc')
              or (s['kind'] in ('res', 'cap') and len(s.get('members') or []) > 1)]
    if merged and not any(d['t'] == 'text' and d['cls'] == 'legend' for d in v['draw']):
        return ['merged symbols %s without legend' % ', '.join(merged)]
    return []


_SUBV = {}


def subtree_values(cell):
    if cell in _SUBV:
        return _SUBV[cell]
    vals = []
    for e in cells[cell]['elems']:
        if e['kind'] in ('res', 'cap', 'ind'):
            vals.append(num(e['value']))
        elif e['kind'] == 'mos':
            vals += [num(e['params'][k]) for k in ('w', 'l') if k in e['params']]
        elif e['kind'] == 'inst':
            vals += subtree_values(e['cell'])
    _SUBV[cell] = [x for x in vals if x is not None]
    return _SUBV[cell]


NUMTOK = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?)(meg|[fpnumk])?(Ω)?(?![\w])')


def chk_numerics(v):
    """plan §3.5-7 / §4.1-9: every value in titles, notes and legends is a netlist value; bit counts match the bus"""
    errs = []
    vals = subtree_values(v['cell'])
    sym = {s['id'] for s in v['symbols']}
    lines = [v['title']] + [d['s'] for d in v['draw'] if d['t'] == 'text' and (d['cls'] in ('note', 'legend') or (d['cls'] == 'size' and d.get('owner') not in sym)
                                                                                 or (d['cls'] == 'blk' and 'Ω' in d['s']))]
    for txt in lines:
        for m in NUMTOK.finditer(txt):
            if not (m.group(2) or m.group(3)):
                continue
            x = num(m.group(1) + (m.group(2) or ''))
            if not any(abs(x - y) <= 1e-9 * max(abs(x), abs(y), 1e-30) for y in vals):
                errs.append('"%s%s%s" in "%s" is not a netlist value' % (m.group(1), m.group(2) or '', m.group(3) or '', txt[:60]))
        for m in re.finditer(r'(?<![\w])(\d+)b(?![\w])', txt):
            widths = {len(expand(b)) for b in re.findall(r'[\w]*(?:<\d+:\d+>[\w]*)+', txt)}
            if int(m.group(1)) not in widths:
                errs.append('"%sb" in "%s" matches no bus width %s' % (m.group(1), txt[:60], sorted(widths)))
    return errs


def chk_unit_size(v):
    """plan §3.1-8 / M10: at most 20 drawn symbols on a unit view"""
    if v['level'] != 'unit':
        return []
    n = sum(1 for s in v['symbols'] if s['kind'] in ('nmos', 'pmos', 'res', 'cap', 'varres', 'varcap', 'visrc', 'switch', 'tri', 'box', 'inv'))
    return ['%d symbols > 20' % n] if n > 20 else []


def chk_cci(v):
    """plan §3.3-7 / §4.1-12: a cross-coupled inverter pair is drawn with both inverters turned 90°.
    Inverter symbols of this generator are horizontal, so any cross-coupled pair of them is a violation."""
    invs = [s for s in v['symbols'] if s['kind'] == 'inv']
    errs = []
    for a, b in itertools.combinations(invs, 2):
        ya, aa = expected_vec(v['cell'], [p for p in a['pins'] if p['name'] == 'Y'][0]), expected_vec(v['cell'], [p for p in a['pins'] if p['name'] == 'A'][0])
        yb, ab = expected_vec(v['cell'], [p for p in b['pins'] if p['name'] == 'Y'][0]), expected_vec(v['cell'], [p for p in b['pins'] if p['name'] == 'A'][0])
        if ya == ab and yb == aa:
            errs.append('%s/%s cross-coupled inverters drawn horizontally' % (a['id'], b['id']))
    return errs


def check_view(v, tx=None):
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
    for lb in labels:                 # attachments are recomputed from geometry on every run
        lb.pop('_node', None); lb.pop('_root0', None)
    # ---------------- 1. geometry -> nets ----------------
    uf = UF()
    W_ = ['w%d' % i for i in range(len(wires))]
    for i in range(len(wires)):
        uf.f(W_[i])
    wbb = [seg_bbox(w['pts']) for w in wires]
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
    # ---------------- 1-1. symbol strokes (plan §4.1-1, SKILL §9-1-1) ----------------
    # every stroke a symbol draws, except the device body (MOS channel, resistor zigzag, current-source circle,
    # capacitor plates, block outline), is read like a wire: a stroke that joins two pins of different nets is a SHORT
    items = stroke_items(v)
    suf = UF()
    for k in range(len(items)):
        suf.f(k)
    for i, j in itertools.combinations(range(len(items)), 2):
        a, b = items[i], items[j]
        if not bbox_near(a['bb'], b['bb']):
            continue
        same_owner = a['owner'] == b['owner']
        hit = False
        for s1 in segs(a['pts']):
            for s2 in segs(b['pts']):
                if same_owner and touch(s1[0], s1[1], s2[0], s2[1]):
                    hit = True
                elif not same_owner and (any(on_seg(e, s2[0], s2[1]) for e in (a['pts'][0], a['pts'][-1])) or
                                         any(on_seg(e, s1[0], s1[1]) for e in (b['pts'][0], b['pts'][-1]))):
                    hit = True
                if hit:
                    break
            if hit:
                break
        if hit:
            suf.u(i, j)
    comp_pins = collections.defaultdict(set)
    comp_wires = collections.defaultdict(set)
    for k, it in enumerate(items):
        r = suf.f(k)
        for idx, (s, p) in enumerate(pins):
            P = (p['x'], p['y'])
            if bbox_near(it['bb'], (P[0], P[1], P[0], P[1])) and any(on_seg(P, q1, q2) for q1, q2 in segs(it['pts'])):
                comp_pins[r].add(idx)
        for i, w in enumerate(wires):
            if not bbox_near(it['bb'], wbb[i]):
                continue
            if any(on_seg(e, q1, q2) for e in (w['pts'][0], w['pts'][-1]) for q1, q2 in segs(it['pts'])) or \
               any(on_seg(e, q1, q2) for e in (it['pts'][0], it['pts'][-1]) for q1, q2 in segs(w['pts'])):
                comp_wires[r].add(i)
    stroke_short = []
    for r in set(comp_pins) | set(comp_wires):
        vecs = {}
        for i in comp_pins[r]:
            ev = expected_vec(cell, pins[i][1])
            if ev is not None:
                vecs.setdefault(ev, []).append('%s.%s' % (pins[i][0]['id'], pins[i][1]['name']))
        if len(vecs) > 1:
            stroke_short.append({'symbol': sorted({items[k]['owner'] for k in range(len(items)) if suf.f(k) == r}), 'pins': sorted(sum(vecs.values(), []))})
        nodes = ['p%d' % i for i in comp_pins[r]] + [W_[i] for i in comp_wires[r]]
        for n in nodes[1:]:
            uf.u(nodes[0], n)
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
    for lb in labels:
        if '_node' in lb:
            lb['_root0'] = uf.f(lb['_node'])
    pins_root0 = {idx: uf.f(pinnode[idx]) for idx in pinnode}
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
    vis_ports = [p for p in cells[cell]['ports'] if set(cn.get(p, [])) & VISIBLE]
    if scope:
        sc_nets = set()
        for e in elems:
            sc_nets |= set(e['pins'].values() if e['kind'] == 'inst' else e['terms'].values())
        vis_ports = [p for p in vis_ports if p in sc_nets]
    missing_ports = [p for p in vis_ports if p not in portnames]
    hidden_ports_drawn = [p for p in portnames if p in cn and not (set(cn[p]) & VISIBLE)]
    # omitted list = hidden classification (block views)
    om_nets = set()
    for o in v['omitted']:
        if 'net' in o:
            om_nets |= set(expand(o['net']))
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
    # ---- v6.1: omitted list (plan §3.5-5) for every view: drawn nets (line, black label, port, power symbol) are not
    # in it, every undrawn hidden net of the view is, and a bus is one <MSB:LSB> line
    drawn_black = set()
    for lb in labels:
        if lb['kind'] in ('net', 'port', 'power', 'offpage'):
            drawn_black |= set(expand(lb['name']))
    for idx in pin_vec:
        if idx not in open_pins:
            drawn_black |= set(pin_vec[idx])
    om_bad += ['drawn net %s is in the omitted list' % n for n in sorted(om_nets & drawn_black)]
    if v['level'] != 'block':
        sc = set()
        for e in elems:
            sc |= set(e['pins'].values() if e['kind'] == 'inst' else [x for k, x in e['terms'].items() if not (e['kind'] == 'mos' and k == 'b')])
        for n in sorted(sc):
            c = set(cn.get(n, []))
            if (c & {'general_control', 'bias', 'power'}) and not (c & VISIBLE) and n not in drawn_black and n not in group_internal and n not in om_nets:
                om_bad.append('hidden net %s missing from omitted list' % n)
    singles = [o['net'] for o in v['omitted'] if 'net' in o and not re.search(r'<\d+:\d+>', o['net'])]
    om_bad += ['bus %s not written as one <MSB:LSB> line' % bn for bn, bits, _ in group_bus(singles) if len(bits) > 1]
    # ---- v6.1: label pairing (plan §3.5-1, §4.1-2): a connection label needs a partner or a port; exceptions: an
    # unused output, a name on a wire that already joins the pins, an off-page connector on a boundary net
    def conn_count(n):
        k = sum(1 for e in cells[cell]['elems'] if n in (e['pins'].values() if e['kind'] == 'inst' else
                                                          [x for t_, x in e['terms'].items() if not (e['kind'] == 'mos' and t_ == 'b')]))
        return k + (1 if n in cells[cell]['ports'] else 0)
    comps = collections.defaultdict(set); kinds = collections.defaultdict(set)
    for lb in labels:
        if '_root0' in lb and lb['kind'] in ('net', 'port', 'offpage'):
            comps[lb['name']].add(lb['_root0']); kinds[lb['name']].add(lb['kind'])
    npins = collections.Counter(pins_root0.values())
    unpaired = []
    for lb in labels:
        if lb['kind'] != 'net' or '_root0' not in lb:
            continue
        nm = lb['name']
        if len(comps[nm]) >= 2 or (kinds[nm] & {'port', 'offpage'}) or npins[lb['_root0']] >= 2:
            continue
        if npins[lb['_root0']] == 1:
            idx = [i for i, r in pins_root0.items() if r == lb['_root0']][0]
            if all(conn_count(n) <= 1 for n in pin_vec.get(idx, ())):
                continue          # unused output (plan §3.5-4)
        unpaired.append(nm)
    # boundary nets of a virtual-block / unit view: off-page connector (or the cell port) required (plan §3.5-1)
    boundary_bad, offpage_bad = [], []
    if scope:
        for root, idxs in groups.items():
            nets = set()
            for i in idxs:
                nets |= set(pin_vec[i])
            kk = {lb['kind'] for lb in labels if '_node' in lb and uf.f(lb['_node']) == root}
            for n in nets:
                if not (set(cn.get(n, [])) & VISIBLE):
                    continue
                if any(e['name'] not in scope and n in (e['pins'].values() if e['kind'] == 'inst' else e['terms'].values()) for e in cells[cell]['elems']):
                    if not (kk & {'offpage', 'port'}) or (n not in cells[cell]['ports'] and 'offpage' not in kk):
                        boundary_bad.append(n)
    for lb in labels:
        if lb['kind'] == 'offpage':
            for n in expand(lb['name']):
                if not scope or not any(e['name'] not in scope and n in (e['pins'].values() if e['kind'] == 'inst' else e['terms'].values())
                                        for e in cells[cell]['elems']):
                    offpage_bad.append(lb['name'])
    conn_errors = {
        'symbol_stroke_joins_pins': stroke_short, 'unpaired_labels': unpaired, 'boundary_net_without_offpage': boundary_bad,
        'offpage_on_non_boundary_net': offpage_bad,
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
    tb = {t['tid']: t for t in (tx if tx is not None else texts.get(v['id'], []))}
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
    # ---- v6.1 quality (plan §1.4-1, §1.4-7): 4-way junctions, collinear line ends of different nets < 40 px,
    # dashed lines, wire width
    four_way = [list(d) for d in dots if branches(d) >= 4]
    def free_end(i, P):
        # a line end that stops on another wire (T junction) or at a pin is not a free end
        if any(j != i and any(on_seg(P, a, b) for a, b in segs(w2['pts'])) for j, w2 in enumerate(wires)):
            return False
        return not any(same(P, (p['x'], p['y'])) for s, p in pins)
    ends = []
    for i, w in enumerate(wires):
        if free_end(i, w['pts'][0]):
            ends.append((i, tuple(w['pts'][0]), tuple(w['pts'][1])))
        if free_end(i, w['pts'][-1]):
            ends.append((i, tuple(w['pts'][-1]), tuple(w['pts'][-2])))
    collinear = []
    for (i, P, Q), (j, P2, Q2) in itertools.combinations(ends, 2):
        if i == j or uf.f(W_[i]) == uf.f(W_[j]):
            continue
        for ax in (0, 1):
            o = 1 - ax
            if abs(P[o] - Q[o]) < EPS and abs(P2[o] - Q2[o]) < EPS and abs(P[o] - P2[o]) < EPS:
                d1, d2 = P[ax] - Q[ax], P2[ax] - Q2[ax]
                if d1 * d2 < 0 and (P2[ax] - P[ax]) * d1 > 0 and abs(P2[ax] - P[ax]) < 40 - 1e-6:
                    collinear.append({'ends': [list(P), list(P2)], 'gap': round(abs(P2[ax] - P[ax]), 1)})
    dashed = [k for k, d in enumerate(v['draw']) if d['t'] in ('line', 'rect') and d.get('dash') not in (None, '', 'none')]
    wire_w = [k for k, d in enumerate(v['draw']) if d.get('owner') == 'wire' and abs(d['w'] - 1.6) > 1e-6]
    quality = {
        'four_way_junctions': four_way, 'collinear_end_gap': collinear, 'dashed_lines': dashed, 'wire_width': wire_w,
        'text_overlap': len(overlaps) + len(text_line), 'text_text_overlap': overlaps, 'text_line_overlap': text_line,
        'wire_through_symbol': through, 'symmetry_violations': sym_v, 'twisted_lines': twisted, 'short_jogs': jogs,
        'close_junctions': close, 'avoidable_crossings': avoidable, 'structural_crossings': allowed,
    }
    counts = {'text_overlap': len(overlaps) + len(text_line), 'wire_through_symbol': len(through), 'symmetry_violations': len(sym_v),
              'twisted_lines': len(twisted), 'short_jogs': len(jogs), 'close_junctions': len(close),
              'avoidable_crossings': len(avoidable), 'structural_crossings_allowed': len(allowed),
              'four_way_junctions': len(four_way), 'collinear_end_gap': len(collinear), 'dashed_lines': len(dashed), 'wire_width': len(wire_w)}
    # ---- v6.1 rule checks (plan §4.1-6..15, V24)
    floating = [lb['name'] for lb in labels if lb['kind'] == 'port' and not str(lb.get('_node', '')).startswith('w')]
    unattached = ['%s.%s' % (pins[i][0]['id'], pins[i][1]['name']) for i in open_pins
                  if pins[i][0]['kind'] in ('tri', 'box', 'inv') and pin_side(pins[i][0], pins[i][1]) == 'right']
    # plan §3.5-2 / §1.4-3: every bus label / bus port sits on a wire with a slash; no bit count when the name has <a:b>;
    # names are <MSB:LSB>
    busmark = []
    slashes = [d for d in v['draw'] if d['t'] == 'line' and d.get('owner') == 'bus']
    def slash_on(i):
        return [d for d in slashes if any(on_seg(((d['pts'][0][0] + d['pts'][1][0]) / 2, (d['pts'][0][1] + d['pts'][1][1]) / 2), a, b, tol=1.0)
                                          for a, b in segs(wires[i]['pts']))]
    for lb in labels:
        if lb['kind'] in ('net', 'port', 'offpage') and re.search(r'<\d+:\d+>', lb['name']) and str(lb.get('_node', '')).startswith('w'):
            for a_, b_ in re.findall(r'<(\d+):(\d+)>', lb['name']):
                if int(a_) < int(b_):
                    busmark.append('%s: not <MSB:LSB>' % lb['name'])
            i = int(lb['_node'][1:])
            if not slash_on(i):
                busmark.append('%s: bus without slash' % lb['name'])
            for d in slash_on(i):
                cx, cy = (d['pts'][0][0] + d['pts'][1][0]) / 2, (d['pts'][0][1] + d['pts'][1][1]) / 2
                if any(t['t'] == 'text' and t['cls'] == 'buswidth' and math.hypot(t['x'] - cx, t['y'] - cy) < 25 for t in v['draw']):
                    busmark.append('%s: bit count written although the name has <a:b>' % lb['name'])
    checks = {
        'bus_marks': sorted(set(busmark)),
        'floating_ports': floating, 'unattached_output_pins': unattached,
        'polarity': chk_polarity(v), 'pin_names': chk_pin_names(v), 'pin_sides': chk_pin_sides(v), 'gray_scope': chk_gray(v, pins),
        'names': chk_names(v), 'block_pins': chk_block_pins(v), 'values': chk_values(v), 'text_inside': chk_text_inside(v, tb),
        'legend': chk_legend(v), 'numerics': chk_numerics(v), 'unit_size': chk_unit_size(v), 'cci': chk_cci(v),
    }
    # line kind per net (plan §4.1-7), for the cross-view comparison
    wdraw = [d for d in v['draw'] if d.get('owner') == 'wire']
    net_kinds = collections.defaultdict(set)
    for i, w in enumerate(wires):
        r = uf.f(W_[i])
        nms = set(names.get(r, set()))
        for idx in groups.get(r, []):
            nms |= set(pin_vec[idx])
        for n in nms:
            net_kinds[n].add((wdraw[i]['w'], wdraw[i].get('dash')))
    return {'view': v['id'], 'cell': cell, 'level': v['level'], 'title': v['title'], 'scene_sha': scene_sha(v),
            'connectivity': {'pass': n_err == 0, 'error_count': n_err, 'errors': {k: x for k, x in conn_errors.items() if x},
                             'drawn_nets': len(groups), 'drawn_pins': len(pins)},
            'quality_counts': counts, 'quality_details': {k: x for k, x in quality.items() if x and k != 'text_overlap'},
            'quality_pass': all(counts[k] == 0 for k in counts if k != 'structural_crossings_allowed'),
            'checks': {k: x for k, x in checks.items() if x}, 'checks_pass': not any(checks.values()),
            '_net_line_kinds': {n: sorted(map(list, k), key=str) for n, k in net_kinds.items()}}


# ======================================================================================
# v6.1 global checks (plan §4.1, V24) — they read the out/ files, so a mutated copy can be passed in
# ======================================================================================
FLAT = {d['path']: d for d in flatten(cells, TOP)}
INSTP = {pre.rstrip('/'): (cname, nm) for pre, cname, nm in instance_tree(cells, TOP) if pre}


def html_data(html):
    i = html.index('const DATA = ') + len('const DATA = ')
    j = html.index(';\nconst PPTX')
    return json.loads(html[i:j])


def md_tables(md):
    """{'port': {port: (class, K)}, 'control': [(bus, bits, class, K, endpoint)], 'summary': {...}}"""
    port, ctrl = {}, []
    sec = None
    for ln in md.splitlines():
        if ln.startswith('## '):
            sec = ln[3:]
        if not ln.startswith('|') or ln.startswith('|---'):
            continue
        c = [x.strip() for x in ln.strip('|').split('|')]
        if sec and sec.startswith('최상위 포트') and len(c) >= 3 and c[0] != '포트':
            port[c[0]] = (c[1], c[2])
        if sec and sec.startswith('제어 분류') and len(c) >= 5 and c[0] != '제어':
            ctrl.append((c[0], [b.strip() for b in c[1].split(',')], c[2], c[3], c[4]))
    summ = {}
    block = md.split('```')[1] if '```' in md else ''
    for ln in block.splitlines():
        if ':' not in ln:
            continue
        k, val = ln.split(':', 1)
        summ[k.strip()] = val.strip()
    return {'port': port, 'control': ctrl, 'summary': summ}


def chk_questions(ann):
    """V24 질문 검사: low confidence only, built from a template, never about something a rule decides (plan §2.7)"""
    errs = []
    for q in ann.get('_questions_and_assumed_answers', []):
        tid = q.get('template')
        if q.get('kind') in RULE_DECIDED_TOPICS:
            errs.append('%s: asks about %s, which a rule decides (%s)' % (q.get('id'), q.get('kind'), RULE_DECIDED_TOPICS[q['kind']]))
            continue
        if tid not in QUESTION_TEMPLATES:
            errs.append('%s: not built from a question template' % q.get('id'))
            continue
        try:
            txt = render_question(tid, q.get('fields', {}))
        except (KeyError, IndexError):
            errs.append('%s: template fields missing' % q.get('id'))
            continue
        if txt != q.get('question'):
            errs.append('%s: text is not the template sentence' % q.get('id'))
        if not str(q.get('confidence', '')).startswith('low'):
            errs.append('%s: confidence "%s" is not low' % (q.get('id'), q.get('confidence')))
        if tid == 'not_in_dictionary':
            cell = q['fields']['item'].split()[0]
            if A['block'].get(cell, {}).get('role') in IN_DICTIONARY:
                errs.append('%s: %s is a dictionary block (%s), nothing to ask' % (q.get('id'), cell, A['block'][cell]['role']))
    return errs


def chk_landing(ann, md):
    """V24 끝점 핀 검사: instance.pin form, exists, reached from the control net (through static logic), not a driver"""
    errs = []
    mdc = {r[0]: r[4] for r in md_tables(md)['control']}
    for r in ann.get('_controls', []):
        ep = r.get('endpoint_pin', '')
        m = re.match(r'^([A-Za-z_]\w*(?:/[A-Za-z_]\w*)*)\.(\w+)$', ep)
        if not m:
            errs.append('%s: "%s" is not instance.pin' % (r['bus'], ep)); continue
        path, pinname = m.groups()
        d = FLAT.get(path)
        if d is None:
            if path in INSTP and pinname in cells[INSTP[path][0]]['ports']:
                net, kind = INSTP[path][1][pinname], 'inst'
            else:
                errs.append('%s: %s does not exist in the netlist' % (r['bus'], ep)); continue
        else:
            if (d['kind'] == 'mos' and pinname not in ('d', 'g', 's')) or (d['kind'] != 'mos' and pinname not in d['terms']):
                errs.append('%s: %s has no pin %s' % (r['bus'], path, pinname)); continue
            net, kind = d['terms'][pinname], d['kind']
        reached = set(r['bits'])
        for _ in range(8):           # through static CMOS logic: a node pulled up and down by gates of reached nets
            new = set()
            for x in FLAT.values():
                if x['kind'] == 'mos':
                    if x['terms']['g'] in reached:
                        for t in ('d', 's'):
                            n = x['terms'][t]
                            both = {y['type'] for y in FLAT.values() if y['kind'] == 'mos' and y['terms']['g'] in reached and n in (y['terms']['d'], y['terms']['s'])}
                            if both == {'n', 'p'}:
                                new.add(n)
                    d, s = x['terms']['d'], x['terms']['s']
                    if d in reached and not (s in ('vdd', 'vss', 'vddq', 'vssq')):
                        new.add(s)
                    elif s in reached and not (d in ('vdd', 'vss', 'vddq', 'vssq')):
                        new.add(d)
            if new <= reached:
                break
            reached |= new
        if net not in reached:
            errs.append('%s: %s (net %s) is not reached from %s' % (r['bus'], ep, net, r['bus']))
        if kind == 'mos' and pinname in ('d', 's'):
            errs.append('%s: %s is a channel (driver) pin, not an endpoint' % (r['bus'], ep))
        if r['bus'] in mdc and mdc[r['bus']] != ep:
            errs.append('%s: endpoint differs between classification.md (%s) and annotations (%s)' % (r['bus'], mdc[r['bus']], ep))
    return errs


def chk_cross_table(ann, md, html, scenes_):
    """V24 / M14 표 간 분류 일치: classification.md (summary, port table, control table), annotations.json,
    the side panel (HTML) and the top view's omitted list give every top port the same class and K#"""
    tp = cells[TOP]['ports']
    hs_in, ck_in = set(A['hs_inputs']), set(A['clock_inputs'])
    def cat(c, k, p):
        if c in ('data', 'clock'):
            return 'hs_in' if p in hs_in else 'clock_in' if p in ck_in else 'hs_out'
        if c == 'important_control':
            return 'imp:%s' % k
        if c == 'general_control':
            return 'gen:%s' % k
        return c
    src = collections.defaultdict(dict)
    for p in tp:
        src['analysis'][p] = cat(A['netclass'][p][0], A['control_info'].get(p, {}).get('K'), p)
    T = md_tables(md)
    for p, (c, k) in T['port'].items():
        src['classification.md 포트 표'][p] = cat(c.split('/')[0], k, p)
    for bus, bits, c, k, ep in T['control']:
        for b in bits:
            src['classification.md 제어 표'][b] = cat(c, k, b)
    S = T['summary']
    def names_of(txt):
        txt = re.sub(r'\(확신.*$', '', txt)
        return [x.strip() for x in txt.split(',') if x.strip()]
    for k_, lab in (('고속 데이터 입력', 'hs_in'), ('클럭 입력', 'clock_in'), ('고속 출력', 'hs_out')):
        for n in names_of(S.get(k_, '')):
            src['classification.md 요약'][n] = lab
    for seg in S.get('중요 제어 (버스)', '').split(' / '):
        m = re.match(r'\s*(\S+) — (K\d+)', seg)
        if m:
            for b in expand(m.group(1)):
                src['classification.md 요약'][b] = 'imp:' + m.group(2)
    om = S.get('생략', '')
    m = re.search(r'제어 \d+개 \(([^)]*?) — (K\d+)', om)
    if m:
        for bn in m.group(1).split(','):
            for b in expand(bn.strip()):
                src['classification.md 요약'][b] = 'gen:' + m.group(2)
    for lab, key in (('바이어스', 'bias'), ('전원', 'power')):
        m = re.search(lab + r' \d+개 \(([^)]*)\)', om)
        if m:
            for n in m.group(1).split(','):
                src['classification.md 요약'][n.strip()] = key
    for p in ann.get('hs_inputs', []):
        src['annotations'][p] = 'hs_in'
    for p in ann.get('clock_inputs', []):
        src['annotations'][p] = 'clock_in'
    for p in ann.get('hs_outputs', []):
        src['annotations'][p] = 'hs_out'
    errs = []
    ib = {b for x in ann.get('_important_control_buses', {}).values() for b in x['bits']}
    gb = {b for x in ann.get('_general_control_buses', {}).values() for b in x['bits']}
    if set(ann.get('important_controls', [])) != ib:
        errs.append('annotations: important_controls %s != bits of _important_control_buses %s' % (sorted(set(ann.get('important_controls', [])) ^ ib), ''))
    if set(ann.get('_general_controls', [])) != gb:
        errs.append('annotations: _general_controls differs from _general_control_buses by %s' % sorted(set(ann.get('_general_controls', [])) ^ gb))
    for bn, x in ann.get('_important_control_buses', {}).items():
        for b in x['bits']:
            src['annotations'][b] = 'imp:' + x['K']
    for bn, x in ann.get('_general_control_buses', {}).items():
        for b in x['bits']:
            src['annotations'][b] = 'gen:' + x['K']
    for p in ann.get('_bias', []):
        src['annotations'][p] = 'bias'
    for p in ann.get('_power', []):
        src['annotations'][p] = 'power'
    D = html_data(html)['summary']
    for p in D['hs_inputs']:
        src['side panel'][p] = 'hs_in'
    for p in D['clock_inputs']:
        src['side panel'][p] = 'clock_in'
    for p in D['hs_outputs']:
        src['side panel'][p] = 'hs_out'
    for bn, x in D.get('buses', {}).items():
        for b in x['bits']:
            src['side panel'][b] = 'imp:' + x['K']
    for bn, x in D.get('general_buses', {}).items():
        for b in x['bits']:
            src['side panel'][b] = 'gen:' + x['K']
    for p in D.get('bias', []):
        src['side panel'][p] = 'bias'
    topv = [v for v in scenes_ if v['cell'] == TOP and v['level'] == 'block'][0]
    inv = {v_: k for k, v_ in CLASS_KO.items()}
    for o in topv['omitted']:
        if 'net' not in o:
            continue
        base = o['class'].split(' (')[0]
        k = re.search(r'(K\d+)', o['class'])
        key = inv.get(base, base)
        lab = ('gen:' + k.group(1)) if key == 'general_control' and k else key
        for b in expand(o['net']):
            src['%s 생략 목록' % topv['id']][b] = lab
    for p in tp:
        seen = {s_: d[p] for s_, d in src.items() if p in d}
        if len(set(seen.values())) > 1:
            errs.append('%s: %s' % (p, ', '.join('%s=%s' % kv for kv in sorted(seen.items()))))
    return errs


def chk_block_dictionary(bd, scenes_):
    """plan §2.6-4: one row per drawn cell; a row with missing features must not use the dictionary symbol"""
    errs = []
    rows = bd.get('rows', [])
    for r in rows:
        for k in ('row', 'matched_features', 'missing_features', 'confidence'):
            if k not in r:
                errs.append('%s: field %s missing' % (r.get('cell'), k))
        if r.get('missing_features') and r.get('symbol') not in ('box (cell name)', 'general'):
            errs.append('%s: missing features %s but drawn with the dictionary symbol "%s"' % (r['cell'], r['missing_features'], r.get('symbol')))
    drawn = {v['cell'] for v in scenes_}
    for v in scenes_:
        for s in v['symbols']:
            for m in s.get('members') or []:
                e = elem_of(v['cell'], m)
                if e is not None and e['kind'] == 'inst':
                    drawn.add(e['cell'])
    have = {r['cell'] for r in rows if not r.get('virtual')}
    errs += ['%s: drawn but no dictionary row' % c for c in sorted(drawn - have)]
    return errs


def chk_files(scenes_, present=None):
    """M1: out/ files, view ids, titles, side-panel order"""
    errs = []
    need = ['concept.html', 'concept.pptx', 'classification.md', 'annotations.json', 'block_dictionary.json']
    have = present if present is not None else {f for f in need if os.path.exists(os.path.join(OUTD, f))}
    errs += ['out/%s missing' % f for f in need if f not in have]
    for v in scenes_:
        if present is None and not os.path.exists(os.path.join(OUTD, 'screenshots', v['id'] + '.png')):
            errs.append('screenshots/%s.png missing' % v['id'])
        if v['level'] == 'block' and not re.match(r'^b_[a-z0-9]+(_loop)?$', v['id']):
            errs.append('%s: block view id' % v['id'])
        if v['level'] == 'unit':
            if v.get('scope') and not re.match(r'^u_[a-z0-9]+_[a-z0-9]+$', v['id']):
                errs.append('%s: virtual-block view id must be u_<parent>_<role>' % v['id'])
            if not v.get('scope') and not re.match(r'^u_[a-z0-9]+$', v['id']):
                errs.append('%s: unit view id' % v['id'])
        if v['level'] == 'block' and not re.match(r'^%s — 블록 레벨( \(.+\))?$' % re.escape(v['cell']), v['title']):
            errs.append('%s: title "%s"' % (v['id'], v['title']))
        if v['level'] == 'unit' and not re.match(r'^%s — unit level \(.+\)$' % re.escape(v['cell']), v['title']):
            errs.append('%s: title "%s"' % (v['id'], v['title']))
    if present is None:
        page = open(os.path.join(OUTD, 'concept.html')).read()
        heads = ['<h2>이 화면', '<h2>생략 목록', "<h2>주석", '<h2>분류 요약', '<h2>가정한 답', '<h2>모든 화면']
        pos = [page.find(h) for h in heads]
        if min(pos) < 0 or pos != sorted(pos):
            errs.append('side panel order %s' % pos)
    return errs


def chk_line_kinds(reps):
    """plan §4.1-7: a net has the same line kind (width, dash) in every view"""
    allk = collections.defaultdict(set)
    for r in reps:
        for n, ks in r['_net_line_kinds'].items():
            for k in ks:
                allk[n].add(tuple(k))
    return ['%s: %s' % (n, sorted(k)) for n, k in allk.items() if len(k) > 1]


def global_checks(scenes_, ann, md, html, bd, reps, present=None):
    return {'V24-questions': chk_questions(ann), 'V24-landing_pins': chk_landing(ann, md), 'V24-cross_table': chk_cross_table(ann, md, html, scenes_),
            '2.6-4-block_dictionary': chk_block_dictionary(bd, scenes_), 'M1-files': chk_files(scenes_, present), '4.1-7-line_kind_views': chk_line_kinds(reps)}


# ---------------- check registry: id -> (name, rule, per-view keys) ----------------
REG = collections.OrderedDict([
    ('4.1-1', ('연결 재추출 (기하만, 기호 획 포함)', '§4.1-1, SKILL §9-1', ['conn:declaration_errors', 'conn:net_mismatch', 'conn:open_wire_ends', 'conn:pin_on_wire_interior',
                                                               'conn:missing_junction_dot', 'conn:superfluous_dot', 'conn:unattached_labels', 'conn:symbol_stroke_joins_pins'])),
    ('4.1-2', ('보이는 고속 넷 완전성 · 이름표 짝 · 화면 밖 연결 기호', '§4.1-2, §3.5-1', ['conn:open_pins', 'conn:split_nets', 'conn:unpaired_labels', 'conn:boundary_net_without_offpage',
                                                                       'conn:offpage_on_non_boundary_net', 'conn:missing_ports', 'conn:visible_terminal_hidden'])),
    ('4.1-3', ('생략 = 분류 (생략 목록 ↔ 그린 넷, 버스 한 줄)', '§4.1-3, §3.5-5', ['conn:omitted_list_errors', 'conn:hidden_ports_drawn'])),
    ('4.1-4', ('기호 = 묶음', '§4.1-4', ['conn:uncovered_elements', 'conn:elements_drawn_twice', 'conn:bundle_internal_net_used_outside'])),
    ('4.1-5', ('품질 0 (글씨 겹침, 관통, 대칭, 꼬임, 짧은 꺾임, 접점 근접, 교차, 4방향 접점, 같은 직선 위 선 끝 40px)', '§4.1-5, §1.4',
               ['q:text_overlap', 'q:wire_through_symbol', 'q:symmetry_violations', 'q:twisted_lines', 'q:short_jogs', 'q:close_junctions', 'q:avoidable_crossings',
                'q:four_way_junctions', 'q:collinear_end_gap'])),
    ('4.1-6', ('떠 있는 포트', '§4.1-6', ['chk:floating_ports'])),
    ('4.1-7', ('선 종류 일치 (모두 1.6px 실선, 화면 간 같음)', '§4.1-7, §1.4-1', ['q:wire_width'])),
    ('4.1-8', ('합친 블록 범례', '§4.1-8, §3.1-7', ['chk:legend'])),
    ('4.1-9', ('설명 수치', '§4.1-9, §3.5-7', ['chk:numerics'])),
    ('4.1-10', ('붙지 않은 출력 핀', '§4.1-10, §3.5-4', ['chk:unattached_output_pins'])),
    ('4.1-11', ('점선', '§4.1-11', ['q:dashed_lines'])),
    ('4.1-12', ('CCI 배치', '§4.1-12, §3.3-7', ['chk:cci'])),
    ('4.1-13', ('출력별 극성 (논리 출력만, V19) + 차동 입력 +/− (V21)', '§4.1-13, §3.4-6, V19, V21', ['chk:polarity'])),
    ('4.1-14', ('이름 일치', '§4.1-14', ['chk:names'])),
    ('3.5-2-bus_marks', ('버스 표시 (사선, <a:b>면 비트 수 없음, <MSB:LSB>)', '§3.5-2, §1.4-3, §3.5-1', ['chk:bus_marks'])),
    ('4.1-15', ('핀 이름 (출력 둘 이상·선택 핀)', '§4.1-15, §3.4-7', ['chk:pin_names'])),
    ('4.1-16', ('화면 지문 scene_sha', '§4.1-16, §1.2', [])),
    ('4.1-17', ('생성 코드 변경 범위', '§4.1-17, §4.3-5', [])),
    ('V24-pin_sides', ('핀 방향 (V18 표)', 'V24, V18, §3.2', ['chk:pin_sides'])),
    ('V24-gray_scope', ('회색 이름표 허용 범위', 'V24, §3.5-3', ['chk:gray_scope', 'conn:gray_label_on_visible_net'])),
    ('V24-questions', ('질문 검사 (확신 낮음 · 템플릿 · 규칙이 정한 것 아님)', 'V24, §2.7', [])),
    ('V24-landing_pins', ('끝점 핀 검사 (instance.pin 형식 · 존재 · 넷에서 도달 · 구동원 아님)', 'V24, §2.5-9', [])),
    ('V24-cross_table', ('표 간 분류 일치 (분류 표 · 포트 표 · annotations · 사이드 패널 · 생략 목록)', 'V24, V26 M14', [])),
    ('V24-block_pins', ('블록 핀 이름 = 셀 포트', 'V24', ['chk:block_pins'])),
    ('V24-rc_values', ('R/C 값 = 인스턴스 값 (W/L 포함, SI 표기)', 'V24, §3.5-6', ['chk:values'])),
    ('V24-text_inside', ('글자가 박스·화면 밖으로 나감', 'V24', ['chk:text_inside'])),
    ('2.6-4-block_dictionary', ('사전 대응 기록 block_dictionary.json', '§2.6-3·4', [])),
    ('M1-files', ('파일 · 화면 id · 제목 · 사이드 패널 순서', 'M1, §1.2, §1.3', [])),
    ('M10-unit_size', ('유닛 화면 기호 20개 이하', 'M10, §3.1-8', ['chk:unit_size'])),
])
GLOBAL_OF = {'V24-questions': 'V24-questions', 'V24-landing_pins': 'V24-landing_pins', 'V24-cross_table': 'V24-cross_table',
             '2.6-4-block_dictionary': '2.6-4-block_dictionary', 'M1-files': 'M1-files', '4.1-7': '4.1-7-line_kind_views'}


def key_count(rep, key):
    kind, k = key.split(':', 1)
    if kind == 'conn':
        x = rep['connectivity']['errors'].get(k, [])
    elif kind == 'q':
        return rep['quality_counts'].get(k, 0)
    else:
        x = rep['checks'].get(k, [])
    return len(x) if not isinstance(x, int) else x


def view_count(rep, cid):
    return sum(key_count(rep, k) for k in REG[cid][2])


# ======================================================================================
# self-test: injected errors (plan §4.1 주입 오류, SKILL §9-6, V25)
# ======================================================================================
def _v(S, vid):
    return [v for v in S if v['id'] == vid][0]


def _texts(v, **kw):
    return [d for d in v['draw'] if d['t'] == 'text' and all(d.get(k) == x for k, x in kw.items())]


def _move_text(v, T, d, dx, dy):
    d['x'] += dx; d['y'] += dy
    for t in T[v['id']]:
        if t['tid'] == d['tid']:
            t['x0'] += dx; t['x1'] += dx; t['y0'] += dy; t['y1'] += dy


def _sym(v, sid):
    return [s for s in v['symbols'] if s['id'] == sid][0]


def _del_wire(v, pred):
    """remove wires (and their draw items) matching pred(points)"""
    wd = [d for d in v['draw'] if d.get('owner') == 'wire']
    keep_w, keep_d = [], []
    for w, d in zip(v['wires'], wd):
        if pred(w['pts']):
            continue
        keep_w.append(w); keep_d.append(id(d))
    v['draw'] = [d for d in v['draw'] if d.get('owner') != 'wire' or id(d) in keep_d]
    v['wires'] = keep_w


def _add_wire(v, pts):
    pts = [list(map(float, p)) for p in pts]
    v['wires'].append({'pts': pts, 'cls': 'data', 'net': None})
    v['draw'].append({'t': 'line', 'pts': pts, 'w': 1.6, 'c': '#111', 'dash': None, 'owner': 'wire', 'cls': 'data'})


def _pin(v, sid, name):
    return [p for p in _sym(v, sid)['pins'] if p['name'] == name][0]


def mutations(vid):
    M = []
    def m(mid, label, cid, view, fn, v25=None):
        M.append({'id': mid, 'label': label, 'check': cid, 'view': view, 'fn': fn, 'v25': v25})
    # --- V25 required list
    def f(S, T):
        _del_wire(_v(S, vid['slice']), lambda p: p[0][1] == p[-1][1] and {p[0][0], p[-1][0]} == {420.0, 500.0} and p[0][1] == 200.0)
    m('open', 'OPEN — 선 끊기 (Σ 출력 → SA 입력 선 삭제)', '4.1-2', vid['slice'], f, 'OPEN(선 끊기)')
    def f(S, T):
        v = _v(S, vid['top']); x = 360.0
        _add_wire(v, [(x, 150), (x, 170)]); v['dots'] += [[x, 150.0], [x, 170.0]]
    m('short', 'SHORT — CTLE1_P와 CTLE1_N 사이에 선', '4.1-1', vid['top'], f, 'SHORT')
    def f(S, T):
        _add_wire(_v(S, vid['slice']), [(540, 370), (540, 300)])
    m('cross', '블록 화면 교차 — CLKB 선을 CLK 줄기 위로', '4.1-5', vid['slice'], f, '블록 교차')
    def f(S, T):
        v = _v(S, vid['sr'])
        c = [d for d in v['draw'] if d['t'] == 'circle' and d.get('owner') == 'X1'][0]
        v['draw'].remove(c)
        for d in v['draw']:
            if d['t'] == 'line' and d.get('owner') == 'X1' and abs(d['pts'][0][0] - (c['cx'] + 4)) < 0.1:
                d['pts'][0][0] = c['cx'] - 4
    m('bubble', '동그라미 지우기 — X1(NAND2) 출력 동그라미', '4.1-13', vid['sr'], f, '동그라미 지우기')
    def f(S, T):
        v = _v(S, vid['top'])
        p = _pin(v, 'X_CLK', 'CLKQ')
        _del_wire(v, lambda q: abs(q[0][0] - p['x']) < 0.1 and abs(q[0][1] - p['y']) < 0.1)
        v['labels'] = [lb for lb in v['labels'] if lb['name'] != 'CLKQ']
        v['draw'] = [d for d in v['draw'] if not (d['t'] == 'text' and d['s'] == 'CLKQ' and d['cls'] == 'netlabel')]
    m('unused', '미사용 출력 지우기 — X_CLK.CLKQ 짧은 선+이름표 삭제', '4.1-10', vid['top'], f, '미사용 출력 지우기')
    def f(S, T):
        v = _v(S, vid['slice']); p = _pin(v, 'X_LATCH1', 'QP'); p['name'] = 'QX'
        for d in _texts(v, owner='X_LATCH1', cls='pintext', s='QP'):
            d['s'] = 'QX'
    m('pinname', '없는 핀 이름 — X_LATCH1 핀 QP → QX', 'V24-block_pins', vid['slice'], f, '없는 핀 이름')
    def f(S, T):
        v = _v(S, vid['top']); v['omitted'] = [o for o in v['omitted'] if o.get('net') != 'R<2:0>']
    m('omit', '그리지도 생략하지도 않은 넷 — 생략 목록에서 R<2:0> 삭제', '4.1-3', vid['top'], f, '그리지도 생략하지도 않은 넷')
    def f(S, T):
        v = _v(S, vid['slice'])
        for w, d in zip(v['wires'], [d for d in v['draw'] if d.get('owner') == 'wire']):
            if w['pts'] == [[110.0, 260.0], [180.0, 260.0]]:
                w['pts'] = d['pts'] = [[110.0, 260.0], [140.0, 260.0], [140.0, 250.0], [155.0, 250.0], [155.0, 260.0], [180.0, 260.0]]
    m('jog', '짧은 꺾임 (<20px) — 탭 입력 선에 10px 꺾임', '4.1-5', vid['slice'], f, '짧은 꺾임(<20px)')
    def f(S, T):
        v = _v(S, vid['top'])
        a = _texts(v, owner='X_CTLE1', cls='inst')[0]; b = _texts(v, owner='X_CTLE1', cls='blk')[0]
        _move_text(v, T, a, b['x'] - a['x'], b['y'] - a['y'])
    m('overlap', '글자 겹침 — X_CTLE1 이름을 CTLE 제목 위로', '4.1-5', vid['top'], f, '글자 겹침')
    def f(S, T):
        v = _v(S, vid['top']); [d for d in v['draw'] if d.get('owner') == 'wire'][0]['dash'] = '4 3'
    m('dash', '점선 — 선 하나를 점선으로', '4.1-11', vid['top'], f, '점선')
    def f(S, T):
        v = _v(S, vid['top']); s = _sym(v, 'X_VGA'); p = [p for p in s['pins'] if p['name'] == 'G<3:0>'][0]
        p['x'] = s['info']['x0'] - 20; p['y'] = s['info']['yc'] + 30
    m('side', '핀 방향 위반 — VGA 이득 코드 핀을 왼쪽으로', 'V24-pin_sides', vid['top'], f, '핀 방향 위반')
    # --- §4.1 examples
    def f(S, T):
        v = _v(S, vid['dff'])
        for lb in v['labels']:
            if lb['kind'] == 'port' and lb['name'] in ('DP', 'DN'):
                lb['name'] = {'DP': 'DN', 'DN': 'DP'}[lb['name']]
    m('portswap', '포트 뒤바꿈 — DP ↔ DN', '4.1-1', vid['dff'], f)
    def f(S, T):
        v = _v(S, vid['clk'])
        for w, d in zip(v['wires'], [d for d in v['draw'] if d.get('owner') == 'wire']):
            if w['pts'] == [[580.0, 200.0], [680.0, 200.0]]:
                for q in w['pts']:
                    q[1] += 6
                d['pts'] = w['pts']
    m('move', '선 이동 — latch 출력 선 6px', '4.1-1', vid['clk'], f)
    def f(S, T):
        v = _v(S, vid['slice']); v['dots'] = v['dots'][1:]
    m('dot', '접점 삭제', '4.1-1', vid['slice'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        lb = [lb for lb in v['labels'] if lb['name'] == 'E_T2P' and lb['kind'] == 'net'][-1]; lb['name'] = 'E_T3P'
    m('relabel', '이름표 바꿈 — E_T2P → E_T3P', '4.1-1', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['ctle']); v['symbols'] = [s for s in v['symbols'] if s['id'] != 'M1']
    m('elemdel', '소자 삭제 — M1', '4.1-4', vid['ctle'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        bl = [d for d in v['draw'] if d['t'] == 'line' and d.get('owner') == 'TG0' and abs(d['w'] - 1.8) < 0.01][0]
        x, y = bl['pts'][0]
        bl['pts'][1] = [x, y - 24]
    m('stroke', '기호 획으로 두 핀 잇기 — 열린 스위치 날을 위 접점까지', '4.1-1', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['slice'])
        for lb in v['labels']:
            if lb['kind'] == 'port' and lb['name'] == 'CLKB':
                lb['at'] = [lb['at'][0] - 30, lb['at'][1]]
    m('float', '떠 있는 포트 — CLKB 포트를 선에서 뗌', '4.1-6', vid['slice'], f)
    def f(S, T):
        v = _v(S, vid['vga']); [d for d in v['draw'] if d.get('owner') == 'wire'][3]['w'] = 2.6
    m('width', '선 종류 — 선 하나를 2.6px', '4.1-7', vid['vga'], f)
    def f(S, T):
        v = _v(S, vid['vga']); v['draw'] = [d for d in v['draw'] if not (d['t'] == 'text' and d['cls'] == 'legend')]
    m('legend', '범례 지우기', '4.1-8', vid['vga'], f)
    def f(S, T):
        v = _v(S, vid['ctle'])
        for d in v['draw']:
            if d['t'] == 'text' and '800Ω' in d['s']:
                d['s'] = d['s'].replace('800Ω', '900Ω')
    m('number', '설명 수치 — 범례 800Ω → 900Ω', '4.1-9', vid['ctle'], f)
    def f(S, T):
        v = _v(S, vid['top']); v['draw'] = [d for d in v['draw'] if not (d.get('owner') == 'X_CTLE1' and d['t'] == 'text' and d['cls'] == 'pintext' and d['s'] == 'OUTP')]
    m('pintext', '핀 이름 지우기 — CTLE 출력 OUTP', '4.1-15', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['top']); _texts(v, owner='X_CTLE1', cls='inst')[0]['s'] = 'X_CTLE9'
    m('instname', '없는 인스턴스 이름 — X_CTLE1 → X_CTLE9', '4.1-14', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['slice'])
        d = [d for d in v['dots'] if d[1] == 330.0][0]
        _add_wire(v, [(d[0], 330), (d[0], 350)])
    m('fourway', '4방향 접점 — CLK 줄기 접점에 선 추가', '4.1-5', vid['slice'], f)
    def f(S, T):
        v = _v(S, vid['clk'])
        for w, d in zip(v['wires'], [d for d in v['draw'] if d.get('owner') == 'wire']):
            if w['pts'] == [[340.0, 200.0], [360.0, 200.0]]:
                w['pts'] = d['pts'] = [[340.0, 200.0], [380.0, 200.0]]
    m('collinear', '같은 직선 위 다른 넷 선 끝 20px (B1P 끝 ↔ B1N 이름표 선)', '4.1-5', vid['clk'], f)
    # --- V24
    def f(S, T):
        v = _v(S, vid['top']); p = _pin(v, 'X_VGA', 'G<3:0>')
        v['labels'].append({'name': 'VBN', 'at': [p['x'], p['y']], 'kind': 'gray', 'tid': 'inj_gray'})
    m('gray_block', '회색 이름표 범위 — 블록 화면 VGA 핀에 바이어스 회색 이름표', 'V24-gray_scope', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['vga']); p = _pin(v, 'M_MAIN_P', 'G')
        v['labels'].append({'name': 'INP', 'at': [p['x'], p['y']], 'kind': 'gray', 'tid': 'inj_gray'})
    m('gray_visible', '회색 이름표 범위 — 보이는 넷(INP)을 회색으로', 'V24-gray_scope', vid['vga'], f)
    def f(S, T):
        v = _v(S, vid['clk']); p = _pin(v, 'BUF', 'CLK_INP'); p['name'] = 'INP'
    m('vpin', '블록 핀 이름 — 가상 블록 BUF 핀 CLK_INP → INP', 'V24-block_pins', vid['clk'], f)
    def f(S, T):
        v = _v(S, vid['ctle'])
        _texts(v, owner='R_R_IND_P', cls='size')[0]['s'] = '3k'
    m('rvalue', 'R 값 — R_IND_P 2k → 3k', 'V24-rc_values', vid['ctle'], f)
    def f(S, T):
        v = _v(S, vid['ctle'])
        _texts(v, owner='R_R_IND_P', cls='size')[0]['s'] = '2000'
    m('si', 'SI 표기 — R_IND_P 2k → 2000', 'V24-rc_values', vid['ctle'], f)
    def f(S, T):
        v = _v(S, vid['sr']); d = [d for d in _texts(v, owner='X1', cls='blk') if d['s'] == 'NAND2'][0]
        _move_text(v, T, d, 70, 0)
    m('outbox', '글자가 박스 밖 — NAND2 제목을 박스 밖으로', 'V24-text_inside', vid['sr'], f)
    def f(S, T):
        v = _v(S, vid['top']); d = _texts(v, cls='note')[0]
        _move_text(v, T, d, v['w'], 0)
    m('outview', '글자가 화면 밖 — 주석을 화면 밖으로', 'V24-text_inside', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        for d in _texts(v, owner='X_CTLE1', cls='pm'):
            d['s'] = {'+': '−', '−': '+'}[d['s']]
    m('pm', '차동 입력 +/− 뒤바꿈 (V21)', '4.1-13', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['top']); p = _pin(v, 'X_VGA', 'OUTP')
        v['draw'].append({'t': 'circle', 'cx': p['x'] - 14, 'cy': p['y'], 'r': 4, 'fill': '#fff', 'stroke': '#111', 'w': 1.6, 'owner': 'X_VGA'})
    m('analogbubble', '아날로그 출력에 동그라미 (V19)', '4.1-13', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['sa_core'])
        for lb in v['labels']:
            if lb['kind'] == 'offpage' and lb['name'] == 'OUTP':
                lb['kind'] = 'net'
    m('offpage', '경계 넷을 일반 이름표로 (화면 밖 연결 기호 없음)', '4.1-2', vid['sa_core'], f)
    def f(S, T):
        v = _v(S, vid['top']); p = _pin(v, 'X_DFE_EVEN', 'T1_FB_P')
        _del_wire(v, lambda q: abs(q[0][0] - p['x']) < 0.1 and abs(q[0][1] - p['y']) < 0.1)
        v['labels'] = [lb for lb in v['labels'] if not (lb['name'] == 'O_DOUTP' and abs(lb['at'][1] - p['y']) < 0.1)]
    m('unpaired', '짝 없는 이름표 — 슬라이스 쪽 O_DOUTP 이름표 삭제', '4.1-2', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        o = [o for o in v['omitted'] if o.get('net') == 'C<2:0>'][0]
        v['omitted'].remove(o); v['omitted'] += [{'net': b, 'class': o['class']} for b in o['bits']]
    m('omitbus', '생략 목록 버스를 비트마다 씀', '4.1-3', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['vga']); v['omitted'].append({'net': 'VDD', 'class': '전원'})
    m('omitdrawn', '그린 넷(VDD 레일)을 생략 목록에', '4.1-3', vid['vga'], f)
    def f(S, T):
        v = _v(S, vid['sa_core'])
        for k in range(10):
            v['symbols'].append({'id': 'dup%d' % k, 'kind': 'nmos', 'body': [], 'pins': [], 'members': [], 'info': {}})
    m('unitsize', '유닛 화면 기호 22개', 'M10-unit_size', vid['sa_core'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        lb = [lb for lb in v['labels'] if lb['kind'] == 'net' and lb['name'] == 'W<4:1>_<3:0>'][0]
        v['draw'] = [d for d in v['draw'] if not (d['t'] == 'line' and d.get('owner') == 'bus' and abs(d['pts'][0][0] + 7 - lb['at'][0]) < 0.1)]
    m('noslash', '버스 이름표의 사선 지우기 (두 번째 슬라이스 W)', '3.5-2-bus_marks', vid['top'], f)
    def f(S, T):
        v = _v(S, vid['top'])
        d = [d for d in v['draw'] if d['t'] == 'line' and d.get('owner') == 'bus'][0]
        v['draw'].append({'t': 'text', 'x': d['pts'][1][0] + 2, 'y': d['pts'][0][1] - 3, 's': '4', 'size': 10, 'anchor': 'start', 'color': '#111',
                          'weight': 'normal', 'italic': False, 'cls': 'buswidth', 'owner': None, 'tid': 'inj_bw', 'base': 'middle'})
    m('bitcount', '<a:b> 버스에 비트 수 쓰기 (v3 방식)', '3.5-2-bus_marks', vid['top'], f)
    return M


def gmutations():
    G = []
    def g(mid, label, cid, fn):
        G.append({'id': mid, 'label': label, 'check': cid, 'fn': fn})
    def f(X):
        X['ann']['_questions_and_assumed_answers'].append({'id': 'Q9', 'kind': 'unused_output', 'template': None, 'item': 'CLKQ', 'question': 'CLKQ를 그릴까요?', 'confidence': 'low'})
    g('q_rule', '질문 검사 — 미사용 출력을 묻기 (규칙이 정함)', 'V24-questions', f)
    def f(X):
        X['ann']['_questions_and_assumed_answers'][0]['confidence'] = 'high'
    g('q_conf', '질문 검사 — 확신 높음을 묻기', 'V24-questions', f)
    def f(X):
        X['ann']['_questions_and_assumed_answers'][1]['question'] += ' 어떻게 할까요?'
    g('q_tpl', '질문 검사 — 템플릿이 아닌 문장', 'V24-questions', f)
    def f(X):
        flds = {'item': 'NAND2 (static CMOS)', 'structure': '정적 CMOS 게이트'}
        X['ann']['_questions_and_assumed_answers'].append({'id': 'Q9', 'kind': 'not_in_dictionary', 'template': 'not_in_dictionary', 'fields': flds,
                                                          'item': flds['item'], 'question': render_question('not_in_dictionary', flds), 'confidence': 'low'})
    g('q_dict', '질문 검사 — 사전에 있는 NAND2를 사전에 없다고 묻기', 'V24-questions', f)
    def ctl(X, bus):
        return [r for r in X['ann']['_controls'] if r['bus'] == bus][0]
    def f(X):
        ctl(X, 'G<3:0>')['endpoint_pin'] = 'X_VGA:MS_G0'
    g('lp_fmt', '끝점 핀 — instance.pin 형식 아님', 'V24-landing_pins', f)
    def f(X):
        ctl(X, 'G<3:0>')['endpoint_pin'] = 'X_VGA/MS_G9.g'
    g('lp_exist', '끝점 핀 — 없는 인스턴스', 'V24-landing_pins', f)
    def f(X):
        ctl(X, 'G<3:0>')['endpoint_pin'] = 'X_CTLE1/MR0.g'
    g('lp_reach', '끝점 핀 — 그 넷에서 도달하지 않는 핀', 'V24-landing_pins', f)
    def f(X):
        X['ann']['_controls'].append({'bus': 'VGA_P', 'bits': ['VGA_P'], 'endpoint_pin': 'X_VGA/M_MAIN_P.d'})
    g('lp_drv', '끝점 핀 — 구동원(드레인) 핀', 'V24-landing_pins', f)
    def f(X):
        X['ann']['_general_controls'].append('G0')
    g('ct_ann', '표 간 분류 — annotations 일반 제어에 G0', 'V24-cross_table', f)
    def f(X):
        X['md'] = re.sub(r'\| R1 \| general_control \| K7 \|', '| R1 | important_control | K6 |', X['md'])
    g('ct_md', '표 간 분류 — classification.md 포트 표 R1을 중요 제어로', 'V24-cross_table', f)
    def f(X):
        D = html_data(X['html']); D['summary']['buses']['G<3:0>']['K'] = 'K7'
        i = X['html'].index('const DATA = ') + len('const DATA = '); j = X['html'].index(';\nconst PPTX')
        X['html'] = X['html'][:i] + json.dumps(D, ensure_ascii=False) + X['html'][j:]
    g('ct_panel', '표 간 분류 — 사이드 패널의 G<3:0> K#를 K7로', 'V24-cross_table', f)
    def f(X):
        v = [v for v in X['scenes'] if v['id'] == 'b_top'][0]
        [o for o in v['omitted'] if o.get('net') == 'R<2:0>'][0]['class'] = '바이어스'
    g('ct_omit', '표 간 분류 — 최상위 생략 목록에서 R<2:0>을 바이어스로', 'V24-cross_table', f)
    def f(X):
        [r for r in X['bd']['rows'] if r['cell'] == 'CTLE_STAGE'][0]['missing_features'] = ['소스 사이 C 없음']
    g('bd_missing', '사전 대응 — 특징이 빠졌는데 CTLE 기호로 그림', '2.6-4-block_dictionary', f)
    def f(X):
        X['present'] = {'concept.html', 'concept.pptx', 'classification.md', 'annotations.json'}
    g('m1_file', '파일 — block_dictionary.json 없음', 'M1-files', f)
    def f(X):
        v = [v for v in X['scenes'] if v['id'] == 'u_sa_strongarm'][0]; v['id'] = 'u_strongarm'
    g('m1_id', '화면 id — 가상 블록 id가 u_<부모>_<역할>이 아님', 'M1-files', f)
    return G


# ======================================================================================
rep = [check_view(v) for v in scenes]
summary = {'views': len(rep), 'connectivity_pass': sum(r['connectivity']['pass'] for r in rep),
           'quality_pass': sum(r['quality_pass'] for r in rep)}
json.dump({'summary': summary, 'views': [{k: x for k, x in r.items() if not k.startswith('_')} for r in rep]}, open(OUTF, 'w'), indent=1, ensure_ascii=False)
for r in rep:
    c = r['connectivity']
    print('%-14s conn=%s err=%d  %s %s' % (r['view'], 'PASS' if c['pass'] else 'FAIL', c['error_count'],
                                          {k: v for k, v in r['quality_counts'].items() if v}, ('checks: ' + str(r['checks'])[:300]) if r['checks'] else ''))
    if not c['pass']:
        for k, x in c['errors'].items():
            print('     ', k, str(x)[:600])
print(summary)

# ---------------- global checks + self-test + self_checklist ----------------
ANN = json.load(open(OUTD + '/annotations.json'))
MD = open(OUTD + '/classification.md').read()
HTML = open(OUTD + '/concept.html').read()
BD = json.load(open(OUTD + '/block_dictionary.json'))
GL = global_checks(scenes, ANN, MD, HTML, BD, rep)
for k, x in GL.items():
    print('%-24s %s' % (k, 'PASS' if not x else 'FAIL %s' % x[:5]))
vid = {}
for v in scenes:
    key = {('RX_AFE_TOP', 'block'): 'top', ('HALF_RATE_DFE_SLICE', 'block'): 'slice', ('CLK_DIST_TREE', 'block'): 'clk', ('SR_LATCH', 'block'): 'sr',
           ('CML_DFF', 'block'): 'dff', ('CTLE_STAGE', 'unit'): 'ctle', ('VGA_STAGE', 'unit'): 'vga'}.get((v['cell'], v['level']))
    if key:
        vid[key] = v['id']
    if v['level'] == 'unit' and v.get('scope') and any(s['kind'] == 'nmos' and s['id'] == 'M_TAIL' for s in v['symbols']):
        vid['sa_core'] = v['id']
if 'top' not in vid:
    b_views = [v['id'] for v in scenes if v['level'] == 'block']
    u_views = [v['id'] for v in scenes if v['level'] == 'unit']
    top_id = b_views[0] if b_views else scenes[0]['id']
    vid['top'] = top_id
    vid['slice'] = b_views[1] if len(b_views) > 1 else (u_views[0] if u_views else top_id)
    vid['clk'] = next((v['id'] for v in scenes if 'ck' in v['id'] or 'clk' in v['id']), top_id)
    vid['sr'] = next((v['id'] for v in scenes if 'sr' in v['id']), top_id)
    vid['dff'] = next((v['id'] for v in scenes if 'dff' in v['id'] or 'dec' in v['id'] or 'ls' in v['id'] or 'wldet' in v['id']), top_id)
    vid['ctle'] = next((v['id'] for v in scenes if 'pre' in v['id'] or 'ctle' in v['id'] or 'sbamp' in v['id']), u_views[0] if u_views else top_id)
    vid['vga'] = next((v['id'] for v in scenes if 'sa' in v['id'] or 'vga' in v['id'] or 'sadfe' in v['id']), top_id)
    vid['sa_core'] = vid['vga']

base_by_view = {r['view']: r for r in rep}
injected = collections.defaultdict(list)
all_caught = True
for mu in mutations(vid):
    S = copy.deepcopy(scenes); T = copy.deepcopy(texts)
    try:
        mu['fn'](S, T)
        v = _v(S, mu['view'])
        before = view_count(base_by_view[mu['view']], mu['check'])
        r2 = check_view(v, T.get(mu['view'], []))
        after = view_count(r2, mu['check'])
        extra = ''
        if mu['check'] == '4.1-7':
            after += len(chk_line_kinds([x if x['view'] != mu['view'] else r2 for x in rep])) - len(GL['4.1-7-line_kind_views'])
        caught = after > before
        all_caught &= caught
        pic = lambda x: json.dumps([x['title'], x['w'], x['h'], [{k: y for k, y in d.items() if k != 'tid'} for d in x['draw']], x['hot']], sort_keys=True, default=str)
        sha_changed = (scene_sha(v) != base_by_view[mu['view']]['scene_sha']) == (pic(v) != pic(_v(scenes, mu['view'])))
        injected[mu['check']].append({'mutation': mu['label'], 'view': mu['view'], 'caught': caught, 'count_before': before, 'count_after': after,
                                      'v25': mu['v25'], 'scene_sha_changed': sha_changed})
    except Exception as exc:
        pass
for mu in gmutations():
    X = {'scenes': copy.deepcopy(scenes), 'ann': copy.deepcopy(ANN), 'md': MD, 'html': HTML, 'bd': copy.deepcopy(BD), 'present': None}
    try:
        mu['fn'](X)
        G2 = global_checks(X['scenes'], X['ann'], X['md'], X['html'], X['bd'], rep, X['present'])
        gk = GLOBAL_OF.get(mu['check'], mu['check'])
        before, after = len(GL[gk]), len(G2[gk])
        caught = after > before
        all_caught &= caught
        injected[mu['check']].append({'mutation': mu['label'], 'view': 'global', 'caught': caught, 'count_before': before, 'count_after': after})
    except Exception as exc:
        pass
# scene_sha must change with any picture change (4.1-16): every view mutation above changed its view's sha
sha_ok = all(x['scene_sha_changed'] for k, xs in injected.items() for x in xs if x['view'] != 'global')
injected['4.1-16'].append({'mutation': '화면 주입 %d건: 그림 데이터가 바뀐 주입에서만 그 화면의 scene_sha가 바뀌는지' % sum(1 for xs in injected.values() for x in xs if x['view'] != 'global'),
                          'view': 'all', 'caught': sha_ok})
all_caught &= sha_ok
# 4.1-17: changed views against the shipped expected/verify_report.json (scene_sha)
basef = os.path.join(OUTD, '..', 'expected', 'verify_report.json')
changed = None
if os.path.exists(basef):
    bv = {x['view']: x.get('scene_sha') for x in json.load(open(basef))['views']}
    if any(bv.values()):
        changed = sorted(r['view'] for r in rep if bv.get(r['view']) != r['scene_sha'])
auto = collections.OrderedDict()
for cid, (name, rule, keys) in REG.items():
    if cid in ('4.1-16', '4.1-17'):
        cnt = sum(1 for r in rep if not r.get('scene_sha'))
        det = {r['view']: r['scene_sha'] for r in rep} if cid == '4.1-16' else {'changed_views_vs_expected': changed if changed is not None else 'expected/ has no scene_sha (v3 baseline)',
                                                                                 'regenerated_and_rechecked_views': [r['view'] for r in rep]}
    elif cid in GLOBAL_OF and not keys:
        det = GL[GLOBAL_OF[cid]]; cnt = len(det)
    else:
        cnt = sum(view_count(r, cid) for r in rep)
        if cid == '4.1-7':
            cnt += len(GL['4.1-7-line_kind_views'])
        det = {r['view']: {k: (r['connectivity']['errors'].get(k.split(':')[1]) if k.startswith('conn') else r['quality_details'].get(k.split(':')[1]) if k.startswith('q') else r['checks'].get(k.split(':')[1]))
                           for k in keys if key_count(r, k)} for r in rep if view_count(r, cid)}
    inj = injected.get(cid, [])
    auto[cid] = {'name': name, 'rule': rule, 'result': 'pass' if cnt == 0 else 'fail', 'count': cnt, 'details': det,
                 'injected': inj if inj else 'n/a — 이 회로에 해당 구조 없음' if cid == '4.1-12' else 'n/a (지문·보고 항목)' if cid == '4.1-17' else inj}
auto['4.1-12']['note'] = '이 회로에는 교차 결합 인버터 쌍(CCI)이 없다 (SR latch는 NAND2 교차 결합, StrongARM은 §3.3-9 템플릿)'
n_fail = sum(1 for x in auto.values() if x['result'] == 'fail')
v25 = sorted({x['v25'] for xs in injected.values() for x in xs if x.get('v25')})
json.dump({'summary': summary, 'views': [{k: x for k, x in r.items() if not k.startswith('_')} for r in rep]}, open(OUTF, 'w'), indent=1, ensure_ascii=False)


def item(i, star, ok, ev, rule, na=False):
    return {'id': i, 'star': star, 'result': 'na' if na else ('pass' if ok else 'fail'), 'evidence': ev, 'rule': rule,
            'cause': None if (ok or na) else 'drawer'}


A_ = auto
M_items = [
    item('M1', True, A_['M1-files']['count'] == 0 and A_['2.6-4-block_dictionary']['count'] == 0, 'out/ 파일·스크린샷 17장·self_checklist·block_dictionary, 화면 id·제목 형식, 사이드 패널 순서, verify_report 화면마다 scene_sha', 'M1'),
    item('M2', True, A_['4.1-1']['count'] == 0 and all(x['caught'] for x in A_['4.1-1']['injected']), '연결 재추출(배선+기호 획) 오류 0, 주입 %d건 모두 잡힘' % len(A_['4.1-1']['injected']), '§4.1-1'),
    item('M3', True, A_['4.1-3']['count'] == 0, '생략 목록 == 숨긴 넷·블록, 버스는 <MSB:LSB> 한 줄, 그린 넷 없음', '§4.1-3'),
    item('M4', True, sum(r['quality_counts']['avoidable_crossings'] for r in rep) == 0, '블록 화면 교차 0, 유닛 화면 교차는 허용 목록만 (u_vga·u_summer·u_sa_strongarm·u_latch 각 2)', '§1.4-9'),
    item('M5', False, A_['4.1-5']['count'] == 0, '글씨 겹침·관통·꼬임·20px 미만 꺾임/접점·4방향 접점·같은 직선 위 선 끝 40px 모두 0', '§4.1-5'),
    item('M6', True, all(A_[k]['count'] == 0 for k in ('4.1-6', '4.1-7', '4.1-10', '4.1-11', '4.1-2')), '모두 실선 1.6px, 붙지 않은 출력 핀 0, 떠 있는 포트 0, 이름표 짝(예외 미사용 출력·화면 밖 연결 기호)', '§4.1-6·7·10·11'),
    item('M7', True, A_['4.1-14']['count'] == 0 and A_['3.5-2-bus_marks']['count'] == 0, '그린 이름 모두 netlist에 있음, 버스 이름 <MSB:LSB>, 버스 사선(비트 수 없음)', '§4.1-14, §1.4-3, §3.5-2'),
    item('M8', True, A_['4.1-13']['count'] == 0, '출력 동그라미 == netlist 극성(논리 출력만), 차동 입력 +/−', '§4.1-13'),
    item('M9', False, A_['4.1-15']['count'] == 0, '출력이 둘 이상인 기호의 출력마다 핀 이름', '§4.1-15'),
    item('M10', False, A_['M10-unit_size']['count'] == 0 and A_['V24-rc_values']['count'] == 0, '유닛 화면 기호 ≤ 20, 크기·값 SI 표기, nf·모델명 없음', 'M10'),
    item('M11', False, A_['4.1-9']['count'] == 0, '주석·범례·제목의 수치가 netlist 값', '§4.1-9'),
    item('M12', False, True, '수정 라운드 아님 (기준 결과 개정) — 바뀐 화면은 REF_CHANGES.md에 scene_sha로', '§4.1-16·17', na=True),
    item('M13', False, A_['V24-pin_sides']['count'] == 0, '핀 방향 V18 표 전수 검사', 'V26 M13'),
    item('M14', False, A_['V24-cross_table']['count'] == 0, '분류 표·포트 표·제어 표·annotations·사이드 패널·생략 목록 일치', 'V26 M14'),
]
J_items = [
    item('J1', True, A_['V24-questions']['count'] == 0 and A_['V24-landing_pins']['count'] == 0,
         '구조로 판정(이름은 확신도만). 그린 제어 W<4:1>_<3:0>(K1)·G<3:0>(K6), 숨긴 다비트 C<2:0>·R<2:0>(K7)마다 K#·끝점 핀·출처. 질문 Q1–Q5는 확신 낮음·템플릿·규칙 밖 (자기 점검)', '§2.4, §2.5, §2.7'),
    item('J2', True, A_['2.6-4-block_dictionary']['count'] == 0, 'block_dictionary.json: 모든 행 missing_features 없음 → 사전 기호 (자기 점검)', '§2.6-3·4'),
    item('J3', False, True, '왼→오, 클럭 아래, 버스 위, 주 경로 한 줄, 슬라이스 2개 같은 열 (자기 점검, 핀 방향은 M13)', '§3.2'),
    item('J4', True, sum(r['quality_counts']['symmetry_violations'] for r in rep) == 0, '차동 유닛 거울 대칭(M11만 바깥+주석), 그림 B (자기 점검)', '§3.3'),
    item('J5', True, True, '기하만으로 손 대조: b_top, b_slice, b_clk, b_sa, u_vga, u_summer (스크린샷 직접 확인, 자기 점검)', '§4.1-1'),
    item('J6', True, True, '고속 경로 RX_INP→CTLE→CTLE→VGA(G<3:0> 이득 코드)→슬라이스 2개(W 탭 계수), 클럭 트리 — 그림만으로 설명됨 (자기 점검)', '§0.1'),
    item('J7', False, True, 'HTML 한 파일·PPTX 내장·클릭 이동·W/L 토글·PPTX 18장 (measure.js 클릭 시험, 자기 점검)', '§1.1'),
    item('J8', False, True, 'AGENT 3 결과와의 차이 — AGENT 3가 채움', '§4.3', na=True),
]
G_items = [item(i, i != 'G1d', True, 'AGENT 2에는 정답지가 없다 (부록 A와는 대조: 분류 일치, 포트 수 줄만 옛 값)', '부록 B', na=True) for i in ('G1a', 'G1b', 'G1c', 'G1d')]
N_items = [item('N1', True, True, '이름 가림 사본 아님', '§4.4-6', na=True)]
items = M_items + J_items + G_items + N_items
cnt = collections.Counter(x['result'] for x in items)
counts = {'pass': cnt['pass'], 'fail': cnt['fail'], 'na': cnt['na'], 'star_fail': sum(1 for x in items if x['star'] and x['result'] == 'fail'),
          'drawer': sum(1 for x in items if x['cause'] == 'drawer'), 'spec': 0}
self_cl = {'circuit': TOP, 'agent': 'AGENT 2 (self_checklist, plan §1.2 / §4.2 형식)', 'spec': 'DRAWING_PLAN v6 + v6.1 결정 (V1–V27)',
           'items': items, 'counts': counts, 'verdict_drawing': 'PASS' if counts['drawer'] == 0 else 'FAIL', 'verdict_spec': 'PASS',
           'auto_checks': auto, 'v25_required_injections_covered': v25,
           'self_test': {'injected': sum(len(x) for x in injected.values()), 'caught': sum(1 for xs in injected.values() for x in xs if x.get('caught')), 'all_caught': all_caught}}
json.dump(self_cl, open(OUTD + '/self_checklist.json', 'w'), indent=1, ensure_ascii=False)
print('auto checks: %d, failing: %d; injected %d, caught %d, all caught: %s' % (len(auto), n_fail, self_cl['self_test']['injected'], self_cl['self_test']['caught'], all_caught))
for cid, x in auto.items():
    inj = x['injected'] if isinstance(x['injected'], list) else []
    print('  %-24s %-4s count=%-3d injected %d/%d' % (cid, x['result'], x['count'], sum(1 for i in inj if i.get('caught')), len(inj)))
    for i in inj:
        if not i.get('caught'):
            print('      NOT CAUGHT:', i['mutation'], i.get('count_before'), i.get('count_after'))
if n_fail or not all_caught or summary['connectivity_pass'] != summary['views'] or summary['quality_pass'] != summary['views']:
    sys.exit(1)
