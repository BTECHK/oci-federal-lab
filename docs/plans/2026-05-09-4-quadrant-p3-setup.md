# [AGENT HANDOFF] OCI FedPlatform — 4-Quadrant P3 Extensions

**Repo:** `C:\Users\k_a_s\OneDrive\Desktop\github\oci-federal-lab`
**Branch:** `git checkout -b se-integration-p3`
**Prerequisite:** OCI P2 complete and merged to master.

## What P2 Added (Foundation for P3)

```
fedtracker-app/routes/ingest.py + logs.py (P2 routes)
fedagent/ extended with k3s metrics + multi-host polling
fedplatform-cli/ extended with dr-status, failover-check
functions/python/log-summarizer/
functions/go/dr-health-probe/
scripts/INC-002-oscap-regression.sh, INC-003-k3s-dr-readiness.sh
phases/phase-2-fedanalytics-dr/INCIDENTS.md
```

## P3 Theme: FedCompliance — CI/CD Modernization & Supply Chain Security

Phase 3 scenario: migrate from k3s to OKE Basic (managed Kubernetes), add GitOps with Helm + ArgoCD, implement supply chain security (Trivy + Cosign + SBOM), add AI-powered compliance reporting.

---

## Action Items

### 1. Untrack Phase 3 Directory

Check if `phases/phase-3-fedcompliance-gitops-security/` is in `.gitignore`. If so, remove that line.

---

### 2. Extend `fedtracker-app/` — Add P3 Routes

**New scaffold files:**
- `fedtracker-app/routes/compliance.py` — GET /compliance/controls/{framework}, POST /compliance/scan, GET /compliance/report
- `fedtracker-app/routes/evidence.py` — POST /evidence/generate (outputs CMMC artifact package to Object Storage)

**New answers files:**
- `fedtracker-app/answers/routes/compliance.py` — working compliance endpoints that query FedAgent scan results
- `fedtracker-app/answers/routes/evidence.py` — evidence package generator that bundles audit logs + scan results + compliance mapping

**Update `fedtracker-app/answers/main.py`:** add P3 router includes.
**Update `fedtracker-app/main.py` scaffold:** add P3 section comments.

---

### 3. Extend `fedagent/` — Add P3 Metrics

**Update `fedagent/collector.go` scaffold:** add section comments for P3 metric descriptors.

**Update `fedagent/answers/` to add:**
- `fedplatform_trivy_findings_total{image, severity}` counter — runs `trivy image` as subprocess, parses JSON output
- `fedplatform_cosign_signature_valid{image}` gauge — runs `cosign verify` subprocess, returns 1=valid 0=invalid
- `fedplatform_pipeline_last_build_status{job}` gauge — calls Jenkins REST API, returns 1=success 0=failure

**Update `fedagent/oscap.go`:** extend subprocess execution pattern to handle Trivy and Cosign in `fedagent/answers/trivy.go` and `fedagent/answers/cosign.go`.

---

### 4. Extend `fedplatform-cli/` — Add P3 Commands

**New scaffold files:**
- `fedplatform-cli/commands/compliance.py` — `scan-trigger` (trigger FedAgent scan), `policy-report --output json|md` (generate CMMC control mapping report)
- `fedplatform-cli/commands/pipeline.py` — `pipeline-status` (query Jenkins API via fedagent metrics)

**New answers files + update main.py** scaffold and answers.

---

### 5. Create `functions/python/evidence-collector/` — New P3 Python Function

**Trigger:** OCI Events on object creation in `scan-results/` bucket (FedAgent writes scan output there)
**Does:** reads scan JSON → maps CVE/finding to CMMC control IDs → generates evidence package → writes to `compliance-artifacts/evidence-TIMESTAMP/`

```
functions/python/evidence-collector/
├── func.py          ← scaffold
├── func.yaml        ← OCI Events object create trigger on scan-results bucket
├── requirements.txt ← fdk, oci
├── answers/
│   └── func.py      ← complete implementation
└── README.md
```

**Scaffold sections:**
- Section 1: Parse OCI Events notification, extract scan-results object name
- Section 2: Download scan JSON from Object Storage
- Section 3: Map CVE IDs and findings to CMMC control catalog (lookup table)
- Section 4: Bundle evidence package (scan JSON + control mapping + audit excerpt)
- Section 5: Write package to compliance-artifacts/evidence-TIMESTAMP/ with manifest

---

### 6. Create `functions/go/supply-chain-validator/` — New P3 Go Function

**Trigger:** OCI Events on image push to OCI Container Registry
**Does:** validates Cosign signature → runs Trivy scan → returns PASS/FAIL with finding list → writes to `supply-chain-results/`

```
functions/go/supply-chain-validator/
├── main.go          ← scaffold
├── go.mod           ← module fedplatform/supply-chain-validator; requires fnproject/fdk-go
├── func.yaml        ← trigger: OCI Container Registry image push event
├── answers/
│   └── main.go      ← complete implementation
└── README.md
```

**Scaffold sections:**
- Section 1: Parse OCI Container Registry push event, extract image reference
- Section 2: Run Cosign verify via os/exec, capture output
- Section 3: Run Trivy image scan via os/exec, parse JSON findings
- Section 4: Build PASS/FAIL result with severity summary
- Section 5: Write result JSON to supply-chain-results/ bucket

