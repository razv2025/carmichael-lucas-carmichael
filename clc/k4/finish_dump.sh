#!/bin/sh
# Finish the survivor-dump rerun of campaign 2 (its last 16 blocks were lost to a git stash on 2026-11-01), then certify
# both campaigns with hard assertions.  Pauses the 1e24 rescan meanwhile so the blocks finish quickly.
cd "$(dirname "$0")"
../scanctl.sh pause >/dev/null 2>&1
nice -n 10 ./enum_k4 --p1max 500000 --bs 32 --kappa 2 --filter --dumpw --threads 14 --log k4_p1_500000_dump.jsonl --sol k4_p1_500000_dump_sol.txt >> k4_p1_500000_dump.out 2>&1
rc=$?
../scanctl.sh resume >/dev/null 2>&1
echo "enum exit $rc $(date)" >> k4_p1_500000_dump.out
python3 certify_k4.py k4_n1e30_dump.jsonl k4_n1e30_dump_sol.txt --reference k4_n1e30.jsonl --out CERTIFY_n1e30.txt
python3 certify_k4.py k4_p1_500000_dump.jsonl k4_p1_500000_dump_sol.txt --reference k4_p1_500000.jsonl --out CERTIFY_p1_500000.txt
