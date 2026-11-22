# 분류 확인 표 — RX_AFE_TOP

```
고속 데이터 입력 : RX_INP, RX_INN                           (확신 높음 — 사용자 지정, 구조 일치: CTLE 입력쌍 게이트 + 종단/ESD 패드)
클럭 입력        : CLK_INP, CLK_INN                         (확신 높음 — 구조: latch 클럭 스티어링·StrongARM 꼬리/리셋 게이트까지 도달, 이름 일치)
고속 출력        : DOUT_EVEN_P, DOUT_EVEN_N, DOUT_ODD_P, DOUT_ODD_N
중요 제어 (버스) : W<4:1>_<3:0> — K1 DFE 탭 계수 가중치 (확신 높음) / G<3:0> — K6 VGA 이득 코드 (확신 높음)
생략             : 제어 6개 (C<2:0>, R<2:0> — K7 정적 트림), 바이어스 4개 (IREF, VBN, VBP, VCM_RX), 전원 2개 (VDD, VSS), 블록 1개 (X_BIAS (BIAS_GEN))
질문             : Q1 C0, C1, C2 (CTLE_STAGE) / Q2 X_DIV_M / X_DIV_S (CLK_DIST_TREE) / Q3 M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2 / Q4 STRONGARM_SLICER: M11 / Q5 W1_0…W4_3, G0…G3, C0…C2, R0…R2
```

## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택하여 annotations.json에 저장)

- **Q1** [name_vs_structure, §2.6-2, §2.7-2] `C0, C1, C2 (CTLE_STAGE)`: 구조는 두 소스 사이 직렬 스위치 쌍(MC0N, MC0P, MC1N, MC1P, MC2N, MC2P = 저항 경로)과 항상 연결된 C(C_DEG_BASE, C0_CAP, C1_CAP, C2_CAP)인데 이름/기능은 C 뱅크 제어(가변 C)입니다. (가변 R + 고정 C로 / 가변 C로)
  - 확신: low (이름-구조 불일치)
  - 가정한 답: 가변 R + 고정 C로 — 구조를 따름(§2.6-2). 스위치 쌍은 가변 R_S 묶음, C_DEG_BASE ∥ C0_CAP ∥ C1_CAP ∥ C2_CAP는 고정 C_S 하나(50f + 40f + 80f + 160f)로 그림. C<2:0>는 K7 정적 = 일반 제어(숨김).
- **Q2** [name_vs_structure, §2.6-2, §2.7-2] `X_DIV_M / X_DIV_S (CLK_DIST_TREE)`: 구조는 latch 2개 직렬, 귀환 루프 없음(master D 입력 = 자기 클럭 넷)인데 이름/기능은 ÷2 분주기(인스턴스 이름 DIV)입니다. (LATCH 2개로 / ÷2로)
  - 확신: low (이름-구조 불일치, 사전의 ÷2 = latch 루프와 불일치)
  - 가정한 답: LATCH 2개로 — 구조대로 LATCH 박스 2개와 실제 연결을 그림. ÷2 기호는 쓰지 않음.
- **Q3** [netlist_error_confirm, §2.7-4] `M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2`: 전달 게이트의 NMOS 게이트=VSS, PMOS 게이트=VDD라 항상 꺼져 있고, 그래서 O_DOUTN, O_DOUTP는 구동원 없이 고속 핀(X_DFE_EVEN.T1_FB_N, X_DFE_EVEN.T1_FB_P)에만 닿습니다(미구동). netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (구조상 항상 OFF — netlist 오류 가능)
  - 가정한 답: 의도됨으로 가정하고 규칙대로 그림(§2.3-2, §2.3-13): TG는 열린 스위치 "(off)", O_DOUTN, O_DOUTP는 고속(미구동)으로 그리고 이름표(블록 화면)·화면 밖 연결 기호(유닛 화면)로 끝냄.
- **Q4** [netlist_error_confirm, §2.7-4] `STRONGARM_SLICER: M11`: M11(PMOS, S=VDD, D=DP, G=DN)의 거울 짝(D=DN, G=DP)이 없어 차동 회로가 비대칭입니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (대칭 위반이 netlist에 있음)
  - 가정한 답: 의도됨으로 가정하고 그대로 그림(§3.3-6): M11는 연결된 노드(DP) 쪽 바깥, 게이트(DN)는 이름표, "비대칭" 주석.
