"""Prime harvesting for the subset-product construction.

Milestone hunt (Carmichael + Lucas-Carmichael): fix two coprime odd smooth
moduli O1, O2 (given as {prime: exponent-cap} dicts) and a 2-adic budget a2.
Harvest primes p with
    p - 1 = 2d,          d | O1   (so p ≡ 3 mod 4, all pool primes),
    p + 1 = 2^t * m,     t <= a2, m | O2.
Any squarefree product n of pool primes with n ≡ 1 (mod lcm of the p-1) and
n ≡ -1 (mod lcm of the p+1) is then simultaneously Carmichael and
Lucas-Carmichael by Korselt's criteria.

Plain-Carmichael mode (calibration / classic Loeh-Niebuhr): harvest p with
p - 1 | Lambda for a fixed smooth Lambda (2 allowed in Lambda).
"""

from dataclasses import dataclass, field

from .numth import factor_over, is_prime, v2


@dataclass(frozen=True)
class Record:
    p: int
    fac_m1: dict[int, int] = field(hash=False)  # factorization of p - 1
    fac_p1: dict[int, int] | None = field(default=None, hash=False)  # of p + 1


def _smooth_divisors(caps: dict[int, int], limit: int | None):
    primes = sorted(caps)

    def rec(i: int, val: int, fac: tuple):
        yield val, fac
        for j in range(i, len(primes)):
            q = primes[j]
            v = val
            for e in range(1, caps[q] + 1):
                v *= q
                if limit is not None and v > limit:
                    break
                yield from rec(j + 1, v, fac + ((q, e),))

    yield from rec(0, 1, ())


def smooth_divisors_list(caps: dict[int, int], limit: int | None = None):
    """All (value, fac-dict) products of `caps` primes within caps and limit."""
    return [(v, dict(f)) for v, f in _smooth_divisors(caps, limit)]


def harvest_clc(
    o1_caps: dict[int, int],
    o2_caps: dict[int, int],
    a2: int,
    d_limit: int | None = None,
    max_divisors: int | None = None,
) -> list[Record]:
    """Harvest primes for the Carmichael + Lucas-Carmichael hunt."""
    assert all(q % 2 == 1 and is_prime(q) for q in o1_caps), "O1 must be odd primes"
    assert all(q % 2 == 1 and is_prime(q) for q in o2_caps), "O2 must be odd primes"
    assert not set(o1_caps) & set(o2_caps), "O1 and O2 must be coprime"
    assert a2 >= 2
    excluded = set(o1_caps) | set(o2_caps)

    pool = []
    plus_caps = dict(o2_caps)
    seen = 0
    for d, fac_d in _smooth_divisors(o1_caps, d_limit):
        seen += 1
        if max_divisors is not None and seen > max_divisors:
            break
        p = 2 * d + 1
        if p in excluded or p < 3:
            continue
        # cheap filter first: p + 1 = 2(d+1) must be 2^t * (divisor of O2)
        e = d + 1
        t = v2(e) + 1  # v2(p+1); d odd => d+1 even => t >= 2
        if t > a2:
            continue
        m = e >> (t - 1)
        fac_m = factor_over(m, plus_caps)
        if fac_m is None:
            continue
        if not is_prime(p):
            continue
        fac_m1 = {2: 1, **dict(fac_d)}
        fac_p1 = {2: t, **fac_m}
        pool.append(Record(p=p, fac_m1=fac_m1, fac_p1=fac_p1))
    pool.sort(key=lambda r: r.p)
    return pool


def harvest_carmichael(lam_caps: dict[int, int], m_limit: int | None = None) -> list[Record]:
    """Harvest primes p with (p-1) | Lambda for the plain-Carmichael calibration."""
    excluded = set(lam_caps)
    pool = []
    for m, fac_m in _smooth_divisors(lam_caps, m_limit):
        p = m + 1
        if p < 3 or p in excluded:
            continue
        if not is_prime(p):
            continue
        pool.append(Record(p=p, fac_m1=dict(fac_m)))
    pool.sort(key=lambda r: r.p)
    return pool
