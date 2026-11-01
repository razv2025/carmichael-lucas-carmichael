# AI-agent adversarial audit of `paper/clc.tex` (2026-10-29) — not an independent human review

*Produced by a reviewer agent given only the LaTeX source and instructed to re-derive every proof, test every claim
numerically, and look for gaps. It did not read any other repository file. Each finding is followed by its resolution.*

**No FATAL findings.** Theorems 2.1, 2.2, 2.3, 3.1(a),(b), Corollary 3.2, Lemma 3.4, Theorems 5.1–5.3 and the Corollary
after 5.3 were found correct as written; Theorem 3.1(c) is true but its proof needed repair.

1. **ERROR — Theorem 3.1(c), Π > 1 branch.** "(1+p₂⁻²)³ ≤ 1+3.0001p₂⁻²" is false for every p₂ ≤ 173 (effective constant 3.00219 at p₂ = 37), and even granting it, 3.0001(8p₁³−1) < 24p₁³+3 fails for p₁ ≥ 23. Suggested fixes: use (1+u)³ ≤ 1+3u/(1−u), or prove Π < 1 rigorously. *Resolution:* the branch is now proved via "only the d-factor can exceed 1" (e > d ≥ 1 and s > 2p₁ ⇒ e, s ≥ 2), giving Π ≤ 1+1/r² and r² ≤ 8p₁³−1 < 24p₁³. Same error was found independently by the fact-check.
2. **GAP — Remark after 3.1 (Π < 1 always).** With e = 2 the stated inequality can fail (example p₂=1009, q=1021, r=1033); needs e ≥ 3, which holds because e = 2 forces Pr = q². *Resolution:* the remark was removed; the proof no longer relies on Π < 1.
3. **ERROR (minor) — Lemma 3.3 "iff".** Solvability also needs gcd(p₁, L_{p₂}) = 1; counterexamples (13,157), (97,193). *Resolution:* statement now "iff p₁ ∤ p₂²−1 and p₁ ≡ p₂ (mod g)"; the algorithm paragraph says such pairs are skipped (they have no completion). (Found independently in the author's own third pass before this report arrived.)
4. **GAP/TYPO — "p₂ < √24 p₁^{3/2}".** Part (c) gives p₂² ≤ 24p₁³+1. *Resolution:* now "p₂² ≤ 24p₁³+1 < 24.01p₁³ = (4.9p₁^{3/2})²".
5. **GAP (trivial) — Prop 2.3.** s < 2√2p₂²/(p₂²−1) < 3 needs p₂ ≥ 5. *Resolution:* stated.
6. **GAP — Algorithm paragraph.** Range of the j-walk and the hand-over threshold unstated; m > 2⌈√(2p₁)⌉ unstated; strict vs weak window form. *Resolution:* paragraph rewritten with S, R_j, M*, explicit j-range and the exact m-window, the admissibility definition (weak form, as implemented), and the note that the two walks give identical survivor lists on six instances.
7. **GAP — Validation / proof of Theorem 3.5.** (a) Relaxed test cannot exercise the Fermat step (13685 is not Carmichael): say so. (b) Inconsistency "every survivor re-verified in Python" vs "survivors with P > 2⁴⁰": the P ≤ 2⁴⁰ survivors rest on the C 128-bit routine; re-verify all in Python. (c) "goes through with 2 replaced by κ" not literally true for part (c). *Resolution:* (a) stated; (b) text now says exactly what was done, the C routine is checked against Python in the test suite (`test_c_fermat_routine_matches_python`), and both campaigns are being rerun with `--dumpw` so that all 1,904 + 1,185 survivors are re-verified in Python (`clc/k4/rerun_dump.sh`, result in `RESULT_dump_reverify.txt`); (c) reworded to the lemmas actually used.
8. **STYLE/accuracy — Howe's definition.** Howe's criterion for order 2 allows n ≡ 1 or n ≡ p (mod p²−1); the paper's "iff n ≡ p" describes a subclass. *Resolution:* reworded; the CLC conclusion is unchanged (n ≡ 1 is impossible for CLC n). Checking the exact wording against Howe's paper is on the pre-submission checklist.
9. **STYLE — §5.2** attribution of the side-split fact to Lemma 2.2. *Resolution:* now "immediate".
10. **STYLE — "x ≥ 2"** unnecessary. *Resolution:* "x > 0".
11. **STYLE — Theorem 5.2** even-m shortcut (optional). Not adopted.
12. **Heuristic.** Recomputed 6.3×10⁻⁷ / 96.5% (paper had 7.5×10⁻⁷ / 97%). *Resolution:* fixed, with the reproducing script `agrawal/k4_heuristic.py`.

## What the referee verified numerically
Lemma 2.1 by brute force (p < 120, k < 3000); Prop 2.3 over all prime triples ≤ 3000 (max t = 1.994, max s = 2.823, no CLC triple); the product identity symbolically and the failure of the 3.0001 estimate exactly; the mod-24 step; impossibility of p₂² = 24p₁³+1 for p₁ ≤ 10⁵; Lemma 3.3 counterexamples by full-period brute force; Lemma 3.4's identity symbolically and all its inequalities on 62 relaxed (κ = 24, 120) two-prime tuples (true j not floor/ceil in 56 of 62); the relaxed four-prime problem (only 13685 below the search range; d,e,s = 27, 67, 977; des·Π = 24³·5³); Theorems 5.1–5.3 symbolically for m = 2..6 and by brute force; the factorisations and Lucas conditions of 15500309690554865758009 and 26921089; Table 2's sum.
