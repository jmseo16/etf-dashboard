# rx_l4

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l4/netlist.sp -o runs/rx_l4/out`
  2. `python3 tool/hsio_draw.py exam/rx_l4/netlist.sp -o runs/rx_l4/out --annotations runs/rx_l4/annotations.json` (질문에 답한 뒤 다시 돌림)
- 종료 코드와 마지막 요약 줄 (2회차): 종료 코드 0 / `views 26, connectivity 26, quality 26` / `self-test: 156/156 injected errors caught; questions: 0; 251s`
  (1회차: 종료 코드 0, 같은 숫자, `questions: 1; 153s`)
- 도구가 오류로 멈췄으면 오류 내용: 멈춤 없음.

## 숫자 (draw_report.md에서 그대로, 2회차)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 270 / 235
- 검증기 오류 주입 (넣은 수 / 잡은 수): 156 / 156

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| ctl:wl_ck | K9 (가정) | K9 (그대로 확정) | netlist 505행 `xi39 wl_ck net222 wl_en wl_out vdd vss wldet`: wl_ck는 wldet의 d 입력에만 들어가 출력 wl_out으로만 나감 → 관찰용 시험 입력 |

분류를 고친 항목은 없음. 답한 항목 1개.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_eq (최상위) | 도구가 그린 그대로 읽힘. 이름표(net…)가 많고 odtleg3 두 개와 odtctl 사이 선이 길게 돌아감. xi23 ckbuf 출력은 net223 이름표만 있고 갈 곳이 안 보임(검사는 통과). 나머지 뚜렷한 문제 없음 |
| b_dqsrx | 없음 (선 교차 없음, 인버터 삼각형 정상) |
| u_sadfe1 | 트랜지스터 화면이 가로로 매우 길어 글자가 작아 읽기 어려움. 전반적으로 선은 이어져 있으나 오른쪽 끝(h1p 쪽) 가로선이 길게 이어짐 |

## 그 밖에 적을 것
- tool/, exam/ 파일은 고치지 않음. 질문 id는 도구 제안 선택지 중 기본값과 같은 답을 고름(판단: 위 근거).
- 화면 PNG는 3장만 직접 열어 봤고, 나머지 23장은 열어 보지 않음.
