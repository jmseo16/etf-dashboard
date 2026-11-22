"""HSPICE / Virtuoso-style netlist parser + flattener (no name-based rules)."""
import re

SI = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3,
      'meg': 1e6, 'g': 1e9, 't': 1e12}


def num(s):
    s = s.strip().lower()
    m = re.match(r'^([-+]?[0-9.]+(?:e[-+]?\d+)?)(meg|[fpnumkgt])?', s)
    if not m:
        return None
    v = float(m.group(1))
    if m.group(2):
        v *= SI[m.group(2)]
    return v


def parse(path):
    raw = open(path).read().splitlines()
    lines = []
    for ln in raw:
        s = ln.strip()
        if not s or s.startswith('*'):
            continue
        if s.startswith('+'):
            lines[-1] += ' ' + s[1:].strip()
        else:
            lines.append(s)
    cells = {}
    order = []
    cur = None
    for s in lines:
        tok = s.split()
        t0 = tok[0].upper()
        if t0 == '.SUBCKT':
            cur = {'name': tok[1], 'ports': tok[2:], 'elems': []}
            cells[tok[1]] = cur
            order.append(tok[1])
        elif t0 == '.ENDS':
            cur = None
        elif t0.startswith('.'):
            continue
        elif cur is not None:
            name = tok[0]
            k = name[0].upper()
            if k == 'M':
                d, g, s_, b, model = tok[1:6]
                params = {}
                for p in tok[6:]:
                    if '=' in p:
                        a, v = p.split('=', 1)
                        params[a.lower()] = v
                mtype = 'p' if model.upper().startswith('P') else 'n'
                cur['elems'].append({'name': name, 'kind': 'mos', 'type': mtype, 'model': model,
                                     'terms': {'d': d, 'g': g, 's': s_, 'b': b}, 'params': params})
            elif k == 'D':
                a, c, model = tok[1:4]
                params = {p.split('=')[0].lower(): p.split('=')[1] for p in tok[4:] if '=' in p}
                cur['elems'].append({'name': name, 'kind': 'dio', 'terms': {'p': a, 'n': c}, 'value': model, 'params': params})
            elif k in 'RCL':
                n1, n2 = tok[1:3]
                val = tok[3] if len(tok) > 3 else ''
                cur['elems'].append({'name': name, 'kind': {'R': 'res', 'C': 'cap', 'L': 'ind'}[k],
                                     'terms': {'p': n1, 'n': n2}, 'value': val})
            elif k == 'X':
                # last token without '=' is the subckt name
                toks = [t for t in tok[1:] if '=' not in t]
                sub = toks[-1]
                nodes = toks[:-1]
                cur['elems'].append({'name': name, 'kind': 'inst', 'cell': sub, 'nodes': nodes})
    # resolve instance pin maps
    for c in cells.values():
        for e in c['elems']:
            if e['kind'] == 'inst':
                sub = cells[e['cell']]
                if len(sub['ports']) != len(e['nodes']):
                    raise ValueError('port count mismatch %s in %s' % (e['name'], c['name']))
                e['pins'] = dict(zip(sub['ports'], e['nodes']))
    return cells, order


def cell_nets(cell):
    nets = []
    seen = set()
    for p in cell['ports']:
        if p not in seen:
            nets.append(p); seen.add(p)
    for e in cell['elems']:
        vals = e['pins'].values() if e['kind'] == 'inst' else e['terms'].values()
        for n in vals:
            if n not in seen:
                nets.append(n); seen.add(n)
    return nets


