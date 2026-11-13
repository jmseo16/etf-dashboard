#!/bin/bash
set -e
cd "$(dirname "$0")"
OUT=../out
python3 parse.py ../rx_afe_top.sp netlist.json
python3 analyze.py netlist.json analysis.json > analysis.log
python3 build.py
python3 verify.py netlist.json analysis.json views.json verify_raw.json
python3 make_docs.py $OUT > /dev/null
python3 render_pptx.py views.json summary.json $OUT/concept.pptx
python3 render_html.py views.json verify_raw.json $OUT/concept.pptx $OUT/concept.html summary.json
rm -f $OUT/screenshots/*.png
node shots.js $(realpath $OUT/concept.html) $(realpath $OUT/screenshots) $PWD/browser.json
python3 merge_report.py verify_raw.json browser.json $OUT/verify_report.json
(cd pptimg && rm -f *.png *.pdf && timeout 180 soffice --headless --convert-to pdf ../$OUT/concept.pptx --outdir . >/dev/null 2>&1 && pdftoppm -r 60 -png concept.pdf s)
