"""Ambient-aligned multi-hyperbola pools (same shift as HJSW).

Critical distinction vs `multi_hyperbola_pool` / board `hyperbola_points`:

* Board pools collect cells with ``x*y ≡ c (mod p)`` **after** the ambient→board
  shift. Those generally do **not** contain HJSW: overlap is often 0.
* This module builds hyperbolas in ambient ``G(p)``, optionally ∩ T2 / T2∪M,
  then applies the **same** translation as ``hjsw()``. Then HJSW ⊂ pool when
  residue 1 and region ⊇ T2.

Construction pipeline: warm-start from HJSW inside the ambient pool, run
all-slope local search + unstructured polish, compare to multi-seed polished
HJSW. Finite gains are reported honestly — not claimed as asymptotic.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Iterable, List, Sequence, Set, Tuple

from research.allslope_hitting import (
	bad_general_lines,
	disjoint_excess_lower_bound,
	excess_sum,
)
from research.constructions import (
	ambient_grid,
	hjsw,
	is_prime,
	middle_blocks,
	t2_blocks,
)
from research.joint_pack import local_search
from research.multi_hyperbola import multi_hyperbola_pool
from research.primary_repair import exact_primary_max, greedy_primary_max, primary_keys
from research.search import greedy_augment
from research.verify import verify_claim

Point = Tuple[int, int]

# Region tags for ambient masks before the HJSW shift.
REGION_T2 = "t2"
REGION_T2M = "t2m"
REGION_G = "g"


def ambient_shift(p: int) -> Tuple[int, int, int]:
	"""Return ``(shift_x, shift_y, n)`` matching ``hjsw()``."""
	xmin, _, ymin, _ = ambient_grid(p)
	n = 2 * p
	return 1 - xmin, 1 - ymin, n


def shift_ambient_to_board(points: Iterable[Point], p: int) -> List[Point]:
	"""Map ambient points into ``[1,n]²`` with the HJSW translation."""
	sx, sy, n = ambient_shift(p)
	out: Set[Point] = set()
	for x, y in points:
		bx, by = x + sx, y + sy
		if 1 <= bx <= n and 1 <= by <= n:
			out.add((bx, by))
	return sorted(out)


def ambient_region(p: int, region: str = REGION_T2) -> Set[Point]:
	"""Ambient integer cells for the named mask, clipped to ``G(p)``."""
	xmin, xmax, ymin, ymax = ambient_grid(p)
	if region == REGION_T2:
		raw = t2_blocks(p)
	elif region == REGION_T2M:
		raw = t2_blocks(p) | middle_blocks(p)
	elif region == REGION_G:
		raw = {
			(x, y)
			for x in range(xmin, xmax + 1)
			for y in range(ymin, ymax + 1)
		}
	else:
		raise ValueError(f"unknown region {region!r}")
	return {
		(x, y)
		for x, y in raw
		if xmin <= x <= xmax and ymin <= y <= ymax
	}


def ambient_hyperbola_points(p: int, c: int, region: str = REGION_T2) -> Set[Point]:
	"""Ambient points of ``xy ≡ c (mod p)`` inside the named region ∩ ``G(p)``."""
	c = c % p
	if c == 0:
		return set()
	out: Set[Point] = set()
	for x, y in ambient_region(p, region):
		if x % p == 0 or y % p == 0:
			continue
		if (x * y - c) % p == 0:
			out.add((x, y))
	return out


def ambient_multi_pool(
	p: int,
	residues: Sequence[int],
	*,
	region: str = REGION_T2,
) -> Tuple[int, List[Point]]:
	"""Board pool = shift(⋃_c ambient H(c) ∩ region).

	When ``1 ∈ residues`` and ``region`` contains T2, ``hjsw(p)`` is a subset.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	cs = sorted({c % p for c in residues if c % p != 0})
	amb: Set[Point] = set()
	for c in cs:
		amb |= ambient_hyperbola_points(p, c, region)
	board = shift_ambient_to_board(amb, p)
	n = 2 * p
	return n, board


def hjsw_overlap(p: int, pool: Sequence[Point]) -> int:
	"""How many HJSW points lie in ``pool``."""
	_, hj = hjsw(p, 1)
	return len(set(map(tuple, hj)) & set(map(tuple, pool)))


def board_vs_ambient_overlap(p: int, residues: Sequence[int]) -> dict:
	"""Document that board multi-H and ambient multi-H are different sets."""
	n, board_pool = multi_hyperbola_pool(p, residues, mask_t2=False)
	_, amb_pool = ambient_multi_pool(p, residues, region=REGION_T2M)
	_, hj = hjsw(p, 1)
	hs = set(map(tuple, hj))
	bs = set(map(tuple, board_pool))
	as_ = set(map(tuple, amb_pool))
	return {
		"p": p,
		"n": n,
		"board_pool": len(bs),
		"ambient_pool": len(as_),
		"board_∩_ambient": len(bs & as_),
		"hjsw_in_board": len(hs & bs),
		"hjsw_in_ambient": len(hs & as_),
		"hjsw": len(hs),
	}


