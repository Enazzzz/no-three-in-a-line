# Session history (recovered)

Timeline is approximate; cloud VMs were wiped mid-work.

## Phase 1 — Classical constructions & search
- Implemented collinearity verifier and Erdős / HJSW constructions
- Verified HJSW sizes `3(p−1)` on `n=2p` for primes
- Small-n search / greedy / CP-SAT attempts; bundled configs for many `n≤60` (Prellberg-style) and some larger winners
- Could not produce a proven asymptotic construction above `3/2`

## Phase 2 — HJSW augmentation experiments
- Greedy augmentation sometimes `>1.55n` for special primes up to `n=562` (`p=281`)
- Catalogued partial winner list; failed to find modular pattern
- S3/S4 middle repairs failed to beat HJSW after deletions

## Phase 3 — Algebraic reframing (user)
- Stop treating augmentation as generic independent set
- Residue constraints for horiz/vert/slope±1; difference-class formulation

## Phase 4 — Distributed compute design (user)
- Coordinator / worker / independent verification / leaderboard
- Implemented once on a sibling cloud VM; wiped before GitHub push
- Auth blocked until temporary fine-grained PAT provided (Aug 2026)

## Phase 5 — Offload (this commit series)
- Parent VM returned empty after weeks
- PAT granted write access to `Enazzzz/no-three-in-a-line`
- Full rebuild + memory dump pushed to branch `cursor/offload-everything-7e69`

## Infra lessons
- Agents without linked `repoUrl` do not receive GitHub write credentials
- Public repo ≠ push access
- Commit/push continuously; local artifacts die with the pod

## Phase 6 — Algebraic survivor fix + subset tables (2026-08-11)

- Fixed four-constraint horiz/vert filter: use ≥2 saturation, not “occupied”
- Slope-table O(m) individual addability; exact/greedy MIS on tiny ok-pools
- Empirically: 4-constraint survivors grow with p, but all-slope survivors stay O(10–50)
- Additive gains of ~4–31 points; some ratios >1.55; no asymptotic breakthrough
- Data: `data/addability_scan.csv`, `data/subset_scan.csv`

## Phase 7 — Hyperbola-union next step + findings post

- Compared HJSW / subset / ±1-filtered multi-hyperbola unions on p≤181
- Union does not systematically beat subset (13–5 in subset’s favor; Δ≈0)
- Root cause: H(c₁) vs HJSW has individually-ok counts typically 0–2
- Posted write-up: `docs/FINDINGS.md`
- Next direction: simultaneous / delete-first multi-hyperbola designs

## Phase 8 — Simultaneous / delete-first multi-hyperbola

- Implemented raw multi-hyperbola pools + delete-first / greedy-keep
- Scan p≤97: multi loses to subset (9–2); falls back to HJSW by p≈83
- Posted: `docs/FINDINGS_MULTI_HYPERBOLA.md` + `data/multi_hyperbola_scan.csv`
- Unstructured deletion on bigger unions does not beat classical S₂

## Phase 9 — Exact primary-class repair

- BnB max subset with ≤2 per row/col/±1 on multi-hyperbola pools
- Primary size can exceed HJSW by ~Θ(p); all-slope repair loss grows faster
- Posted: `docs/FINDINGS_PRIMARY_REPAIR.md`, `data/primary_surplus_diag.csv`
- Binding obstruction = non-primary slopes, not primary capacity

## Phase 10 — All-slope hitting lower bounds

- Disjoint-excess LB on general-slope deletions vs primary surplus
- For p≥17, LB > surplus (gap widens with p); surplus cannot survive repair
- Posted: `docs/FINDINGS_ALLSLOPE_HITTING.md`, `data/allslope_hitting_scan.csv`

## Phase 11 — Structured geometric schedules

- column/row bands, T2/M partition, chessboard residue coloring
- LB ≥ surplus on all scanned primes; no asymptotic escape
- Posted: `docs/FINDINGS_STRUCTURED.md`, `data/structured_schedule_scan.csv`

