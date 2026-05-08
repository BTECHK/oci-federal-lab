# Architecture Decision Record (ADR) Log

Ongoing record of key decisions, trade-offs, pivots, and lessons learned while building the OCI Federal Lab. Written for future reference, README content, LinkedIn posts, and blog material.

**Format:** Each entry captures what was decided, what alternatives were considered, why this path was chosen, and what we learned. Entries are reverse-chronological (newest first).

> **Note — Potential Future Work:** Several ADRs below (notably ADR-001, ADR-003, ADR-007, ADR-008) reference Phase 2 (FedAnalytics DR) and Phase 3 (FedCompliance GitOps Security). Those phases are **planned but not yet started** — treat any mention of them as forward-looking scope, not delivered work.

---

## ADR-011: Kubernetes Pillar Progression — k3s in Phase 2, OKE Basic Introduced in Phase 3
**Date:** 2026-05-07 (same day as ADR-009, supersedes it before any implementation work landed)
**Status:** Accepted
**Context:** ADR-009 pivoted Phase 2's Kubernetes spine from self-managed k3s to managed OKE Basic, citing cost ceiling and employer signal. The reasoning was internally sound but it broke a deliberate pedagogical decision: k3s was placed in Phase 2 specifically so the lab could teach the bare-bones primitives of Kubernetes — control plane install, agent join token, kubelet, kube-proxy, Flannel CNI, NodePort routing — *before* introducing a managed control plane in a later phase. Replacing k3s with OKE in Phase 2 would have collapsed two lessons (primitives and managed) into one, with the primitives demoted to a 1-page appendix. The user caught this within the same session, before any Phase 2 implementation-guide rewrites had been applied.

The corrected design honors ADR-007's original "build it yourself first, then use the managed equivalent" framing — which ADR-009 had partially overridden — by keeping k3s as the Phase 2 spine and instead introducing OKE Basic in Phase 3 as the explicit managed-K8s migration step.

**Decision:** Lock the following Kubernetes progression across the three phases:

- **Phase 1 — FedTracker Migration:** No Kubernetes. Containerization with Podman + Docker only. Establishes the OCI / Linux / Terraform / Ansible / Jenkins baseline without K8s overhead.
- **Phase 2 — FedAnalytics DR:** **k3s 2-node DIY cluster** on Always Free A1.Flex. Manual install via `curl get.k3s.io | sh`, manual agent join with `K3S_URL` + `K3S_TOKEN`, manual kubeconfig retrieval, manual NodePort networking, manual multi-node troubleshooting. Phase 23 of the implementation guide stays substantially as-written — this ADR explicitly forbids any rewrite that swaps k3s out of Phase 2.
- **Phase 3 — FedCompliance GitOps Security:** **OKE Basic introduced as the managed-K8s migration step.** New early-Phase-3 step: terminate the Phase 2 k3s cluster, provision OKE Basic with an Always Free A1.Flex worker pool, redeploy FedCompliance to the new managed cluster. Helm + ArgoCD GitOps then target OKE (not k3s as in the original P3 plan). One-time paid `VM.Standard.E5.Flex` worker demo (~$5, tagged `lifetime=ephemeral`) demonstrates the paid scale-out path.

**Rationale:** The strongest interview narrative the project produces comes from being able to say, in order: "I built a multi-node Kubernetes cluster from scratch in Phase 2, including the agent-join handshake and the CNI overlay; in Phase 3 I migrated to OKE Basic and added Helm and ArgoCD GitOps on top." That sentence requires both halves. ADR-009 would have eliminated the first half by demoting k3s to an appendix. ADR-011 preserves both, and aligns the project with ADR-007's original pedagogical commitment.

**Trade-offs:**
- Phase 3 grows: it now absorbs the OKE migration step (~600 lines of new content), the kubectl-from-OKE pattern, the OKE node-pool lifecycle, and the paid-worker demo.
- Phase 3's discretionary budget absorbs the ~$5 paid worker demo and ~$10 of Flexible Load Balancer demo windows that ADR-009 had budgeted to Phase 2 — net cap unchanged at ~$70.
- The "no per-phase tool doubling" rule from ADR-010 still holds: Phase 3 uses OKE only (k3s is gone after the migration); Phase 2 uses k3s only.

