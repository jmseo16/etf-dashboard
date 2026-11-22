# rx_l3

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out`
  2. `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out --annotations runs/rx_l3/annotations.json`
- 종료 코드와 마지막 요약 줄:
  1. `views 22, connectivity 22, quality 22` / `self-test: 131/131 injected errors caught; questions: 1; 70s` / 종료 코드 0
  2. `views 22, connectivity 22, quality 22` / `self-test: 131/131 injected errors caught; questions: 0; 64s` / 종료 코드 0
- 도구가 오류로 멈췄으면 오류 내용: 없음 (두 번 다 정상 종료)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 22 / 22 / 22
- 꺾임 수 / 이름표로 이은 곳: 167 / 104
- 검증기 오류 주입 (넣은 수 / 잡은 수): 131 / 131

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `wl_ck` (ctl:wl_ck) | 가정한 답 K9 (시험 입력) | K9 (그대로 확인) | `xi39 wl_ck net222 wl_en wl_out vdd vss wldet` — `wldet` 서브회로는 `d ck en q`, 즉 `wl_ck`는 `d`(샘플되는 입력) 자리이고 실제 클럭은 `net222`(ckbuf 체인 출력)이다. wl_ck는 칩 핀으로는 클럭처럼 보이지만 회로에서는 dfftg에 샘플되어 상태 출력 `wl_out`으로만 나가는 시험 입력이라 K9이 맞다고 판단했다. |

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_top (최상위) | 없음. dq<7:0>이 2개씩 묶여 4개의 dqslice×2 블록으로 들어가고, odtctl/odtleg3/vrefdac/lvlup/biasgen 등 제어·기준 블록이 좌측에, ckbuf 체인과 wldet이 우측에 배치되어 신호가 왼쪽→오른쪽으로 흐른다. 9번째 더미 dqslice 인스턴스(xi38, pad=vssq로 고정된 교정용 복제 슬라이스)는 화면에 보이지 않는데, 숨김 규칙(더미/고속 신호와 무관)에 맞는 처리로 보인다. |
| b_dqslice | 없음. 두 sadfe(SA) 사이에 교차 결합된 net99/net100/net101/net102가 이름표로 깔끔하게 이어져 있고, srnand(SR nand) 출력이 인버터 체인을 거쳐 qr/qf로 나간다. |
| b_wldet | 없음. ck→nand2x2(en과 함께)→invx4→dfftg(d)→invx1→invx4→q 순서로 netlist(xi0~xi4)와 정확히 일치한다. |

## 그 밖에 적을 것
- 질문 1개(`ctl:wl_ck`)는 도구가 이미 낸 기본값(K9)이 netlist 구조와 맞다고 판단해 그대로 답으로 적고 재실행했다. 분류표의 다른 항목은 모두 합당해 보여 고치지 않았다.
