"""Plan §3: device roles, signal tracing, signal classes, important-control detection,
block roles and confidence.  Judgement is structural; names are only used as hints
for the confidence column (plan §1-1, §3.5)."""
import json, re, sys
from collections import defaultdict, Counter

NL = json.load(open(sys.argv[1]))
CELLS, TOP = NL['cells'], NL['tops'][0]

# ---------------------------------------------------------------- flatten
FLAT = []          # flat devices
INST = []          # flat instances (path, cell)
def flatten(cell, path, netmap):
    c = CELLS[cell]
    def fn(n):
        return netmap.get(n, (path + '/' + n) if path else n)
    for d in c['devices']:
        full = (path + '/' if path else '') + d['name']
        if d['type'] == 'X':
            INST.append({'path': full, 'cell': d['cell'], 'parent': cell, 'name': d['name'],
                         'pins': {p: fn(n) for p, n in d['pins'].items()}})
            flatten(d['cell'], full, {p: fn(n) for p, n in d['pins'].items()})
        else:
            fd = dict(d); fd['path'] = full; fd['cell'] = cell; fd['local'] = d['name']
            fd['inst'] = path
            for t in ('D', 'G', 'S', 'B', 'A'):
                if t in d: fd[t] = fn(d[t])
            if d['type'] in 'RCL': fd['B'] = fn(d['B'])
            FLAT.append(fd)
flatten(TOP, '', {p: p for p in CELLS[TOP]['ports']})

def terms(d):
    return ['D', 'G', 'S'] if d['type'] == 'M' else ['A', 'B']
NETDEV = defaultdict(list)
for d in FLAT:
    for t in terms(d):
        NETDEV[d[t]].append((d, t))

# ---------------------------------------------------------------- power (bulk majority)
pb = Counter(d['B'] for d in FLAT if d['type'] == 'M' and d['pol'] == 'p')
nb = Counter(d['B'] for d in FLAT if d['type'] == 'M' and d['pol'] == 'n')
VDD, VSS = pb.most_common(1)[0][0], nb.most_common(1)[0][0]
POWER = {VDD, VSS}

# ---------------------------------------------------------------- bias & common-mode nets (structure)
BIAS, WHY = set(), {}
for d in FLAT:
    if d['type'] == 'M' and d['G'] == d['D'] and d['G'] not in POWER:
        BIAS.add(d['G']); WHY[d['G']] = 'diode node (%s)' % d['path']
for n, lst in NETDEV.items():
    if n in POWER: continue
    rs = [(d, t) for d, t in lst if d['type'] == 'R']
    others = [(d, t) for d, t in lst if d['type'] != 'R' and not (d['type'] == 'C')]
    far = {d['B'] if t == 'A' else d['A'] for d, t in rs}
    if len(rs) >= 2 and not others and len(far - POWER) >= 2:
        BIAS.add(n); WHY[n] = 'common-mode node of termination R'
    if len(rs) == 1 and all(t == 'G' for d, t in others) and others:
        r = rs[0][0]; f = r['B'] if rs[0][1] == 'A' else r['A']
        if f in POWER:
            BIAS.add(n); WHY[n] = 'gate tied through R to supply (active-inductor gate)'

TOP_PORTS = CELLS[TOP]['ports']
def gate_only(n):
    return NETDEV[n] and all(d['type'] == 'M' and t == 'G' for d, t in NETDEV[n])
# bias ports: top ports that reach only bias nets / diode
CONTROL = {p for p in TOP_PORTS if p not in POWER and p not in BIAS and gate_only(p)}

# ---------------------------------------------------------------- device roles (§3.1)
def common_source_node(n, exclude, pol=None, k=1):
    return n not in POWER and sum(1 for d, t in NETDEV[n] if d['type'] == 'M' and t == 'S' and d is not exclude
               and d['G'] not in POWER and (pol is None or d['pol'] == pol)) >= k
def gate_class(n):
    if n in POWER: return 'power'
    if n in BIAS: return 'bias'
    if n in CONTROL: return 'control'
    return 'signal?'
