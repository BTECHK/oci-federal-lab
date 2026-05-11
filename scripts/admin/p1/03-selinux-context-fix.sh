#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P1 — SELinux context fix helper
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: Common SELinux drift restoration for fedplatform files.
#          Uses restorecon + semanage fcontext for persistent fixes.
#
# Usage: sudo ./scripts/admin/p1/03-selinux-context-fix.sh
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: Check getenforce state ────────────────────────────────────
# WHAT: Verify SELinux is enforcing; warn if permissive or disabled.


# ── Section 2: Restorecon known paths ────────────────────────────────────
# WHAT: For each fedplatform-managed path, run restorecon -Rv.
# LEARNING: restorecon applies the policy; chcon is one-off and doesn't persist.


# ── Section 3: Capture recent AVC denials ────────────────────────────────
# WHAT: ausearch -m avc -ts recent → if any, suggest audit2allow workflow.
