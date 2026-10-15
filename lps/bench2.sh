#!/bin/sh
cd "$(dirname "$0")"
for ns in 7600 19000 50000; do
  rm -f bm2.jsonl bm2.txt
  ./engine734 1500 $ns bm2.jsonl bm2.txt 2>/dev/null >/dev/null
  python3 -c "
import json
rows=[json.loads(l) for l in open('bm2.jsonl')]
r=sum(x['right'] for x in rows); s=sum(x['secs'] for x in rows)
mx=max(x['left'] for x in rows)
print(f'nslabs=$ns: {r/max(s,1):.3e} tuples/s | {s}s | max left/slab {mx:.2e} | bitmap ~{mx*32/8/1e6:.1f} MB', flush=True)
"
done
rm -f bm2.jsonl bm2.txt
echo BENCH2-DONE
