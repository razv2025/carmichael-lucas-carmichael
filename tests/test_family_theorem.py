"""Appendix A of the paper: no product of m >= 2 pairwise non-proportional linear forms a_i k + b_i (a_i > 0) satisfies
(f_i - 1) | (n - 1) and (f_i + 1) | (n + 1) identically.  Brute-force confirmation on small coefficient ranges, a check
that the one-sided (Carmichael) condition alone does have solutions there (so the search is not vacuous), and a check of
the two facts the proof uses."""
from fractions import Fraction as F
from itertools import combinations, product

def n_at(forms, x):
    v = F(1)
    for a, b in forms: v *= a * x + b
    return v

def one_sided(forms):   # (f_i - 1) | (n - 1) for all i
    return all(n_at(forms, F(1 - b, a)) == 1 for a, b in forms)

def two_sided(forms):
    return one_sided(forms) and all(n_at(forms, F(-1 - b, a)) == -1 for a, b in forms)

def families(m, amax, bmax):
    lin = [(a, b) for a in range(1, amax + 1) for b in range(-bmax, bmax + 1)]
    for fs in combinations(lin, m):
        if all(fs[i][0] * fs[j][1] != fs[j][0] * fs[i][1] for i in range(m) for j in range(i)):   # pairwise non-proportional
            yield fs

def test_no_two_sided_family_small_ranges():
    found1 = 0
    for m, amax, bmax in ((2, 14, 8), (3, 7, 4)):
        for fs in families(m, amax, bmax):
            if one_sided(fs):
                found1 += 1
                # step 1 of the proof: all sigma_i coincide
                assert len({F(1 - b, a) for a, b in fs}) == 1
                assert not two_sided(fs)
    assert found1 > 0          # one-sided families exist in the range

def test_chernick_is_one_sided_only():
    ch = ((6, 1), (12, 1), (18, 1))
    assert one_sided(ch) and not two_sided(ch)
    # step 2: at tau_i for the factor of largest slope, the other factors lie strictly inside (-1, 1)
    a_max = max(a for a, _ in ch); tau = F(-2, a_max)
    assert all(abs(a * tau + b) < 1 for a, b in ch if a != a_max) and abs(n_at(ch, tau)) < 1
