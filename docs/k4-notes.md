# Carmichael ∩ Lucas–Carmichael numbers with four prime factors

*Working note, 2026-10-29. Code, logs and result files: `clc/k4/`.*

## 1. Statement

A squarefree n = p₁⋯p_k is **CLC** if (p−1) | (n−1) and (p+1) | (n+1) for every p | n.
Williams (1977) showed k ≠ 3 and 3 ∤ n. Four prime factors is the first open case.

**Theorem A.** Let n = p₁p₂p₃p₄ (p₁<p₂<p₃<p₄) be CLC. Then
(a) every pᵢ ≡ 1 (mod 12);
(b) p₃ < 2p₁p₂, p₄ < √(2p₁p₂p₃) < 2p₁p₂, and n < 4(p₁p₂)³;
(c) p₂² ≤ 24p₁³ + 1.
Consequently p₃, p₄ < 9.9 p₁^{5/2}, n < 477 p₁^{15/2}, and for each p₁ there are only finitely many such n.

**Theorem B (computation).** There is no 4-prime CLC number with n ≤ 10³⁰, and none whatsoever with p₁ ≤ 500,000.
Hence any 4-prime CLC number has p₁ > 500,000 and n > 10³⁰.

## 2. Proofs

**Lemma 1.** For p | n: n is CLC at p ⟺ n/p ≡ 1 (mod L_p), L_p := (p²−1)/2.
*Proof.* (p−1)|(n−1) and (p+1)|(n+1) ⟺ n ≡ p (mod lcm(p−1,p+1)) = (mod L_p) ⟺ L_p | n−p = p(n/p−1) ⟺ L_p | n/p − 1, since gcd(p, p²−1) = 1. ∎

**(a).** 4 | L_p for every odd p, so n ≡ p (mod 4) for all p | n: all pᵢ lie in one class c mod 4 and n ≡ c⁴ ≡ 1, so c = 1.
For p ≠ 3, 3 | L_p, so n ≡ p (mod 3) for every p | n with p ≠ 3; if 3 | n this forces every other prime ≡ 0 (mod 3), absurd, so 3 ∤ n (Williams) and all pᵢ ≡ n ≡ c⁴ ≡ 1 (mod 3). ∎

**(b).** Write P = p₁p₂, q = p₃, r = p₄. Lemma 1 at r: Pq − 1 = d·L_r with an integer d ≥ 1, i.e.
  2Pq = d(r²−1) + 2.                                   (iii)
Hence 2Pq ≥ r² + 1 > q², so q < 2P and r < √(2Pq) < 2P; thus m := qr < 4P² and n = Pm < 4P³. Also d < 2Pq/(r²−1) < 2P/q < 2p₁.
Likewise Lemma 1 at q and at p₂ give integers e, s ≥ 1 with
  2Pr = e(q²−1) + 2,      2p₁qr = s(p₂²−1) + 2.        (iv), (ii)
(Equivalently 2n = t·p³ − (t−2)·p for every p | n, with t = (n/p − 1)/L_p.) ∎

**(c).** Multiply (iii), (iv), (ii): the left side is 8p₁³p₂²q²r²; the right side is
  d·e·s · r²q²p₂² · Π,  Π := (1 − (d−2)/(dr²)) (1 − (e−2)/(eq²)) (1 − (s−2)/(sp₂²)).
So d·e·s·Π = 8p₁³. Each factor of Π lies in [1 − 1/x², 1 + 1/x²] with x ∈ {r, q, p₂} ≥ p₂, so
  (1 − 1/p₂²)³ ≤ Π ≤ (1 + 1/p₂²)³.
Now read (iii), (iv), (ii) modulo p₁: the left sides vanish, so d(r²−1) ≡ e(q²−1) ≡ s(p₂²−1) ≡ −2 (mod p₁); as p₁ ≥ 13 is odd, p₁ ∤ d, e, s. Hence d·e·s ≠ 8p₁³, i.e. Π ≠ 1.
If Π < 1 then des ≥ 8p₁³ + 1 and Π = 8p₁³/des ≤ 1 − 1/(8p₁³+1); with Π ≥ 1 − 3/p₂² this gives p₂² ≤ 24p₁³ + 3.
If Π > 1: a factor of Π exceeds 1 only when its quotient is 1; e > d ≥ 1 (as r > q) and s > 2p₁ (as qr ≥ p₂²+1), so only
the d-factor can, and Π ≤ 1 + 1/r². With des ≤ 8p₁³ − 1 we get Π ≥ 1 + 1/(8p₁³−1), hence r² ≤ 8p₁³ − 1 and p₂² < r² < 8p₁³.
In either case p₂² ≤ 24p₁³ + 1 (the first case via p₂² ≡ 1 mod 24). ∎
**Correction (2026-10-29):** the first write-up handled Π > 1 with "(1+1/p₂²)³ ≤ 1 + 3.0001/p₂²", which is false (coefficient 3.0022 at
p₂ = 37) and does not close; caught by the independent fact-check (docs/review-facts-2026-10-29.md). The enumeration used p₂² ≤ 24p₁³+3,
satisfied in both cases, so Theorem B stands.

