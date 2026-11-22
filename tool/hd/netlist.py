"""SPICE netlist reader: subcircuits, MOS / R / C / D devices and X instances."""
import re
from collections import OrderedDict

SI = {'t': 1e12, 'g': 1e9, 'meg': 1e6, 'x': 1e6, 'k': 1e3, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'a': 1e-18}


def num(s):
    """'1.2u' -> 1.2e-6, None when s is not a plain number."""
    if s is None:
        return None
    m = re.match(r'^([+-]?\d*\.?\d+(?:e[+-]?\d+)?)(meg|[tgxkmunpfa])?[a-z]*$', str(s).lower())
    if not m:
        return None
    return float(m.group(1)) * (SI[m.group(2)] if m.group(2) else 1.0)


def fmt_si(s):
    """Netlist size string -> short SI text ('3.2e-07' -> '320n'). Unparsable text is returned as is."""
    v = num(s)
    if v is None:
        return str(s)
    if v == 0:
        return '0'
    for suf, mul in (('G', 1e9), ('M', 1e6), ('k', 1e3), ('', 1.0), ('m', 1e-3), ('u', 1e-6), ('n', 1e-9), ('p', 1e-12), ('f', 1e-15)):
        if abs(v) >= mul * 0.9995:
            t = '%.3g' % (v / mul)
            return t + suf
    return '%.3g' % v


class Dev(object):
    __slots__ = ('name', 'kind', 'pins', 'model', 'params', 'value')

    def __init__(self, name, kind, pins, model, params, value=None):
        self.name, self.kind, self.pins, self.model, self.params, self.value = name, kind, pins, model, params, value

    @property
    def mtype(self):
        """'n' or 'p' for a MOS device (from the model name), else ''."""
        if self.kind != 'm':
            return ''
        m = self.model.lower()
        if m.startswith('p') or 'pch' in m or 'pmos' in m or m.startswith('pfet'):
            return 'p'
        return 'n'

    def size_text(self):
        if self.kind == 'm':
            t = '%s/%s' % (fmt_si(self.params.get('w', '?')), fmt_si(self.params.get('l', '?')))
            m = self.params.get('m', '1')
            if m not in ('1', '1.0'):
                t += ' x%s' % m
            return t
        if self.value is not None:
            return fmt_si(self.value)
        if self.kind in ('r', 'c') and self.model:
            return self.model
        return ''


class Cell(object):
    def __init__(self, name, ports):
        self.name, self.ports, self.devs = name, ports, []


def _logical_lines(text):
    out = []
    for raw in text.splitlines():
        ln = raw.rstrip()
        if not ln.strip():
            continue
        s = ln.lstrip()
        if s.startswith('*'):
            continue
        if s.startswith('+') and out:
            out[-1] += ' ' + s[1:]
            continue
        if '$' in s:
            s = s.split('$', 1)[0]
        out.append(s)
    return out


def parse(path):
    """Return (cells OrderedDict name->Cell, globals list). Names are lower-cased."""
    cells, cur, globs = OrderedDict(), None, []
    text = open(path, encoding='utf-8', errors='replace').read()
    for ln in _logical_lines(text):
        tok = ln.split()
        key = tok[0].lower()
        if key == '.subckt':
            ports = [t.lower() for t in tok[2:] if '=' not in t]
            cur = Cell(tok[1].lower(), ports)
            cells[cur.name] = cur
            continue
        if key.startswith('.ends'):
            cur = None
            continue
        if key == '.global':
            globs += [t.lower() for t in tok[1:]]
            continue
        if key.startswith('.'):
            continue
        if cur is None:
            continue
        args = [t for t in tok[1:] if '=' not in t]
        params = dict((t.split('=', 1)[0].lower(), t.split('=', 1)[1]) for t in tok[1:] if '=' in t)
        nm, k = tok[0].lower(), key[0]
        a = [x.lower() for x in args]
        if k == 'm' and len(a) >= 5:
            cur.devs.append(Dev(nm, 'm', OrderedDict(zip('dgsb', a[:4])), a[4], params))
        elif k in 'rc' and len(a) >= 2:
            val, model = None, ''
            for x in a[2:]:
                if num(x) is not None and val is None:
                    val = x
                else:
                    model = x
            if val is None:
                val = params.get(k) or params.get('r') or params.get('c')
            cur.devs.append(Dev(nm, k, OrderedDict((('a', a[0]), ('b', a[1]))), model, params, val))
        elif k == 'd' and len(a) >= 2:
            cur.devs.append(Dev(nm, 'd', OrderedDict((('a', a[0]), ('k', a[1]))), a[2] if len(a) > 2 else '', params))
        elif k == 'x' and len(a) >= 1:
            cur.devs.append(Dev(nm, 'x', a[:-1], a[-1], params))
    # bind instance pins to the port names of the referenced cell
    for c in cells.values():
        for d in c.devs:
            if d.kind == 'x':
                ref = cells.get(d.model)
                if ref is None:
                    raise ValueError('cell %s: instance %s uses undefined subcircuit %s' % (c.name, d.name, d.model))
                if len(ref.ports) != len(d.pins):
                    raise ValueError('cell %s: instance %s has %d nets, %s has %d ports' % (c.name, d.name, len(d.pins), d.model, len(ref.ports)))
                d.pins = OrderedDict(zip(ref.ports, d.pins))
    return cells, globs


def top_cell(cells):
    """The cell nobody instantiates (the last such one when several)."""
    used = set(d.model for c in cells.values() for d in c.devs if d.kind == 'x')
    tops = [n for n in cells if n not in used]
    return tops[-1] if tops else list(cells)[-1]


_BUS = re.compile(r'^(.*?)(?:<(\d+)>|\[(\d+)\]|_(\d+)|(\d+))$')


def bus_split(name):
    """'tap<3>' -> ('tap', 3); 'dq7' -> ('dq', 7); no index -> (name, None)."""
    m = _BUS.match(name)
    if not m or not m.group(1):
        return name, None
    idx = next(g for g in m.groups()[1:] if g is not None)
    stem = m.group(1)
    if m.group(4) is not None:
        stem = stem          # 'w1_2' -> 'w1'
    return stem, int(idx)


def flatten(cells, top):
    """Flat device list: [(path, Dev, {pin: flatnet})]. Local nets of an instance become 'path/net'."""
    out = []

    def walk(cname, prefix, bind):
        c = cells[cname]
        for d in c.devs:
            pm = OrderedDict()
            for p, n in d.pins.items():
                pm[p] = bind.get(n, prefix + n)
            if d.kind == 'x':
                walk(d.model, prefix + d.name + '/', pm)
            else:
                out.append((prefix + d.name, d, pm))
    walk(top, '', dict((p, p) for p in cells[top].ports))
    return out
