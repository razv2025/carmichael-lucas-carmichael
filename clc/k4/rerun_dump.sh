#!/bin/sh
# Re-run both campaigns with --dumpw so that EVERY window survivor is written out and can be re-verified in Python.
cd "$(dirname "$0")"
nice -n 10 ./enum_k4 --B 1e30 --kappa 2 --filter --dumpw --threads 14 --log k4_n1e30_dump.jsonl --sol k4_n1e30_dump_sol.txt > k4_n1e30_dump.out 2>&1
nice -n 10 ./enum_k4 --p1max 500000 --bs 32 --kappa 2 --filter --dumpw --threads 14 --log k4_p1_500000_dump.jsonl --sol k4_p1_500000_dump_sol.txt > k4_p1_500000_dump.out 2>&1
{ echo "# Python re-verification of ALL window survivors (dump rerun, $(date))"; for f in k4_n1e30_dump_sol.txt k4_p1_500000_dump_sol.txt; do echo "## $f: $(grep -c '^W ' $f) W lines, $(grep -c '^WSURV' $f) WSURV, $(grep -c '^FSURV' $f) FSURV, $(grep -c '^SOLUTION' $f) SOLUTION"; python3 verify_k4.py $f | tail -3; done; } > RESULT_dump_reverify.txt 2>&1
echo DONE >> RESULT_dump_reverify.txt
