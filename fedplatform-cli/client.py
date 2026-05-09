"""
FedTracker API HTTP client.
Wraps requests to the FedTracker API and FedAgent metrics endpoint.
"""
import os
import requests

FEDTRACKER_URL = os.environ.get("FEDTRACKER_URL", "http://localhost:8000")
FEDAGENT_URL = os.environ.get("FEDAGENT_URL", "http://localhost:9100")


# ── Section 1: Base URL configuration ───────────────────────────────
# WHAT: Read FEDTRACKER_URL and FEDAGENT_URL from environment; provide defaults
# LEARNING: 12-factor app config pattern — never hardcode service URLs in source
# LOOK UP: os.environ.get, environment variable documentation
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: GET /personnel ────────────────────────────────────────
# WHAT: Fetch personnel list from FedTracker; return list of dicts
# LEARNING: requests.get, response.raise_for_status(), response.json()
# LOOK UP: requests.Response, HTTP status codes, raise_for_status
#
# Write your implementation below. Check answers/ only after attempting.
def get_personnel(clearance: str = None) -> list:
    pass


# ── Section 3: POST /audit/export ───────────────────────────────────
# WHAT: Trigger an audit log export; return the Object Storage pointer JSON
# LEARNING: POST with no body, JSON response parsing
# LOOK UP: requests.post, requests.Response.json
#
# Write your implementation below. Check answers/ only after attempting.
def trigger_audit_export() -> dict:
    pass


# ── Section 4: GET /health/deep ──────────────────────────────────────
# WHAT: Call the deep health check endpoint; return component status dict
# LEARNING: Handling non-200 status codes gracefully (503 = degraded, not error)
# LOOK UP: requests.get, response.status_code
#
# Write your implementation below. Check answers/ only after attempting.
def get_health() -> dict:
    pass


# ── Section 5: Scrape FedAgent /metrics ─────────────────────────────
# WHAT: Fetch Prometheus text format from FedAgent; parse oscap_score line
# LEARNING: Prometheus text exposition format, string parsing without a library
# LOOK UP: prometheus text format spec, str.startswith, str.split
#
# Write your implementation below. Check answers/ only after attempting.
def get_compliance_score(framework: str = "fedramp") -> float:
    pass
