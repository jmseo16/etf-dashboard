import hashlib, os, re, sys
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
