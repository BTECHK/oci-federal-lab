# PRD: OCI Federal Compliance Lab

**Version:** 1.1
**Author:** [Your Name]
**Date:** March 2026 — Updated 2026-05-07 (cost-conscious restructure)
**Status:** Active
**Project Type:** Portfolio / Interview Preparation Lab

> **2026-05-07 restructure note:** The 30-day OCI trial-credit window has lapsed. Budget framing, US-006 (CI/CD), and US-008 (Kubernetes) have been rewritten to reflect ADR-009 (OKE Basic replaces k3s as Phase 2 spine) and ADR-010 (CloudBees free trial dropped; OSS feature replication via Role Strategy + Audit Trail + shared libraries). See `docs/ARCHITECTURE-DECISIONS.md` and `C:\Users\k_a_s\.claude\plans\i-think-for-phase-abundant-pixel.md`.

---

## Introduction

Build and operate a federal compliance infrastructure environment on Oracle Cloud Infrastructure, from manual provisioning through full CI/CD automation. The lab simulates real federal cloud engineering workflows — Oracle Linux administration, Terraform IaC, Ansible configuration management, Jenkins pipelines, Kubernetes orchestration, and security compliance scanning — across three independent phases that each cover every skill required for a Cloud Engineer / Linux Admin role.

This is a learning lab, not a production application. The "product" is the infrastructure itself, the automation that manages it, and the documented evidence of hands-on execution.

---

## Goals

- Demonstrate hands-on proficiency with every tool in federal cloud engineer job descriptions
- Build muscle memory on Oracle Linux administration (SELinux, LVM, systemd, firewalld, PAM, sysctl)
- Write Terraform, Ansible, Bash, Python, and Jenkinsfiles by hand (not copy-paste)
- Build FastAPI applications section-by-section to understand API design fundamentals
- Practice security hardening with production frameworks (CIS, NIST 800-171, EO 14028)
- Produce a portfolio artifact with documented architecture decisions and evidence
- Stay within $150 hard cap (~$70 discretionary for paid services, ~$30 reserve; trial credits no longer in play)

---

## User Stories

### US-001: OCI Account & Network Foundation
**Description:** As a cloud engineer, I want to provision OCI networking and compute manually so that I understand the console and CLI before automating with Terraform.

**Acceptance Criteria:**
- [ ] OCI tenancy created (Always Free tier; trial-credit window has lapsed)
- [ ] Compartment, VCN, subnets (public + private), security lists, internet gateway configured
- [ ] Oracle Linux 9 compute instance SSH-accessible
- [ ] Budget alerts set at $75 / $115 / $140 against the $150 hard cap (see ADR-009 cost framework)

### US-002: Oracle Linux Hardening
**Description:** As a Linux admin, I want to harden an Oracle Linux 9 instance so that I can demonstrate production security practices.

**Acceptance Criteria:**
- [ ] SELinux in enforcing mode, custom booleans configured
- [ ] LVM volume created/extended for application data
- [ ] systemd service created and hardened (ProtectSystem, NoNewPrivileges)
- [ ] firewalld zones configured for application traffic
- [ ] PAM password policies applied
- [ ] sysctl kernel parameters tuned
- [ ] journalctl used for log forensics

### US-003: Compliance API (FastAPI)
**Description:** As a cloud engineer, I want to build a REST API by hand so that I understand API design patterns and can discuss them in interviews.

**Acceptance Criteria:**
- [ ] FastAPI app with CRUD endpoints for compliance records
- [ ] Pydantic models for request/response validation
- [ ] Oracle Autonomous Database connection
- [ ] OpenAPI/Swagger docs auto-generated at /docs
- [ ] Health check endpoint returns 200

### US-004: Infrastructure as Code (Terraform)
**Description:** As a cloud engineer, I want to codify all OCI infrastructure in Terraform so that environments are reproducible.

