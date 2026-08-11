"""Best-effort no-three-in-line solver aiming for denser-than-1.55n configs.

Asymptotically beating 3/2 remains open; this module returns the best
construction it can find quickly for some n in [min_n, 2*min_n].
"""

from __future__ import annotations

from typing import List, Tuple

from research.constructions import hjsw, is_prime, next_prime
from research.hyperbola_union import try_hyperbola_unions
from research.search import greedy_augment
from research.subset import max_safe_augmentation
from research.verify import verify_claim

Point = Tuple[int, int]

# Strictly increasing n across calls (process-local).
_LAST_N = 0

# Primes where prior HJSW+greedy / subset scans beat 1.55n (partial list).
_WINNING_PRIMES = [
	5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97, 107, 109, 139, 151, 167, 173, 181, 281,
]


def _ratio(n: int, pts: List[Point]) -> float:
	"""Return |pts|/n."""
	return len(pts) / n if n else 0.0


def _candidates_for_min_n(min_n: int) -> List[int]:
	"""Odd primes p with n=2p in [min_n, 2*min_n] and n > _LAST_N."""
	lo = max(min_n, _LAST_N + 1)
	hi = 2 * min_n
	primes: List[int] = []
	# Prefer known winners inside the window.
	for p in _WINNING_PRIMES:
		n = 2 * p
		if lo <= n <= hi:
			primes.append(p)
	# Fill with other primes in range.
	p = next_prime(max(3, (lo + 1) // 2))
	while 2 * p <= hi:
		if 2 * p >= lo and p not in primes and is_prime(p):
			primes.append(p)
		p = next_prime(p + 1)
	return primes


def _augment(n: int, base: List[Point], p: int) -> List[Point]:
	"""Combine algebraic safe-subset / hyperbola-union with a short greedy polish.

	Subset search is cheap once individually-ok pools are filtered (~O(10–50)
	vertices). For moderate primes, also try a ±1-filtered second hyperbola.
	"""
	candidates: List[List[Point]] = []

	exact_limit = 24 if p <= 120 else 18
	subset_pts, _stats = max_safe_augmentation(n, base, exact_limit=exact_limit)
	candidates.append(subset_pts)

	# Hyperbola-union is cheap for p≲120; skip on huge boards in this VM budget.
	if p <= 120:
		_n2, union_pts, _ust = try_hyperbola_unions(p, time_limit_s=min(6.0, 0.04 * p + 1.0))
		candidates.append(union_pts)

	best = max(candidates, key=len)
	budget = min(6.0, 0.015 * p + 1.0)
	polished = greedy_augment(
		n,
		best,
		time_limit_s=budget,
		seed=p,
		prefer_four_constraint=True,
	)
	ok, _ = verify_claim(n, polished)
	if ok and len(polished) >= len(best):
		return polished
	ok2, _ = verify_claim(n, best)
	return best if ok2 else list(base)


def solution(min_n: int) -> Tuple[int, List[Point]]:
	"""Return (n, points) with no three collinear and n in [min_n, 2*min_n].

	Tries HJSW + algebraic subset + short greedy for admissible primes.
	Updates _LAST_N so subsequent calls use strictly larger n.
	"""
	global _LAST_N
	if min_n < 1:
		raise ValueError("min_n must be positive")

	best_n = None
	best_pts: List[Point] = []
	best_ratio = -1.0

	# Bound how many primes we try so large min_n cannot blow the 60s budget.
	cands = _candidates_for_min_n(min_n)
	# Prefer smaller boards first (faster verify / subset).
	cands = sorted(cands)[:8]

	for p in cands:
		n, base = hjsw(p)
		ok, _ = verify_claim(n, base)
		if not ok:
			continue
		pts = _augment(n, list(base), p)
		r = _ratio(n, pts)
		score = (1 if r > 1.55 else 0, r, len(pts))
		best_score = (1 if best_ratio > 1.55 else 0, best_ratio, len(best_pts))
		if best_n is None or score > best_score:
			best_n, best_pts, best_ratio = n, pts, r

	if best_n is None:
		# Fallback: smallest HJSW above last n.
		p = next_prime(max(3, (_LAST_N // 2) + 1))
		while 2 * p < min_n:
			p = next_prime(p + 1)
		if 2 * p > 2 * min_n:
			p = next_prime(max(3, (min_n + 1) // 2))
		best_n, best_pts = hjsw(p)

	_LAST_N = best_n
	return best_n, best_pts


if __name__ == "__main__":
	# Smoke demo only — not part of the judged interface.
	for m in (5, 10, 20):
		n, pts = solution(m)
		ok, reason = verify_claim(n, pts)
		print(m, n, len(pts), f"{len(pts)/n:.4f}", ok, reason)
