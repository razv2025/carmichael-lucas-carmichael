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
  p+1 | n+1, equal to OEIS A329948 (Suteu; b-file by Eldar); zero verification failures;
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

## Extension to 10²⁴ — verified 2026-10-21

Source: all 308,279,939 Carmichael numbers < 10²⁴ (Shallue–Webster's
tabulation) as Hermann Stamm-Wilbrandt's public PARI `writebin` vector
(https://stamm-wilbrandt.de/carm10e24.bin, 12,296,962,769 bytes, dated
7 Mar 2026). Pipeline (`pipeline_1e24.sh`): download (size verified) →
decode with PARI/GP `read()` (`decode_pari_writebin.gp`) → completeness
check (`verify_carmichael_list.py`, output `VERIFY_1e24_list_completeness.txt`:
counts below 10²²/10²³/10²⁴ = 49,679,870 / 123,381,982 / 308,279,939 exactly
as published, strictly increasing, first five 561, 1105, 1729, 2465, 2821)
→ scan (`scan_carmichael_list_for_clc.py`, 12 workers, 21 h of compute).

Result (`RESULT_1e24_2026-10-21.txt`): **zero Lucas–Carmichael among all
308,279,939 Carmichael numbers below 10²⁴**, zero verification failures.
New near-miss record: 15500309690554865758009 (≈1.55×10²², nine prime
factors) has **four** primes with p+1 | n+1 — no number below 10²² has more
than three. 826 numbers have exactly three (179 below 10²²).

Independent per-ω cross-checks of the 10²⁴ scan against published OEIS data
(both computed by other people with other code):
- three-prime Carmichael numbers below 10²⁴: ours 1,494,738 = OEIS A132195
  a(24) (J. M. Chick's tabulation, arXiv:0711.2915); below 10²²: 420,658 ✓.
- eleven-prime Carmichael numbers below 10²⁴: ours 6,529,921 = OEIS A299711
  a(24); below 10²²: 262,818 ✓.

## Rescan with the full match histogram — 2026-11-02

`rescan_1e24.sh` reran the complete list with `scan_resumable.py` (checkpointed) to record how many Carmichael numbers below
10²⁴ have exactly g primes with p+1 | n+1, for every g (the first run kept only the g = 3 count and one maximiser).
Result (`RESULT_1e24_rescan_2026-11.txt`, certified by `certify_rescan.py` → `CERTIFY_1e24_rescan.txt`): all per-ω counts,
the 826 three-match count and the maximiser agree with the first run; **exactly 14 numbers have four matching primes**
(ω = 9: 7, ω = 10: 5, ω = 11: 2), none has five; 63,231 have two and 5,807,346 have one. Zero verification failures, zero hits.
(During this run a checkpoint race in `scan_resumable.py` was found and fixed: the main loop wrote `offsets` outside the lock
used by the result-callback thread while it serialised the state.)