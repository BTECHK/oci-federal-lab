#!/usr/bin/env python3
"""
Seed data generator for FedPlatform Oracle ADB.

Generates Faker-based synthetic data and bulk-inserts into the user-written schema.
Reads DATABASE_URL env var for ADB connection (with wallet path via TNS_ADMIN).

Usage:
    python generate.py --rows-personnel 50 --rows-audit 500

The complete reference implementation lives in `answers/generate.py` (gitignored).
Try to implement each section yourself first; check answers/ only if stuck.
"""

import os
import click

# ── Section 1: Oracle ADB connection setup ─────────────────────────────
# WHAT: Open a connection pool to Oracle ADB using oracledb thin client.
# LEARNING: Connection pooling vs single connection; ADB wallet auth; thin mode vs thick mode.
# LOOK UP: oracledb.create_pool, oracledb.init_oracle_client, TNS_ADMIN env, wallet location.
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Faker providers + seed reproducibility ───────────────────
# WHAT: Initialize Faker with a fixed seed so repeated runs produce the same data.
# LEARNING: Deterministic test data; locale selection; custom providers for domain-specific data.
# LOOK UP: faker.Faker, faker.Faker.seed_instance, faker.providers.* (especially internet, person).


# ── Section 3: personnel table generator ────────────────────────────────
# WHAT: Generate N personnel rows with realistic federal-employee-shaped data.
# LEARNING: Schema-driven generation; respecting CHECK constraints from user's DDL; bulk insert performance.
# LOOK UP: cursor.executemany, oracledb.array DML, batch_size tuning.


# ── Section 4: audit_log table generator ────────────────────────────────
# WHAT: Generate N audit_log rows. Must reference valid personnel.id values (FK).
# LEARNING: Foreign-key-respecting generation; mixing realistic action types; timestamp distributions.
# LOOK UP: pseudo-random selection from a queried list of valid PKs.


# ── Section 5: app_logs table generator (P2+) ───────────────────────────
# WHAT: Generate N app_logs rows with varied severity distribution.
# LEARNING: Skewed distributions (most logs INFO, few ERROR); JSONB payload generation.
# LOOK UP: random.choices with weights, json.dumps on Faker-generated dicts.


# ── Section 6: CLI entrypoint ───────────────────────────────────────────
# WHAT: Click-based CLI that accepts row counts and orchestrates generators.
# LEARNING: Click options vs arguments, progress reporting with click.progressbar.
# LOOK UP: click.command, click.option, click.echo, click.progressbar.

@click.command()
@click.option('--rows-personnel', default=50, help='Personnel rows to generate')
@click.option('--rows-audit', default=500, help='Audit log rows to generate')
@click.option('--rows-applogs', default=0, help='App log rows to generate (P2+)')
def main(rows_personnel, rows_audit, rows_applogs):
    """Seed FedPlatform ADB with synthetic data."""
    click.echo(f"Seeding {rows_personnel} personnel, {rows_audit} audit, {rows_applogs} app_logs...")
    # Wire up sections 1-5 here.
    # Check answers/generate.py for reference.


if __name__ == '__main__':
    main()
