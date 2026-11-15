"""Step 1 (plan section 3): structural analysis.
device roles, signal tracing (data / clock), signal classes, important-control detection,
block roles, confidence, questions. Writes analysis.json, annotations.json, classification.md
Usage: python3 analyze.py <netlist> <top> <outdir> [hs_input ...]
"""
import sys, json, re, collections
from netlist import parse, flatten, instance_tree, cell_nets, num

NET_SEP = '/'


class Flat:
    def __init__(self, cells, top):
        self.cells = cells
        self.top = top
        self.devs = flatten(cells, top)
        self.by_net = collections.defaultdict(list)   # net -> [(dev, term)]
        for d in self.devs:
            for t, n in d['terms'].items():
                if d['kind'] == 'mos' and t == 'b':
                    continue
                self.by_net[n].append((d, t))
        self.find_rails()
        self.eff = {}
        for d in self.devs:
            if d['kind'] == 'mos':
                self.eff[d['path']] = self.eff_sd(d)

    # ---------- rails: structural (most common bulk of P / N devices) ----------
    def find_rails(self):
        pb = collections.Counter(d['terms']['b'] for d in self.devs if d['kind'] == 'mos' and d['type'] == 'p')
        nb = collections.Counter(d['terms']['b'] for d in self.devs if d['kind'] == 'mos' and d['type'] == 'n')
        self.supply = pb.most_common(1)[0][0]
        self.ground = nb.most_common(1)[0][0]
        self.rails = {self.supply, self.ground}

    def is_rail(self, n):
        return n in self.rails

    def dist_to_rail(self, start, mtype):
        rail = self.ground if mtype == 'n' else self.supply
        seen = {start: 0}
        q = collections.deque([start])
        while q:
            x = q.popleft()
            if x == rail:
                return seen[x]
            for d, t in self.by_net[x]:
                if d['kind'] == 'mos' and d['type'] == mtype and t in 'ds':
                    o = d['terms']['s' if t == 'd' else 'd']
                    if o not in seen:
                        seen[o] = seen[x] + 1
                        q.append(o)
        return 99

    def eff_sd(self, d):
        """effective (source, drain) by structure: source = terminal nearer own rail."""
        a, b = d['terms']['s'], d['terms']['d']
        own = self.ground if d['type'] == 'n' else self.supply
        other = self.supply if d['type'] == 'n' else self.ground
        if a == own: return a, b
        if b == own: return b, a
        if b == other: return a, b
        if a == other: return b, a
        da, db = self.dist_to_rail(a, d['type']), self.dist_to_rail(b, d['type'])
        if db < da:
            return b, a
        return a, b

    # ---------- structural predicates ----------
    def loaded(self, m, x):
        """node x has a load relative to device m (pull-up for NMOS, pull-down for PMOS)"""
        for e, t in self.by_net[x]:
            if e is m:
                continue
            if e['kind'] == 'mos':
                if t not in 'ds':
                    continue
                o = e['terms']['s' if t == 'd' else 'd']
                if e['terms']['g'] == x:   # diode
                    return True
                if m['type'] == 'n':
                    if e['type'] == 'p':
                        return True
                    if o == self.supply:
                        return True  # active inductor / follower load
                else:
                    if e['type'] == 'n':
                        return True
            elif e['kind'] == 'res':
                o = e['terms']['n' if t == 'p' else 'p']
                if (m['type'] == 'n' and o == self.supply) or (m['type'] == 'p' and o == self.ground):
                    return True
        return False

    def pull_gates(self, x, mtype):
        rail = self.supply if mtype == 'p' else self.ground
        gates = set(); seen = {x}; q = [x]
        while q:
            y = q.pop()
            if y == rail:
                continue
            for d, t in self.by_net[y]:
                if d['kind'] == 'mos' and d['type'] == mtype and t in 'ds':
                    o = d['terms']['s' if t == 'd' else 'd']
                    gates.add(d['terms']['g'])
                    if o not in seen:
                        seen.add(o); q.append(o)
        return gates

    def static_cmos(self, x):
        pu = self.pull_gates(x, 'p'); pd = self.pull_gates(x, 'n')
        return bool(pu) and pu == pd

    def cm_node(self, y):
        """common-mode node: >=2 resistors from distinct non-rail nets, everything else is R/C to a rail."""
        if self.is_rail(y):
            return False
        rs = set(); other_ok = True
        for e, t in self.by_net[y]:
            if e['kind'] == 'res':
                o = e['terms']['n' if t == 'p' else 'p']
                if self.is_rail(o):
                    continue
                rs.add(o)
            elif e['kind'] == 'cap':
                o = e['terms']['n' if t == 'p' else 'p']
                if not self.is_rail(o):
                    other_ok = False
            else:
                other_ok = False
        return len(rs) >= 2 and other_ok

    def common_source_node(self, x, exclude=None):
        """x is the effective source of >=2 other MOS"""
        cnt = 0
        for e, t in self.by_net[x]:
            if e is exclude or e['kind'] != 'mos' or t not in 'ds':
                continue
            s, dd = self.eff[e['path']]
            if s == x:
                cnt += 1
        return cnt >= 2

    def pair_node(self, x, exclude=None):
        """x is the common source of >=2 MOS whose drains are loaded (a differential pair)"""
        cnt = 0
        for e, t in self.by_net[x]:
            if e is exclude or e['kind'] != 'mos' or t not in 'ds':
                continue
            s, dd = self.eff[e['path']]
            if s == x and not self.is_rail(dd) and self.loaded(e, dd):
                cnt += 1
        return cnt >= 2

    def tg_partner(self, d):
        if d['kind'] != 'mos':
            return None
        a, b = d['terms']['d'], d['terms']['s']
        if self.is_rail(a) or self.is_rail(b):
            return None
        for e, t in self.by_net[a]:
            if e is d or e['kind'] != 'mos' or e['type'] == d['type'] or t not in 'ds':
                continue
            if {e['terms']['d'], e['terms']['s']} == {a, b}:
                return e
        return None

    # ---------- tracing ----------
    def trace(self, starts, cls):
        reached = {}
        events = []
        q = collections.deque()
        for s in starts:
            reached[s] = {'depth': 0, 'via': 'start'}
            q.append(s)
        edges = self.trace_edges = []
        def add(n, frm, via):
            if self.is_rail(n):
                return
            edges.append((frm, n))
            if n in reached:
                return
            reached[n] = {'depth': reached[frm]['depth'] + 1, 'via': via}
            q.append(n)
        while q:
            x = q.popleft()
            for d, t in self.by_net[x]:
                if d['kind'] == 'mos':
                    s, dr = self.eff[d['path']]
                    g = d['terms']['g']
                    if t == 'g':
                        if g in (d['terms']['d'], d['terms']['s']):
                            events.append((d['path'], 'diode: stop')); continue
                        if self.is_rail(dr):
                            # source follower / active inductor: gate signal -> source
                            if not self.is_rail(s):
                                add(s, x, d['path'] + ' (follower g->s)')
                            continue
                        if not self.loaded(d, dr):
                            events.append((d['path'], 'gate %s: drain %s has no load (tail / steering / stacked switch): stop' % (x, dr)))
                            continue
                        if cls == 'clock' and self.is_rail(s) and not self.static_cmos(dr):
                            events.append((d['path'], 'gate %s: reset/precharge (rail source, dynamic node %s): stop' % (x, dr)))
                            continue
                        add(dr, x, d['path'] + ' (g->d)')
                    elif t in 'ds':
                        p = self.tg_partner(d)
                        if p is not None:
                            o = d['terms']['s' if t == 'd' else 'd']
                            add(o, x, d['path'] + ' (TG channel)')
                            continue
                        if x == s and not self.is_rail(s) and not self.is_rail(dr) and self.loaded(d, dr):
                            add(dr, x, d['path'] + ' (stacked s->d)')
                else:
                    o = d['terms']['n' if t == 'p' else 'p']
                    if self.is_rail(o):
                        continue
                    if self.cm_node(o):
                        events.append((d['path'], 'common-mode node %s: stop' % o)); continue
                    add(o, x, d['path'] + ' (series passive)')
        return reached, events

    def clock_pin_devices(self, nets):
        """devices whose gate is in nets and that act as clock pins of latches/samplers"""
        found = []
        for d in self.devs:
            if d['kind'] != 'mos' or d['terms']['g'] not in nets:
                continue
            s, dr = self.eff[d['path']]
            if self.is_rail(s) and self.pair_node(dr, d):
                found.append((d['path'], 'clocked tail'))
            elif self.is_rail(s) and not self.is_rail(dr) and self.loaded(d, dr) and not self.static_cmos(dr) and self.has_cross(dr):
                found.append((d['path'], 'reset/precharge'))
            elif not self.is_rail(s) and self.pair_node(dr, d):
                # steering: sibling sharing the source, different gate, steering into a different pair
                for e, t in self.by_net[s]:
                    if e is d or e['kind'] != 'mos' or t not in 'ds':
                        continue
                    es, edr = self.eff[e['path']]
                    if es == s and edr != dr and e['terms']['g'] != d['terms']['g'] and self.pair_node(edr, e):
                        found.append((d['path'], 'clock steering')); break
        return found

    def has_cross(self, x, depth=2):
        """node x is (or is one stacked device away from) a cross-coupled node"""
        frontier = {x}
        for _ in range(depth):
            nxt = set()
            for y in frontier:
                if self.is_cross_node(y):
                    return True
                for e, t in self.by_net[y]:
                    if e['kind'] == 'mos' and t in 'ds':
                        nxt.add(e['terms']['s' if t == 'd' else 'd'])
            frontier = nxt - self.rails
        return False

    def is_cross_node(self, y):
        for a, t in self.by_net[y]:
            if a['kind'] != 'mos' or t != 'd':
                continue
            for b, t2 in self.by_net[a['terms']['g']]:
                if b is not a and b['kind'] == 'mos' and t2 == 'd' and b['type'] == a['type'] and b['terms']['g'] == y:
                    return True
        return False



