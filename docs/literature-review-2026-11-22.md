# Williams numbers: literature and OEIS review, 22 November 2026

Scope: every result, computation, list or web resource found that bounds, constructs or excludes Williams numbers
(squarefree composite n with (p−1) | (n−1) and (p+1) | (n+1) for all primes p | n; equivalently n ≡ p (mod (p²−1)/2)),
or any class containing them, and every statement of novelty or prior work in `paper/clc.tex` (v1.2).

Method: four independent searches (OEIS sweep with ~120 full-text queries and term-by-term tests of every relevant
b-file; literature under all names on arXiv, zbMATH, OpenAlex/Semantic Scholar citations, MathOverflow/Math.SE, GitHub,
Zenodo, HAL, web; a full read of J. C. Puddefoot's census repositories; an adversarial audit of the manuscript against
primary sources). The quotes marked ✔ below were then re-read by the author's assistant in the primary source.
This supersedes the frontier statements in `docs/literature-williams-numbers.md`.

## 1. Best known bounds (state on 22 Nov 2026)

| statement | bound | source | status |
|---|---|---|---|
| no Williams number, any number of prime factors | **10³⁰** | follows from Puddefoot's census of the Chebyshev–Carmichael numbers (OEIS A299799), a class containing every Williams number; none of its 196 terms is one (checked by us: 190 terms have no prime with (p+1) \| (n+1), 6 have exactly one) | inference; the census is unrefereed, single-author, AI-assisted, not replicated; nobody had stated the consequence |
| same, by a different method | 10²⁴ | our factor-and-test scan of the Shallue–Webster tabulation | ours; reproduces A299799 below 10²⁴ (14 terms), A335336 and A329948 below 10²² |
| same, explicitly stated in print by others | 10¹⁶ | Leng 2017 (MIT PRIMES report; all k) ✔; Pinch 2007 (odd k) ✔ | |
| implied by OEIS tabulations | 10²² (A329948, A335336, Eldar 2024, from Goutier's table); 10²¹ (A175530, Alekseyev 2020); 10¹⁸ (Lucas–Carmichael list, Suteu, 19 Nov 2026) | OEIS | |
| subclass: all p ≡ 3 (mod 4) | 10¹⁸ | Grau, Oller-Marcén, Rodríguez, Sadornil 2015 (arXiv:1401.4708, Prop. 15) ✔ | superseded |
| four prime factors, n | N > 10²⁴ (McIntosh–Dipra 2015) ✔; n > 10³⁰ (inference from the census); **n > 10³²** (ours) | | only 10³⁰ < n ≤ 10³² rests on our paper alone |
| four prime factors, smallest prime | p₁ > 2×10⁴ (McIntosh–Dipra) ✔; **p₁ > 10⁶** (ours, n unbounded) | | no competing statement found anywhere |

No class containing all Williams numbers was found with a completeness bound beyond 10³⁰, and no four-prime
statement comparable to ours.

## 2. The census that supersedes the general 10²⁴ bound

- J. C. (John) Puddefoot, GitHub `pudepiedj/cheb-cn2-census` (A299799 complete below 10²⁸, 87 terms; b-file published
  20 Oct 2026) and `pudepiedj/cheb-cn2-census-2` (complete below 10³⁰, 196 terms; single commit `657f647`, 8 Nov 2026;
  430 h on 30 threads). Also order-2 Carmichael censuses (A175531: 10²⁵ on 24 Sep, 10²⁸ on 13 Oct, 10³⁰ on 8 Nov) and two
  repositories of non-rigid order-2 numbers by Howe's construction (12 and 20 Nov 2026).
- Class searched: squarefree n with n ≡ 1 or p (mod (p²−1)/2) at every prime, each prime choosing independently; no
  restriction on sign pattern, number of factors or smallest prime. The all-"p" pattern is the Williams case. A reading
  of the proofs and the C code found no gap specific to that pattern.
- What to hedge: unrefereed; proofs and code AI-written ("author: Claude Opus 5.5 and JCP"); the only "independent
  review" is another AI model; no second implementation; the raw survivor file of the main (capped) part is unpublished
  and was not replayed at 10³⁰; the type-"p" code path has thin independent validation (the first term with a type-p
  prime is at 2.3×10²⁶, above every Carmichael tabulation).
- His repositories never mention Williams, Lucas–Carmichael or Baillie–PSW. He is currently constructing order-2
  numbers with more and more type-p primes (up to four, in a 2,712-digit number); an order-2 number with every prime
  of type p would be a Williams number.
- Our scan is the first external check of his list (14 terms below 10²⁴, identical), by a route independent of his.
- Timeline: his 10²⁸ census predates our 10²⁴ scan (20–21 Oct) and v1.0 of our paper (2 Nov).

## 3. Literature missing from the paper (all verified in the source unless noted)

1. **Puddefoot's censuses; OEIS A299799, A175531** — see §2. Must be cited; changes the title and abstract.
2. **OEIS A079543** (Reble 2003) and **A304291** (Lava 2018): the Williams condition without the squarefree
   requirement; Williams numbers are exactly their squarefree terms; none of the 1,384 known terms is squarefree.
3. **C. Ballot, "On absolute Lucas pseudoprimes", Integers 26 (2026) #A102** ✔ (24 Aug 2026). Restates Williams's
   question (odd number of factors), generalises his three-factor theorem (Thms 12–13), builds Chernick-type universal
   forms for absolute Lucas pseudoprimes (bears on our Appendix A). Says the question is Problem 5, p. 271, of
   Ballot–Williams, *The Lucas Sequences* (Springer 2023) — book not read.
4. **Strong Fibonacci pseudoprimes** (Lidl–Müller–Oswald 1990; Müller–Oswald; first examples Guillaume–Morain 1992/96),
   via Pinch 2007 ✔: Type II (odd number of primes, all ≡ 3 mod 4, p²−1 | N−p) is a subclass of Williams numbers — exactly
   the "order-2 type" of our Howe remark; Pinch found none below 10¹⁶ and noted the link to Williams's question. In
   Pinch's form (Carmichael with 2(p+1) | N−1 or N−p) every four-prime Williams number is a strong Fibonacci
   pseudoprime (our inference: all p ≡ 1 mod 12). Originals not read; cite through Pinch unless obtained.
5. **A. Leng, MIT PRIMES 2017** ✔: no Carmichael ∩ Lucas–Carmichael number below 10¹⁶ (all k); re-proves k ≠ 3 and
   the mod-12 lemma. Unrefereed.
6. **Grau, Oller-Marcén, Rodríguez, Sadornil, Czechoslovak Math. J. 65 (2015)** ✔: Williams numbers with all
   p ≡ 3 (mod 4) excluded below 10¹⁸ (as Carmichael ∩ Gaussian-Carmichael numbers ≡ 3 mod 4).
7. **Helmreich–Webster, Integers 24A (2024) #A8** (tabulating absolute Lucas pseudoprimes to 2⁶⁴; same CD-window
   device) and **Pinch, Math. Comp. 61 (1993)** — for the algorithm's ancestry (§4, item 5).
