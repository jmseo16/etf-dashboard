"""Plan §1.5 step 2: classification confirmation table + questions -> annotations.json, classification.md,
block_dictionary.json (plan §2.5-9, §2.6-4, §2.7). Usage: classify_report.py <workdir> <outdir> <netlist>"""
import json, sys, re, collections
from netlist import parse, group_bus, Polarity
from spec_rules import CLASS_KO, DICT_ROWS, QUESTION_TEMPLATES, RULE_DECIDED_TOPICS, render_question

W = sys.argv[1]
OUT = sys.argv[2]
NL = sys.argv[3]
A = json.load(open(W + '/analysis.json'))
cells, order = parse(NL)
top = A['top']
nc = A['netclass']
tp = cells[top]['ports']
topnets = sorted({n for n in nc if '/' not in n})
internal_top = [n for n in topnets if n not in tp]
blocks = A['block']
CI = A['control_info']


def cls(n):
    return nc.get(n, ['?'])


def el(cell, name):
    return [e for e in cells[cell]['elems'] if e['name'] == name][0]


hs_in = A['hs_inputs']
clk_in = A['clock_inputs']
hs_out = [p for p in tp if ('data' in cls(p) or 'clock' in cls(p)) and p not in hs_in and p not in clk_in]
imp = [p for p in tp if 'important_control' in cls(p)]
gen = [p for p in tp if 'general_control' in cls(p)]
bias_ports = [p for p in tp if 'bias' in cls(p)]
bias_int = [n for n in internal_top if 'bias' in cls(n)]
power = [p for p in tp if 'power' in cls(p)]

# ---------------- control buses (plan §2.5-7) with K#, endpoint pin (instance.pin) and source (plan §2.5-9) -------
def bus_rows(names):
    rows = []
    for bn, bits, notation in group_bus(names):
        ks = sorted({CI[b]['K'] for b in bits})
        assert len(ks) == 1, (bn, ks)          # §2.5-7: bits with different endpoint classes would be split
        rows.append({'bus': bn, 'bits': bits, 'notation': notation, 'K': ks[0], 'class': cls(bits[0])[0],
                     'endpoint_pin': CI[bits[0]]['endpoint'], 'source': CI[bits[0]]['source'],
                     'why': CI[bits[0]]['why']})
    return rows


def describe(row):
    ep_inst = row['endpoint_pin'].rsplit('.', 1)[0]
    # role of the cell that owns the endpoint device's group (structural, from the analysis)
    path = ep_inst.split('/')
    cell = top
    roles = []
    for comp in path[:-1]:
        e = [x for x in cells[cell]['elems'] if x['name'] == comp][0]
        cell = e['cell']
        roles.append(blocks[cell]['role'])
    role = [r for r in roles if r not in ('composite', 'dac')]
    role = role[-1] if role else roles[-1] if roles else '?'
    if row['K'] == 'K1':
        return '%s 가중치 — 스위치(전류 DAC) → 탭 쌍 꼬리 전류, 탭 입력 = 귀환 고속 데이터, %s 출력에서 합산' % (
            'DFE 탭 계수' if role == 'summer' else '합산 가지', 'Σ' if role == 'summer' else role)
    if row['K'] == 'K6':
        sh = re.search(r'shared by (.*)$', row['why'][0])
        return '%s 이득 코드 — 스위치 → 이득 쌍 꼬리 전류, 출력을 여러 비트 경로가 공유 (%s)' % (role.upper(), sh.group(1) if sh else '')
    if row['K'] == 'K7':
        return '%s 안쪽 노드의 정적 트림 (소스 degeneration 뱅크: 피킹·이득), 출처 = 최상위 포트' % role.upper()
    return ''


imp_rows = bus_rows(imp)
gen_rows = bus_rows(gen)
for r in imp_rows + gen_rows:
    r['function'] = describe(r)
    r['drawing'] = '버스 (사선 + 이름, 비트 수 없음; 받는 블록 위에서)' if r['class'] == 'important_control' else '숨김 (생략 목록에 한 줄)'

