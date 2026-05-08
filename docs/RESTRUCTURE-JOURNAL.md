# Restructure Journal — Behind-the-Scenes Notes

> **Purpose:** The implementation guides in `phases/phase-1-fedtracker-migration/`, `phases/phase-2-fedanalytics-dr/`, and `phases/phase-3-fedcompliance-gitops-security/` are written to be standalone educational documents — anyone downloading the repo from GitHub should be able to follow them as polished tutorials without seeing meta-commentary about how the project evolved.
>
> This file is the opposite. It captures the design decisions, course-corrections, and "why we changed direction here" thoughts that belong in a blog post or a retrospective conversation rather than in a user-facing guide. Pair this with `docs/ARCHITECTURE-DECISIONS.md` (which holds the formal ADRs) when writing about the project later.

---

## Timeline of major direction changes

| Date | Change | ADR |
|---|---|---|
| 2026-03-18 | Original master design: three independent phases, repeated skill pillars (Ollama → OCI GenAI → scikit-learn; OpenSCAP → AIDE → Trivy; Podman/Docker → k3s → Helm/ArgoCD) | ADR-001 |
| 2026-03-26 | FedRAMP readiness agent replaces a generic "evidence collector" Ollama use case | ADR-003 |
| 2026-03-26 | Air-gapped AI demonstration adds Step 16.5 (block egress, prove Ollama still works) | ADR-004 |
| 2026-03-31 | Manual Day 1 → IaC rebuild Day 3 (the inception-loop pedagogy) | ADR-005 |
| 2026-03-31 | Three-layer DevOps model documented (Layer 0 bootstrap, Layer 1 IaC, Layer 2 app) | ADR-006 |
| 2026-04-02 | DIY-first / managed-second framing locked across phases (later partially overridden by ADR-009, then restored by ADR-011) | ADR-007 |
| 2026-04-02 | Phase-first repository structure (`phases/phase-N-app-theme/`) | ADR-008 |
| 2026-05-07 (morning) | OKE Basic proposed to replace k3s as Phase 2 spine on cost-and-employer-signal grounds | ADR-009 (now superseded) |
| 2026-05-07 (morning) | CloudBees CI free trial dropped from Phase 2; OSS plugin stack replaces it | ADR-010 |
| 2026-05-07 (mid-day) | ADR-009 walked back: k3s stays in Phase 2 (bare-bones K8s); OKE Basic moves to Phase 3 (managed-K8s migration) | ADR-011 |
| 2026-05-08 | Phase 1 scope freeze: any change to Phase 1 (including the implementation guide) forces retroactive setup work, so Phase 1 is locked at session-start state | (informal) |

---

## The K8s pedagogy walkback (worth a blog post on its own)

The most interesting course-correction was a same-day reversal on the Kubernetes pillar.

**What happened.** ADR-009 was written on cost-and-employer-signal grounds: trial credits had lapsed, the budget cap was tightening, and the original k3s plan consumed the entire 4 OCPU Always Free quota. OKE Basic's free control plane plus Always Free A1.Flex workers was the same dollar cost ($0 baseline) and signaled "managed Kubernetes" on the resume — which is what every federal Cloud Engineer / SRE job posting asks for. The pivot looked like a clean win.

**Why it was wrong.** Within hours, the pedagogical cost of the pivot became visible. k3s was placed in Phase 2 specifically to teach the bare-bones primitives — control plane install, agent join token, kubelet, kube-proxy, Flannel CNI, NodePort routing — *before* introducing a managed control plane. ADR-009 collapsed two lessons (primitives and managed) into one, with the primitives demoted to a 1-page appendix. The interview narrative lost its strongest sentence: "I built a multi-node Kubernetes cluster from scratch in Phase 2, then migrated to OKE Basic in Phase 3 and added Helm and ArgoCD GitOps on top." That sentence requires both halves.

**The fix.** ADR-011 (same day, before any implementation rewrites had landed) preserved the progression by introducing OKE Basic in Phase 3 as a managed-K8s migration step — k3s in Phase 2, OKE in Phase 3, Helm + ArgoCD layered on the new managed cluster. ADR-007's original "DIY first, then managed" framing — which ADR-009 had partially overridden — was restored to full effect.

**Lesson for future restructures.** Cost-and-employer-signal is one axis. Pedagogical sequencing is another. When an architecture decision optimizes one axis at the cost of another, the second axis often costs more than you think. The interview talking point a project produces is often more valuable than the resume keyword density. Lock pedagogical sequencing first, then optimize cost within that envelope.

---

## CloudBees CI: considered and skipped (the OSS-plugin replication story)

**What was considered.** A 30-day CloudBees CI free trial in Phase 2: download the WAR, replace the OSS Jenkins WAR, apply a license, configure folder RBAC + audit + CasC bundles natively, demonstrate the migration path, then either continue paying or revert.

**Why it was skipped.** Three reasons:
1. **Trial-license fragility.** Forgetting to cancel, hitting a feature gate at the wrong moment, or losing access on day 31 right before an interview are all real demo-time risks. The pattern is fragile in a way that a portfolio artifact shouldn't be.
2. **OSS plugins cover the actual learning objective.** The four features that matter at solo-lab scale — folder RBAC, audit logging, configuration-as-code, pipeline templating — all replicate cleanly on free Jenkins plugins (Role Strategy, Audit Trail, JCasC, the Folder plugin, plus shared libraries for templating). The patterns transfer directly to any commercial Jenkins distribution.
3. **The interview narrative is stronger with the swap, not weaker.** "I evaluated CloudBees CI's free trial against the OSS plugin stack and decided the plugins covered the actual learning objective at no cost or trial-license risk" demonstrates engineering judgment in a way that "I migrated to CloudBees during a free trial" does not.

