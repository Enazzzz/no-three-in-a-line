"""Scan Conjecture B reduction lemmas B1/B2.

Usage:
  PYTHONPATH=. python3 research/scan_conjecture_b_lemmas.py > data/conjecture_b_lemmas_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.conjecture_b_lemmas import mono_color_primary_bound, scan_reduction_rows
from research.constructions import is_prime
from research.lb_surplus import primes_from_to


def main() -> None:
	"""Emit B1/B2 reduction CSV plus a short mono-color appendix on stderr."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--lo", type=int, default=17)
	parser.add_argument("--hi", type=int, default=79)
	parser.add_argument("--bnb", type=float, default=1.0)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"residues",
		"pool",
		"hjsw",
		"primary",
		"primary_method",
		"majority",
		"minority",
		"minority_covered",
		"coverage_frac",
		"color_sizes",
		"bad_lines",
		"lb_disjoint",
		"surplus",
		"floor_m_over_3",
		"b1_lb_ge_m3",
		"b2_m3_ge_surplus",
		"implies_B",
		"lb_minus_surplus",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	t_all = time.monotonic()
	rows = scan_reduction_rows(lo=args.lo, hi=args.hi, bnb_s=args.bnb)
	# Re-run with timings per row would double work; stamp batch time thinly.
	per = (time.monotonic() - t_all) / max(len(rows), 1)
	b1 = b2 = both = 0
	for row in rows:
		row["runtime_s"] = f"{per:.3f}"
		b1 += int(row["b1_lb_ge_m3"])
		b2 += int(row["b2_m3_ge_surplus"])
		both += int(row["implies_B"])
		writer.writerow(row)

	print(
		f"# summary: rows={len(rows)} B1={b1}/{len(rows)} B2={b2}/{len(rows)} "
		f"implies_B={both}/{len(rows)}",
		file=sys.stderr,
	)

	# Mono-color appendix (not part of the main CSV).
	print("# mono-color primary max vs HJSW", file=sys.stderr)
	for p in primes_from_to(args.lo, min(args.hi, 43)):
		if not is_prime(p):
			continue
		m = mono_color_primary_bound(p, 1, bnb_s=min(2.0, args.bnb + 0.5), seed=p)
		print(
			f"# mono p={m['p']} best={m['best']} hjsw={m['hjsw']} "
			f"ratio={m['best_over_hjsw']} ntil={m['verified_ntil']}",
			file=sys.stderr,
		)


if __name__ == "__main__":
	main()
