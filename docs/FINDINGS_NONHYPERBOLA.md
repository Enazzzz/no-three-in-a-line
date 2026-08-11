# Findings — non-hyperbola second families

**Date:** 2026-08-11  
**Scope:** primes `p ∈ {17,19,23,29,31}` on `n=2p`.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

Slope census showed second **modular hyperbolas** have almost no risk-0 cells
against a full `H(c0)` and only `O(1)–O(10)` against HJSW
(`FINDINGS_SLOPE_CENSUS.md`). Is that an artifact of the hyperbola equation, or
does **any** second pool fail the same way?

## Families tried

| Family | Definition (then +kp lifts to the board) |
|--------|------------------------------------------|
| `hyperbola_c2` | control: `xy ≡ 2 (mod p)` |
| `parabola` | `y ≡ x² (mod p)` |
| `circle` | `x² + y² ≡ 1 (mod p)` |
| `pell_d2` | `x² − 2y² ≡ 1 (mod p)` |
| `exponential` | `(x, g^x)` for a primitive root `g` |
| `affine_line` | `y ≡ 2x+1 (mod p)` (self-collinear junk control) |
| `middle_blocks` | all cells of HJSW middle blocks `M` |
| `board_risk0_ceiling` | **every** board cell that is risk-0 vs HJSW |
| `delete_k_then_board_risk0` | delete `k∈{1,3}` HJSW points, then board risk-0 |

Code: `research/nonhyperbola.py`  
Data: `data/nonhyperbola_scan.csv`

Fair baseline: same greedy polish budget on raw HJSW (`hjsw_polished`).

## Headline results

1. **No algebraic second family beats polished HJSW.** For every structured
   pool, `delta_vs_polished ≤ 0`. Typical risk-0 counts stay `O(1)–O(10)`,
   matching the hyperbola control — not `Θ(p)`.
2. **Board-wide ceiling also fails to win.** Against HJSW, only ~5–7% of board
   cells are risk-0 (`102/1156` at `p=17`, `189/3844` at `p=31`). Of those,
   only ~8–13 also clear primary row/col/±1 vs the seed. Enriching from the
   **entire** risk-0 set ties polished HJSW at best (`delta_vs_polished = 0`)
   and never beats it on this scan.
3. **Delete-to-unlock does not help.** Removing 1–3 HJSW points increases
   board risk-0 (e.g. `107 → 134 → 188` at `p=19`) but final size still does
   not beat the polished baseline; net often worse.
4. Side note: parabola / circle / Pell lifts, like a single hyperbola, often
   have `self_nonprim3 = 0` on these boards. Cleanliness alone is not the
   scarce resource — **compatibility with HJSW under primary capacity** is.

### Snapshot (`delta_vs_polished`)

| p | best algebraic Δ | board ceiling Δ | delete-3 Δ |
|--:|-----------------:|----------------:|-----------:|
| 17 | 0 | 0 | −1 |
| 19 | −1 | 0 | 0 |
| 23 | 0 | 0 | 0 |
| 29 | 0 | 0 | (skipped) |
| 31 | 0 | 0 | (skipped) |

## Interpretation

The obstruction is not “wrong curve.” Once HJSW occupies its primary slots,
almost every risk-0 cell is primary-blocked or mutually conflicts with other
risk-0 cells. Ordinary polish already saturates the tiny addable residue.
Swapping the second family’s equation cannot open a `Θ(p)` corridor while the
seed stays intact.

## What this is *not*

- Not a proof that no point set larger than polished HJSW exists (obviously
  false for tiny `n`; the claim is about these enrichment pipelines).
- Not a proof that a carefully co-designed pair of families (built together,
  not HJSW-first) cannot work.

## Concrete next step after this

1. Drop HJSW-first enrichment as a research mainline.
2. Prefer either:
   - a **joint** algebraic construction (two families designed together so
     mixed triples stay sparse *and* primary loads share fairly), or
   - a **proof** track: single-`H` non-primary cleanliness for all odd `p`,
     and/or `LB(p) ≥ surplus(p)` for raw multi-`H` primary optima when `p≥17`.

## Repro

```bash
PYTHONPATH=. python3 research/scan_nonhyperbola.py > data/nonhyperbola_scan.csv
```
