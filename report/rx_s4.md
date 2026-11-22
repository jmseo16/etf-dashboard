# rx_s4

## 실행
- 명령: (순서대로)
  1. `python3 tool/hsio_draw.py exam/rx_s4/netlist.sp -o runs/rx_s4/out` — 질문 0개. 분류 확인 후 고칠 항목이 있다고 판단.
  2. `annotations.json`에 `net_class: {vref: reference, tap<2>: K1, tap<1>: K1, tap<0>: K1}`을 적고 `--annotations runs/rx_s4/annotations.json`으로 재실행 — **최종 결과**.
- 종료 코드와 마지막 요약 줄 (최종 실행):
  ```
  views 15, connectivity 15, quality 15
  self-test: 93/93 injected errors caught; questions: 0; 205s
  EXIT=0
  ```
  (1번 실행의 요약: `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 227s` / `EXIT=0`)
- 도구가 오류로 멈췄으면 오류 내용: 없음. netlist에 `.subckt ck_gbuf`가 두 번 정의되어 있고 `** Library name` 줄이 중복되지만, 도구는 오류 없이 끝났다.

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 149 / 88
- 검증기 오류 주입 (넣은 수 / 잡은 수): 93 / 93

## 질문에 답한 것, 분류를 고친 것
질문은 없었다. 아래는 분류 표에서 확신하고 고친 항목이다.

| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `vref` | 중요 제어 — 켜기/끄기 (K3) | 기준 (reference) | `r0 vref net30 4k`, `r1 net30 net3 4k`, `mn0/mn1`(MOS 캡, 게이트가 net30/net3). `xi24 rx_pre_dg`에서 `inp=net1`, `vref=net3`. 즉 `vref`는 기준 전압 분압의 입력이고, 스위치가 아니다. |
| `tap<2>`, `tap<1>`, `tap<0>` | 중요 제어 — 켜기/끄기 (K3) | K1 (가중치, 탭 계수) | `dfe_sum3` 안에서 `tap<k>`가 `net55/56/57`과 `mn10/mp10`, `mn13/mp13`, `mn16/mp16`을 거쳐 `net58/59/60`을 구동하고, 이것이 합산 노드 `net54`의 꼬리 전류원 `mn12(m=4)`, `mn15(m=2)`, `mn18(m=1)`의 게이트다. 폭 비율이 4:2:1이므로 이진 가중 DFE 탭이다. `rx_l4`의 `t1w`(K1)와 같은 구조. |

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `b_dqrx_eq` (최상위) | 없음. `vref` 분압 → `net3`, `tap` 버스, `ofe/ofo` 경로가 netlist와 일치. |
| `b_dfe_sum3` | 연결 오류는 없음. 그러나 소자가 캔버스 왼쪽 위 일부에만 모여 있고 나머지는 빈 공간이다. 글자가 아주 작고, 긴 세로 배선이 아래쪽 접지 소자까지 내려간다. 읽기 어려움. |
| `b_sa_ci` | 연결 오류는 없음. 위와 같은 문제: 넓은 빈 공간, 긴 배선(아래쪽 소자까지), 작은 글자. |

## 그 밖에 적을 것
- 1차 실행에서 분류 표를 보고 `vref`와 `tap`을 고쳐 다시 돌렸다. 고친 근거는 위 표에 있다. 확신이 낮은 항목(`ofe`, `ofo`, `lb_p`/`lb_n`)은 그대로 두었다.
- 같은 머신에서 다른 `hsio_draw.py` 프로세스가 같은 `runs/rx_s4/out`에 쓰고 있었다. 모든 프로세스가 끝난 뒤 `classification.md`(`vref → 기준`, `tap<2:0> → K1 사용자 답`)와 `annotations.json`을 다시 읽어 최종 산출물이 맞는지 확인했다.
- 도구 실행 시간: 단독 227초(1차), 경쟁 중에는 205–228초.
- `tool/`과 `exam/`은 수정하지 않았다.
