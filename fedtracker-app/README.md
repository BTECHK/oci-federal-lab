# FedTracker API

Python FastAPI application for federal personnel and compliance tracking.
Part of FedPlatform — OCI federal compliance evidence platform.

**Run locally:** `uvicorn main:app --reload` (from this directory)
**Deploy:** Ansible copies answers/ contents to /opt/fedtracker/ on the OCI VM

## Patterns exercised
1. FastAPI routing with APIRouter, path parameters, response models
2. Pydantic v2 models with field validation and custom validators
3. SQLite (dev) / Oracle Autonomous DB (prod) dual-backend pattern
4. Immutable audit log (CMMC AU-2 compliance) — every mutation is recorded
5. Deep health check exercising all external dependencies

## Phase evolution
- **P1:** Personnel CRUD + immutable audit log + deep health check + Object Storage export
- **P2:** POST /ingest/batch, POST /webhook (OCI Events receiver), GET /pipeline/status, GET /logs
- **P3:** GET /compliance/controls/{framework}, POST /compliance/scan, POST /evidence/generate

## ADR links
- ADR-013: Instance Principal auth for CLI (same pattern used in POST /audit/export)
