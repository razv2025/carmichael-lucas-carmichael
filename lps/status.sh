#!/bin/sh
cd "$(dirname "$0")"
python3 -c "
import json, os, statistics
# Total right-side tuples for H=12000, from the phase-1 fit right_i =
# 5.347e9 * i^0.332 (0.4% residual over 864 slabs). Work per slab grows as
# i^(1/3): slab width ~ i^(4/3), 4-term sum density ~ z^(-3/7).
T = 1.3880e15
rows=[json.loads(l) for l in open('prog734_h12000v4.jsonl')]
new=[json.loads(l) for l in open('prog734_h12000_g720k.jsonl')] if os.path.exists('prog734_h12000_g720k.jsonl') else []
done=sum(r['right'] for r in rows)+sum(r['right'] for r in new)
slab=43950+len(new); N=720000
cands=sum(r['cands'] for r in rows)+sum(r['cands'] for r in new)
src=(new or rows)[-500:]
# Robust rate: the engine times slabs by wall clock, so any slab spanning a
# sleep/outage is charged the whole gap. Reject outliers against the median.
med=statistics.median(r['secs'] for r in src) or 1
clean=[r for r in src if r['secs'] <= max(3*med, 5)] or src
rate=sum(r['right'] for r in clean)/max(sum(r['secs'] for r in clean),1)
lost=sum(r['secs'] for r in src)-sum(r['secs'] for r in clean)
print(f'slab {slab}/{N} | {100*done/T:.2f}% of work done | candidates {cands}')
print(f'clean rate {rate:.2e} tuples/s | {(T-done)/rate/86400:.0f} days of compute left')
print(f'  (median slab {med:.0f}s; rejected {len(src)-len(clean)}/{len(src)} outlier slabs = {lost/3600:.1f}h of downtime)')
"
