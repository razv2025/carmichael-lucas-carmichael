"""Chernick-style parametric families for Carmichael + Lucas-Carmichael numbers.

Ansatz: n(k) = prod_i (a_i k + b_i), m factors, a_i > 0. Requiring the
polynomial-root conditions
    (p_i - 1) | (n - 1):  n((1-b_i)/a_i) = 1
    (p_i + 1) | (n + 1):  n((-1-b_i)/a_i) = -1
and writing D_ij = a_i b_j - a_j b_i gives, for every i:

    C_i:  prod_{j != i} (a_j + D_ij) = a_i^(m-1)
    L_i:  prod_{j != i} (D_ij - a_j) = a_i^(m-1)

plus realizability of D as a wedge a ∧ b (b integers up to k-translation).

THEOREM (m = 3): no nondegenerate family exists. Proof: C_i - L_i expansions
give a_2 D_13 = -a_3 D_12, a_1 D_23 = a_3 D_12, a_1 D_23 = -a_2 D_13; the
rank identity D_23 a_1 - D_13 a_2 + D_12 a_3 = 0 then forces 3 a_3 D_12 = 0,
hence D = 0, hence b proportional to a (degenerate: p_i = a_i k' with no
constant term, never simultaneously prime beyond k' = 1).

Special case b_i = -1 for all i ("all-minus", m odd): D_ij = a_j - a_i and
both conditions reduce to prod_{j != i} (2 a_j - a_i) = a_i^(m-1).

THEOREM (uniform-sign impossibility, every m): the all-minus system
prod_{j != i} (2 a_j - a_i) = a_i^(m-1) and the all-plus system
prod_{j != i} (a_i - 2 a_j) = a_i^(m-1) have no solutions in distinct
positive integers. Proof: take i with a_i = max_j a_j. For every j != i,
0 < a_j < a_i gives -a_i < 2 a_j - a_i < a_i, so |2 a_j - a_i| < a_i
strictly; hence |prod_{j != i} (2 a_j - a_i)| < a_i^(m-1). Same bound for
a_i - 2 a_j. QED. (The searches below over these systems serve as
independent verification of the algebra.)

Key pruning fact: each factor of a product equal to a_i^(m-1) divides
a_i^(m-1), so all candidate factors live among signed divisors of a_i^(m-1).

Usage:
    python3 -m agrawal.family --mode m4 --amax 60
    python3 -m agrawal.family --mode pm1 --m 5 --amax 400
"""

import argparse
import sys
import time
from itertools import combinations_with_replacement
from math import gcd, isqrt

from .numth import is_prime, prod
from .verify import is_carmichael, is_lucas_carmichael