- **Q5** [bus_notation_guess, §2.5-7] `W1_0…W4_3, G0…G3, C0…C2, R0…R2`: 비트 표기가 `<n>`이 아니어서 이름 끝 숫자를 비트 번호로 읽어 `W<4:1>_<3:0>`, `G<3:0>`, `C<2:0>`, `R<2:0>`로 묶었습니다. 맞습니까? (예 / 표기 지정)
  - 확신: low (비트 표기 추측, §2.5-7)
  - 가정한 답: 예 — W<4:1>_<3:0>, G<3:0>, C<2:0>, R<2:0>.

## 규칙이 정한 것 (묻지 않음, §2.7-4)

- dictionary_listed_block: INV; NAND2; SR_LATCH — §2.6-1 (논리 게이트·SR latch·ICG·DLY·LS·C2C·OTA는 사전에 있음) → 사전 행으로 그림 (논리 게이트: 출력 동그라미, SR latch: 박스)
- unused_output: STRONGARM_SLICER: QNB, QPB; CLK_DIST_TREE: CLKIB_BUF, CLKI_BUF, CLKQB_BUF, CLKQ_BUF; RX_AFE_TOP: CLKQ, CLKQB — §3.5-4, §2.7-4 (미사용 출력: 짧은 선 + 이름표) → 지우지 않고 짧은 선 + 넷 이름표
- bus_grouping: W<4:1>_<3:0>; G<3:0>; C<2:0>; R<2:0> — §2.5-7 (같은 기능의 비트는 버스 하나) → 기능별 버스 하나 (`W<4:1>_<3:0>` 16비트 하나)

## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| W<4:1>_<3:0> | W1_0, W1_1, W1_2, W1_3, W2_0, W2_1, W2_2, W2_3, W3_0, W3_1, W3_2, W3_3, W4_0, W4_1, W4_2, W4_3 | important_control | K1 | X_DFE_EVEN/X_SUM/X_DAC1/MS0.g | 최상위 포트 (정적) | DFE 탭 계수 가중치 — 스위치(전류 DAC) → 탭 쌍 꼬리 전류, 탭 입력 = 귀환 고속 데이터, Σ 출력에서 합산 | 버스 (사선 + 이름, 비트 수 없음; 받는 블록 위에서) |
| G<3:0> | G0, G1, G2, G3 | important_control | K6 | X_VGA/MS_G0.g | 최상위 포트 (정적) | VGA 이득 코드 — 스위치 → 이득 쌍 꼬리 전류, 출력을 여러 비트 경로가 공유 (X_DFE_EVEN, X_DFE_ODD (HALF_RATE_DFE_SLICE)) | 버스 (사선 + 이름, 비트 수 없음; 받는 블록 위에서) |
| C<2:0> | C0, C1, C2 | general_control | K7 | X_CTLE1/MC0N.g | 최상위 포트 (정적) | CTLE 안쪽 노드의 정적 트림 (소스 degeneration 뱅크: 피킹·이득), 출처 = 최상위 포트 | 숨김 (생략 목록에 한 줄) |
| R<2:0> | R0, R1, R2 | general_control | K7 | X_CTLE1/MR0.g | 최상위 포트 (정적) | CTLE 안쪽 노드의 정적 트림 (소스 degeneration 뱅크: 피킹·이득), 출처 = 최상위 포트 | 숨김 (생략 목록에 한 줄) |

- 비트 표기: W1_0/W4_3 → W<4:1>_<3:0>, G0/G3 → G<3:0>, C0/C2 → C<2:0>, R0/R2 → R<2:0> — 표기 추측(§2.5-7), 확신 낮음 → Q5.
- G<3:0>: 끝점 = 이득 쌍 꼬리 스위치(VGA 행 §2.6-1), 출력을 여러 비트 경로가 공유 → K6(부록 A, C.8 D6, V1). 같은 다리는 "코드로 켜는 병렬 다리"(V4, K5)의 특징도 가진다 — 분류 이름만 다르고 그림(버스)은 같다.
- C<2:0>: 끝점 = 고속 경로 안쪽 노드(소스 사이)의 degeneration 스위치 → K7, 출처 = 포트(정적) → 일반 제어, 숨김 (V7).
- R<2:0>: 끝점 = 고속 경로 안쪽 노드(소스 사이)의 degeneration 스위치 → K7, 출처 = 포트(정적) → 일반 제어, 숨김 (V7).

