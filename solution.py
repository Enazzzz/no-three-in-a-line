"""Best-effort no-three-in-line solver aiming for denser-than-1.55n configs.

Asymptotically beating 3/2 remains open; this module returns the best
construction it can find quickly for some n in [min_n, 2*min_n].
"""

from __future__ import annotations

from typing import List, Tuple

from research.constructions import hjsw, is_prime, next_prime
from research.search import greedy_augment
from research.verify import verify_claim

Point = Tuple[int, int]

# Strictly increasing n across calls (process-local).
_LAST_N = 0

# Primes where prior HJSW+greedy scans beat 1.55n (partial list).
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


def solution(min_n: int) -> Tuple[int, List[Point]]:
	"""Return (n, points) with no three collinear and n in [min_n, 2*min_n].

	Tries HJSW and HJSW+greedy for admissible primes. Updates _LAST_N so
	subsequent calls use strictly larger n.
	"""
	global _LAST_N
	if min_n < 1:
		raise ValueError("min_n must be positive")

	best_n = None
	best_pts: List[Point] = []
	best_ratio = -1.0

	for p in _candidates_for_min_n(min_n):
		n, base = hjsw(p)
		ok, _ = verify_claim(n, base)
		if not ok:
			continue
		# Time budget scales mildly with p but stays under ~1 minute total.
		budget = min(20.0, 0.05 * p + 2.0)
		aug = greedy_augment(n, base, time_limit_s=budget, seed=p, prefer_four_constraint=True)
		ok2, _ = verify_claim(n, aug)
		pts = aug if ok2 else base
		r = _ratio(n, pts)
		# Prefer ratio > 1.55 when possible; otherwise best ratio then size.
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