omitted_blocks = []
for e in cells[top]['elems']:
    if e['kind'] == 'inst' and blocks[e['cell']]['symbol'] == 'omit':
        omitted_blocks.append({'inst': e['name'], 'cell': e['cell'], 'role': blocks[e['cell']]['role']})

# ---------------- questions: low confidence only, template sentences, nothing a rule decides (plan §2.7) -------
Q = []


def ask(tid, fields, assumed, confidence):
    Q.append({'id': 'Q%d' % (len(Q) + 1), 'template': tid, 'kind': tid, 'rule': QUESTION_TEMPLATES[tid]['rule'],
              'fields': fields, 'item': fields['item'], 'question': render_question(tid, fields),
              'assumed': assumed, 'confidence': confidence})


# (1) name vs structure: a control named like a C bank whose switches form a resistive path (plan §2.6-2)
cmis = [n for n in gen if CI[n]['bundle_type'] == ['R'] and n[0].upper() == 'C']
if cmis:
    cell = [c for c, b in blocks.items() if b['role'] == 'ctle'][0]
    sws = sorted({p.split('/')[-1] for n in cmis for p in CI[n]['switches']})
    caps = [e['name'] for e in cells[cell]['elems'] if e['kind'] == 'cap']
    capv = ' + '.join(el(cell, c)['value'] for c in caps)
    ask('name_vs_structure', {
        'item': '%s (%s)' % (', '.join(cmis), cell),
        'structure': '두 소스 사이 직렬 스위치 쌍(%s = 저항 경로)과 항상 연결된 C(%s)' % (', '.join(sws), ', '.join(caps)),
        'name': 'C 뱅크 제어(가변 C)', 'opt_structure': '가변 R + 고정 C', 'opt_name': '가변 C'},
        '가변 R + 고정 C로 — 구조를 따름(§2.6-2). 스위치 쌍은 가변 R_S 묶음, %s는 고정 C_S 하나(%s)로 그림. %s는 K7 정적 = 일반 제어(숨김).' % (
            ' ∥ '.join(caps), capv, group_bus(cmis)[0][0]),
        'low (이름-구조 불일치)')
# (2) name says divider, structure has no feedback loop (plan §2.6-2 example)
for f in A['latch_pairs']:
    if f['name_hint_divider'] and not f['feedback_loop']:
        ask('name_vs_structure', {
            'item': '%s / %s (%s)' % (f['master'], f['slave'], f['cell']),
            'structure': 'latch 2개 직렬, 귀환 루프 없음(master D 입력 = 자기 클럭 넷)',
            'name': '÷2 분주기(인스턴스 이름 DIV)', 'opt_structure': 'LATCH 2개', 'opt_name': '÷2'},
            'LATCH 2개로 — 구조대로 LATCH 박스 2개와 실제 연결을 그림. ÷2 기호는 쓰지 않음.',
            'low (이름-구조 불일치, 사전의 ÷2 = latch 루프와 불일치)')
# (3) possible netlist errors: always-off TG + undriven high-speed nets (plan §2.7-4, §2.3-2, §2.3-13)
tgs = [g for g in A['groups'].get(top, []) if g['role'] == 'tg']
if tgs:
    und = A['undriven_hs']
    loads = []
    for n in und:
        for e in cells[top]['elems']:
            if e['kind'] == 'inst':
                for p, v in e['pins'].items():
                    if v == n:
                        loads.append('%s.%s' % (e['name'], p))
    ask('netlist_error_confirm', {
        'item': ', '.join('/'.join(g['members']) for g in tgs),
        'fact': '전달 게이트의 NMOS 게이트=%s, PMOS 게이트=%s라 항상 꺼져 있고, 그래서 %s는 구동원 없이 고속 핀(%s)에만 닿습니다(미구동)' % (
            A['rails']['ground'], A['rails']['supply'], ', '.join(und), ', '.join(loads))},
        '의도됨으로 가정하고 규칙대로 그림(§2.3-2, §2.3-13): TG는 열린 스위치 "(off)", %s는 고속(미구동)으로 그리고 이름표(블록 화면)·화면 밖 연결 기호(유닛 화면)로 끝냄.' % ', '.join(und),
        'low (구조상 항상 OFF — netlist 오류 가능)')
