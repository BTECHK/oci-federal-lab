# Runbook: Trigger DR Drill

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P2 execution.

**When to use:** scheduled DR drill (quarterly), or pre-production cutover validation.
**Estimated time:** 30-90 minutes
**Severity context:** N/A — drill is planned, not an incident; treat as planned change

## Symptom

N/A — this is a planned drill, not a response to a symptom. Use this runbook to execute the drill consistently.

## Pre-drill (capture baseline)

1. _<USER FILLS: capture current SLI snapshot — backup_age, app health, k3s node states>_
2. _<USER FILLS: notify stakeholders the drill is starting>_
3. _<USER FILLS: confirm DR replica is current (ADB cross-region copy fresh, Object Storage replication caught up)>_

## Failure Injection

1. _<USER FILLS: which failure mode this drill simulates — node loss, region loss, ADB unavailable, etc.>_
2. _<USER FILLS: command to inject failure>_
3. _<USER FILLS: confirm failure is observed (alerts fire, /health/deep degraded, etc.)>_

## Recovery

1. _<USER FILLS: invoke dr-health-probe to confirm degraded state>_
2. _<USER FILLS: trigger failover (DNS cutover? ADB switchover? promote standby?)>_
3. _<USER FILLS: monitor recovery (RTO measurement starts when failure injected, ends when full functionality restored)>_

## Verification

- _<USER FILLS: full functional test against recovered environment>_
- _<USER FILLS: data integrity check (no rows lost during failover, RPO measurement)>_

## Post-drill

1. _<USER FILLS: restore primary if drill was a true failover>_
2. _<USER FILLS: capture post-drill SLI snapshot to compare against pre>_
3. _<USER FILLS: write `evidence/dr-drills/p2-fedanalytics-dr.md` report>_

## Escalation

- If drill discovers an actual problem (not just measurement): file incident, do real recovery

## Postmortem trigger

- Always write a drill report; treat it as a positive postmortem ("what worked, what'd we change")
