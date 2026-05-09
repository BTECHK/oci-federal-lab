"""
Compliance routes — Phase 3 control catalog + scan orchestration.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/compliance", tags=["compliance"])


# ── Section 1: GET /compliance/controls/{framework} ───────────────────
# WHAT: Return the control catalog for a framework (cmmc, fedramp, nist-800-53)
# LEARNING: path parameters with constrained values, embedded reference data
# LOOK UP: Path() with regex, dict lookups, 404 on unknown framework
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: POST /compliance/scan ──────────────────────────────────
# WHAT: Trigger a FedAgent scan, persist a scan record, return job id
# LEARNING: write-side endpoint vs report endpoint, idempotency keys
# LOOK UP: requests.post to FedAgent admin endpoint or oci function invoke
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: GET /compliance/report ─────────────────────────────────
# WHAT: Aggregate the latest scan record + AIDE log + audit summary
# LEARNING: read-only aggregation endpoint, joining across tables
# LOOK UP: SQL JOIN, summary statistics
#
# Write your implementation below. Check answers/ only after attempting.
