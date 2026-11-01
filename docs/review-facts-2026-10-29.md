# AI-agent fact-check audit of `paper/clc.tex` (2026-10-29) — not an independent human review

*Produced by an independent reviewer agent given only the LaTeX source and instructed to verify every numerical and
factual claim against primary evidence (raw result files, block logs, OEIS, Crossref, arXiv, the cited PDFs). No
repository files were modified by the reviewer. Items marked DISCREPANCY were fixed in the paper the same day; see the
"Resolution" notes.*

## Summary of discrepancies
- **D1 (proof error).** Thm 3.1(c), case Π>1: "(1+p₂⁻²)³ ≤ 1+3.0001 p₂⁻²" is false; the correct coefficient at p₂=37 is 3.0022, and with it the case does not yield p₂² ≤ 24p₁³+3. *Resolution:* the case is now proved differently — e>d≥1 and s>2p₁, so only the d-factor of Π can exceed 1, Π ≤ 1+1/r², hence r² ≤ 8p₁³−1 < 24p₁³. The enumeration used p₂² ≤ 24p₁³+3 (valid in both cases), so Theorem B is unaffected. A test (`tests/test_theorems.py::test_pi_greater_than_one_case`) now records both the false estimate and the corrected argument.
- **D2.** §6 four-prime heuristic 7.5e-7 / 97% not reproduced: following the description exactly gives 6.34e-7 / 96.5%; no script existed in the repo. *Resolution:* `agrawal/k4_heuristic.py` added (reproduces 6.339e-7, 96.5%); paper and notes now quote 6.3e-7 / ≈96%.
- **D3.** "exactly one … has four matching primes" is not supported by archived output: the scan recorded only the first n attaining the maximum and never printed the (matches, ω) histogram. *Resolution:* wording changed to "first attained at …; the count was not recorded"; scanner now prints the full histogram for future runs; optional rerun listed in the plan.
- **D4.** Bibliography titles: Chick = "Carmichael number variable relations: three-prime Carmichael numbers up to 10²⁴"; SW24 = "Advances in tabulating Carmichael numbers", Res. Number Theory 11 (2025) art. 8; SW25 = "Algorithms for Carmichael numbers". *Resolution:* fixed.
- **D5.** Pinch's 10¹⁶ statement is restricted to an odd number of prime divisors; the paper quoted it unrestricted and used it in §6 for the (even-k) p₁=13 case. *Resolution:* restriction stated; §6 now cites our own 10²⁴ scan.
- **D6.** Side conditions p≡3 (mod 8), (5/p)=−1 are Pomerance's (reprised by BFW); Chen–Greene use order conditions ord_p(2)|M, ord_F(p)|N with n≡2,3 (mod 5); Grantham's paper is not a construction attempt. *Resolution:* sentence rewritten.
- Minor: A329948 was authored by D. Suteu (A. Eldar contributed the 179-term b-file); "six seconds" measured as 8.8 s; p₁>500000 tail "below 10⁻²⁵" is borderline. *Resolution:* all reworded.

## A. Computational results
1. Totals 308,279,939 / 49,679,870 / 123,381,982 — RESULT and VERIFY files; Shallue–Webster abstracts (arXiv:2506.09903: "308,279,939 Carmichael numbers less than 10^24"; arXiv:2401.14495: 49679870 below 10^22). **CONFIRMED.**
2. Per-ω table — identical to RESULT_1e24, sum 308,279,939. **CONFIRMED.**
3. 826 / 179 three-match numbers — RESULT files. **CONFIRMED.**
4. Zero hits, zero verification failures. **CONFIRMED.**
5. Best near miss 15500309690554865758009 = 37·103·109·127·307·523·613·1429·2089, Carmichael, matches {37,109,1429,2089}, 4 of 9. **CONFIRMED.** Uniqueness **UNSUPPORTED** (see D3): the script updates `best` only on strict `>` and printed only the ω-marginal and the g==3 total.
6. 1e22 best partial 9857524690572481 = 13·19·61·271·433·1181·4721, matches {13,61,433}; equals the first term of A329948. **CONFIRMED.**
7. k4 block logs, independently summed (dedup by blk): n1e30 — 3811 blocks = nblk, no duplicates/gaps, pairs 230,612,582,193, wsurv 1,904, fsurv 1, sol 0; p1_500000 — 323 blocks = nblk, pairs 86,517,004,140, wsurv 1,185, fsurv 1, sol 0. Equal to Table 1 and the RESULT files. **CONFIRMED.**
8. Coverage: block p₁-ranges non-overlapping and in order; n1e30 covers all 487,684 primes ≡1 (mod 12) in [13, 31622776]; p1_500000 covers all 10,329 in [13, 500000]; p1max = ⌊B^{1/4}⌋, p2max = ⌊(B/13)^{1/3}⌋ and isqrt(24·500000³+1) respectively. **CONFIRMED.**
9. Wall times 5208.3 s = 86.8 min and 8734.1 s = 145.6 min; run_k4.log timestamps agree; host Apple M4 Pro, 14 threads. **CONFIRMED.**
10. Solution files: exactly one FSURV each (26921089 = 13·37·97·577, Carmichael, 2^(n−1)≡1, 38 ∤ 26921090), 907 and 222 WSURV lines, all with P>2⁴⁰, none passing base-2 Fermat; 907+997 = 1904 and 222+963 = 1185 handled in C vs Python. **CONFIRMED.**
11. Relaxed check 13685: d=27, e=67, s=977, d·e·s·Π = 1,728,000 = 24³·5³ exactly. **CONFIRMED.**
12. Numerics: √(24·13³+1) = 229.6; 477·13^7.5 = 1.079e11; 4·4.9³ = 470.6 < 477; √24 = 4.899 < 4.9; 2⁶⁴ = 1.845e19. **CONFIRMED.**
13. `enum_k4 --B 1e24` rerun: 153/153 blocks, 359,696,710 pairs, 656 window survivors, 1 Fermat survivor (26921089), 0 solutions, 8.8 s. **CONFIRMED** (timing approximate).
14. 1e24 scan elapsed 75822 s (21.1 h); pipeline log 13:28:16 Oct 20 → 10:31:59 Oct 21. Consistent.
15. DATA_SHA256: a006972.txt hash equals a fresh download. **CONFIRMED** (12.3 GB / 7.5 GB files not re-hashed).

