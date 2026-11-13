import re
from collections import defaultdict
def compress(names):
    """['W1_0',..,'W4_3'] -> ['W<1:4>_<0:3>'] for full rectangular numeric sets, else unchanged."""
    groups = defaultdict(list)
    for n in names:
        groups[re.sub(r'\d+', '#', n)].append(tuple(int(x) for x in re.findall(r'\d+', n)))
    out = []
    for key, nums in groups.items():
        k = len(nums[0])
        if k == 0 or len(nums) == 1:
            out += [n for n in names if re.sub(r'\d+', '#', n) == key]; continue
        ranges = [sorted({x[i] for x in nums}) for i in range(k)]
        full = 1
        for r in ranges: full *= len(r)
        if full == len(nums) and all(r == list(range(r[0], r[-1] + 1)) for r in ranges):
            s = key
            for r in ranges:
                s = s.replace('#', '<%d:%d>' % (r[0], r[-1]) if len(r) > 1 else str(r[0]), 1)
            out.append(s)
        else:
            out += [n for n in names if re.sub(r'\d+', '#', n) == key]
    return out
def expand(name):
    """'W<1:4>_<0:3>' -> ['W1_0','W1_1',..] (order: first range outermost)."""
    m = re.search(r'<(\d+):(\d+)>', name)
    if not m: return [name]
    a, b = int(m.group(1)), int(m.group(2))
    rng = range(a, b + 1) if a <= b else range(a, b - 1, -1)
    out = []
    for i in rng:
        out += expand(name[:m.start()] + str(i) + name[m.end():])
    return out
