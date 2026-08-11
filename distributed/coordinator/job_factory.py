"""Expand (prime, family, seed) triples into coordinator jobs."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

DEFAULT_PRIMES = [
	5, 7, 17, 19, 31, 37, 61, 67, 71, 83, 97, 107, 109, 139, 151, 167, 173, 181, 281,
]
DEFAULT_FAMILIES = ["hjsw", "hjsw_augment", "algebraic_addable", "hyperbola_union"]
DEFAULT_SEEDS = [0, 1, 2]


def expand_jobs(
	primes: Optional[Iterable[int]] = None,
	families: Optional[Iterable[str]] = None,
	seeds: Optional[Iterable[int]] = None,
	time_limit_s: int = 50,
	max_jobs: Optional[int] = None,
) -> List[Dict]:
	"""Create one job dict per (prime, family, seed) — natural shard key."""
	primes = list(primes) if primes is not None else list(DEFAULT_PRIMES)
	families = list(families) if families is not None else list(DEFAULT_FAMILIES)
	seeds = list(seeds) if seeds is not None else list(DEFAULT_SEEDS)
	jobs: List[Dict] = []
	for p in primes:
		for family in families:
			for seed in seeds:
				jobs.append(
					{
						"job_id": f"{family}-p{p}-s{seed}",
						"family": family,
						"params": {
							"p": p,
							"n": 2 * p,
							"seed": seed,
							"c": 1,
							"time_limit_s": time_limit_s,
						},
					}
				)
				if max_jobs is not None and len(jobs) >= max_jobs:
					return jobs
	return jobs
