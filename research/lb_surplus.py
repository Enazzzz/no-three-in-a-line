"""LB vs surplus certificates for multi-hyperbola primary packings.

Correct scope (see docs/PROOF_LB_SURPLUS.md):

* NOT true for every primary-feasible S: an all-slope-valid subset T ⊆ ∪H(c)
  with |T| > 3(p−1) has LB=0 but positive surplus.
* Target statement: for *large* / max-primary packings S of ∪H(c) (|C|≥2),
  disjoint-excess LB(S) ≥ |S| − 3(p−1) when p≥17.

This module builds best-of warm-start/exact/greedy primary packings and
records LB − surplus.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Dict, List, Sequence, Tuple

from research.allslope_hitting import (
	bad_general_lines,
	disjoint_excess_lower_bound,
	excess_sum,
)
from research.constructions import hjsw, is_prime, next_prime
from research.hyperbola_union import hyperbola_points
from research.multi_hyperbola import default_residue_sets, multi_hyperbola_pool
from research.primary_repair import exact_primary_max, greedy_primary_max, primary_keys
from research.proof_single_h import classify_collinear_triples
from research.verify import verify_claim

Point = Tuple[int, int]


def best_primary_packing(
	pool: Sequence[Point],
	hjsw_pts: Sequence[Point],
	*,
	bnb_s: float = 1.5,
	seed: int = 0,
) -> Tuple[List[Point], dict]:
	"""Best of: HJSW warm-start greedy, exact BnB, and plain greedy."""
	pool_set = set(map(tuple, pool))  # type: ignore[arg-type]
	base = [tuple(p) for p in hjsw_pts if tuple(p) in pool_set]  # type: ignore[misc]
	counts: Counter = Counter()
	warm: List[Point] = list(base)
	for pt in warm:
		for k in primary_keys(pt):
			counts[k] += 1
	extra = list(pool_set - set(warm))
	rng = random.Random(seed)
	rng.shuffle(extra)
	class_members: Dict[Tuple[str, int], List[Point]] = {}
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

	exact, est = exact_primary_max(list(pool), time_limit_s=bnb_s, seed=seed)
	greedy = greedy_primary_max(list(pool), seed=seed)
	candidates = [
		("warm_hjsw", warm),
		("exact", exact),
		("greedy", greedy),
	]
	label, best = max(candidates, key=lambda t: len(t[1]))
	return best, {
		"method": label,
		"warm_size": len(warm),
		"exact_size": len(exact),
		"greedy_size": len(greedy),
		"exact_stats": est,
	}


def color_sizes(points: Sequence[Point], p: int) -> List[int]:
	"""Sizes of xy ≡ c (mod p) color classes, descending."""
	ct: Counter = Counter((x * y) % p for x, y in points)
	return sorted((v for k, v in ct.items() if k != 0), reverse=True)


def analyze_lb_surplus(
	p: int,
	residues: Sequence[int],
	*,
	bnb_s: float = 1.5,
	seed: int = 0,
) -> dict:
	"""One (p, C) certificate row."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	cs = [c % p for c in residues if c % p != 0]
	if len(cs) < 2:
		raise ValueError("need |C|≥2 for multi-hyperbola LB claim")
	n, pool = multi_hyperbola_pool(p, cs, mask_t2=False)
	_, hjsw_pts = hjsw(p, 1)
	S, pst = best_primary_packing(pool, hjsw_pts, bnb_s=bnb_s, seed=seed)
	bad = bad_general_lines(S)
	lb = disjoint_excess_lower_bound(bad)
	ex = excess_sum(bad)
	surplus = len(S) - len(hjsw_pts)
	gap = lb - surplus
	# Corollary check: all bad lines mixed (single-H theorem).
	# Color by xy mod p.
	pure = 0
	mixed = 0
	for pts in bad.values():
		labs = {(x * y) % p for x, y in pts}
		if len(labs) <= 1:
			pure += 1
		else:
			mixed += 1
	cols = color_sizes(S, p)
	minority = len(S) - cols[0] if cols else 0
	return {
		"p": p,
		"n": n,
		"residues": "|".join(str(c) for c in cs),
		"pool": len(pool),
		"hjsw": len(hjsw_pts),
		"primary": len(S),
		"primary_method": pst["method"],
		"surplus": surplus,
		"bad_lines": len(bad),
		"excess_sum": ex,
		"lb_disjoint": lb,
		"lb_minus_surplus": gap,
		"holds": int(gap >= 0),
		"pure_bad": pure,
		"mixed_bad": mixed,
		"color_sizes": ",".join(str(v) for v in cols),
		"minority": minority,
		"minority_over_3": minority // 3,
		"warm_size": pst["warm_size"],
		"exact_size": pst["exact_size"],
		"greedy_size": pst["greedy_size"],
	}


def ntil_surplus_counterexample(p: int, c1: int = 2, *, local_s: float = 1.5) -> dict:
	"""Exhibit primary-feasible T with |T|>HJSW but LB=0 (in-pool NTIL).

	Shows why the claim cannot quantify over *all* primary-feasible sets.
	"""
	from research.joint_pack import local_search

	n, hjsw_pts = hjsw(p, 1)
	_, pool = multi_hyperbola_pool(p, [1, c1], mask_t2=False)
	T = local_search(n, pool, hjsw_pts, time_limit_s=local_s, seed=p)
	ok, reason = verify_claim(n, T)
	bad = bad_general_lines(T)
	lb = disjoint_excess_lower_bound(bad)
	return {
		"p": p,
		"hjsw": len(hjsw_pts),
		"ntil_in_pool": len(T),
		"surplus": len(T) - len(hjsw_pts),
		"lb": lb,
		"bad_lines": len(bad),
		"verified_ntil": ok,
		"reason": reason,
		"shows_universal_claim_false": int(ok and len(T) > len(hjsw_pts) and lb == 0),
	}


def primes_from_to(lo: int, hi: int) -> List[int]:
	"""Odd primes in [lo, hi]."""
	out: List[int] = []
	p = next_prime(lo) if lo > 2 else 3
	if lo <= 3 and is_prime(3):
		p = 3
	while p <= hi:
		if p >= lo and is_prime(p):
			out.append(p)
		p = next_prime(p + 1)
	return out
