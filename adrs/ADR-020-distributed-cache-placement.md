# ADR-020: Distributed Cache Placement — Edge vs Service

**Status:** Proposed (P3 introduces; user implements + finalizes)
**Date:** 2026-05-10 (locked via v2 addendum)
**Context phase:** Phase 3 — FedCompliance GitOps Security

---

## Context

P3 introduces hot-path compliance lookups: "given resource X and policy Y, is the resource compliant as of time Z?" These queries:
- Hit at API Gateway hot path (every authenticated request that touches a compliance-relevant endpoint)
- Have a high cache hit rate (~95% on repeated resources/policies within minutes)
- Are read-heavy (write only when a scan or policy evaluation completes — minutes/hours apart)
- Tolerate eventual consistency (5min TTL acceptable; compliance state doesn't change second-by-second)

Choice: where does the cache live?

## Decision

Add **OCI Cache with Redis** (managed Redis on OCI, free-tier eligible at small size) between FedTracker API and ADB for hot compliance lookups. Cache-aside pattern with 5min TTL. Cache lives at the service tier (fedtracker-app uses it), NOT at the gateway tier.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| OCI Cache (Redis) at service tier | Sub-ms reads, cache-aside is well-understood, fedtracker-app already coupled to ADB | New service to operate, but managed | **Selected** |
| In-process LRU in FedTracker | Sub-µs, zero infra cost | Cache state per FedTracker instance — at multi-replica P3, cache hit rate drops with replica count; cold start invalidates entire cache | Rejected — doesn't scale across replicas |
| Cache at OCI API Gateway (response cache) | Even faster — sub-ms cache hit returned without touching service | Cache invalidation hard (gateway doesn't know when compliance state changes); per-route TTL only; doesn't help internal callers | Rejected for primary cache; could layer ON TOP for ultra-hot routes |
| Cache in ADB itself (Result Cache) | Native to ADB, no new infra | Coupled to single ADB instance; cold restart loses cache; less control over TTL | Rejected — less observable than Redis |

## Consequences

**Positive:**
- 95% of compliance lookups served from sub-ms cache; 5% hit ADB
- Cache state shared across all fedtracker-app replicas (no per-replica cold start cost)
- Cache invalidation explicit (DELETE on Redis key when policy evaluation completes)
- Operationally similar to ElastiCache/Memorystore/Azure Cache for Redis — common pattern across clouds

**Negative:**
- New service to operate (managed but still operationally distinct)
- Stale-cache risk: 5min TTL means a compliance state change may take up to 5min to be reflected in API responses. Document this clearly in the API spec.
- Cache stampede risk on cold start — multiple replicas miss the same key simultaneously and all hit ADB. Mitigated via singleflight pattern (only one in-flight ADB call per key per replica).

## Implementation Notes

- Terraform: `phases/phase-3-fedcompliance-gitops-security/terraform/oci-cache.tf` provisions managed Redis
- Client integration: `fedtracker-app/cache.py` (scaffold + answers/) uses redis-py with connection pool
- Cache key shape: `compliance:{resource_id}:{policy_id}`
- Cache invalidation: explicit DELETE called from the compliance scan completion handler

## Quiz (5 questions)

1. What's the cache stampede problem, and why does the singleflight pattern (asyncio Lock or fastapi-cache's wrapper) mitigate it? What does it cost?

2. We chose 5min TTL. What changes if we set TTL to 1h? To 30s? Walk through the staleness-vs-hit-rate tradeoff at each.

3. If we layered an additional cache at the API Gateway response-cache tier ON TOP of this service-tier cache, what new failure modes appear? When would the extra hop be worth it?

4. Cache invalidation is hard. Beyond TTL, what's the explicit invalidation trigger in this design? What gets missed if that trigger fails?

5. At 10× lab traffic, would you upgrade to Redis cluster (sharded) or stay with single-node? What's the cardinality of `(resource_id, policy_id)` that drives this?

## Key Takeaways (interview prep)

1. **Decision:** Distributed cache at service tier with cache-aside + 5min TTL + explicit invalidation on compliance-state change. Sub-ms reads for 95% of compliance lookups; 5% reach ADB.

2. **Why not in-process LRU:** at multi-replica P3, in-process cache state diverges per replica. Each new replica cold-starts with empty cache; rolling deploys mean cache is constantly partially-cold. Distributed cache amortizes warmup across all replicas.

3. **Why not gateway cache:** gateway can't invalidate on internal events (compliance state change). Service tier owns the invalidation contract because it owns the writes.

4. **Cache stampede mitigation via singleflight:** when N replicas miss the same cold key simultaneously, singleflight ensures only 1 hits ADB; the others wait for the result. Costs you a brief lock per key but avoids ADB pile-up during traffic burst.

5. **At scale:** Redis cluster (sharded) becomes necessary when the working set exceeds ~25% of single-node memory. Cardinality of `(resource_id, policy_id)` is the planning input. For lab scale (~100 resources × ~30 policies = 3000 keys), single-node fits fine.
