"""Certify sharp ambient bound n≤2p for single-H cleanliness; density probes.

Usage:
  PYTHONPATH=. python3 research/scan_ambient.py > data/ambient_sharp_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.ambient import certify_sharp_bound, density_probe, primes_to


def main() -> None:
	"""Emit sharp-bound certificate (+ optional density rows)."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--limit", type=int, default=80)
	parser.add_argument("--density", action="store_true", help="also probe n≠2p ratios")
	args = parser.parse_args()

	fields = [
		"p",
		"clean_at_2p",
		"clean_at_2p1",
		"max_lifts_2p",
		"max_lifts_2p1",
		"nonprim_2p",
		"nonprim_2p1",
		"sharp_ok",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	fails = 0
	for p in primes_to(args.limit):
		t0 = time.monotonic()
		row = certify_sharp_bound(p)
		row["runtime_s"] = f"{time.monotonic() - t0:.3f}"
		writer.writerow(row)
		if not row["sharp_ok"]:
			fails += 1

	print(f"# sharp_ok failures: {fails}", file=sys.stderr)

	if args.density:
		dfields = [
			"p",
			"n",
			"ratio_2p",
			"ratio",
			"delta_ratio_vs_2p",
			"H_nonprim",
			"final",
		]
		print("# density probes:", file=sys.stderr)
		dw = csv.DictWriter(sys.stderr, fieldnames=dfields, extrasaction="ignore")
		dw.writeheader()
		for p in [17, 19, 31, 43]:
			for n in (2 * p - 1, 2 * p, 2 * p + 1, 3 * p):
				row = density_probe(p, n, polish_s=0.5, seed=p)
				dw.writerow(row)


if __name__ == "__main__":
	main()