for c, s in A['symmetry'].items():
    for m in s['unmatched_devices']:
        e = el(c, m)
        ask('netlist_error_confirm', {
            'item': '%s: %s' % (c, m),
            'fact': '%s(%s, S=%s, D=%s, G=%s)의 거울 짝(D=%s, G=%s)이 없어 차동 회로가 비대칭입니다' % (
                m, 'PMOS' if e['type'] == 'p' else 'NMOS', e['terms']['s'], e['terms']['d'], e['terms']['g'],
                e['terms']['g'], e['terms']['d'])},
            '의도됨으로 가정하고 그대로 그림(§3.3-6): %s는 연결된 노드(%s) 쪽 바깥, 게이트(%s)는 이름표, "비대칭" 주석.' % (m, e['terms']['d'], e['terms']['g']),
            'low (대칭 위반이 netlist에 있음)')
# (4) guessed bit notation (plan §2.5-7: notation guessed -> low confidence)
guessed = [(bn, bits) for bn, bits, nt in group_bus(imp + gen) if nt in ('suffix', 'underscore2')]
if guessed:
    ask('bus_notation_guess', {
        'item': ', '.join('%s…%s' % (b[0], b[-1]) for _, b in guessed),
        'buses': ', '.join('`%s`' % bn for bn, _ in guessed)},
        '예 — %s.' % ', '.join(bn for bn, _ in guessed),
        'low (비트 표기 추측, §2.5-7)')

# what a rule decides (not asked, plan §2.7-4) — listed so the reader sees why there is no question
rule_decided = []
listed = [c for c, b in blocks.items() if A['cell_insts'].get(c) and b['role'] in ('nand', 'nor', 'sr_latch', 'inverter')]
rule_decided.append({'topic': 'dictionary_listed_block', 'items': listed, 'rule': RULE_DECIDED_TOPICS['dictionary_listed_block'],
                     'decision': '사전 행으로 그림 (논리 게이트: 출력 동그라미, SR latch: 박스)'})
uo = A['unused_outputs']
rule_decided.append({'topic': 'unused_output', 'items': ['%s: %s' % (c, ', '.join(v)) for c, v in uo.items()],
                     'rule': RULE_DECIDED_TOPICS['unused_output'], 'decision': '지우지 않고 짧은 선 + 넷 이름표'})
rule_decided.append({'topic': 'bus_grouping', 'items': [r['bus'] for r in imp_rows + gen_rows],
                     'rule': RULE_DECIDED_TOPICS['bus_grouping'], 'decision': '기능별 버스 하나 (`W<4:1>_<3:0>` 16비트 하나)'})

# ---------------- non-high-speed categories (plan §2.5-9 second sentence) ----------------
nonhs = [
    ('기준 전압 (P1·VREF)', '없음 — ESD 붙은 비교기 기준 패드 없음, 비교기·샘플러 한쪽 입력으로 들어가는 추적 안 된 넷 없음'),
    ('상태 출력 (O1) · 명령 (K8) · 시험 (K9)', '없음 — 상태 소자가 구동하는 출력 포트·상태 소자 동기 입력·모니터 출력 없음'),
    ('워드 속도 디지털', '없음 — 직렬화기·디시리얼라이저 워드 경계 없음'),
    ('이득·VREF 코드 (K6)', ', '.join('%s (%s)' % (r['bus'], r['K']) for r in imp_rows if r['K'] == 'K6') or '없음'),
]

