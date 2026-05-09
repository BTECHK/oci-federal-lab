"""
Health Checker — OCI Function
Polls FedTracker /health/deep and surfaces per-component status.
"""
import io, json, logging, os
from datetime import datetime, timezone
import requests
from fdk import response

APP_HEALTH_URL = os.environ.get("APP_HEALTH_URL", "http://10.0.2.201:8000/health/deep")
log = logging.getLogger(__name__)


def handler(ctx, data: io.BytesIO = None):
    checked_at = datetime.now(timezone.utc).isoformat() + "Z"
    try:
        r    = requests.get(APP_HEALTH_URL, timeout=10)
        body = r.json()
        verdict  = "HEALTHY" if r.status_code == 200 else "DEGRADED"
        failures = [
            name for name, c in body.get("components", {}).items()
            if not c.get("ok")
        ]
    except requests.exceptions.ConnectionError as e:
        body     = {}
        verdict  = "UNREACHABLE"
        failures = ["connection"]
        log.error("Cannot reach %s: %s", APP_HEALTH_URL, e)

    result = {
        "function":   "health-checker",
        "checked_at": checked_at,
        "target":     APP_HEALTH_URL,
        "verdict":    verdict,
        "components": body.get("components", {}),
        "failures":   failures,
    }
    return response.Response(
        ctx,
        response_data=json.dumps(result),
        headers={"Content-Type": "application/json"},
    )
