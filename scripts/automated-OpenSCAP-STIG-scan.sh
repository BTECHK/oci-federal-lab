#!/bin/bash
# =============================================================================
# DISA STIG Scanner — runs OpenSCAP and summarizes results
# Usage: sudo ./stig_scan.sh
# Output: HTML report + console summary
# =============================================================================

TIMESTAMP=$(date -u '+%Y%m%d_%H%M%S')
RESULTS="/tmp/stig-results-${TIMESTAMP}.xml"
REPORT="/tmp/stig-report-${TIMESTAMP}.html"
PROFILE="xccdf_org.ssgproject.content_profile_stig"
CONTENT="/usr/share/xml/scap/ssg/content/ssg-ol9-ds.xml"

echo "=== DISA STIG Scan ==="
echo "Profile: DISA STIG for Oracle Linux 9"
echo "Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Run the scan
oscap xccdf eval \
  --fetch-remote-resources \
  --profile "${PROFILE}" \
  --results "${RESULTS}" \
  --report "${REPORT}" \
  "${CONTENT}" 2>/dev/null

# Parse results
PASS=$(grep -oP '<result[^>]*>\K[^<]+' "${RESULTS}" 2>/dev/null | grep -c '^pass$' || echo 0)
FAIL=$(grep -oP '<result[^>]*>\K[^<]+' "${RESULTS}" 2>/dev/null | grep -c '^fail$' || echo 0)
NOTAPPLICABLE=$(grep -oP '<result[^>]*>\K[^<]+' "${RESULTS}" 2>/dev/null | grep -c '^notapplicable$' || echo 0)
TOTAL=$((PASS + FAIL))

echo "=== Results ==="
echo "  Passed:         ${PASS}"
echo "  Failed:         ${FAIL}"
echo "  Not Applicable: ${NOTAPPLICABLE}"
echo "  Total Checked:  ${TOTAL}"
if [ "${TOTAL}" -gt 0 ]; then
    SCORE=$(( PASS * 100 / TOTAL ))
    echo "  Score:          ${SCORE}%"
fi
echo ""
echo "  HTML Report:    ${REPORT}"
echo "  XML Results:    ${RESULTS}"
echo ""
echo "Completed: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
SCANEOF

chmod +x /opt/fedtracker/stig_scan.sh