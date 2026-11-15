# SKILL.md 교체 문안 — 기준 결과 RX AFE (v6.1)

이 파일은 `SKILL_v6.md`에 그대로 붙여 넣는 교체 문안이다.

- **A** — §11 전체(제목 줄부터 §12 앞까지)를 바꾼다. 옛 §11 첫 줄의 "v3 기준" 인용 블록은 없앤다.
- **B** — §4.12의 첫 코드 블록(분류 확인 표 예시)을 바꾼다.
- **C** — §0 표의 `reference/rx_afe/out/`, `reference/rx_afe/expected/` 두 줄과 §2.2 코드 블록을 바꾼다.
- **D** — 바꿀 문안이 아니다. 이 기준 결과와 맞지 않게 남은 SKILL 일반 규격 줄의 목록(오케스트레이터 검토용)이다.

---

## A. §11 교체 문안

## 11. 기준 결과 — RX AFE (`reference/rx_afe/`)

`bash reference/rx_afe/work/run_all.sh`를 돌리면 `out/`의 `classification.md`, `annotations.json`, `verify_report.json`, `block_dictionary.json`이 `expected/`의 같은 파일과 바이트 단위로 같아야 한다. 화면마다 `scene_sha`도 `expected/verify_report.json`과 같아야 한다. `run_all.sh`는 검증(자동 검사 또는 주입 시험)이 하나라도 실패하면 0이 아닌 값으로 끝난다.

### 11.1 분류 (사용자 확인 완료, 계획서 부록 A + 결정)
| 분류 | 결과 |
|---|---|
| 고속 데이터 입력 | RX_INP, RX_INN |
| 고속 데이터 출력 | DOUT_EVEN_P/N, DOUT_ODD_P/N |
| 고속 데이터 내부 | CTLE1_P/N, CTLE2_P/N, VGA_P/N, E_T2P/N, E_T3P/N, O_T2P/N, O_T3P/N, O_DOUTP/N. O_DOUTP/N은 항상 꺼진 TG 뒤라 **미구동**이다(계획서 §2.3-13, Q3) |
| 고속 클럭 | CLK_INP/N → (B1P/B1N) → CLKI, CLKIB, CLKQ, CLKQB |
| 중요 제어 (버스) | `W<4:1>_<3:0>` 16비트 — **K1**. DFE 탭 1~4 계수: 전류 DAC 스위치 → 탭 쌍 꼬리 전류, 탭 입력 = 귀환 데이터, Σ 출력에서 합산. 끝점 `X_DFE_EVEN/X_SUM/X_DAC1/MS0.g` |
| 중요 제어 (버스) | `G<3:0>` 4비트 — **K6**. VGA 이득 코드: 스위치 → 이득 쌍 꼬리 전류, VGA 출력 VGA_P/N을 X_DFE_EVEN·X_DFE_ODD(HALF_RATE_DFE_SLICE 2개)가 공유한다. 끝점 `X_VGA/MS_G0.g`. 같은 다리는 V4의 "코드로 켜는 병렬 다리"(K5) 특징도 가진다. 분류 이름은 부록 A·C.8 D6·V1에 따라 K6이고, 그림(버스)은 K5여도 같다 |
| 숨김 일반 제어 | `C<2:0>`, `R<2:0>` (CTLE) — **K7** 정적 트림. 고속 경로 안쪽 노드(두 소스 사이)의 degeneration 스위치이고 출처가 최상위 포트라 일반 제어다(V7). 끝점 `X_CTLE1/MC0N.g`, `X_CTLE1/MR0.g` |
| 숨김 바이어스 | IREF (K11, BIAS_GEN 미러에만 닿음, C.8 D5), VBN, VBP, VCM_RX (종단 공통모드, V14) |
| 비고속 분류 점검 (§2.5-9) | 기준 전압·상태 출력·명령·시험 입력·워드 속도 디지털 없음. 이득 코드 K6 = `G<3:0>` |
| 생략 블록 | X_BIAS (BIAS_GEN) — 고속 신호와 무관 |
| 블록 역할 | CTLE_STAGE = CTLE, VGA_STAGE = VGA, DFE_SUMMER = Summer, STRONGARM_SLICER = 비교기(StrongARM 코어 + SR latch·INV 출력단), CML_LATCH = latch, CML_DFF = DFF, INV·NAND2 = 논리 게이트, SR_LATCH = SR latch, IDAC_4BIT = 전류 DAC(부모 유닛 화면의 가변 전류원), HALF_RATE_DFE_SLICE·CLK_DIST_TREE·RX_AFE_TOP = 복합 블록. 모두 사전 행(§2.6-1)이라 묻지 않는다. `block_dictionary.json`의 모든 행은 `missing_features`가 비어 있다 |
| 최상위 포트 | 37개 중 28개를 포트 기호 10개로 그린다: 데이터 입력 2, 클럭 입력 2, 출력 4, W 버스 1, G 버스 1. 숨긴 포트는 9개다: IREF, C0–C2, R0–R2, VDD, VSS |

