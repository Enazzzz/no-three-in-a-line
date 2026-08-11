"""Compare structured schedules vs raw unions; extend LB≥surplus checks.

Usage:
  PYTHONPATH=. python3 research/scan_structured_schedule.py > data/structured_schedule_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.allslope_hitting import run_hitting_case
from research.multi_hyperbola import default_residue_sets, multi_hyperbola_pool
from research.structured_schedule import SCHEDULES, best_structured, evaluate_structured

PRIMES = [5, 7, 17, 19, 31, 37, 61, 67, 71, 83]


def main() -> None:
	"""Emit structured-schedule comparison CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--bnb", type=float, default=2.5)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"raw_surplus",
		"raw_lb_minus_surplus",
		"raw_kept_minus_hjsw",
		"struct_schedule",
		"struct_c0",
		"struct_c1",
		"struct_pool",
		"struct_primary",
		"struct_surplus",
		"struct_lb_minus_surplus",
		"struct_kept_minus_hjsw",
		"struct_final",
		"struct_ratio",
		"struct_beats_hjsw",
		"lb_ge_surplus_raw",
		"lb_ge_surplus_struct",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in PRIMES:
		t0 = time.monotonic()
		# Raw max-primary among default residue sets (unmasked), for LB compare.
		raw_best = None
		for residues in default_residue_sets(p)[:4]:
			row = run_hitting_case(p, residues, mask_t2=False, bnb_s=min(1.5, args.bnb))
			if raw_best is None or row["primary_size"] > raw_best["primary_size"]:
				raw_best = row
		assert raw_best is not None

		st = best_structured(p, bnb_s=args.bnb, polish_s=0.8)
		writer.writerow(
			{
				"p": p,
				"n": 2 * p,
				"raw_surplus": raw_best["surplus"],
				"raw_lb_minus_surplus": raw_best["lb_minus_surplus"],
				"raw_kept_minus_hjsw": raw_best["kept_minus_hjsw"],
				"struct_schedule": st.get("schedule", ""),
				"struct_c0": st.get("c0", ""),
				"struct_c1": st.get("c1", ""),
				"struct_pool": st.get("pool", ""),
				"struct_primary": st.get("primary_size", ""),
				"struct_surplus": st.get("surplus", ""),
				"struct_lb_minus_surplus": st.get("lb_minus_surplus", ""),
				"struct_kept_minus_hjsw": st.get("kept_minus_hjsw", ""),
				"struct_final": st.get("final_size", ""),
				"struct_ratio": f"{st.get('final_ratio', 0):.6f}",
				"struct_beats_hjsw": int(bool(st.get("beats_hjsw_final"))),
				"lb_ge_surplus_raw": int(raw_best["lb_minus_surplus"] >= 0),
				"lb_ge_surplus_struct": int(st.get("lb_minus_surplus", 0) >= 0),
				"runtime_s": f"{time.monotonic() - t0:.3f}",
			}
		)
		out.flush()


if __name__ == "__main__":
	main()
