"""Shared number-theory helpers. gmpy2 when available, sympy fallback."""

import math

try:
    import gmpy2

    def is_prime(n: int) -> bool:
        # gmpy2.is_prime is BPSW + Miller-Rabin rounds; no BPSW pseudoprime is known,
        # and certainly none below the sizes we certify separately before publishing.
        return bool(gmpy2.is_prime(int(n), 25))

except ImportError:  # pragma: no cover
    import sympy

    def is_prime(n: int) -> bool:
        return bool(sympy.isprime(int(n)))


def v2(n: int) -> int:
    """2-adic valuation of n > 0."""
    return (n & -n).bit_length() - 1


def prod(xs) -> int:
    out = 1
    for x in xs:
        out *= x
    return out


def factor_over(n: int, caps: dict[int, int]) -> dict[int, int] | None:
    """Factor n using only the primes in `caps`, respecting exponent caps.

    Returns the factorization dict, or None if n has a factor outside `caps`
    or exceeds a cap. n must be positive.
    """
    fac = {}
    for q, cap in caps.items():
        if n == 1:
            break
        e = 0
        while n % q == 0:
            n //= q
            e += 1
        if e > cap:
            return None
        if e:
            fac[q] = e
    return fac if n == 1 else None


def fac_to_int(fac: dict[int, int]) -> int:
    return prod(q**e for q, e in fac.items())


def phi_from_fac(fac: dict[int, int]) -> int:
    out = 1
    for q, e in fac.items():
        out *= (q - 1) * q ** (e - 1)
    return out


def lcm_fac(facs) -> dict[int, int]:
    """lcm of factorization dicts, as a factorization dict."""
    out: dict[int, int] = {}
    for fac in facs:
        for q, e in fac.items():
            if e > out.get(q, 0):
                out[q] = e
    return out


def crt_prime_powers(residues: dict[int, int]) -> tuple[int, int]:
    """CRT for a system x ≡ r_i (mod m_i) with pairwise-coprime prime-power moduli.

    `residues` maps prime power -> residue. Returns (x, M) with 0 <= x < M.
    """
    x, m = 0, 1
    for pe, r in residues.items():
        g = math.gcd(m, pe)
        assert g == 1, f"moduli not coprime: gcd({m},{pe})={g}"
        # x' ≡ x (mod m), x' ≡ r (mod pe)
        t = ((r - x) * pow(m, -1, pe)) % pe
        x += m * t
        m *= pe
    return x % m, m
