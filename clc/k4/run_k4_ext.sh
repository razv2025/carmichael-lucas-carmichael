#!/bin/sh
# Extension campaigns (November 2026): smallest prime p1 ≤ 10^6 (no bound on n), then all n ≤ 10^32.
# One execution each, with every window survivor dumped (--dumpw), followed by the Python re-verification and the
# hard-assertion certificate.  Safe to re-run: finished blocks are skipped, finished campaigns are skipped.
# Launch detached:  nohup ./run_k4_ext.sh > run_k4_ext.log 2>&1 &      Control: ./k4ctl.sh status|pause|resume|stop
# NEVER run git stash / clean / checkout that removes files in this directory while this is running.
set -u
cd "$(dirname "$0")"
THREADS=${THREADS:-14}
notify() { command -v wa-notify >/dev/null 2>&1 && wa-notify "$1" >/dev/null 2>&1; :; }
[ -x ./enum_k4 ] || { echo "build enum_k4 first (make)"; exit 1; }

campaign() { # name certify-extra-args -- enum args...
  name=$1; extra=$2; shift 2
  if [ -f "CERTIFY_${name}.txt" ] && grep -q '^CERTIFIED' "CERTIFY_${name}.txt"; then echo "[$name] already certified"; return 0; fi
  echo "[$name] start $(date)"
  caffeinate -i nice -n 10 ./enum_k4 "$@" --kappa 2 --filter --dumpw --threads "$THREADS" --log "k4_${name}.jsonl" --sol "k4_${name}_sol.txt" > "k4_${name}.out" 2>> "k4_${name}.err"
  rc=$?
  echo "[$name] enum exit $rc $(date)"
  [ $rc -eq 0 ] || { notify "Williams k=4 run $name FAILED (enum exit $rc)"; return $rc; }
  {
    echo "# 4-prime Williams-number enumeration — campaign $name — $(date)"
    echo "# command: enum_k4 $* --kappa 2 --filter --dumpw"
    echo "# host: $(hostname) $(sysctl -n machdep.cpu.brand_string 2>/dev/null)"
    tail -1 "k4_${name}.out"
    echo "# Python re-verification of every SOLUTION / FSURV / WSURV / W line:"
    python3 verify_k4.py "k4_${name}_sol.txt" 2>&1 | tail -20
  } > "RESULT_${name}.txt"
  # shellcheck disable=SC2086
  python3 certify_k4.py "k4_${name}.jsonl" "k4_${name}_sol.txt" $extra --out "CERTIFY_${name}.txt" > /dev/null 2>"certify_${name}.err"
  crc=$?
  echo "[$name] certify exit $crc $(date)"; tail -1 "CERTIFY_${name}.txt"
  if [ $crc -eq 0 ]; then notify "Williams k=4 run $name done and CERTIFIED: $(tail -1 "k4_${name}.out" | cut -c1-150)"
  else notify "Williams k=4 run $name finished but certification FAILED - see CERTIFY_${name}.txt"; fi
  return $crc
}

campaign p1_1000000 "--reference k4_p1_500000.jsonl --reference-prefix" --p1max 1000000 --bs 32 || exit 1
campaign n1e32 "" --B 1e32 || exit 1
echo "ALL DONE $(date)"
