#!/usr/bin/env python3
"""Independent exact verification of lines produced by enum_k4 (SOLUTION / FSURV).

For every SOLUTION line: re-derive n from the four primes, check primality (sympy),
and check n/p ≡ 1 (mod (p^2-1)/kappa) for each p.  For kappa = 2 also check the
textbook definitions: (p-1) | (n-1) and (p+1) | (n+1), i.e. Carmichael AND Lucas–Carmichael.
For every FSURV line (a window survivor that is a base-2 Fermat pseudoprime): factor m
and report whether n is CLC at all (it should not be unless a SOLUTION line follows).
Usage: python3 verify_k4.py SOLFILE..."""
import sys, re
from sympy import isprime, factorint

def check(kappa, ps):
    """Exact check of the tuple AS GIVEN (no sorting, no de-duplication): strictly increasing distinct primes,
    and n/p ≡ 1 (mod (p^2-1)/kappa) for each p; for kappa = 2 also the textbook divisibilities."""
    if len(ps) != 4 or any(ps[i] >= ps[i+1] for i in range(3)):
        return 0, False
    n = 1
    for p in ps: n *= p
    ok = all(isprime(p) for p in ps)
    ok &= all(((n // p) - 1) % ((p*p - 1) // kappa) == 0 for p in ps)
    if kappa == 2:
        ok &= all((n - 1) % (p - 1) == 0 and (n + 1) % (p + 1) == 0 for p in ps)
    return n, ok

def main(paths):
    bad = 0; nsol = 0; nfs = 0; nws = 0
    for path in paths:
        for line in open(path):
            kv = dict(re.findall(r'(\w+)=(\d+)', line))
            if line.startswith('SOLUTION'):
                nsol += 1
                kappa = int(kv['kappa']); ps = [int(kv[k]) for k in ('p1','p2','q','r')]
                n, ok = check(kappa, ps)
                print(('OK  ' if ok else 'BAD ') + f"n={n} = {'*'.join(map(str,ps))} kappa={kappa}" + ('' if n == int(kv['n']) else '  (n mismatch!)'))
                bad += (not ok) or n != int(kv['n'])
            elif line.startswith('W '):
                nws += 1
                p1, p2, m = (int(x) for x in line.split()[1:4])
                n = p1 * p2 * m
                if pow(2, n - 1, n) != 1: continue
                nfs += 1
                f = factorint(m); qr = sorted(f)
                clc = len(f) == 2 and all(e == 1 for e in f.values()) and qr[0] > p2 and check(2, [p1, p2, qr[0], qr[1]])[1]
                print(f"W passed Fermat: p1={p1} p2={p2} m={m} = {f}  -> {'CLC!!' if clc else 'not CLC'}")
                bad += clc
            elif line.startswith('WSURV'):
                # window survivor handed over from C (n too large for 128-bit arithmetic): Fermat first, then exact
                nws += 1
                p1, p2, m = (int(kv[k]) for k in ('p1','p2','m'))
                n = p1 * p2 * m
                if pow(2, n - 1, n) != 1: continue
                nfs += 1
                f = factorint(m)
                qr = sorted(f)
                clc = len(f) == 2 and all(e == 1 for e in f.values()) and qr[0] > p2 and check(2, [p1, p2, qr[0], qr[1]])[1]
                print(f"WSURV passed Fermat: p1={p1} p2={p2} m={m} = {f}  -> {'CLC!!' if clc else 'not CLC'}")
                bad += clc
            elif line.startswith('FSURV'):
                nfs += 1
                p1, p2, m, n = (int(kv[k]) for k in ('p1','p2','m','n'))
                f = factorint(m)
                qr = sorted(f)
                clc = len(f) == 2 and all(e == 1 for e in f.values()) and qr[0] > p2 and check(2, [p1, p2, qr[0], qr[1]])[1]
                print(f"FSURV p1={p1} p2={p2} m={m} = {f}  -> {'CLC!!' if clc else 'not CLC'}")
                bad += clc
    print(f"verified: {nsol} SOLUTION lines, {nws} WSURV lines (window survivors checked in Python), {nfs} base-2 Fermat pseudoprimes examined, {bad} problems")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main(sys.argv[1:])
