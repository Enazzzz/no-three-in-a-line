# Findings — ambient redesign (boards other than n=2p)

**Date:** 2026-08-11  
**Claim level:** theorem sharpening + empirical density probes.  
**Not** an asymptotic breakthrough.

## Question

Is the HJSW board size `n=2p` an arbitrary convention, or is it forced by
the modular hyperbola’s lift geometry? Can denser constructions live on
`n ≠ 2p`?

## Sharp cleanliness bound

Extending `PROOF_SINGLE_H.md`:

| Board size | Max lifts per `F_p^*` residue | Single-`H` non-primary ≥3-lines |
|------------|-------------------------------|----------------------------------|
| `n ≤ 2p` | ≤ 2 | **none** (theorem) |
| `n = 2p+1` | ≥ 3 (residue `1` lifts to `1,1+p,1+2p`) | **appear** (certified) |
| `n = 3p` | 3 | many (dozens–hundreds) |

Certificate: all odd primes `p≤79` are clean at `n=2p` and dirty at
`n=2p+1` (`data/ambient_sharp_scan.csv`).

So **`n=2p` is the largest board on which the two-lift single-`H` argument
works.** Growing the board with the same modulus immediately imports
non-primary triples inside one hyperbola.

Code: `research/ambient.py`

## Density probes

Relative to polished HJSW on `n=2p`:

1. **Crop** to `n=2p−k`: ratios typically **fall** (fewer points, similar
   structure).
2. **Expand** to `n=2p+1` or `n=3p` with hyperbola packs / HJSW-fit polish:
   ratios land near `1.40–1.56`, **not** systematically above the `n=2p`
   baseline (~`1.52–1.58` in the same polish budget).
3. **Lift-restricted subsets** on `n=3p` (keep only lifts in `{0,1}²`) still
   underperform HJSW’s ratio on `n=2p`.
4. Side note: Erdős parabola on `p×p` polishes to ~`1.45–1.59` on small `p`
   but trends toward ~`1.47` as `p` grows — not a `3/2` beater.

## Interpretation

The classical ambient is not a historical accident. Once you commit to
modular hyperbolas with modulus `p`, the clean lift window stops at `n=2p`.
“Just use a bigger board” is not available without either

* changing the modulus with `n`, or
* accepting same-color non-primary damage and repairing it (the multi-`H`
  obstruction from `PROOF_LB_SURPLUS.md`).

## What this is *not*

- Not a proof that no construction on `n ≠ 2p` can beat `3/2`.
- Not progress past HJSW density.

## Concrete next step after this

- Finish Conjecture B (max-primary matching) on the classical board, or
- Change the **algebraic family** (not just `n`), co-designed with a cut
  that does not rely on two-lift cleanliness.

## Repro

```bash
PYTHONPATH=. python3 research/scan_ambient.py --limit 80 --density > data/ambient_sharp_scan.csv
```
