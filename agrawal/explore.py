"""Configuration explorer for the Carmichael + Lucas-Carmichael milestone hunt.

Sweeps random assignments of small odd primes to the O1 (p-1) and O2 (p+1)
sides, harvests the prime pool for each configuration, measures the margin
    pool_size - log2 phi(lcm)
after greedy subpool selection, and runs the meet-in-the-middle search whenever
the margin makes hits plausible. Every configuration's stats append to a JSONL
log; verified hits go to a separate file and are the headline event.

Usage:
    python3 -m agrawal.explore --minutes 120 --out data/explore.jsonl
"""

import argparse
import json
import random
import time
from pathlib import Path

from .harvest import harvest_clc
from .numth import is_prime
from .solver import build_system, greedy_subpool, mitm_search

SMALL_ODD_PRIMES = [q for q in range(3, 600) if is_prime(q)]


def random_config(rng: random.Random) -> dict:
    q_max = rng.choice([60, 100, 200, 400, 600])
    basket = [q for q in SMALL_ODD_PRIMES if q <= q_max]
    n_primes = rng.randint(min(10, len(basket)), len(basket))
    primes = rng.sample(basket, n_primes)
    o1, o2 = {}, {}
    for q in primes:
        side = rng.random()
        cap = rng.choice([1, 1, 2]) if q <= 13 else 1
        if side < 0.5:
            o1[q] = cap
        else:
            o2[q] = cap
    a2 = rng.randint(4, 24)
    d_limit = 10 ** rng.randint(8, 24)
    return {"o1": o1, "o2": o2, "a2": a2, "d_limit": d_limit}


def run_config(cfg: dict, mitm_seconds: float, max_hits: int) -> dict:
    t0 = time.time()
    pool = harvest_clc(
        cfg["o1"], cfg["o2"], cfg["a2"],
        d_limit=cfg["d_limit"], max_divisors=3_000_000,
    )
    rec = {
        "cfg": {
            "o1": {str(k): v for k, v in cfg["o1"].items()},
            "o2": {str(k): v for k, v in cfg["o2"].items()},
            "a2": cfg["a2"],
            "d_limit": cfg["d_limit"],
        },
        "harvest_seconds": round(time.time() - t0, 2),
        "pool_size": len(pool),
    }
    if len(pool) >= 3:
        sub = greedy_subpool(pool, max_n=44)
        _, _, stats = build_system(sub)
        rec["subpool_size"] = len(sub)
        rec["log2_phi_M"] = round(stats["log2_phi_M"], 2)
        rec["margin"] = round(stats["margin"], 2)
        rec["subpool_primes"] = [r.p for r in sub] if len(sub) <= 60 else None
        if stats["margin"] > -14 and len(sub) >= 3:
            # even at negative margin a lucky hit is possible, and for the
            # small pools that dominate this regime the MITM is nearly free
            hits = list(
                mitm_search(sub, max_hits=max_hits, time_limit=mitm_seconds)
            )
            rec["mitm_hits"] = len(hits)
            rec["hits"] = [
                {k: (str(v) if k == "n" else v) for k, v in h.items()}
                for h in hits
            ]
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--out", default="data/explore.jsonl")
    ap.add_argument("--hits-out", default="data/HITS.jsonl")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mitm-seconds", type=float, default=60.0)
    ap.add_argument("--max-hits", type=int, default=5)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    hits_out = Path(args.hits_out)
    rng = random.Random(args.seed)
    deadline = time.time() + args.minutes * 60

    i = 0
    best_margin = float("-inf")
    while time.time() < deadline:
        i += 1
        cfg = random_config(rng)
        try:
            rec = run_config(cfg, args.mitm_seconds, args.max_hits)
        except Exception as e:  # log and keep sweeping
            rec = {"cfg_error": repr(e), "cfg": str(cfg)}
        rec["iter"] = i
        rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        with out.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        margin = rec.get("margin")
        if margin is not None and margin > best_margin:
            best_margin = margin
            print(f"[{i}] new best margin {margin:+.2f} "
                  f"(pool {rec['pool_size']}, subpool {rec.get('subpool_size')}, "
                  f"log2phi {rec.get('log2_phi_M')})", flush=True)
        for h in rec.get("hits", []):
            if h.get("verified"):
                with hits_out.open("a") as f:
                    f.write(json.dumps({"iter": i, **h}) + "\n")
                print(f"*** VERIFIED CLC HIT at iter {i}: k={h['k']}, "
                      f"{h['n_digits']} digits ***", flush=True)
    print(f"done: {i} configs, best margin {best_margin:+.2f}", flush=True)


if __name__ == "__main__":
    main()
