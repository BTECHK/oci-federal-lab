#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# INC-002 Prevention: OpenSCAP Compliance Regression Check
# Incident: phases/phase-2-fedanalytics-dr/INCIDENTS.md → INC-002
# Postmortem: phases/phase-2-fedanalytics-dr/postmortems/INC-002-*.md
#
# Purpose: Detect OpenSCAP score regression before it persists post-update.
#          Compares the current score against the recorded baseline; fails
#          if the score has dropped by more than the allowed delta.
#
# Usage: ./scripts/INC-002-oscap-regression.sh [--max-drop N]
#   --max-drop N: allowed drop (default 5 points)
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

BASELINE_FILE="${OSCAP_BASELINE_FILE:-/opt/fedtracker/oscap-baseline.txt}"
OVAL_CONTENT="${OVAL_CONTENT:-/usr/share/xml/scap/ssg/content/ssg-ol9-oval.xml}"
RESULTS_FILE="${OSCAP_RESULTS:-/tmp/oscap-regression-results.xml}"
MAX_DROP=5

if [[ "${1:-}" == "--max-drop" && -n "${2:-}" ]]; then
    MAX_DROP=$2
fi

if [[ ! -f "$BASELINE_FILE" ]]; then
    echo "INC-002: ERROR — baseline file missing: $BASELINE_FILE" >&2
    echo "INC-002: run a clean oscap, then write the score to $BASELINE_FILE" >&2
    exit 1
fi

baseline=$(cat "$BASELINE_FILE")

# Run oscap (degrades gracefully if binary missing)
if ! command -v oscap >/dev/null 2>&1; then
    echo "INC-002: ERROR — oscap binary not found" >&2
    exit 1
fi

set +e
oscap oval eval --results "$RESULTS_FILE" "$OVAL_CONTENT" >/dev/null 2>&1
set -e

# Parse pass/fail counts to compute score
pass=$(grep -c "<result>true</result>" "$RESULTS_FILE" 2>/dev/null || echo 0)
fail=$(grep -c "<result>false</result>" "$RESULTS_FILE" 2>/dev/null || echo 0)
total=$((pass + fail))

if (( total == 0 )); then
    echo "INC-002: ERROR — could not parse oscap results from $RESULTS_FILE" >&2
    exit 1
fi

current=$(( pass * 100 / total ))
delta=$(( baseline - current ))

echo "INC-002: baseline=$baseline current=$current delta=$delta"

if (( delta > MAX_DROP )); then
    echo "INC-002: REGRESSION — score dropped $delta points (> $MAX_DROP allowed)" >&2
    exit 1
fi

echo "INC-002: score within tolerance — safe to proceed"
exit 0
