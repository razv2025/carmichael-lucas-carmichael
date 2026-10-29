# clc/k4 — Carmichael ∩ Lucas–Carmichael numbers with exactly four prime factors

**Status (2026-10-29): BOTH CAMPAIGNS COMPLETE — no 4-prime CLC number exists with n ≤ 10³⁰, and none exists (for any n) with smallest prime ≤ 500,000.**

| campaign | scope | pairs (p1,p2) | window survivors | Fermat survivors | solutions | wall |
|---|---|---|---|---|---|---|
| `RESULT_n1e30.txt` | all n ≤ 10³⁰ | 230,612,582,193 | 1,904 | 1 | **0** | 87 min |
| `RESULT_p1_500000.txt` | all n, smallest prime p1 ≤ 500,000 | 86,517,004,140 | 1,185 | 1 | **0** | 146 min |

The single Fermat survivor in both is the Carmichael number 26921089 = 13·37·97·577 (not Lucas–Carmichael). Every survivor with
P > 2⁴⁰ (907 + 222 lines) was re-verified independently in Python (`verify_k4.py`): 0 problems. Host: Apple M4 Pro, 14 threads.
Corollary (with Theorem A, n < 477 p1^{15/2}): **any 4-prime CLC number has p1 > 500,000 and n > 10³⁰**; in fact n > p1⁴ > 6×10²².

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
  Π = (1−(d−2)/(dr²))(1−(e−2)/(eq²))(1−(s−2)/(sp2²)) ∈ [1−3/p2², 1+3.0001/p2²].  Each equation read mod p1
  gives t(x²−1) ≡ −2 (mod p1), so p1 ∤ d, e, s, hence d e s ≠ 8p1³, which forces  **p2² ≤ 24 p1³ + 3**
  (and p2² ≡ 1 mod 24 gives p2² ≤ 24p1³+1).  Corollaries: q, r < 2P < 9.9 p1^{5/2};  n < 477 p1^{15/2};
  for each p1 only finitely many n;  a 4-prime CLC number n has p1 > (n/477)^{2/15}.
  Sanity check on the relaxed κ=24 solution 13685 = 5·7·17·23: d=27, e=67, s=977, des=1,767,393, Π=0.97765, des·Π = 13824·125 ✓.
- Heuristic: expected number of 4-prime CLC numbers ≈ Σ_{p1} 54/(p1⁵ ln³p1) ≈ 10⁻⁵, almost all of it at p1 = 13
  (n < 1.1×10¹¹, long excluded).  Mass beyond p1 > X is ~ 3/(X⁴ ln⁴X).

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
- Timings: `--p1max 30000` 42 s; cost ∝ X^{2.5}; `--B 1e24` 6 s, cost ∝ B^{1/2}.  Limits: p2 < 4.29×10⁹ (64-bit L2),
  so B ≤ ~10³⁰ and X ≤ ~8×10⁵ without a 128-bit extension.

## Possible extensions
- 128-bit L2 arithmetic would allow B = 10³² (~15 h) or p1 ≤ 10⁶ (~10 h); heuristic value is small (remaining mass ~ X⁻⁴).
- Proofs and discussion: `docs/k4-notes.md`.