def flatten(cells, top):
    """Return list of flat primitive devices. Each: path, cell, local, kind, type, terms(global), lterms(local), params/value, inst (instance path)."""
    devs = []

    def rec(cname, prefix, netmap):
        c = cells[cname]
        def g(n):
            if n in netmap:
                return netmap[n]
            return prefix + n
        for e in c['elems']:
            if e['kind'] == 'inst':
                sub = cells[e['cell']]
                nm = {p: g(n) for p, n in e['pins'].items()}
                rec(e['cell'], prefix + e['name'] + '/', nm)
            else:
                d = {'path': prefix + e['name'], 'cell': cname, 'local': e['name'], 'kind': e['kind'],
                     'inst': prefix, 'lterms': dict(e['terms']),
                     'terms': {k: g(v) for k, v in e['terms'].items()}}
                if e['kind'] == 'mos':
                    d['type'] = e['type']; d['params'] = e['params']; d['model'] = e['model']
                else:
                    d['value'] = e.get('value')
                devs.append(d)
    top_ports = cells[top]['ports']
    rec(top, '', {p: p for p in top_ports})
    return devs


def instance_tree(cells, top):
    """list of (inst_path, cell, netmap local->global)"""
    out = []

    def rec(cname, prefix, netmap):
        out.append((prefix, cname, dict(netmap)))
        c = cells[cname]
        def g(n):
            return netmap.get(n, prefix + n)
        for e in c['elems']:
            if e['kind'] == 'inst':
                nm = {p: g(n) for p, n in e['pins'].items()}
                # also add internal nets lazily: handled by g in child
                rec(e['cell'], prefix + e['name'] + '/', nm)
    rec(top, '', {p: p for p in cells[top]['ports']})
    # complete netmaps with internal nets
    res = []
    for prefix, cname, nm in out:
        full = {}
        for n in cell_nets(cells[cname]):
            full[n] = nm.get(n, prefix + n)
        res.append((prefix, cname, full))
    return res


def fmt_len(v):
    """format W/L string like '24u' '45n'"""
    return v


# ======================================================================================
# v6.1 helpers shared by the generator and the checker (plan §3.5-6, §2.5-7, §3.4-6/§4.1-13)
# ======================================================================================
_PFX = [(1e12, 't'), (1e9, 'g'), (1e6, 'meg'), (1e3, 'k'), (1, ''), (1e-3, 'm'), (1e-6, 'u'), (1e-9, 'n'), (1e-12, 'p'), (1e-15, 'f')]


def fmt_si(s):
    """netlist value string -> SI-prefixed string (plan §3.5-6): '2000' -> '2k', '600e-9' -> '600n', '50f' -> '50f'"""
    v = num(str(s))
    if v is None:
        return str(s)
    if v == 0:
        return '0'
    for mul, p in _PFX:
        if abs(v) >= mul * 0.9999999:
            m = v / mul
            txt = ('%.3f' % m).rstrip('0').rstrip('.')
            return txt + p
    return str(s)


def si_equal(a, b, rel=1e-9):
    va, vb = num(str(a)), num(str(b))
    return va is not None and vb is not None and abs(va - vb) <= rel * max(abs(va), abs(vb), 1e-30)


def group_bus(names):
    """group bit names into <MSB:LSB> buses (plan §2.5-7, §1.4-3). Returns [(busname, [bits LSB first], notation)];
    notation: 'angle' (<n>), 'suffix' (number tail, e.g. G0), 'underscore2' (two indices, e.g. W1_0), 'single'."""
    import collections as _c
    out = []
    two = _c.defaultdict(list); one = _c.defaultdict(list); rest = []
    for n in names:
        m2 = re.match(r'^(\D*?)(\d+)_(\d+)$', n)
        m1 = re.match(r'^(.*?\D)(\d+)$', n) or re.match(r'^()(\d+)$', n)
        ma = re.match(r'^(.*)<(\d+)>$', n)
        if ma:
            one[(ma.group(1), '<>')].append((int(ma.group(2)), n))
        elif m2:
            two[m2.group(1)].append((int(m2.group(2)), int(m2.group(3)), n))
        elif m1:
            one[(m1.group(1), '')].append((int(m1.group(2)), n))
        else:
            rest.append(n)
    for k, v in two.items():
        a = sorted({x for x, _, _ in v}); b = sorted({y for _, y, _ in v})
        if len(v) == len(a) * len(b) and a == list(range(a[0], a[-1] + 1)) and b == list(range(b[0], b[-1] + 1)) and len(v) > 1:
            bits = [n for _, _, n in sorted(v)]
            out.append(('%s<%d:%d>_<%d:%d>' % (k, a[-1], a[0], b[-1], b[0]), bits, 'underscore2'))
        else:
            rest += [n for _, _, n in v]
    for (k, kind), v in one.items():
        idx = sorted(i for i, _ in v)
        if len(v) > 1 and idx == list(range(idx[0], idx[-1] + 1)):
            out.append(('%s<%d:%d>' % (k, idx[-1], idx[0]), [n for _, n in sorted(v)], 'angle' if kind else 'suffix'))
        else:
            rest += [n for _, n in v]
    for n in rest:
        out.append((n, [n], 'single'))
    return out


