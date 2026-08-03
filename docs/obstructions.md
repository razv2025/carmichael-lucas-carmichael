# Obstructions to Carmichael–Lucas-Carmichael numbers

*Working notes, July 2026. Repo: `~/Claude/Math` (verification code in
`agrawal/`, all searches reproducible via the commands cited).*

## 1. Motivation

Call n a **CLC number** if it is simultaneously a Carmichael number
(n squarefree composite, (p−1) | (n−1) for every prime p | n) and a
Lucas–Carmichael number ((p+1) | (n+1) for every p | n). No CLC number is
known; existence is open.

Interest is sharpened by Agrawal's conjecture (AKS): the Lenstra–Pomerance
counterexample mechanism requires an n that is CLC **and** has all prime
factors ≡ 3 (mod 80) with n ≢ ±1 (mod 5). Any obstruction to CLC numbers is
an obstruction to the only known route to refuting Agrawal's conjecture; a
CLC construction method is a prerequisite for that refutation.

This note records one quantified empirical obstruction (§3) and three
impossibility theorems (§4) covering the two classical construction
paradigms for Carmichael-type numbers.

## 2. Setup

Korselt-style criteria: n = p₁⋯p_k (distinct odd primes, k ≥ 3) is CLC iff
n ≡ 1 (mod p−1) and n ≡ −1 (mod p+1) for every p | n. The two classical
paradigms for constructing Carmichael numbers are:

- **Subset products** (Erdős 1956; Löh–Niebuhr; Alford–Granville–Pomerance):
  harvest many primes with p−1 dividing a fixed smooth Λ, then find a subset
  whose product hits 1 (mod Λ).
- **Polynomial families** (Chernick 1939): n(k) = ∏(aᵢk + bᵢ) with
  divisibility built in as polynomial identities, e.g. (6k+1)(12k+1)(18k+1).

Both must be two-sided for CLC. Both, it turns out, break.

## 3. The subset-product wall (empirical, quantified)

Two-sided subset products need every small odd prime q assigned to one side:
q may divide chosen p−1's or chosen p+1's, never both (else n ≡ 1 ≡ −1 mod q),
plus a 2-adic branch (all p ≡ 3 mod 4, or all p ≡ 1 mod 4). Define the
**margin** of a configuration = (usable pool size) − log₂ φ(lcm of all
required p∓1); expected solutions ≈ 2^margin.

Findings (code: `twins.py`, `split.py`, `golden.py`, `explore.py`):

| approach | best margin |
|---|---|
| random smooth-moduli configs (3,250 sampled, all >−14 searched exhaustively) | −8.2 (tiny 3-prime systems) |
| twin-smooth pools + optimized side-split, y = 60 / 100 / 140 / 200 | −29.0 / −30.6 / −31.0 / −36.9 |
| golden (sparse p∓1, tower) pools, y = 200 | −36.9 |

The wall is flat-to-worsening in every scaling direction. Mechanism: each
usable prime adds 1 bit of subset freedom but ~2.5 bits of modulus; towers
(2·3ᵇ+1) nest on one side only, since qᵇ+1 is essentially never a matching
prime power. Hill-climbing over side-assignments saturates (hundreds of
restarts, identical optima). Harvesting is not the bottleneck — 25,660
twin-smooth primes at (y=200, X=10¹⁰) take 27 s — the consistency constraint is.

## 4. Polynomial families: impossibility theorems

Ansatz n(k) = ∏ᵢ₌₁ᵐ (aᵢk + bᵢ), aᵢ > 0, factors pairwise non-proportional,
with the CLC divisibilities required as polynomial-root identities:
n((1−bᵢ)/aᵢ) = 1 and n((−1−bᵢ)/aᵢ) = −1. Write Dᵢⱼ = aᵢbⱼ − aⱼbᵢ. The
conditions become, for every i:

∏_{j≠i}(aⱼ + Dᵢⱼ) = ∏_{j≠i}(Dᵢⱼ − aⱼ) = aᵢ^(m−1).   (†)

**Theorem 1 (m = 3, any offsets).** No family exists. *Proof.* Subtracting
the two products in (†) for each i gives a₂D₁₃ = −a₃D₁₂, a₁D₂₃ = a₃D₁₂,
a₁D₂₃ = −a₂D₁₃. The wedge identity D₂₃a₁ − D₁₃a₂ + D₁₂a₃ = 0 (D = a∧b)
then forces 3a₃D₁₂ = 0, so D = 0, i.e. b ∝ a: the degenerate family
pᵢ = aᵢk′ with no constant term. ∎

**Theorem 2 (uniform signs bᵢ = ±1, every m).** No family exists. *Proof.*
(†) reduces to ∏_{j≠i}(2aⱼ − aᵢ) = aᵢ^(m−1) (resp. mirrored). Take
aᵢ = max: distinct positive aⱼ < aᵢ give |2aⱼ − aᵢ| < aᵢ strictly, so the
product is < aᵢ^(m−1) in absolute value. ∎

**Theorem 3 (generic position, every m).** Let sᵢ = (bᵢ−1)/aᵢ and
tᵢ = (bᵢ+1)/aᵢ. If the sᵢ are pairwise distinct and the tᵢ are pairwise
distinct, no family exists. *Proof.* G(τ) := n(−τ) has leading coefficient
c′ = (−1)ᵐ∏aᵢ and satisfies G(sᵢ) = 1, G(tᵢ) = −1. Distinctness gives the
complete factorizations G − 1 = c′∏(τ − sᵢ) and G + 1 = c′∏(τ − tᵢ);
subtracting, 2 = c′[∏(τ − tᵢ) − ∏(τ − sᵢ)] identically in τ. The τ^(m−1)
coefficient yields Σ(tᵢ − sᵢ) = Σ 2/aᵢ = 0, impossible. ∎

