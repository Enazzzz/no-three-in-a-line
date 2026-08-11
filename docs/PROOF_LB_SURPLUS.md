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

The only scanned failure of `LB≥surplus` among small primes is
`p=7` with `C={1,2,6}` (`gap=−2`), matching `FINDINGS_ALLSLOPE_HITTING.md`.

```bash
PYTHONPATH=. python3 research/scan_lb_surplus.py --lo 7 --hi 80 > data/lb_surplus_scan.csv
```

## Proof outline toward Conjecture B (incomplete)

1. **Color partition.** Residues `c=xy mod p` partition `S` as `⊔_c S_c`.
2. **Majority / minority.** Let `M = max_c |S_c|` and `m = |S|−M` (minority
   mass). For max-primary `S` one expects `M` close to the mono-color NTIL
   scale while `m` is forced upward by the cardinality objective.
3. **Matching.** Because bad lines are mixed (Theorem A) and typically have
   size 3, a disjoint packing of bad lines yields
   `LB(S) ≥ ν` with `ν` on the order of `m/3` when minority points are almost
   all incident to some bad line (observed: minority coverage ≳90%).
4. **Gap.** Need a uniform inequality `ν ≥ |S|−3(p−1)`. Missing piece: a
   lower bound on `ν` in terms of `|S|` and `p` that does not depend on the
   algorithmic packing.

Until step 4 is closed, Conjecture B remains open; Certificate B′ is the
working substitute for the pools this repo actually searches.

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

Either finish step 4 of the outline (matching bound for max-primary `S`),
or leave the proof track and seek a construction that is not a multi-`H`
primary packing.
