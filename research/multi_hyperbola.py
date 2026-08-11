"""Simultaneous / delete-first multi-hyperbola constructions.

Unlike HJSW-seeded grafting, these methods build a point set from a raw
union of several modular hyperbolas (optionally masked to T2), then either:

* **greedy-keep** — walk the pool once, keeping a point only if it preserves
  no-three-in-line (and optionally ≤2 on horiz/vert/±1);
* **delete-first** — while some horiz/vert/±1 class has ≥3 points, delete a
  point from a worst class; then greedy-keep the remainder for other slopes.

This is the constructive step recommended in docs/FINDINGS.md.
VM-scoped: small residue sets (|C|≤3) and primes up to a few hundred.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from research.constructions import ambient_grid, hjsw, is_prime, t2_blocks
from research.hyperbola_union import hyperbola_points
from research.search import greedy_augment
from research.subset import _norm_slope, build_slope_tables, individually_addable
from research.verify import verify_claim

Point = Tuple[int, int]


def translated_t2(p: int) -> Set[Point]:
	"""T2 half-blocks mapped into the same [1, 2p]² board as hjsw()."""
	xmin, _, ymin, _ = ambient_grid(p)
	shift_x = 1 - xmin
	shift_y = 1 - ymin
	n = 2 * p
	out: Set[Point] = set()
	for x, y in t2_blocks(p):
		bx, by = x + shift_x, y + shift_y
		if 1 <= bx <= n and 1 <= by <= n:
			out.add((bx, by))
	return out


def multi_hyperbola_pool(
	p: int,
	residues: Sequence[int],
	*,
	mask_t2: bool = True,
) -> Tuple[int, List[Point]]:
	"""Raw union ⋃_c H(c) on the n=2p board, optionally ∩ translated T2."""
	if not is_prime(p) or p == 2:
		raise ValueError("p must be an odd prime")
	n = 2 * p
	pool: Set[Point] = set()
	for c in residues:
		c = c % p
		if c == 0:
			continue
		pool |= set(hyperbola_points(n, p, c))
	if mask_t2:
		pool &= translated_t2(p)
	return n, sorted(pool)


def _class_counts(points: Sequence[Point]) -> Dict[str, Counter]:
	"""Occupancy counters for rows, cols, slope±1 diagonals."""
	return {
		"row": Counter(y for _, y in points),
		"col": Counter(x for x, _ in points),
		"plus": Counter(x - y for x, y in points),
		"minus": Counter(x + y for x, y in points),
	}


def _violations(pt: Point, counts: Dict[str, Counter], threshold: int = 3) -> int:
	"""How many primary classes would be at/over threshold if pt is present."""
	x, y = pt
	v = 0
	if counts["row"][y] >= threshold:
		v += 1
	if counts["col"][x] >= threshold:
		v += 1
	if counts["plus"][x - y] >= threshold:
		v += 1
	if counts["minus"][x + y] >= threshold:
		v += 1
	return v


def delete_first_primary(
	points: Sequence[Point],
	*,
	threshold: int = 3,
	seed: int = 0,
) -> List[Point]:
	"""Delete until every row/col/±1 class has < threshold points."""
	rng = random.Random(seed)
	pts: List[Point] = [tuple(p) for p in points]  # type: ignore[misc]
	rng.shuffle(pts)
	counts = _class_counts(pts)

	def worst_classes() -> List[Tuple[str, int]]:
		bad: List[Tuple[str, int]] = []
		for name, ctr in counts.items():
			for key, c in ctr.items():
				if c >= threshold:
					bad.append((name, key))
		return bad

	guard = 0
	max_steps = len(pts) + 5
	while worst_classes() and guard < max_steps:
		guard += 1
		# Delete the point that sits in the most currently-bad classes.
		scored = []
		for i, pt in enumerate(pts):
			scored.append((_violations(pt, counts, threshold), rng.random(), i))
		scored.sort(reverse=True)
		# Only delete if it actually participates in a violation.
		idx = None
		for score, _r, i in scored:
			if score > 0:
				idx = i
				break
		if idx is None:
			break
		x, y = pts.pop(idx)
		counts["row"][y] -= 1
		counts["col"][x] -= 1
		counts["plus"][x - y] -= 1
		counts["minus"][x + y] -= 1
	return pts


def greedy_keep(
	n: int,
	pool: Sequence[Point],
	*,
	seed: int = 0,
	enforce_primary: bool = True,
) -> List[Point]:
	"""Keep points from pool that preserve no-three-in-line (slope tables)."""
	rng = random.Random(seed)
	order = list(pool)
	rng.shuffle(order)
	kept: List[Point] = []
	tables: Dict[Point, Set[Tuple[int, int]]] = {}
	counts = _class_counts([])

	for cand in order:
		x, y = cand
		if enforce_primary:
			if counts["row"][y] >= 2 or counts["col"][x] >= 2:
				continue
			if counts["plus"][x - y] >= 2 or counts["minus"][x + y] >= 2:
				continue
		if kept and not individually_addable(cand, kept, tables):
			continue
		# Accept.
		tables[cand] = set()
		for q in kept:
			s = _norm_slope(x - q[0], y - q[1])
			tables[q].add(s)
			tables[cand].add(s)
		kept.append(cand)
		counts["row"][y] += 1
		counts["col"][x] += 1
		counts["plus"][x - y] += 1
		counts["minus"][x + y] += 1
	# Bounds check (pool should already be in-board).
	kept = [(x, y) for x, y in kept if 1 <= x <= n and 1 <= y <= n]
	return kept


def build_multi_hyperbola(
	p: int,
	residues: Sequence[int],
	*,
	mode: str = "delete_first",
	mask_t2: bool = True,
	polish_s: float = 2.0,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""Construct a verified set from a multi-hyperbola pool.

	Modes:
	  - greedy_keep: simultaneous selection from the raw union
	  - delete_first: primary-class deletion, then greedy_keep, then polish
	"""
	n, pool = multi_hyperbola_pool(p, residues, mask_t2=mask_t2)
	stats: dict = {
		"family": f"multi_hyperbola_{mode}",
		"residues": list(residues),
		"mask_t2": mask_t2,
		"pool": len(pool),
		"mode": mode,
	}

	if mode == "greedy_keep":
		kept = greedy_keep(n, pool, seed=seed, enforce_primary=True)
	elif mode == "delete_first":
		thinned = delete_first_primary(pool, threshold=3, seed=seed)
		stats["after_primary_delete"] = len(thinned)
		kept = greedy_keep(n, thinned, seed=seed + 1, enforce_primary=True)
	else:
		raise ValueError(f"unknown mode {mode}")

	stats["pre_polish"] = len(kept)
	polished = greedy_augment(n, kept, time_limit_s=polish_s, seed=seed)
	ok, reason = verify_claim(n, polished)
	final = polished if ok else kept
	ok2, reason2 = verify_claim(n, final)
	# Fallback: never return invalid; prefer raw HJSW if everything fails.
	if not ok2:
		n2, base = hjsw(p, residues[0] if residues else 1)
		final = base
		n = n2
		ok2, reason2 = verify_claim(n, final)
		stats["fell_back_hjsw"] = True

	stats.update(
		{
			"size": len(final),
			"ratio": len(final) / n if n else 0.0,
			"verified": ok2,
			"reason": reason2,
		}
	)
	return n, final, stats


