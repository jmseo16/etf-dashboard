"""Scene -> SVG text."""
from xml.sax.saxutils import escape


def svg(S, show_size=True):
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Helvetica,Arial,sans-serif">' % (S['w'], S['h'], S['w'], S['h']),
         '<rect width="100%" height="100%" fill="#fff"/>']
    st = 'stroke="#111" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"'

    def shape(v, extra=''):
        k = v[0]
        if k == 'line':
            return '<line x1="%s" y1="%s" x2="%s" y2="%s" %s %s/>' % (v[1], v[2], v[3], v[4], st, extra)
        if k == 'rect':
            return '<rect x="%s" y="%s" width="%s" height="%s" %s %s/>' % (v[1], v[2], v[3], v[4], st, extra)
        if k == 'circle':
            return '<circle cx="%s" cy="%s" r="%s" %s fill="#fff" %s/>' % (v[1], v[2], v[3], st.replace('fill="none"', ''), extra)
        pts = ' '.join('%s,%s' % (x, y) for x, y in v[1])
        if k == 'fpoly':
            return '<polygon points="%s" stroke="#111" stroke-width="1" stroke-linejoin="round" fill="#111" %s/>' % (pts, extra)
        if k == 'poly':
            return '<polygon points="%s" %s fill="#fff" %s/>' % (pts, st.replace('fill="none"', ''), extra)
        return '<polyline points="%s" %s %s/>' % (pts, st, extra)
    for w in S['wires']:
        for s in w['segs']:
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (s[0], s[1], s[2], s[3], st))
    for l in S['labels']:
        if l.get('seg'):
            s = l['seg']
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (s[0], s[1], s[2], s[3], st if not l['gray'] else st.replace('#111', '#888')))
    for t in S['tags']:
        for v in t['shapes']:
            o.append(shape(v))
    for sym in S['symbols']:
        g = ''.join(shape(v) for v in sym['shapes'])
        if sym.get('target'):
            b = sym['box']
            o.append('<g class="hot" data-target="%s" style="cursor:pointer">%s<rect x="%s" y="%s" width="%s" height="%s" fill="#fff" fill-opacity="0.01" stroke="none"/></g>'
                     % (sym['target'], g, b[0], b[1], b[2] - b[0], b[3] - b[1]))
        else:
            o.append(g)
    for x, y, d in S.get('humps', []):
        # the feedback wire is lifted over the wire it crosses: erase 5 px each side, redraw the crossed wire, add the arc
        if d == 'h':
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#fff" stroke-width="3.4"/>' % (x - 5, y, x + 5, y))
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (x, y - 7, x, y + 7, st))
            o.append('<path d="M%s,%s A5,5 0 0 1 %s,%s" %s/>' % (x - 5, y, x + 5, y, st))
        else:
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#fff" stroke-width="3.4"/>' % (x, y - 5, x, y + 5))
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (x - 7, y, x + 7, y, st))
            o.append('<path d="M%s,%s A5,5 0 0 1 %s,%s" %s/>' % (x, y - 5, x, y + 5, st))
    for x, y in S['dots']:
        o.append('<circle cx="%s" cy="%s" r="3" fill="#111"/>' % (x, y))
    for x, y, d in S['slashes']:
        o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (x - 4, y + 5, x + 4, y - 5, st))
    for p in S['ports']:
        o.append(shape(['poly', p['shape']]))
    for T in S['texts']:
        if T['kind'] == 'size' and not show_size:
            continue
        o.append('<text x="%s" y="%s" font-size="%s" text-anchor="%s" fill="%s"%s%s%s pointer-events="none">%s</text>'
                 % (round(T['x'], 1), round(T['y'], 1), T['size'], T['anchor'], T['color'], ' font-style="italic"' if T['italic'] else '',
                    ' font-weight="bold"' if T['bold'] else '', ' class="sz"' if T['kind'] == 'size' else '', escape(T['s'])))
    o.append('</svg>')
    return '\n'.join(o)
