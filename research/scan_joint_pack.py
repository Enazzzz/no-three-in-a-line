"""Scan joint all-slope packing vs polished HJSW.

Usage:
  PYTHONPATH=. python3 research/scan_joint_pack.py > data/joint_pack_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.constructions import is_prime
from research.joint_pack import run_joint_case

PRIMES = [17, 19, 23, 29, 31, 37, 41, 43]
SPEC = "H1_H2_par_circ"


def main() -> None:
	"""Emit joint-pack comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--polish", type=float, default=0.7)
	parser.add_argument("--local", type=float, default=2.0)
	parser.add_argument("--trials", type=int, default=3)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"spec",
		"pool",
		"hjsw",
		"hjsw_polished",
		"empty_pack",
		"empty_final",
		"local_pack",
		"local_final",
		"best_final",
		"delta_vs_polished",
		"winner",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	for p in PRIMES:
		if not is_prime(p):
			continue
		t0 = time.monotonic()
		row = run_joint_case(
			p,
			SPEC,
			polish_s=args.polish,
			local_s=args.local,
			trials=args.trials,
			seed=p,
		)
		row["runtime_s"] = f"{time.monotonic() - t0:.2f}"
		writer.writerow(row)


if __name__ == "__main__":
	main()
