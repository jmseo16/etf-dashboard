"""classify_l1.py <outdir> [post] - hand-derived classification of rx_l1 (rxbyte_top)"""
import json, sys
OUT = sys.argv[1]; POST = len(sys.argv) > 2 and sys.argv[2] == 'post'
C = lambda bus, bits, K, ep, fn, draw, src='최상위 포트 (정적)': dict(bus=bus, bits=bits, K=K, ep=ep, fn=fn, draw=draw, source=src)
rng = lambda n, a, b: ['%s<%d>' % (n, i) for i in range(a, b - 1, -1)]
controls = [
 C('odt_en', ['odt_en'], 'K4', 'xi6/mp2.g', 'ODT 켜기 (odtctl NAND)', '한 줄 → DEC 박스'),
 C('rtt<2:0>', rng('rtt', 2, 0), 'K4', 'xi6/mp2.g', 'ODT 코드 → odtctl → 모든 DQ/DQS 패드의 풀업 다리 PMOS 게이트', '버스 → DEC 박스'),
 C('t1w<2:0>', rng('t1w', 2, 0), 'K1', 'xi30/xi4/mn12.g', 'DFE 탭1 가중치: 스위치 → 탭1 쌍 꼬리, 탭 입력 = 상대 경로 SR latch 출력, 비교기 노드에서 합산', '버스 (SA 위)'),
 C('t2w<1:0>', rng('t2w', 1, 0), 'K1', 'xi30/xi4/mn22.g', 'DFE 탭2 가중치: 탭 입력 = 자기 경로 SR latch 출력', '버스 (SA 위)'),
 C('vrc<5:0>', rng('vrc', 5, 0), 'K6', 'xi2/mp11.g', '비교기 기준 레벨 코드 (VREF DAC): 인버터 → 스위치 PMOS → 분압 저항, 8개 슬라이스가 같은 vref(net204)를 공유', '버스 → VREF 박스'),
 C('rx_en', ['rx_en'], 'K3', 'xi30/xi2/mn6.g', '수신기 켜기: 레벨 시프터(lvlup) → 각 슬라이스 sbamp en/enb, dqsamp·acamp 꼬리 스위치', '한 줄 (분기)'),
 C('slp', ['slp'], 'K3', 'mp0.g', '슬립: 슬라이스 전원(net200) 헤더 스위치', '한 줄'),
 C('gate_open', ['gate_open'], 'K3', 'xi9/xi0/mn0.g', 'DQS 게이트 열기: 클럭 게이트 래치 enable (게이트되는 클럭이 고속이므로 K3)', '한 줄'),
 C('wl_en', ['wl_en'], 'K3', 'xi39/xi0.b', 'WL 검출기 클럭 게이트 enable', '한 줄'),
 C('wl_ck', ['wl_ck'], 'K8', 'xi39/xi2/mn0.g', 'WL 검출 플립플롭 D 입력 (샘플링 대상 신호)', '한 줄 (낮은 확신)'),
]
general = [C('ddl<2:0>', rng('ddl', 2, 0), 'K7', 'xi10/xi1/mn0.g', 'DQS 지연선 탭 선택 (같은 지연 소자의 탭 고르기 = 미세 트림)', '숨김')]
bias = [dict(net='ibias', K='K11', ep='xi1/mn0.g', fn='기준 전류 입력'), dict(net='net203', K='K11', ep='xi2/mp10.g', fn='biasgen 의 vbp → vrefdac 전류원 게이트')]
Q = [
 dict(id='Q1', template='port_role', kind='port_role', rule='§2.7-2', item='wl_ck', question='포트 `wl_ck`는 고속 데이터 입력입니까? (예 / 클럭 / 제어 / 바이어스)',
      assumed='제어 (K8) — 단일 디지털 포트라 §2.4-1 에 따라 데이터가 아님. wldet 플립플롭의 D 입력(DQS 파생 클럭으로 샘플링)이라 명령 한 줄로 그림', confidence='low (역할이 구조로 정해지지 않음)'),
 dict(id='Q2', template='netlist_error_confirm', kind='netlist_error_confirm', rule='§2.7-4', item='xi14/xi15, xi16/xi17, xi18/xi19, xi20/xi21 (ckbuf)',
      fact='같은 입력(net216 등)에서 같은 출력(net218 등)을 두 인스턴스가 함께 구동합니다 (출력 단락)', question='`xi14/xi15, xi16/xi17, xi18/xi19, xi20/xi21 (ckbuf)`: 같은 입력에서 같은 출력을 두 인스턴스가 함께 구동합니다 (출력 단락). netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)',
      assumed='의도됨 (병렬 구동으로 세기 ×2) — 반복 인스턴스로 합쳐 `xi14 … xi15` 로 그림', confidence='low (출력 단락)'),
 dict(id='Q3', template='netlist_error_confirm', kind='netlist_error_confirm', rule='§2.7-4', item='xi38 (dqslice)',
      fact='패드·enable 이 vssq, 탭 코드가 vss, odtb 가 vddq 에 묶이고 출력 net224/net225 가 아무것도 구동하지 않습니다', question='`xi38 (dqslice)`: 입력이 모두 전원에 묶이고 출력이 쓰이지 않습니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)',
      assumed='의도됨 (클럭 부하 맞춤용 더미/복제 슬라이스) — 블록으로 그리고 상수 입력은 회색 선 + 이름표', confidence='low (상수 입력, 출력 미사용)'),
 dict(id='Q4', template='not_in_dictionary', kind='not_in_dictionary', rule='§2.6-3, §2.7-3', item='acamp (dqsrx 안, xi1/xi2)',
      structure='직렬 C + 자기 바이어스 R + 인버터형 증폭기(헤더/풋터 enable)', question='`acamp`: 블록 역할 사전에 없는 구조입니다 (AC 결합 인버터 증폭기). 일반 박스로 그릴까요? (예 / 역할 지정)', assumed='예 — 일반 박스', confidence='low (사전에 없음)'),
 dict(id='Q5', template='not_in_dictionary', kind='not_in_dictionary', rule='§2.6-3, §2.7-3', item='sbamp (dqslice 안, xi2/xi3)',
      structure='게이트가 입력인 PMOS/NMOS 스택 인버터형 증폭기 + 헤더/풋터 enable(en/enb), 두 개가 입력을 맞바꿔 한 쌍', question='`sbamp`: 블록 역할 사전에 없는 구조입니다 (인버터형 단일 입력 증폭기 + enable). 일반 박스로 그릴까요? (예 / 역할 지정)', assumed='예 — 삼각형 "AMP" 일반 박스', confidence='low (사전에 없음)'),
 dict(id='Q6', template='not_in_dictionary', kind='not_in_dictionary', rule='§2.6-3, §2.7-3', item='sadfe (dqslice 안, xi4/xi6)',
      structure='StrongARM 코어 + 탭 쌍 5개(h1: 가중 3개, h2: 가중 2개)가 입력쌍 꼬리 노드에 합산', question='`sadfe`: StrongARM 행의 특징은 모두 있고 합산 탭 쌍이 더 붙었습니다. 비교기(SA) 기호로 그릴까요? (예 / 역할 지정)', assumed='예 — SA 삼각형에 탭 입력(왼쪽)·가중치 버스(위) 핀을 더해 그림', confidence='low (사전 행 확장)'),
 dict(id='Q7', template='netlist_error_confirm', kind='netlist_error_confirm', rule='§2.7-4', item='d0, d1 (ndio_ant)',
      fact='클럭 선(net214, net215)에 vss 로 가는 안테나 다이오드가 붙어 있습니다 (패드가 아닌 곳의 다이오드)', question='`d0, d1`: 클럭 선에 다이오드가 붙어 있습니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)', assumed='의도됨 (안테나 보호) — 클럭 선에 매달린 다이오드 기호 "ESD"로 그림', confidence='low (패드 밖 다이오드)'),
 dict(id='Q8', template='bus_notation_guess', kind='bus_notation_guess', rule='§2.5-7', item='t1w2..0, t2w1..0, vrc5..0, ddl2..0, rtt2..0, dq7..0, qr7..0, qf7..0',
      buses='t1w<2:0>, t2w<1:0>, vrc<5:0>, ddl<2:0>, rtt<2:0>, dq<7:0>, qr<7:0>, qf<7:0>', question='`t1w2…`: 비트 표기가 `<n>`이 아니어서 이름 끝 숫자를 비트 번호로 읽어 t1w<2:0>, t2w<1:0>, vrc<5:0>, ddl<2:0>, rtt<2:0>, dq<7:0>, qr<7:0>, qf<7:0>로 묶었습니다. 맞습니까? (예 / 표기 지정)',
      assumed='예', confidence='low (비트 표기 추측)'),
]
ports = [('dq7..dq0', 'data', '고속 데이터 입력 (ESD + ODT 패드) ×8', '높음'), ('dqs_t, dqs_c', 'clock', '고속 클럭(스트로브) 입력 (ESD + ODT, 클럭 트리를 거쳐 샘플러 클럭 꼬리·리셋에 도달)', '높음'),
 ('qr7..qr0, qf7..qf0', 'hs_out', '고속 출력 ×16', '높음'), ('wl_out', 'O1', '상태 출력 (플립플롭이 구동)', '높음'),
 ('odt_en, rtt<2:0>', 'K4', 'ODT', '높음'), ('t1w<2:0>, t2w<1:0>', 'K1', 'DFE 탭 가중치', '높음'), ('vrc<5:0>', 'K6', 'VREF 코드', '높음'),
 ('rx_en, slp, gate_open, wl_en', 'K3', '켜기', 'rx_en/slp/gate_open 높음, wl_en 높음'), ('wl_ck', 'K8', '낮은 확신 (Q1)', '낮음'),
 ('ddl<2:0>', 'K7 일반', '숨김', '높음'), ('ibias', 'K11', '숨김', '높음'), ('vdd/vddq/vss/vssq', '전원', '숨김', '높음')]
