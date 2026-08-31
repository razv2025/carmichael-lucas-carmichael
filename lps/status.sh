#!/bin/sh
cd "$(dirname "$0")"
python3 -c "
import json
lines = [json.loads(l) for l in open('prog734_h12000v4.jsonl')]
r = sum(l['right'] for l in lines); s = sum(l['secs'] for l in lines)
c = sum(l['cands'] for l in lines)
total = 12000**4/24
print(f'slabs {len(lines)}/14400 | {100*r/total:.2f}% of tuples | candidates {c}')
if s: print(f'avg {r/s:.2e} tuples/s | est. remaining {(total-r)/(r/s)/86400:.0f} days of running')
"
