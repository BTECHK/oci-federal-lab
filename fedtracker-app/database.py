"""
FedTracker database connection.
Supports SQLite (local/dev) and Oracle Autonomous DB (production OCI).
"""
import os
import sqlite3


DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/opt/fedtracker/fedtracker.db")


# ── Section 1: SQLite connection ─────────────────────────────────────
# WHAT: Open a SQLite connection in WAL mode and return it
# LEARNING: sqlite3.connect, row_factory, PRAGMA journal_mode=WAL (why it matters for concurrency)
# LOOK UP: sqlite3.Row, PRAGMA journal_mode
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Oracle Autonomous DB connection ───────────────────────
# WHAT: Open an oracledb connection using environment-variable credentials and a wallet
# LEARNING: OCI ADB connection via wallet (mTLS), connection pooling considerations
# LOOK UP: oracledb.connect, OCI wallet directory structure, ORACLE_DSN format
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: get_db() dependency ──────────────────────────────────
# WHAT: Router-level dependency that returns a DB connection based on DB_TYPE
# LEARNING: FastAPI dependency injection pattern — why use Depends(get_db) over a global
# LOOK UP: FastAPI Depends, contextmanager pattern for DB lifecycle
#
# Write your implementation below. Check answers/ only after attempting.
def get_db():
    pass  # remove this stub when implementing
