#!/usr/bin/env python3
"""Pack the drawing tool (drawtool/) into ONE self-contained HTML file for in-house release.

usage: python3 make_release_html.py R0.3
The HTML shows the README and release notes, carries every source file (base64 + SHA-256), and can be
unpacked either with the Python restore script printed in it or with the save buttons in a browser.
"""
import base64, datetime, hashlib, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = sys.argv[1] if len(sys.argv) > 1 else 'R0.3'
SRC = os.path.join(HERE, 'drawtool')
FILES = ['README.md', 'hsio_draw.py', 'hd/__init__.py', 'hd/netlist.py', 'hd/analyze.py', 'hd/views.py', 'hd/layout.py',
         'hd/route.py', 'hd/verify.py', 'hd/selftest.py', 'hd/render.py', 'hd/output.py', 'hd/shot.js']
SAMPLE = os.path.join(HERE, 'tests', 'exam', 'rx_s1', 'netlist.sp')
ver = re.search(r'"(.+?)"', open(os.path.join(SRC, 'hd/__init__.py')).read()).group(1)
commit = subprocess.check_output(['git', '-C', HERE, 'rev-parse', '--short', 'HEAD']).decode().strip()
items = []
for f in FILES:
    b = open(os.path.join(SRC, f), 'rb').read()
    items.append({'path': 'drawtool/' + f, 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'b64': base64.b64encode(b).decode()})
if os.path.exists(SAMPLE):
    b = open(SAMPLE, 'rb').read()
    items.append({'path': 'sample/rx_s1/netlist.sp', 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'b64': base64.b64encode(b).decode()})
RESTORE = r'''#!/usr/bin/env python3
"""usage: python3 restore.py HSIO_%s_DRAWTOOL.html [out dir]   -- unpacks every file and checks its SHA-256"""
import base64, hashlib, json, os, re, sys
src = open(sys.argv[1], encoding='utf-8').read()
out = sys.argv[2] if len(sys.argv) > 2 else '.'
m = re.search(r'<script id="bundle" type="application/json">(.*?)</script>', src, re.S)
bad = 0
for it in json.loads(m.group(1)):
    b = base64.b64decode(it['b64'])
    ok = hashlib.sha256(b).hexdigest() == it['sha256']
    bad += not ok
    p = os.path.join(out, it['path'])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(b)
    print('OK ' if ok else 'BAD', it['path'])
print(bad, 'checksum mismatches')
sys.exit(1 if bad else 0)
''' % REL

def md(text):
    """Very small Markdown -> HTML (headings, lists, tables, code blocks, inline code, bold)."""
    out, i, lines = [], 0, text.split('\n')
    inl = lambda s: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(s)))
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre>%s</pre>' % html.escape('\n'.join(lines[i + 1:j])))
            i = j + 1
        elif ln.startswith('#'):
            n = len(ln) - len(ln.lstrip('#'))
            out.append('<h%d>%s</h%d>' % (min(n + 2, 5), inl(ln[n:].strip()), min(n + 2, 5)))
            i += 1
        elif ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            body = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inl(c) for c in r) for r in rows[2:])
            out.append('<div class="tbl"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (''.join('<th>%s</th>' % inl(c) for c in rows[0]), body))
        elif re.match(r'^(\d+\.|-) ', ln):
            tag = 'ol' if ln[0].isdigit() else 'ul'
            its = []
            while i < len(lines) and (re.match(r'^(\d+\.|-) ', lines[i]) or (lines[i].startswith('   ') and its)):
                if re.match(r'^(\d+\.|-) ', lines[i]):
                    its.append(re.sub(r'^(\d+\.|-) ', '', lines[i]))
                else:
                    its[-1] += ' ' + lines[i].strip()
                i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inl(x) for x in its), tag))
        elif ln.strip():
            j = i
            while j < len(lines) and lines[j].strip() and not re.match(r'^(#|\||```|\d+\. |- )', lines[j]):
                j += 1
            out.append('<p>%s</p>' % inl(' '.join(lines[i:j])))
            i = j
        else:
            i += 1
    return '\n'.join(out)

