"""Subset-product solver.

Given a harvested pool, we impose the sufficient global condition
    n ≡ 1 (mod M1),  n ≡ -1 (mod M2)
where M1 = lcm(p-1), M2 = lcm(p+1) over the pool (M2 absent in plain-Carmichael
mode). gcd(M1, M2) = 2 by construction (all pool primes ≡ 3 mod 4, sides use
disjoint odd primes), and 1 ≡ -1 (mod 2), so the target residue t mod
M = lcm(M1, M2) exists. Any subset with product ≡ t (mod M) and >= 3 elements
is a hit; hits are re-verified exactly by verify.py.

Solver: meet-in-the-middle over the pool (Gray-code enumeration on the right
half, hash table on the left half). Practical up to ~44 pool primes; larger
pools go through `greedy_subpool` first. A Wagner k-list solver is the planned
upgrade for pools where N far exceeds log2 phi(M).
"""

import time
from math import log2

from .harvest import Record
from .numth import crt_prime_powers, fac_to_int, lcm_fac, phi_from_fac
from .verify import is_carmichael, is_lucas_carmichael


def build_system(pool: list[Record]) -> tuple[int, int, dict]:
    """Returns (M, t, stats). t is the required residue of n mod M."""
    m1_fac = lcm_fac(r.fac_m1 for r in pool)
    clc_mode = pool[0].fac_p1 is not None
    if clc_mode:
        assert all(r.fac_p1 is not None for r in pool)
        m2_fac = lcm_fac(r.fac_p1 for r in pool)
        assert m1_fac.get(2) == 1, "pool must be all p ≡ 3 (mod 4)"
        shared = set(m1_fac) & set(m2_fac) - {2}
        assert not shared, f"sides share odd primes {shared}"
        m_fac = lcm_fac([m1_fac, m2_fac])
        residues = {}
        for q, e in m_fac.items():
            if q == 2:
                residues[2**e] = (2**e) - 1  # n ≡ -1 mod 2-part (from M2 side)
            elif q in m1_fac:
                residues[q**e] = 1
            else:
                residues[q**e] = q**e - 1
    else:
        m_fac = m1_fac
        residues = {q**e: 1 for q, e in m_fac.items()}
    t, M = crt_prime_powers(residues)
    stats = {
        "pool_size": len(pool),
        "log2_phi_M": log2(phi_from_fac(m_fac)),
        "log2_M": log2(fac_to_int(m_fac)),
        "clc_mode": clc_mode,
        "margin": len(pool) - log2(phi_from_fac(m_fac)),
    }
    return M, t, stats


def greedy_subpool(pool: list[Record], max_n: int = 44) -> list[Record]:
    """Pick up to max_n records greedily minimizing lcm growth, maximizing the
    margin  |subpool| - log2 phi(lcm)  along the way; returns the best prefix."""
    remaining = list(pool)
    chosen: list[Record] = []
    cur_fac: dict[int, int] = {}
    best_margin, best_len = float("-inf"), 0
    while remaining and len(chosen) < max_n:
        def added_bits(r: Record) -> float:
            facs = [cur_fac, r.fac_m1] + ([r.fac_p1] if r.fac_p1 else [])
            return log2(phi_from_fac(lcm_fac(facs)) or 1)
        nxt = min(remaining, key=added_bits)
        remaining.remove(nxt)
        chosen.append(nxt)
        cur_fac = lcm_fac(
            [cur_fac, nxt.fac_m1] + ([nxt.fac_p1] if nxt.fac_p1 else [])
        )
        margin = len(chosen) - log2(phi_from_fac(cur_fac))
        # only apply the margin cutoff once the subpool can actually form
        # k >= 3 subsets in volume; tiny subpools are useless regardless of margin
        if len(chosen) >= 6 and margin >= best_margin:
            best_margin, best_len = margin, len(chosen)
    if best_len == 0:
        return chosen
    return chosen[:best_len]


def _enumerate_products(primes: list[int], M: int):
    """dict: subset-product mod M -> list of bitmasks (all 2^len subsets)."""
    table: dict[int, list[int]] = {1: [0]}
    prods = [1]
    for i, p in enumerate(primes):
        pm = p % M
        new = []
        for mask, val in enumerate(prods):
            nv = (val * pm) % M
            new.append(nv)
            table.setdefault(nv, []).append(mask | (1 << i))
        prods.extend(new)
    return table, prods


def mitm_search(
    pool: list[Record],
    max_hits: int = 25,
    left_size: int | None = None,
    time_limit: float | None = None,
    verbose: bool = False,
    system: tuple[int, int] | None = None,
):
    """Meet-in-the-middle subset-product search. Yields verified hits as dicts.

    `system` = (M, t) overrides the default modulus/target construction (used
    by split.py, whose splits build their own residue systems)."""
    if not pool:
        return
    if system is not None:
        M, t = system
    else:
        M, t, _stats = build_system(pool)
    n_pool = len(pool)
    if left_size is None:
        left_size = min(n_pool // 2, 21)
    left = pool[:left_size]
    right = pool[left_size:]
    if len(right) > 26:
        raise ValueError(
            f"right half 2^{len(right)} too large; reduce pool (greedy_subpool)"
        )
    left_table, _ = _enumerate_products([r.p for r in left], M)

    right_primes = [r.p % M for r in right]
    right_invs = [pow(pm, -1, M) for pm in right_primes]
    # Gray-code walk over right subsets
    cur = 1
    mask = 0
    t0 = time.time()
    hits = 0
    total = 1 << len(right)
    for g in range(total):
        if g:
            bit = (g & -g).bit_length() - 1
            if mask >> bit & 1:
                cur = (cur * right_invs[bit]) % M
            else:
                cur = (cur * right_primes[bit]) % M
            mask ^= 1 << bit
        # need left product L with L * cur ≡ t (mod M)
        need = (t * pow(cur, -1, M)) % M
        for lmask in left_table.get(need, ()):
            k = bin(lmask).count("1") + bin(mask).count("1")
            if k < 3:
                continue
            primes = [left[i].p for i in range(len(left)) if lmask >> i & 1] + [
                right[i].p for i in range(len(right)) if mask >> i & 1
            ]
            clc = pool[0].fac_p1 is not None
            ok_c = is_carmichael(primes)
            ok_lc = is_lucas_carmichael(primes) if clc else None
            n = 1
            for p in primes:
                n *= p
            hit = {
                "n_digits": len(str(n)),
                "k": k,
                "primes": primes,
                "n": n,
                "carmichael": ok_c,
                "lucas_carmichael": ok_lc,
                "verified": ok_c and (ok_lc is not False),
            }
            if verbose:
                print(f"hit: k={k}, {hit['n_digits']} digits, "
                      f"carmichael={ok_c}, lucas_carmichael={ok_lc}")
            yield hit
            hits += 1
            if hits >= max_hits:
                return
        if time_limit is not None and g % 65536 == 0 and time.time() - t0 > time_limit:
            return
