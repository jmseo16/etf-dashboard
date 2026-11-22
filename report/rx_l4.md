# rx_l4

## 실행
- 명령: (순서대로)
  1. `python3 tool/hsio_draw.py exam/rx_l4/netlist.sp -o runs/rx_l4/out` — 질문 1개 나옴 (`ctl:wl_ck`, 기본 가정 K9).
  2. `annotations.json`에 `ctl:wl_ck: hs_clock`을 적고 `--annotations runs/rx_l4/annotations.json`으로 재실행 — **잘못된 답이었음, 결과 폐기** (아래 "그 밖에" 참고).
  3. `annotations.json`을 `ctl:wl_ck: K9`로 고치고 같은 `--annotations` 명령으로 재실행 — **최종 결과**.
- 종료 코드와 마지막 요약 줄 (최종 실행):
  ```
  views 26, connectivity 26, quality 26
  self-test: 156/156 injected errors caught; questions: 0; 166s
  EXIT=0
  ```
  (1번 실행의 요약: `views 26, connectivity 26, quality 26` / `self-test: 156/156 injected errors caught; questions: 1; 147s` / `EXIT=0`)
- 도구가 오류로 멈췄으면 오류 내용: 없음. 다만 같은 머신에서 다른 프로세스가 같은 `runs/rx_l4/out`에 쓰고 있었다 (그 밖에 참고).

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 270 / 235
- 검증기 오류 주입 (넣은 수 / 잡은 수): 156 / 156

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `ctl:wl_ck` | K9 (시험 입력, 기본 가정) | K9 | `xi39 wl_ck net222 wl_en wl_out` → `wldet(d ck en q)`에서 `wl_ck`는 `d` 핀. `d`는 `xi2 dfftg`의 D로만 들어가고, 플롭 Q는 `xi4`를 거쳐 `wl_out`(출력 포트)으로만 나간다. 클럭 핀(`ck`)은 `net222`(내부 스트로브)에서 `wl_en`과 NAND로 만든 클럭이다. 즉 `wl_ck`는 클럭이 아니라 관찰용으로 넣는 데이터 입력이므로 K9. |

분류 표(`classification.md`)는 고치지 않았다. 확신하는 분류 오류가 없었다.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `b_rxbyte_eq` (최상위) | 없음. `wl_ck`가 `wldet`의 `d`, 스트로브가 `ck`에 붙은 것이 netlist와 일치. |
| `b_wldet` | 없음. `ck→nand2x2(en)→invx4→dfftg.ck`, `d→dfftg.d`, `q→invx1→invx4→q` 경로가 netlist와 일치. |
| `b_dqslice` | 없음. `ctledg`의 `vref` 입력, 두 `sadfe1`, 두 `srnand`, 출력 `qr`/`qf`의 연결이 netlist와 일치. |

## 그 밖에 적을 것
- **잘못 낸 답과 정정**: 1차로 `wl_ck`를 `hs_clock`으로 적었다. `wldet`의 핀 대응(`d`=`wl_ck`, `ck`=`net222`)을 잘못 읽은 결과였다. 화면과 netlist를 다시 대조해 K9로 되돌리고 최종 실행을 다시 했다. `hs_clock` 결과는 최종 산출물이 아니다.
- **같은 출력 폴더를 쓰는 다른 프로세스**: 실행 중에 같은 머신의 다른 `hsio_draw.py` 프로세스(같은 상대 경로 `runs/rx_l4/out`)가 같은 폴더에 쓰고 있었다. 그들을 제어할 수 없어서, 모든 프로세스가 끝난 뒤 `classification.md`(`wl_ck (K9)`, "사용자 답")와 `annotations.json`(`ctl:wl_ck: K9`)을 다시 읽어 최종 산출물이 맞는지 확인했다.
- 도구 실행 시간: 단독 147초, 경쟁 중에는 166–188초.
- `tool/`과 `exam/`은 수정하지 않았다.
