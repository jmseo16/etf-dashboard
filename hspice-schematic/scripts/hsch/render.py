"""Scene -> single self-contained HTML file (inline SVG + vanilla JS viewer)."""
from __future__ import annotations

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "..", "assets")


def _f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


def _e(s):
    return html.escape(str(s), quote=True)


def prim_svg(p):
    k = p[0]
    if k == "line":
        return f'<line class="{p[5]}" x1="{_f(p[1])}" y1="{_f(p[2])}" x2="{_f(p[3])}" y2="{_f(p[4])}"/>'
    if k == "polyline":
        pts = " ".join(f"{_f(x)},{_f(y)}" for x, y in p[1])
        return f'<polyline class="{p[2]}" points="{pts}"/>'
    if k == "poly":
        pts = " ".join(f"{_f(x)},{_f(y)}" for x, y in p[1])
        return f'<polygon class="{p[2]}" points="{pts}"/>'
    if k == "circle":
        return f'<circle class="{p[4]}" cx="{_f(p[1])}" cy="{_f(p[2])}" r="{_f(p[3])}"/>'
    if k == "path":
        return f'<path class="{p[2]}" d="{p[1]}"/>'
    if k == "text":
        anc = p[5] if len(p) > 5 else "middle"
        return f'<text class="{p[4]}" x="{_f(p[1])}" y="{_f(p[2])}" text-anchor="{anc}">{_e(p[3])}</text>'
    return ""


def _path_d(prims_path, ox=0, oy=0):
    return prims_path


