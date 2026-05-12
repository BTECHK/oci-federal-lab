"""
Unit tests for FedTracker database module.
Tests SQLite connection, WAL mode, and basic CRUD operations.
"""
import pytest


# ── Section 1: Test get_db returns a working connection ─────────────
# WHAT: Call get_db() and verify it returns a connection that can execute a simple query
# LEARNING: Testing database connectivity, sqlite3.Row row factory
# LOOK UP: sqlite3.connect, conn.execute("SELECT 1"), conn.row_factory
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Test SQLite WAL mode is enabled ──────────────────────
# WHAT: Query PRAGMA journal_mode on the connection and assert it returns "wal"
# LEARNING: WAL mode enables concurrent reads during writes — required for web apps
# LOOK UP: PRAGMA journal_mode, sqlite3 PRAGMA queries, WAL vs rollback journal
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Test basic CRUD round-trip ───────────────────────────
# WHAT: Insert a personnel record, read it back, verify the data matches
# LEARNING: End-to-end DB test — INSERT then SELECT, parameterized queries
# LOOK UP: cursor.execute with ?, cursor.lastrowid, fetchone()
#
# Write your implementation below. Check answers/ only after attempting.
