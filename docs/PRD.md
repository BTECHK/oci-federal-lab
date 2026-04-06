# PRD: OCI Federal Compliance Lab

**Version:** 1.0
**Author:** [Your Name]
**Date:** March 2026
**Status:** Active
**Project Type:** Portfolio / Interview Preparation Lab

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
- Stay within $100 budget using OCI $300 trial credits

---

## User Stories

### US-001: OCI Account & Network Foundation
**Description:** As a cloud engineer, I want to provision OCI networking and compute manually so that I understand the console and CLI before automating with Terraform.

**Acceptance Criteria:**
- [ ] OCI tenancy created with $300 trial credits
- [ ] Compartment, VCN, subnets (public + private), security lists, internet gateway configured
- [ ] Oracle Linux 9 compute instance SSH-accessible
- [ ] Budget alert set at $50

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

### US-006: CI/CD Pipeline (Jenkins → CloudBees CI)
**Description:** As a cloud engineer, I want to build Jenkins pipelines and migrate to CloudBees CI so that I can demonstrate the enterprise governance layer federal programs require.

**Acceptance Criteria:**
- [ ] Open-source Jenkins installed on Oracle Linux (P1)
- [ ] Jenkinsfile with validate → build → deploy stages (P1)
- [ ] Migration to CloudBees CI (trial WAR replacement or plugin stack) (P2)
- [ ] Enterprise features configured: folder RBAC, CasC, audit trail (P2)
- [ ] Advanced CloudBees governance: pipeline templates, CasC versioning, cross-team visibility (P3)
- [ ] Progressive complexity: open-source install (P1) → CloudBees migration (P2) → pipeline templates + governance (P3)

### US-007: Container Builds (Podman + Docker)
**Description:** As a cloud engineer, I want to containerize the API using both Podman and Docker so that I understand the Oracle Linux native tooling.

**Acceptance Criteria:**
- [ ] Dockerfile builds with both `podman build` and `docker build`
- [ ] Multi-stage build with distroless/slim base
- [ ] Podman rootless execution demonstrated
- [ ] Comparison documented (max 2 hours)

### US-008: Kubernetes Orchestration (k3s)
**Description:** As a cloud engineer, I want to deploy to a multi-node k3s cluster so that I can demonstrate Kubernetes fundamentals.

**Acceptance Criteria:**
- [ ] 2-node k3s cluster on OCI ARM A1 free-tier instances
- [ ] Application deployed via kubectl with raw manifests (P2)
- [ ] Helm charts and ArgoCD GitOps in P3
- [ ] Cross-node networking verified

### US-009: Security Compliance Scanning
**Description:** As a cloud engineer, I want to run compliance scans so that I can discuss security posture in interviews.

**Acceptance Criteria:**
- [ ] OpenSCAP CIS baseline scan (P1)
- [ ] AIDE file integrity monitoring (P2)
- [ ] Trivy + Syft SBOM supply chain scanning (P3)

### US-010: AI Integration
**Description:** As a cloud engineer, I want to integrate AI capabilities so that I can discuss AI-augmented operations.

**Acceptance Criteria:**
- [ ] Ollama local LLM for compliance evidence collection (P1)
- [ ] OCI GenAI for incident classification (P2)
- [ ] scikit-learn for security pattern detection (P3)

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

- **Budget constraint:** $100 max from $300 OCI trial credits. ARM A1 instances are Always Free tier.
- **Oracle Linux 9:** Ships Podman by default, Docker not in repos. SELinux enforcing by default.
- **k3s on ARM:** Fully conformant K8s, ~70MB binary, runs on free-tier ARM instances.
- **Autonomous Database:** OCI's managed Oracle DB — Always Free tier includes 2 instances.
- **Phase independence:** Each phase tears down at the end. No cross-phase dependencies.

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
| Total cost | Under $100 |
| Can articulate any design decision in <60 seconds | Self-assessed |

---

## Open Questions

| Question | Status |
|----------|--------|
| Should Phase 2 k3s use same ARM instances or new ones? | Use new instances (phases are independent) |
| Should CloudBees exercises simulate licensed features? | Yes — JCasC, folder RBAC, shared libraries using open-source equivalents |
| How much time on Podman vs Docker comparison? | Max 2 hours on Day 3 |