MOS = [d for d in FLAT if d['type'] == 'M']
BYINST = defaultdict(list)
for d in MOS: BYINST[d['inst']].append(d)
def static_cmos(devs):
    """every gate net drives exactly one P and one N; P devices touch only VDD/out/internal-P,
    N devices form the pull-down; no bias/power gates (INV, NAND, NOR)."""
    if not devs or len(devs) != len([x for x in FLAT if x['inst'] == devs[0]['inst']]): return False
    g = defaultdict(Counter)
    for d in devs:
        if d['G'] in POWER or d['G'] in BIAS or d['G'] in CONTROL: return False
        g[d['G']][d['pol']] += 1
    return all(c['p'] == 1 and c['n'] == 1 for c in g.values())
LOGIC_INST = {i for i, ds in BYINST.items() if static_cmos(ds)}
for d in MOS:
    g, dr, s = d['G'], d['D'], d['S']
    gc = gate_class(g); d['gclass'] = gc
    partners = [e for e in BYINST[d['inst']] if e is not d]
    if d['inst'] in LOGIC_INST:
        role = 'logic'
    elif g in POWER and s in POWER and dr not in POWER and g == s:
        role = 'esd'
    elif any(e['pol'] != d['pol'] and {e['D'], e['S']} == {dr, s} and dr not in POWER and s not in POWER
             for e in partners):
        role = 'tgate'
    elif g == dr:
        role = 'diode'
    elif any(e['pol'] == d['pol'] and e['G'] == dr and e['D'] == g for e in partners):
        role = 'xc'
    elif gc == 'control':
        role = 'switch'
    elif s in POWER and common_source_node(dr, d, d['pol']):
        role = 'tail' if gc == 'bias' else 'tail_clk'
    elif gc == 'signal?' and common_source_node(dr, d, d['pol'], 2) and \
            any(e['D'] == s and e['S'] in POWER for e in partners):
        role = 'steer'          # drain = common source of a pair, source = tail node
    elif (s in POWER or dr in POWER) and gc in ('power', 'bias'):
        role = 'load'
    elif s in POWER and gc == 'signal?':
        role = 'reset'          # refined below: only if gate also clocks a tail in this cell
    elif gc == 'bias':
        role = 'cascode'
    else:
        role = 'input'
    d['role'] = role
# reset/precharge only when its gate drives a clocked tail in the same cell
for d in MOS:
    if d['role'] == 'reset' and not any(e['inst'] == d['inst'] and e['G'] == d['G'] and
                                        e['role'] in ('tail_clk', 'steer') for e in MOS):
        d['role'] = 'input' if d['S'] not in POWER else 'load?'
    if d['role'] == 'steer' and d['gclass'] != 'signal?':
        d['role'] = 'cascode'

# ---------------------------------------------------------------- signal tracing (§3.2)
STOP = POWER | BIAS | CONTROL
def trace(seeds):
    S, frontier, via = set(seeds), list(seeds), {}
    def add(n, why):
        if n in STOP or n in S: return
        S.add(n); frontier.append(n); via[n] = why
    while frontier:
        n = frontier.pop()
        for d, t in NETDEV[n]:
            if d['type'] == 'M':
                r = d['role']
                if t == 'G' and r in ('input', 'xc', 'logic', 'load?'):
                    add(d['D'], d['path'] + ' g->d')
                    if d['D'] in POWER: add(d['S'], d['path'] + ' follower g->s')
                if t == 'S' and r in ('input', 'xc', 'logic', 'cascode', 'load?') and n not in POWER:
                    add(d['D'], d['path'] + ' s->d')
                if r == 'tgate' and t in ('D', 'S'):
                    add(d['S'] if t == 'D' else d['D'], d['path'] + ' tgate')
            elif d['type'] in 'RCL':
                o = d['B'] if t == 'A' else d['A']
                add(o, d['path'] + ' series %s' % d['type'])
    return S, via

def drives_gate(n):
    return any(d['type'] == 'M' and t == 'G' for d, t in NETDEV[n])
def driven(n):
    return any(d['type'] == 'M' and t in ('D', 'S') and d['role'] not in ('esd',) and d['role'] != 'tgate'
               for d, t in NETDEV[n])
