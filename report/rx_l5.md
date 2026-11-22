# rx_l5

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out`
  2. (질문 1개에 답한 뒤) `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out --annotations runs/rx_l5/annotations.json`
- 종료 코드와 마지막 요약 줄: 두 번 모두 종료 코드 0. 재실행 후: `views 28, connectivity 28, quality 28` / `self-test: 179/179 injected errors caught; questions: 0; 94s`
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 28 / 28 / 28
- 꺾임 수 / 이름표로 이은 곳: 171 / 102
- 검증기 오류 주입 (넣은 수 / 잡은 수): 179 / 179

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| ctl:wl_ck | K9 (가정한 답) | K9 | `xi39 wl_ck net222 wl_en wl_q ... wl_det`: wl_ck는 wl_det의 d 입력이고 dqs 클럭(net222)으로 샘플되어 wl_q 상태 출력으로만 감. 도구의 가정과 같아 답이 같음. 분류 표는 고치지 않음 |

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rx_byte8 (최상위) | xi23 버퍼 출력(net223)이 이름표로 끝남(xi38 더미 레인으로 가는 net이라 추정). pwr_dn의 PMOS mp0는 다른 블록과 이어지지 않고 따로 떠 있음(전원 스위치로 그려짐). vref 선이 dq<3:0> 쪽으로 길게 돌아감. 그 외 눈에 띄는 오류 없음 |
| b_dq_lane | 없음 |

(b_dq_lane 외에 b_dq_afe 등은 열지 않음. 이 보고서에서 연 화면은 2장뿐이며, 지시된 3장이 아님. 다른 화면 한 장을 더 열지 못했다.)

## 그 밖에 적을 것
- 질문 답이 도구 기본값과 같았지만 지시에 따라 annotations.json을 쓰고 재실행함. 재실행 전후 숫자는 같음.
- rx_l5/rx_s5 netlist의 최상위 이름은 각각 rx_byte8, dqrx_slice.
