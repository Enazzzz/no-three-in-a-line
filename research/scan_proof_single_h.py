"""Verify single-H proof ingredients across primes.

Usage:
  PYTHONPATH=. python3 research/scan_proof_single_h.py > data/proof_single_h_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

from research.proof_single_h import primes_to, verify_proof_ingredients


def main() -> None:
	"""Emit proof-ingredient verification CSV."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--limit", type=int, default=120)
	args = parser.parse_args()

	fields = [
		"p",
		"c",
		"fp_at_most_two",
		"collinear_delta_mod_p",
		"same_residue_chord_primary",
		"nonprimary_ge3",
		"primary_two_res_triples",
		"nonprimary_triples",
		"ok",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields)
	writer.writeheader()

	for p in primes_to(args.limit):
		st = verify_proof_ingredients(p, 1)
		tc = st["triple_classes"]
		nonprim_triples = (
			tc["nonprimary_same_res"]
			+ tc["nonprimary_two_res"]
			+ tc["nonprimary_three_res"]
		)
		writer.writerow(
			{
				"p": p,
				"c": st["c"],
				"fp_at_most_two": int(st["fp_at_most_two"]),
				"collinear_delta_mod_p": int(st["collinear_delta_mod_p"]),
				"same_residue_chord_primary": int(st["same_residue_chord_primary"]),
				"nonprimary_ge3": st["nonprimary_ge3"],
				"primary_two_res_triples": tc["primary_two_res"],
				"nonprimary_triples": nonprim_triples,
				"ok": int(st["ok"]),
			}
		)


if __name__ == "__main__":
	main()
