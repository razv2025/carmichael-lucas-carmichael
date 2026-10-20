#!/bin/sh
# Control the Carmichael-list CLC scan: status | pause | resume | stop
# pause/resume = SIGSTOP/SIGCONT (instant freeze, memory kept, zero loss;
#                killed by reboot/logout; survives sleep).
# stop         = graceful SIGTERM; scan_resumable.py checkpoints and exits
#                (rerun later to continue). Refuses for the non-resumable
#                full_scan.py unless --force (that would lose all progress).
set -u
pids() { { pgrep -f 'pipeline24.sh'; pgrep -f 'full_scan.py'; pgrep -f 'scan_resumable.py'; pgrep -f 'multiprocessing.spawn'; } 2>/dev/null | sort -u; }
case "${1:-status}" in
  status)
    P=$(pids); [ -z "$P" ] && { echo "no scan processes"; exit 0; }
    echo "$P" | xargs -I{} ps -o stat= -p {} | cut -c1 | sort | uniq -c | awk '{print $1" processes in state "$2"  (R/S=running, T=paused)"}'
    echo "$P" | xargs -I{} ps -o pcpu= -p {} | awk '{s+=$1} END {printf "CPU %.0f%%\n", s}'
    echo "$P" | xargs -I{} ps -o rss= -p {} | awk '{s+=$1} END {printf "memory %.2f GB\n", s/1048576}'
    for f in /Users/razvakil/.claude/jobs/*/tmp/c24/scan24.out /Users/razvakil/.claude/jobs/*/tmp/c24/scan_resumable.out; do
      [ -f "$f" ] && echo "progress: $(tail -1 "$f")"; done; exit 0 ;;
  pause)  pids | xargs kill -STOP && sleep 1 && "$0" status ;;
  resume) pids | xargs kill -CONT && sleep 1 && "$0" status ;;
  stop)
    if pgrep -f 'full_scan.py' >/dev/null && [ "${2:-}" != "--force" ]; then
      echo "REFUSING: full_scan.py has no checkpoint; stopping loses all progress. Use 'pause', or 'stop --force'."; exit 1; fi
    pgrep -f 'scan_resumable.py' | xargs -r kill -TERM 2>/dev/null
    [ "${2:-}" = "--force" ] && pids | xargs -r kill -TERM
    echo "stop signal sent; a resumable scan checkpoints and exits within ~2 min" ;;
  *) echo "usage: $0 {status|pause|resume|stop [--force]}"; exit 2 ;;
esac
