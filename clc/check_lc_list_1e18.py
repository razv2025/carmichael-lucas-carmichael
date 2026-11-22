#!/usr/bin/env python3
"""Converse check on D. Suteu's list of Lucas–Carmichael numbers below 10^18 (linked from OEIS A006972 since Nov 2026:
https://github.com/trizen/experimental-projects/blob/master/pseudoprimes/lucas-carmichael/lucas-carmichael-1e18.zip).
A Williams number is a Lucas–Carmichael number that is also Carmichael, hence a base-2 Fermat pseudoprime.
For every listed n: test 2^(n-1) mod n; any pseudoprime is factored and tested with Korselt's criterion.
Also: the list is strictly increasing, counts below 10^k are printed (the count below 10^15 must be 129,125, the size
of the OEIS a-file), and a random sample is factored and checked against the Lucas–Carmichael definition.
Usage: python3 check_lc_list_1e18.py LIST.txt     (one number per line, or 'index number')"""
import os, sys, hashlib, random
from sympy import factorint
path = sys.argv[1]; ns = [int(l.split()[-1]) for l in open(path) if l.strip() and not l.startswith('#')]
assert all(a < b for a, b in zip(ns, ns[1:])), "list not strictly increasing"
psp = [n for n in ns if pow(2, n - 1, n) == 1]
will = []
for n in psp:
    f = factorint(n)
    if all(e == 1 for e in f.values()) and all((n - 1) % (p - 1) == 0 for p in f): will.append(n)
random.seed(1); bad = 0
for n in random.sample(ns, 3000):
    f = factorint(n)
    if not (len(f) >= 2 and all(e == 1 for e in f.values()) and all((n + 1) % (p + 1) == 0 for p in f)): bad += 1
print(f"{os.path.basename(path)} (sha256 {hashlib.sha256(open(path,'rb').read()).hexdigest()}): {len(ns):,} numbers, max {max(ns)}")
print("counts below 10^k:", {k: sum(1 for n in ns if n < 10**k) for k in (12, 15, 16, 17, 18)})
print(f"sample of 3000 not Lucas–Carmichael: {bad}; base-2 Fermat pseudoprimes: {len(psp)}; Carmichael (= Williams) numbers: {len(will)} {will[:3]}")
sys.exit(1 if will or bad else 0)
