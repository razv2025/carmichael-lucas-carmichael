# Publication plan: what, where, how — and why not, and how we answer that

*Prepared 2026-10-29 for Raz Vakil's consultation. Companion to `paper/clc.tex`.*

## 1. What we have (and what each item is worth)

| # | result | type | novelty / value |
|---|---|---|---|
| 1 | No CLC number below 10²⁴ (independent factor-and-test over the complete Carmichael tabulations; completeness and per-class cross-checks; near-miss statistics: max 4 of 9 matching primes, 826 with three) | verified computation | First printed bound since Pinch's 10¹⁶ (2007); 10⁸× extension. Low mathematical depth, high reliability, useful to three communities (Williams/Lucas–Carmichael, Baillie–PSW, Agrawal). |
| 2 | Theorem A: a 4-prime CLC number has all pᵢ ≡ 1 (mod 12), p₃ < 2p₁p₂, p₄ < √(2p₁p₂p₃), **p₂² ≤ 24p₁³ + 1**, n < 477p₁^{15/2} | theorem (elementary, 1 page) | **The only new theorem on Williams's question since 1977.** Makes the 4-prime case finite per smallest prime. This is what makes the note a paper rather than a data report. |
| 3 | Theorem B: no 4-prime CLC with n ≤ 10³⁰; none at all with p₁ ≤ 500,000 | verified computation (validated algorithm) | Settles the first open case far beyond the general bound; the p₁-bounded statement holds for all n. |
| 4 | Polynomial-family impossibility theorems (m = 3; uniform offsets ±1; generic position) + exhaustive degenerate strata | theorems (elementary) + computation | Modest but clean; show the Chernick paradigm cannot be made two-sided in its simple forms. Theorem for m=3 is weaker than Williams's absolute result and must be presented as its parametric analogue (the paper does). |
| 5 | Subset-product margin wall (≈ −30, flat in y) | measurement | Explains quantitatively why the Baillie–PSW community calls the route intractable. Not a theorem; present as such. |
| 6 | Heuristics: k=4 expected count ≈ 10⁻⁶; onset of CLC numbers ~10²⁰⁸–10⁴⁹⁰ with ~100 primes | heuristic | Context; must be hedged. The k=4 heuristic is simple and credible; the onset model has wide error bars. |
| 7 | Cross-literature synthesis (Williams ↔ Baillie–PSW ↔ Lenstra–Pomerance/Agrawal ↔ Howe) | exposition | Real service value: these literatures do not cite each other. |

**Recommended headline:** Theorem A + Theorem B, with the 10²⁴ bound as the second result and the obstructions/heuristics as supporting material. Title as in the draft.

## 2. Where

Ordered by recommendation:

