#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# INC-003 Prevention: k3s Cluster DR Readiness Check
# Incident: phases/phase-2-fedanalytics-dr/INCIDENTS.md → INC-003
# Postmortem: phases/phase-2-fedanalytics-dr/postmortems/INC-003-*.md
#
# Purpose: Verify k3s cluster health and ADB backup age before DR drills.
#          Blocks the drill if any node is NotReady or the most recent ADB
#          backup is older than the configured threshold.
#
# Usage: ./scripts/INC-003-k3s-dr-readiness.sh [--max-backup-age-hours N]
#   --max-backup-age-hours N: backup freshness ceiling (default 4)
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

MAX_BACKUP_AGE_HOURS=4
ADB_OCID="${ADB_OCID:-}"

if [[ "${1:-}" == "--max-backup-age-hours" && -n "${2:-}" ]]; then
    MAX_BACKUP_AGE_HOURS=$2
fi

# ── Gate 1: every k3s node is Ready ─────────────────────────────────────
if ! command -v kubectl >/dev/null 2>&1; then
    echo "INC-003: ERROR — kubectl not found" >&2
    exit 1
fi

not_ready=$(kubectl get nodes --no-headers 2>/dev/null | awk '$2 != "Ready" {print $1}')
if [[ -n "$not_ready" ]]; then
    echo "INC-003: BLOCK — k3s nodes not Ready:" >&2
    echo "$not_ready" >&2
    exit 1
fi

# ── Gate 2: ADB backup is fresh ─────────────────────────────────────────
if [[ -z "$ADB_OCID" ]]; then
    echo "INC-003: WARN — ADB_OCID not set; skipping backup-age gate"
    echo "INC-003: nodes Ready, drill cleared (without backup-age check)"
    exit 0
fi

if ! command -v oci >/dev/null 2>&1; then
    echo "INC-003: ERROR — oci CLI not found" >&2
    exit 1
fi

last_backup=$(oci db autonomous-database get \
    --autonomous-database-id "$ADB_OCID" \
    --query 'data."time-of-last-backup"' --raw-output)

if [[ -z "$last_backup" || "$last_backup" == "null" ]]; then
    echo "INC-003: BLOCK — could not read time-of-last-backup from ADB" >&2
    exit 1
fi

last_epoch=$(date -d "$last_backup" +%s)
now_epoch=$(date +%s)
age_hours=$(( (now_epoch - last_epoch) / 3600 ))

echo "INC-003: last backup $last_backup (${age_hours}h ago)"

if (( age_hours > MAX_BACKUP_AGE_HOURS )); then
    echo "INC-003: BLOCK — backup is ${age_hours}h old (max allowed: ${MAX_BACKUP_AGE_HOURS}h)" >&2
    exit 1
fi

echo "INC-003: cluster Ready, backup fresh — drill cleared"
exit 0
