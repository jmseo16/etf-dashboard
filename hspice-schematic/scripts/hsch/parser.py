"""HSPICE netlist parser -> hierarchical IR (plain dicts, JSON-serialisable).

IR layout:
{
  "top": "CELL" | null,
  "roots": [...],                      # cells not instantiated by any other cell
  "globals": [...],
  "cells": {
    "CELL": {
      "name": "CELL",
      "ports": ["A", "B", ...],
      "params": {...},
      "devices": [
        {"name": "M1", "kind": "M", "type": "nmos",
         "pins": [["d","OUTP"],["g","INP"],["s","SP"],["b","VSS"]],
         "model": "NCH", "params": {"w": "16u", "l": "45n"}, "ref": null}
        ...
      ]
    }
  },
  "warnings": [...]
}
"""
from __future__ import annotations

import os
import re

TOP_CELL = "__TOP__"

_SI = {
    "t": 1e12, "g": 1e9, "meg": 1e6, "x": 1e6, "k": 1e3, "mil": 25.4e-6,
    "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18,
}
_NUM_RE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)(meg|mil|[tgxkmunpfa])?[a-z]*$", re.I)


def parse_value(text):
    """Parse an HSPICE number with optional SI suffix. Returns float or None."""
    if text is None:
        return None
    s = str(text).strip().strip("'\"")
    m = _NUM_RE.match(s)
    if not m:
        return None
    v = float(m.group(1))
    suf = (m.group(2) or "").lower()
    return v * _SI.get(suf, 1.0)


def _logical_lines(text):
    """Strip comments, join '+' continuation lines. Yields (lineno, line)."""
    out = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("*"):
            continue
        # '$' starts an inline comment (HSPICE) when at start or preceded by whitespace
        line = re.sub(r"(^|\s)\$.*$", "", line)
        # '//' is not HSPICE, but some generators emit it
        if not line.strip():
            continue
        if line.lstrip().startswith("+"):
            if out:
                out[-1] = (out[-1][0], out[-1][1] + " " + line.lstrip()[1:])
            continue
        out.append((i, line.strip()))
    return out


def _tokenize(line):
    # normalise "a = b" -> "a=b", keep quoted expressions together
    line = re.sub(r"\s*=\s*", "=", line)
    tokens, buf, quote = [], "", None
    for ch in line:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            buf += ch
        elif ch in " \t,()":
            if buf:
                tokens.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    return tokens


def _split_params(tokens):
    pos, params = [], {}
    for t in tokens:
        if "=" in t and not t.startswith("="):
            k, v = t.split("=", 1)
            params[k.lower()] = v
        else:
            pos.append(t)
    return pos, params


_PMOS_HINT = re.compile(r"(^p|pch|pmos|pfet|_p\b)", re.I)
_NMOS_HINT = re.compile(r"(^n|nch|nmos|nfet|_n\b)", re.I)


class Netlist:
    def __init__(self):
        self.cells = {}
        self.globals = []
        self.params = {}
        self.models = {}          # model name (lower) -> type (nmos/pmos/...)
        self.warnings = []
        self._canon = {}          # (cell, lower) -> display spelling

    # ---- name canonicalisation (HSPICE is case-insensitive) ----
    def canon(self, cell, name):
        key = (cell if not self._is_global(name) else "*", name.lower())
        if key not in self._canon:
            self._canon[key] = name
        return self._canon[key]

    def _is_global(self, name):
        return name.lower() in {g.lower() for g in self.globals} or name == "0"

    def new_cell(self, name, ports, params):
        cell = {"name": name, "ports": ports, "params": params, "devices": []}
        self.cells[name] = cell
        return cell


def parse_file(path, mos_type_map=None):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return parse_text(text, base_dir=os.path.dirname(os.path.abspath(path)), mos_type_map=mos_type_map)