## 비고속 분류 점검 (§2.5-9)

- 기준 전압 (P1·VREF): 없음 — ESD 붙은 비교기 기준 패드 없음, 비교기·샘플러 한쪽 입력으로 들어가는 추적 안 된 넷 없음
- 상태 출력 (O1) · 명령 (K8) · 시험 (K9): 없음 — 상태 소자가 구동하는 출력 포트·상태 소자 동기 입력·모니터 출력 없음
- 워드 속도 디지털: 없음 — 직렬화기·디시리얼라이저 워드 경계 없음
- 이득·VREF 코드 (K6): G<3:0> (K6)

## 최상위 포트 분류

| 포트 | 분류 | K# | 근거 |
|---|---|---|---|
| RX_INP | data |  | 사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD) |
| RX_INN | data |  | 사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD) |
| CLK_INP | clock |  | 클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK) |
| CLK_INN | clock |  | 클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK) |
| IREF | bias | K11 | 바이어스: diode-connected (mirror) node |
| DOUT_EVEN_P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_LATCH1/M1 (g->d)) |
| DOUT_EVEN_N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_LATCH1/M2 (g->d)) |
| DOUT_ODD_P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_LATCH1/M1 (g->d)) |
| DOUT_ODD_N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_LATCH1/M2 (g->d)) |
| C0 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/C0_MID (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE1/SP-X_CTLE1/C0_MID (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MC0N.g |
| C1 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/C1_MID (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE1/SP-X_CTLE1/C1_MID (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MC1N.g |
| C2 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/C2_MID (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE1/SP-X_CTLE1/C2_MID (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MC2N.g |
| R0 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MR0.g |
| R1 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MR1.g |
| R2 | general_control | K7 | 일반 제어 K7: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank inside the high-speed path: peaking/gain trim); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank inside the high-speed path: peaking/gain trim); 끝점 X_CTLE1/MR2.g |
| G0 | important_control | K6 | 중요 제어 K6: gain code: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair; stage output VGA_N/VGA_P shared by X_DFE_EVEN, X_DFE_ODD (HALF_RATE_DFE_SLICE); 끝점 X_VGA/MS_G0.g |
| G1 | important_control | K6 | 중요 제어 K6: gain code: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair; stage output VGA_N/VGA_P shared by X_DFE_EVEN, X_DFE_ODD (HALF_RATE_DFE_SLICE); 끝점 X_VGA/MS_G1.g |
| G2 | important_control | K6 | 중요 제어 K6: gain code: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair; stage output VGA_N/VGA_P shared by X_DFE_EVEN, X_DFE_ODD (HALF_RATE_DFE_SLICE); 끝점 X_VGA/MS_G2.g |
| G3 | important_control | K6 | 중요 제어 K6: gain code: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair; stage output VGA_N/VGA_P shared by X_DFE_EVEN, X_DFE_ODD (HALF_RATE_DFE_SLICE); 끝점 X_VGA/MS_G3.g |
| W1_0 | important_control | K1 | 중요 제어 K1: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC1/MS0.g |
| W1_1 | important_control | K1 | 중요 제어 K1: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC1/MS1.g |
| W1_2 | important_control | K1 | 중요 제어 K1: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC1/MS2.g |
| W1_3 | important_control | K1 | 중요 제어 K1: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC1/MS3.g |
| W2_0 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC2/MS0.g |
| W2_1 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC2/MS1.g |
| W2_2 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC2/MS2.g |
| W2_3 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC2/MS3.g |
| W3_0 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC3/MS0.g |
| W3_1 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC3/MS1.g |
| W3_2 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC3/MS2.g |
| W3_3 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC3/MS3.g |
| W4_0 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC4/MS0.g |
| W4_1 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC4/MS1.g |
| W4_2 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC4/MS2.g |
| W4_3 | important_control | K1 | 중요 제어 K1: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; 끝점 X_DFE_EVEN/X_SUM/X_DAC4/MS3.g |
| VDD | power |  | 전원 (구조: PMOS/NMOS 벌크 최다 넷) |
| VSS | power |  | 전원 (구조: PMOS/NMOS 벌크 최다 넷) |

## 최상위 내부 넷 분류

| 넷 | 분류 | K# | 근거 |
|---|---|---|---|
| CLKI | clock |  | 고속 클럭: CLK_INP/CLK_INN 에서 추적 (via X_CLK/X_DIV_M/M1 (g->d)) |
| CLKIB | clock |  | 고속 클럭: CLK_INP/CLK_INN 에서 추적 (via X_CLK/X_DIV_M/M2 (g->d)) |
| CLKQ | clock |  | 고속 클럭: CLK_INP/CLK_INN 에서 추적 (via X_CLK/X_DIV_S/M1 (g->d)) |
| CLKQB | clock |  | 고속 클럭: CLK_INP/CLK_INN 에서 추적 (via X_CLK/X_DIV_S/M2 (g->d)) |
| CTLE1_N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE1/M2 (g->d)) |
| CTLE1_P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE1/M1 (g->d)) |
| CTLE2_N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE2/M2 (g->d)) |
| CTLE2_P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE2/M1 (g->d)) |
| E_T2N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF2/X_S/M2 (g->d)) |
| E_T2P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF2/X_S/M1 (g->d)) |
| E_T3N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF3/X_S/M2 (g->d)) |
| E_T3P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF3/X_S/M1 (g->d)) |
| O_DOUTN | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via M_TIE_N (TG channel)) — **미구동** (항상 꺼진 TG 뒤, §2.3-13, Q3) |
| O_DOUTP | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via M_TIE_P (TG channel)) — **미구동** (항상 꺼진 TG 뒤, §2.3-13, Q3) |
| O_T2N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF2/X_S/M2 (g->d)) |
| O_T2P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF2/X_S/M1 (g->d)) |
| O_T3N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF3/X_S/M2 (g->d)) |
| O_T3P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF3/X_S/M1 (g->d)) |
| VBN | bias | K11 | 바이어스: diode-connected (mirror) node |
| VBP | bias | K11 | 바이어스: diode-connected (mirror) node |
| VCM_RX | bias | K11 | 바이어스: common-mode node of a termination |
| VGA_N | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_VGA/M_MAIN_N (g->d)) |
| VGA_P | data |  | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_VGA/M_MAIN_P (g->d)) |

