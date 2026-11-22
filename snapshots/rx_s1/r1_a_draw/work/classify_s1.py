"""classify_s1.py - writes classification.md / annotations.json / block_dictionary.json for rx_s1 (hand-derived classification,
structure read from the netlist; see log). usage: classify_s1.py <outdir> [post]   (post = after the classification review)"""
import json, sys
OUT = sys.argv[1]; POST = len(sys.argv) > 2 and sys.argv[2] == 'post'

hs_in = ['pad', 'lb_p', 'lb_n']
clk_in = ['ck', 'ckb']
hs_out = ['dout_e', 'dout_o']
ref = ['vref']

controls = [
    dict(bus='rtt<2:0>', bits=['rtt<2>', 'rtt<1>', 'rtt<0>'], K='K4', ep='xi21/mp2.g', source='최상위 포트 (정적)', cls='important_control',
         fn='ODT 종단 코드: odt_dec(NAND + 레벨 시프터)를 지나 PMOS 스위치 mp2/mp1/mp0 게이트(enb<2:0>) → 패드에 R을 직렬로 거는 스위치', draw='버스 → DEC 박스 → 버스 → 입력선 위 가변 종단 R'),
    dict(bus='odt_en', bits=['odt_en'], K='K4', ep='xi21/mp2.g', source='최상위 포트 (정적)', cls='important_control',
         fn='ODT 전체 켜기(NAND로 rtt와 AND) → 같은 종단 스위치', draw='한 줄 → DEC 박스'),
    dict(bus='tap<3:0>', bits=['tap<3>', 'tap<2>', 'tap<1>', 'tap<0>'], K='K1', ep='xi26/mn10.g', source='최상위 포트 (정적)', cls='important_control',
         fn='DFE 탭 가중치: 스위치(전류 DAC) → 귀환 쌍(hp/hn) 꼬리 전류, 귀환 쌍 입력 = 다른 경로 SR latch 출력(고속 데이터), 출력 노드에서 합산', draw='버스 (Σ 위)'),
    dict(bus='tap_sgn', bits=['tap_sgn'], K='K1', ep='xi26/mn8.g', source='최상위 포트 (정적)', cls='important_control',
         fn='DFE 탭 부호: 인버터 2개를 지나 sgn/sgnb로 귀환 쌍 전류가 outp/outn 어느 쪽으로 가는지 고름', draw='한 줄 → 인버터 → Σ 위 (sgn, sgnb)'),
    dict(bus='lb_en', bits=['lb_en'], K='K2', ep='xi24/mn6.g', source='최상위 포트 (정적)', cls='important_control',
         fn='입력 선택: 패드 쌍(sel_m = rx_en & ~lb_en) 대 루프백 쌍(sel_l = rx_en & lb_en) 중 하나를 켬', draw='한 줄 → 논리 → AMP 위 선택 핀'),
    dict(bus='rx_en', bits=['rx_en'], K='K3', ep='xi26/mn2.g', source='최상위 포트 (정적)', cls='important_control',
         fn='수신기 켜기: Σ 꼬리 스위치(mn2), 클럭 게이트(ck_gbuf NAND), 입력쌍 꼬리 스위치 논리(sel_m/sel_l)', draw='한 줄 (Σ 두 개, CK GATE, 논리로 갈라짐)'),
]
general = [
    dict(bus='ofe_p<1:0>', bits=['ofe_p<1>', 'ofe_p<0>'], K='K7', ep='xi28/mn11.g', source='최상위 포트 (정적)', fn='짝수 경로 SA 입력 노드 C 뱅크 (오프셋 트림)'),
    dict(bus='ofe_n<1:0>', bits=['ofe_n<1>', 'ofe_n<0>'], K='K7', ep='xi28/mn7.g', source='최상위 포트 (정적)', fn='짝수 경로 SA 입력 노드 C 뱅크 (오프셋 트림)'),
    dict(bus='ofo_p<1:0>', bits=['ofo_p<1>', 'ofo_p<0>'], K='K7', ep='xi29/mn11.g', source='최상위 포트 (정적)', fn='홀수 경로 SA 입력 노드 C 뱅크 (오프셋 트림)'),
    dict(bus='ofo_n<1:0>', bits=['ofo_n<1>', 'ofo_n<0>'], K='K7', ep='xi29/mn7.g', source='최상위 포트 (정적)', fn='홀수 경로 SA 입력 노드 C 뱅크 (오프셋 트림)'),
]
bias = [dict(net='ibias', K='K11', ep='xi26/mn3.g', fn='기준 전류 입력 포트 (rx_bias 미러 다이오드 + Σ 꼬리 게이트)'),
        dict(net='net4', K='K11', ep='xi24/mn3.g', fn='rx_bias 가 만든 바이어스 vbn_q → rx_pre 꼬리 게이트')]
