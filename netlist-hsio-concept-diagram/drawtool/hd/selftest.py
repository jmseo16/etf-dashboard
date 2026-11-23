"""Error injection: damage a correct scene on purpose and confirm that the verifier reports it."""
import copy
import json
from . import verify as VF


def _first_long_seg(S, minlen=40):
    for wi, w in enumerate(S['wires']):
        for si, s in enumerate(w['segs']):
            if abs(s[0] - s[2]) + abs(s[1] - s[3]) >= minlen:
                return wi, si
    return None


def mutations(S):
    """Yield (name, expected keys, mutated scene)."""
    loc = _first_long_seg(S)
    if loc:
        wi, si = loc
        M = copy.deepcopy(S)
        del M['wires'][wi]['segs'][si]
        yield 'delete a wire piece', ('open', 'dangling_end', 'pin_open'), M
        M = copy.deepcopy(S)
        s = M['wires'][wi]['segs'][si]
        if s[0] == s[2]:
            s[3] = s[3] - 10 if s[3] > s[1] else s[3] + 10
        else:
            s[2] = s[2] - 10 if s[2] > s[0] else s[2] + 10
        yield 'pull a wire end back 10 px', ('open', 'dangling_end', 'pin_open', 'tee_without_dot'), M
        M = copy.deepcopy(S)
        s = M['wires'][wi]['segs'][si]
        if s[0] == s[2]:
            mid = (s[1] + s[3]) // 20 * 10
            M['wires'][wi]['segs'][si:si + 1] = [[s[0], s[1], s[0], mid], [s[0], mid, s[0] + 10, mid], [s[0] + 10, mid, s[0] + 10, mid + 10],
                                                 [s[0] + 10, mid + 10, s[0], mid + 10], [s[0], mid + 10, s[2], s[3]]]
        else:
            mid = (s[0] + s[2]) // 20 * 10
            M['wires'][wi]['segs'][si:si + 1] = [[s[0], s[1], mid, s[1]], [mid, s[1], mid, s[1] + 10], [mid, s[1] + 10, mid + 10, s[1] + 10],
                                                 [mid + 10, s[1] + 10, mid + 10, s[1]], [mid + 10, s[1], s[2], s[3]]]
        yield 'add a needless jog to a straight wire', ('avoidable_bend', 'short_jog', 'crossing', 'text_on_wire', 'wire_through_symbol', 'short', 'tee_without_dot', 'four_way', 'dangling_end'), M
    # a straight wire between two facing pins becomes a 20 px step (one symbol pin moved off the line)
    pin_at = dict(((p['x'], p['y']), (sym['id'], p['side'])) for sym in S['symbols'] for p in sym['pins'])
    for wi, w in enumerate(S['wires']):
        if len(w['segs']) != 1:
            continue
        x1, y1, x2, y2 = w['segs'][0]
        if y1 != y2 or abs(x2 - x1) < 60 or (x1, y1) not in pin_at or (x2, y2) not in pin_at:
            continue
        if x1 > x2:
            x1, x2 = x2, x1
        if pin_at[(x1, y1)][0] == pin_at[(x2, y1)][0] or pin_at[(x1, y1)][1] != 'r' or pin_at[(x2, y1)][1] != 'l':
            continue
        M = copy.deepcopy(S)
        mid = (x1 + x2) // 20 * 10
        M['wires'][wi]['segs'] = [[x1, y1, mid, y1], [mid, y1, mid, y1 + 20], [mid, y1 + 20, x2, y1 + 20]]
        for sym in M['symbols']:
            for p in sym['pins']:
                if (p['x'], p['y']) == (x2, y1):
                    p['y'] = y1 + 20
        yield 'put two facing pins 20 px out of line', ('jog', 'crossing', 'short', 'text_on_wire', 'wire_through_symbol', 'tee_without_dot', 'four_way'), M
        break
    if S['ports']:
        # a symbol drawn further out than a port, in the direction the port points
        M = copy.deepcopy(S)
        p_ = M['ports'][0]
        xs_ = [q[0] for q in p_['shape']]
        ys_ = [q[1] for q in p_['shape']]
        x, y = p_['x'], p_['y']
        if max(xs_) - min(xs_) > max(ys_) - min(ys_):
            dx = -1 if min(xs_) < x else 1
            bx = [x + dx * 60 - 20, y - 20, x + dx * 60 + 20, y + 20]
        else:
            dy = -1 if min(ys_) < y else 1
            bx = [x - 20, y + dy * 60 - 20, x + 20, y + dy * 60 + 20]
        bx = [min(bx[0], bx[2]), min(bx[1], bx[3]), max(bx[0], bx[2]), max(bx[1], bx[3])]
        M['symbols'].append({'id': 'injected', 'kind': 'inst', 'members': [], 'cell': '', 'target': '', 'box': bx,
                             'shapes': [['rect', bx[0], bx[1], bx[2] - bx[0], bx[3] - bx[1]]], 'pins': [], 'x': bx[0], 'y': bx[1]})
        yield 'draw a symbol beyond a port', ('port_facing_in',), M
    if S['dots']:
        M = copy.deepcopy(S)
        del M['dots'][0]
        yield 'remove a junction dot', ('open', 'tee_without_dot', 'dangling_end'), M
    labs = [i for i, l in enumerate(S['labels']) if not l['gray']]
    names = sorted(set(tuple(S['labels'][i]['bits']) for i in labs))
    if len(names) >= 2:
        M = copy.deepcopy(S)
        a = [i for i in labs if tuple(S['labels'][i]['bits']) == names[0]][0]
        M['labels'][a]['bits'] = list(names[1])
        M['labels'][a]['text'] = S['labels'][[i for i in labs if tuple(S['labels'][i]['bits']) == names[1]][0]]['text']
        yield 'rename one net label to another net', ('short', 'open', 'lonely_label', 'width_mismatch'), M
    if len(S['texts']) >= 2:
        M = copy.deepcopy(S)
        a, b = M['texts'][0], M['texts'][1]
        dx, dy = a['bbox'][0] - b['bbox'][0], a['bbox'][1] - b['bbox'][1]
        b['x'] += dx
        b['y'] += dy
        b['bbox'] = [b['bbox'][0] + dx, b['bbox'][1] + dy, b['bbox'][2] + dx, b['bbox'][3] + dy]
        yield 'put one text on top of another', ('text_overlap',), M
    pins = [(sym, p) for sym in S['symbols'] for p in sym['pins'] if p['mode'] == 'wire']
    if len(pins) >= 2:
        M = copy.deepcopy(S)
        syms = [s for s in M['symbols'] if len([p for p in s['pins'] if p['mode'] == 'wire']) >= 2]
        for s in syms:
            ps = [p for p in s['pins'] if p['mode'] == 'wire']
            if ps[0]['bits'] != ps[1]['bits'] and len(ps[0]['bits']) == len(ps[1]['bits']):
                ps[0]['bits'], ps[1]['bits'] = ps[1]['bits'], ps[0]['bits']
                yield 'swap two pins of a symbol', ('short', 'open'), M
                break


def run(scenes, cells, levels):
    """Returns {'injected': n, 'caught': n, 'missed': [...]} over all scenes."""
    res = {'injected': 0, 'caught': 0, 'missed': []}
    for S in scenes:
        cell = cells[S['cell']]
        base = VF.check(S, cell, levels[S['id']])
        for name, keys, M in mutations(S):
            r = VF.check(M, cell, levels[S['id']])
            res['injected'] += 1
            if any(r['counts'].get(k, 0) > base['counts'].get(k, 0) for k in keys):
                res['caught'] += 1
            else:
                res['missed'].append('%s: %s' % (S['id'], name))
    return res
