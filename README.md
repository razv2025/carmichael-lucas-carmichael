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
  Closing this gap (bigger baskets, asymmetric side design, Wagner k-list
  solver for huge pools) is the research frontier.

## Roadmap

1. ✅ Verifier + harvester + MITM solver + explorer.
2. Margin optimization: config search (hill-climbing on margin), asymmetric
   O1/O2 designs, prime-power caps, larger baskets.
3. Wagner generalized-birthday solver (k-list) for pools ≫ 44 primes.
4. Tighten to full Agrawal conditions: pᵢ ≡ 3 (mod 80) filters, per-prime
   ρ(p)/λ(p) congruence obligations (Váňa's reformulation), r = 5.
5. Certify any hit (ECPP prime certificates) and independent verification.
