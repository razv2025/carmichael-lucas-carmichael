"""Executable checks of the mathematical statements in the paper (docs/k4-notes.md, docs/obstructions.md).

These do not prove the theorems; they verify the algebraic identities the proofs rest on, exactly and
symbolically where possible, and brute-force the small cases.
"""
from fractions import Fraction
from itertools import combinations
from math import gcd, isqrt

import sympy as sp
from sympy import primerange


def L(p, kappa=2):
    return (p * p - 1) // kappa


# ---------- Lemma 1:  (p-1)|(n-1) and (p+1)|(n+1)  <=>  n/p ≡ 1 (mod (p^2-1)/2) ----------
def test_lemma1_equivalence_bruteforce():
    primes = list(primerange(3, 200))
    for p in primes:
        for m in range(1, 3000):
            n = p * m
            lhs = (n - 1) % (p - 1) == 0 and (n + 1) % (p + 1) == 0
            rhs = (m - 1) % L(p) == 0
            assert lhs == rhs, (p, m)


# ---------- Williams: no CLC number with three prime factors (brute force over p3 ≤ 3000) ----------
def clc(ps):
    n = 1
    for p in ps:
        n *= p
    return all((n - 1) % (p - 1) == 0 and (n + 1) % (p + 1) == 0 for p in ps)


def test_no_three_prime_clc_small():
    primes = list(primerange(3, 3000))
    hits = [t for t in combinations(primes, 3) if clc(t)]
    assert hits == []


def test_three_prime_structure_forces_t_equals_1():
    # the proof's first step: p1 p2 ≡ 1 (mod L3) with p1 p2 < p3^2 forces 2 p1 p2 = p3^2 + 1.  Check the
    # inequality step on all prime triples: whenever L3 | p1 p2 - 1, the quotient is exactly 1.
    primes = list(primerange(3, 600))
    for p1, p2, p3 in combinations(primes, 3):
        if (p1 * p2 - 1) % L(p3) == 0:
            assert (p1 * p2 - 1) // L(p3) == 1


# ---------- Theorem A, part (a): mod-12 structure (the congruence argument, checked on all 4-tuples) ----------
def test_mod4_mod3_argument():
    # For any odd primes p1..p4 with n ≡ p_i (mod 4) for all i and n ≡ p_i (mod 3) for all i (p_i ≠ 3),
    # all p_i ≡ 1 (mod 12).  (These two congruences are consequences of 4 | L_p and 3 | L_p.)
    primes = list(primerange(5, 60))
    for ps in combinations(primes, 4):
        n = ps[0] * ps[1] * ps[2] * ps[3]
        if all(n % 4 == p % 4 for p in ps) and all(n % 3 == p % 3 for p in ps):
            assert all(p % 12 == 1 for p in ps)


# ---------- Theorem A, part (c): the product identity  d e s Π = kappa^3 p1^3 ----------
def des_pi_identity(p1, p2, q, r, kappa):
    """d, e, s defined (as rationals) by the three quotient equations; returns d e s Π and kappa^3 p1^3."""
    P = p1 * p2
    d = Fraction(kappa * (P * q - 1), r * r - 1)
    e = Fraction(kappa * (P * r - 1), q * q - 1)
    s = Fraction(kappa * (p1 * q * r - 1), p2 * p2 - 1)
    Pi = (1 - (d - kappa) / (d * r * r)) * (1 - (e - kappa) / (e * q * q)) * (1 - (s - kappa) / (s * p2 * p2))
    return d * e * s * Pi, Fraction(kappa**3 * p1**3)


def test_product_identity_is_algebraic():
    # holds for arbitrary integers, not only solutions: it is an identity once d, e, s are defined by the equations
    import random
    rng = random.Random(1)
    for _ in range(2000):
        p1, p2, q, r = (rng.randrange(3, 10**6) | 1 for _ in range(4))
        kappa = rng.choice([2, 24, 120])
        if r * r == 1 or q * q == 1:
            continue
        lhs, rhs = des_pi_identity(p1, p2, q, r, kappa)
        assert lhs == rhs


