#!/bin/sh
# k4ctl.sh status|pause|resume|stop  — control the detached run_k4.sh campaign.
cd "$(dirname "$0")"
pids() { { pgrep -f 'run_k4.sh'; pgrep -f 'enum_k4 --'; } 2>/dev/null | sort -u; }
case "${1:-status}" in
  pause)  pids | xargs kill -STOP 2>/dev/null; echo "paused (SIGSTOP); memory stays allocated — use stop to release it";;
  resume) pids | xargs kill -CONT 2>/dev/null; echo "resumed";;
  stop)   pids | xargs kill -TERM 2>/dev/null; sleep 1; pids | xargs kill -KILL 2>/dev/null; echo "stopped; rerun ./run_k4.sh (or nohup ./run_k4.sh > run_k4.log 2>&1 &) to resume from the last finished block";;
  status)
    if [ -n "$(pids)" ]; then echo "running: $(pids | tr '\n' ' ')"; ps -o pid,stat,%cpu,rss,etime,command -p "$(pgrep -f 'enum_k4 --' | head -1)" 2>/dev/null | tail -1; else echo "not running"; fi
    for f in k4_*.jsonl; do
      [ -f "$f" ] || continue
      python3 - "$f" <<'PY'
import sys, json
f = sys.argv[1]; hdr = None; blocks = {}; 
for line in open(f):
    try: o = json.loads(line)
    except Exception: continue
    if 'header' in o: hdr = o
    elif 'blk' in o: blocks[o['blk']] = o
if not hdr: sys.exit()
n = hdr['nblk']; done = len(blocks)
pairs = sum(b['pairs'] for b in blocks.values()); ws = sum(b['wsurv'] for b in blocks.values()); fs = sum(b['fsurv'] for b in blocks.values()); sol = sum(b['sol'] for b in blocks.values())
sec = sum(b['sec'] for b in blocks.values())
# ETA: work per block is not uniform; weight remaining blocks by p1 (work per p1 grows like p1^1.5 in p1-mode, shrinks in B-mode)
if blocks:
    rate = pairs / max(1e-9, max(b['t'] for b in blocks.values()))
print(f"{f}: B={hdr['B']} p1max={hdr.get('p1max',0)}  blocks {done}/{n} ({100*done/n:.1f}%)  pairs={pairs:,}  window_survivors={ws}  fermat_survivors={fs}  SOLUTIONS={sol}  cpu-block-sec={sec:,.0f}")
PY
    done
    for s in k4_*_sol.txt; do [ -f "$s" ] && echo "$s: $(grep -c '^SOLUTION' "$s") SOLUTION, $(grep -c '^FSURV' "$s") FSURV, $(grep -c '^WSURV' "$s") WSURV lines"; done
    ls RESULT_*.txt 2>/dev/null;;
  *) echo "usage: $0 status|pause|resume|stop";;
esac
