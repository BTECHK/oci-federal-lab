"""
Ingest routes — Phase 2 batch upload + webhook + pipeline status.
"""
from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter(prefix="/ingest", tags=["ingest"])


# ── Section 1: POST /ingest/batch — CSV batch upload ─────────────────
# WHAT: Accept a multipart CSV file, validate headers, insert rows
# LEARNING: FastAPI UploadFile, multipart/form-data, streaming CSV parsing
# LOOK UP: fastapi.UploadFile, csv.DictReader, async file.read()
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: POST /webhook — OCI Events receiver ────────────────────
# WHAT: Accept signed OCI Events notifications (e.g., Object Storage create)
# LEARNING: webhook signature verification, raw request body access
# LOOK UP: Request.body(), HMAC verification (hmac.compare_digest)
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: GET /ingest/pipeline/status ───────────────────────────
# WHAT: Return last batch ingest stats (rows, errors, last_run_at)
# LEARNING: read-only summary endpoint, pulling from a status table
# LOOK UP: SELECT MAX(created_at) FROM ingest_runs
#
# Write your implementation below. Check answers/ only after attempting.