roles = [('padesd', ['dqslice.xi0', 'rxbyte_top.xi4', 'rxbyte_top.xi5'], 'termination_esd', 'RX 종단 · ESD', '박스 "ESD"', 'high', ['다이오드 클램프 + 직렬 R + GGNMOS'], []),
 ('odtleg3', ['dqslice.xi1', 'rxbyte_top.xi6', 'rxbyte_top.xi7'], 'termination', 'RX 종단 (가변)', '입력선 위 가변 종단 R', 'high', ['PMOS 스위치 + R 3다리'], []),
 ('odtctl', ['rxbyte_top.xi3'], 'composite', '공통 복합 블록 (DEC 박스)', 'DEC', 'high', ['nand2x1 ×3 + lvlup ×3'], []),
 ('biasgen', ['rxbyte_top.xi1'], 'bias', '바이어스', '생략', 'high', [], []),
 ('vrefdac', ['rxbyte_top.xi2'], 'dac', '기준 전압 DAC "VREF" 박스', 'VREF', 'high', ['전류원 + 코드 스위치 + 분압 R'], []),
 ('lvlup', ['rxbyte_top.xi0', 'odtctl.xi3..xi5'], 'ls', '공통 레벨 시프터', 'LS', 'high', [], []),
 ('dqsrx', ['rxbyte_top.xi8'], 'composite', '공통 복합 블록 (하위에 사전에 없는 acamp)', '박스', 'low', ['dqsamp(R 부하 차동쌍), invx1, invx4'], ['하위 acamp 가 사전 행 아님']),
 ('dqsamp', ['dqsrx.xi0'], 'ctle?', 'R 부하 차동 증폭기', '삼각형 AMP', 'low', ['R 부하 차동쌍 + 꼬리 스위치/전류원'], ['VGA/CTLE 특징 없음 → 일반 박스']),
 ('acamp', ['dqsrx.xi1', 'dqsrx.xi2'], 'unknown', '사전에 없음', '삼각형 AMP', 'low', [], ['AC 결합 인버터 증폭기']),
 ('dqsgate', ['rxbyte_top.xi9'], 'composite', '공통 복합 블록 (ICG 류)', '박스', 'high', ['lat_tg ×2, nand2x2 ×2, invx4 ×2'], []),
 ('dly3', ['rxbyte_top.xi10', 'xi11'], 'dly', '공통 지연 셀 (DLY)', '박스', 'high', ['dlybuf 체인 + mux2tg 3개'], []),
 ('ckbuf', ['rxbyte_top.xi12..xi23'], 'composite', 'Clock 버퍼 (CMOS 인버터 2단)', '삼각형 BUF', 'high', ['invx4 ×2'], []),
 ('dqslice', ['rxbyte_top.xi30..xi37', 'xi38'], 'composite', '공통 복합 블록 (하위에 sbamp·sadfe 일반/변형)', '박스', 'low', ['padesd, odtleg3, sbamp ×2, sadfe ×2, srnand ×2, inv ×4'], ['하위 sbamp 가 사전 행 아님']),
 ('sbamp', ['dqslice.xi2', 'dqslice.xi3'], 'unknown', '사전에 없음', '삼각형 AMP', 'low', [], ['인버터형 증폭기 + enable']),
 ('sadfe', ['dqslice.xi4', 'dqslice.xi6'], 'comparator', 'RX 비교기·샘플러 (StrongARM) + 탭 쌍', '삼각형 SA + 탭 핀', 'low', ['클럭 꼬리, 입력쌍, cross-coupled NMOS/PMOS, 리셋 PMOS'], ['탭 쌍(합산) — 사전 행 확장']),
 ('srnand', ['dqslice.xi5', 'dqslice.xi7'], 'sr_latch', '공통 SR latch', '박스', 'high', ['nand2x2 ×2 교차 결합'], []),
 ('wldet', ['rxbyte_top.xi39'], 'composite', '공통 복합 블록', '박스', 'high', ['nand2x2, invx4, dfftg, invx1, invx4'], []),
 ('dfftg', ['wldet.xi2'], 'dff', '공통 Latch·DFF (TG DFF)', '박스 DFF', 'high', ['상보 클럭 TG 마스터-슬레이브'], []),
 ('lat_tg', ['dqsgate.xi0', 'dqsgate.xi1'], 'latch', '공통 Latch (TG)', '박스 LATCH', 'high', [], []),
 ('mux2tg', ['dly3.xi1,5,11'], 'mux', '공통 MUX', '사다리꼴 MUX', 'high', ['상보 선택 TG'], []),
 ('invx1/invx4/nand2x1/nand2x2/dlybuf', ['여러 곳'], 'inverter/nand', '공통 논리 게이트', '인버터/박스', 'high', [], []),
 ('rxbyte_top', ['(top)'], 'general', '복합 블록 (예외: 하위에 사전에 없는 블록)', '최상위', 'low', [], ['dqsrx/dqslice 가 사전 밖 하위를 가짐'])]
