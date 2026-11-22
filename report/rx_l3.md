# rx_l3

## 실행
- 명령 (순서대로):
  1. `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out`
  2. `runs/rx_l3/annotations.json` 작성: `{"answers": {"ctl:wl_ck": "hs_data"}}` (분류 고침 없음)
  3. `python3 tool/hsio_draw.py exam/rx_l3/netlist.sp -o runs/rx_l3/out --annotations runs/rx_l3/annotations.json`
- 종료 코드와 마지막 요약 줄 (도구 출력 그대로):
  - 1차: 종료 코드 0 / `views 22, connectivity 22, quality 22` / `self-test: 131/131 injected errors caught; questions: 1; 74s`
  - 2차(답 반영): 종료 코드 0 / `views 22, connectivity 22, quality 22` / `self-test: 131/131 injected errors caught; questions: 0; 61s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로, 2차 실행 결과)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 22 / 22 / 22
- 꺾임 수 / 이름표로 이은 곳: 165 / 105 (1차 실행은 167 / 104)
- 검증기 오류 주입 (넣은 수 / 잡은 수): 131 / 131

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| 질문 `ctl:wl_ck` (포트 `wl_ck`) | 중요 제어 K9 "시험 입력" (기본값, 선택지 K9/K8/hs_data/hs_clock) | `hs_data` | `wl_ck`는 `xi39`(wldet)의 `d` 핀에만 연결되고, wldet 안에서 `dfftg`(xi2)의 `d` 입력이다. 이 플립플롭의 클럭은 `nand2x2`(xi0, `ck`=net222와 `en`=wl_en의 NAND) → `invx4`(xi1)를 거친 net106이다. 즉 고속 클럭으로 샘플되는 데이터 입력이고, 출력 `wl_out`은 플립플롭 Q에 나온다. 시험 전용 입력이라는 근거는 netlist에 없다. |

분류 표(classification.md)는 고친 것이 없다. 다만 `wl_ck` 행의 "근거" 칸에 도구가 쓴 "패드/차동쌍 → 입력 트랜지스터 → 샘플러 데이터 입력" 문구는 이 포트에 맞지 않는다(아래 "그 밖에" 참고).

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `runs/rx_l3/out/screenshots/b_rxbyte_top.png` (최상위) | 없음. `wl_ck`는 `wldet`의 `d`로, `wl_en`은 `en`으로 들어가고 `wl_out`이 나온다. `wldet`의 `ck`는 최상위에서 아래쪽을 돌아 `ckbuf` xi22 출력(net222)에 이어진다. 우회가 길지만 끊김은 없다. |
| `runs/rx_l3/out/screenshots/b_wldet.png` | 없음. 숨은 것 없이 `nand2x2` → `invx4` → `dfftg` → `invx1` → `invx4` 순서로 그렸다. |
| `runs/rx_l3/out/screenshots/b_dqslice.png` | 없음. 패드 쪽 `padesd`에서 `sbamp` 두 개와 `sadfe` 두 개로 나가고, `srnand`가 `qr`/`qf`를 낸다. 이름표 `net94`, `net95` 등이 한 번씩 맞게 쓰였다. |

## 그 밖에 적을 것
- 도구가 낸 질문의 근거 문구가 틀렸다. 질문 자체("고속 클럭으로 샘플되어 관찰용 출력으로만 간다")는 맞다. 하지만 `classification.md` 표의 `wl_ck` 근거 칸은 패드 경로를 가리키는 문구로 남아 있다. 이건 도구의 문구 문제다. 도구는 고치지 않았다.
- 도구의 판정 중 확신이 낮은 것은 없었다. 네 번째 화면 등은 열지 않았다(지시대로 세 장).
- 결정: `wl_ck`를 `K9`(시험 입력) 대신 `hs_data`로 답했다. 근거는 위 표의 netlist 경로다. 이 답을 반영하려고 한 번 더 돌렸다.
- 도구 출력의 `runs/rx_l3/out/annotations.json`은 도구가 만든 빈 틀이다. 내가 쓴 답은 `runs/rx_l3/annotations.json`에 있다.