## Phase 12 — Slope census / mixed-line masks

- Single `H(c)` has zero non-primary ≥3-lines; unions are all-mixed
- Mixed-kill and risk0 second-hyperbola masks lose to polished HJSW
- Posted: `docs/FINDINGS_SLOPE_CENSUS.md`, `data/slope_census_scan.csv`

## Phase 13 — Non-hyperbola second families

- Parabola/circle/Pell/exp/line + board risk0 ceiling + delete-k unlock
- All tie or lose to polished HJSW; bottleneck is primary capacity, not curve
- Posted: `docs/FINDINGS_NONHYPERBOLA.md`, `data/nonhyperbola_scan.csv`

## Phase 14 — Joint all-slope packing + single-H certificate

- Empty joint greedy loses; local search only O(1) finite +1/+2 sometimes
- Posted: `docs/FINDINGS_JOINT.md`

## Phase 15 — Single-H non-primary theorem

- Proved: H(c) on n=2p has no non-primary ≥3-line (field incidence + lifts)
- Machine checks through p≤97; cleanliness certificate through p≤241
- Posted: `docs/PROOF_SINGLE_H.md`, `data/proof_single_h_scan.csv`

## Phase 16 — LB ≥ surplus (multi-H primary packings)

- Proved: bad lines are always mixed (corollary of single-H)
- Counterexample: in-pool NTIL can have surplus>0 with LB=0 (not universal)
- Certificate: best-of primary packings, all 80 cases p∈[17,79] have LB≥surplus
- Posted: `docs/PROOF_LB_SURPLUS.md`, `data/lb_surplus_scan.csv`

## Phase 17 — HJSW T2 block sacrifice

- Drop one T2 half-block (± M/H refill) then polish vs multi-seed baseline
- Only O(1) gains; comparable to random same-size deletion
- Posted: `docs/FINDINGS_BLOCK_SACRIFICE.md`, `data/block_sacrifice_scan.csv`

## Phase 18 — Ambient redesign / sharp n≤2p bound

- Proved sharpness: single-H cleanliness requires n≤2p (dirty at n=2p+1)
- Larger boards with same modulus lose the two-lift advantage; densities lag
- Posted: `docs/FINDINGS_AMBIENT.md`, `data/ambient_sharp_scan.csv`

## Phase 19 — Ambient-aligned multi-hyperbola

- Board `xy ≡ c` pools ≠ ambient HJSW supersets (often HJSW ∩ board ≈ O(1))
- Ambient-aligned pools contain HJSW; fair local search only +O(1) vs polish
- Ambient primary can violate LB≥surplus (Conjecture B′ is pool-dependent)
- Posted: `docs/FINDINGS_AMBIENT_MULTI_H.md`, `data/ambient_multi_h_scan.csv`

## Phase 20 — Conjecture B reduction (theorem track)

- Goal pivot: prefer theorems over new constructions
- Certified lemmas B1 (`LB≥⌊m/3⌋`) and B2 (`⌊m/3⌋≥surplus`) on 80/80 board packs
- Minority bad-line coverage imperfect (≳0.81); mono-color primary ≪ HJSW
- Posted: updated `docs/PROOF_LB_SURPLUS.md`, `data/conjecture_b_lemmas_scan.csv`

## Phase 21 — B2 provenance check (negative)

- ~0.7 mono/HJSW is `∼2p/3(p−1)`, not a single-H corollary
- Real structure: board H row/col occupancy ≤2 (two-lift) ⇒ primary⇔±1 caps
- Conjecture M: mono size `2p` or `2(p+1)` by `p mod 4` (16/16 through p=61)
- Mono cap ↛ B2 (only 4/60 rows forced); B2 is an independent conjecture
- Posted: `research/b2_provenance.py`, `data/b2_provenance_scan.csv`