**Corollary.** Every CLC polynomial family (any m) must contain two indices
with pⱼ − 1 = (aⱼ/aᵢ)(pᵢ − 1) or pⱼ + 1 = (aⱼ/aᵢ)(pᵢ + 1) as polynomial
identities (a repeated C-root or L-root — "proportional shifted forms").
Moreover if the sᵢ are distinct, G is already determined as
c′∏(τ − sᵢ) + 1, and t-distinctness re-triggers the contradiction, so at
least one side must be degenerate.

Theorem 3 subsumes Theorems 1–2 in generic position; Theorem 1 also covers
the degenerate strata for m = 3.

## 5. Exhaustive searches of the degenerate strata

The divisor structure of (†) — every factor divides aᵢ^(m−1) — gives strong
pruning; `search_general` (in `family.py`) covers all offset vectors b,
including the proportional-form strata that Theorem 3 does not exclude.
Results (all **empty**):

| system | bound | time |
|---|---|---|
| m = 4, general offsets | aᵢ ≤ 500 | 45 min |
| m = 5, general offsets | aᵢ ≤ 150 | 1.8 h |
| m = 6, general offsets | aᵢ ≤ 60 | 54 h |
| bᵢ = −1, m = 5/7/9/11 | aᵢ ≤ 20000/5000/3000/1500 | seconds (verifies Thm 2) |

## 6. Density heuristic and onset estimates

An Erdős–Pomerance-style count (code: `heuristic.py`) models the expected
number of k-factor objects ≤ x built from primes with p−1 (and p+1) y-smooth,
including a per-odd-prime **side-consistency factor** F_q = 2(1−1/q)^k −
(1−2/q)^k and a 2-adic branch factor 2^(1−k) — ingredients absent from naive
squaring of the Carmichael heuristic, and calibrated against ground truth:

- one-sided per-prime γ fitted to Pinch's counts C(10¹⁵) = 105212,
  C(10¹⁸) = 1401644 (model matches within ~1.4 in ln at both anchors);
- two-sided per-prime γ fitted to this repo's measured twin-smooth prime
  counts at (y, X) = (60,10⁹), (100,10⁹), (140,2·10⁹), (200,10¹⁰);
- an upper calibration from the known emptiness E(CLC ≤ 10¹⁸) ≤ 1
  (all Carmichael numbers to 10¹⁸ are enumerated; none is Lucas–Carmichael).

Onsets (sanity anchor: the same machinery puts the first Carmichael number
near 10³; truth 561):

| object | first expected near | optimal shape |
|---|---|---|
| CLC number | **10²⁰⁸ – 10⁴⁹⁰** | k* ≈ 80–110 factors, y* ≈ 40–90 |
| LP/Agrawal counterexample (+ p ≡ 3 mod 80) | **10²'⁴⁰⁰ – 10²'⁹⁰⁰** | k* ≈ 270, y* ≈ 300–400 |

Interpretation: CLC numbers should exist but start hundreds of digits out —
consistent with every construction obstruction in §§3–5 — and the first
Agrawal counterexample is expected at *thousands* of digits, sharpening the
Lenstra–Pomerance "large but positive density" picture into a concrete (if
heuristic) scale. Both estimates are highly sensitive to the per-prime
calibration (the ranges shown span the defensible band); the qualitative
conclusion — far beyond exhaustive search, within reach of *targeted
construction only if the §§3–5 obstructions can be broken* — is robust.

## 7. The remaining m = 4 question, made explicit

By Theorem 3, an m = 4 family needs a repeated C-root (s₁ = s₂ = σ, WLOG up
to the b → −b mirror). Writing G − 1 = c′(τ−σ)(τ−s₃)(τ−s₄)(τ−ρ) with a free
fourth root ρ and imposing G(tᵢ) = −1 gives four polynomial conditions
E₁–E₄; E₁, E₂ are linear in ρ, and eliminating ρ yields an explicit
compatibility polynomial divisible by (a₁ − a₂) ≠ 0 (derivation reproducible
via `python3 -m agrawal.strata_m4`). No rational solution with positive aᵢ is
known; the integer search covers aᵢ ≤ 500 exhaustively. Deciding this system
is the precise gap between "empty in searched ranges" and a full m = 4
impossibility theorem.

## 8. Discussion

- The two classical construction paradigms are, respectively, quantitatively
  walled (≈ 2⁻³⁰ per attempt at the optimum, flat in every parameter) and
  provably/exhaustively closed in the ranges above.
- Caveat: the family theorems close *polynomial-identity* families. Families
  satisfying the divisibilities only on residue-restricted k, or entirely
  different mechanisms (e.g. Pell-driven sporadic solutions), are not excluded.
- Implication for Agrawal's conjecture: Lenstra–Pomerance counterexamples
  inherit every obstruction above plus congruence conditions (all p ≡ 3 mod 80).
  The absence of structured routes is consistent with their prediction that
  counterexamples, though of positive density asymptotically, begin at
  computationally inaccessible sizes.

## 9. Open

1. Close m = 4 fully (casework on proportional-form strata after Theorem 3;
   the C·L product identity ∏(Dᵢⱼ² − aⱼ²) = aᵢ^(2m−2) may help).
2. A density heuristic for CLC numbers analogous to Pomerance's Carmichael
   count, incorporating the two-sided smoothness correlation.
3. Størmer/Pell complete twin-smooth enumerations to settle the small-modulus
   subset-product regime unconditionally.