### 11.2 질문 (이 netlist에서 반드시 나와야 하는 것)
모든 질문은 확신 낮음이고, `spec_rules.QUESTION_TEMPLATES`의 템플릿 문장으로 만든다(annotations에 `template`·`fields`가 있다).

| ID | 템플릿 | 내용 | 처리 |
|---|---|---|---|
| Q1 | name_vs_structure | CTLE의 C0–C2: 이름은 C 뱅크인데 구조는 SP–SN 사이 직렬 스위치 쌍(저항 경로)이고, C*_CAP은 항상 연결돼 있다 | 구조대로 처리한다. 스위치 쌍은 가변 R_S에 넣고, C_DEG_BASE ∥ C0_CAP ∥ C1_CAP ∥ C2_CAP은 고정 C_S(50f + 40f + 80f + 160f)로 그린다 |
| Q2 | name_vs_structure | X_DIV_M/S: 이름은 ÷2인데 귀환 루프가 없다 | 구조대로 LATCH 박스 2개로 그린다 |
| Q3 | netlist_error_confirm | M_TIE TG: NMOS 게이트=VSS, PMOS 게이트=VDD라 항상 꺼져 있다 → O_DOUTP/N 미구동(X_DFE_EVEN.T1_FB_P/N에만 닿음) | 끊긴 것으로 처리한다: 열린 스위치 "(off)". O_DOUTP/N은 고속(미구동)으로 그린다. 끝은 블록 화면에서는 이름표, u_top_tg에서는 화면 밖 연결 기호다 |
| Q4 | netlist_error_confirm | StrongARM M11(PMOS, S=VDD, D=DP, G=DN)에 짝이 없다 | DP쪽 바깥에 두고, 게이트 DN은 이름표로 잇고, 비대칭 주석을 단다 |
| Q5 | bus_notation_guess | 비트 표기가 `<n>`이 아니다: W1_0…W4_3, G0…G3, C0…C2, R0…R2 | 이름 끝 숫자를 비트로 읽는다: `W<4:1>_<3:0>`, `G<3:0>`, `C<2:0>`, `R<2:0>` (§2.5-7 표기 추측 → 확신 낮음) |

규칙이 정해서 **묻지 않는 것**(§2.7-4, classification.md "규칙이 정한 것"):
- NAND2, SR_LATCH, INV — 사전 목록이다(§2.6-1).
- 미사용 고속 출력 — 최상위 CLKQ/CLKQB, 클럭 트리 인버터 출력 4개(CLKI_BUF, CLKIB_BUF, CLKQ_BUF, CLKQB_BUF), StrongARM QPB/QNB. 짧은 선 + 이름표로 그린다(§3.5-4).
- W를 16비트 버스 하나로 묶기 — 같은 기능의 비트는 버스 하나다(§2.5-7).

### 11.3 화면 17개 (id · 셀 · 레벨 · 크기 · 하위 · 허용 교차)
가상 블록 화면의 id는 `u_<부모 짧은 이름>_<역할>`이다(계획서 §1.3-1).

