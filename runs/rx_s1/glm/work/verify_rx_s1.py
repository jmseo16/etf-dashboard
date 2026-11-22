# Self-test for rx_s1 block-level drawing: netlist connectivity (soundness/completeness),
# node coverage, hidden-list coverage, geometry (box overlap, canvas, text width).
import sys, os, json, copy, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, model
from types import SimpleNamespace
def clone(m, **kw):
    d = {k: copy.deepcopy(getattr(m,k)) for k in dir(m) if k.isupper()}
    d.update(kw)
    return SimpleNamespace(**d)
NET = '/home/user/exam_haiku/repo/runs/rx_s1/input/netlist.sp'

def parse_top(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    start = [i for i,l in enumerate(lines) if l.startswith('.subckt dq_rx_unit ')][0]
    end = [i for i in range(start,len(lines)) if lines[i].startswith('.ends')][0]
    ports = lines[start].split()[2:]
    elems = []
    for l in lines[start+1:end]:
        t = l.split()
        if not t or l.startswith('*'): continue
        name = t[0]
        if name.startswith('x'):
            elems.append((name, t[1:-1]))
        elif name[0] in 'rm':
            npins = 2 if name[0]=='r' else 4
            elems.append((name, t[1:1+npins]))
    return ports, elems

def netnodes(m, ports, elems):
    g_of = {}
    for g, insts in m.GROUPS.items():
        for i in insts: g_of[i] = g
    nets = {}
    for name, pins in elems:
        g = g_of.get(name)
        if g is None: continue
        for p in pins:
            nets.setdefault(p, set()).add(g)
    for p in ports:
        nets.setdefault(p, set())
        bus = m.BUS_OF.get(p)
        nodename = 'P:' + (bus or p)
        nets[p].add(nodename)
    # keep nets with >=2 nodes after hiding
    out = {}
    for n, s in nets.items():
        if n in m.HIDDEN_PORTS: continue
        s2 = set()
        for x in s:
            if x.startswith('P:'):
                nm = x[2:]
                if nm in m.HIDDEN_PORTS or nm.split('<')[0] in ('ofe_p','ofe_n','ofo_p','ofo_n') or nm in m.HIDDEN_PORTS:
                    continue
                s2.add(x)
            elif x in m.HIDDEN_NODES:
                continue
            else:
                s2.add(x)
        if len(s2) >= 2: out[n] = s2
    return out

def union_find_connected(nodes, edges):
    par = {n:n for n in nodes}
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for a,b in edges:
        if a in par and b in par: par[f(a)] = f(b)
    return len({f(n) for n in nodes}) == 1

OUTDIR = '.'

def segs_of(m):
    from types import SimpleNamespace
    import gen_geom
    return gen_geom.all_segments(m)

def check(m, ports, elems):
    res = {}
    net = netnodes(m, ports, elems)
    # 1 soundness: each drawn edge's nets must touch both endpoints
    snd = 0; details=[]
    for a,b,nets in m.EDGES:
        for n in nets:
            ns = net.get(n, set())
            if a not in ns or b not in ns:
                snd += 1; details.append(f'soundness: {a}-{b} net {n}')
    res['1_soundness'] = snd
    # 2 completeness: each net's nodes connected by drawn edges carrying that net
    comp = 0
    for n, nodes in net.items():
        es = [(a,b) for a,b,nets in m.EDGES if n in nets]
        if not union_find_connected(nodes, es):
            comp += 1; details.append(f'completeness: net {n} nodes {sorted(nodes)}')
    res['2_completeness'] = comp
    # 3 node existence: every drawn endpoint is a known box or port
    unk = 0
    for a,b,_ in m.EDGES:
        for x in (a,b):
            if x.startswith('P:'):
                if x[2:] not in m.PORT_POS and x[2:] not in m.PORTS and x[2:] not in m.BUS_OF.values(): unk+=1
            elif x not in m.BOXES: unk+=1
    res['3_unknown_nodes'] = unk
    # 4 coverage: every non-hidden group appears in drawing
    drawn = {x for a,b,_ in m.EDGES for x in (a,b) if not x.startswith('P:')}
    missing = [g for g in m.GROUPS if g not in m.HIDDEN_NODES and g not in drawn]
    res['4_group_coverage'] = len(missing)
    # 5 box overlap
    bx = list(m.BOXES.items()); ov = 0
    for i in range(len(bx)):
        for j in range(i+1,len(bx)):
            a=bx[i][1]; b=bx[j][1]
            if a['x']<b['x']+b['w'] and b['x']<a['x']+a['w'] and a['y']<b['y']+b['h'] and b['y']<a['y']+a['h']:
                ov+=1; details.append(f'overlap {bx[i][0]} {bx[j][0]}')
    res['5_box_overlap'] = ov
    # 6 canvas: boxes and ports inside 1200x680
    out = 0
    for k,b in m.BOXES.items():
        if b['x']<0 or b['y']<0 or b['x']+b['w']>1200 or b['y']+b['h']>680: out+=1
    for k,(x,y) in m.PORT_POS.items():
        if x<0 or y<0 or x>1200 or y>680: out+=1
    res['6_canvas'] = out
    # 7 text width: title/sub approx 7px per char (title 13px bold ~8px) must fit box width
    tw = 0
    for k,b in m.BOXES.items():
        if len(b['title'])*8 > b['w'] or len(b['sub'])*6 > b['w']: tw+=1; details.append(f'text width {k}')
    res['7_text_width'] = tw
    # 8 hidden list covers every hidden port of the netlist used in drawing
    html_path = os.path.join(os.path.dirname(os.path.abspath(OUTDIR)) if False else OUTDIR, 'concept.html')
    html = open(html_path, encoding='utf-8').read().lower() if os.path.exists(html_path) else ''
    hid_tokens = ['rx_bias','ibias','ofe','ofo','전원','net27','net29']
    miss = [t for t in hid_tokens if t not in html]
    import gen_geom
    res['8_hidden_listed'] = len(miss)
    res['9_diagonal_segments'] = gen_geom.diagonal_count(m)
    res['10_crossings'] = gen_geom.crossings(m)
    res['11_line_through_box'] = gen_geom.through_box_count(m)
    for t in miss: details.append(f'hidden item not listed in 생략 목록: {t}')
    return res, details

if __name__ == '__main__':
    out_dir = sys.argv[1]
    OUTDIR = out_dir
    ports, elems = parse_top(NET)
    report = {}
    base, det = check(model, ports, elems)
    report['baseline'] = base; report['baseline_details'] = det
    inj = {}
    # injection A: remove one drawn edge -> completeness must catch
    m2 = clone(model, EDGES=[e for e in model.EDGES if e[0]!='SR_E' or e[1]!='OUT_E'])
    r,_ = check(m2, ports, elems); inj['A_remove_edge_SR_E-OUT_E'] = {'caught': r['2_completeness']>0, 'count': r['2_completeness']}
    # injection B: add a wrong edge -> soundness must catch
    m3 = clone(model, EDGES=model.EDGES + [('PAD','SA_E',['net1'])])
    r,_ = check(m3, ports, elems); inj['B_add_wrong_edge_PAD-SA_E'] = {'caught': r['1_soundness']>0, 'count': r['1_soundness']}
    # injection C: overlap two boxes -> overlap check must catch
    bx = copy.deepcopy(model.BOXES); bx['SA_O']['x']=bx['SUM_O']['x']+20; m4 = clone(model, BOXES=bx)
    r,_ = check(m4, ports, elems); inj['C_overlap_SA_O'] = {'caught': r['5_box_overlap']>0, 'count': r['5_box_overlap']}
    # injection D: drop a group from drawing -> coverage must catch
    m5 = clone(model, EDGES=[e for e in model.EDGES if 'SR_O' not in e[:2]])
    r,_ = check(m5, ports, elems); inj['D_drop_SR_O'] = {'caught': r['4_group_coverage']>0 or r['2_completeness']>0, 'count': r['4_group_coverage']+r['2_completeness']}
    report['injection'] = inj
    rd,_ = check(clone(model, EDGES=model.EDGES), ports, elems)
    # file checks
    fc = {'concept.html': os.path.exists(os.path.join(out_dir,'concept.html')), 'concept.pptx': os.path.exists(os.path.join(out_dir,'concept.pptx'))}
    report['files'] = fc
    json.dump(report, open(os.path.join(out_dir,'verify_report.json'),'w'), ensure_ascii=False, indent=1)
    print(json.dumps({'baseline': base, 'injection': inj, 'files': fc}, ensure_ascii=False))
    for d in det: print('  -', d)
