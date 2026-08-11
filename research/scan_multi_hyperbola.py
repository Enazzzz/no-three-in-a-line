"""Scan simultaneous / delete-first multi-hyperbola vs HJSW and subset.

Usage:
  PYTHONPATH=. python3 research/scan_multi_hyperbola.py > data/multi_hyperbola_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.constructions import hjsw
from research.multi_hyperbola import best_multi_hyperbola, build_multi_hyperbola
from research.subset import max_safe_augmentation
from research.verify import verify_claim

# Keep ≤97 by default so the combinatorial residue×mode sweep fits a VM turn.
DEFAULT_PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97]
EXTRA_PRIMES = [107, 109, 139]


def main() -> None:
	"""Emit comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--extra", action="store_true", help="Include primes up to 139")
	parser.add_argument("--polish", type=float, default=2.0)
	args = parser.parse_args()
	primes = list(DEFAULT_PRIMES) + (EXTRA_PRIMES if args.extra else [])

	fields = [
		"p",
		"n",
		"hjsw_size",
		"hjsw_ratio",
		"subset_size",
		"subset_ratio",
		"multi_size",
		"multi_ratio",
		"multi_family",
		"multi_mode",
		"multi_residues",
		"multi_mask_t2",
		"multi_pool",
		"best_method",
		"best_ratio",
		"beats_1_55",
		"delta_multi_minus_hjsw",
		"delta_multi_minus_subset",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in primes:
		t0 = time.monotonic()
		n, base = hjsw(p)
		subset_pts, sst = max_safe_augmentation(n, base, exact_limit=24 if p <= 120 else 18)
		ok_s, _ = verify_claim(n, subset_pts)
		if not ok_s:
			subset_pts = list(base)

		n_m, multi_pts, mst = best_multi_hyperbola(p, polish_s=args.polish, seed=p)
		assert n_m == n

		hjsw_ratio = len(base) / n
		subset_ratio = len(subset_pts) / n
		multi_ratio = len(multi_pts) / n
		best = max(
			(("hjsw", hjsw_ratio), ("subset", subset_ratio), ("multi", multi_ratio)),
			key=lambda t: t[1],
		)
		writer.writerow(
			{
				"p": p,
				"n": n,
				"hjsw_size": len(base),
				"hjsw_ratio": f"{hjsw_ratio:.6f}",
				"subset_size": len(subset_pts),
				"subset_ratio": f"{subset_ratio:.6f}",
				"multi_size": len(multi_pts),
				"multi_ratio": f"{multi_ratio:.6f}",
				"multi_family": mst.get("family", ""),
				"multi_mode": mst.get("mode", ""),
				"multi_residues": "|".join(str(c) for c in (mst.get("residues") or [])),
				"multi_mask_t2": mst.get("mask_t2", ""),
				"multi_pool": mst.get("pool", ""),
				"best_method": best[0],
				"best_ratio": f"{best[1]:.6f}",
				"beats_1_55": int(best[1] > 1.55),
				"delta_multi_minus_hjsw": len(multi_pts) - len(base),
				"delta_multi_minus_subset": len(multi_pts) - len(subset_pts),
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
