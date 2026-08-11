# AGENT MEMORY DUMP — DELETE AFTER INGEST

**Next agent instructions:** Read this entire file into context. Then **delete this file**, commit with message `chore: remove AGENT_MEMORY_DUMP after ingest`, and push. Do not leave secrets or this dump in the long-lived tree.

**Do NOT commit any GitHub tokens.** A temporary PAT was used for the initial offload; it must be revoked by the human after push succeeds.

---

## Identity / context

- Human: Zane Davis (`Enazzzz`), email `zaneamater@gmail.com`
- Repo: `https://github.com/Enazzzz/no-three-in-a-line` (public; was accidentally private at first)
- Parent cloud agent (this offload source): `bc-019fc5f1-13f1-7210-b8cc-908f54577e69` — "No-three-in-a-line construction"
- Earlier build agents (VMs wiped): `bc-621a0762-9093-55ac-b560-5e0e140400b1`, `bc-8a5cf65e-291e-524a-bd78-18e17275bb17`, `bc-df726e5a-fb1a-59d5-b482-02633d1dbbbb`
- Original problem: Python `solution(min_n) -> (n, points)` returning configs on `[1,n]²` with no three collinear, `len(points) > 1.55 * n`, `min_n ≤ n ≤ 2*min_n`, strictly increasing `n` across calls, ≤1 minute per call
- Beating classical **3/2** asymptotic ratio by a constant (>1.55) is **genuinely open**; literature best still HJSW 1975: `(3/2)n − o(n)`

## What was lost

- First research tree under `/agent/research`, `/agent/solution.py`, bundled configs up to n=562 — lost when cloud pod terminated
- Distributed volunteer-compute tree was rebuilt on a sibling VM, then wiped again before GitHub push (no credentials until PAT)
- This dump + rebuilt code is the durable recovery

## Mathematical / research findings (keep)

### Classical constructions
- **Erdős parabola:** points `(i, i² mod p)` style on primes — density ~1×n classically for related constructions; not enough alone for >1.55n
- **HJSW (Hall–Jackson–Sudbery–Wild 1975):** odd prime `p`, conceptually grid `G = [−(p−1)/2, (3p−1)/2] × [0, 2p−1]`, translated to `[1, 2p]²` so `n = 2p`
- Modular hyperbola `H(c,p) = {(x,y): xy ≡ c (mod p)}`, `c ≠ 0`
- Normal points partitioned into blocks A,B,C,D (half-blocks of side `((p−1)/2)`), shifted by multiples of `p`
- **T2** = 12 of 16 half-blocks; `S2 = H(c,p) ∩ T2` has **3 points of each of p−1 classes** → `|S2| = 3(p−1)` ≈ **1.5 n − O(1)**
- Congruent copies in G form squares; problematic lines for extras mainly **slope 0, ∞, ±1**
- Middle unused blocks `M = A0,0 ∪ B0,0 ∪ C0,1 ∪ D0,1`
- S3/S4 = add middle ∩ hyperbola → creates 3-/4-in-lines; optimal repair deleted extras and landed back on HJSW size

### Experimental augmentation results
- HJSW + greedy fill of underfull rows/cols **sometimes** beats `1.55n` for specific primes, up to at least **`n=562` (`p=281`, ratio ≈1.5516)**
- Observed winning primes (partial): `5,7,17,19,31,37,61,67,71,83,97,107,109,139,151,167,173,181,281`
- Many nearby losers; **no clean modular pattern** found (mod 4/8/12/24, QR of 2/3/5)
- Individually addable cells after HJSW only ~`O(0.1n)` and appeared to **decline** with `p`; greedy often kept roughly half after conflicts
- Shaving additive `O(1)` off `1.5n − O(1)` does **not** beat the asymptotic ratio

### Algebraic addability program (user-directed; preferred over generic greedy)
1. Write HJSW as union of algebraic curves over `F_p` (the hyperbola cut to half-blocks)
2. For every empty `(x,y)`, exact conditions: no horizontal, vertical, slope +1, slope −1 conflict
3. Express addability as **residue constraints**
4. Reframe: *How large is the largest subset of an algebraically defined point set avoiding a small collection of difference classes?*

