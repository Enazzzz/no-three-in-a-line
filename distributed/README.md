# No-Three-in-Line Volunteer Compute (lightweight)

Distributed search harness for the **no-three-in-line** problem on `{1..n}²`.
Not BOINC — small FastAPI coordinator + Python workers.

**Natural sharding:** one job per `(prime p, construction family, optimization params)`.
Board size for prime jobs: **n = 2p**.

## Trust model

**Workers are never trusted.** The coordinator runs `ntil.verify.verify_claim`
(exact integer cross-product) before accepting any claim onto the leaderboard.
Rejected claims are stored with `verified=0` for audit. Accepted claims get
`cert_hash` = SHA-256 of canonical claim JSON.

## Layout

```
distributed/
  ntil/           # verify, HJSW constructions, algebraic helpers, solvers
  coordinator/    # FastAPI + SQLite + job factory
  worker/         # pull → solve → upload
  schemas/        # JSON Schema for jobs / claims
  scripts/        # seed_jobs, verify_claim, demo_local.sh
  web/            # leaderboard.html
```

## Families

| Family | Behavior |
|--------|----------|
| `hjsw` | HJSW S₂: hyperbola `xy ≡ c (mod p)` ∩ T₂ (size `3(p-1)`) |
| `hjsw_augment` | HJSW + greedy fill (prefers four-constraint survivors) |
| `algebraic_addable` | Residue / slope-±1 filter, then greedy |
| `hyperbola_union` | HJSW seed + further hyperbola union attempts |

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Leaderboard HTML |
| `GET` | `/health` | Liveness |
| `POST` | `/jobs/seed` | Seed jobs |
| `GET` | `/jobs/next?worker_id=` | Lease job |
| `GET` | `/jobs/{id}` | Job metadata |
| `POST` | `/claims` | Submit claim (server verifies; 400 if bad) |
| `GET` | `/leaderboard?min_n=&limit=` | Verified claims |

## Run

```bash
cd distributed
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PWD
bash scripts/demo_local.sh
```

Env: `NTIL_DB_PATH` (default `/tmp/ntil_coordinator.sqlite3`).
