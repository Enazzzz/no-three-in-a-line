# Next agent checklist

1. Read `docs/FINDINGS.md` and `docs/FINDINGS_MULTI_HYPERBOLA.md`.
2. Do **not** redo: HJSW polishing races, HJSW-seeded second-hyperbola grafts,
   or unstructured greedy delete-first on raw multi-hyperbola unions — those
   three are measured and saturated for this VM scale.
3. Higher-leverage next attempts (if continuing):
   - structured multi-hyperbola block masks `T*` with disjoint primary classes
   - exact min-deletion / matching repair for primary classes on small `p`
4. Commit and push frequently — cloud VMs wipe uncommitted work.
5. Do not claim an asymptotic `>1.55n` breakthrough without a real construction or proof.
