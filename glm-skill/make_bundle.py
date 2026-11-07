#!/usr/bin/env python3
"""Regenerate glm-skill/hspice-schematic/SOURCE_BUNDLE.md from the reference implementation.

usage: python3 glm-skill/make_bundle.py          (run from the repository root)
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "glm-skill", "hspice-schematic", "SOURCE_BUNDLE.md")
FILES = [
    "hspice-schematic/SKILL.md",
    "hspice-schematic/references/style_rules.md",
    "hspice-schematic/scripts/build.py",
    "hspice-schematic/scripts/hsch/__init__.py",
    "hspice-schematic/scripts/hsch/parser.py",
    "hspice-schematic/scripts/hsch/analyze.py",
    "hspice-schematic/scripts/hsch/geom.py",
    "hspice-schematic/scripts/hsch/router.py",
    "hspice-schematic/scripts/hsch/layout_leaf.py",
    "hspice-schematic/scripts/hsch/layout_block.py",
    "hspice-schematic/scripts/hsch/render.py",
    "hspice-schematic/scripts/hsch/verify.py",
    "hspice-schematic/scripts/hsch/export_pptx.py",
    "hspice-schematic/scripts/screenshot.js",
    "hspice-schematic/scripts/ui_selftest.js",
    "hspice-schematic/assets/viewer.css",
    "hspice-schematic/assets/viewer.js",
    "tests/test_hsch.py",
    "tests/netlists/input_buffer_system.sp",
    "tests/netlists/virtuoso_style.sp",
]
LANG = {".py": "python", ".js": "javascript", ".css": "css", ".md": "markdown", ".sp": "spice"}
FENCE = "````"

RESTORE = r'''import hashlib, os, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
dest = sys.argv[2] if len(sys.argv) > 2 else "."
pat = re.compile(r"^### FILE: (\S+)\n<!-- sha256=([0-9a-f]{64}) newline=([01]) -->\n````\w*\n(.*?)\n````$", re.S | re.M)
n = bad = 0
for path, sha, nl, body in pat.findall(src):
    data = body + ("\n" if nl == "1" else "")
    if body == "" and nl == "0":
        data = ""
    full = os.path.join(dest, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    ok = hashlib.sha256(data.encode("utf-8")).hexdigest() == sha
    bad += not ok
    n += 1
    print(("OK   " if ok else "BAD  ") + path)
print(f"{n} files restored, {bad} checksum mismatches")
sys.exit(1 if bad else 0)
'''


def main():
    parts = [
        "# hspice-schematic — 기준 구현 전체 소스 (SOURCE_BUNDLE)\n",
        "`SKILL.md`(구현 명세서)와 함께 쓰는 파일이다. 아래 각 `### FILE: <경로>` 블록을 그 경로에 **그대로** "
        "저장하면 기준 구현과 똑같은 도구가 된다. 파일마다 SHA-256이 적혀 있으니 복원 후 반드시 대조한다.\n",
        "## 복원 방법\n",
        "1. 코드를 실행할 수 있으면: 아래 복원 스크립트를 `restore.py`로 저장하고\n"
        "   `python3 restore.py SOURCE_BUNDLE.md <저장할 폴더>` 실행 → 모든 줄이 `OK`, `0 checksum mismatches`여야 한다.\n"
        "2. 실행할 수 없으면: 각 블록의 내용을 한 글자도 바꾸지 말고 그 경로의 파일로 만든다 "
        "(코드 블록 바깥 줄바꿈 규칙: `newline=1`이면 파일 끝에 줄바꿈 하나).\n"
        "3. 그다음 `SKILL.md` §14 검증 절차를 실행한다 (`pip install python-pptx`, 검증용 Node.js + Playwright).\n",
        "### 복원 스크립트 (restore.py)\n",
        FENCE + "python\n" + RESTORE.rstrip("\n") + "\n" + FENCE + "\n",
        "## 파일 목록\n",
    ]
    listing = []
    blocks = []
    for rel in FILES:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            data = f.read()
        if FENCE in data:
            raise SystemExit(f"{rel} contains {FENCE}; choose a longer fence")
        sha = hashlib.sha256(data.encode("utf-8")).hexdigest()
        nl = "1" if data.endswith("\n") else "0"
        body = data[:-1] if nl == "1" else data
        lang = LANG.get(os.path.splitext(rel)[1], "")
        listing.append(f"- `{rel}` ({data.count(chr(10))} lines)")
        blocks.append(f"### FILE: {rel}\n<!-- sha256={sha} newline={nl} -->\n{FENCE}{lang}\n{body}\n{FENCE}\n")
    parts.append("\n".join(listing) + "\n")
    parts.append("## 파일 내용\n")
    parts += blocks
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {len(FILES)} files)")


if __name__ == "__main__":
    main()
