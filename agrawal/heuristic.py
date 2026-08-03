"""Erdős–Pomerance-style density heuristic for Carmichael, CLC, and
Lenstra–Pomerance/Agrawal numbers, with an onset estimate ("first such
number expected near 10^?").

Model: numbers n <= x with k prime factors, primes near B = x^(1/k), built
from primes whose p-1 (and, two-sided, p+1) are y-smooth.

  ln E(x; k, y) = ln C(P, k)  -  ln lambda_1  [- ln lambda_2]  [+ ln F]

- P = pi(B) * rho(u)^s * gamma^s_per_prime, u = ln B / ln y, s = sides (1 or 2);
  gamma is a per-prime calibration factor fitted to true Carmichael counts.
- lambda ≈ exp(psi(y)) with prime-power correction: ln lambda ≈ y + pi(y) ln u.
- F = side-consistency probability (two-sided only): for each odd q <= y the
  chosen primes must not use q on both the p-1 and p+1 sides,
  F_q = 2(1-a)^k - (1-2a)^k with a = 1/q, plus a 2-adic branch factor 2^(1-k).
- Agrawal mode: additionally all p ≡ 3 (mod 80): extra factor 16^(-k)
  relative to the p ≡ 3 (mod 4) branch already priced into F.

Caveats: heuristic throughout; smoothness events on p-1 and p+1 treated as
independent (times the fitted gamma); lambda approximations crude. The
calibration against known Carmichael counts (Pinch: C(10^15) = 105212,
C(10^18) = 1401644) anchors the one-sided model; the two-sided model reuses
gamma^2 per prime, with a sensitivity band reported.

Usage:  python3 -m agrawal.heuristic
"""

import argparse
from math import comb, exp, inf, lgamma, log

from .twins import primes_upto

# ------------------------------------------------------------- Dickman rho

_H = 0.01
_UMAX = 120.0


def _build_rho():
    """Stable evaluation via the integral equation u*rho(u) = int_{u-1}^{u} rho."""
    n = int(_UMAX / _H) + 1
    per_unit = int(1.0 / _H)
    rho = [0.0] * n
    for i in range(n):
        u = i * _H
        if u <= 1.0:
            rho[i] = 1.0
            continue
        j0 = i - per_unit  # index of u-1 (exact: 1/H is integer)
        s = 0.5 * rho[j0]
        for j in range(j0 + 1, i):
            s += rho[j]
        # u*rho_i = H*(s + rho_i/2)  =>  rho_i = H*s / (u - H/2)
        rho[i] = _H * s / (u - 0.5 * _H)
    return rho


_RHO = _build_rho()


def ln_rho(u: float) -> float:
    """ln Dickman rho(u), linear interpolation; -inf when underflowed."""
    if u <= 1.0:
        return 0.0
    if u >= _UMAX:
        return -inf
    i = int(u / _H)
    f = u / _H - i
    v = _RHO[i] * (1 - f) + _RHO[min(i + 1, len(_RHO) - 1)] * f
    return log(v) if v > 0 else -inf


# ------------------------------------------------------- consistency factor

_QCAP = 1_000_000
_PRIMES_F = [q for q in primes_upto(100_000) if q % 2 == 1]


def ln_consistency(k: float, y: float) -> float:
    """ln F(k, y): probability the k chosen primes admit a side assignment."""
    total = (1 - k) * log(2) + log(2)  # 2-adic branch: all p = 3 or all 1 mod 4
    for q in _PRIMES_F:
        if q > y:
            return total
        a = 1.0 / q
        if k * a > 40:
            # both (1-a)^k and (1-2a)^k are ~0: F_q ~ 2(1-a)^k
            total += log(2) + k * log(1 - a)
            continue
        fq = 2 * (1 - a) ** k - (1 - 2 * a) ** k
        if fq <= 0:
            return -inf
        total += log(fq)
    # tail q in (100k, y]: ln F_q ~ -k(k-1)/q^2, sum ~ -k^2/Q
    total += -(k * k) / 100_000.0
    return total


# ----------------------------------------------------------- expected count


def ln_expected(ln_x: float, k: int, y: float, mode: str, ln_gamma: float) -> float:
    """ln E(number of mode-objects <= x with k factors, smoothness y)."""
    ln_b = ln_x / k
    if log(y) >= ln_b or y < 3 or k < 3:
        return -inf
    u = ln_b / log(y)
    sides = 1 if mode == "carmichael" else 2
    ln_pool_density = sides * (ln_rho(u) + ln_gamma)
    if ln_pool_density == -inf:
        return -inf
    ln_pi_b = ln_b - log(ln_b)  # pi(B) ~ B/ln B
    ln_pool = ln_pi_b + ln_pool_density
    if mode == "agrawal":
        ln_pool -= log(16)  # p ≡ 3 (mod 80) within the p ≡ 3 (mod 4) branch
    if ln_pool < log(k) + 1:  # need pool comfortably >= k
        return -inf
    # ln C(P, k) ~ k ln P - ln k!
    ln_choose = k * ln_pool - lgamma(k + 1)
    # lambda: lcm of the p-+1 systems, ln ~ psi(y) + prime-power correction,
    # capped by the trivial bound prod(p_i) ~ x
    ln_lam = min(y + (y / log(y)) * log(max(u, 1.0)), k * ln_b)
    total = ln_choose - sides * ln_lam
    if sides == 2:
        total += ln_consistency(float(k), y)
    return total


