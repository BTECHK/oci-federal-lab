# Runbook: Restore ADB from Backup

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P2 execution.

**When to use:** ADB data corruption, accidental DROP TABLE, ransomware/insider compromise of writes.
**Estimated time:** 15 minutes (PITR clone) to 2+ hours (full restore + validation)
**Severity context:** P0 if production data loss; P2 if non-prod or recoverable from app-layer

## Symptom

- _<USER FILLS: missing rows? specific table inaccessible? OCI Monitoring alert on data freshness?>_

## Diagnostics

1. _<USER FILLS: confirm extent of data loss (which tables, which time range)>_
2. _<USER FILLS: check ADB backup status — when was last successful backup?>_
3. _<USER FILLS: decide: PITR clone (point-in-time recovery) vs full restore?>_

## Remediation

### Option A: PITR Clone (preferred for small recovery windows)
1. _<USER FILLS: `oci db autonomous-database create-from-clone-time` command>_
2. _<USER FILLS: validate clone has the required data>_
3. _<USER FILLS: cutover app to clone OR copy needed rows back to primary>_

### Option B: Full Restore (last-resort)
1. _<USER FILLS: identify restore point>_
2. _<USER FILLS: `oci db autonomous-database restore` command>_
3. _<USER FILLS: wait for restore (can take 1-2h on Always Free)>_
4. _<USER FILLS: validate row counts and data integrity>_

**Rollback if remediation fails:** _<USER FILLS: pivot to DR region if primary is unrecoverable>_

## Verification

- _<USER FILLS: row count comparison against expected>_
- _<USER FILLS: business-logic validation queries>_
- _<USER FILLS: app E2E test reads/writes successfully>_

## Escalation

- **Page if:** data loss exceeds RPO threshold, or restore exceeds RTO threshold

## Postmortem trigger

- Always postmortem any data loss event. Document RTO/RPO actual vs target.