def test_product_identity_on_relaxed_solution():
    # 13685 = 5·7·17·23 satisfies n/p ≡ 1 (mod (p^2-1)/24) for all four primes
    p1, p2, q, r, kappa = 5, 7, 17, 23, 24
    n = p1 * p2 * q * r
    assert all(((n // p) - 1) % L(p, kappa) == 0 for p in (p1, p2, q, r))
    P = p1 * p2
    d = kappa * (P * q - 1) // (r * r - 1); e = kappa * (P * r - 1) // (q * q - 1); s = kappa * (p1 * q * r - 1) // (p2 * p2 - 1)
    assert (d, e, s) == (27, 67, 977)
    assert all(x % p1 != 0 for x in (d, e, s))          # p1 ∤ d, e, s
    lhs, rhs = des_pi_identity(p1, p2, q, r, kappa)
    assert lhs == rhs and d * e * s != kappa**3 * p1**3


def test_mod_p1_step():
    # d(r^2-1) ≡ -kappa (mod p1) whenever kappa P q = d(r^2-1) + kappa, so p1 | d would force p1 | kappa.
    import random
    rng = random.Random(2)
    for _ in range(500):
        p1 = rng.choice(list(primerange(5, 500)))
        d = rng.randrange(1, 10**6); r = rng.randrange(3, 10**6)
        for kappa in (2, 24):
            lhs = d * (r * r - 1) + kappa          # = kappa P q, divisible by p1
            if lhs % p1 == 0:
                assert (d * (r * r - 1)) % p1 == (-kappa) % p1
                if d % p1 == 0:
                    assert kappa % p1 == 0


def test_pi_bounds_and_p2_bound_logic():
    # Π ∈ [(1-1/p2^2)^3, (1+1/p2^2)^3] for integer d,e,s ≥ 1 and r > q > p2; then des ≠ 8p1^3 ⇒ p2^2 ≤ 24 p1^3 + 3.
    import random
    rng = random.Random(3)
    for _ in range(3000):
        p2 = rng.randrange(37, 10**5); q = rng.randrange(p2 + 1, 10**6); r = rng.randrange(q + 1, 10**7)
        d, e, s = (rng.randrange(1, 10**6) for _ in range(3))
        Pi = (1 - Fraction(d - 2, d * r * r)) * (1 - Fraction(e - 2, e * q * q)) * (1 - Fraction(s - 2, s * p2 * p2))
        y = Fraction(1, p2 * p2)
        assert (1 - y) ** 3 <= Pi <= (1 + y) ** 3
    # the inequality chain:  if des Π = 8 p1^3 with des ≥ 8p1^3 + 1 then Π ≤ 1 - 1/(8p1^3+1), and Π ≥ 1 - 3/p2^2
    for p1 in primerange(13, 2000):
        # the largest p2 compatible with 1 - 3/p2^2 ≤ 1 - 1/(8 p1^3 + 1)  is  p2^2 ≤ 3(8p1^3+1) = 24 p1^3 + 3
        p2max = isqrt(24 * p1**3 + 3)
        assert Fraction(3, p2max**2) >= Fraction(1, 8 * p1**3 + 1)
        assert Fraction(3, (p2max + 1) ** 2) < Fraction(1, 8 * p1**3 + 1)


# ---------- Theorem A, part (b): size bounds from one quotient equation ----------
def test_size_bounds():
    import random
    rng = random.Random(4)
    for _ in range(2000):
        P = rng.randrange(10, 10**6); d = rng.randrange(1, 50); r = rng.randrange(5, 10**5)
        num = d * (r * r - 1) + 2
        if num % (2 * P):
            continue
        q = num // (2 * P)
        if not (q < r):
            continue
        assert q < 2 * P and r * r < 2 * P * q and q * r < 4 * P * P


# ---------- Polynomial-family theorems (symbolic) ----------
def test_family_theorem1_identities():
    a1, a2, a3, b1, b2, b3 = sp.symbols('a1 a2 a3 b1 b2 b3')
    a = [a1, a2, a3]; b = [b1, b2, b3]
    D = lambda i, j: a[i] * b[j] - a[j] * b[i]
    # subtracting the C and L products for index i gives the stated linear relations
    def diff(i):
        others = [j for j in range(3) if j != i]
        C = sp.prod([a[j] + D(i, j) for j in others]); Lp = sp.prod([D(i, j) - a[j] for j in others])
        return sp.expand(C - Lp)
    assert sp.simplify(diff(0) - 2 * (a2 * D(0, 2) + a3 * D(0, 1))) == 0
    assert sp.simplify(diff(1) - 2 * (a1 * D(1, 2) + a3 * D(1, 0))) == 0
    assert sp.simplify(diff(2) - 2 * (a1 * D(2, 1) + a2 * D(2, 0))) == 0
    # wedge identity
    assert sp.expand(D(1, 2) * a1 - D(0, 2) * a2 + D(0, 1) * a3) == 0


def test_family_theorem3_coefficient():
    for m in (2, 3, 4, 5, 6):
        a = sp.symbols(f'a1:{m+1}', positive=True); b = sp.symbols(f'b1:{m+1}'); tau = sp.symbols('tau')
        s = [(b[i] - 1) / a[i] for i in range(m)]; t = [(b[i] + 1) / a[i] for i in range(m)]
        poly = sp.Poly(sp.expand(sp.prod([tau - ti for ti in t]) - sp.prod([tau - si for si in s])), tau)
        assert poly.degree() <= m - 1
        c = poly.coeff_monomial(tau ** (m - 1))
        assert sp.simplify(c + sum(2 / ai for ai in a)) == 0     # coefficient of tau^{m-1} is -Σ 2/a_i ≠ 0


def test_family_theorem2_bruteforce():
    # all-minus system ∏_{j≠i}(2a_j - a_i) = a_i^{m-1} has no solution in distinct positive integers (small range)
    # (the SYSTEM has no solution: the proof shows the equation fails at the index of the largest a_i;
    #  single equations can hold, e.g. a = (2, 3, 6) at i = 1: (4-3)(12-3) = 9 = 3^2)
    for m in (3, 4, 5):
        for a in combinations(range(1, 26), m):
            imax = max(range(m), key=lambda i: a[i])
            assert sp.prod([2 * a[j] - a[imax] for j in range(m) if j != imax]) != a[imax] ** (m - 1)
            assert sp.prod([a[imax] - 2 * a[j] for j in range(m) if j != imax]) != a[imax] ** (m - 1)


def test_root_conditions_match_divisibility():
    # the polynomial-root formulation: n((1-b_i)/a_i) = 1  <=>  ∏_{j≠i}(a_j + D_ij) = a_i^{m-1}
    a = (6, 12, 18); b = (1, 1, 1)  # Chernick's Carmichael family (one-sided)
    k = sp.symbols('k')
    n = sp.prod([ai * k + bi for ai, bi in zip(a, b)])
    for i in range(3):
        val = n.subs(k, sp.Rational(1 - b[i], a[i]))
        D = [a[i] * b[j] - a[j] * b[i] for j in range(3)]
        assert val == 1
        assert sp.prod([a[j] + D[j] for j in range(3) if j != i]) == a[i] ** 2


def test_pi_greater_than_one_case():
    """Corrected Π>1 argument of Theorem A(c): e > d, s > 2 p1, so only the d-factor can exceed 1 and Π ≤ 1 + 1/r².
    Also records that the earlier estimate (1+x)^3 ≤ 1 + 3.0001 x (x = 1/p2², p2 ≥ 37) is FALSE."""
    import random
    rng = random.Random(5)
    x = Fraction(1, 37 * 37)
    assert (1 + x) ** 3 > 1 + Fraction(30001, 10000) * x          # the old constant was wrong
    for _ in range(3000):
        p1 = rng.choice([13, 37, 61, 73, 97, 109])
        p2 = rng.choice([p for p in range(37, 5000) if p % 12 == 1 and p > p1])
        q = rng.randrange(p2 + 1, 10**5); r = rng.randrange(q + 1, 10**6)
        P = p1 * p2
        d = Fraction(2 * (P * q - 1), r * r - 1); e = Fraction(2 * (P * r - 1), q * q - 1); s = Fraction(2 * (p1 * q * r - 1), p2 * p2 - 1)
        assert e > d and s > 2 * p1                                  # hence e, s ≥ 2 when they are integers
        if d >= 1:
            f1 = 1 - (d - 2) / (d * r * r); f2 = 1 - (e - 2) / (e * q * q); f3 = 1 - (s - 2) / (s * p2 * p2)
            assert f2 <= 1 and f3 <= 1 and f1 <= 1 + Fraction(1, r * r)
            assert f1 * f2 * f3 <= 1 + Fraction(1, r * r)
