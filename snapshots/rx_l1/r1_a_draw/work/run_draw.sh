#!/bin/bash
set -e
export NODE_PATH=/home/antigravity/jmseo16/etf-dashboard/node_modules
W="$(cd "$(dirname "$0")" && pwd)"
OUT="$(cd "$W/../out" && pwd)"

mkdir -p "$OUT/screenshots"
cd "$W"

python3 render_html.py . "$OUT"
node measure.js "$OUT/concept.html" "$W/texts.json" ""
python3 make_pptx.py . "$OUT"
python3 render_html.py . "$OUT"
rm -f "$OUT/screenshots"/*.png
node measure.js "$OUT/concept.html" "$W/texts.json" "$OUT/screenshots"
echo "Draw pipeline completed successfully."
