"""Golden-prime harvesting: primes p where BOTH p-1 and p+1 are structurally
sparse — 2^a times at most `max_omega` odd prime powers with primes <= y.

Unlike the X-bounded twin-smooth scan (twins.py), this reaches arbitrarily
large p (towers like 2*3^b + 1) because sparse numbers are directly
enumerable. Golden primes are the cheap ones for the CLC subset-product:
few odd side-primes to assign (low conflict), and primes sharing a base
tower (e.g. 19 = 2*3^2+1, 163 = 2*3^4+1) nest inside the same modulus
prime-power for free.

Usage:
    python3 -m agrawal.golden --y 300 --pmax 1e22 --out data/golden-y300.jsonl
"""

import argparse
import time

from .harvest import Record
from .numth import is_prime
from .twins import primes_upto, save_pool


def _factor_over_full(n: int, primes: list[int]) -> dict[int, int] | None:
    """Full factorization of n over `primes` (no caps); None if a factor escapes."""
    fac = {}
    for q in primes:
        if n == 1:
            break
        e = 0
        while n % q == 0:
            n //= q
            e += 1
        if e:
            fac[q] = e
    return fac if n == 1 else None


def sparse_odd_parts(y: int, p_max: int, max_omega: int = 2):
    """All odd numbers <= p_max that are products of <= max_omega prime powers
    with primes <= y, as (value, factorization)."""
    odd_primes = [q for q in primes_upto(y) if q > 2]
    pps = []  # (value, prime, exponent)
    for q in odd_primes:
        v, b = q, 1
        while v <= p_max:
            pps.append((v, q, b))
            v *= q
            b += 1
    pps.sort()
    parts = [(1, {})]
    parts += [(v, {q: b}) for v, q, b in pps]
    if max_omega >= 2:
        for i, (v1, q1, b1) in enumerate(pps):
            if v1 * v1 > p_max:
                break
            for v2, q2, b2 in pps[i + 1 :]:
                if v1 * v2 > p_max:
                    break
                if q1 != q2:
                    parts.append((v1 * v2, {q1: b1, q2: b2}))
    if max_omega >= 3:
        raise NotImplementedError("max_omega <= 2 for now")
    return parts


def harvest_golden(y: int, p_max: int, max_omega: int = 2) -> list[Record]:
    """Primes p (y < p <= p_max) with one of p-1, p+1 sparse by construction
    and the other side fully y-smooth."""
    all_primes = primes_upto(y)
    found: dict[int, Record] = {}
    for o, ofac in sparse_odd_parts(y, p_max // 2, max_omega):
        m = 2 * o
        a = 1
        while m <= p_max:
            for delta in (1, -1):
                p = m + delta
                if p <= y or p in found or not is_prime(p):
                    continue
                # constructed side is m = p - delta; the other side is p + delta
                other = p + delta
                fac_other = _factor_over_full(other, all_primes)
                if fac_other is None:
                    continue
                fac_m = {2: a, **ofac}
                if delta == 1:  # m = p-1
                    found[p] = Record(p=p, fac_m1=fac_m, fac_p1=fac_other)
                else:  # m = p+1
                    found[p] = Record(p=p, fac_m1=fac_other, fac_p1=fac_m)
            m *= 2
            a += 1
    pool = sorted(found.values(), key=lambda r: r.p)
    return pool


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--y", type=int, default=300)
    ap.add_argument("--pmax", type=float, default=1e20)
    ap.add_argument("--max-omega", type=int, default=2)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = time.time()
    pool = harvest_golden(args.y, int(args.pmax), args.max_omega)
    save_pool(pool, args.out)
    big = sum(1 for r in pool if r.p.bit_length() > 64)
    print(
        f"y={args.y} pmax={args.pmax:.0e}: {len(pool)} golden primes "
        f"({big} above 2^64) in {time.time()-t0:.1f}s -> {args.out}",
        flush=True,
    )


if __name__ == "__main__":
    main()
