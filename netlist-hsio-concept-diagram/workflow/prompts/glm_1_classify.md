# GLM — 1단계: 분류 초안

너는 그리는 쪽이다. 작업 폴더의 `spec/DRAWING_PLAN.md`(명세서)와 `spec/SKILL.md`(구현 가이드)만 근거로 쓴다.
쓸 수 있는 폴더는 `glm/`뿐이다. `review/`, `user/`, `input/`은 읽기만 한다.

1. `input/netlist.sp`를 파싱·평탄화한다 (SKILL §4.1–4.3). `input/hints.md`가 있으면 확신도에만 쓴다.
2. 고속 데이터·클럭 추적(명세서 §2.3), 입력 포트 판정(§2.4), 제어·비고속 분류(§2.5 끝점 표)를 **구조로** 한다. 이름은 확신도에만.
3. 블록 역할을 사전 대응으로 정한다(§2.6). 사전 행의 특징이 모두 맞을 때만 사전 기호, 아니면 일반 박스 + 질문.
4. 질문은 확신이 낮은 것만, 템플릿 문장으로(§2.7). 규칙이 이미 정한 것은 묻지 않는다(netlist 오류 의심은 확인 질문).
5. 산출물 (`glm/out/`): `classification.md`(분류 표, 포트 표, 그리는 제어·숨긴 다비트 제어마다 K#·끝점 핀·출처, 질문과 가정한 답), `annotations.json`, `block_dictionary.json`.
6. 아직 그리지 않는다. 끝나면 `state.json`의 `step`을 `2_review_classify`, `next`를 `claude`로 바꾸고 `log.md`에 한 줄 남긴다.
