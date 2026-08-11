# Findings — ambient-aligned multi-hyperbola pools

**Date:** 2026-08-11  
**Claim level:** methodological correction + finite construction probe.  
**Not** an asymptotic breakthrough.

## Motivation

Earlier multi-`H` work used **board** pools from
`hyperbola_points(n,p,c)` — cells with `xy ≡ c (mod p)` **after** the
ambient→board shift. HJSW is built the other way: ambient `H(c) ∩ T2` in
`G(p)`, then translated. Those are **different** point sets.

Consequence: `HJSW ∩ multi_hyperbola_pool(...)` is often tiny (≈6–18 of
`3(p−1)` points in the scan). So “HJSW warm-start” on board pools was
frequently an empty seed + greedy fill — not a true S₂ seed.

## Fix

`research/ambient_multi_h.py` builds

```
pool = shift( ⋃_{c∈C} (H(c) ∩ region) )
```

with the **same** shift as `hjsw()`, for `region ∈ {T2, T2∪M, G(p)}`.

Then `HJSW ⊂ pool` whenever `1 ∈ C` and `region ⊇ T2` (verified in scan).

## Board vs ambient (same size, different set)

For `p=17`, residues `{1,2,3}`, T2∪M:

| Pool | Size | ∩ HJSW | ∩ each other |
|------|------|--------|--------------|
| Board multi-`H` | 192 | 6 | 40 |
| Ambient multi-`H` | 192 | **48** | 40 |

Same cardinality, largely disjoint.

## Primary packing / LB vs surplus

On **ambient** T2∪M pools, algorithmic max-primary packings **need not**
satisfy Conjecture B′ (`LB ≥ surplus`). Examples from
`data/ambient_multi_h_scan.csv`:

| p | surplus | LB | LB − surplus |
|---|---------|----|--------------|
| 19 | 13 | 9 | **−4** |
| 37 | 24 | 18 | **−6** |
| 41 | 20 | 16 | **−4** |
| 47 | 28 | 26 | **−2** |

So Conjecture B′ is **pool-dependent**: it was certified for board-coordinate
multi-`H` pools, not for ambient-aligned ones.

Predicted net `surplus − LB > 0` does **not** yield a better NTIL set under
greedy hitting + polish: hitting deletes more than the disjoint-excess LB
(LB is a lower bound, not a tight deletion plan). Repaired sizes stay at or
below fair polished HJSW (spot check `p∈{19,37,41,47}`).

## Final constructions vs fair polished HJSW

Local search inside the ambient pool, seeded from HJSW, then unstructured
polish, vs **multi-seed** polished HJSW:

| Outcome | Typical |
|---------|---------|
| Δ vs raw HJSW | +4…+8 (ordinary polish) |
| Δ vs polished HJSW | **0**, occasionally **+1…+3** |

Wins at `+1…+3` match the joint-pack / block-sacrifice noise class — not a
modular density improvement. No scaling pattern with `p`.

Data: `data/ambient_multi_h_scan.csv`  
Code: `research/ambient_multi_h.py`, `research/scan_ambient_multi_h.py`

## What this closes / reopens

**Closes:** hope that “just use ambient coordinates” + multi-`H` local search
beats polished HJSW asymptotically. Under a fair baseline it does not.

**Keeps open / clarifies:**

1. Board-pool Conjecture B′ matching proof (separate from ambient).
2. Why ambient primary can have `LB < surplus` — mixed-line geometry differs
   when colors are ambient residues, not board `xy mod p`.
3. New algebraic families / moduli co-designed with `n`.

## Do not redo

- Claiming large ambient multi-`H` wins without a multi-seed polished-HJSW
  baseline (easy to inflate Δ by comparing to raw S₂).
- Treating board `xy ≡ c` pools as ambient HJSW supersets.
