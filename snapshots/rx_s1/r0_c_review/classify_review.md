# 분류 검토 (claude_2_review_classify) — rx_s1  *(같은 모델이 검토함: 그리는 쪽과 검토하는 쪽이 같은 모델이다)*

읽은 것: `r0_a_classify/` 3개 파일, netlist 발췌(아래 줄), 명세서 §2.3–2.7.

## (a) 고칠 목록 (그리는 쪽이 반영함, 근거 = netlist 줄 + 조항)
1. 블록 역할 표의 인스턴스 목록이 셀마다 첫 곳만 적혀 있었음 → 계층 경로(`odt_dec.xi0` 등)로 전수 기재 (inv_a 9+1, inv_c 2+3, nand2_a 2+3, nand2_c 2, nor2_c 2, ls_lh 3). 근거: netlist `xi0 … inv_c` (sa_dt), `xi2/xi3 … inv_c` (ck_gbuf), `xi0..xi2 … nand2_a` (odt_dec).
2. `esd_dq` 는 `r0 pad pad_r 150` 직렬 R 때문에 §2.6-1 "입력선 위 표시"로 그리면 pad ≠ pad_r 이 하나의 선으로 이어져 SHORT. 선 사이 박스로 그림. 명세서에 이 경우의 규칙이 없다 → "명세서 틈"으로 기록(질문 아님).
3. K2/K3/K1 끝점 핀 재확인: `xi24 … net102 net104 …` (sel_m/sel_l = rx_en·lb_en 논리), `dfe_sum mn2 net50 en net51` (K3), `mn8/mn9 … sgn` `mn6/mn7 … sgnb` (K1 부호). 변경 없음.
4. 분류가 맞다고 본 것 (손으로 다시 따라감): pad → esd(pad_r) → rx_pre(inp) → Σ ×2 → SA ×2 → SR ×2 → inv chain → dout; 클럭 ck/ckb → ck_gbuf → SA ck; 기준 vref → r0+mn0 → rx_pre.vref (RC 저역통과에서 멈춤, 기준); 숨김: ofe/ofo (K7 포트 정적), ibias·net4 (K11), 전원.

## (b) 사용자 질문 (최대 10개 중 5개) — 사용자가 없으므로 가정한 답으로 진행
| # | 질문 | 선택지 | 가정한 답 | 왜 묻나 |
|---|---|---|---|---|
| Q1 | rx_pre 를 일반 박스("AMP")로 그려도 되나 | 예 / 역할 지정 | 예 | 고속 경로 위 블록이 사전에 없음 (§2.6-3) |
| Q2 | rx_en 은 K3(켜기)인가 K2(선택)인가 | K3 / K2 | K3 | 끝점이 두 분류에 걸침, 그림은 같음 |
| Q3 | tap_sgn 은 K1(가중치 부호)인가 K2인가 | K1 / K2 | K1 | 부호 스위치, 그림은 같음 |
| Q4 | D=S 묶인 MOS(MOS 커패시터)가 netlist 오류인가 | 의도됨 / 오류 | 의도됨 | rx_pre 의 교차 커패시터가 특이 (§2.7-4) |
| Q5 | sa_dt 오프셋 C 뱅크를 가변 C로 그려도 되나 | 가변 C / 오프셋 DAC | 가변 C | 이름-구조 불일치 가능 (§2.6-2) |

## (c) 묻지 않고 가정한 답으로 둔 것
- 사전 목록 블록(inv/nand/nor/ls/sr_latch), 미사용 출력 net27/net29, 버스 묶기(`<n>` 표기라 추측 아님).
- lb_p/lb_n 은 이름(`lb`)과 구조(입력쌍 게이트)가 일치 → 질문 없음.
- vref 는 ESD가 없어 P1(외부 기준 패드)이 아니라 "기준 전압" 규칙(§2.5-6)으로 분류.
- 가상 블록 id: `u_sa_dt_stage1`, `u_sa_dt_stage2`, `u_top_lpf` (역할 이름이 명세서에 없어 stage1/2 로 정함).
