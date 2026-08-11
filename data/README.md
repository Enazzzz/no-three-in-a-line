# Experimental tables

| File | Contents |
|------|----------|
| `winning_primes.json` | Primes where prior scans beat ratio 1.55 on `n=2p` |
| `addability_scan.csv` | Four-constraint / middle-block counts (corrected ≥2 rule) |
| `subset_scan.csv` | Individually-ok pools + max safe subset sizes |
| `hyperbola_union_scan.csv` | Head-to-head HJSW vs subset vs hyperbola-union |
| `second_hyperbola_pool.csv` | How many `H(c₁)` points are all-slope-safe vs HJSW |
| `multi_hyperbola_scan.csv` | Simultaneous / delete-first multi-hyperbola vs baselines |
| `primary_repair_scan.csv` | Exact primary repair pipeline vs HJSW/subset |
| `primary_surplus_diag.csv` | Max primary surplus and all-slope repair loss |
| `allslope_hitting_scan.csv` | Hitting LB/UB vs primary surplus over HJSW |
| `structured_schedule_scan.csv` | Band/block/chessboard schedules vs raw LB |
| `slope_census_scan.csv` | Single-H vs union mixed-line census + mask trials |
| `nonhyperbola_scan.csv` | Non-hyperbola / board-risk0 second pools vs polished HJSW |
| `joint_pack_scan.csv` | Joint empty-greedy / local-search packs vs polished HJSW |
| `single_h_clean_scan.csv` | Single-H primary vs non-primary ≥3-line census |
| `proof_single_h_scan.csv` | Lemma checks for the single-H non-primary theorem |

Always re-verify configurations with `research.verify.verify_claim`.
See `docs/FINDINGS*.md` and `docs/PROOF_SINGLE_H.md`.
