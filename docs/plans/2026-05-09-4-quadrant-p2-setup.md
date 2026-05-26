# [AGENT HANDOFF] OCI FedPlatform — 4-Quadrant P2 Extensions

**Repo:** `C:\Users\k_a_s\OneDrive\Desktop\github\oci-federal-lab`
**Branch:** `git checkout -b se-integration-p2`
**Prerequisite:** OCI P1 complete and merged to master.

## What P1 Built (Foundation)

```
fedtracker-app/          ← Python FastAPI (scaffold + answers/)
fedagent/                ← Go Prometheus exporter (scaffold + answers/)
fedplatform-cli/         ← Python CLI (scaffold + answers/)
functions/python/audit-processor/
functions/go/health-checker-go/
adrs/ADR-012, ADR-013
scripts/INC-001-aide-preflight.sh
phases/phase-1-fedtracker-migration/INCIDENTS.md
```

## P2 Theme: FedAnalytics — DR Drill & k3s Kubernetes

Phase 2 scenario: federal analytics platform needs DR capability. Deploy FedAnalytics app on k3s cluster, implement backup architecture, prove recovery within RTO/RPO.

---

## Action Items

### 1. Untrack Phase 2 Directory

Check if `phases/phase-2-fedanalytics-dr/` is in `.gitignore`. If so, remove that line. Phase 2 must be tracked to commit its files.

---

### 2. Extend `fedtracker-app/` — Add P2 Routes

Add new scaffold files + corresponding answers for Phase 2 routes:

**New scaffold files (section-comment stubs):**
- `fedtracker-app/routes/ingest.py` — POST /ingest/batch (CSV batch upload), POST /webhook (OCI Events receiver), GET /pipeline/status
- `fedtracker-app/routes/logs.py` — GET /logs?severity=ERROR&since=1h (query app_logs table with filters)

**New answers files:**
- `fedtracker-app/answers/routes/ingest.py` — working implementation of all ingest endpoints
- `fedtracker-app/answers/routes/logs.py` — working log query endpoint

**Update `fedtracker-app/answers/main.py`:** add router includes for the two new modules.
**Update `fedtracker-app/main.py` scaffold:** add section comments for P2 router registration.

---

### 3. Extend `fedagent/` — Add P2 Metrics

Extend the existing Go Prometheus exporter to support multi-host polling and k3s/ADB metrics.

**Update `fedagent/oscap.go` scaffold:** add section comment for multi-host goroutine pool.
**Update `fedagent/collector.go` scaffold:** add section comments for new P2 metric descriptors.

**Update `fedagent/answers/` to add:**
- Multi-host polling: spawn goroutine per host from a hosts slice flag, use `sync.WaitGroup`
- New metrics:
  - `fedplatform_k3s_node_ready{node}` gauge — poll k3s API `/api/v1/nodes`, check Ready condition
  - `fedplatform_backup_age_seconds{target}` gauge — OCI CLI `oci db autonomous-database get`, parse `timeOfLastBackup`

**Update `fedagent/go.mod`:** add `k8s.io/client-go` if needed for k3s API calls (or use raw HTTP to k3s kubeconfig endpoint).

---

### 4. Extend `fedplatform-cli/` — Add P2 Commands

**New scaffold files:**
- `fedplatform-cli/commands/dr.py` — `dr-status` command (calls k3s API + fedagent /metrics for k3s gauges)
- `fedplatform-cli/commands/failover.py` — `failover-check --rto <minutes>` command (measures actual failover time)

**New answers files:**
- `fedplatform-cli/answers/commands/dr.py`
- `fedplatform-cli/answers/commands/failover.py`

**Update `fedplatform-cli/main.py` scaffold + `answers/main.py`:** register new P2 commands.

---

### 5. Create `functions/python/log-summarizer/` — New P2 Python Function

**Trigger:** OCI Events timer (daily 23:00 UTC)
**Does:** queries FedTracker `app_logs` table for today's entries → builds Ollama prompt → writes Markdown compliance narrative to `compliance-artifacts/` bucket

```
functions/python/log-summarizer/
├── func.py          ← scaffold
├── func.yaml        ← timer trigger (OCI Events schedule)
├── requirements.txt ← fdk, oci, oracledb, requests
├── answers/
│   └── func.py      ← complete implementation
└── README.md
```

