import os, json

out_dir = "/home/antigravity/jmseo16/etf-dashboard/runs/rx_l1/glm/out"
os.makedirs(out_dir, exist_ok=True)

# 1. annotations.json
annotations = {
  "hs_inputs": [
    "dq7", "dq6", "dq5", "dq4", "dq3", "dq2", "dq1", "dq0"
  ],
  "clock_inputs": [
    "dqs_t", "dqs_c"
  ],
  "hs_outputs": [
    "qr7", "qr6", "qr5", "qr4", "qr3", "qr2", "qr1", "qr0",
    "qf7", "qf6", "qf5", "qf4", "qf3", "qf2", "qf1", "qf0",
    "wl_out"
  ],
  "important_controls": [
    "rx_en", "gate_open", "wl_en", "wl_ck", "slp", "odt_en",
    "rtt<2>", "rtt<1>", "rtt<0>",
    "vrc<5>", "vrc<4>", "vrc<3>", "vrc<2>", "vrc<1>", "vrc<0>",
    "t1w<2>", "t1w<1>", "t1w<0>",
    "t2w<1>", "t2w<0>",
    "ddl<2>", "ddl<1>", "ddl<0>"
  ],
  "show_bias": [],
  "hide": [
    "ibias",
    "vdd",
    "vddq",
    "vss",
    "vssq"
  ],
  "block_roles": {
    "invx1": "inverter",
    "invx4": "inverter",
    "nand2x1": "nand",
    "nand2x2": "nand",
    "lvlup": "level_shifter",
    "lat_tg": "latch",
    "dfftg": "flip_flop",
    "mux2tg": "multiplexer",
    "dlybuf": "delay_buffer",
    "ckbuf": "clock_buffer",
    "padesd": "termination_esd",
    "odtleg3": "termination",
    "odtctl": "composite",
    "biasgen": "bias",
    "vrefdac": "dac",
    "dqsamp": "cml_buffer",
    "acamp": "amplifier",
    "dqsrx": "composite",
    "dqsgate": "composite",
    "dly3": "delay_line",
    "sbamp": "vga",
    "sadfe": "strongarm",
    "srnand": "sr_latch",
    "dqslice": "composite",
    "wldet": "phase_detector",
    "rxbyte_top": "composite"
  },
  "questions": []
}

with open(os.path.join(out_dir, "annotations.json"), "w", encoding="utf-8") as f:
    json.dump(annotations, f, indent=2, ensure_ascii=False)