power = ['vdd', 'vddq', 'vss', 'vssq']

questions = [
    dict(id='Q1', template='not_in_dictionary', kind='not_in_dictionary', rule='§2.6-3, §2.7-3', item='rx_pre (X xi24)',
         structure='R 부하 의사 차동쌍(mn0/mn1) + 같은 부하를 공유하는 루프백 쌍(mn4/mn5), 쌍마다 꼬리 스위치(mn2, mn6) + 꼬리 전류원, D=S 묶인 MOS 커패시터 2개',
         question='`rx_pre`: 블록 역할 사전에 없는 구조입니다 (R 부하 의사 차동쌍 2개가 한 부하 공유). 일반 박스로 그릴까요? (예 / 역할 지정)',
         assumed='예 — 일반 박스 "AMP"(삼각형, 소자 구성 이름)로 그리고 확신 낮음으로 기록. VGA·CTLE 행의 특징(이득 단 가산 또는 소스 degeneration C)이 없어 사전 기호를 쓰지 않음', confidence='low (사전에 없음)'),
    dict(id='Q2', template='control_class', kind='control_class', rule='§2.7-3', item='rx_en',
         why='끝점이 Σ 꼬리 스위치·클럭 게이트(K3)이면서 입력쌍 선택 논리 sel_m/sel_l(K2 후보)에도 닿음',
         question='`rx_en`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (끝점이 K3(꼬리·클럭 게이트)와 K2(선택 스위치)에 모두 닿음). (K3 켜기 / K2 선택)',
         assumed='K3 켜기 — 같은 신호가 두 입력쌍을 모두 켜고 꺼서 "고르는" 신호가 아님(lb_en이 K2). 어느 쪽이든 그림은 중요 제어 한 줄', confidence='low (K2/K3 경계)'),
    dict(id='Q3', template='control_class', kind='control_class', rule='§2.7-3', item='tap_sgn',
         why='끝점이 귀환 쌍 전류를 outp/outn 으로 돌리는 스위치(부호)',
         question='`tap_sgn`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (부호 스위치: K1 가중치 / K2 선택). (K1 / K2)',
         assumed='K1 — 탭 가중치의 부호이므로 같은 합산 가지의 세기 제어로 봄. 그림은 한 줄', confidence='low (K1/K2 경계)'),
    dict(id='Q4', template='netlist_error_confirm', kind='netlist_error_confirm', rule='§2.7-4', item='rx_pre.mn8, rx_pre.mn9, sa_dt.mn8/mn10/mn12/mn14, dq_rx_unit.mn0',
         fact='MOSFET 의 드레인과 소스가 같은 넷에 묶여 있고 게이트만 신호 노드(MOS 커패시터)입니다. rx_pre의 mn8(게이트 inp, D=S=outp)·mn9(게이트 vref, D=S=outn)는 입력과 반대편 출력을 잇는 교차 커패시터',
         question='`rx_pre.mn8, rx_pre.mn9, sa_dt.mn8/mn10/mn12/mn14, dq_rx_unit.mn0`: MOSFET 의 드레인과 소스가 같은 넷에 묶여 있고 게이트만 신호 노드(MOS 커패시터)입니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)',
         assumed='의도됨(MOS 커패시터) — 커패시터 기호로 그리고 "MOS C"로 표기. rx_pre의 교차 접속은 netlist 대로 그림', confidence='low (D=S 묶인 소자)'),
    dict(id='Q5', template='name_vs_structure', kind='name_vs_structure', rule='§2.6-2, §2.7-2', item='sa_dt.ofp<1:0>, ofn<1:0> (오프셋 코드)',
         structure='스위치(mn7/9/11/13) + D=S MOS 커패시터(mn8/10/12/14) = C 뱅크가 비교기 1단 출력 노드(net62/net63)에 매달림', name='"of" = 오프셋 트림 DAC',
         opt_structure='가변 C 뱅크(출처 포트 = 일반 제어, 숨김)', opt_name='오프셋 전류 DAC',
         question='`sa_dt.ofp<1:0>, ofn<1:0>`: 구조는 스위치로 켜는 C 뱅크인데 이름/기능은 오프셋 트림입니다. (가변 C 뱅크로 / 오프셋 DAC로)',
         assumed='가변 C 뱅크로 — 구조를 따름. 스위치+MOS C 쌍을 개념 기호 가변 C로 묶고 코드는 K7 일반 제어(숨김)', confidence='low (이름-구조 불일치 가능)'),
]
POST_NOTES = []

