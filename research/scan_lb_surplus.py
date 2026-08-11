"""Scan LB − surplus certificates for multi-H primary packings.

Usage:
  PYTHONPATH=. python3 research/scan_lb_surplus.py > data/lb_surplus_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.lb_surplus import (
	analyze_lb_surplus,
	ntil_surplus_counterexample,
	primes_from_to,
)
from research.multi_hyperbola import default_residue_sets


def main() -> None:
	"""Emit LB≥surplus certificate CSV (+ counterexample notes on stderr)."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--lo", type=int, default=7)
	parser.add_argument("--hi", type=int, default=80)
	parser.add_argument("--bnb", type=float, default=1.2)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"residues",
		"pool",
		"hjsw",
		"primary",
		"primary_method",
		"surplus",
		"bad_lines",
		"excess_sum",
		"lb_disjoint",
		"lb_minus_surplus",
		"holds",
		"pure_bad",
		"mixed_bad",
		"color_sizes",
		"minority",
		"minority_over_3",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	fails_ge17 = 0
	total_ge17 = 0
	for p in primes_from_to(args.lo, args.hi):
		for res in default_residue_sets(p):
			if len(res) < 2:
				continue
			t0 = time.monotonic()
			row = analyze_lb_surplus(p, res, bnb_s=args.bnb, seed=p)
			row["runtime_s"] = f"{time.monotonic() - t0:.3f}"
			writer.writerow(row)
			if p >= 17:
				total_ge17 += 1
				if not row["holds"]:
					fails_ge17 += 1

	# Document the universal-claim counterexample on a few primes.
	err = sys.stderr
	print("# NTIL counterexamples to 'every primary-feasible S' universality:", file=err)
	for p in (17, 19, 31):
		cex = ntil_surplus_counterexample(p, local_s=1.2)
		print(cex, file=err)
	print(f"# certificate rows p>=17: {total_ge17}, failures: {fails_ge17}", file=err)


if __name__ == "__main__":
	main()
