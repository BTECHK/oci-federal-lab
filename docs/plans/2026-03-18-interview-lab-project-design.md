# AFS Cloud Engineer Interview Lab — Master Project Design
## Three Independent Hands-On Labs for Interview Preparation

**Date:** 2026-03-18 | **Updated:** 2026-03-20
**Target Role:** Accenture Federal Services — Cloud Engineer / Linux Admin (CL9 Specialist)
**Timeline:** ~15 days total (3 phases x 5 days max), 4-8 hours/day
**Budget:** $0-$15 (OCI Always Free tier)
**Execution Partner:** Claude Code (tutor + troubleshooting guide)

---

## DESIGN PRINCIPLES

1. **Three completely independent projects** — each starts from a fresh OCI environment and tears down at the end
2. **Every project covers ALL priority skills** — if you only complete Phase 1, you've touched every topic
3. **Implement + Break + Fix** — every core skill includes intentional troubleshooting practice
4. **You build DevOps/infra by hand** — Terraform, Ansible, Bash, Python scripts, pipeline configs, K8s manifests, Helm charts, Linux admin commands
5. **App code is built by hand** — Python FastAPI apps are scaffolded section-by-section with ELI5 explanations; SQL schemas and seed data are copy-paste with thorough comments
6. **New concepts get full ELI5 treatment** regardless of which phase they appear in — API concepts also get **Interview Insight** boxes explaining how to discuss them in interviews
7. **Returning concepts get abbreviated but followable guidance** — commands listed, ELI5 skipped, references to earlier phases
8. **Guide format follows implementation-guide-generator-prompt.md** — location tags, ELI5 blocks, verification steps, cost checks, troubleshooting tables, command reference tables
9. **AI is a pillar** — one distinct AI integration per phase, different tool and use case each time
10. **Security is a pillar** — one distinct production security concern per phase, different tool each time
11. **Container progression** — Docker/Compose in Phase 1, k3s in Phase 2, K8s+deployment manager in Phase 3
12. **API is a pillar** — one distinct API concept per phase, building from REST fundamentals to webhooks to API auth, with Interview Insight boxes after each new concept

---

## SKILL PRIORITY RANKING (Recruiter-Signal Weighted)

| Tier | # | Skill | Recruiter Signal | JD Signal |
|---|---|---|---|---|
| MUST-HAVE | 1 | Oracle Linux admin | Asked directly | "Linux Admin" in title |
| MUST-HAVE | 2 | OCI infrastructure | Asked directly | "Oracle Cloud Infrastructure" in JD |
| MUST-HAVE | 3 | Terraform | On resume, will be probed | Listed in JD |
| HIGH | 4 | Security hardening | "ensuring security" | Federal role, implicit |
| HIGH | 5 | Cost management | "cost management" explicitly | Listed in JD |
| HIGH | 6 | Disaster recovery | "disaster recovery" explicitly | Listed in JD |
| HIGH | 7 | Ansible | Not mentioned by recruiter | Listed in JD |
| HIGH | 8 | Bash scripting | Implicit in automation | "Automation" in JD |
| MEDIUM | 9 | Jenkins CI/CD | Not mentioned by recruiter | "Cloudbees Jenkins" in JD |
| MEDIUM | 10 | Oracle Database | Not mentioned by recruiter | "Oracle Database" in JD |
| MEDIUM | 11 | Python scripting | Not mentioned | On resume |
| MEDIUM | 12 | Containers/Kubernetes | Industry standard | Implied by modernization focus |
| SPRINKLE | 13 | AI considerations | Company interest, not in JD | Not in JD |

---

## PILLAR OVERVIEW

### AI Pillar — One Per Phase, All Different Tools and Use Cases

| Phase | AI Use Case | Tool (Free) | OCI Native Equivalent | Pattern |
|-------|-------------|-------------|----------------------|---------|
| **1** | Compliance Evidence Collector | **Ollama** (local LLM) | OCI Generative AI Service | Air-gapped local inference |
| **2** | Incident Classification & Response | **OCI Generative AI Service** (Cohere Command or Meta Llama) | OCI Generative AI Service | Cloud-native AI, covered by $300 trial credits |
| **3** | Security Pattern Detection | **scikit-learn** (classical ML) | OCI Anomaly Detection | Statistical ML, no LLM |

**Diversity achieved:** Local LLM (air-gapped), cloud-native LLM (OCI GenAI), classical ML — three completely different approaches.

### Security Pillar — One Per Phase, All Different Tools and Concerns

| Phase | Security Concern | Tool (Free) | Compliance Framework | Pattern |
|-------|-----------------|-------------|---------------------|---------|
| **1** | CIS Baseline Compliance | **OpenSCAP** | CIS Benchmarks | Hardening validation |
| **2** | File Integrity Monitoring | **AIDE** | NIST 800-171 SI-7 | Change detection |
| **3** | Supply Chain Security | **Trivy + Syft SBOM** | EO 14028 | Build pipeline security |

### Container Pillar — Progressive Complexity

| Phase | Container Scope | Tool | Pattern |
|-------|----------------|------|---------|
| **1** | Podman + Docker + Compose | Podman, Docker CE | Podman as Oracle Linux native, Docker for comparison |
| **2** | k3s — "the hard-ish way" | k3s, kubectl, manual YAML | Understand K8s fundamentals |
| **3.1** | Pipeline deploys raw manifests | k3s, kubectl apply via pipeline | Understand what tools abstract away |
| **3.2** | Helm + ArgoCD (production-grade) | Helm charts, ArgoCD GitOps | How real production deployments work |

**Why k3s instead of full K8s:** k3s IS Kubernetes — a fully conformant K8s distribution by Rancher/SUSE packaged as a single ~70MB binary. Same API, same kubectl, same manifests. Full K8s clusters require significant RAM that cloud free tiers don't support. k3s runs a multi-node cluster comfortably on free-tier ARM instances. All K8s knowledge (manifests, kubectl, concepts) transfers 1:1 to managed services (OKE, EKS, GKE, AKS). In production, you'd use the cloud provider's managed K8s service.

**Multi-node k3s setup (2 ARM A1 instances on Always Free tier):**
- **Node 1 (k3s server):** control plane + worker — 2 OCPU / 12 GB RAM (VM.Standard.A1.Flex)
- **Node 2 (k3s agent):** worker only — 2 OCPU / 12 GB RAM (VM.Standard.A1.Flex)
- Both within Always Free tier (4 OCPU / 24 GB total split across 2 instances)
- Real inter-node networking via Flannel VXLAN overlay — pods on different nodes communicate seamlessly
- This gives you actual multi-node K8s experience: node scheduling, cross-node networking, node failure scenarios

