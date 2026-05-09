"""
Personnel routes — CRUD endpoints for federal personnel records.
"""
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/personnel", tags=["personnel"])


# ── Section 1: List personnel (GET /personnel) ───────────────────────
# WHAT: Return paginated list of personnel records from the DB
# LEARNING: Query parameters with FastAPI Query(), pagination pattern (skip/limit)
# LOOK UP: fastapi.Query, APIRouter, response_model
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Get single personnel record (GET /personnel/{id}) ─────
# WHAT: Fetch one record by ID; raise 404 if not found
# LEARNING: Path parameters, HTTPException, 404 handling
# LOOK UP: fastapi.HTTPException, path parameter type coercion
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Create personnel record (POST /personnel) ─────────────
# WHAT: Insert a new record, return 201 with the new ID
# LEARNING: POST with request body, status_code=201, Pydantic validation
# LOOK UP: fastapi.APIRouter status_code, BaseModel as request body
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Audit log write on every mutation ─────────────────────
# WHAT: Call log_audit() after every CREATE, UPDATE, DELETE
# LEARNING: CMMC AU-2 — every action must be recorded with who/what/when
# LOOK UP: audit log schema, log_audit() signature in database.py
#
# (Implement inside each handler above — this section is a reminder, not a separate function)
