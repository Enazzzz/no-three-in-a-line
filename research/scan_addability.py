"""Generate addability summary CSV for interesting primes.

Usage: PYTHONPATH=. python research/scan_addability.py > data/addability_scan.csv
"""

from __future__ import annotations

import csv
import sys

from research.algebraic import summarize_addability
from research.constructions import hjsw

DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97, 107, 109, 139, 151, 167, 173, 181, 281]


def main() -> None:
	"""Print CSV of four-constraint survivor counts (corrected ≥2 row/col rule)."""
	writer = csv.DictWriter(
		sys.stdout,
		fieldnames=[
			"p",
			"n",
			"base_size",
			"hv_safe",
			"four_constraint_survivors",
			"middle_cells",
			"middle_hv_safe",
			"middle_four_survivors",
			"rows_with_one",
			"cols_with_one",
			"sat_plus",
			"sat_minus",
		],
	)
	writer.writeheader()
	for p in DEFAULT_PRIMES:
		n, pts = hjsw(p)
		s = summarize_addability(n, p, pts)
		writer.writerow(
			{
				"p": p,
				"n": n,
				"base_size": s["base_size"],
				"hv_safe": s["hv_safe"],
				"four_constraint_survivors": s["four_constraint_survivors"],
				"middle_cells": s["middle_cells"],
				"middle_hv_safe": s["middle_hv_safe"],
				"middle_four_survivors": s["middle_four_survivors"],
				"rows_with_one": s["rows_with_one"],
				"cols_with_one": s["cols_with_one"],
				"sat_plus": s["sat_plus"],
				"sat_minus": s["sat_minus"],
			}
		)


if __name__ == "__main__":
	main()