**`func.yaml`:**
```yaml
schema_version: 20180708
name: log-summarizer
version: 0.0.1
runtime: python3.11
entrypoint: func.py
memory: 256
timeout: 120
```

**Scaffold sections in `func.py`:**
- Section 1: Connect to Oracle ADB, query app_logs for today WHERE created_at > TRUNC(SYSDATE)
- Section 2: Format log entries into Ollama prompt template
- Section 3: POST to Ollama /api/generate with compliance narrative prompt
- Section 4: Write Markdown response to OCI Object Storage compliance-artifacts bucket

---

### 6. Create `functions/go/dr-health-probe/` — New P2 Go Function

**Trigger:** OCI Events rule on manual DR drill trigger event
**Does:** polls all k3s node /health endpoints concurrently → writes alert JSON to `dr-alerts/` if any degraded

```
functions/go/dr-health-probe/
├── main.go          ← scaffold
├── go.mod           ← module fedplatform/dr-health-probe; requires fnproject/fdk-go
├── func.yaml        ← trigger config
├── answers/
│   └── main.go      ← complete implementation
└── README.md
```

**Scaffold sections in `main.go`:**
- Section 1: fdk-go handler setup, parse k3s node IPs from config/env
- Section 2: Launch goroutines — one per node, each calls /health endpoint
- Section 3: sync.WaitGroup coordination, collect results
- Section 4: If any node degraded, write alert JSON to dr-alerts/ bucket via OCI SDK

Teaches: goroutines in serverless context, `sync.WaitGroup`, concurrent HTTP with timeouts, OCI Object Storage write from Go.

---

### 7. Create `phases/phase-2-fedanalytics-dr/INCIDENTS.md` — 2 Breaks

```markdown
# Phase 2 Incident Catalog

## INC-002: OpenSCAP Score Drops After Package Update

**Theme:** Security — compliance regression detection
**Difficulty:** P2 integration

### Symptom
FedAgent metrics show `fedplatform_oscap_score` dropped from 87 to 61.
`scripts/INC-002-oscap-regression.sh` exits 1 with regression warning.

### Where to Look
1. Run `oscap oval eval --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-ol9-oval.xml` and compare to baseline
2. Check `rpm -Va` for modified package files
3. Check `rpm -q --changelog <package>` for recent changes
4. Compare `/opt/fedtracker/oscap-baseline.txt` to current score

### Expected Diagnosis
The break script installs a non-CIS-compliant package. Investigation finds the package and removes it or accepts the deviation with documented justification.

### Prevention
`scripts/INC-002-oscap-regression.sh` — detects score drops before they persist.

---

## INC-003: k3s Node Fails During DR Drill

**Theme:** Kubernetes — node failure recovery
**Difficulty:** P2 integration

### Symptom
`kubectl get nodes` shows a node in NotReady state during DR drill.
`scripts/INC-003-k3s-dr-readiness.sh` exits 1 before drill starts.

### Where to Look
1. `journalctl -u k3s -n 100` on the failing node
2. `kubectl describe node <node-name>` for conditions and events
3. Check disk space: `df -h /var/lib/rancher/k3s`
4. Check kubelet cert expiry: `openssl x509 -noout -dates -in /var/lib/rancher/k3s/agent/client-kubelet.crt`

### Expected Diagnosis
The break script fills disk on the worker node or expires a cert. Investigation traces the NotReady condition to its root cause.

### Prevention
`scripts/INC-003-k3s-dr-readiness.sh` — validates k3s cluster health before DR drills begin.
```

Create gitignored:
- `phases/phase-2-fedanalytics-dr/breaks/INC-002-oscap-regression.sh`
- `phases/phase-2-fedanalytics-dr/breaks/INC-003-k3s-node-failure.sh`
- `phases/phase-2-fedanalytics-dr/solutions/INC-002-oscap-regression-solution.md`
- `phases/phase-2-fedanalytics-dr/solutions/INC-003-k3s-node-failure-solution.md`
- `phases/phase-2-fedanalytics-dr/postmortems/.gitkeep`

---

### 8. Create Prevention Scripts

