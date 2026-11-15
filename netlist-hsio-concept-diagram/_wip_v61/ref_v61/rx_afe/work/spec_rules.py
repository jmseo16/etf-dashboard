"""Spec-derived constants shared by analysis, report, layout and verification (DRAWING_PLAN v6 + v6.1 decisions).
Nothing here names a net, cell or instance of a particular netlist."""

# ---------------- signal classes (plan §2.5-4) -> label used in every table / panel ----------------
CLASS_KO = {
    'data': '고속 데이터', 'clock': '고속 클럭', 'important_control': '중요 제어', 'general_control': '일반 제어',
    'bias': '바이어스', 'power': '전원', 'internal': '내부', 'unused': '미사용',
}
HIDDEN_CLASSES = {'general_control', 'bias', 'power'}
VISIBLE_CLASSES = {'data', 'clock', 'important_control'}

# endpoint table (plan §2.5-5) — K#: (class, drawing)
K_TABLE = {
    'K1': ('important_control', '버스'), 'K2': ('important_control', '선택 핀까지 선'), 'K3': ('important_control', '한 줄/버스'),
    'K4': ('important_control', '버스'), 'K5': ('important_control', '버스'), 'K6': ('important_control', '버스'),
    'K7L': ('important_control', '버스'), 'K7': ('general_control', '숨김'), 'K8': ('command', '한 줄'),
    'K9': ('test', '한 줄'), 'K10': ('general_control', '숨김'), 'K11': ('bias', '숨김'),
}

# ---------------- block dictionary (plan §2.6-1) ----------------
# analysis role -> (dictionary row, block symbol)
DICT_ROWS = {
    'termination': ('RX 종단 · ESD', '입력선 위 R/ESD 표시'),
    'termination_esd': ('RX 종단 · ESD', '입력선 위 R/ESD 표시'),
    'ctle': ('RX CTLE', '삼각형 "CTLE"'),
    'vga': ('RX VGA', '삼각형 "VGA"'),
    'tia': ('RX TIA', '삼각형 "TIA"'),
    'summer': ('RX/TX Summer (DFE·FFE)', 'Σ'),
    'strongarm': ('RX 비교기 · 샘플러 (StrongARM)', '삼각형 + 클럭'),
    'comparator': ('RX 비교기 · 샘플러 (StrongARM)', '삼각형 + 클럭'),
    'latch': ('공통 Latch · DFF (latch)', '박스 LATCH'),
    'dff': ('공통 Latch · DFF (DFF)', '박스 DFF'),
    'cml_buffer': ('Clock 버퍼 (CML)', '삼각형 "BUF"'),
    'inverter': ('공통 논리 게이트 (INV)', '인버터'),
    'nand': ('공통 논리 게이트 (NAND)', '박스(셀 이름) + 출력 동그라미'),
    'nor': ('공통 논리 게이트 (NOR)', '박스(셀 이름) + 출력 동그라미'),
    'sr_latch': ('공통 SR latch', '박스(셀 이름)'),
    'dac': ('공통 바이어스 · DAC · 디지털 제어 (전류 DAC → 개념 기호 가변 전류원, §3.4-3)', '가변 전류원(부모 유닛 화면)'),
    'bias': ('공통 바이어스 · DAC · 디지털 제어', '생략'),
    'composite': ('공통 복합 블록', '박스(셀 이름)'),
    'tg': ('(기본 소자) 전달 게이트 — 항상 꺼짐 (§2.2)', '열린 스위치'),
}
# §2.6-1 "다음도 사전에 있다 — 묻지 않는다"
DICT_LISTED = {'inverter', 'nand', 'nor', 'and', 'or', 'xor', 'sr_latch', 'icg', 'dly', 'ls', 'c2c', 'ota'}
IN_DICTIONARY = set(DICT_ROWS) | DICT_LISTED

# V19: polarity bubbles / per-output polarity only on logic outputs. Linear amplifier / analog rows are exempt.
ANALOG_ROLES = {'ctle', 'vga', 'tia', 'summer', 'ota', 'lpf', 'dac', 'bias', 'charge_pump'}

# ---------------- questions (plan §2.7-2..4) ----------------
QUESTION_TEMPLATES = {
    'name_vs_structure': {
        'rule': '§2.6-2, §2.7-2',
        'text': '`{item}`: 구조는 {structure}인데 이름/기능은 {name}입니다. ({opt_structure}로 / {opt_name}로)'},
    'netlist_error_confirm': {
        'rule': '§2.7-4',
        'text': '`{item}`: {fact}. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)'},
    'bus_notation_guess': {
        'rule': '§2.5-7',
        'text': '`{item}`: 비트 표기가 `<n>`이 아니어서 이름 끝 숫자를 비트 번호로 읽어 {buses}로 묶었습니다. 맞습니까? (예 / 표기 지정)'},
    'not_in_dictionary': {
        'rule': '§2.6-3, §2.7-3',
        'text': '`{item}`: 블록 역할 사전에 없는 구조입니다 ({structure}). 일반 박스로 그릴까요? (예 / 역할 지정)'},
    'port_role': {
        'rule': '§2.7-2, §2.7-3',
        'text': '포트 `{item}`는 {guess}입니까? ({options})'},
    'control_class': {
        'rule': '§2.7-3',
        'text': '`{item}`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 ({why}). (중요 / 일반)'},
}
# topics a rule already decides (plan §2.7-4): a question about one of these is an error
RULE_DECIDED_TOPICS = {
    'unused_output': '§3.5-4, §2.7-4 (미사용 출력: 짧은 선 + 이름표)',
    'bus_grouping': '§2.5-7 (같은 기능의 비트는 버스 하나)',
    'dictionary_listed_block': '§2.6-1 (논리 게이트·SR latch·ICG·DLY·LS·C2C·OTA는 사전에 있음)',
    'always_on_tg': '§2.2 (항상 켜진 전달 게이트 = 연결, 질문 없음)',
}


def render_question(tid, fields):
    return QUESTION_TEMPLATES[tid]['text'].format(**fields)
