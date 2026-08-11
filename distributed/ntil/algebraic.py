"""Residue-constraint / algebraic addability helpers for HJSW augmentation."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

Point = Tuple[int, int]


def occupied_rows_cols(points: Sequence[Point]) -> Tuple[Set[int], Set[int]]:
	"""Return the sets of occupied row y-values and column x-values."""
	rows = {y for _, y in points}
	cols = {x for x, _ in points}
	return rows, cols


def difference_counts(points: Sequence[Point]) -> Tuple[Dict[int, int], Dict[int, int]]:
	"""Count points on each slope-+1 diagonal (x-y) and slope--1 diagonal (x+y)."""
	d_plus: Dict[int, int] = defaultdict(int)
	d_minus: Dict[int, int] = defaultdict(int)
	for x, y in points:
		d_plus[x - y] += 1
		d_minus[x + y] += 1
	return dict(d_plus), dict(d_minus)


def saturated_differences(
	points: Sequence[Point],
	threshold: int = 2,
) -> Tuple[Set[int], Set[int]]:
	"""Return D+^(threshold) and D-^(threshold) difference classes."""
	d_plus, d_minus = difference_counts(points)
	sat_plus = {d for d, c in d_plus.items() if c >= threshold}
	sat_minus = {s for s, c in d_minus.items() if c >= threshold}
	return sat_plus, sat_minus


def residue_sets(points: Sequence[Point], p: int) -> Tuple[Set[int], Set[int]]:
	"""Occupied x and y residues modulo p (excluding 0 if present)."""
	rx = {x % p for x, _ in points}
	ry = {y % p for _, y in points}
	return rx, ry


def f_plus(t: int, c: int, p: int) -> int:
	"""Hyperbola image t - c*t^{-1} mod p (representative in 0..p-1)."""
	inv = pow(t, -1, p)
	return (t - (c * inv)) % p


def f_minus(t: int, c: int, p: int) -> int:
	"""Hyperbola image t + c*t^{-1} mod p."""
	inv = pow(t, -1, p)
	return (t + (c * inv)) % p


def middle_band_candidates(n: int, p: int, occupied_rows: Set[int], occupied_cols: Set[int]) -> List[Point]:
	"""List empty cells whose row and column are currently unoccupied.

	These are the horiz/vert-safe candidates (necessary, not sufficient).
	"""
	out: List[Point] = []
	for x in range(1, n + 1):
		if x in occupied_cols:
			continue
		for y in range(1, n + 1):
			if y in occupied_rows:
				continue
			out.append((x, y))
	return out


def four_constraint_survivors(
	n: int,
	base: Sequence[Point],
	pool: Sequence[Point] | None = None,
) -> List[Point]:
	"""Cells that do not hit saturated horiz/vert/slope±1 classes of base.

	If pool is None, uses all empty cells on the n×n board.
	"""
	base_set = set(map(tuple, base))
	rows, cols = occupied_rows_cols(list(map(tuple, base)))
	sat_plus, sat_minus = saturated_differences(list(map(tuple, base)))
	if pool is None:
		pool = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1) if (x, y) not in base_set]

	survivors: List[Point] = []
	for x, y in pool:
		if (x, y) in base_set:
			continue
		if y in rows or x in cols:
			continue
		if (x - y) in sat_plus:
			continue
		if (x + y) in sat_minus:
			continue
		survivors.append((x, y))
	return survivors


def summarize_addability(n: int, p: int, base: Sequence[Point]) -> dict:
	"""Return counts useful for algebraic augmentation experiments."""
	rows, cols = occupied_rows_cols(list(map(tuple, base)))
	sat_plus, sat_minus = saturated_differences(list(map(tuple, base)))
	rx, ry = residue_sets(list(map(tuple, base)), p)
	mid = middle_band_candidates(n, p, rows, cols)
	surv = four_constraint_survivors(n, base, mid)
	return {
		"n": n,
		"p": p,
		"base_size": len(base),
		"occupied_rows": len(rows),
		"occupied_cols": len(cols),
		"sat_plus": len(sat_plus),
		"sat_minus": len(sat_minus),
		"residues_x": len(rx),
		"residues_y": len(ry),
		"middle_hv_safe": len(mid),
		"four_constraint_survivors": len(surv),
	}