**Helm + ArgoCD — complementary, not competitors:**
- **Helm** = K8s package manager. Bundles YAML manifests into reusable, versioned "charts" with templating and values overrides. Think `apt`/`yum` but for K8s apps.
- **ArgoCD** = GitOps continuous delivery. Watches a git repo and automatically syncs desired state to the K8s cluster. Provides UI, rollback, drift detection.
- **In production you use both:** Helm charts (packaging) deployed BY ArgoCD (delivery). Nobody runs raw `kubectl apply` against loose YAML in production.
- **Interview story progression:** "I started with raw manifests and `kubectl apply` in the pipeline so I understand the base layer. Then I refactored to Helm for packaging and ArgoCD for GitOps delivery — that's what production teams actually run."

### API Pillar — Progressive Protocol Mastery

| Phase | API Scope | Concept | Pattern |
|-------|-----------|---------|---------|
| **1** | REST fundamentals | **FastAPI basics, HTTP verbs, Pydantic, status codes** | Build API by hand, full ELI5, OpenAPI/Swagger intro |
| **2** | Webhooks + API Gateway | **OCI Events → webhook → audit action** + OCI API Gateway | Event-driven API patterns, rate limiting intro |
| **3** | API auth + request lifecycle | **API keys + mTLS concepts** | Full request path diagram, Interview Insights on API security |

**Why these concepts:**
- Phase 1: REST is the foundation — every cloud service exposes REST APIs. Build by hand for muscle memory.
- Phase 2: Webhooks = how cloud events trigger actions. OCI API Gateway = managed entry point.
- Phase 3: API auth = production requirement. mTLS = federal/enterprise standard. Full request path = interview gold.

**Interview Insight concept:** After each new API concept, an "Interview Insight" callout box explains how to talk about that concept in an interview — what interviewers are testing for, what a strong answer sounds like, and common mistakes.

---

## PHASE OVERVIEW

| | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| **Theme** | Legacy-to-Cloud Migration | DR Drill & Backup Architecture | CI/CD Modernization & AI-Augmented Ops |
| **Days** | 1-5 | 6-10 | 11-15 |
| **Max Duration** | 5 days | 5 days | 5 days |
| **Difficulty** | Foundation | Intermediate | Advanced |
| **OCI setup** | Manual first, then Terraform | Terraform from the start | Terraform with modules |
| **Ansible depth** | Basic hardening playbook | Drift detection + remediation | Roles + Vault integration |
| **CI/CD pipeline** | Simple validate + deploy (Jenkins) | Scheduled checks pipeline | Multi-stage with security scanning |
| **Python focus** | OCI SDK cost script + AI evidence collector | Log correlator + cost modeler | OCI Function + compliance reporter |
| **Linux depth** | Fundamentals | Operational troubleshooting | Advanced tuning + systemd |
| **AI pillar** | Ollama evidence collector | OCI Generative AI incident classifier | scikit-learn pattern detection |
| **Security pillar** | OpenSCAP CIS scanning | AIDE file integrity | Trivy + SBOM supply chain |
| **Container pillar** | Podman + Docker + Compose | k3s hard-ish way | 3.1: pipeline + kubectl apply, 3.2: Helm + ArgoCD |
| **Core narrative** | "Build it right" | "Break it, fix it" | "Automate everything" |

---

## PHASE 1: LEGACY-TO-CLOUD MIGRATION ON OCI

### Scenario
A federal agency has been running an internal personnel tracking application on a manually-configured Oracle Linux server. No IaC, no automated deployments, no proper security hardening. You migrate this to a properly architected OCI environment, containerize the app, validate CIS compliance, and generate AI-assisted compliance evidence.

### Pre-Built App: "FedTracker"
Simple Python FastAPI application (~200 lines) built section-by-section with thorough inline comments:
- **POST /personnel** — create new personnel record (Pydantic: PersonnelCreate with name, role, clearance_level, project_id)
- **GET /personnel** — list all personnel with pagination (query params: skip, limit)
- **GET /personnel/{id}** — get single personnel record
- **GET /audit** — view audit log entries with date filtering
- **POST /audit/export** — export audit log as CSV
- **GET /health** — service health check with DB connectivity status
- Connects to Oracle Autonomous DB via python-oracledb
- Every action writes to audit_log table (CMMC AU controls)
- Runs as a systemd service (Day 1-3), then as Docker container (Day 4)
- SQL schema with tables: `projects`, `personnel`, `audit_log` + seed data + audit trigger

### Target Architecture

```
Internet
    |
+---v--------------------------------------------------+
|  OCI VCN: 10.0.0.0/16                                |
|                                                        |
|  +---------------------------+                        |
|  | Public Subnet 10.0.1.0/24 |                        |
|  |  Bastion/CI VM              |                        |
|  |  (Oracle Linux 8)          |                        |
|  +-------------+-------------+                        |
|                |                                       |
|  +-------------v--------------+                       |
|  | Private Subnet 10.0.2.0/24 |                       |
|  |  App Server VM              |                       |
|  |  (Oracle Linux 8)           |                       |
|  |  Docker + FedTracker        |                       |
|  +-------------+--------------+                       |
|                |                                       |
|  +-------------v--------------+                       |
|  | Oracle Autonomous DB        |                       |
|  | (Always Free)               |                       |
|  +----------------------------+                       |
|                                                        |
|  Object Storage: backups, cost reports, evidence       |
+--------------------------------------------------------+
```

### Day 1 (~6-8 hrs): "The Legacy Server"

**Implementation:**
- Create OCI account, compartment, non-root IAM user with appropriate policies
- Set up basic VCN (manual via console) — public subnet, internet gateway, security lists
- Configure SSH key pairs
- Enable billing alerts (cost protection)
- Launch Oracle Linux 8 VM in public subnet (the "legacy" server)
- Linux admin fundamentals: users, permissions, packages, services, firewall, disk mounting, log review
- Manually install app stack (Python, FastAPI, Oracle DB client)
- Deploy FedTracker the messy way — no automation, everything by hand
- Write Bash health check script (by hand)
- Write Python script using OCI SDK for resource/cost data (by hand)

**Troubleshooting:**
- Misconfigure firewalld (block app port) -> app unreachable -> diagnose with `ss`, `journalctl`, `firewall-cmd` -> fix
- Create user with wrong permissions -> app can't read files -> diagnose with `ls -la`, audit logs -> fix
- Stop FastAPI service -> diagnose via `systemctl status`, logs -> restart and enable

**Skills touched:** Oracle Linux admin, OCI basics, IAM setup, Bash scripting, Python scripting, Oracle DB (connect + query)

### Day 2 (~6-8 hrs): "The Proper Architecture"

