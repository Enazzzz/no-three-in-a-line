"""Scan B2 provenance: mono caps vs whether they imply lemma B2.

Usage:
  PYTHONPATH=. python3 research/scan_b2_provenance.py > data/b2_provenance_scan.csv
"""

from __future__ import annotations

import argparse
import csv
import sys

from research.b2_provenance import (
	b2_from_mono_cap_alone,
	conjectured_mono_primary_cap,
	mono_primary_size,
	row_col_automatic,
)
from research.conjecture_b_lemmas import analyze_reduction
from research.constructions import is_prime
from research.lb_surplus import primes_from_to
from research.multi_hyperbola import default_residue_sets


def main() -> None:
	"""Emit mono-size rows and a multi-H B2-from-cap check CSV on stdout.

	Two blocks separated by a blank line are awkward for DictWriter; we emit
	one unified schema with ``kind`` ∈ {mono, multih}.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("--lo", type=int, default=5)
	parser.add_argument("--hi", type=int, default=61)
	parser.add_argument("--bnb", type=float, default=2.0)
	args = parser.parse_args()

	fields = [
		"kind",
		"p",
		"residues",
		"row_col_automatic",
		"mono_best",
		"conjectured_cap",
		"hits_cap",
		"hjsw",
		"best_over_hjsw",
		"asymp_2p_over_3pm1",
		"majority",
		"minority",
		"surplus",
		"floor_m_over_3",
		"b2_actual",
		"b2_forced_by_mono_cap",
		"surplus_if_M_at_cap",
	]
	out = open(sys.stdout.fileno(), mode="w", buffering=1)
	writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
	writer.writeheader()

	mono_hits = 0
	mono_n = 0
	for p in primes_from_to(args.lo, args.hi):
		if not is_prime(p) or p == 2:
			continue
		m = mono_primary_size(p, 1, bnb_s=args.bnb, seed=p)
		mono_n += 1
		mono_hits += int(m["hits_cap"])
		writer.writerow(
			{
				"kind": "mono",
				"p": p,
				"residues": "1",
				"row_col_automatic": m["row_col_automatic"],
				"mono_best": m["best"],
				"conjectured_cap": m["conjectured_cap"],
				"hits_cap": m["hits_cap"],
				"hjsw": m["hjsw"],
				"best_over_hjsw": m["best_over_hjsw"],
				"asymp_2p_over_3pm1": m["asymp_2p_over_3p"],
				"majority": m["best"],
				"minority": 0,
				"surplus": m["best"] - m["hjsw"],
				"floor_m_over_3": 0,
				"b2_actual": "",
				"b2_forced_by_mono_cap": "",
				"surplus_if_M_at_cap": "",
			}
		)

	forced = 0
	actual = 0
	multi_n = 0
	for p in primes_from_to(max(args.lo, 17), min(args.hi, 79)):
		for C in default_residue_sets(p):
			if len(C) < 2:
				continue
			row = analyze_reduction(p, C, bnb_s=min(1.0, args.bnb), seed=p)
			chk = b2_from_mono_cap_alone(row["majority"], row["minority"], p)
			multi_n += 1
			actual += int(row["b2_m3_ge_surplus"])
			forced += int(chk["b2_forced_by_cap"])
			writer.writerow(
				{
					"kind": "multih",
					"p": p,
					"residues": row["residues"],
					"row_col_automatic": int(row_col_automatic(p)),
					"mono_best": "",
					"conjectured_cap": conjectured_mono_primary_cap(p),
					"hits_cap": "",
					"hjsw": row["hjsw"],
					"best_over_hjsw": "",
					"asymp_2p_over_3pm1": f"{(2 * p) / (3 * (p - 1)):.4f}",
					"majority": row["majority"],
					"minority": row["minority"],
					"surplus": row["surplus"],
					"floor_m_over_3": row["floor_m_over_3"],
					"b2_actual": row["b2_m3_ge_surplus"],
					"b2_forced_by_mono_cap": chk["b2_forced_by_cap"],
					"surplus_if_M_at_cap": chk["surplus_if_M_at_cap"],
				}
			)

	print(
		f"# mono hits conjectured cap {mono_hits}/{mono_n}; "
		f"multih B2 actual {actual}/{multi_n}; "
		f"B2 forced by mono cap alone {forced}/{multi_n}",
		file=sys.stderr,
	)


if __name__ == "__main__":
	main()
