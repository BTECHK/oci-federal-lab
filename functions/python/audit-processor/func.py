"""
audit-processor — OCI Function (Python)

Trigger: OCI Events on object creation in audit-evidence/ bucket
Action:  Parse CSV → extract action_summary + top_ips → write JSON to audit-evidence-processed/
"""
import csv
import io
import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone

log = logging.getLogger(__name__)
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "audit-evidence-processed")


# ── Section 1: fdk handler and event parsing ─────────────────────────
# WHAT: Define the handler(ctx, data) entry point; parse the OCI Events notification body
# LEARNING: fdk handler signature — ctx (context) and data (BytesIO event body)
# LOOK UP: fdk.response.Response, json.loads, OCI Events notification schema
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Download CSV from Object Storage ──────────────────────
# WHAT: Use OCI Object Storage client with resource principal to GET the uploaded CSV
# LEARNING: Resource Principal auth (no API key), ObjectStorageClient.get_object
# LOOK UP: oci.auth.signers.get_resource_principals_signer, ObjectStorageClient
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Parse CSV rows ────────────────────────────────────────
# WHAT: Read rows with csv.DictReader; compute action_summary and top 5 source IPs
# LEARNING: csv.DictReader, collections.Counter, most_common(N)
# LOOK UP: csv.DictReader, Counter.most_common
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Write JSON artifact ──────────────────────────────────
# WHAT: Upload the structured JSON to audit-evidence-processed/ bucket
# LEARNING: ObjectStorageClient.put_object, JSON serialization, naming convention
# LOOK UP: put_object, json.dumps, object naming (same base name, .json extension)
#
# Write your implementation below. Check answers/ only after attempting.


def handler(ctx, data: io.BytesIO = None):
    """OCI Function entry point. Called by OCI Events on audit-evidence/ object creation."""
    pass  # remove stub when implementing
