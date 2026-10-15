#!/bin/sh
cd "$(dirname "$0")"
python3 -c "
import json, math, statistics, os
N=720000
rows=[json.loads(l) for l in open('prog734_h12000v4.jsonl')]          # phase 1 (N=14400)
new=[json.loads(l) for l in open('prog734_h12000_g720k.jsonl')] if os.path.exists('prog734_h12000_g720k.jsonl') else []
done_work=sum(r['right'] for r in rows)+sum(r['right'] for r in new)
slab_now=43950+len(new)
# work per slab on the fine grid grows as i^(1/3)
src=new if len(new)>=40 else None
if src:
    pts=[(r['slab'], r['right']) for r in src]
    xs=[math.log(s) for s,_ in pts]; ys=[math.log(v) for _,v in pts]
    mx,my=statistics.mean(xs),statistics.mean(ys)
    p=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
    C=math.exp(my-p*mx)
else:
    p, C = 1/3., sum(r['right'] for r in rows[-50:])/50/50/ (879**(1/3.))
remaining=sum(C*i**p for i in range(slab_now, N))
clean=[r for r in (new or rows)[-400:] if r['secs']<600] or (new or rows)[-10:]
rate=sum(r['right'] for r in clean)/max(sum(r['secs'] for r in clean),1)
cands=sum(r['cands'] for r in rows)+sum(r['cands'] for r in new)
print(f'slab {slab_now}/{N} | {100*done_work/(done_work+remaining):.2f}% of work | candidates {cands}')
print(f'clean rate {rate:.2e} tuples/s | {remaining/rate/86400:.0f} days of compute left (if never asleep)')
"
