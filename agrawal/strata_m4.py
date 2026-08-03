"""Symbolic derivation of the reduced system for m=4 CLC families in the
s-collision stratum (s1 = s2 = sigma), the case Theorem 3 leaves open.

Run: python3 -m agrawal.strata_m4   (prints E1..E4 and the E1/E2
compatibility polynomial after eliminating the free root rho).

G(tau) = n(-tau) = c'(tau-sigma)(tau-s3)(tau-s4)(tau-rho) + 1 with
c' = a1a2a3a4; requiring G(t_i) = -1 at t_i = s_i + 2/a_i gives E1..E4.
E1, E2 are linear in rho; eliminating rho yields a compatibility polynomial
divisible by (a1 - a2), nonzero in this stratum. Together with E3, E4 this
is the full obstruction system for the stratum; no rational solution with
positive a_i is known, and the exhaustive integer search (search_general,
a_i <= 400+) finds none. Closing it analytically is open problem 1 of
docs/obstructions.md.
"""

import sympy as sp


def derive():
    a1, a2, a3, a4, sg, s3, s4, rho, tau = sp.symbols(
        "a1 a2 a3 a4 sigma s3 s4 rho tau"
    )
    c = a1 * a2 * a3 * a4
    G = c * (tau - sg) * (tau - s3) * (tau - s4) * (tau - rho) + 1
    ts = [sg + 2 / a1, sg + 2 / a2, s3 + 2 / a3, s4 + 2 / a4]
    eqs = [sp.numer(sp.together(G.subs(tau, t) + 1)) for t in ts]
    r1 = sp.solve(eqs[0], rho)[0]
    r2 = sp.solve(eqs[1], rho)[0]
    compat = sp.factor(sp.numer(sp.together(r1 - r2)))
    return eqs, compat


if __name__ == "__main__":
    eqs, compat = derive()
    for i, e in enumerate(eqs, 1):
        print(f"E{i}:", sp.factor(e), "\n")
    print("compatibility (must vanish; (a1-a2) factor nonzero in stratum):")
    print(compat)