ports_table = [
    ('pad', 'data', '고속 데이터 입력 (ESD + ODT 종단이 붙은 패드)', '높음'), ('lb_p', 'data', '고속 데이터 입력 (루프백 쌍 +)', '높음'), ('lb_n', 'data', '고속 데이터 입력 (루프백 쌍 −)', '높음'),
    ('vref', 'reference', '기준 (비교기 쪽 입력 = 프리앰프 vref 게이트, RC 필터 뒤)', '높음'), ('ck', 'clock', '고속 클럭 입력', '높음'), ('ckb', 'clock', '고속 클럭 입력', '높음'),
    ('dout_e', 'hs_out', '고속 출력', '높음'), ('dout_o', 'hs_out', '고속 출력', '높음'),
    ('odt_en', 'K4', 'ODT 켜기', '높음'), ('rtt<2:0>', 'K4', 'ODT 코드', '높음'), ('tap<3:0>', 'K1', 'DFE 탭 가중치', '높음'), ('tap_sgn', 'K1', 'DFE 탭 부호', '낮음 (Q3)'),
    ('lb_en', 'K2', '입력 선택', '높음'), ('rx_en', 'K3', '수신기 켜기', '낮음 (Q2)'),
    ('ofe_p<1:0>', 'K7 일반', '오프셋 트림 (숨김)', '높음'), ('ofe_n<1:0>', 'K7 일반', '오프셋 트림 (숨김)', '높음'), ('ofo_p<1:0>', 'K7 일반', '오프셋 트림 (숨김)', '높음'), ('ofo_n<1:0>', 'K7 일반', '오프셋 트림 (숨김)', '높음'),
    ('ibias', 'K11 바이어스', '기준 전류 (숨김)', '높음'), ('vdd/vddq/vss/vssq', '전원', '숨김', '높음')]

