#!/usr/bin/env python3
"""Certify the two passes of census_1e24.py and export the census data.

Usage: python3 certify_census.py STATE1.json STATE2.json RESCAN_STATE.json OUTDIR [--oeis DIR]
Asserts, for each pass: chunk ids contiguous and unique, total 308,279,939, joint histogram sum = total, zero verification
failures, every recorded number re-verified here (product of its primes, Korselt, pattern recomputed, recording rule).
Across passes: joint and end histograms identical.  Against the certified November rescan: the (#'+', omega) histogram
is identical.  Internal consistency: recorded lists have exactly the sizes the histograms predict.
With --oeis DIR (b-files b335336.txt, b329948.txt, b299799.txt downloaded from oeis.org): the terms below their stated
bounds are compared with our lists as sets.  Writes the lists and histograms to OUTDIR and prints a report."""
import json, sys, os, argparse, hashlib, gzip, time
ap = argparse.ArgumentParser(); ap.add_argument('s1'); ap.add_argument('s2'); ap.add_argument('rescan'); ap.add_argument('out'); ap.add_argument('--oeis')
a = ap.parse_args(); fails = []; rep = []
def must(c, msg):
    if not c: fails.append(msg)
    return c
TOTAL = 308279939
s1, s2, old = (json.load(open(p)) for p in (a.s1, a.s2, a.rescan))
def pattern(n, ps): return "".join('+' if (n + 1) % (p + 1) == 0 else '-' if (n - 1) % (p + 1) == 0 else '0' for p in ps)
for name, st in (("pass 1", s1), ("pass 2", s2)):
    d = sorted(st['done'])
    must(d == list(range(len(d))), f"{name}: chunk ids not contiguous/unique")
    must(st['total'] == TOTAL, f"{name}: total {st['total']}"); must(sum(st['joint'].values()) == TOTAL, f"{name}: joint sum")
    must(not st['bad'], f"{name}: {len(st['bad'])} verification failures")
    ns = [r[0] for r in st['recs']]; must(len(set(ns)) == len(ns), f"{name}: duplicate records")
    for n, ps, pat in st['recs']:
        prod = 1
        for p in ps: prod *= p
        ok = prod == n and ps == sorted(set(ps)) and all((n - 1) % (p - 1) == 0 for p in ps) and pattern(n, ps) == pat
        if not ok: fails.append(f"{name}: record {n} fails re-verification"); break
    rep.append(f"{name}: {len(d)} chunks contiguous, total {st['total']:,}, verification failures {len(st['bad'])}, records {len(st['recs']):,} (all re-verified)")
