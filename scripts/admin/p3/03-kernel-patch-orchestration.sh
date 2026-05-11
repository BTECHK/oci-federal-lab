#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P3 — Kernel patch orchestration (with health check + rollback)
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: Orchestrate a kernel update with pre-flight checks, app health
#          gating, reboot, post-reboot verification, and rollback path.
#          See docs/exercises/p3/patch-simulation-report.md for the full
#          scenario template; this script is the executable companion.
#
# Usage: sudo ./scripts/admin/p3/03-kernel-patch-orchestration.sh [--dry-run]
#
# Rollback: dnf history rollback <pre-update-transaction-id>
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: Pre-flight ────────────────────────────────────────────────
# WHAT: Check uptime, disk space, currently active services, no in-flight
#       critical operations (e.g., is fedtracker handling traffic right now?).
# LEARNING: Production patching requires "drain" semantics.


# ── Section 2: Capture pre-state ─────────────────────────────────────────
# WHAT: uname -r, dnf history list, aide --check (clean), app /health/deep.


# ── Section 3: dnf update kernel ─────────────────────────────────────────


# ── Section 4: Reboot orchestration ──────────────────────────────────────
# WHAT: shutdown -r with notification window; capture pre-reboot timestamp.


# ── Section 5: Post-reboot verification (run by systemd unit on boot) ────
# WHAT: Verify new kernel running, app healthchecks pass, AIDE clean.


# ── Section 6: Rollback (manual trigger if verification fails) ───────────
# WHAT: dnf history rollback to pre-update transaction; reboot to old kernel.
