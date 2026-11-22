# rx_s1

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_s1/netlist.sp -o runs/rx_s1/out` (annotations 없음, 재실행 없음)
- 종료 코드와 마지막 요약 줄: 종료 코드 0. `views 15, connectivity 15, quality 15` / `self-test: 93/93 injected errors caught; questions: 0; 36s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 113 / 50
- 검증기 오류 주입 (넣은 수 / 잡은 수): 93 / 93

## 질문에 답한 것, 분류를 고친 것
없음 (질문 0개; classification.md의 분류도 틀렸다고 확신하는 것이 없어 그대로 둠. annotations.json 없음)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_dq_rx_unit (최상위) | 없음. 제어 디코딩 블록(odt_dec, inv/nand 체인)이 화면 아래에 따로 떠 있는 것처럼 보이나 출력은 이름표로 이어짐. vref가 r0·mn0(RC)로만 보임 |
| u_rx_pre | 없음 (트랜지스터 화면; 선이 길고 위쪽으로 크게 돌아가나 검사 통과). 출력 outp/outn이 캐패시터 mn8/mn9 뒤에 놓여 읽기 어려움 |
| b_sa_dt | 없음. 센스앰프 트랜지스터 화면으로, outn/outp/net62/net63 이름표가 여러 곳에 흩어져 추적이 힘듦 |

## 그 밖에 적을 것
- 도구·exam 파일은 수정하지 않았다.
