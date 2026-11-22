# rx_l2

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_l2/netlist.sp -o runs/rx_l2/out`
  2. (questions.json에 질문 1개 → `runs/rx_l2/annotations.json` 작성 후)
     `python3 tool/hsio_draw.py exam/rx_l2/netlist.sp -o runs/rx_l2/out --annotations runs/rx_l2/annotations.json` (로그: `runs/rx_l2/rerun.log`)
- 종료 코드와 마지막 요약 줄 (도구 출력 그대로):
  - 1차: `views 26, connectivity 26, quality 26` / `self-test: 159/159 injected errors caught; questions: 1; 135s` / 종료 코드 0
  - 2차(답 반영): `views 26, connectivity 26, quality 26` / `self-test: 159/159 injected errors caught; questions: 0; 138s` / 종료 코드 0
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 213 / 103
- 검증기 오류 주입 (넣은 수 / 잡은 수): 159 / 159

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| 질문 `ctl:wl_ck` (포트 wl_ck) | 질문: 고속 클럭으로 샘플되는 데이터 입력 같지만 출력으로만 감. 기본 가정 K8 | K8 (명령/시험 입력) | `xi39 wl_ck net222 wl_en wl_out wldet` → wldet 내부 `xi2 d net106 net107 dfftg`: wl_ck는 플롭의 **D 입력**이고, 클럭은 net222(ckbuf 체인, dqs 경로에서 옴)이다. 결과는 `wl_out`(상태 출력, O1)으로만 나간다. 샘플러 데이터 입력(dq)이나 클럭 역할 게이트가 아니므로 고속 데이터(hs_data)·클럭(hs_clock)으로 보지 않았다. K9의 정의는 README에 없어 비교하지 못했고, 도구 기본값이며 README의 "명령/시험 입력" 설명과 맞아 K8을 택했다. |

분류 표 자체는 고치지 않았다(확신 있는 틀린 항목 없음).

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_pd (최상위) | 없음. 블록·선·이름표가 netlist 구조(VREF, dqsrx/dqsgate/dly3 경로, dqslice ×4 ×2, wldet)와 맞아 보인다. 다만 ckbuf 팬아웃 부분이 빽빽하다(도구 검사는 모두 통과). |
| b_wldet | 없음. `ck`→nand2x2(a), `en`→nand2x2(b), `d`→dfftg, `q`→invx4 순서가 netlist `wldet`과 맞다. |
| u_dqsamp | 없음. inp/inn 입력 쌍, en 게이트, vbn 꼬리, outp/outn 출력이 netlist `dqsamp`과 맞아 보인다. |

## 그 밖에 적을 것
- 질문 1개는 `runs/rx_l2/annotations.json`의 `answers`에 `ctl:wl_ck: K8`로 적고 다시 돌렸다. 2차 실행에서 질문이 0개가 되었고 분류 표에서 wl_ck 근거가 "사용자 답"으로 바뀌었다.
- 2차 실행 후 `runs/rx_l2/out/` 아래 PNG 26장과 PPTX는 같은 명령으로 다시 만들어졌다.
- 시험 지시문 외의 것은 바꾸지 않았다. `tool/`과 `exam/`은 건드리지 않았다.
