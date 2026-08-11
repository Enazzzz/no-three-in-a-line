"""Compare HJSW / subset / hyperbola-union on interesting primes.

Usage:
  PYTHONPATH=. python3 research/scan_hyperbola_union.py > data/hyperbola_union_scan.csv

Compute scope: winning primes up to 181 by default (p=281 optional via --large).
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.hyperbola_union import compare_methods

DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97, 107, 109, 139, 151, 167, 173, 181]
LARGE_PRIMES = [281]


def main() -> None:
	"""Emit CSV comparing construction families."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--large", action="store_true", help="Also include p=281")
	parser.add_argument("--polish", type=float, default=3.0)
	args = parser.parse_args()
	primes = list(DEFAULT_PRIMES)
	if args.large:
		primes += LARGE_PRIMES

	fields = [
		"p",
		"n",
		"hjsw_size",
		"hjsw_ratio",
		"subset_size",
		"subset_ratio",
		"subset_indiv_ok",
		"union_size",
		"union_ratio",
		"union_family",
		"union_c1",
		"union_extras",
		"best_method",
		"best_ratio",
		"beats_1_55",
		"delta_union_minus_subset",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in primes:
		t0 = time.monotonic()
		# Scale polish down a bit for larger p.
		polish = min(args.polish, 2.0 + 20.0 / max(5, p / 10.0))
		cmp = compare_methods(p, polish_s=polish)
		hjsw = cmp["hjsw"]
		subset = cmp["subset"]
		union = cmp["union"]
		best = max(
			(("hjsw", hjsw["ratio"]), ("subset", subset["ratio"]), ("union", union["ratio"])),
			key=lambda t: t[1],
		)
		writer.writerow(
			{
				"p": p,
				"n": cmp["n"],
				"hjsw_size": hjsw["size"],
				"hjsw_ratio": f"{hjsw['ratio']:.6f}",
				"subset_size": subset["size"],
				"subset_ratio": f"{subset['ratio']:.6f}",
				"subset_indiv_ok": subset.get("individually_ok", ""),
				"union_size": union["size"],
				"union_ratio": f"{union['ratio']:.6f}",
				"union_family": union.get("union_family", ""),
				"union_c1": union.get("c1", ""),
				"union_extras": "|".join(str(x) for x in (union.get("extras_used") or [])),
				"best_method": best[0],
				"best_ratio": f"{best[1]:.6f}",
				"beats_1_55": int(best[1] > 1.55),
				"delta_union_minus_subset": union["size"] - subset["size"],
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
