# Publication strategy and pre-submission risk register

*Version 2026-11-01 (first version 2026-10-29), for Raz Vakil. Companion to `paper/clc.tex`.*

**CLC number**: a squarefree composite n that is both Carmichael ((p−1) | (n−1) for every prime p | n) and
Lucas–Carmichael ((p+1) | (n+1) for every p | n). The same objects appear in the literature as **1-Williams numbers**
(see §5; the literature comparison is being completed and governs the final wording of every novelty claim).

## 1. What we have

| # | result | type | status |
|---|---|---|---|
| 1 | **Theorem A** (= McIntosh–Dipra 2015, Thms 2–3, d = 4; restated with an independent proof). All pᵢ ≡ 1 (mod 12), p₃ < 2p₁p₂, p₄ < √(2p₁p₂p₃), p₂² ≤ 24p₁³ + 1. | known theorem, our proof | **not new** (established 2026-11-01 from the full text); kept as a self-contained restatement |
| 2 | **Theorem B.** No four-prime Williams number with n ≤ 10³⁰; none with p₁ ≤ 500,000 (any n). Extends McIntosh–Dipra's p₁ > 2×10⁴, N > 10²⁴. | computation | **certified** 2026-11-01 (`clc/k4/CERTIFY_*.txt`): full coverage, all survivors re-tested in Python |
| 3 | No CLC number below 10²⁴ (factor-and-test of the complete Carmichael tabulations; completeness and per-class cross-checks; maximum of four matching primes). | computation on external data | done; a rescan recording the full match histogram is running (~21 h) |
| 4 | Synthesis of the Lucas–Carmichael / Baillie–PSW / Agrawal / Howe connections. | exposition | wording depends on §5 |
| 5 | Polynomial-family impossibility theorems; exhaustive strata; subset-product margin measurement. | theorems + measurement | moved to Appendix A |
| 6 | Heuristics (four-prime expected count ≈ 6×10⁻⁷; onset model). | speculative | labelled as such; onset model in Appendix B |

Recommended core (per the external review of 2026-11-01): lead with Theorem A, the certified enumeration (Theorem B) and
the 10²⁴ scan; keep items 5–6 as appendices. Working title: *Explicit bounds and exhaustive searches for four-prime
Williams numbers (Carmichael ∩ Lucas–Carmichael)*, to be fixed after §5.

## 2. Venues

The journals' AI policies decide eligibility; the assessments below are from the external review of 2026-11-01 and must be
rechecked against the live policy pages immediately before submission.

| venue | fit | eligibility / reservation | recommendation |
|---|---|---|---|
| arXiv (math.NT) | natural first step | permits disclosed AI assistance; a first-time submitter may need an endorsement | submit after Gates A–B |
| Canadian Mathematical Bulletin | good (Williams's question appeared there) | Cambridge requires declared AI use and full human accountability | **primary journal target**; ask the editor in advance about substantive AI involvement in proofs and code |
| Experimental Mathematics | good (computation + heuristics) | Taylor & Francis forbids generative-AI first drafts; detailed declaration required | possible only with a human-rewritten manuscript |
| Journal of Number Theory | stretch | plausible only if the inequality and the search advance are clearly substantial beyond McIntosh–Dipra (JNT 2015) | decide after §5 |
| Mathematics of Computation | aspirational | needs algorithmic or certification novelty; endorsement from a consultant would matter | decide after §5 |
| Journal of Integer Sequences | constrained | forbids LLM-written English; requires detailed credit for proof suggestions; discourages brute-force term extensions | only after a genuinely independent human rewrite |
| Integers | **ineligible** | its policy states it will not consider work using AI to produce mathematics, code or text | removed |

OEIS: concise comments on A006972 / A002997 (and the near-miss data on A329948) only after the preprint identifier exists;
OEIS is a record, not a priority mechanism. Code and owned data: Zenodo deposit with a versioned DOI; third-party inputs are
cited and checksummed (`clc/DATA_SHA256.txt`), not redistributed.

## 3. Dissemination order

1. Finish the certification (Gate A), the literature comparison (§5) and the human proof review.
2. Send consultants the manuscript first, with assigned questions (proof correctness; enumeration completeness; prior art; venue
   level). Share the AI audit reports afterwards, so they do not anchor the first reading.
3. Freeze a release candidate: tag, archive code, logs, hashes and result files under a versioned DOI.
4. Submit a policy-compliant, human-accountable preprint to arXiv.
5. Post the OEIS comments, citing the arXiv identifier.
6. Address substantive feedback; submit to the chosen journal when the completion gates below are met, not after a fixed
   elapsed time.

## 4. Authorship and AI disclosure

The AI system (Claude, Anthropic) was used for proof discovery and drafting, code generation, prose drafting, literature search,
and adversarial checking. The disclosure must name these roles separately (the current acknowledgement does). The author must
independently reconstruct and accept responsibility for every proof, computation, citation and sentence; the two AI audit
reports in `docs/` are adversarial checks, not independent human review, and are labelled accordingly. A consultant is offered
co-authorship only for a contribution meeting ordinary authorship standards.

## 5. Literature and novelty (final)

Full texts of McIntosh–Dipra (JNT 2015) and Zhang (Math. Comp. 2015) were read on 2026-11-01 (`docs/literature-williams-numbers.md`).
**Theorem A is not new**: it is McIntosh–Dipra's Theorems 2–3 for d = 4 (they even have the better p₃ < p₁p₂ and prove Π < 1
outright). Lemma 2.2(c) and the k = 3 proof are theirs as well. What the manuscript still contributes:

