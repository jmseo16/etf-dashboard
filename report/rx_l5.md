# rx_l5

## 실행
- 명령: (1) `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out` (첫 실행, 질문 1개)
  (2) 답 `runs/rx_l5/annotations.json` 작성 후 `python3 tool/hsio_draw.py exam/rx_l5/netlist.sp -o runs/rx_l5/out --annotations runs/rx_l5/annotations.json`
  (3) 다른 셸에서 같은 명령이 같은 출력 폴더에 동시에 돌고 있어, 그 실행들이 끝난 뒤 `rm -rf runs/rx_l5/out` 후 (2)와 같은 명령을 다시 돌렸다 (최종 결과물은 이 실행).
- 종료 코드와 마지막 요약 줄 (최종 실행): `EXIT=0`, `views 28, connectivity 28, quality 28`, `self-test: 179/179 injected errors caught; questions: 0; 88s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 28 / 28 / 28
- 꺾임 수 / 이름표로 이은 곳: 171 / 102
- 검증기 오류 주입 (넣은 수 / 잡은 수): 179 / 179

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `ctl:wl_ck` (포트 `wl_ck`) | 질문: K9 / K8 / hs_data / hs_clock 중 선택. 기본값 K9 | **K9** (시험 입력) | `xi39 wl_ck net222 wl_en wl_q ... wl_det` (netlist 456행). `wl_det` 안에서 `wl_ck`는 `xi2 dff`의 **D 입력**(`d`)에만 가고, 그 플롭의 클럭은 `net222`(ckdrv 출력, `xi38` 쪽 고속 클럭 경로)다. `wl_ck`의 다른 부하는 없고 출력 `wl_q`는 관찰용으로만 나간다. 고속 데이터 경로(`dq_lane`)에는 들어가지 않으므로 `hs_data`가 아니고, 클럭을 만드는 입력도 아니므로 `hs_clock`이 아니며, 명령 신호(K8)도 아니다. |

분류 표는 고치지 않았다(확신하는 오분류 없음).

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `b_rx_byte8` (최상위) | 이상한 점 없음. 화면상 `dq_lane` 블록 사이에 교차하는 선이 많은 편이다(검증기는 통과로 셌고, 교차 여부는 확대해서 확인하지 않음). `wl_ck` 입력은 `wl_det`의 `d` 핀에 바로 연결되어 있다. |
| `b_wl_det` | 이상한 점 없음. `en`(`wl_en`)은 `nd2x2`의 `b`, `ck`는 `a`로 들어가고, 출력 `q`는 `inv4`·`inv1`·`inv4` 체인을 거쳐 `wl_q`로 나간다. |
| `b_dq_lane` | 이상한 점 없음. `vref` → `dq_afe` → `dq_smp`, `ckt`·`ckc`는 아래 입력 포트로 연결됨. |

## 그 밖에 적을 것
- 같은 명령을 다른 셸에서 같은 출력 폴더에 여러 번 동시에 돌리는 일이 있었다. 그 실행들은 내가 시작하지 않았고 종료시키지 않았다. 모두 끝난 뒤 깨끗하게 다시 돌렸고, 최종 폴더는 그 단일 실행 결과다.
- 도구가 답을 반영하면서 `runs/rx_l5/out/annotations.json`에 `net_class: {"wl_ck": "K9"}`를 적어 넣었다(도구 동작). 내가 적은 원본 `runs/rx_l5/annotations.json`에는 `answers`만 있다.