## B. Literature and data
16–17. A132195 a(22)=420658, a(24)=1494738; A299711 a(22)=262818, a(24)=6529921 — b-files. **CONFIRMED.**
18. A329948: "at least 3 prime factors p with p+1 | m+1"; b-file by Eldar, 179 terms below 10²²; author D. Suteu (2019). **CONFIRMED** (attribution reworded).
19. A006972: Suteu's table has 129,125 lines (399 … 999997631942399). **CONFIRMED.**
20. Goutier readme row 22: total 49679870, per-ω identical to RESULT_1e22; C(10¹⁵)=105212, C(10¹⁸)=1401644 also there and on Pinch's page. **CONFIRMED.**
21. Pinch tables URL live; "Carmichael numbers up to 10^21", Turku 2007, TUCS 46; 20,138,200 numbers ≤ 10²¹. **CONFIRMED.**
22. carm10e24.bin: HTTP 200, Last-Modified 7 Mar 2026, 12,296,962,769 bytes. **CONFIRMED.**
23. Williams, CMB 20 (1977) 133–143, DOI 10.4153/CMB-1977-025-9; full text confirms the question, odd k under his formulation, p±1 divisibilities, 3∤n, k≠3. **CONFIRMED.**
24. Pinch, "Absolute quadratic pseudoprimes", Turku 2007, TUCS 46, pp. 113–128 (page range via OEIS A392556/7). **CONFIRMED.**
25–33. Howe (MC 69, 1711–1719), BFW (MC 90, 1931–1955), Chen–Greene (FQ 41, 334–344), AKS, AGP, Chernick, Löh–Niebuhr, Erdős, Grantham (MC 70, 873–891) — all via Crossref/zbMATH/scans. **CONFIRMED.**
34–36. Shallue–Webster and Chick titles — **DISCREPANCY**, fixed (D4).
37. Pomerance 1984 (dopo.pdf): construction with p≡3 mod 8, (5/p)=−1, smooth squarefree (p−1)/2 and (p+1)/4, n≡1 mod Q1, n≡−1 mod Q3 ⇒ p−1|n−1 and p+1|n+1. **CONFIRMED.**
38. Gilchrist 2013 web page (2009 verification from Feitsma's psp(2) list; Nicely's page; Greathouse 2011): no BPSW pseudoprime below 2⁶⁴. **CONFIRMED**; reference details added.
39. Pinch's 10¹⁶ statement restricted to odd number of prime divisors — **DISCREPANCY**, fixed (D5).
40. BPSW construction attributions — **PARTIAL DISCREPANCY**, fixed (D6).
41. Lenstra–Pomerance AIM notes (archived PDF, §B.1 pp. 30–32): k≡1 mod 4 (also k≡3), pᵢ≡3 mod 80, (pᵢ−1)|(n−1), (pᵢ+1)|(n+1). **CONFIRMED.**
42–43. 2⁶⁴ bound; Pinch Turku references. **CONFIRMED.**

## C. Other
44. Thm 3.1(c) Π>1 constant — **DISCREPANCY**, fixed (D1). The Π<1 case, the bound −1/x² ≤ (t−2)/(tx²) < 1/x², and the mod-24 step were checked and are correct.
45. §6 heuristic — **DISCREPANCY**, fixed (D2). Tail beyond p₁ = 500,000: ~1.8e-25 by X⁻⁴ extrapolation, ~3e-26 with log factors.
46. Table 1 / Theorem 3.6 — **CONFIRMED.**
47. Not checked by the reviewer: family-search timings and ranges (§5), subset-product margins, onset heuristics, self-test counts, "make test under a minute", SHA-256 of the large inputs, Gilchrist's page itself (host down).
