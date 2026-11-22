#!/usr/bin/env python3
"""A Williams number is a Chebyshev–Carmichael number (OEIS A299799): for every prime p | n it has n == 1 (mod p-1) and
n == -1 (mod p+1), and A299799 consists of the Carmichael numbers with n == +-1 (mod p+1) for every p | n.
Given a b-file of A299799 (e.g. J. C. Puddefoot's census below 10^30, https://oeis.org/A299799/b299799.txt), factor each
term, classify each prime ('+': (p+1)|(n+1), '-': (p+1)|(n-1)) and report whether any term is a Williams number (all '+').
Usage: python3 check_cheb_census_for_williams.py b299799.txt"""
import os, sys, hashlib
from sympy import factorint
path = sys.argv[1]; terms = [int(l.split()[1]) for l in open(path) if l.strip() and not l.startswith('#')]
allminus = mixed = williams = bad = 0
for n in terms:
    ps = sorted(factorint(n)); pat = "".join('+' if (n + 1) % (p + 1) == 0 else '-' if (n - 1) % (p + 1) == 0 else '0' for p in ps)
    if '0' in pat or any((n - 1) % (p - 1) for p in ps): bad += 1; print("NOT Chebyshev-Carmichael:", n)
    elif set(pat) == {'+'}: williams += 1; print("WILLIAMS NUMBER:", n, ps)
    elif '+' in pat: mixed += 1; print(f"mixed: {n} = {' * '.join(map(str, ps))}  {pat}")
    else: allminus += 1
print(f"{os.path.basename(path)} (sha256 {hashlib.sha256(open(path,'rb').read()).hexdigest()}): {len(terms)} terms, max {max(terms):.3e}; "
      f"all '-': {allminus}; mixed signs: {mixed}; Williams numbers (all '+'): {williams}; not in the class: {bad}")
sys.exit(1 if williams or bad else 0)
