# Findings — slope census and mixed-line masks

**Date:** 2026-08-11  
**Scope:** primes `p ∈ {11,…,43}`; modular hyperbolas on `n=2p`.  
**Claim level:** empirical. **Not** an asymptotic breakthrough.

## Question

Structured geometric schedules still had `LB ≥ surplus`
(`FINDINGS_STRUCTURED.md`). Can we instead **forbid the slopes that
carry non-primary triples** — by understanding which lines are bad on
`H(c)` and `H(c0)∪H(c1)`, then masking those meetings before packing?

## Headline law

On every scanned prime:

1. A **single** modular hyperbola `H(c)` has **zero** non-primary lines
   with ≥3 board points. The only ≥3-lines inside one `H` are **primary**
   (row / column / slope ±1), with multiplicity up to 4.
2. In a union `H(c0)∪H(c1)`, **every** non-primary ≥3-line is **mixed**
   (uses both residues). Pure same-`c` non-primary triples do not appear.
3. Mixed-line splits are dominated by `(2,1)` and `(2,2)` color patterns.

So multi-hyperbola non-primary damage is entirely **cross-hyperbola**.
Single-`H` sets are already all-slope-clean once primary capacities hold.

Code: `research/slope_census.py`  
Data: `data/slope_census_scan.csv`

## Mask constructions tried

| Family | Idea |
|--------|------|
| `single_h_primary` | Primary-pack one `H(c)` (already non-primary clean) |
| `mixed_kill_then_primary` | Greedy/exact hit all mixed lines on `H(c0)∪H(c1)`, then primary-pack |
| `risk_masked` (`full`) | Keep only `H(c1)` points with risk 0 vs full `H(c0)` |
| `risk_masked` (`primary`) | Risk 0 vs a primary packing of `H(c0)` |
| `hjsw_protected_enrich` | Never delete HJSW; add individually all-slope-ok extras |

Fair baseline: same greedy polish budget on raw HJSW (`hjsw_polished`).

## Results (snapshot)

| p | union mixed | full-risk safe | prim-risk safe | mixed deleted | best vs polished |
|--:|------------:|---------------:|---------------:|--------------:|------------------|
| 19 | 356 | 0 | 20 | 68 | polished wins / ties |
| 31 | 708 | 4 | 22 | 131 | polished wins / ties |
| 37 | 1136 | 0 | 13 | 177 | polished wins / ties |
| 43 | 1440 | 0 | 17 | 185 | polished wins / ties |

Across the scan:

- `union_pure = 0` and `union_all_mixed = 1` on **all** rows.
- Risk vs **full** `H(c0)` is essentially total (`safe ≈ 0`): almost every
  `H(c1)` point completes a non-primary triple with some pair in `H(c0)`.
- Risk vs a **primary packing** of `H(c0)` frees ~10–25 extras, but after
  residual mixed hitting + primary re-pack + polish the final size stays
  **below** polished HJSW (typical Δ ≈ −2…−7).
- Mixed-line hitting deletes ~Θ(p) points (often matching the exact min
  count on these sizes), wiping the naive union surplus before primary
  packing can help.
- `hjsw_protected_enrich` does not beat the polished-HJSW baseline; gains
  attributed to “extras” were mostly ordinary polish.

## Interpretation

1. **Slope forbidding cannot be “local to one residue.”** One `H` is already
   non-primary-clean; the obstruction appears only when residues mix.
2. **Cross-color incidence is dense.** Against the full first hyperbola,
   second-hyperbola cells are almost all immediately illegal. Against a
   thinned primary subset there is some room, but not enough room to beat
   the classical geometric cut `T2∪M` after repair.
3. This reframes the earlier LB≥surplus story: the mandatory deletions are
   paying for **mixed** triples, not for structure inside a single `H(c)`.

## What this is *not*

- Not a proof that every single `H(c)` is non-primary-clean for all odd
  primes (only scanned through 43, with spot checks to 61).
- Not progress past the HJSW asymptotic density.

## Concrete next step after this

1. **Prove** the single-hyperbola law (no non-primary 3-term progression on
   the `n=2p` board lifts of `xy ≡ c (mod p)`).
2. Or design a second point set that is **not** a second modular hyperbola —
   e.g. a different algebraic curve / random lift — chosen so mixed triples
   with HJSW stay sparse enough that risk-0 extras are Θ(p).
3. Optional: formalize `LB(p) ≥ surplus(p)` for raw max-primary multi-`H`
   pools for all odd `p≥17` (still open as a proof).

## Repro

```bash
PYTHONPATH=. python3 research/scan_slope_census.py > data/slope_census_scan.csv
```
