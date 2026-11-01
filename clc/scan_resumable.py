"""Resumable CLC scan over a numbers-only Carmichael list.

Same test as scan_carmichael_list_for_clc.py (factor each n, verify Korselt,
count primes p with (p+1)|(n+1)), but checkpointed: completed line-chunks and
all aggregates are written atomically to a state file, so the run can be
stopped (SIGTERM / Ctrl-C) and rerun to continue. Submission is bounded
(at most 2*workers chunks in flight) so memory stays small.

  python3 -I scan_resumable.py LIST.txt STATE.json [--workers 12] [--chunk 100000]
  stop gracefully:  kill -TERM <parent pid>      (finishes in-flight chunks)
"""
import sys, os, re, json, time, signal, argparse, threading
from multiprocessing import Pool
from math import gcd
from sympy import isprime, factorint

SMALL = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def factor_carmichael(n):
    stack, out = [n], []
    while stack:
        m = stack.pop()
        if m == 1: continue
        if isprime(m): out.append(m); continue
        d, s = m - 1, 0
        while d % 2 == 0: d //= 2; s += 1
        split = None
        for a in SMALL:
            g = gcd(a, m)
            if 1 < g < m: split = g; break
            x = pow(a, d, m)
            if x == 1 or x == m - 1: continue
            for _ in range(s):
                y = pow(x, 2, m)
                if y == 1: split = gcd(x - 1, m); break
                if y == m - 1: break
                x = y
            if split and 1 < split < m: break
            split = None
        if split is None or not (1 < split < m):
            for q, e in factorint(m).items():
                if e != 1: raise RuntimeError(f"non-squarefree cofactor {m}")
                out.append(q)
            continue
        stack += [split, m // split]
    return sorted(out)

def work(args):
    idx, nums = args
    hits, hist, bad, best = [], {}, [], (0, 0, 0)
    for n in nums:
        ps = factor_carmichael(n)
        prod = 1
        for p in ps: prod *= p
        if not (prod == n and len(set(ps)) == len(ps) and len(ps) >= 3
                and all((n - 1) % (p - 1) == 0 for p in ps)):
            bad.append(n); continue
        good = sum(1 for p in ps if (n + 1) % (p + 1) == 0)
        key = f"{good},{len(ps)}"
        hist[key] = hist.get(key, 0) + 1
        if good > best[0]: best = (good, len(ps), n)
        if good == len(ps): hits.append([n, ps])
    return idx, len(nums), hits, hist, bad, best

def load_state(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {"done": [], "offsets": {}, "total": 0, "hits": [], "hist": {}, "bad": [], "best": [0, 0, 0]}

def save_state(path, st):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(st, f)
    os.replace(tmp, path)

def chunks(path, size, done, offsets):
    """Yield (idx, start_offset, numbers) for chunks not yet done."""
    idx = 0
    with open(path, "rb") as f:
        # fast-forward to the lowest pending chunk if its offset is known
        pending = [i for i in range(len(offsets)) if i not in done] if offsets else []
        if pending and str(pending[0]) in offsets:
            idx = pending[0]; f.seek(offsets[str(idx)])
        while True:
            start = f.tell(); buf = []
            while len(buf) < size:
                raw = f.readline()
                if not raw: break
                m = re.fullmatch(rb"\s*([0-9]+)\s*", raw)
                if m: buf.append(int(m.group(1)))
            if not buf: return
            if idx not in done: yield idx, start, buf
            idx += 1
            if len(buf) < size: return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list"); ap.add_argument("state")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--chunk", type=int, default=100000)
    a = ap.parse_args()
    st = load_state(a.state); done = set(st["done"])
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    t0 = time.time(); inflight = threading.Semaphore(2 * a.workers)
    lock = threading.Lock(); since_ckpt = [0]

    def merge(res):
        idx, cnt, hits, hist, bad, best = res
        with lock:
            st["total"] += cnt; st["hits"] += hits; st["bad"] += bad
            for k, v in hist.items(): st["hist"][k] = st["hist"].get(k, 0) + v
            if best[0] > st["best"][0]: st["best"] = list(best)
            st["done"].append(idx); done.add(idx); since_ckpt[0] += 1
            if since_ckpt[0] >= a.workers:
                save_state(a.state, st); since_ckpt[0] = 0
                print(f"  {st['total']:,} done, {time.time()-t0:.0f}s (checkpoint)", flush=True)
        inflight.release()

    with Pool(a.workers) as pool:
        for idx, start, nums in chunks(a.list, a.chunk, done, st["offsets"]):
            if stop.is_set(): break
            with lock:                      # the callback thread serialises st under this lock (race fixed 2026-11-01)
                st["offsets"][str(idx)] = start
            inflight.acquire()
            pool.apply_async(work, ((idx, nums),), callback=merge,
                             error_callback=lambda e: (print("FATAL worker error:", e, flush=True), os._exit(3)))
        pool.close(); pool.join()
    save_state(a.state, st)
    finished = not stop.is_set()
    print(f"{'FINISHED' if finished else 'STOPPED (checkpointed, rerun to continue)'}: "
          f"{st['total']:,} numbers, {len(st['done'])} chunks, {time.time()-t0:.0f}s")
    if finished:
        print(f"verification failures: {len(st['bad'])}  {st['bad'][:5]}")
        print(f"FULL CLC hits: {len(st['hits'])}  {st['hits']}")
        print(f"BEST partial: {st['best'][0]} of {st['best'][1]} primes, n = {st['best'][2]}")
        by_k = {}
        for key, v in st["hist"].items():
            k = int(key.split(",")[1]); by_k[k] = by_k.get(k, 0) + v
        print(f"count by omega: {dict(sorted(by_k.items()))}")
        print(f"numbers with exactly 3 matching primes: {sum(v for key,v in st['hist'].items() if key.startswith('3,'))}")
        # full (matching primes, omega) histogram — added 2026-11-01 so the count of 4-match numbers is on record
        gs = sorted(set(int(key.split(',')[0]) for key in st['hist']))
        for g in gs:
            row = {int(key.split(',')[1]): v for key, v in st['hist'].items() if int(key.split(',')[0]) == g}
            print(f"numbers with exactly {g} matching primes: {sum(row.values()):,}  by omega: {dict(sorted(row.items()))}")

if __name__ == "__main__":
    main()
