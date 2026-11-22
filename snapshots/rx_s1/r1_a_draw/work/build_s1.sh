#!/bin/bash
# build_s1.sh : generate scenes, html, pptx, screenshots (does NOT run the checker)
set -e
export NODE_PATH=/opt/node22/lib/node_modules:/opt/node-tools/node_modules
cd "$(dirname "$0")"
OUT=../out
mkdir -p $OUT/screenshots
python3 gen_s1.py ../../input/netlist.sp . > /dev/null
python3 classify_s1.py $OUT post > /dev/null
echo '{}' > analysis.json
rm -f $OUT/concept.pptx
python3 render_html.py . $OUT > /dev/null
node measure.js $PWD/$OUT/concept.html $PWD/texts.json "" > /dev/null
python3 make_pptx.py . $OUT > /dev/null
python3 render_html.py . $OUT > /dev/null
rm -f $OUT/screenshots/*.png
node measure.js $PWD/$OUT/concept.html $PWD/texts.json $PWD/$OUT/screenshots
