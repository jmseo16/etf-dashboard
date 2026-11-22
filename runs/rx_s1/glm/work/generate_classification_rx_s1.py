import os, json

out_dir = "/home/antigravity/jmseo16/etf-dashboard/runs/rx_s1/glm/out"
os.makedirs(out_dir, exist_ok=True)

# 1. annotations.json
annotations = {
  "hs_inputs": [
    "pad"
  ],
  "clock_inputs": [
    "ck",
    "ckb"
  ],
  "hs_outputs": [
    "dout_e",
    "dout_o"
  ],
  "important_controls": [
    "lb_en",
    "rx_en",
    "odt_en",
    "rtt<2>",
    "rtt<1>",
    "rtt<0>",
    "tap<3>",
    "tap<2>",
    "tap<1>",
    "tap<0>",
    "tap_sgn"
  ],
  "show_bias": [],
  "hide": [
    "ofe_p<1>",
    "ofe_p<0>",
    "ofe_n<1>",
    "ofe_n<0>",
    "ofo_p<1>",
    "ofo_p<0>",
    "ofo_n<1>",
    "ofo_n<0>",
    "ibias",
    "vdd",
    "vddq",
    "vss",
    "vssq"
  ],
  "block_roles": {
    "inv_a": "inverter",
    "inv_c": "inverter",
    "nand2_a": "nand",
    "nand2_c": "nand",
    "nor2_c": "nor",
    "ls_lh": "ls",
    "esd_dq": "termination_esd",
    "odt_pu": "termination",
    "odt_dec": "composite",
    "rx_bias": "bias",
    "rx_pre": "unknown",
    "dfe_sum": "summer",
    "sa_dt": "comparator",
    "sr_nor": "sr_latch",
    "ck_gbuf": "composite",
    "dq_rx_unit": "composite"
  },
  "_sources": {
    "hs_inputs": "automatic structural analysis (pad input to ESD/ODT/preamp) + assumed answer",
    "others": "automatic structural analysis + assumed answers below"
  },
  "_important_control_buses": {
    "tap<3:0>": {
      "bits": ["tap<3>", "tap<2>", "tap<1>", "tap<0>"],
      "K": "K1",
      "function": "DFE 탭 계수 가중치 — IDAC 스위치 → 탭 쌍 꼬리 전류, Σ 출력에서 합산",
      "endpoint_pin": "xi26/mn10.g",
      "source": "port"
    },
    "tap_sgn": {
      "bits": ["tap_sgn"],
      "K": "K1",
      "function": "DFE 탭 계수 극성 제어 — 극성 반전 스위치 게이트 구동",
      "endpoint_pin": "xi5/mn0.g",
      "source": "port"
    },
    "lb_en": {
      "bits": ["lb_en"],
      "K": "K2",
      "function": "루프백 선택 신호 — pad/vref 경로와 lb_p/lb_n 루프백 경로 간 상보 선택",
      "endpoint_pin": "xi0/mn0.g",
      "source": "port"
    },
    "rx_en": {
      "bits": ["rx_en"],
      "K": "K3",
      "function": "수신기 켜기/끄기 — 클럭 게이팅 버퍼, 프리앰프, DFE summer 꼬리 인에이블",
      "endpoint_pin": "xi25/xi0/mn1.g",
      "source": "port"
    },
    "odt_en": {
      "bits": ["odt_en"],
      "K": "K4",
      "function": "종단 켜기/끄기 — ODT 디코더 NAND 입력",
      "endpoint_pin": "xi22/xi2/mn0.g",
      "source": "port"
    },
    "rtt<2:0>": {
      "bits": ["rtt<2>", "rtt<1>", "rtt<0>"],
      "K": "K4",
      "function": "가변 종단 저항 코드 — ODT 디코더 거쳐 패드 풀업 저항 스위치 제어",
      "endpoint_pin": "xi22/xi2/mn1.g",
      "source": "port"
    }
  },
  "_general_controls": [
    "ofe_p<1>",
    "ofe_p<0>",
    "ofe_n<1>",
    "ofe_n<0>",
    "ofo_p<1>",
    "ofo_p<0>",
    "ofo_n<1>",
    "ofo_n<0>"
  ],
  "_questions_and_assumed_answers": [
    {
      "id": "Q1",
      "template": "hs_input_role",
      "kind": "hs_input_role",
      "rule": "DRAWING_PLAN §2.4",
      "fields": {"item": "pad, lb_p, lb_n"},
      "item": "pad, lb_p, lb_n",
      "question": "pad가 주 고속 데이터 입력 포트이고, lb_p 및 lb_n은 시험용 루프백 데이터 입력이 맞습니까?",
      "assumed": "예 — pad는 최상위 주 고속 입력으로 표시하고, lb_p/lb_n은 루프백 데이터 입력으로 처리",
      "confidence": "low (구조 분석상 두 경로 모두 차동 신호이나 pad가 패드/ESD/ODT 연결)"
    },
    {
      "id": "Q2",
      "template": "clock_input_role",
      "kind": "clock_input_role",
      "rule": "DRAWING_PLAN §2.4",
      "fields": {"item": "ck, ckb"},
      "item": "ck, ckb",
      "question": "ck, ckb가 차동 고속 클럭 입력 포트가 맞습니까?",
      "assumed": "예 — ck, ckb는 클럭 게이팅 버퍼(ck_gbuf)를 거쳐 even/odd 센스앰프의 클럭 꼬리로 연결되는 클럭 입력",
      "confidence": "low (구조상 클럭 게이팅 버퍼 통과 확인, 이름 일치)"
    },
    {
      "id": "Q3",
      "template": "block_role_unknown",
      "kind": "block_role_unknown",
      "rule": "DRAWING_PLAN §2.6-3",
      "fields": {"item": "rx_pre"},
      "item": "rx_pre",
      "question": "rx_pre는 pad/vref 및 루프백 lb_p/lb_n을 수신하는 전치증폭기/MUX 구조로 사전 기호에 정확히 일치하지 않아 일반 박스 PREAMP로 그립니다. 맞습니까?",
      "assumed": "예 — 일반 박스 PREAMP로 그리고 내부 구성(입력쌍, 루프백쌍, 부하 R, MOS 중화 C) 요약",
      "confidence": "low (사전 VGA/CTLE와 상이하여 일반 박스로 판정)"
    },
    {
      "id": "Q4",
      "template": "block_role_sa",
      "kind": "block_role_sa",
      "rule": "DRAWING_PLAN §2.6-1",
      "fields": {"item": "sa_dt"},
      "item": "sa_dt",
      "question": "sa_dt는 2단 구조의 double-tail 동적 비교기(StrongARM 변형)입니다. 사전 비교기 기호(삼각형 SA + 클럭)로 그립니다. 맞습니까?",
      "assumed": "예 — 비교기 기호로 그리고 유닛 화면에서 1단 및 2단 대칭 배치",
      "confidence": "low (double-tail 구조를 비교기 행으로 대응)"
    },
    {
      "id": "Q5",
      "template": "block_role_summer",
      "kind": "block_role_summer",
      "rule": "DRAWING_PLAN §2.6-1",
      "fields": {"item": "dfe_sum"},
      "item": "dfe_sum",
      "question": "dfe_sum은 주 입력과 DFE 1차 탭 피드백 및 IDAC 가중치를 합산하는 회로입니다. 사전 summer 기호(Σ)로 그립니다. 맞습니까?",
      "assumed": "예 — 사전 summer(Σ) 기호로 그림",
      "confidence": "low (사전 summer 행 대응 확인)"
    },
    {
      "id": "Q6",
      "template": "odt_block_role",
      "kind": "odt_block_role",
      "rule": "DRAWING_PLAN §2.5-8, §2.6-1",
      "fields": {"item": "odt_dec, odt_pu"},
      "item": "odt_dec, odt_pu",
      "question": "odt_dec는 DEC 박스로 그리고, odt_pu는 패드 입력선 위의 가변 종단 저항 기호로 그립니다. 맞습니까?",
      "assumed": "예 — odt_dec는 DEC 박스, odt_pu는 pad 선 위 가변 R 기호",
      "confidence": "low (명세서 규칙 적용 확인)"
    },
    {
      "id": "Q7",
      "template": "control_classification",
      "kind": "control_classification",
      "rule": "DRAWING_PLAN §2.5-5 K7",
      "fields": {"item": "ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0>"},
      "item": "ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0>",
      "question": "ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0>는 센스앰프 내부 커패시티브 오프셋 트림 제어로 K7 일반 제어(숨김)로 처리합니다. 맞습니까?",
      "assumed": "예 — K7 정적 트림 제어로 숨김 목록에 기재",
      "confidence": "low (내부 노드 트림 스위치 판단)"
    },
    {
      "id": "Q8",
      "template": "netlist_unused_output",
      "kind": "netlist_unused_output",
      "rule": "DRAWING_PLAN §3.5-4",
      "fields": {"item": "xi9.y(net27), xi12.y(net29)"},
      "item": "xi9.y(net27), xi12.y(net29)",
      "question": "xi9와 xi12 인버터의 출력 net27, net29는 아무것도 구동하지 않는 미사용 출력입니다. 짧은 선 + 이름표로 유지합니까?",
      "assumed": "예 — 명세서 §3.5-4 미사용 출력 규칙대로 짧은 선 + 넷 이름표 표시",
      "confidence": "low (넷리스트 상 미연결 출력 확인)"
    }
  ]
}

