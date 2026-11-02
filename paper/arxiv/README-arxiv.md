# arXiv submission kit (v1.1)

Upload **only** `paper/clc.tex` (single file; bibliography is inline, no .bbl or figures needed). arXiv compiles with pdflatex;
the packages used (amsart, amsmath, amssymb, amsthm, booktabs, array, url, enumitem, algorithm, algpseudocode, xcolor, hyperref)
are all in TeX Live. If the build fails, download the log from the submission page and fix before announcing.

Form fields:
- **Archive / category:** math (Number Theory, `math.NT`). No cross-list needed.
- **Title:** Exhaustive searches for Williams numbers: the four-prime case and a general 10^24 bound
- **Authors:** Raz Vakil
- **Abstract:** `abstract.txt` (plain text; arXiv accepts the inline TeX math as written).
- **Comments:** 11 pages, 1 algorithm, 3 tables. Code, logs and certification records: https://doi.org/10.5281/zenodo.23886954
- **MSC classes:** 11Y11 (Primary), 11A51, 11Y16
- **License:** arXiv.org perpetual, non-exclusive license is sufficient; CC BY 4.0 if you prefer maximal reuse.
- **Report number / Journal ref / DOI:** leave empty (the Zenodo DOI is for the code archive, not the article).

After the identifier arXiv:YYMM.NNNNN exists: add it to README.md and CITATION.cff, then do the OEIS comments and the emails
(drafts to be prepared on request).
