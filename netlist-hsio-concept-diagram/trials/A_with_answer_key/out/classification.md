# 분류 확인 표 — rx_afe_top.sp (top: RX_AFE_TOP)

> 계획서 §8 2단계 형식. 사용자에게 물을 수 없어 질문마다 가장 그럴듯한 답을 가정하고 진행했다 (annotations.json `_assumed_answers`).

```
고속 데이터 입력 : RX_INP, RX_INN              (확신 높음)
클럭 입력        : CLK_INP, CLK_INN            (확신 높음)
고속 출력        : DOUT_EVEN_P/N, DOUT_ODD_P/N
중요 제어 (버스) : W<1:4>_<0:3> — DFE 탭 계수 (확신 높음)
생략             : 제어 10개 (C<0:2>, G<0:3>, R<0:2>), 바이어스 4개 (IREF, VBN, VBP, VCM_RX), 블록 1개 (BIAS_GEN)
질문             : 6개 (Q1~Q6, 아래) — 답을 받을 수 없어 가정한 답으로 진행
```

## 질문과 가정한 답

| # | 대상 | 질문 (선택지) | 가정한 답 |
|---|---|---|---|
| Q1 | M_TIE_P/M_TIE_P2, M_TIE_N/M_TIE_N2 (DOUT_ODD_P/N ↔ O_DOUTP/N) | 전달 게이트의 NMOS 게이트=VSS, PMOS 게이트=VDD 라 구조상 항상 OFF입니다. O_DOUTP/N을 DFE 탭1 피드백(고속 데이터)으로 볼까요? (예·그림은 TG 그대로 / 아니오·O_DOUT는 구동 없음 / netlist 오류) | 예 — O_DOUTP/N = 고속 데이터(부록 A와 일치). 그림은 netlist 그대로 TG 기호로 그리고 "항상 OFF" 경고를 붙임 (선으로 단락시키지 않음). |
| Q2 | CTLE_STAGE 의 C<0:2> 와 C0_CAP..C2_CAP | 이름은 C 뱅크지만 C0_CAP..C2_CAP는 SP–SN에 직접(항상) 연결되고, C<0:2>는 SP–SN 사이 직렬 MOS 쌍(MC*P–MC*N)만 켭니다. 어떻게 그릴까요? (구조대로 가변 R + 고정 C / 이름대로 가변 C) | 구조대로 — R_S(가변) = R_DEG_BASE∥MR<0:2>∥MC<0:2>P-N, C_S(고정) = C_DEG_BASE∥C<0:2>_CAP. C<0:2>는 어느 쪽이든 일반 제어(숨김). |
| Q3 | STRONGARM_SLICER M11 (PMOS, D=DP, G=DN, S=VDD) | 짝(D=DN, G=DP)이 없는 비대칭 소자입니다. (의도된 비대칭·그대로 그림 / netlist 누락) | 그대로 그림(정확성 우선). 대칭 축 밖 P쪽에 두고 비대칭 예외로 표시. |
| Q4 | CLK_DIST_TREE X_DIV_M / X_DIV_S | 이름은 분주기(DIV)지만 출력→입력 피드백 루프가 없고 X_DIV_M의 데이터 입력이 클럭 B1N/B1P입니다. 블록 종류는? (CML latch 2개 / ÷2 분주기 / I/Q 생성) | CML latch 2개로 그림(구조 우선). CLKI/CLKIB/CLKQ/CLKQB 는 모두 고속 클럭. |
| Q5 | 사전에 없는 블록: HALF_RATE_DFE_SLICE, CLK_DIST_TREE, SR_LATCH, NAND2 | 박스(셀 이름) + 보이는 핀만으로 그려도 됩니까? (예 / 역할 지정) | 예 — 박스로 그림. 하위 블록은 사전대로(Σ, StrongARM, LATCH, DFF, BUF, INV). |
| Q6 | 부하 없는 고속 넷: CLKQ/CLKQB(최상위), CLKI_BUF 등 INV 체인 출력, QPB/QNB | 추적상 고속 넷이지만 아무 데도 연결되지 않습니다. (그림·이름표로 끝냄 / 생략) | 그림 — 생략은 분류(숨김)대로만 허용(§6-3)이라 짧은 선 + 이름표로 끝냄. |

## 최상위 포트 분류 (37개 → 그림 9개)

