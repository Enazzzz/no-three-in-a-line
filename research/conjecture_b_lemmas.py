"""Certificate for Conjecture B proof reduction (board multi-H pools).

Conjecture B would follow from two lemmas on a max-primary (or algorithmic
large-primary) set S ⊆ U(C):

* (B1) LB(S) ≥ ⌊m(S)/3⌋, where m is minority color mass
* (B2) ⌊m(S)/3⌋ ≥ surplus(S) = |S| − 3(p−1)

This module recomputes those quantities on the same best-of primary packings
used for Certificate B′ and records coverage / mono-color diagnostics.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Tuple

from research.allslope_hitting import bad_general_lines, disjoint_excess_lower_bound
from research.constructions import hjsw, is_prime
from research.hyperbola_union import hyperbola_points
from research.lb_surplus import best_primary_packing
from research.multi_hyperbola import default_residue_sets, multi_hyperbola_pool
from research.primary_repair import exact_primary_max, greedy_primary_max
from research.verify import verify_claim

Point = Tuple[int, int]


def board_color(pt: Point, p: int) -> int:
	"""Board residue ``xy mod p`` (board-pool coloring)."""
	return (pt[0] * pt[1]) % p


def minority_stats(S: Sequence[Point], p: int) -> dict:
	"""Majority / minority sizes and bad-line coverage of minority points."""
	pts = [tuple(q) for q in S]  # type: ignore[misc]
	cols = Counter(board_color(pt, p) for pt in pts)
	if not cols:
		return {
			"majority": 0,
			"minority": 0,
			"majority_color": 0,
			"color_sizes": "",
			"minority_covered": 0,
			"coverage_frac": 1.0,
			"bad_lines": 0,
		}
	maj_c = max(cols, key=cols.get)
	majority = cols[maj_c]
	minor = [pt for pt in pts if board_color(pt, p) != maj_c]
	bad = bad_general_lines(pts)
	covered = {q for L in bad.values() for q in L if board_color(q, p) != maj_c}
	m = len(minor)
	return {
		"majority": majority,
		"minority": m,
		"majority_color": maj_c,
		"color_sizes": ",".join(str(v) for v in sorted(cols.values(), reverse=True)),
		"minority_covered": len(covered),
		"coverage_frac": (len(covered) / m) if m else 1.0,
		"bad_lines": len(bad),
	}


def analyze_reduction(
	p: int,
	residues: Sequence[int],
	*,
	bnb_s: float = 1.0,
	seed: int = 0,
) -> dict:
	"""One row of the B1/B2 reduction certificate."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	cs = [c % p for c in residues if c % p != 0]
	n, pool = multi_hyperbola_pool(p, cs, mask_t2=False)
	_, hj = hjsw(p, 1)
	S, pst = best_primary_packing(pool, hj, bnb_s=bnb_s, seed=seed)
	ms = minority_stats(S, p)
	bad = bad_general_lines(S)
	lb = disjoint_excess_lower_bound(bad)
	surplus = len(S) - len(hj)
	m = ms["minority"]
	m3 = m // 3
	return {
		"p": p,
		"n": n,
		"residues": "|".join(str(c) for c in cs),
		"pool": len(pool),
		"hjsw": len(hj),
		"primary": len(S),
		"primary_method": pst["method"],
		"majority": ms["majority"],
		"minority": m,
		"minority_covered": ms["minority_covered"],
		"coverage_frac": f"{ms['coverage_frac']:.4f}",
		"color_sizes": ms["color_sizes"],
		"bad_lines": ms["bad_lines"],
		"lb_disjoint": lb,
		"surplus": surplus,
		"floor_m_over_3": m3,
		"b1_lb_ge_m3": int(lb >= m3),
		"b2_m3_ge_surplus": int(m3 >= surplus),
		"implies_B": int(lb >= m3 >= surplus),
		"lb_minus_surplus": lb - surplus,
	}


def mono_color_primary_bound(p: int, c: int = 1, *, bnb_s: float = 2.0, seed: int = 0) -> dict:
	"""Max primary packing inside a single board hyperbola (empirical bound).

	By ``PROOF_SINGLE_H``, primary-feasible ⇒ NTIL on one color. Size is still
	far below HJSW on the primes probed (HJSW lives in ambient T2, not board H).
	"""
	n = 2 * p
	pool = hyperbola_points(n, p, c)
	_, hj = hjsw(p, 1)
	g = greedy_primary_max(pool, seed=seed)
	ex, _ = exact_primary_max(pool, time_limit_s=bnb_s, seed=seed)
	best = max(g, ex, key=len)
	ok, _ = verify_claim(n, best)
	return {
		"p": p,
		"c": c % p,
		"pool": len(pool),
		"hjsw": len(hj),
		"greedy": len(g),
		"exact": len(ex),
		"best": len(best),
		"best_over_hjsw": f"{len(best) / len(hj):.4f}" if hj else "",
		"verified_ntil": int(ok),
	}


def scan_reduction_rows(
	*,
	lo: int = 17,
	hi: int = 79,
	bnb_s: float = 1.0,
) -> List[dict]:
	"""All default ``|C|≥2`` residue sets in ``[lo, hi]``."""
	from research.lb_surplus import primes_from_to

	out: List[dict] = []
	for p in primes_from_to(lo, hi):
		for C in default_residue_sets(p):
			if len(C) < 2:
				continue
			out.append(analyze_reduction(p, C, bnb_s=bnb_s, seed=p))
	return out
