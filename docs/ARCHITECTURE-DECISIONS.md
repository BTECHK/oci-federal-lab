# Architecture Decision Record (ADR) Log

Ongoing record of key decisions, trade-offs, pivots, and lessons learned while building the OCI Federal Lab. Written for future reference, README content, LinkedIn posts, and blog material.

**Format:** Each entry captures what was decided, what alternatives were considered, why this path was chosen, and what we learned. Entries are reverse-chronological (newest first).

---

## ADR-008: Phase-First Repository Structure with Enterprise Naming
**Date:** 2026-04-02
**Status:** Accepted
**Context:** The original repo had flat top-level directories (`terraform/`, `ansible/`, `docker/`, `scripts/`, `tests/`). This worked for Phase 1 alone, but with 3 phases plus a Linux deep dive, files like `harden.yml` and `deploy_app.yml` would collide. The naming was generic — an interviewer browsing the repo couldn't tell which phase or app a file belonged to. Enterprise teams organize by project/service, not by tool type.
**Decision:** Reorganize into a `phases/` directory with descriptive folder names: `phase-1-fedtracker-migration`, `phase-2-fedanalytics-dr`, `phase-3-fedcompliance-cicd`. Each phase contains its own `terraform/`, `ansible/`, `app/`, `docker/`, and `docs/` subdirectories. Project-wide documentation (ADRs, lessons, known issues, PRD) stays in the root `docs/` folder. Shared utilities stay in `tools/`.
**Rationale:** Phase-first organization matches how you talk about the project — "let me walk you through Phase 1" — and everything for that story is in one place. The naming convention (number + app name + theme) tells interviewers immediately what skill and what application each phase demonstrates. This pattern is also portable to other cloud projects (AWS, Azure, GCP).
**Trade-offs:**
- Ansible/Terraform commands from the repo root are longer (`phases/phase-1-fedtracker-migration/ansible/...`)
- Implementation guides needed path updates (52+ command references)
- Phase-specific docs are further from the root README (one more click)
**Alternatives considered:**
- Tool-first organization (`terraform/phase-1/`, `ansible/phase-1/`) — rejected because it fragments each phase's story across multiple root directories
- Flat structure with prefixed filenames (`phase-1-harden.yml`) — rejected because it doesn't scale and doesn't match enterprise patterns

---

## ADR-007: OCI Managed Services — Build It Yourself First, Then Use the Managed Equivalent
**Date:** 2026-04-02
**Status:** Accepted
**Context:** Phase 3 builds production-like infrastructure using self-managed tools: k3s for Kubernetes, local `terraform apply` for infrastructure, Jenkins for CI/CD. In production federal environments, teams often use managed equivalents: OKE (managed K8s), OCI Resource Manager (managed Terraform), OCI DevOps (managed CI/CD). The question arose: should we replace the DIY tools with managed services in Phase 3?
**Decision:** Keep the DIY implementation as primary Phase 3 content. Add appendices exploring managed alternatives (OCI Resource Manager, OKE comparison, OCIR scanning enhancements, OCI DevOps). The Phase 1 Linux admin deep dive covers OCI OS Management Hub for enterprise patch management.
**Rationale:** The interview story is strongest when you can say "I built it from scratch AND I know the managed alternative." Replacing k3s with OKE would remove the Kubernetes internals learning. Replacing Jenkins with OCI DevOps would remove pipeline-as-code authoring experience. The progression is deliberate: understand the primitives (Phase 1-3), then understand what the managed service abstracts away (appendices).
**Trade-offs:**
- OKE control plane costs money (not Always Free) — appendix is comparison-focused with an optional trial-credits lab
- OCI Resource Manager is free — most practical to demonstrate hands-on
- OCI OS Management Hub is free on paid tenancies — covered in Linux admin deep dive with lifecycle environments
**See also:** Phase 3 Appendices A-D for managed services labs; Phase 1 Linux admin deep dive Step 9 for OSMH patching workflow.

---

