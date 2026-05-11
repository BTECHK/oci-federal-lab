# Runbook: Restart fedtracker-app

**STATUS:** Scaffolded 2026-05-10. User fills exact commands during admin day P1 execution.

**When to use:** /health/deep is failing, app is unresponsive, or you need to apply config changes that require restart.
**Estimated time:** 2-5 minutes (single VM) / 5-15 minutes (k3s rolling restart at P2+)
**Severity context:** P2 — service degradation but not data loss; restart is recoverable

## Symptom

- _<USER FILLS: what you'd see — error rate alert? /health/deep failure? specific log line?>_

## Diagnostics

1. _<USER FILLS: exact command to verify the symptom>_
2. _<USER FILLS: exact command to narrow root cause (logs? process state?)>_
3. _<USER FILLS: exact command to confirm hypothesis>_

## Remediation

1. _<USER FILLS: exact systemctl or kubectl command + expected output>_
2. _<USER FILLS: verification step>_

**Rollback if remediation fails:** _<USER FILLS: roll back to previous image tag / config>_

## Verification

- _<USER FILLS: exact health check command>_
- _<USER FILLS: smoke test (curl GET /health/deep, assert 200 + components.db.healthy)>_

## Escalation

- **Page if:** _<USER FILLS: restart fails twice, or app fails again within 15 min>_
- **Owner:** platform-on-call

## Postmortem trigger

- _<USER FILLS: write postmortem if restart was caused by an upstream change you didn't initiate, or if downtime > 5 min>_
