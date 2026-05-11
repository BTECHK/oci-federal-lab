# Phase 3 Key Takeaways — Interview Prep

**USER FILLS at end of Phase 3.**

---

## Architecture Decisions

1. **ADR-018 — NoSQL document for scanner output:** _<fill in: why doc model beats relational here>_
2. **ADR-020 — Distributed cache placement (service tier):** _<fill in: why not gateway tier or in-process>_
3. **OKE migration:** _<fill in: what you gained / lost vs k3s>_
4. **GitOps via ArgoCD:** _<fill in: the audit trail benefit>_

## Operational Lessons

1. **INC-004 cert expiry:** _<fill in>_
2. **INC-005 SLO burn:** _<fill in: multi-window burn rate response>_
3. **Patch simulation:** _<fill in: rollback drill what surprised you>_
4. **Supply chain story:** _<fill in: the full chain Cosign sign in CI → Cosign verify at admission → Trivy scan results in NoSQL>_
5. _<fill in>_

## What I Would Do Differently at Scale

1. _<fill in: e.g., Redis cluster sharded once working set exceeds 25% single-node memory>_
2. _<fill in: e.g., dedicated Cosign key per environment + transparency log (Rekor) for full supply chain attestation>_
3. _<fill in>_

## Strongest Stories

1. **The patch simulation:** _<fill in: pre-patch state → execution → rollback drill → lessons>_
2. **The supply chain chain-of-trust:** _<fill in: CI signs, admission verifies, Trivy gates, NoSQL stores queryable index>_
3. **API Gateway as compliance edge:** _<fill in: JWT at edge + audit logs + scope reduction for backend>_
