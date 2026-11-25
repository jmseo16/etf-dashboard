"""Structural analysis of the flattened design: rails, high-speed tracing, control classification.

Everything here is decided from structure. Names are used only to pair differential ports.
Result: Analysis object with a class for every flat net, the drivers of every net, and questions.
"""
import re
from collections import OrderedDict, defaultdict
from . import netlist as NL

VISIBLE = ('hs_data', 'hs_clock', 'reference', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K8', 'K9', 'status')
KPRI = ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K8', 'K9', 'K7', 'K10', 'K11']
KTEXT = {'K1': '가중치(탭 계수)', 'K2': '경로 선택', 'K3': '켜기/끄기', 'K4': '종단', 'K5': '구동 세기', 'K6': '기준 레벨 코드',
         'K7': '트림(정적)', 'K8': '명령', 'K9': '시험 입력', 'K10': '일반(모드)', 'K11': '바이어스'}
SUP_RE = re.compile(r'^(vdd|vcc|avdd|dvdd|vpp)\w*$')
GND_RE = re.compile(r'^(vss|gnd|avss|dvss|vee|0)\w*$')


class Analysis(object):
    pass


def _pair_name(a, b):
    """True when two port names look like the two halves of a differential pair."""
    sa, ia = NL.bus_split(a)
    sb, ib = NL.bus_split(b)
    if ia != ib:
        return False
    for x, y in ((sa, sb), (sb, sa)):
        for p, n in (('p', 'n'), ('_p', '_n'), ('_t', '_c'), ('t', 'c'), ('', 'b'), ('', '_b'), ('', 'n'), ('p', 'm'), ('', 'bar'), ('_t', '_b')):
            if x.endswith(p) and y.endswith(n) and x[:len(x) - len(p)] == y[:len(y) - len(n)] and len(x) - len(p) > 0:
                return True
    return False


def analyze(cells, top, ann=None):
    ann = ann or {}
    A = Analysis()
    A.cells, A.top = cells, top
    F = NL.flatten(cells, top)
    A.flat = F
    tports = cells[top].ports
    # ---------------------------------------------------------------- rails
    sup, gnd = set(), set()
    for path, d, pm in F:
        if d.kind == 'm':
            (sup if d.mtype == 'p' else gnd).add(pm['b'])
    both = sup & gnd
    for n in both:
        base = n.split('/')[-1]
        if GND_RE.match(base):
            sup.discard(n)
        else:
            gnd.discard(n)
    for p in tports:
        if SUP_RE.match(p):
            sup.add(p)
        elif GND_RE.match(p):
            gnd.add(p)
    rails = sup | gnd
    A.sup, A.gnd, A.rails = sup, gnd, rails
    # ---------------------------------------------------------------- indices
    n = len(F)
    kind = [d.kind for _, d, _ in F]
    gate_of, chan_of, pas_of, dio_of = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    ch = [None] * n       # channel nets (a, b) of device i (two-terminal for r/c/d as well)
    src = [None] * n      # declared source net of a MOS
    gt = [None] * n
    cap = [False] * n     # MOS used as capacitor
    for i, (path, d, pm) in enumerate(F):
        if d.kind == 'm':
            gt[i] = pm['g']
            ch[i] = (pm['d'], pm['s'])
            if pm['d'] == pm['s']:
                cap[i] = True
                # a MOS capacitor is a two-terminal device between its gate and its tied channel
                if pm['g'] not in rails:
                    pas_of[pm['g']].append(i)
                if pm['d'] not in rails:
                    pas_of[pm['d']].append(i)
                ch[i] = (pm['g'], pm['d'])
                continue
            src[i] = pm['s']
            gate_of[pm['g']].append(i)
            chan_of[pm['d']].append(i)
            chan_of[pm['s']].append(i)
        elif d.kind in 'rc':
            ch[i] = (pm['a'], pm['b'])
            pas_of[pm['a']].append(i)
            pas_of[pm['b']].append(i)
        elif d.kind == 'd':
            ch[i] = (pm['a'], pm['k'])
            dio_of[pm['a']].append(i)
            dio_of[pm['k']].append(i)
    A.gate_of, A.chan_of, A.pas_of = gate_of, chan_of, pas_of
    ismos = lambda i: kind[i] == 'm' and not cap[i]
    size = [(d.model, d.params.get('w'), d.params.get('l'), d.params.get('m', '1')) for _, d, _ in F]
    mtype = [d.mtype for _, d, _ in F]

    def other(i, net):
        a, b = ch[i]
        return b if a == net else a

    # power switch: MOS whose two channel nets are both rails (header / footer)
    pwr_sw = [i for i in range(n) if ismos(i) and ch[i][0] in rails and ch[i][1] in rails and ch[i][0] != ch[i][1]]
    # diode-connected MOS -> bias node
    bias_nodes = set(gt[i] for i in range(n) if ismos(i) and gt[i] in ch[i] and gt[i] not in rails)
    # not a bias node: the fed-back device of a unity buffer (diode-connected, but one half of a matched pair)
    for i in range(n):
        if ismos(i) and gt[i] in ch[i] and src[i] not in rails and gt[i] in bias_nodes:
            if any(j != i and ismos(j) and mtype[j] == mtype[i] and src[j] == src[i] and size[j] == size[i] and gt[j] != gt[i]
                   for j in chan_of.get(src[i], ())):
                bias_nodes.discard(gt[i])
    # ---------------------------------------------------------------- regenerative pairs and clocked devices
    regen = set()
    for a in range(n):
        if not ismos(a) or gt[a] in rails:
            continue
        for b in chan_of.get(gt[a], ()):
            if b != a and ismos(b) and mtype[a] == mtype[b] and gt[b] != gt[a] and gt[b] in ch[a]:
                regen.add(gt[a])
                regen.add(gt[b])

    def reach_regen(net, hops=3):
        seen, fr = {net}, [net]
        for _ in range(hops):
            nx = []
            for x in fr:
                if x in regen:
                    return True
                for i in chan_of.get(x, ()):
                    o = other(i, x)
                    if o not in rails and o not in seen:
                        seen.add(o)
                        nx.append(o)
            fr = nx
        return any(x in regen for x in fr)

    def railside(i):
        a, b = ch[i]
        if a in rails and b not in rails:
            return b
        if b in rails and a not in rails:
            return a
        return None

    def pure_stack(x, t):
        cs = [j for j in chan_of.get(x, ()) if ismos(j)]
        return len(cs) == 2 and len(chan_of.get(x, ())) == 2 and not gate_of.get(x) and not pas_of.get(x) and \
            all(mtype[j] == t for j in cs) and x not in tports

    # a transmission gate with one side on a rail (a mux input tied to a constant): n and p across the same two nets
    grp_ = defaultdict(list)
    for i in range(n):
        if ismos(i):
            grp_[frozenset(ch[i])].append(i)
    tgrail = set()
    for k_, v_ in grp_.items():
        if len(k_) == 2 and len(k_ & rails) == 1 and set(mtype[i] for i in v_) == {'n', 'p'} and \
                not (set(gt[i] for i in v_ if mtype[i] == 'n') & set(gt[i] for i in v_ if mtype[i] == 'p')):
            tgrail.update(v_)

    def gate_out(i):
        """Output net of the static stage device i belongs to (the end of its series stack away from the rail).
        None for a pass device (both channel nets are ordinary nodes)."""
        if i in tgrail:
            return None
        t = mtype[i]
        ends = [x for x in ch[i] if x not in rails and not pure_stack(x, t)]
        if len(ends) == 2:
            return None
        if len(ends) == 1:
            o = other(i, ends[0])
            # the far side must lead to a rail through the stack, otherwise it is a pass device
            prev, x = i, o
            for _ in range(8):
                if x in rails:
                    return ends[0]
                if not pure_stack(x, t):
                    return None
                nxt = [j for j in chan_of[x] if j != prev][0]
                prev, x = nxt, other(nxt, x)
            return None
        # both ends are stack nodes or rails: walk away from the rail
        prev, x = i, (ch[i][0] if ch[i][1] in rails else ch[i][1])
        for _ in range(8):
            if x in rails:
                return None
            if not pure_stack(x, t):
                return x
            nxt = [j for j in chan_of[x] if j != prev][0]
            prev, x = nxt, other(nxt, x)
        return None

    def near(a, b, hops=2):
        seen, fr = {a}, [a]
        for _ in range(hops):
            nx = []
            for x in fr:
                for i in chan_of.get(x, ()):
                    o = other(i, x)
                    if o == b:
                        return True
                    if o not in rails and o not in seen:
                        seen.add(o)
                        nx.append(o)
            fr = nx
        return False

    ckdev, ckgate = set(), set()
    for x, devs in list(gate_of.items()):
        if x in rails:
            continue
        ns = [i for i in devs if mtype[i] == 'n' and railside(i)]
        ps = [i for i in devs if mtype[i] == 'p' and railside(i)]
        outs_n = set(gate_out(i) for i in ns)
        hit = []
        for j in ps:
            if gate_out(j) in outs_n:
                continue                       # same static gate
            for i in ns:
                if gate_out(i) == railside(i) and near(railside(i), railside(j)):
                    hit += [i, j]
        if hit:
            ckgate.add(x)
            ckdev.update(hit)
            # every precharge / tail device of this clock on the same stage
            for j in ps + ns:
                if any(near(railside(j), railside(h)) or railside(j) == railside(h) for h in hit):
                    ckdev.add(j)

    def inv_out(x):
        """Nets driven by a plain inverter whose input is x."""
        outs = []
        for i in gate_of.get(x, ()):
            y = railside(i)
            if y is None:
                continue
            gs = set(gt[j] for j in chan_of.get(y, ()) if ismos(j) and railside(j) == y)
            ts = set(mtype[j] for j in chan_of.get(y, ()) if ismos(j) and railside(j) == y and gt[j] == x)
            if gs == {x} and ts == {'n', 'p'}:
                outs.append(y)
        return outs

    fr = list(ckgate)
    while fr:                       # complement clocks made by an inverter (double-tail second stage)
        x = fr.pop()
        for y in inv_out(x):
            devs = [i for i in gate_of.get(y, ()) if railside(i) and reach_regen(railside(i), 1) and gate_out(i) == railside(i)
                    and not any(gt[j] == y and mtype[j] != mtype[i] and gate_out(j) == gate_out(i) for j in gate_of.get(y, ()))]
            if devs and y not in ckgate:
                ckgate.add(y)
                ckdev.update(devs)
                fr.append(y)
    # transmission-gate latches: two TGs with swapped gates sharing a node, one of them closing a loop
    tg = {}
    for i in range(n):
        if ismos(i) and ch[i][0] not in rails and ch[i][1] not in rails:
            tg.setdefault(frozenset(ch[i]), []).append(i)
    tgs = [(k, v) for k, v in tg.items() if len(k) == 2 and set(mtype[i] for i in v) == {'n', 'p'}]
    tgset = set(i for k_, v_ in tgs for i in v_) | tgrail      # transmission gates: the only devices treated as pass switches

    def drives(x, y, depth=4):
        """y is reachable from x through gate -> channel steps (static stages)."""
        seen, fr = {x}, [x]
        for _ in range(depth):
            nx = []
            for u in fr:
                for i in gate_of.get(u, ()):
                    for o in ch[i]:
                        if o not in rails and o not in seen:
                            if o == y:
                                return True
                            seen.add(o)
                            nx.append(o)
            fr = nx
        return False

    stor, latch_d = set(), set()       # latch storage nodes / data inputs of latches
    for k1, v1 in tgs:
        g1n = [gt[i] for i in v1 if mtype[i] == 'n'][0]
        g1p = [gt[i] for i in v1 if mtype[i] == 'p'][0]
        for k2, v2 in tgs:
            if k1 == k2 or not (k1 & k2):
                continue
            g2n = [gt[i] for i in v2 if mtype[i] == 'n'][0]
            g2p = [gt[i] for i in v2 if mtype[i] == 'p'][0]
            if g1n == g2p and g1p == g2n:
                x = list(k1 & k2)[0]
                y1, y2 = list(k1 - {x})[0], list(k2 - {x})[0]
                if drives(x, y1) or drives(x, y2):
                    ckgate.update((g1n, g1p))
                    ckdev.update(v1 + v2)
                    stor.add(x)
                    for y in (y1, y2):
                        if not drives(x, y):
                            latch_d.add(y)        # the far side of the input switch: where data enters the latch
    A.ckgate, A.regen = ckgate, regen
    # ---------------------------------------------------------------- pads and port pairs
    def esd_mos(i):
        """MOS between a net and a rail whose gate is a rail or goes to a rail through a resistor."""
        if not ismos(i) or railside(i) is None:
            return False
        g = gt[i]
        return g in rails or any(kind[j] == 'r' and other(j, g) in rails for j in pas_of.get(g, ())) and not gate_of.get(g, [None])[1:]

    def has_esd(x):
        return any(other(i, x) in rails for i in dio_of.get(x, ())) or any(esd_mos(i) for i in chan_of.get(x, ()))

    def input_like(p):
        """The port is not driven from inside: its channel attachments are only ESD devices."""
        return all(esd_mos(i) for i in chan_of.get(p, ()))

    pads = [p for p in tports if p not in rails and input_like(p) and
            (has_esd(p) or any(kind[i] == 'r' and has_esd(other(i, p)) for i in pas_of.get(p, ())))]
    padgrp = set(pads)
    for p in pads:                       # pad group: the pad and what a series resistor reaches
        for i in pas_of.get(p, ()):
            if kind[i] == 'r' and other(i, p) not in rails:
                padgrp.add(other(i, p))
    A.pads = pads
    plain = [p for p in tports if p not in rails and p not in pads]
    pairs, used = [], set()
    for i, a in enumerate(plain):
        for b in plain[i + 1:]:
            if a not in used and b not in used and _pair_name(a, b) and input_like(a) and input_like(b):
                pairs.append((a, b))
                used.update((a, b))
    for a, b in ann.get('pairs', []):
        pairs.append((a.lower(), b.lower()))

    # ---------------------------------------------------------------- forward tracing
    drivers = defaultdict(set)
    drivers_all = drivers
    padset = set()                 # output pads (filled once they are known)

    def trace(seeds, stop_ck, caps=True, blocked=(), rec=None):
        drivers = drivers_all if rec is None else rec
        seen, fr = set(seeds), list(seeds)
        hit_ck = False
        while fr:
            x = fr.pop(0)                     # nearest first: a net is 'driven' by the side the signal reaches it from
            for i in gate_of.get(x, ()):
                if i in ckdev:
                    hit_ck = True
                    if stop_ck:
                        continue
                for o in ch[i]:
                    if o not in rails:
                        if i not in tgset:
                            drivers[o].add(i)     # a transmission gate is not driven by its select: data flow sets its direction
                        if o not in seen:
                            seen.add(o)
                            fr.append(o)
            for i in chan_of.get(x, ()):
                o = other(i, x)
                if o not in rails and o not in seen:
                    drivers[o].add(i)
                    seen.add(o)
                    fr.append(o)
            for i in pas_of.get(x, ()):
                o = other(i, x)
                if kind[i] != 'r' and (not caps or o in blocked):
                    continue
                if kind[i] == 'r' and o in padset:
                    drivers[o].add(i)             # every leg that reaches a pad drives it
                if o not in rails and o not in seen:
                    if kind[i] == 'r':
                        drivers[o].add(i)
                    seen.add(o)
                    fr.append(o)
        return seen, hit_ck

    def feeds_pair(a, b):
        """a and b gate two same-type devices that share a source node (a differential pair)."""
        for i in gate_of.get(a, ()):
            for j in gate_of.get(b, ()):
                if mtype[i] == mtype[j] and src[i] == src[j] and src[i] not in rails:
                    return True
        return False

    def first_stage_logic(p):
        """Every device gated by p is an input of a static CMOS gate (it has a complementary partner)."""
        devs = gate_of.get(p, ())
        if not devs:
            return False
        for i in devs:
            if not any(gt[j] == p and mtype[j] != mtype[i] and gate_out(j) == gate_out(i) and gate_out(i) is not None for j in devs):
                return False
        return True

    def clock_reach(p):
        """p reaches a clocked device through static stages only."""
        seen, fr = {p}, [p]
        while fr:
            x = fr.pop()
            if x in ckgate:
                return True
            for i in gate_of.get(x, ()):
                if i in ckdev:
                    return True
                for o in ch[i]:
                    if o not in rails and o not in seen:
                        seen.add(o)
                        fr.append(o)
            for i in pas_of.get(x, ()):
                o = other(i, x)
                if o not in rails and o not in seen:
                    seen.add(o)
                    fr.append(o)
            for i in chan_of.get(x, ()):
                o = other(i, x)
                if o not in rails and o not in seen and i not in ckdev:
                    seen.add(o)
                    fr.append(o)
        return False

    questions = []
    data_seeds, clk_seeds = [], []
    forced = dict((k.lower(), v) for k, v in ann.get('net_class', {}).items())
    for p in pads:
        (clk_seeds if clock_reach(p) else data_seeds).append(p)
    for a, b in pairs:
        if feeds_pair(a, b):
            (clk_seeds if clock_reach(a) and clock_reach(b) else data_seeds).extend([a, b])
        elif first_stage_logic(a) and first_stage_logic(b) and clock_reach(a) and clock_reach(b):
            clk_seeds += [a, b]
    # ---------------------------------------------------------------- transmit side: inputs that are not pads
    def fwd(seeds, through_clock=False, clock_gates=False):
        """Nets reached going forward (gate -> stage output, static pass switches, R). No side effects."""
        seen, fr = set(seeds), list(seeds)
        while fr:
            x = fr.pop()
            for i in gate_of.get(x, ()):
                if i in ckdev and not clock_gates:
                    continue                      # what gates a clocked device is a clock, not data moving on
                o = gate_out(i)
                if o is None and i not in tgset:
                    outs_ = [y for y in ch[i] if y not in rails and y != src[i]]      # pair device: its drain side
                else:
                    outs_ = [o] if o is not None else ([y for y in ch[i] if y not in rails] if clock_gates else [])
                for o in outs_:
                    if o not in seen:
                        seen.add(o)
                        fr.append(o)
            for i in chan_of.get(x, ()):
                o = other(i, x)
                if o in rails or o in seen or (i in ckdev and not through_clock):
                    continue
                if i in tgset:                    # pass switch
                    seen.add(o)
                    fr.append(o)
            for i in pas_of.get(x, ()):
                o = other(i, x)
                if kind[i] == 'r' and o not in rails and o not in seen:
                    seen.add(o)
                    fr.append(o)
        return seen
    inside = fwd(stor | regen)                 # what a state element drives: not a first entry of data
    after_latch = fwd(stor)
    primary_d = latch_d - inside
    taken = set(pads) | set(x for ab in pairs for x in ab)

    def undriven(p):
        return not any(ismos(j) and (gate_out(j) == p) for j in chan_of.get(p, ()))
    driven_ports = set(q for q in tports if q not in rails and (not undriven(q) or q in pads))
    tx_data, tx_clk = [], []
    for p in tports:
        if p in rails or p in taken or p in data_seeds or p in clk_seeds or not undriven(p) or not gate_of.get(p) and not chan_of.get(p):
            continue
        # a single-ended clock: the port, or its buffered copy, clocks a state element
        chain, fr_ = {p}, [p]
        for _ in range(6):
            fr_ = [y for x in fr_ for y in inv_out(x) if y not in chain]
            chain.update(fr_)
        if chain & ckgate:
            tx_clk.append(p)
            continue
        reach = fwd([p])
        if not (reach & primary_d):
            continue
        # ... and what it becomes after sampling leaves through an output
        if (fwd([p], through_clock=True) - {p}) & driven_ports:
            tx_data.append(p)
    data_seeds += tx_data
    clk_seeds += tx_clk
    # a pad whose legs are switched by that data is an output, not an input
    T_tx = set()
    if tx_data or tx_clk:
        T_tx = fwd(tx_data + [x for ab in pairs for x in ab if x in data_seeds], through_clock=True) | \
            fwd(tx_clk + [x for ab in pairs for x in ab if x in clk_seeds], through_clock=True, clock_gates=True)
    out_pads = []
    for p in pads:
        nodes = [p] + [other(i, p) for i in pas_of.get(p, ()) if kind[i] == 'r' and other(i, p) not in rails]
        if any(ismos(j) and railside(j) == z and gt[j] in T_tx for z in nodes for j in chan_of.get(z, ())):
            out_pads.append(p)
    for p in out_pads:
        for lst in (data_seeds, clk_seeds):
            if p in lst:
                lst.remove(p)
    A.out_pads = out_pads
    padset.update(out_pads)
    for p, c in forced.items():
        if p in tports:
            for lst in (data_seeds, clk_seeds):
                if p in lst:
                    lst.remove(p)
            if c == 'hs_data':
                data_seeds.append(p)
            elif c == 'hs_clock':
                clk_seeds.append(p)
    def find_ref(T_data, T):
        ref = set()
        for i in range(n):
            if not ismos(i) or gt[i] in T or gt[i] in rails or src[i] in rails:
                continue
            # the partner shares the source node, or sits across a degeneration R/C between the two sources
            srcs = [src[i]] + [other(r, src[i]) for r in pas_of.get(src[i], ()) if other(r, src[i]) not in rails]
            for sn in srcs:
                for j in chan_of.get(sn, ()):
                    if j != i and ismos(j) and mtype[j] == mtype[i] and src[j] == sn and gt[j] in T_data and gt[j] != gt[i] \
                            and size[i] == size[j]:
                        ref.add(gt[i])
        fr = list(ref)
        while fr:                        # a reference stays a reference through a series R or a static pass switch
            x = fr.pop()
            for i in pas_of.get(x, ()):
                o = other(i, x)
                if kind[i] == 'r' and o not in rails and o not in T and o not in ref:
                    ref.add(o)
                    fr.append(o)
            for i in chan_of.get(x, ()):
                o = other(i, x)
                if ismos(i) and gt[i] not in T and gt[i] not in ref and gt[i] != o and gt[i] != x \
                        and o not in rails and o not in T and o not in ref and o not in bias_nodes:
                    ref.add(o)
                    fr.append(o)
            # ... and through a unity buffer: the other gate of a matched pair whose one gate is the reference
            for i in gate_of.get(x, ()):
                if not ismos(i) or src[i] in rails:
                    continue
                for j in chan_of.get(src[i], ()):
                    o = gt[j]
                    if j != i and ismos(j) and mtype[j] == mtype[i] and src[j] == src[i] and size[i] == size[j] \
                            and o not in rails and o not in T and o not in ref and o not in bias_nodes:
                        ref.add(o)
                        fr.append(o)
        return ref - bias_nodes

    def full_trace(caps, blocked):
        ckrec = defaultdict(set)              # what the clock walk found; pass switches on data nets do not count
        T_clk, _ = trace(clk_seeds, stop_ck=True, caps=caps, blocked=blocked, rec=ckrec)
        T_data, _ = trace(data_seeds, stop_ck=False, caps=caps, blocked=blocked)
        T_clk -= T_data - set(clk_seeds)
        # nodes under a clocked tail / precharge device belong to the data path
        add = set()
        for i in ckdev:
            if railside(i):
                for o in ch[i]:
                    if o not in rails and o not in T_data and o not in T_clk:
                        add.add(o)
                        drivers[o].add(i)
        more, _ = trace(list(T_data | add), stop_ck=False, caps=caps, blocked=blocked)
        T_data |= more - T_clk
        # clock dividers: a clocked latch that no data reaches (it samples its own output) makes a new clock
        for _ in range(6):
            new = set()
            for i in ckdev:
                if gate_out(i) is None and gt[i] in T_clk:
                    for o in ch[i]:
                        if o not in rails and o not in T_data and o not in T_clk and o in inside:
                            new.add(o)        # fed from a state element, not from outside
            if not new:
                break
            m2, _ = trace(list(new), stop_ck=True, caps=caps, blocked=blocked, rec=ckrec)
            T_clk |= m2 - T_data - set(q for q in m2 if q in tports and undriven(q))   # an input that a latch samples stays an input
        for o, ds in ckrec.items():
            for i in ds:
                if (i not in tgset and (o not in T_data or gate_out(i) is not None)) or (i in tgset and o in T_clk):
                    drivers[o].add(i)
        return T_data, T_clk

    rx_seeds = [x for x in data_seeds if x not in tx_data]
    T_rxonly = (trace(rx_seeds, stop_ck=False)[0] if (rx_seeds and tx_data) else None)
    T_data, T_clk = full_trace(False, ())
    ref = find_ref(T_data, T_data | T_clk)
    T_data, T_clk = full_trace(True, ref)
    T = T_data | T_clk
    ref = find_ref(T_data, T) | ref
    ref -= T
    # ---------------------------------------------------------------- control tracing
    target = T | ref | padgrp
    cls = {}
    for x in rails:
        cls[x] = 'rail'
    for x in T_data:
        cls[x] = 'hs_data'
    for x in T_clk:
        cls[x] = 'hs_clock'
    for x in ref:
        cls.setdefault(x, 'reference')
    ctl_ports = [p for p in tports if p not in rails and p not in T and p not in ref]
    out_ports = set()
    A.endpoints = {}

    def foreign(o, p):
        """A net a control trace must not walk into: a bias node, or another input port (one nothing inside drives)."""
        if o == p:
            return False
        if o in bias_nodes:
            return True
        return o in tports and not any(ismos(j) and other(j, o) in rails for j in chan_of.get(o, ()))

    def ctl_trace(p):
        """Follow a static control. Returns (visited {net: polarity set}, endpoints [(dev, pol, via)], reaches_output)."""
        vis = {p: {0}}
        fr = [(p, 0)]
        ends, outs = [], []
        while fr:
            x, pol = fr.pop()
            if x in tports and x != p:
                outs.append(x)
            for i in gate_of.get(x, ()):
                a, b = ch[i]
                if (a in target or b in target) or i in pwr_sw:
                    ends.append((i, pol, 'gate'))
                    continue
                for o in (a, b):
                    if foreign(o, p):
                        if o in bias_nodes:
                            vis.setdefault(o, set())
                        continue
                    if o not in rails and (pol ^ 1) not in vis.setdefault(o, set()):
                        vis[o].add(pol ^ 1)
                        if i not in tgset:
                            drivers[o].add(i)     # a transmission gate does not drive what it connects: its select only opens it
                        fr.append((o, pol ^ 1))
            for i in chan_of.get(x, ()):
                o = other(i, x)
                if o in rails or foreign(o, p):
                    continue
                if o in target:
                    ends.append((i, pol, 'chan'))
                    continue
                if pol not in vis.setdefault(o, set()):
                    vis[o].add(pol)
                    drivers[o].add(i)
                    fr.append((o, pol))
            for i in pas_of.get(x, ()):
                o = other(i, x)
                if o in rails or foreign(o, p):
                    continue
                if o in target:
                    ends.append((i, pol, 'pas'))
                    continue
                if pol not in vis.setdefault(o, set()):
                    vis[o].add(pol)
                    drivers[o].add(i)
                    fr.append((o, pol))
        return vis, ends, outs

    def chan_reach(net, pred, hops=3, through=None):
        """Some net satisfying pred is reachable from net through channels / R within hops."""
        seen, fr = {net}, [net]
        for _ in range(hops + 1):
            nx = []
            for x in fr:
                if pred(x):
                    return True
                for i in list(chan_of.get(x, ())) + [j for j in pas_of.get(x, ()) if kind[j] == 'r']:
                    o = other(i, x)
                    if o not in seen and (o not in rails or pred(o)):
                        seen.add(o)
                        nx.append(o)
            fr = nx
        return False

    def end_type(i, via):
        """What a control endpoint device does: term / ref / sum / trim / gate / pwr."""
        a, b = ch[i]
        if i in pwr_sw:
            return 'pwr'
        if not ismos(i):
            return 'gate'
        if via == 'gate' and gate_out(i) in loopnodes:
            return 'state'
        hs = [x for x in (a, b) if x in target]
        non = [x for x in (a, b) if x not in target]
        # termination: rail -- switch -- (R) -- pad
        if (a in rails or b in rails):
            o = b if a in rails else a
            if o in padgrp or any(kind[j] == 'r' and other(j, o) in padgrp for j in pas_of.get(o, ())):
                return 'term'
        for x in (a, b):
            if x not in rails and any(kind[j] == 'r' and other(j, x) in padgrp and (a in rails or b in rails) for j in pas_of.get(x, ())):
                return 'term'
        # reference level: the switch leads to a reference net
        for x in (a, b):
            if x in ref or (x not in rails and any(kind[j] == 'r' and other(j, x) in ref for j in pas_of.get(x, ()))):
                return 'ref'
        # trim: the far side of the switch only holds capacitors
        for x in non:
            if x not in rails and not gate_of.get(x) and len(chan_of.get(x, ())) == 1 and pas_of.get(x):
                return 'trim'
        for x in (a, b):
            if x not in rails and not gate_of.get(x) and len(chan_of.get(x, ())) == 1 and pas_of.get(x) and \
                    all(kind[j] != 'r' for j in pas_of[x]):
                return 'trim'
        # offset trim: a static device in parallel with a device whose gate is a high-speed signal
        if via == 'gate' and a not in rails and b not in rails and gt[i] not in T:
            if any(j != i and ismos(j) and set(ch[j]) == {a, b} and gt[j] in T for j in chan_of.get(a, ())):
                return 'trim'
        # summing branch: the switch sits under a pair (common-source node of two devices with HS gates)
        for x in (a, b):
            if x in rails:
                continue
            up = [j for j in chan_of.get(x, ()) if j != i and ismos(j) and (gt[j] in T or gt[j] in ref)]
            if len(up) >= 2 and len(set(gt[j] for j in up)) >= 2:
                return 'sum'
        return 'gate'

    def has_partner(i):
        """Device i is one input device of a static CMOS gate (a complementary device shares its gate net and output)."""
        o = gate_out(i)
        return o is not None and any(mtype[j] != mtype[i] and gate_out(j) == o for j in gate_of.get(gt[i], ()))

    def is_delay_select(ends):
        """Both mux data inputs carry the same signal, one of them delayed by buffers."""
        for i, pol, via in ends:
            if not ismos(i) or ch[i][0] in rails or ch[i][1] in rails:
                continue
            a, b = ch[i]
            for z in (a, b):
                src = other(i, z)
                others = [other(j, z) for j in chan_of.get(z, ()) if j != i and ismos(j) and other(j, z) not in rails and other(j, z) != src]
                for s2 in others:
                    if drives(src, s2, 12) or drives(s2, src, 12):
                        return True
        return False

    # ---------------------------------------------------------------- three-valued switch-level evaluation
    def net_paths(o, t, val):
        """(definitely on, possibly on) for the type-t network between node o and its rail."""
        want = 1 if t == 'n' else 0
        rail_ok = gnd if t == 'n' else sup
        best = [False, False]

        def walk(x, seen, definite, depth):
            for i in chan_of.get(x, ()):
                if not ismos(i) or mtype[i] != t or i in seen:
                    continue
                g = gt[i]
                v = (1 if g in sup else 0) if g in rails else val.get(g)
                if v is not None and v != want:
                    continue
                d2 = definite and v == want
                y = other(i, x)
                if y in rail_ok:
                    best[1] = True
                    if d2:
                        best[0] = True
                elif y not in rails and depth < 4 and not gate_of.get(y) and y not in tports:
                    walk(y, seen | {i}, d2, depth + 1)
        walk(o, frozenset(), True, 0)
        return best

    def node_value(o, val):
        pd, pdp = net_paths(o, 'n', val)
        if pd:
            return 0
        pu, pup = net_paths(o, 'p', val)
        if pu and not pdp:
            return 1
        return None

    def propagate(init):
        val = dict(init)
        fr = list(init)
        guard = 0
        while fr and guard < 4000:
            guard += 1
            x = fr.pop()
            for i in gate_of.get(x, ()):
                o = gate_out(i)
                if o is None or o in val or o in rails:
                    continue
                v = node_value(o, val)
                if v is not None:
                    val[o] = v
                    fr.append(o)
        return val
    A.propagate = propagate
    # driver legs on output pads: (device, pad)
    legs, leg_pad = [], {}
    for pd_ in out_pads:
        nodes = [pd_] + [other(i, pd_) for i in pas_of.get(pd_, ()) if kind[i] == 'r' and other(i, pd_) not in rails]
        for z in nodes:
            for j in chan_of.get(z, ()):
                if ismos(j) and railside(j) == z and gt[j] not in rails and not esd_mos(j):
                    legs.append(j)
                    leg_pad[j] = pd_
    leg_gate = defaultdict(list)
    for j in legs:
        leg_gate[gt[j]].append(j)
    ctl_set = set(ctl_ports)
    cone = {}

    def cone_of(q):
        if q not in cone:
            cone[q] = fwd([q])
        return cone[q]

    def leg_state(j, val):
        v = val.get(gt[j])
        if v is None:
            return 'x'
        return 'on' if (v == 1) == (mtype[j] == 'n') else 'off'

    def force_class(p):
        """How a control acts on the pad driver legs it reaches: 'term' (can hold a leg on whatever the data does),
        'drv' (can only switch a leg off / let the data through), or None."""
        mine = [g for g in leg_gate if g in cone_of(p)]
        if not mine:
            return None, []
        res, hit = None, []
        for g in mine[:3]:
            j = leg_gate[g][0]
            co = [q for q in ctl_ports if q != p and g in cone_of(q)][:7]
            for m in range(1 << len(co)):
                base = dict((q, (m >> k) & 1) for k, q in enumerate(co))
                st = []
                for v in (0, 1):
                    base[p] = v
                    st.append(leg_state(j, propagate(base)))
                if 'on' in st and st[0] != st[1]:
                    return 'term', [j]
                if 'off' in st and 'x' in st:
                    res = 'drv'
                    hit = leg_gate[g]
        return res, hit

    def forces_nothing(p):
        """Neither value of the control pins any high-speed node: it only changes strength or timing (a trim)."""
        gates_ = set(gt[i] for i, pol, via in A.endpoints.get(p, ()))
        for v in (0, 1):
            val = propagate({p: v})
            if any(g not in val for g in gates_):
                return False                  # the evaluation did not get as far as the endpoints: not known
            if any(x in T for x in val if x != p):
                return False
        return True
    # nodes of latch loops (a set / reset device sits on one of them)
    loopnodes = set(stor)
    for x in stor:
        for y in fwd([x]):
            if y != x and x in fwd([y], through_clock=True):
                loopnodes.add(y)

    port_k, port_why = OrderedDict(), {}
    ctl_vis = {}
    for p in ctl_ports:
        vis, ends, outs = ctl_trace(p)
        ctl_vis[p] = vis
        A.endpoints[p] = ends
        types = [end_type(i, via) for i, pol, via in ends]
        pols = set(pol ^ (1 if mtype[i] == 'p' else 0) for i, pol, via in ends
                   if via == 'gate' and ismos(i) and ((ch[i][0] not in rails and ch[i][1] not in rails) or i in tgrail) and not has_partner(i))
        why = ''
        if p in bias_nodes or any(x in bias_nodes for x in vis) and not ends:
            k, why = 'K11', '다이오드 연결 노드(바이어스)'
        elif not ends and outs:
            k, why = 'status_in', '출력 포트로만 감'
        elif not ends:
            k, why = 'K10', '고속 노드에 닿는 끝점 없음'
        elif legs and force_class(p)[0] == 'term':
            k, why = 'K4', '데이터와 무관하게 패드 다리를 켤 수 있음(종단)'
        elif legs and force_class(p)[0] == 'drv':
            hit = force_class(p)[1]
            others = [j for j in legs if j not in hit and leg_pad[j] in set(leg_pad[h] for h in hit)]
            if hit and all(gt[j] in after_latch for j in hit) and others and not all(gt[j] in after_latch for j in others):
                k, why = 'K1', '한 박자 늦은 데이터로 구동되는 패드 다리의 가중치(디엠퍼시스/FFE)'
            else:
                k, why = 'K5', '패드 드라이버 다리를 고르는 코드(구동 세기)'
        elif types and all(t == 'state' for t in types):
            k, why = 'K8', '상태 소자(래치/플립플롭)의 세트·리셋'
        elif 'term' in types:
            k, why = 'K4', '패드로 가는 R의 직렬 스위치'
        elif 'ref' in types:
            k, why = 'K6', '기준 전압으로 가는 스위치(레벨 코드)'
        elif all(t == 'trim' for t in types):
            k, why = 'K7', '정적 트림(C를 붙이는 스위치, 또는 입력 소자와 병렬인 오프셋 가지)'
        elif len(pols) == 2 and 'pwr' not in types:
            if is_delay_select(ends):
                k, why = 'K7', '같은 신호의 지연 탭 선택(정적 지연 트림)'
            else:
                k, why = 'K2', '양쪽 극성으로 경로를 고름(선택)'
        elif 'sum' in types and all(t in ('sum',) for t in types):
            k, why = 'K1', '합산 가지(차동쌍 아래 스위치)'
        elif 'pwr' in types:
            k, why = 'K3', '전원 스위치(헤더/풋터)'
        elif all(t == 'gate' for t in types) and all(via == 'gate' and gate_out(i) is not None for i, pol, via in ends) and forces_nothing(p):
            k, why = 'K7', '어느 값으로도 고속 노드를 묶지 못함(세기·타이밍 트림)'
        else:
            k, why = 'K3', '고속 경로의 게이트/꼬리 스위치'
        port_k[p], port_why[p] = k, why
    # one class per bus: multi-bit 'sum' = K1, 1-bit 'sum' = K3 (enable)
    stems = defaultdict(list)
    for p in ctl_ports:
        s, ix = NL.bus_split(p)
        stems[s if ix is not None else p].append(p)
    for s, ps in stems.items():
        ks = set(port_k[p] for p in ps)
        if len(ps) == 1 and port_k[ps[0]] == 'K5':
            port_k[ps[0]], port_why[ps[0]] = 'K3', '1비트: 패드 드라이버를 켜고 끔'
        if len(ps) == 1 and port_k[ps[0]] == 'K1':
            port_k[ps[0]], port_why[ps[0]] = 'K3', '1비트: 고속 경로의 꼬리 스위치(켜기)'
        elif len(ks) > 1:
            best = min(ks, key=lambda k: KPRI.index(k) if k in KPRI else 99)
            for p in ps:
                port_k[p] = best
    for p, c in forced.items():
        if p in port_k and (c in KPRI or c in ('status_in',)):
            port_k[p], port_why[p] = c, '사용자 답'
        elif p in port_k and c in ('control_hidden', 'hidden'):
            port_k[p], port_why[p] = 'K7', '사용자 답'
        elif p in port_k and c == 'bias':
            port_k[p], port_why[p] = 'K11', '사용자 답'
        elif p in port_k and c == 'reference':
            port_k.pop(p)
            ref.add(p)
            cls[p] = 'reference'
    A.port_k, A.port_why = port_k, port_why

    def kcls(k):
        return k if k in VISIBLE else ('status' if k == 'status_in' else ('bias' if k == 'K11' else 'hidden'))

    # nets on a control trace take the class of the control (the most visible one when several)
    order = sorted(port_k, key=lambda p: KPRI.index(port_k[p]) if port_k[p] in KPRI else 50)
    for p in reversed(order):
        for x in ctl_vis.get(p, {}):
            if x not in rails and x not in T and x not in ref:
                cls[x] = kcls(port_k[p])
    for x in bias_nodes:
        if x not in T:
            cls[x] = 'bias'
    # outputs: top ports driven from inside
    for p in tports:
        if p in rails:
            continue
        if p in T and p not in data_seeds and p not in clk_seeds:
            out_ports.add(p)
            if T_rxonly is not None and p not in T_rxonly and p not in padgrp:
                cls[p] = 'status'             # sampled side input (not from a pad) leaving through its own output
        elif p not in T and p not in ctl_ports:
            pass
    for p in tports:
        # actively driven from inside and not a high-speed net: status output
        if p in rails or p in T or p in bias_nodes:
            continue
        if any(ismos(j) and gate_out(j) == p for j in chan_of.get(p, ())):
            port_k.pop(p, None)
            cls[p] = 'status'
            out_ports.add(p)
    for x in ref:                         # what holds a reference net: channel or resistor attachments
        for i in list(chan_of.get(x, ())) + [j for j in pas_of.get(x, ()) if kind[j] == 'r']:
            drivers[x].add(i)
    for x in bias_nodes:
        for i in chan_of.get(x, ()):
            if gt[i] == x:
                drivers[x].add(i)
    A.cls, A.T_data, A.T_clk, A.ref = cls, T_data, T_clk, ref
    A.data_seeds, A.clk_seeds, A.out_ports = data_seeds, clk_seeds, out_ports
    A.drivers = drivers
    A.bias_nodes, A.padgrp, A.pwr_sw = bias_nodes, padgrp, pwr_sw
    A.kind, A.ch, A.gt, A.mtype, A.ckdev = kind, ch, gt, mtype, ckdev
    A.gate_out, A.src, A.size, A.has_partner = gate_out, src, size, has_partner
    A.index = dict((path, i) for i, (path, d, pm) in enumerate(F))
    A.pairs = pairs
    # ---------------------------------------------------------------- questions (low confidence only)
    for p in pads:
        pass
    for p, k in port_k.items():
        if k == 'K10':
            questions.append({'id': 'ctl:%s' % p, 'item': p,
                              'q': '포트 %s: 고속 노드에 닿는 끝점을 찾지 못했습니다. 숨길까요?' % p,
                              'options': ['K10(숨김)', 'K3', 'K8', 'hs_data', 'hs_clock'], 'default': 'K10(숨김)'})
        if k == 'status_in':
            questions.append({'id': 'ctl:%s' % p, 'item': p,
                              'q': '포트 %s: 고속 클럭으로 샘플되어 관찰용 출력으로만 갑니다(데이터 입력처럼 쓰임). 시험 입력으로 한 줄 그립니다.' % p,
                              'options': ['K9', 'K8', 'hs_data', 'hs_clock'], 'default': 'K9'})
    A.questions = questions
    return A


def cell_occurrences(cells, top):
    """{cell: [(inst_path, {local net: flat net})]} for every instance in the hierarchy (top has path '')."""
    occ = defaultdict(list)

    def walk(cname, prefix, bind):
        c = cells[cname]
        local = {}
        for p in c.ports:
            local[p] = bind[p]
        for d in c.devs:
            for nname in (d.pins.values()):
                if nname not in local:
                    local[nname] = prefix + nname
        occ[cname].append((prefix[:-1] if prefix else '', local))
        for d in c.devs:
            if d.kind == 'x':
                walk(d.model, prefix + d.name + '/', dict((p, local[nn]) for p, nn in d.pins.items()))
    walk(top, '', dict((p, p) for p in cells[top].ports))
    return occ
