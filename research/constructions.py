"""Classical no-three-in-line constructions (Erdős parabola, HJSW)."""

from __future__ import annotations

from typing import List, Sequence, Set, Tuple

Point = Tuple[int, int]


def is_prime(n: int) -> bool:
	"""Trial-division primality for moderate integers."""
	if n < 2:
		return False
	if n % 2 == 0:
		return n == 2
	d = 3
	while d * d <= n:
		if n % d == 0:
			return False
		d += 2
	return True


def next_prime(n: int) -> int:
	"""Smallest prime ≥ n."""
	if n <= 2:
		return 2
	p = n if n % 2 else n + 1
	while not is_prime(p):
		p += 2
	return p


def erdos_parabola(p: int) -> Tuple[int, List[Point]]:
	"""Erdős modular parabola on a p×p board: (i, i² mod p) shifted to [1,p]."""
	if not is_prime(p) or p < 3:
		raise ValueError("erdos_parabola requires an odd prime p")
	pts = [(i + 1, ((i * i) % p) + 1) for i in range(p)]
	return p, sorted(set(pts))


def _block_rect(kind: str, p: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
	"""Return ((x0,x1),(y0,y1)) inclusive ranges for the base block kind in {A,B,C,D}.

	Matches Kovács–Nagy–Szabó / Hall et al. Definition 2.3:
	  A00 = [1,h]×[h+1,p-1]
	  B00 = [h+1,p-1]×[h+1,p-1]
	  C00 = [1,h]×[1,h]
	  D00 = [h+1,p-1]×[1,h]
	with h=(p-1)/2.
	"""
	h = (p - 1) // 2
	if kind == "A":
		return (1, h), (h + 1, p - 1)
	if kind == "B":
		return (h + 1, p - 1), (h + 1, p - 1)
	if kind == "C":
		return (1, h), (1, h)
	if kind == "D":
		return (h + 1, p - 1), (1, h)
	raise ValueError(f"unknown block kind {kind}")


def _shifted_block(kind: str, r: int, s: int, p: int) -> Set[Point]:
	"""Integer points of block Kind_{r,s} = Kind00 + (r p, s p)."""
	(x0, x1), (y0, y1) = _block_rect(kind, p)
	pts: Set[Point] = set()
	for x in range(x0 + r * p, x1 + r * p + 1):
		for y in range(y0 + s * p, y1 + s * p + 1):
			pts.add((x, y))
	return pts


def t2_blocks(p: int) -> Set[Point]:
	"""Union of the twelve HJSW half-blocks T2(p) inside G(p).

	T2 := (A0,1 ⊔ A1,0 ⊔ A1,1)
	    ⊔ (B-1,0 ⊔ B-1,1 ⊔ B0,1)
	    ⊔ (C0,0 ⊔ C1,0 ⊔ C1,1)
	    ⊔ (D-1,0 ⊔ D-1,1 ⊔ D0,0)
	"""
	specs = [
		("A", 0, 1), ("A", 1, 0), ("A", 1, 1),
		("B", -1, 0), ("B", -1, 1), ("B", 0, 1),
		("C", 0, 0), ("C", 1, 0), ("C", 1, 1),
		("D", -1, 0), ("D", -1, 1), ("D", 0, 0),
	]
	out: Set[Point] = set()
	for kind, r, s in specs:
		out |= _shifted_block(kind, r, s, p)
	return out


def ambient_grid(p: int) -> Tuple[int, int, int, int]:
	"""Return (xmin, xmax, ymin, ymax) for G(p) = [-(p-1)/2, (3p-1)/2] × [0, 2p-1]."""
	h = (p - 1) // 2
	return -h, (3 * p - 1) // 2, 0, 2 * p - 1


def hjsw(p: int, c: int = 1) -> Tuple[int, List[Point]]:
	"""Hall–Jackson–Sudbery–Wild S2 construction on an n=2p board.

	S2 = H(c,p) ∩ T2(p), translated so the ambient window maps into [1,n]².
	Size is 3*(p-1) = (3/2)*n - 3.
	"""
	if not is_prime(p) or p == 2:
		raise ValueError("hjsw requires an odd prime p")
	if c % p == 0:
		raise ValueError("c must be nonzero mod p")

	xmin, xmax, ymin, ymax = ambient_grid(p)
	t2 = t2_blocks(p)
	raw: List[Point] = []
	for x, y in t2:
		if not (xmin <= x <= xmax and ymin <= y <= ymax):
			continue
		if x % p == 0 or y % p == 0:
			continue
		if (x * y - c) % p != 0:
			continue
		raw.append((x, y))

	n = 2 * p
	shift_x = 1 - xmin
	shift_y = 1 - ymin
	pts = sorted({(x + shift_x, y + shift_y) for x, y in raw})
	pts = [(x, y) for x, y in pts if 1 <= x <= n and 1 <= y <= n]
	return n, pts


def hjsw_size(p: int) -> int:
	"""Expected |S2| = 3*(p-1)."""
	return 3 * (p - 1)


def middle_blocks(p: int) -> Set[Point]:
	"""Unused middle blocks M = A00 ⊔ B00 ⊔ C01 ⊔ D01."""
	specs = [("A", 0, 0), ("B", 0, 0), ("C", 0, 1), ("D", 0, 1)]
	out: Set[Point] = set()
	for kind, r, s in specs:
		out |= _shifted_block(kind, r, s, p)
	return out
