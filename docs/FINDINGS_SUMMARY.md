# Research summary — no-three-in-line

**Date:** 2026-08-11  
**Repo:** dense no-three-in-line on `{1,…,n}²`  
**Classical barrier:** HJSW (1975) achieves `(3/2)n − o(n)`  
**This document:** one-page synthesis of all findings and proofs in `docs/`.  
Detail and data live in the linked write-ups; this file is the map.

---

## Bottom line

1. **No asymptotic progress past `3/2`.** Nothing here beats HJSW by a fixed
   positive density. Finite ratios `>1.55n` on special primes are polish /
   search noise on top of HJSW, not a new construction family.
2. **Two theorems landed:**
   - A single modular hyperbola on boards of size `n ≤ 2p` has **no**
     non-primary 3-line (`PROOF_SINGLE_H.md`). The bound is **sharp**:
     dirty at `n = 2p+1` (`FINDINGS_AMBIENT.md`).
   - Consequently, all non-primary damage in multi-hyperbola pools is
     **cross-color / mixed**.
3. **Multi-hyperbola primary-then-repair is closed** for the pools this repo
   searches: for `p ≥ 17`, algorithmic max-primary packings have
   deletion lower bound `LB ≥ surplus` over HJSW (`PROOF_LB_SURPLUS.md`,
   80/80 cases through `p ≤ 79`). A full matching proof for every
   max-primary set remains open; the *universal* claim for every
   primary-feasible set is **false** (in-pool NTIL counterexamples).
4. **HJSW-first grafting and S₂ surgery are saturated** — second curves,
   board-wide risk0, joint search, T2 block sacrifice, same-modulus board
   growth: all O(1) or worse vs polished HJSW.

**Honest status:** the obstruction map is much clearer; the asymptotic
record is unchanged.

---

## Setup (notation)

- Odd prime `p`, classical board `n = 2p`.
- Modular hyperbola
  `H(c) = {(x,y) : xy ≡ c (mod p), p ∤ x, p ∤ y}` with board lifts.
- **Primary** directions: rows, columns, slopes `±1` (capacity ≤2 in a
  valid set).
- **HJSW / S₂:** `H(c) ∩ T2` (twelve half-blocks), size `3(p−1) = (3/2)n − 3`.
- **Surplus** of a set `S`: `|S| − 3(p−1)`.
- **LB:** disjoint-excess lower bound on deletions needed to clear
  non-primary ≥3-lines.

---

## What is proved

### Theorem — single hyperbola is non-primary-clean for `n ≤ 2p`

On `{1,…,n}²` with `n ≤ 2p`, every ≥3-point line inside one `H(c)` is
primary.

**Idea:** each `F_p^*` residue has at most two lifts, so same-residue chords
are primary; three distinct residues cannot be collinear on `xy = c` over
`F_p` (quadratic); board collinearity forces that F_p condition.

**Sharpness:** at `n = 2p+1`, residue `1` gets lifts `1, 1+p, 1+2p`;
non-primary triples appear. Certified for all odd primes `p ≤ 79`.

→ `docs/PROOF_SINGLE_H.md`, `docs/FINDINGS_AMBIENT.md`

### Corollary — multi-hyperbola damage is mixed-only

In any subset of `⋃_c H(c)`, every non-primary ≥3-line uses ≥2 residues.

---

## What is certified (not fully proved)

### Conjecture B′ — `LB ≥ surplus` for large multi-`H` primary packings

For odd primes `17 ≤ p ≤ 79` and default residue sets with `|C| ≥ 2`, the
best-of (HJSW warm-start / exact BnB / greedy) primary packing `S` of
`⋃_{c∈C} H(c)` satisfies `LB(S) ≥ |S| − 3(p−1)`. Gap widens with `p`.

**Scope warning:** false for arbitrary primary-feasible sets — an in-pool
NTIL set can beat HJSW by a few points with `LB = 0`.

→ `docs/PROOF_LB_SURPLUS.md`, earlier table in `FINDINGS_ALLSLOPE_HITTING.md`

---

## Dead-end map (do not redo)

