"""Referee for the Lander-Parkin-Selfridge searches.

Any claimed solution must pass these exact big-int checks before being
reported. Any claimed exhaustive bound must come with the search log
(range covered, filter configuration, checksum of candidate counts).
"""


def check_513(a: int, b: int, c: int, d: int) -> bool:
    """a^5 + b^5 + c^5 = d^5 with 0 < a <= b <= c < d, disjoint sides."""
    if not (0 < a <= b <= c < d):
        return False
    if d in (a, b, c):
        return False
    return a**5 + b**5 + c**5 == d**5


def check_615(a: int, xs: list[int]) -> bool:
    """a^6 = x1^6 + ... + x5^6, positive, a not among xs."""
    return (
        len(xs) == 5
        and all(x > 0 for x in xs)
        and a not in xs
        and sum(x**6 for x in xs) == a**6
    )


def check_624(a: int, b: int, xs: list[int]) -> bool:
    """a^6 + b^6 = x1^6 + ... + x4^6, positive, sides disjoint."""
    return (
        len(xs) == 4
        and all(x > 0 for x in xs)
        and a > 0 < b
        and not ({a, b} & set(xs))
        and a**6 + b**6 == sum(x**6 for x in xs)
    )


def brute_513(d_max: int):
    """Python reference search: all (a,b,c,d) with d <= d_max satisfying
    a^5+b^5+c^5 = d^5. Also returns the number of exact fifth-power sums
    inspected — used to cross-validate the C core's coverage accounting."""
    fifth = [i**5 for i in range(d_max + 1)]
    fifth_set = {v: i for i, v in enumerate(fifth)}
    hits = []
    inspected = 0
    for d in range(2, d_max + 1):
        d5 = fifth[d]
        for c in range(1, d):
            rem = d5 - fifth[c]
            # need a^5 + b^5 = rem with a <= b <= c
            for b in range(1, c + 1):
                r2 = rem - fifth[b]
                if r2 <= 0:
                    break
                if r2 > fifth[b]:
                    continue
                inspected += 1
                a = fifth_set.get(r2)
                if a is not None and 1 <= a <= b:
                    hits.append((a, b, c, d))
    return hits, inspected
