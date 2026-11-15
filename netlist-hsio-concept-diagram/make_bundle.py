#!/usr/bin/env python3
"""Pack the skill folder into text-only bundles for hand-over by e-mail (no zip).

usage:
  python3 make_bundle.py                          SOURCE_BUNDLE.md (skill) + TESTS_BUNDLE.md (regression set)
  python3 make_bundle.py --release R0 --spec v6.1 releases/R0/HSIO_R0_SOURCE.md + HSIO_R0_TESTS.md
The receiver restores every file with the restore script printed at the top of each bundle;
every file carries its SHA-256, so a changed character is reported.
"""
import datetime
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    "RELEASES.md",
    "SKILL.md",
    "DRAWING_PLAN.md",
    "Q2_layout_options.html",
    "spec_lint.py",
    "make_bundle.py",
    "workflow/WORKFLOW.md",
    "workflow/orchestrate.py",
    "workflow/orchestrate_config.json",
    "workflow/prompts/glm_1_classify.md",
    "workflow/prompts/claude_2_review_classify.md",
    "workflow/prompts/glm_4_draw.md",
    "workflow/prompts/claude_6_review_final.md",
    "workflow/prompts/glm_7_fix.md",
    "reference/rx_afe/rx_afe_top.sp",
    "reference/rx_afe/.gitignore",
    "reference/rx_afe/work/run_all.sh",
    "reference/rx_afe/work/netlist.py",
    "reference/rx_afe/work/analyze.py",
    "reference/rx_afe/work/spec_rules.py",
    "reference/rx_afe/work/classify_report.py",
    "reference/rx_afe/work/scene.py",
    "reference/rx_afe/work/layouts.py",
    "reference/rx_afe/work/render_html.py",
    "reference/rx_afe/work/make_pptx.py",
    "reference/rx_afe/work/measure.js",
    "reference/rx_afe/work/verify.py",
    "reference/rx_afe/expected/classification.md",
    "reference/rx_afe/expected/annotations.json",
    "reference/rx_afe/expected/block_dictionary.json",
    "reference/rx_afe/expected/verify_report.json",
]
LANG = {".py": "python", ".js": "javascript", ".md": "markdown", ".sp": "spice", ".sh": "bash",
        ".json": "json", ".html": "html"}
FENCE = "`" * 5  # built, so this file never contains the fence itself

RESTORE = r'''import hashlib, os, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
dest = sys.argv[2] if len(sys.argv) > 2 else "netlist-hsio-concept-diagram"
pat = re.compile(r"^### FILE: (\S+)\n<!-- sha256=([0-9a-f]{64}) newline=([01]) -->\n`{5}\w*\n(.*?)\n`{5}$", re.S | re.M)
n = bad = 0
for path, sha, nl, body in pat.findall(src):
    data = body + ("\n" if nl == "1" else "")
    full = os.path.join(dest, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    ok = hashlib.sha256(data.encode("utf-8")).hexdigest() == sha
    bad += not ok
    n += 1
    print(("OK   " if ok else "BAD  ") + path)
print("%d files restored, %d checksum mismatches" % (n, bad))
sys.exit(1 if bad else 0)
'''


def write_bundle(out, files, header):
    parts = list(header) + [
        "### 복원 스크립트 (restore.py)\n",
        FENCE + "python\n" + RESTORE.rstrip("\n") + "\n" + FENCE + "\n",
        "## 파일 목록\n",
    ]
    listing, blocks = [], []
    for rel in files:
        with open(os.path.join(HERE, rel), encoding="utf-8") as f:
            data = f.read()
        if FENCE in data:
            raise SystemExit("%s contains %s; choose a longer fence" % (rel, FENCE))
        sha = hashlib.sha256(data.encode("utf-8")).hexdigest()
        nl = "1" if data.endswith("\n") else "0"
        body = data[:-1] if nl == "1" else data
        lang = LANG.get(os.path.splitext(rel)[1], "")
        listing.append("| `%s` | %d | `%s…` |" % (rel, len(data.encode("utf-8")), sha[:12]))
        blocks.append("### FILE: %s\n<!-- sha256=%s newline=%s -->\n%s%s\n%s\n%s\n" % (rel, sha, nl, FENCE, lang, body, FENCE))
    parts.append("| 경로 | 바이트 | SHA-256 |\n|---|---|---|\n" + "\n".join(listing) + "\n")
    parts.append("## 파일\n")
    parts.extend(blocks)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("wrote", out, os.path.getsize(out), "bytes,", len(files), "files")


