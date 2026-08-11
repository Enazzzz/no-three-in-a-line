"""Greedy augmentation search for no-three-in-line sets."""

from __future__ import annotations

import random
import time
from typing import List, Optional, Sequence, Set, Tuple

from research.algebraic import four_constraint_survivors
from research.verify import _orient

Point = Tuple[int, int]


def _shares_line_with_two(pt: Point, pts: Sequence[Point]) -> bool:
	"""Return True if adding pt creates a 3-term collinear subset with existing pts."""
	# For each existing pair, check collinearity with pt — O(m^2); OK for moderate m.
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
	residue constraints; then fall back to remaining empty cells.
	"""
	rng = random.Random(seed)
	pts: List[Point] = [tuple(p) for p in base]  # type: ignore[misc]
	occupied: Set[Point] = set(pts)
	t0 = time.monotonic()

	if candidates is None:
		if prefer_four_constraint:
			primary = four_constraint_survivors(n, pts)
			primary_set = set(primary)
			rest = [
				(x, y)
				for x in range(1, n + 1)
				for y in range(1, n + 1)
				if (x, y) not in occupied and (x, y) not in primary_set
			]
			candidates = list(primary) + rest
		else:
			candidates = [
				(x, y)
				for x in range(1, n + 1)
				for y in range(1, n + 1)
				if (x, y) not in occupied
			]

	order = list(candidates)
	rng.shuffle(order)

	for cand in order:
		if time.monotonic() - t0 > time_limit_s:
			break
		if cand in occupied:
			continue
		if _shares_line_with_two(cand, pts):
			continue
		pts.append(cand)
		occupied.add(cand)
	return pts
