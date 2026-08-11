"""Exact / greedy max safe subset among four-constraint survivors.

Survivors of the primary residue filters can still conflict with each other
(shared unsaturated row/col/diagonal, or a general slope with the base).
This module builds a conflict graph and finds a large conflict-free subset.

Compute budget: exact branch-and-bound only for tiny survivor pools; otherwise
degree-greedy. Full collinearity vs the base is checked when validating.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

from research.algebraic import four_constraint_survivors, saturated_differences, saturated_rows_cols
from research.verify import _orient, verify_claim

Point = Tuple[int, int]


def _pair_conflicts(a: Point, b: Point, base: Sequence[Point]) -> bool:
	"""True if {a,b} cannot both be added to base (4-class or general slope)."""
	# Shared row / col always conflicts (would make ≥3 with an existing point,
	# or create a third later; two extras on same empty-ish line is unsafe vs base).
	if a[0] == b[0] or a[1] == b[1]:
		return True
	if a[0] - a[1] == b[0] - b[1]:
		return True
	if a[0] + a[1] == b[0] + b[1]:
		return True
	# General slope: a,b collinear with some base point.
	for p in base:
		if _orient(a, b, p) == 0:
			return True
	return False


def conflict_graph(
	survivors: Sequence[Point],
	base: Sequence[Point],
) -> Dict[Point, Set[Point]]:
	"""Undirected conflict adjacency among survivors relative to base."""
	pts = [tuple(p) for p in survivors]  # type: ignore[misc]
	g: Dict[Point, Set[Point]] = {p: set() for p in pts}
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			if _pair_conflicts(pts[i], pts[j], base):
				g[pts[i]].add(pts[j])
				g[pts[j]].add(pts[i])
	return g


def greedy_independent_set(graph: Dict[Point, Set[Point]]) -> List[Point]:
	"""Degree-greedy independent set (light compute)."""
	remaining = set(graph)
	chosen: List[Point] = []
	while remaining:
		# Prefer low degree, then deterministic coords.
		v = min(remaining, key=lambda p: (len(graph[p] & remaining), p[0], p[1]))
		chosen.append(v)
		remaining.remove(v)
		remaining -= graph[v]
	return chosen


def exact_independent_set(graph: Dict[Point, Set[Point]], limit: int = 22) -> List[Point]:
	"""Branch-and-bound MIS for tiny graphs; falls back to greedy if |V|>limit."""
	verts = list(graph)
	if len(verts) > limit:
		return greedy_independent_set(graph)

	best: List[Point] = []

	def bb(remaining: Set[Point], current: List[Point]) -> None:
		nonlocal best
		if len(current) + len(remaining) <= len(best):
			return
		if not remaining:
			if len(current) > len(best):
				best = list(current)
			return
		# Branch on lowest-degree vertex.
		v = min(remaining, key=lambda p: (len(graph[p] & remaining), p[0], p[1]))
		# Take v.
		bb(remaining - {v} - graph[v], current + [v])
		# Skip v.
		bb(remaining - {v}, current)

	bb(set(verts), [])
	return best


def max_safe_augmentation(
	n: int,
	base: Sequence[Point],
	*,
	pool: Sequence[Point] | None = None,
	exact_limit: int = 22,
) -> Tuple[List[Point], dict]:
	"""Return base ∪ max safe survivor subset, plus stats.

	exact_limit caps the exact MIS size so medium primes stay cheap on a VM.
	"""
	base_list = [tuple(p) for p in base]  # type: ignore[misc]
	surv = four_constraint_survivors(n, base_list, pool)
	# Drop survivors that individually fail full collinearity vs base
	# (other slopes beyond the four primary classes).
	individually_ok: List[Point] = []
	for cand in surv:
		trial = base_list + [cand]
		ok, _ = verify_claim(n, trial)
		if ok:
			individually_ok.append(cand)

	g = conflict_graph(individually_ok, base_list)
	if len(individually_ok) <= exact_limit:
		picked = exact_independent_set(g, limit=exact_limit)
		method = "exact"
	else:
		picked = greedy_independent_set(g)
		method = "greedy"

	aug = list(base_list) + picked
	ok, reason = verify_claim(n, aug)
	# If greedy somehow slipped, peel until valid (should be rare).
	if not ok:
		aug = list(base_list)
		for cand in picked:
			trial = aug + [cand]
			tok, _ = verify_claim(n, trial)
			if tok:
				aug.append(cand)
		ok, reason = verify_claim(n, aug)
		method = method + "+peel"

	stats = {
		"four_constraint_survivors": len(surv),
		"individually_ok": len(individually_ok),
		"added": len(aug) - len(base_list),
		"method": method,
		"verified": ok,
		"reason": reason,
		"ratio": len(aug) / n if n else 0.0,
		"sat_rows_cols": tuple(map(len, saturated_rows_cols(base_list))),
		"sat_diags": tuple(map(len, saturated_differences(base_list))),
	}
	return aug, stats