# ======================================================================================
def gate_users(F, n):
    return [d for d, t in F.by_net[n] if d['kind'] == 'mos' and t == 'g']


def classify(F, cells, top, hs_inputs):
    top_ports = cells[top]['ports']
    data_r, data_ev = F.trace(hs_inputs, 'data')
    data_edges = collections.defaultdict(set)
    for a, b in F.trace_edges:
        data_edges[a].add(b)

    def downstream(nets):
        seen = set(nets); q = list(nets)
        while q:
            x = q.pop()
            for y in data_edges[x]:
                if y not in seen:
                    seen.add(y); q.append(y)
        return seen

    def sharing_paths(drains):
        """bit paths (sibling instances of one cell) that receive the stage output (plan §2.5-5 K6)"""
        par = min(drains).rsplit('/', 1)[0] + '/' if '/' in min(drains) else ''
        insts = collections.defaultdict(set)
        for n in downstream(drains):
            if not n.startswith(par):
                continue
            rest = n[len(par):]
            if '/' in rest:
                insts[rest.split('/')[0]].add(n)
        bycell = collections.defaultdict(list)
        for i in insts:
            c = [cc for pre, cc, nm in instance_tree(cells, top) if pre == par + i + '/']
            if c:
                bycell[c[0]].append(i)
        return {c: sorted(v) for c, v in bycell.items() if len(v) >= 2}
    cand = [p for p in top_ports if p not in F.rails and p not in hs_inputs and p not in data_r]
    clock_inputs, clk_evidence = [], {}
    for p in cand:
        r, ev = F.trace([p], 'clock')
        pins = F.clock_pin_devices(set(r))
        if pins:
            clock_inputs.append(p)
            clk_evidence[p] = pins
    clk_r, clk_ev = F.trace(clock_inputs, 'clock')
    all_nets = set(F.by_net) | set(top_ports)
    netclass = {}
    for n in all_nets:
        cs = []
        if n in F.rails: cs.append('power')
        if n in data_r: cs.append('data')
        if n in clk_r: cs.append('clock')
        netclass[n] = cs
    # switches
    switch_info = {}
    for n in all_nets:
        if netclass[n]:
            continue
        users = gate_users(F, n)
        if not users:
            continue
        sw = []
        for d in users:
            s, dr = F.eff[d['path']]
            if d['terms']['g'] in (d['terms']['d'], d['terms']['s']):
                continue
            if F.is_rail(s) or F.is_rail(dr):
                continue
            sw.append(d)
        if sw and len(sw) == len(users):
            switch_info[n] = sw
    depth = {k: v['depth'] for k, v in data_r.items()}
    depth.update({k: v['depth'] for k, v in clk_r.items() if k not in depth})

    def srcs_at(x):
        return [e for e, t in F.by_net[x] if e['kind'] == 'mos' and t in 'ds' and F.eff[e['path']][0] == x]

    control_info = {}
    for n, sws in switch_info.items():
        kinds = []
        btypes = set()
        for d in sws:
            s, dr = F.eff[d['path']]
            # bundle type: series with current source -> I, series with cap -> C, else R
            series = [e for e, t in F.by_net[s] if e is not d and (e['kind'] != 'mos' or t in 'ds')]
            if any(e['kind'] == 'mos' and F.is_rail(F.eff[e['path']][0]) for e in series) and len(series) == 1:
                btypes.add('I')
            elif any(e['kind'] == 'cap' for e in series) and len(series) == 1:
                btypes.add('C')
            else:
                btypes.add('R')
            prs = [p for p in srcs_at(dr) if p is not d]
            if len(prs) >= 2 and all(p['terms']['g'] in data_r or p['terms']['g'] in clk_r for p in prs):
                gates = sorted({p['terms']['g'] for p in prs})
                drains = {F.eff[p['path']][1] for p in prs}
                others = []
                for x in drains:
                    for e, t in F.by_net[x]:
                        if e['kind'] == 'mos' and t in 'ds' and F.eff[e['path']][1] == x and e not in prs and e['type'] == prs[0]['type']:
                            if e['terms']['g'] in data_r or e['terms']['g'] in clk_r:
                                others.append(e)
                if not others:
                    kinds.append(('general', 'tail of the only pair at %s' % ','.join(sorted(drains))))
                    continue
                allg = {}
                for e in others + prs:
                    allg.setdefault(F.eff[e['path']][0], set()).add(e['terms']['g'])
                main_src = min(allg, key=lambda k: min(depth.get(g, 999) for g in allg[k]))
                main_g = allg[main_src]
                if set(gates) != main_g and F.eff[prs[0]['path']][0] != main_src:
                    kinds.append(('important', 'K1', 'switch -> current of pair %s, summed at %s with main pair %s' % (
                        '/'.join(gates), '/'.join(sorted(drains)), '/'.join(sorted(main_g)))))
                else:
                    # gain stage switched in (VGA row, plan §2.6-1). K6 if the stage output is shared by >= 2 bit paths
                    sh = sharing_paths(drains)
                    if sh:
                        kinds.append(('important', 'K6', 'gain code: switch -> current of an extra pair with the SAME inputs %s as the main pair; '
                                      'stage output %s shared by %s' % ('/'.join(gates), '/'.join(sorted(drains)),
                                                                       '; '.join('%s (%s)' % (', '.join(v), c) for c, v in sh.items()))))
                    else:
                        kinds.append(('general', 'K7', 'gain code not shared: switch -> current of an extra pair with the SAME inputs %s' % '/'.join(gates)))
            else:
                kinds.append(('general', 'K7', 'switch across %s-%s (degeneration bank inside the high-speed path: peaking/gain trim)' % (s, dr)))
        k = 'important' if any(k == 'important' for k, _, _ in kinds) else 'general'
        order = ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11']
        kk = min((kn for kd, kn, _ in kinds if kd == k), key=order.index)
        first = sorted(sws, key=lambda d: d['path'])[0]
        control_info[n] = {'kind': k, 'K': kk, 'why': sorted({w for _, _, w in kinds}), 'bundle_type': sorted(btypes),
                           'switches': [d['path'] for d in sws], 'endpoint': first['path'] + '.g',
                           'source': 'port' if n in top_ports else 'internal'}
        netclass[n] = ['important_control' if k == 'important' else 'general_control']
    bias_why = {}
    for n in all_nets:
        if netclass[n]:
            continue
        users = gate_users(F, n)
        diode = any(d['kind'] == 'mos' and d['terms']['g'] == n and n in (d['terms']['d'], d['terms']['s']) for d, t in F.by_net[n])
        if F.cm_node(n):
            netclass[n] = ['bias']; bias_why[n] = 'common-mode node of a termination'; continue
        if diode:
            netclass[n] = ['bias']; bias_why[n] = 'diode-connected (mirror) node'; continue
        if users:
            what = sorted({('active-inductor gate' if F.is_rail(F.eff[d['path']][1]) else 'tail/current source' if F.is_rail(F.eff[d['path']][0]) and not F.loaded(d, F.eff[d['path']][1]) or F.pair_node(F.eff[d['path']][1], d) or any(F.eff[e['path']][0] == F.eff[d['path']][1] for e, t in F.by_net[F.eff[d['path']][1]] if e is not d and e['kind'] == 'mos')
                            else 'load') for d in users})
            netclass[n] = ['bias']; bias_why[n] = 'drives only gates of ' + ', '.join(what); continue
        netclass[n] = ['internal']
    return dict(data_r=data_r, data_ev=data_ev, clk_r=clk_r, clk_ev=clk_ev, clock_inputs=clock_inputs,
                clk_evidence=clk_evidence, netclass=netclass, control_info=control_info, bias_why=bias_why, depth=depth)


