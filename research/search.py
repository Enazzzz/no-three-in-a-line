"""Greedy augmentation search for no-three-in-line sets."""

from __future__ import annotations

import random
import time
from typing import List, Optional, Sequence, Set, Tuple

from research.algebraic import four_constraint_survivors, unsaturated_hv_candidates
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import _orient

Point = Tuple[int, int]


def _shares_line_with_two(pt: Point, pts: Sequence[Point]) -> bool:
	"""Return True if adding pt creates a 3-term collinear subset with existing pts."""
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			if _orient(pts[i], pts[j], pt) == 0:
				return True
	return False


def greedy_augment(
	n: int,
	base: Sequence[Point],
	candidates: Optional[Sequence[Point]] = None,
	time_limit_s: float = 30.0,
	seed: int = 0,
	prefer_four_constraint: bool = True,
) -> List[Point]:
	"""Greedily add candidates that preserve no-three-in-line.

	If prefer_four_constraint, first try survivors of the four primary
	residue constraints; then fall back to remaining unsaturated hv cells.
	Uses slope tables so each candidate check is O(m), not O(m²).
	"""
	rng = random.Random(seed)
	pts: List[Point] = [tuple(p) for p in base]  # type: ignore[misc]
	occupied: Set[Point] = set(pts)
	t0 = time.monotonic()
	tables = build_slope_tables(pts)

	if candidates is None:
		hv = unsaturated_hv_candidates(n, pts)
		if prefer_four_constraint:
			primary = four_constraint_survivors(n, pts, hv)
			primary_set = set(primary)
			rest = [c for c in hv if c not in primary_set]
			candidates = list(primary) + rest
		else:
			candidates = hv

	order = list(candidates)
	rng.shuffle(order)

	for cand in order:
		if time.monotonic() - t0 > time_limit_s:
			break
		if cand in occupied:
			continue
		if not individually_addable(cand, pts, tables):
			continue
		# Extend slope tables with the accepted point.
		tables[cand] = set()
		for q in pts:
			s = _norm_slope(cand[0] - q[0], cand[1] - q[1])
			tables[q].add(s)
			tables[cand].add(s)
		pts.append(cand)
		occupied.add(cand)
	return pts
