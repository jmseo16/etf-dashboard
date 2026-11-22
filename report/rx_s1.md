# rx_s1

## 실행
- 명령:
  - `python3 tool/hsio_draw.py exam/rx_s1/netlist.sp -o runs/rx_s1/out`
- 종료 코드와 마지막 요약 줄: 종료 코드 0, `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 32s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (정상 종료)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 113 / 50
- 검증기 오류 주입 (넣은 수 / 잡은 수): 93 / 93

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
(없음 — `questions.json`에 질문이 0개였고, `classification.md`의 분류표를 netlist와 대조했을 때 틀렸다고 확신할 수 있는 항목을 찾지 못했다. 예: `ofe_p<1:0>`/`ofe_n<1:0>`/`ofo_p<1:0>`/`ofo_n<1:0>`은 `dfe_sum`/`sa_dt` 안쪽 노드에 붙는 정적 트림 커패시터 스위치로 보여 K7(정적 트림, 숨김) 그대로 두었다.)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_unit (최상위) | 없음. 신호가 왼쪽(pad/vref/ck)에서 오른쪽(dout_e/dout_o)으로 깔끔하게 흐르고 교차 없음. |
| b_sa_dt | 위쪽 차동 입력단(mp0/mp1, mn1/mn2 등)과 아래쪽 래치단(mp2~mp4, mn3~mn6)이 화면 안에서 공간적으로 멀리 떨어져 있고 `ck` 인버터에서 나온 선 하나가 화면을 가로질러 길게 이어짐. 보기엔 어색하지만 연결·품질 검사는 모두 통과. |
| u_dfe_sum | 없음. tap<3:0> 가중치 스위치와 sgn/sgnb 극성 스위치, 차동쌍 배치가 규칙대로 깔끔하게 그려짐. |

## 그 밖에 적을 것
- `tool/`, `exam/`은 수정하지 않았다.
- 질문이 없었고 분류를 고치지도 않았으므로 `runs/rx_s1/annotations.json`은 만들지 않았고 재실행도 하지 않았다.
