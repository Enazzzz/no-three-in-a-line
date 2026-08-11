# Next agent checklist

1. Read `docs/FINDINGS*.md` and `docs/PROOF_SKETCH_SINGLE_H.md`.
2. Do **not** redo saturated paths:
   - HJSW polish / second-family grafts onto S₂ (hyperbola or otherwise)
   - unstructured delete-first / exact primary packing hoping repair helps
   - geometric band/block/chessboard residue schedules alone
   - mixed-line kill / risk0 masks / board risk0 ceiling / delete-k unlock
   - joint empty-greedy or light local search on H∪parabola∪circle pools
     (only O(1) finite noise vs polished HJSW)
3. Higher-leverage next attempts:
   - **Finish the proof** of single-`H` non-primary cleanliness on `n=2p`
   - Prove `LB(p) ≥ surplus(p)` for raw max-primary multi-`H` pools for all
     odd `p≥17`
   - New geometric cuts / constructions that are not pool+search variants
4. Commit and push frequently; prefer landing on `main` over opening PRs unless asked.
5. Do not claim an asymptotic `>1.55n` breakthrough without a real construction or proof.
