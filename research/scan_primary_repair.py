"""Scan exact primary-class repair on multi-hyperbola pools.

Usage:
  PYTHONPATH=. python3 research/scan_primary_repair.py > data/primary_repair_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.constructions import hjsw
from research.primary_repair import best_primary_pipeline
from research.subset import max_safe_augmentation
from research.verify import verify_claim

DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67]


def main() -> None:
	"""Emit primary-repair comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--bnb", type=float, default=4.0, help="BnB seconds per instance")
	parser.add_argument("--polish", type=float, default=1.0)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"hjsw_size",
		"subset_size",
		"subset_ratio",
		"best_residues",
		"mask_t2",
		"pool",
		"primary_size",
		"delta_primary_minus_hjsw",
		"general_collinear_triples",
		"repaired_size",
		"final_size",
		"final_ratio",
		"delta_final_minus_hjsw",
		"delta_final_minus_subset",
		"primary_method",
		"primary_timed_out",
		"beats_1_55",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in DEFAULT_PRIMES:
		t0 = time.monotonic()
		n, base = hjsw(p)
		sub, _ = max_safe_augmentation(n, base, exact_limit=24 if p <= 120 else 18)
		ok, _ = verify_claim(n, sub)
		if not ok:
			sub = list(base)
		row = best_primary_pipeline(p, bnb_s=args.bnb, polish_s=args.polish)
		writer.writerow(
			{
				"p": p,
				"n": n,
				"hjsw_size": len(base),
				"subset_size": len(sub),
				"subset_ratio": f"{len(sub)/n:.6f}",
				"best_residues": "|".join(str(c) for c in row["residues"]),
				"mask_t2": row["mask_t2"],
				"pool": row["pool"],
				"primary_size": row["primary_size"],
				"delta_primary_minus_hjsw": row["delta_primary_minus_hjsw"],
				"general_collinear_triples": row["general_collinear_triples"],
				"repaired_size": row["repaired_size"],
				"final_size": row["final_size"],
				"final_ratio": f"{row['final_ratio']:.6f}",
				"delta_final_minus_hjsw": row["delta_final_minus_hjsw"],
				"delta_final_minus_subset": row["final_size"] - len(sub),
				"primary_method": row["primary_method"],
				"primary_timed_out": int(row["primary_timed_out"]),
				"beats_1_55": int(row["final_ratio"] > 1.55),
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
