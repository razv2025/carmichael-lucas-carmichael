#!/usr/bin/env python3
"""Certify a finished scan_resumable.py run of the 1e24 Carmichael list.
Asserts: the state file is FINISHED-consistent (done chunk ids contiguous 0..K-1, every chunk once), total == 308,279,939,
histogram sum == total, zero verification failures, zero hits; prints the full (matching primes, omega) histogram.
Usage: python3 certify_rescan.py STATE.json [--expect-total N]"""
import json, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('state'); ap.add_argument('--expect-total', type=int, default=308279939)
a = ap.parse_args(); st = json.load(open(a.state)); fails = []
done = sorted(st['done']); K = len(done)
if done != list(range(K)): fails.append(f"chunk ids not contiguous/unique: {K} ids, max {done[-1] if done else None}")
if st['total'] != a.expect_total: fails.append(f"total {st['total']} != expected {a.expect_total}")
hs = sum(st['hist'].values())
if hs != st['total']: fails.append(f"histogram sum {hs} != total {st['total']}")
if st['bad']: fails.append(f"{len(st['bad'])} verification failures: {st['bad'][:5]}")
if st['hits']: fails.append(f"HITS: {st['hits']}")
by_g = {}
for key, v in st['hist'].items():
    g, k = (int(x) for x in key.split(',')); by_g.setdefault(g, {})[k] = v
print(f"chunks {K} contiguous; total {st['total']:,}; histogram sum {hs:,}; failures {len(st['bad'])}; hits {len(st['hits'])}; best {st['best']}")
for g in sorted(by_g): print(f"  exactly {g} matching primes: {sum(by_g[g].values()):,}  by omega {dict(sorted(by_g[g].items()))}")
print("CERTIFIED" if not fails else "FAILED: " + "; ".join(fails)); sys.exit(1 if fails else 0)