1. **arXiv, math.NT** (cross-list cs.SC or math.NA is not needed). Immediate, establishes priority, citable. Do this first, after the consultants' pass and the checklist in §4. Endorsement may be required for a first-time submitter in math.NT; a consultant can endorse.
2. **OEIS**: comments on A006972 (Lucas–Carmichael numbers) and A002997 (Carmichael numbers): "No number below 10^24 is both a Carmichael and a Lucas–Carmichael number (R. Vakil, 2026); a four-prime example would have p_2^2 <= 24 p_1^3 + 1 and none exists with n <= 10^30 or p_1 <= 500000." Reference the arXiv number. Also a comment on A329948 (the near-miss sequence) noting the first number with four matching primes, 15500309690554865758009, and the count 826 below 10²⁴ — these extend Eldar's data and may warrant a new sequence (numbers with ≥ 4 matching primes). OEIS editors will ask for the method; point to the repository.
3. **Journal.** Realistic targets for a short computational/elementary number theory paper:
   - *Integers* (electronic, free, friendly to elementary and computational results; moderate turnaround).
   - *Journal of Integer Sequences* (free, fits the OEIS connection and the tabulation flavour).
   - *Mathematics of Computation* (higher bar; the 10²⁴ verification plus Theorem A/B might fit as a short paper, but expect the referee to ask for more theory or a larger computation).
   - *Experimental Mathematics* (fits the heuristics + computation mix).
   - *Canadian Mathematical Bulletin* (where Williams's question appeared; a note answering part of a CMB question is natural there).
   Recommendation: arXiv now; then Integers or JIS, unless a consultant pushes for CMB or Math. Comp.
4. **Code and data DOI**: Zenodo deposit of the tagged repository (and of the result/log files) so the paper can cite a DOI; the 12.3 GB input is not ours to redistribute — cite Stamm-Wilbrandt's URL and give the SHA-256 (`clc/DATA_SHA256.txt`).
5. **Announce** to the people whose work we build on and who will care: Shallue & Webster (their list), Goutier, Stamm-Wilbrandt, Eldar (A329948), Baillie/Fiori/Wagstaff (BPSW), Howe, Pinch, and Williams if reachable. A short, specific email with the arXiv link. This is also the fastest way to learn of anything we missed.

## 3. How (process)

1. Consultants read `paper/clc.pdf` with the two questions: is anything wrong, and is anything already known. Give them `docs/review-*.md` (the independent review reports) so they see what has already been checked.
2. Resolve every TODO in the .tex (affiliation, email, repository URL, AI statement wording, two bibliography checks).
3. Run `./run_tests.sh` on a clean clone; make sure the `make test` self-tests and the pytest identity checks pass from scratch.
4. Tag the repository (`v1.0`), deposit on Zenodo, put the DOI in the paper.
5. Submit to arXiv; post OEIS comments the same day, citing the arXiv number.
6. After two weeks of feedback, submit to the chosen journal.

## 4. Concerns, and how we mitigate them

| concern | why it matters | mitigation (done / to do) |
|---|---|---|
| **Correctness of the proofs.** Theorem A is new and the whole k=4 story rests on it. | A wrong inequality or missed case would be embarrassing and would invalidate Theorem B's second half. **This already happened once: the first draft's Π > 1 case used a false numerical estimate (3.0001 instead of 3.0022); the independent fact-check caught it and the case now has a clean proof (only the d-factor of Π can exceed 1). The enumeration had used the weaker bound, so Theorem B was never at risk.** | Done: proof re-derived twice independently in-session; algebraic identity d·e·s·Π = 8p₁³ verified exactly on 2000 random integer tuples and on the relaxed solution 13685 (tests/test_theorems.py); every inequality step has an executable check; an independent adversarial referee agent re-derived each proof from the LaTeX alone (report in docs/). To do: at least one human number theorist reads §3 line by line. |
| **Correctness of the code.** A complete-enumeration claim is only as good as its completeness. | A dropped candidate class = a false theorem. | Done: self-tests brute-force the sub-problems; the enumerator was validated on a relaxed instance with known solutions against an independent brute force; two different candidate walks agree on 6 instances (one with 11 million survivors); the real run reproduces the independent 10²⁴ result; all survivors re-verified in Python; per-block logs allow auditing coverage. The design error found by the tests (true j not floor/ceil) is disclosed in the paper. To do: a second person compiles and runs `make test` on another machine. |
| **Correctness of the 10²⁴ scan.** We rely on other people's tabulations. | If a list is incomplete, our bound is wrong. | Done: three completeness checks (counts at 10²²/10²³/10²⁴ against Shallue–Webster, monotonicity, initial segment), per-ω cross-checks against two independently computed OEIS sequences, 179-count against A329948, converse check against Suteu's Lucas–Carmichael table; SHA-256 of inputs recorded. The paper states the dependence explicitly. |
| **"It's just a bigger number."** Referees may see a negative computational result as incremental. | Rejection on significance. | Theorem A is a genuine theorem; the paper leads with it. The cross-literature synthesis is a second contribution. Choose venues (Integers/JIS) where such papers are welcome. |
| **Priority / already known.** Someone may have proved Theorem A or run the k=4 case before. | Embarrassment; wasted effort. In this project we were scooped once before (the LPS k=7 case) because "published bound" ≠ "frontier". | Done: literature search found no theorem on k=4 since Williams 1977 and no bound beyond Pinch's 10¹⁶; Pinch's and Goutier's own data flags imply the 10²² emptiness but it was never stated in print. To do: before submission, (i) search again (MathSciNet/zbMATH for "Lucas–Carmichael", "Williams numbers", citations of Williams 1977 and Howe 2000; arXiv full-text), (ii) ask the consultants, (iii) email Howe/Pinch/Shallue–Webster with the preprint. Also verify the Puddefoot/order-2 census claim from our notes before using it anywhere (the paper deliberately omits it). |
| **AI assistance.** Code, proofs and text were drafted with an AI system. | Journals and arXiv increasingly require disclosure; undisclosed use is an ethics problem; disclosed use may bias referees. | Disclose plainly in the acknowledgements (template in the .tex). The author must actually check every proof by hand before signing that sentence; the test suite and independent reviews make the computations verifiable regardless of who wrote them. Check the target journal's AI policy (Integers, JIS and AMS journals permit disclosed assistance; none permits an AI author). |
| **Outsider author / no affiliation.** | Some editors weight credentials. | Preprint quality, complete reproducibility, a consultant's endorsement for arXiv, and (if a consultant contributes materially) co-authorship. |
| **Overclaiming.** Phrases like "settled", "proved impossible". | Credibility. | The paper distinguishes theorem / verified computation / measurement / heuristic in every section; the k=4 case is "open; empty below 10³⁰ and for p₁ ≤ 500,000", not "settled". Keep that discipline in talks and the OEIS comments. |
| **The heuristic onset estimates (10²⁰⁸–10⁴⁹⁰).** Wide ranges, calibration choices. | A referee may call them unfounded. | Presented as heuristic with stated calibration and error band; not used anywhere else in the paper. Could be moved to an appendix or cut if a referee objects. |
| **Family theorems are weaker than they sound.** Only polynomial-identity families are excluded. | A referee will note the gap. | Stated as a Remark in §5, and Theorem 5.1 is explicitly called the parametric shadow of Williams's theorem. |
| **Data redistribution.** The 12.3 GB list is Shallue–Webster's/Stamm-Wilbrandt's. | Licensing. | We redistribute nothing; we cite and checksum. Acknowledge all providers (done). |
| **Reproducibility over time.** URLs rot. | Future readers cannot re-check. | Zenodo DOI for code + our result/log files; record the input checksums; the k=4 computation needs no external data at all. |
| **Earlier mistakes in this project** (unverified "none below 10¹⁸" draft claim; the LPS "record" that wasn't). | Pattern risk: confident claims later retracted. | Both were caught internally and corrected before any external statement; the process now requires an independent route for every claim (this document, the tests, the two review reports). Nothing in the paper rests on an unverified claim. |

## 5. Pre-submission checklist

- [ ] *Optional but recommended:* rerun the 10²⁴ scan with the current `scan_carmichael_list_for_clc.py` (now prints the full (matches, ω) histogram, ~21 h on 12 cores) to record how many numbers have four matching primes; the paper currently says only "first attained at …".

- [ ] Consultant A (number theorist) has read §§2–3 and signed off on the proofs (both independent reviews are in `docs/review-math-2026-10-29.md` and `docs/review-facts-2026-10-29.md`).
- [ ] Howe's order-2 criterion quoted in §1 and §4 checked against Howe, Math. Comp. 69 (2000), Theorem 1.
- [ ] Dump rerun finished (`clc/k4/RESULT_dump_reverify.txt` ends with DONE, all W lines 'not CLC'); then replace the TODO in §3 of the paper by "all 1,904 + 1,185 window survivors were re-verified in Python" and commit the dump logs.
- [ ] Consultant B has run `./run_tests.sh` from a clean clone on another machine.
- [ ] Literature re-check done (MathSciNet/zbMATH/arXiv) and the Puddefoot claim verified or dropped.
- [ ] All TODOs in `paper/clc.tex` resolved; bibliography entries for Shallue–Webster, Pinch 2007 and Gilchrist verified.
- [ ] Repository tagged; Zenodo DOI obtained and cited.
- [ ] AI-assistance statement confirmed by the author.
- [ ] arXiv submission; OEIS comments drafted (§2 item 2) and submitted.
- [ ] Emails to data providers and the three communities.
