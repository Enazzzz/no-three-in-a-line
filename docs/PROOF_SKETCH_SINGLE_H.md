# Proof sketch — single hyperbola has no non-primary 3-line

**Status:** conjecture + computational certificate. Not a complete proof.  
**Companion data:** `data/single_h_clean_scan.csv` (all odd primes `p≤179`:
`nonprimary_ge3 = 0`).

## Statement

Let `p` be an odd prime, `n = 2p`, and `c ∈ F_p^*`. Let

```
H(c) = { (x,y) ∈ {1,…,n}² : x y ≡ c (mod p),  p ∤ x, p ∤ y }.
```

**Conjecture.** Every line that contains ≥3 points of `H(c)` is a
**primary** line (horizontal, vertical, or slope ±1). Equivalently: `H(c)`
has no 3-term progression on a slope outside `{0, ∞, ±1}`.

## Why this is plausible

Over the field `F_p`, a line meets the hyperbola `xy = c` in **at most two**
points (substitute `y = mx+b` into `xy=c` to get a quadratic). So any
non-primary triple on the board must use the **lifts**
`x = x₀ + i p`, `y = y₀ + j p` with `i,j ∈ {0,1}` in an essential way.

On the `n=2p` board each nonzero residue class for `x` (resp. `y`) has at
most two representatives. Empirically, the only time three lifts align is
when the line is already primary (where the ambient lattice is richer —
rows/cols/±1 diagonals can collect both lifts from several residues).

## Proof outline (incomplete)

1. Reduce three collinear board points `P₁,P₂,P₃ ∈ H(c)` to their
   residues `(xᵢ mod p, yᵢ mod p)` on the hyperbola in `F_p²`.
2. If the three residues are **distinct** as `F_p`-points, they cannot be
   collinear over `F_p` on a non-horizontal/vertical line unless the board
   line’s slope is somehow “folded” by the `p`-periodic lifts — write the
   collinearity determinant and reduce mod `p`.
3. If two share a residue class, they differ by `(±p, 0)`, `(0, ±p)`, or
   `(±p, ±p)` — i.e. the chord between them is already a primary direction.
   Show that extending that chord to a third `H(c)` point forces the line
   to stay primary.
4. Handle slope ±1 separately as primary (allowed to be dirty).

Missing piece: a clean case analysis for “three distinct residues whose
board lifts become collinear with non-primary slope.” That is the step that
still needs algebra, not just scanning.

## Computational certificate

```bash
PYTHONPATH=. python3 research/scan_single_h_clean.py --limit 180 > data/single_h_clean_scan.csv
```

Through `p=179` (40 odd primes), every row has `nonprimary_ge3 = 0` while
`primary_ge3 > 0` and `max_on_line ≤ 4`.

## Use in the project

This law explains why multi-hyperbola damage is entirely **mixed**
(`FINDINGS_SLOPE_CENSUS.md`). A full proof would turn that empirical split
into a theorem and focus future constructions on cross-family incidence
geometry alone.
