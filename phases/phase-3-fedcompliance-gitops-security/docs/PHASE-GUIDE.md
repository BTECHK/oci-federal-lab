# Phase 3 — FedCompliance GitOps + Security (OKE + API GW + Supply Chain + Cache + Patch Sim)

**Public phase guide.** For detailed local notes, see `implementation-guide.md` (gitignored).

**Estimated effort:** ~36-42 focused hours.

---

## Phase Theme

Modernize from k3s to OKE Basic (managed Kubernetes), GitOps via Helm + ArgoCD, supply chain security (Trivy + Cosign + SBOM), API Gateway with JWT validation, distributed cache (OCI Cache Redis), and the **kernel CVE patch simulation** — the final layer of admin reps.

## Architecture (end of phase)

```
External users → OCI API Gateway (JWT validation via IDCS JWKS)
                 ↓
                 → OCI LB → OKE Basic cluster
                            ├── fedtracker (Helm-deployed, ArgoCD synced)
                            ├── fedagent (with Trivy + Cosign + Jenkins metrics)
                            ├── cert-manager + nginx-ingress
                            ├── OPA Gatekeeper (admission policies, ADR-005)
                            └── ollama
                 ↓
                 → OCI Cache (Redis, hot compliance lookups, ADR-020)
                 → Oracle ADB
                 → OCI NoSQL (compliance_events_hot + supply_chain_results — ADR-018)
                 → OCI Object Storage (+ scan-results/, supply-chain-results/, helm-charts/)
                 → OCIR (signed images via Cosign)
                 → OCI Events (image push, object create, timer)
```

New: ArgoCD GitOps, OCI API Gateway, supply-chain-validator function, evidence-collector function, OCI Cache, Cloud Guard posture monitoring.

## Phase 3 Building Blocks

| Component | What's added vs P2 |
|---|---|
| fedtracker-app | + routes/compliance.py, routes/evidence.py |
| fedagent | + Trivy + Cosign + Jenkins metrics, supply chain gRPC streaming |
| fedplatform-cli | + scan-trigger, policy-report, pipeline-status, supply-chain-query commands |
| functions/python/evidence-collector | NEW — CVE→CMMC mapping, evidence package generation |
| functions/go/supply-chain-validator | NEW — Cosign verify + Trivy scan, writes to NoSQL doc store |
| OCI NoSQL `supply_chain_results` | NEW table per ADR-018 |
| OCI Cache (Redis) | NEW per ADR-020 |
| OCI API Gateway | NEW (ADR-015 already documented; deploy in P3) |
| OWASP ZAP CI scan | new GitHub Actions workflow |

## Sequenced Steps (each with EVIDENCE CHECKPOINT)

### Step 1 — OKE Basic cluster provisioning

Migrate from k3s (decommission) to OKE Basic. Stand up cluster with managed control plane + 3-node pool.

📋 **EVIDENCE CHECKPOINT** (`docs/exercises/p3/`):
- [ ] `terraform plan` for OKE → `command-outputs/p3-tf-oke-plan.txt`
- [ ] `kubectl config view --minify` → `configs/p3-oke-kubeconfig-sanitized.yaml`
- [ ] `kubectl get nodes` showing managed nodes → `command-outputs/p3-oke-nodes.txt`

### Step 2 — ArgoCD installation + initial sync

Install ArgoCD via Helm. Configure Application resource pointing to git repo.

📋 **EVIDENCE CHECKPOINT**:
- [ ] ArgoCD Application yaml → `configs/p3-argocd-app.yaml`
- [ ] First successful sync output → `command-outputs/p3-argocd-first-sync.txt`
- [ ] Screenshot of ArgoCD UI showing app green → `screenshots/p3-argocd-sync.png`

### Step 3 — OCI Cache (Redis) provisioning + integration

Provision OCI Cache per ADR-020. Wire `fedtracker-app/cache.py` cache-aside.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `terraform plan` → `command-outputs/p3-tf-cache-plan.txt`
- [ ] redis-cli ping from fedtracker pod → `command-outputs/p3-cache-ping.txt`
- [ ] Cache hit rate metric capture (before + after warmup) → `command-outputs/p3-cache-hit-rate.txt`
- [ ] Latency comparison: cache hit vs cache miss → `docs/compliance/p3-cache-latency-comparison.md`

