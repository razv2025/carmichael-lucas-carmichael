#!/bin/sh
cd "$(dirname "$0")"
python3 -c "
import json, os
# Total right-side tuples for H=12000, from the phase-1 power-law fit
# right_i = 5.347e9 * i^0.332 over the N=14400 grid (0.4% residual on 200
# slabs, 864 slabs of data). Work per slab grows as i^(1/3) because slab
# width ~ i^(4/3) and 4-term sum density ~ z^(-3/7).
T = 1.3880e15
rows=[json.loads(l) for l in open('prog734_h12000v4.jsonl')]
new=[json.loads(l) for l in open('prog734_h12000_g720k.jsonl')] if os.path.exists('prog734_h12000_g720k.jsonl') else []
done=sum(r['right'] for r in rows)+sum(r['right'] for r in new)
slab=43950+len(new); N=720000
cands=sum(r['cands'] for r in rows)+sum(r['cands'] for r in new)
src=(new or rows)
clean=[r for r in src[-2000:] if r['secs'] < (30 if new else 600)] or src[-20:]
rate=sum(r['right'] for r in clean)/max(sum(r['secs'] for r in clean),1)
print(f'slab {slab}/{N} | {100*done/T:.2f}% of work done | candidates {cands}')
print(f'clean rate {rate:.2e} tuples/s | {(T-done)/rate/86400:.0f} days of compute left')
print(f'  (wall-clock is longer by however much the Mac sleeps)')
"