cand_in = [p for p in TOP_PORTS if p not in STOP and not driven(p)]
cand_out = [p for p in TOP_PORTS if p not in STOP and driven(p)]
reach, inputs = {}, {}
for p in cand_in:
    S, via = trace([p])
    reach[p] = S
    clocky = sorted({d['path'] for n in S for d, t in NETDEV[n]
                     if t == 'G' and d['role'] in ('tail_clk', 'steer', 'reset')})
    has_term = any(d['type'] == 'R' and (d['A'] in BIAS or d['B'] in BIAS) for d, t in NETDEV[p]) or \
        any(d['type'] == 'R' and (d['A'] in BIAS or d['B'] in BIAS) for n in S for d, t in NETDEV[n]
            if n in [p] or (n.endswith(p.split('/')[-1])))
    inputs[p] = {'kind': 'clock' if clocky else 'data', 'clock_evidence': clocky[:4],
                 'reached_gates': len([1 for n in S for d, t in NETDEV[n] if t == 'G'])}
DATA_IN = [p for p in cand_in if inputs[p]['kind'] == 'data']
CLK_IN = [p for p in cand_in if inputs[p]['kind'] == 'clock']
DATA, via_d = trace(DATA_IN)
CLOCK, via_c = trace(CLK_IN)
BOTH = sorted(DATA & CLOCK)

# ---------------------------------------------------------------- important vs general control (§3.3)
def branch_pairs(sw):
    seen, todo, pairs = set(), [sw['D'], sw['S']], []
    while todo:
        n = todo.pop()
        if n in seen or n in POWER or n in DATA or n in CLOCK: continue
        seen.add(n)
        for d, t in NETDEV[n]:
            if d['type'] == 'M' and t == 'S' and (d['G'] in DATA or d['G'] in CLOCK):
                pairs.append(d)
            elif d['type'] == 'M' and t in ('D', 'S') and d['role'] in ('switch', 'tail', 'load', 'cascode'):
                todo.append(d['S'] if t == 'D' else d['D'])
            elif d['type'] in 'RC':
                todo.append(d['B'] if t == 'A' else d['A'])
    return pairs
CTRL_INFO = {}
for p in sorted(CONTROL):
    sws = [d for d in MOS if d['G'] == p and d['role'] == 'switch']
    verdict, ev = 'general', []
    for sw in sws:
        for bd in branch_pairs(sw):
            node = bd['D']
            others = [e for e in MOS if e['D'] == node and e['role'] == 'input' and
                      e['G'] != bd['G'] and e['S'] != bd['S']]
            unswitched = [e for e in others if not any(bd2 is e for s2 in MOS if s2['role'] == 'switch'
                                                       for bd2 in branch_pairs(s2))] if others else []
            mains = {e['G'] for e in MOS if e['D'] == node and e['role'] == 'input' and
                     not any(e is x for s2 in sws for x in branch_pairs(s2))}
            if node in DATA | CLOCK and mains and bd['G'] not in mains:
                verdict = 'important'
                ev.append('%s -> %s: gate %s (≠ main %s) summed at %s' % (sw['path'], bd['path'], bd['G'],
                                                                          '/'.join(sorted(mains)), node))
            else:
                ev.append('%s -> %s: same path as main input (gate %s) at %s' % (sw['path'], bd['path'], bd['G'], node)
                          if bd else sw['path'])
        if not branch_pairs(sw):
            ev.append('%s: switch between %s and %s (no separate signal branch)' % (sw['path'], sw['D'], sw['S']))
    CTRL_INFO[p] = {'verdict': verdict, 'switches': sorted({s['path'] for s in sws}), 'evidence': ev[:3]}
    CTRL_INFO[p]['verdict'] = 'important' if any('≠ main' in e for e in ev) else 'general'
IMPORTANT = sorted(p for p, v in CTRL_INFO.items() if v['verdict'] == 'important')
GENERAL = sorted(p for p, v in CTRL_INFO.items() if v['verdict'] == 'general')