class Polarity:
    """Structural signal polarity (plan §3.4-6 반전 블록, §4.1-13 출력별 극성).
    Edges between local nets of a cell: gate -> loaded drain (inverting), stacked source -> drain and
    follower gate -> source (non-inverting), conducting TG / series R,C (non-inverting, both ways, not through a
    common-mode node), sub-instance input port -> output port (child polarity). Clock-role gates stop by
    construction (their drains carry no load). BFS from the main input(s); the shortest path gives the parity."""

    def __init__(self, cells, top):
        import collections as _c
        self.cells = cells
        devs = flatten(cells, top)
        pb = _c.Counter(d['terms']['b'] for d in devs if d['kind'] == 'mos' and d['type'] == 'p')
        nb = _c.Counter(d['terms']['b'] for d in devs if d['kind'] == 'mos' and d['type'] == 'n')
        sup, gnd = set(pb), set(nb)          # exam patch: every PMOS-bulk net is a supply, every NMOS-bulk net a ground (plan 2.1-1)
        self.sup = _c.defaultdict(set); self.gnd = _c.defaultdict(set)
        for prefix, cname, nm in instance_tree(cells, top):
            for ln, gn in nm.items():
                if gn in sup: self.sup[cname].add(ln)
                if gn in gnd: self.gnd[cname].add(ln)
        self._pm = {}

    def _elems(self, cname, members):
        es = self.cells[cname]['elems']
        return [e for e in es if members is None or e['name'] in members]

    def _rail(self, cname, n):
        return n in self.sup[cname] or n in self.gnd[cname]

    def edges(self, cname, members=None):
        import collections as _c
        es = self._elems(cname, members)
        sup, gnd = self.sup[cname], self.gnd[cname]
        rail = lambda n: n in sup or n in gnd
        at = _c.defaultdict(list)
        for e in es:
            if e['kind'] == 'mos':
                for t in ('d', 's'):
                    at[e['terms'][t]].append((e, t))
            elif e['kind'] in ('res', 'cap', 'ind'):
                for t in ('p', 'n'):
                    at[e['terms'][t]].append((e, t))
        def own(e):
            return gnd if e['type'] == 'n' else sup
        def other(e):
            return sup if e['type'] == 'n' else gnd
        def dist(x, e):
            seen = {x: 0}; q = [x]
            while q:
                y = q.pop(0)
                if y in own(e):
                    return seen[y]
                for f, t in at[y]:
                    if f['kind'] == 'mos' and f['type'] == e['type']:
                        o = f['terms']['s' if t == 'd' else 'd']
                        if o not in seen:
                            seen[o] = seen[y] + 1; q.append(o)
            return 99
        def sd(e):
            a, b = e['terms']['s'], e['terms']['d']
            if a in own(e): return a, b
            if b in own(e): return b, a
            if b in other(e): return a, b
            if a in other(e): return b, a
            return (b, a) if dist(b, e) < dist(a, e) else (a, b)
        def loaded(m, x):
            for f, t in at[x]:
                if f is m:
                    continue
                if f['kind'] == 'mos':
                    o = f['terms']['s' if t == 'd' else 'd']
                    if f['terms']['g'] == x:
                        return True
                    if m['type'] == 'n' and (f['type'] == 'p' or o in sup):
                        return True
                    if m['type'] == 'p' and f['type'] == 'n':
                        return True
                elif f['kind'] == 'res':
                    o = f['terms']['n' if t == 'p' else 'p']
                    if (m['type'] == 'n' and o in sup) or (m['type'] == 'p' and o in gnd):
                        return True
            return False
        def cm_node(y):
            if rail(y):
                return False
            rs = set()
            for f, t in at[y]:
                if f['kind'] == 'res':
                    o = f['terms']['n' if t == 'p' else 'p']
                    if not rail(o):
                        rs.add(o)
                elif f['kind'] == 'cap':
                    if not rail(f['terms']['n' if t == 'p' else 'p']):
                        return False
                else:
                    return False
            return len(rs) >= 2
        E = []
        for e in es:
            if e['kind'] == 'mos':
                g = e['terms']['g']
                s, d = sd(e)
                if g in (e['terms']['d'], e['terms']['s']):
                    continue
                part = [f for f, t in at[e['terms']['d']] if f is not e and f['kind'] == 'mos' and f['type'] != e['type']
                        and {f['terms']['d'], f['terms']['s']} == {e['terms']['d'], e['terms']['s']}]
                if part and not rail(e['terms']['d']) and not rail(e['terms']['s']):
                    off = (g in own(e)) and all(f['terms']['g'] in own(f) for f in part)
                    if not off:
                        E.append((e['terms']['d'], e['terms']['s'], 0)); E.append((e['terms']['s'], e['terms']['d'], 0))
                    continue
                if rail(g):
                    continue
                if rail(d):
                    if not rail(s):
                        E.append((g, s, 0))           # follower / active inductor
                    continue
                if loaded(e, d):
                    E.append((g, d, 1))
                    if not rail(s):
                        E.append((s, d, 0))           # stacked: source follows into drain
            elif e['kind'] in ('res', 'cap', 'ind'):
                a, b = e['terms']['p'], e['terms']['n']
                if rail(a) or rail(b) or cm_node(a) or cm_node(b):
                    continue
                E.append((a, b, 0)); E.append((b, a, 0))
            elif e['kind'] == 'inst':
                for (p, q), par in self.port_map(e['cell']).items():
                    E.append((e['pins'][p], e['pins'][q], par))
        return E

    def reach(self, cname, starts, members=None):
        """multi-source BFS; starts: {local net: parity}. Returns {net: parity}"""
        import collections as _c
        adj = _c.defaultdict(list)
        for a, b, p in self.edges(cname, members):
            adj[a].append((b, p))
        res = dict(starts)
        frontier = list(starts)
        while frontier:
            nxt = []
            for x in frontier:
                for y, p in adj[x]:
                    if y in res or self._rail(cname, y):
                        continue
                    res[y] = res[x] ^ p
                    nxt.append(y)
            frontier = nxt
        return res

    def port_map(self, cname):
        if cname in self._pm:
            return self._pm[cname]
        self._pm[cname] = {}
        ports = [p for p in self.cells[cname]['ports'] if not self._rail(cname, p)]
        m = {}
        for p in ports:
            r = self.reach(cname, {p: 0})
            for q in ports:
                if q != p and q in r:
                    m[(p, q)] = r[q]
        self._pm[cname] = m
        return m

    def outputs(self, cname, ins, outs, members=None):
        """per-output polarity of a drawn block (plan §4.1-13). ins: main input nets in drawn order (P first);
        outs: output nets in drawn order. Two main inputs and an even number of outputs = differential: output k is
        compared with the input on its own side (k even -> ins[0], k odd -> ins[1]) under complementary drive.
        Otherwise every output is compared with ins[0]. Returns {out: 'inv' | 'non' | None (not reached)}."""
        res = {}
        if len(ins) >= 2 and len(outs) % 2 == 0:
            r = self.reach(cname, {ins[0]: 0, ins[1]: 1}, members)
            for k, o in enumerate(outs):
                if o not in r:
                    res[o] = None
                else:
                    res[o] = 'inv' if r[o] != (k % 2) else 'non'
        else:
            r = self.reach(cname, {ins[0]: 0}, members)
            for o in outs:
                res[o] = None if o not in r else ('inv' if r[o] else 'non')
        return res
