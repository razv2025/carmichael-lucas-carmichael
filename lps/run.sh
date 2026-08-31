#!/bin/sh
# Resume the (7,3,4) H=12000 search from the last completed slab.
# Safe to re-run any time; stops by itself at full coverage (14400 slabs).
cd "$(dirname "$0")"
while :; do
  n=$(wc -l < prog734_h12000v4.jsonl | tr -d ' ')
  [ "$n" -ge 14400 ] && { echo "SEARCH COMPLETE: full H=12000 coverage"; break; }
  echo "resuming from slab $n/14400 ..."
  nice -n 10 ./engine734 12000 14400 prog734_h12000v4.jsonl cand734_h12000v4.txt "$n"
  sleep 5
done