# 2. block_dictionary.json
block_dict = [
  {"cell": "invx1", "role": "inverter", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle + bubble", "missing_features": []},
  {"cell": "invx4", "role": "inverter", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle + bubble", "missing_features": []},
  {"cell": "nand2x1", "role": "nand", "confidence": "high", "rule": "§2.6-3", "symbol": "nand2 gate", "missing_features": []},
  {"cell": "nand2x2", "role": "nand", "confidence": "high", "rule": "§2.6-3", "symbol": "nand2 gate", "missing_features": []},
  {"cell": "lvlup", "role": "level_shifter", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "lat_tg", "role": "latch", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "dfftg", "role": "flip_flop", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "mux2tg", "role": "multiplexer", "confidence": "high", "rule": "§2.6-3", "symbol": "mux symbol", "missing_features": []},
  {"cell": "dlybuf", "role": "delay_buffer", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle 'BUF'", "missing_features": []},
  {"cell": "ckbuf", "role": "clock_buffer", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle 'CLK'", "missing_features": []},
  {"cell": "padesd", "role": "termination_esd", "confidence": "high", "rule": "§2.6-3", "symbol": "R/ESD mark on input line", "missing_features": []},
  {"cell": "odtleg3", "role": "termination", "confidence": "high", "rule": "§2.6-3", "symbol": "R/switch leg to vddq", "missing_features": []},
  {"cell": "odtctl", "role": "composite", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "biasgen", "role": "bias", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "vrefdac", "role": "dac", "confidence": "high", "rule": "§2.6-3", "symbol": "box 'VREF DAC'", "missing_features": []},
  {"cell": "dqsamp", "role": "cml_buffer", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle 'BUF'", "missing_features": []},
  {"cell": "acamp", "role": "amplifier", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle 'AMP'", "missing_features": []},
  {"cell": "dqsrx", "role": "composite", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "dqsgate", "role": "composite", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "dly3", "role": "delay_line", "confidence": "high", "rule": "§2.6-3", "symbol": "box 'DLY'", "missing_features": []},
  {"cell": "sbamp", "role": "vga", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle 'VGA'", "missing_features": []},
  {"cell": "sadfe", "role": "strongarm", "confidence": "high", "rule": "§2.6-3", "symbol": "triangle + clock", "missing_features": []},
  {"cell": "srnand", "role": "sr_latch", "confidence": "high", "rule": "§2.6-3", "symbol": "box 'SR'", "missing_features": []},
  {"cell": "dqslice", "role": "composite", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []},
  {"cell": "wldet", "role": "phase_detector", "confidence": "high", "rule": "§2.6-3", "symbol": "box 'WL DET'", "missing_features": []},
  {"cell": "rxbyte_top", "role": "composite", "confidence": "high", "rule": "§2.6-3", "symbol": "box (cell name)", "missing_features": []}
]

with open(os.path.join(out_dir, "block_dictionary.json"), "w", encoding="utf-8") as f:
    json.dump(block_dict, f, indent=2, ensure_ascii=False)

# 3. classification.md
md_content = """# 분류 확인 표 — rxbyte_top

```
고속 데이터 입력 : dq7, dq6, dq5, dq4, dq3, dq2, dq1, dq0 (확신 높음 — 구조: DQ 슬라이스 입력 패드 + ESD/ODT)
클럭 입력        : dqs_t, dqs_c (확신 높음 — 구조: 차동 DQS 스트로브 수신기, 래치 및 StrongARM 트리 도달)
고속 출력        : qr7..qr0, qf7..qf0, wl_out (확신 높음 — 구조: 상승/하강 데이터 래치 출력 및 WL 검출 출력)
중요 제어 (버스) : rx_en, gate_open, wl_en, wl_ck, slp, odt_en, rtt<2:0>, vrc<5:0>, t1w<2:0>, t2w<1:0>, ddl<2:0>
생략             : 바이어스 1개 (ibias — K7), 전원 4개 (vdd, vddq, vss, vssq)
질문             : 없음 (규칙 기반 전수 분류 완료)
```

## 포트 분류 표
| 포트 | 종류 | 분류 | 근거 |
|---|---|---|---|
| dq<7:0> | 입력 | 고속 데이터 | 8비트 데이터 수신 입력 |
| dqs_t, dqs_c | 입력 | 고속 클럭 | 차동 DQS 클럭 스트로브 입력 |
| qr<7:0> | 출력 | 고속 데이터 | 라이징 에지 복구 데이터 출력 |
| qf<7:0> | 출력 | 고속 데이터 | 폴링 에지 복구 데이터 출력 |
| wl_out | 출력 | 중요 제어 | Write Leveling 위상 판정 결과 출력 |
| rx_en | 입력 | 중요 제어 | 수신기 활성화 제어 |
| gate_open | 입력 | 중요 제어 | DQS 게이팅 윈도우 제어 |
| wl_en | 입력 | 중요 제어 | Write Leveling 활성화 |
| wl_ck | 입력 | 중요 제어 | Write Leveling 기준 클럭 |
| slp | 입력 | 중요 제어 | 수신기 슬립/파워다운 제어 |
| odt_en | 입력 | 중요 제어 | 온다이 터미네이션 활성화 |
| rtt<2:0> | 입력 | 중요 제어 (버스) | ODT 임피던스 제어 코드 |
| vrc<5:0> | 입력 | 중요 제어 (버스) | VREF DAC 전압 설정 코드 |
| t1w<2:0> | 입력 | 중요 제어 (버스) | DFE 탭 1 가중치 제어 코드 |
| t2w<1:0> | 입력 | 중요 제어 (버스) | DFE 탭 2 가중치 제어 코드 |
| ddl<2:0> | 입력 | 중요 제어 (버스) | DQS 딜레이 라인 튜닝 코드 |
| ibias | 입력 | 바이어스 (생략) | 마스터 기준 전류 바이어스 |
| vdd, vddq | 전원 | 전원 (생략) | 코어 및 I/O 전원 공급 레일 |
| vss, vssq | 접지 | 전원 (생략) | 코어 및 I/O 접지 레일 |

## 블록 역할 표
| 셀 | 역할 | 확신도 | 기호 | 근거 |
|---|---|---|---|---|
| invx1 | inverter | high | triangle + bubble | 표준 인버터 |
| invx4 | inverter | high | triangle + bubble | 4배 구동 인버터 |
| nand2x1 | nand | high | nand2 gate | 2입력 낸드 게이트 |
| nand2x2 | nand | high | nand2 gate | 2배 구동 낸드 게이트 |
| lvlup | level_shifter | high | box (cell name) | 레벨 시프터 (VDD -> VDDQ) |
| lat_tg | latch | high | box (cell name) | 트랜스미션 게이트 래치 |
| dfftg | flip_flop | high | box (cell name) | TG D-플립플롭 |
| mux2tg | multiplexer | high | mux symbol | 2:1 TG 멀티플렉서 |
| dlybuf | delay_buffer | high | triangle 'BUF' | 딜레이 버퍼 단위 셀 |
| ckbuf | clock_buffer | high | triangle 'CLK' | 클럭 분배 버퍼 |
| padesd | termination_esd | high | R/ESD mark | 입력 보호 ESD 소자 |
| odtleg3 | termination | high | R/switch leg | 3단계 선택 ODT 저항 레그 |
| odtctl | composite | high | box (cell name) | ODT 디코더 컨트롤러 |
| biasgen | bias | high | box (cell name) | 바이어스 전압 생성기 |
| vrefdac | dac | high | box 'VREF DAC' | 64단계 VREF 저항 사다리 DAC |
| dqsamp | cml_buffer | high | triangle 'BUF' | DQS 차동 전치 증폭기 |
| acamp | amplifier | high | triangle 'AMP' | AC 결합 증폭기 |
| dqsrx | composite | high | box (cell name) | DQS 차동 수신기 복합 블록 |
| dqsgate | composite | high | box (cell name) | DQS 게이팅 제어 블록 |
| dly3 | delay_line | high | box 'DLY' | 3비트 디지털 제어 딜레이 라인 |
| sbamp | vga | high | triangle 'VGA' | 단일-차동 변환 프리앰프 |
| sadfe | strongarm | high | triangle + clock | StrongARM 기반 2-탭 DFE 감지 증폭기 |
| srnand | sr_latch | high | box 'SR' | SR NAND 래치 |
| dqslice | composite | high | box (cell name) | 단일 DQ 레인 수신 슬라이스 |
| wldet | phase_detector | high | box 'WL DET' | Write Leveling 위상 검출기 |
| rxbyte_top | composite | high | box (cell name) | 8비트 바이트 수신기 최상위 블록 |

## 질문과 가정한 답
- 질문 없음 (명세서 규칙에 따라 전수 분류 완료)
"""

with open(os.path.join(out_dir, "classification.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("Classification files generated successfully for rx_l1.")