def scene_svg(sc):
    x0, y0, x1, y1 = sc["bounds"]
    out = [f'<svg class="sch" xmlns="http://www.w3.org/2000/svg" data-cell="{_e(sc["cell"])}" '
           f'viewBox="{_f(x0)} {_f(y0)} {_f(x1 - x0)} {_f(y1 - y0)}" data-bounds="{_f(x0)},{_f(y0)},{_f(x1)},{_f(y1)}">']
    out.append('<g class="layer-wires">')
    for w in sc["wires"]:
        out.append(f'<line class="wire{" diag" if w.get("diag") else ""}" data-net="{_e(w["net"])}" x1="{_f(w["x1"])}" y1="{_f(w["y1"])}" '
                   f'x2="{_f(w["x2"])}" y2="{_f(w["y2"])}"/>')
    out.append("</g>")
    out.append('<g class="layer-syms">')
    for s in sc["symbols"]:
        is_blk = s["kind"] == "X"
        cls = "symg blkg clickable" if is_blk else "symg dev"
        keep = ";".join(",".join(_f(v) for v in r) for r in s.get("keepout", []))
        attrs = f'class="{cls}" data-inst="{_e(s["inst"])}" data-keep="{keep}"'
        if is_blk:
            attrs += f' data-ref="{_e(s["ref"])}" data-hidden="{_e(",".join(s.get("hidden_pins", [])))}"'
            if s.get("body"):
                attrs += f' data-body="{",".join(_f(v) for v in s["body"])}"'
        else:
            attrs += f' data-type="{_e(s["type"])}"'
        out.append(f"<g {attrs}>")
        if is_blk:
            bx0, by0, bx1, by1 = s["bbox"]
            out.append(f'<rect class="hit" x="{_f(bx0)}" y="{_f(by0)}" width="{_f(bx1 - bx0)}" height="{_f(by1 - by0)}"/>')
        for p in s["prims"]:
            out.append(prim_svg(p))
        for (lx, ly, parts, anchor) in s["labels"]:
            spans = "".join(f'<tspan class="{c}">{_e(t)}</tspan>' if c else _e(t) for t, c in parts)
            out.append(f'<text class="devlbl" x="{_f(lx)}" y="{_f(ly)}" text-anchor="{anchor}">{spans}</text>')
        out.append("</g>")
    out.append("</g>")
    out.append('<g class="layer-rails">')
    for r in sc["rails"]:
        out.append(f'<g class="rail" data-net="{_e(r["net"])}" data-ax="{_f(r["x"])}" data-ay="{_f(r["y"])}">')
        for p in r["prims"]:
            out.append(prim_svg(p))
        if r.get("named"):
            out.append(f'<text class="rail-t" x="{_f(r["x"] + 12)}" y="{_f(r["y"] + 16)}">{_e(r["net"])}</text>')
        out.append("</g>")
    out.append("</g>")
    out.append('<g class="layer-dots">')
    for d in sc["dots"]:
        out.append(f'<circle class="dot" data-net="{_e(d["net"])}" cx="{_f(d["x"])}" cy="{_f(d["y"])}" r="2.6"/>')
    out.append("</g>")
    out.append('<g class="layer-labels">')
    for t in sc["terminals"]:
        cls = "term port" if t["port"] else ("term bylabel" if t.get("by_label") else "term")
        out.append(f'<g class="{cls}" data-net="{_e(t["net"])}" data-ax="{_f(t["x"])}" data-ay="{_f(t["y"])}">')
        if (t["port"] or t.get("portsym")) and not t.get("plain"):
            out.append(f'<circle class="termc" cx="{_f(t["x"])}" cy="{_f(t["y"])}" r="3.2"/>')
        if t.get("arrow"):
            x, y = t["x"], t["y"]
            pts = ([(x + 4, y), (x - 5, y - 4), (x - 5, y + 4)] if t["arrow"] == "R"
                   else [(x - 4, y), (x + 5, y - 4), (x + 5, y + 4)])
            out.append('<polygon class="arrowhead" points="' + " ".join(f"{_f(a)},{_f(b)}" for a, b in pts) + '"/>')
        rot = (f' transform="rotate(-90 {_f(t["tx"])} {_f(t["ty"])})" data-rot="1"' if t.get("rot") else "")
        out.append(f'<text class="term-t" x="{_f(t["tx"])}" y="{_f(t["ty"])}" text-anchor="{t["anchor"]}"{rot}>{_e(t["net"])}</text>')
        out.append("</g>")
    for l in sc["labels"]:
        out.append(f'<text class="netlabel {l["cls"]}" data-net="{_e(l["net"])}" data-ax="{_f(l["ax"])}" '
                   f'data-ay="{_f(l["ay"])}" x="{_f(l["x"])}" y="{_f(l["y"])}" text-anchor="{l["anchor"]}">{_e(l["text"])}</text>')
    out.append("</g>")
    out.append('<g class="layer-pins">')
    for p in sc["pins"]:
        out.append(f'<circle class="pin" data-inst="{_e(p["inst"])}" data-pin="{_e(p["pin"])}" '
                   f'data-net="{_e(p["net"])}" cx="{_f(p["x"])}" cy="{_f(p["y"])}" r="2"/>')
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def render_html(scenes, info, title, out_path):
    with open(os.path.join(ASSETS, "viewer.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ASSETS, "viewer.js"), encoding="utf-8") as f:
        js = f.read()
    views = []
    for cell, sc in scenes.items():
        views.append(f'<div class="view" data-cell="{_e(cell)}" hidden>{scene_svg(sc)}</div>')
    data = json.dumps(info, ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)}</title>
<style>{css}</style>
</head>
<body>
<header class="bar">
  <div class="crumbs" id="crumbs"></div>
  <div class="tools">
    <label><input type="checkbox" data-toggle="wl" checked> W/L·m</label>
    <label><input type="checkbox" data-toggle="val" checked> R/C 값</label>
    <label><input type="checkbox" data-toggle="name" checked> 소자 이름</label>
    <label><input type="checkbox" data-toggle="net"> 넷 이름</label>
    <button id="btn-up" title="상위 블록 (Esc)">↑ 상위</button>
    <button id="btn-fit" title="화면 맞춤 (F)">⤢ 맞춤</button>
    <select id="cell-jump" title="셀로 이동"></select>
  </div>
</header>
<main>
  <section class="canvas" id="canvas">
    {''.join(views)}
    <div class="tip" id="tip" hidden></div>
  </section>
  <aside class="side" id="side"></aside>
</main>
<script id="hsch-data" type="application/json">{data}</script>
<script>{js}</script>
</body>
</html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path