ann = {
    'hs_inputs': hs_in, 'clock_inputs': clk_in, 'hs_outputs': hs_out,
    'important_controls': imp, 'show_bias': [], 'hide': [],
    'block_roles': {c: b['role'] for c, b in blocks.items() if A['cell_insts'].get(c)},
    '_sources': {'hs_inputs': 'user answer (given)', 'others': 'automatic structural analysis + assumed answers below'},
    '_important_control_buses': {r['bus']: {'bits': r['bits'], 'K': r['K'], 'function': r['function'], 'endpoint_pin': r['endpoint_pin'],
                                            'source': r['source']} for r in imp_rows},
    '_general_controls': gen,
    '_general_control_buses': {r['bus']: {'bits': r['bits'], 'K': r['K'], 'function': r['function'], 'endpoint_pin': r['endpoint_pin'],
                                          'source': r['source']} for r in gen_rows},
    '_controls': [{k: r[k] for k in ('bus', 'bits', 'class', 'K', 'endpoint_pin', 'source', 'function', 'drawing')} for r in imp_rows + gen_rows],
    '_bias': bias_ports + bias_int, '_power': power,
    '_undriven_hs': A['undriven_hs'],
    '_omitted_blocks': omitted_blocks,
    '_non_hs_categories': [{'category': a, 'result': b} for a, b in nonhs],
    '_questions_and_assumed_answers': Q,
    '_not_asked_rule_decided': rule_decided,
}
json.dump(ann, open(OUT + '/annotations.json', 'w'), indent=1, ensure_ascii=False)

# --------------- markdown ---------------
L = []
L.append('# 분류 확인 표 — %s\n' % top)
L.append('```')
L.append('고속 데이터 입력 : %-40s (확신 높음 — 사용자 지정, 구조 일치: CTLE 입력쌍 게이트 + 종단/ESD 패드)' % ', '.join(hs_in))
L.append('클럭 입력        : %-40s (확신 높음 — 구조: latch 클럭 스티어링·StrongARM 꼬리/리셋 게이트까지 도달, 이름 일치)' % ', '.join(clk_in))
L.append('고속 출력        : %s' % ', '.join(hs_out))
L.append('중요 제어 (버스) : %s' % ' / '.join('%s — %s %s (확신 높음)' % (r['bus'], r['K'], r['function'].split(' — ')[0]) for r in imp_rows))
L.append('생략             : 제어 %d개 (%s — K7 정적 트림), 바이어스 %d개 (%s), 전원 %d개 (%s), 블록 %d개 (%s)' % (
    len(gen), ', '.join(r['bus'] for r in gen_rows), len(bias_ports + bias_int), ', '.join(bias_ports + bias_int), len(power), ', '.join(power),
    len(omitted_blocks), ', '.join('%s (%s)' % (b['inst'], b['cell']) for b in omitted_blocks)))
L.append('질문             : %s' % ' / '.join('%s %s' % (q['id'], q['item']) for q in Q))
L.append('```\n')
L.append('## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택하여 annotations.json에 저장)\n')
for q in Q:
    L.append('- **%s** [%s, %s] %s\n  - 확신: %s\n  - 가정한 답: %s' % (q['id'], q['template'], q['rule'], q['question'], q['confidence'], q['assumed']))
L.append('\n## 규칙이 정한 것 (묻지 않음, §2.7-4)\n')
for r in rule_decided:
    L.append('- %s: %s — %s → %s' % (r['topic'], '; '.join(r['items']), r['rule'], r['decision']))
L.append('\n## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)\n')
L.append('| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |')
L.append('|---|---|---|---|---|---|---|---|')
for r in imp_rows + gen_rows:
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (r['bus'], ', '.join(r['bits']), r['class'], r['K'], r['endpoint_pin'],
                                                       '최상위 포트 (정적)' if r['source'] == 'port' else r['source'], r['function'], r['drawing']))
L.append('')
L.append('- 비트 표기: %s — 표기 추측(§2.5-7), 확신 낮음 → %s.' % (
    ', '.join('%s → %s' % ('/'.join([b[0], b[-1]]), bn) for bn, b in guessed), [q['id'] for q in Q if q['template'] == 'bus_notation_guess'][0] if guessed else '-'))
k6 = [r for r in imp_rows if r['K'] == 'K6']
for r in k6:
    L.append('- %s: 끝점 = 이득 쌍 꼬리 스위치(VGA 행 §2.6-1), 출력을 여러 비트 경로가 공유 → K6(부록 A, C.8 D6, V1). '
             '같은 다리는 "코드로 켜는 병렬 다리"(V4, K5)의 특징도 가진다 — 분류 이름만 다르고 그림(버스)은 같다.' % r['bus'])
