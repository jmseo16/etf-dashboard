#!/bin/bash
# quick render of scenes.json to PNG for eyeballing: rend.sh <workdir> <tmpdir>
export NODE_PATH=/opt/node22/lib/node_modules:/opt/node-tools/node_modules
W=$1; T=$2; mkdir -p $T/shots
python3 render_html.py $W $T >/dev/null && node measure.js $T/concept.html $T/texts.json $T/shots >/dev/null
