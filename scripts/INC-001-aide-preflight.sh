#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# INC-001 Prevention: AIDE Integrity Pre-flight Check
# Incident: phases/phase-1-fedtracker-migration/INCIDENTS.md → INC-001
# Postmortem: phases/phase-1-fedtracker-migration/postmortems/INC-001-*.md
#
# Purpose: Verify AIDE file integrity before deployment. Blocks deploy if
#          changes detected. Created after INC-001: unauthorized binary
#          detected post-deploy.
#
# Usage: ./scripts/INC-001-aide-preflight.sh [--strict]
#   --strict: also fail if aide.db is older than 1 hour
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

AIDE_DB="${AIDE_DB:-/var/lib/aide/aide.db.gz}"
MAX_DB_AGE_HOURS_DEFAULT=24
MAX_DB_AGE_HOURS_STRICT=1

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
    STRICT=1
fi

if [[ $STRICT -eq 1 ]]; then
    MAX_DB_AGE_HOURS=$MAX_DB_AGE_HOURS_STRICT
else
    MAX_DB_AGE_HOURS=$MAX_DB_AGE_HOURS_DEFAULT
fi

# ── Stale-baseline guard ────────────────────────────────────────────────
if [[ ! -f "$AIDE_DB" ]]; then
    echo "AIDE: ERROR — baseline database not found at $AIDE_DB" >&2
    echo "AIDE: run 'aide --init' to create the baseline before deploying." >&2
    exit 1
fi

db_age_seconds=$(( $(date +%s) - $(stat -c %Y "$AIDE_DB") ))
db_age_hours=$(( db_age_seconds / 3600 ))

if (( db_age_hours > MAX_DB_AGE_HOURS )); then
    echo "AIDE: ERROR — baseline is ${db_age_hours}h old (max allowed: ${MAX_DB_AGE_HOURS}h)" >&2
    echo "AIDE: run 'aide --update && cp /var/lib/aide/aide.db.new.gz $AIDE_DB' to refresh." >&2
    exit 1
fi

# ── Integrity check ─────────────────────────────────────────────────────
set +e
aide_output=$(aide --check 2>&1)
aide_exit=$?
set -e

# AIDE exits 0 = clean, non-zero = differences detected
if [[ $aide_exit -ne 0 ]]; then
    echo "AIDE: WARNING — file integrity violations detected" >&2
    echo "AIDE: changed entries follow:" >&2
    echo "$aide_output" | grep -E "^(changed|added|removed):" >&2 || echo "$aide_output" >&2
    echo "AIDE: blocking deployment. Investigate before retrying." >&2
    exit 1
fi

echo "AIDE: integrity verified — safe to deploy"
exit 0