Teaches: os/exec subprocess in Go serverless context, JSON parsing, image registry event schema.

---

### 7. Create `phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md` — 2 Breaks

```markdown
# Phase 3 Incident Catalog

## INC-004: TLS Certificate Expires Mid-Pipeline

**Theme:** Security — certificate lifecycle management
**Difficulty:** P3 multi-component

### Symptom
Jenkins pipeline fails with SSL handshake error. FedAgent metrics show `fedplatform_pipeline_last_build_status{job="deploy-fedcompliance"}` = 0.
`scripts/INC-004-cert-expiry-check.sh` exits 1 with "cert expires in 0 days".

### Where to Look
1. `openssl s_client -connect <host>:443 -showcerts` — view cert chain
2. Check Jenkins logs for SSL handshake errors
3. Review cert renewal cron job: `crontab -l | grep certbot` or `systemctl status certbot.timer`
4. Check Kubernetes secret age: `kubectl get secret tls-cert -o yaml | grep notAfter`

### Expected Diagnosis
The break script modifies the cert expiry or disables cert renewal. Investigation finds expired cert and triggers renewal.

### Prevention
`scripts/INC-004-cert-expiry-check.sh` — daily cert expiry check, warns at 30 days.

---

## INC-005: SLO Error Budget Burn from Ollama Latency Spike

**Theme:** Reliability — SLO burn rate response
**Difficulty:** P3 multi-component

### Symptom
`scripts/INC-005-slo-budget-check.py` exits 1: "Error budget < 20% remaining".
Ollama response times > 30s causing log-summarizer function timeouts.

### Where to Look
1. Check Ollama logs: `journalctl -u ollama -n 100`
2. Check system resources: `top`, `free -h`, GPU utilization if applicable
3. Check FedAgent metrics for recent error rate spike
4. Review log-summarizer function logs in OCI console

### Expected Diagnosis
The break script increases Ollama load or reduces VM resources. Investigation finds resource contention and implements response (model swap, VM resize, or error budget policy).

### Prevention
`scripts/INC-005-slo-budget-check.py` — tracks error budget consumption.
```

Create gitignored:
- `phases/phase-3-fedcompliance-gitops-security/breaks/INC-004-cert-expiry.sh`
- `phases/phase-3-fedcompliance-gitops-security/breaks/INC-005-ollama-latency.sh`
- `phases/phase-3-fedcompliance-gitops-security/solutions/INC-004-cert-expiry-solution.md`
- `phases/phase-3-fedcompliance-gitops-security/solutions/INC-005-ollama-latency-solution.md`
- `phases/phase-3-fedcompliance-gitops-security/postmortems/.gitkeep`

---

### 8. Create Prevention Scripts

`scripts/INC-004-cert-expiry-check.sh` (Bash):
```bash
#!/usr/bin/env bash
# INC-004 Prevention: TLS Certificate Expiry Check
# Incident: phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md → INC-004
# Purpose: Warn when any TLS cert expires within 30 days. Blocks pipeline if expired.
```
- For each endpoint in ENDPOINTS list: `openssl s_client -connect $host:$port` extracts notAfter
- Exits 1 if any cert expires within 30 days or is already expired

`scripts/INC-005-slo-budget-check.py` (Python):
```python
#!/usr/bin/env python3
# INC-005 Prevention: SLO Error Budget Check
# Incident: phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md → INC-005
# Purpose: Calculate remaining error budget. Exit 1 if < 20% remaining.
```
- Queries Prometheus API for `fedplatform_oscap_findings_total` error rate
- Calculates budget consumed against 99.5% SLO target
- Exits 1 if remaining budget < 20%

---

### 9. Update P3 Implementation Guide

**File:** `phases/phase-3-fedcompliance-gitops-security/docs/implementation-guide.md`

Add sections after OKE cluster setup and Helm/ArgoCD content:
- **4-Quadrant Model: Phase 3 Extensions** — what FedTracker gains (compliance + evidence routes), what FedAgent gains (Trivy + Cosign + Jenkins metrics)
- **Step X — Extend FedTracker API (P3 compliance routes)** walkthrough
- **Step X — Extend FedAgent (supply chain metrics)** walkthrough
- **Step X — evidence-collector Function** — event chain from FedAgent scan output
- **Step X — supply-chain-validator Go Function** — OCI Container Registry push trigger
- **Step X — Extend fedplatform-cli (P3 commands)** walkthrough

---

## Verification Gates

1. `fedtracker-app/routes/compliance.py` has section-comment blocks
2. `fedtracker-app/answers/routes/compliance.py` has working GET /compliance/controls/{framework}
3. `fedagent/answers/` has Trivy + Cosign + Jenkins metrics implemented
4. `functions/python/evidence-collector/func.py` is scaffold; `answers/func.py` is complete
5. `functions/go/supply-chain-validator/main.go` compiles: `go build ./...` exits 0
6. `phases/phase-3-fedcompliance-gitops-security/INCIDENTS.md` has INC-004 and INC-005 with Prevention sections
7. `scripts/INC-004-cert-expiry-check.sh` and `scripts/INC-005-slo-budget-check.py` exist and are executable
8. `git status` shows no `answers/`, `breaks/`, `solutions/` tracked