roles = [  # (cell, instances, role, dictionary row, symbol, confidence, matched, missing)
    ('esd_dq', ['xi20'], 'termination_esd', 'RX 종단 · ESD', '박스 "ESD" (직렬 R이 있어 입력선 위 표시가 아니라 선 사이 박스, 명세서 틈 → 아래 "막힌 곳")', 'high',
     ['패드에서 전원으로 가는 다이오드 클램프 d0..d3', 'GGNMOS mn0 (게이트 r1로 접지)'], []),
    ('odt_pu', ['xi21'], 'termination', 'RX 종단 · ESD (가변 종단)', '입력선 위 가변 종단 R (§3.4-5)', 'high', ['패드에서 전원(vddq)으로 R + PMOS 스위치 3다리 (이진 가중 60/120/240)'], []),
    ('odt_dec', ['xi22'], 'composite', '공통 복합 블록 (제어 허브·디코더 → DEC 박스)', '박스 "DEC"', 'high', ['하위가 모두 사전: nand2_a ×3, ls_lh ×3'], []),
    ('rx_bias', ['xi23'], 'bias', '공통 바이어스·DAC·디지털 제어', '생략', 'high', ['미러 + 인에이블'], []),
    ('rx_pre', ['xi24'], 'unknown', '사전에 없음 → 일반 박스(삼각형 "AMP")', '삼각형 "AMP" + 질문 Q1', 'low', ['R 부하 차동쌍 2개', '꼬리 스위치+전류원'], ['VGA: 이득 단 가산/degeneration R 코드 없음', 'CTLE: 소스 degeneration C 없음']),
    ('ck_gbuf', ['xi25'], 'composite', '공통 복합 블록', '박스 "CK GATE" (보이는 핀만)', 'high', ['하위가 모두 사전: nand2_c ×2, inv_c ×2'], []),
    ('dfe_sum', ['xi26', 'xi27'], 'summer', 'RX/TX Summer (DFE·FFE)', 'Σ 박스', 'high', ['주 쌍 + 귀환 탭 쌍이 같은 출력에 합산', '탭 전류 = 스위치+꼬리 반복 → 가변 전류원 + 계수 버스 tap<3:0>'], []),
    ('sa_dt', ['xi28', 'xi29'], 'comparator', 'RX 비교기 · 샘플러 (double-tail)', '삼각형 "SA" + 클럭 표시', 'high', ['1단: 클럭 꼬리 + 입력쌍 + 리셋 PMOS', '2단: 헤더(클럭 반전) + 교차 결합 래치 + 1단 출력 입력 NMOS'], []),
    ('sr_nor', ['xi30', 'xi31'], 'sr_latch', '공통 SR latch', '박스', 'high', ['NOR2 2개 교차 결합'], []),
    ('inv_a', ['xi0', 'xi2', 'xi4', 'xi5', 'xi6', 'xi7', 'xi9', 'xi10', 'xi12'], 'inverter', '공통 논리 게이트 (INV)', '인버터', 'high', ['정적 CMOS 인버터'], []),
    ('inv_c', ['xi8', 'xi11'], 'inverter', '공통 논리 게이트 (INV)', '인버터', 'high', ['정적 CMOS 인버터'], []),
    ('nand2_a', ['xi1', 'xi3'], 'nand', '공통 논리 게이트 (NAND)', '박스 + 출력 동그라미', 'high', ['정적 CMOS NAND'], []),
    ('nand2_c', ['xi0', 'xi1'], 'nand', '공통 논리 게이트 (NAND)', '박스 + 출력 동그라미', 'high', ['정적 CMOS NAND'], []),
    ('nor2_c', ['xi0', 'xi1'], 'nor', '공통 논리 게이트 (NOR)', '박스 + 출력 동그라미', 'high', ['정적 CMOS NOR'], []),
    ('ls_lh', ['xi3', 'xi4', 'xi5'], 'ls', '공통 레벨 시프터 (LS)', '박스 "LS"', 'high', ['인버터 + 교차 결합 PMOS 래치 + 출력 인버터 (vdd → vddq)'], []),
    ('dq_rx_unit', ['(top)'], 'general', '공통 복합 블록 (예외: 하위 rx_pre 가 사전에 없음)', '최상위 화면', 'low', ['하위 대부분이 사전'], ['하위 rx_pre 가 사전 행 아님 → 복합 블록 행 조건 불충족']),
    ('(virtual) r0+mn0', ['(top)'], 'lpf', '공통 RC 평균기', '박스 "LPF"', 'high', ['직렬 R + MOS 커패시터(게이트–접지)'], []),
    ('(virtual) sa_dt/stage1', ['xi28', 'xi29'], 'comparator_stage1', '비교기 1단 (가상 블록)', '박스 stage1', 'high', ['클럭 꼬리, 입력쌍, 리셋'], []),
    ('(virtual) sa_dt/stage2', ['xi28', 'xi29'], 'comparator_stage2', '비교기 2단 (가상 블록)', '박스 stage2', 'high', ['헤더, 교차 결합 래치'], []),
]

