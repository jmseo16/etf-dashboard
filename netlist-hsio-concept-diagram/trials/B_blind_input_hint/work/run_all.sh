#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-etf-dashboard/7bf12658-25a0-5871-a755-cec3e3517cc8/scratchpad/hsio_trial_blind
cd $S/work
python3 analyze.py ../rx_afe_top.sp RX_AFE_TOP . RX_INP RX_INN > /dev/null
python3 classify_report.py . ../out ../rx_afe_top.sp > /dev/null
python3 layouts.py . ../rx_afe_top.sp
rm -f ../out/concept.pptx
python3 render_html.py . ../out
node measure.js $S/out/concept.html $S/work/texts.json ""
python3 make_pptx.py . ../out
python3 render_html.py . ../out
rm -f $S/out/screenshots/*.png
node measure.js $S/out/concept.html $S/work/texts.json $S/out/screenshots
python3 verify.py . ../rx_afe_top.sp ../out/verify_report.json
