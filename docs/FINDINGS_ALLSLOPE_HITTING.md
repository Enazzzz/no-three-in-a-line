# Findings — all-slope hitting bounds vs primary surplus

**Date:** 2026-08-11  
**Scope:** max primary-feasible multi-hyperbola sets for `p ≤ 61`.  
**Claim level:** empirical lower bounds + exact small cases. **Not** a full
asymptotic proof, but a quantitative obstruction.

## Question

`FINDINGS_PRIMARY_REPAIR.md` showed primary packing can beat HJSW by ~Θ(p),
yet greedy all-slope repair ate the surplus. Was that just a bad repair, or
is the surplus **provably unsustainable**?

## Method

On a primary-optimal set `S`:

1. Enumerate non-primary lines with `k ≥ 3` points of `S`.
2. Each such line forces ≥ `k−2` deletions on that line.
3. Compute:
   - **LB:** greedy disjoint-excess packing (sum of excesses on point-disjoint lines)
   - **UB:** greedy hitting (delete max-excess points)
   - **Exact min deletions:** BnB when the instance is tiny
4. Compare LB / exact deletions to `surplus = |S| − |HJSW|`.

Code: `research/allslope_hitting.py`  
Data: `data/allslope_hitting_scan.csv`

## Headline result

**From `p ≥ 17`, the disjoint-excess lower bound already exceeds the primary surplus.**  
So even an *optimal* all-slope repair cannot keep a HJSW-beating primary set
of this form — at least `LB − surplus` extra points must go, forcing final size
`≤ |HJSW|` (and typically below, once UB/exact are used).

| p | surplus | LB deletions | LB − surplus | min del (UB/exact) | kept − HJSW |
|---|--------:|-------------:|-------------:|-------------------:|------------:|
| 5 | 4 | 4 | 0 | 4 (exact) | 0 |
| 7 | 6 | 4 | −2 | 4 (exact) | +2 |
| 17 | 8 | 14 | **+6** | 18 | −10 |
| 19 | 8 | 14 | **+6** | 21 | −13 |
| 31 | 16 | 27 | **+11** | 36 | −20 |
| 37 | 14 | 31 | **+17** | 40 | −26 |
| 61 | 27 | 59 | **+32** | 84 | −57 |

Tiny primes (`p≤7`) still allow a scrap of room; the gap **opens and widens**
after that.

## Interpretation

1. The primary surplus over HJSW is real.
2. It is **not an artifact of bad repair** for `p≥17`: a combinatorial lower
   bound on mandatory deletions already cancels it.
3. Therefore “pack primary classes harder on raw multi-hyperbola unions” is
   closed as a path to beating `3/2`.
4. Any construction that hopes to beat HJSW must ensure that **non-primary
   lines never accumulate excess** in the first place (structure), or prove a
   different pool where LB stays below surplus as `p→∞`.

## What this is *not*

- Not a proof that HJSW is asymptotically optimal among all constructions.
- Not a proof for every multi-hyperbola mask — only for the primary-optimal
  sets arising from the pools we actually built (`⋃ H(c)`, optional T2).
- Not a new dense construction.

## Concrete next step after this

Shift from deletion analysis to **construction constraints**: design point
sets (masks / residue schedules) whose non-primary line loads are capped by
algebra, then measure whether primary density can still exceed `3(p−1)`.

Optional analytic follow-up: prove `LB(p) ≥ surplus(p)` for **maximum**
primary packings of these pools for all odd primes `p≥17`. See
`docs/PROOF_LB_SURPLUS.md` for the precise statement, NTIL counterexamples
to the universal primary-feasible claim, and a certificate through `p≤79`.

## Repro

```bash
PYTHONPATH=. python3 research/scan_allslope_hitting.py > data/allslope_hitting_scan.csv
```
