# ADR-018: NoSQL Document vs Relational Schema for Supply Chain Results

**Status:** Proposed (P3 introduces; user implements + finalizes)
**Date:** 2026-05-10 (locked via v1 addendum)
**Context phase:** Phase 3 — FedCompliance GitOps Security

---

## Context

P3's supply-chain-validator Go function produces scan output per image push:
- Cosign signature validation result (boolean + metadata)
- Trivy CVE findings (variable count, severity bucketing)
- SBOM components (variable count, package metadata)
- Cosign attestations (varies by signing tool version)

The shape varies across scanner versions and across image types (Go binary vs Python+native libs vs k8s manifest). Adding columns to ADB every time Trivy changes its output schema is operationally painful. JSON columns in ADB work but lose queryability across the structure.

## Decision

Store structured scan results in **OCI NoSQL Database** as a document, keyed by `image_digest`. Bulk JSON output also archived to Object Storage (already happening from existing P3 design). Secondary index on `(scanned_at DESC, severity)` enables the "find all images with HIGH CVE in last 7 days" query pattern.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| ADB JSON column | Stays in existing relational engine; JSON_VALUE queries work | Query syntax verbose; index on JSON path requires functional index per query shape | Rejected — too rigid for evolving scanner output |
| ADB with strict columns | Strongly typed, easy queries | Schema migration every time Trivy adds a new field | Rejected — operational overhead |
| Object Storage only | Free-tier generous, schema-free | No secondary index; "find all images with HIGH CVE in last 7 days" requires full bucket scan | Rejected — query pattern needs index |
| OCI NoSQL document | Free tier (small footprint), document model handles drift, secondary index on (scanned_at, severity) | New table to operate (but already adopted at P2 — ADR-017) | **Selected** |

## Consequences

**Positive:**
- Scanner output schema drift is absorbed without schema migrations
- Queries by severity + time window are first-class
- Bulk JSON in Object Storage is the durable archive (compliance evidence); NoSQL is the queryable index over it

**Negative:**
- Two storage locations for the same logical data (NoSQL doc + Object Storage blob)
- Consistency: NoSQL row could exist without Object Storage blob (or vice versa) for a window during the write path — needs careful ordering (write Object Storage first, then NoSQL)

## Implementation Notes

- Write order: Object Storage `PutObject` (idempotent on image_digest) → NoSQL `PutOperation` (idempotent on PK)
- If NoSQL write fails after Object Storage success: retry later via background reconciliation (no compliance-relevant data lost; just queryability lag)
- Cross-reference: `evidence/supply-chain-results/` Object Storage bucket + NoSQL `supply_chain_results` table — both share `image_digest` as their natural key

## Quiz (5 questions)

1. Why write to Object Storage before NoSQL, not the other way around? What failure mode does this ordering avoid?

2. If a scanner adds a new field (`license_findings`), what changes in the data layer? Compare to if this were stored in strict ADB columns.

3. What's the cost in NoSQL request units of doing the secondary-index query "all images scanned in the last 24h with severity=HIGH"? Does it scale linearly with total images or with results returned?

4. How does the document model affect your ADR-017 enrichment pattern? Does the supply-chain-results table need a batch enrichment job into ADB the same way compliance_events_hot does?

5. If a regulator asked for "all CRITICAL CVEs in any production image in the last 12 months," which storage do you query, and what's the latency expectation?

## Key Takeaways (interview prep)

1. **Decision:** Document model for scanner output because the shape drifts faster than DDL migrations can keep up. Strict-relational columns would force a schema change per scanner version bump.

2. **Pattern:** Object Storage as durable archive (compliance-bound) + NoSQL as queryable index. Bulk content in Object Storage, queryable structured fields in NoSQL.

3. **Write ordering matters:** Object Storage first (compliance evidence must be durable before we say "scan complete"), NoSQL second (queryability is recoverable; archival is not).

4. **Secondary index payoff:** "find images with HIGH CVE in last 7 days" is sub-second on NoSQL secondary index, vs full bucket scan on Object Storage which costs 100× the latency at scale.

5. **At scale:** If we were processing thousands of images/day, I'd add OCI Streaming between the scanner output and the storage writes to absorb burst and provide replay if storage write fails.
