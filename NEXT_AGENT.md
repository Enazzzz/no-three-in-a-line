# Next agent checklist

1. Read `docs/FINDINGS.md`, `docs/FINDINGS_MULTI_HYPERBOLA.md`, and
   `docs/FINDINGS_PRIMARY_REPAIR.md`.
2. Do **not** redo:
   - HJSW polishing races / second-hyperbola grafts onto S₂
   - unstructured greedy delete-first on raw multi-hyperbola unions
   - exact primary-only packing hoping all-slope repair will preserve surplus
     (surplus is real; repair eats it)
3. Higher-leverage next attempts:
   - algebraically structured masks / residue schedules that control
     **non-primary** slopes by construction
   - lower bounds on all-slope hitting-set size for primary-optimal multi-hyperbola sets
4. Commit and push frequently — cloud VMs wipe uncommitted work.
5. Do not claim an asymptotic `>1.55n` breakthrough without a real construction or proof.
