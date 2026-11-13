"""§8 step 2 confirmation table, §3.5 annotations, omitted summary."""
import json, sys
from collections import Counter, defaultdict
from util import compress

AN = json.load(open('analysis.json')); NL = json.load(open('netlist.json'))['cells']
views = json.load(open('views.json'))
OUT = sys.argv[1]
TOP = AN['top']; ports = NL[TOP]['ports']
LC = AN['local_classes'][TOP]
cls = {p: LC[p] for p in ports}
ctrl_gen = AN['general']; imp = AN['important']
bias_ports = [p for p in ports if 'bias' in cls[p]]
bias_int = sorted(n for n, c in LC.items() if 'bias' in c and n not in ports)
power = [p for p in ports if 'power' in cls[p]]
drawn_ports = AN['data_inputs'] + AN['clock_inputs'] + AN['outputs']

def pn(lst):
    out, seen = [], set()
    for n in lst:
        if n in seen: continue
        for a, b in (('_P', '_N'), ('P', 'N')):
            if n.endswith(a) and n[:-len(a)] + b in lst:
                out.append(n[:-len(a)] + a + '/' + b.lstrip('_')); seen |= {n, n[:-len(a)] + b}; break
        else:
            out.append(n); seen.add(n)
    return out

questions = [
 dict(id='Q1', item='M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2 (DOUT_ODD_P/N ↔ O_DOUTP/N)',
      q='전달 게이트의 NMOS 게이트=VSS, PMOS 게이트=VDD 라 구조상 항상 OFF입니다. O_DOUTP/N을 DFE 탭1 피드백(고속 데이터)으로 볼까요? (예·그림은 TG 그대로 / 아니오·O_DOUT는 구동 없음 / netlist 오류)',
      assumed='예 — O_DOUTP/N = 고속 데이터(부록 A와 일치). 그림은 netlist 그대로 TG 기호로 그리고 "항상 OFF" 경고를 붙임 (선으로 단락시키지 않음).'),
 dict(id='Q2', item='CTLE_STAGE 의 C<0:2> 와 C0_CAP..C2_CAP',
      q='이름은 C 뱅크지만 C0_CAP..C2_CAP는 SP–SN에 직접(항상) 연결되고, C<0:2>는 SP–SN 사이 직렬 MOS 쌍(MC*P–MC*N)만 켭니다. 어떻게 그릴까요? (구조대로 가변 R + 고정 C / 이름대로 가변 C)',
      assumed='구조대로 — R_S(가변) = R_DEG_BASE∥MR<0:2>∥MC<0:2>P-N, C_S(고정) = C_DEG_BASE∥C<0:2>_CAP. C<0:2>는 어느 쪽이든 일반 제어(숨김).'),
 dict(id='Q3', item='STRONGARM_SLICER M11 (PMOS, D=DP, G=DN, S=VDD)',
      q='짝(D=DN, G=DP)이 없는 비대칭 소자입니다. (의도된 비대칭·그대로 그림 / netlist 누락)',
      assumed='그대로 그림(정확성 우선). 대칭 축 밖 P쪽에 두고 비대칭 예외로 표시.'),
 dict(id='Q4', item='CLK_DIST_TREE X_DIV_M / X_DIV_S',
      q='이름은 분주기(DIV)지만 출력→입력 피드백 루프가 없고 X_DIV_M의 데이터 입력이 클럭 B1N/B1P입니다. 블록 종류는? (CML latch 2개 / ÷2 분주기 / I/Q 생성)',
      assumed='CML latch 2개로 그림(구조 우선). CLKI/CLKIB/CLKQ/CLKQB 는 모두 고속 클럭.'),
 dict(id='Q5', item='사전에 없는 블록: HALF_RATE_DFE_SLICE, CLK_DIST_TREE, SR_LATCH, NAND2',
      q='박스(셀 이름) + 보이는 핀만으로 그려도 됩니까? (예 / 역할 지정)',
      assumed='예 — 박스로 그림. 하위 블록은 사전대로(Σ, StrongARM, LATCH, DFF, BUF, INV).'),
 dict(id='Q6', item='부하 없는 고속 넷: CLKQ/CLKQB(최상위), CLKI_BUF 등 INV 체인 출력, QPB/QNB',
      q='추적상 고속 넷이지만 아무 데도 연결되지 않습니다. (그림·이름표로 끝냄 / 생략)',
      assumed='그림 — 생략은 분류(숨김)대로만 허용(§6-3)이라 짧은 선 + 이름표로 끝냄.'),
]
notes = [
 'CTLE_STAGE M_IND_P/N: NMOS인데 S=VDD, B=VDD 로 적혀 있음(전기적 소스는 OUTP). netlist 단자대로 그림 — 분류에는 영향 없음.',
 'X_CTLE1, X_CTLE2 는 같은 C<0:2>, R<0:2> 를 공유.',
 'CML_LATCH, INV 는 데이터 경로(DFE)와 클럭 경로(CLK_DIST_TREE)에 모두 쓰임 → 셀 화면 하나, 선 굵기는 셀 핀 기준(DP/DN/QP/QN 데이터, CLK/CLKB 클럭).',
 '데이터와 클럭 양쪽에서 도달한 넷: 없음.',
]
n_gen = len(ctrl_gen)
lines = [
 '고속 데이터 입력 : %-28s(확신 높음)' % ', '.join(AN['data_inputs']),
 '클럭 입력        : %-28s(확신 높음)' % ', '.join(AN['clock_inputs']),
 '고속 출력        : %s' % ', '.join(pn(AN['outputs'])),
 '중요 제어 (버스) : %s — DFE 탭 계수 (확신 높음)' % ', '.join(compress(imp)),
 '생략             : 제어 %d개 (%s), 바이어스 %d개 (%s), 블록 1개 (BIAS_GEN)' % (
     n_gen, ', '.join(compress(ctrl_gen)), len(bias_ports) + len(bias_int), ', '.join(bias_ports + bias_int)),
 '질문             : %d개 (Q1~Q%d, 아래) — 답을 받을 수 없어 가정한 답으로 진행' % (len(questions), len(questions)),
]
summary = {'lines': lines + [''] + ['%s %s → 가정: %s' % (q['id'], q['item'], q['assumed']) for q in questions],
           'notes': notes}