| Approach | Result | Detail |
|----------|--------|--------|
| HJSW + unstructured greedy polish | Finite `>1.55n` on special `p`; no modular pattern; not asymptotic | Phase 2 / `RESEARCH.md` |
| S₃/S₄ middle-hyperbola + hitting repair | Returns to ~HJSW size | Phase 2 |
| Four-constraint survivors → subset MIS | Survivors grow; all-slope-ok pool stays O(10–50); +O(1)–O(10) only | Phase 6 |
| HJSW + second hyperbola (±1 / all-slope graft) | Individually-ok extras typically 0–2; no systematic win | `FINDINGS.md` |
| Raw multi-`H` delete-first / greedy-keep | Loses to subset; falls back to HJSW by `p ≈ 83` | `FINDINGS_MULTI_HYPERBOLA.md` |
| Exact primary max on multi-`H`, then all-slope repair | Primary surplus ~Θ(p); repair deletes more than surplus | `FINDINGS_PRIMARY_REPAIR.md` |
| Hitting LB vs surplus | For `p ≥ 17`, `LB > surplus` on these pools | `FINDINGS_ALLSLOPE_HITTING.md` |
| Band / block / chessboard residue schedules | Still `LB ≥ surplus`; geometric separation insufficient | `FINDINGS_STRUCTURED.md` |
| Slope census + mixed-kill / risk0 masks | Single-`H` clean; unions all-mixed; masks lose to polished HJSW | `FINDINGS_SLOPE_CENSUS.md` |
| Non-hyperbola second families (parabola, circle, Pell, exp, …) | Risk0 still O(1)–O(10); board risk0 ceiling ties polished HJSW | `FINDINGS_NONHYPERBOLA.md` |
| Delete-k from HJSW to unlock risk0 | More free cells; enrich still ≤ polished baseline | `FINDINGS_NONHYPERBOLA.md` |
| Joint empty-greedy / local search on mixed pools | Empty loses; local search only O(1) finite noise | `FINDINGS_JOINT.md` |
| T2 block sacrifice ± M refill + polish | O(1); ≈ random same-size deletion | `FINDINGS_BLOCK_SACRIFICE.md` |
| Ambient `n > 2p` with same modulus `p` | Loses two-lift cleanliness; densities lag HJSW on `n=2p` | `FINDINGS_AMBIENT.md` |
| Tile two HJSW copies on `n=4p` | Ratio ~1.41–1.45 < 3/2 | `FINDINGS_BLOCK_SACRIFICE.md` |

---

## Positive structural picture

```
                    single H(c), n ≤ 2p
                    ─────────────────
                    non-primary clean
                    (theorem, sharp)

                    multi-H union
                    ─────────────────
                    only MIXED non-primary
                    triples hurt

                    primary packing of multi-H
                    ─────────────────
                    can beat |HJSW| by ~Θ(p)
                    but LB on mixed deletions
                    cancels surplus (p ≥ 17)

                    HJSW = H ∩ T2
                    ─────────────────
                    still the density champion
                    among tested algebraic cuts
```

**Why `n = 2p` matters:** it is the largest board where every residue has
≤2 lifts, so single-`H` stays all-slope-clean. That is why classical HJSW
lives there — not an accident of notation.

**Why grafting fails:** once HJSW occupies primary slots, almost every
risk-0 cell vs the seed is primary-blocked or mutually conflicting; ordinary
polish already takes the tiny residue. Changing the second curve does not
open a `Θ(p)` corridor.

**Why primary-first fails:** the surplus is real but paid for by mixed
triples whose mandatory deletions exceed it.

---

## Finite artifacts (not asymptotic claims)

- Polished HJSW (and slight variants) sometimes exceed `1.55n` for particular
  primes (list in `data/winning_primes.json` / `solution.py`).
- Joint local search / block sacrifice occasionally beat a single polish
  seed by +1…+4 points; under multi-seed baselines this is noise.
- Tiny primes (`p ≤ 7`) can still show `LB < surplus` scraps; the gap opens
  from `p ≥ 11`–`17` onward.

---

## Open directions (higher leverage)

1. **Finish Conjecture B** — turn the max-primary matching outline in
   `PROOF_LB_SURPLUS.md` into a uniform theorem for all `p ≥ 17`.
2. **New algebraic family + cut**, with modulus co-designed with `n`
   (not “same `p`, bigger board”).
3. Anything that is **not** another HJSW-first graft, multi-`H` primary
   packing, or S₂ polish-seed surgery.

Still out of scope as a “solution”: claiming density `> 3/2 + ε` without a
construction or proof.

---

## Index of detailed docs

| Doc | Role |
|-----|------|
| `PROOF_SINGLE_H.md` | Theorem: single-`H` clean for `n ≤ 2p` |
| `PROOF_LB_SURPLUS.md` | Mixed corollary + LB≥surplus certificate / conjecture |
| `FINDINGS_AMBIENT.md` | Sharpness at `n=2p+1`; ambient probes |
| `FINDINGS_ALLSLOPE_HITTING.md` | First LB vs surplus tables |
| `FINDINGS_PRIMARY_REPAIR.md` | Primary surplus vs repair loss |
| `FINDINGS_STRUCTURED.md` | Band/block/chessboard schedules |
| `FINDINGS_SLOPE_CENSUS.md` | Pure vs mixed census; risk masks |
| `FINDINGS_NONHYPERBOLA.md` | Other curves + board risk0 ceiling |
| `FINDINGS_JOINT.md` | Joint all-slope packing |
| `FINDINGS_BLOCK_SACRIFICE.md` | T2 block drop experiments |
| `FINDINGS_MULTI_HYPERBOLA.md` | Delete-first multi-`H` |
| `FINDINGS.md` | Early hyperbola-union vs subset |
| `RESEARCH.md` | Problem statement + pointers |
| `SESSION_HISTORY.md` | Chronological phase log |
| `NEXT_AGENT.md` | Saturated paths + next bets |

Data CSVs are catalogued in `data/README.md`.
