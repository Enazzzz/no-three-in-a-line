"""Volunteer worker: lease job → solve → upload claim."""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict

import httpx

from ntil.solvers import run_family


def run_once(server: str, worker_id: str) -> bool:
	"""Pull at most one job and submit a claim. Return True if a job ran."""
	with httpx.Client(base_url=server, timeout=120.0) as client:
		resp = client.get("/jobs/next", params={"worker_id": worker_id})
		resp.raise_for_status()
		job = resp.json().get("job")
		if not job:
			return False
		family = job["family"]
		params: Dict[str, Any] = dict(job.get("params") or {})
		params.setdefault("time_limit_s", job.get("time_limit_s", 50))
		result = run_family(family, params)
		claim = {
			"job_id": job["job_id"],
			"n": result["n"],
			"points": result["points"],
			"size": result["size"],
			"ratio": result["ratio"],
			"family": result["family"],
			"params": result["params"],
			"stats": result["stats"],
			"worker_id": worker_id,
		}
		cr = client.post("/claims", json=claim)
		# 400 means rejected (still recorded); other errors raise.
		if cr.status_code not in (200, 400):
			cr.raise_for_status()
		print(worker_id, job["job_id"], cr.status_code, cr.json())
		return True


def main() -> None:
	"""CLI entrypoint."""
	parser = argparse.ArgumentParser(description="NTIL volunteer worker")
	parser.add_argument("--server", default="http://127.0.0.1:8000")
	parser.add_argument("--worker-id", required=True)
	parser.add_argument("--max-jobs", type=int, default=1)
	parser.add_argument("--loop", action="store_true", help="Keep polling when idle")
	parser.add_argument("--idle-sleep", type=float, default=2.0)
	args = parser.parse_args()

	done = 0
	while done < args.max_jobs:
		ran = run_once(args.server, args.worker_id)
		if ran:
			done += 1
			continue
		if not args.loop:
			break
		time.sleep(args.idle_sleep)


if __name__ == "__main__":
	main()