if POST:
    # review corrections (claude_2_review_classify): complete the instance lists, note the ESD spec gap (not asked: rule gap, drawn as box)
    roles = [list(r) for r in roles]
    for r in roles:
        if r[0] == 'inv_c':
            r[1] = ['dq_rx_unit.xi8', 'dq_rx_unit.xi11', 'sa_dt.xi0', 'ck_gbuf.xi2', 'ck_gbuf.xi3']
        if r[0] == 'nand2_a':
            r[1] = ['dq_rx_unit.xi1', 'dq_rx_unit.xi3', 'odt_dec.xi0', 'odt_dec.xi1', 'odt_dec.xi2']
        if r[0] == 'nand2_c':
            r[1] = ['ck_gbuf.xi0', 'ck_gbuf.xi1']
        if r[0] == 'nor2_c':
            r[1] = ['sr_nor.xi0', 'sr_nor.xi1']
        if r[0] == 'ls_lh':
            r[1] = ['odt_dec.xi3', 'odt_dec.xi4', 'odt_dec.xi5']
        if r[0] == 'inv_a':
            r[1] = ['dq_rx_unit.' + x for x in ['xi0', 'xi2', 'xi4', 'xi5', 'xi6', 'xi7', 'xi9', 'xi10', 'xi12']] + ['rx_bias.xi0 (생략된 블록 안)']
    roles = [tuple(r) for r in roles]
    POST_NOTES = ['esd_dq 는 직렬 R(r0)이 패드와 pad_r 사이에 있어 입력선 위 표시(§2.6-1)로는 연결이 틀어짐 → 선 사이 박스로 그림. 명세서 틈 (규칙이 뜻을 정하지 못함이 아니라 규칙이 없음)으로 기록, 사용자 질문으로 올리지 않음.',
                  '검토 확인: K2/K3/K1 끝점 핀과 출처를 netlist 줄로 다시 확인함 (xi24 mn2/mn6 게이트 = sel_m/sel_l = rx_en·lb_en 논리, xi26 mn2.g = en, xi26 mn8/mn9.g = sgn, mn6/mn7.g = sgnb)',
                  '검토 확인: 블록 역할 표의 인스턴스 목록에 계층 경로를 붙여 완전하게 고침 (검토 전에는 셀마다 첫 곳만 적혀 있었음)']

annotations = {
    'hs_inputs': hs_in, 'clock_inputs': clk_in, 'hs_outputs': hs_out,
    'important_controls': sum([c['bits'] for c in controls], []), 'show_bias': [], 'hide': sum([c['bits'] for c in general], []) + ['ibias'],
    'block_roles': {'esd_dq': 'termination_esd', 'odt_pu': 'termination', 'odt_dec': 'composite', 'rx_bias': 'bias', 'rx_pre': 'unknown', 'ck_gbuf': 'composite', 'dfe_sum': 'summer',
                    'sa_dt': 'comparator', 'sr_nor': 'sr_latch', 'inv_a': 'inverter', 'inv_c': 'inverter', 'nand2_a': 'nand', 'nand2_c': 'nand', 'nor2_c': 'nor', 'ls_lh': 'ls', 'dq_rx_unit': 'general'},
    '_sources': {'hs_inputs': '구조로 판정 (사용자 없음)', 'others': '손으로 읽은 구조 분석 + 가정한 답'},
    '_reference_inputs': ref,
    '_important_control_buses': {c['bus']: {'bits': c['bits'], 'K': c['K'], 'function': c['fn'], 'endpoint_pin': c['ep'], 'source': 'port'} for c in controls},
    '_general_controls': sum([c['bits'] for c in general], []),
    '_general_control_buses': {c['bus']: {'bits': c['bits'], 'K': c['K'], 'function': c['fn'], 'endpoint_pin': c['ep'], 'source': 'port'} for c in general},
    '_bias': ['ibias', 'net4'], '_power': power,
    '_omitted_blocks': [{'inst': 'xi23', 'cell': 'rx_bias', 'role': 'bias'}],
    '_unused_outputs': ['net27 (xi9.y)', 'net29 (xi12.y)'],
    '_non_hs_categories': [
        {'category': '기준 전압 (P1·VREF)', 'result': 'vref — 기준 (프리앰프 vref 게이트, RC 필터 r0+mn0 뒤). ESD가 없어 P1(외부 기준 패드)은 아님, "기준 전압" 규칙 적용 → 회색 선 + 이름표, AMP 왼쪽 둘째 핀'},
        {'category': '상태 출력 (O1) · 명령 (K8) · 시험 (K9)', 'result': '없음'},
        {'category': '워드 속도 디지털', 'result': '없음'},
        {'category': '이득·VREF 코드 (K6)', 'result': '없음'}],
    '_questions_and_assumed_answers': [dict(q, **{'confidence': q['confidence']}) for q in questions],
}
for q in annotations['_questions_and_assumed_answers']:
    q.setdefault('fields', {k: v for k, v in q.items() if k in ('item', 'structure', 'name', 'fact', 'why', 'opt_structure', 'opt_name')})
