"""Near-miss census over a numbers-only Carmichael list (resumable; same chunking and factoring as scan_resumable.py).

For every Carmichael number n = p_1 < ... < p_k in the list (factored, Korselt verified) each prime p is classified:
    '+'  if (p+1) | (n+1)      (the Lucas–Carmichael condition at p; n is a Williams number iff all primes are '+')
    '-'  if (p+1) | (n-1)      (McIntosh's condition [Integers 14 (2014) A59]; all primes '-' = his 'super-Carmichael')
    '0'  otherwise             ('+' and '-' exclude each other because p+1 > 2)
Aggregates: the joint histogram of (#'+', #'-', k); for each sign, how often the smallest and the largest prime carry it,
by k.  Recorded individually (n, primes, pattern): every n with at least three '+', every n in which at least half of the
primes are '+', and (the '-' sign being far more frequent) every n with k >= 7 in which all primes but at most one are '-',
and any n in which all primes are '-'.  With --rule 2 (second pass) instead: every n with at least two '+', and every n
whose largest prime is '+' (OEIS A335336).

  python3 -I census_1e24.py LIST.txt STATE.json [--workers 12] [--chunk 100000] [--limit N]
  stop gracefully: kill -TERM <parent pid>; rerun the same command to continue.
"""
import sys, os, json, time, signal, argparse, threading, importlib.util
from multiprocessing import Pool
_spec = importlib.util.spec_from_file_location("scan_resumable", os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_resumable.py"))
_sr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_sr)
factor_carmichael, chunks = _sr.factor_carmichael, _sr.chunks

RULE = 1
def _init(rule):
    global RULE; RULE = rule

def work(args):
    idx, nums = args
    joint, ends, recs, bad = {}, {}, [], []
    for n in nums:
        ps = factor_carmichael(n)
        prod = 1
        for p in ps: prod *= p
        if not (prod == n and len(set(ps)) == len(ps) and len(ps) >= 3 and all((n - 1) % (p - 1) == 0 for p in ps)):
            bad.append(n); continue
        pat = "".join('+' if (n + 1) % (p + 1) == 0 else '-' if (n - 1) % (p + 1) == 0 else '0' for p in ps)
        k = len(ps); a = pat.count('+'); b = pat.count('-')
        key = f"{a},{b},{k}"; joint[key] = joint.get(key, 0) + 1
        for tag, ch in (("lo", pat[0]), ("hi", pat[-1])):
            if ch != '0':
                e = f"{tag}{ch},{k}"; ends[e] = ends.get(e, 0) + 1
        if RULE == 1: keep = a >= 3 or 2 * a >= k or b == k or (k >= 7 and b >= k - 1)
        else: keep = a >= 2 or pat[-1] == '+'      # rule 2: two or more '+', or the largest prime is '+' (OEIS A335336)
        if keep: recs.append([n, ps, pat])
    return idx, len(nums), joint, ends, recs, bad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list"); ap.add_argument("state")
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--chunk", type=int, default=100000)
    ap.add_argument("--limit", type=int, default=0, help="test aid: stop after this many chunks")
    ap.add_argument("--rule", type=int, default=1, choices=(1, 2), help="which numbers are recorded individually (see work())")
    a = ap.parse_args()
    if os.path.exists(a.state): st = json.load(open(a.state))
    else: st = {"done": [], "offsets": {}, "total": 0, "joint": {}, "ends": {}, "recs": [], "bad": [], "chunk": a.chunk, "rule": a.rule}
    assert st["chunk"] == a.chunk and st.get("rule", 1) == a.rule, "chunk size or rule differs from the state file"
    done = set(st["done"]); stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set()); signal.signal(signal.SIGINT, lambda *_: stop.set())
    t0 = time.time(); inflight = threading.Semaphore(2 * a.workers); lock = threading.Lock(); since = [0]
    def save():
        tmp = a.state + ".tmp"
        with open(tmp, "w") as f: json.dump(st, f)
        os.replace(tmp, a.state)
    def merge(res):
        idx, cnt, joint, ends, recs, bad = res
        with lock:
            st["total"] += cnt; st["recs"] += recs; st["bad"] += bad
            for k, v in joint.items(): st["joint"][k] = st["joint"].get(k, 0) + v
            for k, v in ends.items(): st["ends"][k] = st["ends"].get(k, 0) + v
            st["done"].append(idx); done.add(idx); since[0] += 1
            if since[0] >= a.workers:
                save(); since[0] = 0
                print(f"  {st['total']:,} done, {time.time()-t0:.0f}s (checkpoint)", flush=True)
        inflight.release()
    submitted = 0
    with Pool(a.workers, initializer=_init, initargs=(a.rule,)) as pool:
        for idx, start, nums in chunks(a.list, a.chunk, done, st["offsets"]):
            if stop.is_set() or (a.limit and idx >= a.limit): break
            with lock: st["offsets"][str(idx)] = start
            inflight.acquire(); submitted += 1
            pool.apply_async(work, ((idx, nums),), callback=merge,
                             error_callback=lambda e: (print("FATAL worker error:", e, flush=True), os._exit(3)))
        pool.close(); pool.join()
    with lock: save()
    print(f"{'STOPPED (checkpointed, rerun to continue)' if stop.is_set() else 'FINISHED'}: {st['total']:,} numbers, {len(st['done'])} chunks, {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
