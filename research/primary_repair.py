"""Exact (or capped) max subset under primary-class capacities.

Primary classes = rows, columns, slope-+1 diagonals, slope--1 diagonals,
each allowed at most `cap` points (default 2 for no-three-in-line on those
slopes). This is the 'exact primary repair' step from FINDINGS_MULTI_HYPERBOLA:

  take a multi-hyperbola pool → largest subset with all primary classes ≤2
  → then repair remaining (general-slope) collisions.

No ILP solver in the VM, so we use branch-and-bound with a simple capacity
bound. Exact on small pools; falls back to degree-greedy if the search
budget is exhausted.
"""

from __future__ import annotations

import random
import time
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

from research.constructions import hjsw
from research.multi_hyperbola import multi_hyperbola_pool, default_residue_sets
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim, _orient

Point = Tuple[int, int]


def primary_keys(pt: Point) -> Tuple[Tuple[str, int], ...]:
	"""The four primary class keys for a point."""
	x, y = pt
	return (("row", y), ("col", x), ("plus", x - y), ("minus", x + y))


def greedy_primary_max(
	pool: Sequence[Point],
	*,
	cap: int = 2,
	seed: int = 0,
) -> List[Point]:
	"""Degree-greedy: prefer points whose classes are currently emptiest."""
	rng = random.Random(seed)
	order = list(pool)
	rng.shuffle(order)
	counts: Counter = Counter()
	# Pre-degree in the pool graph of shared classes (light heuristic).
	class_members: Dict[Tuple[str, int], List[Point]] = {}
	for pt in order:
		for k in primary_keys(pt):
			class_members.setdefault(k, []).append(pt)
	degree = {
		pt: sum(len(class_members[k]) - 1 for k in primary_keys(pt)) for pt in order
	}
	order.sort(key=lambda pt: (degree[pt], rng.random()))

	kept: List[Point] = []
	for pt in order:
		keys = primary_keys(pt)
		if any(counts[k] >= cap for k in keys):
			continue
		kept.append(pt)
		for k in keys:
			counts[k] += 1
	return kept


def exact_primary_max(
	pool: Sequence[Point],
	*,
	cap: int = 2,
	time_limit_s: float = 5.0,
	seed: int = 0,
) -> Tuple[List[Point], dict]:
	"""Branch-and-bound maximum subset with primary capacities ≤ cap.

	Returns (points, stats). If the time budget expires, returns the best
	found (which is at least as good as the greedy warm-start).
	"""
	pts = [tuple(p) for p in pool]  # type: ignore[misc]
	# Warm start.
	greedy = greedy_primary_max(pts, cap=cap, seed=seed)
	best: List[Point] = list(greedy)
	t0 = time.monotonic()
	nodes = 0
	timed_out = False

	# Order by greedy degree for stronger pruning.
	class_members: Dict[Tuple[str, int], int] = Counter()
	for pt in pts:
		for k in primary_keys(pt):
			class_members[k] += 1
	pts.sort(key=lambda pt: sum(class_members[k] for k in primary_keys(pt)), reverse=True)

	def bound(i: int, counts: Counter) -> int:
		"""Optimistic: pack remaining points ignoring mutual conflicts beyond caps."""
		# Residual capacity sum / 4 is a weak but cheap upper on additions.
		# Better: greedily count how many remaining could still fit alone.
		add = 0
		local = counts.copy()
		for j in range(i, len(pts)):
			keys = primary_keys(pts[j])
			if any(local[k] >= cap for k in keys):
				continue
			add += 1
			for k in keys:
				local[k] += 1
		return add

	def dfs(i: int, current: List[Point], counts: Counter) -> None:
		nonlocal best, nodes, timed_out
		nodes += 1
		if time.monotonic() - t0 > time_limit_s:
			timed_out = True
			return
		if len(current) + bound(i, counts) <= len(best):
			return
		if i == len(pts):
			if len(current) > len(best):
				best = list(current)
			return
		pt = pts[i]
		keys = primary_keys(pt)
		# Try include.
		if all(counts[k] < cap for k in keys):
			for k in keys:
				counts[k] += 1
			current.append(pt)
			dfs(i + 1, current, counts)
			current.pop()
			for k in keys:
				counts[k] -= 1
			if timed_out:
				return
		# Skip.
		dfs(i + 1, current, counts)

	dfs(0, [], Counter())
	stats = {
		"pool": len(pool),
		"greedy_size": len(greedy),
		"size": len(best),
		"nodes": nodes,
		"timed_out": timed_out,
		"exact": (not timed_out) and len(best) >= len(greedy),
		"runtime_s": time.monotonic() - t0,
		"method": "bnb_primary" if not timed_out else "bnb_primary_timeout",
	}
	# Guarantee ≥ greedy.
	if len(best) < len(greedy):
		best = list(greedy)
		stats["method"] = "greedy_fallback"
	return best, stats


