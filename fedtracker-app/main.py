"""
FedTracker API — entry point.

Federal Personnel Tracking Application. CMMC AU-2 compliant audit log.
Database: SQLite (dev) or Oracle Autonomous DB (prod).
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager


# ── Section 1: Imports and application setup ─────────────────────────
# WHAT: Import routers from routes/, create the FastAPI app instance
# LEARNING: FastAPI app factory pattern, APIRouter separation by domain
# LOOK UP: FastAPI(), include_router(), app title/description/version
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Lifespan context manager ─────────────────────────────
# WHAT: Run startup logic (DB init, seed data) before serving requests
# LEARNING: FastAPI lifespan replaces deprecated @app.on_event("startup")
# LOOK UP: contextlib.asynccontextmanager, FastAPI(lifespan=...)
#
# Write your implementation below. Check answers/ only after attempting.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


# ── Section 3: App instance and middleware registration ─────────────
# WHAT: Create app with lifespan, add TraceIDMiddleware, include routers
# LEARNING: Middleware execution order, add_middleware vs decorator
# LOOK UP: app.add_middleware, app.include_router, APIRouter prefix
#
# Write your implementation below. Check answers/ only after attempting.

app = FastAPI(title="FedTracker", version="1.0.0", lifespan=lifespan)


# ── Section 3b (P2): Register ingest + logs routers ─────────────────
# WHAT: Wire up P2 routes — POST /ingest/batch, POST /ingest/webhook,
#       GET /ingest/pipeline/status, GET /logs
# LEARNING: routers compose by domain, each owns its prefix and tags
# LOOK UP: routes/ingest.py and routes/logs.py for the router objects
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Development entry point ──────────────────────────────
# WHAT: Allow running with `python main.py` during development
# LEARNING: uvicorn.run vs gunicorn, __name__ == "__main__" guard
# LOOK UP: uvicorn.run host/port/reload args
#
# Write your implementation below. Check answers/ only after attempting.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
