"""Non-hyperbola second families vs HJSW: risk0 density and enrich trials.

Motivation (`FINDINGS_SLOPE_CENSUS.md`): second modular hyperbolas have almost
no risk-0 cells against full H(c0) / only O(1)–O(10) against HJSW. This module
asks whether a *different* algebraic (or exhaustive) second pool is sparser
in mixed triples.

Families:
  - modular parabola / circle / Pell / exponential / affine line (with F_p lifts)
  - full-board risk0 ceiling (upper bound over *any* second family)
  - optional delete-k from HJSW to unlock more risk0 cells

None of these are claimed to beat HJSW asymptotically; they are dead-end probes.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

from research.algebraic import saturated_differences, unsaturated_hv_candidates
from research.allslope_hitting import is_primary_dir, line_key, lines_with_counts
from research.constructions import ambient_grid, hjsw, is_prime, middle_blocks
from research.hyperbola_union import hyperbola_points
from research.search import greedy_augment
from research.subset import build_slope_tables, individually_addable, _norm_slope
from research.verify import verify_claim

Point = Tuple[int, int]
FamilyFn = Callable[[int, int], List[Point]]


def lift_fp_pairs(n: int, p: int, pairs: Sequence[Point]) -> List[Point]:
	"""Lift F_p^* × F_p^* pairs to the n=2p board via +kp translates."""
	pts: List[Point] = []
	seen: Set[Point] = set()
	for x0, y0 in pairs:
		x0, y0 = x0 % p, y0 % p
		if x0 == 0 or y0 == 0:
			continue
		for i in range((n - x0) // p + 1):
			x = x0 + i * p
			if not (1 <= x <= n):
				continue
			for j in range((n - y0) // p + 1):
				y = y0 + j * p
				if 1 <= y <= n and (x, y) not in seen:
					seen.add((x, y))
					pts.append((x, y))
	return pts


def family_hyperbola(n: int, p: int, c: int = 2) -> List[Point]:
	"""Control: second modular hyperbola H(c)."""
	return hyperbola_points(n, p, c % p)


def family_parabola(n: int, p: int) -> List[Point]:
	"""Erdős-style modular parabola y ≡ x² (mod p), lifted to the board."""
	pairs = [(x, (x * x) % p) for x in range(1, p) if (x * x) % p != 0]
	return lift_fp_pairs(n, p, pairs)


def family_circle(n: int, p: int, c: int = 1) -> List[Point]:
	"""Modular circle x² + y² ≡ c (mod p)."""
	c = c % p
	pairs = [
		(x, y)
		for x in range(1, p)
		for y in range(1, p)
		if (x * x + y * y) % p == c
	]
	return lift_fp_pairs(n, p, pairs)


def family_pell(n: int, p: int, d: int = 2, c: int = 1) -> List[Point]:
	"""Pell-like x² − d y² ≡ c (mod p)."""
	d, c = d % p, c % p
	pairs = [
		(x, y)
		for x in range(1, p)
		for y in range(1, p)
		if (x * x - d * y * y) % p == c
	]
	return lift_fp_pairs(n, p, pairs)


def _primitive_root(p: int) -> int:
	"""Smallest primitive root mod p (p prime)."""
	for g in range(2, p):
		ok = True
		# Factor p-1 lightly via trial.
		m = p - 1
		# Check g^{(p-1)/q} ≠ 1 for prime factors q of p-1.
		factors: List[int] = []
		tmp = m
		d = 2
		while d * d <= tmp:
			if tmp % d == 0:
				factors.append(d)
				while tmp % d == 0:
					tmp //= d
			d += 1 if d == 2 else 2
		if tmp > 1:
			factors.append(tmp)
		for q in factors:
			if pow(g, m // q, p) == 1:
				ok = False
				break
		if ok:
			return g
	return 2


def family_exponential(n: int, p: int, g: Optional[int] = None) -> List[Point]:
	"""Exponential curve (x, g^x mod p) for a primitive root g."""
	if g is None:
		g = _primitive_root(p)
	pairs = [(x, pow(g, x, p)) for x in range(1, p) if pow(g, x, p) != 0]
	return lift_fp_pairs(n, p, pairs)


def family_affine_line(n: int, p: int, a: int = 2, b: int = 1) -> List[Point]:
	"""Affine line y ≡ a x + b (mod p) — expected to be self-collinear-heavy."""
	a, b = a % p, b % p
	pairs = [(x, (a * x + b) % p) for x in range(1, p) if (a * x + b) % p != 0]
	return lift_fp_pairs(n, p, pairs)


def middle_block_cells(p: int) -> List[Point]:
	"""Board coordinates of HJSW middle blocks M (same shift as hjsw())."""
	xmin, _xmax, ymin, _ymax = ambient_grid(p)
	n = 2 * p
	sx, sy = 1 - xmin, 1 - ymin
	pts: List[Point] = []
	for x, y in middle_blocks(p):
		xx, yy = x + sx, y + sy
		if 1 <= xx <= n and 1 <= yy <= n:
			pts.append((xx, yy))
	return pts


def self_nonprimary_triple_count(pool: Sequence[Point]) -> int:
	"""Count non-primary lines with ≥3 points inside `pool` alone."""
	n = 0
	for (dx, dy, _b), pts in lines_with_counts(pool).items():
		if len(pts) >= 3 and not is_primary_dir(dx, dy):
			n += 1
	return n


def forbidden_cells_nonprimary(base: Sequence[Point], n: int) -> Set[Point]:
	"""Board cells that lie on a non-primary line already determined by ≥2 base points.

	Any extra point in this set has risk ≥1 against `base`. Complements are risk0.
	"""
	pts = [tuple(p) for p in base]  # type: ignore[misc]
	forbidden: Set[Point] = set()
	m = len(pts)
	seen_lines: Set[Tuple[int, int, int]] = set()
	for i in range(m):
		for j in range(i + 1, m):
			key = line_key(pts[i], pts[j])
			dx, dy, inter = key
			if is_primary_dir(dx, dy):
				continue
			if key in seen_lines:
				continue
			seen_lines.add(key)
			# Enumerate integer board points on the line dy*x - dx*y = inter.
			if dx == 0:
				# Vertical — primary; skipped above.
				continue
			for x in range(1, n + 1):
				num = dy * x - inter
				if num % dx != 0:
					continue
				y = num // dx
				if 1 <= y <= n:
					forbidden.add((x, y))
	return forbidden


def risk0_against(base: Sequence[Point], pool: Sequence[Point], n: Optional[int] = None) -> List[Point]:
	"""Points of `pool` that create no new non-primary ≥3-line with `base`.

	Uses a line-forbidden mask (fast) when `n` is known; otherwise falls back
	to per-point collinearity checks.
	"""
	base_t = [tuple(p) for p in base]  # type: ignore[misc]
	bset = set(base_t)
	if n is None:
		# Infer a loose board size from coordinates.
		n = max((max(p) for p in base_t), default=1)
		for q in pool:
			n = max(n, q[0], q[1])

	forbidden = forbidden_cells_nonprimary(base_t, n)
	safe: List[Point] = []
	for q in pool:
		qt = tuple(q)  # type: ignore[misc]
		if qt in bset:
			continue
		if qt not in forbidden:
			safe.append(qt)
	return safe


def primary_ok_against(n: int, base: Sequence[Point], cands: Sequence[Point]) -> List[Point]:
	"""Filter candidates that respect unsaturated row/col/±1 vs `base`."""
	base_t = [tuple(p) for p in base]  # type: ignore[misc]
	sat_plus, sat_minus = saturated_differences(base_t)
	out: List[Point] = []
	for q in cands:
		if not unsaturated_hv_candidates(n, base_t, [q]):
			continue
		x, y = q
		if (x - y) in sat_plus or (x + y) in sat_minus:
			continue
		out.append(q)
	return out


def enrich_from_pool(
	n: int,
	seed: Sequence[Point],
	extras: Sequence[Point],
	*,
	polish_s: float = 1.0,
	rng_seed: int = 0,
) -> Tuple[List[Point], dict]:
	"""Greedily add extras preserving primary + all-slope, then polish."""
	pts: List[Point] = [tuple(p) for p in seed]  # type: ignore[misc]
	tables = build_slope_tables(pts)
	order = list(extras)
	rng = random.Random(rng_seed)
	rng.shuffle(order)
	added: List[Point] = []
	for cand in order:
		if not unsaturated_hv_candidates(n, pts, [cand]):
			continue
		sat_plus, sat_minus = saturated_differences(pts)
		x, y = cand
		if (x - y) in sat_plus or (x + y) in sat_minus:
			continue
		if not individually_addable(cand, pts, tables):
			continue
		tables[cand] = set()
		for q in pts:
			s = _norm_slope(x - q[0], y - q[1])
			tables[q].add(s)
			tables[cand].add(s)
		pts.append(cand)
		added.append(cand)

	polished = greedy_augment(n, pts, time_limit_s=polish_s, seed=rng_seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else pts
	ok2, reason2 = verify_claim(n, final)
	stats = {
		"extras_in": len(extras),
		"extras_added": len(added),
		"final_size": len(final),
		"verified": ok2,
		"reason": reason2,
	}
	return final, stats


FAMILY_BUILDERS: Dict[str, FamilyFn] = {
	"hyperbola_c2": lambda n, p: family_hyperbola(n, p, 2),
	"parabola": family_parabola,
	"circle": lambda n, p: family_circle(n, p, 1),
	"pell_d2": lambda n, p: family_pell(n, p, 2, 1),
	"exponential": family_exponential,
	"affine_line": family_affine_line,
}


def evaluate_family(
	p: int,
	name: str,
	pool: Sequence[Point],
	*,
	polish_s: float = 0.8,
	seed: int = 0,
) -> dict:
	"""Risk0 / primary-ok / enrich metrics for one pool against HJSW."""
	if not is_prime(p) or p == 2:
		raise ValueError("odd prime required")
	n, hjsw_pts = hjsw(p, 1)
	safe = risk0_against(hjsw_pts, pool, n)
	prim = primary_ok_against(n, hjsw_pts, safe)
	# Fair baseline: polish HJSW alone.
	base_final, base_st = enrich_from_pool(n, hjsw_pts, [], polish_s=polish_s, rng_seed=seed)
	final, st = enrich_from_pool(n, hjsw_pts, safe, polish_s=polish_s, rng_seed=seed + 1)
	# Self-collinearity census is only meaningful for structured thin pools.
	self_np = self_nonprimary_triple_count(pool) if len(pool) <= 250 else -1
	return {
		"p": p,
		"n": n,
		"family": name,
		"hjsw": len(hjsw_pts),
		"pool": len(pool),
		"self_nonprim3": self_np,
		"risk0": len(safe),
		"risk0_primary_ok": len(prim),
		"hjsw_polished": base_st["final_size"],
		"enrich_added": st["extras_added"],
		"enrich_final": st["final_size"],
		"delta_vs_hjsw": st["final_size"] - len(hjsw_pts),
		"delta_vs_polished": st["final_size"] - base_st["final_size"],
		"verified": st["verified"],
	}


def evaluate_board_ceiling(p: int, *, polish_s: float = 0.8, seed: int = 0) -> dict:
	"""Upper bound: every board cell that is risk0 vs HJSW."""
	n, hjsw_pts = hjsw(p, 1)
	board = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
	return evaluate_family(p, "board_risk0_ceiling", board, polish_s=polish_s, seed=seed)


def evaluate_delete_k(
	p: int,
	k: int,
	*,
	polish_s: float = 0.8,
	seed: int = 0,
	sample_for_rank: int = 400,
) -> dict:
	"""Delete k HJSW points that most unlock risk0 (heuristic), then enrich.

	Ranking uses a board sample for speed when n is large; the final risk0
	pass still uses the full board.
	"""
	n, hjsw_pts = hjsw(p, 1)
	seed_list = [tuple(pt) for pt in hjsw_pts]  # type: ignore[misc]
	board = [(x, y) for x in range(1, n + 1) for y in range(1, n + 1)]
	rng = random.Random(seed)
	rank_pool = board if n * n <= 1600 else rng.sample(board, min(sample_for_rank, len(board)))

	gains: List[Tuple[int, Point]] = []
	for v in seed_list:
		reduced = [pt for pt in seed_list if pt != v]
		gains.append((len(risk0_against(reduced, rank_pool, n)), v))
	gains.sort(reverse=True)
	victims = {v for _, v in gains[:k]}
	reduced = [pt for pt in seed_list if pt not in victims]
	safe = risk0_against(reduced, board, n)

	base_final, base_st = enrich_from_pool(n, hjsw_pts, [], polish_s=polish_s, rng_seed=seed)
	final, st = enrich_from_pool(n, reduced, safe, polish_s=polish_s, rng_seed=seed + k)
	return {
		"p": p,
		"n": n,
		"family": f"delete_{k}_then_board_risk0",
		"hjsw": len(hjsw_pts),
		"reduced_seed": len(reduced),
		"risk0": len(safe),
		"hjsw_polished": base_st["final_size"],
		"enrich_added": st["extras_added"],
		"enrich_final": st["final_size"],
		"delta_vs_hjsw": st["final_size"] - len(hjsw_pts),
		"delta_vs_polished": st["final_size"] - base_st["final_size"],
		"verified": st["verified"],
	}


def scan_all_families(p: int, *, polish_s: float = 0.8, seed: int = 0) -> List[dict]:
	"""Evaluate built-in algebraic families + middle-block + board ceiling."""
	n = 2 * p
	rows: List[dict] = []
	for name, builder in FAMILY_BUILDERS.items():
		pool = builder(n, p)
		rows.append(evaluate_family(p, name, pool, polish_s=polish_s, seed=seed))
	rows.append(
		evaluate_family(p, "middle_blocks", middle_block_cells(p), polish_s=polish_s, seed=seed)
	)
	# Board ceiling is O(n² · |HJSW|²); keep for moderate p.
	if p <= 31:
		rows.append(evaluate_board_ceiling(p, polish_s=polish_s, seed=seed))
	# Delete-k unlock is slower still — small primes only.
	for k in (1, 3):
		if p <= 23:
			rows.append(evaluate_delete_k(p, k, polish_s=polish_s, seed=seed))
	return rows