if POST:
    roles = [r for r in roles]
ann = {'hs_inputs': ['dq<7:0>'], 'clock_inputs': ['dqs_t', 'dqs_c'], 'hs_outputs': ['qr<7:0>', 'qf<7:0>'], 'important_controls': sum([c['bits'] for c in controls], []),
 'show_bias': [], 'hide': sum([c['bits'] for c in general], []) + ['ibias'], 'block_roles': {r[0]: r[2] for r in roles},
 '_sources': {'others': '손으로 읽은 구조 분석 + 가정한 답'}, '_reference_inputs': [],
 '_important_control_buses': {c['bus']: {'bits': c['bits'], 'K': c['K'], 'function': c['fn'], 'endpoint_pin': c['ep'], 'source': 'port'} for c in controls},
 '_general_controls': sum([c['bits'] for c in general], []), '_general_control_buses': {c['bus']: {'bits': c['bits'], 'K': c['K'], 'function': c['fn'], 'endpoint_pin': c['ep'], 'source': 'port'} for c in general},
 '_bias': ['ibias', 'net203'], '_power': ['vdd', 'vddq', 'vss', 'vssq', 'net200 (가상 전원)'], '_omitted_blocks': [{'inst': 'xi1', 'cell': 'biasgen', 'role': 'bias'}],
 '_status_outputs': ['wl_out (O1)'],
 '_non_hs_categories': [{'category': '기준 전압 (P1·VREF)', 'result': 'net204 — vrefdac 가 만든 기준 전압, 코드 vrc<5:0> (K6)'}, {'category': '상태 출력 (O1) · 명령 (K8) · 시험 (K9)', 'result': 'wl_out O1, wl_ck K8(낮음)'}, {'category': '워드 속도 디지털', 'result': '없음'}, {'category': '이득·VREF 코드 (K6)', 'result': 'vrc<5:0>'}],
 '_questions_and_assumed_answers': [dict(q) for q in Q]}