Concrete residues:
- Occupied row/col residue sets `R_y`, `R_x` (for classical HJSW, `|R_x|=|R_y|=p−1` — almost all residues occupied; extras live in middle strip `M`)
- Slope +1: `D_+^{(2)} = {d : |S ∩ {x−y=d}| ≥ 2}`; map `f_+(t) = t − c t^{-1}`
- Slope −1: `D_-^{(2)}` via `f_-(t) = t + c t^{-1}`
- Candidate pool often `U = H(c',p) ∩ M` or integer points of `M` satisfying the four predicates
- Goal: prove `|S| ≥ (3/2+ε)n` or at least `(3/2)n + ω(1)` / `n/log n` additive improvement; or prove density of addable set → 0

### Literature notes
- Green suspects `3/2` may be optimal
- Guy–Kelly heuristic ~`1.81n`
- Kovács–Nagy–Szabó (2025) improve `k≥3` no-`(k+1)`-in-line; for `k=2` still cite HJSW; Remark 3.4 hints careful slope-`±1` deletion on multi-hyperbola unions might slightly help

### Failed approaches (do not redo naively)
- Double parabola / exponential / Beatty on `p×p`
- S3/S4 hitting-set repair of middle hyperbola
- Same-`c` middle block wholesale
- Naive larger windows
- Simple Moser–Tardos
- Subgrid cropping of HJSW
- Treating augmentation as generic independent-set / greedy only

### Verifier / solution interface constraints
- `solution(min_n)` returns `(n, points)`
- Points distinct in `[1,n]×[1,n]`
- No three collinear (exact integer orientation / cross-product)
- `len(points) > 1.55 * n`
- Strictly increasing `n` across calls (`_LAST_N` style)
- ≤1 minute per call
- Optional: no durable file side effects beyond `if __name__`

### Distributed volunteer-compute design (implemented under `distributed/`)
- **Not full BOINC** — lightweight FastAPI coordinator + Python workers
- Natural shard: one job per `(prime p, construction family, optimization params)`; `n=2p`
- Families: `hjsw`, `hjsw_augment`, `algebraic_addable`, `hyperbola_union`
- Worker downloads job → runs solver → uploads best set + certificate + stats
- **Workers are NEVER trusted**; server independently re-verifies every claim before leaderboard
- Certificate: SHA-256 of canonical claim JSON
- API: `GET /`, `/health`, `POST /jobs/seed`, `GET /jobs/next`, `GET /jobs/{id}`, `POST /claims`, `GET /leaderboard`
- SQLite store with job leasing / TTL
- Smoke: demo accepts verified claims; fake collinear claim → HTTP 400

### Coding preferences (user rules)
- Tabs for indentation
- Docstrings / comments on functions
- Imports at top of modules (no inline imports)
- Every project should contain `.cursor/` at root (may be empty; user adds structure)
- Auto-commits OK; commit often so VM wipe doesn't lose work
- Prefer serious but lightly conversational tone
- Frontend design rules exist but N/A unless building UI beyond simple leaderboard

### Open next steps
1. Implement algebraic residue tables for each prime; measure size of 4-constraint survivor set in `M`
2. Exact / ILP max difference-class-safe subset on survivors for small→medium `p`
3. Try hyperbola unions with deliberate slope-±1 deletion (KNS Remark 3.4)
4. Run distributed workers on known interesting primes; publish verified leaderboard
5. Do **not** claim asymptotic >1.55 unless a real construction/proof exists

### Ops / infra lessons
- Cloud agent without linked `repoUrl` gets **no** GitHub write credentials
- Making repo public ≠ write access
- Uncommitted files die when VM is replaced; conversation memory may survive
- Always push early and often

---

## File inventory expected after offload

```
.cursor/
AGENT_MEMORY_DUMP.md          # THIS FILE — delete after next-agent ingest
README.md
docs/RESEARCH.md
docs/ALGEBRAIC_ADDABILITY.md
docs/DISTRIBUTED.md
docs/SESSION_HISTORY.md
research/verify.py
research/constructions.py
research/algebraic.py
research/search.py
solution.py
distributed/                  # full volunteer-compute harness
```

End of dump.
