"""Structured multi-hyperbola schedules that limit cross-residue mixing.

Motivation (FINDINGS_ALLSLOPE_HITTING): raw ⋃ H(c) primary packing beats HJSW
but non-primary deletion LBs exceed the surplus. These builders avoid stacking
several hyperbolas on the same geometric support:

* column_band — left x-half uses c0, right x-half uses c1
* row_band — bottom y-half uses c0, top y-half uses c1
* block_partition — partition translated T2∪M half-blocks between two residues

Then we primary-pack and compare hitting LBs / final size to HJSW.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

from research.allslope_hitting import analyze_primary_set, bad_general_lines, greedy_hitting_upper_bound
from research.constructions import ambient_grid, hjsw, is_prime, middle_blocks, t2_blocks
from research.hyperbola_union import hyperbola_points
from research.primary_repair import exact_primary_max, repair_all_slopes
from research.search import greedy_augment
from research.verify import verify_claim

Point = Tuple[int, int]


def _translated(points: Set[Point], p: int) -> Set[Point]:
	"""Map ambient-grid points into the [1, 2p]² board used by hjsw()."""
	xmin, _, ymin, _ = ambient_grid(p)
	sx, sy = 1 - xmin, 1 - ymin
	n = 2 * p
	out: Set[Point] = set()
	for x, y in points:
		bx, by = x + sx, y + sy
		if 1 <= bx <= n and 1 <= by <= n:
			out.add((bx, by))
	return out


def column_band_pool(p: int, c0: int = 1, c1: int = 2) -> Tuple[int, List[Point]]:
	"""Left columns from H(c0), right columns from H(c1)."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	c0, c1 = c0 % p, c1 % p
	left = [pt for pt in hyperbola_points(n, p, c0) if pt[0] <= p]
	right = [pt for pt in hyperbola_points(n, p, c1) if pt[0] > p]
	return n, sorted(set(left) | set(right))


def row_band_pool(p: int, c0: int = 1, c1: int = 2) -> Tuple[int, List[Point]]:
	"""Bottom rows from H(c0), top rows from H(c1)."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	c0, c1 = c0 % p, c1 % p
	bottom = [pt for pt in hyperbola_points(n, p, c0) if pt[1] <= p]
	top = [pt for pt in hyperbola_points(n, p, c1) if pt[1] > p]
	return n, sorted(set(bottom) | set(top))


def block_partition_pool(p: int, c0: int = 1, c1: int = 2) -> Tuple[int, List[Point]]:
	"""T2 blocks ← H(c0); middle blocks M ← H(c1)."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	c0, c1 = c0 % p, c1 % p
	t2 = _translated(t2_blocks(p), p)
	mid = _translated(middle_blocks(p), p)
	h0 = set(hyperbola_points(n, p, c0)) & t2
	h1 = set(hyperbola_points(n, p, c1)) & mid
	return n, sorted(h0 | h1)


def chessboard_pool(p: int, c0: int = 1, c1: int = 2) -> Tuple[int, List[Point]]:
	"""Alternate residues by (⌊(x-1)/h⌋ + ⌊(y-1)/h⌋) mod 2 with h=(p-1)//2.

	A coarse 2×2 block chessboard on the n=2p board, each color one hyperbola.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	h = max(1, (p - 1) // 2)
	c0, c1 = c0 % p, c1 % p
	h0 = set(hyperbola_points(n, p, c0))
	h1 = set(hyperbola_points(n, p, c1))
	out: Set[Point] = set()
	for x, y in h0:
		if ((x - 1) // h + (y - 1) // h) % 2 == 0:
			out.add((x, y))
	for x, y in h1:
		if ((x - 1) // h + (y - 1) // h) % 2 == 1:
			out.add((x, y))
	return n, sorted(out)


SCHEDULES = {
	"column_band": column_band_pool,
	"row_band": row_band_pool,
	"block_partition": block_partition_pool,
	"chessboard": chessboard_pool,
}


def evaluate_structured(
	p: int,
	schedule: str,
	*,
	c0: int = 1,
	c1: int = 2,
	bnb_s: float = 3.0,
	polish_s: float = 1.0,
) -> dict:
	"""Primary-pack a structured pool and score vs HJSW + hitting bounds."""
	if schedule not in SCHEDULES:
		raise KeyError(schedule)
	n, pool = SCHEDULES[schedule](p, c0=c0, c1=c1)
	primary, pst = exact_primary_max(pool, cap=2, time_limit_s=bnb_s, seed=p)
	n_h, hjsw_pts = hjsw(p)
	surplus = len(primary) - len(hjsw_pts)
	hit = analyze_primary_set(primary, bnb_s=min(2.0, bnb_s))
	repaired = repair_all_slopes(n, primary, seed=p)
	polished = greedy_augment(n, repaired, time_limit_s=polish_s, seed=p)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else repaired
	ok2, reason2 = verify_claim(n, final)
	# Also greedy-hit residual size (matches hitting analysis).
	bad = bad_general_lines(primary)
	deleted, _ = greedy_hitting_upper_bound(primary, bad)
	hit_residual = [pt for pt in primary if pt not in set(deleted)]
	ok3, _ = verify_claim(n, hit_residual)
	return {
		"p": p,
		"n": n,
		"schedule": schedule,
		"c0": c0,
		"c1": c1,
		"pool": len(pool),
		"hjsw_size": len(hjsw_pts),
		"primary_size": len(primary),
		"surplus": surplus,
		"primary_method": pst["method"],
		"bad_lines": hit["bad_lines"],
		"lb_disjoint": hit["lb_disjoint"],
		"ub_greedy": hit["ub_greedy"],
		"min_deletions": hit["min_deletions"],
		"lb_minus_surplus": hit["lb_disjoint"] - surplus,
		"kept_minus_hjsw": hit["kept_after_min_del"] - len(hjsw_pts),
		"repaired_size": len(repaired),
		"final_size": len(final) if ok2 else len(hit_residual),
		"final_ratio": (len(final) if ok2 else len(hit_residual)) / n,
		"final_verified": ok2 or ok3,
		"beats_hjsw_final": (len(final) if ok2 else len(hit_residual)) > len(hjsw_pts),
		"reason": reason2 if ok2 else reason,
	}


def best_structured(p: int, **kwargs) -> dict:
	"""Try all schedules × a few (c0,c1); keep best final verified size."""
	n_h, hjsw_pts = hjsw(p)
	best = {
		"p": p,
		"n": n_h,
		"schedule": "hjsw_fallback",
		"pool": len(hjsw_pts),
		"hjsw_size": len(hjsw_pts),
		"primary_size": len(hjsw_pts),
		"surplus": 0,
		"lb_disjoint": 0,
		"lb_minus_surplus": 0,
		"kept_minus_hjsw": 0,
		"final_size": len(hjsw_pts),
		"final_ratio": len(hjsw_pts) / n_h,
		"final_verified": True,
		"beats_hjsw_final": False,
	}
	pairs = [(1, 2), (1, 3), (1, p - 1), (2, 3)]
	for schedule in SCHEDULES:
		for c0, c1 in pairs:
			if c0 % p == 0 or c1 % p == 0 or c0 % p == c1 % p:
				continue
			row = evaluate_structured(p, schedule, c0=c0, c1=c1, **kwargs)
			if not row["final_verified"]:
				continue
			key = (row["final_size"], row["surplus"], -row["lb_minus_surplus"])
			bkey = (best["final_size"], best.get("surplus", 0), -best.get("lb_minus_surplus", 0))
			if key > bkey:
				best = row
	return best