def device_role(F, d, data_r, clk_r, netclass):
    if d['kind'] != 'mos':
        a, b = d['terms']['p'], d['terms']['n']
        if F.is_rail(a) or F.is_rail(b):
            if d['kind'] == 'cap':
                return {'role': 'cap_to_rail'}
            o = b if F.is_rail(a) else a
            # R from supply to a gate-only node = active-inductor gate resistor
            if all(t == 'g' for e, t in F.by_net[o] if e is not d):
                return {'role': 'gate_r'}
            return {'role': 'r_to_rail'}
        if F.cm_node(a) or F.cm_node(b):
            return {'role': 'termination'}
        return {'role': 'series_' + d['kind']}
    s, dr = F.eff[d['path']]
    g = d['terms']['g']
    sig = lambda n: n in data_r or n in clk_r
    t = d['type']
    own = F.ground if t == 'n' else F.supply
    if F.is_rail(s) and g == own and not F.is_rail(dr):
        return {'role': 'esd' if sig(dr) else 'off_device'}
    if g in (d['terms']['d'], d['terms']['s']):
        return {'role': 'diode'}
    p = F.tg_partner(d)
    if p is not None:
        return {'role': 'tg', 'partner': p['local']}
    for e, tt in F.by_net[g]:
        if e is not d and e['kind'] == 'mos' and tt == 'd' and e['type'] == t and e['terms']['g'] == d['terms']['d'] and e['inst'] == d['inst']:
            return {'role': 'cross', 'partner': e['local']}
    if F.is_rail(dr):
        return {'role': 'active_inductor' if not sig(g) else 'follower'}
    if sig(g):
        if F.loaded(d, dr):
            if F.is_rail(s) and g in clk_r and not F.static_cmos(dr):
                return {'role': 'reset'}
            if F.static_cmos(dr):
                return {'role': 'logic'}
            return {'role': 'input'}
        # stacked device of a static CMOS gate?
        seen = {dr}; q = [dr]
        while q:
            y = q.pop()
            if F.static_cmos(y):
                return {'role': 'logic'}
            for e, tt in F.by_net[y]:
                if e is not d and e['kind'] == 'mos' and e['type'] == t and tt in 'ds':
                    o = e['terms']['s' if tt == 'd' else 'd']
                    if o not in seen and not F.is_rail(o):
                        seen.add(o); q.append(o)
        if F.is_rail(s) and F.pair_node(dr, d):
            return {'role': 'clocked_tail'}
        if F.pair_node(dr, d):
            return {'role': 'clock_steering'}
        return {'role': 'unknown'}
    gc = netclass.get(g, [])
    if 'general_control' in gc or 'important_control' in gc:
        return {'role': 'switch'}
    if F.is_rail(s):
        feeds = [e for e, tt in F.by_net[dr] if e is not d and e['kind'] == 'mos' and tt in 'ds'
                 and F.eff[e['path']][0] == dr and not F.is_rail(F.eff[e['path']][1])]
        if feeds:
            if all('general_control' in netclass.get(e['terms']['g'], []) or 'important_control' in netclass.get(e['terms']['g'], []) for e in feeds):
                return {'role': 'switched_current_source'}
            return {'role': 'tail'}
        return {'role': 'load'}
    return {'role': 'cascode' if 'bias' in gc else 'unknown'}


