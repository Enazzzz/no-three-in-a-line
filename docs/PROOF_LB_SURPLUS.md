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

### Reduction (sufficient lemmas)

Write `M = max_c |S ∩ H(c)|` and `m = |S| − M` (majority / minority mass
under **board** coloring `xy mod p`). Let `LB` be the disjoint-excess lower
bound. Conjecture B follows from:

| Lemma | Statement | Status |
|-------|-----------|--------|
| **B1** | `LB(S) ≥ ⌊m/3⌋` | Certified 80/80 on algorithmic max-primary packs (`data/conjecture_b_lemmas_scan.csv`); **not proved** |
| **B2** | `⌊m/3⌋ ≥ surplus(S)` | Same certificate 80/80; **not proved** |

Together: `LB ≥ ⌊m/3⌋ ≥ surplus`. Code: `research/conjecture_b_lemmas.py`.

**Caveats for a proof of B1.** Minority points are **not** always all on bad
lines (min coverage ≈ 0.81 on the certificate). So B1 is not just
“cover minority by disjoint triangles.” The disjoint-excess packing still
clears `⌊m/3⌋` on every scanned row; the missing argument is a structural
matching that does not assume full coverage.

**Caveats for a proof of B2.** Equivalently
`3(p−1) − M ≥ m − ⌊m/3⌋` (majority deficit vs residual minority). On the
certificate, `surplus/m ≤ 1/4`. A usable bound may come from controlling
`M` via mono-color primary capacity (below).

### Outline steps (older numbering)

1. **Color partition.** Residues `c=xy mod p` partition `S` as `⊔_c S_c`.
2. **Majority / minority.** As above.
3. **Matching (→ B1).** Mixed bad lines (Theorem A) + disjoint excess packing
   → `LB ≥ ⌊m/3⌋` for large primary `S`.
4. **Gap (→ B2).** Uniform `⌊m/3⌋ ≥ |S|−3(p−1)`.

Until B1 and B2 are proved for max-primary `S`, Conjecture B remains open;
Certificate B′ + the B1/B2 scan are the working substitutes.

### Empirical mono-color capacity (lemma candidate)

Any primary-feasible subset of a **single** board `H(c)` is NTIL
(`PROOF_SINGLE_H`). Algorithmic max primary inside board `H(1)` is only about
`0.68–0.75` of `|HJSW|` for `17≤p≤43` (appendix in the lemma scan log) —
consistent with HJSW living in ambient T2, not board `H(1)`. A proved upper
bound `M ≤ α·3(p−1)` with `α<1` would help B2.

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

**Theorem track (preferred):** prove lemmas **B1** and **B2** above for
maximum-cardinality primary-feasible `S ⊆ U(C)` (board pools). Start with
B2 via a mono-color majority bound, then B1 via a matching that tolerates
uncovered minority points.

Construction track remains open but is secondary while the goal is a theorem
out of the multi-`H` obstruction.
