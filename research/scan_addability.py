"""Generate addability summary CSV for interesting primes (offline utility)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# Repo root on path when run as python -m is awkward; prefer:
# PYTHONPATH=. python research/scan_addability.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from research.algebraic import summarize_addability
from research.constructions import hjsw


DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97]


def main() -> None:
	"""Print CSV of four-constraint survivor counts."""
	writer = csv.DictWriter(
		sys.stdout,
		fieldnames=[
			"p",
			"n",
			"base_size",
			"middle_hv_safe",
			"four_constraint_survivors",
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
				"middle_hv_safe": s["middle_hv_safe"],
				"four_constraint_survivors": s["four_constraint_survivors"],
				"sat_plus": s["sat_plus"],
				"sat_minus": s["sat_minus"],
			}
		)


if __name__ == "__main__":
	main()
