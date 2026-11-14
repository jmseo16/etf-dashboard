"""Plan section 8 step 2: classification confirmation table + questions -> annotations.json, classification.md"""
import json, sys, re, collections
from netlist import parse

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


def cls(n):
    return nc.get(n, ['?'])


hs_in = A['hs_inputs']
clk_in = A['clock_inputs']
hs_out = [p for p in tp if ('data' in cls(p) or 'clock' in cls(p)) and p not in hs_in and p not in clk_in]
imp = [p for p in tp if 'important_control' in cls(p)]
gen = [p for p in tp if 'general_control' in cls(p)]
bias_ports = [p for p in tp if 'bias' in cls(p)]
bias_int = [n for n in internal_top if 'bias' in cls(n)]
power = [p for p in tp if 'power' in cls(p)]


def bus_name(names):
    # group names like W1_0..W4_3 into W<4:1>_<3:0> (structure: same switch type, same function)
    pat = collections.defaultdict(list)
    for n in names:
        m = re.match(r'^(\D*?)(\d+)_(\d+)$', n)
        if m:
            pat[m.group(1)].append((int(m.group(2)), int(m.group(3))))
    out = []
    for k, v in pat.items():
        a = sorted({x for x, _ in v}); b = sorted({y for _, y in v})
        out.append('%s<%d:%d>_<%d:%d>' % (k, a[-1], a[0], b[-1], b[0]))
    return out


imp_bus = bus_name(imp)
blocks = A['block']
omitted_blocks = []
for prefix_list in [A['cell_insts']]:
    pass
# omitted blocks at top level: instances whose cell has no HS net
for e in cells[top]['elems']:
    if e['kind'] == 'inst' and blocks[e['cell']]['symbol'] == 'omit':
        omitted_blocks.append('%s (%s: %s)' % (e['name'], e['cell'], blocks[e['cell']]['role']))

# ---------------- questions (low confidence only) ----------------
Q = []
# control name vs structure
for n, ci in sorted(A['control_info'].items()):
    pass
cmis = [n for n in gen if A['control_info'][n]['bundle_type'] == ['R'] and n[0].upper() == 'C']
if cmis:
    Q.append({'id': 'Q1', 'item': ', '.join(cmis) + ' (CTLE_STAGE)',
              'question': '이름(C*)은 커패시터 뱅크 제어처럼 보이지만, 구조상 스위치 MC*P/MC*N은 SP-C*_MID-SN 직렬 경로(저항 경로)이고 C*_CAP은 SP-SN에 항상 연결된 고정 C입니다. 구조대로 그릴까요? (예: 가변 R + 고정 C / 아니오: 가변 C로)',
              'assumed': '예 — 구조를 따름. C0..C2 스위치는 가변 R 묶음에 포함, C_DEG_BASE+C0_CAP+C1_CAP+C2_CAP은 고정 C 하나(합계 330f)로 그림. C0..C2는 일반 제어(그리지 않음).',
              'confidence': 'low (이름-구조 불일치)'})
for f in A['latch_pairs']:
    if f['name_hint_divider'] and not f['feedback_loop']:
        Q.append({'id': 'Q2', 'item': '%s / %s in %s' % (f['master'], f['slave'], f['cell']),
                  'question': '인스턴스 이름은 ÷2 분주기(DIV)이지만 구조상 귀환 루프가 없습니다 (master의 D 입력 = 자기 클럭 B1N/B1P, slave 출력은 어디로도 되돌아가지 않음). 구조대로 "LATCH 2개 직렬"로 그릴까요? (예 / ÷2로 그림 / netlist 오류)',
                  'assumed': '예 — 구조대로 LATCH 박스 2개와 실제 연결을 그림. ÷2 기호는 쓰지 않음. netlist 오류 가능성을 보고서에 남김.',
                  'confidence': 'low (이름-구조 불일치, 사전의 ÷2 = latch 루프와 불일치)'})
