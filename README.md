# Carmichael ∩ Lucas–Carmichael numbers

Code, data and notes behind the preprint (repository: https://github.com/razv2025/carmichael-lucas-carmichael)

> R. Vakil, *Exhaustive searches for Williams numbers: the four-prime case and a general 10²⁴ bound* (2026) — `paper/clc.tex`, `paper/clc.pdf`; supplementary note `paper/supplement.pdf`.

A squarefree composite n is **Carmichael** if (p−1) | (n−1) for every prime p | n and **Lucas–Carmichael** if (p+1) | (n+1) for every p | n. Numbers that are both are **Williams numbers** (Echi 2007; the question is H. C. Williams's, 1977); no example is known. The code and older notes call them CLC numbers. Prior work: McIntosh–Dipra (JNT 2015) proved finiteness with all but three primes fixed and excluded four-prime examples with p₁ ≤ 2×10⁴ or N ≤ 10²⁴; see `docs/literature-williams-numbers.md`. Results in this repository:

| result | where |
|---|---|
| No such number below 10²⁴ (independent scan of all 308,279,939 Carmichael numbers < 10²⁴, with completeness and OEIS cross-checks; near-miss statistics) | `clc/` — `RESULT_1e24_2026-10-21.txt`, `RESULT_1e22_2026-10-20.txt`, `VERIFY_1e24_list_completeness.txt`, `DATA_SHA256.txt` |
| Theorem A (four prime factors p₁<p₂<p₃<p₄): all pᵢ ≡ 1 (mod 12), p₃ < 2p₁p₂, p₄ < √(2p₁p₂p₃), p₂² ≤ 24p₁³ + 1 — **this is McIntosh–Dipra's theorem (JNT 2015, Thms 2–3, d = 4)**, restated with an independent proof | `paper/clc.tex` §3, `docs/k4-notes.md` |
| **Theorem B**: no four-prime example with n ≤ 10³⁰, and none at all with smallest prime ≤ 500,000 | `clc/k4/` — `RESULT_n1e30.txt`, `RESULT_p1_500000.txt`, per-block logs `k4_*.jsonl` |
| Impossibility theorems for two-sided Chernick-type polynomial families; exhaustive searches of the remaining strata; quantified failure of the two-sided subset-product method; heuristics | `agrawal/`, `docs/obstructions.md`, `data/` |

## Layout

- `paper/` — the preprint (LaTeX; build with `tectonic clc.tex`).
- `clc/` — the 10²²/10²⁴ verification: `scan_carmichael_list_for_clc.py` (factor-and-test scan), `scan_resumable.py` + `scanctl.sh` (checkpointed variant), `verify_carmichael_list.py` (completeness), `decode_pari_writebin.gp`, `pipeline_1e24.sh`, `check_lc_table_for_carmichael.py` (converse check). Inputs are the public tabulations cited in the paper (not redistributed; checksums in `DATA_SHA256.txt`).
- `clc/k4/` — the four-prime enumeration: `enum_k4.c` (algorithm and proofs of the facts it uses in the header comment), `brute_k4.c` (brute-force reference for the relaxed test problem), `verify_k4.py` (independent re-verification of survivors), `run_k4.sh` / `k4ctl.sh` (driver and control), `Makefile` (`make test`).
- `agrawal/` — polynomial-family searches and theorems (`family.py`, `strata_m4.py`), subset-product experiments (`harvest.py`, `twins.py`, `split.py`, `golden.py`, `solver.py`, `explore.py`), the density heuristic (`heuristic.py`), and the exact verifier (`verify.py`). `docs/agrawal-hunt-log.md` is the original working log.
- `tests/` — pytest suite, including executable checks of the identities used in every proof (`test_theorems.py`) and of the scanner (`test_clc.py`).
- `docs/` — `k4-notes.md` (proofs), `obstructions.md` (working note on constructions and heuristics), `publication-plan.md` (venues, process, concerns and mitigations), `review-*.md` (independent review reports), `k7-search.md` (an unrelated earlier project on the Lander–Parkin–Selfridge conjecture, kept for the record together with `lps/`).

## Running the checks

```
pip install -r requirements.txt     # sympy, pytest (gmpy2 optional)
./run_tests.sh                      # pytest + C self-tests + relaxed end-to-end + 1e24 reproduction, ~1–2 min
```

Reproducing the computations: the 10²⁴ scan needs the Shallue–Webster list (`clc/pipeline_1e24.sh`, ~21 CPU-hours on 12 cores); the four-prime campaigns need no external data (`clc/k4/run_k4.sh`, 87 + 146 minutes on an Apple M4 Pro).

## License

MIT (see `LICENSE`). Please cite the preprint (`CITATION.cff`).
