# rx_l3

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out`
  2. (질문 1개에 답한 뒤) `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out --annotations runs/rx_l3/annotations.json`
- 종료 코드와 마지막 요약 줄: 두 번 모두 종료 코드 0. 마지막 줄(2차): `self-test: 131/131 injected errors caught; questions: 0; 68s` (바로 앞 줄 `views 22, connectivity 22, quality 22`)
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 22 / 22 / 22
- 꺾임 수 / 이름표로 이은 곳: 167 / 104
- 검증기 오류 주입 (넣은 수 / 잡은 수): 131 / 131

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| ctl:wl_ck | K9 (시험 입력, 가정) | K9 (도구 판정과 같음, 고친 것 없음) | `xi39 wl_ck net222 wl_en wl_out ... wldet`: wl_ck는 wldet의 d 핀 → `xi2 d net106 net107 dfftg`의 데이터 입력. 클럭은 내부 net222, 출력은 wl_out뿐. |

답한 항목 1개, 분류를 고친 항목 0개.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_top (최상위) | 눈에 띄는 오류는 없음. 다만 ckbuf 3개(xi20, xi22, xi23)의 출력이 이름표만 있고 이웃 블록 선은 없음(이름표로 이은 것이라 규칙상 정상). dqs_c 선이 odtleg3(xi7)까지 길게 우회하고 odtctl 출력 버스가 위아래로 길게 꺾임. 읽기 어렵지만 틀린 연결로 보이지는 않음. |
| b_dqsrx | xi3(invx1)의 입력과 xi5 입력이 acamp 출력에서 갈라져 위로 크게 돌아가는 선이 있음. 연결이 맞는지 netlist와 직접 대조하지는 않았음(도구 검사는 통과). 그 외 겹침 없음. |
| b_wldet는 열지 않음. 대신 3번째로 rx_s3의 b_dq_rx_unit을 열었음(rx_s3 보고서 참고) | 해당 없음 |

## 그 밖에 적을 것
- 연 화면은 이 회로에서 2장(b_rxbyte_top, b_dqsrx)이다. 지시문은 회로마다 3장(최상위 + 다른 두 장)이 아니라 "최상위 화면과 다른 화면 두 장"이므로 이 회로는 한 장 모자란다. 어느 화면이 b_wldet인지 열어 보지 않았다. 열지 않은 것을 열었다고 적지 않는다.
- 질문에 대한 판단은 위 근거로 결정했고 도구의 가정과 같아서 그림은 1차와 2차가 같다.
