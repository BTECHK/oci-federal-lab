# [AGENT HANDOFF] OCI FedPlatform — 4-Quadrant Restructure (Phase 1)

**Repo:** `C:\Users\k_a_s\OneDrive\Desktop\github\oci-federal-lab`
**Execute:** NOW — OCI is the first project in the sequencing order
**Status:** Phase 1 only. P2/P3 evolution points are documented at the bottom but NOT in scope for this execution.

---

## Read This First (Agent Context)

This is a **major restructure** of the OCI Federal Lab repo. The project is being upgraded from a single-app-per-phase model to a **4-quadrant model** where every phase has:
1. A Python server-side app (FastAPI, long-running, evolves across phases)
2. A Go server-side service (metrics exporter/agent, long-running, evolves across phases)
3. A Python serverless function (OCI Function, fresh purpose each phase)
4. A Go serverless function (OCI Function Go runtime, fresh purpose each phase)
5. A Python CLI (cross-phase operator tool, not a quadrant — supporting service)

**Why this change:** The portfolio previously had no evidence of writing application code (only DevOps/infrastructure work). Adding Go + Python apps with the scaffold/answers pedagogy creates coding reps and demonstrates language × deployment model judgment to L5/L6 SRE/backend hiring managers.

**Go does not exist anywhere in this repo.** The prior confirmed language stack was Python, HCL (Terraform), YAML (Ansible), and Bash. No Go files, no go.mod, no Go dependencies exist in any phase. Every Go artifact in this plan is brand new. Do not look for existing Go code to reference.

**Python does exist** in two locations that need to be migrated:
- `phases/phase-1-fedtracker-migration/app/main.py` (~600 LOC FastAPI app — this becomes the answer key)
- `phases/phase-1-fedtracker-migration/functions/audit-processor/func.py` (real working OCI Function — becomes answer key)
- `phases/phase-1-fedtracker-migration/functions/health-checker/func.py` (Python — being replaced by a Go rewrite)

**Staged-fix plans in docs/plans/ are superseded.** The files `staged-fix-42-phase16-evidence-agent.md` and `staged-fix-43-phase17-functions-rewire.md` contain conflicting instructions about the functions paths. Those paths (`phases/phase-1-fedtracker-migration/functions/`) are being restructured. Follow THIS plan only — ignore any conflicting instructions in the staged-fix files.

---

## Current Repo State (What Exists Before Changes)

```
oci-federal-lab/
├── .claude/              ← SESSION-HANDOFF.md, settings.json (do not touch)
├── docs/                 ← ARCHITECTURE-DECISIONS.md, PRD.md, RESTRUCTURE-JOURNAL.md, plans/
├── phases/
│   ├── phase-1-fedtracker-migration/
│   │   ├── ansible/      ← REAL playbooks including deploy_app.yml
│   │   ├── app/          ← REAL main.py (~600 LOC FastAPI) + requirements.txt
│   │   ├── docker/       ← REAL Dockerfile + main.py copy
│   │   ├── functions/
│   │   │   ├── audit-processor/  ← REAL func.py + func.yaml + requirements.txt
│   │   │   └── health-checker/   ← REAL func.py (Python — being REPLACED by Go)
│   │   ├── terraform/    ← REAL .tf files (8 files: network, compute, IAM, events, storage)
│   │   └── docs/         ← implementation-guide.md (live guide, ~8000 lines)
│   ├── phase-2-fedanalytics-dr/  ← mostly empty placeholders
│   └── phase-3-fedcompliance-gitops-security/ ← mostly empty placeholders
├── scripts/              ← cost_estimator.py + shell scripts
├── tools/                ← shell utilities
├── .gitignore            ← needs 3 new entries
├── CLAUDE.md             ← guide authoring instructions (do not touch)
├── CHANGES-STAGING.md    ← guide fix staging (do not touch)
└── PILLAR-MATRIX.md      ← phase coverage matrix
```

**No `adrs/` directory exists** — create it fresh.
**No `fedtracker-app/`, `fedagent/`, `fedplatform-cli/`, `functions/` at repo root** — create all fresh.

---

## Scaffold / Answers Pattern (Universal — Applies to Every File)

