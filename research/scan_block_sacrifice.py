"""Scan HJSW block-sacrifice constructions vs polished baseline.

Usage:
  PYTHONPATH=. python3 research/scan_block_sacrifice.py > data/block_sacrifice_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.block_sacrifice import run_block_sacrifice
from research.constructions import is_prime

PRIMES = [17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 61]


def main() -> None:
	"""Emit block-sacrifice comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--polish", type=float, default=0.6)
	parser.add_argument("--seeds", type=int, default=5)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"hjsw",
		"baseline_polished",
		"best_final",
		"delta_vs_baseline",
		"best_tag",
		"dropped",
		"refill_added",
		"random_delta_max",
		"random_delta_mean",
		"beats_random_max",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	for p in PRIMES:
		if not is_prime(p):
			continue
		t0 = time.monotonic()
		row = run_block_sacrifice(
			p,
			polish_s=args.polish,
			n_polish_seeds=args.seeds,
			seed=p,
			include_random_control=True,
		)
		row["runtime_s"] = f"{time.monotonic() - t0:.2f}"
		writer.writerow(row)


if __name__ == "__main__":
	main()
