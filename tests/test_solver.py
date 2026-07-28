from agrawal.harvest import harvest_carmichael, harvest_clc, smooth_divisors_list
from agrawal.solver import build_system, greedy_subpool, mitm_search
from agrawal.verify import is_carmichael


def test_smooth_divisors():
    got = sorted(v for v, _ in smooth_divisors_list({2: 2, 3: 1}))
    assert got == [1, 2, 3, 4, 6, 12]
    got = sorted(v for v, _ in smooth_divisors_list({2: 3, 5: 1}, limit=10))
    assert got == [1, 2, 4, 5, 8, 10]


def test_harvest_carmichael_pool():
    # Lambda = 2^4 * 3^2 * 5 * 7 = 5040; known divisor-plus-one primes
    pool = harvest_carmichael({2: 4, 3: 2, 5: 1, 7: 1})
    ps = [r.p for r in pool]
    for p in [11, 13, 17, 19, 29, 31, 37, 41, 43, 61, 71, 73, 113, 127, 211]:
        assert p in ps
    assert 5041 not in ps  # 71^2, composite
    # p - 1 must divide Lambda
    for r in pool:
        assert 5040 % (r.p - 1) == 0


def test_mitm_finds_carmichael_numbers():
    # classic Loeh-Niebuhr construction at toy scale: this must produce
    # verified Carmichael numbers in well under a second
    pool = harvest_carmichael({2: 4, 3: 2, 5: 1, 7: 1})
    hits = list(mitm_search(pool, max_hits=5))
    assert hits, "expected Carmichael hits from the 5040 pool"
    for h in hits:
        assert h["verified"]
        assert is_carmichael(h["primes"])
        assert h["k"] >= 3


def test_harvest_clc_structure():
    pool = harvest_clc({3: 2, 7: 1, 11: 1, 19: 1}, {5: 1, 13: 1, 17: 1}, a2=8)
    for r in pool:
        assert r.p % 4 == 3  # forced by construction
        assert (r.p - 1) % 2 == 0 and ((r.p - 1) // 2) % 2 == 1
        assert r.fac_p1 is not None
        # p+1 reconstructs from its factorization
        v = 1
        for q, e in r.fac_p1.items():
            v *= q**e
        assert v == r.p + 1


def test_build_system_and_greedy():
    pool = harvest_carmichael({2: 4, 3: 2, 5: 1, 7: 1})
    M, t, stats = build_system(pool)
    assert t % 16 == 1 and t % 9 == 1 and t % 5 == 1 and t % 7 == 1
    assert stats["margin"] > 0
    sub = greedy_subpool(pool, max_n=10)
    assert 0 < len(sub) <= 10
