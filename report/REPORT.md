# 시험 보고 — 넷리스트로 고속 IO 개념도 그리기 (R0.2)

## 모델·환경
- 모델: Claude Sonnet 5.5 (claude-sonnet-5-5), 추론 설정은 기본값(알 수 없음). 한 모델이 그리는 역할(GLM)과 검토 역할(Claude)을 모두 했다 — 모든 검토에 "같은 모델이 검토함"을 적었다.
- 환경: Python 3.13, python-pptx 1.0.2, Node 22, Playwright + chromium(설치함), LibreOffice. 기준 결과 재현 성공 (17/17/17, 주입 57/57, expected 와 동일: `report/env_check.md`).

## 회차별 결과
| 회로 | 회차 | 화면 | 자동 검사 총 건수(첫 → 마지막) | 주입 | verdict (그림/명세) |
|---|---|---|---|---|---|
| rx_s1 | 0 분류 | — | — | — | — (질문 5개) |
| rx_s1 | 1 | 18 | 0 → 0 (a 단계 개발 중 86까지 관찰) | 32/32 | FAIL / FAIL |
| rx_s1 | 2 | 18 | 1 → 0 | 32/32 | FAIL / FAIL (남은 1건: u_sa_dt_stage2 교차 결합 인버터 쌍 CCI) |
| rx_l1 | 0 분류 | — | — | — | — (질문 8개) |
| rx_l1 | 1 | 9 (약 30 중) | 39 → 0 (6번) | 31/31 | FAIL / FAIL |

## 최종 산출물 경로
- rx_s1: `snapshots/rx_s1/r2_b_selftest/` (concept.html, concept.pptx, screenshots 18장, verify_report.json, self_checklist.json), 검토 `r2_c_review/`, 보고 `report/rx_s1/round_{0,1,2}.md`
- rx_l1: `snapshots/rx_l1/r1_b_selftest/` (9화면), 검토 `r1_c_review/`, 보고 `report/rx_l1/round_{0,1}.md`

## 끝내 못 한 것
- rx_s1: CCI(§3.3-7 90° 돌린 인버터 쌍) — 회전 MOS 기호가 도구·명세서에 없음. 회차 3 은 하지 않음(고칠 수 없어서). 검사기 미구현: §4.1 의 4, 7, 8, 9, 12, 17, 19, 20, 21, 22 (돌리지 않음으로 적었고 통과로 세지 않음).
- rx_l1: 화면의 약 2/3 미작성 (sadfe, dqsrx, acamp, dqsamp, dqsgate, lat_tg, dfftg, mux2tg, dly3, dlybuf, ckbuf, wldet, odtctl, lvlup, vrefdac, odtleg3), 비교기 +/− 표시, 합친 블록 범례, 회차 2·3. 분량·시간 부족.
- 두 회로 모두: 독립 검사기와 비교하지 못했다(검사기는 이번에 새로 짠 것). a 단계에서 rx_s1 회차 1 은 "검증기를 돌리기 전" 규칙을 지키지 못했다(새 도구를 만들며 개발용으로 돌림, selftest_log.md 에 공개); rx_s1 회차 2 와 rx_l1 회차 1 은 지켰다. rx_l1 의 checklist J7 에 PPTX "11장"이라고 적은 것은 틀렸고 실제 10장이다(정정).
- 기준 코드의 자동 분류(analyze.py)와 검증기(verify.py)는 새 회로에서 쓸 수 없어(예외·RX 이름 고정) 분류는 손으로, 검사기는 새로 만들었다.

## 배포 묶음에서 고쳤으면 하는 점
1. `analyze.py`·`verify.py`·`layouts.py` 가 RX AFE 이름(셀·인스턴스·포트)과 가정(차동 입력, 전원 한 쌍, 다이오드 없음)에 묶여 있어 "출발점으로 써도 된다"가 사실상 불가능하다. 일반 부분(파서, 기하 재추출, 품질 검사)과 RX 전용 부분(주입 시험 목록, 화면 id)을 분리해 주면 좋겠다.
2. 새 netlist 의 블록 화면 생성기는 SKILL §7 에 절차만 있고 코드가 없다. 경로 탐색(직선/ㄱ자/Z, 교차 시 이름표) 참조 구현이 필요하다.
3. 명세서 틈: 직렬 R 이 있는 ESD, MOS 커패시터, 필터를 거친 기준 전압, 회전된 MOS 기호(CCI), 합산 쌍 + 극성 선택 스위치 템플릿, 가상 전원을 만드는 헤더 스위치, 단일 디지털 포트가 샘플링 대상인 경우, 클럭 연결이 갈리는 반복 슬라이스, 합친 병렬 인스턴스(출력 단락).
4. 버스 이름 규칙(`<MSB:LSB>`)과 netlist 의 `w1_2` 식 이름의 대응(별칭)을 검사기가 어떻게 읽어야 하는지 명세서 §1.4-3 / §4.1-14 에 한 줄 적어 주면 좋겠다.
5. 시험 분량: 26셀·약 30화면 회로(rx_l1)는 지금 도구 수준에서 한 번에 끝내기 어렵다 — 화면 목록을 자동으로 뽑는 도구가 있으면 좋겠다.
