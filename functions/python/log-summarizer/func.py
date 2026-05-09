"""
log-summarizer — Phase 2 OCI Function.
Trigger: OCI Events scheduled (daily 23:00 UTC).
"""
import io
import json
import logging

from fdk import response

logger = logging.getLogger(__name__)


# ── Section 1: Connect to ADB and query today's logs ──────────────────
# WHAT: Connect to Oracle Autonomous DB, SELECT * FROM app_logs
#       WHERE created_at > TRUNC(SYSDATE)
# LEARNING: oracledb thin mode, parameterized queries, wallet auth
# LOOK UP: oracledb.connect, oracledb.connect(config_dir=...), context closing
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Build Ollama prompt template ───────────────────────────
# WHAT: Format log entries into a compliance-narrative prompt
# LEARNING: prompt engineering for compliance summaries, severity grouping
# LOOK UP: f-string formatting, json.dumps for structured prompts
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Call Ollama /api/generate ──────────────────────────────
# WHAT: POST {"model": "...", "prompt": "...", "stream": false}
# LEARNING: synchronous HTTP from inside a serverless function, timeout limits
# LOOK UP: requests.post, response.json()["response"]
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Write Markdown to compliance-artifacts/ bucket ─────────
# WHAT: Use OCI Object Storage SDK to upload the narrative as a .md object
# LEARNING: resource principal auth in OCI Functions, put_object signature
# LOOK UP: oci.object_storage.ObjectStorageClient, oci.auth.signers
#
# Write your implementation below. Check answers/ only after attempting.


def handler(ctx, data: io.BytesIO = None):
    """
    Stub. Returns 'not implemented' until learner builds out sections 1-4.
    """
    return response.Response(
        ctx,
        response_data=json.dumps({"status": "not_implemented"}),
        headers={"Content-Type": "application/json"},
    )