with open(f"{out_dir}/annotations.json", "w", encoding="utf-8") as f:
    json.dump(annotations, f, indent=1, ensure_ascii=False)

# 2. block_dictionary.json
block_dict = {
  "_rule": "plan §2.6-3/4: a dictionary row is drawn only when every structure feature of the row is present; missing_features non-empty + dictionary symbol = fail",
  "rows": [
    {
      "cell": "inv_a",
      "instances": ["xi0", "xi2", "xi4", "xi5", "xi6", "xi7", "xi9", "xi10", "xi12", "xi23/xi0"],
      "virtual": False,
      "role": "inverter",
      "row": "공통 논리 게이트 (INV)",
      "symbol": "인버터",
      "matched_features": ["PMOS/NMOS 하나씩, 게이트·드레인 공통 (정적 CMOS)"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "inv_c",
      "instances": ["xi8", "xi11", "xi25/xi2", "xi25/xi3", "xi28/xi0", "xi29/xi0"],
      "virtual": False,
      "role": "inverter",
      "row": "공통 논리 게이트 (INV)",
      "symbol": "인버터",
      "matched_features": ["PMOS/NMOS 하나씩, 게이트·드레인 공통 (정적 CMOS)"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "nand2_a",
      "instances": ["xi1", "xi3", "xi22/xi0", "xi22/xi1", "xi22/xi2"],
      "virtual": False,
      "role": "nand",
      "row": "공통 논리 게이트 (NAND)",
      "symbol": "박스(셀 이름) + 출력 동그라미",
      "matched_features": ["static CMOS gate: 2 parallel PMOS pull-ups, 2 series NMOS pull-downs (NAND)"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "nand2_c",
      "instances": ["xi25/xi0", "xi25/xi1"],
      "virtual": False,
      "role": "nand",
      "row": "공통 논리 게이트 (NAND)",
      "symbol": "박스(셀 이름) + 출력 동그라미",
      "matched_features": ["static CMOS gate: 2 parallel PMOS pull-ups, 2 series NMOS pull-downs (NAND)"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "nor2_c",
      "instances": ["xi30/xi0", "xi30/xi1", "xi31/xi0", "xi31/xi1"],
      "virtual": False,
      "role": "nor",
      "row": "공통 논리 게이트 (NOR)",
      "symbol": "박스(셀 이름) + 출력 동그라미",
      "matched_features": ["static CMOS gate: 2 series PMOS pull-ups, 2 parallel NMOS pull-downs (NOR)"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "ls_lh",
      "instances": ["xi22/xi3", "xi22/xi4", "xi22/xi5"],
      "virtual": False,
      "role": "ls",
      "row": "공통 Level shifter (LS)",
      "symbol": "박스 LS",
      "matched_features": ["저전압 차동 입력 NMOS + 고전압 cross-coupled PMOS 부하"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "esd_dq",
      "instances": ["xi20"],
      "virtual": False,
      "role": "termination_esd",
      "row": "RX 종단 · ESD",
      "symbol": "입력선 위 R/ESD 표시",
      "matched_features": ["패드에서 전원으로 다이오드 클램프 및 직렬 저항, 게이트 접지 클램프 NMOS"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "odt_pu",
      "instances": ["xi21"],
      "virtual": False,
      "role": "termination",
      "row": "RX 종단 · ESD",
      "symbol": "입력선 위 가변 종단 R 표시",
      "matched_features": ["스위치 PMOS와 직렬 저항 뱅크 (패드 풀업 종단)"],
      "missing_features": [],
      "confidence": "high",
      "questions": ["Q6"]
    },
    {
      "cell": "odt_dec",
      "instances": ["xi22"],
      "virtual": False,
      "role": "composite",
      "row": "제어 디코더",
      "symbol": "박스 DEC",
      "matched_features": ["중요 제어 rtt<2:0>, odt_en을 받아 종단 스위치 제어 버스 생성"],
      "missing_features": [],
      "confidence": "high",
      "questions": ["Q6"]
    },
    {
      "cell": "rx_bias",
      "instances": ["xi23"],
      "virtual": False,
      "role": "bias",
      "row": "공통 바이어스 발생기",
      "symbol": "omit",
      "matched_features": ["고속 신호 노드에 직접 닿지 않는 바이어스 전류/전압 발생 블록"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "rx_pre",
      "instances": ["xi24"],
      "virtual": False,
      "role": "unknown",
      "row": "일반 박스 (사전 외)",
      "symbol": "박스 PREAMP",
      "matched_features": ["입력쌍 mn0/mn1, 루프백쌍 mn4/mn5, 부하 R r0/r1, 중화 커패시터 mn8/mn9"],
      "missing_features": ["사전 VGA/CTLE 특성과 불일치"],
      "confidence": "low",
      "questions": ["Q3"]
    },
    {
      "cell": "dfe_sum",
      "instances": ["xi26", "xi27"],
      "virtual": False,
      "role": "summer",
      "row": "RX/TX Summer (DFE·FFE)",
      "symbol": "Σ",
      "matched_features": [
        "주 차동쌍 mn0/mn1과 피드백 탭 쌍 mn4/mn5이 부하 R r0/r1에서 합산",
        "DFE 탭 가중치 IDAC 스위치 mn10, mn12, mn14, mn16",
        "DFE 탭 극성 선택 스위치 mn6, mn7, mn8, mn9"
      ],
      "missing_features": [],
      "confidence": "high",
      "questions": ["Q5"]
    },
    {
      "cell": "sa_dt",
      "instances": ["xi28", "xi29"],
      "virtual": False,
      "role": "comparator",
      "row": "RX 비교기 · 샘플러 (StrongARM)",
      "symbol": "삼각형 SA + 클럭",
      "matched_features": [
        "1단: 클럭 꼬리 mn0, 차동 입력쌍 mn1/mn2, 프리차지 PMOS mp0/mp1",
        "2단: 클럭 꼬리 PMOS mp2, cross-coupled PMOS mp3/mp4, cross-coupled NMOS mn3/mn4, 입력 NMOS mn5/mn6",
        "오프셋 트림 DAC 커패시터/스위치 mn7~mn14"
      ],
      "missing_features": [],
      "confidence": "high",
      "questions": ["Q4"]
    },
    {
      "cell": "sr_nor",
      "instances": ["xi30", "xi31"],
      "virtual": False,
      "role": "sr_latch",
      "row": "공통 SR latch",
      "symbol": "박스(셀 이름)",
      "matched_features": ["NOR2 2개 교차 결합: xi0.y=q, xi1.y=qb"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "ck_gbuf",
      "instances": ["xi25"],
      "virtual": False,
      "role": "composite",
      "row": "Clock 게이팅 버퍼",
      "symbol": "삼각형 버퍼 + 게이트 입력",
      "matched_features": ["차동 클럭 ck/ckb와 rx_en NAND2_C 및 인버터 구동"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    },
    {
      "cell": "dq_rx_unit",
      "instances": [],
      "virtual": False,
      "role": "composite",
      "row": "최상위 블록",
      "symbol": "박스",
      "matched_features": ["최상위 수신기 계층 구조"],
      "missing_features": [],
      "confidence": "high",
      "questions": []
    }
  ]
}

with open(f"{out_dir}/block_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(block_dict, f, indent=1, ensure_ascii=False)

# 3. classification.md
md = """# 분류 확인 표 — dq_rx_unit

```
고속 데이터 입력 : pad (확신 높음 — 구조: ESD·ODT 연결, 전치증폭기 입력쌍 게이트)
클럭 입력        : ck, ckb (확신 높음 — 구조: 클럭 게이팅 버퍼 거쳐 double-tail 센스앰프 꼬리 구동)
고속 출력        : dout_e, dout_o (확신 높음 — even/odd SR 래치 출력 구동 인버터 체인 출력)
중요 제어 (선/버스) : tap<3:0> — K1 DFE 탭 계수 가중치 (확신 높음)
                   tap_sgn — K1 DFE 탭 극성 (확신 높음)
                   lb_en — K2 루프백 선택 (확신 높음)
                   rx_en — K3 수신기 켜기/끄기 (확신 높음)
                   odt_en — K4 종단 켜기 (확신 높음)
                   rtt<2:0> — K4 종단 코드 (확신 높음)
생략             : 제어 8개 (ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — K7 센스앰프 오프셋 트림), 바이어스 1개 (ibias — K11), 전원 4개 (vdd, vddq, vss, vssq), 블록 1개 (xi23 (rx_bias))
질문             : Q1 (pad, lb_p, lb_n 역할) / Q2 (ck, ckb 클럭 판정) / Q3 (rx_pre 일반 박스) / Q4 (sa_dt double-tail 비교기) / Q5 (dfe_sum summer) / Q6 (odt_dec, odt_pu) / Q7 (ofe/ofo K7 숨김) / Q8 (net27, net29 미사용 출력)
```

## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택하여 annotations.json에 저장)

- **Q1** [hs_input_role, §2.4, §2.7-2] `pad, lb_p, lb_n`: pad가 주 고속 데이터 입력 포트이고, lb_p 및 lb_n은 시험용 루프백 데이터 입력이 맞습니까? (pad 주입력, lb_p/n 루프백 / pad와 lb_p/n 모두 주입력)
  - 확신: low (구조상 두 경로 모두 차동 신호이나 pad가 패드/ESD/ODT 연결)
  - 가정한 답: pad 주입력, lb_p/n 루프백 — pad를 주 고속 입력으로 그리고 lb_p/lb_n은 루프백 데이터 입력으로 처리.
- **Q2** [clock_input_role, §2.4, §2.7-2] `ck, ckb`: ck, ckb가 차동 고속 클럭 입력 포트가 맞습니까? (예 / 아니오)
  - 확신: low (구조상 클럭 게이팅 버퍼 통과 확인, 이름 일치)
  - 가정한 답: 예 — ck, ckb는 클럭 게이팅 버퍼(ck_gbuf)를 거쳐 even/odd 센스앰프의 클럭 꼬리로 연결되는 클럭 입력.
- **Q3** [block_role_unknown, §2.6-3] `rx_pre`: rx_pre는 pad/vref 및 루프백 lb_p/lb_n을 수신하는 전치증폭기/MUX 구조로 사전 기호에 정확히 일치하지 않아 일반 박스 PREAMP로 그립니다. 맞습니까? (일반 박스 PREAMP / VGA / CTLE)
  - 확신: low (사전 VGA/CTLE와 상이하여 일반 박스로 판정)
  - 가정한 답: 일반 박스 PREAMP — 일반 박스 PREAMP로 그리고 내부 구성(입력쌍, 루프백쌍, 부하 R, MOS 중화 C) 요약.
- **Q4** [block_role_sa, §2.6-1] `sa_dt`: sa_dt는 2단 구조의 double-tail 동적 비교기(StrongARM 변형)입니다. 사전 비교기 기호(삼각형 SA + 클럭)로 그립니다. 맞습니까? (삼각형 SA + 클럭 / 일반 박스)
  - 확신: low (double-tail 구조를 비교기 행으로 대응)
  - 가정한 답: 삼각형 SA + 클럭 — 비교기 기호로 그리고 유닛 화면에서 1단 및 2단 대칭 배치.
- **Q5** [block_role_summer, §2.6-1] `dfe_sum`: dfe_sum은 주 입력과 DFE 1차 탭 피드백 및 IDAC 가중치를 합산하는 회로입니다. 사전 summer 기호(Σ)로 그립니다. 맞습니까? (Σ 기호 / 일반 박스)
  - 확신: low (사전 summer 행 대응 확인)
  - 가정한 답: Σ 기호 — 사전 summer(Σ) 기호로 그림.
- **Q6** [odt_block_role, §2.5-8, §2.6-1] `odt_dec, odt_pu`: odt_dec는 DEC 박스로 그리고, odt_pu는 패드 입력선 위의 가변 종단 저항 기호로 그립니다. 맞습니까? (예 / 아니오)
  - 확신: low (명세서 규칙 적용 확인)
  - 가정한 답: 예 — odt_dec는 DEC 박스, odt_pu는 pad 선 위 가변 R 기호.
- **Q7** [control_classification, §2.5-5] `ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0>`: 센스앰프 내부 커패시티브 오프셋 트림 제어로 K7 일반 제어(숨김)로 처리합니다. 맞습니까? (숨김(K7) / 그리기)
  - 확신: low (내부 노드 트림 스위치 판단)
  - 가정한 답: 숨김(K7) — K7 정적 트림 제어로 숨김 목록에 기재.
- **Q8** [netlist_unused_output, §3.5-4] `xi9.y(net27), xi12.y(net29)`: xi9와 xi12 인버터의 출력 net27, net29는 아무것도 구동하지 않는 미사용 출력입니다. 짧은 선 + 이름표로 유지합니까? (유지 / 제거)
  - 확신: low (넷리스트 상 미연결 출력 확인)
  - 가정한 답: 유지 — 명세서 §3.5-4 미사용 출력 규칙대로 짧은 선 + 넷 이름표 표시.

## 규칙이 정한 것 (묻지 않음, §2.7-4)

- dictionary_listed_block: inv_a, inv_c, nand2_a, nand2_c, nor2_c, ls_lh, sr_nor — §2.6-1 (논리 게이트·SR latch·LS는 사전에 있음) → 사전 행으로 그림
- unused_output: net27, net29 — §3.5-4 (미사용 출력: 짧은 선 + 이름표)
- bus_grouping: tap<3:0>, rtt<2:0>, ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — §2.5-7 (같은 기능의 비트는 버스 하나)

## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| tap<3:0> | tap<3>, tap<2>, tap<1>, tap<0> | important_control | K1 | xi26/mn10.g | 최상위 포트 | DFE 탭 계수 가중치 — IDAC 스위치 → 탭 쌍 꼬리 전류, Σ 출력에서 합산 | 버스 (사선 + 이름) |
| tap_sgn | tap_sgn | important_control | K1 | xi5/mn0.g | 최상위 포트 | DFE 탭 계수 극성 제어 — 극성 반전 스위치 게이트 구동 | 선 (단일 비트) |
| lb_en | lb_en | important_control | K2 | xi0/mn0.g | 최상위 포트 | 루프백 선택 신호 — pad/vref 경로와 lb_p/lb_n 루프백 경로 간 상보 선택 | 선 (단일 비트) |
| rx_en | rx_en | important_control | K3 | xi25/xi0/mn1.g | 최상위 포트 | 수신기 켜기/끄기 — 클럭 게이팅 버퍼, 프리앰프, DFE summer 꼬리 인에이블 | 선 (단일 비트) |
| odt_en | odt_en | important_control | K4 | xi22/xi2/mn0.g | 최상위 포트 | 종단 켜기/끄기 — ODT 디코더 NAND 입력 | 선 (단일 비트) |
| rtt<2:0> | rtt<2>, rtt<1>, rtt<0> | important_control | K4 | xi22/xi2/mn1.g | 최상위 포트 | 가변 종단 저항 코드 — ODT 디코더 거쳐 패드 풀업 저항 스위치 제어 | 버스 (사선 + 이름) |
| ofe_p<1:0> | ofe_p<1>, ofe_p<0> | general_control | K7 | xi28/mn11.g | 최상위 포트 | 센스앰프 (even, P측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofe_n<1:0> | ofe_n<1>, ofe_n<0> | general_control | K7 | xi28/mn7.g | 최상위 포트 | 센스앰프 (even, N측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofo_p<1:0> | ofo_p<1>, ofo_p<0> | general_control | K7 | xi29/mn11.g | 최상위 포트 | 센스앰프 (odd, P측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofo_n<1:0> | ofo_n<1>, ofo_n<0> | general_control | K7 | xi29/mn7.g | 최상위 포트 | 센스앰프 (odd, N측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |

## 비고속 분류 점검 (§2.5-9)

- 기준 전압 (P1·VREF): vref — 외부 포트에서 RC 저역통과 필터(r0, mn0) 거쳐 프리앰프(rx_pre) 한쪽 입력으로 공급되는 기준 전압
- 상태 출력 (O1) · 명령 (K8) · 시험 (K9): 없음
- 워드 속도 디지털: 없음
- 이득·VREF 코드 (K6): 없음

## 최상위 포트 분류

| 포트 | 분류 | K# | 근거 |
|---|---|---|---|
| pad | data |  | 주 고속 입력 (구조: ESD, ODT, 프리앰프 입력쌍 게이트) |
| vref | reference |  | 판정 기준 전압 (비고속 아날로그, 회색 실선 VREF) |
| ck | clock |  | 차동 고속 클럭 입력 (구조: 클럭 게이팅 버퍼 거쳐 SA 클럭 꼬리 구동) |
| ckb | clock |  | 차동 고속 클럭 입력 (구조: 클럭 게이팅 버퍼 거쳐 SA 클럭 꼬리 구동) |
| lb_p | data |  | 루프백 시험 고속 입력 (프리앰프 루프백 차동쌍 게이트) |
| lb_n | data |  | 루프백 시험 고속 입력 (프리앰프 루프백 차동쌍 게이트) |
| lb_en | important_control | K2 | pad vs 루프백 선택 스위치 MUX 제어 |
| rx_en | important_control | K3 | 수신기 활성화 및 클럭 게이팅 enable 제어 |
| odt_en | important_control | K4 | ODT 종단 활성화 제어 |
| rtt<2> | important_control | K4 | ODT 종단 저항 코드 bit 2 |
| rtt<1> | important_control | K4 | ODT 종단 저항 코드 bit 1 |
| rtt<0> | important_control | K4 | ODT 종단 저항 코드 bit 0 |
| tap<3> | important_control | K1 | DFE summer 탭 가중치 코드 bit 3 |
| tap<2> | important_control | K1 | DFE summer 탭 가중치 코드 bit 2 |
| tap<1> | important_control | K1 | DFE summer 탭 가중치 코드 bit 1 |
| tap<0> | important_control | K1 | DFE summer 탭 가중치 코드 bit 0 |
| tap_sgn | important_control | K1 | DFE summer 탭 극성 부호 제어 |
| ofe_p<1> | general_control | K7 | Even 센스앰프 P측 오프셋 트림 bit 1 |
| ofe_p<0> | general_control | K7 | Even 센스앰프 P측 오프셋 트림 bit 0 |
| ofe_n<1> | general_control | K7 | Even 센스앰프 N측 오프셋 트림 bit 1 |
| ofe_n<0> | general_control | K7 | Even 센스앰프 N측 오프셋 트림 bit 0 |
| ofo_p<1> | general_control | K7 | Odd 센스앰프 P측 오프셋 트림 bit 1 |
| ofo_p<0> | general_control | K7 | Odd 센스앰프 P측 오프셋 트림 bit 0 |
| ofo_n<1> | general_control | K7 | Odd 센스앰프 N측 오프셋 트림 bit 1 |
| ofo_n<0> | general_control | K7 | Odd 센스앰프 N측 오프셋 트림 bit 0 |
| ibias | bias | K11 | 정적 바이어스 전류 입력 (rx_bias 연결) |
| dout_e | data |  | Even 데이터 고속 출력 (인버터 체인 구동) |
| dout_o | data |  | Odd 데이터 고속 출력 (인버터 체인 구동) |
| vdd | power |  | 코어 전원 공급 레일 |
| vddq | power |  | IO/전치증폭기 전원 공급 레일 |
| vss | power |  | 코어 접지 레일 |
| vssq | power |  | IO/전치증폭기 접지 레일 |

## 최상위 내부 넷 분류

| 넷 | 분류 | 근거 |
|---|---|---|
| net1 | data | pad에서 esd_dq 통과 후 rx_pre 입력 |
| net2<2:0> | important_control | odt_dec 출력에서 odt_pu로 가는 종단 enable 버스 (enb<2:0>) |
| net3 | reference | vref에서 RC 필터(r0, mn0) 통과 후 rx_pre 기준 전압 |
| net4 | bias | rx_bias에서 rx_pre로 가는 vbn_q 바이어스 |
| net6, net7 | data | rx_pre 차동 출력 (outp, outn), dfe_sum 입력 |
| net8 | clock | ck_gbuf even 클럭 출력 (cko) |
| net9 | clock | ck_gbuf odd 클럭 출력 (ckob) |
| net10, net11 | data | dfe_sum even 차동 출력, sa_dt even 입력 |
| net12, net13 | data | dfe_sum odd 차동 출력, sa_dt odd 입력 |
| net14, net15 | data | sr_nor even 출력 (q, qb), dfe_sum odd 피드백 (hp, hn) 및 dout_e 인버터 입력 |
| net16, net17 | data | sr_nor odd 출력 (q, qb), dfe_sum even 피드백 (hp, hn) 및 dout_o 인버터 입력 |
| net18, net19 | data | sa_dt even 차동 출력, sr_nor even 입력 |
| net24, net25 | data | sa_dt odd 차동 출력, sr_nor odd 입력 |
| net26 | data | dout_e 인버터 중간 넷 |
| net27 | data | sr_nor even 반전 출력 인버터 출력 (미사용 출력) |
| net28 | data | dout_o 인버터 중간 넷 |
| net29 | data | sr_nor odd 반전 출력 인버터 출력 (미사용 출력) |
| net100 | general_control | lb_en 인버터 출력 (lb_enb) |
| net101 | general_control | sel_m NAND 출력 |
| net102 | important_control | sel_m (rx_pre 메인 입력쌍 활성화) |
| net103 | general_control | sel_l NAND 출력 |
| net104 | important_control | sel_l (rx_pre 루프백 입력쌍 활성화) |
| net105 | important_control | tap_sgn 인버터 출력 (sgnb) |
| net106 | important_control | tap_sgn 버퍼 출력 (sgn) |
"""

with open(f"{out_dir}/classification.md", "w", encoding="utf-8") as f:
    f.write(md)

print("Classification generated successfully.")
