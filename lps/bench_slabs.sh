#!/bin/sh
# Measure throughput vs per-slab footprint at H=1500.
# Total left entries at H=1500 ~ 5.6e8; slab counts chosen to give
# ~3e7 (current production), ~3e6, ~3e5 left entries per slab.
cd "$(dirname "$0")"
for ns in 19 190 1900; do
  rm -f bm.jsonl bm.txt
  ./engine734 1500 $ns bm.jsonl bm.txt 2>/dev/null >/dev/null
  python3 -c "
import json
rows=[json.loads(l) for l in open('bm.jsonl')]
r=sum(x['right'] for x in rows); s=sum(x['secs'] for x in rows)
mx=max(x['left'] for x in rows)
print(f'nslabs=$ns: {r/max(s,1):.3e} tuples/s | {s}s total | max left/slab {mx:.2e} | bitmap ~{mx*32/8/1e6:.0f} MB', flush=True)
"
done
rm -f bm.jsonl bm.txt
echo BENCH-DONE
