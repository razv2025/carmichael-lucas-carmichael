# Literature check: Carmichael ∩ Lucas–Carmichael numbers are "Williams numbers" (1-Williams numbers)

*2026-11-01. Prompted by an external review; carried out by an AI research agent from primary sources where accessible
(full texts of Williams 1977, McIntosh 2014, Echi 2007, Pinch's preprint, Phatak 2020, BFW 2021, Chen–Greene 2003,
Pomerance 1984; abstract/metadata level only for McIntosh–Dipra 2015, Zhang 2015, Al-Rasasi–Ghanmi 2013 and
Bouallègue–Echi–Pinch 2010, whose PDFs sit behind bot walls although they are free). Copies in the job scratch directory
`lit/`. This is an AI-agent report, not a human literature review.*

## Full-text reading of McIntosh–Dipra and Zhang (2026-11-01, PDFs in `docs/sources/`, not redistributed)

**McIntosh–Dipra (JNT 147, 2015), read in full.** Their §2 contains our Lemma 2.1 ((p²−1)/2 | N/p − 1), the observation that all pᵢ are congruent mod 12 and ≡ 1 if d is even (our Lemma 2.2(c)), the quotients f_q, f_r, f_s (our s, e, d) with f_s < 2P (our d < 2p₁), and Theorem 1 (no three-prime Williams number) by the argument we use. Theorem 2 proves finiteness with d−3 primes fixed via 8P³ < f_q f_r f_s < 8P³(1+1/(q²−1))³, the lower bound **proved** by Newton's inequality (so Π < 1 always — our Π > 1 case is vacuous), giving q < 5P^{3/2}, r < 2Pq, s < √(2Pqr). Theorem 3 sharpens to q < 5P^{3/2}, **r < Pq**, s < √(2Pqr) < 5√2 P^{5/2}. For d = 4 (P = p₁) this is our Theorem A with p₂ < 5p₁^{3/2} (ours: 4.9p₁^{3/2}) and p₃ < p₁p₂ (ours, weaker: 2p₁p₂). §3 derives an 8th-degree polynomial for q²; §4 describes two searches: the (f_s, f_r, f_q)-loop search giving p₁ > 2×10⁴ for four primes, and a Pinch-style complete search over compatible prime sets for 4 ≤ d ≤ 13 'for various values of X between 10²⁰ and 10³⁵' (bounds per d not stated; nine near-misses found). A separate four-prime search (loop over f_s and s, Fermat prefilter) gives Observation 2: no Carmichael N < 10²⁴ with four prime factors and (s+1) | (N+1) for the largest prime s; they list four-prime base-2 pseudoprimes with s±1 | N±1 (OEIS A335336). They also treat non-squarefree N < 10¹⁰ (five examples) and sC numbers.

**Zhang (Math. Comp. 84, 2015), abstract, §§1–2 and §7 read.** Conjecture 4: log₂|W(L)| = 2^{s^{1/2−o(1)}} for EDON conductors with ω(L) = s (vs. 2^{s(1+o(1))} for Carmichael numbers); the modulus is split as L = L⁽¹⁾L⁽²⁾/2 with gcd 2 (the side assignment); Q(L₁₁₉) has 1,029 primes with ≥ 2²⁴ expected Williams numbers; Remark 7.4 predicts such a Williams number has about 428 prime factors; Remark 7.5 relates Chen–Greene's sets ('Williams conductors' of > 1,600 primes).

**Net effect:** Theorem A is McIntosh–Dipra's Theorems 2–3 for d = 4 (our proof is independent and our constants marginally differ; theirs on p₃ is better). Genuinely ours: the (p₁,p₂)-pair algorithm (CRT class + window filter + certified completeness) and the extension of the four-prime exclusion to n ≤ 10³⁰ and p₁ ≤ 500,000; the clean all-k bound 10²⁴ with cross-checks and near-miss statistics (their all-d search has unstated per-d bounds); the appendix theorems and measurements.

## (Superseded) the two papers, as first located
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
- **Reattributed (final, after full-text reading):** Theorem A = McIntosh–Dipra Theorems 2–3 (d = 4), restated with an independent proof; the word 'sharper' has been removed. Lemma 2.2(c) and the k = 3 proof are theirs too.
- **Reframed as an improvement:** Theorem B extends McIntosh–Dipra's (p₁ > 2×10⁴, N > 10²⁴) to (p₁ > 500,000, n > 10³⁰) by a different algorithm (CRT class + window filter vs. their t_s/s loop).
- **Kept with a caveat:** the all-k bound 10²⁴ (Theorem 3.1) is the largest we found in print; to be checked against McIntosh–Dipra's search section.
- **Contextualised:** the subset-product margins are compared with Zhang's Conjecture 2; the Baillie–PSW identification is cited to McIntosh 2014 / McIntosh–Dipra / Zhang rather than presented as new; the Chen–Greene/Grantham paragraph mentions Phatak's unrefereed negative result.
- **Still believed new (no prior source found):** the 10³⁰ / 500,000 enumeration and its algorithm with certified completeness, the clean 10²⁴ all-k verification with cross-checks and near-miss statistics, the polynomial-family theorems (Appendix A), the margin measurements.
