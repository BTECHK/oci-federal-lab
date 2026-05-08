# Pillar Coverage Matrix

Machine-readable tracker: what was promised in the original design vs what is delivered in the guides.
**Every agent writing or editing guide content MUST cross-reference this file before marking a phase complete.**

Original design: `docs/plans/2026-03-18-interview-lab-project-design.md`
Last verified: 2026-05-07 (Phase 2 / Phase 3 rows updated for cost-conscious restructure — see ADR-010 (CloudBees skip) and ADR-011 (k3s in P2, OKE Basic in P3 — supersedes ADR-009).)

> **Note — Potential Future Work:** Phase 2 (FedAnalytics DR) and Phase 3 (FedCompliance GitOps Security) are planned but **not yet started**. All rows in those sections describe intended scope, not delivered work. Their "DONE" status reflects guide authoring, not live lab execution.

> **Anchor concepts (every phase hammers ≥ 2):** Infrastructure as Code, CI/CD, Containerization & Kubernetes, Security, AI exposure. Net-new features must serve one of these and clear an L6-additive-value bar — observability, API maturity, framework thinking, and operational maturity (the 2026-04-15 cheat-sheet additions) are explicitly out of scope per the 2026-05-07 restructure.

> **Kubernetes progression (locked per ADR-011):** P1 has no K8s; **P2 = k3s 2-node DIY** (bare-bones primitives — control plane install, agent join, kubelet, Flannel, NodePort); **P3 = OKE Basic migration** (managed K8s + Helm + ArgoCD GitOps on top). Pulling OKE into P2 or demoting k3s to an appendix is explicitly forbidden.

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
| AI | OCI Generative AI Agents (managed RAG) — incident triage over runbook corpus | RESCOPED | Phase 26 (Steps 26.1-26.5) — needs rewrite per ADR-009/restructure | 2026-05-07 |
| Security | AIDE file integrity monitoring | DONE | Phase 24 (Steps 24.1-24.5) | 2026-04-08 |
| Security | OCI Bastion service (managed jump host, replaces a self-managed bastion VM at Phase 2 cluster spin-up) | NEW | Phase 20 (new module introduced fresh in Phase 2 — Phase 1's existing bastion VM stays as-is per the user-approved scope freeze 2026-05-08) | 2026-05-08 |
| Container | k3s 2-node cluster (hard-ish way) — bare-bones K8s learning step (control plane install, agent join token, kubelet, Flannel, NodePort) | DONE | Phase 23 (Steps 23.1-23.6) — restored as Phase 2 spine per ADR-011 | 2026-05-07 |
| Load Balancing | OCI Load Balancer — 3-tier architecture | DONE | Phase 23B (Steps 23B.1-23B.4) | 2026-04-08 |
| IaC/Terraform | Multi-node infra + DB (Days 1-2) | DONE | Phase 20 | 2026-04-08 |
| Ansible | Hardening + app deployment | DONE | Phase 21 | 2026-04-08 |
| Ansible | Drift detection (--check mode) | DONE | Phase 23A (Steps 23A.1-23A.3) | 2026-04-08 |
| CI/CD | Jenkins (single CI/CD spine — no parallel OCI DevOps; CloudBees trial dropped per ADR-010) | RESCOPED | Phase 22 — strip CloudBees migration arc | 2026-05-07 |
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
| Security | Cosign image signing + verification stage in Jenkins pipeline | NEW | Phase 31 (new step — pairs with OPA admission) | 2026-05-07 |
| Security | OCI Bastion service (introduced in Phase 2; reused in Phase 3 unchanged) | CARRY-FORWARD | Phase 30 (terraform — reuse bastion-service module from Phase 2) | 2026-05-07 |
| Container | OKE Basic migration: k3s → managed K8s with Always Free A1.Flex worker pool (the "you built it from scratch in P2 — here's the managed equivalent" lesson per ADR-011) | NEW | Phase 30 (new step early in P3) — terminates Phase 2 k3s + provisions OKE Basic + redeploys FedCompliance | 2026-05-07 |
| Container | One-time paid `VM.Standard.E5.Flex` worker for ~6 hr load-test demo (~$5, tagged `lifetime=ephemeral`) | NEW | Phase 30 appendix | 2026-05-07 |
| Container | Helm + ArgoCD GitOps targeting OKE Basic (re-targeted from k3s per ADR-011) | RESCOPED | Phase 32 (full day) — re-target from k3s to OKE | 2026-05-07 |
| Load Balancing | OCI LB Terraform (3-tier as code) | DONE | Appendix E | 2026-04-08 |
| IaC/Terraform | Modules (network, compute, database) | DONE | Phase 30 (Steps 30.2-30.7) | 2026-04-08 |
| Ansible | Vault integration + secrets from OCI Vault | DONE | Phase 30 (Steps 30.9-30.10) | 2026-04-08 |
| CI/CD | 9-stage Jenkins pipeline with security gates | DONE | Phase 31 (Steps 31.6-31.13) | 2026-04-08 |
| CI/CD | CloudBees-feature replication via free OSS plugins (Role Strategy RBAC, Audit Trail, shared library templating) | NEW | Phase 31 (new subsection — see ADR-010) | 2026-05-07 |
| Compliance | compliance_collector.py — OCI API queries to CMMC mapping | DONE | Phase 33 (Step 33.7) | 2026-04-08 |
| OCI Vault | Secrets management with instance principals | DONE | Phase 30 (Step 30.9) | 2026-04-08 |
| Break-fix | Hands-on exercises (CrashLoopBackOff, pipeline gate, Helm rollback, ArgoCD drift) | DONE | Phase 33B (Exercises 1-4) | 2026-04-08 |

---

## Pillar Progression Summary

> **Note:** Phase 2 and Phase 3 columns below describe planned progression — those phases are **potential future work**, not yet started.

| Pillar | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **API** | REST fundamentals | Webhooks + API Gateway | API key auth + mTLS concepts |
| **AI** | Ollama (local LLM, FedRAMP agent) | OCI Generative AI Agents (managed RAG) | scikit-learn (classical ML, pipeline telemetry) |
| **Security** | OpenSCAP DISA STIG | AIDE file integrity + OCI Bastion service | Trivy + SBOM + Cosign image signing |
| **Container** | Podman + Docker + Compose | k3s 2-node DIY (bare-bones K8s — primitives) | OKE Basic migration + Helm + ArgoCD GitOps on managed cluster |
| **Load Balancing** | N/A | OCI LB (Console, manual) | OCI LB (Terraform, as code) |
| **IaC** | Terraform from scratch + Resource Manager appendix | Terraform (returning) | Terraform modules |
| **Ansible** | Hardening + deploy | Hardening + drift detection | Vault integration |
| **CI/CD** | N/A | Jenkins (single spine — no parallel tools) | 9-stage Jenkins pipeline + CloudBees-parity (Role Strategy, Audit Trail, shared lib) |
| **DR** | N/A | Ransomware sim + recovery drill | N/A |

All Phase 1 pillars delivered as of 2026-04-08. Phase 2 and Phase 3 remain potential future work, restructured 2026-05-07 per ADR-010 (CloudBees free trial dropped) and ADR-011 (k3s in P2 / OKE Basic in P3 — supersedes ADR-009).

---

## Agent Instructions

1. Before marking any phase "complete", check every row for that phase in this matrix
2. A pillar is NOT delivered until it has a hands-on section in the guide (mentions in tables/diagrams don't count)
3. Update the Status, Guide Section, and Verified columns when content is added
4. If a deliverable is descoped, change Status to "DESCOPED" with a note explaining why
