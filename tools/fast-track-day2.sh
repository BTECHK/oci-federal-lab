#!/bin/bash
# =============================================================
# fast-track-day2.sh — Rebuild Day 1 app + apply Day 2 Oracle DB patch
#
# One-shot recovery script for users who lost Day 1 code when the
# legacy server was terminated before pushing to git.
#
# Run on:  app-server (SSH via bastion)
# Run as:  clouduser (sudo for systemd/env file)
# Prereq:  app-server-setup.sh already ran (clouduser, Python 3.11, pip packages exist)
# Usage:   bash fast-track-day2.sh
#
# Creates:
#   /opt/fedtracker/main.py         — Full FedTracker API with Oracle DB support
#   /opt/fedtracker/health_check.sh — Bash health check script
#   /opt/fedtracker/oci_reporter.py — OCI SDK resource reporter
#   /etc/fedtracker/env             — Database credentials (EDIT BEFORE STARTING)
#   /etc/systemd/system/fedtracker.service — systemd unit
#
# After running: edit /etc/fedtracker/env with your actual passwords, then:
#   sudo systemctl restart fedtracker
#   curl http://localhost:8000/health
# =============================================================
set -euo pipefail

echo "=== Fast-Track Day 2 Recovery ==="
echo "Rebuilding Day 1 app code + Oracle DB support on app-server"
echo ""

# --- Verify prerequisites ---
if ! id clouduser &>/dev/null; then
    echo "ERROR: clouduser doesn't exist. Run app-server-setup.sh first."
    exit 1
fi

if ! command -v python3.11 &>/dev/null; then
    echo "ERROR: python3.11 not installed. Run app-server-setup.sh first."
    exit 1
fi

if [ ! -d /opt/fedtracker ]; then
    echo "ERROR: /opt/fedtracker doesn't exist. Run app-server-setup.sh first."
    exit 1
fi

# =============================================================
# 1/5 — Create main.py (Day 1 code + Oracle DB get_db patch)
# =============================================================
echo "=== 1/5 Creating /opt/fedtracker/main.py ==="

cat > /opt/fedtracker/main.py << 'MAINEOF'
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
MAINEOF

echo "  Created main.py (6 endpoints + Oracle DB support)"

# =============================================================
# 2/5 — Create health_check.sh
# =============================================================
echo "=== 2/5 Creating /opt/fedtracker/health_check.sh ==="

cat > /opt/fedtracker/health_check.sh << 'HEALTHEOF'
#!/bin/bash
# =============================================================================
# FedTracker Health Check Script
# Checks: service status, port listening, disk usage, memory usage, app endpoint
# Usage: ./health_check.sh
# Exit codes: 0 = all healthy, 1 = one or more checks failed
# =============================================================================

# Track whether any checks fail
FAILED=0

# --- Check 1: Service Status ---
echo "=== FedTracker Health Report ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

echo -n "[Service]    fedtracker: "
if systemctl is-active --quiet fedtracker; then
    echo "RUNNING ✓"
else
    echo "DOWN ✗"
    FAILED=1
fi

# --- Check 2: Port Listening ---
echo -n "[Port]       8000/tcp:   "
if ss -tlnp | grep -q ':8000 '; then
    echo "LISTENING ✓"
else
    echo "NOT LISTENING ✗"
    FAILED=1
fi

# --- Check 3: Disk Usage ---
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
echo -n "[Disk]       root (/):   "
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "${DISK_USAGE}% used ✓"
else
    echo "${DISK_USAGE}% used ✗ (WARNING: above 80%)"
    FAILED=1
fi

# --- Check 4: Memory Usage ---
MEM_TOTAL=$(free -m | awk 'NR==2 {print $2}')
MEM_AVAILABLE=$(free -m | awk 'NR==2 {print $7}')
MEM_USED_PCT=$(( (MEM_TOTAL - MEM_AVAILABLE) * 100 / MEM_TOTAL ))
echo -n "[Memory]     RAM:        "
if [ "$MEM_USED_PCT" -lt 90 ]; then
    echo "${MEM_USED_PCT}% used (${MEM_AVAILABLE}MB available) ✓"