def parse_text(text, base_dir=".", mos_type_map=None):
    nl = Netlist()
    mos_type_map = {k.lower(): v for k, v in (mos_type_map or {}).items()}
    lines = _logical_lines(text)
    _expand_includes(lines, base_dir, nl)

    # first pass: globals and models so canonicalisation / typing works
    for _, line in lines:
        low = line.lower()
        if low.startswith(".global"):
            nl.globals.extend(_tokenize(line)[1:])
        elif low.startswith(".model"):
            toks = _tokenize(line)
            if len(toks) >= 3:
                nl.models[toks[1].lower()] = toks[2].lower()

    cur = None
    top_devices = []
    for lineno, line in lines:
        toks = _tokenize(line)
        if not toks:
            continue
        head = toks[0].lower()
        if head.startswith("."):
            if head in (".subckt", ".macro"):
                pos, params = _split_params(toks[1:])
                pos = [p for p in pos if p.lower() not in ("params:", "param:")]
                if not pos:
                    nl.warnings.append(f"{lineno}번째 줄: 이름 없는 .SUBCKT")
                    continue
                name = pos[0]
                cur = nl.new_cell(name, [], params)
                cur["ports"] = [nl.canon(name, p) for p in pos[1:]]
            elif head in (".ends", ".eom"):
                cur = None
            elif head == ".param":
                _, params = _split_params(toks[1:])
                (cur["params"] if cur else nl.params).update(params)
            # other dot-cards (.global/.model/.option/.end/.temp/...) are ignored here
            continue
        cell_name = cur["name"] if cur else TOP_CELL
        dev = _parse_element(toks, cell_name, nl, mos_type_map, lineno)
        if dev is None:
            continue
        (cur["devices"] if cur else top_devices).append(dev)

    if top_devices:
        nl.new_cell(TOP_CELL, [], {})["devices"] = top_devices

    # resolve subckt instance pin names
    for cell in nl.cells.values():
        for d in cell["devices"]:
            if d["kind"] != "X":
                continue
            ref = _find_cell(nl, d["ref"])
            if ref is None:
                nl.warnings.append(f"{cell['name']}/{d['name']}: 정의되지 않은 subckt '{d['ref']}' (빈 블록으로 처리)")
                d["pins"] = [[f"p{i+1}", n] for i, (_, n) in enumerate(d["pins"])]
                continue
            d["ref"] = ref["name"]
            nets = [n for _, n in d["pins"]]
            if len(nets) != len(ref["ports"]):
                nl.warnings.append(
                    f"{cell['name']}/{d['name']}: 노드 {len(nets)}개, {ref['name']} 포트는 {len(ref['ports'])}개")
            d["pins"] = [[ref["ports"][i] if i < len(ref["ports"]) else f"p{i+1}", n] for i, n in enumerate(nets)]

    instantiated = {d["ref"] for c in nl.cells.values() for d in c["devices"] if d["kind"] == "X"}
    roots = [c for c in nl.cells if c not in instantiated]
    top = TOP_CELL if TOP_CELL in nl.cells else (_pick_top(nl, roots) if roots else None)
    return {
        "top": top,
        "roots": roots,
        "globals": nl.globals,
        "params": nl.params,
        "cells": nl.cells,
        "warnings": nl.warnings,
    }


def _expand_includes(lines, base_dir, nl, depth=0):
    i = 0
    while i < len(lines):
        lineno, line = lines[i]
        low = line.lower()
        if low.startswith(".include") or low.startswith(".inc ") or (low.startswith(".lib") and len(_tokenize(line)) == 2):
            toks = _tokenize(line)
            path = toks[1].strip("'\"") if len(toks) > 1 else ""
            full = os.path.join(base_dir, path)
            if depth < 8 and path and os.path.isfile(full):
                with open(full, encoding="utf-8", errors="replace") as f:
                    sub = _logical_lines(f.read())
                _expand_includes(sub, os.path.dirname(full), nl, depth + 1)
                lines[i:i + 1] = sub
                i += len(sub)
                continue
            nl.warnings.append(f"{lineno}번째 줄: include 파일 '{path}' 없음 (무시)")
        i += 1


def _find_cell(nl, name):
    for c in nl.cells.values():
        if c["name"].lower() == str(name).lower():
            return c
    return None


