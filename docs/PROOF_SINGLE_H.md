# Theorem — single hyperbola has no non-primary 3-line

**Status:** proved for the `n=2p` board lifts used in this repo.  
**Code:** `research/proof_single_h.py` (lemma checks)  
**Data:** `data/proof_single_h_scan.csv`, `data/single_h_clean_scan.csv`

## Statement

Let `p` be an odd prime, `n = 2p`, and `c ∈ {1,…,p−1}`. Define

```
H(c) = { (x,y) ∈ {1,…,n}² : xy ≡ c (mod p),  p ∤ x, p ∤ y }.
```

Equivalently, writing residues `r,s ∈ {1,…,p−1}` with `rs ≡ c (mod p)` and
lift bits `a,b ∈ {0,1}`,

```
H(c) = { (r + a p,  s + b p) }.
```

**Theorem.** Every Euclidean line that contains at least three points of
`H(c)` is a **primary** line: horizontal, vertical, or of slope `±1`.
In particular, `H(c)` has no 3-term progression on any other slope.

## Lemmas

### Lemma A (field incidence)

Over the field `F_p`, the hyperbola `xy = c` (`c ≠ 0`) meets every line in
**at most two** points.

*Proof.* A non-vertical line is `y = mx + β`. Substitute into `xy = c`:

```
x(mx + β) = c  ⇒  m x² + β x − c = 0,
```

a quadratic, hence ≤2 roots unless identically zero (which would force
`m = β = c = 0`, impossible). A vertical line `x = r ≠ 0` meets the
hyperbola in the single point `(r, c r^{-1})`. □

### Lemma B (collinearity lifts to an F_p condition)

Let `P_j = (r_j + a_j p, s_j + b_j p)` for `j=1,2,3` be three board points,
with `a_j,b_j ∈ {0,1}` and `r_j,s_j ∈ {1,…,p−1}`. They are collinear iff

```
Δ + p K + p² M = 0,
```

where

```
Δ = (r₂−r₁)(s₃−s₁) − (r₃−r₁)(s₂−s₁),
```

and `K,M` are integer forms in the residues and lift bits
(`research/proof_single_h.board_collinearity_delta`). In particular,
collinearity implies `Δ ≡ 0 (mod p)`.

*Proof.* Expand the determinant identity
`(x₂−x₁)(y₃−y₁) = (x₃−x₁)(y₂−y₁)` after substituting the lifts. □

### Lemma C (same-residue chords are primary)

Two distinct lifts of the same `F_p` point `(r,s)` differ by
`(ε₁ p, ε₂ p)` with `(ε₁,ε₂) ∈ {−1,0,1}² \ {(0,0)}`. Their slope is
`ε₂/ε₁ ∈ {0, ∞, ±1}` — i.e. **primary**.

*Proof.* Immediate from the lift grid `{0,1}×{0,1}` translated by `(r,s)`. □

## Proof of the theorem

Let `L` be a line containing three distinct points `P₁,P₂,P₃ ∈ H(c)`.
Write `Q_j = (r_j, s_j) ∈ F_p²` for their projections (so `Q_j` lies on
`xy = c`). Let `t = |{Q₁,Q₂,Q₃}|`.

**Case `t = 3`.** Lemma B gives `Δ ≡ 0 (mod p)`, so the vectors
`Q₂−Q₁` and `Q₃−Q₁` are parallel over `F_p`. None is zero (distinct
projections), hence `Q₁,Q₂,Q₃` are collinear over `F_p`. Lemma A then
forbids three distinct hyperbola points on one line — contradiction.
So this case cannot occur.

**Case `t = 1`.** All three points are lifts of one `F_p` point. Those
lifts sit on the axis-aligned `2×2` grid of Lemma C. Any three corners of
a rectangle fail to be collinear, so this case cannot occur either.
(Concretely: collinear triples inside one residue never appear in scans.)

**Case `t = 2`.** By pigeonhole, some projection `Q` appears twice: two
distinct lifts of `Q` lie on `L`. Lemma C says the chord they determine is
primary, so `L` itself is primary.

These cases are exhaustive. Therefore every ≥3-point line in `H(c)` is
primary. □

## Structural corollary

On a ≥3-point primary line inside `H(c)`, the residue pattern is always
**two distinct `F_p` points, each with both lifts** (pattern `2+2` on a
4-point line). Mixed non-primary triples appear only when **two different
hyperbolas** are united (`FINDINGS_SLOPE_CENSUS.md`).

## Machine checks

```bash
PYTHONPATH=. python3 research/scan_proof_single_h.py --limit 100 > data/proof_single_h_scan.csv
PYTHONPATH=. python3 research/scan_single_h_clean.py --limit 250 > data/single_h_clean_scan.csv
```

- Proof-ingredient scan: all odd primes `p≤97` report `ok=1`
  (Lemmas A–C identities + zero non-primary ≥3-lines).
- Cleanliness certificate: all odd primes `p≤241` have `nonprimary_ge3=0`.

The theorem above is the analytic result; the CSV rows are sanity
certificates for the identities, not a substitute for the proof.

## What this closes

- Single-`H` pools need only **primary** repair; they are already all-slope
  clean.
- Multi-`H` non-primary damage is entirely **cross-residue / mixed**.

## What this does not close

- It does not beat HJSW density.
- It does not prove `LB ≥ surplus` for multi-`H` primary optima (still open
  as a uniform-in-`p` inequality, though empirically clean for `p≥17`).
