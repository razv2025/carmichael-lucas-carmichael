"""Complete, independent CLC scan of a numbers-only Carmichael list.
Line-based batching (no byte-offset splitting) so no line can be dropped.
For each n: factor by Miller-Rabin sqrt(1)-splitting (gmpy2), verify product,
primality, squarefreeness and Korselt, then count primes p with (p+1)|(n+1)."""
import sys, time, re
from multiprocessing import Pool
from math import gcd
from sympy import isprime, factorint
mpz = int
powmod = pow
def is_prime(m, _rounds=None): return isprime(m)

SMALL = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def factor_carmichael(n):
    stack, out = [mpz(n)], []
    while stack:
        m = stack.pop()
        if m == 1: continue
        if is_prime(m, 30): out.append(int(m)); continue
        d, s = m - 1, 0
        while d % 2 == 0: d //= 2; s += 1
        split = None
        for a in SMALL:
            g = gcd(a, m)
            if 1 < g < m: split = g; break
            x = powmod(a, d, m)
            if x == 1 or x == m - 1: continue
            for _ in range(s):
                y = powmod(x, 2, m)
                if y == 1:
                    split = gcd(x - 1, m); break
                if y == m - 1: break
                x = y
            if split and 1 < split < m: break
            split = None
        if split is None or not (1 < split < m):
            # cofactor is an ordinary composite (has Fermat witnesses): general factoring
            f = factorint(int(m))
            for q, e in f.items():
                if e != 1: raise RuntimeError(f"non-squarefree cofactor {m}")
                out.append(int(q))
            continue
        stack.append(split); stack.append(m // split)
    return sorted(out)

def work(batch):
    hits, hist, bad, cnt, best = [], {}, [], 0, (0, 0, 0)
    for n in batch:
        cnt += 1
        ps = factor_carmichael(n)
        prod = 1
        for p in ps: prod *= p
        ok = (prod == n and len(set(ps)) == len(ps) and len(ps) >= 3
              and all((n - 1) % (p - 1) == 0 for p in ps))
        if not ok: bad.append(n); continue
        good = sum(1 for p in ps if (n + 1) % (p + 1) == 0)
        k = len(ps)
        hist[(good, k)] = hist.get((good, k), 0) + 1
        if good > best[0]: best = (good, k, n)
        if good == k: hits.append((n, ps))
    return cnt, hits, hist, bad, best

def batches(path, size=20000):
    buf = []
    with open(path, 'rb') as f:
        for raw in f:
            m = re.fullmatch(rb'\s*([0-9]+)\s*', raw)
            if not m: continue           # the lone 0x1A trailer
            buf.append(int(m.group(1)))
            if len(buf) == size: yield buf; buf = []
    if buf: yield buf

if __name__ == "__main__":
    path = sys.argv[1]; t0 = time.time()
    total, hits, hist, bad, best = 0, [], {}, [], (0, 0, 0)
    with Pool(12) as pool:
        for cnt, h, hs, b, bs in pool.imap_unordered(work, batches(path), chunksize=1):
            total += cnt; hits += h; bad += b
            for key, v in hs.items(): hist[key] = hist.get(key, 0) + v
            if bs[0] > best[0]: best = bs
            if total % 5_000_000 < 20000: print(f"  {total:,} done, {time.time()-t0:.0f}s", flush=True)
    print(f"TOTAL scanned: {total:,}   (expected 49,679,870 -> {'MATCH' if total == 49679870 else 'MISMATCH'})")
    print(f"verification failures: {len(bad)}  {bad[:5]}")
    print(f"FULL CLC hits: {len(hits)}  {hits}")
    print(f"BEST partial: {best[0]} of {best[1]} primes, n = {best[2]}")
    by_k = {}
    for (g, k), v in hist.items(): by_k[k] = by_k.get(k, 0) + v
    print(f"count by omega: {dict(sorted(by_k.items()))}")
    print(f"numbers with exactly 3 matching primes: {sum(v for (g,k),v in hist.items() if g == 3)}  (Eldar/A329948: 179)")
    print(f"elapsed {time.time()-t0:.0f}s")