json.dump(summary, open('summary.json', 'w'), ensure_ascii=False, indent=1)

ann = {'hs_inputs': AN['data_inputs'], 'clock_inputs': AN['clock_inputs'], 'hs_outputs': AN['outputs'],
       'important_controls': compress(imp), 'show_bias': [], 'hide': [],
       'block_roles': {'CTLE_STAGE': 'ctle', 'VGA_STAGE': 'vga', 'DFE_SUMMER': 'summer',
                       'STRONGARM_SLICER': 'strongarm', 'CML_LATCH': 'cml_latch', 'CML_DFF': 'dff',
                       'IDAC_4BIT': 'idac', 'BIAS_GEN': 'bias', 'INV': 'cmos_buffer',
                       'HALF_RATE_DFE_SLICE': 'unknown_box', 'CLK_DIST_TREE': 'unknown_box',
                       'SR_LATCH': 'unknown_box', 'NAND2': 'unknown_box'},
       '_assumed_answers': {q['id']: {'item': q['item'], 'question': q['q'], 'assumed_answer': q['assumed'],
                                      'answered_by': 'assumed (no user available)'} for q in questions},
       '_overrides': {'CTLE_STAGE.degeneration': 'variable_R + fixed_C (Q2)',
                      'CLK_DIST_TREE.X_DIV_M,X_DIV_S': 'cml_latch, not divider (Q4)',
                      'RX_AFE_TOP.M_TIE_*': 'tgate drawn as-is, flagged always-off (Q1)'},
       '_netlist': 'rx_afe_top.sp', '_top': TOP}
