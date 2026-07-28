"""The referee: exact verification of the Agrawal congruence and of
Carmichael / Lucas-Carmichael conditions.

Agrawal's conjecture (Lenstra-Pomerance form): for coprime n, r, if
    (X - 1)^n  ≡  X^n - 1   (mod n, X^r - 1)
then n is prime or n^2 ≡ 1 (mod r).

A counterexample is a composite n with n^2 ≢ 1 (mod r) passing the congruence.
Everything the search pipeline produces must pass `is_agrawal_counterexample`
(for the full hunt) or `is_carmichael` + `is_lucas_carmichael` (milestone hunt)
before it counts.
"""

import math

from .numth import is_prime, prod


def _poly_mul_cyclic(a: list[int], b: list[int], mod: int, r: int) -> list[int]:
    """Product of polynomials a, b in Z_mod[X]/(X^r - 1)."""
    out = [0] * r
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j, bj in enumerate(b):
            if bj:
                k = i + j
                if k >= r:
                    k -= r
                out[k] += ai * bj
    return [c % mod for c in out]


def agrawal_congruence(n: int, r: int, mod: int | None = None) -> bool:
    """Exact check of (X-1)^n ≡ X^n - 1 (mod `mod`, X^r - 1), default mod = n.

    Passing mod = p for a prime factor p of squarefree n gives the per-prime
    CRT check: the congruence holds mod n iff it holds mod every prime factor.
    """
    n, r = int(n), int(r)
    if mod is None:
        mod = n
    if n < 2 or r < 2 or math.gcd(n, r) != 1 or mod < 2:
        raise ValueError("need n >= 2, r >= 2, gcd(n, r) = 1")
    # left side by binary exponentiation
    base = [0] * r
    base[0] = (-1) % mod
    base[1] = 1 % mod
    result = [0] * r
    result[0] = 1 % mod
    e = n
    while e:
        if e & 1:
            result = _poly_mul_cyclic(result, base, mod, r)
        base = _poly_mul_cyclic(base, base, mod, r)
        e >>= 1
    # right side: X^(n mod r) - 1
    expect = [0] * r
    expect[n % r] = (expect[n % r] + 1) % mod
    expect[0] = (expect[0] - 1) % mod
    return result == expect


def agrawal_congruence_crt(factors: list[int], r: int) -> bool:
    """Per-prime check for squarefree n = prod(factors); equivalent to the
    direct check but stays fast when n is enormous and factors are known."""
    n = prod(factors)
    assert len(set(factors)) == len(factors), "n must be squarefree"
    return all(agrawal_congruence(n, r, mod=p) for p in factors)


def is_agrawal_counterexample(n: int, r: int, factors: list[int] | None = None) -> bool:
    """Full counterexample check. If `factors` is given it is verified and used
    both to certify compositeness and to run the fast CRT congruence check."""
    n, r = int(n), int(r)
    if not is_prime(r) or math.gcd(n, r) != 1:
        return False
    if pow(n, 2, r) == 1:
        return False  # escape clause: not a counterexample
    if factors is not None:
        if prod(factors) != n or len(factors) < 2:
            return False
        if not all(is_prime(p) for p in factors):
            return False
        if len(set(factors)) == len(factors):
            return agrawal_congruence_crt(factors, r)
        return agrawal_congruence(n, r)
    if is_prime(n):
        return False
    return agrawal_congruence(n, r)


def _check_factored(factors: list[int]) -> int:
    assert len(factors) >= 3, "need at least 3 prime factors"
    assert len(set(factors)) == len(factors), "must be squarefree"
    assert all(is_prime(p) for p in factors), "all factors must be prime"
    return prod(factors)


def is_carmichael(factors: list[int]) -> bool:
    """Korselt: n squarefree, >= 3 prime factors, (p-1) | (n-1) for all p | n."""
    n = _check_factored(factors)
    return all((n - 1) % (p - 1) == 0 for p in factors)


def is_lucas_carmichael(factors: list[int]) -> bool:
    """n odd squarefree, >= 3 prime factors, (p+1) | (n+1) for all p | n."""
    n = _check_factored(factors)
    return n % 2 == 1 and all((n + 1) % (p + 1) == 0 for p in factors)