**Implementation:**
- Design target architecture: VCN with public/private subnets, bastion, NAT gateway, security lists, NSGs
- Build it all manually via OCI console
- Launch new Oracle Linux 8 VM in private subnet
- Set up Oracle Autonomous DB (free tier), connect from VM, run schema scripts
- Security hardening: SSH key-only auth, disable root login, firewalld rules, auditd, login banner
- Implement cost tagging strategy on all resources
- IAM policies: admin group, operator group, auditor group (least privilege)

**Troubleshooting:**
- Misconfigure security list (block SSH or HTTP) -> can't connect -> diagnose via console + `ping`/`traceroute` -> fix
- Wrong route table (private subnet -> internet gateway instead of NAT) -> can't reach internet for updates -> diagnose -> fix
- IAM policy too restrictive -> user can't launch resources -> diagnose error -> adjust policy

**Skills touched:** OCI infra (deep), security hardening, cost management, Oracle DB, Oracle Linux admin

### Day 3 (~6-8 hrs): "Automate Everything"

**Implementation:**
- Write Terraform from scratch to codify Day 2 architecture (section by section, full ELI5)
  - provider.tf, variables.tf, network.tf, compute.tf, outputs.tf
- Write Ansible playbook to automate Linux hardening + app deployment
  - inventory.ini, harden_oracle_linux.yml, deploy_app.yml
- Destroy Day 2 environment
- Recreate entirely with `terraform apply` + `ansible-playbook` to prove it works

**Troubleshooting:**
- Terraform variable typo -> `terraform plan` fails -> read error -> fix
- Terraform state drift: manually change something in console -> run `terraform plan` -> see diff -> reconcile
- Ansible SSH connection failure (wrong key/user) -> diagnose from error output -> fix
- Ansible idempotency test: run playbook twice -> confirm no unintended changes

**Skills touched:** Terraform, Ansible, OCI infra (via code), Oracle Linux admin (via automation)

### Day 4 (~6-8 hrs): "Containerize & Secure"

**Implementation:**
- **NEW CONCEPT:** Podman fundamentals — full ELI5
  - What is Podman? (Docker alternative — daemonless, rootless, no Docker daemon running as root)
  - Podman is what Oracle Linux and RHEL ship by default — Docker is NOT in the repos
  - Same CLI as Docker (podman build, podman run, podman push)
  - Build FedTracker with Podman: `podman build -t fedtracker .`
  - Run with Podman: `podman run -d -p 5000:5000 fedtracker`
  - Why Podman matters: rootless by default (security), daemonless (no 140MB daemon overhead), Red Hat/federal standard
- Docker comparison (~30 min):
  - Install Docker CE, build same Dockerfile: `docker build -t fedtracker .`
  - Note: same Dockerfile, same image, different runtime (daemon vs daemonless)
  - Key difference: Docker uses containerd under the hood; Podman uses conmon + runc directly
  - *Interview line: "On Oracle Linux, I used Podman because that's what RHEL-based systems ship. Same Dockerfile works with both."*
- **NEW CONCEPT:** Docker Compose — full ELI5
  - Write docker-compose.yml with app service (container points to Autonomous DB)
  - `docker-compose up/down`, logs, exec into container
  - Note: Podman also supports `podman-compose` but Docker Compose is more mature
- **NEW CONCEPT:** OpenSCAP CIS benchmark scanning — full ELI5
  - Install OpenSCAP on Oracle Linux 8
  - Run CIS Oracle Linux 8 benchmark scan -> HTML compliance report
  - Bash script to automate: run scan, parse results, log pass/fail count
  - Remediate top 5 failures manually
- **NEW CONCEPT:** AI-Powered Compliance Evidence Collector — full ELI5
  - Install Ollama on compute instance, pull small model (mistral:7b or llama3:8b)
  - Python script collects system evidence: CIS scan results, SSH config, firewall rules, IAM state, service status
  - Feeds evidence to Ollama -> generates narrative summary per control family
  - Output: Markdown evidence package organized by compliance control families
  - *In production: OCI Generative AI Service. Lab: Ollama (free, air-gapped capable)*

**Troubleshooting:**
- Docker build fails (missing dependency in Dockerfile) -> read build output -> fix
- Container can't connect to DB (network mode issue) -> diagnose -> fix
- OpenSCAP scan shows unexpected failures -> research CIS control -> remediate or document exception
- Ollama model too large for instance memory -> switch to smaller model or quantized version

**Skills touched:** Podman (new), Docker, Docker Compose, OpenSCAP (new), Ollama/AI (new), Python (deep), security compliance

### Day 5 (~4-6 hrs): "Pipeline & Operations"

**Implementation:**
- **NEW CONCEPT:** OCI Functions (serverless) — full ELI5
  - What is serverless? (upload code, cloud runs it, you pay per invocation, no server to manage)
  - How OCI Functions compares to AWS Lambda (same concept, built on open-source Fn Project — less vendor lock-in)
  - Python function: audit file processor
    - Trigger: file uploaded to Object Storage "audit-evidence" bucket → OCI Events → triggers Function
    - Function reads the file, runs basic validation, writes summary to another bucket
    - ~30 lines of Python
  - Bash-in-Docker function: health check automation
    - Custom Docker image with Bash script that checks VM health endpoints
    - Trigger: OCI Alarm (CPU > 80%) → Notification → Function
    - ~20 lines of Bash in a Dockerfile
  - Verify: upload file → see function trigger → see output in Object Storage
  - Cost: $0 (2 million invocations/month free — more generous than Lambda)
- Install Jenkins on bastion VM (or separate VM)
- Build pipeline config: validate Terraform -> Ansible lint -> deploy containerized app
- Block volume backup of app server
- Restore drill: destroy VM -> restore from backup -> validate
- Write DR runbook
- Python cost reporting script (OCI SDK)
- Tear down all resources

**Troubleshooting:**
- Pipeline fails due to missing credential -> read console output -> add credential -> rerun
- Corrupt app deployment (wrong env variable) -> pipeline "succeeds" but app broken -> diagnose from app logs -> fix
- DR drill: terminate VM -> recover via Terraform + Ansible -> validate app works

**Skills touched:** OCI Functions (new), CI/CD pipeline, DR/backup, Bash, Python, cost management

---

## PHASE 2: DISASTER RECOVERY DRILL & BACKUP ARCHITECTURE

### Scenario
A federal contractor's analytics database suffered a simulated ransomware event. You build a resilient environment, implement immutable backup architecture, deploy on Kubernetes, then intentionally destroy things and prove recovery within defined RTO/RPO targets. AI-assisted incident classification automates first-pass triage.

