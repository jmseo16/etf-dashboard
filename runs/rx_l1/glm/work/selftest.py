"""selftest.py <workdir> <netlist> <outdir> <run number> <note>: runs check.py + inject.py, writes verify_report.json,
self_checklist.json and appends one line to selftest_log.md"""
import json, sys, subprocess, os, collections
W, NL, OUT, RUN, NOTE = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
subprocess.check_call([sys.executable, 'check.py', W, NL, OUT + '/verify_report.json'], stdout=subprocess.DEVNULL)
subprocess.check_call([sys.executable, 'inject_l1.py', W, NL, W + '/inject_result.json'], stdout=subprocess.DEVNULL)
from check import CHECKS, NOT_IMPLEMENTED
vr = json.load(open(OUT + '/verify_report.json'))
inj = json.load(open(W + '/inject_result.json'))
bycheck = collections.defaultdict(list)
for r in inj:
    bycheck[r['check']].append(r)
auto = []
for cid, name in CHECKS:
    n = vr['totals'].get(cid, 0)
    items = bycheck.get(cid, [])
    auto.append({'id': cid, 'name': name, 'status': 'pass' if n == 0 else 'fail', 'count': n,
                 'injected': '%d/%d' % (sum(1 for r in items if r['caught']), len(items)), 'injected_cases': [r['name'] for r in items]})
sc = {'auto_checks': auto, 'self_test': {'injected': len(inj), 'caught': sum(1 for r in inj if r['caught']), 'all_caught': all(r['caught'] for r in inj)},
      'not_implemented': NOT_IMPLEMENTED, 'total_count': vr['total_count'],
      'note': '이 파일은 그린 쪽 자체 점검이다. 합격 근거가 아니다 (WORKFLOW 1절).'}
json.dump(sc, open(OUT + '/self_checklist.json', 'w'), indent=1, ensure_ascii=False)
tot = vr['totals']
line = '실행 %d | %s | 총 %d건 | %s' % (RUN, ', '.join('%s:%d' % (k.split('-')[0] + k.split('-')[1][:0] if False else k, v) for k, v in sorted(tot.items(), key=lambda kv: kv[0])) , vr['total_count'], NOTE)
log = OUT + '/selftest_log.md'
open(log, 'a').write(line + '\n')
print(line)
print(sc['self_test'], vr['summary'])
