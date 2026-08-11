"""Scan non-hyperbola second families vs polished HJSW.

Usage:
  PYTHONPATH=. python3 research/scan_nonhyperbola.py > data/nonhyperbola_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.constructions import is_prime
from research.nonhyperbola import scan_all_families

PRIMES = [17, 19, 23, 29, 31]


def main() -> None:
	"""Emit non-hyperbola family comparison CSV (long form: one row per family)."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--polish", type=float, default=0.8)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"family",
		"hjsw",
		"pool",
		"self_nonprim3",
		"risk0",
		"risk0_primary_ok",
		"reduced_seed",
		"hjsw_polished",
		"enrich_added",
		"enrich_final",
		"delta_vs_hjsw",
		"delta_vs_polished",
		"verified",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	for p in PRIMES:
		if not is_prime(p):
			continue
		t0 = time.monotonic()
		rows = scan_all_families(p, polish_s=args.polish, seed=p)
		elapsed = time.monotonic() - t0
		# Split runtime evenly for reporting.
		per = elapsed / max(1, len(rows))
		for row in rows:
			row["runtime_s"] = f"{per:.2f}"
			# Optional fields for delete_* rows.
			row.setdefault("pool", "")
			row.setdefault("self_nonprim3", "")
			row.setdefault("risk0_primary_ok", "")
			row.setdefault("reduced_seed", "")
			writer.writerow(row)


if __name__ == "__main__":
	main()