# ---------------- groups (primitive units inside a cell) ----------------
def cell_groups(cells, cname, croles, block_roles, rails_local):
    c = cells[cname]
    prims = [e for e in c['elems'] if e['kind'] != 'inst']
    dacs = [e for e in c['elems'] if e['kind'] == 'inst' and block_roles.get(e['cell'], {}).get('role') == 'dac']
    items = [('p', e['name']) for e in prims] + [('x', e['name']) for e in dacs]
    parent = {it: it for it in items}
    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def u(a, b):
        parent[f(a)] = f(b)
    netitems = collections.defaultdict(list)
    gate_of = collections.defaultdict(list)
    for e in prims:
        if e['kind'] == 'mos':
            for t in 'ds':
                n = e['terms'][t]
                if n not in rails_local:
                    netitems[n].append(('p', e['name']))
            gate_of[e['terms']['g']].append(('p', e['name']))
        else:
            for n in e['terms'].values():
                if n not in rails_local:
                    netitems[n].append(('p', e['name']))
    for e in dacs:
        sub = cells[e['cell']]
        # output pin(s) of the DAC: nets that connect to channels inside the parent
        for p, n in e['pins'].items():
            if n in netitems and n not in rails_local:
                netitems[n].append(('x', e['name']))
    for n, its in netitems.items():
        # a net connecting only to channel terminals joins the items; ports that are inputs of other instances do not matter
        for a in its[1:]:
            u(its[0], a)
    # gate-only attachments (e.g. active-inductor gate resistor joins its transistor):
    # an internal (non-port) net used by exactly one passive and one gate
    for n, its in list(netitems.items()):
        if n in c['ports'] or n not in gate_of:
            continue
        gd = gate_of[n]
        if len(its) == 1 and len(gd) == 1 and its[0][0] == 'p':
            e0 = [p for p in prims if p['name'] == its[0][1]][0]
            if e0['kind'] in ('res', 'cap'):
                u(its[0], gd[0])
    groups = collections.defaultdict(list)
    for it in items:
        groups[f(it)].append(it[1])
    return [sorted(v, key=lambda nm: [x['name'] for x in c['elems']].index(nm)) for v in groups.values()]


