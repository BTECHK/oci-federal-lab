"""
evidence-collector — Phase 3 OCI Function.
Trigger: OCI Events on object created in scan-results/ bucket.
"""
import io
import json

from fdk import response


# ── Section 1: Parse OCI Events notification ──────────────────────────
# WHAT: Decode the trigger event, extract bucket name + object name
# LEARNING: OCI Events notification schema, JSON parsing in serverless
# LOOK UP: data.getvalue, json.loads, event["data"]["resourceName"]
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Download scan results ──────────────────────────────────
# WHAT: Use OCI Object Storage client to GET the scan-results object
# LEARNING: resource principal auth in functions, get_object response
# LOOK UP: oci.object_storage.ObjectStorageClient.get_object
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Map findings to CMMC controls ──────────────────────────
# WHAT: For each finding, look up the impacted CMMC control(s) using a
#       static lookup table (or fetch from FedTracker /compliance/controls)
# LEARNING: cross-walking technical findings to compliance controls
# LOOK UP: dict-of-list lookup, severity → control ID mapping
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Bundle the evidence package ────────────────────────────
# WHAT: Build evidence-TIMESTAMP/{scan.json, controls.json, audit.csv,
#       manifest.json} as multiple objects (or a ZIP)
# LEARNING: package layout for downstream auditors, manifest pattern
# LOOK UP: zipfile, io.BytesIO, multi-part Object Storage layouts
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 5: Write package to compliance-artifacts/ bucket ──────────
# WHAT: Upload each artifact (or the ZIP) under evidence-TIMESTAMP/ prefix
# LEARNING: prefix-based bucket organization, content-type per artifact
# LOOK UP: oci.object_storage.put_object, content_type parameter
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 6 (v3): LLM-assisted control classification (Ollama) ──────
# WHAT: replace/augment Section 3's STATIC finding->control lookup with a local
#       Ollama classifier. For each finding (CVE, severity, asset), prompt the
#       model to assign the most relevant NIST 800-53 / CMMC control family +
#       control_id(s) with a confidence score and a one-line rationale. Keep the
#       static table as a deterministic fallback when confidence is low.
# LEARNING: the original stub ("every High finding maps to every control") is
#       noise an auditor won't trust; an LLM classifier yields a specific,
#       defensible mapping. Air-gap holds — same local Ollama as log-summarizer,
#       no external API.
# LOOK UP: requests.post(f"{OLLAMA_URL}/api/generate", json={"model","prompt",
#       "stream":False}) returning STRICT JSON {control_ids, family, confidence,
#       rationale}; parse defensively; threshold via env CLASSIFY_MIN_CONFIDENCE.
# ADR: adrs/ADR-022-llm-evidence-classification-poam.md
#
# Write your implementation below. Check answers/ only after attempting.


def handler(ctx, data: io.BytesIO = None):
    return response.Response(
        ctx,
        response_data=json.dumps({"status": "not_implemented"}),
        headers={"Content-Type": "application/json"},
    )
