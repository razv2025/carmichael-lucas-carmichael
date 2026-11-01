# Literature check: Carmichael ∩ Lucas–Carmichael numbers are "Williams numbers" (1-Williams numbers)

*2026-11-01. Prompted by an external review; carried out by an AI research agent from primary sources where accessible
(full texts of Williams 1977, McIntosh 2014, Echi 2007, Pinch's preprint, Phatak 2020, BFW 2021, Chen–Greene 2003,
Pomerance 1984; abstract/metadata level only for McIntosh–Dipra 2015, Zhang 2015, Al-Rasasi–Ghanmi 2013 and
Bouallègue–Echi–Pinch 2010, whose PDFs sit behind bot walls although they are free). Copies in the job scratch directory
`lit/`. This is an AI-agent report, not a human literature review.*

## Two papers the author must download and read by hand (both free)
- **McIntosh & Dipra, "Carmichael numbers with p+1 | n+1", J. Number Theory 147 (2015) 81–91** —
  `https://www.sciencedirect.com/science/article/pii/S0022314X14002108/pdf` (JNT open archive).
  Check: the exact inequalities and constants for d = 4 (compare with p₂² ≤ 24p₁³+1, p₃ < 2p₁p₂, p₄ < √(2p₁p₂p₃)); whether a
  complete search for Williams numbers with all d is reported beyond 10¹⁶; the exact four-prime statement (p₁ > 2×10⁴, N > 10²⁴).
- **Zhang, "Estimating the counts of Carmichael and Williams numbers with small multiple seeds", Math. Comp. 84 (2015) 309–337** —
  `https://www.ams.org/mcom/2015-84-291/S0025-5718-2014-02837-8/S0025-5718-2014-02837-8.pdf`.
  Check §7 ("what a Williams number looks like") against our heuristic (hundreds of digits, ~80–110 primes) and Conjecture 2
  against our margin measurements.

