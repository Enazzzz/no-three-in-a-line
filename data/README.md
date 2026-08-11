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

Always re-verify configurations with `research.verify.verify_claim`.
See `docs/FINDINGS*.md`.
