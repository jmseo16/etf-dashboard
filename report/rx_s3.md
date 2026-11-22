# rx_s3

## 실행
- 명령 (순서대로):
  1. `python3 tool/hsio_draw.py exam/rx_s3/netlist.sp -o runs/rx_s3/out`
  - 질문 0개이고 분류 고침이 없어서 두 번째 실행은 하지 않았다. `runs/rx_s3/annotations.json`도 만들지 않았다.
- 종료 코드와 마지막 요약 줄 (도구 출력 그대로): 종료 코드 0 / `views 15, connectivity 15, quality 15` / `self-test: 96/96 injected errors caught; questions: 0; 44s`
- 도구가 오류로 멈췄으면 오류 내용: 없음

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 15 / 15 / 15
- 꺾임 수 / 이름표로 이은 곳: 147 / 57
- 검증기 오류 주입 (넣은 수 / 잡은 수): 96 / 96

## 질문에 답한 것, 분류를 고친 것
없음

(분류 표의 `lb_en`(K2), `tap_sgn`(K2), `tap<3:0>`(K1), `ofe_*`/`ofo_*`/`ckdly<1:0>`(K7 숨김)은 netlist를 확인했고 도구 판정과 맞아서 그대로 두었다. `lb_en`은 `rx_pre`의 `sel_m`/`sel_l`을, `tap_sgn`은 `dfe_sum`의 `sgn`/`sgnb`를, `tap<3:0>`은 `dfe_sum`의 탭 전류 스위치를, `ofe`/`ofo`/`ckdly`는 `sa_dt`와 `ck_gate`의 MOS 커패시터 스위치를 구동한다.)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| `runs/rx_s3/out/screenshots/b_dq_rx_unit.png` (최상위) | 없음. 큰 우회 배선이 있지만 끊김이나 떠 있는 끝은 없었다. |
| `runs/rx_s3/out/screenshots/b_ck_gate.png` | 없음. `dly<1>`/`dly<0>`는 MOS 커패시터 스위치로 그려졌고, `ckt`/`ckc`는 `nor2_c`에서 `cko`/`ckob`까지 이어진다. |
| `runs/rx_s3/out/screenshots/u_dfe_sum.png` | 없음. `sgn`/`sgnb` 쌍으로 두 쌍의 교차 스위치가 `outp`/`outn`으로 가고, 탭 전류 스위치 `tap<3:0>`은 가로로 나란히 놓였다. |

## 그 밖에 적을 것
- 눈으로 본 것은 보고서에 적은 세 장이 전부다. 세부 배선을 하나씩 대조하지는 않았다.
