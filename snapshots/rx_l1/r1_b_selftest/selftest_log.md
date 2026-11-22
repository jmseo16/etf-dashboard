# selftest_log — rx_l1 회차 1

(형식: 실행 k | 검사별 건수 | 총 n건 | 이번에 고친 것) — 실행 1–5 는 c 단계 이전에 이 b 단계에서 검사기를 돌린 기록이다 (a 단계 snapshot 은 그 전에 저장함).
실행 1 | 1-conn:6, 2-label:1, 3-omit:4, 5-overlap:12, 5-endline:9, 6-port:3, 14-names:2, 18-pinside:2 | 총 39건 | 첫 실행 (그림 그대로)
실행 2 | 5-overlap:10, 5-endline:4 (나머지 0) | 총 14건 | 병합 ckbuf 소자 목록·이름 형식, 다이오드 뒤집기, 포트 위치, ddl 별칭, w2 핀 추가, 게이트 핀 분류, 합친 이름 "첫 … 끝" 검사 허용
실행 3 | 5-overlap:5, 5-endline:2 (나머지 0) | 총 7건 | 슬라이스 상자 폭·핀 간격, 스텁 길이 어긋나게
실행 4 | 5-endline:2 (나머지 0) | 총 2건 | SR 출력 핀 간격, SA 위쪽 핀 간격, PWR SW 상자 높이
실행 5 | 5-overlap:1 (나머지 0) | 총 1건 | AMP 위쪽 핀 스텁 길이 어긋나게
실행 6 | 1-conn:0, 1-touch:0, 10-outpin:0, 11-dash:0, 13-polarity:0, 14-names:0, 15-pinnames:0, 16-sha:0, 18-pinside:0, 2-label:0, 23-blockpins:0, 24-rcvalue:0, 25-inside:0, 3-omit:0, 5-cross:0, 5-dots:0, 5-endline:0, 5-kink:0, 5-overlap:0, 5-pierce:0, 5-short:0, 6-port:0 | 총 0건 | AMP 부제 글자 지움 (겹침 1건 → 0)
