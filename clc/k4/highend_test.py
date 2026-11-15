#!/usr/bin/env python3
"""Independent big-integer cross-check of enum_k4.c's per-pair arithmetic where L2 = (p2^2-1)/2 exceeds 2^63.

For sampled admissible pairs (p1, p2) the C routine do_pair() (driven by highend_test.c) must agree with this file on:
  * whether the pair is consistent (p1 ≡ p2 mod gcd(L1,L2)),
  * the CRT class  m ≡ m0 (mod Lam)  of  p2 m ≡ 1 (mod L1),  p1 m ≡ 1 (mod L2),
  * the number of class members in (p2^2, 4P^2)  [single-sweep walk],
  * the exact list of window survivors, in both walk modes (single sweep and production two-sweep walk).
Nothing here shares code with the C program; Python integers are unbounded.
Usage: python3 highend_test.py [--pairs N] [--seed S]      exit status 0 iff everything agrees."""
import argparse, math, random, subprocess, sys
from sympy import isprime, nextprime, prevprime

def adm_near(x, direction):
    p = x
    while True:
        p = nextprime(p) if direction > 0 else prevprime(p)
        if p % 12 == 1: return p

def window(T, m, p1):
    """exists integer j >= 1 with |j m - T| <= max(2 j S, 8 p1), S = ceil(sqrt(2 p1)) — tested on a generous j range"""
    S = math.isqrt(2*p1); S += S*S < 2*p1
    j0 = T // m
    return any(abs(j*m - T) <= max(2*j*S, 8*p1) for j in range(max(1, j0 - 3), j0 + 5))

def reference(p1, p2, forced=()):
    L1, L2 = (p1*p1 - 1)//2, (p2*p2 - 1)//2
    g = math.gcd(L1, L2)
    if (p2 - p1) % g: return dict(skip=1)
    Lam = L1*L2//g
    # brute CRT, independent of the C formula: m = a1 + L1 k with a1 = p2^{-1} mod L1, solve for k mod L2/g
    a1 = pow(p2, -1, L1); a2 = pow(p1, -1, L2)
    k = ((a2 - a1)//g * pow(L1//g, -1, L2//g)) % (L2//g) if L2//g > 1 else 0
    m0 = a1 + L1*k
    assert (p2*m0 - 1) % L1 == 0 and (p1*m0 - 1) % L2 == 0 and 0 <= m0 < Lam
    P = p1*p2; T = 4*P*P; lo, hi = p2*p2 + 1, T - 1
    first = m0 + max(0, -(-(lo - m0)//Lam))*Lam
    ms = range(first, hi + 1, Lam)
    return dict(skip=0, m0=m0, Lam=Lam, cand=len(ms), W=sorted(m for m in ms if window(T, m, p1)), L2=L2)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pairs', type=int, default=20000); ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args(); rnd = random.Random(a.seed)
    pairs = set()
    # corner cases: largest p1 ≤ 10^6 with the largest admissible p2 ≤ sqrt(24 p1^3 + 3), and the first p2 past 2^32
    top = adm_near(10**6, -1)
    for p1 in (top, adm_near(top, -1), adm_near(915_000, +1), adm_near(957_000, +1)):
        cap = math.isqrt(24*p1**3 + 3)
        p = cap + 1
        for _ in range(40): p = adm_near(p, -1); pairs.add((p1, p))
        p = 2**32
        for _ in range(40):
            p = adm_near(p, +1)
            if p <= cap: pairs.add((p1, p))
    while len(pairs) < a.pairs:
        p1 = adm_near(rnd.randrange(917_000, 10**6), -1)
        cap = math.isqrt(24*p1**3 + 3)
        p2 = adm_near(rnd.randrange(2**32, cap), -1)
        if p2 > 2**32: pairs.add((p1, p2))
    pairs = sorted(pairs)
    inp = "".join(f"{a_} {b_}\n" for a_, b_ in pairs)
    bad = 0; stats = dict(pairs=len(pairs), skipped=0, L2_ge_2_63=0, cand=0, W=0, maxL2bits=0)
    for mode in ([], ['--oldwalk']):
        out = subprocess.run(['./highend_test'] + mode, input=inp, capture_output=True, text=True, check=True).stdout
        got = {}
        for line in out.split('\n'):
            t = line.split()
            if not t: continue
            key = (int(t[1]), int(t[2])); d = got.setdefault(key, dict(W=[]))
            if t[0] == 'TRACE': d['m0'], d['Lam'] = int(t[3]), int(t[4])
            elif t[0] == 'W': d['W'].append(int(t[3]))
            elif t[0] == 'PAIR': d['skip_g'], d['skip_inv'], d['cand'] = int(t[3]), int(t[4]), int(t[5])
            elif t[0] == 'WSURV': pass
            else: print("unexpected line:", line); bad += 1
        for pq in pairs:
            ref = reference(*pq); c = got.get(pq)
            if c is None or 'cand' not in c: print("missing", pq); bad += 1; continue
            if ref['skip']:
                ok = c['skip_g'] == 1 and 'm0' not in c
            else:
                ok = (c['skip_g'] == 0 and c['skip_inv'] == 0 and c.get('m0') == ref['m0'] and c.get('Lam') == ref['Lam']
                      and sorted(c['W']) == ref['W'] and (not mode or c['cand'] == ref['cand']))
            if not ok: bad += 1; print("MISMATCH", mode, pq, {k: v for k, v in ref.items()}, c)
            if not mode:
                stats['skipped'] += ref['skip']
                if not ref['skip']:
                    stats['cand'] += ref['cand']; stats['W'] += len(ref['W'])
                    stats['L2_ge_2_63'] += ref['L2'] >= 2**63; stats['maxL2bits'] = max(stats['maxL2bits'], ref['L2'].bit_length())
    print(f"HIGHEND: {stats}  mismatches={bad}")
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
