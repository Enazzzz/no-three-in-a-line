"""B2 provenance: what single-H structure actually implies for mono size.

Conclusions (see docs/PROOF_LB_SURPLUS.md):

* Board ``H(c)`` on ``n=2p`` has ≤2 points per row and per column already,
  so primary-feasibility reduces to the ±1 diagonal caps.
* That is a corollary of two-lift geometry, not of the ~0.7-vs-HJSW fit.
* Algorithmic mono primary size equals ``2(p+1)`` when ``p≡1 (mod 4)`` and
  ``2p`` when ``p≡3 (mod 4)`` on all odd primes checked through 61 — still
  a conjecture, and even the uniform ``M ≤ 2(p+1)`` bound does **not** imply
  lemma B2 on the board multi-H certificates.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional, Tuple

from research.constructions import hjsw, is_prime
from research.hyperbola_union import hyperbola_points
from research.primary_repair import exact_primary_max, greedy_primary_max
from research.verify import verify_claim

Point = Tuple[int, int]


def board_hyperbola_row_col_max(p: int, c: int = 1) -> Tuple[int, int, int]:
	"""Return ``(max_row_occ, max_col_occ, |H(c)|)`` on the ``n=2p`` board."""
	H = hyperbola_points(2 * p, p, c)
	rows = Counter(y for _, y in H)
	cols = Counter(x for x, _ in H)
	return max(rows.values()), max(cols.values()), len(H)


def row_col_automatic(p: int, c: int = 1) -> bool:
	"""True if every row/col meets ``H(c)`` in at most 2 points."""
	mr, mc, _ = board_hyperbola_row_col_max(p, c)
	return mr <= 2 and mc <= 2


def conjectured_mono_primary_cap(p: int) -> int:
	"""Conjectural max primary size in board ``H(c)``: ``2p`` or ``2(p+1)``.

	Pattern from exact BnB through ``p≤61``: ``2(p+1)`` if ``p≡1 (mod 4)``,
	else ``2p`` if ``p≡3 (mod 4)``. Not derived from ``PROOF_SINGLE_H``;
	single-H only gives NTIL⇔primary once row/col are automatic.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	if p % 4 == 1:
		return 2 * (p + 1)
	if p % 4 == 3:
		return 2 * p
	raise ValueError("odd prime must be 1 or 3 mod 4")


def mono_primary_size(
	p: int,
	c: int = 1,
	*,
	bnb_s: float = 3.0,
	seed: int = 0,
) -> dict:
	"""Algorithmic max primary packing in board ``H(c)`` vs structural scales."""
	n = 2 * p
	pool = hyperbola_points(n, p, c)
	_, hj = hjsw(p, 1)
	g = greedy_primary_max(pool, seed=seed)
	ex, _ = exact_primary_max(pool, time_limit_s=bnb_s, seed=seed)
	best = max(g, ex, key=len)
	ok, _ = verify_claim(n, best)
	cap = conjectured_mono_primary_cap(p)
	mr, mc, _ = board_hyperbola_row_col_max(p, c)
	return {
		"p": p,
		"c": c % p,
		"pool": len(pool),
		"max_row_in_H": mr,
		"max_col_in_H": mc,
		"row_col_automatic": int(mr <= 2 and mc <= 2),
		"hjsw": len(hj),
		"best": len(best),
		"conjectured_cap": cap,
		"hits_cap": int(len(best) == cap),
		"best_over_hjsw": f"{len(best) / len(hj):.4f}",
		"best_over_3p": f"{len(best) / (3 * (p - 1)):.4f}",
		"asymp_2p_over_3p": f"{(2 * p) / (3 * (p - 1)):.4f}",
		"verified_ntil": int(ok),
	}


def b2_from_mono_cap_alone(
	majority: int,
	minority: int,
	p: int,
	*,
	mono_cap: Optional[int] = None,
) -> dict:
	"""Check whether ``M ≤ mono_cap`` is enough to force B2 arithmetically.

	B2 needs ``⌊m/3⌋ ≥ M + m − 3(p−1)``. Substituting the worst-case
	``M = mono_cap`` yields a sufficient condition that typically **fails**
	when ``m`` is large — so a mono-color cap does not prove B2.
	"""
	cap = mono_cap if mono_cap is not None else conjectured_mono_primary_cap(p)
	m = minority
	m3 = m // 3
	# Worst surplus under M ≤ cap (using actual m).
	sur_worst = cap + m - 3 * (p - 1)
	actual_sur_if_M = majority + m - 3 * (p - 1)
	return {
		"mono_cap": cap,
		"floor_m_over_3": m3,
		"surplus_if_M_at_cap": sur_worst,
		"b2_forced_by_cap": int(m3 >= sur_worst),
		"surplus_with_actual_M": actual_sur_if_M,
		"b2_with_actual_M": int(m3 >= actual_sur_if_M),
	}
