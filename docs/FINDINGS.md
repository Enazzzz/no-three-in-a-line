# Findings — next step (hyperbola unions)

**Date:** 2026-08-11  
**Scope:** VM-limited scans on known interesting odd primes `p ≤ 181` (`n = 2p`).  
**Claim level:** empirical progress report. **Not** an asymptotic breakthrough.

## Goal of this step

Prior work showed classical HJSW polishing is bottlenecked by *non-primary*
slopes: four-constraint survivors grow with `p`, but individually addable
cells stay `O(10–50)`. The planned next step (KNS Remark 3.4 direction) was:

> change the seed — try unions of hyperbolas with careful slope-`±1` deletion —
> instead of polishing a single HJSW hyperbola.

## Methods compared

| Method | Description |
|--------|-------------|
| `hjsw` | Classical S₂, size `3(p−1)` |
| `subset` | HJSW + exact/greedy MIS on all-slope-safe cells + short greedy polish |
| `union` | HJSW seed + greedily add `H(c₁)` (and short multi-`c` chains) with horiz/vert/`±1` + all-slope filters + polish |

Data: `data/hyperbola_union_scan.csv`, `data/second_hyperbola_pool.csv`.

## Headline results

1. **Augmentation beats raw HJSW**, and often clears `1.55n`, on every scanned prime — but only by **additive** amounts (roughly `+8` to `+24` points in this range).
2. **Hyperbola-union does not systematically beat algebraic subset.**  
   On 18 primes: subset best on **13**, union best on **5**, mean size delta
   `union − subset ≈ +0.1` (range `−2 … +2`).
3. **Why union under-delivers:** points from a second hyperbola `H(c₁)` are
   almost never individually addable to HJSW after *all* slopes are checked.
   Typical `indiv_ok` from the best `c₁` is **0–2**, while the full-board
   individually-ok pool is **8–40**. Primary-class (`±1`) filters leave a
   medium pool; general slopes wipe it.

### Ratios (means over `p ≤ 181`)

| Family | Mean ratio |
|--------|------------|
| HJSW | ≈ 1.447 |
| subset | ≈ 1.567 |
| union | ≈ 1.567 |

Both augmented families sit near `~1.56` here; that is compatible with
`1.5n + O(1)`–style gains and does **not** establish a constant-factor
improvement for large `n`.

## Interpretation

- The algebraic diagnosis was right: **non-`{0,∞,±1}` slopes** are the real
  filter on HJSW extras.
- A naive “paste on another hyperbola and delete `±1` conflicts” does **not**
  open a large new safe set relative to HJSW, because those extra hyperbola
  points still collide with S₂ on other slopes.
- Multi-`c` chaining rarely helps beyond a single secondary residue for the
  same reason — there is almost nothing safe to chain.

## What this is *not*

- Not a proof that `3/2` is tight.
- Not a construction with ratio `≥ 3/2 + ε` for large `n`.
- Not a failure of the broader KNS idea — only of the **HJSW-seeded greedy
  second-hyperbola** instantiation we actually ran.

## Concrete next step after this

Stop grafting onto a frozen HJSW S₂. Instead try one of:

1. **Simultaneous multi-hyperbola design:** choose a small set of residues
   `C ⊂ F_p^×`, take `⋃_{c∈C} (H(c) ∩ T*)` for a redesigned block mask `T*`,
   then delete on saturated `±1` (and measure all-slope survivors).
2. **Delete-first unions:** form a large multi-hyperbola set, remove a
   hitting set for saturated `±1` classes, *then* repair other slopes.
3. **Distributed sweep** of residue tuples `(c0,c1,c2)` with independent
   verification — only after a local prototype shows a growing additive term.

Until one of those shows **individually-ok density that grows with `p`**,
treat `>1.55n` wins as sparse finite artifacts.

## Follow-up (same day): simultaneous / delete-first

See **`FINDINGS_MULTI_HYPERBOLA.md`**. Short version: greedy delete-first /
keep on raw multi-hyperbola unions beats HJSW slightly on tiny primes but
**loses to HJSW-subset** as `p` grows, and falls back to HJSW by `p≈83`.
Unstructured deletion does not beat the classical S₂ transversal.

## Follow-up: exact primary repair

See **`FINDINGS_PRIMARY_REPAIR.md`**. Exact max subset under ≤2 per
row/col/±1 **can exceed HJSW by ~Θ(p)**, but all-slope repair deletes more
than the surplus. Primary classes are not the binding obstruction; other
slopes are.

## Follow-up: hitting-set lower bounds

See **`FINDINGS_ALLSLOPE_HITTING.md`**. For `p≥17`, a disjoint-excess lower
bound on mandatory general-slope deletions **already exceeds** the primary
surplus over HJSW — so the surplus cannot survive optimal repair.

## Follow-up: structured schedules

See **`FINDINGS_STRUCTURED.md`**. Column/row bands, T2/M partition, and
chessboard residue schedules still satisfy `LB ≥ surplus` on all scanned
primes; disjoint supports do not remove the non-primary obstruction.

## Repro

```bash
PYTHONPATH=. python3 research/scan_hyperbola_union.py > data/hyperbola_union_scan.csv
PYTHONPATH=. python3 -c "from research.hyperbola_union import compare_methods; print(compare_methods(31))"
```
