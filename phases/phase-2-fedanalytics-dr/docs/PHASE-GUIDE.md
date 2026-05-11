# Phase 2 — FedAnalytics DR (k3s + DR Drill + NoSQL Hot-Write)

**Public phase guide.** For detailed local notes, see `implementation-guide.md` (gitignored).

**Estimated effort:** ~33-39 focused hours.

---

## Phase Theme

Federal analytics platform with DR capability. Migrate FedTracker to k3s (3 nodes), implement DR drill scenario with RTO/RPO measurement, add CSV batch ingest, introduce OCI NoSQL for compliance hot-write decoupling. Foundation for OKE + supply chain in P3.

## Architecture (end of phase)

```
Primary region (us-ashburn-1):           DR region (us-phoenix-1):
  k3s cluster (3 nodes)                    Standby App VM
  - fedtracker-deployment (3 replicas)     ADB cross-region backup target
  - fedagent-daemonset                     Object Storage replication target
  - ollama-deployment (LLM)
  ↓
  Oracle ADB (primary)  ←→ ADB cross-region copy (RPO < 4h)
  Object Storage         ←→ replicated buckets
  OCI NoSQL (compliance_events_hot, TTL 7d)
  OCI Events (timer + manual DR trigger + object-create)
```

New: OCI NoSQL `compliance_events_hot` table (ADR-017). Batch enrichment function reads NoSQL hourly → writes normalized rows to ADB.

## Phase 2 Building Blocks

| Component | What's added vs P1 |
|---|---|
| fedtracker-app | + routes/ingest.py, routes/logs.py |
| fedagent | + multi-host polling, k3s metrics, ADB backup-age metric |
| fedplatform-cli | + dr-status, failover-check commands |
| functions/python/log-summarizer | NEW — daily scheduled compliance narrative |
| functions/go/dr-health-probe | NEW — on-demand concurrent node polling |
| functions/python/compliance-event-batcher | NEW (per ADR-017) — hourly NoSQL → ADB enrichment |
| OCI NoSQL `compliance_events_hot` | NEW table per ADR-017 |
| gRPC: ComplianceService + DR methods (GetK3sNodeHealth, GetADBBackupStatus) | new methods on existing service |

## Sequenced Steps (each with EVIDENCE CHECKPOINT)

### Step 1 — k3s cluster provisioning (3 nodes)

Stand up k3s cluster on 3 OL9 VMs (1 server + 2 agents).

📋 **EVIDENCE CHECKPOINT** (`evidence/admin/p2/`):
- [ ] `kubectl get nodes -o wide` → `command-outputs/p2-kubectl-nodes.txt`
- [ ] k3s server systemd unit → `configs/k3s.service`
- [ ] Flannel CNI config → `configs/flannel.yaml`
- [ ] Screenshot of OCI compute showing 3 instances → `screenshots/p2-k3s-instances.png`

### Step 2 — fedtracker-app on k3s

Helm-deploy fedtracker (3 replicas) to k3s.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Helm values file → `configs/fedtracker-values.yaml`
- [ ] `kubectl get deploy,svc,pod -n fedplatform` → `command-outputs/p2-fedtracker-deploy.txt`
- [ ] curl from inside cluster (kubectl exec) → 200 OK → `command-outputs/p2-fedtracker-in-cluster.txt`

### Step 3 — Ollama deployment

Deploy Ollama on k3s for the log-summarizer LLM dependency.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Ollama pod logs → `command-outputs/p2-ollama-startup.txt`
- [ ] Test inference: curl POST :11434/api/generate → `command-outputs/p2-ollama-test.txt`

### Step 4 — OCI NoSQL provisioning + integration

Provision NoSQL table per ADR-017. Wire fedagent to write events.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `terraform plan` output → `command-outputs/p2-tf-nosql-plan.txt`
- [ ] OCI CLI: `oci nosql table get` → `command-outputs/p2-nosql-table.json`
- [ ] Test event write from fedagent: `oci nosql query` → `command-outputs/p2-nosql-event-read.txt`
- [ ] Update `evidence/db/design-doc.md` with NoSQL hot-write decision

### Step 5 — compliance-event-batcher function

Deploy the batch enrichment function. Triggered hourly.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `fn deploy` output → `command-outputs/p2-batcher-deploy.txt`
- [ ] Function invocation trace: NoSQL read → ADB write → `command-outputs/p2-batcher-flow.txt`

### Step 6 — log-summarizer + dr-health-probe functions

Deploy P2 functions per the existing P2 plan.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Sample compliance narrative output → `evidence/reports/p2-compliance-narrative-sample.md`
- [ ] dr-health-probe response showing concurrent node polling → `command-outputs/p2-dr-probe-response.json`

### Step 7 — gRPC DR methods

Wire GetK3sNodeHealth + GetADBBackupStatus in fedagent. Use from fedtracker /health/deep.

📋 **EVIDENCE CHECKPOINT**:
- [ ] grpcurl test of GetK3sNodeHealth → `command-outputs/p2-grpc-k3s-health.json`
- [ ] /health/deep response showing k3s block → `command-outputs/p2-health-deep-with-k3s.json`

### Step 8 — Admin Day P2 (networking + storage + k3s OS)

Execute the dedicated admin day per `admin-day-p2.md`. iptables, LVM, namespaces, sysctl tuning, k3s OS-level debug, certificate stores.

📋 See `admin-day-p2.md` for full step list and EVIDENCE CHECKPOINTS.

### Step 9 — DR Drill execution

Execute the DR drill scenario. Capture pre-drill state, inject failure (one of: k3s node down, ADB backup stale, full failover), measure RTO/RPO, write postmortem.

📋 **EVIDENCE CHECKPOINT** — see `evidence/dr-drills/p2-fedanalytics-dr.md` template; fill all sections.

### Step 10 — INC-002 + INC-003 simulations

Run both P2 break scenarios. Write postmortems.

📋 **EVIDENCE CHECKPOINT**:
- [ ] INC-002 OpenSCAP regression: scan output before/after → `command-outputs/p2-inc002-*.txt`
- [ ] INC-003 k3s node failure: kubectl events + diagnostic flow → `command-outputs/p2-inc003-*.txt`
- [ ] Postmortems in `phases/phase-2-fedanalytics-dr/postmortems/`

---

## Phase 2 Key Takeaways (interview prep)

_<USER FILLS at end of phase>_

1. **k3s primitives:** _<what feeling the primitives taught you vs OKE managed>_
2. **DR drill measurement:** _<your RTO/RPO actual vs target; what surprised you>_
3. **NoSQL hot-write decoupling:** _<ADR-017 rationale + the specific failure mode it avoids>_
4. **Multi-host metrics:** _<the goroutine concurrency pattern you used>_
5. **At scale:** _<what changes at 30 nodes / multi-region active-active>_