Every app, service, and function uses this structure:
- **Tracked source file** = scaffold with section-comment blocks (stubs, not working code)
- **`answers/` directory** = gitignored, contains complete working implementation
- Ansible and Docker deploy from `answers/` on live infrastructure

Section comment format:
```python
# ── Section N: Name ─────────────────────────────────────────────────
# WHAT: what this section does in plain English
# LEARNING: the key concept or pattern being practiced
# LOOK UP: specific APIs, packages, or docs to reference
#
# Write your implementation below. Check answers/ only after attempting.
```

For Go:
```go
// ── Section N: Name ─────────────────────────────────────────────────
// WHAT: what this section does
// LEARNING: the Go concept being practiced
// LOOK UP: specific packages or interfaces to reference
//
// Write your implementation below. Check answers/ only after attempting.
```

---

## Action Items — Execute in This Order

### 1. Update `.gitignore`

Add these three lines to the existing `.gitignore` (do not remove anything):
```
**/answers/
**/breaks/
**/solutions/
```

---

### 2. Archive Existing Files (Copy, Do Not Delete Yet)

Create archive directory and copy originals — this is the rollback safety net:
```
phases/phase-1-fedtracker-migration/archive/
├── README.md             ← create: "Pre-4-quadrant originals. Archived 2026-05-08. See fedtracker-app/ and functions/ at repo root."
├── app-original/
│   ├── main.py           ← COPY from phases/phase-1-fedtracker-migration/app/main.py
│   └── requirements.txt  ← COPY from phases/phase-1-fedtracker-migration/app/requirements.txt
├── docker-original/
│   └── main.py           ← COPY from phases/phase-1-fedtracker-migration/docker/main.py
└── functions-original/
    ├── audit-processor/  ← COPY entire dir from phases/phase-1-fedtracker-migration/functions/audit-processor/
    └── health-checker/   ← COPY entire dir from phases/phase-1-fedtracker-migration/functions/health-checker/
```

After copying, leave the originals in place — do not move or delete until verification gate passes.

---

### 3. Create `fedtracker-app/` — Python App Scaffold

Create at repo root (NOT inside phases/). This replaces the old `phases/phase-1-fedtracker-migration/app/` as the canonical app location.

**Directory structure to create:**
```
fedtracker-app/
├── main.py          ← scaffold
├── models.py        ← scaffold
├── database.py      ← scaffold
├── routes/
│   ├── __init__.py  ← empty
│   ├── personnel.py ← scaffold
│   ├── audit.py     ← scaffold
│   └── health.py    ← scaffold
├── middleware.py    ← scaffold
├── requirements.txt ← copy from archive/app-original/requirements.txt, keep unchanged
├── answers/         ← gitignored; see below
└── README.md        ← see below
```

**`answers/` directory:** Refactor the original `phases/phase-1-fedtracker-migration/app/main.py` into the multi-file structure. The original is a single monolithic file — split it so:
- `answers/main.py` — FastAPI app setup, lifespan, router includes, startup/shutdown
- `answers/models.py` — All Pydantic models (PersonnelCreate, PersonnelResponse, AuditEntry, etc.)
- `answers/database.py` — SQLAlchemy engine, OCI ADB connection string, get_db() dependency
- `answers/routes/personnel.py` — All /personnel CRUD endpoints
- `answers/routes/audit.py` — GET /audit, POST /audit/export endpoints
- `answers/routes/health.py` — GET /health, GET /health/deep endpoints
- `answers/middleware.py` — Trace ID injection middleware
- `answers/__init__.py`, `answers/routes/__init__.py` — empty

**Scaffold files** (each gets section-comment blocks with WHAT/LEARNING/LOOK UP, empty implementations):
- `main.py`: Section 1 (imports + app creation), Section 2 (lifespan context manager), Section 3 (router registration), Section 4 (startup event: DB init + seed data)
- `models.py`: Section 1 (Personnel models), Section 2 (Audit models), Section 3 (response envelope)
- `database.py`: Section 1 (SQLAlchemy engine setup), Section 2 (OCI ADB connection), Section 3 (get_db dependency)
- `routes/personnel.py`: Section 1 (GET /personnel list), Section 2 (GET /personnel/{id}), Section 3 (POST /personnel), Section 4 (audit log write on every request)
- `routes/audit.py`: Section 1 (GET /audit with date filter), Section 2 (POST /audit/export → Object Storage upload)
- `routes/health.py`: Section 1 (GET /health shallow), Section 2 (GET /health/deep — checks DB + Object Storage + Ollama + disk)
- `middleware.py`: Section 1 (generate trace ID), Section 2 (inject into request state + response headers)

