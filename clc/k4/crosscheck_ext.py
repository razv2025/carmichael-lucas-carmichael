#!/usr/bin/env python3
"""Cross-checks between the four k=4 campaigns through their window-survivor sets (W lines: p1 p2 m).

The campaigns overlap: every n ≤ 10^30 is ≤ 10^32, every p1 ≤ 500,000 is ≤ 10^6, and the bounded-n and bounded-p1
campaigns share all tuples with p1 ≤ 10^6 and n ≤ 10^32.  The survivor of a tuple does not depend on the campaign,
so the survivor sets must agree exactly on each overlap although the campaigns partition the work differently
(different block sizes, different p2 ranges, different executions).  Exit status 0 iff all three equalities hold."""
import sys
def W(path):
    return {tuple(int(x) for x in l.split()[1:4]) for l in open(path) if l.startswith('W ')}
w30, w32 = W('k4_n1e30_dump_sol.txt'), W('k4_n1e32_sol.txt')
w5, w6 = W('k4_p1_500000_dump_sol.txt'), W('k4_p1_1000000_sol.txt')
n = lambda t: t[0]*t[1]*t[2]
checks = [
    ("n<=1e32 campaign restricted to n<=1e30  ==  n<=1e30 campaign", {t for t in w32 if n(t) <= 10**30}, w30),
    ("p1<=1e6 campaign restricted to p1<=500000  ==  p1<=500000 campaign", {t for t in w6 if t[0] <= 500000}, w5),
    ("n<=1e32 campaign restricted to p1<=1e6  ==  p1<=1e6 campaign restricted to n<=1e32", {t for t in w32 if t[0] <= 10**6}, {t for t in w6 if n(t) <= 10**32}),
]
print(f"survivor sets: n<=1e30: {len(w30)}  n<=1e32: {len(w32)}  p1<=500000: {len(w5)}  p1<=1e6: {len(w6)}")
bad = 0
for name, a, b in checks:
    ok = a == b; bad += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {len(a)} vs {len(b)} tuples" + ("" if ok else f"; only left {sorted(a-b)[:5]} only right {sorted(b-a)[:5]}"))
print("CROSSCHECK: all survivor sets agree on the overlaps" if not bad else "CROSSCHECK FAILED")
sys.exit(1 if bad else 0)
