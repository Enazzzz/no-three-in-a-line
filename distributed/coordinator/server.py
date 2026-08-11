"""FastAPI coordinator: jobs, claims (independently verified), leaderboard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from coordinator.job_factory import expand_jobs
from coordinator.store import Store
from ntil.verify import certificate_hash, verify_claim

_DEFAULT_DB = os.environ.get("NTIL_DB_PATH", "/tmp/ntil_coordinator.sqlite3")
_WEB_DIR = Path(__file__).resolve().parent.parent / "web"

store = Store(_DEFAULT_DB)
app = FastAPI(
	title="NTIL Volunteer Coordinator",
	description=(
		"No-three-in-line volunteer compute. "
		"Workers are never trusted: every claim is re-verified before leaderboard."
	),
	version="0.1.0",
)


class SeedRequest(BaseModel):
	"""Body for POST /jobs/seed."""

	primes: Optional[List[int]] = None
	families: Optional[List[str]] = None
	seeds: Optional[List[int]] = Field(default=None, description="RNG/param seeds")
	max_jobs: Optional[int] = None
	time_limit_s: int = 50


class ClaimRequest(BaseModel):
	"""Body for POST /claims."""

	job_id: Optional[str] = None
	n: int
	points: List[List[int]]
	size: Optional[int] = None
	ratio: Optional[float] = None
	family: Optional[str] = None
	params: Optional[Dict[str, Any]] = None
	stats: Optional[Dict[str, Any]] = None
	worker_id: str = "anonymous"


@app.get("/health")
def health() -> Dict[str, str]:
	"""Liveness probe."""
	return {"status": "ok"}


@app.post("/jobs/seed")
def seed_jobs(body: SeedRequest) -> Dict[str, Any]:
	"""Expand primes×families×seeds into the job queue."""
	jobs = expand_jobs(
		primes=body.primes,
		families=body.families,
		seeds=body.seeds,
		time_limit_s=body.time_limit_s,
		max_jobs=body.max_jobs,
	)
	inserted = store.create_jobs(jobs)
	return {"created": inserted, "total_requested": len(jobs)}


@app.get("/jobs/next")
def next_job(worker_id: str = Query(..., min_length=1)) -> Dict[str, Any]:
	"""Lease the next pending job."""
	job = store.lease_next_job(worker_id)
	if job is None:
		return {"job": None}
	return {"job": job}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
	"""Return job row metadata."""
	job = store.get_job(job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="job_not_found")
	return job


@app.post("/claims")
def post_claim(body: ClaimRequest) -> Dict[str, Any]:
	"""Accept a claim only after independent verification."""
	pts = body.points
	size = body.size if body.size is not None else len(pts)
	ratio = body.ratio if body.ratio is not None else (size / body.n if body.n else 0.0)
	ok, reason = verify_claim(body.n, pts)
	payload = body.model_dump()
	payload["size"] = size
	payload["ratio"] = ratio
	cert = certificate_hash(payload)
	cid = store.submit_claim(
		job_id=body.job_id,
		payload=payload,
		n=body.n,
		size=size,
		ratio=ratio,
		verified=ok,
		reject_reason="" if ok else reason,
		cert_hash=cert,
		worker_id=body.worker_id,
	)
	if not ok:
		raise HTTPException(
			status_code=400,
			detail={"verified": False, "reason": reason, "claim_id": cid, "cert_hash": cert},
		)
	return {"verified": True, "claim_id": cid, "cert_hash": cert, "size": size, "ratio": ratio}


@app.get("/leaderboard")
def leaderboard(min_n: int = 0, limit: int = 50) -> Dict[str, Any]:
	"""Verified claims sorted by density."""
	rows = store.leaderboard(min_n=min_n, limit=limit)
	return {"count": len(rows), "entries": rows}


@app.get("/")
def index() -> FileResponse:
	"""Serve the static leaderboard page."""
	return FileResponse(_WEB_DIR / "leaderboard.html")
