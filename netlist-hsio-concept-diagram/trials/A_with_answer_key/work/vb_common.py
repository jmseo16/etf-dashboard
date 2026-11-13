import json, re
from geom import *
from util import compress, expand

NL = json.load(open('netlist.json'))['cells']
AN = json.load(open('analysis.json'))
LC = AN['local_classes']
VISIBLE = {'data', 'clock', 'both', 'important'}

def dev(cell, name):
    return next(d for d in NL[cell]['devices'] if d['name'] == name)
def ncls(cell, net):
    c = set(LC[cell].get(net, []))
    if 'important' in c: return 'bus'
    if c & {'data', 'both'}: return 'data'
    if 'clock' in c: return 'clock'
    return 'hidden'
def wl(cell, names):
    ds = [dev(cell, n) for n in names]
    if ds[0]['type'] in 'RC':
        return '/'.join(d['value'] for d in ds)
    W = [d['params'].get('W', '?') for d in ds]; Ls = sorted({d['params'].get('L', '?') for d in ds})
    ms = [d['params'].get('m', d['params'].get('M', '1')) for d in ds]
    if len(W) == 1:
        s = '%s/%s' % (W[0], Ls[0])
    else:
        unit = re.sub(r'[\d.]+', '', W[0])
        if all(re.sub(r'[\d.]+', '', w) == unit for w in W):
            s = 'W=%s%s L=%s' % (','.join(re.sub(r'[^\d.]', '', w) for w in W), unit, ','.join(Ls))
        else:
            s = 'W=%s L=%s' % (','.join(W), ','.join(Ls))
    if any(m != '1' for m in ms): s += ' m=' + ','.join(ms)
    return s
def mname(names):
    c = compress(names)
    return c[0] if len(c) == 1 else '∥'.join(names) if len(names) <= 2 else names[0] + '…(×%d)' % len(names)

def wcls(cell, net):
    k = ncls(cell, net)
    return {'bus': 'bus', 'clock': 'clock', 'data': 'data'}.get(k, 'internal')

def finalize(v, scope=None):
    """fill the omitted list with every scope net that is neither visible nor shown as tag/rail."""
    cell = v.d['cell']
    devs = NL[cell]['devices']
    if scope is None: scope = [d['name'] for d in devs]
    v.d['scope'] = scope
    tagged = {t['net'] for t in v.d['tags']} | {r['net'] for r in v.d['rails']}
    have = {o['item'] for o in v.d['omitted']}
    nets = set()
    for d in devs:
        if d['name'] not in scope: continue
        if d['type'] == 'M': nets |= {d['D'], d['G'], d['S']}
        elif d['type'] in 'RCL': nets |= {d['A'], d['B']}
        else: nets |= set(d['pins'].values())
    for n in sorted(nets):
        c = set(LC[cell].get(n, []))
        if c & VISIBLE or n in tagged or n in have: continue
        if c <= {'internal'} and v.d['level'] == 'unit': continue      # drawn as plain internal wire
        why = {'power': '전원', 'bias': '바이어스', 'general': '일반 제어', 'internal': '내부 노드(블록 안)'}
        v.omit(n, 'net', '/'.join(why.get(x, x) for x in sorted(c)))
    return v.d

def mos_pm(names, term_map):
    """pinmap for a merged MOS symbol: pin -> slices (one per device)."""
    return {p: [[[n, t]] for n in names] for p, t in term_map.items()}
