#!/bin/sh
# Near-miss census of all Carmichael numbers < 1e24 (census_1e24.py).  ~21 CPU-hours; resumable: rerun to continue.
# Launch detached:  nohup ./census_1e24.sh > /dev/null 2>&1 &        second pass (rule 2):  PASS2=1 nohup ./census_1e24.sh ...
cd "$(dirname "$0")"
LIST=${LIST:-/Users/razvakil/.claude/jobs/c6e4e4e0/tmp/c24/carm10e24.txt}
[ -f "$LIST" ] || { echo "input list missing: $LIST" >> census_1e24.log; exit 1; }
echo "# census started $(date); input $LIST ($(stat -f %z "$LIST") bytes)" >> census_1e24.log
caffeinate -i nice -n 10 python3 -I census_1e24.py "$LIST" census_1e24_state${PASS2:+2}.json ${PASS2:+--rule 2} --workers ${WORKERS:-13} >> census_1e24.log 2>&1
if tail -1 census_1e24.log | grep -q '^FINISHED'; then command -v wa-notify >/dev/null 2>&1 && wa-notify "Math: near-miss census of the 10^24 Carmichael list finished" >/dev/null 2>&1; fi
