# Exhaustive search for (7,3,4): a⁷+b⁷+c⁷ = d⁷+e⁷+f⁷+g⁷

*Working notes, started 2026-08-18. Code: `lps/engine734.c`, `lps/verify.py`.
Logs: `lps/prog734_*.jsonl` (one JSON line per slab = the coverage proof).*

## 1. Why this case

The Lander–Parkin–Selfridge conjecture asserts that a sum of m k-th powers
equal to a sum of n k-th powers (disjoint sides) forces m+n ≥ k. The cases
with m+n = k are the "tight" ones: heuristically they should have solutions
(log-density), several are known for k ≤ 6 and k = 8, but for **k = 7 all
four tight cases (7,1,6), (7,2,5), (7,3,4), (7,4,3) are open**, and the
published search bounds are term ranges of roughly 1,000–1,400 from
EulerNet circa 2001 — untouched for 25 years while attention went to k = 5
and k = 6 (Braun 2026 pushed (5,1,3) to d ≤ 2.76×10⁶ with 10.5M vCPU-hours;
yoyo@home exhausted (6,2,5) to 250,000 in 2011).

Among the k = 7 tight cases, (7,3,4) is the cheapest: the 3|4 split is the
most balanced meet-in-the-middle, giving O(H⁴) work instead of the O(H⁵)
of a 2|5 split.

## 2. Method

Slab meet-in-the-middle, following Bernstein (Math. Comp. 2001) and
Eisermann (arXiv:0803.3273):

- The value interval [0, 3H⁷] is partitioned into slabs with roughly equal
  left-side population (boundaries at zmax·(i/n)^(7/3)).
- Per slab: enumerate every 3-term sum a⁷+b⁷+c⁷ (a ≥ b ≥ c) landing inside
  the slab, bucket by the low byte, sort by **full 128-bit value**; fill a
  bitmap sized to the slab (~32 slots per entry, so it stays cache-resident).
- Then enumerate every 4-term sum d⁷+e⁷+f⁷+g⁷ in the slab, probe the bitmap
  (48 probes prefetched ahead), and on a hit binary-search the bucket and
  compare full 128-bit values.
- Any match is written to the candidate file and verified independently in
  Python with exact big integers before being believed.

**Coverage proof.** Slabs partition the value space, so a completed set of
slab records is a certificate of exhaustive coverage for that H. Each record
logs the slab's z-interval and its left/right tuple counts; the search
resumes from the record count, so interruptions cost at most one slab.

**Validation.** The engine is compiled with a `POWER` macro and cross-checked
against an independent Python brute force at k = 3 (81,079 matches
reproduced exactly, across several slab counts) and at k = 11, H = 80, where
values exceed 2⁶⁴ (guards the 128-bit path). The Python reference also
reproduces Lander–Parkin's 1967 (5,1,3) empty range in 2 seconds.

## 3. Results

| range | status | tuples scanned | candidates |
|---|---|---|---|
| **H ≤ 2,000, exhaustive** | **complete, no solution** | 6.69×10¹¹ | 0 |
| H ≤ 12,000 | in progress (836/14,400 slabs) | 3.13×10¹³ | 0 |

The H ≤ 2,000 result already exceeds the ~1,000–1,400 bounds of record, and
is the first extension of the (7,3,4) range since 2001.

## 4. Engineering notes (measured, not assumed)

- **Match on full 128-bit values, never low-64 keys.** A low-64 key scheme
  passed every small test and then produced a 3.8 GB candidate file at
  H = 2,000: tuples built from multiples of 2¹⁰ have seventh powers ≡ 0 mod
  2⁶⁴, so 2-adically smooth families collide structurally, not randomly.
  Regression test: POWER=11, H=80 (values > 2⁶⁴).
- **A galloping pointer-walk over a value-sorted left table was slower**
  than bitmap+binary-search and was discarded: each (d,e,f) triple's g-range
  re-enters the slab near its bottom, so walks traverse the whole table.
- **Software prefetch alone bought 1.09×** — the M4's out-of-order engine
  already overlapped those misses.
- **Shrinking the random-access footprint bought the real win**: sizing the
  bitmap per slab (instead of a fixed 1 GiB) and using 10× more slabs gave
  **1.89× end-to-end** (3462 s → 1829 s at H = 2,000; 3.66×10⁸ tuples/s).
- **Optimization round 2 (all measured at H=1500/7600 slabs; ~2-3% run-to-run
  variance, so only the first clears noise):** two-pointer g-bounds
  (`OPT_PTR`, monotone in f) **+8.6% — kept**; low-64-only hot path
  (`OPT_LO64`) 0% alone and -1.6% with PTR — rejected; residue-class skipping
  mod 29/43 (`OPT_RESIDUE`) **0.0% despite eliminating 26% of bitmap probes**
  — rejected; short-range fast path (`OPT_SHORT`) -12.5% — rejected; running
  at nice 0 instead of 10 gains only 5%. The OPT_RESIDUE result is the
  instructive one: it is the classical sieving technique from the literature,
  it is correct mathematics, and it is worthless here because after the grid
  migration the bitmap probe is no longer the bottleneck. Measure before
  optimizing.
- **Cumulative speedup over the original engine: 2.8x** (1.62e8 -> 4.46e8
  tuples/s, production-to-production at H=12000), cutting the full sweep from
  ~99 to ~36 days of compute.
- **Throughput is dominated by free RAM, and degrades as a cliff, not a
  slope.** Under memory pressure (3.3 GB of 4 GB swap in use, 1.8M pageouts)
  slabs ran at 2.7×10⁶ tuples/s — ~90× slower — while still showing ~1000%
  CPU, because the threads were faulting rather than computing. It recovered
  to full speed on its own when other applications released memory. If this
  becomes chronic, doubling the slab count halves the per-slab working set.

## 5. Next

1. Finish H = 12,000 (≈33 days of clean running at 3.6×10⁸ tuples/s).
2. (7,2,5) and (7,1,6) variants. Both are costlier than (7,3,4) — the term
   splits are less balanced — so expect materially lower H for equal effort.
3. If (7,3,4) stays empty to H = 12,000, that is a publishable negative
   result: a 10× extension of a 25-year-old bound, with a reproducible
   coverage certificate.