tgs = [g for g in A['groups'].get(top, []) if g['role'] == 'tg']
if tgs:
    Q.append({'id': 'Q3', 'item': ', '.join('/'.join(g['members']) for g in tgs),
              'question': '전달 게이트(NMOS 게이트=VSS, PMOS 게이트=VDD)라 항상 꺼져 있습니다. 그러면 O_DOUTP/N(= X_DFE_EVEN의 탭1 귀환 입력 T1_FB)은 떠 있습니다. 의도된 것입니까? (의도됨 / 연결(항상 ON)이어야 함)',
              'assumed': '끊긴 것으로 처리(계획서 §3.2): TG는 열린 스위치 기호 + "(off)". O_DOUTP/N은 구동이 없지만 X_DFE_EVEN의 고속 핀(T1_FB)에 붙어 있어 고속 데이터로 그리고 이름표로 끝냄.',
              'confidence': 'low (구조상 항상 OFF)'})
for c, s in A['symmetry'].items():
    if s['unmatched_devices']:
        Q.append({'id': 'Q4', 'item': '%s: %s' % (c, ', '.join(s['unmatched_devices'])),
                  'question': '%s에 거울 짝이 없는 소자가 있습니다 (M11: PMOS, S=VDD, D=DP, G=DN; 반대쪽 D=DN, G=DP 소자 없음). 차동 회로가 비대칭이 됩니다. 의도된 것입니까? (의도됨 / netlist 오류)' % c,
                  'assumed': '그대로 그림 (정확성 > 대칭, 계획서 §5.2-7). M11은 연결된 노드(DP) 쪽 바깥에 두고, 게이트(DN)는 이름표로 연결, "비대칭" 표시.' % (),
                  'confidence': 'low (대칭 위반이 netlist에 있음)'})
unknown = [c for c, b in blocks.items() if b['conf'] == 'low' and A['cell_insts'].get(c)]
if unknown:
    Q.append({'id': 'Q5', 'item': ', '.join('%s (%s)' % (c, blocks[c]['role']) for c in unknown),
              'question': '블록 역할 사전에 없는 구조입니다 (정적 CMOS 게이트, 교차 결합 게이트 = SR latch). 박스(셀 이름)로 그릴까요? (예 / 역할 지정)',
              'assumed': '예 — 사전 규칙대로 박스(셀 이름) + 보이는 핀. 유닛 레벨은 소자 그대로.',
              'confidence': 'low (사전에 없음)'})
dang = sorted({n.split('/')[-1] for n in A.get('dangling_hs_nets', [])})
# dangling at the top level: HS nets with a single connection
topconn = collections.Counter()
for e in cells[top]['elems']:
    vals = e['pins'].values() if e['kind'] == 'inst' else e['terms'].values()
    for v in vals:
        topconn[v] += 1
dtop = [n for n in internal_top if ('data' in cls(n) or 'clock' in cls(n)) and topconn[n] == 1]
Q.append({'id': 'Q6', 'item': 'top: %s; CLK_DIST_TREE: CLKI_BUF, CLKIB_BUF, CLKQ_BUF, CLKQB_BUF; STRONGARM_SLICER: QPB, QNB' % ', '.join(dtop),
          'question': '추적상 고속 넷이지만 아무 곳에도 연결되지 않은(부하 없는) 출력입니다. 그릴까요? (그림 / 생략)',
          'assumed': '그림 — 분류가 고속이므로 §6.3(생략은 분류대로만)에 따라 생략하지 않고, 끝에 넷 이름표만 둔 짧은 선으로 표시.',
          'confidence': 'low (계획서에 규칙 없음)'})
Q.append({'id': 'Q7', 'item': ', '.join(imp_bus),
          'question': '중요 제어 16비트(W1_0..W4_3)를 "DFE 탭 계수" 기능 하나의 버스로 묶을까요, 탭별 4비트 버스 4개로 나눌까요? (16b 1개 / 4b×4)',
          'assumed': '16b 버스 1개 (W<4:1>_<3:0>) — §4.4 "기능별 버스 하나"를 "DFE 탭 계수" 기능으로 해석.',
          'confidence': 'low (계획서 해석)'})

ann = {
    'hs_inputs': hs_in, 'clock_inputs': clk_in, 'hs_outputs': hs_out,
    'important_controls': imp, 'show_bias': [], 'hide': [],
    'block_roles': {c: b['role'] for c, b in blocks.items() if A['cell_insts'].get(c)},
    '_sources': {'hs_inputs': 'user answer (given)', 'others': 'automatic structural analysis + assumed answers below'},
    '_important_control_buses': {imp_bus[0]: {'bits': imp, 'function': 'DFE tap 1-4 coefficients (IDAC_4BIT switches -> tap-pair tail current)'}} if imp_bus else {},
    '_general_controls': gen, '_bias': bias_ports + bias_int, '_power': power,
    '_questions_and_assumed_answers': Q,
}
json.dump(ann, open(OUT + '/annotations.json', 'w'), indent=1, ensure_ascii=False)

