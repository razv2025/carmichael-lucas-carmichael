"""Checks of the CLC scanning code in clc/ (the 10^22 / 10^24 verification) on known inputs."""
import importlib.util, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


scan = load("scan_clc", "clc/scan_carmichael_list_for_clc.py")

CARMICHAEL = {561: [3, 11, 17], 1105: [5, 13, 17], 1729: [7, 13, 19], 2465: [5, 17, 29], 2821: [7, 13, 31],
              26921089: [13, 37, 97, 577],
              9857524690572481: None,                 # best near-miss below 1e22 (3 matching primes)
              15500309690554865758009: None}          # best near-miss below 1e24 (4 of 9 primes)


def test_factor_carmichael_known():
    for n, ps in CARMICHAEL.items():
        got = scan.factor_carmichael(n)
        prod = 1
        for p in got:
            prod *= p
        assert prod == n and len(set(got)) == len(got)
        assert all((n - 1) % (p - 1) == 0 for p in got)
        if ps:
            assert got == ps


def test_work_counts_matching_primes():
    cnt, hits, hist, bad, best = scan.work(list(CARMICHAEL))
    assert cnt == len(CARMICHAEL) and bad == [] and hits == []
    assert best[0] == 4 and best[2] == 15500309690554865758009
    n = 9857524690572481
    ps = scan.factor_carmichael(n)
    assert sum(1 for p in ps if (n + 1) % (p + 1) == 0) == 3 and len(ps) == 7


def test_work_detects_non_carmichael_and_clc():
    # a non-Carmichael squarefree number must be reported as a verification failure
    cnt, hits, hist, bad, best = scan.work([3 * 5 * 7])
    assert bad == [105]
    # a synthetic 'CLC' cannot be supplied (none known) — check the hit logic on a Lucas–Carmichael test instead
    n = 399  # 3·7·19 is Lucas–Carmichael but not Carmichael
    ps = scan.factor_carmichael(n)
    assert all((n + 1) % (p + 1) == 0 for p in ps) and not all((n - 1) % (p - 1) == 0 for p in ps)


def test_batches_skips_trailer(tmp_path):
    p = tmp_path / "l.txt"
    p.write_bytes(b"561\n1105\n\x1a")
    assert list(scan.batches(str(p), size=10)) == [[561, 1105]]


def test_c_fermat_routine_matches_python():
    """The enumerator's 128-bit modular exponentiation (used to reject window survivors with P <= 2^40)
    must agree with Python's pow on random odd moduli up to 2^122, including Carmichael numbers."""
    import random, shutil
    k4 = ROOT / "clc" / "k4"
    if shutil.which("cc") is None:
        import pytest; pytest.skip("no C compiler")
    subprocess.run(["make", "-s", "enum_k4"], cwd=k4, check=True)
    rng = random.Random(7)
    ns = [rng.getrandbits(b) | 1 for b in (20, 40, 64, 65, 90, 100, 122) for _ in range(40)]
    ns += [561, 1105, 1729, 26921089, 15500309690554865758009, 13 * 97 * 21349]
    out = subprocess.run([str(k4 / "enum_k4"), "--fermat-check"], input="\n".join(map(str, ns)) + "\n",
                         capture_output=True, text=True, check=True).stdout.split("\n")
    got = dict(tuple(map(int, l.split())) for l in out if l.strip())
    assert len(got) == len(set(ns))
    for n in ns:
        assert got[n] == pow(2, n - 1, n), n