**`README.md`** content:
```markdown
# FedTracker API

Python FastAPI application for federal personnel and compliance tracking.
Part of FedPlatform — OCI federal compliance evidence platform.

**Deployment:** Ansible deploys from answers/ to /opt/fedtracker/app/ on the OCI VM.
Run locally: uvicorn answers.main:app --reload

**Patterns exercised:**
1. FastAPI routing with APIRouter, path parameters, response models
2. Pydantic v2 models with field validation
3. SQLAlchemy ORM with Oracle Autonomous Database
4. Immutable audit log pattern (CMMC AU-2 compliance)
5. Deep health check with dependency validation

**Phase evolution:**
- P1: Personnel CRUD + audit log + health check
- P2: Add /ingest/batch, /webhook, /logs endpoints
- P3: Add /compliance/controls, /compliance/scan, /evidence/generate endpoints
```

---

### 4. Create `fedagent/` — Go App Scaffold

Create at repo root. This is the first Go code in this repo.

**Directory structure:**
```
fedagent/
├── main.go      ← scaffold
├── collector.go ← scaffold
├── oscap.go     ← scaffold
├── go.mod       ← real file (not scaffold)
├── answers/     ← gitignored; Go implementation
└── README.md    ← see below
```

**`go.mod`** (tracked, not scaffold — this is real):
```
module fedplatform/fedagent

go 1.22

require (
    github.com/prometheus/client_golang v1.19.0
)
```

**Scaffold files:**

`main.go` sections:
- Section 1: Flag parsing (`-host` string, `-interval` duration, `-port` int)
- Section 2: Prometheus registry creation and collector registration
- Section 3: HTTP handler for /metrics endpoint
- Section 4: HTTP server startup with graceful shutdown

`collector.go` sections:
- Section 1: Struct definition with metric descriptors (use prometheus.Desc)
- Section 2: `Describe(ch chan<- *prometheus.Desc)` method — send descriptors to channel
- Section 3: `Collect(ch chan<- prometheus.Metric)` method — call oscap, emit metrics

`oscap.go` sections:
- Section 1: Run `oscap oval eval` via `os/exec`, capture stdout
- Section 2: Parse XML output using `encoding/xml`
- Section 3: Return struct with score and findings by severity

**`answers/`**: Write complete working Go implementation. It must compile with `go build ./...`. FedAgent P1 scope: runs OpenSCAP scan on localhost, parses results, exposes Prometheus metrics on `:9100/metrics`.

Metrics to expose:
- `fedplatform_oscap_score{host, framework}` gauge — compliance score 0-100
- `fedplatform_oscap_findings_total{host, severity}` counter — findings by severity (high/medium/low)

**`README.md`** content:
```markdown
# FedAgent

Go Prometheus exporter for OpenSCAP compliance monitoring.
Part of FedPlatform — runs as a long-lived service on the OCI VM.

Build: go build -o fedagent ./...
Run:   ./fedagent -host localhost -port 9100 -interval 1h
Metrics: http://localhost:9100/metrics

Patterns exercised:
1. prometheus.Collector interface (Describe + Collect)
2. goroutines + sync.Mutex for concurrent metric collection
3. os/exec subprocess invocation with timeout
4. encoding/xml for structured output parsing

Phase evolution:
- P1: Single-host OpenSCAP score export
- P2: Multi-host goroutine polling, k3s node health, ADB backup age
- P3: Trivy findings, Cosign validity, Jenkins pipeline status
```

---

### 5. Create `fedplatform-cli/` — Python CLI Scaffold

Create at repo root.

