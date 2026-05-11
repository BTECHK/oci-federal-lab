#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Admin P1 — SSH hardening validator
# Created: 2026-05-10 (v2 addendum)
#
# Purpose: Validate sshd_config against CIS Benchmark for Oracle Linux 9.
#          Runs `sshd -T` to fetch runtime config, compares against expected
#          hardened values, exits 0 if compliant, 1 with diff if not.
#
# Usage: sudo ./scripts/admin/p1/01-ssh-hardening-validate.sh
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Section 1: Expected hardened values ─────────────────────────────────
# WHAT: Define the expected hardened sshd_config values per CIS OL9.
# LEARNING: Which sshd options are security-relevant and why.
# LOOK UP: CIS OL9 Benchmark sections 5.2.x, sshd_config(5).
#
# Write your implementation below.


# ── Section 2: Capture current runtime config ────────────────────────────
# WHAT: Run `sshd -T` to get the runtime view (which may differ from file).
# LEARNING: Why runtime !== file (drop-ins, /etc/ssh/sshd_config.d/, defaults).


# ── Section 3: Compare + report ──────────────────────────────────────────
# WHAT: For each expected value, check actual; collect mismatches.


# ── Section 4: Exit code + output ────────────────────────────────────────
# WHAT: Exit 0 if compliant, 1 with structured mismatch report.