def group_role(cells, cname, members, croles, cn, F, prefix):
    c = cells[cname]
    el = {e['name']: e for e in c['elems']}
    rl = collections.Counter(croles[m]['role'] for m in members if m in croles)
    if rl.get('termination') or rl.get('esd'):
        parts = []
        if rl.get('termination'): parts.append('termination')
        if rl.get('esd'): parts.append('ESD')
        return {'role': 'termination_esd' if rl.get('esd') else 'termination', 'conf': 'high', 'symbol': 'R/ESD mark on input line',
                'why': ' + '.join(parts) + ': R from HS input to a common-mode node' + (', MOS pad clamps with gate tied to own rail' if rl.get('esd') else '')}
    if rl and set(rl) == {'tg'}:
        return {'role': 'tg', 'conf': 'high', 'symbol': 'switch (TG)', 'why': 'NMOS+PMOS between the same two nets, gates tied to rails'}
    if rl.get('clocked_tail') and rl.get('cross', 0) >= 4 and rl.get('reset'):
        return {'role': 'strongarm', 'conf': 'high', 'symbol': 'triangle + clock',
                'why': 'clocked tail, input pair, cross-coupled NMOS on input drains + cross-coupled PMOS, reset PMOS'}
    if rl.get('cross', 0) >= 2 and rl.get('clock_steering', 0) >= 2:
        return {'role': 'latch', 'conf': 'high', 'symbol': 'box LATCH', 'why': 'input pair + cross-coupled pair, tails steered by complementary clocks'}
    if rl.get('logic') and set(rl) <= {'logic'}:
        n_p = sum(1 for m in members if el[m].get('type') == 'p')
        n_n = sum(1 for m in members if el[m].get('type') == 'n')
        if n_p == 1 and n_n == 1:
            return {'role': 'inverter', 'conf': 'high', 'symbol': 'inverter', 'why': 'complementary PMOS/NMOS with common gate and drain'}
        ps = [el[m] for m in members if el[m].get('type') == 'p']; ns = [el[m] for m in members if el[m].get('type') == 'n']
        outs = {e['terms']['d'] for e in ps} & {e['terms']['d'] for e in ns} | {e['terms']['s'] for e in ps} & {e['terms']['d'] for e in ns}
        par_p = all(F.is_rail(F.eff[prefix + e['name']][0]) for e in ps)       # every PMOS from the supply = parallel pull-up
        ser_n = sum(1 for e in ns if F.is_rail(F.eff[prefix + e['name']][0])) == 1 and len(ns) >= 2
        par_n = all(F.is_rail(F.eff[prefix + e['name']][0]) for e in ns)
        ser_p = sum(1 for e in ps if F.is_rail(F.eff[prefix + e['name']][0])) == 1 and len(ps) >= 2
        if par_p and ser_n and n_p == n_n:
            return {'role': 'nand', 'conf': 'high', 'symbol': 'box (cell name) + output bubble',
                    'why': 'static CMOS gate: %d parallel PMOS pull-ups, %d series NMOS pull-downs (NAND, dictionary list §2.6-1)' % (n_p, n_n)}
        if par_n and ser_p and n_p == n_n:
            return {'role': 'nor', 'conf': 'high', 'symbol': 'box (cell name) + output bubble',
                    'why': 'static CMOS gate: %d series PMOS, %d parallel NMOS (NOR, dictionary list §2.6-1)' % (n_p, n_n)}
        return {'role': 'static_cmos_gate', 'conf': 'low', 'symbol': 'box (cell name)', 'why': 'static CMOS gate (pull-up gate set = pull-down gate set), stack shape not a dictionary gate'}
    inputs = [m for m in members if m in croles and croles[m]['role'] == 'input']
    if inputs:
        # pair inputs by structural source node
        loc_eff = {m: F.eff[prefix + m] for m in inputs}
        by_src = collections.defaultdict(list)
        for m in inputs:
            by_src[loc_eff[m][0]].append(m)
        pairs = [v for v in by_src.values() if len(v) == 2]
        singles = [v[0] for v in by_src.values() if len(v) == 1]
        degen = False
        if len(singles) == 2 and not pairs:
            sa = loc_eff[singles[0]][0]; sb = loc_eff[singles[1]][0]
            # sources connected by R/C/switch
            for m in members:
                e = el[m]
                ts = set(e['terms'].values()) if e['kind'] != 'inst' else set()
                if e['kind'] in ('res', 'cap') and {prefix_strip(F, prefix, sa), prefix_strip(F, prefix, sb)} <= ts:
                    degen = True
            pairs = [singles]
        drains = [frozenset(F.eff[prefix + m][1] for m in p) for p in pairs]
        gates = [frozenset(el[m]['terms']['g'] for m in p) for p in pairs]
        if len(pairs) == 1:
            if degen:
                return {'role': 'ctle', 'conf': 'high', 'symbol': 'triangle "CTLE"', 'why': 'differential pair with separate sources joined by R/C (source degeneration)'}
            return {'role': 'cml_buffer', 'conf': 'high', 'symbol': 'triangle "BUF"', 'why': 'single differential pair, common tail, loads'}
        if len(set(drains)) == 1:
            if len(set(gates)) == 1:
                return {'role': 'vga', 'conf': 'high', 'symbol': 'triangle "VGA"', 'why': '%d pairs share outputs, all with the same inputs; extra pairs switched in' % len(pairs)}
            return {'role': 'summer', 'conf': 'high', 'symbol': 'Σ', 'why': '%d pairs with different inputs summed at shared outputs' % len(pairs)}
    return {'role': 'unknown', 'conf': 'low', 'symbol': 'box (cell name)', 'why': 'structure not in dictionary'}