```
fedplatform-cli/
├── main.py           ← scaffold — CLI entry point
├── commands/
│   ├── __init__.py   ← empty
│   ├── personnel.py  ← scaffold — list-personnel command
│   ├── audit.py      ← scaffold — export-audit command
│   └── compliance.py ← scaffold — compliance-check command
├── client.py         ← scaffold — HTTP client wrapper for FedTracker API
├── requirements.txt  ← click, requests, tabulate
├── answers/          ← gitignored
└── README.md
```

**Scaffold sections:**
- `main.py`: Section 1 (Click group setup), Section 2 (command registration and --help config)
- `client.py`: Section 1 (FedTracker base URL config), Section 2 (GET /personnel request), Section 3 (POST /audit/export request), Section 4 (GET /health/deep request)
- `commands/personnel.py`: Section 1 (Click command definition with --clearance option), Section 2 (call client, format tabular output)
- `commands/audit.py`: Section 1 (--since option parsing), Section 2 (trigger export, download CSV)
- `commands/compliance.py`: Section 1 (--framework option), Section 2 (call FedAgent /metrics endpoint, parse score)

**P1 commands the user will implement:**
- `fedplatform-cli list-personnel [--clearance LEVEL]`
- `fedplatform-cli export-audit [--since Nd]`
- `fedplatform-cli compliance-check [--framework fedramp|nist]`

---

### 6. Create `functions/python/audit-processor/` — Promote Existing to Scaffold

The original is at `phases/phase-1-fedtracker-migration/functions/audit-processor/` — it has real working code.

**Create directory:** `functions/python/audit-processor/` at repo root

**Files:**
```
functions/python/audit-processor/
├── func.py          ← scaffold (NEW — stubs of the original)
├── func.yaml        ← COPY from archive/functions-original/audit-processor/func.yaml
├── requirements.txt ← COPY from archive/functions-original/audit-processor/requirements.txt
├── answers/
│   └── func.py      ← COPY from archive/functions-original/audit-processor/func.py (the original working code)
└── README.md
```

**Scaffold `func.py` sections:**
- Section 1: Import fdk, oci SDK; define handler signature
- Section 2: Parse incoming OCI Events notification body to extract bucket name + object name
- Section 3: Download CSV from `audit-evidence/` bucket using OCI Object Storage client
- Section 4: Parse CSV rows, compute action_summary dict, extract top 5 source IPs
- Section 5: Write JSON artifact to `audit-evidence-processed/` bucket

**`README.md`** notes: Trigger = OCI Events on `audit-evidence/` Object Storage. Teach: fdk handler, resource principal auth, Object Storage client, CSV parsing.

---

### 7. Create `functions/go/health-checker-go/` — New Go Serverless

The original Python `health-checker` is archived in `archive/functions-original/health-checker/`. This is a **Go rewrite** — do not copy the Python. Write new Go code.

**Why Go:** Go cold start is ~5ms vs Python ~100ms. This function runs every 5 minutes (288 invocations/day). The cold-start comparison is an explicit teaching point.

```
functions/go/health-checker-go/
├── main.go          ← scaffold
├── go.mod           ← real file
├── func.yaml        ← create new (Go runtime config)
├── answers/
│   └── main.go      ← complete working Go implementation
└── README.md
```

**`go.mod`:**
```
module fedplatform/health-checker-go

go 1.22

require (
    github.com/fnproject/fdk-go v0.0.22
)
```

**`func.yaml`:**
```yaml
schema_version: 20180708
name: health-checker-go
version: 0.0.1
runtime: go
entrypoint: ./health-checker-go
memory: 128
timeout: 30
config:
  APP_HEALTH_URL: http://10.0.2.201:8000/health/deep
```

**Scaffold `main.go` sections:**
- Section 1: Import fdk, net/http, encoding/json, context, time
- Section 2: Define ComponentStatus and HealthResult structs for JSON unmarshal
- Section 3: HTTP GET to APP_HEALTH_URL with context timeout (10s)
- Section 4: Unmarshal response body into ComponentStatus, determine verdict (HEALTHY/DEGRADED/UNREACHABLE)
- Section 5: Return structured JSON verdict with fdk.Send

