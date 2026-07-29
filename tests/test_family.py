from agrawal.family import (
    instantiate,
    realize_b,
    search_pm1,
    signed_divisors,
)
from agrawal.verify import is_carmichael


def test_signed_divisors():
    assert signed_divisors(8) == [-8, -4, -2, -1, 1, 2, 4, 8]


def test_realize_b_roundtrip():
    a = (2, 3, 5, 7)
    b = (1, -4, 2, 3)
    D = {
        (i, j): a[i] * b[j] - a[j] * b[i]
        for i in range(4)
        for j in range(i + 1, 4)
    }
    got = realize_b(a, D)
    assert got is not None
    # any valid b' differs from b by a multiple of a (translation);
    # realize_b returns the representative with 0 <= b'_1 < a_1
    t = (got[0] - b[0])  # must be integer multiple of a[0] = 2... just verify D
    D2 = {
        (i, j): a[i] * got[j] - a[j] * got[i]
        for i in range(4)
        for j in range(i + 1, 4)
    }
    assert D2 == D


def test_chernick_analogue_machinery():
    # sanity: the Carmichael-only Chernick family (6k+1)(12k+1)(18k+1)
    # instantiates to genuine Carmichael numbers (k=1 -> 1729)
    a, b = (6, 12, 18), (1, 1, 1)
    ps = [ai * 1 + bi for ai, bi in zip(a, b)]
    assert ps == [7, 13, 19]
    assert is_carmichael(ps)  # 1729


def test_pm1_small_empty():
    # matches the earlier brute-force result: no all-minus m=3 families
    assert search_pm1(3, 200) == []


def test_instantiate_smoke():
    # no true CLC family known; instantiate must simply not crash / not yield
    hits = list(instantiate((6, 12, 18), (1, 1, 1), 50))
    assert hits == []  # Chernick gives Carmichael, never Lucas-Carmichael too