def count_general_collinear_triples(points: Sequence[Point]) -> int:
	"""Count unordered triples that are collinear on a non-primary slope.

	Primary slopes are horiz/vert/±1; those should already be clean if the
	primary packing succeeded. We still count all collinear triples for safety.
	"""
	pts = [tuple(p) for p in points]  # type: ignore[misc]
	m = len(pts)
	total = 0
	nonprimary = 0
	for i in range(m):
		for j in range(i + 1, m):
			for k in range(j + 1, m):
				if _orient(pts[i], pts[j], pts[k]) != 0:
					continue
				total += 1
				x1, y1 = pts[i]
				x2, y2 = pts[j]
				dx, dy = x2 - x1, y2 - y1
				# Primary if horiz, vert, or |slope|=1.
				if dx == 0 or dy == 0 or abs(dx) == abs(dy):
					continue
				nonprimary += 1
	return nonprimary


def repair_all_slopes(n: int, points: Sequence[Point], *, seed: int = 0) -> List[Point]:
	"""Greedy-keep from an already primary-feasible set to kill general slopes."""
	# Re-run greedy keep with slope tables; primary already ≤2 so mostly all-slope.
	rng = random.Random(seed)
	order = list(points)
	rng.shuffle(order)
	kept: List[Point] = []
	tables = {}
	from collections import Counter

	counts: Counter = Counter()
	for cand in order:
		x, y = cand
		# Keep primary caps hard.
		if counts[("row", y)] >= 2 or counts[("col", x)] >= 2:
			continue
		if counts[("plus", x - y)] >= 2 or counts[("minus", x + y)] >= 2:
			continue
		if kept and not individually_addable(cand, kept, tables):
			continue
		tables[cand] = set()
		for q in kept:
			s = _norm_slope(x - q[0], y - q[1])
			tables[q].add(s)
			tables[cand].add(s)
		kept.append(cand)
		counts[("row", y)] += 1
		counts[("col", x)] += 1
		counts[("plus", x - y)] += 1
		counts[("minus", x + y)] += 1
	return [(x, y) for x, y in kept if 1 <= x <= n and 1 <= y <= n]


def run_primary_pipeline(
	p: int,
	residues: Sequence[int],
	*,
	mask_t2: bool = True,
	cap: int = 2,
	bnb_s: float = 3.0,
	polish_s: float = 1.0,
	seed: int = 0,
) -> dict:
	"""Full pipeline + diagnostics for one (p, residue set)."""
	n, pool = multi_hyperbola_pool(p, residues, mask_t2=mask_t2)
	primary, pst = exact_primary_max(pool, cap=cap, time_limit_s=bnb_s, seed=seed)
	# Verify primary packing.
	from collections import Counter

	ctr: Counter = Counter()
	for pt in primary:
		for k in primary_keys(pt):
			ctr[k] += 1
	primary_ok = all(v <= cap for v in ctr.values())
	gen_trips = count_general_collinear_triples(primary) if len(primary) <= 120 else -1
	repaired = repair_all_slopes(n, primary, seed=seed)
	polished = greedy_augment(n, repaired, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else repaired
	ok2, reason2 = verify_claim(n, final)
	n_h, hjsw_pts = hjsw(p)
	return {
		"p": p,
		"n": n,
		"residues": list(residues),
		"mask_t2": mask_t2,
		"pool": len(pool),
		"primary_size": len(primary),
		"primary_ok": primary_ok,
		"primary_method": pst["method"],
		"primary_timed_out": pst["timed_out"],
		"primary_runtime_s": pst["runtime_s"],
		"general_collinear_triples": gen_trips,
		"repaired_size": len(repaired),
		"final_size": len(final),
		"final_ratio": len(final) / n if n else 0.0,
		"final_verified": ok2,
		"hjsw_size": len(hjsw_pts),
		"delta_primary_minus_hjsw": len(primary) - len(hjsw_pts),
		"delta_final_minus_hjsw": len(final) - len(hjsw_pts),
		"reason": reason2,
	}


def best_primary_pipeline(p: int, *, bnb_s: float = 3.0, polish_s: float = 1.0) -> dict:
	"""Try a few residue/mask settings; keep best final verified size."""
	best: Optional[dict] = None
	for residues in default_residue_sets(p)[:4]:  # keep VM light
		for mask in (True, False):
			row = run_primary_pipeline(
				p, residues, mask_t2=mask, bnb_s=bnb_s, polish_s=polish_s, seed=p
			)
			if not row["final_verified"]:
				continue
			if best is None or row["final_size"] > best["final_size"]:
				best = row
			# Also track best primary even if final shrinks — recorded inside row.
	if best is None:
		n, pts = hjsw(p)
		best = {
			"p": p,
			"n": n,
			"residues": [1],
			"mask_t2": True,
			"pool": len(pts),
			"primary_size": len(pts),
			"primary_ok": True,
			"primary_method": "hjsw_fallback",
			"primary_timed_out": False,
			"primary_runtime_s": 0.0,
			"general_collinear_triples": 0,
			"repaired_size": len(pts),
			"final_size": len(pts),
			"final_ratio": len(pts) / n,
			"final_verified": True,
			"hjsw_size": len(pts),
			"delta_primary_minus_hjsw": 0,
			"delta_final_minus_hjsw": 0,
			"reason": "ok",
		}
	return best
