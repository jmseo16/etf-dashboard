# rx_l5

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out`
  2. `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out --annotations runs/rx_l5/annotations.json`
- 종료 코드와 마지막 요약 줄:
  1. 0 / `views 28, connectivity 28, quality 28` / `self-test: 179/179 injected errors caught; questions: 1; 92s`
  2. 0 / `views 28, connectivity 28, quality 28` / `self-test: 179/179 injected errors caught; questions: 0; 90s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (멈추지 않음)

## 숫자 (draw_report.md에서 그대로, 2차 실행 기준)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 28 / 28 / 28
- 꺾임 수 / 이름표로 이은 곳: 171 / 102
- 검증기 오류 주입 (넣은 수 / 잡은 수): 179 / 179

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `wl_ck` (질문 id `ctl:wl_ck`) | 확신 없음 (기본값 K9) | K9 | `xi39 wl_ck net222 wl_en wl_q vdd vss wl_det` — `wl_det` 서브서킷(`.subckt wl_det d ck en q vdd vss`)에서 `ck`(=wl_ck)는 `en`과 NAND(xi0)된 뒤 inv(xi1)를 거쳐 `dff`(xi2)의 클럭 핀으로 들어가고, `dff`는 `d`(=wl_q, 저속 상태 신호)를 샘플링해 `q`(=wl_q 출력, 관찰용)로 내보낸다. 즉 wl_ck는 데이터가 아니라 저속 상태 신호를 솎아내는 샘플 클럭이며 결과는 모니터링 출력(wl_q)에만 쓰이므로, 질문 문구("고속 클럭으로 샘플되어 관찰용 출력으로만 감")와 도구의 기본값(K9)이 타당하다고 판단해 그대로 답했다. |

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rx_byte8 (최상위) | 없음 |
| b_wl_det | 없음 |
| b_dly_line | 없음 |

## 그 밖에 적을 것
questions.json의 질문 1개(`ctl:wl_ck`)에 netlist 구조를 근거로 기본값 K9을 그대로 답해 annotations.json을 작성하고 재실행했으며, 재실행 후 질문은 0개가 되었고 분류표의 다른 항목 중에는 확신을 갖고 틀렸다고 판단한 것이 없어 추가로 고치지 않았다.
