# 실사용 작업 흐름 — GLM(무제한) + Claude Code(토큰 제한)

> 전제: **사내 GLM(OpenCode)은 토큰 무제한, 사내 Claude Code는 토큰 제한.**
> 그래서 반복·대량 작업(코드 작성, 그리기, 검사기를 통과할 때까지 반복 수정)은 GLM이 하고,
> 판단·검토(분류 확인, 최종 검토, 수정 지시서 작성)는 Claude Code가 짧게 한다. 두 도구 사이는 **파일로만** 주고받는다.
> 규칙의 근거는 같은 폴더 위의 `DRAWING_PLAN.md`(명세서)와 `SKILL.md`(구현 가이드)다. 이 문서는 "누가·언제·무엇을"만 정한다.

---

## 1. 역할

| 단계 | 담당 | 받는 것 | 내는 것 | 지시문 |
|---|---|---|---|---|
| 0 | 사용자 | — | `input/netlist.sp`, `input/hints.md`(선택: 고속 입력·클럭 포트, 아는 블록) | — |
| 1 분류 초안 | **GLM** | netlist, hints, 명세서 전체 | `glm/out/classification.md`, `annotations.json`, `block_dictionary.json`, 질문 | `prompts/glm_1_classify.md` |
| 2 분류 검토 | **Claude** | 검토 묶음 `review/pack_classify/` (분류 표·사전 대응·질문·필요한 netlist 발췌) | `review/classify_review.md` (고칠 목록, 사용자에게 물을 것) | `prompts/claude_2_review_classify.md` |
| 3 확인 | **사용자** | 질문, Claude 검토 | `user/answers.md` (마지막 줄 `확인 완료`) | — |
| 4 그리기 | **GLM** | 확정 분류(answers 반영) | `glm/out/` 전부(명세서 §1.2) | `prompts/glm_4_draw.md` |
| 5 관문 | **검증 스크립트** | `glm/out/` | 자동 검사(체크리스트 M 묶음) 0건이면 통과 | (모델 없음) |
| 6 최종 검토 | **Claude** | 검토 묶음 `review/pack_rK/` (최상위 + 대표 화면 3–5장, 자동 검사 요약, 체크리스트, 분류 표) | `review/rK/checklist.json`, `fix_request.md` | `prompts/claude_6_review_final.md` |
| 7 수정 | **GLM** | `review/rK/fix_request.md` | 고친 `glm/out/` + 바뀐 화면 목록 | `prompts/glm_7_fix.md` |

- 5 → 6 → 7 → 5를 **최대 3라운드**. 3라운드 뒤에도 남는 것은 사용자에게 보고한다.
- **GLM의 자체 점검(`self_checklist.json`)은 합격 근거가 아니다.** 합격은 5(검증 스크립트)와 6(Claude)이 정한다. 시험에서 그린 쪽 검사기가 "전부 통과"라고 한 그림에 끊어진 선·교차·동그라미 누락이 있었다.
- **분류는 그리기 전에 확인한다(2–3단계).** 분류가 틀린 채 다 그리면 고치는 데 그림 전체를 다시 해야 한다.

## 2. 정답지는 필요 없다

정답지(설계자가 쓴 분류)는 명세서를 시험·개선할 때만 쓴다. 실사용에서는 아래가 대신한다.

| 정답지가 잡던 것 | 실사용에서 |
|---|---|
| 연결 | 그림의 기하만으로 연결을 다시 읽어 netlist와 비교 (검증 스크립트) |
| 극성 | 논리 출력마다 netlist에서 극성 계산 → 동그라미와 대조 (검증 스크립트) |
| 포트·제어 분류 | 2단계 Claude 검토 + **3단계 사용자 확인** (`annotations.json`이 자동 판정보다 우선) |
| 블록 역할 | `block_dictionary.json` (특징이 모두 맞을 때만 사전 기호) + Claude 검토 + 사용자 확인 |

