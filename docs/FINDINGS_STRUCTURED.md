# Findings — structured schedules vs non-primary slope load

**Date:** 2026-08-11  
**Scope:** primes `p ≤ 83`; schedules that avoid stacking several `H(c)` on the
same geometric support.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

Raw multi-hyperbola unions produce a primary surplus over HJSW that a deletion
**lower bound** already cancels (`FINDINGS_ALLSLOPE_HITTING.md`). Can a
**structured** support — assigning different residues to disjoint bands/blocks —
keep a primary surplus while driving the non-primary LB below that surplus?

## Schedules tried

| Schedule | Rule |
|----------|------|
| `column_band` | `x≤p` ← `H(c0)`, `x>p` ← `H(c1)` |
| `row_band` | `y≤p` ← `H(c0)`, `y>p` ← `H(c1)` |
| `block_partition` | translated T2 ← `H(c0)`, middle M ← `H(c1)` |
| `chessboard` | coarse 2×2 block coloring, alternate residues |

Code: `research/structured_schedule.py`  
Data: `data/structured_schedule_scan.csv`

## Headline results

1. **Raw pools:** `LB ≥ surplus` on **all 10** scanned primes (strengthens the
   earlier `p≥17` table; tiny primes meet equality / non-negative gap too in
   this max-primary sample).
2. **Structured pools:** also `LB ≥ surplus` on **all 10**. Separating supports
   did **not** open a window where primary surplus outruns mandatory deletions.
3. **Final density:** structured + polish sometimes beats raw HJSW by a few
   points on small `p` (finite-gain band, ratios ~1.48–1.55). By `p∈{71,83}`
   the sweep falls back to plain HJSW.
4. Structured often **reduces** primary size below HJSW (negative surplus) —
   safer geometrically, but then there is nothing left to “spend” on density.

### Snapshot

| p | raw surplus | raw LB−sur | best schedule | struct surplus | struct LB−sur | final |
|---|------------:|-----------:|---------------|---------------:|--------------:|------:|
| 19 | 7 | +6 | block_partition | −8 | +16 | 59 |
| 31 | 6 | +19 | column_band | +6 | +16 | 94 |
| 61 | 27 | +32 | row_band | +12 | +33 | 182 |
| 83 | 28 | +53 | (HJSW fallback) | 0 | 0 | 246 |

## Interpretation

Disjoint geometric supports are not enough. Non-primary 3-term progressions
still form **inside** a single band/block and across the cut. The obstruction
is not merely “two hyperbolas occupying the same cells”; it is the additive
structure of hyperbola point sets on lines of slope `∉ {0,∞,±1}`.

So the next constructive bar is higher: a schedule must constrain **which
slopes can meet three times**, not only which region uses which `c`.

## What this is *not*

- Not a proof that no structured multi-hyperbola works.
- Not progress on the asymptotic record past HJSW.

## Concrete next step after this

1. Algebraic slope census: for `H(c) ∩` a fixed mask, describe lines of slope
   `s` with ≥3 points and forbid those `s` by mask design.
2. Or prove formally `LB(p) ≥ surplus(p)` for raw max-primary pools for all
   odd `p≥17` (now empirically clean through 83).

## Repro

```bash
PYTHONPATH=. python3 research/scan_structured_schedule.py > data/structured_schedule_scan.csv
```