def signed_divisors(n: int) -> list[int]:
    n = abs(n)
    small = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            small.append(d)
            if d * d != n:
                small.append(n // d)
    return sorted(small + [-d for d in small])


def signed_divisors_pow(x: int, e: int) -> list[int]:
    """Signed divisors of x^e, generated from the factorization of x —
    O(number of divisors), never trial-dividing the (huge) power itself."""
    fac = {}
    n = x
    d = 2
    while d * d <= n:
        while n % d == 0:
            fac[d] = fac.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    divs = [1]
    for q, a in fac.items():
        divs = [dv * q**i for dv in divs for i in range(a * e + 1)]
    return sorted(divs + [-dv for dv in divs])


# ---------------------------------------------------------------- m = 4 general


def pair_candidates(x: int, y: int, x3_divs: set[int]) -> list[int]:
    """Possible u = a_j + D_ij values for a_i = x, a_j = y:
    u | x^3 and (u - 2y) | x^3 (both factors of products equal to x^3)."""
    return [u for u in x3_divs if u != 0 and (u - 2 * y) in x3_divs and u != 2 * y]


def per_index_triples(x: int, ys: tuple[int, int, int], x3_divs: set[int]):
    """Triples (u_1, u_2, u_3), u_t = a_{j_t} + D_{i j_t}, with
    prod u = x^3 and prod (u - 2 y_t) = x^3."""
    target = x**3
    c0 = pair_candidates(x, ys[0], x3_divs)
    c1 = pair_candidates(x, ys[1], x3_divs)
    out = []
    for u0 in c0:
        for u1 in c1:
            r, rem = divmod(target, u0 * u1)
            if rem:
                continue
            u2 = r
            if u2 not in x3_divs or u2 == 2 * ys[2]:
                continue
            if (u0 - 2 * ys[0]) * (u1 - 2 * ys[1]) * (u2 - 2 * ys[2]) == target:
                out.append((u0, u1, u2))
    return out


def realize_b(a: tuple[int, ...], D: dict[tuple[int, int], int]):
    """Find integer b with D_ij = a_i b_j - a_j b_i, using k-translation
    freedom (b_1 ranges mod a_1). Returns b or None."""
    m = len(a)
    for beta in range(a[0]):
        b = [beta]
        ok = True
        for j in range(1, m):
            num = D[(0, j)] + a[j] * beta
            if num % a[0]:
                ok = False
                break
            b.append(num // a[0])
        if not ok:
            continue
        if all(
            a[i] * b[j] - a[j] * b[i] == D[(i, j)]
            for i in range(m)
            for j in range(i + 1, m)
        ):
            return tuple(b)
    return None


def search_m4(a_max: int, progress: bool = False):
    """Exhaustive search for m = 4 general-offset families with a_i <= a_max."""
    hits = []
    divs_cache: dict[int, set[int]] = {}
    for a in combinations_with_replacement(range(1, a_max + 1), 4):
        if gcd(gcd(a[0], a[1]), gcd(a[2], a[3])) != 1:
            continue
        cand = []
        feasible = True
        for i in range(4):
            x = a[i]
            if x not in divs_cache:
                divs_cache[x] = set(signed_divisors_pow(x, 3))
            ys = tuple(a[j] for j in range(4) if j != i)
            tri = per_index_triples(x, ys, divs_cache[x])
            if not tri:
                feasible = False
                break
            cand.append(tri)
        if not feasible:
            continue
        others = [[j for j in range(4) if j != i] for i in range(4)]
        # match antisymmetric D across the four index-local triples
        for t0 in cand[0]:
            D = {}
            for pos, j in enumerate(others[0]):
                D[(0, j)] = t0[pos] - a[j]
            for t1 in cand[1]:
                D1 = {}
                for pos, j in enumerate(others[1]):
                    D1[(1, j)] = t1[pos] - a[j]
                if D1[(1, 0)] != -D[(0, 1)]:
                    continue
                for t2 in cand[2]:
                    D2 = {}
                    for pos, j in enumerate(others[2]):
                        D2[(2, j)] = t2[pos] - a[j]
                    if D2[(2, 0)] != -D[(0, 2)] or D2[(2, 1)] != -D1[(1, 2)]:
                        continue
                    for t3 in cand[3]:
                        D3 = {}
                        for pos, j in enumerate(others[3]):
                            D3[(3, j)] = t3[pos] - a[j]
                        if (
                            D3[(3, 0)] != -D[(0, 3)]
                            or D3[(3, 1)] != -D1[(1, 3)]
                            or D3[(3, 2)] != -D2[(2, 3)]
                        ):
                            continue
                        full = {
                            (0, 1): D[(0, 1)],
                            (0, 2): D[(0, 2)],
                            (0, 3): D[(0, 3)],
                            (1, 2): D1[(1, 2)],
                            (1, 3): D1[(1, 3)],
                            (2, 3): D2[(2, 3)],
                        }
                        if all(v == 0 for v in full.values()):
                            continue  # degenerate (b || a)
                        b = realize_b(a, full)
                        if b is not None:
                            hits.append((a, b))
                            print(f"FAMILY FOUND: a={a} b={b}", flush=True)
        if progress and a[0] == a[1] == a[2] == 1:
            print(f"  ... a={a}", file=sys.stderr, flush=True)
    return hits


# ------------------------------------------------------------- all-minus, odd m


def search_pm1(m: int, a_max: int):
    """Search prod_{j != i} (2 a_j - a_i) = a_i^(m-1) for all i (b_i = -1,
    m odd). Partner pruning: 2 a_j - a_i must be a signed divisor of a_i^(m-1)."""
    assert m % 2 == 1
    partner: dict[int, set[int]] = {}
    for x in range(1, a_max + 1):
        s = set()
        for d in signed_divisors_pow(x, m - 1):
            if (d + x) % 2 == 0:
                y = (d + x) // 2
                if 1 <= y <= a_max and y != x:
                    s.add(y)
        partner[x] = s

    hits = []

    def extend(chosen: list[int], allowed: set[int]):
        if len(chosen) == m:
            if all(
                prod(2 * y - x for y in chosen if y != x) == x ** (m - 1)
                for x in chosen
            ):
                hits.append(tuple(chosen))
                print(f"ALL-MINUS FAMILY: a={tuple(chosen)}", flush=True)
            return
        start = chosen[-1] + 1 if chosen else 1
        for y in sorted(v for v in allowed if v >= start):
            extend(chosen + [y], allowed & partner[y])

    for x in range(1, a_max + 1):
        extend([x], set(partner[x]))
    return hits


# --------------------------------------------------------------- instantiation


def instantiate(a, b, k_max: int, k_min: int = 1):
    """Scan k for prime values of every a_i k + b_i; exact-verify CLC."""
    for k in range(k_min, k_max + 1):
        ps = [ai * k + bi for ai, bi in zip(a, b)]
        if len(set(ps)) != len(ps) or any(p < 3 for p in ps):
            continue
        if not all(is_prime(p) for p in ps):
            continue
        if is_carmichael(ps) and is_lucas_carmichael(ps):
            yield k, ps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["m4", "pm1"], required=True)
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--amax", type=int, required=True)
    args = ap.parse_args()
    t0 = time.time()
    if args.mode == "m4":
        hits = search_m4(args.amax)
        print(f"m4 search a<={args.amax}: {len(hits)} families, "
              f"{time.time()-t0:.0f}s", flush=True)
    else:
        hits = search_pm1(args.m, args.amax)
        print(f"pm1 m={args.m} search a<={args.amax}: {len(hits)} families, "
              f"{time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