| id | 셀 | 레벨 | viewBox | 하위 화면 | 교차 |
|---|---|---|---|---|---|
| b_top | RX_AFE_TOP | 블록(최상위) | 1420×840 | b_clk, b_slice, u_ctle, u_top_term, u_top_tg, u_vga | 0 |
| b_slice | HALF_RATE_DFE_SLICE | 블록 | 1420×520 | b_dff, b_sa, u_latch, u_summer | 0 |
| b_clk | CLK_DIST_TREE | 블록 | 1300×480 | u_clk_buf, u_clk_term, u_inv, u_latch | 0 |
| u_top_term | RX_AFE_TOP | 유닛 (입력 종단 + ESD) | 640×600 | | 0 |
| u_top_tg | RX_AFE_TOP | 유닛 (전달 게이트, 항상 OFF) | 800×440 | | 0 |
| u_ctle | CTLE_STAGE | 유닛 (CTLE, 대칭) | 900×680 | | 0 |
| u_vga | VGA_STAGE | 유닛 (그림 B) | 1000×660 | | 2 |
| u_summer | DFE_SUMMER | 유닛 (그림 B) | 1120×660 | | 2 |
| b_sa | STRONGARM_SLICER | 블록 | 900×400 | b_sr, u_inv, u_sa_strongarm | 0 |
| u_sa_strongarm | STRONGARM_SLICER | 유닛 (StrongARM core) | 820×700 | | 2 |
| b_sr | SR_LATCH | 블록 (교차 결합 NAND2) | 640×420 | u_nand | 0 |
| u_nand | NAND2 | 유닛 (정적 CMOS NAND) | 560×520 | | 0 |
| u_inv | INV | 유닛 | 480×420 | | 0 |
| u_latch | CML_LATCH | 유닛 (CML latch) | 800×700 | | 2 |
| b_dff | CML_DFF | 블록 (master-slave) | 760×420 | u_latch | 0 |
| u_clk_term | CLK_DIST_TREE | 유닛 (클럭 입력 종단) | 640×510 | | 0 |
| u_clk_buf | CLK_DIST_TREE | 유닛 (CML 클럭 버퍼) | 760×560 | | 0 |

### 11.4 화면별로 반드시 같아야 하는 것

**모든 블록 화면에 공통**

**극성 동그라미** (§3.4-6, §4.1-13, V19). 논리 출력에만 단다. 극성은 netlist 구조로 정한다: 게이트 → 부하 있는 드레인 = 반전, 스택 소스 → 드레인 = 그대로, 하위 블록 = 그 블록의 극성. 차동 블록은 상보 입력에서 같은 쪽 입력(P↔P, N↔N)과 비교한다. 그 결과는 다음과 같다:
- 반전 → 동그라미: INV, NAND2(Y), SR_LATCH(Q·QB), CML_LATCH(QP·QN), StrongARM 코어(OUTP·OUTN), 클럭 BUF(B1P·B1N), CLK_DIST_TREE 박스의 CLKI·CLKIB.
- 비반전 → 동그라미 없음: CML_DFF, STRONGARM_SLICER(SA), HALF_RATE_DFE_SLICE, CLK_DIST_TREE의 CLKQ·CLKQB.
- 아날로그 → 동그라미 없음: CTLE·VGA·Σ.

**차동 입력 표시** (V21). 삼각형 입력에 +/−를 단다. "+"는 동그라미를 달기 전 첫(위) 출력과 같은 위상인 입력이다.
- CTLE·VGA: OUTP가 INP 소자의 드레인이라 반전하고, 아날로그라 동그라미가 없다 → 위 입력(INP) "−", 아래 입력(INN) "+".
- SA·BUF·StrongARM 코어: 위 입력 "+".

**출력 핀 이름** (§3.4-7). 출력이 둘 이상인 삼각형은 출력선 위·아래에 핀 이름을 쓴다(OUTP/OUTN, QP/QN, B1P/B1N). 박스는 지금처럼 안쪽에 쓴다.

**버스 표시** (§3.5-2). 사선만 긋고, 이름에 `<a:b>`가 있으므로 비트 수는 쓰지 않는다. 버스 이름표에도 사선을 긋는다.

