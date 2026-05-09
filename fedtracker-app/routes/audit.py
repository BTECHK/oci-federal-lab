"""
Audit log routes.
"""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/audit", tags=["audit"])


# ── Section 1: List audit log (GET /audit) ───────────────────────────
# WHAT: Return recent audit entries with optional date range filtering
# LEARNING: Optional Query parameters, dynamic SQL WHERE clause construction
# LOOK UP: typing.Optional with FastAPI Query, parameterized SQL
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Export audit log (POST /audit/export) ─────────────────
# WHAT: Build a CSV from audit_log rows and upload it to OCI Object Storage
# LEARNING: Instance Principal auth, OCI Object Storage put_object, CSV generation in memory
# LOOK UP: oci.auth.signers.InstancePrincipalsSecurityTokenSigner, io.StringIO, csv.writer
#
# Write your implementation below. Check answers/ only after attempting.
