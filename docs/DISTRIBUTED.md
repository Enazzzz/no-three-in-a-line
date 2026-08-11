# Distributed volunteer compute

Lightweight (not BOINC) certified search harness for no-three-in-line.

## Why distribute

The search shards naturally:

- one worker per prime `p`
- one worker per construction family
- one worker per optimization parameter (seed, `c`, time budget)

## Architecture

```
Coordinator  --creates jobs-->  queue queue
Worker       --leases job---->  runs solver
Worker       --uploads------->  claim {points, stats, cert material}
Server       --verifies------>  leaderboard (only if verify OK)
```

### Trust model

**Workers are never trusted.** Every claim is independently checked with
exact integer collinearity before it can appear as verified.

Rejected claims are stored with `verified=0` for audit.
Accepted claims get `cert_hash = SHA-256(canonical_json(claim))`.

## Job shape

```json
{
  "job_id": "hjsw_augment-p281-s7",
  "family": "hjsw_augment",
  "params": {"p": 281, "n": 562, "seed": 7, "c": 1},
  "time_limit_s": 50
}
```

Board size for prime jobs: `n = 2p`.

## Families

| Family | Behavior |
|--------|----------|
| `hjsw` | Classical S₂ hyperbola ∩ T₂ |
| `hjsw_augment` | HJSW + greedy fill (middle-biased) |
| `algebraic_addable` | Residue / slope-±1 filter, then greedy |
| `hyperbola_union` | HJSW seed + further hyperbola union attempts |

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Leaderboard HTML |
| `GET` | `/health` | Liveness |
| `POST` | `/jobs/seed` | Expand primes × families × seeds |
| `GET` | `/jobs/next?worker_id=` | Lease one pending job |
| `GET` | `/jobs/{id}` | Job metadata |
| `POST` | `/claims` | Submit claim (400 if invalid) |
| `GET` | `/leaderboard` | Verified claims |

## Run locally

See `distributed/README.md` and `distributed/scripts/demo_local.sh`.

## Interesting primes to seed

`5,7,17,19,31,37,61,67,71,83,97,107,109,139,151,167,173,181,281`
(from prior HJSW-augmentation scans that beat 1.55 on those `n=2p`).