**`answers/main.go`:** Complete working Go OCI Function that polls `/health/deep` and returns a structured verdict.

---

### 8. Create `adrs/` Directory — Two ADR Files

Create `adrs/` at repo root. Note: existing `docs/ARCHITECTURE-DECISIONS.md` stays and is NOT replaced — `adrs/` is the new home for individual decision files going forward.

**`adrs/ADR-012-pull-vs-push-metrics.md`:**
```markdown
# ADR-012: Prometheus Pull Model for OpenSCAP Metrics

**Status:** Accepted
**Date:** 2026-05-08
**Deciders:** Portfolio architect

## Context
FedAgent needs to expose OpenSCAP compliance scores. Two options: (1) push scores to OCI Monitoring API, (2) expose a Prometheus /metrics endpoint that Prometheus scrapes.

## Decision
Use Prometheus pull model (option 2).

## Rationale
- No OCI Monitoring cost or API rate limits
- Works in air-gapped FedRAMP environments (no outbound calls required)
- Standard Prometheus ecosystem — Grafana, AlertManager, recording rules all work
- OCI Monitoring push requires authenticated outbound API calls from the exporter

## Consequences
- Requires Prometheus server to be deployed in the environment (addressed in Phase 2 with k3s)
- Metrics are only as fresh as the scrape interval (acceptable for compliance scores)

## Learning Check
1. What is the difference between a Prometheus gauge and a counter? When would you use each?
2. Why does the Prometheus pull model suit air-gapped environments?
3. What is the prometheus.Collector interface, and why implement it vs. using prometheus.NewGaugeVec directly?
4. How does sync.Mutex protect concurrent metric collection in FedAgent?
5. What would break if two Prometheus scrapers hit the same exporter concurrently without mutex protection?
```

**`adrs/ADR-013-cli-instance-principal-auth.md`:**
```markdown
# ADR-013: Instance Principal Auth for fedplatform-cli

**Status:** Accepted
**Date:** 2026-05-08

## Context
fedplatform-cli needs to call OCI APIs (Object Storage, etc.) when running on the OCI VM. Auth options: (1) API key in ~/.oci/config, (2) Instance Principal (IAM role on the VM instance).

## Decision
Use Instance Principal when running on OCI VMs; fall back to ~/.oci/config for local development.

## Rationale
- No credentials stored in files or environment variables on production VMs
- Instance Principal is automatically rotated by OCI — no key rotation toil
- Aligns with EO 14028 least-privilege requirements (no long-lived credentials)

## Consequences
- CLI requires IAM policy granting the instance Dynamic Group permission to call OCI APIs
- Local development requires ~/.oci/config setup (acceptable trade-off)

## Learning Check
1. What is an OCI Instance Principal and how is it different from a Service Principal?
2. Why is storing API keys in environment variables on a VM a security risk?
3. How does the OCI Python SDK detect whether to use Instance Principal vs. config file auth?
4. What IAM policy statement grants an instance Dynamic Group access to Object Storage?
5. What happens to CLI auth if the VM is shut down and restarted?
```

---

### 9. Create `phases/phase-1-fedtracker-migration/INCIDENTS.md`

Also create the gitignored supporting files.

**`phases/phase-1-fedtracker-migration/INCIDENTS.md`** (tracked, public):
```markdown
# Phase 1 Incident Catalog

## INC-001: AIDE Detects Unauthorized Binary Change

**Theme:** Security — file integrity monitoring
**Difficulty:** P1 foundational

### Symptom
AIDE daily cron job outputs an alert to /var/log/aide/aide.log. Email notification (if configured) shows:
"AIDE: Warning — integrity check failed for /opt/fedtracker/fedagent"

The Prometheus /metrics endpoint shows `fedplatform_oscap_findings_total{severity="high"}` counter has increased.

### Where to Look
1. Run `aide --check` and read the full output
2. Check `/var/log/aide/aide.log` for the specific changed file and what attribute changed (hash, size, mtime)
3. Run `rpm -V fedagent` (or equivalent package verify) to check if the binary was replaced
4. Review recent command history: `history | grep fedagent`

### Expected Diagnosis
The break script introduced a change to the fedagent binary. Investigation should reveal which attribute changed and trace the source.

### Postmortem Template
Write your postmortem in `postmortems/INC-001-aide-detection-postmortem.md` covering:
- What happened (timeline)
- Root cause
- Detection method
- Resolution
- What you would do differently
```

