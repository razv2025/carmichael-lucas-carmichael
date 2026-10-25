#!/bin/sh
# Production driver for the 4-prime CLC enumeration.  Runs on the Mac only; safe to re-run (resumes by block).
#   ./run_k4.sh            -> runs the two campaigns below, writes RESULT files when complete
# Campaign 1: all n ≤ 1e30                 (log k4_n1e30.jsonl,  sol k4_n1e30_sol.txt)
# Campaign 2: all n with p1 ≤ P1MAX (no bound on n; Theorem A)   (log k4_p1_${P1MAX}.jsonl, ...)
# Launch detached:  nohup ./run_k4.sh > run_k4.log 2>&1 &
# Pause/resume/stop:  ./k4ctl.sh pause | resume | stop | status
set -u
cd "$(dirname "$0")"
P1MAX=${P1MAX:-500000}
THREADS=${THREADS:-14}
echo "$$" > run_k4.pid
[ -x ./enum_k4 ] || cc -O3 -march=native -o enum_k4 enum_k4.c -lpthread -lm || exit 1

campaign() { # name args...
  name=$1; shift
  if [ -f "RESULT_${name}.txt" ]; then echo "[$name] already complete"; return 0; fi
  echo "[$name] start $(date)"
  nice -n 10 ./enum_k4 "$@" --kappa 2 --filter --threads "$THREADS" --log "k4_${name}.jsonl" --sol "k4_${name}_sol.txt" > "k4_${name}.out" 2>> "k4_${name}.err"
  rc=$?
  echo "[$name] enum exit $rc $(date)"
  if [ $rc -eq 0 ]; then
    {
      echo "# 4-prime Carmichael–Lucas–Carmichael enumeration — campaign $name — $(date)"
      echo "# command: enum_k4 $* --kappa 2 --filter"
      echo "# host: $(hostname) $(sysctl -n machdep.cpu.brand_string 2>/dev/null)"
      tail -1 "k4_${name}.out"
      echo "# Python re-verification of every SOLUTION / FSURV / WSURV line:"
      python3 verify_k4.py "k4_${name}_sol.txt" 2>&1 | tail -20
    } > "RESULT_${name}.txt"
    cat "RESULT_${name}.txt"
  fi
  return $rc
}

campaign n1e30 --B 1e30 || exit 1
campaign "p1_${P1MAX}" --p1max "$P1MAX" --bs 32 || exit 1
echo "ALL DONE $(date)"
rm -f run_k4.pid