`scripts/INC-002-oscap-regression.sh` (Bash):
```bash
#!/usr/bin/env bash
# INC-002 Prevention: OpenSCAP Compliance Regression Check
# Incident: phases/phase-2-fedanalytics-dr/INCIDENTS.md → INC-002
# Postmortem: phases/phase-2-fedanalytics-dr/postmortems/INC-002-*.md
# Purpose: Detect OpenSCAP score regression before it persists post-update.
```
- Runs oscap oval eval, extracts score
- Reads baseline from `/opt/fedtracker/oscap-baseline.txt`
- Exits 1 if current score < baseline - 5 points

`scripts/INC-003-k3s-dr-readiness.sh` (Bash):
```bash
#!/usr/bin/env bash
# INC-003 Prevention: k3s Cluster DR Readiness Check
# Incident: phases/phase-2-fedanalytics-dr/INCIDENTS.md → INC-003
# Purpose: Verify k3s cluster health and ADB backup age before DR drills.
```
- `kubectl get nodes --no-headers | grep -v Ready` → exits 1 if any NotReady
- OCI CLI: gets last ADB backup timestamp, exits 1 if > 4 hours old

---

### 9. Add ADR-014

`adrs/ADR-016-k3s-before-oke-pedagogy.md` — why k3s DIY cluster in P2 before managed OKE in P3. Key: feel the primitives (control plane, kubelet, Flannel CNI, kubeconfig) before the managed abstraction. Include 5 quiz questions. (Renumbered from ADR-014 to free that slot for the gRPC ADR.)

**ADR-021 (v3 AI) — decide at phase start:** `adrs/ADR-021-airgapped-rag-bm25.md` — how to do air-gapped compliance Q&A (BM25/vectorless vs dense-vector vs managed RAG) and how the chatbot grounds or abstains. Decide BEFORE building `fedtracker-app/rag.py` + `routes/chat.py`; build steps + evidence in `docs/exercises/p2/ai/rag-chatbot-notes.md`. Include 5 quiz questions; confirm consequences after the phase.

---

### 10. Update P2 Implementation Guide

**File:** `phases/phase-2-fedanalytics-dr/docs/implementation-guide.md`

Add sections after existing k3s cluster setup content:
- **4-Quadrant Model: Phase 2 Extensions** — what FedTracker gains, what FedAgent gains, new functions
- **Step X — Extend FedTracker API** — walkthrough adding ingest + log routes
- **Step X — Extend FedAgent** — walkthrough adding multi-host + k3s metrics
- **Step X — log-summarizer Function** — deploy and verify Ollama-powered narrative
- **Step X — dr-health-probe Go Function** — deploy and verify concurrent node polling
- **Step X — Extend fedplatform-cli** — add dr-status and failover-check commands

---

### 11. Extend gRPC Interface — DR Methods

**Update `fedagent/proto/compliance.proto`** to add P2 methods to existing ComplianceService:

```proto
import "google/protobuf/empty.proto";

service ComplianceService {
  rpc GetOscapScore(GetOscapScoreRequest) returns (GetOscapScoreResponse);
  // P2 methods
  rpc GetK3sNodeHealth(google.protobuf.Empty) returns (K3sNodeHealthResponse);
  rpc GetADBBackupStatus(google.protobuf.Empty) returns (ADBBackupStatusResponse);
}

message K3sNodeHealthResponse {
  message NodeStatus {
    string node = 1;
    bool ready = 2;
    string last_heartbeat = 3;
  }
  repeated NodeStatus nodes = 1;
}

message ADBBackupStatusResponse {
  string last_backup_at = 1;
  int64 backup_age_seconds = 2;
  bool within_rpo = 3;     // age < 4 hours
}
```

Regenerate Go stubs (`protoc ...`).

**Update `fedagent/grpc_server.go` scaffold + answers:** add Section for `GetK3sNodeHealth` (queries k3s API via kubeconfig in env) and `GetADBBackupStatus` (calls OCI CLI `oci db autonomous-database get`).

**Update `fedtracker-app/grpc_client.py` scaffold + answers:** add `get_k3s_node_health()` and `get_adb_backup_status()` async methods.

**Update `fedtracker-app/answers/routes/health.py`:** GET /health/deep enriched with k3s node status from gRPC; surfaces in `components.k3s_cluster` block.

