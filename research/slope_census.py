"""Algebraic / combinatorial census of non-primary slopes on hyperbola pools.

Key empirical law (verified on scanned primes):

* A *single* modular hyperbola H(c) on the n=2p board has **no** non-primary
  line with ≥3 integer points.
* In a union H(c0) ∪ H(c1), **every** non-primary ≥3-line is *mixed*
  (uses points from both residues). Pure same-c bad lines do not appear.

So multi-hyperbola damage is entirely cross-color. This module:

1. census — classify bad lines as pure vs mixed
2. mixed_kill_then_primary — delete a hitting set of mixed lines first, then
   primary-pack the cleaned pool (slope-forbidding via deletion mask)
3. hjsw_protected_enrich — keep HJSW; add H(c1) cells that stay individually
   all-slope-ok (seed never deleted)
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Set, Tuple

from research.allslope_hitting import (
	bad_general_lines,
	disjoint_excess_lower_bound,
	exact_min_deletions,
	greedy_hitting_upper_bound,
)
from research.algebraic import saturated_differences, unsaturated_hv_candidates
from research.constructions import hjsw, is_prime
from research.hyperbola_union import hyperbola_points
from research.primary_repair import exact_primary_max
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]


def census_bad_lines(
	pool: Sequence[Point],
	color: Dict[Point, int],
) -> dict:
	"""Classify non-primary ≥3-lines by color mixing.

	`color[pt]` is a residue label (e.g. c). Lines whose points use ≥2 labels
	are mixed; otherwise pure.
	"""
	bad = bad_general_lines(pool)
	pure = 0
	mixed = 0
	mix_excess = 0
	pure_excess = 0
	slope_hist: Counter = Counter()
	split_hist: Counter = Counter()
	for key, pts in bad.items():
		labels = {color.get(pt, -1) for pt in pts}
		ex = len(pts) - 2
		dx, dy, _b = key
		slope_hist[(dx, dy)] += 1
		# Count how many points per color (sorted by label for stability).
		by_lab: Counter = Counter(color.get(pt, -1) for pt in pts)
		split_hist[tuple(sorted(by_lab.values(), reverse=True))] += 1
		if len(labels) <= 1:
			pure += 1
			pure_excess += ex
		else:
			mixed += 1
			mix_excess += ex
	return {
		"bad_lines": len(bad),
		"pure_lines": pure,
		"mixed_lines": mixed,
		"pure_excess": pure_excess,
		"mixed_excess": mix_excess,
		"all_mixed": pure == 0,
		"disjoint_lb": disjoint_excess_lower_bound(bad),
		"top_slopes": slope_hist.most_common(8),
		"top_splits": split_hist.most_common(8),
	}


def color_by_hyperbola(n: int, p: int, residues: Sequence[int]) -> Tuple[List[Point], Dict[Point, int]]:
	"""Build ∪ H(c) with a color map (first c wins on overlaps)."""
	color: Dict[Point, int] = {}
	for c in residues:
		c = c % p
		if c == 0:
			continue
		for pt in hyperbola_points(n, p, c):
			color.setdefault(pt, c)
	return sorted(color), color


def census_single_vs_union(p: int, c0: int = 1, c1: int = 2) -> dict:
	"""Compare bad-line census for H(c0), H(c1), and their union."""
	n = 2 * p
	c0, c1 = c0 % p, c1 % p
	h0 = hyperbola_points(n, p, c0)
	h1 = hyperbola_points(n, p, c1)
	col0 = {pt: c0 for pt in h0}
	col1 = {pt: c1 for pt in h1}
	union_pts, colU = color_by_hyperbola(n, p, [c0, c1])
	return {
		"p": p,
		"n": n,
		"c0": c0,
		"c1": c1,
		"size_c0": len(h0),
		"size_c1": len(h1),
		"size_union": len(union_pts),
		"census_c0": census_bad_lines(h0, col0),
		"census_c1": census_bad_lines(h1, col1),
		"census_union": census_bad_lines(union_pts, colU),
	}


def single_hyperbola_primary_pack(
	p: int,
	c: int = 1,
	*,
	bnb_s: float = 4.0,
	polish_s: float = 1.0,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""Primary-pack one H(c). Non-primary lines are empirically empty, so this
	is already a candidate NTIL set after primary capacities.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	pool = hyperbola_points(n, p, c % p)
	packed, st = exact_primary_max(pool, time_limit_s=bnb_s, seed=seed)
	# Safety: strip any residual non-primary (should be none).
	bad = bad_general_lines(packed)
	if bad:
		deleted, _ = greedy_hitting_upper_bound(packed, bad)
		packed = [pt for pt in packed if pt not in set(deleted)]
	polished = greedy_augment(n, packed, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else packed
	ok2, reason2 = verify_claim(n, final)
	_, hjsw_pts = hjsw(p, c % p)
	stats = {
		"family": "single_h_primary",
		"c": c % p,
		"pool": len(pool),
		"primary_size": len(packed),
		"bnb": st,
		"final_size": len(final),
		"ratio": len(final) / n if n else 0.0,
		"delta_vs_hjsw": len(final) - len(hjsw_pts),
		"verified": ok2,
		"reason": reason2,
	}
	return n, final, stats


def mixed_kill_then_primary(
	p: int,
	residues: Sequence[int],
	*,
	bnb_s: float = 4.0,
	hit_s: float = 3.0,
	polish_s: float = 1.5,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""Slope-forbidding mask via mixed-line hitting set, then primary pack.

	Pipeline:
	  U = ∪ H(c)
	  delete a (near-)min hitting set of non-primary ≥3-lines (all mixed)
	  primary-max the surviving pool
	  short greedy polish
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	cs = [c % p for c in residues if c % p != 0]
	pool, color = color_by_hyperbola(n, p, cs)
	census = census_bad_lines(pool, color)
	bad = bad_general_lines(pool)
	# Exact API returns a count only; we need an explicit deleted set.
	# Use greedy hitting for the mask, and record the BnB lower/exact count
	# as a certificate that we are not wildly suboptimal.
	deleted_pts, del_count = greedy_hitting_upper_bound(pool, bad)
	exact_count, hit_method = exact_min_deletions(pool, bad, time_limit_s=hit_s)
	cleaned = [pt for pt in pool if pt not in set(deleted_pts)]
	# Confirm cleaned has no non-primary ≥3-lines.
	bad2 = bad_general_lines(cleaned)
	if bad2:
		extra, _ = greedy_hitting_upper_bound(cleaned, bad2)
		cleaned = [pt for pt in cleaned if pt not in set(extra)]
		del_count += len(extra)
		hit_method = f"{hit_method}+extra_pass"

	packed, pst = exact_primary_max(cleaned, time_limit_s=bnb_s, seed=seed)
	# Re-check slopes after primary (subset of clean ⇒ clean).
	polished = greedy_augment(n, packed, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else packed
	ok2, reason2 = verify_claim(n, final)
	_, hjsw_pts = hjsw(p, cs[0] if cs else 1)
	stats = {
		"family": "mixed_kill_then_primary",
		"residues": cs,
		"pool": len(pool),
		"census": {
			"bad_lines": census["bad_lines"],
			"pure_lines": census["pure_lines"],
			"mixed_lines": census["mixed_lines"],
			"all_mixed": census["all_mixed"],
			"disjoint_lb": census["disjoint_lb"],
		},
		"mixed_deleted": del_count,
		"exact_min_deletions": exact_count,
		"hit_method": hit_method,
		"cleaned": len(cleaned),
		"primary_size": len(packed),
		"bnb": pst,
		"final_size": len(final),
		"ratio": len(final) / n if n else 0.0,
		"delta_vs_hjsw": len(final) - len(hjsw_pts),
		"verified": ok2,
		"reason": reason2,
	}
	return n, final, stats


def hjsw_protected_enrich(
	p: int,
	c1: int = 2,
	*,
	c0: int = 1,
	polish_s: float = 1.0,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""HJSW(c0) seed + H(c1) extras that preserve primary + all slopes.

	Never deletes seed points. Density ≥ classical when verification holds.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n, seed_pts = hjsw(p, c0)
	seed_set: Set[Point] = set(map(tuple, seed_pts))  # type: ignore[arg-type]
	c1 = c1 % p
	extras = [pt for pt in hyperbola_points(n, p, c1) if pt not in seed_set]
	pts: List[Point] = [tuple(p0) for p0 in seed_pts]  # type: ignore[misc]
	tables = build_slope_tables(pts)
	added: List[Point] = []
	for cand in extras:
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
		added.append(cand)

	# Safety net: repair mixed lines by deleting only non-seed points.
	bad = bad_general_lines(pts)
	deleted = 0
	live_set = set(pts)
	for line_pts in list(bad.values()):
		live = [pt for pt in line_pts if pt in live_set]
		while len(live) > 2:
			victims = [pt for pt in live if pt not in seed_set]
			if not victims:
				break
			v = victims[0]
			pts.remove(v)
			live_set.discard(v)
			live.remove(v)
			deleted += 1

	polished = greedy_augment(n, pts, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else pts
	ok2, reason2 = verify_claim(n, final)
	stats = {
		"family": "hjsw_protected_enrich",
		"c0": c0,
		"c1": c1,
		"seed_size": len(seed_pts),
		"extras_considered": len(extras),
		"extras_added": len(added),
		"extras_deleted_repair": deleted,
		"final_size": len(final),
		"ratio": len(final) / n if n else 0.0,
		"delta_vs_hjsw": len(final) - len(seed_pts),
		"verified": ok2,
		"reason": reason2,
	}
	return n, final, stats


def _point_risk_against(base: Sequence[Point], q: Point) -> int:
	"""Number of non-primary ≥3-lines in base∪{q} that contain q."""
	qt = tuple(q)  # type: ignore[misc]
	bad = bad_general_lines(list(base) + [qt])
	return sum(1 for pts in bad.values() if qt in pts)


def risk_masked_second_hyperbola(
	p: int,
	c0: int = 1,
	c1: int = 2,
	*,
	max_risk: int = 0,
	base_mode: str = "full",
	bnb_s: float = 4.0,
	polish_s: float = 1.5,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""Add H(c1) points whose mixed-line risk vs a base set is ≤ max_risk.

	`base_mode`:
	  - ``full``: risk against all of H(c0) (almost always total — safe≈0)
	  - ``primary``: risk against a primary packing of H(c0)
	  - ``hjsw``: risk against the classical HJSW seed for c0
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	c0, c1 = c0 % p, c1 % p
	h0 = hyperbola_points(n, p, c0)
	h1 = hyperbola_points(n, p, c1)
	if base_mode == "full":
		base: List[Point] = list(h0)
	elif base_mode == "primary":
		base, _ = exact_primary_max(h0, time_limit_s=bnb_s, seed=seed)
	elif base_mode == "hjsw":
		_, base = hjsw(p, c0)
		base = [tuple(pt) for pt in base]  # type: ignore[misc]
	else:
		raise ValueError(f"unknown base_mode {base_mode}")

	base_set = set(base)
	safe: List[Point] = []
	risk_hist: Counter = Counter()
	for q in h1:
		qt = tuple(q)  # type: ignore[misc]
		if qt in base_set:
			continue
		risk = _point_risk_against(base, qt)
		risk_hist[risk] += 1
		if risk <= max_risk:
			safe.append(qt)

	pool = list(base) + safe
	color = {pt: c0 for pt in base}
	for pt in safe:
		color[pt] = c1
	census = census_bad_lines(pool, color)
	bad = bad_general_lines(pool)
	deleted_pts: List[Point] = []
	if bad:
		deleted_pts, _ = greedy_hitting_upper_bound(pool, bad)
	cleaned = [pt for pt in pool if pt not in set(deleted_pts)]
	packed, pst = exact_primary_max(cleaned, time_limit_s=bnb_s, seed=seed)
	polished = greedy_augment(n, packed, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else packed
	ok2, reason2 = verify_claim(n, final)
	_, hjsw_pts = hjsw(p, c0)
	# Fair baseline: same polish budget on raw HJSW.
	hjsw_polished = greedy_augment(n, list(hjsw_pts), time_limit_s=polish_s, seed=seed)
	ok_h, _ = verify_claim(n, hjsw_polished)
	if not ok_h:
		hjsw_polished = list(hjsw_pts)
	stats = {
		"family": "risk_masked_second_h",
		"c0": c0,
		"c1": c1,
		"max_risk": max_risk,
		"base_mode": base_mode,
		"h0": len(h0),
		"h1": len(h1),
		"base_size": len(base),
		"safe_extras": len(safe),
		"risk_hist": dict(sorted(risk_hist.items())),
		"census_after_mask": {
			"bad_lines": census["bad_lines"],
			"pure": census["pure_lines"],
			"mixed": census["mixed_lines"],
		},
		"post_hit_deleted": len(deleted_pts),
		"cleaned": len(cleaned),
		"primary_size": len(packed),
		"bnb": pst,
		"final_size": len(final),
		"ratio": len(final) / n if n else 0.0,
		"delta_vs_hjsw": len(final) - len(hjsw_pts),
		"delta_vs_hjsw_polished": len(final) - len(hjsw_polished),
		"hjsw_polished": len(hjsw_polished),
		"verified": ok2,
		"reason": reason2,
	}
	return n, final, stats
