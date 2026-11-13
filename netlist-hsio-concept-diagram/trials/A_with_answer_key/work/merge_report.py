import json, sys
rep = json.load(open(sys.argv[1])); br = json.load(open(sys.argv[2])); out = sys.argv[3]
views = []
for r in rep['views']:
    b = br.get(r['view'], {})
    c = dict(r['counts']); c['text_overlap_browser'] = len(b.get('overlaps', []))
    views.append({'view': r['view'], 'connectivity': 'PASS' if r['connectivity_ok'] else 'FAIL',
                  'connectivity_errors': r['errors'], 'warnings': r['warnings'],
                  'quality_counts': c,
                  'quality_zero': all(v == 0 for k, v in c.items() if k != 'structural_crossing'),
                  'structural_crossings': r['quality']['structural_crossing'],
                  'loop_wires_exempt_from_twist': r.get('loop_wires_exempt_from_twist', []),
                  'quality_details': {k: v for k, v in r['quality'].items() if v and k != 'structural_crossing'},
                  'screenshot': 'screenshots/%s.png' % r['view']})
summary = {'netlist': 'rx_afe_top.sp', 'views': len(views),
           'all_connectivity_pass': all(v['connectivity'] == 'PASS' for v in views),
           'all_quality_zero': all(v['quality_zero'] for v in views),
           'structural_crossings_total': sum(len(v['structural_crossings']) for v in views),
           'mobile_check_390px': br.get('__mobile'),
           'method': {'connectivity': 'geometry re-read (wire polylines, pin points, junctions, port/label/rail names) '
                                      'compared with the netlist; merged devices expanded slice-wise; concept symbols '
                                      'compared by bundle outer nets; bundle-internal nets must not appear outside',
                      'text_overlap': 'python estimate (monospace 0.6em) + browser getBBox (text_overlap_browser)',
                      'crossings': 'every proper crossing must be declared structural with a reason by the layout '
                                   'template; undeclared ones are counted as avoidable_crossing'}}
json.dump({'summary': summary, 'views': views}, open(out, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
