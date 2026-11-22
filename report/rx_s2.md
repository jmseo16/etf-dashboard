# rx_s2 (dq_rx_ct)

## 실행
- 명령:
  - `python3 tool/hsio_draw.py exam/rx_s2/netlist.sp -o runs/rx_s2/out`
- 종료 코드와 마지막 요약 줄: `EXIT:1`, `views 14, connectivity 14, quality 13` / `self-test: 86/86 injected errors caught; questions: 0; 30s`
- 도구가 오류로 멈췄으면 오류 내용: 멈추지 않음. 다만 화면 `u_odt_ct`에서 품질 검사가 실패해 종료 코드가 1이 되었다 (`verify_report.json`: `placement_problem: 1`, 세부 사유 `"label net15: no room"` — net15 이름표를 놓을 자리가 부족하다는 경고).

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 14 / 14 / 13
- 꺾임 수 / 이름표로 이은 곳: 118 / 55
- 검증기 오류 주입 (넣은 수 / 잡은 수): 86 / 86

## 질문에 답한 것, 분류를 고친 것
없음 (questions.json에 질문 없음, 분류 표도 구조적으로 정해져 있어 틀렸다고 확신할 항목이 없었다)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_ct (최상위) | 없음 |
| u_odt_ct | 품질 검사가 "실패"로 표시된 화면. 그림 자체는 겉보기엔 깨끗해 보이지만 `net15` 이름표가 r5 저항 옆(mn2 열)에 비좁게 붙어 있어, 검증기가 지적한 "자리 부족" 문제가 이 부근으로 추정된다. |
| u_dfe_sum5 | 없음 |

## 그 밖에 적을 것
- `u_odt_ct`의 품질 실패는 지시문에 따라 도구/그림을 고치지 않고 그대로 두었다.