# --------------- markdown ---------------
L = []
L.append('# 분류 확인 표 — %s\n' % top)
L.append('```')
L.append('고속 데이터 입력 : %-40s (확신 높음 — 사용자 지정, 구조 일치: CTLE 입력쌍 게이트 + 종단/ESD 패드)' % ', '.join(hs_in))
L.append('클럭 입력        : %-40s (확신 높음 — 구조: latch 클럭 스티어링·StrongARM 꼬리/리셋 게이트까지 도달, 이름 일치)' % ', '.join(clk_in))
L.append('고속 출력        : %s' % ', '.join(hs_out))
L.append('중요 제어 (버스) : %s (16b) — DFE 탭1~4 계수 (IDAC 스위치 → 탭 쌍 꼬리 전류, 탭 입력 = 귀환 데이터, summer 출력에서 합산)  (확신 높음; 묶음 방식은 Q7)' % ', '.join(imp_bus))
L.append('생략             : 제어 %d개 (%s), 바이어스 %d개 (%s), 전원 %d개 (%s), 블록 %d개 (%s)' % (
    len(gen), ', '.join(gen), len(bias_ports + bias_int), ', '.join(bias_ports + bias_int), len(power), ', '.join(power),
    len(omitted_blocks), ', '.join(omitted_blocks)))
L.append('질문             : %s' % ' / '.join('%s %s' % (q['id'], q['item']) for q in Q))
L.append('```\n')
L.append('## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택하여 annotations.json에 저장)\n')
for q in Q:
    L.append('- **%s** `%s` — %s\n  - 확신: %s\n  - 가정한 답: %s' % (q['id'], q['item'], q['question'], q['confidence'], q['assumed']))
L.append('\n## 최상위 포트 분류\n')
L.append('| 포트 | 분류 | 근거 |')
L.append('|---|---|---|')
dt = A['data_trace']; ct = A['clock_trace']
def reason(n):
    c = cls(n)
    if n in hs_in:
        return '사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD)'
    if n in clk_in:
        return '클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK)'
    if 'data' in c:
        return '고속 데이터: %s 에서 추적 (via %s)' % ('RX_INP/RX_INN', dt[n]['via'])
    if 'clock' in c:
        return '고속 클럭: CLK_INP/N 에서 추적 (via %s)' % ct[n]['via']
    if 'important_control' in c:
        return '중요 제어: ' + '; '.join(A['control_info'][n]['why'])
    if 'general_control' in c:
        return '일반 제어: ' + '; '.join(A['control_info'][n]['why'][:2]) + (' (이름-구조 불일치 → Q1)' if n in cmis else '')
    if 'bias' in c:
        return '바이어스: ' + A['bias_why'].get(n, '')
    if 'power' in c:
        return '전원 (구조: PMOS/NMOS 벌크 최다 넷)'
    return '?'
for p in tp:
    L.append('| %s | %s | %s |' % (p, '/'.join(cls(p)), reason(p)))
L.append('\n## 최상위 내부 넷 분류\n')
L.append('| 넷 | 분류 | 근거 |')
L.append('|---|---|---|')
for n in internal_top:
    L.append('| %s | %s | %s |' % (n, '/'.join(cls(n)), reason(n)))
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
        L.append('- %s: 핀 %s 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (선 굵기는 데이터 기준, 패널에 주석)' % (c, ', '.join(mixed)))
L.append('\n## 추적 중 멈춘 곳 (요약)\n')
ev = collections.Counter()
for d, why in A['data_events'] + A['clock_events']:
    k = re.sub(r'X_[A-Z0-9_/]+/', '', why)
    ev[(d.split('/')[-1], re.sub(r'(gate|drain|node) \S+', r'\1 *', why))] += 1
for (d, w), k in sorted(ev.items()):
    L.append('- %s: %s (×%d)' % (d, w, k))
open(OUT + '/classification.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:12]))