json.dump(annotations, open(OUT + '/annotations.json', 'w'), indent=1, ensure_ascii=False)

bd = {'_rule': 'plan §2.6-3/4: dictionary row only when every feature of the row is present', 'rows': []}
for cell, inst, role, row, sym, conf, mt, ms in roles:
    bd['rows'].append({'cell': cell, 'instances': inst, 'virtual': cell.startswith('('), 'role': role, 'row': row, 'symbol': sym, 'matched_features': mt, 'missing_features': ms,
                       'confidence': conf, 'questions': ['Q1'] if cell == 'rx_pre' else []})
bd['not_drawn'] = ['rx_bias (xi23)']
json.dump(bd, open(OUT + '/block_dictionary.json', 'w'), indent=1, ensure_ascii=False)

L = []
L.append('# 분류 확인 표 — dq_rx_unit (rx_s1)\n')
L.append('```')
L.append('고속 데이터 입력 : pad (ESD + ODT 패드), lb_p, lb_n (루프백 쌍)     (확신 높음 — 구조: 입력 트랜지스터 게이트 → 샘플러 데이터 입력)')
L.append('클럭 입력        : ck, ckb                                          (확신 높음 — 구조: 샘플러 클럭 꼬리·리셋 게이트까지 도달)')
L.append('기준             : vref (RC 필터 r0+mn0 뒤 프리앰프 둘째 입력)')
L.append('고속 출력        : dout_e, dout_o')
L.append('중요 제어        : rtt<2:0>, odt_en — K4 ODT 종단 / tap<3:0> — K1 DFE 탭 가중치 / tap_sgn — K1 탭 부호 (낮음) / lb_en — K2 입력 선택 / rx_en — K3 켜기 (낮음)')
L.append('생략             : 제어 8개 (ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — K7 정적 트림), 바이어스 2개 (ibias, net4), 전원 4개 (vdd, vddq, vss, vssq), 블록 1개 (xi23 (rx_bias))')
L.append('질문             : Q1 rx_pre / Q2 rx_en / Q3 tap_sgn / Q4 D=S 묶인 MOS / Q5 sa_dt 오프셋 코드')
L.append('```\n')
L.append('## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택)\n')
for q in questions:
    L.append('- **%s** [%s, %s] %s' % (q['id'], q['template'], q['rule'], q['question']))
    L.append('  - 확신: %s' % q['confidence'])
    L.append('  - 가정한 답: %s' % q['assumed'])
