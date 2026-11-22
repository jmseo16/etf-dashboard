"""Independent check of a drawn scene. Nothing here uses the router's own data: the connection of
every pin is read back from the line coordinates alone and compared with the netlist."""
import hashlib
import json
from collections import defaultdict

CONN_KEYS = ('open', 'short', 'pin_open', 'dangling_end', 'tee_without_dot', 'width_mismatch')
QUAL_KEYS = ('avoidable_bend', 'short_jog', 'crossing', 'wire_through_symbol', 'text_overlap', 'text_on_wire',
             'text_on_symbol', 'four_way', 'lonely_label', 'placement_problem')


def scene_sha(S):
    keep = dict((k, S[k]) for k in ('id', 'title', 'w', 'h', 'symbols', 'wires', 'dots', 'labels', 'ports', 'texts', 'tags', 'slashes'))
    return hashlib.sha256(json.dumps(keep, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def _norm(s):
    x1, y1, x2, y2 = s
    return (x1, y1, x2, y2) if (x1, y1) <= (x2, y2) else (x2, y2, x1, y1)


def _on(p, s):
    """Point on segment (inclusive)."""
    x, y = p
    return (s[0] == s[2] == x and s[1] <= y <= s[3]) or (s[1] == s[3] == y and s[0] <= x <= s[2])


def _interior(p, s):
    x, y = p
    return (s[0] == s[2] == x and s[1] < y < s[3]) or (s[1] == s[3] == y and s[0] < x < s[2])


def netlist_net(cell, inst, pin):
    """Local net of (instance, pin) in a parsed cell. MOS capacitors use a = gate, b = tied channel."""
    for d in cell.devs:
        if d.name == inst:
            if d.kind == 'm' and pin in ('a', 'b'):
                return d.pins['g'] if pin == 'a' else d.pins['d']
            return d.pins.get(pin)
    return None


def check(S, cell, level):
    R = defaultdict(list)
    segs = []
    for w in S['wires']:
        for s in w['segs']:
            if (s[0], s[1]) != (s[2], s[3]):
                segs.append(_norm(s))
    stub = []
    for l in S['labels']:
        if l.get('seg'):
            stub.append(_norm(l['seg']))
    allsegs = sorted(set(segs + stub))
    dots = set((d[0], d[1]) for d in S['dots'])
    # ---------------------------------------------------------------- terminals
    terms = []     # (point, kind, payload)
    for sym in S['symbols']:
        for p in sym['pins']:
            terms.append(((p['x'], p['y']), 'pin', (sym, p)))
    for p in S['ports']:
        terms.append(((p['x'], p['y']), 'port', p))
    for l in S['labels']:
        terms.append(((l['x'], l['y']), 'label', l))
    for t in S['tags']:
        terms.append(((t['x'], t['y']), 'tag', t))
    tpts = set(t[0] for t in terms)
    # ---------------------------------------------------------------- split segments into pieces
    ends = defaultdict(int)
    for s in allsegs:
        ends[(s[0], s[1])] += 1
        ends[(s[2], s[3])] += 1
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    pieces = []
    for s in allsegs:
        horiz = s[1] == s[3]
        cut = set([(s[0], s[1]), (s[2], s[3])])
        for p in list(ends) + list(tpts) + list(dots):
            if not _interior(p, s):
                continue
            if p in dots or p in tpts:
                cut.add(p)
                continue
            # endpoint of another segment on our interior: collinear overlap joins, a perpendicular end needs a dot
            col = any((o[1] == o[3]) == horiz and o != s and _on(p, o) and (p == (o[0], o[1]) or p == (o[2], o[3])) for o in allsegs)
            if col:
                cut.add(p)
            else:
                R['tee_without_dot'].append('(%d,%d)' % p)
        pts = sorted(cut)
        for a, b in zip(pts, pts[1:]):
            pieces.append((a, b))
            union(a, b)
    for t in terms:
        find(t[0])
    # ---------------------------------------------------------------- crossings and 4-way points
    H = [s for s in allsegs if s[1] == s[3]]
    Vv = [s for s in allsegs if s[0] == s[2]]
    ncross = 0
    for h in H:
        for v in Vv:
            p = (v[0], h[1])
            if _interior(p, h) and _interior(p, v) and p not in dots:
                ncross += 1
                if (level == 'block' and not S.get('has_mos')) or find((h[0], h[1])) == find((v[0], v[1])):
                    R['crossing'].append('(%d,%d)' % p)
    deg = defaultdict(set)
    for a, b in pieces:
        deg[a].add(b)
        deg[b].add(a)
    for p, nb in deg.items():
        if len(nb) >= 4:
            R['four_way'].append('(%d,%d)' % p)
        if len(nb) >= 3 and p not in dots:
            R['tee_without_dot'].append('(%d,%d)' % p)
    # ---------------------------------------------------------------- name merging and comparison with the netlist
    comp_names = defaultdict(set)          # component -> names (labels, ports, rail tags)
    comp_pins = defaultdict(list)
    for pt, kind, pay in terms:
        c = find(pt)
        if kind == 'pin':
            comp_pins[c].append(pay)
        elif kind == 'port':
            comp_names[c].add(tuple(pay['bits']))
        elif kind == 'label':
            comp_names[c].add(tuple(pay['bits']))
        else:
            comp_names[c].add((pay['net'],))
    byname = defaultdict(list)
    for c, names in comp_names.items():
        for nm in names:
            byname[nm].append(c)
    for nm, cs in byname.items():
        for c in cs[1:]:
            union(cs[0], c)
    groups = defaultdict(lambda: {'pins': [], 'names': set()})
    for pt, kind, pay in terms:
        g = groups[find(pt)]
        if kind == 'pin':
            g['pins'].append(pay)
        elif kind == 'tag':
            g['names'].add((pay['net'],))
        else:
            g['names'].add(tuple(pay['bits']))
    net_groups = defaultdict(set)
    for root, g in groups.items():
        widths = set(len(p['bits']) for sym, p in g['pins']) | set(len(n) for n in g['names'])
        if len(widths) > 1:
            R['width_mismatch'].append('%s' % sorted(str(n) for n in g['names']))
            continue
        w = widths.pop() if widths else 1
        for k in range(w):
            nets = set(n[k] for n in g['names'])
            for sym, p in g['pins']:
                for inst, pin in p['bits'][k]:
                    n = netlist_net(cell, inst, pin)
                    if n is None:
                        R['short'].append('unknown pin %s.%s' % (inst, pin))
                    else:
                        nets.add(n)
            if len(nets) > 1:
                R['short'].append('nets %s drawn as one' % ', '.join(sorted(nets)))
            for n in nets:
                net_groups[n].add(root)
    for n, roots in net_groups.items():
        if len(roots) > 1:
            R['open'].append('net %s is drawn in %d separate pieces' % (n, len(roots)))
    # ---------------------------------------------------------------- loose pins and loose line ends
    seg_pts = set()
    for a, b in pieces:
        seg_pts.add(a)
        seg_pts.add(b)
    named_pts = set(t[0] for t in terms if t[1] in ('label', 'tag', 'port'))
    for pt, kind, pay in terms:
        if kind == 'pin' and pt not in seg_pts and pt not in named_pts:
            R['pin_open'].append('%s.%s at (%d,%d)' % (pay[0]['id'], pay[1]['name'], pt[0], pt[1]))
        if kind == 'port' and pt not in seg_pts:
            R['pin_open'].append('port %s at (%d,%d)' % (pay['name'], pt[0], pt[1]))
    for p, nb in deg.items():
        if len(nb) == 1 and p not in tpts:
            # a T on another line with a dot is a proper end
            if not (p in dots and any(_interior(p, s) for s in allsegs)):
                R['dangling_end'].append('(%d,%d)' % p)
    # ---------------------------------------------------------------- labels need a partner
    cnt = defaultdict(int)
    for l in S['labels']:
        if not l['gray']:
            cnt[tuple(l['bits'])] += 1
    portnames = set(tuple(p['bits']) for p in S['ports'])
    use = defaultdict(int)
    for d in cell.devs:
        for n in (d.pins.values() if hasattr(d.pins, 'values') else d.pins):
            use[n] += 1
    for nm, c in cnt.items():
        if c >= 2 or nm in portnames:
            continue
        if len(nm) == 1 and use.get(nm[0], 0) <= 1 and nm[0] not in cell.ports:
            continue                      # unused output: one lead with its name
        if any(set(nm) & set(pn) for pn in portnames):
            continue
        # every other pin of the net may be hidden on this screen
        drawn = sum(1 for sym in S['symbols'] for p in sym['pins'] if set(p.get('nets', [])) & set(nm))
        if drawn <= 1:
            continue
        R['lonely_label'].append(str(nm))
    # ---------------------------------------------------------------- bends that a straight line could replace
    boxes = [sym['box'] for sym in S['symbols']]
    tboxes = [t['bbox'] for t in S['texts']]
    node = set(p for p, nb in deg.items() if len(nb) != 2) | tpts | dots
    seen = set()

    def free_line(a, b):
        s = _norm((a[0], a[1], b[0], b[1]))
        for bx in boxes:
            if s[0] == s[2]:
                if bx[0] < s[0] < bx[2] and s[1] < bx[3] and s[3] > bx[1]:
                    return False
            elif bx[1] < s[1] < bx[3] and s[0] < bx[2] and s[2] > bx[0]:
                return False
        for bx in tboxes:
            if s[0] == s[2]:
                if bx[0] - 2 < s[0] < bx[2] + 2 and s[1] < bx[3] and s[3] > bx[1]:
                    return False
            elif bx[1] - 2 < s[1] < bx[3] + 2 and s[0] < bx[2] and s[2] > bx[0]:
                return False
        for o in allsegs:
            if s[0] == s[2]:
                if o[0] == o[2] == s[0] and o[1] < s[3] and o[3] > s[1]:
                    return False
                if o[1] == o[3] and o[0] <= s[0] <= o[2] and s[1] < o[1] < s[3]:
                    return False
            else:
                if o[1] == o[3] == s[1] and o[0] < s[2] and o[2] > s[0]:
                    return False
                if o[0] == o[2] and o[1] <= s[1] <= o[3] and s[0] < o[0] < s[2]:
                    return False
        for pt in tpts:
            if _interior(pt, s):
                return False
        return True
    pin_side = {}
    for sym in S['symbols']:
        for p in sym['pins']:
            pin_side[(p['x'], p['y'])] = p['side']
    for start in node:
        for nxt in deg.get(start, ()):
            if (start, nxt) in seen:
                continue
            path = [start, nxt]
            while path[-1] not in node:
                nb = [q for q in deg[path[-1]] if q != path[-2]]
                if not nb:
                    break
                path.append(nb[0])
            seen.add((start, nxt))
            seen.add((path[-1], path[-2]))
            # corners of the path
            corners = [path[i] for i in range(1, len(path) - 1)
                       if (path[i - 1][0] == path[i][0]) != (path[i][0] == path[i + 1][0])]
            if not corners:
                continue
            a, b = path[0], path[-1]
            run = [a] + corners + [b]
            for u, v in zip(run[1:-1], run[2:-1]):
                if abs(u[0] - v[0]) + abs(u[1] - v[1]) < 20:
                    R['short_jog'].append('(%d,%d)-(%d,%d)' % (u[0], u[1], v[0], v[1]))
            if (a[0] == b[0] or a[1] == b[1]) and a != b:
                d = 'v' if a[0] == b[0] else 'h'
                okside = True
                for e, o in ((a, b), (b, a)):
                    sd = pin_side.get(e)
                    if sd is None:
                        continue
                    want = {'h': ('r' if o[0] > e[0] else 'l'), 'v': ('b' if o[1] > e[1] else 't')}[d]
                    if sd != want:
                        okside = False
                if okside and free_line(a, b):
                    R['avoidable_bend'].append('(%d,%d)-(%d,%d): %d bends' % (a[0], a[1], b[0], b[1], len(corners)))
    # ---------------------------------------------------------------- wires through symbols, text overlaps
    for s in segs:
        for sym in S['symbols']:
            bx = sym['box']
            if s[0] == s[2]:
                hit = bx[0] + 1 < s[0] < bx[2] - 1 and s[1] < bx[3] - 1 and s[3] > bx[1] + 1
            else:
                hit = bx[1] + 1 < s[1] < bx[3] - 1 and s[0] < bx[2] - 1 and s[2] > bx[0] + 1
            if hit:
                R['wire_through_symbol'].append('%s (%d,%d)-(%d,%d)' % (sym['id'], s[0], s[1], s[2], s[3]))
    T = S['texts']
    for i, a in enumerate(T):
        for b in T[i + 1:]:
            A, B = a['bbox'], b['bbox']
            ox = min(A[2], B[2]) - max(A[0], B[0])
            oy = min(A[3], B[3]) - max(A[1], B[1])
            if ox > 2 and oy > 2:
                R['text_overlap'].append('"%s" / "%s"' % (a['s'], b['s']))
    for a in T:
        A = a['bbox']
        for s in segs:
            if s[0] == s[2]:
                hit = A[0] + 1 < s[0] < A[2] - 1 and s[1] < A[3] - 1 and s[3] > A[1] + 1
            else:
                hit = A[1] + 1 < s[1] < A[3] - 1 and s[0] < A[2] - 1 and s[2] > A[0] + 1
            if hit:
                R['text_on_wire'].append('"%s"' % a['s'])
                break
    # text crossed by a stroke of a symbol (lines, triangles, circles; box outlines are checked through their edges)
    strokes = []
    for sym in S['symbols']:
        for v in sym['shapes']:
            if v[0] == 'line':
                strokes.append((v[1], v[2], v[3], v[4]))
            elif v[0] == 'rect':
                x, y, w, h = v[1], v[2], v[3], v[4]
                strokes += [(x, y, x + w, y), (x, y + h, x + w, y + h), (x, y, x, y + h), (x + w, y, x + w, y + h)]
            elif v[0] == 'circle':
                strokes += [(v[1] - v[3], v[2], v[1] + v[3], v[2]), (v[1], v[2] - v[3], v[1], v[2] + v[3])]
            else:
                pts = v[1] + ([v[1][0]] if v[0] == 'poly' else [])
                strokes += [(a_[0], a_[1], b_[0], b_[1]) for a_, b_ in zip(pts, pts[1:])]
    for tg in S['tags']:
        for v in tg['shapes']:
            if v[0] == 'line':
                strokes.append((v[1], v[2], v[3], v[4]))
    for p_ in S['ports']:
        pts = p_['shape'] + [p_['shape'][0]]
        strokes += [(a_[0], a_[1], b_[0], b_[1]) for a_, b_ in zip(pts, pts[1:])]

    def seg_hits_box(sg, bx):
        x1, y1, x2, y2 = sg
        bx0, by0, bx1, by1 = bx[0] + 1, bx[1] + 1, bx[2] - 1, bx[3] - 1
        if bx0 >= bx1 or by0 >= by1:
            return False
        # Liang-Barsky clipping
        dx, dy = x2 - x1, y2 - y1
        t0, t1 = 0.0, 1.0
        for p_, q_ in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
            if p_ == 0:
                if q_ < 0:
                    return False
            else:
                t = q_ / float(p_)
                if p_ < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
        return t0 < t1
    for a in T:
        if any(seg_hits_box(sg, a['bbox']) for sg in strokes):
            R['text_on_symbol'].append('"%s"' % a['s'])
    for p in S.get('problems', []):
        R['placement_problem'].append(p)
    nb = 0
    for start in node:
        pass
    out = {'id': S['id'], 'scene_sha': scene_sha(S), 'counts': dict((k, len(R.get(k, []))) for k in CONN_KEYS + QUAL_KEYS),
           'details': dict((k, v[:12]) for k, v in R.items() if v),
           'crossings_drawn': ncross,
           'bends': sum(max(0, len(_corners_of(w['segs']))) for w in S['wires']),
           'labels': sum(1 for l in S['labels'] if not l['gray']),
           'wires': len(S['wires'])}
    out['connectivity_pass'] = all(out['counts'][k] == 0 for k in CONN_KEYS)
    out['quality_pass'] = all(out['counts'][k] == 0 for k in QUAL_KEYS)
    return out


def _corners_of(segs):
    pts = defaultdict(set)
    for s in segs:
        pts[(s[0], s[1])].add('h' if s[1] == s[3] else 'v')
        pts[(s[2], s[3])].add('h' if s[1] == s[3] else 'v')
    return [p for p, o in pts.items() if len(o) == 2]
