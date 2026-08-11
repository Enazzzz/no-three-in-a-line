# LB ≥ surplus for multi-hyperbola primary packings

**Status:** proved corollary + certified conjecture (not a full uniform proof).  
**Code:** `research/lb_surplus.py`  
**Data:** `data/lb_surplus_scan.csv`

## Setup

Let `p` be an odd prime, `n=2p`, and `C ⊂ F_p^*` with `|C|≥2`. Write

```
U(C) = ⋃_{c∈C} H(c)
```

for the usual `n=2p` board lifts. Let `S ⊆ U(C)` be **primary-feasible**
(≤2 points per row, column, and slope-`±1` diagonal). Let `bad(S)` be the
non-primary lines with ≥3 points of `S`, and let `LB(S)` be the greedy
disjoint-excess lower bound on the number of deletions needed to clear
`bad(S)` (`research/allslope_hitting.disjoint_excess_lower_bound`).

Write `surplus(S) = |S| − 3(p−1)` (vs classical HJSW size).

## What is already proved

### Theorem A (mixed-only damage)

Every line in `bad(S)` is **mixed**: it uses at least two distinct residues
`c = xy mod p`.

*Proof.* If a non-primary ≥3-line met only one color class `S ∩ H(c)`, it
would be a non-primary ≥3-line inside a single hyperbola, contradicting
`PROOF_SINGLE_H.md`. □

Empirically: every certificate row has `pure_bad = 0`.

## What is *false* without size hypotheses

### Counterexample to universality

The inequality `LB(S) ≥ surplus(S)` is **false** for arbitrary
primary-feasible `S`. An all-slope-valid (NTIL) subset `T ⊆ U(C)` is
primary-feasible with `LB(T)=0`. Local search inside `U({1,2})` finds

| p | HJSW | in-pool NTIL | surplus | LB |
|--:|-----:|-------------:|--------:|---:|
| 17 | 48 | 50 | +2 | 0 |
| 19 | 54 | 56 | +2 | 0 |
| 31 | 90 | 91 | +1 | 0 |

So `surplus>0=LB`. The claim can only target **large primary packings** —
sets that exceed the NTIL optimum by accepting non-primary triples.

## Certified conjecture

### Conjecture B (max-primary / large primary)

For every odd prime `p≥17` and every `C` with `2≤|C|≤4`, if `S` is a
**maximum-cardinality** primary-feasible subset of `U(C)`, then

```
LB(S) ≥ surplus(S) = |S| − 3(p−1).
```

Equivalently: after any all-slope repair of such an `S`, the surviving size
is at most `3(p−1)`.

### Certificate B′ (algorithmic primary packings)

For every odd prime `17≤p≤79` and every default residue set with `|C|≥2`
(`research/multi_hyperbola.default_residue_sets`), letting `S` be the
best-of

- HJSW warm-start greedy,
- capped exact primary BnB,
- degree-greedy primary packing,

we have `LB(S) ≥ surplus(S)` in **all 80 / 80** rows
(`data/lb_surplus_scan.csv`). Minimum `LB−surplus` by `p` grows from
`+6` at `p=17` to about `+38` near `p=79`.

**Pool scope:** `U(C)` here means the **board-coordinate** union from
`hyperbola_points` / `multi_hyperbola_pool`. Ambient-aligned unions
(same shift as HJSW) are different sets; their primary packings can have
`LB < surplus` — see `docs/FINDINGS_AMBIENT_MULTI_H.md`. Also, board-pool
“HJSW warm-start” typically retains few S₂ points because HJSW ⊄ board `U(C)`.

The only scanned failure of `LB≥surplus` among small primes is
`p=7` with `C={1,2,6}` (`gap=−2`), matching `FINDINGS_ALLSLOPE_HITTING.md`.

```bash
PYTHONPATH=. python3 research/scan_lb_surplus.py --lo 7 --hi 80 > data/lb_surplus_scan.csv
```

## Proof outline toward Conjecture B (incomplete)

### Reduction (sufficient lemmas — not a free lunch)

Write `M = max_c |S ∩ H(c)|` and `m = |S| − M` (majority / minority mass
under **board** coloring `xy mod p`). Let `LB` be the disjoint-excess lower
bound. Conjecture B *would* follow from:

| Lemma | Statement | Status |
|-------|-----------|--------|
| **B1** | `LB(S) ≥ ⌊m/3⌋` | Certified 80/80 (`data/conjecture_b_lemmas_scan.csv`); **not proved** |
| **B2** | `⌊m/3⌋ ≥ surplus(S)` | Same certificate 80/80; **not proved** |

