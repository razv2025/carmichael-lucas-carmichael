import pytest

from agrawal.numth import is_prime
from agrawal.verify import (
    agrawal_congruence,
    agrawal_congruence_crt,
    is_agrawal_counterexample,
    is_carmichael,
    is_lucas_carmichael,
)


def test_primes_pass_congruence():
    # every prime n with gcd(n, r) = 1 satisfies the congruence (Frobenius)
    for n in [3, 7, 13, 97, 10007, 104729]:
        for r in [5, 7, 11]:
            if n % r:
                assert agrawal_congruence(n, r), (n, r)


def test_small_composites_never_counterexamples():
    # reproduces the known verification on a small range: no composite passes
    # with n^2 != 1 mod 5 (Kayal-Saxena checked to 1e10, Primaboinca to 1e17)
    for n in range(6, 3000):
        if n % 5 and not is_prime(n):
            assert not is_agrawal_counterexample(n, 5), n


def test_crt_matches_direct():
    # squarefree composites: per-prime CRT check agrees with direct check
    cases = [([3, 11, 17], 7), ([7, 13], 5), ([3, 5, 47], 7), ([23, 89], 5)]
    for factors, r in cases:
        n = 1
        for p in factors:
            n *= p
        assert agrawal_congruence_crt(factors, r) == agrawal_congruence(n, r)


def test_vana_mersenne_r4():
    # Váňa: composite Mersenne numbers M_p (p prime > 3) pass the r = 4
    # congruence (LP form allows composite r); they satisfy n^2 ≡ 1 (mod 4),
    # so they are not counterexamples — a good independent probe of the code.
    m11 = 2**11 - 1  # 2047 = 23 * 89
    assert not is_prime(m11)
    assert agrawal_congruence(m11, 4)
    m23 = 2**23 - 1  # composite
    assert not is_prime(m23)
    assert agrawal_congruence(m23, 4)


def test_carmichael():
    assert is_carmichael([3, 11, 17])  # 561
    assert is_carmichael([5, 13, 17])  # 1105
    assert not is_carmichael([3, 5, 7])
    with pytest.raises(AssertionError):
        is_carmichael([3, 11])  # too few factors


def test_lucas_carmichael():
    assert is_lucas_carmichael([3, 7, 19])  # 399, smallest
    assert is_lucas_carmichael([5, 11, 17])  # 935
    assert is_lucas_carmichael([5, 7, 11, 23])  # 8855
    assert not is_lucas_carmichael([3, 11, 17])  # 561 is Carmichael, not LC
    assert not is_lucas_carmichael([7, 11, 13, 41])  # 41041 is Carmichael, not LC


def test_no_known_number_is_both():
    # spot-check: the first Lucas-Carmichael numbers are not Carmichael
    for factors in [[3, 7, 19], [5, 11, 17], [5, 13, 31], [5, 7, 11, 23]]:
        assert not is_carmichael(factors)