json.dump(ann, open(OUT + '/annotations.json', 'w'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ classification.md
br = AN['block_roles']
conf_override = {'SR_LATCH': 'low', 'NAND2': 'low', 'HALF_RATE_DFE_SLICE': 'low', 'CLK_DIST_TREE': 'low'}
sym = {'ctle': '삼각형 CTLE', 'vga': '삼각형 VGA', 'summer': 'Σ', 'strongarm': '삼각형 SA + 클럭', 'cml_latch': '박스 LATCH',
       'dff': '박스 DFF', 'idac': '생략 → 가변 전류원(합산기 안)', 'bias': '생략', 'inv': '작은 삼각형(버퍼)',
       'nand2': '박스 NAND2', 'sr_latch': '박스 SR LATCH', 'composite': '박스(셀 이름)'}
md = ['# 분류 확인 표 — rx_afe_top.sp (top: %s)' % TOP, '',
      '> 계획서 §8 2단계 형식. 사용자에게 물을 수 없어 질문마다 가장 그럴듯한 답을 가정하고 진행했다 (annotations.json `_assumed_answers`).', '',
      '```'] + lines + ['```', '', '## 질문과 가정한 답', '']
md += ['| # | 대상 | 질문 (선택지) | 가정한 답 |', '|---|---|---|---|']
md += ['| %s | %s | %s | %s |' % (q['id'], q['item'], q['q'], q['assumed']) for q in questions]
md += ['', '## 최상위 포트 분류 (37개 → 그림 9개)', '', '| 포트 | 분류 | 그림 |', '|---|---|---|']
for p in ports:
    c = '/'.join(cls[p]); shown = p in drawn_ports or p in imp
    md.append('| %s | %s | %s |' % (p, c, '버스 W<1:4>_<0:3>' if p in imp else ('핀' if shown else '생략')))
md += ['', '## 블록 역할 (§3.4) — 구조 판정 + 이름 힌트', '', '| 셀 | 역할 | 확신 | 구조 근거 | 그림 |', '|---|---|---|---|---|']
for cn, r in br.items():
    md.append('| %s | %s | %s | %s | %s |' % (cn, r['role'], conf_override.get(cn, r['confidence']), r['why'],
                                            '최상위' if cn == TOP else sym.get(r['role'], '')))
md += ['', '## 신호 분류 (최상위 내부 넷 포함)', '']
top_nets = sorted(LC)
for k, title in (('data', '고속 데이터'), ('clock', '고속 클럭'), ('important', '중요 제어'), ('general', '일반 제어'),
                 ('bias', '바이어스/공통모드'), ('power', '전원')):
    md.append('- **%s**: %s' % (title, ', '.join(n for n in top_nets if k in LC[n])))
md += ['', '## 중요 제어 판정 근거 (§3.3)', '']
for p in ['W1_0', 'G0', 'R0', 'C0']:
    i = AN['control'][p]
    md.append('- `%s` → **%s**: %s' % (p, i['verdict'], '; '.join(i['evidence'][:2])))
md += ['', '## 소자 역할 요약 (§3.1, 셀별)', '']
per = defaultdict(lambda: defaultdict(set))
for path, d in AN['device_roles'].items():
    per[d['cell']][d['role']].add(path.split('/')[-1])
for cn in NL:
    if cn in per:
        md.append('- **%s**: ' % cn + '; '.join('%s: %s' % (r, ', '.join(sorted(v))) for r, v in sorted(per[cn].items())))
md += ['', '## 생략 목록 (화면별)', '']
for v in views:
    if v['omitted']:
        md.append('- **%s**: ' % v['id'] + '; '.join('%s (%s)' % (o['item'], o['why']) for o in v['omitted']))
md += ['', '## 참고', ''] + ['- ' + n for n in notes]
open(OUT + '/classification.md', 'w').write('\n'.join(md) + '\n')
print('\n'.join(lines))
