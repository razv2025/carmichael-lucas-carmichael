#!/bin/sh
# Resume the (7,3,4) H=12000 search.
#
# Grid history (slab boundaries are z = zmax*(i/N)^(7/3), so a k-fold refinement
# maps slab i of N to slab k*i of k*N with IDENTICAL boundaries):
#   phase 1: N=14400, slabs 0..878 complete   -> prog734_h12000v4.jsonl
#   phase 2: N=720000, starting at slab 43950 -> prog734_h12000_g720k.jsonl
#            (43950/720000 == 879/14400 exactly; no gap, no rework)
cd "$(dirname "$0")"
N=720000
OFFSET=43950
PROG=prog734_h12000_g720k.jsonl
CAND=cand734_h12000v4.txt
echo "supervisor $$" > search.pid
trap 'kill "$ENGINE" 2>/dev/null; rm -f search.pid; exit 0' INT TERM
while :; do
  done_here=$( [ -f "$PROG" ] && wc -l < "$PROG" | tr -d ' ' || echo 0 )
  n=$((OFFSET + done_here))
  [ "$n" -ge "$N" ] && { echo "SEARCH COMPLETE: full H=12000 coverage"; break; }
  echo "resuming at slab $n/$N ..."
  nice -n 10 ./engine734 12000 "$N" "$PROG" "$CAND" "$n" &
  ENGINE=$!
  echo "engine $ENGINE" >> search.pid
  wait "$ENGINE"
  sleep 5
done
rm -f search.pid