## 블록 역할 (셀별)

| 셀 | 역할 | 기호 | 확신 | 근거 |
|---|---|---|---|---|
| INV | inverter | inverter | high | complementary PMOS/NMOS with common gate and drain |
| NAND2 | nand | box (cell name) + output bubble | high | static CMOS gate: 2 parallel PMOS pull-ups, 2 series NMOS pull-downs (NAND, dictionary list §2.6-1) |
| SR_LATCH | sr_latch | box (cell name) | high | two NAND gates cross-coupled (output of each drives an input of the other): SR latch (dictionary list §2.6-1) |
| STRONGARM_SLICER | comparator | triangle "SA" + clock | high | StrongARM core (clocked tail, input pair, cross-coupled NMOS/PMOS, reset PMOS) + output stage (inverter, sr_latch): comparator row |
| CML_LATCH | latch | box LATCH | high | input pair + cross-coupled pair, tails steered by complementary clocks |
| CML_DFF | dff | box DFF | high | two latches in series (master->slave) with complementary clocks |
| IDAC_4BIT | dac | variable current source (concept symbol in parent) | high | repeated (bias current source + series switch) units sharing one output |
| CTLE_STAGE | ctle | triangle "CTLE" | high | differential pair with separate sources joined by R/C (source degeneration) |
| VGA_STAGE | vga | triangle "VGA" | high | 5 pairs share outputs, all with the same inputs; extra pairs switched in |
| DFE_SUMMER | summer | Σ | high | 5 pairs with different inputs summed at shared outputs |
| HALF_RATE_DFE_SLICE | composite | box (cell name) | high | hierarchical: 5 sub-blocks + 0 primitive unit(s); every sub-block is a dictionary block |
| CLK_DIST_TREE | composite | box (cell name) | high | hierarchical: 10 sub-blocks + 2 primitive unit(s); every sub-block is a dictionary block |
| BIAS_GEN | bias | omit | high | diode/mirror devices only; no high-speed net |
| RX_AFE_TOP | composite | box (cell name) | high | hierarchical: 7 sub-blocks + 3 primitive unit(s); every sub-block is a dictionary block |

