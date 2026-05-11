# ADR-017: OCI NoSQL vs ADB for Compliance Event Hot-Write

**Status:** Proposed (P2 introduces; user implements + finalizes)
**Date:** 2026-05-10 (locked via v1 addendum)
**Context phase:** Phase 2 — FedAnalytics DR

---

## Context

P2 introduces high-velocity compliance event detection from fedagent (OpenSCAP score changes, AIDE alerts). These events are:
- Frequent (potentially 100s/min during a scan storm)
- Semi-structured (payload shape varies by event source)
- Short-lived (interesting for ~7 days; long-tail is cold archive)
- Append-only (no updates, no deletes other than TTL expiry)

The existing data layer is Oracle Autonomous Database (ADB) on Always Free tier (1 OCPU, 20 GB). ADB handles the OLTP transactional state (personnel, audit_log, app_logs).

## Decision

Use **OCI NoSQL Database (Always Free tier)** for the `compliance_events_hot` table. Nightly batch enrichment job reads from NoSQL and writes normalized records into ADB `compliance_events` for long-term reporting + CMMC evidence packaging.

## Alternatives Considered

| Option | Pro | Con | Verdict |
|---|---|---|---|
| ADB only | Simpler architecture, one engine to operate | OLTP/hot-write contention; semi-structured fits awkwardly in ADB columns; risks Always Free OCPU pressure | Rejected |
| Object Storage as event log | Free-tier generous, append-only natively | Slow random reads, no secondary indexes for query | Rejected — query patterns require index |
| OCI Streaming (Kafka-compat) | Streaming-native | Event payload retention + query is a separate problem | Rejected — overkill, no consumer benefit |
| **OCI NoSQL Database** | Free tier (133M reads/writes/mo + 25GB), TTL native, document model fits semi-structured payload, secondary indexes for queries | New engine to operate; consistency model is eventually-consistent across replicas | **Selected** |

## Consequences

**Positive:**
- ADB stays focused on transactional state (no hot-write contention)
- Document model handles payload schema drift across event sources
- TTL means no manual archival job needed for hot data
- Free tier covers expected lab volume comfortably

**Negative:**
- Two engines to monitor (ADB + NoSQL)
- Eventual consistency between NoSQL writes and ADB batch enrichment — `compliance_events` may lag NoSQL by up to 1h
- Operationally distinct backup strategy from ADB

## Implementation Notes

- Connection from fedagent uses Instance Principal auth (no credentials)
- NoSQL table schema authored via Terraform (see `phases/phase-2-fedanalytics-dr/terraform/oci-nosql.tf`)
- Batch enrichment lives in `functions/python/compliance-event-batcher/`
- ADR-013 already established instance-principal auth pattern; this ADR extends to NoSQL Go SDK

## Quiz (5 questions)

1. Why not use Object Storage as the event log if the workload is append-only?

2. What's the eventual-consistency window between fedagent writing to NoSQL and the data being visible in ADB `compliance_events`? What user-visible behavior could that affect?

3. If the lab grew 10× and the NoSQL Always Free tier was exhausted, which ADR decision would need to be revisited first — and why?

4. What's the trade-off of TTL-based expiry vs explicit archival job? When would you switch from TTL to job?

5. How does this decision interact with ADR-013 (instance-principal auth)? What changes for the NoSQL SDK call site that doesn't for ADB?

## Key Takeaways (interview prep)

1. **Decision:** I split the hot-write path from the OLTP state because ADB on Always Free has limited OCPU and semi-structured event ingest would contend with personnel/audit reads. OCI NoSQL on Always Free has 133M reads+writes/mo headroom that fits this workload cleanly.

2. **Pattern:** Hot-cold write separation — high-velocity ingest goes to a NoSQL store with TTL, batch ETL normalizes into the relational store for long-term reporting + cross-reference queries. This is a common pattern at scale; the lab demonstrates it at lab scale.

3. **Why NoSQL over Streaming:** Event payload retention + secondary-index queries are first-class in NoSQL but require building a consumer + indexer if using Streaming. Streaming wins for event distribution; NoSQL wins for event queryability.

4. **Eventual consistency:** I'm explicit that `compliance_events` (in ADB) trails `compliance_events_hot` (in NoSQL) by up to 1h. User-visible queries for "what happened in the last hour" must hit NoSQL; queries for "what happened last month" hit ADB.

5. **At scale:** If event rate hit 10K/min, I'd add OCI Streaming in front of NoSQL for buffering, keep the same enrichment pattern but make it streaming consumer instead of batch.