readme = open(os.path.join(SRC, 'README.md'), encoding='utf-8').read()
readme = re.sub(r'^# .*\n', '', readme, count=1)
rows = ''.join('<tr><td><code>%s</code></td><td class="n">%d</td><td class="sha">%s</td><td><button data-i="%d">저장</button></td></tr>' % (it['path'], it['bytes'], it['sha256'][:16] + '…', k) for k, it in enumerate(items))
today = datetime.date.today().isoformat()
page = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HSIO %(rel)s — hsio_draw v%(ver)s</title>
<style>
:root{--bg:#f5f6f4;--paper:#fff;--fg:#1b1f1d;--muted:#5d6661;--rule:#d5dad6;--accent:#1f6b52;--code:#eef1ee}
@media (prefers-color-scheme:dark){:root{--bg:#121614;--paper:#1a1f1c;--fg:#e4e9e6;--muted:#9aa5a0;--rule:#2e3632;--accent:#6cc7a3;--code:#222a26}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 "Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif;padding:0 16px}
main{max-width:920px;margin:0 auto;padding:36px 0 80px}
h1{font-size:1.8rem;margin:0 0 6px} h2{font-size:1.3rem;margin:44px 0 10px;padding-top:12px;border-top:2px solid var(--fg)}
h3{font-size:1.1rem;margin:28px 0 6px} h4,h5{font-size:1rem;margin:20px 0 4px}
.meta{color:var(--muted);font:13px ui-monospace,Consolas,monospace}
code,pre,.sha{font-family:ui-monospace,Consolas,"D2Coding",monospace;font-size:.88em}
code{background:var(--code);padding:1px 4px} pre{background:var(--code);padding:12px 14px;overflow-x:auto;line-height:1.5}
.tbl{overflow-x:auto;border:1px solid var(--rule);background:var(--paper);margin:10px 0}
table{border-collapse:collapse;width:100%%;font-size:.92rem} th,td{padding:7px 10px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{color:var(--muted);font-size:.82rem;background:var(--bg)} td.n{text-align:right;font-variant-numeric:tabular-nums} .sha{color:var(--muted)}
button{font:inherit;padding:4px 12px;border:1px solid var(--accent);background:transparent;color:var(--accent);cursor:pointer}
button:hover{background:var(--accent);color:var(--paper)} .big{padding:8px 18px;font-weight:600}
li{margin:4px 0} .note{color:var(--muted);font-size:.9rem}
</style></head><body><main>
<p class="meta">배포 %(rel)s · %(today)s · 도구 v%(ver)s · 소스 커밋 %(commit)s</p>
<h1>hsio_draw — netlist에서 고속 IO 개념도를 그리는 도구</h1>
<p>SPICE netlist 하나를 넣으면 신호를 분류하고, 블록 화면과 트랜지스터 화면을 모두 그리고, 그림 좌표만으로 연결을 다시 읽어 netlist와 대조한 결과까지 냅니다. 이 HTML 한 파일에 도구 소스 전부가 들어 있습니다.</p>

<h2>1. 풀기</h2>
<p><b>방법 A (권장)</b> — 아래 스크립트를 <code>restore.py</code>로 저장하고 실행합니다. 파일마다 SHA-256을 확인합니다.</p>
<pre id="restore">%(restore)s</pre>
<p><button id="copy">restore.py 복사</button> <button id="saverestore">restore.py 저장</button></p>
<pre>python3 restore.py HSIO_%(rel)s_DRAWTOOL.html .
# 모든 줄이 OK, 마지막 줄이 "0 checksum mismatches"</pre>
<p><b>방법 B</b> — 이 파일을 브라우저로 열어 아래 표의 "저장" 버튼으로 파일을 하나씩 받습니다. 폴더 구조(<code>drawtool/hd/…</code>)는 직접 맞춥니다.</p>
<div class="tbl"><table><thead><tr><th>파일</th><th>바이트</th><th>SHA-256</th><th></th></tr></thead><tbody>%(rows)s</tbody></table></div>

<h2>2. 필요한 것과 첫 실행</h2>
<ul><li>Python 3.8 이상 (필수). 추가 패키지 없이 HTML·검증 결과까지 나옵니다.</li>
<li><code>python-pptx</code> (선택): 있으면 <code>concept.pptx</code>를 만들고 HTML에 넣습니다.</li>
<li>Node.js + Playwright (선택): 있으면 화면별 PNG를 만듭니다. 없으면 SVG만 남고 <code>--no-png</code>로 건너뜁니다.</li></ul>
<pre>python3 drawtool/hsio_draw.py sample/rx_s1/netlist.sp -o out_s1 --no-png
# 기대 결과 (v%(ver)s):  views 15, connectivity 15, quality 15
#                       self-test: 111/111 injected errors caught; questions: 0</pre>
<p class="note">숫자가 다르면 풀기에서 파일이 바뀐 것입니다. <code>out_s1/concept.html</code>을 브라우저로 열어 그림을 확인합니다.</p>

<h2>3. 검증 절차 (도구가 그린 뒤)</h2>
<ol><li><b>도구 안 (자동)</b>: 화면마다 연결 검사 6종, 품질 검사 14종, 오류 주입 시험. <code>draw_report.md</code>와 <code>verify_report.json</code>에 0건인지 확인합니다.</li>
<li><b>분류 확인</b>: <code>classification.md</code>와 <code>questions.json</code>을 읽고, 틀렸다고 확신하는 것만 <code>annotations.json</code>에 적어 다시 실행합니다.</li>
<li><b>눈으로 검토</b>: 최상위 화면과 대표 화면 3–5장을 직접 엽니다. 검증기가 세지 못하는 것(회로 묶음이 떨어져 놓임, 화면이 넓어 글자가 작음, 긴 직선)은 여기서만 잡힙니다.</li></ol>

<h2>4. 이 버전의 시험 결과</h2>
<div class="tbl"><table><thead><tr><th>시험</th><th>결과</th></tr></thead><tbody>
<tr><td>회귀 시험 (수신 회로 10개, 화면 206개)</td><td>연결 206/206, 품질 206/206, 오류 주입 1,529개 모두 검출</td></tr>
<tr><td>분류 (출제 의도 273항목)</td><td>270 일치. 다른 3개는 모두 쓰기 레벨링 관찰 입력 한 종류이고, 도구가 질문으로 남깁니다</td></tr>
<tr><td>낮은 사양 모델 3종에 맡긴 시험 (v0.1–v0.5, 5회차)</td><td>끊긴 선 0건. 처음 보는 회로(5회차)에서 세 모델의 그림 47장이 서로 같음</td></tr>
</tbody></table></div>
<p class="note">알려진 한계: 시험 회로는 모두 가상의 DQ/DQS 수신 회로입니다. 송신 회로, PLL, 실제 설계 netlist로는 시험하지 않았습니다. 새 회로에서 이상한 그림이 나오면 netlist 발췌와 화면 id를 보내 주세요.</p>

<h2>5. 사용 설명 (README)</h2>
%(readme)s

<script id="bundle" type="application/json">%(bundle)s</script>
<script>
var B=JSON.parse(document.getElementById('bundle').textContent);
function save(name,bytes){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([bytes]));a.download=name;document.body.appendChild(a);a.click();a.remove();}
function dec(b64){var s=atob(b64),u=new Uint8Array(s.length);for(var i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u;}
document.querySelectorAll('button[data-i]').forEach(function(b){b.onclick=function(){var it=B[+b.dataset.i];save(it.path.split('/').pop(),dec(it.b64));};});
var R=document.getElementById('restore').textContent;
document.getElementById('saverestore').onclick=function(){save('restore.py',R);};
document.getElementById('copy').onclick=function(){var t=this;navigator.clipboard.writeText(R).then(function(){t.textContent='복사됨';},function(){var r=document.createRange();r.selectNodeContents(document.getElementById('restore'));var s=getSelection();s.removeAllRanges();s.addRange(r);});};
</script>
</main></body></html>
''' % {'rel': REL, 'ver': ver, 'today': today, 'commit': commit, 'restore': html.escape(RESTORE), 'rows': rows,
       'readme': md(readme), 'bundle': json.dumps(items)}
out = os.path.join(HERE, 'releases', REL)
os.makedirs(out, exist_ok=True)
path = os.path.join(out, 'HSIO_%s_DRAWTOOL.html' % REL)
open(path, 'w', encoding='utf-8').write(page)
print(path, len(page), 'bytes,', len(items), 'files')
