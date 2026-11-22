# rx_l1

## 실행
- 명령: `python3 tool/hsio_draw.py exam/rx_l1/netlist.sp -o runs/rx_l1/out` (한 번만 실행; annotations 없음, 재실행 없음)
- 종료 코드와 마지막 요약 줄: 종료 코드 0. `views 25, connectivity 25, quality 25` / `self-test: 150/150 injected errors caught; questions: 1; 120s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (120초가 걸려 셸의 120초 제한으로 백그라운드로 넘어갔으나 정상 종료)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 25 / 25 / 25
- 꺾임 수 / 이름표로 이은 곳: 192 / 97
- 검증기 오류 주입 (넣은 수 / 잡은 수): 150 / 150

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
| ctl:wl_ck (질문) | 가정 K8 | K8 (도구의 가정 그대로, annotations 안 씀) | `xi39 wl_ck net222 wl_en wl_out ... wldet`: wl_ck는 wldet의 d 핀으로 들어가 dfftg(xi2)가 샘플하고 출력 wl_out으로만 감. 시험/명령 입력으로 보는 게 타당 |

분류 수정: 없음 (틀렸다고 확신하는 항목 없음). 따라서 annotations.json은 만들지 않았고 재실행도 하지 않음.

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_top (최상위) | 없음. 참고: slp 스위치 mp0가 어디에도 이어지지 않은 채 net200 이름표로만 끝남(net200은 dqslice 쪽으로 쓰임). odtleg3(xi6)의 pad는 선 없이 `dqs_t` 이름표로 이음. xi38(더미 dqslice)과 ddl 등은 생략됨 |
| b_wldet | 없음 |
| b_dqsrx | 없음. 인버터 피드백 선이 위로 크게 돌아가지만 검사는 통과 |

## 그 밖에 적을 것
- 같은 폴더에서 이 실행과 무관해 보이는 다른 python 프로세스(다른 경로의 hsio_draw)가 보였으나 건드리지 않았다.
- 도구·exam 파일은 수정하지 않았다.
