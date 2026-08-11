# Findings — exact primary-class repair

**Date:** 2026-08-11  
**Scope:** primes `p ≤ 67`, multi-hyperbola pools `|C|≤3`, branch-and-bound max
subset with ≤2 points per row/col/slope-`±1`, then all-slope repair.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

Previous steps showed unstructured greedy deletion on multi-hyperbola unions
loses to HJSW. Was that because we failed to pack the **primary** classes
optimally? Exact primary repair asks:

> How large can a multi-hyperbola subset be if we only enforce horiz/vert/±1
> capacities, and what happens when other slopes are repaired afterward?

## Method

1. Pool = `⋃_{c∈C} H(c)` on `n=2p` (with/without T2 mask).
2. **Exact-ish primary max:** branch-and-bound (greedy warm-start) for maximum
   subset with every primary class size `≤ 2`.
3. Count general-slope collinear triples in that set.
4. Greedy all-slope repair → optional short polish → verify.

Code: `research/primary_repair.py`  
Data: `data/primary_repair_scan.csv`, `data/primary_surplus_diag.csv`

## Headline result

**Primary packing can beat HJSW — sometimes by `Θ(p)`.**  
**All-slope repair then deletes *more* than that surplus.**

Max-primary surplus examples (unmasked multi-hyperbola pools):

| p | HJSW | primary | Δ primary | gen triples | after repair | repair loss | final vs HJSW |
|---|-----:|--------:|----------:|------------:|-------------:|------------:|--------------:|
| 7 | 18 | 24 | +6 | 6 | 20 | 4 | +3 |
| 19 | 54 | 62 | +8 | 78 | 36 | 26 | +5 |
| 31 | 90 | 106 | +16 | 134 | 62 | 44 | +6 |
| 37 | 108 | 122 | +14 | 143 | 74 | 48 | 0 |
| 61 | 180 | 207 | +27 | (large) | 105 | 102 | −3 |
| 67 | 198 | 225 | +27 | (large) | 125 | 100 | −4 |

So:

1. The four primary classes are **not** the binding asymptotic obstruction for
   these multi-hyperbola pools — there exist primary-feasible sets larger than
   classical S₂.
2. The binding obstruction is **other slopes**. Repair cost grows at least as
   fast as the primary surplus in this range.
3. Final verified sizes still sit in the same finite-gain band as HJSW-subset
   polishing; no evidence of ratio `≥ 3/2 + ε`.

## Interpretation

This closes a plausible loophole from `FINDINGS_MULTI_HYPERBOLA.md`
(“maybe greedy deletion was just a bad primary repair”). Exact primary packing
confirms the surplus is real **and** confirms it is eaten by non-primary
collinearities.

KNS-style “delete carefully on ±1” is therefore insufficient by itself for
multi-hyperbola unions on the full board: after ±1/horiz/vert are clean, the
set is still full of other 3-term APs.

## What this is *not*

- Not a new record construction.
- Not a proof that `3/2` is tight.
- Not a claim that every structured multi-hyperbola mask fails — only that
  **capacity-exact repair of raw unions** does not yield lasting density.

## Concrete next step after this

If continuing, prefer **algebraically structured** designs where non-primary
slopes are controlled *by construction* (e.g. block masks / residue schedules
that limit arbitrary slopes), not post-hoc deletion of a dense raw union.
Alternatively, quantify the growth rate of min all-slope hitting-set size on
these primary-optimal sets (even a lower bound would be progress).

## Repro

```bash
PYTHONPATH=. python3 research/scan_primary_repair.py > data/primary_repair_scan.csv
```
