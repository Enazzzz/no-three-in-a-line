"""SQLite job/claim store for the volunteer coordinator."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional


class Store:
	"""Persistent job queue and verified/rejected claims."""

	def __init__(self, path: str) -> None:
		"""Open (or create) the SQLite database at path."""
		self.path = path
		self._conn = sqlite3.connect(path, check_same_thread=False)
		self._conn.row_factory = sqlite3.Row
		self._init_schema()

	def _init_schema(self) -> None:
		"""Create tables if missing."""
		cur = self._conn.cursor()
		cur.executescript(
			"""
			CREATE TABLE IF NOT EXISTS jobs (
				id TEXT PRIMARY KEY,
				family TEXT NOT NULL,
				params_json TEXT NOT NULL,
				status TEXT NOT NULL,
				leased_to TEXT,
				lease_expires REAL,
				created_at REAL NOT NULL
			);
			CREATE TABLE IF NOT EXISTS claims (
				id TEXT PRIMARY KEY,
				job_id TEXT,
				payload_json TEXT NOT NULL,
				n INTEGER,
				size INTEGER,
				ratio REAL,
				verified INTEGER NOT NULL,
				reject_reason TEXT,
				cert_hash TEXT,
				worker_id TEXT,
				created_at REAL NOT NULL
			);
			"""
		)
		self._conn.commit()

	def create_jobs(self, jobs: List[Dict[str, Any]]) -> int:
		"""Insert pending jobs; skip duplicates by id. Return inserted count."""
		cur = self._conn.cursor()
		inserted = 0
		now = time.time()
		for job in jobs:
			jid = job["job_id"]
			try:
				cur.execute(
					"INSERT INTO jobs (id, family, params_json, status, created_at) VALUES (?,?,?,?,?)",
					(jid, job["family"], json.dumps(job["params"]), "pending", now),
				)
				inserted += 1
			except sqlite3.IntegrityError:
				pass
		self._conn.commit()
		return inserted

	def lease_next_job(self, worker_id: str, lease_s: float = 600.0) -> Optional[Dict[str, Any]]:
		"""Lease the next pending (or expired) job to worker_id."""
		cur = self._conn.cursor()
		now = time.time()
		# Requeue expired leases.
		cur.execute(
			"UPDATE jobs SET status='pending', leased_to=NULL, lease_expires=NULL "
			"WHERE status='leased' AND lease_expires < ?",
			(now,),
		)
		row = cur.execute(
			"SELECT * FROM jobs WHERE status='pending' ORDER BY created_at ASC LIMIT 1"
		).fetchone()
		if row is None:
			self._conn.commit()
			return None
		cur.execute(
			"UPDATE jobs SET status='leased', leased_to=?, lease_expires=? WHERE id=?",
			(worker_id, now + lease_s, row["id"]),
		)
		self._conn.commit()
		return {
			"job_id": row["id"],
			"family": row["family"],
			"params": json.loads(row["params_json"]),
			"time_limit_s": json.loads(row["params_json"]).get("time_limit_s", 50),
		}

	def mark_job_done(self, job_id: str) -> None:
		"""Mark a job completed."""
		self._conn.execute("UPDATE jobs SET status='done' WHERE id=?", (job_id,))
		self._conn.commit()

	def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
		"""Return job metadata or None."""
		row = self._conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
		if row is None:
			return None
		return dict(row)

	def submit_claim(
		self,
		*,
		job_id: Optional[str],
		payload: Dict[str, Any],
		n: int,
		size: int,
		ratio: float,
		verified: bool,
		reject_reason: str,
		cert_hash: str,
		worker_id: str,
	) -> str:
		"""Store a claim row; return claim id."""
		cid = str(uuid.uuid4())
		self._conn.execute(
			"INSERT INTO claims (id, job_id, payload_json, n, size, ratio, verified, "
			"reject_reason, cert_hash, worker_id, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
			(
				cid,
				job_id,
				json.dumps(payload),
				n,
				size,
				ratio,
				1 if verified else 0,
				reject_reason,
				cert_hash,
				worker_id,
				time.time(),
			),
		)
		self._conn.commit()
		if verified and job_id:
			self.mark_job_done(job_id)
		return cid

	def leaderboard(self, min_n: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
		"""Return verified claims ordered by ratio then size."""
		rows = self._conn.execute(
			"SELECT * FROM claims WHERE verified=1 AND n>=? "
			"ORDER BY ratio DESC, size DESC, n ASC LIMIT ?",
			(min_n, limit),
		).fetchall()
		out: List[Dict[str, Any]] = []
		for row in rows:
			payload = json.loads(row["payload_json"])
			out.append(
				{
					"claim_id": row["id"],
					"job_id": row["job_id"],
					"n": row["n"],
					"size": row["size"],
					"ratio": row["ratio"],
					"family": payload.get("family"),
					"params": payload.get("params"),
					"cert_hash": row["cert_hash"],
					"worker_id": row["worker_id"],
				}
			)
		return out