def default_residue_sets(p: int) -> List[List[int]]:
	"""Small residue tuples to try (VM budget)."""
	sets = [
		[1],
		[1, 2],
		[1, 3],
		[1, 2, 3],
		[1, 2, p - 1],
		[2, 3, 5] if p > 5 else [1, 2],
	]
	# Deduplicate / scrub zeros.
	out: List[List[int]] = []
	seen = set()
	for s in sets:
		t = tuple(sorted({c % p for c in s if c % p != 0}))
		if not t or t in seen:
			continue
		seen.add(t)
		out.append(list(t))
	return out


def best_multi_hyperbola(
	p: int,
	*,
	polish_s: float = 2.0,
	seed: int = 0,
) -> Tuple[int, List[Point], dict]:
	"""Try a few residue sets × modes; return densest verified config."""
	best_n, best_pts = hjsw(p)
	best_st = {
		"family": "hjsw_fallback",
		"size": len(best_pts),
		"ratio": len(best_pts) / best_n,
		"verified": True,
	}
	for residues in default_residue_sets(p):
		for mode in ("delete_first", "greedy_keep"):
			for mask in (True, False):
				n, pts, st = build_multi_hyperbola(
					p,
					residues,
					mode=mode,
					mask_t2=mask,
					polish_s=max(0.5, polish_s / 4.0),
					seed=seed,
				)
				if st.get("verified") and len(pts) > len(best_pts):
					best_n, best_pts, best_st = n, pts, st
	best_st["ratio"] = len(best_pts) / best_n
	best_st["size"] = len(best_pts)
	return best_n, best_pts, best_st
