from agrawal.golden import harvest_golden, sparse_odd_parts
from agrawal.numth import is_prime


def reconstruct(fac):
    v = 1
    for q, e in fac.items():
        v *= q**e
    return v


def test_sparse_odd_parts():
    parts = dict(
        (v, f) for v, f in sparse_odd_parts(10, 100, max_omega=2)
    )
    assert parts[1] == {}
    assert parts[27] == {3: 3}
    assert parts[63] == {3: 2, 7: 1}
    assert 45 in parts  # 3^2 * 5
    assert all(v % 2 == 1 for v in parts)
    # no repeated-prime pseudo-pairs: 9*3 = 27 must appear only as {3:3}
    assert parts[27] == {3: 3}


def test_harvest_golden_small():
    pool = harvest_golden(20, 10**6)
    ps = {r.p for r in pool}
    # classic fully-golden primes
    assert 31 in ps  # 30 = 2*3*5, 32 = 2^5
    assert 127 in ps  # 126 = 2*3^2*7, 128 = 2^7
    assert 257 not in ps  # 256 = 2^8 but 258 = 2*3*43 and 43 > 20
    for r in pool:
        assert is_prime(r.p) and r.p > 20
        assert reconstruct(r.fac_m1) == r.p - 1
        assert reconstruct(r.fac_p1) == r.p + 1
        assert max(r.fac_m1) <= 20 and max(r.fac_p1) <= 20


def test_towers_reach_beyond_scan_range():
    # towers like 2*3^b + 1 give golden primes far beyond any twin-scan bound
    pool = harvest_golden(100, 10**15)
    assert any(r.p > 10**9 for r in pool)
