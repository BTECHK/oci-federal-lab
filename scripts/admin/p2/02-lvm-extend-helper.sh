#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P2 — LVM extend helper (safe online extension)
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: Safely extend an LV + filesystem online. Pre-flight checks
#          ensure VG has free space; post-extend verifies filesystem.
#
# Usage: sudo ./scripts/admin/p2/02-lvm-extend-helper.sh <lv-name> <size>
#        Example: sudo ./scripts/admin/p2/02-lvm-extend-helper.sh data-lv 5G
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: Pre-flight (VG free space, FS type, mount state) ──────────


# ── Section 2: lvextend + resize2fs (or xfs_growfs) ──────────────────────


# ── Section 3: Verify (lvs, df, fs integrity check) ──────────────────────
