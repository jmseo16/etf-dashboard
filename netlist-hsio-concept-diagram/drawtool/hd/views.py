"""Build one drawable model per cell: components, pins, visible nets, ports, omitted items."""
import re
from collections import OrderedDict, defaultdict
from . import netlist as NL
from .analyze import VISIBLE, cell_occurrences

RANK = ['hs_data', 'hs_clock', 'reference', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K8', 'K9', 'status', 'other', 'bias', 'hidden', 'rail']
ANON = re.compile(r'^(net|n)$')


class Pin(object):
    def __init__(self, name, nets, side, cls, direction, bits):
        self.name = name          # label drawn at the pin
        self.nets = tuple(nets)   # local nets carried (1 = scalar, >1 = bus)
        self.side = side          # 'l' 'r' 't' 'b'
        self.cls = cls
        self.dir = direction      # 'in' / 'out'
        self.bits = bits          # per bit: [(instance name, cell pin), ...] (for verification)
        self.x = self.y = None

    @property
    def key(self):
        return self.nets


class Comp(object):
    def __init__(self, cid, kind):
        self.id, self.kind = cid, kind      # kind: inst / mos / res / cap / dio
        self.members = [cid]
        self.cell = None
        self.sym = 'box'
        self.title = ''
        self.sub = ''
        self.pins = OrderedDict()
        self.dev = None
        self.target = None                  # view id opened by a click
        self.bubble = False
        self.size_text = ''
        self.rail_pins = {}                 # pin name -> rail net (drawn as a local tag)
        self.gray_pins = {}                 # pin name -> hidden net (drawn as a gray label)


class View(object):
    def __init__(self, cell, level):
        self.cell, self.level = cell, level
        self.id = ('u_' if level == 'unit' else 'b_') + re.sub(r'[^a-z0-9_]', '_', cell)
        self.comps = []
        self.ports = []                     # (name, nets tuple, cls, dir)
        self.omitted = []                   # text lines
        self.notes = []
        self.netcls = {}
        self.legend = []


def bus_label(nets):
    """Name of a net tuple: stem<hi:lo> when it is a contiguous bus, else the first … last names."""
    if len(nets) == 1:
        return nets[0]
    sp = [NL.bus_split(x) for x in nets]
    stems = set(s for s, i in sp)
    idx = [i for s, i in sp]
    if len(stems) == 1 and all(i is not None for i in idx):
        if idx == list(range(idx[0], idx[0] - len(idx), -1)) or idx == list(range(idx[0], idx[0] + len(idx))):
            return '%s<%d:%d>' % (sp[0][0], idx[0], idx[-1])
    return '%s … %s' % (nets[0], nets[-1])


def best_class(classes):
    cs = [c for c in classes if c]
    if not cs:
        return 'other'
    return min(cs, key=lambda c: RANK.index(c) if c in RANK else RANK.index('other'))


def build(cells, top, A, ann=None):
    """Return OrderedDict view id -> View for every cell that is drawn, top first."""
    ann = ann or {}
    occ = cell_occurrences(cells, top)
    # class of each local net of each cell: the most visible class over all places the cell is used
    lcls = {}
    for cname, lst in occ.items():
        m = defaultdict(list)
        for path, local in lst:
            for ln, fn in local.items():
                m[ln].append(A.cls.get(fn))
        lcls[cname] = dict((ln, best_class(v)) for ln, v in m.items())
    rails_l = {}
    for cname, lst in occ.items():
        r = set()
        for path, local in lst:
            for ln, fn in local.items():
                if fn in A.rails:
                    r.add(ln)
        rails_l[cname] = r
    sup_l = dict((c, set(ln for path, local in lst for ln, fn in local.items() if fn in A.sup)) for c, lst in occ.items())
    # pin direction of each cell port: 'out' when a device inside the cell drives the net
    pdir = {}
    for cname, lst in occ.items():
        d = {}
        for port in cells[cname].ports:
            out = False
            for path, local in lst:
                fn = local[port]
                pre = (path + '/') if path else ''
                for i in A.drivers.get(fn, ()):
                    if A.flat[i][0].startswith(pre) and path != '':
                        out = True
                        break
                if out:
                    break
            d[port] = 'out' if out else 'in'
        # pass switches (a mux): of the ports their channels join, the one most switches meet at is the output
        c_ = cells[cname]
        rl_ = rails_l[cname]
        pas_ = [e for e in c_.devs if e.kind == 'm' and e.pins['d'] not in rl_ and e.pins['s'] not in rl_ and e.pins['d'] != e.pins['s']
                and e.pins['d'] in d and e.pins['s'] in d]     # a switch between two ports of the cell
        driven_ = set(e.pins['d'] for e in c_.devs if e.kind == 'm' and (e.pins['s'] in rl_)) | \
            set(n for e in c_.devs if e.kind == 'x' for p_, n in e.pins.items() if pdir.get(e.model, {}).get(p_) == 'out')
        if pas_ and cname != top:
            cnt = defaultdict(int)
            for e in pas_:
                for t in ('d', 's'):
                    if e.pins[t] in d and e.pins[t] not in driven_:
                        cnt[e.pins[t]] += 1
            if len(cnt) > 1:
                top_n = max(cnt.values())
                best = [x for x, v in cnt.items() if v == top_n]
                if len(best) == 1:
                    for x in cnt:
                        d[x] = 'out' if x == best[0] else 'in'
        pdir[cname] = d
    roles = {}

    def role(cname):
        if cname in roles:
            return roles[cname]
        c = cells[cname]
        forced = ann.get('block_role', {}).get(cname)
        mos = [d for d in c.devs if d.kind == 'm']
        subs = [d for d in c.devs if d.kind == 'x']
        r = 'box'
        path0, local0 = occ[cname][0]
        pre = (path0 + '/') if path0 else ''
        flat_idx = [i for i, (pth, d, pm) in enumerate(A.flat) if pth.startswith(pre)] if cname != top else []
        if cname == top:
            roles[cname] = 'top'
            return 'top'
        nonrail = [p for p in c.ports if p not in rails_l[cname]]
        ins = [p for p in nonrail if pdir[cname][p] == 'in']
        outs = [p for p in nonrail if pdir[cname][p] == 'out']
        kcl = set(lcls[cname].get(p) for p in nonrail)
        if not subs and len(mos) == 2 and len(c.devs) == 2 and len(ins) == 1 and len(outs) == 1 and \
                set(d.mtype for d in mos) == {'n', 'p'} and mos[0].pins['g'] == mos[1].pins['g']:
            r = 'inv'
        elif subs and not mos and len(subs) == len(c.devs) and len(ins) == 1 and len(outs) == 1 and \
                all(role(d.model) in ('inv', 'buf') for d in subs):
            ninv = sum(1 for d in subs if role(d.model) == 'inv')
            r = 'buf' if ninv % 2 == 0 else 'inv'
        elif not subs and len(mos) == 4 and len(c.devs) == 4 and len(ins) == 1 and len(outs) == 1 and _is_two_inverters(c):
            r = 'buf'
        elif not subs and _is_static_gate(c, rails_l[cname]) and len(outs) == 1:
            r = 'gate'
        elif any(i in A.ckdev and A.kind[i] == 'm' and (A.ch[i][0] in A.rails or A.ch[i][1] in A.rails) for i in flat_idx) and not subs:
            r = 'samp'
        elif not subs and _count_pairs(c, rails_l[cname]) >= 2 and any(d.kind == 'r' for d in c.devs) and 'K1' in kcl:
            r = 'sum'
        elif any(lcls[cname].get(p) == 'reference' for p in outs) and not (kcl & {'hs_data', 'hs_clock'}) and \
                (subs or any(d.kind == 'r' for d in c.devs) or
                 any(d.pins['d'] in rails_l[cname] or d.pins['s'] in rails_l[cname] for d in mos)):
            r = 'vref'              # something in the cell makes the level (not a bare pass switch)
        elif nonrail and not (kcl & {'hs_data', 'hs_clock', 'reference'}) and any(lcls[cname].get(p) in VISIBLE for p in outs):
            r = 'dec'
        roles[cname] = forced or r
        return roles[cname]

    views = OrderedDict()
    drawn_cells = []

    def is_dummy(d, cname):
        """Instance with every data input tied to a rail and every visible output unused."""
        vis_in = [p for p, n in d.pins.items() if n not in rails_l[cname] and pdir[d.model][p] == 'in'
                  and lcls[cname].get(n) == 'hs_data']
        tied = [p for p, n in d.pins.items() if n in rails_l[cname] and lcls[d.model].get(p) in ('hs_data',)]
        outs = [n for p, n in d.pins.items() if pdir[d.model][p] == 'out' and n not in rails_l[cname]]
        use = defaultdict(int)
        for e in cells[cname].devs:
            for n in e.pins.values():
                use[n] += 1
        unused = all(use[n] == 1 and n not in cells[cname].ports for n in outs)
        return bool(outs) and unused and not vis_in and bool(tied)

    def make(cname):
        if cname in drawn_cells:
            return
        drawn_cells.append(cname)
        c = cells[cname]
        subs = [d for d in c.devs if d.kind == 'x']
        level = 'block' if subs else 'unit'
        V = View(cname, level)
        V.title = '%s — %s' % (cname, '블록 레벨' if level == 'block' else 'unit level')
        cl = lcls[cname]
        V.netcls = cl
        rl = rails_l[cname]
        use = defaultdict(int)
        for e in c.devs:
            for nn in e.pins.values():
                use[nn] += 1

        rawnets = set(nn for e in c.devs if e.kind != 'x' for nn in e.pins.values())

        def vis(nn):
            if nn in rl:
                return False
            k = cl.get(nn, 'other')
            if level == 'unit' or nn in rawnets:
                return k not in ('bias', 'hidden')
            return k in VISIBLE

        hide_inst = set(x.lower() for x in ann.get('hide_instances', []))
        for d in c.devs:
            if d.kind == 'x':
                sub = cells[d.model]
                r = role(d.model)
                outs = [n for p, n in d.pins.items() if pdir[d.model][p] == 'out' and n not in rl]
                vis_out = [n for n in outs if vis(n)]
                vis_any = [n for p, n in d.pins.items() if vis(n)]
                has_hs = any(cl.get(n) in ('hs_data', 'hs_clock') for p, n in d.pins.items() if n not in rl)
                if d.name in hide_inst or r == 'omit':
                    V.omitted.append('%s (%s) — 사용자 지정 생략' % (d.name, d.model))
                    continue
                if not vis_any or (not vis_out and not has_hs):
                    V.omitted.append('%s (%s) — %s' % (d.name, d.model, '고속 신호와 무관' if not vis_any or all(cl.get(n) in ('bias', 'hidden', 'other') for n in outs) else '일반 제어만 만듦'))
                    continue
                if is_dummy(d, cname):
                    V.omitted.append('%s (%s) — 더미(입력이 전원에 묶이고 출력 미사용)' % (d.name, d.model))
                    continue
                K = Comp(d.name, 'inst')
                K.cell, K.dev = d.model, d
                K.sym = {'inv': 'inv', 'buf': 'buf'}.get(r, 'box')
                K.title = {'samp': 'SA', 'sum': 'Σ', 'vref': 'VREF'}.get(r, d.model)
                K.sub = d.model if K.title != d.model else ''
                K.role = r
                K.bubble = r in ('inv',) or (r == 'gate')
                has_data_in = any(cl.get(n) == 'hs_data' and pdir[d.model][p] == 'in' for p, n in d.pins.items())
                any_hs = any(cl.get(n) in ('hs_data', 'hs_clock', 'reference') for p, n in d.pins.items() if n not in rl)
                for p, n in d.pins.items():
                    if n in rl:
                        continue
                    if not vis(n):
                        continue
                    k = cl.get(n, 'other')
                    dr = pdir[d.model][p]
                    if dr == 'out':
                        side = 'r'
                    elif k == 'hs_data' or k == 'reference' or not any_hs:
                        side = 'l'
                    elif k == 'hs_clock':
                        side = 'b' if has_data_in else 'l'
                    else:
                        side = 't'
                    K.pins[p] = Pin(p, [n], side, k, dr, [[(d.name, p)]])
                K.target = d.model
                V.comps.append(K)
            else:
                nets = [n for n in d.pins.values()] if d.kind != 'm' else [d.pins['d'], d.pins['g'], d.pins['s']]
                nonrail = [n for n in nets if n not in rl]
                if level == 'block':
                    if not any(vis(n) for n in nonrail):
                        if nonrail:
                            V.omitted.append('%s — %s' % (d.name, '일반 제어·바이어스에만 연결'))
                        continue
                    if d.kind == 'd' and len(nonrail) == 1 and cl.get(nonrail[0]) == 'hs_clock' or \
                            (d.kind == 'd' and len(nonrail) == 1 and nonrail[0] not in c.ports and 'ant' in d.model):
                        V.omitted.append('%s — 안테나 다이오드(패드가 아닌 넷 → 전원)' % d.name)
                        continue
                kind = {'m': 'mos', 'r': 'res', 'c': 'cap', 'd': 'dio'}[d.kind]
                if d.kind == 'm' and d.pins['d'] == d.pins['s']:
                    kind = 'cap'            # MOS used as a capacitor between gate and tied channel
                K = Comp(d.name, kind)
                K.dev = d
                K.size_text = d.size_text() + (' (MOS C)' if kind == 'cap' and d.kind == 'm' else '')
                K.mtype = d.mtype
                if kind == 'mos':
                    pl = [('d', d.pins['d']), ('g', d.pins['g']), ('s', d.pins['s'])]
                elif kind == 'cap' and d.kind == 'm':
                    pl = [('a', d.pins['g']), ('b', d.pins['d'])]
                else:
                    pl = list(d.pins.items())
                for p, n in pl:
                    if n in rl:
                        K.rail_pins[p] = n
                    elif not vis(n):
                        K.gray_pins[p] = n
                    K.pins[p] = Pin(p, [n], None, cl.get(n, 'other'), 'in' if p == 'g' else 'io', [[(d.name, p)]])
                V.comps.append(K)
        # ------------------------------------------------ regular structures drawn as one symbol
        _collapse_trees(V)
        _collapse_ladders(V, cl, rl, c.ports)
        # ------------------------------------------------ bus pins on one symbol (cell ports stem<k>)
        for K in V.comps:
            if K.kind != 'inst' or getattr(K, 'folded', False):
                continue
            groups = OrderedDict()
            for p in list(K.pins):
                s, ix = NL.bus_split(p)
                if ix is not None and not ANON.match(s):
                    groups.setdefault((s, K.pins[p].side), []).append((ix, p))
            for (s, side), lst in groups.items():
                if len(lst) < 2:
                    continue
                lst.sort(reverse=True)
                nets = [K.pins[p].nets[0] for ix, p in lst]
                if len(set(nets)) != len(nets) or len(set(K.pins[p].cls for ix, p in lst)) != 1:
                    continue
                first = lst[0][1]
                newp = Pin('%s<%d:%d>' % (s, lst[0][0], lst[-1][0]), nets, side, K.pins[first].cls, K.pins[first].dir,
                           [[(K.id, p)] for ix, p in lst])
                order = list(K.pins.keys())
                pos = order.index(first)
                for ix, p in lst:
                    del K.pins[p]
                items = list(K.pins.items())
                items.insert(min(pos, len(items)), (newp.name, newp))
                K.pins = OrderedDict(items)
        # ------------------------------------------------ merge repeated instances (same cell, bit-indexed nets)
        if level == 'block':
            _merge_instances(V)
        # ------------------------------------------------ overlapping bus tuples -> expand to scalars
        def broken_tuples():
            owner = defaultdict(set)
            for K in V.comps:
                for P in K.pins.values():
                    for n in P.nets:
                        owner[n].add(P.nets)
            return set(t for n, ts in owner.items() if len(ts) > 1 for t in ts if len(t) > 1)
        broken = broken_tuples()
        # a merged block whose bus overlaps another use of the same nets is drawn as separate instances again
        for K in list(V.comps):
            if len(K.members) > 1 and any(P.nets in broken for P in K.pins.values()):
                i = V.comps.index(K)
                V.comps[i:i + 1] = K.orig
                V.legend = [l for l in V.legend if not l.startswith(K.id + ' = ')]
        broken = broken_tuples()
        if broken:
            for K in V.comps:
                items = []
                for name, P in K.pins.items():
                    if P.nets in broken and len(K.members) == 1:
                        for k, n in enumerate(P.nets):
                            pn = P.bits[k][0][1]
                            items.append((pn, Pin(pn, [n], P.side, P.cls, P.dir, [P.bits[k]])))
                    else:
                        items.append((name, P))
                K.pins = OrderedDict(items)
        # ------------------------------------------------ ports of the view
        keys = OrderedDict()
        for K in V.comps:
            for P in K.pins.values():
                if P.name in K.rail_pins or P.name in K.gray_pins:
                    continue
                keys.setdefault(P.nets, []).append((K, P))
        seen = set()
        for port in c.ports:
            if port in rl or not vis(port) or port in seen:
                continue
            tup = next((t for t in keys if port in t), None)
            if tup is None:
                continue
            if not all(x in c.ports for x in tup):
                tup = (port,)
            seen.update(tup)
            k = cl.get(port, 'other')
            drv = 'out' if (pdir[cname][port] == 'out' and cname != top) or (cname == top and port in A.out_ports) else 'in'
            V.ports.append((bus_label(tup), tup, k, drv))
        V.keys = keys
        # omission list: hidden nets of the cell
        hid = defaultdict(list)
        for n in sorted(set(nn for e in c.devs for nn in e.pins.values())):
            if n in rl:
                continue
            if not vis(n) and (n in c.ports or level == 'unit'):
                hid[cl.get(n, 'other')].append(n)
        txt = {'bias': '바이어스', 'hidden': '일반 제어', 'other': '내부'}
        for k, ns in hid.items():
            V.omitted.append('%s — %s' % (', '.join(_compress(ns)), txt.get(k, k)))
        if rl:
            V.omitted.append('%s — 전원' % ', '.join(sorted(rl)) if level == 'block' else '전원은 국소 전원 기호로 표시: %s' % ', '.join(sorted(rl)))
        V.sup = sup_l[cname] & rl
        V.rails = rl
        views[V.id] = V
        for K in V.comps:
            if K.kind == 'inst' and K.cell:
                make(K.cell)
                tid = next(v.id for v in views.values() if v.cell == K.cell)
                K.target = tid

    make(top)
    for V in views.values():
        V.role = role(V.cell) if V.cell != top else 'top'
        if V.level == 'unit':
            V.title += ' (%s)' % {'inv': '인버터', 'buf': '버퍼', 'samp': '비교기·샘플러', 'sum': '합산기', 'gate': '정적 CMOS 게이트',
                                  'vref': '기준 전압 발생', 'dec': '제어 로직'}.get(V.role, '트랜지스터 화면')
    return views, roles, lcls, pdir


def _compress(names):
    """['a<1>','a<0>','b'] -> ['a<1:0>', 'b']"""
    g, out = OrderedDict(), []
    for n in names:
        s, ix = NL.bus_split(n)
        if ix is None or ANON.match(s):
            out.append(n)
        else:
            g.setdefault(s, []).append(ix)
    for s, ix in g.items():
        ix.sort(reverse=True)
        out.append('%s<%d:%d>' % (s, ix[0], ix[-1]) if len(ix) > 1 else NL_name(s, ix[0], names))
    return out


def NL_name(stem, ix, names):
    for n in names:
        if NL.bus_split(n) == (stem, ix):
            return n
    return '%s%d' % (stem, ix)


def _is_two_inverters(c):
    mos = c.devs
    outs = defaultdict(list)
    for d in mos:
        outs[d.pins['d']].append(d)
    return len(outs) == 2 and all(len(v) == 2 and set(x.mtype for x in v) == {'n', 'p'} and v[0].pins['g'] == v[1].pins['g'] for v in outs.values())


def _count_pairs(c, rails):
    """Number of differential pairs: two same-type, same-size MOS sharing a non-rail source with different gates."""
    n, seen = 0, set()
    mos = [d for d in c.devs if d.kind == 'm' and d.pins['d'] != d.pins['s']]
    for i, a in enumerate(mos):
        for b in mos[i + 1:]:
            if a.name in seen or b.name in seen:
                continue
            if a.mtype == b.mtype and a.pins['s'] == b.pins['s'] and a.pins['s'] not in rails and a.pins['g'] != b.pins['g'] \
                    and a.pins['d'] != b.pins['d'] and a.params.get('w') == b.params.get('w') and a.params.get('m', '1') == b.params.get('m', '1'):
                n += 1
                seen.update((a.name, b.name))
    return n


def _is_static_gate(c, rails):
    mos = [d for d in c.devs if d.kind == 'm']
    if len(mos) != len(c.devs) or len(mos) < 2 or len(mos) > 8:
        return False
    gn = set(d.pins['g'] for d in mos if d.mtype == 'n')
    gp = set(d.pins['g'] for d in mos if d.mtype == 'p')
    return gn == gp and all(g in c.ports for g in gn)


def _merge_instances(V):
    """Instances of one cell whose pins differ only by a bit index become one symbol with bus pins."""
    groups = OrderedDict()
    intup = {}                     # net -> (bus tuple of a folded symbol, position)
    for K in V.comps:
        if getattr(K, 'folded', False):
            for P in K.pins.values():
                if len(P.nets) > 1:
                    for k, x in enumerate(P.nets):
                        intup.setdefault(x, (P.nets, k))
    for K in V.comps:
        if K.kind != 'inst' or getattr(K, 'folded', False):
            continue
        sig = [K.cell]
        ok = True
        for name, P in K.pins.items():
            if len(P.nets) > 1:
                sig.append((name, P.nets))
                continue
            s, ix = NL.bus_split(P.nets[0])
            if P.nets[0] in intup:
                sig.append((name, ('TUP', intup[P.nets[0]][0])))
            else:
                sig.append((name, ('BUS', s)) if ix is not None and not ANON.match(s) else (name, P.nets[0]))
        groups.setdefault(tuple(sig), []).append(K)
    for sig, lst in groups.items():
        if len(lst) < 2:
            continue
        varying, good = [], True
        for name in lst[0].pins:
            nets = [K.pins[name].nets for K in lst]
            if len(set(nets)) == 1:
                continue
            if len(set(nets)) == len(nets) and all(len(t) == 1 for t in nets):
                varying.append(name)
            else:
                good = False
        if not good:
            continue
        if varying:
            tk = [v for v in varying if lst[0].pins[v].nets[0] in intup]
            if tk:
                lst.sort(key=lambda K: intup[K.pins[tk[0]].nets[0]][1])
            else:
                key = varying[0]
                lst.sort(key=lambda K: -NL.bus_split(K.pins[key].nets[0])[1])
        import copy
        originals = [copy.deepcopy(K) for K in lst]
        head = lst[0]
        head.orig = originals
        for name, P in head.pins.items():
            if name in varying:
                P.nets = tuple(K.pins[name].nets[0] for K in lst)
                P.bits = [[(K.id, K.pins[name].bits[0][0][1])] for K in lst]
                P.name = name
            else:
                P.bits = [[(K.id, b[0][1]) for K in lst] for b in P.bits]
        head.members = [K.id for K in lst]
        ids = [K.id for K in lst]
        head.id = '%s … %s' % (ids[0], ids[-1]) if len(ids) > 2 else '%s, %s' % (ids[0], ids[1])
        head.mult = len(lst)
        V.legend.append('%s = %s (%s ×%d)' % (head.id, ', '.join(ids), head.cell, len(ids)))
        for K in lst[1:]:
            V.comps.remove(K)


def _collapse_trees(V):
    """A selection tree (instances of one cell, each output feeding a data input of the next) becomes one
    'MUX N:1' symbol: leaf inputs as one bus, the select nets of every level as buses, one output."""
    by_cell = OrderedDict()
    for K in V.comps:
        if K.kind == 'inst' and all(len(P.nets) == 1 for P in K.pins.values()):
            by_cell.setdefault(K.cell, []).append(K)
    for cell, lst in by_cell.items():
        if len(lst) < 3:
            continue
        outs = [[n for n, P in K.pins.items() if P.dir == 'out'] for K in lst]
        if any(len(o) != 1 for o in outs):
            continue
        op = outs[0][0]
        if any(o[0] != op for o in outs):
            continue
        drv = dict((K.pins[op].nets[0], K) for K in lst)
        if len(drv) != len(lst):
            continue
        dpins = [n for n in lst[0].pins if n != op and any(n in K.pins and K.pins[n].nets[0] in drv for K in lst)]
        if len(dpins) < 2 or any(d not in K.pins for K in lst for d in dpins):
            continue
        spins = [n for n in lst[0].pins if n != op and n not in dpins]
        users = defaultdict(int)       # how many pins in the whole view use a net
        for K in V.comps:
            for P in K.pins.values():
                for x in P.nets:
                    users[x] += 1
        child_of = set(K.pins[d].nets[0] for K in lst for d in dpins)
        roots = [K for K in lst if K.pins[op].nets[0] not in child_of]
        for root in roots:
            levels, leaves, ok = [[root]], [], True
            members = [root]

            def walk(K, depth):
                for d in dpins:
                    x = K.pins[d].nets[0]
                    ch = drv.get(x)
                    if ch is not None and ch is not K and users[x] == 2:
                        while len(levels) <= depth + 1:
                            levels.append([])
                        levels[depth + 1].append(ch)
                        members.append(ch)
                        walk(ch, depth + 1)
                    else:
                        leaves.append((x, K, d))
            walk(root, 0)
            if len(members) < 3 or len(set(x for x, _, _ in leaves)) != len(leaves):
                continue
            sel = {}
            for sp in spins:
                per = []
                for lv in levels:
                    ns = set(K.pins[sp].nets[0] for K in lv if sp in K.pins)
                    if len(ns) != 1 or any(sp not in K.pins for K in lv):
                        ok = False
                        break
                    per.append(ns.pop())
                if not ok or len(set(per)) != len(per):
                    ok = False
                    break
                sel[sp] = per
            if not ok:
                continue
            F = Comp('%s … %s' % (members[0].id, members[-1].id), 'inst')
            F.folded = True
            F.cell, F.dev = cell, root.dev
            F.sym, F.role = 'box', 'box'
            F.title = 'MUX %d:1' % len(leaves)
            F.sub = '%s ×%d' % (cell, len(members))
            F.members = [K.id for K in members]
            F.orig = list(members)
            d0 = root.pins[dpins[0]]
            F.pins['in'] = Pin('in<%d:0>' % (len(leaves) - 1), [x for x, _, _ in reversed(leaves)], d0.side, d0.cls, 'in',
                               [[(K.id, d)] for x, K, d in reversed(leaves)])
            for sp in spins:
                P0 = root.pins[sp]
                if len(levels) > 1:
                    F.pins[sp] = Pin('%s<%d:0>' % (sp, len(levels) - 1), sel[sp], P0.side, P0.cls, 'in',
                                     [[(K.id, sp) for K in lv] for lv in levels])
                else:
                    F.pins[sp] = Pin(sp, sel[sp], P0.side, P0.cls, 'in', [[(K.id, sp) for K in levels[0]]])
            Po = root.pins[op]
            F.pins[op] = Pin(op, Po.nets, Po.side, Po.cls, 'out', [[(root.id, op)]])
            i = V.comps.index(members[0])
            for K in members:
                V.comps.remove(K)
            V.comps.insert(min(i, len(V.comps)), F)
            V.legend.append('%s = %s (%s ×%d, %d:1 선택 트리)' % (F.id, ', '.join(F.members), cell, len(members), len(leaves)))


def _collapse_ladders(V, cl, rl, ports):
    """A series string of resistors (six or more) becomes one 'R ×N' symbol; the nodes used elsewhere are its tap bus."""
    res = [K for K in V.comps if K.kind == 'res' and len(K.pins) == 2]
    if len(res) < 6:
        return
    at = defaultdict(list)
    for K in res:
        for P in K.pins.values():
            at[P.nets[0]].append(K)
    users = defaultdict(int)
    for K in V.comps:
        for P in K.pins.values():
            for x in P.nets:
                users[x] += 1
    inner = lambda x: x not in rl and len(at[x]) == 2 and at[x][0] is not at[x][1]
    done = set()

    def extend(K, x):
        out = []
        while inner(x):
            nxt = at[x][0] if at[x][1] is K else at[x][1]
            if nxt in done:
                break
            done.add(nxt)
            out.append(nxt)
            o = [P.nets[0] for P in nxt.pins.values()]
            o.remove(x)
            K, x = nxt, o[0]
        return out, x
    for K0 in res:
        if K0 in done:
            continue
        done.add(K0)
        n0, n1 = [P.nets[0] for P in K0.pins.values()]
        left, e0 = extend(K0, n0)
        right, e1 = extend(K0, n1)
        chain = left[::-1] + [K0] + right
        ends = [e0, e1]
        if len(chain) < 6 or any(K.gray_pins for K in chain):
            continue
        # nodes along the chain, in order
        nodes = []
        for a, b in zip(chain, chain[1:]):
            sh = set(P.nets[0] for P in a.pins.values()) & set(P.nets[0] for P in b.pins.values())
            if len(sh) != 1:
                nodes = None
                break
            nodes.append(sh.pop())
        if not nodes or len(set(nodes)) != len(nodes):
            continue
        taps = [x for x in nodes if users[x] > 2 or x in ports]
        if len(taps) < 2:
            continue
        # same order as a bus that already carries exactly these nets (a folded selection tree)
        for K in V.comps:
            for P in K.pins.values():
                if len(P.nets) == len(taps) and set(P.nets) == set(taps):
                    taps = list(P.nets)
        F = Comp('%s … %s' % (chain[0].id, chain[-1].id), 'inst')
        F.folded = True
        F.cell, F.dev = None, chain[0].dev
        F.sym, F.role = 'box', 'box'
        F.title = 'R ×%d' % len(chain)
        sizes = set(K.size_text for K in chain)
        e = [x for x in ends if x in rl]
        F.sub = ('%s ' % sizes.pop() if len(sizes) == 1 else '') + ('(%s – %s)' % (ends[0], ends[1]) if len(e) == 2 else '저항 사다리')
        F.members = [K.id for K in chain]
        F.orig = list(chain)
        pin_of = lambda K, x: [n for n, P in K.pins.items() if P.nets[0] == x][0]
        for nm, x, K in (('a', ends[0], chain[0]), ('b', ends[1], chain[-1])):
            if x not in rl and x not in taps:
                F.pins[nm] = Pin(nm, [x], 'l', cl.get(x, 'other'), 'in', [[(K.id, pin_of(K, x))]])
        cls = best_class([cl.get(x, 'other') for x in taps])
        F.pins['tap'] = Pin('tap<%d:0>' % (len(taps) - 1), taps, 'r', cls, 'out',
                            [[(K.id, pin_of(K, x)) for K in at[x]] for x in taps])
        i = V.comps.index(chain[0])
        for K in chain:
            V.comps.remove(K)
        V.comps.insert(min(i, len(V.comps)), F)
        V.legend.append('%s = %s (직렬 저항 %d개, 탭 %d개)' % (F.id, ', '.join(F.members), len(chain), len(taps)))