### Step 4 — OCI NoSQL `supply_chain_results` table

Add second NoSQL table per ADR-018.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Table provisioning output → `command-outputs/p3-nosql-supply-chain-table.json`
- [ ] Secondary index on (scanned_at, severity) → `command-outputs/p3-nosql-secondary-index.json`
- [ ] Test query: HIGH CVEs in last 7d → `command-outputs/p3-nosql-query-test.json`

### Step 5 — supply-chain-validator + evidence-collector functions

Deploy P3 functions. supply-chain-validator triggered by OCIR image push.

📋 **EVIDENCE CHECKPOINT**:
- [ ] Test image push → function invocation trace → `command-outputs/p3-supply-chain-flow.txt`
- [ ] Sample scan result JSON in Object Storage → `docs/exercises/p3/screenshots/p3-supply-chain-result.json`
- [ ] CMMC evidence package sample → `docs/compliance/p3-cmmc-evidence-package-sample.md`

### Step 6 — OCI API Gateway deployment (ADR-015)

Deploy API Gateway with JWT validation, rate limiting, CORS, audit logging policies.

📋 **EVIDENCE CHECKPOINT**:
- [ ] `terraform plan` → `command-outputs/p3-tf-apigw-plan.txt`
- [ ] curl with JWT: 200 → `command-outputs/p3-apigw-jwt-success.txt`
- [ ] curl without JWT: 401 → `command-outputs/p3-apigw-jwt-rejected.txt`
- [ ] Rate limit test (rapid curl) showing 429 → `command-outputs/p3-apigw-ratelimit.txt`

### Step 7 — Cosign + Trivy in CI

Wire Cosign signing in CI; Trivy scan + Cosign verify in OKE admission via OPA Gatekeeper.

📋 **EVIDENCE CHECKPOINT**:
- [ ] CI workflow file → `.github/workflows/release.yml`
- [ ] Signed image manifest (cosign tree output) → `command-outputs/p3-cosign-tree.txt`
- [ ] Admission block test: unsigned image rejected → `command-outputs/p3-admission-rejected.txt`

### Step 8 — gRPC supply chain streaming

Wire `StreamComplianceEvents` server-streaming RPC. Test with fedtracker as consumer.

📋 **EVIDENCE CHECKPOINT**:
- [ ] grpcurl stream test → `command-outputs/p3-grpc-streaming.txt`
- [ ] Compliance events persisted in ADB compliance_events table → `command-outputs/p3-compliance-events-row.json`

### Step 9 — OWASP ZAP DAST in CI

Add ZAP baseline scan to CI; runs on PR + weekly cron.

📋 **EVIDENCE CHECKPOINT**:
- [ ] ZAP workflow file → `.github/workflows/security-scan.yml`
- [ ] Sample ZAP report → `docs/compliance/p3-zap-baseline-report.html` (or excerpt)

### Step 10 — Admin Day P3 + Patch Simulation

Execute the dedicated admin day per `admin-day-p3.md`. auditd + OpenSCAP + AIDE + PAM. Then run the kernel CVE patch simulation per `docs/exercises/p3/patch-simulation-report.md`.

📋 See `admin-day-p3.md` and `docs/exercises/p3/patch-simulation-report.md` for full checkpoints.

### Step 11 — INC-004 + INC-005 simulations

Run both P3 break scenarios. Write postmortems.

📋 **EVIDENCE CHECKPOINT**:
- [ ] INC-004 cert expiry: openssl + recovery trace → `command-outputs/p3-inc004-*.txt`
- [ ] INC-005 SLO burn: Prom + Grafana + recovery → `command-outputs/p3-inc005-*.txt`
- [ ] Postmortems in `phases/phase-3-fedcompliance-gitops-security/postmortems/`

---

## Phase 3 Key Takeaways (interview prep)

_<USER FILLS at end of phase>_

1. **OKE vs k3s decision:** _<what managed gave you vs what you lost from k3s primitives>_
2. **Supply chain story:** _<the full chain from CI to admission, with key invariants>_
3. **API Gateway as compliance edge:** _<JWT validation at edge, audit logging, what scope reduction it gave the backend>_
4. **Cache placement (ADR-020):** _<why service-tier not gateway-tier>_
5. **Patch simulation lesson:** _<the lifecycle pattern + rollback strategy at scale>_
