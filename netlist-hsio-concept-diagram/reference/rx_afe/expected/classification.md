# 분류 확인 표 — RX_AFE_TOP

```
고속 데이터 입력 : RX_INP, RX_INN                           (확신 높음 — 사용자 지정, 구조 일치: CTLE 입력쌍 게이트 + 종단/ESD 패드)
클럭 입력        : CLK_INP, CLK_INN                         (확신 높음 — 구조: latch 클럭 스티어링·StrongARM 꼬리/리셋 게이트까지 도달, 이름 일치)
고속 출력        : DOUT_EVEN_P, DOUT_EVEN_N, DOUT_ODD_P, DOUT_ODD_N
중요 제어 (버스) : W<4:1>_<3:0> (16b) — DFE 탭1~4 계수 (IDAC 스위치 → 탭 쌍 꼬리 전류, 탭 입력 = 귀환 데이터, summer 출력에서 합산)  (확신 높음; 묶음 방식은 Q7)
생략             : 제어 10개 (C0, C1, C2, R0, R1, R2, G0, G1, G2, G3), 바이어스 4개 (IREF, VBN, VBP, VCM_RX), 전원 2개 (VDD, VSS), 블록 1개 (X_BIAS (BIAS_GEN: bias))
질문             : Q1 C0, C1, C2 (CTLE_STAGE) / Q2 X_DIV_M / X_DIV_S in CLK_DIST_TREE / Q3 M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2 / Q4 STRONGARM_SLICER: M11 / Q5 NAND2 (static_cmos_gate), SR_LATCH (cross_coupled_gates) / Q6 top: CLKQ, CLKQB; CLK_DIST_TREE: CLKI_BUF, CLKIB_BUF, CLKQ_BUF, CLKQB_BUF; STRONGARM_SLICER: QPB, QNB / Q7 W<4:1>_<3:0>
```

## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택하여 annotations.json에 저장)

- **Q1** `C0, C1, C2 (CTLE_STAGE)` — 이름(C*)은 커패시터 뱅크 제어처럼 보이지만, 구조상 스위치 MC*P/MC*N은 SP-C*_MID-SN 직렬 경로(저항 경로)이고 C*_CAP은 SP-SN에 항상 연결된 고정 C입니다. 구조대로 그릴까요? (예: 가변 R + 고정 C / 아니오: 가변 C로)
  - 확신: low (이름-구조 불일치)
  - 가정한 답: 예 — 구조를 따름. C0..C2 스위치는 가변 R 묶음에 포함, C_DEG_BASE+C0_CAP+C1_CAP+C2_CAP은 고정 C 하나(합계 330f)로 그림. C0..C2는 일반 제어(그리지 않음).
- **Q2** `X_DIV_M / X_DIV_S in CLK_DIST_TREE` — 인스턴스 이름은 ÷2 분주기(DIV)이지만 구조상 귀환 루프가 없습니다 (master의 D 입력 = 자기 클럭 B1N/B1P, slave 출력은 어디로도 되돌아가지 않음). 구조대로 "LATCH 2개 직렬"로 그릴까요? (예 / ÷2로 그림 / netlist 오류)
  - 확신: low (이름-구조 불일치, 사전의 ÷2 = latch 루프와 불일치)
  - 가정한 답: 예 — 구조대로 LATCH 박스 2개와 실제 연결을 그림. ÷2 기호는 쓰지 않음. netlist 오류 가능성을 보고서에 남김.
- **Q3** `M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2` — 전달 게이트(NMOS 게이트=VSS, PMOS 게이트=VDD)라 항상 꺼져 있습니다. 그러면 O_DOUTP/N(= X_DFE_EVEN의 탭1 귀환 입력 T1_FB)은 떠 있습니다. 의도된 것입니까? (의도됨 / 연결(항상 ON)이어야 함)
  - 확신: low (구조상 항상 OFF)
  - 가정한 답: 끊긴 것으로 처리(계획서 §3.2): TG는 열린 스위치 기호 + "(off)". O_DOUTP/N은 구동이 없지만 X_DFE_EVEN의 고속 핀(T1_FB)에 붙어 있어 고속 데이터로 그리고 이름표로 끝냄.
