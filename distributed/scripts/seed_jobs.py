"""Seed the coordinator job queue."""

from __future__ import annotations

import argparse

import httpx


def main() -> None:
	"""POST /jobs/seed with optional filters."""
	parser = argparse.ArgumentParser()
	parser.add_argument("--server", default="http://127.0.0.1:8000")
	parser.add_argument("--max-jobs", type=int, default=12)
	parser.add_argument("--time-limit", type=int, default=15)
	args = parser.parse_args()
	body = {
		"max_jobs": args.max_jobs,
		"time_limit_s": args.time_limit,
		"families": ["hjsw", "hjsw_augment", "algebraic_addable"],
		"seeds": [0],
		"primes": [5, 7, 17, 19],
	}
	r = httpx.post(f"{args.server}/jobs/seed", json=body, timeout=60.0)
	r.raise_for_status()
	print(r.json())


if __name__ == "__main__":
	main()
