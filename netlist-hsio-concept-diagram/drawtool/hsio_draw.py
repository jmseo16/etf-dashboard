#!/usr/bin/env python3
"""HSIO concept-diagram drawing tool.

    python3 hsio_draw.py <netlist.sp> -o <out dir> [--annotations answers.json] [--top CELL] [--no-png]

Reads a SPICE netlist, classifies the signals from the circuit structure, draws every screen
(block screens and transistor screens), checks every screen by reading the connections back from
the line coordinates, and writes the results to the output directory.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hd import VERSION, netlist as NL, analyze as AZ, views as VW, route as RT, verify as VF, selftest as ST, output as OUT, render as RD  # noqa


def apply_answers(ann, questions):
    """Answers to tool questions ('answers': {question id: option}) become net classes."""
    nc = dict(ann.get('net_class', {}))
    for q in questions:
        a = ann.get('answers', {}).get(q['id'])
        if not a:
            continue
        a = a.split('(')[0].strip()
        for port in [x.strip() for x in q['item'].split(',')]:
            nc[port] = {'제어': 'K3'}.get(a, a)
    ann = dict(ann)
    ann['net_class'] = nc
    return ann


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('netlist')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--annotations')
    ap.add_argument('--top')
    ap.add_argument('--no-png', action='store_true')
    a = ap.parse_args(argv)
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    cells, globs = NL.parse(a.netlist)
    top = (a.top or NL.top_cell(cells)).lower()
    ann = {}
    if a.annotations and os.path.exists(a.annotations):
        ann = json.load(open(a.annotations, encoding='utf-8'))
    A = AZ.analyze(cells, top, ann)
    if ann.get('answers'):
        ann = apply_answers(ann, A.questions)
        A = AZ.analyze(cells, top, ann)
    views, roles, lcls, pdir = VW.build(cells, top, A, ann)
    scenes, report = [], []
    for V in views.values():
        S = json.loads(json.dumps(RT.build_scene(V)))
        scenes.append(S)
        r = VF.check(S, cells[V.cell], V.level)
        r['title'] = S['title']
        report.append(r)
        print('  %-28s %s' % (V.id, 'ok' if r['connectivity_pass'] and r['quality_pass'] else 'PROBLEM ' + str(dict((k, v) for k, v in r['counts'].items() if v))))
    levels = dict((v.id, v.level) for v in views.values())
    st = ST.run(scenes, cells, levels)
    md, info = OUT.classification(A, cells, top, views)
    summ = [ln for ln in md.splitlines()[2:8]]
    qtxt = ['%s → %s' % (q['q'], ann.get('answers', {}).get(q['id'], q['default'] + ' (가정)')) for q in A.questions]
    ok = OUT.pptx(scenes, summ, os.path.join(a.out, 'concept.pptx'))
    pbytes = open(os.path.join(a.out, 'concept.pptx'), 'rb').read() if ok else b''
    open(os.path.join(a.out, 'concept.html'), 'w', encoding='utf-8').write(OUT.html(scenes, views, summ, qtxt, pbytes, '%s — HSIO 개념도' % top))
    json.dump(scenes, open(os.path.join(a.out, 'scenes.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    summary = {'views': len(report), 'connectivity_pass': sum(1 for r in report if r['connectivity_pass']),
               'quality_pass': sum(1 for r in report if r['quality_pass']),
               'bends': sum(r['bends'] for r in report), 'net_labels': sum(r['labels'] for r in report)}
    json.dump({'tool_version': VERSION, 'top': top, 'summary': summary, 'self_test': st, 'views': report},
              open(os.path.join(a.out, 'verify_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(a.out, 'classification.md'), 'w', encoding='utf-8').write(md)
    omitted = dict((S['id'], S.get('omitted', [])) for S in scenes)
    json.dump({'top': top, 'ports': info, 'data_inputs': A.data_seeds, 'clock_inputs': A.clk_seeds, 'outputs': sorted(A.out_ports),
               'omitted_top': omitted.get(scenes[0]['id'], []), 'merged_top': scenes[0].get('legend', [])},
              open(os.path.join(a.out, 'classification.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'questions': A.questions, 'how_to_answer': 'annotations.json 의 "answers" 에 {질문 id: 선택지} 로 적고 --annotations 로 다시 실행'},
              open(os.path.join(a.out, 'questions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(ann if ann else {'answers': {}, 'net_class': {}, 'block_role': {}, 'hide_instances': []},
              open(os.path.join(a.out, 'annotations.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bd = [{'cell': c, 'row': r, 'confidence': 'high' if r != 'box' else 'low'} for c, r in roles.items() if any(v.cell == c for v in views.values())]
    json.dump(bd, open(os.path.join(a.out, 'block_dictionary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    npng = 0
    if not a.no_png:
        svgdir = os.path.join(a.out, 'screenshots')
        os.makedirs(svgdir, exist_ok=True)
        for S in scenes:
            open(os.path.join(svgdir, S['id'] + '.svg'), 'w', encoding='utf-8').write(RD.svg(S))
        try:
            subprocess.check_call(['node', os.path.join(HERE, 'hd', 'shot.js'), svgdir, '1'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
            npng = len([f for f in os.listdir(svgdir) if f.endswith('.png')])
        except Exception as e:
            print('  (PNG screenshots skipped: %s)' % type(e).__name__)
    lines = ['# 그리기 결과 — %s' % top, '', '- 도구 버전: %s' % VERSION, '- 화면 수: %d' % summary['views'],
             '- 연결 검사 통과: %d / %d' % (summary['connectivity_pass'], summary['views']),
             '- 품질 검사 통과: %d / %d' % (summary['quality_pass'], summary['views']),
             '- 꺾임 수(전체): %d, 이름표로 이은 곳: %d' % (summary['bends'], summary['net_labels']),
             '- 검증기 오류 주입: %d개 넣어 %d개 잡음' % (st['injected'], st['caught']),
             '- 질문: %d개 (questions.json)' % len(A.questions),
             '- PPTX: %s, PNG: %d장' % ('있음' if ok else '없음(python-pptx 없음)', npng),
             '- 걸린 시간: %.0f초' % (time.time() - t0), '', '## 화면별 결과', '', '| 화면 | 연결 | 품질 | 문제 |', '|---|---|---|---|']
    for r in report:
        bad = dict((k, v) for k, v in r['counts'].items() if v)
        lines.append('| %s | %s | %s | %s |' % (r['id'], '통과' if r['connectivity_pass'] else '**실패**', '통과' if r['quality_pass'] else '**실패**',
                                                 ', '.join('%s %d' % kv for kv in bad.items()) or ''))
    open(os.path.join(a.out, 'draw_report.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('views %(views)d, connectivity %(connectivity_pass)d, quality %(quality_pass)d' % summary)
    print('self-test: %d/%d injected errors caught; questions: %d; %.0fs' % (st['caught'], st['injected'], len(A.questions), time.time() - t0))
    return 0 if summary['connectivity_pass'] == summary['views'] and summary['quality_pass'] == summary['views'] else 1


if __name__ == '__main__':
    sys.exit(main())