**생략 목록** (§3.5-5). 버스는 `<MSB:LSB>` 한 줄로 쓰고, 분류는 한국어로 쓴다(`C<2:0> — 일반 제어 (K7 정적 트림)`). 블록 문구는 "고속 신호와 무관"이다. 유닛 화면에서는 레일·접지 기호로 그린 VDD/VSS를 넣지 않는다. 회색 이름표로만 보인 바이어스(VBN, VBP)는 넣는다.

**화면별**

**b_top**
- 주 경로는 한 줄이다: RX_INP/N → [종단·ESD 표시 "R_T 50Ω"] → CTLE(X_CTLE1) → CTLE(X_CTLE2) → VGA → X_DFE_EVEN(위 박스).
- **VGA 이득 코드**: `G<3:0>` 포트(위, y=50)에서 VGA 삼각형 위 핀(x0+30)까지 곧은 버스선, 가운데 사선. 인스턴스 이름 X_VGA는 그 선의 오른쪽으로 옮긴다.
- X_DFE_ODD는 그 아래 같은 열에 둔다. 주 입력은 VGA_P/VGA_N 이름표다. 두 슬라이스의 피드백·탭 입력(왼쪽)과 탭 출력(오른쪽)은 전부 이름표다.
- W 버스: 포트는 위 슬라이스 위에서 선으로 내려온다(사선, 비트 수 없음). 아래 슬라이스는 30px 짧은 선 + 사선 + `W<4:1>_<3:0>` 이름표다.
- 클럭 트리 박스는 왼쪽 아래에 둔다. CLK_INP/N 포트에서 선으로 잇는다. 출력 CLKI/CLKIB(동그라미)와 CLKQ/CLKQB는 짧은 선 + 이름표다. 슬라이스 클럭 핀(아래)도 이름표다. X_DFE_ODD는 CLKIB, CLKI 순이다(netlist대로 뒤바뀜).
- DOUT_ODD_P/N 오른쪽에 열린 스위치 두 개와 O_DOUTP/N 이름표가 있다.
- 숨긴 포트 9개는 그리지 않는다.

**b_slice**
- Σ(X_SUM, 왼쪽)는 높이 270이다. 주 입력 INP/INN(y 200/220) 아래에 **탭 입력 T1P…T4N을 왼쪽 핀**(y 260…400)으로 두고, 왼쪽 포트 T1_FB_P…T4_INN에서 곧은 선으로 잇는다(V18: 데이터는 왼쪽).
- W 버스는 위에서 들어온다(사선).
- 다음 순서로 오른쪽 출력까지 간다: SA 삼각형(+/−, 클럭 표시, 동그라미 없음) → LATCH(QP·QN 동그라미) → DFF → DFF.
- D_OUTP/N, T2_OUTP/N은 사슬의 갈림 모서리에서 위/아래 포트로 나간다.
- CLK는 아래 줄기 선이고, **CLKB는 블록마다 이름표**다.

**b_clk**
- CLK_INP/N → 종단 표시 → BUF 삼각형(자동 가상 블록, +/−, B1P·B1N 동그라미, 핀 이름 B1P/B1N). BUF 출력선은 x=360에서 끝난다. 같은 직선 위의 다른 넷 이름표 선(400–440)과 40px을 띄운다(§1.4-7).
- B1P/B1N 이름표 → LATCH(X_DIV_M, 데이터 입력에 B1N/B1P **이름표**, 클럭 핀 B1P/B1N 이름표, QP·QN 동그라미) → LATCH(X_DIV_S, 동그라미) → CLKI/CLKIB/CLKQ/CLKQB 포트.
- 인버터 체인 4개는 갈림 모서리 위아래로 두고, 끝은 `*_BUF` 이름표(미사용 출력)다.

**b_sa**
- StrongARM 코어 삼각형(자동 가상 블록, +/−, OUTP·OUTN 동그라미, 클럭 아래) → SR_LATCH 박스(Q·QB 동그라미) → QP/QN 포트.
- 인버터 2개가 있고, 출력은 QPB/QNB 이름표(미사용 출력)다.

