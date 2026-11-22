# rx_s2

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_s2/netlist.sp -o runs/rx_s2/out`
  (질문 0개, 고친 분류 없음 → annotations.json을 쓰지 않았고 다시 돌리지 않았다.)
- 종료 코드와 마지막 요약 줄 (도구 출력 그대로):
  - `views 14, connectivity 14, quality 13`
  - `self-test: 86/86 injected errors caught; questions: 0; 30s`
  - 종료 코드 1 (도구 문서: 모두 통과 0, 아니면 1)
- 도구가 오류로 멈췄으면 오류 내용: 멈추지는 않았다. 화면 `u_odt_ct`의 품질 검사가 실패했다 (`placement_problem: 1`, 세부: `label net15: no room`). 도구는 나머지 화면을 모두 만들었다. 도구는 고치지 않았다.

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 14 / 14 / 13
- 꺾임 수 / 이름표로 이은 곳: 118 / 55
- 검증기 오류 주입 (넣은 수 / 잡은 수): 86 / 86

## 질문에 답한 것, 분류를 고친 것
없음 (질문 0개. 분류 표를 검토했고 확신 있는 틀린 항목은 찾지 못했다. 예: `vref`=기준, `tap_sgn`/`lb_en`=경로 선택 K2, `ofe_*`/`ofo_*` 오프셋 트림 K7은 sa_sarm의 정적 스위치 구조와 맞다.)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_ct (최상위) | 없음. 블록 배치와 선 연결이 netlist(esd_gc, odt_ct, odt_dec2, rx_pre, dfe_sum5 ×2, sa_sarm ×2, sr_nand ×2, ck_gbuf)와 맞아 보인다. |
| u_odt_ct | 품질 검사 실패 대상. 저항 r5의 왼쪽 이름표 `net15`를 둘 자리가 없다는 검사 결과다(`label net15: no room`). 이 화면에서 시각적으로 큰 어긋남은 보이지 않았다. 도구 문제로 기록만 한다. |
| u_sa_sarm | 없음. 오프셋 트림 스위치 mn5–mn16 배치와 래치 구조가 netlist와 맞아 보인다. |

## 그 밖에 적을 것
- 도구의 품질 검사 1건 실패(`u_odt_ct`, 이름표 자리 부족)가 종료 코드 1의 원인이다. 시험 지시문에 따라 도구(`tool/`)는 고치지 않았다. 보고만 한다.
- 실패 화면은 `runs/rx_s2/out/screenshots/u_odt_ct.png`, 검증 세부는 `runs/rx_s2/out/verify_report.json`에 있다.
- `tool/`과 `exam/`은 건드리지 않았다.