Create the gitignored files:
- `phases/phase-1-fedtracker-migration/breaks/INC-001-aide-binary-change.sh` — pre-written break script (modifies a file in /opt/fedtracker/ to trigger AIDE)
- `phases/phase-1-fedtracker-migration/solutions/INC-001-aide-binary-change-solution.md` — full investigation walkthrough
- `phases/phase-1-fedtracker-migration/postmortems/` — empty dir with .gitkeep (user fills this in)

---

### 10. Update Ansible `deploy_app.yml`

**File:** `phases/phase-1-fedtracker-migration/ansible/playbooks/deploy_app.yml`

Current behavior: copies `phases/phase-1-fedtracker-migration/app/main.py` (single file) to the VM.

New behavior: sync entire `fedtracker-app/answers/` directory to the VM (multi-file app structure).

Find the copy task that references the old app path and replace with:
```yaml
- name: Deploy FedTracker app
  ansible.posix.synchronize:
    src: "{{ playbook_dir }}/../../../../fedtracker-app/answers/"
    dest: /opt/fedtracker/app/
    delete: yes
    rsync_opts:
      - "--exclude=__pycache__"
      - "--exclude=*.pyc"
```

If `ansible.posix.synchronize` is not available in the existing playbook setup, use:
```yaml
- name: Deploy FedTracker app files
  ansible.builtin.copy:
    src: "{{ playbook_dir }}/../../../../fedtracker-app/answers/"
    dest: /opt/fedtracker/app/
    mode: '0644'
```

Also check if `requirements.txt` path is hardcoded anywhere in the playbook and update to reference `fedtracker-app/requirements.txt`.

---

### 11. Guide Updates — Phase 1 Implementation Guide

**File:** `phases/phase-1-fedtracker-migration/docs/implementation-guide.md`

**Strategy:** Clean inserts at specific points + path retrofits in existing content. Do not rewrite or reorganize existing content.

**A. Insert: 4-Quadrant Model Intro** (insert near the beginning, after the Phase 1 goal/cost/prerequisites section, before the first `terraform` step)

Insert a new section titled "The FedPlatform 4-Quadrant Model" explaining:
- The 4 artifacts (Python API, Go FedAgent, Python OCI Function, Go OCI Function) + Python CLI
- The scaffold/answers pattern (write the scaffolded file, check answers/ only after attempting)
- That FedAgent and health-checker-go are new Go work introduced in this restructure
- That the guide has been updated to add Phase 14 (FedAgent) and Phase 15 (CLI) steps

**B. Insert: Phase 14 — Build FedAgent (Go)** (insert after existing Ansible/Docker content, before Jenkins/CI section)

New section: "Step 14 — Build FedAgent: Go Prometheus Exporter"
- Install Go on the VM (`go install` from OCI package or binary download)
- Clone/copy fedagent/ to the VM at /opt/fedtracker/fedagent/
- Walk through the scaffold: `main.go` → `collector.go` → `oscap.go`
- `go build -o fedagent ./...`
- Run as systemd service on :9100
- Verify: `curl http://localhost:9100/metrics` returns oscap metrics
- Prometheus scrape config (forward-reference to Phase 2 observability stack)

**C. Insert: Phase 15 — Build fedplatform-cli (Python)** (insert after Phase 14)

New section: "Step 15 — Build fedplatform-cli: Python Operator CLI"
- Install on the VM: `pip install -e /opt/fedtracker/fedplatform-cli/`
- Walk through scaffold: `main.py` → `client.py` → `commands/`
- Test P1 commands against running FedTracker API:
  - `fedplatform-cli list-personnel`
  - `fedplatform-cli export-audit --since 7d`
  - `fedplatform-cli compliance-check --framework fedramp`

**D. Insert: Go Function walkthrough** (in the Functions/Phase 17 section, after audit-processor)

