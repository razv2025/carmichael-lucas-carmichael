#!/bin/sh
# Resume the (7,3,4) H=12000 search from the last completed slab.
# Writes PIDs to search.pid so stop.sh can terminate supervisor+engine reliably.
cd "$(dirname "$0")"
echo "supervisor $$" > search.pid
trap 'kill "$ENGINE" 2>/dev/null; rm -f search.pid; exit 0' INT TERM
while :; do
  n=$(wc -l < prog734_h12000v4.jsonl | tr -d ' ')
  [ "$n" -ge 14400 ] && { echo "SEARCH COMPLETE: full H=12000 coverage"; break; }
  echo "resuming from slab $n/14400 ..."
  nice -n 10 ./engine734 12000 14400 prog734_h12000v4.jsonl cand734_h12000v4.txt "$n" &
  ENGINE=$!
  echo "engine $ENGINE" >> search.pid
  wait "$ENGINE"
  sleep 5
done
rm -f search.pid
