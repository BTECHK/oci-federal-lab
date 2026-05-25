"""
poam-generator — v3 (P3) OCI Function (stretch item).
Trigger: OCI Events on a HIGH-severity finding (or scheduled sweep).
Drafts a POA&M (Plan of Action & Milestones) item from a finding + its classified
control. Air-gapped: drafting uses the local Ollama, no external API.
"""
import io
import json

from fdk import response


# ── Section 1: Parse the finding + classified control ─────────────────
# WHAT: read the trigger payload — a HIGH finding plus the control_id(s) the
#       evidence-collector classifier (ADR-022) assigned to it.
# LEARNING: a POA&M item is anchored to a specific control + a specific weakness;
#       carry both through from classification.
# LOOK UP: data.getvalue(), json.loads; the evidence-collector output shape.
# ADR: adrs/ADR-022-llm-evidence-classification-poam.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Build the POA&M draft prompt (Ollama) ──────────────────
# WHAT: prompt the model to draft the standard POA&M fields: weakness
#       description, source of discovery, affected control_id, proposed
#       remediation, milestones (with dates), resources required, and a
#       scheduled completion. Ask for STRICT JSON.
# LEARNING: a POA&M is a regulator-facing artifact with a fixed shape; constrain
#       the model to those fields, and label the output a DRAFT for human sign-off.
# LOOK UP: f-string prompt with the POA&M field list; json schema in the prompt.
# ADR: adrs/ADR-022-llm-evidence-classification-poam.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Call Ollama /api/generate ──────────────────────────────
# WHAT: POST {"model","prompt","stream":False} to the local Ollama; parse the
#       JSON POA&M draft defensively.
# LEARNING: same synchronous-HTTP-from-a-function pattern as log-summarizer; mind
#       the function timeout vs model latency.
# LOOK UP: requests.post(f"{OLLAMA_URL}/api/generate", ...).json()["response"].
# ADR: adrs/ADR-022-llm-evidence-classification-poam.md
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 4: Persist the draft (Object Storage + poam_items) ────────
# WHAT: write the draft JSON to compliance-artifacts/poam-drafts/{ts}.json, and
#       optionally INSERT a row into the poam_items table marked status='draft'.
# LEARNING: drafts are not final — they wait for human review/sign-off before
#       status becomes 'open'. The poam_items table DDL is YOURS to write (DB track).
# LOOK UP: oci.object_storage.put_object; oracledb INSERT into poam_items.
# ADR: adrs/ADR-022-llm-evidence-classification-poam.md
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
