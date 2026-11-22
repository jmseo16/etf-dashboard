# rx_s5

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_s5/netlist.sp -o runs/rx_s5/out`
- 종료 코드와 마지막 요약 줄: 종료 코드 0. `views 19, connectivity 19, quality 19` / `self-test: 122/122 injected errors caught; questions: 0; 38s`
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 19 / 19 / 19
- 꺾임 수 / 이름표로 이은 곳: 126 / 61
- 검증기 오류 주입 (넣은 수 / 잡은 수): 122 / 122

## 질문에 답한 것, 분류를 고친 것
없음 (질문 0개, 틀렸다고 확신하는 분류 없음 → annotations 없이 재실행하지 않음)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dqrx_slice (최상위) | odt_pu의 pad가 dq_pad 이름표로만 이어지고, 두 Σ 블록의 입력 일부(inp/hp/hn 등)가 이름표 net으로 끝남. 비교기·MUX는 박스(README에 명시된 미구현). 눈에 띄는 오류 없음 |
| b_ck_gbuf | 없음. en 핀이 위쪽은 포트, 아래쪽은 이름표로 이어짐(같은 net을 한쪽은 선, 한쪽은 이름표로 표시) |

## 그 밖에 적을 것
- 세 번째 화면은 열지 못함: 연 것은 2장.
- 숫자는 draw_report.md에서 옮김.
