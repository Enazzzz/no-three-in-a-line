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
