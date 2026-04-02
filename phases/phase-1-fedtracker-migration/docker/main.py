#!/usr/bin/env python3
"""
FedTracker — Federal Personnel Tracking Application
A FastAPI app demonstrating REST API fundamentals and federal compliance patterns.

Database: SQLite (Day 1 legacy mode) or Oracle Autonomous DB (Day 2+)
Audit: Every action is logged for CMMC AU compliance
Server: uvicorn (ASGI) on port 8000
"""

import os
import csv
import io
import sqlite3
from datetime import datetime, date, timezone
from typing import Optional, List

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


# --- Lifespan (startup/shutdown) ---
# Note: init_db() is defined later in this file (Step 4), but Python doesn't execute
# the lifespan body until the app starts — so the function will exist by then.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts."""
    print(f"[FedTracker] Starting with DB_TYPE={os.environ.get('DB_TYPE', 'sqlite')}")
    if os.environ.get("DB_TYPE", "sqlite") == "sqlite":
        print(f"[FedTracker] SQLite database: {os.environ.get('SQLITE_PATH', '/opt/fedtracker/fedtracker.db')}")
        init_db()
        print("[FedTracker] Database initialized with seed data")
    yield
    print("[FedTracker] Shutting down gracefully")


# Create the FastAPI application instance
# This is like Flask's app = Flask(__name__), but with auto-docs and validation built in
app = FastAPI(
    title="FedTracker",
    description="Federal Personnel Tracking API — CMMC AU compliant",
    version="1.0.0-legacy",
    lifespan=lifespan
)

# --- Configuration ---
# DB_TYPE controls which database backend to use
# Day 1: "sqlite" (default) — file-based, everything on one box
# Day 2+: "oracle" — Oracle Autonomous DB (set via environment variable)
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/opt/fedtracker/fedtracker.db")


# --- Pydantic Models ---
# These classes define the SHAPE of data the API accepts and returns.
# FastAPI uses them to:
#   1. Validate incoming request data automatically
#   2. Generate API documentation with field descriptions
#   3. Serialize response data to JSON

class PersonnelCreate(BaseModel):
    """What the client sends when creating a new personnel record."""
    name: str = Field(..., min_length=1, max_length=200, description="Full name of the person")
    role: str = Field(..., min_length=1, max_length=100, description="Job role or title")
    clearance_level: str = Field(
        default="UNCLASSIFIED",
        description="Security clearance level (UNCLASSIFIED, CONFIDENTIAL, SECRET, TOP SECRET)"
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Project identifier this person is assigned to"
    )


class PersonnelResponse(BaseModel):
    """What the API returns for a personnel record."""
    id: int
    name: str
    role: str
    clearance_level: str
    project_id: Optional[str]
    created_at: str
    updated_at: str


# --- Database Helpers ---