def prefix_strip(F, prefix, n):
    return n[len(prefix):] if n.startswith(prefix) else n


def mirror_partners(cells, cname, F, prefix, pairs_seed):
    """structural P/N mirror: seed with input net pairs, extend through devices with a unique candidate
    (same kind/type/size, all known terminal nets mapped). Returns (net map, device map, unmatched)."""
    c = cells[cname]
    prims = [e for e in c['elems'] if e['kind'] != 'inst']
    nm = {}
    for a, b in pairs_seed:
        nm[a] = b; nm[b] = a
    for e in prims:
        if e['kind'] == 'mos':
            nm.setdefault(e['terms']['b'], e['terms']['b'])
    for p in c['ports']:
        pass
    rails = {F.supply, F.ground}
    for ln in cell_all_nets(c):
        if ln in rails:
            nm[ln] = ln
    dm = {}
    def keys(e):
        return [k for k in e['terms'] if not (e['kind'] == 'mos' and k == 'b')]
    def cands(e):
        out = []
        for f2 in prims:
            if f2['name'] in dm or f2['kind'] != e['kind'] or f2.get('type') != e.get('type'):
                continue
            if e['kind'] == 'mos' and e['params'] != f2['params']:
                continue
            if e['kind'] != 'mos' and e.get('value') != f2.get('value'):
                continue
            ok = True; nk = 0
            if e['kind'] == 'mos':
                for k in keys(e):
                    a = e['terms'][k]
                    if a in nm:
                        nk += 1
                        if f2['terms'][k] != nm[a]:
                            ok = False; break
            else:
                ts = list(e['terms'].values()); ts2 = list(f2['terms'].values())
                for a in ts:
                    if a in nm:
                        nk += 1
                        if nm[a] not in ts2:
                            ok = False; break
            if ok and nk:
                out.append(f2)
        return out
    changed = True
    relax = False
    while True:
        changed = False
        for e in prims:
            if e['name'] in dm:
                continue
            cs = cands(e)
            if len(cs) == 1 or (relax and cs):
                f2 = cs[0]
                dm[e['name']] = f2['name']; dm[f2['name']] = e['name']
                if e['kind'] == 'mos':
                    for k in keys(e):
                        a, b = e['terms'][k], f2['terms'][k]
                        nm.setdefault(a, b); nm.setdefault(b, a)
                else:
                    ts = list(e['terms'].values()); ts2 = list(f2['terms'].values())
                    known = [a for a in ts if a in nm]
                    if len(known) == 1:
                        a = known[0]; oa = [x for x in ts if x != a][0]
                        ob = [x for x in ts2 if x != nm[a]]
                        if ob:
                            nm.setdefault(oa, ob[0]); nm.setdefault(ob[0], oa)
                changed = True
                relax = False
        if not changed:
            if relax:
                break
            relax = True
    unmatched = [e['name'] for e in prims if e['name'] not in dm]
    return nm, dm, unmatched


def cell_all_nets(c):
    s = set(c['ports'])
    for e in c['elems']:
        s |= set(e['pins'].values()) if e['kind'] == 'inst' else set(e['terms'].values())
    return s


def F_local_global(F, prefix, n):
    return n


