# OCI Federal Compliance Lab

> A hands-on cloud engineering lab simulating a federal compliance environment on Oracle Cloud Infrastructure. Three independent phases progressively build infrastructure, security hardening, disaster recovery, and CI/CD automation — all on Oracle Linux with production-grade tooling.

**Author:** BTECHK
**Cloud:** Oracle Cloud Infrastructure (OCI)
**Linux:** Oracle Linux 9
**Budget:** $0–$100 (OCI $300 trial credits)

---

## Why This Project Exists

This project was born from a specific gap: the distance between *understanding* cloud infrastructure concepts and *demonstrating* them with real, deployed systems. Federal cloud environments have unique constraints — compliance frameworks (FedRAMP, NIST 800-171, CIS benchmarks), air-gapped considerations, Oracle-native tooling, and security-first architecture. This lab builds that environment from scratch, by hand, with every decision documented.

The project serves two purposes:
1. **Interview preparation** — Hands-on practice with every tool in the Oracle Cloud + Linux Admin stack
2. **Portfolio artifact** — A documented, reproducible lab that demonstrates cloud engineering depth beyond certifications

---

## Project Themes

Each phase tackles a real-world federal infrastructure scenario:

### Phase 1: Legacy-to-Cloud Migration
*"Migrate a compliance tracking system from manual processes to cloud infrastructure."*

Build the foundation: OCI networking, compute, Oracle Autonomous Database, a FastAPI compliance API (built by hand), Terraform IaC, Ansible hardening, Jenkins CI/CD, Docker/Podman containerization, and Oracle Linux administration (SELinux, LVM, systemd, firewalld, journalctl).

### Phase 2: Disaster Recovery & Backup Architecture
*"Design and execute a DR drill for a federal compliance system."*

Build DR infrastructure: cross-region replication, automated backup verification, k3s Kubernetes cluster, AIDE file integrity monitoring, incident classification with OCI GenAI, webhook-driven audit pipelines, and measured RTO/RPO. **Migrate from open-source Jenkins to CloudBees CI** — configure enterprise RBAC, Configuration as Code, and audit trail logging.

### Phase 3: CI/CD Modernization & AI-Augmented Operations
*"Modernize the deployment pipeline with GitOps, supply chain security, and AI-powered monitoring."*

Production-grade delivery: multi-stage Jenkins pipelines with security scanning, Helm charts, ArgoCD GitOps, Trivy + SBOM supply chain security, API authentication (keys + mTLS concepts), scikit-learn anomaly detection, and **advanced CloudBees CI governance** (pipeline templates, CasC bundle versioning, cross-team visibility, shared library enforcement).

---

## Results

| Phase | Screenshot | What It Proves |
|-------|-----------|---------------|
| Phase 1 | ![Swagger UI + Health Check](phases/phase-1-fedtracker-migration/docs/screenshots/swagger-and-health.png) | REST API built from scratch, running on OCI, with auto-generated docs |
| Phase 2 | ![k3s + AIDE](phases/phase-2-fedanalytics-dr/docs/screenshots/k3s-and-aide.png) | Kubernetes cluster running + file integrity monitoring (NIST SI-7) |
| Phase 3 | ![Jenkins Pipeline](phases/phase-3-fedcompliance-cicd/docs/screenshots/jenkins-pipeline.png) | Full CI/CD with security scanning (Trivy + SBOM), GitOps delivery |

---

## Tech Stack

| Category | Tools |
|----------|-------|
| **Cloud** | OCI (Compute, VCN, Autonomous DB, Object Storage, Functions, API Gateway, GenAI) |
| **Linux** | Oracle Linux 9 (SELinux, LVM, systemd, firewalld, PAM, sysctl, journalctl) |
| **IaC** | Terraform (progressive: manual → basics → modules) |
| **Config Mgmt** | Ansible (progressive: playbooks → drift detection → roles + vault) |
| **CI/CD** | Jenkins → CloudBees CI (progressive: open-source install → CloudBees migration → pipeline templates + governance) |
| **Containers** | Podman (Oracle Linux native) + Docker (comparison), containerd under K8s |
| **Kubernetes** | k3s (multi-node on ARM A1 free-tier instances) |
| **Packaging** | Helm |
| **GitOps** | ArgoCD |
| **API** | FastAPI (Python) — REST, Webhooks, API Gateway, API auth |
| **AI** | Ollama (FedRAMP readiness agent), OCI GenAI, scikit-learn |
| **Security** | OpenSCAP (CIS), AIDE (file integrity), Trivy + Syft (supply chain) |
| **Scripting** | Bash, Python |