must(s1['joint'] == s2['joint'], "joint histograms of the two passes differ"); must(s1['ends'] == s2['ends'], "end histograms of the two passes differ")
rep.append("pass 1 and pass 2: joint histogram (#'+', #'-', omega) and smallest/largest-prime histograms identical")
J = {tuple(int(x) for x in k.split(',')): v for k, v in s1['joint'].items()}
plus = {}
for (x, y, k), v in J.items(): plus[f"{x},{k}"] = plus.get(f"{x},{k}", 0) + v
must(plus == old['hist'], "(#'+', omega) histogram differs from the certified rescan")
rep.append("(#'+', omega) histogram identical to the certified rescan of 2 Nov 2026 (rescan_1e24_state.json)")
cnt = lambda f: sum(v for key, v in J.items() if f(*key))
r1, r2 = sorted(s1['recs']), sorted(s2['recs'])
A = lambda r: r[2].count('+'); Bm = lambda r: r[2].count('-'); K = lambda r: len(r[1])
p3 = [r for r in r1 if A(r) >= 3]; sC = [r for r in r1 if Bm(r) == K(r)]; half = [r for r in r1 if 2 * A(r) >= K(r)]
nsc = [r for r in r1 if K(r) >= 7 and Bm(r) == K(r) - 1]
p2 = [r for r in r2 if A(r) >= 2]; gpf = [r for r in r2 if r[2][-1] == '+']
must(len(p3) == cnt(lambda x, y, k: x >= 3), "count of >=3 '+' records"); must(len(sC) == cnt(lambda x, y, k: y == k), "count of all-'-' records")
must(len(half) == cnt(lambda x, y, k: 2 * x >= k), "count of half-'+' records"); must(len(nsc) == cnt(lambda x, y, k: k >= 7 and y == k - 1), "near-sC count")
must(len(p2) == cnt(lambda x, y, k: x >= 2), "count of >=2 '+' records")
must(len(gpf) == sum(v for key, v in s1['ends'].items() if key.startswith('hi+')), "count of gpf '+' records")
must([r for r in p2 if A(r) >= 3] == p3, "the >=3 '+' lists of the two passes differ")
must(len(r1) == len({r[0] for r in p3 + sC + half + nsc}) and len(r2) == len({r[0] for r in p2 + gpf}), "records outside the recording rules")
must(cnt(lambda x, y, k: x == k) == 0, "A WILLIAMS NUMBER (all '+')")
rep.append(f"lists: >=3 '+': {len(p3)} (4 '+': {sum(1 for r in p3 if A(r)==4)}, 5+: {sum(1 for r in p3 if A(r)>=5)}); >=2 '+': {len(p2):,}; at least half '+': {len(half)}; largest prime '+': {len(gpf):,}; all '-' (super-Carmichael): {len(sC)}; all but one '-' with omega>=7: {len(nsc):,}; Williams numbers: 0")
byk = {}
for r in gpf: byk[K(r)] = byk.get(K(r), 0) + 1
rep.append(f"largest prime '+', by omega: {dict(sorted(byk.items()))}")
if a.oeis:
    def bfile(name):
        p = os.path.join(a.oeis, name); t = [int(l.split()[1]) for l in open(p) if l.strip() and not l.startswith('#')]
        return t, hashlib.sha256(open(p, 'rb').read()).hexdigest()
    for name, bound, ours, what in (("b335336.txt", 10**22, gpf, "Carmichael k with gpf(k)+1 | k+1 (A335336, Eldar/Suteu, below 1e22)"),
                                    ("b329948.txt", 10**22, p3, "Carmichael numbers with >= 3 primes p+1 | n+1 (A329948, Suteu/Eldar, below 1e22)"),
                                    ("b299799.txt", 10**24, sC, "Chebyshev-Carmichael = super-Carmichael numbers (A299799, Puddefoot's census, restricted to < 1e24)")):
        t, h = bfile(name); theirs = {x for x in t if x < bound}; mine = {r[0] for r in ours if r[0] < bound}
        must(theirs == mine, f"{name}: sets differ (theirs {len(theirs)}, ours {len(mine)}, only theirs {sorted(theirs-mine)[:3]}, only ours {sorted(mine-theirs)[:3]})")
        rep.append(f"OEIS {name} ({len(t)} terms, sha256 {h[:16]}…): {what}: {len(theirs)} terms = our {len(mine)}: {'EQUAL' if theirs == mine else 'DIFFERENT'}")
os.makedirs(a.out, exist_ok=True)
def dump(fn, rows, header):
    op = gzip.open if fn.endswith('.gz') else open
    with op(os.path.join(a.out, fn), 'wt') as f:
        f.write("# " + header + "\n# n = p_1 * ... * p_k   pattern ('+': (p+1)|(n+1), '-': (p+1)|(n-1), '0': neither; in the order of the primes)\n")
        for n, ps, pat in rows: f.write(f"{n} = {' * '.join(map(str, ps))}   {pat}\n")
dump("plus3.txt", p3, f"All {len(p3)} Carmichael numbers below 10^24 with at least three prime factors p such that (p+1) | (n+1)")
dump("plus2.txt.gz", p2, f"All {len(p2)} Carmichael numbers below 10^24 with at least two prime factors p such that (p+1) | (n+1)")
dump("half_plus.txt", half, f"All {len(half)} Carmichael numbers below 10^24 in which at least half of the prime factors p satisfy (p+1) | (n+1)")
dump("gpf_plus.txt", gpf, f"All {len(gpf)} Carmichael numbers below 10^24 whose largest prime factor p satisfies (p+1) | (n+1)  (OEIS A335336)")
dump("super_carmichael.txt", sC, f"All {len(sC)} Carmichael numbers below 10^24 with (p+1) | (n-1) for every prime factor p (McIntosh's super-Carmichael numbers; OEIS A299799)")
dump("near_super_carmichael.txt", nsc, f"All {len(nsc)} Carmichael numbers below 10^24 with at least 7 prime factors, all but one of which satisfy (p+1) | (n-1)")
with open(os.path.join(a.out, "b335336_to_1e24.txt"), 'w') as f:
    for i, r in enumerate(gpf, 1): f.write(f"{i} {r[0]}\n")
json.dump({"joint (plus,minus,omega)": dict(sorted(s1['joint'].items(), key=lambda kv: tuple(int(x) for x in kv[0].split(',')))),
           "ends (lo/hi sign, omega)": dict(sorted(s1['ends'].items()))}, open(os.path.join(a.out, "histograms.json"), 'w'), indent=0)
rep.append("CERTIFIED: all assertions hold" if not fails else "FAILED:\n  " + "\n  ".join(fails))
text = f"# census of the Carmichael numbers below 10^24 — certification {time.strftime('%Y-%m-%d %H:%M')}\n" + "\n".join(rep)
print(text); open(os.path.join(a.out, "CERTIFY_census.txt"), 'w').write(text + "\n"); sys.exit(1 if fails else 0)
