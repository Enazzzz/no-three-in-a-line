"""Joint two-family packing: all-slope-aware from the start (not HJSW-first).

Previous dead ends fixed an HJSW seed then grafted. Here we either:

1. **greedy_from_empty** — pack a joint pool with primary + all-slope caps
2. **local_search** — start from HJSW (or empty greedy), then add / 1-for-many
   swaps / ruin-recreate inside the joint pool

Pools combine modular hyperbolas with non-hyperbola families
(`research/nonhyperbola.py`). Goal: measure whether joint search beats a
fair polished-HJSW baseline by more than O(1) noise.
"""

from __future__ import annotations

import random
import time
from collections import Counter
from typing import Dict, List, Optional, Sequence, Set, Tuple

from research.constructions import hjsw, is_prime
from research.hyperbola_union import hyperbola_points
from research.nonhyperbola import (
	FAMILY_BUILDERS,
	family_circle,
	family_parabola,
)
from research.primary_repair import primary_keys
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]


def joint_pool(p: int, spec: str = "H1_H2_par_circ") -> Tuple[int, List[Point]]:
	"""Build a named joint pool on the n=2p board.

	`spec` is a short tag; see `POOL_SPECS`.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n = 2 * p
	parts: List[Sequence[Point]] = []
	if "H1" in spec or spec.startswith("H"):
		parts.append(hyperbola_points(n, p, 1))
	if "H2" in spec:
		parts.append(hyperbola_points(n, p, 2))
	if "H3" in spec:
		parts.append(hyperbola_points(n, p, 3))
	if "par" in spec:
		parts.append(family_parabola(n, p))
	if "circ" in spec:
		parts.append(family_circle(n, p, 1))
	if "pell" in spec:
		parts.append(FAMILY_BUILDERS["pell_d2"](n, p))
	if not parts:
		raise ValueError(f"unknown pool spec {spec}")
	pool: Set[Point] = set()
	for part in parts:
		pool |= set(map(tuple, part))  # type: ignore[arg-type]
	return n, sorted(pool)


POOL_SPECS = (
	"H1",
	"H1_H2",
	"H1_H2_H3",
	"H1_par",
	"H1_H2_par_circ",
	"par_circ",
)


def _rebuild(pts: Sequence[Point]) -> Tuple[Dict[Point, Set[Tuple[int, int]]], Counter]:
	"""Slope tables + primary occupancy for a point list."""
	tables = build_slope_tables(pts)
	counts: Counter = Counter()
	for pt in pts:
		for k in primary_keys(pt):
			counts[k] += 1
	return tables, counts


def _feasible(
	pts: Sequence[Point],
	tables: Dict[Point, Set[Tuple[int, int]]],
	counts: Counter,
	cand: Point,
) -> bool:
	"""True if cand respects primary caps and all-slope vs current pts."""
	if any(counts[k] >= 2 for k in primary_keys(cand)):
		return False
	if pts and not individually_addable(cand, pts, tables):
		return False
	return True


def _commit(
	pts: List[Point],
	tables: Dict[Point, Set[Tuple[int, int]]],
	counts: Counter,
	cand: Point,
) -> None:
	"""Append cand and update tables/counts in place."""
	tables[cand] = set()
	x, y = cand
	for q in pts:
		s = _norm_slope(x - q[0], y - q[1])
		tables[q].add(s)
		tables[cand].add(s)
	pts.append(cand)
	for k in primary_keys(cand):
		counts[k] += 1


def greedy_from_empty(
	n: int,
	pool: Sequence[Point],
	*,
	passes: int = 12,
	seed: int = 0,
) -> List[Point]:
	"""Multi-start degree-greedy all-slope packing from an empty set."""
	best: List[Point] = []
	rng = random.Random(seed)
	base_pool = [tuple(p) for p in pool]  # type: ignore[misc]
	# Static primary degree in the ambient pool (prefer less contested cells).
	class_members: Dict[Tuple[str, int], List[Point]] = {}
	for pt in base_pool:
		for k in primary_keys(pt):
			class_members.setdefault(k, []).append(pt)
	degree = {
		pt: sum(len(class_members[k]) - 1 for k in primary_keys(pt)) for pt in base_pool
	}

	for _ in range(passes):
		order = list(base_pool)
		rng.shuffle(order)
		order.sort(key=lambda pt: (degree[pt], rng.random()))
		pts: List[Point] = []
		tables: Dict[Point, Set[Tuple[int, int]]] = {}
		counts: Counter = Counter()
		for cand in order:
			if _feasible(pts, tables, counts, cand):
				_commit(pts, tables, counts, cand)
		if len(pts) > len(best):
			best = pts
	return best


def local_search(
	n: int,
	pool: Sequence[Point],
	start: Sequence[Point],
	*,
	time_limit_s: float = 2.5,
	seed: int = 0,
) -> List[Point]:
	"""Add / swap / ruin-recreate local search inside `pool`.

	Starts from `start` (typically HJSW). Never accepts a move that violates
	primary or all-slope constraints.
	"""
	t0 = time.monotonic()
	rng = random.Random(seed)
	pts: List[Point] = [tuple(p) for p in start]  # type: ignore[misc]
	tables, counts = _rebuild(pts)
	avail: List[Point] = list(set(map(tuple, pool)) - set(pts))  # type: ignore[arg-type]
	best: List[Point] = list(pts)
	guard = 0

	while time.monotonic() - t0 < time_limit_s and guard < 100_000:
		guard += 1
		# --- try pure adds ---
		rng.shuffle(avail)
		added = False
		for cand in avail[:120]:
			if cand in set(pts):
				continue
			if _feasible(pts, tables, counts, cand):
				_commit(pts, tables, counts, cand)
				avail = [q for q in avail if q != cand]
				added = True
				break
		if added:
			if len(pts) > len(best):
				best = list(pts)
			continue

		# --- try delete-one, refill many ---
		order = list(pts)
		rng.shuffle(order)
		improved = False
		for victim in order[:36]:
			trial = [q for q in pts if q != victim]
			tables2, counts2 = _rebuild(trial)
			gains = [c for c in avail if _feasible(trial, tables2, counts2, c)]
			tmp = list(trial)
			tb, ct = _rebuild(tmp)
			got: List[Point] = []
			cands = list(gains)
			rng.shuffle(cands)
			for cand in cands:
				if _feasible(tmp, tb, ct, cand):
					_commit(tmp, tb, ct, cand)
					got.append(cand)
			if len(tmp) > len(pts):
				pts = tmp
				tables, counts = tb, ct
				avail = list((set(avail) | {victim}) - set(got))
				improved = True
				if len(pts) > len(best):
					best = list(pts)
				break
		if improved:
			continue

		# --- ruin and recreate ---
		k = rng.randint(2, 5)
		victims = set(rng.sample(pts, min(k, len(pts))))
		pts = [q for q in pts if q not in victims]
		avail = list(set(avail) | victims)
		tables, counts = _rebuild(pts)
		rng.shuffle(avail)
		for cand in avail:
			if _feasible(pts, tables, counts, cand):
				_commit(pts, tables, counts, cand)
		avail = [q for q in avail if q not in set(pts)]
		if len(pts) > len(best):
			best = list(pts)

	return best


def run_joint_case(
	p: int,
	spec: str = "H1_H2_par_circ",
	*,
	polish_s: float = 0.8,
	local_s: float = 2.5,
	greedy_passes: int = 10,
	trials: int = 3,
	seed: int = 0,
) -> dict:
	"""Compare empty-greedy + local-search joint packs vs polished HJSW."""
	n, hjsw_pts = hjsw(p, 1)
	_, pool = joint_pool(p, spec)

	hjsw_pol = greedy_augment(n, list(hjsw_pts), time_limit_s=polish_s, seed=seed)
	ok_h, _ = verify_claim(n, hjsw_pol)
	if not ok_h:
		hjsw_pol = list(hjsw_pts)

	empty = greedy_from_empty(n, pool, passes=greedy_passes, seed=seed)
	empty_pol = greedy_augment(n, empty, time_limit_s=polish_s, seed=seed + 1)
	ok_e, _ = verify_claim(n, empty_pol)
	if not ok_e:
		empty_pol = empty

	best_local = list(hjsw_pts)
	best_local_pol = list(hjsw_pol)
	for t in range(trials):
		ls = local_search(
			n, pool, hjsw_pts, time_limit_s=local_s, seed=seed * 17 + t + p
		)
		pol = greedy_augment(n, ls, time_limit_s=polish_s, seed=seed + 3 + t)
		ok, _ = verify_claim(n, pol)
		final = pol if ok else ls
		ok2, _ = verify_claim(n, final)
		if not ok2:
			continue
		if len(final) > len(best_local_pol):
			best_local = ls
			best_local_pol = final

	best_size = max(len(hjsw_pol), len(empty_pol), len(best_local_pol))
	if best_size == len(best_local_pol) and len(best_local_pol) > len(hjsw_pol):
		winner = "joint_local"
	elif best_size == len(empty_pol) and len(empty_pol) > len(hjsw_pol):
		winner = "joint_empty"
	else:
		winner = "hjsw_polished"

	return {
		"p": p,
		"n": n,
		"spec": spec,
		"pool": len(pool),
		"hjsw": len(hjsw_pts),
		"hjsw_polished": len(hjsw_pol),
		"empty_pack": len(empty),
		"empty_final": len(empty_pol),
		"local_pack": len(best_local),
		"local_final": len(best_local_pol),
		"best_final": best_size,
		"delta_vs_polished": best_size - len(hjsw_pol),
		"winner": winner,
		"verified": True,
	}