for q in ann['_questions_and_assumed_answers']:
    q['fields'] = {k: v for k, v in q.items() if k in ('item', 'structure', 'fact', 'buses')}
json.dump(ann, open(OUT + '/annotations.json', 'w'), indent=1, ensure_ascii=False)
bd = {'rows': [{'cell': r[0], 'instances': r[1], 'virtual': False, 'role': r[2], 'row': r[3], 'symbol': r[4], 'matched_features': r[6], 'missing_features': r[7], 'confidence': r[5], 'questions': []} for r in roles], 'not_drawn': ['biasgen (xi1)']}
json.dump(bd, open(OUT + '/block_dictionary.json', 'w'), indent=1, ensure_ascii=False)
L = ['# 분류 확인 표 — rxbyte_top (rx_l1)\n', '```',
 '고속 데이터 입력 : dq<7:0> (ESD + ODT 패드 8개)           (확신 높음)', '클럭 입력        : dqs_t, dqs_c                          (확신 높음 — DQS 수신기·게이트·지연·클럭 트리를 거쳐 샘플러 클럭 꼬리/리셋에 도달)',
 '고속 출력        : qr<7:0>, qf<7:0>', '상태 출력        : wl_out (O1)',
 '중요 제어        : odt_en, rtt<2:0> K4 / t1w<2:0>, t2w<1:0> K1 / vrc<5:0> K6 / rx_en, slp, gate_open, wl_en K3 / wl_ck K8 (낮음)',
 '생략             : 제어 3개 (ddl<2:0> K7), 바이어스 2개 (ibias, net203), 전원 (vdd, vddq, vss, vssq, 가상 전원 net200), 블록 1개 (xi1 (biasgen))',
 '질문             : Q1 wl_ck / Q2 ckbuf 출력 단락 / Q3 더미 슬라이스 xi38 / Q4 acamp / Q5 sbamp / Q6 sadfe / Q7 안테나 다이오드 / Q8 버스 표기', '```\n', '## 질문과 가정한 답\n']
