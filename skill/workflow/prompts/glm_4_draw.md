# GLM — 4단계: 그리기 (검증 스크립트를 통과할 때까지 반복)

1. `review/classify_review.md`의 고칠 목록과 `user/answers.md`를 반영해 분류를 확정한다. 사용자 답은 자동 판정보다 우선이다(`annotations.json`에 기록).
2. 명세서 §3(화면 구성, 블록·유닛 레벨, 기호, 이름표·버스·생략 목록)대로 모든 화면을 그린다. SKILL §5–§8의 수치·템플릿을 그대로 쓴다.
3. 검증기는 `spec/reference/rx_afe/work/verify.py`에서 시작해 넓힌다. 처음부터 새로 짜지 않는다. 명세서 §4.1의 자동 검사를 모두 넣고, 검사마다 오류를 일부러 넣어 잡히는지 시험한다(§4.1의 필수 오류 주입 목록).
4. 자동 검사가 **0건**이 될 때까지 고친다. 0건이 아닌데 다음 단계로 넘기지 않는다.
5. 산출물은 명세서 §1.2 전부(`concept.html` 한 파일에 PPTX 내장, `concept.pptx`, `classification.md`, `annotations.json`, `block_dictionary.json`, `verify_report.json`(화면마다 `scene_sha`), `self_checklist.json`, `screenshots/`).
6. 끝나면 `state.json`을 `5_gate`로 바꾸고 `log.md`에 한 줄.
