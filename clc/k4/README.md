# clc/k4 — Carmichael ∩ Lucas–Carmichael numbers with exactly four prime factors

**Status (2026-11-17): no 4-prime CLC (Williams) number exists with n ≤ 10³², and none exists (for any n) with smallest prime ≤ 10⁶.** (October 2026: n ≤ 10³⁰ and p1 ≤ 500,000, each run twice; November 2026: n ≤ 10³² and p1 ≤ 10⁶, each run once and cross-checked against the October runs and each other.)

| campaign | scope | pairs (p1,p2) | window survivors | Fermat survivors | solutions | wall |
|---|---|---|---|---|---|---|
| `RESULT_n1e30.txt` | all n ≤ 10³⁰ | 230,612,582,193 | 1,904 | 1 | **0** | 87 min |
| `RESULT_n1e32.txt` | all n ≤ 10³² | 2,023,458,339,412 | 2,616 | 1 | **0** | ≈12 h running time (est.; suspended by sleep) |
| `RESULT_p1_500000.txt` | all n, smallest prime p1 ≤ 500,000 | 86,517,004,140 | 1,185 | 1 | **0** | 146 min |
| `RESULT_p1_1000000.txt` | all n, smallest prime p1 ≤ 10⁶ | 441,962,984,992 | 1,482 | 1 | **0** | ≈12 h running time (est.; suspended by sleep) |

The single Fermat survivor in all four runs is the Carmichael number 26921089 = 13·37·97·577 (not Lucas–Carmichael). Every survivor with
P > 2⁴⁰ (907 + 222 lines in October; 1,619 + 485 in November) was re-verified independently in Python (`verify_k4.py`): 0 problems. Host: Apple M4 Pro, 14 threads.
Corollary: **any 4-prime CLC number has p1 > 10⁶ and n > 10³²**.

November extension, extra checks: `CERTIFY_p1_1000000.txt` asserts blocks 0–321 equal to the October p1 ≤ 500,000 log field by field; `CROSSCHECK_ext.txt` (`crosscheck_ext.py`): the survivor sets of the four runs agree exactly on all three overlaps; `make highend` (`highend_test.c`, `highend_test.py`): CRT class, candidate counts and survivors of the production routine vs. Python big integers on 20,000 pairs with p1 > 915,000 (4,539 inconsistent in both; of the other 15,461, 15,433 have (p2²−1)/2 ≥ 2⁶³), 0 mismatches; output archived in `HIGHEND_2026-11-15.txt`. Driver: `run_k4_ext.sh`.

## What this is
Williams (1977) proved a CLC number cannot have k = 3 prime factors. k = 4 is the first open case
(all four primes must be ≡ 1 mod 4). This directory holds a complete, validated enumerator for k = 4,
plus a new elementary theorem that makes the k = 4 problem finite for each smallest prime p1.

