# rx_l4

## 실행
- 명령:
  - `python3 tool/hsio_draw.py exam/rx_l4/netlist.sp -o runs/rx_l4/out`
- 종료 코드와 마지막 요약 줄: `EXIT:0`, `views 26, connectivity 26, quality 26`, `self-test: 156/156 injected errors caught; questions: 1; 151s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (정상 종료)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 270 / 235
- 검증기 오류 주입 (넣은 수 / 잡은 수): 156 / 156

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| `wl_ck` (questions.json: ctl:wl_ck) | 가정한 답 K9 | K9 동의 (그대로 둠) | netlist 466행 `rxbyte_eq` 포트 목록, 505행 `xi39 wl_ck net222 wl_en wl_out vdd vss wldet`. `wldet` 서브서킷(454행)은 `d ck en q`로, 호출 순서상 wl_ck가 `d`(데이터) 자리, net222가 `ck`(클럭) 자리에 들어간다. 즉 wl_ck는 클럭이 아니라 내부 클럭(net222)에 의해 샘플되는 데이터형 시험 입력이며 출력(wl_out)으로만 가므로 K9(시험 입력)이 맞다.

(분류 표는 추가로 고친 항목 없음)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_eq (최상위) | 없음. 포트·블록 배치, 이름표 연결 모두 깔끔함 |
| b_dqsrx | 없음. differential 입력/출력, 버퍼 체인 배선 정상 |
| u_sadfe1 | 없음. 트랜지스터 스택과 반복 인스턴스(×N) 배치 정상 |

## 그 밖에 적을 것
없음.
