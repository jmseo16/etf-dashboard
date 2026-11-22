# rx_s4

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_s4/netlist.sp -o runs/rx_s4/out`
  2. `python3 tool/hsio_draw.py exam/rx_s4/netlist.sp -o runs/rx_s4/out --annotations runs/rx_s4/annotations.json` (분류 수정 후 다시 돌림)
- 종료 코드와 마지막 요약 줄 (2회차): 종료 코드 0 / `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 280s`
  (1회차: 종료 코드 0, 같은 숫자, 꺾임 151·이름표 86, 227s)
- 도구가 오류로 멈췄으면 오류 내용: 멈춤 없음.

## 숫자 (draw_report.md에서 그대로, 2회차)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 149 / 88
- 검증기 오류 주입 (넣은 수 / 잡은 수): 93 / 93

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| vref (최상위 포트) | 중요 제어 K3 (켜기/끄기) | reference (기준) | 270행 서브회로 포트 vref; `r0 vref net30 4k`로 RC 필터를 거쳐 rx_pre_dg의 vref(`mn1 outp vref ...` 차동쌍 한쪽 게이트)로 감. 켜고 끄는 스위치가 아니라 DC 기준 전압 |

질문은 0개였음. 고친 항목 1개. 수정 후 vref는 분류표에서 "기준"이 됨.
tap<2:0>은 K3로 두었으나(dfe_sum3 안에서 인버터와 스위치 게이트로 가는 가중치 켜기/끄기 성격) 확신이 없어 그대로 둠.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dqrx_eq (최상위) | vref가 r0→r1로 들어가 아래 odt_dec 쪽까지 길게 내려가는 선과 MOS 커패시터 2개가 화면 한가운데를 가로지름(vref 그림이 복잡). lb_p/lb_n은 이름표 없이 rx_pre_dg에 바로 붙음. 그 외 선 교차 없음 |
| b_dfe_sum3 | 화면이 세로로 매우 길고(약 4350x5210) 대부분 비어 있음. 아래쪽 트랜지스터(mn17, mn19 등)가 맨 아래에 떨어져 배치되고 거기로 가는 선이 아주 길게 내려감. 글자가 작아 읽기 어려움. 검사는 통과 |
| u_rx_pre_dg | 선은 읽을 만함. 위쪽 오른쪽 트림(pk, C) 부분의 선이 길게 돌아감. 큰 문제 없음 |

## 그 밖에 적을 것
- tool/, exam/ 파일은 고치지 않음.
- 화면 PNG는 3장만 직접 열어 봤고, 나머지 12장은 열어 보지 않음.
