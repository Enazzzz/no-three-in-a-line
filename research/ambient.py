"""Ambient board size vs modular hyperbola cleanliness and density.

Key law (extends PROOF_SINGLE_H.md): on board size n with modulus p,

* for n ≤ 2p every residue in F_p^* has ≤2 lifts, and H(c) stays
  non-primary-clean;
* for n ≥ 2p+1 some residues get a third lift and non-primary ≥3-lines appear.

This module certifies the boundary and probes densities for n ≠ 2p.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from research.allslope_hitting import is_primary_dir, lines_with_counts
from research.constructions import hjsw, is_prime, next_prime
from research.search import greedy_augment
from research.verify import verify_claim

Point = Tuple[int, int]


def hyperbola_lifts(n: int, p: int, c: int = 1) -> List[Point]:
	"""Board points with xy ≡ c (mod p), p ∤ x, p ∤ y, for general n."""
	c = c % p
	pts: List[Point] = []
	for x in range(1, n + 1):
		if x % p == 0:
			continue
		y0 = (c * pow(x, -1, p)) % p
		if y0 == 0:
			continue
		y = y0
		while y <= n:
			pts.append((x, y))
			y += p
	return pts


def max_lifts_per_residue(n: int, p: int) -> int:
	"""Maximum number of board lifts of a single F_p^* residue in {1..n}."""
	# Residue r has lifts r, r+p, r+2p, ... while ≤ n.
	best = 0
	for r in range(1, p):
		k = 0
		x = r
		while x <= n:
			k += 1
			x += p
		best = max(best, k)
	return best


def nonprimary_ge3_count(points: Sequence[Point]) -> int:
	"""Count non-primary lines with ≥3 points."""
	n = 0
	for (dx, dy, _b), pts in lines_with_counts(points).items():
		if len(pts) >= 3 and not is_primary_dir(dx, dy):
			n += 1
	return n


def census_ambient(p: int, n: int, c: int = 1) -> dict:
	"""Cleanliness + lift census for one (p, n)."""
	H = hyperbola_lifts(n, p, c)
	return {
		"p": p,
		"n": n,
		"c": c % p,
		"pool": len(H),
		"max_lifts": max_lifts_per_residue(n, p),
		"nonprimary_ge3": nonprimary_ge3_count(H),
		"clean": int(nonprimary_ge3_count(H) == 0),
		"expected_clean": int(n <= 2 * p),
	}


def certify_sharp_bound(p: int) -> dict:
	"""Check clean at n=2p and dirty at n=2p+1 (when 2p+1 makes sense)."""
	at_2p = census_ambient(p, 2 * p)
	at_2p1 = census_ambient(p, 2 * p + 1)
	ok = at_2p["clean"] == 1 and at_2p1["clean"] == 0 and at_2p["max_lifts"] == 2 and at_2p1["max_lifts"] >= 3
	return {
		"p": p,
		"clean_at_2p": at_2p["clean"],
		"clean_at_2p1": at_2p1["clean"],
		"max_lifts_2p": at_2p["max_lifts"],
		"max_lifts_2p1": at_2p1["max_lifts"],
		"nonprim_2p": at_2p["nonprimary_ge3"],
		"nonprim_2p1": at_2p1["nonprimary_ge3"],
		"sharp_ok": int(ok),
	}


def density_probe(p: int, n: int, *, polish_s: float = 0.6, seed: int = 0) -> dict:
	"""Polish HJSW cropped/padded to board n; report ratio vs n=2p baseline."""
	n0, hjsw_pts = hjsw(p, 1)
	base = greedy_augment(n0, list(hjsw_pts), time_limit_s=polish_s, seed=seed)
	ok, _ = verify_claim(n0, base)
	if not ok:
		base = list(hjsw_pts)

	fit = [(x, y) for x, y in hjsw_pts if 1 <= x <= n and 1 <= y <= n]
	# If n > n0, also allow H(c) points on the larger board as extras via polish only
	# starting from fit (greedy_augment searches the full board).
	pol = greedy_augment(n, fit if fit else [(1, 1)], time_limit_s=polish_s, seed=seed + n)
	ok2, _ = verify_claim(n, pol)
	final = pol if ok2 else fit
	return {
		"p": p,
		"n": n,
		"n0": n0,
		"hjsw_polished_2p": len(base),
		"ratio_2p": len(base) / n0,
		"fit": len(fit),
		"final": len(final),
		"ratio": len(final) / n if n else 0.0,
		"delta_ratio_vs_2p": (len(final) / n if n else 0.0) - (len(base) / n0),
		"H_nonprim": nonprimary_ge3_count(hyperbola_lifts(n, p, 1)),
	}


def primes_to(limit: int) -> List[int]:
	"""Odd primes ≤ limit."""
	out: List[int] = []
	p = 3
	while p <= limit:
		if is_prime(p):
			out.append(p)
		p = next_prime(p + 1)
	return out