def stamp(release, spec):
    """One header line naming the release, the spec version, the source commit and the date."""
    if not release:
        return []
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                                         universal_newlines=True).strip()
    except Exception:
        commit = "unknown"
    return ["> **Release %s** — 명세서 %s — 소스 커밋 `%s` — %s\n"
            % (release, spec or "?", commit, datetime.date.today().isoformat())]


def test_files():
    root = os.path.join(HERE, "tests", "regression")
    files = []
    for d, _, fs in sorted(os.walk(root)):
        for name in sorted(fs):
            files.append(os.path.relpath(os.path.join(d, name), HERE).replace(os.sep, "/"))
    return files


def source_header(name, release, spec):
    notes = ["RELEASE_NOTES_%s.md" % release] if release else []
    return [
        "# 넷리스트 기반 High-Speed IO 개념도 그리기 — 스킬 전체 묶음\n",
    ] + stamp(release, spec) + [
        "텍스트 파일만 주고받을 때 쓰는 파일이다 (메일 첨부 가능, zip 아님). 이 파일 하나에 스킬 폴더 "
        "`netlist-hsio-concept-diagram/`의 텍스트 파일이 **전부** 들어 있다: 명세서, 구현 가이드, 그림 B, "
        "기준 netlist·코드·기대 결과, 실사용 흐름(workflow), 검사기. 그림 파일(PNG, PPTX, HTML 결과)은 넣지 않았다 — "
        "복원 후 기준 코드로 다시 만든다. %s\n" % ("배포 노트는 `%s`." % notes[0] if notes else ""),
        "## 복원 방법\n",
        "1. 아래 복원 스크립트를 `restore.py`로 저장하고 실행한다:\n"
        "   `python3 restore.py %s netlist-hsio-concept-diagram`\n"
        "   → 모든 줄이 `OK`, 마지막 줄이 `0 checksum mismatches`여야 한다. (메일이 .md를 막아 .txt로 바꿔 받았어도 똑같다.)\n"
        "2. 코드를 실행할 수 없으면 각 `### FILE:` 블록 내용을 한 글자도 바꾸지 말고 그 경로의 파일로 만든다 "
        "(`newline=1`이면 파일 끝에 줄바꿈 하나).\n"
        "3. 기준 결과를 다시 만든다 (Python 3.6+ + python-pptx, Node.js 18+ + Playwright Chromium):\n"
        "   `bash netlist-hsio-concept-diagram/reference/rx_afe/work/run_all.sh`\n"
        "   → `reference/rx_afe/out/`에 concept.html, concept.pptx, screenshots/ 17장. `out/verify_report.json`의 summary가 "
        "`{'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}`, `out/`의 classification.md·annotations.json·"
        "block_dictionary.json이 `expected/`와 같아야 한다.\n"
        "4. 그다음 `SKILL.md`를 처음부터 읽는다. 실사용(GLM + Claude Code 분담)은 `workflow/WORKFLOW.md`.\n" % name,
    ]


def main():
    args = sys.argv[1:]
    release = args[args.index("--release") + 1] if "--release" in args else None
    spec = args[args.index("--spec") + 1] if "--spec" in args else None
    if release:
        out_dir = os.path.join(HERE, "releases", release)
        src_name, test_name = "HSIO_%s_SOURCE.md" % release, "HSIO_%s_TESTS.md" % release
        files = FILES + ["RELEASE_NOTES_%s.md" % release]
    else:
        out_dir = HERE
        src_name, test_name = "SOURCE_BUNDLE.md", "TESTS_BUNDLE.md"
        files = FILES
    missing = [f for f in files if not os.path.exists(os.path.join(HERE, f))]
    if missing:
        raise SystemExit("missing files: %s" % ", ".join(missing))
    write_bundle(os.path.join(out_dir, src_name), files, source_header(src_name, release, spec))
    test_header = [
        "# 넷리스트 기반 High-Speed IO 개념도 그리기 — 회귀 시험 세트 묶음\n",
    ] + stamp(release, spec) + [
        "`tests/regression/`의 시험 netlist·정답지·설계 메모 전부. 쓰는 법은 그 안의 `README.md`. "
        "**정답지·설계 메모·name_map은 검증 쪽에만 준다(그리는 쪽에는 netlist.sp만).**\n",
        "## 복원 방법\n",
        "`python3 restore.py %s netlist-hsio-concept-diagram` → 모든 줄 `OK`, 마지막 줄 `0 checksum mismatches`.\n" % test_name,
    ]
    write_bundle(os.path.join(out_dir, test_name), test_files(), test_header)


if __name__ == "__main__":
    main()
