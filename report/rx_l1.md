# rx_l1

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l1/netlist.sp -o runs/rx_l1/out`
  2. `runs/rx_l1/annotations.json` 작성 (`answers: {"ctl:wl_ck": "K8"}`)
  3. `python3 tool/hsio_draw.py exam/rx_l1/netlist.sp -o runs/rx_l1/out --annotations runs/rx_l1/annotations.json`
- 종료 코드와 마지막 요약 줄:
  - 1차: 종료 코드 0 / `views 25, connectivity 25, quality 25` / `self-test: 150/150 injected errors caught; questions: 1; 117s`
  - 2차(답 적용): 종료 코드 0 / `views 25, connectivity 25, quality 25` / `self-test: 150/150 injected errors caught; questions: 0; 84s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 25 / 25 / 25
- 꺾임 수 / 이름표로 이은 곳: 192 / 97
- 검증기 오류 주입 (넣은 수 / 잡은 수): 150 / 150

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| 질문 `ctl:wl_ck` | 명령 K8 (가정한 답) | K8 | `xi39 wl_ck net222 wl_en wl_out` → `wldet`의 `d` 핀. `wldet` 안의 `dfftg`가 `net222`(= `xi22` ckbuf 체인으로 온 DQS 지연 클럭, 더미 슬라이스 `xi38`의 `ckt`와 같은 넷)로 wl_ck를 샘플함. wl_ck는 데이터 슬라이스(`xi30`–`xi37`)로 가지 않고 wl_out 한 곳으로만 감. 고속 데이터 경로가 아니라 명령 비트로 판단. 시험 입력(K9)은 아님 |

분류 고침: 없음 (도구의 분류 표는 netlist와 모두 맞다고 판단)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `runs/rx_l1/out/screenshots/b_rxbyte_top.png` (최상위) | 없음 |
| `runs/rx_l1/out/screenshots/b_dqslice.png` | SA 기호(`sadfe`) 아래쪽 클럭 핀 표시 `ck`가 삼각형 기호와 겹쳐 글자가 일부 가려짐 |
| `runs/rx_l1/out/screenshots/b_dfftg.png` | 없음 |

## 그 밖에 적을 것
- 질문은 1개, 답은 K8로 적었다. 확신은 중간 정도이며, K9 또는 hs_data일 가능성은 netlist 구조상 낮다고 봤다.
- 도구 파일(`tool/`)과 `exam/`은 건드리지 않았다.
- 2차 실행 결과에서 화면 수와 검사 수는 1차와 같다.
