#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P3 — AIDE baseline rebuild (after authorized changes)
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: After a planned change (package install, config update), rebuild
#          the AIDE database so the next daily check doesn't false-alarm.
#          Audits the rebuild itself.
#
# Usage: sudo ./scripts/admin/p3/02-aide-baseline-rebuild.sh [reason]
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: Capture reason + actor for audit log ──────────────────────
# WHAT: aide --update is destructive of the baseline; log who + why.


# ── Section 2: Run aide --check first (capture diff being accepted) ──────


# ── Section 3: aide --update + atomic db swap ────────────────────────────


# ── Section 4: Verify new baseline (aide --check; expect clean) ──────────
