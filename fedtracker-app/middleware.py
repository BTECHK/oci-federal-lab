"""
FedTracker middleware.
Injects a trace ID into every request for distributed tracing.
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ── Section 1: Trace ID generation ──────────────────────────────────
# WHAT: Generate a UUID4 trace ID and attach it to the request state
# LEARNING: FastAPI request state, UUID generation, middleware lifecycle
# LOOK UP: BaseHTTPMiddleware, request.state, uuid.uuid4
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Inject into response headers ──────────────────────────
# WHAT: Add X-Trace-ID header to every response so clients can correlate logs
# LEARNING: Middleware call_next pattern, response headers in FastAPI
# LOOK UP: BaseHTTPMiddleware.dispatch, Response.headers
#
# Write your implementation below. Check answers/ only after attempting.

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pass  # remove this stub when implementing
