import sys, time
from sympy import factorint
path = sys.argv[1]
nums = []
for line in open(path):
    parts = line.split()
    if len(parts) == 2 and parts[1].isdigit():
        nums.append(int(parts[1]))
t0 = time.time()
mx = max(nums); hits = []; bad_lc = 0
for n in nums:
    f = factorint(n)
    ps = list(f)
    if any(e > 1 for e in f.values()) or any((n + 1) % (p + 1) for p in ps):
        bad_lc += 1; continue            # sanity: table entry not LC?!
    if all((n - 1) % (p - 1) == 0 for p in ps):
        hits.append((n, ps))
print(f"checked {len(nums)} Lucas-Carmichael numbers, max = {mx} ({mx:.3e}), in {time.time()-t0:.1f}s")
print(f"table sanity: entries failing LC/squarefree check = {bad_lc}")
print(f"CARMICHAEL + LUCAS-CARMICHAEL numbers found: {len(hits)}")
for n, ps in hits: print("  ", n, ps)
