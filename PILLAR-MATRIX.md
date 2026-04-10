# Pillar Coverage Matrix

Machine-readable tracker: what was promised in the original design vs what is delivered in the guides.
**Every agent writing or editing guide content MUST cross-reference this file before marking a phase complete.**

Original design: `docs/plans/2026-03-18-interview-lab-project-design.md`
Last verified: 2026-04-08

> **Note — Potential Future Work:** Phase 2 (FedAnalytics DR) and Phase 3 (FedCompliance GitOps Security) are planned but **not yet started**. All rows in those sections describe intended scope, not delivered work. Their "DONE" status reflects guide authoring, not live lab execution.

---

## Phase 1 — FedTracker Migration

| Pillar | Promised Deliverable | Status | Guide Section | Verified |
|--------|---------------------|--------|---------------|----------|
| API | REST fundamentals, FastAPI, HTTP verbs, Pydantic, status codes, OpenAPI/Swagger | DONE | Phase 3 (Step 3.1-3.9) | 2026-04-08 |
| AI | FedRAMP readiness agent + Ollama (updated from evidence collector per ADR-003) | DONE | Phase 16 (Step 16.1-16.5) | 2026-04-08 |
| Security | OpenSCAP DISA STIG scanning (updated from CIS — CIS profile doesn't exist on OL9) | DONE | Phase 15 (Step 15.1-15.3) | 2026-04-08 |
| Container | Podman + Docker | DONE | Phase 6A + Phase 14 | 2026-04-08 |
| Container | Docker Compose | DONE | Phase 14.6 | 2026-04-08 |
| IaC/Terraform | Provider, variables, network, compute, outputs — from scratch | DONE | Phase 11 (Step 11.1-11.7) | 2026-04-08 |
| Ansible | Hardening playbook + app deployment + inventory | DONE | Phase 12 (Step 12.1-12.8) | 2026-04-08 |
| Linux Admin | SELinux, LVM, Systemd, Networking, User/PAM, Patching (Days 6-7) | DONE | linux-admin-deep-dive.md | 2026-04-08 |
| Break-fix | Firewall, permissions, service — hands-on exercises | DONE | Phase 7 (Step 7.1-7.3) + deep dive | 2026-04-08 |
| Migration | Docker Desktop to OCIR to Podman on OCI | DONE | Phase 14 (Step 14.1-14.4) | 2026-04-08 |

---

## Phase 2 — FedAnalytics DR  *(Potential Future Work — not yet started)*

| Pillar | Promised Deliverable | Status | Guide Section | Verified |
|--------|---------------------|--------|---------------|----------|
| API | Webhooks + HMAC signature validation | DONE | Phase 21, Step 8 | 2026-04-08 |
| API | OCI API Gateway + rate limiting | DONE | Phase 21B (Steps 21B.1-21B.6) | 2026-04-08 |
| AI | OCI Generative AI incident classifier | DONE | Phase 26 (Steps 26.1-26.5) | 2026-04-08 |
| Security | AIDE file integrity monitoring | DONE | Phase 24 (Steps 24.1-24.5) | 2026-04-08 |
| Container | k3s 2-node cluster (hard-ish way) | DONE | Phase 23 (Steps 23.1-23.6) | 2026-04-08 |
| Load Balancing | OCI Load Balancer — 3-tier architecture | DONE | Phase 23B (Steps 23B.1-23B.4) | 2026-04-08 |
| IaC/Terraform | Multi-node infra + DB (Days 1-2) | DONE | Phase 20 | 2026-04-08 |
| Ansible | Hardening + app deployment | DONE | Phase 21 | 2026-04-08 |
| Ansible | Drift detection (--check mode) | DONE | Phase 23A (Steps 23A.1-23A.3) | 2026-04-08 |
| CI/CD | Jenkins + CloudBees CI migration | DONE | Phase 22 | 2026-04-08 |
| Break-fix | Days 1-2 troubleshooting | DONE | Phase 20-21 tables | 2026-04-08 |
| Break-fix | Days 3-5 scenarios (k3s networking, ransomware, recovery) | DONE | Phase 23.6 + Phase 25 | 2026-04-08 |
| DR | Ransomware simulation + recovery drill + RTO/RPO measurement | DONE | Phase 25 (Steps 25.1-25.6) | 2026-04-08 |
| DR | Object Storage backup architecture (versioning, retention, lifecycle) | DONE | Phase 24A (Steps 24A.1-24A.3) | 2026-04-08 |
| Ops | Log rotation + cost modeling + teardown | DONE | Phase 27 (Steps 27.1-27.4) | 2026-04-08 |

---

## Phase 3 — FedCompliance GitOps Security  *(Potential Future Work — not yet started)*

| Pillar | Promised Deliverable | Status | Guide Section | Verified |
|--------|---------------------|--------|---------------|----------|
| API | API key auth + validation endpoint | DONE | Phase 30 (FedCompliance app, Step 30.11) | 2026-04-08 |
| API | mTLS concepts (conceptual, not hands-on) | DONE | API Pillar section (ELI5 + Interview Insight) | 2026-04-08 |
| API | Full request path diagram (client to DB) | DONE | Request Path section (ELI5 + 7-step walkthrough) | 2026-04-08 |
| API | API types comparison (REST, GraphQL, gRPC, Webhooks) | DONE | Appendix F | 2026-04-08 |
| AI | scikit-learn IsolationForest anomaly detection | DONE | Phase 33 (Step 33.5) | 2026-04-08 |
| Security | Trivy + SBOM supply chain security | DONE | Phase 31 (Steps 31.2-31.5) | 2026-04-08 |
| Container | Helm + ArgoCD GitOps | DONE | Phase 32 (full day) | 2026-04-08 |
| Load Balancing | OCI LB Terraform (3-tier as code) | DONE | Appendix E | 2026-04-08 |
| IaC/Terraform | Modules (network, compute, database) | DONE | Phase 30 (Steps 30.2-30.7) | 2026-04-08 |
| Ansible | Vault integration + secrets from OCI Vault | DONE | Phase 30 (Steps 30.9-30.10) | 2026-04-08 |
| CI/CD | 9-stage Jenkins pipeline with security gates | DONE | Phase 31 (Steps 31.6-31.13) | 2026-04-08 |
| Compliance | compliance_collector.py — OCI API queries to CMMC mapping | DONE | Phase 33 (Step 33.7) | 2026-04-08 |
| OCI Vault | Secrets management with instance principals | DONE | Phase 30 (Step 30.9) | 2026-04-08 |
| Break-fix | Hands-on exercises (CrashLoopBackOff, pipeline gate, Helm rollback, ArgoCD drift) | DONE | Phase 33B (Exercises 1-4) | 2026-04-08 |

---

## Pillar Progression Summary

> **Note:** Phase 2 and Phase 3 columns below describe planned progression — those phases are **potential future work**, not yet started.

| Pillar | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **API** | REST fundamentals | Webhooks + API Gateway | API key auth + mTLS concepts |
| **AI** | Ollama (local LLM) | OCI GenAI (cloud AI) | scikit-learn (classical ML) |
| **Security** | OpenSCAP DISA STIG | AIDE file integrity | Trivy + SBOM |
| **Container** | Podman + Docker + Compose | k3s (multi-node K8s) | Helm + ArgoCD |
| **Load Balancing** | N/A | OCI LB (Console, manual) | OCI LB (Terraform, as code) |
| **IaC** | Terraform from scratch | Terraform (returning) | Terraform modules |
| **Ansible** | Hardening + deploy | Hardening + drift detection | Vault integration |
| **CI/CD** | N/A | Jenkins + CloudBees | 9-stage pipeline |
| **DR** | N/A | Ransomware sim + recovery drill | N/A |

All Phase 1 pillars delivered as of 2026-04-08. Phase 2 and Phase 3 remain potential future work.

---

## Agent Instructions

1. Before marking any phase "complete", check every row for that phase in this matrix
2. A pillar is NOT delivered until it has a hands-on section in the guide (mentions in tables/diagrams don't count)
3. Update the Status, Guide Section, and Verified columns when content is added
4. If a deliverable is descoped, change Status to "DESCOPED" with a note explaining why