## What is established in print (chronological)
| source | content relevant to us |
|---|---|
| Williams 1977 (CMB 20, 133–143; full text) | Poses the question; proves k ≠ 3, 3 ∤ n, and k odd ≥ 5 in his Lucas-sequence formulation. Our Proposition 2.3 is his argument. |
| Pinch 2006/07 preprint "Absolute quadratic pseudoprimes" (full text) | "Williams asked whether there are any Carmichael numbers N with an odd number of prime divisors and … p+1 | N+1. There are no such Carmichael numbers up to 10¹⁶." Parity-restricted. Already tabulates the criterion (p²−1)/2 | N+1. |
| Echi 2007 (CRMR Canada 29, 41–47; full text) | Defines a-Korselt and **a-Williams numbers**; our objects are the 1-Williams numbers; drops the parity restriction; restates Williams's k odd ≥ 5; constructs (3p)-Williams numbers p(3p−2)(3p+2). |
| Bouallègue–Echi–Pinch 2010 (IJNT 6, 257–269; review only) | Korselt numbers and sets; conjectures; "whether a 1-Williams number exists remains open". |
| Al-Rasasi–Ghanmi 2013 (Missouri J. Math. Sci. 25, 134–152; abstract/review) | For every a, finitely many a-Williams numbers with three prime factors (weaker than Williams's k ≠ 3 for a = 1). |
| McIntosh 2014 (Integers 14, #A59; full text) | Parallel problem (p±1) | (n−1) ("super-Carmichael"): no 3-prime example; **finiteness with d−3 primes fixed via the product of three quotients t_q t_r t_s squeezed around 8P³ with P ∤ t_q t_r t_s** (q < 20P^{5/2}, r, s < 2Pq); 4-prime: p₁ > 4000, N > 10²⁴; complete searches to 10²⁴ for 5 ≤ d ≤ 12. §4 "Williams numbers": the Baillie–PSW motivation, Echi's name, gcd(pᵢ−1, pⱼ+1) = 2 compatibility, "a study of Williams numbers was undertaken by McIntosh and Mitra [= Dipra]". |
| **McIntosh–Dipra 2015 (JNT 147, 81–91; abstract level)** | Williams numbers (= our objects). **Finitely many with a given set of d−3 prime factors. Search methods. Four prime factors: p₁ > 2×10⁴ and N > 10²⁴.** Records four-prime base-2 pseudoprime near-misses (OEIS A335336). Cites Baillie–Wagstaff, Chen–Greene, Grantham, Pomerance 1984, Williams 1977, Pinch, Echi. |
| Zhang 2015 (Math. Comp. 84, 309–337; abstract + author's expanded abstract) | Williams numbers = Carmichael with p+1 | n+1 (after Echi's relaxation). Formalises the two-sided side-assignment of the modulus's primes; Conjecture 2: log₂log₂ |W(L)| = s^{1/2−o(1)}; a set of 1,029 primes with ≥ 2²⁴ expected Williams numbers, none found; $500 prize. No nonexistence bound. |
| Phatak 2020 (viXra 2007.0102; unrefereed) | Claims no subset of Grantham's 2,030-prime set is a Williams number (exhaustive over 160,681,183 candidate subsets); derivations not rigorous. |
| Ballot–Williams 2023 (Springer, *The Lucas Sequences*, ch. 4) | Reference list links Williams 1977, Pinch and McIntosh–Dipra. |
| OEIS | A329948 (Suteu 2019; b-file Eldar): Carmichael numbers with ≥ 3 primes p+1 | m+1, 179 terms below 10²² — agrees with our count. A335336 (Suteu 2020): Carmichael k with gpf(k)+1 | k+1; comment on McIntosh–Dipra's four-prime pseudoprimes. No OEIS entry is named "Williams numbers" in this sense. |
| Cross-citations | Williams-number papers cite Pomerance 1984, Chen–Greene, Grantham, Baillie–Wagstaff; BFW 2021 lists Williams 1977; Pomerance 1984 and Chen–Greene 2003 do not cite Williams; the Lenstra–Pomerance/Agrawal side and Howe appear unconnected (not fully checked). |

## Consequences for the manuscript (applied 2026-11-01)
- **Removed as false:** "no further theorem since 1977", "only published bound is Pinch's 10¹⁶", "first open case untouched", "these literatures do not cite one another and use no common name". The paper now uses the name *Williams number* and cites Echi, BEP, Al-Rasasi–Ghanmi, McIntosh, McIntosh–Dipra, Zhang, Phatak.
- **Reattributed:** the finiteness-for-fixed-p₁ corollary and the product-of-quotients mechanism are McIntosh's (2014) and McIntosh–Dipra's (2015). Theorem A is presented as the explicit form (exponent 3/2 and constants) — *"sharper" is provisional until McIntosh–Dipra's own inequalities have been read.*
- **Reframed as an improvement:** Theorem B extends McIntosh–Dipra's (p₁ > 2×10⁴, N > 10²⁴) to (p₁ > 500,000, n > 10³⁰) by a different algorithm (CRT class + window filter vs. their t_s/s loop).
- **Kept with a caveat:** the all-k bound 10²⁴ (Theorem 3.1) is the largest we found in print; to be checked against McIntosh–Dipra's search section.
- **Contextualised:** the subset-product margins are compared with Zhang's Conjecture 2; the Baillie–PSW identification is cited to McIntosh 2014 / McIntosh–Dipra / Zhang rather than presented as new; the Chen–Greene/Grantham paragraph mentions Phatak's unrefereed negative result.
- **Still believed new (no prior source found):** Lemma 2.2(c) (k even ⇒ all p ≡ 1 mod 12), the explicit constants of Theorem A, the 10³⁰ / 500,000 enumeration and its algorithm, the polynomial-family theorems (Appendix A), the 10²⁴ all-k verification and its near-miss statistics.
