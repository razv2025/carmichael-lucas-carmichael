# CLC verification: no Carmichael number ≤ 10²² is Lucas–Carmichael

Verified 2026-10-20 on the M4 Pro, independently of Goutier's flags.

- `scan_carmichael_list_for_clc.py` — input: a numbers-only list of Carmichael
  numbers (Goutier's list to 10²², 49,679,870 lines, OEIS A002997/a002997.7z).
  Line-based batching (no byte-offset splitting, so no line can be dropped);
  factors each n by Miller–Rabin √1-splitting with a general-factoring fallback
  for non-Carmichael cofactors; re-verifies product, primality, squarefreeness
  and Korselt; counts primes p with (p+1) | (n+1). 12 workers, 1761 s.
  Run as `python3 -I scan_carmichael_list_for_clc.py LIST.txt`.
- `check_lc_table_for_carmichael.py` — the converse check on Suteu's complete
  Lucas–Carmichael table to 10¹⁵ (OEIS A006972/a006972.txt): Korselt on each.
- `RESULT_1e22_2026-10-20.txt` — output. Cross-checks that all passed:
  total 49,679,870 = Goutier = Shallue–Webster; per-ω counts equal Goutier's
  published tally in all 11 classes; exactly 179 numbers have 3 primes with
  p+1 | n+1, equal to Eldar's OEIS A329948; zero verification failures;
  **zero full hits**. Best partial: 3 matching primes (never more).

## Operating a scan: `scanctl.sh` and `scan_resumable.py` (added 2026-10-20)

Lessons from the first 10²⁴ run: the original scanner cannot be stopped
without losing all progress, and pausing it by hand failed twice because zsh
does not word-split unquoted variables (so `kill $PIDS` saw one bogus pid).

- `scanctl.sh status|pause|resume|stop [--force]`
  - `pause` / `resume` send SIGSTOP / SIGCONT to every scan process (found by
    pattern, split with `xargs`) and print the resulting states. Instant,
    zero loss, memory kept (~0.3 GB); survives sleep, not reboot/logout.
  - `stop` sends SIGTERM for a graceful checkpoint-and-exit. It REFUSES for
    the old non-resumable scanner unless `--force`.
- `scan_resumable.py LIST STATE.json [--workers 12] [--chunk 100000]` —
  the same factor-and-test as `scan_carmichael_list_for_clc.py`, but with
  bounded in-flight submission and an atomically-written checkpoint
  (completed chunk ids, byte offsets, all aggregates). SIGTERM/Ctrl-C finish
  the in-flight chunks, checkpoint, and exit; rerunning the same command
  continues. "Pause and release memory" is therefore just `stop` + rerun.
  Verified: a run killed at 33/75 chunks and resumed produced aggregates
  identical to an uninterrupted run, every chunk processed exactly once.

Use `scan_resumable.py` for all future runs.