**Inline verification:**
- fedagent gRPC server returns valid responses for `GetK3sNodeHealth` and `GetADBBackupStatus`
- fedtracker-app /health/deep includes k3s node block from gRPC

---

## Verification Gates

1. `fedtracker-app/routes/ingest.py` has section-comment blocks
2. `fedtracker-app/answers/routes/ingest.py` has working POST /ingest/batch
3. `fedagent/answers/collector.go` exposes `fedplatform_k3s_node_ready` metric
4. `functions/python/log-summarizer/func.py` is a scaffold; `answers/func.py` is complete
5. `functions/go/dr-health-probe/main.go` compiles: `go build ./...` exits 0
6. `phases/phase-2-fedanalytics-dr/INCIDENTS.md` has INC-002 and INC-003 with Prevention sections
7. `scripts/INC-002-oscap-regression.sh` and `scripts/INC-003-k3s-dr-readiness.sh` exist and are executable
8. `adrs/ADR-016-k3s-before-oke-pedagogy.md` exists with quiz questions (renumbered from ADR-014 — see verification-grpc-gateway-zap-2026-05-09 branch)
9. `git status` shows no `answers/`, `breaks/`, `solutions/` tracked

---

## Addendum 2026-05-24 — v3 AI-Forward Pass (P2)

**Status:** v3 AI layer. Delta-add on top of the v1+v2 P2 lock — nothing above changes. Scaffold committed; **you build the AI logic** (chunking/retrieval, prompts, the catalog). Decide the ADR at phase **START**, confirm at end. Scope: scaffold-only — `answers/` is yours.

### v3-P2a. Air-gapped RAG over the controls catalog + compliance Q&A chatbot

**Theme:** GRC automation that works **offline** — the air-gap differentiator no cloud-API project can claim. Deliberately **BM25 / vectorless** (no embedding model at all) — the opposite pattern from AWS's dense-vector RAG, and maximally air-gap-pure. Ollama generates only; it never retrieves.

**Decide first — ADR-021** (`adrs/ADR-021-airgapped-rag-bm25.md`, blank quiz): BM25/vectorless vs dense-vector vs managed RAG for air-gapped controls lookup; why no embedding model (keyword/control-ID precision, e.g. "AC-3"); how the chatbot grounds answers or **abstains** when retrieval is weak; document OCI GenAI as the managed alternative.

**Build** `fedtracker-app/rag.py` + `fedtracker-app/routes/chat.py`:
- BM25 / FTS5 retrieval (`rank_bm25` or SQLite FTS5) over a NIST 800-53 / 800-171 / CMMC controls catalog (JSON/markdown in-repo or Object Storage) — keyword/ID precise, no vectors.
- `POST /chat/ask` → retrieve control(s) → Ollama generate → plain-English answer + cited control IDs.
- Realizes the previously-placeholder "OCI GenAI Agents for incident triage" — done air-gapped on Ollama.

**answers/ spec (you write it):** chunking/retrieval logic + the chat route + the Ollama prompt; you provide the catalog.

**Cross-phase dependency:** the controls catalog + finding→control vocabulary you build here is reused by **P3** evidence classification (ADR-022) — keep the control IDs consistent.

**Evidence:** `docs/exercises/p2/ai/rag-chatbot-notes.md` — most important: the **air-gap test** (block network egress, prove RAG still answers) + Q&A traces.

**Verify:** with the host's outbound network blocked, `POST /chat/ask "what does AC-3 require?"` still returns a grounded answer citing the control ID.

### v3-P2b. Container pull-through cache (cache #2, container layer — no ADR)

**Theme:** the project's SECOND cache, at the **container** layer (cache #1 = OCI Cache at the API edge). A pull-through registry / in-cluster mirror so image pulls survive a registry blip — fits the air-gapped story. Kept feature, **no dedicated ADR**.

**Build** per `docs/exercises/p2/container-cache-notes.md`: configure a pull-through cache / mirror (Podman → k3s → OKE progression), point the cluster at it, prove a cache hit.

**answers/ spec (you write it):** the registry/mirror config (config, not code).

**Evidence:** `docs/exercises/p2/container-cache-notes.md` (pull-through config, a warm-cache pull served without hitting the upstream registry, latency delta).

**Verify:** a second image pull is served from the local cache with the upstream unreachable.
