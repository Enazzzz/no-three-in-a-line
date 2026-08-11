"""All-slope hitting-set bounds on primary-feasible point sets.

Given a set that already respects ≤2 per row/col/±1, measure how many
deletions are *necessary* to eliminate general-slope 3-collinearities.

For each non-primary line L containing k≥3 points, at least k−2 deletions
must land on L. We compute:

* exact min deletions (BnB) for small instances
* a greedy constructive upper bound (delete highest-degree points)
* a disjoint-excess lower bound (pack lines' excesses on disjoint point sets)

Compare these to the primary surplus over HJSW. If LB ≥ surplus, the surplus
cannot survive all-slope repair.
"""

from __future__ import annotations

import time
from collections import defaultdict
from math import gcd
from typing import Dict, List, Sequence, Set, Tuple

from research.constructions import hjsw
from research.multi_hyperbola import default_residue_sets, multi_hyperbola_pool
from research.primary_repair import exact_primary_max, primary_keys
from research.verify import verify_claim

Point = Tuple[int, int]
LineKey = Tuple[int, int, int]  # normalized (dx, dy, intercept)


def _norm_dir(dx: int, dy: int) -> Tuple[int, int]:
	"""Canonical direction with gcd 1 and sign convention."""
	if dx == 0 and dy == 0:
		return (0, 0)
	g = gcd(dx, dy)
	dx //= g
	dy //= g
	if dx < 0 or (dx == 0 and dy < 0):
		dx, dy = -dx, -dy
	return dx, dy


def is_primary_dir(dx: int, dy: int) -> bool:
	"""True for horizontal, vertical, or slope ±1 directions."""
	dx, dy = _norm_dir(dx, dy)
	if dx == 0 or dy == 0:
		return True
	return abs(dx) == abs(dy)


def line_key(a: Point, b: Point) -> LineKey:
	"""Identity of the unique line through a and b."""
	dx, dy = _norm_dir(b[0] - a[0], b[1] - a[1])
	# intercept: dy*x - dx*y is constant on the line.
	inter = dy * a[0] - dx * a[1]
	return (dx, dy, inter)


def lines_with_counts(points: Sequence[Point]) -> Dict[LineKey, List[Point]]:
	"""Group points by every line determined by at least one pair.

	Built by iterating pairs — O(m²). Fine for m ≲ 250.
	"""
	pts = [tuple(p) for p in points]  # type: ignore[misc]
	# Map line → set of points known on it.
	buckets: Dict[LineKey, Set[Point]] = defaultdict(set)
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			key = line_key(pts[i], pts[j])
			buckets[key].add(pts[i])
			buckets[key].add(pts[j])
	return {k: sorted(v) for k, v in buckets.items() if len(v) >= 2}


def bad_general_lines(points: Sequence[Point]) -> Dict[LineKey, List[Point]]:
	"""Non-primary lines with ≥3 points (must delete ≥ k−2 on each)."""
	out: Dict[LineKey, List[Point]] = {}
	for key, pts in lines_with_counts(points).items():
		dx, dy, _ = key
		if is_primary_dir(dx, dy):
			continue
		if len(pts) >= 3:
			out[key] = pts
	return out


def excess_sum(bad: Dict[LineKey, List[Point]]) -> int:
	"""Σ (k−2) over bad lines — weak fractional numerator."""
	return sum(len(pts) - 2 for pts in bad.values())


def disjoint_excess_lower_bound(bad: Dict[LineKey, List[Point]]) -> int:
	"""Greedy pack bad lines on disjoint point sets; sum excesses.

	Each packed line with k points contributes k−2 to the lower bound, and
	those points are removed so later lines cannot reuse them.
	"""
	# Prefer lines with larger excess first.
	items = sorted(bad.values(), key=lambda pts: (len(pts) - 2, len(pts)), reverse=True)
	used: Set[Point] = set()
	lb = 0
	for pts in items:
		live = [p for p in pts if p not in used]
		if len(live) < 3:
			continue
		ex = len(live) - 2
		lb += ex
		# Remove all live points on this line (they can only "pay" here).
		used.update(live)
	return lb


def greedy_hitting_upper_bound(points: Sequence[Point], bad: Dict[LineKey, List[Point]]) -> Tuple[List[Point], int]:
	"""Delete points that hit the most current excess until none remains."""
	remaining: Set[Point] = set(map(tuple, points))  # type: ignore[misc]
	# Mutable line membership.
	line_pts: Dict[LineKey, Set[Point]] = {k: set(v) for k, v in bad.items()}
	deleted: List[Point] = []

	def total_excess() -> int:
		return sum(max(0, len(s) - 2) for s in line_pts.values())

	guard = 0
	while total_excess() > 0 and guard < len(points) + 5:
		guard += 1
		# Score: how much excess a point participates in.
		score: Dict[Point, int] = defaultdict(int)
		for s in line_pts.values():
			ex = len(s) - 2
			if ex <= 0:
				continue
			for p in s:
				if p in remaining:
					score[p] += ex
		if not score:
			break
		victim = max(score, key=lambda p: (score[p], p[0], p[1]))
		remaining.remove(victim)
		deleted.append(victim)
		for s in line_pts.values():
			s.discard(victim)
	return deleted, len(deleted)


