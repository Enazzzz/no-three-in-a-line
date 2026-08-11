"""Per-family solvers for volunteer workers."""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Sequence, Tuple

from ntil.algebraic import four_constraint_survivors, summarize_addability
from ntil.constructions import hjsw, is_prime
from ntil.verify import _orient, verify_claim

Point = Tuple[int, int]


def _shares_line_with_two(pt: Point, pts: Sequence[Point]) -> bool:
	"""True if pt is collinear with some existing pair."""
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			if _orient(pts[i], pts[j], pt) == 0:
				return True
	return False


def _greedy(n: int, base: List[Point], candidates: List[Point], time_limit_s: float, seed: int) -> List[Point]:
	"""Greedy augment with a wall-clock budget."""
	rng = random.Random(seed)
	pts = list(base)
	occ = set(pts)
	order = list(candidates)
	rng.shuffle(order)
	t0 = time.monotonic()
	for cand in order:
		if time.monotonic() - t0 > time_limit_s:
			break
		if cand in occ:
			continue
		if _shares_line_with_two(cand, pts):
			continue
		pts.append(cand)
		occ.add(cand)
	return pts


def solve_hjsw(params: Dict[str, Any]) -> Dict[str, Any]:
	"""Return classical HJSW S2."""
	p = int(params["p"])
	c = int(params.get("c", 1))
	t0 = time.monotonic()
	n, pts = hjsw(p, c)
	ok, reason = verify_claim(n, pts)
	return {
		"n": n,
		"points": pts,
		"size": len(pts),
		"ratio": len(pts) / n,
		"family": "hjsw",
		"params": params,
		"stats": {"runtime_s": time.monotonic() - t0, "verified_local": ok, "reason": reason},
	}


def solve_hjsw_augment(params: Dict[str, Any]) -> Dict[str, Any]:
	"""HJSW + greedy fill preferring four-constraint survivors."""
	p = int(params["p"])
	c = int(params.get("c", 1))
	seed = int(params.get("seed", 0))
	budget = float(params.get("time_limit_s", 20))
	t0 = time.monotonic()
	n, base = hjsw(p, c)
	surv = four_constraint_survivors(n, base)
	rest = [
		(x, y)
		for x in range(1, n + 1)
		for y in range(1, n + 1)
		if (x, y) not in set(base) and (x, y) not in set(surv)
	]
	pts = _greedy(n, list(base), surv + rest, budget, seed)
	ok, reason = verify_claim(n, pts)
	summary = summarize_addability(n, p, base)
	return {
		"n": n,
		"points": pts,
		"size": len(pts),
		"ratio": len(pts) / n,
		"family": "hjsw_augment",
		"params": params,
		"stats": {
			"runtime_s": time.monotonic() - t0,
			"verified_local": ok,
			"reason": reason,
			"base_size": len(base),
			"survivors": summary["four_constraint_survivors"],
		},
	}


def solve_algebraic_addable(params: Dict[str, Any]) -> Dict[str, Any]:
	"""Only attempt four-constraint survivors (stricter pool)."""
	p = int(params["p"])
	c = int(params.get("c", 1))
	seed = int(params.get("seed", 0))
	budget = float(params.get("time_limit_s", 20))
	t0 = time.monotonic()
	n, base = hjsw(p, c)
	surv = four_constraint_survivors(n, base)
	pts = _greedy(n, list(base), surv, budget, seed)
	ok, reason = verify_claim(n, pts)
	return {
		"n": n,
		"points": pts,
		"size": len(pts),
		"ratio": len(pts) / n,
		"family": "algebraic_addable",
		"params": params,
		"stats": {
			"runtime_s": time.monotonic() - t0,
			"verified_local": ok,
			"reason": reason,
			"pool": len(surv),
			"addability": summarize_addability(n, p, base),
		},
	}


def solve_hyperbola_union(params: Dict[str, Any]) -> Dict[str, Any]:
	"""Try a few c values; keep the densest verified HJSW+augment result."""
	p = int(params["p"])
	seed = int(params.get("seed", 0))
	budget = float(params.get("time_limit_s", 20))
	t0 = time.monotonic()
	best: Dict[str, Any] | None = None
	# Sample a few nonzero residues.
	cs = [1, 2, 3, (p - 1) // 2, p - 1]
	cs = [c for c in cs if c % p != 0]
	rng = random.Random(seed)
	rng.shuffle(cs)
	per = max(2.0, budget / max(1, len(cs)))
	for c in cs:
		sub = dict(params)
		sub["c"] = c
		sub["time_limit_s"] = per
		cand = solve_hjsw_augment(sub)
		if best is None or cand["size"] > best["size"]:
			best = cand
	assert best is not None
	best["family"] = "hyperbola_union"
	best["stats"]["runtime_s"] = time.monotonic() - t0
	best["stats"]["tried_c"] = cs
	return best


SOLVERS = {
	"hjsw": solve_hjsw,
	"hjsw_augment": solve_hjsw_augment,
	"algebraic_addable": solve_algebraic_addable,
	"hyperbola_union": solve_hyperbola_union,
}


def run_family(family: str, params: Dict[str, Any]) -> Dict[str, Any]:
	"""Dispatch to a named solver family."""
	if family not in SOLVERS:
		raise KeyError(f"unknown family {family}")
	if not is_prime(int(params["p"])) or int(params["p"]) == 2:
		raise ValueError("params.p must be an odd prime")
	return SOLVERS[family](params)
