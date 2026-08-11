# Next agent checklist

1. Read **`docs/FINDINGS_SUMMARY.md`** (one-doc synthesis), then detail
   `FINDINGS*.md` / `PROOF_*.md` as needed.
2. Do **not** redo saturated paths:
   - HJSW polish / second-family grafts / T2 block-sacrifice on S₂
   - unstructured delete-first / exact primary packing hoping repair helps
   - geometric band/block/chessboard residue schedules alone
   - mixed-line kill / risk0 / board ceiling / delete-k / joint pool+search
   - re-proving single-`H` cleanliness / re-scanning LB≥surplus certificates
   - ambient `n>2p` with the **same** modulus `p` (loses two-lift cleanliness)
   - ambient-aligned multi-`H` local search vs polished HJSW (O(1) only;
     see `FINDINGS_AMBIENT_MULTI_H.md`)
3. Higher-leverage next attempts:
   - Finish Conjecture B matching bound in `PROOF_LB_SURPLUS.md` (**board**
     pools only; ambient pools can violate LB≥surplus)
   - New algebraic families / moduli co-designed with `n` (not same-`p`
     board growth, not ambient multi-`H` polish)
4. Commit and push frequently; prefer landing on `main` over opening PRs unless asked.
5. Do not claim an asymptotic `>1.55n` breakthrough without a real construction or proof.
6. When comparing constructions to HJSW, use a **multi-seed polished** baseline;
   raw `|S₂|` inflates deltas. Prefer ambient-aligned pools if the seed is HJSW.
