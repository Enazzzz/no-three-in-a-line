"""Computational census: single modular hyperbola non-primary cleanliness.

Supports the proof-track item in NEXT_AGENT.md: on n=2p boards, H(c) appears
to have no non-primary line with ≥3 points (only primary classes do).
"""

from __future__ import annotations

import argparse
import csv
import sys

from research.allslope_hitting import is_primary_dir, lines_with_counts
from research.constructions import is_prime, next_prime
from research.hyperbola_union import hyperbola_points


def census_single_h(p: int, c: int = 1) -> dict:
	"""Count ≥3-lines inside H(c) on the n=2p board, split primary/non-primary."""
	n = 2 * p
	pool = hyperbola_points(n, p, c % p)
	prim = 0
	nonprim = 0
	max_k = 0
	for (dx, dy, _b), pts in lines_with_counts(pool).items():
		if len(pts) < 3:
			continue
		max_k = max(max_k, len(pts))
		if is_primary_dir(dx, dy):
			prim += 1
		else:
			nonprim += 1
	return {
		"p": p,
		"n": n,
		"c": c % p,
		"pool": len(pool),
		"primary_ge3": prim,
		"nonprimary_ge3": nonprim,
		"max_on_line": max_k,
		"clean_nonprimary": int(nonprim == 0),
	}


def primes_to(limit: int) -> list:
	"""Odd primes ≤ limit."""
	out = []
	p = 3
	while p <= limit:
		if is_prime(p):
			out.append(p)
		p = next_prime(p + 1)
	return out


def main() -> None:
	"""Emit single-H cleanliness CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--limit", type=int, default=200)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"c",
		"pool",
		"primary_ge3",
		"nonprimary_ge3",
		"max_on_line",
		"clean_nonprimary",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()
	for p in primes_to(args.limit):
		writer.writerow(census_single_h(p, 1))


if __name__ == "__main__":
	main()
