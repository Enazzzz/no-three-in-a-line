"""Residue-constraint / algebraic addability helpers for HJSW augmentation.

Horiz/vert safety uses the true no-three-in-line rule: a row (resp. column)
may hold at most two points. Candidates are therefore rejected only when the
row or column is already *saturated* (≥2), not merely occupied.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ntil.constructions import ambient_grid, middle_blocks

Point = Tuple[int, int]


def occupied_rows_cols(points: Sequence[Point]) -> Tuple[Set[int], Set[int]]:
	"""Return the sets of occupied row y-values and column x-values."""
	rows = {y for _, y in points}
	cols = {x for x, _ in points}
	return rows, cols


def row_col_counts(points: Sequence[Point]) -> Tuple[Dict[int, int], Dict[int, int]]:
	"""Return per-row and per-column occupancy counts."""
	rows = Counter(y for _, y in points)
	cols = Counter(x for x, _ in points)
	return dict(rows), dict(cols)


def saturated_rows_cols(
	points: Sequence[Point],
	threshold: int = 2,
) -> Tuple[Set[int], Set[int]]:
	"""Rows / columns that already hold ≥ threshold points (cannot accept more)."""
	rows, cols = row_col_counts(points)
	sat_rows = {y for y, c in rows.items() if c >= threshold}
	sat_cols = {x for x, c in cols.items() if c >= threshold}
	return sat_rows, sat_cols


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


def translated_middle_blocks(p: int) -> Set[Point]:
	"""Middle blocks M mapped into the same [1, 2p]² board as hjsw()."""
	xmin, _, ymin, _ = ambient_grid(p)
	shift_x = 1 - xmin
	shift_y = 1 - ymin
	n = 2 * p
	out: Set[Point] = set()
	for x, y in middle_blocks(p):
		bx, by = x + shift_x, y + shift_y
		if 1 <= bx <= n and 1 <= by <= n:
			out.add((bx, by))
	return out


def unsaturated_hv_candidates(
	n: int,
	points: Sequence[Point],
	pool: Optional[Sequence[Point]] = None,
) -> List[Point]:
	"""Empty cells whose row and column each still have room (<2 points)."""
	base_set = set(map(tuple, points))
	sat_rows, sat_cols = saturated_rows_cols(list(map(tuple, points)))
	if pool is None:
		pool = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
	out: List[Point] = []
	for x, y in pool:
		if (x, y) in base_set:
			continue
		if y in sat_rows or x in sat_cols:
			continue
		out.append((x, y))
	return out


def middle_band_candidates(
	n: int,
	p: int,
	occupied_rows: Set[int],
	occupied_cols: Set[int],
) -> List[Point]:
	"""Backward-compatible wrapper: cells in fully empty rows and columns."""
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
	"""Cells that avoid saturated horiz/vert/slope±1 classes of base.

	Horiz/vert: reject only if the row or column already has ≥2 points.
	Slope ±1: reject if the corresponding diagonal already has ≥2 points.
	If pool is None, uses all empty cells on the n×n board.
	"""
	base_set = set(map(tuple, base))
	sat_rows, sat_cols = saturated_rows_cols(list(map(tuple, base)))
	sat_plus, sat_minus = saturated_differences(list(map(tuple, base)))
	if pool is None:
		pool = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1) if (x, y) not in base_set]

	survivors: List[Point] = []
	for x, y in pool:
		if (x, y) in base_set:
			continue
		if y in sat_rows or x in sat_cols:
			continue
		if (x - y) in sat_plus:
			continue
		if (x + y) in sat_minus:
			continue
		survivors.append((x, y))
	return survivors


def summarize_addability(n: int, p: int, base: Sequence[Point]) -> dict:
	"""Return counts useful for algebraic augmentation experiments."""
	row_c, col_c = row_col_counts(list(map(tuple, base)))
	sat_rows, sat_cols = saturated_rows_cols(list(map(tuple, base)))
	sat_plus, sat_minus = saturated_differences(list(map(tuple, base)))
	rx, ry = residue_sets(list(map(tuple, base)), p)
	hv = unsaturated_hv_candidates(n, base)
	surv = four_constraint_survivors(n, base, hv)
	mid = translated_middle_blocks(p)
	mid_pool = [pt for pt in mid if pt not in set(map(tuple, base))]
	mid_hv = unsaturated_hv_candidates(n, base, mid_pool)
	mid_surv = four_constraint_survivors(n, base, mid_hv)
	return {
		"n": n,
		"p": p,
		"base_size": len(base),
		"occupied_rows": len(row_c),
		"occupied_cols": len(col_c),
		"sat_rows": len(sat_rows),
		"sat_cols": len(sat_cols),
		"rows_with_one": sum(1 for c in row_c.values() if c == 1),
		"cols_with_one": sum(1 for c in col_c.values() if c == 1),
		"sat_plus": len(sat_plus),
		"sat_minus": len(sat_minus),
		"residues_x": len(rx),
		"residues_y": len(ry),
		"hv_safe": len(hv),
		"four_constraint_survivors": len(surv),
		"middle_cells": len(mid_pool),
		"middle_hv_safe": len(mid_hv),
		"middle_four_survivors": len(mid_surv),
		"middle_hv_safe_legacy_empty": len(
			middle_band_candidates(n, p, set(row_c), set(col_c))
		),
	}
