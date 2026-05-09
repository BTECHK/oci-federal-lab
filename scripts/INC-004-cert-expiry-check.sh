#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# INC-004 Prevention: TLS Certificate Expiry Check
# Incident: phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md → INC-004
# Postmortem: phases/phase-3-fedcompliance-gitops-security/postmortems/INC-004-*.md
#
# Purpose: Warn when any TLS cert expires within the warning window.
#          Blocks the pipeline if any cert is expired.
#
# Usage: ./scripts/INC-004-cert-expiry-check.sh [--warn-days N]
#   --warn-days N: warn-and-fail threshold in days (default 30)
#
# Endpoint list comes from $ENDPOINTS (space-separated host:port). Default:
#   ENDPOINTS="lab.local:443 jenkins.lab.local:443 fedtracker.lab.local:443"
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

WARN_DAYS=30
ENDPOINTS="${ENDPOINTS:-lab.local:443 jenkins.lab.local:443 fedtracker.lab.local:443}"

if [[ "${1:-}" == "--warn-days" && -n "${2:-}" ]]; then
    WARN_DAYS=$2
fi

if ! command -v openssl >/dev/null 2>&1; then
    echo "INC-004: ERROR — openssl not found" >&2
    exit 1
fi

now=$(date +%s)
warn=$(( WARN_DAYS * 86400 ))
fail=0

for ep in $ENDPOINTS; do
    host="${ep%:*}"
    port="${ep#*:}"

    expiry=$(echo | openssl s_client -servername "$host" -connect "$ep" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null \
        | sed 's/notAfter=//')

    if [[ -z "$expiry" ]]; then
        echo "INC-004: WARN — could not read cert for $ep" >&2
        continue
    fi

    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || true)
    if [[ -z "$expiry_epoch" ]]; then
        echo "INC-004: WARN — could not parse expiry $expiry for $ep" >&2
        continue
    fi

    days_left=$(( (expiry_epoch - now) / 86400 ))
    echo "INC-004: $ep expires in ${days_left}d ($expiry)"

    if (( expiry_epoch - now <= 0 )); then
        echo "INC-004: BLOCK — $ep is EXPIRED" >&2
        fail=1
    elif (( expiry_epoch - now < warn )); then
        echo "INC-004: BLOCK — $ep expires in less than ${WARN_DAYS}d" >&2
        fail=1
    fi
done

if (( fail == 1 )); then
    exit 1
fi

echo "INC-004: all certs above ${WARN_DAYS}d threshold — safe"
exit 0