**b_sr**
- NAND2 두 개를 위아래 거울로 둔다(Y 동그라미).
- 교차 결합은 **이름표**다(QB→위 NAND B, Q→아래 NAND B).
- 제목은 "SR_LATCH — 블록 레벨 (교차 결합 NAND2)"이다.

**b_dff**
- LATCH(X_M) → LATCH(X_S)로 두고, 둘 다 QP·QN에 동그라미를 단다. 사이 넷 이름은 MP/MN이다.
- netlist에서 master의 클럭 핀이 뒤바뀌어 있다(CLK 핀←CLKB, CLKB 핀←CLK). 그래서 CLK 줄기 선은 X_M의 CLKB 핀과 X_S의 CLK 핀으로 가고, CLKB는 나머지 두 핀에 이름표로 단다. 교차 0.

**u_vga**
- 그림 B. 추가 쌍 꼬리 = 가변 전류원 `I_G<3:0>`이다. 그 오른쪽 버스 핀에서 `G<3:0>` 포트(오른쪽, 사선)로 간다(§3.4-4).
- 범례에 "중요 제어 G<3:0> (K6, …)"를 쓴다.

**u_summer**
- 그림 B. `X_DAC<4:1>` 가변 전류원 → `W<4:1>_<3:0>` 포트(사선, 비트 수 없음).
- 합친 탭 쌍 게이트 포트 `T<4:1>P`/`T<4:1>N`에도 사선을 긋는다.

**u_sa_strongarm · u_clk_buf · u_top_tg**
- 화면 밖으로 나가는 넷은 **화면 밖 연결 기호**(작은 오각 화살표 + 11px 이름)로 그린다(§3.5-1): OUTP/OUTN, B1P/B1N, O_DOUTP/O_DOUTN.
- 셀 포트는 지금처럼 포트 기호로 그린다.

**u_ctle**
- 게이트 저항 값은 SI 표기 "2k"로 쓴다(§3.5-6).

**u_nand**
- 제목은 "NAND2 — unit level (정적 CMOS NAND)"이다.

**u_ctle·u_vga·u_summer·u_sa_strongarm·u_latch**
- 그 밖에는 §8 표와 스크린샷대로다.

### 11.5 검증·산출물 (이 기준 결과에서 나와야 하는 값)
- `verify_report.json` summary는 `{'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}`이다. 화면마다 `scene_sha`(제목·크기·그림 요소·클릭 영역의 SHA-256)와 `checks`가 있다.
- `self_checklist.json`의 `auto_checks`에는 자동 검사 29개가 있고 모두 `pass`, 건수 0이다. 계획서 §4.1-1~17, V24 8개, 버스 표시(§3.5-2), 사전 대응(§2.6-4), M1 파일, M10 유닛 크기가 들어 있다.
- 주입 오류 57건이 모두 잡힌다(`self_test.all_caught = true`). V25 필수 목록 11종(OPEN, SHORT, 블록 교차, 동그라미 지우기, 미사용 출력 지우기, 없는 핀 이름, 그리지도 생략하지도 않은 넷, 짧은 꺾임, 글자 겹침, 점선, 핀 방향 위반)이 모두 들어 있다. §4.1-12 CCI는 이 회로에 CCI가 없어 해당 없음이다.
- 체크리스트 counts는 `{pass 20, fail 0, na 7, star_fail 0}`이고 `verdict_drawing = PASS`이다.
- `block_dictionary.json`은 그린 셀 13행과 가상 블록 6행(입력 종단·ESD, TG 2개, 클럭 종단, CML 클럭 버퍼, StrongARM 코어)으로 19행이다. `not_drawn`은 BIAS_GEN이다.

---

## B. §4.12 첫 코드 블록 교체 문안