8. **Suteu's Lucas–Carmichael list to 10¹⁸** (linked from A006972 since 19–21 Nov 2026): our converse check is stated
   only to 10¹⁵. All 1,792,712 terms were tested by a review agent: none is Carmichael.
9. **Tamilvanan–Muthukrishnan, arXiv:2311.08012** (one-sided Lucas–Carmichael form (6m−1)(12m−1)(18m−1)) for Appendix A.
10. OEIS A335336 and A329948 as entries (near-miss sequences; both stop at 10²²; our census extends both to 10²⁴).

## 4. Faults in the manuscript (v1.2) to fix before submission

1. **Title, abstract, Table 1 last row, Theorem 5.1 framing, "We know of no larger published bound…"** — superseded
   (the sentence is false). Reframe: 10²⁴ as an independent verification; 10³⁰ as a corollary conditional on the census.
2. **"our per-ω tallies agree with independently published counts … eleven-prime ones (OEIS A299711)"** — false:
   A299711's a(24) was taken from Shallue–Webster ✔, the source of our input. Only Chick's three-prime count is
   independent. Table 3 reproduces Tables 3–4 of arXiv:2506.09903 and should say so.
3. **Howe remark, "we have not pursued this"** — superseded: every order-2 Carmichael number below 10³⁰ is rigid
   (A175531), so none is a Williams number; and the type has a 1990 name (item 3.4).
