#!/usr/bin/env bash
# Local smoke demo: coordinator + seed + worker + leaderboard + reject fake claim.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT"
export NTIL_DB_PATH="/tmp/ntil_demo.sqlite3"
rm -f "$NTIL_DB_PATH"

python3 -m uvicorn coordinator.server:app --host 127.0.0.1 --port 8000 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT
sleep 2

python3 "$ROOT/scripts/seed_jobs.py" --server http://127.0.0.1:8000 --max-jobs 6 --time-limit 8
python3 -m worker.client --server http://127.0.0.1:8000 --worker-id demo-1 --max-jobs 3

echo "=== leaderboard ==="
curl -sS "http://127.0.0.1:8000/leaderboard" | python3 -m json.tool | head -40

echo "=== fake collinear claim (expect 400) ==="
curl -sS -o /tmp/ntil_fake.json -w "%{http_code}\n" -X POST "http://127.0.0.1:8000/claims" \
	-H 'Content-Type: application/json' \
	-d '{"n":3,"points":[[1,1],[2,2],[3,3]],"worker_id":"attacker"}'
cat /tmp/ntil_fake.json; echo
