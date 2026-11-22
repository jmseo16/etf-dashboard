# rx_s5

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_s5/netlist.sp -o runs/rx_s5/out`
- 종료 코드와 마지막 요약 줄: 0 / `views 19, connectivity 19, quality 19` / `self-test: 122/122 injected errors caught; questions: 0; 36s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (멈추지 않음)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 19 / 19 / 19
- 꺾임 수 / 이름표로 이은 곳: 126 / 61
- 검증기 오류 주입 (넣은 수 / 잡은 수): 122 / 122

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
(없음)

questions.json에 질문이 0개였고, classification.md의 분류표를 netlist와 대조해 보았을 때 확신을 갖고 틀렸다고 단정할 항목을 찾지 못해 다시 실행하지 않았다.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dqrx_slice (최상위) | 없음 |
| b_sa_dt | 없음 |
| b_odt_dec | 없음 |

## 그 밖에 적을 것
모든 화면이 연결·품질 검사를 통과했고 질문도 없어, annotations.json을 만들지 않고 1회 실행으로 끝냈다.
