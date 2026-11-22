# rx_l2 (rxbyte_pd)

## 실행
- 명령:
  - `python3 tool/hsio_draw.py exam/rx_l2/netlist.sp -o runs/rx_l2/out`
- 종료 코드와 마지막 요약 줄: `EXIT:0`, `views 26, connectivity 26, quality 26` / `self-test: 159/159 injected errors caught; questions: 1; 134s`
- 도구가 오류로 멈췄으면 오류 내용: 없음 (정상 종료)

## 숫자 (draw_report.md에서 그대로)
- 화면 수 / 연결 검사 통과 / 품질 검사 통과: 26 / 26 / 26
- 꺾임 수 / 이름표로 이은 곳: 213 / 103
- 검증기 오류 주입 (넣은 수 / 잡은 수): 159 / 159

## 질문에 답한 것, 분류를 고친 것
| 항목 | 도구의 판정 | 내 답 | 근거 (netlist의 어느 소자·넷) |
|---|---|---|---|
(없음 — `wl_ck` 질문은 도구의 가정한 답(K8, 중요 제어-명령)이 netlist와 맞다고 판단했다. `xi39 wl_ck net222 wl_en wl_out wldet`에서 `wldet`은 `d`를 `ck`(net222, ckbuf 체인에서 온 고속 클럭)로 샘플링하는 `dfftg`를 쓰므로, wl_ck는 고속 클럭이 아니라 그 클럭으로 래치되는 데이터성 명령 입력이 맞다. 확신이 서므로 고치지 않았다.)

## 그림에서 본 것 (연 화면 3장)
| 화면 | 이상한 점 (없으면 "없음") |
|---|---|
| b_rxbyte_pd (최상위) | 없음 |
| b_dqsrx | 없음 |
| b_sadt_dfe | 왼쪽 위 테일 트랜지스터 박스(mp7/mp2 부근)가 다른 선·글자와 겹쳐 보이고, 가장 긴 가로 배선 몇 개가 화면 전체 폭을 가로질러 길게 뻗어 있어 한눈에 보기 어렵다. (검사는 통과했으므로 연결 자체는 맞는 것으로 보임)

## 그 밖에 적을 것
- questions.json의 질문 1개는 가정한 답(K8)을 그대로 받아들이고 재실행하지 않았다(annotations.json 작성 안 함).