4. **McIntosh–Dipra's searches described incompletely** ✔: they ran three (quotient loop → p₁ > 2×10⁴; the (f_s, s) loop
   with Fermat prefilter → N > 10²⁴; Pinch-style for 4 ≤ d ≤ 13 with X between 10²⁰ and 10³⁵, two (d, X) pairs stated:
   d = 6 at 10²⁰, d = 11 at 10³⁰). "At unstated bounds" should be made exact.
5. **"the new contributions are the enumeration algorithm…"** — overstated: completion of a preproduct by a cofactor in
   one residue class mod λ(P), and the Beeger–Duparc–Pinch bound on the product CD, are standard in Carmichael
   tabulation and described in Shallue–Webster arXiv:2506.09903 §2 and Thm 8 ✔. New: the adaptation to (p²−1)/2 with a
   two-prime cofactor, the completeness proof, the certified runs.
6. **"with a slight sharpening" (abstract), "slightly sharper bound on p₂" (remark)** — overstated: McIntosh–Dipra's
   inequality unrounded, plus a congruence step.
7. **Introduction: "Lucas–Carmichael numbers play the same role for Lucas sequences…"** — true only for an odd number
   of prime factors; a four-prime Williams number is not an absolute Lucas pseudoprime and has no Baillie–PSW
   relevance (McIntosh–Dipra say so). State that the four-prime case is of arithmetic interest in Echi's sense.
8. **Four-prime theorem**: add that n < 10³⁰ also follows from the census; new are 10³⁰ < n ≤ 10³² and p₁ ≤ 10⁶.
9. **Theorem 5.1**: credit "179 below 10²²" to OEIS A329948 inside the statement.
10. **Chen–Greene** described as using only "weaker order conditions" — they considered both kinds of prime set.
11. **Echi "dropped the parity restriction"** — check against Echi's paper (not accessed); Zhang supports it,
    McIntosh–Dipra describe Echi differently.
12. **Acknowledgement "settles the theory of the four-prime case"** — existence is open; say "establishes the
    finiteness bounds".
13. **Appendix A**: position against Ballot 2026, Helmreich–Webster and Tamilvanan–Muthukrishnan; Theorem A.1 (m = 3)
    is the polynomial shadow of Williams's and Ballot's three-factor theorem.
14. **Author name**: the JNT byline is "Richard J. McIntosh, Mitra Dipra" (running head "M. Dipra") ✔, but McIntosh's
    own 2014 paper cites it as "R.J. McIntosh and D. Mitra" ✔. Keep the byline form; ask McIntosh if in contact.
15. `docs/literature-williams-numbers.md` l.35: McIntosh 2014's searches for 5 ≤ d ≤ 12 were "for various values of X
    between 10¹⁶ and 10²⁴" ✔, not complete to 10²⁴.

## 5. What survives as new

- No four-prime Williams number with smallest prime ≤ 10⁶ (n unbounded). No competing source.
- No four-prime Williams number with 10³⁰ < n ≤ 10³². Would be absorbed by a census extension past 10³².
- The near-miss census of all Carmichael numbers below 10²⁴ (prime-by-prime classification; 14 four-match numbers,
  840 with ≥ 3, 14,062 with the largest prime matching, none with ω ≤ 4); extends A329948 and A335336 from 10²² to 10²⁴.
  Anyone can redo it from the public list.
- The first independent check of the A299799 census (below 10²⁴), and the observation that it bounds Williams numbers.
- Appendix A (no two-sided linear-factor universal form in three strata): no prior statement found; elementary.

## 6. Coverage and limits

Not accessible: Echi 2007; Lidl–Müller–Oswald and Müller–Oswald originals; Ballot–Williams 2023; Bouallègue–Echi–Pinch
2010 and Al-Rasasi–Ghanmi 2013 beyond abstracts; Pinch 1993; Phatak 2020; Google Scholar, MathSciNet, the NMBRTHRY list,
mersenneforum's internal search, GitHub code search. OEIS drafts are invisible until approved. A result posted only in
those places would have been missed. Puddefoot's census completeness was read, not re-run.
