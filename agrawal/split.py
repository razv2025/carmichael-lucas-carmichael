"""Side-split optimization over a twin-smooth pool.

The CLC condition needs n ≡ 1 (mod p-1) contributions and n ≡ -1 (mod p+1)
contributions to coexist, so every small odd prime q must be assigned to one
side: q | (p-1) allowed only if q is a "side-1" prime, q | (p+1) only if
"side-2". The 2-adic branch works the same way: either all pool primes
p ≡ 3 (mod 4) (then n ≡ -1 mod 2^a) or all p ≡ 1 (mod 4) (then n ≡ 1 mod 2^a).

Given a cached twin-smooth pool, a split keeps the subset of pool primes
consistent with it. We hill-climb over splits to maximize the margin
    |usable subpool| - log2 phi(lcm)
and run the MITM solver on the best splits found.

Usage:
    python3 -m agrawal.split --pool data/twins-y100-1e9.jsonl --minutes 60
"""

import argparse
import json
import random
import time
from math import log2
from pathlib import Path

from .harvest import Record
from .numth import crt_prime_powers, lcm_fac, phi_from_fac
from .solver import greedy_subpool, mitm_search
from .twins import load_pool


def _odd_primes(fac: dict[int, int]) -> frozenset[int]:
    return frozenset(q for q in fac if q != 2)


def prep(pool: list[Record]) -> list[dict]:
    out = []
    for r in pool:
        out.append(
            {
                "rec": r,
                "m1_odd": _odd_primes(r.fac_m1),
                "p1_odd": _odd_primes(r.fac_p1),
                "branch": 3 if r.p % 4 == 3 else 1,
            }
        )
    return out


def consistent_pool(prepped: list[dict], side1: set[int], branch: int) -> list[Record]:
    """Pool records usable under the given side-1 prime set and 2-adic branch."""
    out = []
    for e in prepped:
        if e["branch"] != branch:
            continue
        if not e["m1_odd"] <= side1:
            continue
        if e["p1_odd"] & side1:
            continue
        out.append(e["rec"])
    return out


def build_split_system(sub: list[Record], side1: set[int], branch: int):
    """(M, t) for a consistent subpool under the split."""
    m_fac = lcm_fac(
        [r.fac_m1 for r in sub] + [r.fac_p1 for r in sub]
    )
    residues = {}
    for q, e in m_fac.items():
        pe = q**e
        if q == 2:
            residues[pe] = 1 % pe if branch == 1 else pe - 1
        elif q in side1:
            residues[pe] = 1
        else:
            residues[pe] = pe - 1
    t, M = crt_prime_powers(residues)
    return M, t, m_fac


def split_margin(sub: list[Record]) -> float:
    if len(sub) < 3:
        return float("-inf")
    m_fac = lcm_fac([r.fac_m1 for r in sub] + [r.fac_p1 for r in sub])
    return len(sub) - log2(phi_from_fac(m_fac))


def eval_split(prepped, side1: set[int], branch: int, max_n: int = 44):
    """Returns (margin of best greedy prefix, usable pool, greedy subpool)."""
    usable = consistent_pool(prepped, side1, branch)
    if len(usable) < 3:
        return float("-inf"), usable, []
    sub = greedy_subpool(usable, max_n=max_n)
    return split_margin(sub), usable, sub


def hill_climb(
    prepped: list[dict],
    all_odd: list[int],
    branch: int,
    rng: random.Random,
    iters: int = 400,
) -> tuple[float, set[int]]:
    """Flip/swap local search over the side-1 set for one 2-adic branch."""
    side1 = {q for q in all_odd if rng.random() < 0.5}
    best, _, _ = eval_split(prepped, side1, branch)
    for _ in range(iters):
        q = rng.choice(all_odd)
        cand = set(side1)
        if q in cand:
            cand.discard(q)
        else:
            cand.add(q)
        m, _, _ = eval_split(prepped, cand, branch)
        if m >= best:
            best, side1 = m, cand
    return best, side1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--minutes", type=float, default=30.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters", type=int, default=400)
    ap.add_argument("--mitm-margin", type=float, default=-16.0)
    ap.add_argument("--mitm-seconds", type=float, default=120.0)
    ap.add_argument("--out", default="data/splits.jsonl")
    ap.add_argument("--hits-out", default="data/HITS.jsonl")
    args = ap.parse_args()

    pool = load_pool(args.pool)
    prepped = prep(pool)
    all_odd = sorted({q for e in prepped for q in (e["m1_odd"] | e["p1_odd"])})
    print(f"pool: {len(pool)} twin-smooth primes, {len(all_odd)} odd side-primes, "
          f"branch3={sum(e['branch']==3 for e in prepped)}, "
          f"branch1={sum(e['branch']==1 for e in prepped)}", flush=True)

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    hits_path = Path(args.hits_out)
    deadline = time.time() + args.minutes * 60
    best_overall = float("-inf")
    restart = 0
    while time.time() < deadline:
        restart += 1
        branch = rng.choice([1, 3])
        margin, side1 = hill_climb(prepped, all_odd, branch, rng, iters=args.iters)
        rec = {
            "restart": restart,
            "branch": branch,
            "margin": round(margin, 2) if margin > float("-inf") else None,
            "side1": sorted(side1),
        }
        if margin > best_overall:
            best_overall = margin
            print(f"[{restart}] new best margin {margin:+.2f} (branch {branch})",
                  flush=True)
        if margin > args.mitm_margin:
            _, usable, sub = eval_split(prepped, side1, branch)
            M, t, _ = build_split_system(sub, side1, branch)
            hits = list(mitm_search(sub, max_hits=10, time_limit=args.mitm_seconds,
                                    system=(M, t)))
            rec["subpool"] = [r.p for r in sub]
            rec["mitm_hits"] = len(hits)
            for h in hits:
                if h["verified"]:
                    with hits_path.open("a") as f:
                        f.write(json.dumps(
                            {k: (str(v) if k == "n" else v) for k, v in h.items()}
                        ) + "\n")
                    print(f"*** VERIFIED CLC HIT: k={h['k']}, "
                          f"{h['n_digits']} digits ***", flush=True)
        with out.open("a") as f:
            f.write(json.dumps(rec) + "\n")
    print(f"done: {restart} restarts, best margin {best_overall:+.2f}", flush=True)


if __name__ == "__main__":
    main()
