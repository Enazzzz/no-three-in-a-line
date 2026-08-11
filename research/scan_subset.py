"""Scan four-constraint + individually-ok + max safe subset for scoped primes.

Usage:
  PYTHONPATH=. python research/scan_subset.py > data/subset_scan.csv

Keeps compute light: default primes stop at 109; exact MIS only if
individually-ok ≤ 24.
"""

from __future__ import annotations

import csv
import sys
import time

from research.algebraic import four_constraint_survivors, summarize_addability
from research.constructions import hjsw
from research.subset import max_safe_augmentation
from research.verify import verify_claim

# Cap at 97 for this VM pass; larger primes need distributed workers.
DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97]


def main() -> None:
	"""Emit CSV of subset-augmentation results."""
	fields = [
		"p",
		"n",
		"base_size",
		"hv_safe",
		"four_constraint_survivors",
		"individually_ok",
		"added",
		"final_size",
		"ratio",
		"beats_1_55",
		"method",
		"runtime_s",
	]
	# Line-buffered so a killed VM still leaves a partial CSV on disk if redirected.
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()
	for p in DEFAULT_PRIMES:
		t0 = time.monotonic()
		n, base = hjsw(p)
		s = summarize_addability(n, p, base)
		aug, st = max_safe_augmentation(n, base, exact_limit=24)
		ok, _ = verify_claim(n, aug)
		assert ok, (p, st)
		writer.writerow(
			{
				"p": p,
				"n": n,
				"base_size": len(base),
				"hv_safe": s["hv_safe"],
				"four_constraint_survivors": s["four_constraint_survivors"],
				"individually_ok": st["individually_ok"],
				"added": st["added"],
				"final_size": len(aug),
				"ratio": f"{st['ratio']:.6f}",
				"beats_1_55": int(st["ratio"] > 1.55),
				"method": st["method"],
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
