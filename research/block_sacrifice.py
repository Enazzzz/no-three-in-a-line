"""HJSW geometric block sacrifice then polish / M-refill.

Motivation: multi-H primary-then-repair is closed (`PROOF_LB_SURPLUS.md`).
This module tries a different cut — delete one (or one family of) T2
half-block(s) from HJSW, optionally refill from middle-block hyperbola
cells, then greedy-polish.

Empirically this only moves O(1) vs a multi-seed polished-HJSW baseline and
is comparable to deleting a random subset of the same size (polish-path
noise), so it is a documented dead end rather than a density advance.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence, Set, Tuple

from research.algebraic import saturated_differences, unsaturated_hv_candidates
from research.constructions import (
	_shifted_block,
	ambient_grid,
	hjsw,
	is_prime,
)
from research.hyperbola_union import hyperbola_points
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]

T2_SPECS: List[Tuple[str, int, int]] = [
	("A", 0, 1),
	("A", 1, 0),
	("A", 1, 1),
	("B", -1, 0),
	("B", -1, 1),
	("B", 0, 1),
	("C", 0, 0),
	("C", 1, 0),
	("C", 1, 1),
	("D", -1, 0),
	("D", -1, 1),
	("D", 0, 0),
]

M_SPECS: List[Tuple[str, int, int]] = [
	("A", 0, 0),
	("B", 0, 0),
	("C", 0, 1),
	("D", 0, 1),
]


def _board_shift(p: int) -> Tuple[int, int]:
	"""Shift taking ambient G(p) into the [1,n]² board used by hjsw()."""
	xmin, _xmax, ymin, _ymax = ambient_grid(p)
	return 1 - xmin, 1 - ymin


def block_on_board(kind: str, r: int, s: int, p: int) -> Set[Point]:
	"""Translate one ambient half-block into board coordinates."""
	sx, sy = _board_shift(p)
	n = 2 * p
	out: Set[Point] = set()
	for x, y in _shifted_block(kind, r, s, p):
		xx, yy = x + sx, y + sy
		if 1 <= xx <= n and 1 <= yy <= n:
			out.add((xx, yy))
	return out


def middle_on_board(p: int) -> Set[Point]:
	"""Union of middle blocks M on the board."""
	out: Set[Point] = set()
	for kind, r, s in M_SPECS:
		out |= block_on_board(kind, r, s, p)
	return out


def enrich_allslope(
	n: int,
	seed: Sequence[Point],
	extras: Sequence[Point],
) -> Tuple[List[Point], int]:
	"""Greedily add extras preserving primary caps and all slopes."""
	pts: List[Point] = [tuple(p) for p in seed]  # type: ignore[misc]
	tables = build_slope_tables(pts)
	added = 0
	for cand in extras:
		qt = tuple(cand)  # type: ignore[misc]
		if qt in set(pts):
			continue
		if not unsaturated_hv_candidates(n, pts, [qt]):
			continue
		sat_plus, sat_minus = saturated_differences(pts)
		x, y = qt
		if (x - y) in sat_plus or (x + y) in sat_minus:
			continue
		if not individually_addable(qt, pts, tables):
			continue
		tables[qt] = set()
		for q in pts:
			s = _norm_slope(x - q[0], y - q[1])
			tables[q].add(s)
			tables[qt].add(s)
		pts.append(qt)
		added += 1
	return pts, added


def multi_seed_polish(
	n: int,
	pts: Sequence[Point],
	*,
	polish_s: float,
	seeds: Sequence[int],
) -> List[Point]:
	"""Best verified greedy polish over several RNG seeds."""
	best: List[Point] = [tuple(p) for p in pts]  # type: ignore[misc]
	for s in seeds:
		pol = greedy_augment(n, list(pts), time_limit_s=polish_s, seed=s)
		ok, _ = verify_claim(n, pol)
		if ok and len(pol) > len(best):
			best = pol
	ok2, _ = verify_claim(n, best)
	if not ok2:
		# Fall back to the seed itself if somehow unverified.
		best = [tuple(p) for p in pts]  # type: ignore[misc]
	return best


def refill_pools(p: int, seed_pts: Sequence[Point]) -> Dict[str, List[Point]]:
	"""Named refill candidate pools after a sacrifice."""
	n = 2 * p
	H1 = set(hyperbola_points(n, p, 1))
	H2 = set(hyperbola_points(n, p, 2))
	M = middle_on_board(p)
	seed_set = set(map(tuple, seed_pts))  # type: ignore[arg-type]
	return {
		"none": [],
		"M_H1": sorted(M & H1),
		"M_H2": sorted(M & H2),
		"M_H12": sorted(M & (H1 | H2)),
		"H2": sorted(H2 - seed_set),
	}


def run_block_sacrifice(
	p: int,
	*,
	polish_s: float = 0.7,
	n_polish_seeds: int = 6,
	seed: int = 0,
	include_random_control: bool = True,
) -> dict:
	"""Best single-block sacrifice vs multi-seed polished HJSW baseline."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n, hjsw_pts = hjsw(p, 1)
	polish_seeds = [seed + i for i in range(n_polish_seeds)]
	baseline = multi_seed_polish(n, hjsw_pts, polish_s=polish_s, seeds=polish_seeds)
	pools = refill_pools(p, hjsw_pts)

	best = {
		"final": len(baseline),
		"delta_vs_baseline": 0,
		"tag": "hjsw_polished",
		"dropped": 0,
		"refill_added": 0,
	}

	rng = random.Random(seed + p)
	random_deltas: List[int] = []

	for spec in T2_SPECS:
		blk = block_on_board(*spec, p)
		if not blk:
			continue
		reduced = [pt for pt in hjsw_pts if pt not in blk]
		dropped = len(hjsw_pts) - len(reduced)
		for rname, pool in pools.items():
			pts, added = enrich_allslope(n, reduced, pool)
			final = multi_seed_polish(n, pts, polish_s=polish_s, seeds=polish_seeds)
			if len(final) > best["final"]:
				best = {
					"final": len(final),
					"delta_vs_baseline": len(final) - len(baseline),
					"tag": f"drop_{spec[0]}{spec[1]}_{spec[2]}+{rname}",
					"dropped": dropped,
					"refill_added": added,
				}

		# Random control: same cardinality deletion, no refill, same polish.
		if include_random_control and dropped > 0:
			for _ in range(4):
				victims = set(rng.sample(list(hjsw_pts), dropped))
				red = [pt for pt in hjsw_pts if pt not in victims]
				fin = multi_seed_polish(n, red, polish_s=polish_s, seeds=polish_seeds)
				random_deltas.append(len(fin) - len(baseline))

	return {
		"p": p,
		"n": n,
		"hjsw": len(hjsw_pts),
		"baseline_polished": len(baseline),
		"best_final": best["final"],
		"delta_vs_baseline": best["delta_vs_baseline"],
		"best_tag": best["tag"],
		"dropped": best["dropped"],
		"refill_added": best["refill_added"],
		"random_delta_max": max(random_deltas) if random_deltas else "",
		"random_delta_mean": (
			f"{sum(random_deltas) / len(random_deltas):.2f}" if random_deltas else ""
		),
		"beats_random_max": (
			int(best["delta_vs_baseline"] > max(random_deltas)) if random_deltas else ""
		),
	}
