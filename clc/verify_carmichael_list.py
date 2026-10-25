"""Completeness checks on a decoded numbers-only Carmichael list before scanning.
Usage: python3 -I verify_list.py LIST.txt
Expected (OEIS A055553 / Shallue-Webster / Goutier):
  C(10^22) = 49,679,870   C(10^23) = 123,381,982   C(10^24) = 308,279,939"""
import sys, re
path = sys.argv[1]
exp = {22: 49679870, 23: 123381982, 24: 308279939}
cnt = {22: 0, 23: 0, 24: 0}
prev = 0; total = 0; nonmono = 0; bad = 0; first = []
with open(path, 'rb') as f:
    for raw in f:
        m = re.fullmatch(rb'\s*([0-9]+)\s*', raw)
        if not m: bad += 1; continue
        n = int(m.group(1)); total += 1
        if len(first) < 5: first.append(n)
        if n <= prev: nonmono += 1
        prev = n
        if n < 10**22: cnt[22] += 1
        if n < 10**23: cnt[23] += 1
        if n < 10**24: cnt[24] += 1
print(f"total lines: {total:,}   malformed: {bad}   non-increasing steps: {nonmono}")
print(f"first five: {first}   (expected [561, 1105, 1729, 2465, 2821])")
print(f"largest: {prev}")
ok = True
for d in (22, 23, 24):
    s = 'MATCH' if cnt[d] == exp[d] else 'MISMATCH'
    ok &= cnt[d] == exp[d]
    print(f"  count < 10^{d}: {cnt[d]:,}  expected {exp[d]:,}  -> {s}")
print("VERDICT:", "COMPLETE AND CONSISTENT" if ok and bad == 0 and nonmono == 0 and first == [561,1105,1729,2465,2821] else "PROBLEM")
