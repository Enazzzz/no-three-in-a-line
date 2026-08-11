# No-Three-in-Line Research Offload

Recovered research + constructions + a **certified** lightweight volunteer-compute harness for searching dense no-three-in-line configurations.

> **Asymptotic status:** beating `(3/2)n` by a fixed constant (e.g. `>1.55n` for large `n`) remains **open**. Literature best is still Hall–Jackson–Sudbery–Wild (HJSW, 1975): `(3/2)n − o(n)`.

## Layout

| Path | Purpose |
|------|---------|
| `AGENT_MEMORY_DUMP.md` | Full session memory for the next agent — **delete after ingest** |
| `docs/` | Research notes, algebraic program, distributed design, session history |
| `research/` | Verifier, HJSW/Erdős constructions, algebraic helpers, greedy search |
| `solution.py` | Best-effort `solution(min_n)` using HJSW + augmentation |
| `distributed/` | Coordinator / worker / verify-before-leaderboard harness |
| `.cursor/` | Cursor project dir (add rules/commands as you like) |

## Quick checks

```bash
python3 -c "from research.constructions import hjsw; from research.verify import verify_claim; p=5; n,pts=hjsw(p); print(n,len(pts),verify_claim(n,pts))"
python3 -c "from solution import solution; print(solution(10))"
```

## Distributed demo

```bash
cd distributed
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PWD
bash scripts/demo_local.sh
```

## Trust model

Workers are **never** trusted. The coordinator re-runs exact integer collinearity checks before accepting any claim.

## Next agent

1. Read `docs/FINDINGS*.md` (especially structured + all-slope hitting)
2. Next leverage: algebraic non-primary slope census / formal LB≥surplus
3. Prefer commits on `main` (or merge feature branches) over PRs unless asked
4. Push often — VM disk is temporary
