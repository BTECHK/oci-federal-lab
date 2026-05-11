#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P2 — k3s node debug helper
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: Standard debug checklist for a NotReady k3s node. Captures
#          journal, crictl state, disk pressure, cert expiry in one run.
#
# Usage: sudo ./scripts/admin/p2/03-k3s-node-debug.sh [output-dir]
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: journalctl -u k3s -n 200 ─────────────────────────────────


# ── Section 2: crictl ps + crictl pods ───────────────────────────────────


# ── Section 3: disk + memory pressure check ──────────────────────────────


# ── Section 4: kubelet cert expiry ───────────────────────────────────────


# ── Section 5: network reachability (server <-> agent) ───────────────────
