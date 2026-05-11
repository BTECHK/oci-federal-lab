# OCI Federal Compliance Lab

> A hands-on cloud engineering lab simulating a federal compliance environment on Oracle Cloud Infrastructure. Built from scratch on Oracle Linux 9 with production-grade tooling and a security-first, compliance-aware mindset.

**Author:** [Your Name]
**Cloud:** Oracle Cloud Infrastructure (OCI)
**Linux:** Oracle Linux 9
**Budget:** $150 hard cap (~$70 discretionary for paid services, ~$30 reserve; trial credits no longer in play). See ADR-009 for the cost framework that drives Phase 2/3 tooling choices.

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

- **Disaster Recovery & Backup Architecture** — DR drill design, cross-region replication, backup verification, file integrity monitoring, measured RTO/RPO. Built on a self-managed 2-node k3s cluster (the bare-bones-Kubernetes learning step per ADR-011) with OCI Generative AI Agents for incident triage.
- **CI/CD Modernization & AI-Augmented Operations** — Migrate workloads from k3s to OKE Basic (the managed-Kubernetes step per ADR-011), then layer Helm + ArgoCD GitOps delivery on top. Multi-stage Jenkins pipelines with supply-chain security scanning (Trivy + SBOM + Cosign image signing), API authentication, and anomaly detection. CloudBees-parity governance (Role Strategy RBAC, audit trail, shared library templating) replicated on free OSS Jenkins — see ADR-010.

Details, scope, and documentation for these phases will be published here as each phase is started and completed.

---

## Design Decisions

See the [design documents](docs/plans/) and [ADR log](docs/ARCHITECTURE-DECISIONS.md) for the rationale behind technology choices, including:
- Why Podman on Oracle Linux (RHEL-native, rootless, FIPS-compliant)
- Why Jenkins for CI/CD, with CloudBees-parity features replicated on free OSS plugins (see ADR-010)
- Why k3s in Phase 2 then OKE Basic in Phase 3 — primitives first, managed second (see ADR-011, which supersedes ADR-009)
- Why on-prem Ollama for the FedRAMP readiness agent (air-gap capability demonstration)

---

## Cost Considerations

### Run-rate (lab scale)

- **Estimated $0-$20/month** at typical lab usage. Always Free tier covers the majority of the architecture.
- **Always Free coverage:**
  - 2× VM.Standard.E2.1.Micro AMD instances (24GB RAM each)
  - Oracle Autonomous Database: 1 OCPU, 20GB storage, 60-day auto-backup
  - Object Storage: 20GB total across buckets
  - OCI Functions: 2M invocations/mo
  - OCI NoSQL Database: 133M reads/writes/mo + 25GB storage
  - OCI Vault: free tier covers ~150 secret operations/sec
  - OCI API Gateway: 1M req/mo free
  - Cloud Guard, IAM, basic VCN networking: free
- **First paid-tier hits as traffic grows:**
  1. Object Storage egress beyond 10TB/mo
  2. Function invocations beyond 2M/mo (Ollama-driven workflows could push this)
  3. NoSQL read/write units if event rate exceeds ~50/sec sustained
  4. OCI Cache (managed Redis) — small managed tier; ~$15/mo at smallest config (P3 addition)

### Cost levers

- **Lever 1: VM count.** Lab runs on 2 Always Free VMs; doubling to 4 (P2 k3s expansion to 4 nodes) crosses into paid tier ($30-50/mo for additional E2.1.Standard or Flex instances).
- **Lever 2: ADB tier upgrade.** Always Free → Always-on (production) tier is the single biggest lab-vs-prod cost delta; ~$1000/mo for the smallest paid ADB.
- **Lever 3: Object Storage class.** Standard → Archive saves ~50% but adds retrieval latency; matters at compliance-archive scale.
- **Lever 4: Function memory + concurrency.** Default Functions are cheap; tuning memory up for Ollama-bound workflows linearly scales cost.

### Architectural decisions driven by cost

- **ADB Always Free over RDS-equivalent paid:** chose ADB for the Always Free tier (vs. a paid Oracle DB option) — accepted the tier's OCPU/storage caps and built the architecture around them (hot-write decoupling to OCI NoSQL per ADR-017).
- **k3s in P2 before OKE in P3:** k3s on existing VMs avoided OKE's managed-control-plane cost during the learning phase. OKE in P3 is justified because P3's GitOps + supply chain story needs the managed primitives.
- **Self-hosted Ollama vs managed LLM:** LLM inference happens on the existing VM (Always Free) rather than paying for a managed inference service. Slower, but $0 incremental cost.
- **Cosign in CI vs OCI Vulnerability Scanning Service:** Cosign + Trivy in CI is free; OCIR built-in scanning is paid. Both are documented; only the free path is enabled by default.

### What changes at production scale

- **Tier upgrades become primary cost driver.** ADB paid tier alone exceeds $1000/mo; production OKE clusters with 3+ node pools run $300-500/mo; Object Storage at compliance scale (10+ TB) runs $250-500/mo.
- **Cross-region replication doubles storage cost.** Production DR needs active cross-region replica, not just backups.
- **Managed observability adds up.** OCI Monitoring + OCI Logging at production retention (90d+) becomes a $200-400/mo line item.
- **Security tooling tiers up.** OCI Vulnerability Scanning Service, Cloud Guard advanced features, Threat Intel — each is a $0 → $100s/mo step.

---

## License

This is a portfolio project built for educational and self-study purposes.