else
    echo "${MEM_USED_PCT}% used (${MEM_AVAILABLE}MB available) ✗ (WARNING: above 90%)"
    FAILED=1
fi

# --- Check 5: Application Health Endpoint ---
echo -n "[Endpoint]   /health:    "
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "HTTP ${HTTP_CODE} ✓"
else
    echo "HTTP ${HTTP_CODE} ✗"
    FAILED=1
fi

# --- Summary ---
echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "Overall: ALL CHECKS PASSED ✓"
    exit 0
else
    echo "Overall: ONE OR MORE CHECKS FAILED ✗"
    exit 1
fi
HEALTHEOF

chmod +x /opt/fedtracker/health_check.sh
echo "  Created health_check.sh (5 checks)"

# =============================================================
# 3/5 — Create oci_reporter.py (OCI SDK resource reporter)
# =============================================================
echo "=== 3/5 Creating /opt/fedtracker/oci_reporter.py ==="

cat > /opt/fedtracker/oci_reporter.py << 'REPORTEREOF'
#!/usr/bin/env python3
"""
OCI Resource Reporter
Queries OCI APIs to report on compute instances, their status,
and tagging compliance. Run with: python3.11 oci_reporter.py

Requires: python3.11 -m pip install oci
Requires: ~/.oci/config with valid API key authentication
"""

import oci
import sys
from datetime import datetime, timezone

# Load OCI configuration from ~/.oci/config
# This reads your tenancy OCID, user OCID, API key, and region
try:
    config = oci.config.from_file()
    oci.config.validate_config(config)
    print("[OCI Reporter] Configuration loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load OCI config: {e}")
    print("  Fix: Ensure ~/.oci/config exists and has valid credentials")
    sys.exit(1)


def get_compartment_id(config, compartment_name="fedtracker-lab"):
    """Find the compartment OCID by name."""
    identity = oci.identity.IdentityClient(config)
    tenancy_id = config["tenancy"]

    compartments = identity.list_compartments(tenancy_id).data
    for c in compartments:
        if c.name == compartment_name and c.lifecycle_state == "ACTIVE":
            print(f"[OCI Reporter] Found compartment: {c.name} ({c.id[:30]}...)")
            return c.id

    print(f"[WARNING] Compartment '{compartment_name}' not found. Using tenancy root.")
    return tenancy_id


def list_compute_instances(config, compartment_id):
    """List all compute instances in the compartment with details."""
    compute = oci.core.ComputeClient(config)

    instances = compute.list_instances(compartment_id).data
    print(f"\n{'='*60}")
    print(f"  COMPUTE INSTANCES ({len(instances)} found)")
    print(f"{'='*60}")

    for inst in instances:
        # Skip terminated instances
        if inst.lifecycle_state == "TERMINATED":
            continue

        print(f"\n  Name:          {inst.display_name}")
        print(f"  State:         {inst.lifecycle_state}")
        print(f"  Shape:         {inst.shape}")

        # Show shape config (OCPUs and memory) if available
        if inst.shape_config:
            print(f"  OCPUs:         {inst.shape_config.ocpus}")
            print(f"  Memory (GB):   {inst.shape_config.memory_in_gbs}")

        print(f"  AD:            {inst.availability_domain}")
        print(f"  Created:       {inst.time_created.strftime('%Y-%m-%d %H:%M UTC')}")

        # Check for tags (freeform tags)
        if inst.freeform_tags:
            print(f"  Tags:          {inst.freeform_tags}")
        else:
            print(f"  Tags:          ⚠ NONE (untagged resource!)")

    return instances