def compress(names):
    """W1_0..W4_3 -> W<1:4>_<0:3>; G0..G3 -> G<0:3> (only for full rectangular sets)."""
    groups = defaultdict(list)
    for n in names:
        key = re.sub(r'\d+', '#', n); nums = tuple(int(x) for x in re.findall(r'\d+', n))
        groups[key].append(nums)
    out = []
    for key, nums in groups.items():
        k = len(nums[0]) if nums else 0
        if k == 0: out.append(key); continue
        ranges = [sorted({x[i] for x in nums}) for i in range(k)]
        full = 1
        for r in ranges: full *= len(r)
        ok = full == len(nums) and all(r == list(range(r[0], r[-1] + 1)) for r in ranges)
        if ok:
            s = key
            for r in ranges:
                s = s.replace('#', '<%d:%d>' % (r[0], r[-1]) if len(r) > 1 else str(r[0]), 1)
            out.append(s)
        else:
            out += [n for n in names if re.sub(r'\d+', '#', n) == key]
    return out

# ---------------------------------------------------------------- per-cell local classes
def local_classes():
    res = defaultdict(lambda: defaultdict(set))
    insts = [{'path': '', 'cell': TOP, 'pins': {p: p for p in TOP_PORTS}}] + INST
    for it in insts:
        c = CELLS[it['cell']]
        nets = set(c['ports'])
        for d in c['devices']:
            if d['type'] == 'M': nets |= {d['D'], d['G'], d['S']}
            elif d['type'] in 'RCL': nets |= {d['A'], d['B']}
            else: nets |= set(d['nodes'])
        for n in nets:
            f = it['pins'].get(n, (it['path'] + '/' + n) if it['path'] else n)
            res[it['cell']][n].add(netclass(f))
    return {c: {n: sorted(v) for n, v in m.items()} for c, m in res.items()}
def netclass(f):
    if f in POWER: return 'power'
    if f in DATA and f in CLOCK: return 'both'
    if f in DATA: return 'data'
    if f in CLOCK: return 'clock'
    if f in IMPORTANT: return 'important'
    if f in GENERAL: return 'general'
    if f in BIAS: return 'bias'
    return 'internal'
LOCAL = local_classes()

# ---------------------------------------------------------------- block roles (§3.4)
def cell_features(cn):
    c = CELLS[cn]
    ms = [d for d in FLAT if d['cell'] == cn]
    first = ms[0]['inst'] if ms else None
    ms = [d for d in ms if d['inst'] == first]
    roles = Counter(d['role'] for d in ms if d['type'] == 'M')
    subs = [d['cell'] for d in c['devices'] if d['type'] == 'X']
    hs = any(set(v) & {'data', 'clock', 'both'} for v in LOCAL[cn].values())
    pairs = defaultdict(list)
    for d in ms:
        if d['type'] == 'M' and d['role'] == 'input': pairs[d['S']].append(d)
    dpairs = [v for v in pairs.values() if len(v) == 2]
    degen = any(d['type'] in 'RC' and {d['A'], d['B']} and all(
        any(e['S'] == n and e['role'] == 'input' for e in ms if e['type'] == 'M') for n in (d['A'], d['B']))
        for d in ms)
    outs = Counter(e['D'] for v in dpairs for e in v)
    shared = max(outs.values()) if outs else 0
    gates_by_out = defaultdict(set)
    for v in dpairs:
        for e in v: gates_by_out[e['D']].add(e['G'])
    return dict(roles=roles, subs=subs, hs=hs, npairs=len(dpairs), degen=degen, shared=shared,
                diff_gates=max((len(g) for g in gates_by_out.values()), default=0), ms=ms)