- **Q4** `STRONGARM_SLICER: M11` — STRONGARM_SLICER에 거울 짝이 없는 소자가 있습니다 (M11: PMOS, S=VDD, D=DP, G=DN; 반대쪽 D=DN, G=DP 소자 없음). 차동 회로가 비대칭이 됩니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (대칭 위반이 netlist에 있음)
  - 가정한 답: 그대로 그림 (정확성 > 대칭, 계획서 §5.2-7). M11은 연결된 노드(DP) 쪽 바깥에 두고, 게이트(DN)는 이름표로 연결, "비대칭" 표시.
- **Q5** `NAND2 (static_cmos_gate), SR_LATCH (cross_coupled_gates)` — 블록 역할 사전에 없는 구조입니다 (정적 CMOS 게이트, 교차 결합 게이트 = SR latch). 박스(셀 이름)로 그릴까요? (예 / 역할 지정)
  - 확신: low (사전에 없음)
  - 가정한 답: 예 — 사전 규칙대로 박스(셀 이름) + 보이는 핀. 유닛 레벨은 소자 그대로.
- **Q6** `top: CLKQ, CLKQB; CLK_DIST_TREE: CLKI_BUF, CLKIB_BUF, CLKQ_BUF, CLKQB_BUF; STRONGARM_SLICER: QPB, QNB` — 추적상 고속 넷이지만 아무 곳에도 연결되지 않은(부하 없는) 출력입니다. 그릴까요? (그림 / 생략)
  - 확신: low (계획서에 규칙 없음)
  - 가정한 답: 그림 — 분류가 고속이므로 §6.3(생략은 분류대로만)에 따라 생략하지 않고, 끝에 넷 이름표만 둔 짧은 선으로 표시.
- **Q7** `W<4:1>_<3:0>` — 중요 제어 16비트(W1_0..W4_3)를 "DFE 탭 계수" 기능 하나의 버스로 묶을까요, 탭별 4비트 버스 4개로 나눌까요? (16b 1개 / 4b×4)
  - 확신: low (계획서 해석)
  - 가정한 답: 16b 버스 1개 (W<4:1>_<3:0>) — §4.4 "기능별 버스 하나"를 "DFE 탭 계수" 기능으로 해석.

## 최상위 포트 분류

| 포트 | 분류 | 근거 |
|---|---|---|
| RX_INP | data | 사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD) |
| RX_INN | data | 사용자 지정 고속 입력 (구조 확인: CTLE1 입력쌍 게이트, 종단 R→공통모드, ESD) |
| CLK_INP | clock | 클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK) |
| CLK_INN | clock | 클럭 입력: 구조 추적이 latch 클럭 스티어링/StrongARM 꼬리·리셋 게이트에 도달 (+ 이름 힌트 CLK) |
| IREF | bias | 바이어스: diode-connected (mirror) node |
| DOUT_EVEN_P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_LATCH1/M1 (g->d)) |
| DOUT_EVEN_N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_LATCH1/M2 (g->d)) |
| DOUT_ODD_P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_LATCH1/M1 (g->d)) |
| DOUT_ODD_N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_LATCH1/M2 (g->d)) |
| C0 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/C0_MID (degeneration bank, not a summing branch); switch across X_CTLE1/SP-X_CTLE1/C0_MID (degeneration bank, not a summing branch) (이름-구조 불일치 → Q1) |
| C1 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/C1_MID (degeneration bank, not a summing branch); switch across X_CTLE1/SP-X_CTLE1/C1_MID (degeneration bank, not a summing branch) (이름-구조 불일치 → Q1) |
| C2 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/C2_MID (degeneration bank, not a summing branch); switch across X_CTLE1/SP-X_CTLE1/C2_MID (degeneration bank, not a summing branch) (이름-구조 불일치 → Q1) |
| R0 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank, not a summing branch); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank, not a summing branch) |
| R1 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank, not a summing branch); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank, not a summing branch) |
| R2 | general_control | 일반 제어: switch across X_CTLE1/SN-X_CTLE1/SP (degeneration bank, not a summing branch); switch across X_CTLE2/SN-X_CTLE2/SP (degeneration bank, not a summing branch) |
| G0 | general_control | 일반 제어: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair (gain only) |
| G1 | general_control | 일반 제어: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair (gain only) |
| G2 | general_control | 일반 제어: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair (gain only) |
| G3 | general_control | 일반 제어: switch -> current of an extra pair with the SAME inputs CTLE2_N/CTLE2_P as the main pair (gain only) |
| W1_0 | important_control | 중요 제어: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W1_1 | important_control | 중요 제어: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W1_2 | important_control | 중요 제어: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W1_3 | important_control | 중요 제어: switch -> current of pair DOUT_EVEN_N/DOUT_EVEN_P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_DOUTN/O_DOUTP, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W2_0 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W2_1 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W2_2 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W2_3 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W3_0 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W3_1 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W3_2 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W3_3 | important_control | 중요 제어: switch -> current of pair E_T2N/E_T2P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T2N/O_T2P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P |
| W4_0 | important_control | 중요 제어: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W4_1 | important_control | 중요 제어: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W4_2 | important_control | 중요 제어: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| W4_3 | important_control | 중요 제어: switch -> current of pair E_T3N/E_T3P, summed at X_DFE_EVEN/SUMN/X_DFE_EVEN/SUMP with main pair VGA_N/VGA_P; switch -> current of pair O_T3N/O_T3P, summed at X_DFE_ODD/SUMN/X_DFE_ODD/SUMP with main pair VGA_N/VGA_P |
| VDD | power | 전원 (구조: PMOS/NMOS 벌크 최다 넷) |
| VSS | power | 전원 (구조: PMOS/NMOS 벌크 최다 넷) |