def exact_min_deletions(
	points: Sequence[Point],
	bad: Dict[LineKey, List[Point]],
	*,
	time_limit_s: float = 5.0,
) -> Tuple[int, str]:
	"""BnB minimum deletions so every bad line keeps ≤2 points.

	Returns (deletions, method_tag).
	"""
	pts = [tuple(p) for p in points]  # type: ignore[misc]
	# Warm start from greedy.
	_del, ub = greedy_hitting_upper_bound(pts, bad)
	best = ub
	t0 = time.monotonic()
	timed_out = False

	# Only points that lie on some bad line matter.
	candidates = sorted({p for s in bad.values() for p in s})
	# Incidence list.
	inc: Dict[Point, List[LineKey]] = defaultdict(list)
	for k, s in bad.items():
		for p in s:
			inc[p].append(k)

	line_sets: Dict[LineKey, Set[Point]] = {k: set(v) for k, v in bad.items()}

	def current_excess(deleted: Set[Point]) -> int:
		ex = 0
		for s in line_sets.values():
			live = len(s - deleted)
			if live > 2:
				ex += live - 2
		return ex

	def lower_now(deleted: Set[Point]) -> int:
		# Disjoint excess on residual instance.
		resid = {k: [p for p in s if p not in deleted] for k, s in line_sets.items()}
		resid = {k: v for k, v in resid.items() if len(v) >= 3}
		return disjoint_excess_lower_bound(resid)

	def dfs(i: int, deleted: Set[Point], del_count: int) -> None:
		nonlocal best, timed_out
		if time.monotonic() - t0 > time_limit_s:
			timed_out = True
			return
		ex = current_excess(deleted)
		if ex == 0:
			if del_count < best:
				best = del_count
			return
		if del_count + lower_now(deleted) >= best:
			return
		if i == len(candidates):
			return
		# Bound: must still delete at least `ex` somehow — weak.
		if del_count + 1 >= best and ex > 0:
			# still try; lower_now handles tighter
			pass
		p = candidates[i]
		# Skip points already implied useless? Always branch keep/delete.
		# Delete p.
		deleted.add(p)
		dfs(i + 1, deleted, del_count + 1)
		deleted.remove(p)
		if timed_out:
			return
		# Keep p (only if some residual capacity allows — always try).
		dfs(i + 1, deleted, del_count)

	dfs(0, set(), 0)
	tag = "bnb_exact" if not timed_out else "bnb_timeout_ub"
	# best is always ≤ greedy ub; if timeout, best may still have improved.
	return best, tag


def analyze_primary_set(points: Sequence[Point], *, bnb_s: float = 4.0) -> dict:
	"""Full hitting-set analysis for one primary-feasible set."""
	bad = bad_general_lines(points)
	weak = excess_sum(bad)
	lb = disjoint_excess_lower_bound(bad)
	_del, ub = greedy_hitting_upper_bound(points, bad)
	if len(bad) == 0:
		exact, tag = 0, "no_bad_lines"
	elif sum(len(v) for v in bad.values()) <= 80 and bnb_s > 0:
		exact, tag = exact_min_deletions(points, bad, time_limit_s=bnb_s)
	else:
		exact, tag = ub, "greedy_ub_only"
	kept = len(points) - exact
	return {
		"size": len(points),
		"bad_lines": len(bad),
		"excess_sum": weak,
		"lb_disjoint": lb,
		"ub_greedy": ub,
		"min_deletions": exact,
		"deletion_method": tag,
		"kept_after_min_del": kept,
	}


def run_hitting_case(
	p: int,
	residues: Sequence[int],
	*,
	mask_t2: bool = False,
	bnb_s: float = 4.0,
) -> dict:
	"""Build max-primary set for (p,C), analyze hitting bounds vs HJSW."""
	n, pool = multi_hyperbola_pool(p, residues, mask_t2=mask_t2)
	primary, pst = exact_primary_max(pool, cap=2, time_limit_s=min(6.0, bnb_s + 2.0), seed=p)
	n_h, hjsw_pts = hjsw(p)
	surplus = len(primary) - len(hjsw_pts)
	hit = analyze_primary_set(primary, bnb_s=bnb_s)
	# Verify a greedy-hit residual is valid no-three-in-line.
	bad = bad_general_lines(primary)
	deleted, _ = greedy_hitting_upper_bound(primary, bad)
	residual = [pt for pt in primary if pt not in set(deleted)]
	ok, reason = verify_claim(n, residual)
	return {
		"p": p,
		"n": n,
		"residues": list(residues),
		"mask_t2": mask_t2,
		"pool": len(pool),
		"hjsw_size": len(hjsw_pts),
		"primary_size": len(primary),
		"surplus": surplus,
		"primary_method": pst["method"],
		**{f"hit_{k}": v for k, v in hit.items()},
		"lb_minus_surplus": hit["lb_disjoint"] - surplus,
		"exact_del_minus_surplus": hit["min_deletions"] - surplus,
		"kept_minus_hjsw": hit["kept_after_min_del"] - len(hjsw_pts),
		"greedy_residual_verified": ok,
		"reason": reason,
	}