Together: `LB ≥ ⌊m/3⌋ ≥ surplus`. Code: `research/conjecture_b_lemmas.py`.

**Warning.** This is a reduction to **two new claims**, not an inheritance
from `PROOF_SINGLE_H`. Unless B1/B2 get independent counting proofs, the
reduction trades one conjecture for two. Prefer proving Conjecture B
directly, or proving B1 alone plus a different gap argument.

**Caveats for B1.** Minority points are not always all on bad lines (min
coverage ≈ 0.81). B1 is not “cover minority by disjoint triangles.”

### B2 provenance (pushed first — negative result)

The suggestive “mono primary ≈ 0.7 · |HJSW|” figure is **not** a corollary
of the single-hyperbola theorem. Provenance check
(`research/b2_provenance.py`, `data/b2_provenance_scan.csv`):

1. **What single-H + two-lift *does* give.** On board `H(c)` with `n=2p`,
   every row and every column already meets `H(c)` in ≤2 points. So any
   subset is automatically row/col primary-feasible; primary ⇔ ≤2 on each
   slope-`±1` diagonal; and by `PROOF_SINGLE_H`, primary ⇔ NTIL on that
   color. This is real structure — and it never mentions HJSW.

2. **Where the ~0.7 comes from.** Algorithmic max primary size in board
   `H(1)` equals `2(p+1)` when `p≡1 (mod 4)` and `2p` when `p≡3 (mod 4)`
   for all odd primes `5≤p≤61` (16/16 hits). Comparing to
   `|HJSW|=3(p−1)` yields ratio `∼ 2p/3(p−1) → 2/3`. That is a comparison
   of two different geometries (board ±1 packing vs ambient T2 cut), not a
   consequence of single-H cleanliness.

3. **Even a mono cap does not force B2.** Substituting the uniform bound
   `M ≤ 2(p+1)` into B2 gives the sufficient arithmetic test
   `⌊m/3⌋ ≥ 2(p+1) + m − 3(p−1) = m − p + 5`. On board multi-H
   certificates this fails on **56/60** rows with `p≤61` (only 4/60 forced),
   while actual B2 (using the true `M`) still holds. So a proved mono-color
   capacity bound — even the tight-looking `2(p+1)` — is **not** a proof of
   B2. Large minority mass makes the worst-case-`M` surplus too big.

**Verdict:** treat B2 as an independent conjecture (or drop it as a proof
route). Do not advertise the 0.7 ratio as single-H provenance.

### Outline steps (older numbering)

1. **Color partition.** Residues `c=xy mod p` partition `S` as `⊔_c S_c`.
2. **Majority / minority.** As above.
3. **Matching (→ B1).** Mixed bad lines (Theorem A) + counting → `LB ≥ ⌊m/3⌋`.
4. **Gap.** Still need `LB ≥ surplus` (directly, or via something other than
   the failed mono-cap→B2 route).

Until there is a counting proof, Conjecture B remains open; Certificate B′
is the working substitute for the pools this repo searches.

### Mono-color cap (separate conjecture; does not unlock B2)

**Conjecture M.** For odd prime `p` and board `H(c)` on `n=2p`, every
primary-feasible `T ⊆ H(c)` has

```
|T| ≤ 2(p + 1_{p≡1 (mod 4)}).
```

Certified for `c=1` and `5≤p≤61`. Proving M is worthwhile as hyperbola
geometry; it is **not** a path to B2 (above).

## Consequences

- For the multi-hyperbola primary-then-repair pipeline, **p≥17 is a closed
  dead end** at the level of these pools: the primary surplus cannot survive
  all-slope repair whenever Certificate B′ / Conjecture B applies.
- Combined with `PROOF_SINGLE_H.md`, the obstruction is specifically
  **cross-color** incidence under primary saturation.

## What this does not claim

- Not a proof that HJSW is asymptotically optimal among all point sets.
- Not a proof for every geometric mask or every primary-feasible set.
- Not a new dense construction.

## Next step

**Theorem track:** seek a **direct counting proof** of Conjecture B
(`LB ≥ surplus` for max-primary board multi-`H`), or a counting proof of
**B1** plus a gap argument that does **not** route through mono-cap→B2.

Do **not** treat B2 as settled by the ~0.7 mono/HJSW ratio — that ratio has
no single-H provenance and the mono cap does not imply B2.

Optional side lemma: prove Conjecture M (mono primary `≤ 2(p+1_{p≡1 mod 4})`)
as hyperbola/±1 packing geometry, explicitly decoupled from Conjecture B.
