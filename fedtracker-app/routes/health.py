"""
Health check routes.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


# ── Section 1: Shallow health check (GET /health) ────────────────────
# WHAT: Return service status + basic DB connectivity check
# LEARNING: Simple liveness probe — what minimal information a health check needs
# LOOK UP: FastAPI response shape, sqlite3 SELECT 1 as ping
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Deep health check (GET /health/deep) ──────────────────
# WHAT: Probe every external dependency: DB, Object Storage, Ollama, disk
# LEARNING: Dependency graph observability — return per-component status with 200/503
# LOOK UP: oci.auth.signers, ObjectStorageClient.head_bucket, shutil.disk_usage,
#          JSONResponse with custom status_code
#
# Write your implementation below. Check answers/ only after attempting.