def main():
    nl, top, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    hs_inputs = sys.argv[4:]
    cells, order = parse(nl)
    F = Flat(cells, top)
    insts = instance_tree(cells, top)
    top_ports = cells[top]['ports']
    C = classify(F, cells, top, hs_inputs)
    data_r, clk_r, netclass = C['data_r'], C['clk_r'], C['netclass']

    cellnet = collections.defaultdict(lambda: collections.defaultdict(set))
    cell_insts = collections.defaultdict(list)
    l2g = {}
    for prefix, cname, nm in insts:
        cell_insts[cname].append(prefix)
        l2g[prefix] = nm
        for ln, gn in nm.items():
            for c in netclass.get(gn, ['internal']):
                cellnet[cname][ln].add(c)
    for cname in cells:
        for p in cells[cname]['ports']:
            if not cellnet[cname][p]:
                cellnet[cname][p].add('unused')

    roles = {}
    for cname in cells:
        if not cell_insts[cname]:
            continue
        r = {}
        for prefix in cell_insts[cname]:
            for d in F.devs:
                if d['inst'] != prefix:
                    continue
                rr = device_role(F, d, data_r, clk_r, netclass)
                if d['local'] in r and r[d['local']]['role'] != rr['role']:
                    r[d['local']].setdefault('alt', []).append(rr['role'])
                else:
                    r.setdefault(d['local'], rr)
        roles[cname] = r

    # block roles bottom-up
    block = {}
    groups = {}
    def rails_local(cname):
        pre = cell_insts[cname][0]
        return {ln for ln, gn in l2g[pre].items() if gn in F.rails}
    done = set()
    def solve(cname):
        if cname in done:
            return block[cname]
        c = cells[cname]
        for e in c['elems']:
            if e['kind'] == 'inst':
                solve(e['cell'])
        cn = cellnet[cname]
        hs = any(('data' in v or 'clock' in v) for v in cn.values())
        rl = collections.Counter(v['role'] for v in roles.get(cname, {}).values())
        insts_ = [e for e in c['elems'] if e['kind'] == 'inst']
        prims = [e for e in c['elems'] if e['kind'] != 'inst']
        if not hs:
            if rl.get('diode'):
                b = {'role': 'bias', 'conf': 'high', 'symbol': 'omit', 'why': 'diode/mirror devices only; no high-speed net'}
            elif rl.get('switch') and (rl.get('switched_current_source') or rl.get('tail')):
                b = {'role': 'dac', 'conf': 'high', 'symbol': 'variable current source (concept symbol in parent)',
                     'why': 'repeated (bias current source + series switch) units sharing one output'}
            else:
                b = {'role': 'no_hs', 'conf': 'low', 'symbol': 'omit', 'why': 'no high-speed net'}
            block[cname] = b; done.add(cname); return b
        pre = cell_insts[cname][0]
        gs = cell_groups(cells, cname, roles.get(cname, {}), block, rails_local(cname))
        ginfo = []
        for gm in gs:
            gr = group_role(cells, cname, [m for m in gm if m in roles.get(cname, {})], roles.get(cname, {}), cn, F, pre)
            gr['members'] = gm
            ginfo.append(gr)
        groups[cname] = ginfo
        nondac = [e for e in insts_ if block.get(e['cell'], {}).get('role') != 'dac']
        if not nondac and len(ginfo) == 1:
            b = dict(ginfo[0]); b.pop('members', None)
        elif not prims and len(nondac) == 2 and nondac[0]['cell'] == nondac[1]['cell']:
            a, bb = nondac
            sub = block[a['cell']]['role']
            subports = cells[a['cell']]['ports']
            # series: an output pin net of a is an input pin net of b
            link = set(a['pins'].values()) & set(bb['pins'].values())
            if sub == 'latch':
                ca = (a['pins'].get('CLK'), a['pins'].get('CLKB'))
                cb = (bb['pins'].get('CLK'), bb['pins'].get('CLKB'))
                # identify clock pins structurally: pins that are clock-only in the latch cell
                b = {'role': 'dff', 'conf': 'high' if ('DFF' in cname.upper() or 'FF' in cname.upper()) else 'low',
                     'symbol': 'box DFF', 'why': 'two latches in series (master->slave) with complementary clocks'}
            elif sub in ('nand', 'nor') and (set(a['pins'].values()) & set(bb['pins'].values())):
                # cross-coupled: each gate's output drives an input of the other
                b = {'role': 'sr_latch', 'conf': 'high', 'symbol': 'box (cell name)',
                     'why': 'two %s gates cross-coupled (output of each drives an input of the other): SR latch (dictionary list §2.6-1)' % sub.upper()}
            elif sub == 'static_cmos_gate':
                b = {'role': 'cross_coupled_gates', 'conf': 'low', 'symbol': 'box (cell name)',
                     'why': 'two static CMOS gates cross-coupled; NOT in the dictionary'}
            else:
                b = {'role': 'composite', 'conf': 'high', 'symbol': 'box (cell name)', 'why': 'two sub-blocks'}
        elif [g['role'] for g in ginfo] == ['strongarm'] and nondac and all(block[e['cell']]['role'] in ('sr_latch', 'inverter') for e in nondac):
            b = {'role': 'comparator', 'conf': 'high', 'symbol': 'triangle "SA" + clock',
                 'why': 'StrongARM core (clocked tail, input pair, cross-coupled NMOS/PMOS, reset PMOS) + output stage (%s): comparator row' %
                        ', '.join(sorted({block[e['cell']]['role'] for e in nondac}))}
        else:
            b = {'role': 'composite', 'conf': 'high', 'symbol': 'box (cell name)',
                 'why': 'hierarchical: %d sub-blocks + %d primitive unit(s); every sub-block is a dictionary block' % (len(nondac), len(ginfo))}
        block[cname] = b; done.add(cname)
        return b
    solve(top)
    for cname in cells:
        if cell_insts[cname] and cname not in done:
            solve(cname)

    # latch pairs inside composite cells: divider check (feedback loop)
    findings = []
    for cname in cells:
        c = cells[cname]
        latches = [e for e in c['elems'] if e['kind'] == 'inst' and block.get(e['cell'], {}).get('role') == 'latch']
        if len(latches) >= 2 and block.get(cname, {}).get('role') != 'dff':
            outs = {}
            ins = {}
            for e in latches:
                lc = cellnet[e['cell']]
                # data inputs/outputs of the latch cell by trace direction (first instance)
                outs[e['name']] = [e['pins'][p] for p in ('QP', 'QN') if p in e['pins']]
                ins[e['name']] = [e['pins'][p] for p in ('DP', 'DN') if p in e['pins']]
            for a in latches:
                for b2 in latches:
                    if a is b2: continue
                    if set(outs[a['name']]) & set(ins[b2['name']]):
                        loop = bool(set(outs[b2['name']]) & set(ins[a['name']]))
                        clkpins_a = {a['pins'].get('CLK'), a['pins'].get('CLKB')}
                        d_is_clock = bool(set(ins[a['name']]) & clkpins_a)
                        findings.append({'cell': cname, 'master': a['name'], 'slave': b2['name'], 'feedback_loop': loop,
                                         'master_D_is_its_own_clock': d_is_clock,
                                         'name_hint_divider': any('DIV' in x['name'].upper() for x in (a, b2))})

    # mirror (symmetry) analysis for differential unit cells
    sym = {}
    # seeds are derived structurally: input-pair gate nets of each cell (no name rule)
    sym = {}
    for cname in cells:
        if not cell_insts[cname] or block.get(cname, {}).get('role') in ('bias', 'dac'):
            continue
        pre = cell_insts[cname][0]
        r = roles.get(cname, {})
        el = {e['name']: e for e in cells[cname]['elems']}
        ins = [m for m, v in r.items() if v['role'] in ('input',) and el[m]['kind'] == 'mos']
        seed = []
        bysrc = collections.defaultdict(list)
        for m in ins:
            bysrc[F.eff[pre + m][0]].append(m)
        for v in bysrc.values():
            if len(v) == 2 and el[v[0]]['type'] == el[v[1]]['type']:
                seed.append((el[v[0]]['terms']['g'], el[v[1]]['terms']['g']))
        if not seed:
            continue
        nm, dm, un = mirror_partners(cells, cname, F, pre, seed)
        sym[cname] = {'seed': seed, 'unmatched_devices': un}

    # undriven high-speed nets (plan §2.3-13): every channel on the net belongs to an always-off TG, no other driver
    def off_tg(d):
        p = F.tg_partner(d)
        if p is None:
            return False
        own = lambda m: F.ground if m['type'] == 'n' else F.supply
        return d['terms']['g'] == own(d) and p['terms']['g'] == own(p)
    undriven = []
    for n, cs in netclass.items():
        if not ({'data', 'clock'} & set(cs)) or n in hs_inputs or n in C['clock_inputs']:
            continue
        chans = [(d, t) for d, t in F.by_net[n] if d['kind'] == 'mos' and t in 'ds']
        passive = [d for d, t in F.by_net[n] if d['kind'] != 'mos']
        if chans and all(off_tg(d) for d, t in chans) and not passive:
            undriven.append(n)
    # unused outputs (plan §3.5-4): a high-speed local net of a cell with a single connection
    unused = collections.defaultdict(list)
    for cname in cells:
        if not cell_insts[cname]:
            continue
        cnt = collections.Counter()
        for e in cells[cname]['elems']:
            vals = e['pins'].values() if e['kind'] == 'inst' else [v for k, v in e['terms'].items() if not (e['kind'] == 'mos' and k == 'b')]
            for v in vals:
                cnt[v] += 1
        for n, k in cnt.items():
            if k == 1 and n not in cells[cname]['ports'] and ({'data', 'clock'} & cellnet[cname][n]):
                unused[cname].append(n)
    res = {
        'undriven_hs': sorted(undriven), 'unused_outputs': {c: sorted(v) for c, v in unused.items()},
        'top': top, 'rails': {'supply': F.supply, 'ground': F.ground},
        'hs_inputs': hs_inputs, 'clock_inputs': C['clock_inputs'], 'clock_evidence': C['clk_evidence'],
        'netclass': {k: v for k, v in sorted(netclass.items())},
        'bias_why': C['bias_why'],
        'data_trace': {k: v for k, v in sorted(data_r.items(), key=lambda kv: kv[1]['depth'])},
        'clock_trace': {k: v for k, v in sorted(clk_r.items(), key=lambda kv: kv[1]['depth'])},
        'data_events': C['data_ev'], 'clock_events': C['clk_ev'],
        'control_info': C['control_info'],
        'cellnet': {c: {n: sorted(v) for n, v in d.items()} for c, d in cellnet.items()},
        'cell_insts': cell_insts,
        'roles': roles, 'block': block, 'groups': groups, 'latch_pairs': findings, 'symmetry': sym,
        'eff': F.eff, 'l2g': l2g,
    }
    json.dump(res, open(outdir + '/analysis.json', 'w'), indent=1, default=list)
    print('clock inputs', C['clock_inputs'])
    for c in cells:
        print(c, block.get(c))
        for g in groups.get(c, []):
            print('    group', g['role'], g['members'])
    print('latch pairs', findings)
    print('symmetry', sym)


if __name__ == '__main__':
    main()