| 포트 | 분류 | 그림 |
|---|---|---|
| RX_INP | data | 핀 |
| RX_INN | data | 핀 |
| CLK_INP | clock | 핀 |
| CLK_INN | clock | 핀 |
| IREF | bias | 생략 |
| DOUT_EVEN_P | data | 핀 |
| DOUT_EVEN_N | data | 핀 |
| DOUT_ODD_P | data | 핀 |
| DOUT_ODD_N | data | 핀 |
| C0 | general | 생략 |
| C1 | general | 생략 |
| C2 | general | 생략 |
| R0 | general | 생략 |
| R1 | general | 생략 |
| R2 | general | 생략 |
| G0 | general | 생략 |
| G1 | general | 생략 |
| G2 | general | 생략 |
| G3 | general | 생략 |
| W1_0 | important | 버스 W<1:4>_<0:3> |
| W1_1 | important | 버스 W<1:4>_<0:3> |
| W1_2 | important | 버스 W<1:4>_<0:3> |
| W1_3 | important | 버스 W<1:4>_<0:3> |
| W2_0 | important | 버스 W<1:4>_<0:3> |
| W2_1 | important | 버스 W<1:4>_<0:3> |
| W2_2 | important | 버스 W<1:4>_<0:3> |
| W2_3 | important | 버스 W<1:4>_<0:3> |
| W3_0 | important | 버스 W<1:4>_<0:3> |
| W3_1 | important | 버스 W<1:4>_<0:3> |
| W3_2 | important | 버스 W<1:4>_<0:3> |
| W3_3 | important | 버스 W<1:4>_<0:3> |
| W4_0 | important | 버스 W<1:4>_<0:3> |
| W4_1 | important | 버스 W<1:4>_<0:3> |
| W4_2 | important | 버스 W<1:4>_<0:3> |
| W4_3 | important | 버스 W<1:4>_<0:3> |
| VDD | power | 생략 |
| VSS | power | 생략 |

## 블록 역할 (§3.4) — 구조 판정 + 이름 힌트

| 셀 | 역할 | 확신 | 구조 근거 | 그림 |
|---|---|---|---|---|
| INV | inv | high | CMOS inverter | 작은 삼각형(버퍼) |
| NAND2 | nand2 | low | CMOS NAND2 (not in dictionary) | 박스 NAND2 |
| SR_LATCH | sr_latch | low | cross-coupled NAND pair (not in dictionary) | 박스 SR LATCH |
| STRONGARM_SLICER | strongarm | high | clocked tail + input pair + NMOS/PMOS cross-coupled + reset PMOS | 삼각형 SA + 클럭 |
| CML_LATCH | cml_latch | high | input pair + cross-coupled pair with clock steering | 박스 LATCH |
| CML_DFF | dff | high | two latches in series | 박스 DFF |
| IDAC_4BIT | idac | high | switch + current source repeated | 생략 → 가변 전류원(합산기 안) |
| CTLE_STAGE | ctle | high | differential pair with source degeneration (R∥C between sources) | 삼각형 CTLE |
| VGA_STAGE | vga | high | several pairs share outputs, extra pairs switched, same input | 삼각형 VGA |
| DFE_SUMMER | summer | high | several pairs with different inputs summed at shared outputs | Σ |
| HALF_RATE_DFE_SLICE | composite | low | hierarchical: CML_DFF, CML_LATCH, DFE_SUMMER, STRONGARM_SLICER | 박스(셀 이름) |
| CLK_DIST_TREE | composite | low | hierarchical: CML_LATCH, INV | 박스(셀 이름) |
| BIAS_GEN | bias | high | diode/mirror only, no high-speed net | 생략 |
| RX_AFE_TOP | composite | low | hierarchical: BIAS_GEN, CLK_DIST_TREE, CTLE_STAGE, HALF_RATE_DFE_SLICE, VGA_STAGE | 최상위 |

## 신호 분류 (최상위 내부 넷 포함)

- **고속 데이터**: CTLE1_N, CTLE1_P, CTLE2_N, CTLE2_P, DOUT_EVEN_N, DOUT_EVEN_P, DOUT_ODD_N, DOUT_ODD_P, E_T2N, E_T2P, E_T3N, E_T3P, O_DOUTN, O_DOUTP, O_T2N, O_T2P, O_T3N, O_T3P, RX_INN, RX_INP, VGA_N, VGA_P
- **고속 클럭**: CLKI, CLKIB, CLKQ, CLKQB, CLK_INN, CLK_INP
- **중요 제어**: W1_0, W1_1, W1_2, W1_3, W2_0, W2_1, W2_2, W2_3, W3_0, W3_1, W3_2, W3_3, W4_0, W4_1, W4_2, W4_3
- **일반 제어**: C0, C1, C2, G0, G1, G2, G3, R0, R1, R2
- **바이어스/공통모드**: IREF, VBN, VBP, VCM_RX
- **전원**: VDD, VSS

## 중요 제어 판정 근거 (§3.3)

- `W1_0` → **important**: X_DFE_EVEN/X_SUM/X_DAC1/MS0 -> X_DFE_EVEN/X_SUM/M_T1P: gate O_DOUTP (≠ main E_T2P/E_T3P/O_T2P/VGA_P) summed at X_DFE_EVEN/SUMP; X_DFE_EVEN/X_SUM/X_DAC1/MS0 -> X_DFE_EVEN/X_SUM/M_T1N: gate O_DOUTN (≠ main E_T2N/E_T3N/O_T2N/VGA_N) summed at X_DFE_EVEN/SUMN
- `G0` → **general**: X_VGA/MS_G0 -> X_VGA/M_G0_P: same path as main input (gate CTLE2_P) at VGA_P; X_VGA/MS_G0 -> X_VGA/M_G0_N: same path as main input (gate CTLE2_N) at VGA_N
- `R0` → **general**: X_CTLE1/MR0 -> X_CTLE1/M2: same path as main input (gate RX_INN) at CTLE1_N; X_CTLE1/MR0 -> X_CTLE1/M1: same path as main input (gate RX_INP) at CTLE1_P
- `C0` → **general**: X_CTLE1/MC0P -> X_CTLE1/M2: same path as main input (gate RX_INN) at CTLE1_N; X_CTLE1/MC0P -> X_CTLE1/M1: same path as main input (gate RX_INP) at CTLE1_P

