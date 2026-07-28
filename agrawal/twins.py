"""Twin-smooth prime harvesting.

A pool prime for the CLC hunt needs BOTH p-1 and p+1 y-smooth. Equivalently:
m = p-1 and m+2 = p+1 are a twin pair of y-smooth numbers with a prime between
them. We enumerate all y-smooth numbers <= X (sparse), intersect with their
shift by 2, and primality-test the midpoints. The harvested pool is cached as
JSONL and re-split many ways by split.py without re-harvesting.

Usage:
    python3 -m agrawal.twins --y 100 --xmax 1e9 --out data/twins-y100-1e9.jsonl
"""

import argparse
import json
import time
from array import array
from bisect import bisect_left
from pathlib import Path

from .harvest import Record
from .numth import is_prime


def primes_upto(y: int) -> list[int]:
    sieve = bytearray([1]) * (y + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(y**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i in range(2, y + 1) if sieve[i]]


def smooth_numbers(y: int, x_max: int) -> array:
    """Sorted array of all y-smooth integers in [1, x_max]."""
    ps = primes_upto(y)
    out = array("q")

    def rec(i: int, val: int):
        out.append(val)
        for j in range(i, len(ps)):
            v = val * ps[j]
            if v > x_max:
                # primes are sorted; larger ones only overshoot further
                if ps[j] * val > x_max:
                    break
            else:
                rec(j, v)

    rec(0, 1)
    out = array("q", sorted(out))
    return out


def factor_smooth(n: int, ps: list[int]) -> dict[int, int]:
    fac = {}
    for q in ps:
        if n == 1:
            break
        e = 0
        while n % q == 0:
            n //= q
            e += 1
        if e:
            fac[q] = e
    assert n == 1, "not smooth over the given primes"
    return fac


def harvest_twins(y: int, x_max: int) -> list[Record]:
    """All primes p <= x_max - 1 with p-1 and p+1 both y-smooth, p > y."""
    ps = primes_upto(y)
    sm = smooth_numbers(y, x_max)
    pool = []
    n = len(sm)
    for m in sm:
        if m % 2:
            continue  # p = m+1 must be odd, so m is even
        i = bisect_left(sm, m + 2)
        if i >= n or sm[i] != m + 2:
            continue
        p = m + 1
        if p <= y or not is_prime(p):
            continue
        pool.append(
            Record(p=p, fac_m1=factor_smooth(m, ps), fac_p1=factor_smooth(m + 2, ps))
        )
    return pool


def save_pool(pool: list[Record], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in pool:
            f.write(
                json.dumps(
                    {
                        "p": r.p,
                        "m1": {str(k): v for k, v in r.fac_m1.items()},
                        "p1": {str(k): v for k, v in r.fac_p1.items()},
                    }
                )
                + "\n"
            )


def load_pool(path: str | Path) -> list[Record]:
    pool = []
    with Path(path).open() as f:
        for line in f:
            d = json.loads(line)
            pool.append(
                Record(
                    p=d["p"],
                    fac_m1={int(k): v for k, v in d["m1"].items()},
                    fac_p1={int(k): v for k, v in d["p1"].items()},
                )
            )
    return pool


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--y", type=int, required=True)
    ap.add_argument("--xmax", type=float, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = time.time()
    pool = harvest_twins(args.y, int(args.xmax))
    save_pool(pool, args.out)
    print(
        f"y={args.y} xmax={args.xmax:.0e}: {len(pool)} twin-smooth primes "
        f"in {time.time()-t0:.1f}s -> {args.out}",
        flush=True,
    )


if __name__ == "__main__":
    main()