New subsection: "Step 17.X — Build health-checker-go: Go Serverless Function"
- Walk through `functions/go/health-checker-go/main.go` scaffold
- Explain fdk-go vs Python fdk pattern differences
- `go build -o health-checker-go ./...`
- Deploy to OCI Functions alongside the Python audit-processor
- Compare cold start: Go ~5ms vs Python ~100ms in OCI console metrics

**E. Path Retrofits** (find and replace in existing content):

| Find | Replace with |
|---|---|
| `phases/phase-1-fedtracker-migration/app/main.py` | `fedtracker-app/answers/main.py` (for deployment references) or `fedtracker-app/main.py` (for scaffold references) |
| `phases/phase-1-fedtracker-migration/functions/audit-processor/` | `functions/python/audit-processor/` |
| `phases/phase-1-fedtracker-migration/functions/health-checker/` | `functions/go/health-checker-go/` |

Run this check after retrofits: `grep -n "phases/phase-1-fedtracker-migration/app/main.py" phases/phase-1-fedtracker-migration/docs/implementation-guide.md` should return zero hits.

---

## Verification Gates (All Must Pass Before Done)

1. `fedtracker-app/main.py` contains `# ── Section` comment blocks — NOT a full implementation
2. `fedtracker-app/answers/main.py` runs: `cd fedtracker-app && uvicorn answers.main:app` starts without import error
3. `fedagent/` compiles: `cd fedagent && go build ./...` exits 0
4. `fedagent/go.mod` exists and declares `prometheus/client_golang`
5. `functions/python/audit-processor/answers/func.py` is the original working code from archive
6. `functions/python/audit-processor/func.py` is a scaffold (section comments, not working code)
7. `functions/go/health-checker-go/main.go` compiles: `cd functions/go/health-checker-go && go build ./...` exits 0
8. `git status` confirms no `answers/`, `breaks/`, `solutions/` directories are tracked
9. `git grep -n "phases/phase-1-fedtracker-migration/app/main.py" phases/phase-1-fedtracker-migration/docs/implementation-guide.md` returns zero hits
10. `phases/phase-1-fedtracker-migration/INCIDENTS.md` exists with INC-001 scenario
11. `adrs/ADR-012-pull-vs-push-metrics.md` and `adrs/ADR-013-cli-instance-principal-auth.md` exist with quiz questions

---

## P2 / P3 Evolution (Reference Only — Do Not Implement Now)

**P2 adds to fedtracker-app:** POST /ingest/batch, POST /webhook, GET /pipeline/status, GET /logs
**P2 adds to fedagent:** goroutine multi-host polling, k3s node health gauges, ADB backup age metric
**P2 Python function:** log-summarizer (scheduled, Ollama-powered compliance narrative)
**P2 Go function:** dr-health-probe (concurrent k3s node polling with sync.WaitGroup)
**P2 CLI additions:** dr-status, failover-check commands

**P3 adds to fedtracker-app:** GET /compliance/controls/{framework}, POST /compliance/scan, POST /evidence/generate
**P3 adds to fedagent:** Trivy image scan findings, Cosign signature validity, Jenkins pipeline status
**P3 Python function:** evidence-collector (event-chained from FedAgent scan output)
**P3 Go function:** supply-chain-validator (OCI Container Registry push → Trivy + Cosign)
**P3 CLI additions:** scan-trigger, policy-report, pipeline-status commands

---

## Related Plans (Do Not Confuse With This One)

| Plan | Location | Status |
|---|---|---|
| This plan (4-quadrant P1 restructure) | `docs/plans/2026-05-08-4-quadrant-p1-restructure.md` | **ACTIVE** |
| Master SE spec (all 4 projects) | `Project ideas/docs/plans/2026-05-08-se-integration-4-quadrant-model.md` | Reference |
| staged-fix-42-phase16-evidence-agent.md | `docs/plans/` | **SUPERSEDED** — functions paths changed |
| staged-fix-43-phase17-functions-rewire.md | `docs/plans/` | **SUPERSEDED** — functions paths changed |
| Prior restructure (cost/K8s/Terraform state) | `.claude/plans/i-think-for-phase-abundant-pixel.md` (archived section) | Separate work item |
