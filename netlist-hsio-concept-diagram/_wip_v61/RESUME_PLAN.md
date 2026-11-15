# 재개 계획 (19:09 KST 정지 → 23:10 KST 재개) — 배포 v6.1 진행 중

이 폴더(`_wip_v61/`)는 배포 전 작업물 사본이다. 배포가 끝나면 지운다.
원본 작업 폴더: scratchpad/loop/ (spec_v61_draft/, ref_v61/, iter4/). 컨테이너가 바뀌었으면 이 사본에서 이어간다.

## 남은 일 (순서)
1. **v6.1 명세서 마무리** (작성 에이전트 a4d17f9edb4e6aa21 재개): V73–V85(재검토 R1–R12 + 극성 주 입력)와 V86–V92(기준 결과 §11 교체 문안 반영, 부록 A 갱신, 이득 코드 정의 등)가 적용 중이었다. 어디까지 들어갔는지 C.8 표로 확인하고 나머지 적용. spec_lint 0.
2. **짧은 재검토** (검토 에이전트 a151423a1f5333cb0): V73–V92만, 배포 가능 판정.
3. **저장소 반영**: spec_v61_draft의 DRAWING_PLAN.md·SKILL.md → 저장소, ref_v61/reference/rx_afe/{work,expected} → reference/rx_afe/ (out/는 run_all.sh로 다시 생성, 17/17·expected 일치 확인).
4. **배포 번호 R0** (사용자 결정): 사내로 보내는 묶음은 명세서 버전과 따로 R0, R1 …로 번호를 붙인다. R0 = 명세서 v6.1.
   - 스킬 폴더에 `RELEASES.md`(배포 번호 | 날짜 | 명세서 버전 | 커밋 | 들어 있는 것 | 회사 발송) 표를 만들고 R0 행을 적는다.
   - `RELEASE_NOTES_R0.md`(사용법, 1–4회차 검증 요약, 알려진 한계 = C.9 + 정책 차이 V7/V14/V15 + orchestrate.py 실제 CLI 미검증 + 4회차 시험은 v5로 진행)를 스킬 폴더에 쓰고 SOURCE 묶음에 넣는다.
5. **묶음 파일** (Gmail: zip 불가 → 텍스트 묶음만): make_bundle.py FILES에 workflow/(WORKFLOW.md, prompts/*, orchestrate.py, orchestrate_config.json), spec_lint.py, make_bundle.py, RELEASES.md, RELEASE_NOTES_R0.md, reference 새 파일(work/spec_rules.py, expected/block_dictionary.json)을 넣는다. 묶음 맨 위 제목에 "Release 0 (R0) — 명세서 v6.1 — 커밋 <해시> — 날짜"를 적는다.
   - 결과 파일 2개: `releases/R0/HSIO_R0_SOURCE.md`(스킬 전체 + 복원 스크립트), `releases/R0/HSIO_R0_TESTS.md`(회귀 시험 세트). 둘 다 복원 검사(모든 파일 OK, 체크섬 불일치 0).
6. 커밋, 태그 `release-0`, push. `_wip_v61/` 삭제.
7. **사용자에게 파일 전달**: SendUserFile(display: attach)로 `HSIO_R0_SOURCE.md`, `HSIO_R0_TESTS.md`를 보낸다. 사내 메일이 .md를 막으면 .txt로 이름만 바꿔도 된다고 함께 알린다.

## 4회차 루프 (배포와 별개, 계속)
- E: 3라운드 수정 중이었음 (AGENT 2-E aa0b09614877ccf95 재개, fix_request_r2.md: 극성 주 입력·짧은 꺾임) → 끝나면 AGENT 3-E a5ea516b6f9ff2c00에 round3 검증.
- D·F·G: 그림 PASS로 종료.