for q in Q:
    L += ['- **%s** [%s, %s] %s' % (q['id'], q['template'], q['rule'], q['question']), '  - 확신: ' + q['confidence'], '  - 가정한 답: ' + q['assumed']]
L += ['\n## 규칙이 정한 것 (묻지 않음)\n', '- dictionary_listed_block: invx1, invx4, nand2x1, nand2x2, lvlup(LS), dly3(DLY), srnand(SR latch), lat_tg/dfftg(latch/DFF), mux2tg(MUX) — §2.6-1',
 '- unused_output: xi38 의 qr/qf (net224, net225) — 짧은 선 + 이름표 (§3.5-4)', '- bus_grouping: §2.5-7\n', '## 제어 분류 (K#·끝점 핀·출처)\n', '| 제어 | 비트 | 분류 | K# | 끝점 핀 | 출처 | 기능 | 그림 |', '|---|---|---|---|---|---|---|---|']
for c in controls:
    L.append('| %s | %s | important_control | %s | %s | %s | %s | %s |' % (c['bus'], ', '.join(c['bits']), c['K'], c['ep'], c['source'], c['fn'], c['draw']))
for c in general:
    L.append('| %s | %s | general_control | %s | %s | %s | %s | 숨김 |' % (c['bus'], ', '.join(c['bits']), c['K'], c['ep'], c['source'], c['fn']))
for b in bias:
    L.append('| %s | %s | bias | %s | %s | 바이어스 노드 | %s | 숨김 |' % (b['net'], b['net'], b['K'], b['ep'], b['fn']))
L += ['\n## 비고속 분류 점검\n'] + ['- %s: %s' % (c['category'], c['result']) for c in ann['_non_hs_categories']]
L += ['\n## 최상위 포트 분류\n', '| 포트 | 분류 | 설명 | 확신 |', '|---|---|---|---|'] + ['| %s | %s | %s | %s |' % p for p in ports]
L += ['\n## 블록 역할\n', '| 셀 | 인스턴스 | 역할 | 사전 행 | 확신 |', '|---|---|---|---|---|'] + ['| %s | %s | %s | %s | %s%s |' % (r[0], ', '.join(r[1]), r[2], r[3], r[5], ' — 빠진 특징: ' + '; '.join(r[7]) if r[7] else '') for r in roles]
L += ['\n## netlist 에서 이상하다고 본 곳\n', '- ckbuf 병렬 출력 단락 (Q2), 더미 슬라이스 xi38 (Q3), 안테나 다이오드 (Q7)', '- 상위의 mp0 가 만드는 net200 은 PMOS 벌크로 쓰이는 가상 전원(헤더)이라 전원으로 분류',
      '- dqslice 안 두 sadfe 는 대칭 구조: 한 경로의 h1 = 상대 SR 출력, h2 = 자기 SR 출력 (반속도 2탭 DFE)']
if POST:
    L += ['\n## 검토 뒤 보완 (claude_2_review_classify)\n', '- 명세서 틈: 한 셀 안의 트랜지스터 1개(mp0 헤더)가 가상 전원을 만드는 경우의 그림 규칙 없음 → mp0 를 "PWR SW" 박스로 그리고 net200 은 숨김(전원)으로 둠',
          '- wl_ck K8 는 확신 낮음 유지(질문 Q1). 블록 역할 표의 인스턴스 목록을 계층 경로로 보완', '- 그림 범위: 시험 시간 안에 모든 셀의 화면을 그릴 수 없다고 판단 → 회차 1 에서 그릴 화면 목록을 줄임(보고서에 명시)']
open(OUT + '/classification.md', 'w').write('\n'.join(L) + '\n')