L.append('\n## 규칙이 정한 것 (묻지 않음, §2.7-4)\n')
L.append('- dictionary_listed_block: inv_a, inv_c, nand2_a, nand2_c, nor2_c, sr_nor, ls_lh — §2.6-1')
L.append('- unused_output: dq_rx_unit: net27 (xi9.y), net29 (xi12.y) — §3.5-4 (짧은 선 + 이름표)')
L.append('- bus_grouping: rtt<2:0>, tap<3:0>, ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — §2.5-7 (비트 표기가 `<n>`이라 추측 아님)\n')
L.append('## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)\n')
L.append('| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |')
L.append('|---|---|---|---|---|---|---|---|')
for c in controls:
    L.append('| %s | %s | important_control | %s | %s | %s | %s | %s |' % (c['bus'], ', '.join(c['bits']), c['K'], c['ep'], c['source'], c['fn'], c['draw']))
for c in general:
    L.append('| %s | %s | general_control | %s | %s | %s | %s | 숨김 (생략 목록에 한 줄) |' % (c['bus'], ', '.join(c['bits']), c['K'], c['ep'], c['source'], c['fn']))
for b in bias:
    L.append('| %s | %s | bias | %s | %s | 바이어스 노드 | %s | 숨김 |' % (b['net'], b['net'], b['K'], b['ep'], b['fn']))
L.append('\n- rx_en 끝점 핀: Σ 꼬리 스위치 xi26/mn2.g (K3), 클럭 게이트 xi25/xi0.b (K3), 선택 논리 xi24/mn2.g·mn6.g (K2 후보) — Q2')
L.append('- tap_sgn 끝점: 인버터 xi5, xi6 → Σ 의 sgn/sgnb 게이트 xi26/mn8.g, mn9.g, mn6.g, mn7.g — Q3')
L.append('- 정적 트림 ofe/ofo: 끝점 = 비교기 1단 출력 노드의 스위치 게이트, 출처 = 최상위 포트이므로 일반(K7) — 숨김\n')
L.append('## 비고속 분류 점검 (§2.5-9)\n')
for c in annotations['_non_hs_categories']:
    L.append('- %s: %s' % (c['category'], c['result']))
L.append('\n## 최상위 포트 분류\n')
L.append('| 포트 | 분류 | 설명 | 확신 |'); L.append('|---|---|---|---|')
for p in ports_table:
    L.append('| %s | %s | %s | %s |' % p)
L.append('\n## 블록 역할 (§2.6, block_dictionary.json)\n')
L.append('| 셀 | 인스턴스 | 역할 | 사전 행 | 확신 |'); L.append('|---|---|---|---|---|')
for cell, inst, role, row, sym, conf, mt, ms in roles:
    L.append('| %s | %s | %s | %s | %s%s |' % (cell, ', '.join(inst), role, row, conf, ' — 빠진 특징: ' + '; '.join(ms) if ms else ''))
L.append('\n## netlist 에서 이상하다고 본 곳\n')
L.append('- rx_pre mn8 (D=S=outp, G=inp), mn9 (D=S=outn, G=vref): 입력과 반대편 출력을 잇는 교차 MOS 커패시터 (Q4)')
L.append('- sa_dt mn8/mn10/mn12/mn14, dq_rx_unit mn0: D=S 묶인 MOS 커패시터 (Q4, 의도로 보임)')
L.append('- sa_dt 의 mp2 헤더 게이트는 ck 의 반전(net60); 1단 리셋 PMOS(mp0/mp1)는 ck 로 직접 구동 — 정상')
L.append('- dfe_sum 의 sgn/sgnb 는 top 에서 tap_sgn 인버터 두 개로 만들어짐: sgnb = ~tap_sgn(net105), sgn = tap_sgn(net106) — 이름과 반대로 보이지만 netlist 대로')
L.append('- 짝수 경로 Σ(xi26)의 귀환 입력은 홀수 경로 SR(net16/net17), 홀수 경로 Σ(xi27)는 짝수 경로 SR(net14/net15) — 반속도 루프 풀림 구조, 이상 아님')
if POST_NOTES:
    L.append('\n## 검토 뒤 보완 (claude_2_review_classify)\n')
    L += ['- ' + n for n in POST_NOTES]
open(OUT + '/classification.md', 'w').write('\n'.join(L) + '\n')
print('written', OUT)
