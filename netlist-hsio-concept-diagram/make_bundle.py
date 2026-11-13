#!/usr/bin/env python3
"""Pack the whole skill folder into one text file (SOURCE_BUNDLE.md) for text-only hand-over.

usage: python3 make_bundle.py            (run from this folder or anywhere)
The receiver restores every file with the restore script printed at the top of the bundle.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "SOURCE_BUNDLE.md")
FILES = [
    "SKILL.md",
    "DRAWING_PLAN.md",
    "Q2_layout_options.html",
    "reference/rx_afe/rx_afe_top.sp",
    "reference/rx_afe/.gitignore",
    "reference/rx_afe/work/run_all.sh",
    "reference/rx_afe/work/netlist.py",
    "reference/rx_afe/work/analyze.py",
    "reference/rx_afe/work/classify_report.py",
    "reference/rx_afe/work/scene.py",
    "reference/rx_afe/work/layouts.py",
    "reference/rx_afe/work/render_html.py",
    "reference/rx_afe/work/make_pptx.py",
    "reference/rx_afe/work/measure.js",
    "reference/rx_afe/work/verify.py",
    "reference/rx_afe/expected/classification.md",
    "reference/rx_afe/expected/annotations.json",
    "reference/rx_afe/expected/verify_report.json",
]
LANG = {".py": "python", ".js": "javascript", ".md": "markdown", ".sp": "spice", ".sh": "bash",
        ".json": "json", ".html": "html"}
FENCE = "````"

RESTORE = r'''import hashlib, os, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
dest = sys.argv[2] if len(sys.argv) > 2 else "netlist-hsio-concept-diagram"
pat = re.compile(r"^### FILE: (\S+)\n<!-- sha256=([0-9a-f]{64}) newline=([01]) -->\n````\w*\n(.*?)\n````$", re.S | re.M)
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


def main():
    parts = [
        "# 넷리스트 기반 High-Speed IO 개념도 그리기 — 전체 파일 묶음 (SOURCE_BUNDLE)\n",
        "텍스트 파일만 주고받을 수 있을 때 쓰는 파일이다. 이 파일 하나에 스킬 폴더 `netlist-hsio-concept-diagram/`의 "
        "텍스트 파일이 **전부** 들어 있다 (가이드, 계획서, 그림 B, 기준 netlist, 기준 코드, 기대 결과). "
        "그림 파일(스크린샷 PNG, PPTX, HTML)은 넣지 않았다 — 복원 후 기준 코드로 다시 만든다.\n",
        "## 복원 방법\n",
        "1. 아래 복원 스크립트를 `restore.py`로 저장하고 실행한다:\n"
        "   `python3 restore.py SOURCE_BUNDLE.md netlist-hsio-concept-diagram`\n"
        "   → 모든 줄이 `OK`, 마지막 줄이 `0 checksum mismatches`여야 한다.\n"
        "2. 코드를 실행할 수 없으면 각 `### FILE:` 블록 내용을 한 글자도 바꾸지 말고 그 경로의 파일로 만든다 "
        "(`newline=1`이면 파일 끝에 줄바꿈 하나).\n"
        "3. 기준 결과를 다시 만든다 (Python 3.6+ + python-pptx, Node.js 18+ + Playwright Chromium 필요):\n"
        "   `bash netlist-hsio-concept-diagram/reference/rx_afe/work/run_all.sh`\n"
        "   → `reference/rx_afe/out/`에 concept.html, concept.pptx, screenshots/ 17장이 생기고, "
        "`out/verify_report.json`의 summary가 `{'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}`이어야 한다. "
        "`out/classification.md`, `out/annotations.json`은 `expected/`의 같은 파일과 내용이 같아야 한다.\n"
        "4. 그다음 `SKILL.md`를 처음부터 읽는다. 그림 B는 `Q2_layout_options.html`을 브라우저로 열어 본다.\n",
        "### 복원 스크립트 (restore.py)\n",
        FENCE + "python\n" + RESTORE.rstrip("\n") + "\n" + FENCE + "\n",
        "## 파일 목록\n",
    ]
    listing, blocks = [], []
    for rel in FILES:
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
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("wrote", OUT, os.path.getsize(OUT), "bytes,", len(FILES), "files")


if __name__ == "__main__":
    main()
