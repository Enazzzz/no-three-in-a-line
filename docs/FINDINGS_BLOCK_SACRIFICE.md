# Findings — HJSW T2 block sacrifice

**Date:** 2026-08-11  
**Scope:** primes `p ∈ {17,…,61}`; multi-seed polish baseline.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

Multi-hyperbola primary-then-repair is closed for `p≥17`
(`PROOF_LB_SURPLUS.md`). Can a **geometric** edit of HJSW — delete one T2
half-block, optionally refill from middle-block hyperbola cells, then polish —
beat polished HJSW by a scaling margin?

## Method

1. Multi-seed polish of raw HJSW (fair baseline).
2. For each of the twelve T2 half-blocks: delete its HJSW points; optionally
   greedily refill from `M∩H(1)`, `M∩H(2)`, `M∩(H1∪H2)`, or `H(2)`.
3. Multi-seed polish the result.
4. Control: random deletions of the same cardinality (no refill).

Code: `research/block_sacrifice.py`  
Data: `data/block_sacrifice_scan.csv`

## Results

| p | baseline | best | Δ | beats random-max? |
|--:|---------:|-----:|--:|:-----------------:|
| 17 | 54 | 55 | +1 | no |
| 19 | 60 | 60 | 0 | no |
| 23 | 71 | 72 | +1 | no |
| 29 | 88 | 91 | +3 | no |
| 31 | 98 | 99 | +1 | no |
| 37 | 116 | 117 | +1 | no |
| 41 | 124 | 126 | +2 | no |
| 43 | 132 | 134 | +2 | no |
| 47 | 143 | 147 | +4 | **yes** (once) |
| 53 | 162 | 163 | +1 | no |
| 61 | 192 | 192 | 0 | no |

1. Gains are **O(1)** and do not grow with `p` (gone by `p=61` in this sweep).
2. Best tags often use refill `none` — the move is “delete a block then
   re-polish,” not a successful middle-block graft.
3. Structured drops **rarely beat** the best random drop of the same size;
   typical structured Δ sits inside the random-drop noise band.

## Interpretation

HJSW is not a uniquely optimal polish seed: removing a few points can change
the greedy-augmentation path by O(1). That is polish stochasticity / local
search noise, not a new geometric density regime. Middle-block refill after
sacrifice does not systematically help.

Side probe (not in CSV): tiling two HJSW copies on an `n=4p` board
(v-/h-stack) lands at ratio ~1.41–1.45, **below** `3/2`.

## What this is *not*

- Not progress past the HJSW asymptotic density.
- Not evidence that no geometric surgery on T2 can work — only that
  single-block sacrifice + M/H refill + greedy polish does not.

## Concrete next step after this

Prefer constructions that change the **ambient design** (different `n` vs
`p` relation, non-hyperbola families co-designed with a new cut, or a
finished matching proof for Conjecture B), not further polish-seed surgery
on S₂.

## Repro

```bash
PYTHONPATH=. python3 research/scan_block_sacrifice.py > data/block_sacrifice_scan.csv
```