def best_ln_expected(ln_x: float, mode: str, ln_gamma: float):
    """max over (k, y) of ln E; returns (value, k, y)."""
    best = (-inf, None, None)
    k = 3
    ks = []
    while k < 3.2e5:
        ks.append(int(k))
        k *= 1.35
    for k in ks:
        ln_b = ln_x / k
        if ln_b < log(3) * 1.5:
            break
        y = 8.0
        while log(y) < ln_b * 0.95 and y < 5e5:
            v = ln_expected(ln_x, k, y, mode, ln_gamma)
            if v > best[0]:
                best = (v, k, y)
            y *= 1.3
    return best


def onset(mode: str, ln_gamma: float, lo: float = 8.0, hi: float = 30000.0):
    """Smallest ln x with best_ln_expected >= 0 (binary search)."""
    if best_ln_expected(hi, mode, ln_gamma)[0] < 0:
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if best_ln_expected(mid, mode, ln_gamma)[0] >= 0:
            hi = mid
        else:
            lo = mid
    return hi


def calibrate_two_sided() -> float:
    """Fit the per-prime two-sided ln(gamma) directly against this repo's
    measured twin-smooth prime counts (harvest_twins), rather than assuming
    independence of the p-1 and p+1 smoothness events."""
    # (y, X, measured count of primes <= X with p-+1 both y-smooth)
    anchors = [(60, 1e9, 670), (100, 1e9, 2534), (140, 2e9, 7727),
               (200, 1e10, 25660)]
    vals = []
    for y, x, cnt in anchors:
        ln_b = log(x)
        u = ln_b / log(y)
        ln_pi = ln_b - log(ln_b)
        vals.append((log(cnt) - ln_pi - 2 * ln_rho(u)) / 2)
    return sum(vals) / len(vals)


def calibrate() -> float:
    """Fit per-prime ln(gamma) so the one-sided model matches Pinch's
    Carmichael counts at 10^15 and 10^18."""
    anchors = [(15 * log(10), log(105212)), (18 * log(10), log(1401644))]
    lo, hi = -3.0, 3.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        err = sum(best_ln_expected(lx, "carmichael", mid)[0] - t
                  for lx, t in anchors)
        if err > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-calibration", action="store_true")
    args = ap.parse_args()
    if args.skip_calibration:
        lg = 0.0
    else:
        lg = calibrate()
        print(f"calibrated per-prime ln(gamma) = {lg:+.3f} "
              f"(gamma = {exp(lg):.3f})")
        for lx, truth in [(15, 105212), (18, 1401644)]:
            v, k, y = best_ln_expected(lx * log(10), "carmichael", lg)
            print(f"  check x=1e{lx}: model ln count {v:.1f} "
                  f"vs true {log(truth):.1f} (k*={k}, y*={y:.0f})")
    lg2 = calibrate_two_sided()
    print(f"two-sided per-prime ln(gamma) from measured twin-smooth counts: "
          f"{lg2:+.3f} (gamma = {exp(lg2):.3f})")
    v18 = best_ln_expected(18 * log(10), "clc", lg2)[0]
    print(f"reality check: model ln E(CLC <= 1e18) = {v18:+.1f} "
          f"(truth: zero CLC numbers exist below 1e18)")
    # strongest defensible calibration: largest gamma consistent with
    # E(CLC <= 1e18) <= 1
    lo, hi = 0.0, lg2
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if best_ln_expected(18 * log(10), "clc", mid)[0] > 0:
            hi = mid
        else:
            lo = mid
    lg_cons = 0.5 * (lo + hi)
    print(f"largest gamma consistent with that emptiness: "
          f"ln_gamma = {lg_cons:+.3f} (gamma = {exp(lg_cons):.3f})")
    print()
    for mode, lgm in [("carmichael", lg), ("clc", lg_cons), ("clc", lg2),
                      ("agrawal", lg_cons), ("agrawal", lg2)]:
        o = onset(mode, lgm)
        if o is None:
            print(f"{mode:10s} (ln_gamma={lgm:+.2f}): no onset below 1e13000")
            continue
        digits = o / log(10)
        v, k, y = best_ln_expected(o * 1.05, mode, lgm)
        print(f"{mode:10s} (ln_gamma={lgm:+.2f}): first expected near "
              f"10^{digits:,.0f}   (k* ~ {k}, y* ~ {y:.0f})")


if __name__ == "__main__":
    main()
