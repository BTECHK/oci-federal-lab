# Phase 2 Key Takeaways — Interview Prep

**USER FILLS at end of Phase 2.**

---

## Architecture Decisions

1. **ADR-016 — k3s before OKE:** _<fill in: what feeling the primitives gave you>_
2. **ADR-017 — OCI NoSQL hot-write:** _<fill in: hot/cold separation rationale>_
3. **DR architecture:** _<fill in: active-passive, RPO/RTO targets, cross-region copy>_

## Operational Lessons

1. **INC-002 OpenSCAP regression:** _<fill in>_
2. **INC-003 k3s node failure:** _<fill in>_
3. **DR drill measurement:** _<fill in: actual RTO/RPO vs target; what surprised you>_
4. _<fill in>_

## What I Would Do Differently at Scale

1. _<fill in: e.g., multi-region active-active with conflict-free CRDT replication for compliance events>_
2. _<fill in: e.g., OCI Streaming in front of NoSQL for burst absorption at 10× event rate>_
3. _<fill in>_

## Strongest Stories

1. **The DR drill story:** _<fill in: pre-drill, injection, recovery, measurement, what'd you change>_
2. **The NoSQL hot-write decision:** _<fill in: ADR-017 reasoning + the failure mode it avoids>_
3. _<fill in>_
