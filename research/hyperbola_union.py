"""Hyperbola-union trials with slope-±1 deletion (KNS Remark 3.4 style).

Start from HJSW S2 for c0, then try adding points from H(c1) ∩ board that
survive unsaturated horiz/vert, deleting or skipping any candidate that
lands on an already-saturated ±1 diagonal. Keep the densest verified set.

Scoped for a VM: only a few (c0,c1) pairs and a short greedy polish.
"""

from __future__ import annotations

from typing import List, Sequence, Set, Tuple

from research.algebraic import saturated_differences, unsaturated_hv_candidates
from research.constructions import hjsw, is_prime
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]


def _hyperbola_points(n: int, p: int, c: int) -> List[Point]:
	"""All board points with x y ≡ c (mod p), x,y ≠ 0 (mod p)."""
	pts: List[Point] = []
	for x in range(1, n + 1):
		if x % p == 0:
			continue
		# y ≡ c * x^{-1} (mod p); lift into [1,n].
		inv = pow(x, -1, p)
		y0 = (c * inv) % p
		if y0 == 0:
			continue
		for k in range((n - y0) // p + 1):
			y = y0 + k * p
			if 1 <= y <= n:
				pts.append((x, y))
	return pts


def union_with_pm1_filter(
	n: int,
	base: Sequence[Point],
	extra_pool: Sequence[Point],
) -> List[Point]:
	"""Greedily add extra_pool points avoiding saturated row/col/±1 and all slopes."""
	pts: List[Point] = [tuple(p) for p in base]  # type: ignore[misc]
	occ: Set[Point] = set(pts)
	tables = build_slope_tables(pts)
	# Refresh ±1 saturation as we go via counts in tables is awkward; recompute lightly.
	for cand in extra_pool:
		if cand in occ:
			continue
		sat_rows_cols = unsaturated_hv_candidates(n, pts, [cand])
		if not sat_rows_cols:
			continue
		sat_plus, sat_minus = saturated_differences(pts)
		x, y = cand
		if (x - y) in sat_plus or (x + y) in sat_minus:
			continue
		if not individually_addable(cand, pts, tables):
			continue
		tables[cand] = set()
		for q in pts:
			s = _norm_slope(x - q[0], y - q[1])
			tables[q].add(s)
			tables[cand].add(s)
		pts.append(cand)
		occ.add(cand)
	return pts


def try_hyperbola_unions(p: int, c0: int = 1, time_limit_s: float = 5.0) -> Tuple[int, List[Point], dict]:
	"""Return best verified (n, points, stats) among a few secondary residues."""
	if not is_prime(p) or p == 2:
		raise ValueError("p must be an odd prime")
	n, base = hjsw(p, c0)
	best = list(base)
	best_stats = {"family": "hjsw", "c0": c0, "c1": None, "size": len(base)}
	# A few nonzero secondary residues; skip c0.
	c1s = [c for c in (2, 3, (p - 1) // 2, p - 2, p - 1) if c % p != 0 and c != c0 % p]
	for c1 in c1s:
		pool = _hyperbola_points(n, p, c1)
		# Prefer points not already in base.
		base_set = set(base)
		pool = [pt for pt in pool if pt not in base_set]
		merged = union_with_pm1_filter(n, base, pool)
		polished = greedy_augment(
			n, merged, time_limit_s=max(1.0, time_limit_s / max(1, len(c1s))), seed=c1
		)
		ok, _ = verify_claim(n, polished)
		if not ok:
			ok2, _ = verify_claim(n, merged)
			cand = merged if ok2 else list(base)
		else:
			cand = polished
		if len(cand) > len(best):
			best = cand
			best_stats = {
				"family": "hyperbola_union_pm1",
				"c0": c0,
				"c1": c1,
				"size": len(cand),
				"ratio": len(cand) / n,
				"pool": len(pool),
			}
	ok, reason = verify_claim(n, best)
	best_stats["verified"] = ok
	best_stats["reason"] = reason
	best_stats["ratio"] = len(best) / n
	return n, best, best_stats