## ADR-006: DevOps Tool Layering — Where Everything Runs
**Date:** 2026-03-31
**Status:** Accepted
**Context:** While working through Terraform Step 11, a key question surfaced: "Doesn't Terraform have a server in production? How does it maintain updates to the account where it sits? I'm creating changes to a machine that I'm running the change agent on." This is the "inception problem" — a real architectural question DevOps teams deal with.
**Decision:** Document the three-layer model that explains where every tool in the lab runs, and how it maps to production:
- **Layer 0 (Bootstrap):** Set up manually or by a one-time script. Includes: cloud account, service accounts, CI/CD server, Terraform state storage. This layer is NEVER self-managed — it breaks the inception loop.
- **Layer 1 (Infrastructure):** Managed by Terraform. Includes: VCN/VPC, subnets, gateways, IAM, databases, registries, load balancers.
- **Layer 2 (Application):** Managed by Ansible/K8s/CI/CD. Includes: software on VMs, app deployment, config files, container orchestration.

In the lab, your laptop IS Layer 0 — you run Terraform and Ansible directly. In production, a CI/CD pipeline replaces your laptop, but someone still set up that pipeline by hand (or with a bootstrap script). The loop always breaks at Layer 0.

Managed CI/CD (GitHub Actions, Terraform Cloud, OCI Resource Manager) eliminates the inception problem entirely — the platform provider maintains the execution environment.
**Why this matters for interviews:** Understanding this layering model is what separates "I ran `terraform apply`" from "I understand how infrastructure automation fits into an organization's deployment architecture." The lab teaches the tools; this ADR captures the mental model.
**See also:** `docs/DEVOPS-ARCHITECTURE-REFERENCE.md` for ASCII architecture diagrams and the lab-vs-production comparison table.

---