def block_role(cn):
    f = cell_features(cn); r = f['roles']; subs = Counter(f['subs'])
    if not f['hs']:
        if r['diode'] and not f['subs']: return 'bias', 'diode/mirror only, no high-speed net', 'BIAS'
        if r['switch'] and (r['tail'] or any(d['type'] == 'M' and d['role'] == 'load' for d in f['ms'])):
            return 'idac', 'switch + current source repeated', 'DAC'
        return 'omit', 'no high-speed net', ''
    if r['tail_clk'] and r['xc'] >= 4 and r['reset'] >= 2:
        return 'strongarm', 'clocked tail + input pair + NMOS/PMOS cross-coupled + reset PMOS', 'STRONGARM'
    if r['xc'] >= 2 and r['steer'] >= 2:
        return 'cml_latch', 'input pair + cross-coupled pair with clock steering', 'LATCH'
    if f['degen'] and f['npairs'] == 0 or (f['degen']):
        return 'ctle', 'differential pair with source degeneration (R∥C between sources)', 'CTLE'
    if f['shared'] >= 4 and f['diff_gates'] == 1:
        return 'vga', 'several pairs share outputs, extra pairs switched, same input', 'VGA'
    if f['shared'] >= 4 and f['diff_gates'] > 1:
        return 'summer', 'several pairs with different inputs summed at shared outputs', 'SUM'
    if r['logic'] == 2 and len(f['ms']) == 2: return 'inv', 'CMOS inverter', 'INV'
    if r['logic'] >= 2 and len(f['ms']) == 4: return 'nand2', 'CMOS NAND2 (not in dictionary)', 'NAND'
    if subs and set(subs) == {'CML_LATCH'} and len(f['subs']) == 2: return 'dff', 'two latches in series', 'DFF'
    if subs and set(subs) == {'NAND2'}: return 'sr_latch', 'cross-coupled NAND pair (not in dictionary)', 'SR'
    return 'composite', 'hierarchical: ' + ', '.join(sorted(set(f['subs']))), 'BOX'

ROLES = {}
for cn in CELLS:
    role, why, sym = block_role(cn)
    hint = {'ctle': 'CTLE', 'vga': 'VGA', 'summer': 'SUM', 'strongarm': 'STRONGARM', 'cml_latch': 'LATCH',
            'dff': 'DFF', 'bias': 'BIAS', 'idac': 'DAC', 'inv': 'INV', 'nand2': 'NAND', 'sr_latch': 'SR'}.get(role)
    conf = 'high' if hint and hint in cn.upper() else 'low'
    if role == 'composite': conf = 'low'
    ROLES[cn] = {'role': role, 'why': why, 'confidence': conf}

out = {'top': TOP, 'power': {'VDD': VDD, 'VSS': VSS},
       'data_inputs': DATA_IN, 'clock_inputs': CLK_IN, 'inputs_evidence': inputs,
       'outputs': [p for p in cand_out if p in DATA or p in CLOCK],
       'unclassified_ports': [p for p in TOP_PORTS if p not in STOP and p not in DATA and p not in CLOCK],
       'bias': sorted(n for n in BIAS if '/' not in n), 'bias_all': sorted(BIAS), 'bias_why': WHY,
       'control': CTRL_INFO, 'important': IMPORTANT, 'general': GENERAL,
       'important_bus': compress(IMPORTANT), 'general_compressed': compress(GENERAL),
       'data_nets': sorted(DATA), 'clock_nets': sorted(CLOCK), 'both': BOTH,
       'trace_via': {**{k: 'data: ' + v for k, v in via_d.items()}, **{k: 'clock: ' + v for k, v in via_c.items()}},
       'local_classes': LOCAL, 'block_roles': ROLES,
       'device_roles': {d['path']: {'role': d['role'], 'cell': d['cell'], 'gclass': d.get('gclass')}
                        for d in MOS},
       'instances': INST, 'flat': [{k: v for k, v in d.items()} for d in FLAT]}
json.dump(out, open(sys.argv[2], 'w'), indent=1, default=list)
print('VDD/VSS', VDD, VSS)
print('data in', DATA_IN, 'clock in', CLK_IN)
print('outputs', out['outputs'], 'unclassified', out['unclassified_ports'])
print('important', compress(IMPORTANT), 'general', compress(GENERAL))
print('bias', out['bias'])
print('both', BOTH)
print('top data nets', [n for n in sorted(DATA) if '/' not in n])
print('top clock nets', [n for n in sorted(CLOCK) if '/' not in n])
for cn, r in ROLES.items(): print('  %-22s %-10s %-5s %s' % (cn, r['role'], r['confidence'], r['why']))
print(Counter(d['role'] for d in MOS))
