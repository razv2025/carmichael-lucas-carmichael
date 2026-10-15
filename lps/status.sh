#!/bin/sh
cd "$(dirname "$0")"
python3 -c "
import json, math, statistics
rows=[json.loads(l) for l in open('prog734_h12000v4.jsonl')]
n=len(rows); N=14400
# per-slab work grows as i^(1/3) (slab width i^(4/3) x sum-density z^(-3/7))
pts=[(r['slab'], r['right']) for r in rows if r['slab']>=20]
xs=[math.log(s) for s,_ in pts]; ys=[math.log(v) for _,v in pts]
mx,my=statistics.mean(xs),statistics.mean(ys)
p=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
C=math.exp(my-p*mx)
done=sum(r['right'] for r in rows)
remaining=sum(C*i**p for i in range(n,N))
clean=[r for r in rows[-400:] if r['secs']<600] or rows[-10:]
rate=sum(r['right'] for r in clean)/sum(r['secs'] for r in clean)
cands=sum(r['cands'] for r in rows)
print(f'slabs {n}/{N} | {100*done/(done+remaining):.2f}% of WORK done | candidates {cands}')
print(f'clean rate {rate:.2e} tuples/s | {remaining/rate/86400:.0f} days of compute left')
print(f'  (= {remaining/rate/86400:.0f}d if never asleep; wall-clock is longer by however much the Mac sleeps)')
"
