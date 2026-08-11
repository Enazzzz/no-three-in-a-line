"""Machine-checkable lemmas for single-hyperbola non-primary cleanliness.

Theorem (see docs/PROOF_SINGLE_H.md): on the n=2p board, H(c) has no
non-primary line containing ≥3 points.

This module verifies the algebraic ingredients used in the proof:

1. F_p hyperbola meets any line in ≤2 points
2. Board collinearity ⇒ F_p-projection determinant Δ ≡ 0 (mod p)
3. Two distinct lifts of the same F_p point determine a primary direction
4. Exhaustive scan certificate for primes up to a limit
"""

from __future__ import annotations

from itertools import combinations
from math import gcd
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from research.allslope_hitting import is_primary_dir, line_key, lines_with_counts
from research.constructions import is_prime, next_prime
from research.hyperbola_union import hyperbola_points

Point = Tuple[int, int]
FpPoint = Tuple[int, int]


def fp_hyperbola_points(p: int, c: int) -> List[FpPoint]:
	"""Points of xy ≡ c over F_p^*."""
	c = c % p
	out: List[FpPoint] = []
	for r in range(1, p):
		# s = c * r^{-1}
		s = (c * pow(r, -1, p)) % p
		if s != 0:
			out.append((r, s))
	return out


def fp_line_hits_hyperbola(p: int, c: int, r1: int, s1: int, r2: int, s2: int) -> int:
	"""How many F_p hyperbola points lie on the line through (r1,s1),(r2,s2)."""
	if (r1, s1) == (r2, s2):
		raise ValueError("need two distinct points")
	dr, ds = (r2 - r1) % p, (s2 - s1) % p
	hits = 0
	for r, s in fp_hyperbola_points(p, c):
		# (r-r1, s-s1) parallel to (dr, ds) over F_p
		if (ds * ((r - r1) % p) - dr * ((s - s1) % p)) % p == 0:
			hits += 1
	return hits


def lemma_fp_at_most_two(p: int, c: int = 1) -> bool:
	"""Every line through two distinct F_p hyperbola points hits ≤2 of them.

	(Equivalent to: no 3 F_p points of xy=c are collinear.)
	"""
	pts = fp_hyperbola_points(p, c)
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			if fp_line_hits_hyperbola(p, c, *pts[i], *pts[j]) > 2:
				return False
	return True


def board_collinearity_delta(
	p: int,
	P: Sequence[Point],
) -> Tuple[int, int, int]:
	"""For three board points, return (Δ, K, M) in Δ + p K + p² M = LHS-RHS.

	Uses the lift decomposition x=r+a p, y=s+b p with a,b∈{0,1}, r,s∈{1..p-1}.
	"""
	if len(P) != 3:
		raise ValueError("need three points")
	decomp = []
	for x, y in P:
		r, s = x % p, y % p
		a, b = (x - r) // p, (y - s) // p
		decomp.append((r, s, a, b))
	(r1, s1, a1, b1), (r2, s2, a2, b2), (r3, s3, a3, b3) = decomp
	delta = (r2 - r1) * (s3 - s1) - (r3 - r1) * (s2 - s1)
	K = (
		(r2 - r1) * (b3 - b1)
		+ (a2 - a1) * (s3 - s1)
		- (r3 - r1) * (b2 - b1)
		- (a3 - a1) * (s2 - s1)
	)
	M = (a2 - a1) * (b3 - b1) - (a3 - a1) * (b2 - b1)
	return delta, K, M


def lemma_collinear_implies_delta_mod_p(p: int, c: int = 1) -> bool:
	"""Every collinear triple in H(c) has Δ ≡ 0 (mod p)."""
	n = 2 * p
	H = hyperbola_points(n, p, c)
	for (_dx, _dy, _b), pts in lines_with_counts(H).items():
		if len(pts) < 3:
			continue
		for triple in combinations(pts, 3):
			delta, K, M = board_collinearity_delta(p, triple)
			# Exact collinearity identity.
			if delta + p * K + p * p * M != 0:
				return False
			if delta % p != 0:
				return False
	return True


def lift_direction_primary(p: int, x1: int, y1: int, x2: int, y2: int) -> bool:
	"""True if two distinct lifts of the same F_p point have primary chord."""
	if (x1 % p, y1 % p) != (x2 % p, y2 % p):
		raise ValueError("residues must match")
	dx, dy = x2 - x1, y2 - y1
	# Must be multiple of p in each nonzero coordinate.
	if dx % p != 0 or dy % p != 0:
		return False
	dx //= p
	dy //= p
	return is_primary_dir(dx, dy)


def lemma_same_residue_chord_primary(p: int, c: int = 1) -> bool:
	"""Any two distinct board lifts of one F_p hyperbola point form a primary chord."""
	n = 2 * p
	H = hyperbola_points(n, p, c)
	by_res: Dict[FpPoint, List[Point]] = {}
	for x, y in H:
		by_res.setdefault((x % p, y % p), []).append((x, y))
	for lifts in by_res.values():
		for i in range(len(lifts)):
			for j in range(i + 1, len(lifts)):
				if not lift_direction_primary(p, *lifts[i], *lifts[j]):
					return False
	return True


def classify_collinear_triples(p: int, c: int = 1) -> Dict[str, int]:
	"""Count collinear H-triples by residue pattern and primary/non-primary."""
	n = 2 * p
	H = hyperbola_points(n, p, c)
	counts: Dict[str, int] = {
		"primary_same_res": 0,
		"primary_two_res": 0,
		"primary_three_res": 0,
		"nonprimary_same_res": 0,
		"nonprimary_two_res": 0,
		"nonprimary_three_res": 0,
	}
	seen_lines = set()
	for key, pts in lines_with_counts(H).items():
		if len(pts) < 3:
			continue
		dx, dy, _b = key
		prim = is_primary_dir(dx, dy)
		for triple in combinations(pts, 3):
			res = [(x % p, y % p) for x, y in triple]
			nuniq = len(set(res))
			if prim:
				if nuniq == 1:
					counts["primary_same_res"] += 1
				elif nuniq == 2:
					counts["primary_two_res"] += 1
				else:
					counts["primary_three_res"] += 1
			else:
				if nuniq == 1:
					counts["nonprimary_same_res"] += 1
				elif nuniq == 2:
					counts["nonprimary_two_res"] += 1
				else:
					counts["nonprimary_three_res"] += 1
		seen_lines.add(key)
	counts["lines_ge3"] = len(seen_lines)
	return counts


def verify_proof_ingredients(p: int, c: int = 1) -> dict:
	"""Run all local lemmas for one prime; return a status dict."""
	n = 2 * p
	H = hyperbola_points(n, p, c)
	nonprim = sum(
		1
		for (dx, dy, _b), pts in lines_with_counts(H).items()
		if len(pts) >= 3 and not is_primary_dir(dx, dy)
	)
	return {
		"p": p,
		"c": c % p,
		"fp_at_most_two": lemma_fp_at_most_two(p, c),
		"collinear_delta_mod_p": lemma_collinear_implies_delta_mod_p(p, c),
		"same_residue_chord_primary": lemma_same_residue_chord_primary(p, c),
		"nonprimary_ge3": nonprim,
		"triple_classes": classify_collinear_triples(p, c),
		"ok": nonprim == 0
		and lemma_fp_at_most_two(p, c)
		and lemma_collinear_implies_delta_mod_p(p, c)
		and lemma_same_residue_chord_primary(p, c),
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