def get_db():
    """Get a database connection based on DB_TYPE."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    elif DB_TYPE == "oracle":
        import oracledb
        conn = oracledb.connect(
            user=os.environ.get("ORACLE_USER", "ADMIN"),
            password=os.environ.get("ORACLE_PASSWORD", ""),
            dsn=os.environ.get("ORACLE_DSN", "fedtrackerdb_low"),
            config_dir=os.environ.get("ORACLE_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_location=os.environ.get("ORACLE_WALLET_DIR", "/opt/oracle/wallet"),
            wallet_password=os.environ.get("ORACLE_WALLET_PASSWORD", "")
        )
        return conn
    else:
        raise ValueError(f"Unknown DB_TYPE: {DB_TYPE}")


def init_db():
    """Create tables if they don't exist (SQLite mode)."""
    if DB_TYPE != "sqlite":
        return
    conn = get_db()
    cursor = conn.cursor()

    # Personnel table — tracks federal employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            clearance_level TEXT DEFAULT 'UNCLASSIFIED',
            project_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit log table — CMMC AU compliance
    # Every action is recorded: who did what, when, and the result
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            details TEXT,
            source_ip TEXT
        )
    """)

    # Seed data — sample personnel records to work with
    cursor.execute("SELECT COUNT(*) FROM personnel")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            ("Ada Lovelace", "Lead Engineer", "TOP SECRET", "PROJ-001"),
            ("Grace Hopper", "Senior Architect", "SECRET", "PROJ-001"),
            ("Alan Turing", "Cryptography Lead", "TOP SECRET/SCI", "PROJ-002"),
            ("Margaret Hamilton", "Software Director", "SECRET", "PROJ-002"),
            ("Katherine Johnson", "Data Analyst", "CONFIDENTIAL", "PROJ-003"),
        ]
        cursor.executemany(
            "INSERT INTO personnel (name, role, clearance_level, project_id) VALUES (?, ?, ?, ?)",
            seed_data
        )
        # Log the seed action
        cursor.execute(
            "INSERT INTO audit_log (action, resource_type, details, source_ip) VALUES (?, ?, ?, ?)",
            ("SEED_DATA", "personnel", "Loaded 5 initial records", "system")
        )

    conn.commit()
    conn.close()


def log_audit(action: str, resource_type: str, resource_id=None, details=None, source_ip="unknown"):
    """Write an entry to the audit log."""
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (action, resource_type, resource_id, details, source_ip) VALUES (?, ?, ?, ?, ?)",
        (action, resource_type, str(resource_id) if resource_id else None, details, source_ip)
    )
    conn.commit()
    conn.close()


# --- API Endpoints ---

@app.get("/health")
def health_check():
    """
    Health check endpoint — used by monitoring scripts, load balancers, and Kubernetes probes.
    Returns service status and database connectivity.
    """
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "fedtracker",
        "version": "1.0.0-legacy",
        "database": {"type": DB_TYPE, "status": db_status},
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }


@app.get("/personnel")
def list_personnel(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum records to return")
):
    """
    List personnel records with pagination.
    Use skip and limit query parameters to page through results.
    Example: /personnel?skip=10&limit=5 returns records 11-15.
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM personnel ORDER BY name LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()

    personnel = [dict(row) for row in rows]
    log_audit("LIST", "personnel", details=f"Retrieved {len(personnel)} records (skip={skip}, limit={limit})")

    return {"count": len(personnel), "skip": skip, "limit": limit, "personnel": personnel}


@app.post("/personnel", status_code=201)
def create_personnel(person: PersonnelCreate):
    """
    Create a new personnel record.
    Requires name and role. Clearance level defaults to UNCLASSIFIED.
    Returns 201 Created with the new record's ID.
    """
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO personnel (name, role, clearance_level, project_id) VALUES (?, ?, ?, ?)",
        (person.name, person.role, person.clearance_level, person.project_id)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit("CREATE", "personnel", resource_id=new_id,
              details=f"Added {person.name} ({person.role})")

    return {"message": "Personnel record created", "id": new_id}


@app.get("/personnel/{person_id}")
def get_personnel(person_id: int):
    """
    Get a single personnel record by ID.
    Returns 404 if the record doesn't exist.
    """
    conn = get_db()
    row = conn.execute("SELECT * FROM personnel WHERE id = ?", (person_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Personnel record {person_id} not found")

    log_audit("READ", "personnel", resource_id=person_id)
    return dict(row)


@app.get("/audit")
def get_audit_log(
    limit: int = Query(default=50, ge=1, le=500, description="Maximum entries to return"),
    start_date: Optional[str] = Query(default=None, description="Filter entries after this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Filter entries before this date (YYYY-MM-DD)")
):
    """
    View the audit trail — all recorded actions.
    Supports date filtering with start_date and end_date query parameters.
    """
    conn = get_db()

    query = "SELECT * FROM audit_log"
    params = []
    conditions = []

    if start_date:
        conditions.append("timestamp >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("timestamp <= ?")
        params.append(end_date + " 23:59:59")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    entries = [dict(row) for row in rows]
    return {"count": len(entries), "audit_log": entries}


@app.post("/audit/export")
def export_audit_csv():
    """
    Export the audit log as a CSV file.
    Returns a downloadable CSV with all audit entries.
    Used for compliance reporting and evidence collection.
    """
    conn = get_db()
    rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    conn.close()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "action", "resource_type", "resource_id", "details", "source_ip"])
    for row in rows:
        writer.writerow([row["id"], row["timestamp"], row["action"],
                        row["resource_type"], row["resource_id"],
                        row["details"], row["source_ip"]])

    output.seek(0)
    log_audit("EXPORT", "audit_log", details=f"Exported {len(rows)} audit entries as CSV")

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"}
    )


# --- Main Entry Point ---
# Startup logic (init_db) is handled by the lifespan function defined at the top of the file.
# The lifespan pattern replaces the deprecated @app.on_event("startup") decorator.

# This block runs when you execute: python3 main.py
# In production, you'd use: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