### Pre-Built App: "FedAnalytics"
Python FastAPI data ingestion service (~180 lines) built section-by-section with thorough inline comments:
- **POST /ingest** — ingest CSV data batch (Pydantic: IngestRequest with source, data_type, records list)
- **GET /ingest/status** — pipeline status and last run timestamp
- **POST /webhook** — receive OCI Events webhook notifications (validates signature, triggers audit action)
- **GET /logs** — query generated log entries with severity filtering
- **GET /metrics** — basic pipeline metrics (records processed, error count)
- **GET /health** — service health
- Reads CSV data and writes to Oracle Autonomous DB
- Generates realistic log entries (access logs, error logs, audit events)
- Runs as systemd service (Day 1-2), then on k3s (Day 3+)

### Day 1 (~6-8 hrs): "Build the Environment Fast"

**Implementation:**
- Fresh OCI: VCN, subnets, compute, Autonomous DB — Terraform from the start (returning, abbreviated guidance)
- Deploy FedAnalytics via Ansible (returning, abbreviated)
- Seed database with federal analytics data
- **NEW CONCEPT:** OCI Object Storage with versioning and retention locks (immutable backups) — full ELI5 + walkthrough
- **NEW CONCEPT:** OCI Object Storage lifecycle policies — full walkthrough

**Troubleshooting:**
- Terraform provider auth failure (wrong API key fingerprint) -> read error -> fix
- Ansible can't reach private VM (security list missing SSH rule) -> diagnose -> fix

**Skills touched:** Terraform (reps), Ansible (reps), OCI infra (reps), Oracle DB, OCI Object Storage (new)

### Day 2 (~6-8 hrs): "Backup Architecture & Monitoring"

**Implementation:**
- Write Bash backup automation script: DB export -> Object Storage upload (by hand)
- **NEW CONCEPT:** Python log correlator (by hand) — parses `/var/log/messages`, auditd, app logs, flags anomalies (failed SSH, privilege escalation, unusual DB queries) — full ELI5 on log formats + parsing
- **NEW CONCEPT:** cron jobs for scheduled backups and log collection — full ELI5
- **NEW CONCEPT:** Ansible drift detection (`--check` mode against baseline) — full ELI5
- CI/CD pipeline: scheduled backup validation + drift check (returning pipeline config, new scheduling concept)
- **NEW CONCEPT:** AIDE file integrity monitoring — full ELI5
  - Install AIDE, initialize baseline database
  - Configure to monitor: `/etc`, `/usr/bin`, `/var/www`, app directories
  - Run initial check to confirm clean baseline

**Troubleshooting:**
- Cron job doesn't execute (permission issue) -> diagnose via `/var/log/cron` -> fix
- Python script crashes on malformed log line -> read traceback -> add error handling
- Backup script fails silently (wrong Object Storage bucket name) -> diagnose -> fix

**Skills touched:** Bash, Python, cron (new), Ansible drift detection (new), AIDE (new), CI/CD pipeline, Oracle Linux admin (logs deep dive)

### Day 3 (~6-8 hrs): "Kubernetes the Hard-ish Way"

**Implementation:**
- **NEW CONCEPT:** Multi-node k3s cluster setup — full ELI5
  - Terraform provisions 2 ARM A1 instances (2 OCPU / 12 GB each) or add second instance to existing Terraform
  - Install k3s server on Node 1, retrieve join token
  - Install k3s agent on Node 2, join to cluster using token
  - Verify: `kubectl get nodes` shows 2 nodes Ready
  - Understand components: API server, scheduler, etcd, kubelet, Flannel VXLAN overlay
  - `kubectl` basics: get, describe, logs, exec, port-forward
- **NEW CONCEPT:** Kubernetes manifests by hand — full ELI5
  - Write Deployment YAML for FedAnalytics (by hand, every field explained)
  - Write Service YAML (NodePort to expose app)
  - Write ConfigMap for app configuration
  - Write Secret for DB credentials
  - NO Helm, NO shortcuts — understand what each field does
- Deploy FedAnalytics to k3s, verify from outside the cluster
- Practice: scale replicas, rolling update, rollback
- **NEW CONCEPT:** Inter-node networking exercises — full ELI5
  - Deploy pods on both nodes, `curl` between them to prove overlay network works
  - `kubectl get pods -o wide` to see node placement
  - Use `nodeSelector` to pin a pod to a specific node
  - Trace a request: external → NodePort on Node 1 → Service → Pod on Node 2
  - **Optional stretch:** NetworkPolicy — restrict which pods can communicate across nodes

**Troubleshooting:**
- Pod stuck in CrashLoopBackOff -> `kubectl logs`, `kubectl describe pod` -> fix
- Service not routing traffic -> wrong selector label -> diagnose -> fix
- Secret mounted but app can't read (wrong mount path) -> diagnose -> fix
- k3s agent can't join cluster (firewall blocking port 6443) -> diagnose -> open port in OCI security list -> rejoin
- Pod-to-pod cross-node communication fails (Flannel VXLAN port 8472 blocked) -> diagnose -> fix security list

**Skills touched:** Kubernetes fundamentals (new), kubectl (new), YAML manifests (new), multi-node networking (new), container orchestration

### Day 4 (~6-8 hrs): "Break Everything, Recover Everything"

**Implementation:**
- **Simulate ransomware:** delete DB tables, corrupt app config, stop services, modify monitored files
- Run AIDE check -> see exactly what files were altered during the attack
- Python script parses AIDE report -> logs changes to app_logs table
- Recover DB from Object Storage backup, validate row counts and integrity
- Recover app server: `terraform destroy` -> `terraform apply` -> Ansible re-hardening -> redeploy to k3s
- Measure and document actual RTO
- **AI Pillar:** Incident Classification & Automated Runbook
  - Python script captures incident indicators: AIDE file changes, backup status, service health, log anomalies
  - Sends incident summary to OCI Generative AI Service (Cohere Command or Meta Llama) -> model classifies incident type and recommends response steps
  - Auto-generates incident response report (who/what/when/impact/actions taken)
  - *Uses OCI Generative AI Service directly — cloud-native, covered by $300 OCI trial credits*
- **Simulate configuration drift:** manually change firewall rules + SSH config -> Ansible drift detection -> auto-remediate

**Troubleshooting:**
- DB restore fails (wrong wallet config after re-provision) -> diagnose connection error -> fix
- Ansible remediation has task ordering bug -> diagnose -> fix task order
- Backup too old (intentionally skip a backup cycle) -> understand RPO implications -> document

**Skills touched:** DR/backup (core focus), AIDE (applied), AI incident response (new), Terraform (reps), Ansible (reps), security

### Day 5 (~4-6 hrs): "Operational Hardening & Teardown"