ADR-010 captures the formal decision. The Phase 2 implementation guide presents the OSS plugin stack as the path without dwelling on what was rejected.

---

## OCI Generative AI Service → OCI Generative AI Agents

**What changed.** Phase 2's incident classification originally called OCI Generative AI Inference directly (a Cohere Command R+ chat completion wrapping a hand-written classification prompt). The 2026-05-07 restructure swapped this for OCI Generative AI Agents — Oracle's managed RAG service over a runbook corpus.

**Why managed RAG over direct inference.** Three reasons:
1. **Retrieval is hard to build well.** Chunking, embedding, vector store, top-k retrieval, prompt assembly — getting any of these wrong silently degrades quality. Managed Agents handle all of it.
2. **Citation traceability is required in federal environments under NIST 800-53 SI-7 and AU-10.** Auditors need to see *which* runbook the AI cited, not just what it said. Direct inference has no built-in citation mechanism.
3. **Agentic patterns are what employers actually ask about now.** Tool calling, multi-step reasoning, knowledge bases — that's the AI conversation in federal hiring, not raw chat completion.

The trade-off is per-call cost (~$10–15 budgeted across all of Phase 2 against the $70 discretionary cap). For incident triage where you want explainable answers grounded in your specific runbooks, that's the right trade.

---

## Phase 1 scope freeze (2026-05-08)

The user invested significant time configuring Phase 1's existing infrastructure (self-managed bastion VM, Ansible inventory, SSH keys against specific hosts, walkthrough state at Step 16). Any change to the Phase 1 implementation guide that doesn't match the existing on-disk setup forces retroactive setup work — an unacceptable cost for marginal documentation improvements.

The 2026-05-08 freeze locks Phase 1 at session-start state:
- No Bastion service swap (the OCI Bastion service module that was briefly created has been deleted).
- No Resource Manager Stack appendix (briefly drafted, deleted).
- No edits to the Phase 1 implementation guide.
- The PILLAR-MATRIX rows that referenced Phase 1 retrofits as upstream dependencies have been reframed to introduce those upgrades fresh in Phase 2 / Phase 3 instead.

Phase 1 remains the bare-bones manual-then-IaC walkthrough it was at session start. Any future upgrades to it live in a separate workstream.

---

## Cost framework (the $150 cap reasoning)

Phase 1 had been running on a 30-day OCI free-credit window that had lapsed by 2026-05-07, with ~$50 of incidental spend already accrued. The restructure set a $150 hard cap with three buckets:

| Bucket | Cap | Rationale |
|---|---|---|
| Already spent | ~$50 | Sunk cost |
| Reserved overrun pad | $30 | Demos, accidents, safety margin |
| Discretionary spend on paid services | ~$70 | Real budget for paid services |

**Discretionary breakdown:**
- OCI Generative AI Agents tokens (Phase 2): ~$15
- OKE worker outside Always Free for one-time load demo (Phase 3): ~$5
- Flexible Load Balancer hours during demo windows (Phase 3): ~$10
- Block volume / Object Storage overage cushion: ~$15
- Unallocated buffer: ~$25

**Three guardrails replace any need for a teardown script:**
1. OCI budget alerts at $75, $115, $140 thresholds.
2. `lifetime=ephemeral` tag on every Terraform-created resource — end-of-session console query lists what's still running.
3. The "leave-it-Friday rule": any compute, paid LB, or paid block volume left running over a weekend is an automatic Monday teardown candidate.

---

## Anchor concepts (the YAGNI guard)

Every phase hammers at least two of these five concepts:
1. Infrastructure as Code
2. CI/CD
3. Containerization & Kubernetes
4. Security
5. AI exposure

Net-new features must serve one of these and clear an L6-additive-value bar. Observability, API maturity, framework thinking, and operational maturity (the four "cheat-sheet pillar" additions from a 2026-04-15 brainstorm) were explicitly cut from the restructure as scope creep — they reclaimed ~8–10 hours per phase that went into actual depth instead.

---

## What this project is not

- A real production system — no production entropy (no real users, no 90-day SRE on-call cycles, no real customer data).
- A multicloud project — AWS, Azure, and GCP variants are tracked separately in the `Project ideas/` folder; this repo is OCI only.
- A portfolio competing on breadth — three phases hammer the same skills in different combinations; depth matters more than tool-name density.

---

## Blog-post-shaped fragments

Things that could become standalone blog posts:

1. **"The K8s pedagogy walkback: a same-day ADR I had to write back."** Story of ADR-009 → ADR-011 — what cost-and-employer-signal optimization missed, and why pedagogical sequencing is its own axis.
2. **"I evaluated CloudBees CI for my federal lab and chose OSS Jenkins instead."** ADR-010 in narrative form — the trial-license fragility argument, the OSS-plugin replication patterns, the interview-narrative swap.
3. **"OCI Generative AI Agents vs direct inference: when managed RAG earns its $15."** The citation-traceability case under NIST 800-53 SI-7 / AU-10, the agentic-AI signal employers ask about, the cost trade-off.
4. **"The leave-it-Friday rule: how I keep cloud lab spend under $150 without writing a teardown script."** The three-guardrail pattern (budget alerts + ephemeral tag + weekend rule).
5. **"Why my Phase 1 didn't change in the restructure."** The 2026-05-08 scope freeze — the unacceptable cost of guide drift against existing infrastructure setup.