## 셀 안의 기본 소자 묶음 (유닛)

- CML_LATCH: **latch** — MP_LP, MP_LN, M1, M2, M3, M4, M5, M6, MB — input pair + cross-coupled pair, tails steered by complementary clocks
- INV: **inverter** — MP, MN — complementary PMOS/NMOS with common gate and drain
- CLK_DIST_TREE: **termination** — R_TERM_P, R_TERM_N, C_VCM — termination: R from HS input to a common-mode node
- CLK_DIST_TREE: **cml_buffer** — MP_B1P, MP_B1N, MN_B1P, MN_B1N, MB_B1 — single differential pair, common tail, loads
- CTLE_STAGE: **ctle** — MP_LP, MP_LN, M_IND_P, M_IND_N, R_IND_P, R_IND_N, M1, M2, MBP, MBN, R_DEG_BASE, MR0, MR1, MR2, C_DEG_BASE, MC0P, MC0N, C0_CAP, MC1P, MC1N, C1_CAP, MC2P, MC2N, C2_CAP — differential pair with separate sources joined by R/C (source degeneration)
- VGA_STAGE: **vga** — MP_LP, MP_LN, M_MAIN_P, M_MAIN_N, MB_M, M_G0_P, M_G0_N, MS_G0, MB_G0, M_G1_P, M_G1_N, MS_G1, MB_G1, M_G2_P, M_G2_N, MS_G2, MB_G2, M_G3_P, M_G3_N, MS_G3, MB_G3 — 5 pairs share outputs, all with the same inputs; extra pairs switched in
- DFE_SUMMER: **summer** — MP_LP, MP_LN, M_MP, M_MN, MB_M, M_T1P, M_T1N, X_DAC1, M_T2P, M_T2N, X_DAC2, M_T3P, M_T3N, X_DAC3, M_T4P, M_T4N, X_DAC4 — 5 pairs with different inputs summed at shared outputs
- NAND2: **nand** — MP1, MP2, MN1, MN2 — static CMOS gate: 2 parallel PMOS pull-ups, 2 series NMOS pull-downs (NAND, dictionary list §2.6-1)
- STRONGARM_SLICER: **strongarm** — M_TAIL, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11 — clocked tail, input pair, cross-coupled NMOS on input drains + cross-coupled PMOS, reset PMOS
- RX_AFE_TOP: **termination_esd** — R_RX_P, R_RX_N, C_RX_VCM, M_ESD_P1, M_ESD_N1, M_ESD_P2, M_ESD_N2 — termination + ESD: R from HS input to a common-mode node, MOS pad clamps with gate tied to own rail
- RX_AFE_TOP: **tg** — M_TIE_P, M_TIE_P2 — NMOS+PMOS between the same two nets, gates tied to rails
- RX_AFE_TOP: **tg** — M_TIE_N, M_TIE_N2 — NMOS+PMOS between the same two nets, gates tied to rails

## 참고: 데이터·클럭 겸용 셀

- CML_LATCH: 핀 DP, DN, QP, QN 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (평탄 넷 중 데이터·클럭 양쪽에서 닿는 넷은 없음)
- INV: 핀 A, Y 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (평탄 넷 중 데이터·클럭 양쪽에서 닿는 넷은 없음)

## 추적 중 멈춘 곳 (요약)

- M10: gate * reset/precharge (rail source, dynamic node * stop (×2)
- M5: gate * drain * has no load (tail / steering / stacked switch): stop (×12)
- M6: gate * drain * has no load (tail / steering / stacked switch): stop (×12)
- M7: gate * reset/precharge (rail source, dynamic node * stop (×2)
- M8: gate * reset/precharge (rail source, dynamic node * stop (×2)
- M9: gate * reset/precharge (rail source, dynamic node * stop (×2)
- MN2: gate * drain * has no load (tail / steering / stacked switch): stop (×4)
- M_TAIL: gate * drain * has no load (tail / steering / stacked switch): stop (×2)
- R_RX_N: common-mode node * stop (×1)
- R_RX_P: common-mode node * stop (×1)
- R_TERM_N: common-mode node * stop (×1)
- R_TERM_P: common-mode node * stop (×1)