체크리스트의 G 묶음(정답지)은 "해당 없음", N 묶음(이름 가림)도 "해당 없음"이다.
**회귀 시험 세트**: 스킬(명세서·도구)을 고칠 때는 정답지 딸린 시험 netlist로 다시 돌려 전에 맞던 것이 틀려지지 않았는지 본다. 실업무 netlist에서 새 문제가 나오면, 사용자가 확인한 `annotations.json`을 그 netlist의 정답지로 올려 세트에 더할 수 있다(사내에만 보관).

## 3. 작업 폴더

```
hsio_job_<회로명>/
  spec/        배포본 사본 (DRAWING_PLAN.md, SKILL.md, reference/, …)   둘 다 읽기만
  input/       netlist.sp, hints.md                                     사용자만 씀
  state.json   현재 단계·라운드·다음 담당                                  진행 담당만 씀
  glm/         work/ (GLM 코드), out/ (산출물)                            GLM만 씀
  review/      pack_*/ (검토 묶음), classify_review.md, r1/ r2/ r3/       Claude만 씀 (pack은 진행 담당이 만듦)
  user/        answers.md                                               사용자만 씀
  prompts/     단계별 지시문 (이 폴더의 prompts/ 사본)
  log.md       누가 언제 무엇을 했는지 (한 줄씩 덧붙임)
```

**소유 규칙**: 한 폴더는 한 쪽만 쓴다. Claude는 `glm/`을 고치지 않는다(검토하는 쪽이 그림을 고치면 독립 검증이 깨진다). GLM은 `review/`를 고치지 않는다.

## 4. `state.json`

```json
{"job": "<회로명>", "step": "1_classify", "round": 0, "max_rounds": 3,
 "next": "glm", "history": [["2026-11-15T10:00", "1_classify", "start"]]}
```
단계: `1_classify` → `2_review_classify` → `3_user_confirm` → `4_draw` → `5_gate` → `6_review_final` → (`7_fix` → `5_gate` → `6_review_final`)* → `done`.
6단계 `checklist.json`의 `verdict_drawing`이 PASS면 `done`, FAIL이면 `7_fix`, 라운드가 `max_rounds`면 `done`(남은 항목 보고).

## 5. 진행 방식

- **방식 1 — 수동**: 사용자가 `state.json`을 보고 해당 도구를 연다. GLM에는 "prompts/glm_N_*.md를 읽고 그대로 하라", Claude에는 "prompts/claude_N_*.md를 읽고 그대로 하라". 끝나면 도구가 `state.json`을 다음 단계로 바꾸고 `log.md`에 한 줄 남긴다.
- **방식 2 — 스크립트** (`orchestrate.py`): 모델이 아닌 코드가 상태 기계를 돌린다. GLM·Claude는 명령줄 비대화 실행으로 부른다(명령은 `orchestrate_config.json`에서 정한다. 예: GLM `opencode run …`, Claude `claude -p …`). 5단계 관문은 스크립트가 직접 판정하고, 3단계에서는 `user/answers.md`의 `확인 완료`를 기다린다. Claude에게는 스크립트가 만든 **검토 묶음**만 넘긴다(큰 netlist·화면 전체를 읽히지 않는다).
  - 이 초안은 실제 사내 GLM·Claude 없이 가짜 명령으로만 시험했다. 사내에서 `orchestrate_config.json`의 두 명령만 맞추면 된다.

## 6. Claude 토큰 아끼기

- Claude가 읽는 것은 **검토 묶음**뿐: 분류 표, `block_dictionary.json`, 질문, 자동 검사 요약, 최상위 + 대표 화면 3–5장, 필요한 netlist 발췌.
- 명세서는 전체가 아니라 필요한 절만 (분류 검토: §2.4–2.7, 최종 검토: §3, §4.2 J 묶음).
- 연결·교차·겹침·이름·극성·핀 방향처럼 기계로 볼 수 있는 것은 Claude가 다시 보지 않는다(5단계).
- 시험에서 측정한 규모(큰 netlist, MOS 4–7천 개): Claude가 혼자 다 하면 160만–200만 토큰, 이 분배로는 Claude 15만–30만 토큰 정도.
