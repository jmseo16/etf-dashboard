#!/usr/bin/env python3
"""Keep the spec from turning into patchwork. Run before every commit that touches the spec.

usage: python3 spec_lint.py [folder]      (default: this script's folder)
exit 0 = clean, 1 = problems (each printed as FAIL <check>: <detail>).

Rules enforced (DRAWING_PLAN.md v6+, appendix C "명세서 고치는 규칙"):
  1. skeleton   — the '## ' chapters are exactly SKELETON; '### ' numbers sit under an existing
                  chapter and run 1, 2, 3 ... without gaps.
  2. markers    — no override/patch markers in the body (outside the header block and appendix C):
                  struck text, "대체", "이긴다", "(바꿈)", "vN:" version tags.
  3. refs       — every §N / §N.M reference in DRAWING_PLAN.md (outside appendix C) and every "계획서 §" reference in
                  SKILL.md points at an existing chapter / sub-section.
  4. checklist  — the checklist sub-section has one table; ids match M\\d+ | J\\d+ | G1[a-d] | N\\d+,
                  are unique, and every row cites at least one § or 부록 reference.
  5. history    — the version in the status line appears in appendix C.
  6. skill-top  — SKILL.md has no stacked "명세서 vN" notes before its first '## ' heading.
"""
import os
import re
import sys

SKELETON = ["0", "1", "2", "3", "4", "부록 A", "부록 B", "부록 C"]
BODY_MARKERS = [
    (r"~~", "struck text"),
    (r"대체(됨|된다|되며|되고)|§[\d.\-]+[^|\n]{0,15}(로|으로) 대체", "'대체' (superseded) note"),
    (r"(§[\d.\-]+|절|조항)[^|\n]{0,20}이긴다", "'이긴다' (section wins) note"),
    (r"\(바꿈\)|\(나눔\)|\(범위\)", "change tag"),
    (r"(?<![\w.])v\d+(\.\d+)?\s*[:：]", "version tag 'vN:'"),
    (r"명세서 v\d", "version mention"),
]
CHECK_ID = re.compile(r"^\|\s*\**(M\d+|J\d+|G1[a-d]|N\d+)\**\s*\|")


def chapter_key(title):
    m = re.match(r"(부록 [A-Z])", title)
    if m:
        return m.group(1)
    m = re.match(r"(\d+)\.", title)
    return m.group(1) if m else title.split()[0]


def main():
    here = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    plan = open(os.path.join(here, "DRAWING_PLAN.md"), encoding="utf-8").read()
    skill = open(os.path.join(here, "SKILL.md"), encoding="utf-8").read()
    fails = []
    lines = plan.split("\n")

    # 1. skeleton
    chapters, subs = [], {}
    for ln in lines:
        if ln.startswith("## "):
            chapters.append(chapter_key(ln[3:].strip()))
        elif ln.startswith("### "):
            m = re.match(r"(\d+)\.(\d+)\b", ln[4:].strip())
            if m:
                subs.setdefault(m.group(1), []).append(int(m.group(2)))
            elif chapters and not chapters[-1].startswith("부록"):
                fails.append(("skeleton", "unnumbered sub-section in chapter %s: %s" % (chapters[-1], ln)))
    if chapters != SKELETON:
        fails.append(("skeleton", "chapters %s != %s" % (chapters, SKELETON)))
    for ch, nums in subs.items():
        if ch not in SKELETON:
            fails.append(("skeleton", "sub-sections under a missing chapter %s" % ch))
        if nums != list(range(1, len(nums) + 1)):
            fails.append(("skeleton", "chapter %s sub-sections not 1..n: %s" % (ch, nums)))
    known = set(c for c in chapters if not c.startswith("부록"))
    known |= set("%s.%d" % (ch, n) for ch, nums in subs.items() for n in nums)

    # 2. markers (body = after the header block, before appendix C)
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), 0)
    end = next((i for i, ln in enumerate(lines) if ln.startswith("## 부록 C")), len(lines))
    for i in range(start, end):
        for pat, what in BODY_MARKERS:
            if re.search(pat, lines[i]):
                fails.append(("markers", "line %d: %s — %s" % (i + 1, what, lines[i].strip()[:90])))

    # 3. refs
    def check_refs(text, label, pattern):
        for m in re.finditer(pattern, text):
            if re.search(r"SKILL(\.md)?\s*$", text[max(0, m.start() - 11):m.start()]):
                continue  # a reference into SKILL.md, not into the plan
            ref = m.group(1)
            parts = ref.split(".")
            key = parts[0] if len(parts) == 1 else "%s.%s" % (parts[0], parts[1])
            if key not in known:
                fails.append(("refs", "%s: §%s does not exist" % (label, ref)))
    check_refs("\n".join(lines[:end]), "DRAWING_PLAN", r"§(\d+(?:\.\d+)?)")  # appendix C may cite old numbers
    check_refs(skill, "SKILL", r"계획서\s*§(\d+(?:\.\d+)?)")

    # 4. checklist
    ck_idx = next((i for i, ln in enumerate(lines) if ln.startswith("### ") and "체크리스트" in ln), None)
    if ck_idx is None:
        fails.append(("checklist", "no '### ... 체크리스트' sub-section"))
    else:
        j = ck_idx + 1
        while j < len(lines) and not lines[j].startswith("#"):
            j += 1
        ids = []
        for ln in lines[ck_idx:j]:
            m = CHECK_ID.match(ln)
            if m:
                ids.append(m.group(1))
                if "§" not in ln and "부록" not in ln:
                    fails.append(("checklist", "%s cites no § rule" % m.group(1)))
        dup = sorted(set(x for x in ids if ids.count(x) > 1))
        if not ids:
            fails.append(("checklist", "no item rows found"))
        if dup:
            fails.append(("checklist", "duplicate ids %s" % dup))

    # 5. history
    m = re.search(r"명세서 (v\d+(?:\.\d+)?)", "\n".join(lines[:start]))
    appc = "\n".join(lines[end:])
    if not m:
        fails.append(("history", "no '명세서 vN' in the status line"))
    elif m.group(1) not in appc:
        fails.append(("history", "%s is not recorded in appendix C" % m.group(1)))

    # 6. skill-top
    top = skill.split("\n## ", 1)[0]
    notes = re.findall(r"명세서 v\d", top)
    if len(notes) > 1:
        fails.append(("skill-top", "%d stacked version notes before the first chapter" % len(notes)))

    for check, detail in fails:
        print("FAIL %s: %s" % (check, detail))
    print("spec_lint: %d problem(s)" % len(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
