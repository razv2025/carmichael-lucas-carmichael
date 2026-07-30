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

THEOREM (generic-position impossibility, every m): let s_i = (b_i - 1)/a_i
and t_i = (b_i + 1)/a_i (the C- and L-roots). If the s_i are pairwise
distinct and the t_i are pairwise distinct, no CLC family exists.
Proof: G(tau) := n(-tau) has leading coefficient c' = (-1)^m prod a_i;
G(s_i) = 1 and G(t_i) = -1 for all i. Distinctness gives the complete
factorizations G - 1 = c' prod(tau - s_i) and G + 1 = c' prod(tau - t_i);
subtracting, 2 = c'[prod(tau - t_i) - prod(tau - s_i)] identically, and the
tau^(m-1) coefficient forces sum(t_i - s_i) = sum 2/a_i = 0 — impossible
for positive a_i. QED. Moreover if only the s_i are distinct, G is already
determined as c' prod(tau - s_i) + 1, and t-distinctness would re-trigger
the contradiction — so EVERY family (any m) needs a repeated s-value or a
repeated t-value: two indices with p_j - 1 = (a_j/a_i)(p_i - 1) or
p_j + 1 = (a_j/a_i)(p_i + 1) as identities ("proportional shifted forms").
The searches below cover these degenerate strata automatically.

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


# ------------------------------------------------------- general m search


def pair_candidates(x: int, y: int, xd: set[int]) -> list[int]:
    """Possible u = a_j + D_ij values for a_i = x, a_j = y:
    u | x^(m-1) and (u - 2y) | x^(m-1) (both are factors of products equal
    to x^(m-1); xd is the signed-divisor set of x^(m-1))."""
    return [u for u in xd if u != 0 and (u - 2 * y) in xd and u != 2 * y]


def per_index_tuples(x: int, ys: tuple[int, ...], xd: set[int], pc):
    """(m-1)-tuples (u_t), u_t = a_{j_t} + D_{i j_t}, with prod u = x^(m-1)
    and prod (u - 2 y_t) = x^(m-1). pc caches pair_candidates by (x, y)."""
    target = x ** len(ys)
    cands = []
    for y in ys:
        key = (x, y)
        if key not in pc:
            pc[key] = pair_candidates(x, y, xd)
        if not pc[key]:
            return []
        cands.append(pc[key])
    out = []

    def rec(pos: int, upartial: list[int], prod_u: int):
        if pos == len(ys) - 1:
            u_last, rem = divmod(target, prod_u)
            if rem == 0 and u_last in cands[pos] :
                us = upartial + [u_last]
                v = 1
                for u, y in zip(us, ys):
                    v *= u - 2 * y
                if v == target:
                    out.append(tuple(us))
            return
        for u in cands[pos]:
            if target % (prod_u * u) == 0:
                rec(pos + 1, upartial + [u], prod_u * u)

    rec(0, [], 1)
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


def search_general(m: int, a_max: int, progress_every: int = 0):
    """Exhaustive search for general-offset m-factor families, a_i <= a_max.

    Covers ALL offset vectors b (including the degenerate proportional-form
    strata that the generic-position theorem does not exclude), because the
    per-index divisor conditions constrain D directly."""
    hits = []
    divs_cache: dict[int, set[int]] = {}
    pc: dict[tuple[int, int], list[int]] = {}
    seen = 0
    for a in combinations_with_replacement(range(1, a_max + 1), m):
        g = 0
        for v in a:
            g = gcd(g, v)
        if g != 1:
            continue
        seen += 1
        if progress_every and seen % progress_every == 0:
            print(f"  ... {seen} tuples, at a={a}", file=sys.stderr, flush=True)
        cand = []
        feasible = True
        for i in range(m):
            x = a[i]
            if x not in divs_cache:
                divs_cache[x] = set(signed_divisors_pow(x, m - 1))
            ys = tuple(a[j] for j in range(m) if j != i)
            tup = per_index_tuples(x, ys, divs_cache[x], pc)
            if not tup:
                feasible = False
                break
            cand.append(tup)
        if not feasible:
            continue
        others = [[j for j in range(m) if j != i] for i in range(m)]

        def match(i: int, D: dict):
            if i == m:
                if all(v == 0 for v in D.values()):
                    return  # degenerate (b proportional to a)
                b = realize_b(a, D)
                if b is not None:
                    hits.append((a, b))
                    print(f"FAMILY FOUND: m={m} a={a} b={b}", flush=True)
                return
            for tup in cand[i]:
                Di = {}
                ok = True
                for pos, j in enumerate(others[i]):
                    d = tup[pos] - a[j]
                    if j < i:
                        if D[(j, i)] != -d:
                            ok = False
                            break
                    else:
                        Di[(i, j)] = d
                if ok:
                    D.update(Di)
                    match(i + 1, D)
                    for key in Di:
                        del D[key]

        match(0, {})
    return hits


def search_m4(a_max: int, progress: bool = False):
    """Backward-compatible wrapper."""
    return search_general(4, a_max)


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
    ap.add_argument("--mode", choices=["m4", "pm1", "gen"], required=True)
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--amax", type=int, required=True)
    args = ap.parse_args()
    t0 = time.time()
    if args.mode == "m4":
        hits = search_general(4, args.amax, progress_every=2_000_000)
        print(f"m4 search a<={args.amax}: {len(hits)} families, "
              f"{time.time()-t0:.0f}s", flush=True)
    elif args.mode == "gen":
        hits = search_general(args.m, args.amax, progress_every=2_000_000)
        print(f"general m={args.m} search a<={args.amax}: {len(hits)} families, "
              f"{time.time()-t0:.0f}s", flush=True)
    else:
        hits = search_pm1(args.m, args.amax)
        print(f"pm1 m={args.m} search a<={args.amax}: {len(hits)} families, "
              f"{time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
