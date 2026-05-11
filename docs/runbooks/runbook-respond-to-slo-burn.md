# Runbook: Respond to SLO Error Budget Burn

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P3 execution.

**When to use:** Multi-window burn-rate alert fires (fast + slow burn); scripts/INC-005-slo-budget-check.py exits non-zero.
**Estimated time:** 15-60 minutes
**Severity context:** P1 if fast-burn (consuming budget in hours); P2 if slow-burn (consuming over days)

## Symptom

- _<USER FILLS: burn rate alert text? error budget remaining %? which SLO?>_

## Diagnostics

1. _<USER FILLS: Grafana panel for the affected SLO — what's the current burn vs target?>_
2. _<USER FILLS: identify the dominant failure mode driving burn (latency? errors? availability?)>_
3. _<USER FILLS: correlate with recent deploys, traffic changes, dependency status>_

## Remediation

Depends on the cause. Common cases:
- **Recent deploy regression:** trigger `runbook-rollback-bad-helm-release.md`
- **Dependency degraded:** _<USER FILLS: failover to alternate dep, or circuit-break the call>_
- **Capacity exhaustion:** _<USER FILLS: scale up the affected service>_
- **Latency spike from Ollama (INC-005):** _<USER FILLS: model swap to lighter, VM resize, or accept budget burn with documented exception>_

**Rollback if remediation fails:** _<USER FILLS: escalate to error budget policy — freeze deploys until burn stops>_

## Verification

- _<USER FILLS: burn rate alert clears>_
- _<USER FILLS: error budget consumption slows visibly in Grafana>_
- _<USER FILLS: SLI returns to expected band for 30 min>_

## Escalation

- **Page if:** fast-burn continues > 30 min after first remediation
- **Owner:** SRE on-call

## Postmortem trigger

- Always postmortem fast-burn events
- Slow-burn postmortem if budget exhausted (not just consumed)
