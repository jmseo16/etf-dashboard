# rx_s2

## 실행
- 명령: `for c in rx_l2 rx_s2; do python3 tool/hsio_draw.py exam/$c/netlist.sp -o runs/$c/out | tail -8; done` (반복문 안에서 두 번째로 실행됨)
- 종료 코드와 마지막 요약 줄: 종료 코드 1. `views 14, connectivity 14, quality 13` / `self-test: 86/86 injected errors caught; questions: 0; 29s`
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음. 품질 검사 1개 실패(u_odt_ct: `placement_problem 1`, 상세 `label net15: no room`).

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 14 / 14 / 13
- 꺾임 수 / 이름표로 이은 곳: 118 / 55
- 검증기 오류 주입 (넣은 수 / 잡은 수): 86 / 86

## 질문에 답한 것, 분류를 고친 것
없음. 질문 0개였고, 분류 표에서 틀렸다고 확신하는 항목이 없어 annotations.json을 만들지 않았고 다시 돌리지 않았다. 답하거나 고친 항목 수: 0.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_ct (최상위) | 선 교차나 겹침은 눈에 띄지 않음. 블록 사이의 긴 선이 많음(ck_gbuf의 ckob가 화면 끝까지 감). |
| u_odt_ct | 도구가 실패로 표시한 화면. net15 이름표가 mn2 드레인과 r5 왼쪽 두 곳에 있어 선으로 잇지 못하고 이름표로 이었음. 이름표 자리 문제로 검사가 실패했다고 도구가 보고하지만 그림에서 글자 겹침은 보이지 않음. |
| (rx_l2의 b_rxbyte_pd, b_wldet은 rx_l2 보고서에 기록) | — |

## 그 밖에 적을 것
- 이 회로는 종료 코드 1이며, 품질 검사 13/14로 모두 통과하지 못했다.
- 도구·exam 파일은 고치지 않았다. 그림 판독은 눈으로 본 수준이다.
