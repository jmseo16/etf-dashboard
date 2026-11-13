"""HSPICE / Virtuoso-style netlist parser -> JSON (subckts, devices, instances)."""
import json, re, sys

def parse(path):
    lines = []
    for raw in open(path):
        s = raw.rstrip('\n')
        if not s.strip() or s.lstrip().startswith('*'):
            continue
        if s.lstrip().startswith('+'):
            lines[-1] += ' ' + s.lstrip()[1:].strip()
        else:
            lines.append(s.strip())
    cells, cur, order = {}, None, []
    for ln in lines:
        tok = ln.split()
        kw = tok[0].upper()
        if kw == '.SUBCKT':
            cur = {'name': tok[1], 'ports': tok[2:], 'devices': []}
            cells[tok[1]] = cur; order.append(tok[1])
            continue
        if kw == '.ENDS':
            cur = None; continue
        if kw.startswith('.') or cur is None:
            continue
        name = tok[0]; t = name[0].upper()
        params = {k: v for k, v in (x.split('=', 1) for x in tok[1:] if '=' in x)}
        pos = [x for x in tok[1:] if '=' not in x]
        if t == 'M':
            d, g, s, b, model = pos[:5]
            cur['devices'].append({'name': name, 'type': 'M', 'model': model,
                'pol': 'p' if model.upper().startswith('P') else 'n',
                'D': d, 'G': g, 'S': s, 'B': b, 'params': params})
        elif t in 'RCL':
            cur['devices'].append({'name': name, 'type': t, 'A': pos[0], 'B': pos[1],
                                   'value': pos[2] if len(pos) > 2 else params.get('r', '')})
        elif t == 'X':
            cur['devices'].append({'name': name, 'type': 'X', 'cell': pos[-1], 'nodes': pos[:-1]})
    # resolve instance pin maps and check counts
    errors = []
    for c in cells.values():
        for d in c['devices']:
            if d['type'] == 'X':
                sub = cells.get(d['cell'])
                if sub is None:
                    d['blackbox'] = True; errors.append('undefined cell %s' % d['cell']); continue
                if len(sub['ports']) != len(d['nodes']):
                    errors.append('port count mismatch %s/%s' % (c['name'], d['name']))
                d['pins'] = dict(zip(sub['ports'], d['nodes']))
    # top = cell not instantiated by others
    used = {d['cell'] for c in cells.values() for d in c['devices'] if d['type'] == 'X'}
    tops = [n for n in order if n not in used]
    return {'cells': cells, 'order': order, 'tops': tops, 'errors': errors}

if __name__ == '__main__':
    nl = parse(sys.argv[1])
    json.dump(nl, open(sys.argv[2], 'w'), indent=1)
    print('cells', len(nl['cells']), 'tops', nl['tops'], 'errors', nl['errors'])
