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
| Phase 1 | ![Swagger UI + Health Check](docs/screenshots/phase-1-swagger-and-health.png) | REST API built from scratch, running on OCI, with auto-generated docs |
| Phase 2 | ![k3s + AIDE](docs/screenshots/phase-2-k3s-and-aide.png) | Kubernetes cluster running + file integrity monitoring (NIST SI-7) |
| Phase 3 | ![Jenkins Pipeline](docs/screenshots/phase-3-jenkins-pipeline.png) | Full CI/CD with security scanning (Trivy + SBOM), GitOps delivery |

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
├── terraform/              # IaC — all infrastructure defined here
│   ├── modules/            # Reusable Terraform modules
│   └── environments/
│       ├── dev/            # Dev environment configs
│       └── prod/           # Prod environment configs
├── ansible/                # Configuration management
│   ├── playbooks/          # Ansible playbooks
│   ├── roles/              # Ansible roles
│   └── inventory/          # Host inventory files
├── scripts/                # Bash/Python automation scripts
├── docker/                 # Dockerfiles, compose files
├── docs/                   # Documentation
│   ├── screenshots/        # Evidence of completed work
│   ├── plans/              # Design documents
│   ├── PRD.md              # Product Requirements Document
│   ├── phase-1-implementation-guide.md
│   ├── phase-2-implementation-guide.md
│   └── phase-3-implementation-guide.md
├── tests/                  # Test scripts
├── .github/workflows/      # GitHub Actions (if needed)
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## How to Use This Repo

This is a **learning lab**, not a deploy-and-forget project. Each phase has a detailed implementation guide in `docs/` that walks through every step:

1. Read the implementation guide for the phase you're working on
2. Execute each step by hand — typing commands, writing Terraform/Ansible/scripts
3. Commit your work as you go (each major milestone = a commit)
4. Capture screenshots of key outputs in `docs/screenshots/`
5. Tear down resources when done with a phase (cost management)

---

## Phase Status

| Phase | Guide | Status |
|-------|-------|--------|
| Phase 1: Legacy-to-Cloud Migration | [Implementation Guide](docs/phase-1-implementation-guide.md) | Not started |
| Phase 2: DR & Backup Architecture | [Implementation Guide](docs/phase-2-implementation-guide.md) | Not started |
| Phase 3: CI/CD Modernization | [Implementation Guide](docs/phase-3-implementation-guide.md) | Not started |

---

## Design Decisions

See the [design document](docs/plans/) for the full rationale behind every technology choice, including:
- Why Podman on Oracle Linux (RHEL-native, rootless, FIPS-compliant)
- Why k3s instead of OKE (free-tier compatible, same K8s API)
- Why Jenkins (JD requirement: CloudBees Jenkins)
- Why ArgoCD + Helm (production GitOps pattern)
- Why three independent phases (any single phase covers all JD requirements)

---

## License

This is a portfolio project built for educational and self-study purposes.
