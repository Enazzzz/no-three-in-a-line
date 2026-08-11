"""Collinearity verification for no-three-in-line configurations."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, List, Sequence, Tuple

Point = Tuple[int, int]


def _orient(a: Point, b: Point, c: Point) -> int:
	"""Return the cross product (b-a) x (c-a); 0 iff a,b,c collinear."""
	return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def verify_claim(n: int, points: Sequence[Sequence[int]]) -> Tuple[bool, str]:
	"""Independently check a claimed configuration.

	Checks distinctness, bounds in [1,n]^2, and no three collinear.
	"""
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


def is_valid(n: int, points: Iterable[Sequence[int]]) -> bool:
	"""Return True iff the configuration is a valid no-three-in-line set."""
	ok, _ = verify_claim(n, list(points))
	return ok


def certificate_hash(claim: dict) -> str:
	"""SHA-256 of canonical JSON for a claim payload (sorted keys)."""
	# Drop volatile fields that should not affect the certificate identity.
	payload = {k: claim[k] for k in claim if k not in {"stats", "claimed_at"}}
	blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
	return hashlib.sha256(blob.encode("utf-8")).hexdigest()
