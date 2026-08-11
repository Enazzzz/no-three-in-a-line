"""Hyperbola-union trials with slope-±1 deletion (KNS Remark 3.4 style).

Pipeline:
  1. Seed = HJSW S2 for residue c0 on n=2p.
  2. For each extra residue c in a short list, take H(c) ∩ board minus the seed,
     and greedily add points that clear unsaturated horiz/vert, unsaturated
     slope ±1, and all-slope collinearity (slope tables).
  3. Optionally chain several extra residues (multi-hyperbola).
  4. Short unstructured greedy polish.

Goal of this module is the *next research step* — measure whether changing
the algebraic seed beats polishing a single hyperbola — not a full solution.
"""

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from research.algebraic import saturated_differences, unsaturated_hv_candidates
from research.constructions import hjsw, is_prime
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, max_safe_augmentation, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]


def hyperbola_points(n: int, p: int, c: int) -> List[Point]:
	"""All board points with x y ≡ c (mod p), x,y not divisible by p."""
	pts: List[Point] = []
	for x in range(1, n + 1):
		if x % p == 0:
			continue
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
	*,
	seed: int = 0,
) -> List[Point]:
	"""Greedily add extra_pool points avoiding saturated row/col/±1 and all slopes."""
	pts: List[Point] = [tuple(p) for p in base]  # type: ignore[misc]
	occ: Set[Point] = set(pts)
	tables = build_slope_tables(pts)
	order = list(extra_pool)
	rng = random.Random(seed)
	rng.shuffle(order)
	# Prefer candidates on currently unsaturated ±1 diagonals (cheap score).
	sat_plus, sat_minus = saturated_differences(pts)

	def score(pt: Point) -> Tuple[int, int, int]:
		x, y = pt
		return (
			int((x - y) in sat_plus) + int((x + y) in sat_minus),
			x,
			y,
		)

	order.sort(key=score)

	for cand in order:
		if cand in occ:
			continue
		if not unsaturated_hv_candidates(n, pts, [cand]):
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


def default_extra_residues(p: int, c0: int = 1, limit: int = 6) -> List[int]:
	"""Short list of secondary residues to try (VM-scoped)."""
	cands = [2, 3, 5, (p - 1) // 2, p - 2, p - 1, 7, 11]
	out: List[int] = []
	for c in cands:
		c = c % p
		if c == 0 or c == (c0 % p) or c in out:
			continue
		out.append(c)
		if len(out) >= limit:
			break
	return out


def chain_hyperbola_union(
	p: int,
	*,
	c0: int = 1,
	extras: Optional[Sequence[int]] = None,
	polish_s: float = 3.0,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""HJSW seed, then sequentially fold in extra hyperbolas with ±1 filter."""
	if not is_prime(p) or p == 2:
		raise ValueError("p must be an odd prime")
	n, base = hjsw(p, c0)
	pts = list(base)
	used: List[int] = []
	added_per_c: Dict[int, int] = {}
	extras = list(extras) if extras is not None else default_extra_residues(p, c0)
	for c1 in extras:
		before = len(pts)
		pool = [pt for pt in hyperbola_points(n, p, c1) if pt not in set(pts)]
		pts = union_with_pm1_filter(n, pts, pool, seed=seed + c1)
		gained = len(pts) - before
		if gained > 0:
			used.append(c1)
			added_per_c[c1] = gained

	polished = greedy_augment(n, pts, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else pts
	ok2, reason2 = verify_claim(n, final)
	stats = {
		"family": "hyperbola_union_chain",
		"c0": c0,
		"extras_tried": list(extras),
		"extras_used": used,
		"added_per_c": added_per_c,
		"base_size": len(base),
		"pre_polish": len(pts),
		"size": len(final),
		"ratio": len(final) / n if n else 0.0,
		"verified": ok2,
		"reason": reason2 if ok2 else reason2 or reason,
	}
	return n, final, stats


def try_hyperbola_unions(p: int, c0: int = 1, time_limit_s: float = 5.0) -> Tuple[int, List[Point], dict]:
	"""Best of: single secondary c, and a short multi-c chain. Backward compatible."""
	n, base = hjsw(p, c0)
	best = list(base)
	best_stats: dict = {"family": "hjsw", "c0": c0, "c1": None, "size": len(base), "ratio": len(base) / n}

	# Pairwise single-extra trials.
	for c1 in default_extra_residues(p, c0, limit=5):
		pool = [pt for pt in hyperbola_points(n, p, c1) if pt not in set(base)]
		merged = union_with_pm1_filter(n, base, pool, seed=c1)
		per = max(0.8, time_limit_s / 6.0)
		polished = greedy_augment(n, merged, time_limit_s=per, seed=c1)
		ok, _ = verify_claim(n, polished)
		cand = polished if ok else merged
		ok2, _ = verify_claim(n, cand)
		if not ok2:
			continue
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

	# Chained multi-c (one shot).
	n2, chained, st = chain_hyperbola_union(p, c0=c0, polish_s=max(1.0, time_limit_s / 3.0), seed=p)
	assert n2 == n
	if st["verified"] and st["size"] > len(best):
		best = chained
		best_stats = st

	ok, reason = verify_claim(n, best)
	best_stats["verified"] = ok
	best_stats["reason"] = reason
	best_stats["ratio"] = len(best) / n
	best_stats["size"] = len(best)
	return n, best, best_stats


def compare_methods(p: int, polish_s: float = 3.0) -> dict:
	"""Head-to-head: HJSW, subset MIS, best union. For findings tables."""
	n, base = hjsw(p)
	subset_pts, subset_stats = max_safe_augmentation(n, base, exact_limit=24 if p <= 120 else 18)
	n_u, union_pts, union_stats = try_hyperbola_unions(p, time_limit_s=polish_s * 2)
	# Polish subset briefly for fair-ish comparison.
	subset_polished = greedy_augment(n, subset_pts, time_limit_s=polish_s, seed=p)
	ok_s, _ = verify_claim(n, subset_polished)
	if not ok_s:
		subset_polished = subset_pts

	def pack(label: str, pts: Sequence[Point], extra: Optional[dict] = None) -> dict:
		ok, reason = verify_claim(n, list(pts))
		row = {
			"method": label,
			"size": len(pts),
			"ratio": len(pts) / n if n else 0.0,
			"verified": ok,
			"reason": reason,
		}
		if extra:
			row.update(extra)
		return row

	return {
		"p": p,
		"n": n,
		"hjsw": pack("hjsw", base),
		"subset": pack(
			"subset",
			subset_polished,
			{"individually_ok": subset_stats["individually_ok"], "subset_added": subset_stats["added"]},
		),
		"union": pack(
			"union",
			union_pts,
			{
				"union_family": union_stats.get("family"),
				"c1": union_stats.get("c1"),
				"extras_used": union_stats.get("extras_used"),
			},
		),
	}
