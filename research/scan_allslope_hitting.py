"""Scan all-slope hitting bounds vs primary surplus over HJSW.

Usage:
  PYTHONPATH=. python3 research/scan_allslope_hitting.py > data/allslope_hitting_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.allslope_hitting import run_hitting_case
from research.multi_hyperbola import default_residue_sets

# Exact BnB deletions only cheap for smaller primaries; still record LBs everywhere.
DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61]


def main() -> None:
	"""Emit hitting-bound CSV for max-primary multi-hyperbola sets."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--bnb", type=float, default=3.0)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"residues",
		"mask_t2",
		"pool",
		"hjsw_size",
		"primary_size",
		"surplus",
		"bad_lines",
		"excess_sum",
		"lb_disjoint",
		"ub_greedy",
		"min_deletions",
		"deletion_method",
		"lb_minus_surplus",
		"exact_del_minus_surplus",
		"kept_minus_hjsw",
		"greedy_residual_verified",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in DEFAULT_PRIMES:
		# Pick the residue/mask maximizing primary size (the surplus case).
		best = None
		t0 = time.monotonic()
		for residues in default_residue_sets(p):
			for mask in (False, True):
				# Spend less BnB on larger p.
				bnb = args.bnb if p <= 37 else min(args.bnb, 1.5)
				row = run_hitting_case(p, residues, mask_t2=mask, bnb_s=bnb)
				if best is None or row["primary_size"] > best["primary_size"]:
					best = row
		assert best is not None
		writer.writerow(
			{
				"p": best["p"],
				"n": best["n"],
				"residues": "|".join(str(c) for c in best["residues"]),
				"mask_t2": best["mask_t2"],
				"pool": best["pool"],
				"hjsw_size": best["hjsw_size"],
				"primary_size": best["primary_size"],
				"surplus": best["surplus"],
				"bad_lines": best["hit_bad_lines"],
				"excess_sum": best["hit_excess_sum"],
				"lb_disjoint": best["hit_lb_disjoint"],
				"ub_greedy": best["hit_ub_greedy"],
				"min_deletions": best["hit_min_deletions"],
				"deletion_method": best["hit_deletion_method"],
				"lb_minus_surplus": best["lb_minus_surplus"],
				"exact_del_minus_surplus": best["exact_del_minus_surplus"],
				"kept_minus_hjsw": best["kept_minus_hjsw"],
				"greedy_residual_verified": int(best["greedy_residual_verified"]),
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
