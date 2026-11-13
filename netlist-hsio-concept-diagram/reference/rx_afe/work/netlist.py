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