*Consequences.* p₂ < 4.9p₁^{3/2}; p₃ < 2P < 9.8p₁^{5/2}; p₄ < 2P; n < 4P³ < 4·(4.9)³·p₁^{15/2} < 477p₁^{15/2}.

*Check on a relaxed instance.* With the modulus (p²−1)/24 instead of (p²−1)/2 the same algebra gives d·e·s·Π = 24³p₁³, and the solution 13685 = 5·7·17·23 has d=27, e=67, s=977: des = 1,767,393, Π = 0.977650, des·Π = 1,728,000 = 24³·5³. ✓

## 3. Algorithm (`clc/k4/enum_k4.c`)

For each admissible pair p₁ < p₂ (both ≡ 1 mod 12; p₂ ≤ min((B/p₁)^{1/3}, √(24p₁³+3))):
1. Lemma 1 at p₁ and p₂: p₂m ≡ 1 (mod L₁), p₁m ≡ 1 (mod L₂). Solvable iff p₁ ≡ p₂ (mod gcd(L₁,L₂)) (about 23% of pairs); then m lies in one class mod Λ = lcm(L₁,L₂) ≈ P²/(4·gcd).
2. Candidates m ≡ m₀ (mod Λ) in (p₂², min(4P², B/P)]. With j := d·e, (iii)·(iv) gives
   jm² − 4P²m = j(q²+r²−1) − 4P(q+r) + 4, hence |jm − 4P²| ≤ max(2j√(2p₁), 8p₁).
   The admissible j for a fixed m form an interval containing 4P²/m, so testing ⌊4P²/m⌋ and ⌈4P²/m⌉ is an exact filter
   (the true j itself need not be either — the self-tests caught this). For large m the walk goes over j instead of m.
3. Survivors: base-2 Fermat test on n (necessary for Carmichael numbers), then r is recovered as an integer root of
   dx³ − (d−2)x − 2n for d ≤ 2p₁, q = m/r, and all four conditions plus primality are checked; everything is re-verified
   independently in Python (`verify_k4.py`).
Cost: ~B^{1/2}/log²B pairs for the n-bounded run, ~X^{5/2} for the p₁-bounded run; 32 million pairs/s on the M4 Pro.

**Validation.** Brute-force self-tests on the (q,r) half-problem in four relaxed variants (43 half-solutions) check (iii), the
window inequality, the cubic, and both reconstruction paths; the CRT class is brute-forced for 13,037 pairs; the two-sweep walk
reproduces a single-sweep reference on six instances (up to 11,007,875 survivors); on the relaxed problem the enumerator finds
exactly the one solution (13685) that brute force finds below 10¹²; on the real problem `--B 1e24` reproduces the empty result of
the complete 10²⁴ scan in 6 s.

## 4. Results (2026-10-29, Apple M4 Pro, 14 threads)

| scope | (p₁,p₂) pairs | window survivors | Fermat survivors | solutions | wall |
|---|---|---|---|---|---|
| n ≤ 10³⁰ | 230,612,582,193 | 1,904 | 1 | 0 | 87 min |
| p₁ ≤ 500,000, any n | 86,517,004,140 | 1,185 | 1 | 0 | 146 min |

The one Fermat survivor is the Carmichael number 26921089 = 13·37·97·577 (37+1 ∤ n+1). Logs: `clc/k4/k4_*.jsonl` (one line per block).

## 5. Heuristics and what remains

Conditioning on (a), each condition n/p ≡ 1 (mod L_p/12) has "probability" 24/p². Summing ∏ 24/pᵢ² over p₁<p₂<q<r ≡ 1 (mod 12) with
p₂² ≤ 24p₁³+1 and q, r ∈ (p₂, 2P) gives an expected count ≈ 6.3×10⁻⁷ (`python3 -m agrawal.k4_heuristic`), about 96% of it from
p₁ = 13 (where n < 1.1×10¹¹, long excluded). The mass left after Theorem B (p₁ > 5×10⁵) decays like X⁻⁴ and is of order 10⁻²⁵.

A proof that k = 4 is impossible would need a bound on p₁ itself. Theorem A reduces the problem to one free parameter
(given p₁ everything is bounded polynomially), and the identity d·e·s·Π = 8p₁³ with p₁ ∤ des shows the integer
δ = des − 8p₁³ ≥ 1 equals 8p₁³(1/Π − 1), which pins the sizes of q, r, p₂ relative to p₁ but does not by itself exclude them.
Natural next steps: analyse δ for small values; a 128-bit version of the enumerator would reach B = 10³² or p₁ ≤ 10⁶ in about
half a day each.
