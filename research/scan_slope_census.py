"""Scan slope census + mixed-kill / risk-mask constructions vs HJSW.

Usage:
  PYTHONPATH=. python3 research/scan_slope_census.py > data/slope_census_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time

from research.constructions import hjsw, is_prime
from research.search import greedy_augment
from research.slope_census import (
	census_single_vs_union,
	hjsw_protected_enrich,
	mixed_kill_then_primary,
	risk_masked_second_hyperbola,
	single_hyperbola_primary_pack,
)
from research.verify import verify_claim

PRIMES = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43]


def main() -> None:
	"""Emit slope-census and mask construction CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--bnb", type=float, default=2.0)
	parser.add_argument("--hit", type=float, default=1.5)
	parser.add_argument("--polish", type=float, default=0.8)
	args = parser.parse_args()

	fields = [
		"p",
		"n",
		"hjsw",
		"hjsw_polished",
		"single_bad_c0",
		"single_bad_c1",
		"union_pure",
		"union_mixed",
		"union_all_mixed",
		"union_disjoint_lb",
		"single_h_final",
		"single_h_delta",
		"mixed_kill_final",
		"mixed_kill_delta",
		"mixed_deleted",
		"exact_min_del",
		"risk_full_safe",
		"risk_prim_safe",
		"risk_prim_final",
		"risk_prim_delta_pol",
		"protect_final",
		"protect_delta_pol",
		"best_final",
		"best_delta_pol",
		"best_family",
		"runtime_s",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in PRIMES:
		if not is_prime(p):
			continue
		t0 = time.monotonic()
		n, hjsw_pts = hjsw(p, 1)
		hjsw_pol = greedy_augment(n, list(hjsw_pts), time_limit_s=args.polish, seed=p)
		ok_h, _ = verify_claim(n, hjsw_pol)
		if not ok_h:
			hjsw_pol = list(hjsw_pts)

		cen = census_single_vs_union(p, 1, 2)
		u = cen["census_union"]

		_, _, st_s = single_hyperbola_primary_pack(
			p, 1, bnb_s=args.bnb, polish_s=args.polish, seed=p
		)
		_, _, st_m = mixed_kill_then_primary(
			p,
			[1, 2],
			bnb_s=args.bnb,
			hit_s=args.hit,
			polish_s=args.polish,
			seed=p,
		)
		_, _, st_rf = risk_masked_second_hyperbola(
			p, 1, 2, max_risk=0, base_mode="full", bnb_s=args.bnb, polish_s=args.polish, seed=p
		)
		_, _, st_rp = risk_masked_second_hyperbola(
			p, 1, 2, max_risk=0, base_mode="primary", bnb_s=args.bnb, polish_s=args.polish, seed=p
		)
		_, _, st_p = hjsw_protected_enrich(p, 2, c0=1, polish_s=args.polish, seed=p)

		def dpol(size: int) -> int:
			return size - len(hjsw_pol)

		cands = [
			("single_h_primary", st_s["final_size"], dpol(st_s["final_size"])),
			("mixed_kill_then_primary", st_m["final_size"], dpol(st_m["final_size"])),
			("risk_masked_primary", st_rp["final_size"], dpol(st_rp["final_size"])),
			("hjsw_protected_enrich", st_p["final_size"], dpol(st_p["final_size"])),
			("hjsw_polished", len(hjsw_pol), 0),
		]
		best = max(cands, key=lambda t: t[1])

		writer.writerow(
			{
				"p": p,
				"n": n,
				"hjsw": len(hjsw_pts),
				"hjsw_polished": len(hjsw_pol),
				"single_bad_c0": cen["census_c0"]["bad_lines"],
				"single_bad_c1": cen["census_c1"]["bad_lines"],
				"union_pure": u["pure_lines"],
				"union_mixed": u["mixed_lines"],
				"union_all_mixed": int(u["all_mixed"]),
				"union_disjoint_lb": u["disjoint_lb"],
				"single_h_final": st_s["final_size"],
				"single_h_delta": st_s["delta_vs_hjsw"],
				"mixed_kill_final": st_m["final_size"],
				"mixed_kill_delta": st_m["delta_vs_hjsw"],
				"mixed_deleted": st_m["mixed_deleted"],
				"exact_min_del": st_m["exact_min_deletions"],
				"risk_full_safe": st_rf["safe_extras"],
				"risk_prim_safe": st_rp["safe_extras"],
				"risk_prim_final": st_rp["final_size"],
				"risk_prim_delta_pol": dpol(st_rp["final_size"]),
				"protect_final": st_p["final_size"],
				"protect_delta_pol": dpol(st_p["final_size"]),
				"best_final": best[1],
				"best_delta_pol": best[2],
				"best_family": best[0],
				"runtime_s": f"{time.monotonic() - t0:.2f}",
			}
		)


if __name__ == "__main__":
	main()