---

## Project Structure

```
oci-federal-lab/
├── phases/                                        # Each phase is self-contained
│   ├── phase-1-fedtracker-migration/              # Legacy-to-Cloud Migration
│   │   ├── terraform/                             # IaC for Phase 1 infrastructure
│   │   ├── ansible/                               # Config management (playbooks, inventory, roles)
│   │   ├── app/                                   # FedTracker application source code
│   │   ├── docker/                                # Dockerfile, docker-compose
│   │   └── docs/                                  # Phase 1 guide, deep dive, screenshots
│   ├── phase-2-fedanalytics-dr/                   # Disaster Recovery & Backup
│   │   ├── terraform/ ansible/ app/ docker/
│   │   └── docs/
│   └── phase-3-fedcompliance-cicd/                # CI/CD Modernization
│       ├── terraform/ ansible/ app/ docker/
│       └── docs/
├── docs/                                          # Project-wide documentation
│   ├── ARCHITECTURE-DECISIONS.md                  # ADR log — why decisions were made
│   ├── LESSONS-LEARNED.md                         # Meta-checklist for guide writing
│   ├── KNOWN-ISSUES.md                            # Errors & patterns reference
│   ├── PRD.md                                     # Product Requirements Document
│   ├── DEVOPS-ARCHITECTURE-REFERENCE.md           # Lab-to-production mapping
│   └── plans/                                     # Design documents
├── tools/                                         # Shared utilities (cost estimator, helpers)
├── .github/workflows/                             # GitHub Actions
├── .env.example                                   # Environment variable template
├── .gitignore
└── README.md
```

---

## How to Use This Repo

This is a **learning lab**, not a deploy-and-forget project. Each phase has a detailed implementation guide in its `docs/` folder that walks through every step:

1. Read the implementation guide for the phase you're working on
2. Execute each step by hand — typing commands, writing Terraform/Ansible/scripts
3. Commit your work as you go (each major milestone = a commit)
4. Capture screenshots of key outputs in each phase's `docs/screenshots/`
5. Tear down resources when done with a phase (cost management)

---

## Phase Status

| Phase | Guide | Status |
|-------|-------|--------|
| Phase 1: Legacy-to-Cloud Migration | [Implementation Guide](phases/phase-1-fedtracker-migration/docs/implementation-guide.md) | In progress |
| Phase 1: Linux Admin Deep Dive | [Deep Dive](phases/phase-1-fedtracker-migration/docs/linux-admin-deep-dive.md) | Not started |
| Phase 2: DR & Backup Architecture | [Implementation Guide](phases/phase-2-fedanalytics-dr/docs/implementation-guide.md) | Not started |
| Phase 3: CI/CD Modernization | [Implementation Guide](phases/phase-3-fedcompliance-cicd/docs/implementation-guide.md) | Not started |

---

## Design Decisions

See the [design document](docs/plans/) for the full rationale behind every technology choice, including:
- Why Podman on Oracle Linux (RHEL-native, rootless, FIPS-compliant)
- Why k3s instead of OKE (free-tier compatible, same K8s API — OKE comparison in Phase 3 Appendix B)
- Why Jenkins (JD requirement: CloudBees Jenkins — OCI DevOps comparison in Phase 3 Appendix D)
- Why ArgoCD + Helm (production GitOps pattern)
- Why three independent phases (any single phase covers all JD requirements)
- OCI managed services explored: Resource Manager, OKE, OCIR scanning, OCI DevOps, OS Management Hub (see Phase 3 Appendices + ADR-007)

---

## License

This is a portfolio project built for educational and self-study purposes.
