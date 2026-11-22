# rx_s3

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_s3/netlist.sp -o runs/rx_s3/out`
- 종료 코드와 마지막 요약 줄: `views 15, connectivity 15, quality 15` / `self-test: 96/96 injected errors caught; questions: 0; 45s` / 종료 코드 0
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 147 / 57
- 검증기 오류 주입 (넣은 수 / 잡은 수): 96 / 96

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
(없음 — questions.json이 비어 있었고, 분류표를 netlist와 대조한 결과 틀렸다고 확신할 항목을 찾지 못해 다시 돌리지 않았다)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_unit (최상위) | 없음. pad/lb_p/lb_n → rx_pre → dfe_sum(Σ) 2개 → sa_dt → sr_nor → 인버터 체인 → dout_e/dout_o 순으로 왼쪽에서 오른쪽으로 흐르고, ck_t/ck_c → ck_rcv → ck_gate가 아래쪽에 분리되어 있다. net14 등 일부는 이름표로 길게 이어져 있지만 교차 없이 보인다. |
| u_dfe_sum | 없음. 차동쌍(mn0/mn1)과 tap<3:0> 가중치 스위치(mn10~mn17) 열이 세로로 쌓여 netlist와 순서가 일치한다. |
| b_odt_dec | 없음. odt_en/rtt<2:0> → nand2_a ×3 → ls_lh ×3 → enb<2:0> 순서가 netlist(xi0~xi5)와 그대로 일치한다. |

## 그 밖에 적을 것
- 질문도 없었고 분류표(고속 데이터 pad/lb_p/lb_n/vref, 클럭 ck_t/ck_c, 제어 K1~K4, 숨김 K7/K11 등)가 netlist 구조와 맞아 보여 annotations 없이 한 번만 돌렸다.