## Mathematics (all proved from the two divisibility conditions; full write-up still to be written — see TODO)
Notation: n = p1 p2 q r (p1<p2<q<r), P = p1 p2, L_p = (p²−1)/2.  CLC ⟺ n/p ≡ 1 (mod L_p) for every p | n.
- (F1) all four primes ≡ 1 (mod 12)  [mod 4 from Korselt; mod 3 from Williams's 3 ∤ n].
- (F2) 2Pq = d(r²−1)+2 with integer d ≥ 1  ⇒  q < 2P, r < √(2Pq), m := qr < 4P², n < 4P³, d < 2p1.
  Likewise 2Pr = e(q²−1)+2, and 2 p1 q r = s(p2²−1)+2 (condition at p2).
  Cubic representation: 2n = t p³ − (t−2) p for every p | n, t = (n/p − 1)/L_p.
- (F3) Conditions at p1, p2 put m in ONE residue class mod lcm(L1, L2); solvable iff p1 ≡ p2 (mod gcd(L1,L2)).
- (F4) With j = d·e:  |jm − 4P²| ≤ max(2j√(2p1), 8p1).  (Filter. The admissible j for fixed m form an interval,
  so "floor or ceil of 4P²/m passes" is an exact test — but the TRUE j need not be floor/ceil; the self-tests caught this.)
- **(F6) THEOREM A (new):** multiply the three equations in (F2): d·e·s·Π = 8p1³ with
  Π = (1−(d−2)/(dr²))(1−(e−2)/(eq²))(1−(s−2)/(sp2²)) ∈ [(1−1/p2²)³, (1+1/p2²)³].  Each equation read mod p1
  gives t(x²−1) ≡ −2 (mod p1), so p1 ∤ d, e, s, hence d e s ≠ 8p1³. If Π<1 this forces p2² ≤ 24p1³+3; if Π>1 only the
  d-factor can exceed 1 (e>d≥1, s>2p1), so Π ≤ 1+1/r² and r² ≤ 8p1³−1. Either way **p2² ≤ 24 p1³ + 1**
  (and p2² ≡ 1 mod 24 gives p2² ≤ 24p1³+1).  Corollaries: q, r < 2P < 9.9 p1^{5/2};  n < 477 p1^{15/2};
  for each p1 only finitely many n;  a 4-prime CLC number n has p1 > (n/477)^{2/15}.
  Sanity check on the relaxed κ=24 solution 13685 = 5·7·17·23: d=27, e=67, s=977, des=1,767,393, Π=0.97765, des·Π = 13824·125 ✓.
- Heuristic: expected number of 4-prime CLC numbers ≈ 6×10⁻⁷ (`agrawal/k4_heuristic.py`), ~96% of it at p1 = 13
  (n < 1.1×10¹¹, long excluded).  Mass beyond p1 > X decays like X⁻⁴.

## Code
- `enum_k4.c` — the enumerator (C, pthreads, __int128). Two modes: `--B 1e30` (all n ≤ B) and `--p1max X`
  (ALL n with smallest prime ≤ X, no bound on n, via Theorem A). Checkpointed per block (JSONL log); rerun = resume.
  Walk per pair: CRT class, two-sweep candidate walk (sweep A over m with floor/ceil j; sweep B over j for large m),
  window filter (F4), base-2 Fermat filter, exact reconstruction of r via the cubic (F5) with d ≤ 2p1, full check.
  For P > 2⁴⁰ (n may exceed 128 bits) survivors are written as `WSURV` lines and verified by `verify_k4.py`.
- `brute_k4.c` — brute force for the κ-relaxed problem (n/p ≡ 1 mod (p²−1)/κ); matches a Python brute force exactly.
- `verify_k4.py` — independent sympy re-verification of SOLUTION / FSURV / WSURV lines.
- `run_k4.sh` — production driver (campaign 1: n ≤ 1e30 ≈ 1.5 h; campaign 2: p1 ≤ 500,000 ≈ 14 h, est.).
  Launch detached: `nohup ./run_k4.sh > run_k4.log 2>&1 &`.   Control: `./k4ctl.sh status|pause|resume|stop`.
  Results land in `RESULT_n1e30.txt` and `RESULT_p1_500000.txt` (each includes the Python re-verification).

## Validation done (all passing)
- Self-tests `--selftest`: T1 brute-forces the (q,r) half-problem for small pairs in four relaxed variants
  (43 half-solutions) and checks (F2),(F4),(F5) and reconstruction through both code paths; T2 brute-forces the
  CRT class for 13,037 pairs. Zero violations.  (T1 is what caught the floor/ceil misconception.)
- End-to-end on the relaxed κ=24 problem: finds exactly 13685, the only solution brute force finds below 10¹².
- Two-sweep walk vs. simple walk (`--oldwalk --dumpw`): identical survivor lists on six instances (incl. 11,007,875 survivors).
- Real problem: `--B 1e24` → 0 solutions in 6 s (consistent with the full 10²⁴ scan in `clc/`); only base-2
  pseudoprime survivor is the Carmichael number 26921089 = 13·37·97·577, correctly rejected.
- Timings: `--p1max 30000` 42 s; cost ∝ X^{2.5}; `--B 1e24` 6 s, cost ∝ B^{1/2}.  Limit: L2 = (p2²−1)/2 < 2⁶⁴ (asserted per pair),
  i.e. p2 < 6.07×10⁹: X ≤ ~1.15×10⁶ in `--p1max` mode; in `--B` mode p2 stays far below this (≤ 7.1×10⁸ at B = 10³²), only the sieve grows.

## Possible extensions
- Done in November 2026 without any 128-bit extension: B = 10³² and p1 ≤ 10⁶ (≈12 h each). Going further in p1 needs 128-bit L2; heuristic value is small (remaining mass ~ X⁻⁴).
- Proofs and discussion: `docs/k4-notes.md`.
