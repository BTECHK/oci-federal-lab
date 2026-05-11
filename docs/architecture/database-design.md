# Database Design Doc — FedPlatform (Oracle ADB)

**USER WRITES THIS.** Fill in your schema rationale before writing DDL.

---

## Access Patterns

### Reads (frequency, latency expectation)
_<fill in: e.g., "GET /personnel/{id} — 500/sec at p99 < 50ms — single-row lookup by PK">_

### Writes (frequency, latency expectation, transactional boundary)
_<fill in: e.g., "POST /personnel — 10/sec, must atomically write personnel + audit_log row">_

### Audit / append-only patterns
_<fill in: e.g., "audit_log is append-only, immutable; FK to personnel.id with ON DELETE NO ACTION">_

## Normalization Decisions

_<fill in: 3NF vs partial denormalization, why>_

## Index Strategy

_<fill in: which columns get B-tree, which get function-based, which composite indexes and the query that drives them>_

## Partitioning Strategy (Oracle ADB-specific)

_<fill in: range partition on created_at for audit_log? interval partitioning? hash partitioning for personnel by department? Or none — justify either way>_

## Locking + Isolation

_<fill in: SERIALIZABLE for audit ops, READ COMMITTED for reads, optimistic concurrency on personnel updates? Use row-level locks vs application-level coordination?>_

## Connection Pool Sizing

_<fill in: target pool size, why; how it relates to ADB's session limits on Always Free tier>_

## What Doesn't Fit Relational (justification for NoSQL hot-write at P2)

_<fill in: why compliance_events_hot belongs in OCI NoSQL, not ADB — high-write semi-structured events with TTL>_

## Failure Modes

_<fill in: what happens during ADB switchover, how the app reconnects, idempotency of writes, etc.>_

## Key Takeaways (interview prep — 5 bullets)

1. _<fill in>_
2. _<fill in>_
3. _<fill in>_
4. _<fill in>_
5. _<fill in>_