**Implementation:**
- **NEW CONCEPT:** Log rotation and retention policies — full ELI5
- Python cost modeling script: calculates backup storage costs over 30/60/90 day retention (by hand)
- Full end-to-end drill: destroy everything -> Terraform apply -> Ansible configure -> deploy to k3s -> validate app + DB + backups
- Write incident response report and DR runbook
- Document lessons learned
- Tear down

**Troubleshooting:**
- Log rotation misconfigured (logs fill disk) -> diagnose disk usage -> fix rotation config
- End-to-end rebuild has ordering issue (DB not ready when app tries to connect) -> add retry logic or wait

**Skills touched:** Python, cost management, K8s (reps), full-stack validation, documentation

---

## PHASE 3: CI/CD PIPELINE MODERNIZATION & AI-AUGMENTED OPERATIONS

### Scenario
A federal team has been deploying their compliance reporting tool manually — SSHing in, pulling code, restarting services. No audit trail, no security scanning, hardcoded secrets. You build a full CI/CD pipeline that deploys to Kubernetes with Helm, implements supply chain security (SBOM), and adds AI-powered security pattern detection.

### Pre-Built App: "FedCompliance"
Containerized Python FastAPI application (~200 lines) built section-by-section with thorough inline comments:
- **GET /compliance/status** — overall compliance dashboard (returns control counts by status)
- **GET /compliance/controls/{framework}** — list controls for CMMC/NIST framework
- **POST /compliance/scan** — trigger compliance scan (Pydantic: ScanRequest with scope, framework)
- **GET /compliance/report** — generate compliance report with findings
- **POST /auth/validate** — validate API key and return permissions (API auth practice)
- **GET /health** — service health
- Compliance status dashboard reading from Oracle DB
- Intentional dependency vulnerabilities for scanning practice
- Simple log query interface (for AI integration)
- Dockerfile provided
- Runs via Docker -> deployed to k3s via Helm

### Day 1 (~6-8 hrs): "Environment & Secure Foundations"

**Implementation:**
- Fresh OCI via Terraform (returning, abbreviated)
- **NEW CONCEPT:** Terraform modules — refactor flat .tf files into network module, compute module, database module — full ELI5 + section-by-section
- Deploy Oracle Linux VM + Autonomous DB via modules
- Ansible hardening (returning, abbreviated)
- **NEW CONCEPT:** OCI Vault for secrets management — full ELI5 + walkthrough
- **NEW CONCEPT:** Ansible Vault integration — pull secrets from OCI Vault — full walkthrough
- Deploy FedCompliance using secrets from Vault
- Set up 2-node k3s cluster (returning, abbreviated — server + agent pattern from Phase 2)