## 최상위 내부 넷 분류

| 넷 | 분류 | 근거 |
|---|---|---|
| CLKI | clock | 고속 클럭: CLK_INP/N 에서 추적 (via X_CLK/X_DIV_M/M1 (g->d)) |
| CLKIB | clock | 고속 클럭: CLK_INP/N 에서 추적 (via X_CLK/X_DIV_M/M2 (g->d)) |
| CLKQ | clock | 고속 클럭: CLK_INP/N 에서 추적 (via X_CLK/X_DIV_S/M1 (g->d)) |
| CLKQB | clock | 고속 클럭: CLK_INP/N 에서 추적 (via X_CLK/X_DIV_S/M2 (g->d)) |
| CTLE1_N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE1/M2 (g->d)) |
| CTLE1_P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE1/M1 (g->d)) |
| CTLE2_N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE2/M2 (g->d)) |
| CTLE2_P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_CTLE2/M1 (g->d)) |
| E_T2N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF2/X_S/M2 (g->d)) |
| E_T2P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF2/X_S/M1 (g->d)) |
| E_T3N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF3/X_S/M2 (g->d)) |
| E_T3P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_EVEN/X_DFF3/X_S/M1 (g->d)) |
| O_DOUTN | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via M_TIE_N (TG channel)) |
| O_DOUTP | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via M_TIE_P (TG channel)) |
| O_T2N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF2/X_S/M2 (g->d)) |
| O_T2P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF2/X_S/M1 (g->d)) |
| O_T3N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF3/X_S/M2 (g->d)) |
| O_T3P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_DFE_ODD/X_DFF3/X_S/M1 (g->d)) |
| VBN | bias | 바이어스: diode-connected (mirror) node |
| VBP | bias | 바이어스: diode-connected (mirror) node |
| VCM_RX | bias | 바이어스: common-mode node of a termination |
| VGA_N | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_VGA/M_MAIN_N (g->d)) |
| VGA_P | data | 고속 데이터: RX_INP/RX_INN 에서 추적 (via X_VGA/M_MAIN_P (g->d)) |

## 블록 역할 (셀별)

