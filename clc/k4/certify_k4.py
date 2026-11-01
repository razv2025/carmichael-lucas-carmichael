#!/usr/bin/env python3
"""Certification of a k=4 enumeration campaign: hard assertions, fail-fast, provenance.

Usage: python3 certify_k4.py CAMPAIGN_LOG.jsonl CAMPAIGN_SOL.txt [--reference REF_LOG.jsonl] [--out REPORT.txt]

Asserts: header present; every block id 0..nblk-1 logged exactly once; block p1 ranges are increasing, disjoint and
contiguous over the admissible primes (≡ 1 mod 12, 13 ≤ p1 ≤ p1max); the dumped W lines (one per window survivor,
deduplicated by (p1,p2,m)) number exactly sum(wsurv); if a reference log is given, per-block pairs/wsurv/fsurv/sol agree
with it; every W line is re-tested in Python (base-2 Fermat on n = p1 p2 m; survivors factored and checked against the
original tuple without normalisation); no SOLUTION lines unless they verify. Writes a report with SHA-256 of the binary,
source, logs and sol file, compiler/host/git revision. Exit status 0 only if everything holds."""
import argparse, hashlib, json, os, platform, subprocess, sys, time
from sympy import isprime, factorint

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()

def admissible_primes(lo, hi):
    """primes p ≡ 1 (mod 12) in [lo, hi] (sieve)"""
    import math
    sieve = bytearray([1]) * (hi + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(hi) + 1):
        if sieve[i]: sieve[i*i::i] = bytearray(len(range(i*i, hi + 1, i)))
    return [p for p in range(max(lo, 13), hi + 1) if sieve[p] and p % 12 == 1]

