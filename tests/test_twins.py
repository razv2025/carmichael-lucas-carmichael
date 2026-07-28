from agrawal.numth import is_prime
from agrawal.split import (
    build_split_system,
    consistent_pool,
    eval_split,
    prep,
)
from agrawal.twins import harvest_twins, load_pool, save_pool, smooth_numbers


def smooth_over(n, y):
    for q in range(2, y + 1):
        while n % q == 0:
            n //= q
    return n == 1


def test_smooth_numbers():
    sm = list(smooth_numbers(5, 30))
    assert sm == [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30]


def test_harvest_twins_small():
    pool = harvest_twins(20, 100000)
    assert pool, "expected twin-smooth primes below 1e5 at y=20"
    for r in pool:
        assert is_prime(r.p) and r.p > 20
        assert smooth_over(r.p - 1, 20) and smooth_over(r.p + 1, 20)
        v1 = 1
        for q, e in r.fac_m1.items():
            v1 *= q**e
        v2 = 1
        for q, e in r.fac_p1.items():
            v2 *= q**e
        assert v1 == r.p - 1 and v2 == r.p + 1
    # 23 is twin-smooth at y=20 (22 = 2*11, 24 = 2^3*3) and exceeds y
    assert any(r.p == 23 for r in pool)
    # 17 is twin-smooth but <= y, hence correctly excluded
    assert not any(r.p == 17 for r in pool)


def test_save_load_roundtrip(tmp_path):
    pool = harvest_twins(20, 10000)
    path = tmp_path / "pool.jsonl"
    save_pool(pool, path)
    back = load_pool(path)
    assert [r.p for r in back] == [r.p for r in pool]
    assert back[0].fac_m1 == pool[0].fac_m1


def test_split_consistency():
    pool = harvest_twins(20, 100000)
    prepped = prep(pool)
    # side1 = all odd primes: p+1 may then use only powers of 2
    all_odd = {3, 5, 7, 11, 13, 17, 19}
    for branch in (1, 3):
        usable = consistent_pool(prepped, all_odd, branch)
        for r in usable:
            assert all(q == 2 for q in r.fac_p1)
            assert r.p % 4 == (3 if branch == 3 else 1)


def test_build_split_system_residues():
    pool = harvest_twins(20, 100000)
    prepped = prep(pool)
    side1 = {3, 7, 11, 19}
    margin, usable, sub = eval_split(prepped, side1, branch=3)
    if len(sub) >= 3:
        M, t, m_fac = build_split_system(sub, side1, branch=3)
        for r in sub:
            assert (t - 1) % (r.p - 1) == 0, "target must be ≡ 1 mod every p-1"
            assert (t + 1) % (r.p + 1) == 0, "target must be ≡ -1 mod every p+1"
