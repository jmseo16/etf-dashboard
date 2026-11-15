# 재개 계획 (19:09 KST 정지 → 23:10 KST 재개) — 배포 v6.1 진행 중

이 폴더(`_wip_v61/`)는 배포 전 작업물 사본이다. 배포가 끝나면 지운다.
원본 작업 폴더: scratchpad/loop/ (spec_v61_draft/, ref_v61/, iter4/). 컨테이너가 바뀌었으면 이 사본에서 이어간다.

## 남은 일 (순서)
1. **v6.1 명세서 마무리** (작성 에이전트 a4d17f9edb4e6aa21 재개): V73–V85(재검토 R1–R12 + 극성 주 입력)와 V86–V92(기준 결과 §11 교체 문안 반영, 부록 A 갱신, 이득 코드 정의 등)가 적용 중이었다. 어디까지 들어갔는지 C.8 표로 확인하고 나머지 적용. spec_lint 0.
2. **짧은 재검토** (검토 에이전트 a151423a1f5333cb0): V73–V92만, 배포 가능 판정.
3. **저장소 반영**: spec_v61_draft의 DRAWING_PLAN.md·SKILL.md → 저장소, ref_v61/reference/rx_afe/{work,expected} → reference/rx_afe/ (out/는 run_all.sh로 다시 생성, 17/17·expected 일치 확인).
4. **RELEASE.md** 작성 (버전, 사용법, 1–4회차 검증 요약, 알려진 한계 = C.9 + 정책 차이 V7/V14/V15 + orchestrate.py 실제 CLI 미검증 + 4회차 시험은 v5로 진행).
5. make_bundle.py FILES에 workflow/, spec_lint.py, RELEASE.md, reference 새 파일(spec_rules.py, expected/block_dictionary.json) 추가 → SOURCE_BUNDLE.md, TESTS_BUNDLE.md 다시 만들고 복원 검사.
6. 커밋, 태그 `hsio-concept-v6.1`, push. `_wip_v61/` 삭제.

## 4회차 루프 (배포와 별개, 계속)
- E: 3라운드 수정 중이었음 (AGENT 2-E aa0b09614877ccf95 재개, fix_request_r2.md: 극성 주 입력·짧은 꺾임) → 끝나면 AGENT 3-E a5ea516b6f9ff2c00에 round3 검증.
- D·F·G: 그림 PASS로 종료.
