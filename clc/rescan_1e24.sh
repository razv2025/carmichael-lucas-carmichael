#!/bin/sh
# Rescan of all Carmichael numbers < 1e24 with the resumable scanner, recording the FULL (matching primes, omega)
# histogram (the 2026-10-21 run recorded only the first number attaining the maximum).  ~21 CPU-hours on 12 workers; resumable: rerun this
# script to continue after a stop (./scanctl.sh stop) or a reboot.
cd "$(dirname "$0")"
LIST=${LIST:-/Users/razvakil/.claude/jobs/c6e4e4e0/tmp/c24/carm10e24.txt}
STATE=rescan_1e24_state.json
OUT=RESULT_1e24_rescan_2026-11.txt
[ -f "$LIST" ] || { echo "input list missing: $LIST (re-create with pipeline_1e24.sh)"; exit 1; }
echo "# rescan started $(date); input $LIST ($(stat -f %z "$LIST") bytes)" >> rescan_1e24.log
nice -n 10 python3 -I scan_resumable.py "$LIST" "$STATE" --workers 12 >> rescan_1e24.log 2>&1
if grep -q '^FINISHED' rescan_1e24.log; then
  { echo "# Rescan of all 308,279,939 Carmichael numbers < 1e24 with the full histogram — $(date)"
    echo "# input SHA-256: see DATA_SHA256.txt (carm10e24.txt)"; sed -n '/^FINISHED/,$p' rescan_1e24.log; } > "$OUT"
fi
