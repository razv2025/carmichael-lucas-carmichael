"""Heuristic expected number of four-prime Carmichael–Lucas–Carmichael numbers (paper, §6).

Model: condition on Theorem A(a) (all primes ≡ 1 mod 12). For such p the condition n/p ≡ 1 (mod (p²−1)/2)
is automatic modulo 12, so treat the remaining condition as an independent event of probability 24/p².
Sum ∏ 24/p_i² over primes p1 < p2 < q < r, all ≡ 1 (mod 12), subject to Theorem A: p2² ≤ 24 p1³ + 1 and
p2 < q < r < 2 p1 p2.  Exact prime sums via a sieve; p1 ranges over primes ≤ P1MAX (default 1000; the
tail decays like p1^-4).

    python3 -m agrawal.k4_heuristic [P1MAX]
"""
import bisect, math, sys


def primes_upto(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if sieve[i]]


def main(p1max=1000):
    p2max = math.isqrt(24 * p1max**3 + 1)
    limit = 2 * p1max * p2max                       # largest r considered
    pr = [p for p in primes_upto(limit) if p % 12 == 1]
    inv2 = [1.0 / (p * p) for p in pr]
    pref = [0.0]
    for v in inv2:
        pref.append(pref[-1] + v)
    pref2 = [0.0]                                    # prefix sums of 1/p^4, to remove the q = r diagonal
    for v in inv2:
        pref2.append(pref2[-1] + v * v)

    def seg(lo, hi):   # sums over primes p ≡ 1 (12) with lo < p < hi
        i = bisect.bisect_right(pr, lo); j = bisect.bisect_left(pr, hi)
        return pref[j] - pref[i], pref2[j] - pref2[i]

    total = 0.0; by_p1 = {}
    for p1 in pr:
        if p1 > p1max:
            break
        e1 = 0.0
        for p2 in pr:
            if p2 <= p1:
                continue
            if p2 * p2 > 24 * p1**3 + 1:
                break
            s1, s2 = seg(p2, 2 * p1 * p2)
            pairs = (s1 * s1 - s2) / 2              # ordered pairs q < r
            e1 += 24**4 / (p1 * p1 * p2 * p2) * pairs
        by_p1[p1] = e1; total += e1
    print(f"p1 <= {p1max}: expected number of four-prime CLC numbers = {total:.4g}")
    for p1 in list(by_p1)[:4]:
        print(f"  p1 = {p1:4d}: {by_p1[p1]:.4g}  ({100*by_p1[p1]/total:.1f}%)")
    last = max(by_p1); print(f"  last p1 = {last}: {by_p1[last]:.3g}; tail beyond p1max ~ {by_p1[last]*last/3:.2g} (p1^-4 decay)")
    return total, by_p1


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