**Troubleshooting:**
- Terraform module reference error (wrong output variable) -> read error -> fix
- App fails to start (OCI Vault policy doesn't grant read access to compute) -> diagnose from logs -> fix IAM policy
- Module dependency issue (compute depends on network but not declared) -> Terraform error -> add `depends_on`

**Skills touched:** Terraform modules (new), OCI Vault (new), Ansible Vault (new), k3s (reps), OCI infra (reps), Oracle Linux (reps)

### Day 2 (~6-8 hrs): "The Pipeline + Raw K8s Deploy" (Stage 3.1)

**Why raw manifests first:** Before using Helm or ArgoCD, deploy with raw `kubectl apply` through the pipeline. This ensures you understand exactly what those tools abstract away. An interviewer who sees you jump straight to Helm might wonder if you understand the underlying mechanics.

**Implementation:**
- Install Jenkins (returning, abbreviated) — *Note: This OCI project uses Jenkins. Future projects will use GitLab CI, GitHub Actions, etc. per Rule 14.*
- **NEW CONCEPT:** Multi-stage pipeline with approval gates — full ELI5 + section-by-section pipeline config:
  1. Checkout
  2. Terraform validate + plan
  3. **NEW CONCEPT:** Trivy container security scanning — full ELI5
  4. **NEW CONCEPT:** SBOM generation with Syft — full ELI5
     - Generate SPDX SBOM: `syft <image> -o spdx-json`
     - Store SBOM artifact alongside container image
     - *Interview talking point: EO 14028 requires SBOM for all federal software*
  5. Ansible lint
  6. Manual approval gate
  7. Build + push Docker image to OCIR
  8. `kubectl apply -f k8s/` — deploy raw manifests to k3s
  9. Smoke test
- **NEW CONCEPT:** Pipeline credentials management (OCI config, SSH keys, Vault tokens, kubeconfig) — full walkthrough
- Verify: app running on k3s, deployed entirely through pipeline

**Troubleshooting:**
- Trivy finds critical CVE in base image -> pipeline blocks -> update Dockerfile base image -> rerun
- Approval gate times out -> understand federal deployment approval requirements -> rerun
- Pipeline can't authenticate to OCI (wrong credential ID) -> diagnose -> fix
- `kubectl apply` fails in pipeline (kubeconfig not mounted correctly) -> diagnose -> fix

**Skills touched:** CI/CD pipeline (deep, new patterns), Trivy (new), Syft SBOM (new), pipeline+K8s integration, container security

### Day 3 (~6-8 hrs): "Helm + ArgoCD — Production-Grade Delivery" (Stage 3.2)

**Why this progression matters:** Day 2 deployed with raw `kubectl apply`. Now refactor to how production teams actually do it: Helm packages the app, ArgoCD delivers it via GitOps. The pipeline no longer runs `kubectl` directly — ArgoCD watches the git repo and syncs automatically.

**Implementation:**
- **NEW CONCEPT:** Helm fundamentals — full ELI5
  - Understand charts, templates, values.yaml
  - Create a Helm chart for FedCompliance (by hand, every template explained)
  - templates/deployment.yaml, templates/service.yaml, templates/configmap.yaml, templates/secret.yaml
  - values.yaml with environment-specific overrides
- Deploy FedCompliance to k3s via Helm (manual first)
- **NEW CONCEPT:** Helm lifecycle — full ELI5
  - `helm install`, `helm upgrade`, `helm rollback`, `helm history`
  - Demonstrate: push a bad config -> `helm rollback` -> app restored
- **NEW CONCEPT:** ArgoCD fundamentals — full ELI5
  - Install ArgoCD on k3s cluster
  - Understand GitOps pattern: git repo = source of truth, ArgoCD syncs cluster state to match
  - Create ArgoCD Application pointing to the Helm chart in your git repo
  - Demonstrate: push a change to git -> ArgoCD auto-detects -> syncs to cluster
  - ArgoCD UI: view sync status, health, diff, rollback
- Update pipeline: pipeline now builds image + pushes to OCIR + updates Helm values in git. ArgoCD handles the actual K8s deployment.
- Practice: rolling update via Helm values change -> ArgoCD auto-sync

**Troubleshooting:**
- Helm template rendering error (wrong indentation in YAML) -> `helm template --debug` -> fix
- ArgoCD Application stuck "OutOfSync" -> check diff in UI -> fix manifest -> ArgoCD re-syncs
- ArgoCD can't reach git repo (SSH key not configured) -> diagnose -> fix
- Helm release stuck in PENDING -> `helm rollback` -> investigate -> redeploy

**Skills touched:** Helm (new), ArgoCD (new), GitOps patterns (new), K8s deployment patterns (new), container orchestration

### Day 4 (~6-8 hrs): "AI-Augmented Operations & Compliance"

**Implementation:**
- **OCI Functions (serverless)** (returning from Phase 1 — abbreviated)
- Write Python OCI Function by hand: pulls logs from app_logs table -> processes with AI -> writes summary to Object Storage
- **AI Pillar:** Security Pattern Detection with scikit-learn
  - Python script analyzes app_logs: unusual access times, error rate spikes, new source IPs, privilege changes
  - Uses scikit-learn IsolationForest for anomaly scoring on numerical features
  - Rule engine flags known-bad patterns (brute force signatures, privilege escalation sequences)
  - Generates a security digest with scored findings
  - *In production: OCI Anomaly Detection Service. Lab: scikit-learn (free, no API costs)*
  - *Interview talking point: "Not everything needs an LLM. Classical ML is appropriate for air-gapped and cost-sensitive environments."*
- **NEW CONCEPT:** Compliance-as-code evidence collector — Python script by hand: queries OCI APIs (IAM policies, security lists, encryption, audit log config) -> outputs CMMC control mapping report
- Add compliance collector as CI/CD pipeline stage

**Troubleshooting:**
- OCI Function deployment fails (wrong runtime version) -> diagnose from function logs -> fix
- scikit-learn model flags too many false positives -> adjust contamination parameter -> retrain
- Compliance script returns incomplete data (paginated OCI API results) -> diagnose -> fix pagination

**Skills touched:** OCI Functions (new), scikit-learn (new), Python (deep), AI integration (new), compliance automation (new)

### Day 5 (~4-6 hrs): "End-to-End Validation & Teardown"

**Implementation:**
- Full end-to-end flow: code push -> pipeline -> security scan + SBOM -> approval -> image push to OCIR -> Helm values updated in git -> ArgoCD auto-syncs to k3s -> compliance report -> AI security digest
- **NEW CONCEPT:** Pre-commit hooks with detect-secrets — full walkthrough
- Bash teardown script (clean destroy in reverse order: ArgoCD apps -> Helm releases -> k3s -> Terraform)
- Document pipeline architecture and decisions
- Tear down

**Troubleshooting:**
- Pre-commit hook blocks a commit with a false positive -> understand how to configure allowlists -> fix
- Full pipeline has a race condition (deploy before scan completes) -> diagnose stage ordering -> fix

**Skills touched:** End-to-end CI/CD, secrets hygiene (new), Helm (reps), K8s (reps), documentation, Bash

---

## NEW VS RETURNING CONCEPTS BY PHASE

### Phase 1 — Everything is New
ALL concepts get full ELI5 + scaffolded build treatment.

Includes: OCI account bootstrap, VCN, compute, Autonomous DB, Oracle Linux admin, Terraform basics, Ansible basics, Jenkins basics, Podman, Docker, Docker Compose, OCI Functions, OpenSCAP, Ollama AI, Bash scripting, Python OCI SDK

### Phase 2 — New Concepts (Full Documentation)
- OCI Object Storage versioning + retention locks
- OCI Object Storage lifecycle policies
- Python log parsing and correlation
- cron job scheduling
- Ansible drift detection (--check mode)
- AIDE file integrity monitoring
- k3s installation and Kubernetes fundamentals
- Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
- kubectl operations
- AI incident classification with OCI Generative AI Service
- Log rotation and retention
- DR drill methodology (RTO/RPO measurement)
- Backup automation patterns

### Phase 2 — Returning Concepts (Abbreviated)
- OCI VCN/subnet/compute setup (Terraform)
- Ansible playbook basics
- CI/CD pipeline basics
- firewalld, user management
- Oracle DB connection and queries
- Docker basics (building/running images)

### Phase 3 — New Concepts (Full Documentation)
- Terraform modules (reusable patterns)
- OCI Vault (secrets management)
- Ansible Vault integration
- Multi-stage CI/CD pipeline with approval gates
- Trivy container security scanning
- Syft SBOM generation (EO 14028)
- Pipeline credentials management
- Pipeline -> raw kubectl apply -> K8s deployment (Stage 3.1)
- Helm chart creation and lifecycle (Stage 3.2)
- ArgoCD GitOps delivery (Stage 3.2)
- Pipeline -> image build -> ArgoCD auto-sync pattern
- OCI Functions (serverless)
- scikit-learn anomaly detection for security
- Compliance-as-code evidence collection
- Pre-commit hooks (detect-secrets)

### Phase 3 — Returning Concepts (Abbreviated)
- Full OCI environment setup via Terraform
- k3s setup and kubectl
- Ansible hardening playbooks
- CI/CD pipeline setup
- Bash scripting, Python scripting
- Oracle Linux service management
- Docker image building
- OCI Object Storage

---

## PILLAR DETAIL: AI INTEGRATION

### Phase 1: AI-Powered Compliance Evidence Collector (Ollama)
- **What:** Python script auto-collects system evidence (CIS scan results, SSH config, firewall rules, IAM state, service status, disk encryption) and feeds it to a local LLM to generate narrative evidence summaries per compliance control family.
- **Output:** Markdown evidence package ready for assessor review.
- **Tool:** Ollama running mistral:7b or llama3:8b locally on compute instance.
- **OCI native equivalent:** OCI Generative AI Service (FedRAMP High authorized).
- **Why local:** Demonstrates air-gapped AI capability — evidence data never leaves the instance. This matters for classified environments.
- **Interview framing:** "I automated the most painful part of ATO — evidence collection. The script scrapes 15 system configs and generates draft evidence narratives. In production, this would use OCI GenAI Service; I used Ollama to demonstrate air-gapped capability."

### Phase 2: AI-Assisted Incident Classification & Response (OCI Generative AI Service)
- **What:** During DR drill, Python script captures incident indicators (AIDE file changes, backup status, service health, log anomalies), sends to OCI Generative AI Service, model classifies incident type (ransomware, data corruption, insider threat) and recommends response steps. Auto-generates incident response report.
- **Output:** Classified incident type + recommended runbook + IR report.
- **Tool:** OCI Generative AI Service (Cohere Command or Meta Llama via oci.generative_ai_inference SDK).
- **Why OCI GenAI:** Cloud-native, covered by $300 trial credits, same service used in production. No third-party API dependency.
- **Interview framing:** "During the DR drill, my AI tool classified the incident in seconds and generated a draft IR report. I used OCI Generative AI Service — the same cloud-native service you'd use in production."

### Phase 3: Security Pattern Detection (scikit-learn)
- **What:** Python script analyzes app_logs using IsolationForest for anomaly scoring on numerical features (request frequency, error rates, access times) plus a rule engine for known-bad patterns (brute force, privilege escalation). Generates daily security digest with scored findings.
- **Output:** Security digest with anomaly scores and flagged patterns.
- **Tool:** scikit-learn (free, open-source, no API costs).
- **OCI native equivalent:** OCI Anomaly Detection Service (MSET2-based).
- **Why classical ML:** Shows you know when NOT to use generative AI. Statistical anomaly detection is cheaper, faster, and runs without network connectivity. Air-gap friendly.
- **Interview framing:** "Not everything needs an LLM. I built a lightweight anomaly detector using classical ML — runs with zero API costs, zero network dependency. Appropriate for air-gapped and budget-constrained environments."

---

## PILLAR DETAIL: SECURITY

### Phase 1: CIS Baseline Compliance with OpenSCAP
- **What:** Install OpenSCAP, run CIS Oracle Linux 8 benchmark, generate HTML compliance report, remediate top findings.
- **Tool:** OpenSCAP + scap-security-guide (free, installed from Oracle Linux repos).
- **Why it fits Phase 1:** First thing after migration = prove the instance meets baseline security. This is standard for any FedRAMP environment.
- **Combines with:** Linux admin (remediation), Bash scripting (automation), AI pillar (evidence collection feeds CIS results to Ollama).

### Phase 2: File Integrity Monitoring with AIDE
- **What:** Install AIDE, initialize baseline, monitor critical paths. During ransomware sim, AIDE detects exactly what changed. Python script parses AIDE report.
- **Tool:** AIDE (free, installed from Oracle Linux repos).
- **Why it fits Phase 2:** NIST 800-171 SI-7 requires file integrity verification. During DR, you need to know WHAT was compromised to validate the restore is clean.
- **Combines with:** DR drill (evidence of compromise), Python scripting (report parsing), AI pillar (AIDE results feed into incident classification).

### Phase 3: Supply Chain Security with Trivy + Syft SBOM
- **What:** Trivy scans container images for CVEs. Syft generates SPDX-format SBOM. Both integrated into CI/CD pipeline. SBOMs stored as compliance artifacts.
- **Tools:** Trivy (free), Syft (free, Anchore open source).
- **Why it fits Phase 3:** EO 14028 mandates SBOM for all federal software. Supply chain security is THE hot topic in federal DevSecOps.
- **Combines with:** CI/CD pipeline (automated gates), container security, compliance automation.

---

## COST STRATEGY

All three phases use OCI Always Free tier:
- Compute: VM.Standard.A1.Flex (ARM) — 4 OCPUs, 24 GB RAM total (free) — split into 2 nodes (2 OCPU/12GB each) for multi-node k3s cluster
- Compute: VM.Standard.E2.1.Micro (x86) — 2 instances (free)
- Autonomous Database: 2 instances, 20 GB each (free)
- Object Storage: 10 GB (free)
- Block Volume: 200 GB (free)
- Load Balancer: 1 instance (free)
- VCN + networking: free
- OCI Functions: 2M invocations/month (free)
- OCI Vault: 20 key versions (free)

**AI costs:** $0 — Ollama is local/free, Groq has free tier, scikit-learn is a Python library.
**Security tool costs:** $0 — OpenSCAP, AIDE, Trivy, Syft are all open-source.
**K8s costs:** $0 — k3s runs on existing compute instances.

**Critical:** Tear down all non-Always-Free resources at end of each phase. Terraform destroy handles this.

**Estimated total cost across all 3 phases: $0-$15**

---

## DELIVERABLES PER PHASE

Each phase produces a GitHub-ready repository:

```
phase-N-project-name/
+-- README.md                     # What you built, architecture, decisions
+-- terraform/
|   +-- provider.tf
|   +-- variables.tf
|   +-- network.tf
|   +-- compute.tf
|   +-- outputs.tf
|   +-- (Phase 3: modules/)
+-- ansible/
|   +-- inventory.ini
|   +-- playbooks/
|       +-- harden.yml
|       +-- deploy.yml
+-- pipeline/
|   +-- Jenkinsfile               # OCI project uses Jenkins; future projects vary
+-- k8s/                          # Phase 2-3
|   +-- deployment.yaml
|   +-- service.yaml
|   +-- configmap.yaml
|   +-- secret.yaml
|   +-- (Phase 3: helm/)
+-- scripts/
|   +-- health_check.sh
|   +-- [phase-specific].sh
|   +-- [phase-specific].py
+-- app/
|   +-- main.py                   # Pre-built, well-commented
|   +-- requirements.txt
|   +-- Dockerfile
|   +-- docker-compose.yml        # Phase 1
+-- sql/
|   +-- schema.sql
|   +-- seed_data.sql
+-- docs/
    +-- architecture.md
    +-- troubleshooting-log.md    # Document what you broke and fixed
    +-- [dr-runbook/incident-report/pipeline-docs].md
    +-- evidence/                 # AI-generated compliance evidence
```

---

## META RULES FOR CROSS-PLATFORM ADAPTATION

These rules govern generating equivalent projects for AWS, GCP, and Azure.

### RULE 1: THREE-PHASE STRUCTURE (flexible)
Phases represent progressive complexity, not fixed topics.

**Default federal template:**
- Phase 1 = Migrate + Harden (foundation)
- Phase 2 = Resilience + Recovery (intermediate)
- Phase 3 = Automation + Compliance (advanced)

**Alternative structures (generated per use case):**
- Analytics-focused: Ingest -> Transform -> Visualize/ML
- Platform-focused: Deploy -> Scale -> Observe
- Security-focused: Harden -> Detect -> Respond
- Data-focused: Store -> Process -> Serve

The constant: Phase 1 = small scope, Phase 2 = more moving parts, Phase 3 = ties it all together.

### RULE 2: SKILL PILLARS (repeated every phase, different tool)
- IaC: Terraform (universal across clouds)
- Config Management: Ansible (universal across clouds)
- Scripting: Bash + Python (universal)
- AI: 1 integration per phase, DIFFERENT approach each time
- Security: 1 production concern per phase, DIFFERENT tool each time

### RULE 3: AI DIVERSITY ACROSS PHASES
- Phase 1 = Local/edge inference (no cloud API dependency)
- Phase 2 = Cloud AI API (demonstrates managed service integration)
- Phase 3 = Classical ML / statistical (shows when NOT to use generative AI)

### RULE 4: SECURITY DIVERSITY ACROSS PHASES
- Phase 1 = Hardening & baseline compliance (CIS/STIG)
- Phase 2 = Integrity monitoring & incident detection
- Phase 3 = Supply chain & secrets management

### RULE 5: COST NORTH STAR
- Default: Cloud-native tool
- If paid: Swap for free/open-source equivalent
- Document: "In production -> [native tool]. Lab -> [free alternative]"

### RULE 6: FEDERAL THEMES (when applicable)
- Each phase addresses a REAL federal challenge scenario
- Use actual compliance frameworks (CMMC, FedRAMP, NIST, EO 14028)
- App data should reflect realistic government use cases
- NOT required for non-government-focused projects (see Rule 13)

### RULE 7: APP TIER PATTERN
- Simple FastAPI app -> cloud-native DB -> REST API
- Each phase = different app with different domain data
- Apps are COPY-PASTE with comments; infra is HAND-BUILT

### RULE 8: PLATFORM SUBSTITUTION MAP
```
                    OCI                  AWS                    GCP                    Azure
Compute:            OCI Compute          EC2                    Compute Engine         Azure VM
Database:           Autonomous DB        RDS / Aurora           Cloud SQL              Azure SQL / Cosmos
Object Storage:     Object Storage       S3                     Cloud Storage          Blob Storage
Secrets:            OCI Vault            Secrets Manager/KMS    Secret Manager         Key Vault
Serverless:         OCI Functions        Lambda                 Cloud Functions        Azure Functions
AI Service:         OCI GenAI Service    Bedrock                Vertex AI              Azure OpenAI Service
Anomaly Detection:  OCI Anomaly Det.     Lookout for Metrics    Vertex AI              Azure Anomaly Detector
Container Registry: OCIR                 ECR                    Artifact Registry      ACR
Managed K8s:        OKE                  EKS                    GKE                    AKS
```

### RULE 9: LINUX DISTRO
- OCI project: Oracle Linux 8 (required — Oracle's distro)
- AWS project: Amazon Linux 2023 or RHEL
- GCP project: Rocky Linux 9 or Ubuntu
- Azure project: Ubuntu 22.04 or RHEL
- Pick what's natural for the platform, not forced.

### RULE 10: PROGRESSIVE COMPLEXITY
- Phase 1: Manual setup + basic Terraform, basic Ansible, simple bash
- Phase 2: Terraform with variables, Ansible with Vault, Python automation
- Phase 3: Terraform modules, Ansible roles, CI/CD pipelines, containers + K8s

### RULE 11: CONTAINER PROGRESSION (every project)
- Phase 1 = Docker + Docker Compose (containerize the app)
- Phase 2 = k3s "hard-ish way" — 2-node cluster (server + agent on separate instances), manual manifests, kubectl, understand every field
  - k3s = lightweight K8s distribution (single binary, same API as full K8s). 2 ARM A1 instances (2 OCPU/12GB each) fit within Always Free tier. Real inter-node networking via Flannel VXLAN overlay. Networking exercises: cross-node pod communication, nodeSelector, request tracing, NetworkPolicy (optional). In production, use managed K8s (OKE/EKS/GKE/AKS).
- Phase 3.1 = Pipeline deploys via raw `kubectl apply` — proves you understand the base layer before abstracting
- Phase 3.2 = Refactor to Helm (packaging) + ArgoCD or equivalent (GitOps delivery)
  - Pipeline no longer runs kubectl directly — it builds the image, updates Helm values in git, and ArgoCD auto-syncs
  - This 3.1 -> 3.2 progression is CRITICAL for interview storytelling: "I deployed with raw manifests first, then refactored to production-grade tooling"
- Vary the K8s delivery tool per project: Helm+ArgoCD (OCI) -> ArgoCD+Kustomize -> Helm+Flux -> etc.
- Budget approach: k3s on free-tier compute, ArgoCD runs on same cluster (lightweight)

### RULE 12: ACCOUNT BOOTSTRAP
- Phase 1 Day 1 must cover: non-root user, IAM basics, network setup, key management
- Scoped to project needs only (don't over-teach IAM theory)
- Depth varies by platform (AWS needs most setup, GCP needs least)

### RULE 13: THEME FLEXIBILITY
- Federal/compliance is one theme, not THE theme
- Future projects target: analytics, fintech, healthcare, startup SaaS, etc.
- Theme drives data and scenarios, not the skill pillars
- Phases generated on the fly per use case

### RULE 14: TOOL DIVERSITY ACROSS PROJECTS
**Constants (every project):** Terraform, Ansible, Kubernetes, Docker, Bash, Python

**Vary per project:**
- CI/CD pipeline: Jenkins (OCI) -> GitLab CI -> GitHub Actions -> (etc.)
- K8s delivery: Helm+ArgoCD (OCI) -> ArgoCD+Kustomize -> Helm+Flux -> (etc.)
- Monitoring: OCI native -> Prometheus/Grafana -> Datadog free -> Splunk free
- Container Registry: OCIR -> Docker Hub -> ECR -> GCR/Artifact Registry
- Goal: Touch many tools briefly, not master one deeply
- Each project introduces 1-2 NEW tools alongside the constants

### RULE 15: IMPLEMENTATION GUIDE STYLE
- The user builds DevOps/infra by hand (Terraform, Ansible, K8s manifests, Bash, Python, Helm charts)
- App code is copy-paste with thorough comments
- New concepts: full ELI5, section-by-section build, verification steps
- Returning concepts: step-by-step commands, no ELI5, still followable
- Format: location tags, ELI5 blocks, verification steps, cost checks, troubleshooting tables

---

## IMPLEMENTATION GUIDE GENERATION

Each phase will have a detailed implementation guide generated using the format defined in `implementation-guide-generator-prompt.md`. Guides will follow the style of `resume-api-repo/docs/phase-2-implementation-guide.md`.

The guide generator prompt will be populated with phase-specific details:
- PROJECT NAME, DESCRIPTION
- CLOUD PROVIDER: OCI (Always Free)
- TECH STACK per phase
- PHASES TO GENERATE (internal phases within each project)
- DEVOPS FILES TO BUILD BY HAND vs CODE FILES TO COPY-PASTE
- TARGET AUDIENCE: Career switcher with AWS/PM background, new to OCI/Linux/Terraform/Ansible
- LEARNING GOALS per phase
- DEPLOYMENT ENVIRONMENTS: Local terminal, OCI Console, VM Terminal (SSH), Editor
- SPECIAL CONSTRAINTS: OCI Always Free, Oracle Linux 8, ARM instances
