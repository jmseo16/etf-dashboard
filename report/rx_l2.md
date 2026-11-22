# rx_l2

## 실행
- 명령: `for c in rx_l2 rx_s2; do python3 tool/hsio_draw.py exam/$c/netlist.sp -o runs/$c/out | tail -8; done` (두 회로를 한 반복문으로 실행. 120초 제한으로 백그라운드로 넘어갔지만 끝까지 돌았음. 이 회로는 138초 걸림)
- 종료 코드와 마지막 요약 줄: 종료 코드 0. `views 26, connectivity 26, quality 26` / `self-test: 159/159 injected errors caught; questions: 1; 138s`
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 213 / 103
- 검증기 오류 주입 (넣은 수 / 잡은 수): 159 / 159

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| ctl:wl_ck | K8 (가정한 답) | K8 (도구 가정 그대로 수용) | `xi39 wl_ck net222 wl_en wl_out vdd vss wldet`: wl_ck는 wldet의 d 입력이고 net222가 샘플 클럭. wldet 안에서 dfftg로 샘플되어 wl_out으로만 감. 명령/시험 입력으로 보는 것이 타당하다고 판단. |

바꾼 것이 없으므로 annotations.json을 만들지 않았고 다시 돌리지 않았다. 분류 표에서 틀렸다고 확신하는 항목은 없었다.
답하거나 고친 항목 수: 질문 1개에 답함(도구 가정과 같음), 분류 수정 0.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_pd (최상위) | 없음. 전원 스위치 mp0(slp)는 net200/vdd에 연결되어 다른 블록과 선이 없는 채 따로 그려짐(전원 기호 표현으로 보임). |
| b_wldet | 없음. nand2x2 → invx4 → dfftg → invx1 → invx4 흐름이 netlist와 같음. |
| b_dqslice | 열지 않음. 대신 b_wldet 외에 다른 화면을 열지 못했음(아래 참고). |

(정직하게: 지시는 최상위 외에 다른 화면 두 장이나 rx_l2에서는 b_rxbyte_pd, b_wldet 두 장만 열었다. rx_s2 쪽 세 장은 그 보고서에 있음.)

## 그 밖에 적을 것
- 도구·exam 파일은 고치지 않았다.
- 그림 판독은 눈으로 본 수준이며 모든 선을 netlist와 대조하지는 않았다.