def check_clc_tuple(p1, p2, q, r):
    ps = [p1, p2, q, r]
    if not (p1 < p2 < q < r): return False
    if any(not isprime(p) for p in ps): return False
    n = p1 * p2 * q * r
    return all((n - 1) % (p - 1) == 0 and (n + 1) % (p + 1) == 0 for p in ps)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('sol')
    ap.add_argument('--reference'); ap.add_argument('--out')
    a = ap.parse_args()
    fails = []; notes = []
    def must(cond, msg):
        if not cond: fails.append(msg)
    hdr = None; blocks = {}; dup = 0
    for line in open(a.log):
        o = json.loads(line)
        if 'header' in o: hdr = o
        elif 'blk' in o:
            if o['blk'] in blocks: dup += 1
            blocks[o['blk']] = o
    must(hdr is not None, "no header line")
    nblk = hdr['nblk']; must(dup == 0, f"{dup} duplicate block lines")
    must(sorted(blocks) == list(range(nblk)), f"blocks logged {len(blocks)}/{nblk}; missing {sorted(set(range(nblk)) - set(blocks))[:20]}")
    # contiguity over admissible primes
    p1max = hdr['p1max'] or int(round(float(hdr['B']) ** 0.25)) if hdr.get('B') != 'none' else hdr['p1max']
    if hdr.get('p1max'): p1max = hdr['p1max']
    else:
        B = int(hdr['B']); p1max = 1
        while (p1max + 1) ** 4 <= B: p1max += 1
    pr = admissible_primes(13, p1max)
    must(len(pr) == hdr['n_p1'], f"admissible p1 count {len(pr)} != header n_p1 {hdr['n_p1']}")
    bs = hdr['bs']; ok_ranges = True
    for b in range(nblk):
        if b not in blocks: ok_ranges = False; break
        lo, hi = pr[b*bs], pr[min((b+1)*bs, len(pr)) - 1]
        if blocks[b]['p1lo'] != lo or blocks[b]['p1hi'] != hi: ok_ranges = False; fails.append(f"block {b} range {blocks[b]['p1lo']}-{blocks[b]['p1hi']} != expected {lo}-{hi}"); break
    must(ok_ranges, "block ranges not contiguous over admissible primes")
    tot = {k: sum(o[k] for o in blocks.values()) for k in ('pairs','wsurv','fsurv','sol','cand','skip_g','skip_inv')}
    if a.reference:
        ref = {}
        for line in open(a.reference):
            o = json.loads(line)
            if 'blk' in o: ref[o['blk']] = o
        for b, o in blocks.items():
            if b in ref:
                for k in ('pairs','wsurv','fsurv','sol','p1lo','p1hi'):
                    must(o[k] == ref[b][k], f"block {b}: {k} {o[k]} != reference {ref[b][k]}")
        must(sorted(ref) == sorted(blocks), "reference log covers a different block set")
    # W lines
    W = set(); wsurv_lines = 0; fsurv = 0; sols = []
    for line in open(a.sol):
        if line.startswith('W '):
            p1, p2, m = (int(x) for x in line.split()[1:4]); W.add((p1, p2, m))
        elif line.startswith('WSURV'): wsurv_lines += 1
        elif line.startswith('FSURV'): fsurv += 1
        elif line.startswith('SOLUTION'): sols.append(line)
    must(len(W) == tot['wsurv'], f"distinct W tuples {len(W)} != sum(wsurv) {tot['wsurv']}")
    must(fsurv == tot['fsurv'], f"FSURV lines {fsurv} != sum(fsurv) {tot['fsurv']}")
    # per-block survivor counts: p1 determines the block (blocks are consecutive ranges of admissible primes)
    import bisect
    starts = [blocks[b]['p1lo'] for b in range(nblk)] if ok_ranges else []
    if starts:
        per_blk = {}
        for (p1, p2, m) in W:
            b = bisect.bisect_right(starts, p1) - 1
            per_blk[b] = per_blk.get(b, 0) + 1
        bad_blocks = [b for b in range(nblk) if per_blk.get(b, 0) != blocks[b]['wsurv']]
        must(not bad_blocks, f"per-block W counts differ from logged wsurv in blocks {bad_blocks[:10]}")
    # Python re-test of every survivor
    t0 = time.time(); ferm = 0; clc_found = 0
    for (p1, p2, m) in sorted(W):
        n = p1 * p2 * m
        if pow(2, n - 1, n) != 1: continue
        ferm += 1
        f = factorint(m)
        if len(f) == 2 and all(e == 1 for e in f.values()):
            q, r = sorted(f)
            if check_clc_tuple(p1, p2, q, r): clc_found += 1; fails.append(f"CLC FOUND: {p1} {p2} {q} {r}")
        notes.append(f"survivor passing Fermat: p1={p1} p2={p2} m={m} = {dict(f)}")
    must(clc_found == len(sols), f"{clc_found} CLC tuples found in Python vs {len(sols)} SOLUTION lines")
    must(ferm == tot['fsurv'], f"Python base-2 Fermat survivors {ferm} != logged fermat_survivors {tot['fsurv']}")
    for line in sols:
        kv = dict(x.split('=') for x in line.split()[1:])
        must(check_clc_tuple(*(int(kv[k]) for k in ('p1','p2','q','r'))), "SOLUTION line fails exact check: " + line.strip())
    # provenance
    here = os.path.dirname(os.path.abspath(__file__))
    prov = {}
    for f in ('enum_k4', 'enum_k4.c', a.log, a.sol):
        p = f if os.path.isabs(f) or os.path.exists(f) else os.path.join(here, f)
        prov[f] = sha(p) if os.path.exists(p) else 'MISSING'
    def run(cmd):
        try: return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip().split('\n')[0]
        except Exception as e: return f'n/a ({e})'
    rep = [f"# k=4 enumeration certification — {time.strftime('%Y-%m-%d %H:%M:%S')}",
           f"log: {a.log}   sol: {a.sol}   reference: {a.reference}",
           f"header: {json.dumps(hdr)}",
           f"blocks: {len(blocks)}/{nblk} unique, ranges contiguous over {len(pr)} admissible primes 13..{p1max}",
           f"totals: pairs={tot['pairs']:,} cand={tot['cand']:,} skip_gcd={tot['skip_g']:,} skip_inv={tot['skip_inv']:,} window_survivors={tot['wsurv']} fermat_survivors={tot['fsurv']} solutions={tot['sol']}",
           f"W lines: {len(W)} distinct (p1,p2,m) tuples within this campaign, per-block counts equal to the log, all re-tested in Python in {time.time()-t0:.0f}s; passing base-2 Fermat: {ferm} (= logged); CLC: {clc_found}",
           *["  " + n for n in notes],
           f"provenance: host={platform.node()} machine={platform.machine()} os={platform.platform()}",
           f"  compiler: {run(['cc', '--version'])}",
           f"  git revision: {run(['git', '-C', here, 'rev-parse', 'HEAD'])}  (dirty files: {run(['git', '-C', here, 'status', '--short', '--', here]) or 'none'})",
           *[f"  sha256 {k}: {v}" for k, v in prov.items()],
           ("CERTIFIED: all assertions hold" if not fails else "FAILED:\n  " + "\n  ".join(fails))]
    text = "\n".join(rep); print(text)
    if a.out: open(a.out, 'w').write(text + "\n")
    sys.exit(0 if not fails else 1)

if __name__ == '__main__':
    main()
