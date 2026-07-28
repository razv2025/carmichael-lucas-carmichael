# Agrawal counterexample hunt

Search infrastructure targeting **Agrawal's conjecture** (from the AKS
primality test), which is heuristically expected to be **false**
(Lenstra–Pomerance, [AIM notes pp. 30–32](http://www.aimath.org/WWN/primesinp/primesinp.pdf)):

> If r is a prime not dividing n and (X−1)^n ≡ X^n − 1 (mod n, X^r − 1),
> then n is prime or n² ≡ 1 (mod r).

A counterexample would collapse AKS to a single congruence (Õ(log³ n) primality
testing). The known counterexample mechanism (r = 5) requires n = p₁⋯p_k,
k odd, all pᵢ ≡ 3 (mod 80), with n simultaneously a **Carmichael** number
((pᵢ−1) | (n−1)) and a **Lucas–Carmichael** number ((pᵢ+1) | (n+1)).

## Current phase: the milestone hunt

**No number that is both Carmichael and Lucas–Carmichael is known to exist.**
Finding the first is a standalone open problem and a strict prerequisite of the
Lenstra–Pomerance route. Construction: fix coprime odd smooth moduli O1, O2 and
a 2-adic budget; harvest primes p with (p−1)/2 | O1 and (p+1) | 2^a·O2; then
any subset with product ≡ 1 (mod lcm(p−1)) and ≡ −1 (mod lcm(p+1)) is a hit
(Korselt). This is the Erdős / Löh–Niebuhr / Alford–Granville–Pomerance
subset-product method with *two-sided* conditions — the two-sided smoothness
coupling (d | O1 and (d+1) | 2^a·O2 simultaneously) is the entire difficulty.

## Layout

- `agrawal/verify.py` — the referee: exact Agrawal congruence check (direct and
  per-prime CRT), Carmichael / Lucas–Carmichael verification. Nothing counts
  unless it passes here.
- `agrawal/harvest.py` — prime harvesting by divisor enumeration of smooth moduli.
- `agrawal/solver.py` — modulus/target construction (CRT over prime powers),
  greedy subpool selection, meet-in-the-middle subset-product search.
- `agrawal/explore.py` — background sweep over (O1, O2, a2) configurations;
  logs `pool_size`, `log2_phi_M` and the key dashboard metric
  `margin = pool_size − log2 φ(M)` (expected hits ≈ 2^margin).
- `tests/` — pytest suite (run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/`).

## Status / findings log

- 2026-07-28: pipeline built and validated — the solver reproduces classic
  Carmichael numbers from the Λ = 5040 pool instantly. First random CLC sweeps
  show margins around **−70**: pools of ~20 primes against ~74-bit moduli.
- 2026-07-28 (later): random config sweeps (3,250 configs): best margin −8.2,
  all configs above −14 searched exhaustively, no hit (~1% cumulative odds
  consumed). Plateau in the −8..−16 range for tiny matched pools.
- 2026-07-28 (evening): **twin-smooth reformulation.** New harvester finds all
  primes with p±1 y-smooth by smooth-set intersection: 2,534 primes at
  (y=100, X=1e9) in 1.4s; 7,727 at (y=140, X=2e9). Split optimizer (hill-climb
  over side assignments) reveals the **margin wall: ≈ −30, flat across
  y = 60/100/140**. Cause, quantified: a global side-assignment keeps only
  ~s usable primes (s = number of odd side primes) while the modulus costs
  ~2.5s bits — the two-sided coupling loses ~1.5 bits per prime no matter y.
  Breaking the wall needs structurally cheaper primes (low ω(p∓1) "golden"
  twins via Pell/Størmer–CHM enumeration), subset-lcm (not pool-lcm)
  formulations, or a fundamentally better selection method.

## Roadmap

1. ✅ Verifier + harvester + MITM solver + explorer.
2. Margin optimization: config search (hill-climbing on margin), asymmetric
   O1/O2 designs, prime-power caps, larger baskets.
3. Wagner generalized-birthday solver (k-list) for pools ≫ 44 primes.
4. Tighten to full Agrawal conditions: pᵢ ≡ 3 (mod 80) filters, per-prime
   ρ(p)/λ(p) congruence obligations (Váňa's reformulation), r = 5.
5. Certify any hit (ECPP prime certificates) and independent verification.