1. **Theorem B** — the four-prime exclusion extended from (p₁ > 2×10⁴, N > 10²⁴) to (p₁ > 500,000, n > 10³⁰), by a different
   and faster algorithm (CRT class for the cofactor + window filter), with a certified completeness record.
2. **The 10²⁴ all-k verification** with completeness/OEIS cross-checks and near-miss statistics (McIntosh–Dipra's all-d
   search states no per-d bound).
3. A self-contained exposition linking the Williams-number, Baillie–PSW, Agrawal and Howe literatures (with correct citations now).
4. Appendix material: polynomial-family theorems, two-sided subset-product measurements compared with Zhang's Conjecture 4.

**Assessment.** This is now a short computational note, not a theorem paper. Realistic outlets: arXiv (certainly worth posting
as a record of the computation and the algorithm); a computational journal only if the referee values the 10⁶× extension and
the certified method — Mathematics of Computation is unlikely, CMB possible but a stretch, JIS/Integers blocked by AI policy.
An alternative with real value at low cost: send the results to McIntosh (and Zhang), who will know whether a note is
warranted, and post the OEIS comments. **The author should decide whether to proceed to a journal at all**; the arXiv posting
and OEIS record are recommended regardless.

## 6. Risk register (neutral form)

| risk | mitigation in place | still to do |
|---|---|---|
| Proof correctness (Theorem A) | two reconstructions; executable checks of every identity (`tests/test_theorems.py`); two AI audits, one of which found and repaired a false estimate in the Π > 1 case | human number-theorist review of §3 |
| Enumeration completeness (Theorem B) | lemmas stated and proved; completeness proposition in §3; both candidate walks agree on six instances; relaxed-problem regression to 10¹² archived; per-block logs; **certified** by `certify_k4.py` (`CERTIFY_*.txt`) | — |
| Verifier soundness | verifier checks the original tuple without normalisation; negative tests; C Fermat routine cross-checked against Python | — |
| Dependence on external tabulations (10²⁴) | three completeness checks; per-ω cross-checks against two OEIS sequences; checksums | — |
| Prior art | literature note written; manuscript reframed | read McIntosh–Dipra and Zhang in full; resolve the two TODOs |
| AI policy compliance | roles disclosed; venue matrix | recheck policies at submission; human-authored prose where required |
| Process errors | the rerun's last blocks were lost to a `git stash -u` on live log files (2026-11-01) and recomputed; the wrapper now fails fast and certifies coverage | never run file-removing git commands while a job writes into the tree |

## 7. Gates

**Gate A — before any public posting**
- [ ] Theorem A proof text final (both Π branches explicit; δ sign correct); reviewed by a human number theorist.
- [x] `CERTIFY_n1e30.txt` and `CERTIFY_p1_500000.txt` present, ending in CERTIFIED (3,811/3,811 and 323/323 blocks; 1,904 and 1,185 distinct survivors, all re-tested in Python) — 2026-11-01 13:04.
- [x] Literature comparison written; novelty claims rewritten against McIntosh–Dipra and Zhang.
- [x] McIntosh–Dipra and Zhang read in full (2026-11-01); the two TODOs in the paper resolved; Theorem A reattributed.
- [x] Implementation-completeness proposition written into §3 (Proposition 3.6).

**Gate B — release candidate**
- [ ] `./run_tests.sh` passes from a clean clone on a second machine (transcript saved).
- [ ] Source, compiler flags, binaries' hashes, inputs' hashes, command lines and logs frozen; Zenodo DOI.
- [ ] 10²⁴ histogram rescan finished, or the four-match count claim removed.
- [ ] Every bibliography entry verified against the primary source.

**Gate C — journal submission**
- [ ] Target journal's AI policy confirmed against the actual use history (written guidance if ambiguous).
- [ ] Prose human-authored to the standard the venue requires.
- [ ] Disclosure text matches the roles in §4.
- [ ] Substantive consultant feedback resolved.
