# geometry helpers for the rx_s1 checker: orthogonal routes, crossings, line-through-box
def route_pts(m, a, b):
    def center(bx): return (bx['x']+bx['w']/2, bx['y']+bx['h']/2)
    def clip(bx, tx, ty):
        cx, cy = center(bx); dx, dy = tx-cx, ty-cy
        sx = (bx['w']/2)/abs(dx) if dx else 1e9
        sy = (bx['h']/2)/abs(dy) if dy else 1e9
        t = min(sx, sy); return (cx+dx*t, cy+dy*t)
    def pt(n): return m.PORT_POS[n[2:]] if n.startswith('P:') else center(m.BOXES[n])
    pa, pb = pt(a), pt(b)
    if not a.startswith('P:'): pa = clip(m.BOXES[a], *pb)
    if not b.startswith('P:'): pb = clip(m.BOXES[b], *pa)
    (x1,y1),(x2,y2) = pa, pb
    if abs(y1-y2) < 0.5 or abs(x1-x2) < 0.5: return [(x1,y1),(x2,y2)]
    xm = (x1+x2)/2
    return [(x1,y1),(xm,y1),(xm,y2),(x2,y2)]
def all_segments(m):
    out = []
    for a,b,_ in m.EDGES:
        p = route_pts(m,a,b)
        for (x1,y1),(x2,y2) in zip(p,p[1:]): out.append((a,b,(x1,y1,x2,y2)))
    return out
def diagonal_count(m):
    return sum(1 for _,_,(x1,y1,x2,y2) in all_segments(m) if abs(x1-x2)>0.5 and abs(y1-y2)>0.5)
def crossings(m):
    S = all_segments(m); c = 0
    def inter(s,t):
        x1,y1,x2,y2 = s; x3,y3,x4,y4 = t
        if abs(x1-x2)<0.5 and abs(x3-x4)<0.5: return False
        if abs(y1-y2)<0.5 and abs(y3-y4)<0.5: return False
        if abs(x1-x2)<0.5: # s vertical
            if abs(y3-y4)<0.5: return min(x3,x4)<x1<max(x3,x4) and min(y1,y2)<y3<max(y1,y2)
            return False
        if abs(x3-x4)<0.5: return min(x1,x2)<x3<max(x1,x2) and min(y3,y4)<y1<max(y3,y4)
        return False
    for i in range(len(S)):
        for j in range(i+1,len(S)):
            if S[i][0]==S[j][0] and S[i][1]==S[j][1]: continue
            if inter(S[i][2],S[j][2]): c += 1
    return c
def through_box_count(m):
    c = 0
    for a,b,(x1,y1,x2,y2) in all_segments(m):
        for k,bx in m.BOXES.items():
            if k in (a,b): continue
            lx,hx,ly,hy = bx['x'],bx['x']+bx['w'],bx['y'],bx['y']+bx['h']
            if abs(y1-y2)<0.5:
                if ly<y1<hy and min(x1,x2)<hx and max(x1,x2)>lx: c+=1
            else:
                if lx<x1<hx and min(y1,y2)<hy and max(y1,y2)>ly: c+=1
    return c
