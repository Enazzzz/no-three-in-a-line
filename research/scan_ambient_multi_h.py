"""Scan ambient-aligned multi-hyperbola packs vs polished HJSW.

Usage:
  PYTHONPATH=. python3 research/scan_ambient_multi_h.py > data/ambient_multi_h_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.ambient_multi_h import (
	REGION_T2,
	REGION_T2M,
	analyze_ambient_primary,
	board_vs_ambient_overlap,
	default_residues,
	run_ambient_case,
)
from research.constructions import is_prime

PRIMES = [17, 19, 23, 29, 31, 37, 41, 43, 47]


def main() -> None:
	"""Emit ambient-aligned multi-H comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--polish", type=float, default=0.8)
	parser.add_argument("--local", type=float, default=2.5)
	parser.add_argument("--trials", type=int, default=3)
	parser.add_argument("--bnb", type=float, default=1.0)
	parser.add_argument("--residues", type=int, default=3, help="use 1..k residues")
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"region",
		"residues",
		"pool",
		"hjsw",
		"hjsw_in_pool",
		"hjsw_polished",
		"local_pack",
		"best_final",
		"delta_vs_hjsw",
		"delta_vs_polished",
		"winner",
		"verified",
		"primary",
		"surplus",
		"lb_disjoint",
		"lb_minus_surplus",
		"primary_holds",
		"board_hjsw_overlap",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	for p in PRIMES:
		if not is_prime(p):
			continue
		res = default_residues(p, args.residues)
		t0 = time.monotonic()
		# Prefer T2∪M (larger than T2; still ambient-aligned).
		row = run_ambient_case(
			p,
			res,
			region=REGION_T2M,
			polish_s=args.polish,
			local_s=args.local,
			trials=args.trials,
			seed=p,
		)
		prim = analyze_ambient_primary(
			p, res, region=REGION_T2M, bnb_s=args.bnb, seed=p
		)
		ov = board_vs_ambient_overlap(p, res)
		row.update(
			{
				"primary": prim["primary"],
				"surplus": prim["surplus"],
				"lb_disjoint": prim["lb_disjoint"],
				"lb_minus_surplus": prim["lb_minus_surplus"],
				"primary_holds": prim["holds"],
				"board_hjsw_overlap": ov["hjsw_in_board"],
				"runtime_s": f"{time.monotonic() - t0:.2f}",
			}
		)
		writer.writerow(row)

		# Also emit a T2-only comparison row for the same p.
		row2 = run_ambient_case(
			p,
			res,
			region=REGION_T2,
			polish_s=args.polish,
			local_s=args.local,
			trials=args.trials,
			seed=p,
		)
		prim2 = analyze_ambient_primary(
			p, res, region=REGION_T2, bnb_s=args.bnb, seed=p
		)
		row2.update(
			{
				"primary": prim2["primary"],
				"surplus": prim2["surplus"],
				"lb_disjoint": prim2["lb_disjoint"],
				"lb_minus_surplus": prim2["lb_minus_surplus"],
				"primary_holds": prim2["holds"],
				"board_hjsw_overlap": ov["hjsw_in_board"],
				"runtime_s": f"{time.monotonic() - t0:.2f}",
			}
		)
		writer.writerow(row2)


if __name__ == "__main__":
	main()