**Acceptance Criteria:**
- [ ] All Phase 1 resources recreatable via `terraform apply`
- [ ] State stored remotely in OCI Object Storage
- [ ] Variables and outputs properly structured
- [ ] Progressive complexity: basics (P1) → variables (P2) → modules (P3)

### US-005: Configuration Management (Ansible)
**Description:** As a cloud engineer, I want to automate server configuration with Ansible so that hardening is repeatable.

**Acceptance Criteria:**
- [ ] Hardening playbook applies SELinux, firewall, sysctl, user configs
- [ ] Idempotent — running twice produces no changes
- [ ] Progressive complexity: playbooks (P1) → drift detection (P2) → roles + vault (P3)

### US-006: CI/CD Pipeline (Jenkins as single spine; CloudBees-parity via OSS plugins)
**Description:** As a cloud engineer, I want to build Jenkins pipelines and replicate the enterprise governance features federal programs care about (folder-level RBAC, audit logging, pipeline templating) using free OSS Jenkins plugins — without locking the demo to a CloudBees free trial. See ADR-010.

**Acceptance Criteria:**
- [ ] Open-source Jenkins installed on Oracle Linux (P1)
- [ ] Jenkinsfile with validate → build → deploy stages (P1)
- [ ] Jenkins remains the single CI/CD spine across all phases — no parallel OCI DevOps or GitHub Actions stacks (P2/P3)
- [ ] Folder-level RBAC via Role Strategy plugin (P3)
- [ ] Audit logging via Audit Trail plugin (P3)
- [ ] Pipeline templating via shared library structure (`vars/`, `src/`, `resources/`) (P3)
- [ ] Cosign image signing + verification stage in pipeline (P3)
- [ ] Progressive complexity: open-source install (P1) → 9-stage pipeline with security gates (P2) → CloudBees-parity governance + supply-chain attestation (P3)

### US-007: Container Builds (Podman + Docker)
**Description:** As a cloud engineer, I want to containerize the API using both Podman and Docker so that I understand the Oracle Linux native tooling.

**Acceptance Criteria:**
- [ ] Dockerfile builds with both `podman build` and `docker build`
- [ ] Multi-stage build with distroless/slim base
- [ ] Podman rootless execution demonstrated
- [ ] Comparison documented (max 2 hours)

### US-008: Kubernetes Orchestration (OKE Basic, with k3s preserved as appendix)
**Description:** As a cloud engineer, I want to deploy to a managed OKE Basic cluster so that I can demonstrate the production-shaped Kubernetes pattern federal employers actually run, while preserving a single k3s appendix for the "I understand the primitives" interview talking point. See ADR-009.

**Acceptance Criteria:**
- [ ] OKE Basic cluster (free control plane) with 3-node A1.Flex worker pool on Always Free tier (P2)
- [ ] Application deployed via kubectl with raw manifests (P2)
- [ ] Helm charts and ArgoCD GitOps on the same OKE cluster (P3 — no rebuild)
- [ ] Cross-node networking verified
- [ ] One-time paid `VM.Standard.E5.Flex` worker (~6 hr, ~$5, tagged `lifetime=ephemeral`) for a load-test demo, then torn down (P2)
- [ ] k3s appendix (~1 page) demonstrates the DIY equivalent for narrative completeness

### US-009: Security Compliance Scanning
**Description:** As a cloud engineer, I want to run compliance scans so that I can discuss security posture in interviews.

**Acceptance Criteria:**
- [ ] OpenSCAP CIS baseline scan (P1)
- [ ] AIDE file integrity monitoring (P2)
- [ ] Trivy + Syft SBOM supply chain scanning (P3)

### US-010: AI Integration
**Description:** As a cloud engineer, I want to integrate AI capabilities so that I can discuss AI-augmented operations across local, managed-RAG, and classical-ML patterns.