## 소자 역할 요약 (§3.1, 셀별)

- **INV**: logic: MN, MP
- **NAND2**: logic: MN1, MN2, MP1, MP2
- **STRONGARM_SLICER**: input: M1, M2; load?: M11; reset: M10, M7, M8, M9; tail_clk: M_TAIL; xc: M3, M4, M5, M6
- **CML_LATCH**: input: M1, M2; load: MP_LN, MP_LP; steer: M5, M6; tail: MB; xc: M3, M4
- **IDAC_4BIT**: switch: MS0, MS1, MS2, MS3; tail: MB0, MB1, MB2, MB3
- **CTLE_STAGE**: input: M1, M2; load: MP_LN, MP_LP, M_IND_N, M_IND_P; switch: MC0N, MC0P, MC1N, MC1P, MC2N, MC2P, MR0, MR1, MR2; tail: MBN, MBP
- **VGA_STAGE**: input: M_G0_N, M_G0_P, M_G1_N, M_G1_P, M_G2_N, M_G2_P, M_G3_N, M_G3_P, M_MAIN_N, M_MAIN_P; load: MP_LN, MP_LP; switch: MS_G0, MS_G1, MS_G2, MS_G3; tail: MB_G0, MB_G1, MB_G2, MB_G3, MB_M
- **DFE_SUMMER**: input: M_MN, M_MP, M_T1N, M_T1P, M_T2N, M_T2P, M_T3N, M_T3P, M_T4N, M_T4P; load: MP_LN, MP_LP; tail: MB_M
- **CLK_DIST_TREE**: input: MN_B1N, MN_B1P; load: MP_B1N, MP_B1P; tail: MB_B1
- **BIAS_GEN**: diode: M_NLOAD, M_NREF, M_PREF; load: M_NMIR, M_PMIR
- **RX_AFE_TOP**: esd: M_ESD_N1, M_ESD_N2, M_ESD_P1, M_ESD_P2; tgate: M_TIE_N, M_TIE_N2, M_TIE_P, M_TIE_P2

## 생략 목록 (화면별)

- **RX_AFE_TOP**: X_BIAS (BIAS_GEN: 바이어스 발생기 — 고속 신호와 연결 없음 (§4-3)); C_RX_VCM (입력 공통모드 디커플링 C (VCM_RX–VSS)); C0 (일반 제어); C1 (일반 제어); C2 (일반 제어); G0 (일반 제어); G1 (일반 제어); G2 (일반 제어); G3 (일반 제어); IREF (바이어스); R0 (일반 제어); R1 (일반 제어); R2 (일반 제어); VBN (바이어스); VBP (바이어스); VCM_RX (바이어스); VDD (전원); VSS (전원)
- **CLK_DIST_TREE**: C_VCM (공통모드 디커플링 C (VCM_CLK–VSS)); T_B1 (내부 노드(블록 안)); VBN (바이어스); VCM_CLK (바이어스); VDD (전원); VSS (전원)
- **HALF_RATE_DFE_SLICE**: VBN (바이어스); VBP (바이어스); VDD (전원); VSS (전원)
- **CML_DFF**: VBN (바이어스); VDD (전원); VSS (전원)
- **SR_LATCH**: VDD (전원); VSS (전원)
- **CTLE_STAGE**: C0 (일반 제어); C1 (일반 제어); C2 (일반 제어); G_IND_N (바이어스); G_IND_P (바이어스); R0 (일반 제어); R1 (일반 제어); R2 (일반 제어)
- **VGA_STAGE**: G0 (일반 제어); G1 (일반 제어); G2 (일반 제어); G3 (일반 제어)
- **RX_TERM**: C_RX_VCM (디커플링 C (VCM_RX–VSS), 고속 신호와 무관)

## 참고

- CTLE_STAGE M_IND_P/N: NMOS인데 S=VDD, B=VDD 로 적혀 있음(전기적 소스는 OUTP). netlist 단자대로 그림 — 분류에는 영향 없음.
- X_CTLE1, X_CTLE2 는 같은 C<0:2>, R<0:2> 를 공유.
- CML_LATCH, INV 는 데이터 경로(DFE)와 클럭 경로(CLK_DIST_TREE)에 모두 쓰임 → 셀 화면 하나, 선 굵기는 셀 핀 기준(DP/DN/QP/QN 데이터, CLK/CLKB 클럭).
- 데이터와 클럭 양쪽에서 도달한 넷: 없음.
