"""
Logs routes — Phase 2 application log query endpoint.
"""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/logs", tags=["logs"])


# ── Section 1: GET /logs — query application logs ────────────────────
# WHAT: Return app_logs rows filtered by severity + time window
# LEARNING: query parameter parsing, time window math, SQL parameterization
# LOOK UP: Query() default values, datetime.timedelta parsing, parameterized SQL
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: app_logs schema reference ──────────────────────────────
# Table app_logs(id, created_at, severity, source, message, trace_id)
# severity ∈ {DEBUG, INFO, WARN, ERROR, CRITICAL}
# Filter rules:
#   severity: case-insensitive exact match; default = no filter
#   since: ISO duration like "1h", "30m", "7d"; default = "1h"
#   limit: 1-1000; default 100