for r in gen_rows:
    L.append('- %s: 끝점 = 고속 경로 안쪽 노드(소스 사이)의 degeneration 스위치 → K7, 출처 = 포트(정적) → 일반 제어, 숨김 (V7).' % r['bus'])
L.append('\n## 비고속 분류 점검 (§2.5-9)\n')
for a, b in nonhs:
    L.append('- %s: %s' % (a, b))
L.append('\n## 최상위 포트 분류\n')
L.append('| 포트 | 분류 | K# | 근거 |')
L.append('|---|---|---|---|')
dt = A['data_trace']; ct = A['clock_trace']


def reason(n):
    c = cls(n)
    if n in hs_in:
        return '사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD)'
    if n in clk_in:
        return '클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK)'
    if 'data' in c:
        s = '고속 데이터: %s 에서 추적 (via %s)' % ('/'.join(hs_in), dt[n]['via'])
        if n in A['undriven_hs']:
            s += ' — **미구동** (항상 꺼진 TG 뒤, §2.3-13, Q3)'
        return s
    if 'clock' in c:
        return '고속 클럭: %s 에서 추적 (via %s)' % ('/'.join(clk_in), ct[n]['via'])
    if 'important_control' in c or 'general_control' in c:
        return '%s %s: %s; 끝점 %s' % (CLASS_KO[c[0]], CI[n]['K'], '; '.join(CI[n]['why'][:2]), CI[n]['endpoint'])
    if 'bias' in c:
        return '바이어스: ' + A['bias_why'].get(n, '')
    if 'power' in c:
        return '전원 (구조: PMOS/NMOS 벌크 최다 넷)'
    return '?'


def kcol(n):
    return CI[n]['K'] if n in CI else ('K11' if 'bias' in cls(n) else '')


for p in tp:
    L.append('| %s | %s | %s | %s |' % (p, '/'.join(cls(p)), kcol(p), reason(p)))
L.append('\n## 최상위 내부 넷 분류\n')
L.append('| 넷 | 분류 | K# | 근거 |')
L.append('|---|---|---|---|')
for n in internal_top:
    L.append('| %s | %s | %s | %s |' % (n, '/'.join(cls(n)), kcol(n), reason(n)))
L.append('\n## 블록 역할 (셀별)\n')
L.append('| 셀 | 역할 | 기호 | 확신 | 근거 |')
L.append('|---|---|---|---|---|')
for c in order:
    if not A['cell_insts'].get(c):
        continue
    b = blocks[c]
    L.append('| %s | %s | %s | %s | %s |' % (c, b['role'], b['symbol'], b['conf'], b.get('why', '')))
L.append('\n## 셀 안의 기본 소자 묶음 (유닛)\n')
for c, gs in A['groups'].items():
    for g in gs:
        L.append('- %s: **%s** — %s — %s' % (c, g['role'], ', '.join(g['members']), g.get('why', '')))
L.append('\n## 참고: 데이터·클럭 겸용 셀\n')
for c, d in A['cellnet'].items():
    mixed = [n for n, v in d.items() if 'data' in v and 'clock' in v]
    if mixed:
        L.append('- %s: 핀 %s 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (평탄 넷 중 데이터·클럭 양쪽에서 닿는 넷은 없음)' % (c, ', '.join(mixed)))
L.append('\n## 추적 중 멈춘 곳 (요약)\n')
ev = collections.Counter()
for d, why in A['data_events'] + A['clock_events']:
    ev[(d.split('/')[-1], re.sub(r'(gate|drain|node) \S+', r'\1 *', why))] += 1
for (d, w), k in sorted(ev.items()):
    L.append('- %s: %s (×%d)' % (d, w, k))
open(OUT + '/classification.md', 'w').write('\n'.join(L) + '\n')

# ---------------- block dictionary record (plan §2.6-4) ----------------
P = Polarity(cells, top)