def _greedy_primary_from_seed(
	pool: Sequence[Point],
	seed: Sequence[Point],
	*,
	rng_seed: int = 0,
) -> List[Point]:
	"""Primary-feasible packing: keep seed ∩ pool, then greedy fill."""
	pool_set = set(map(tuple, pool))  # type: ignore[arg-type]
	warm: List[Point] = [tuple(p) for p in seed if tuple(p) in pool_set]  # type: ignore[misc]
	counts: Counter = Counter()
	for pt in warm:
		for k in primary_keys(pt):
			counts[k] += 1
	extra = list(pool_set - set(warm))
	rng = random.Random(rng_seed)
	rng.shuffle(extra)
	class_members: dict = {}
	for pt in extra:
		for k in primary_keys(pt):
			class_members.setdefault(k, []).append(pt)
	extra.sort(key=lambda pt: sum(len(class_members.get(k, [])) for k in primary_keys(pt)))
	for pt in extra:
		if any(counts[k] >= 2 for k in primary_keys(pt)):
			continue
		warm.append(pt)
		for k in primary_keys(pt):
			counts[k] += 1
	return warm


def analyze_ambient_primary(
	p: int,
	residues: Sequence[int],
	*,
	region: str = REGION_T2M,
	bnb_s: float = 1.0,
	seed: int = 0,
) -> dict:
	"""Primary packing of an ambient-aligned pool + LB vs surplus.

	Unlike board-coordinate pools, HJSW warm-start is meaningful here.
	"""
	n, pool = ambient_multi_pool(p, residues, region=region)
	_, hj = hjsw(p, 1)
	warm = _greedy_primary_from_seed(pool, hj, rng_seed=seed)
	exact, _ = exact_primary_max(list(pool), time_limit_s=bnb_s, seed=seed)
	greedy = greedy_primary_max(list(pool), seed=seed)
	label, S = max(
		[("warm_hjsw", warm), ("exact", exact), ("greedy", greedy)],
		key=lambda t: len(t[1]),
	)
	bad = bad_general_lines(S)
	lb = disjoint_excess_lower_bound(bad)
	ex = excess_sum(bad)
	surplus = len(S) - len(hj)
	return {
		"p": p,
		"n": n,
		"region": region,
		"residues": "|".join(str(c) for c in residues),
		"pool": len(pool),
		"hjsw": len(hj),
		"hjsw_in_pool": hjsw_overlap(p, pool),
		"primary": len(S),
		"primary_method": label,
		"surplus": surplus,
		"bad_lines": len(bad),
		"excess_sum": ex,
		"lb_disjoint": lb,
		"lb_minus_surplus": lb - surplus,
		"holds": int(lb >= surplus),
	}


def run_ambient_case(
	p: int,
	residues: Sequence[int],
	*,
	region: str = REGION_T2M,
	polish_s: float = 0.8,
	local_s: float = 2.5,
	trials: int = 3,
	seed: int = 0,
) -> dict:
	"""Fair local-search pack in ambient pool vs multi-seed polished HJSW."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n, pool = ambient_multi_pool(p, residues, region=region)
	_, hj = hjsw(p, 1)
	overlap = hjsw_overlap(p, pool)

	# Multi-seed polish of HJSW alone (baseline).
	best_hj = list(hj)
	for t in range(trials):
		pol = greedy_augment(n, list(hj), time_limit_s=polish_s, seed=seed + t)
		ok, _ = verify_claim(n, pol)
		if ok and len(pol) > len(best_hj):
			best_hj = pol

	# Local search inside ambient pool, seeded from HJSW.
	best_local = list(hj)
	best_final = list(best_hj)
	for t in range(trials):
		ls = local_search(
			n, pool, hj, time_limit_s=local_s, seed=seed * 19 + t + p
		)
		pol = greedy_augment(n, ls, time_limit_s=polish_s, seed=seed + 50 + t)
		ok, _ = verify_claim(n, pol)
		final = pol if ok else ls
		ok2, _ = verify_claim(n, final)
		if not ok2:
			continue
		if len(ls) > len(best_local):
			best_local = ls
		if len(final) > len(best_final):
			best_final = final

	# Empty-ish: local search from warm primary packing (not HJSW).
	warm = _greedy_primary_from_seed(pool, hj, rng_seed=seed)
	# Repair warm via local search may start invalid — start from HJSW if warm dirty.
	ok_w, _ = verify_claim(n, warm)
	start2 = warm if ok_w else hj
	ls2 = local_search(n, pool, start2, time_limit_s=local_s, seed=seed + 99)
	pol2 = greedy_augment(n, ls2, time_limit_s=polish_s, seed=seed + 100)
	ok3, _ = verify_claim(n, pol2)
	alt = pol2 if ok3 else ls2
	if verify_claim(n, alt)[0] and len(alt) > len(best_final):
		best_final = alt

	delta = len(best_final) - len(best_hj)
	winner = "ambient_local" if delta > 0 else "hjsw_polished"
	return {
		"p": p,
		"n": n,
		"region": region,
		"residues": "|".join(str(c % p) for c in residues if c % p),
		"pool": len(pool),
		"hjsw": len(hj),
		"hjsw_in_pool": overlap,
		"hjsw_polished": len(best_hj),
		"local_pack": len(best_local),
		"best_final": len(best_final),
		"delta_vs_hjsw": len(best_final) - len(hj),
		"delta_vs_polished": delta,
		"winner": winner,
		"verified": int(verify_claim(n, best_final)[0]),
	}


def default_residues(p: int, k: int = 3) -> List[int]:
	"""First ``k`` nonzero residues ``1..`` for ambient unions."""
	out: List[int] = []
	c = 1
	while len(out) < k and c < p:
		out.append(c)
		c += 1
	return out