def check_tagging_compliance(instances):
    """Check if all resources have required tags."""
    print(f"\n{'='*60}")
    print(f"  TAGGING COMPLIANCE CHECK")
    print(f"{'='*60}")

    untagged = []
    for inst in instances:
        if inst.lifecycle_state == "TERMINATED":
            continue
        if not inst.freeform_tags:
            untagged.append(inst.display_name)

    if untagged:
        print(f"\n  ⚠ {len(untagged)} untagged resource(s) found:")
        for name in untagged:
            print(f"    - {name}")
        print(f"\n  Recommendation: Add 'Project', 'Environment', and 'Owner' tags")
        print(f"  to all resources for cost tracking and compliance.")
    else:
        print(f"\n  ✓ All resources are tagged")

    return untagged


def main():
    """Generate the OCI resource report."""
    print(f"\n{'#'*60}")
    print(f"  OCI RESOURCE REPORT")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Region:    {config.get('region', 'unknown')}")
    print(f"{'#'*60}")

    # Find our compartment
    compartment_id = get_compartment_id(config)

    # List compute instances
    instances = list_compute_instances(config, compartment_id)

    # Check tagging compliance
    untagged = check_tagging_compliance(instances)

    # Summary
    active_count = len([i for i in instances if i.lifecycle_state != "TERMINATED"])
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Active instances:    {active_count}")
    print(f"  Untagged resources:  {len(untagged)}")
    print(f"  Region:              {config.get('region')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
REPORTEREOF

echo "  Created oci_reporter.py (OCI SDK resource reporter)"

# =============================================================
# 4/5 — Create systemd service + environment file
# =============================================================
echo "=== 4/5 Creating systemd service + env file ==="

sudo mkdir -p /etc/fedtracker
sudo tee /etc/fedtracker/env > /dev/null << 'ENVEOF'
DB_TYPE=oracle
ORACLE_USER=ADMIN
ORACLE_PASSWORD=YOUR_ADMIN_PASSWORD_HERE
ORACLE_DSN=fedtrackerdb_low
ORACLE_WALLET_DIR=/opt/oracle/wallet
ORACLE_WALLET_PASSWORD=YOUR_WALLET_PASSWORD_HERE
ENVEOF
sudo chmod 600 /etc/fedtracker/env
sudo chown root:root /etc/fedtracker/env

sudo tee /etc/systemd/system/fedtracker.service > /dev/null << 'SVCEOF'
[Unit]
Description=FedTracker Personnel Tracking Application (FastAPI)
After=network.target

[Service]
User=clouduser
Group=clouduser
WorkingDirectory=/opt/fedtracker
EnvironmentFile=/etc/fedtracker/env
ExecStart=/usr/bin/python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
echo "  Service file + env template created"

# =============================================================
# 5/5 — Set ownership
# =============================================================
echo "=== 5/5 Setting ownership ==="
chown clouduser:clouduser /opt/fedtracker/main.py
chown clouduser:clouduser /opt/fedtracker/health_check.sh
chown clouduser:clouduser /opt/fedtracker/oci_reporter.py
echo "  Files owned by clouduser"

echo ""
echo "=============================================="
echo "  Fast-Track Day 2 Recovery Complete"
echo "=============================================="
echo ""
echo "NEXT STEPS:"
echo "  1. Edit /etc/fedtracker/env with your actual passwords:"
echo "     sudo vi /etc/fedtracker/env"
echo "     - Replace YOUR_ADMIN_PASSWORD_HERE with your ADB admin password"
echo "     - Replace YOUR_WALLET_PASSWORD_HERE with your wallet password"
echo ""
echo "  2. Start the service:"
echo "     sudo systemctl enable --now fedtracker"
echo ""
echo "  3. Verify:"
echo "     curl http://localhost:8000/health"
echo "     curl http://localhost:8000/personnel"
echo ""
echo "  4. Continue with the guide at Step 9.5 verification"
echo ""