**Alternatives considered (and rejected):**
- Keep ADR-009 as-is and demote k3s to a Phase 2 appendix (rejected — destroys the bare-bones learning step that the project's pedagogy depends on).
- Run k3s and OKE side-by-side in Phase 3 to "show the migration delta" (rejected — violates the no-doubling rule and adds compute cost without proportional learning value).
- Push OKE further out, into a hypothetical Phase 4 (rejected — no Phase 4 exists in the project, and OKE-with-Helm-and-ArgoCD is the natural Phase 3 deliverable).
- Keep both ADR-009 and ADR-011 as "Accepted" with conflicting decisions and let the implementation guides arbitrate (rejected — ADRs are the authoritative source; conflicts here become drift everywhere downstream).

**See also:** ADR-007 (DIY-first, managed-second framing — restored to full effect by this ADR); ADR-009 (the pivot that this ADR supersedes — body preserved in the log for traceability); ADR-001 (the original three-phase pillar design); the cost framework in `C:\Users\k_a_s\.claude\plans\i-think-for-phase-abundant-pixel.md`; the verification gate "K8s pedagogy gate" added to that plan.

---

## ADR-010: Skip CloudBees Free Trial — Replicate Distinctive Features with Free OSS Jenkins
**Date:** 2026-05-07
**Status:** Accepted
**Context:** Earlier Phase 2 design referenced a "Jenkins + CloudBees CI migration" arc, on the theory that a CloudBees free trial would demonstrate enterprise-grade pipeline governance (folder-level RBAC, audit logging, pipeline templating, Operations Center). With the 30-day trial-credit window for OCI now lapsed and a hard $150 budget cap on the project, every paid or trial-locked dependency adds risk: forgetting to cancel a trial, hitting a feature gate mid-demo, or losing access to the rendered artifact when the trial ends. The question became: which CloudBees features actually matter for a solo portfolio lab, and can they be reproduced with free OSS Jenkins?
**Decision:** Skip the CloudBees free trial entirely. Replicate the three distinctive features that matter for a solo lab using free OSS Jenkins plugins and built-in capabilities:
- **Folder-level RBAC** via the Role Strategy plugin (matrix-based role assignments per folder)
- **Audit logging** via the Audit Trail plugin (records pipeline edits, run triggers, RBAC changes)
- **Pipeline templating** via shared library structure (`vars/`, `src/`, `resources/` — built into OSS Jenkins)

Explicitly out of scope (overkill for a solo lab, not worth replicating): Operations Center / multi-controller architecture, Beekeeper update center, cross-team governance dashboards, CloudBees Pipeline Explorer.
**Rationale:** The interview talking point becomes stronger with the swap, not weaker: "I evaluated CloudBees against OSS Jenkins for the features that matter at solo-lab scale, decided the free plugins covered the actual learning objective (RBAC + audit + templating), and avoided a paid dependency on the critical path." This frames the decision as deliberate engineering, not budget-driven compromise. Skipping the trial also eliminates the risk of trial expiry breaking the demo right before an interview.
**Trade-offs:**
- Loses hands-on exposure to the CloudBees UI specifically (acceptable — the underlying plugin patterns transfer to any Jenkins-derived product)
- Loses the "I migrated to CloudBees CI" narrative (replaced with the stronger "I evaluated and chose OSS" narrative)
**Alternatives considered:**
- Run the CloudBees trial alongside OSS Jenkins (rejected — doubles up CI/CD learning, violates the "no per-phase tool doubling" rule)
- Use Jenkins X (rejected — adds K8s-native complexity not on the learning anchor list)
- Use OCI DevOps as primary CI/CD (rejected — Jenkins is already the spine across all three phases; switching mid-project would fragment the CI/CD narrative)
**See also:** Phase 3 implementation guide CloudBees-replication subsection (Role Strategy + Audit Trail + shared library walkthrough).

---

## ADR-009: Phase 2 Kubernetes — OKE Basic with Always Free Workers Replaces k3s as Spine
**Date:** 2026-05-07
**Status:** **Superseded by ADR-011** (same day, before any implementation-guide rewrites landed). The cost-and-employer-signal reasoning below is sound, but it was applied to the wrong phase — pivoting Phase 2 away from k3s destroyed the deliberate "bare-bones first, managed second" learning progression that motivated putting k3s in Phase 2 in the first place. ADR-011 preserves the k3s/OKE progression by introducing OKE Basic in Phase 3 (as a managed-K8s migration step) instead of replacing k3s in Phase 2. Body retained below for traceability — the walking-back is itself worth preserving.
**Context:** Original Phase 2 design used a self-managed 2-node k3s cluster on Always Free A1.Flex compute, framed under ADR-007 ("build it yourself first, then use the managed equivalent"). Two pressures forced a re-evaluation:
1. **Cost ceiling.** With trial credits gone and a $150 hard cap, the 2-node k3s footprint consumes the entire 4 OCPU Always Free quota — leaving no headroom for any other compute in the same tenancy. OKE Basic's control plane is free, and worker nodes can run on the same Always Free A1.Flex shape, so the dollar-cost is identical at $0 baseline.
2. **Employer signal.** Job postings for federal Cloud Engineer / SRE roles ask for managed Kubernetes (EKS / AKS / GKE / OKE) almost universally; self-managed k3s is a niche skill that signals homelab depth, not production readiness. Using OKE as the spine lets the resume cite the managed Oracle service explicitly.
**Decision:** Phase 2 spine is OKE Basic with a 3-node A1.Flex Always Free worker pool. k3s is preserved as a single 1-page appendix demonstrating the DIY equivalent (kept for the "I understand the primitives" interview talking point), but no longer a daily part of the Phase 2 build.
**One-time paid demo:** Within a $5 sub-budget, briefly attach a paid `VM.Standard.E5.Flex` worker (~1 OCPU, ~6 hours wall-clock) to the OKE node pool, run a short load test, then tear down the same session. Tagged `lifetime=ephemeral`. This proves the paid path without committing to it.
**Rationale:** This change directly contradicts the "DIY first, managed second" framing of ADR-007 *for the Kubernetes pillar specifically*. The contradiction is intentional: ADR-007 was written when free credits were available and time was abundant. With both gone, the cost-vs-employer-signal trade-off flips. ADR-007 still holds for the Terraform pillar (local `terraform apply` is free, and Resource Manager is now an appendix per Phase 1 retrofits) and the CI/CD pillar (Jenkins remains spine; OCI DevOps is not added in parallel — see ADR-010).
**Trade-offs:**
- Loses the k3s "build a cluster from scratch" learning depth — partially recovered via the appendix
- OKE Basic node pools can't be torn down and re-created as cheaply as k3s on a single VM (slightly more friction in the spin-up/tear-down habit)
- Adds OKE-specific concepts (cluster auth, Kubeconfig issuance, node pool lifecycle) that have no k3s equivalent
**Alternatives considered:**
- Keep k3s as primary, OKE as appendix (rejected — inverts the employer-signal weighting that drove this ADR)
- Skip Kubernetes in Phase 2 entirely, push it to Phase 3 (rejected — Phase 3 already adds Helm/ArgoCD on top of an existing cluster; without P2's K8s spine, P3 has nowhere to land)
- Use OKE Enhanced (rejected — paid control plane, ~$50+/month, would consume most of the $70 discretionary budget on its own)
**See also:** ADR-007 (the "DIY first" framing this ADR partially overrides); ADR-001 (the original three-phase pillar design); the cost framework in `C:\Users\k_a_s\.claude\plans\i-think-for-phase-abundant-pixel.md`.

---

## ADR-008: Phase-First Repository Structure with Enterprise Naming
**Date:** 2026-04-02
**Status:** Accepted
**Context:** The original repo had flat top-level directories (`terraform/`, `ansible/`, `docker/`, `scripts/`, `tests/`). This worked for Phase 1 alone, but with 3 phases plus a Linux deep dive, files like `harden.yml` and `deploy_app.yml` would collide. The naming was generic — an interviewer browsing the repo couldn't tell which phase or app a file belonged to. Enterprise teams organize by project/service, not by tool type.
**Decision:** Reorganize into a `phases/` directory with descriptive folder names: `phase-1-fedtracker-migration`, `phase-2-fedanalytics-dr`, `phase-3-fedcompliance-gitops-security`. Each phase contains its own `terraform/`, `ansible/`, `app/`, `docker/`, and `docs/` subdirectories. Project-wide documentation (ADRs, lessons, known issues, PRD) stays in the root `docs/` folder. Shared utilities stay in `tools/`.
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
**Context:** Interview is for a federal Cloud Engineer / Linux Admin role. Need to demonstrate breadth across many skills (Terraform, Ansible, Kubernetes, CI/CD, security, AI, containers, API development). A single linear project would only touch each skill once.
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
- **Windows SSH gotchas** — `chmod 600` doesn't work in Git Bash, need `icacls` in PowerShell. WSL2 resolves this by handling `chmod` natively. Notepad saves `.txt` extensions by default. SSH config must have no extension. None of this is in standard OCI docs. (2026-03-25)
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
