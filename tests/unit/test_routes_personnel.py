"""
Unit tests for FedTracker personnel routes.
Tests the /personnel endpoints for CRUD operations and validation.
"""
import pytest


# ── Section 1: Test POST /personnel — happy path ───────────────────
# WHAT: Send a valid PersonnelCreate payload, assert 201 response with an id field
# LEARNING: TestClient.post with JSON body, status code assertions
# LOOK UP: TestClient.post(json=...), response.status_code, response.json()
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Test POST /personnel — invalid data ─────────────────
# WHAT: Send a payload missing required fields (e.g. no name), assert 422 Unprocessable Entity
# LEARNING: FastAPI auto-validates against Pydantic models and returns 422 with error details
# LOOK UP: FastAPI validation error response format, 422 status code
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Test GET /personnel/{id} — found and not found ──────
# WHAT: Create a record via POST, then GET it by id (200). Also GET a non-existent id (404).
# LEARNING: Testing dependent operations — create then read pattern, HTTP 404 semantics
# LOOK UP: TestClient.get, HTTPException(status_code=404), response detail field
#
# Write your implementation below. Check answers/ only after attempting.