```
고속 데이터 입력 : RX_INP, RX_INN            (확신 높음)
클럭 입력        : CLK_INP, CLK_INN          (확신 높음)
고속 출력        : DOUT_EVEN_P, DOUT_EVEN_N, DOUT_ODD_P, DOUT_ODD_N
중요 제어 (버스) : W<4:1>_<3:0> — K1 DFE 탭1~4 계수 (확신 높음) / G<3:0> — K6 VGA 이득 코드, 두 슬라이스 공유 (확신 높음)
생략             : 제어 6개 (C<2:0>, R<2:0> — K7 정적 트림), 바이어스 4개 (IREF, VBN, VBP, VCM_RX), 전원 2개 (VDD, VSS), 블록 1개 (X_BIAS (BIAS_GEN))
질문             : Q1 … Q5 (확신 낮은 것만, 템플릿 문장)
```

---

## C. §0 표·§2.2 교체 문안

§0 표의 두 줄:

| 파일 | 역할 | 권위 |
|---|---|---|
| `reference/rx_afe/out/` | 기준 결과: `concept.html`, `concept.pptx`, `classification.md`, `annotations.json`, `verify_report.json`(화면마다 `scene_sha`), `self_checklist.json`(`auto_checks`), `block_dictionary.json`, `screenshots/` 17장 | **결과 모습의 기준** |
| `reference/rx_afe/expected/` | 기대 결과 중 텍스트 파일(분류 표, annotations, 검증 결과, 사전 대응 기록) — `run_all.sh` 결과와 바이트 단위로 대조 | |

§2.2 코드 블록:

```bash
bash reference/rx_afe/work/run_all.sh          # 검증·주입 시험이 하나라도 실패하면 0이 아닌 값으로 끝난다
python3 -c "import json;print(json.load(open('reference/rx_afe/out/verify_report.json'))['summary'])"
# 기대값: {'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}
python3 -c "import json;print(json.load(open('reference/rx_afe/out/self_checklist.json'))['self_test'])"
# 기대값: {'injected': 57, 'caught': 57, 'all_caught': True}
for f in classification.md annotations.json verify_report.json block_dictionary.json; do cmp reference/rx_afe/out/$f reference/rx_afe/expected/$f; done
```

---

## D. 이 기준 결과와 맞지 않게 남은 SKILL 일반 규격 줄 (교체 문안 아님 — 오케스트레이터 검토용)

이 줄들은 기준 결과의 분류를 적은 줄이 아니라 그리기·검증 규격이라 이번 교체 범위 밖이다. 다만 지금 기준 결과(계획서 v6 + v6.1)와 다르다.

| SKILL 위치 | 지금 문장 | 기준 결과·계획서 |
|---|---|---|
| §6.3 "버스 표시" | 사선 + 비트 수 글자 | 이름에 `<a:b>`가 있으면 비트 수 없음 (계획서 §3.5-2) |
| §7-7 끝에서 둘째 줄 | "버스면 이름표에도 비트 수" | 이름표에도 버스 표시(사선), `<a:b>`면 비트 수 없음 |
| §12 여섯째 항목 | "버스는 사선 + 비트 수 표시" | 같음 (§3.5-2) |
| §6.4 블록 기호 | 동그라미·+/−·출력 핀 이름 언급 없음 | 논리 출력 반전이면 동그라미(V19), 차동 입력 +/−(V21), 출력 둘 이상이면 핀 이름(§3.4-7) — 기준 코드 `scene.tri/box`의 `bubbles`, `pm`, `out_names` |
| §6.3 | 화면 밖 연결 기호 정의 없음 | `scene.offpage`: 오각 화살표 길이 14·높이 8, 이름 11px 보통 굵기 (§3.5-1) |
| §4.9 역할 이름 | `static_cmos_gate`, `cross_coupled_gates` 계열 | 기준 코드 역할 이름 `nand`/`nor`, `sr_latch`, `comparator` (사전 목록 §2.6-1) |
| §5-4 · §6.5 | 가상 블록 화면 id 규칙 없음 | `u_<부모>_<역할>` (계획서 §1.3-1) |
| §7-2 | 피드백·탭 입력 왼쪽 | 기준 결과도 이제 왼쪽(b_slice). 일치 |
| §9 | 검증 항목 1–7 | 기준 `verify.py`는 계획서 §4.1 전부 + V24 + 버스 표시 + 주입 시험 57건을 돌리고 `self_checklist.json`에 쓴다 |
