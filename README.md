# OCI Federal Compliance Lab

> A hands-on cloud engineering lab simulating a federal compliance environment on Oracle Cloud Infrastructure. Built from scratch on Oracle Linux 9 with production-grade tooling and a security-first, compliance-aware mindset.

**Author:** [Your Name]
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

## Current Focus — Phase 1: Legacy-to-Cloud Migration

*"Migrate a compliance tracking system from manual processes to cloud infrastructure."*

Build the foundation: OCI networking, compute, Oracle Autonomous Database, a FastAPI compliance API (built by hand), Terraform IaC, Ansible hardening, Jenkins CI/CD, Docker/Podman containerization, and Oracle Linux administration (SELinux, LVM, systemd, firewalld, journalctl). Includes an on-prem FedRAMP readiness agent running Ollama locally to prove air-gap capability.

---

## Results

| Phase | Screenshot | What It Proves |
|-------|-----------|---------------|
| Phase 1 | ![Swagger UI + Health Check](phases/phase-1-fedtracker-migration/docs/screenshots/swagger-and-health.png) | REST API built from scratch, running on OCI, with auto-generated docs |

---

## Tech Stack (Phase 1)

| Category | Tools |
|----------|-------|
| **Cloud** | OCI (Compute, VCN, Autonomous DB, Object Storage, Functions) |
| **Linux** | Oracle Linux 9 (SELinux, LVM, systemd, firewalld, PAM, sysctl, journalctl) |
| **IaC** | Terraform |
| **Config Mgmt** | Ansible |
| **CI/CD** | Jenkins |
| **Containers** | Podman (Oracle Linux native) + Docker (comparison) |
| **API** | FastAPI (Python) — REST |
| **AI** | Ollama (FedRAMP readiness agent, on-prem / air-gap capable) |
| **Security** | OpenSCAP (CIS / DISA STIG baselines) |
| **Scripting** | Bash, Python |

---

## Project Structure

```
oci-federal-lab/
├── phases/
│   └── phase-1-fedtracker-migration/              # Legacy-to-Cloud Migration
│       ├── terraform/                             # IaC for Phase 1 infrastructure
│       ├── ansible/                               # Config management (playbooks, inventory, roles)
│       ├── app/                                   # FedTracker application source code
│       ├── docker/                                # Dockerfile, docker-compose
│       └── docs/                                  # Phase 1 deep dive, screenshots
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

This is a **learning lab**, not a deploy-and-forget project. Work through each phase by hand:

1. Read the phase's deep-dive and planning docs
2. Execute each step by hand — typing commands, writing Terraform/Ansible/scripts
3. Commit your work as you go (each major milestone = a commit)
4. Capture screenshots of key outputs in each phase's `docs/screenshots/`
5. Tear down resources when done with a phase (cost management)

A sanitized, standard-operating-procedure version of each phase will be published here as the phase completes.

---

## Phase Status

| Phase | Status |
|-------|--------|
| Phase 1: Legacy-to-Cloud Migration | In progress |
| Phase 1: Linux Admin Deep Dive | Not started |

---

## Future Work

The lab is structured to eventually cover two additional federal-infrastructure themes once Phase 1 is complete:

- **Disaster Recovery & Backup Architecture** — DR drill design, cross-region replication, backup verification, file integrity monitoring, measured RTO/RPO, and an open-source → enterprise CI migration story.
- **CI/CD Modernization & AI-Augmented Operations** — Multi-stage pipelines with supply-chain security scanning, GitOps delivery, API authentication, and anomaly detection.

Details, scope, and documentation for these phases will be published here as each phase is started and completed.

---

## Design Decisions

See the [design documents](docs/plans/) and [ADR log](docs/ARCHITECTURE-DECISIONS.md) for the rationale behind Phase 1 technology choices, including:
- Why Podman on Oracle Linux (RHEL-native, rootless, FIPS-compliant)
- Why Jenkins for CI/CD (JD requirement: CloudBees Jenkins)
- Why on-prem Ollama for the FedRAMP readiness agent (air-gap capability demonstration)

---

## License

This is a portfolio project built for educational and self-study purposes.
