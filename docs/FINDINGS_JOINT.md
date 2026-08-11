# Findings — joint all-slope packing

**Date:** 2026-08-11  
**Scope:** primes `p ∈ {17,…,43}`; joint pools `H(1)∪H(2)∪parabola∪circle`.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

HJSW-first enrichment is saturated (`FINDINGS_NONHYPERBOLA.md`). Can a
**joint** search — packing two or more algebraic families together under
primary + all-slope constraints from the start — beat polished HJSW by a
scaling margin?

## Methods

| Method | Idea |
|--------|------|
| `greedy_from_empty` | Multi-start degree-greedy on the joint pool; never seeds HJSW |
| `local_search` | Start at HJSW; add / delete-1-refill / ruin-recreate inside the pool |
| baseline | Same polish budget on raw HJSW |

Code: `research/joint_pack.py`  
Data: `data/joint_pack_scan.csv`

## Results

| p | polished HJSW | empty final | local final | Δ vs polished | winner |
|--:|--------------:|------------:|------------:|--------------:|--------|
| 17 | 54 | 49 | 54 | 0 | hjsw_polished |
| 19 | 60 | 54 | 60 | 0 | hjsw_polished |
| 23 | 71 | 67 | 73 | +2 | joint_local |
| 29 | 88 | 82 | 89 | +1 | joint_local |
| 31 | 98 | 88 | 98 | 0 | hjsw_polished |
| 37 | 115 | 107 | 115 | 0 | hjsw_polished |
| 41 | 124 | 122 | 124 | 0 | hjsw_polished |
| 43 | 131 | 126 | 132 | +1 | joint_local |

1. **Empty joint greedy systematically underperforms** polished HJSW (gap
   often ~4–10 points). The classical `T2` cut still wins as a seed.
2. **Local search finds occasional O(1) finite gains** (+1 or +2 on a few
   primes). These are the same class of noise as earlier contest-ratio
   spikes — they do **not** grow with `p`.
3. On half the scan, joint local search merely recovers the polished baseline.

## Interpretation

Building families together under an all-slope oracle does not unlock a new
density regime on these pools. Whatever structure HJSW exploits in one
hyperbola ∩ `T2` is not improved by freely mixing a second hyperbola and
two other modular curves at this search depth.

## What this is *not*

- Not a proof that no joint algebraic construction works.
- Not progress past the HJSW asymptotic density.

## Concrete next step after this

Prefer the **proof** track for a while:

1. ~~Prove single-`H` non-primary cleanliness on `n=2p`~~ — done:
   `docs/PROOF_SINGLE_H.md`.
2. Prove `LB(p) ≥ surplus(p)` for raw max-primary multi-`H` pools for odd
   `p≥17`.

If returning to constructions: need a new geometric cut (not just a larger
joint pool + local search).

## Repro

```bash
PYTHONPATH=. python3 research/scan_joint_pack.py > data/joint_pack_scan.csv
```
