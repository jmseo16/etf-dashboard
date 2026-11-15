#!/usr/bin/env python3
"""Run the GLM + Claude Code workflow of WORKFLOW.md as a state machine (방식 2).

The models never decide what happens next; this script does. GLM gets the long, repetitive steps,
Claude gets short review steps with a prepared review pack, the gate is decided here from the
deliverables, and the user-confirm step waits for user/answers.md to end with "확인 완료".

usage:
  python3 orchestrate.py init   JOB --netlist path/to/netlist.sp [--hints hints.md] [--spec SKILL_DIR]
  python3 orchestrate.py run    JOB [--config orchestrate_config.json]   # advance until it must wait or is done
  python3 orchestrate.py status JOB

Commands for the two models come from the config (see orchestrate_config.json). Placeholders:
  {job} job folder, {prompt_file} the prompt file written for this call, {prompt_text} its text.
Python 3.6+, standard library only.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["1_classify", "2_review_classify", "3_user_confirm", "4_draw", "5_gate",
         "6_review_final", "7_fix", "done"]
DEFAULT_CONFIG = {
    "glm_cmd": ["opencode", "run", "{prompt_text}"],
    "claude_cmd": ["claude", "-p", "{prompt_text}"],
    "timeout_s": 7200,
    "max_rounds": 3,
    "max_gate_retries": 3,
    "pack_views": 4,
}
PROMPT = {"1_classify": "glm_1_classify.md", "2_review_classify": "claude_2_review_classify.md",
          "4_draw": "glm_4_draw.md", "6_review_final": "claude_6_review_final.md", "7_fix": "glm_7_fix.md"}
SCRIPT_OWNS_STATE = ("\n\n(방식 2: state.json과 log.md는 orchestrate.py가 바꾼다. 너는 고치지 마라. "
                     "산출물만 정해진 폴더에 쓰고 끝내라.)\n")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def p(job, *parts):
    return os.path.join(job, *parts)


def load_state(job):
    with open(p(job, "state.json"), encoding="utf-8") as f:
        return json.load(f)


def save_state(job, st):
    with open(p(job, "state.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def log(job, who, msg):
    with open(p(job, "log.md"), "a", encoding="utf-8") as f:
        f.write("- %s · %s · %s\n" % (now(), who, msg))
    print("[%s] %s" % (who, msg))


def set_step(job, st, step, note):
    st["step"] = step
    st["next"] = {"1_classify": "glm", "4_draw": "glm", "7_fix": "glm", "2_review_classify": "claude",
                  "6_review_final": "claude", "3_user_confirm": "user", "5_gate": "script",
                  "done": "-"}[step]
    st["history"].append([now(), step, note])
    save_state(job, st)


def cmd_init(a):
    job = a.job
    for d in ("spec", "input", "glm/out", "glm/work", "review", "user", "prompts"):
        os.makedirs(p(job, d), exist_ok=True)
    shutil.copy(a.netlist, p(job, "input", "netlist.sp"))
    if a.hints:
        shutil.copy(a.hints, p(job, "input", "hints.md"))
    spec = a.spec or os.path.dirname(HERE)
    for name in ("DRAWING_PLAN.md", "SKILL.md"):
        if os.path.exists(os.path.join(spec, name)):
            shutil.copy(os.path.join(spec, name), p(job, "spec", name))
    if os.path.isdir(os.path.join(spec, "reference")) and not os.path.exists(p(job, "spec", "reference")):
        shutil.copytree(os.path.join(spec, "reference"), p(job, "spec", "reference"))
    for f in os.listdir(os.path.join(HERE, "prompts")):
        shutil.copy(os.path.join(HERE, "prompts", f), p(job, "prompts", f))
    if not os.path.exists(p(job, "user", "answers.md")):
        with open(p(job, "user", "answers.md"), "w", encoding="utf-8") as f:
            f.write("# 질문 답\n\n<!-- review/classify_review.md의 사용자 질문(최대 10개)에만 답하고, 맨 마지막 줄에 확인 완료 네 글자만 쓴다 -->\n")
    st = {"job": os.path.basename(os.path.abspath(job)), "step": "1_classify", "round": 0,
          "gate_retries": 0, "next": "glm", "history": [[now(), "1_classify", "init"]]}
    save_state(job, st)
    open(p(job, "log.md"), "a").close()
    log(job, "orchestrate", "작업 폴더 준비 완료")


def run_model(job, cfg, who, step, extra):
    with open(p(job, "prompts", PROMPT[step]), encoding="utf-8") as f:
        text = f.read()
    text = "작업 폴더: %s\n%s\n\n%s%s" % (os.path.abspath(job), extra, text, SCRIPT_OWNS_STATE)
    pf = p(job, "review" if who == "claude" else "glm", "_prompt_%s.md" % step)
    with open(pf, "w", encoding="utf-8") as f:
        f.write(text)
    tmpl = cfg["%s_cmd" % who]
    argv = [s.replace("{job}", os.path.abspath(job)).replace("{prompt_file}", os.path.abspath(pf))
            .replace("{prompt_text}", text) for s in tmpl]
    log(job, who, "%s 시작" % step)
    r = subprocess.run(argv, cwd=job, timeout=cfg["timeout_s"])
    if r.returncode != 0:
        raise SystemExit("%s 명령이 실패했다 (exit %d). log.md를 보고 다시 run 하라." % (who, r.returncode))
    log(job, who, "%s 끝" % step)


def need(job, *rel):
    missing = [x for x in rel if not os.path.exists(p(job, x))]
    if missing:
        raise SystemExit("산출물이 없다: %s — 같은 단계를 다시 run 하라." % ", ".join(missing))


def copy_if(src, dst_dir):
    if os.path.exists(src):
        shutil.copy(src, dst_dir)


def build_pack(job, name, views=0):
    pack = p(job, "review", name)
    os.makedirs(pack, exist_ok=True)
    for f in ("classification.md", "annotations.json", "block_dictionary.json", "self_checklist.json"):
        copy_if(p(job, "glm", "out", f), pack)
    vr = p(job, "glm", "out", "verify_report.json")
    if os.path.exists(vr):
        with open(vr, encoding="utf-8") as f:
            rep = json.load(f)
        with open(os.path.join(pack, "verify_summary.json"), "w", encoding="utf-8") as f:
            json.dump({"summary": rep.get("summary"), "auto_checks": rep.get("auto_checks")}, f,
                      ensure_ascii=False, indent=1)
    if views:
        shots = p(job, "glm", "out", "screenshots")
        if os.path.isdir(shots):
            names = sorted(os.listdir(shots))
            top = [n for n in names if n.startswith("b_top")]
            blocks = sorted([n for n in names if n.startswith("b_") and n not in top],
                            key=lambda n: -os.path.getsize(os.path.join(shots, n)))
            for n in top + blocks[:views]:
                shutil.copy(os.path.join(shots, n), pack)
    return pack


def gate(job):
    """M-group gate from the deliverables: verify summary all pass and every auto check zero."""
    need(job, "glm/out/verify_report.json")
    with open(p(job, "glm", "out", "verify_report.json"), encoding="utf-8") as f:
        rep = json.load(f)
    s = rep.get("summary") or {}
    problems = []
    if not s or not (s.get("views") == s.get("connectivity_pass") == s.get("quality_pass")):
        problems.append("verify summary %s" % s)
    sc = p(job, "glm", "out", "self_checklist.json")
    if os.path.exists(sc):
        with open(sc, encoding="utf-8") as f:
            ac = (json.load(f) or {}).get("auto_checks") or {}
        items = ac.items() if isinstance(ac, dict) else enumerate(ac)
        for k, v in items:
            n = v.get("count", v.get("violations", 0)) if isinstance(v, dict) else v
            ok = v.get("pass", n in (0, None)) if isinstance(v, dict) else n in (0, None, True)
            if not ok:
                problems.append("auto_check %s = %s" % (k, n))
    return problems


def cmd_run(a):
    job = a.job
    cfg = dict(DEFAULT_CONFIG)
    cf = a.config or os.path.join(HERE, "orchestrate_config.json")
    if os.path.exists(cf):
        with open(cf, encoding="utf-8") as f:
            cfg.update(json.load(f))
    st = load_state(job)
    while True:
        step = st["step"]
        if step == "1_classify":
            run_model(job, cfg, "glm", step, "단계: 분류 초안")
            need(job, "glm/out/classification.md", "glm/out/block_dictionary.json")
            set_step(job, st, "2_review_classify", "분류 초안 완료")
        elif step == "2_review_classify":
            pack = build_pack(job, "pack_classify")
            run_model(job, cfg, "claude", step, "단계: 분류 검토. 검토 묶음: %s" % pack)
            need(job, "review/classify_review.md")
            set_step(job, st, "3_user_confirm", "분류 검토 완료")
        elif step == "3_user_confirm":
            with open(p(job, "user", "answers.md"), encoding="utf-8") as f:
                lines = [x.strip() for x in f if x.strip()]
            if not lines or lines[-1].strip("-*# ") != "확인 완료":
                log(job, "orchestrate", "사용자 답을 기다린다: review/classify_review.md의 질문(최대 10개)에 "
                                        "user/answers.md로 답한 뒤 마지막 줄에 '확인 완료'를 쓰고 다시 run")
                return
            set_step(job, st, "4_draw", "사용자 확인 완료")
        elif step == "4_draw":
            run_model(job, cfg, "glm", step, "단계: 그리기")
            set_step(job, st, "5_gate", "그리기 완료")
        elif step == "5_gate":
            problems = gate(job)
            if problems:
                st["gate_retries"] += 1
                log(job, "orchestrate", "관문 불통과 (%d/%d): %s" % (st["gate_retries"], cfg["max_gate_retries"],
                                                                 "; ".join(problems)))
                if st["gate_retries"] > cfg["max_gate_retries"]:
                    set_step(job, st, "done", "관문 재시도 한도 초과 — 사용자 보고")
                    log(job, "orchestrate", "멈춤: 자동 검사가 0건이 되지 않는다. glm/out/verify_report.json을 확인하라")
                    return
                with open(p(job, "review", "gate_fail.md"), "w", encoding="utf-8") as f:
                    f.write("# 관문 불통과 — 자동 검사가 0건이 아니다\n\n" + "\n".join("- " + x for x in problems))
                prev = "4_draw" if st["round"] == 0 else "7_fix"
                st["history"].append([now(), prev, "관문 불통과로 다시"])
                run_model(job, cfg, "glm", prev, "단계: 관문 불통과 수정. review/gate_fail.md의 자동 검사를 0건으로 만들어라.")
                save_state(job, st)
                continue
            st["gate_retries"] = 0
            st["round"] += 1
            set_step(job, st, "6_review_final", "관문 통과 (라운드 %d)" % st["round"])
        elif step == "6_review_final":
            k = st["round"]
            pack = build_pack(job, "pack_r%d" % k, views=cfg["pack_views"])
            os.makedirs(p(job, "review", "r%d" % k), exist_ok=True)
            run_model(job, cfg, "claude", step, "단계: 최종 검토 라운드 %d. 검토 묶음: %s. 결과는 review/r%d/에." % (k, pack, k))
            need(job, "review/r%d/checklist.json" % k)
            with open(p(job, "review", "r%d" % k, "checklist.json"), encoding="utf-8") as f:
                verdict = json.load(f).get("verdict_drawing")
            if verdict == "PASS":
                set_step(job, st, "done", "그림 PASS (라운드 %d)" % k)
            elif k >= cfg["max_rounds"]:
                set_step(job, st, "done", "라운드 한도 — 남은 항목은 review/r%d/checklist.json" % k)
            else:
                need(job, "review/r%d/fix_request.md" % k)
                set_step(job, st, "7_fix", "그림 FAIL (라운드 %d)" % k)
        elif step == "7_fix":
            k = st["round"]
            run_model(job, cfg, "glm", step, "단계: 수정. 수정 요청: review/r%d/fix_request.md" % k)
            set_step(job, st, "5_gate", "수정 완료 (라운드 %d)" % k)
        elif step == "done":
            log(job, "orchestrate", "완료: %s" % st["history"][-1][2])
            return
        st = load_state(job)


def cmd_status(a):
    st = load_state(a.job)
    print(json.dumps({k: st[k] for k in ("job", "step", "round", "next")}, ensure_ascii=False))
    for h in st["history"][-5:]:
        print("  ", h)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    i = sub.add_parser("init"); i.add_argument("job"); i.add_argument("--netlist", required=True)
    i.add_argument("--hints"); i.add_argument("--spec")
    r = sub.add_parser("run"); r.add_argument("job"); r.add_argument("--config")
    s = sub.add_parser("status"); s.add_argument("job")
    a = ap.parse_args()
    {"init": cmd_init, "run": cmd_run, "status": cmd_status}.get(a.cmd, lambda _: ap.print_help())(a)


if __name__ == "__main__":
    main()
