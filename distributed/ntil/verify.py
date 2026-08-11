"""Collinearity verification — workers are never trusted."""

from __future__ import annotations

import hashlib
import json
from typing import List, Sequence, Tuple

Point = Tuple[int, int]


def _orient(a: Point, b: Point, c: Point) -> int:
	"""Cross product (b-a)×(c-a); zero iff collinear."""
	return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def verify_claim(n: int, points: Sequence[Sequence[int]]) -> Tuple[bool, str]:
	"""Independently check distinctness, bounds, and no three collinear."""
	pts: List[Point] = [tuple(p) for p in points]  # type: ignore[misc]
	if len(pts) != len(set(pts)):
		return False, "duplicate_points"
	for x, y in pts:
		if not (1 <= x <= n and 1 <= y <= n):
			return False, "out_of_bounds"
	m = len(pts)
	for i in range(m):
		for j in range(i + 1, m):
			for k in range(j + 1, m):
				if _orient(pts[i], pts[j], pts[k]) == 0:
					return False, f"collinear:{pts[i]},{pts[j]},{pts[k]}"
	return True, "ok"


def certificate_hash(claim: dict) -> str:
	"""SHA-256 of canonical JSON (volatile fields excluded)."""
	payload = {k: claim[k] for k in claim if k not in {"stats", "claimed_at"}}
	blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
	return hashlib.sha256(blob.encode("utf-8")).hexdigest()
