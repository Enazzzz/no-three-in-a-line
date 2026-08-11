# Findings — simultaneous / delete-first multi-hyperbola

**Date:** 2026-08-11  
**Scope:** primes `p ≤ 97` (`n = 2p`), residue sets `|C| ≤ 3`, optional T2 mask.  
**Claim level:** empirical progress report. **Not** an asymptotic breakthrough.

Follows `docs/FINDINGS.md` (hyperbola-grafting step). That note asked for
**simultaneous / delete-first** designs that do not graft onto a frozen HJSW S₂.

## What we built

`research/multi_hyperbola.py`:

1. **Pool:** `⋃_{c∈C} H(c)` on the `n=2p` board, optionally ∩ translated T2.
2. **`delete_first`:** delete points until every row/col/slope-`±1` class has
   `< 3` points; then greedy-keep for all-slope safety; short polish.
3. **`greedy_keep`:** simultaneous one-pass keep from the raw union with
   primary caps + slope tables.

Scanner: `research/scan_multi_hyperbola.py` → `data/multi_hyperbola_scan.csv`.

## Headline results (`p ≤ 97`)

| Method | Wins (best ratio) | Mean ratio |
|--------|-------------------|------------|
| HJSW | 0 / 11 | ≈ 1.421 |
| subset (HJSW + MIS polish) | **9 / 11** | ≈ 1.552 |
| multi (best delete-first / greedy-keep) | 2 / 11 | ≈ 1.530 |

- Multi beats raw HJSW modestly on small primes (typical `+3…+5` points).
- Multi **loses to subset** as `p` grows: mean `multi − subset ≈ −4` points
  (range `−14…+1`). At `p ∈ {83,97}` the sweep fell back to plain HJSW.
- Clearing `1.55n` still happens for some small `p`, but density does **not**
  improve with `|C|` in a way that looks like `ε n`.

### Reading of the failure mode

Raw multi-hyperbola pools are large (`|C|=3` ∩ T2 is ~3× HJSW), but after
primary-class deletion the survivor set is only ~HJSW-sized, and the subsequent
all-slope greedy-keep **shrinks below** the classical structured S₂ selection.
In other words: HJSW is already a strong structured transversal of one
hyperbola; unstructured deletion on a bigger union does not discover a denser
safe subset with this greedy budget.

## What this is *not*

- Not a refutation of every multi-hyperbola idea (structured block masks,
  matching-based ±1 hitting sets, ILP on small `p`, etc. remain open).
- Not evidence for ratio `≥ 3/2 + ε`.

## Concrete next step after this

The greedy delete-first / keep pipeline on raw unions is a **measured dead end**
at this compute scale. Higher-leverage attempts:

1. **Structured masks:** design `T*` so several hyperbolas contribute
   *disjoint* primary classes (algebraic scheduling), not post-hoc deletion.
2. **Exact primary repair:** on small `p`, solve min-deletions to make all
   row/col/±1 classes ≤2 (ILP / matching), then measure all-slope damage.
3. **Stop chasing finite `>1.55` flukes** unless a construction shows
   individually-ok extras **growing with `p`**.

## Repro

```bash
PYTHONPATH=. python3 research/scan_multi_hyperbola.py > data/multi_hyperbola_scan.csv
```