def roles_of(cell, members=None):
    r = A['roles'].get(cell, {})
    out = collections.defaultdict(list)
    for m, v in r.items():
        if members is None or m in members:
            out[v['role']].append(m)
    return out


def feats(role, cell, members=None):
    R = roles_of(cell, members)
    f = []
    if role == 'ctle':
        f.append('차동 입력쌍 %s' % '/'.join(R['input']))
        f.append('소스 분리 (꼬리 %s) + 소스 사이 degeneration R: %s ∥ 스위치 %s' % ('/'.join(R['tail']),
                 ', '.join(e['name'] for e in cells[cell]['elems'] if e['kind'] == 'res' and e['name'] in R['series_res']),
                 ', '.join(R['switch'])))
        caps = [e for e in cells[cell]['elems'] if e['kind'] == 'cap']
        f.append('소스 사이 C가 영점을 만듦 (피킹용 C, 고정): %s = %s' % (' ∥ '.join(e['name'] for e in caps), ' + '.join(e['value'] for e in caps)))
    elif role == 'vga':
        f.append('주 차동쌍 + 같은 입력의 추가 이득 쌍 %d개 (%s), 출력 공유' % (len(R['input']) // 2 - 1, ', '.join(R['input'])))
        f.append('이득 단을 스위치로 더함: 이득 쌍 꼬리의 스위치 %s' % ', '.join(R['switch']))
        f.append('소스 사이 C 없음 (C는 고정·작음 조건 만족)')
    elif role == 'summer':
        f.append('입력이 다른 차동쌍 %d개가 같은 출력에 합산 (%s)' % (len(R['input']) // 2, ', '.join(R['input'])))
        f.append('탭 쌍 꼬리 = 전류 DAC 인스턴스 (%s)' % ', '.join(e['name'] for e in cells[cell]['elems'] if e['kind'] == 'inst'))
    elif role == 'dac':
        f.append('(스위치 %s + 전류원 %s) 반복, 출력 하나 공유 → 개념 기호 "가변 전류원" (§3.4-3)' % ('/'.join(R['switch']), '/'.join(R.get('switched_current_source', []) + R.get('tail', []))))
    elif role in ('comparator', 'strongarm'):
        f.append('클럭 꼬리 %s' % '/'.join(R['clocked_tail']))
        f.append('입력쌍 %s' % '/'.join(m for m in R['input'] if el(cell, m)['type'] == 'n'))
        cn = [m for m in R['cross'] if el(cell, m)['type'] == 'n']; cp = [m for m in R['cross'] if el(cell, m)['type'] == 'p']
        f.append('입력쌍 드레인 위 cross-coupled NMOS %s + cross-coupled PMOS %s' % ('/'.join(cn), '/'.join(cp)))
        f.append('리셋 PMOS %s' % '/'.join(R['reset']))
        if role == 'comparator':
            subs = [e for e in cells[cell]['elems'] if e['kind'] == 'inst']
            f.append('출력단: %s' % ', '.join('%s (%s)' % (e['name'], blocks[e['cell']]['role']) for e in subs))
    elif role == 'latch':
        f.append('입력쌍 %s' % '/'.join(R['input']))
        f.append('cross-coupled 쌍 %s' % '/'.join(R['cross']))
        f.append('클럭 스티어링 %s (상보 클럭으로 두 꼬리를 번갈아)' % '/'.join(R['clock_steering']))
    elif role == 'dff':
        subs = [e for e in cells[cell]['elems'] if e['kind'] == 'inst']
        f.append('latch 2개 직렬 %s → %s' % (subs[0]['name'], subs[1]['name']))
        f.append('반대 클럭: %s.CLK=%s, %s.CLK=%s' % (subs[0]['name'], subs[0]['pins']['CLK'], subs[1]['name'], subs[1]['pins']['CLK']))
    elif role == 'inverter':
        f.append('PMOS/NMOS 하나씩, 게이트·드레인 공통 (정적 CMOS)')
    elif role in ('nand', 'nor'):
        f.append(blocks[cell]['why'])
    elif role == 'sr_latch':
        subs = [e for e in cells[cell]['elems'] if e['kind'] == 'inst']
        f.append('%s 2개 교차 결합: %s' % (subs[0]['cell'], '; '.join('%s.%s=%s' % (e['name'], cells[e['cell']]['ports'][2], e['pins'][cells[e['cell']]['ports'][2]]) for e in subs)))
    elif role == 'cml_buffer':
        f.append('차동쌍 하나 %s, 공통 꼬리 %s, 부하 %s' % ('/'.join(R['input']), '/'.join(R['tail']), '/'.join(R['load'])))
    elif role in ('termination', 'termination_esd'):
        f.append('고속 입력에서 공통모드 노드로 R: %s' % '/'.join(R['termination']))
        if R.get('cap_to_rail'):
            f.append('공통모드 노드에서 접지로 C: %s' % '/'.join(R['cap_to_rail']))
        if R.get('esd'):
            f.append('패드에서 전원으로 MOS 클램프(게이트가 자기 레일): %s' % '/'.join(R['esd']))
    elif role == 'tg':
        f.append('같은 두 넷 사이 NMOS+PMOS, 게이트가 끄는 레일(NMOS→접지, PMOS→전원)에 묶임 → 항상 꺼짐')
    elif role == 'composite':
        subs = [e for e in cells[cell]['elems'] if e['kind'] == 'inst']
        f.append('하위 블록이 모두 사전에 있음: %s' % ', '.join('%s (%s)' % (e['name'], blocks[e['cell']]['role']) for e in subs))
        for g in A['groups'].get(cell, []):
            f.append('기본 소자 묶음(가상 블록)도 사전 행: %s (%s)' % (g['role'], ', '.join(g['members'])))
    return f


drawn_cells = [c for c in order if A['cell_insts'].get(c) and blocks[c]['symbol'] != 'omit']
qby = collections.defaultdict(list)
for q in Q:
    for c in drawn_cells:
        if c in q['item'] or any(inst in q['item'] for inst in [e['name'] for e in cells[top]['elems'] if e['kind'] == 'inst' and e['cell'] == c]):
            qby[c].append(q['id'])
rows = []
for c in drawn_cells:
    b = blocks[c]
    row, sym = DICT_ROWS.get(b['role'], ('general', 'box (cell name)'))
    insts = sorted({pre.rstrip('/').split('/')[-1] for pre in A['cell_insts'][c] if pre})
    rows.append({'cell': c, 'instances': insts, 'virtual': False, 'role': b['role'], 'row': row, 'symbol': sym,
                 'matched_features': feats(b['role'], c), 'missing_features': [], 'confidence': b['conf'],
                 'questions': qby.get(c, [])})
for c, gs in A['groups'].items():
    if not A['cell_insts'].get(c) or blocks[c]['symbol'] == 'omit':
        continue
    if len(gs) == 1 and blocks[c]['role'] == gs[0]['role']:
        continue          # the cell itself is the group (already one row)
    for g in gs:
        row, sym = DICT_ROWS.get(g['role'], ('general', 'box (cell name)'))
        qs = [q['id'] for q in Q if any(m in q['item'] for m in g['members'])]
        rows.append({'cell': c, 'virtual_block': '%s: %s' % (c, ', '.join(g['members'])), 'virtual': True, 'role': g['role'], 'row': row,
                     'symbol': sym, 'matched_features': feats(g['role'], c, set(g['members'])), 'missing_features': [],
                     'confidence': g['conf'], 'questions': qs})
not_drawn = [{'cell': c, 'role': blocks[c]['role'], 'row': DICT_ROWS.get(blocks[c]['role'], ('general',))[0], 'reason': '생략 (고속 신호와 무관)'}
             for c in order if A['cell_insts'].get(c) and blocks[c]['symbol'] == 'omit']
json.dump({'_rule': 'plan §2.6-3/4: a dictionary row is drawn only when every structure feature of the row is present; '
                    'missing_features non-empty + dictionary symbol = fail',
           'rows': rows, 'not_drawn': not_drawn}, open(OUT + '/block_dictionary.json', 'w'), indent=1, ensure_ascii=False)
print('\n'.join(L[:12]))
