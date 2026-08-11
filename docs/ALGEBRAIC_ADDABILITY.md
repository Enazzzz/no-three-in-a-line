# Algebraic addability program

Instead of treating HJSW augmentation as a generic independent-set /
greedy graph problem, rewrite it algebraically.

## 1. HJSW as an algebraic curve over `F_p`

Fix odd prime `p`, residue `c ∈ F_p^×`, and

```
H(c,p) = { (x,y) ∈ Z² : x y ≡ c (mod p) }.
```

HJSW is (essentially) one hyperbola cut to a union of twelve affine
half-blocks `T2`:

```
S2 = H(c,p) ∩ T2,   |S2| = 3(p−1).
```

## 2. Exact conditions for an empty cell `(x,y)`

### Horizontal / vertical

If row `y` already meets `S2` in ≥2 points, no third point is allowed on
that row (same for columns). For classical HJSW, occupied residue sets
`R_x`, `R_y` each have size `p−1`, so only a thin middle residue strip
(corresponding to unused blocks `M`) is horiz/vert-safe.

### Slope `+1`

Conflict with saturated diagonals

```
D_+^{(2)}(S) = { d : |S ∩ {x' − y' = d}| ≥ 2 }.
```

On the hyperbola, `x' − y' = t − c t^{-1}` for occupied `t`, so `D_+`
is (up to block lifts) the image of

```
f_+(t) = t − c t^{-1}.
```

### Slope `−1`

Same with sums / `f_-(t) = t + c t^{-1}` and

```
D_-^{(2)}(S) = { s : |S ∩ {x' + y' = s}| ≥ 2 }.
```

## 3. Combinatorial core

Let `U` be an algebraically defined candidate pool (e.g. `H(c',p) ∩ M`
or all of `M` filtered by the four residue predicates).

**Question:** How large is the largest subset of `U` that avoids a small
menu of difference classes (here primarily four), relative to the
structured obstacle set coming from `S2`?

This is closer to additive combinatorics than to unstructured greedy
search, and explains why prime-by-prime winner lists looked noisy.

## 4. Predictions

- Horiz/vert force almost all extras into `M`.
- Inside `M`, slope `±1` are the real filter; forbidden diagonal residues
  can cover nearly everything for large `p`, matching `~O(0.1n)` declining
  addable counts.
- Constant-factor improvement needs positive-density survivors after
  **all** slopes, not only the four.
- Positive path: change `c` or take a **union of hyperbolas**, then delete
  carefully on slope `±1` (cf. KNS Remark 3.4).

## 5. Implementation checklist

1. For each prime `p`, compute `S2` and exact `R_x, R_y, D_+^{(2)}, D_-^{(2)}`.
2. Enumerate `U ⊆ M` satisfying the four predicates.
3. Solve max safe subset (exact for small `p`, density heuristics for large).
4. Only then filter remaining general slopes.
5. Log tables of survivor counts vs `p` (job for `distributed/` workers).

Code helpers live in `research/algebraic.py`, `research/subset.py`, and
`distributed/ntil/algebraic.py`.

## 6. Empirical results (2026-08-11, corrected ≥2 rule)

**Bug fixed:** an earlier filter treated any occupied row/column as forbidden.
With the correct ≤2-per-line rule, four-constraint survivor counts grow with
`p` (e.g. ~20k at `p=281`).

**All-slope bottleneck:** after filtering general slopes via slope tables,
the individually addable pool stays small — roughly **8–46** points across
winning primes up to `p=281`. Exact / greedy MIS on that tiny conflict graph
adds about **4–31** points:

| p | 4-constraint | individually ok | added | ratio |
|---|-------------:|----------------:|------:|------:|
| 5 | 24 | 10 | 4 | 1.600 |
| 97 | 2555 | 20 | 14 | 1.557 |
| 139 | 5058 | 23 | 19 | 1.558 |
| 281 | 20335 | 46 | 31 | 1.550 |

This matches the program’s prediction: primary classes leave many candidates,
but **other slopes wipe almost all of them**. Additive `O(1)`–`O(√n)` style
gains still do **not** beat the asymptotic `3/2` barrier. Next leverage is
changing the seed (hyperbola unions + careful ±1 deletion), not polishing
classical HJSW alone.

See `data/addability_scan.csv` and `data/subset_scan.csv`.

## 7. Hyperbola-union smoke (same day)

`research/hyperbola_union.py` tries a second residue `c1` with ±1 deletion.
On small primes it slightly beats pure HJSW-subset (e.g. `p=31`: union
ratio ≈1.581 vs subset ≈1.548). Still additive, not asymptotic — but a
better seed than polishing a single hyperbola.
