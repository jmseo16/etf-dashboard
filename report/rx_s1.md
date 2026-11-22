# rx_s1

## 실행
- 명령:
  1. `python3 tool/hsio_draw.py exam/rx_s1/netlist.sp -o runs/rx_s1/out`
  2. `runs/rx_s1/annotations.json` 작성 (`net_class: {"tap_sgn": "K1"}`)
  3. `python3 tool/hsio_draw.py exam/rx_s1/netlist.sp -o runs/rx_s1/out --annotations runs/rx_s1/annotations.json`
- 종료 코드와 마지막 요약 줄:
  - 1차: 종료 코드 0 / `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 38s`
  - 2차(분류 고침 적용): 종료 코드 0 / `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 31s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 113 / 50
- 검증기 오류 주입 (넣은 수 / 잡은 수): 93 / 93

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| 포트 `tap_sgn` (분류 고침) | 경로 선택 K2 | K1 (가중치 부호) | `xi26`, `xi27`(`dfe_sum`)의 `sgn`/`sgnb` 입력. `dfe_sum` 안에서 `sgn`이 `mn8`/`mn9`(및 `mn6`/`mn7`) 쌍의 출력 연결을 교차시켜 탭 계수의 부호를 바꿈. 입력 경로(`lb_p`/`lb_n` 또는 `pad`)를 고르는 것이 아님. `tap<3:0>`(K1)과 같은 탭 계수의 일부로 판단 |

질문: 없음 (`questions.json`이 비어 있음)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `runs/rx_s1/out/screenshots/b_dq_rx_unit.png` (최상위) | 없음 |
| `runs/rx_s1/out/screenshots/u_rx_pre.png` | 없음 |
| `runs/rx_s1/out/screenshots/b_sa_dt.png` | 없음 |

## 그 밖에 적을 것
- `tap_sgn`의 K1 변경은 판단이다. K2("경로 선택")로 두면 도구 판정 그대로이므로, 이 한 항목이 다른 판단과 다를 수 있다.
- `lb_en`(K2)과 `pad`/`lb_p`/`lb_n`(데이터)은 도구 판정을 그대로 두었다. netlist상 `lb_en`은 `rx_pre` 경로 선택이 맞다고 봤다.
- 도구 파일(`tool/`)과 `exam/`은 건드리지 않았다.