**Acceptance Criteria:**
- [ ] Ollama local LLM (FedRAMP readiness agent — air-gap capable) (P1)
- [ ] OCI Generative AI Agents (managed RAG over runbook corpus — incident triage). Estimated ~$10–15 of token spend within the $70 discretionary cap. (P2)
- [ ] scikit-learn IsolationForest for pipeline-telemetry anomaly detection (P3)

---

## Functional Requirements

- FR-1: All infrastructure provisioned on OCI using Oracle Linux 9 compute instances
- FR-2: Each phase is independent — can be started from a fresh environment
- FR-3: Every phase covers all JD-required skills (Terraform, Ansible, Linux, Jenkins, containers)
- FR-4: FastAPI apps built by hand with section-by-section scaffolding and ELI5 explanations
- FR-5: SQL schemas and seed data provided as copy-paste with inline comments
- FR-6: Implementation guides provide step-by-step commands, verification steps, and troubleshooting tables
- FR-7: Linux admin skills woven throughout at natural integration points (not isolated days)
- FR-8: Interview Insight boxes after each new API/DevOps concept
- FR-9: Cost checks at each major milestone to prevent budget overrun
- FR-10: Teardown instructions at end of each phase

---

## Non-Goals

- This is NOT a production application — it's a learning lab
- No custom domain names or SSL certificate management
- No multi-tenancy or user authentication on the API (beyond API key concepts)
- No CloudBees license purchase — open-source Jenkins + terminology knowledge only
- No third-party AI APIs (Groq, OpenAI) — all cloud-native or open-source
- No frontend UI — API-only with Swagger docs
- No automated testing beyond basic health checks (testing is not the learning focus)

---

## Technical Considerations

- **Budget constraint:** $150 hard cap (~$50 already spent, ~$70 discretionary, ~$30 reserve). Trial credits no longer in play. ARM A1.Flex instances on Always Free tier are the default; paid shapes only for tightly-scoped, time-boxed demos.
- **Oracle Linux 9:** Ships Podman by default, Docker not in repos. SELinux enforcing by default.
- **OKE Basic on ARM:** Free control plane, A1.Flex worker pool on Always Free tier (3 nodes within the 4 OCPU quota). Replaces the original k3s plan as Phase 2 spine — see ADR-009.
- **Autonomous Database:** OCI's managed Oracle DB — Always Free tier includes 2 instances.
- **Phase independence:** Phases share knowledge prerequisites but no live infrastructure prerequisites. Phase 3 reuses the Phase 2 OKE cluster only when both phases run in the same tenancy at the same time; otherwise Phase 3 stands up its own OKE Basic cluster from the same Terraform module.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| All JD skills practiced hands-on | 13/13 skills touched in Phase 1 alone |
| Terraform resources deployable | `terraform apply` succeeds from clean state |
| Ansible playbooks idempotent | Second run reports 0 changes |
| Jenkins pipeline runs end-to-end | Build → test → deploy completes |
| API endpoints functional | All CRUD + health check return valid JSON |
| Security scans executed | OpenSCAP, AIDE, Trivy all produce reports |
| Total cost | Under $150 hard cap (~$70 discretionary spent on paid services across P2/P3) |
| Can articulate any design decision in <60 seconds | Self-assessed |

---

## Open Questions

| Question | Status |
|----------|--------|
| Should Phase 2 use OKE Basic or k3s as the K8s spine? | **Resolved 2026-05-07 — OKE Basic with Always Free A1.Flex workers.** k3s preserved as 1-page appendix. See ADR-009. |
| Should CloudBees free trial be used for the enterprise governance demo? | **Resolved 2026-05-07 — No.** Replicate Role Strategy + Audit Trail + shared-library templating on free OSS Jenkins. See ADR-010. |
| Should Phase 3 spin up its own OKE cluster or reuse Phase 2's? | Reuse Phase 2's when both phases run in the same tenancy session; otherwise stand up via the same Phase 2 Terraform module. |
| How much time on Podman vs Docker comparison? | Max 2 hours on Day 3 |