| 셀 | 역할 | 기호 | 확신 | 근거 |
|---|---|---|---|---|
| INV | inverter | triangle (CMOS buffer) | high | complementary PMOS/NMOS with common gate and drain |
| NAND2 | static_cmos_gate | box (cell name) | low | static CMOS gate (pull-up gate set = pull-down gate set): NOT in the dictionary |
| SR_LATCH | cross_coupled_gates | box (cell name) | low | two static CMOS gates cross-coupled (SR latch); NOT in the dictionary |
| STRONGARM_SLICER | composite | box (cell name) | high | hierarchical: 3 sub-blocks + 1 primitive unit(s); not itself a dictionary block |
| CML_LATCH | latch | box LATCH | high | input pair + cross-coupled pair, tails steered by complementary clocks |
| CML_DFF | dff | box DFF | high | two latches in series (master->slave) with complementary clocks |
| IDAC_4BIT | dac | variable current source (concept symbol in parent) | high | repeated (bias current source + series switch) units sharing one output |
| CTLE_STAGE | ctle | triangle "CTLE" | high | differential pair with separate sources joined by R/C (source degeneration) |
| VGA_STAGE | vga | triangle "VGA" | high | 5 pairs share outputs, all with the same inputs; extra pairs switched in |
| DFE_SUMMER | summer | Σ | high | 5 pairs with different inputs summed at shared outputs |
| HALF_RATE_DFE_SLICE | composite | box (cell name) | high | hierarchical: 5 sub-blocks + 0 primitive unit(s); not itself a dictionary block |
| CLK_DIST_TREE | composite | box (cell name) | high | hierarchical: 10 sub-blocks + 2 primitive unit(s); not itself a dictionary block |
| BIAS_GEN | bias | omit | high | diode/mirror devices only; no high-speed net |
| RX_AFE_TOP | composite | box (cell name) | high | hierarchical: 7 sub-blocks + 3 primitive unit(s); not itself a dictionary block |

## 셀 안의 기본 소자 묶음 (유닛)

- CML_LATCH: **latch** — MP_LP, MP_LN, M1, M2, M3, M4, M5, M6, MB — input pair + cross-coupled pair, tails steered by complementary clocks
- INV: **inverter** — MP, MN — complementary PMOS/NMOS with common gate and drain
- CLK_DIST_TREE: **termination** — R_TERM_P, R_TERM_N, C_VCM — termination: R from HS input to a common-mode node
- CLK_DIST_TREE: **cml_buffer** — MP_B1P, MP_B1N, MN_B1P, MN_B1N, MB_B1 — single differential pair, common tail, loads
- CTLE_STAGE: **ctle** — MP_LP, MP_LN, M_IND_P, M_IND_N, R_IND_P, R_IND_N, M1, M2, MBP, MBN, R_DEG_BASE, MR0, MR1, MR2, C_DEG_BASE, MC0P, MC0N, C0_CAP, MC1P, MC1N, C1_CAP, MC2P, MC2N, C2_CAP — differential pair with separate sources joined by R/C (source degeneration)
- VGA_STAGE: **vga** — MP_LP, MP_LN, M_MAIN_P, M_MAIN_N, MB_M, M_G0_P, M_G0_N, MS_G0, MB_G0, M_G1_P, M_G1_N, MS_G1, MB_G1, M_G2_P, M_G2_N, MS_G2, MB_G2, M_G3_P, M_G3_N, MS_G3, MB_G3 — 5 pairs share outputs, all with the same inputs; extra pairs switched in
- DFE_SUMMER: **summer** — MP_LP, MP_LN, M_MP, M_MN, MB_M, M_T1P, M_T1N, X_DAC1, M_T2P, M_T2N, X_DAC2, M_T3P, M_T3N, X_DAC3, M_T4P, M_T4N, X_DAC4 — 5 pairs with different inputs summed at shared outputs
- NAND2: **static_cmos_gate** — MP1, MP2, MN1, MN2 — static CMOS gate (pull-up gate set = pull-down gate set): NOT in the dictionary
- STRONGARM_SLICER: **strongarm** — M_TAIL, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11 — clocked tail, input pair, cross-coupled NMOS on input drains + cross-coupled PMOS, reset PMOS
- RX_AFE_TOP: **termination_esd** — R_RX_P, R_RX_N, C_RX_VCM, M_ESD_P1, M_ESD_N1, M_ESD_P2, M_ESD_N2 — termination + ESD: R from HS input to a common-mode node, MOS pad clamps with gate tied to own rail
- RX_AFE_TOP: **tg** — M_TIE_P, M_TIE_P2 — NMOS+PMOS between the same two nets, gates tied to rails
- RX_AFE_TOP: **tg** — M_TIE_N, M_TIE_N2 — NMOS+PMOS between the same two nets, gates tied to rails

## 참고: 데이터·클럭 겸용 셀

- CML_LATCH: 핀 DP, DN, QP, QN 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (선 굵기는 데이터 기준, 패널에 주석)
- INV: 핀 A, Y 는 DFE 경로에서는 데이터, CLK_DIST_TREE에서는 클럭 (선 굵기는 데이터 기준, 패널에 주석)

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