## ADR-005: Manual Provisioning → IaC Rebuild (Deliberate Teardown)
**Date:** 2026-03-31
**Status:** Accepted
**Context:** Day 1 built all infrastructure manually via OCI Console — VCN, subnets, compute instance, firewall rules, security lists. This was intentional: you need to feel the pain of manual work to understand what IaC replaces. But the legacy VM and VCN have no git history (committed locally on the VM, never pushed to remote), no reproducibility, and no audit trail. Day 2 rebuilds the same architecture properly with public/private subnets and a bastion pattern.
**Decision:** Terminate the legacy VM and tear down the Day 1 infrastructure before Day 2. Do not backfill documentation or attempt to preserve CLI output. The absence of automation artifacts for Day 1 is the point. **Exception:** App code (main.py, health_check.sh, oci_reporter.py) is preserved in the GitHub repo's `app/` directory — Ansible and Docker build steps on Days 2-4 depend on these files.
**Alternatives considered:**
- Screenshot every console step for portfolio proof (noise — console clicks aren't impressive)
- Run OCI CLI queries to capture state before deletion (over-engineering — Terraform IS the proof)
- Keep legacy VM running alongside new VMs (can't — only 1 OCPU free of 4 Always Free A1 cores)
- ~~Push the VM's local git repo to GitHub~~ — Adopted partially. App code files (main.py, health_check.sh, oci_reporter.py) are SCP'd to local repo `app/` and pushed to GitHub in Step 6.2. Downstream steps (Ansible deploy, Docker build, Day 3/5 commits) require them. The VM's .git history is discarded — only the files matter.
**Why this approach:** The interview story is stronger with the gap: "Day 1 has no Terraform because I did it manually. That's why I can explain exactly what every Terraform resource block replaces — I configured each one by hand first." The `.tf` files in git from Day 2+ are the portfolio proof. The ADR log captures the decision trail. Anything else is documentation theater.
**Lesson:** Not everything needs to be tracked. The end product (working IaC, CI/CD, automated config) matters more than proving you clicked buttons in a console.

---

## ADR-004: Air-Gapped AI Demonstration — Prove It, Don't Just Claim It
**Date:** 2026-03-26
**Status:** Accepted
**Context:** The FedRAMP readiness agent uses Ollama for local AI inference. The interview talking point is "air-gapped capable." But claiming air-gap without demonstrating it is weak.
**Decision:** Added Step 16.5 — block all outbound HTTP/HTTPS with iptables, run the agent, prove it works on localhost only. Restore network after.
**Alternatives considered:**
- `podman run --network=none` (simpler but only proves container isolation, not the full agent flow)
- Remove NAT gateway entirely (too destructive — can't re-add easily on free tier)
- Just claim it in the interview (lazy, unverifiable)
**Why this approach:** Demonstrable > declarative. An interviewer who hears "I blocked outbound traffic and the agent still worked" gets a concrete mental image. It's 4 lines of bash for a disproportionate interview impact.

---

## ADR-003: FedRAMP Readiness Agent Replaces Ollama Evidence Collector
**Date:** 2026-03-26
**Status:** Accepted
**Context:** The original AI pillar for Phase 1 was an "AI-Powered Compliance Evidence Collector" — a Python script that scrapes system configs and feeds them to Ollama for narrative summaries. This overlapped conceptually with a more useful tool: a FedRAMP readiness agent that actually checks controls and scores the environment.
**Decision:** Replace the evidence collector with a rules-based FedRAMP readiness agent (~270 lines Python) that:
- Checks 18 NIST 800-53 Rev 5 controls across 6 families (AC, AU, CM, IA, SC, SI)
- Uses weighted scoring (Lynis-style earned/possible model)
- Separates check definitions (JSON) from check logic (Python) — Prowler pattern
- Feeds results to Ollama for narrative report generation
**Alternatives considered:**
- OSCAL-powered agent parsing the full NIST catalog (too complex, scope creep risk)
- Prowler wrapper + Ollama (adds heavy dependency, not educational)
- Keep the evidence collector (works but doesn't teach FedRAMP concepts)
**Why this approach:** Rules-based checks are debuggable and understandable. A hiring manager can read `checklist.json` and immediately see what's being checked. The Lynis scoring model is dead simple. Zero pip dependencies for the agent itself (stdlib only + requests for Ollama API). The interview story is stronger: "I built a FedRAMP readiness agent" > "I built an evidence collector."
**AI pillar after this change:**
- Phase 1: Ollama — FedRAMP readiness agent (rules + narrative)
- Phase 2: OCI GenAI — Incident classification (unchanged)
- Phase 3: scikit-learn — Security pattern detection (unchanged)

---

## ADR-002: Real Migration Simulation — Local Docker Desktop to OCIR to OCI Compute
**Date:** 2026-03-26
**Status:** Accepted
**Context:** Phase 1 was titled "Legacy-to-Cloud Migration" but everything was built directly on OCI. There was no actual migration — no "on-prem" origin, no registry push, no cross-environment deployment. The narrative was hollow.
**Decision:** Restructure Phase 14 (Day 4) to simulate a real migration:
1. Build FedTracker container locally on Windows Docker Desktop (simulates "on-prem")
2. Push to OCIR (OCI Container Registry, 500 MB free tier)
3. Pull and deploy on OCI compute with Podman
**Alternatives considered:**
- Build on a second OCI VM simulating "on-prem" (uses free tier resources, adds complexity)
- Build in WSL2 on Windows (more realistic Linux env but adds WSL setup overhead)
- Keep everything on OCI and just restructure the narrative (still no real migration)
- Use Object Storage as migration vehicle (anti-pattern for containers — registries exist for this)
**Why this approach:** Docker Desktop on Windows is already installed. OCIR is free tier. The workflow (build → tag → push → pull → run) is the exact pattern used in real federal migrations. Podman on Oracle Linux is daemonless/rootless — a genuine security advantage worth demonstrating.
**Struggle:** The original guide had container work on Day 4 but the app wasn't built until Day 1 Phase 3. Had to carefully slot the migration into Day 4 without disrupting the existing Dockerfile build flow. Solution: new Steps 14.2-14.4 for migration, then existing Podman/Docker content becomes Steps 14.5-14.7.

---

## ADR-001: Three Independent Phases with Repeated Skill Pillars
**Date:** 2026-03-18
**Status:** Accepted
**Context:** Interview is for Accenture Federal Services Cloud Engineer / Linux Admin. Need to demonstrate breadth across many skills (Terraform, Ansible, Kubernetes, CI/CD, security, AI, containers, API development). A single linear project would only touch each skill once.
**Decision:** Three independent phases, each with the same "skill pillars" but different tools and use cases:
- AI: Ollama (Phase 1) → OCI GenAI (Phase 2) → scikit-learn (Phase 3)
- Security: OpenSCAP CIS (Phase 1) → AIDE (Phase 2) → Trivy SBOM (Phase 3)
- Containers: Podman/Docker (Phase 1) → k3s (Phase 2) → Helm/ArgoCD (Phase 3)
- API: REST basics (Phase 1) → Webhooks (Phase 2) → API auth/mTLS (Phase 3)
**Why this approach:** If you only complete Phase 1, you've touched every skill pillar. Each subsequent phase deepens the same skills with different tools. This is muscle memory through repetition with variation — the same pedagogical approach used in music practice (same scales, different keys).
**Trade-off:** Each phase is ~5 days / ~7,000 lines of guide content. Total project is massive (~20,000 lines). Mitigation: phases are independent — you can stop after Phase 1 and still have a complete portfolio artifact.

---

## Struggles & Lessons Learned

### OCI Free Tier Pain Points
- **VCN wizard corrupts tags** when compartment has tag defaults with user-applied values. Workaround: create VCN via CLI instead. (2026-03-23)
- **A1 Flex capacity** frequently unavailable in all ADs. Had to retry at off-peak hours. Settled on 1 OCPU / 8 GB instead of planned 2/12. (2026-03-25)
- **Tag defaults cause wizard failures** across multiple services. May remove tag defaults entirely and tag via CLI/Terraform instead. (2026-03-25)
- **Cloud Guard, Security Zones, Vulnerability Scanning** — none work on Always Free tier. This forced the FedRAMP agent to be a custom tool rather than using native OCI compliance features. (2026-03-26)

### Guide Writing Lessons
- **Step 7.2 `chmod 000` doesn't break the service** — Python bytecode cache (`__pycache__/`) lets uvicorn start even when `main.py` has no permissions. Must also `rm -rf __pycache__/` for the exercise to work. (2026-03-31)
- **`alternatives --set python3` to 3.11 breaks `firewall-cmd`** — system tools depend on Python 3.9's `gi` module. Fix: revert to 3.9 with `alternatives --set python3 /usr/bin/python3.9` (must `--install` first if not registered). Guide already warns about this but Step 7.1 doesn't mention the workaround. (2026-03-31)
- **`su - clouduser` vs `sudo su - clouduser`** — 12 occurrences in the guide had the wrong command. Cloud-init users on OL9 have no password set, so `su -` fails. Caught during live walkthrough. (2026-03-25)
- **Windows SSH gotchas** — `chmod 600` doesn't work in Git Bash, need `icacls` in PowerShell. Notepad saves `.txt` extensions by default. SSH config must have no extension. None of this is in standard OCI docs. (2026-03-25)
- **Copy-paste into Cloud Shell** — `\` line continuations break when pasted. All CLI commands must be single lines. (2026-03-25)
- **OCI quota policy names** don't match documentation (`blockstorage` vs `block-storage`). Comments (`#`) cause parser errors in quota policies. (2026-03-23)

### Architecture Pivots
- **Original plan had Groq API** for Phase 2 AI, switched to OCI GenAI Service to avoid third-party dependency and stay within the $300 trial credits. (2026-03-18)
- **Evidence collector → FedRAMP agent** was a mid-project pivot driven by realizing the evidence collector didn't teach FedRAMP concepts. The agent is more interview-relevant. (2026-03-26)
- **Migration simulation** added after realizing "legacy-to-cloud" was a claim without evidence. The Docker Desktop → OCIR → Podman flow makes the migration real. (2026-03-26)

---

## Future Blog Post Ideas
- "Building a FedRAMP Readiness Agent with 270 Lines of Python and a Local LLM"
- "The Air-Gap Test: Proving Your AI Tool Works Without Internet"
- "OCI Free Tier for Federal Cloud Labs: What Works and What Doesn't"
- "Three Phases, One Skill Stack: Repetition with Variation for Interview Prep"
- "Why I Migrated a Container Instead of Just Deploying One"
- "The Inception Problem: Who Manages the Infrastructure That Manages Your Infrastructure?"