def _pick_top(nl, roots):
    def depth(name, seen=()):
        cell = nl.cells[name]
        subs = [d["ref"] for d in cell["devices"] if d["kind"] == "X" and d["ref"] in nl.cells and d["ref"] not in seen]
        return 1 + max((depth(s, seen + (name,)) for s in subs), default=0)
    return max(roots, key=lambda r: (depth(r), len(nl.cells[r]["devices"])))


def _mos_type(model, nl, mos_type_map):
    m = model.lower()
    if m in mos_type_map:
        return mos_type_map[m]
    mt = nl.models.get(m, "")
    if mt in ("pmos", "nmos"):
        return mt
    if _PMOS_HINT.search(model):
        return "pmos"
    if _NMOS_HINT.search(model):
        return "nmos"
    nl.warnings.append(f"모델 '{model}': NMOS/PMOS 구분 불가, NMOS로 가정 (mos_types에 지정하세요)")
    return "nmos"


def _parse_element(toks, cell, nl, mos_type_map, lineno):
    name = toks[0]
    letter = name[0].upper()
    pos, params = _split_params(toks[1:])
    C = lambda n: nl.canon(cell, n)

    def dev(kind, typ, pins, model=None, ref=None):
        return {"name": name, "kind": kind, "type": typ,
                "pins": [[p, C(n)] for p, n in pins],
                "model": model, "params": params, "ref": ref, "line": lineno}

    try:
        if letter == "M":
            if len(pos) < 5:
                raise ValueError("MOSFET needs 4 nodes + model")
            d, g, s, b, model = pos[:5]
            return dev("M", _mos_type(model, nl, mos_type_map), [("d", d), ("g", g), ("s", s), ("b", b)], model=model)
        if letter in "RCL":
            if len(pos) < 2:
                raise ValueError("2 nodes required")
            typ = {"R": "res", "C": "cap", "L": "ind"}[letter]
            key = {"R": "r", "C": "c", "L": "l"}[letter]
            model = None
            if len(pos) >= 3:
                if parse_value(pos[2]) is not None or pos[2].startswith("'"):
                    params.setdefault(key, pos[2])
                else:
                    model = pos[2]
                    if len(pos) >= 4:
                        params.setdefault(key, pos[3])
            return dev(letter, typ, [("p", pos[0]), ("n", pos[1])], model=model)
        if letter in "VI":
            if len(pos) < 2:
                raise ValueError("2 nodes required")
            rest = " ".join(pos[2:])
            if rest:
                params.setdefault("value", rest)
            return dev(letter, "vsrc" if letter == "V" else "isrc", [("p", pos[0]), ("n", pos[1])])
        if letter in "EG":
            if len(pos) < 4:
                raise ValueError("4 nodes required")
            if len(pos) > 4:
                params.setdefault("gain", pos[4])
            return dev(letter, "vcvs" if letter == "E" else "vccs",
                       [("p", pos[0]), ("n", pos[1]), ("cp", pos[2]), ("cn", pos[3])])
        if letter in "FH":
            if len(pos) < 3:
                raise ValueError("2 nodes + vsrc required")
            params.setdefault("vctrl", pos[2])
            return dev(letter, "cccs" if letter == "F" else "ccvs", [("p", pos[0]), ("n", pos[1])])
        if letter == "D":
            return dev("D", "diode", [("a", pos[0]), ("k", pos[1])], model=pos[2] if len(pos) > 2 else None)
        if letter == "Q":
            pins = [("c", pos[0]), ("b", pos[1]), ("e", pos[2])]
            model = pos[3] if len(pos) > 3 else None
            return dev("Q", "bjt", pins, model=model)
        if letter == "X":
            if len(pos) < 2:
                raise ValueError("subckt instance needs nodes + name")
            ref = pos[-1]
            return dev("X", "inst", [(f"p{i+1}", n) for i, n in enumerate(pos[:-1])], ref=ref)
    except (ValueError, IndexError) as e:
        nl.warnings.append(f"{lineno}번째 줄: '{name}' 해석 실패: {e}")
        return None
    nl.warnings.append(f"{lineno}번째 줄: 지원하지 않는 소자 '{name}' (무시)")
    return None
