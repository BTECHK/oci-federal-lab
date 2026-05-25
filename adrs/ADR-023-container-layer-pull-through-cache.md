# ADR-023: Container-Layer Cache — Registry Pull-Through Mirror (k3s)

**Status:** Proposed (P2 introduces; user implements + finalizes)
**Date:** 2026-05-25
**Context phase:** Phase 2 — FedAnalytics DR (k3s)

---

## Context

This is the project's **second cache, at the container layer** — distinct from the service-tier Redis cache (ADR-020, P3). In the k3s (P2) → OKE (P3) work, cluster nodes repeatedly pull the same images (FedTracker app, FedAgent, sidecars, base images) from the registry. Cold pulls slow node scaling, node replacement, and — critically for this lab's theme — **DR rebuilds**, and every pull is an external registry round-trip, which a federal/air-gap-leaning posture wants to minimize. Goal: cache container images close to the cluster so the two caches in this project sit at two different layers (service tier + container tier).

## Decision

Add a **pull-through registry mirror** in front of the image registry: configure the cluster's containerd to pull through a local registry mirror so repeated image pulls are served locally instead of from the upstream registry each time. The user provisions the mirror (Terraform under `phases/phase-2-fedanalytics-dr/terraform/` + containerd config) — this ADR fixes the **decision and placement**; the infra is built by hand per the lab's build-it-yourself discipline.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| **Pull-through registry mirror** (containerd mirror) | Cuts repeated pulls cluster-wide; speeds scaling + DR rebuild; fewer external round-trips | A mirror to run + keep warm; storage for cached layers | **Selected** |
| Pull from the registry every time (no cache) | Zero extra infra | Slow cold scaling/DR; external dependency on every pull | Rejected |
| Bake everything into one fat base image | No pull-time deps | Brittle, huge images, rebuild churn on any dep change | Rejected |
| Node-local containerd cache only | Free, automatic per node | Helps an existing node, not a *new* one — DR/scale still cold | Partial — the mirror covers new nodes too |

## Consequences

**Positive:**
- Faster node scaling and DR rebuilds — the slow path (pulling N images cold) is served locally.
- Fewer external registry round-trips — aligns with the air-gap-leaning posture.
- Two caches now sit at two layers (service-tier Redis + container-tier mirror) — the portfolio shows caching at more than one tier.

**Negative:**
- The mirror is infrastructure to run, size, and keep current.
- Staleness if the mirror isn't invalidated when a new image is pushed under a moving tag (`:latest`); prefer immutable digests.
- Cached layers consume storage that must be capped/garbage-collected.

## Implementation Notes

- **User-built infra** (not pre-scaffolded): Terraform for the mirror + containerd registry-mirror config on the k3s nodes (and the OKE node pools at P3).
- Prefer pinning images by digest so the mirror never serves a stale `:latest`.
- Evidence = image pull time / DR-rebuild time **before vs after** the mirror.

## Quiz (5 questions)

1. Why a pull-through registry mirror rather than baking everything into a fat base image? What does each cost you on a dependency change?
2. How does the mirror specifically speed a DR rebuild, when a node-local containerd cache does not?
3. What's the staleness risk with a registry mirror, and how do immutable digests vs moving tags change it?
4. The mirror's disk fills with cached layers. What's your GC/retention strategy, and what breaks if you get it wrong?
5. How does this cache's value differ from the service-tier Redis cache (ADR-020)? Why are both worth having?

## Key Takeaways (interview prep)

1. **Decision:** A container-layer pull-through registry mirror for the k3s/OKE clusters — the project's second cache, at a different layer than the service-tier Redis (ADR-020). **Tradeoff:** a mirror to operate + layer storage vs. slow cold pulls on every scale/DR event.
2. **Pattern:** Cache images close to the cluster; pin by digest to avoid serving a stale moving tag.
3. **Why two caches:** service-tier Redis cuts DB read latency; the container-tier mirror cuts image-pull latency. Different bottlenecks, different layers — that's the breadth point.
4. **Failure mode:** unbounded layer storage or a stale `:latest`; mitigate with GC + digests.
5. **At scale:** promote to a managed registry with geo-replication; per-region mirrors; tie GC to image-retention policy.
