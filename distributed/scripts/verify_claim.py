"""Offline re-verification of a claim JSON file.

Run with: PYTHONPATH=distributed python scripts/verify_claim.py claim.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ntil.verify import certificate_hash, verify_claim


def main() -> None:
	"""Load claim JSON and print verification result."""
	parser = argparse.ArgumentParser()
	parser.add_argument("path", type=Path)
	args = parser.parse_args()
	claim = json.loads(args.path.read_text())
	ok, reason = verify_claim(int(claim["n"]), claim["points"])
	print({"ok": ok, "reason": reason, "cert": certificate_hash(claim)})


if __name__ == "__main__":
	main()
